<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Omega Engine — PR, Public Cut, and Release Standards

**Entity**: @makali (MaKaLi, Build/Run Governance)
**Date**: 2026-10-12
**Status**: DRAFT — pending Jem review, then Architect ratification
**Canonical home**: `docs/operations/`
**Mandates**: M4 (plan→verify→execute), M13 (Temple-Grade before release),
M23 (failure integrity), M24 (venv sovereignty), M26 (doc standards),
M27 (tracking integrity), M28 (artifact preservation),
M29 (remote claim integrity), M30 (third-party boundary & public secret exemption)

---

## 0. How to read this document

Every normative rule carries one of two labels:

| Label | Meaning |
|:--|:--|
| **CI-REQUIRED** | A workflow, Makefile target, or pre-commit hook **blocks** merge or release when the rule is violated. |
| **RECOMMENDED** | A documented convention enforced by reviewer checklist and human attestation. |

If a rule is marked CI-REQUIRED but no gate exists for it, that is a **known gap**
and is recorded in §11. A CI-REQUIRED rule without a gate is a documentation lie —
the same failure class as a `package-data` glob pointing at files that do not
exist. Do not let this document accumulate unenforced SHALLs.

**Unenforced claims are worse than absent rules.** Where external research could
not verify a norm, this document says so explicitly rather than asserting it.

### 0.5 If you are cutting a release today

Tag immutability (§4.1) is the most consequential rule here, and it is easy to
bury under allowlist mechanics. If you are doing a release right now, do these in
order and stop if any fails:

1. **Sync** — `git fetch origin --prune`. Never trust a local branch ref (§4.1).
2. **Fresh clone the cut** — verify outside your working checkout (§6.3).
3. **Gate** — bootstrap, check-engine, temple-grade, M23; confirm zero live-state mutation (§6.2).
4. **Tag annotated on an explicit SHA** — `git tag -a vX.Y.Z <sha>`, never a branch name (§4.1).
5. **Assert the peel before push** — `git rev-parse vX.Y.Z^{commit}` == cut head (§4.1).
6. **Push, then re-assert** — `git ls-remote --tags origin` (§4.1).
7. **Clean build** — `rm -rf build/ dist/ src/*.egg-info`, then `python -m build` (§5.2).
8. **Inspect the artifact** — wheel contents vs the packaging allowlist (§5.1).
9. **Smoke-test outside the repo** — install the wheel in a clean venv (§6.2).
10. **Publish and clean duplicates** (§4.4).

Full detail in §10.3. If any step is skipped, say so in the tag message rather
than implying a green result.

---

## 1. Scope and authority

### 1.1 Scope

This document governs three adjacent activities and the verification they depend on:

1. **Pull requests** — how changes reach `main`.
2. **Public cut** — what subset of the repository is allowed to ship.
3. **Release** — how a verified cut becomes an immutable, installable artifact.

Verification (§6), packaging (§5), CI (§7), documentation (§8), and roles (§9)
exist to serve those three. Where this document conflicts with a workflow file,
**the workflow is ground truth and this document is stale** — fix the document in
the same PR that changes behavior.

### 1.2 Authority order

Precedence is unchanged and absolute:

```
SOVEREIGN_MANDATES.md  (Law)
  → sprint SSOT (ACTIVE_SPRINT.json)
    → Hub NEXT_ACTION
      → vision / strategy docs
        → this document
```

A mandate overrides this document. This document overrides habit.

### 1.3 Citation rule (D-609)

When citing a mandate, cite the **ID**, and the ID must equal the section number
in `SOVEREIGN_MANDATES.md`. `SOVEREIGN_MANDATES.md` is **M1–M30**, and
`MANDATES_CONDENSED.md` is the v3.11.0 tier-0 injection of the same 30 laws.

> **Known defect (G17).** The 27-law count lives in
> `scripts/check_mandate_compliance.py`, which enumerates M1…M27 over a
> 30-mandate set — a coverage gap in the checker, not a stale tier-0 file. See
> §11.
>
> **Known defect (G18).** `SOVEREIGN_MANDATES.md` §28/§29/§30 carry inline tags
> `(M29)`/`(M30)`/`(M35)` that disagree with their section numbers, violating
> D-609 (`DOCS_ACCURACY_AUDIT_20261003.md:60-100`, Finding A). Citations that
> resolve to the wrong law are a governance-tier hazard. See §11.

### 1.4 Standing decisions

These were ratified for this document and should not be relitigated without an
Architect-level decision carrying a decision ID:

| Decision | Value |
|:--|:--|
| Canonical location | `docs/operations/` |
| Scope | Full (PR + cut + release) |
| Version policy | **New tag for every fix.** A published tag is never moved. |
| Public-history posture | Revisit later. **No history rewrite is in scope now.** |
| Merge model | **Direct push to `main`.** Merge-gating (§7.4) is therefore off by architecture, not by omission. |

---

## 2. Pull-request standards

### 2.1 Commits and branches

| Rule | Level | Detail |
|:--|:--|:--|
| Commit messages follow Conventional Commits | **RECOMMENDED** — *no commit-lint gate exists (G19)* | `type(scope): description`. `feat` → MINOR, `fix` → PATCH, `BREAKING CHANGE` / `!` → MAJOR. Squash-merge at the merge commit is the supported path. |
| Branch naming | **RECOMMENDED** | `feat/*`, `fix/*`, `research/*`, `chore/*` from `main`. |
| PR targets `main` | **RECOMMENDED** — *see G19* | `CONTRIBUTING.md:159` still names a historical branch `release/debut-v1.6.0`; workflows gate `main` / `release/initial-v1` / `develop` / `release/debut`. Resolve before wiring any base-branch check. |

> **Gap (G2):** `CONTRIBUTING.md:156,169` calls `temple-grade` "decorative until
> PR-H wiring lands". That is **stale**. `ci.yml:65-70` and `release.yml:51-53`
> both gate on it. Fix the wording; do not let contributors skip it locally.

### 2.2 PR template

The template at `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md` is the
required form.

| Rule | Level |
|:--|:--|
| All template sections completed (Summary / Changes / Testing / Documentation / Checklist) | **RECOMMENDED** — *GitHub has no native completeness gate; no custom check exists (G19)* |
| Testing section states the **actual** commands run and their real results | **RECOMMENDED** |
| Documentation section names every doc touched, or states "none needed" | **RECOMMENDED** |

