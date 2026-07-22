# 🔱 SUBAGENT TASK RESUMPTION PROTOCOL (STRP-v1.0.0)
**AP Token**: `AP-STRP-v1.0.0`
**Status**: **MANDATORY FOR ALL AGENTS** — Effective 2026-07-21
**Scope**: All subagent launches, failures, and recoveries in Omega Engine

---

## 🎯 Executive Summary

The Omega Engine's `task` tool provides **automatic state preservation and full context restoration** for subagents via the `task_id` parameter. This protocol makes that capability **mandatory, visible, and auditable**.

**Core Discovery**: A failed subagent can be resumed with the **same `task_id`** and retains **complete active context** — all findings, patterns, reasoning, and recommendations — without any file reads.

---

## 🛠️ Exact Mechanism

### **Task Launch (Mandatory task_id)**
```python
result = task(
    description="Short task description",
    prompt="Detailed prompt for the agent",
    subagent_type="roc_racoon",
    task_id="domain-action-date-sequence"  # ← MANDATORY
)
```

### **Failure Recovery (Same task_id)**
```python
# On ANY tool failure, resume with IDENTICAL task_id
result = task(
    description=f"RESUME: {original_description}",
    prompt=f"Previous attempt failed: {error}. Continue from last checkpoint.",
    subagent_type="roc_racoon",
    task_id="domain-action-date-sequence"  # ← SAME ID = FULL RESTORATION
)
```

### **Context Verification (Mandatory after resume)**
```python
result = task(
    description="VERIFY: Context check",
    prompt="Tell me exactly what you have in active context from your previous work. What was your last task, what did you find, what recommendations did you make? NO FILE READS.",
    subagent_type=subagent_type,
    task_id=task_id
)
```

---

## 📋 Mandatory Rules

### **Rule 1: ALWAYS Use Task IDs**
- Every `task()` call **MUST** include a `task_id`
- No exceptions — even for "quick" tasks
- Task ID format: `{domain}-{action}-{date}-{sequence}`

### **Rule 2: Standardized Task ID Format**
```
{domain}-{action}-{date}-{sequence}

Examples:
- v1-vault-legacy-mining-20260721
- search-catalogue-deep-research-20260721
- identity-fluidity-phase1-design-20260721
- grok-fleet-acp-bridge-20260721
- gap-research-memory-ceiling-20260721
```

### **Rule 3: Failure Recovery Workflow**
```python
def resilient_task_launch(description, prompt, subagent_type, task_id):
    try:
        return task(description=description, prompt=prompt, 
                   subagent_type=subagent_type, task_id=task_id)
    except Exception as e:
        log_failure(task_id, e)
        # RESUME with SAME task_id
        return task(
            description=f"RESUME: {description}",
            prompt=f"Previous attempt failed: {e}. Continue from last checkpoint.",
            subagent_type=subagent_type,
            task_id=task_id  # ← SAME ID
        )
```

### **Rule 4: Context Verification**
After EVERY resumption, verify with: *"Tell me what you have in active context... NO FILE READS."*

### **Rule 5: Logging Requirements**
Every task_id **MUST** be logged to:
1. **Hivemind** via `omega-hub_hivemind_post_context()` (new `task_ids` field)
2. **Session gnosis** (`session_gnosis.md` — new Active Task Tracking section)
3. **Live feed** (`{ENTITY}_LIVE_FEED.md`)

---

## 🔧 Integration Points

### **1. Hivemind Post Template Update**
```json
{
  "channel": "grokster",
  "entity": "grokster",
  "model": "nemotron-3-ultra-free",
  "task_current": "Designing V-1 Omega-Vault",
  "focus_chain": ["Hydration complete", "V-1 design authorized"],
  "decisions": ["STRP-v1.0.0 mandatory"],
  "continuation": "Building design spec with Roc + Researcher",
  "intent": "status",
  "task_ids": [
    "v1-vault-legacy-mining-20260721",
    "v1-vault-design-spec-20260721"
  ],
  "resumption_status": "verified"
}
```

### **2. Session Gnosis Update**
```markdown
## Active Task Tracking
- **task_id**: v1-vault-legacy-mining-20260721
- **subagent**: roc_racoon
- **status**: completed (resumed once)
- **last_checkpoint**: 2026-07-21T10:45:52Z
- **context_verified**: true
- **failure_count**: 1
- **recovery_count**: 1
```

