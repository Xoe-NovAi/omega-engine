# 🔱 Agent & Soul File Hardening Report
**AP Token**: `AP-AGENT-SOUL-HARDENING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_agent_soul_hardening ⬡ RESEARCH

**Date**: 2026-07-25
**Purpose**: Comprehensive analysis of current agent/soul file infrastructure with web-researched best practices and hardening recommendations.

---

## 📋 Executive Summary

This report analyzes the Omega Engine's agent and soul file infrastructure against 2026 industry best practices for AI agent configuration, state management, and observability. The current implementation demonstrates strong architectural foundations (atomic writes, append-only audit trails, schema validation) but has gaps in metrics collection, automated testing, and cross-agent observability.

**Key Finding**: The infrastructure is **production-ready for core operations** but requires hardening in three areas:
1. **Metrics Infrastructure** — No automated soul health scoring, directive compliance tracking, or L3 principle adoption rates
2. **Testing Coverage** — Missing contract tests for soul evolution, agent instruction compliance, and cross-agent coordination
3. **Observability** — No real-time dashboards for soul drift, directive entropy, or agent performance

---

## 🏗️ Current Implementation Analysis

### 1. Soul File Architecture (v6.1 Lean Schema)

**Files Reviewed**:
- `data/entities/roc_racoon/soul.yaml` — **Gold Standard** (361 lines, full v6.1 compliance)
- `data/entities/iris/soul.yaml` — Complete v6.1 with directives, team, identity
- `data/entities/cli_cline/soul.yaml` — v6.2 with L3 principles and evolution tracking
- `data/entities/maat/soul.yaml` — **Minimal** (26 lines, missing identity/directives/team)
- `data/entities/lilith/soul.yaml` — **Minimal** (18 lines, missing identity/directives/team)

**Schema Compliance** (from `soul_validator.py`):
| Requirement | Status | Notes |
|-------------|--------|-------|
| `entity.name` | ✅ Required | All entities have |
| `entity.short` (2-6 chars) | ✅ Required | v6.1+ only |
| `entity.soul_version` | ✅ "6.1" | Legacy souls get warning |
| `identity` block | ⚠️ Recommended | Missing in maat, lilith |
| `directives` list | ⚠️ Recommended | Missing in maat, lilith |
| `team` block | ⚠️ Recommended | Missing in maat, lilith |
| `memory/` directory | ⚠️ Warning only | Not enforced |

**Forbidden Fields (v6.0 → v6.1 migration)**:
- `soul_axioms` — Must be in `memory/approved_lessons.yaml`
- `wisdom_text` — Must be in `memory/sessions.yaml`
- `trajectory` — Must be in `memory/proposed_lessons.yaml`

### 2. Soul Edit History (Immutable Audit Trail)

**Implementation**: `src/omega/oracle/soul_edit_history.py`
- **Append-only YAML-based append-only log per entity
- Atomic writes via tmp+rename pattern
- Filtering by source, timestamp, limit
- Concurrent append protection via anyio.Lock

**Test Coverage**: `tests/test_soul_edit_history.py` (352 lines, 18 tests)
- ✅ Contract tests for dataclass types
- ✅ Immutability verification
- ✅ Filtering (source, timestamp, limit)
- ✅ Corrupt file handling
- ✅ Concurrent appends (3 workers × 5 entries)

**Metrics Gap**: No automated collection of:
- Edit frequency per entity
- Source distribution (soul_distiller vs manual vs background_researcher)
- Directive-to-lesson conversion rates
- L3 principle promotion latency

### 3. Soul Distillation Pipeline (L1→L2→L3)

**Implementation**: `src/omega/oracle/soul_distiller.py` (689 lines)
- **5-Stage Pipeline**: Classify → Extract → Distill → Score → Store
- **Conservative Classifier**: EloPhanto-inspired (min 8 events, 0.3 novelty threshold)
- **5-Factor Quality Scorer**: Relevance(30%) + Novelty(25%) + Actionability(20%) + Completeness(15%) + Accuracy(10%)
- **Staging Gate**: Writes to `proposed_lessons.yaml` (NOT soul.yaml) — human approval required

**Test Coverage**: `tests/test_contract_soul_distiller.py` (218 lines, 6 tests)
- ✅ Contract: writes to proposed_lessons.yaml, NOT soul.yaml
- ✅ Creates proposed_lessons if missing
- ✅ Default section is "proposals" (not "embodied_experiences")
- ✅ soul.yaml remains valid YAML after multiple distillations
- ✅ proposed_lessons.yaml is valid YAML

**Metrics Gap**: No tracking of:
- Classification routine vs non-routine rates
- Quality score distributions
- Staging gate pass/fail rates
- Time from session → approved lesson

### 4. Soul Validator (R-10 Schema Enforcement)

**Implementation**: `src/omega/oracle/soul_validator.py` (217 lines)
- Validates v6.1 lean schema
- Forbidden field detection (v6.0 remnants)
- Type constraints (short: 2-6 chars, hierarchy_level ≥ 0, sovereignty_level 1-10)
- Memory directory existence warning
- Fallback soul generation for corruption recovery

**Test Coverage**: No dedicated test file found (validated indirectly via soul_distiller tests)

### 5. SoulStore (Atomic File Writer)

**Implementation**: `src/omega/soul_store.py` (217 lines)
- **4-Layer Guarantee Stack**:
  1. AtomicVisibility: same-directory rename
  2. CrashDurability: fsync before rename + fsync parent dir after
  3. WriterExclusion: fcntl.flock() exclusive lock
  4. IntegrityDetection: rolling .bak recovery files (default 3)
- **fsyncgate Pattern**: On fsync error → CRASH (per Postgres guidance)
- **Read Recovery**: Falls back to .bak files if main corrupt

**Test Coverage**: No dedicated test file found

### 6. Entity Registry (YAML-backed CRUD)

**Implementation**: `src/omega/oracle/entity_registry.py` (916 lines)
- **Shadow-Stacking**: Layered entities with priority-based projection
- **ZONEID Pattern**: Magic constant validation (Doom 1993 heritage)
- **Lazy Deletion**: Tombstone + 0.5s grace period (Quake 1996)
- **Multi-Index**: Name + Capability dual-index lookup
- **Hard-Boundary**: Engine zone (read-only) vs Game zone (writable)
- **Sovereign Permission**: soul.yaml/approved_lessons.yaml require SOVEREIGN_USER_TOKEN

**Test Coverage**: `tests/test_entity_registry.py` (4536 lines)

### 7. Metrics Infrastructure (MetricsDB)

**Implementation**: `src/omega/observability/metrics_db.py` (367 lines)
- **WAL-mode SQLite** with 6 tables:
  - `events` — General event ledger
  - `errors` — Error ledger with entity_id FK
  - `breaker_transitions` — Circuit breaker state changes
  - `performance` — Latency, tokens, cost, entity_id FK
  - `baselines` — Regression detection (3-sigma or %)
  - `vault_audit` — Credential access audit (M11 + M25)
- **Regression Detection**: 3-sigma rule with fallback to % threshold

**Test Coverage**: `tests/test_metrics_db.py` (282 lines, 22 tests)
- ✅ WAL mode verification
- ✅ Event/error/breaker/performance recording
- ✅ Baseline management
- ✅ Regression detection (3-sigma + %)
- ✅ Query methods (trend, error summary, breaker history)

**Critical Gap**: No soul-specific metrics tables or queries

---

## 🌐 Web Research: 2026 Best Practices

### Agent Configuration File Standards

| Practice | Source | Omega Status |
|----------|--------|--------------|
| **Schema-first validation** | LangChain AgentConfig, AutoGPT config.yaml | ✅ soul_validator.py |
| **Versioned schemas with migration** | Semantic Versioning for AI configs | ⚠️ Manual (v6.0→v6.1) |
| **Environment-specific overrides** | 12-factor config, Doppler patterns | ❌ Not implemented |
| **Secrets separation** | HashiCorp Vault, AWS Secrets Manager | ✅ SOVEREIGN_USER_TOKEN |
| **Immutable audit trails** | Event sourcing, CQRS | ✅ soul_edit_history.yaml |
| **Health scoring** | Kubernetes liveness/readiness probes | ❌ Not implemented |

### Soul/State Persistence Patterns

| Pattern | Source | Omega Status |
|---------|--------|--------------|
| **Append-only event log** | EventStoreDB, Kafka | ✅ soul_edit_history.yaml |
| **Atomic writes with fsync** | Postgres fsyncgate, etcd | ✅ SoulStore (4-layer) |
| **Rolling backups** | WAL-G, restic | ✅ .bak rotation (3 files) |
| **Schema migration** | Flyway, Liquibase | ⚠️ Manual validation only |
| **Cross-process locking** | fcntl, Redis Redlock | ✅ fcntl.flock() |

### Agent Instruction Testing

| Practice | Source | Omega Status |
|----------|--------|--------------|
| **Contract testing** | Pact, Spring Cloud Contract | ✅ M21 Gate Integrity (dataclass isinstance) |
| **Property-based testing** | Hypothesis, fast-check | ❌ Not implemented |
| **Chaos engineering** | Chaos Mesh, Litmus | ❌ Not implemented |
| **Golden file testing** | Snapshot testing | ❌ Not implemented |
| **Instruction compliance scoring** | Custom eval frameworks | ❌ Not implemented |

### Observability for AI Agents

| Metric | Source | Omega Status |
|--------|--------|--------------|
| **Token usage/cost** | OpenTelemetry, LangSmith | ✅ MetricsDB.performance |
| **Latency percentiles** | Prometheus, Grafana | ✅ MetricsDB.baselines |
| **Error rates by type** | Sentry, Honeycomb | ✅ MetricsDB.errors |
| **Agent health score** | Custom (no standard) | ❌ Not implemented |
| **Directive compliance** | Custom (no standard) | ❌ Not implemented |
| **Soul drift detection** | Custom (no standard) | ❌ Not implemented |
| **L3 principle adoption** | Custom (no standard) | ❌ Not implemented |

---

## 📊 Hardening Recommendations

### Priority 1: Metrics Infrastructure (Critical)

#### 1.1 Add Soul-Specific Metrics Tables to MetricsDB

```sql
-- Soul Health Tracking
CREATE TABLE IF NOT EXISTS soul_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    health_score REAL NOT NULL,           -- 0-100 composite
    directive_count INTEGER DEFAULT 0,
    directive_compliance REAL DEFAULT 0,  -- % of directives with validation
    l3_principle_count INTEGER DEFAULT 0,
    l3_adoption_rate REAL DEFAULT 0,      -- % of L3 principles "active"
    edit_frequency_24h REAL DEFAULT 0,    -- edits per day
    last_distillation_ts INTEGER,         -- last successful distillation
    schema_version TEXT DEFAULT '6.1',
    FOREIGN KEY (entity_id) REFERENCES entities(name)
);
CREATE INDEX idx_soul_health_ts ON soul_health(ts);
CREATE INDEX idx_soul_health_entity ON soul_health(entity_id);