> **Gap (G1) — stale mandate checklist.** The template lists M1, M7, M8, M9, M11,
> M13, M22, M23, M24, M26, M27. It **omits M14, M28, M29, M30**, which are in
> force. Contributors attesting to that list are not attesting to the real law
> set. Fix the list before wiring the completeness gate, or the gate will
> enforce the wrong thing.

### 2.3 Required checks before merge

| Gate | Level | Source |
|:--|:--|:--|
| `pytest tests/` passes | **CI-REQUIRED** | `ci.yml` |
| flake8 hard errors (`E9,F63,F7,F82`) clear | **CI-REQUIRED** | `ci.yml` |
| `make check-mandates` (reaches `check-mandate-compliance` transitively via `Makefile:753`) | **CI-REQUIRED** | `ci.yml:63` |
| `make temple-grade require_clean=1 HUB_IMPORT_MODE=pristine` | **CI-REQUIRED** | `ci.yml:65-70` |
| Secret scan (gitleaks + truffleHog + C3 mirror) | **CI-REQUIRED** | `secrets.yml`, `secret-scan.yml` |
| REUSE lint exits 0 | **CI-REQUIRED** — *currently RED; see note* | `reuse-compliance.yml:40-45` |
| ≥1 maintainer approval | **CI-REQUIRED** — *requires branch protection, not configured* | — |

> **REUSE waiver reality check.** `reuse-compliance.yml` runs a bare `reuse lint`
> with **no waiver logic whatsoever** — the waiver is a human document, not a
> machine input. So the gate is RED and the exception is enforced only by people
> reading `docs/operations/REUSE_WAIVER_DEBUT_20261003.md`. Treat this as an
> open compliance gap (G6), not as a satisfied gate.

> **Gap (G15):** `main` is **protected** (§9.1) against force-push, deletion, and
> unresolved conversations — verified by real rejected pushes, not by reading
> settings. Required reviews are deferred because this is a **solo-maintainer
> repository** (`Xoe-NovAi` is the only collaborator) and would deadlock. Required
> status checks are **declined by architecture**, not oversight — see §7.4.

### 2.4 AI disclosure

Contributors disclose AI-generated or AI-assisted work via `AI-generated:` /
`AI-assisted review:` in the PR body or commit trailer. Unattributed AI output is
not acceptable.

**RECOMMENDED**, project-local policy.

> External research found **no authoritative cross-project AI-disclosure norm**.
> Several individual projects require disclosure, but this was not verified
> against primary sources. Keep this as project policy and do not describe it as
> an industry requirement.

### 2.5 Contributor licensing

`CONTRIBUTING.md:31-75` offers a CLA (required for corporate contributors,
recommended for individuals) **or** a DCO `Signed-off-by`.

**RECOMMENDED.**

> No CLA bot or DCO app configuration exists in this repo, so neither is
> mechanically enforced. This is an unenforced claim of the kind §0 warns about.
> Either wire a DCO check or drop the claim. See G3 in the register.

---

## 3. Public-cut standards

### 3.1 The allowlist is the SSOT

`docs/strategy/PUBLIC_ALLOWLIST.txt` is the single source of truth for what may
ship. `.gitignore` is **not** an allowlist mechanism — it describes the working
tree, not the release surface.

- **ALLOW** — patterns permitted in the public cut.
- **FORGE** — patterns explicitly excluded, checked *before* ALLOW.
- **Explicit Exclusions** — retained as `KEEP_EXTRA` entries.

**Precedence, preserved exactly** (`scripts/apply_public_allowlist.sh`):

```
exception  >  keep-extra  >  FORGE  >  allowlist  >  remove
```

| Rule | Level |
|:--|:--|
| Cut produced only by `scripts/apply_public_allowlist.sh` | **CI-REQUIRED** |
| Default is dry-run; `--confirm` mutates the index | **CI-REQUIRED** |
| `--confirm` requires a clean tracked tree | **CI-REQUIRED** |
| Removed-file count is exactly `0` on `release/debut` and on tags | **CI-REQUIRED** |
| VULN#6 (silent-allow-all patterns such as `.`, `*`, `**`) blocks under `--strict` | **CI-REQUIRED** |
| Symlink leak audit blocks under `--strict` | **CI-REQUIRED** |
| Pre-cut secret-history disposition check | **CI-REQUIRED** |
| ALLOW section has ≥5 patterns and all three sections present | **CI-REQUIRED** |

### 3.2 Expanding the public surface

| Rule | Level |
|:--|:--|
| Moving a path from FORGE to ALLOW requires **Architect sign-off** with a decision ID | **CI-REQUIRED** by process |
| The cut script and its setup counterpart must remain in the public tree | **CI-REQUIRED** |

**Never mass-`git rm` and rewrite history in the same week as a filter-repo.**
M28 requires transitions to be explicit, auditable, and recoverable.

### 3.3 Translator fragility

`glob_to_regex` in the cut script has quirks (`**` → `\.*` literal-dot behavior)
that downstream tests pin with fuzz parity.

| Rule | Level |
|:--|:--|
| Do not change glob translation order without a fuzz-parity run **and** a boundary diff | **CI-REQUIRED** |

> **Known issue (G13 / D-628):** 13 entries written as `[CUT-…]` inside Explicit
> Exclusions are parsed as **KEEP**. Files intended for exclusion are retained.
> This is a boundary semantics decision requiring an owner. See §11.

### 3.4 What must never ship

Confirmed by inspection of the `v1.6.0-alpha` tag tree:

- `docs/federation/` — Node 1 handover material
- `src/omega_youtube_research/` — parked research module
- `config/wads/arcana_novai/` — ANAi WAD (not Omega IWAD)
- `data/entities/sophia/` — undefined entity, not Omega IWAD
- `data/entities/makali_fusion/` — superseded fork
- internal `data/` paths: `handoff/`, `logs/`, `quarantine/`, `federation/`, `knowledge/`
- `src/omega/vault/` — excluded per D-565
- host-local configs (`*.local.yaml`), credentials, `keys/`

> **Near-miss worth recording:** during the `v1.6.0-alpha` cycle, a
> `cp -r config/*` into the package-data directory swept in `keys/`,
> `*.local.yaml`, and the whole ANAi WAD. It was caught only by inspecting the
> built wheel. This is the concrete reason §5 mandates explicit file lists.

---

## 4. Release, tag, and artifact standards

### 4.1 Tags are immutable

This is the single most consequential rule in this document.

