---
schema_version: "1.0"
document_type: "reference"
document_id: "migration-case-studies-evidence-2026-08-22-v3"
title: "Migration Case Studies — Evidence Compendium"
status: "DRAFT"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "case-studies", "evidence", "pydantic", "kubernetes", "django", "python2to3", "home-assistant", "mcp", "zed"]
priority: "P0"
depends_on: ["MIGRATION_PLAYBOOK_SPEC_20260822_v3.md"]
blocks: []
acceptance_gates:
  - "All 8 case studies have structured metadata"
  - "Each study maps to playbook sections"
  - "Key findings extracted as actionable patterns"
  - "Sources cited with URLs and dates"
  - "Passes `make doc-llm-validate`"
cross_references:
  - "MIGRATION_PLAYBOOK_SPEC_20260822_v3.md"
  - "REHEARSAL_LEARNING_PLAN_20260822_v3.md"
  - "SOVEREIGN_MANDATES.md"
llm_metadata:
  token_budget: 10000
  chunk_strategy: "section_per_case_study"
  answer_first_sections: true
  self_contained_code: false
  modular_pages: true
---

# 🔱 Migration Case Studies — Evidence Compendium
**AP Token**: `AP-MIGRATION-CASE-STUDIES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_case_studies ⬡ DRAFT

**Date**: 2026-08-22
**Purpose**: Structured evidence from 8 real-world breaking-change migrations, mapped to Omega Migration Playbook sections. Each study includes: project context, deprecation strategy, tooling, communication, tracking, outcomes, and lessons for Omega.

---

## What

A **curated, cited compendium** of how mature open-source projects executed breaking-change migrations. Not anecdotes — each entry has source URLs, dates, and specific mechanisms used.

## Why

The Omega Migration Playbook (§1-6) is derived from these patterns. This document provides the **evidence base** so future maintainers can verify, extend, or challenge the playbook's assumptions.

---

## Case Study Index

| # | Project | Migration | Key Playbook Sections Informed |
|---|---------|-----------|--------------------------------|
| 1 | **Pydantic** | v1 → v2 (2023-2024) | §2.2, §2.3, §3.1, §3.2, §3.4 |
| 2 | **FastAPI** | Pydantic v1 → v2 integration (2024-2025) | §1.2, §2.1, §2.3 |
| 3 | **Kubernetes** | API deprecation policy (ongoing) | §1.1, §1.2, §2.1, §4.2 |
| 4 | **Django** | LTS release cycle & deprecation (ongoing) | §1.2, §2.1, §5.1 |
| 5 | **Python** | 2 → 3 (2008-2020) | §3.1, §3.2, §3.4, §5.1 |
| 6 | **Home Assistant** | Entity model breaking changes (2024-2026) | §1.1, §2.1, §2.3, §4.2 |
| 7 | **MCP** | SEP-2596 Feature Lifecycle (2026) | §1.1, §1.3, §2.1, §5.1 |
| 8 | **Zed/Tauri** | GPUI pre-1.0 breaking changes (ongoing) | §1.1, §3.1, §5.1 |

---

## 1. Pydantic v1 → v2 (2023-2024)

### 1.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Pydantic — Python data validation library |
| **Migration** | v1 (pure Python) → v2 (Rust core `pydantic-core`) |
| **Timeline** | v2.0 released June 2023; v1 support dropped in FastAPI 0.126.0 (Dec 2025) |
| **Breaking Changes** | 50+ method renames, `Optional[T]` default `None` removed, type coercion stricter, regex engine changed to Rust |
| **Sources** | [Official Migration Guide](https://pydantic.dev/docs/validation/latest/get-started/migration/) (2024), [FastAPI Migration Guide](https://fastapi.tiangolo.com/how-to/migrate-from-pydantic-v1-to-pydantic-v2/) (2024), [Tomodahinata Complete Guide](https://tomodahinata.com/en/blog/pydantic-v1-to-v2-migration-complete-guide/) (2026-06-26), [Medium: Migrating to Pydantic V2](https://medium.com/codex/migrating-to-pydantic-v2-5a4b864621c3) (2024-03-27) |

### 1.2 Deprecation Strategy

| Mechanism | Implementation |
|-----------|----------------|
| **Dual-namespace shim** | `pydantic.v1` namespace provides full v1 API inside v2 package; allows gradual migration |
| **Deprecation warnings** | `DeprecationWarning` emitted on every v1 method access (e.g., `.dict()`, `.json()`) |
| **Staged migration path** | 1) Upgrade to `pydantic>=1.10.17` (last v1) → 2) Install v2, run unmigrated modules with `from pydantic.v1 import ...` → 3) Migrate module by module |
| **Minimum window** | ~2.5 years (v2.0 Jun 2023 → FastAPI drops v1 Dec 2025) |

### 1.3 Tooling: `bump-pydantic`

| Aspect | Detail |
|--------|--------|
| **Tool** | [`bump-pydantic`](https://github.com/pydantic/bump-pydantic) — official codemod by Pydantic team |
| **Technology** | libcst-based (preserves formatting, comments) |
| **Scope** | Mechanical renames: `.dict()`→`.model_dump()`, `.json()`→`.model_dump_json()`, `.parse_obj()`→`.model_validate()`, Config class→`ConfigDict`, etc. |
| **Limitation** | **Cannot fix silent breaking changes**: `Optional[T]` default, type coercion, regex engine, Union resolution |

### 1.4 Silent Breaking Changes (The Real Danger)

| Change | v1 Behavior | v2 Behavior | Impact |
|--------|-------------|-------------|--------|
| `Optional[T]` | Omittable, default `None` | Required, allows `None` | **Highest impact** — fields become required silently |
| `float` → `int` coercion | Allowed (truncates) | Only if fractional part is zero | Data loss risk |
| `number` → `string` coercion | Allowed | Off by default | API breaks |
| `Union` resolution | Left-to-right | "Smart mode" (most specific) | Different validation results |
| Regex engine | Python `re` | Rust `regex` crate | Lookaround/backreference fail |

### 1.5 Communication & Documentation

| Artifact | Quality |
|----------|---------|
| **Official Migration Guide** | Excellent — comprehensive tables, before/after code, explains *why* |
| **FastAPI Integration Guide** | Excellent — framework-specific, version-pinned |
| **Community Guides** | High quality — Tomodahinata (2026) splits into "mechanical" vs "silent" layers |

### 1.6 Outcomes & Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **Dual-namespace shim enables staged migration** | §1.3, §7.3 — adopt for `pillars`→`slots` |
| **Mechanical renames ≠ complete migration** | §3.2 — codemod decision matrix must flag silent changes |
| **`Optional[T]` default removal is highest-risk silent change** | §2.3 Step 3 — explicit migration guide section for silent changes |
| **Framework integration guide critical** | §2.3 — Omega needs `docs/migrations/<feature>-migration.md` per framework surface (CLI, MCP, WAD) |
| **2.5-year window worked for ecosystem** | §1.2 — 6-month minimum is floor; complex migrations need longer |

---

## 2. FastAPI + Pydantic v2 Integration (2024-2025)

### 2.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | FastAPI — Python web framework built on Pydantic |
| **Migration** | Dropped Pydantic v1 support in FastAPI 0.126.0 (Dec 20, 2025) |
| **Sources** | [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/), [PyBlog: Pydantic v2 Migration](https://www.pyblog.in/programming/python/pydantic-v2-what-changed-and-why-your-apis-need-an-upgrade/) (2026-05-07) |

### 2.2 Strategy

| Mechanism | Implementation |
|-----------|----------------|
| **Version-pinned requirement** | `pydantic >= 2.7.0` in `pyproject.toml` / `setup.py` |
| **Deprecation warning in 0.127.0** | `pydantic.v1` imports raise `DeprecationWarning` |
| **Full removal in next release** | Hard deadline communicated clearly |
| **Migration guide** | [fastapi.tiangolo.com/how-to/migrate-from-pydantic-v1-to-pydantic-v2/](https://fastapi.tiangolo.com/how-to/migrate-from-pydantic-v1-to-pydantic-v2/) |

### 2.3 Key Pattern: Framework Owns the Deadline

FastAPI **did not wait** for ecosystem readiness. They set a date, communicated it, and enforced it. The Pydantic team's `pydantic.v1` shim bought time, but FastAPI's deadline forced action.

**Omega Application**: Engine core sets deprecation deadlines; WADs/stacks must comply. No "ecosystem readiness" veto.

---

## 3. Kubernetes API Deprecation Policy (Ongoing)

### 3.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Kubernetes — Container orchestration platform |
| **Policy** | [Kubernetes Deprecation Policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/) (updated 2024-10-25) |
| **Migration Guide** | [Deprecated API Migration Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/) (updated 2025-05-16) |
| **Sources** | [Plural.sh Practical Guide](https://www.plural.sh/blog/deprecated-kubernetes-apis/) (2026-01-22) |

### 3.2 Policy Mechanics

| Track | Deprecation Window | Removal Window | Notes |
|-------|-------------------|----------------|-------|
| **GA (v1)** | 12 months or 3 releases | 12 months or 3 releases after deprecation | "No plans for major version removing GA APIs" |
| **Beta (v1beta1)** | 9 months or 3 releases | 9 months or 3 releases after deprecation | Max version skew = 2 releases |
| **Alpha (v1alpha1)** | May be removed ANY release without notice | N/A | Experimental only |

**Key Rule**: Beta APIs deprecated ≤9 months or 3 minor releases after introduction; removed ≤9 months or 3 releases after deprecation.

### 3.3 Migration Guide Structure

Each deprecated API has a dedicated section:

```markdown
### <Resource Name>

