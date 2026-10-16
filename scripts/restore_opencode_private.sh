#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Restore private .opencode/ files after a public allowlist cut
#
# Problem: apply_public_allowlist.sh removes tracked private files from the
# working tree. Files like wrapper.sh, hooks/, and opencode.json are private
# (contain session state, credentials, local agent config) and must never hit
# main — but your local OpenCode install depends on them to launch.
#
# Solution: This script restores the private files from a known-good pre-cut
# commit (58e5fe62^) into your working tree as untracked files. Safe to re-run
# anytime; idempotent; never commits anything.
#
# Usage:
#   bash scripts/restore_opencode_private.sh
#
# Files restored:
#   .opencode/wrapper.sh                    (executable, alias target)
#   .opencode/hooks/session_end.py          (wrapper dependency)
#   .opencode/agents/archive/grok_cli.md    (retired agent, kept for history)
#
# What this does NOT touch:
#   - Root opencode.json (tracked, public — grok_cli agent block already removed)
#   - Any tracked .opencode/ files (agents/, rules/, skills/ — allowlisted)
#   - Session state (.last_session.json, logs/, data/)

set -euo pipefail

SOURCE_COMMIT="58e5fe62^"  # Last commit before the public cut
PRIVATE_FILES=(
  ".opencode/wrapper.sh"
  ".opencode/hooks/session_end.py"
  ".opencode/agents/archive/grok_cli.md"
)

# NOTE: .opencode/opencode.json is intentionally NOT restored — it is dead
# weight. OpenCode reads the ROOT ./opencode.json (tracked, public), never
# .opencode/opencode.json. Restoring the old private copy caused a phantom
# "which config is real?" split. The hooks block that used to live there now
# lives in the tracked root config. Do not add it back.

echo "🔱 Restoring private .opencode/ files from ${SOURCE_COMMIT}"
echo ""

# Verify source commit exists
if ! git cat-file -e "${SOURCE_COMMIT}^{commit}" 2>/dev/null; then
  echo "❌ ERROR: Source commit ${SOURCE_COMMIT} not found in local repo"
  echo "   Expected: last commit before the public allowlist cut (58e5fe62)"
  echo "   Fix: git fetch --all or adjust SOURCE_COMMIT to a valid pre-cut commit"
  exit 1
fi

# Restore each file
for file in "${PRIVATE_FILES[@]}"; do
  if git cat-file -e "${SOURCE_COMMIT}:${file}" 2>/dev/null; then
    # Create parent directory if needed
    mkdir -p "$(dirname "$file")"

    # Restore file content
    if git show "${SOURCE_COMMIT}:${file}" > "$file" 2>/dev/null; then
      # Make wrapper.sh executable
      if [[ "$file" == *wrapper.sh ]]; then
        chmod +x "$file"
      fi

      echo "✅ $file"
    else
      echo "⚠️  Failed to restore $file"
    fi
  else
    echo "⚠️  $file not found in ${SOURCE_COMMIT} (skipping)"
  fi
done

echo ""
echo "✅ Restore complete. Private files are untracked (not staged, not committed)."
echo ""
echo "Verify:"
echo "  - bash -n .opencode/wrapper.sh              # syntax check"
echo "  - test -x .opencode/wrapper.sh              # executable"
echo "  - jq -e . opencode.json >/dev/null          # valid JSON (ROOT config — the real one)"
echo ""
echo "These files are private and will never leak to main (correctly untracked)."
