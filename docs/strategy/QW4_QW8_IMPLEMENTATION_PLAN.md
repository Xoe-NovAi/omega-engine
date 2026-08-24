# 🔱 QW-4 & QW-8 Implementation Plan
## pool_tracker Wiring + Context Gauge Greenfield

**AP Token**: `AP-QW4-QW8-IMPL-PLAN-20260810-v1.0.0`
⬡ OMEGA ⬡ IMPLEMENTATION ⬡ QW4 ⬡ QW8 ⬡ PLAN

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: READY FOR IMPLEMENTATION

---

## 📋 QW-4: pool_tracker.py Wiring

### Objective
Replace reactive key rotation (429-only) with proactive drain-aware selection from `pool_tracker.py`.

### Current State
- `RemoteProvider.generate()` rotates `_active_key_index` on 429 (reactive)
- `UsagePoolTracker` in `pool_tracker.py` is dead code (standalone, not imported)
- `USAGE_POOL_LOG.json` exists with 8 keys (agy_key_01-08), all active, zero usage
- `ProviderConfig.api_keys` field exists and is populated for cloud providers

### Implementation Steps

#### Step 1: Initialize pool_tracker in ModelGateway.__init__()

```python
# src/omega/oracle/model_gateway.py

from omega.oracle.pool_tracker import UsagePoolTracker
from omega.oracle.pool_state import PoolState

class ModelGateway:
    def __init__(self, ...):
        # ... existing init ...
        
        # Initialize pool tracker if Antigravity entity exists
        self._pool_tracker: Optional[UsagePoolTracker] = None
        antigravity_soul = Path("data/entities/antigravity/soul.yaml")
        if antigravity_soul.exists():
            pool_state = PoolState.from_soul(antigravity_soul)
            if pool_state.pool_g or pool_state.pool_c:
                self._pool_tracker = UsagePoolTracker(pool_state=pool_state)
```

#### Step 2: Select key before provider call (in generate())

```python
# In ModelGateway.generate(), after provider selection:

# Step 1.7: Pool-aware key selection (QW-4)
if self._pool_tracker and self._is_cloud_provider(provider):
    # Determine pool name from provider
    pool_name = "pool_g" if "google" in provider.name or "gemini" in provider.name else "pool_c"
    # Select best key (drain-aware scoring)
    selected_key = await self._pool_tracker.select_key(pool_name, model_name)
    if selected_key:
        # Set the active key index to the selected key
        key_idx = provider.config.api_keys.index(selected_key) if selected_key in provider.config.api_keys else 0
        provider._active_key_index = key_idx
        logger.info(f"Pool tracker selected key {selected_key} (index {key_idx}) for {provider.name}")
```

#### Step 3: Track usage after successful inference

```python
# In ModelGateway.generate(), after successful result:

# Track usage to pool_tracker (QW-4)
if self._pool_tracker and self._is_cloud_provider(provider):
    pool_name = "pool_g" if "google" in provider.name or "gemini" in provider.name else "pool_c"
    tokens_used = len(system_prompt) // 4 + len(result) // 4  # rough estimate
    await self._pool_tracker.track_usage(
        pool=pool_name,
        model=model_name,
        key_id=selected_key or "unknown",
        tokens=tokens_used,
        success=True
    )
```

#### Step 4: Add pool health endpoint

```python
# In ModelGateway:

async def get_pool_health(self, pool_name: str) -> Optional[dict]:
    """Get pool health snapshot."""
    if not self._pool_tracker:
        return None
    health = await self._pool_tracker.get_pool_health(pool_name)
    return {
        "pool_name": health.pool_name,
        "total_keys": health.total_keys,
        "available_keys": health.available_keys,
        "cooling_keys": health.cooling_keys,
        "drained_keys": health.drained_keys,
        "remaining_quota_pct": health.remaining_quota_pct,
        "is_healthy": health.is_healthy,
    }
```

### Files to Modify
- `src/omega/oracle/model_gateway.py` — wire pool_tracker

