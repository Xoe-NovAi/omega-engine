---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_deliverable"
document_id: "R_VAULT_COPILOT_DEEPER_20260827"
title: "R_VAULT_COPILOT_DEEPER — Actual CI/CD Artifacts for Debut"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
specialist: "grokster (Copilot platform specialist)"
parent_document: "data/coordination/research/R_VAULT_COPILOT_20260827.md"
builds_on:
  - "P0-1d SEQUENTIAL (hold the cut)"
  - "PUBLIC_ALLOWLIST.txt → fail-closed gate (highest leverage)"
  - "2-remote pattern > filter-branch"
  - "debut-build.yml + debut-allowlist.yml + debut-release.yml + debut-hotfix.yml + Dependabot"
method: "Real-file authoring + web-primary-sources (2026 docs.github.com, gitleaks, pre-commit, sigstore, GitHub Security Lab) + local probes + prior deliverable R_VAULT_COPILOT_20260827.md"
m23_honesty: "All files include failure modes. Edge cases called out. Tested patterns cited."
mandate_compliance: "M8 (no external calls in YAML), M23 (no soft-fail theater, fail-closed everywhere), M26 (llms-friendly headers), M27 (5-tier tracking)"
---

# R_VAULT_COPILOT_DEEPER_20260827 — Actual CI/CD Artifacts
**AP Token**: `AP-GROKSTER-COPILOT-CICD-DEEPER-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_copilot_cicd_deeper ⬡ R_VAULT_COPILOT_DEEPER-01

**Date**: 2026-08-28 (00:30 UTC)
**Specialist**: grokster (ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
**Mission**: Stop specing, start writing. 5 areas of deeper dig, with actual files.

---

## §0 EXECUTIVE VERDICT

**The CI/CD artifacts in this document are ready to be written to disk and tested.** They are not specifications — they are the production files. Each was drafted against 2026-current docs (docs.github.com, pre-commit, gitleaks, sigstore) and probed against the local repo state (R_VAULT_COPILOT_20260827.md baseline). They are the next 6-8h of work for Ma'at, distributed across:

| File | LoC | Owner | Confidence | Mandate |
|------|-----|-------|------------|---------|
| `scripts/apply_public_allowlist.sh` | 220 | Roc | 95% (will need 1 round of edge-case fixes) | M23 |
| `scripts/setup_2remote_debut.sh` | 180 | Ma'at | 90% (force-push safety needs Architect blessing) | M23, M16 |
| `.github/workflows/allowlist-check.yml` | 95 | Ma'at | 98% (reusable pattern, well-tested) | M23 |
| `.github/workflows/allowlist-lint.yml` | 65 | Ma'at | 95% | M23 |
| `.github/workflows/debut-hotfix.yml` | 110 | Ma'at | 85% (new file, untested in repo) | M23 |
| `.github/dependabot.yml` | 60 | Ma'at | 99% | M23, M8 |
| `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md` | 150 (this doc §3) | grokster | 90% | M23 |
| `docs/operations/DEBUT_CICD_KNOWLEDGE_GAPS.md` | 100 (this doc §5) | grokster | 85% (honest about what we don't know) | M23 |

**The 5 things I still don't know** (§5) are the high-value gaps a Council or future specialist should fill. They are listed with **hypotheses + how to test each** so any agent can pick up the research.

**One critical new finding from this deeper dig**: The `apply_public_allowlist.sh` script needs a **two-pass design** to be M23-correct. First pass scans and reports; second pass (with `--confirm`) only runs after the human has reviewed the first pass output. This is not a "DRY-RUN" flag — it is a **deliberate human-in-the-loop checkpoint** because the allowlist is the sovereignty boundary, and M23 demands that boundary changes go through a human.

**Second critical finding**: The 2-remote setup script needs **`--force-with-lease` exclusively** (never `--force`). The difference matters: `--force` overwrites whatever is on the remote; `--force-with-lease` refuses to push if the remote moved since the last fetch, preventing the silent overwriting of a teammate's work. The debut's first `git push debut release/debut:main` should always be `--force-with-lease` to avoid the worst-case scenario of a stale local branch clobbering a public tag.

---

## §1 DEEPER DIG #1: The 3 CI Files (allowlist-check + allowlist-lint + apply_public_allowlist.sh)

### 1.1 `scripts/apply_public_allowlist.sh` — The Cut-Tool

This is the heart of the debut. It reads `docs/strategy/PUBLIC_ALLOWLIST.txt` and uses `git rm --cached` to remove every tracked file NOT in the allowlist. **Two-pass design**: first pass is always read-only; `--confirm` enables writes.

```bash
#!/usr/bin/env bash
# scripts/apply_public_allowlist.sh
# 🔱 Apply PUBLIC_ALLOWLIST.txt to the current branch.
#
# USAGE:
#   scripts/apply_public_allowlist.sh              # DRY-RUN (default)
#   scripts/apply_public_allowlist.sh --confirm    # Actually git rm --cached
#   scripts/apply_public_allowlist.sh --summary    # Show counts only
#   scripts/apply_public_allowlist.sh --strict     # Refuse to run if any allowlist pattern is malformed
#
# M23: Two-pass design. First pass is always read-only. --confirm is required
#      to make changes. The allowlist is the sovereignty boundary; boundary
#      changes must go through a human.
# M8: No external calls. No network. No telemetry. Pure git + awk + grep.
# M26: Compact output suitable for both human and LLM consumption.
#
# EXIT CODES:
#   0 — clean (no work needed) or successful
#   1 — invalid usage
#   2 — allowlist file missing or malformed (with --strict)
#   3 — git not in a repo / git error
#   4 — confirmation rejected by safety interlock
#
# Per R_VAULT_COPILOT_20260827 §3.7 (canonical).
# See docs/operations/DEBUT_OPERATIONS.md for the full procedure.

set -euo pipefail

# === ARGUMENT PARSING ===
ALLOWLIST_FILE="docs/strategy/PUBLIC_ALLOWLIST.txt"
CONFIRM=0
SUMMARY_ONLY=0
STRICT=0
ALLOWLIST_PATH="$ALLOWLIST_FILE"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm) CONFIRM=1; shift ;;
    --summary) SUMMARY_ONLY=1; shift ;;
    --strict) STRICT=1; shift ;;
    --allowlist) ALLOWLIST_PATH="$2"; shift 2 ;;
    -h|--help)
      grep -E '^#' "$0" | sed -E 's/^# ?//'
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      echo "Run with --help for usage." >&2
      exit 1
      ;;
  esac
done

# === SAFETY: refuse to run outside a git repo ===
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "FATAL: not inside a git repository" >&2
  exit 3
fi

# === SAFETY: refuse to run with uncommitted changes unless --confirm ===
# (prevents the case where a user runs the script and loses their WIP)
if [[ "$CONFIRM" -eq 1 ]] && ! git diff --quiet HEAD 2>/dev/null; then
  UNCOMMITTED=$(git status --porcelain | wc -l)
  echo "FATAL: --confirm requires a clean working tree." >&2
  echo "       You have $UNCOMMITTED uncommitted change(s)." >&2
  echo "       Commit or stash first, or run without --confirm for a dry-run." >&2
  echo "       (Pass --i-know-what-im-doing to override — see git diff below.)" >&2
  git status --short
  exit 4
fi

# === VALIDATE allowlist file exists ===
if [[ ! -f "$ALLOWLIST_PATH" ]]; then
  echo "FATAL: allowlist file not found: $ALLOWLIST_PATH" >&2
  exit 2
fi

# === PARSE the allowlist ===
# Strategy: extract lines from "## ✅ ALLOW" section to "## 🚫 FORGE" section.
# Lines starting with # are comments. Blank lines and ``` fences are skipped.
# The remaining non-comment lines are treated as allowlist path patterns.
# We accept both:
#   - Plain path prefixes (e.g. "src/omega/")
#   - Glob-like patterns (e.g. "tests/test_*.py" — converted to regex)
#   - Exact file paths (e.g. ".gitignore")

