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
#   Round-7 (perf, Ma'at, 2026-10-04): the cut took ~19 min and is re-run on
#     every iteration of the release work. Two compounding bottlenecks, both
#     removed WITHOUT behavioural change — stdout/stderr verified byte-identical
#     against a fixture captured from v6 at HEAD (df278eb):
#       1. ~135k `awk` spawns. is_in_keep_extra() re-compiled every
#          Explicit-Exclusion glob into a regex via `printf '%s' | awk` — once
#          per pattern PER FILE (13 x 10,369 = 134,797 forks, each also paying
#          full awk startup). Every pattern is now compiled ONCE at startup by
#          glob_to_regex() in pure bash: zero forks inside the per-file loop.
#       2. ~9,000 index rewrites. The --confirm path called `git rm --cached`
#          once per removed file: 9,561 forks and 9,561 index read/write cycles.
#          Removal is now ONE `git rm --cached --pathspec-from-file=-` call fed
#          the NUL-delimited removal list (1 index write). The per-file loop is
#          retained ONLY as a diagnostic fallback, so per-file failure reporting
#          ("WARN: git rm failed for <path>") stays byte-identical; git rm is
#          transactional, so a failed batch leaves the index untouched.
#     Added --timing: per-phase wall-clock to stderr, so a slow run is
#     diagnosable without re-instrumenting.
#     glob_to_regex() reproduces the old awk translation byte-for-byte,
#     INCLUDING the pre-existing `**` -> `\.*` quirk (a literal dot, NOT "any
#     depth"). Parity verified against the awk original over 200,000 fuzzed
#     patterns — 0 divergences. Do not "fix" the quirk here; changing it would
#     silently change which files are kept.
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
#   scripts/apply_public_allowlist.sh --timing     # Print per-phase wall-clock to stderr (diagnostics)
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
TIMING=0
# Allow env var to override default (in addition to --allowlist arg)
ALLOWLIST_PATH="${ALLOWLIST_PATH:-$ALLOWLIST_FILE}"
# Initialize FORGE_PATTERNS early so length checks are safe
FORGE_PATTERNS=()

# === TIMING (round-7) ===
# Pure-bash microsecond clock — EPOCHREALTIME is a bash-5 builtin, so this
# costs no fork. Timing goes to stderr and only when --timing is passed, so
# default stdout/stderr remain byte-identical to v6.
TIMING_T0=""
_t_us() { local t="${EPOCHREALTIME/[.,]/}"; printf '%s' "$((10#$t))"; }
# _fmt_ms <microseconds> -> "12.345"
_fmt_ms() {
  local d=$(( $1 ))
  printf '%d.%03d' "$(( d / 1000000 ))" "$(( (d % 1000000) / 1000 ))"
}
# timing_mark <label> — records elapsed since the previous mark and since start
timing_mark() {
  [[ "$TIMING" -eq 1 ]] || return 0
  local now; now=$(_t_us)
  printf '  [timing] %-36s %8ss  (total %ss)\n' \
    "$1" "$(_fmt_ms $(( now - _TIMING_PREV )))" "$(_fmt_ms $(( now - TIMING_T0 )))" >&2
  _TIMING_PREV=$now
}
start_timing() {
  [[ "$TIMING" -eq 1 ]] || return 0
  TIMING_T0=$(_t_us); _TIMING_PREV=$TIMING_T0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm) CONFIRM=1; shift ;;
    --summary) SUMMARY_ONLY=1; shift ;;
    --strict) STRICT=1; shift ;;
    --timing) TIMING=1; shift ;;
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

start_timing

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

