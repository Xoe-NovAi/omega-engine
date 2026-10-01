<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Migration Case Studies — Raw Evidence Dump
**AP Token**: `AP-RESEARCHER-MIGRATION-EVIDENCE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-22
**Purpose**: Raw evidence backing `MIGRATION_PLAYBOOK_SPEC_20260822.md`. Project-by-project findings with URLs and excerpts. Companion to prior art: Roc Racoon's `PILLAR_LEAK_AUDIT_20260822.md` / `PILLAR_REFACTOR_PLAN_20260822.md` and researcher gap docs.
**Search protocol**: SR-V1 fleet (parallel-search tier), session `a7f3c9e2-migration-playbook-2026`, queries included "2026"/"latest".

---

## 1. Pydantic v1 → v2 (closest analogue to our Pillar→Node rename)

**URLs**:
- https://docs.pydantic.dev/latest/migration
- https://pydantic.dev/docs/validation/latest/get-started/migration
- https://github.com/pydantic/bump-pydantic

**Findings**:
1. **Dual-name shim via namespace**: V2 ships `pydantic.v1` sub-namespace so old-API code keeps working inside the new package. This is the canonical "compatibility import path" pattern — users opt into the OLD api explicitly rather than the new one being broken.
2. **Codemod shipped as separate beta tool**: `pip install bump-pydantic` (libcst-based). Explicitly labeled *beta* — the project did NOT claim full automation. Guide says: run tool → "Review the changes and address any issues the tool couldn't fix automatically."
3. **Migration guide structure**: install section → tool usage → "Continue using V1 features" escape hatch → major breaking changes table (`dict()` → `model_dump()`, etc.) → behavior-change warnings (e.g., `Optional[T]` no longer implies default) → checklist → FAQ accordion of common errors.
4. **Escape hatch versioning**: `pip install "pydantic==1.*"` pinned old line remains installable. Two parallel majors coexist on PyPI.
5. **Known pain**: ValidationError *format* changed, breaking downstream parsers — a meta-breaking-change (code that consumed error output broke even if app code migrated). Lesson: **error/message formats are part of the contract**.
6. **Python 3.14 forced cliff**: V1 incompatible with newer Python — external pressure ended the shim life. Lesson: shims have natural death dates set by dependencies, not just policy.

## 2. Kubernetes API deprecations

**URLs**:
- https://kubernetes.io/docs/reference/using-api/deprecation-guide/ (versioned snapshots e.g. v1-33, v1-35)
- https://www.plural.sh/blog/deprecated-kubernetes-apis (2026-01-22)
- https://access.redhat.com/articles/6955985 (2026-06-09)

**Findings**:
1. **Written deprecation policy with math**: API versions live N releases (GA APIs: 12 months or 3 releases minimum per k8s API policy). Removal happens only at MAJOR-ish milestone releases, never mid-cycle.
2. **Per-release migration guide**: One canonical "Deprecated API Migration Guide" page organized BY RELEASE ("The v1.25 release stopped serving…"), each entry listing: replacement API + since-when, notable semantic diffs (e.g., empty `spec.selector` meaning flipped between policy/v1beta1 and policy/v1 — silent behavior change!), and migration commands.
3. **Test-with-removals-simulated**: `--runtime-config=<group>/<version>=false` lets users rehearse the removal BEFORE it lands. ← Directly applicable: we should be able to disable legacy pillar shims via config flag to rehearse removal.
4. **Detection tooling without telemetry**: client warnings emitted at request time, API server audit logs, and metrics — all LOCAL to the operator's cluster. Operators find their own deprecated usage; the project never phones home. This is exactly our M8-compatible model.
5. **Failure mode observed**: guide itself went stale (GitHub issue kubernetes/website#51011 — missing v1.33 Endpoints deprecation, labeled rotten). Lesson: **migration guides rot; assign an owner and a freshness gate**.
6. **`kubectl convert` was removed from core** — automated conversion tooling itself needs a maintenance story.

## 3. MCP Specification (most relevant — we ARE an MCP project)

**URLs**:
- https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning
- https://stacktr.ee/blog/mcp-2026-spec-changes (2026-07-28)
- https://mcpmigrate.dev/blog/mcp-spec-2026-07-28-migration-guide
- https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/

**Findings**:
1. **Date-stamped versions marking last breaking change**: `YYYY-MM-DD` = "last date backwards-incompatible changes were made." Backward-compatible changes do NOT bump the version.
2. **Formal feature lifecycle (SEP-2596)**: Active → Deprecated → Removed. Deprecated features remain ≥ **12 months**, or ≥ **90 days** under expedited removal (security only). Public deprecated-features registry with mandatory documented migration path.
3. **RC freeze + validation window**: RC locked 2026-05-21, final 2026-07-28 — a 10-week frozen-target window so SDK maintainers migrate against something that doesn't move.
4. **Negotiation instead of hard cutover**: every request carries `protocolVersion`; servers accept or negotiate down. Old-version servers keep working after new spec publication.
5. **Third-party ecosystem response**: within weeks, commercial migration guides appeared cataloging every SEP-level break with grep-able fixes ("Grep your server… for hardcoded -32002"). Lesson: when you publish precise change lists, the ecosystem writes your migration tooling FOR you.
6. **Silent-degrade warning**: "servers that don't speak it will degrade quietly and then stop working" — worst-case UX. Lesson: fail LOUD with actionable errors during migration windows.

## 4. Python 2 → 3

**URLs**:
- https://peps.python.org/pep-0702/ (context on deprecation mechanics)
- https://docs.python.org/3/library/warnings.html

**Findings** (well-documented history, corroborated by PEP text):
1. **Big-bang failure**: py2→py3 initially broke the ecosystem with no compat path; adoption stalled for a decade until `six`/`__future__` shims and `caniusepython3` tooling emerged. Canonical lesson: **never break without a dual-run path**.
2. **Premature removal reverted**: CPython had to revert removal of long-deprecated unittest features from 3.11 because users weren't ready (cited verbatim in PEP 702 motivation). Lesson: removal dates must be driven by evidence of migration completion, not calendar alone.
3. **Warning taxonomy is load-bearing**: `DeprecationWarning` (library devs) vs `FutureWarning` (end users) vs `PendingDeprecationWarning` (ignored by default). Default filters show DeprecationWarning only from `__main__` — i.e., surface warnings to the person who can act.
4. **Static+runtime dual signaling**: PEP 702 `@warnings.deprecated()` decorator warns BOTH at type-check time AND runtime. ~1,900 of top-5000 PyPI packages use runtime DeprecationWarnings; static checkers catch what grep cannot.

## 5. Django deprecation cycle

**URLs**:
- https://docs.djangoproject.com/en/stable/internals/release-process/ (feature removal timeline; corroborated across search results)
- https://stackoverflow.com/questions/79571257/ (migration-file hygiene context)

**Findings**:
1. **Fixed mechanical timeline**: feature deprecated in A.B → raises `RemovedInDjangoAB.CWarning` → removed in A.B+2 (roughly 12 months). The warning CLASS NAME encodes the removal version — the warning itself tells you the deadline.
2. **Deprecations never in LTS final releases**; removals land only at feature releases. Predictability > speed.
3. **Runtime warnings visible in test runs**: Django docs instruct enabling `-Wd:::DeprecationWarning` in test settings so YOUR suite surfaces upcoming breaks. Lesson: make CI the deprecation tripwire.

## 6. Home Assistant (monthly cadence, consumer-grade comms)

**URLs**:
- https://www.home-assistant.io/changelogs/core-2026.3 (full changelog format)
- https://developers.home-assistant.io/blog/ (deprecation announcements; established knowledge)

**Findings**:
1. **Dedicated "Breaking Changes" section published BEFORE the release** in each monthly changelog, written user-first ("we thought long and hard… here is why, here is what to do"), separate from the technical "All changes" list.
2. **Two-tier comms**: blog release notes (humans) + changelog (machines/power users) + developer deprecation policy (integrations get ~4 releases / deprecation period before removal).
3. **YAML/config keys deprecated with runtime warnings logged locally** in the HA UI/logs — again local-log-based tracking, zero telemetry.

## 7. Codemod tooling state of the art (2025–2026)

**URLs**:
- https://github.com/ast-grep/ast-grep (15.6k stars; explicit mission: "if you're an open-source library author, ast-grep can help your library users adopt breaking changes more easily")
- https://ast-grep.github.io/
- https://docs.openrewrite.org/popular-recipe-guides (2026-08-19; recipes moving to "Code Genome Project")
- https://www.baeldung.com/java-openrewrite (2025-07-17)
- https://www.moderne.ai/openrewrite ; https://tooldirectory.ai/tools/moderne (reviewed 2026-08-08)
- https://gist.github.com/htunnicliff/dc3a7a0cd9e55a71f622f7b2468eb45e

**Findings**:
1. **ast-grep**: Rust/tree-sitter CLI; YAML-rule codemods; pattern-isomorphic-to-code; pip-installable (`pip install ast-grep-cli`). Best fit for OUR Python repo when patterns are syntactic (e.g., `.pillar` → `.slots[0]`, `list_pillar_keepers()` → `list_node_keepers()`).
2. **LibCST**: lossless concrete-syntax tree; powers bump-pydantic; right choice when transforms need type/comment preservation and complex logic. Higher build cost than ast-grep YAML rules.
3. **OpenRewrite/Moderne**: Java-centric mass-refactoring; 10k+ recipes; now expanding to Python; enterprise platform (Moderne) proves codemods scale to thousands of repos — validating the investment for post-debut.
4. **Build-vs-not heuristic** (synthesized from pydantic/k8s/OpenRewrite evidence): build a codemod when (a) the change is syntactically detectable, (b) affected call sites number in dozens+, (c) the same class of change will recur (post-debut reality). Otherwise ship a table + grep recipes in the guide. AI agents (per Deska 2026-08-18 article) are increasingly used as ad-hoc codemod runners fed the migration guide as context — viable middle path for one-off renames.

## 8. Telemetry-free deprecation tracking

**URLs**:
- Kubernetes deprecation guide (audit logs + client warnings — see §2)
- https://docs.python.org/3/library/warnings.html (warning filters/counters)
- HA developer docs (local log deprecation warnings)
- Etsy Debriefing Facilitation Guide: https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf

**Synthesized mechanisms compatible with M8 (zero telemetry)**:
| Mechanism | How | Who reads it |
|---|---|---|
| Runtime warning counters | Deprecation shim increments a local counter/log line each hit | User (via `omega doctor` style command) |
| Local audit log | Shim hits appended to `data/logs/deprecations.log` with trace_id | User + issue templates |
| Opt-in report command | `omega report-deprecations` prints/redacts summary user pastes into GitHub issue template | Maintainers |
| Issue templates | "Migration problem" template asks which shim fired | Maintainers |
| CI tripwire | `-W error::DeprecationWarning` mode in tests | Repo owners |
| Grep recipes | Published patterns users run against own code | Users |

No successful OSS project surveyed uses covert telemetry for this. All use emission-at-point-of-use + local visibility + opt-in reporting.

## 9. Post-mortem & institutional knowledge formats

**URLs**:
- https://sre.google/sre-book/postmortem-culture/
- https://sre.google/workbook/postmortem-culture/
- https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf
- https://github.com/architecture-decision-record/architecture-decision-record
- https://catio.tech/blog/architecture-decision-record (2026-06-15)
- https://sreconcepts.com/blameless-postmortems.html

**Findings**:
1. **Google SRE blameless postmortem sections**: Impact, Timeline, Cause(s) (contributing factors, not "root cause" singular), What Went Well, What Went Poorly, Lucky Escapes, Action Items (each with owner + tracked bug; "a postmortem without subsequent action is indistinguishable from no postmortem").
2. **Blameless language discipline**: rewrite "John ran the migration untested" → "CI lacked a dry-run check; runbook command was ambiguous." Systemic causes only.
3. **Etsy/Jeli**: facilitation-guided learning reviews; Morgue tool (github.com/etsy/morgue) treats postmortems as queryable records.
4. **ADR discipline (Nygard)**: Title/Status/Context/Decision/Consequences; immutable once accepted; superseded-by links. MADR adds decision drivers + options pros/cons. Key anti-pattern: ADR sprawl (ADRs ≠ runbooks ≠ design docs).
5. **Mapping to Omega systems**: Nygard Context ≈ our L1 narrative; Consequences ≈ L2 insight; the distilled cross-migration invariant ≈ L3 universal principle. Our PIVOT_LOG already plays the ADL role — migration post-mortems should enter as numbered decisions with supersession links, NOT a parallel system.

---
*End of evidence dump. Citations verified 2026-08-22.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
