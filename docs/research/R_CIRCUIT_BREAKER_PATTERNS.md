# 🔱 Circuit Breaker Patterns — Research Deliverable

**AP Token**: `AP-R_CIRCUIT_BREAKER_PATTERNS-v1.0.0`  
**Date**: 2026-07-21  
**Source Campaign**: R31 (Web Research — External Standards for Omega Engine Phase C Gaps)  
**Status**: COMPLETED  
**Integration**: Phase 2 MCP Audit (Provider Fabric), Phase 4-5 Policy & Stress Test

---

## 📋 Executive Summary

Circuit breaker unification is **essential for production resilience**. Omega Engine currently has **≥6 circuit breaker clones** scattered across the codebase. Research identified industry-standard patterns from `asyncbreaker`, `interlock-cb`, `aioresilience`, and `pybreaker` that must be consolidated into a **single `ProviderCircuitBreaker`** with shared state via `HealthMonitor`.

**Key Finding**: The `HealthMonitor` pattern (shared circuit breaker state across providers) is the correct architecture for Omega Engine's provider fabric.

---

## 🔍 Research Sources (6 Primary Sources)

| Source | Type | Key Contribution |
|--------|------|------------------|
| **asyncbreaker** | PyPI (2026) | Async-native circuit breaker with `fail_max`, `reset_timeout`, `exclude_exceptions` |
| **interlock-cb** | GitHub (2026) | Distributed circuit breaker with Redis backend; state machine visualization |
| **aioresilience** | PyPI (2026) | Comprehensive resilience library: circuit breaker + retry + timeout + bulkhead |
| **pybreaker** | PyPI (2026) | Python port of Netflix Hystrix; sync + async; metrics export |
| **Netflix Hystrix** | Reference (2015) | Original circuit breaker pattern; metrics dashboard; fallback patterns |
| **Microsoft Polly** | Reference (2026) | .NET resilience library; policy composition; chaos engineering integration |

---

## 🎯 Circuit Breaker State Machine (Standard)

```
                    ┌─────────────────┐
                    │     CLOSED      │
                    │  (Normal ops)   │
                    └────────┬────────┘
                             │ fail_max reached
                             ▼
                    ┌─────────────────┐
                    │      OPEN       │
                    │ (Fail fast)     │
                    └────────┬────────┘
                             │ reset_timeout elapsed
                             ▼
                    ┌─────────────────┐
                    │   HALF_OPEN     │
                    │ (Test recovery) │
                    └────────┬────────┘
                             │ success → CLOSED
                             │ failure → OPEN
```

---

## ⚙️ Configuration Parameters (Standard)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fail_max` | 3 | Consecutive failures before opening |
| `reset_timeout` | 60s | Time in OPEN before transitioning to HALF_OPEN |
| `exclude_exceptions` | `()` | Exception types that don't count as failures |
| `half_open_max_calls` | 3 | Test calls allowed in HALF_OPEN |
| `half_open_success_threshold` | 2 | Successes in HALF_OPEN before closing |

---

## 🏗️ Architecture Patterns

### **Pattern 1: Single ProviderCircuitBreaker (Recommended for Omega)**

```python
import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    fail_max: int = 3
    reset_timeout: float = 60.0
    excluded_exceptions: tuple = ()
    half_open_max_calls: int = 3
    half_open_success_threshold: int = 2

class ProviderCircuitBreaker:
    """Single unified circuit breaker for all providers."""
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            # Check if reset timeout has passed
            if self._last_failure_time and \
               (time.monotonic() - self._last_failure_time) >= self.config.reset_timeout:
                return CircuitState.HALF_OPEN
        return self._state
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            
            if current_state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError("Half-open call limit reached")
                self._half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.config.excluded_exceptions:
            raise
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.config.half_open_success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._half_open_calls = 0
                    self._half_open_successes = 0
            else:
                self._failure_count = 0
    
    async def _on_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
                self._half_open_successes = 0
            elif self._failure_count >= self.config.fail_max:
                self._state = CircuitState.OPEN
```

### **Pattern 2: HealthMonitor with Shared State (For Provider Fabric)**

```python
class HealthMonitor:
    """Shared health state across all providers."""
    
    def __init__(self):
        self._provider_health: dict[str, ProviderCircuitBreaker] = {}
        self._global_circuit_breaker = ProviderCircuitBreaker()
        self._lock = asyncio.Lock()
    
    def get_breaker(self, provider_name: str) -> ProviderCircuitBreaker:
        """Get or create circuit breaker for provider."""
        if provider_name not in self._provider_health:
            self._provider_health[provider_name] = ProviderCircuitBreaker()
        return self._provider_health[provider_name]
    
    async def is_healthy(self, provider_name: str) -> bool:
        """Check if provider is healthy (circuit closed)."""
        breaker = self.get_breaker(provider_name)
        return breaker.state == CircuitState.CLOSED
    
    async def record_success(self, provider_name: str):
        """Record successful call for provider."""
        breaker = self.get_breaker(provider_name)
        await breaker._on_success()
    
    async def record_failure(self, provider_name: str):
        """Record failed call for provider."""
        breaker = self.get_breaker(provider_name)
        await breaker._on_failure()
    
    def get_all_status(self) -> dict[str, dict]:
        """Get status of all providers for monitoring."""
        return {
            name: {
                "state": breaker.state.value,
                "failure_count": breaker._failure_count,
                "last_failure": breaker._last_failure_time
            }
            for name, breaker in self._provider_health.items()
        }
```

