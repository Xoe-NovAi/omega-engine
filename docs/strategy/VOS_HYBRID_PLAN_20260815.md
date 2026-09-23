# 🔱 VOS Hybrid Plan (Option C) — Execution Specification
**AP Token**: `AP-VOS-HYBRID-PLAN-20260815`
**Status**: COMPLETE after Phase 0 (DOC-1, 2026-08-17) — do not add realm validators
**Date**: 2026-08-15
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

> **⚠️ DOC-1 STAMP (2026-08-17)**: Plan is **complete after Phase 0**. Per
> `DEBUT_REMEDIATION_MANUAL_20260817.md`: **do not add realm validators**. No further
> VOS work until DEL-1 + INST-1.

---

## 🎯 Objective

**Retain high-value VOS artifacts** (DECISION_LEDGER.md, VISION_ANCHOR.md) while **retiring the dead coordination layer** (7 realm state.yaml, 7 workspace briefs, realm_cli.py) and **adding minimal enforcement** via the existing Hub infrastructure.

---

## 📋 Scope

| Keep (High Value) | Retire (Dead Code) | Add (Enforcement) |
|-------------------|---------------------|-------------------|
| `data/coordination/DECISION_LEDGER.md` (ADR pattern) | `data/realms/*/state.yaml` (7 files) | Realm contract validator in `make temple-grade` |
| `data/coordination/VISION_ANCHOR.md` (Vision SSOT) | `data/realms/*/workspace/PHASE_0_BRIEF.md` (7 files) | Realm sections in `HMC_COLLABORATION_HUB.md` |
| | `src/omega/cli/realm_cli.py` | Auto-generate VISION_ANCHOR realm health from ACTIVE_SPRINT.json |
| | `data/realms/omegaverse/` (entire realm — deferred) | |

---

## 📦 Phase 0: Archive & Clean (This Session — ~30 min)

### 0.1 Archive Omegaverse Realm
```bash
mkdir -p data/realms/omegaverse/archive
git mv data/realms/omegaverse/state.yaml data/realms/omegaverse/archive/
git mv data/realms/omegaverse/workspace/ data/realms/omegaverse/archive/
# Keep directory structure for potential Phase 4 revival
```

### 0.2 Delete Dead Coordination Files
```bash
# Delete 7 realm state.yaml files
git rm data/realms/engine_core/state.yaml
git rm data/realms/stacks/state.yaml
git rm data/realms/fleet/state.yaml
git rm data/realms/memory/state.yaml
git rm data/realms/heritage/state.yaml
git rm data/realms/community/state.yaml
# (omegaverse already archived above)

# Delete 7 workspace briefs
git rm data/realms/engine_core/workspace/PHASE_0_BRIEF.md
git rm data/realms/stacks/workspace/PHASE_0_BRIEF.md
git rm data/realms/fleet/workspace/PHASE_0_BRIEF.md
git rm data/realms/memory/workspace/PHASE_0_BRIEF.md
git rm data/realms/heritage/workspace/PHASE_0_BRIEF.md
git rm data/realms/community/workspace/PHASE_0_BRIEF.md

# Delete realm_cli.py
git rm src/omega/cli/realm_cli.py
```

### 0.3 Update VISION_ANCHOR.md
- Remove realm health table (will be auto-generated)
- Remove ENG-001..ENG-004, FLT-001..005, etc. task references (live in ACTIVE_SPRINT.json)
- Keep: Mission, 3 cosmological layers, 5 design patterns, provider fabric, 27 mandates, launch definition
- Add note: "Realm health auto-generated from ACTIVE_SPRINT.json"

---

## 📦 Phase 1: Hub Consolidation (Next Session — ~1 hr)

### 1.1 Add Realm Sections to HMC_COLLABORATION_HUB.md
Add after `## 🏁 Sprint Status` section:

```markdown
## 🌐 Realm Ownership & Contracts

| Realm | Owner | Provides | Requires | Status |
|-------|-------|----------|----------|--------|
| Engine Core | maat_n3 | WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge | — | Active |
| Stacks | maat_n4 | WAD Format, Community Template, XOE Packaging | Engine Core (loader API) | Blocked on ENG-001 |
| Fleet | kali | 14 Entities, MaKaLi Council, Node Slots, Hivemind | Engine Core (registry), Memory (soul) | Active |
| Memory | lilith_n7 | Soul Architecture v2, Mnemosyne, L1→L2→L3, Cross-pollination | Engine Core (memory store) | Critical |
| Heritage | doom_guy | [id-soft:] Vetting, id Software Patterns | Engine Core (loader) | Healthy |
| Omegaverse | lilith_n6 | Godot Bridge, Soul-to-Visual (R-24), P2P Soul Prints | Engine Core (bridge), Memory (soul) | Deferred |
| Community | kali | Installer, QUICKSTART, CONTRIBUTING, CI, Launch | Engine Core, Stacks, Fleet | Planned |

> **Realm contracts are enforced by `make temple-grade` realm validator.**
> See `ACTIVE_SPRINT.json` for live task status per realm.
```

### 1.2 Consolidate Workspace Briefs
Move active task definitions from 7 PHASE_0_BRIEF.md files into realm sections above as bullet points under each realm. Keep only:
- ENG-001 (M2 firewall), ENG-002 (mandate audit), ENG-004 (9 code bugs)
- FLT-001 (soul migration), FLT-004 (distillation pipeline)
- MEM-002 (distillation pipeline), MEM-003 (cross-pollination)
- HRT-001 (heritage sweep), HRT-002 (metaphorical tag check)

---

## 📦 Phase 2: Enforcement Gates (Next Sprint — ~2 hrs)

