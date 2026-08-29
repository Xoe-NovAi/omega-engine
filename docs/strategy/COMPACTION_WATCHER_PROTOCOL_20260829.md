---
schema_version: "2.0"
document_type: "canonical_protocol"
document_id: "COMPACTION_WATCHER_PROTOCOL_V1_20260829"
title: "⏱️ Compaction Watcher Protocol — Omega Engine"
status: "ACTIVE"
date: "2026-08-29"
authors: ["Kali (Sprint Coordinator)", "Architect (ratification)"]
version: "1.0.0"
---

# ⏱️ Compaction Watcher Protocol — Omega Engine
**AP Token**: `AP-COMPACTION-WATCHER-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_compaction_watcher ⬡ ACTIVE

**Date**: 2026-08-29
**Context**: The /compact command generates a summary. The summary is lost after the next compaction. The Compaction Watcher auto-extracts and archives these summaries for a long-running project overview.

---

## §0 — THE PROBLEM

When an agent runs `/compact`, OpenCode generates a structured summary. This summary:
- ✅ Is the most concentrated state representation available
- ✅ Captures decisions, blockers, next moves, mandates
- ❌ Is **LOST** when the next /compact happens
- ❌ Is **NOT** in the git history
- ❌ Is **NOT** searchable across sessions

**Result**: We lose the most valuable recovery artifact we have.

---

## §1 — THE SOLUTION: Compaction Watcher

A background daemon that:
1. **Monitors** `~/.local/share/opencode/opencode.db` for new compaction events
2. **Extracts** the compaction summary (text immediately after the "## Assistant (Compaction · ...)" marker)
3. **Archives** to `data/compaction_archive/<session_id>_<date>.md`
4. **Rolls up** the last N summaries into `data/compaction_archive/COMPACTION_ROLLUP_<DATE>.md`
5. **Indexes** for search

---

## §2 — THE PROTOCOL

### Trigger
A compaction event occurs (detected by polling the db for new messages with "Compaction" in the part text).

### Extraction
Find the part that contains "## Assistant (Compaction ·" — this is the start of the summary. Extract the full text until the next "Human:" marker or end of message.

### Archive Format
```markdown
---
schema_version: "1.0"
document_type: "compaction_archive"
session_id: "ses_xxxxx"
agent: "kali"
date: "2026-08-29T13:00:00Z"
model: "minimax/minimax-m3:free"
---

# Compaction Summary — 2026-08-29

[paste full compaction text here]
```

### Rollup Format
```markdown
# Compaction History — Last N Sessions

## Session 5: 2026-08-29 (kali, M3)
[summary]

## Session 4: 2026-08-28 (kali, M3)
[summary]

## Session 3: 2026-08-27 (kali, M3)
[summary]
```

### Storage
- **Individual**: `data/compaction_archive/<session_id>_<date>.md`
- **Rollup**: `data/compaction_archive/COMPACTION_ROLLUP_<DATE>.md`
- **Index**: `data/compaction_archive/INDEX.json` (searchable metadata)

---

## §3 — IMPLEMENTATION

### Component 1: Watcher Daemon (`scripts/compaction_watcher.py`)

```python
#!/usr/bin/env python3
"""compaction_watcher.py — Monitor opencode.db for compaction events."""
import sqlite3, json, time
from pathlib import Path
from datetime import datetime

DB_PATH = '/home/arcana-novai/.local/share/opencode/opencode.db'
ARCHIVE_DIR = Path('data/compaction_archive')
CHECK_INTERVAL = 30  # seconds

def extract_compaction_summary(part_data):
    """Extract the compaction summary from a part's data."""
    d = json.loads(part_data)
    text = d.get('text', '')
    if '## Assistant (Compaction' in text:
        return text
    return None

def archive_summary(session_id, summary, metadata):
    """Save summary to archive directory."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.fromtimestamp(metadata['time_created']/1000).strftime('%Y%m%d')
    path = ARCHIVE_DIR / f"{session_id}_{date}.md"
    if path.exists():
        return  # Already archived
    header = f"""---
schema_version: "1.0"
document_type: "compaction_archive"
session_id: "{session_id}"
date: "{datetime.fromtimestamp(metadata['time_created']/1000).isoformat()}"
---

