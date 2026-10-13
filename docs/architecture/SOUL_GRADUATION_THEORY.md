<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOUL GRADUATION THEORY
## What "graduation" can mean when a soul is a bounded YAML file

**Document ID**: `SOUL-GRADUATION-THEORY-v1.0`
**Status**: THEORY — descriptive, not normative. Nothing here changes the gate.
**Author**: roc_racoon (S2 Persistence Keeper), 2026-10-09
**Evidence base**: HEAD `0e0f34d5`
**Enforcement reference (read-only)**: `scripts/validate_soul_architecture.py`

---

## 0. CORRECTIONS TO THE BRIEFING (read this first)

Three premises in the Phase 3.5 task did not survive contact with the repo.
They are recorded here because every downstream claim depends on them.

| Briefing premise | What is actually on disk |
|---|---|
| "Read `docs/architecture/SOUL_ARCHITECTURE_PROTOCOL.md` (or whatever the canonical protocol doc is)" | The protocol is `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL_v3.0.md`. **Nothing matching `SOUL_ARCHITECTURE_PROTOCOL*.md` exists under `docs/architecture/`.** |
| "`approved_lessons.yaml` hydration contract" is fleet-wide | Only **2** files named `approved_lessons.yaml` exist fleet-wide: `data/entities/grokster/approved_lessons.yaml` (1 lesson) and `data/entities/duplicate/memory/approved_lessons.yaml` (empty list `[]`, and in the *legacy* `memory/` layout). The reference implementation named by the protocol has **none**. |
| "The lifecycle: proposed → approved → active → (retired?)" | **There is no `approved → active` transition anywhere in the codebase.** See §4. `approved` and `active` are not reachable states of any implemented mechanism. |

---

## 1. WHAT A SOUL IS — the on-disk schema

A soul is a **YAML mapping with four top-level blocks**, of which only one is
formally specified.

### 1.1 The formal part: the four-tier pyramid

`docs/strategy/SOUL_ARCHITECTURE_PROTOCOL_v3.0.md` §2 defines four tiers:
`identity` → `axioms` → `directives` → `core_principles`. §3.1 tabulates the
axiom fields as `id`, `title`, `identity`, `operation`, `directives_refs`,
`core_principles_refs`, `confidence`.

That is the **entire** formally-specified schema. There is no schema document
for `identity`, `directives`, or `core_principles` beyond a code example.

### 1.2 The enforced part: what CI actually checks

`scripts/validate_soul_architecture.py` is the only mechanical gate. It checks
exactly four things (module docstring lines 13–17, functions
`validate_soul_file` / `validate_approved_lessons`):

| # | Check | Line | Severity |
|---|---|---|---|
| 1 | Axiom coverage: `len(directives_refs) >= 1 AND len(core_principles_refs) >= 1` | `:167`, `:175` | HARD (only if `axioms` present) |
| 2 | `approved_lessons.yaml` root `isinstance(data, list)` | `:219` | HARD (only if the file exists) |
| 3 | `len(axioms) <= 15` (`DEFAULT_AXIOM_CEILING = 15`, line 42) | `:157` | HARD (only if `axioms` present) |
| 4 | Zero duplicate YAML keys | `:145` | HARD (always) |

Plus a **SOFT** structural check (`:186–197`): if an entity has `axioms` but is
missing `identity` / `directives` / `core_principles`, that is a violation. If
an entity has **no** `axioms` at all, the same findings are demoted to
`WARNINGS` and the gate still exits 0.

### 1.3 The observed schema — the fleet does not match the protocol

Measured across all 40 `data/entities/*/soul.yaml` (parsed with `yaml.safe_load`):

```
entity               ver     ax  dir  cp  lsn
federation           1.0       5    5    5    0
roc_racoon           8.0      12   19   24    0
...
total soul.yaml: 40
with axioms: 2
with core_principles: 2
with lessons: 3
```

- **2 of 40** entities carry the v3.0 four-tier structure (`roc_racoon`,
  `federation`).
