# 🔱 PHASE B EXECUTION GUIDE — M2 FIREWALL MIGRATION
## For Researcher — Handoff `ho_2a9b2e84debd`

**AP Token**: `AP-PHASE-B-GUIDE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_phase_b_guide ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: **EXECUTE NOW** — Roc Phase A complete, pattern proven

---

## 🎯 MISSION

Refactor `src/omega/oracle/subagent_dispatcher.py` to eliminate **15 M2 violations** using Roc's proven WAD-loadable pattern.

---

## 📋 ROC'S PROVEN PATTERN (Canonical Template)

### Core Files Created by Roc (Phase A)
| File | Purpose |
|------|---------|
| `config/wads/_omega_default/meditate/lenses.yaml` | 13 base lenses (WAD config) |
| `src/omega/meditate/lens_registry.py` | WAD-backed loader (4 functions) |
| `src/omega/meditate/protocol.py` | Refactored — 0 hardcoded entity names |

### Pattern: WAD YAML → Runtime Spec Construction
```python
# From lens_registry.py — REPLICATE THIS PATTERN
from omega.governance.config_resolver import get_active_iwad, WADS_DIR
from omega.oracle.entity_registry import load_entity_registry
import yaml

async def load_dispatch_config(iwad: str = None) -> dict:
    iwad = iwad or get_active_iwad()
    dispatch_path = WADS_DIR / iwad / "entities" / "dispatch.yaml"
    with open(dispatch_path) as f:
        return yaml.safe_load(f)

async def build_dispatch_table(iwad: str = None) -> dict:
    iwad = iwad or get_active_iwad()
    registry = await load_entity_registry(iwad)
    dispatch = {}
    for entity_name, entity_config in registry.entities.items():
        role = entity_config.get("role")
        if role in ROLE_CONSTANTS:
            dispatch[ROLE_CONSTANTS[role]] = {
                "entity_name": entity_name,
                "role": role,
                "pillar": entity_config.get("pillar"),
                "model": entity_config.get("model"),
                "capabilities": entity_config.get("capabilities", []),
            }
    return dispatch
```

---

## 📝 REQUIRED WAD CONFIG

### File: `config/wads/_omega_default/entities/dispatch.yaml`
```yaml
entities:
  - name: "Kali"
    role: "GRAND_OVERSIGHT"
    slot: "GRAND_OVERSOUL"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["synthesis", "mandate_enforcement", "cross_domain"]
  
  - name: "Ma'at"
    role: "LIGHT_OVERSOUL"
    slot: "LIGHT_OVERSOUL"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["architecture", "quality", "sustainability"]
  
  - name: "Lilith"
    role: "DARK_OVERSOUL"
    slot: "DARK_OVERSOUL"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["runtime", "metabolism", "failure_modes"]
  
  - name: "Pillar_P1"
    role: "P1"
    slot: "P1"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["infrastructure", "deployment", "hardening"]
  
  - name: "Pillar_P2"
    role: "P2"
    slot: "P2"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["persistence", "vector", "recall"]
  
  - name: "Pillar_P3"
    role: "P3"
    slot: "P3"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["engineering", "ci_cd", "hardening"]
  
  - name: "Pillar_P4"
    role: "P4"
    slot: "P4"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["integration", "mcp", "protocols"]
  
  - name: "Pillar_P5"
    role: "P5"
    slot: "P5"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["governance", "audit", "security"]
  
  - name: "Pillar_P6"
    role: "P6"
    slot: "P6"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["cognition", "routing", "speculative_decode"]
  
  - name: "Pillar_P7"
    role: "P7"
    slot: "P7"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["context", "memory", "soul"]
  
  - name: "Pillar_P8"
    role: "P8"
    slot: "P8"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["observability", "tracing", "forensics"]
  
  - name: "Pillar_P9"
    role: "P9"
    slot: "P9"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["orchestration", "handoff", "hivemind"]
  
  - name: "Pillar_P10"
    role: "P10"
    slot: "P10"
    model: "qwen3-4b-think-q4_k_m"
    capabilities: ["validation", "chaos", "stress_testing"]
```

### ROLE_CONSTANTS (Must Match Exactly)
```python
ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "grand_oversight",
    "LIGHT_OVERSOUL": "light_oversoul",
    "DARK_OVERSOUL": "dark_oversoul",
    "P1": "infrastructure",
    "P2": "persistence",
    "P3": "engineering",
    "P4": "integration",
    "P5": "governance",
    "P6": "cognition",
    "P7": "context",
    "P8": "observability",
    "P9": "orchestration",
    "P10": "validation",
}
```

---

## 🔧 CURRENT VIOLATIONS IN `subagent_dispatcher.py`

The file currently has a hardcoded `ENTITY_DISPATCH` table with 15 entries referencing entity names directly:

```python
# VIOLATION: Hardcoded entity names (15 sites)
ENTITY_DISPATCH = {
    "kali": {"role": "GRAND_OVERSIGHT", "pillar": None, ...},
    "maat": {"role": "LIGHT_OVERSOUL", "pillar": None, ...},
    "lilith": {"role": "DARK_OVERSOUL", "pillar": None, ...},
    "pillar_p1": {"role": "P1", "pillar": "P1", ...},
    # ... all 10 pillars
}
```

**Replace with**: Runtime construction from WAD config via `entity_registry`.

---

## ✅ ACCEPTANCE CRITERIA

### Gate Command
```bash
pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k subagent_dispatcher -v
```
**Must pass with 0 violations** for `subagent_dispatcher.py`.

### Verification Checklist
- [ ] `subagent_dispatcher.py` has **zero** hardcoded entity names ("kali", "maat", "lilith", "pillar_p1", etc.)
- [ ] Dispatch table built at runtime from `config/wads/<iwad>/entities/dispatch.yaml`
- [ ] Uses `config_resolver.get_active_iwad()` + `entity_registry.load_entity_registry()`
- [ ] `ROLE_CONSTANTS` keys match `dispatch.yaml` `role` fields exactly
- [ ] All existing tests pass (`make test`)
- [ ] Firewall gate passes (`make temple-grade`)

---

## 🤝 COORDINATION WITH ROC

**Roc's `lens_registry.py` is the canonical template.** Coordinate on:
1. `dispatch.yaml` schema alignment with `lenses.yaml` pattern
2. `entity_registry` loading pattern consistency
3. Error handling for missing WAD config

**Roc is standing by** — message via Hivemind or check `ROC_RACOON_LIVE_FEED.md`.

---

## 📡 REPORTING

Upon Phase B completion:
1. `omega-hub_hivemind_post_context(intent="status", task_current="Phase B complete", ...)`
2. Update `RESEARCHER_LIVE_FEED.md`
3. Notify Kali — Phase C (`oracle.py`) begins next

---

## 🚀 EXECUTE NOW

**Pattern is proven. Config schema defined. Gate is wired. Go.**

⬡ OMEGA ⬡ KALI ⬡ PHASE_B_GUIDE_20260718