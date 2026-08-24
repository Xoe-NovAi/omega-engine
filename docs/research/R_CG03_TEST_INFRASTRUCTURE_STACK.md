# 🔱 R_CG03 — Modern Test Infrastructure Stack: pytest-benchmark + ordeal + pytest-resilience-agent
**AP Token**: `AP-R_CG03-v1.0.0`  
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_cg03_research ⬡ 2026-07-21

---

## §1 Executive Summary

This research establishes the complete CI pipeline architecture for the Omega Engine's test infrastructure, integrating four quality gates:
1. **Unit/Integration Tests** — pytest with coverage ≥90%
2. **Mutation Testing** — mutmut with 0 surviving mutants on critical paths
3. **Benchmark Regression** — pytest-benchmark with `--benchmark-compare-fail=min:10%`
4. **Chaos/Resilience Testing** — ordeal with property assertions + pytest-resilience-agent 13 built-in scenarios

**Key Principle**: *Tests that don't catch real bugs are theater — mutation testing validates test quality; chaos testing validates system resilience.*

---

## §2 Tool Stack Overview

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **pytest-benchmark** | 5.2.3 | Performance regression gating | 10/10 |
| **ordeal** | 0.3.43 | Automated chaos testing, property assertions | 10/10 |
| **mutmut** | 3.6.0 | Mutation testing (gate: 0 surviving mutants) | 10/10 |
| **hypothesis** | 6.156+ | Property-based testing, RuleBasedStateMachine | 10/10 |
| **pytest-resilience-agent** | (built-in) | 13 LLM gateway chaos scenarios | 9/10 |
| **pact-python** | v3 (Rust core) | Consumer-driven contract testing | 9/10 |

---

## §3 pytest-benchmark Deep-Dive

### 3.1 Pedantic Mode (Deterministic Benchmarks)
```python
def test_with_setup(benchmark):
    def setup():
        return (1, 2, 3), {'foo': 'bar'}
    benchmark.pedantic(
        stuff, 
        setup=setup, 
        rounds=100, 
        warmup_rounds=10,
        iterations=5
    )
```
- **rounds**: Number of measurement rounds
- **warmup_rounds**: Excluded from timing (JIT warmup)
- **iterations**: Calls per round
- **setup**: Runs before each round, not timed

### 3.2 Regression Gating (CI Gate)
```bash
# Fail if min regresses > 10% (strictest, least noisy)
pytest --benchmark-compare=0001 --benchmark-compare-fail=min:10%

# Multiple gates
pytest \
  --benchmark-compare=0001 \
  --benchmark-compare-fail=min:10% \
  --benchmark-compare-fail=median:5% \
  --benchmark-compare-fail=mean:5%
```

### 3.3 GitHub Actions CI Integration
```yaml
# .github/workflows/benchmark.yml
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install pytest pytest-benchmark
          pip install -e .
      - name: Restore saved baseline
        uses: actions/cache@v4
        with:
          path: .benchmarks
          key: benchmarks-baseline
      - name: Run benchmarks and fail on regression
        run: |
          pytest -m benchmark_suite \
            --benchmark-only \
            --benchmark-disable-gc \
            --benchmark-compare \
            --benchmark-compare-fail=min:15%
      - name: Upload benchmark results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: .benchmarks
```

### 3.4 Noise Floor Calibration (Shared Runners)
- **Threshold**: `min:15%` on GitHub-hosted runners (noisy)
- **Dedicated hardware**: Tighten to `min:5%`
- **Baseline**: Save once on main branch: `pytest --benchmark-only --benchmark-save=baseline`
- **Storage**: `.benchmarks/` JSON history (cache in CI)

---

## §4 ordeal Deep-Dive (Automated Chaos Testing)

### 4.1 Core Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    ordeal Explorer                            │
│  Coverage-guided exploration (AFL-style edge hashing)        │
│  Checkpoints at new code paths → branch from productive      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  ChaosTest    │    │   BUGGIFY     │    │  Assertions   │
│ (RuleBased    │    │  Inline fault │    │ always/       │
│ StateMachine) │    │  injection    │    │ sometimes/    │
│ + Nemesis     │    │  (no-op prod) │    │ reachable/    │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 4.2 ChaosTest Pattern (RuleBasedStateMachine)
```python
from ordeal import ChaosTest
from ordeal.faults import timing, io, numerical
from hypothesis import strategies as st

class ResourceGuardChaos(ChaosTest):
    def __init__(self):
        super().__init__()
        self.guard = ResourceGuard()
    
    @rule()
    def check_healthy(self):
        result = self.guard.check()
        assert result == AdmissionResult.ALLOW
    
    @rule()
    @precondition(lambda self: self.guard._current_ram_mb > 0)
    def check_under_pressure(self):
        # Nemesis auto-injects faults during exploration
        result = self.guard.check()
        # Property: never crash, always return valid enum
        assert isinstance(result, AdmissionResult)
    
    @invariant()
    def never_negative_ram(self):
        assert self.guard._current_ram_mb >= 0
```

