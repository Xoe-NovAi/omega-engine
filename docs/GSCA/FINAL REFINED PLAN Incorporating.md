---

## FINAL REFINED PLAN (Incorporating GSCA Review)

### 🔴 Critical Corrections

| # | Issue | Resolution |
|---|-------|------------|
| **1** | OpenCode profiles must be in `opencode.json` under `profiles` object, not separate files | Unified single config file |
| **2** | Tailscale routing: Node 1 → Node 0 via MagicDNS `hp.tailscale-mesh.ts.net:8016` (or static Tailscale IPv4) | Explicit peer address in omega-hub wrapper |
| **3** | `makali` on AMD Zen 2 needs AMD-specific prompt (no Intel params) | Separate `makali.md` with AMD-only targets |

### 🟢 High-Value Optimizations

| # | Opportunity | Implementation |
|---|-------------|----------------|
| **1** | Batch multi-file ingestion via parallel-search array | Single aggregated payload, eliminates round-trips |
| **2** | Async SQLite-vec via inotifywait sidecar daemon | Non-blocking embedding, main agent loop unburdened |

---

### 📦 Unified Production Configuration

#### Single `~/.config/opencode/opencode.json` (Node 1)

```json
{
  "$schema": "https://opencode.ai",
  "mcp": {
    "servers": {
      "parallel-search": {
        "type": "remote",
        "url": "https://parallel.ai",
        "enabled": true,
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {env:PARALLEL_API_KEY}"
        },
        "timeout": 120000,
        "max_retries": 3
      }
    }
  },
  "profiles": {
    "asus_build": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": false } },
      "env": { "OPENCODE_ENABLE_PARALLEL": "false" }
    },
    "asus_plan": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/asus_plan.md}"]
    },
    "grokster": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/grokster.md}"]
    }
  }
}
```

**Node 0** gets mirror config with `kali`/`makali` profiles instead.

---

### 🔧 Omega-Hub Wrapper (Node 0 Production Code)

```python
# omega_hub/tools/library_web_search.py
import os
import json
import aiofiles
from datetime import datetime

async def library_web_search(ctx, query: str, limit: int = 15) -> str:
    """
    Unthrottled Ingestion Wrapper for local Tailscale Federation.
    Routes queries directly to parallel-search MCP and saves raw data locally.
    """
    # 1. Local SQLite-vec cache check
    local_cache = await ctx.call_tool("mempalace", "search", {"query": query, "limit": 3})
    if local_cache and getattr(local_cache, 'highest_confidence', 0) > 0.96:
        return local_cache.payload

    # 2. Remote parallel-search via explicit schema
    search_payload = await ctx.call_tool("parallel-search", "web_search", {
        "query": query,
        "max_results": limit
    })
    
    urls = json.loads(search_payload).get("canonical_urls", [])[:5]
    accumulated_markdown = []

    for url in urls:
        # Fetch un-truncated text blocks
        raw_document = await ctx.call_tool("parallel-search", "web_fetch", {"url": url})
        
        # Clean filename
        clean_slug = "".join([c if c.isalnum() else "_" for c in url.split("/")[-1]])
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
        archive_path = os.path.expanduser(f"~/WanderGround/inbox/{ctx.agent_name}_{timestamp}_{clean_slug}.md")
        
        # YAML Frontmatter
        frontmatter = (
            "---\n"
            f"source_url: \"{url}\"\n"
            f"entity: \"{ctx.agent_name}\"\n"
            f"timestamp: \"{datetime.utcnow().isoformat()}Z\"\n"
            f"query: \"{query}\"\n"
            "---\n\n"
        )
        
        # Atomic write
        async with aiofiles.open(archive_path, mode='w') as f:
            await f.write(frontmatter + raw_document)
            
        accumulated_markdown.append(raw_document)
        
    return "\n\n---NEW FILE INGESTION---\n\n".join(accumulated_markdown)
```

---

### 📝 Updated Prompts

#### `~/.config/opencode/prompts/makali.md` (AMD-Only)

