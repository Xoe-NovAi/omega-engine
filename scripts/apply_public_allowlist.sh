#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# scripts/apply_public_allowlist.sh
# 🔱 Apply PUBLIC_ALLOWLIST.txt to the current branch.
# v5 — D-565 enforcement: FORGE section now parsed as cut list
#   Round-3 (8 bugs): inline comments, fence detection, default entity, dirty-check,
#                     no-pathspec, force-with-lease, self-exemption, backtick corruption
#   Round-4 (2 bugs, Carmack's audit):
#     VULN #2: Explicit Exclusions section never parsed → default demo entity gets cut
#     VULN #6: Single-char '.' or '**' pattern silently allows everything
#   Round-5 (1 bug, Ma'at's audit, 2026-08-28):
#     D-565 GAP: FORGE section was purely documentary — vault files shipped in
#                public release because broad `src/omega/` allow matched them.
#                Now: FORGE section parsed as cut list, checked before ALLOW match.
#   Round-6 (1 bug + 1 audit, Ma'at's audit, 2026-10-03, D-610 re-cut):
#     BUG #9: `[[ ! -f "$f" ]]` guard before `git rm --cached` is FALSE for a
#            symlink-to-directory and for a dangling symlink, so removal was
#            SKIPPED for exactly those entries. `data/library` and
#            `data/memory` -> /media/arcana-novai/omega_library/... shipped in
#            the published release/debut (3c051021), leaking the account name
#            and mount layout. Now `[[ ! -e "$f" && ! -L "$f" ]]`.
#     AUDIT: symlink detection reads mode 120000 from the git INDEX, never
#            `[[ -f ]]` on the working tree. A KEPT symlink still ships as a
#            pointer to its target, so every kept symlink is now reported with
#            its target, and --strict refuses to cut while any remain.
#
# See data/coordination/research/R_VAULT_COPILOT_ROUND3_20260827.md §2
# See data/coordination/research/R_VAULT_COPILOT_ROUND4_20260828.md §1
# See data/coordination/KALI_TO_MAAT_D565_ENFORCEMENT_20260828.md
#
# USAGE:
#   scripts/apply_public_allowlist.sh              # DRY-RUN (default)
#   scripts/apply_public_allowlist.sh --confirm    # Actually git rm --cached
#   scripts/apply_public_allowlist.sh --summary    # Show counts only
#   scripts/apply_public_allowlist.sh --strict     # Refuse to run if any allowlist pattern is malformed
#   scripts/apply_public_allowlist.sh --allowlist PATH
#
# M23: Two-pass design. First pass is always read-only. --confirm is required
#      to make changes. The allowlist is the sovereignty boundary; boundary
#      changes must go through a human.
# M8: No external calls. No network. No telemetry. Pure git + awk + grep.
# M26: Compact output suitable for both human and LLM consumption.

set -euo pipefail

ALLOWLIST_FILE="${ALLOWLIST_FILE:-docs/strategy/PUBLIC_ALLOWLIST.txt}"
CONFIRM=0
SUMMARY_ONLY=0
STRICT=0
# Allow env var to override default (in addition to --allowlist arg)
ALLOWLIST_PATH="${ALLOWLIST_PATH:-$ALLOWLIST_FILE}"
# Initialize FORGE_PATTERNS early so length checks are safe
FORGE_PATTERNS=()

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

# === SAFETY (BUG #4 round-3 fix): catch untracked files too ===
if [[ "$CONFIRM" -eq 1 ]]; then
  DIRTY=$(git status --porcelain | grep -v '^??' || true)
  UNTRACKED=$(git status --porcelain | grep -c '^??' || true)
  if [[ -n "$DIRTY" ]]; then
    echo "FATAL: --confirm requires a clean working tree (no modified tracked files)." >&2
    echo "       Modified/staged tracked files:" >&2
    echo "$DIRTY" | sed 's/^/         /' >&2
    echo "       Commit or stash first, or run without --confirm for a dry-run." >&2
    echo "       (Untracked files: $UNTRACKED — these are OK.)" >&2
    exit 4
  fi
fi

# === VALIDATE allowlist file exists ===
if [[ ! -f "$ALLOWLIST_PATH" ]]; then
  echo "FATAL: allowlist file not found: $ALLOWLIST_PATH" >&2
  exit 2
fi

