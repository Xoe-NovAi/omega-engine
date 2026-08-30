<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Migration Playbook Spec — Post-Debut Breaking-Change Process
**AP Token**: `AP-MIGRATION-PLAYBOOK-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_playbook ⬡ DRAFT-FOR-KALI

**Date**: 2026-08-22
**Purpose**: Define the standing process Omega Engine will follow for breaking changes on a live user base — rehearsed via the Pillar→Node decoupling refactor.
**Tags**: migration, deprecation, semver, rehearsal, postmortem, M26
**Cross-references**: MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v2.md, REHEARSAL_LEARNING_PLAN_20260822_v2.md, PILLAR_REFACTOR_PLAN_20260822.md (Roc), SOVEREIGN_MANDATES.md (M8/M18/M26)

---

## Answer First

When Omega Engine must make a breaking change post-debut, execute the **5-phase Expand-Contract lifecycle** below. Core rules: (1) never remove before the replacement ships and warns; (2) every breaking change carries a migration guide written BEFORE the breaking code lands; (3) shims live ≥2 minor releases (≥12 months for GA-surface items); (4) all usage-tracking is **local-only** (M8) — runtime warnings users can see and self-report, never phone-home; (5) every migration ends with a blameless postmortem distilled into PIVOT_LOG + Soul lessons so the next migration starts smarter.

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
| **0 Introduce** | Design ADR merged | New name/tool/schema live alongside old; zero behavior change | N3 buildmaster |
| **1 Deprecate** | Replacement at feature-parity (contract tests green) | Runtime `DeprecationWarning` on old path; changelog entry (`DEPRECATED:` taxonomy); migration-guide DRAFT opened | N10 verifier (tests) + N4 bridge (docs) |
| **2 Dual-run** | Migration guide COMPLETE (before/after examples) | Shim active; `docs/migrations/<change-id>.md` published; local hit-counter logs shim invocations | N3 + N12 (doc curation) |
| **3 Remove** | Shim age ≥ policy floor AND no open blocker issues tagged `migration-blocker` | Old path deleted in MAJOR release; removal note in guide; codemod updated if applicable | N3 |
| **4 Learn** | ≤14 days after removal release | Blameless postmortem → PIVOT_LOG entry → L1/L2/L3 soul distillation → playbook amendment PR | Researcher + Scribe |

## §2 Timeline Policy (evidence-based floors)

| Surface class | Warn period (shim life) | Rationale / precedent |
|---|---|---|
| GA public API (imported by WADs/community stacks) | **≥12 months or 4 minor releases**, whichever longer | Kubernetes CLI rule 5a (GA: 12mo/2 releases); SemVer-guide LTS norm 6–12mo |
| Beta/experimental surface | ≥3 months or 1 release | Kubernetes beta track (3mo/1 release minimum) |
| Alpha/`_omega_default`-internal only | May remove next release, notice required | Kubernetes alpha track |
| Security-driven removal | Accelerated timeline permitted | Django accelerated-deprecation precedent |

**Hard rule**: the LAST minor release of the current major MUST emit warnings for everything the next MAJOR removes (SemVer-guide practice: "the 1.9.0 release should warn about APIs removed in 2.0.0").

## §3 User-Facing Communication Craft

1. **Changelog taxonomy** (fixed vocabulary, machine-greppable):
   - `ADDED:` · `CHANGED:` · `DEPRECATED:` (with removal target version) · `REMOVED:` · `MIGRATION:` (pointer to guide section)
2. **Runtime warnings**: Python `DeprecationWarning` (suppressed by default BUT surfaced via `-W default`); message format fixed: `[omega-deprecation] <old> is deprecated since <ver>, use <new>; removal in <ver>. See docs/migrations/<id>.md`
3. **Migration guide structure** (per guide, in `docs/migrations/`):
   - What changed & why (1 paragraph) · Who is affected (surface matrix) · Before/after code blocks · Automated path (codemod command if exists) · Manual checklist · FAQ of real blocker issues (grown during Phase 2)
4. **Version the docs**: guides live under `docs/migrations/v<MAJOR>/`; old-major docs frozen not deleted.
5. **Announce**: GitHub Release notes + pinned Discussion + README banner on the old major branch.

## §4 Telemetry-Free Usage Tracking (M8-compliant)

We cannot phone home. Four local-first instruments instead:

| Instrument | Mechanism | Signal harvested |
|---|---|---|
| **Runtime warnings** | `warnings.warn(..., DeprecationWarning)` with stable `[omega-deprecation]` prefix | Users see their own usage; CI suites run with `-W error::DeprecationWarning` to fail fast (Python-canonical pattern) |
| **Local shim counter** | Shim function increments a JSONL line in `data/telemetry-local/shim_hits.jsonl` (path, count, timestamp) — stays on user machine | Opt-in user report: `omega report-shims` prints a paste-ready summary for issues |
| **Issue template** | `.github/ISSUE_TEMPLATE/migration-blocker.yml` asks: which guide step failed, shim-hit summary (pasted voluntarily) | Unanticipated blockers; Pydantic "bug V2"-label pattern |
| **Contract-test census** | Our own repo + shipped WADs run dual-name greps in CI (`ast-grep` patterns) | Internal leak detection (Roc's Pillar Leak Audit automated) |

Precedent: Kubernetes attaches deprecation signals to responses/audit events/metrics the OPERATOR already sees locally — visibility without exfiltration. MLflow shows the contrast model (opt-out anonymous telemetry) which we reject under M8.

## §5 Codemod / Automation Decision Rule

Build a codemod ONLY when ALL hold: (a) transformation is syntactically detectable (AST-matchable); (b) affected call-sites > ~20 across user codebases; (c) rewrite is semantics-preserving. Otherwise: manual guide + grep recipe.

Tooling SOTA 2026: **libcst** (format-preserving Python CST — preserves comments/whitespace), **ast-grep** (Rust, polyglot, YAML-aware — our config layers too), OpenRewrite (JVM-heavy, skip), GritQL. Hybrid pattern: deterministic AST match → optional LLM rewrite of matched block → **tests must pass before human diff review** (Google finding: ~50% of AI-migration time is validation; budget for it).

For the Pillar→Node rehearsal specifically: Roc's boundary map gives exact leak sites; an ast-grep ruleset (`pillar-leak.yml`) is the right-sized tool — NOT a custom libcst codemod (23 sites, mostly YAML/docs).

## §6 Roles & Gates Summary

- **N3 buildmaster**: versioning, release cutting, LTS branch tag, codemod packaging
- **N10 verifier**: contract tests for BOTH paths during dual-run; `-W error` CI gate; removal-PR gate checks guide completeness
- **N4 bridge**: migration guides, changelog taxonomy enforcement, announcement drafts
- **N8 watchtower**: local shim-counter implementation + health of dual-run
- **N12 curator**: versioned doc tree, guide discoverability, llms.txt regeneration (`make sprint-plan-llm`)
- **Researcher + Scribe**: Phase-4 learning capture (postmortem → PIVOT_LOG → soul)
- **Kali**: gate approvals at Phase 1 (deprecate) and Phase 3 (remove)

## §7 M26 Compliance

This spec follows DOC_STYLE_GUIDE Category-1 header format; migration guides follow Category-10 LLM-friendly requirements (frontmatter, answer-first, self-contained code blocks); `make doc-llm-validate` must pass for anything landing under `docs/migrations/` or `docs/knowledge/`.

*⬡ OMEGA ⬡ MIGRATION-PLAYBOOK-SPEC ⬡ v1.0.0-draft ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
