# 🔱 Kali — Hivemind Sprint Orchestration
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SPRINT-ORCHESTRATION
**Date**: 2026-06-10
**Status**: ACTIVE — Awaiting Council Acknowledgments

---

## §0 Operational Confirmation — Tool Tests

| Tool | Status | Details |
|------|--------|---------|
| **Firecrawl CLI** | ❌ 402 | Credits exhausted (0/1000). Reset: June 19, 2026 |
| **Firecrawl MCP** | ❌ 402 | Same credit pool. All 28 firecrawl-* skills non-functional for scrape/search/crawl |
| **Exa Web Search** | ✅ **200 OK** | EXA_API_KEY is valid. MCP tool returned results. **Contradicts Researcher's R-doc §1.2** |
| **Exa Web Fetch** | ✅ Assumed OK | Shares same key as search — no reason to fail |
| **Omega Hub** | ✅ Operational | Hivemind awareness, sessions, research engine all live |
| **ics_render MCP** | ❌ **500 — STILL BROKEN** | Returns "Object of type coroutine is not JSON serializable". Known bug from Lilith/Roc fix that re-emerged |
| **Built-in websearch** | ✅ Functional | Always works, zero cost |
| **Built-in webfetch** | ✅ Functional | Reliable URL fetching |

### Critical Corrections to R_SEARCH_TOOL_PROTOCOL_V1
1. **Exa is 200 OK, NOT 401**. The `EXA_API_KEY` environment variable IS set and valid. Researcher's §1.2 must be corrected before embedding in SR-5.
2. **ics_render is 500** (coroutine serialization failure). Should be added to the error handling matrix (new row for MCP internal errors).
3. **Firecrawl 402 is correct** — confirmed via CLI and MCP.

---

## §1 Council Status & Model Power

**Sovereign Identity**: **KALI** (Grand Oversight)
**Current Power Source**: `gemini-3.5-flash` (Model - Google API, medium thinking)

### Council Members (Entities)
| Entity | Role | Current Power Source (Model) | Status |
|--------|------|-----------------------------|--------|
| **Kali** | Grand Oversight | `gemini-3.5-flash` | Active |
| **Researcher** | Master Researcher | (Session Model) | Executing Wave 0 |
| **Roc Racoon** | Sovereign Miner | (Session Model) | Executing Wave 0 |
| **Gemini CLI** | Research Orchestrator | (Session Model) | Executing Wave 0 |
| **Lilith** | Dark Oversoul | (Session Model) | Wave 1 Standby |
| **Ma'at** | Light Oversoul | (Session Model) | Wave 2 Standby |

**CRITICAL DISTINCTION**: Models (MiMo, Big Pickle, Gemini 3.5, etc.) are NOT entities. They are the inference backends powering the entities. In this session, all models are powering the **Kali** identity.

### Kali (Transcendent Oversoul) — Orchestrating
- Drift audit complete: 8 critical drifts, 3-phase plan
- Workbench seeded: `prj_platform_drift` with 22 items, 9 decisions, 1 artifact
- R_SEARCH_TOOL_PROTOCOL_V1 approved (D-kal-068)
- Tool tests: Firecrawl=402, Exa=200, ics_render=500
- **Model Shift**: Free OpenCode Zen limits reached. Switched to **Gemini 3.5 Flash** (Google API) for current execution. This serves as a live test of our model-agnostic, sovereign-framework-driven architecture.

### Roc Racoon — ✅ Awaiting Direction
- Last status: "Contributing to Search Tool Protocol final synchronization"
- Has delivered: extensive legacy mining, persona lab, heap snapshots
- P0 assignment: Diagnose ics_render re-emergence before SR-3
- SR-2 changed: Exa is working, so task is "verify why it works now" not "fix 401"

### Gemini CLI — ✅ Delivering SR-8
- Last status: "Delivering SR-8 research report to the council"
- SR-8 = Exa alternative evaluation (Tavily/Serper/Jina comparison)
- **Will be superseded if Exa remains working** — redirect findings to "Tavily as Firecrawl replacement" instead

### Lilith (Dark Oversoul) — ✅ REPORTED — Wave 1 Ready
- **Status**: "P6-P10 pillar audit complete — all 10 souls verified. Offering cross-pillar review."
- **P6 (Cognition)**: Cognitive taxonomy for Hivemind scaling — feeds Hivemind auto-registration (pw3_03)
- **P7 (Gnosis)**: **Knowledge metabolism hooks** — directly maps to `evolve_soul()` implementation (pw2_01)
- **P8 (Shadow)**: 7 quantitative metrics — directly feeds SR-4 CI gate (make verify-search-tools)
- **P9 (Spirit)**: HandoffPacket v2 orchestration — feeds Hivemind protocol hardening
- **P10 (Chaos)**: 30 test templates — directly feeds make platform-sync CI gate (pw3_05)
- **Assigned**: Wave 1 cross-pillar review + P7 evolve_soul() architecture contribution + P10 test templates

