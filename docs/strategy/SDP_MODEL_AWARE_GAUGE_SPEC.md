# 🔱 SDP Model-Aware Gauge Specification
## Dynamic Context Window Detection and Per-Model Threshold Calculation

**AP Token:** `AP-SDP-MODEL-AWARE-GAUGE-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ MODEL-AWARE-GAUGE

**Date:** 2026-08-09
**Status:** ACTIVE — Mandatory for Phase 1 Context Gauge Implementation
**Mandate Binding:** M1 (AnyIO), M23 (Failure Integrity), M18 (Token Efficiency)

---

## §1 The Core Problem

The Context Gauge **cannot assume a fixed 200K window**. The active model's actual context window varies wildly:

| Model Category | Example Models | Context Window | Compaction Trigger | Notes |
|---|---|---|---|---|
| **OpenCode Zen Standard** | Sonnet 4.6, Gemini 3.6 Flash, Nemotron 3 Super | 200,000 | 85% (170K) | Default assumption |
| **OpenCode Zen Extended** | Nemotron 3 Ultra, Longcat 2.0 | 1,000,000 | 85% (850K) | Free tier available |
| **AGY Cloud** | Gemini 3.1 Pro | 2,000,000 | N/A (API limit) | Weekly pool limited |
| **AGY Cloud** | Claude Sonnet 4.6 / Opus 4.6 | 200,000 | N/A (API limit) | Weekly pool limited |
| **Local GGUF** | Qwen3-1.7B, Llama-3.1-8B | Configurable (4K-128K) | N/A (OOM) | Hardware limited |

**If the Gauge assumes 200K but the model is Nemotron 3 Ultra (1M), it will falsely report CRITICAL_REDZONE at 180K tokens (18% actual usage).**

---

## §2 Model Window Registry

### 2.0 Critical: Correct Token Data Source (G-4 Verified 2026-08-10)

**CRITICAL**: `session.tokens_input` overcounts by **~87×** (verified: 22M vs 253K).
NEVER use additive session totals for context pressure measurement.

**Correct query** (uses latest assistant message):
```sql
SELECT json_extract(data, '$.tokens.total') AS working_set_tokens,
       json_extract(data, '$.modelID') AS model_id,
       json_extract(data, '$.tokens.input') AS new_input,
       json_extract(data, '$.tokens.cache.read') AS cache_read
FROM message 
WHERE session_id = ? 
  AND json_extract(data, '$.role') = 'assistant'
ORDER BY time_created DESC 
LIMIT 1
```

**Python implementation**:
```python
import sqlite3
DB_PATH = Path.home() / ".local/share/opencode/opencode.db"
conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("""
    SELECT json_extract(data, '$.tokens.total') AS total,
           json_extract(data, '$.modelID') AS model
    FROM message 
    WHERE session_id = ? 
      AND json_extract(data, '$.role') = 'assistant'
    ORDER BY time_created DESC 
    LIMIT 1
""", (session_id,))
row = cur.fetchone()
working_set_tokens = row['total'] if row else 0
```

Full schema reference: `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md`

### 2.1 Source of Truth: `config/models.yaml`

```yaml
models:
  - id: "gemini-3.1-pro-preview-customtools"
    provider: "google"
    context_window: 2000000
    compaction_trigger_pct: 0.0   # No compaction - API limit only
    tier: 4
    is_agy: true
  
  - id: "claude-sonnet-4-6"
    provider: "antigravity"
    context_window: 200000
    compaction_trigger_pct: 0.0   # No compaction - API limit only
    tier: 2
    is_agy: true
  
  - id: "nemotron-3-ultra-free"
    provider: "opencode-zen"
    context_window: 1000000
    compaction_trigger_pct: 0.85  # OpenCode compacts at 85%
    tier: 3
    is_agy: false
  
  - id: "longcat-2.0-free"
    provider: "opencode-zen"
    context_window: 1000000
    compaction_trigger_pct: 0.85
    tier: 3
    is_agy: false
  
  - id: "qwen3-1.7b"
    provider: "native-gguf"
    context_window: 32768       # Configurable via LLAMA_CPP_N_CTX
    compaction_trigger_pct: 0.0  # No compaction - OOM instead
    tier: 1
    is_local: true
    kv_cache_per_token_bytes: 57344  # Calculated at load time
