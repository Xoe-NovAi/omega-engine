---
schema_version: "3.0"
document_type: "research_guide_manual"
document_id: "r-c11-property-test-patterns-20260723"
title: "Comprehensive Research Campaign Manual: C-11 Property Test Patterns for OOMProtector + SoulStore"
status: "ACTIVE"
version: "1.0.0"
date: "2026-07-23"
owner: "roc_racoon"
tags: ["research", "phase-c", "p0-tickets", "guard-and-distill", "property-testing", "hypothesis", "oom-protector", "soul-store", "async-patterns"]
priority: "P0"
cross_references:
  - "docs/sprints/guard-and-distill/index.md"
  - "docs/sprints/guard-and-distill/02-p0-tickets/C-11-property-tests.md"
  - "docs/sprints/guard-and-distill/08-verified-findings.md"
  - "docs/research/R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md"
  - "AGENTS.md"
  - "SOVEREIGN_MANDATES.md"
llm_metadata:
  token_budget: 6000
  chunk_strategy: "section_per_domain"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Comprehensive Research Campaign Manual: C-11 Property Test Patterns
**AP Token**: `AP-RESEARCH-C11-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ ACTIVE ⬡ 2026-07-23

## §1 Executive Summary

This manual provides an exhaustive, executable search strategy for **C-11 Property Tests** — implementing Hypothesis non-stateful `@given` async property tests for:
1. **OOMProtector**: 3-signal fusion thresholds (PSI + MemAvailable + cgroups) under load
2. **SoulStore**: Atomic write invariants under concurrent access + crash recovery

**Critical Constraint (Verified Finding §2.1)**: Hypothesis 6.159.0 does **NOT** support async `RuleBasedStateMachine`. Use **non-stateful `@given` async property tests** with `pytest-asyncio` + `anyio_mode=auto` (proven working in `tests/property/test_breaker_fsm.py`).

**Mandate Alignment**: M1 (AnyIO Absolute), M11 (Soul Integrity), M13 (Temple-Grade), M23 (Failure Integrity).

---

## §2 Execution Strategy (Sovereign Search Protocol)

Agents executing this guide MUST follow the T0-T6 search tier protocol:

| Tier | Tool | Scope | When to Use |
|------|------|-------|-------------|
| **T0** | Local cache (`.firecrawl/`) | Free | Check before any external search |
| **T1** | `websearch` | Free, built-in | **Primary search tool** — always available |
| **T2** | `webfetch` | Free, built-in | **Deep extraction** of specific docs |
| **T3** | `searxng_searxng_search` | Free, sovereign | Semantic/neural refinement |
| **T4** | `omega-hub_library_web_search` | API key (Exa) | High-precision seeds, academic/technical |
| **T5** | `firecrawl_firecrawl_scrape/search` | Credits | Full-page scrape, structured crawl |
| **T6** | `sieve research` | Local-first | Full pipeline (T1→T2→T3), zero API keys |

**Fallback chain**: `websearch` → `webfetch` → `searxng_searxng_search` → `omega-hub_library_web_search` → `firecrawl_firecrawl_search` → `sieve research`

**TEMPORAL MANDATE**: It is **2026**. All queries MUST include "2026" or "latest". NO "2024" or "2025".

**HARD-STOP RULE (M23)**: If all tools fail → `[TOOL-CHAIN-COLLAPSE]`. NO simulated rigor.

---

## §3 Exhaustive Research Domains & Search Vectors

### 🛡️ Domain 1: OOMProtector 3-Signal Fusion Properties (Sync Logic)
**Technical Context**: `OOMProtector._fuse_signals()` is pure sync logic that takes a `PressureSnapshot` (PSI some/full avg10/60/300, MemAvailable GB, cgroup pressure) and returns `AdmissionResult` enum. No I/O in this function — testable with crafted snapshots. Thresholds: `min_reserve_gb=2.0`, `throttle_gb=4.0`, `psi_full_avg10 > 0.05` → thrashing.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Monotonicity Properties** | `hypothesis property test monotonic function "more pressure" "higher risk" 2026` | `property-based testing monotonicity invariant python hypothesis` |
| **Threshold Boundary Testing** | `hypothesis @given boundary testing "edge case" threshold 2026` | `hypothesis strategies floats integers boundary values testing` |
| **Enum Return Validation** | `hypothesis test function returns valid enum value all inputs 2026` | `property test return type enum hypothesis python` |
| **Priority Ordering Invariants** | `hypothesis property test priority ordering "A beats B beats C" 2026` | `property based testing priority logic invariant hypothesis` |
| **PressureSnapshot Strategies** | `hypothesis strategies composite dataclass PressureSnapshot 2026` | `hypothesis from_type dataclass strategy generation` |
| **OOM Killer Linux Kernel** | `site:kernel.org "oom_score_adj" "MemAvailable" pressure stall 2026` | `linux kernel oom killer memory pressure PSI cgroups v2` |

**Extraction Targets:**
- [ ] Exact `PressureSnapshot` field ranges for realistic test data generation
- [ ] Mathematical proof that `_fuse_signals()` is monotonic in each pressure dimension
- [ ] Boundary values where `AdmissionResult` transitions (DENY_OOM_RISK → DENY_THRASHING → THROTTLE → ALLOW)
- [ ] Hypothesis strategy patterns for composite dataclasses with constrained fields
- [ ] Linux kernel PSI (Pressure Stall Information) semantics for `avg10`, `avg60`, `avg300`

---

### 💾 Domain 2: SoulStore Atomic Write Invariants (Async + Crash Recovery)
**Technical Context**: `SoulStore.write_atomic(path, str)` + `read_with_recovery(path)` using `os.replace()` + `fcntl.flock()` + backup rotation (`.1.bak`, `.2.bak`). **Known M1 violations**: `fcntl.flock()` blocks event loop, `read_with_recovery()` uses sync `path.read_text()`, `_rotate_backups()` uses sync `shutil.copy2()`. Tests use `tempfile.mkdtemp()` inside each test (no pytest fixtures with `@given`).

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Atomic Write Patterns** | `python "os.replace" atomic write crash recovery property test 2026` | `atomic file write python os.replace hypothesis property test` |
| **Concurrent Read During Write** | `hypothesis test "read during write" atomic visibility old OR new 2026` | `property test concurrent file read atomic write python` |
| **Temp File Cleanup** | `hypothesis property test "no temp files leaked" cleanup 2026` | `property test file cleanup guarantee hypothesis python` |
| **Backup Rotation Invariants** | `file backup rotation .1.bak .2.bak property test hypothesis 2026` | `backup rotation algorithm property based testing` |
| **Crash Recovery Simulation** | `property test "simulate crash mid-write" recovery fallback 2026` | `crash recovery file system property test hypothesis` |
| **fcntl.flock Async Wrapper** | `anyio.to_thread.run_sync fcntl.flock non-blocking 2026` | `python async file locking fcntl anyio thread` |
| **Empty/Whitespace Content** | `hypothesis test empty string round trip file write 2026` | `property test edge case empty content file write` |

**Extraction Targets:**
- [ ] Proven Hypothesis strategy for generating valid YAML-like content strings
- [ ] Pattern for `tempfile.mkdtemp()` inside `@given` test body (avoiding fixture HealthCheck)
- [ ] `anyio.to_thread.run_sync()` wrapper for `fcntl.flock()` to fix M1 violation
- [ ] Property test for "read returns old OR new, never partial" under concurrent access
- [ ] Backup rotation invariant: `.1.bak` contains SAME content as main (not previous)
- [ ] Recovery test: delete main file → `read_with_recovery()` falls back to `.1.bak`

---

### ⚡ Domain 3: Hypothesis Async Patterns (Non-Stateful @given)
**Technical Context**: Verified finding — `RuleBasedStateMachine` does NOT support async. Working pattern: `@pytest.mark.anyio` + `@given` + `async def test_...` with `anyio_mode=auto`. Proven in `test_breaker_fsm.py`.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Async @given Pattern** | `hypothesis @given async function pytest-asyncio anyio_mode 2026` | `hypothesis async property test pytest anyio working pattern` |
| **anyio_mode Configuration** | `pytest-asyncio anyio_mode auto hypothesis integration 2026` | `pytest.ini anyio_mode hypothesis async tests` |
| **CancelScope Shielding** | `anyio.CancelScope shield=True atomic file write 2026` | `anyio cancel scope shield file operation hypothesis test` |
| **TaskGroup for Concurrency** | `anyio.create_task_group concurrent file access hypothesis 2026` | `anyio task group property test concurrent access` |
| **HealthCheck Suppression** | `hypothesis suppress_health_check too_slow function_scoped_fixture 2026` | `hypothesis HealthCheck.too_slow deadline=None CI` |
| **Derandomize for CI** | `hypothesis derandomize=True max_examples 500 CI profile 2026` | `hypothesis settings profile CI deterministic` |

**Extraction Targets:**
- [ ] Exact decorator order: `@pytest.mark.anyio` BEFORE `@given` (proven in test_breaker_fsm.py)
- [ ] `anyio_mode="auto"` in pytest.ini or pyproject.toml
- [ ] `CancelScope(shield=True)` pattern for protecting atomic writes from cancellation
- [ ] `anyio.create_task_group()` for concurrent read/write property tests
- [ ] `@settings(max_examples=500, derandomize=True, deadline=None, suppress_health_check=[HealthCheck.too_slow])`
- [ ] Hypothesis profile registration in `tests/property/conftest.py`

---

### 🔧 Domain 4: Implementation-Specific Patterns (Omega Engine Codebase)
**Technical Context**: Existing working patterns in `tests/property/test_breaker_fsm.py` and `tests/property/test_oom_protector_fuse.py` (to be created). SoulStore has M1 violations that need fixing but not blocking C-11 MVP.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **OOMProtector Config** | `site:github.com "OOMProtectorConfig" "min_reserve_gb" 2026` | `omega-engine OOMProtectorConfig thresholds` |
| **PressureSnapshot Fields** | `site:github.com "PressureSnapshot" "psi_some_avg10" 2026` | `omega-engine PressureSnapshot dataclass fields` |
| **SoulStore API** | `site:github.com "SoulStore" "write_atomic" "read_with_recovery" 2026` | `omega-engine SoulStore atomic write API` |
| **AdmissionResult Enum** | `site:github.com "AdmissionResult" "DENY_OOM_RISK" 2026` | `omega-engine AdmissionResult enum values` |
| **Test Breaker FSM Pattern** | `site:github.com "test_breaker_fsm.py" "anyio" "hypothesis" 2026` | `omega-engine tests/property/test_breaker_fsm.py` |

**Extraction Targets:**
- [ ] Exact `OOMProtectorConfig` defaults and field types
- [ ] Exact `PressureSnapshot` dataclass definition with all fields
- [ ] Exact `SoulStore.write_atomic(path, str)` and `read_with_recovery(path)` signatures
- [ ] Exact `AdmissionResult` enum members: `ALLOW`, `THROTTLE`, `DENY_OOM_RISK`, `DENY_THRASHING`
- [ ] Working test pattern from `test_breaker_fsm.py` for async property tests

---

### 📋 Domain 5: CI/CD Integration & Flakiness Prevention
**Technical Context**: Property tests must run reliably in CI with 500 examples, derandomized, no flakiness.

| Vector | Primary Query (Advanced Dorks) | Fallback Query / Target Source |
|--------|--------------------------------|--------------------------------|
| **Hypothesis CI Profile** | `hypothesis register_profile ci max_examples derandomize 2026` | `hypothesis settings profile CI deterministic` |
| **GitHub Actions Hypothesis** | `github actions hypothesis property test cache database 2026` | `hypothesis database github actions cache` |
| **Flakiness Prevention** | `hypothesis flaky test prevention deadline None too_slow 2026` | `hypothesis prevent flaky tests CI` |
| **Example Database** | `hypothesis example database .hypothesis gitignore 2026` | `hypothesis example database commit or ignore` |

**Extraction Targets:**
- [ ] `conftest.py` profile registration for "ci" and "dev" profiles
- [ ] GitHub Actions workflow step for running property tests
- [ ] `.hypothesis/` directory gitignore strategy
- [ ] `deadline=None` for I/O-bound async tests

---

## §4 Synthesis & Reporting Protocol

1. **Execute Sequentially**: Do not parallelize across domains to maintain focus. Complete Domain 1, then Domain 2, etc.
2. **Log Verbatim**: Record exact URLs, code snippets, and standard RFC numbers.
3. **Distill**: Translate raw findings into actionable technical decisions for the Omega Engine.
4. **Update Tickets**: Inject the verified patterns directly into the P0 tickets (`C-11-property-tests.md`).
5. **Gate**: Proceed to code execution ONLY when all Extraction Targets for a specific ticket are checked and verified.
6. **Hivemind Post**: Post synthesis to Hivemind with `intent: decision` for team awareness.

---

## §5 Quick Reference: Proven Working Patterns (From Codebase)

### Pattern A: Async @given Property Test (from test_breaker_fsm.py)
```python
@pytest.mark.anyio
@given(
    mode=st.sampled_from(["cusum", "sliding_window"]),
    failures=st.integers(min_value=1, max_value=15),
)
@settings(max_examples=30)
async def test_failures_trip_circuit(self, mode: str, failures: int):
    breaker = AsyncCircuitBreaker(...)
    for _ in range(failures):
        async def _fail():
            raise ConnectionError("simulated")
        try:
            await breaker.call(_fail)
        except (ConnectionError, CircuitOpenError):
            pass
    # assertions...
