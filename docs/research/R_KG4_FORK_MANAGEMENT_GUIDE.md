# 🔱 Knowledge Gap 4: Fork Management & Synchronization Strategy
**AP Token**: `AP-KG4-FORK-MANAGEMENT-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ RESEARCH ⬡ 2026-07-25

## Executive Summary

Forks that diverge from upstream become maintenance burdens. A disciplined sync strategy — rebase for small custom commits on fast-moving upstream, merge for long-lived forks — prevents the "stale fork" problem where PRs accumulate 1000+ merge conflicts.

**Key Finding**: Never commit directly to `main` on your fork. Keep `main` as a clean mirror of upstream. All changes belong on feature branches.

---

## §1 Core Fork Workflow

### Setup (One-Time)

```bash
# Add upstream remote
git remote add upstream https://github.com/original-org/repo.git

# Verify
git remote -v
# origin    https://github.com/your-user/repo.git (fetch/push)
# upstream  https://github.com/original-org/repo.git (fetch/push)
```

### Daily Sync

```bash
# Option A: Merge (simpler, creates merge commits)
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# Option B: Rebase (linear history, preferred)
git checkout main
git fetch upstream
git rebase upstream/main
git push origin main --force-with-lease
```

### Feature Branch Sync

```bash
# After syncing main, rebase feature branch
git checkout feature/my-change
git rebase main
# Resolve conflicts if any, then:
git push origin feature/my-change --force-with-lease
```

### GitHub CLI Alternative

```bash
# Sync fork from GitHub (no local clone needed)
gh repo sync your-user/repo --source original-org/repo

# From within cloned fork
gh repo sync --source original-org/repo
```

---

## §2 Sync Strategy Decision Tree

```
Is your fork for long-term maintenance or short-term contribution?
│
├─ SHORT-TERM (single PR or small fix)
│   └─ Rebase onto upstream/main → linear history, clean PR
│      └─ Preferred: git rebase + --force-with-lease
│
├─ LONG-TERM (active fork with custom changes)
│   ├─ Is upstream fast-moving (daily commits)?
│   │  ├─ YES → Rebase preferred
│   │  │  └─ Use merging rebase (Git for Windows pattern)
│   │  └─ NO → Merge acceptable
│   │     └─ Simpler, preserves full commit history
│   └─ Are you contributing back?
│      ├─ YES → Feature branches + daily sync
│      └─ NO → Periodic bulk syncs OK
│
└─ DIVERGED FORK (main has commits not in upstream)
   ├─ If 1-5 commits → rebase onto upstream/main
   ├─ If 5+ commits → merge (safer, preserves history)
   └─ If you don't need custom commits → hard reset to upstream
      └─ git reset --hard upstream/main + --force push
```

---

## §3 Sync Cadence Recommendations

| Fork Type | Frequency | Method |
|-----------|-----------|--------|
| Active development on feature branch | **Daily** | `git rebase upstream/main` |
| Before opening a PR | **Always** | Sync + rebase feature branch |
| Passive fork (only consuming) | **Weekly** | `git fetch upstream + merge` |
| Long-lived fork with custom patches | **Per upstream release** | Merging rebase |
| Security patches upstream | **Immediate** | Fetch + merge/rebase same day |

**Drift Budget**: Max 7-10 days behind upstream. Beyond that, merge conflicts compound exponentially.

---

## §4 Handling Merge Conflicts

### Conflict Prevention

| Practice | Why |
|----------|-----|
| Sync before starting new work | Base your branch on latest code |
| Sync feature branches frequently | Small, frequent rebases < giant resync |
| Communicate about shared files | Coordinate with others touching same code |
| Keep feature branches short-lived | Less drift = fewer conflicts |

### Conflict Resolution

```bash
# When rebase hits conflicts
git rebase upstream/main
# → Conflict markers appear in files
# Resolve each file, then:
git add <resolved-file>
git rebase --continue

# Use git mergetool for visual diff
git mergetool

# Identify upstreamed commits (Git for Windows pattern)
git range-diff --left-only <commit>^! <commit>..<upstream-branch>
# If commit was upstreamed: git rebase --skip
```

### The 18-Month Stale Fork Antipattern

A real incident: contributor forked repo 18 months ago, made changes on main, submitted PR. The fork was 1200 commits behind. PR had 1200+ merge conflicts. Maintainers spent 2 hours trying to resolve before closing as stale.

**Fix**: Always create a fresh feature branch from latest upstream, never work on your fork's main.

---

## §5 Fork Maintenance Playbook

### Feature Branch Workflow

```bash
# 1. Start fresh: sync main, create branch
git checkout main
git fetch upstream
git rebase upstream/main
git push origin main
git checkout -b fix/login-error

# 2. Work, commit, push
git add -A && git commit -m "fix(auth): prevent null pointer on logout"
git push origin fix/login-error

# 3. Sync mid-work (daily)
git fetch upstream
git rebase upstream/main  # while on feature branch
git push origin fix/login-error --force-with-lease

# 4. Open PR from your feature branch
# 5. After PR merged, delete branch
git checkout main && git branch -d fix/login-error
git push origin --delete fix/login-error
```

### Automated Sync (GitHub Actions)

```yaml
name: Sync fork with upstream
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6AM
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: Configure git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
      - name: Sync with upstream
        run: |
          git remote add upstream https://github.com/original-org/repo.git
          git fetch upstream
          git checkout main
          git merge upstream/main --ff-only || {
            echo "Fast-forward merge failed. Manual intervention needed."
            exit 1
          }
          git push origin main
```

### Git Configuration for Conflict Management

```bash
# Enable rerere (reuse recorded resolution) for recurring conflicts
git config --global rerere.enabled true

# Better merge conflict display
git config --global merge.conflictStyle diff3
```

---

## §6 Decision Framework

| Factor | Prefer Rebase | Prefer Merge |
|--------|---------------|--------------|
| Commit history | Linear, clean | Preserves full history |
| Custom commits on fast-moving upstream | ✅ | ❌ (merge commits accumulate) |
| Long-lived fork with many patches | ❌ (constant rebase pain) | ✅ |
| Multiple contributors on same fork | ❌ (force-push danger) | ✅ |
| First-time fork manager | ❌ (merge is simpler) | ✅ |
| Reviewing upstreamed commits | ✅ (easy cherry-pick) | ❌ (complex diff) |

---

## §7 Sources

1. GitHub Docs, "Syncing a fork" — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork
2. CoreUI, "How to sync fork in Git" (2026-03-16) — https://coreui.io/answers/how-to-sync-fork-in-git/
3. How2, "How to Keep Git Forks in Sync with Upstream Changes" (2026-02-10) — https://how2.sh/posts/how-to-git-version-control-sync-forks-upstream/
4. GitHub Blog, "Being friendly: Strategies for friendly fork management" — https://github.blog/developer-skills/github/friend-zone-strategies-friendly-fork-management/
5. TheCodeForge, "Forking and Contributing — The PR That Was Open for 18 Months" (2026-07-11) — https://thecodeforge.io/devops/forking-contributing/

---

## Decision Gate

✅ **Fork maintenance playbook with decision tree** — Rebase vs merge decision framework
✅ **Sync cadence recommendations** — Daily/weekly/per-release frequencies
✅ **Conflict resolution guide** — Prevention strategies + resolution steps
✅ **Automated sync workflow** — GitHub Actions template for weekly sync
✅ **18-month stale fork cautionary tale** — Real incident with lessons learned