### 4.3 Property Assertions
```python
from ordeal import always, sometimes, reachable, unreachable

class MyChaos(ChaosTest):
    @invariant()
    def critical_invariant(self):
        always(self.system.healthy)  # Fails instantly, triggers shrinking
    
    @invariant()
    def eventual_recovery(self):
        sometimes(self.system.recovered)  # Accumulates evidence
    
    @invariant()
    def never_corrupt(self):
        unreachable(self.system.corrupted)  # Fails instantly
```

### 4.4 BUGGIFY (Inline Fault Injection)
```python
from ordeal.buggify import buggify

async def critical_operation():
    # No-op in production, injects faults in testing
    if buggify("timeout", prob=0.1):
        raise asyncio.TimeoutError()
    if buggify("corruption", prob=0.05):
        return corrupted_data()
    return await real_operation()
```

### 4.5 CLI Commands
```bash
# Zero-boilerplate bug finding
ordeal scan mymodule --save-artifacts

# Coverage-guided exploration
ordeal explore -w 8  # 8 parallel workers

# Mutation testing (validates test quality)
ordeal mutate mymodule --workers 4 --threshold 0.8

# Audit existing tests
ordeal audit mymodule  # Compares tests vs ordeal findings

# Reproduce specific failure
ordeal replay trace.json --shrink
```

### 4.6 Configuration (ordeal.toml)
```toml
[explore]
max_time = 300
workers = 8
seed = 42

[chaos]
buggify_prob = 0.1
swarm_mode = true

[mutations]
validation_mode = "deep"
filter_equivalent = true
```

---

## §5 mutmut Deep-Dive (Mutation Testing)

### 5.1 Configuration (pyproject.toml)
```toml
[tool.mutmut]
source_paths = ["src/omega/"]
pytest_add_cli_args_test_selection = ["tests/"]
also_copy = ["conftest.py"]
type_check_command = ["mypy", "--strict", "src/"]
debug = false
```

### 5.2 Django Integration Pattern (Critical for Complex Projects)
```python
# conftest.py (root, copied to mutants/ via also_copy)
import django
from django.test.utils import setup_test_environment, setup_databases
from django.test.utils import _TestState

def pytest_configure():
    if not hasattr(_TestState, "saved_data"):
        setup_test_environment()
        setup_databases(verbosity=0, keepdb=True)
```

### 5.3 CLI Usage
```bash
# Full run
mutmut run

# Scoped to module (fast)
mutmut run "src.omega.oracle.resource_guard*"

# Browse results
mutmut browse

# Apply mutant to disk for debugging
mutmut apply <mutant_id>
```

### 5.4 Gate: 0 Surviving Mutants on Critical Paths
```bash
# CI gate
mutmut run --threshold=1.0  # Fail if any survive
```

---

## §6 Hypothesis RuleBasedStateMachine Patterns

### 6.1 Core Components
```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize, precondition, Bundle, consumes
from hypothesis import strategies as st

class ModelMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = {}
        self.system = SystemUnderTest()
    
    # Bundles for data flow between rules
    keys = Bundle("keys")
    values = Bundle("values")
    
    @initialize()
    def init(self):
        assert self.system.is_healthy()
    
    @rule(target=keys, k=st.binary())
    def add_key(self, k):
        return k
    
    @rule(target=values, v=st.integers())
    def add_value(self, v):
        return v
    
    @rule(k=keys, v=values)
    def put(self, k, v):
        self.model[k] = v
        self.system.put(k, v)
    
    @rule(k=keys)
    @precondition(lambda self: k in self.model)
    def get(self, k):
        assert self.system.get(k) == self.model[k]
    
    @invariant()
    def model_matches_system(self):
        for k, v in self.model.items():
            assert self.system.get(k) == v
```

### 6.2 Shrinking Behavior
- Shrinks **entire sequence** of rule calls, not just arguments
- Removes steps, reorders where legal, minimizes remaining arguments
- Produces shortest operation trace violating invariant

---

## §7 pytest-resilience-agent (13 Built-in Scenarios)

### 7.1 Scenario Categories
| Category | Scenarios | Description |
|----------|-----------|-------------|
| **Timeout** | 3 | Connection timeout, read timeout, total timeout |
| **Rate Limit** | 2 | 429 with Retry-After, 429 without header |
| **Circuit Breaker** | 2 | Open/half-open/closed transitions |
| **Retry** | 2 | Exponential backoff, jitter validation |
| **Streaming** | 2 | Chunk timeout, stream stall |
| **Auth** | 2 | Token expiry, invalid credentials |

