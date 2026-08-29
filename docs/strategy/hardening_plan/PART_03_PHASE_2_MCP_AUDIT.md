# 🔱 Omega Engine Hardening Plan — Phase 2: MCP Audit & Integration (C-4a)

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Phase**: 2 — MCP Audit & Integration Chain Hardening  
**Days**: 8-14  
**Hardware Profile**: Network I/O, Light CPU — **Parallel OK** (with thermal monitoring)

---

## 📋 What I Am Working On
Execute the 7-day MCP audit (C-4a) and remediate critical integration chain vulnerabilities. This is the single most critical path to Phase Γ.

---

## 🔍 First Principles
**M23 Failure Integrity**: Mandatory tool missing → `[TOOL-CHAIN-COLLAPSE]`. No soft-failures.  
**M9 Error Integrity**: Typed, traceable, testable errors. No bare `except:`.  
**Current State**: File-Hivemind fallback as primary integration method, provider fabric stubbed, MCP client hardcoded.

**Right Approximation**: Primary integration should be cloud-based with verified endpoints. File-based is true fallback only. All integration points must have contract tests and hard-failure patterns.

---

## 🎯 Phase 2 Objectives

| Objective | Success Metric | Tool |
|-----------|----------------|------|
| Integration chain vulnerability remediation | 0 soft-failures, all hard-failures documented | Custom audit |
| Provider fabric implementation | 100% of providers functional with local-first enforcement | Integration tests |
| MCP client configurability | Provider selection via config, not hardcoded | Config audit |
| SearXNG/Firecrawl/Exa validation | All endpoints responding < 500ms | Health check suite |
| Contract test suite | 100% of MCP tool paths covered | `pytest --cov=mcp_servers/omega_hub` |
| M22 Response Provenance | `provider_name` in `GenerateResult` matches actual backend | Trace validation |

---

## 📋 Detailed Actions

### Day 8: Integration Chain Vulnerability Audit

**Action**: Map the entire integration chain and identify single points of failure.

```bash
# 1. Inventory all MCP endpoints
curl -s http://127.0.0.1:8016/debug/tools | jq -r '.handler_count'

# 2. Trace a sample call: oracle_talk → MCP Hub → Gateway → ModelGateway → Provider
# Add logging to verify each hop

# 3. Identify file-Hivemind fallback patterns
grep -r "HALL_OF_RECORDS" mcp_servers/omega_hub/tools/
grep -r "_cold_path\|_latest_path" mcp_servers/omega_hub/tools/

# 4. Check for soft-failures (bare except:, Exception: without logging)
grep -r "except:" mcp_servers/omega_hub/ --exclude-dir=__pycache__
grep -r "except Exception:" mcp_servers/omega_hub/ --exclude-dir=__pycache__

# 5. Verify error propagation (M9, M22)
# Force provider failure → verify OmegaError subtype with trace_id
```

**Deliverable**: `data/coordination/integration_vulnerability_report_20260721.md`

### Day 9: Provider Fabric Implementation

**File**: `mcp_servers/omega_hub/gateway/provider_fabric.py` (new)  
**Pattern**: `[id-soft: quake3-1999] QVM` — isolated provider modules with defined interfaces  
**Web Research Integration**:
- Circuit breaker patterns from asyncbreaker, interlock-cb, aioresilience libraries
- Use `pybreaker` or custom `AsyncCircuitBreaker` with `fail_max=3`, `reset_timeout=60`
- HealthMonitor pattern for shared state across providers
- Consolidate ≥6 circuit breaker clones into single `ProviderCircuitBreaker`
- State machine: CLOSED → OPEN → HALF_OPEN → CLOSED