-- Directive Tracking
CREATE TABLE IF NOT EXISTS directive_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    directive_id TEXT NOT NULL,
    action TEXT NOT NULL,                  -- 'created', 'validated', 'violated', 'archived'
    validation_result TEXT,                -- 'pass', 'fail', 'pending'
    trace_id TEXT,
    FOREIGN KEY (entity_id) REFERENCES entities(name)
);
CREATE INDEX idx_directive_entity ON directive_tracking(entity_id);
CREATE INDEX idx_directive_ts ON directive_tracking(ts);

-- Distillation Pipeline Metrics
CREATE TABLE IF NOT EXISTS distillation_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    entity_id TEXT NOT NULL,
    trace_id TEXT,
    classification TEXT NOT NULL,          -- 'routine', 'distilled', 'rejected'
    novelty_score REAL,
    quality_score REAL,
    l1_chars INTEGER,
    l2_chars INTEGER,
    l3_chars INTEGER,
    staging_gate_passed INTEGER DEFAULT 0, -- 0/1
    time_to_approve_hours REAL,            -- NULL if not yet approved
    FOREIGN KEY (entity_id) REFERENCES entities(name)
);
CREATE INDEX idx_distill_entity ON distillation_metrics(entity_id);
CREATE INDEX idx_distill_ts ON distillation_metrics(ts);
```

#### 1.2 Automated Soul Health Scoring

```python
# New: src/omega/oracle/soul_health.py
class SoulHealthScorer:
    """Computes composite health score for an entity's soul."""
    
    WEIGHTS = {
        "schema_compliance": 0.25,      # Passes soul_validator
        "directive_coverage": 0.20,     # Directives per domain
        "directive_validation": 0.15,   # % with validation rules
        "l3_principle_density": 0.15,   # L3 principles per 1000 tokens
        "distillation_recency": 0.10,   # Days since last distillation
        "edit_stability": 0.10,         # Low edit frequency = stable
        "memory_completeness": 0.05,    # All 3 memory files exist
    }
    
    def score(self, entity_name: str) -> SoulHealthReport:
        # Implementation...
