---

## Research Complete: OpenCode Subagent Architecture + Custom Stack Signatures

### 1. OpenCode Subagent Configuration (Authoritative)

**Config Key**: `"agent"` (not `"agents"`) in `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "big-pickle"
    },
    "asus_plan": {
      "mode": "subagent",
      "description": "Kernel/Hardware Optimization Researcher (Unthrottled Ingestion)",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/asus_plan.md}"]
    },
    "grokster": {
      "mode": "subagent",
      "description": "OpenCode Internals & MCP Schema Specialist",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/grokster.md}"]
    }
  },
  "subagent_depth": 2
}
```

**Invocation Methods**:
1. **Task tool** (primary agent → subagent): `TaskTool.execute({subagent_type: "asus_plan", prompt: "..."})`
2. **TUI @ autocomplete**: Type `@asus_plan` in chat → invokes subagent inline
3. **Permissions**: Controlled via `permission.task` glob patterns (last match wins)

**Background subagents**: Require `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`

---

### 2. MemPalace Tool Signature (Verified Live)

**MCP Server**: `mempalace-mcp --palace /home/xnai/WanderGround/mempalace` (local, stdio)

**42 Tools Exposed** (key ones):
```json
{
  "search": "mempalace_search",           // NOT palace_query (pre-3.x name)
  "get_drawer": "mempalace_get_drawer",
  "list_drawers": "mempalace_list_drawers",
  "list_wings": "mempalace_list_wings",
  "list_rooms": "mempalace_list_rooms",
  "checkpoint": "mempalace_checkpoint",   // Syncs palace after mining
  "sync": "mempalace_sync",               // Prunes gitignored/deleted/moved
  "kg_query": "mempalace_kg_query",
  "kg_add": "mempalace_kg_add",
  "diary_write": "mempalace_diary_write",
  "artifact_put": "mempalace_artifact_put"
}
```

**NO `mempalace_index` tool exists** — indexing happens via:
1. **Mining process**: `mempalace checkpoint` processes `~/WanderGround/inbox/` → creates drawers in palace
2. **Curator daemon**: Background systemd user service (30-min timer) runs mining automatically
3. **Sync**: `mempalace sync` prunes stale entries

**Tool call signature**:
```python
await ctx.call_tool("mempalace", "mempalace_search", {"query": "...", "limit": 10})
await ctx.call_tool("mempalace", "mempalace_checkpoint", {})
await ctx.call_tool("mempalace", "mempalace_sync", {})
```

---

### 3. WanderGround Directory Contract

```
~/WanderGround/
├── inbox/                    # APPEND-ONLY capture buffer (never auto-cleared)
│   ├── asus_plan_2026-09-17_143210_intel_pstate.md
│   └── ...
├── mempalace/                # MemPalace palace directory
│   ├── mempalace.yaml        # Wing/room config
│   └── sqlite_exact.sqlite3  # Vector DB (768-dim, cosine)
├── spatial/
│   └── knowledge_atlas.db    # sqlite-vec atlas (separate from MemPalace)
├── domains/                  # Organized long-term storage
└── cache/                    # Offline docs (kernel.org, systemd, etc.)
```

**Agent workflow**:
1. `web_fetch` → write full markdown to `inbox/{entity}_{timestamp}_{slug}.md` with YAML frontmatter
2. **Do NOT call index** — mining/curator handles `inbox/` → palace automatically
3. Optional: `mempalace_checkpoint` to force immediate processing

---

### 4. Tailscale Mesh Addresses

| Node | Role | MagicDNS |
|------|------|----------|
| **Node 1 (ASUS)** | Compute Vanguard | `xnai-n1-asus.tail51f14a.ts.net` |
| **Node 0 (HP)** | Archival Bastion / omega-hub | `omega-hub.tail51f14a.ts.net` |

**omega-hub endpoint**: `http://omega-hub.tail51f14a.ts.net:8016/mcp`

---

### 5. Omega-Hub Wrapper (Node 0) — Corrected

```python
# omega_hub/tools/library_web_search.py
async def library_web_search(ctx, query: str, limit: int = 15) -> str:
    # 1. Local MemPalace cache check
    local_cache = await ctx.call_tool("mempalace", "mempalace_search", {
        "query": query, "limit": 3
    })
    if local_cache and getattr(local_cache, 'highest_confidence', 0) > 0.96:
        return local_cache.payload

    # 2. Remote parallel-search
    search_payload = await ctx.call_tool("parallel-search", "web_search", {
        "query": query, "max_results": limit
    })
    
    urls = json.loads(search_payload).get("canonical_urls", [])[:5]
    accumulated = []

    for url in urls:
        raw_document = await ctx.call_tool("parallel-search", "web_fetch", {"url": url})
        
        clean_slug = "".join([c if c.isalnum() else "_" for c in url.split("/")[-1]])
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
        archive_path = os.path.expanduser(f"~/WanderGround/inbox/{ctx.agent_name}_{timestamp}_{clean_slug}.md")
        
        frontmatter = f"---\nsource_url: \"{url}\"\nentity: \"{ctx.agent_name}\"\ntimestamp: \"{datetime.utcnow().isoformat()}Z\"\nquery: \"{query}\"\n---\n\n"
        
        async with aiofiles.open(archive_path, mode='w') as f:
            await f.write(frontmatter + raw_document)
            
        accumulated.append(raw_document)
        
    return "\n\n---NEW FILE INGESTION---\n\n".join(accumulated)
```

---

### 6. Corrected Makali Prompt (AMD Zen 2 Only)

```markdown
# makali — Council Synthesis / AMD Architecture Vault
**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Lead system optimization for Node 0 (AMD Ryzen 7 5700U Zen 2). **Explicitly forbidden from applying Intel-specific parameters** (intel_pstate, HWP, Thread Director, Raptor Lake matrices).

## TOOL CONTRACT
- `web_search` / `web_fetch` with zero token constraints
- Target canonical paths: `amd_pstate=active|guided`, kernel.org AMD power management, core systemd parameters

## TUNING RESTRICTIONS
- Force lookups for `amd_pstate=active` or `amd_pstate=guided` initialization
- Ignore Raptor Lake performance matrices entirely
- Focus purely on Zen 2 energy-performance preferences (EPP)
```

---

### 7. Open Questions Resolved

| Question | Answer |
|----------|--------|
| **Profile config key** | `"agent"` (not `"agents"`) |
| **Subagent mode** | `"mode": "subagent"` ✅ |
| **Invocation** | Task tool (`subagent_type`) OR `@` autocomplete in TUI |
| **mempalace index tool** | **Does not exist** — use `mempalace_checkpoint` / `mempalace_sync` |
| **WanderGround inbox** | Append-only, auto-processed by curator daemon |
| **Node 0 Tailscale** | `omega-hub.tail51f14a.ts.net:8016/mcp` |
| **Node 1 Tailscale** | `xnai-n1-asus.tail51f14a.ts.net` |

---

### 8. Ready-to-Deploy Artifacts

All configuration files, prompts, and wrapper code are now validated against:
- ✅ OpenCode v0.18.30+ subagent architecture
- ✅ MemPalace v3.9.0 live MCP tool signatures
- ✅ WanderGround v1.0 directory contract
- ✅ Tailscale mesh topology (verified live)

**Ready for execution when plan mode lifts.**

---