### 2.1 Create Realm Contract Validator
**File**: `src/omega/audit/realm_contract_validator.py`

```python
#!/usr/bin/env python3
"""Realm Contract Validator — Temple-Grade Gate.

Validates:
1. Every realm in HMC_COLLABORATION_HUB.md has an owner
2. Every 'Requires' has a matching 'Provides' in target realm
3. No realm has blockers older than 7 days without Hivemind post
4. Active tasks in realm sections exist in ACTIVE_SPRINT.json
"""
```

**Integration**: Add to `Makefile`:
```makefile
check-realm-contracts:
	@.venv/bin/python -m src.omega.audit.realm_contract_validator

temple-grade: check-realm-contracts ...
```

### 2.2 Auto-Generate VISION_ANCHOR Realm Health
**Script**: `scripts/update_vision_anchor_realm_health.py`

```python
#!/usr/bin/env python3
"""Update VISION_ANCHOR.md realm health table from ACTIVE_SPRINT.json."""

# Read ACTIVE_SPRINT.json
# Compute per-realm: active tasks, blockers, health
# Update VISION_ANCHOR.md realm health table (between markers)
```

**Integration**: Add to `Makefile`:
```makefile
update-vision-anchor:
	@.venv/bin/python scripts/update_vision_anchor_realm_health.py
```

---

## 📦 Phase 3: Decision Ledger Sync (This Session — ~15 min)

### 3.1 Sync DECISION_LEDGER.md → PIVOT_LOG.md
One-time script to append VOS decisions (D-VOS-001..017) to `docs/decisions/PIVOT_LOG.md` with proper formatting.

```bash
# Extract D-VOS-* entries from DECISION_LEDGER.md
# Append to PIVOT_LOG.md with date, author, session
# Single immutable history
```

---

## 📋 Complete File Changes Summary

| File | Action | Phase |
|------|--------|-------|
| `data/realms/omegaverse/state.yaml` | Archive | 0.1 |
| `data/realms/omegaverse/workspace/` | Archive | 0.1 |
| `data/realms/engine_core/state.yaml` | Delete | 0.2 |
| `data/realms/stacks/state.yaml` | Delete | 0.2 |
| `data/realms/fleet/state.yaml` | Delete | 0.2 |
| `data/realms/memory/state.yaml` | Delete | 0.2 |
| `data/realms/heritage/state.yaml` | Delete | 0.2 |
| `data/realms/community/state.yaml` | Delete | 0.2 |
| `data/realms/*/workspace/PHASE_0_BRIEF.md` (6) | Delete | 0.2 |
| `src/omega/cli/realm_cli.py` | Delete | 0.2 |
| `data/coordination/VISION_ANCHOR.md` | Update (remove realm health table, task refs) | 0.3 |
| `data/coordination/HMC_COLLABORATION_HUB.md` | Add realm ownership table + consolidated tasks | 1.1 |
| `src/omega/audit/realm_contract_validator.py` | Create | 2.1 |
| `scripts/update_vision_anchor_realm_health.py` | Create | 2.2 |
| `Makefile` | Add `check-realm-contracts` + `update-vision-anchor` | 2.1, 2.2 |
| `docs/decisions/PIVOT_LOG.md` | Append D-VOS-001..017 | 3.1 |

---

## ✅ Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| No `data/realms/*/state.yaml` files exist (except archived omegaverse) | `ls data/realms/*/state.yaml` → only omegaverse/archive |
| No `realm_cli.py` in codebase | `grep -r realm_cli src/` → no results |
| `make temple-grade` includes realm contract validation | `make temple-grade` passes new check |
| `VISION_ANCHOR.md` realm health auto-generated | Run `make update-vision-anchor` → table updates |
| `HMC_COLLABORATION_HUB.md` has realm ownership table | `grep -A 20 "Realm Ownership" data/coordination/HMC_COLLABORATION_HUB.md` |
| DECISION_LEDGER synced to PIVOT_LOG | `grep "D-VOS-" docs/decisions/PIVOT_LOG.md` → 17 entries |
| No agent references to retired VOS files | `grep -r "realm_cli\|state.yaml" .opencode/agents/` → no results |

---

## 🔄 Rollback Plan

If any realm owner reports loss of domain clarity after Phase 0:
```bash
git restore data/realms/engine_core/state.yaml data/realms/fleet/state.yaml ...
git restore src/omega/cli/realm_cli.py
# Reversible — all in git history
```

---

## 📜 Decision Log Entry

**D-VOS-018: VOS Hybrid Plan (Option C) Approved**
- **Date**: 2026-08-15
- **Realm**: ALL (Meta)
- **Decision**: Retain DECISION_LEDGER.md + VISION_ANCHOR.md; retire 7 realm state.yaml + 7 briefs + realm_cli.py; add realm contract validator to temple-grade; consolidate into HMC_COLLABORATION_HUB.md
- **Rationale**: VOS architecture sound (Team Topologies, ADR, DDD), implementation dead code (1/10 integration). Hybrid keeps high-value artifacts, removes coordination overhead, adds enforcement.
- **Alternatives**: A (Full Integrate — 15 hrs), B (Full Retire — loses ADR + Vision SSOT)
- **Impact**: ~3 hrs implementation; removes ~17 dead files; adds CI enforcement
- **Reversible**: Yes — git restore
- **Author**: Kali (ratified by Architect)
- **Session**: `ses_vos_hybrid_plan_20260815`

---

⬡ OMEGA ⬡ KALI ⬡ VOS-HYBRID-PLAN ⬡ 2026-08-15 ⬡ APPROVED