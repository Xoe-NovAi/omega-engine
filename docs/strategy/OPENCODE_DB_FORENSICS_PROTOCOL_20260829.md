---
schema_version: "2.0"
document_type: "canonical_protocol"
document_id: "OPENCODE_DB_FORENSICS_PROTOCOL_V1_20260829"
title: "🔍 OpenCode DB Forensics Protocol — Omega Engine"
status: "ACTIVE"
date: "2026-08-29"
authors: ["Kali (Sprint Coordinator)", "All entities contribute"]
version: "1.0.0"
---

# 🔍 OpenCode DB Forensics Protocol — Omega Engine
**AP Token**: `AP-OPENCODE-DB-FORENSICS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_forensics ⬡ ACTIVE

**Date**: 2026-08-29
**Context**: Every agent should be able to do forensics on its own thought stream via the opencode.db. This is a LIVING document — all agents contribute discoveries.

---

## §0 — WHY THIS PROTOCOL EXISTS

The opencode.db (`~/.local/share/opencode/opencode.db`) is the **sovereign record** of every agent's thought stream, tool calls, and decisions. It is the single most valuable forensic asset in the Omega Engine.

**Yet most agents never query it.** They treat the conversation as ephemeral. They don't realize they can reconstruct their own decision-making process from the db.

**This protocol teaches every agent how to do forensics on itself.**

---

## §1 — THE DB SCHEMA (Authoritative Reference)

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `session` | Session metadata | `id`, `title`, `agent`, `model`, `time_created`, `time_updated`, `parent_id` |
| `message` | Conversation messages | `id`, `session_id`, `role`, `time_created`, `data` (JSON) |
| `part` | Message parts (text/tool/reasoning) | `id`, `message_id`, `session_id`, `time_created`, `data` (JSON) |

### Critical Schema Notes

- **`part.data` is JSON**, not a flat string. Text content is in `part.data.text`
- **`message.data` is JSON** with `parts` array
- **`session.model` is JSON** with `id`, `providerID`, `variant`
- **No `type` column on `part`** — type is in `part.data.type` (e.g., `"text"`, `"tool"`, `"reasoning"`)
- **`session.time_created` is milliseconds** since epoch (Unix epoch × 1000)

### Common Gotchas

1. **Empty text fields**: Many `part.data.text` fields are empty strings. Check `part.data` for the actual content.
2. **Tool parts**: `part.data.tool`, `part.data.state.input`, `part.data.state.output`, `part.data.state.error`
3. **Truncated outputs**: Long outputs are truncated. Look for `part.data.metadata.truncated: true`
4. **Externalized outputs**: Very long outputs go to `~/.local/share/opencode/tool-output/` (path in `part.data.state.metadata.outputPath`)

---

## §2 — THE 7 CORE FORENSIC QUERIES

### Query 1: List Recent Sessions
```sql
SELECT id, title, agent, time_created, time_updated
FROM session
ORDER BY time_updated DESC
LIMIT 20;
```
**Use**: "What sessions have I had recently?"

### Query 2: Find Sessions by Agent
```sql
SELECT id, title, time_created, time_updated
FROM session
WHERE agent = 'kali'
ORDER BY time_created DESC
LIMIT 10;
```
**Use**: "What has Kali been working on?"

### Query 3: Find Sessions in Time Range
```sql
SELECT id, title, time_created
FROM session
WHERE time_created > 1787900000000  -- milliseconds since epoch
  AND time_created < 1788000000000
ORDER BY time_created;
```
**Use**: "What happened on Aug 28-29?"

### Query 4: Extract Part Text (THE most important query)
```python
import sqlite3, json
conn = sqlite3.connect('file:///home/arcana-novai/.local/share/opencode/opencode.db?mode=ro', uri=True)
cursor = conn.cursor()
cursor.execute('SELECT p.id, p.data FROM part p WHERE p.data LIKE "%search_term%"')
for pid, data in cursor.fetchall():
    d = json.loads(data)
    if 'text' in d and d['text']:
        print(d['text'][:500])
