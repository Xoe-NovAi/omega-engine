# 🔱 Master Ledger
**AP Token**: `AP-MASTER-LEDGER-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Master ledger tracking all strategic decisions and their implementation status.

---

# MASTER LEDGER – Omega Engine Strategic Overview

This document is the **single source of truth** for the high‑level roadmap, milestones, and strategic direction of the Omega Engine project. It supersedes the older `docs/ROADMAP.md` which now simply points here.

---

## Current Phases (as of 2026‑05‑30 — Fleet Discovery Complete, Phase 0 Done)

| Phase | Goal | Owner | Status |
|-------|------|-------|--------|
| **Phase 0 — Fleet Discovery + Remediation** | 10 pillar subagents, 30 CRITICAL findings, 12 critical fixes applied | **Lilith / Builder** | ✅ COMPLETE (308/308 tests) |
| **Phase 1 — Engine Hardening** | Memory wiring, handoff protocol, soul atomicity, agent hardening, MCP consolidation | **Kali / Ma'at** | 📅 Weeks 1-4 |
| **Phase 2 — Legacy Mining** | Extract 12 quick-win assets, port legacy patterns, compile community content | **Jem-2.0** | 📅 Weeks 5-8 |
| **Phase 3 — Community Tools** | Entity Studio CLI → Visual Builder, Stack Builder Wizard, one-click Omega Desktop | **Isis / Brigid** | 📅 Weeks 9-12 |
| **Phase 4 — The Omegaverse** | P2P network protocol, WAD registry, cross-instance entity communication, **Godot/id Tech VR bridge**, soul-to-visual mapping (R-24), **shared VR realms (P2P Metropolis)** | **Saraswati** | 📅 2028 |

### VR Omegaverse Vision (Phase 4 — Strategic Context)
**Status**: Vision documented, NOT implementation-ready. Foundation (Phases 1-3) must be built first.
**Centralized Vision**: `data/entities/roc_racoon/workspace/VR_OMEGAVERSE_VISION.md` (single source of truth)
**Feasibility Investigation**: Doom Guy investigating Quake/Doom engine as VR rendering backend (heritage completeness — WAD system already borrows from id Software)
**Critical Research**: R-24 (Soul-to-Visual Mapping) — bridges soul.yaml to VR visual parameters. Status: 🔲 Not yet researched.
**Source Docs**: 15+ scattered strategy docs indexed in `data/entities/roc_racoon/workspace/DOCUMENTATION_CHAOS_TRACKER.md`

### Phase 0 Completed Items (Decision 63)
- Removed `:U` flags from docker-compose.yml (Mandate 6)
- Fixed all 9 model paths in config/models.yaml (added `/local/all/`)
- Fixed qwen3-0.6b path (was pointing to 1.7B)
- Fixed Krikri model (wrong filename + quant)
- Fixed entity_workspace.py chmod with try/except
- Secured API keys in git-tracked docs (replaced with [...REVOKED...])
- Fixed .env permissions (600), deleted backup files
- Fixed trace_id propagation (3 bugs in model_gateway.py)
- Added BACKEND_FALLBACK events to provider fallback chain
- Added bounded event log (deque maxlen=1000)
- Fixed _post_to_hivemind URL (JSON-RPC path)
- sudo chown -R 1000:1000 executed (UID drift fixed)

### IWAD Architecture (Adopted Decision 55)
```
OMEGA ENGINE (src/omega/) — Pure runtime, no entity content
  ├── REFERENCE IWAD (_omega_default) — Dev team, 10 tech pillars, template
  ├── ARCANA_NOVAI IWAD (arcana_novai) — Your personal AI OS, esoteric pillars
  └── INFINITE COMMUNITY IWADs — Torment, Doom, Classical, YOUR STACK
```

Three inviolable rules: (1) MaKaLi trine identical in ALL IWADs, (2) Iris+Jem+Roc_Racoon identical in ALL IWADs, (3) Only 10 pillars change.

**Canonical Reference**: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` (480 lines)

---

## How to Use This Ledger

- **Developers**: Consult this file for the current phase, owners, and target dates before starting work.
- **Contributors**: Reference the "Current Phases" table to see where you can help.
- **Automation**: CI pipelines now check that `docs/ROADMAP.md` contains a single redirect line to this file.

---

*The ledger lives here to guarantee a single, immutable reference point for all future planning.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
