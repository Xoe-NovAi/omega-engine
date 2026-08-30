# 🔱 Jem Gap-Filling Report — QW-4 & QW-8 Knowledge Acquisition
**AP Token**: `AP-JEM-GAP-FILLING-20260810-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_gap_filling ⬡ COMPLETE

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: ✅ COMPLETE — All gaps filled

---

## 🎯 Objective

Fill all knowledge gaps required for QW-4 (pool_tracker wiring) and QW-8 (Context Gauge greenfield) implementation. This report records findings for team reference.

---

## 📊 Gap-Filling Results

### QW-4: pool_tracker.py Wiring

| Gap | Status | Finding |
|-----|--------|---------|
| USAGE_POOL_LOG.json exists | ✅ FILLED | 8 keys (agy_key_01-08), all `active`, zero usage since 2026-06-18 |
| RemoteProvider key rotation | ✅ FILLED | Already rotates `_active_key_index` on 429s (reactive, lines 325-335 in remote_provider.py) |
| ProviderConfig.api_keys | ✅ FILLED | Field exists, `resolve_current_api_key()` returns key at index |
| AntigravityProvider inheritance | ✅ FILLED | Inherits `RemoteProvider.generate()` — same rotation logic |
| pool_tracker.py status | ✅ FILLED | Standalone, NOT imported anywhere — dead code |

**Design Decision**: QW-4 is NOT "add key rotation" (exists), it's **"replace reactive rotation with pool_tracker's proactive drain-aware selection."**

### QW-8: Context Gauge (Greenfield)

| Gap | Status | Finding |
|-----|--------|---------|
| Data source for live tokens | ✅ FILLED | `message.data.tokens.total` from latest assistant message |
| G-4 blocker verified | ✅ FILLED | `session.tokens_input` overcounts by **~87×** (22M vs 253K) |
| Token JSON structure | ✅ FILLED | `tokens.total`, `tokens.input`, `tokens.output`, `tokens.reasoning`, `tokens.cache.read`, `tokens.cache.write` |
| Model identification | ✅ FILLED | `message.data.modelID` (e.g., "longcat-2.0-free") |
| Active models (August 2026) | ✅ FILLED | deepseek-v4-flash-free, nemotron-3-ultra-free, laguna-s-2.1-free, longcat-2.0-free |
| BudgetGate relationship | ✅ FILLED | Complementary — BudgetGate controls **cost**, Context Gauge measures **context pressure** |
| Existing gauge code | ✅ FILLED | None in engine (only third-party headroom) |
| opencode.db accessibility | ✅ FILLED | Read-only via Python `sqlite3` (16GB, 2436 sessions, 106K messages) |
| Floor calibration data | ✅ FILLED | First assistant turn's `tokens.total` = floor (cached system prompt) |

---

## 🔑 Critical Findings

### 1. opencode.db Schema (Verified)

**message table**:
```
id: TEXT
session_id: TEXT
time_created: INTEGER
time_updated: INTEGER
data: TEXT (JSON blob)
```

**message.data JSON structure**:
```json
{
  "role": "assistant",
  "time": {"created": 1777904895768},
  "parentID": "msg_...",
  "modelID": "longcat-2.0-free",
  "providerID": "opencode",
  "mode": "plan",
  "agent": "plan",
  "path": {"cwd": "...", "root": "..."},
  "cost": 0,
  "tokens": {
    "total": 162636,
    "input": 1349,
    "output": 967,
    "reasoning": 0,
    "cache": {
      "read": 160320,
      "write": 0
    }
  },
  "variant": "max"
}
```

**session table** (relevant columns):
```
id: TEXT
title: TEXT
directory: TEXT
model: TEXT (JSON: {"id":"longcat-2.0-free","providerID":"opencode","variant":"medium"})
cost: REAL
tokens_input: INTEGER (ADDITIVE — overcounts ~87×)
tokens_output: INTEGER
tokens_reasoning: INTEGER
tokens_cache_read: INTEGER
tokens_cache_write: INTEGER
time_created: INTEGER
time_updated: INTEGER
```

### 2. G-4 Blocker Verified

**CRITICAL**: `session.tokens_input` (22,203,733) overcounts by **~87×** vs `message.data.tokens.total` (253,005) from latest assistant message.

**Correct query for working-set tokens**:
```sql
SELECT json_extract(data, '$.tokens.total') AS working_set_tokens,
       json_extract(data, '$.modelID') AS model_id
