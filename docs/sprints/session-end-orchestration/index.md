---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "sprint_plan"
document_id: "sprint-session-end-orchestration-20260730"
version: "1.0.0"
title: "Sprint: Session-End Orchestration + Local Worker Pool Integration"
ap_token: "AP-SPRINT-SESSION-END-ORCH-v1.0.0"
date: "2026-07-30"
duration_days: 5
phase: "Carmack Pivot — Phase 1-2 Execution"
status: "ACTIVE"
owner: "KALI"
priority: "P0"
tags: [sprint, session-end, distillation, wrapper, local-worker-pool, olvwm]
depends_on: ["data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md"]
blocks: []
acceptance_gates:
  - "opencode wrapper: queries DB, exports OPENCODE_SESSION_ID/ENTITY/MODEL after exit"
  - "session_end.py: calls Oracle SoulDistillationPipeline with exported transcript"
  - "SoulDistiller uses local LLM (via Roc's Worker Pool) for L1/L2/L3 extraction"
  - "proposed_lessons.yaml populated with real L1/L2/L3 from local inference"
  - "opencode-sessions-explorer plugin installed and operational"
  - "Roc Phase 0: make test passes, omega talk returns native-gguf"
cross_references:
  - "docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md"
  - "docs/research/R_SESSION_END_WRAPPER_PATTERN_20260730.md"
  - "data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md"
  - "data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md"
  - "SOVEREIGN_MANDATES.md"
  - "AGENTS.md"

llm_metadata:
  token_budget: 16000
  target_audience: "kali, roc_racoon, opencode"
  reading_level: "technical"
  summary: "Execute Session-End Orchestration pivot: wrapper DB integration, semantic distillation pipeline, and Roc's Local Worker Pool integration. 3 parallel tracks over 5 days."
  chunk_strategy: "section_per_topic"
---

# 🔱 Sprint: Session-End Orchestration + Local Worker Pool Integration

