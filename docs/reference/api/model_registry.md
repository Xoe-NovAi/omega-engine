# 🔱 Model Registry — Unified Model Catalog & SQLite Index
**AP Token**: `AP-MODEL-REGISTRY-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Model Registry package — YAML frontmatter model cards, provider configs, research profiles, and derived SQLite index.
**Tags**: model-registry, catalog, sqlite, index, model-cards, providers
**Cross-references**: src/omega/model_registry/registry.py, src/omega/model_registry/models.py, src/omega/model_registry/providers.py, src/omega/model_registry/query.py, src/omega/model_registry/research.py, config/model_registry/

---

## Overview

The `model_registry` package provides a **unified model catalog** for the Omega Engine. It follows the principle: **files are source of truth, SQLite is derived index**.

```
┌─────────────────────────────────────────────────────────────┐
│                  Model Registry Package                      │
├─────────────────────────────────────────────────────────────┤
│  registry.py         │  ModelRegistry — load, index, query  │
│  models.py           │  Data classes (ModelCard, etc.)      │
│  providers.py        │  ProviderConfig                      │
│  research.py         │  ResearchProfile                     │
│  query.py            │  ModelRegistryQuery — fluent API     │
│  __init__.py         │  Public exports                      │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow**:
```
YAML Frontmatter (.yaml.md)  ──load_all()──▶  ModelRegistry (in-memory)
                                      │
                                      ▼
                              build_index() ──▶  SQLite Index (config/model_registry/index.sqlite)
                                      │
                                      ▼
                              ModelRegistryQuery ──▶  Fluent queries
```

---

## Directory Structure

```
config/model_registry/
├── models/                    # Model cards (YAML frontmatter)
│   ├── local/
│   ├── cloud/
│   └── cli/
├── providers/                 # Provider configurations (.yaml)
├── research_profiles/         # Research profiles (.yaml)
├── model_db/                  # Legacy CURRENT_MODELS.md
└── index.sqlite               # Derived SQLite index (gitignored)
```

---

## Core Classes

### ModelRegistry

Main registry service — loads all sources, builds SQLite index, provides query access.

#### Constructor

```python
ModelRegistry(registry_root: str = "config/model_registry")
```

#### Methods

##### `load_all() -> None`
Load all model cards, providers, and research profiles from disk.

```python
registry = ModelRegistry()
registry.load_all()
print(f"Loaded {len(registry._model_cards)} models")
print(f"Loaded {len(registry._providers)} providers")
```

##### `get_model(model_id: str) -> Optional[ModelCard]`
Get model card by ID.

##### `get_models(platform=None, tier=None, provider=None) -> List[ModelCard]`
Get models with optional filters.

```python
# All local T1 models
local_t1 = registry.get_models(platform=Platform.LOCAL, tier=Tier.T1)

# All OpenRouter models
openrouter = registry.get_models(provider="openrouter")
```

##### `get_provider(provider_name: str) -> Optional[ProviderConfig]`
Get provider config by name.

##### `get_providers() -> List[ProviderConfig]`
Get all providers sorted by priority.

##### `get_research_profile(profile_name: str) -> Optional[ResearchProfileData]`
Get research profile by name.

##### `build_index() -> None`
Build SQLite index from loaded data. **Drops existing tables** to prevent schema drift.

```python
registry.build_index()
# Index built at config/model_registry/index.sqlite
```

##### `query(sql: str, params: tuple = ()) -> List[Dict]`
Execute raw SQL on index.

```python
results = registry.query(
    "SELECT model_id, context_window FROM models WHERE platform = ? AND tier = ?",
    ("local", "T1")
)
```

---

## Data Models (models.py)

### Enums

| Enum | Values | Description |
|------|--------|-------------|
| `Platform` | `CLOUD`, `LOCAL`, `CLI`, `STEALTH` | Deployment platform |
| `Tier` | `T1`, `T2`, `T3` | Capability tier |
| `Status` | `ACTIVE`, `DEPRECATED`, `EXPERIMENTAL`, `STEALTH` | Model status |

### ModelCard

Complete model specification with 30+ fields.

