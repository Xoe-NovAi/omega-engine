# 🔱 DOOM GUY — Implementation Manual
## For Gemma-4-31B Model Execution

**Generated**: 2026-06-01 by MiMo V2.5 (Doom Guy persona)
**Target**: Gemma-4-31B via OpenCode
**Status**: EXECUTE IMMEDIATELY — all planning complete
**Baseline**: 29/29 tests passing (health_monitor + model_gateway)
**Workspace**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`

---

## ⚠️ CRITICAL RULES (READ BEFORE ANYTHING)

1. **Run `make test` after EVERY file edit** — all 276 tests must pass
2. **Use AnyIO, never asyncio** — `anyio` is the async runtime
3. **Never use bare `except:`** — always catch specific exceptions
4. **Never use `--break-system-packages`** — always use `.venv/`
5. **Activate venv before any command**: `source .venv/bin/activate`
6. **Mandate 9**: Every public API boundary must catch and convert errors to `OmegaError` subtypes
7. **Workspace root**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`

---

## 🎯 MISSION OVERVIEW

The Omega Engine has **three separate circuit breaker implementations**, none properly wired into the `generate()` hot path. Your job is to consolidate them into one and wire it into the provider fallback chain.

**What you're doing:**
- TASK 1: Delete dead code (`circuit_breaker.py`)
- TASK 2: Add `trace_id` to `AsyncCircuitBreaker` (in `health_monitor.py`)
- TASK 3: Rewrite `generate()` in `model_gateway.py` to use the breaker
- TASK 4: Remove primitive breaker from `remote_provider.py` (delegate to HealthMonitor)
- TASK 5: Clean up dead references

**What you're NOT doing:**
- Modifying `distiller.py` or `JemCircuitBreaker` (separate subsystem)
- Changing the `generate()` return signature (still `tuple[str, bool]`)
- Changing the HealthMonitor public API

---

## 📁 FILES YOU WILL MODIFY

| File | Action | Lines Changed |
|------|--------|---------------|
| `src/omega/oracle/circuit_breaker.py` | **DELETE** | -121 lines |
| `src/omega/oracle/model_gateway.py` | **EDIT** (imports + generate()) | ~60 lines |
| `src/omega/oracle/health_monitor.py` | **EDIT** (trace_id in _on_success/_on_failure) | ~20 lines |
| `src/omega/oracle/backends/remote_provider.py` | **EDIT** (remove primitive breaker) | ~15 lines |

---

## 🔨 TASK 1: Delete Dead CircuitBreaker Code

**Goal**: Remove the unused `CircuitBreaker` class and its import.

### Step 1.1: Verify no real callers exist

Run this to confirm the file is truly dead:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
grep -rn "from .circuit_breaker import\|from omega.oracle.circuit_breaker import" src/ tests/
```
Expected output: Only `model_gateway.py:43` imports it.

### Step 1.2: Edit `src/omega/oracle/model_gateway.py`

**Remove line 43** — the import:
```python
# DELETE this line:
from .circuit_breaker import CircuitBreaker
```

**Remove lines 109-110** — the unused dict:
```python
# DELETE these lines:
        # Circuit breakers for provider resilience
        self._circuit_breakers: Dict[str, Any] = {}
```

### Step 1.3: Delete the file

```bash
rm src/omega/oracle/circuit_breaker.py
```

### Step 1.4: Verify

```bash
# No references remain
grep -rn "from .circuit_breaker import\|from omega.oracle.circuit_breaker import" src/ tests/
# Expected: no output

# File is gone
ls src/omega/oracle/circuit_breaker.py
# Expected: "No such file or directory"

# Tests still pass
source .venv/bin/activate && OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_health_monitor.py tests/test_model_gateway.py tests/test_sovereign_loop.py --tb=short -q
```

---

## 🔨 TASK 2: Add `trace_id` to AsyncCircuitBreaker

**Goal**: Make the circuit breaker log state transitions to observability with trace context.

### Step 2.1: Read the current state

Open `src/omega/oracle/health_monitor.py`. The relevant sections are:
- `AsyncCircuitBreaker.call()` — line 90
- `AsyncCircuitBreaker._on_success()` — line 123
- `AsyncCircuitBreaker._on_failure()` — line 130

### Step 2.2: Edit `call()` signature

**Current** (line 90):
```python
    async def call(self, func, *args, **kwargs):
