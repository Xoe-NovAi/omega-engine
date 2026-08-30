<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI'S GUIDE: RESUMING STALLED RESEARCHER SUBAGENTS
**STRP-v1.0.0 Protocol — Practical Implementation Guide**

---

## 🎯 **What This Guide Covers**

You have **2 stalled Researcher subagents** in your parallel chat. This guide explains:
- **How the task resumption system works** (STRP-v1.0.0)
- **Exact commands to resume your subagents** with full context
- **Best practices** to never lose work again
- **Troubleshooting** for common issues

---

## 🧠 **How the System Works (The Secret)**

### **The Magic: `task_id` Parameter**

When you launch a subagent with a `task_id`, the system **automatically saves state** at checkpoints. If the tool fails (streaming error, timeout, etc.), the **same `task_id` restores FULL CONTEXT** — all findings, patterns, reasoning, recommendations — **without any file reads**.

```
┌─────────────────────────────────────────────────────────────┐
│  LAUNCH WITH task_id          FAILURE OCCURS               │
│  ─────────────────────        ─────────────────             │
│  task(                        System auto-saves:            │
│    description="...",         • Active context              │
│    prompt="...",              • Findings & patterns         │
│    subagent_type="researcher",│ • Reasoning chains          │
│    task_id="my-task-20260721" │ • Recommendations           │
│  )                            │ • File paths read           │
│                               │                             │
│  RESUME WITH SAME task_id     │                             │
│  ─────────────────────────    │                             │
│  task(                        │                             │
│    description="RESUME: ...", │                             │
│    prompt="Continue...",      │                             │
│    subagent_type="researcher",│                             │
│    task_id="my-task-20260721" │  ← SAME ID = FULL RESTORE  │
│  )                            │                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Step 1: Find Your Task IDs**

### **Check Your Session Gnosis**
```bash
# Look for Researcher tasks in your session tracking
grep -A 3 "task_id.*researcher" data/entities/researcher/session_gnosis.md
```

### **Expected Format**
```
task_id: research-local-ai-crisis-frameworks-20260721
subagent: researcher
status: completed (resumed once)
last_checkpoint: 2026-07-21T11:26:55.854183+00:00
context_verified: true
failure_count: 1
recovery_count: 1
```

### **If No Task IDs Found**
Check your Hivemind handoffs:
```bash
omega-hub_hivemind_handoff_list(status="active") | grep researcher
```

---

## 🚀 **Step 2: Resume Your Subagents**

### **Template Command (Copy & Adapt)**

```python
# FOR EACH STALLED TASK — Use EXACT SAME task_id
task(
    description="RESUME: [Original Task Description]",
    prompt="Previous attempt failed with: '[ERROR MESSAGE]'. Continue from last checkpoint where [WHAT YOU WERE DOING].",
    subagent_type="researcher",
    task_id="[YOUR_EXACT_TASK_ID]"  # ← CRITICAL: SAME ID
)
```

### **Real Example for Your Tasks**

```python
# Task 1: Local AI Crisis Frameworks
task_id_1 = "research-local-ai-crisis-frameworks-20260721"

task(
    description="RESUME: Research local offline AI crisis intervention frameworks",
    prompt="Previous attempt failed with: 'API timeout while querying local models'. Continue from last checkpoint where we collected 12 case studies and identified 3 framework categories.",
    subagent_type="researcher",
    task_id=task_id_1
)

# Task 2: Cognitive Bias Detection
task_id_2 = "cognitive-bias-local-llm-detection-20260721"

task(
    description="RESUME: Cognitive bias detection in small LLMs",
    prompt="Previous attempt failed with: 'Insufficient local data for bias analysis'. Continue from last checkpoint where we analyzed 5 local models and documented bias patterns.",
    subagent_type="researcher",
    task_id=task_id_2
)
```

---

## ✅ **Step 3: Verify Context (MANDATORY)**

### **After EACH Resumption, Run This:**

```python
# Verify context was fully restored
task(
    description="VERIFY: Context check for [task name]",
    prompt="Tell me exactly what you have in active context from your previous work on [topic]. What did you find? What recommendations did you make? What was your last step? NO FILE READS.",
    subagent_type="researcher",
    task_id="[SAME_TASK_ID]"
)
```

### **Expected Good Response**
```
## Researcher — Active Context Report

### Last Task Completed
Research local offline AI crisis intervention frameworks — collected 12 case studies...

### Repositories Mined
| Repo | Status | Key Files |
|------|--------|-----------|
| ...  | ✅     | ...       |

### Key Findings
1. Pattern A: ...
2. Pattern B: ...

### Recommendations Made
- Schema design for...
- Implementation focus on...

### Deliverable Written
File: data/coordination/RESEARCHER_XXX_20260721.md
```

---

## 📋 **Step 4: Log Everything (Hivemind + Session Gnosis)**

### **Update Hivemind (After Each Resumption)**
```python
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="kali",
    model="nemotron-3-ultra-free",
    task_current="[RESUME] Researcher subagents resumed with full context",
    focus_chain=[
        "Resume research local offline AI crisis intervention frameworks",
        "Resume cognitive bias detection in small LLMs",
        "Verify context and continue with data collection"
    ],
    decisions=[
        "D-XXX: Resumed failed Researcher tasks with full context preservation"
    ],
    continuation="Next: Verify context and continue with data collection — @researcher acknowledge via hivemind_accept_handoff",
    session_id="ses_20260721_kali_003",
    intent="status",
    suggested_model=None,
    task_ids=["research-local-ai-crisis-frameworks-20260721", "cognitive-bias-local-llm-detection-20260721"],
    resumption_status="verified"
)
```

### **Update Session Gnosis**
```bash
# Add to data/entities/researcher/session_gnosis.md
cat >> data/entities/researcher/session_gnosis.md << 'EOF'

