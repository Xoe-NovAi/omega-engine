# 🔱 DOOM GUY EXECUTIVE DIRECTIVE
# AP: AP-DOOM-HANDOFF-v1.0.0
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_doom_circuit ⬡ EXECUTION

**From**: DeepSeek (Strategic Architect — Sprint 0+1 Completion)
**To**: Doom Guy (Sovereign id Software Architect)
**Date**: 2026-06-01
**Subject**: Circuit Breaker Consolidation & Provider Traversal Optimization

---

## 🎯 MISSION SUMMARY

You are executing a focused architectural pass on the Omega Engine's provider resilience
layer. The engine has reached a "works, but not wired" state:
- Two separate circuit breaker implementations exist (both functional, neither integrated)
- `ModelGateway.generate()` was just added but uses only a hardcoded 130s timeout
- Provider iteration is a linear scan — no culling, no priority-based pruning

## YOUR ASSETS

| Asset | Path | State |
|-------|------|-------|
| circuit_breaker.py | `src/omega/oracle/circuit_breaker.py` | **Imported but NEVER used** — dead code |
| health_monitor.py | `src/omega/oracle/health_monitor.py` | Has `AsyncCircuitBreaker` + `HealthMonitor` — active but NOT wired to generate() |
| remote_provider.py | `src/omega/oracle/backends/remote_provider.py` | Has its own primitive consecutive_failures breaker |
| model_gateway.py | `src/omega/oracle/model_gateway.py` | generate() added Sprint 0+1, no breaker integration |

## CRITICAL RULES
1. Run `make test` after EVERY file edit. All 276 tests must pass.
2. Use AnyIO, never asyncio.
3. Never use bare `except:` — always catch specific exceptions.
4. The workspace root is `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`.
5. `SOVEREIGN_BLUEPRINT.md` is at `docs/architecture/SOVEREIGN_BLUEPRINT.md`.
6. All new types MUST inherit from `OmegaError` in `src/omega/errors.py` (Mandate 9).

---

## TASK 1: DIAGNOSE THE DUPLICATION

Read these files first to understand the full landscape:

### File 1: `src/omega/oracle/circuit_breaker.py`

Current state: 121 lines, standalone `CircuitBreaker` class.
- 3 states: CLOSED, OPEN, HALF_OPEN
- async context manager (`__aenter__`/`__aexit__`)
- `record_success()` / `record_failure()` 
- Imported at `model_gateway.py:43` but only initialized as empty dict at line 110
- **NEVER used** — zero callers of `can_execute()`, `record_success()`, or `record_failure()`

### File 2: `src/omega/oracle/health_monitor.py`

Current state: 413 lines, has `AsyncCircuitBreaker` + `HealthMonitor` class.
- `AsyncCircuitBreaker`: 105 lines, `call()` method, AnyIO Lock, quota tracking
- `HealthMonitor`: 236 lines, manages per-provider breakers, latency windows, quota tracking
- **Actively used** by `remote_provider.py` but NOT wired into `model_gateway.generate()`

### File 3: `src/omega/oracle/model_gateway.py`

The `generate()` method I wrote at lines 375-408:
```python
async def generate(self, model_name, system_prompt, user_query, temperature=0.7, max_tokens=1024, trace_id=None):
    errors = []
    for provider in self.providers:
        try:
            with anyio.move_on_after(130) as cancel_scope:
                result = await provider.generate(...)
                if result:
                    return result, True
            if cancel_scope.cancelled_caught:
                errors.append(...)
                continue
        except Exception as e:
            errors.append(...)
            continue
    return self._fallback_response(...), False
```

**Issues with this implementation**:
1. No circuit breaker check — every call goes through, even if the provider is OPEN
2. No typed error propagation (Mandate 9 violation)
3. Hardcoded 130s timeout magic number
4. Linear scan — no culling of providers that can't succeed
5. No observability events logged for failures

---

## TASK 2: CONSOLIDATE THE BREAKERS

