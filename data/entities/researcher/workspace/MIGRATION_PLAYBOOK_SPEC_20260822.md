<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Breaking Change on a Live Repo — Migration Playbook Spec (Rehearsal Instantiation)
**AP Token**: `AP-RESEARCHER-MIGRATION-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-22
**Status**: PROPOSED — awaiting Kali ratification as standing playbook
**Scope**: Standing process for MAJOR breaking changes (schema/tool renames) on a live user base; instantiated here for the Pillar→Node decoupling rehearsal (Roc Racoon `PILLAR_REFACTOR_PLAN_20260822.md`, D180).
**Evidence base**: `MIGRATION_CASE_STUDIES_EVIDENCE_20260822.md` (same directory). Section refs `[E§n]` point there.
**Doc standards**: Written per `docs/standards/DOC_STYLE_GUIDE.md` / `LLM_FRIENDLY_DOCS_BP.md` (M26): hierarchical headers, tables, code blocks, self-contained sections, no orphan references. If promoted to a sprint, generate `llms.txt`/`llms-full.txt` via `make sprint-plan-llm` and pass `make doc-llm-validate`.

---

## L1 Executive Summary

Mature projects handle breaking changes on live users with five invariants: **(1)** a written deprecation policy with a guaranteed shim lifetime, **(2)** an Expand-Contract sequence — add the new name and dual-read shims BEFORE removing the old, **(3)** a migration guide structured old→new with escape hatches, **(4)** loud local signals at the point of deprecated use (runtime warnings + grep recipes), never covert telemetry, **(5)** a blameless post-mortem distilled into permanent decision records. This spec turns those into a 7-phase playbook with gates, artifacts, and comms cadence, then instantiates it for our Pillar→Node rehearsal. Because the repo is pre-debut, we compress timelines but run every phase anyway — the rehearsal's product is the tested process itself.

---

## 0. The Deprecation Policy (write once, reuse forever)

Before any migration, the project needs a published promise `[E§2, E§3]`. Adopt:

| Rule | Omega Engine value | Precedent |
|---|---|---|
| Versioning | SemVer; breaking changes only in MAJOR | Pydantic, standard OSS |
| Shim lifetime post-debut | ≥ 2 minor releases minimum (PyTorch ExecuTorch model); target 12 months for protocol-level contracts (MCP SEP-2596) | [E§1, E§3] |
| Deprecation marking | Runtime `DeprecationWarning`-class warning + static-visible decorator + docs entry, each naming replacement AND removal version | PEP 702, Django `RemovedInDjangoXXWarning` [E§4, E§5] |
| Removal scheduling | Removals land only at MAJOR boundaries, never mid-minor | Kubernetes API policy [E§2] |
| Escape hatch | Compat import path (`omega.legacy.pillars`) kept until removal version | `pydantic.v1` [E§1] |
| Expedited removal | Security-only, ≥ 90 days notice | MCP SEP-2596 [E§3] |
| Guide freshness | Every migration guide has a named owner + freshness check each release (k8s guide rot lesson) | [E§2 finding 5] |

**Artifact P0**: `docs/reference/DEPRECATION_POLICY.md` (one page). This is the single highest-leverage post-debut artifact — MCP's policy was adopted exactly when its user base exploded.

## 1. The Seven Phases

### Phase A — Decision & Contract Freeze
- **Do**: Write the change as an ADR-shaped entry in `PIVOT_LOG.md` (Nygard: Context/Decision/Consequences) `[E§9]`. Define the NEW contract precisely (types, field names, error semantics) before touching code. Error/message formats are contract too `[E§1 finding 5]`.
- **Gate G-A**: New contract documented; old contract enumerated (every public symbol touched); removal version declared.
- **Rehearsal instantiation**: DONE — D180 ruling + Roc Racoon audit define slots/metadata end-state and enumerate 23 M2 violations.

### Phase B — Expand (add new before removing old)
- **Do**: Ship new names alongside old. Dual-name shims: old name delegates to new implementation, emits warning. Both names fully tested. Kubernetes' "replacement available since vX" pattern applies: users must be able to move BEFORE anything breaks.
- **Gate G-B**: 100% of new surface covered by contract tests (M21); shims pass-through identical behavior; test suite green on both paths.
- **Rehearsal note**: Roc's plan goes straight to rename (pre-debut privilege). For rehearsal fidelity, implement shims ANYWAY — they are the thing being practiced.

### Phase C — Emit Signals (loud, local, zero-telemetry)
- **Do** `[E§8]`: Each shim hit → (1) runtime `DeprecationWarning` naming replacement + removal version; (2) one line to local `data/logs/deprecations.log` with trace_id; (3) increment local counter readable via a doctor-style command.
- **Ship**: grep recipes / ast-grep rules in the migration guide so users can scan their own code; CI tripwire recipe (`-W error::DeprecationWarning` equivalent).
- **Gate G-C**: warning text reviewed for actionability ("use X instead; Y removed in Z"); M8 audit confirms no external transmission.

### Phase D — Publish Migration Guide
- **Structure** (validated against pydantic/k8s/MCP guides) `[E§1, E§2, E§3, Deska E§7]`:
  1. Executive summary: affected versions, estimated effort, WHY (motivation buys patience)
  2. Old→New comparison table (fastest parity view)
  3. Before/after code blocks per use case — including edge cases and failure modes, not just happy path
  4. Automated path first (codemod/grep commands), manual path second
  5. Troubleshooting: common error messages of the NEW version and fixes
  6. Escape hatch section (compat import) with its expiry date
  7. Changelog entry using Keep-a-Changelog taxonomy under "Changed"/"Removed" cross-linked from guide
- **Comms cadence post-debut**: announce at deprecation release (blog/changelog/discussions), remind at each release until removal, final "removal next release" notice. Pre-debut rehearsal: internal Hivemind posts substitute.
- **Gate G-D**: guide passes `make doc-llm-validate`; a non-author agent completes a dry-run migration on a fixture repo using ONLY the guide (the "stranger test").

### Phase E — Support Window (shim life)
- **Do**: Monitor LOCAL signals only: deprecations.log volume in your own runs, issue-template reports, opt-in `report-deprecations` pastes. Triage feedback like k8s does: "users who weren't involved originally may have good arguments not to remove" `[E§ PyTorch policy]`.
- **Rule**: removal date may slip on evidence; it may never arrive early except security `[E§4 finding 2 — CPython reverted a removal]`.
- **Gate G-E**: evidence log shows shim hit-rate trend; go/no-go memo for removal.

### Phase F — Contract (remove)
- **Do**: Rehearse removal FIRST via config flag disabling shims (k8s `--runtime-config=…=false` pattern) `[E§2 finding 3]`. Then delete shims in a MAJOR release; changelog "Removed" section links guide; guide gets a "this migration is complete as of vX" tombstone.
- **Gate G-F**: full suite green with shims deleted AND with shim-disable flag flipped; no dead imports remain (grep gate).

### Phase G — Post-Mortem & Distillation
- **Do**: Blameless review within one week of removal `[E§9]`. Format below (§3). Distill L1→L2→L3 into entity souls; file decisions in PIVOT_LOG; update this playbook with deltas.
- **Gate G-G**: post-mortem published; ≥1 L3 candidate recorded; playbook updated (version bump).

## 2. Rehearsal Instantiation Map (Pillar→Node)

| Playbook phase | Roc Racoon plan coverage | Rehearsal addition required |
|---|---|---|
| A Decision | ✅ D180 + audit | None |
| B Expand | ❌ direct rename | Add `pillars` property shim delegating to `slots` + warning (temporary, flagged as rehearsal-only) |
| C Signals | ❌ | Warning emission + local deprecations.log line in shim |
| D Guide | ❌ | Write mini-guide even though audience is internal agents/scripts — exercises the format |
| E Support | N/A (compressed) | Simulate: run suite twice, second time with shims disabled |
| F Contract | ✅ phases 1–4 | Add explicit shim-deletion step + flag-flip rehearsal |
| G Post-mortem | ❌ | This playbook's §3 template, executed |

## 3. Migration Post-Mortem Template (blameless, maps to our systems)

```markdown
# Migration Post-Mortem: <name> (<old> → <new>)
## Impact        — what broke/would have broken for users; counts from local logs
## Timeline      — decision → expand → signal → guide → support → removal dates
## What Went Well        — systemic factors that helped
## What Went Poorly      — systemic factors (NO NAMES; "CI lacked X", not "agent forgot Y")
## Lucky Escapes         — near-misses caught by accident
## Action Items          — [] AI-nn <verb> <system change> by <date> (owner) — tracked in TASK_REGISTRY
## Distillation
  L1 (Narrative): what happened
  L2 (Insight):   why it worked/failed structurally
  L3 (Universal): timeless principle → proposed_lessons.yaml
