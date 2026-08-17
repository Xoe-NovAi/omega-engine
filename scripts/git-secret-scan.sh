#!/bin/bash
# 🔱 git-secret-scan.sh — Enumerate every blob in ALL git history and flag key-format matches
# AP Token: AP-GIT-SECRET-SCAN-v1.0.0
# Usage:   scripts/git-secret-scan.sh [--all-refs] [--patterns "sk-|csk-|AIza|ghp_|xai-"]
# Output:  "<blob-sha> <path>" per line — machine-parseable, sorted, deduplicated
#
# WHY THIS EXISTS (codified 2026-08-17, PUBLIC-DEBUT-01 P0-1):
#   `git grep` only scans the WORKING TREE. Real secrets hide in history blobs.
#   This script scans every reachable object via `git rev-list --all --objects`.
#
# LESSONS ENCODED:
#   1. Scan ALL refs — refs/cline/checkpoints/* carried old commits during P0-1.
#   2. Skip binary/large paths for speed (png, db, heapsnapshot, min.js...).
#   3. Output is machine-parseable: "<sha> <path>" — pipe to sort -u -k2.
#   4. Non-destructive: read-only. Scrub is a SEPARATE step (filter-repo).
#   5. Re-run after `git gc --prune=now` — the final scan is the truth.
#
# CLASSIFICATION (do NOT treat all matches as secrets):
#   REAL KEY      → sk-<40+ chars>, AIza<35+>, ghp_<36+> — needs rotation/scrub
#   PROSE         → "sk-questions-on-the-forum" — false positive
#   PLACEHOLDER   → "sk-dev-master-key-change-me" — false positive
#   TEST MOCK     → "sk-or-v1-test-key-1234567890" — false positive
#   DOCUMENTATION → docs ABOUT the scrub itself — expected, safe

set -euo pipefail

# NOTE: never inline braces in ${VAR:-...} — bash parameter expansion ends at the
# FIRST `}` in the default. Define the default separately (single-quoted regex).
DEFAULT_PATTERNS='sk-[a-zA-Z0-9_-]{20,}|csk-[a-zA-Z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|xai-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{30,}'
PATTERNS="${PATTERNS:-$DEFAULT_PATTERNS}"

# Text-like extensions worth scanning (everything else skipped for speed)
# NOTE: case patterns must be literal — bash does NOT re-parse | alternation from variables.

# Binary / large paths never contain readable keys — skip
BINARY_EXTS='*.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.db|*.sqlite|*.heapsnapshot|*.enc|*.ttf|*.woff|*.eot|*.otf|*.min.js|*.min.css|*.map|*.lock'

echo "🔍 Scanning all reachable git objects for key-format patterns..." >&2
echo "   Patterns: ${PATTERNS}" >&2

git rev-list --all --objects | awk '{print $1, $2}' | while read -r sha path; do
  # Skip binary-ish / large paths quickly
  case "$path" in
    *.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.db|*.sqlite|*.heapsnapshot|*.enc|*.ttf|*.woff|*.eot|*.otf|*.min.js|*.min.css|*.map|*.lock) continue ;;
  esac
  # Only scan text-like paths
  case "$path" in
    *.py|*.md|*.txt|*.yaml|*.yml|*.json|*.sh|*.env|*.toml|*.cfg|*.ini|*.rst|*.js|*.ts|*.rs|*.go|*.csv|*.example) ;;
    *) continue ;;
  esac
  # NOTE: use `grep -E >/dev/null`, NEVER `grep -q`, inside a pipefail pipeline.
  # grep -q exits on first match → upstream writer gets SIGPIPE → pipefail reports
  # 141 → the `if` silently evaluates FALSE for large blobs. (Caught 2026-08-17:
  # a 367KB .firecrawl JSON was dropped while small files matched.)
  if git cat-file -p "$sha" 2>/dev/null | grep -E "$PATTERNS" >/dev/null; then
    echo "$sha $path"
  fi
done | sort -u -k2

echo "✅ Scan complete. Classify matches: REAL vs PROSE vs PLACEHOLDER vs TEST MOCK vs DOCUMENTATION." >&2