**Core Identity**:
```python
model_id: str                    # Unique identifier
display_name: str                # Human-readable name
version: str                     # Version string
provider: str                    # Provider name (openrouter, native-gguf, etc.)
platform: Platform               # CLOUD | LOCAL | CLI | STEALTH
tier: Tier                       # T1 | T2 | T3
status: Status                   # ACTIVE | DEPRECATED | EXPERIMENTAL | STEALTH
context_window: int              # Context window in tokens
max_output_tokens: int = 0       # Max output tokens
```

**Capabilities** (0.0-1.0 scores + boolean flags):
```python
capabilities: Capabilities = Capabilities(
    reasoning: float = 0.0,
    code_generation: float = 0.0,
    knowledge: float = 0.0,
    creative: float = 0.0,
    tool_use: bool = False,
    structured_output: bool = False,
    multimodal: bool = False,
    code_execution: bool = False,      # Extended (P1)
    parallel_search: bool = False,     # Extended (P1)
    workspace_integration: bool = False # Extended (P1)
)
```

**Economics**:
```python
pricing: Pricing = Pricing(
    input_per_mtok: float = 0.0,
    output_per_mtok: float = 0.0,
    cached_input_per_mtok: float = 0.0,
    batch_discount: float = 0.0,
    intro_pricing: Optional[dict] = None,
    free_tier: bool = False,
    cost_per_1k_tokens_usd: float = 0.0
)
latency_p99_ms: int = 0
uptime_percent: float = 0.0
```

**Sampling Parameters (T1)**:
```python
parameters: Parameters = Parameters(
    temperature: float = 0.7,
    top_p: float = 0.95,
    top_k: int = 40,
    repetition_penalty: float = 1.1,
    max_tokens: int = 4096,
    stop_sequences: List[str] = [],
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    logit_bias: Optional[dict] = None,
    seed: Optional[int] = None,
    model_specific_overrides: dict = {}
)
```

**Model Architecture (P1)**:
```python
architecture: ModelArchitecture = ModelArchitecture(
    total: str = "Unknown",
    active: str = "Unknown",
    architecture: str = "unknown",  # dense, MoE, hybrid, router
    experts: int = 0,
    active_experts: int = 0,
    shared_experts: int = 0,
    quantization: str = "Unknown",
    training_tokens: str = "Unknown",
    source: str = "estimated",  # official, estimated, community
    verified: bool = False,
    verified_date: Optional[str] = None
)
```

**Routing**:
```python
routing: Routing = Routing(
    engine_routable: bool = True,
    opencode_cli_only: bool = False,
    recommended_engine_alternative: Optional[str] = None
)
```

**Identity & Community** (for stealth models):
```python
identity_history: Optional[IdentityHistory] = None
community_intelligence: Optional[CommunityIntelligence] = None
live_api_state: Optional[LiveAPIState] = None
```

**Research & Evidence**:
```python
research_profile: ResearchProfile = ResearchProfile()
empirical_evidence: EmpiricalEvidence = EmpiricalEvidence()
provider_fabric: ProviderFabric = ProviderFabric()
benchmark_sources: BenchmarkSources = BenchmarkSources()
```

**Metadata**:
```python
tags: List[str] = []
created_at: str = ""
updated_at: str = ""
schema_version: str = "1.2.0"
```

---

## ProviderConfig (providers.py)

```python
@dataclass
class ProviderConfig:
    provider: str                    # Unique name
    priority: int                    # Lower = higher priority
    enabled: bool = True
    description: str = ""
    api_key: Optional[str] = None    # Single key (legacy)
    api_keys: List[str] = []         # Multiple keys (current)
    base_url: str = ""
    endpoint: str = ""
    supported_models: List[str] = []
```

---

## ResearchProfile (research.py)

```python
@dataclass
class ResearchProfile:
    profile: str                     # Profile name
    context_window: int = 4096
    reasoning_depth: str = "iterative"  # "single" | "iterative" | "deep"
    tool_fidelity: str = "medium"       # "low" | "medium" | "high"
    failure_signature: str = "shallow"
    shadow_focus: str = "force_deepening"
    guardrails: List[str] = []
```

---

## ModelRegistryQuery (query.py)

Fluent query builder for the SQLite index.

```python
from omega.model_registry import ModelRegistry, ModelRegistryQuery

registry = ModelRegistry()
registry.load_all()
registry.build_index()

query = ModelRegistryQuery(registry.index_path)

# Fluent API
results = (query
    .platform(Platform.LOCAL)
    .tier(Tier.T1)
    .min_context_window(8192)
    .has_capability("tool_use")
    .order_by("context_window", desc=True)
    .limit(10)
    .execute())

# Raw SQL fallback
results = query.raw("SELECT * FROM models WHERE platform = ?", ("local",))
```

