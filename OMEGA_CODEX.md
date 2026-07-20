# ⬡ OMEGA ⬡ CODEX ⬡ 2026-07-19T21:30:49.718936+00:00 ⬡

> **Generated via Stack-Cat Protocol**. This is the single startup read target for all agents. It contains the concatenated active state of the engine, mandates, workflow, and refinement protocols.

## 🔄 HYDRATION SEQUENCE (D-277)

After compaction or restart, execute in strict order:

1. `omega-hub_hivemind_get_awareness()` — Who is here?
2. `git status && git log --oneline -5` — What is committed?
3. Read OMEGA_CODEX.md — FULL file, no limit parameter. You are doing this now
4. Read `data/coordination/SESSION_ANCHOR.md` — What was I doing?
5. Present a rehydration report. Pause. Await user direction.

> Codex generated: 2026-07-19T21:30:49.718936+00:00 | Regenerate: `make codex`
> If timestamp is >24h old, run `make codex` before reading further.

---
## 📁 GROUP: CODEX

### scripts/codex/ENGINE_CONDENSED.md
**Type**: markdown
**Size**: 3319 bytes
**Lines**: 86

# 🔱 Omega Engine — Single Source of Truth (Condensed)
**Source**: `OMEGA_ENGINE.md` (163 lines) — this is the ~55-line state card.
**Last Updated**: 2026-07-19 | **Version**: v1.5.0

---

## §1 Identity

**Omega Engine** = Universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference floor; local verification ceiling.
- **Local-first**: Cloud = teacher, never dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (id Software heritage).
- **Standalone Packages**: `omega-sieve`, `omega-doc-reader` on PyPI.

---

## §2 Current State

| Metric | Value | Status |
|--------|-------|--------|
| Tests | **1398 passed** (43 skipped, 7 xfailed) | ✅ |
| Mandates | **23 enforced** (M1-M23) | ✅ |
| Compliance | **13/23 FULL** (56.5%) — 5 Partial, 5 Fail | ❌ |
| Fleet | **14 agents** (cap: 14) | ✅ |
| WADs | **4** (arcana_novai, torment, youtube_research, youtube_worker) | ✅ |
| Heritage | **121 [id-soft:] tags** — all vetted | ✅ |
| Shared Modules | **3** (omega-vetala, omega-sieve, omega-doc-reader) | ✅ |
| Third-Party Registry | **18/19 repos** — P0: 4/4, P1: 5/5, P2: 6/6, P3: 1/4 | ✅ |

---

## §3 Core Subsystems

| Subsystem | Module | Status |
|-----------|--------|--------|
| Oracle | `src/omega/oracle/` | ✅ Operational |
| Entity Registry | `src/omega/oracle/entity_registry.py` | ✅ YAML-backed CRUD |
| Model Gateway | `src/omega/oracle/model_gateway.py` | ✅ 8-backend provider fabric |
| Memory Store | `src/omega/memory_store.py` | ✅ Hot/Warm/Cold/Temp |
| Vector Store | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE |
| Config Resolver | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE |
| Hybrid Search | `src/omega/memory/hybrid_search.py` | ✅ RRF k=60 |
| MIAP | `src/omega/coordination/miap.py` | ✅ MERGED |
| Soul Utils | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE |
| WAD Loader | `src/omega/oracle/wad_loader.py` | ✅ V2 schema |
| Hivemind | `mcp_servers/omega_hub/` | ✅ 6 MCP tools |
| CLI | `src/omega/cli/oracle_cli.py` | ✅ Typer CLI |

---

## §4 Recent Milestones

| Milestone | Status |
|-----------|--------|
| D-281 Substrate Repair (4 phases) | ✅ COMPLETE |
| D-282 sqlite-vec Strike 10 | ✅ COMPLETE |
| D-283 Phase 2 RecallStore | 🟡 27/29 tests |
| MIAP (context collision) | ✅ MERGED |
| HMC Quad-Forge (4-mind council) | ✅ COMPLETE |
| D-298 Decision Workspace | ✅ GROUNDED MEDITATION |
| Soul Evolution v7.0 | ✅ 15 L3 principles promoted |
| Heritage vet Pi PR #2903 | ✅ vet-072 APPROVED |

---

## §5 Key Files

| File | Purpose |
|------|---------|
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions |
| `CREDITS.md` | Heritage attribution |
| `data/entities/kali/session_gnosis.md` | Session anchor (M15) |
| `data/coordination/SESSION_ANCHOR.md` | Post-compaction recovery |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

