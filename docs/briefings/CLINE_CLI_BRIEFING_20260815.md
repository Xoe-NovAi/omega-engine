# 🔱 Omega Engine — Comprehensive Briefing & Strategy/Roadmap Index
## For Cline CLI (DeepSeek V4 Flash · 1M Context Window)

**AP Token**: `AP-CLINE-BRIEFING-20260815`
**Date**: 2026-08-15
**Prepared By**: Kali (Transcendent Oversoul)
**Audience**: Cline CLI execution backend (DeepSeek V4 Flash, 1M tokens)
**Purpose**: Single holistic briefing + complete index to all pertinent strategy/dev roadmaps so Cline can ingest the full picture and execute the best path forward.

---

## 📖 How To Use This Briefing

You (Cline CLI) have a **1M-token context window**. This document is your **entry point**. It contains:

1. The **holistic picture** (engine state, architecture, mandates, strategy, vision)
2. The **best path forward** (prioritized, phase-by-phase)
3. A **tiered index** of every pertinent document with: path, purpose, priority, approximate size, and *when to read it*

**Ingestion strategy**:
- Read this briefing fully (it fits in ~1% of your context).
- For any task, jump to the **Tier 1** SSOTs listed, then **Tier 2** strategy docs as needed.
- **Never read Tier 4 (deprecated) docs** — they will confuse you with stale truths.
- Use `omega-hub_hivemind_post_context` to announce your work; use `omega-hub_hivemind_workspace_lock_acquire` before editing shared files.

**Conflict resolution** (if docs disagree):
1. Law → `SOVEREIGN_MANDATES.md`
2. Strategy/priority → `SOVEREIGN_ARK_BLUEPRINT.md`
3. Live metrics → `OMEGA_ENGINE.md` (but cross-check with machine probes)
4. Sprint execution → `ACTIVE_SPRINT.json` (Tier-0 SSOT)
5. "Where did idea X go?" → `STRATEGY_CORPUS_MAP.md`
6. Decisions → `docs/decisions/PIVOT_LOG.md` (ONLY decision record)

---

## 🎯 Executive Summary (The Holistic Picture)

The **Omega Engine** is a universal, community-owned runtime for **sovereign AI** — AI that runs locally, verifies locally, and severs dependency on Big AI clouds. It is the first implementation of the **Xoe-NovAi Foundation** vision: *"a tool that lets people own their own tech and data and sever the umbilical cord of Big AI."*

