<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Migration Case Studies & Web Evidence — Rehearsal Migration v6
**AP Token**: `AP-MIGRATION-EVIDENCE-v6.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_evidence ⬡ ACTIVE

**Date**: 2026-08-22
**Session**: `ses_fd48c0515ffeVFWbDNV3zy6T1z` (primed Researcher, split-test v6)
**Purpose**: Raw web-research evidence base for the Post-Debut Breaking-Change Playbook. Every claim cites its source; all sources fetched live on 2026-08-22 via SR-V1 protocol.
**Companion**: `MIGRATION_PLAYBOOK_SPEC_20260822_v6.md` (the spec this evidence grounds)

---

## §1 Python 2 → 3 — The Canonical Cautionary Tale

### What they published
- `2to3` fixer tool, `six` compatibility library, `python-future`/`futurize`, `from __future__ import` statements.
- **Key failure**: early Python 3 *removed* the `u''` literal and `bytes %` formatting, forbidding dual-compatible code. Restored only in 3.3 (`u''`) and 3.5 (`bytes %`).
- Source: Gregory Szorc, "Mercurial's Journey to and Reflections on Python 3" (gregoryszorc.com, 2020-01-13).

### What went wrong
1. **"Flag day" transitions were non-viable** for large projects; the viable path (dual-compatible source) was initially impossible. Szorc: *"attempting a rewrite instead of performing incremental evolution"* is the folly mirrored by Py3k.
2. **7-year ecosystem stall**: Python 3.5 (Sep 2015) was the first viable porting target for many projects — 7 years after 3.0 (Dec 2008). Szorc calls 2008–2015 "the lost years."
3. **LWN consensus** (lwn.net/Articles/843660/, Jan 2021): all-or-nothing implementation forced simultaneous conversion of ALL transitive dependencies. Guido publicly conceded the transition was a mistake (PyCascades 2018).
4. **Silent behavioral changes were the real risk**, not mechanical ones. Kodare.net production migration (2018): `'ß'.upper()` → `'SS'` in py3 caused a production crash on cutover day; `'{}'.format(b'asd')` renders differently; `int('1_0')` parses in py3 but not py2. Mechanical changes were trivially automated; dangerous ones "still run without error and produce subtly wrong results."
5. **Coordination problem, not technical problem**: Victor Stinner (FOSDEM 2018): *"The biggest challenge is to explain to your manager that you will spend between 1 day and 1 month on working on a change that doesn't add any feature."*
6. **Lesson institutionalized**: Stinner: Python 4 will follow the same deprecation policy as any 3.x release — no major backward-incompatible changes without a slow transition period helped by documentation and tooling.

### Successful practitioner patterns
- **Kodare.net (240K LOC)**: py2 → py2/py3 → py3 strangler path; CI whitelist so fixed apps can't regress; commit machine-generated vs human edits separately (*"commit this stage even if it's badly broken"*); crash-log-driven rollout — enable py3, collect crashes via Sentry, fix all, repeat; ability to switch one batch machine at a time AND switch back.
- **CrowdStrike (~200K LOC)**: catalog first, prune dead products first ("easiest conversion is deprecation"); Tox multi-version test matrix; invest heavily in TEST refactoring over code beauty (40–50 tests → 3,000 via parametrize); A/B drift validation at the end.

---

## §2 Django — The Gold-Standard Formal Policy

Source: docs.djangoproject.com/en/6.0/internals/release-process/ + /internals/deprecation/ + /misc/api-stability/ (fetched 2026-08-22).

### Policy mechanics
- Feature releases every ~8 months. SemVer-ish ("not pure SemVer").
- **Shim lifetime = minimum 2 feature releases (~16 months)**: feature deprecated in A.x keeps working through all A.x emitting `RemovedInDjangoB0Warning`; removed in B.0 (or B.1 if deprecated in the last A.x release).
- LTS special rule: deprecations started in an LTS (X.2) drop in Y.1, NOT Y.0 — third-party apps must span LTS-to-LTS upgrades. Y.2 LTS drops NO shims.
- Public **Deprecation Timeline document** lists every pending removal version by version.
- API stability commitment: breakage WITHOUT deprecation only for security or unavoidable bugfixes.

### Why this matters for us
Django proves you can ship breaking changes continuously IF (a) the warning names the removal version, (b) shims outlive two release cycles, (c) one canonical timeline page answers "what dies when."

---

## §3 Pydantic v1 → v2 — Codemod + Shim + Silent-Breaking Taxonomy

Sources: github.com/pydantic/bump-pydantic (archived 2026-05-27); pydantic.dev migration guide; brtkwr.com pydantic-v2-migration-tips (2025-11-17); tomodahinata.com complete guide (2026-06-26); akasa.com/blog/llms-upgraded-pydantic-shim-library.

### What they published
- Official migration guide with full before/after tables (`.dict()`→`.model_dump()`, `Config`→`model_config`, `@validator`→`@field_validator`+`@classmethod`, `orm_mode`→`from_attributes`).
- **`pydantic.v1` namespace shim**: entire V1 API vendored inside the V2 package — staged per-module migration within one process.
- **`bump-pydantic` codemod** (LibCST-based): rules BP001–BP010, `--diff` dry-run mode, per-rule disable flags. Now archived (mission complete).

### Coverage honesty (critical finding)
- bump-pydantic handles *"about 80% of the changes automatically… occasionally makes mistakes with complex validators"* (brtkwr).
- Tomoda Hinata (2026): the essential hard part is NOT mechanical renames but **"silently breaking changes that work but behave quietly differently"**: `Optional[int]` no longer implies `= None`; float→int coercion tightened; Union left-to-right → smart mode; constraints don't descend into generic args (`list[str] = Field(pattern=...)` silently stops applying per-element); `TypeError` no longer wrapped as `ValidationError`.
- **Verification-first doctrine**: characterization tests against v1 BEFORE migrating; run v1/v2 side-by-side and diff outputs; try `strict=True` to surface coercion reliance; both mypy plugins during transition.

### Akasa shim-library war story (structural coordination)
- ~20 services shared a domain-models library; couldn't upgrade any service without upgrading ALL. Three prior attempts died as stale PRs.
- Solution: `pydantic_12_shims` exporting the V2 API surface implemented atop whichever pydantic is installed (inspired by `six`). Key property: *"code using the shims could be merged to main and coexist with code that hadn't been updated yet."*
- Env-var kill-switch `TURN_PYDANTIC_V1_OFF` let already-migrated services flip runtime behavior without new edits.
- Verification: AI-generated 1600-line compatibility suite asserting shim ≡ native V2, run in a 3-config Actions matrix.
- **Anti-pattern discovered**: using `pydantic.v1` for unexposed models created a SECOND migration later; FastAPI dropped `pydantic.v1.BaseModel` support entirely; mixing v1/v2 models in one graph is unsupported.

---

## §4 Kubernetes API Deprecations — Warning Infrastructure at Scale

Sources: kubernetes.io/docs/reference/using-api/deprecation-policy/; /docs/reference/using-api/deprecation-guide/; KEP-1693 (github.com/kubernetes/enhancements); kubernetes.io/blog/2020/09/03/warnings/; KEP-1635 prevent-permabeta.

### Policy rules (distilled)
- Rule 1: API elements removed ONLY by incrementing the API group version — never within a served version.
- Rule 4a lifetimes: GA never removed within a major version; Beta supported ≤9 months/3 releases after introduction AND after deprecation; Alpha removable anytime.
- Rule 5a CLI: GA elements function ≥12 months or 2 releases post-deprecation; Rule 6: deprecated CLI MUST warn; Rule 7: deprecated behaviors function ≥1 year.
- Rule 10: feature-gate deprecations documented in BOTH release notes and CLI help, stating whether the gate is non-operational.
- KEP-1635 anti-permabeta: beta APIs auto-expire — GA-or-new-beta within 9 months or the API is force-deprecated; kube-apiserver stops serving expired betas mechanically.

### The v1.19 warning system (KEP-1693) — the model for M8-compliant tracking
When a request hits a deprecated API:
1. **`Warning` response header** (RFC 7234 §5.5, code 299): `<group>/<version> <kind> is deprecated in v1.X+, unavailable in v1.Y+; use <replacement>` — includes removal version AND replacement. Server-originated, works for all clients including ones applying manifests they didn't write.
2. **Gauge metric** `apiserver_requested_deprecated_apis{group,version,resource,subresource,removed_release}` = 1 — lets ADMINISTRATORS query their own usage locally via Prometheus.
3. **Audit annotation** `"k8s.io/deprecated":"true"` — identifies specific clients/objects needing updates.
4. `kubectl --warnings-as-errors` — CI gate treating any warning as failure.
5. CRDs can set custom `deprecationWarning` strings pointing at migration guides.
6. Per-release **Deprecated API Migration Guide** page listing exactly what stopped serving in each version, with per-resource instructions.

### Key insight for zero-telemetry
Kubernetes does NOT phone home. The usage-measurement loop is **local to each operator**: emit the signal (header/metric/log), give operators self-service queries, and let THEM report back voluntarily. The project learns about real-world usage through issue reports backed by operator-local evidence.

---

## §5 MCP SEP-2596 — Specification-Level Lifecycle (Our Direct Analogue)

Sources: modelcontextprotocol.io/seps/2596-spec-feature-lifecycle-and-deprecation; /community/feature-lifecycle; /specification/draft/deprecated; blog.modelcontextprotocol.io 2026-07-28 posts; SEP-2577.

### The mechanics
- Three feature states: **Active / Deprecated / Removed**. Deprecated = still works, scheduled for removal, migration path documented, new implementations SHOULD NOT adopt.
- **Minimum 12-month deprecation window**, measured from the revision RELEASE date (not SEP-final date) — every feature deprecated in the same revision shares one earliest-removal date.
- Expedited removal only for active security risk (published advisory or in-the-wild exploitation, no mitigation), floor 90 days, Core Maintainer approval required.
- Replacement must be Active before deprecation lands: *"A feature is not deprecated while its documented replacement is still only in draft."*
- Restoration possible via superseding SEP; re-deprecation restarts the clock.
- Documentation obligations at deprecation: `@deprecated` schema annotation referencing the SEP + revision; entry in the canonical **deprecated registry page** ("the canonical answer to 'what is on its way out, and by when'"); changelog entry; SDK-native deprecation markers (`@Deprecated`, `[Obsolete]`, etc.) in next SDK release.
- Removal itself needs no SEP — maintainer decision during release prep, AFTER confirming the migration target is still Active.
- Live registry (fetched 2026-08-22): Roots/Sampling/Logging/Dynamic Client Registration deprecated 2026-07-28, earliest removal 2027-07-28; HTTP+SSE transport legacy-deprecated with year-long offramp.

### The 2026-07-28 stateless rewrite (breaking change handled honestly)
- Largest revision ever; handshake REMOVED (SEP-2575). Maintainers' framing: *"This release contains breaking changes. We don't intend for that to be the norm."* Clean break justified only because future evolution now has deprecation windows + extensions framework + conformance-suite gating (SEP-2484: no Standards Track SEP reaches Final without a conformance scenario).
- Ten-week validation window between RC and final; Tier-1 SDKs expected to ship support within it.
- Dual-era interop matrix specified exhaustively (modern/legacy/dual-era × client/server) with deterministic probing (`server/discover` probe → fall back to `initialize`).

---

## §6 Home Assistant — Consumer-Grade Breaking-Change Craft

Sources: home-assistant.io/faq/do-updates-break-things/; github.com/home-assistant/architecture discussion #920 + ADR/0010 + issue #195; developers.home-assistant.io blog (device-split deprecation post).

### Safety-by-default stack
- Monthly releases; **automatic backup taken before each update** (rollback guaranteed); public beta period precedes stable; breaking changes documented in advance in release notes; built-in **repairs system proactively flags issues post-update and walks users through resolution**; users choose when to update.

### Formalized deprecation policy (architecture discussion #920)
- Prior informal standard: 2 release cycles (~2 months) for YAML config options — consequence: skipping 2 cycles = missed migration path = breakage.
- Proposal adopted direction: extend to **6 months (6 release cycles)** so users upgrading twice a year never hit breaks.
- Requirements: deprecated YAML config MUST raise an issue in the user's **repairs dashboard** explaining why and what to do; if automated migration exists it becomes REQUIRED, and failed imports raise repair issues too.
- Release notes carry a "Backward-incompatible changes" section per release; a "Farewell to the following" section documents integration removals WITH reasons (broken since X, library unmaintained since Y).
- Device-split example (dev blog): best-effort compatibility shims with honest limits — *"an AI-assisted analysis of 462 custom integrations… suggests at least 90% are expected to work unaffected, which also means some will not"* — shims removed after a full year (2026.x → 2027.8), explicitly stated.

### Lesson
HA treats breaking-change communication as a PRODUCT FEATURE: repairs dashboard = local, telemetry-free issue surfacing; automatic backup = rollback guarantee; reasons-not-just-changes in release notes.

---

## §7 Codemod / Automated Migration Tooling — State of the Art 2025–2026

Sources: libcst.readthedocs.io (codemods tutorial + API); ast-grep.github.io/catalog/python/; codemod.com/blog/imperative-vs-declarative-codemods (2025-05-15); bump-pydantic repo.

### Tool landscape
| Tool | Model | Sweet spot | Key capability |
|------|-------|-----------|----------------|
| **LibCST** | Imperative Python, concrete syntax tree | Format-preserving bulk refactors in Python codebases | `CodemodTest.assertCodemod()` unit testing; `AddImportsVisitor`; parallel execution; `--unified-diff` dry-run mode; repo config via `.libcst.codemod.yaml` |
| **ast-grep** | Declarative YAML rules + imperative NAPI scripts | Pattern-shaped renames/rewrites; fast compiled matching | `pattern:`/`fix:` pairs; `rewriters` for recursive inner-node transforms (e.g., `Optional[Union[...]]` full unwrapping); test fixtures per rule |
| **bump-pydantic** | Purpose-built codemod (LibCST) | One specific library migration | Rule IDs (BP001…), per-rule disable, diff mode — the reference pattern for a migration-specific tool |
| **OpenRewrite** | Imperative recipes (JVM ecosystem) | Java/Spring mass upgrades | Python equivalents don't exist at same maturity; LibCST is the Python analogue |

### When to build vs. manual guide (evidence-based)
- **Build a codemod when**: changes are syntactically pattern-matchable (renames, import moves, decorator swaps); the affected surface is large (>~50 call sites); the transformation is deterministic. ast-grep's OpenAI SDK migration example shows multi-rule YAML files handling real API migrations.
- **Do NOT build when**: correctness requires semantic judgment. Evidence: bump-pydantic CANNOT automate `Optional[T]` → add `= None` because *"it can't judge the meaning"* (Tomoda). The 20% it leaves is exactly the silently-breaking semantic residue.
- **Declarative-first doctrine** (codemod.com): YAML rules for simple pattern matches (fast to author, fast to run); imperative scripts only for context-dependent/multi-step edits.
- **Codemods need their own tests**: LibCST's `assertCodemod(before, after)` pattern; ast-grep rule fixtures. An untested codemod is a bug generator with good marketing.
- **Dry-run/diff mode is mandatory**: both LibCST (`--unified-diff`) and bump-pydantic (`--diff`) ship it; kodare.net's lesson: commit machine output separately from human fixes so blame stays clean.

---

## §8 Telemetry-Free Deprecation Tracking

### The Kubernetes answer (operator-local signals)
See §4. The complete zero-phone-home loop: emit Warning headers + local gauge metrics + audit annotations → operators query THEIR OWN data → voluntary issue reports carry evidence back to maintainers. No central telemetry required.

### The Home Assistant answer (local repairs dashboard)
Deprecated config raises an entry in the user's own Repairs UI with remediation steps. Users seeing the issue file bug reports naturally. Zero external data flow.

### Opt-in contract patterns (if we ever relax M8 — recorded for completeness, NOT recommended)
- `bougie` TELEMETRY.md (github.com/cresset-tools/bougie): consent-versioned schema, allow-list-only fields, `telemetry log` prints exact bytes that would be sent, `DO_NOT_TRACK=1` universal opt-out, CI defaults off.
- Archon issue #980 design: opt-IN default, whitelist properties, `telemetry inspect` shows literal JSON, dev builds have empty keys so telemetry can never fire from dev clones.
- cli-telemetry-spec: "disclose before you send" on stderr first-run; never blocks/fails/retries; aggregate-on-receipt collector.

### Omega-relevant synthesis
For an M8 engine, the viable measurement channels are:
1. **Runtime warnings captured locally** (Python `DeprecationWarning` → structured local log under `data/`).
2. **A self-diagnostic command** (à la `bougie diagnose --last` / HA repairs): users run it, paste output into an issue template.
3. **Issue templates** that ask the diagnostic questions directly ("run `omega doctor --deprecations` and paste").
4. **Local metrics** mirroring K8s gauge semantics in our observability DB (M8-legal: local observability stored in `data/` is explicitly permitted by Mandate 8).

---

## §9 Blameless Post-Mortem & Learning Capture

Sources: sre.google/sre-book/postmortem-culture/ + /workbook/postmortem-culture/ + /example-postmortem/; cloud.google.com/blog CRE fearless-shared-postmortems; etsy.com/codeascraft/debriefing-facilitation-guide + DebriefingFacilitationGuide.pdf; PagerDuty Jeli docs.

### Google SRE template (8 sections)
1. Summary (one paragraph, executive-readable)
2. Impact (numbers: who/how many/how long)
3. Timeline (UTC timestamps + T+N relative notation)
4. Root cause (5-whys to systemic cause)
5. What went well
6. What went poorly
7. **Where we got lucky** (the most valuable section — surfaces unmitigated risks; e.g., "right person was on-call implies tribal knowledge needing a playbook")
8. Action items table: ONE named owner each ("owned by the team means owned by no one"), due date, priority, status actually updated.

Review criteria before publication: key incident data collected? impact complete? root cause deep enough? action plan appropriate? shared with stakeholders?

External-postmortem rules (CRE): keep "Root causes and Trigger", "What went wrong", "Where we got lucky"; strip names (roles not people), sensitive detail, unlabeled graph axes.

### Etsy Debriefing Facilitation Guide (the learning-first correction)
- Post-mortems are *"first and foremost a learning opportunity, not a fixing one."* The urge to find THE root cause is seductive but premature.
- Ask **"how" not "why"**: "why" elicits defensive explanations; "how" elicits descriptions and context.
- Walk the annotated timeline FIRST; collect remediation ideas during but discuss only AFTER the timeline is agreed — early fixes are often mooted by fuller context.
- Talk to the people who would usually be blamed — their cues, mental models, and rationales are the richest data.
- Morgue = Etsy's postmortem metadata tool (timeline, graphs, chat logs, "request a facilitator" button).

### Jeli (PagerDuty) additions
- **Takeaways/themes** tab: what surprised you? what should others know more about? what does this share with other incidents?
- Aggregating multiple reviews reveals organizational patterns invisible one-at-a-time.

### Mapping onto Omega systems
| SRE concept | Omega equivalent |
|-------------|------------------|
| Postmortem document | PIVOT_LOG decision entry + session report |
| Action items w/ owner+date | ACTIVE_SPRINT.json tickets (6 canonical statuses, M27) |
| Lessons learned | Soul Distillation L1(narrative)→L2(insight)→L3(principle), SO-10a format |
| Trend analysis across postmortems | Corpus Map rows + proposed_lessons.yaml aggregation |
| Runbook updates | Node Domain Indexes + KB updates |

---

## §10 Cross-Cutting Synthesis — The Convergent Pattern

Every mature project independently converged on:

1. **Expand→Contract lifecycle**: add new way → warn on old way with removal date → remove old way. (Django shims, K8s version tracks, MCP Active/Deprecated/Removed, Pydantic namespace shim.)
2. **Warnings that name the removal version AND the replacement** — at the moment of use, not just in release notes. (Django `RemovedInDjango51Warning`, K8s Warning header, Python DeprecationWarning.)
3. **A single canonical registry page** answering "what is deprecated and by when." (Django Deprecation Timeline, K8s Migration Guide, MCP deprecated.mdx.)
4. **Shim lifetime ≥ 2 release cycles or ~12 months**, whichever binds. (Django 2 features, K8s GA ≥12mo, MCP 12mo floor, HA 6 months consumer-grade.)
5. **Mechanical vs semantic split**: automate the mechanical 80%, hand-crush the silent-behavioral 20% with characterization tests. (Pydantic/bump-pydantic, Python 2to3 vs bytes/str.)
6. **Local-first usage signals + voluntary reporting** — nobody needs phone-home telemetry. (K8s operator-local metrics, HA repairs dashboard.)
7. **Learning capture as institutional memory**: blameless format, single-owner action items, aggregated themes. (Google/Etsy/Jeli.)

## Source Register

| # | Source | Type | Fetched | Priority |
|---|--------|------|---------|----------|
| SR1 | gregoryszorc.com Mercurial/Python 3 retrospective | Blog (primary practitioner) | 2026-08-22 | P0 |
| SR2 | lwn.net/Articles/843660/ Python 2→3 discussion | Forum thread | 2026-08-22 | P1 |
| SR3 | mail.python.org python-dev retrospective thread (2018) | Mailing list | 2026-08-22 | P2 |
| SR4 | archive.fosdem.org Victor Stinner interview | Interview | 2026-08-22 | P1 |
| SR5 | kodare.net py2→py3 production migration | Blog (primary practitioner) | 2026-08-22 | P0 |
| SR6 | crowdstrike.com Python 2→3 case study | Case study | 2026-08-22 | P1 |
| SR7 | docs.djangoproject.com release-process + deprecation + api-stability | Official docs | 2026-08-22 | P0 |
| SR8 | github.com/pydantic/bump-pydantic + PyPI | Repo/docs | 2026-08-22 | P0 |
| SR9 | pydantic.dev migration guide | Official docs | 2026-08-22 | P0 |
| SR10 | brtkwr.com + tomodahinata.com Pydantic v2 guides | Practitioner blogs | 2026-08-22 | P1 |
| SR11 | akasa.com pydantic shim-library post | Engineering blog | 2026-08-22 | P0 |
| SR12 | kubernetes.io deprecation-policy + deprecation-guide | Official docs | 2026-08-22 | P0 |
| SR13 | KEP-1693 warnings + KEP-1635 prevent-permabeta | Design docs | 2026-08-22 | P0 |
| SR14 | kubernetes.io/blog/2020/09/03/warnings/ | Project blog | 2026-08-22 | P0 |
| SR15 | modelcontextprotocol.io SEP-2596 + feature-lifecycle + deprecated registry | Spec/process | 2026-08-22 | P0 |
| SR16 | blog.modelcontextprotocol.io 2026-07-28 RC + final posts | Project blog | 2026-08-22 | P0 |
| SR17 | home-assistant.io FAQ + architecture #920 + dev blog | Docs/discussions | 2026-08-22 | P0 |
| SR18 | libcst.readthedocs.io codemods docs | Official docs | 2026-08-22 | P0 |
| SR19 | ast-grep.github.io Python catalog | Official docs | 2026-08-22 | P1 |
| SR20 | codemod.com imperative-vs-declarative blog | Vendor blog | 2026-08-22 | P2 |
| SR21 | sre.google postmortem-culture + example + CRE lessons | Canonical practice | 2026-08-22 | P0 |
| SR22 | etsy.com debriefing facilitation guide + PDF | Practice guide | 2026-08-22 | P0 |
| SR23 | support.pagerduty.com Jeli post-incident reviews | Product docs | 2026-08-22 | P1 |
| SR24 | cresset-tools/bougie TELEMETRY.md + javimosch/cli-telemetry-spec + Archon #980 | Telemetry contracts | 2026-08-22 | P2 |

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_evidence ⬡ COMPLETE ⬡ 2026-08-22*