**AP Token**: `AP-SPRINT-SESSION-END-ORCH-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sprint ⬡ ACTIVE

**Date**: 2026-07-30
**Duration**: 5 days (2026-07-30 → 2026-08-04)
**Phase**: Carmack Pivot — Phase 1-2 Execution

---

## §1 Sprint Objective

**Execute the Session-End Orchestration pivot: fix the broken distillation pipeline by replacing regex with local LLM inference, using OpenCode's SQLite DB as transcript SSOT and Roc's Local Worker Pool as sovereign execution substrate.**

**Three parallel tracks**:
- **Track A (Kali)**: Phase 1 — Wrapper DB Integration (`opencode db` query → env vars → `session_end.py`)
- **Track B (Kali → Roc dep)**: Phase 2 — Semantic Distillation Pipeline (local LLM via Worker Pool)
- **Track C (Roc)**: Phase 0 — 4 Pipe Fixes → working local inference

---

## §2 Research Corrections (2026-07-30 Web Deep Dive)

### Critical Finding 1: Oracle SoulDistiller is NOT intelligent
The Oracle `SoulDistiller` has a **good pipeline infrastructure** but **regex extraction**. Key salvageable components:
- `SessionClassifier` — novelty/decision detection (keep)
- `SovereigntyScorer` — 5-factor quality scoring (keep)
- `SoulDistillationPipeline` — Classify → Distill → Score → Store (keep as framework)
- `SoulDistiller._extract_narrative()` — **regex-based, replace with LLM**
- `SoulDistiller._distill_insight()` — **regex-based, replace with LLM**
- `SoulDistiller._extract_principle()` — **regex-based, replace with LLM**
- `SoulDistiller.append_to_soul()` — writes via USM (keep, but verify USM works)

**Decision**: Rewrite `SoulDistiller.distill_session()` to accept LLM-generated content. Keep the pipeline wrapper (classifier → scorer → store).

### Critical Finding 2: opencode-sessions-explorer CONFIRMED EXISTS
- GitHub: `iamironz/opencode-sessions-explorer` (MIT, 14 commits, created 2026-06-13)
- **18 tools**: 17 read-only + 1 write (unarchive-session)
- Install: `"plugin": ["opencode-sessions-explorer"]` in opencode.json
- Requires: `"~/.local/share/opencode/**": "allow"` in `external_directory` permissions
- Auto-installed by OpenCode on startup via Bun (no separate npm install)
- **Needed setup**: `bunx opencode-sessions-explorer-check-deps` then `bunx opencode-sessions-explorer-bulk-export`
- **Note**: This plugin gives the *running model* tools for session recall. It does NOT help with post-exit distillation — the wrapper-based approach is still correct.

### Critical Finding 3: opencode CLI export limitation
- `opencode export <sessionID>` exports ONLY the root session — **subagent tree NOT included**
- `opencode db [query]` supports raw SQL with `--format json` or `--format tsv`
- `opencode db path` prints database path
- **Implication**: For multi-agent sessions, we need SQL queries on the DB, not just `opencode export`

### Critical Finding 4: opencode.json plugin configuration
- `"plugin"` array accepts: strings (`"package-name"`), tuples (`["package-name", {...options}]`), or objects (`{"package": "...", "options": {...}}`)
- npm plugins auto-installed via Bun on startup
- `external_directory` permissions control filesystem access

---

## §3 P0 Tickets (Must Complete)

### Track A: Wrapper DB Integration (Kali)

| ID | Ticket | Effort | Status | Depends On |
|----|--------|--------|--------|------------|
| **W-1** | Wrapper queries `opencode db` for session metadata after exit | 2h | 🔴 PLANNED | None |
| **W-2** | Export OPENCODE_SESSION_ID, OPENCODE_ENTITY, OPENCODE_MODEL to env | 1h | 🔴 PLANNED | W-1 |
| **W-3** | Test: normal exit, Ctrl+C, kill -TERM produce correct env vars | 1h | 🔴 PLANNED | W-2 |

### Track B: Semantic Distillation Pipeline (Kali → Local Worker Pool)

| ID | Ticket | Effort | Status | Depends On |
|----|--------|--------|--------|------------|
| **D-1** | Rewrite SoulDistiller.distill_session() for LLM input | 3h | 🔴 PLANNED | W-3 |
| **D-2** | Integrate Oracle SoulDistillationPipeline into session_end.py | 2h | 🔴 PLANNED | D-1 |
| **D-3** | Wire local LLM call via ProviderFabric (proxy for Worker Pool) | 3h | 🔴 PLANNED | D-2, Roc Phase 0 |
| **D-4** | Test: session end → proposed_lessons.yaml populated | 1h | 🔴 PLANNED | D-3 |

### Track C: Roc's 4 Pipe Fixes (Roc)

| ID | Ticket | Effort | Status | Depends On |
|----|--------|--------|--------|------------|
| **P0-1** | Fix 0.1: `providers.py:352-353` → type_k=None, type_v=None | 0.5h | 🔴 PLANNED | None |
| **P0-2** | Fix 0.2: `remote_provider.py:223` → add logit_bias, repetition_penalty, **kwargs | 0.5h | 🔴 PLANNED | None |
| **P0-3** | Fix 0.3: Priority-first routing in model_gateway.py (Option C) | 1h | 🔴 PLANNED | None |
| **P0-4** | Fix 0.4: `providers.py:482` → use models.yaml context_window | 0.5h | 🔴 PLANNED | None |
| **P0-5** | Update tests: test_providers.py:324-328 for type_k=None | 0.5h | 🔴 PLANNED | P0-1 |
| **P0-6** | Integration test: omega talk "hello" → native-gguf response | 1h | 🔴 PLANNED | P0-1..P0-5 |

### Shared

| ID | Ticket | Effort | Status | Depends On |
|----|--------|--------|--------|------------|
| **S-1** | Install opencode-sessions-explorer plugin in opencode.json | 0.5h | 🔴 PLANNED | None |
| **S-2** | Run bunx opencode-sessions-explorer-check-deps | 0.5h | 🔴 PLANNED | S-1 |
| **S-3** | Run bunx opencode-sessions-explorer-bulk-export | 0.5h | 🔴 PLANNED | S-2 |
| **S-4** | Update AGENTS.md with plugin instructions | 0.5h | 🔴 PLANNED | S-3 |

---

## §4 Redesigned Architecture (Post-Research Correction)

```
┌────────────────────────────────────────────────────────────────────┐
│  SESSION END                                                        │
│  (process exits, wrapper catches via waitpid)                       │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  WRAPPER DB INTEGRATION (Phase 1)                                   │
│  .opencode/wrapper.sh                                               │
│  ├── opencode db "SELECT id, agent, model ... ORDER BY id DESC LIMIT 1"│
│  ├── --format json → parse session_id, entity, model               │
│  ├── export OPENCODE_SESSION_ID, OPENCODE_ENTITY, OPENCODE_MODEL   │
│  └── exec python .opencode/hooks/session_end.py                    │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  TRANSCRIPT RETRIEVAL                                               │
│  session_end.py                                                     │
│  ├── opencode export <SESSION_ID> --format json > /tmp/transcript.json│
│  └── Parse JSON → extract user/assistant messages + tool calls     │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  DISTILLATION (Phase 2 — via local LLM)                            │
│  session_end.py → Oracle SoulDistillationPipeline                  │
│  ├── Stage 1: SessionClassifier (keep — novelty gate)              │
│  ├── Stage 2-3: LLM-driven L1/L2/L3 extraction                    │
│  │   └── Calls NativeGGUFProvider (via ModelGateway or Worker Pool)│
│  ├── Stage 4: SovereigntyScorer (keep — quality gate)             │
│  └── Stage 5: append_to_soul() → proposed_lessons.yaml            │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  AGENT MEMORY (Phase 3 — in-session)                               │
│  opencode-sessions-explorer plugin                                  │
│  └── 18 tools for recall, search, cost analysis                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## §5 Dependency Graph

