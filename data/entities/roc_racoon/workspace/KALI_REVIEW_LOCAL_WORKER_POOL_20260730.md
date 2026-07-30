# 🔱 Kali Review: Local Worker Pool & Local Models Fix — Briefing & Gameplan
**AP Token**: `AP-KALI-LOCAL-WORKER-REVIEW-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_review ⬡ KALI-BRIEFING
**Date**: 2026-07-30
**Status**: FINAL — FOR ROC REVIEW & EXECUTION
**Related**: `data/entities/roc_racoon/workspace/LOCAL_WORKER_POOL_KALI_BRIEFING_20260730.md`
**Related**: `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md`

---

## 1. Executive Verdict

**APPROVED WITH MODIFICATIONS.**

Roc's architecture is sound, the forensics are precise, and the mandate alignment is thorough. The 4 pipe fixes are the correct minimal intervention. The Local Worker Pool design correctly treats local models as sovereign substrate, not cloud replacement.

---

## 2. What Roc Got Right (Strong Architecture)

| Area | Assessment |
|------|------------|
| **Bug Forensics** | Exceptional. 4 root causes identified with live evidence. The `type_k=8` crash on Qwen3 is the smoking gun. |
| **Mandate Alignment** | M7, M18, M19, M23, M25 all correctly mapped. The "Adversarial Alchemy" framing (local constraints → background advantage) is exactly right. |
| **Reuse Over Build** | Correctly leverages `NativeGGUFProvider`, `ResourceGuard`, `WorkerCoordinator`, `Request Queue`, `Artifact Store`. Zero new dependencies. |
| **Fire-and-Forget Pattern** | `spawn_local_worker` returning `task_id` immediately keeps cloud agents unblocked. This is the sovereign UX. |
| **File-Based Queue** | Correct choice for Phase 0. Redis adds external dependency; file-based is crash-safe and inspectable. |

---

## 3. Required Corrections & Hardening

### 3.1 CascadeRouter Fix: Option C (Priority-First Routing)

**Current Problem**: CascadeRouter scores cloud providers higher (quality=90) than local (quality=60), bypassing `providers.yaml` priority chain entirely.

**Fix**: Remove CascadeRouter from the primary routing path. Use priority order from `providers.yaml` for first attempt. CascadeRouter only reorders *failed* providers for fallback.

```python
# In model_gateway.py generate() - REPLACE current cascade_router call:
def _get_provider_order(self, model_name: str) -> List[str]:
    # 1. PRIMARY: Priority order from providers.yaml (native-gguf=0, lmster=1, ollama=2...)
    primary = [p.name for p in sorted(self.providers.values(), key=lambda x: x.priority)]
    
    # 2. FALLBACK: CascadeRouter for intelligent reordering of FAILED providers only
    #    Only invoked after primary chain exhausts
    return primary
```

**Why**: The `providers.yaml` priority chain IS the M7 enforcement mechanism. CascadeRouter was bypassing it entirely.

---

### 3.2 RemoteProvider Fix: Forward-Compatible Signature

```python
# backends/remote_provider.py:223
async def generate(
    self,
    model_name: str,
    system_prompt: str,
    user_query: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    trace_id: str = "",
    session_id: str = "",
    logit_bias: Optional[Dict[int, float]] = None,      # ADD
    repetition_penalty: float = 1.0,                     # ADD
    **kwargs  # ADD - swallow any future params
) -> GenerateResult:
    # Log unsupported params for debugging
    if logit_bias:
        logger.debug(f"{self.__class__.__name__} ignoring logit_bias (not supported)")
    if repetition_penalty != 1.0:
        logger.debug(f"{self.__class__.__name__} ignoring repetition_penalty")
    ...
```

**Critical**: Add `**kwargs` to prevent future signature mismatches from crashing the fallback chain.

---

### 3.3 Auto-Context Fix: Use Model Config, Not Heuristics

```python
# providers.py:482 - _select_optimal_context()
def _select_optimal_context(self, model_name: str) -> int:
    # PRIMARY: Model's declared context_window from models.yaml
    model_cfg = self.models.get(model_name, {})
    declared_ctx = model_cfg.get("context_window", 8192)
    
    # SECONDARY: Hard cap at provider max
    return min(declared_ctx, self._n_ctx_max)