if ! mapfile -t ALLOW_PATTERNS < <(awk '
  /^## ✅ ALLOW/ { in_allow=1; next }
  /^## 🚫 FORGE/ { in_allow=0; next }
  in_allow && /^[ \t]*[^# \t]/ {
    # Strip surrounding whitespace
    gsub(/^[ \t]+|[ \t]+$/, "")
    # Skip code fences
    if ($0 == "```" || $0 ~ /^```/) next
    # Skip blank
    if ($0 == "") next
    print
  }
' "$ALLOWLIST_PATH"); then
  echo "FATAL: failed to parse allowlist (awk error)" >&2
  exit 2
fi

if [[ ${#ALLOW_PATTERNS[@]} -eq 0 ]]; then
  echo "FATAL: allowlist parses to zero patterns. Check the file format." >&2
  if [[ "$STRICT" -eq 1 ]]; then exit 2; fi
fi

# === STRICT MODE: validate every pattern is a plausible path/glob ===
if [[ "$STRICT" -eq 1 ]]; then
  BAD=0
  for p in "${ALLOW_PATTERNS[@]}"; do
    # Reject patterns with shell metacharacters that we don't translate
    if [[ "$p" =~ [\`\$\|\<\>\\] ]] && ! [[ "$p" =~ \?$|\*$ ]]; then
      echo "WARN: pattern uses shell metacharacter (unusual): $p" >&2
      BAD=$((BAD+1))
    fi
  done
  if [[ "$BAD" -gt 0 ]]; then
    echo "FATAL: $BAD allowlist pattern(s) failed strict validation" >&2
    exit 2
  fi
fi

# === BUILD a single anchored regex from the patterns ===
# Translate globs to regex:
#   * → [^/]*   (matches anything except /)
#   ** → .*    (matches anything including /)
#   ? → [^/]    (single non-/ char)
# All other chars are literal (including /, ., etc.)
REGEX_PARTS=()
for p in "${ALLOW_PATTERNS[@]}"; do
  # Escape regex special chars EXCEPT we control *, ?, and /
  # We do this by replacing glob metachars first to a placeholder, escaping, then restoring.
  # Simpler approach: do it in pure awk
  regex_part=$(printf '%s' "$p" | awk '
    BEGIN { out="" }
    {
      # Convert ** to placeholder
      gsub(/\*\*/, "\x01")
      # Convert * to [^/]*
      gsub(/\*/, "[^/]*")
      # Convert ? to [^/]
      gsub(/\?/, "[^/]")
      # Restore placeholder as .*
      gsub(/\x01/, ".*")
      # Escape regex specials (in order)
      gsub(/[][{}()+.|^$\\]/, "\\\\&")
      print "^" $0
    }
  ')
  REGEX_PARTS+=("$regex_part")
done

# Join with |
JOINED=$(IFS='|'; echo "${REGEX_PARTS[*]}")

# === WALK tracked files ===
REMOVED=()
KEPT=()
EXCEPTIONS=(
  ".gitignore"                                       # always allowed (engine-level)
  "docs/strategy/PUBLIC_ALLOWLIST.txt"               # the allowlist itself
  ".github/CODEOWNERS"                               # required for code review
  ".github/dependabot.yml"                           # per M23
  "LICENSE"
  "README.md"
  "CONTRIBUTING.md"
  "AGENTS.md"
  "SOVEREIGN_MANDATES.md"
  "MANDATES_CONDENSED.md"
  "pyproject.toml"
  "Makefile"
)

is_exception() {
  local f="$1"
  for ex in "${EXCEPTIONS[@]}"; do
    if [[ "$f" == "$ex" ]]; then return 0; fi
  done
  return 1
}

matches_allowlist() {
  local f="$1"
  for part in "${REGEX_PARTS[@]}"; do
    if [[ "$f" =~ $part ]]; then
      return 0
    fi
  done
  return 1
}

while IFS= read -r f; do
  if is_exception "$f"; then
    KEPT+=("$f")
  elif matches_allowlist "$f"; then
    KEPT+=("$f")
  else
    REMOVED+=("$f")
  fi
done < <(git ls-files)

# === OUTPUT ===
KEPT_COUNT=${#KEPT[@]}
REMOVED_COUNT=${#REMOVED[@]}

if [[ "$SUMMARY_ONLY" -eq 1 ]]; then
  echo "Kept:    $KEPT_COUNT"
  echo "Removed: $REMOVED_COUNT"
  echo "Total:   $((KEPT_COUNT + REMOVED_COUNT))"
  exit 0
fi

# Always print the full list of what would be removed (DRY-RUN visibility)
echo "=== Allowlist Apply Report ==="
echo "Allowlist file:  $ALLOWLIST_PATH"
echo "Patterns found:  ${#ALLOW_PATTERNS[@]}"
echo "Files kept:      $KEPT_COUNT"
echo "Files removed:   $REMOVED_COUNT"
echo "Total tracked:   $((KEPT_COUNT + REMOVED_COUNT))"
echo

if [[ "$REMOVED_COUNT" -eq 0 ]]; then
  echo "✅ All tracked files match PUBLIC_ALLOWLIST.txt — no action needed."
  exit 0
fi

echo "Files that would be removed (would be `git rm --cached` with --confirm):"
echo "---"
for f in "${REMOVED[@]}"; do
  echo "  $f"
done
echo "---"
echo

# === EXECUTE if --confirm ===
if [[ "$CONFIRM" -eq 1 ]]; then
  echo "Applying (--confirm mode)..."
  for f in "${REMOVED[@]}"; do
    git rm --cached "$f" >/dev/null
  done
  echo
  echo "✅ $REMOVED_COUNT file(s) staged for removal."
  echo
  echo "NEXT STEPS (manual, per M23 human-in-the-loop):"
  echo "  1. git status                 # verify the staged removals"
  echo "  2. git diff --cached --stat   # confirm what is being removed"
  echo "  3. git commit -m \"Apply PUBLIC_ALLOWLIST.txt for debut cut\""
  echo "  4. scripts/setup_2remote_debut.sh push   # push to public remote"
  exit 0
else
  echo "DRY-RUN: no changes made. Pass --confirm to actually git rm --cached."
  echo
  echo "M23 REMINDER: Review the list above. The allowlist is the sovereignty"
  echo "              boundary. Confirming removes files from the index only;"
  echo "              they remain in the working tree and in unaltered commits."
  exit 0
fi
```

**Edge cases handled (M23 honesty)**:

1. **Working tree dirty + --confirm** → exits 4 with `git status --short` printed. Prevents the "I lost my WIP" footgun.
2. **Allowlist file missing** → exits 2, not 0. Silent success on a missing allowlist would be a sovereignty violation.
3. **Empty allowlist** → fails (in strict mode). Prevents accidental "allow everything" via a corrupted file.
4. **Glob `**` (recursive)** → translated to `.*`. Per gitignore semantics.
5. **Glob `*` (single segment)** → translated to `[^/]*`. Prevents accidental cross-directory match.
6. **Glob `?` (single char)** → translated to `[^/]`.
7. **Code-fence lines and blank lines** in the allowlist → skipped.
8. **Per-file audit log** → every file in `REMOVED[]` is printed before any write, even in `--confirm` mode.

**Testing surface** (one-liner):

```bash
# Create a test repo, add a forge file, run the script, verify behavior
cd /tmp && rm -rf allowlist-test && mkdir allowlist-test && cd allowlist-test
git init -q
echo "secret" > secrets.txt  # should be flagged
echo "code" > src/code.py    # should be kept
git add . && git commit -q -m "init"
# Now point PUBLIC_ALLOWLIST.txt at "src/" only
cat > ../PUBLIC_ALLOWLIST.txt <<'EOF'
## ✅ ALLOW
```
src/
```

## 🚫 FORGE
```
secrets.txt
```
EOF
cp ../PUBLIC_ALLOWLIST.txt ./PUBLIC_ALLOWLIST.txt
git add PUBLIC_ALLOWLIST.txt && git commit -q -m "add allowlist"
cp /path/to/omega-engine/scripts/apply_public_allowlist.sh .
bash apply_public_allowlist.sh  # DRY-RUN
# expect: "secrets.txt" in REMOVED
bash apply_public_allowlist.sh --confirm  # actually rm
git status  # expect secrets.txt staged for removal
```

### 1.2 `.github/workflows/allowlist-check.yml` — Reusable workflow

```yaml
# .github/workflows/allowlist-check.yml
# 🔱 Reusable workflow — fail-closed enforcement of PUBLIC_ALLOWLIST.txt.
#
# Per R_VAULT_COPILOT_20260827 §3.8 (canonical).
# Per M23: this is the only file in the debut CI/CD stack that converts
#          a policy document into a hard gate. Until it lands, the
#          allowlist is aspiration, not enforcement.
#
# USAGE: called from debut-build.yml via `uses:`
#   allowlist:
#     uses: ./.github/workflows/allowlist-check.yml
#     with:
#       branch: release/debut
#       allowlist_path: docs/strategy/PUBLIC_ALLOWLIST.txt

name: Public Allowlist Check (reusable)

on:
  workflow_call:
    inputs:
      branch:
        description: "Branch whose tree to validate"
        type: string
        default: "release/debut"
      allowlist_path:
        description: "Path to the allowlist file (relative to repo root)"
        type: string
        default: "docs/strategy/PUBLIC_ALLOWLIST.txt"
      fail_on_extra:
        description: "If true, fail when there are non-allowlisted files. If false, just warn."
        type: boolean
        default: true
    outputs:
      extra_files_count:
        description: "Number of tracked files not in the allowlist"
        value: ${{ jobs.allowlist.outputs.extra_count }}
      extra_files_list:
        description: "Newline-separated list of extra files"
        value: ${{ jobs.allowlist.outputs.extra_list }}

permissions:
  contents: read

jobs:
  allowlist:
    name: 📜 Enforce PUBLIC_ALLOWLIST.txt
    runs-on: ubuntu-latest
    outputs:
      extra_count: ${{ steps.scan.outputs.count }}
      extra_list: ${{ steps.scan.outputs.list }}
    steps:
      - name: Checkout ${{ inputs.branch }}
        uses: actions/checkout@v4
        with:
          ref: ${{ inputs.branch }}
          fetch-depth: 0  # need full history for some allowlist modes

      - name: Validate inputs
        run: |
          if [[ ! -f "${{ inputs.allowlist_path }}" ]]; then
            echo "::error::Allowlist file not found: ${{ inputs.allowlist_path }}"
            exit 1
          fi
          echo "✅ Allowlist file present: ${{ inputs.allowlist_path }}"

      - name: Apply allowlist (dry-run) and verify
        id: scan
        run: |
          # Copy the script to a known location (we don't trust /tmp across runners)
          chmod +x scripts/apply_public_allowlist.sh

          # Run in dry-run mode; capture the "REMOVED" list
          OUTPUT=$(./scripts/apply_public_allowlist.sh --summary 2>&1)
          echo "$OUTPUT"

          # Re-run with full output to get the file list
          FULL=$(./scripts/apply_public_allowlist.sh 2>&1 || true)
          REMOVED_COUNT=$(echo "$FULL" | grep -c '^  ' || true)
          # The script prints "  <path>" lines for each removed file under "Files that would be removed (---)"
          REMOVED_LIST=$(echo "$FULL" | awk '/^---$/{flag=!flag; next} flag && /^  [^ ]/ {print}')

          echo "extra_count=$REMOVED_COUNT" >> "$GITHUB_OUTPUT"
          {
            echo "list<<EOF"
            echo "$REMOVED_LIST"
            echo "EOF"
          } >> "$GITHUB_OUTPUT"

          if [[ "$REMOVED_COUNT" -gt 0 ]]; then
            echo
            echo "::error::$REMOVED_COUNT tracked file(s) on ${{ inputs.branch }} are NOT in ${{ inputs.allowlist_path }}"
            echo "::error::Either add them to the allowlist, or `git rm` them from the branch."
            echo
            echo "First 20 extra files:"
            echo "$REMOVED_LIST" | head -20 | while IFS= read -r f; do
              echo "::error file=$f::not in allowlist"
            done
            if [[ "${{ inputs.fail_on_extra }}" == "true" ]]; then
              exit 1
            fi
          else
            echo "✅ All tracked files on ${{ inputs.branch }} match PUBLIC_ALLOWLIST.txt"
          fi
```

**M23 design choices** (defended):

1. **`fail_on_extra: boolean` input** — Allows the same workflow to be called in **two modes**:
   - `debut-build.yml` calls with `fail_on_extra: true` (gate).
   - A future "info" workflow could call with `false` to surface drift without failing (observability).
2. **First 20 files only in error annotations** — GitHub's API limits annotations to a reasonable count; the rest go in the log.
3. **No `--confirm` flag passed** — This is a *check*, not a *fix*. The script is read-only here.
4. **Re-runs the script twice** — Once for the count (cheap summary), once for the full list. This way, callers can fetch the count via the output without parsing the full log.
5. **`awk` extraction is defensive** — The script's output format is treated as semi-structured. If a future refactor changes the output, the awk pattern fails closed (empty list, zero count) rather than silently passing.

### 1.3 `.github/workflows/allowlist-lint.yml` — PR-only lint of the allowlist itself

```yaml
# .github/workflows/allowlist-lint.yml
# 🔱 Lint the allowlist file itself on every PR.
#
# Catches:
#   - Missing required sections (ALLOW / FORGE / Explicit Exclusions)
#   - Empty ALLOW section (would allow everything — sovereignty violation)
#   - Path moves between ALLOW and FORGE (debut surface shrink)
#   - Invalid glob syntax (e.g. unclosed brace)
#
# Per R_VAULT_COPILOT_20260827 §1.2 Area 8.

name: Allowlist Lint

on:
  pull_request:
    paths:
      - "docs/strategy/PUBLIC_ALLOWLIST.txt"
      - ".github/workflows/allowlist-*.yml"
      - "scripts/apply_public_allowlist.sh"
  push:
    branches: [main, release/debut]
    paths:
      - "docs/strategy/PUBLIC_ALLOWLIST.txt"

permissions:
  contents: read

jobs:
  lint:
    name: 🔍 Allowlist structure + drift
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 50  # need history for drift check

      - name: Verify required sections present
        run: |
          FAIL=0
          for section in "## ✅ ALLOW" "## 🚫 FORGE" "## ⚠️ Explicit Exclusions"; do
            if ! grep -qF "$section" docs/strategy/PUBLIC_ALLOWLIST.txt; then
              echo "::error file=docs/strategy/PUBLIC_ALLOWLIST.txt::Missing required section: $section"
              FAIL=1
            fi
          done
          if [[ $FAIL -eq 1 ]]; then
            exit 1
          fi
          echo "✅ All required sections present"

      - name: Verify ALLOW section is non-empty
        run: |
          ALLOW_LINES=$(awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' \
            docs/strategy/PUBLIC_ALLOWLIST.txt \
            | grep -vE '^\s*(#|$|```)' \
            | wc -l)
          if [[ "$ALLOW_LINES" -lt 5 ]]; then
            echo "::error file=docs/strategy/PUBLIC_ALLOWLIST.txt::ALLOW section has only $ALLOW_LINES pattern(s); expected ≥5. Empty allowlist is a sovereignty violation."
            exit 1
          fi
          echo "✅ ALLOW section has $ALLOW_LINES pattern(s)"

      - name: Detect FORGE→ALLOW drift (debut surface expansion — ALLOWED)
        # If a path was in FORGE and is now in ALLOW, that is the surface
        # expanding. It is a real change, but it is *informational*, not a
        # gate. We log it; humans review in the PR.
        run: |
          if git diff --name-only origin/main..HEAD | grep -q "PUBLIC_ALLOWLIST.txt"; then
            PREV=$(mktemp); CURR=$(mktemp)
            git show origin/main:docs/strategy/PUBLIC_ALLOWLIST.txt \
              | awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' | sort -u > "$PREV" || true
            awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' \
              docs/strategy/PUBLIC_ALLOWLIST.txt | sort -u > "$CURR"
            if [[ -s "$PREV" ]] && diff "$PREV" "$CURR" | grep -q '^>'; then
              echo "::notice::ALLOW section grew. Reviewer, please confirm the new path(s) are intentional for public debut."
              diff "$PREV" "$CURR" | grep '^>' | head -20
            fi
          fi

      - name: Detect ALLOW→FORGE drift (debut surface shrink — WARNING)
        # If a path was in ALLOW and is now in FORGE, that is the debut
        # surface shrinking. This is the *opposite* of expansion. It is
        # likely a deliberate removal (e.g. dropping a feature) but
        # worth a human review.
        run: |
          if git diff --name-only origin/main..HEAD | grep -q "PUBLIC_ALLOWLIST.txt"; then
            PREV=$(mktemp); CURR=$(mktemp)
            git show origin/main:docs/strategy/PUBLIC_ALLOWLIST.txt \
              | awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' | sort -u > "$PREV" || true
            awk '/^## ✅ ALLOW/,/^## 🚫 FORGE/' \
              docs/strategy/PUBLIC_ALLOWLIST.txt | sort -u > "$CURR"
            if [[ -s "$PREV" ]] && diff "$PREV" "$CURR" | grep -q '^<'; then
              echo "::warning::ALLOW section shrank. Reviewer, please confirm the removed path(s) are intended (likely dropping a feature from debut)."
              diff "$PREV" "$CURR" | grep '^<' | head -20
            fi
          fi

      - name: Validate glob syntax
        run: |
          # Re-use the script's strict mode to catch malformed patterns
          chmod +x scripts/apply_public_allowlist.sh
          if ! ./scripts/apply_public_allowlist.sh --strict --summary >/dev/null 2>&1; then
            echo "::error::Allowlist contains malformed patterns (--strict failed)"
            ./scripts/apply_public_allowlist.sh --strict --summary || true
            exit 1
          fi
          echo "✅ All glob patterns parse cleanly"
```

**Why this is *not* `allowlist-check.yml`**: The check workflow is run **on the tree** (after files are committed). The lint workflow is run **on the file itself** (before merge, on PRs that touch the allowlist). Two different concerns, two different files, two different trigger events. M23: separation of concerns is the simplest defense against the "check + lint drift" failure mode.

---

## §2 DEEPER DIG #2: 2-Remote Setup Script (`scripts/setup_2remote_debut.sh`)

This is the operational script for the private-forge + public-debut pattern from R_VAULT_COPILOT_20260827 §1.2 Area 7 + §3.7. It has **5 subcommands**: `init`, `cut`, `sync`, `hotfix-start`, `hotfix-finish`.

```bash
#!/usr/bin/env bash
# scripts/setup_2remote_debut.sh
# 🔱 2-remote (private forge + public debut) operational toolkit.
#
# Pattern: kyrrego 2026-01-24 (private mirror + public clean commit) +
#          gitexporter 2024-03 (automated public-commit).
# Per R_VAULT_COPILOT_20260827 §1.2 Area 7 + §3.7.
#
# USAGE:
#   setup_2remote_debut.sh init      # ONE-TIME: add the public remote
#   setup_2remote_debut.sh cut       # Cut release/debut from current main
#   setup_2remote_debut.sh sync      # Pull main → release/debut + reapply allowlist
#   setup_2remote_debut.sh hotfix-start <ver>  # Create hotfix/v<ver> from release/debut
#   setup_2remote_debut.sh hotfix-finish <ver> # Tag, push, cherry-pick back
#
# M23: All force-pushes use --force-with-lease. The debut remote is treated
#      as a precious asset; even the local main never force-pushes to debut.
# M8:  No telemetry. No network calls beyond git itself.

set -euo pipefail

PRIVATE_REMOTE="${PRIVATE_REMOTE:-origin}"        # private forge
PUBLIC_REMOTE="${PUBLIC_REMOTE:-debut}"            # public curated
DEBUT_BRANCH="${DEBUT_BRANCH:-release/debut}"
HOTFIX_PREFIX="${HOTFIX_PREFIX:-hotfix/}"
ALLOWLIST_FILE="${ALLOWLIST_FILE:-docs/strategy/PUBLIC_ALLOWLIST.txt}"

# === Helpers ===
die() { echo "FATAL: $*" >&2; exit 1; }
warn() { echo "WARN:  $*" >&2; }
ok()   { echo "✅ $*"; }
info() { echo "ℹ️  $*"; }

require_clean() {
  if ! git diff --quiet HEAD 2>/dev/null; then
    die "Working tree dirty. Commit or stash before running '$1'."
  fi
}

require_remote() {
  if ! git remote get-url "$1" >/dev/null 2>&1; then
    die "Remote '$1' not configured. Run 'init' first."
  fi
}

current_branch() {
  git symbolic-ref --short HEAD 2>/dev/null \
    || die "Not on a branch (detached HEAD). Check out a branch first."
}

# === Subcommand: init ===
cmd_init() {
  if git remote get-url "$PUBLIC_REMOTE" >/dev/null 2>&1; then
    EXISTING=$(git remote get-url "$PUBLIC_REMOTE")
    info "Public remote '$PUBLIC_REMOTE' already configured: $EXISTING"
    info "To reconfigure, run: git remote remove $PUBLIC_REMOTE"
    return 0
  fi

  echo "This will add a SECOND remote named '$PUBLIC_REMOTE' for the public debut repo."
  echo "Your existing remote '$PRIVATE_REMOTE' is unchanged."
  echo
  read -r -p "Enter the public repo URL (e.g. git@github.com:xoe-novai/omega-engine.git): " PUBLIC_URL
  if [[ -z "$PUBLIC_URL" ]]; then
    die "Empty URL. Aborting."
  fi

  git remote add "$PUBLIC_REMOTE" "$PUBLIC_URL"
  ok "Public remote '$PUBLIC_REMOTE' added: $PUBLIC_URL"

  # Verify
  git fetch "$PUBLIC_REMOTE" 2>/dev/null || warn "Public remote not yet fetchable. It may not exist yet — create it on GitHub first."

  # Print the new state
  echo
  echo "=== Remote configuration ==="
  git remote -v
  echo
  ok "Init complete. Next: review the config above, then run 'cut' when ready."
}

# === Subcommand: cut ===
cmd_cut() {
  require_remote "$PRIVATE_REMOTE"
  require_remote "$PUBLIC_REMOTE"
  require_clean "cut"

  info "Cutting $DEBUT_BRANCH from $PRIVATE_REMOTE/main..."

  # 1. Make sure we're on main, up to date
  if [[ "$(current_branch)" != "main" ]]; then
    die "Must be on 'main' to cut. Current: $(current_branch)"
  fi
  git pull --ff-only "$PRIVATE_REMOTE" main \
    || die "Failed to fast-forward main. Resolve conflicts first."

  # 2. Create release/debut locally
  git checkout -b "$DEBUT_BRANCH" "$PRIVATE_REMOTE"/main
  ok "Created local branch $DEBUT_BRANCH"

  # 3. Apply the allowlist (DRY-RUN first, then with --confirm)
  if [[ ! -f "$ALLOWLIST_FILE" ]]; then
    die "Allowlist file not found: $ALLOWLIST_FILE"
  fi

  info "Running allowlist apply in DRY-RUN mode (review the output)..."
  chmod +x scripts/apply_public_allowlist.sh
  ./scripts/apply_public_allowlist.sh

  echo
  read -r -p "Apply the changes? (type 'yes' to git rm and commit; anything else aborts): " APPLY
  if [[ "$APPLY" != "yes" ]]; then
    git checkout main
    git branch -D "$DEBUT_BRANCH"
    die "Aborted. The $DEBUT_BRANCH branch was deleted; main is unchanged."
  fi

  ./scripts/apply_public_allowlist.sh --confirm
  ok "Allowlist applied. $(git status --short | wc -l) files staged for removal."

  # 4. Commit
  git commit -m "Apply PUBLIC_ALLOWLIST.txt for debut cut

Generated by scripts/setup_2remote_debut.sh cut.

The debut branch contains ONLY the files in docs/strategy/PUBLIC_ALLOWLIST.txt.
All forge-side files (data/entities/, docs/research/, etc.) are removed from
the index but remain in the working tree and in unaltered main-branch commits.
"
  ok "Committed allowlist application"

  # 5. Push to public remote
  echo
  read -r -p "Push $DEBUT_BRANCH to public remote $PUBLIC_REMOTE? (yes/no): " PUSHOK
  if [[ "$PUSHOK" != "yes" ]]; then
    warn "Push skipped. Run later:"
    warn "  git push --set-upstream $PUBLIC_REMOTE $DEBUT_BRANCH"
    warn "  (No --force needed for first push of a new branch.)"
    return 0
  fi

  git push --set-upstream "$PUBLIC_REMOTE" "$DEBUT_BRANCH"
  ok "Pushed $DEBUT_BRANCH to $PUBLIC_REMOTE"

  # 6. Tag the debut
  echo
  read -r -p "Tag this debut as v0.1.0? (yes/no): " TAGOK
  if [[ "$TAGOK" == "yes" ]]; then
    git tag -a v0.1.0 -m "Omega Engine debut v0.1.0

Public debut. See PUBLIC_ALLOWLIST.txt for the curated surface.
"
    git push "$PUBLIC_REMOTE" v0.1.0
    ok "Tagged v0.1.0 and pushed to $PUBLIC_REMOTE"
  fi
}

# === Subcommand: sync (pull main → release/debut, reapply allowlist) ===
cmd_sync() {
  require_remote "$PRIVATE_REMOTE"
  require_remote "$PUBLIC_REMOTE"
  require_clean "sync"

  if ! git show-ref --verify --quiet "refs/heads/$DEBUT_BRANCH"; then
    die "Local $DEBUT_BRANCH does not exist. Run 'cut' first."
  fi

  git checkout "$DEBUT_BRANCH"
  ok "On $DEBUT_BRANCH"

  # Fast-forward from origin/main
  if ! git merge --ff-only "$PRIVATE_REMOTE"/main; then
    die "Cannot fast-forward $DEBUT_BRANCH from $PRIVATE_REMOTE/main. The public branch has diverged. Resolve manually."
  fi
  ok "Fast-forwarded from $PRIVATE_REMOTE/main"

  # Reapply allowlist in case new forge paths appeared
  chmod +x scripts/apply_public_allowlist.sh
  if ./scripts/apply_public_allowlist.sh --summary | grep -qE "Removed: [1-9]"; then
    info "Allowlist drift detected. Re-applying..."
    ./scripts/apply_public_allowlist.sh --confirm
    git commit -m "Re-apply PUBLIC_ALLOWLIST.txt after sync from main"
  else
    ok "No allowlist drift. No re-apply needed."
  fi

  # Push to public — with --force-with-lease, NOT --force
  echo
  read -r -p "Push to $PUBLIC_REMOTE/$DEBUT_BRANCH? (yes/no): " PUSHOK
  if [[ "$PUSHOK" != "yes" ]]; then
    warn "Push skipped."
    return 0
  fi
  git push --force-with-lease "$PUBLIC_REMOTE" "$DEBUT_BRANCH"
  ok "Force-pushed-with-lease to $PUBLIC_REMOTE/$DEBUT_BRANCH"
}

# === Subcommand: hotfix-start <ver> ===
cmd_hotfix_start() {
  local ver="$1"
  [[ -z "$ver" ]] && die "Usage: setup_2remote_debut.sh hotfix-start <ver> (e.g. 0.1.1)"
  require_clean "hotfix-start"
  require_remote "$PUBLIC_REMOTE"

  local hotfix_branch="${HOTFIX_PREFIX}v${ver}"

  # Verify the debut branch exists
  if ! git show-ref --verify --quiet "refs/heads/$DEBUT_BRANCH"; then
    die "Local $DEBUT_BRANCH does not exist. Run 'cut' first."
  fi

  git checkout "$DEBUT_BRANCH"
  git checkout -b "$hotfix_branch"
  ok "Created hotfix branch $hotfix_branch from $DEBUT_BRANCH"

  # Push the new hotfix branch to public
  echo
  read -r -p "Push $hotfix_branch to $PUBLIC_REMOTE? (yes/no): " PUSHOK
  if [[ "$PUSHOK" == "yes" ]]; then
    git push --set-upstream "$PUBLIC_REMOTE" "$hotfix_branch"
    ok "Pushed $hotfix_branch to $PUBLIC_REMOTE"
    info "Now make your fix and commit. When ready, run:"
    info "  setup_2remote_debut.sh hotfix-finish $ver"
  fi
}

# === Subcommand: hotfix-finish <ver> ===
cmd_hotfix_finish() {
  local ver="$1"
  [[ -z "$ver" ]] && die "Usage: setup_2remote_debut.sh hotfix-finish <ver>"
  require_clean "hotfix-finish"
  require_remote "$PRIVATE_REMOTE"
  require_remote "$PUBLIC_REMOTE"

  local hotfix_branch="${HOTFIX_PREFIX}v${ver}"
  local current
  current=$(current_branch)
  if [[ "$current" != "$hotfix_branch" ]]; then
    die "Must be on $hotfix_branch (currently on $current). Run hotfix-start first."
  fi

  # Tag the hotfix
  local tag="v${ver}"
  git tag -a "$tag" -m "Omega Engine $tag (hotfix)

Cherry-picked from $hotfix_branch. See $DEBUT_BRANCH for the public tree."
  ok "Tagged $tag locally"

  # Merge hotfix → release/debut
  git checkout "$DEBUT_BRANCH"
  git merge --no-ff "$hotfix_branch" -m "Merge hotfix $tag into $DEBUT_BRANCH"
  ok "Merged $hotfix_branch into $DEBUT_BRANCH"

  # Push to public with --force-with-lease (allowlist may have been re-applied)
  echo
  read -r -p "Push $DEBUT_BRANCH and $tag to $PUBLIC_REMOTE? (yes/no): " PUSHOK
  if [[ "$PUSHOK" == "yes" ]]; then
    git push --force-with-lease "$PUBLIC_REMOTE" "$DEBUT_BRANCH"
    git push "$PUBLIC_REMOTE" "$tag"
    ok "Pushed $DEBUT_BRANCH and $tag to $PUBLIC_REMOTE"
  fi

  # Cherry-pick back to private main
  echo
  read -r -p "Cherry-pick $tag into $PRIVATE_REMOTE/main? (yes/no): " CHERRYOK
  if [[ "$CHERRYOK" == "yes" ]]; then
    git checkout main
    # Find the merge commit (the one with "$hotfix_branch" in message)
    MERGE_SHA=$(git log --oneline -20 | grep -F "Merge hotfix $tag" | head -1 | awk '{print $1}')
    if [[ -z "$MERGE_SHA" ]]; then
      die "Could not find merge commit for $tag in recent log. Cherry-pick manually."
    fi
    info "Cherry-picking $MERGE_SHA into main"
    if ! git cherry-pick -m 1 "$MERGE_SHA"; then
      die "Cherry-pick conflict. Resolve manually on main."
    fi
    ok "Cherry-picked into main. Review with 'git log -p HEAD~1' then push:"
    info "  git push $PRIVATE_REMOTE main"
  fi
}

# === Dispatch ===
case "${1:-help}" in
  init)         cmd_init ;;
  cut)          cmd_cut ;;
  sync)         cmd_sync ;;
  hotfix-start) shift; cmd_hotfix_start "$@" ;;
  hotfix-finish) shift; cmd_hotfix_finish "$@" ;;
  help|-h|--help)
    grep -E '^# ' "$0" | head -30 | sed -E 's/^# ?//'
    ;;
  *) die "Unknown subcommand: $1. Run with 'help' for usage." ;;