**Local-First Enforcement (M7)**:
```python
import asyncio
from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    fail_max: int = 3
    reset_timeout: int = 60
    excluded_exceptions: tuple = ()

class ProviderCircuitBreaker:
    """Single unified circuit breaker for all providers"""
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            # Check if reset timeout has passed
            if self._last_failure_time and \
               (asyncio.get_event_loop().time() - self._last_failure_time) >= self.config.reset_timeout:
                return CircuitState.HALF_OPEN
        return self._state
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._on_success()
            return result
        except self.config.excluded_exceptions:
            raise
        except Exception as e:
            async with self._lock:
                self._on_failure()
            raise
    
    def _on_success(self):
        self._failure_count = 0
        self._state = CircuitState.CLOSED
    
    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = asyncio.get_event_loop().time()
        if self._failure_count >= self.config.fail_max:
            self._state = CircuitState.OPEN

class ProviderFabric:
    def __init__(self, model_gateway: ModelGateway):
        self.model_gateway = model_gateway
        self.local_providers = ["native-gguf", "lmster", "ollama"]
        self.cloud_providers = ["google", "openrouter", "opencode", "anthropic", "xai"]
        self.health_monitor = get_health_monitor()
        self.admission_control = asyncio.Semaphore(4)  # 4 local slots (LLAMA_CPP_N_THREADS=4)
        # Single unified circuit breaker for all providers
        self.circuit_breaker = ProviderCircuitBreaker()
    
    async def get_provider(self, preferred: Optional[str] = None) -> str:
        """Get provider with local-first enforcement"""
        # 1. Check local capacity via admission control
        if self.admission_control._value > 0:
            # Try local providers in order
            for provider in self.local_providers:
                if await self._is_provider_healthy(provider):
                    await self.admission_control.acquire()
                    return provider
        
        # 2. Fall back to cloud if local saturated or unhealthy
        for provider in self.cloud_providers:
            if await self._is_provider_healthy(provider):
                return provider
        
        # 3. Last resort: error
        raise ProviderUnavailableError("No healthy providers available")
    
    async def proxy_request(self, provider_name: str, payload: Dict) -> Dict:
        """Proxy request with provider-specific handling and circuit breaker"""
        # Use circuit breaker for all provider calls
        async def _call_provider():
            async with self.admission_control if provider_name in self.local_providers else null_context():
                # Actual provider call via ModelGateway
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
        
        return await self.circuit_breaker.call(_call_provider)
```

### Day 10: MCP Client Configurability

**File**: `mcp_servers/omega_hub/mcp_client.py` (update)

**Action**: Remove hardcoded SearXNG URL, make configurable via `config/providers.yaml` or environment.

```python
# Before (hardcoded):
# mcp_client = SovereignMCPClient(server_url="http://127.0.0.1:8018/mcp")

# After (configurable):
def __init__(self, server_url: Optional[str] = None):
    self.server_url = server_url or os.environ.get(
        "OMEGA_SEARXNG_MCP_URL", 
        "http://127.0.0.1:8018/mcp"  # fallback for backward compatibility
    )
    # ... rest unchanged
```

**Validation**:
- Verify `config/providers.yaml` has `mcp.searxng.url` field
- Test with custom URL via environment variable
- Confirm backward compatibility with existing deployments

**Deliverable**: Updated `mcp_client.py` + config schema documentation

### Day 11: Endpoint Validation Suite

**Action**: Create comprehensive health check suite for all MCP-dependent services.

```bash
# 1. SearXNG MCP Server
curl -s http://127.0.0.1:8018/mcp/health
curl -s http://127.0.0.1:8018/mcp/tools/list
curl -X POST http://127.0.0.1:8018/mcp/tools/call \
  -d '{"name": "search", "arguments": {"query": "test omega engine"}}'

# 2. Firecrawl (if configured)
# 3. Exa (if configured)
# 4. Local services: native-gguf, lmster, Ollama
# 5. Cloud providers: Google, OpenRouter (with test credentials in CI only)

# 6. Measure latency
for endpoint in searxng firecrawl exa google openrouter; do
  for i in {1..10}; do
    time curl -s -X POST $endpoint ... 2>&1 | grep -E "real|user|sys"
  done
done
```

**Deliverable**: `data/coordination/endpoint_validation_20260721.json` with latency_p50, latency_p99, success_rate

### Day 12: Contract Test Suite for MCP Tools

**File**: `tests/integration/test_mcp_chain.py` (new)

**Pattern**: End-to-end contract tests verifying the full chain with `GenerateResult` validation.

```python
class TestMCPChain:
    """Test the full MCP integration chain with empirical validation"""
    
    async def test_oracle_talk_local_first(self):
        """Verify oracle_talk respects local-first and returns correct provenance"""
        result = await oracle_talk("What is 2+2?")
        
        # M21: Gate Integrity - isinstance check
        assert isinstance(result, GenerateResult)
        
        # M22: Response Provenance - provider_name must match actual backend
        assert result.provider_name in ["native-gguf", "lmster", "ollama"]
        assert result.provider_name == result.backend  # From oracle_talk response
        
        # M9: Error Integrity - must be OmegaError subtype on failure
        # (tested in separate failure test)
        
        # Basic validity
        assert result.text is not None
        assert result.trace_id is not None
        assert result.latency_ms >= 0
    
    async def test_fallback_chain_order(self):
        """Verify local providers tried before cloud when healthy"""
        # Saturate local providers with 4 concurrent requests
        # 5th request should go to cloud
        # Verify provider_name in GenerateResult
        
    async def test_error_propagation(self):
        """Force provider failure → verify OmegaError with trace_id"""
        # Mock provider failure
        # Call oracle_talk
        # Verify result is OmegaError subtype
        # Verify trace_id preserved
    
    async def test_hivemind_post_context_integrity(self):
        """Verify hivemind_post_context writes to hot and cold store"""
        # Call hivemind_post_context
        # Verify entry in hot store (in-memory)
        # Verify entry in cold store (HALL_OF_RECORDS)
        # Verify timestamp consistency
```

