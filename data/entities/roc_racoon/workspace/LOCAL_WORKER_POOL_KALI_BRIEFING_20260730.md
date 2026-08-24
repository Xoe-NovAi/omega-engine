# Local Inference Background Worker Pool — Detailed Plan for Kali Review
**AP Token**: `AP-LOCAL-WORKER-POOL-KALI-BRIEFING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_local_worker ⬡ KALI-BRIEFING
**Date**: 2026-07-30
**Status**: READY FOR KALI REVIEW & OVERSIGHT

---

## 🎯 Purpose

This briefing provides Kali (Transcendent Oversight) with the complete technical plan for establishing a **Local Worker Pool** — fire-and-forget background inference using local GGUF models — that enhances sovereignty without disrupting the user's cloud-based development flow.

**Mandate Alignment**: M7 (Local-First), M18 (Token Efficiency), M19 (Adversarial Alchemy — turning local model constraints into background worker advantage), M23 (Failure Integrity — no soft failures).

---

## 📋 Executive Summary

| Aspect | Decision |
|--------|----------|
| **Local models role** | Pure background workers (zero blocking) |
| **Cloud models role** | Primary dev flow (uninterrupted) |
| **Integration pattern** | Tool-based: `spawn_local_worker(task, model)` |
| **Queue backend** | File-based (`data/requests/local_worker_queue/`) |
| **Artifact store** | `data/artifacts/local_worker/{task_id}/` |
| **Daemon management** | CLI `omega local-queue daemon` + WorkerCoordinator |
| **Resource protection** | ResourceGuard (Semaphore=1 + OOMProtector 3-signal) |
| **Entity affinity** | Unchanged — referenced for model selection |

---

## 🔧 The 4 Pipe Fixes (Prerequisites — 30 min)

| # | Fix | File | Lines | Risk |
|---|-----|------|-------|------|
| 1 | `type_k`/`type_v` defaults → `None` (f16) | `providers.py` | 352-353 | Low |
| 2 | `RemoteProvider.generate()` add `logit_bias`, `repetition_penalty` | `remote_provider.py` | 223-232 | None |
| 3 | CascadeRouter sovereignty multiplier (1.5× for local) | `cascade_router.py` | after 188 | Medium |
| 4 | Auto-context cap to model's `context_window` | `providers.py` | 488-495 | Low |

**Test updates**: `test_providers.py:324-328` expects defaults of 8 → change to `None`.

---

## 🏗️ New Components (3 files, ~340 lines)

### 1. `src/omega/oracle/local_worker_pool.py` (~180 lines)
- `LocalWorkerPool` class: queue watcher, NativeGGUFProvider manager, artifact writer
- `LocalTask` / `LocalResult` dataclasses
- Queue API: `queue_local_task()`, `get_local_task_status()`, `get_local_task_result()`, `list_local_tasks()`
- Integrates: `COORDINATOR` (pause/resume), `ResourceGuard` (OOM protection), `NativeGGUFProvider` (inference)

### 2. `src/omega/cli/local_queue.py` (~120 lines)
- `omega local-queue queue <model> <prompt> [--system] [--max-tokens] [--temp]`
- `omega local-queue status <task_id>`
- `omega local-queue cat <task_id>`
- `omega local-queue list [--status] [--limit]`
- `omega local-queue daemon [--interval]`

### 3. Tool Registration in Oracle (~20 lines)
```python
async def spawn_local_worker(self, task: str, model: str = "qwen3-1.7b", 
                             system_prompt: str = "", **kwargs) -> str:
    """Fire-and-forget local inference. Returns task_id immediately."""