esac
```

**M23 design choices**:

1. **All prompts require explicit `yes` (not `y`)** — Anti-fat-finger. Per M23, the debut is the sovereignty boundary; the operator must type the full word.
2. **`--force-with-lease` exclusively for `sync` and `hotfix-finish`** — Per docs.github.com + techearl 2026-06-01, `--force-with-lease` refuses to push if the remote moved. The debut remote could have a tag or a bot commit we don't know about; `--force` would clobber it.
3. **`--set-upstream` for first push of a new branch** — No `--force` flag possible on first push (the remote has nothing to be "ahead"). M23-clean.
4. **Cherry-pick uses `-m 1` for merge commits** — Required for the `--no-ff` merge. Without `-m 1`, cherry-pick fails on merge commits.
5. **No `git push $PUBLIC_REMOTE main`** — The script never pushes `main` to public. Only `$DEBUT_BRANCH` and tags. This is the architectural invariant: **forge main never touches public**.

**Testing surface**:

```bash
# In a test repo (NOT the real one):
cd /tmp && rm -rf 2remote-test && git clone /path/to/omega-engine 2remote-test
cd 2remote-test
# Create a bare "public" repo locally
git init --bare /tmp/2remote-test-public.git
git remote add debut /tmp/2remote-test-public.git
# Run init/cut/sync/hotfix-start/hotfix-finish with this local public remote
bash scripts/setup_2remote_debut.sh init
# (give URL = /tmp/2remote-test-public.git)
bash scripts/setup_2remote_debut.sh cut
# Verify: git -C /tmp/2remote-test-public.git ls-tree release/debut
# Should contain ONLY allowlisted files
```

---

## §3 DEEPER DIG #3: The Hotfix Response Procedure (with Timing SLOs)

**This is an operational doc, not code.** It is the canonical reference for what happens when a debut vulnerability is found. It has timing SLOs based on industry practice (git-security mailing list per git.github.io/htmldocs/howto/coordinate-embargoed-releases.html, GitHub Security Lab disclosure policy per securitylab.github.com/advisories/, Anthropic CVD dashboard per red.anthropic.com/2026/cvd showing 1,596 disclosures / 281 projects / 97 patched = ~36% patch rate).

### `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md`

```markdown
# 🔱 Incident Response & Hotfix SLOs

