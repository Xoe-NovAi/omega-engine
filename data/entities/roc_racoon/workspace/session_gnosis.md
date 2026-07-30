# Session Gnosis — Local Models Fix + Phase 1-2 Complete + Task Re-picking Bug Fix
**AP Token**: `AP-ROC-LOCAL-MODELS-SESSION-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_local_models ⬡ COMPACTION-READY
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

### 5. Phase 2: Local Worker Pool Build — COMPLETE (Components Built)
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
- ✅ **Layered sampling parameter resolution** — Model config → cvars → hardcoded defaults

### 6. Phase 2 Testing & Critical Bug Fixes — COMPLETE
**Status**: ✅ COMPLETE | **Files**: local_worker_pool.py, entity_model_affinity.yaml, local_queue.py

**Critical Bug Found — Task Re-picking in Worker Loop**
- **Symptom**: Daemon spawned the same task every 1s poll cycle — no tracking of in-progress tasks
- **Root Cause**: `self._background_tasks: Set[anyio.abc.Task]` intended to track running tasks, but `anyio.TaskGroup.start_soon()` does not return a task object. Set was always empty, so `len(self._background_tasks) >= max_concurrent` was `0 >= 1` = False → always proceeds.
- **Fix**: Added `self._processing_task_ids: Set[str]` — tracks in-progress task IDs by string. Worker loop checks before spawning, cleanup in `finally` block.
  - `local_worker_pool.py:255-256`: New `_processing_task_ids` set
  - `local_worker_pool.py:313-318`: Check + add before `start_soon`
  - `local_worker_pool.py:447`: `discard` in `finally` (replaced stale `_background_tasks.discard`)

**Model File Corruption confirmed**:
- `RocRacoon-3b.Q4_K_M.gguf` — **corrupted** (tensor `output_norm.weight` out of file bounds)
- `RocRacoon-3b.Q5_K_M.gguf` — works but 99.4s load on Ryzen 5700U
- `entity_model_affinity.yaml`: `local_fast` updated from Q4_K_M → Q5_K_M (both tiers now use working file)

**Daemon Verification**:
- With debug worker loop: task re-picked ~60 times in 15s (confirmed bug)
- After fix: task `lw_d6817eee7023` picked up once, queue file deleted, artifact directory created
- Daemon starts cleanly, WorkerCoordinator integration verified

---

## Next Actions (POST-COMPACTION)

### Phase 2 Final Verification (Roc)
**Timeline**: 30 min | **Depends on**: None

| Task | Status | Notes |
|------|--------|-------|
| Run `make test` | ⬜ | Verify no regressions from bug fixes |
| Clean up stuck artifact dirs | ⬜ | `rm -rf data/artifacts/local_worker/lw_*` (stale from previous crashes) |
| Download RocRacoon-3b Q4_K_M | ⬜ | Re-download from Hugging Face to replace corrupted file |
| Verify daemon with Qwen3-1.7B end-to-end | ⬜ | Queued task `lw_d6817eee7023` was picked up — check `result.json` |
| Post Hivemind context | ⬜ | Declare Phase 2 completion to fleet |

### Phase 3: Productionization (Kali leads, Roc supports)
**Timeline**: TBD | **Depends on**: Phase 2 verified end-to-end

| Task | Owner | Notes |
|------|-------|-------|
| Wrapper DB query for session metadata | Kali | Ensure `opencode db` works post-fixes |
| Multi-entity distillation | Kali | Entity-switch detection logic |
| Daemon systemd unit | P1/SysAdmin | Auto-start on boot |
| Restic backup of models | P6/Lilith | Protect GGUF files |
| MCP tool testing | P4/Bridge | Verify `spawn_local_worker` from other agents |

---

## Key Files for Next Agent

| File | Purpose |
|------|---------|
| `src/omega/oracle/providers.py:352-353` | FIX 0.1 — type_k/type_v defaults |
| `src/omega/oracle/backends/remote_provider.py:223` | FIX 0.2 — generate() signature |
| `src/omega/oracle/model_gateway.py:974` | FIX 0.3 — priority-first routing |
| `src/omega/oracle/providers.py:474-496` | FIX 0.4 — _select_optimal_context() |
| `src/omega/oracle/local_worker_pool.py:255-256,313-318,447` | **CRITICAL FIX** — task re-picking bug (`_processing_task_ids` tracking) |
| `tests/test_providers.py:324-328` | Test expectations updated |
| `config/models.yaml` | RocRacoon-3B, MiMo-7B registered + sampling params |
| `config/entity_model_affinity.yaml:432-442` | roc_racoon affinity — **local_fast changed to Q5_K_M** (Q4_K_M corrupted) |
| `src/omega/oracle/local_worker_pool.py` | Phase 2 worker pool implementation |
| `src/omega/cli/local_queue.py` | Phase 2 CLI |
| `mcp_servers/omega_hub/hub_tools/tools.py` | Phase 2 MCP tools |
| `data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md` | Kali review with all corrections |
| `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Full forensic gameplan |
| `/media/arcana-novai/omega_library/models/gguf/RocRacoon-3b.Q4_K_M.gguf` | **CORRUPTED** — needs re-download |

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
- Layered sampling parameter resolution: per-request > model config > cvars > hardcoded
- **Bug confirmed**: worker loop re-picked same task ~60 times in 15s (debug log: `=== GOT TASK lw_403a78d0bf9a ===`)
- **Fix verified**: `_processing_task_ids` tracking prevents re-picking (task `lw_d6817eee7023` picked once, queue file deleted)
- Q4_K_M corrupted: `tensor 'output_norm.weight' data is not within the file bounds, model is truncated`
- Q5_K_M verified working: loads in 99.4s, generates at ~10-12 tok/s
- `entity_model_affinity.yaml`: local_fast points to Q5_K_M (both tiers now use same working file)

