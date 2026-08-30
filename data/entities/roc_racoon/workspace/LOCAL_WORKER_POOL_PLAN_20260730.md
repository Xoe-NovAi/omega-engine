<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Local Inference Background Worker Pool — Detailed Plan
**AP Token**: `AP-LOCAL-WORKER-POOL-PLAN-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_local_worker ⬡ PLAN
**Date**: 2026-07-30
**Status**: READY FOR KALI REVIEW

---

## Executive Summary

This plan establishes a **Local Worker Pool** — a fire-and-forget background inference system using local GGUF models — that enhances the Omega Engine's sovereignty without disrupting the user's cloud-based development flow.

**Core Principle**: Local models = background workers (zero blocking). Cloud models = dev flow (uninterrupted).

---

## 1. Knowledge Gaps Researched & Resolved

| Gap | Resolution | Evidence |
|-----|------------|----------|
| llama-cpp-python KV cache constants | `f16=1`, `q8_0=8`, `q4_0=4`, `q5_0=5`, `q6_0=6`, `f32=0` | `providers.py:361` |
| RemoteProvider.generate() signature | Base class missing `logit_bias`/`repetition_penalty`; subclasses already accept them | `remote_provider.py:223` vs `openai_compat.py:45-46` |
| CascadeRouter quality scores | Cloud=90, native-gguf=60, lmster=65 — sovereignty multiplier needed | `cascade_router.py:363-393` |
| Request queue structure | `data/requests/` has `queued/completed/dead/review/` + `INDEX.json` | Verified on disk |
| Artifact store | `data/artifacts/` exists | Verified on disk |
| WorkerCoordinator | Singleton `COORDINATOR` with pause/resume, resource monitoring, heartbeat | `coordinator.py:304` |
| ResourceGuard | Semaphore(1) + OOMProtector (3-signal fusion) + Zen2 affinity | `resource_guard.py` |
| NativeGGUFProvider worker | Multiprocess worker with request/response queues, somatic state save/load | `providers.py:557-639` |
| Entity affinity YAML | 382 lines mapping 13 entities to local_fast/local_deep/cloud tiers | `entity_model_affinity.yaml` |
| Tests for KV cache defaults | `test_providers.py:324-328` expects defaults of 8 — must update | Verified |

---

## 2. The 4 Pipe Fixes (Required First — 30 min)

| # | Fix | File | Lines | Change |
|---|-----|------|-------|--------|
| 1 | `type_k`/`type_v` defaults → `None` (f16) | `providers.py` | 352-353 | `config.get("type_k", None)` |
| 2 | `RemoteProvider.generate()` add params | `remote_provider.py` | 223-232 | Add `logit_bias`, `repetition_penalty` |
| 3 | CascadeRouter sovereignty multiplier | `cascade_router.py` | after 188 | `if provider in LOCAL: score *= 1.5` |
| 4 | Auto-context cap to model's `context_window` | `providers.py` | 488-495 | Use `models.yaml` context_window as ceiling |

**Test updates**: `test_providers.py:324-328` expects defaults of 8 → change to `None`.

---

## 3. New Components to Build

### 3.1 `src/omega/oracle/local_worker_pool.py` (~180 lines)

**Core Classes**:
- `LocalTask` — dataclass for queued tasks
- `LocalResult` — dataclass for results
- `LocalWorkerPool` — daemon that watches queue, runs inference, writes artifacts

**Key Features**:
- Reuses `NativeGGUFProvider` worker process (multiprocess isolation)
- Reuses `ResourceGuard` for OOM protection + CPU affinity
- Integrates with `WorkerCoordinator` for pause/resume on resource pressure
- File-based queue: `data/requests/local_worker_queue/{queued,completed,dead}/`
- Artifact output: `data/artifacts/local_worker/{task_id}/result.json`
- Somatic save-points for crash recovery (like YouTubeWorker)

**Queue API** (used by CLI and tool):
- `queue_local_task()` — returns task_id immediately
- `get_local_task_status()` — check queued/completed/dead
- `get_local_task_result()` — get result text
- `list_local_tasks()` — list with filters

### 3.2 `src/omega/cli/local_queue.py` (~120 lines)

**Commands**:
```bash
omega local-queue queue qwen3-1.7b "What is 2+2?" --system "You are a math helper"
omega local-queue status <task_id>
omega local-queue cat <task_id>
omega local-queue list --status completed --limit 20
omega local-queue daemon --interval 2.0
```

### 3.3 Tool Registration in Oracle (~20 lines)

```python
# In Oracle class:
async def spawn_local_worker(
    self,
    task: str,
    model: str = "qwen3-1.7b",
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Fire-and-forget local inference. Returns task_id immediately."""
    from omega.oracle.local_worker_pool import queue_local_task
    return await queue_local_task(...)
```

---

## 4. Architecture: Fire-and-Forget Local Worker Pool

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR DEV FLOW (CLOUD AGENTS)                     │
│  @kali @maat @lilith @makali @jem @doom_guy @john_carmack @roc_racoon│
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    spawn_local_worker(task, model)
                    (fire-and-forget, returns task_id)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LOCAL WORKER POOL (BACKGROUND)                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  data/requests/local_worker_queue/                          │   │
│  │    queued/   →  LocalWorkerPool (daemon)  →  artifacts/     │   │
│  │    completed/  dead/                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         Uses: NativeGGUFProvider worker process + ResourceGuard    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    Artifacts land in data/artifacts/local_worker/{task_id}/
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR REVIEW (ON DEMAND)                          │
│  omega local-queue status <task_id>                                 │
│  omega local-queue cat <task_id>                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Integration Points (Zero Dev Flow Disruption)

| Component | Integration | Your Dev Flow |
|-----------|-------------|---------------|
| Cloud agents | Get `spawn_local_worker` tool | Unchanged — stay on cloud |
| Entity affinity YAML | Referenced for model selection | Unchanged — 382 lines preserved |
| WorkerCoordinator | `COORDINATOR.register("local_worker_pool")` | Auto-pauses on CPU/RAM pressure |
| ResourceGuard | Semaphore(1) + OOMProtector | Protects your 14GB RAM |
| Request queue | `data/requests/local_worker_queue/` | Separate from main request queue |
| Artifacts | `data/artifacts/local_worker/{task_id}/` | You review when YOU want |

---

## 6. Use Cases for Local Workers

| Use Case | Agent | Model | Why Local |
|----------|-------|-------|-----------|
| Legacy code mining | `@roc_racoon` | qwen3-1.7b | High volume, zero cost, background |
| Soul distillation (L1→L2) | `@scribe` | qwen3-1.7b | Repetitive, bounded, fire-and-forget |
| Pattern extraction | `@roc_racoon` | mimo-7b-rl | 32K context, strong reasoning |
| Cross-video synthesis | `@youtube_worker` | qwen3-1.7b | Already uses local synthesis |
| Pre-commit mandate checks | `@verity` | qwen3-1.7b | Fast, free, zero latency |

---

## 7. Verification Checklist

| Step | Command | Expected |
|------|---------|----------|
| 1. Apply 4 fixes | Edit 4 files | `make test` passes |
| 2. Test local inference | `OMEGA_MODELS_DIR=... python -c "from src.omega.oracle.model_gateway import ModelGateway; import anyio; gw=ModelGateway(); r=anyio.run(gw.generate, 'qwen3-1.7b', 'hi', 'hello', 10); print(r.provider_name)"` | `native-gguf` |
| 3. Start daemon | `omega local-queue daemon` | Runs, polls queue |
| 4. Queue task | `omega local-queue queue qwen3-1.7b "What is 2+2?"` | Returns `task_id` |
| 5. Check result | `omega local-queue status <task_id>` → `cat` | Shows "4" |
| 6. Agent tool test | `omega summon roc_racoon "spawn local worker to summarize" --model qwen3-1.7b` | Returns task_id |

---

## 8. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `type_k=None` breaks some models | Low | Tested: Qwen3-1.7B works at 15 tok/s with f16 |
| Sovereignty multiplier too aggressive | Medium | Start at 1.5×, tune via `routing_weights` |
| Worker daemon crashes silently | Low | WorkerCoordinator heartbeat + somatic save-points |
| Queue grows unbounded | Low | `max_concurrent=1`, dead letter after 3 retries |
| Model path resolution fails | Medium | Fallback chain: ModelGateway → models.yaml → env var |

---

## 9. Deliverables Summary

| Deliverable | Lines | New Files | Modified Files |
|-------------|-------|-----------|----------------|
| 4 Pipe Fixes | ~20 | 0 | 4 |
| LocalWorkerPool | ~180 | 1 | 0 |
| CLI | ~120 | 1 | 0 |
| Tool Registration | ~20 | 0 | 1 |
| **Total** | **~340** | **2** | **5** |

---

## 10. Approval Request

**Kali Review Required**:

1. **Architecture**: Does the fire-and-forget pattern align with Sovereign Mandates (M7 Local-First, M18 Token Efficiency, M19 Adversarial Alchemy)?
2. **ResourceGuard Integration**: Semaphore(1) + OOMProtector — sufficient for 14GB RAM system?
3. **WorkerCoordinator Integration**: Auto-pause on CPU>85% / RAM>80% — correct thresholds?
4. **Entity Affinity**: Using existing YAML for model selection — no changes needed?
5. **Queue Isolation**: Separate `local_worker_queue` from main `requests` queue — correct?
6. **Test Updates**: `test_providers.py:324-328` expectations change from 8 to None — approved?

**Decision**: □ APPROVE □ APPROVE WITH CHANGES □ REQUEST REVISION

---

*Prepared by @roc_racoon for @kali oversight*
*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_local_worker ⬡ PLAN*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