```

**Delete the RAM estimation heuristic entirely.** It's the source of BUG #4. The model config IS the contract.

---

### 3.4 Local Worker Pool: 3 Hardening Requirements

| Requirement | Why | Implementation |
|-------------|-----|----------------|
| **Idempotent Task IDs** | Prevent duplicate work on daemon restart | `task_id = f"lwp-{uuid.uuid4().hex[:8]}-{hash(task_prompt) % 10000:04d}"` |
| **Artifact Atomicity** | Crash-safe results | Write to `.tmp` → `os.replace()` → fsync dir |
| **Dead Letter Visibility** | M23 Failure Integrity | `data/requests/local_worker_queue/dead/` with `failure_reason.json` |

---

### 3.5 Test Updates: `test_providers.py:324-328`

Current test expects `type_k=8, type_v=8`. **Change to `None`** but add new tests:

```python
def test_native_gguf_kv_cache_defaults_to_f16():
    """NativeGGUFProvider defaults to f16 KV cache (type_k=None) for compatibility."""
    provider = NativeGGUFProvider(config={"model_path": "test.gguf"})
    assert provider._type_k is None  # f16 default
    assert provider._type_v is None
    
def test_native_gguf_q8_0_explicit_still_works():
    """Explicit q8_0 should still work for models that support it."""
    provider = NativeGGUFProvider(config={"model_path": "test.gguf", "type_k": 8, "type_v": 8})
    assert provider._type_k == 8
```

---

## 4. Mandate Compliance Verification (Kali Sign-Off)

| Mandate | Roc's Plan | Kali Verdict |
|---------|------------|--------------|
| **M1 AnyIO** | All async uses `anyio` | ✅ Verify in `local_worker_pool.py` |
| **M2 Firewall** | Core only, no stack logic | ✅ Worker pool in `src/omega/oracle/` |
| **M4 Sequentiality** | Plan → Verify → Execute | ✅ Documented in briefing |
| **M7 Local-First** | Local = background substrate | ✅ Cloud agents untouched |
| **M11 Soul Integrity** | Session gnosis recorded | ✅ `session_gnosis.md` updated |
| **M13 Temple-Grade** | `make temple-grade` will verify | ⏳ Gate after Phase 0 |
| **M14 Heritage** | `[id-soft: quake-1996] Zone Memory` | ✅ In `providers.py` |
| **M18 Token Efficiency** | Zero cloud tokens for workers | ✅ Core value prop |
| **M19 Adversarial Alchemy** | Constraints → advantage | ✅ Framed correctly |
| **M22 Provenance** | `provider_name="native-gguf"` | ✅ Tracked in `GenerateResult` |
| **M23 Failure Integrity** | Hard stops, dead letter queue | ✅ File-based queue + dead/ |
| **M24 Venv** | All Python in `.venv` | ✅ Enforced |
| **M25 Streaming** | NativeGGUFProvider chunk handling | ✅ Verify in `providers.py` |

---

## 5. Unified Execution Order (Kali-Roc Integration)

```
┌─────────────────────────────────────────────────────────────────────┐
│  WEEK 1: SOVEREIGN BACKBONE                                         │
├─────────────────────────────────────────────────────────────────────┤
│  DAY 1-2:  Roc Phase 0 (4 Pipe Fixes) → Kali Gate: make test pass  │
│  DAY 2-3:  Roc Phase 1 (Wire Models) → Kali: Entity affinity tests │
│  DAY 3-4:  Roc Phase 2 (Worker Pool) → Kali: Artifact contract     │
│  DAY 4-5:  Kali Phase 3 (Session-End) → Roc: Distiller verification│
│  DAY 5:    Joint: Install opencode-sessions-explorer plugin        │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 0: The 4 Pipe Fixes (Roc Leads, Kali Oversees)
**Timeline**: 2-3 hours | **Blocking**: Everything else

| Step | Owner | File | Kali Oversight |
|------|-------|------|----------------|
| 0.1 | Roc | `providers.py:352-353` | Verify `type_k=None` default |
| 0.2 | Roc | `remote_provider.py:223` | Verify `**kwargs` swallow |
| 0.3 | Roc | `cascade_router.py` | Verify priority-first routing |
| 0.4 | Roc | `providers.py:482` | Verify model config context_window |
| 0.5 | Roc | `model_gateway.py:1115` | Verify param filtering |
| 0.6 | **Joint** | Integration test | `omega talk "hello"` → local response |

