# 🔱 Orchestration — Sovereign Triage Router
**AP Token**: `AP-ORCHESTRATION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Orchestration module — deterministic model selection based on domain, entity soul, and real-time health.
**Tags**: orchestration, triage, model-selection, routing, resource-guard
**Cross-references**: src/omega/orchestration/triage_router.py, src/omega/oracle/model_gateway.py, src/omega/oracle/resource_guard.py, docs/architecture/ORACLE_DEEP_DIVE.md

---

## Overview

The `orchestration` package implements the **Sovereign Triage Router** — a deterministic model selection engine that routes queries to the optimal model based on:

1. **Domain inference** — keyword-based classification + entity routing history
2. **Entity preferences** — model preferences stored in each entity's `soul.yaml`
3. **Real-time health** — quota usage, success rates, latency from `HealthMonitor`
4. **Hard constraints** — context window, cost ceiling, latency budget

This is the **single control plane** for model routing (D-536: one router only).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Package                     │
├─────────────────────────────────────────────────────────────┤
│  triage_router.py   │  TriageRouter — main entry point      │
│  __init__.py        │  (empty — exports via triage_router)  │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow**:
```
Query → TriageRequest → Domain Inference → Entity Soul Lookup
                              ↓
                    Candidate Pool Assembly (T1/T2/T3 tiers)
                              ↓
                    Constraint Filtering (context, cost, latency)
                              ↓
                    Score Adjustment (health + quota)
                              ↓
                    Selection + Fallback Chain → TriageResponse
```

---

## Core Data Models

### TaskRequest
```python
@dataclass
class TaskRequest:
    description: str                    # User query
    domain: Optional[str] = None        # Explicit domain override
    estimated_tokens: int = 1000        # Token budget estimate
    complexity: str = "standard"        # "fast" | "standard" | "deep"
    preferred_models: List[str] = []    # Explicit model preferences
```

### EntityContext
```python
@dataclass
class EntityContext:
    name: str                           # Entity name (e.g., "Prometheus")
    soul_path: Path                     # Path to entity's soul.yaml
    current_temperature: Optional[float] = None
    domain_affinity: Dict[str, float] = {}  # Historical domain scores
```

### Constraints
```python
@dataclass
class Constraints:
    max_latency_ms: Optional[int] = None
    max_cost_usd: Optional[float] = None
    available_tokens: Optional[int] = None
    preferred_backends: List[str] = ["local", "cloud"]
```

### TriageRequest (Composite)
```python
@dataclass
class TriageRequest:
    task: TaskRequest
    entity: EntityContext
    constraints: Constraints
    session: SessionContext
```

### TriageResponse
```python
@dataclass
class TriageResponse:
    selected_model: ModelSelection      # Chosen model + params
    fallback_chain: List[FallbackOption]  # Up to 3 fallbacks + mock
    confidence: float                   # Selection confidence (0.0-1.0)
    reasoning: List[str]                # Human-readable rationale
    estimated_latency_ms: int
    estimated_cost_usd: float
    routing_timestamp: str              # ISO 8601
    expires_at: str                     # ISO 8601 (10s TTL)
