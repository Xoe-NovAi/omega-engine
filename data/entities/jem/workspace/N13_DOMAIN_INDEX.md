<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N13 arcana — Domain Index (T4)

**AP Token**: `AP-N13-DOMAIN-INDEX-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ N13-ARCANA ⬡ opencode ⬡ trc_domain_index ⬡ CONSULTABLE
**Date**: 2026-08-22 · **KB**: `N13_ARCANA_KB_20260822.md` (57KB) · **Charter**: `NODE_EXPERT_SESSIONS_PLAN.md` §4

---

## Wiring Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              OMEGA ENGINE CORE              │
                    └─────────────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────────┐
│  WAD LAYER (M2)  │          │  RUNTIME (src/)  │          │   EXTERNAL CORPUS    │
├──────────────────┤          ├──────────────────┤          ├──────────────────────┤
│ config/wads/     │          │ src/omega/oracle │          │ omega_library:       │
│  arcana_novai/   │──load──▶│  .oracle.py      │          │  mnemosyne/ (13      │
│   manifest.yaml  │  (1)     │   :24 import     │          │   spheres, DORMANT)  │
│   spheres.yaml   │          │   :232 WADLoader │          │  tarot intake/       │
│   qliphoth.yaml  │          │  .wad_loader.py  │          │   (genesis chat,     │
│   axioms.yaml    │          │   :503-514       │          │    Lilith Deck)      │
│   hierarchy.yaml │          │   IMemoryAdapter │          └──────────┬───────────┘
│   entities.yaml  │          │    validation    │                     │ future
│   vault_schema   │          └────────┬─────────┘                     ▼ (2)
└────────┬─────────┘                   │                    ┌──────────────────────┐
         │ entities via                ▼                    │ N7 MnemosyneAdapter  │
         ▼ EntityRegistry    ┌──────────────────┐           │ (NOT YET IMPLEMENTED;│
┌──────────────────┐         │ src/omega/meditate│          │  OQ-003 → N7 owns)   │
│ 13 Pillar Keepers│         │  protocol.py      │          └──────────────────────┘
│ + Sophia/Ma'at/  │         │  lens_registry.py │
│ Lilith/Jem/Iris  │         │   expects WAD     │          ┌──────────────────────┐
└──────────────────┘         │   meditate/       │          │ src/omega/astrology.py│
                             │   lenses.yaml     │◀─(3)─────│  BirthRecord, first- │
                             │   (MISSING —      │          │  breath DB+md, M1-   │
                             │   GOT-008/OQ-002) │          │  compliant           │
                             └──────────────────┘          └──────────────────────┘
```
**(1)** `oracle.py:24` imports WADLoader; `:232` instantiates with registry. **(2)** Mnemosyne corpus is external (`/media/arcana-novai/omega_library/data_archive/mnemosyne/`) — no runtime wiring until N7 adapter exists. **(3)** astrology.py feeds birth data toward Kerykeion/pyswisseph (not yet in deps — GOT-012).

## Key Files Table

| File | Role | Status |
|------|------|--------|
| `config/wads/arcana_novai/entities.yaml` | 27 entity defs incl. 13 Pillar Keepers (**NOT "pantheon.yaml"** — C-1) | WIRED |
| `config/wads/arcana_novai/spheres.yaml` | 13 spheres + entity↔sphere map + technical domains | WIRED |
| `config/wads/arcana_novai/qliphoth.yaml` | 12 shells = failure taxonomy (severity/engine_pattern/detection/recovery) | WIRED (data-layer only) |
| `config/wads/arcana_novai/{axioms,hierarchy,vault_schema}.yaml` | Five-Fold law; governance ranks; entity vault schema | WIRED |
| `config/wads/arcana_novai/tmpfzhu8kz4.tmp` | stale 41KB tmpfile | **DELETE ME** (C-2) |
| `config/wads/arcana_novai/meditate/lenses.yaml` | expected by lens_registry.py | **MISSING** (GOT-008; OQ-002 → N13 to author) |
| `src/omega/oracle/wad_loader.py` | WAD loading + IMemoryAdapter validation (:503-514) | WIRED |
| `src/omega/meditate/{protocol,lens_registry}.py` | Meditate-v1.2 + WAD-backed lens loading (**package**, not a single module — C-3) | WIRED (falls back to 6 generic lenses) |
| `src/omega/astrology.py` | First-breath tracking; SQLite + atomic md; M1 AnyIO | WIRED (cvar config prerequisite — GOT-010) |
| `/media/.../mnemosyne/*/shadow_memory.json` | 13 pristine sphere states (DORMANT, xp=0) | UNWIRED (OQ-003→N7) |

