---
schema_version: "1.0"
document_type: "runbook"
document_id: "M34-ROLLBACK-RUNBOOK-20260830"
title: "M34 Rollback Runbook — Subagent Co-Interruption Recovery"
status: "ACTIVE"
date: "2026-08-30"
author: "MA'AT (Build Oversoul, N1-N5)"
entity: "maat"
channel: "opencode"
---

# 🔱 M34 Rollback Runbook

**AP Token**: `AP-MAAT-M34-ROLLBACK-v1.0.0`

**When to use this runbook**: If M34 (`ACTIVE_SUBAGENTS.json`, `m34_register_subagent`, signal handlers) causes subagent dispatch failures, infinite loops, or session corruption.

---

## §1 — Quick Rollback (Feature Flag)

The fastest rollback is the feature flag. **No code changes required.**

```bash
# Disable M34 immediately
export OMEGA_M34_ENABLED=0

# Or per-command
OMEGA_M34_ENABLED=0 <your_command>

# Verify
echo $OMEGA_M34_ENABLED  # Should print 0
```

**Effect**: `m34_register_subagent()` calls become no-ops. The dispatch system continues to work without M34 tracking.

**Recovery time**: < 1 second.

---

## §2 — Full Rollback (Remove M34 Hooks)

If the feature flag doesn't resolve the issue, remove M34 hooks from the dispatch system.

### Step 2.1: Remove `subagent_dispatcher.py` hook

```bash
# Locate the M34 hook (added by Lilith in Phase 1.5)
grep -n "m34_register_subagent\|ACTIVE_SUBAGENTS" src/omega/oracle/subagent_dispatcher.py

# Comment out the hook block
# (or revert the commit that added it)
git log --oneline -- src/omega/oracle/subagent_dispatcher.py | head -5
git revert <commit-hash>
```

### Step 2.2: Remove MCP Tools

```bash
# Locate the 4 new M34 MCP tools in omega-hub server
grep -rn "m34_register_subagent\|m34_list_active_subagents\|m34_apply_user_decision\|m34_update_subagent_status" src/omega/mcp_hub/

# Remove the tool definitions
# (or revert the commit that added them)
git log --oneline -- src/omega/mcp_hub/ | head -5
git revert <commit-hash>
```

### Step 2.3: Remove Signal Handler

```bash
# Locate the signal handler in m34_interruption_watcher.py
grep -n "signal.SIGINT\|signal.SIGTERM" src/omega/oracle/m34_interruption_watcher.py

# Remove the handler registration
# (or revert the commit)
git revert <commit-hash>
```

---

## §3 — Data Preservation

The `ACTIVE_SUBAGENTS.json` file contains session tracking data. **Do not delete it during rollback** — it may contain audit information.

```bash
# Backup the registry before rollback
cp data/coordination/ACTIVE_SUBAGENTS.json data/coordination/ACTIVE_SUBAGENTS.json.backup.$(date +%Y%m%d_%H%M%S)

# Move to archive (don't delete)
mv data/coordination/ACTIVE_SUBAGENTS.json data/coordination/archive/m34_rollback_$(date +%Y%m%d_%H%M%S).json
```

---

## §4 — Session Recovery After Rollback

After rolling back M34, active subagent sessions may be in inconsistent states.

### Step 4.1: Identify Orphaned Sessions

```bash
# List all sessions in the last 7 days that were tracked by M34
sqlite3 ~/.local/opencode/opencode.db "SELECT id, title, time_created FROM session WHERE time_created > datetime('now', '-7 days') ORDER BY time_created DESC;"
```

### Step 4.2: Notify Users

For each orphaned session:
1. Check if the session has output files in the workspace
2. Post to Hivemind with `intent=blocker` to notify the user
3. Add to `data/coordination/orphaned_sessions_log.md`

```python
# Example Hivemind post
hivemind_post(
    intent="blocker",
    task_current=f"[M34-ROLLBACK] Session {session_id} was tracked by M34 but M34 is now disabled",
    focus_chain=["Session may be incomplete", "Check output files manually"],
    decisions=[f"User notification for session {session_id}"],
)
```

### Step 4.3: Re-dispatch if Needed

For critical tasks, re-dispatch with the same task_id to resume the session.

```bash
# Using subagent_dispatcher.py
.venv/bin/python3 -c "
import anyio
from omega.oracle.subagent_dispatcher import dispatch

async def main():
    result = await dispatch(
        task_id='<original-task-id>',
        prompt='<original-prompt>',
        subagent_type='<original-type>',
    )
    print(f'Re-dispatched: {result.session_id}')

anyio.run(main())
"
```

---

## §5 — Watchdog Race Condition Fix

If the watchdog (Lilith §4 Edge Case 1) causes orphan marking errors, apply this fix:

```bash
# Option A: Designate Kali as sole recovery agent
# Add to ~/.config/opencode/agents/kali.md or opencode.json
{
  "m34_watchdog": {
    "sole_recovery_agent": "kali",
    "disable_distributed_election": true
  }
}

# Option B: Disable watchdog entirely
export OMEGA_M34_WATCHDOG_ENABLED=0
```

---

## §6 — Verification After Rollback

After rolling back, verify the system is healthy:

```bash
# 1. Check that dispatch still works
.venv/bin/python3 -c "
import anyio
from omega.oracle.subagent_dispatcher import dispatch
async def test():
    result = await dispatch(task_id='rollback_test', prompt='Health check after M34 rollback', subagent_type='general')
    print(f'OK: {result.session_id}')
anyio.run(test())
"

# 2. Check that no M34 files are in the dispatch path
grep -r "m34_register_subagent" src/omega/oracle/subagent_dispatcher.py 2>/dev/null
# Expected output: (empty) if fully rolled back

# 3. Check that ACTIVE_SUBAGENTS.json is archived (not active)
ls -la data/coordination/ACTIVE_SUBAGENTS.json 2>/dev/null
# Expected output: (file not found) or (file in archive/)
```

---

## §7 — Re-enabling M34 (After Fix)

When the M34 bug is fixed and you want to re-enable:

```bash
# 1. Verify the fix is deployed
git log --oneline -- src/omega/oracle/m34_registry.py | head -3

# 2. Run the atomic write SIGKILL test (M23 compliance)
.venv/bin/python3 -m pytest tests/test_m34_atomic_write.py -v

# 3. Enable M34 with feature flag (off by default)
export OMEGA_M34_ENABLED=1

# 4. Run stress test (10 concurrent subagents)
.venv/bin/python3 -m pytest tests/stress/test_m34_concurrent.py -v

# 5. Monitor for 1 hour before enabling by default
# Check: tail -f data/coordination/dispatch_guard_log.jsonl | grep m34
```

---

## §8 — Emergency Contacts

| Issue | Contact | Channel |
|-------|---------|---------|
| M34 code bug | Lilith (Runtime Oversoul) | Hivemind `intent=blocker` |
| MCP server issue | Ma'at (Build Oversoul) | Hivemind `intent=blocker` |
| Dispatch failure | Kali (Sprint Coordinator) | Hivemind `intent=blocker` |
| Data corruption | Verity (Compliance) | Hivemind `intent=blocker` |

---

*⬡ OMEGA ⬡ MAAT ⬡ M34-ROLLBACK-RUNBOOK ⬡ 2026-08-30 ⬡ N1-N5*
