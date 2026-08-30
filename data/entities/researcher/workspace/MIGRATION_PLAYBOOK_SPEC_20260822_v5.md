---
schema_version: "1.0"
document_type: "protocol"
document_id: "migration-playbook-2026-08-22"
title: "Omega Engine Breaking-Change Migration Playbook"
status: "DRAFT"
version: "5.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "deprecation", "breaking-changes", "codemod", "postmortem", "m8-telemetry-free", "pillar-node"]
priority: "P1"
depends_on: ["D180 pillar-decoupling", "M26 doc standards", "M8 zero telemetry", "SO-10a structured gnosis"]
blocks: ["rehearsal-migration-execution"]
acceptance_gates:
  - "make doc-llm-validate passes when promoted to docs/standards/"
  - "Every deprecation carries DEP-ID + removal date + migration path"
  - "No shim removed without PIVOT_LOG D-remove entry + postmortem distillation"
cross_references:
  - "data/entities/researcher/workspace/MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v5.md"
  - "data/entities/researcher/workspace/REHEARSAL_LEARNING_PLAN_20260822_v5.md"
  - "docs/decisions/PIVOT_LOG.md"
  - "docs/standards/DOC_STYLE_GUIDE.md"
llm_metadata:
  token_budget: 8000
  chunk_strategy: "section_per_component"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Omega Engine — Breaking-Change Migration Playbook