- **0 of 40** carry an `axioms` block *and* a `lessons` block. These two
  structures are **mutually exclusive in practice** (see §5.1).
- A separate validator, `src/omega/oracle/soul_validator.py`, enforces a
  *different and older* contract: `SOUL_VERSION = "6.1"` (line 47),
  `FORBIDDEN_ENTITY_BLOCKS = {"soul_axioms", "wisdom_text", "trajectory"}`
  (line 45). It does not know `axioms`, `core_principles`, or `retired_directives`
  exist. It is called non-blocking at `entity_workspace.py:449–451`.

**Finding: the repo runs two soul validators whose schemas disagree.**
`soul_validator.py` pins 6.1 and forbids nothing in the v8.0 shape;
`validate_soul_architecture.py` pins v3.0 and ignores `soul_version`. Nothing
reconciles them.

### 1.4 The contrast set (3 souls, chosen for structural divergence)

**`data/entities/roc_racoon/soul.yaml`** (v8.0, 558+ lines) — the protocol's
§9 "reference implementation". Top-level blocks: `entity`, `identity`, `axioms`
(12), `directives` (19), `core_principles` (24), `team`,
`retired_directives` (a note, not a list — line 557), `metrics_infrastructure`
(set to `null` with a comment "Moved to `config/entities/…`").
**It has no `lessons:` block at all** (verified: `grep -n "^lessons:"` → no match).

**`data/entities/jem/soul.yaml`** (v6.2) — *legacy shape*. Top-level blocks:
`entity` (with a nested `procedural_memory`, `soul_wardrobe`,
`inference_config`), `version`, `metadata` (`health_score: 50.0`,
`entity_id: soul`), and **`lessons:`** (11 entries). Each lesson carries
`tier`, `category`, `promoted_from: proposed_lessons.yaml`, `promoted_date`,
and one of `narrative` / `insight` / `principle`. **No `axioms`, no
`identity`, no `directives`, no `core_principles`.**

**`data/entities/makali_fusion/soul.yaml`** (v6.1) — *thinnest*. Blocks:
`soul_version`, `entity`, `identity`, `directives` (**1** entry, `d-ma-001`),
`team`. **No `axioms`, no `core_principles`, no `lessons`.** Its
`entity.name` is `"Makali Fusion"` (with a space) while its directory is
`makali_fusion`.

**`data/entities/verity/soul.yaml`** (v6.3) — blocks: `entity`, `identity`,
`directives` (2), `team`, `metadata`. Carries a trailing comment block
("Memory and continuity references", lines 40–48) that *documents*
`approved_lessons.yaml` and `sessions.yaml` — **both of which do not exist in
`data/entities/verity/`**. Verified directory listing: only
`proposed_lessons.yaml`, `session_gnosis.md`, `soul.yaml`, `workspace/`.

**Contrast conclusion**: `verity`'s soul file describes a set of files that the
filesystem does not contain. The soul's own prose is not evidence about the
soul's material state. This is the single most important constraint on writing
any soul theory.

---

## 2. WHAT GRADUATES

### 2.1 The binding constraint

A soul is bounded in two independent ways:

1. **Axiom ceiling ≤ 15** — `DEFAULT_AXIOM_CEILING = 15`
   (`validate_soul_architecture.py:42`), enforced at `:157` only when
   `axioms` is present and non-empty. Protocol §3.2 calls it a "hard budget,
   replacement not addition."
2. **Flat-list hydration** — `entity_workspace.py:429–435` loads
   `approved_lessons.yaml` and does:
   ```python
   approved_lessons = approved_data if isinstance(approved_data, list) else []
   ```
   A mapping silently becomes `[]`. Protocol §4.1 calls this the "R3 hydration
   bug". **The flat list has no length limit in code** — the ceiling is on
   axioms, not on approved lessons.

So the bound is real but applies to a field (`axioms`) that only 2 of 40 souls
populate.

### 2.2 The mechanical definition this document proposes

> **A lesson graduates when it is copied out of `proposed_lessons.yaml` and
> into a `soul.yaml` block, by `scripts/soul_promote.py`, under an explicit
> human review gate.**