| Rule | Level |
|:--|:--|
| Tag shape is `v*.*.*` | **CI-REQUIRED** (workflow trigger) |
| Release tags are **annotated** (`git tag -a`), never lightweight | **CI-REQUIRED** |
| **A published tag is never moved, force-updated, or deleted** | **CI-REQUIRED** |
| **New tag for every fix.** A correction ships as a new version | **CI-REQUIRED** |
| The tag is created on an **explicit SHA**, never on a branch name | **CI-REQUIRED** |
| Peel assertion before push: `git rev-parse <tag>^{commit}` equals the intended cut head | **CI-REQUIRED** |
| Refs synced before tagging: `git fetch origin --prune` | **CI-REQUIRED** |

**Why explicit SHA and not a branch name.** During the `v1.6.0-alpha` cycle, the
tag was created from a stale local `release/debut` ref that had not moved when the
branch was force-pushed. The tag silently marked the wrong tree and published
ruling-violating content. The same class of defect recurred in verification, where
a fresh clone from a local path resolved to the stale branch instead of the remote.

Two rules prevent recurrence:
1. Tag `origin/release/debut`'s resolved SHA, never the local branch name.
2. Assert the peel equals that SHA **before** pushing, and re-assert via
   `git ls-remote` **after** pushing.

> Git does not technically forbid `git tag -f`. **This repo does** — an active
> tag ruleset blocks tag updates and deletions, and immutable releases are on
> (§9.3). Both were verified by real rejected pushes, not by reading settings.
> Recovery is deliberate: disable the ruleset, fix, re-enable.

### 4.2 Versioning

SemVer 2.0.0. Prerelease identifiers are hyphen + dot-separated:
`1.6.0-alpha`, `1.6.0-alpha.1`, `1.6.0-rc.1`. Prerelease sorts **below** the
normal version, and `alpha < alpha.1 < beta < rc.1 < normal`.

The `v` prefix is a **tag convention**, not part of the SemVer version. `pyproject.toml`
carries `1.6.0-alpha` (no `v`).

| Rule | Level |
|:--|:--|
| Tag version, `pyproject.toml` version, and CHANGELOG heading agree | **CI-REQUIRED** — *no gate exists yet* |

> **Gap (G9):** version drift has already occurred in this repo
> (`1.6.0-alpha` vs `1.6.0-alpha.1` vs `1.6.1-alpha` in different documents).
> No CI check enforces consistency.

### 4.3 Changelog

| Rule | Level |
|:--|:--|
| Every tag has a `## [x.y.z] - YYYY-MM-DD` CHANGELOG section | **CI-REQUIRED** |
| Release notes are non-empty; **empty-notes fallback is forbidden** | **CI-REQUIRED** |
| Sections used: Added / Changed / Fixed / Security; empty sections omitted | **RECOMMENDED** |
| `CHANGELOG.md` is canonical; GitHub-generated notes are supplementary | **RECOMMENDED** |

> **Gap (G8):** `release.yml:70` still permits
> `|| echo "No changelog section found"`, which ships a release with no notes.
> That directly contradicts the PR-template requirement to update the CHANGELOG.
> This fallback must become fail-closed.

### 4.4 Release creation

`release.yml` creates releases with deterministic `gh` CLI calls
(`gh release delete <tag> -y || true`, then `gh release create`), replacing
`softprops/action-gh-release`, whose retry logic produced duplicate drafts for a
moved tag and then failed finalizing with `already_exists`.

| Rule | Level |
|:--|:--|
| Exactly one release per tag | **CI-REQUIRED** |
| Stale releases for the tag are removed before creating | **CI-REQUIRED** |
| The delete step **never deletes or moves the tag** | **CI-REQUIRED** |
| Duplicate-release handling is acceptable **only** alongside tag-immutability proof | **RECOMMENDED** |

> There is no universal external norm for duplicate-release handling. Delete-then-
> create is tool-specific (`gh`). Keep it, but keep it paired with §4.1 — otherwise
> it normalizes moving tags.

### 4.5 Artifacts and provenance

| Rule | Level |
|:--|:--|
| Build sdist + wheel via `python -m build` (isolated; **never** `--no-isolation`) | **CI-REQUIRED** |
| Release workflow: temple-grade → changelog → build → publish → verify install | **CI-REQUIRED** |
| Published artifacts carry SHA-256 checksums | **RECOMMENDED** |
| SBOM export | **RECOMMENDED** — *GitHub/PyPI attestation support is evolving; not a SHALL* |
| Signed provenance (Sigstore/cosign) | **RECOMMENDED** — *project-specific, tool-pinned* |

---

## 5. Packaging standards

### 5.1 Explicit file lists only

| Rule | Level |
|:--|:--|
| `package-data` uses an **explicit** pattern list | **RECOMMENDED** — *no wheel-content gate (G10)* |
| **Never copy a directory tree into the package.** Copy named files | **RECOMMENDED** — *no gate (G10)* |
| No host-local configs (`*.local.yaml`), credentials, or `keys/` in any artifact | **RECOMMENDED** — *no gate (G10)* |
| No absolute machine paths in packaged config | **RECOMMENDED** |
| Packaged defaults are verbatim copies of already-public files, same license | **RECOMMENDED** |

