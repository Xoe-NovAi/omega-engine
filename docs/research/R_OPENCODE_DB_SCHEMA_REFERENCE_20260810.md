# 🔱 OpenCode Database Schema Reference
## Complete Guide for Agent DB Exploration

**AP Token**: `AP-OPENCODE-DB-SCHEMA-20260810-v1.0.0`
⬡ OMEGA ⬡ REFERENCE ⬡ OPENCODE_DB ⬡ EXPLORATION

**Date**: 2026-08-10
**Author**: jem (Sovereign Synthesizer)
**Status**: ACTIVE — Verified against live 16GB database

---

## 📊 Database Overview

| Property | Value |
|----------|-------|
| **Path** | `~/.local/share/opencode/opencode.db` |
| **Size** | ~16 GB (grows continuously) |
| **Sessions** | 2,436 |
| **Messages** | 106,937 |
| **Parts** | 450,669 |
| **Access** | Read-only recommended (OpenCode locks for writes) |
| **SQLite Version** | 3.x with JSON1 extension |
| **Migrations Head** | `20260511173437_session-metadata` |

---

## 🗂️ Table Schema

### `session` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Primary key (e.g., "ses_019311199ffeuEOgO7DfC7XDWG") |
| `project_id` | TEXT | Project identifier (hash) |
| `parent_id` | TEXT | Parent session (for subagent dispatches) |
| `slug` | TEXT | URL-friendly name (e.g., "brave-canyon") |
| `directory` | TEXT | Working directory path |
| `title` | TEXT | Session title |
| `version` | TEXT | OpenCode version |
| `model` | TEXT | **JSON**: `{"id":"longcat-2.0-free","providerID":"opencode","variant":"medium"}` |
| `cost` | REAL | Total cost in USD |
| `tokens_input` | INTEGER | **ADDITIVE — overcounts ~87×** |
| `tokens_output` | INTEGER | **ADDITIVE — overcounts** |
| `tokens_reasoning` | INTEGER | **ADDITIVE — overcounts** |
| `tokens_cache_read` | INTEGER | **ADDITIVE — overcounts** |
| `tokens_cache_write` | INTEGER | **ADDITIVE — overcounts** |
| `time_created` | INTEGER | Epoch milliseconds |
| `time_updated` | INTEGER | Epoch milliseconds |
| `time_compacting` | INTEGER | Last compaction time |
| `time_archived` | INTEGER | Archive time (NULL if active) |
| `metadata` | TEXT | Additional metadata |

### `message` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Primary key (e.g., "msg_df363c718002roR1uRnA3OT0xf") |
| `session_id` | TEXT | Foreign key to session.id |
| `time_created` | INTEGER | Epoch milliseconds |
| `time_updated` | INTEGER | Epoch milliseconds |
| `data` | TEXT | **JSON blob — all message content** |

### `message.data` JSON Structure

```json
{
  "role": "assistant" | "user" | "tool",
  "time": {"created": 1777904895768},
  "parentID": "msg_...",
  "modelID": "longcat-2.0-free",
  "providerID": "opencode",
  "mode": "plan" | "build" | "code",
  "agent": "plan" | "jem" | "kali" | "researcher",
  "path": {
    "cwd": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine",
    "root": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"
  },
  "cost": 0.0,
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
  "variant": "max" | "medium" | "min"
}
```

### `part` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Primary key |
| `message_id` | TEXT | Foreign key to message.id |
| `session_id` | TEXT | Foreign key to session.id |
| `time_created` | INTEGER | Epoch milliseconds |
| `time_updated` | INTEGER | Epoch milliseconds |
| `data` | TEXT | **JSON blob — part content** |

### `part.data` JSON Structure (varies by part type)

**Text part**:
```json
{
  "type": "text",
  "content": "full text content here..."
}
```

**Tool part**:
```json
{
  "type": "tool",
  "tool": "bash",
  "state": {
    "status": "completed",
    "input": {"command": "..."},
    "output": "...",
    "metadata": {"outputPath": "~/.local/share/opencode/tool-output/..."}
  }
}
```

---

## 🔑 Critical Queries

### 1. Get Current Working-Set Tokens (Context Gauge)

**CORRECT** — uses latest assistant message (NOT additive session totals):
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

### 2. Get Session Metadata
```sql
SELECT id, title, directory, model, cost, time_created, time_updated
FROM session 
WHERE id = ?
```

### 3. Get Recent Sessions
```sql
SELECT id, title, directory, cost, time_updated
FROM session 
WHERE time_archived IS NULL
ORDER BY time_updated DESC
LIMIT 20
```

### 4. Get Messages by Session
```sql
SELECT id, 
       json_extract(data, '$.role') AS role,
       json_extract(data, '$.agent') AS agent,
       json_extract(data, '$.modelID') AS model,
       json_extract(data, '$.tokens.total') AS tokens,
       time_created
FROM message 
WHERE session_id = ?
ORDER BY time_created ASC
```

