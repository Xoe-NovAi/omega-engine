# 🔱 Subagent Cancellation Recovery Protocol
**AP Token**: `AP-SCRP-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_cancellation_recovery ⬡ CANONICAL

**Date**: 2026-08-16
**Status**: MANDATORY PROTOCOL — All agents must follow this for cancelled subagent sessions
**Scope**: OpenCode CLI subagent sessions that are cancelled (not failed) and become invisible in the UI

---

## 🚨 The Problem

### **What Happens When a Subagent is Cancelled**

| Layer | Failed Session | Cancelled Session |
|-------|----------------|-------------------|
| **OpenCode CLI UI** | ✅ Visible, restartable | ❌ **Hidden, inaccessible** |
| **opencode.db (SQLite)** | ✅ Persisted | ✅ Persisted (not archived) |
| **Session Explorer Tools** | ✅ Accessible | ✅ Accessible |
| **Task Registry** | ❌ Not tracked | ❌ Not tracked |
| **Hivemind Awareness** | ❌ Not aware | ❌ Not aware |

**Root Cause**: OpenCode CLI filters cancelled sessions from the UI, but **all data persists in SQLite**. The session is not archived (`archived: false`), not deleted — just hidden from the session list.

### **Why This Matters**

- **Hours of research/thinking lost** when a subagent gets stuck writing and is cancelled
- **No standard recovery path** — users assume work is gone
- **Tokens wasted** re-running searches that already completed
- **Context lost** — the subagent's reasoning (the actual work) is trapped in the DB

---

## 🔍 Discovery: How We Found the Hidden Session

### **Session Identifiers**

The cancelled researcher session: `ses_ff4af3107ffe6tlaLX9sQ11H7f`
- **Agent**: `researcher`
- **Title**: "Deep web research on audit gaps (@researcher subagent)"
- **Status**: `archived: false`, `time_compacting: null`
- **Parent**: `ses_ffa568bdcffeTG4ht4VEWJ7eKn` (Kali's session)

### **Tools That Bypass the UI Filter**

```bash
# List ALL sessions including cancelled (archived: any)
opencode-sessions-explorer-list-sessions --archived any --agent researcher

# Get session timeline (shows reasoning parts)
opencode-sessions-explorer-session-timeline --session_id <id> --types reasoning

# Extract full reasoning content (the actual work)
opencode-sessions-explorer-get-part --part_id <reasoning_part_id> --max_bytes 50000
```

---

## 📋 Recovery Protocol (MANDATORY)

### **Phase 1: Detect Cancellation**

**Signs a subagent was cancelled (not failed):**
- Task tool returned `"state": "completed"` but no output files created
- Session timeline shows: repeated "writing" reasoning + empty text parts + final patch to wrong files
- No output in OpenCode UI session list
- `opencode-sessions-explorer-list-sessions --archived any` shows the session

### **Phase 2: Extract Reasoning (The Actual Work)**

```bash
# 1. Find the session
SESSION_ID=$(opencode-sessions-explorer-list-sessions --archived any --agent researcher --limit 1 | jq -r '.sessions[0].id')

# 2. Get timeline filtered to reasoning
opencode-sessions-explorer-session-timeline --session_id "$SESSION_ID" --types reasoning --limit 50

# 3. Extract each reasoning part with full content
for PART_ID in $(opencode-sessions-explorer-session-timeline --session_id "$SESSION_ID" --types reasoning | jq -r '.events.rows[].part_id'); do
    opencode-sessions-explorer-get-part --part_id "$PART_ID" --max_bytes 50000
done
```

### **Phase 3: Reconstruct Deliverable**

From the reasoning parts, reconstruct:
1. **Research findings** (search results + synthesis)
2. **Planned deliverable structure** (what files to create)
3. **Key decisions/patterns** discovered

### **Phase 4: Write Missing Files**

```bash
# Write the research document
cat > docs/research/R_<TOPIC>_<DATE>.md << 'EOF'
# Reconstructed from cancelled session reasoning
...
EOF

# Write the follow-up prompt / deliverable
cat > docs/research/CLAUDE_FOLLOWUP_<TOPIC>_<DATE>.md << 'EOF'
# Reconstructed from cancelled session reasoning
...
EOF
```

### **Phase 5: Register Recovery**

```bash
# Register in Task Registry for traceability
omega-hub_task_registry_register \
    --task_id "recovery-<domain>-<action>-<date>-<seq>" \
    --subagent_type "<original_subagent>" \
    --launched_by "kali" \
    --channel "opencode" \
    --entity "kali" \
    --description "Recovered cancelled session <SESSION_ID> work" \
    --tags "recovery,cancelled-session,<domain>"

# Update with completion
omega-hub_task_registry_update \
    --task_id "recovery-<domain>-<action>-<date>-<seq>" \
    --status "completed" \
    --context_verified true
