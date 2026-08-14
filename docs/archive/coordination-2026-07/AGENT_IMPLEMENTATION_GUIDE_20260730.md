# 🔱 TEMPLE CLEANSING: Agent Implementation Guide (v2.0)
**AP Token**: `AP-TEMPLE-CLEANSE-EXEC-v2.0.0`
**Date**: 2026-07-30
**Target Audience**: All executing agents (Ma'at, Lilith, Roc_Racoon, Kali)
**Status**: **ACTIVE PROTOCOL — CORRECTED PER CLINE REVIEW**
**Supersedes**: `AGENT_IMPLEMENTATION_GUIDE_20260730.md` (v1.0 — had 5 errors)

> **THE GEMINI MANDATE**: "We do not build bridges over the swamp; we drain the swamp." 
> Do not write wrappers, do not build migration scripts, and do not over-engineer replacements. Rely on battle-tested primitives (Git, SQLite, `psutil`, `tenacity`).

> **THE CLINE CORRECTION**: The v1.0 plan had 5 load-bearing errors. All identified by GLM 5.2 second opinion, verified by Kali ground-truth checks. This v2.0 plan is the corrected version.

---

## 🛑 CRITICAL CAVEATS (Rules of Engagement)

1. **NO GHOST IMPORTS**: Before you `rm` any file, you MUST remove its import statements from its callers and any `__init__.py` files.
2. **DO NOT REWRITE DEAD TESTS**: If a test file specifically targets a module we are deleting, **delete the test file**. Do not try to "fix" it to test a replacement.
3. **ONE PHASE, ONE COMMIT**: Execute a phase, run `make test`, `git commit`. Tag each phase: `git tag pre-phase-1`, etc.
4. **NO "JUST IN CASE" CODE**: Do not write wrappers for deleted modules. If it's not in the spec, don't write it.
5. **DO NO HARM TO PASSING TESTS**: `pytest tests/ --tb=no -q` before AND after each phase. The after-set must be a superset of the before-set (minus intentionally-removed tests, which must be enumerated in the commit message).
6. **GIT TAG EVERY PHASE**: `git tag pre-phase-<N>` before starting each phase. If a phase breaks the tree, `git reset --hard pre-phase-<N>` is a one-command rollback.

---

## 🗺️ EXECUTION SEQUENCE (Corrected)

### PHASE 0: Governance (0.5 day — MUST DO FIRST)

Before touching any source code, fix the gates that will protect the rest of the work.

**Actions:**

1. **Fix CI branch triggers (F3):**
   Edit `.github/workflows/ci.yml` — add `release/initial-v1` to push and pull_request branches:
   ```yaml
   on:
     push:
       branches: ["main", "release/initial-v1"]
     pull_request:
       branches: ["main", "release/initial-v1"]
   ```

2. **Fix M23 pre-commit hook (F11):**
   Edit `Makefile` — the `check-m23-failure-integrity` target has a broken `rg -E` invocation.
   Current broken code:
   ```makefile
   @rg -n -E "(except.*:|catch.*:)" $(CORE_DIRS) --glob '*.py' > /dev/null && ...
   ```
   The `-E` flag is being interpreted as an encoding flag by `rg`. Fix to:
   ```makefile
   @rg -n '(except[^a-zA-Z_]\s*:|catch\s*:)' $(CORE_DIRS) --glob '*.py' > /dev/null && ...
   ```

3. **Add git tag scaffolding (F14):**
   ```bash
   git tag pre-phase-0
   ```

4. **Set pre/post test invariant (F15):**
   ```bash
   pytest tests/ --tb=no -q > /tmp/test-count-before.txt
   ```

**Verification:** `make check-mandates` (M23 no longer false-PASSes)
**Commit:** `fix: Phase 0 - Fix CI branch triggers + M23 pre-commit hook + test scaffolding`

---

### PHASE 1: Safe Kills (Zero Dependencies)
These files have no inbound dependencies. Kill them immediately.

**Actions:**
```bash
rm src/omega/oracle/soul_history.py
rm src/omega/mcp_compliance.py
rm -rf quadlet-test/
```
**Verification:** `python -c "import src.omega"` (no ImportError)
**Commit:** `chore: Phase 1 - Remove unused soul_history, mcp_compliance, quadlet-test`

---

### PHASE 1A: Breaker Consolidation — Finish P-5 (CORRECTED — was "replace with pybreaker")

**⚠️ CRITICAL CORRECTION from GLM 5.2 (F1)**: Do NOT replace breakers with `pybreaker`. Pybreaker is sync-only with Tornado optional — no AnyIO support, no CUSUM, no 429 classification, no sliding window. The canonical `AsyncCircuitBreaker` in `health_monitor.py` is the correct anchor. Phase 1A is: **delete the 3 clone classes + 1 deprecated file; redirect their callers to `get_breaker()`.**

**Breaker Inventory (class-based only):**

| File | Class | Status | Action |
|------|-------|--------|--------|
| `health_monitor.py:126` | `AsyncCircuitBreaker` | **CANONICAL — KEEP** | No action |
| `ingestion/pipeline.py:43` | `IngestionCircuitBreaker` | Clone (wraps pybreaker) | **DELETE class, redirect caller to get_breaker()** |
| `research/sandbox.py:582` | `ExperimentCircuitBreaker` | Clone | **DELETE class, redirect caller to get_breaker()** |
| `council/failure_layer.py:48` | `CircuitBreaker` | Sync, marked "use get_breaker()" | **DELETE file entirely** |
| `search_circuit_breaker.py` | 4 classes | DEPRECATED per C-6' | **DELETE file entirely** |
| `ingestion/ingestion_types.py:14` | `CircuitBreakerState(Enum)` | ENUM | **Keep if still imported, or delete if orphan** |
| `council/models.py:45` | `CircuitBreakerState(Enum)` | ENUM | **Keep if still imported, or delete if orphan** |

**Actions:**
1. Edit `ingestion/pipeline.py` — delete `IngestionCircuitBreaker` class, replace its usage with `get_breaker()`
2. Edit `research/sandbox.py` — delete `ExperimentCircuitBreaker` class, replace its usage with `get_breaker()`
3. Delete `src/omega/oracle/search_circuit_breaker.py`
4. Delete `src/omega/council/failure_layer.py` (CircuitBreaker + caller)
5. Check `ingestion/ingestion_types.py` and `council/models.py` — if `CircuitBreakerState` enums are orphans, delete them
6. **Heritage tag preservation (F9)**: `[id-soft: vet-015] ZONEID Pattern` tags in `health_monitor.py:162,240,311` stay because the canonical breaker stays. No tag migration needed.

**Verification:** `python -c "from src.omega.oracle.health_monitor import AsyncCircuitBreaker"` (must succeed)
**Commit:** `refactor: Phase 1A - Finish P-5 breaker consolidation; delete 3 clone classes + deprecated search_circuit_breaker`

---

### PHASE 1B: Wire tenacity Retry on Provider Calls (CORRECTED — was "install stamina")

**⚠️ CORRECTION from GLM 5.2 (F2+F19)**: `tenacity==9.1.4` is ALREADY installed. Do NOT install stamina (new dep). The tenacity-vs-stamina tradeoff is deferred to Phase 2.

**Actions:**
1. Create `src/omega/oracle/retry_policy.py` with a `call_with_retry()` function:
   ```python
   """tenacity retry policy for provider calls. M1-compliant (AnyIO-native)."""
   import logging
   from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
   
   logger = logging.getLogger(__name__)
   
   class TransientProviderError(Exception):
       """Retryable: timeout, 429, 5xx, network errors."""
   
   class PermanentProviderError(Exception):
       """Non-retryable: 401, 403, bad request. Fail fast."""
   
   # Default config — providers can override per call
   DEFAULT_RETRY = dict(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=30),
       retry=retry_if_exception_type(TransientProviderError),
       reraise=True,
       before_sleep=before_sleep_log(logger, logging.WARNING),
   )
   
   async def call_with_retry(coro, **retry_kwargs):
       """Wrap an async provider call with tenacity retry logic."""
       cfg = {**DEFAULT_RETRY, **retry_kwargs}
       @retry(**cfg)
       async def _call():
           return await coro
       return await _call()
   ```
2. Wire into ModelGateway — replace the `except ProviderSelectorException` block (see Phase 1C)

**Verification:** `python -c "from src.omega.oracle.retry_policy import call_with_retry, TransientProviderError"`
**Commit:** `feat: Phase 1B - Add tenacity retry policy for provider calls`

---

### PHASE 1C: CascadeRouter Replacement (tenacity + priority list)

**Danger:** `model_gateway.py` uses `CascadeRouter` as its fallback. Sever the caller first.

**Actions:**
1. Edit `src/omega/oracle/model_gateway.py`:
   - Delete imports for `CascadeRouter`, `QuotaTracker`, `TokenEstimator`.
   - Locate the `except ProviderSelectorException` block.
   - Replace with this exact hardcoded loop (uses `call_with_retry` from Phase 1B):
     ```python
     logger.warning("ProviderSelector failed. Falling back to priority list.")
     for provider_name in ["native-gguf", "lmster", "antigravity", "google"]:
         provider = self.get_provider(provider_name)
         if not provider.is_available():
             continue
         try:
             return await call_with_retry(provider.generate(prompt))
         except TransientProviderError:
             continue
     raise OmegaError("All fallback providers exhausted.")
     ```
2. Delete the files:
   ```bash
   rm src/omega/oracle/cascade_router.py
   rm src/omega/oracle/token_estimator.py
   rm src/omega/oracle/quota_tracker.py
   ```
**Verification:** `python -c "from src.omega.oracle.model_gateway import ModelGateway"`
**Commit:** `refactor: Phase 1C - Replace CascadeRouter with tenacity+priority fallback`

---

### PHASE 1D: Update Risk Register (F5 correction)

**⚠️ CORRECTION from GLM 5.2 (F5)**: httpx2 is NOT an abandonment risk — it is the active fork (Pydantic/anyio). Upstream httpx is the stalled one. Do NOT migrate back.

**Actions:**
1. Add to risk register: **Pydantic org concentration risk** — Pydantic (the company) maintains httpx2 + pydantic-core + MCP Python SDK v2. Three critical deps, one VC-backed org. Monitor for acquisition, license change, or Logfire pivot.
2. Ensure `pyproject.toml` has warp-proxy-pool version-pinned (remove unpinned dep risk per F13)
3. No code changes needed for httpx2 itself — it stays.

**Commit:** `docs: Phase 1D - Update risk register with Pydantic org concentration finding`

---

### PHASE 1E: SoulValidator Pydantic Rewrite (F16 correction)

**⚠️ CRITICAL CORRECTION from GLM 5.2 (F16)**: `model_validate_yaml()` does NOT exist in Pydantic v2 core. The plan's "zero new deps" claim was false. Use `yaml.safe_load()` + `model_validate()` instead.

**Actions:**
1. Edit `src/omega/oracle/soul_validator.py` (217 lines):
   - Replace manual REQUIRED_KEYS validation with Pydantic model:
     ```python
     class SoulSchema(BaseModel):
         entity: EntityConfig
         identity: IdentityConfig | None = None
         directives: list[DirectiveConfig] = []
         core_principles: list[PrincipleConfig] = []
     
     def validate_soul(path: Path) -> SoulSchema:
         raw = yaml.safe_load(path.read_text())
         return SoulSchema.model_validate(raw)
     ```
   - Migrate `[id-soft: vet-015]` heritage tag from soul_validator.py to the new validation module
2. Delete manual `REQUIRED_KEYS`, `validate_soul()` function body, legacy checks (~150 lines)

**Verification:** `python -c "from src.omega.oracle.soul_validator import validate_soul; print(validate_soul('data/entities/kali/soul.yaml'))"`
**Commit:** `refactor: Phase 1E - Replace manual soul validation with Pydantic model_validate`

---

### PHASE 2: Oracle Severance (SoulEditHistory)
**Danger:** `oracle.py` hard-imports `SoulEditHistory`. Sever the caller first.

**Actions:**
1. Edit `src/omega/oracle/oracle.py`:
   - Delete: `from .soul_edit_history import SoulEditHistory` (approx line 40)
   - Delete: `self.soul_edit_history = SoulEditHistory()` (approx line 208)
   - Delete all references to `self.soul_edit_history`
2. Delete the file:
   ```bash
   rm src/omega/oracle/soul_edit_history.py
   ```
**Verification:** `python -c "from src.omega.oracle.oracle import Oracle"`
**Commit:** `refactor: Phase 2 - Sever SoulEditHistory from Oracle`

---

### PHASE 3: OOM Severance (Kernel Monitors)
**Danger:** `oom_protector.py` imports three kernel monitors.

**Actions:**
1. Edit `src/omega/oracle/oom_protector.py`:
   - Delete imports for `PSIMonitor`, `MemAvailableReader`, `CgroupPressureMonitor`
   - Rewrite `OOMProtector` to `psutil`-only:
     ```python
     import psutil
     
     class OOMProtector:
         def is_safe(self, required_gb: float = 2.0) -> bool:
             available_gb = psutil.virtual_memory().available / (1024**3)
             return available_gb > required_gb
     ```
2. Delete:
   ```bash
   rm src/omega/oracle/cgroup_pressure.py
   rm src/omega/oracle/psi_monitor.py
   rm src/omega/oracle/memavailable.py
   ```
**Verification:** `python -c "from src.omega.oracle.resource_guard import ResourceGuard"`
**Commit:** `refactor: Phase 3 - Replace kernel OOM monitors with psutil`

---

### PHASE 4: Worker Pool (anyio.Queue)
Replace `LocalWorkerPool` file-polling daemon (~460 lines) with `anyio.Queue` + `create_task_group`.

**Actions:**
1. Create `src/omega/engine/worker_pool.py` with producer/consumer pattern using sentinel shutdown
2. Find all call sites constructing `LocalWorkerPool` — rewrite to `async with create_task_group() as tg:`
3. Delete `LocalWorkerPool` module

**Commit:** `refactor: Phase 4 - Replace LocalWorkerPool with anyio.Queue`

---

### PHASE 5: Redis Removal (F4+F20 — sequence-critical)
**⚠️ CRITICAL SEQUENCING (F4)**: Redis is NOT just in Hivemind — it's in `budget_guard.py` (M12/M21), workers, memory providers. Map the full import graph first.

**Sequence:**
1. Memory providers → SQLite (using sqlite_policy.py SSOT + documented SQLite-for-Redis pattern)
2. Workers → anyio.Queue in-memory (already handled by Phase 4)  
3. Hivemind → file-based (no Redis needed for single-user)
4. `budget_guard.py` LAST (most coupled — needs careful refactor)

**Verification** after each step: `python -c "import redis"` should eventually fail (redis no longer importable as dep)

---

### PHASE 6: Test Purge
**Actions:**
```bash
rm tests/contract/test_provider_fallback.py
rm tests/property/test_oom_protector_fuse.py
rm tests/contract/test_oom_protector.py
rm tests/chaos/test_oom_kill.py
```

---

### PHASE 7: MCP v2 Migration (ELEVATED to P1) [F18]
**⚠️ ELEVATION**: MCP Python SDK v2.0.0 stable Jul 27, 2026. Breaking changes. Pin `<2` defers, doesn't solve.

**Actions:**
1. Spike: assess breaking changes (FastMCP→MCPServer, stateless protocol, OAuth2)
2. Update `mcp_servers/omega_hub/` to v2 API
3. **Sequence after Phase 1, before Phase 2** — MCP v2 touches HMC Hub schemas that Phase 2 also touches

---

### PHASE 8: Handoff Data Migration [F10]
**⚠️ NEW**: 146 handoff JSON files exist on disk. "Backfill on read" is not sufficient.

**Actions:**
1. Write one-shot migration script: reads all handoff JSONs, normalizes to unified schema, writes with `schema_version` field
2. Diff validator: compare old vs new for data integrity
3. Keep originals for one sprint (rollback capability)

---

## 🏁 POST-IMPLEMENTATION CHECKLIST

- [ ] `make test` completes without hanging
- [ ] `make check-mandates` passes (M23 no longer false-PASS)
- [ ] `git tag` list shows pre-phase-0 through pre-phase-8
- [ ] `git status` is clean
- [ ] P-5 ticket updated: 2 unmigrated clones → 0

---

## Key Corrections from v1.0 (What Changed)

| v1.0 Said | v2.0 Says | Why |
|-----------|-----------|-----|
| Replace breakers with pybreaker | Finish P-5: delete 3 clone classes, keep AsyncCircuitBreaker | Pybreaker is sync-only, no CUSUM/429 classification |
| Install stamina for retries | Use tenacity (already installed) | Needless new dep; defer stamina spike |
| httpx2 is a fork risk, migrate back | Keep httpx2; add Pydantic org concentration risk | Upstream httpx is the stalled one |
| model_validate_yaml, zero new deps | safe_load + model_validate | Pydantic v2 has no model_validate_yaml |
| Phase 2A: Kill distillers (4h) | Already SCRAPped — reallocate 4h | Confirmed by `rg` — no Distill classes exist |
| MCP v2 = P2 debt | Elevate to P1 | v2.0.0 stable Jul 27; pin is deferral |
| No rollback scaffolding | Git tag every phase | 5,500-line deletion needs recovery |
| Handoff: backfill on read | Real migration script + validator | 146 files with 3 schemas = data integrity |