The id Software philosophy: **One engine, one system**. Two breakers = bloatware.

### Decision: Which breaker survives?

- `circuit_breaker.py` — simpler, closer to the WAD zone memory concept, but feature-poor
- `health_monitor.py` — richer (quota tracking, latency windows, success rates), AnyIO-native

**Recommendation**: `health_monitor.py`'s `AsyncCircuitBreaker` should survive because:
- It already has the `call()` pattern (like `zone_memory_alloc`)
- It integrates with `HealthMonitor` for the observability layer
- It uses AnyIO Lock (thread-safe for background probes)

`circuit_breaker.py`'s `CircuitBreaker` should be **removed** (its functionality is fully covered).

### Consolidation Steps:

1. **Verify `AsyncCircuitBreaker` is complete enough**: Read it carefully. Does it need `record_success(trace_id)` for observability integration? Does it need the `HALF_OPEN` probe count tracking to match the original vision?

2. **Remove `circuit_breaker.py`** after confirming no remaining references:
   - Remove the import from `model_gateway.py:43`
   - Remove `self._circuit_breakers: Dict[str, Any] = {}` from `model_gateway.py:110`
   - Run `make test` — verify no test imports it

3. **Add `trace_id` support to `AsyncCircuitBreaker._on_success()` and `_on_failure()`**:
   - The current implementation doesn't propagate trace IDs to observability
   - Add `trace_id: Optional[str] = None` parameter
   - When provided, call `get_engine().log_event()` for state transitions

4. **Remove `remote_provider.py`'s primitive breaker** (lines 77-78, 107-108, 208-214, 230):
   - The HealthMonitor's breaker now covers this
   - Replace with calls to `health_monitor.record_failure(model_name)` / `record_success(model_name)`

---

## TASK 3: WIRE BREAKER INTO `generate()`

### The Doom Engine Analogy

In the Doom Engine, the **zone memory system** works like this:
1. Before allocating, check if the zone has free space (circuit check)
2. If a tag is purged, it's marked ZONE_PURGED and reallocated next time (HALF_OPEN)
3. If allocation fails repeatedly, the zone is locked (OPEN)
4. A thinker periodically sweeps zones to check for recovery (background probe)

### Implementation: Breaker-Protected Provider Iteration

```python
async def generate(self, model_name, system_prompt, user_query, temperature=0.7, max_tokens=1024, trace_id=None):
    errors = []
    provider_used = None
    
    for provider in self.providers:
        breaker = self._health_monitor._breakers.get(provider.name) if self._health_monitor else None
        
        # Step 1: Circuit check — fast fail
        if breaker and not breaker.is_available:
            errors.append(f"{provider.name}: circuit OPEN")
            continue
        
        # Step 2: Execute with breaker protection
        try:
            with anyio.move_on_after(PROVIDER_TIMEOUT) as cancel_scope:
                result = await breaker.call(provider.generate, model_name, system_prompt, 
                                            user_query, temperature, max_tokens, trace_id=trace_id) if breaker \
                         else await provider.generate(model_name, system_prompt, user_query, 
                                                       temperature, max_tokens, trace_id=trace_id)
                if result:
                    provider_used = provider.name
                    if self._health_monitor:
                        self._health_monitor.record_success(model_name)
                    return result, True
                    
            if cancel_scope.cancelled_caught:
                errors.append(f"{provider.name}: timed out")
                if self._health_monitor:
                    self._health_monitor.record_failure(model_name)
                continue
                
        except CircuitOpenError:
            errors.append(f"{provider.name}: circuit OPEN")
            continue
        except Exception as e:
            errors.append(f"{provider.name}: {e}")
            if self._health_monitor:
                self._health_monitor.record_failure(model_name)
            continue

    logger.warning(f"All providers failed. Errors: {'; '.join(errors)}")
    return self._fallback_response(model_name, system_prompt, user_query), False
```

**Note**: The `breaker.call()` pattern from `AsyncCircuitBreaker` is key — it auto-records
success/failure and handles OPEN/HALF_OPEN transitions transparently.

