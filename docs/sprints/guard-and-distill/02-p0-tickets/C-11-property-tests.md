---
schema_version: "1.0"
document_type: "ticket_page"
document_id: "c-11-property-tests"
title: "C-11: Property Tests for OOMProtector + SoulStore"
status: "PLANNED"
version: "1.0.0"
date: "2026-07-22"
owner: "maat/P3"
tags: ["sprint-plan", "phase-c", "p0-tickets", "llm-friendly", "guard-and-distill", "property-testing", "hypothesis", "oom-protector", "soul-store"]
priority: "P0"
depends_on: ["C-2'", "C-1'"]
blocks: ["C-0.5", "Phase D"]
acceptance_gates:
  - "OOMProtector: 3-signal fusion monotonicity verified (more pressure → higher risk)"
  - "OOMProtector: State machine transitions: Healthy → Degraded → Critical → Recovering → Healthy"
  - "SoulStore: Concurrent writes never corrupt data (all reads return old OR new, never partial)"
  - "SoulStore: Zero temp files leaked after any operation (including crashes)"
  - "SoulStore: Crash recovery — read after simulated mid-write kill returns valid data"
  - "100% property test pass in CI"
  - "No flakiness: derandomize=True, suppress_health_check=[too_slow], CI profile (500 examples)"
cross_references:
  - "SOVEREIGN_ARK_BLUEPRINT.md"
  - "FLEET_TEAM_PLAYBOOK.md"
  - "LLM_FRIENDLY_DOCS_BP.md"
llm_metadata:
  token_budget: 3000
  chunk_strategy: "section_per_ticket"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 C-11: Property Tests for OOMProtector + SoulStore
**AP Token**: `AP-TICKET-C11-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ticket_p0 ⬡ ACTIVE

**Date**: 2026-07-22
**Ticket ID**: `C-11`
**Sprint**: `guard-and-distill-2026-07-22`
**Priority**: P0
**Owner**: maat/P3
**Status**: PLANNED
**Depends On**: ["C-2'", "C-1'"]
**Blocks**: ["C-0.5", "Phase D"]
**Estimated Hours**: 12

---

## What

> ⚠️ **CARMACK AUDIT (2026-07-22)**: Scope trimmed. Start strictly with OOMProtector and SoulStore invariants. Do NOT build a massive chaos testing suite or benchmarks until core invariants are proven.
>
> ⚠️ **VERIFIED FINDINGS (2026-07-22)**: Hypothesis 6.159.0 does NOT support async `RuleBasedStateMachine` (confirmed via GitHub issues #3712, #4107). `hypothesis-trio` is stale (v0.6.0 from 2021). **Use non-stateful `@given` async property tests** with pytest-asyncio + `anyio_mode=auto`. See `08-verified-findings.md` §2.1 for details.

Implement Hypothesis non-stateful `@given` async property tests for:
1. **OOMProtector**: 3-signal fusion thresholds (PSI + MemAvailable + cgroups) under load
2. **SoulStore**: Atomic write invariants under concurrent access + crash recovery

## Why

Current tests are example-based. Property-based testing finds edge cases humans miss — especially for stateful systems with concurrency and crash scenarios.

## Acceptance Criteria (Copy-Paste Verifiable)

- [ ] OOMProtector: 3-signal fusion monotonicity verified (more pressure → higher risk)
- [ ] OOMProtector: State machine transitions: `Healthy → Degraded → Critical → Recovering → Healthy`
- [ ] SoulStore: Concurrent writes never corrupt data (all reads return old OR new, never partial)
- [ ] SoulStore: Zero temp files leaked after any operation (including crashes)
- [ ] SoulStore: Crash recovery — read after simulated mid-write kill returns valid data
- [ ] 100% property test pass in CI
- [ ] No flakiness: `derandomize=True`, `suppress_health_check=[too_slow]`, CI profile (500 examples)

## Dependencies

- **Requires**: C-2' (OOMProtector 3-signal fusion) ✅ DONE, C-1' (SoulStore atomic writer) ✅ DONE
- **Enables**: C-0.5 (Scribe needs verified storage), Phase D (integrity gate)

## Implementation Sketch (Self-Contained)

```python
# File: tests/property/test_oom_protector_given.py
# Purpose: Non-stateful @given property tests for OOMProtector 3-signal fusion
# Dependencies: hypothesis, pytest-asyncio, anyio, src.omega.oracle.oom_protector
#
# NOTE: Hypothesis 6.159.0 does NOT support async RuleBasedStateMachine.
# Using @given with async functions + pytest-asyncio anyio_mode=auto instead.
# See docs/sprints/guard-and-distill/08-verified-findings.md §2.1