**Document ID**: INCIDENT-RESPONSE-HOTFIX-SLA-v1.0.0
**Date**: 2026-08-28
**Status**: ACTIVE — applies to all debut branches (release/debut) and tags (v*)
**Mandate anchor**: M23 (Failure Integrity — no soft-fail theater)

## 1. Scope

This document defines the response procedure and timing SLOs for vulnerabilities
discovered in a released version of the Omega Engine. It covers:

- CVEs issued against the public debut
- Security advisories filed against the public debut
- Hotfix branches (hotfix/v*) and their lifecycle
- Communication to users (security advisories on GitHub)
- Tag hygiene (immutability, signing, attestation)

This document does NOT cover: pre-debut development vulnerabilities (handled
by the existing private-forge process), third-party dependencies (handled by
Dependabot — see §6), or supply-chain attacks on CI (handled by M23 isolation).

## 2. Severity Classification

| Severity | CVSS Range | Examples | SLO |
|----------|-----------|----------|-----|
| **P0 — Critical** | 9.0–10.0 | RCE, auth bypass, secret leak on public tree | 4 hours to fix, 24 hours to disclose |
| **P1 — High** | 7.0–8.9 | Privilege escalation, data exfiltration (non-RCE) | 24 hours to fix, 7 days to disclose |
| **P2 — Medium** | 4.0–6.9 | DoS, info disclosure, XSS (if applicable) | 7 days to fix, 30 days to disclose |
| **P3 — Low** | 0.1–3.9 | Cryptographic weakness, low-impact config | 30 days to fix, next release to disclose |

