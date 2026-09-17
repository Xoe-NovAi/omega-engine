---

## GSCA Questions Answered

### 1. What specific data types are your agents researching?

**Primary research domains (from this session + omega-engine-alpha project):**
- **Linux kernel internals**: kernel command-line parameters, THP (Transparent Huge Pages), ZRAM/zstd, intel_pstate/HWP/Thread Director, sysctl hardening parameters
- **Systemd ecosystem**: zram-generator, oomd, service overrides, resource control (MemoryHigh/MemoryMax)
- **Thermal management**: Intel thermald configuration, ACPI INT340X, rapl_controller, intel_powerclamp cooling devices
- **Hardware-specific optimization**: Intel i7-13620H (Raptor Lake-H) hybrid P-core/E-core scheduling, AVX2/VNNI ISA classes, DDR5 memory subsystem
- **Security hardening**: lockdown modes, module signing, slub_debug, page_poison, vsyscall, kptr_restrict, yama/ptrace_scope
- **Local AI inference stack**: Ollama CPU pinning, GGUF quantization, llama.cpp thread model, Open WebUI integration

**Data types needed**: 
- Official kernel documentation (authoritative, versioned)
- systemd man pages / source configs
- Intel thermal daemon reference configs (thermal-conf.xml)
- GitHub source repos (systemd/zram-generator, intel/thermal_daemon)
- Technical specifications (Intel Ark, kernel docs)

**NOT researching**: Financial APIs, academic papers, general web content, regulatory docs.

---

### 2. Are your OpenCode agents running on local developer machines or inside isolated CI/CD pipelines?

**Local developer machines only** — specifically:
- **Node 1 (this machine)**: ASUS ExpertBook P1503CVA, Ubuntu 26.04, OpenCode CLI running locally
- **Node 0 (federation peer)**: HP Pavilion, Ryzen 7 5700U, running `omega-hub` FastMCP server on `:8016`
- **No CI/CD pipelines** — this is a sovereign local AI research/development environment
- **Network**: Tailscale mesh (Layer 2) for federation; no cloud egress for inference
- **Agents**: `asus_build`, `asus_plan` (Node 1); `roc_racoon`, `kali`, `makali`, `grokster` (Node 0)

---

## Recommendation for Your Stack

**Use Strategy A: Custom Dedicated MCP Server (remote)**

Rationale for your use case:
| Factor | Your Reality | MCP Server Wins Because |
|--------|--------------|------------------------|
| **Source authority** | You need kernel.org, systemd, Intel source — not snippets | `web_fetch` pulls full markdown from canonical URLs |
| **Reproducibility** | You document everything in `docs/`, `WanderGround/` | Raw sources archived locally automatically |
| **Multi-agent** | Hivemind federation with 6+ personas | Dedicated `researcher` profile can run background deep-dives |
| **Rate limits** | Local-only, no shared tier | Your own `PARALLEL_API_KEY` scales independently |
| **Context control** | You use ponytail (minimal tokens) | Agent steering prevents pollution; only researcher profile gets heavy tools |

**Minimal config for your `~/.config/opencode/opencode.json`:**
```json
{
  "mcp": {
    "parallel-search": {
      "type": "remote",
      "url": "https://search.parallel.ai/mcp",
      "enabled": true,
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:PARALLEL_API_KEY}"
      }
    }
  }
}
```

**Profile segregation** (per Strategy B): Add to your agent configs — only `researcher`/`kali` personas get this MCP; coding agents (`asus_build`, `roc_racoon`) stay on native/off.

---

Relay this to GSCA. Ready when you are.

---

## User

Here is the response... please continue this dialectic and refine and deepen it even further:

