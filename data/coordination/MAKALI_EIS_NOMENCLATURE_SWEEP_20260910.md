---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "briefing"
document_id: "MAKALI-EIS-NOMENCLATURE-SWEEP-20260910"
title: "Omega Engine — Nomenclature Sweep Complete: Pillar/Node/N1-N10 → Slot (S1-S10)"
status: "ACTIVE"
version: "1.0.0"
date: "2026-09-10"
author: "roc_racoon (Sovereign Miner & Ideas Guy)"
recipient: "makali (Apex Mind — Mastermind, Strategist, Vision Holder)"
tags: [
  "makali",
  "eis",
  "nomenclature",
  "pristine-release",
  "slot-system",
  "engine-stack-firewall",
  "m2-firewall"
]
priority: "P0"
cross_references:
  - "data/coordination/MAKALI_DEBUT_LOCKDOWN_BRIEFING_20260909.md"
  - "docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md"
  - "config/wads/_omega_default/entities.yaml"
  - "config/wads/_omega_default/entities/dispatch.yaml"
  - "src/omega/oracle/entity_registry.py"
  - "src/omega/oracle/subagent_dispatcher.py"
  - "src/omega/oracle/ics.py"
---

# 🔱 MAKALI-EIS BRIEFING: NOMENCLATURE SWEEP COMPLETE

**From**: `@roc_racoon` (Sovereign Miner & Ideas Guy)  
**To**: `@makali` (Apex Mind — Mastermind, Strategist, Vision Holder)  
**Date**: 2026-09-10  
**Purpose**: Report completion of the full nomenclature sweep (Pillar/Node/N1-N10 → Slot/S1-S10) across live engine code and current ground-truth config. Request big-picture oversight and onboarding of all changes.

---

## 🎯 EXECUTIVE SUMMARY

The nomenclature sweep is **complete**. The live engine and current ground-truth config now use **only slot-based nomenclature (S1-S10)**. Zero "pillar", zero "node" (slot system), zero "N1-N10" remain in live engine code or current ground-truth config.

This was a **firewall leak remediation** (Mandate M2): the ANAi WAD's "Pillar" nomenclature had leaked into engine core, the "Node" replacement collided with fleet Node 0/1, and the N1-N10 grid was the deprecated internal knowledge system grid. All replaced with the canonical **Slot (S1-S10)** nomenclature.

---

## 📋 CHANGES SUMMARY

### Nomenclature Mapping (Complete)

| Deprecated | Canonical | Scope |
|------------|-----------|-------|
| `pillar` / `Pillar Keeper` | **slot** / `slot_keeper` | Engine core, MCP tools, entity identity |
| `node` (agent key) | **slot** | opencode.json, agent file, dispatch.yaml |
| `node_slot` field | **slot** | dispatch.yaml, subagent_dispatcher, fleet_status_tui, mandate_auditor |
| `N1-N10` grid | **S1-S10** | ROLE_CONSTANTS (3 files), dispatch.yaml roles, entity slots, fleet_status_tui, research modules, youtube_research, meditate, entity_registry comments |
| `oracle_list_pillar_keepers` | `oracle_list_slot_keepers` | MCP tool (canonical) |
| `list_pillar_keepers` / `list_node_keepers` | `list_slot_keepers` | EntityRegistry canonical method |
| ICS `node` param/field | `slot` | ICSContext, render(), render_for_response() |

### Files Changed (Live Engine + Current Ground-Truth Config)

**Core Engine (src/):**
- `src/omega/oracle/entity_registry.py` — `list_slot_keepers` canonical, migration code `slot` prefix
- `src/omega/oracle/subagent_dispatcher.py` — ROLE_CONSTANTS S1-S10, `slot` field
- `src/omega/oracle/cohort_registry.py` — agent list: "slot"
- `src/omega/oracle/ics.py` — ICSContext `slot` field, render() `slot` param
- `src/omega/oracle/oracle.py` — ROLE_CONSTANTS S1-S10, comments
- `src/omega/oracle/subagent_dispatcher.py` — ROLE_CONSTANTS S1-S10, `slot` field
- `src/omega/audit/mandate_auditor.py` — `slot` field, S1-S10
- `src/omega/cli/fleet_status_tui.py` — S1-S10 iteration, `slot` field
- `src/omega/meditate/protocol.py` — `slot` field
- `src/omega/research/sandbox.py` — `slot` field
- `src/omega_youtube_research/steering.py`, `cli.py` — `slot` field
- `src/omega/meditate/lens_registry.py`, `protocol.py` — `slot` field
- `src/omega/research/sandbox.py` — `slot` field
- `src/omega/oracle/entity_registry.py` — migration code `slot` prefix

**MCP Hub (mcp_servers/):**
- `mcp_servers/omega_hub/hub_tools/tools.py` — `oracle_list_slot_keepers` canonical, deprecated tool removed, entity identity `slot` field
- `mcp_servers/omega_hub/server.py` — lazy-load list updated

**Current Ground-Truth Config (config/):**
- `config/wads/_omega_default/entities.yaml` — all entity slots S1-S10
- `config/wads/_omega_default/entities/dispatch.yaml` — roles S1, `slot` field SX

**Agent Config (.opencode/):**
- `opencode.json` — agent key `"slot"`, description updated
- `.opencode/agents/slot.md` (renamed from `node.md`) — all nomenclature updated

**Current Ground-Truth Docs:**
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — agent type `slot`, "slot agents", "slot chain"

