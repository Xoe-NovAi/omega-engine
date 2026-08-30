# Rollback Plan — Exact Revert Commands

**Authority**: Phase 1 Plan — All changes config-only, fully reversible  
**Execution**: Run in order if any verification test fails  
**Time to rollback**: ~2 minutes

---

## Rollback Commands (In Order)

### 1. Restore opencode.json
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git checkout opencode.json
```

### 2. Remove MANDATES_CONDENSED.md
```bash
rm MANDATES_CONDENSED.md
```

### 3. Remove Sovereign Compaction Plugin
```bash
rm ~/.config/opencode/plugin/sovereign-compaction.ts
```

### 4. Remove Skill permission Denies
```bash
# Remediated 2026-08-21 (DEV-04): CI-4 now uses permission.skill in opencode.json,
# NOT SKILL.md frontmatter. Rollback = delete the block (restores default allow-all):
jq 'del(.permission.skill)' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json
# (If opencode.json was git-tracked and unchanged otherwise, `git checkout opencode.json` above already covers this.)
```

### 5. Remove Environment Variables (if added to shell profile)
```bash
# Remove from ~/.bashrc or ~/.zshrc
sed -i '/OMEGA_ENTITY/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
sed -i '/OMEGA_PHASE/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
sed -i '/OPENCODE_DISABLE_AUTOCOMPACT/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
```

---

## Single-Command Full Rollback

```bash
#!/bin/bash
# rollback_phase1.sh - Complete Phase 1 rollback

set -e

cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

echo "Rolling back Phase 1 Context Injection..."

# 1. opencode.json
git checkout opencode.json
echo "✓ opencode.json restored"

# 2. MANDATES_CONDENSED.md
rm -f MANDATES_CONDENSED.md
echo "✓ MANDATES_CONDENSED.md removed"

# 3. Compaction plugin
rm -f ~/.config/opencode/plugin/sovereign-compaction.ts
echo "✓ sovereign-compaction.ts removed"

# 4. Skills permission denies (DEV-04: permission.skill, not auto_load)
jq 'del(.permission.skill)' opencode.json > opencode.json.tmp && mv opencode.json.tmp opencode.json
echo "✓ Skill permission block removed (default allow-all restored)"

# 5. Environment variables
sed -i '/OMEGA_ENTITY/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
sed -i '/OMEGA_PHASE/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
sed -i '/OPENCODE_DISABLE_AUTOCOMPACT/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
echo "✓ Environment variables cleaned"

echo ""
echo "=== ROLLBACK COMPLETE ==="
echo "Verify: opencode --log-level DEBUG run 'hello' 2>&1 | head -20"
```

---

## Verification After Rollback

```bash
# Verify original state restored
jq '.instructions' opencode.json
# Expected: ["SOVEREIGN_MANDATES.md", "ORACLE_STACK.md", ...]

jq '.compaction' opencode.json
# Expected: {"auto":true,"prune":true,"tail_turns":3,"preserve_recent_tokens":40000,"reserved":10000}

jq '.plugin[]' opencode.json
# Expected: 4 plugins (no sovereign-compaction)

jq '.agent.kali' opencode.json
# Expected: {"mode":"all","temperature":0.5,"steps":50} (no model/variant/toolProfile)

ls MANDATES_CONDENSED.md 2>&1
# Expected: "No such file or directory"

ls ~/.config/opencode/plugin/sovereign-compaction.ts 2>&1
# Expected: "No such file or directory"

jq '.permission.skill' opencode.json
# Expected: null (DEV-04: permission block removed; default allow-all restored)
```

---

## Git-Based Rollback (Alternative)

If you committed Phase 1 changes:

```bash
# View recent commits
git log --oneline -5

# Rollback to commit before Phase 1
git reset --hard HEAD~1  # Adjust number as needed

# Or revert specific commit
git revert <commit-hash>
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20*