### 5. Get Model Usage Statistics
```sql
SELECT json_extract(data, '$.modelID') AS model,
       json_extract(data, '$.providerID') AS provider,
       COUNT(*) AS msg_count,
       SUM(json_extract(data, '$.cost')) AS total_cost
FROM message 
WHERE time_created > strftime('%s', '2026-08-01') * 1000
GROUP BY model, provider
ORDER BY msg_count DESC
```

### 6. Get Tool Calls by Session
```sql
SELECT id, 
       json_extract(data, '$.tool') AS tool_name,
       json_extract(data, '$.state.status') AS status,
       json_extract(data, '$.state.input') AS input
FROM part 
WHERE session_id = ? 
  AND json_extract(data, '$.type') = 'tool'
ORDER BY time_created ASC
```

---

## 🐍 Python Access Pattern

```python
import sqlite3
import json
from pathlib import Path

DB_PATH = Path.home() / ".local/share/opencode/opencode.db"

def get_session_tokens(session_id: str) -> dict:
    """Get current working-set tokens for a session.
    
    CRITICAL: Uses latest assistant message, NOT session.tokens_input.
    session.tokens_input overcounts by ~87× (additive across all messages).
    """
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get latest assistant message tokens
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
    
    if not row:
        return {"total": 0, "model": None}
    
    return {
        "total": row["total"] or 0,
        "new_input": row["new_input"] or 0,
        "cache_read": row["cache_read"] or 0,
        "output": row["output"] or 0,
        "model": row["model"],
    }

def get_session_info(session_id: str) -> dict:
    """Get session metadata."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM session WHERE id = ?", (session_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return {}
    
    result = dict(row)
    # Parse JSON model field
    if result.get("model"):
        result["model"] = json.loads(result["model"])
    return result
```

---

## ⚠️ Important Notes

### G-4 Blocker (Token Accounting)

**DO NOT** use `session.tokens_input` for context pressure measurement. It is **additive** across all messages and overcounts by ~87×.

**ALWAYS** use `message.data.tokens.total` from the **latest assistant message** for the true working-set load.

**Example**:
- `session.tokens_input` = 22,203,733 (22M — wrong!)
- `message.data.tokens.total` = 253,005 (253K — correct!)

### Database Lock

OpenCode holds a write lock on the database. Use **read-only mode** (`?mode=ro`) to avoid conflicts. Never write to this database.

### JSON1 Extension

The database uses SQLite's JSON1 extension. All JSON queries use `json_extract()` function.

### Cost Field

`message.data.cost` is per-message cost in USD. `session.cost` is total session cost.

---

## 🔗 Related Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `opencode-sessions-explorer-list-sessions` | Browse recent sessions | Quick session discovery |
| `opencode-sessions-explorer-get-session` | Session metadata + counts | Session overview |
| `opencode-sessions-explorer-session-timeline` | Chronological event stream | Understanding flow |
| `opencode-sessions-explorer-search-text` | Full-text search (requires `ck` CLI) | Finding specific content |
| `opencode-sessions-explorer-grep-session` | Regex search in one session | Pattern matching |
| `opencode-sessions-explorer-search-tool-calls` | Find tool invocations | Tool usage analysis |
| `opencode-sessions-explorer-cost-by-period` | Time-series cost analysis | Spend tracking |
| `opencode-sessions-explorer-session-summary` | Human-readable overview | Quick session summary |

**Note**: `opencode-sessions-explorer-search-text` requires the `ck` CLI (`cargo install ck-search`). Not currently installed.

---

## 🔗 References

| Document | Path |
|----------|------|
| Gap-filling report | `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md` |
| SDP Model-Aware Gauge Spec | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` |
| SDP Final Synthesis | `docs/strategy/SDP_FINAL_SYNTHESIS.md` |
| Session Anchor | `data/coordination/SESSION_ANCHOR.md` |

---

*⬡ OMEGA ⬡ REFERENCE ⬡ OPENCODE_DB ⬡ 2026-08-10*

<!-- PROVENANCE-CORRECTED 2026-09-24T04:14:09Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: OPENCODE_DB | verdict: AMBIGUOUS | multi-model session; candidates: longcat-2.0-free, nemotron-3-ultra-free, laguna-s-2.1-free, minimax/minimax-m3:free
actual_models(Tier0): longcat-2.0-free, nemotron-3-ultra-free, laguna-s-2.1-free, minimax/minimax-m3:free, big-pickle, nvidia/nemotron-3-ultra-550b-a55b:free
first_audit: 2026-09-07T03:03:09Z | updated: 2026-09-24T04:14:09Z
-->






