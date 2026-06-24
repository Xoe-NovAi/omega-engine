# 🔱 P10 VALIDATION REPORT — Epoch I: The Bedrock
**Source**: Lilith (Dark Oversoul) → P7 (Context) → P8 (Observability) → **P10 (Validation — Verifier, Stress Testing & QA)**
**Date**: 2026-06-24
**AP Token**: `AP-P10-EPOCHI-v1.0.0`
**⬡ OMEGA ⬡ P10-VALIDATION ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I**

---

## §1 EXECUTIVE SUMMARY

P10 assessed the Omega Engine's M21 Gate Integrity, cross-pillar validation needs, contract test gap, and validation infrastructure across all Epoch I strikes. This is the synthesis point — the FINAL Pillar in the serial chain, receiving findings from P7 (Context), P8 (Observability), and the Build Side (P1-P3 via Ma'at).

### Overall Verdict: 🟡 CONDITIONAL GO — M21 is 4/24 tests (16.7%)

| Domain | Current | Needed | Gap | Epoch I Priority |
|--------|---------|--------|-----|------------------|
| **M21 Contract Tests** | 4 | 24 | 20 (83% gap) | 🔴 MUST RESOLVE |
| **Soul.yaml validation (P7)** | 0 | 6-8 | Full gap | 🔴 P0 |
| **Observability validation (P8)** | 0 | 6-8 | Full gap | 🔴 P0 |
| **ResourceGuard (P3)** | 0 | 3-4 | Full gap | 🟡 P1 |
| **USM/SomaticState (P3)** | 0 | 4-6 | Full gap (no USM yet) | 🟡 P1 |
| **TUI contract tests (P3)** | 0 | 2-3 | Full gap (no TUI yet) | 🟢 P2 |
| **Additional M21 boundaries** | 0 | 6-8 | Full gap | 🟡 P1 |

**Key finding**: The M21 gap is larger than the strategic docs projected. The 4 existing tests cover only `ModelGateway.generate()` and `Oracle.talk()` boundaries. **Zero tests exist for observability, soul.yaml, ResourceGuard, MemoryStore, EntityRegistry, HealthMonitor, or SomaticState**. However, the foundation is structurally sound — the test patterns (`pytest.mark.anyio`, `_run()` helper, `conftest.py` fixtures) are proven and consistent. The gap is coverage breadth, not infrastructure quality.

**Three critical dependencies for P10 to proceed**:
1. **P2 must update `soul_validator.py` to v6.1** — without a target schema, soul template tests cannot validate
2. **P3's USM and TUI must be built** — several contract tests are design-time (can be written in parallel but not executed)
3. **P8 must wire observability hooks** — observability contract tests validate behavior that P8 is still implementing

---

## §2 M21 GATE INTEGRITY ASSESSMENT

### 2.1 Current State — 4 Contract Tests (16.7% of 24)

The existing `tests/test_contract_m21.py` contains 4 tests covering 2 API boundaries:

| # | Test | Boundary | Type | Validates |
|---|------|----------|------|-----------|
| 1 | `test_generate_returns_generateresult` | `ModelGateway.generate()` | Positive contract | Returns `GenerateResult` (not str/tuple) |
| 2 | `test_talk_returns_oracleresponse` | `Oracle.talk()` | Positive contract | Returns `OracleResponse` (not raw str) |
| 3 | `test_generateresult_has_required_fields` | `GenerateResult` dataclass | Field contract | `text`, `provider_name`, `is_cloud`, `latency_ms`, `model_used` all correct type |
| 4 | `test_talk_does_not_return_generateresult` | `Oracle.talk()` | Negative contract | Does NOT return `GenerateResult` (regression guard) |

