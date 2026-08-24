# 🔱 Fork Management & Synchronization Guide
**AP Token**: `AP-FORK-MANAGEMENT-GUIDE-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_fork_management ⬡ 2026-07-25

<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Xoe-NovAi Foundation -->

---

## Executive Summary

This guide provides a comprehensive fork management strategy for the Omega Engine team, synthesized from KG-4 research findings. Forks that diverge from upstream become maintenance burdens without disciplined sync strategies.

**Purpose**: Establish sustainable fork maintenance practices that prevent the "stale fork" problem.

**Scope**: Applies to all forks maintained by the Omega Engine team, including AGY OAuth plugin and community contributions.

---

## 🎯 Core Principle: Never Commit to main on Fork

**Rule**: Keep `main` as a clean mirror of upstream. All changes belong on feature branches.

**Why**: This enables:
- Easy upstream sync (rebase or merge)
- Clean PR history
- Minimal merge conflicts
- Sustainable long-term maintenance

---

## 🔧 Setup (One-Time)

### Add Upstream Remote

```bash
# Add upstream remote
git remote add upstream https://github.com/original-org/repo.git

# Verify
git remote -v
# origin    https://github.com/your-user/repo.git (fetch/push)
# upstream  https://github.com/original-org/repo.git (fetch/push)
```

### Configure Git

```bash
# Enable rerere (reuse recorded resolution)
git config --global rerere.enabled true

# Configure fetch to prune stale branches
git config --global fetch.prune true

# Configure pull to rebase by default
git config --global pull.rebase true
```

---

## 🔄 Sync Strategy

### Daily Sync (Recommended)

```bash
# Option A: Rebase (preferred for small custom commits)
git checkout main
git fetch upstream
git rebase upstream/main
git push origin main --force-with-lease

# Option B: Merge (simpler, creates merge commits)
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

### Weekly Full Sync

```bash
# Fetch all upstream changes
git fetch upstream --prune

# Rebase main onto upstream
git checkout main
git rebase upstream/main

# Update all feature branches
git checkout feature/my-change
git rebase main

# Push with lease to prevent force push accidents
git push origin main --force-with-lease
git push origin feature/my-change --force-with-lease
```

### Immediate Sync (Security Fixes)

```bash
# When upstream releases security fix
git fetch upstream
git checkout main
git cherry-pick <commit-hash>  # Or rebase
git push origin main
# Deploy immediately
```

---

## 📊 Sync Cadence by Fork Type

| Fork Type | Sync Frequency | Strategy | Notes |
|-----------|----------------|----------|-------|
| **Active contribution** (PR pending) | Daily | Rebase | Keep PR up-to-date |
| **Custom patches** (small) | Weekly | Rebase | Max drift 7-10 days |
| **Custom patches** (large) | Per upstream release | Merge | Preserve patch history |
| **Security patches** | Immediate | Cherry-pick | Deploy ASAP |
| **Research/experimental** | Never sync | Fork & forget | Isolated experiments |

---

## 🛠️ Conflict Prevention

### Before Starting Work

```bash
# Always sync before creating feature branch
git fetch upstream
git checkout main
git rebase upstream/main
git checkout -b feature/my-change
```

### During Development

```bash
# Sync feature branch frequently
git fetch upstream
git rebase upstream/main
# Resolve any conflicts immediately
```

### Before Submitting PR

```bash
# Final sync before PR
git fetch upstream
git rebase upstream/main
# Resolve any conflicts
git push origin feature/my-change --force-with-lease
```

---

## 🔥 Conflict Resolution

### When Rebase Hits Conflicts

```bash
# Start rebase
git rebase upstream/main

# Conflict markers appear in files
# Resolve each file, then:
git add <resolved-file>
git rebase --continue

# Use git mergetool for visual diff
git mergetool

# Abort rebase if needed
git rebase --abort
```

### Using git rerere

```bash
# Enable rerere (reuse recorded resolution)
git config --global rerere.enabled true

# When rebase hits conflicts, rerere will:
# 1. Record conflict resolution
# 2. Auto-apply same resolution if conflict recurs
# 3. Save time on repeated conflicts

# Check rerere status
git rerere status

# Forget specific resolution
git rerere forget <file>
```

### Common Conflict Patterns

| Conflict Type | Resolution |
|---------------|------------|
| **Package version bumps** | Accept upstream version, re-test |
| **Config file changes** | Merge carefully, preserve custom settings |
| **API changes** | Update custom code to match new API |
| **Test changes** | Merge tests, update custom test expectations |

---

## 📋 Fork Maintenance Checklist

### Daily

- [ ] Check for upstream releases
- [ ] Sync if security fix released
- [ ] Monitor PR feedback

### Weekly

- [ ] Full upstream sync
- [ ] Update all feature branches
- [ ] Review merge conflicts
- [ ] Update documentation

### Monthly

- [ ] Review fork strategy
- [ ] Assess drift budget
- [ ] Clean up stale branches
- [ ] Update sync cadence if needed

### Per Upstream Release

- [ ] Review changelog for breaking changes
- [ ] Test custom patches against new version
- [ ] Update documentation
- [ ] Deploy if security fix

---

## 🚨 Emergency Procedures

### Security Vulnerability in Upstream

1. **Immediate**: Fetch upstream fix
2. **Assess**: Determine impact on custom patches
3. **Apply**: Cherry-pick or rebase fix
4. **Test**: Verify custom patches still work
5. **Deploy**: Roll out fix immediately
6. **Notify**: Inform users of security update

### Breaking Changes in Upstream

1. **Review**: Analyze breaking changes
2. **Assess**: Determine impact on custom code
3. **Plan**: Create migration plan
4. **Test**: Test custom patches against new version
5. **Update**: Modify custom code as needed
6. **Deploy**: Roll out updated fork

### Fork Abandonment

1. **Assess**: Determine if fork is still needed
2. **Archive**: Create archive branch
3. **Document**: Record fork status
4. **Migrate**: Move to alternative if available
5. **Notify**: Inform users of fork status

---

## 📊 Metrics & Monitoring

### Track These Metrics

| Metric | Target | Alert If |
|--------|--------|----------|
| **Drift days** | <7 days | >10 days |
| **Merge conflicts** | 0 | >5 files |
| **Sync frequency** | Weekly | Monthly |
| **Security patch lag** | <24 hours | >72 hours |

### Monitoring Commands

```bash
# Check drift from upstream
git log --oneline main..upstream/main | wc -l

# Check merge conflicts
git merge-tree $(git merge-base main upstream/main) main upstream/main | grep -c "^<<<<<<<"

# Check sync frequency
git log --oneline --since="1 week ago" main | wc -l
```

---

## Decision Gate: Fork Management Compliance

✅ **ACHIEVED**: This guide provides comprehensive fork management strategy, synthesized from KG-4 research findings.

**Next Steps**:
1. Apply this guide to AGY OAuth fork
2. Set up automated upstream sync
3. Configure git rerere for recurring conflicts
4. Establish drift budget monitoring

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_fork_management ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