```
**Use**: "Find all parts that mention X"

### Query 5: Find Tool Calls in a Session
```python
cursor.execute('SELECT p.data FROM part p WHERE p.session_id = ? AND p.data LIKE "%tool%"', (session_id,))
for data in cursor.fetchall():
    d = json.loads(data[0])
    if d.get('type') == 'tool':
        print(f"Tool: {d.get('tool')}")
        print(f"Input: {d.get('state', {}).get('input', {})}")
        print(f"Output: {d.get('state', {}).get('output', '')[:200]}")
```
**Use**: "What tools did this session use?"

### Query 6: Find Reasoning Steps
```python
cursor.execute('SELECT p.data FROM part p WHERE p.data LIKE "%reasoning%"')
for data in cursor.fetchall():
    d = json.loads(data[0])
    if d.get('type') == 'reasoning':
        print(d.get('text', '')[:500])
```
**Use**: "What was I thinking when I made this decision?"

### Query 7: Reconstruct Decision Timeline
```python
cursor.execute('''
    SELECT p.time_created, p.data
    FROM part p
    WHERE p.session_id = ?
    ORDER BY p.time_created
''', (session_id,))
events = []
for ts, data in cursor.fetchall():
    d = json.loads(data)
    if d.get('type') == 'text':
        events.append((ts, 'TEXT', d.get('text', '')[:200]))
    elif d.get('type') == 'tool':
        events.append((ts, 'TOOL', f"{d.get('tool')}: {str(d.get('state', {}).get('input', {}))[:100]}"))
for ts, kind, content in events:
    print(f"{ts} [{kind}] {content}")
```
**Use**: "Walk me through this session chronologically"

---

## §3 — PYTHON FORENSICS PATTERNS

### Pattern 1: Read-Only DB Connection (CRITICAL)
```python
# ALWAYS use mode=ro and uri=True to prevent accidental writes
conn = sqlite3.connect('file:///home/arcana-novai/.local/share/opencode/opencode.db?mode=ro', uri=True)
```
**Why**: The db is shared with the running OpenCode process. Accidental writes will corrupt it.

### Pattern 2: JSON Parsing with Error Handling
```python
try:
    d = json.loads(data)
    if 'text' in d:
        print(d['text'])
except json.JSONDecodeError:
    pass  # Some parts have non-JSON data
except Exception as e:
    print(f"Error: {e}")
```
**Why**: Not all `part.data` is valid JSON. Always handle errors.

### Pattern 3: Safe Text Extraction
```python
def extract_text(part_data):
    """Safely extract text from any part type."""
    d = json.loads(part_data) if isinstance(part_data, str) else part_data
    if isinstance(d, dict):
        return d.get('text', '') or ''
    return ''
```
**Why**: Defensive coding prevents crashes on malformed data.

### Pattern 4: Time Conversion
```python
from datetime import datetime
ts_ms = 1787260912049
dt = datetime.fromtimestamp(ts_ms / 1000)
# Result: 2026-08-20 12:21:52
```
**Why**: Timestamps are in milliseconds, not seconds.

---

## §4 — ADVANCED FORENSICS

### Advanced 1: Find When a File Was Created
```python
# Search for tool calls that created a file
cursor.execute('SELECT p.time_created, p.data FROM part p WHERE p.data LIKE "%projection.md%" AND p.data LIKE "%cat%"')
for ts, data in cursor.fetchall():
    d = json.loads(data)
    if d.get('tool') == 'bash' and 'projection.md' in str(d.get('state', {}).get('input', {})):
        print(f"Created at: {datetime.fromtimestamp(ts/1000)}")