```

### Pattern B: Sync Property Test for Pure Logic (from test_breaker_fsm.py)
```python
class Breaker429Machine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.breaker = AsyncCircuitBreaker("test", failure_threshold=3)

    @rule()
    def record_429_rate_limit(self):
        state_before = self.breaker.state
        self.breaker.record_429(retry_after=30.0, response_body="rate limit")
        assert self.breaker.state == state_before
```

### Pattern C: Temp Dir Inside Test (No Fixtures)
```python
@pytest.mark.anyio
@given(content=yaml_content)
@settings(max_examples=500, derandomize=True, deadline=None)
async def test_round_trip(content: str):
    store = SoulStore()
    tmp_dir = Path(tempfile.mkdtemp())  # NOT tmp_path fixture!
    path = tmp_dir / "soul.yaml"
    await store.write_atomic(path, content)
    result = await store.read_with_recovery(path)
    assert result == content
```

---

## §6 Environment Verification (Pre-Research)

| Package | Required Version | Verification Command |
|---------|------------------|---------------------|
| `anyio` | >= 4.13.0 | `python -c "import anyio; print(anyio.__version__)"` |
| `hypothesis` | >= 6.100.0 | `python -c "import hypothesis; print(hypothesis.__version__)"` |
| `pytest` | >= 9.0.0 | `python -c "import pytest; print(pytest.__version__)"` |
| `pytest-asyncio` | NOT in main project | AnyIO pytest plugin used instead |
| `anyio_mode` | "auto" | Check `pyproject.toml` or `pytest.ini` |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ RESEARCH-GUIDE-C11 ⬡ 2026-07-23*
*AP Token: `AP-RESEARCH-C11-PATTERNS-v1.0.0`*