```

### 2.2 Runtime Resolution

The Gauge must resolve the active model's window **at query time**:

```python
async def get_active_model_window() -> ModelWindowInfo:
    """Resolve the current model's context window from multiple sources."""
    
    # Priority 1: OpenCode environment (most accurate)
    model_id = os.environ.get("OPENCODE_MODEL_ID")  # e.g., "nemotron-3-ultra-free"
    if model_id:
        config = load_models_yaml()
        model_config = config.get(model_id)
        if model_config:
            return ModelWindowInfo(
                model_id=model_id,
                context_window=model_config["context_window"],
                compaction_trigger_pct=model_config["compaction_trigger_pct"],
                tier=model_config["tier"],
                source="env"
            )
    
    # Priority 2: ProviderRegistry (fallback)
    provider = get_active_provider()  # From ModelGateway
    if provider:
        return ModelWindowInfo(
            model_id=provider.name,
            context_window=provider.context_window,
            compaction_trigger_pct=provider.compaction_trigger_pct,
            tier=provider.tier,
            source="registry"
        )
    
    # Priority 3: Conservative default
    return ModelWindowInfo(
        model_id="unknown",
        context_window=200_000,
        compaction_trigger_pct=0.85,
        tier=2,
        source="default"
    )
```

---

## §3 Gauge Output Schema (Extended)

### 3.1 Complete Output

```json
{
  "session_id": "ses_abc123",
  "model_info": {
    "model_id": "nemotron-3-ultra-free",
    "provider": "opencode-zen",
    "context_window": 1000000,
    "compaction_trigger_pct": 0.85,
    "tier": 3,
    "is_local": false,
    "is_agy": false,
    "source": "env"
  },
  "current_tokens": 162000,
  "current_percentage": 16.2,
  "message_count": 67,
  "redzone_threshold_pct": 80.0,
  "compaction_threshold_pct": 85.0,
  "tokens_to_redzone": 638000,
  "tokens_to_compaction": 688000,
  "status": "SAFE",
  "estimated_tokens_per_message": 2418,
  "recommended_action": "CONTINUE",
  
  "local_horizon": {
    "model_loaded": null,
    "kv_cache_gb": 0,
    "total_allocated_gb": 0,
    "available_ram_gb": 12.0,
    "status": "N/A"
  },
  
  "energy_budget": {
    "session_energy_joules": 12400,
    "sovereign_cost_equiv": 16200
  }
}
```

### 3.2 Status Calculation Logic

```python
def calculate_status(current_pct: float, compaction_pct: float, redzone_pct: float = 0.80) -> str:
    if compaction_pct == 0.0:
        # No compaction (AGY cloud, local) - only pool/ram limits matter
        return "SAFE"  # Handled by pool/ram gauges
    
    if current_pct >= redzone_pct:
        return "CRITICAL_REDZONE"
    elif current_pct >= (redzone_pct - 0.05):  # 75%
        return "REDZONE"
    else:
        return "SAFE"
```

---

## §4 Per-Model Threshold Overrides

Some models need custom thresholds due to their specific behavior:

| Model | Redzone | Compaction | Rationale |
|---|---|---|---|
| **Nemotron 3 Ultra / Longcat 2.0** | 80% (800K) | 85% (850K) | Standard |
| **AGY Models (Gemini 3.1 Pro, Sonnet 4.6)** | N/A | N/A | No compaction — use **Pool Gauge** instead |
| **Local GGUF** | N/A | N/A | No compaction — use **RAM Gauge** instead |
| **Standard 200K Models** | 80% (160K) | 85% (170K) | Standard |

**Implementation:** The Gauge returns `compaction_threshold_pct = 0.0` for models without compaction, and the agent logic switches to the appropriate gauge (Pool Gauge for AGY, RAM Gauge for local).

---

## §5 Multi-Gauge Architecture

The "Context Gauge" is actually a **Gauge Aggregator** that routes to the correct sub-gauge:

```
omega-hub_get_context_pressure
    │
    ├─► Resolve active model → ModelWindowInfo
    │
    ├─► IF model.is_agy:
    │       ► Call PoolGauge (V-1 Vault) → tokens_remaining, pool_status
    │       ► Return AGY_GAUGE_OUTPUT
    │
    ├─► ELIF model.is_local:
    │       ► Call RAMGauge (hardware_stats + KV cache calc) → ram_remaining, max_safe_ctx
    │       ► Return LOCAL_GAUGE_OUTPUT
    │
    └─► ELSE (daily cloud model):
            ► Call TokenGauge (opencode.db) → current_tokens, percentages
            ► Return TOKEN_GAUGE_OUTPUT