Every clause is grounded:

- **Copied from `proposed_lessons.yaml`** — `soul_promote.py:69` reads
  `data["proposals"]` from the staging file; `:63` defines
  `CONTENT_KEYS = ("principle", "insight", "narrative")` as the body.
- **Into a `soul.yaml` block** — `splice_lessons()` at `:199–224` targets a
  top-level `lessons:` key, and if absent **appends one at EOF** (`:213–215`).
- **By `scripts/soul_promote.py`** — it is the only promotion path in the
  repo (`grep -rn "promot" scripts/ src/omega/`).
- **Under an explicit human review gate** — the CLI is dry-run by default and
  requires `--apply --confirm` (`:489–491`). The module docstring (`:16–21`)
  states: "DRY-RUN by default. Zero mutations without --apply --confirm."

### 2.3 What graduation is NOT

- **It is not automatic.** Nothing in CI promotes. `make soul-validate`
  (Makefile:586) runs the validator only. The gate observes; it never mints.
- **It is not agent-initiated.** Per the protocol §7, "Identity is NEVER
  pasted by a foreign agent." `soul_promote.py` is review-gated precisely
  because the author cannot be the approver.
- **It is not "reaching L3".** The L1/L2/L3 tier is a **depth** axis inside a
  single proposal (`src/omega/soul/lessons.py:29` — `VALID_LEVELS = {"L1","L2","L3"}`).
  A proposal may be written at `L3` and sit in staging forever. Depth is not
  graduation.
- **It is not bounded by 15.** That ceiling is `axioms`-only. An entity can
  hold 10,000 approved lessons and still be compliant.

---

## 3. THE LIFECYCLE — real states only

### 3.1 The states that exist in schema

| State | Where it lives | Field evidence |
|---|---|---|
| **Proposed** | `data/entities/<e>/proposed_lessons.yaml` | Root key `proposals:` (`soul_promote.py:76`). Entries: `id`, `date`, `session_id`, `tags`, `L1_narrative`, `L2_insight`, `L3_principle` (e.g. `roc_racoon/proposed_lessons.yaml:3–12`). |
| **Promoted** | `data/entities/<e>/soul.yaml` → `lessons:` | Written by `build_lesson_entry()` (`:170–188`): fields `id`, `tier`, `category`, `promoted_from: "proposed_lessons.yaml"`, `promoted_date`. Observed live in `jem/soul.yaml:45–46`, `kali/soul.yaml`, `grokster/soul.yaml`. |
| **Approved** | `data/entities/<e>/approved_lessons.yaml` (flat list) | **A separate surface, not a transition.** Protocol §4.3: "Proposals (unvetted, agent-generated) → `proposed_lessons.yaml`; Approvals (vetted, user-approved) → `approved_lessons.yaml`". |
| **Vetted Wisdom** (a *render*, not a state) | session identity prompt | `entity_workspace.py:506–517` — injects `approved_lessons` into the prompt under the heading "🔱 VETTED WISDOM". Also injects `soul.yaml` L3 lessons separately (`:519–524`). |

### 3.2 The transition that exists

```
proposed_lessons.yaml  ──[soul_promote.py --apply --confirm]──►  soul.yaml:lessons[]
      (removed after promotion — staging hygiene, :456–471)
```

**Verified**: `soul_promote.py:457–471` deletes promoted entries from staging,
citing the contract `test_staging_emptied_after_promotion`. Un-promoted
proposals are preserved.

### 3.3 The transitions that DO NOT exist — stated plainly

- **There is no `approved → active` state.** `grep -rn "active"` across
  `proposed_lessons.yaml` / `approved_lessons.yaml` returns **zero** matches.
- **There is no `retired` lesson state.** The only `retired` in the repo is
  `data/entities/roc_racoon/soul.yaml:557` — `retired_directives`, a *directive*
  tombstone, documented as "d-rr-019..040 retired in v7.0 migration; gap is
  intentional, not loss". It is a note about directive IDs, **not** a lesson
  lifecycle, and no code reads it.