### Tests to Add
- `tests/contract/test_pool_tracker_integration.py` — verify key selection, usage tracking, pool health

### Estimated Effort: 2 hours

---

## 📋 QW-8: Context Gauge (Greenfield)

### Objective
Build context pressure measurement system that measures absolute working-set tokens and applies color bands.

### Data Source (Verified)
- **Primary**: `message.data.tokens.total` from latest assistant message in opencode.db
- **Fallback**: `token_estimator.estimate_tokens()` for pre-inference estimation
- **DO NOT USE**: `session.tokens_input` (overcounts ~87×)

### Implementation Steps

#### Step 1: Create ContextGauge class

```python
# src/omega/oracle/context_gauge.py

import sqlite3
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Context windows from SDP ground truth (2026-08-09)
MODEL_WINDOWS = {
    "nemotron-3-ultra-free": 1_000_000,
    "longcat-2.0-free": 1_000_000,
    "laguna-s-2.1-free": 262_144,
    "deepseek-v4-flash-free": 1_000_000,
    "nvidia/nemotron-3-super-120b-a12b:free": 262_144,
    "poolside/laguna-s-2.1:free": 262_144,
}

# Color bands (absolute working-set tokens)
BANDS = [
    (40_000, "GREEN", "Full reasoning capacity"),
    (90_000, "YELLOW", "Prefer delegating searches"),
    (150_000, "ORANGE", "Split before reading"),
    (250_000, "RED", "Handoff imminent"),
    (float('inf'), "BLACK", "STOP — hand off now"),
]

@dataclass
class GaugeResult:
    session_id: str
    model_id: str
    context_window: int
    working_set_tokens: int
    new_input_tokens: int
    cache_read_tokens: int
    output_tokens: int
    utilization_pct: float
    band: str
    band_description: str
    recommended_action: str
    tokens_to_redzone: int
    tokens_to_compaction: int

class ContextGauge:
    """Measures context pressure for active OpenCode sessions."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".local/share/opencode/opencode.db"
    
    def get_context_pressure(self, session_id: str) -> Optional[GaugeResult]:
        """Get current context pressure for a session."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get latest assistant message
        cur.execute("""
            SELECT json_extract(data, '$.tokens.total') AS total,
                   json_extract(data, '$.tokens.input') AS new_input,
                   json_extract(data, '$.tokens.cache.read') AS cache_read,
                   json_extract(data, '$.tokens.output') AS output,
                   json_extract(data, '$.modelID') AS model
            FROM message 
            WHERE session_id = ? 
              AND json_extract(data, '$.role') = 'assistant'
            ORDER BY time_created DESC 
            LIMIT 1
        """, (session_id,))
        
        row = cur.fetchone()
        conn.close()
        
        if not row or row['total'] is None:
            return None
        
        model_id = row['model'] or "unknown"
        working_set = row['total']
        context_window = MODEL_WINDOWS.get(model_id, 200_000)
        
        # Calculate band
        band, description = self._calculate_band(working_set)
        
        # Calculate utilization
        utilization = (working_set / context_window) * 100 if context_window > 0 else 0
        
        # Calculate thresholds
        redzone_threshold = int(context_window * 0.80)
        compaction_threshold = int(context_window * 0.85)
        
        return GaugeResult(
            session_id=session_id,
            model_id=model_id,
            context_window=context_window,
            working_set_tokens=working_set,
            new_input_tokens=row['new_input'] or 0,
            cache_read_tokens=row['cache_read'] or 0,
            output_tokens=row['output'] or 0,
            utilization_pct=round(utilization, 1),
            band=band,
            band_description=description,
            recommended_action=self._recommend_action(band),
            tokens_to_redzone=max(0, redzone_threshold - working_set),
            tokens_to_compaction=max(0, compaction_threshold - working_set),
        )
    
    def _calculate_band(self, tokens: int) -> tuple:
        for threshold, band, desc in BANDS:
            if tokens < threshold:
                return band, desc
        return "BLACK", "STOP — hand off now"
    
    def _recommend_action(self, band: str) -> str:
        actions = {
            "GREEN": "CONTINUE",
            "YELLOW": "PREFER_DELEGATE",
            "ORANGE": "SPLIT_BEFORE_READING",
            "RED": "HANDOFF_IMMINENT",
            "BLACK": "STOP_AND_HANDOFF",
        }
        return actions.get(band, "UNKNOWN")
```

