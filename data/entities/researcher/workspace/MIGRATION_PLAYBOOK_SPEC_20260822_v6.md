---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "spec"
document_id: "migration-playbook-spec-20260822-v6"
title: "Post-Debut Breaking-Change Migration Playbook (Spec)"
status: "DRAFT"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "deprecation", "breaking-changes", "mcp-hub", "expand-contract", "m26"]
priority: "P1"
depends_on: ["D180", "PILLAR_REFACTOR_PLAN_20260822"]
blocks: ["post-debut pillar→slots migration execution"]
acceptance_gates:
  - "make doc-llm-validate passes on this document structure"
  - "Every policy rule traces to a cited case study in MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v6.md"
cross_references:
  - "MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v6.md"
  - "REHEARSAL_LEARNING_PLAN_20260822_v6.md"
  - "data/entities/roc_racoon/workspace/mining_reports/PILLAR_REFACTOR_PLAN_20260822.md"
llm_metadata:
  token_budget: 8000
  chunk_strategy: "section_per_component"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Post-Debut Breaking-Change Migration Playbook — Spec
**AP Token**: `AP-MIGRATION-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT

**Date**: 2026-08-22
**Purpose**: Define Omega Engine's canonical process for running and documenting breaking-change migrations against a live user base, modeled on proven industry practice and adapted to our constraints (M8 zero-telemetry, M2 firewall, M26 doc standards).
**Evidence base**: `MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v6.md` (§ references below point there)

---

## §0 What & Why

**What**: A five-stage migration lifecycle (Announce → Shim → Track → Remove → Learn) with concrete artifacts, owners, timelines, and doc formats for every breaking change that touches users of the engine, MCP Hub tools, WAD configs, or agent-facing surfaces.

**Why**: The engine is about to have its first external users (PUBLIC-DEBUT). The pillar→slots decoupling (D180) is already a live example: `oracle_list_pillar_keepers` MCP tool renames to `oracle_list_node_keepers`, response fields change (`pillar`→`slot`), WAD YAML keys migrate (`pillars:`→`slots:`), SPIFFE ID paths change. Every future change of this class needs one repeatable process — not improvisation per incident.

**Design constraints honored**:
- **M8 Zero Telemetry**: all usage tracking is operator-local + voluntary reporting (§4; evidence §8).
- **M2 Firewall**: WAD-layer semantics never leak into engine-core migration code; migrations move data between layers, never interpret it.
- **M18 Sane-Boundary**: this spec preserves edge cases (silent-behavioral changes, LTS-spanning users, dual-era clients) rather than compressing them away.
- **M23 Failure Integrity**: every stage has explicit terminal states; no silent shim decay.
- **M26 Doc Standards**: every user-facing artifact lands in an LLM-validatable format (§6).

---

## §1 The Five-Stage Lifecycle (Expand → Contract)

```
Stage 1 ANNOUNCE ──► Stage 2 SHIM ──► Stage 3 TRACK ──► Stage 4 REMOVE ──► Stage 5 LEARN
(deprecation entry)  (dual-name       (local signals +   (removal release,  (blameless post-
                      shims, new       voluntary report)  registry update)   mortem → soul)
                      way live)