## Resumption: 2026-07-21T11:30:00Z
- Task ID: research-local-ai-crisis-frameworks-20260721
- Context verified: true
- Next steps: Continue with data collection phase
- Failure count: 1
- Recovery count: 1

## Resumption: 2026-07-21T11:30:00Z
- Task ID: cognitive-bias-local-llm-detection-20260721
- Context verified: true
- Next steps: Continue with bias pattern analysis
- Failure count: 1
- Recovery count: 1
EOF
```

---

## 🛠️ **Complete Resumption Script (Copy-Paste Ready)**

```bash
#!/bin/bash
# kali_resume_researchers.sh — Run this to resume both tasks

echo "=== KALI: RESUMING STALLED RESEARCHER SUBAGENTS ==="

# Your task IDs (UPDATE THESE FROM YOUR SESSION GNOSIS)
TASK_1="research-local-ai-crisis-frameworks-20260721"
TASK_2="cognitive-bias-local-llm-detection-20260721"

echo "Task 1: $TASK_1"
echo "Task 2: $TASK_2"

# Resume Task 1
echo "Resuming Task 1..."
# (Run the task() call for Task 1 here)

# Resume Task 2
echo "Resuming Task 2..."
# (Run the task() call for Task 2 here)

# Verify Task 1
echo "Verifying Task 1 context..."
# (Run the VERIFY task() call for Task 1 here)

# Verify Task 2
echo "Verifying Task 2 context..."
# (Run the VERIFY task() call for Task 2 here)

# Log to Hivemind
echo "Logging to Hivemind..."
# (Run the Hivemind post_context call here)

echo "=== RESUMPTION COMPLETE ==="
```

---

## 🔧 **Troubleshooting**

### **Problem: "Task ID not found"**
```bash
# Check if task_id exists in system
omega-hub_hivemind_get_continuation(channel="opencode", entity="researcher")
```

### **Problem: Context not restored**
```bash
# Force fresh context verification
task(
    description="FORCE VERIFY: Context check",
    prompt="What do you remember from your previous work? If nothing, say 'NO CONTEXT'.",
    subagent_type="researcher",
    task_id="[YOUR_TASK_ID]"
)
```

### **Problem: Subagent says "I don't know"**
- The task_id might be wrong
- Check `session_gnosis.md` for exact task_id
- Try without task_id first to see if fresh context works

---

## 📝 **Task ID Format Reference**

### **Standard Format**
```
{domain}-{action}-{date}-{sequence}

Examples:
- research-local-ai-crisis-frameworks-20260721
- cognitive-bias-local-llm-detection-20260721
- v1-vault-legacy-mining-20260721
- search-catalogue-deep-research-20260721
```

### **Your Likely Task IDs**
Based on your current work:
1. `research-local-ai-crisis-frameworks-20260721`
2. `cognitive-bias-local-llm-detection-20260721`

---

## 🎯 **Quick Reference Card**

| Action | Command | Key Point |
|--------|---------|-----------|
| **Launch new** | `task(..., task_id="new-id")` | Always include task_id |
| **Resume failed** | `task(..., task_id="same-id")` | **SAME ID = FULL RESTORE** |
| **Verify context** | `task(prompt="Tell me what you know...", task_id="same-id")` | Mandatory after resume |
| **Log to Hivemind** | `hivemind_post_context(task_ids=[...], resumption_status="verified")` | Track all resumptions |
| **Update gnosis** | Add to `session_gnosis.md` | Audit trail |

---

## 🚨 **Golden Rules (NEVER BREAK)**

1. **ALWAYS use task_id** — No exceptions
2. **SAME task_id for resume** — Different ID = new context = lost work
3. **VERIFY after resume** — "Tell me what you know" before continuing
4. **LOG everything** — Hivemind + session_gnosis.md
5. **CHECK gnosis first** — Find exact task_ids before resuming

---

## 📞 **Emergency Contacts**

| Issue | Who to Ping | Channel |
|-------|-------------|---------|
| Task ID not working | @grokster | Hivemind |
| Context not restoring | @jem | Hivemind |
| System failure | @kali (self) | Direct |

---

## 📚 **Reference Documents**

| Document | Purpose |
|----------|---------|
| `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md` | Full protocol spec |
| `docs/strategy/HIVEMIND_POST_TEMPLATE.md` | Updated with task_ids fields |
| `AGENTS.md` | STRP section in workflow |
| `data/entities/researcher/session_gnosis.md` | Your task tracking |

---

## ✅ **Checklist for Each Resumption**

- [ ] Found exact task_id in session_gnosis.md
- [ ] Resumed with SAME task_id
- [ ] Verified context with "Tell me what you know"
- [ ] Logged to Hivemind with task_ids + resumption_status
- [ ] Updated session_gnosis.md with recovery info
- [ ] Continued work from verified checkpoint

---

*⬡ OMEGA ⬡ KALI'S RESUMPTION GUIDE ⬡ 2026-07-21 ⬡ STRP-v1.0.0 ⬡ NO MORE WASTED SUBAGENTS*