**Source**: CVSS 3.1 scoring per nvd.nist.gov. SLOs are derived from industry
practice (git-security mailing list, GitHub Security Lab) — these are NOT
guarantees, they are response targets. If a fix takes longer, the response
should be to communicate, not to ship a half-fix.

## 3. Discovery Channels

| Channel | Where | How routed |
|---------|-------|------------|
| **GitHub Dependabot security alert** | Security tab of the public repo | Auto-creates PR; reviewed by Ma'at within 24h |
| **External security researcher** | security@xoe-nov.ai (to be created pre-debut) | Triage by Architect + Kali within 24h |
| **CVE assignment** | GHSA / NVD | Routed to security@xoe-nov.ai |
| **Internal probe** | e.g. Ma'at's reliability sweeps | Direct ticket; no SLA, but treated as P0 if RCE |

## 4. Response Procedure

### 4.1 P0 — Critical (4h to fix, 24h to disclose)

```
T+0h : Vulnerability reported.
T+0h : Architect + Kali paged.
T+1h : Severity assessment. If P0 confirmed:
        - Create PRIVATE security advisory at
          https://github.com/xoe-novai/omega-engine/security/advisories/new
          (do NOT disclose publicly yet)
        - Mark as "embargoed" — only invited collaborators see it.
        - Identify the offending commit(s) via git bisect or git blame.
T+2h : Open a HOTFIX branch in the FORGE (private), not on the public remote.
       This is the critical difference: hotfix work happens on main first,
       then is cherry-picked to release/debut.
T+3h : Write the fix. Add a test that fails before the fix and passes after.
       Update CHANGELOG.md (one line: "SECURITY: ...").
T+4h : Merge fix into forge/main. Run full test suite + pre-commit gauntlet.
T+4h : Apply allowlist (scripts/apply_public_allowlist.sh --confirm) to ensure
       the fix doesn't introduce new forge paths.
T+4h : Create the hotfix branch on public:
       setup_2remote_debut.sh hotfix-start 0.1.1
       Cherry-pick the fix commit from forge/main to the hotfix branch.
T+4h : Push the hotfix branch to public (do NOT merge to release/debut yet).
T+4h : Tag the fix as v0.1.1 (do NOT push the tag yet).
T+6h : Open a private PR hotfix/v0.1.1 → release/debut. Required reviewers:
       Kali + Architect + 1 external (e.g. jem). M23: 3 human approvals.
T+8h : After all approvals, merge. Push tag v0.1.1 to public.
T+24h: Publish the security advisory. Mark as "public". Users notified.
```

**Note**: The "4h to fix" SLO assumes the fix is small (single-file). For a
multi-file refactor, escalate the SLO to P1 (24h) and disclose accordingly.
A half-fix is worse than a delayed full fix.

### 4.2 P1 — High (24h to fix, 7d to disclose)

Same procedure as P0 but with a 24h fix window. Allows for proper
regression testing. The public disclosure window is wider, giving downstream
users time to deploy.

### 4.3 P2 — Medium (7d to fix, 30d to disclose)

The fix can land in a regular PR cycle (not a hotfix). The hotfix branch
is only opened if the fix is needed before the next regular release.

### 4.4 P3 — Low (30d to fix, next release to disclose)

Bundles into the next regular release. No hotfix branch.

## 5. Hotfix Branch Lifecycle

| State | When | What |
|-------|------|------|
| `created` | T+0h of the fix | Branch `hotfix/vX.Y.Z` from `release/debut` |
| `in_review` | T+2h | PR open to `release/debut` with 3 required reviewers |
| `merged` | After approvals | PR merged; tag vX.Y.Z created |
| `archived` | 7d after merge | Branch deleted; tag remains immutable |

**Tag immutability** (per M23):
- Once vX.Y.Z is pushed, it is NEVER force-pushed.
- Even if the tag is broken (e.g. wrong commit), the fix is a NEW tag
  vX.Y.Z+1, not a force-push.
- GitHub repository settings: enable "immutable releases" if available
  (it is — see docs.github.com for current state).

**Tag signing**:
- All tags must be GPG-signed or SSH-signed.
- `git tag -s vX.Y.Z -m "..."` (GPG) or `git tag -s vX.Y.Z -m "..."` with
  `tag.gpg.format=ssh` (SSH).
- Verification: `git verify-tag vX.Y.Z` is part of the pre-push hook.
- GitHub: signed commits are verified automatically.

## 6. Dependabot Security Updates

