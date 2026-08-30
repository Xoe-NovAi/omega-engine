---
schema_version: "1.0"
document_type: "reference"
document_id: "migration-case-studies-evidence-v4"
title: "Migration Case Studies Evidence — Breaking Changes in Mature Projects (v4)"
status: "ACTIVE"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "breaking-changes", "deprecation", "case-studies", "split-test-v4"]
priority: "P1"
depends_on: ["D180 pillar decoupling"]
blocks: ["MIGRATION_PLAYBOOK_SPEC_20260822_v4.md"]
acceptance_gates:
  - "Every claim carries a source URL with last_verified date"
cross_references:
  - "MIGRATION_PLAYBOOK_SPEC_20260822_v4.md"
  - "REHEARSAL_LEARNING_PLAN_20260822_v4.md"
llm_metadata:
  token_budget: 6000
  chunk_strategy: "section_per_case"
  answer_first_sections: true
  self_contained_code: true
---

# Migration Case Studies Evidence (v4)

**AP Token**: `AP-MIGRATION-CASE-STUDIES-v4-20260822`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-22 · `last_verified: 2026-08-22` · All sources fetched live this session (SR-V1).

## What (Answer-First)

Raw evidence base for the Rehearsal Migration playbook: how mature projects (Python, Pydantic/FastAPI, Kubernetes, Home Assistant, Bevy/Rust, MCP) ran live breaking-change migrations, what they published, what tooling they shipped, what failed. Each case ends with an **Omega Transfer** mapping the lesson onto our engine.

---

## C1 — Python 2→3: The Decade-Long Cautionary Tale

| Aspect | Finding | Source |
|---|---|---|
| Duration & damage | ~a decade (2008–2020 EOL); broke libraries, split the community; tipping point came only when flagship libraries (numpy, Django) dropped Py2 | pythonskillset.com/articles/python-2-vs-3-migration-decade-reshaped-language (2026-06-24) |
| Core failure mode | Both versions runnable for years with no forcing function; ecosystem waited for everyone else instead of migrating | same source |
| 2026 retrospective | AI tooling now makes the *mechanical half* of such migrations tractable — the organizational problem (coordination, forcing functions) remains human | fullscale.io/blog/python-2-to-3-migration |
| Warning machinery legacy | Produced modern taxonomy: `DeprecationWarning` (dev-facing, ignored by default outside `__main__` per PEP 565), `FutureWarning` (end-user-facing); `warnings.deprecated()` decorator (3.13+) emits runtime warnings + static-checker diagnostics | docs.python.org/3/library/warnings.html, docs.python.org/3/library/exceptions.html |

**Omega Transfer**: Never ship a deprecation without a removal date AND a forcing function. Our equivalent of "flagship library drops support" = a Node charter amendment that flips a gate. Use `DeprecationWarning`-style dual audiences: engine-log warnings for operators, doc banners for users.

## C2 — Pydantic v1→v2 + FastAPI: The Modern Reference Migration

| Aspect | Finding | Source |
|---|---|---|
| Published artifacts | Official migration guide (pydantic.dev/docs/validation/latest/get-started/migration) + `bump-pydantic` codemod (PyPI, beta) + `pydantic.v1` shim namespace so old code keeps importing during transition | pydantic.dev/docs/validation/latest/get-started/migration |
| Issue triage during migration | Dedicated `bug V2` GitHub label to actively monitor migration-caused errors | same source |
| Shim lifecycle end | FastAPI 0.126.0 (Dec 20 2025) dropped Pydantic v1 entirely (`pydantic >= 2.7.0` minimum); 0.127.0 raises deprecation warning on `pydantic.v1` imports before full drop — warning-then-drop sequencing | pyblog.in/programming/python/pydantic-v2-what-changed-and-why-your-apis-need-an-upgrade (2026-05-07) |
| Codemod limits | bump-pydantic handles mechanical renames (`.dict()`→`.model_dump()`, `@validator`→`@field_validator`) but NOT semantic changes (strict-mode coercion differences, generic models) — those stay manual-guide territory | deepwiki.com/pydantic/pydantic/8.1-v1-to-v2-migration + pyblog.in |
| v3 lesson learned | Team explicitly signaled v3 will NOT be a large API rewrite like v2 — institutional learning from v2's disruption | pyblog.in FAQ |

**Omega Transfer**: The warning→shim→drop sequence maps exactly onto our pillar refactor (engine auto-migrates `pillars:`→`slots:` on load = shim; MCP tool rename needs a deprecation alias period). A dedicated issue label per migration = cheap tracking without telemetry.

## C3 — Kubernetes: The Formal Policy Gold Standard

