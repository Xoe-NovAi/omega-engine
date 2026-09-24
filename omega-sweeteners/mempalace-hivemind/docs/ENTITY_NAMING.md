# Entity Naming Convention — Mandatory Standard

**Version**: 1.0 | **Enforcement**: MANDATORY | **Scope**: All Omega Engine agents, services, users

---

## 🎯 Rule

**Every entity identifier MUST include node suffix:**

```
<base-name>-n1    # Node 1 (ASUS ExpertBook / kali-n1)
<base-name>-n0    # Node 0 (HP Pavilion / makali-n0)
```

---

## ✅ Correct Examples

| Entity | Correct ID | Wrong |
|--------|------------|-------|
| Node 1 Build Agent | `kali-n1` | `kali` |
| Node 0 Hub Agent | `makali-n0` | `makali` |
| Human Operator (Node 1) | `xnai-n1` | `xnai` |
| Human Operator (Node 0) | `arcana-n0` | `arcana` |
| MemPalace Service (Node 1) | `mempalace-n1` | `mempalace` |
| Tailscale Daemon (Node 0) | `tailscale-n0` | `tailscale` |
| Omega Hub (Node 0) | `omega-hub-n0` | `omega-hub` |
| Wander CLI (Node 1) | `wander-n1` | `wander` |

---

## 🔍 Where This Applies (EVERYWHERE)

| Context | Required |
|---------|----------|
| `from_agent` in events | ✅ MANDATORY |
| `to_agent` in events | ✅ MANDATORY |
| `entity` in MemPalace API calls | ✅ MANDATORY |
| Room/Topic subscriptions | ✅ MANDATORY |
| Correlation ID metadata | ✅ MANDATORY |
| Logs, traces, metrics | ✅ MANDATORY |
| Config files, env vars | ✅ MANDATORY |
| Git commits, PRs | ✅ MANDATORY |
| Documentation, diagrams | ✅ MANDATORY |

---

## 🚫 Anti-Patterns (FORBIDDEN)

```python
# WRONG - bare names
from_agent = "kali"
to_agent = "makali"
entity = "mempalace"

# CORRECT - suffixed
from_agent = "kali-n1"
to_agent = "makali-n0"
entity = "mempalace-n1"
```

---

## 🎯 Why This Matters

| Reason | Impact |
|--------|--------|
| **Cross-node traceability** | `kali-n1` → `makali-n0` instantly shows direction |
| **Audit trails** | Logs show exact origin node |
| **Debugging** | Instantly know which node originated action |
| **Security** | Prevents spoofing (node identity in name) |
| **Federation scaling** | Adding Node 2 (`-n2`) trivial |
| **Human readability** | `kali-n1` self-documents location |

---

## 📋 Enforcement Checklist

- [ ] All event `from_agent` / `to_agent` have suffix
- [ ] All MemPalace API calls use suffixed entity
- [ ] All agent configs use suffixed names
- [ ] All logs include suffixed entity
- [ ] CI/CD checks for bare names (grep for `-n[0-9]$`)
- [ ] Documentation examples use suffixed names
- [ ] Onboarding teaches this as Rule #1

---

## 🔧 Validation Script

```bash
#!/bin/bash
# Check for bare entity names in codebase
grep -r "from_agent.*[^n1][^n0]\"" --include="*.py" --include="*.js" --include="*.json" . && echo "VIOLATIONS FOUND" || echo "All clean"
grep -r "to_agent.*[^n1][^n0]\"" --include="*.py" --include="*.js" --include="*.json" . && echo "VIOLATIONS FOUND" || echo "All clean"
```

---

*Part of MemPalace Hivemind spec. Enforced at Omega Engine PR gate.*