```markdown
# makali — Council Synthesis / AMD Architecture Vault
**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Lead system optimization for Node 0 (AMD Ryzen 7 5700U Zen 2). **Explicitly forbidden from applying Intel-specific parameters** (intel_pstate, HWP, Thread Director, Raptor Lake matrices).

## TOOL CONTRACT
- `web_search` / `web_fetch` with zero token constraints
- Target canonical paths: `amd-pstate` documentation, kernel.org AMD power management, core systemd parameters

## TUNING RESTRICTIONS
- Force lookups for `amd_pstate=active` or `amd_pstate=guided` initialization
- Ignore Raptor Lake performance matrices entirely
- Focus purely on Zen 2 energy-performance preferences (EPP)
```

---

### ⚡ Async SQLite-Vec Sidecar (Optimization #2)

**New component**: `~/WanderGround/daemon/embed_daemon.py`

```python
#!/usr/bin/env python3
"""Background daemon: inotifywait on inbox/ → chunk → embed → sqlite-vec"""
import asyncio
import os
from pathlib import Path

INBOX = Path(os.path.expanduser("~/WanderGround/inbox"))
ATLAS = Path(os.path.expanduser("~/WanderGround/atlas"))

async def embed_daemon():
    proc = await asyncio.create_subprocess_exec(
        "inotifywait", "-m", "-e", "close_write", "--format", "%f", str(INBOX),
        stdout=asyncio.subprocess.PIPE
    )
    
    async for line in proc.stdout:
        filename = line.decode().strip()
        if filename.endswith(".md"):
            filepath = INBOX / filename
            # Read, chunk, embed via mempalace.index
            # Non-blocking, keeps main agent loop free
            await asyncio.create_task(mempalace_index_async(filepath))

if __name__ == "__main__":
    asyncio.run(embed_daemon())
```

**Deploy as systemd user service**:
```ini
# ~/.config/systemd/user/wanderground-embed.service
[Unit]
Description=WanderGround Async Embedding Daemon
After=default.target

[Service]
Type=simple
ExecStart=/home/xnai/WanderGround/daemon/embed_daemon.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

---

### 🎯 Tailscale Address Resolution

**Node 0 MagicDNS**: `hp.tailscale-mesh.ts.net:8016` (verify with `tailscale status`)

**Omega-hub wrapper uses explicit peer**:
```python
# In omega-hub config or wrapper
OMEGA_HUB_PEER = "http://hp.tailscale-mesh.ts.net:8016/mcp"
# OR static Tailscale IP: http://100.x.y.z:8016/mcp
```

---

### 📋 Updated Execution Order

```bash
# 1. Backup current state
cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak

# 2. Deploy UNIFIED opencode.json (Node 1)
# [single file with profiles object]

# 3. Deploy mirror opencode.json (Node 0) with kali/makali profiles
# [scp to Node 0]

# 4. Add env vars to ~/.bashrc (both nodes)
# [source ~/.bashrc]

# 5. Create prompt files (4 files: asus_plan, grokster, kali, makali)
# [with {include:...} syntax]

# 6. Create WanderGround structure + async daemon
mkdir -p ~/WanderGround/{inbox,domains/01_local_ai/{kernel,systemd,thermald},atlas,audit,daemon}
# [copy embed_daemon.py, enable systemd user service]

# 7. Deploy omega-hub wrapper on Node 0
# [copy library_web_search.py to omega-hub tool registry]

# 8. Pre-populate offline cache
# [wget/git clone]

# 9. Run validation suite
opencode mcp list --verbose
opencode run --profile asus_plan "test sequence..."

# 10. First real research: full intel_pstate + amd_pstate + zram-generator + thermal-conf.xml
```

---

### ❓ Open Questions for You

1. **Profile activation**: How do you switch profiles in OpenCode? `opencode --profile=asus_plan`? `OPENCODE_PROFILE=asus_plan`? Need exact command for validation step.

2. **Inbox retention**: Async daemon reads `inbox/` as append-only archive, or auto-clear after embedding?

3. **mempalace.index signature**: Confirm exact tool call — `ctx.call_tool("mempalace", "index", {"path": "..."})` or different?

4. **Node 0 hostname**: What's the actual MagicDNS name? `hp.tailscale-mesh.ts.net` or different?

5. **mTLS**: Want me to include cert generation for mutual TLS on parallel-search endpoint?

---

**Plan fully incorporates GSCA review. Ready for your decisions on Q1-5, then executable.**

---