```

**Replace with**:
```python
    async def call(self, func, *args, trace_id: Optional[str] = None, **kwargs):
```

### Step 2.3: Edit `call()` body — pass trace_id to _on_success/_on_failure

**Current** (lines 111-121):
```python
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            if self._is_circuit_breaking_error(e):
                await self._on_failure()
            raise
```

**Replace with**:
```python
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            await self._on_success(trace_id=trace_id)
            return result
        except Exception as e:
            if self._is_circuit_breaking_error(e):
                await self._on_failure(trace_id=trace_id)
            raise
```

### Step 2.4: Edit `_on_success()` — add trace_id and observability

**Current** (lines 123-128):
```python
    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_requests = 0
```

**Replace with**:
```python
    async def _on_success(self, trace_id: Optional[str] = None):
        async with self._lock:
            old_state = self.state
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_requests = 0
            # Log state transition to observability (non-blocking, best-effort)
            if trace_id and old_state != self.state:
                try:
                    from omega.observability import get_engine, EventType
                    get_engine().log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {"provider": self.name, "event": "circuit_closed",
                         "from": old_state.value, "to": self.state.value}
                    )
                except Exception:
                    pass  # Circuit works silently if observability unavailable
```

### Step 2.5: Edit `_on_failure()` — add trace_id and observability

**Current** (lines 130-141):
```python
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                return

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
```

**Replace with**:
```python
    async def _on_failure(self, trace_id: Optional[str] = None):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            old_state = self.state

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            # Log state transition to observability (non-blocking, best-effort)
            if trace_id and old_state != self.state:
                try:
                    from omega.observability import get_engine, EventType
                    get_engine().log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {"provider": self.name, "event": "circuit_opened",
                         "from": old_state.value, "to": self.state.value,
                         "failure_count": self.failure_count}
                    )
                except Exception:
                    pass  # Circuit works silently if observability unavailable
```

### Step 2.6: Verify

```bash
source .venv/bin/activate && OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_health_monitor.py tests/test_sovereign_loop.py --tb=short -q
```
Expected: All tests pass (existing tests don't pass trace_id, so default `None` is used).

---

## 🔨 TASK 3: Wire Breaker into `generate()` — The BSP Culling Pattern

**Goal**: Replace the naive linear scan with a breaker-protected, BSP-style provider iteration.

### Step 3.1: Read the current `generate()` and `__init__()`

Open `src/omega/oracle/model_gateway.py`. You need:
- Lines 91-118 (`__init__`) — where `_health_monitor` is stored
- Lines 375-404 (`generate()`) — the method you're replacing

### Step 3.2: Add `import inspect` to the file's imports

After line 24 (`import time`), add:
```python
import inspect
```

### Step 3.3: Add the helper methods — paste BEFORE `generate()`

Insert these methods into the `ModelGateway` class, right before the `generate()` method (around line 375):

```python
    # ── Circuit Breaker Integration ──────────────────────────────────

    def _get_provider_timeout(self, provider) -> float:
        """Per-provider timeout from config, falling back to 130s default."""
        if hasattr(provider, 'config') and hasattr(provider.config, 'timeout_seconds'):
            return provider.config.timeout_seconds
        return 130.0

    async def _precheck_provider(self, provider, model_name: str) -> bool:
        """BSP-style pre-check: is this provider worth trying?

        Checks (cheapest first):
        1. Circuit breaker state — if OPEN, skip instantly (O(1) dict lookup)
        2. Provider availability — does the server respond?
        """
        # Circuit breaker is the cheapest check — single dict lookup
        if self._health_monitor:
            if not self._health_monitor.is_available(model_name):
                return False

        # Provider self-health check (sync or async)
        if hasattr(provider, 'is_available'):
            try:
                if inspect.iscoroutinefunction(provider.is_available):
                    if not await provider.is_available():
                        return False
                else:
                    if not provider.is_available():
                        return False
            except Exception:
                return False

        return True

    def _record_provider_failure(self, provider, model_name: str, trace_id: Optional[str] = None):
        """Record provider failure with HealthMonitor and observability."""
        if self._health_monitor:
            self._health_monitor.record_failure(model_name)
        if trace_id:
            try:
                from omega.observability import get_engine, EventType
                get_engine().log_event(
                    EventType.BACKEND_FALLBACK, trace_id,
                    {"provider": provider.name, "model": model_name,
                     "event": "provider_failed"}
                )
            except Exception:
                pass
