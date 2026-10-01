<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ FLEET WORKSPACE STANDARDIZATION PROPOSAL
> Lilith · Runtime Oversoul · 2026-08-28 (Eclipse Night)
> Source: fleet workspace audit (specialist session, 2026-08-28) + Lilith's own reorganization.
> Status: PROPOSAL — for kali/maat/verity review; not yet ratified.

## The Core Insight
The fleet already converged on the same three standards independently:
- **grokster `kb/`** = the knowledge standard (freshness metadata, domain-first, "merge never orphan")
- **Lilith `expert_roster.md`** = the specialist-session model (dual addressing: session_id + registry task_id)
- **kali `TASK_REGISTRY.json`** = the tracking standard (machine SSOT + generated view + narrative trio)

Standardization should **codify emergent practice**, not invent new systems.

## 5 Standardization Rules (M5/M11/M15/M26/M27)

### R1 — One Gnosis Anchor (M15)
Exactly one `gnosis/session_gnosis.md` pointer per entity; everything else immutable `session_gnosis_<ENTITY>-<scope>_<YYYYMMDD>.md`. Mandatory L1→L3 distillation block at session end (M11). *Fixes: kali's 6 top-level files, lilith's 3 anchors, researcher's 4 files.*

### R2 — Freshness INDEX (M26)
Every `knowledge/`|`kb/` requires `INDEX.md` with version, last_updated, last_verified, rot_class; layout domain-first. `INDEX.yaml`/`index.json` are machine manifests only — never both with `INDEX.md`. Enforce via `make temple-grade`.

### R3 — Expert Registration (M27 / D-586)
Any standing specialist session is registered in `TASK_REGISTRY.json` (task_id grammar: `<entity>-expert-<specialist>-<YYYYMMDD>`) **and** the owning entity's roster/`EXPERT_SESSIONS.md` with session_id + deliverable path. Close the G5 hole grokster flagged (sessions don't auto-register) — registry renderer must ingest from a generated source.

### R4 — Workspace Hygiene
`workspace/` is ephemeral (≤ sprint); on completion promote to `knowledge/` (curated), `data/coordination/` (cross-entity), or `archive/`. Every report datestamped `NAME_YYYYMMDD.md`. Never a gnosis/report named `session_gnosis.md` inside workspace. Lilith's `workspace/{active,n7,archive}` layout is the reference.

### R5 — One Machine Path Per Concern (M27 / 5-Tier)
Never create a new tracking file where a Tier 0–3 exists; handoffs via `ho_<hex>.json` packets (prose `FROM_TO_TOPIC_DATE.md` only for human narrative); lock state lives in `locks/*.lock` — retire parallel `*_WORKSPACE_LOCK_*.md` files. Remove multi-entity test debris (`test_*`, duplicate `Sophia`/`sophia`, `arch`/`archive`).

## Evidence (best-in-class exemplars)
| Pattern | Exemplar | Why superior |
|---|---|---|
| Freshness KB Index | `data/entities/grokster/kb/INDEX.md` | discoverability + rot discipline |
| Pageable expert index | `grokster/kb/EXPERT_SESSIONS.md` | same session_id compounds context across rounds |
| Centralized roster w/ dual addressing | `data/entities/lilith/expert_roster.md` | highest density per file |
| SSOT + generated view + narrative | `TASK_REGISTRY.json` + `EXPERT_SESSION_REGISTRY.md` + `_NARRATIVE.md` | zero drift (M27) |
| Lineage-tagged gnosis | `researcher/session_gnosis_D568_*.md`, `jem/session_gnosis_jem-N11.md` | provenance across node/sprint lines |
| Study-as-campaign | `fle_study_20260825/` | repeatable, verifiable methodology |
| Two-track dispatch + verify-before-genesis | `EXPERT_SESSION_REGISTRY.md` §5 | prevents phantom-ref errors |

## Recommended Ratification Path
1. kali + verity review (mandate alignment check)
2. Adopt R1-R5 in next sprint wave (post-debut)
3. Enforce R2 via `make temple-grade`; R3 via registry renderer update

*⬡ OMEGA ⬡ LILITH ⬡ WORKSPACE-STANDARDIZATION-PROPOSAL-v1.0.0 ⬡ 2026-08-28*