#### Step 2: Integrate with ModelGateway

```python
# src/omega/oracle/model_gateway.py

from omega.oracle.context_gauge import ContextGauge

class ModelGateway:
    def __init__(self, ...):
        # ... existing init ...
        self._context_gauge = ContextGauge()
    
    async def get_context_pressure(self, session_id: str) -> Optional[dict]:
        """Get context pressure for a session."""
        result = self._context_gauge.get_context_pressure(session_id)
        if not result:
            return None
        return {
            "session_id": result.session_id,
            "model_id": result.model_id,
            "context_window": result.context_window,
            "working_set_tokens": result.working_set_tokens,
            "utilization_pct": result.utilization_pct,
            "band": result.band,
            "band_description": result.band_description,
            "recommended_action": result.recommended_action,
            "tokens_to_redzone": result.tokens_to_redzone,
            "tokens_to_compaction": result.tokens_to_compaction,
        }
```

#### Step 3: Add MCP tool (QW-10 dependency)

```python
# In omega_hub server (future QW-10):

@mcp_tool("get_context_pressure")
async def get_context_pressure(session_id: str) -> dict:
    """Get context pressure for an OpenCode session."""
    gateway = get_model_gateway()
    return await gateway.get_context_pressure(session_id)
```

### Files to Create
- `src/omega/oracle/context_gauge.py` — ContextGauge class
- `tests/contract/test_context_gauge.py` — Test suite

### Files to Modify
- `src/omega/oracle/model_gateway.py` — integrate ContextGauge

### Tests to Add
- Band calculation (GREEN/YELLOW/ORANGE/RED/BLACK)
- Model window resolution
- Token extraction from opencode.db
- Threshold calculation (80% redzone, 85% compaction)
- Integration with ModelGateway

### Estimated Effort: 4 hours

---

## 📊 Combined Effort Estimate

| Task | Effort | Files | Tests |
|------|--------|-------|-------|
| QW-4 Step 1: Init pool_tracker | 30 min | model_gateway.py | — |
| QW-4 Step 2: Key selection | 30 min | model_gateway.py | — |
| QW-4 Step 3: Usage tracking | 30 min | model_gateway.py | — |
| QW-4 Step 4: Health endpoint | 30 min | model_gateway.py | — |
| QW-4 Tests | 30 min | test_pool_tracker_integration.py | 4 tests |
| QW-8 Step 1: ContextGauge class | 60 min | context_gauge.py | — |
| QW-8 Step 2: ModelGateway integration | 30 min | model_gateway.py | — |
| QW-8 Step 3: MCP tool (QW-10) | 30 min | omega_hub server | — |
| QW-8 Tests | 60 min | test_context_gauge.py | 6 tests |
| **Total** | **~5.5 hours** | **3 new files, 2 modified** | **10 tests** |

---

## 🔗 References

| Document | Path |
|----------|------|
| Gap-filling report | `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md` |
| opencode.db schema reference | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` |
| SDP Model-Aware Gauge Spec | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` |
| SDP Final Synthesis | `docs/strategy/SDP_FINAL_SYNTHESIS.md` |
| pool_tracker.py | `src/omega/oracle/pool_tracker.py` |
| pool_state.py | `src/omega/oracle/pool_state.py` |
| remote_provider.py | `src/omega/oracle/backends/remote_provider.py` |

---

*⬡ OMEGA ⬡ IMPLEMENTATION ⬡ QW4 ⬡ QW8 ⬡ PLAN ⬡ 2026-08-10*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: QW4 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