FROM message 
WHERE session_id = ? 
  AND json_extract(data, '$.role') = 'assistant'
ORDER BY time_created DESC 
LIMIT 1
```

**Python implementation**:
```python
import sqlite3
conn = sqlite3.connect('file:///home/arcana-novai/.local/share/opencode/opencode.db?mode=ro', uri=True)
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

### 3. Active Models (August 2026)

| Model | Provider | Context Window | Tier |
|-------|----------|---------------|------|
| deepseek-v4-flash-free | opencode | 1,000,000 (assumed) | 4 |
| nemotron-3-ultra-free | opencode | 1,000,000 | 4 |
| laguna-s-2.1-free | opencode | 262,144 | 3 |
| longcat-2.0-free | opencode | 1,000,000 | 4 |

### 4. BudgetGate vs Context Gauge

| System | Purpose | Data Source |
|--------|---------|-------------|
| **BudgetGate** | Control cloud cost | `config.budget.daily_cloud_tokens` (cvar) |
| **Context Gauge** | Measure context pressure | `message.data.tokens.total` (opencode.db) |

They are **complementary** — BudgetGate blocks when cost exhausted, Context Gauge warns when context degraded.

### 5. pool_tracker.py Status

- **Location**: `src/omega/oracle/pool_tracker.py` (630 lines)
- **Class**: `UsagePoolTracker`
- **Dependencies**: `pool_state.py` (PoolState, PoolConfig, etc.)
- **Features**: Key rotation, usage tracking, pool health, atomic JSON writes
- **Current state**: Standalone, NOT imported anywhere — dead code
- **D-1 notice**: Anti-thrashing algorithm removed; default is "sticky"

### 6. RemoteProvider Key Rotation (Existing)

```python
# remote_provider.py:325-335
if is_rate_limit and len(self.config.api_keys) > 1:
    self._active_key_index = (self._active_key_index + 1) % len(self.config.api_keys)
    logger.info(f"Provider {self.name} rate limited. Rotating to key index {self._active_key_index}")
```

This is **reactive** (only on 429). QW-4 should add **proactive** drain-aware selection from pool_tracker.

---

## 📋 Implementation Design (Ready)

### QW-4: Wire pool_tracker into ModelGateway.generate()

1. **Before provider call**: `await pool_tracker.select_key(pool_name, model)` → set `provider._active_key_index`
2. **After successful inference**: `await pool_tracker.track_usage(pool, model, key_id, tokens, success)`
3. **Initialize pool_tracker** in `ModelGateway.__init__()` if `USAGE_POOL_LOG.json` exists

### QW-8: Build ContextGauge class

1. Query `message.data.tokens.total` from latest assistant message (read-only SQLite)
2. Resolve model window from `config/models.yaml` or SDP ground truth
3. Calculate absolute working-set tokens (not %)
4. Apply color bands: GREEN <40K, YELLOW 40-90K, ORANGE 90-150K, RED 150-250K, BLACK ≥250K
5. Expose via `ContextGauge.get_context_pressure(session_id)` → JSON

---

## 🔗 References

| Document | Path | Purpose |
|----------|------|---------|
| Local gap research | `data/coordination/JEM_RESEARCH_KNOWLEDGE_GAPS_20260810.md` | Initial gap identification |
| Web gap research | `data/coordination/JEM_WEB_RESEARCH_GAPS_20260810.md` | Web research findings |
| SDP Final Synthesis | `docs/strategy/SDP_FINAL_SYNTHESIS.md` | Master SDP architecture |
| Model-Aware Gauge Spec | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` | Gauge specification |
| opencode.db schema | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` | DB schema reference |
| Session Anchor | `data/coordination/SESSION_ANCHOR.md` | Current session state |

---

## 🎯 Next Steps

1. **QW-4**: Implement pool_tracker wiring in ModelGateway.generate()
2. **QW-8**: Build ContextGauge greenfield per SDP spec
3. **Update SDP_FINAL_SYNTHESIS.md** with verified G-4 data
4. **Update SDP_MODEL_AWARE_GAUGE_SPEC.md** with correct query
5. **Update AGENTS.md** with opencode.db access patterns

---

*⬡ OMEGA ⬡ JEM ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_gap_filling ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
