#!/usr/bin/env python3
"""parallel_bridge.py — local stdio MCP bridge for Parallel Web Search.

Why this exists: opencode 1.18's remote client cannot complete the MCP
handshake with search.parallel.ai (its HTTP stack is refused at the edge;
curl succeeds with identical requests). This bridge speaks MCP over stdio
(local transport, which opencode handles fine) and forwards upstream via
curl subprocesses (whose TLS fingerprint the edge accepts).

Protocol: JSON-RPC 2.0, one message per line on stdin/stdout (MCP stdio).
Logs go to stderr ONLY — stdout is the protocol channel.

Upstream: POST https://search.parallel.ai/mcp (Streamable HTTP).
Auth: Bearer PARALLEL_API_KEY (env first, ~/.config/opencode/.env fallback).
No secrets are stored in this file or the repo.

Usage (opencode.json):
    "parallel-search": {
      "type": "local",
      "command": ["/home/xnai/Documents/Projects/omega-engine-alpha/scripts/parallel_bridge.py"],
      "enabled": true
    }
"""
import json
import os
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://search.parallel.ai/mcp"
TIMEOUT = 110


def log(msg: str) -> None:
    print(f"[parallel_bridge] {msg}", file=sys.stderr, flush=True)


def api_key() -> str:
    k = os.environ.get("PARALLEL_API_KEY", "")
    if not k:
        envp = Path.home() / ".config" / "opencode" / ".env"
        if envp.exists():
            for line in envp.read_text().splitlines():
                if line.startswith("PARALLEL_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"')
    if not k:
        sys.exit("PARALLEL_API_KEY not set (env or ~/.config/opencode/.env)")
    return k


class Upstream:
    """Minimal Streamable-HTTP client with curl as the engine."""

    def __init__(self, key: str):
        self.key = key
        self.session: str | None = None

    def post(self, payload: dict) -> dict:
        import re
        cmd = [
            "curl", "-s", "--max-time", str(TIMEOUT),
            "-X", "POST", UPSTREAM,
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json, text/event-stream",
            "-H", f"Authorization: Bearer {self.key}",
        ]
        if self.session:
            cmd += ["-H", f"Mcp-Session-Id: {self.session}"]
        cmd += ["-D", "-", "-d", json.dumps(payload)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT + 10)
        out = p.stdout
        m = re.search(r"(?im)^mcp-session-id:\s*(\S+)", out)
        if m:
            self.session = m.group(1)
        # Body may be plain JSON (Parallel answers application/json) or SSE.
        body: str = out
        for pat in ("\r\n\r\n", "\n\n"):
            if pat in out:
                body = out.split(pat, 1)[1]
                break
        else:
            # No header/body separator (HTTP/2 dump): cut at first JSON/SSE start
            cut = re.search(r"\n(\{|\s*event:)", out)
            if cut:
                body = out[cut.start() + 1:]
        body = body.strip()
        if body.startswith("{"):
            msg = json.loads(body)
            if "result" in msg or "error" in msg:
                return msg
            raise RuntimeError(f"unexpected body: {body[:200]}")
        # SSE envelope: take data: lines, last JSON-RPC message wins
        result: dict = {}
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                try:
                    msg = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                if msg.get("jsonrpc") == "2.0" and ("result" in msg or "error" in msg):
                    result = msg
        if not result:
            raise RuntimeError(f"empty upstream response (curl rc={p.returncode}): {p.stderr[:200]}")
        return result


def serve() -> None:
    up = Upstream(api_key())
    log("bridge online, upstream=" + UPSTREAM)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params", {})

        def reply(result=None, error=None):
            out: dict = {"jsonrpc": "2.0", "id": mid}
            if error is not None:
                out["error"] = error
            else:
                out["result"] = result
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()

        try:
            if method == "initialize":
                up.post({
                    "jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "parallel-bridge", "version": "1.0"},
                    },
                })
                reply({"protocolVersion": "2024-11-05",
                       "capabilities": {"tools": {}},
                       "serverInfo": {"name": "parallel-bridge", "version": "1.0"}})
            elif method in ("notifications/initialized", "notifications/cancelled"):
                pass  # notifications carry no id; no reply
            elif method == "tools/list":
                if mid is None:
                    continue
                reply(up.post({"jsonrpc": "2.0", "id": 2,
                               "method": "tools/list", "params": {}}).get("result", {}))
            elif method == "tools/call":
                if mid is None:
                    continue
                reply(up.post({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                               "params": params}).get("result", {}))
            elif method == "ping":
                if mid is not None:
                    reply({})
            else:
                if mid is not None:
                    reply(error={"code": -32601, "message": f"unknown method {method}"})
        except Exception as e:  # keep the bridge alive; report per-request
            log(f"request {method} failed: {e}")
            if mid is not None:
                reply(error={"code": -32603, "message": str(e)[:300]})


if __name__ == "__main__":
    serve()