## Entry Points by Reader Intent

- **"How do I add/query esoteric correspondences?"** → KB §Deep Dig OQ-004/OQ-010 (sovereign correspondence DB schema + PD pipeline); PD-Provenance Table for sourcing rules.
- **"Why does meditation fall back to generic lenses?"** → GOT-008; fix = author `meditate/lenses.yaml` (OQ-002, N13-owned).
- **"What's the licensing boundary?"** → KB §PD-Provenance Table + W-phase W2/W3 verdicts. Hard rules: Book T c.1890s/Waite/Mathers/Papus = PD-primary; Tarotoo = MIT reference-only; Liber 777/Regardie/DuQuette = excluded; **Kerykeion = AGPL hazard** (prefer pyswisseph direct).
- **"Who owns what?"** → KB §Deep Dig 1 table: 9 N13-owned, 6 routed (N7 adapter, N4 MCP integration, N3 models/extras, N1 cvar defaults, N8 Qliphoth events).
- **"Where are the genesis documents?"** → `/media/arcana-novai/omega_library/intake/mining_queue/Omega-Early-Material/tarot/` (99KB Grok chat = methodological DNA; 20KB Lilith guide = extraction target).

## Doc Map

| Doc | Tier | Content |
|-----|------|---------|
| `N13_ARCANA_KB_20260822.md` | KB | G+A+W phases: validation, digests, PD table, gotchas, OQ resolutions, web research, source register |
| `N13_MINING_BRIEF_20260822.md` | T2 | Miner mission/output contract/source inventory |
| `N13_DOMAIN_INDEX.md` | T4 | This file — orientation & hazards |
| `N13_EXTERNAL_SOURCES.md` | T5 | Prioritized external queue |
| `data/entities/jem/proposed_lessons.yaml` | Soul | N13-001, N13-002 staged (⚠ file has pre-existing YAML defect at line 16 — N11 block indentation) |

## Hazard Register

| ID | Hazard | Severity | Mitigation |
|----|--------|----------|------------|
| HZ-N13-1 | `entities.yaml` ≠ `pantheon.yaml` — charter/G-phase misname persists in some docs | LOW | Use this index as naming SSOT (correction C-1) |
| HZ-N13-2 | Stale `tmpfzhu8kz4.tmp` (41KB) inside WAD root — non-atomic-write residue | LOW | Delete on next WAD touch (C-2) |
| HZ-N13-3 | `src/omega/meditate/` is a package (protocol+lens_registry), not one module — imports of `omega.meditate.lens_registry` must use package path | LOW | Correction C-3 |
| HZ-N13-4 | Kerykeion is AGPL-3.0 — viral license vs Apache-2.0 engine | HIGH | Route to N3 (OQ-009): prefer pyswisseph-direct or optional-extra-with-boundary |
| HZ-N13-5 | Tarotoo license inconsistency (README "CC BY 4.0" vs LICENSE MIT) | MEDIUM | Treat as MIT per LICENSE file; flag in N4 contract review (C-4) |
| HZ-N13-6 | Zenodo DOI superseded (21268290 → 21285778/21282132) | LOW | Cite new DOIs (C-5) |
| HZ-N13-7 | Astrology silently produces garbage charts if `config.location.sovereign_home.*` unset (defaults 0.0/0.0/UTC) | MEDIUM | OQ-008→N1: fail-loud requirement |
| HZ-N13-8 | vault_schema.yaml references nonexistent MnemosyneAdapter (vaporware) | HIGH | OQ-003→N7; do not build against it until implemented |
| HZ-N13-9 | proposed_lessons.yaml pre-existing YAML parse error (line 16, N11 block indent) blocks whole-file tooling | MEDIUM | Escalate to Scribe/Kali; N13 entries verified valid in isolation |
| HZ-N13-10 | gemstone-guide.md 0-byte void in corpus | LOW | DELETE per OQ-001 ruling |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: N13-ARCANA | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