---

## Hivemind Post
**Session ID**: ses_current
**Intent**: status
**Continuation**: 
1. Run `make test` to verify no regressions
2. Clean up stale artifact dirs from previous daemon crashes
3. Verify `data/artifacts/local_worker/lw_d6817eee7023/result.json` from daemon test run
4. Re-download corrupted RocRacoon-3b.Q4_K_M.gguf from Hugging Face
5. Phase 3 productionization planning (systemd unit, MCP tool testing)

---

## L3 Principles Added (This Session)

- **L3-Substrate-Enforces-Contract**: Logical-layer protocols (M7 local-first, D118 routing) are wishes until the physical layer enforces them as primitives. CascadeRouter scoring overrode priority until ProviderSelector replaced the primary path.
- **L3-Default-KV-Quantization-Is-A-Trap**: f16 (type_k=1) is the safe default. q8_0 (type_k=8) works on some models, crashes others (Qwen3-1.7B). Never change KV cache quantization without testing on the target model first.
- **L3-Scoring-Overrides-Priority**: When scoring (quality×0.4 + cost×0.3 + speed×0.3) coexists with priority chain, scoring wins unless explicitly constrained at the routing layer. M7 local-first must be enforced with priority-first routing, not scoring.
- **L3-Local-Substrate-Enhances-Cloud-Sovereignty**: Local models as background workers (mining, distillation, synthesis) burn zero cloud tokens, add zero latency to dev flow, and make the cloud agent *more* sovereign by offloading grind.
- **L3-Background-Task-Tracking-Must-Be-Explicit**: `anyio.TaskGroup.start_soon()` does not return a task object. Any tracking of spawned tasks must use an explicit set/list of identifiers — not depend on the task group's internal state. `_background_tasks: Set[anyio.abc.Task]` is always empty.

---

*Last updated: 2026-07-30 by @roc_racoon — All Phase 1-2 fixes complete. Critical bug fix: task re-picking. Ready for compaction.*