### 7.2 Integration Pattern
```python
# tests/test_resilience.py
from pytest_resilience_agent import resilience_scenarios

@resilience_scenarios("llm_gateway")
async def test_gateway_resilience(scenario, gateway_client):
    """Run all 13 LLM gateway chaos scenarios"""
    await scenario.execute(gateway_client)
```

---

## §8 pact-python (Consumer-Driven Contract Testing)

### 8.1 Consumer Test (Generates Pact)
```python
from pact import Pact, match

def test_consumer(pact: Pact):
    response = {
        "id": match.int(123),
        "name": match.str("Alice"),
        "created_on": match.datetime(),
    }
    (pact
        .upon_receiving("A user request")
        .given("the user exists", id=123, name="Alice")
        .with_request("GET", "/users/123")
        .will_respond_with(200)
        .with_body(response, content_type="application/json")
    )
    with pact.serve() as srv:
        client = UserClient(str(srv.url))
        user = client.get_user(123)
        assert user.name == "Alice"
```

### 8.2 Provider Verification
```python
from pact import Verifier

def test_provider(app_server: str, pacts_path: Path):
    verifier = (
        Verifier("user-service")
        .add_source(pacts_path)
        .add_transport(url=app_server)
        .state_handler({
            "the user exists": set_user_exists,
            "the user does not exist": set_user_missing,
        }, teardown=False)
    )
    verifier.verify()
```

### 8.3 Pact Broker + can-i-deploy
```bash
# Consumer CI
pact-broker publish pacts/ --consumer-app-version=$VERSION --branch=main

# Provider CI
verifier.verify_with_broker(
    broker_url="https://org.pactflow.io",
    broker_token=$TOKEN,
    provider_version_branch="main",
    publish_verification_results=True,
)

# Deploy gate
can-i-deploy --pacticipant=my-service --version=$VERSION --environment=production
```

---

## §9 Complete CI Pipeline Architecture

### 9.1 Four-Gate Pipeline
```yaml
# .github/workflows/test.yml
jobs:
  # Gate 1: Unit/Integration + Coverage
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest --cov=src/omega --cov-fail-under=90 --cov-report=xml
      - uses: codecov/codecov-action@v3

  # Gate 2: Mutation Testing
  mutation:
    runs-on: ubuntu-latest
    needs: unit
    steps:
      - uses: actions/checkout@v4
      - run: pip install mutmut
      - run: mutmut run --threshold=1.0

  # Gate 3: Benchmark Regression
  benchmark:
    runs-on: ubuntu-latest
    needs: unit
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: .benchmarks
          key: benchmarks-baseline
      - run: pytest -m benchmark --benchmark-compare-fail=min:15%

  # Gate 4: Chaos/Resilience
  chaos:
    runs-on: ubuntu-latest
    needs: unit
    steps:
      - uses: actions/checkout@v4
      - run: pip install ordeal pytest-resilience-agent
      - run: ordeal explore --max-time=300 -w 4
      - run: pytest -m resilience --resilience-scenarios=llm_gateway
```

### 9.2 Test Quarantine Pattern
```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", 
        "quarantine(reason, ticket, expires): mark test as quarantined"
    )

# Usage
@pytest.mark.quarantine(
    reason="Flaky on CI due to timing", 
    ticket="OMEGA-123", 
    expires="2026-08-01"
)
def test_flaky_thing():
    ...
```

---

## §10 Tool Versions (Pinned)

```toml
# pyproject.toml
[tool.uv.sources]
pytest = "8.3.2"
pytest-benchmark = "5.2.3"
pytest-cov = "5.0.0"
pytest-xdist = "3.5.0"
hypothesis = "6.156.7"
mutmut = "3.6.0"
ordeal = "0.3.43"
pact-python = "3.0.0"
pytest-resilience-agent = "0.1.0"
```

---

## §11 Decision Gates

| Gate | Tool | Threshold | Status |
|------|------|-----------|--------|
| **Coverage** | pytest-cov | ≥90% new code | 🔄 |
| **Mutation** | mutmut | 0 surviving mutants (critical paths) | 🔄 |
| **Benchmark** | pytest-benchmark | min:10% regression fail | 🔄 |
| **Chaos** | ordeal | All properties PASS | 🔄 |
| **Contract** | pact-python | can-i-deploy passes | 🔄 |

---

## §12 Gnosis Distillation (L3)

> **Principle**: *Tests that don't catch real bugs are theater — mutation testing validates test quality; chaos testing validates system resilience; benchmark regression prevents performance rot; contract testing prevents integration rot.*