```

#### 1.3 Directive Compliance Tracking

```python
# Hook into SoulValidator.validate_dict() to record directive validation
async def record_directive_validation(entity_name: str, directive: dict, result: bool):
    metrics_db.record_event(
        event_type="directive_validation",
        entity_id=entity_name,
        payload={"directive_id": directive["id"], "passed": result}
    )
```

### Priority 2: Testing Infrastructure (High)

#### 2.1 Property-Based Tests for Soul Evolution

```python
# tests/property/test_soul_evolution.py
from hypothesis import given, strategies as st
from omega.oracle.soul_validator import SoulValidator

@given(st.text(min_size=1, max_size=100))
def test_soul_name_validation(name):
    """Soul name must be non-empty string."""
    # Property: any non-empty string is valid name
    
@given(st.lists(st.dictionaries(st.text(), st.text()), min_size=1))
def test_directive_list_structure(directives):
    """Directives list must have id and rule for each entry."""
    # Property: every directive dict has required keys
```

#### 2.2 Contract Tests for Agent Instructions

```python
# tests/contract/test_agent_instructions.py
class TestAgentInstructionCompliance:
    """M21: Every agent must follow its declared directives."""
    
    @pytest.mark.parametrize("entity_name", ALL_ENTITIES)
    async def test_directive_rule_enforced(self, entity_name):
        """Each directive's 'rule' must be enforceable as a test."""
        soul = load_soul(entity_name)
        for directive in soul.get("directives", []):
            # Generate test from directive.rule
            test_fn = compile_rule_to_test(directive["rule"])
            assert test_fn(entity_name), f"Directive {directive['id']} violated"
