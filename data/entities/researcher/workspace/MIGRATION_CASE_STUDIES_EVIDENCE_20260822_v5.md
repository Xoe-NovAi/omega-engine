# Migration Case Studies Evidence Base (v5)
**AP Token**: `AP-MIGRATION-CASE-STUDIES-v5.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-22
**Purpose**: Primary-source evidence for the Rehearsal Migration playbook — how mature open-source projects run breaking-change migrations for live user bases, what they publish, and what went wrong.
**Method**: SR-V1 search protocol (`.firecrawl/` cache tier-0 miss verified → websearch/webfetch tiers). All sources fetched live 2026-08-22 unless noted.
**Split-test note**: Authored independently; v1–v4 artifacts NOT consulted (controlled experiment).
**Companion artifacts**: `MIGRATION_PLAYBOOK_SPEC_20260822_v5.md` · `REHEARSAL_LEARNING_PLAN_20260822_v5.md`

---

## Source Register

| # | Source | Type | Verified | Evidences |
|---|--------|------|----------|-----------|
| S1 | https://docs.djangoproject.com/en/dev/internals/deprecation/ | Official docs | 2026-08-22 | Django deprecation timeline mechanics; two-release removal rule |
| S2 | https://pydantic.dev/docs/validation/latest/get-started/migration | Official docs | 2026-08-22 | Pydantic v1→v2 guide; bump-pydantic codemod; pydantic.v1 shim namespace |
| S3 | https://pypi.org/project/bump-pydantic | Tool page | 2026-08-22 | BP001–BP009 codemod rules; --diff check mode |
| S4 | https://pyblog.in/programming/python/pydantic-v2-what-changed-and-why-your-apis-need-an-upgrade | Analysis | 2026-05-07 | FastAPI 0.126.0 drop of v1; silent-coercion failure class |
| S5 | https://kubernetes.io/docs/reference/using-api/deprecation-policy/ | Official policy | 2024-10-25 mtime | GA/Beta/Alpha removal rules; announce-in-sync rule |
| S6 | https://kubernetes.io/docs/reference/using-api/deprecation-guide/ | Official guide | 2025-05-16 mtime | "Removed APIs by release" per-version migration guide |
| S7 | https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596 | SEP PR (merged) | 2026-04-17 created | SEP-2596 lifecycle mechanics verbatim |
| S8 | https://aaif.io/blog/mcp-just-handed-you-a-deprecation-policy-steal-it | Analysis | 2026-07-27 | AAIF reading of SEP-2596; missing-lifecycle failure mode |
| S9 | https://v2.tauri.app/start/migrate/from-tauri-1 | Official guide | 2026-08-22 | Tauri v2 migration guide structure; `tauri migrate` CLI |
| S10 | https://developer.chrome.com/docs/extensions/develop/migrate | Official guide | 2024-02-14 | Chrome MV3 checklist; Extension Manifest Converter |
| S11 | https://www.pythonskillset.com/articles/python-2-vs-3-migration-decade-reshaped-language | Retrospective | 2026-06-24 | Python 2→3 arc; EOL deadline as forcing function |
| S12 | https://versions.dev/modernize/python/python-2-to-python-3 | Guide | 2026-05-22 | 2to3 insufficiency; unicode/bytes human-review class |
| S13 | https://community.home-assistant.io/t/focus-on-backward-compatibility/598956 | Community thread | 2023-08-03 | Multi-year upgrade breakage pain (user-side evidence) |
| S14 | https://www.home-assistant.io/changelogs/core-2026.3 | Changelog | 2026-08-22 | HA changelog taxonomy incl. breaking-change entries |
| S15 | https://sre.google/sre-book/postmortem-culture/ | Canonical SRE | stable | Blameless definition; triggers; template metadata fields |
| S16 | https://sre.google/sre-book/example-postmortem/ | Canonical SRE | stable | Example postmortem section structure |
| S17 | https://incident.io/blog/sre-incident-postmortem-best-practices | Practitioner | 2026-03-13 | 5-step process; blame-vs-blameless language table |
| S18 | http://code.hootsuite.com/blameless-post-mortems | Practitioner | 2018-02-07 | Etsy lineage: Allspaw blameless postmortems; Milstein 5-Whys-with-humans |
| S19 | https://libcst.readthedocs.io/en/latest/codemods_tutorial.html | Tool docs | current | LibCST codemod CLI; `.libcst.codemod.yaml` repo config |
| S20 | https://ast-grep.github.io/ | Tool docs | current | Structural search/rewrite; YAML scan rules |
| S21 | https://gist.github.com/eightHundreds/70c9ec82c2b7ba7140dc2cfaa311e8d1 | Practitioner blog mirror | current | Bevy 0.9→0.10 semi-automated migration workflow (compile→rewrite→verify loop) |
| S22 | https://docs.openrewrite.org/ | Tool docs | 2026-08-18 | OpenRewrite LST recipes; lossless semantic trees |
| S23 | https://doc.holiday/blog/how-to-write-a-migration-guide-that-developers-follow | Craft guide | 2026-06-20 | Error-string-as-header technique; Diátaxis mapping; 3-dev usability test |
| S24 | https://gitdoc.ai/blog/writing-migration-guides-that-dont-break-users | Craft guide | 2026-06-18 | Task-organized guides; effort estimates; v1-compat shim library pattern |
| S25 | https://deska.dev/blog/agent-breaking-change-migration-guide | Craft guide | 2026-08-18 | Comparison-table architecture; troubleshooting-section requirement |
| S26 | https://arxiv.org/pdf/2604.24072v2 | Academic | 2026-05-20 | Log4j case study: ~30% of Java API changes are backward-incompatible; 32% of devs avoid updates over compatibility fears |

---

## §1 Case Studies

### 1.1 Python 2 → 3 — The Decade-Long Hard Fork [S11, S12]

**What happened**: Python 3 (2008) deliberately broke compatibility to fix Unicode handling (bytes-vs-str split), integer division, and iterator semantics. The community did not migrate en masse for a decade.

**Timeline facts**:
- Python 3.0 released December 2008; Python 2.7 (final 2.x) released July 2010.
- The effective forcing function was the **EOL announcement**: January 1, 2020 end-of-life. As it approached, distributors (Ubuntu, Red Hat) stopped shipping Python 2 by default, thousands of PyPI packages dropped support, and migration tooling adoption spiked.
- Lesson recorded in retrospectives: **deprecation without a hard deadline does not move ecosystems**. Twelve years of gentle warnings produced less migration than the final 24 months of countdown pressure.

**Tooling published**: `2to3` (syntax rewriter, ships with CPython), `futurize`/`pastefrom` (python-future library), `six` (dual-compat shims library).

**What went wrong / lessons**:
1. **No dual-runtime strategy at launch** — early Python 3 could not run Python 2 code at all; libraries had to maintain parallel branches. The `six`/`__future__` ecosystem emerged bottom-up years later, which is backwards: the compat layer should have been official on day one.
2. **Codemods insufficient for semantic classes** — `2to3` handles mechanical syntax but the unicode/bytes split, integer-division assumptions, and C-extension compatibility require human review plus non-ASCII test fixtures [S12]. A bytes/str fix passing ASCII-only tests can still corrupt real input.
3. **Warning fatigue** — Python 2.7 emitted `DeprecationWarning`s for years with no consequence attached; users learned to ignore them (and `-W ignore` became common).

**Omega mapping**: Our Pillar→Node decoupling (D180) is small-scale but structurally similar — an engine-wide concept rename with WAD-layer data migration. We already ship auto-migration on load (`entity_registry.py:404-419`), which is the correct "six"-style compat layer. The Python lesson says: pair every rename with a removal date, not just a warning.

---

### 1.2 Django — Institutionalized Two-Release Deprecation [S1]

**Policy mechanics** (the most copyable model in open source):
- A feature is deprecated in release X.Y with a `RemovedInDjango<XY+2>DeprecationWarning`.
- It is **removed exactly two feature releases later** (e.g., deprecated in 5.0 → removed in 6.0). The removal list is pre-committed in a public document: `docs/internals/deprecation.md` — the "Deprecation Timeline."
- Each timeline entry cross-references the release notes of the version where the deprecation was announced ("See the Django 6.0 release notes for more details").
- **Transitional settings pattern**: during the window, Django ships both old and new mechanisms, with the old one emitting warnings (e.g., `CSRF_COOKIE_MASKED`, `DEFAULT_HASHING_ALGORITHM`, `USE_BLANK_CHOICE_DASH` — all listed in the timeline as "transitional settings will be removed").
- **Accelerated path for security**: security-related deprecations skip the normal cadence ("An accelerated timeline was used as this was a security related deprecation" — Markup contrib app, Python-Markdown <2.1).
- **Stub-retention for data compatibility**: removed model fields sometimes leave "a stub field will remain for compatibility with historical migrations" (NullBooleanField, JSONField) — i.e., removal respects persisted-data reality, not just code cleanliness.

**Runtime warning discipline**: `django.utils.deprecation` provides named warning classes per removal target, so users can filter/upgrade selectively (`-W error::DeprecationWarning::django`) and CI can promote warnings to failures.

**What went right**: the pre-committed public timeline means users can plan upgrades years ahead; nothing is ever removed "under them on a Tuesday."

**Omega mapping**: This is the direct template for our shim-lifetime policy — deprecate in version N, remove in N+2, publish the removal schedule in advance, name the warning class after the removal milestone.

---

### 1.3 Pydantic v1 → v2 — Codemod + Compat Namespace + Forced Cliff [S2, S3, S4]

**What happened**: Pydantic v2 rewrote the validation core in Rust (pydantic-core, 5–50× perf claims). Breaking changes were extensive: `Config` class → `model_config = ConfigDict(...)`, `@validator` → `@field_validator` (+ mandatory `@classmethod`), `.dict()`/`.json()` → `.model_dump()`/`.model_dump_json()`, `GenericModel` → standard generics, stricter type coercion.

**The three-part migration kit they published**:
1. **Official migration guide** (pydantic.dev/docs/.../migration) — change-by-change with before/after.
2. **`pydantic.v1` compat namespace** — v2 ships the entire v1 API importable as `from pydantic.v1 import ...`; conversely v1 ≥1.10.17 offers `pydantic.v1` imports so both major versions share one package identity. Documented caveat: module objects differ (`pydantic.v1.fields is not pydantic.fields`) even though symbols are identical — a subtle dual-name-shim hazard worth recording.
3. **`bump-pydantic` codemod** (LibCST-based, beta) — nine numbered rules (BP001 add default None to Optional fields; BP002 Config→model_config; BP003 Field param renames; BP004 import rewrites; BP005 GenericModel; BP006 __root__→RootModel; BP007 decorator replacements; BP008 con* functions→Annotated; BP009 TODO-marking for un-automatable custom types). Supports `--diff` mode to preview before applying.

**Ecosystem forcing**: FastAPI carried the cliff — FastAPI 0.126.0 (Dec 2025) dropped Pydantic v1 entirely (`pydantic >= 2.7.0` minimum), after emitting deprecation warnings for `pydantic.v1` imports in prior releases. Downstream frameworks converting warnings into deadlines is what actually completed the ecosystem migration.

**What went wrong / lessons**:
1. **Silent-behavior-change class** — the hardest breakage wasn't renamed methods but *stricter semantics*: string-to-int coercion that silently succeeded in v1 raises in v2; unknown-field handling flipped defaults. Guides must lead with behavior deltas, not just API renames [S4].
2. **Codemod coverage honesty** — BP009 explicitly marks what automation *cannot* fix with TODO comments rather than pretending success. Honest partial automation beats silently-incomplete transformation.
3. **Dual-namespace identity traps** — `isinstance` checks across the v1/v2 boundary fail because classes genuinely differ. Shims need documented identity semantics.

**Omega mapping**: Our pillar→slot auto-migration on load is the BP-style mechanical layer; the `metadata` opaque bag is the compat namespace. The lesson: enumerate what the automator will NOT do (our equivalent of BP009) inside the refactor plan itself.

---

### 1.4 Kubernetes — Policy-Grade API Deprecation [S5, S6]

**Rules (verbatim structure)**:
- **Rule #1**: API elements may only be removed by incrementing the API group version — never within a served version.
- **Rule #2**: API objects must round-trip between versions in a release without information loss.
- Removal windows by stability track:
  - **GA**: may be removed only by incrementing the group version (effectively never within a major).
  - **Beta**: deprecated no more than 9 months or 3 minor releases after introduction; no longer served 9 months or 3 minor releases after deprecation (whichever is longer).
  - **Alpha**: removable in any release without notice.
- **Announce-in-sync rule**: deprecations are documented AND announced (kubernetes-announce list) synchronized with the release that marks them deprecated.
- **Metrics escape hatch**: a deprecated metric can be "hidden" (still served, not advertised) for one release so admins get a final migrate-off window.
- **Storage-vs-serving split**: serving endpoints for persisted API versions may be disabled on schedule, but the API server must keep decoding previously persisted data (issue #52185 caveat) — removal of storage formats is a separate, harder gate than removal of endpoints.

**User-facing artifact**: the **Deprecated API Migration Guide**, maintained per release with a "Removed APIs by release" table (e.g., v1.32 stopped serving flow-control APIs), each entry listing old→new mappings and required actions.

**What went right**: exceptions exist but "will always be announced in all relevant release notes"; the policy is a living document with explicit SIG escalation for cases that don't fit.

**Omega mapping**: The storage-vs-serving distinction maps directly onto our config/data layers — we may stop *writing* legacy `pillars:` keys long before we stop *reading* them (auto-migration keeps reading forever for historical files). Also adopt the announce-in-sync rule: the Hivemind closeout post IS our kubernetes-announce.

---

### 1.5 MCP SEP-2596 — Specification Feature Lifecycle (Our Own Ecosystem's New Law) [S7, S8]

**Merged April 17, 2026** into the MCP spec. Mechanics:
- Every spec feature moves through a defined lifecycle: **Active → Deprecated → Removed**.
- **Minimum twelve-month window** between deprecation landing and earliest permitted removal.
- Deprecations REQUIRE a documented migration path — or an explicit statement that none is needed. "A deprecation is never just a tombstone with no guidance attached" [S8].
- Required machine-readable markers: `@deprecated` schema annotations + mandatory changelog entries.
- **Two-SEP procedure**: deprecation and removal are each their own standards-track proposal — removal cannot ride along inside the deprecation PR.
- **Replacement-gate**: any named migration-target replacement must ALREADY be Active when the deprecation lands (not merely planned at removal time) — prevents deprecating toward vaporware.
- **Expedited security route**: ≥90 days minimum, requires maintainer sign-off.
- **Relocation path**: low-usage features may move out of core to extensions (SEP-2133 binding) rather than die.
- Retroactive application: existing informal deprecations (HTTP+SSE transport; `includeContext` values) were reclassified under the new policy.

**AAIF practitioner reading** [S8]: the failure mode SEP-2596 targets is "missing lifecycle" — tools that accumulate with no owner, no version, no sunset date. Their prescription: turn inventory into a registry with a lifecycle state per entry. Quote-worthy: teams that treat the lifecycle as paperwork "come out with the same sediment they went in with."

**Omega mapping**: This is the newest and most directly applicable model — it's from OUR protocol ecosystem (we implement MCP; N4 bridge watches its revisions per D-587 amendment). Adopt wholesale: lifecycle states, 12-month floor for anything user-facing, migration-path-required rule, replacement-must-exist rule, two-step removal procedure (mirrors our Plan→Verify→Execute M4).

---

### 1.6 Tauri v1 → v2 — Ship the Codemod With the Release [S9]

**Guide architecture** (v2.tauri.app/start/migrate/from-tauri-1):
- Organized by subsystem: Configuration → Rust Crate Changes → JavaScript API Changes → Environment Variables → then deep-dive sections per migrated area ("Migrate to File System Plugin", "Migrate Permissions", etc.), each with copy-paste before/after for both languages.
- Every removed item links to its replacement ("Migration" anchor links inline in the removal list).
- Behavior-change callouts separated from renames ("Change of default behavior — failing to do so will prevent your users from getting further updates!").

**The killer feature**: `npm run tauri migrate` — a CLI codemod SHIPPED IN THE SAME RELEASE as the breaking changes, covering config restructuring and permission prefixing (changelog evidence: "The `tauri migrate` tool will automate the migration process, which involves prefixing all app, event, image, menu... permissions with `core:`").

**Lesson**: the best moment to ship automation is simultaneously with the break, not as a follow-up. Users' first contact with the migration should offer a command, not homework.

### 1.7 Chrome Manifest V2 → V3 — Checklist + Partial Converter [S10]

- Guide opens with a **checklist summary** and lets users enter via checklist or dive into sections.
- Ships **Extension Manifest Converter** with honest framing: "It does not do everything for you, but it will get you started" — README documents exactly what the tool changes (coverage honesty again).
- Advises **step-wise rollout**: publish to a limited audience first.
- Advises against adding new functionality mid-migration (permission-prompt side effects).

### 1.8 Home Assistant — Monthly Cadence Friction [S13, S14]

- Monthly release train with breaking changes flagged in release notes/changelog taxonomy.
- Community evidence of the multi-version-jump problem: users upgrading across 2+ years report "soooo many broken configs" because breaking changes are only documented per-release — there is no aggregate multi-release migration path [S13].
- **Lesson**: per-release notes are necessary but insufficient; someone must maintain cumulative "upgrading from far back" paths, or accept permanent support load from stragglers.

---

## §2 User-Facing Communication Craft

### 2.1 Deprecation Notice Conventions (synthesized across S1/S5/S7/S23)

| Convention | Exemplar | Omega adoption |
|---|---|---|
| Named warning class per removal milestone | Django `RemovedInDjango60DeprecationWarning` | ✅ Adopt: `RemovedInOmega<N>DeprecationWarning`-style naming in logs |
| Runtime warning with location info | Python `DeprecationWarning(stacklevel=2)` | ✅ Adopt: log warning includes caller file:line |
| Machine-readable annotation in schema/config | SEP-2596 `@deprecated` annotations | ✅ Adopt: `deprecated:` key in YAML configs with `since:` + `removal:` fields |
| Announce synchronized with release | Kubernetes announce-in-sync | ✅ Adopt: Hivemind post (intent=status) at deprecation commit |
| Public pre-committed removal timeline | Django internals/deprecation.md | ✅ Adopt: `DEPRECATION_TIMELINE.md` in coordination dir |
| Two-proposal separation (deprecate ≠ remove) | SEP-2596 two-SEP procedure | ✅ Adopt: separate PIVOT_LOG decisions D-deprecate vs D-remove |

### 2.2 Timeline Norms (measured)

- **Django**: 2 feature releases (~16 months at annual cadence).
- **Kubernetes Beta**: max(9 months, 3 minor releases) after deprecation; GA effectively never within a version.
- **SEP-2596**: 12-month floor; 90-day security-expedited floor.
- **Python**: counterexample — 12 years of warnings without enforcement moved nobody; the dated EOL moved everyone.

**Synthesis for Omega**: single-user-software reality means our "user base" is the Architect + future community. Adopt: **N+2 minor releases OR 60 days (whichever is LONGER) for internal surfaces; 12-month floor for anything touching the sovereign corpus or entity soul data** (data outlives code — Kubernetes storage-rule logic).

### 2.3 Writing Guides Users Actually Follow [S23, S24, S25]

Convergent craft rules:
1. **Organize by user task, not by author's change-list** — "Update your authentication flow (~15 min)" beats "Authentication module changes." Include effort estimates so users can schedule [S24].
2. **Error strings as navigation** — developers paste error text into search; put the exact new-version error message verbatim in headers/callouts with the fix underneath [S23]. Research confirms error messages are primary navigation during troubleshooting.
3. **Comparison tables first, prose second** — Legacy Pattern | New Pattern table gives instant parity scanning [S25].
4. **Before/after code blocks, always self-contained** — matches our own M26 self-contained-code mandate.
5. **Separate breaks-now from breaks-eventually** — immediate breakers at top with high visual weight; deprecation timelines secondary [S23].
6. **Troubleshooting section is mandatory** — common new-version errors and fixes [S25].
7. **Honest automation coverage** — state what the codemod does and does not do (Chrome converter framing; bump-pydantic BP009 TODOs).
8. **Validate with 3 outsiders** — paraphrase testing, plus-minus testing, task-based testing: watch three uninvolved developers attempt the migration without help [S23].
9. **Version-stamp and link-check** — guides rot fast; stale guides actively mislead [S23].

---

## §3 Codemod / Automated Migration Tooling (2025–2026 State)

### 3.1 Tool Landscape

| Tool | Language | Mechanism | Best For | Maturity Signal |
|---|---|---|---|---|
| **LibCST** [S19] | Python | Concrete Syntax Tree (formatting-preserving) | Repo-specific codemods that must not reformat code; ships `libcst.tool initialize` with `.libcst.codemod.yaml` repo config, blacklist patterns, formatter hooks (black) | Powers Instagram/Meta production migrations; bump-pydantic built on it |
| **ast-grep** [S20, S21] | Polyglot (tree-sitter) | Pattern `$A && $A()` → rewrite `$A?.()`; YAML rule files for scan/lint/fix | Quick semi-automated migrations across many files/languages; interactive fixing | Bevy 0.9→0.10 workflow documented; codemod.com adopting as backend |
| **OpenRewrite** [S22] | Java-first, expanding (Python parser exists) | Lossless Semantic Trees + recipe catalog; Gradle/Maven plugins | Framework migrations at scale (Spring Boot upgrades are flagship) | Netflix-origin; Moderne commercializes multi-repo scale |
| **2to3/futurize** [S12] | Python | AST rewrite | Mechanical syntax only | Proven insufficient alone for semantic changes |
| **Custom CLI** (Tauri `migrate`, Chrome converter) | Any | Hand-written project-specific tool | When migration touches config files + multiple languages + permissions systems | Shipped same-release with the break |

### 3.2 The Semi-Automated Loop (Bevy workflow, generalizable) [S21]

Four steps, repeatable until green:
1. Clean git branch for the migration.
2. Update dependencies; check lockfiles for transitive drift.
3. **Compile → Rewrite (ast-grep patterns from the migration guide) → Verify → Format. Repeat.**
4. Run tests; fix remaining by hand.

Mantra quoted: "use automation that maximizes your productivity. Write codemod that is straightforward to you and fix remaining issues by hand."

### 3.3 Build-vs-Manual Decision Matrix (synthesized)

Build a codemod when ALL hold:
- Change is mechanically detectable (renames, import moves, signature swaps) — the bump-pydantic BP001–BP008 class.
- Affected sites number in dozens+ or span many files.
- Formatting preservation matters (→ LibCST) or polyglot reach matters (→ ast-grep).
- The migration will recur (multiple repos/WADs, future community stacks).

Write a manual guide instead when ANY hold:
- Change is semantic/behavioral (Pydantic strictness class) — automation would transform syntax while leaving wrong behavior.
- Affected sites are few (<~20) — guide + grep is cheaper than tool maintenance.
- One-shot migration with no recurrence — tool pays for itself never.
- Data/config migration where correctness >> speed (entity souls, vault schemas) — human review mandatory regardless (Python unicode lesson).

**Honesty requirement either way**: publish explicit "what the tool does NOT cover" (BP009 TODO pattern; Chrome converter README).

---

## §4 Telemetry-Free Deprecation Tracking (M8 Constraint)

We cannot count shim hits via phone-home. Measured alternatives across the researched ecosystem:

1. **Local structured logs ARE allowed** (M8 exception: local observability in `data/`). Emit a structured log line on every shim/deprecated-path invocation: `{event: "deprecated_use", id: "pillar_field_read", site: "file:line", ts}`. Aggregate locally with sqlite/jq. This is our primary hit-rate signal and costs zero external telemetry. Precedent: Kubernetes' hidden-metric escape hatch serves the same purpose server-side [S5]; our equivalent is the local log.
2. **Opt-in reporting** — a `omega report-deprecations` CLI that packages the LOCAL deprecation log into a paste-able issue template. User pulls the trigger; nothing leaves the machine unprompted. (Pattern aligned with crash-reporter opt-in norms.)
3. **Issue templates asking the right question** — "Which version are you migrating FROM?" captures the multi-version-jump distribution Home Assistant lacks [S13].
4. **Contract tests as synthetic users** — tests that exercise ONLY the deprecated surface prove the shim works and, when the shim is deleted, fail loudly as the removal gate. Count of passing shim-tests = upper bound on supported legacy surface.
5. **Grep-able deprecation IDs** — every deprecation carries a stable ID (e.g., `DEP-PILLAR-001`) in warning text, changelog, timeline doc, and issue template. Enables users to self-report precisely and enables us to correlate without any network calls.
6. **Time-boxed census instead of continuous telemetry** — since our deployment population is knowable (Architect's machines + Hivemind awareness), periodic manual census (`grep -r "pillars:" config/ data/`) replaces usage analytics entirely. Kubernetes needs hidden metrics because it can't see its users; we CAN see ours.

---

## §5 Post-Mortem & Learning Capture Discipline

### 5.1 Canonical Formats

**Google SRE blameless postmortem** [S15, S16]:
- Definition: "focuses on identifying the contributing causes of the incident without indicting any individual or team... assumes that everyone involved had good intentions and did the right thing with the information they had."
- Trigger criteria (objective): SLO-breach, data-loss, release-delay caused by defect, monitoring-blind-spot detection + stakeholder request.
- Sections: Summary → Impact → Timeline (UTC timestamps) → Contributing factors (root causes + trigger) → What went well → Action items (owner + tracker bug each).
- Culture mechanics: postmortem review is a SEPARATE meeting from incident review (days later, analytical, not adrenaline); templates carry metadata fields for trend aggregation; "Postmortems at Google" working group cross-pollinates; surveys measure process effectiveness.

**Blame-language conversion table** [S17] (directly reusable as our writing rule):

| Blame-oriented | Blameless |
|---|---|
| "Engineer X deployed a buggy change" | "The CI/CD pipeline did not catch the bug before production" |
| "The on-call was slow to respond" | "Alert noise caused fatigue, delaying triage" |
| "The team missed a warning sign" | "Warning signs were not documented in runbooks" |

**Five-Whys discipline** [S18, Medium synthesis]: chains that terminate at a person are incomplete — redirect: "why was it POSSIBLE to misconfigure without automated validation catching it?" The absent guardrail is the root cause, not the human.

**Etsy/Jeli lineage** [S18]: John Allspaw's blameless postmortems & just culture; Dan Milstein's "5 Whys With Humans, Not Robots" — ask why the human's action made sense given what they knew. Learning reviews must produce fixable system changes, not "be careful" items.

**What-went-well is load-bearing** [Medium synthesis]: documenting which detection/response mechanism worked prevents accidentally deleting it in the next refactor. Most teams skip it and lose institutional knowledge about their protections.

### 5.2 Turning One-Off Migrations Into Institutional Knowledge

Mechanism ladder (increasing permanence):
1. **Runbook** — repeatable steps for the NEXT migration (task-organized, effort-estimated, per §2.3).
2. **ADR / Decision log** — immutable record of WHY (our PIVOT_LOG D-series; Kubernetes' "policy is a living document" + announced exceptions).
3. **Template extraction** — Google's working group extracts shared template/metadata from individual postmortems; ours: extract the migration-guide skeleton from each real migration into `docs/standards/`.
4. **Soul Distillation L1→L2→L3** — narrative → insight → principle (SO-10a format). Maps cleanly: L1 = postmortem timeline/summary; L2 = contributing-factor analysis; L3 = timeless principle (e.g., N11 Insight 2 style: "a decision is only as ratified as its least-updated config surface").
5. **Corpus Map row** — every artifact registered so the next session finds it (D-366 discipline).

### 5.3 Failure Modes Observed (avoid these)

- Publishing without doing: action items dying in backlog [Rootly/incident.io critiques] — our mitigation: action items land in ACTIVE_SPRINT.json immediately, not in prose.
- Conflating timeline with analysis in one paragraph [Medium synthesis] — keep verifiable timeline separate from labeled interpretation.
- Vanity completeness: complex templates get abandoned [S17] — keep our postmortem template minimal (Google's example is the reference for completeness, not a form to fill field-for-field).
- Per-release documentation without cumulative paths [S13 Home Assistant] — maintain the aggregate migration index, not just per-release notes.

---

## §6 Local Discovery Findings (repo fit)

| Checked | Result | Implication |
|---|---|---|
| `scripts/validate_llm_docs.py` | EXISTS | Playbook spec must carry full YAML frontmatter to pass if promoted to docs/ |
| `scripts/check_doc_tokens.py` + `make doc-token-check` | EXISTS | Spec must respect token budgets (Architecture Deep-Dive: 8K target/16K hard) |
| `docs/sprints/current/{llms.txt,llms-full.txt}` | EXIST, generated | Sprint-plan-llm pattern confirmed live; playbook can reuse generation pattern |
| `make doc-llm-validate` | Wired into `make temple-grade` (Makefile:232) | Doc standards are CI-enforced, not aspirational |
| `.firecrawl/` cache | No migration-relevant content (podman/claude/hf topics only) | SR-V1 tier-0 miss legitimate; web tiers justified |
| DOC_STYLE_GUIDE categories | Workspace files = Category 7 (working docs, header-exempt); promoted docs = Category 1/6 (headers + LLM-format required) | Spec written promotion-ready |

---

## §7 Synthesis: The Ten Transferable Laws

1. **Deadline > warning** (Python): a deprecation without a removal date is noise.
2. **Pre-commit the timeline publicly** (Django): removal schedules are promises, not intentions.
3. **Never deprecate toward vaporware** (SEP-2596): the replacement must exist and be Active first.
4. **Deprecation requires a migration path or an explicit "none needed"** (SEP-2596): tombstones are forbidden.
5. **Ship the codemod with the break** (Tauri): first contact should offer a command, not homework.
6. **Automate the mechanical, guide the semantic, review the data** (Pydantic/Python): three change classes, three responses.
7. **Publish what automation does NOT cover** (BP009/Chrome): honest partial automation beats silent incompleteness.
8. **Data outlives endpoints** (Kubernetes storage rule): stop writing legacy formats long before stopping reading them.
9. **Aggregate paths for stragglers** (Home Assistant inverse): per-release notes strand multi-version jumpers.
10. **Blameless is analytic, not polite** (Google/Etsy): five-whys terminating at a person is an unfinished investigation.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_migration_evidence ⬡ SR-V1 complete ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