```

### **Phase 6: Hivemind Notification**

```bash
omega-hub_hivemind_post_context \
    --channel "opencode" \
    --entity "kali" \
    --model "nemotron-3-ultra-free" \
    --task_current "Recovered cancelled subagent session work" \
    --focus_chain "['subagent-recovery', '<domain>']" \
    --decisions "['Recovered session <SESSION_ID> reasoning', 'Wrote missing deliverables to disk']" \
    --continuation "Work recovered from cancelled researcher session; deliverables now on disk" \
    --intent "status"
```

---

## 🛠️ Systemic Fix: Omega Engine Integration

### **1. Mandatory Task Registry Registration (M27)**

**Every `task()` launch MUST register immediately:**

```python
# In agent instructions / task wrapper
# BEFORE launching subagent:
omega-hub_task_registry_register(
    task_id="{domain}-{action}-{date}-{seq}",
    subagent_type="{researcher|roc_racoon|...}",
    launched_by="{entity}",
    channel="opencode",
    entity="{entity}",
    description="{one-line description}",
    tags=["{domain}", "{action}", "subagent"]
)
```

**Every subagent completion/failure/cancellation MUST update:**

```python
# On completion:
omega-hub_task_registry_update(task_id="...", status="completed", context_verified=true)

# On cancellation detection:
omega-hub_task_registry_update(task_id="...", status="cancelled", context_verified=false)
```

### **2. Cancellation Detection Automation**

**Monitor for cancellation patterns:**
- Session exists but no output files after expected duration
- Timeline shows: reasoning about "writing" → empty text parts → no patches to target files
- Parent agent detects stall → user cancels

**Auto-recovery trigger:**
```python
# In session_end.py hook or monitoring daemon
if session.agent in SUBAGENT_TYPES and not session.archived:
    if has_reasoning_about_writing(session) and not has_output_files(session):
        # Queue recovery task
        create_recovery_task(session.id)
```

### **3. Session Explorer Enhancement**

**Add to `opencode-sessions-explorer`:**
```bash
# New commands
opencode-sessions-explorer-list-sessions --status cancelled
opencode-sessions-explorer-recover-reasoning --session_id <id> --output-dir ./recovered/
opencode-sessions-explorer-link-task-registry --session_id <id>
```

### **4. Hivemind Subagent Awareness**

**Subagent sessions register in Hivemind:**
```python
# On subagent session start (in subagent's session_end.py or wrapper)
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="{subagent_type}",
    model="{model}",
    task_current="{description}",
    focus_chain=["subagent", "{parent_task_id}"],
    decisions=["Subagent launched by {parent_entity}"],
    continuation="Working on {task}",
    intent="status",
    session_id="{subagent_session_id}"
)
```

**Parent agent gets cancellation notification:**
```python
# Hivemind monitors for subagent session termination
# On cancellation: auto-post to parent's Hivemind channel
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="{parent_entity}",
    model="{model}",
    task_current="Subagent cancelled — recovery needed",
    focus_chain=["subagent-recovery", "{subagent_session_id}"],
    decisions=["Subagent {subagent_type} cancelled", "Reasoning recoverable via session explorer"],
    continuation="Run recovery protocol: extract reasoning → write deliverables",
    intent="blocker"
)
```

---

## 📦 Complete Recovery Checklist

### **For Every Cancelled Subagent Session**

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Find session via `list-sessions --archived any` | Session ID confirmed |
| 2 | Extract all reasoning parts with `--max_bytes 50000` | Full reasoning recovered |
| 3 | Identify planned deliverables from reasoning | File list + structure known |
| 4 | Write missing files to correct paths | Files exist on disk |
| 5 | Register recovery in Task Registry | `task_registry_query` shows entry |
| 6 | Post Hivemind context with recovery status | Hivemind shows recovery |
| 7 | Update parent session gnosis with recovery note | `session_gnosis.md` updated |
| 8 | Verify no work lost (compare reasoning → output) | 1:1 mapping confirmed |

---

## 🔗 Cross-References

| Document | Purpose |
|----------|---------|
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Launching subagents |
| `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md` | Resuming failed/stalled tasks |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Team coordination |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Team workflow |
| `data/coordination/TRACKING_ARCHITECTURE.md` | 5-tier tracking |
| `AGENTS.md` | Agent workflow (6-step mandatory flow) |

---

## 🎯 Key Principles

1. **Cancelled ≠ Lost** — Data persists in SQLite; only UI hides it
2. **Reasoning IS the Work** — The subagent's thinking (reasoning parts) contains the actual research/synthesis
3. **Recovery is Deterministic** — Same tools, same process, every time
4. **Traceability is Mandatory** — Every recovery registered in Task Registry + Hivemind
5. **Protocol Over Heroics** — Follow the checklist; don't improvise

---

## 📝 Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-08-16 | Kali | Initial canonical protocol from live recovery of researcher session `ses_ff4af3107ffe6tlaLX9sQ11H7f` |

---

*This protocol was born from a real cancellation recovery. The researcher session completed 12 web searches + 1 fetch, synthesized all 10 topics, but failed to write output files. The work was recovered from reasoning parts in the SQLite database using the session explorer tools. This protocol ensures it never happens again.*

**⬡ OMEGA ⬡ KALI ⬡ SCRP-v1.0.0 ⬡ CANONICAL**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