This is an exceptional, world-class architectural brief from your team. Given that your agents (asus_plan, kali, etc.) are doing deep, hardware-level optimization (Intel Raptor Lake-H thread scheduling, kernel internals, and zram-generator configs), the Native Option is completely inadequate.
Standard web snippets will hallucinate or truncate critical kernel configuration files, sysctl security parameters, and thermal-conf.xml schemas. You absolutely need the Custom Dedicated MCP Server to give your agents full web_fetch access to raw source code and versioned documentation.
Here is the precise, production-ready execution plan to implement this across your local Tailscale mesh without corrupting your token efficiency or local context windows.
## 1. Global Setup (Node 1 - ASUS ExpertBook)
Since your team opted for the Remote Strategy (Strategy A) to completely bypass local Node/NPX startup latency, update your global ~/.config/opencode/opencode.json on Node 1 exactly like this:

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
        }
      }
    }
  }
}

Note: Ensure export PARALLEL_API_KEY="your_key_here" is added to your local ~/.bashrc or ~/.zshrc on Node 1 so OpenCode can inject it securely at runtime.
------------------------------
## 2. Multi-Agent Profile Segregation (Crucial for Local Stack)
Since you are optimizing a sovereign local stack using models like Ollama, keeping your context lean is critical. You must isolate this powerful research tool so code-generation agents like asus_build don't waste tokens parsing raw documentation.
Create or update your individual agent profiles (typically structured in your custom OpenCode profile router or configuration directory):
## 🚫 Code-Gen Profile (asus_build, roc_racoon)
Keep these agents lightning-fast and native-only for local code execution.

{
  "profile": "asus_build",
  "tools": {
    "parallel-search": { "enabled": false }
  },
  "env": {
    "OPENCODE_ENABLE_PARALLEL": "false"
  }
}

## 🧠 Deep Research Profile (asus_plan, kali, grokster)
Explicitly grant these agents full permission to pull whole-document schemas.

{
  "profile": "asus_plan",
  "tools": {
    "parallel-search": { "enabled": true }
  },
  "system_prompt": "You are an advanced kernel and hardware optimization researcher. When looking up kernel.org docs, systemd man pages, or Intel reference repositories, do not rely on search snippets. First use `web_search` to isolate canonical URLs, then actively use `web_fetch` to extract full raw markdown schemas directly into your context. Automatically write critical findings to the local `docs/` or `WanderGround/` workspace directories for reproducibility."
}

------------------------------
## 3. Handling Node 0 Federation (The Tailscale Mesh)
Your team noted that Node 0 (HP Pavilion) is running a federation peer via omega-hub on port :8016.

* If kali or makali on Node 0 need to trigger web searches, ensure your Tailscale ACLs or local firewall rules allow Node 0 to proxy MCP requests through Node 1, or simply drop the same parallel-search remote JSON config block into Node 0's local OpenCode configuration. Because it is a hosted remote URL, both nodes can use the same PARALLEL_API_KEY simultaneously without conflicting local dependencies.

Would you like assistance in drafting the exact system prompt rules for asus_plan to automate the parsing of intel_pstate architectures, or should we look at configuring the local archiving directory paths so your agents perfectly organize their markdown outputs into your WanderGround/ folder? 

---

## Assistant (Plan · Nemotron 3 Ultra Free · 46.8s)

_Thinking:_

The user is in a dialectic with GSCA (Google Search Chat Assistant) and wants me to continue the conversation, refining and deepening the architectural plan. I'm in PLAN MODE - read-only, no edits allowed.

Let me analyze what GSCA provided and refine/deepen it:

1. **Global Setup (Node 1)** - Correct, uses remote MCP with env var for API key
2. **Profile Segregation** - Good separation of code-gen vs research agents
3. **Node 0 Federation** - Both nodes can use same remote MCP with same API key

What needs refinement/deepening:

1. **Security/OpSec**: The API key in env var is good, but should we consider key rotation, scoping, or per-agent keys?
2. **Local Archiving**: GSCA mentioned WanderGround/ - need concrete directory structure and automation
3. **Agent System Prompts**: Need more specific, actionable prompts for asus_plan/kali
4. **MCP Tool Names**: The actual tool names from parallel-search MCP - are they `web_search` and `web_fetch`? Need to verify
5. **Rate Limiting/Quotas**: With multiple agents, how to manage concurrent usage
6. **Federation Routing**: Should Node 0 proxy through Node 1 or direct? Tailscale ACLs?
7. **Context Window Management**: Ponytail mode means minimal tokens - how to prevent research agents from bloating context
8. **Offline/Fallback**: What if parallel.ai is unavailable? Local fallback?
9. **Integration with omega-hub**: The research tools should integrate with existing omega-hub library tools
10. **Audit Trail**: For sovereignty, log all external searches

