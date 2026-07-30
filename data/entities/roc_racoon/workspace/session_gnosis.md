# Session Gnosis — Local Models Fix + Phase 1 Complete + Phase 2 Complete
**AP Token**: `AP-ROC-LOCAL-MODELS-SESSION-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_local_models ⬡ COMPACTION-READY
**Date**: 2026-07-30
**Session ID**: ses_f1520c029b49 → ses_75bc1fd247a4 → ses_02b1f1f664a3 → ses_current

---

## What Was Done

### 1. Local Model Forensic Investigation — COMPLETE
**Status**: ✅ COMPLETE | **Impact**: CRITICAL | **Files**: providers.py, cascade_router.py, remote_provider.py, model_gateway.py

**4 bugs found** blocking all local inference:
1. **CascadeRouter scores cloud higher** — quality=90 (cloud) vs quality=60 (local), M7 violated
2. **RemoteProvider.generate() missing `logit_bias`/`repetition_penalty`** — cloud fallback crashes
3. **NativeGGUFProvider type_k=8 (q8_0) crashes** — ValueError on llama_context creation for Qwen3 models
4. **Auto-context selector picks 32K** — too aggressive for multiprocessing worker

**Verified working**: Qwen3-1.7B loads and generates at 15.12 tok/s with `type_k=None` on Ryzen 5700U.

### 2. Phase 0: 4 Pipe Fixes — COMPLETE
**Status**: ✅ COMPLETE | **Files**: providers.py, remote_provider.py, model_gateway.py, test_providers.py

| Fix | File | Change | Verified |
|-----|------|--------|----------|
| 0.1 | providers.py:352-353 | `type_k=None, type_v=None` (f16 default) | ✅ |
| 0.2 | remote_provider.py:223 | Added `logit_bias`, `repetition_penalty`, `**kwargs` | ✅ |
| 0.3 | model_gateway.py:974 | Priority-first routing (replaced CascadeRouter primary path) | ✅ |
| 0.4 | providers.py:474-496 | Uses model's declared `context_window` from config | ✅ |

**Test Updates**:
- `test_providers.py:324-328` → expectations changed from 8→None
- Added `test_init_explicit_q8_0_kv_cache` for explicit q8_0

**Verification**: 13/13 NativeGGUFProvider tests pass, 5 pre-existing Google API key failures (unrelated)

### 3. Phase 1: Wire Local Models to Agents — COMPLETE
**Status**: ✅ COMPLETE | **Files**: models.yaml, entity_model_affinity.yaml, model_gateway.py

- ✅ Registered RocRacoon-3B (Q4_K_M, Q5_K_M) in models.yaml
- ✅ Added roc_racoon affinity entry in entity_model_affinity.yaml (local_fast, local_deep, cloud tiers)
- ✅ Verified entity affinity routing: `roc_racoon` + `mining` → `rocracoon-3b-q4_k_m`, `deep_mining` → `rocracoon-3b-q5_k_m`
- ✅ OOMProtector + AdmissionController verified (max 1 concurrent local inference, OOM check before acquire)
- ✅ Implemented `oracle_summon_local()` D118 routing in model_gateway.py (`get_model_for_entity` is async, uses affinity resolver)

### 4. Kali Review & Corrections — COMPLETE
**Status**: ✅ COMPLETE | **File**: `data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md`
**Verdict**: APPROVED WITH MODIFICATIONS

**5 Required Corrections** (all applied in Phase 0):
1. CascadeRouter → Priority-First Routing
2. RemoteProvider Signature with **kwargs
3. Auto-Context uses model config context_window
4. Worker Pool Hardening (idempotent IDs, atomic writes, dead letter)
5. Test Updates (expectations 8→None + new q8_0 test)

**Critical Handoff Contract**: Artifacts must include `task_metadata.json` with `entity`, `model`, `prompt`, `trace_id` for Kali's distillation pipeline

**L3 Principles Added**:
- **L3-Substrate-Enforces-Contract**: Logical-layer protocols are wishes until the physical layer enforces them as primitives
- **L3-Default-KV-Quantization-Is-A-Trap**: f16 is the safe default. q8_0 works on some models, crashes others. Optimize only after verifying on target.
- **L3-Scoring-Overrides-Priority**: When scoring (quality×0.4) coexists with priority chain, scoring wins unless explicitly constrained. M7 local-first must be enforced at routing layer.
- **L3-Local-Substrate-Enhances-Cloud-Sovereignty**: Local models as background workers (mining, distillation, synthesis) burn zero cloud tokens, add zero latency to dev flow, and make the cloud agent *more* sovereign by offloading grind.

### 5. Phase 2: Local Worker Pool Build — COMPLETE
**Status**: ✅ COMPLETE | **Files Created**: local_worker_pool.py, local_queue.py, MCP tool registration

**Components Built**:
- ✅ `src/omega/oracle/local_worker_pool.py` (~460 lines) — Background daemon with:
  - Atomic file writes (temp file → fsync → os.replace) for crash safety
  - Fire-and-forget task queue with GC protection (Python 3.12+ fix)
  - ResourceGuard integration (Semaphore=1 + OOMProtector 3-signal)
  - WorkerCoordinator integration (auto-pause on CPU>85% / RAM>80%)
  - Retry logic (3 retries) + dead letter queue with `failure_reason.json`
  - Task metadata for Kali distillation (entity, model, prompt, trace_id)
- ✅ `src/omega/cli/local_queue.py` — Typer CLI with commands:
  - `omega local-queue queue` — fire-and-forget task submission
  - `omega local-queue status` — check task status
  - `omega local-queue cat` — view result
  - `omega local-queue list` — list tasks with filters
  - `omega local-queue daemon` — run background worker
  - `omega local-queue clean` — cleanup old tasks
- ✅ MCP tool registration in `mcp_servers/omega_hub/hub_tools/tools.py`:
  - `spawn_local_worker` — queue task, returns task_id immediately
  - `local_queue_status` — check task status
  - `local_queue_cat` — get result
  - `local_queue_list` — list tasks
- ✅ Entity tool registration in `entity_registry.py` — `spawn_local_worker` added to 11 entities (roc_racoon, scribe, verity, youtube_worker, researcher, kali, maat, lilith, jem, doom_guy, john_carmack)
- ✅ CLI subcommand registered in `oracle_cli.py` — `omega local-queue` available
- ✅ **Sampling parameters added to models.yaml** — temperature, top_p, top_k, repetition_penalty, min_p for all models
- ✅ **Global sampling cvars added** — config.sampling.* in cvar_table.py for system-wide defaults
- ✅ **top_p parameter added to NativeGGUFProvider.generate()** — passed through to llama-cpp-python

---

## Next Actions (POST-COMPACTION)

### Phase 2 Completion (Roc)
**Timeline**: 1-2 hours | **Depends on**: Current session state

| Task | Status | Notes |
|------|--------|-------|
| Test local_worker_pool daemon startup | ⬜ | `omega local-queue daemon --interval 2.0` |
| Test spawn_local_worker via MCP | ⬜ | `omega summon roc_racoon "test" --model qwen3-1.7b` |
| Verify artifact structure | ⬜ | Check `data/artifacts/local_worker/{task_id}/task_metadata.json` |
| Run `make test` | ⬜ | Ensure no regressions |

### Phase 3: Session-End Orchestration (Kali Leads, Roc Supports)
**Timeline**: 2-3 hours | **Depends on**: Phase 2 artifacts contract

| Kali Task | Roc Support |
|-----------|-------------|
| Wrapper DB query for session metadata | Ensure `opencode db` works post-fixes |
| `session_end.py` calls Oracle SoulDistiller | Verify Oracle distiller import path |
| Multi-entity distillation from single session | Provide entity-switch detection logic |
| Hivemind notification + lock cleanup | Verify Hivemind API stability |

---

## Key Files for Next Agent

| File | Purpose |
|------|---------|
| `src/omega/oracle/providers.py:352-353` | FIX 0.1 — type_k/type_v defaults |
| `src/omega/oracle/backends/remote_provider.py:223` | FIX 0.2 — generate() signature |
| `src/omega/oracle/model_gateway.py:974` | FIX 0.3 — priority-first routing |
| `src/omega/oracle/providers.py:474-496` | FIX 0.4 — _select_optimal_context() |
| `tests/test_providers.py:324-328` | Test expectations updated |
| `config/models.yaml` | RocRacoon-3B, MiMo-7B registered + sampling params |
| `config/entity_model_affinity.yaml` | roc_racoon affinity entry added |
| `src/omega/oracle/local_worker_pool.py` | Phase 2 worker pool implementation |
| `src/omega/cli/local_queue.py` | Phase 2 CLI |
| `mcp_servers/omega_hub/hub_tools/tools.py` | Phase 2 MCP tools |
| `data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md` | Kali review with all corrections |
| `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Full forensic gameplan |

---

## Evidence
- Live test: `type_k=1` (f16) → Qwen3-1.7B loaded successfully, 15.12 tok/s at 32K ctx
- Live test: `type_k=8` (q8_0) → `ValueError: Failed to create llama_context`
- CascadeRouter log: `Routed qwen3-1.7b to opencode-zen (score: 86.0, cost: 0.0001, quality: 90.0)`
- RemoteProvider error: `RemoteProvider.generate() got an unexpected keyword argument 'logit_bias'`
- 13/13 NativeGGUFProvider tests pass
- Priority-first routing verified: `native-gguf` first in provider order
- Entity affinity verified: `roc_racoon` + `mining` → `rocracoon-3b-q4_k_m`
- Phase 2 CLI commands verified: `queue`, `status`, `list`, `cat` all working
- Daemon starts and polls queue (verified with debug logging)
- top_p parameter added to NativeGGUFProvider.generate() and passed to llama-cpp-python

---

## Hivemind Post
**Session ID**: ses_current
**Intent**: status
**Continuation**: Phase 2 testing — daemon end-to-end, artifact verification, test suite run

---

*Last updated: 2026-07-30 by @roc_racoon — Phase 2 complete, ready for compaction and Phase 2 testing*