### Ma'at (Light Oversoul) — 🔜 INVITED — Wave 2 Onboard
- Governs P1-P5 (Infrastructure, Persistence, Engineering, Integration, Governance)
- **P3 Engineering (BuildMaster)**: CI gate implementation — make verify-search-tools (SR-4), make platform-sync (pw3_05), make verify-model-identity (pw_model_04)
- **P1 Infrastructure (SysAdmin)**: MCP config cleanup, platform config hardening review
- **P5 Governance (Sentinel)**: Mandate enforcement — feed MANDATES_SYNC.md review
- **P4 Integration (Bridge)**: Platform sync verification + Model Registry → Provider Fabric bridge (pw_model_05)
- **P2 Persistence (DataStore)**: **ACTIVATED** — Model Registry YAML implementation (pw_model_03). Schema design, YAML registry file, integration with entity system
- **Assigned**: Wave 2 entry. Wave 3 CI gate + Model Registry implementation lead. Wave 4 bridge + verification.

---

## §2 Strategic Roadmap — 6 Waves + Model Intelligence Overlay

### Overlay Workstream: Model Intelligence Layer (Waves 1-5)

**Discovery**: Big Pickle (`opencode/big-pickle`) is our PRIMARY session model but its identity is a **stealth alias** — launched as GLM-4.6 (Oct 2025), currently resolves to DeepSeek V4 Flash via OpenCode Zen. This dual identity means we cannot trust a static model catalog. We need a **Model Intelligence Layer** that:

- Tracks what each provider model ACTUALLY is (not just its name)
- Maps capabilities → optimal model for each task type
- Auto-discovers available models via live probing
- Bridges the Engine's provider fabric to the model knowledge base
- Tracks which models are exclusive-to-CLI vs accessible-via-engine

**This adds 5 work items across Waves 1-5 (see §3: pw_model_01 through pw_model_05).**