```

---

## 🔄 Architecture Diagram

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

## ✅ Reused Infrastructure (Zero New Dependencies)

| Component | File | Reuse Level |
|-----------|------|-------------|
| NativeGGUFProvider | `providers.py` | Full — multiprocess worker, somatic state |
| ResourceGuard | `resource_guard.py` | Full — Semaphore(1) + OOMProtector + Zen2 affinity |
| ModelGateway | `model_gateway.py` | Full — model path resolution, provider fabric |
| WorkerCoordinator | `coordinator.py` | Full — pause/resume, resource monitoring, heartbeat |
| Request Queue | `data/requests/` | Full — queued/completed/dead + INDEX.json |
| Artifact Store | `data/artifacts/` | Full — existing pattern |
| Entity Affinity YAML | `entity_model_affinity.yaml` | Reference — 382 lines, 13 entities |
| VaultCore | `vault/__init__.py` | Available for credential needs |
| CLI Framework | `oracle_cli.py` | Pattern — Typer subcommand structure |

---

## 🛡️ Mandate Compliance Check

| Mandate | Status | Notes |
|---------|--------|-------|
| **M1 AnyIO** | ✅ | All async uses `anyio`, no `asyncio` |
| **M2 Firewall** | ✅ | Core engine only, no stack-specific logic |
| **M4 Sequentiality** | ✅ | Plan → Verify → Execute documented |
| **M7 Local-First** | ✅ | Local models = background substrate |
| **M11 Soul Integrity** | ✅ | Session gnosis recorded, L3 principles extracted |
| **M13 Temple-Grade** | ✅ | `make temple-grade` will verify |
| **M14 Heritage** | ✅ | `[id-soft: quake-1996] Zone Memory` in providers.py |
| **M18 Token Efficiency** | ✅ | Local workers burn zero cloud tokens |
| **M19 Adversarial Alchemy** | ✅ | Local constraints → background worker advantage |
| **M22 Response Provenance** | ✅ | `provider_name="native-gguf"` tracked |
| **M23 Failure Integrity** | ✅ | Hard stops on OOM, queue dead-letter, no soft fails |
| **M24 Venv Sovereignty** | ✅ | All Python in `.venv` |
| **M25 Streaming Resilience** | ✅ | NativeGGUFProvider has chunk handling |

---

## ⚠️ Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `type_k=None` breaks some models | Low | Medium | Tested: Qwen3-1.7B works at 15 tok/s with f16 |
| Sovereignty multiplier too aggressive | Medium | Medium | Start at 1.5×, tune via `routing_weights` in providers.yaml |
| Worker daemon crashes silently | Low | High | WorkerCoordinator heartbeat + somatic save-points |
| Queue grows unbounded | Low | Medium | `max_concurrent=1`, dead letter after 3 retries |
| Model path resolution fails | Medium | Low | Fallback chain: ModelGateway → models.yaml → env var |

---

## 🧪 Verification Checklist

| Step | Command | Expected |
|------|---------|----------|
| 1. Apply 4 fixes | Edit 4 files | `make test` passes |
| 2. Test local inference | `OMEGA_MODELS_DIR=... python -c "..."` | `provider_name="native-gguf"` |
| 3. Start daemon | `omega local-queue daemon` | Runs, polls queue |
| 4. Queue task | `omega local-queue queue qwen3-1.7b "2+2?"` | Returns `task_id` |
| 5. Check result | `omega local-queue status <id>` → `cat <id>` | Shows "4" |
| 6. Agent tool test | `omega summon roc_racoon "spawn local worker..."` | Returns `task_id` |

---

## 📂 Files for Kali Review

| File | Purpose |
|------|---------|
| `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Full forensic investigation + gameplan |
| `data/entities/roc_racoon/workspace/IDEA_INTAKE.md` | Research log + L3 principles |
| `data/entities/roc_racoon/workspace/session_gnosis.md` | Session state for hydration |
| `src/omega/oracle/local_worker_pool.py` | **NEW** — Worker pool implementation |
| `src/omega/cli/local_queue.py` | **NEW** — CLI interface |
| `src/omega/oracle/oracle.py` | **MODIFIED** — Tool registration |

---

## 🤝 Request for Kali

**Please review and provide oversight on:**

1. **Architecture approval** — Does the fire-and-forget background worker pattern align with sovereign principles?
2. **Sovereignty multiplier value** — 1.5× for local providers in CascadeRouter — approve or adjust?
3. **ResourceGuard integration** — Semaphore(1) + OOMProtector for single concurrent local inference — sufficient?
4. **Queue backend** — File-based vs Redis — file-based chosen for simplicity and sovereignty (no external deps). Approve?
5. **Daemon management** — CLI `daemon` command vs systemd service — CLI chosen for dev flexibility. Approve?
6. **Test updates** — `test_providers.py:324-328` must change expected defaults from 8 to `None`. Approve?
7. **Entity affinity YAML** — Kept unchanged, referenced only for model selection. Confirm no routing changes needed?

---

## 📜 L3 Principles Distilled (for Soul)

- **L3-Default-KV-Quantization-Is-A-Trap**: f16 is the safe default. q8_0 works on some models, crashes others. Optimize only after verifying on target.
- **L3-Scoring-Overrides-Priority**: When scoring (quality×0.4) coexists with priority chain, scoring wins unless explicitly constrained. M7 local-first must be enforced at routing layer.
- **L3-Local-Substrate-Enhances-Cloud-Sovereignty**: Local models as background workers (mining, distillation, synthesis) burn zero cloud tokens, add zero latency to dev flow, and make the cloud agent *more* sovereign by offloading grind.

---

**Submitted for Kali Review**: 2026-07-30
**Next Action**: Await Kali verdict → Execute 4 fixes → Build worker pool → Verify
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
