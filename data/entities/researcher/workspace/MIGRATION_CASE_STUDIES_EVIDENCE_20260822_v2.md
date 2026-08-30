<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Migration Case Studies — Evidence Base
**AP Token**: `AP-MIGRATION-CASES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_cases ⬡ EVIDENCE

**Date**: 2026-08-22 (searches run this date; "2026"/"latest" queries per SR-V1)
**Purpose**: Cited real-world evidence behind MIGRATION_PLAYBOOK_SPEC_20260822_v2.md — what mature projects published, what worked, what failed.
**Tags**: case-studies, python, django, pydantic, kubernetes, mcp, codemods, postmortem

---

## Answer First

Five patterns recur across every successful live-base migration: **(1) warn-before-remove with a dual-name shim period; (2) the migration guide is written before the breaking code, not after; (3) removal timing is policy-bound (version-count or months), not mood-bound; (4) deprecation signals are made visible in the user's OWN environment (runtime warnings, response headers, local metrics) rather than harvested via telemetry; (5) the migration ends with captured institutional knowledge (postmortem/KEP/timeline doc), which is why the SECOND migration by the same project is always smoother.** Failures cluster where a project skipped #1 (Python 2→3's decade of pain was mostly ecosystem deadlock, not missing tooling) or skipped #2 (Pydantic v2's beta codemod shipped after community panic).

## §1 Python 2 → 3 — the cautionary tale

- **What they published**: official porting guide, `2to3` codemod, six/dual-support libraries, extended support windows (Python 2.7 EOL stretched to 2020 — a full decade of dual life).
- **What went wrong**: no runtime compatibility layer inside 3.x itself for years (`pydantic.v1`-style namespace came to Python only via third-party `six`); the ecosystem waited on the *fewest-motivated* dependency in each chain; C-extension users had the hardest path and the least guidance.
- **Lesson for us**: ship the shim INSIDE our own package (namespace alias / re-export), never rely on the community to bridge. Our WAD consumers are few but their chains include engine internals — internal shims kill external pain.
- Sources: python.org porting docs (canonical); decade-long 2.7 maintenance record.

## §2 Django — policy as a living document

- **Mechanism**: a permanent, versioned **Deprecation Timeline** page (docs.djangoproject.com/en/5.2/internals/deprecation) listing exactly which API dies in which future release, cross-linked to the release notes "two versions prior" where deprecation was announced.
- **Policy**: feature deprecated in X → removed in X+2 (roughly); **accelerated timeline explicitly allowed for security** (documented in the timeline itself).
- **Lesson**: publish ONE canonical removal schedule, not scattered changelog mentions. Our equivalent: a single `docs/migrations/SCHEDULE.md` maintained by N4.

## §3 Pydantic v1 → v2 (+ FastAPI downstream) — modern library-scale

- **Published artifacts**: comprehensive migration guide (method-rename table: `.dict()`→`.model_dump()` etc.); **`bump-pydantic` codemod** (libcst-based, PyPI-installable, honest "still in beta"); **`pydantic.v1` shim namespace** so v1 code runs unmodified under the v2 package (from v1.10.17); old method names retained emitting `DeprecationWarning`; dedicated `"bug V2"` issue label to funnel/triage migration breakage reports.
- **Downstream pattern (FastAPI)**: supported both, then warned (`pydantic.v1` import warning in 0.127), then dropped v1 entirely at 0.126+ minimum `pydantic>=2.7` — the classic warn-then-drop ladder.
- **What went wrong**: codemod arrived effectively post-peak-pain and stayed "beta"; silent coercion-rule changes broke code that tests didn't cover (string→int strictness).
- **Lessons**: (a) shim namespaces work — adopt for any renamed module; (b) label-based issue triage gives telemetry-free breakage signal; (c) codemods must ship WITH the deprecation, not after; (d) document semantic/coercion changes even more loudly than renames — they fail silently.
- Sources: pydantic.dev/docs/migration (v2.8 & v2.11 & latest); pyblog.in v2 guide (2026-05); FastAPI release notes via same.

## §4 Kubernetes — the gold standard for operator-visible deprecation

- **Policy doc**: kubernetes.io/docs/reference/using-api/deprecation-policy — stability-tiered clocks: GA APIs "may be deprecated but not removed within a major version"; Beta served ≥9 months/3 releases after deprecation; Alpha removable anytime; CLI elements GA ≥12 months/2 releases.
- **User-visible signals (all LOCAL to the operator — zero exfiltration)**: RFC-7234 `Warning` header on deprecated API calls; `"k8s.io/deprecated":"true"` audit annotation; `apiserver_requested_deprecated_apis` Prometheus gauge joined with request counts and a **`removed_release` label** telling you the exact release that will break you; hidden-metrics escape hatch flag (`--show-hidden-metrics-for-version=`).
- **Per-release communication**: "Removals, Deprecations, and Major Changes" blog per release + migration options in docs at removal time.
- **Lesson**: this is our M8-compliant ideal — make the deprecation observable where the user already lives (their logs/metrics/warnings), give an escape hatch, and stamp every signal with the removal version.

## §5 MCP spec (our direct dependency) — living through it now

- The 2026-07-28 stateless rewrite was a breaking spec revision handled by versioned spec documents + transport negotiation; our own N4 charter amendment (MCP spec-revision watch, quarterly cadence) exists precisely because upstream breaks are recurring. Lesson: when your DEPENDENCY breaks itself, your playbook needs a "reactive migration" mode — same artifacts (guide/shim/gate) driven by upstream changelogs instead of our roadmap.

## §6 Codemod tooling landscape (2026)

| Tool | Nature | Fit for us |
|---|---|---|
| **libcst** | Format-preserving Python CST; powers bump-pydantic | Custom Python codemods where formatting must survive |
| **ast-grep** | Rust CLI, polyglot structural search/rewrite, YAML-aware | **Primary choice** — covers our .py AND config/WAD YAML layers; used for CI leak-census |
| OpenRewrite | 5000+ recipes, JVM-centric | Skip (wrong ecosystem weight) |
| GritQL / Comby | Pattern languages | Alternative syntax for ast-grep-class jobs |
| LLM-assisted hybrid | AST-match deterministic + LLM rewrite matched block | For semantic rewrites only; Google data: ~50% of time goes to validation — budget it |

Key research datum (Google, 39 migrations/12mo): 74% of edits AI-generated, 87% committed unmodified, timelines cut ~50% — BUT validation dominated human time. Non-negotiable rule adopted into spec §5: **every migrated file passes its existing test suite before human review.**

## §7 Postmortem formats (feeding REHEARSAL_LEARNING_PLAN)

- **Google SRE book ch.15** (Postmortem Culture) + canonical example: sections = Summary · Impact · Timeline · Root cause(s) · What went well / What went wrong / Where we got lucky · Action items with owner+due+priority.
- **Etsy Debriefing Facilitation Guide** (codeascraft): facilitation-grounded blameless practice; "naming blame without shame."
- **Jeli**: operational-learning framing — focus on how work normally flows, not just the failure.
- **Blameless rewrite rule**: replace "X did Y" with "The system made Y the easiest path."
- **Flywheel** (incident.io/Loon SRE pattern): Write ≤48h → Share one channel → Track action-item aging weekly → Meta-review monthly for repeat factors → Fund top systemic fixes quarterly.

## Source Register

| # | Source | Used for |
|---|--------|----------|
| SR-C1 | docs.djangoproject.com/en/5.2/internals/deprecation | Django timeline/policy |
| SR-C2 | pydantic.dev/docs/validation/{2.8,2.11}/get-started/migration + docs.pydantic.dev/latest/migration | Pydantic artifacts |
| SR-C3 | github.com/pydantic/bump-pydantic | Codemod |
| SR-C4 | pyblog.in Pydantic v2 guide (2026-05-07) | FastAPI drop ladder, gotchas |
| SR-C5 | kubernetes.io/docs/reference/using-api/deprecation-policy | K8s tiered clocks + local signals |
| SR-C6 | kubernetes.io/blog/2022/11/18/upcoming-changes-in-kubernetes-1-26 | Per-release removal comms |
| SR-C7 | pkgpulse.com SemVer breaking-changes guide (2026-03-29) | Timeline norms, LTS, guide-first |
| SR-C8 | tianpan.co AI-codebase-migration (2026-05-06) | Codemod SOTA + Google study |
| SR-C9 | pypi.org/project/libcst · ast-grep GitHub topic pages | Tooling |
| SR-C10 | sre.google/sre-book/postmortem-culture + example-postmortem | SRE format |
| SR-C11 | Etsy Debriefing Facilitation Guide (extfiles.etsy.com / codeascraft) | Blameless facilitation |
| SR-C12 | slashield.io + theartofcto.com postmortem templates (2026) | 5-section structure, flywheel |
| SR-C13 | mlflow.org/docs/latest/community/usage-tracking | Telemetry contrast model |

*Honesty note*: Home Assistant / Zed / Tauri were queried but did not surface primary-policy pages above threshold in this pass; they are NOT cited as evidence here rather than padded in. Can deep-dive on request.

*⬡ OMEGA ⬡ MIGRATION-CASE-STUDIES ⬡ v1.0.0 ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
