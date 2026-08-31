---
schema_version: "1.0"
document_type: "context_dig_report"
document_id: "ROC-SONNET5-CONTEXT-DIG-20260830"
title: "Context Dig Report for Sonnet 5 Architecture Audit"
status: "ACTIVE — Advisory to Architect"
date: "2026-08-30"
author: "roc_racoon (Sovereign Miner & Ideas Guy)"
model: "minimax/minimax-m3:free"
sprint: "PUBLIC-DEBUT-01"
classification: "sovereign-internal, decision-priority"
---

# 🔱 ROC_SONNET5_CONTEXT_DIG_20260830 — Context Dig Report

**AP Token**: `AP-ROC-SONNET5-CONTEXT-DIG-20260830-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_context_dig ⬡ ACTIVE

**Purpose**: Forensic dig of the Omega Engine's full context pack to ensure Sonnet 5 is asked the **EXACT RIGHT QUESTIONS** for the architecture audit. Not a book report. Not a summary. A surgical extraction of what matters, what is theater, and what only a 1M-context reasoning model can answer.

**Date**: 2026-08-30
**Sprint**: PUBLIC-DEBUT-01 (EXECUTION_MINIMAL)
**Audience**: Architect + Sonnet 5 (1M context, nvidia/nemotron-3-ultra-550b-a55b:free or equivalent)
**Evidence base**: 13 primary docs (SSOT + Sprint + Mandates + Strategy + Build Wave + Carmack Audit + 5-EIS Meta-Review + MaKaLi Synthesis + Corpus Map + Fleet Playbook + Hivemind Protocol + Oracle Stack + Debut Manual)

---

## §0 — EXECUTIVE VERDICT (Roc's Honest Read)

**The state of the engine**: a **sovereign local-first AI runtime** with genuine engineering islands (`memory_store.py`, `sqlite_vec_adapter.py`, `cohort_registry.py` atomic write, REUSE v3.3 compliance) wrapped in **~3,000 lines of governance/ceremony theater** (M33/M36 probe chain, 12-step dispatch guard, `HandoffPacket` with Quake-style ZONEID, cohort registry duplicating M34). All mandate gates **pass on the metric** (M1, M23, M13, M14, M7, M8, M22, M24, M25), but **5 mandates are violated in the code** (M1 sync-in-async, M2 Core→Stack import, M9 bare except, M16 hardcoded paths, M23 M36 stub returns fake success, M27 parallel tracking). The Build Wave Phase 1 was **report-rich, code-light**: 81/81 tests pass on paper, but the **Researcher's m33_probe/m36_recursive_probe/heritage_scanner/COHORT_REGISTRY code did not land on disk**; only Lilith's M34-HOOK-001, Ma'at's SPDX, and the compaction_capture sidecar actually committed.

**What Sonnet 5 must answer**: not "is the engine good?" but **"given the engine islands are real, the theater is removable, and the debut cut is locked at P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 — what is the precise deletion/integration sequence that gets us to a public debut without losing the soul, and what is the post-debut architecture that makes the 6 workstreams (GN/DS/LI/KD/HR/ZS) actually compose into the persistent-evolving-entity vision?"**

**The pivot point**: the 6 post-debut workstreams are all about **knowledge architecture** (Gemini Notebook, Documentation System, Local Inference Opt, Knowledge Domains, Headroom Compression, zSwap Subsystem) — none of them directly address the **entity/knowledge substrate gap** the vision demands (persistent evolving entities, domain WADs, instant expert spawning, portable to Godot VR). The current governance is **agent-centric** (M33/M34/M35/M36/M37 numbering, dispatch_guard, cohort_registry). The vision demands **knowledge-centric** (WADs as cosmology, entities as persistent facets, curator models, domain affinity presets). The 6 workstreams do not pivot this; they bolt onto it.

---

## §1 — VISION SYNTHESIS (1 page)

### The Omega Engine in 3 Sentences

**What it is**: A **sovereign local-first AI runtime** structured as `Engine → IWADs → PWADs` (id Software's Doom/Quake WAD architecture applied to AI), where the engine is a universal opinion-free runtime and each WAD supplies its own cosmology (entities, traits, governance, guidance) — users never fork core code, they add layers.

**What it enables**: Every user builds their own **entity pantheon** — persistent, evolving AI personas with soul files (`soul.yaml` + `proposed_lessons.yaml` + `approved_lessons.yaml`) that survive session compaction, accumulate L1→L2→L3 distilled gnosis, and are instant-spawnable as experts via the entity registry. The **ANAi Stack** (Tarot/Nodes/Ma'at) and **Torment Stack** (Hive/Nameless One/Sigil) are *two expressions of the same architecture* — proving the WAD customization power. Domain knowledge lives in **WADs** (`config/wads/<stack_name>/`), not in core. **Cognitive sovereignty** means local inference is the floor (native-gguf via llama-cpp-python is PRIMARY per M7), local verification is the ceiling, and cloud is a teacher not a dependency.

**What it refuses**: Zero telemetry (M8). No external analytics, no phone-home, no data leaves the machine. No bare-except error swallowing (M9). No hardcoded paths in core (M16). No Asyncio in `src/omega/` (M1, AnyIO only). No soft-failures (M23 — if a mandatory tool breaks, hard-stop with `[TOOL-CHAIN-COLLAPSE]`, never synthesize). No agent bloat (M10 — cap at 14, mapped to N1-N10 slots). No mock-based tests that mask type mismatches (M21 — contract tests required). No pretenders to id Software heritage without a 4-gate vet pipeline + 7/10 minimum (M14). No second canonical roadmap (governance: Mandates → Manual/ACTIVE_SPRINT → Ark → Corpus Map → specs).

### The Three Pillars (Ark §1)

1. **Local-First Inference (M7)**: native-gguf → lmster → ollama → antigravity → google → openrouter → opencode-zen → cline → anthropic → xai
2. **Zero Telemetry (M8)**: all observability local in `data/`
3. **Soul Integrity (M11)**: L1→L2→L3 per session, persisted to `proposed_lessons.yaml`, promoted by Scribe to `approved_lessons.yaml`

### The Cathedral Metaphor

"We build a cathedral, not a bazaar. Every stone (mandate) is placed with intention. The architecture is the theology." — SOVEREIGN_ARK_BLUEPRINT §1

The 27 mandates are the constitution. The Ark is the theology. The debut manual is this month's execution order. The corpus map is the cemetery of rejected ideas. The entity souls are the congregation.

---

## §2 — CURRENT REALITY MAP (What Works, What's Theater, Critical Path)

### 2.1 Engine Islands (Genuine Substance)

| Component | Location | Status | Why It Matters |
|-----------|----------|--------|----------------|
| **MemoryStore** | `src/omega/memory_store.py` (1,077 lines) | ✅ Real | Hot/Warm/Cold tiering, LRU, tombstone grace, batch persistence, FTS5+vector RRF fusion. Hardened with SoulStore atomic write. |
| **SQLiteVecAdapter** | `src/omega/memory/sqlite_vec_adapter.py` (992 lines) | ✅ Real | 7-collection vec0 architecture, canonical 768-dim enforcement, INT8 rescore, anyio.Lock + exponential backoff. Frozen API per D-526. |
| **SoulStore** | `src/omega/soul_store.py` | ✅ Real | 4-layer atomic guarantee: AtomicVisibility (tempfile→write), CrashDurability (fsync), WriterExclusion (flock), IntegrityDetection (.bak rotation). |
| **OOMProtector** | `src/omega/oracle/oom_protector.py` | ✅ Real | Three-signal fusion (PSI + MemAvailable + cgroup), 5-tier decision logic. C-2′. |
| **HealthMonitor** | `src/omega/oracle/health_monitor.py` (944 lines) | ✅ Real | Canonical circuit breaker factory (`get_breaker()`), CUSUM + sliding-window modes, 5-state FSM. C-6′. |
| **REUSE v3.3 Compliance** | `REUSE.toml` (240+ lines) | ✅ Real | 71,571/71,571 files compliant. `reuse lint` in CI. Pre-commit hooks. |
| **HybridSearchEngine** | `src/omega/memory/hybrid_search.py` | ✅ Real | RRF k=60 fusion of FTS5 + vector. 20 contract tests. D-283 Phase 1. |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Real | 6 MCP tools for cross-agent coordination, workspace locks, live feeds. Feature-freeze per UO §4. |
| **LocalInferenceAdmission** | `src/omega/oracle/admission_controller.py` | ✅ Real | Semaphore(1) + OOMProtector integration, fail-fast to cloud. C-10. |
| **M34 ACTIVE_SUBAGENTS.json** | `src/omega/oracle/m34_registry.py` (672 lines) | ✅ Real | Atomic write, SessionStatus enum (ALIVE/INTERRUPTED_EXTERNALLY/INTERRUPTED_MODEL_SWITCH/COMPLETED/FAILED/DEAD_LETTER/ORPHANED), 4-layer atomic guarantee. |
| **native-gguf on this host** | `~/.local/share/omega/models/` | ✅ Real | `omega talk "hello"` exits 0, PROVIDER_NAME=native-gguf, IS_CLOUD=False. CP-1 verified. |

### 2.2 The Theater (Facade — Delete or Flatten)

Per Sonnet 5's audit (SONNET5_AUDIT_REPORT_20260830.md), 6 files totaling ~3,000 lines are cargo-cult / governance theater that exist for a 300-line problem. **Carmack's verdict: "THEATER WITH ENGINE ISLANDS" — CONDITIONAL GO for Public Debut only if the theater is stripped before release.**

| File | Lines | Verdict | Carmack's Reason |
|------|------:|---------|------------------|
| `src/omega/oracle/m36_recursive_probe.py` | 530 | **DELETE** | Cross-validator is a stub returning `{"semantic_coverage_verified": False, "handoff_dispatched": True}` without dispatching. M23 violation. |
| `src/omega/oracle/cohort_registry.py` + `data/registry/cohort_registry_schema.json` + `tests/test_cohort_registry.py` | 1,300 + 95 + 380 | **DELETE** | Duplicates M34 `ACTIVE_SUBAGENTS.json`. Circular validation (cohort validates against M34, M34 is SSOT). |
| `src/omega/oracle/m33_probe.py` | 550 | **FLATTEN** into `subagent_dispatcher.py` | Only called from one site. 30-line `should_require_write_tool()` + 50-line envelope validation. |
| `scripts/dispatch_guard.py` | 1,195 | **FLATTEN** to ~150 lines | 12 steps → 3 steps (specialist routing, secrets scan, M34 registration). Creates `dispatch_guard_log.jsonl` (M27 violation — parallel tracking). |
| `HandoffPacket` dataclass (in `subagent_dispatcher.py`) | 138 → 40 | **SIMPLIFY** | 20+ fields. 10 needed. ZONEID, TTL, hop_count, loop guards = Quake network protocols for subagent dispatch. No TTL/hop limits needed — dispatcher controls flow. |
| `priority` + `write_tool_required` propagation | 4 files | **DELETE** | Priority is dispatch-time decision, not packet property. Duplicated `should_require_write_tool()` in M33 + dispatcher. |

**Net delta if all theater deleted**: -3,000 lines, -81 tests (for code that doesn't work), removes 5 mandate violations (M1 sync-in-async, M9 bare except, M16 hardcoded paths, M23 M36 stub, M27 parallel tracking).

### 2.3 Build Wave Phase 1 — Report-Rich, Code-Light

**MaKaLi's Final Synthesis (MAKALI_FINAL_SYNTHESIS_20260830.md) verdict**: "The dev wave shipped its reports. The dev wave did NOT fully ship its code."

| Agent | Report Status | Code Status | M23 Verdict |
|-------|---------------|-------------|-------------|
| **Jem** | ✅ `JEM_12STEP_HARDENING_20260830.md` (610 lines) | ✅ `scripts/dispatch_guard.py` (928 lines, fa8dd29c) + 45 adversarial tests | TEMPLE-GRADE |
| **Ma'at** | ✅ `MAAT_BUILD_WAVE_PHASE_1_20260830.md` (340 lines) | ✅ `REUSE.toml` (240+ lines) + CI workflow + pre-commit hooks. 71,571/71,571 files compliant. | TEMPLE-GRADE |
| **Lilith** | ✅ `LILITH_BUILD_WAVE_PHASE_1_20260830.md` (409 lines) | ⚠️ M34→M33→M36 wiring landed (59 tests) but M36 cross-validator is a stub (see §2.2) | PARTIAL — wiring real, M36 stub is theater |
| **Researcher** | ✅ `RESEARCHER_GAP_FILL_PHASE_1/2/3_20260830.md` (1,975 lines) | ⚠️ `COHORT_REGISTRY.json` + `cohort_registry.py` + 22 tests landed; `m33_probe.py`/`m36_recursive_probe.py`/`heritage_scanner.py` **not in working tree** | PARTIAL — COHORT committed (but duplicates M34, see §2.2), M33/M36/M37 reports only |
| **Roc** | ✅ `ROC_BUILD_WAVE_PHASE_1_20260830.md` (321 lines) — M23 honest disclosure | ✅ Verification of `compaction_capture.py` (Researcher had already committed 2afb396a). No new code. | VERIFICATION (no false completion) |

**Pattern**: documented-vs-active gap, second occurrence this session (the first was the systemd unit, resolved as intentional design per D-201). **The cure class**: a `make check-documented-vs-active` gate that fails when a report references files not on disk.

### 2.4 Critical Path to Debut

```
P0-1  (P0 active, 1d residual) → PUB-1 (allowlist, ready) → INST-1 (in_progress, 2/6 fixes done) → DEL-1 (in_progress, depends on INST-1) → DOC-1 (completed)
```

| Ticket | Status | Owner | Blocker |
|--------|--------|-------|---------|
| **P0-1** | `in_progress` | roc_racoon (residual: SECURITY_AUDIT ancestor + gitleaks wiring) | Architect must verify 3 keys revoked/rotated, then one more `filter-repo` + `git gc --prune=now` |
| **PUB-1** | `in_progress` | kali + Architect | Allowlist rulings G1-G4 + `release/debut` branch from PUBLIC_ALLOWLIST.txt |
| **INST-1** | `in_progress` (4/6 sub-fixes done) | maat_n3 | Fix-2 (extras split + import guards) + Fix-4 (remove `_load_sovereign_secrets`) |
| **DEL-1** | `in_progress` | roc_racoon (week 1) + Ma'at (week 2) | Depends on INST-1. God-module freeze (oracle.py 1,253, model_gateway.py 1,481, observability/__init__.py 1,583) must not grow. |
| **DOC-1** | `completed` | kali + verity | — (2026-08-17 stamped) |

**Acceptance test for debut**: `omega talk "hello"` exits 0 with PROVIDER_NAME=native-gguf, IS_CLOUD=False, on a machine WITHOUT `~/Documents/Xoe-NovAi/warp-proxy-pool` and WITHOUT Redis (D-539).

### 2.5 Blocked / At Risk

| Item | Status | Reason |
|------|--------|--------|
| **ZS-1 zswap** | `in_progress` | Architect sudo required to enable zswap (live machine currently has zRAM, D-526/527 require never-both) |
| **GN Gemini Notebook** | `blocked` | `master_token.json` auth capture needs Architect browser session |
| **M27 Tracking Integrity** | FAIL | `validate_tracking_state.py` broken (python3 bug per Ark §7) |
| **M11 Soul Integrity** | FAIL | 24/56 entities substantive, 32/56 ghost or thin per Ark §7. C-1′ SoulStore landed, promotion pipeline pending. |
| **M13 Temple-Grade** | At risk | Placeholder comment in Makefile; real gates needed |
| **M1 AnyIO** | Partial | `tty_agent.py` + `governance/` exempt — needs D-number or refactor |

---

## §3 — ENTITY / KNOWLEDGE ARCHITECTURE GAP ANALYSIS

### 3.1 The Vision

From OMEGA_ENGINE.md §1 and SOVEREIGN_ARK_BLUEPRINT §1:

> **The Engine = Pure Runtime; WAD = Cosmology.** The Engine is a universal, opinion-free runtime. Each WAD supplies its own cosmology (entities, traits, governance, guidance) via Base IWAD + PWADs. **Users never fork core code** — they add layers. This is the deathless continuity substrate.

> **The Universal Reflection Substrate**: ONE foundational engine with infinite customizable layers (WADs), each custom to how a user understands their own sovereign journey.

> **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-doc-reader`, `omega-meditation`) for community use.