The **<group>/<version>** API version of <Resource> is no longer served as of v1.XX.

* Migrate manifests and API clients to use the **<group>/<new-version>** API version, available since v1.YY.
* All existing persisted objects are accessible via the new API
* Notable changes in **<group>/<new-version>**:
  + <Specific behavioral change 1>
  + <Specific behavioral change 2>
```

### 3.4 Testing with Deprecated APIs Disabled

```bash
# API server flag to simulate removal
--runtime-config=<group>/<version>=false
# Example:
--runtime-config=admissionregistration.k8s.io/v1beta1=false
```

### 3.5 Outcomes & Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **Track-based policy (GA/Beta/Alpha) with explicit windows** | §1.1 — Omega: Active/Deprecated/Removed with 6-month minimum |
| **Migration guide per API with "Notable changes" behavioral diffs** | §2.3 — Silent breaking changes called out explicitly |
| **Runtime simulation flag (`--runtime-config`)** | §4.2 — Omega: `OMEGA_DISABLE_<FEATURE>=1` for testing removal |
| **Persisted objects accessible via new API** | §7.3 — Dual-name shim must preserve data compatibility |
| **Version skew = 2 releases max** | §1.2 — Omega monthly minors → 3-release window aligns |

---

## 4. Django LTS Release Cycle & Deprecation (Ongoing)

### 4.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Django — Python web framework |
| **Release Cycle** | 8-month feature releases; **LTS every 3rd release (3-year support)** |
| **Sources** | [Django 5.2 LTS Release](https://www.djangoproject.com/weblog/2025/apr/02/django-52-released/) (2025-04-02), [TuxCare EOL Guide 2026](https://tuxcare.com/blog/django-eol-guide-2026/), [gdevops.frama.io version table](https://gdevops.frama.io/django/versions/5.2/5.2.html) |

### 4.2 Deprecation Mechanics

| Mechanism | Implementation |
|-----------|----------------|
| **Deprecation warnings** | `RemovedInDjangoXXWarning` emitted 2+ releases before removal |
| **LTS as stability anchor** | LTS releases (3.2, 4.2, 5.2) receive only security fixes; no new deprecations |
| **Deprecation timeline** | Feature deprecated in X.Y → removed in X.(Y+2) (two feature releases) |
| **Documentation** | [Django Deprecation Timeline](https://docs.djangoproject.com/en/stable/internals/deprecation/) per release |

### 4.3 EOL Reality (TuxCare 2026 Analysis)

- Django 3.2, 4.0, 4.1, 5.0, 5.1 **all EOL** as of 2026
- Running EOL = unpatched CVEs, compliance failures, ecosystem drift
- **Breaking changes accumulate** — delayed migration = exponentially harder

### 4.4 Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **LTS cadence creates predictable deprecation windows** | §1.2 — Omega: consider annual LTS post-v1.0 |
| **Deprecation warnings 2 releases before removal** | §1.1 — 6-month / 3-minor window ≈ 2 releases |
| **EOL creates compounding risk (security + ecosystem)** | §5.1 — Post-mortem must capture "delay cost" |
| **Third-party support (TuxCare) exists for EOL** | §4.2 — Omega: local tracking enables self-support |

---

## 5. Python 2 → 3 Migration (2008-2020)

### 5.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Python language |
| **Migration** | Python 2 (EOL Jan 2020) → Python 3 |
| **Duration** | ~12 years (Python 3.0 Dec 2008 → 2.7 EOL Jan 2020) |
| **Sources** | [RealPython Recap](https://realpython.com/lessons/converting-code-python-2-3-recap/), [FullScale 2026](https://fullscale.io/blog/python-2-to-3-migration/), [KnowledgeLib 2026](https://knowledgelib.io/software/migrations/python2-to-python3/2026), [ScoutAPM 2020](https://www.scoutapm.com/blog/automated-tools-and-strategies-to-help-migrate-from-python-2-to-3) |

### 5.2 Tooling Evolution

| Era | Tool | Status |
|-----|------|--------|
| 2008-2020 | `2to3` (stdlib `lib2to3`) | **Removed in Python 3.13 (Oct 2024)** |
| 2015+ | `futurize` (python-future) | Active — supports Python 3.8+ |
| 2016+ | `python-modernize` (based on `six`) | Active |
| 2020+ | **LibCST** | **Modern standard** — CST preserves formatting |
| 2022+ | **ast-grep** | Polyglot, Rust-based, fast |

### 5.3 Migration Strategies Used

| Strategy | Description | Notable User |
|----------|-------------|--------------|
| **Big Bang** | Convert all at once | Small projects |
| **Straddle** | Code runs on both 2 & 3 (`six`, `__future__`) | Instagram (zero-downtime) |
| **Incremental** | Module-by-module with `tox` multi-version testing | Most large codebases |

### 5.4 Instagram's Zero-Downtime Strategy (ScoutAPM 2020)

1. All new code Python 2+3 compatible with tests
2. Pick module → convert → test on both → merge
3. Release to internal users → beta → 100% rollout
4. Delete compatibility code after full rollout
5. **Key**: `tox` for multi-version CI; percentage rollout

### 5.5 Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **`2to3` removed — LibCST/ast-grep are modern standard** | §3.1 — Tool selection matrix reflects 2025-2026 reality |
| **Straddle pattern (dual compatibility) works for large codebases** | §7.3 — Dual-name shim is straddle pattern |
| **`tox` multi-version CI essential** | §4.2 — Omega: `OMEGA_DISABLE_<FEATURE>` for removal simulation |
| **Percentage rollout reduces blast radius** | §6 — Adoption window with gradual enforcement |
| **12-year timeline — ecosystem moves slowly** | §1.2 — 6-month minimum is aggressive; plan for longer |

---

## 6. Home Assistant Breaking Changes (2024-2026)

### 6.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Home Assistant — Home automation platform |
| **Migration** | Device tracker entity model changes (2026-06-15) |
| **Sources** | [Home Assistant Developer Blog](https://developers.home-assistant.io/blog/2026/06/15/device-tracker-changes/) (2026-06-15) |

### 6.2 Deprecation Mechanics

| Mechanism | Implementation |
|-----------|----------------|
| **Architecture Proposals** | Each deprecation linked to GitHub Discussion: [#627](https://github.com/home-assistant/architecture/discussions/627), [#1387](https://github.com/home-assistant/architecture/discussions/1387), [#1389](https://github.com/home-assistant/architecture/discussions/1389) |
| **Explicit removal version** | "Will stop working in Home Assistant Core **2027.7**" (13+ months notice) |
| **Capability attributes** | New `tracking_type` attribute distinguishes entity behaviors |
| **Migration path** | `battery_level` → separate battery sensor; `location_name` → `in_zones` list |

### 6.3 Communication Pattern

```markdown
## Deprecation of `battery_level`

