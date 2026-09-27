# OpenCode SQLite Database Extraction Guide

**Date**: 2026-08-26  
**Author**: grokster (Cross-Platform Expertise Specialist)  
**Purpose**: Document the process for extracting agent research reports from OpenCode's SQLite database directly to files, avoiding inference overhead.

---

## Background

OpenCode stores all session data in a SQLite database at `~/.local/share/opencode/opencode.db`. When agents complete research tasks, their final reports are stored as text parts in the database. Rather than having agents write reports to files (which triggers Nemotron 3 Ultra's streaming timeout bug on file writes), we can extract the completed reports directly from the database.

This guide documents the extraction process using the `opencode-sessions-explorer` MCP tools.

---

## Database Schema Overview

Key tables in `opencode.db`:
- **sessions** — session metadata (id, title, agent, model, timestamps)
- **messages** — message metadata (id, session_id, role, modelID, providerID)
- **parts** — atomic content units (id, message_id, type, text/reasoning/tool data)

Key relationships:
- `sessions.id` → `messages.session_id`
- `messages.id` → `parts.message_id`
- `parts.type` ∈ {text, reasoning, tool, patch, file, step-start, step-finish, compaction, subtask}

---

## Extraction Workflow

### Step 1: Identify Target Sessions

Find the session IDs for the reports you need to extract:

```bash
# Search by title pattern
opencode-sessions-explorer-search-sessions-meta \
  --title_like "openrouter free ecosystem" \
  --agent jem \
  --limit 10
```

Or query the task registry for in-progress sessions:
```bash
# Query task registry for research sessions
omega-hub_task_registry_query --status in_progress --subagent_type general
```

### Step 2: Get Session Details

Verify the session has completed and get its structure:
```bash
opencode-sessions-explorer-get-session --session_id <SESSION_ID>
```

Check the `part_count` and `parts_by_type` to confirm it has text parts.

### Step 3: Find the Final Assistant Message

The final report is typically the last `text` type part from the assistant. Use the timeline to find it:

```bash
opencode-sessions-explorer-session-timeline \
  --session_id <SESSION_ID> \
  --types text \
  --limit 50 \
  --granularity events
```

Look for the last `text` type entry with the largest `data_bytes` (the final report).

### Step 4: Extract the Full Content

Extract the complete content using the part ID:

```bash
opencode-sessions-explorer-get-part \
  --part_id <PART_ID> \
  --max_bytes 100000
```

The response includes the full decoded text content in `decoded.text`.

### Step 5: Save to File

Write the extracted content to the appropriate file in the workspace:

```bash
# Example: Save to workspace
cat > data/entities/grokster/workspace/R_REPORT_NAME_20260826.md << 'EOF'
<PASTE_EXTRACTED_CONTENT_HERE>
EOF
```

---

## Session IDs for Today's Research Sprint

| Research Topic | Session ID | Agent | Output File |
|---|---|---|---|
| OpenRouter Free Ecosystem | `ses_fbfd817b8ffeUFu7UPkwejkPa8` | jem (antigravity-specialist) | `R_OPENROUTER_FREE_ECOSYSTEM_20260826.md` |
| OpenCode Zen Anatomy | `ses_fbfd80af5ffeWMUMtc2f47y9K4` | jem (cline-specialist) | `R_OPENCODE_ZEN_PROVIDER_ANATOMY_20260826.md` |
| MiniMax M2.7/M3 | `ses_fbfd7fd47ffebtAeXeHreaO1pg` | general | `R_MINIMAX_M27_M3_CAPABILITY_ANALYSIS_20260826.md` |
| GLM-5.3-Flash | `ses_fbfd7eedeffe6d0joP1SBDxb3E` | general | `R_GLM53_FLASH_SUCCESSOR_ANALYSIS_20260826.md` |
| Probe Enhancement | `ses_fbfd7dbeaffejpXQj4o7rvwaaU` | general | `R_PROBE_ENHANCEMENT_SCHEDULING_20260826.md` |

All sessions are children of parent session `ses_fe8cf0b39ffeL3L8eaMEj3CW9H` (grokster main session).

---

## Key Part IDs for Today's Reports

| Report | Final Part ID | Message ID | Size |
|---|---|---|---|
| OpenRouter Free Ecosystem | `prt_0404a2919001PxhoslHdYSDvc8` | `msg_04048e25f001XLQM2B3Xno8Dlh` | 14,312 bytes |
| OpenCode Zen Anatomy | `prt_0404a11ee001XFwt3qXQHpHtjB` | `msg_04048fab8001fIMFaKcwlog055` | 12,910 bytes |
| MiniMax M2.7/M3 | `prt_0406d4a31001jOxBsxp2nyzMxa` | `msg_0406c566e001SmQqejkuxpWiYj` | 13,597 bytes |
| GLM-5.3-Flash | `prt_0404a378600126mSkxUuld1POy` | `msg_0404915850013y3gbmpunpY4LK` | 19,269 bytes |
| Probe Enhancement | `prt_0404b9874001kmBj8x5C1DM9VB` | `msg_040491de90014Fggb14FXT1VOd` | 7,935 bytes |

---

## Automation Script

For future extractions, use this Python script pattern:

```python
#!/usr/bin/env python3
"""
Extract agent reports from OpenCode SQLite database.
Usage: python3 extract_report.py <session_id> <output_file>
"""

import subprocess
import json
import sys

def get_session_timeline(session_id):
    """Get timeline of text events for a session."""
    result = subprocess.run([
        'opencode-sessions-explorer-session-timeline',
        '--session_id', session_id,
        '--types', 'text',
        '--limit', '50',
        '--granularity', 'events'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

def get_part_content(part_id, max_bytes=100000):
    """Extract full content from a part."""
    result = subprocess.run([
        'opencode-sessions-explorer-get-part',
        '--part_id', part_id,
        '--max_bytes', str(max_bytes)
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if data['ok']:
        return data['data']['decoded']['text']
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 extract_report.py <session_id> <output_file>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    output_file = sys.argv[2]
    
    # Get timeline
    timeline = get_session_timeline(session_id)
    
    # Find last text part
    text_parts = [row for row in timeline['data']['events']['rows'] 
                  if row[3] == 0]  # type 0 = text
    
    if not text_parts:
        print("No text parts found")
        sys.exit(1)
    
    # Get last text part (final report)
    last_part = text_parts[-1]
    part_id = last_part[0]
    
    # Extract content
    content = get_part_content(part_id)
    if content:
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Extracted {len(content)} bytes to {output_file}")
    else:
        print("Failed to extract content")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## Best Practices

### 1. **Extract, Don't Regenerate**
- The report is already in the database — extract it directly
- Avoids Nemotron 3 Ultra's streaming timeout on file writes
- Preserves exact formatting and content

### 2. **Use Part IDs, Not Session IDs**
- Part IDs are stable and precise
- Session IDs can have multiple messages; part IDs pinpoint exact content

### 3. **Check Data Bytes First**
- Use `data_bytes` from timeline to identify the largest text part (the final report)
- Avoids extracting intermediate/partial responses

### 4. **Preserve Original Formatting**
- The database stores exact markdown with tables, code blocks, etc.
- Direct extraction preserves all formatting perfectly

### 5. **Verify Before Saving**
- Check `data_bytes` matches expected size
- Quick visual scan of extracted content before saving

### 6. **Document the Extraction**
- Record session ID, part ID, message ID, and extraction timestamp
- Enables reproducibility and audit trail

---

## Troubleshooting

### "Message not found" Error
- The message ID from timeline may not match get-message
- Use `get-part` directly with the part ID from timeline

### Truncated Content
- Increase `--max_bytes` parameter (default 65536, max 262144)
- For very large reports, use 100000 or higher

### Part Not Found
- Verify session ID is correct
- Check session has `archived: false`
- Verify part ID exists in timeline

### Empty Content
- Part may be reasoning type, not text
- Filter timeline by `type: text` only

---

## Integration with Omega Workflow

### For Research Sprints:
1. Launch research agents with chat-output instruction
2. Agents complete research and output to chat (stored in DB)
3. Run extraction script to pull all reports
4. Save to `data/entities/grokster/workspace/`
4. Commit to git for version control

### For Handoffs:
- Extract reports from specialist sessions
- Include in handoff packets
- Preserve exact content for receiving agent

---

## Tools Reference

### MCP Tools Used:
- `opencode-sessions-explorer-search-sessions-meta` — Find sessions by metadata
- `opencode-sessions-explorer-get-session` — Get session metadata
- `opencode-sessions-explorer-session-timeline` — Get event timeline
- `opencode-sessions-explorer-get-part` — Extract full part content
- `opencode-sessions-explorer-get-message` — Get message with all parts

### Direct SQLite Access (Advanced):
```bash
# Direct query for session parts
sqlite3 ~/.local/share/opencode/opencode.db "
SELECT p.id, p.type, p.data_bytes, m.role, m.modelID
FROM parts p
JOIN messages m ON p.message_id = m.id
WHERE m.session_id = '<SESSION_ID>' AND p.type = 'text'
ORDER BY p.time_created DESC
LIMIT 1;
"
```

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-08-26 | grokster | Initial version — documented today's 5-report extraction |

---

## Related Files

- `data/entities/grokster/workspace/R_OPENROUTER_FREE_ECOSYSTEM_20260826.md`
- `data/entities/grokster/workspace/R_OPENCODE_ZEN_PROVIDER_ANATOMY_20260826.md`
- `data/entities/grokster/workspace/R_MINIMAX_M27_M3_CAPABILITY_ANALYSIS_20260826.md`
- `data/entities/grokster/workspace/R_GLM53_FLASH_SUCCESSOR_ANALYSIS_20260826.md`
- `data/entities/grokster/workspace/R_PROBE_ENHANCEMENT_SCHEDULING_20260826.md`

---

*This guide enables the Omega Team to efficiently extract agent research outputs from the OpenCode database without inference overhead, avoiding file-write streaming timeouts and preserving exact content fidelity.*