```

---

## TriageRouter

### Constructor
```python
TriageRouter(
    health_monitor: Optional[HealthMonitor] = None,
    capability_matrix: Optional[Dict] = None
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `health_monitor` | `HealthMonitor` | Real-time health data (quota, latency, success rate) |
| `capability_matrix` | `Dict[str, List[Model]]` | Domain → model mappings |

### Main Method

#### `async select_model(request: TriageRequest) -> TriageResponse`

Execute the full triage pipeline and return a routing decision.

```python
from omega.orchestration import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext
from pathlib import Path

router = TriageRouter(health_monitor=health_monitor, capability_matrix=cap_matrix)

request = TriageRequest(
    task=TaskRequest(
        description="Harden the container security configuration",
        complexity="deep",
        estimated_tokens=2000
    ),
    entity=EntityContext(
        name="Prometheus",
        soul_path=Path("data/entities/prometheus/soul.yaml")
    ),
    constraints=Constraints(
        max_latency_ms=5000,
        max_cost_usd=0.05,
        preferred_backends=["local"]
    ),
    session=SessionContext(id="ses_123", trace_id="trace_456")
)

response = await router.select_model(request)
print(f"Selected: {response.selected_model.name} via {response.selected_model.provider}")
print(f"Confidence: {response.confidence:.2f}")
print(f"Reasoning: {response.reasoning}")
```

---

## Domain Inference

The router classifies tasks into domains using keyword matching:

| Domain | Keywords |
|--------|----------|
| `strength` | protect, defend, fight, warrior, power, boundary |
| `dream` | imagine, create, inspire, poetry, healing, flow, emotion |
| `will` | sovereign, decision, light, rebellion, creation, forethought |
| `voice` | speak, knowledge, art, communication, speech, language |
| `descent` | dream, underworld, transformation, descent, rebirth |
| `analysis` | analyze, research, audit, review, synthesize, compare |
| `creation` | code, implement, build, design, architect, write |

**Priority**:
1. Explicit `task.domain` override
2. Keyword scoring (highest score wins)
3. Entity's most common recent domain (from `soul.yaml` routing_history)
4. Default: `"general"`

---

## Candidate Pool Assembly (3 Tiers)

| Tier | Source | Base Score | Description |
|------|--------|------------|-------------|
| **T1** | Entity `soul.yaml` → `model_preferences.by_domain[domain]` | 1.0 | Entity-optimized models |
| **T2** | `capability_matrix[domain]` | 0.7 | Task-appropriate models |
| **T3** | `capability_matrix["universal"]` or mock | 0.3/0.1 | Universal fallback |

Models failing health checks (`health_monitor.is_available()`) are excluded.

---

## Constraint Filtering

Hard filters applied to candidate pool:

| Constraint | Check |
|------------|-------|
| `available_tokens` | `model.context_window >= available_tokens` |
| `max_cost_usd` | `estimated_cost <= max_cost_usd` |
| `max_latency_ms` | `health_monitor.get_latency_p99(model) <= max_latency_ms` |

If **no candidates survive**, emergency escalation uses all candidates (ignoring constraints).

---

## Score Adjustment

Real-time adjustments applied to base tier scores:

| Factor | Impact | Formula |
|--------|--------|---------|
| Quota usage | -30% max | `score *= 1.0 - quota_usage * 0.3` |
| Success rate | +20% max | `score *= 0.8 + success_rate * 0.2` |

---

## Fallback Chain

Up to 3 fallbacks + final mock safety net:

```python
fallback_chain = [
    FallbackOption(model="model-b", provider="local", reason="T2_task_appropriate fallback"),
    FallbackOption(model="model-c", provider="cloud", reason="T3_universal_fallback fallback"),
    FallbackOption(model="mock", provider="mock", reason="Final offline fallback")
]
```

---

## Dynamic Temperature Calculation

| Complexity | Base Temp | Creative Domain Bonus |
|------------|-----------|----------------------|
| `fast` | 0.3 | +0.2 (capped at 1.0) |
| `standard` | 0.7 | +0.2 |
| `deep` | 0.5 | +0.2 |

Creative domains: `dream`, `art`, `poetry`

Entity's `current_temperature` (from soul) overrides if set.

---

## Configuration

### Capability Matrix Structure
```python
capability_matrix = {
    "analysis": [Model(name="gemma-4b", provider="local", context_window=8192, ...)],
    "creation": [Model(name="qwen3-4b", provider="local", context_window=32768, ...)],
    "universal": Model(name="nemotron-3-ultra", provider="cloud", context_window=128000, ...),
    # ... other domains
}
```

### HealthMonitor Interface
```python
class HealthMonitor:
    def is_available(self, model_name: str) -> bool: ...
    def get_quota_usage(self, provider: str) -> float: ...      # 0.0-1.0
    def get_success_rate(self, model_name: str) -> float: ...   # 0.0-1.0
    def get_latency_p99(self, model_name: str) -> int: ...      # milliseconds
```

---

## Usage Example

```python
from omega.orchestration import TriageRouter
from omega.oracle import HealthMonitor
from pathlib import Path

# Initialize with real health monitor
health = HealthMonitor()
cap_matrix = load_capability_matrix()  # From config
router = TriageRouter(health_monitor=health, capability_matrix=cap_matrix)

# Route a query for entity "Kali"
request = TriageRequest(
    task=TaskRequest(
        description="Audit the firewall rules for Mandate 2 compliance",
        complexity="standard",
        estimated_tokens=1500
    ),
    entity=EntityContext(
        name="Kali",
        soul_path=Path("data/entities/kali/soul.yaml")
    ),
    constraints=Constraints(
        max_latency_ms=3000,
        max_cost_usd=0.0,  # Local only
        preferred_backends=["local"]
    ),
    session=SessionContext(id="ses_789", trace_id="trace_abc")
)

response = await router.select_model(request)

# Use the selected model
from omega.oracle import ModelGateway
gateway = ModelGateway()
result = await gateway.generate(
    model_name=response.selected_model.name,
    system_prompt="You are Kali, the auditor...",
    user_query=request.task.description,
    temperature=response.selected_model.temperature,
    max_tokens=response.selected_model.context_window
)
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio`; no `asyncio` imports |
| **M7 Local-First** | `preferred_backends` defaults to `["local", "cloud"]`; local models in T1/T2 |
| **M13 Temple-Grade** | Hard constraint filtering; no silent degradation |
| **M23 Failure Integrity** | Emergency escalation on empty candidate pool; explicit error paths |

---

## Testing

```bash
pytest tests/test_triage_router.py -v
```

Key test scenarios:
- Domain inference accuracy
- Tier assembly and filtering
- Constraint enforcement
- Fallback chain construction
- Temperature calculation
- Health monitor integration

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ ORCHESTRATION-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