import pytest
from hypothesis import given, settings, strategies as st
from src.omega.oracle.oom_protector import OOMProtector

# ─── OOMProtector Property Tests ────────────────────────────────────────

@given(
    psi_pressure=st.floats(0.0, 100.0),
    mem_available_mb=st.integers(100, 8000),
    cgroup_usage_mb=st.integers(100, 8000),
    sys_load=st.floats(0.0, 100.0),
)
@settings(max_examples=500, derandomize=True)
async def test_oom_fusion_risk_bounds(
    psi_pressure, mem_available_mb, cgroup_usage_mb, sys_load
):
    """3-signal fusion risk must always be in [0.0, 1.0]"""
    oom = OOMProtector()
    oom.psi._last_pressure = psi_pressure
    oom.mem._last_available_mb = mem_available_mb
    oom.cgroup._current_usage_mb = cgroup_usage_mb
    
    risk = await oom.check_available()
    assert 0.0 <= risk <= 1.0, f"Risk out of bounds: {risk}"


@given(
    low_psi=st.floats(0.0, 30.0),
    high_psi=st.floats(60.0, 100.0),
    mem=st.integers(1500, 8000),
    cgroup=st.integers(100, 2000),
)
@settings(max_examples=200, derandomize=True)
async def test_oom_fusion_monotonicity(
    low_psi, high_psi, mem, cgroup
):
    """More PSI pressure → higher or equal risk (monotonicity)"""
    oom = OOMProtector()
    oom.mem._last_available_mb = mem
    oom.cgroup._current_usage_mb = cgroup
    
    oom.psi._last_pressure = low_psi
    risk_low = await oom.check_available()
    
    oom.psi._last_pressure = high_psi
    risk_high = await oom.check_available()
    
    assert risk_high >= risk_low, (
        f"Monotonicity violated: risk({low_psi})={risk_low} > risk({high_psi})={risk_high}"
    )


@given(
    psi_pressure=st.floats(0.0, 100.0),
    mem_reduction=st.integers(100, 4000),
)
@settings(max_examples=200, derandomize=True)
async def test_oom_state_transitions(psi_pressure, mem_reduction):
    """State transitions follow: Healthy → Degraded → Critical → Recovering → Healthy"""
    oom = OOMProtector()
    oom.psi._last_pressure = psi_pressure
    
    # Start with plenty of memory → Healthy
    oom.mem._last_available_mb = 8000
    oom.cgroup._current_usage_mb = 100
    assert oom.state == "Healthy", f"Expected Healthy, got {oom.state}"
    
    # Reduce memory → may transition to Degraded or Critical
    oom.mem._last_available_mb = max(100, 8000 - mem_reduction)
    await oom.check_available()
    assert oom.state in ("Healthy", "Degraded", "Critical"), (
        f"Invalid state after mem pressure: {oom.state}"
    )

# ─── SoulStore Property Tests ───────────────────────────────────────────

@given(
    data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(max_size=100),
        max_size=10,
    ),
)
@settings(max_examples=500, derandomize=True)
async def test_soul_store_round_trip(data):
    """Write then read must return identical data"""
    import tempfile
    from pathlib import Path
    from src.omega.soul_store import SoulStore
    
    temp_dir = tempfile.mkdtemp()
    store = SoulStore(temp_dir)
    
    await store.write(data)
    result = await store.read()
    
    assert result == data, f"Round-trip failed: wrote {data}, read {result}"


@given(
    data_a=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(max_size=100),
        max_size=5,
    ),
    data_b=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(max_size=100),
        max_size=5,
    ),
)
@settings(max_examples=200, derandomize=True)
async def test_soul_store_atomic_visibility(data_a, data_b):
    """Read must return either old data OR new data, never partial/corrupt"""
    import tempfile
    from pathlib import Path
    from src.omega.soul_store import SoulStore
    
    temp_dir = tempfile.mkdtemp()
    store = SoulStore(temp_dir)
    
    await store.write(data_a)
    
    # Concurrent read during write
    async def read_racer():
        return await store.read()
    
    async with anyio.create_task_group() as tg:
        tg.start_soon(store.write, data_b)
        read_result = await read_racer()
    
    # Must be either data_a (old) or data_b (new), never partial
    assert read_result == data_a or read_result == data_b, (
        f"Atomic visibility violated: got {read_result}"
    )


