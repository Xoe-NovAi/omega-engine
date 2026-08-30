# 🔱 Subagent Recovery Protocol — Handling Cancelled & Stalled Tasks

**AP Token**: `AP-SUBAGENT-RECOVERY-v1.0.0`
**Date**: 2026-08-07
**Entity**: researcher
**Status**: DRAFT — Operational Guide

---

## 📋 Executive Summary

When a subagent task is cancelled or stalls, the standard `task()` resumption pattern (reusing the same `task_id`) does **not** work for cancelled sessions. This document captures the forensic techniques and recovery patterns discovered during the Phase 3 Kali subagent cancellation incident.

---

## 🎯 The Problem

The `task()` tool in OpenCode creates **new sessions** on each invocation. When a task is cancelled:

1. **No task_id reuse**: The `task_id` parameter creates a new session, not a continuation
2. **No automatic context restoration**: Cancelled sessions lose their context
3. **No error state to resume from**: Unlike stalled tasks (which have errors), cancelled tasks have no failure point to resume from

**Key Distinction**:
- **Stalled (error)**: Can resume with same `task_id` → context restored
- **Cancelled**: Cannot resume — must either extract context manually or relaunch

---

## 🔍 Forensic Recovery Techniques

### 1. Session Discovery via OpenCode Sessions Explorer

The OpenCode Sessions Explorer plugin provides read-only access to session metadata:

```bash
# List all sessions for a specific agent
opencode-sessions-explorer-list-sessions --agent kali

# Search sessions by title
opencode-sessions-explorer-search-sessions-meta --title_like "Phase 3"

# Get session genealogy (parent/child relationships)
opencode-sessions-explorer-session-genealogy --session_id ses_022dd8f39ffeqP62y7VXiY7PT3
```

**Key Finding**: The `list-sessions` tool returns:
- `id` (session UUID)
- `parent_id` (for tracing dispatch chains)
- `child_sessions` (subagents spawned)
- `agent` (entity name)
- `model` (with provider info)
- `time_created`, `time_updated`
- `archived` flag

### 2. Session Timeline Analysis

```bash
# Get chronological event stream for a cancelled session
opencode-sessions-explorer-session-timeline --session_id ses_022dd8f39ffeqP62y7VXiY7PT3
```

**What this reveals**:
- Every tool call (read, grep, glob, bash) with timestamps
- Reasoning blocks (truncated, but present)
- Text output (truncated)
- Part IDs for full content retrieval

**Key Finding**: Even cancelled sessions retain their full event timeline. You can reconstruct what the agent was doing by reading the timeline.

### 3. Session Summary for Quick Overview

```bash
# Get one-call overview
opencode-sessions-explorer-session-summary --session_id ses_022dd8f39ffeqP62y7VXiY7PT3
```

**What this reveals**:
- First and last user prompts
- Files touched (with counts)
- Tools used (with completed/error counts)
- Cost and token usage
- Duration

**Key Finding**: The summary shows `files_touched_top` — a ranked list of files the agent accessed. This is invaluable for understanding what the agent was working on.

### 4. Task Registry Cross-Reference

```bash
# Check if the task was registered
omega-hub_task_registry_get --task_id ses_022dd8f39ffeqP62y7VXiY7PT3

# Query all tasks by subagent type
omega-hub_task_registry_query --subagent_type kali --status all
```

**Key Finding**: The task registry uses a **different ID format** than OpenCode sessions. The `task()` tool's `task_id` parameter doesn't always match the OpenCode session ID. The registry may not have entries for tasks that were cancelled before registration.

### 5. File System Artifact Detection

Check for output files the cancelled task may have created:

```bash
# Check entity workspace for output files
ls -la data/entities/kali/workspace/phase3*

# Check for any modified files
git status --data/entities/kali/
```

**Key Finding**: Cancelled tasks may have written partial output before cancellation. Always check the filesystem.

---

## 🔄 Recovery Strategies