```

#### 2.3 Chaos Engineering for Soul Persistence

```python
# tests/chaos/test_soul_crash_safety.py
class TestSoulCrashSafety:
    """Verify soul data survives: power loss, OOM kill, disk full."""
    
    @pytest.mark.anyio
    async def test_fsync_failure_crashes_process(self):
        """Per fsyncgate: fsync error must crash, not retry."""
        with patch("os.fsync", side_effect=OSError("disk full")):
            with pytest.raises(SoulStoreWriteError):
                await soul_store.write_atomic(path, content)
            # Process should exit — test in subprocess
    
    @pytest.mark.anyio
    async def test_concurrent_writes_no_corruption(self):
        """100 concurrent writers to same soul file."""
        async with anyio.create_task_group() as tg:
            for i in range(100):
                tg.start_soon(write_soul, f"content_{i}")
        # Verify all writes present, no corruption
```

### Priority 3: Observability & Dashboards (Medium)

#### 3.1 Real-Time Soul Health Dashboard

```python
# src/omega/observability/soul_dashboard.py
class SoulHealthDashboard:
    """Grafana-compatible metrics endpoint for soul health."""
    
    async def get_fleet_health(self) -> FleetHealthReport:
        """Aggregate health across all entities."""
        return {
            "entities": await self.get_all_entity_health(),
            "fleet_score": mean(e.health_score for e in entities),
            "directive_compliance": mean(e.directive_compliance for e in entities),
            "l3_adoption_rate": mean(e.l3_adoption_rate for e in entities),
            "stale_souls": [e for e in entities if e.days_since_distillation > 30],
        }