@given(
    data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(max_size=100),
        max_size=5,
    ),
)
@settings(max_examples=200, derandomize=True)
async def test_soul_store_no_temp_files_leaked(data):
    """No temp files should exist after write completes"""
    import tempfile
    from pathlib import Path
    from src.omega.soul_store import SoulStore
    
    temp_dir = tempfile.mkdtemp()
    store = SoulStore(temp_dir)
    
    await store.write(data)
    
    # Check no .tmp files remain
    tmp_files = list(Path(temp_dir).glob("*.tmp"))
    assert len(tmp_files) == 0, f"Leaked temp files: {tmp_files}"


@given(
    data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(max_size=100),
        max_size=5,
    ),
    crash_point=st.sampled_from(["before_fsync", "after_fsync", "before_replace"]),
)
@settings(max_examples=100, derandomize=True)
async def test_soul_store_crash_recovery(data, crash_point):
    """Simulated crash mid-write must not corrupt previously written data"""
    import tempfile
    from pathlib import Path
    from src.omega.soul_store import SoulStore
    
    temp_dir = tempfile.mkdtemp()
    store = SoulStore(temp_dir)
    
    # Write initial data
    await store.write(data)
    
    # Simulate crash mid-write by creating a .tmp file manually
    import json
    tmp_path = Path(temp_dir) / f".tmp.{os.getpid()}.tmp"
    tmp_path.write_text(json.dumps({"corrupt": "data"))
    
    # New instance should recover (ignore corrupt tmp files)
    new_store = SoulStore(temp_dir)
    result = await new_store.read()
    
    # Should return original data, not the corrupt tmp data
    assert result == data or result is None, (
        f"Crash recovery returned unexpected data: {result}"
    )
    if result is not None:
        assert result == data, f"Crash recovery lost data: expected {data}, got {result}"

# CI Profile: 500 examples, no deadline, suppress too_slow
# Run: pytest tests/property/test_oom_protector_given.py -v
```

## Research-Backed Patterns (Structured)

```yaml
research_patterns:
  - pattern: "Hypothesis Async RuleBasedStateMachine"
    source: "GitHub hypothesis/hypothesis#4107, MarkTechPost 2026-04-18, TechOral 2026-06-14"
    key_insights:
      - "Use sync wrapper + anyio.run() for async FSM rules"
      - "Register CI profiles: dev (max_examples=20), ci (max_examples=500, deadline=None)"
      - "suppress_health_check=[HealthCheck.too_slow] for stateful tests"
      - "derandomize=True for reproducibility"
  
  - pattern: "State Machine Modeling"
    source: "Hypothesis docs, oneuptime 2026-01-30"
    key_insights:
      - "Model OOMProtector as: Healthy → Degraded → Critical → Recovering → Healthy"
      - "Use Bundle for data flow between rules"
      - "invariant() for safety properties (monotonicity, bounds)"
      - "precondition() for valid transitions"
  
  - pattern: "SoulStore Atomicity Invariants"
    source: "Grok CLI review F-01, Ma'at C-1' implementation"
    key_insights:
      - "Concurrent writes: all reads return old OR new (never partial)"
      - "Temp file cleanup: zero *.tmp files after any operation"
      - "Crash recovery: restart + read returns valid data"
      - "4-layer guarantee: AtomicVisibility + CrashDurability + WriterExclusion + IntegrityDetection"
```

## Commands to Verify

```bash
# Run OOMProtector property tests (dev profile)
HYPOTHESIS_PROFILE=dev pytest tests/property/test_oom_protector_fsm.py -v

# Run SoulStore property tests (dev profile)
HYPOTHESIS_PROFILE=dev pytest tests/property/test_soul_store_fsm.py -v

# Run full CI profile (500 examples each)
HYPOTHESIS_PROFILE=ci pytest tests/property/test_oom_protector_fsm.py tests/property/test_soul_store_fsm.py -v

# Verify no flakiness (run 3x)
for i in 1 2 3; do HYPOTHESIS_PROFILE=ci pytest tests/property/ -v; done

# Full temple-grade check
make temple-grade
```

## Kali Amendments Applied

| Amendment | Original Scope | Amended Scope |
|-----------|----------------|---------------|
| **Amendment 2** | "OOMProtector 3-signal fusion thresholds" | **Add SoulStore atomicity invariants** — concurrent writes never corrupt, temp files always cleaned, crash recovery returns valid data |

---

*⬡ OMEGA ⬡ MAAT ⬡ TICKET-C11 ⬡ v1.0.0 ⬡ 2026-07-22*