**Tests**:
- 100% coverage of MCP tool paths
- Property-based tests for error conditions
- Performance benchmarks for each tool
- Failure injection tests

**Deliverable**: `tests/integration/test_mcp_chain.py` + updated `conftest.py` for fixtures

### Day 13: Hard-Failure Implementation

**Action**: Replace all soft-failures with hard-failures per M23.

**Patterns to Replace**:
1. **Bare except:** → Specific exception types + logging + re-raise
2. **except Exception: without logging** → Log with `logger.exception()` + re-raise `OmegaError`
3. **Soft-fail fallbacks** → `[TOOL-CHAIN-COLLAPSE]` + documentation in `SYSTEM_FAILURE_LOG.md`

**Example Transformation**:
```python
# BEFORE (soft-failure)
try:
    result = await some_operation()
except Exception:
    logger.warning("Operation failed, continuing")
    return default_value

# AFTER (hard-failure per M23)
try:
    result = await some_operation()
except SpecificError as e:
    logger.error(f"Specific operation failed: {e}")
    raise OmegaError(f"Specific operation failed: {e}") from e
except Exception as e:
    logger.exception(f"Unexpected error in operation: {e}")
    raise OmegaError(f"Operation failed: {e}") from e
```

**Critical Paths to Fix**:
- MCP server startup/shutdown
- Provider fabric proxy_request
- Hivemind context persistence
- Tool execution wrappers (`m9_safe` decorator validation)

**Deliverable**: Patched files in `mcp_servers/omega_hub/` with hard-failure patterns

### Day 14: Verification & Gate Check

**Verification Suite**:
```bash
# 1. Run contract test suite
make test-mcp-chain  # New make target

# 2. Verify local-first enforcement
# Saturate local providers → verify cloud fallback only when needed

# 3. Verify hard-failures
# Force provider failure → verify [TOOL-CHAIN-COLLAPSE] logged, not silent fallback

# 4. Verify M22 Response Provenance
# Check that provider_name in GenerateResult matches actual backend used

# 5. Performance regression test
# Ensure no >20% latency increase from baseline
```

**Gate Criteria (Phase 2 → Phase 3)**:
- [ ] Integration vulnerability report completed and remediated
- [ ] Provider fabric implements local-first enforcement with admission control
- [ ] MCP client is configurable (not hardcoded)
- [ ] All MCP-dependent endpoints validated and responding < 500ms
- [ ] Contract test suite covers 100% of MCP tool paths
- [ ] M22 Response Provenance verified: `provider_name` matches actual backend
- [ ] All soft-failures replaced with hard-failures per M23
- [ ] No regression in test suite performance (>20% latency increase)

---

## 📊 Phase 2 Artifacts (All Must Exist Before Phase 3)

| Artifact | Location | Purpose |
|----------|----------|---------|
| Vulnerability Report | `data/coordination/integration_vulnerability_report_*.md` | Audit findings |
| Provider Fabric | `mcp_servers/omega_hub/gateway/provider_fabric.py` | Local-first enforcement |
| Updated MCP Client | `mcp_servers/omega_hub/mcp_client.py` | Configurable endpoint |
| Endpoint Validation | `data/coordination/endpoint_validation_*.json` | Health & latency metrics |
| Contract Test Suite | `tests/integration/test_mcp_chain.py` | Full chain validation |
| Hard-Failure Patched Files | `mcp_servers/omega_hub/*.py` | M23 compliance |
| Make Target | `Makefile:test-mcp-chain` | Runs MCP contract tests |
| Validation Scripts | `scripts/verify_mcp_*.sh` | Automated checks |

---

## ⚠️ Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Local-first enforcement breaks existing workflows | **MEDIUM** | Integration errors | Configurable strictness level, gradual rollout |
| Provider fabric adds latency | **LOW** | Performance regression | Benchmark before/after, optimize critical path |
| SearXNG MCP server downtime during validation | **MEDIUM** | Audit delay | Document in `SYSTEM_FAILURE_LOG.md`, proceed with available endpoints |
| Contract tests expose hidden bugs | **HIGH** | Schedule delay | Fix bugs immediately, don't skip tests |
| Hard-failure implementation too strict | **MEDIUM** | False positives | Start with logging-only mode, enforce after validation |

---

## 📋 Confidence: 9/10
**Primary Source**: C-4a deadline (7-day starting today), M23 Failure Integrity, M9 Error Integrity, M22 Response Provenance, M7 Local-First mandate.

**This phase is critical path. If MCP integration fails, the engine cannot communicate with external systems or coordinate agents.**

---

**Next**: See `PART_04_PHASE_3_REFACTORING.md` for Phase 3 detailed actions.