```
Google SRE rule adopted verbatim: *"a postmortem without subsequent action is indistinguishable from no postmortem"* — every post-mortem needs ≥1 tracked action item `[E§9]`.

## 4. Codemod Decision Rule

Build an automated migrator iff ALL of: (a) syntactically detectable pattern, (b) ≥ ~20 call sites, (c) pattern class recurs across future migrations. Tool choice: **ast-grep YAML rules** for mechanical renames (pip-installable, matches our Bash-first tooling); **LibCST** only if transforms need comment/formatting preservation or logic. Otherwise publish grep recipes in the guide and let AI agents execute them against user repos (2026 norm) `[E§7]`.
For THIS rehearsal: 23 violations across scripts/tests/WAD-YAML — borderline. Recommend ast-grep rules as practice artifacts even if manual fixing is faster, because the rules are reusable post-debut.

## 5. Anti-Pattern Register (learned from failures)

1. Big-bang without dual-run path (Python 2→3 decade stall) `[E§4]`
2. Calendar-driven removal despite evidence users aren't ready (CPython 3.11 reverts) `[E§4]`
3. Silent degradation instead of loud errors (MCP servers pre-2026-07-28) `[E§3]`
4. Breaking error-message formats while APIs "didn't change" (pydantic ValidationError) `[E§1]`
5. Unowned migration guides that rot (k8s website issue #51011) `[E§2]`
6. ADR sprawl — decisions, runbooks, guides conflated into one doc class `[E§9]`

---
*Next artifact: `REHEARSAL_LEARNING_PLAN_20260822.md`. Ratification: Kali.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