```

### Stage rules (each traced to evidence)

| # | Rule | Source |
|---|------|--------|
| R1 | A feature is never removed in the same version that deprecates it. Removal happens only at a MAJOR/minor boundary after the minimum window. | K8s Rule 1 [§4]; Django B.0 removal [§2] |
| R2 | **Minimum shim lifetime: 2 release cycles OR 12 months, whichever is LONGER.** Security-expedited removal allowed at ≥90 days with Architect approval recorded in PIVOT_LOG. | Django ≥2 features [§2]; MCP 12-month floor [§5]; expedited clause [§5] |
| R3 | The replacement must be fully shipped and documented BEFORE the deprecation is announced. Never deprecate toward a draft. | MCP SEP-2596 [§5] |
| R4 | Every runtime warning MUST state: what is deprecated, since which version, earliest removal version, and the replacement. | K8s Warning header [§4]; Django warning taxonomy [§2] |
| R5 | One canonical registry page answers "what is deprecated and by when" for the whole project. | Django Deprecation Timeline [§2]; MCP deprecated.mdx [§5] |
| R6 | Mechanical changes get codemods with dry-run mode; semantic changes get characterization tests first. Never automate judgment. | bump-pydantic honesty [§3][§7] |
| R7 | Shims are tracked assets with named owners and terminal states — they cannot silently rot. | M23; akasa kill-switch [§3] |
| R8 | Every completed migration ends with a blameless post-mortem distilled L1→L2→L3 into proposed_lessons.yaml. | Google SRE / Etsy / Jeli [§9]; M11 |

### Versioning anchor

Omega uses SemVer:
- **MAJOR** = K8s API-group increment / MCP revision boundary — where removals land.
- **MINOR** = deprecation warnings may START here (like Django feature releases).
- **PATCH** = never carries deprecations or removals.

---

## §2 Stage 1 — ANNOUNCE

**What happens**: A breaking change is identified; the deprecation is specified before any code moves.

**Artifacts produced (all mandatory)**:

1. **Migration Ticket** in ACTIVE_SPRINT.json (Tier-0 statuses only, M27):

```yaml
ticket:
  id: "MIG-<seq>"
  title: "Deprecate <old> → <new>"
  priority: "P1"
  owner: "<single entity>"          # R7: one named owner
  depends_on: ["<replacement ticket id>"]   # R3 enforced structurally
  stages:
    announce: {release: "vX.Y", status: backlog}
    remove: {earliest_release: "vX'.Y'", status: backlog}   # computed from R2
  acceptance_criteria:
    - "registry entry exists in docs/reference/DEPRECATIONS.md"
    - "runtime warning names removal version + replacement"
    - "codemod or manual guide exists per §3 decision matrix"
```

2. **Registry entry** in `docs/reference/DEPRECATIONS.md` — the single canonical page (R5):

```markdown
| Deprecated | Since | Earliest removal | Replacement | Migration guide |
|------------|-------|------------------|-------------|-----------------|
| `oracle_list_pillar_keepers` MCP tool | v1.1.0 | v1.3.0 | `oracle_list_node_keepers` | #mig-pillar-slots |
```

3. **Release-notes entry** under a fixed `## Backward-Incompatible Changes` heading; each item states reason + action + deadline (HA pattern: say WHY, not just WHAT [§6]).

4. **Runtime warning emission** (lands with Stage 2 code):

```python
# File: src/omega/deprecation.py
# Purpose: M8-compliant deprecation warning helper (Playbook R4)

import warnings


def warn_deprecated(old: str, replacement: str,
                    deprecated_in: str, removal_in: str,
                    stacklevel: int = 3) -> None:
    """Emit a standardized deprecation warning naming removal + replacement."""
    msg = (
        f"{old} is deprecated since {deprecated_in} and will be removed "
        f"in {removal_in}. Use {replacement} instead. "
        f"See docs/reference/DEPRECATIONS.md."
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)
```

**Gate to proceed**: registry row exists AND replacement is live AND warning text reviewed. No announcement without all three (R3, R4, R5).

---

## §3 Stage 2 — SHIM

**What happens**: old and new ways coexist; old emits warnings; users migrate at their own pace.

### Dual-name shim patterns (by surface type)

| Surface | Pattern | Example from pillar→slots |
|---------|---------|---------------------------|
| MCP tool name | Register BOTH names; old delegates to new impl + warns | `oracle_list_pillar_keepers` → calls `oracle_list_node_keepers` body |
| Response field | Emit BOTH fields during window; document which dies | `entity_identity["pillar"]` kept alongside `entity_identity["slot"]` |
| Config YAML key | Accept both keys on load; auto-migrate in memory; warn on legacy key | `pillars:` auto-migrated to `slots:` (already implemented, `entity_registry.py:404-419`) |
| Method/function name | Alias function delegating + warning | `list_pillar_keepers()` → `list_node_keepers()` wrapper |
| Path/ID scheme | Accept both path shapes; normalize internally | SPIFFE `entity/pillar/p6` ↔ `entity/slot/p6` |

### Shim hygiene rules

- Every shim carries `last_verified` date + owning ticket ID in its docstring/comment.
- Shim behavior must be equivalent to the old behavior — a shim that changes behavior is a NEW break (Pydantic lesson: mixing models across shim boundaries was unsupported and bit users [§3]).
- Env-var kill-switches for behavioral shims where feasible (akasa `TURN_PYDANTIC_V1_OFF` pattern [§3]).
- **Shim inventory is queryable**: mark each with `# DEPRECATED-SHIM <MIG-id> removal=<version>`; CI counts them and fails if any outlives its registered removal version (anti-permashim, KEP-1635 analogue [§4]).

### Codemod decision matrix (R6)

