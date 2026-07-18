⚠️ **DEPRECATED NOMENCLATURE** — This document uses legacy terminology that has been renamed:
- **LLOC** → **Meditate** (single-inference cognitive prism)
- **HLOC** → **MC (Mastermind Council)** (multi-subagent same-session)
- **Octave Council** → **Lens Framework** (composable cognitive perspectives)
- **10 Pillars** → **Omega Pantheon** (lens-primary; pillar is optional WAD metadata)
- **P1–P10** references → **Lens names** (infrastructure, persistence, engineering, etc.)

This naming was ratified 2026-07-16 and applied across the fleet on 2026-07-18.
Content below is preserved as-is for historical reference. See `config/wads/_omega_default/meditate/lenses.yaml` for current lens definitions.
# 🔱 YAML Hardening Brief — Omega Engine
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_yaml_hardening ⬡ HANDOFF
**Date**: 2026-06-05
**Status**: 📋 HANDOFF BRIEF — Delegated to Kali (P3 Engineering)
**From**: Roc Racoon (Sovereign Miner, design lane)
**To**: Kali (P3, implementation lane) → Researcher (audit lane)
**Severity**: 🔴 P0 — `data/entities/roc_racoon/soul.yaml` is currently **non-parseable** by standard YAML loaders (yaml.safe_load fails)

---

## §0 Why This Brief Exists

During final session cleanup, I attempted to add two evolution entries to `soul.yaml`
and discovered the file **fails YAML parse** with multiple syntax errors. Per
**d-rr-036** (Triad delegation: Design-Implement-Observe), my role is to **DESIGN
the problem statement and HAND OFF**, not to implement the fix.

**This is not a one-file problem.** It is a fleet-wide pattern that must be hardened
at the protocol level. The 6 legacy repos and current engine use ad-hoc YAML emission
that accumulates structural errors over time.

---

## §1 The Immediate Failure: soul.yaml

### 1.1 Current State
- **File**: `data/entities/roc_racoon/soul.yaml` (953 lines, 80,856 chars)
- **Parser**: `yaml.safe_load()` **FAILS**
- **Error**: `line 941, column 5: while scanning a simple key — could not find expected ':'`
- **Root cause**: Multi-line evolution entries use the shorthand `- DATE: value`
  syntax with unescaped colons in the value, and continuation lines (indented sub-items)
  that the parser interprets as new mapping keys.

### 1.2 Specific Problem Pattern

The evolution block uses this pattern (lines 939-944):
```yaml
  - 2026-06-04: "**SESSION 3 — THREE GHOSTS RECOVERY**. User assigned deep mining of 3 lost persona systems: Jem (Jerrica/Synergy triad), Omnidroid (Phi-OmniMatrix polymath), and 8 Facet Council (Gem oversoul + LLOC/HLOC). Grid search across ALL 3 partitions found all three systems:"
    - JEM: app/JEM_SOUL.md recovered from omega-stack-legacy — complete 3-layer identity (Synergy→Jem→Jerrica) + Holograms (Kimber/Iris, Aja/Athena, Shana/Brigid, Raya/Hestia)
    - OMNIDROID: Ω Omnidroid BIOS Loader + 6-module cognitive architecture + Omnidroid Lite recovered from ANCESTRAL_HUB (omega_vault). Phi-OmniMatrix confirmed as local model assignment.
    - 8 FACET COUNCIL: GEMINI_SOUL_MAP.md (8+1 facets) + MULTI_CLI_COPILOT_GEM_STRATEGY_v2.md (Gem paradigm, LLOC/HLOC governance) + ARCHETYPE_PERSONAS_PROMPTS.md (Egyptian Triad + Greek templates) recovered from omega-stack-legacy.
    User clarified: LLOC = cognitive-only review (the real innovation). HLOC = full subagent launch. 10 Pillar system predates the 8 Facet Council — they are PARALLEL systems, not ancestor/descendant. NO INTEGRATION — documentation and discovery only. Omnidroid naming open for deliberation (Omnidroid/Omnimatrix/Omegadroid/Other).
```