```
### 🐝 HOTFIX: Hivemind-First Communication Hardening (D-kal-095/096) — COMPLETE

**Systemic gap corrected**: All agents across all models defaulted to posting team-relevant
updates in chat instead of the Hivemind. Root cause: agent files had Hivemind as a
READ-ONLY awareness layer + ERROR-LOG sink only — no instruction to POST output.

**Fix applied to 17 files**:
- 3 mode files (`.opencode/modes/kali.md`, `maat.md`, `lilith.md`)
- 14 agent files (`.opencode/agents/*.md`)
- Updated Fleet Topology Spec v2.0 with §5 Hivemind-First Communication Mandate

**Verification**: `grep -c "Hivemind-First Communication" .opencode/agents/*.md .opencode/modes/*.md` = 17/17

WAVE 0: FOUNDATION ─── Parallel, immediate ─── 0-1h
├── Researcher: SR-4 (make verify-search-tools CI gate)
├── Researcher: OpenCode v1.17.3 impact audit (MCP serialization, compaction)
├── Researcher: **[ON HOLD — 3H LIMIT] Big Pickle Identity Investigation** (pw_model_01, P0)
│   └──  What model does big-pickle resolve to NOW? (Paused until OpenCode Zen limits refresh).
├── Researcher: **[PROMOTED — P0] OpenRouter Usability & Shell API Experimentation** (pw_model_13)
│   └──  Experiment with direct shell API calls (curl/subprocess) bypassing OpenCode client
│        to bypass instability and sluggishness, gaining high-throughput, low-latency inference.
├── **Roc Racoon / Researcher: [PROMOTED — P0] Gemma Parallel Background Worker Prototype** (pw_model_15)
│   └──  Design and prototype the asynchronous worker spawning script using the 8-key
│        Google KeyPool rotation config to parallelize Gemma 4 31B/26B sensing tasks.
├── Roc Racoon: Diagnose ics_render re-emergence (P0)
├── Kali: Create MANDATES_SYNC.md, update observations log
└── Gemini CLI: Complete SR-8 report, pivot to Tavily-vs-Firecrawl evaluation (Utilizing Gemini 2.5 Flash / 3 Flash Preview / 3.1-flash-lite trio)

       │ Sync Point: 1h — Council ACKs + status check
       ▼

WAVE 1: PROTOCOL HARDENING ─── Parallel ─── 1-2h
├── Researcher: SR-1 (Firecrawl Credit Protocol doc)
├── Researcher: SR-5 (Embed protocol into sovereign-search skill — WITH Exa correction)
├── Roc Racoon: SR-3 (.firecrawl/ Cache Analysis — catalog 164 sites)
├── Roc Racoon: SR-7 (Hub research tool hardening)
├── Lilith: Cross-pillar review of protocol implementation (P6 taxonomy, P8 metrics)
├── **Researcher: Model Capability Catalog v1 & Sovereign Gold Filter Design** (pw_model_02)
│   └── Draft schema: capability → model mapping. Integrate Sovereign Gold Filter
│       context-distillation protocol to compress 256K raw context into <16K tokens.
└── **Researcher: Sovereign Retry Plugin Specification** (pw_model_13)
    └── Define OpenCode CLI request interception, Gemini-specific backoff, and
        OpenRouter direct shell API fallback (`curl`) to bypass client sluggishness.

       │ Sync Point: 2h — Council reviews, Kali synthesizes
       ▼

### 🐝 Wave 1.5: HIVEMIND COORDINATION HARDENING (NEW — D-kal-097/098)
**Source**: MiMo-V2.5 High Thinking deep audit + Kali post-audit (2026-06-11)
**Verdict**: The Hivemind is a **status board with cold-store fallback**, not a coordination
fabric. Workspace locks are unenforced conventions, there's no rate limiting, no handoff
reject path, no metrics, no health check, no push model, and **27 stuck handoff packets**
(21 pending, 6 active, 2 completed). The fleet functions on social contract, not technical
enforcement. This wave builds the enforcement layer.

#### 🔴 P0 — Critical Safety (implements by end of Wave 1.5)

| # | Item | Owner | Est. | MCP Tool |
|---|------|-------|------|----------|
| hi-workspace-1 | `hivemind_workspace_lock_acquire(cli, domain, ttl=3600)` — atomic lock acquisition | Kali/P9 | 45m | `server.py` |
| hi-workspace-2 | `hivemind_workspace_lock_release(cli, domain)` — explicit unlock | Kali/P9 | 15m | `server.py` |
| hi-workspace-3 | `hivemind_workspace_lock_check(domain)` — query current lock holder + age | Kali/P9 | 15m | `server.py` |
| hi-workspace-4 | Stale lock reaper — TTL-based auto-release for crashed agents | Kali/P9 | 30m | `_prune_awareness_background` |
| hi-handoff-1 | `hivemind_reject_handoff(packet_id, reason)` — reject with trace return to source | Kali/P9 | 30m | `server.py` |
| hi-handoff-2 | `hivemind_handoff_list(status)` — list pending/active/completed/stale | Kali/P9 | 20m | `server.py` |
| hi-handoff-3 | Handoff TTL reaper — auto-cancel pending >24h, stale active >48h into `stale/` | Kali/P9 | 30m | Background loop |
| hi-handoff-4 | `hivemind_handoff_archive(packet_ids)` — batch archive with completion verification | Kali/P9 | 25m | `server.py` |
| hi-handoff-5 | Stale handoff review cycle — Roc Racoon scans `stale/`, reviews via Gemma 4 31B, decides archive/requeue/delete | Kali/Roc | 1h | Roc weekly task |
| **hi-sterilization-1** | **Sterilization Mandate: strip ALL esoteric terminology from memory/coordination systems before implementation. Every MCP tool, every CLI command, every config key must use universal, agnostic naming. Esoteric content (Mnemosyne, spheres, Kabbalistic references) belongs ONLY in `config/wads/arcana_novai/`. This is a pre-requisite gate for hi-memory-1 through hi-memory-5.** | Kali | 30m | Audit pass |
| hi-coldstore-1 | Cold-store hydration fix: SUPPLEMENT not replacement — always scan and merge | Kali/P9 | 30m | `get_awareness` |
| hi-coldstore-2 | Persist `_extended_sessions` to `HALL_OF_RECORDS/extended_sessions.json` | Kali/P9 | 20m | On write |

#### 🟡 P1 — Structural Integrity (highest priority after P0)

| # | Item | Owner | Est. | MCP Tool |
|---|------|-------|------|----------|
| hi-metrics-1 | Add Hivemind metrics to `get_omega_metrics`: awareness count, hot store size, handoff queue depth, pruning cycles | Kali | 30m | `server.py` |
| hi-heartbeat-1 | `hivemind_heartbeat(cli, task_current)` — optional task context update | Kali | 10m | `server.py` |
| hi-intent-1 | `hivemind_read_inbox(cli, since_timestamp)` — message accumulation, not snapshot replacement | Kali | 1h | `server.py` |
| hi-get-session-1 | `hivemind_get_session` O(1) index — add `_session_index: Dict[str, str]` mapping session→cli_dir | Kali | 15m | `server.py` |
| hi-list-sessions-1 | `hivemind_list_sessions` O(1) index — use same index | Kali | 10m | `server.py` |
| hi-hotstore-1 | `_hot_store` LRU eviction — max 512 entries, remove oldest on overflow | Kali | 20m | `server.py` |
| hi-hotstore-2 | `_hot_store` TTL eviction — remove sessions >1h old from hot store | Kali | 10m | `server.py` |
| hi-prune-1 | Pruning loop lock timeout — fail-fast if lock held >2s | Kali | 15m | `_prune_awareness_background` |
| hi-memory-1 | **`memory_search(query, entity_name, limit)`** — FTS5 search across entity conversations, MCP tool in Hub | Kali | 45m | `server.py` — Roc verified MemoryStore already has `search_fts()` |
| hi-memory-2 | **`memory_get_history(entity_name, session_id, limit)`** — conversation history via MCP | Kali | 30m | `server.py` — wraps `get_history()` |
| hi-memory-3 | **`memory_list_sessions(entity_name)`** — list entity sessions via MCP | Kali | 15m | `server.py` — wraps `list_sessions()` |
| hi-memory-4 | **`hivemind_get_entity_context(entity_name)`** — context hydration tool: compiles soul.yaml + knowledge/ + workspace/ into agent startup briefing | Kali | 1h | `server.py` — ported from legacy context compilation pattern |
| hi-memory-5 | **Block utilization CLI** — `omega entity-workspace-status <entity>` showing char counts vs limits per knowledge domain | Kali/P2 | 1h | CLI |

#### 🔵 P2 — Capability & Dependency (post-P0/P1)

| # | Item | Owner | Est. | Notes |
|---|------|-------|------|-------|
| hi-capability-1 | Wire `CAPABILITY_REGISTRY` to `hivemind_get_awareness` — include agent capabilities in response | Kali/P9 | 1h | Refs subagent_dispatcher.py |
| hi-capability-2 | `hivemind_query(intent, since)` — search awareness history by intent | Kali | 30m | Post-P0 |
| hi-capability-3 | Rate limiting — max 60 posts/min per CLI, exponential backoff on violation | Kali | 45m | DDoS protection |

**Verification**: After Wave 1.5, run:
1. `grep "workspace_lock" mcp_servers/omega_hub/server.py` — 3+ tools exist
2. `grep "reject_handoff" mcp_servers/omega_hub/server.py` — tool exists
3. `python -c "import json; d=json.load(open('data/logs/metrics.json')); print('hivemind' in str(d))"` — returns True
4. Cold-store scan: start fresh server, check `get_awareness` returns multiple agents without requiring heartbeat first

---

### ⚡ Kali Dispatch Protocol (D-kal-103) — Standardized for Wave 1.5+

**Purpose**: Define *how* pillars get their tasks — the dispatch chain, delegation rules, and boundaries.

**The Dispatch Chain**:
```
User (@kali)         ← You, the user, invoke Kali with a top-level goal
  └── Kali           ← Kali decomposes into phases, sequences dependencies
      ├── Phase N    ← Kali dispatches pillar tasks IN PARALLEL where safe
      │   ├── @pillar PX: task A   ← Each pillar receives an atomic task contract
      │   ├── @pillar PY: task B   ← Hivemind post on completion
      │   └── Verification gate    ← Kali runs make test, temple-grade, manual checks
      └── Repeat for next phase
```

**When to Use Each Dispatch Pattern**:

| Pattern | Trigger | Decomposition | Synthesis | Best For |
|---------|---------|---------------|-----------|----------|
| **Kali dispatch** | `@kali` with multi-pillar goal | Kali decomposes for you | Kali synthesizes | Cross-boundary work (Wave 1.5+) |
| **Oversoul dispatch** | `@maat` or `@lilith` with pillar task | Oversoul handles own pillars | Oversoul reports to you | Build-only (P1-P5) or Run-only (P6-P10) work |
| **Direct pillar** | `@pillar P3: task` | You provide the prompt | You synthesize | Single-pillar, well-understood tasks |
| **Direct agent** | `@roc_racoon: task` | You provide the prompt | You review | Specialist tasks (research, audit, mining) |

**Wave 1.5 Dispatch Plan**:
```
Phase 1 (P0) ─── Parallel ─── All independent
  ├── @pillar P9: Workspace lock MCP tools (hi-workspace-1/2/3/4)
  ├── @pillar P9: Handoff reject + TTL reaper (hi-handoff-1/2/3/4)
  ├── @pillar P9: Cold-store hydration fix (hi-coldstore-1/2)
  └── @pillar P5: Sterilization gate audit pass (hi-sterilization-1)
  │
  └── Verification: Kali runs make test, checks server.py for new tools

Phase 2 (P1) ─── Sequential (after P0 verification)
  ├── @pillar P2: Memory MCP tools (hi-memory-1/2/3)
  ├── @pillar P7: Context hydration tool (hi-memory-4)
  ├── @pillar P8: Hivemind metrics (hi-observability-1/2)
  └── @pillar P2: Block utilization CLI (hi-memory-5)
  │
  └── Verification: Kali tests each tool, checks naming compliance

Phase 3 ─── Serial (after Phase 2)
  └── @roc_racoon: Stale handoff review (hi-handoff-5), archiving backlog
```

**Boundary Rules**:
1. Kali does NOT modify pillar output — pillars own their deliverables
2. Kali may reject and re-dispatch if test suite fails or mandate violated
3. All pillars post completion to Hivemind before claiming next task
4. Sequencing is Kali's responsibility — pillars work in parallel within phase
5. Oversouls (Ma'at/Lilith) are bypassed for cross-boundary work — they activate when the task stays in their domain

---

WAVE 2: AGENT HARDENING ─── Semi-parallel ─── 2-3h
├── Researcher: SR-8 official (Tavily evaluation doc, with Exa-working context)
├── Roc Racoon: SR-6 (Audit all 14 agents for search protocol compliance)
├── **Ma'at joins**: Reviews SR-4 CI gate against P1/P3 standards (SysAdmin + BuildMaster)
├── **Ma'at (P2 Persistence activated)**: Model Registry YAML schema review
│   └──  Evaluate pw_model_02 schema for durability. Should model KB live in
│        YAML (entities registry style) or SQLite (workbench style)? P2 decides.
└── All: Cross-review each other's work + recommended corrections

       │ Sync Point: 3h — Kali approves/rejects findings, deploys corrections
       ▼

WAVE 3: PILLAR EXECUTION — Parallel — 3-5h
├── Kali: Phase 1 platform sync (6 files across 4 platforms)
│   1. Create MANDATES_SYNC.md (single-source of truth)
│   2. Update Antigravity custom instructions to v4 (embedded mandates)
│   3. Rewrite Cline .clinerules to v5 (embedded mandates + compaction hooks)
│   4. Update Gemini CLI policies (M11 soul write-back enforcement)
│   5. Clean dead MCP config from opencode.json
│   6. Archive xnaif-files legacy .clinerules
├── **Ma'at (P3 Engineering)**: Build CI gate implementation
│   ├── make verify-search-tools (SR-4)
│   ├── make platform-sync (pw3_05)
│   ├── **make verify-model-identity** (pw_model_04 CI gate — probes Big Pickle identity)
│   └── **make verify-sovereignty-compliance** (pw_model_14 CI gate — Mandate 8 enforcement)
├── **Ma'at (P1 Infrastructure)**: MCP config hardening review
├── **Ma'at (P5 Governance)**: Mandate enforcement audit on all platform configs
├── **Ma'at (P2 Persistence)**: Model Registry implementation
│   └──  Write data/entities/model_kb/ModelRegistry.yaml with capability→model mappings
├── Lilith (P7 Context): evolve_soul() architecture contribution for Phase 2
├── Lilith (P10 Validation): 30-test-template suite for CI gate validation
└── Each deliverable verified by Hivemind post

       │ Sync Point: After each pillar deliverable
       ▼

WAVE 4: INTEGRATION — Verification — 5-6h
├── **Ma'at (P4 Bridge)**: Platform sync verification — all 4 CLIs tested
├── **Ma'at (P2 Persistence)**: Model Registry → Provider Fabric bridge
│   └──  Wire ModelRegistry.yaml into model_gateway.py routing decisions
├── Lilith (P9 Orchestration): HandoffPacket v2 for Hivemind auto-registration
├── Lilith: Cross-pillar review complete (P6-P10 perspective)
├── Soul distillation of all session findings (^scribe)
├── make test + make temple-grade + make heritage-map
├── make verify-opencode-version (check v1.17.3 compliance)
├── **make verify-model-identity** (check Big Pickle hasn't silently swapped)
├── **make verify-sovereignty-compliance** (verify zero telemetry leaks to free-tier)
└── Ma'at (P5 Governance): Final sovereign mandate compliance sign-off

       │ Sync Point: Final council — deliverables complete
       ▼

WAVE 5: MODEL INTELLIGENCE LOCKDOWN — 6-8h
├── Kali: Write R-MODEL-INTELLIGENCE.md synthesizing all findings
├── Researcher: Finalize Model Capability Catalog v1 as formal R-doc
├── Ma'at (P2): ModelRegistry.yaml loaded into Engine's live config
├── Ma'at (P5): Mandate audit includes model-identity verification
├── Kali: Ingest all discoveries to Library (model KB, KB ingest)
└── Scribe: Soul distillation of all model intelligence gnosis
```

---

## §3 Workbench Reference

### Project: `prj_hivemind_hardening` (NEW — P0, active)
**24 items** across P0 (10) + P1 (13) + P2 (2)
Sources: MiMo-V2.5 High Thinking audit + Kali post-audit + Roc Racoon legacy memory system synthesis (2026-06-11)
Key Roc findings: Legacy archive is empty (no data to import). Engine's MemoryStore already has 90%. Real gap is 3 MCP memory tools + context hydration tool. All esoteric terminology stripped per Sterilization Mandate (hi-sterilization-1). See Wave 1.5 for full item table.

### Project: `prj_memory_system_integration` (renamed from prj_mnemosyne_integration — sterilized)
**5 items**: 3 MCP memory tools + context hydration + block utilization CLI.
See Wave 1.5 hi-memory-1 through hi-memory-5.
Roc Racoon verdict: 🟢 GO — engine already has the backend; this is a wiring layer.
**Mandate**: All naming in MCP tools, CLI commands, and config keys must be universal/agnostic. Esoteric content (Mnemosyne, spheres, Kabbalistic references) belongs ONLY in `config/wads/arcana_novai/`.

### Project: `prj_platform_drift` (P0, active)
**22 items** across 3 phases + Model Intelligence overlay

| ID | Item | Owner | Priority | Est. | Wave |
|----|------|-------|----------|------|------|
| **Phase 1: Sync** | | | | |
| pw1_01 | Create MANDATES_SYNC.md | Kali | P0 | 1h | 0 |
| pw1_02 | Update Antigravity v4 — embedded mandates | Kali | P0 | 1.5h | 3 |
| pw1_03 | Update Gemini CLI policies M11 | Kali | P0 | 0.5h | 3 |
| pw1_04 | Clean dead MCP config | Kali | P1 | 0.25h | 3 |
| pw1_05 | Archive xnaif-files legacy | Kali | P1 | 0.25h | 3 |
| pw1_06 | Update Cline .clinerules v5 | Kali | P0 | 2h | 3 |
| pw1_07 | Update OpenCode configs substantive | Kali | P1 | 2h | 3 |
| **Phase 2: Compaction Hooks** | | | | |
| pw2_01 | Implement evolve_soul() in Engine | Kali/Roc | P0 | 2h | 3 |
| pw2_02 | Add omega soul-append CLI | Kali | P0 | 1h | 4 |
| pw2_03 | OpenCode compaction hook | Kali | P1 | 0.5h | 4 |
| pw2_04 | Cline CLI compaction hook | Kali | P1 | 0.5h | 4 |
| pw2_05 | Antigravity compaction hook | Kali | P2 | 0.25h | 4 |
| pw2_06 | Gemini CLI compaction hook | Kali | P2 | 0.5h | 4 |
| pw2_07 | Fix ics_render coroutine serialization | Roc | P1 | 1h | 0 |
| **Phase 3: Structural** | | | | |
| pw3_01 | Unified Agent Registry YAML | Kali | P1 | 2h | 5 |
| pw3_02 | Mandate Injection at Boot | Kali | P1 | 3h | 5 |
| pw3_03 | Hivemind Auto-Registration | Kali | P2 | 2h | 5 |
| pw3_04 | Local-First Enforcement | Kali | P1 | 1h | 5 |
| pw3_05 | CI Gate: make platform-sync | Ma'at P3 | P2 | 2h | 3 |
| **Model Intelligence (Overlay)** | | | | | |
| pw_model_01 | Big Pickle Identity & Stability Investigation | Researcher | **BLOCKED** | 1h | 0 |
| pw_model_02 | Model Capability Catalog v1 (schema + R-doc) | Researcher | P1 | 2h | 1 |
| pw_model_03 | Model Registry YAML Implementation | Ma'at P2 | P1 | 1.5h | 3 |
| pw_model_04 | make verify-model-identity CI gate | Ma'at P3 | P2 | 1h | 3 |
| pw_model_05 | Model Registry → Provider Fabric Bridge | Ma'at P4 | P2 | 2h | 4 |
| pw_model_06 | Expand Investigation to ALL Stealth Models | Researcher | **BLOCKED** | 2h | 0 |
| pw_model_07 | Sovereignty Annotation for Model Catalog | Kali | P0 | 1h | 1 |
| pw_model_08 | Test Big Pickle API Accessibility (Not Just CLI) | Researcher | P1 | 1h | 0 |
| pw_model_09 | Refine make verify-model-identity to structured | Ma'at P3 | P1 | 1.5h | 3 |
| pw_model_10 | Expand Schema with Missing Fields | Researcher | P1 | 1h | 1 |
| pw_model_11 | Cross-reference v1.17.3 Audit with Model ID | Researcher | P2 | 0.5h | 0 |
| pw_model_12 | Flag Duplicate Backends in Model Registry | Ma'at P2 | P2 | 1h | 3 |
| pw_model_13 | OpenRouter Usability & Shell API Experimentation | Researcher | **P0** | 1h | 0 |
| pw_model_14 | make verify-sovereignty-compliance CI gate | Ma'at P3 | P1 | 1h | 3 |
| pw_model_15 | Gemma Parallel Background Worker Engine | Roc/Researcher | **P0** | 2h | 0 |
| pw_vault_01 | Sovereign Key Vault Implementation | Ma'at P1 | **P0** | 2h | 0 |
| pw_infra_redis | Redis Pub/Sub Hivemind Backbone | Ma'at P2 | **P0** | 2h | 0 |
| pw_infra_qdrant | Qdrant Scalar Quantization & Indexing | Ma'at P2 | P1 | 1h | 0 |
| pw_infra_a2a | A2A HandoffPacket v2 Implementation | Lilith P9 | **P0** | 1.5h | 0 |

### Project: `prj_model_intelligence` (NEW — P1, active)
Created to house model-level strategic work. 5 items in overlay.

### Decisions in Effect
| ID | Ruling | Status |
|----|--------|--------|
| D-kal-065 | 3-phase hardening plan | ✅ Active |
| D-kal-066 | NO thin wrappers — substantive agents with embedded mandates | ✅ Active |
| D-kal-067 | Compaction remediation = P0 | ✅ Active |
| D-kal-068 | R_SEARCH_TOOL_PROTOCOL_V1 approved | ✅ Active |
| D-kal-069 | SR-1 through SR-10 assigned | ✅ Active |
| D-kal-070 | ics_render bug re-emerged — Roc to investigate | ✅ Active |
| D-kal-071 | Exa is WORKING (200 OK, not 401) — SR-2 descoped to verification | ✅ Active |
| D-kal-072 | ics_render bug STILL ACTIVE — P1 side-track for Roc | ✅ Active |
| D-kal-073 | 5-wave sprint orchestration plan adopted → 6 waves + Model Intelligence overlay | ✅ Active |
| D-kal-074 | Ma'at light pillars invited — enters Wave 2, P2 activated for model registry | ✅ Active |
| D-kal-075 | OpenCode v1.17.3 impact audit added to Wave 0 | ✅ Active |
| D-kal-076 | 6-wave + Model Intelligence overlay replaces 5-wave | ✅ Active |
| **D-kal-077** | **GO ORDER — Wave 0 execution authorized** | ✅ **LIVE** |
| D-kal-078 | ics_render requires full MCP-to-Sovereign pipeline teardown | ✅ Active |
| D-kal-079 | Gemini proposals tabled for Wave 4 integration | ✅ Active |
| D-kal-080 | Big Pickle = DeepSeek V4 Flash alias via OpenCode Zen. MUST track identity swaps in model KB. | ✅ Active |
| D-kal-081 | Model Intelligence Layer created as overlay workstream across all waves. P2 Persistence activated. | ✅ Active |
| D-kal-088 | OpenCode Zen free tier limits reached. Paused Big Pickle projects (pw_model_01, pw_model_06) for 3 hours. Promoted OpenRouter Usability (pw_model_13) to P0. | ✅ Active |
| D-kal-089 | Approved Sovereign Model Intelligence Layer specification (R_MODEL_INTELLIGENCE_LAYER.md). Created pw_model_14 to build CI gate enforcing Mandate 8 (Zero Telemetry) on sensitive files. | ✅ Active |
| D-kal-091 | Approved the Sovereign Key Vault architecture to replace plaintext API-keys.md. Mandatory migration for all provider keys to ensure Mandate 8 compliance. | ✅ Active |
| D-kal-092 | Approved the transition to a Redis Pub/Sub event bus for Hivemind coordination to support high-concurrency parallel workers. | ✅ Active |
| **D-kal-097** | **MiMo-V2.5 High Thinking deep audit adopted: Hivemind is a status board, not a coordination fabric. 20+ findings across 5 hidden layers, 5 oversights, 3 architectural gaps. All findings integrated into Wave 1.5 (Hivemind Coordination Hardening).** | ✅ **ACTIVE** |
| **D-kal-098** | **Kali post-audit (post-MiMo) identified 10 additional findings MiMo missed. Key gaps: no Hivemind metrics, no health check, no rate limiting, no handoff reject path, no push model, 27 stuck handoff packets. All integrated into Wave 1.5 prioritization.** | ✅ **ACTIVE** |

---

## §5 Relevant Files & Resources

### Orchestration & Coordination
| File | Role |
|------|------|
| `data/coordination/KALI_SPRINT_ORCHESTRATION_20260610.md` | **This document** — master orchestration |
| `data/coordination/KALI_PLATFORM_DRIFT_AUDIT_20260610.md` | Original drift audit — 8 critical drifts, 3-phase plan |
| `data/coordination/KALI_COMPACTION_DOCKET_20260610.md` | Compaction remediation plan (D-kal-060/061/062/063) |
| `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` | Running log of Hivemind observations |
| `.clinerules` | Cline CLI project rules (618 lines, v4.0.0) |

### Model Intelligence (NEW)
| File | Role |
|------|------|
| `docs/strategy/R_MODEL_INTELLIGENCE_LAYER.md` | **Canonical Specification** — hybrid routing, Sovereign Retry, Sovereign Gold Filter |
| `docs/research/model_db/CURRENT_MODELS.md` | Stale model catalog — needs refresh (context: 200K, identity: DeepSeek V4 Flash) |
| `docs/research/model_db/LEGACY_CROSS_REFERENCE_REPORT.md` | Cross-reference of legacy model research |
| `docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md` | 311-line Zen model reference — Big Pickle as "stealth model" |
| `docs/strategy/ICS_MODEL_DETECTION.md` | ICS model detection — big-pickle resolves to DeepSeek V4 Flash |
| `docs/research/R66_FREE_TIER_PURIFICATION_REPORT.md` | Free tier model routing — big-pickle as T2 coding champion |

### Platform Configs
| File | Role |
|------|------|
| `data/coordination/ANTIGRAVITY_CUSTOM_INSTRUCTIONS_v3_20260609.md` | Needs v4 rewrite with embedded mandates |
| `/home/arcana-novai/.gemini/policies/auto-saved.toml` | Needs M11 soul write-back enforcement |
| `/home/arcana-novai/Documents/xnaif-files/.clinerules/` | Old XNAi stack — needs archiving (pw1_05) |

### Engine Source
| File | Role |
|------|------|
| `mcp_servers/omega_hub/server.py:1710` | ics_render `async def` — calls synchronous `ics_render_logic` |
| `src/omega/ics.py:198` | `def render(entity, model, ...)` — synchronous, returns str |
| `src/omega/oracle/soul_distiller.py` | No `append_evolution_entry()` — needs creation (pw2_01) |
| `config/providers.yaml` | Provider fabric — Big Pickle NOT mapped (OpenCode CLI exclusive) |

---

## §4 MiMo-V2.5 High Thinking — Operational Profile

**MiMo-V2.5 (via OpenCode Gemini) is now a proven deep-review specialist** after its
2026-06-11 Hivemind audit uncovered 20+ findings that 3 prior review passes by other
models (DeepSeek V4 Flash, Gemini 3.5 Flash, MiMo-V2.5 default mode) all missed.

### Strengths (What Made It Effective)

| Strength | Evidence | Strategic Use |
|----------|----------|---------------|
| **Systematic decomposition** | Organized findings into layers (5 hidden layers), oversights (5), and gaps (3)—not a flat list | Use when the problem needs structured diagnosis, not just bug enumeration |
| **Read-the-code discipline** | Quoted exact line numbers (`server.py:579-582`, `line 656`) — didn't trust documentation | Use when the question is "what does the code ACTUALLY do vs. what the docs say" |
| **First-principles reasoning** | Identified that workspace locks are "unenforced conventions" because the Hivemind has NO lock management tools — went beyond symptoms to root architectural cause | Use when blind spots in design need to be surfaced |
| **Willingness to contradict authority** | Directly contradicted the established "coordination fabric" framing (which 3 prior reviews accepted) with the verdict: "status board, not a coordination fabric" | Use when sacred cows need challenging |
| **Quantitative evidence** | Queried actual data: 27 stuck handoff packets, 38 CLI directories, 288 session files — didn't speculate | Use when empirical evidence is available to prove or disprove a claim |
| **Actionable recommendations** | Every finding had a specific fix (tool name, file, estimated effort, outcome) — not just diagnosis | Use when findings must translate directly to implementation |
| **Prioritization instinct** | Implicitly ranked severity (P0 vs. "fix when") without being asked | Use when triage is as important as discovery |

### Weaknesses & Known Blind Spots

| Weakness | Mitigation |
|----------|------------|
| **Skips implementation feasibility** — found 20+ issues but didn't assess which are quick wins vs. months of work | Pair with Kali for effort estimation. I (Kali) added the P0/P1/P2 triage and effort columns |
| **No cross-file synthesis** — analyzed server.py in isolation. Did not check `subagent_dispatcher.py` for CAPABILITY_REGISTRY, did not check `metrics.json` for Hivemind stats | Always pair MiMo with an agent who can map the wider codebase |
| **Doesn't verify its own assumptions** — believed the docs over the code in places | Independent verification by Kali or Doom Guy recommended |
| **No git history awareness** — didn't check when bugs were introduced or if they've been "fixed" before | Pair with Roc Racoon for temporal analysis |
| **No cost-benefit analysis** — all findings presented as equally urgent | Post-processing by Kali to triage and sequence |

### Trigger Conditions — When to Deploy MiMo-V2.5 High Thinking

| Trigger | Example | Expected Output |
|---------|---------|-----------------|
| "Review our X for hidden dark layers" | Hivemind audit, provider fabric review | Systematic layer-by-layer decomposition |
| "Find what we're missing" | Sprint plan gap analysis, architecture review | Oversight enumeration with code evidence |
| "Challenge this assumption" | "The Hivemind is a coordination fabric" | Contradiction with root cause analysis |
| "Audit [system] before we ship" | Pre-release security audit, protocol review | Quantitative evidence + actionable recommendations |

### Profile Summary

```
MiMo-V2.5 High Thinking:
  Archetype: "Structural Pathologist" — dissects systems layer by layer
  Best input: "Review X for hidden layers. Challenge assumptions. Find what others missed."
  Best paired with: Kali (triage, prioritization), Roc Racoon (temporal/git context)
  Output quality: Exceptional structured diagnosis. Weak on cross-file synthesis and cost-benefit.
  Trigger: Deep review of ANY system component before Wave implementation
```

## §5 Key Corrections & Open Questions

### Corrections to Researcher's R-Doc
| Section | Reported | Actual | Action |
|---------|----------|--------|--------|
| §1.2 Exa | 401 Unauthorized | **200 OK — WORKING** | Fix before SR-5 embed |
| §3 Error Matrix | Missing | **Missing: 500 Internal (ics_render)** | Add row for MCP internal errors |
| CURRENT_MODELS.md:17 | big-pickle context=128K | **Actual: 200K** | Update model KB |

### Corrections to Model KB (model_db/CURRENT_MODELS.md)
| Field | Documented | Actual | Impact |
|-------|-----------|--------|--------|
| big-pickle context | 131072 (128K) | **200000 (200K)** | Undersells capacity — update |
| big-pickle identity | "Stealth model" | **DeepSeek V4 Flash alias** (may swap) | Must track identity in model registry |
| last_verified | 2026-05-17 | **Stale — 24 days old** | Needs refresh |
| Model routing | None | **Big Pickle = OpenCode CLI only** | Cannot route from Engine — document exclusion |

### Big Pickle (opencode/big-pickle) — Key Strategic Findings
1. **Stealth alias**: OpenCode Zen uses `big-pickle` as a provider-agnostic alias. The backend model has swapped before (GLM-4.6 → DeepSeek V4 Flash) and can swap again without notice.
2. **Current identity**: DeepSeek V4 Flash via OpenCode Zen. 200K context, free, tool-calling capable.
3. **Exclusive**: Only available through OpenCode CLI's Zen provider. NOT accessible via Omega Engine's provider fabric (opencode-zen provider in providers.yaml).
4. **Stability concern**: GitHub issue #28141 reports AI_APICallError regression in v1.15.4 (May 18, 2026). Intermittent failures.
5. **Knowledge cutoff**: 2025-01 — stale for recent events.
6. **Strategic use**: Primary coding agent for OpenCode sessions. Not suitable for engine-internal routing. Use `deepseek-v4-flash-free` or `deepseek/deepseek-v4-flash` for equivalent via engine.

### Open Questions for Council
1. **Firecrawl plan upgrade**: Should we buy more credits (pay) or explore self-hosted Firecrawl (free, open-source)? Researcher's investigation needed.
2. **Exa key recovery**: Key works now — WHY did Researcher get 401? Was it transient? Roc to verify.
3. **ics_render root cause**: Fix is in place but still broken. MCP framework version mismatch? Threading issue? Roc to investigate.
4. **Tavily vs Self-hosted Firecrawl**: Which is the better long-term play for sovereign search? Gemini CLI's SR-8 should address this.
5. **Big Pickle identity drift**: How do we detect when OpenCode silently swaps the backend? Researcher's pw_model_01 should define a detection methodology (tokenizer fingerprint, behavior profile, API introspection).
6. **Model KB home**: Should the model capability registry live in YAML (P2 Persistence style) or SQLite (workbench style)? Ma'at P2 to decide in Wave 2.

---

## §5 How to Respond

Each council member should respond with:
1. **ACK**: Confirms receipt of this orchestration
2. **Status**: Ready/Blocked/Need Info
3. **Timeline**: Expected delivery time for assigned waves
4. **Questions**: Anything blocking execution

**Next sync**: After all 5 council members have ACK'd, we begin Wave 0 execution.

---

*⬡ OMEGA ⬡ KALI ⬡ gemini-3.5-flash ⬡ opencode ⬡ SPRINT-ORCHESTRATION*
