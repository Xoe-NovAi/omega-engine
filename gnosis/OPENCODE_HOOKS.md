# OpenCode Hook Integration for Gnosis Lock
## Automatic Pre-Compaction Capture

---

> ## ⚠️ STATUS: HOOKS NOT SUPPORTED (as of OpenCode 1.18.30)
>
> Verified 2026-09-09: OpenCode v1.18.x does **not** implement a hooks /
> lifecycle-event system. The `hooks` key is absent from the config schema
> (`https://opencode.ai/config.json`), `opencode debug config` ignores it, and
> no hook code exists in the upstream repo. Adding `"hooks": {...}` to
> `opencode.json` has **no effect** — compaction runs normally and the ritual
> does not fire.
>
> Also verified: there is **no CLI command to compact a running session**
> (`opencode compact` is not a subcommand; it treats "compact" as a project
> path). Compaction happens only inside the TUI via `/compact`.
>
> **Use the shell commands instead** (already installed in `~/.bash_aliases`):
>
> | Instead of an auto-hook, run... | Then |
> |---------------------------------|------|
> | `gnosis-lock "reason"` | switch to OpenCode and type `/compact "reason"` |
> | `make gnosis-lock REASON="reason"` | switch to OpenCode and type `/compact "reason"` |
> | `gnosis-stats` / `make gnosis-stats` | view the evolution log |
>
> Full usage: see `docs/GNOSIS_USAGE.md`.
>
> The remainder of this document is kept as a **forward-compatible
> reference** — if OpenCode adds hooks in a later version, this integration
> can be re-enabled. The `opencode_hooks.py` handler already works when
> invoked manually (tested).

---

## Overview

OpenCode's hook system allows automatic execution of scripts at lifecycle events.
We configure hooks to run the pre-compaction ritual automatically.

---

## Hook Configuration

Add to `~/.config/opencode/opencode.json`:

```json
{
  "hooks": {
    "pre_compact": {
      "command": [
        "/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh",
        "--session-id",
        "{{session_id}}",
        "--reason",
        "Pre-compact hook triggered"
      ],
      "timeout": 120000
    },
    "session_end": {
      "command": [
        "/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh",
        "--session-id",
        "{{session_id}}",
        "--reason",
        "Session ended naturally"
      ],
      "timeout": 120000
    }
  }
}
```

---

## Available Hook Events

| Hook | Trigger | Use Case |
|------|---------|----------|
| `pre_compact` | Before `/compact` command | Capture state before context reduction |
| `session_end` | When session ends (exit, timeout) | Capture final state |
| `pre_task` | Before agent task starts | Mark task boundaries |
| `post_task` | After agent task completes | Capture task outcomes |
| `on_error` | When error occurs | Capture error context |
| `agent_switch` | When switching agents | Capture agent transition |

---

## Hook Variables

OpenCode provides these template variables:

| Variable | Description |
|----------|-------------|
| `{{session_id}}` | Current session ID |
| `{{agent_name}}` | Active agent name |
| `{{task_id}}` | Current task ID |
| `{{working_dir}}` | Project working directory |
| `{{model}}` | Active model name |

---

## Custom Hook Script: `scripts/compaction/opencode_hooks.py`

```python
#!/usr/bin/env python3
# OpenCode Hook Handler for Gnosis Lock
# Called by OpenCode hooks, routes to appropriate ritual

import json
import sys
import os
import subprocess
from datetime import datetime, timezone

HOOK_TYPE = os.environ.get("OPENCODE_HOOK_TYPE", "")
SESSION_ID = os.environ.get("OPENCODE_SESSION_ID", f"hook-{datetime.now().isoformat()}")
REASON = os.environ.get("OPENCODE_HOOK_REASON", "Hook triggered")

RITUAL_SCRIPT = "/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh"

def run_ritual(reason: str) -> int:
    """Execute the pre-compaction ritual."""
    try:
        result = subprocess.run(
            [RITUAL_SCRIPT, "--session-id", SESSION_ID, "--reason", reason],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("❌ Ritual timed out", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Ritual failed: {e}", file=sys.stderr)
        return 1

def main():
    hook_type = os.environ.get("OPENCODE_HOOK_TYPE", "unknown")
    
    reason_map = {
        "pre_compact": "Pre-compact hook",
        "session_end": "Session ended",
        "pre_task": "Task started",
        "post_task": "Task completed",
        "on_error": "Error occurred",
        "agent_switch": "Agent switched"
    }
    
    reason = reason_map.get(hook_type, f"Hook: {hook_type}")
    
    print(f"🔱 Gnosis Lock: {hook_type} hook triggered for session {os.environ.get('OPENCODE_SESSION_ID', 'unknown')}")
    
    if hook_type in ["pre_compact", "session_end"]:
        # Full ritual for compaction/session end
        return run_ritual(reason)
    elif hook_type in ["post_task", "on_error"]:
        # Lightweight event logging
        log_event(hook_type, reason)
        return 0
    else:
        print(f"ℹ️  Hook {hook_type} acknowledged, no ritual needed")
        return 0

def log_event(hook_type: str, reason: str):
    """Log lightweight event to evolution log."""
    try:
        import json
        EVOLUTION_LOG = "/home/xnai/Documents/Projects/omega-engine-alpha/gnosis/evolution/evolution_log.jsonl"
        
        event = {
            "event_id": f"hook-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "event_type": "HOOK_EVENT",
            "session_id": SESSION_ID,
            "description": f"OpenCode hook: {hook_type} - {reason}",
            "metadata": {"hook_type": hook_type},
            "tags": ["hook", hook_type],
            "version": "1.0"
        }
        
        with open(EVOLUTION_LOG, 'a') as f:
            f.write(json.dumps(event) + '\n')
    except Exception as e:
        print(f"⚠️  Failed to log hook event: {e}", file=sys.stderr)

if __name__ == "__main__":
    from datetime import timezone
    sys.exit(main())
```

---

## Installation

```bash
# 1. Make scripts executable
chmod +x /home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh
chmod +x /home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/opencode_hooks.py

# 2. Add hook config to opencode.json (merge with existing)
# See opencode.json hook configuration above

# 3. Test hook manually
OPENCODE_HOOK_TYPE=pre_compact OPENCODE_SESSION_ID=test-session OPENCODE_HOOK_REASON="Test" \
  python3 /home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/opencode_hooks.py
```

---

## Hook Debugging

```bash
# View hook execution logs
tail -f ~/.local/share/opencode/logs/hooks.log

# Test ritual directly
/home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh \
  --session-id manual-test --reason "Manual test"

# Check evolution log after hook
tail -5 /home/xnai/Documents/Projects/omega-engine-alpha/gnosis/evolution/evolution_log.jsonl
```

---

## Integration with Evolution Log

Hooks automatically log `HOOK_EVENT` events to the evolution log with:
- `event_type`: HOOK_EVENT
- `metadata.hook_type`: The hook that triggered
- `tags`: ["hook", hook_type]
- `session_id`: Current session

This provides full traceability of when rituals ran and why.

---

*Part of Gnosis Lock Protocol v1.0 — ensuring no gnosis is lost to compaction or session boundaries.*