```

### Advanced 2: Trace Decision Through Multiple Messages
```python
# Find a decision and trace its execution
search_term = "I'll create projection.md"
cursor.execute('SELECT m.id, m.time_created, p.data FROM message m JOIN part p ON p.message_id = m.id WHERE p.data LIKE ?', (f'%{search_term}%',))
```

### Advanced 3: Find Sessions That Used a Specific Tool
```python
cursor.execute('SELECT DISTINCT session_id FROM part WHERE data LIKE "%llama_cpp.server%"')
```

### Advanced 4: Measure Session Duration
```python
cursor.execute('SELECT (time_updated - time_created) / 1000.0 as duration_sec, title FROM session WHERE agent = "kali" ORDER BY time_created DESC LIMIT 10')
```

### Advanced 5: Find Errors
```python
cursor.execute('SELECT p.data FROM part p WHERE p.data LIKE "%error%" AND p.data LIKE "%status%error%"')
for data in cursor.fetchall():
    d = json.loads(data[0])
    if d.get('state', {}).get('status') == 'error':
        print(d.get('state', {}).get('error', ''))
```

---

## §5 — PERFORMANCE & SAFETY

### Performance
- **Always use `mode=ro`** — prevents accidental writes
- **Index on session_id** — most queries filter by session
- **Limit results** — the db can have millions of parts
- **Use LIKE with care** — full table scans are slow

### Safety Rules
1. **NEVER write to the db** — it's owned by the running OpenCode process
2. **NEVER delete from the db** — use VACUUM with extreme caution (needs 2× disk space)
3. **ALWAYS handle JSON parse errors** — not all data is valid JSON
4. **ALWAYS limit query results** — prevent OOM
5. **ALWAYS backup before destructive operations** — `cp opencode.db opencode.db.backup`

---

## §6 — COMMON USE CASES

### Use Case 1: "When did I create X?"
```python
# Search for creation events
cursor.execute('SELECT p.time_created, p.data FROM part p WHERE p.data LIKE "%cat > %X%"')
```

### Use Case 2: "What was I thinking when I made decision Y?"
```python
# Find the reasoning parts near a decision
cursor.execute('''
    SELECT p.time_created, p.data
    FROM part p
    WHERE p.data LIKE "%decision Y%"
    ORDER BY p.time_created
''')
# Then read the reasoning parts immediately before
```

### Use Case 3: "How long did session X take?"
```python
cursor.execute('SELECT (time_updated - time_created) / 1000.0 FROM session WHERE id = ?', (session_id,))
```

### Use Case 4: "What tools did I use in my last session?"
```python
cursor.execute('''
    SELECT DISTINCT json_extract(p.data, '$.tool')
    FROM part p
    WHERE p.session_id = (
        SELECT id FROM session ORDER BY time_updated DESC LIMIT 1
    )
''')
```

### Use Case 5: "Reconstruct my thought process for a specific decision"
```python
# Find all parts within 5 minutes of a decision
decision_ts = 1787260912049  # example
window = 5 * 60 * 1000  # 5 minutes in ms
cursor.execute('''
    SELECT p.time_created, json_extract(p.data, '$.type'), p.data
    FROM part p
    WHERE p.time_created BETWEEN ? AND ?
    ORDER BY p.time_created
''', (decision_ts - window, decision_ts + window))
```

---

## §7 — DISCOVERIES LOG (Add Yours!)

### Discovery 1: The part.data JSON structure
**Discovered by**: Kali, 2026-08-29
**Context**: Trying to extract text from parts
**Finding**: `part.data` is JSON, text is in `part.data.text` (not a top-level column)
**Impact**: All text extraction queries need to parse JSON

### Discovery 2: Time is in milliseconds
**Discovered by**: Kali, 2026-08-29
**Context**: Converting session timestamps
**Finding**: `time_created` and `time_updated` are in milliseconds, not seconds
**Impact**: Must divide by 1000 for datetime conversion

### Discovery 3: Tool parts have nested state
**Discovered by**: Kali, 2026-08-29
**Context**: Extracting tool call details
**Finding**: `part.data.state.input`, `part.data.state.output`, `part.data.state.error`
**Impact**: Tool forensics requires `json_extract(p.data, '$.state.input')`

### [YOUR_DISCOVERY_HERE]
**Discovered by**: [Your entity], [date]
**Context**: [What were you trying to do?]
**Finding**: [What did you learn?]
**Impact**: [How does this help other agents?]

---

## §8 — SCRIPT TEMPLATES

### Template 1: Find When a File Was Created
```python
#!/usr/bin/env python3
"""find_file_creation.py — Find when a file was first created"""
import sqlite3, json, sys
from datetime import datetime