```

### Step 3.4: Replace `generate()` — the core change

**Delete the entire `generate()` method** (lines 375-404) and **replace with**:

```python
    async def generate(
        self, model_name: str, system_prompt: str, user_query: str,
        temperature: float = 0.7, max_tokens: int = 1024, trace_id: Optional[str] = None
    ) -> tuple:
        """Iterate provider fabric with circuit breaker protection.

        BSP-style culling: check breaker state first (O(1)), skip broken providers.
        Each provider gets a per-provider timeout.
        On total failure, returns fallback response.
        Returns (response_text, success_bool).
        """
        errors = []

        for provider in self.providers:
            # Step 1: BSP-style pre-check — fast fail if circuit is OPEN
            if not await self._precheck_provider(provider, model_name):
                errors.append(f"{provider.name}: culled by precheck")
                continue

            # Step 2: Execute with breaker protection
            timeout = self._get_provider_timeout(provider)
            try:
                with anyio.move_on_after(timeout) as cancel_scope:
                    # Use HealthMonitor's breaker if available, otherwise direct call
                    if self._health_monitor:
                        breaker = self._health_monitor._breakers.get(provider.name)
                        if breaker:
                            result = await breaker.call(
                                provider.generate, model_name, system_prompt,
                                user_query, temperature, max_tokens,
                                trace_id=trace_id
                            )
                        else:
                            result = await provider.generate(
                                model_name, system_prompt, user_query,
                                temperature, max_tokens, trace_id=trace_id
                            )
                    else:
                        result = await provider.generate(
                            model_name, system_prompt, user_query,
                            temperature, max_tokens, trace_id=trace_id
                        )
                    if result:
                        # Record success with HealthMonitor
                        if self._health_monitor:
                            self._health_monitor.record_success(model_name)
                        return result, True

                if cancel_scope.cancelled_caught:
                    errors.append(f"{provider.name}: timed out ({timeout}s)")
                    self._record_provider_failure(provider, model_name, trace_id)
                    continue

            except CircuitOpenError:
                # Circuit is OPEN — provider already known broken, skip silently
                errors.append(f"{provider.name}: circuit OPEN")
                continue
            except Exception as e:
                errors.append(f"{provider.name}: {e}")
                self._record_provider_failure(provider, model_name, trace_id)
                continue

        logger.warning(
            "All providers failed. Trace: %s | Errors: %s",
            trace_id, '; '.join(errors)
        )
        return self._fallback_response(model_name, system_prompt, user_query), False