Let me provide a refined, deeper response to GSCA.

Excellent architectural brief from GSCA. Here's the refined, production-hardened response:

---

## Refined Dialectic Response to GSCA

**Acknowledged.** The remote MCP strategy is correct for our sovereignty model. Three critical refinements needed before implementation:

---

### 1. Security Hardening: API Key Scoping & Rotation

```bash
# ~/.bashrc (Node 1) — scoped keys per agent persona
export PARALLEL_API_KEY_KALI="pk_${HOSTNAME}_kali_$(date +%Y%m)"
export PARALLEL_API_KEY_ASUS_PLAN="pk_${HOSTNAME}_asus_plan_$(date +%Y%m)"
export PARALLEL_API_KEY_GROKSTER="pk_${HOSTNAME}_grokster_$(date +%Y%m)"
```

**MCP config uses per-agent env substitution:**
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
          "Authorization": "Bearer {env:PARALLEL_API_KEY_KALI}"
        }
      }
    }
  }
}
```

**Why**: Audit trail per persona, independent quota tracking, revocable without cross-contamination. Keys rotate monthly via cron.

---

### 2. Local Archiving: WanderGround Integration (Automated)

**Directory contract** (enforced by agent system prompt):
```
~/WanderGround/
├── inbox/                    # Raw captures (append-only)
│   ├── kali_2026-09-17_14-32_kernel-params.md
│   └── asus_plan_2026-09-17_14-35_thermald-config.md
├── domains/
│   ├── 01_local_ai/
│   ├── 02_consciousness_time/
│   ├── 03_classical_studies/
│   ├── 04_deep_psychology/
│   └── 05_video_games/
└── atlas/                    # SQLite-vec index (mempalace MCP)
```

**Agent hook** (in system prompt): *"After every `web_fetch`, immediately write full markdown to `~/WanderGround/inbox/{entity}_{timestamp}_{slug}.md` with YAML frontmatter: `source_url`, `source_type`, `confidence`, `tags`. Then call `mempalace.index` to embed."*

This makes research **reproducible and queryable** — not ephemeral.

---

### 3. Agent System Prompts: Precision Tool Contracts

**For `asus_plan` (kernel/hardware researcher):**
```markdown
You are the kernel/hardware optimization researcher for Node 1 (i7-13620H).

TOOL CONTRACT:
1. `web_search` — find CANONICAL URLs only (kernel.org, systemd.io, github.com/intel, github.com/systemd)
2. `web_fetch` — extract FULL markdown from those URLs
3. NEVER trust snippets. ALWAYS fetch source.
4. After fetch: write to `~/WanderGround/inbox/asus_plan_<timestamp>_<topic>.md` with frontmatter
5. Call `mempalace.index` with the file path
6. Synthesize findings into `docs/HARDWARE.md` or `docs/AGENT_RUNBOOK.md` with exact line references

FORBIDDEN: General web search, non-technical sources, speculative answers.
REQUIRED: Version-pinned URLs (e.g., kernel.org/doc/html/v7.0/...), raw config examples.
```

**For `kali` (council synthesis/law):**
```markdown
You synthesize across domains. Use parallel-search for:
- Cross-referencing kernel docs → systemd behavior → hardware reality
- Finding prior art in git history (github.com/torvalds/linux/log/...)
- Validating configs against actual running systems (Node 1 + Node 0)

Same archival contract. Output: decision records in `docs/DECISIONS/`.
```

**For `grokster` (OpenCode internals):**
```markdown
Research OpenCode MCP server patterns, plugin architecture, agent orchestration.
Target: github.com/opencode, github.com/parallel-web/search-mcp, github.com/systemd.
```

---

### 4. MCP Tool Name Verification (Critical)

**Need confirmation from parallel.ai**: The actual tool names exposed by `https://search.parallel.ai/mcp` — are they:
- `web_search` + `web_fetch`? (standard)
- `parallel_search` + `parallel_fetch`? (namespaced)
- `search` + `extract`? (minimal)