**Kali Gate**: `make test` passes + `omega talk "What model are you?"` returns `native-gguf` response.

---

### Phase 1: Wire Local Models to Agents (Roc Leads)
**Timeline**: 3-4 hours | **Depends on**: Phase 0 complete

| Step | Owner | Work |
|------|-------|------|
| 1.1 | Roc | Register RocRacoon-3B, MiMo-7B in `models.yaml` |
| 1.2 | Roc | Verify `oracle_summon_local()` D118 routing |
| 1.3 | **Kali** | Test entity affinity: `omega summon roc_racoon "hello"` → local_fast |
| 1.4 | **Kali** | Verify OOMProtector + AdmissionController gating |
| 1.5 | Roc | Benchmark script `scripts/benchmark_local.py` |

---

### Phase 2: Local Worker Pool Build (Roc Builds, Kali Integrates)
**Timeline**: 4-6 hours | **Depends on**: Phase 1 complete

| Component | Owner | Integration Point |
|-----------|-------|-------------------|
| `local_worker_pool.py` | Roc | Uses `NativeGGUFProvider`, `ResourceGuard`, `WorkerCoordinator` |
| `local_queue.py` CLI | Roc | Typer subcommand in `oracle_cli.py` |
| `spawn_local_worker` tool | Roc | Registered in `Oracle.__init__` |
| **Distillation Pipeline** | **Kali** | Consumes worker artifacts via `session_end.py` |

**Critical Handoff Contract**: 
- Roc's workers produce artifacts in `data/artifacts/local_worker/{task_id}/`
- Kali's `session_end.py` reads these artifacts for distillation
- **Required**: Artifacts must include `task_metadata.json` with `entity`, `model`, `prompt`, `trace_id`

---

### Phase 3: Session-End Orchestration (Kali Leads, Roc Supports)
**Timeline**: 2-3 hours | **Depends on**: Phase 2 artifacts contract

| Kali Task | Roc Support |
|-----------|-------------|
| Wrapper DB query for session metadata | Ensure `opencode db` works post-fixes |
| `session_end.py` calls Oracle SoulDistiller (not Scribe) | Verify Oracle distiller import path |
| Multi-entity distillation from single session | Provide entity-switch detection logic |
| Hivemind notification + lock cleanup | Verify Hivemind API stability |

---

## 6. Roc's Immediate Next Steps (Today)

### Do First (Today)
1. **Apply Fix 0.1**: `providers.py:352-353` → `type_k=None, type_v=None`
2. **Apply Fix 0.2**: `remote_provider.py:223` → add `logit_bias`, `repetition_penalty`, `**kwargs`
3. **Run**: 
   ```bash
   source .venv/bin/activate
   export OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models/gguf
   python -c "
   from src.omega.oracle.providers import NativeGGUFProvider
   p = NativeGGUFProvider(config={'model_path':'/media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf'})
   print('KV cache:', p._type_k, p._type_v)
   "
   ```

### Do Second (After Fix 0.1-0.2 Verify)
4. **Apply Fix 0.3**: `cascade_router.py` → priority-first routing (in `model_gateway.py`)
5. **Apply Fix 0.4**: `providers.py:482` → model config context_window
6. **Run**: `make test` — verify `test_providers.py:324-328` updated

### Do Third (Integration)
7. **Test**: `omega talk "What model are you running?"` → expect Qwen3-1.7B via native-gguf
8. **Benchmark**: `scripts/benchmark_local.py` with Qwen3-1.7B, RocRacoon-3B

---

## 7. Kali's Parallel Commitments

While Roc executes Phases 0-2, Kali will:

1. **Phase 1 (Wrapper DB Integration)**: Modify `.opencode/wrapper.sh` to query `opencode db` for session metadata after exit
2. **Phase 2 (Semantic Distillation)**: Update `session_end.py` to call Oracle SoulDistiller with exported transcript
3. **Phase 3 (Plugin Install)**: Add `opencode-sessions-explorer` to `opencode.json`