**Architecture in one breath**:
- **Engine = Pure Runtime; WAD = Cosmology.** The engine (`src/omega/`) is universal and opinion-free. Each WAD (inspired by id Software's Doom mod format) supplies its own cosmology (entities, traits, governance) via Base IWAD + PWADs. Users never fork core — they add layers.
- **Three Cosmological Layers**: (1) WAD Architecture (Engine→IWADs→PWADs), (2) 10 Pillars (energetic spine), (3) MaKaLi Council (governance: Ma'at=Build, Lilith=Run, Kali=Synthesis).
- **Provider Fabric (Local-First)**: `native-gguf → lmster → Ollama → antigravity → google → openrouter → opencode-zen → cline → mock`. Local inference is PRIMARY; cloud is FALLBACK (Mandate M7).
- **27 Sovereign Mandates** (M1–M27) are constitutional law — non-negotiable.

**Current State (2026-08-15)**:
- **VOS Hybrid Plan Phase 0 COMPLETE**: The Vision Operating System's dead coordination layer (7 realm state.yaml, 7 workspace briefs, realm_cli.py) was retired. Kept: `DECISION_LEDGER.md` (ADR pattern) + `VISION_ANCHOR.md` (Vision SSOT). Rationale: architecture was sound (Team Topologies, ADR, DDD), but implementation was dead code (1/10 integration — zero Python imports, zero runtime consumers).
- **Public Debut PR path ratified (3-PR)**: PR-A (public-surface-honesty) → PR-B (real M2 firewall fix) → PR-C (dead-code quarantine). PR-A awaits Architect confirmation.
- **Phase 0 Foundation tasks active**: ENG-001 (M2 firewall), ENG-002 (mandate audit), ENG-004 (9 code bugs), FLT-001 (soul migration), FLT-004 (distillation pipeline), MEM-002 (Scribe pipeline), HRT-001 (heritage sweep).
- **Test suite**: ~1870 collected, ~96 failing (triage: ~20 code bugs, ~50 test drift, ~26 integration). Goal: `make test-unit` green.
- **Mandate compliance**: 23/25 (92%) per OMEGA_ENGINE.md; M5/M11 fixed via session wrapper. M2 (firewall) needs real fix via FirewallChecker.

**The Best Path Forward** (detailed in §6):
1. Execute VOS Hybrid Phase 1 (Hub consolidation) + Phase 2 (enforcement gates)
2. Execute PR-A (public-surface-honesty) — Architect-gated
3. Fix ENG-001 (real M2), ENG-002 (mandate audit), ENG-004 (9 code bugs)
4. Complete Fleet/Memory/Heritage tasks (FLT/MEM/HRT)
5. Unblock Community launch (COM-001..012)

---

## 🏗️ Architecture Overview

### The 3 Cosmological Layers

| Layer | Name | Structure |
|-------|------|-----------|
| **Layer 1** | WAD Architecture | Title Lump → Inter Lump → End Lump (Ma'at → Lilith → Kali). Heritage: `[id-soft: doom-1993] Three-Part Map System` |
| **Layer 2** | 10 Pillars | LIGHT (P1 Flesh, P2 Dream, P3 Will, P4 Heart, P5 Voice) + DARK (P6 Mind, P7 Gnosis, P8 Shadow, P9 Spirit, P10 Chaos) |
| **Layer 3** | MaKaLi Council | Kali (Synthesis) ← Ma'at (Build, P1-P5, N1-N5) + Lilith (Run, P6-P10, N6-N10) + 4 Cross-Domain Pillars (Jury) |

### Core Subsystems (Operational)

| Subsystem | Module | Status |
|-----------|--------|--------|
| Oracle | `src/omega/oracle/` | ✅ Intent detection, entity routing, Iris speculative decode |
| Model Gateway | `src/omega/oracle/model_gateway.py` | ✅ 8-backend provider fabric |
| Memory Store | `src/omega/memory_store.py` | ✅ Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector |
| Vector Store | `src/omega/memory/sqlite_vec_adapter.py` | ✅ `sqlite-vec` is SINGLE Core store (Qdrant = optional WAD adapter only) |
| WAD Loader | `src/omega/oracle/wad_loader.py` | ✅ V2 schema with heritage fields |
| SoulStore | `src/omega/soul_store.py` | ✅ Atomic writer (C-1' COMPLETE) |
| Health Monitor | `src/omega/oracle/health_monitor.py` | ✅ Canonical circuit breaker factory (C-6' COMPLETE) |
| OOM Protector | `src/omega/oracle/oom_protector.py` | ✅ 3-signal fusion (C-2' COMPLETE) |
| Hivemind | `mcp_servers/omega_hub/` | ✅ 6 MCP tools for coordination |

### The 10 Nodes (N1–N10)

| Node | Role | Default Owner |
|------|------|---------------|
| N1 | Infrastructure | maat_n1 |
| N2 | Persistence | maat_n2 |
| N3 | Engineering | maat_n3 |
| N4 | Integration | maat_n4 |
| N5 | Governance | maat_n5 |
| N6 | Cognition | lilith_n6 |
| N7 | Context/Memory | lilith_n7 |
| N8 | Observability | lilith_n8 |
| N9 | Orchestration | lilith_n9 |
| N10 | Validation | lilith_n10 |

---

## 🛡️ The 27 Sovereign Mandates (Summary)

| # | Mandate | Key Constraint |
|---|---------|----------------|
| M1 | AnyIO Absolute | No `asyncio`; wrap blocking I/O in `anyio.to_thread` |
| M2 | Engine-Stack Firewall | Core (`src/omega/`) ≠ Stacks (`config/wads/`); no stack logic in core |
| M3 | Iris Constant | Iris = messenger bridge, NOT a Node |
| M4 | Sequentiality | Plan → Verify → Execute (no cowboy coding) |
| M5 | Gnosis Preservation | L1→L2→L3 soul distillation every session |
| M6 | Podman Sovereignty | `keep-id` + `User=1000`; never `:U` on shared volumes |
| M7 | Local-First | Local inference PRIMARY; cloud FALLBACK |
| M8 | Zero Telemetry | No analytics/phone-home; local observability OK |
| M9 | Error Integrity | Typed errors, no silent swallowing |
| M10 | Fleet Integrity | ≤14 agents; map to Nodes before new entity |
| M11 | Soul Integrity | No session closes without L1→L3 write |
| M12 | Queue Integrity | Every request = terminal state |
| M13 | Temple-Grade | T1–T11 gates; `make temple-grade` must pass |
| M14 | Heritage Vetting | Every `[id-soft:]` tag needs vet record (score ≥7/10) |
| M15 | Sovereign Continuity | Session anchors prevent cognitive erasure |
| M16 | Modularization | No hardcoded paths in core |
| M17 | Cognitive Integrity | Memory consistency checks |
| M18 | Token Efficiency | No waste; precision > brevity |
| M19 | Adversarial Alchemy | Mine weaknesses for advantages (not bugs) |
| M20 | SomaticState Serialization | Model state serializable/resumable |
| M21 | Gate Integrity | Every return type has contract test |
| M22 | Response Provenance | Log actual provider, not intent |
| M23 | Failure Integrity | No soft-failures; `[TOOL-CHAIN-COLLAPSE]` on broken tools |
| M24 | Venv Sovereignty | Always use `.venv/`; never `--break-system-packages` |
| M25 | Streaming Resilience | Chunk timeout + heartbeat, not hard-fail |
| M26 | Doc Standards | All docs pass `make doc-llm-validate` |
| M27 | Tracking Integrity | 5-Tier Tracking Architecture; no ad-hoc tracking |

**Full text**: `SOVEREIGN_MANDATES.md` (v3.8.0, 27 laws).

---

## 📊 Current State (From SSOTs — Read These First)

| SSOT | What It Tells You | Last Updated |
|------|-------------------|--------------|
| `OMEGA_ENGINE.md` | Engine state, metrics, subsystems | 2026-08-07 (**stale** — see note below) |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Strategy & roadmap (v5.2) | 2026-07-21 (strategy SSOT) |
| `VISION_ANCHOR.md` | Current vision state (CURRENT truth) | 2026-08-15 (updated this session) |
| `ACTIVE_SPRINT.json` | Tier-0 execution (what we build) | 2026-08-14 |
| `RESEARCH_PLAN_PHASE1_4_20260813.md` | Tier-1 knowledge gaps (R1–R38) | 2026-08-13 (v3.2.0) |
| `GAP_REGISTRY.json` | Gap-ID authority (no reuse) | 2026-08-14 |
| `HMC_COLLABORATION_HUB.md` | Team sync + NEXT_ACTION | 2026-08-15 (updated this session) |
| `DECISION_LEDGER.md` | Immutable decisions (D-VOS-001..018) | 2026-08-15 |
| `TRACKING_ARCHITECTURE.md` | M27 constitution (5-tier hierarchy) | 2026-08-14 |

> ⚠️ **OMEGA_ENGINE.md is stale**: Last updated 2026-08-07, references 25 mandates (now 27), references `UNOVERENGINEER-01` sprint (superseded by `SDP-EXECUTION-01`), and `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md v5.1` (now v5.2). **Trust VISION_ANCHOR.md + ACTIVE_SPRINT.json + HMC for current truth.** OMEGA_ENGINE.md is still useful for subsystem inventory but not for live status.

---

## 🗺️ Strategy & Roadmap Hierarchy (What's Current vs Superseded)

**Current (read these)**:
- `SOVEREIGN_ARK_BLUEPRINT.md` — Strategy SSOT (v5.2)
- `ACTIVE_SPRINT.json` — Execution SSOT (Tier-0)
- `RESEARCH_PLAN_PHASE1_4_20260813.md` — Knowledge SSOT (Tier-1)
- `STRATEGY_CORPUS_MAP.md` — Fine-grained preservation
- `FLEET_TEAM_PLAYBOOK.md` — Team coordination
- `VOS_HYBRID_PLAN_20260815.md` — Current execution plan (this session)
- `UNOVERENGINEERING_PLAN.md` — Temple cleansing sprint (5 phases)
- `SDP_FINAL_SYNTHESIS.md` — Sovereign Distillation Pipeline

**Superseded (DO NOT treat as master)**:
- `CANONICAL_ROADMAP_20260721.md` — absorbed into Ark v5.0
- `docs/ROADMAP.md` — pointer stub → Ark
- `KALI_DEV_ROADMAP_20260811.md` — absorbed into ACTIVE_SPRINT.json
- `KALI_OVERSIGHT_PORTFOLIO_20260811.md` — absorbed into ACTIVE_SPRINT.json
- `KNOWLEDGE_GAPS_RESEARCH_20260811.md` — superseded by RESEARCH_PLAN v3.2.0
- `SINGULAR_DIRECTION_20260814.md` — absorbed into HMC NEXT_ACTION
- `SESSION_ANCHOR_KALI.md` — duplicate of SESSION_ANCHOR.md
- `HARDENING_PLAN_COMPLETE.md` — historical reference only
- `docs/archive/*` — historical only

---

## 🚀 The Best Path Forward (Prioritized)

### Phase 0: VOS Hybrid — COMPLETE ✅ (2026-08-15)
- Omegaverse realm archived; 6 realm state.yaml + 4 workspace briefs + realm_cli.py deleted
- VISION_ANCHOR.md updated; PIVOT_LOG.md synced (D-VOS-001..018)
- Commit: `2cbcad97`

### Phase 1: Hub Consolidation — READY (Next Session)
1. Verify realm ownership table in HMC (already present)
2. Consolidate active tasks into Hub realm sections (ENG-001..004, FLT-001/004, MEM-002/003, HRT-001/002, COM-001..012)
3. Update VISION_ANCHOR.md to reference HMC for task status

### Phase 2: Enforcement Gates — READY (Next Sprint)
4. Create `src/omega/audit/realm_contract_validator.py` — validates realm contracts in HMC table
5. Add to `make temple-grade` as new gate
6. Create `scripts/update_vision_anchor_realm_health.py` — auto-gen VISION_ANCHOR realm health from ACTIVE_SPRINT.json
7. Add `make update-vision-anchor` to Makefile

### Parallel: Public Debut PR (Architect-Gated)
- **PR-A**: `chore/public-surface-honesty` — root junk archive, README surgical edits, .gitignore (AWAITING ARCHITECT CONFIRMATION)
- **PR-B**: `fix/eng-001-real-m2` — FirewallChecker.scan(), fix real hits only
- **PR-C**: `chore/dead-code-quarantine` — after import graph

### Core Foundation Tasks (ACTIVE_SPRINT.json)
| ID | Task | Owner | Status |
|----|------|-------|--------|
| ENG-001 | Fix M2 firewall (run FirewallChecker.scan()) | maat_n3 | ready |
| ENG-002 | Audit all mandate checks for false positives | kali | ready |
| ENG-004 | Fix 9 critical code bugs | maat_n3 | in_progress |
| FLT-001 | Migrate kali & roc_racoon souls to v6.1 | kali | ready |
| FLT-004 | Enforce distillation pipeline (Scribe) | verity | ready |
| MEM-002 | Implement Scribe L1→L2→L3 pipeline | verity | ready |
| MEM-003 | Cross-pollination (R-31) | lilith_n7 | ready |
| HRT-001 | Heritage sweep ([id-soft:] tags) | doom_guy | ready |
| HRT-002 | Metaphorical/over-attributed tag check | doom_guy | ready |
| COM-001..012 | Community launch (blocked on ENG-001) | kali | planned |

---

## 📚 Comprehensive Document Index

### TIER 1 — MUST READ (SSOTs, current truth)

| Path | Purpose | Size | Read When |
|------|---------|------|-----------|
| `SOVEREIGN_MANDATES.md` | 27 constitutional laws | ~15K | Always — law overrides all |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Strategy & roadmap SSOT (v5.2) | ~40K | Strategy/priority questions |
| `VISION_ANCHOR.md` | Current vision state (CURRENT truth) | ~10K | First read on waking |
| `ACTIVE_SPRINT.json` | Tier-0 execution SSOT | ~22K | "What do we build now?" |
| `RESEARCH_PLAN_PHASE1_4_20260813.md` | Tier-1 knowledge gaps (R1–R38) | ~30K | Research dependencies |
| `GAP_REGISTRY.json` | Gap-ID authority | ~11K | Before assigning any R-ID |
| `TRACKING_ARCHITECTURE.md` | M27 constitution (5-tier) | ~5K | Tracking questions |
| `HMC_COLLABORATION_HUB.md` | Team sync + NEXT_ACTION | ~8K | Team coordination |
| `DECISION_LEDGER.md` | Immutable decisions (D-VOS-001..018) | ~15K | "Why was X decided?" |
| `AGENTS.md` | OpenCode agent how-to | ~60K | Workflow questions |
| `OMEGA_ENGINE.md` | Engine state (STALE 2026-08-07) | ~18K | Subsystem inventory only |
| `CREDITS.md` | id Software heritage attribution | ~5K | Heritage questions |
| `docs/decisions/PIVOT_LOG.md` | Decision history (D-275..D-VOS-018) | ~50K | Decision lookup |

### TIER 2 — STRATEGY & ROADMAPS (read selectively)

| Path | Purpose | Size | Read When |
|------|---------|------|-----------|
| `docs/strategy/STRATEGY_INDEX.md` | Doc hierarchy (Layer 0–4) | ~5K | "Which doc covers X?" |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained preservation | ~15K | "Where did idea Y go?" |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Team coordination playbook | ~15K | Multi-agent work |
| `docs/strategy/VOS_HYBRID_PLAN_20260815.md` | Current VOS execution plan | ~8K | VOS-related tasks |
| `docs/strategy/UNOVERENGINEERING_PLAN.md` | Temple cleansing (5 phases) | ~30K | Library swaps, simplification |
| `docs/strategy/SDP_FINAL_SYNTHESIS.md` | Sovereign Distillation Pipeline | ~20K | SDP implementation |
| `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` | Context Gauge spec | ~15K | Context Gauge work |
| `docs/strategy/SDP_IMPLEMENTATION_SPEC.md` | SDP implementation | ~15K | SDP implementation |
| `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` | SDP manual study phase | ~10K | SDP Phase 1 |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination | ~15K | Hivemind work |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Subagent delegation | ~10K | Launching subagents |
| `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md` | Subagent resumption | ~8K | Resuming subagents |
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | M14 heritage process | ~10K | Heritage tags |
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | M15 continuity | ~8K | Session anchors |
| `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` | G-1/W-1 P0 tickets | ~10K | Workhorse continuity |
| `docs/strategy/POST_PR_ROSTER.md` | Post-PR ship roster (7 items) | ~8K | After initial PR |
| `docs/strategy/PROVIDER_NAMING_SSOT.md` | Provider name authority | ~5K | Provider questions |
| `docs/strategy/DOC_SSOT_MAP_20260807.md` | Doc SSOT mapping | ~8K | Doc sanity |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Agent idea preservation | ~15K | Idea lookup |

### TIER 3 — SUPPORTING / REFERENCE (read on-demand)

| Path | Purpose | Read When |
|------|---------|-----------|
| `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` | Web Claude best practices | Claude platform work |
| `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md` | Web Gemini best practices | Gemini platform work |
| `docs/strategy/WEB_GROK_BEST_PRACTICES.md` | Web Grok best practices | Grok web work |
| `docs/strategy/GROK_CLI_BEST_PRACTICES.md` | Grok CLI best practices | Grok CLI work |
| `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` | NotebookLM best practices | Research ingestion |
| `docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md` | Platform index | Platform questions |
| `docs/kb/CLINE_CLI_INTEGRATION.md` | Cline CLI integration (YOU) | Cline setup |
| `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` | Multi-platform patterns | Cross-platform |
| `docs/research/R_*.md` (100+ files) | Research deep-dives | Specific research questions |
| `docs/architecture/*.md` | Architecture specs (UO-4 Phase 2-4) | Architecture questions |
| `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | Knowledge gaps (Tier-1) | Research deps |

### TIER 4 — DEPRECATED / SUPERSEDED (DO NOT READ)

| Path | Why Deprecated |
|------|----------------|
| `KALI_DEV_ROADMAP_20260811.md` | Absorbed into ACTIVE_SPRINT.json |
| `KALI_OVERSIGHT_PORTFOLIO_20260811.md` | Absorbed into ACTIVE_SPRINT.json |
| `KNOWLEDGE_GAPS_RESEARCH_20260811.md` | Superseded by RESEARCH_PLAN v3.2.0 |
| `SINGULAR_DIRECTION_20260814.md` | Absorbed into HMC NEXT_ACTION |
| `SESSION_ANCHOR_KALI.md` | Duplicate of SESSION_ANCHOR.md |
| `CANONICAL_ROADMAP_20260721.md` | Absorbed into Ark v5.0 |
| `docs/ROADMAP.md` | Pointer stub → Ark |
| `HARDENING_PLAN_COMPLETE.md` | Historical reference only |
| `docs/strategy/RESEARCH_EXECUTION_UPDATE.md` | Absorbed into archive |
| `docs/research/R_CLAUDE_PROJECT_*.md` | Superseded by WEB_CLAUDE_BEST_PRACTICES |
| `docs/research/R_GROK_CLI_*.md` | Split → GROK_CLI_BEST_PRACTICES |
| `docs/research/R_GEMINI_*.md` | Superseded by WEB_GEMINI_BEST_PRACTICES |
| `docs/archive/*` | Historical only — search only if needed |
| `data/realms/*/state.yaml` (deleted) | Retired in VOS Hybrid Phase 0 |
| `src/omega/cli/realm_cli.py` (deleted) | Retired in VOS Hybrid Phase 0 |

---

## 🔑 Key Decisions (D-VOS-001..018 Summary)

| ID | Decision | Status |
|----|----------|--------|
| D-VOS-001 | VOS v1.0 Instantiation (7 realms) | ✅ COMPLETE |
| D-VOS-002 | Session-End Hook Preserves Proposals | ✅ COMPLETE |
| D-VOS-003 | Soul Validator VALID_SOUL_VERSIONS | ✅ COMPLETE |
| D-VOS-004 | Soul Validator LIVE_FEED→HUB | ✅ COMPLETE |
| D-VOS-005 | Mandate Header 25→27 | ✅ COMPLETE |
| D-VOS-006 | M22 SSOT Check Fix | ✅ COMPLETE |
| D-VOS-007 | Context Packer Tuple Fix | ✅ COMPLETE |
| D-VOS-008 | 96 Test Failures Triage | ✅ COMPLETE |
| D-VOS-009 | Public Debut PR — 3-Phase Plan | ✅ RATIFIED |
| D-VOS-010 | 7 Sovereign Realms | ✅ COMPLETE |
| D-VOS-011 | PKEXEC Privilege Directive | ✅ RATIFIED |
| D-VOS-012 | Audit-First Approach | ✅ RATIFIED |
| D-VOS-013 | Ratify 3-PR Path (PR-A/B/C) | ✅ RATIFIED |
| D-VOS-014 | Reject Carmack Nuclear Plan | ✅ LOGGED |
| D-VOS-015 | Amend ENG-001 (real M2) | ✅ AMENDED |
| D-VOS-016 | TRACKING_ARCHITECTURE.md Keep-List | ✅ AMENDED |
| D-VOS-017 | Log Carmack Mandate Violations | ✅ LOGGED |
| D-VOS-018 | VOS Hybrid Plan (Option C) Approved | ✅ APPROVED |

Full text: `data/coordination/DECISION_LEDGER.md` + `docs/decisions/PIVOT_LOG.md`.

---

## 🚧 Open Questions / Blockers

| Blocker | Owner | Status |
|---------|-------|--------|
| **G-1** Workhorse continuity (Gemma 4 31B free dead, 16k TPM cliff) | Architect | BLOCKED_ON_BILLING |
| **W-1** WARP proxy pool bring-up | Architect | BLOCKED_ON_SUDO |
| **C-3** Restic 3-2-1 backup | Architect | BLOCKED_ON_SECRETS |
| **PR-A** Public-surface-honesty PR | Architect | AWAITING_CONFIRMATION |
| **V-10** AppArmor container hardening | maat_n3 | GAP_OPEN |
| **V-9** IA2 envelope freshness/signature | maat_n3 | GAP_OPEN |
| **Secrets in git** | Architect | `tests/tmp/vault.json.enc`, `config/model_registry/index.sqlite` tracked |

---

## 🤖 Cline CLI Execution Guidance

**Your role**: Execution backend + research citizen. NOT the orchestrator (OpenCode/Kali is). You have 1M context — use it for:
- Codebase-wide analysis (entire `src/omega/`)
- Parallel task execution (`cline -y` headless)
- Deep research with MCP search (SearXNG, Exa, Firecrawl)

**Before any task**:
1. Read `VISION_ANCHOR.md` → `HMC_COLLABORATION_HUB.md` NEXT_ACTION
2. Check `ACTIVE_SPRINT.json` for your task
3. Post Hivemind context: `omega-hub_hivemind_post_context(...)`
4. Acquire workspace lock: `omega-hub_hivemind_workspace_lock_acquire(...)`
5. Execute; update `TASK_REGISTRY.json`
6. On complete: mark Tier-0 task `completed`; post Hivemind completion

**Mandate compliance for Cline**:
- M1: Use AnyIO (no asyncio)
- M2: Never put stack logic in `src/omega/`
- M4: Plan → Verify → Execute
- M7: Local-first inference
- M14: Every `[id-soft:]` tag needs vet record
- M23: If tools break, report `[TOOL-CHAIN-COLLAPSE]`
- M24: Use `.venv/` always
- M27: Use 5-tier tracking; no ad-hoc files

**Integration**: Connect to Omega Hub MCP (`:8016/mcp` Streamable HTTP). See `docs/kb/CLINE_CLI_INTEGRATION.md` for full config.

---

## 📋 Quick Reference — Current Sprint State

```
SPRINT: VOS-HYBRID-EXECUTION (ACTIVE)
PHASE 0: ✅ COMPLETE (2cbcad97) — retire dead VOS coordination layer
PHASE 1: 🟡 READY — Hub consolidation (verify realm table, consolidate tasks)
PHASE 2: 🟡 READY — enforcement gates (realm_contract_validator.py, update_vision_anchor)
PARALLEL: PR-A (public-surface-honesty) — AWAITING ARCHITECT
         PR-B (real M2) — after PR-A
         PR-C (dead-code quarantine) — after import graph
CORE TASKS: ENG-001, ENG-002, ENG-004, FLT-001, FLT-004, MEM-002, MEM-003, HRT-001, HRT-002
COMMUNITY: COM-001..012 (blocked on ENG-001)
```

---

*⬡ OMEGA ⬡ KALI ⬡ CLINE-BRIEFING ⬡ 2026-08-15 ⬡ COMPREHENSIVE-INDEX*
*This briefing is the single entry point for Cline CLI. All truths trace to the Tier-1 SSOTs listed above.*