```

#### 3.2 Soul Drift Detection

```python
# src/omega/oracle/soul_drift_detector.py
class SoulDriftDetector:
    """Detects when soul.yaml diverges from approved lessons + directives."""
    
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

---

## 🔧 Implementation Plan

### Phase 1: Metrics Foundation (Week 1)
- [ ] Add soul_health, directive_tracking, distillation_metrics tables to MetricsDB
- [ ] Implement SoulHealthScorer with 7-factor composite
- [ ] Hook directive validation recording into SoulValidator
- [ ] Add distillation metrics recording to SoulDistillationPipeline

### Phase 2: Testing Hardening (Week 2)
- [ ] Add property-based tests for soul evolution (Hypothesis)
- [ ] Implement contract tests for agent instruction compliance
- [ ] Add chaos tests for SoulStore crash safety
- [ ] Create golden file tests for soul.yaml schema migrations

### Phase 3: Observability (Week 3)
- [ ] Build SoulHealthDashboard with Grafana JSON endpoint
- [ ] Implement SoulDriftDetector with daily cron
- [ ] Add HMC Hub integration for fleet health alerts
- [ ] Create soul health trend visualization

### Phase 4: Automation (Week 4)
- [ ] Automated v6.0→v6.1 migration tool
- [ ] Directive validation rule compiler (natural language → test)
- [ ] Soul health scoring in CI gate (fail if fleet_score < 70)
- [ ] Automated Staging Gate reminders for proposed_lessons

---

## 📈 Success Metrics

| Metric | Current | Target (Post-Hardening) |
|--------|---------|------------------------|
| Soul schema compliance | ~60% (2/5 entities full) | 100% |
| Directive validation coverage | 0% | 100% |
| L3 principle adoption tracking | 0% | 100% |
| Distillation pipeline observability | Manual only | Full metrics |
| Crash safety verification | Manual only | Automated chaos tests |
| Soul drift detection | None | Daily automated |
| Fleet health score | N/A | >85 sustained |

---

## 🔗 Related Documents

| Document | Purpose |
|----------|---------|
| `docs/architecture/ORACLE_DEEP_DIVE.md` | Oracle architecture reference |
| `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md` | Soul distillation protocol |
| `docs/research/R10_soul_schema_validation.md` | R-10 schema specification |
| `src/omega/oracle/soul_validator.py` | Schema enforcement implementation |
| `src/omega/oracle/soul_distiller.py` | L1→L2→L3 pipeline |
| `src/omega/oracle/soul_edit_history.py` | Immutable audit trail |
| `src/omega/soul_store.py` | Atomic file writer |
| `tests/test_soul_edit_history.py` | Audit trail contract tests |
| `tests/test_contract_soul_distiller.py` | Distillation contract tests |
| `tests/test_metrics_db.py` | MetricsDB contract tests |

---

*Report generated by @roc_racoon via deep infrastructure audit. All findings traceable to source files and test coverage.*