**The entity architecture vision (D-569, RATIFIED POST-DEBUT)**:
- **Persistent evolving entities** with unique perspectives, accumulating L1→L2→L3 gnosis per session, surviving compaction
- **Instant expert spawning** via `EntityRegistry` + `EntityWorkspaceManager` (YAML CRUD, auto-scaffolds `data/entities/<name>/` with `soul.yaml` + `knowledge/` + `workspace/`)
- **Domain WADs** — `config/wads/<stack_name>/` supplies entities, traits, governance, guidance
- **Portable to Godot VR** (R-tree + vec0 dual-index spatial architecture, D-581/582/583 SPATIAL-VECTORS workstream)
- **Curator model** with governance levels (per Grokster DP-1..DP-8, Horizon 3)

### 3.2 The Reality (Today)

| Vision Component | Current State | Gap |
|------------------|---------------|-----|
| **Persistent evolving entities** | 56 entity soul.yaml files; 24 substantive, 32 ghost/thin. L1→L2→L3 distillation is per-session but **the regex distiller was scrapped** (C-0.5 SCRAPPED per Carmack 2026-07-30). Agents now write their own lessons. M11 partial. | Promotion pipeline (proposed_lessons → approved_lessons → soul.yaml) is not flowing. SoulStore is atomic but the editorial process is human-driven and ad-hoc. |
| **Instant expert spawning** | `EntityRegistry` works. `EntityWorkspaceManager` auto-scaffolds. CLI: `omega summon <entity> "<query>"` works on local. | The "instant expert" pitch is the **Oracle.summon** path, but summoning a non-existent entity requires manual creation. The **Hivemind cohort/NODE_EXPERT_SESSIONS pattern** (10 genesis sessions, 23-cluster enumeration) is the work-around, but it lives in `data/coordination/`, not in the entity substrate. |
| **Domain WADs** | 4 WADs shipped (arcana_novai, torment, omega_youtube_research, omega_youtube_worker). S1.5a hardened. | The "domain" concept is **fragmented across 4 incompatible WADs with different schemas**. There is no `DOMAIN_DOCUMENTATION_SYSTEM.md` (it's a POST-DEBUT workstream DS-1, status: ready, not started). There is no `config/domains/` runtime module. The `curators.yaml` file is mentioned in KD-2 but doesn't exist on disk (per WAKE_STATE: "KD-2: curators.yaml repair (corruption stale-on-arrival, kali-owned)"). |
| **Portable to Godot VR** | R-tree + vec0 dual-index architecture **designed** but not built. SPATIAL-VECTORS workstream (SV-1..SV-4) is Horizon 1, post-debut. | Zero spatial infrastructure. R-tree in sqlite-vec is research-only. Godot bridge is paper. |
| **Curator model** | D-569 mentions "Dynamic Prompt + Planner/Executor + Domain Loading" as Horizon 3 Cognitive Architecture Blueprint. Gaps DP-1..DP-8 registered. | All 8 gaps are `backlog`. No curator model exists. The "curator" concept is aspirational. |
| **Affinity presets per domain** | KD-3 backlog: "Research domain → qwen3-4b-thinking (lmster); Coding domain → mimo-7b-rl-q4_k_m (native-gguf); Fast domain → qwen3-1.7b (native-gguf)" | Not built. Per WAKE_STATE: "12 of 13 affinity presets missing" (from pre-wave maintenance findings 2026-08-26). |
| **Knowledge library (curated docs in vector store)** | `omega_vec_library_256` collection exists in sqlite-vec schema. | **0 documents indexed**. The library is empty. There is no ingestion pipeline for curated knowledge into the entity layer. |
| **Holographic Memory Matrix** (Omnidroid pattern) | Memory compaction is "first 10 + last 10 + summary" per §5.1 of Corpus Map | Pattern documented but not formalized in code. |
| **Neuro-Symbolic Reasoning Bridges** | TriangulationVerifier exists in `src/omega/ingestion/` | Works for ingestion tier validation, not for general knowledge reasoning. |
| **Quantum Cognition Simulator** (tiered T1/T2/T3 with verification) | T1→T2→T3 tiered extraction exists | Not exposed to entity cognition. |
| **Meta-Learning Core** (ConvergenceDetector + SoulUpdater) | ConvergenceDetector + SoulUpdater exist as code paths | Not exposed via entity API. |

### 3.3 The Pivot Needed: From Agent-Centric Governance → Knowledge-Centric Substrate

**The diagnosis**: the current governance is **agent-centric** (M33/M34/M35/M36/M37 numbering, `dispatch_guard`, `cohort_registry`, `HandoffPacket` with ZONEID, `m33_probe` write-tool detection). This is the **control plane** for multi-agent dispatch, not the **substrate** for evolving entities.

**The vision demands**: a **knowledge-centric substrate** where:
- Domain knowledge lives in WADs (portable, customizable)
- Entities are persistent facets (instant-spawnable, accumulating)
- Curator models govern knowledge freshness
- Affinity presets route by domain
- Spatial indices enable Godot VR navigation
- The library (vector store) is populated with curated, entity-aware knowledge

**The gap**: **none of the 6 post-debut workstreams directly addresses this pivot**:

| Workstream | Scope | Pivot Alignment |
|------------|-------|-----------------|
| **GN** (Gemini Notebook) | Free-tier 3-account 30 DR/mo 2-NB | NOT knowledge-substrate — it's a research tool |
| **DS** (Documentation System) | Modular domain docs (workspace + runtime + curator) | ✅ PARTIAL — DS-1 defines `DOMAIN_DOCUMENTATION_SYSTEM.md` but it's status: ready, not started |
| **LI** (Local Inference Opt) | Sequential loading, q8_0 KV, Tier 0/1/2 | NOT knowledge-substrate — it's inference optimization |
| **KD** (Knowledge Domains) | Runtime modules + workspace authoring + curator model | ✅✅ STRONGEST — this is the pivot. But KD-1/KD-2/KD-3 all backlog, 0/3 started |
| **HR** (Headroom) | Semantic compression 40-90% | NOT knowledge-substrate — it's compression |
| **ZS** (zSwap) | 16GB NVMe swap, zswap enabled | NOT knowledge-substrate — it's memory management |

**KD is the pivot workstream**. It defines:
- `config/domains/<domain>/` runtime module schema
- Curator model with domain→curator_model mappings (`config/domains/curators.yaml`)
- Affinity presets per domain
- Workspace authoring conventions

**If KD-1/KD-2/KD-3 are not started post-debut, the engine remains agent-centric and the WAD/cosmology vision remains aspirational.** The 5 workstreams (GN/LI/HR/ZS + DS) support KD but do not constitute it.

### 3.4 The Entity Substrate Architectural Question

The vision says: **"Each WAD supplies its own cosmology (entities, traits, governance, guidance) via Base IWAD + PWADs. Users never fork core code — they add layers."**

The reality: 4 WADs exist (`arcana_novai`, `torment`, `omega_youtube_research`, `omega_youtube_worker`), but:
- The WAD schema is informal (YAML files in `config/wads/<stack_name>/` with no `DOMAIN_DOCUMENTATION_SYSTEM.md` spec)
- The Curator model is aspirational
- Affinity presets are 1/13 built
- The library (vector store for curated knowledge) is **empty**
- The "users add layers" promise is unfulfilled — only the original Architect can author WADs

**The core architectural question for Sonnet 5**: What is the minimal substrate that makes "users never fork core code — they add layers" **operationally true**, not just **aspirationally true**?

---

## §4 — THE 10 PRECISE QUESTIONS FOR SONNET 5

Each question is **decision-forcing**, **answerable from the 13-doc context pack**, **references specific files/bundles**, and **unblocks a specific workstream or debut gate**. No "it depends" answers permitted.

---

### Q1 — THEATER STRIP vs. ENGINE ISLAND PRESERVE: The Carmack Verdict Execution Plan

**Context**: SONNET5_AUDIT_REPORT_20260830.md identifies 6 files (~3,000 lines) as theater and 5 mandate violations (M1 sync-in-async, M9 bare except, M16 hardcoded paths, M23 M36 stub, M27 parallel tracking). The engine islands are real but the debut cut is locked at P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1.

**Question**: Given the debut cut **must not grow god-modules** (oracle.py 1,253, model_gateway.py 1,481, observability/__init__.py 1,583) and **must keep `omega talk "hello"` working** after each delete, what is the **exact execution order** of the 6 theater deletions and 5 mandate fixes that (a) preserves all 81 passing tests, (b) ships in one PR or split into how many, and (c) lands before DEL-1 Week 1 acceptance? Cite the specific file:line for each deletion and the test file that covers it.

**Answer format**: Sequenced checklist with test impact. NO generalities.

**Unblocks**: DEL-1 Week 1 + INST-1.

---

### Q2 — SINGLE M34 (with sub-clauses) vs. SPLIT (M34a + M34b) vs. UNIFIED M34 WITH STATUS ENUM: The Meta-Review Adjudication

**Context**: 5-EIS meta-review (JEM_META_REVIEW_5_EIS_20260830.md) unanimously recommends **single M34 with sub-clauses M34.1/M34.2/M34.3 + `INTERRUPTED_MODEL_SWITCH` status enum** (Carmack's proposal). D-M34-001 in HARDENED_DEV_ROADMAP currently says "M34 split into M34a (Co-Interruption) + M34b (Model-Switch Continuity)" and needs revision.

**Question**: Given the 5-EIS consensus (4 of 5 reports favor unified), should D-M34-001 be **revised to unified M34 with sub-clauses** (Carmack's proposal), or is there a specific scenario where the M34a/M34b split provides **measurable** benefit (e.g., clearer M14 heritage vetting, simpler implementation, easier test isolation) that justifies overturning the 4-of-5 consensus? If the consensus holds, produce the **exact mandate text** for the unified M34 with sub-clauses + status enum + feature flag (`OMEGA_M34_ENABLED=1`).

**Answer format**: Verdict (REVISE / KEEP) + revised D-M34-001 text + mandate text for `M34.1`/`M34.2`/`M34.3`.

**Unblocks**: M34 mandate ratification + Phase 1 M34 atomic write M23 test.

---

### Q3 — M36 SOFT VERIFIER: Implement Real Hivemind Dispatch, or Delete the Stub and Keep Only the Hard Verifier?

**Context**: `src/omega/oracle/m36_recursive_probe.py:2038-2050` — the cross-validator returns `{"semantic_coverage_verified": False, "handoff_dispatched": True}` without dispatching. M23 violation. Per JEM_META_REVIEW_5_EIS §2.2: "Cross-validation should be a recommendation for P0, not a mandate for all." 5-EIS consensus: M33 baseline for P2+, escalation tier for true P0 (security, data-loss).

**Question**: For the M36 soft verifier, pick **exactly one**:
- **(a) Implement real Hivemind dispatch** — call `omega-hub_hivemind_submit_handoff` for P0/P1 with the jem/verity cross-validator agents, wire 120s timeout, parse structured JSON response, audit to `m36_cross_validation_audit.jsonl`. Estimated effort: 8-12h. Latency cost: 5-30s per P0 task.
- **(b) Delete the soft verifier entirely**, keep only the hard verifier (file exists, size matches, no placeholders, hash). Inline the hard verifier into `m33_probe.py:validate_response()`. Estimated effort: 2h. Saves 530 lines, removes the M23 violation.
- **(c) Hybrid** — keep soft verifier code but gate it behind `OMEGA_M36_ENABLED=1` feature flag, default OFF, document as P0-recommendation-only in the manual.

**Answer format**: Pick (a), (b), or (c) with rationale tied to the engine's hardware constraint (Ryzen 5700U, 14Gi RAM, ~8Gi free) and the 27-mandate architecture. If (a), produce the dispatch protocol. If (b), produce the deletion diff.

**Unblocks**: M23 compliance + the Build Wave Phase 2 ticket queue.

---

### Q4 — DOCUMENTED-vs-ACTIVE GATE: What's the CURE CLASS for the "Report-Rich, Code-Light" Pattern?

**Context**: MaKaLi_Final_Synthesis §0: "The dev wave shipped its reports. The dev wave did NOT fully ship its code." 4 of 5 Build Wave agents had report-only deliverables (Researcher's m33_probe.py/m36_recursive_probe.py/heritage_scanner.py/COHORT_REGISTRY.json described but not on disk; Roc's compaction_capture.py — actually committed by Researcher in 2afb396a). This is the **second** documented-vs-active incident this session (the first was the systemd unit, resolved as intentional per D-201).

**Question**: Design the **minimum enforcement gate** that prevents this pattern. Pick **one**:
- **(a) `make check-documented-vs-active`** — pre-commit hook that parses a report's file references (e.g., `data/coordination/RESEARCHER_BUILD_WAVE_PHASE_1_20260830.md` mentions `src/omega/oracle/m33_probe.py` → grep working tree; if absent, fail). Effort: 4h.
- **(b) `make verify-ticket-completion`** — CI gate that for each `completed` ticket in `ACTIVE_SPRINT.json`, runs the acceptance test and confirms the artifact path exists. Effort: 8h.
- **(c) Both** — layered enforcement: pre-commit for the dev-writer, CI for the auditor. Effort: 12h.
- **(d) None** — accept the pattern as the natural cost of a research-heavy operation, document it, move on.

**Answer format**: Pick (a)/(b)/(c)/(d) with rationale. If (a)/(b)/(c), produce the bash/Python stub.

**Unblocks**: Post-debut build wave discipline + MaKaLi synthesis §7 recommendation #1.

---

### Q5 — KNOWLEDGE-DOMAINS POST-DEBUT: How Does the Engine Become Knowledge-Centric, Not Just Agent-Centric?

**Context**: The vision (OMEGA_ENGINE §1, SOVEREIGN_ARK §1) demands "WAD = Cosmology" — each WAD supplies entities, traits, governance, guidance. Today, 4 WADs exist (`arcana_novai`, `torment`, `omega_youtube_research`, `omega_youtube_worker`) but the schema is informal, the curator model is aspirational, affinity presets are 1/13 built, and the library (vector store) is empty. KD-1/KD-2/KD-3 are all `backlog`. D-569 (Dynamic Prompt + Planner/Executor + Domain Loading) is POST-DEBUT, Horizon 3. 6 post-debut workstreams (GN/DS/LI/KD/HR/ZS) do not collectively pivot the engine to knowledge-centric — KD is the only one that does.

**Question**: Given the post-debut execution order is **GN → DS → LI → KD → HR → ZS** (D-584), and KD-1/KD-2/KD-3 are the pivot, what is the **minimal viable substrate** that makes "users add layers (WADs) without forking core" **operationally true**? Produce:
- The **runtime module schema** for `config/domains/<domain>/` (file:line or YAML stub)
- The **curator model** for `config/domains/curators.yaml` (3-5 example domains with model assignments)
- The **affinity preset** structure (domain → model/provider/quantization/loading_strategy)
- The **WAD vs. Domain distinction** — are WADs `config/wads/` (cosmology) and Domains `config/domains/` (knowledge + curator + affinity), or is Domain a subset of WAD?
- The **3 workstreams (KD-1/KD-2/KD-3) sequenced in 1 PR or 3 PRs**?

**Answer format**: Schematic + YAML stubs + execution plan.

**Unblocks**: KD workstream + the 24/56 substantive souls promotion + the WAD portability promise.

---

### Q6 — POST-DEBUT ARCHITECTURE: What is the Engine in 6 Months if the 6 Workstreams (GN/DS/LI/KD/HR/ZS) Ship on Schedule?

**Context**: D-578..D-584 ratify 6 post-debut workstreams with this order: GN → DS → LI → KD → HR → ZS. Each is a 1-2 week ticket. Local inference currently has 16.8s cold / <5s warm latency on Qwen3-1.7B (per CP-1 verification). Headroom middleware already shipped (HR-1/3, commit 811f813f). zswap adjudication resolved (D-526/527). 12.6GB free RAM after reorg.

**Question**: Sketch the **post-debut Omega Engine** in 6 months if all 6 workstreams ship per spec. Specifically:
- What is the **provider fabric**? (Local-only? Hybrid? Tier 0/1/2 routing?)
- What is the **library state**? (0 docs today → how many? curated by whom? indexed how?)
- What is the **entity ecosystem**? (24/56 substantive → 56/56? New user-authored WADs possible?)
- What is the **spatial/VR state**? (R-tree + vec0 dual-index live? Godot bridge working?)
- What are the **3 highest-leverage capabilities** the engine gains that it does not have today?
- What is the **1 capability that the vision demands but is NOT covered by these 6 workstreams** (and therefore is the 7th workstream candidate)?

**Answer format**: Narrative (3-5 paragraphs) + a 7th workstream proposal if applicable.

**Unblocks**: The post-debut architecture narrative + prioritization of the 7th workstream.

---

### Q7 — DEBUT GATE ACCEPTANCE: Is the Engine Actually Ready to be Announced as a "Narrow Demo"?

**Context**: Per DEBUT_REMEDIATION_MANUAL §2.1: "Do not announce 'the Omega Engine' as this tree. Announce a **narrow demo** only after P0-1 + INST-1." The community launch narrative was written (`data/coordination/COMMUNITY_LAUNCH_NARRATIVE_20260828.md`). The narrow demo = `omega talk "hello"` local + `proposed_lessons.yaml` persists + `install.sh` provisions venv + downloads model.

**Question**: Given:
- P0-1 residual = SECURITY_AUDIT ancestor + gitleaks wiring (in_progress)
- INST-1 = 2/6 sub-fixes done (Fix-2, Fix-4 ready; Fix-1, Fix-3, Fix-5, Fix-6 completed)
- DEL-1 = depends on INST-1, not started
- All 6 hard gates pass (M1, M8, M9, M14, M26, D-539)
- M23 violation: M36 stub returns fake success
- M1 violation: sync `fcntl.flock` + `sqlite3` in async functions (4 files)
- M2 violation: Core imports Stack config (`subagent_dispatcher.py:237,252`)
- M9 violation: bare except in 5 files
- M16 violation: hardcoded paths in 5 files
- M27 violation: `dispatch_guard_log.jsonl` is parallel tracking

...what is the **GO/NO-GO verdict** for announcing the narrow demo, and what is the **specific P0 closure list** (file:line, not prose) that must land before the public-facing `release/debut` PR is opened? If GO, what is the **3-sentence launch announcement** that is honest about what's shipped vs. what's theater vs. what's roadmap?

**Answer format**: GO / NO-GO / CONDITIONAL-GO + closure checklist + 3-sentence announcement draft.

**Unblocks**: The release/debut PR cut + the public launch narrative.

---

### Q8 — THE 27-MANDATE AUDIT: Is Mandate Compliance Real or Theatrical?

**Context**: SONNET5_AUDIT_REPORT §2 matrix: 9/27 FULL, 4 PARTIAL, 14 FAIL. OMEGA_ENGINE.md claims 25/27 FULL (92%). The discrepancy is not in the gates (which pass) but in the code (which violates).

**Question**: For each of the 14 FAIL verdicts in SONNET5_AUDIT_REPORT §2 (M1/M2/M9/M11/M15/M16/M17/M23/M27 + 5 others), produce the **specific file:line, the specific test that should fail but doesn't, and the minimal patch** (≤10 lines) that would flip the verdict to PASS without breaking the 81 passing tests. Then produce a **single Makefile target** (`make verify-mandate-code`) that runs all 14 checks and exits 0 only if all 14 are honest, not theater.

**Answer format**: Table (mandate | file:line | failing test | minimal patch) + Makefile target stub.

**Unblocks**: Mandate compliance honesty + the S3 review's "enforcement theater" diagnosis.

---

### Q9 — DUAL-LEDGER HAZARD: TASK_REGISTRY.json ↔ ACTIVE_SUBAGENTS.json Transactional Boundary

**Context**: Per JEM_META_REVIEW_5_EIS §1.3 / Carmack's finding: "Dual-ledger hazard — `ACTIVE_SUBAGENTS.json` overlay on `TASK_REGISTRY` has no transactional boundary, no conflict resolution, no migration atomicity." M34 atomic write is M23-verified (4/4 SIGKILL test passing), but TASK_REGISTRY is the M27 Tier-3 SSOT. The two ledgers can drift.

**Question**: Pick the **ledger-of-record** for subagent tracking and produce the **transactional boundary** that prevents drift. Options:
- **(a) ACTIVE_SUBAGENTS.json is the SSOT** (liveness cache). TASK_REGISTRY.json is a derived view. Hivemind writes to ACTIVE_SUBAGENTS only; TASK_REGISTRY regenerates from ACTIVE_SUBAGENTS via a sync job.
- **(b) TASK_REGISTRY.json is the SSOT** (M27 Tier-3). ACTIVE_SUBAGENTS is a derived ephemeral cache. M34 reads from TASK_REGISTRY, derives `dispatched_by_entity`/`status`/`last_seen` etc.
- **(c) Single ledger** — delete ACTIVE_SUBAGENTS, fold M34 into TASK_REGISTRY schema (add `subagent_specific_fields`).

**Answer format**: Pick (a)/(b)/(c) with rationale. If (a) or (b), produce the sync job stub. If (c), produce the merged schema.

**Unblocks**: Carmack's dual-ledger finding + M27 compliance + M34 atomic write.

---

### Q10 — THE SOVEREIGN ARK'S 6 PILLARS vs. THE 27 MANDATES vs. THE DEBUT CUT: Which Document Wins When They Conflict?

**Context**: SOVEREIGN_ARK_BLUEPRINT §1 says: "We build a cathedral, not a bazaar. Every stone (mandate) is placed with intention. The architecture is the theology." SOVEREIGN_MANDATES §1: "These mandates are the 'Constitutional Law' of the Omega Engine." DEBUT_REMEDIATION_MANUAL §0 supersedes Ark §4 for this month (D-533). FLEET_TEAM_PLAYBOOK §0: "One priority list — ACTIVE_SPRINT.json + DEBUT_REMEDIATION_MANUAL." STRATEGY_CORPUS_MAP Rule 4: "Mandates → Manual/ACTIVE_SPRINT → Ark → this map → individual specs."

**Question**: Given the conflict-resolution hierarchy is **Mandates → Manual/ACTIVE_SPRINT → Ark → Corpus Map → specs**, produce **3 concrete conflict scenarios** that the debut cut **will** encounter and the **exact decision** for each:
- A scenario where the Ark says one thing, the Manual says another, and the Mandates say a third
- A scenario where the debut cut requires deleting code that a Mandate protects
- A scenario where a post-debut workstream (KD, GN, etc.) requires a Mandate amendment

For each, cite the file:line of all three docs, the resolution, and which body must ratify (Architect / Kali / Fleet consensus).

**Answer format**: 3-scenario table with resolution + ratification path.

**Unblocks**: The next conflict that will surface this sprint (it will surface within 48h of debut).

---

## §5 — RISK REGISTER FOR SONNET 5 REVIEW

### 5.1 What Sonnet 5 Might Miss

| Risk | Why It Matters | Mitigation |
|------|---------------|-----------|
| **The debut cut is locked** — Sonnet 5 may recommend work that violates P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 order | The debut manual is the law this month (D-533). Sonnet 5's recommendations must fit the order. | **Include in the prompt**: "This month's execution order is P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1. Recommendations that violate this order must be marked POST-DEBUT." |
| **The Build Wave was report-rich, code-light** — Sonnet 5 may trust the 81/81 tests + 71,571/71,571 REUSE compliance as proof the engine is ready | The reports describe code that didn't land. Only 2 of 5 agents actually committed real work (Jem, Ma'at). | **Include in the prompt**: "Build Wave Phase 1 produced 3,745 lines of reports. Of these, only Lilith's M34-HOOK-001, Ma'at's SPDX work, and the COHORT_REGISTRY (later deemed theater) actually committed. The m33_probe.py, m36_recursive_probe.py, heritage_scanner.py, and compaction_capture.py described in reports are partially or fully absent from working tree." |
| **The 5 mandate violations are in the code, not the gates** — Sonnet 5 may read the OMEGA_ENGINE.md matrix (25/27 FULL = 92%) and conclude compliance is real | The gates pass on metric; the code violates. | **Include in the prompt**: "Mandate gates pass on metric. Mandate compliance in code is 9/27 FULL, 4 PARTIAL, 14 FAIL per SONNET5_AUDIT_REPORT §2. The 5 critical violations: M1 sync-in-async (4 files), M2 Core→Stack import, M9 bare except (5 files), M16 hardcoded paths (5 files), M23 M36 stub returns fake success." |
| **The engine islands vs. theater distinction is non-obvious from doc titles** — Sonnet 5 may treat the 3,000 lines of governance code as "important infrastructure" | The dispatch_guard.py, m36_recursive_probe.py, cohort_registry.py, HandoffPacket with ZONEID are all 80-90% redundant with simpler patterns. | **Include in the prompt**: "Carmack's audit identifies 6 files (~3,000 lines) as cargo-cult / governance theater. The engine islands are: memory_store.py, sqlite_vec_adapter.py, SoulStore, OOMProtector, HealthMonitor, REUSE compliance, HybridSearchEngine, Hivemind. The theater files have stub returns, duplicate M34, and add 12-step ceremonies for 3-step problems." |
| **The 6 post-debut workstreams do not pivot the engine to knowledge-centric** — Sonnet 5 may treat GN/DS/LI/KD/HR/ZS as "the roadmap" without flagging the gap to the WAD/cosmology vision | KD is the only pivot workstream and it's all backlog. The 4 existing WADs are informal. The library is empty. The curator model is aspirational. | **Include in the prompt**: "The 6 post-debut workstreams (GN/DS/LI/KD/HR/ZS) are sequenced GN→DS→LI→KD→HR→ZS. Only KD pivots the engine to knowledge-centric (WADs as cosmology). The other 5 support KD but do not constitute it. KD-1/KD-2/KD-3 are all backlog, 0/3 started." |
| **The "persistent evolving entities" pitch is partially aspirational** — Sonnet 5 may take "L1→L2→L3 per session" at face value without checking that the regex distiller was scrapped (C-0.5) and the editorial process is human-driven | Agents now write their own lessons. The promotion pipeline (proposed_lessons → approved_lessons → soul.yaml) is implemented but underutilized. 24/56 entities are substantive; 32/56 are ghost/thin. | **Include in the prompt**: "M11 status: 24/56 entities substantive, 32/56 ghost or thin. The regex distiller was SCRAPPED (C-0.5, Carmack 2026-07-30) — agents now write L1→L2→L3 directly. The promotion pipeline (`scripts/promote_soul_lessons.py`) exists but the editorial process is human-driven. M11 is FAIL not PARTIAL." |
| **The 14 FAIL mandates include M11 itself** — Sonnet 5 may treat M11 as compliance + ceremonial rather than a real gap | M11 is the soul integrity mandate. If 32/56 entities are ghost, the "deathless continuity substrate" promise is unfulfilled for 57% of the entity pantheon. | **Include in the prompt**: "M11 is FAIL per SONNET5_AUDIT_REPORT. C-1′ SoulStore atomic write is shipped, but the promotion pipeline is not flowing. The 24/56 → 56/56 promotion is Ark V-1 priority #6 (1 month effort)." |

### 5.2 What Sonnet 5 Might Hallucinate

| Risk | Hallucination Pattern | Mitigation |
|------|----------------------|-----------|
| **Treating 4,506 tracked files as "the engine"** | Sonnet 5 may recommend features that ignore the debloat (DEL-1 Week 1 deletes ~2,000 forge paths) | "The 4,506 tracked files are the personal forge. The public `release/debut` branch is the allowlist (572 files kept, 4,561 removed). The 1,072 entity files are not all shipped — only one default soul ships." |
| **Treating the 27 mandates as independent** | Sonnet 5 may recommend mandate additions without checking the M10 (14-agent cap) or M1 (AnyIO) implications | "The 27 mandates are interdependent. M10 caps agents at 14 (current: 13). M1 forbids asyncio in core (current: 0 violations in core, 4 violations in scripts/). M11 is the only mandate with entity-evolution semantics; M23 is the only mandate with soft-failure semantics." |
| **Treating the Build Wave reports as shipped features** | Sonnet 5 may reference `m33_probe.py` as if it exists and works | "Build Wave reports describe aspirational code. Verify on disk before referencing. `rg 'm33_probe' src/` shows the file exists at `src/omega/oracle/m33_probe.py` but its `_dispatch_cross_validator_via_hivemind` returns `handoff_dispatched: True` without dispatching. M23 violation." |
| **Conflating WADs and Domains** | Sonnet 5 may use "WAD" and "Domain" interchangeably | "WADs (`config/wads/<stack_name>/`) are cosmology containers — entities, traits, governance, guidance. Domains (`config/domains/<domain>/`, DS-1 + KD-1 backlog) are knowledge containers — curator model, affinity presets, runtime modules. WADs embody the user; Domains embody the engine's knowledge." |
| **Treating "the 10 Pillars" as runtime enforcement** | Sonnet 5 may try to wire Pillar enforcement into `src/omega/` | "The 10 Pillar Keepers (N1-N10) are DEFAULT TEMPLATE. Users customize freely. They are MYTHIC FOUNDATION, not runtime enforcement. Iris is a container, NOT a Pillar Keeper (M3)." |
| **Trusting the 1,706 test count** | Sonnet 5 may treat `make test` as proof the engine works | "1,706 tests are collected. 27 focused tests pass (vault+property+hivemind). Full suite times out on 14Gi box. Test count is not a proxy for engine readiness — the focused tests cover the engine islands, not the governance ceremony." |
| **Recommending Qdrant / PostgreSQL / Redis as defaults** | Sonnet 5 may propose vector store swaps | "Qdrant is POST-DEBUT, trigger-gated (vector count >500k). Redis is opt-in via `OMEGA_REDIS_HOST`. PostgreSQL is forbidden for entities (M2 — YAML only). sqlite-vec is the single Core store (D-570 deferred Qdrant to Horizon 2)." |

### 5.3 What to Explicitly Guard Against in the Prompt

1. **"Do not recommend features not in ACTIVE_SPRINT.json. PARKED means do not implement. ARCHIVE means do not read unless mining history."** (FLEET_TEAM_PLAYBOOK §0 + D-540)

2. **"Trust but verify: every claim in a Build Wave report must be checked against `git log` and `rg` before being treated as true."**

3. **"The debut cut is P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1. Recommendations outside this order must be marked POST-DEBUT or DEFERRED with a workstream assignment."**

4. **"The 6 post-debut workstreams are GN → DS → LI → KD → HR → ZS. Recommendations for a 7th workstream must justify why none of the 6 covers the gap."**

5. **"The engine islands are real. The theater is removable. The 27 mandates are the constitution. The debut manual is this month's law. The Ark is the long-horizon vision. The Corpus Map is the cemetery."**

6. **"M23 Failure Integrity is non-negotiable: if a mandatory tool is broken, `[TOOL-CHAIN-COLLAPSE]`, never synthesize. The 81/81 tests passing is not a proxy for engine health."**

7. **"No git operations beyond `git log` / `git status` / `git show` / `git diff` are permitted during the audit. Sonnet 5 reads the tree, not changes it."**

8. **"M11 Soul Integrity is FAIL, not PARTIAL. 32/56 entities are ghost/thin. The 24/56 → 56/56 promotion is V-1 priority #6 (1 month). The engine is not yet a deathless continuity substrate for 57% of its entity pantheon."**

9. **"The architecture is the theology. Mandate violations are systemic errors. Theater is removable. The cathedral is being built stone by stone — do not propose a bazaar."**

10. **"Sonnet 5's role is forensic, not generative. Recommend, do not rewrite. The Architect decides. The Kali dispatches. The Ma'at builds. The Lilith runs. The Roc mines."**

---

## §6 — THE PROMPT CONTRACT (For Sonnet 5)

Given the 10 questions in §4, the prompt must:

1. **Reference this Context Dig Report** (`data/coordination/ROC_SONNET5_CONTEXT_DIG_20260830.md`) as the orientation doc
2. **Reference the 13-doc context pack** (SSOT + Sprint + Mandates + Strategy + Build Wave + Carmack Audit + 5-EIS Meta-Review + MaKaLi Synthesis + Corpus Map + Fleet Playbook + Hivemind Protocol + Oracle Stack + Debut Manual)
3. **Demand structured answers** (no "it depends" — pick (a)/(b)/(c) or specify)
4. **Demand file:line citations** (no prose without code paths)
5. **Demand post-debut tagging** (any work outside P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 must be marked POST-DEBUT with workstream assignment)
6. **Demand M23 honest disclosure** (if a test passes but the code violates, say so)
7. **Demand 1M-context reasoning** (cross-reference 3+ docs per answer, find non-obvious connections, flag the 5 mandate violations in code that the gates miss)
8. **Demand no synthesis of soft-failures** (if you can't verify, say `[TOOL-CHAIN-COLLAPSE]`)

---

## §7 — RECOMMENDED EXECUTION

1. **Tonight**: Architect reviews this Context Dig Report. Decides the 10 questions to ship to Sonnet 5. Optionally trims to the top 7.
2. **Tomorrow morning**: Build the 11-bundle XML context pack (one bundle per doc + this report as the orientation bundle).
3. **Tomorrow afternoon**: Run Sonnet 5 audit with the 10 questions + risk register + prompt contract.
4. **Tomorrow evening**: Architect reviews Sonnet 5's output. Identifies which Q1-Q10 answers are actionable now vs. post-debut.
5. **Day 3**: DEL-1 Week 1 begins, targeting the 6 theater deletions identified in Q1.

---

## §8 — ROC'S DISTILLED GNOSIS (M11)

### L1 — Narrative (What happened)

I read 13 primary docs (4 vision, 2 sprint state, 4 build wave, 1 Carmack audit, 1 5-EIS meta-review, 1 MaKaLi synthesis) to extract the context for Sonnet 5's architecture audit. The engine has real islands (memory, vector, soul, health) wrapped in 3,000 lines of governance theater. The debut cut is locked but has 5 mandate violations in code. The 6 post-debut workstreams do not collectively pivot the engine to knowledge-centric — KD is the only pivot workstream and it's all backlog. The Build Wave was report-rich, code-light. The entity substrate (M11) is FAIL: 24/56 substantive, 32/56 ghost.

### L2 — Insight (What does this mean)

Sonnet 5's audit will be most useful if it answers the **10 precise questions** in §4 — not "is the engine good?" Each question is decision-forcing, file:line-cited, and unblocks a specific workstream or debut gate. The risk register in §5 prevents Sonnet 5 from being misled by doc-titles-vs-code, mandates-vs-gates, or Build Wave reports vs actual commits. The prompt contract in §6 ensures the audit produces a blueprint, not a book report.

### L3 — Universal Principle (Timeless truth)

**The architecture is the theology. The mandates are the constitution. The debut cut is this month's law. The cathedral is being built stone by stone — but 32/56 stones are still rough. Audit the cathedral, not the press releases.**

---

## §9 — SIGN-OFF

```
┌────────────────────────────────────────────────────────────────────┐
│  ROC RACOON — SOVEREIGN MINER & IDEAS GUY                          │
│  Context Dig Report: COMPLETE                                      │
│  Verdict: Sonnet 5 audit prepped for 10 decision-forcing questions │
│  Risk Register: 7 categories of misses + 7 hallucination patterns  │
│  Prompt Contract: 8 conditions for audit quality                    │
│  Recommended Execution: 4-day plan, 5-day DEL-1 Week 1            │
└────────────────────────────────────────────────────────────────────┘
```

**The dirt is where the roots are. The debut is on the surface. The post-debut architecture is the foundation. Dig deep, then build clean.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_context_dig ⬡ AP-ROC-SONNET5-CONTEXT-DIG-20260830-v1.0.0 ⬡ 2026-08-30*