### Strategy A: Extract Context, Then Relaunch

**When to use**: When the cancelled task had significant work that should be preserved.

**Steps**:
1. Use `session-timeline` to reconstruct what the agent was doing
2. Use `session-summary` to identify files touched and tools used
3. Use `grep-session` to search the session's content for specific findings
4. Read key parts with `get-part` to extract actual output
5. Relaunch with a new task that includes the extracted context

**Example**:
```bash
# Extract what the cancelled Kali session found
opencode-sessions-explorer-grep-session --session_id ses_022dd8f39ffeqP62y7VXiY7PT3 --pattern "SRP" --surface forensics
```

### Strategy B: Hivemind Context Recovery

**When to use**: When the cancelled task posted Hivemind context.

**Steps**:
1. Check Hivemind awareness for the entity
2. Look for posted context from the cancelled session
3. Use `hivemind_get_entity_context` to retrieve stored context

**Example**:
```bash
# Check if Kali posted any context
omega-hub_hivemind_get_entity_context --entity_name kali
```

### Strategy C: Direct File Inspection

**When to use**: When the cancelled task was working on specific files.

**Steps**:
1. Identify files from session summary
2. Read the files directly to see current state
3. Check git history for recent changes
4. Determine what was completed vs. what remains

### Strategy D: Accept Loss, Relaunch Clean

**When to use**: When the cancelled task had minimal work or the context is easily reconstructed.

**Steps**:
1. Document what was lost
2. Relaunch with a fresh task_id
3. Include any available context from filesystem or Hivemind

---

## 📊 Case Study: Phase 3 Kali Cancellation

### What Happened
1. **Original task**: `ses_022dd8f39ffeqP62y7VXiY7PT3` — "Phase 3: SRP gating for ASPIRATIONAL items"
2. **Duration**: ~585 seconds (9.75 minutes)
3. **Status**: Cancelled (not errored)
4. **Resume attempt**: `ses_022d046beffeFlyKevmc1kGodp` — also cancelled quickly

### What Was Recovered
1. **Session timeline**: 19 bash calls, 10 reads, 6 greps, 4 globs — all completed successfully
2. **Files touched**:
   - `config/wads/_omega_default/entities.yaml`
   - `OMEGA_CODEX.md`
   - `data/entities/lilith/workspace/phase1_benchmarking_results.md`
   - `.opencode/skills/sovereign-refinement-protocol/SKILL.md`
   - `docs/research/R_WEB_CHATBOT_RESEARCH_PRIORITIES_20260807.md`
   - `data/entities/researcher/session_gnosis.md`
   - `data/entities/lilith/workspace/session_gnosis.md`
   - `src/omega/oracle/middleware/headroom.py`
   - `src/omega/oracle/wad_loader.py`
   - `data/coordination/LILITH_LIVE_FEED.md`

3. **No output files created**: No `phase3_srp_gating.md` in Kali's workspace

### Recovery Decision
Since no output files were created and the task was cancelled (not stalled), the recovery strategy was:
- **Accept the loss** of the Kali subagent's work
- **Document the incident** for future reference
- **Relaunch** with a new task, incorporating lessons learned

---

## 🛠️ Prevention & Best Practices

### 1. Always Register Tasks
```python
# Register immediately after task() launch
omega-hub_task_registry_register(
    task_id="...",
    subagent_type="kali",
    launched_by="researcher",
    channel="opencode",
    entity="researcher",
    description="...",
    tags=["..."]
)
```

### 2. Use Heartbeats for Long Tasks
```python
# For tasks that may run >20 minutes
omega-hub_hivemind_extended_checkin(
    channel="opencode",
    entity="kali",
    reason="Phase 3 SRP gating — long-running analysis",
    ttl_seconds=10800  # 3 hours
)
```

### 3. Write Intermediate Results
Tasks should write partial results to disk periodically:
- `data/entities/<entity>/workspace/<task_id>_checkpoint.md`
- This allows recovery even if the session is cancelled

