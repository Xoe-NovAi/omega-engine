#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
OpenCode Compaction Resilience Guard
Monitors for compaction triggers and auto-writes session_gnosis.md
M15: Sovereign Continuity — maintain session anchors independently of toolchain
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

SESSION_GNOSIS_DIR = Path.home() / ".config" / "opencode" / "session_gnosis"
SESSION_GNOSIS_DIR.mkdir(parents=True, exist_ok=True)

def write_session_gnosis(session_id: str, context: Dict[str, Any]) -> Path:
    """Write session state before compaction."""
    gnosis_file = SESSION_GNOSIS_DIR / f"{session_id}.md"
    content = f"""# SESSION GNOSIS — {session_id}
**Captured**: {datetime.now().isoformat()}
**Reason**: Pre-compaction preservation (M15 Sovereign Continuity)

## Context
```json
{json.dumps(context, indent=2, default=str)}
```

## Active Tasks
{context.get('active_tasks', 'Unknown')}

## Key Decisions
{context.get('decisions', 'None recorded')}

## Continuation Notes
{context.get('continuation', 'Resume from last checkpoint')}

## Pipeline State (if applicable)
{context.get('pipeline_state', 'No active pipeline')}

## Hivemind Awareness
{context.get('hivemind_state', 'Not captured')}
"""
    gnosis_file.write_text(content)
    print(f"[compaction-guard] Wrote session gnosis to {gnosis_file}", file=sys.stderr)
    return gnosis_file

def main():
    if len(sys.argv) < 2:
        print("Usage: opencode-compaction-guard <session_id> [context_json]", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    write_session_gnosis(session_id, context)

if __name__ == "__main__":
    main()