```

### 5.1 AGY Gauge Output (Pool-Based)

```json
{
  "gauge_type": "AGY_POOL",
  "model_id": "gemini-3.1-pro",
  "account_id": "account-3",
  "weekly_pool_tokens": 1000000,
  "used_this_week": 450000,
  "remaining": 550000,
  "pool_status": "PARTIAL",
  "estimated_tokens_for_task": 15000,
  "can_accommodate": true,
  "recommended_action": "PROCEED | ESCALATE_TO_DIFFERENT_ACCOUNT | WAIT_FOR_REFRESH"
}
```

### 5.2 Local Gauge Output (RAM-Based)

```json
{
  "gauge_type": "LOCAL_RAM",
  "model_id": "qwen3-1.7b",
  "n_ctx": 32768,
  "kv_cache_gb": 1.80,
  "model_weights_gb": 1.75,
  "total_allocated_gb": 4.20,
  "available_ram_gb": 12.00,
  "remaining_ram_gb": 7.80,
  "max_safe_n_ctx": 65536,
  "ram_status": "SAFE",
  "recommended_action": "CONTINUE | REDUCE_CTX | OFFLOAD_TO_CLOUD"
}
```

---

## §6 Integration with ModelGateway

The `ModelGateway.generate()` method is the **single point of truth** for the active model. It must expose the model info to the Gauge:

```python
# In src/omega/oracle/model_gateway.py

class ModelGateway:
    def __init__(self, ...):
        self._active_model_info: Optional[ModelWindowInfo] = None
    
    async def generate(self, ..., model_name: Optional[str] = None, ...) -> GenerateResult:
        # Resolve model before generation
        provider = await self._select_provider(model_name)
        self._active_model_info = ModelWindowInfo(
            model_id=provider.name,
            context_window=provider.config.context_window,
            compaction_trigger_pct=provider.config.compaction_trigger_pct,
            tier=provider.config.tier,
            is_local=provider.is_local,
            is_agy=provider.is_agy
        )
        # ... rest of generation
    
    def get_active_model_info(self) -> Optional[ModelWindowInfo]:
        return self._active_model_info
```

The Gauge tool calls `ModelGateway.get_active_model_info()` via the MCP server.

---

## §7 Testing Requirements

| Test | Description |
|---|---|
| **Model Resolution** | Mock `OPENCODE_MODEL_ID` env var → verify correct window returned |
| **Priority Fallback** | Env var missing → ProviderRegistry used → Default used |
| **AGY Gauge** | Mock V-1 Vault → verify pool status calculation |
| **Local Gauge** | Mock hardware stats + model config → verify KV cache calc |
| **Threshold Logic** | Parametrized: 74%→SAFE, 76%→REDZONE, 81%→CRITICAL |
| **Compaction=0 Handling** | AGY/Local models return `compaction_threshold_pct: 0` → status=SAFE |
| **Multi-Gauge Routing** | Integration test: each model type routes to correct sub-gauge |

---

## §8 Implementation Checklist

| Component | Spec Section | Phase | Owner |
|---|---|---|---|
| `config/models.yaml` schema | §2.1 | 1 | N3 Engineering |
| ModelWindowInfo dataclass | §2.2 | 1 | N3 Engineering |
| Gauge Aggregator | §5 | 1 | N1 Infrastructure |
| Pool Gauge (V-1 integration) | §5.1 | 3 | N1 Infrastructure / V-1 Vault |
| RAM Gauge (Hardware Horizon) | §5.2 | 1 | N1 Infrastructure |
| ModelGateway integration | §6 | 1 | N3 Engineering |
| Token Gauge (opencode.db) | Existing | 1 | N1 Infrastructure |
| Per-model threshold config | §4 | 1 | N3 Engineering |
| Test suite | §7 | 1 | N10 Validation |

---

*⬡ OMEGA ⬡ SDP-MODEL-AWARE-GAUGE ⬡ 2026-08-09*