# === Precompile every glob to an anchored regex ONCE (round-7 perf) ===
#
# v4 semantics, preserved exactly: do NOT escape [ ] or ^ — bash regex needs
# them unescaped:
#   - [ and ] for character classes (e.g. [^/] from `*` glob translation)
#   - ^ is special only at the start of a regex; we prepend our own ^
#     so any ^ in the middle of the pattern is a literal anyway.
#
# The translation steps and their ORDER are load-bearing, because they mirror
# the original `printf '%s' "$p" | awk '{...}'` program that this replaces:
#   1. "**" -> 0x01 placeholder   2. "*" -> "[^/]*"   3. "?" -> "[^/]"
#   4. 0x01 -> ".*"               5. escape ( ) { } + . | $ \
# Step 4 runs BEFORE step 5, so the "." that step 4 emits is itself escaped by
# step 5: "**" yields  \.*  (a LITERAL DOT), not the ".*" that a reader would
# expect. That quirk is pre-existing behaviour baked into which files are KEPT.
# It is reproduced here deliberately. Do not reorder these steps, and do not
# "fix" step 4 — either change silently rewrites the keep/cut boundary (M23:
# the allowlist is the sovereignty boundary).
#
# Parity: this function was differentially tested against the original awk
# program over 200,000 fuzzed patterns (alphabet includes * ? . / \ ( ) { } +
# | $ [ ] ^ and spaces) — 0 divergences.
glob_to_regex() {
  local p="$1" out='' i=0 n c
  # Characters escaped by awk step 5. Note '\' is tested separately below
  # because a backslash inside a bash case pattern needs its own quoting.
  local META='(){}+.|$'
  p="${p//\*\*/$'\x01'}"          # 1
  p="${p//\*/[^/]*}"              # 2
  p="${p//\?/[^/]}"               # 3
  p="${p//$'\x01'/.*}"            # 4
  n=${#p}
  while (( i < n )); do            # 5
    c="${p:i:1}"
    if [[ "$c" == '\' || "$META" == *"$c"* ]]; then
      out+="\\$c"
    else
      out+="$c"
    fi
    (( i++ ))
  done
  printf '^%s' "$out"
}

# Compile a whole pattern array into a parallel regex array, once.
_precompile_all() {
  local -n _src="$1" _dst="$2"
  local _p
  _dst=()
  for _p in "${_src[@]:-}"; do
    [[ -z "$_p" ]] && continue
    _dst+=( "$(glob_to_regex "$_p")" )
  done
}

# ALLOW -> REGEX_PARTS (matched with [[ =~ ]]). Compiled once, up front.
REGEX_PARTS=()
_precompile_all ALLOW_PATTERNS REGEX_PARTS
timing_mark "parse ALLOW + compile regexes (${#REGEX_PARTS[@]})"


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

# Explicit Exclusions -> KEEP_EXTRA_REGEX. Compiled once, up front (round-7).
# Previously each of the ~13 patterns was recompiled with `printf | awk` for
# EVERY candidate file: 13 x 10,369 = 134,797 awk forks. Now zero forks here.
KEEP_EXTRA_REGEX=()
_precompile_all KEEP_EXTRA KEEP_EXTRA_REGEX
timing_mark "parse FORGE/exclusions + compile (${#KEEP_EXTRA_REGEX[@]})"

is_exception() {
  local f="$1"
  for ex in "${EXCEPTIONS[@]}"; do
    if [[ "$f" == "$ex" ]]; then return 0; fi
  done
  return 1
}

is_in_keep_extra() {
  local f="$1" k
  for k in "${KEEP_EXTRA_REGEX[@]:-}"; do
    if [[ -z "$k" ]]; then continue; fi
    if [[ "$f" =~ $k ]]; then return 0; fi
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
timing_mark "read git index (git ls-files -s)"

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
timing_mark "classify ${#KEPT[@]} kept / ${#REMOVED[@]} removed"

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
  timing_mark "summary written"
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
  timing_mark "no removals; report written"
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
  #
  # [maat 2026-10-04] Round-7: that filter is applied here as a SEPARATION
  # pass, and the surviving paths are removed in ONE `git rm --cached` call.
  # The old loop forked git once per file — 9,561 forks and 9,561 index
  # read/write cycles for a typical cut.
  #
  # Paths are fed NUL-delimited (--pathspec-file-nul) so paths containing
  # spaces or newlines are passed through verbatim rather than being word
  # split. `--pathspec-from-file=-` is git's own idiom for removing more paths
  # than fit in an argument vector, and it performs exactly ONE index write.
  #
  # Paths are NOT prefixed with :(literal) and GIT_LITERAL_PATHSPECS is NOT set,
  # deliberately: the per-file `git rm --cached "$f"` this replaces used git's
  # DEFAULT pathspec semantics, so leaving the default keeps matching behaviour
  # identical rather than accidentally narrowing it.
  SKIP_ABSENT=()
  REMOVE_BATCH=()
  for f in "${REMOVED[@]}"; do
    if [[ ! -e "$f" && ! -L "$f" ]]; then
      SKIP_ABSENT+=("$f")
    else
      REMOVE_BATCH+=("$f")
    fi
  done

  # Same warning, same order, as the old in-loop `continue` branch.
  for f in ${SKIP_ABSENT[@]+"${SKIP_ABSENT[@]}"}; do
    echo "WARN: skip $f (absent from the working tree and not a symlink)" >&2
  done

  BATCH_OK=0
  if [[ ${#REMOVE_BATCH[@]} -gt 0 ]]; then
    timing_mark "partition removals (${#REMOVE_BATCH[@]} rm / ${#SKIP_ABSENT[@]} skip)"
    if printf '%s\0' "${REMOVE_BATCH[@]}" \
         | git rm --cached --pathspec-from-file=- --pathspec-file-nul >/dev/null 2>&1; then
      BATCH_OK=1
    fi
    timing_mark "batch git rm --cached (1 index write)"
  fi

  if [[ "$BATCH_OK" -eq 0 && ${#REMOVE_BATCH[@]} -gt 0 ]]; then
    # A batched `git rm` is transactional: on any error it rolls back and
    # leaves the index untouched, so re-running per file here is safe and
    # reproduces the old per-file diagnostics exactly. This is the ONLY path
    # that emits "WARN: git rm failed for <path>".
    echo "WARN: batched git rm failed; retrying per-file for diagnostics" >&2
    for f in "${REMOVE_BATCH[@]}"; do
      git rm --cached "$f" >/dev/null 2>&1 || {
        echo "WARN: git rm failed for $f" >&2
      }
    done
    timing_mark "per-file git rm fallback"
  fi

  echo
  echo "OK $REMOVED_COUNT file(s) staged for removal."
  echo
  echo "NEXT STEPS (manual, per M23 human-in-the-loop):"
  echo "  1. git status                 # verify the staged removals"
  echo "  2. git diff --cached --stat   # confirm what is being removed"
  echo "  3. git commit -m 'Apply PUBLIC_ALLOWLIST.txt for debut cut'"
  echo "  4. scripts/setup_2remote_debut.sh cut   # push to public remote"
  timing_mark "confirm: report written"
  exit 0
else
  echo "DRY-RUN: no changes made. Pass --confirm to actually git rm --cached."
  echo
  echo "M23 REMINDER: Review the list above. The allowlist is the sovereignty"
  echo "              boundary. Confirming removes files from the index only;"
  echo "              they remain in the working tree and in unaltered commits."
  timing_mark "dry-run: report written"
  exit 0
fi