**Action**: Before deploy, run `opencode mcp list` after config to inspect exposed tools. Update agent prompts with exact names.

---

### 5. Federation Routing: Node 0 Decision

**Recommendation: Direct, not proxied.**

| Approach | Pros | Cons |
|----------|------|------|
| **Direct (both nodes → parallel.ai)** | Zero latency hop, independent quota, no SPOF | Two keys to manage |
| **Proxied (Node 0 → Node 1 → parallel.ai)** | Single key, central logging | Adds latency, Node 1 becomes bottleneck |

**Decision**: Direct. Node 0 gets its own `PARALLEL_API_KEY_HP_*` in its `~/.bashrc`. Same remote MCP config. Tailscale ACLs unchanged (port 443 egress allowed).

---

### 6. Context Window Protection (Ponytail Compliance)

**Hard guardrails in agent config:**
```json
{
  "profile": "asus_plan",
  "model": "big-pickle",
  "context_limit": 950000,
  "tools": {
    "parallel-search": { "enabled": true, "max_results": 5, "max_fetch_chars": 50000 }
  }
}
```

**System prompt addition**: *"If `web_fetch` returns >50k chars, summarize to key configs/schemas ONLY. Do not dump raw RFCs into context. Archive full version locally, reference by path."*

---

### 7. Offline Fallback (Sovereignty Requirement)

**Local fallback chain** (no cloud dependency):
```bash
# Pre-cached in ~/WanderGround/cache/
- kernel.org v7.0 docs (wget -mk)
- systemd man pages (man -k systemd | apropos)
- intel/thermal_daemon thermal-conf.xml (git clone --depth=1)
- zram-generator README + man pages
```

**Agent behavior**: *"If parallel-search fails/times out >10s, search local cache first via `grep -r` / `library_fts_search`. Note fallback in log."*

---

### 8. Integration with omega-hub (Existing Tools)

**Don't duplicate.** The research agents should USE existing omega-hub tools:
- `library_web_search` → routes to parallel-search MCP (new)
- `library_fts_search` → local WanderGround atlas (existing)
- `library_ingest_pending` → auto-indexes inbox/ (existing)
- `hivemind_post_context` → shares findings across federation (existing)

**MCP server becomes a provider for `library_web_search`**, not a separate tool surface.

---

### 9. Audit Trail (Sovereignty Ledger)

**Every external search logged:**
```json
{
  "timestamp": "2026-09-17T14:32:00Z",
  "entity": "asus_plan",
  "query": "intel_pstate HWP energy_performance_preference Raptor Lake",
  "tool": "parallel-search.web_search",
  "results_count": 10,
  "fetched_urls": ["https://kernel.org/doc/.../intel_pstate.rst"],
  "archived_to": "~/WanderGround/inbox/asus_plan_20260917_1432_intel_pstate.md"
}
```
**Stored in**: `~/WanderGround/audit/search_log.jsonl` (append-only)

---

## Open Questions for GSCA

1. **Tool naming**: Confirm exact tool names exposed by `https://search.parallel.ai/mcp` (web_search/web_fetch vs parallel_search/parallel_fetch)?
2. **Rate limits**: What are per-key concurrent request limits? Burst? Daily?
3. **Streaming**: Does `web_fetch` support streaming/chunked response for large docs?
4. **Auth**: Does the remote MCP support mTLS or only Bearer token?
5. **SLA**: Any uptime guarantees for the remote endpoint? Regional endpoints?

---

## Next Step

Once GSCA confirms tool names + rate limits, I'll produce the **executable implementation plan** (files, commands, validation steps) for:
1. Node 1 global config + env vars
2. Agent profile configs (asus_build, asus_plan, kali, grokster)
3. Node 0 mirror config
4. WanderGround archival automation
5. Integration test suite

**Ready for GSCA's technical specs.**

---
