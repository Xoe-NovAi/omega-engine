#!/usr/bin/env python3
# ==============================================================================
# OMEGA ENGINE — OPENCODE HOOK HANDLER
# ==============================================================================
# Handles OpenCode lifecycle hooks, routes to pre-compaction ritual or
# logs lightweight events to evolution log.
#
# Environment variables provided by OpenCode:
#   OPENCODE_HOOK_TYPE       - Type of hook (pre_compact, session_end, etc.)
#   OPENCODE_SESSION_ID      - Current session ID
#   OPENCODE_HOOK_REASON     - Human-readable reason
#   OPENCODE_AGENT_NAME      - Active agent name
#   OPENCODE_TASK_ID         - Current task ID
#   OPENCODE_WORKING_DIR     - Project working directory
# ==============================================================================

import json
import sys
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path("/home/xnai/Documents/Projects/omega-engine-alpha")
RITUAL_SCRIPT = PROJECT_ROOT / "scripts" / "compaction" / "pre_compaction_ritual.sh"
EVOLUTION_LOG = PROJECT_ROOT / "gnosis" / "evolution" / "evolution_log.jsonl"

# ─── Event Type Mapping ───────────────────────────────────────────────────────
HOOK_REASONS = {
    "pre_compact": "Pre-compact hook triggered",
    "session_end": "Session ended naturally",
    "pre_task": "Task started",
    "post_task": "Task completed",
    "on_error": "Error occurred",
    "agent_switch": "Agent switched"
}

RITUAL_HOOKS = {"pre_compact", "session_end"}
LIGHTWEIGHT_HOOKS = {"post_task", "on_error", "agent_switch", "pre_task"}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def append_evolution_log(event: dict) -> None:
    """Append event to evolution log (append-only JSONL)."""
    EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EVOLUTION_LOG, 'a') as f:
        f.write(json.dumps(event) + '\n')

def log_hook_event(hook_type: str, session_id: str, reason: str, metadata: dict = None) -> None:
    """Log a lightweight hook event to evolution log."""
    event = {
        "event_id": f"hook-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "timestamp": now_iso(),
        "event_type": "HOOK_EVENT",
        "session_id": session_id,
        "description": f"OpenCode hook: {hook_type} — {reason}",
        "metadata": metadata or {"hook_type": hook_type},
        "tags": ["hook", hook_type],
        "version": "1.0"
    }
    append_evolution_log(event)

def run_ritual(session_id: str, reason: str) -> int:
    """Execute the full pre-compaction ritual."""
    try:
        result = subprocess.run(
            [str(RITUAL_SCRIPT), "--session-id", session_id, "--reason", reason],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT)
        )
        # Print output for visibility in hook logs
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("❌ Ritual timed out after 120s", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Ritual failed: {e}", file=sys.stderr)
        return 1

# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    hook_type = os.environ.get("OPENCODE_HOOK_TYPE", "unknown")
    session_id = os.environ.get("OPENCODE_SESSION_ID", f"hook-{now_iso()}")
    agent_name = os.environ.get("OPENCODE_AGENT_NAME", "unknown")
    task_id = os.environ.get("OPENCODE_TASK_ID", "none")
    
    reason = HOOK_REASONS.get(hook_type, f"Hook: {hook_type}")
    
    print(f"🔱 Gnosis Lock: [{hook_type}] hook for session {session_id} (agent: {agent_name})")
    
    # Always log hook event to evolution log
    log_hook_event(hook_type, session_id, reason, {
        "hook_type": hook_type,
        "agent_name": agent_name,
        "task_id": task_id
    })
    
    # Route to appropriate handler
    def run_ritual(session_id: str, reason: str) -> int:
        """Execute the full pre-compaction ritual."""
        try:
            result = subprocess.run(
                [str(RITUAL_SCRIPT), session_id, reason],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(PROJECT_ROOT)
            )
            # Print output for visibility in hook logs
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.returncode
        except subprocess.TimeoutExpired:
            print("❌ Ritual timed out after 120s", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"❌ Ritual failed: {e}", file=sys.stderr)
            return 1
    
    if hook_type in RITUAL_HOOKS:
        print(f"🔄 Running full pre-compaction ritual...")
        return run_ritual(session_id, reason)
    
    elif hook_type in LIGHTWEIGHT_HOOKS:
        print(f"📝 Logged lightweight hook event")
        return 0
    
    else:
        print(f"ℹ️  Unknown hook type '{hook_type}', logged only")
        return 0

if __name__ == "__main__":
    sys.exit(main())