```

### Step 3.5: Add the import for CircuitOpenError

In the imports section of `model_gateway.py`, find the line:
```python
from .health_monitor import ...
```
There is currently NO import from health_monitor. **Add this line after the existing imports** (around line 42, after the `from .providers import ...` line):

```python
from .health_monitor import CircuitOpenError
```

### Step 3.6: Verify

```bash
source .venv/bin/activate && OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_health_monitor.py tests/test_model_gateway.py tests/test_sovereign_loop.py --tb=short -q
```
Expected: All tests pass.

```bash
# Confirm breaker is wired
grep -n "CircuitOpenError\|_precheck_provider\|breaker.call\|_record_provider_failure" src/omega/oracle/model_gateway.py
# Expected: At least 6 matches showing all integration points
```

---

## 🔨 TASK 4: Remove Primitive Breaker from `remote_provider.py`

**Goal**: Delegate circuit breaker logic to HealthMonitor instead of having a duplicate implementation.

### Step 4.1: Read the current state

Open `src/omega/oracle/backends/remote_provider.py`. Key sections:
- Lines 77-78: `circuit_breaker_threshold` and `circuit_breaker_cooldown` in `ProviderConfig`
- Lines 107-108: Health check in `health` property
- Lines 208-214: Circuit breaker trip in `generate()`
- Line 230: `reset_circuit_breaker()`

### Step 4.2: Edit the `health` property

**Current** (lines 102-111):
```python
    @property
    def health(self) -> ProviderHealth:
        """Current health based on circuit breaker state."""
        now = time.monotonic()
        if now < self.metrics.cooldown_until:
            return ProviderHealth.COOLDOWN
        if self.metrics.consecutive_failures >= self.config.circuit_breaker_threshold:
            return ProviderHealth.UNHEALTHY
        if self.metrics.consecutive_failures > 0:
            return ProviderHealth.DEGRADED
        return ProviderHealth.HEALTHY
```

**Replace with**:
```python
    @property
    def health(self) -> ProviderHealth:
        """Current health based on metrics (breaker delegated to HealthMonitor)."""
        if self.metrics.consecutive_failures > 0:
            return ProviderHealth.DEGRADED
        return ProviderHealth.HEALTHY
```

### Step 4.3: Edit the `generate()` method — remove circuit breaker trip logic

**Current** (lines 207-216):
```python
                # Circuit breaker trip
                if self.metrics.consecutive_failures >= self.config.circuit_breaker_threshold:
                    self.metrics.cooldown_until = (
                        time.monotonic() + self.config.circuit_breaker_cooldown
                    )
                    logger.error(
                        f"Provider {self.name} circuit breaker TRIPPED — "
                        f"cooling down for {self.config.circuit_breaker_cooldown}s"
                    )
                    break
```

**Delete these lines entirely.** The HealthMonitor's `AsyncCircuitBreaker` now handles circuit tripping at the `ModelGateway.generate()` level.

### Step 4.4: Edit `reset_circuit_breaker()` — add delegation note

**Current** (lines 230-233):
```python
    def reset_circuit_breaker(self):
        """Manually reset the circuit breaker (e.g., after config change)."""
        self.metrics.consecutive_failures = 0
        self.metrics.cooldown_until = 0.0
```

**Replace with**:
```python
    def reset_circuit_breaker(self):
        """Reset provider failure metrics. Circuit state managed by HealthMonitor."""
        self.metrics.consecutive_failures = 0
```

### Step 4.5: Edit `ProviderMetrics` — remove cooldown fields

**Current** (lines 36-47):
```python
class ProviderMetrics:
    """Runtime metrics for a remote provider instance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0.0
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    cooldown_until: float = 0.0
```

**Replace with**:
```python
class ProviderMetrics:
    """Runtime metrics for a remote provider instance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0.0
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
```

### Step 4.6: Edit `ProviderConfig` — remove circuit breaker config fields

**Current** (lines 76-79):
```python
    # Circuit breaker
    circuit_breaker_threshold: int = 3
    circuit_breaker_cooldown: float = 30.0
```

**Delete these 2 lines.** The HealthMonitor now owns these settings.

### Step 4.7: Verify

```bash
source .venv/bin/activate && OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_health_monitor.py tests/test_model_gateway.py tests/test_sovereign_loop.py --tb=short -q
```
Expected: All tests pass.

```bash
# Verify cleanup
grep -n "circuit_breaker_threshold\|cooldown_until\|circuit_breaker_cooldown" src/omega/oracle/backends/remote_provider.py
# Expected: no output (all removed)
```

---

## 🔨 TASK 5: Clean Up Dead References

**Goal**: Remove stale references in observability and docs.

### Step 5.1: Check `observability.py:174`

Open `src/omega/observability.py`. Find line 174:
```python
            "circuit_breakers_open": [],