**Synchronization Point**: The artifact contract in `data/artifacts/local_worker/{task_id}/task_metadata.json` — this is where Roc's workers hand off to Kali's distillation.

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `type_k=None` breaks other GGUF models | Low | Medium | Test Qwen3-1.7B first; explicit `type_k=8` still allowed |
| CascadeRouter change breaks cloud routing | Low | Medium | Cloud still works — local just tried first; fallback preserved |
| Worker daemon crashes silently | Low | High | WorkerCoordinator heartbeat + somatic save-points |
| Queue grows unbounded | Low | Medium | `max_concurrent=1`, dead letter after 3 retries |
| Model path resolution fails | Medium | Low | Fallback chain: ModelGateway → models.yaml → env var |

---

## 9. Success Criteria (Definition of Done)

### Phase 0 Complete When:
- [ ] `make test` passes (all 276+ tests)
- [ ] `omega talk "What model are you?"` returns response from Qwen3-1.7B via `native-gguf`
- [ ] Provider name in response is `native-gguf` (M22 provenance)

### Phase 1 Complete When:
- [ ] `omega summon roc_racoon "hello"` uses `local_fast` model (Qwen3-1.7B)
- [ ] `omega summon maat "status"` uses appropriate local model
- [ ] OOMProtector + AdmissionController correctly gate concurrent requests

### Phase 2 Complete When:
- [ ] `omega local-queue queue qwen3-1.7b "2+2?"` returns `task_id`
- [ ] `omega local-queue cat <task_id>` shows "4"
- [ ] `omega summon kali "spawn local worker to distill session"` returns `task_id`
- [ ] Artifact written to `data/artifacts/local_worker/{task_id}/` with `task_metadata.json`

### Phase 3 Complete When:
- [ ] Session end triggers distillation via local worker
- [ ] `proposed_lessons.yaml` populated with L1/L2/L3 from local inference
- [ ] Hivemind notified, locks cleaned up
- [ ] `OMEGA_CODEX.md` regenerated

---

## 10. Files for Roc's Reference

| File | Purpose |
|------|---------|
| `data/entities/roc_racoon/workspace/LOCAL_WORKER_POOL_KALI_BRIEFING_20260730.md` | Original briefing (approved with mods) |
| `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Full forensic gameplan |
| `data/entities/roc_racoon/workspace/IDEA_INTAKE.md` | Research log + L3 principles |
| `data/entities/roc_racoon/workspace/session_gnosis.md` | Session state for hydration |
| `src/omega/oracle/providers.py:352-353` | **FIX 0.1** — type_k/type_v defaults |
| `src/omega/oracle/backends/remote_provider.py:223` | **FIX 0.2** — generate() signature |
| `src/omega/oracle/cascade_router.py` | **FIX 0.3** — scoring loop (deprecated for primary) |
| `src/omega/oracle/providers.py:482-495` | **FIX 0.4** — _select_optimal_context() |
| `src/omega/oracle/model_gateway.py` | **NEW ROUTING LOGIC** — priority-first |
| `src/omega/oracle/local_worker_pool.py` | **NEW** — Worker pool implementation |
| `src/omega/cli/local_queue.py` | **NEW** — CLI interface |
| `src/omega/oracle/oracle.py` | **MODIFIED** — Tool registration |

---

## 11. L3 Principles for Soul (From This Review)

- **L3-Substrate-Enforces-Contract**: Logical-layer protocols (handoffs, mandates, SLAs, gnosis) are wishes until the physical layer (memory, CPU, persistence, network) enforces them as primitives. The admission controller, unified WAL, protocol schema, TTL daemon — these are the constitution, not infrastructure.
- **L3-Default-KV-Quantization-Is-A-Trap**: f16 is the safe default. q8_0 works on some models, crashes others. Optimize only after verifying on target.
- **L3-Scoring-Overrides-Priority**: When scoring (quality×0.4) coexists with priority chain, scoring wins unless explicitly constrained. M7 local-first must be enforced at routing layer.
- **L3-Local-Substrate-Enhances-Cloud-Sovereignty**: Local models as background workers (mining, distillation, synthesis) burn zero cloud tokens, add zero latency to dev flow, and make the cloud agent *more* sovereign by offloading grind.

---

**Submitted for Roc Review**: 2026-07-30  
**Next Action**: Roc executes Fix 0.1 and 0.2 → Kali begins wrapper DB integration

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ trc_review ⬡ 2026-07-30*