```
Is the change syntactically pattern-matchable?
├── YES + >50 call sites  → BUILD codemod (ast-grep YAML rules first;
│                            LibCST command if imports/context needed)
│                            MUST ship --diff dry-run + unit tests
├── YES + ≤50 call sites  → sed/grep recipe in the migration guide (no tooling)
└── NO (semantic judgment)→ NO codemod. Characterization tests FIRST,
                             then manual steps with before/after tables.
```

Evidence anchor: bump-pydantic automates ~80% and *cannot* judge `Optional[T]` semantics [§7]; the 20% residue is exactly where production incidents live (kodare `'ß'.upper()` [§1]).

### Verification-first doctrine (from Pydantic community [§3])

Before ANY cutover release:
1. Characterization tests pin current behavior (golden outputs).
2. Old/new run side-by-side in CI; outputs diffed.
3. Strict-mode probe run to surface reliance on lenient behavior.
4. Contract tests assert BOTH shim and canonical paths return identical results (M21).

---

## §4 Stage 3 — TRACK (Zero-Telemetry Measurement)

**Problem**: How do we know if anyone still uses a shim, without telemetry?

**Answer (evidence §8)**: We don't measure users — we give USERS the means to measure themselves, and make reporting effortless.

### The four local channels

1. **Local deprecation ledger** (K8s gauge analogue). Every warning emission appends a structured line to `$DATA_DIR/deprecations/hits.jsonl`:

```json
{"ts": "2026-09-01T12:00:00Z", "feature": "oracle_list_pillar_keepers",
 "since": "v1.1.0", "removal": "v1.3.0", "caller": "setup.sh"}
```

   M8-legal: stored locally in `data/`, never transmitted. Ring-buffered (cap 10,000 lines) to prevent bloat.

2. **Self-diagnostic command**: `omega doctor --deprecations`
   - Reads the local ledger; summarizes hits by feature/recency/caller.
   - Emits a paste-ready markdown block for issue reports (bougie `diagnose --issue` pattern [§8]).
   - This is our Repairs-dashboard equivalent (HA [§6]): proactive, local, actionable.

3. **Issue template hook** (`.github/ISSUE_TEMPLATE/bug_report.yml`): one field asks users to run `omega doctor --deprecations` and paste output. Voluntary, evidence-backed, zero phone-home.

4. **CI self-lint for integrators**: agents/WAD authors running our test suite get failures on deprecated-API use (`warnings-as-errors` mode, kubectl pattern [§4]) — the ecosystem migrates because their own gates force it.

### What we deliberately do NOT do

- No usage counters, no crash upload, no opt-in analytics (opt-in contract patterns recorded as prior art only [§8] — M8-forbidden here).
- No inferences from download counts: install counts can't distinguish "working" from "broken-but-silent" (cli-telemetry-spec insight [§8]). Local ledgers + issue reports are the honest signals.
- **Stated honestly (M23)**: telemetry-free tracking has a blind spot — silent users who never report are invisible. Removal decisions therefore weigh elapsed-window + registry discipline more heavily than usage data, and removals may be deferred indefinitely when uncertainty is high (MCP allows features to stay Deprecated longer than the minimum [§5]).

---

## §5 Stage 4 — REMOVE

**Preconditions checklist (all must hold)**:

- [ ] Minimum window elapsed (R2) — verified against registry dates, not memory.
- [ ] Replacement confirmed Active and documented (MCP removal discipline [§5]).
- [ ] Local ledger shows declining-or-flat hits AND no open blocker issues citing the shim (best-effort signal; see §4 honesty note).
- [ ] Architect sign-off recorded in PIVOT_LOG (decision, not automatic event).

**Execution**:

- Delete shims in the release named in the registry; NEVER earlier, rarely later (later is fine — MCP: features may remain Deprecated much longer than the minimum [§5]).
- Update registry page: row moves to a **Removed** section with changelog link (MCP registry pattern [§5]).
- Release notes item under `## Backward-Incompatible Changes`: "Removed `<old>` as scheduled since v<dep>. Use `<new>`."
- CI permashim check passes (no shim older than its registered removal version).

---

## §6 Stage 5 — LEARN

Covered in depth by the companion doc `REHEARSAL_LEARNING_PLAN_20260822_v6.md`. Summary:

1. Blameless post-mortem within one week of migration completion (Google SRE 8-section format adapted, single-owner action items).
2. Distill L1→L2→L3 into overseer's proposed_lessons.yaml tagged `[MIG]` (SO-10a structured-gnosis format).
3. Update this playbook with any new pattern/gotcha discovered (the playbook itself is a living KB per Standing Order 8 curation duty).
4. Corpus Map row for the migration's evidence trail.