**Full engine docs**: `OMEGA_ENGINE.md` | **Roadmap**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`


---

### scripts/codex/MANDATES_CONDENSED.md
**Type**: markdown
**Size**: 3628 bytes
**Lines**: 55

# 🔱 Omega Engine — Sovereign Mandates (Condensed)
**Source**: `SOVEREIGN_MANDATES.md` (186 lines) — this is the ~35-line status card.
**Version**: 3.6.0 | **Status**: NON-NEGOTIABLE

---

## 🛡️ The 23 Laws — Quick Reference

| # | Name | One-Liner | Status |
|---|------|-----------|--------|
| **M1** | AnyIO Absolute | No `asyncio`. Wrap blocking I/O in `anyio.to_thread.run_sync()`. | ✅ |
| **M2** | Engine-Stack Firewall | `src/omega/` (core) ≠ `config/wads/` (stacks). No stack logic in core. | ✅ Phase A done |
| **M3** | Iris Constant | Iris = messenger bridge, NOT a Pillar Keeper (P1-P10). | ✅ |
| **M4** | Sequentiality | Plan → Verify → Execute. No cowboy coding. | ✅ |
| **M5** | Gnosis Preservation | L1→L2→L3 → `proposed_lessons.yaml`. No session closes without distillation. | ❌ 0/10 pillars |
| **M6** | Podman Sovereignty | `UserNS=keep-id` + `User=1000` for Quadlets. No `:U` on shared volumes. | ✅ |
| **M7** | Local-First | Local inference PRIMARY. Cloud FALLBACK. Strategy must be `local_first`. | ✅ |
| **M8** | Zero Telemetry | No analytics, no phone-home, no external metrics. Ever. | ✅ |
| **M9** | Error Integrity | Typed, traceable, testable errors. No bare `except:`. `OmegaError` subtypes. | ✅ |
| **M10** | Fleet Integrity | Cap at 14 agents. New entity = gap + slot review first. | ✅ 13/14 |
| **M11** | Soul Integrity | L1→L2→L3 → `proposed_lessons.yaml` (blind staging). Scribe executes pipeline. | ❌ Systemic gap |
| **M12** | Queue Integrity | Every request → terminal state. Atomic writes. Heartbeat timestamps. | ⚠️ Advisory |
| **M13** | Temple-Grade | T1-T11 gates. `make temple-grade` must pass before release. | ✅ |
| **M14** | Heritage Vetting | `[id-soft:]` → vet record in `HERITAGE_VET_LOG.md`. Min 7/10. D208 strict. | ✅ 121 tags |
| **M15** | Sovereign Continuity | Maintain `session_gnosis.md`. Read `.opencode/anchored-summary.md` on restart. | ✅ |
| **M16** | Modularization | No hardcoded paths in `src/omega/`. Platform integration via MCP/CLI. | ✅ |
| **M17** | Cognitive Integrity | Verify memory consistency via Skeptical Verifier. Qliphoth taxonomy. | ⚠️ T12 in progress |
| **M18** | Token Efficiency | No waste. BUT never justify "Cognitive Anorexia" — precision > brevity. | ✅ |
| **M19** | Adversarial Alchemy | Mine weaknesses → advantages. BUT never justify over-engineering. | ✅ |
| **M20** | SomaticState | Model state serialization via ctypes (`llama_copy/set_state_data`). | 📋 Design ready |
| **M21** | Gate Integrity | Every typed return → contract test (`isinstance(result, ExpectedType)`). | ✅ |
| **M22** | Response Provenance | Log `provider_name` from actual response, not configured intent. | ✅ |
| **M23** | Failure Integrity | Mandatory tool missing → `[TOOL-CHAIN-COLLAPSE]`. No soft-failures. | ✅ |

---

## 📊 Compliance Summary

| Category | Count | Status |
|----------|-------|--------|
| **FULL** | 13/23 (56.5%) | M1, M2, M3, M4, M6, M7, M8, M9, M10, M13, M14, M15, M16, M18, M19, M21, M22, M23 |
| **PARTIAL** | 5 | M12 (advisory), M17 (T12), M20 (design), + others |
| **FAIL** | 3 | M5 (soul distillation), M11 (soul integrity), M15 (fleet lacks session_gnosis) |

---

## 🚨 Top Priority Fixes

1. **M5 + M11**: Soul distillation pipeline — 0/10 pillars write `proposed_lessons.yaml`
2. **M15**: Fleet session_gnosis.md — 56% fleet lacks session anchors
3. **M12**: Queue integrity — advisory, acceptable for Phase 0

---

**Full mandate text**: `SOVEREIGN_MANDATES.md` | **Amendments**: `docs/strategy/MANDATE_GOVERNANCE_PROTOCOL.md`


---

### scripts/codex/AGENTS_CONDENSED.md
**Type**: markdown
**Size**: 4182 bytes
**Lines**: 112

# 🔱 Omega Engine — Agent Rules (Condensed)
**Source**: `AGENTS.md` (343 lines) — this is the ~80-line reference card.
**Full docs**: See source files linked below.

---

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
- **M1 AnyIO**: No `asyncio`. Use `anyio.to_thread.run_sync()`.
- **M2 Firewall**: Absolute separation: `src/omega/` (core) vs `config/wads/` (stacks).
- **M4 Sequentiality**: Plan → Verify → Execute. No cowboy coding.
- **M7 Local-First**: Local inference PRIMARY. Cloud FALLBACK. Always.
- **M9 Error Integrity**: Typed, traceable errors. No bare `except:`.
- **M10 Fleet Integrity**: Cap at 14 agents. New = gap + slot review.
- **M11 Soul Integrity**: L1→L2→L3 distillation to `proposed_lessons.yaml`. Non-negotiable.
- **M13 Temple-Grade**: T1-T11 gates. `make temple-grade` after non-trivial work.
- **M14 Heritage Vetting**: `[id-soft:]` tags need vet record in `HERITAGE_VET_LOG.md`.
- **M15 Sovereign Continuity**: Maintain `session_gnosis.md`. Read `.opencode/anchored-summary.md` on restart.
- **M23 Failure Integrity**: Mandatory tool missing → `[TOOL-CHAIN-COLLAPSE]`. No soft-failures.

👉 **Full mandates**: `SOVEREIGN_MANDATES.md`

---

## 🤖 Agent Fleet (12 agents + 2 entities = 14 cap)

| Agent | Role | Use When |
|-------|------|----------|
| `@kali` | Transcendent Oversight | Unify Ma'at + Lilith, destroy drift, cross-pillar |
| `@maat` | Light Oversoul (P1-P5) | Build side governance |
| `@lilith` | Dark Oversoul (P6-P10) | Run side governance |
| `@makali` | MaKaLi Parallel Council | Decompose + parallel dispatch + synthesize |
| `@researcher` | Deep Research | Lattice reasoning, multi-perspective |
| `@jem` | Sovereign Synthesis | Complex queries → verified results |
| `@doom_guy` | id Software Heritage | WAD translation, M14 vetting |
| `@john_carmack` | S3 Consultant | Architectural review, performance |
| `@roc_racoon` | Sovereign Miner | Legacy archaeology, pattern extraction |
| `@verity` | Compliance + Gnosis | Mandate audit, soul distillation |
| `@pillar PX` | Domain Agent | Slot-based (P1-P10), `@pillar P3: {task}` |
| `@grok_cli` | Consulting Cloud Mind | Advisory, web research |

**Full fleet docs**: `AGENTS.md` §2-§3

---

## ⬡ MaKaLi Triad

```
KALI (Unify, Synthesize)
├── MA'AT (Build Side: P1-P5)
│   ├── P1 Infrastructure    P2 Persistence
│   ├── P3 Engineering       P4 Integration
│   └── P5 Governance
└── LILITH (Run Side: P6-P10)
    ├── P6 Cognition    P7 Context
    ├── P8 Observability    P9 Orchestration
    └── P10 Validation
