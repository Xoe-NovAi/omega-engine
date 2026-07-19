#!/usr/bin/env python3
"""
OpenCode Session Hydration — Restores context from session_gnosis.md
M15: Sovereign Continuity — recover from compaction/context loss
"""
import json
from pathlib import Path
from typing import Dict, Any

def hydrate_session(session_id: str) -> Dict[str, Any]:
    """Restore session context from gnosis file."""
    gnosis_file = Path.home() / ".config" / "opencode" / "session_gnosis" / f"{session_id}.md"
    
    if gnosis_file.exists():
        content = gnosis_file.read_text()
        return {
            "restored": True,
            "session_id": session_id,
            "gnosis_content": content,
            "source_file": str(gnosis_file)
        }
    
    # Fallback: check anchored summary
    anchored = Path(".opencode/anchored-summary.md")
    if anchored.exists():
        return {
            "restored": True,
            "session_id": session_id,
            "gnosis_content": anchored.read_text(),
            "source_file": str(anchored),
            "fallback": True
        }
    
    return {"restored": False, "session_id": session_id}

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: opencode-hydration <session_id>", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    result = hydrate_session(session_id)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()