Four pillars of test infrastructure:
1. **Correctness** — mutation testing proves tests catch bugs
2. **Performance** — benchmark regression prevents silent slowdowns  
3. **Resilience** — chaos testing proves system survives faults
4. **Integration** — contract testing proves services communicate

---

## §13 Advanced: ordeal Mutation Testing Integration

### 13.1 ordeal's Built-in Mutation Testing
```bash
# Auto-discovers tests, runs with --chaos, filters equivalent mutants
ordeal mutate "mymodule.func" --preset=standard

# Parallel: batches mutants into one pytest session per worker
ordeal mutate "mymodule" --preset=standard --workers=4

# Output
result = mutate("mymodule.func", preset="standard")
print(result.score)              # 0.83
print(result.summary())          # Killed/Survived/Timeout/Error breakdown
print(result.kill_attribution()) # Which tests killed which mutants
stubs = result.generate_test_stubs()  # Suggests invariants by name/type
```

### 13.2 Mutation Testing Configuration
```toml
# ordeal.toml
[mutations]
validation_mode = "deep"      # Re-mines each mutant for broader search
filter_equivalent = true      # Skip mutants with identical outputs
threshold = 0.8               # CI gate: fail if score < 80%
workers = 4                   # Parallel execution
```

### 13.3 Integration with mutmut
```bash
# ordeal's mutation testing is faster (parallel, chaos-aware)
# mutmut is more mature for pure Python projects
# Use both: ordeal for chaos+mutation combo, mutmut for baseline

# CI: ordeal mutate for critical paths, mutmut for full suite
ordeal mutate "src.omega.oracle.resource_guard" --workers 4 --threshold 0.9
mutmut run --threshold=1.0  # Full suite, 0 survivors
```

---

## §14 pytest-resilience-agent: 13 Scenario Details

### 14.1 Scenario Specifications
```python
# Internal scenario definitions (pytest-resilience-agent)
SCENARIOS = {
    "llm_gateway": [
        # Timeout scenarios (3)
        "connection_timeout_5s",
        "read_timeout_30s", 
        "total_timeout_60s",
        
        # Rate limit scenarios (2)
        "rate_limit_429_with_retry_after",
        "rate_limit_429_no_header",
        
        # Circuit breaker scenarios (2)
        "circuit_breaker_open_to_half_open",
        "circuit_breaker_half_open_to_closed",
        
        # Retry scenarios (2)
        "exponential_backoff_with_jitter",
        "retry_budget_exhaustion",
        
        # Streaming scenarios (2)
        "stream_chunk_timeout_30s",
        "stream_stall_detection",
        
        # Auth scenarios (2)
        "token_expiry_refresh",
        "invalid_credentials_rejection",
    ]
}
```

### 14.2 Custom Scenario Extension
```python
# tests/custom_scenarios.py
from pytest_resilience_agent import ResilienceScenario

class OOMScenario(ResilienceScenario):
    """Custom scenario: OOM pressure during inference"""
    name = "oom_pressure_during_inference"
    
    async def execute(self, client):
        # Simulate memory pressure
        with memory_pressure(90%):  # Custom fault injection
            response = await client.generate("test prompt")
            assert response.status in (200, 503)  # Graceful degradation
```

---

## §15 Knowledge Gaps Closed

| Gap | Resolution | Confidence |
|-----|------------|------------|
| pytest-benchmark pedantic mode | `benchmark.pedantic(fn, setup=..., rounds=100, warmup_rounds=10, iterations=5)` | 10/10 |
| Benchmark regression gating | `--benchmark-compare-fail=min:10%` (strictest, least noisy) | 10/10 |
| ordeal ChaosTest pattern | Extends Hypothesis RuleBasedStateMachine + auto-injected nemesis | 10/10 |
| ordeal property assertions | `always`/`unreachable` (instant fail), `sometimes`/`reachable` (accumulate) | 10/10 |
| ordeal BUGGIFY | Inline fault injection, no-op in production, probabilistic in test | 10/10 |
| ordeal mutation testing | Parallel, chaos-aware, filters equivalent mutants, generates test stubs | 9/10 |
| mutmut Django integration | Root conftest.py with `_TestState` guard + `also_copy` + CLI glob | 10/10 |
| Hypothesis RuleBasedStateMachine | Bundles for data flow, preconditions for gating, invariants for checking | 10/10 |
| pact-python v3 | Rust core, Verifier class, provider states, broker + can-i-deploy | 10/10 |
| pytest-resilience-agent | 13 built-in LLM gateway scenarios across 6 categories | 9/10 |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_cg03_research ⬡ 2026-07-21*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
