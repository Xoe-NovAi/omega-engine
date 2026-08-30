# 🔱 Migration Playbook Spec — Breaking Changes on a Live Repo (Canonical Merge)
**AP Token**: `AP-MIGRATION-PLAYBOOK-SPEC-v1.1.0`
⬡ OMEGA ⬡ RESEARCHER+KALI ⬡ opencode ⬡ trc_migration_playbook ⬡ MERGED-DRAFT

**Date**: 2026-08-22
**Status**: MERGED DRAFT — awaiting Kali ratification → promotion to `docs/migrations/MIGRATION_PLAYBOOK.md`
**Provenance**: Canonical merge of `MIGRATION_PLAYBOOK_SPEC_20260822.md` (fresh-session run, Ox Alpha `x-preview-f-free`, low thinking — DB-verified) + `MIGRATION_PLAYBOOK_SPEC_20260822_v2.md` (primed-session run, Nemotron 3 Ultra, high thinking — DB-verified). Split-test analysis: `data/coordination/SPLIT_TEST_ANALYSIS_20260822.md`.
**Companion**: `REHEARSAL_LEARNING_PLAN_20260822_MERGED.md` (same directory)
**Tags**: migration, deprecation, semver, rehearsal, postmortem, M8, M18, M21, M26

---

## Answer First

When Omega Engine must make a breaking change on a live user base, execute the **5-phase Expand-Contract lifecycle** (§1). Five invariants recur across every mature project studied (Pydantic, Kubernetes, MCP, Django, Python, Home Assistant): **(1)** never remove before the replacement ships AND warns — dual-name shims with a policy-bound lifetime; **(2)** the migration guide is written BEFORE the breaking code lands; **(3)** removal timing is policy-bound (version-count or months), never mood-bound — CPython reverted a calendar-driven removal; **(4)** deprecation signals live in the user's OWN environment (runtime warnings, local logs, opt-in reports) — zero covert telemetry (M8); **(5)** every migration ends in captured institutional knowledge (blameless postmortem → PIVOT_LOG → soul lessons), which is why each project's SECOND migration is smoother than its first.

---

## §0 The Deprecation Policy (write once, reuse forever — P0 artifact)

**Artifact P0**: `docs/reference/DEPRECATION_POLICY.md` (one page). Must exist BEFORE the first live breaking change — MCP adopted theirs exactly when their user base exploded. Every row below is precedent-backed `[E§n]` = `MIGRATION_CASE_STUDIES_EVIDENCE_20260822*.md` section ref.

| Rule | Omega Engine value | Precedent |
|---|---|---|
| Versioning | SemVer; breaking changes only in MAJOR | Pydantic, standard OSS [E§1] |
| Shim lifetime — GA public surface | ≥12 months or 4 minor releases, whichever longer | k8s CLI GA track (12mo/2-rel), LTS norm 6–12mo [E§2, E§7] |
| Shim lifetime — beta/experimental surface | ≥3 months or 1 release | k8s beta track [E§2] |
| Shim lifetime — alpha/`_omega_default`-internal | May remove next release, notice required | k8s alpha track [E§2] |
| Expedited removal | Security-only, ≥90 days notice | MCP SEP-2596, Django accelerated [E§3, E§5] |
| Deprecation marking | Runtime warning + static-visible decorator + docs entry, each naming replacement AND removal version | PEP 702, Django `RemovedInDjangoXXWarning` [E§4, E§5] |
| Removal scheduling | Removals land only at MAJOR boundaries, never mid-minor | Kubernetes API policy [E§2] |
| Warn-everything rule | Last minor release of a major MUST warn about everything the next MAJOR removes | SemVer guide practice ("1.9.0 warns about 2.0.0 removals") [E§7] |
| Escape hatch | Compat import path (`omega.legacy.pillars`) kept until removal version; shims have natural death dates set by dependencies too | `pydantic.v1`; pydantic v1 killed by Python 3.14 [E§1] |
| Guide freshness | Every migration guide has a named owner + freshness check each release | k8s website issue #51011 guide-rot incident [E§2] |

## §1 The 5-Phase Lifecycle (Expand → Contract)

```
Phase 0      Phase 1        Phase 2         Phase 3         Phase 4
INTRODUCE    DEPRECATE      DUAL-RUN        REMOVE          LEARN
new name     warn on old    old+new both    delete old      postmortem
ships first  name at        work (shim);    in MAJOR        → institutional
             runtime        docs versioned  release         knowledge
```