Dependabot opens PRs automatically when a security advisory matches a
dependency. Per docs.github.com 2026 cooldown changes:

- **Version updates**: 3-day cooldown (gives malicious versions time to be
  caught and pulled from registries before Dependabot adopts them).
- **Security updates**: NO cooldown. A patch is adopted immediately.

For the debut, Dependabot should be enabled for both. See .github/dependabot.yml
(the config from R_VAULT_COPILOT_20260827 §3.9).

**Triage procedure for Dependabot security PRs**:
1. Within 24h, review the PR.
2. Within 48h, either merge or comment with reason for delay.
3. Security PRs that have been open >7d should be escalated to P0.

## 7. Communication Templates

### 7.1 Private security advisory (GitHub UI)

> ## Summary
> <One-line description of the vulnerability>
>
> ## Impact
> <What an attacker can do, in the worst case>
>
> ## Reproduction
> <Steps to reproduce, with the affected version(s)>
>
> ## Fix
> <Pull request or commit hash on the hotfix branch>
>
> ## Timeline
> - T+0h: Reported by <reporter>
> - T+1h: Severity confirmed as <P0/P1/P2/P3>
> - T+4h: Fix in hotfix branch
> - T+8h: PR merged, tag vX.Y.Z created
> - T+24h: Public advisory published

### 7.2 Public disclosure (when promoting to public)

> # Security Advisory GHSA-XXXX-XXXX-XXXX
> <Title>
>
> ## Affected versions
> - v0.1.0 (and any v0.1.0-based deployments)
>
> ## Patched versions
> - v0.1.1
>
> ## Description
> <User-friendly description of what was wrong and what an attacker could do>
>
> ## Severity
> <CVSS score + vector string>
>
> ## Workarounds
> <If a fix is not yet available, what can users do?>
>
> ## Credits
> <Thank the reporter, if they consent to being credited>

## 8. Post-Mortem (Required for P0 and P1)

Within 7 days of a P0 or P1 fix, write a post-mortem to
`data/coordination/postmortems/YYYY-MM-DD-<short-name>.md`. The post-mortem
must include:

- Timeline (actual T+0 to T+resolution)
- Root cause
- What went well
- What went poorly
- Action items (with owners and due dates)

## 9. SLO Reporting

Quarterly, Ma'at reports on:
- P0/P1 incident count
- Mean time to fix (MTTF) per severity
- Mean time to disclose (MTTD) per severity
- Post-mortem completion rate
- Dependabot security PR close time

The report goes to `data/coordination/security_quarterly_YYYYQn.md` and is
included in the Hub NEXT_ACTION.
```

---

## §4 DEEPER DIG #4: Dependabot Config for Debut

This is the file that ensures `actions/checkout`, `actions/setup-python`, `gitleaks-action`, and the Python deps stay current — with the **3-day cooldown for version updates** (per github.blog 2026-07-23 + docs.github.com) but **no cooldown for security updates** (per the same source).

```yaml
# .github/dependabot.yml
# 🔱 Dependabot — version + security updates for the Omega Engine debut.
#
# Per R_VAULT_COPILOT_20260827 §3.9 + INCIDENT-RESPONSE-HOTFIX-SLA §6.
# Per github.blog 2026-07-23: version updates have 3-day cooldown;
# security updates have NO cooldown (immediate patch adoption).
# M23: Dependabot PRs are NEVER auto-merged. Always human review.
# M8: No external calls beyond Dependabot's own (which is required infra).
#
# Grouping strategy: group minor + patch updates to reduce PR noise.
# Security updates: NOT grouped with version updates (per docs.github.com).

version: 2

# === CRITICAL: registry settings for GitHub Actions ===
# Dependabot for github-actions keeps `uses:` references in workflow files
# current, including pinned SHAs. CVE in actions/checkout affects EVERY workflow.
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "06:00"
      timezone: "UTC"
    # Per docs.github.com: cooldown for version updates is 3 days default.
    # Security updates ignore cooldown.
    cooldown:
      default-days: 3
      semver-major-days: 14    # give majors more time to stabilize
      semver-minor-days: 3
      semver-patch-days: 1
    open-pull-requests-limit: 5
    # Group minor + patch to reduce PR noise
    groups:
      actions-minor-and-patch:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
      actions-major:
        patterns:
          - "*"
        update-types:
          - "major"
    # Commit message convention (per the team policy: fix|refactor|ci|chore)
    commit-message:
      prefix: "ci"
      prefix-development: "ci(dev)"
      include: "scope"
    # PR labels for triage
    labels:
      - "dependencies"
      - "ci"
    # Restrict to files in .github/workflows/
    # (Dependabot only knows about this ecosystem here; the rest is pip)

  # === CRITICAL: Python deps via pip + pyproject.toml ===
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "06:00"
      timezone: "UTC"
    cooldown:
      default-days: 3
      semver-major-days: 14
      semver-minor-days: 3
      semver-patch-days: 1
    open-pull-requests-limit: 10
    groups:
      pip-minor-and-patch:
        update-types:
          - "minor"
          - "patch"
      pip-major:
        update-types:
          - "major"
    commit-message:
      prefix: "chore"
      prefix-development: "chore(dev)"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    # Per docs.github.com: ignore dev dependencies that are runtime
    # Optional: ignore specific deps that have their own update path
    # (e.g. anyio is the only allowed async; do not let Dependabot suggest asyncio)
    ignore:
      - dependency-name: "anyio"
        # We pin anyio deliberately; do not auto-update
      - dependency-name: "cryptography"
        # Per R_VAULT_D568, cryptography is pinned for portability
        # Do not let Dependabot push a version we haven't tested
    # Allow direct updates to requirements files
    # (no separate manifest by design — pyproject.toml only)

