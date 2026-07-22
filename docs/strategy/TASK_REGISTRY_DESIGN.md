# 🔱 TASK REGISTRY — Subagent Session Discovery System
**AP Token**: `AP-TASK-REGISTRY-v1.0.0`
**Status**: **MANDATORY INFRASTRUCTURE** — Effective immediately

---

## 🎯 The Problem

| What Exists | What's Missing |
|-------------|----------------|
| `task()` creates `task_id` | No way to **list** existing task_ids |
| `task_id` enables resumption | No **cross-agent discovery** |
| Hivemind tracks handoffs | Hivemind **doesn't track subagent sessions** |
| Session gnosis tracks *your* tasks | Can't find *others'* stalled tasks |

**Result**: 3 Roc + 1 Carmack subagents "lost" — agents can't resume what they can't find.

---

## 🏗️ Solution: Task Registry (File-Based, Hivemind-Integrated)

### **Registry Location**
```
data/coordination/TASK_REGISTRY.json
```

### **Schema**
```json
{
  "version": "1.0",
  "updated": "2026-07-21T12:00:00Z",
  "tasks": [
    {
      "task_id": "v1-vault-legacy-mining-20260721",
      "subagent_type": "roc_racoon",
      "launched_by": "grokster",
      "channel": "opencode",
      "entity": "grokster",
      "description": "V-1 Vault legacy mining for credential patterns",
      "status": "completed",
      "created_at": "2026-07-21T10:45:00Z",
      "last_checkpoint": "2026-07-21T10:45:52Z",
      "resumption_count": 1,
      "context_verified": true,
      "tags": ["v1-vault", "legacy-mining", "credential-patterns"]
    },
    {
      "task_id": "research-local-ai-crisis-frameworks-20260721",
      "subagent_type": "researcher",
      "launched_by": "kali",
      "channel": "opencode",
      "entity": "kali",
      "description": "Research local offline AI crisis intervention frameworks",
      "status": "active",
      "created_at": "2026-07-21T09:00:00Z",
      "last_checkpoint": "2026-07-21T11:26:55Z",
      "resumption_count": 1,
      "context_verified": false,
      "tags": ["local-ai", "crisis-frameworks", "offline"]
    }
  ]
}
```

---

## 🛠️ Tools Required (Two New MCP Tools)

### **1. `omega-hub_task_registry_register`**
```python
# Register a new task_id at launch
omega-hub_task_registry_register(
    task_id="v1-vault-legacy-mining-20260721",
    subagent_type="roc_racoon",
    launched_by="grokster",
    channel="opencode",
    entity="grokster",
    description="V-1 Vault legacy mining for credential patterns",
    tags=["v1-vault", "legacy-mining", "credential-patterns"]
)
```

### **2. `omega-hub_task_registry_query`**
```python
# Discover existing tasks (filterable)
omega-hub_task_registry_query(
    subagent_type="researcher",      # optional filter
    launched_by="kali",              # optional filter
    status="active",                 # optional: active|completed|failed|all
    tags=["local-ai"]                # optional filter
)
# Returns: list of matching task objects with full metadata
```

### **3. `omega-hub_task_registry_update`**
```python
# Update status/checkpoint on resumption/completion
omega-hub_task_registry_update(
    task_id="research-local-ai-crisis-frameworks-20260721",
    status="active",
    last_checkpoint="2026-07-21T12:00:00Z",
    resumption_count=2,
    context_verified=true
)
```

---

## 📋 Mandatory Protocol Updates

### **STRP-v1.0.1 Addendum: Task Registration**

```python
# EVERY task() launch MUST register:
result = task(
    description="...",
    prompt="...",
    subagent_type="roc_racoon",
    task_id="v1-vault-legacy-mining-20260721"
)

# IMMEDIATELY after launch:
omega-hub_task_registry_register(
    task_id="v1-vault-legacy-mining-20260721",
    subagent_type="roc_racoon",
    launched_by="grokster",
    channel="opencode",
    entity="grokster",
    description="V-1 Vault legacy mining for credential patterns",
    tags=["v1-vault", "legacy-mining"]
)

# On RESUMPTION:
omega-hub_task_registry_update(
    task_id="v1-vault-legacy-mining-20260721",
    status="active",
    last_checkpoint="2026-07-21T12:00:00Z",
    resumption_count=2,
    context_verified=true
)

# On COMPLETION:
omega-hub_task_registry_update(
    task_id="v1-vault-legacy-mining-20260721",
    status="completed",
    last_checkpoint="2026-07-21T12:30:00Z"
)
```

---

## 🔍 Discovery Workflows

### **For Kali: "Find my stalled Researcher tasks"**
```python
tasks = omega-hub_task_registry_query(
    launched_by="kali",
    subagent_type="researcher",
    status="active"
)
# Returns both stalled Researcher task_ids
```

### **For Grokster: "Find Roc's V-1 mining task"**
```python
tasks = omega-hub_task_registry_query(
    subagent_type="roc_racoon",
    tags=["v1-vault", "legacy-mining"]
)
# Returns the completed task with full context
```