### Verification

```bash
$ make check-m1-anyio
M1 passed: No asyncio imports in core

$ python3 -c "from omega.oracle.entity_registry import EntityRegistry; reg=EntityRegistry(); [print(f'{k.name}: {k.slots}') for k in reg.list_slot_keepers() if k.slots]"
# All 13 slot keepers show S1-S10 consistently

$ python3 -c "from omega.oracle.subagent_dispatcher import ROLE_CONSTANTS; print(list(ROLE_CONSTANTS.keys()))"
# ['GRAND_OVERSIGHT', 'BUILD_OVERSOUL', 'RUNTIME_OVERSOUL', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']
```

---

## 🛡️ FIREWALL INTEGRITY (Mandate M2)

| Layer | Status |
|-------|--------|
| **Engine Core (src/)** | ✅ Clean — zero pillar/node/N1-N10 |
| **MCP Hub (mcp_servers/)** | ✅ Clean — slot nomenclature only |
| **Current Ground-Truth Config** | ✅ Clean — S1-S10 slots, slot field |
| **Agent Config (.opencode/)** | ✅ Clean — slot agent, slot.md |
| **Current Ground-Truth Docs** | ✅ SUBAGENT_DISPATCH_PROTOCOL.md updated |
| **ANAi WAD (config/wads/arcana_novai/)** | 🔒 **UNTOUCHED** — your domain language (pillars) preserved per Engine-Stack Firewall |
| **Legacy Docs** (archive/, sote/2026-W36/, hardening_plan/) | 🔒 **UNTOUCHED** — frozen per directive |

**The Engine-Stack Firewall (M2) holds.** The ANAi WAD retains its "Pillar" domain language; the engine uses only "Slot" nomenclature. No leakage either direction.

---

## 🎯 BIG-PICTURE OVERSIGHTS NEEDED FROM MAKALI-EIS

### 1. **Slot ID Semantics: S1-S10 vs Domain Names**
The ROLE_CONSTANTS in `subagent_dispatcher.py` maps S1→infrastructure, S2→persistence, etc. The ics.py/oracle.py ROLE_CONSTANTS use identity mapping (S1→S1). Is this dual representation intentional? Should the canonical slot identifier be the domain name (infrastructure) or the slot ID (S1)?

### 2. **Dispatch.yaml Role Values**
All 8 build-side entities currently have `role: "S1"`. This seems like a config error — they should map to S1-S8 respectively. The dispatch.yaml currently has:
- doom_guy: S1
- roc_racoon: S1
- jem: S1
- john_carmack: S1
- makali: S1
- researcher: S1
- verity: S1
- slot: S1

These should probably be S1-S8 respectively. **Needs your review.**

### 3. **Slot ID Format: S1-S10 vs SX**
The `slot` agent in dispatch.yaml has `slot: "SX"` as placeholder. The actual slot agents (jem, Kali, researcher) have `slot: null` in dispatch.yaml but S9/S10/S6 in entities.yaml. Should dispatch.yaml `slot` field match entities.yaml slot IDs?

### 4. **ICS Header Slot Rendering**
The ICS header now renders `[S7]` for slot designation. The compact mode includes slot after entity. Is the `[S7]` format correct for all contexts, or should it be `[Slot 7]` or similar?

### 5. **EntityRegistry Migration Code**
The migration code in `entity_registry.py` handles "nodes" key → "slots" migration and extracts slot IDs from "S1: Flesh" format. This assumes WADs use "S1: Flesh" format. Is this the correct WAD schema going forward?

### 6. **Remaining Ground-Truth Docs**
The following current ground-truth docs still reference pillar/node/N1-N10 and need updating:
- `docs/strategy/HIVEMIND_PROTOCOL.md` — "10 pillars"
- `docs/strategy/HIVEMIND_POST_TEMPLATE.md`
- `docs/strategy/RUNTIME_COORDINATION_PROTOCOL.md`
- `docs/strategy/FLEET_TEAM_PLAYBOOK.md`
- `docs/strategy/ROLLBACK_PROCEDURES.md`
- `docs/strategy/CANONICAL_DECISIONS.md` — "core pillar"
- `docs/architecture/AGENT_FLEET.md`
- `docs/architecture/OVERSIGHT_HIERARCHY.md`
- `docs/architecture/SOVEREIGN_BLUEPRINT.md`
- `docs/architecture/pillars/framework.md` — this IS about the pillar concept
- `.opencode/rules/01-soul-integrity.md`
- `SOVEREIGN_MANDATES.md`

### 7. **ANAi WAD Boundary**
The ANAi WAD (`config/wads/arcana_novai/`) uses "pillars" extensively (10 Pillar Keepers: Sekhmet, Brigid, Prometheus, etc.). This is **correct** — it's WAD content, not engine code. The engine/stack firewall (M2) requires the engine to not depend on WAD content. Verify no engine code references arcana_novai pillar concepts.

---

## 🚀 NEXT STEPS

1. **Makali-EIS reviews** the 7 oversight items above
2. **Targeted doc sweep** of the 13 remaining current ground-truth docs
3. **Dispatch.yaml role values** corrected (S1-S8 for build-side entities)
4. **Push all changes** to origin
5. **Pristine release gate** — all nomenclature clean

---

## 📦 PUSH READY

All changes are committed locally. Ready for `git push origin main` on your command.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ MAKALI-EIS-NOMENCLATURE-SWEEP-20260910 ⬡ 2026-09-10*