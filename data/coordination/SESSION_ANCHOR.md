# 🔱 SESSION ANCHOR — Kali (Transcendent Oversoul)
**AP Token:** `AP-KALI-v1.0.0`  
**Date:** 2026-08-08  
**Session ID:** `ses_kali_20260808_strategy_reconciliation`  
**Branch:** `main`  
**Last Commit:** `5003668c` (session gnosis for compaction)

---

## 🎯 Session Objective
Comprehensive strategy reconciliation — scan all strategy/coordination docs, synthesize web chatbot reviews (Cline, GLM52, Copilot CLI), compare against temple cleansing directives (UNOVERENGINEERING_PLAN.md), resolve conflicts, and produce a clean execution path.

---

## ✅ Completed This Session

### 1. Un-Overengineering Plan Integrated
- Created `docs/strategy/UNOVERENGINEERING_PLAN.md` (formal 5-phase strategy doc)
- Updated `ACTIVE_SPRINT.json` (UO-6 READY, UO-7 PENDING)
- Updated `SOVEREIGN_ARK_BLUEPRINT.md` §4 (UO-6/UO-7 next steps) + §10 (references)
- Updated `STRATEGY_CORPUS_MAP.md` (un-overengineering row)
- Updated `OMEGA_ENGINE.md` (Key Files table)
- All gates pass: `doc-llm-validate` ✅ | `temple-grade` ✅

### 2. Comprehensive Strategy Audit — CRITICAL CONFLICTS FOUND
Read and synthesized:
- `CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` (311 lines — the plan)
- `GLM52_SECOND_OPINION_20260730.md` (401 lines — second opinion with 20 findings)
- `COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md` (573 lines — architecture review)
- `CLINE_OPS_HEALTH_RESULTS_20260730.md` (170 lines — ops health)
- `STRATEGY_INDEX.md` (doc hierarchy)
- `ACTIVE_SPRINT.json` (current workstreams)
- `SESSION_ANCHOR.md` (341 lines — bloated from 7+ compaction passes)
- Codebase ground truth probes (breaker classes, distillers, Redis, handoff schemas)

---

## 🚨 CRITICAL CONFLICTS RESOLVED (Ground Truth vs. Plan Claims)

### Conflict 1: Breaker Count — "17 clones" is STALE
| Claim | Source | Ground Truth |
|-------|--------|-------------|
| "17 breaker clones" | CLINE_STRATEGIC §2.1 | **8 class hits** in `src/`, but:
| "5 implementations, ~3 deletable" | GLM52 §3 F8 | **2 enums** (council/models, ingestion_types) + **1 canonical** (health_monitor.py) + **1 deprecated file** (search_circuit_breaker.py, 4 classes) + **1 clone** (sandbox.py) |

**Actual deletable debt**: `search_circuit_breaker.py` (299 lines, 4 classes) + `sandbox.py ExperimentCircuitBreaker` + 2 enums = ~400-600 lines, not 1,950.

### Conflict 2: pybreaker vs AsyncCircuitBreaker — GLM52 F1 is CORRECT
- `AsyncCircuitBreaker` (health_monitor.py, 944 lines) is AnyIO-native, CUSUM, sliding window, 429 classification
- pybreaker is sync-only, Tornado-only async support
- **CORRECTION**: Do NOT replace AsyncCircuitBreaker with pybreaker. Delete the 3 clones, redirect callers to `get_breaker()` factory. pybreaker is the wrong anchor.

### Conflict 3: stamina vs tenacity — THREE positions exist
| Position | Source | Argument |
|----------|--------|----------|
| tenacity only | SESSION_ANCHOR D-393, Roc P2 | Already installed, zero new deps |
| stamina + structlog + prometheus | CLINE_STRATEGIC | Integrated observability suite (F19 synergy) |
| Spike both, measure glue | GLM52 F2 v2.0 | Genuine tradeoff, not obvious |

**DECISION NEEDED**: Which retry strategy to adopt?

