Ollama is not an MCP client. It is an inference server that runs models and exposes a chat API with tool calling support. So you need a bridge layer between your repo, the MCP server, and the model.

```
repo ──> MCP server (read-only tools) ──> bridge/client loop ──> Ollama /api/chat (tools=[...])
```

## 1. Check which models can call tools

The model must report the `tools` capability or none of this works.

```bash
ollama show qwen2.5-coder:7b     # look for "tools" under Capabilities
ollama show LFM2.5-2.6B-Q4_K_M   # likely missing; see below
```

| Model (from your `ollama list`) | Tool use | Note |
|---|---|---|
| `qwen2.5-coder:7b` (4.7 GB) | Try first | Fits 16 GB comfortably |
| `phi4-mini` (2.5 GB) | Try | A review I found rates Phi-4 only "fair" on complex tool schemas |
| `gemma4-12b-qat`, `nemotron3-nano` | Test | Gemma 4 is listed as tool-capable in the same review |
| `qwen2.5-coder:14b` (9 GB) | Avoid for now | Leaves little RAM for context on 16 GB |
| `LFM2.5-2.6B-Q4_K_M` | Probably not as imported | A raw GGUF import usually lacks a tools template. I haven't verified this for your build, so `ollama show` is the check |
| Qwen3 8B (not pulled) | Candidate to pull | The same review calls Qwen 3 the most reliable tool caller in its class |

## 2. Bridge options

| Option | Effort | Use when |
|---|---|---|
| `ollmcp` (`pip install mcp-client-for-ollama`) | Low | You want it working today. It supports STDIO, SSE, and Streamable HTTP server connections (v0.35.1, released Sep 30, 2026) |
| `mcphost` | Low | A CLI one-liner: `mcphost -m ollama:qwen3:14b --config mcp-servers.json` |
| Own loop (Python `mcp` SDK + `ollama`) | Medium | You need per-agent tool allowlists and logging inside Omega. Code below |

## 3. Repo access: a small read-only MCP server

I recommend three tools, not the stock filesystem server. Small models get unreliable when shown many tool schemas, and the stock server also exposes write tools. This one jails paths to the repo root.

```python
# omega_repo_mcp.py   (pip install "mcp[cli]")
import os, re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

ROOT = Path(os.environ["OMEGA_REPO_ROOT"]).resolve()
SKIP = {".git", "node_modules", "__pycache__", ".venv"}
mcp = FastMCP("omega-repo-ro")

def _safe(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError("path escapes repo root")
    return p

@mcp.tool()
def list_dir(path: str = ".") -> list[str]:
    """List files and folders in a repo directory."""
    return sorted(f"{c.name}/" if c.is_dir() else c.name
                  for c in _safe(path).iterdir() if c.name not in SKIP)

@mcp.tool()
def read_file(path: str, start_line: int = 1, max_lines: int = 200) -> str:
    """Read a slice of a repo file, with line numbers."""
    lines = _safe(path).read_text(errors="replace").splitlines()
    chunk = lines[start_line - 1 : start_line - 1 + max_lines]
    return "\n".join(f"{start_line + i}: {l}" for i, l in enumerate(chunk))[:40_000]

@mcp.tool()
def search(pattern: str, glob: str = "*.py", max_hits: int = 30) -> list[str]:
    """Regex search across repo files matching a glob."""
    rx, hits = re.compile(pattern), []
    for f in ROOT.rglob(glob):
        if not f.is_file() or SKIP & set(f.parts) or not f.resolve().is_relative_to(ROOT):
            continue
        for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{n}: {line.strip()[:160]}")
                if len(hits) >= max_hits:
                    return hits
    return hits

if __name__ == "__main__":
    mcp.run()  # stdio
```

## 4. Wire it up

**Fast path (`ollmcp`):** save as `mcp-servers.json`.

```json
{
  "mcpServers": {
    "omega-repo": {
      "command": "python3",
      "args": ["/abs/path/omega_repo_mcp.py"],
      "env": { "OMEGA_REPO_ROOT": "/abs/path/to/your/repo" }
    }
  }
}
```

```bash
ollmcp --servers-json mcp-servers.json --model qwen2.5-coder:7b   # confirm flags with: ollmcp --help
```

**Own loop** (`pip install ollama mcp`):

```python
# agent_loop.py
import asyncio, os, sys
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "qwen2.5-coder:7b"
params = StdioServerParameters(
    command=sys.executable, args=["omega_repo_mcp.py"],
    env={**os.environ},  # must pass OMEGA_REPO_ROOT explicitly
)

async def ask(question: str, max_turns: int = 8) -> None:
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        await s.initialize()
        tools = [{"type": "function", "function": {
                    "name": t.name, "description": t.description or "",
                    "parameters": t.inputSchema}}
                 for t in (await s.list_tools()).tools]
        msgs = [{"role": "system", "content": "Answer only from tool output. Cite file:line."},
                {"role": "user", "content": question}]
        client = ollama.AsyncClient()
        for _ in range(max_turns):
            resp = await client.chat(model=MODEL, messages=msgs, tools=tools)
            msgs.append(resp.message)
            if not resp.message.tool_calls:
                print(resp.message.content)
                return
            for tc in resp.message.tool_calls:
                try:
                    res = await s.call_tool(tc.function.name, dict(tc.function.arguments))
                    out = "\n".join(c.text for c in res.content if hasattr(c, "text"))
                except Exception as e:  # tool errors go back to the model, not the crash handler
                    out = f"ERROR: {e}"
                msgs.append({"role": "tool", "tool_name": tc.function.name, "content": out})
        print("Stopped: max_turns reached")

asyncio.run(ask(sys.argv[1]))
```

Try: `python agent_loop.py "Where is RequestSizeLimitMiddleware defined and is it enabled?"`

## 5. Omega Stack specifics

| Item | Action |
|---|---|
| `omega-hub` (FastMCP, Library service) | Keep repo tools in the standalone server above until the audit findings are fixed: the disabled `RequestSizeLimitMiddleware`, the mocked proxy handler, and the lazy-init race. Then move the three tools into Library |
| llama-server on `:8080` | For llama-server-backed agents, start it with `--jinja`, which enables tool calling. Point an OpenAI-compatible client at `http://localhost:8080/v1` and reuse the same MCP-to-tools conversion |
| 11-agent fleet | Give each agent a tool allowlist, 3 tools max for small models. Keep agents and models as separate config entities, as you do now |
| `models.yaml` | I haven't seen its schema, so I won't invent keys. Paste it and I'll write the exact `tools:` allowlist entries |
| 16 GB RAM | Run one model at a time. Set `OLLAMA_KEEP_ALIVE` low if swapping starts |

## Action plan

| # | Step | Done when |
|---|---|---|
| 1 | `ollama show` on each candidate and note which have `tools` | You have a shortlist |
| 2 | Save `omega_repo_mcp.py`, set `OMEGA_REPO_ROOT`, run `mcp dev omega_repo_mcp.py` | All 3 tools respond in the inspector |
| 3 | Run `ollmcp` with `qwen2.5-coder:7b` and the JSON config | Model answers with a correct `file:line` |
| 4 | Re-run your hardware-MCP prompt, now with `search` and `read_file`, on 2 models | Compare hallucinated-API counts with the LFM test |
| 5 | Move to `agent_loop.py` for per-agent allowlists and logging | Tool calls are logged per agent |

Step 4 shows whether repo grounding fixes the invented-API problem from the LFM test.