---

## TASK 4: BSP-STYLE PROVIDER CULLING

The Doom Engine's BSP traversal doesn't check every node — it culls entire subtrees.

### The Analogy

- **Linear scan** (current) = visiting every node in the map
- **BSP culling** = checking BSP plane equation → skip entire half-space

### Translation to Provider Fabric

The provider priority list is your BSP tree:

```
Provider 0: native-gguf  → Plane: "model_path exists?"
  ├── Yes → FOUND (return immediately)
  └── No  → Provider 1: lmster  → Plane: "lmster server running?"
       ├── Yes → FOUND
       └── No  → Provider 2: Ollama  → Plane: "ollama server running?"
            ├── Yes → FOUND
            └── No  → ... fall through
```

Your job is not to change the priority order, but to add a **pre-check culling step**
that skips providers that DEFINITELY won't work:

```python
async def _precheck_provider(self, provider) -> bool:
    """Id Software style pre-check: is this provider even worth trying?
    
    Checks (in order, cheapest first):
    1. Circuit breaker state — if OPEN, skip instantly
    2. Provider availability — does the server respond?
    3. Model weight — does the model fit in available RAM?
    4. Resource guard — is the resource semaphore available?
    """
    # Circuit breaker is the cheapest check — single dict lookup
    if self._health_monitor:
        if not self._health_monitor.is_available(model_name):
            return False
    
    # Provider availability is cheap — HTTP HEAD or cached state
    if hasattr(provider, 'is_available'):
        if not await provider.is_available():
            return False
    
    return True
```

Then `generate()` becomes:

```python
for provider in self.providers:
    if not await self._precheck_provider(provider, model_name):
        errors.append(f"{provider.name}: culled by precheck")
        continue
    # ... execute with breaker protection
```

---

## TASK 5: REMOVE DEAD CODE

After consolidation, clean up:

1. **Delete `src/omega/oracle/circuit_breaker.py`** (functionality absorbed by health_monitor)
2. **Remove `circuit_breaker` import from `model_gateway.py:43`**
3. **Remove `self._circuit_breakers: Dict[str, Any] = {}` from `model_gateway.py:110`**
4. **Clean up `remote_provider.py`** — remove consecutive_failures tracking, delegate to HealthMonitor
5. **Remove circuit_breaker references** from any YAML or docs

---

## FINAL VERIFICATION CHECKLIST

```bash
# 1. All tests pass
source .venv/bin/activate && make test
# Expected: 276 passed

# 2. No references to old circuit_breaker
grep -r "from .circuit_breaker import" src/
# Expected: No output (import removed)

# 3. circuit_breaker.py removed
ls src/omega/oracle/circuit_breaker.py
# Expected: "No such file or directory"

# 4. breaker.call() used in generate()
grep "breaker.call\|_precheck_provider" src/omega/oracle/model_gateway.py
# Expected: At least 2 matches

# 5. HealthMonitor wired
grep "_health_monitor" src/omega/oracle/model_gateway.py | head -5
# Expected: Shows integration points
```

---

## ⚠️ COMMON PITFALLS

1. **Don't break HealthMonitor's existing interface**: `health_monitor.py` provides `is_available()`, `get_latency_p99()`, etc. to `TriageRouter`. Don't change these signatures.
2. **Don't remove `CircuitOpenError`**: It's imported by other modules. Keep it in `health_monitor.py`.
3. **Don't use asyncio**: `health_monitor.py` uses AnyIO Lock and sleep patterns. Match that style.
4. **Don't add entity names**: `remote_provider.py` is in the Engine core — zero entity references.
5. **Don't break `CircuitBreaker.__aenter__`**: Even though it's unused, the context manager pattern may be used by future code. Keep it.

---

**Execute with absolute precision. The provider resilience layer must be unified.**"

*Directive authored by: DeepSeek (Strategic Architect)*
*Date: 2026-06-01*