Prefer explicit `package_data` over `include_package_data`. Broad VCS/MANIFEST
inclusion combined with an exclusion list is a known-broken combination
(setuptools issue #3260 — exclusions silently do not take effect), and
`exclude_package_data` interacts the same way. An explicit allowlist is narrower,
auditable, and does not depend on exclusion behavior.

### 5.2 Clean build required

Stale `build/` and `*.egg-info/` directories silently contaminate wheels.

| Rule | Level |
|:--|:--|
| Release build runs after `rm -rf build/ dist/ src/*.egg-info`, or in a fresh worktree | **CI-REQUIRED** |
| Build is isolated (`python -m build`, not `--no-isolation`) | **CI-REQUIRED** |
| `build/`, `dist/`, `*.egg-info/` are gitignored | **CI-REQUIRED** |

> **Observed failure:** a wheel built after a bad copy contained 69 packaged
> config files including `wads/arcana_novai/**`, `github_accounts.yaml`, and
> `lan_exposure_allowlist.local.yaml`, while the source tree held exactly four.
> The contamination came entirely from `build/`. The tree was clean; the cache
> was not. **Inspecting the artifact, not the source, is the only reliable check.**

### 5.3 Config resolution contract

All runtime config access goes through `CONFIG_DIR` from
`src/omega/governance/config_resolver.py`. No module may compute its own config
path from `__file__` parents or a relative `Path("config/...")`.

| Rule | Level |
|:--|:--|
| Config paths resolve via `CONFIG_DIR` | **RECOMMENDED** — *no automated sweep (G20)* |
| Every file read at startup is **enumerated and packaged** | **RECOMMENDED** — *no gate (G20)* |
| Optional configs degrade gracefully when absent | **RECOMMENDED** — *no gate (G20)* |

Resolution order: `OMEGA_CONFIG_DIR` → source tree → CWD → `~/.config/omega` →
package data.

> **Observed failure:** `capability_matrix.py` and `federation_invariant.py` both
> bypassed `CONFIG_DIR`. The wheel published fine because source installs found
> the files, then crashed on the published wheel with
> `FileNotFoundError: Capability matrix not found`. File-by-file fixing is not a
> strategy — §11 records the required full-sweep gate.

### 5.4 First-run state

| Rule | Level |
|:--|:--|
| Every state store initializes its directory and schema before first use | **RECOMMENDED** — *no gate* |
| A read on a fresh install returns empty rather than raising | **RECOMMENDED** |
| A fresh-install smoke test runs against an empty data directory | **RECOMMENDED** |

> **Observed failure:** `USMManager` had nine `sqlite3.connect()` sites that
> assumed the state directory and schema already existed. A fresh install died
> with `OperationalError: unable to open database file`. Fixed with a single
> `_ensure_db()` helper. Any new SQLite-backed store needs the same treatment.

### 5.5 Dependency pins

| Rule | Level |
|:--|:--|
| Pin when there is a stated compatibility reason | **RECOMMENDED** |
| Use `>=` when the pin was a floor, not a tested ceiling | **RECOMMENDED** |
| State the reason inline when pinning | **RECOMMENDED** — *reviewer check, no gate* |

Example: `idna>=3.18` (httpx2 requires ≥3.18) — an exact `==3.18` pin was
unjustified and forced needless conflicts for downstream users.

---

## 6. Verification standards

### 6.1 The core principle

**A local verification proves nothing about a release.** The machine that runs
release gates accumulates state CI will never have. Every claim in a tag message
must come from a gate run on a clean checkout.

### 6.2 Required release gates

| Gate | Level |
|:--|:--|
| `make temple-grade require_clean=1 HUB_IMPORT_MODE=pristine` | **CI-REQUIRED** |
| Fresh clone of the cut | **CI-REQUIRED** |
| `make bootstrap` exits 0 (`Makefile:106`) | **CI-REQUIRED** |
| `check-engine` passes | **CI-REQUIRED** |
| `temple-grade` exits 0 | **CI-REQUIRED** |
| `temple-grade` returns 53/53 | **RECOMMENDED expectation** — see note |
| M23 gate reports no new soft-failure patterns (`scripts/m23_gate.py`) | **CI-REQUIRED** |
| Zero live-state mutation after gates (D-623) | **CI-REQUIRED** |
| All five isolation rulings verified **on the tag tree itself** | **CI-REQUIRED** |
| Install-from-artifact smoke test in a clean venv outside the repo | **CI-REQUIRED** |

> **The 53/53 count is an expectation, not a gate.** `Makefile:521-525` states the
> subset size is "a DOCUMENTED expectation of the subset's size, **not** a hard
> gate: the subset is specified by PATHS below, so the count moves as tests are
> added." Pinning the number as a pass criterion would contradict `Makefile` and
> would break every time a test is legitimately added. Record the observed count
> in the tag message; do not fail on it.

> **"Five isolation rulings"** — defined here because it is used in §6.2 and
> §10.2 without definition: `docs/federation/`, `src/omega_youtube_research/`,
> `config/wads/arcana_novai/`, `data/entities/sophia/`,
> `data/entities/makali_fusion/` — each must be absent from the tag tree, along
> with internal `data/` paths.

### 6.3 Clean-environment discipline

| Rule | Level |
|:--|:--|
| Clone or verify outside any working checkout | **CI-REQUIRED** |
| **Check disk space before long test runs** | **RECOMMENDED** |
| Pin test-count expectations as expectations, never as pass criteria | **RECOMMENDED** |
| Artifacts verified in `/tmp` or a fresh worktree, never in-place | **CI-REQUIRED** |

> **Observed failure:** `/tmp` exhaustion produced
> `sqlite3.OperationalError: database or disk is full` and a pip exit-1 that both
> presented as code defects. Twice. Root cause was ~5 GB of accumulated
> verification clones and venvs, not the code under test. **Distinguish an
> environment failure from a code failure before changing code.**

> A local run is also misleading in the opposite direction: this machine carries
> ~2.5 GB of gitignored harvest state under `data/coordination/` that makes a
> test exceed its timeout locally while passing instantly in CI, where the path
> does not exist.

### 6.4 Claim discipline (M29)

| Rule | Level |
|:--|:--|
| Claims about remote/installed behavior require evidence from the artifact | **CI-REQUIRED** |
| Unverifiable claims are labeled `UNTESTED` or `UNTESTABLE` | **CI-REQUIRED** |
| Dated counts cite their source and commit | **CI-REQUIRED** |
| Never mark something green because it is expected to be green | **CI-REQUIRED** |

> A tag message is a permanent public claim. Every line in it should be a number
> that was measured on that exact tree.

### 6.5 Determinism: a result must not depend on what else ran

> **This section exists because of a live defect, not a hypothetical.**

Two `ci.yml` matrix legs run **identical steps on the same commit**. They
disagreed: 3.12 `success`, 3.13 `failure`. The cause was
`tests/test_search_tools.py::test_cache_growth`, which asserted that the
ambient, gitignored `.firecrawl/` directory existed. That directory is only ever
created as a **side effect** of some other test exercising the cache, so under
`pytest-randomly` the verdict depended on ordering. Same code, same commit,
different seed, opposite answers — and nothing in the output said "flake".

| Rule | Level |
|:--|:--|
| CI runs pytest with `-p no:randomly` (matches `Makefile:547,566,780`) | **CI-REQUIRED** |
| A test must not assert on gitignored or untracked filesystem state | **RECOMMENDED** — see G26 |
| A test that needs a directory must create it (`tmp_path`), not assume it | **RECOMMENDED** |
| Two matrix legs must never disagree on the same commit | **CI-REQUIRED** by discipline |

The repo already wrote this principle down — *"with xdist the visible subset
varies per run, so a red result could not be told apart from a flake, and 'flaky'
would become a verdict rather than a diagnosis"* (`Makefile:526-531`) — and then
did not apply it to the full CI suite. The rule was right; the coverage was not.

### 6.6 No gate may fail invisibly

A workflow triggered only by `cron`/`workflow_dispatch` never runs when code
changes, so its failures stay unseen until a human happens to look.

Two were, on this repo, for months:

| Workflow | Invisible failure |
|:--|:--|
| `sote.yml` | `pip install -r requirements.txt` — this repo has never had a requirements file. Red **every week** since creation. |
| `codex-refresh.yml` | A missing `fi` in its shell block — `syntax error: unexpected end of file`. Red **every day** since creation. |

| Rule | Level |
|:--|:--|
| Every workflow triggers on push/PR, **or** is declared scheduled-only with a stated reason | **CI-REQUIRED** — `make check-workflow-triggers` |
| Declared scheduled-only workflows list their accepted risk | **CI-REQUIRED** |

Enforced by `scripts/check_workflow_trigger_coverage.py`, wired into `temple-grade`.
It is a *structural* check: it cannot tell you a scheduled run is red today, only
that a workflow is **capable** of being red unseen. That residual risk is declared
in the allowlist, not hidden.

---

## 7. CI and workflow standards

### 7.1 Current workflow surface

| Workflow | Triggers | Purpose |
|:--|:--|:--|
| `ci.yml` | `main`, `release/initial-v1` | pytest, flake8, mandates, temple-grade, REUSE, docs |
| `test.yml` | `main`, `develop` | import verify, pytest, sovereignty gate, heritage-vet |
| `secrets.yml` | `main`, `release/debut`, … | gitleaks + truffleHog + C3 |
| `secret-scan.yml` | `main`, `release/initial-v1`, `release/debut` | same trio |
| `allowlist-check.yml` | `release/debut`, tags | cut enforcement |
| `allowlist-lint.yml` | PR + `main`, `release/debut` | allowlist structure |
| `reuse-compliance.yml` | `main`, `release/initial-v1`, `release/debut` | REUSE v3.3 |
| `release.yml` | tag `v*.*.*` | publish artifacts |
| `codex-refresh.yml` | cron + dispatch | CODEX staleness refresh |

### 7.2 Rules

| Rule | Level |
|:--|:--|
| Use `python -m venv .venv`; never `--break-system-packages` (M24) | **CI-REQUIRED** |
| `fail-fast: false` on matrix jobs | **CI-REQUIRED** |
| Secret scanning fails closed on scan steps: no `|| true` | **CI-REQUIRED** for the steps that run — *but see fail-open note* |
| NUL-delimited file passing (`git ls-files -z`) | **CI-REQUIRED** |
| Planted-fixture test proves the scanner can fail | **RECOMMENDED** |
| Publish a required-check matrix per branch | **RECOMMENDED** — *not yet published* |

> **Fail-open path (R10).** `secrets.yml` gates `trufflehog-check` behind
> `if: github.event_name == 'pull_request'` (`secrets.yml:92`), and its summary at
> `:155` accepts `skipped` as a pass. On a **push** — including pushes to
> `release/debut` and tag pushes — truffleHog does not run at all and the job is
> still green. The `|| true` removals at `:52,135` are genuine fail-closed
> hardening, but they do not close this. Verified-only scanning is a second,
> quieter fail-open: it silently drops findings it cannot confirm.

### 7.2.1 Pre-commit is a real enforcement tier

`.pre-commit-config.yaml` is not a convenience — it carries a large share of
mandate enforcement and runs **before** CI ever sees a push: M1 AnyIO, M8 zero
telemetry, M9 error integrity, M23 failure integrity, F821, tracking-state, C3,
M35, gitleaks, trufflehog, REUSE (full on pre-push, per-file on commit), and
`temple-grade` on pre-push. A rule that exists only in pre-commit is
**CI-REQUIRED** for the author and unenforced for anyone who pushes without hooks.
Do not treat pre-commit-only rules as satisfied in CI.

### 7.3 Duplication

> **Gap (G4/G5).** `secrets.yml` and `secret-scan.yml` run the same
> gitleaks+truffleHog+C3 trio on overlapping branches; `ci.yml` and `test.yml`
> both run pytest, flake8, venv setup, and mandate checks with differing flags.
> These have already drifted once (a NUL-delimit fix and `|| true` removals
> landed in one file only). Consolidate to one canonical pipeline per concern,
> or designate canonical vs mirror **with a drift test**.

### 7.4 Required status checks are incompatible with a direct-push workflow

> **Measured, not assumed. Tested on a throwaway branch — it rejected the push.**

This repo merges by **pushing directly to `main`**. Required status checks cannot
be enabled on top of that. With classic branch protection a direct push is
rejected outright:

```
remote: error: GH006: Protected branch update failed
remote: - 2 of 2 required status checks are expected.
 ! [remote rejected]   HEAD -> main (protected branch hook declined)
```

Rulesets are not an escape. GitHub's documentation for the ruleset
`required_status_checks` rule states:

> "Choose which status checks must pass before the ref is updated. When enabled,
> **commits must first be pushed to another ref where the checks pass**."

Both mechanisms therefore require commits to land elsewhere, pass there, and only
then update `main`. The constraint is architectural, not a settings detail — no
amount of payload fiddling changes it.

| Rule | Level |
|:--|:--|
| Do not enable required status checks while this repo pushes directly to `main` | **CI-REQUIRED** by architecture |
| Never use a `bypass_actors` entry to force an incompatible gate on | **CI-REQUIRED** |

> **Why no bypass shortcut.** A ruleset with `bypass_mode: always` for the admin
> *does* admit direct pushes — and the protection then constrains nobody, because
> the only possible actor is exempt. Same mistake already rejected for the tag
> ruleset (§9.3). If a gate can only be satisfied by bypassing it, it is not a gate.

**Enforcement actually in place instead** (deliberate, per §1.4):

| Control | Where |
|:--|:--|
| CI runs every gate on every push and reports red | `ci.yml`, `test.yml` |
| `temple-grade` + M23 run locally on **pre-push** | `.pre-commit-config.yaml` |
| Release gated end-to-end incl. artifact verification | `.github/workflows/release.yml` |
| A published tag cannot be moved or deleted | §9.3 ruleset + immutable releases |

**Revisit when** external contributors start pushing, or when red lands on `main`
often enough to matter. The migration is a workflow change, not a settings change.

### 7.5 Path to merge-gating (when the time comes)

Safe order for a **solo** maintainer:

1. Adopt a PR workflow — push to a topic branch, open a PR, merge it.
2. Add a ruleset requiring a pull request, but **not** requiring approvals.
   Per GitHub: *"The pull request doesn't necessarily have to be approved, but it
   must be opened."* Requiring **reviews** deadlocks a one-person repo; requiring a
   **PR** does not.
3. Only then add `required_status_checks`, limited to checks that always run and
   never skip — never `allowlist-lint.yml`, which is path-filtered.

Never start at step 3. That ordering is the mistake this section documents.

### 7.6 Secrets: gating posture

Gate on **verified** findings; track `unverified`/`unknown` separately rather
than discarding them. TruffleHog exits **183** on findings — distinct from exit 1
on error, and the distinction matters for triage. Enforce fail-on-scan-errors.

> **Caution:** verified-only scanning suppresses valid-but-unverifiable secrets
> (offline keys, deleted accounts, rate-limited APIs). Scanning verified-only as
> the *sole* signal produces false-clean results. Use it as the blocking gate and
> keep unverified visible.

### 7.7 Waivers

A broken gate that is reported and waived **in writing** is governance. A broken
gate that silently ships is a soft failure (M23).

| Rule | Level |
|:--|:--|
| A waiver names the gate, scope, measured counts, reason, and an expiry date | **RECOMMENDED** — *no gate (G21)* |
| A waiver states "documents the exception; does not resolve it" | **RECOMMENDED** |
| An expired waiver blocks the next cut | **RECOMMENDED** — *no gate (G21)* |

> The REUSE waiver (`docs/operations/REUSE_WAIVER_DEBUT_20261003.md`) expires at
> the next cut or 2027-01-01. It is a good model: measured counts, stated reason,
> explicit expiry. It is also a **clock** — see §11.

---

## 8. Documentation standards

| Rule | Level |
|:--|:--|
| The documented install path is the **verified** install path | **RECOMMENDED** — *no gate* |
| Marketing claims map to a source file and are reviewable | **RECOMMENDED** |
| Comparison tables with named competitors are avoided unless independently sourced | **RECOMMENDED** — *project convention from the README review cycle, not an external norm* |
| Ops docs: live source wins; counts are dated and cited | **RECOMMENDED** |
| Annotate, do not silently rewrite historical records (M28) | **RECOMMENDED** |
| Unknown facts are labeled `UNVERIFIED`, never guessed | **RECOMMENDED** |

**Documented install paths are claims.** The README documented
`git clone && ./scripts/install.sh` (verified) while `pyproject.toml` implied a
wheel path that was broken. The README was right and the wheel was wrong; the gap
was only visible because the wheel path was actually tested.

> **Gap (G12):** M26 states reference docs must pass `doc-llm-validate`, but the
> implementation gates only `docs/sprints/current/`. Either widen the gate or
> narrow the mandate wording. As written, M26 is not enforceable.

---

## 9. Roles and approvals

| Role | Authority |
|:--|:--|
| **Author** | Proposes changes; attests to testing and documentation |
| **Maintainer reviewer** | Approves merge; ≥1 required |
| **Release cutter** | Builds the cut; runs §3 and §6 gates |
| **Release approver** | Authorizes the tag; must not be the sole author of the change |
| **Architect** | Sole authority for public-surface expansion (FORGE→ALLOW), boundary calls, IP-sensitive decisions |

| Rule | Level |
|:--|:--|
| FORGE→ALLOW expansion requires Architect sign-off with a decision ID | **CI-REQUIRED** by process |
| Tag creation requires a named release approver | **RECOMMENDED** |
| Required-review count enforced by branch protection | **CI-REQUIRED** — *not configured* |

> **Gap (G15):** `main` is protected (§9.1) but enforces **no review requirement**,
> so "≥1 maintainer review" remains an honor system. That is the correct posture
> for a one-person repo: a required-review gate would deadlock it. Required status
> checks are likewise declined by architecture (§7.4), not by omission.

### 9.1 Branch protection — as actually enabled (2026-10-12)

Enabled on `main` via the GitHub API and **empirically verified**, not assumed:

| Control | State | How verified |
|:--|:--|:--|
| Force-push blocked | ✅ `allow_force_pushes: false` | Real rewind push → `GH006: Cannot force-push to this branch` |
| Branch deletion blocked | ✅ `allow_deletions: false` | Real delete push → `Cannot delete this branch` |
| Admins bound by the above | ✅ `enforce_admins: true` | Same probe run as the admin (sole collaborator) |
| Unresolved conversations block merge | ✅ enabled | API state |
| Normal fast-forward push | ✅ still works | Real push `b2451e9d..5a4c263a` succeeded |
| Required pull-request reviews | ❌ **not enabled** | Would deadlock a solo maintainer |
| Required status checks | ❌ **not enabled** | Two checks are red on `main` (below) |
| Immutable releases | ❌ **unavailable** | API returns 404; not enabled for this account |

**Do not enable force-push protection on `release/debut`.** That branch is
force-pushed on every cut by design (`--force-with-lease`). Protecting it would
break the release process. Only `main` is protected.

### 9.2 Known red checks on `main` — RESOLVED (2026-10-12)

Both were red when D5 began. Both are now green; the record is kept because the
*reason* one of them went unnoticed is the lesson.

| Check | Failure | Cause | Status |
|:--|:--|:--|:--|
| `test-and-lint (3.12)/(3.13)` | `.firecrawl/ cache directory missing` | An order-dependent test asserting on gitignored state | ✅ CLOSED (§6.5) |
| `SOTE Mechanical Pipeline` | `No such file: requirements.txt` | Stale workflow; deps live in `pyproject.toml` | ✅ CLOSED (§6.6) |

Both legs of the `test-and-lint` matrix now agree, and they agree because
determinism is pinned (`-p no:randomly`) rather than by luck.

### 9.3 Tag immutability — ruleset + immutable releases (enabled 2026-10-12)

Two independent controls, **both verified by real rejected pushes**:

| Control | State | Verification |
|:--|:--|:--|
| **Immutable releases** | ✅ `enabled: true` | `GET /repos/{owner}/{repo}/immutable-releases` |
| **Tag ruleset** `protect-release-tags` | ✅ active, `refs/tags/v*` | force-move → *push declined due to repository rule violations* |
| Tag deletion blocked | ✅ | delete → *push declined* |
| **No bypass actors** | ✅ `bypass_actors: []` | admin force-move rejected with no bypass |

> **Correction (was wrong, now fixed).** An earlier revision of this document
> recorded immutable releases as *unavailable (API 404)*. That was a **typo in the
> endpoint path** — `immutable_releases` (underscore) instead of
> `immutable-releases` (hyphen). The feature is GA (2025-10-28) and works on this
> repo. The 404 was mine, not GitHub's. Do not accept a 404 from a path you have
> not cross-checked against the documented endpoint.

**Rulesets, not classic protection, for tags.** Classic branch protection has no
tag target at all. Rulesets layer alongside it — all applicable rules are
enforced — so the §9.1 branch protection remains in place and is not wasted.

Rules use `{"type": "<rule>"}` objects, **not** bare keys:
```json
"rules": [ { "type": "deletion" }, { "type": "update" } ]
```

**Recovery path** (deliberate, logged, reversible — required if a tag is ever
wrong): set the ruleset `enforcement: disabled` → delete/move the tag → restore
`enforcement: active`. Verified end-to-end during setup.

**Why no bypass actor.** A bypass actor gives an admin an escape hatch, but the
maintainer is also the person most likely to move a tag by accident. During setup
the first ruleset *did* grant admin `bypass_mode: always` and a test force-move
succeeded. Protection that the only possible actor can trivially bypass is
protection against nobody. Bypass is a multi-maintainer tool; a solo repo should
use the disable/re-enable recovery path instead.

---

## 10. Checklists

### 10.1 Pull request

- [ ] Conventional Commits; branch named per §2.1
- [ ] All PR template sections completed
- [ ] Mandate checklist current (**after G1 is fixed**)
- [ ] `make temple-grade` green locally (**not** "decorative" — see G2)
- [ ] New tests added for behavior changes
- [ ] Docs and CHANGELOG updated if user-facing
- [ ] No secrets, no `--break-system-packages`, no `import asyncio` in `src/omega/`
- [ ] AI disclosure present if applicable

### 10.2 Public cut

- [ ] `bash scripts/apply_public_allowlist.sh --strict` dry-run reviewed
- [ ] Working tree clean before `--confirm`
- [ ] Cut produced from a **green** `main`
- [ ] Removed-file count = 0 on the cut
- [ ] All five isolation rulings verified on the cut tree
- [ ] Harvester present (`scripts/hivemind_harvest.py` + test), per D-626
- [ ] No `keys/`, no `*.local.yaml`, no arcana_novai, no internal `data/`
- [ ] Any FORGE→ALLOW change carries Architect decision ID

### 10.3 Release and tag

- [ ] Fresh clone of the cut; bootstrap + check-engine + temple-grade + M23 green
- [ ] Zero live-state mutation after gates (D-623)
- [ ] `git fetch origin --prune` before tagging
- [ ] Tag created with `-a` on an **explicit SHA**
- [ ] `git rev-parse <tag>^{commit}` equals the cut head — **before push**
- [ ] Tag pushed; peel re-verified via `git ls-remote` — **after push**
- [ ] CHANGELOG section exists and is non-empty
- [ ] Version agreement: tag ↔ `pyproject.toml` ↔ CHANGELOG
- [ ] Clean build: `rm -rf build/ dist/ src/*.egg-info` first
- [ ] Wheel contents inspected against the packaging allowlist
- [ ] Install-from-artifact smoke test in a clean venv, outside the repo
- [ ] Every claim in the tag message was measured on this tree
- [ ] Existing releases for the tag cleaned up before publishing

### 10.4 Packaging

- [ ] `package-data` lists files explicitly; no directory copies
- [ ] Packaged configs are verbatim copies of already-public files
- [ ] No host-local paths, credentials, or absolute machine paths
- [ ] All startup-read config files enumerated and present in the artifact
- [ ] Config paths resolve through `CONFIG_DIR`
- [ ] Optional configs degrade gracefully when absent
- [ ] Fresh-install state init verified against an empty data dir
- [ ] Dependency pins carry a stated reason

### 10.5 Documentation

- [ ] Documented install path matches a verified path
- [ ] Claims mapped to source files
- [ ] Counts dated and cited
- [ ] M26 scope resolved (**after G12**)
- [ ] Waivers carry expiry dates

---

## 11. Open decisions and gap register

Each entry is a rule in this document that **should** be enforced but is not, or
a known conflict. The Status column distinguishes live gaps from closed ones.

| ID | Gap | Risk | Owner | Status |
|:--|:--|:--|:--|:--|
| G1 | PR-template mandate list omits M14/M28/M29/M30 | Contributors attest to the wrong law set | @verity | OPEN |
| G2 | `CONTRIBUTING.md` calls `temple-grade` decorative | Release gate skipped locally; red arrives late | @maat | OPEN |
| G3 | CLA/DCO declared in `CONTRIBUTING.md` with no bot/app | Unenforced legal claim | @verity | OPEN |
| G4 | Duplicate secret-scan workflows | Drift; patched in one file only | @verity | OPEN |
| G5 | Duplicate Python CI workflows (`ci.yml` / `test.yml`) | Drift in flags and ordering | @maat | OPEN |
| G6 | REUSE RED on `main`; waiver expires next cut or 2027-01-01 | Next release blocked or needs a second waiver | @maat | OPEN |
| G7 | No tag-immutability gate | Moved-tag class recurs | @makali | **CLOSED** (§9.3 ruleset + immutable releases) |
| G8 | Changelog empty-notes fallback permitted | Release ships without notes | @makali | OPEN |
| G9 | No version-vs-tag-vs-CHANGELOG consistency check | Version drift | @makali | OPEN |
| G10 | No wheel-content / packaging-drift gate | Future packager broadens `package-data` | @makali | OPEN |
| G11 | No clean-clone artifact verification standard | Corrupt artifact ships as "verified" | @makali | OPEN |
| G12 | M26 scope mismatch (`doc-llm-validate` scope) | M26 unenforceable as written | @scribe | OPEN |
| G13 | D-628: 13 `[CUT-]` entries parsed as KEEP | Sensitive-adjacent files ship | **Architect** | OPEN |
| G14 | Glob-translator quirks pinned by fuzz parity | A "fix" silently rewrites the boundary | @maat | OPEN |
| G15 | `main` not branch-protected; no required reviews | Unenforced approvals | **Architect** | **PARTIAL** — force-push/deletion/conversation locked (§9.1); reviews deferred (solo); required status checks **declined by architecture**, see §7.4 |
| G16 | Unified checklists | — | — | **CLOSED** (§10) |
| G23 | ~~Immutable releases unavailable~~ — **RESOLVED (2026-10-12):** the earlier 404 was a typo'd endpoint (`immutable_releases`). Immutable releases **enabled**; tag ruleset `protect-release-tags` active on `refs/tags/v*` with no bypass actors (§9.3) | — | — | **CLOSED** |
| G17 | `scripts/check_mandate_compliance.py` enumerates M1…M27 of 30 | M28/M29/M30 unchecked | @verity | OPEN |
| G18 | `SOVEREIGN_MANDATES.md` §28/29/30 inline tags disagree with section numbers (violates D-609) | Citations resolve to the wrong law | @verity | OPEN |
| G19 | No commit-lint; no PR-template completeness gate; branch-target conflict between `CONTRIBUTING.md` and workflows | Contributors guess the process | @maat | OPEN |
| G20 | No automated config-path sweep; startup-read config not enumerated | Wheel ships without a config it needs | @makali | OPEN |
| G21 | No waiver-expiry enforcement; waivers are human-enforced only | Expired waiver silently persists | @verity | OPEN |
| G22 | TruffleHog is PR-only (`secrets.yml:92`); push events run without it | Fail-open secret path on push | @verity | OPEN |
| G24 | ~~Two checks red on `main`~~ — **RESOLVED (2026-10-12):** `test-and-lint` order-dependence fixed; `sote.yml` install fixed | — | — | **CLOSED** (§6.5) |
| G25 | No guard against workflows that can only fail invisibly | A red scheduled workflow goes unseen indefinitely | @makali | **CLOSED** (§6.6) |
| G26 | Tests may assert on gitignored/untracked runtime state | Verdict depends on test ordering; flakiness mistaken for a result | @verity | OPEN (guard would be noisy; see §6.5) |
| G27 | `sote.yml` / `codex-refresh.yml` push directly to `main` with `contents: write` | Breaks when required PRs/checks are enabled | @makali | OPEN |

### 11.1 Decisions requiring the Architect

| # | Decision |
|:--|:--|
| D1 | D-628 boundary disposition — who rules on the 13 mis-parsed entries, and by when |
| D2 | M26 scope — widen `doc-llm-validate` or narrow the mandate |
| D3 | Whether `temple-grade` absorbs secrets + REUSE, or they stay separate with explicit waivers |
| D4 | REUSE backfill owner, sprint, and done-date before waiver expiry |
| D5 | ~~Enable GitHub branch protection (required reviews + required checks) and immutable releases~~ — **DONE (2026-10-12):** `main` protected (force-push, deletion, admins, conversations) and verified by real rejected pushes (§9.1). **Immutable releases enabled + tag ruleset active, no bypass actors (§9.3).** Required reviews deferred (solo maintainer); required status checks deferred pending G24. |
| D6 | LAN posture — rebind tailnet services to loopback, or record reviewed justification per bind |
| D7 | Public `main` history posture (deferred by standing decision §1.4) |
| D8 | ~~Required status checks on `main`~~ — **DECLINED (2026-10-12), by architecture, not oversight.** Direct-push workflow is incompatible with both classic protection and rulesets; commits must land on another ref first and pass there. Enforcement relocated to CI reporting + pre-push `temple-grade` + release gating + tag immutability. Migration path and trigger conditions in §7.4–7.5. |
| D9 | Review trigger: adopt a PR workflow when external contributors push, or when red lands on `main` more than ~1×/month |

### 11.2 Implementation order

1. **Correct the docs that lie:** G1, G2. Cheap, and they currently mislead contributors.
2. **Close the release-loop gaps:** G7, G8, G9, G11. These govern the next release.
3. **Close the packaging gap:** G10, plus the full config-path sweep that §5.3 requires.
4. **Resolve boundary decisions:** D1 (Architect), then G13.
5. **Enforce governance:** D5 branch protection, then G15 roles.
6. **Consolidate CI:** G4, G5 with drift tests.
7. **Clear the waiver clock:** G6 REUSE backfill before expiry.

---

## 12. Sources

**External baseline** (normative weight derives from the repo, not these):

- SemVer 2.0.0 — https://semver.org/ — prerelease shape; released contents MUST NOT change
- `git-tag(1)` — https://git-scm.com/docs/git-tag — annotated vs lightweight; re-tagging is recovery, not a norm
- Conventional Commits 1.0.0 — https://www.conventionalcommits.org/en/v1.0.0/
- GitHub branch protection — https://docs.github.com/articles/enabling-required-reviews-for-pull-requests *(verified URL; redirects to "Managing a branch protection rule")*
- GitHub provenance & integrity — https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity — immutable releases, SBOM
- Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/
- `python -m build` — https://pypi.org/project/build — isolated builds
- REUSE Specification v3.3 — https://reuse.software/spec-3.3
- setuptools data files — https://setuptools.pypa.io/en/latest/userguide/datafiles.html
- setuptools #3260 (exclude-package-data vs include_package_data) — https://github.com/pypa/setuptools/issues/3260 — supports §5.1
- setuptools #4198 (stale egg-info / build dir) — https://github.com/pypa/setuptools/issues/4198 — supports §5.2
- TruffleHog — https://github.com/trufflesecurity/trufflehog — `--results` taxonomy, exit 183, canary detection

**Repo sources:** `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`,
`.github/workflows/*`, `docs/strategy/PUBLIC_ALLOWLIST.txt`,
`scripts/apply_public_allowlist.sh`, `REUSE.toml`,
`docs/operations/REUSE_WAIVER_DEBUT_20261003.md`, `SOVEREIGN_MANDATES.md`,
`Makefile`, `pyproject.toml`.

---

*Draft prepared for Jem review in session `ses_ecf3a559bffeeLumC3BCt3p30a`, then
Architect ratification. Every §11 gap is stated as an open gap rather than an
unenforced requirement.*

*⬡ OMEGA ⬡ MAKALI ⬡ RELEASE_PR_PUBLIC_STANDARDS ⬡ DRAFT-v0.1 ⬡ 2026-10-12 ⬡*
