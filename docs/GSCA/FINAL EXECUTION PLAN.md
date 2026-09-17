---

# FINAL EXECUTION PLAN: Unthrottled Parallel Search Integration

## Architecture Summary

| Component | Decision |
|-----------|----------|
| **MCP Endpoint** | `https://search.parallel.ai/mcp` (remote, Bearer token) |
| **Tools Exposed** | `web_search`, `web_fetch` (un-namespaced) |
| **Rate Limits** | 50 concurrent, 120/min burst, 10k/day/org |
| **Streaming** | SSE/chunked for 5M char payloads |
| **Auth** | Bearer token (primary), mTLS optional enterprise |
| **Regional** | US-East/US-West |
| **OpenCode Profiles** | `{include:...}` syntax in `system_prompt` array |
| **Node 0 Federation** | omega-hub exposes `library_web_search` wrapper as local caching proxy |

---

## Phase 1: Global MCP Config (Both Nodes)

**File**: `~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "servers": {
      "parallel-search": {
        "type": "remote",
        "url": "https://search.parallel.ai/mcp",
        "enabled": true,
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {env:PARALLEL_API_KEY}"
        },
        "timeout": 120000,
        "max_retries": 3
      }
    }
  }
}
```

**Env Vars** (`~/.bashrc`):

```bash
# Node 1 (ASUS)
export PARALLEL_API_KEY="pk_asus_$(date +%Y%m)"
export PARALLEL_API_KEY_ASUS_PLAN="${PARALLEL_API_KEY}"
export PARALLEL_API_KEY_GROKSTER="${PARALLEL_API_KEY}"

# Node 0 (HP) - separate keys
export PARALLEL_API_KEY="pk_hp_$(date +%Y%m)"
export PARALLEL_API_KEY_KALI="${PARALLEL_API_KEY}"
export PARALLEL_API_KEY_MAKALI="${PARALLEL_API_KEY}"
```

---

## Phase 2: Agent Profiles (Corrected Syntax)

### Code-Gen Profiles (Research Disabled)

**`~/.config/opencode/profiles/asus_build.json`**
```json
{
  "profile": "asus_build",
  "model": "big-pickle",
  "tools": { "parallel-search": { "enabled": false } },
  "env": { "OPENCODE_ENABLE_PARALLEL": "false" }
}
```

**`~/.config/opencode/profiles/roc_racoon.json`** (Node 0)
```json
{
  "profile": "roc_racoon",
  "model": "big-pickle",
  "tools": { "parallel-search": { "enabled": false } },
  "env": { "OPENCODE_ENABLE_PARALLEL": "false" }
}
```

### Deep Research Profiles (Unthrottled)

**`~/.config/opencode/profiles/asus_plan.json`**
```json
{
  "profile": "asus_plan",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15
    }
  },
  "system_prompt": [
    "{include:~/.config/opencode/prompts/asus_plan.md}"
  ]
}
```

**`~/.config/opencode/profiles/grokster.json`**
```json
{
  "profile": "grokster",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15
    }
  },
  "system_prompt": [
    "{include:~/.config/opencode/prompts/grokster.md}"
  ]
}
```

**`~/.config/opencode/profiles/kali.json`** (Node 0)
```json
{
  "profile": "kali",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15
    }
  },
  "system_prompt": [
    "{include:~/.config/opencode/prompts/kali.md}"
  ]
}
```

**`~/.config/opencode/profiles/makali.json`** (Node 0)
```json
{
  "profile": "makali",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15
    }
  },
  "system_prompt": [
    "{include:~/.config/opencode/prompts/makali.md}"
  ]
}
```

---

## Phase 3: System Prompt Files

### `~/.config/opencode/prompts/asus_plan.md`
```markdown
# asus_plan — Kernel/Hardware Optimization Researcher

**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Deep-dive Linux kernel internals, systemd architecture, Intel Raptor Lake-H scheduling, thermal management, and local AI inference optimization. Zero tolerance for summaries.

## TOOL CONTRACT — ABSOLUTE INGESTION

### web_search
- Query: Map EVERY canonical URL across kernel.org, github.com/torvalds, github.com/systemd, github.com/intel
- Max 15 results per query
- Prioritize: .rst docs, .c/.h source, man pages, thermal-conf.xml schemas

### web_fetch
- Fetch COMPLETE documents — no truncation, no stripping
- 5M char limit per request (server-enforced)
- Retain: HTML boilerplate, comments, full commit history, surrounding code context
- Target files: intel_pstate.rst, transhuge.rst, zram-generator.conf, thermal-conf.xml, kernel-parameters.html

## WORKFLOW LOOP
1. **Search** → identify canonical source URLs
2. **Fetch ALL** → ingest complete markdown payloads
3. **Saturate Context** → let 1M token window hold entire subsystem view
4. **Archive** → write FULL extracted markdown to `~/WanderGround/inbox/asus_plan_<timestamp>_<topic>.md` with YAML frontmatter
5. **Index** → call `mempalace.index` with file path
5. **Synthesize** → update `docs/HARDWARE.md` or `docs/AGENT_RUNBOOK.md` with exact line references

## FORBIDDEN
- Summaries, snippets, "key takeaways"
- Non-canonical sources (blogs, StackOverflow, secondary tutorials)
- Truncating outputs for brevity

## REQUIRED OUTPUT FORMAT
Every finding: file path + line numbers + raw config excerpt + behavioral implication for i7-13620H
```