The pattern is **structurally invalid** because:
1. The first line ends with a colon and continues with sub-items on lines 940-942
2. The parser sees the `:` at end of line 939 as introducing a nested mapping
3. The `- JEM:` on line 940 is interpreted as a key without a value
4. The list-of-dashes inside a value is ambiguous

**The fix is to use a YAML literal block scalar (`|`) or quoted multi-line string.**

### 1.3 Structural History (How We Got Here)

The file was assembled over 5 sessions (2026-06-02 to 2026-06-05) with ad-hoc edits:

| Date | Action | YAML impact |
|------|--------|-------------|
| 2026-06-02 | Soul awakened, directives d-rr-001 to 007 added under `directives:` key | Clean |
| 2026-06-04 | Three Ghosts recovery, d-rr-008 to 011 added | **Top-level list at lines 7-203 (siblings of `entity:`)** — invalid |
| 2026-06-05 | ICS Treasure Map, d-rr-012 to 018 added | Continued at top level |
| 2026-06-05 | Hivemind work, d-rr-019 to 040 added | Continued at top level |
| 2026-06-05 (this turn) | I tried to merge the two directive lists | Restructured but YAML still fails |

**Two structural bugs introduced**:
1. **Top-level directive list** (lines 7-203) — siblings of `entity:`, should be under `directives:` key
2. **Multi-line evolution entries** with unescaped colons and continuation dashes

I partially fixed bug #1 by merging the two directive lists. Bug #2 remains.

### 1.4 What I Tried (For Kali's Reference)

| Attempt | Result |
|---------|--------|
| Append SESSION 3-C/3-D evolution entries | Failed (file already broken) |
| Edit-tool: replace exact lines | Failed (whitespace mismatch) |
| `cat >> file << EOF` append | Succeeded structurally but file still fails parse |
| Merge top-level list into `directives:` key | Succeeded (combines 33+7 = 40 directives correctly) |
| Quote multi-line evolution entries | Partial — line 941 still fails |
| Convert to literal block scalars (`\|`) | Not yet attempted — needs careful handling of multi-line patterns |

### 1.5 The Critical Bit (For Kali)

**Bug #2 is the hard one.** The evolution entries with sub-items (JEM, OMNIDROID, 8 FACET COUNCIL) need a YAML structure change. Three options:

| Option | Pros | Cons |
|--------|------|------|
| **A. Literal block scalar (`\|`)** | Most YAML-idiomatic; preserves formatting | Indentation rules are strict |
| **B. Folded block scalar (`>`)** | Compacts newlines to spaces | Loses line breaks for readability |
| **C. Convert to list of strings** | Simplest structure | Loses the date-as-key pattern |

**Recommendation**: Option A (literal block scalar) is correct per YAML best practice.

---

## §2 The Pattern Problem: Ad-hoc YAML Emission

### 2.1 Fleet-Wide YAML Inventory

The Omega Engine has **~50+ YAML files** across multiple domains. All are written by hand or by `yaml.dump()` with default settings. None are validated by CI.

| Domain | File Count | Validation Status |
|--------|------------|-------------------|
| Entity souls | 6+ (one per active entity) | ❌ None |
| WAD configs | 4+ (in `config/wads/`) | ❌ None |
| Provider config | 1 (`config/providers.yaml`) | ❌ None |
| Model config | 1 (`config/models.yaml`) | ❌ None |
| Mode definitions | 5+ (`.opencode/modes/*.md`) | ❌ None |
| Agent files | 14+ (`.opencode/agents/*.md`) | ❌ None |
| Demand signals | 6 (`data/coordination/demand_signals/*.json` — JSON, OK) | ✅ JSON |
| KSIG signals | varies | ❌ None |
| Mining reports metadata | varies | ❌ None |
| **TOTAL** | **~50+ files** | **0 validated** |

### 2.2 Root Causes (Per Roc's Mining Observations)

| Pattern | Where It Comes From | Fix |
|---------|--------------------|-----|
| Unescaped colons in values | Hand-edited soul.yamls | Use literal block scalars |
| Unescaped quotes in values | Hand-edited strings | Use single quotes inside double, or escape |
| Top-level lists mixed with mappings | Append-without-merge mentality | Enforce one root document |
| Trailing whitespace | Cat-herd editing | Pre-commit hook |
| Inconsistent indentation | Mixed tabs/spaces | Pre-commit hook (`yamllint`) |
| Inconsistent key ordering | Different sessions | `yamlfmt` or manual discipline |
| Missing `---` document markers | Multi-doc convention skipped | Add markers or split files |