---

## §7 User-Facing Migration Guide Template

Every migration ships ONE guide at `docs/migrations/<mig-id>.md`, LLM-friendly per M26:

```markdown
---
schema_version: "1.0"
document_type: "guide"
document_id: "<mig-id>"
title: "Migrating <old> → <new>"
status: "ACTIVE"
version: "1.0.0"
date: "<YYYY-MM-DD>"
owner: "<entity>"
tags: ["migration", "<surface>"]
llm_metadata:
  token_budget: 1500
  chunk_strategy: "flat"
  answer_first_sections: true
  self_contained_code: true
---
# Migrating <old> → <new>

## What changed
One paragraph: what breaks, for whom, starting which version.

## Why
The reason (HA lesson: users accept changes they understand [§6]).

## Am I affected?
Run: `omega doctor --deprecations`  → paste-ready output names your hits.

## Migrate (mechanical)
If codemod exists:
    omega migrate <mig-id> --diff     # dry run
    omega migrate <mig-id>            # apply
Else: before/after table + sed recipe.

## Migrate (semantic)
Checklist of behavioral differences requiring human judgment
(the bump-pydantic 20% [§7]); each with a verification step.

## Verify
Commands/tests proving the migration worked.

## Timeline
Deprecated in vX.Y · Removed no earlier than vX'.Y' · Registry link.
```

Guide-writing rules distilled from case studies:
- Lead with a copy-paste detection command (users can't follow instructions if they can't tell whether they're affected).
- Separate mechanical from semantic steps explicitly (Pydantic two-layer doctrine [§3]).
- State the deadline in BOTH relative ("two releases") and absolute terms (K8s warning text includes removed_release [§4]).
- Include rollback guidance (HA automatic-backup guarantee mindset [§6]).
- Keep under token budget; link out for depth (M18/M26).

---

## §8 Application to the Live Pillar→Slots Migration (D180)

Mapping the playbook onto Roc Racoon's existing plan (`PILLAR_REFACTOR_PLAN_20260822.md`) — what the playbook ADDS beyond that plan:

| Playbook element | Pillar→slots application | Status |
|------------------|--------------------------|--------|
| Registry page | Create `docs/reference/DEPRECATIONS.md`; seed with pillar→slots rows (MCP tool name, response fields, YAML key, SPIFFE path) | NEW — refactor plan lacks it |
| Runtime warnings | Legacy tool name/field/YAML-key use emits `warn_deprecated()` + local ledger hit | NEW — plan deletes outright |
| Shim window | Plan Phase 1–3 executes the rename; playbook adds: keep legacy aliases until ≥2 releases post-debut OR 12 months | AMENDS plan timing |
| Codemod decision | WAD entities.yaml `pillars:`→`slots:` = mechanical, ~70 entries → scripted YAML transform already drafted in plan Phase 3 ✅; MCP response field consumers = semantic → characterization tests first | CONFIRMS plan approach |
| Tracking | `omega doctor --deprecations` + issue template field | NEW |
| Learning | Post-mortem after Phase 5 sign-off → L1/L2/L3 staged | NEW |

**Sequencing note**: Roc's plan optimizes for internal test-suite greenness NOW (pre-debut). The playbook layer applies POST-debut when external users exist. Recommended order: execute Roc Phases 0–5 as planned (internal clean-up), THEN register the MCP-tool rename in DEPRECATIONS.md with a shim window for any external consumers who cloned pre-debut.

---

## §9 Open Questions (for Architect ruling)

1. **Release cadence assumption**: R2's "2 release cycles" presumes a predictable cadence (Django ≈8mo, HA monthly). Omega cadence post-debut is undefined — should the binding constraint be time-based (12 months) regardless of cycle count?
2. **Registry location**: `docs/reference/DEPRECATIONS.md` vs `docs/sprints/current/deprecations.md`? Reference-doc placement fits DOC_STYLE_GUIDE Category 1 (Omega header required) and survives sprint archival.
3. **Does `omega doctor` belong to N8 watchtower charter?** The self-diagnostic command is an observability surface; N8 owns metrics/provenance. Suggest paging N8 at implementation time.
4. **Shim CI gate ownership**: the anti-permashim CI check is a verifier concern (N10) — fold into `make temple-grade` T-gates or standalone target?

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT ⬡ 2026-08-22*