# === PARSE the ALLOW section ===
# v3 fix (BUG #1, #2 round-3): strip inline comments AND handle language-tagged fences.
# v4 fix (VULN #6 round-4): detect ".*" silent-allow-all patterns.
mapfile -t ALLOW_PATTERNS < <(awk '
  BEGIN { in_allow=0 }
  /^## ✅ ALLOW/ { in_allow=1; next }
  /^## 🚫 FORGE/ { in_allow=0; next }
  in_allow && /^[ \t]*[^# \t]/ {
    # v3 BUG #1 fix: strip trailing inline comments (anything from " # " to EOL)
    sub(/[ \t]+#.*$/, "")
    gsub(/^[ \t]+|[ \t]+$/, "")
    # v3 BUG #2 fix: handle both bare fences and language-tagged fences
    if ($0 ~ /^```/) next
    if ($0 == "") next
    # v4 VULN #6 fix: detect silent-allow-all patterns
    #   A pattern that is just "." (matches any single char at start)
    #   or just "**" / ".*" (matches anything) is a typo or accident.
    #   Also catch ".**" (matches any dotfile).
    #   Reject these in --strict mode; warn otherwise.
    if ($0 == "." || $0 == "*" || $0 == "**" || $0 == ".*" || $0 == ".**" || $0 == ".*/**" || $0 ~ /^\.[\*\?]+$/ || $0 ~ /^\*+$/) {
      print "WARN_VULN6:" $0 > "/dev/stderr"
      next
    }
    print
  }
' "$ALLOWLIST_PATH")

# Capture the VULN #6 warnings separately
WARN_VULN6=$(awk '
  /^## ✅ ALLOW/ { in_allow=1; next }
  /^## 🚫 FORGE/ { in_allow=0; next }
  in_allow && /^[ \t]*[^# \t]/ {
    sub(/[ \t]+#.*$/, "")
    gsub(/^[ \t]+|[ \t]+$/, "")
    if ($0 == "```" || $0 == "" || $0 ~ /^```/) next
    if ($0 == "." || $0 == "*" || $0 == "**" || $0 == ".*" || $0 == ".**" || $0 == ".*/**" || $0 ~ /^\.[\*\?]+$/ || $0 ~ /^\*+$/) {
      print $0
    }
  }
' "$ALLOWLIST_PATH")

if [[ -n "$WARN_VULN6" ]]; then
  echo "WARN: VULN #6 — silent-allow-all patterns detected in ALLOW section:" >&2
  while IFS= read -r p; do
    echo "         $p" >&2
  done <<< "$WARN_VULN6"
  echo "       These patterns would silently match ALL paths. Skipped." >&2
  if [[ "$STRICT" -eq 1 ]]; then
    echo "FATAL: --strict refuses to continue. Fix or remove these patterns." >&2
    exit 2
  fi
fi

if [[ ${#ALLOW_PATTERNS[@]} -eq 0 ]]; then
  echo "FATAL: allowlist parses to zero patterns. Check the file format." >&2
  if [[ "$STRICT" -eq 1 ]]; then exit 2; fi
fi

# === PARSE the Explicit Exclusions section (v4 VULN #2 fix) ===
# The "## ⚠️ Explicit Exclusions" section contains human-readable notes
# like "- `data/entities/_omega_default/soul.yaml` — KEEP (needed for demo)".
# These are paths that should NOT be cut, even if they're in a FORGE directory.
# Format in the file: `- <code-span>path</code-span> — reason`
# Extract the path from each line (between backticks) and add to KEPT_EXTRA.
mapfile -t KEEP_EXTRA < <(awk '
  BEGIN { in_excl=0 }
  /^## ⚠️ Explicit Exclusions/ { in_excl=1; next }
  /^## / { in_excl=0; next }
  in_excl && /^[[:space:]]*-[[:space:]]*`/ {
    # Extract path between first pair of backticks
    line = $0
    sub(/^[^`]*`/, "", line)
    sub(/`.*$/, "", line)
    gsub(/^[ \t]+|[ \t]+$/, "", line)
    if (line != "") print line
  }
' "$ALLOWLIST_PATH")

# === STRICT MODE: validate every pattern is a plausible path/glob ===
if [[ "$STRICT" -eq 1 ]]; then
  BAD=0
  for p in "${ALLOW_PATTERNS[@]}"; do
    if [[ "$p" =~ [\`\(\)\{\}\|\+\$\^\<\>\\] ]]; then
      echo "WARN: pattern uses regex metacharacter (unusual for path glob): $p" >&2
      BAD=$((BAD+1))
    fi
    # v4 VULN #6 also: in strict mode, reject any pattern that would match every path
    if [[ "$p" == "*" || "$p" == "**" || "$p" == "." || "$p" == ".*" ]]; then
      echo "FATAL: VULN #6 — pattern '$p' is silent-allow-all in strict mode" >&2
      BAD=$((BAD+1))
    fi
  done
  if [[ "$BAD" -gt 0 ]]; then
    echo "FATAL: $BAD allowlist pattern(s) failed strict validation" >&2
    exit 2
  fi
fi

# === BUILD a single anchored regex from the patterns ===
# v4 fix: do NOT escape [ ] or ^ — bash regex needs them unescaped:
#   - [ and ] for character classes (e.g. [^/] from `*` glob translation)
#   - ^ is special only at the start of a regex; we prepend our own ^
#     so any ^ in the middle of the pattern is a literal anyway.
REGEX_PARTS=()
for p in "${ALLOW_PATTERNS[@]}"; do
  regex_part=$(printf '%s' "$p" | awk '
    {
      gsub(/\*\*/, "\x01")
      gsub(/\*/, "[^/]*")
      gsub(/\?/, "[^/]")
      gsub(/\x01/, ".*")
      gsub(/[(){}+.|$\\]/, "\\\\&")
      print "^" $0
    }
  ')
  REGEX_PARTS+=("$regex_part")
done

# === PARSE the FORGE section (D-565 enforcement — v5 fix) ===
# The "## 🚫 FORGE" section lists paths that must be CUT from the public
# release, even if they fall under a broad ALLOW pattern. This closes the
# D-565 enforcement gap: previously the FORGE section was purely documentary
# and the script only cut files NOT matching any ALLOW pattern.
#
# Matching semantics: a file matches a FORGE pattern if it equals the pattern
# exactly OR starts with the pattern followed by '/'. This handles directory
# exclusions correctly: "src/omega/vault/" matches "src/omega/vault/crypto.py"
# but does NOT match "src/omega/vault_other/foo.py".
mapfile -t FORGE_PATTERNS < <(awk '
  BEGIN { in_forge=0 }
  /^## 🚫 FORGE/ { in_forge=1; next }
  /^## / { in_forge=0; next }
  in_forge && /^[ \t]*[^# \t]/ {
    # Strip trailing inline comments
    sub(/[ \t]+#.*$/, "")
    gsub(/^[ \t]+|[ \t]+$/, "")
    if ($0 ~ /^```/) next
    if ($0 == "") next
    print
  }
' "$ALLOWLIST_PATH")

# === EXCEPTIONS (v3 BUG #7 round-3 fix) ===
EXCEPTIONS=(
  ".gitignore"
  "docs/strategy/PUBLIC_ALLOWLIST.txt"
  ".github/CODEOWNERS"
  ".github/dependabot.yml"
  ".github/workflows/allowlist-check.yml"
  ".github/workflows/allowlist-lint.yml"
  "LICENSE"
  "README.md"
  "CONTRIBUTING.md"
  "AGENTS.md"
  "SOVEREIGN_MANDATES.md"
  "MANDATES_CONDENSED.md"
  "pyproject.toml"
  "Makefile"
  "scripts/apply_public_allowlist.sh"
  "scripts/setup_2remote_debut.sh"
  "scripts/install.sh"
  "$ALLOWLIST_PATH"
)

is_exception() {
  local f="$1"
  for ex in "${EXCEPTIONS[@]}"; do
    if [[ "$f" == "$ex" ]]; then return 0; fi
  done
  return 1
}

is_in_keep_extra() {
  local f="$1"
  for k in "${KEEP_EXTRA[@]:-}"; do
    if [[ -z "$k" ]]; then continue; fi
    # Translate the exclusion glob to a regex (same as ALLOW patterns)
    local kregex
    kregex=$(printf '%s' "$k" | awk '
      {
        gsub(/\*\*/, "\x01")
        gsub(/\*/, "[^/]*")
        gsub(/\?/, "[^/]")
        gsub(/\x01/, ".*")
        gsub(/[(){}+.|$\\]/, "\\\\&")
        print "^" $0
      }
    ')
    if [[ "$f" =~ $kregex ]]; then return 0; fi
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

# === FORGE match (D-565 enforcement) ===
# A file is FORGE if it equals a FORGE pattern exactly OR starts with
# a FORGE pattern followed by '/'. Directory patterns end with '/'.
is_forge() {
  local f="$1"
  for forge in "${FORGE_PATTERNS[@]:-}"; do
    if [[ -z "$forge" ]]; then continue; fi
    # Exact match OR prefix match (directory containment)
    if [[ "$f" == "$forge" || "$f" == "$forge"* ]]; then
      return 0
    fi
  done
  return 1
}

# === WALK tracked files ===
REMOVED=()
KEPT=()

# [maat 2026-10-03] Symlink detection helpers.
# `git ls-files -s` prints "<mode> <sha> <stage>\t<path>". Mode 120000 is the
# ONLY symlink mode in the git index; 100644/100755 are regular files and
# 160000 is a gitlink (submodule). A symlink must be recognised from the INDEX,
# never from `[[ -f ]]` on the working tree — that is the bug being fixed.
declare -A INDEX_MODE=()
while IFS=$'\t' read -r _meta path; do
  mode="${_meta%% *}"
  INDEX_MODE["$path"]="$mode"
done < <(git ls-files -s)

is_symlink() { [[ "${INDEX_MODE[$1]:-}" == "120000" ]]; }

index_mode_of() { printf '%s' "${INDEX_MODE[$1]:-}"; }

count_symlinks_in() {
  local arrname="$1" n=0 p
  local -n _arr="$arrname"
  for p in "${_arr[@]:-}"; do
    [[ -z "$p" ]] && continue
    if is_symlink "$p"; then n=$((n + 1)); fi
  done
  printf '%d' "$n"
}

while IFS= read -r f; do
  # Priority: exception > explicit exclusion (keep) > FORGE (cut) > allowlist (keep) > remove
  if is_exception "$f"; then
    KEPT+=("$f")
  elif [[ ${#KEEP_EXTRA[@]} -gt 0 ]] && is_in_keep_extra "$f"; then
    KEPT+=("$f")
  elif [[ ${#FORGE_PATTERNS[@]} -gt 0 ]] && is_forge "$f"; then
    # D-565: FORGE patterns cut files even if they match a broad ALLOW pattern
    REMOVED+=("$f")
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
  echo "Symlinks removed: $(count_symlinks_in REMOVED)"
  echo "Symlinks kept:    $(count_symlinks_in KEPT)"
  if [[ -n "$WARN_VULN6" ]]; then
    echo "WARN: VULN #6 patterns skipped (see warnings above)"
  fi
  if [[ ${#KEEP_EXTRA[@]} -gt 0 ]]; then
    echo "Explicit exclusions applied: ${#KEEP_EXTRA[@]}"
  fi
  if [[ ${#FORGE_PATTERNS[@]} -gt 0 ]]; then
    echo "FORGE patterns applied:     ${#FORGE_PATTERNS[@]}"
  fi
  exit 0
fi

echo "=== Allowlist Apply Report (v5 — D-565 enforcement) ==="
echo "Allowlist file:        $ALLOWLIST_PATH"
echo "ALLOW patterns found:  ${#ALLOW_PATTERNS[@]}"
echo "FORGE patterns found:  ${#FORGE_PATTERNS[@]}"
echo "Explicit exclusions:   ${#KEEP_EXTRA[@]}"
echo "Files kept:            $KEPT_COUNT"
echo "Files removed:         $REMOVED_COUNT"
echo "Total tracked:         $((KEPT_COUNT + REMOVED_COUNT))"
echo "Symlinks removed:      $(count_symlinks_in REMOVED)"
echo "Symlinks kept:         $(count_symlinks_in KEPT)"
if [[ -n "$WARN_VULN6" ]]; then
  echo "WARN: VULN #6 patterns skipped: $WARN_VULN6"
fi
echo

# === SYMLINK LEAK AUDIT ===
# [maat 2026-10-03] A symlink in the git index is stored as a blob whose CONTENT
# is the target path. Publishing it publishes the target — for `data/library`
# and `data/memory` that was `/media/arcana-novai/omega_library/...`, leaking
# the account name and the host mount layout into the public repo.
#
# The `-f` guard bug (fixed below) let REMOVED symlinks survive the cut. This
# audit closes the other half: a symlink the ALLOWLIST KEEPS still ships as a
# pointer to its target. Whether it should ship is a boundary question, not a
# mechanical one, so this audit REPORTS rather than overrides the allowlist —
# but it can no longer be silent, and `--strict` refuses to proceed while any
# remain.
SYMLINK_KEPT=()
for k in "${KEPT[@]}"; do
  if is_symlink "$k"; then SYMLINK_KEPT+=("$k"); fi
done

if [[ ${#SYMLINK_KEPT[@]} -gt 0 ]]; then
  echo "### SYMLINK LEAK AUDIT — ${#SYMLINK_KEPT[@]} symlink(s) KEPT by the allowlist"
  echo "A tracked symlink publishes its TARGET PATH verbatim. Review each:"
  for s in "${SYMLINK_KEPT[@]}"; do
    target=$(git cat-file blob ":$s" 2>/dev/null || echo "<unreadable>")
    if [[ "$target" == /* ]]; then
      echo "  LEAK  $s"
      echo "          -> $target   (absolute host path — leaks account/mount layout)"
    else
      echo "  CHECK $s"
      echo "          -> $target   (repo-relative — leaks internal layout)"
    fi
  done
  echo
  if [[ "$STRICT" -eq 1 ]]; then
    echo "FATAL: --strict refuses to cut while the allowlist keeps ${#SYMLINK_KEPT[@]} symlink(s)." >&2
    echo "       Narrow the ALLOW / Explicit-Exclusions patterns, or add the paths" >&2
    echo "       to the 🚫 FORGE section. Boundary changes need a human (M23)." >&2
    exit 2
  fi
  echo "WARN: the symlink(s) above WILL ship. Add them to 🚫 FORGE or narrow the" >&2
  echo "      Explicit Exclusions that keep them. (M23: boundary changes need a human.)" >&2
  echo
fi

if [[ "$REMOVED_COUNT" -eq 0 ]]; then
  echo "OK All tracked files match PUBLIC_ALLOWLIST.txt — no action needed."
  exit 0
fi

# v3 BUG #8 round-3 fix: use single quotes (no backtick command substitution)
echo 'Files that would be removed (would be `git rm --cached` with --confirm):'
echo "---"
for f in "${REMOVED[@]}"; do echo "  $f"; done
echo "---"
echo

if [[ "$CONFIRM" -eq 1 ]]; then
  echo "Applying (--confirm mode)..."
  for f in "${REMOVED[@]}"; do
    # [maat 2026-10-03] BUG #9 — symlink leak.
    #
    # The guard was `[[ ! -f "$f" ]]`. `-f` is FALSE for a symlink whose target
    # is a directory and for a DANGLING symlink, so the removal was silently
    # SKIPPED for exactly the entries that most need removing.
    #
    # Real impact on the published release/debut (3c051021):
    #   data/library -> /media/arcana-novai/omega_library/library-archive
    #   data/memory  -> /media/arcana-novai/omega_library/memory-archive
    # Both were classified REMOVE by this script, listed in the report, and
    # then dropped with "WARN: skip ... (not in working tree)". The symlink
    # blobs shipped publicly, leaking the account name and the mount layout.
    #
    # Fix: skip only when the path is BOTH absent AND not a symlink, so
    # regular files, directories, symlinks (live or dangling) and other
    # special entries are all handed to `git rm --cached`.
    if [[ ! -e "$f" && ! -L "$f" ]]; then
      echo "WARN: skip $f (absent from the working tree and not a symlink)" >&2
      continue
    fi
    git rm --cached "$f" >/dev/null 2>&1 || {
      echo "WARN: git rm failed for $f" >&2
    }
  done
  echo
  echo "OK $REMOVED_COUNT file(s) staged for removal."
  echo
  echo "NEXT STEPS (manual, per M23 human-in-the-loop):"
  echo "  1. git status                 # verify the staged removals"
  echo "  2. git diff --cached --stat   # confirm what is being removed"
  echo "  3. git commit -m 'Apply PUBLIC_ALLOWLIST.txt for debut cut'"
  echo "  4. scripts/setup_2remote_debut.sh cut   # push to public remote"
  exit 0
else
  echo "DRY-RUN: no changes made. Pass --confirm to actually git rm --cached."
  echo
  echo "M23 REMINDER: Review the list above. The allowlist is the sovereignty"
  echo "              boundary. Confirming removes files from the index only;"
  echo "              they remain in the working tree and in unaltered commits."
  exit 0
fi
