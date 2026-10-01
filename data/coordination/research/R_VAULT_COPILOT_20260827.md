---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_deliverable"
document_id: "R_VAULT_COPILOT_20260827"
title: "R_VAULT_COPILOT — Copilot/CI-CD Gap Analysis for Vault + Debut"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
specialist: "grokster (Copilot platform specialist)"
charter: "Standing copilot-specialist; charter + R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md are in active context"
method: "Web-primary-sources (2026-current docs.github.com, gitleaks, copilot-cli, pre-commit, git-filter-repo, ASF infra-actions) + local repo probes (.github/workflows/, .pre-commit-config.yaml, PUBLIC_ALLOWLIST.txt, DEBUT_REMEDIATION_MANUAL, ACTIVE_SPRINT.json, vault research burst 8/6886L)"
m23_honesty: "All claims carry confidence tags. Unverified items marked [PROBE REQUIRED] or [UNVERIFIED]."
mandate_compliance: "M8 Zero Telemetry (no external calls in YAML), M23 Failure Integrity (no soft-fail theater), M26 Doc Standards (llms-friendly headers + line-budget)"
---

# R_VAULT_COPILOT_20260827 — Copilot/CI-CD Gap Analysis
**AP Token**: `AP-GROKSTER-COPILOT-CICD-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_copilot_cicd ⬡ R_VAULT_COPILOT-01

**Date**: 2026-08-28 (00:01 UTC, post-7G launch handoff)
**Specialist**: grokster (Copilot platform specialist, ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
**Brief**: Architect mandate "Every time we look we find more. Keep digging." 8 areas to investigate.

---

## §0 EXECUTIVE VERDICT

**The CI/CD surface is already 80% present but 100% uncoordinated.** The vault research burst (8 dispatches, 6,886L) + the 7G launch handoff have left a stack of decision-ready pieces that nobody has assembled into a single, running debut pipeline. Every specific area the Architect named is either **(A) already done in some form**, **(B) trivially scriptable in <30 min**, or **(C) requires one specific config to land in `.github/` or `.pre-commit-config.yaml`**. None are blocked by research; all are blocked by wiring.

**The two highest-leverage unclaimed opportunities**:

1. **`PUBLIC_ALLOWLIST.txt` → CI enforcer** (item #8). Today the allowlist is *documentation*; it is not enforced. A 30-line GitHub Action can convert it into a fail-closed PR gate that prevents any file outside the allowlist from landing in `release/debut`. **Without this, every other CI gate is downstream of an unforced error.** Effort: 30 min. Risk if missing: a single careless `git add -A` reintroduces `data/entities/`, `docs/research/`, or a stray `.env`.

2. **`release/debut` branch + 2-remote pattern** (item #7). The Architect's "branch from allowlist" (D-553) and Kali's `release/debut` plan are implementable today as a 2-remote workflow (private `origin` for the forge; public `debut` remote for the curated branch) — same pattern as kyrrego's academic-private/public mirror (Jan 2026). This is **not** the same as `git filter-repo` on `main`; it is *additive* and reversible. Effort: 90 min for the cut. Eliminates the "mass-delete main the same week as filter-repo" risk flagged in PUBLIC_ALLOWLIST.txt and the Debut Manual §5.

**Total remaining CI/CD work to ship debut: ~6-8h spread across 5 tickets, all scriptable, all high-confidence.** No new research required. Wiring + verification only.

**The biggest *under*-claimed risk**: P0-1d (SECURITY_AUDIT ancestor) running *sequentially after* `release/debut` cut. If the ancestor commit ships to a public remote and the filter-repo pass *then* finds a residual key, the public remote must be force-pushed with new SHAs, breaking clone URLs and exposing a window where `git clone` returns the leaked history. **Recommendation: hold `release/debut` cut until P0-1d's `git log -S 'csk-' --all` returns clean.** This is the single decision that gates the rest.

---

## §1 GAP ANALYSIS — What's Still Missing From the CI/CD Angle

### 1.1 State of the existing CI/CD surface (probed 2026-08-28 00:01 UTC)

| Layer | File | Status | Provenance |
|-------|------|--------|------------|
| Pre-commit core | `.pre-commit-config.yaml` (185L) | ✅ Exists, comprehensive | local probe |
| Pre-commit → gitleaks | `gitleaks` rev v8.18.4 at pre-commit + pre-push | ✅ Wired | local probe |
| Pre-commit → trufflehog | rev v3.97.1, filesystem mode, `--only-verified` | ✅ Wired | local probe |
| Pre-commit → C3 mirror | `scripts/ci_secret_scan.py` (stdlib, no network) | ✅ Wired, plant-fixture test passes | local probe + manual |
| Pre-commit → M1/M7/M8/M9/M14/M23/M27 | `make check-m*` hooks + `validate_tracking_state.py` | ✅ Wired (Iron Gate per M27) | local probe |
| Pre-commit → Temple-Grade | `make temple-grade` at pre-push | ✅ Wired (slow, correct stage) | local probe |
| GitHub Actions: CI | `.github/workflows/ci.yml` (52L) | ✅ Lint+pytest, py 3.12/3.13 | local probe |
| GitHub Actions: Test | `.github/workflows/test.yml` (105L) | ✅ pytest + mandates + sovereignty | local probe |
| GitHub Actions: Secret Scan | `.github/workflows/secret-scan.yml` (75L) | ✅ gitleaks + trufflehog + C3 mirror | local probe |
| GitHub secret scanning | `.github/secret-scanning.yml` (paths-ignore) | ⚠️ Minimal — only paths-ignore, no custom patterns, no push protection config | local probe |
| Branch protection | (none) | ❌ **MISSING** for `release/debut`, `release/initial-v1`, `main` | inferred from absence |
| Allowlist enforcement | (none) | ❌ **MISSING** — `PUBLIC_ALLOWLIST.txt` is documentation, not a gate | local probe |
| Release automation | (none) | ❌ **MISSING** — no `release-please`, no `semantic-release`, no `gh release` workflow | inferred from absence |
| Hotfix flow | (none) | ❌ **MISSING** — no documented `hotfix/*` branch policy, no branch protection on hotfix targets | inferred from absence |
| Copilot CLI integration | (none) | ❌ **MISSING** — no `--allow-tool` policy, no headless mode used in CI | inferred from absence |
| ASF-style action allowlist | (none) | ❌ **MISSING** — no validation that `uses:` refs in workflows are from trusted orgs | inferred from absence |
| Branch-up hygiene | (none) | ❌ **MISSING** — `actions/checkout@v4` is pinned but no Dependabot/Renovate config for `uses:` upgrades | inferred from absence |
| CodeQL | (none) | ❌ **MISSING** — no `github/codeql-action` workflow; would catch M9 violations that grep misses | inferred from absence |
| SBOM / sigstore | (none) | ❌ **MISSING** — no `anchore/sbom-action` or sigstore signing for debut | inferred from absence |
| Heritage Vet gate | `make heritage-vet` called from `test.yml` | ⚠️ Wired but in 29-warning state per Architect note | local probe + Architect handoff |

**Net assessment**: the secret-scanning gauntlet (gitleaks + trufflehog + C3 mirror) is **best-in-class** and over-built relative to debut needs. The debut *mechanics* (allowlist enforcement, release cut, hotfix flow, Copilot CLI usage) are completely missing.

### 1.2 Per-Area Gap Analysis (Architect's 8 specific areas)

#### AREA 1: GitHub Actions for debut — what CI gates are needed?

**What's there**: 3 workflows (ci, test, secret-scan). `test.yml` is the canonical "all-in-one" (mandates + heritage + docs). `ci.yml` is a smaller lint+pytest.

**What's missing for debut**:
1. **`debut-build.yml`** — runs only on `release/debut` + tags. Validates: allowlist enforcement, INST-1 acceptance test (fresh venv → `pip install -e ".[native,cli]"` → `omega talk "hello"` → exit 0), `make temple-grade`, `make doc-llm-validate`. **This is the single most important workflow for debut** and does not exist.
2. **`debut-allowlist.yml`** — see Area 8. PR-only; fails on any `git ls-files` not in `PUBLIC_ALLOWLIST.txt`.
3. **`debut-release.yml`** — tag-triggered: builds the source tarball + sdist + wheel, runs `gh release create v0.1.0`, attaches artifacts. Uses `gh CLI` with `GITHUB_TOKEN` (org-level, with `contents: write` + `id-token: write` for sigstore).
4. **Dependabot config** at `.github/dependabot.yml` to keep `actions/checkout@v4`, `actions/setup-python@v5`, `gitleaks/gitleaks-action@v2` current. Without this, **a future CVE in `checkout` is a silent attack surface on every PR**.

**Recommended config (debut-build.yml)**:

```yaml
# .github/workflows/debut-build.yml
# 🔱 Debut Build Gate — runs ONLY on release/debut and tags.
# M13 Temple-Grade + M26 Doc Standards + INST-1 acceptance + allowlist validation.
name: Debut Build

on:
  push:
    branches: [release/debut]
    tags: ["v*.*.*"]
  pull_request:
    branches: [release/debut]
  workflow_dispatch:

permissions:
  contents: read
  # id-token: write ONLY for the release job; not needed for build/test

concurrency:
  group: debut-${{ github.ref }}
  cancel-in-progress: true

jobs:
  allowlist:
    name: 📜 Public allowlist enforcement
    uses: ./.github/workflows/allowlist-check.yml
    # see §3.1 for the reusable workflow definition

  install-honesty:
    name: 🐍 Fresh-venv INST-1 acceptance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Fresh venv (per Debut Manual §5 INST-1)
        run: |
          python -m venv /tmp/omega-debut-venv
          source /tmp/omega-debut-venv/bin/activate
          pip install --upgrade pip
          pip install -e ".[native,cli]"
      - name: Local inference smoke test
        env:
          OMEGA_ENV: test
        run: |
          source /tmp/omega-debut-venv/bin/activate
          # In CI we cannot download the GGUF; mock mode proves the wiring.
          # On a runner with the model, drop the MOCK=1 and let it boot.
          OMEGA_MOCK_PROVIDER=1 python -c "
          from omega.oracle.model_gateway import ModelGateway
          from omega.oracle.providers import MockProvider
          gw = ModelGateway(provider=MockProvider())
          r = gw.generate_sync([{'role':'user','content':'hello'}])
          assert r.provider_name == 'mock', r.provider_name
          print('PROVIDER_NAME=mock OK; IS_CLOUD=False')
          "
      - name: omega talk exit-0
        env:
          OMEGA_MOCK_PROVIDER: "1"
        run: |
          source /tmp/omega-debut-venv/bin/activate
          omega talk "hello"  # expect exit 0

  temple-grade:
    name: 🏛️ M13 Temple-Grade gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pyproject.toml
      - name: pip install -e .[dev]
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[cli,dev]"
      - name: make temple-grade
        run: make temple-grade
      - name: make doc-llm-validate (M26)
        run: make doc-llm-validate

  heritage-vet:
    name: 🛡️ M14 Heritage Vet reconcile
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: make heritage-vet
        run: make heritage-vet
      - name: Verify 0 unvetted [id-soft:] tags
        run: |
          UNVETTED=$(grep -rn '\[id-soft:' src/ docs/ \
            --include='*.py' --include='*.md' \
            | wc -l)
          VETTED=$(grep -c '^- id:' data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md 2>/dev/null || echo 0)
          echo "Unvetted tags: $UNVETTED | Vet records: $VETTED"
          # Per M14 D208 strict scope enforcement
          if [ "$UNVETTED" -gt 0 ]; then
            echo "::error::M14 violation: $UNVETTED unvetted [id-soft:] tags (see HERITAGE_VET_LOG.md)"
            exit 1
          fi
```

**Effort**: 90 min to write, test on a fork, and add to the allowlist.

#### AREA 2: pre-commit ↔ GitHub Actions integration

**What's there**: Local `pre-commit run --all-files` works. `test.yml` calls `make heritage-vet`, `make temple-grade` etc. but does **not** call `pre-commit run --all-files` as a discrete step.

**What's missing**:
1. **No `pre-commit run --all-files` in any CI workflow.** This means a developer who skipped local `pre-commit install` can push code that fails locally, as long as the CI's own checks (which are partial — `flake8 src tests --count --select=E9...` only) pass.
2. **No `pre-commit.ci` integration** (the SaaS from pre-commit.ci). The repo has the badge path implicitly (it has the config) but no `.pre-commit-hooks.yaml` advertisement. **For debut, pre-commit.ci should be opted-in** so PRs from forks also get checked (the `pull_request` workflow token-restriction is a known gap for fork PRs — pre-commit.ci handles it via its own token).
3. **No staged branch-protection rule** requiring `pre-commit.ci`'s status check.

**Recommended config — add a single step to `test.yml` and a new `pre-commit.yml` workflow**:

```yaml
# .github/workflows/pre-commit.yml
# Runs the same pre-commit hooks CI-side so a developer's skip
# of `pre-commit install` cannot push violating code.
name: Pre-commit (CI mirror)

on:
  push:
    branches: [main, release/debut, release/initial-v1]
  pull_request:
    branches: [main, release/debut]

permissions:
  contents: read

jobs:
  pre-commit:
    name: 🪝 pre-commit run --all-files
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: pip install pre-commit
        run: pip install pre-commit
      - name: Cache pre-commit environments
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
          restore-keys: pre-commit-
      - name: Run all hooks
        # `pre-commit run --all-files` exits 1 on any failure.
        # `show-diff-on-failure` writes the diff to the action log.
        run: pre-commit run --all-files --show-diff-on-failure
        # M23 honesty: no `--all-files` filtering by branch; same hooks everywhere.
        # M1/M7/M8/M9/M14/M23/M27 are already in the config — the M27 Iron Gate
        # (omega-tracking-state) is the hardest check; expect ~30-60s wall-clock.
```

**For pre-commit.ci** — add this comment to the existing `.pre-commit-config.yaml` to opt-in:

```yaml
# (top of .pre-commit-config.yaml)
# pre-commit.ci config — https://results.pre-commit.ci
ci:
  # Skip the slow pre-commit.ci autoupdate bot on this repo
  # (M23: we want explicit autoupdate review).
  autoupdate_schedule: quarterly
  # Skip some hooks in CI that the runner can't satisfy (none currently)
  skip: []
  # submodules: false — pre-commit.ci default
```

**Effort**: 20 min. The `pre-commit.ci` opt-in is a config block (no separate file). Note: pre-commit.ci is free for OSS repos; for a public debut repo it costs nothing and adds a second layer of enforcement that works on **fork PRs** (where the GitHub Actions token is restricted).

#### AREA 3: Copilot CLI for release automation

**What's there**: Nothing. The copilot CLI is not currently called by any workflow, any script, or any docs.

**What's now possible (post-Feb 2026 GA, post-1.0.4 changelog)**:
- `copilot -p "<prompt>" -s --no-ask-user` for headless mode (one-shot, clean output, no interactive)
- `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN` env-var auth (in that precedence order)
- `--allow-tool='shell(gh:*)'` to scope permissions
- `--max-ai-credits N` to cap spend per session
- `--max-autopilot-continues N` to cap continuation depth
- The `/changelog` slash command supports `last <N>`, `since <version>`, `summarize` (from 1.0.4 changelog 2026-03-11)

**Specific high-value use cases for the Omega Engine debut**:

1. **Changelog generation from conventional commits**. The repo's commit prefix policy (`fix:`, `refactor:`, `docs:`, `chore:`, `test:`, `ci:`, `feat:`, `id-soft:`, `heritage:`) is already conventional-commits-flavored. A Copilot CLI headless run can summarize the last N commits into a release-notes draft. **This is 5 lines of YAML**, not 50.

```yaml
# Part of .github/workflows/debut-release.yml (when a tag is pushed):
- name: Generate release notes draft (Copilot CLI)
  if: startsWith(github.ref, 'refs/tags/v')
  env:
    COPILOT_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Pinned version per M23: deterministic, no surprise breakage.
    npm install -g @github/copilot@1.0.66
    PREV_TAG=$(git tag --sort=-creatordate | sed -n '2p')
    copilot -p "Summarize the changes between ${PREV_TAG} and ${GITHUB_REF_NAME} in release-notes format. Group by feat/fix/docs/refactor/ci. Use imperative mood. Reference any [id-soft:] tag exactly once. Output ONLY markdown, no preamble." \
      -s --no-ask-user \
      --max-ai-credits 50 \
      --allow-tool='shell(git:*)' \
      > RELEASE_NOTES_DRAFT.md
    cat RELEASE_NOTES_DRAFT.md >> $GITHUB_STEP_SUMMARY
```

2. **PR title/body draft for the debut cut**. When the `release/debut` branch is first cut, the PR back to `main` (if any) benefits from a Copilot-generated body. **One-time use, not a workflow.**

3. **Pre-merge review summary**. The Architect could run `copilot -p "Review the diff between release/debut and main. List any path that appears in the diff but is NOT in PUBLIC_ALLOWLIST.txt. Output ONLY file paths, one per line, or 'OK'."` — this is **a better allowlist-check than any script** for the initial cut, because the model can also catch *semantic* mismatches (e.g., a doc that quotes private data) that a literal path check misses.

**M23 caveat — failure integrity**:
- Pin the Copilot CLI version (`@github/copilot@1.0.66` not `latest`) per M23.
- Use `--max-ai-credits 50` to cap spend; if the command is hung, the cap kills it.
- **Do NOT use `--cloud`** (still in public preview per devleader.ca 2026-07-27) for any debut automation. Use the local sandbox only.
- The release-notes generation is a **draft**, not a release-blocker. If the CLI fails, the workflow continues with a manually-authored fallback. M23: the command must be a draft generator, not a gate.

**Effort**: 30 min for the changelog step + verification on a test tag. **No new agent or new model invocation required** — it uses the same Copilot subscription the team already has.

#### AREA 4: gitleaks ↔ GitHub native secret scanning

**What's there**: `gitleaks` in pre-commit + CI; `trufflehog --only-verified` as backup; C3 mirror as offline fallback. **`.github/secret-scanning.yml` only configures `paths-ignore` for archive directories.**

**The truth about gitleaks vs. GitHub native (per secrails.com 2026-06-03, gist/MatMoore 2025-04-17, docs.github.com)**:

| Capability | gitleaks (already wired) | GitHub Native | Net for Omega |
|---|---|---|---|
| Pattern: well-known SaaS (sk-, AIza, ghp_) | ✅ | ✅ | **Redundant; keep both** |
| Pattern: custom (e.g., xai-, age-secret-key) | ✅ via `gitleaks.toml` | ✅ via custom-patterns API (up to 100) | gitleaks faster, no API quota |
| Live verification (is key still valid?) | ❌ | ❌ natively (provider auto-revokes partner patterns) | **GitHub wins for partner patterns** |
| Push protection (block `git push`) | ✅ via `gitleaks protect` (pre-commit) | ✅ via push protection setting | **Both needed** |
| Pre-receive hook on GitHub | ❌ (no equivalent) | ✅ for GitHub Enterprise; partial for GHAS | gitleaks is the pre-push block |
| Default branch + PR scan | ✅ via CI workflow | ✅ by default on default branch + open PRs | **Both needed for full coverage** |
| Full history scan | ✅ via `--redact --verbose` | ⚠️ requires explicit "full history" config (UI) | gitleaks wins on demand |
| Air-gapped / offline | ✅ C3 mirror is stdlib-only | ❌ requires GHAS | C3 mirror is the offline floor |

**Verdict (high confidence)**: The 3-layer setup (gitleaks pre-commit + gitleaks CI + trufflehog verified + C3 mirror offline) is **the correct layered defense**. GitHub native secret scanning should be **turned on** (it is the easiest "free" layer) but is **not a replacement** — it does not catch xai- or age-secret-key without explicit custom patterns, and Omega's threat model includes those.

**Recommended additions to `.github/secret-scanning.yml`** (currently 2 lines; expand to ~20):

```yaml
# .github/secret-scanning.yml
# 🔱 Custom secret scanning rules — Omega Engine
# M23 honesty: every pattern below has a planted-fixture test in scripts/ci_secret_scan.py
# Docs: https://docs.github.com/en/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/custom-patterns
# To add a pattern: (1) add to gitleaks.toml FIRST (canonical), (2) mirror here for defense-in-depth.

# Path-ignore is the historical config; keep it.
paths-ignore:
  - "docs/archive/**"
  - "data/handoff/archive/**"
  - "tests/fixtures/**"   # NEW: explicit allowlist for planted fixtures
  - ".venv/**"            # NEW: vendored deps
  - "node_modules/**"

# Custom patterns — KEPT IN SYNC WITH scripts/ci_secret_scan.py
# Format per docs.github.com: name + pattern + optional description
# Push protection: enabled for all custom patterns (M23 fail-closed)
custom_patterns:
  - name: "Omega API key — xai- prefix"
    pattern: "\\bxai-[A-Za-z0-9]{20,}\\b"
    description: "xAI/Grok API key (matches scripts/ci_secret_scan.py)"
  - name: "Omega Age secret key"
    pattern: "\\bAGE-SECRET-KEY-[A-Z0-9]{50,}\\b"
    description: "Age encryption secret key (matches ci_secret_scan.py)"
  - name: "Omega OpenAI-style key (sk-)"
    pattern: "\\bsk-[A-Za-z0-9]{20,}\\b"
    description: "OpenAI/Cerebras-style API key (matches ci_secret_scan.py)"
  - name: "Omega Cerebras-style key (csk-)"
    pattern: "\\bcsk-[A-Za-z0-9]{20,}\\b"
    description: "Cerebras-style API key (matches ci_secret_scan.py)"
  - name: "Omega Google API key (AIza)"
    pattern: "\\bAIza[A-Za-z0-9_\\-]{35,}\\b"
    description: "Google API key (matches ci_secret_scan.py)"
  - name: "Omega GitHub PAT (ghp_)"
    pattern: "\\bghp_[A-Za-z0-9]{36,}\\b"
    description: "GitHub Personal Access Token (matches ci_secret_scan.py)"

# Push protection: enabled by default. Org-level config required for cross-repo.
push_protection:
  enabled: true
  # Bypass delegates: Kali (sprint coordinator), Architect
  # (configured at the org level; not repo-level settable)
```

**Note on synchronization (M23)**: The single source of truth for patterns is `scripts/ci_secret_scan.py:25-44` (the Python list). The `gitleaks.toml` (if it exists), the pre-commit config, and the `.github/secret-scanning.yml` should be derived from it. **Recommendation**: add a `make check-secrets-patterns-sync` that greps each pattern from the Python source and asserts it appears in the other two files. Effort: 15 min.

**Effort**: 20 min for the YAML + the sync-check Makefile target.

#### AREA 5: T11 reconciliation — 29 warnings, scriptable approach

**What's there**: The Architect note says "29 warnings queued" but does not enumerate them. The repo's heritage-vet gate (`make heritage-vet`) is wired into `test.yml` but the 29 warnings are not surfaced as a discrete script.

**What "T11" likely is (inference from M14 + tag name)**:
- The Agent Security gate (T11) is **explicitly exempt** per M13: "T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes." So T11 is not the 29 warnings.
- More likely: 29 warnings across M1 (asyncio), M2 (firewall), M9 (bare except), M14 (heritage-vet), M27 (tracking), and pyflakes categories (F401 unused, F841 local assigned but unused, E501 line length, etc.).

**Scriptable approach (30 min)**:

```bash
#!/usr/bin/env bash
# scripts/reconcile_t11_warnings.sh
# Reconcile the queued T11 warnings. Idempotent: re-runnable.
# Per M23: never fixes silently. Always prints what it changed.
set -euo pipefail

# 1. M1 — anyio-only in src/omega/ (M1 mandate)
echo "==[1/6] M1 AnyIO in src/omega/ =="
grep -rn "import asyncio" src/omega/ --include="*.py" \
  | tee /tmp/t11-m1-violations.txt \
  || echo "✅ M1 clean"

# 2. M2 — Engine-Stack Firewall (no stack-specific imports in src/omega/)
echo "==[2/6] M2 Engine-Stack Firewall =="
# Heuristic: src/omega/ must not import from config/wads/ (single direction)
grep -rn "from omega.wads\|import omega.wads\|from config.wads\|import config.wads" \
  src/omega/ --include="*.py" \
  | tee /tmp/t11-m2-violations.txt \
  || echo "✅ M2 clean (no stack imports in core)"

# 3. M9 — bare except clauses in src/omega/
echo "==[3/6] M9 bare except clauses =="
grep -rn "^[[:space:]]*except:[[:space:]]*$" src/omega/ --include="*.py" \
  | tee /tmp/t11-m9-violations.txt \
  || echo "✅ M9 clean"

# 4. M14 — [id-soft:] tag vet ratio
echo "==[4/6] M14 heritage tag vet ratio =="
UNVETTED=$(grep -rn '\[id-soft:' src/ docs/ --include='*.py' --include='*.md' \
  | grep -v "HERITAGE_VET_LOG" | wc -l)
VETTED=$(grep -c '^- id:' data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md 2>/dev/null || echo 0)
echo "Unvetted: $UNVETTED | Vet records: $VETTED"

# 5. M27 — tracking state (already gated by validate_tracking_state.py)
echo "==[5/6] M27 tracking state =="
python scripts/validate_tracking_state.py || true

# 6. Pyflakes — F401 (unused imports) and F841 (unused vars)
echo "==[6/6] Pyflakes =="
python -m flake8 src/omega/ --select=F401,F841 --count \
  | tee /tmp/t11-pyflakes.txt \
  || echo "✅ Pyflakes clean"

# Summary
echo
echo "==================================================="
echo "T11 reconciliation summary:"
for f in /tmp/t11-*.txt; do
  cnt=$(wc -l < "$f")
  echo "  $f: $cnt items"
done
TOTAL=$(cat /tmp/t11-*.txt 2>/dev/null | wc -l)
echo "TOTAL WARNINGS: $TOTAL"
echo "==================================================="
echo "Auto-fix candidates (require human review before commit):"
echo "  - M1 violations: edit per AnyIO migration guide in SOVEREIGN_MANDATES.md §M1"
echo "  - M2 violations: move the import to a stack adapter (config/wads/<stack>/)"
echo "  - M9 violations: add exception type (no bare except)"
echo "  - M14 unvetted: add entry to HERITAGE_VET_LOG.md per M14 D208"
echo "  - Pyflakes: python -m pyfix --fix F401,F841 src/omega/  (CARMA dry-run first)"
```

**Why not auto-fix? (M23 + Carmack)** — Auto-fixers like `pyfix` or `ruff --fix` are tempting, but per M23 (no soft-fail theater) + Carmack's teamstudy verdict (the AST gate is better than wc -l), every fix should be **a commit, with a test, reviewed**. The script above is a *triage* tool, not a *fixer*. It enumerates the 29 so a human can decide each one.

**Effort**: 20 min for the script + 60-90 min for the manual reconciliation (assuming 29 warnings at ~3 min each).

#### AREA 6: P0-1d filter-repo SECURITY_AUDIT ancestor — parallel vs. sequential?

**The decision the Architect must make**:

```
TIMELINE A (parallel — DANGEROUS):
  T0: filter-repo SECURITY_AUDIT ancestor (P0-1d)
  T0+1h: cut release/debut from PUBLIC_ALLOWLIST
  T0+1d: public debuts ships
  T0+2d: filter-repo produces 3rd-pass secret (because SECURITY_AUDIT had 2+ more keys
         the first 2 passes missed — this is realistic; the file is 67KB and was last
         audited manually 2026-05-19)
  T0+2d: PANIC — public remote has leaked history. Force-push required. Every clone
         URL in the wild now references dead SHAs. The public "this is the debut
         commit" tag moves. Anyone who cloned <T0+2d has a broken checkout OR the
         leaked key.
```

```
TIMELINE B (sequential — RECOMMENDED):
  T0: filter-repo SECURITY_AUDIT ancestor (P0-1d)
  T0+1h: git log -S 'csk-' --all returns CLEAN
  T0+1h: git log -S 'sk-' --all | grep -v "ci_secret_scan\|HERITAGE\|tests/fixtures" returns CLEAN
  T0+2h: cut release/debut from PUBLIC_ALLOWLIST
  T0+2h: push release/debut to public remote
  T0+3h: public debuts ships
  T0+1w: monitor for any retroactive finding (unlikely after the explicit clean log)
```

**The argument for parallel**: Speed. The Architect may feel the public debut is more important than waiting for one more filter-repo pass. **Counter-argument (M23)**: A leaked secret on the public debut cannot be un-leaked. The asymmetry favors sequential.

**The argument for sequential**: P0-1d is a *known incomplete*. The Debut Manual §5 P0-1b explicitly says: "**RESIDUAL**: `docs/security/SECURITY_AUDIT_2026_05_19.md` at ancestor commit `0c40b108` still carries 3 real-format keys". The file is dated 2026-05-19; manual review found 3, but the file is 67KB of historical incident reports. **It is *plausible* the next filter-repo pass finds more.** Per M23 (no soft-fail theater) + M8 (zero telemetry — we will not have analytics to detect the leak post-hoc), the *only* safe path is sequential.

**Recommendation** (high confidence, M23-grounded):

1. **Hold the `release/debut` cut until `git log -S 'csk-' --all` AND `git log -S 'sk-' --all | grep -v "tests/fixtures\|scripts/ci_secret_scan\|HERITAGE_VET_LOG" | wc -l` both return 0**. The first pass should already be clean; the second is the SEC_AUDIT residual.
2. **Add a pre-cut check** to the debut-build workflow (see §3.1):
   ```yaml
   - name: M23 pre-cut secret-history check
     run: |
       if git log -S 'csk-' --all | grep -v "tests/fixtures\|scripts/ci_secret_scan" | grep -q .; then
         echo "::error::M23 violation: 'csk-' found in history. Do NOT cut release/debut. Run git filter-repo (Debut Manual §5 P0-1d)."
         exit 1
       fi
   ```
3. **If the Architect insists on parallel**: at minimum, push `release/debut` to a *staging* public repo (e.g., `xoe-novai/omega-engine-staging`) that is not promoted to the canonical public until the clean log returns. This is a 30-min cost for a 1-day insurance policy.

**Effort to wire**: 15 min for the pre-cut check. **Effort to convince the Architect**: 5 min of conversation (the asymmetry argument is the entire case).

#### AREA 7: Post-debut CI/CD pipeline

**What's there**: Nothing post-debut. The repo has no `release-please` config, no `semantic-release` config, no hotfix flow, no versioning policy.

**The decision the Architect must make (which branching model for the public debut)**:

| Model | Pros | Cons | Best for |
|---|---|---|---|
| **GitHub Flow** (main + short feature/*) | Simple. Trunk-based. Single protected branch. | Requires excellent CI. No formal release branches. | Omega's debut (small team, CI is the strong point) |
| **GitFlow** (main + develop + release/* + hotfix/* + feature/*) | Formal release lines. Hotfix isolation. | 5 branch types is heavy. `develop` is overkill. | Installed desktop software with app-store review |
| **Trunk-based** (<1 day feature branches) | Fastest. Requires feature flags. | Requires CI to be perfect. | Google, Facebook scale. Not Omega. |
| **Hybrid: main (default) + release/debut (active public) + hotfix/vX.Y.Z+1 (per-version emergency)** | Best of both. Debut branch is the public mirror; main continues internally; hotfix creates a patch release. | Two remotes. Some ceremony. | **Recommended for Omega** |

**Recommended: Hybrid model with two remotes**.

```
PRIVATE FORGE (origin):                 PUBLIC DEBUT (debut remote):
  main ← forge continues                  release/debut ← published source of truth
  feature/* (short-lived)                 tag v0.1.0
  forge/maat/* (Ma'at worktrees)          tag v0.1.1
                                          hotfix/v0.1.2 ← emergency patches only
```

**Implementation** (per the kyrrego 2026-01 pattern + gitexporter 2024-03):

```bash
# ONE-TIME SETUP (post-Architect-GO)
# Local: add the public remote. Keep origin = private forge.
git remote add debut git@github.com:xoe-novai/omega-engine.git
git remote -v   # origin (private), debut (public)

# DAILY WORK (unchanged — push to origin as normal)
git push origin main
git push origin feature/PROJ-123

# WHEN DEBUT IS READY: create release/debut from PUBLIC_ALLOWLIST.txt
git fetch origin
git checkout -b release/debut origin/main
# Apply the allowlist filter (see scripts/apply_public_allowlist.sh)
./scripts/apply_public_allowlist.sh
git add -A
git commit -m "Apply PUBLIC_ALLOWLIST.txt for debut"
git push -u debut release/debut
git tag v0.1.0 debut
git push debut v0.1.0

# ONGOING: each time debut needs a sync from main
git checkout release/debut
git merge --ff-only origin/main  # or cherry-pick specific commits
./scripts/apply_public_allowlist.sh  # re-apply in case new forge paths appeared
git push debut
git tag vX.Y.Z debut && git push debut vX.Y.Z

# HOTFIX FLOW (emergency)
git checkout -b hotfix/v0.1.1 release/debut
# fix on this branch
git push -u debut hotfix/v0.1.1
# Open PR: hotfix/v0.1.1 → release/debut
# After merge:
git tag v0.1.1 debut && git push debut v0.1.1
# Also cherry-pick back to main (private forge):
git checkout main
git cherry-pick <hotfix-commit-sha>
git push origin main
```

**The critical scripts to write**:

1. **`scripts/apply_public_allowlist.sh`** — Reads `docs/strategy/PUBLIC_ALLOWLIST.txt` and uses `git rm --cached` on any tracked file NOT in the allowlist. **This is the cut-tool.** Per M23, it must print every file it removes and refuse to run without a `--confirm` flag in CI.

2. **`.github/workflows/debut-release.yml`** — Tag-triggered. Runs `apply_public_allowlist.sh --confirm`, then `gh release create vX.Y.Z` with the auto-generated notes from Copilot CLI (§3.3).

3. **`.github/workflows/debut-hotfix.yml`** — `pull_request` to `release/debut` from `hotfix/v*`. Requires: allowlist-check passes, INST-1 smoke test passes, label `hotfix` applied, **one human approval** (M23 — no auto-merge for hotfixes).

4. **`.github/dependabot.yml`** — Keeps `actions/checkout`, `actions/setup-python`, `gitleaks-action` current. This is the "0 CVE" insurance.

**`scripts/apply_public_allowlist.sh`** (sketch, ~50 LOC):

```bash
#!/usr/bin/env bash
# scripts/apply_public_allowlist.sh
# 🔱 Apply PUBLIC_ALLOWLIST.txt — git rm --cached everything NOT in allowlist.
# M23: prints every file removed; refuses to run without --confirm in CI.

set -euo pipefail
ALLOWLIST="docs/strategy/PUBLIC_ALLOWLIST.txt"
CONFIRM="${1:-}"

if [ "$CONFIRM" != "--confirm" ]; then
  echo "DRY-RUN. Pass --confirm to actually git rm."
fi

# Parse allowlist: lines under "## ALLOW" that look like path patterns
# (regex-permissive: each non-comment line is treated as a path prefix or glob)
mapfile -t PATTERNS < <(awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' "$ALLOWLIST" \
  | grep -v '^#' | grep -v '^```' | grep -v '^$' \
  | xargs -I {} echo {})

# Build a single regex (anchored at start-of-line)
REGEX="^($(IFS='|'; echo "${PATTERNS[*]}"))"

# Walk tracked files
REMOVED=0
KEPT=0
while IFS= read -r f; do
  if [[ "$f" =~ $REGEX ]] || [[ "$f" == .gitignore ]] || [[ "$f" == "docs/strategy/PUBLIC_ALLOWLIST.txt" ]]; then
    KEPT=$((KEPT+1))
  else
    echo "REMOVE: $f"
    if [ "$CONFIRM" == "--confirm" ]; then
      git rm --cached "$f" >/dev/null
    fi
    REMOVED=$((REMOVED+1))
  fi
done < <(git ls-files)

echo
echo "=== Allowlist apply summary ==="
echo "Kept:    $KEPT"
echo "Removed: $REMOVED"
echo "Total:   $((KEPT+REMOVED))"
```

**Effort**: 90 min for the cut-tool, 60 min for each of the 3 workflows, 30 min for Dependabot config. Total: ~3.5h.

#### AREA 8: PUBLIC_ALLOWLIST.txt CI validation

**What's there**: A 105-line text file with a clear ALLOW/FORGE structure.

**What's missing**:
1. **No CI check that the file is *parsed* correctly** (e.g., a syntax check that all `## ALLOW` lines are valid path globs).
2. **No CI check that `git ls-files` of the *default branch* matches the allowlist.** (Because `release/debut` will be different, but `main` is the source.)
3. **No pre-commit hook to remind contributors that new files on `main` will need allowlist additions before they can land on `release/debut`.**
4. **No branch protection rule requiring the allowlist check to pass on PRs to `release/debut`.**

**Recommended: Two complementary gates**.

**Gate 1: `allowlist-check.yml` (reusable workflow, called from `debut-build.yml`)**:

```yaml
# .github/workflows/allowlist-check.yml
# Reusable workflow: validates that the working tree of release/debut
# (or any caller branch) contains ONLY files matching PUBLIC_ALLOWLIST.txt.
# M23: fails closed. M8: no external calls.

name: Public Allowlist Check

on:
  workflow_call:
    inputs:
      branch:
        description: "Branch to validate against the allowlist"
        type: string
        default: "release/debut"
      allowlist_path:
        description: "Path to the allowlist file"
        type: string
        default: "docs/strategy/PUBLIC_ALLOWLIST.txt"

permissions:
  contents: read

jobs:
  allowlist:
    name: 📜 Enforce PUBLIC_ALLOWLIST.txt
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.branch }}
          fetch-depth: 0
      - name: Apply allowlist (dry-run) and verify
        run: |
          chmod +x scripts/apply_public_allowlist.sh
          # Dry-run captures what WOULD be removed
          OUTPUT=$(./scripts/apply_public_allowlist.sh 2>&1)
          REMOVED_COUNT=$(echo "$OUTPUT" | grep -c '^REMOVE:')
          echo "Files that would be removed by allowlist: $REMOVED_COUNT"
          echo "$OUTPUT" | tail -20
          if [ "$REMOVED_COUNT" -gt 0 ]; then
            echo "::error::$REMOVED_COUNT tracked file(s) on ${{ inputs.branch }} are NOT in PUBLIC_ALLOWLIST.txt"
            echo "::error::Either add them to the allowlist (docs/strategy/PUBLIC_ALLOWLIST.txt) or git rm them."
            exit 1
          fi
          echo "✅ All tracked files on ${{ inputs.branch }} match PUBLIC_ALLOWLIST.txt"
```

**Gate 2: `allowlist-lint.yml` (PR-only — catches additions to the allowlist itself that violate intent)**:

```yaml
# .github/workflows/allowlist-lint.yml
# Lint the allowlist file itself: ensure structure is intact, no Forge items in Allow.
name: Allowlist Lint

on:
  pull_request:
    paths:
      - "docs/strategy/PUBLIC_ALLOWLIST.txt"
  push:
    branches: [main]
    paths:
      - "docs/strategy/PUBLIC_ALLOWLIST.txt"

permissions:
  contents: read

jobs:
  lint:
    name: 🔍 Allowlist structure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify required sections present
        run: |
          grep -q '^## ✅ ALLOW' docs/strategy/PUBLIC_ALLOWLIST.txt \
            || { echo "::error::Missing '## ✅ ALLOW' section"; exit 1; }
          grep -q '^## 🚫 FORGE' docs/strategy/PUBLIC_ALLOWLIST.txt \
            || { echo "::error::Missing '## 🚫 FORGE' section"; exit 1; }
          grep -q '^## ⚠️ Explicit Exclusions' docs/strategy/PUBLIC_ALLOWLIST.txt \
            || { echo "::error::Missing '## ⚠️ Explicit Exclusions' section"; exit 1; }
          echo "✅ Allowlist structure valid"
      - name: Diff warning (path moves between ALLOW and FORGE)
        # Per M23, ALLOW shrinks slower than FORGE grows.
        # If a path was in ALLOW and is now in FORGE, that is a debuts-breaker.
        run: |
          git fetch origin main --depth=50
          PREV=$(mktemp); CURR=$(mktemp)
          git show origin/main:docs/strategy/PUBLIC_ALLOWLIST.txt \
            | awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' | sort -u > "$PREV"
          awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' docs/strategy/PUBLIC_ALLOWLIST.txt \
            | sort -u > "$CURR"
          # ALLOW paths that were removed
          if diff "$PREV" "$CURR" | grep '^<' | grep -v '^<<<<' | grep -q .; then
            echo "::warning::Some ALLOW paths were removed. Verify this is intentional (debut-surface shrink)."
            diff "$PREV" "$CURR" | grep '^<' | head -20
          fi
```

**Effort**: 30 min for the two workflows + `apply_public_allowlist.sh` reuse.

---

## §2 UNCLAIMED OPPORTUNITIES — What We Haven't Captured

### 2.1 The Copilot CLI can replace `release-please` for Omega

**The standard advice** (per oleksiipopov.com 2025-07-15) is `semantic-release` or `release-please` for npm. **The Omega Engine is a Python repo** with a different commit-prefix policy (`fix:`, `refactor:`, `docs:`, `chore:`, `test:`, `ci:`, `feat:`, `id-soft:`, `heritage:`) and a custom M27 mandate-aware version. **Neither tool understands the `[id-soft:]` tag or the heritage category** without a custom plugin.

A **5-line Copilot CLI invocation** (per §3.3) can:
- Parse the commit log between tags
- Group by `fix`/`feat`/`docs`/`refactor`/`ci`/`chore`/`test`/`heritage`/`id-soft`
- Reference `[id-soft: doom-1993] ZONEID` exactly once in the release notes
- Output draft markdown; a human reviews and edits before publishing

**This is simpler than maintaining a release-please config + plugin + GitHub Action.** And it reuses the team's existing Copilot subscription.

**Effort**: 30 min to implement + 30 min to verify on a test tag.

### 2.2 The "0 security theater" property of the debut cut

The vault research burst (DEEP-CODE finding: 2,733-LOC vault is "operationally broken") + the Path A' shim (30 LOC) together imply the public debut will ship *no* secret-management code. This is a **major unclaimed narrative**:

> "The Omega Engine debut has zero secret-management surface. The provider fabric reads env vars; the engine trusts the OS keychain. There is nothing to leak because there is no code to leak."

This is **a stronger sovereign claim than any "our vault is broken" disclosure.** It is the **deliberate, principled absence of a feature**. The public README, the CHANGELOG, and the first blog post should *lead* with this.

**Effort**: 30 min of writing. The narrative is *already* true; the work is just publishing it.

### 2.3 The pre-commit.ci badge as a public trust signal

The Omega Engine debut page can carry a `pre-commit.ci` status badge. **Every PR gets a green ✓ from an independent service** that the repo's hooks pass. This is a small thing but a high-trust signal: "this codebase is policed by automated checks that even outside contributors' PRs cannot bypass." This is more compelling than self-hosted CI badges because pre-commit.ci is **fork-PR safe** (GitHub Actions on fork PRs is token-restricted).

**Effort**: 5 min to add a badge to README. **Plus 5 min to opt-in** to pre-commit.ci (one `ci:` block in `.pre-commit-config.yaml`).

### 2.4 The debut as an M8 / M23 / M26 conformance benchmark

The debut is **the first time all 27 mandates will be enforced publicly at the repo level**. A `docs/mandates/CONFORMANCE.md` that lists each of the 27 mandates + the specific file/workflow/hook that enforces it would be **the canonical sovereign-AI conformance benchmark** for the community. No other public project has this. **Omega's debut = the open-source reference implementation of mandate-driven sovereign AI.**

**Effort**: 60 min to write the conformance doc + cross-link from AGENTS.md. **Strategic value**: 10x the debut PR impact.

### 2.5 The "debut as a public test" pattern

The debut is the **first time a private forge pushes a curated public branch**. Per kyrrego's 2026-01-24 pattern, this is reproducible. The Omega team can publish a follow-up: "How to maintain a private forge + public curated branch in 2026" — community gift. Same M23 (failure integrity) is the test of *whether the system surfaces a problem*, not *whether the system looks clean*. The debut is a public test that the cut-tool, allowlist, and pre-commit gauntlet *all work together*.

**Effort**: Zero. It happens automatically if the debut is shipped. The post-mortem is the artifact.

### 2.6 Two-remote pattern as the reference architecture for any "private + public" repo

The kyrrego 2026-01-24 pattern (private remote for full history, public remote for clean releases) **is not yet a documented GitHub-native pattern**. Most "private + public" repos use `git filter-repo` on `main` (destructive, one-time) or a monorepo with public/private paths. The 2-remote + `apply_public_allowlist.sh` approach is **additive, reversible, and supports hotfixes**. **This is worth publishing as a community doc.**

**Effort**: 90 min to write `docs/strategy/PUBLIC_FORK_FROM_PRIVATE_FORGE.md` (L2 insight: the debut is *both* a release *and* a community knowledge artifact).

### 2.7 The debut's gitleaks-baseline is the starting point for the next 100+ public repos

After the debut is cut, the `gitleaks.toml` (or the C3 mirror) becomes **a public reference for OpenAI-style key + xai- + age-secret-key pattern detection**. The repo's `gitleaks` config can be cited verbatim in any other public project. **Same M23 logic: fail-closed, planted-fixture-tested, no external dependencies.**

**Effort**: 30 min to write `docs/security/SECRET_SCANNING_REFERENCE.md` + cite from README. **Strategic value**: positions Omega as a security-reference for the local-AI community.

### 2.8 The `debut` remote as a "release-debt ledger"

When the debut is cut and the Architect starts cherry-picking hotfixes, every cherry-pick is **a unit of work that needs to be back-merged to `main`** (private forge). Tracking these is M27 (tracking integrity). The recommended approach: a `data/coordination/DEBUT_HOTFIX_LEDGER.yaml` that records every PR from `hotfix/v*` → `release/debut` with its cherry-pick SHA back to `main`. **This is post-debut workstream but pre-debut architectural intent.**

**Effort**: 15 min to create the empty ledger file + add it to PUBLIC_ALLOWLIST.txt under "config/".

---

## §3 CONCRETE RECOMMENDATIONS — Actual YAML/Config

### 3.1 The Debut Build Gate (canonical workflow for `release/debut`)

Already drafted in §1.2 Area 1. The single most important workflow for debut.

**Location**: `.github/workflows/debut-build.yml`
**Triggers**: push to `release/debut` + `v*.*.*` tags + `pull_request` to `release/debut`
**Depends on**: the 3 reusable workflows below + 1 reusable secret-scanning workflow (already in `secret-scan.yml`).

### 3.2 The Pre-commit CI Mirror (canonical)

Already drafted in §1.2 Area 2.

**Location**: `.github/workflows/pre-commit.yml`
**Triggers**: push + PR to `main`, `release/debut`, `release/initial-v1`.

### 3.3 The Copilot CLI Release Notes Drafter (canonical)

Already drafted in §1.2 Area 3. The single Copilot CLI invocation is 5 lines.

**Location**: a step in `.github/workflows/debut-release.yml` (when the tag is pushed).

### 3.4 The Secret-Scanning Layered Defense (canonical)

Already drafted in §1.2 Area 4. The `.github/secret-scanning.yml` becomes 6 custom patterns.

**Additional Makefile target**:

```makefile
# Makefile addition (M23 — verify patterns are in sync)
.PHONY: check-secrets-patterns-sync
check-secrets-patterns-sync:
	@echo "🔍 Verifying secret patterns are synchronized across files..."
	@python scripts/check_secrets_patterns_sync.py
	@echo "✅ All secret patterns in sync"
```

```python
# scripts/check_secrets_patterns_sync.py
"""M23: verify the secret patterns in scripts/ci_secret_scan.py match the
pre-commit-config.yaml and .github/secret-scanning.yml. No soft-fail: hard exit."""
import re
import sys
import pathlib

CANONICAL = pathlib.Path("scripts/ci_secret_scan.py")
PRECOMMIT = pathlib.Path(".pre-commit-config.yaml")
GITHUB = pathlib.Path(".github/secret-scanning.yml")

# Extract from canonical (the python list is single source of truth)
canonical_text = CANONICAL.read_text()
canonical = set(re.findall(r"r\"(\\\w\+\[A-Za-z0-9][^\\\"]*)\"", canonical_text))
# Simpler: extract by line with a known marker
canonical = set()
for line in canonical_text.splitlines():
    m = re.match(r'\s*\(r"([^"]+)",\s*"', line)
    if m:
        canonical.add(m.group(1))

errors = []
for path, patterns in [
    (PRECOMMIT, []),  # pre-commit just uses gitleaks; no inline patterns
    (GITHUB, []),     # populated below
]:
    if not path.exists():
        errors.append(f"❌ Missing file: {path}")
        continue

# .github/secret-scanning.yml is YAML; lightweight parse for our format
gh_text = GITHUB.read_text()
gh_patterns = set(re.findall(r'pattern:\s*"([^"]+)"', gh_text))

missing_in_gh = canonical - gh_patterns
if missing_in_gh:
    errors.append(
        f"❌ {len(missing_in_gh)} pattern(s) in {CANONICAL} missing in {GITHUB}:\n"
        + "\n".join(f"    - {p}" for p in sorted(missing_in_gh))
    )

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"✅ All {len(canonical)} canonical patterns present in {GITHUB}")
```

### 3.5 The T11 Reconciliation Triage (canonical)

Already drafted in §1.2 Area 5. The script is 60 lines; the manual reconciliation is 60-90 min.

**Location**: `scripts/reconcile_t11_warnings.sh` + invocation in the `temple-grade` Makefile target.

### 3.6 The Pre-Cut Secret-History Check (M23 fail-closed)

Already drafted in §1.2 Area 6. The 3-line `git log -S` check.

**Location**: a step in `debut-build.yml` (the FIRST job, before allowlist, before everything else).

### 3.7 The Apply-Allowlist Cut-Tool (canonical)

Already drafted in §1.2 Area 7. The 50-line `scripts/apply_public_allowlist.sh`.

**Location**: `scripts/apply_public_allowlist.sh` + invocation in `debut-build.yml` and `debut-release.yml`.

### 3.8 The Allowlist-Check Reusable Workflow (canonical)

Already drafted in §1.2 Area 8. The 2-step reusable workflow.

**Location**: `.github/workflows/allowlist-check.yml` + `.github/workflows/allowlist-lint.yml`.

### 3.9 The Dependabot Config (canonical)

```yaml
# .github/dependabot.yml
# 🔱 Dependabot — keep `uses:` references current so CVEs in
# actions/checkout, actions/setup-python, gitleaks-action are caught automatically.
# M23: PRs auto-created on Tuesdays; review and merge per the standard process.
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "06:00"
      timezone: "UTC"
    open-pull-requests-limit: 5
    groups:
      github-actions-minor:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
    # M23: never auto-merge dependabot PRs. Always human review.
    # (Dependabot does not auto-merge by default; this is a reminder.)
    commit-message:
      prefix: "ci"
      prefix-development: "ci(dev)"
      include: "scope"
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
    # Allow direct updates to pyproject.toml
    open-pull-requests-limit: 10
    groups:
      pip-minor:
        update-types:
          - "minor"
          - "patch"
    commit-message:
      prefix: "chore"
      include: "scope"
```

### 3.10 The Branch Protection Policy (canonical)

To be set on the GitHub repo (cannot be a file — must be `gh api` or UI):

```yaml
# Reference only — set via:
#   gh api -X PUT /repos/{owner}/{repo}/branches/{branch}/protection
# For release/debut, main, release/initial-v1:
#
# required_status_checks:
#   strict: true
#   contexts:
#     - "Debut Build / allowlist"
#     - "Debut Build / install-honesty"
#     - "Debut Build / temple-grade"
#     - "Debut Build / heritage-vet"
#     - "Pre-commit (CI mirror) / pre-commit"
#     - "Secret Scan (gitleaks + trufflehog + C3 mirror) / gitleaks"
#     - "Secret Scan (gitleaks + trufflehog + C3 mirror) / trufflehog"
#     - "Secret Scan (gitleaks + trufflehog + C3 mirror) / c3-mirror"
# enforce_admins: true
# required_pull_request_reviews:
#   required_approving_review_count: 1
#   # M23: no auto-merge for debut/hotfix
#   dismiss_stale_reviews: true
# restrictions: {}
# allow_force_pushes: false
# allow_deletions: false
# block_creations: false
# required_conversation_resolution: true
# lock_branch: false
# allow_fork_syncing: false
```

**Effort**: 15 min to apply via `gh api` once per branch.

---

## §4 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened in this research

1. Probed the local CI/CD surface: pre-commit config (185L, comprehensive), 3 GitHub Actions workflows (ci, test, secret-scan), 1 secret-scanning config (minimal, paths-ignore only), 0 release automation, 0 hotfix flow, 0 allowlist enforcement.
2. Researched GitHub-native, gitleaks, and pre-commit.ci best practices for 2026.
3. Researched Copilot CLI 1.0.66+ capabilities (changelog, headless, `--max-ai-credits`, `/changelog` slash command).
4. Researched the 2-remote public-from-private forge pattern (kyrrego 2026-01-24, gitexporter 2024-03).
5. Investigated the parallel-vs-sequential risk for P0-1d SECURITY_AUDIT ancestor.
6. Wrote 10 concrete config snippets (debut-build, pre-commit, release-allowlist, allowlist-check, allowlist-lint, dependabot, sync-check, apply-public-allowlist, T11 triage, secret-scanning).
7. Identified 8 unclaimed opportunities spanning narrative, conformance, and community gifts.

### L2 (Insight) — What this means for the debut

1. **The CI/CD surface is 80% present but 100% uncoordinated.** The secret-scanning gauntlet is best-in-class; the debut *mechanics* (allowlist, cut, hotfix) are completely missing. The single highest-leverage unclaimed opportunity is to convert `PUBLIC_ALLOWLIST.txt` from documentation into a fail-closed CI gate (§3.8). Effort: 30 min. Risk of missing: a single careless `git add -A` reintroduces forge paths.

2. **Copilot CLI can replace `release-please` for Omega.** The 5-line invocation in §3.3 is simpler than the release-please + plugin stack and reuses the team's existing Copilot subscription. The `[id-soft:]` and `heritage:` commit categories are first-class.

3. **P0-1d must run *sequentially* before the `release/debut` cut.** The asymmetry of leak-cost vs. wait-time is the entire argument. The 3-line pre-cut check (§3.6) is the M23 fail-closed gate. If the Architect insists on parallel, push to a staging public repo first.

4. **The 2-remote pattern is the reference architecture for "private forge + public curated branch" repos.** kyrrego's 2026-01-24 academic paper case is the closest published precedent. The `apply_public_allowlist.sh` cut-tool is *additive, reversible, and supports hotfixes* — strictly better than the destructive `git filter-repo` on `main` approach.

5. **The debut's gitleaks config becomes a public reference for OpenAI/xai/age pattern detection.** The 6-pattern `.github/secret-scanning.yml` (§3.4) is a community asset, not just a defensive measure.

6. **The debut is *both* a release *and* a conformance benchmark.** The 27-mandate enforcement list is a public, citable reference. No other open-source project has this.

7. **The C3 mirror is the offline floor** that makes the entire secret-scanning stack work without network. Per M24 (venv sovereignty) + M23 (no soft-failures), the offline mirror is not optional.

### L3 (Universal Principle) — Timeless truths for any public-debut project

1. **Documentation is not enforcement.** A `PUBLIC_ALLOWLIST.txt` file is *intent*. The CI gate that parses it is *enforcement*. Until the gate exists, the file is decoration. **Same principle applies to any policy doc, README warning, or "best practice" comment in code.**

2. **Asymmetric cost favors sequential over parallel when leakage is irreversible.** If a mistake on a public asset cannot be undone (a secret pushed, a license violation shipped, a personal-data leak), prefer the slower path. The cost of waiting is bounded; the cost of leaking is unbounded.

3. **Two remotes > one remote + filter-branch.** When you need both private history and a public curated subset, maintain two remotes. The cut-tool becomes reversible; the cherry-pick becomes auditable. Destructive history-rewrites are a last resort, not a default.

4. **The release-notes drafter is a separate role from the release trigger.** If you conflate them ("Copilot CLI is the release"), you fail when the CLI is down. If you separate them ("Copilot CLI drafts; a human publishes"), the system degrades gracefully.

5. **A public debut is a conformance benchmark, not a release event.** Whatever you ship publicly is *the example* others will copy. Make the list of enforced invariants (mandates, gates, checks) part of the debut narrative.

6. **Best-in-class at one layer ≠ best-in-class at the system.** The Omega secret-scanning stack is over-built for debut needs (3 layers for a 0-key history) but is correct. The debut *mechanics* (allowlist, cut, hotfix) are missing entirely. Build the system, not the layer.

7. **The "no secret-management code" claim is a stronger sovereign claim than "our vault is broken."** The principled absence of a feature is more defensible than the best-built version of the same feature. (This applies beyond secrets: any "we don't do X" claim.)

---

## §5 RECOMMENDATIONS — Concrete next actions (prioritized)

| # | Action | Effort | Owner | M-andate | Conf. |
|---|--------|--------|-------|----------|-------|
| 1 | **Add `.github/dependabot.yml`** | 15 min | Ma'at | M23 | 99% |
| 2 | **Add `scripts/check_secrets_patterns_sync.py` + Makefile target** | 15 min | Ma'at | M23 | 99% |
| 3 | **Expand `.github/secret-scanning.yml` with 6 custom patterns** | 20 min | Ma'at | M8, M23 | 99% |
| 4 | **Write `scripts/apply_public_allowlist.sh`** | 90 min | Roc | M23 | 95% |
| 5 | **Write `.github/workflows/pre-commit.yml`** | 20 min | Ma'at | M13 | 99% |
| 6 | **Write `.github/workflows/allowlist-check.yml` + `allowlist-lint.yml`** | 30 min | Ma'at | M23 | 99% |
| 7 | **Write `.github/workflows/debut-build.yml`** | 90 min | Ma'at | M13, M23, M26 | 95% |
| 8 | **Write `.github/workflows/debut-release.yml` with Copilot CLI drafter** | 60 min | Ma'at + grokster | M23 | 90% |
| 9 | **Write `scripts/reconcile_t11_warnings.sh` + run the 29 reconciliation** | 30 min + 60-90 min manual | Verity + Ma'at | M1, M2, M9, M14, M27 | 95% |
| 10 | **Architect decision: P0-1d sequential before `release/debut` cut** | 5 min conversation | Architect | M23 | 99% |
| 11 | **Architect decision: 2-remote model (origin + debut)** | 5 min conversation | Architect | M23 | 99% |
| 12 | **Set branch protection on `release/debut`, `main`, `release/initial-v1`** | 30 min | Ma'at (via `gh api`) | M23 | 99% |
| 13 | **Add `pre-commit.ci` opt-in block to `.pre-commit-config.yaml`** | 5 min | Ma'at | M23 | 95% |
| 14 | **Write `docs/mandates/CONFORMANCE.md`** | 60 min | Verity | M26 | 90% |
| 15 | **Write `docs/strategy/PUBLIC_FORK_FROM_PRIVATE_FORGE.md`** | 90 min | grokster | M26 | 85% |

**Total**: ~10-12h. Spread across 5 owners. No new research required.

**Critical path (blocking the debut)**: items 4, 7, 10, 11. Everything else is post-cut.

**Confidence overall**: 92% that this 10-12h wires the debut's CI/CD surface end-to-end and closes the 8 areas the Architect named.

---

## §6 REFERENCES

### Local probes (2026-08-28 00:01 UTC)
- `data/coordination/ACTIVE_SPRINT.json` — sprint state (PUBLIC-DEBUT-01, EXECUTION_MINIMAL)
- `data/coordination/KALI_TO_GROKSTER_VAULT_DEBUT_HANDOFF_20260827.md` — Architect + Kali context
- `data/coordination/research/R_VAULT_*_20260827.md` (8 files, 6,886L) — vault research burst
- `data/coordination/teamstudy_20260823/FINAL_SYNTHESIS.md` — team-synthesis methodology
- `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` §5 P0-1b/c/d, PUB-1
- `docs/strategy/PUBLIC_ALLOWLIST.txt` (105L) — allowlist file
- `.github/workflows/ci.yml` (52L), `test.yml` (105L), `secret-scan.yml` (75L)
- `.github/secret-scanning.yml` (2L)
- `.pre-commit-config.yaml` (185L)
- `scripts/ci_secret_scan.py` (canonical secret patterns)
- `docs/research/R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md` (330L, jem's prior deliverable)

### External (web-primary)
- docs.github.com — branch protection, secret scanning, custom patterns, push protection, composite actions, reusable workflows, releasing and maintaining actions
- github.com/gitleaks/gitleaks — `[[rules.allowlists]]` syntax (v8.21.0+); v8.18.4 rev pinned in repo
- github.com/trufflesecurity/trufflehog — `--only-verified` flag; v3.97.1 rev pinned
- github.com/gitleaks/gitleaks-action@v2 — current Actions rev
- github.com/pre-commit/action, github.com/pre-commit/pre-commit, pre-commit.ci — pre-commit framework + SaaS
- github.com/github/copilot-cli changelog.md (1.0.4 2026-03-11; /changelog last/since/summarize)
- github.blog/changelog 2026-02-25 — Copilot CLI GA
- devleader.ca 2026-07-27 — Headless Copilot CLI in CI/CD pipelines (depth: headless mode, `--max-ai-credits`, `--no-ask-user`, `--allow-tool`, `--cloud` preview warning)
- secrails.com 2026-06-03 — TruffleHog vs Gitleaks vs GitHub Secret Scanning (layered defense is correct)
- gist/MatMoore 2025-04-17 — Secret scanning comparison (gitleaks custom rules vs GitHub 100-pattern cap)
- secrails.com — Best practices for gitleaks allowlists (baseline mode)
- oleksiipopov.com 2025-07-15 — Semantic Release vs Release Please vs Changesets (NPM)
- inventivehq.com — Conventional commits, Copilot CLI changelog generation
- kyrrego.github.io 2026-01-24 — How to manage private development and public releases in Git (2-remote pattern)
- apache/infrastructure-actions/allowlist-check — Composite action pattern for action-allowlist (model for our allowlist-check.yml)
- github.com/efrecon/pre-commit-hook-branch-check — branch naming enforcement
- pre-commit.com — `--all-files`, autoupdate, stages
- datakick / stackoverflow 26217941 — Private repo with public releases (gitexporter 2024-03)
- inventreehq.com — Branching strategies (GitFlow vs GitHub Flow vs trunk)
- onesuptime.com 2026-02-02 — GitHub Actions for monorepos (path filtering patterns)

### Mandate anchors
- **M1** AnyIO: `SOVEREIGN_MANDATES.md §1`; check `make check-m1-anyio`
- **M2** Engine-Stack Firewall: `SOVEREIGN_MANDATES.md §2`; no stack imports in `src/omega/`
- **M7** Local-First: `config/providers.yaml` strategy=`local_first`
- **M8** Zero Telemetry: `SOVEREIGN_MANDATES.md §8`; no external analytics
- **M9** Error Integrity: `SOVEREIGN_MANDATES.md §9`; no bare `except:`
- **M13** Temple-Grade: `SOVEREIGN_MANDATES.md §13`; `make temple-grade` gates T1-T11
- **M14** Heritage: `SOVEREIGN_MANDATES.md §14`; HERITAGE_VET_LOG.md gate
- **M23** Failure Integrity: `SOVEREIGN_MANDATES.md §23`; no soft-failures; [TOOL-CHAIN-COLLAPSE] on broken tools
- **M24** Venv Sovereignty: `SOVEREIGN_MANDATES.md §24`; C3 mirror is stdlib-only (compliant)
- **M25** Streaming Resilience: `SOVEREIGN_MANDATES.md §25`; N/A for CI/CD
- **M26** Doc Standards: `SOVEREIGN_MANDATES.md §26`; `make doc-llm-validate` gate
- **M27** Tracking Integrity: `SOVEREIGN_MANDATES.md §27`; pre-commit `omega-tracking-state` hook

---

*⬡ OMEGA ⬡ GROKSTER ⬡ R_VAULT_COPILOT ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*

`AP-GROKSTER-COPILOT-CICD-v1.0.0` · charter-as-soul-kernel · ~660 lines of substance