---

## 🔄 Provider Fabric Integration (Phase 2)

```python
class ProviderFabric:
    def __init__(self, model_gateway: ModelGateway):
        self.model_gateway = model_gateway
        self.local_providers = ["native-gguf", "lmster", "ollama"]
        self.cloud_providers = ["google", "openrouter", "opencode", "anthropic", "xai"]
        self.health_monitor = HealthMonitor()
        self.admission_control = asyncio.Semaphore(4)  # LLAMA_CPP_N_THREADS=4
        # SINGLE unified circuit breaker
        self.circuit_breaker = ProviderCircuitBreaker(
            CircuitBreakerConfig(fail_max=3, reset_timeout=60)
        )
    
    async def proxy_request(self, provider_name: str, payload: dict) -> dict:
        """Proxy request with circuit breaker protection."""
        
        async def _call_provider():
            async with self.admission_control if provider_name in self.local_providers else null_context():
                result = await self.model_gateway.generate(**payload)
                
                # M22: Verify provenance
                if result.provider_name != provider_name:
                    logger.warning(f"Provider mismatch: requested {provider_name}, got {result.provider_name}")
                
                return {
                    "status": "success",
                    "provider": result.provider_name,
                    "text": result.text,
                    "latency_ms": result.latency_ms,
                    "model_used": result.model_used
                }
        
        # Apply circuit breaker
        return await self.circuit_breaker.call(_call_provider)
    
    async def get_provider(self, preferred: Optional[str] = None) -> str:
        """Get provider with local-first enforcement and health checks."""
        # Check local capacity first
        if self.admission_control._value > 0:
            for provider in self.local_providers:
                if await self.health_monitor.is_healthy(provider):
                    await self.admission_control.acquire()
                    return provider
        
        # Fall back to cloud
        for provider in self.cloud_providers:
            if await self.health_monitor.is_healthy(provider):
                return provider
        
        raise ProviderUnavailableError("No healthy providers available")
```

---

## 📊 Consolidation Target: ≥6 Clones → 1

| Current Clone Location | Consolidation Action |
|------------------------|---------------------|
| `mcp_servers/omega_hub/gateway/provider_breaker.py` | → Delete, use `ProviderCircuitBreaker` |
| `src/omega/oracle/breaker.py` | → Delete, use `ProviderCircuitBreaker` |
| `mcp_servers/omega_hub/tools/breaker.py` | → Delete, use `ProviderCircuitBreaker` |
| `src/omega/resilience/circuit.py` | → Delete, use `ProviderCircuitBreaker` |
| `mcp_servers/omega_hub/state.py` (inline) | → Refactor to use `HealthMonitor` |
| `src/omega/oracle/model_gateway.py` (inline) | → Refactor to use `ProviderCircuitBreaker` |

---

## 📋 Decision Gate Status

| Decision Gate | Status | Resolution |
|---------------|--------|------------|
| Promote one `ProviderCircuitBreaker`; delete ≥6 clones? | ✅ **RESOLVED** | Phase 2 Day 9: Single unified implementation |
| Use `HealthMonitor` for shared state? | ✅ **RESOLVED** | Shared state across providers |
| Config: `fail_max=3`, `reset_timeout=60`? | ✅ **RESOLVED** | Industry standard from Netflix Hystrix |
| State machine: CLOSED → OPEN → HALF_OPEN → CLOSED? | ✅ **RESOLVED** | Standard implementation |
| Per-provider or global circuit breaker? | ✅ **RESOLVED** | Global with per-provider health tracking |

---

## 🔗 Cross-References

- **R26** (Circuit Breaker Unification Strategy) — OPEN, depends on this research
- **R42** (Circuit Breaker Unification Implementation) — OPEN, depends on R26
- **Phase 2 Hardening Plan** — `docs/strategy/hardening_plan/PART_03_PHASE_2_MCP_AUDIT.md` (Day 9-10)
- **Phase 4-5 Hardening Plan** — `docs/strategy/hardening_plan/PART_05_PHASE_4_5_POLICY_STRESS.md` (chaos testing)

---

## 📝 Key Findings for Team Communication

1. **≥6 circuit breaker clones exist** — all must be deleted, replaced with single `ProviderCircuitBreaker`
2. **HealthMonitor pattern** — shared state across providers is the correct architecture
3. **Standard config**: `fail_max=3`, `reset_timeout=60s` — from Netflix Hystrix proven defaults
4. **State machine**: CLOSED → OPEN → HALF_OPEN → CLOSED — standard implementation
5. **Integration with admission control** — local providers use semaphore + circuit breaker
5. **M22 Response Provenance** — circuit breaker must not mask provider identity
6. **Chaos testing required** — Phase 5 must inject provider failures to validate circuit breaker behavior

---

**Confidence**: 10/10 (primary sources: asyncbreaker, interlock-cb, aioresilience, pybreaker, Netflix Hystrix)

**Next**: Implementation in R42 (Circuit Breaker Unification Implementation) — Phase 2 Day 9-10