| Phase | Gate to enter | Artifacts produced | Owner |
|-------|--------------|-------------------|-------|
| **0 Introduce** | Design ADR merged into PIVOT_LOG (Nygard: Context/Decision/Consequences); NEW contract precisely defined (types, field names, error semantics — error formats are contract too [E§1]) | New name/tool/schema live alongside old; zero behavior change | N3 buildmaster |
| **1 Deprecate** | Replacement at feature-parity (contract tests green, M21) | Runtime `DeprecationWarning` on old path; changelog entry (`DEPRECATED:` taxonomy); migration-guide DRAFT opened | N10 verifier (tests) + N4 bridge (docs) |
| **2 Dual-run** | Migration guide COMPLETE (before/after examples incl. edge cases & failure modes) | Shim active; `docs/migrations/<change-id>.md` published; local hit-counter logs shim invocations | N3 + N12 curator |
| **3 Remove** | Shim age ≥ policy floor (§0) AND no open `migration-blocker` issues AND flag-flip rehearsal clean (§4) | Old path deleted in MAJOR release; removal note + tombstone in guide; codemod updated if applicable | N3 |
| **4 Learn** | ≤14 days after removal release | Blameless postmortem (§8) → PIVOT_LOG entries → L1/L2/L3 soul distillation → playbook amendment PR | Researcher + Scribe |

**Kali gate approvals**: Phase 1 (deprecate) and Phase 3 (remove). Every approval/rejection with rationale becomes a PIVOT_LOG entry — the decision trail IS the deliverable.

## §2 User-Facing Communication Craft

1. **Changelog taxonomy** (fixed vocabulary, machine-greppable): `ADDED:` · `CHANGED:` · `DEPRECATED:` (with removal target version) · `REMOVED:` · `MIGRATION:` (pointer to guide section).
2. **Runtime warnings**: Python `DeprecationWarning`, fixed message format: `[omega-deprecation] <old> is deprecated since <ver>, use <new>; removal in <ver>. See docs/migrations/<id>.md`. Static counterpart: PEP 702 `@warnings.deprecated()` decorator (warns at type-check time AND runtime).
3. **Migration guide structure** (validated against pydantic/k8s/MCP guides [E§1–3]):
   1. Executive summary: affected versions, estimated effort, WHY (motivation buys patience)
   2. Old→New comparison table (fastest parity view)
   3. Before/after code blocks per use case — edge cases and failure modes, not just happy path
   4. Automated path first (codemod/grep commands), manual path second
   5. Troubleshooting: common error messages of the NEW version and fixes
   6. Escape hatch section (compat import) with its expiry date
   7. Changelog entry cross-linked under `Changed:`/`Removed:`
4. **Version the docs**: guides live under `docs/migrations/v<MAJOR>/`; old-major docs frozen, not deleted.
5. **Announce cadence post-debut**: announce at deprecation release (Release notes + pinned Discussion + README banner on old major branch), remind each release until removal, final "removal next release" notice. Home Assistant pattern: dedicated user-first "Breaking Changes" section published BEFORE the release, separate from technical changelog [E§6].
6. **Reactive mode**: when an upstream DEPENDENCY breaks itself (e.g., MCP spec revisions), run the same artifacts (guide/shim/gate) driven by upstream changelogs instead of our roadmap.

## §3 Telemetry-Free Usage Tracking (M8-compliant)

We cannot phone home. Local-first instruments only:

| Instrument | Mechanism | Signal harvested |
|---|---|---|
| **Runtime warnings** | `warnings.warn(..., DeprecationWarning)` with stable `[omega-deprecation]` prefix | Users see own usage; CI runs `-W error::DeprecationWarning` to fail fast |
| **Local shim counter** | Shim increments JSONL line in `data/telemetry-local/shim_hits.jsonl` (path, count, timestamp) — stays on user machine | Opt-in `omega report-shims` prints paste-ready summary for issues |
| **Local deprecations log** | One line per shim hit → `data/logs/deprecations.log` with trace_id | User + issue templates; readable via doctor-style command |
| **Issue template** | `.github/ISSUE_TEMPLATE/migration-blocker.yml`: which guide step failed, shim-hit summary pasted voluntarily | Unanticipated blockers (Pydantic "bug V2" label pattern) |
| **Contract-test census** | Own repo + shipped WADs run dual-name greps (`ast-grep`) in CI | Internal leak detection (automates Roc's Pillar Leak Audit) |
| **Grep recipes** | Published patterns users run against their own code | Users |

Precedent: Kubernetes attaches signals to responses/audit events/metrics the operator already sees locally — visibility without exfiltration [E§2]. No successful OSS project surveyed uses covert telemetry for this.

## §4 Removal Rehearsal (before Phase 3 fires)

Flip a config flag that disables all shims while they still exist (k8s `--runtime-config=<group>/<version>=false` pattern [E§2]). Run full suite + setup.sh. Any new failure = hidden dependency grep missed. Gate G-F requires green with shims deleted AND with shim-disable flag flipped.

## §5 Codemod Decision Rule

Build an automated migrator iff ALL hold: (a) syntactically detectable (AST-matchable); (b) >~20 call sites across user codebases; (c) rewrite is semantics-preserving AND the pattern class recurs across future migrations. Otherwise: manual guide + grep recipes.

Tooling SOTA 2026: **ast-grep** (Rust CLI, polyglot, YAML-aware — covers our .py AND config/WAD layers; primary choice) · **libcst** (format-preserving Python CST — only if comments/formatting must survive) · OpenRewrite (JVM-heavy, skip) · GritQL/Comby (alternatives). Hybrid pattern: deterministic AST match → optional LLM rewrite of matched block → **tests must pass before human diff review** (Google study, 39 migrations/12mo: 74% of edits AI-generated, 87% committed unmodified, timelines cut ~50% — but validation dominated human time [E§8]).

For THIS rehearsal: 23 violations, mostly scripts/tests/YAML → ast-grep ruleset (`pillar-leak.yml`) is right-sized; rules double as reusable post-debut practice artifacts even if manual fixing is faster.

## §6 Roles & Gates Summary

- **N3 buildmaster**: versioning, release cutting, LTS branch tag, codemod packaging
- **N10 verifier**: contract tests for BOTH paths during dual-run; `-W error` CI gate; removal-PR gate checks guide completeness
- **N4 bridge**: migration guides, changelog taxonomy enforcement, announcement drafts, `docs/migrations/SCHEDULE.md` (single canonical removal schedule — Django timeline pattern)
- **N8 watchtower**: local shim-counter implementation + dual-run health
- **N12 curator**: versioned doc tree, guide discoverability, llms.txt regeneration (`make sprint-plan-llm`)
- **Researcher + Scribe**: Phase-4 learning capture (postmortem → PIVOT_LOG → soul)
- **Kali**: gate approvals at Phase 1 and Phase 3

## §7 Rehearsal Instantiation Map (Pillar→Node vs Roc Racoon's plan)

Roc's `PILLAR_REFACTOR_PLAN_20260822.md` covers phases A/F-equivalents but SKIPS Expand/Signal/Guide — exactly the phases this rehearsal exists to practice.

| Playbook phase | Roc plan coverage | Rehearsal addition required |
|---|---|---|
| 0 Introduce | ✅ D180 + audit | None |
| 1 Deprecate | ❌ direct rename | `pillars` property shim delegating to `slots` + warning (rehearsal-only) |
| 2 Dual-run | ❌ | Warning emission + local deprecations.log line in shim; mini-guide even though audience is internal (exercises the format) |
| 3 Remove | ✅ phases 1–4 | Add explicit shim-deletion step + flag-flip rehearsal (§4) |
| 4 Learn | ❌ | §8 template executed; learning plan (companion doc) |

## §8 Migration Postmortem Template (blameless, canonical)

Lands at `docs/migrations/postmortems/<change-id>.md`; passes `make doc-llm-validate`.

```markdown
# Migration Postmortem: <change-id> (<old-name> → <new-name>)
## Summary            — 3 sentences max: what moved, when shipped, final state
## Impact             — surfaces touched, WADs affected, user-visible deltas;
##                      counts from local logs
## Timeline           — Phase 0→4 dates with gate approvals (Kali sign-offs)
## What Went Well     — systemic factors that helped
## What Went Wrong    — systemic factors ONLY ("The system made X the easiest
##                      path" — never "agent X forgot Y")
## Where We Got Lucky — near-misses that gates happened to catch
## Predictions Audit  — score pre-registered hypotheses (H1..Hn): hit/miss
## Playbook Deltas    — concrete amendments to THIS spec (each = one
##                      PR-ready sentence + rationale)
## Action Items       — [ ] AI-Nn <verb> <system change> by <date> (@owner),
##                      tracked in TASK_REGISTRY
## Distillation       — L1 narrative → L2 insight → L3 universal principle
##                      → proposed_lessons.yaml (SO-10a staging)
```

Google SRE rule adopted verbatim: *"a postmortem without subsequent action is indistinguishable from no postmortem"* — every post-mortem needs ≥1 tracked action item [E§9].

## §9 Anti-Pattern Register (learned from others' failures)

1. Big-bang without dual-run path (Python 2→3 decade stall) [E§4]
2. Calendar-driven removal despite evidence users aren't ready (CPython 3.11 reverts) [E§4]
3. Silent degradation instead of loud errors (MCP servers pre-2026-07-28) [E§3]
4. Breaking error-message formats while APIs "didn't change" (pydantic ValidationError) [E§1]
5. Unowned migration guides that rot (k8s website #51011) [E§2]
6. ADR sprawl — decisions, runbooks, guides conflated into one doc class [E§9]
7. Silent semantic changes under identical-looking names (k8s empty `spec.selector` flip) [E§2]

## §10 Verification Flags (carry into execution)

- ⚠️ Home Assistant citations: fresh-session run cites HA URLs; primed run could not confirm primary-policy pages above threshold. Spot-check before promoting HA material to `docs/`.
- ⚠️ FastAPI version anomaly in primed evidence ("warned 0.127, dropped 0.126+") — verify ordering before citing.
- Both source documents retained unmodified in researcher workspace for provenance (M22).

---
*Merge executed by Kali 2026-08-22. Ratification pending. On promotion: regenerate llms-full.txt via `make sprint-plan-llm`; `make doc-llm-validate` must pass.*

*⬡ OMEGA ⬡ MIGRATION-PLAYBOOK-SPEC ⬡ v1.1.0-merged ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