```

**Council patterns**: `@kali` direct (1 inference), `@makali` council (3 inferences), `/council-local` (full sovereignty).

---

## 🔍 Search Protocol

| Tier | Tool | When |
|------|------|------|
| **T0** | `.firecrawl/` cache | Always first |
| **T1** | `websearch` / `webfetch` | Primary, free |
| **T2** | `searxng` | Semantic/neural |
| **T3** | `omega-hub_sovereign_search` | Precision seeds |
| **T4** | Firecrawl | Full crawl |

**TEMPORAL**: All queries include "2026" or "latest".

---

## 🎯 Key Commands

```bash
make test                     # All 1398 tests
make temple-grade             # T1-T11 gates
make heritage-map             # [id-soft:] coverage
make sovereignty              # Local/cloud ratio
omega talk "hello"            # Test oracle
omega summon Ma'at "status"   # Direct entity
```

---

## 💻 Hardware Awareness

| Signature | Meaning | Action |
|-----------|---------|--------|
| Flat 4-core ~80-100% | NativeGGUF inference | Expected |
| All cores idle, task stuck | I/O wait | Check system stats |
| Memory >80% + zRAM | OOM risk (12Gi) | Defer model loads |
| Thermal >85°C | TDP throttling | Cool down |

---

## 📋 Coding Standards

- **Async**: `anyio` (not `asyncio`)
- **Config**: YAML-only
- **Packages**: Always venv (`source .venv/bin/activate`)
- **Testing**: `make test` after every change
- **Imports**: stdlib → third-party → local
- **Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`