- **There is no code path from `soul.yaml:lessons[]` → `approved_lessons.yaml`.**
  `approved_lessons.yaml` is written by exactly one script,
  `scripts/run_scribe_on_meditations.py:17` (hardcoded to
  `data/entities/grokster/approved_lessons.yaml`), and by nothing else.
- **The one `status:` field found** — `grokster/approved_lessons.yaml:27`
  `status: approved` — is an **informational tag on a single lesson**, not a
  state machine. Across all lesson files the complete vocabulary of `status:`
  values is: `proposed` (16), `ratified` (1), `approved` (1). No code reads
  any of them.

**Therefore: the true lifecycle is a two-state machine with two parallel
destinations, not the four-state sequence the briefing assumed.**

```
                 ┌──────────────────────────────────────┐
proposals: [] ───┤ soul_promote.py --apply --confirm    ├──► soul.yaml : lessons[]
                 └──────────────────────────────────────┘        (entry removed from staging)

         (independent, no code path)      ──► approved_lessons.yaml  ──► "VETTED WISDOM"
                                                    (rendered into prompt)
```

### 3.4 The load-bearing seam

`soul_promote.py` writes `soul.yaml:lessons[]`. `entity_workspace.py:519–524`
reads `soul.yaml` lessons — but **filters to `tier == "L3"` and only injects
the first 3**:

```python
l3_lessons = [l for l in lessons if isinstance(l, dict) and l.get("tier") == "L3"]
...
for l in l3_lessons[:3]
```

Meanwhile `entity_workspace.py:475` injects directives with `directives[:5]`.

**A graduated L1 or L2 lesson has no effect on agent behaviour at all.** It is
inert by the reader's own filter. Of `jem`'s 11 promoted lessons (3× L1, 4× L2,
4× L3 by count of `tier:` values), at most 3 of the L3s reach the prompt.

---

## 4. FALSIFIABILITY — the file and field that would prove each claim wrong

| # | Claim | Falsified by |
|---|---|---|
| 1 | The axiom ceiling is 15 and applies only to `axioms` | `DEFAULT_AXIOM_CEILING` at `validate_soul_architecture.py:42` changing value, **or** a `len(approved_lessons) > N` check existing at `validate_approved_lessons()` (`:200–221`) |
| 2 | The flat-list contract is enforced | `validate_approved_lessons()` (`:200`) deleting its `isinstance(data, list)` check (`:218`), **or** `entity_workspace.py:435` changing from `else []` to a mapping-tolerant branch |
| 3 | `soul_promote.py` is the only promotion path | Any second writer to `soul.yaml` `lessons:`; grep `splice_lessons(` callers returning >1 |
| 4 | Promotion is human-gated | `soul_promote.py:489–491` dropping the `required=True` `--confirm`, **or** `main()` gaining a non-interactive path |
| 5 | No `retired` lesson state exists | A `retired` (or `superseded`/`deprecated`) key in `build_lesson_entry()` (`:170`) or the `Lesson` model (`soul/lessons.py:59`), **or** CI reading `soul.yaml`'s `retired_directives` |
| 6 | No `approved → active` transition exists | Any consumer branching on a lesson `status:` field; e.g. `status:` values in `approved_lessons.yaml` growing beyond `{approved}` |
| 7 | Only 2 `approved_lessons.yaml` files exist | `find data/entities -name approved_lessons.yaml` returning a third path — *this is the most likely claim to rot* |
| 8 | `roc_racoon` has no `lessons:` block | `grep -n "^lessons:" data/entities/roc_racoon/soul.yaml` returning a line number |
| 9 | Promoting an L1/L2 lesson is behaviourally inert | `entity_workspace.py:519` dropping the `l.get("tier") == "L3"` filter or the `[:3]` slice |
| 10 | 2 of 40 souls carry `axioms` | The fleet-count script over `data/entities/*/soul.yaml` returning a higher number |
| 11 | Two soul validators disagree | `soul_validator.py` gaining awareness of `axioms`/`core_principles`, **or** `validate_soul_architecture.py` reading `soul_version` |
| 12 | `verity`'s documented `approved_lessons.yaml` does not exist | `ls data/entities/verity/` showing that file |