| Aspect | Finding | Source |
|---|---|---|
| Tiered timelines | GA APIs: may be deprecated, NEVER removed within a major version. Beta: supported ≥9 months or 3 minor releases after deprecation (whichever longer). Alpha: removable any release without notice | kubernetes.io/docs/reference/using-api/deprecation-policy (2024-10-25) |
| Stability monotonicity | Rule #3: an API may not be deprecated in favor of a LESS stable version; replacement must be Active before deprecation lands | same source |
| Per-release migration guides | Every release with removals ships a dedicated "Deprecated API Migration Guide" listing each removed API → replacement + field-level diffs | kubernetes.io/docs/reference/using-api/deprecation-guide/; GKE mirrors it (docs.cloud.google.com/kubernetes-engine/docs/deprecations/apis-1-25) |
| Runtime warnings | Deprecated API usage produces warnings at least one year before removal; announcements synced to release notes + announce list | kubernetes.io/blog/2022/08/04/upcoming-changes-in-kubernetes-1-25 |
| Usage detection (telemetry-based — WE CANNOT COPY) | GKE generates "deprecation insights" from user agents calling deprecated APIs — requires telemetry we forbid under M8 | docs.cloud.google.com/kubernetes-engine/docs/deprecations/apis-1-25 |

**Omega Transfer**: Adopt the tiered-window concept (our WAD-layer concepts = alpha-like, engine API surface = GA-like). Per-release migration guide = our sprint-plan structure. The GKE insights feature is exactly what M8 forbids — our substitute is in §T of the playbook spec.

## C4 — Home Assistant: High-Cadence Breaking Changes + Repairs UX

| Aspect | Finding | Source |
|---|---|---|
| Cadence | Monthly minor releases, each with a "Breaking Changes" release-notes section; deprecation window often several months (log warning + UI "Repairs" notification) before removal | bigiron.cc/guides/home-assistant-update-strategy-surviving-monthly-breaking-changes (2026-07-28) |
| Documented failure mode | The multi-month gap is the problem: a March warning ignored because "it still works" becomes a silently-dead automation in September; nobody remembers the warning | same source |
| User-side mitigation culture | Community ritual: read breaking-changes filtered to your integrations, snapshot before update, treat every Repairs notification as a same-week to-do | same source |
| Anti-pattern observed | Users attempting AI-driven YAML migration get burned ("Do not use AI to migrate. AI will screw up the yaml") — codemods must be deterministic, not generative, for config files | community.home-assistant.io/t/deprecation-template/959403 |

**Omega Transfer**: Silent breakage is the worst outcome class — our M23 Failure Integrity aligns: never let a deprecated path fail silently; make it loud at use-time. Deterministic codemods only for YAML/config; LLM assist allowed for prose, never for config rewrites.

## C5 — Bevy/Rust + ast-grep: Semi-Automated Migration Workflow

| Aspect | Finding | Source |
|---|---|---|
| Workflow | 4 steps: clean git branch → update deps (+check lockfiles) → compile/rewrite/verify/format LOOP → fix remaining tests manually | ast-grep.github.io/blog/migrate-bevy.html |
| Tool role split | Compiler errors locate breaking changes; ast-grep `-p pattern -r rewrite` performs mechanical fixes; human fixes the remainder. "Write codemod that is straightforward to you and fix remaining issues by hand" | same source |
| Ecosystem praise pattern | Yew cited as gold standard: "automation in every release note" — migration snippets shipped WITH the changelog | same source |
| Codemod.com integration | codemod.com considering ast-grep as underlying engine for its code-transformation studio — trend toward pattern-based (not full-AST-programming) codemods | gist.github.com/eightHundreds/70c9ec82c2b7ba7140dc2cfaa311e8d1 |

