# 🔱 R67: Local Implementation Gaps Audit
**Project**: Omega Engine
**Auditor**: Binah (Sovereign Auditor)
**Target**: Sovereign Model Orchestration System (R60/R65)
**Status**: COMPLETE

---

## 🛡️ Executive Summary
The Omega Engine codebase is fundamentally sound but possesses several "stateless" gaps and synchronization frictions that will block the implementation of the Sovereign Model Orchestration System. The most critical failure is the **Conversation Memory vs. Performance Memory** divide: the engine remembers *what* was said, but not *which model performed best* for a specific domain or entity.

---

## 🎯 Audit Target Analysis

### 1. The Oracle-Gateway Link (Routing & Triage)
**Current State**: Routing is a binary escalation (Iris $\rightarrow$ Pillar Keeper). Model selection is static, derived from `entity.model`.

**Gaps**:
- **Static Model Mapping**: `Oracle._summon` and `Oracle._route_by_domain` rely on `entity.model` (oracle.py:348, 412). There is no mechanism to override the model based on real-time health or task complexity.
- **Hardcoded Speculative Model**: `_respond_as_iris` has a hardcoded model `functiongemma-270m-it-q6_k` (oracle.py:296), bypassing the provider fabric's flexibility.
- **Missing Triage Layer**: The `ModelGateway` is a passive executor. The "Triage Router" must be implemented as a middleware between `Oracle` and `ModelGateway` to perform dynamic model selection.

**Hit List**:
- `src/omega/oracle/oracle.py`: Inject Triage Router before `self.model_gateway.generate()` calls (lines 295, 347, 411).
- `src/omega/oracle/model_gateway.py`: Replace static `provider_map` (lines 122-129) with a dynamic Community Catalog lookup.

### 2. The Memory Hook Gap (Soul vs. History)
**Current State**: `ContextBuilder` is a narrative formatter for conversation history.

**Gaps**:
- **Soul-Memory Disconnect**: `ContextBuilder.build_context` (context_builder.py:44) only queries `memory_store.get_history`. It completely ignores the entity's `soul.yaml` lessons and embodied experiences.
- **Absence of Performance Memory**: There is no storage for "Model-Domain Affinity." The engine does not record that "Model X succeeded where Model Y failed" for a specific user's query type.
- **Stateless Context**: Memory is injected as a block of text, but not as a set of "constraints" or "preferences" that can steer the `ModelGateway`.

**Hit List**:
- `src/omega/oracle/context_builder.py`: Extend `build_context` to fetch and format `lessons_learned` from `soul.yaml`.
- `src/omega/memory_store.py`: Implement a new storage tier for `performance_metrics` (model vs. domain success rates).

### 3. AnyIO Absolute Verification (Forensics)
**Current State**: High compliance in core paths, but "leakage" exists in diagnostic and worker code.

**Violations**:
- **Blocking I/O in Async Context**:
    - `src/omega/oracle/model_gateway.py`: `_check_llama_cli` (line 221) and `_check_llmster` (line 229) use `subprocess.run()` inside `detect_backends()` (async def). This blocks the event loop.
    - `src/omega/oracle/oracle.py`: `_track_soul_evolution` uses `Path.exists()` (line 464) and `Path(str(ARCH_SOUL_PATH))` (line 463) synchronously.
- **Asyncio Leakage**:
    - `src/omega/workers/model_updater.py`: Uses `apscheduler.schedulers.asyncio` (line 19). While a dependency, the underlying loop management may conflict with AnyIO.

**Fixes**:
- Replace `subprocess.run` with `anyio.run_process` in `model_gateway.py`.
- Wrap `Path.exists()` in `anyio.to_thread.run_sync` or use `anyio.Path`.

### 4. ResourceGuard Leakage
**Current State**: Consistently applied to local providers via the `ModelGateway` lock.

**Analysis**:
- **Correct**: `model_gateway.py:382` correctly wraps `LocallmsterProvider`, `OllamaProvider`, and `NativeGGUFProvider` in `self.resource_guard.lock()`.
- **Correct**: Remote providers (Google, OpenRouter) bypass the lock to allow parallel cloud inference.
- **Risk**: Headless agents spawned by `Orchestrator` must acquire the lock *before* the subprocess is spawned if that agent is expected to use local inference. This is currently handled in `orchestrator.py` (line 182) but requires strict enforcement in any new agent types.

### 5. WAD/Portable Boundaries
**Current State**: Core logic is in `src/`, but entity-specific routing preferences are still conceptually tied to `config/entities.yaml`.

**Gaps**:
- **Routing Leakage**: `IRIS_DIRECT_KEYWORDS` (oracle.py:73) and `COMPLEXITY_INDICATORS` (oracle.py:79) are hardcoded in the `Oracle` class. These should be moved to a WAD manifest or a global `routing_rules.yaml` to allow users to customize the speculative decoder without editing source code.
- **Packaging**: The `orchestration/` logic must be strictly decoupled from the `WADLoader` to ensure that adding a new orchestration strategy doesn't require updating every `.xoe` package.

---

## 🚩 The Hit List: Immediate Modifications

| File | Line(s) | Action | Priority |
|-------|----------|--------|----------|
| `src/omega/oracle/oracle.py` | 295, 347, 411 | Inject `TriageRouter.select_model()` | 🔴 Critical |
| `src/omega/oracle/oracle.py` | 73, 79 | Move keywords to `config/routing.yaml` | 🟡 High |
| `src/omega/oracle/model_gateway.py` | 221, 229 | Change `subprocess.run` $\rightarrow$ `anyio.run_process` | 🔴 Critical |
| `src/omega/oracle/context_builder.py` | 44-74 | Integrate `soul.yaml` lesson injection | 🔴 Critical |
| `src/omega/memory_store.py` | N/A | Implement `PerformanceMemory` tier | 🟡 High |
| `src/omega/oracle/oracle.py` | 464 | Change `Path.exists()` $\rightarrow$ `anyio.Path().exists()` | 🟢 Low |
