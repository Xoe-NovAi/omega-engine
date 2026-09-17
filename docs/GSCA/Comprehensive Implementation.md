---

## Comprehensive Implementation Plan: Unthrottled Parallel Search Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNTHROTTLED RESEARCH ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Node 1 (ASUS)                    Node 0 (HP)                          │
│  ┌─────────────────┐              ┌─────────────────┐                 │
│  │ asus_plan       │              │ kali            │                 │
│  │ (kernel/hw)     │◄──Tailscale──►│ (council/synth) │                 │
│  │                 │   Layer 2    │                 │                 │
│  │ grokster        │              │ makali          │                 │
│  │ (opencode intern)│             │ roc_racoon      │                 │
│  └────────┬────────┘              └────────┬────────┘                 │
│           │                                │                          │
│           ▼                                ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │           https://search.parallel.ai/mcp                     │     │
│  │  web_search (15 results)  +  web_fetch (5M chars, no strip)  │     │
│  └─────────────────────────────────────────────────────────────┘     │
│           │                                │                          │
│           ▼                                ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │              ~/WanderGround/ (Local Archive)                 │     │
│  │  inbox/  →  domains/  →  atlas (sqlite-vec + mempalace)     │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Global MCP Configuration (Node 1 + Node 0)

**File**: `~/.config/opencode/opencode.json` (both nodes)

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

**Environment Variables** (`~/.bashrc` both nodes):
```bash
# Node 1 (ASUS)
export PARALLEL_API_KEY="pk_asus_${HOSTNAME}_$(date +%Y%m)"
export PARALLEL_API_KEY_ASUS_PLAN="${PARALLEL_API_KEY}"
export PARALLEL_API_KEY_GROKSTER="${PARALLEL_API_KEY}"

# Node 0 (HP) - separate keys for audit isolation
export PARALLEL_API_KEY="pk_hp_${HOSTNAME}_$(date +%Y%m)"
export PARALLEL_API_KEY_KALI="${PARALLEL_API_KEY}"
export PARALLEL_API_KEY_MAKALI="${PARALLEL_API_KEY}"
```

---

### Phase 2: Agent Profile Configurations

#### A. Code-Gen Profiles (Zero Research Tools)
**File**: `~/.config/opencode/profiles/asus_build.json`
```json
{
  "profile": "asus_build",
  "model": "big-pickle",
  "tools": {
    "parallel-search": { "enabled": false }
  },
  "env": {
    "OPENCODE_ENABLE_PARALLEL": "false"
  }
}
```

**File**: `~/.config/opencode/profiles/roc_racoon.json` (Node 0)
```json
{
  "profile": "roc_racoon",
  "model": "big-pickle",
  "tools": {
    "parallel-search": { "enabled": false }
  },
  "env": {
    "OPENCODE_ENABLE_PARALLEL": "false"
  }
}
```

#### B. Deep Research Profiles (Unthrottled)
**File**: `~/.config/opencode/profiles/asus_plan.json` (Node 1)
```json
{
  "profile": "asus_plan",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15,
      "fetch_constraints": {
        "max_chars_per_request": 5000000,
        "strip_html_boilerplate": false,
        "extract_code_blocks_only": false
      }
    }
  },
  "system_prompt_file": "~/.config/opencode/prompts/asus_plan.md"
}
```

**File**: `~/.config/opencode/profiles/grokster.json` (Node 1)
```json
{
  "profile": "grokster",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15,
      "fetch_constraints": {
        "max_chars_per_request": 5000000,
        "strip_html_boilerplate": false,
        "extract_code_blocks_only": false
      }
    }
  },
  "system_prompt_file": "~/.config/opencode/prompts/grokster.md"
}
```

**File**: `~/.config/opencode/profiles/kali.json` (Node 0)
```json
{
  "profile": "kali",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15,
      "fetch_constraints": {
        "max_chars_per_request": 5000000,
        "strip_html_boilerplate": false,
        "extract_code_blocks_only": false
      }
    }
  },
  "system_prompt_file": "~/.config/opencode/prompts/kali.md"
}
```

**File**: `~/.config/opencode/profiles/makali.json` (Node 0)
```json
{
  "profile": "makali",
  "model": "big-pickle",
  "tools": {
    "parallel-search": {
      "enabled": true,
      "max_results": 15,
      "fetch_constraints": {
        "max_chars_per_request": 5000000,
        "strip_html_boilerplate": false,
        "extract_code_blocks_only": false
      }
    }
  },
  "system_prompt_file": "~/.config/opencode/prompts/makali.md"
}
```

---

### Phase 3: System Prompt Files (Raw Context Flooding)

#### `~/.config/opencode/prompts/asus_plan.md`
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
6. **Synthesize** → update `docs/HARDWARE.md` or `docs/AGENT_RUNBOOK.md` with exact line references

## FORBIDDEN
- Summaries, snippets, "key takeaways"
- Non-canonical sources (blogs, StackOverflow, secondary tutorials)
- Truncating outputs for brevity