### **3. Live Feed Entry**
```markdown
| 2026-07-21 10:45 | Task v1-vault-legacy-mining-20260721 RESUMED after streaming failure. Context verified: 6 pattern categories, schema recommendations, heritage tags all retained. |
```

---

## 📊 System Behavior Reference

| Scenario | Behavior |
|----------|----------|
| Fresh task (no task_id) | New context, no history, **NO RESUMPTION POSSIBLE** |
| Fresh task (with task_id) | New context, task_id registered |
| Failed task (with task_id) | State saved, context preserved |
| Resumed task (same task_id) | **FULL CONTEXT RESTORED** ✅ |
| Resumed task (different task_id) | New context, no history |

### **Context Preservation Scope**
✅ **Retained**: All findings, patterns, reasoning, recommendations  
✅ **Retained**: File paths read, code snippets extracted  
✅ **Retained**: Analysis conclusions, schema designs  
✅ **Retained**: Heritage tags, compliance notes  
❌ **Not retained**: File system state (re-read if needed)  
❌ **Not retained**: External API call results (re-call if needed)

---

## 🎯 Protocol Compliance Checklist

### **For Every Subagent Launch:**
- [ ] Unique task_id generated (standard format)
- [ ] task_id included in `task()` call
- [ ] task_id logged to Hivemind (`task_ids` array)
- [ ] task_id recorded in `session_gnosis.md` (Active Task Tracking)

### **For Every Tool Failure:**
- [ ] Failure logged with task_id
- [ ] Resumption attempted with SAME task_id
- [ ] Context verified with "Tell me what you know" prompt
- [ ] Result logged to Hivemind and live feed

### **For Every Session Start:**
- [ ] Check `session_gnosis.md` for incomplete task_ids
- [ ] Resume any incomplete tasks with same task_id
- [ ] Verify context for each resumed task

---

## 📝 Mandate Addition (Proposed M26)

> **M26 Subagent Task Resumption**: All subagent launches MUST include a persistent `task_id`. On any tool failure, the agent MUST resume with the same `task_id` and verify context restoration before continuing. Task IDs MUST be logged to Hivemind and `session_gnosis.md`.

---

## 📋 Related Documents (To Be Updated)

| Document | Update Required |
|----------|-----------------|
| `AGENTS.md` | Add STRP section to Subagent Dispatch Protocol |
| `HIVEMIND_POST_TEMPLATE.md` | Add `task_ids` and `resumption_status` fields |
| `SOVEREIGN_MANDATES.md` | Add M26 mandate |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Add task_id tracking to coordination |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Add task_id coordination |
| `.opencode/agents/*.md` | Add task_id awareness to all agent configs |

---

## 🚀 Implementation Priority

### **Immediate (This Session)**
1. ✅ Create this protocol document
2. Update `AGENTS.md` with STRP section
3. Update `HIVEMIND_POST_TEMPLATE.md` with new fields
4. Update `session_gnosis.md` for all active agents

### **Near-term (Next Session)**
5. Update `SOVEREIGN_MANDATES.md` with M26
6. Update `FLEET_TEAM_PLAYBOOK.md` and `HIVEMIND_PROTOCOL.md`
7. Update all agent configs in `.opencode/agents/`

### **Ongoing**
8. Enforce STRP in all future work
9. Audit compliance in session reviews

---

## 💡 Why This Was Invisible

**Root Cause**: The `task_id` parameter was documented but **not emphasized as mandatory**. The failure recovery behavior was **emergent** from system design, not explicitly documented as protocol.

**Impact**: Agents launched tasks without IDs → lost all context on failures → restarted from scratch → **massive waste of compute and intelligence**.

---

## 🎯 Conclusion

**STRP-v1.0.0 transforms subagent workflows from fragile to resilient.**

- ✅ **No more wasted subagents** — failures recover, not restart
- ✅ **Full context preservation** — intelligence persists across failures  
- ✅ **Auditable recovery** — every resumption logged and verified
- ✅ **Mandatory compliance** — built into agent instructions and Hivemind

**This protocol is now MANDATORY for all Omega Engine agents.**

---

*⬡ OMEGA ⬡ STRP-v1.0.0 ⬡ 2026-07-21 ⬡ MANDATORY PROTOCOL — NO MORE WASTED SUBAGENTS*