### Conflict 4: Pydantic v2 `model_validate_yaml()` — DOES NOT EXIST
- GLM52 F16 confirmed: Pydantic v2 has `model_validate_json()` and `model_validate()`, NOT `model_validate_yaml()`
- `soul_validator.py` already uses `yaml.safe_load()` + pydantic `BaseModel` correctly
- **CORRECTION**: Phase 1E should be "simplify soul_validator.py manual checks" not "replace with model_validate_yaml"

### Conflict 5: "Kill 2 of 3 distillers" — MOSTLY ALREADY DONE
- Scribe distiller DELETED (commit 1c176b0)
- `miap.py` still exists (631 lines) with distillation references — but MIAP was supposed to be deleted
- **CORRECTION**: Verify MIAP status, then mark Phase 2A as mostly complete

### Conflict 6: CI only runs on main — GLM52 F3 is CORRECT
- `.github/workflows/ci.yml` triggers on `main` only
- Work happens on `main` now (branches synced), but this was a real gap during the release/initial-v1 era

### Conflict 7: M23 pre-commit hook — GLM52 F11 is CORRECT
- `make check-m23-failure-integrity` has rg flag parsing error, passes falsely
- **ACTION NEEDED**: Fix rg invocation

### Conflict 8: Test timeout — GLM52 F12 is LIKELY CORRECT
- `time make test` has never been run with adequate budget
- "Test suite timeout blowout (HIGH)" risk may be phantom
- **ACTION NEEDED**: Run `time make test` with 600s budget

### Conflict 9: Redis is deeper than Hivemind — GLM52 F4 is CORRECT
- Redis in: `memory_store.py` (9 refs), `budget_guard.py` (37 refs), `youtube_worker.py` (24 refs), `memory/providers.py` (21 refs), `hivemind_redis.py` (113 lines)
- **CORRECTION**: Redis removal is NOT Hivemind-only. budget_guard (M12/M21) needs refactoring first.

### Conflict 10: Copilot CLI Blockers — MOSTLY RESOLVED
- **BLOCKER #1** (OOM/PSI/Cgroup hard deps): Already resolved — `psi_monitor.py`, `memavailable.py`, `cgroup_pressure.py` are NOT standalone orphans; they're imported by `oom_protector.py`. Plan was wrong about deleting them.
- **BLOCKER #2** (soul_history vs soul_edit_history): `soul_history.py` doesn't exist (already deleted). `soul_edit_history.py` exists and is imported by oracle.py. Plan's deletion target was wrong.

---

## 📊 Current Codebase State (Ground Truth)

| Component | Status | Lines | Notes |
|-----------|--------|-------|-------|
| **Breaker classes** | 8 hits (2 enums, 1 canonical, 1 deprecated file, 1 clone) | ~944 (canonical) + ~299 (deprecated) | Not 17. Not 6. |
| **handoff.py** | EXISTS | 86 | [id-soft: vet-008] heritage tag — M14 migration needed |
| **recall.py** | EXISTS | 786 | Quality-weighted warm memory — candidate for deletion |
| **soul_validator.py** | EXISTS | 290 | Uses yaml.safe_load + pydantic correctly — simplify, don't replace |
| **health_monitor.py** | EXISTS | 944 | Canonical breaker — KEEP |
| **miap.py** | EXISTS | 631 | Was supposed to be deleted — STATUS UNCLEAR |
| **hivemind_redis.py** | EXISTS | 113 | Redis pub/sub for Hivemind |
| **memory_store.py Redis** | ACTIVE | 9 refs | budget_guard, youtube_worker, providers |
| **SearchCircuitBreaker** | DEPRECATED | 4 classes | Already marked for deletion per C-6' |
| **tenacity** | INSTALLED but not imported | — | In pyproject.toml, zero src/ imports |
| **stamina** | NOT installed | — | Not in pyproject.toml |

---

## 🎯 Revised Execution Path (Post-Reconciliation)