TARGET = sys.argv[1] if len(sys.argv) > 1 else "projection.md"

conn = sqlite3.connect('file:///home/arcana-novai/.local/share/opencode/opencode.db?mode=ro', uri=True)
cursor = conn.cursor()
cursor.execute('SELECT p.time_created, p.data FROM part p WHERE p.data LIKE ?', (f'%{TARGET}%',))
for ts, data in cursor.fetchall():
    d = json.loads(data)
    if d.get('tool') == 'bash' and TARGET in str(d.get('state', {}).get('input', {})):
        print(f"Created at: {datetime.fromtimestamp(ts/1000)}")
        break
conn.close()
```

### Template 2: Reconstruct Session Timeline
```python
#!/usr/bin/env python3
"""reconstruct_session.py — Walk through a session chronologically"""
import sqlite3, json, sys
from datetime import datetime

SESSION_ID = sys.argv[1] if len(sys.argv) > 1 else None

conn = sqlite3.connect('file:///home/arcana-novai/.local/share/opencode/opencode.db?mode=ro', uri=True)
cursor = conn.cursor()
cursor.execute('SELECT p.time_created, p.data FROM part p WHERE p.session_id = ? ORDER BY p.time_created', (SESSION_ID,))
for ts, data in cursor.fetchall():
    d = json.loads(data)
    ptype = d.get('type', 'unknown')
    if ptype == 'text':
        print(f"{datetime.fromtimestamp(ts/1000)} [TEXT] {d.get('text', '')[:200]}")
    elif ptype == 'tool':
        print(f"{datetime.fromtimestamp(ts/1000)} [TOOL] {d.get('tool')}")
    elif ptype == 'reasoning':
        print(f"{datetime.fromtimestamp(ts/1000)} [REASONING] {d.get('text', '')[:200]}")
conn.close()
```

---

## §9 — FORENSICS ANTI-PATTERNS

### Anti-Pattern 1: Writing to the db
❌ **NEVER** do `INSERT`, `UPDATE`, `DELETE` on the db.
✅ **ALWAYS** use `mode=ro` in the connection string.

### Anti-Pattern 2: Unbounded queries
❌ **NEVER** `SELECT * FROM part` without `LIMIT`.
✅ **ALWAYS** add `LIMIT N` to prevent OOM.

### Anti-Pattern 3: Assuming flat strings
❌ **NEVER** assume `part.data` is a string.
✅ **ALWAYS** `json.loads()` before accessing fields.

### Anti-Pattern 4: Ignoring errors
❌ **NEVER** let JSON parse errors crash your script.
✅ **ALWAYS** wrap in try/except.

---

## §10 — RELATED PROTOCOLS

| Protocol | Purpose |
|----------|---------|
| `SOVEREIGN_CONTINUITY_STRATEGY.md` | M15 continuity (4 tiers) |
| `EMERGENT_TECHNOLOGY_PROTOCOL_20260829.md` | Track innovations |
| `COMPACTION_WATCHER_PROTOCOL.md` | Auto-archive /compact summaries |
| `OPENCODE_DB_FORENSICS_PROTOCOL.md` | This document |

---

## §11 — HOW TO CONTRIBUTE

Found a better query? A new pattern? A gotcha?

1. **Add to §7 Discoveries Log** with your entity name, date, context, finding, impact
2. **Add new §8 script template** if you have a reusable script
3. **Add new §6 use case** if you solved a common problem
4. **Commit** with message: `docs(forensics): [Your discovery]`

---

*⬡ OMEGA ⬡ KALI ⬡ OPENCODE-DB-FORENSICS-v1.0.0 ⬡ 2026-08-29*
*The db is the sovereign record. Every agent can read it. Every agent can learn from it.*