### Query Methods

| Method | Description |
|--------|-------------|
| `platform(p)` | Filter by Platform |
| `tier(t)` | Filter by Tier |
| `provider(p)` | Filter by provider name |
| `status(s)` | Filter by Status |
| `min_context_window(n)` | Minimum context window |
| `max_context_window(n)` | Maximum context window |
| `has_capability(cap)` | Boolean capability filter |
| `free_tier_only()` | Only free models |
| `order_by(field, desc=False)` | Order results |
| `limit(n)` | Limit results |
| `execute()` | Execute and return List[Dict] |
| `count()` | Return count only |
| `raw(sql, params)` | Execute raw SQL |

---

## YAML Frontmatter Format

Model cards use YAML frontmatter in `.yaml.md` files:

```yaml
---
model_id: "gemma-4b-local"
display_name: "Gemma 4B Local"
version: "2026-07-15"
provider: "native-gguf"
platform: "local"
tier: "T1"
status: "active"
context_window: 8192
max_output_tokens: 4096

capabilities:
  reasoning: 0.75
  code_generation: 0.80
  knowledge: 0.70
  creative: 0.65
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false

pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  free_tier: true
  cost_per_1k_tokens_usd: 0.0

latency_p99_ms: 1200
uptime_percent: 99.5

parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.1
  max_tokens: 4096

routing:
  engine_routable: true
  opencode_cli_only: false

tags: ["local", "gemma", "efficient"]
created_at: "2026-07-15"
updated_at: "2026-07-15"
schema_version: "1.2.0"
---

# Model Description

Markdown content here...
```

---

## Case-Insensitive Enum Parsing

The registry handles inconsistent casing in YAML files via `_enum_ci()`:

```python
# "LOCAL", "local", "Local" → Platform.LOCAL
# "ACTIVE", "active", "Active" → Status.ACTIVE
# "T1", "t1" → Tier.T1
```

This prevents a single malformed card from breaking the entire index build.

---

## Legacy Support

The registry also loads from `model_db/CURRENT_MODELS.md` (legacy format):

```yaml
models:
  gpt-oss-120b-local:
    provider: "openrouter"
    context_window: 128000
    capabilities:
      reasoning: 0.95
      code_generation: 0.90
    # ... auto-parsed to ModelCard
```

Provider names are normalized: `together`→`openrouter`, `sambanova`→`openrouter`, etc.

---

## Usage Example

```python
from omega.model_registry import ModelRegistry, ModelRegistryQuery, Platform, Tier

# Initialize
registry = ModelRegistry("config/model_registry")
registry.load_all()
registry.build_index()

# Direct access
model = registry.get_model("gemma-4b-local")
print(f"{model.display_name}: {model.context_window} ctx, ${model.pricing.cost_per_1k_tokens_usd}/1k")

# Filtered queries
local_models = registry.get_models(platform=Platform.LOCAL, tier=Tier.T1)
for m in local_models:
    print(f"  {m.model_id}: {m.capabilities.reasoning} reasoning")

# Fluent query
query = ModelRegistryQuery(registry.index_path)
best_coders = (query
    .platform(Platform.LOCAL)
    .has_capability("code_generation")
    .order_by("capabilities.code_generation", desc=True)
    .limit(5)
    .execute())

# Provider lookup
provider = registry.get_provider("openrouter")
print(f"OpenRouter priority: {provider.priority}, enabled: {provider.enabled}")
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Registry is sync; async callers use `anyio.to_thread` |
| **M2 Firewall** | Registry is config/data; no engine logic |
| **M7 Local-First** | Platform.LOCAL models prioritized in queries |
| **M13 Temple-Grade** | `build_index()` drops tables to prevent drift |
| **M23 Failure Integrity** | `_enum_ci` prevents single-card corruption |

---

## Testing

```bash
pytest tests/test_model_registry.py -v
```

Key test scenarios:
- YAML frontmatter parsing
- Case-insensitive enum handling
- Legacy format migration
- SQLite index build + query
- Fluent query builder
- Provider config loading

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ MODEL_REGISTRY-v1.0.0 ⬡ 2026-10-02 ⬡*