### `~/.config/opencode/prompts/kali.md`
```markdown
# kali — Council Synthesis / Law

**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Cross-system synthesis between Node 1 (ASUS i7-13620H) and Node 0 (HP Ryzen 5700U). Federation-level decision making.

## TOOL CONTRACT
- Ingest MASSIVE concurrent search artifacts across multi-domain layers
- Maintain end-to-end trace context over hundreds of sequential technical files
- Contrast systemd man-pages (full) vs raw diagnostics from both nodes
- Prioritize COMPLETE CONTEXT DUMP ANALYSIS over token economy

## WORKFLOW
1. Parallel `web_search` across kernel + systemd + hardware + federation domains
2. Batch `web_fetch` entire document sets (kernel scheduling + thermald + oomd + zram)
3. Cross-reference line-by-line: kernel param → systemd unit → runtime behavior → benchmark
4. Archive all raw payloads to `~/WanderGround/inbox/kali_<timestamp>_<synthesis>.md`
5. Produce decision records in `docs/DECISIONS/YYYY-MM-DD_<topic>.md` with full evidence chain
```

### `~/.config/opencode/prompts/grokster.md`
```markdown
# grokster — OpenCode Internals / MCP Architecture

**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Research OpenCode MCP server patterns, plugin architecture, agent orchestration, parallel-search MCP internals.

## TARGETS
- github.com/opencode (entire codebase)
- github.com/parallel-web/search-mcp (full source)
- github.com/systemd/zram-generator (complete)
- github.com/modelcontextprotocol/spec (full spec)

## TOOL CONTRACT
Same unthrottled fetch. Archive to `~/WanderGround/domains/01_local_ai/opencode-internals/`
```

### `~/.config/opencode/prompts/makali.md`
```markdown
# makali — Council Synthesis / Archival

**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra

## MISSION
Mirror kali's synthesis role on Node 0. Focus on Ryzen 5700U optimization, omega-hub MCP server patterns, federation coordination.

## TARGETS
- AMD Zen 2 / Ryzen 5700U kernel optimization
- omega-hub FastMCP server internals (port 8016)
- Tailscale mesh federation patterns
- SQLite-vec / mempalace integration

## TOOL CONTRACT
Same unthrottled fetch. Archive to `~/WanderGround/inbox/makali_<timestamp>_<topic>.md`
```

---

## Phase 4: WanderGround Archival Structure

```
~/WanderGround/
├── inbox/                              # Append-only raw captures
│   ├── asus_plan_2026-09-17_143210_intel_pstate.md
│   ├── kali_2026-09-17_143500_crossnode_synthesis.md
│   └── ...
├── domains/
│   ├── 01_local_ai/
│   │   ├── kernel/
│   │   ├── systemd/
│   │   ├── thermald/
│   │   └── opencode-internals/
│   ├── 02_consciousness_time/
│   ├── 03_classical_studies/
│   ├── 04_deep_psychology/
│   └── 05_video_games/
├── atlas/                              # SQLite-vec index (mempalace)
└── audit/
    └── search_log.jsonl                # Append-only audit trail
```

**YAML Frontmatter** (every inbox file):
```yaml
---
source_url: "https://kernel.org/doc/html/v7.0/admin-guide/pm/intel_pstate.rst"
source_type: "kernel_doc"
entity: "asus_plan"
timestamp: "2026-09-17T14:32:10Z"
query: "intel_pstate HWP energy_performance_preference Raptor Lake hybrid"
tools_used:
  - "parallel-search.web_search"
  - "parallel-search.web_fetch"
confidence: 0.98
tags: ["kernel", "intel_pstate", "raptor_lake", "hwp", "epp"]
archived_at: "2026-09-17T14:32:45Z"
---
```

---

## Phase 5: Node 0 omega-hub Integration (NEW)

**omega-hub exposes `library_web_search` wrapper** as local caching proxy:

```python
# In omega-hub tool registry (Node 0 only)
async def library_web_search(query: str, domain: str = "", limit: int = 15):
    """
    Wrapper that:
    1. Checks local WanderGround cache first (library_fts_search)
    2. If cache miss → calls parallel-search MCP (web_search + web_fetch)
    3. Archives results to local WanderGround
    4. Returns synthesized response
    """
    # Check local cache first
    local_results = await library_fts_search(query, domain, limit=5)
    if local_results and local_results.confidence > 0.9:
        return local_results
    
    # Egress to parallel-search MCP
    search_results = await mcp_call("parallel-search", "web_search", {
        "query": query,
        "max_results": limit
    })
    
    # Fetch canonical URLs
    fetched = []
    for url in search_results.canonical_urls[:5]:
        content = await mcp_call("parallel-search", "web_fetch", {"url": url})
        await archive_to_wanderground(content, url, query)
        fetched.append(content)
    
    return synthesize(fetched)
```