The `battery_level` property has been deprecated in all device tracker base classes, 
and will stop working in Home Assistant Core 2027.7. 
Integrations should communicate battery level via a battery sensor instead.

More details can be found in [architecture proposal #627](...)
```

### 6.4 Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **Architecture proposals as deprecation RFCs** | §2.1 — SEP/ADR format mirrors this |
| **Explicit removal version (not "soon")** | §1.3 — Timeline must have concrete version + date |
| **Capability attributes for behavioral differentiation** | §2.3 — Migration guide must explain new behavioral model |
| **13-month window for entity model changes** | §1.1 — 6-month minimum; complex integrations need more |

---

## 7. MCP SEP-2596: Feature Lifecycle & Deprecation Policy (2026)

### 7.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Model Context Protocol (MCP) |
| **SEP** | [SEP-2596](https://modelcontextprotocol.io/seps/2596-spec-feature-lifecycle-and-deprecation) (Final, 2026-04-17) |
| **Feature Lifecycle** | [Feature Lifecycle Policy](https://modelcontextprotocol.io/community/feature-lifecycle) |
| **Changelog** | [MCP Changelog](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/draft/changelog.mdx) |
| **Blog Analysis** | [MCPBlog: Deprecating Sampling, Roots, Logging](https://mcpblog.dev/blog/2026-04-17-mcp-deprecating-sampling-roots-logging) (2026-04-17) |

### 7.2 Policy Mechanics

| State | Criteria | Minimum Window |
|-------|----------|----------------|
| **Active** | Fully supported | N/A |
| **Deprecated** | SEP accepted; replacement Active; migration path documented | **12 months** (measured from deprecation revision release) |
| **Removed** | Deprecation window complete | N/A |

**Key Rule**: "A feature is not deprecated under this policy while its documented replacement is still only in `draft`."

### 7.3 Deprecation SEP Requirements

Every deprecation SEP MUST:
1. Identify feature by name + link to `schema.ts` + spec prose
2. State rationale against criteria
3. Document migration path (or state none required); replacement MUST be Active
4. Specify minimum deprecation window (≥12 months)
5. Assign earliest removal revision

### 7.4 Expedited Removal Clause

> "If a feature is later found to be unsafe, the project may remove it before the deprecation window expires via an Expedited Removal SEP."

### 7.5 Simultaneous Deprecations (SEP-2577 + SEP-2596)

| Feature | Deprecated | Migration Path |
|---------|------------|----------------|
| **Sampling** | SEP-2577 | Direct LLM API calls; purpose-built coordination layers |
| **Roots** | SEP-2577 | Tool parameters, resource URIs, server config |
| **Logging** | SEP-2577 | `stderr` (stdio) or OpenTelemetry |
| **HTTP+SSE Transport** | SEP-2596 reclassification | Streamable HTTP |

### 7.6 Lessons for Omega

| Lesson | Playbook Mapping |
|--------|------------------|
| **SEP process for deprecation (not removal)** | §2.1 — Omega: SEP/ADR in `docs/decisions/` |
| **Replacement must be Active before deprecation** | §1.3 — Hard rule in playbook |
| **12-month minimum window (MCP) vs 6-month (Omega)** | §1.1 — Omega's 6-month is aggressive; document rationale |
| **Expedited removal for security** | §1.1 — Add "Security Expedited" clause |
| **Changelog tracks deprecated features registry** | §2.1 — Omega: CHANGELOG.md `### Deprecated` section |

---

## 8. Zed / Tauri / GPUI (Ongoing Pre-1.0)

### 8.1 Context

| Attribute | Detail |
|-----------|--------|
| **Project** | Zed — Code editor written in Rust |
| **UI Framework** | **GPUI** — Custom GPU-accelerated framework (pre-1.0) |
| **Sources** | [Zed.dev](https://zed.dev/) (2026-08-12), [GPUI GitHub](https://github.com/zed-industries/zed/tree/main/crates/gpui), [gpui-unofficial docs](https://docs.rs/gpui-unofficial/latest/gpui/index.html) |

### 8.2 Breaking Change Reality

| Aspect | Detail |
|--------|--------|
| **Versioning** | Pre-1.0 — **breaking changes between versions expected** |
| **GPUI README** | "GPUI is still in active development... There will often be breaking changes between versions." |
| **Migration Support** | Minimal — users expected to track `main` or pin versions |
| **Ecosystem** | Extensions must adapt to GPUI changes |

### 8.3 Lessons for Omega (Post-Debut = Post-1.0)

| Lesson | Playbook Mapping |
|--------|------------------|
| **Pre-1.0 breaking changes are expected; post-1.0 they are NOT** | §1.1 — Omega post-debut = post-1.0 semantics |
| **Custom framework = migration burden on users** | §3.2 — Omega's codemod investment reduces user burden |
| **No formal deprecation policy pre-1.0** | §1.1 — Omega MUST have policy before debut |
| **Extension ecosystem breaks with core** | §7.3 — WAD/stack migration must be supported |

---

## 9. Cross-Case Synthesis: Patterns for Omega

### 9.1 Deprecation Window Norms

| Project | Window | Omega Adoption |
|---------|--------|----------------|
| Kubernetes GA | 12 months / 3 releases | **6 months / 3 minors** (more aggressive) |
| Kubernetes Beta | 9 months / 3 releases | N/A |
| Pydantic/FastAPI | ~2.5 years (ecosystem-driven) | **6 months minimum** (engine-driven) |
| Django | 2 feature releases (~16 months) | **6 months / 3 minors** |
| Home Assistant | 13+ months (explicit version) | **6 months minimum; extend for complex** |
| MCP | 12 months minimum | **6 months minimum** |
| Python 2→3 | 12 years | N/A (language-level) |

**Omega Rationale**: Monthly minors + engine-core control = shorter window feasible. **But** complex WAD migrations may need extension — playbook allows this via adoption check gate.

### 9.2 Tooling Convergence (2025-2026)

| Language | Winner | Runner-up |
|----------|--------|-----------|
| **Python** | **LibCST** (CST, preserves formatting) | ast-grep (polyglot) |
| **YAML/JSON/Config** | **ast-grep** (structural, YAML-native) | LibCST (via YAML parsing) |
| **Polyglot/Complex** | **gritql** / **codemod CLI** | Evaluate per case |

**Omega Decision**: LibCST for Python, ast-grep for YAML/WAD configs.

### 9.3 Communication Convergence

| Pattern | Projects Using | Omega Adoption |
|---------|----------------|----------------|
| **RFC/SEP for deprecation decision** | MCP, Kubernetes, Home Assistant | ✅ §2.1 |
| **Explicit removal version in announcement** | Home Assistant, Kubernetes, MCP | ✅ §1.3 |
| **Migration guide per feature** | Pydantic, FastAPI, Kubernetes, Home Assistant | ✅ §2.3 |
| **Dual-namespace/dual-API shim** | Pydantic (`pydantic.v1`), Kubernetes (API versions) | ✅ §7.3 |
| **Runtime simulation flag** | Kubernetes (`--runtime-config`) | ✅ §4.2 (`OMEGA_DISABLE_<FEATURE>`) |

### 9.4 Tracking Convergence (Telemetry-Free)

| Project | Mechanism | Omega Adoption |
|---------|-----------|----------------|
| **Kubernetes** | `--runtime-config` for testing; no usage telemetry | ✅ Local tracker + simulation flag |
| **Pydantic** | Deprecation warnings only; no central tracking | ✅ Local JSONL + opt-in counter |
| **Home Assistant** | Architecture proposals (GitHub Discussions) | ✅ SEP/ADR in `docs/decisions/` |
| **MCP** | SEP process; no runtime tracking specified | ✅ Local tracker + issue template |

---

## 10. Evidence Traceability Matrix

| Playbook Section | Primary Case Studies | Key Evidence |
|------------------|---------------------|--------------|
| §1.1 Feature Lifecycle | MCP SEP-2596, Kubernetes, Home Assistant | 3-state model, minimum windows, replacement-Active rule |
| §1.2 Versioning & Cadence | Django LTS, Kubernetes releases, FastAPI | Monthly minors, LTS anchor, framework-owned deadline |
| §1.3 Announcement Requirements | MCP SEP template, Home Assistant architecture proposals | SEP format, migration path mandatory, timeline fields |
| §2.1 Deprecation Notice Conventions | MCP SEP-2596, Home Assistant blog posts | RFC-style, GitHub Discussion links, explicit version |
| §2.2 Runtime Warning Standard | Pydantic `DeprecationWarning`, Django `RemovedInDjangoXXWarning` | Structured template, stderr + structured log |
| §2.3 Migration Guide Template | Pydantic, FastAPI, Kubernetes, Home Assistant | Answer-First, codemod command, silent changes table |
| §3.1 Tool Selection | Pydantic `bump-pydantic` (libcst), Python 2→3 (LibCST/ast-grep), ast-grep GitHub | 2025-2026 tool landscape |
| §3.2 Build Decision Framework | Pydantic (mechanical vs silent), Python 2→3 (straddle vs big bang) | Decision tree with silent-change awareness |
| §3.4 libcst Pattern | Pydantic `bump-pydantic` source, LibCST docs | CSTTransformer preserving formatting |
| §3.5 ast-grep Pattern | ast-grep README, YAML structural matching | Rule-based YAML transformation |
| §4.2 Local Tracking | Kubernetes (no telemetry), Pydantic (warnings only), M8 mandate | JSONL log + opt-in counter + issue template |
| §5.1 Post-Mortem Template | Google SRE, Etsy Morgue, Atlassian, SLAShield | 5-section, blameless, 5 Whys, action items |
| §5.2 System Mapping | PIVOT_LOG, Soul Distillation, Corpus Map, Hivemind | Omega-specific integration |
| §7 Pillar→Node Application | All above applied to 23 violations | Concrete mapping |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CASE-STUDIES ⬡ v1.0.0 ⬡ 2026-08-22*