### 2.3 Why This Matters Now (The Compounding Effect)

- **D-121 Hivemind Observations Protocol** (Lilith) appends observations to `HIVEMIND_OBSERVATIONS_LOG.md` — manual edit, no validation
- **R-2X heritage patterns** require accurate `CREDITS.md` §1.x entries — manual edit, no validation
- **Soul distillation** (M11) requires accurate soul.yamls — manual edit, no validation
- **Cross-pollination KSIG signals** — JSON, but the schema is enforced by convention, not by validator

**As the fleet grows, the YAML error surface grows linearly. Without hardening, we'll hit a critical failure point where the soul.yaml or another core file becomes non-parseable in production.**

---

## §3 The Hardening Protocol (Proposal for Kali)

### 3.1 Layer 1: Pre-commit Hook (Immediate Win)

Add a pre-commit hook that runs `yamllint` and `yaml.safe_load` on all `.yaml` and `.yml` files.

```yaml
# .pre-commit-config.yaml (proposed)
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        args: ['--config-file=.yamllint']
```

**.yamllint** (proposed):
```yaml
extends: default
rules:
  line-length: max 200
  indentation: 2
  document-start: disable  # we use no-document markers
  truthy:
    check-keys: false
  comments:
    min-spaces-from-content: 1
```

**Effort**: 1 hour (Kali)
**Impact**: Prevents 100% of indentation/formatting errors

### 3.2 Layer 2: Schema Validation (Schema-Driven)

Define JSON Schema (or Pydantic) for the major YAML files:
- `soul.yaml` schema
- `entities.yaml` schema (per IWAD)
- `providers.yaml` schema
- `models.yaml` schema

Use `jsonschema` (Python) or `pydantic` to validate on write AND on read.

**Effort**: 4-6 hours (Kali + Researcher for design)
**Impact**: Prevents structural errors (top-level list vs mapping, missing keys, wrong types)

### 3.3 Layer 3: Lint + Auto-fix (yamllint + yamlfmt)

Add `yamlfmt` or `prettier` to the dev workflow. Run on every commit. Auto-fix where possible.

**Effort**: 2 hours (Kali)
**Impact**: Prevents whitespace, key ordering, and comment placement issues

### 3.4 Layer 4: CI Gate (Temple-Grade)

Add a `make validate-yaml` target to the Makefile (already have `make temple-grade`).
Gate PRs on YAML validation passing.

**Effort**: 1 hour (Kali)
**Impact**: Prevents merge of broken YAML

### 3.5 Layer 5: Documentation (Sovereign Knowledge)

Add a `docs/strategy/YAML_PROTOCOLS.md` that documents:
- When to use literal block scalars (`|`)
- When to use folded block scalars (`>`)
- When to use flow style (`{key: value}`)
- How to escape special characters
- Multi-document conventions
- Common pitfalls (this brief!)

**Effort**: 1-2 hours (Roc, post-handoff)
**Impact**: Prevents future errors by educating the team

---

## §4 The Handoff (What I Need From Kali + Researcher)

### 4.1 Kali (Implementation Lane — P3 Engineering)

**Task Y-1**: Fix `data/entities/roc_racoon/soul.yaml` to be YAML-valid.

**Approach** (recommended):
1. Backup current file: `cp soul.yaml soul.yaml.bak.20260605`
2. Read the file as TEXT (not YAML) to preserve formatting intent
3. Identify all multi-line evolution entries (regex: `^\s*- YYYY-MM-DD:.*$` followed by indented continuation)
4. For each, wrap the value in a literal block scalar: `- DATE: |\n    line1\n    line2\n    ...`
5. Run `yaml.safe_load` to validate
6. Verify semantic equivalence: count directives, lessons, evolution entries
7. Commit with message: `fix(soul.yaml): convert multi-line evolution entries to literal block scalars (Y-1)`