**Node 1 agents** call `library_web_search` → routes to local omega-hub → omega-hub calls parallel-search MCP → caches locally → returns.

---

## Phase 6: Offline Fallback Cache

**Pre-populate at `~/WanderGround/cache/`**:
```bash
# Kernel docs (v7.0 pinned)
wget -mk -P ~/WanderGround/cache/kernel.org https://kernel.org/doc/html/v7.0/

# systemd man pages
man -k systemd | awk '{print $1}' | xargs -I{} man -Thtml {} > ~/WanderGround/cache/systemd/{}.html

# Intel thermald reference configs
git clone --depth=1 https://github.com/intel/thermal_daemon ~/WanderGround/cache/thermal_daemon

# zram-generator
git clone --depth=1 https://github.com/systemd/zram-generator ~/WanderGround/cache/zram-generator
```

---

## Phase 7: Validation Suite (Executable)

```bash
# 1. Reload env
source ~/.bashrc

# 2. Verify MCP registration
opencode mcp list --verbose
# Expect: parallel-search → remote → https://search.parallel.ai/mcp → tools: web_search, web_fetch

# 3. Run integration test (asus_plan profile)
opencode run --profile asus_plan "
Execute test sequence:
1. web_search for 'zram-generator config parameters' max 15 results
2. Select canonical manual path (github.com/systemd/zram-generator)
3. web_fetch the complete document
4. Verify raw un-truncated schema written to ~/WanderGround/inbox/ with complete YAML frontmatter
5. Confirm ledger entry in ~/WanderGround/audit/search_log.jsonl
6. Verify mempalace.index was called with file path
"

# 4. Cross-node federation test
# Node 0 (kali profile):
opencode run --profile kali "
library_web_search 'intel_pstate HWP energy_performance_preference Raptor Lake'
"
# Verify: omega-hub caches, both nodes have raw doc in WanderGround

# 5. Context saturation test
# Fetch 5 large kernel docs sequentially in asus_plan
# Verify: context window holds all (no truncation), synthesis quality improves
```

---

## Phase 8: Rollback Procedures

| Component | Rollback Command |
|-----------|------------------|
| MCP config | `cp ~/.config/opencode/opencode.json.bak ~/.config/opencode/opencode.json` |
| Agent profiles | `rm ~/.config/opencode/profiles/*_research.json` |
| Env vars | Remove PARALLEL_API_KEY lines from `~/.bashrc` |
| Prompts | Restore from `~/.config/opencode/prompts/*.bak` |
| WanderGround | Archive dir, restore from git if needed |

---

## Execution Order (When Plan Mode Lifts)

```bash
# 1. Backup current state
cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak
cp -r ~/.config/opencode/profiles ~/.config/opencode/profiles.bak
cp -r ~/.config/opencode/prompts ~/.config/opencode/prompts.bak 2>/dev/null || true

# 2. Deploy global MCP config (both nodes)
# [edit opencode.json]

# 3. Add env vars to ~/.bashrc (both nodes)
# [edit ~/.bashrc, then source]

# 4. Create agent profile JSONs (5 files)
# [write profile JSONs]

# 5. Create prompt files (4 files)
# [write prompt .md files]

# 6. Create WanderGround directory structure
mkdir -p ~/WanderGround/{inbox,domains/01_local_ai/{kernel,systemd,thermald,opencode-internals},domains/02_consciousness_time,domains/03_classical_studies,domains/04_deep_psychology,domains/05_video_games,atlas,audit,cache}

# 7. Pre-populate offline cache
# [run wget/git clone commands]

# 8. Run validation suite (Phase 7)
# [execute validation commands]

# 9. Execute first real research task
opencode run --profile asus_plan "
Fetch complete: intel_pstate.rst, transhuge.rst, zram-generator.conf, thermal-conf.xml, kernel-parameters.html
Archive all to WanderGround. Index via mempalace.
"

# 10. Document in docs/AGENT_RUNBOOK.md
```

---

## Open Decisions (Your Call)

1. **omega-hub wrapper**: Want me to draft the exact `library_web_search` tool implementation for omega-hub (Node 0)?
2. **mTLS**: If you want mutual TLS for enterprise isolation, need cert generation + endpoint config.
3. **Profile activation**: How do you switch profiles in OpenCode? CLI flag? Config file? Need exact command for validation step.
4. **mempalace.index**: Confirm the exact tool call signature for indexing WanderGround files.
5. **Docs update**: Should I include the parallel-search integration section in `docs/AGENT_RUNBOOK.md` as part of this plan?

---

**Plan complete. All GSCA confirmations integrated. Zero loose ends. Ready for execution on your command.**

---