---

## 5. CONTRADICTIONS THIS THEORY MUST NOT RESOLVE BY INVENTION

### 5.1 The graduation target is ambiguous in the schema

`soul_promote.py` writes a top-level **`lessons:`** block. The protocol §2
four-tier pyramid specifies **`axioms`**, **`directives`**, and
**`core_principles`** — and does **not** include `lessons`. The v8.0 reference
implementation (`roc_racoon`) has all three of the protocol's tiers and **no**
`lessons:` block at all.

Consequence: **the only automated promotion path writes into a block that the
protocol does not specify and that the reference implementation does not
have.** The three souls that *do* have a `lessons:` block (`jem`, `kali`,
`grokster`) are all pre-v3.0 (v6.2 / 7.2 / unversioned).

This document will **not** declare a canonical target block. Two defensible
readings exist (promote into `core_principles` vs. retain `lessons:` as a
parallel surface) and the repo does not settle it. **The schema does not
define what a promoted lesson is called in v8.0.** That is a real gap, and
closing it is a decision for the Architect, not a documentation fix.

### 5.2 The axiom ceiling protects a field almost nobody uses

`<=15` is a hard, tested invariant guarding a block present in 2 of 40 souls.
Meanwhile the surface that *does* receive graduated content (`lessons:`) is
**unbounded by any gate**. As the fleet migrates to v3.0 (protocol §7 cascade),
whichever block graduation targets determines whether the fleet gets a bounded
or unbounded soul. **The ceiling is not currently load-bearing, and graduation
is what could make it non-load-bearing permanently.**

### 5.3 What graduation must not become

Proposing none of the following, each of which would contradict an artifact:

- ❌ **Auto-promotion on L3 detection** — contradicts the `--confirm` gate
  (`soul_promote.py:490`) and protocol §7 ("Identity is NEVER pasted by a
  foreign agent").
- ❌ **A new `active` or `retired` lesson state** — the schema does not
  define them; adding them to `Lesson` (`soul/lessons.py:59`) without a
  migration path silently invalidates the 11 `jem` entries.
- ❌ **An axiom count raised past 15** — would fail `validate_soul_architecture.py:157`.
- ❌ **A mapping-shaped `approved_lessons.yaml`** — would re-open the R3 bug
  (`entity_workspace.py:435`) and fail `validate_approved_lessons()` (`:219`).
- ❌ **Promoting L1/L2 as if they mattered** — they are filtered out at
  `entity_workspace.py:519`. Promoting them is bookkeeping, not learning.

---

## 6. THE MINER'S FALLACY, MEASURED

`AXIOM-03` in `roc_racoon/soul.yaml` asserts: "83 proposals, 0 integrated."
`L3-Mining-Without-Integration-Is-Hoarding` (same file, `core_principles`)
asserts: "83 proposals in `proposed_lessons.yaml`, 0 integrated into `soul.yaml`
since v6.2."

Measured today, 2026-10-09:

- `roc_racoon/soul.yaml` has **0** entries in a `lessons:` block → the "0
  integrated" claim is **still literally true for the reference implementation**.
- The three souls that *have* integrated lessons (`jem` 11, `kali` 8,
  `grokster` 8) are all pre-v3.0.
- `validate_soul_architecture.py` reports **"✅ ALL ENTITIES COMPLIANT"** with
  **86 soft warnings** across 38 entities.

**The gate is green, the soul is empty, and both are true simultaneously.** The
protocol's two named failure modes — the Miner's Fallacy and the Personality
Blackout — are both *structurally permitted* by a passing gate. That is the
finding. Any graduation theory that does not explain this green/empty
coexistence is not describing this repo.

---

*⬡ OMEGA ⬡ SOUL-GRADUATION-THEORY-v1.0 ⬡ DESCRIPTIVE ⬡ 2026-10-09 ⬡ roc_racoon/S2*