**Task Y-2**: Implement Layer 1 (pre-commit hook) and Layer 4 (CI gate) from §3.

**Task Y-3**: When Y-2 done, post to Hivemind for the rest of the fleet to adopt.

### 4.2 Researcher (Audit Lane — Lattice Reasoning)

**Task Y-4**: Lattice audit of YAML patterns across the entire fleet.

Lattice axes to traverse:
- **Technical**: All `.yaml`/`.yml` files in the repo (use `find . -name "*.yaml" -o -name "*.yml"`)
- **Historical**: 6 legacy repos (`omega-stack-legacy`, `xna-omega-legacy`, `foundation-legacy`, etc.) — how did they handle YAML?
- **Current**: Active configs (`config/*.yaml`, `config/wads/*/entities.yaml`, etc.)
- **Future**: What YAML standards are emerging? (e.g., YAML 1.2 vs 1.1, JSON Schema 2020-12)
- **Philosophical**: Is YAML the right choice? (TOML, JSON5, custom DSL?)
- **Practical**: What's the minimal hardening that prevents 80% of errors?

**Deliverable**: `data/entities/researcher/workspace/YAML_FLEET_AUDIT_v1.md` with:
- Citation graph (which files reference which)
- Pattern catalog (ad-hoc vs schema-driven)
- Error taxonomy (what kinds of errors exist in the fleet)
- Recommendations (which 5 files should be hardened first)

**Task Y-5**: Design JSON Schema / Pydantic models for `soul.yaml` and `entities.yaml`.

### 4.3 Roc (Design Lane — Me, post-handoff)

**Task Y-6** (after Kali + Researcher complete): Write `docs/strategy/YAML_PROTOCOLS.md` based on their findings.

**Task Y-7** (after Y-6): Update `data/entities/roc_racoon/workspace/ROC_MINING_TASKS_v3.md` to add Y-1 through Y-6 as resolved.

---

## §5 Open Questions for the Fleet

| # | Question | Owner |
|---|----------|-------|
| Q1 | Should the fleet migrate from YAML to TOML for new files? (TOML is stricter, no indentation issues) | Kali + Researcher |
| Q2 | Should `soul.yaml` be split into `soul.yaml` (core) + `lessons.yaml` (list) + `evolution.yaml` (log)? (separation of concerns) | Roc (design) |
| Q3 | Should we add a `make yaml-validate` target to the Makefile? | Kali |
| Q4 | Should JSON Schema files be checked in alongside the YAML they describe? | Researcher |
| Q5 | How do we handle the "legacy" YAML files in `_omega_default/entities/` that we don't own? | Kali (audit) |

---

## §6 Why This Is a Pillar P3 / Kali Lane Issue

Per `SOVEREIGN_MANDATES.md` M13 (Temple-Grade Compliance) and the H-0 (PIVOT_LOG `implementation_status` watchdog) from my HIVEMIND_HARDENING_SPEC_v1.md, **code-level validation is P3 Engineering**. Per D-kal-033 (Hybrid ownership — Roc designs, Kali implements), this is exactly the pattern: I designed the problem, Kali implements the fix.

**Per d-rr-036 (Triad delegation: Design-Implement-Observe):**
- **Design** = Me (this brief)
- **Implement** = Kali (Y-1, Y-2, Y-3)
- **Observe** = Researcher (Y-4, Y-5)

This is the sovereign way to handle fleet-wide concerns.

---

## §7 Cross-References

- `data/entities/roc_racoon/soul.yaml` — The broken file (953 lines, fails parse)
- `data/entities/roc_racoon/workspace/HIVEMIND_HARDENING_SPEC_v1.md` §17 (Mesh Network context)
- `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` — Will receive new observation
- `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` — Phase 5 = Hivemind Productionization
- `SOVEREIGN_MANDATES.md` M13 (Temple-Grade) — Quality gate
- `PIVOT_LOG.md` D-122 (TTL) — Recent precedent for the "design-impl-observe" pattern

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_yaml_hardening ⬡ HANDOFF*

*Brief complete. Handing off to Kali. This is exactly the d-rr-036 pattern in action — design the problem, delegate the implementation, observe the results.*