## REQUIRED OUTPUT FORMAT
Every finding: file path + line numbers + raw config excerpt + behavioral implication for i7-13620H
```

#### `~/.config/opencode/prompts/kali.md`
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

#### `~/.config/opencode/prompts/grokster.md`
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

---

### Phase 4: WanderGround Archival Automation

**Directory Structure** (enforced by prompts):
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

**YAML Frontmatter Schema** (every inbox file):
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

**Audit Log Entry** (`~/WanderGround/audit/search_log.jsonl`):
```json
{"timestamp":"2026-09-17T14:32:10Z","entity":"asus_plan","query":"intel_pstate HWP...","tool":"parallel-search.web_search","results_count":15,"fetched_urls":["https://kernel.org/..."],"archived_to":"~/WanderGround/inbox/asus_plan_20260917_143210_intel_pstate.md","chars_fetched":4231000}
```

---

### Phase 5: Integration with Existing omega-hub Tools

**Don't duplicate — extend:**

| Existing Tool | New Behavior |
|---------------|--------------|
| `library_web_search` | Routes to `parallel-search.web_search` (remote MCP) |
| `library_fts_search` | Local WanderGround atlas (unchanged) |
| `library_ingest_pending` | Auto-indexes `inbox/` → `domains/` → `atlas` (unchanged) |
| `hivemind_post_context` | Shares findings across federation (unchanged) |
| `spawn_local_worker` | Can run local distillation of fetched docs (unchanged) |

**MCP server becomes a provider for `library_web_search`** — agents call the same tool, backend swaps to parallel.ai.

---

### Phase 6: Offline Fallback Cache (Sovereignty)

**Pre-populated at `~/WanderGround/cache/`**:
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

**Agent fallback behavior**: *"If parallel-search fails/times out >10s, search local cache via `grep -r` / `library_fts_search`. Log fallback in audit."*

---

### Phase 7: Validation & Testing

**1. MCP Registration Verification:**
```bash
opencode mcp list --verbose
# Expected: parallel-search → remote → https://search.parallel.ai/mcp → tools: web_search, web_fetch
```

**2. Tool Exposure Test:**
```bash
# In asus_plan profile:
web_search "intel_pstate HWP energy_performance_preference" --max-results 3
web_fetch "https://kernel.org/doc/html/v7.0/admin-guide/pm/intel_pstate.rst"
# Verify: returns >100k chars, complete document
```

**3. Archival Pipeline Test:**
```bash
# Verify file written to inbox/ with correct frontmatter
# Verify mempalace.index called
# Verify audit log entry created
```

**4. Cross-Node Federation Test:**
```bash
# Node 0 (kali) → parallel-search → fetch kernel doc
# Node 1 (asus_plan) → receives via hivemind_post_context
# Verify both nodes have raw doc in WanderGround
```

**5. Context Saturation Test:**
```bash
# Fetch 5 large kernel docs sequentially
# Verify context window holds all (no truncation)
# Verify synthesis quality improves with more raw context
```

---

### Phase 8: Rollback Procedures

| Component | Rollback Command |
|-----------|------------------|
| MCP config | `cp ~/.config/opencode/opencode.json.bak ~/.config/opencode/opencode.json` |
| Agent profiles | `rm ~/.config/opencode/profiles/*_research.json` |
| Env vars | Remove PARALLEL_API_KEY lines from `~/.bashrc` |
| WanderGround | Archive dir, restore from git if needed |
| Prompts | Restore from `~/.config/opencode/prompts/*.bak` |

---

### Open Questions for Final Confirmation

1. **Tool Names**: GSCA — confirm exact tool names exposed by `https://search.parallel.ai/mcp`? (`web_search`/`web_fetch` vs `parallel_search`/`parallel_fetch` vs `search`/`extract`)

2. **Rate Limits**: Per-key concurrent requests? Burst allowance? Daily quota? (Needed for `max_results: 15` + 5M chars × multiple agents)

3. **Streaming**: Does `web_fetch` support streaming/chunked response for 5M char docs?

4. **Auth**: Bearer token only, or mTLS support for enterprise?

5. **Regional Endpoints**: Any EU/APAC endpoints for latency optimization?

6. **Profile System**: Does OpenCode support `system_prompt_file` reference in profile JSON, or must prompts be inline?

7. **Node 0 Omega-Hub**: Should `omega-hub` expose a `library_web_search` wrapper that routes to parallel-search MCP for federation-wide access?

---

### Execution Order (Once Plan Mode Lifted)

```
1. Backup current opencode.json + profiles
2. Deploy global MCP config (both nodes)
3. Add env vars to ~/.bashrc (both nodes)
4. Create agent profile JSONs + prompt files
5. Create WanderGround directory structure
6. Pre-populate offline cache
7. Run validation suite (Phase 7)
8. Execute first real research task: full intel_pstate.rst + zram-generator + thermal-conf.xml ingestion
9. Verify archival + audit + mempalace indexing
10. Document in docs/AGENT_RUNBOOK.md
```

---

**Ready for GSCA's technical confirmations (Q1-5) and your go/no-go on profile system details (Q6-7).** Once confirmed, this plan is directly executable.

---

