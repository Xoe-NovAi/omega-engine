# Agent & Soul File Hardening — Reference
**AP Token**: AP-AGENT-SOUL-HARDENING-v1.0.0
OMEGA | KALI | opencode | trc_agent_hardening | REFERENCE

**Purpose**: Prescriptive detail for agent & soul file hardening (Soul Health Metrics, Testing Infrastructure, Observability, Automation Pipeline). Extracted from AGENTS.md to reduce per-session token load (M18). Load on demand when hardening agent/soul infrastructure.

**Source**: Originally AGENTS.md section 'Agent & Soul File Hardening (2026-07-25)'. Research: docs/research/R_AGENT_SOUL_FILE_HARDENING_20260725.md

---
Based on comprehensive infrastructure audit and 2026 web research, the following hardening measures are **REQUIRED** for all agents.

### 8. Soul Health Metrics (MANDATORY)

Every entity MUST maintain automated health scoring via `SoulHealthScorer`:

```python
# src/omega/oracle/soul_health.py
class SoulHealthScorer:
    WEIGHTS = {
        "schema_compliance": 0.25,      # Passes soul_validator
        "directive_coverage": 0.20,     # Directives per domain
        "directive_validation": 0.15,   # % with validation rules
        "l3_principle_density": 0.15,   # L3 principles per 1000 tokens
        "distillation_recency": 0.10,   # Days since last distillation
        "edit_stability": 0.10,         # Low edit frequency = stable
        "memory_completeness": 0.05,    # All 3 memory files exist
    }
```

**Metrics to Track (via MetricsDB):**
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `soul_health` | Composite health score | entity_id, health_score, directive_count, directive_compliance, l3_principle_count, l3_adoption_rate, edit_frequency_24h, last_distillation_ts |
| `directive_tracking` | Directive lifecycle | entity_id, directive_id, action (created/validated/violated/archived), validation_result, trace_id |
| `distillation_metrics` | Pipeline observability | entity_id, trace_id, classification (routine/distilled/rejected), novelty_score, quality_score, staging_gate_passed, time_to_approve_hours |

**Automated Collection Points:**
1. `SoulValidator.validate()` → Record schema compliance
2. `SoulHealthScorer.score()` → Compute and store composite health
3. Validation gate → Record directive validation
4. Daily cron → Compute and store `SoulHealthScorer` results

### 9. Testing Infrastructure Hardening (MANDATORY)

**Property-Based Tests (Hypothesis):**
```python
# tests/property/test_soul_evolution.py
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_soul_name_validation(name):
    """Soul name must be non-empty string."""
    
@given(st.lists(st.dictionaries(st.text(), st.text()), min_size=1))
def test_directive_list_structure(directives):
    """Every directive dict must have 'id' and 'rule' keys."""
```

**Contract Tests for Agent Instructions:**
```python
# tests/contract/test_agent_instructions.py
class TestAgentInstructionCompliance:
    @pytest.mark.parametrize("entity_name", ALL_ENTITIES)
    async def test_directive_rule_enforced(self, entity_name):
        """Each directive's 'rule' must be enforceable as a test."""
        soul = load_soul(entity_name)
        for directive in soul.get("directives", []):
            test_fn = compile_rule_to_test(directive["rule"])
            assert test_fn(entity_name), f"Directive {directive['id']} violated"
```

**Chaos Engineering for Soul Persistence:**
```python
# tests/chaos/test_soul_crash_safety.py
class TestSoulCrashSafety:
    @pytest.mark.anyio
    async def test_fsync_failure_crashes_process(self):
        """Per fsyncgate: fsync error must crash, not retry."""
        with patch("os.fsync", side_effect=OSError("disk full")):
            with pytest.raises(SoulStoreWriteError):
                await soul_store.write_atomic(path, content)
    
    @pytest.mark.anyio
    async def test_concurrent_writes_no_corruption(self):
        """100 concurrent writers to same soul file."""
        async with anyio.create_task_group() as tg:
            for i in range(100):
                tg.start_soon(write_soul, f"content_{i}")
        # Verify all writes present, no corruption
```

**Golden File Tests for Schema Migrations:**
```python
# tests/golden/test_soul_schema_migrations.py
def test_v60_to_v61_migration():
    """v6.0 soul with soul_axioms → v6.1 with memory/approved_lessons.yaml"""
    v60_soul = load_golden("v60_soul.yaml")
    migrated = migrate_soul(v60_soul)
    assert "soul_axioms" not in migrated["entity"]
    assert "memory/approved_lessons.yaml" exists
```

### 10. Observability & Dashboards (MANDATORY)

**Real-Time Soul Health Dashboard (Grafana JSON):**
```python
# src/omega/observability/soul_dashboard.py
class SoulHealthDashboard:
    async def get_fleet_health(self) -> FleetHealthReport:
        return {
            "entities": await self.get_all_entity_health(),
            "fleet_score": mean(e.health_score for e in entities),
            "directive_compliance": mean(e.directive_compliance for e in entities),
            "l3_adoption_rate": mean(e.l3_adoption_rate for e in entities),
            "stale_souls": [e for e in entities if e.days_since_distillation > 30],
        }
```

**Soul Drift Detection (Daily Cron):**
```python
# src/omega/oracle/soul_drift_detector.py
class SoulDriftDetector:
    def detect_drift(self, entity_name: str) -> DriftReport:
        soul = load_soul(entity_name)
        approved = load_approved_lessons(entity_name)
        directives = soul.get("directives", [])
        
        drift = []
        # Check: every L3 principle in approved has corresponding directive
        for lesson in approved.get("approved", []):
            if lesson.level == "L3":
                if not any(d["id"] in lesson.content for d in directives):
                    drift.append(f"L3 principle {lesson.id} lacks directive anchor")
        
        # Check: directive validation rules still pass
        for directive in directives:
            if "validation" in directive:
                if not eval_validation(directive["validation"]):
                    drift.append(f"Directive {directive['id']} validation failing")
        
        return DriftReport(entity=entity_name, drift_items=drift)
```

**HMC Hub Integration:**
- Fleet health alerts posted to HMC Hub Discussion Thread
- Stale soul warnings → @maat for remediation
- Drift detection results → @verity for compliance review

### 11. Automation Pipeline (MANDATORY)

**CI Gates (add to .github/workflows/ci.yml):**
```yaml
- name: Soul Health Gate
  run: |
    python -m src.omega.oracle.soul_health --fleet-threshold 70
    # Fails if fleet_score < 70

- name: Directive Compliance Gate
  run: |
    python -m src.omega.oracle.directive_compliance --threshold 0.8
    # Fails if any entity directive_compliance < 80%

- name: Schema Migration Check
  run: |
    python -m src.omega.oracle.soul_migrator --check-only
    # Fails if any v6.0 fields detected
```

**Automated Tooling:**
1. `soul_migrator.py` — v6.0→v6.1 automated migration
2. `directive_compiler.py` — Natural language rule → executable test
3. `soul_health_scorer.py` — Daily fleet health computation
4. `staging_gate_reminder.py` — Notifies when proposed_lessons pending > 7 days

---
