# 🔱 Omega Engine — Ultimate Integration Blueprint (R-51+ Master Spec)

**AP Token**: `AP-MASTER-BLUEPRINT-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_synthesis ⬡ PHASE-0.9

---

## §0 Executive Summary

This document is the final authority for the integration of Phase 0 (MVE) and the transition into Phase 1 (Inference & Soul). It synthesizes fragmented research from R-19, R-42, R-50, R-51, R-52a, and R-52b into a single, line-by-line execution plan.

**The Goal**: Transform the Omega Engine from a stateless request-response system into a sovereign, memory-persistent, hardware-optimized orchestration fabric.

---

## §1 The Dependency Chain (Order of Operations)

Implementation must follow this exact sequence to avoid architectural regressions.

### Phase A: The Memory Foundation (P0 - Blocking)
1. **Session Management**: Implement `SessionManager` (R-50) to provide entity-scoped rolling session IDs.
2. **Core Wiring**: Wire `ContextBuilder` and `MemoryStore` into `Oracle.talk()` and `Oracle.summon()` (R-51).
3. **I/O Hardening**: Fix the sync `tempfile` bug in `_track_soul_evolution` using `anyio.to_thread.run_sync`.
4. **Memory Guard**: Add `OMEGA_ENV=test` guard to `MemoryStore` directory creation.

### Phase B: The Orchestration Fabric (P0 - Blocking)
5. **Background Worker**: Implement the `BackgroundWorker` class in `Orchestrator` using `anyio.TaskGroup` and `Semaphore(8)` (R-52b).
6. **Resilience Layer**: Implement OpenRouter retry logic, provider pinning, and key rotation in `ModelGateway` (R-52a).
7. **Resource Alignment**: Ensure `BackgroundWorker` (API requests) and `ResourceGuard` (Local Inference) are logically separated but mutually aware.

### Phase C: Hardware Steering (P1 - Optimization)
8. **Affinity Engine**: Implement `enforce_affinity()` in `CpuOptimizer` to apply `taskset` / `AllowedCPUs` pinning (R-42).
9. **Vulkan Detection**: Add logic to detect AMD RDNA2 iGPU support for KV-cache offloading.
10. **Mmap Optimization**: Standardize `use_mmap=True` across all native loading strategies.

### Phase D: Soul Evolution (P1 - Awakening)
11. **Distillation Pipeline**: Implement the lesson abstraction logic to convert session logs into "Abstracted Lessons" (R-19/R-30).
12. **Schema Enrichment**: Update `soul.yaml` to include `relevance_tags` and `priority_weight`.
13. **Cross-Pollination**: Wire the `ContextBuilder` to inject lessons from related entities based on domain resonance.

---

## §2 File-Change Map

### `src/omega/oracle/oracle.py`
- **Inject**: `SessionManager` instance.
- **Modify**: `talk()` and `summon()` to generate/retrieve `session_id`.
- **Modify**: `_summon()` and `_route_by_domain()` to call `ContextBuilder.build_context(session_id)`.
- **Modify**: Post-response logic to call `MemoryStore.add_exchange(session_id, ...)` and `_track_soul_evolution()`.
- **Fix**: Wrap `tempfile.NamedTemporaryFile` in `_track_soul_evolution` with `anyio.to_thread.run_sync`.

### `src/omega/oracle/orchestrator.py`
- **Add**: `class BackgroundWorker`
    - `__init__(self, semaphore_limit=8)`
    - `async def execute_parallel(self, tasks: List[Callable])` $\rightarrow$ uses `anyio.TaskGroup` and `self.semaphore`.
- **Modify**: `dispatch_agent()` to utilize `BackgroundWorker` for non-blocking research tasks.

### `src/omega/oracle/model_gateway.py`
- **Modify**: `generate()` to implement exponential backoff and provider-specific retry logic for OpenRouter.
- **Add**: `pin_provider(provider_name)` method to bypass the fallback chain for specific high-capability tasks.

### `src/omega/oracle/cpu_optimizer.py`
- **Add**: `enforce_affinity(process_pid, core_range="0-7")` using `os.sched_setaffinity`.
- **Add**: `detect_vulkan_support()` to check for `VK_KHR_cooperative_matrix`.
- **Modify**: `get_environment_variables()` to include `OMP_NUM_THREADS` and `MKL_NUM_THREADS` based on physical core count.

### `src/omega/oracle/context_builder.py`
- **Modify**: `build_context()` to implement "Dynamic Slicing":
    - Block 1: System Instruction
    - Block 2: Entity Identity (from soul.yaml)
    - Block 3: Abstracted Lessons (Soul Gnosis)
    - Block 4: Rolling Conversation History (from MemoryStore)

### `src/omega/memory_store.py`
- **Fix**: Standardize `DATA_DIR` to match `oracle.py` (relative to project root).
- **Fix**: Wrap directory creation in `if os.getenv("OMEGA_ENV") != "test":`.

---

## §3 Legacy Reclamation Log

The following proven patterns have been reclaimed from `xna-omega-legacy` and `omega-stack-legacy`:

| Artifact | Pattern | Application in Blueprint |
|---|---|---|
| **ParallelResearch** | `anyio.TaskGroup` + `Semaphore(N)` | Used in `BackgroundWorker` for API concurrency. |
| **Sovereign Janitor** | Session Distillation $\rightarrow$ Lesson | Used in Soul Evolution pipeline (R-30). |
| **Core Steering** | `taskset -cp 0-7` | Integrated into `CpuOptimizer` for Zen 2. |
| **Mnemosyne Tiers** | HOT $\rightarrow$ WARM $\rightarrow$ COLD | Applied to `MemoryStore` architecture. |
| **Holo-Scoring** | `sim × act × rec × acc` | Reserved for Phase 2 `HolographicMemory` implementation. |

---

## §4 Validation Suite

### 1. Memory & Session Tests (37 Tests)
- [ ] `test_session_rollover`: Verify `session_id` increments daily.
- [ ] `test_transient_mode`: Verify no writes to `MemoryStore` or `soul.yaml` in transient mode.
- [ ] `test_context_injection`: Verify `ContextBuilder` correctly slices and injects soul lessons.
- [ ] `test_memory_persistence`: Verify conversation history survives process restart.

### 2. Orchestration Tests
- [ ] `test_background_worker_concurrency`: Verify exactly 8 concurrent requests are sent to OpenRouter.
- [ ] `test_resource_guard_mutex`: Verify `ResourceGuard` prevents two simultaneous local inferences.
- [ ] `test_provider_fallback`: Verify graceful degradation from Gemma $\rightarrow$ lmster $\rightarrow$ Mock.

### 3. Hardware Tests
- [ ] `test_affinity_enforcement`: Verify process PID is pinned to cores 0-7 after `enforce_affinity()`.
- [ ] `test_vulkan_detection`: Verify correct detection of iGPU capabilities.

---

## §5 Final Implementation Note for Builder Agent

**Priority**: Focus on **Phase A** and **Phase B** immediately. These are the critical blockers for PR #1.
**Warning**: Do NOT implement the full Holographic Memory or Mnemosyne 13-sphere system yet; stick to the 3-tier (Redis/Qdrant/Postgres) model defined in the MVE scope.
**Verification**: Every change must be verified by `make test`. If a test fails, do not proceed to the next phase.