**AP Token**: `AP-MIGRATION-PLAYBOOK-v5.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT

**Date**: 2026-08-22
**Purpose**: Define how the Omega Engine runs, documents, and learns from breaking-change migrations for live user bases — telemetry-free (M8), LLM-doc-compliant (M26), and mapped onto existing PIVOT_LOG / Soul Distillation / Hivemind systems.
**Evidence base**: `MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v5.md` (§ references below point there).

---

## What

A five-stage lifecycle for every breaking change: **Register → Deprecate → Migrate → Remove → Learn**. Each stage has mandatory artifacts, owners, and gates. The lifecycle is enforced by convention now (this playbook) and by CI gates as surfaces mature.

## Why

The Pillar→Node decoupling (D180) is our first engine-wide breaking change with live consumers (WADs, entity souls, MCP tool contracts, tests). We currently have no institutional process: shims exist (`entity_registry.py:404-419` auto-migration) but no timeline, no guide, no tracking, no learning loop. Every researched exemplar that survived a major migration had four things we lack: a pre-committed removal date, a task-organized guide, honest automation coverage, and a blameless learning capture. This playbook supplies all four under our constraints (zero telemetry, single-architect-plus-fleet reality, Temple-Grade docs).

---

## §1 Lifecycle Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1 REGISTER      STAGE 2 DEPRECATE     STAGE 3 MIGRATE             │
│ DEP-ID minted         dual-path + warning   guide + codemod decision    │
│ PIVOT_LOG D-register  timeline published    rehearsal (if risky)        │
│        │                     │                     │                     │
│        ▼                     ▼                     ▼                     │
│ STAGE 5 LEARN ◄────── STAGE 4 REMOVE                              │
│ postmortem            shim deletion ONLY after:                       │
│ L1→L2→L3              ▸ N+2 releases OR 60d elapsed (internal)        │
│ Corpus Map row        ▸ 12-month floor (corpus/soul data contracts)   │
│ runbook update        ▸ census grep = zero legacy hits                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Two-proposal rule** (SEP-2596 adoption): deprecation and removal are separate PIVOT_LOG decisions. A removal decision may not ride along inside a deprecation entry.

---

## §2 Stage 1 — Register

**What**: every intended breaking change gets a stable identifier BEFORE any code moves.

**Mechanics**:
```yaml
# Mint in data/coordination/DEPRECATION_TIMELINE.md (single table)
- dep_id: DEP-PILLAR-001          # format: DEP-<DOMAIN>-<NNN>, immutable
  surface: config/wads/*/entities.yaml pillars: key
  replacement: slots: key (auto-migrated on load since entity_registry.py:404-419)
  registered: 2026-08-22
  deprecated_in: v0.2.x           # release carrying the dual-path
  remove_not_before: v0.4.x       # N+2 rule
  migration_path: auto on load; codemod optional; guide required
```

**Gates**: DEP-ID exists ⟹ PIVOT_LOG D-register entry exists (one sentence, links this row). No orphan deprecations (Queue Integrity spirit, M12).

---

## §3 Stage 2 — Deprecate

**What**: old path keeps working; new path is available; both are loud.

### 3.1 Dual-path patterns (choose per surface)

| Surface | Pattern | Exemplar |
|---|---|---|
| Python API | Old name delegates to new + emits named warning | Django `RemovedIn<N>DeprecationWarning`; Pydantic `.dict()`→`.model_dump()` |
| Config/YAML | Accept both keys; auto-normalize on load; log normalization event | Our existing `pillars:`→`slots:` loader migration |
| MCP tools | New tool name live; old name aliases to it with response-field `deprecated: true` | SEP-2596 `@deprecated` annotations |
| Data formats | Stop WRITING legacy immediately; keep READING indefinitely until census clears | Kubernetes storage-vs-serving split |

### 3.2 Warning emission standard (telemetry-free)

```python
# File: src/omega/deprecation.py (proposed home; research-only per mission)
# Purpose: single helper so every deprecation logs identically and greppably.

import logging, warnings

logger = logging.getLogger("omega.deprecation")

def warn_deprecated(dep_id: str, removal: str, use_instead: str,
                    stacklevel: int = 3) -> None:
    """Emit one structured local-log line + a Python warning per deprecated call.

    M8-compliant: logger writes to local data/ observability only; nothing
    leaves the machine. dep_id must exist in DEPRECATION_TIMELINE.md.
    """
    msg = (f"[{dep_id}] deprecated; remove_not_before {removal}; "
           f"use {use_instead} instead")
    warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)
    # Local sink only (M8 exception). Include caller site via stacklevel.
    logger.warning("deprecated_use id=%s removal=%s", dep_id, removal)
```

Rules:
- One line per invocation to the LOCAL log (hit-rate signal — Evidence §4.1).
- Named, filterable warning class family so CI can run `-W error::DeprecationWarning` in strict mode.
- Never warn more than once per site per process (warning registry default) — noise kills compliance (Python lesson).

### 3.3 Timeline publication

`data/coordination/DEPRECATION_TIMELINE.md` is the public pre-committed schedule (Django model). Updated in the same commit as the deprecation (announce-in-sync; Hivemind post intent=`status` carries the announcement).

### 3.4 Window norms (ratified defaults)

| Contract class | Minimum window | Basis |
|---|---|---|
| Internal code/config surfaces | N+2 minor releases OR 60 days, whichever LONGER | Django two-release rule, scaled to our cadence |
| External/user-facing contracts (MCP tools, CLI verbs) | 12 months floor | SEP-2596 |
| Security-expedited | ≥90 days + Kali sign-off | SEP-2596 security route |
| Persisted data formats (souls, vaults, corpora) | Read forever; write-new immediately; removal only after census = zero hits across ALL known deployments | Kubernetes storage rule |

---

## §4 Stage 3 — Migrate

### 4.1 The migration guide template (mandatory artifact)

Location: `docs/migrations/DEP-<DOMAIN>-<NNN>.md` (Category 6 KB doc — full LLM-friendly format). Skeleton:

```markdown
---
schema_version: "1.0"
document_type: "guide"
document_id: "dep-pillar-001-migration"
title: "Migrating pillars: to slots:"
status: "ACTIVE"
version: "1.0.0"
date: "<date>"
owner: "<node>"
tags: [migration, dep-pillar-001]
llm_metadata: {token_budget: 3000, chunk_strategy: "flat",
               answer_first_sections: true, self_contained_code: true}
---
# Migrating <surface> (<DEP-ID>)
**Affected**: versions <a> → <b>. **Effort**: ~<N> min typical, ~<M> max.
**Automated coverage**: <what the codemod does> / does NOT cover: <BP009 list>.

## Do this first (breaks NOW)
1. <step with exact command>
## Do this before <removal version> (breaks EVENTUALLY)
...
## Error → Fix table (Ctrl+F targets)
| Error you will see | Fix |
|---|---|
| `AttributeError: ... list_pillar_keepers` | call `list_node_keepers()` |
## Troubleshooting
<common new-version errors + resolutions>
## Verification
<exact commands proving migration succeeded>
```

Craft rules enforced (Evidence §2.3): task-organized with effort estimates; error strings verbatim in headers; comparison table early; self-contained before/after blocks (our own M26 mandate); troubleshooting section mandatory; validate with three uninvolved readers before publishing (paraphrase/plus-minus/task testing); version-stamp + link-check quarterly.

### 4.2 Codemod decision procedure

Run the matrix (Evidence §3.3). For Omega today:

| Candidate migration | Verdict | Tool |
|---|---|---|
| `pillars:` → `slots:` in WAD YAMLs (~70 entities) | **Codemod** — mechanical, dozens of sites, recurring across community WADs | Python+yaml script (already drafted in refactor plan Phase 3); ast-grep unnecessary for YAML |
| `oracle_list_pillar_keepers` → `_node_keepers` rename | **Manual + grep** — <20 sites, one-shot | `grep -rn` checklist in guide |
| Test assertion updates (12 sites) | **Manual** — few sites, judgment in each | Guide checklist |
| Entity soul.yaml `pillars:` fields (3 files) | **Manual review** — data correctness >> speed | Guide + human eyes |

Semi-automated loop for any multi-file pass (Bevy workflow): clean branch → transform → verify (`make test`) → format → repeat until green. Publish the loop itself in the guide.

**Honesty gate**: any shipped automation MUST carry an explicit "does NOT cover" list (bump-pydantic BP009 pattern). Silent partial transformation is an M23 violation.

### 4.3 Rehearsal requirement

Breaking changes touching >50 files or persisted-data formats require a REHEARSAL execution on a scratch clone before the real cut-over. Procedure: `REHEARSAL_LEARNING_PLAN_20260822_v5.md`.

---

## §5 Stage 4 — Remove

Removal is permitted when ALL hold:
1. Window elapsed per §3.4 table (cite dates in the PR).
2. Census grep over all known deployment surfaces returns ZERO legacy-pattern hits:
   ```bash
   # Example census for DEP-PILLAR-001 (run before any shim deletion)
   grep -rn "pillars:" config/ data/entities/ --include="*.yaml" ; echo "exit=$?"
   # exit=1 (no matches) required
   ```
3. Shim contract tests deleted in the SAME commit (they fail loudly otherwise — synthetic-user gate).
4. Separate PIVOT_LOG D-remove entry exists (two-proposal rule).
5. Hivemind closeout post announces removal (kubernetes-announce analog).
6. Postmortem scheduled (Stage 5) — removal without learning capture is incomplete.

Stub-retention exception (Django pattern): if legacy data may still arrive (backups restored, old clones), keep a READ-path stub with its own DEP-ID rather than hard-failing on load.

---

## §6 Stage 5 — Learn (mapping to existing systems)

### 6.1 Blameless postmortem (after every executed migration)

Format (Google SRE minimal set, Evidence §5.1):

```markdown
# Postmortem: DEP-PILLAR-001 pillar→slot migration
## Summary          (2–3 sentences: what, when, impact)
## Timeline         (UTC timestamps; verifiable events ONLY — sources cited)
## Contributing factors (2–5 systemic causes; blameless language table applied)
## What went well   (load-bearing mechanisms to PRESERVE — never skip)
## Action items     (each: owner + ACTIVE_SPRINT.json ID + due date)
## Recurrence check (have we seen this failure class before? prior DEP/PIVOT refs)
```

Writing rules: five-whys chains must terminate at a missing guardrail, never at a person; timeline and analysis are separate sections; blame-language conversion table applied at review.

### 6.2 Distillation ladder (where knowledge lands)

| Artifact | System | Format |
|---|---|---|
| Decision records | `docs/decisions/PIVOT_LOG.md` | D-register + D-remove entries (immutable) |
| Lessons | overseer `proposed_lessons.yaml` | SO-10a: narrative/insight/principle, tagged `[N_XX]` or `[DEP-*]` |
| Reusable guide skeleton | `docs/standards/MIGRATION_GUIDE_TEMPLATE.md` | Extracted from the concrete guide after first execution |
| Registry rows | `STRATEGY_CORPUS_MAP.md` | One row per artifact (D-366 discipline) |
| Sprint items | `ACTIVE_SPRINT.json` | Action items land here SAME DAY, not in prose |

Example L3 principle (format target): *"A decision is only as ratified as its least-updated config surface"* (N11 Insight 2 pattern) → migration equivalent: *"A migration is only complete when the census grep is empty, not when the codemod exits zero."*

### 6.3 Telemetry-free tracking summary (M8)

Primary signal: local structured log `deprecated_use id=<DEP-ID>` lines (§3.2), aggregated locally. Secondary: opt-in `omega report-deprecations` packaging into issue template; issue template asks "migrating FROM which version?" (multi-jump distribution — Home Assistant gap); contract tests as synthetic users; periodic manual census (we can see all our deployments — Kubernetes needs hidden metrics because it cannot; we can).

---

## §7 Roles & Gates

| Role | Duty in lifecycle |
|---|---|
| Researcher | Evidence refresh per migration; guide drafting; postmortem facilitation |
| Roc Racoon | Mechanical sweeps (census greps, bulk edits) per curator-balance clause |
| Ma'at/N3 buildmaster | Version stamping; window arithmetic verification; changelog taxonomy |
| N10 verifier | Contract-test strategy for shims; removal-gate test deletion |
| Kali | Ratifies D-register/D-remove entries; signs off expedited windows |
| Architect | Sole approver for corpus/soul-format windows (12-month class) |

Gate chain: Register(grep timeline) → Deprecate(`make test` green with warnings) → Migrate(guide passes doc-llm-validate; rehearsal done if §4.3 triggers) → Remove(census empty ∧ tests deleted ∧ D-remove exists) → Learn(postmortem filed ∧ lessons staged ∧ corpus row added).

---

## §8 First Application

This playbook's pilot is the Pillar→Node decoupling (D180): audit already exists (`PILLAR_LEAK_AUDIT_20260822.md`), refactor plan exists (`PILLAR_REFACTOR_PLAN_20260822.md`). Gap-fill required to comply: mint DEP-PILLAR-001..00N rows, publish DEPRECATION_TIMELINE.md, add `warn_deprecated` emission to remaining runtime touchpoints, author `docs/migrations/DEP-PILLAR-001.md`, then rehearse per companion plan. Execution sequencing lives in `REHEARSAL_LEARNING_PLAN_20260822_v5.md`.

---

## §9 Non-Goals

- No new agent files (M10) — roles map to existing fleet.
- No telemetry of any kind (M8) — local logs and opt-in packaging only.
- No modification of immutable decision history (PIVOT_LOG append-only).
- No codemod infrastructure purchase/adoption beyond stdlib+existing deps unless the decision matrix triggers twice (build-vs-buy re-evaluated per migration, not pre-built).

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT awaiting Kali ratification ⬡ 2026-08-22*