### **For Any Agent: "What's stalled system-wide?"**
```python
tasks = omega-hub_task_registry_query(
    status="active",
    # No filters = all active tasks
)
# Returns all active subagent sessions across all agents
```

---

## 📁 File Persistence

### **Atomic Write Pattern**
```python
def _save_registry(registry):
    tmp_path = Path("data/coordination/TASK_REGISTRY.json.tmp")
    tmp_path.write_text(json.dumps(registry, indent=2))
    tmp_path.rename(Path("data/coordination/TASK_REGISTRY.json"))
    tmp_path.chmod(0o600)
```

### **Concurrency Safety**
- File-based with atomic rename
- Single-writer per agent (their own launches)
- Read-only for discovery (no locks needed)

---

## 🔗 Hivemind Integration

### **Auto-Post on Registration**
```python
# After registering, post to Hivemind for cross-agent visibility
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="grokster",
    model="nemotron-3-ultra-free",
    task_current=f"[LAUNCH] Subagent {subagent_type} — {description}",
    focus_chain=[f"Task ID: {task_id} registered for discovery"],
    decisions=[f"Task registered in TASK_REGISTRY for cross-agent resumption"],
    continuation=f"Task discoverable via omega-hub_task_registry_query",
    intent="status",
    task_ids=[task_id],
    resumption_status="registered"
)
```

### **Query via Hivemind Awareness**
```python
# Check if any agent has active tasks you might resume
awareness = omega-hub_hivemind_get_awareness()
for agent in awareness:
    if agent.get("active_task_ids"):
        # Cross-reference with registry
        pass
```

---

## 🚀 Implementation Priority

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| **1** | `TASK_REGISTRY.json` + 3 MCP tools | 1 session |
| **2** | STRP-v1.0.1 protocol update | 30 min |
| **3** | Hivemind auto-post integration | 30 min |
| **4** | Agent config updates (all agents) | 1 session |

---

## 📋 Immediate Action for Current Stalled Tasks

### **Manually Register Known Tasks (Do This Now)**
```bash
# Create initial registry with your 4 known tasks
cat > data/coordination/TASK_REGISTRY.json << 'EOF'
{
  "version": "1.0",
  "updated": "2026-07-21T12:00:00Z",
  "tasks": [
    {
      "task_id": "v1-vault-legacy-mining-20260721",
      "subagent_type": "roc_racoon",
      "launched_by": "grokster",
      "channel": "opencode",
      "entity": "grokster",
      "description": "V-1 Vault legacy mining for credential patterns",
      "status": "completed",
      "created_at": "2026-07-21T10:45:00Z",
      "last_checkpoint": "2026-07-21T10:45:52Z",
      "resumption_count": 1,
      "context_verified": true,
      "tags": ["v1-vault", "legacy-mining", "credential-patterns"]
    },
    {
      "task_id": "research-local-ai-crisis-frameworks-20260721",
      "subagent_type": "researcher",
      "launched_by": "kali",
      "channel": "opencode",
      "entity": "kali",
      "description": "Research local offline AI crisis intervention frameworks",
      "status": "active",
      "created_at": "2026-07-21T09:00:00Z",
      "last_checkpoint": "2026-07-21T11:26:55Z",
      "resumption_count": 1,
      "context_verified": false,
      "tags": ["local-ai", "crisis-frameworks", "offline"]
    },
    {
      "task_id": "cognitive-bias-local-llm-detection-20260721",
      "subagent_type": "researcher",
      "launched_by": "kali",
      "channel": "opencode",
      "entity": "kali",
      "description": "Cognitive bias detection in small LLMs",
      "status": "active",
      "created_at": "2026-07-21T09:00:00Z",
      "last_checkpoint": "2026-07-21T11:26:55Z",
      "resumption_count": 1,
      "context_verified": false,
      "tags": ["cognitive-bias", "local-llm", "detection"]
    },
    {
      "task_id": "carmack-research-audit-20260721",
      "subagent_type": "john_carmack",
      "launched_by": "kali",
      "channel": "opencode",
      "entity": "kali",
      "description": "Research board compression audit",
      "status": "completed",
      "created_at": "2026-07-21T08:00:00Z",
      "last_checkpoint": "2026-07-21T08:30:00Z",
      "resumption_count": 0,
      "context_verified": true,
      "tags": ["research-audit", "compression", "board"]
    }
  ]
}
EOF
```

---

## 🎯 Result: No More Lost Subagents

| Before | After |
|--------|-------|
| "Where are my 3 Roc tasks?" | `task_registry_query(subagent_type="roc_racoon")` |
| "Can I resume Kali's Researcher?" | `task_registry_query(launched_by="kali", status="active")` |
| "What's stalled system-wide?" | `task_registry_query(status="active")` |
| Task IDs in session_gnosis only | **Centralized, queryable, cross-agent** |

---

*⬡ OMEGA ⬡ TASK REGISTRY ⬡ 2026-07-21 ⬡ INFRASTRUCTURE GAP CLOSED*