```
TIMELINE: DAY 1───────DAY 2───────DAY 3───────DAY 4───────DAY 5
           
KALI:     W-1 ──→ W-2 ──→ W-3     D-1 ──→ D-2 ──→ D-3 ──→ D-4
           │                             ↑           ↑
ROC:      P0-1,P0-2 ──→ P0-3,P0-4,P0-5 ──→ P0-6 ──→ LocalWorkerPool
           │                             │
SHARED:   S-1,S-2 ──→ S-3,S-4           │
           └─────────────────────────────┴──→ Integration Test
```

---

## §6 Files to Modify

| File | What | Phase |
|------|------|-------|
| `.opencode/wrapper.sh` | Add DB query + env export after OpenCode exits | W-1, W-2 |
| `.opencode/hooks/session_end.py` | Call Oracle SoulDistillationPipeline with exported transcript | D-2, D-3 |
| `src/omega/oracle/soul_distiller.py` | Rewrite `distill_session()` for LLM input; keep pipeline infrastructure | D-1 |
| `src/omega/oracle/providers.py:352-353` | Fix 0.1: type_k=None default | P0-1 |
| `src/omega/oracle/backends/remote_provider.py:223` | Fix 0.2: add **kwargs | P0-2 |
| `src/omega/oracle/model_gateway.py` | Fix 0.3: priority-first routing | P0-3 |
| `src/omega/oracle/providers.py:482-495` | Fix 0.4: context_window from models.yaml | P0-4 |
| `tests/test_providers.py:324-328` | Fix 0.5: Update for type_k=None | P0-5 |
| `opencode.json` | Add `"opencode-sessions-explorer"` to plugin array | S-1 |
| `AGENTS.md` | Add plugin instructions | S-4 |
| `docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md` | Update with research corrections | S-4 |

---

## §7 Acceptance Gates

### Gate 1: Wrapper Works (W-1..W-3)
- [ ] `opencode db --format json "SELECT id FROM session ORDER BY id DESC LIMIT 1"` returns valid JSON
- [ ] `.opencode/wrapper.sh` exports `OPENCODE_SESSION_ID`, `OPENCODE_ENTITY`, `OPENCODE_MODEL`
- [ ] Env vars correctly populated on normal exit, Ctrl+C, kill -TERM

### Gate 2: Distillation Pipeline Works (D-1..D-4)
- [ ] `session_end.py` calls `SoulDistillationPipeline.run()` with exported transcript
- [ ] `SoulDistiller.distill_session()` accepts LLM-generated content
- [ ] `SovereigntyScorer` correctly evaluates LLM output
- [ ] `proposed_lessons.yaml` entries appear after session end
- [ ] `make test` passes

### Gate 3: Local Inference Works (P0-1..P0-6)
- [ ] `omega talk "What model are you?"` → response from Qwen3-1.7B via `native-gguf`
- [ ] Provider name in response is `native-gguf` (M22 provenance)
- [ ] `make test` passes (276+ tests)

### Gate 4: Plugin Operational (S-1..S-4)
- [ ] `opencode-sessions-explorer` in plugin array
- [ ] `bunx opencode-sessions-explorer-check-deps` passes
- [ ] `bunx opencode-sessions-explorer-bulk-export` succeeds

---

## §8 Key L3 Principles (From Research)

- **L3-Distillation-Requires-Semantic-Substrate**: Regex cannot extract universal principles from transcripts. The AI that generated the thoughts is the only entity capable of summarizing the principles behind them. Distillation must be an LLM call, not a text transformation.
- **L3-Transcript-SSOT-Is-External**: Do not duplicate raw conversation storage. OpenCode's SQLite DB (WAL, crash-safe, queryable) is the undisputed SSOT.
- **L3-Plugin-API-Is-Not-Lifecycle**: No event fires after process exit. Post-exit work MUST live in a wrapper.
- **L3-CLI-Export-Has-Limits**: `opencode export` does not export subagent trees. For full multi-agent extraction, use `opencode db` SQL queries directly.
- **L3-Pipeline-Infrastructure-Precedes-Intelligence**: The Oracle SoulDistiller's pipeline (Classifier → Pipeline → Scorer → Store) is salvageable. Only the extraction layer needs replacement. Don't rewrite what works — replace only the broken layer.

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sprint ⬡ 2026-07-30*