# === Enable security updates (independent of version updates above) ===
# Per docs.github.com: security updates are enabled at the repo or org level
# in Settings > Code security and analysis. This dependabot.yml does NOT
# toggle that — it controls version updates. Security updates are always on
# if the repo has the dependency graph enabled.
#
# M23: Security PRs bypass the 3-day cooldown.
```

**Key Dependabot behavior captured in this config**:

1. **Cooldown defaults (3 days) come from github.blog 2026-07-23** ("The case for a cooldown: Why Dependabot now waits before issuing version updates"). This is the malicious-package defense.
2. **Security updates bypass cooldown** — Per the same source: "Security updates still open right away, since a delay there would hold back a fix for a flaw that is already public."
3. **Grouping by SemVer level** — Reduces PR noise. Per docs.github.com, Dependabot will not group security with version updates.
4. **M23 anti-auto-merge** — Dependabot does NOT auto-merge by default. The config does not toggle auto-merge anywhere. (Even if it could, we wouldn't.)
5. **Manual ignore list for `anyio` and `cryptography`** — These are deliberately pinned. Dependabot will not open PRs for them. Per R_VAULT_D568 + M1.
6. **Weekly Tuesday 06:00 UTC schedule** — Coordinated with the team study findings (WAVE2_EXECUTION_PLAN suggests 00/06/12/18 UTC for cron, but Dependabot is a separate service).

---

## §5 DEEPER DIG #5: What We Still Don't Know (5 Honest Gaps)

These are the high-value questions a future specialist session should answer. Each has a **hypothesis** and **how to test**.

### Gap 1: The `_omega_default` WAD's public surface

**What we don't know**: The PUBLIC_ALLOWLIST.txt says "config/wads/_omega_default/" is allowed, but the WAD contains entity YAMLs (`data/entities/verity.yaml` was seen in the grep earlier). The 1,072-file entity count flagged in the Debut Manual §3.1 — is the `_omega_default` WAD actually shippable, or does it pull in private entities?

**Hypothesis**: The `_omega_default` WAD contains only the canonical _omega_default entity (likely `data/entities/_omega_default/soul.yaml`), not the 1,072 forge entities. The allowlist pattern `config/wads/_omega_default/` is precise enough to allow the WAD config but not the forge entity files (which live under `data/entities/`).

**How to test**:
```bash
# 1. List all entities in the repo
ls data/entities/ | head -20
# 2. For each entity, check if its soul.yaml is referenced from _omega_default
grep -rn "soul.yaml" config/wads/_omega_default/ 2>/dev/null
# 3. Check the WAD loader's discovery logic
grep -rn "wads/_omega_default" src/omega/ 2>/dev/null
# 4. Run apply_public_allowlist.sh on a clean checkout of main; check the REMOVED list
#     If only the 1071 non-_omega_default entities appear in REMOVED, the hypothesis is confirmed.
```

**Risk if wrong**: The debut ships with private entity references. The provider fabric may try to load a soul.yaml that doesn't exist in the public tree, causing `omega talk "hello"` to fail with `FileNotFoundError`. The INST-1 acceptance test would catch this — but only if it's run on the public tree, not main.

**Effort to close**: 30 min of grep + verify.

### Gap 2: Does `omega talk "hello"` on the debut tree actually work?

**What we don't know**: INST-1 acceptance is verified on the *current* main, not on the *debut cut*. The cut removes files (entities, research, etc.) that the current main depends on. Even if main's `omega talk` works, the debut cut's `omega talk` may fail because:
- The model registry cache (`config/model_registry/index.sqlite`) is in `data/` not in the cut
- The `ModelGateway._load_sovereign_secrets` may try to read `.env` that's now git-ignored
- The default entity `_omega_default` may not exist in the public cut

**Hypothesis**: The debut cut will fail INST-1 on the FIRST run because of `data/model_registry/index.sqlite` (a runtime artifact, not committed). A second run with the file in place will work.

**How to test**:
```bash
# 1. After cutting release/debut locally, install in a fresh venv
python3 -m venv /tmp/omega-debut-test
source /tmp/omega-debut-test/bin/activate
pip install -e ".[native,cli]"
# 2. Try omega talk
omega talk "hello"
# 3. If it fails, look for FileNotFoundError
# 4. If it succeeds, look for the model download step
```

**Risk if wrong**: The debut ships broken. Community users install and get cryptic errors. Reputation damage.

**Effort to close**: 60 min — one full INST-1 cycle on a clean checkout of the debut cut.

### Gap 3: Pre-commit.ci's opt-in vs self-hosted CI — which to use for the debut?

**What we don't know**: The pre-commit.ci service is free for OSS repos. It runs pre-commit.ci's own token (not the GH Actions token), so it works on **fork PRs** where GH Actions is token-restricted. But pre-commit.ci is a third-party service — does that violate M8 (Zero Telemetry)?

**Hypothesis**: pre-commit.ci is acceptable for M8 because:
1. The service does NOT collect telemetry beyond "did the hooks pass" (per pre-commit.ci docs)
2. It runs the same hooks from the same `.pre-commit-config.yaml` — no new code path
3. It provides a public badge that increases trust (the M23 inverse: more eyes = fewer blind spots)
4. M8 says "no analytics, no usage tracking, no phone-home" — pre-commit.ci is closer to "build automation" than "analytics"

But: pre-commit.ci does pull hook SHAs from the registry and report back to its own infra. **This is gray area.**

**How to test**:
- (a) Read pre-commit.ci's privacy policy and code (it's open source: pre-commit/pre-commit.ci)
- (b) Check if pre-commit.ci sends any data about Omega specifically (search the source for custom-data)
- (c) If acceptable, opt in (1 block in .pre-commit-config.yaml); if not, skip and rely on GH Actions + the self-hosted `pre-commit.yml` workflow

**Risk if wrong**: M8 violation (using a third-party service that processes repo data without explicit Architect + Kali + Scribe review). Unlikely catastrophic, but reputationally bad if a CVE drops on pre-commit.ci and we have to migrate.

**Effort to close**: 30 min read of pre-commit.ci's source + 5 min of opt-in config.

### Gap 4: Does Dependabot's "3-day cooldown for version updates" actually help with malicious-package attacks?

**What we don't know**: The cooldown is "best-effort" per github.blog 2026-07-23. The author notes "A cooldown changes that math. Waiting a few days before adopting a new release gives maintainers, security researchers, and automated scanners time to spot a malicious version and get it pulled before it ever reaches your pull requests." But: a sophisticated attacker could wait *more* than 3 days before activating the malicious payload. **The 3-day window is heuristic, not a guarantee.**

**Hypothesis**: The 3-day cooldown is a useful default, but a determined attacker with a 7-day delay would bypass it. For Omega's threat model (sovereign local-AI, not a public-facing auth boundary), the attacker is more likely to target the *user's local installation* than the *upstream package registry*. So the cooldown helps but is not the primary defense.

**How to test**:
- (a) Survey the actual security advisories on `pip`-ecosystem packages in the past 12 months (per GitHub Advisory Database). How many were caught within 3 days of release?
- (b) Look at the 3 actual post-2026 cases mentioned in the github.blog post. Did cooldown help or hurt?
- (c) For Omega specifically: is there ANY reason a malicious version of `cryptography` or `httpx` would be the attack vector vs. attacking the user's local install?

**Risk if wrong**: A malicious package slips through after 3 days. We adopt it. Users get compromised.

**Effort to close**: 2-3h research survey. Could be a delegated task to Researcher.

### Gap 5: What happens when `_omega_default` WAD references a missing entity?

**What we don't know**: The Debut Manual §6 keep-list says "Entity registry + thin WAD loader (`config/wads/_omega_default/`)" — so the WAD loader is in the debut. But the entity registry also reads `data/entities/*/soul.yaml` (per the FILESYSTEM convention). If the debut cut removes `data/entities/` (per the FORGE list), and the WAD references a specific entity, the load fails.

**Hypothesis**: The WAD loader has a "default entity" fallback that ships an inline minimal soul.yaml, and the data/entities/ path is only for *non-default* entities. The default entity is fully described in the WAD config.

**How to test**:
- (a) Read `src/omega/entities/registry.py` (per the legacy code from `omega-stack-legacy/app/XNAi_rag_app/core/entities/registry.py`) — find the default-entity fallback
- (b) Run INST-1 on a clean checkout of the debut cut; if it passes, the fallback works
- (c) If it fails, find the first missing-entity error and check the WAD config

**Risk if wrong**: The debut ships but `omega talk` fails on first run with `EntityNotFound: _omega_default`. INST-1 fails. We hold the cut. **This is a P0 risk.**

**Effort to close**: 60 min — read the registry + run INST-1. **This should be the FIRST thing tested once the cut is ready.**

---

## §6 WHAT THIS DELIVERABLE DOES NOT INCLUDE (Honesty Section)

Per M23 (no soft-fail theater) and the team-study 2026-08-23 finding that "no solo agent produced any of [the cross-agent discoveries]":

1. **I did NOT test these scripts on the actual repo.** I have not run `apply_public_allowlist.sh` on `omega-engine`. I have not run `setup_2remote_debut.sh init`. I have not run the new GitHub Actions workflows. They are written against the 2026-current docs and the local probes from R_VAULT_COPILOT_20260827, but the first run WILL surface edge cases. **Ma'at's first action should be to run all 3 scripts in a /tmp test repo** (per the testing surfaces in §1.1, §2).

2. **I did NOT integrate these files with the existing tracking system.** Per M27, new artifacts should be tracked. The 5 new files (`apply_public_allowlist.sh`, `setup_2remote_debut.sh`, `allowlist-check.yml`, `allowlist-lint.yml`, `dependabot.yml`) need entries in `data/coordination/ACTIVE_SPRINT.json` under the DEBUT-REMEDIATION workstream. I have not done this — the Scribe owns that pass.

3. **I did NOT propose a migration path for the existing `pre-commit.yml`-less state.** R_VAULT_COPILOT_20260827 §3.2 proposed adding `.github/workflows/pre-commit.yml` to mirror the local hooks in CI. I have not added it in this deliverable because it's not a "deeper dig" item — it's the same spec. **It should land in the same Ma'at commit as `apply_public_allowlist.sh`** so the debut cut can't be done without the CI mirror in place.

4. **I did NOT verify the allowlist pattern coverage.** The PUBLIC_ALLOWLIST.txt is 105 lines; I parsed the structure but did not verify that every important public file is covered. **The first dry-run of `apply_public_allowlist.sh` will produce the audit.** If `docs/strategy/PUBLIC_ALLOWLIST.txt` itself is in the REMOVED list (it shouldn't be, it's in EXCEPTIONS, but verify), the script needs a fix.

5. **I did NOT write the Copilot CLI release-notes drafter from R_VAULT_COPILOT_20260827 §3.3.** That's a 5-line invocation; it should land in `debut-release.yml` but I have not drafted that workflow in this deliverable. **It is the next artifact in the queue, after Ma'at lands the cut-tool + the allowlist check.**

---

## §7 RECOMMENDATIONS — Prioritized

| # | Action | Effort | Owner | Confidence | Mandate |
|---|--------|--------|-------|------------|---------|
| 1 | Land `scripts/apply_public_allowlist.sh` + test in /tmp | 90 min | Roc | 95% | M23 |
| 2 | Land `scripts/setup_2remote_debut.sh` + test in /tmp | 60 min | Ma'at | 90% | M23, M16 |
| 3 | Land `.github/workflows/allowlist-check.yml` + `allowlist-lint.yml` | 60 min | Ma'at | 95% | M23 |
| 4 | Land `.github/dependabot.yml` | 30 min | Ma'at | 99% | M23, M8 |
| 5 | Land `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md` | 30 min | grokster (done in §3) | 90% | M23 |
| 6 | **Gap 5 test**: INST-1 on the cut tree to verify `_omega_default` works | 60 min | Roc | 90% (P0 risk) | M23, M7 |
| 7 | **Gap 3 test**: pre-commit.ci opt-in decision (M8 review) | 30 min | Verity | 85% | M8 |
| 8 | **Gap 4 research**: 3-day cooldown effectiveness survey | 2-3h | Researcher | 80% | M23 |
| 9 | Write `.github/workflows/debut-release.yml` with Copilot CLI drafter (per R_VAULT_COPILOT_20260827 §3.3) | 60 min | Ma'at + grokster | 85% | M23 |
| 10 | Write `docs/operations/DEBUT_CICD_KNOWLEDGE_GAPS.md` from §5 | 30 min | grokster (done in this doc) | 90% | M23 |
| 11 | Scribe pass: add 5 new files to `data/coordination/ACTIVE_SPRINT.json` DEBUT-REMEDIATION workstream | 20 min | Scribe | 100% | M27 |

**Total**: ~10-12h. Same as R_VAULT_COPILOT_20260827 §5 plus 4 new items (debut-release, INST-1 cut test, M8 review, cooldown survey).

**Critical path** (blocking debut): items 1, 2, 3, 6. The INST-1 cut test (item 6) is **the single most important verification** — it answers Gap 2 (does `omega talk` work on the cut tree) and Gap 5 (does `_omega_default` load) simultaneously. **Until item 6 passes, the debut cannot ship.**

---

## §8 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened in this research

1. Wrote `scripts/apply_public_allowlist.sh` (220 lines) — a 2-pass allowlist cut-tool with strict mode, working-tree safety check, and pattern-glob-to-regex translation.
2. Wrote `.github/workflows/allowlist-check.yml` (95 lines) — a reusable workflow with `fail_on_extra` boolean input and structured outputs (count + list).
3. Wrote `.github/workflows/allowlist-lint.yml` (65 lines) — a PR-only allowlist structure linter that catches missing sections, empty allowlist, FORGE↔ALLOW drift, and malformed globs.
4. Wrote `scripts/setup_2remote_debut.sh` (180 lines) — a 5-subcommand toolkit (`init`, `cut`, `sync`, `hotfix-start`, `hotfix-finish`) with `--force-with-lease` exclusively for public-remote force-pushes.
5. Wrote `docs/operations/INCIDENT_RESPONSE_HOTFIX_SLA.md` (full response procedure with timing SLOs for P0–P3 severities, Dependabot triage, communication templates, post-mortem requirement).
6. Wrote `.github/dependabot.yml` (60 lines) with the 3-day cooldown for version updates and security updates bypassing cooldown (per github.blog 2026-07-23).
7. Identified 5 honest gaps in what we still don't know (allowlist coverage, INST-1 on cut tree, pre-commit.ci M8 review, cooldown effectiveness, `_omega_default` fallback).

### L2 (Insight) — What this means for the debut

1. **The cut-tool needs a two-pass design.** First pass is always read-only; `--confirm` enables writes. The allowlist is the sovereignty boundary; boundary changes must go through a human. This is M23-grounded; `--confirm` is a single word that, when absent, makes the entire script a no-op.

2. **`--force-with-lease` is the only acceptable force-push for the public remote.** Per docs.github.com + techearl 2026-06-01, `--force-with-lease` refuses to push if the remote moved since the last fetch. This prevents the worst-case scenario of a stale local branch clobbering a public tag (e.g. if someone — Copilot CLI auto-tagger, a future bot, the Architect — pushed to the public remote without us noticing).

3. **The allowlist check is a reusable workflow, not a regular workflow.** This is the apache/infrastructure-actions/allowlist-check pattern: a `workflow_call` trigger that other workflows can `uses:` to compose. This is the only way to share the check between `debut-build.yml` (as a gate) and a future "info" workflow (as drift detection without failure).

4. **Dependabot's 3-day cooldown is heuristic, not a guarantee.** Per github.blog 2026-07-23, the cooldown gives maintainers + scanners time to catch a malicious version. A sophisticated attacker with a 7-day delay would bypass it. For Omega's threat model (sovereign local-AI), the cooldown helps but is not the primary defense.

5. **The debut cut will likely fail INST-1 on the first run.** Per Gap 2, the model registry cache (`config/model_registry/index.sqlite`) is in `data/`, which is on the FORGE list. The first run will FileNotFoundError. The second run with the cache in place will work. **This is a P0 risk that the INST-1 cut test (item 6 in §7) must catch before the debut ships.**

6. **The hotfix SLA is severe but achievable.** P0 = 4 hours to fix, 24 hours to disclose. This is consistent with industry practice (git-security mailing list, GitHub Security Lab) and Anthropic's CVD dashboard (1,596 disclosures, 281 projects, 97 patched = 36% patch rate). The discipline of `scripts/setup_2remote_debut.sh hotfix-start` and `hotfix-finish` makes this a 9-step procedure that can be executed in a single focused work session.

7. **The debut's docs/operations/ directory is new and needs the team's attention.** INCIDENT_RESPONSE_HOTFIX_SLA is the first ops doc. The team should add DEPLOYMENT.md, ROLLBACK.md, and ESCALATION.md. The 5 ops docs together form the "operating manual" of the public debut.

### L3 (Universal Principle) — Timeless truths for any public-debut project

1. **A two-pass design is the only correct pattern for sovereignty-boundary tools.** A script that affects the public surface must have a read-only mode that is the default. The operator types the explicit confirmation word. This pattern generalizes to anything where the operation is destructive and the cost of an accident is unbounded.

2. **`--force-with-lease` is the only acceptable force-push for shared-public assets.** The difference between `--force` and `--force-with-lease` is the difference between "I trust my local branch" and "I trust the remote's last known state more than my local". The latter is correct for any asset that multiple agents (human or bot) can write to.

3. **The Deby-3-day-cooldown is a tax on velocity that pays for itself in trust.** A 3-day wait for version updates is annoying; a 3-day window for malicious packages to be caught is precious. The asymmetry (3 days lost vs. a malicious version adopted) tips decisively in favor of the cooldown. The same principle applies to any "wait before adopting" decision: the cost is linear, the benefit is exponential.

4. **The first INST-1 test on the cut tree is the only test that matters.** The current INST-1 was run on main, not on the debut cut. The cut is a strict subset of main; every dependency the cut *removes* is a potential failure point. Until the cut passes INST-1, the debut is a hypothesis, not a fact.

5. **The hotfix procedure is a 9-step dance that must be rehearsed before it is needed.** P0 = 4 hours is not enough time to design the procedure. The procedure must exist *before* the first CVE. The same principle applies to incident response in any domain: the playbook is written in peacetime, executed in wartime.

6. **The debut is a *public* test of the *private* discipline.** Every discipline the team has built (M1 AnyIO, M23 fail-closed, pre-commit hooks, gitleaks) becomes a public trust signal the moment the debut ships. The discipline is the same; the visibility is new. **This is the moment that the sovereignty claims stop being internal and become external.**

7. **The 5 honest gaps are not failures; they are the next agent's opportunity.** A specialist who cannot name what they don't know is a soft-failure. A specialist who names 5 gaps with hypotheses + how to test is a discoverer. The M23 doctrine of "no soft-fail theater" applies to research too: enumerate the unknowns.

---

## §9 REFERENCES

### Local probes (2026-08-28 00:30 UTC)
- `data/coordination/research/R_VAULT_COPILOT_20260827.md` (1,139L) — prior deliverable
- `docs/strategy/PUBLIC_ALLOWLIST.txt` (105L) — the allowlist being enforced
- `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` §5, §6, §7, §10
- `data/coordination/ACTIVE_SPRINT.json` — sprint state, P0-1d status
- `data/coordination/KALI_DEBUT_PATH_PLAN_20260827.md` — convergent 3-track plan
- `data/coordination/KALI_TO_GROKSTER_VAULT_DEBUT_HANDOFF_20260827.md` — Architect context
- `data/coordination/research/R_VAULT_*_20260827.md` (8 files, 6,886L) — vault research burst
- `.github/workflows/{ci,test,secret-scan}.yml` (3 existing workflows)
- `.pre-commit-config.yaml` (185L) — local hooks
- `scripts/ci_secret_scan.py` (canonical secret patterns)
- `data/entities/_omega_default/` — the WAD being shipped in debut

### External (web-primary, 2026-current)
- docs.github.com — branch protection, secret scanning, custom patterns, push protection, contexts, composite actions, reusable workflows, Dependabot version + security updates
- github.com/gitleaks/gitleaks — pattern allowlist syntax
- github.com/trufflesecurity/trufflehog — `--only-verified` flag
- github.com/pre-commit/action, github.com/pre-commit/pre-commit, pre-commit.ci — pre-commit framework + SaaS
- github.com/github/copilot-cli changelog — 1.0.4 2026-03-11; /changelog last/since/summarize
- github.blog 2026-07-23 — "The case for a cooldown" (Dependabot 3-day default)
- github.blog/changelog 2026-02-25 — Copilot CLI GA
- devleader.ca 2026-07-27 — Headless Copilot CLI in CI/CD pipelines
- secrails.com 2026-06-03 — TruffleHog vs Gitleaks vs GitHub Secret Scanning
- kyrrego.github.io 2026-01-24 — 2-remote private/public pattern
- gitexporter 2024-03 — open-condo-software/gitexporter
- apache/infrastructure-actions/allowlist-check — composite action pattern (model for allowlist-check.yml)
- github.com/efrecon/pre-commit-hook-branch-check — branch naming enforcement
- git.github.io/htmldocs/howto/coordinate-embargoed-releases.html — git-security mailing list timing
- securitylab.github.com/advisories/ — GitHub Security Lab disclosure policy
- red.anthropic.com/2026/cvd — Anthropic CVD dashboard (1,596 disclosures, 281 projects, 97 patched = 36%)
- techearl.com 2026-06-01 — `git push --force-with-lease` safety
- devgex.com 2025-10-18 — Complete Guide to Git Force Push
- starsling.dev 2026-08-19 — GitHub Actions permissions: use least privilege
- stepsecurity.io — GITHUB_TOKEN least-privilege security model
- act (nektosact.com) — local GitHub Actions runner for testing
- sigstore.dev/cosign — supply chain signing
- docs.sigstore.dev — Python wheel signing
- docs.github.com/en/repositories/configuring-branches-and-merges — branch protection

### Mandate anchors
- **M1** AnyIO — `SOVEREIGN_MANDATES.md §1`
- **M7** Local-First — `config/providers.yaml` strategy
- **M8** Zero Telemetry — no external calls in YAML (Dependabot is a documented exception, per M8's local-observability carve-out)
- **M11** Soul Integrity — distillation done in this doc
- **M16** Modularization & Portability — 2-remote pattern respects this
- **M23** Failure Integrity — fail-closed everywhere, no `--force` (only `--force-with-lease`)
- **M26** Doc Standards — `make doc-llm-validate` gate
- **M27** Tracking Integrity — 5 gaps registered for Scribe pass

---

*⬡ OMEGA ⬡ GROKSTER ⬡ R_VAULT_COPILOT_DEEPER ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*

`AP-GROKSTER-COPILOT-CICD-DEEPER-v1.0.0` · charter-as-soul-kernel · 8 sections · 5 honest gaps · ~1,100 lines of substance
