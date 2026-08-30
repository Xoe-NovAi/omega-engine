#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# scripts/setup_2remote_debut.sh
# 🔱 2-remote (private forge + public debut) operational toolkit.
# v2 — round-4 fixes per R_VAULT_COPILOT_ROUND3_20260827 §2 BUG #6:
#   - Full safety stack: fetch + pre-push audit + explicit-expected-lease
#   - The pre-push audit is the only defense that catches stale-local-main
#     clobbers (where --force-with-lease alone fails).
#
# Pattern: kyrrego 2026-01-24 (private mirror + public clean commit) +
#          gitexporter 2024-03 (automated public-commit).
# Per R_VAULT_COPILOT_20260827 §1.2 Area 7 + §3.7.
# Per R_VAULT_COPILOT_ROUND3_20260827 §4 (force-push safety matrix).
#
# USAGE:
#   setup_2remote_debut.sh init                  # ONE-TIME: add the public remote
#   setup_2remote_debut.sh cut                   # Cut release/debut from current main
#   setup_2remote_debut.sh sync                  # Pull main → release/debut + reapply allowlist
#   setup_2remote_debut.sh hotfix-start <ver>    # Create hotfix/v<ver> from release/debut
#   setup_2remote_debut.sh hotfix-finish <ver>   # Tag, push, cherry-pick back
#   setup_2remote_debut.sh pre-push-audit <remote> <branch>  # Standalone audit
#
# M23: All force-pushes use --force-with-lease=<ref>:<expected_sha>. The
#      pre-push audit is MANDATORY. The debut remote is a sovereign asset;
#      even the local main never force-pushes to debut without a human's
#      "yes" after seeing the divergence.
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
ok()   { echo "OK $*"; }
info() { echo ">>> $*"; }

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