**What these tests get RIGHT:**
- Uses real `isinstance()` checks against actual dataclasses — no mocks masking type drift
- Tests both positive (returns the right type) and negative (doesn't return the wrong type) contracts
- `_run()` pattern in `conftest.py` is consistent with the rest of the test suite
- Clear docstrings explaining M21 mandate and why each test exists

**What these tests MISS:**
- Only 2 of ~12 core API boundaries are covered (ModelGateway, Oracle)
- No observability boundaries tested (`log_event()`, `record()`, `stats()`)
- No entity boundaries tested (`EntityRegistry.get()`, `EntityRegistry.add()`)
- No memory boundaries tested (`MemoryStore.add_exchange()`, `MemoryStore.get_history()`)
- No health monitor boundaries tested (`HealthMonitor.is_available()`, circuit breaker states)
- No session boundaries tested (`SessionManager.create_session()`, `SessionManager.close_session()`)
- No ResourceGuard boundaries tested (`lock()`, capacity tracking)
- No SomaticState boundaries tested (serialization round-trip)
- No YAML/soul boundaries tested (soul.yaml parse, proposed_lessons.yaml format)
- No search/query boundaries tested

### 2.2 Gap Analysis — 20 Contract Tests Needed

The M21 mandate requires **24 total contract tests** covering all core API boundaries. Below is the complete prioritized gap analysis.

#### Tier 1: 🔴 P0 — Epoch I Gate Critical (6-8 tests)

| ID | Boundary | Test Type | What to Validate | Est. Effort | Depends On |
|----|----------|-----------|-----------------|-------------|------------|
| CT-01 | `yaml.safe_load(soul.yaml)` | Parse contract | All 34 souls parse as valid YAML dict | 1h | P2 soul_validator v6.1 |
| CT-02 | v6.1 soul schema validation | Schema contract | soul.yaml has identity/directives/team blocks + soul_version | 1h | P2 soul_validator v6.1 |
| CT-03 | `ObservabilityEngine.log_event()` | Structure contract | Returns event with `_zoneid`, `trace_id`, `timestamp`, `event`, `data` | 0.5h | P8 hook wiring |
| CT-04 | `ObservabilityEngine.record_training_example()` | Field contract | Example has `metadata.backend` as str, `trace_id` as str | 0.5h | P8 hook wiring |
| CT-05 | `GenerateResult.provider_name` non-empty | Field contract | `provider_name` is never None, never empty, always str | 0.5h | None |
| CT-06 | `OracleResponse` has required fields | Field contract | `text` (str), `entity` (str), `confidence` (float), `trace_id` (str) | 0.5h | None |
| **Tier 1 subtotal** | | | | **4h** | |

#### Tier 2: 🟡 P1 — Epoch I Scope (8-10 tests)

| ID | Boundary | Test Type | What to Validate | Est. Effort | Depends On |
|----|----------|-----------|-----------------|-------------|------------|
| CT-07 | `EntityRegistry.get()` | Return type contract | Returns Entity (not None, not dict) | 0.5h | None |
| CT-08 | `EntityRegistry.add()` | Return type contract | Returns Entity (confirms registration) | 0.5h | None |
| CT-09 | `MemoryStore.add_exchange()` | Return type contract | Returns success indicator (bool) | 0.5h | None |
| CT-10 | `MemoryStore.get_history()` | Return type contract | Returns list of exchanges | 0.5h | None |
| CT-11 | `HealthMonitor.is_available()` | Return type contract | Returns bool (not None, not int) | 0.5h | None |
| CT-12 | `SessionManager.create_session()` | Return type contract | Returns session_id (str) | 0.5h | None |
| CT-13 | `SessionManager.close_session()` | Return type contract | Completes without error | 0.5h | None |
| CT-14 | `ResourceGuard.lock()` | Async context contract | Acquires/releases, returns context manager | 1h | None |
| CT-15 | `ResourceGuard` re-entrancy | Behavior contract | Same task re-entering doesn't deadlock | 0.5h | None |
| CT-16 | `proposed_lessons.yaml` format | Schema contract | Has `proposals:` dict, each proposal has required fields | 0.5h | P3 batch converter |
| **Tier 2 subtotal** | | | | **5h** | |

#### Tier 3: 🟡 P1 — USM/SomaticState (4-6 tests)

| ID | Boundary | Test Type | What to Validate | Est. Effort | Depends On |
|----|----------|-----------|-----------------|-------------|------------|
| CT-17 | `SomaticState.serialize()` round-trip | Serialization contract | serialize → deserialize returns identical state | 1h | P3 USM build |
| CT-18 | `CASBlobStore.put()`/`get()` | CAS contract | Store and retrieve binary blob by hash | 0.5h | P3 USM build |
| CT-19 | `SomaticStateKey` dataclass | Field contract | Has `blob_hash` (str), `entity` (str), `timestamp` (str) | 0.5h | P3 USM build |
| CT-20 | ZONEID_SOMATIC header validation | ZONEID contract | Serialized blob header contains `0x1d4a1c` magic | 0.5h | P3 USM build |
| CT-21 | `UnifiedStateManager.snapshot()` | Return type contract | Returns valid SomaticStateKey | 0.5h | P3 USM build |
| CT-22 | `UnifiedStateManager.restore()` | Return type contract | Completes without error | 0.5h | P3 USM build |
| **Tier 3 subtotal** | | | | **3.5h** | |

#### Tier 4: 🟢 P2 — Nice to Have / Epoch II (2-3 tests)

| ID | Boundary | Test Type | What to Validate | Est. Effort | Depends On |
|----|----------|-----------|-----------------|-------------|------------|
| CT-23 | TUI YAML diff engine output | Output contract | Diff produces valid unified diff format | 0.5h | P3 TUI build |
| CT-24 | TUI approval workflow | State contract | Approved → promoted → removed from pending | 0.5h | P3 TUI build |
| CT-25 | `__aexit__` trace_id propagation | Async contract | Provider receives trace_id from caller | 0.5h | None (lower priority) |
| **Tier 4 subtotal** | | | | **1.5h** | |

### 2.3 Effort Estimate by Domain

| Domain | Tests | Effort | Epoch I Impacted | Priority |
|--------|-------|--------|------------------|----------|
| **Soul.yaml validation** (P7/Strike 1) | 6-8 | 3h | ✅ Direct | 🔴 P0 |
| **Observability contracts** (P8/M22) | 6-8 | 2h | ✅ Direct | 🔴 P0 |
| **ResourceGuard** (P3) | 3-4 | 1h | ✅ Direct | 🟡 P1 |
| **Core API boundaries** (EntityRegistry, MemoryStore, HealthMonitor, SessionManager) | 6-8 | 3h | ⭕ Indirect (M21 completeness) | 🟡 P1 |
| **USM/SomaticState** (P3 Strike 2) | 4-6 | 2h | ⏳ Must be built first | 🟡 P1 |
| **TUI contracts** (P3 Strike 3) | 2-3 | 1h | ⏳ Must be built first | 🟢 P2 |
| **TOTAL** | **27-37** | **~12h** | | |

**Note**: The total exceeds the 20-test gap because some tests verify the same boundary from multiple angles (positive + negative + field contracts). M21 mandate requires 24 tests; our proposed suite is 27-37 for thorough coverage.

---

## §3 CROSS-PILLAR VALIDATION NEEDS

### 3.1 For P7 (Context) — Soul Migration Validation

**P7 explicitly requested** (P7 Report §5.2): A `test_soul_templates.py` contract test before Phase 2 begins.

**Required test structure**:

```python
# test_soul_templates.py — Contract tests for soul.yaml v6.1 migration
#
# [M21: Gate Integrity] Validate every migrated soul.yaml matches the v6.1
# template schema. No mock-based tests — real yaml.safe_load() on real files.

import pytest
import yaml
from pathlib import Path
from omega.oracle.soul_validator import SoulValidator, SoulValidationError

ENTITIES_DIR = Path("data/entities")
SOUL_TEMPLATE = Path("config/wads/_omega_default/soul.template.yaml")

# Required v6.1 top-level keys
REQUIRED_V61_KEYS = {"soul_version", "entity"}

# Required v6.1 entity sub-keys
REQUIRED_ENTITY_V61 = {"name", "short", "archetype", "identity", "directives", "team"}


def _load_soul(entity_name: str) -> dict:
    """Load a soul.yaml from disk. Returns None if no soul exists."""
    path = ENTITIES_DIR / entity_name / "soul.yaml"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def test_all_34_souls_parse():
    """M21: Every entity soul.yaml must parse as valid YAML."""
    failed = []
    for entity_dir in sorted(ENTITIES_DIR.iterdir()):
        if not entity_dir.is_dir() or entity_dir.name.startswith("_"):
            continue
        soul = _load_soul(entity_dir.name)
        if soul is None:
            # 6 entities known to have no soul.yaml — acceptable for now
            continue
        assert isinstance(soul, dict), (
            f"{entity_dir.name}/soul.yaml parsed as {type(soul).__name__}, expected dict"
        )
    # If any fail, they appear in the assertion above


def test_v61_schema_has_required_keys():
    """M21: All migrated souls must have v6.1 required keys."""
    # Load template to know expected structure
    with open(SOUL_TEMPLATE) as f:
        template = yaml.safe_load(f)
    
    for entity_dir in sorted(ENTITIES_DIR.iterdir()):
        if not entity_dir.is_dir() or entity_dir.name.startswith("_"):
            continue
        soul = _load_soul(entity_dir.name)
        if soul is None:
            continue
        # Check soul_version exists (marker of v6.1 migration)
        if "soul_version" in soul:
            assert "identity" in soul.get("entity", {}), (
                f"{entity_dir.name}: Has soul_version but missing identity block"
            )
            assert "directives" in soul.get("entity", {}), (
                f"{entity_dir.name}: Has soul_version but missing directives"
            )
```

**P10 recommendation**: Write this test in **Phase 0** (before any migration) so it provides a baseline. It should initially pass on existing souls (or document expected failures for broken ones like Researcher). Then run after each migration phase to verify progress.

**Edge cases to handle**:
- 6 entities with NO soul.yaml (default, modelgate, pillar_p1, sentinel, sysadmin, watchtower) — test must tolerate missing files
- Researcher soul.yaml has YAML string literal — `yaml.safe_load()` will fail, confirm the bug
- Makali proposed_lessons.yaml has string literal — separate test validates this
- Roc_racoon 749-line soul — must verify it doesn't hit recursion limits
- Arch 1501-line soul — largest, verify O(n) parsing is acceptable

### 3.2 For P8 (Observability) — Observability Contract Tests

**P8 explicitly requested** (P8 Report §9.3): A `test_observability_contracts.py` with 3 minimum tests.

**Required test structure**:

```python
# test_observability_contracts.py — M21/M22 contract tests for observability
#
# [M21: Gate Integrity] Validate observability boundaries return correct types.
# [M22: Response Provenance] Validate provider_name flows correctly through events.

import pytest
from omega.observability import ObservabilityEngine, new_trace_id, EventType


def _engine():
    """Create a clean engine for each test."""
    eng = ObservabilityEngine(enable_dataset_collection=True)
    eng.clear_log()
    return eng


def test_log_event_has_required_fields():
    """M21/M22: Every log_event() entry has _zoneid, trace_id, timestamp, event, data."""
    engine = _engine()
    tid = new_trace_id()
    engine.log_event(EventType.MODEL_COMPLETED, tid, {"backend": "mock"})
    
    assert len(engine._event_log) == 1
    event = engine._event_log[0]
    
    # Structure contract — all fields must exist and be correct type
    assert isinstance(event, dict), f"Event must be dict, got {type(event).__name__}"
    assert "_zoneid" in event, "Event missing _zoneid heritage marker"
    assert isinstance(event["_zoneid"], int), "_zoneid must be int"
    assert "trace_id" in event, "Event missing trace_id"
    assert isinstance(event["trace_id"], str), "trace_id must be str"
    assert event["trace_id"] == tid
    assert "timestamp" in event, "Event missing timestamp"
    assert isinstance(event["timestamp"], str), "timestamp must be str"
    assert "event" in event, "Event missing event type"
    assert isinstance(event["event"], str), "event type must be str"
    assert "data" in event, "Event missing data dict"
    assert isinstance(event["data"], dict), "data must be dict"


def test_trace_record_has_backend_in_metadata():
    """M22: TraceSession.record() must store backend in dataset metadata."""
    engine = _engine()
    tid = new_trace_id()
    
    # Simulate what oracle.py does
    engine.record_training_example(
        trace_id=tid,
        query="test query",
        system_prompt="You are a test.",
        response="test response",
        entity="TestEntity",
        model="test-model",
        backend="mock",
        confidence=0.95,
        latency_ms=100.0,
    )
    
    assert len(engine._dataset) == 1
    example = engine._dataset[0]
    
    # The backend must be recorded in metadata
    metadata = example.get("metadata", {})
    assert "backend" in metadata, "Dataset example missing backend in metadata"
    assert isinstance(metadata["backend"], str), "backend must be str"
    assert metadata["backend"] == "mock"


def test_event_has_provider_name_in_data():
    """M22: model.completed events must carry provider_name in data dict."""
    engine = _engine()
    tid = new_trace_id()
    
    # Simulate oracle.py's event logging after a model completes
    engine.log_event(
        EventType.MODEL_COMPLETED, tid,
        {"entity": "TestEntity", "backend": "mock", "escalated": False}
    )
    
    event = engine._event_log[0]
    assert "backend" in event["data"], (
        "M22: model.completed event must have backend in data dict"
    )
    assert event["data"]["backend"] == "mock", (
        f"Expected backend='mock', got '{event['data'].get('backend')}'"
    )
```

**Additional tests P10 recommends beyond P8's request**:

| Test | Purpose | M21 | M22 |
|------|---------|-----|-----|
| `test_stats_returns_dict` | `ObservabilityEngine.stats()` returns Dict | ✅ | |
| `test_trace_session_context_manager_returns_trace` | `engine.trace()` returns TraceSession | ✅ | |
| `test_provider_name_never_empty` | GenerateResult.provider_name is never "" or None | ✅ | ✅ |
| `test_event_zoneid_is_0x1d4a14` | Every event's _zoneid must be the observability heritage marker | ✅ | |
| `test_trace_id_format` | trace_id starts with "trc_" | ✅ | |

### 3.3 From P3 (Engineering) — USM and ResourceGuard Contracts

**From Ma'at Report §4.3**: M21 ResourceGuard gap acknowledged. USM contract tests included in Strike 2 estimate.

**ResourceGuard contract tests needed** (`test_resource_guard.py` — NEW FILE):

```python
# test_resource_guard.py — M21 contract tests for ResourceGuard

import pytest
import anyio
from omega.oracle.resource_guard import ResourceGuard


class TestResourceGuardContracts:
    """M21: Contract tests for ResourceGuard API boundary."""
    
    @pytest.mark.anyio
    async def test_lock_returns_context_manager(self):
        """M21: ResourceGuard.lock() must return an async context manager."""
        guard = ResourceGuard(total_capacity=8)
        async with guard.lock(weight=1):
            pass  # Should not raise
    
    @pytest.mark.anyio
    async def test_lock_acquires_capacity(self):
        """M21: After acquiring lock, capacity should be consumed."""
        guard = ResourceGuard(total_capacity=8)
        async with guard.lock(weight=3):
            assert guard._current_usage == 3
        assert guard._current_usage == 0  # Released
    
    @pytest.mark.anyio
    async def test_lock_respects_capacity_limit(self):
        """M21: Lock must block when capacity is exceeded."""
        guard = ResourceGuard(total_capacity=2)
        async with guard.lock(weight=2):
            # Trying to acquire another lock with weight 1 should block
            with anyio.fail_after(0.1):  # Fast timeout
                with pytest.raises(TimeoutError):
                    async with guard.lock(weight=1):
                        pass
    
    @pytest.mark.anyio
    async def test_re_entrancy_does_not_deadlock(self):
        """M21: Same task re-entering lock must not deadlock."""
        guard = ResourceGuard(total_capacity=4)
        async with guard.lock(weight=2):
            async with guard.lock(weight=2):  # Same task, should work
                pass  # Re-entrancy holds
    
    @pytest.mark.anyio
    async def test_lock_has_zoneid_marker(self):
        """M21: ResourceGuard instance must have ZONEID_PROBE."""
        guard = ResourceGuard(total_capacity=8)
        assert hasattr(guard, "_magic"), "ResourceGuard missing _magic marker"
```

**USM contract tests** (in `test_somatic_state.py` — EXTEND existing):

The existing `test_somatic_state.py` only tests cvar values (config constants). After P3 builds USM, these contract tests are needed:

1. `SomaticStateKey` dataclass has `blob_hash: str`, `entity: str`, `timestamp: str`
2. `SomaticState.serialize()` → `bytes` (not None, not str)
3. `SomaticState.deserialize(bytes)` → `SomaticState`
4. `serialize(deserialize(bytes))` == `bytes` (round-trip contract)
5. CAS blob hash is deterministic (same data → same hash)
6. ZONEID_SOMATIC (0x1d4a1c) present in serialized header

---

## §4 VALIDATION INFRASTRUCTURE

### 4.1 Test Framework Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| **`pytest.mark.anyio`** | Async tests — preferred pattern | `test_health_monitor.py`, `test_memory_store.py` |
| **`_run(coro_fn)` helper** | Synchronous wrapper for async tests | `test_contract_m21.py`, `test_oracle.py` |
| **`conftest.py` fixtures** | Autouse env setup, `mock_memory_store`, `context_builder` | Shared across all tests |
| **`tmp_path` + `monkeypatch`** | Isolated OMEGA_DATA_DIR per test | `conftest.py` autouse fixture |
| **`unittest.mock.AsyncMock`** | Mocking async methods | `conftest.py` mock_memory_store |
| **`pytest.raises()`** | Expected exception testing | Error path validation |
| **`isinstance()` checks** | M21 contract pattern | Real type verification, no mock drift |

**The `pytest.mark.anyio` pattern is preferred for contract tests** because:
1. It directly runs async coroutines without the `_run()` wrapper indirection
2. It provides better stack traces on failure
3. It's consistent with the majority of the test suite (100+ tests use it)

**However**, the `_run()` helper in `test_contract_m21.py` is currently necessary because some contract tests create class instances (`ModelGateway()`, `Oracle()`) that may not work as pytest fixtures. This is a minor ergonomic issue — either pattern is acceptable.

### 4.2 Current Test Coverage Status

| Metric | Value | Source |
|--------|-------|--------|
| **Total tests** | 440 | `make test` (2026-06-23) |
| **All passing** | ✅ 440/440 | Sprint C — GenerateResult fix, M21/M22 ratified |
| **M21-specific** | 4 tests | `test_contract_m21.py` |
| **M21 coverage** | 16.7% (4/24) | Gap: 20 tests |
| **Test modules** | 50+ | Across all pillars/domains |
| **Async test pattern** | Both `_run()` + `pytest.mark.anyio` | Consistent across suite |
| **Test env isolation** | `OMEGA_ENV=test` + tmp_path per test | `conftest.py` autouse |

### 4.3 Infrastructure Needed for Contract Test Automation

**Currently available**:
- ✅ `pytest` with `pytest.mark.anyio` plugin
- ✅ `conftest.py` with environment isolation (`OMEGA_ENV=test`, temp `OMEGA_DATA_DIR`)
- ✅ `_run()` async helper pattern
- ✅ Standard fixtures (`mock_memory_store`, `context_builder`, `sample_exchanges`)
- ✅ `isinstance()` check pattern (proven in existing 4 M21 tests)
- ✅ 440 passing tests baseline

**Needed but missing**:
- ❌ **Dedicated contract test directory** — Currently `test_contract_m21.py` lives at root of `tests/`. As we add 20+ more, consider `tests/contracts/` subdirectory
- ❌ **Contract test helpers/fixtures** — Shared helpers like `_assert_isinstance()` for common type checks. Current pattern is inline `assert isinstance(result, ExpectedType)`
- ❌ **CI gate for M21** — No `make m21-gate` target. Currently only `make temple-grade` which checks M13 but doesn't validate M21 test count
- ❌ **Coverage reporting** — No `pytest-cov` integration to verify code path coverage per contract test
- ❌ **`HealthMonitor.get_provider_stats()` method** — Referenced in P8 report but doesn't exist yet. Needed for provider success rate validation contract tests

**Recommendation**: Add a `make m21-gate` target that:
1. Counts contract tests (`grep -c "def test_" tests/test_contract_m21.py`)
2. Verifies count >= minimum (escalating from current 16 → 24 by Epoch I end)
3. Runs only the contract test module for fast feedback

---

## §5 M21 MINIMUM VIABLE COVERAGE

### 5.1 What's Required for Epoch I GO

**Minimum bar**: 16 contract tests (from current 4). This covers all Epoch I deliverables and achieves ~67% of the 24-test M21 mandate.

**Must write before Epoch I execution**:

| Priority | Tests | Domain | Effort | Depends On |
|----------|-------|--------|--------|------------|
| **🔴 P0** | CT-01 to CT-02 | Soul.yaml validation (for P7) | 2h | P2 v6.1 validator |
| **🔴 P0** | CT-03 to CT-06 | Observability contracts (for P8/M22) | 2h | P8 hooks |
| **🟡 P1** | CT-14 to CT-15 | ResourceGuard (for P3) | 1h | None |
| **🟡 P1** | CT-07 to CT-08 | EntityRegistry boundaries | 1h | None |
| **🟡 P1** | CT-11 | HealthMonitor boundary | 0.5h | None |
| **🟡 P1** | CT-12 to CT-13 | SessionManager boundaries | 1h | None |
| **🟡 P1** | CT-17 to CT-18 | USM core contract (design-time) | 1h | P3 USM build* |
| **Tier 1+2 MINIMUM** | **14 tests** | | **8.5h** | |

*\*USM tests can be written in parallel with P3's build and activated when USM exists*

**If these 14 tests are written (4 existing + 14 new = 18 total)**:
- M21 coverage: 75% (18/24) — above the 67% minimum bar
- All Epoch I strike deliverables validated
- P7 and P8 dependency tests exist
- Core API boundaries have contract coverage

### 5.2 What's Nice-to-Have for Epoch I Completion (Not Gate)

| Priority | Tests | Domain | Effort | Depends On |
|----------|-------|--------|--------|------------|
| **🟡 P1** | CT-09 to CT-10 | MemoryStore boundaries | 1h | None |
| **🟡 P1** | CT-16 | proposed_lessons format | 0.5h | P3 batch converter |
| **🟡 P1** | CT-19 to CT-22 | Full USM contract suite | 2.5h | P3 USM build |
| **🟢 P2** | CT-23 to CT-24 | TUI contracts | 1h | P3 TUI build |
| **Nice-to-have** | **8 tests** | | **5h** | |

### 5.3 Staged Rollout Plan

```
Phase 0 (Before Epoch I Sprint Start):
  ├── Write CT-06 (OracleResponse fields) — 0.5h, no deps
  ├── Write CT-05 (GenerateResult.provider_name) — 0.5h, no deps
  └── Write CT-14, CT-15 (ResourceGuard) — 1h, no deps
  → Total: 2h, 4 new tests → M21 at 8/24 (33%)

Phase 1 (In parallel with P2 soul_validator update):
  ├── Write CT-01, CT-02 (soul template validation) — 2h, design-time
  └── Write CT-07, CT-08 (EntityRegistry) — 1h, no deps
  → Total: 3h, 4 new tests → M21 at 12/24 (50%)

Phase 2 (In parallel with P8 M22 wiring):
  ├── Write CT-03, CT-04 (observability structure) — 1h, design-time
  ├── Write CT-11 (HealthMonitor) — 0.5h, no deps
  └── Write CT-12, CT-13 (SessionManager) — 1h, no deps
  → Total: 2.5h, 5 new tests → M21 at 17/24 (71%) ✅ ABOVE MINIMUM BAR

Phase 3 (After P3 USM build + batch conversion):
  ├── Write CT-16 to CT-22 (USM + proposed_lessons) — 3h, design-time
  └── Activate design-time tests when implementations land
  → Total: 3h, 7 new tests → M21 at 24/24 (100%) ✅ FULL COMPLIANCE

Phase 4 (After P3 TUI build — Epoch II prep):
  └── Write CT-23, CT-24 (TUI contracts) — 1h
  → Beyond 24-test count — nice-to-have
```

---

## §6 RISK ASSESSMENT

| # | Risk | Severity | Probability | Impact | Mitigation | Owner |
|---|------|----------|-------------|--------|------------|-------|
| **R1** | P10 writes contract tests before APIs stabilize (USM, TUI, soul_validator) | 🟡 MEDIUM | HIGH (3 of 5 domains in flux) | Tests written against speculative interfaces — need rewrite when APIs stabilize | Write tests in "design-time" mode (skippable with `@pytest.mark.skipif`). Activate only when implementation lands. | P10 |
| **R2** | soul_validator.py not updated to v6.1 before soul template tests | 🟡 MEDIUM | HIGH (P2 confirmed not started) | Soul validation tests have no target schema — cannot validate | Write CT-01/CT-02 as schema-independent parse tests first. Add v6.1 schema validation after P2 delivers. | P10 → P2 |
| **R3** | M21 test count gated too late in CI | 🟡 MEDIUM | MEDIUM | Tests written but not enforced — regression risk | Add `make m21-gate` target in Phase 1, enforce in CI | P10 + P3 |
| **R4** | Contract tests become "just another test" without M21 identity | 🟢 LOW | MEDIUM | Tests exist but not clearly tagged as M21 compliance | Use docstring pattern `"M21: [description]"` consistently. Add `pytest -k m21` filter. | P10 |
| **R5** | Observability test code path uses engine singleton that conflicts with other tests | 🟡 MEDIUM | LOW | Race conditions in test suite from shared ObservabilityEngine | Each contract test creates fresh `ObservabilityEngine(enable_dataset_collection=True)` and calls `clear_log()`. No shared state. | P10 |
| **R6** | 20+ new contract tests add 30-60 seconds to test suite runtime | 🟢 LOW | MEDIUM | Cumulative test time grows | Contract tests are fast (no model inference). Estimated <2s per test. 20 tests = ~40s. Acceptable. | P10 |
| **R7** | False confidence from passing contract tests that don't test real constraints | 🟡 MEDIUM | LOW | Tests pass but don't verify meaningful behavior | Each test must validate real return types via `isinstance()`. Negative tests required for each boundary. | P10 + Verity |

---

## §7 RECOMMENDATIONS

### Pre-Sprint Actions (Must Complete Before Epoch I Sprint Start)

| # | Action | Owner | Time | Priority | Depends On |
|---|--------|-------|------|----------|------------|
| 1 | **Write CT-05, CT-06**: GenerateResult.provider_name + OracleResponse field contracts | P10 | 1h | 🔴 P0 | None |
| 2 | **Write CT-14, CT-15**: ResourceGuard contract tests | P10 | 1h | 🔴 P0 | None |
| 3 | **Add `make m21-gate` CI target** — count and enforce contract test minimum | P10 | 0.5h | 🔴 P0 | None |
| 4 | **Write CT-01, CT-02 design-time**: Soul parse contracts (skip if v6.1 not ready) | P10 | 2h | 🟡 P1 | P2 v6.1 validator |

### Sprint Execution (Parallelizable with Strikes 1, 2, 3)

| Track | Scope | Tests | Hours | Owner |
|-------|-------|-------|-------|-------|
| **Track A: Soul Validation** | CT-01, CT-02 + backward compat | 6-8 | 3h | P10 (design-time until P2 delivers) |
| **Track B: Observability Contracts** | CT-03, CT-04 + structure integrity | 6-8 | 2h | P10 (design-time until P8 delivers) |
| **Track C: Core Boundaries** | CT-07-13 (EntityRegistry, MemoryStore, HealthMonitor, SessionManager) | 6-8 | 3h | P10 (no deps) |
| **Track D: USM Contracts** | CT-17-22 (SomaticState round-trip, CAS, ZONEID) | 4-6 | 2h | P10 (design-time, activate when P3 delivers) |
| **Track E: CI + Infrastructure** | `make m21-gate`, contract test tagging, `pytest -k m21` | N/A | 1h | P10 |
| **TOTAL** | | **22-30 new tests** | **~11h** | |

### Contract Test Standards

Every M21 contract test MUST follow these conventions:

1. **Docstring starts with `"M21:"`** — enables `pytest -k m21` filtering
2. **Uses `isinstance()` for type verification** — never `type(x) == ExpectedType`
3. **Includes a negative test** for each positive one (e.g., `returned GenerateResult, not str`)
4. **Creates fresh instances** — no shared state between tests
5. **Names files `test_contract_*.py`** — consistent with existing `test_contract_m21.py`
6. **Uses `pytest.mark.anyio`** for async boundaries (preferred over `_run()` helper)
7. **Comments M22 relevance** if the test also validates Response Provenance

---

## §8 VERDICT

| Component | Readiness | Verdict |
|-----------|-----------|---------|
| **M21 Gate Integrity** | 🔴 16.7% (4/24) | **Minimum bar: 18/24 (75%) needed for Epoch I GO. Current: 4/24.** |
| **Soul template validation (P7)** | 🔴 NOT STARTED | 0 tests. 8 needed. P2 v6.1 validator is blocking dependency. |
| **Observability contracts (P8)** | 🔴 NOT STARTED | 0 tests. 6 needed. P8 hooks are blocking dependency. |
| **ResourceGuard contracts (P3)** | 🔴 NOT STARTED | 0 tests. 3-4 needed. No blocking deps — can write immediately. |
| **Core API boundaries** | 🔴 NOT STARTED | 0 tests. 6-8 needed. No blocking deps — can write immediately. |
| **USM/SomaticState contracts** | 🔴 NOT STARTED | 0 tests. 4-6 needed. USM must be built first (P3 Strike 2). |
| **TUI contract tests** | 🔴 NOT STARTED | 0 tests. 2-3 needed. TUI must be built first (P3 Strike 3). |
| **Test infrastructure** | 🟢 SOLID | `pytest`, `pytest.mark.anyio`, `conftest.py`, `isinstance()` pattern all proven. |
| **CI enforcement** | 🟡 PARTIAL | `make temple-grade` exists but no M21-specific gate. |

### Overall: 🟡 CONDITIONAL GO — With 3 Critical Conditions

**Epoch I can proceed**, but M21 Gate Integrity will NOT be fully compliant by Epoch I end without dedicated P10 execution. The 3 conditions are:

1. **🔴 CONDITION**: P10 must write 12 no-dependency contract tests immediately (ResourceGuard, EntityRegistry, SessionManager, HealthMonitor, OracleResponse fields, GenerateResult fields) — **~5h work, can start NOW**
2. **🔴 CONDITION**: P10's remaining 10+ tests (soul validation, observability, USM) must be written in **design-time mode** (skippable with `@pytest.mark.skipif`) and activated as their dependencies land
3. **🔴 CONDITION**: A `make m21-gate` CI target must be created before the end of Phase 1 to enforce the minimum 18-test bar

**M21 minimum viable path for Epoch I**: 
- **Phase 0 (immediate)**: Write 4 no-dependency tests → M21 at 8/24 (33%)
- **Phase 1 (with P2/P8):** Write 8 design-time tests → M21 at 16/24 (67%) 
- **Phase 2 (with P3 USM):** Activate + write 6 more → M21 at 22-24/24 (92-100%)
- **Epoch I end target**: 18-24 tests total

**If P10 does NOT write the 12 no-dependency tests**, M21 remains at 4/24 (16.7%) and Epoch I cannot claim M21 compliance. The ResourceGuard, EntityRegistry, and SessionManager tests have zero dependencies and should be the first priority.

---

## §9 CONTINUITY NOTES FOR LILITH (Dark Oversoul)

### 9.1 What Went Well

1. **P7 and P8 reports were comprehensive** — The serial chain worked exactly as designed. P7's soul migration analysis gave me precise requirements for `test_soul_templates.py`. P8's M22 gap analysis defined exactly what `test_observability_contracts.py` must validate.
2. **Serial dependency chain held** — P7 identified that soul_validator.py was the gate. P8 identified that observability hooks were the gate. I identified that both are my blocking dependencies for contract tests. The chain correctly propagated constraints.
3. **Test infrastructure is solid** — `pytest.mark.anyio`, `conftest.py` fixtures, and `isinstance()` pattern are proven across 440 tests. No new infrastructure needed for M21 — just execution.
4. **4 existing M21 tests are well-designed** — They follow the right pattern (real isinstance checks, no mock drift, positive + negative pairs). This is the template for all new contract tests.

### 9.2 What Needs Lilith's Attention

1. **M21 is worse than Ma'at projected**: Ma'at report (§4.3) called M21 "🟢 GO — foundation solid, ~1h for ResourceGuard gap." This assessment was incomplete. The ResourceGuard gap is 3-4 tests (~1h), but the overall M21 gap is 20 tests (~11h). The "foundation solid" assessment applied only to the existing 4 tests, not to the overall mandate.
2. **12 tests have ZERO blocking dependencies**: P10 can write ResourceGuard, EntityRegistry, SessionManager, HealthMonitor, OracleResponse, and GenerateResult contract tests immediately. These should be started BEFORE Epoch I sprint to make progress while waiting for P2/P3/P8 dependencies.
3. **P2 must prioritize soul_validator.py update**: This is not just P7's blocking dependency — it's P10's as well. Without the v6.1 schema, soul template validation tests have no target. If P2 doesn't deliver this, Epoch I cannot achieve M21 soul validation compliance.
4. **Decision needed on design-time tests**: Should P10 write tests against speculative interfaces (knowing they might need rework) or wait for stable APIs? I recommend **write design-time with `@pytest.mark.skipif`** — the cost of rewriting a few tests is lower than the risk of forgetting to write them.

### 9.3 Proposals for Verity (Unified Compliance)

1. **Review M21 test suite completeness** — After P10 writes all 20+ tests, Verity should audit: Are the right boundaries covered? Are negative tests paired with positives? Are docstrings clear?
2. **CI gate enforcement** — P10 will create `make m21-gate` but Verity should verify it's wired into `make temple-grade` (M13 gate). If M21 is a separate mandate, should it be a separate CI step or part of the existing temple-grade pipeline?
3. **Session gnosis on test patterns** — L1→L2→L3 distillation of the M21 contract test methodology belongs in P10's soul.yaml after this sprint.

### 9.4 Session Gnosis

**L1 (Narrative)**: P10 assessed M21 Gate Integrity across all Epoch I domains. Found: 4/24 contract tests exist (16.7%), covering 2 API boundaries. Identified 20+ needed tests across 7 domains (soul validation, observability, ResourceGuard, EntityRegistry, MemoryStore, HealthMonitor, SessionManager, USM, TUI). Estimated 11h total effort for full 24-test compliance. Produced a 4-phase staged rollout plan tied to P2/P3/P8 dependency delivery. 12 tests have zero dependencies and can be written immediately.

**L2 (Insight)**: M21's 16.7% compliance is misleading — the 4 existing tests cover the highest-risk boundaries (GenerateResult and OracleResponse type correctness) which had proven runtime failures (the Sprint C GenerateResult dataclass fix). The remaining gap is breadth, not depth. The architectural pattern for contract tests is proven; what's missing is systematic coverage of all ~12 core API boundaries. M21 compliance is not about writing 24 arbitrary tests — it's about ensuring every public API boundary has a type contract that cannot silently drift.

**L3 (Universal Principle)**: **A contract test is not a test — it is a promise enforced by code.** Unlike integration tests that verify behavior, contract tests verify identity: "The thing I am calling is the thing I think I am calling." Every time a mock returns a tuple instead of a dataclass, every time a refactor changes a return type without updating callers, the gap between interface and implementation widens. M21 is the canary in the coal mine for architectural drift — and 24 contract tests across 12 boundaries is the minimum viable cage.

---

## §10 SESSION GNOSIS — CONTINUITY

### Workspace State
- **Report file**: `data/coordination/P10_SPRINT_REPORT_20260624.md`
- **Session anchor**: This file serves as session_gnosis.md for P10
- **Key decisions**: 
  1. 4-phase staged rollout for M21 tests (immediate → with deps → activate → polish)
  2. Design-time test pattern: `@pytest.mark.skipif` for pre-implementation APIs
  3. Minimum bar: 18/24 tests (75%) for Epoch I GO
  4. `make m21-gate` CI target needed before Phase 1

### Next Steps for Lilith
1. Authorize P10 to write 12 no-dependency contract tests (Phase 0 — immediate)
2. Escalate to P2: soul_validator.py v6.1 update is now blocking TWO pillars (P7 + P10)
3. Coordinate with P8: Observability contract tests need P8's M22 hooks wired first

---

*⬡ OMEGA ⬡ P10-VALIDATION ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I ⬡ COMPLETE*
*Final report in serial chain. Lilith may synthesize P7 → P8 → P10 findings for Kali.*