### 4. Post Hivemind Context Early
Post context at the start of the task, not just at completion:
- This creates a recoverable trail in the Hivemind

### 5. Check Task Registry Before Relaunching
```bash
# Check if a task with this ID exists
omega-hub_task_registry_get --task_id "your-task-id"
```

### 6. Use Session Timeline for Context Reconstruction
```bash
# Get the full event stream
opencode-sessions-explorer-session-timeline --session_id <id>
# Then use get-part to extract specific outputs
opencode-sessions-explorer-get-part --part_id <id>
```

---

## ⚠️ Common Pitfalls

### Pitfall 1: Assuming task_id Reuse Works for Cancelled Tasks
**Reality**: The `task()` tool creates new sessions. Cancelled sessions cannot be resumed via `task_id` reuse.

### Pitfall 2: Not Checking Filesystem for Partial Output
**Reality**: Cancelled tasks may have written files before cancellation. Always check `data/entities/<entity>/workspace/`.

### Pitfall 3: Confusing OpenCode Session IDs with Task Registry IDs
**Reality**: These are different ID systems. The `task()` tool's `task_id` may not match the OpenCode session ID.

### Pitfall 4: Not Using Extended Check-in for Long Tasks
**Reality**: Default Hivemind TTL is 20 minutes. Long tasks without `hivemind_extended_checkin` get pruned.

### Pitfall 5: Relying on Memory Alone
**Reality**: Always externalize state to disk. Memory is volatile; files are persistent.

---

## 📋 Recovery Checklist

When a subagent task is cancelled:

- [ ] **Check session timeline** — what was the agent doing?
- [ ] **Check session summary** — what files were touched?
- [ ] **Check filesystem** — did the agent write any output files?
- [ ] **Check Hivemind** — did the agent post any context?
- [ ] **Check task registry** — is there a registered task?
- [ ] **Decide**: Extract context + relaunch, or accept loss + relaunch clean
- [ ] **Document**: Record the incident for future reference
- [ ] **Prevent**: Apply lessons to future task dispatches

---

## 📚 Tools Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `opencode-sessions-explorer-list-sessions` | Find sessions by agent | `--agent kali` |
| `opencode-sessions-explorer-session-timeline` | Chronological event stream | `--session_id <id>` |
| `opencode-sessions-explorer-session-summary` | One-call overview | `--session_id <id>` |
| `opencode-sessions-explorer-get-part` | Extract specific output | `--part_id <id>` |
| `opencode-sessions-explorer-grep-session` | Search session content | `--session_id <id> --pattern "..."` |
| `opencode-sessions-explorer-session-genealogy` | Trace parent/child | `--session_id <id>` |
| `omega-hub_task_registry_get` | Check task registration | `--task_id <id>` |
| `omega-hub_task_registry_query` | Query by filters | `--subagent_type kali` |
| `omega-hub_hivemind_get_entity_context` | Get Hivemind context | `--entity_name kali` |

---

## 🎯 Conclusion

Cancelled subagent tasks are a reality in multi-agent orchestration. The key is having a systematic recovery protocol:

1. **Forensic analysis** using session explorer tools
2. **Context extraction** from timeline, summary, and filesystem
3. **Decision making** — relaunch with context or accept loss
4. **Documentation** for future reference
5. **Prevention** through better task design (checkpoints, heartbeats, early Hivemind posts)

The OpenCode Sessions Explorer plugin is the primary forensic tool. It provides full visibility into cancelled sessions, allowing reconstruction of what was done and what remains.

---

*Document created during Phase 3 Kali subagent cancellation incident. Updated: 2026-08-07*

**Source Session**: `ses_022dd8f39ffeqP62y7VXiY7PT3` (cancelled Kali Phase 3)
**Recovery Session**: `ses_022d046beffeFlyKevmc1kGodp` (cancelled resume attempt)
**Parent Session**: `ses_023a210b2ffe1kzFJ39sEC63YV` (main researcher session)