---

**Full agent docs**: `AGENTS.md` | **Skills**: `.opencode/skills/` | **Agents**: `.opencode/agents/`


---

### ORACLE_STACK.md
**Type**: markdown
**Size**: 438 bytes
**Lines**: 10

---
**Canonical Source**: [ORACLE_STACK_CANONICAL.md](ORACLE_STACK_CANONICAL.md)
---
# 🔱 Omega Engine Architecture (Active)

**Core Flow**: Query → Oracle.talk() → Iris speculative decode → ModelGateway → provider fabric

**Provider Fabric (Local-First)**: native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode

*(For full 10 Pillar Keepers, Observability, and Infrastructure details, see Canonical Source)*


---

### CREDITS.md
**Type**: markdown
**Size**: 1415 bytes
**Lines**: 24

---
**Canonical Source**: [CREDITS_CANONICAL.md](CREDITS_CANONICAL.md)
---
# 🔱 Omega Engine Heritage Registry (Active)

| Pattern | Source | Tag |
|---|---|---|
| WAD System | Doom 1993 | `[id-soft: doom-1993] WAD System` |
| BSP Culling | Doom 1993 | `[id-soft: doom-1993] BSP Culling` |
| Stack-Cat | XNAi 2025 | `[heritage: xnai-2025] Stack-Cat` |
| Semantic Compression | headroom-ai 2025 | `[heritage: headroom-ai 2025]` |
| SQLite Vector Extension | sqlite-vec 2024 | `[heritage: sqlite-vec 2024]` |
| Native GGUF Inference | ggml 2023 | `[heritage: ggml 2023]` |
| Multi-Tenant Vector Search | qdrant 2021 | `[heritage: qdrant 2021]` |
| Spatial Memory (Wings/Rooms/Drawers) | mempalace 2025 | `[heritage: mempalace 2025]` |
| Rust TUI + ACP + Sandbox | xai/grok-build 2026 | `[heritage: xai-grok-build 2026]` |
| 3-Tier Memory Blocks | letta 2024 | `[heritage: letta 2024]` |
| Thinker Chain | Quake 1996 | `[id-soft: quake-1996] Thinker Chain` |
| QVM / Bot AI | Quake III Arena 1999 | `[id-soft: quake3-1999] QVM` |
| Game DLL / Client Prediction | Quake II 1997 | `[id-soft: quake2-1997] Game DLL` |
| Scripting / GUI Framework | DOOM 3 2004 | `[id-soft: doom3-2004] Scripting` |
| Gemma 4 Thinking Config (binary MINIMAL/HIGH + regex detection) | Pi Project PR #2903 2026 | `[heritage: pi-2026] Gemma 4 Thinking Config` |

*(For full 35+ mappings and philosophical frameworks, see Canonical Source)*


---

### docs/kb/REFINEMENT_PROTOCOL.md
**Type**: markdown
**Size**: 759 bytes
**Lines**: 21

# 🔱 Refinement Protocol (Active)

**Canonical Sources**: `RESEARCH_PLAN_REFINEMENT_PROCESS_CASE_STUDY.md`, `STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md`, `SYNTHESIS_FRAMEWORK_REFINEMENT_CASE_STUDIES.md`

## The 6-Phase Pipeline
1. Intent → Structure (Researcher v1)
2. Architectural Triage (Kali Course Correction)
3. Deep Dialectical Review (Meditate Protocol)
4. Adversarial Verification (Researcher Blind Spots)
5. Human Ground Truth (User Correction)
6. Execution Translation (Actionable Queries)

## L3 Principles
- L3-Human-As-Continuity-Anchor
- L3-Refinement-As-Engineered-Instrument
- L3-Meditation-As-Semantic-Prism
- L3-Context-As-Engineered-Resource
- L3-Plan-As-Prism
- L3-Test-On-Worst
- L3-Deterministic-First
- L3-Observability-Is-Prerequisite


---