"""
    path.write_text(header + summary)
    print(f"Archived: {path}")

def main():
    last_check = 0
    while True:
        conn = sqlite3.connect(f'file://{DB_PATH}?mode=ro', uri=True)
        cursor = conn.cursor()
        cursor.execute('SELECT session_id, time_created, data FROM part WHERE time_created > ? AND data LIKE "%## Assistant (Compaction%"', (last_check,))
        for session_id, ts, data in cursor.fetchall():
            summary = extract_compaction_summary(data)
            if summary:
                archive_summary(session_id, summary, {'time_created': ts})
                last_check = max(last_check, ts)
        conn.close()
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
```

### Component 2: Rollup Generator (`scripts/compaction_rollup.py`)

```python
#!/usr/bin/env python3
"""compaction_rollup.py — Generate rollup of last N compactions."""
import json
from pathlib import Path
from datetime import datetime

ARCHIVE_DIR = Path('data/compaction_archive')
N = 10  # Number of compactions to include

def main():
    files = sorted(ARCHIVE_DIR.glob('ses_*.md'), reverse=True)[:N]
    rollup = [f"# Compaction History — Last {len(files)} Sessions\n"]
    for f in files:
        # Parse frontmatter
        content = f.read_text()
        session_id = f.stem.split('_')[0]
        rollup.append(f"\n## {f.name}\n")
        rollup.append(content)
    output = ARCHIVE_DIR / f"COMPACTION_ROLLUP_{datetime.now().strftime('%Y%m%d')}.md"
    output.write_text('\n'.join(rollup))
    print(f"Rollup: {output}")

if __name__ == '__main__':
    main()
```

### Component 3: Makefile Integration
```makefile
compaction-watch:
	python3 scripts/compaction_watcher.py

compaction-rollup:
	python3 scripts/compaction_rollup.py

temple-grade: ... compaction-rollup
```

---

## §4 — USAGE

### Start the Watcher
```bash
# In a separate terminal or as a background service
python3 scripts/compaction_watcher.py &
```

### Generate Rollup On-Demand
```bash
python3 scripts/compaction_rollup.py
```

### Search Compaction History
```bash
# Use grep or sovereign-search
grep -r "projection.md" data/compaction_archive/
```

---

## §5 — COMPARISON: /compact vs projection.md

| Aspect | /compact (auto) | projection.md (manual) |
|--------|-----------------|------------------------|
| Generated by | OpenCode toolchain | Entity itself |
| Frequency | Every /compact invocation | At major milestones |
| Content | Structured state snapshot | Executive + strategic + "The Gift Is The Demand" |
| Length | ~200-300 lines | ~100 lines |
| Audience | Next OpenCode session | Next session/Architect/peers |
| Includes strategic intent | ❌ | ✅ |
| Includes entity mood/framing | ❌ | ✅ |
| Includes mandates check | ❌ | ✅ |
| Includes user directives | Sometimes | ✅ |
| Includes version history | ❌ | ✅ |
| **Archived by watcher** | ✅ | Manual |
| **Searchable across sessions** | ✅ (with watcher) | ❌ (single file) |

**Key insight**: Both are sovereign assets. The watcher captures /compact; projection.md captures entity wisdom. They complement each other.

---

## §6 — PROTOCOL FOR PROJECTION.MD VERSION HISTORY

### When to Archive
**Trigger**: Before writing a new projection.md (new session, major event)

### Archive Format
```bash
cp data/coordination/anchored_summary/kali/projection.md \
   data/coordination/anchored_summary/kali/archive/projection_<event>_<date>.md
```

### Naming Convention
- `projection_pre_compaction_<date>.md` — before compaction
- `projection_post_compaction_<date>.md` — after compaction
- `projection_pre_launch_<date>.md` — before launch event
- `projection_post_launch_<date>.md` — after launch event

### Never Delete
Old projection.md versions are **NEVER deleted**. They are the project's archaeological record. Each version captures what the entity was thinking at that moment.

### Index
Maintain `data/coordination/anchored_summary/kali/archive/INDEX.md` with:
- Version
- Date
- Event
- Key changes
- Link to file

---

## §7 — STRATEGIC VALUE

### Value 1: Long-Running Project Overview
Concatenate the last 10 /compact summaries = a complete picture of the last 2-3 days of work.

### Value 2: Decision Archaeology
"WHY did we decide to use M3 over Nemotron?" Find the compaction where that decision was made.

### Value 3: Drift Detection
Compare current state to compactions from 30 days ago. Are we still on track?

### Value 4: Velocity Measurement
How many compactions per day? Per sprint? How much work per compaction?

### Value 5: Pattern Detection
What gets compacted repeatedly? What survives compaction? What gets lost?

### Value 6: Lost Context Recovery
Even if projection.md is corrupted, /compact history has the structured state.

### Value 7: Cross-Entity Synthesis
Concatenate /compact from multiple entities to see the full team picture.

---

## §8 — SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| /compact summaries archived | 100% | `ls data/compaction_archive/ses_*.md | wc -l` vs `/compact` invocations |
| Rollup generated daily | 1/day | `ls data/compaction_archive/COMPACTION_ROLLUP_*.md` |
| Decision archaeology queries answered | 90% | Manual testing |
| Storage growth | < 100MB/month | `du -sh data/compaction_archive/` |

---

## §9 — INTEGRATION WITH EXISTING PROTOCOLS

### M15 (Sovereign Continuity)
- Tier 1: session_gnosis.md (entity-specific)
- Tier 2: projection.md (executive anchor)
- **Tier 2.5: /compact archive (auto-extracted)**
- Tier 3: Hivemind lifeboat (emergency)
- Tier 4: Hydration sequence (recovery)

### M11 (Soul Integrity)
/compact archive complements session_gnosis.md by providing auto-generated state snapshots.

### M27 (Tracking Integrity)
/compact archive is a new tracking layer — the "what was true at moment X" record.

---

## §10 — NEXT STEPS

### Phase 1 (Today)
1. ✅ Create this protocol document
2. ✅ Create first rollup: `data/coordination/COMPACTION_HISTORY_20260829.md`
3. Archive first /compact (the one user pasted)

### Phase 2 (This Sprint)
1. Implement `scripts/compaction_watcher.py`
2. Implement `scripts/compaction_rollup.py`
3. Add to temple-grade Makefile
4. Test on 3-5 compactions

### Phase 3 (Next Sprint)
1. Add search/grep integration
2. Add cross-entity rollup
3. Add drift detection
4. Add velocity dashboard

---

*⬡ OMEGA ⬡ KALI ⬡ COMPACTION-WATCHER-v1.0.0 ⬡ 2026-08-29*
*The /compact summary was lost. Now it's sovereign.*