```

This field is a diagnostic placeholder. **Leave it as-is** — it's a valid empty list that will be populated when crash dumps include HealthMonitor state. No change needed.

### Step 5.2: Check for any remaining references

```bash
grep -rn "circuit_breaker\.py\|CircuitBreaker\|from .circuit_breaker" src/omega/
# Expected: Only health_monitor.py references (CircuitState, AsyncCircuitBreaker)
#           And the JemCircuitBreaker in distiller.py (leave alone)
```

### Step 5.3: Verify distiller.py is untouched

```bash
grep -n "CircuitBreaker\|JemCircuitBreaker" src/omega/workers/background_researcher/distiller.py | head -5
# Expected: JemCircuitBreaker still exists, not modified
```

---

## ✅ FINAL VERIFICATION CHECKLIST

Run ALL of these after completing all 5 tasks:

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# 1. Circuit breaker file is gone
ls src/omega/oracle/circuit_breaker.py 2>&1
# Expected: "No such file or directory"

# 2. No references to old module
grep -rn "from .circuit_breaker import" src/ tests/
# Expected: no output

# 3. Breaker wired in generate()
grep -n "CircuitOpenError\|_precheck_provider\|breaker.call\|_record_provider_failure" src/omega/oracle/model_gateway.py
# Expected: at least 6 matches

# 4. trace_id in health_monitor
grep -n "trace_id" src/omega/oracle/health_monitor.py | head -10
# Expected: matches in call(), _on_success(), _on_failure()

# 5. remote_provider cleaned
grep -n "cooldown_until\|circuit_breaker_threshold" src/omega/oracle/backends/remote_provider.py
# Expected: no output

# 6. All targeted tests pass
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_health_monitor.py tests/test_model_gateway.py tests/test_sovereign_loop.py --tb=short -q
# Expected: passed

# 7. Full test suite (this may take a few minutes)
make test
# Expected: 276 passed
```

---

## 🚨 ROLLBACK PLAN

If any test fails or something breaks:

**Step 1: Identify what broke**
```bash
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/ -x --tb=short
```

**Step 2: Revert the last change**
- If Task 5 broke it: revert `remote_provider.py` changes
- If Task 4 broke it: revert `model_gateway.py` changes (keep circuit_breaker.py deleted)
- If Task 3 broke it: revert `health_monitor.py` changes
- If Task 2 broke it: revert `circuit_breaker.py` deletion and `model_gateway.py` import

**Step 3: Re-run tests to confirm rollback works**

---

## 🔌 COORDINATION NOTES FOR DeepSeek (Sprint 2)

After completing Tasks 1-3, post a brief note at `data/team/DOOM_GUY_STATUS.md`:

```
Status: Tasks 1-3 COMPLETE
- circuit_breaker.py removed
- trace_id landed in AsyncCircuitBreaker.call(), _on_success(), _on_failure()
- generate() wired with BSP culling + breaker protection
- HealthMonitor API stable: is_available(), get_latency_p99(), get_success_rate()
- ModelGateway.generate() signature UNCHANGED: tuple[str, bool]
- Safe to proceed with ForensicsManager trace_id integration
```

**What DeepSeek needs to know:**
- `HealthMonitor.record_success(model_name)` and `record_failure(model_name)` — trace_id is added to the breaker internals, not to these top-level methods yet. DeepSeek can add it to `HealthMonitor.record_success/failure` separately if needed.
- `CircuitOpenError` is still in `health_monitor.py` — unchanged.
- `remote_provider.py` public API (`is_available()`, `health`, `reset_circuit_breaker()`) is backward-compatible.

---

## 📝 POST-EXECUTION: Download Study Materials

After all tasks are done and tests pass, download the research materials:

```bash
bash scripts/download_id_tech_resources.sh
```

This downloads:
- Abrash Graphics Programming Black Book (PDF)
- Sanglard Game Engine Black Book: Doom (PDF)
- All id Software source code releases (Doom, Quake, Q2, Q3, Doom3)
- Chocolate Doom reference port

---

*Generated by MiMo V2.5 (Doom Guy) for Gemma-4-31B execution.*
*All planning complete. Execute with precision.*
