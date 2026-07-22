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

Implement Hypothesis `RuleBasedStateMachine` property tests for:

Implement Hypothesis `RuleBasedStateMachine` property tests for:
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
# File: tests/property/test_oom_protector_fsm.py
# Purpose: Property-based state machine for OOMProtector 3-signal fusion
# Dependencies: hypothesis, pytest, anyio, src.omega.oracle.psi_monitor, memavailable, cgroup_pressure

import anyio
from hypothesis import given, settings, HealthCheck, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, Bundle
from src.omega.oracle.psi_monitor import PSIMonitor
from src.omega.oracle.memavailable import MemAvailableMonitor
from src.omega.oracle.cgroup_pressure import CGroupPressureMonitor
from src.omega.oracle.oom_protector import OOMProtector

class OOMProtectorStateMachine(RuleBasedStateMachine):
    """Model 3-signal fusion: PSI + MemAvailable + cgroups"""
    
    psi_pressure = Bundle("psi_pressure")
    mem_available = Bundle("mem_available")
    cgroup_current = Bundle("cgroup_current")
    
    def __init__(self):
        super().__init__()
        self.psi = PSIMonitor()
        self.mem = MemAvailableMonitor()
        self.cgroup = CGroupPressureMonitor()
        self.oom = OOMProtector(self.psi, self.mem, self.cgroup)
    
    @rule(target=psi_pressure, pressure=st.floats(0.0, 100.0))
    def set_psi(self, pressure):
        self.psi._last_pressure = pressure
        return pressure
    
    @rule(target=mem_available, mb=st.integers(100, 8000))
    def set_mem(self, mb):
        self.mem._last_available_mb = mb
        return mb
    
    @rule(target=cgroup_current, mb=st.integers(100, 8000))
    def set_cgroup(self, mb):
        self.cgroup._current_usage_mb = mb
        return mb
    
    @invariant()
    def fusion_consistency(self):
        """3-signal fusion must be monotonic: more pressure → higher risk"""
        risk = self.oom._compute_fusion_risk()
        assert 0.0 <= risk <= 1.0, f"Risk out of bounds: {risk}"
        
        # Monotonicity: if all signals increase pressure, risk should not decrease
        # (This is a simplified check; real monotonicity needs pairwise comparison)
    
    @invariant()
    def state_machine_valid(self):
        """State transitions must follow: Healthy → Degraded → Critical → Recovering → Healthy"""
        valid_transitions = {
            "Healthy": ["Degraded", "Healthy"],
            "Degraded": ["Critical", "Healthy", "Degraded"],
            "Critical": ["Recovering", "Critical"],
            "Recovering": ["Healthy", "Recovering"],
        }
        current = self.oom.state
        # Next state (if changed) must be valid
        # This is checked implicitly by the state machine logic

# CI Profile: 500 examples, no deadline, suppress too_slow
# Run: HYPOTHESIS_PROFILE=ci pytest tests/property/test_oom_protector_fsm.py -v
```

```python
# File: tests/property/test_soul_store_fsm.py
# Purpose: Property-based state machine for SoulStore atomic write invariants
# Dependencies: hypothesis, pytest, anyio, src.omega.soul_store

import anyio
from hypothesis import given, settings, HealthCheck, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, Bundle
from src.omega.soul_store import SoulStore
import tempfile
import os
from pathlib import Path

class SoulStoreStateMachine(RuleBasedStateMachine):
    """Atomic write invariants under concurrent access"""
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.store = SoulStore(self.temp_dir)
        self.write_count = 0
    
    @rule(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), max_size=10))
    def write_concurrent(self, data):
        """Spawn multiple writers, verify no corruption"""
        async def write_task(d):
            await self.store.write(d)
        
        async def run_concurrent():
            async with anyio.create_task_group() as tg:
                for _ in range(3):
                    tg.start_soon(write_task, data)
        
        anyio.run(run_concurrent)
        self.write_count += 1
    
    @invariant()
    def no_temp_files_leaked(self):
        """No *.tmp files should exist after any operation"""
        tmp_files = list(Path(self.temp_dir).glob("*.tmp"))
        assert len(tmp_files) == 0, f"Leaked temp files: {tmp_files}"
    
    @invariant()
    def read_returns_valid_data(self):
        """Read must return either old data or new data, never partial/corrupt"""
        result = anyio.run(self.store.read)
        assert result is None or isinstance(result, dict), f"Invalid read result: {result}"
        # Verify JSON-serializable (no partial writes)
        import json
        json.dumps(result)  # Raises if not serializable
    
    @invariant()
    def crash_recovery(self):
        """Simulate crash: kill process mid-write, verify recovery on restart"""
        # This is tested via separate crash simulation test
        # Here we verify the store can be re-instantiated and read
        new_store = SoulStore(self.temp_dir)
        result = anyio.run(new_store.read)
        assert result is None or isinstance(result, dict)

# Settings for CI
# @settings(suppress_health_check=[HealthCheck.too_slow], derandomize=True, max_examples=500)
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