**Omega Transfer**: Our pillar refactor already follows this shape (Roc's audit = compiler errors; refactor plan = rewrite recipes). Adopt "automation in every release note": each migration ships its own grep/codemod commands inline.

## C6 — MCP SEP-2596: Deprecation Policy For a Protocol We Depend On

| Aspect | Finding | Source |
|---|---|---|
| Three-state lifecycle | Active → Deprecated → Removed per FEATURE (separate from spec-revision lifecycle Draft/Current/Final); adopted via SEP-2596, Final 2026-04-17 | modelcontextprotocol.io/seps/2596-spec-feature-lifecycle-and-deprecation |
| Minimum window | ≥12 months between deprecation and earliest removal, measured from the revision RELEASE that first marks it Deprecated (not from SEP date) — all features deprecated in one revision share one earliest-removal date | same source |
| Deprecation SEP requirements | Must identify feature, state rationale, document migration path (replacement MUST be Active — not draft), specify window; schema gains `@deprecated` JSDoc referencing SEP + revision; changelog gains "Deprecated" heading; `deprecated.mdx` page created | same source |
| SDK obligations | Tier-1 SDKs MUST emit deprecation warnings; removal from spec does NOT oblige SDKs to drop feature (SDK revision-support policy governs) | same source |
| Telemetry gap acknowledged verbatim | Policy permits deprecation on "negligible adoption" grounds BUT "the project has no shared telemetry today. Until one exists, this criterion relies on SDK maintainer attestation." | same source, Open Questions |
| Expedited removal | Security risk shortens the floor — predictable retirement mechanism for unsafe features | same source |

**Omega Transfer**: SEP-2596 is our closest structural cousin (protocol + live implementers + no telemetry). Copy: release-anchored windows, replacement-must-exist rule, changelog taxonomy, maintainer-attestation instead of telemetry. Our N4 bridge amendment (MCP spec-revision watch) makes tracking this SEP family an standing duty.

---

## T — Cross-Cutting Themes (Tooling & Communication)

### Codemod tooling state of the art (2025–2026)

| Tool | Model | Best for | Source |
|---|---|---|---|
| **libcst** | Python CST preserving formatting/comments | Python codemods where diffs must be minimal reviewable | libcst.readthedocs.io; pypi.org/project/libcst (parses Py 3.0→3.14) |
| **ast-grep** | Pattern-based structural search/rewrite (YAML rules, Rust CLI) | Quick per-release migration commands; multi-language | ast-grep.github.io |
| **OpenRewrite** | Lossless Semantic Trees + composed recipes | Full framework migrations (Spring Boot 1→2 etc.); recipe ecosystems distributed via registries | docs.openrewrite.org (2026-08-18); origin story: Netflix anti-gating culture — offer help, don't coerce (computerweekly.com CW Developer Network) |
| **bump-pydantic** | Single-purpose codemod | Mechanical renames only; semantic changes manual | github.com/pydantic/bump-pydantic |

**When to build vs. write**: build a codemod when (a) change is syntactically localizable, (b) >~10 call sites, (c) transformation has ≤2 parameters; write a guide when semantics change or context matters. Fowler's Parallel Change / expand-contract remains the canonical structural pattern for interface migrations (martinfowler.com/bliki/ParallelChange.html).

### Migration-guide craft (what users actually follow)

1. Organize by USER WORKFLOW, not by internal change list (gitdoc.ai/blog/writing-migration-guides-that-dont-break-users, 2026-06-18)
2. Quick-start path first for the 80% case with zero prerequisites; branch edge cases by SYMPTOM/error-message, not concept (doc.holiday/blog/how-to-write-a-migration-guide-that-developers-follow, 2026-06-20)
3. Error strings verbatim in headers — developers navigate by pasted error messages (same source, citing sciencedirect.com S0164121219302286)
4. Comparison table old→new + verification checklist at end (deska.dev/blog/agent-breaking-change-migration-guide, 2026-08-18)
5. Separate "breaks TODAY" from "breaks eventually" with visual weight on the former
6. Ship automation AT THE TOP of the guide; RFC 8594 `Deprecation`/`Sunset` headers for HTTP APIs (datatracker.ietf.org/doc/html/rfc8594)

### Blameless post-mortem formats

Google SRE canon: blameless = focus on contributing causes without indicting individuals; sections = Summary, Impact (quantified), Timeline (UTC timestamps), Contributing factors (2–5 systemic, blameless framing), What went well, Action items split mitigative vs preventative with owners+dates (sre.google/sre-book/postmortem-culture; sre.google/sre-book/example-postmortem; incident.io/blog/sre-incident-postmortem-best-practices, 2026-03-13). Jeli/PagerDuty add structured timeline curation from comms data (support.pagerduty.com/main/docs/post-incident-reviews-and-postmortems). Key failure mode: post-mortems die when action items are untracked; complex templates get abandoned — keep reference-complete but copy-minimal.

### Telemetry-free deprecation tracking precedents

- MCP SEP-2596: maintainer attestation replaces adoption telemetry (explicit Open Question in the SEP itself)
- Pydantic: dedicated issue label (`bug V2`) turns user bug reports into a usage signal
- Home Assistant: Repairs notifications surface deprecation hits IN the user's own UI — detection moves to the consumer side, locally
- Kubernetes GKE insights: the counter-example (requires server-side telemetry; forbidden under M8)
- Python warnings module: runtime emission is itself the tracking primitive — users who hit the path see it; opt-in aggregation happens via issues/dev-mode runs (`python -W error::DeprecationWarning` in CI converts silent usage into test failures)

*End of evidence file. Companion artifacts: MIGRATION_PLAYBOOK_SPEC_20260822_v4.md (process design), REHEARSAL_LEARNING_PLAN_20260822_v4.md (learning capture).*