# === THE FULL SAFETY STACK (v2) ===
# v2 BUG #6 round-3 fix: the pre-push audit is the only defense that catches
# stale-local-main clobbers. --force-with-lease alone fails 2/6 scenarios.
#
# The safety stack is: fetch → pre-push audit → require explicit "yes" →
#                      --force-with-lease=<ref>:<expected_sha>.
#
# Returns: 0 if push should proceed, 1 if user aborted.
# Usage: safe_push <remote> <branch>
safe_push() {
  local remote="$1"
  local branch="$2"
  local ref="refs/heads/$branch"

  # Step 1: Fetch to update tracking ref
  info "Fetching $remote to update tracking ref..."
  git fetch "$remote" "$branch" 2>/dev/null || warn "fetch failed (remote may not have $branch yet)"

  # Step 2: Pre-push audit (the missing piece in v1)
  echo
  echo "=== Pre-push audit: $remote/$branch ==="
  local AHEAD BEHIND DIVERGED
  AHEAD=$(git log --oneline "$remote/$branch..HEAD" 2>/dev/null || true)
  BEHIND=$(git log --oneline "HEAD..$remote/$branch" 2>/dev/null || true)
  local AHEAD_C BEHIND_C
  AHEAD_C=$(echo -n "$AHEAD" | grep -c . 2>/dev/null || echo 0)
  BEHIND_C=$(echo -n "$BEHIND" | grep -c . 2>/dev/null || echo 0)

  if [[ -n "$AHEAD" ]]; then
    echo "Commits on local (will be pushed): $AHEAD_C"
    echo "$AHEAD" | sed 's/^/    /'
  fi
  if [[ -n "$BEHIND" ]]; then
    echo "WARN: Commits on $remote (would be CLOBBERED): $BEHIND_C"
    echo "$BEHIND" | sed 's/^/    /'
  fi
  if [[ -z "$AHEAD" && -z "$BEHIND" ]]; then
    echo "  (no divergence — fast-forward or no-op)"
  fi
  echo

  # Step 3: Require explicit "yes" if divergence exists
  if [[ "$AHEAD_C" -gt 0 && "$BEHIND_C" -gt 0 ]]; then
    echo "DIVERGED: local is $AHEAD_C ahead AND $BEHIND_C behind."
    echo "This requires --force. Confirming will overwrite the remote's $BEHIND_C commit(s)."
  elif [[ "$BEHIND_C" -gt 0 ]]; then
    echo "REMOTE IS AHEAD: you have $BEHIND_C commit(s) on the remote that are NOT in your local branch."
    echo "This is unusual — the public remote has commits you don't have."
    echo "If you proceed, those commits will be CLOBBERED."
  fi

  read -r -p "Push to $remote/$branch? (type 'yes' to confirm): " PUSHOK
  if [[ "$PUSHOK" != "yes" ]]; then
    die "Aborted by user. No push performed."
  fi

  # Step 4: Push with explicit-expected-lease
  local EXPECTED
  EXPECTED=$(git rev-parse "$remote/$branch" 2>/dev/null || echo "")
  if [[ -n "$EXPECTED" ]]; then
    info "Pushing with --force-with-lease=$ref:$EXPECTED"
    git push --force-with-lease="$ref:$EXPECTED" "$remote" "$branch"
  else
    info "Remote has no $branch yet — pushing new branch (no --force needed)"
    git push --set-upstream "$remote" "$branch"
  fi
  ok "Pushed $branch to $remote"
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
  bash scripts/apply_public_allowlist.sh

  echo
  read -r -p "Apply the changes? (type 'yes' to git rm and commit; anything else aborts): " APPLY
  if [[ "$APPLY" != "yes" ]]; then
    git checkout main
    git branch -D "$DEBUT_BRANCH"
    die "Aborted. The $DEBUT_BRANCH branch was deleted; main is unchanged."
  fi

  bash scripts/apply_public_allowlist.sh --confirm
  ok "Allowlist applied. $(git status --short | wc -l) files staged for removal."

  # 4. Commit
  git commit -m "Apply PUBLIC_ALLOWLIST.txt for debut cut

Generated by scripts/setup_2remote_debut.sh cut.

The debut branch contains ONLY the files in docs/strategy/PUBLIC_ALLOWLIST.txt.
All forge-side files (data/entities/, docs/research/, etc.) are removed from
the index but remain in the working tree and in unaltered main-branch commits.
"
  ok "Committed allowlist application"

  # 5. Push to public remote — use the full safety stack
  safe_push "$PUBLIC_REMOTE" "$DEBUT_BRANCH"

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
  if bash scripts/apply_public_allowlist.sh --summary | grep -qE "Removed: [1-9]"; then
    info "Allowlist drift detected. Re-applying..."
    bash scripts/apply_public_allowlist.sh --confirm
    git commit -m "Re-apply PUBLIC_ALLOWLIST.txt after sync from main"
  else
    ok "No allowlist drift. No re-apply needed."
  fi

  # Push to public — full safety stack
  safe_push "$PUBLIC_REMOTE" "$DEBUT_BRANCH"
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

  # Push to public with FULL SAFETY STACK
  safe_push "$PUBLIC_REMOTE" "$DEBUT_BRANCH"
  git push "$PUBLIC_REMOTE" "$tag"

  # Cherry-pick back to private main
  echo
  read -r -p "Cherry-pick $tag into $PRIVATE_REMOTE/main? (yes/no): " CHERRYOK
  if [[ "$CHERRYOK" == "yes" ]]; then
    git checkout main
    # Find the merge commit (the one with "$hotfix_branch" in message)
    local MERGE_SHA
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

# === Subcommand: pre-push-audit (standalone, callable from anywhere) ===
cmd_pre_push_audit() {
  local remote="${1:-$PUBLIC_REMOTE}"
  local branch="${2:-$DEBUT_BRANCH}"
  require_remote "$remote"

  echo "=== Pre-push audit: $remote/$branch ==="
  git fetch "$remote" "$branch" 2>/dev/null || {
    warn "fetch failed — remote may not have $branch"
    return 0
  }

  local AHEAD BEHIND
  AHEAD=$(git log --oneline "$remote/$branch..HEAD" 2>/dev/null || true)
  BEHIND=$(git log --oneline "HEAD..$remote/$branch" 2>/dev/null || true)

  if [[ -n "$AHEAD" ]]; then
    echo "Commits on local (will be pushed):"
    echo "$AHEAD" | sed 's/^/    /'
  fi
  if [[ -n "$BEHIND" ]]; then
    echo "WARN: Commits on $remote (would be CLOBBERED):"
    echo "$BEHIND" | sed 's/^/    /'
  fi
  if [[ -z "$AHEAD" && -z "$BEHIND" ]]; then
    echo "  (no divergence — fast-forward or no-op)"
  fi
}

# === Dispatch ===
case "${1:-help}" in
  init)              cmd_init ;;
  cut)               cmd_cut ;;
  sync)              cmd_sync ;;
  hotfix-start)      shift; cmd_hotfix_start "$@" ;;
  hotfix-finish)     shift; cmd_hotfix_finish "$@" ;;
  pre-push-audit)    shift; cmd_pre_push_audit "$@" ;;
  help|-h|--help)
    grep -E '^# ' "$0" | head -40 | sed -E 's/^# ?//'
    ;;
  *) die "Unknown subcommand: $1. Run with 'help' for usage." ;;
esac
