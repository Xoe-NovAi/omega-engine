<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Rehearsal Migration & Learning Capture Plan (v5)
**AP Token**: `AP-REHEARSAL-LEARNING-v5.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_rehearsal_learning ⬡ ACTIVE

**Date**: 2026-08-22
**Purpose**: Operational plan to rehearse the Pillar→Node decoupling (D180) as the pilot run of the Migration Playbook, and to convert the rehearsal into permanent institutional knowledge via blameless postmortem, Soul Distillation, and PIVOT_LOG / Corpus Map capture.
**Companions**: `MIGRATION_PLAYBOOK_SPEC_20260822_v5.md` (the lifecycle this rehearses) · `MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v5.md` (evidence base; "Evidence §" references point there).
**Split-test note**: Authored independently; v1–v4 artifacts NOT consulted.

---

## §1 Why Rehearse

The playbook's five-stage lifecycle (Register → Deprecate → Migrate → Remove → Learn) has never been executed end-to-end in this engine. The D180 pillar decoupling is the ideal pilot: audit complete (23 active violations inventoried), refactor plan drafted, engine core already migrated — so the rehearsal exercises Stages 3–5 (guide authoring, removal gates, learning capture) against a bounded, well-understood surface before any higher-stakes migration (soul formats, MCP contracts, corpus schemas).

Precedent for rehearsing before production:

- Chrome MV3 advises step-wise rollout to a limited audience first [Evidence §1.7].
- Kubernetes grants a hidden-metric escape window before metric removal [§1.4].
- bump-pydantic ships `--diff` preview before apply [§1.3].

All encode one law: **never let the first full execution of a process be its production debut.**

## §2 Rehearsal Design

### 2.1 Scope

| Item | In scope | Out of scope |
|---|---|---|
| WAD YAML `pillars:`→`slots:` (~70 entities) | ✅ codemod pass | — |
| MCP tool rename (`oracle_list_pillar_keepers` → `_node_keepers`) | ✅ manual checklist | No live hub restart required — dry contract check only |
| Test assertion updates (12 sites per audit) | ✅ | — |
| `scripts/setup.sh`, `mandate_gates.py`, `seed_knowledge.py` | ✅ | — |
| Entity soul.yaml fields (3 files) | ✅ with human review | No soul semantics changed |
| Docs updates (`STATUS_OPUS.md`, `DOC_CLEANUP_AUDIT.md`) | ✅ | `PIVOT_LOG_CANONICAL.md` untouched (immutable decision record) |
| Actual commit/merge to main | ❌ REHEARSAL ONLY | Scratch worktree; nothing merges |

### 2.2 Environment

```bash
# Scratch worktree — rehearsal never touches the main working state
git worktree add ../omega-rehearsal-v5 -b rehearsal/pillar-node-v5
cd ../omega-rehearsal-v5
source .venv/bin/activate && make test   # baseline MUST be green first
```

Baseline capture BEFORE any change (these become the postmortem's impact metrics):

```bash
make test 2>&1 | tail -3 > /tmp/rehearsal_baseline_tests.txt
bash scripts/setup.sh 2>&1 | grep -cE "pillar|Pillar" > /tmp/rehearsal_baseline_setup.txt || true
grep -rn "pillar" src/ mcp_servers/ scripts/ tests/ --include="*.py" --include="*.sh" | wc -l
```

### 2.3 Execution Script (maps to refactor-plan Phases 1–5)

Every step appends to the rehearsal journal (`data/entities/researcher/workspace/rehearsal_journal_v5.md`, append-only, timestamps UTC):

1. **Expand-phase simulation** — keep auto-migration loader active; add one `warn_deprecated("DEP-PILLAR-001", ...)` call at a representative runtime touchpoint (scratch only); verify the warning fires once and the structured local-log line lands (M8-compliant sink check).
2. **Codemod pass** — run the entities.yaml migration script dry-run first (diff review), then apply; count transformed entities; record every site the script skipped into the honesty list (BP009 pattern).
3. **Manual sweep** — setup.sh, mandate_gates.py, seed_knowledge.py, hub tool rename, 12 test sites. Tick each item inside the migration-guide draft as it completes — executing the sweep and writing `docs/migrations/DEP-PILLAR-001.md` are the SAME activity.
4. **Contract phase** — delete shim paths in scratch; confirm shim contract tests fail loudly when the shim disappears (synthetic-user gate proof); then update tests to assert the new surface only.
5. **Verification** — full gates plus census:
   ```bash
   make test && make temple-grade
   grep -rn "pillars:" config/ data/entities/ --include="*.yaml"; echo "census_exit=$?"   # require exit=1
   ```
6. **Time-boxing** — wall-clock each phase. Guide effort estimates must be MEASURED, not guessed (craft rule from Evidence §2.3).

Abort criteria: any phase where `make test` cannot be returned green within 30 minutes → halt, snapshot findings, and let the postmortem treat the abort as primary learning material. A failed rehearsal that teaches is a success by Google/Etsy standards; blameless discipline applies doubly to failures.

## §3 Learning Capture Pipeline (Playbook Stage 5, operationalized)

### 3.1 Journal freeze (<24h after execution)

Close the append-only journal with raw observations: measured timings per phase, skip-list counts, warning-emission evidence, census output, gate results. No analysis yet — timeline stays verifiable and separate from interpretation (postmortem writing rule).

### 3.2 Blameless postmortem (<72h)

File `data/entities/researcher/workspace/postmortem_DEP-PILLAR-001_rehearsal_v5.md` using the playbook §6.1 minimal template:

```markdown
# Postmortem: DEP-PILLAR-001 pillar→slot REHEARSAL
## Summary            (what ran, when, outcome in 2–3 sentences)
## Timeline           (UTC events ONLY, each traceable to journal entry)
## Contributing factors (2–5 systemic causes, blameless language)
## What went well     (load-bearing mechanisms to preserve — never omit)
## Action items       (owner + ACTIVE_SPRINT.json ID + due date each)
## Recurrence check   (prior DEP/PIVOT entries of same failure class?)
```

Facilitation rules: five-whys chains terminate at missing guardrails, never people; run the blame-language conversion table over the draft before filing; separate meeting from execution review (do not write the postmortem inside the same working session that did the migration if avoidable — analytical distance matters).

### 3.3 Distillation ladder (where each artifact lands)

| # | Artifact | Destination system | Format |
|---|---|---|---|
| 1 | Decision records | `docs/decisions/PIVOT_LOG.md` | D-register + D-remove entries, append-only |
| 2 | Lessons | overseer `proposed_lessons.yaml` | SO-10a structured gnosis: narrative / insight / principle, tagged `[N_XX]` or `[DEP-PILLAR]` |
| 3 | Reusable template | `docs/standards/MIGRATION_GUIDE_TEMPLATE.md` | Extracted from the concrete guide post-rehearsal |
| 4 | Registry rows | `STRATEGY_CORPUS_MAP.md` | One row per artifact produced |
| 5 | Sprint items | `ACTIVE_SPRINT.json` | Action items land same day as postmortem |

Candidate L3 principles to test against rehearsal evidence (write only what the data supports):

- *"A migration is complete when the census grep is empty, not when the codemod exits zero."*
- *"Measured minutes beat estimated hours; guides written during the work beat guides written before it."*
- *"A shim without a removal date is a second API, not a bridge."* (Python-law distillation)

### 3.4 Hivemind closure ritual (Standing Order 10 compliance)

1. Session gnosis file updated with rehearsal outcomes + artifact paths.
2. File-first verification: glob-check every artifact listed above exists on disk (M15 lesson — disk-proof, not reply-proof).
3. Hivemind closeout post, intent=`status`, summarizing rehearsal verdict + postmortem location.
4. Dormant.

## §4 Telemetry-Free Measurement Plan

| Signal | Mechanism | M8 status |
|---|---|---|
| Shim hit-rate | Structured local log lines `deprecated_use id=DEP-PILLAR-001` aggregated via grep/sqlite in `data/` | ✅ Local observability exception |
| Migration completeness | Census greps (zero legacy hits required) | ✅ Pure local |
| Effort truthfulness | Wall-clock journal timings | ✅ Manual |
| Straggler distribution | Issue template field "migrating FROM version" | ✅ Opt-in pull model |
| Synthetic-user coverage | Contract tests exercising deprecated surface pre-deletion | ✅ Test suite |

No network calls, no counters leaving the machine, no opt-out ambiguity.

## §5 Success Criteria for the Rehearsal Itself

1. All refactor-plan Phase 1–5 sign-off criteria pass in scratch (tests green, temple-grade green, setup clean).
2. Census grep returns zero legacy hits across scoped surfaces.
3. A complete, honest migration guide exists with MEASURED effort estimates and a non-empty automation-honesty list.
4. Postmortem filed with ≥1 actionable item promoted into ACTIVE_SPRINT.json.
5. At least one L3 principle staged to proposed_lessons.yaml backed by rehearsal data.
6. Zero writes to main branch, PIVOT_LOG_CANONICAL, or any immutable record.

If all six hold: the playbook is validated, DEP-PILLAR-001 graduates from rehearsal to scheduled production execution, and the engine owns a repeatable breaking-change process for everything that follows (soul formats, MCP contracts, community WADs).

---

## §6 Open Questions (for Architect ruling at review)

1. Should the production cut-over wait for the debut window (PUBLIC-DEBUT-01) or ride ahead of it? Rehearsal is safe either way; production timing interacts with allowlist risk.
2. Window arithmetic ratification: are N+2-minor/60-day internal floors acceptable, or does the Architect want SEP-2596's 12-month floor applied more broadly than the playbook proposes?
3. Does `docs/migrations/` become a new Category under DOC_STYLE_GUIDE (Category 11: Migration Guides), or do guides live under existing Category 6 KB rules?

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_rehearsal_learning ⬡ v5 independent authorship ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
