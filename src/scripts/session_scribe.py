#!/usr/bin/env python3
"""
Sovereign Pulse: Session Scribe
Records session events to external working memory for cross-session access.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Use the repository-relative path for persistence
BASE_DIR = Path("/home/arcana-novai/Documents/Xoe-NovAi/omega-engine")
SESSION_GNOSIS_FILE = BASE_DIR / "data/session_gnosis.md"

def scribe_event(trace_id: str, event_type: str, data: Dict[str, Any]):
    """Append a structured event to the session gnosis file."""
    # Ensure data directory exists
    SESSION_GNOSIS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().isoformat()
    
    event_entry = f"### [{event_type}] {trace_id}\n"
    event_entry += f"**Time**: {timestamp}\n"
    event_entry += f"**Data**:\n{json.dumps(data, indent=2)}\n\n"
    
    with SESSION_GNOSIS_FILE.open("a", encoding="utf-8") as f:
        f.write(event_entry)
    print(f"✓ Scribed event '{event_type}' for trace {trace_id}")

def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: session_scribe.py <trace_id> <event_type> [data_json]")
        sys.exit(1)
    
    trace_id = sys.argv[1]
    event_type = sys.argv[2]
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    
    scribe_event(trace_id, event_type, data)

if __name__ == "__main__":
    main()