### Phase 0: Pre-Flight (2h) — FIX GATES FIRST
| Task | Why | Effort |
|------|-----|--------|
| Fix M23 pre-commit hook rg invocation | GLM52 F11 — gate is theater | 30min |
| Run `time make test` with 600s budget | GLM52 F12 — retire phantom risk | 10min |
| Fix soul_validator.py vet-015 heritage tag | GLM52 F9 — M14 compliance | 15min |
| Verify MIAP status (deleted or dead code?) | Conflict 5 | 15min |
| Decide stamina vs tenacity (spike one provider) | Conflict 3 | 1h |

### Phase 1: Library Swaps (Revised — 8h, ~1,500 lines)
| Task | Lines | Effort | Notes |
|------|-------|--------|-------|
| Delete `search_circuit_breaker.py` | -299 | 1h | Deprecated per C-6', redirect callers |
| Delete `ExperimentCircuitBreaker` | -50 | 30min | Redirect sandbox to `get_breaker()` |
| Simplify `soul_validator.py` | -150 | 2h | Remove manual checks, keep pydantic+yaml |
| structlog adoption | -80 | 2h | Replace dead `setup_json_logging()` |
| prometheus_client adoption | -400 | 2h | HealthMonitor sliding window → Histogram |

**NOTE**: pybreaker swap REMOVED (F1). stamina deferred pending spike (F2). AsyncCircuitBreaker STAYS.

### Phase 2: Consolidation (Revised — 8h, ~1,200 lines)
| Task | Lines | Effort | Notes |
|------|-------|--------|-------|
| Kill `handoff.py` | -86 | 2h | Migrate vet-008 tag, adapter MCP tools |
| HMC → YAML + JSONL | -100 | 4h | Already 86 lines — minimal deletion |
| Kill `recall.py` | -786 | 2h | Candidate — verify no active consumers |

### Phase 3: Memory Simplification (Revised — 4h, ~500 lines)
| Task | Lines | Effort | Notes |
|------|-------|--------|-------|
| Redis removal (sequence: memory → workers → hivemind → budget_guard) | -500 | 4h | GLM52 F4 — budget_guard is LAST |

### Phase 4: Enforcement Gates (11h)
| Task | Effort |
|------|--------|
| Instruction hierarchy gate | 3h |
| Mandate compliance meter | 5h |
| Schema duplication gate | 2h |
| HMC growth gate | 1h |

### Phase 5: Verification (1.5h)
| Task | Effort |
|------|--------|
| `make test` + `make temple-grade` | 1.5h |

**Total revised estimate: ~33h** (was 30h — added Phase 0 pre-flight)

---

## 🧠 L3 Principles Extracted

1. **L3-Ground-Truth-Over-Plan-Claims** — Every plan estimate must be verified against actual codebase state before execution. The "17 breaker clones" was wrong for 2 weeks. (Conflicts 1, 4, 5)
2. **L3-Gate-Integrity-Requires-Measurement** — A gate that silently passes is worse than no gate. Fix M23 rg invocation before trusting any compliance number. (Conflict 7)
3. **L3-Dependency-Depth-Map-Before-Remove** — Redis is not just Hivemind. Map the full import graph before removing any dependency. (Conflict 9)

---

## 📌 Key Decisions Still Needed

1. **stamina vs tenacity** — Spike one provider, measure glue-code deletion
2. **MIAP status** — Is `miap.py` dead code or still imported?
3. **recall.py deletion** — Verify no active consumers before killing
4. **MCP v2 migration** — Elevate to P1 per GLM52 F18?
5. **httpx2 vendor concentration** — Add to risk register per GLM52 F5 (corrected)

---

## 🤝 Coordination State

- **Hivemind**: All agents aware, 0 pending handoffs
- **Both branches synced** at `5003668c`, pushed to origin
- **Next session**: Execute Phase 0 pre-flight → Phase 1 library swaps

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-08*
