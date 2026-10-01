<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ROC — POST-MERGE REVIEW: Alpha Debut State

**Date**: 2026-09-02 | **Session**: ses_ff78b71ebffeDNuypPTT1RL3hH (standing EIS)
**Branch**: `main` at `a28c9c64` | **Repo**: `Xoe-NovAi/omega-engine` (PRIVATE)
**Trigger**: Architect (Node 0) ordered "merge all to main" — alpha PR launch

---

## §1 — EXECUTIVE SUMMARY

**Verdict**: 🔴 **ALPHA DEBUT NOT READY** — The merge to `main` was executed **without applying the PUBLIC_ALLOWLIST.txt filter**. The repo on `main` is the **FULL FORGE (5,939 files)**, not the public surface.

| Metric | Expected (Post-Allowlist) | Actual (main HEAD) | Delta |
|--------|--------------------------|-------------------:|-------|
| Tracked files | ~200-300 (allowlist) | **5,939** | +5,600+ |
| `data/entities/` | ~15 canonical entities | **49 dirs / 88 vestigial files** | +34 entities |
| `docs/strategy/` | 3 files (manual, allowlist, mandates) | **123 files** | +120 |
| `docs/research/` | 0 | **Full corpus** | +100+ |
| `third-party/` | 0 | **13 dirs / 660 MB** | +13 dirs |
| Root stray files | 0 | **35 files** | +35 |
| Test suite | GREEN | **BROKEN** (omega.library missing) | P0 |
| 118MB DB backup | Purged from history | **Back in working tree (untracked)** | P0 |

**The merge was a fast-forward of `release/debut` → `main` but `release/debut` was NEVER filtered by the allowlist.** The allowlist-check workflow only runs on `release/debut` branch and tags — NOT on `main`. The `apply_public_allowlist.sh` script was never run.

---

## §2 — CRITICAL ISSUES BLOCKING ALPHA DEBUT (P0)

### 2.1 Allowlist Never Applied — Full Forge on Main

**Evidence**:
- `git ls-files | wc -l` → **5,939** (allowlist expects ~200-300)
- `PUBLIC_ALLOWLIST.txt` exists at `docs/strategy/PUBLIC_ALLOWLIST.txt` but was **never applied**
- `scripts/apply_public_allowlist.sh` exists but was **never run**
- `.github/workflows/allowlist-check.yml` only triggers on `release/debut` branch and tags — **NOT on `main`**

**File:line**: `.github/workflows/allowlist-check.yml:6-10` — `on: push: branches: [release/debut]`

**Impact**: If the repo is made public NOW, the world sees:
- 49 entity directories (including `anubis/`, `carmack/`, `lucifer/`, `arch/`, etc.)
- Full `docs/research/` corpus (100+ files)
- Full `docs/archive/` (stale history)
- `third-party/` (660 MB of game source code)
- 35 stray root files (session logs, debug scripts, PDFs)

### 2.2 Test Suite Broken — `omega.library` Missing

**Evidence**:
```
E   ModuleNotFoundError: No module named 'omega.library'
src/omega/oracle/sovereign_search_service.py:39: in <module>
    from omega.library.indexer import Indexer
```

**File:line**: `src/omega/oracle/sovereign_search_service.py:39`

**Root cause**: D-565 cleanup removed `omega.library` but the import remains. The SOTE W37 commit (Ma'at) even documented this as a known failure:
> "Correctly detects hub failure (missing omega.library module from D-565 cleanup)"

**File:line**: `data/entities/maat/proposed_lessons.yaml:650-655` (lesson `p0_ci_gates_implemented`)

**Impact**: CI will fail on any clone. `pip install -e .` then `pytest` fails immediately.

### 2.3 118MB Database Backup Back in Working Tree

**Evidence**:
```
Untracked files:
  data/omega_memory.db.bak.pre_qwen3

$ du -sh data/omega_memory.db.bak.pre_qwen3
118M
```

**History**: This file was purged from git history via `git filter-repo` (per merge notes), but the **working tree copy was not deleted**. It's now untracked but present.

**Impact**: If accidentally committed, it bloats the repo by 118MB. If the repo is made public, anyone cloning gets this file.

### 2.4 35 Stray Root Files Still Tracked

**Evidence** (from `git ls-files`):
```
20260829-session-ses_fdef.md
350-percentage-of-365-Google-Search.pdf
350-percentage-of-365-Google-Search.pdf.license
Grokster-compaction-summary-09012026-11_19_AM.md
INTEGRATION_SUMMARY.md
OAuth-failure-incident-session-ses_fe8c.md
P1.md
P3.md
P4.md
P5.md
P6.md
P7.md
P9.md
PAGE-FROM-KALI-ses fdef2be4effe4pAaLXCTUx62GO.md
PILLAR_REFACTOR_WEB_EVIDENCE.md
PILLAR_RESEARCH_GAPS_20260822.md
PRE_COMPACTION_NOTES.md
QUICK_WINS_FROM_GROK.md
Roc-EIS-report-08-31-2026.md
Roc-launched-ses_ff78.md
debug_test.py
failure-remediation-ses_fdef.md
file
file-write-fail-forensics-session-ses_ff78.md
find_iris.py
find_iris.py.license
old-claude-sys-prompt.md
omega_engine_audit_report.md
quantum_error_correction_2026_article.md
session_gnosis.md
sovereign-intelligence-unlocked-ses_fdef.md
trim_scope.py
trim_scope.py.license
update_docs.py
update_docs.py.license
```

**Allowlist status**: All listed in `PUBLIC_ALLOWLIST.txt:121-131` under "Stray root-level junk — G4" — **should NOT be tracked**.

### 2.5 88 Vestigial Entity Files Tracked

**Evidence**: `git ls-files | grep "data/entities/(anubis|arch|brigid|carmack|cli_cline|cli_gemini|cline_kqv|default|ereshkigal|general|hecate|inanna|lucifer|makali_fusion|movie-expert|omnidroid|p10|pillar_p1|prometheus|quality|saraswati|sekhmet|sysadmin|watchtower|web_gemini)/" | wc -l` → **88**

**Allowlist status**: `PUBLIC_ALLOWLIST.txt:98` — `data/entities/` is FORGE except "one default soul"

**Impact**: Public sees 34 non-canonical entities (`anubis`, `arch`, `carmack`, `lucifer`, etc.)

### 2.6 6 `.pyc` Files Still Tracked

**Evidence**:
```
mcp_servers/__pycache__/__init__.cpython-313.pyc
mcp_servers/omega_hub/__pycache__/__init__.cpython-313.pyc
mcp_servers/omega_hub/__pycache__/mcp_client.cpython-313.pyc
mcp_servers/omega_hub/__pycache__/server.cpython-313.pyc
mcp_servers/omega_hub/__pycache__/state.cpython-313.pyc
mcp_servers/omega_hub/hub_tools/__pycache__/m34_active_subagents.cpython-313.pyc
```

**Status**: Modified in working tree (recompiled). `.gitignore` has `__pycache__/` but these were grandfathered in.

---

## §3 — HIGH-PRIORITY WORK NEEDED POST-MERGE (P1)

### 3.1 Apply Allowlist to Main (or Create Clean Release Branch)

**Options**:
- **Option A**: Run `scripts/apply_public_allowlist.sh --confirm` on `main`, commit, force-push
- **Option B**: Create `release/debut-v1.6.0` from `main`, apply allowlist there, tag and release
- **Option C**: Use `git filter-repo` with paths-from-file to create a clean public branch

**Recommendation**: Option B — keep `main` as forge, create clean `release/debut` for public.

### 3.2 Fix Test Suite (omega.library Import)

**Root cause**: `src/omega/oracle/sovereign_search_service.py:39` imports `omega.library.indexer.Indexer` but `omega.library` was removed in D-565.

**Fix options**:
- Restore `omega.library` from git history (if it was a real module)
- Stub the import with a conditional/fallback
- Make `omega.library` an optional dependency

**File:line**: `src/omega/oracle/sovereign_search_service.py:39`

### 3.3 Remove 118MB DB Backup from Working Tree

```bash
rm data/omega_memory.db.bak.pre_qwen3
# Add to .gitignore if not already
echo "data/omega_memory.db.bak.*" >> .gitignore
```

### 3.4 Clean Stray Root Files

```bash
# Remove from tracking (they're in .gitignore already or should be)
git rm --cached 20260829-session-ses_fdef.md \
  350-percentage-of-365-Google-Search.pdf \
  350-percentage-of-365-Google-Search.pdf.license \
  Grokster-compaction-summary-09012026-11_19_AM.md \
  INTEGRATION_SUMMARY.md \
  OAuth-failure-incident-session-ses_fe8c.md \
  P1.md P3.md P4.md P5.md P6.md P7.md P9.md \
  PAGE-FROM-KALI-ses\ fdef2be4effe4pAaLXCTUx62GO.md \
  PILLAR_REFACTOR_WEB_EVIDENCE.md \
  PILLAR_RESEARCH_GAPS_20260822.md \
  PRE_COMPACTION_NOTES.md \
  QUICK_WINS_FROM_GROK.md \
  Roc-EIS-report-08-31-2026.md \
  Roc-launched-ses_ff78.md \
  debug_test.py \
  failure-remediation-ses_fdef.md \
  file \
  file-write-fail-forensics-session-ses_ff78.md \
  find_iris.py find_iris.py.license \
  old-claude-sys-prompt.md \
  omega_engine_audit_report.md \
  quantum_error_correction_2026_article.md \
  session_gnosis.md \
  sovereign-intelligence-unlocked-ses_fdef.md \
  trim_scope.py trim_scope.py.license \
  update_docs.py update_docs.py.license
```

### 3.5 Clean Vestigial Entities

Per the Entity Cleanup Dialectic (D-400 through D-410):
- Delete 11 mythology entities (`anubis`, `brigid`, `ereshkigal`, `hecate`, `inanna`, `lucifer`, `omnidroid`, `prometheus`, `quality`, `saraswati`, `sekhmet`)
- Merge `carmack` → `john_carmack`
- Archive `cli_gemini`, `web_gemini`, `sysadmin`, `watchtower`
- Relocate `cline_kqv` to `experiments/kq5-godot/`
- Merge `Sophia` (capital-S) → `sophia`
- Delete `default`, `general`, `movie-expert`, `archive` (lowercase)

### 3.6 Remove Tracked `.pyc` Files

```bash
find mcp_servers/ -name "*.pyc" -exec git rm --cached {} \;
```

### 3.7 Update CHANGELOG.md and STATUS_REPORT.md

- `CHANGELOG.md` last entry: `[v1.5.0] - 2026-07-18` (stale)
- `STATUS_REPORT.md` last entry: `2026-07-22` (stale)

---

## §4 — WHAT THE ALLOWLIST/ARCHITECTURE MISSED

### 4.1 Allowlist-Check Workflow Not Wired to Main

**File:line**: `.github/workflows/allowlist-check.yml:6-10`
```yaml
on:
  push:
    branches: [release/debut]
    tags: ["v*.*.*"]
```
**Missed**: The workflow should ALSO run on `main` pushes, or the release process should mandate that `main` is always allowlist-filtered before any tag/push.

### 4.2 No PUBLIC_ALLOWLIST.txt in Repo Root

The allowlist lives at `docs/strategy/PUBLIC_ALLOWLIST.txt` but the script defaults to `ALLOWLIST_FILE="${ALLOWLIST_FILE:-docs/strategy/PUBLIC_ALLOWLIST.txt}"`. This works, but the file is not discoverable from the repo root.

### 4.3 The "Self-Exemption" for apply_public_allowlist.sh

**File:line**: `.github/workflows/allowlist-check.yml:103-112` — The workflow verifies the cut-tool is in the public tree. But if the allowlist is never applied, the tool is in the forge tree, not the public tree.

### 4.4 No Pre-Merge Gate on Main

The CI workflow (`.github/workflows/ci.yml:3-4`) runs on `main` and `release/initial-v1` but does NOT include the allowlist check. The allowlist check is a separate workflow that only runs on `release/debut`.

### 4.5 Entity Fleet Not Canonicalized

The allowlist says `data/entities/` is FORGE except "one default soul" but the actual entity fleet has 49 directories. The canonical 14-agent fleet in `.opencode/agents/` is clean, but `data/entities/` is not.

### 4.6 Third-Party Heritage Registry

`PUBLIC_ALLOWLIST.txt:103` explicitly lists `third-party/` as FORGE. But the heritage vetting (M14) produced 13 repos with 660MB of source code. The public debut has no heritage registry — this is a deliberate cut, but it means the "heritage" claim in README is not verifiable from the public repo.

---

## §5 — DIALECTIC POSITIONS

### 5.1 Concede

1. **The merge was premature** — The Architect ordered "merge all to main" but the allowlist filter was a prerequisite that was skipped. The repo on `main` is not the public surface.

2. **The test suite is broken and was known broken** — Ma'at's SOTE W37 commit documented the `omega.library` failure but the fix was not completed before merge.

3. **The 118MB DB backup is back** — The `git filter-repo` purged it from history but the working tree copy was not cleaned up. This is a process gap.

4. **35 stray root files are tracked** — These were identified in my pre-publish audit and the allowlist explicitly marks them as G4 (delete). They were not removed before merge.

5. **Vestigial entities are tracked** — 34 non-canonical entities in `data/entities/` that the allowlist says should not exist on the public surface.

### 5.2 Defend

1. **The SOTE v1.0.3 work IS complete and valuable** — The nested dialectic, Ma'at implementation, CI/CD pipeline, and P0 gates are all real work that should ship. The problem is the *packaging*, not the content.

2. **The allowlist mechanism IS well-designed** — `apply_public_allowlist.sh` v5 handles VULN #2, #6, D-565 gap. The tool is solid; it just wasn't run.

3. **The repo is PRIVATE** — `Xoe-NovAi/omega-engine` is private. The damage is contained until visibility changes.

4. **The entity cleanup dialectic produced clear decisions** — D-400 through D-410 from yesterday's session give a precise cleanup plan. It just needs execution.

5. **The CI/CD pipeline (SOTE W37) IS implemented** — The workflows, Makefile targets, JSON schema validation, and temple-grade gate are all there. They just need the test suite to pass.

### 5.3 Synthesize

1. **Immediate action**: Create a clean `release/debut-v1.6.0` branch from `main`, run `scripts/apply_public_allowlist.sh --confirm`, fix the `omega.library` import, run CI to green, tag `v1.6.0`, and make the repo public from THAT branch. Do NOT try to clean `main` in place.

2. **Process fix**: Add allowlist-check to the `main` branch workflow, or mandate that `main` is always allowlist-clean before any tag. The current architecture has a gap: `main` can drift from the allowlist.

3. **The alpha debut CAN ship this week** — All the hard work (SOTE, nested dialectic, Ma'at impl, entity cleanup decisions, subagent-verifier spec) is done. The remaining work is mechanical cleanup (allowlist apply, test fix, file removal) — 2-4 hours of focused work.

4. **Post-debut**: The entity cleanup (D-400-410) and docs reorganization should be the first post-merge sprint. The allowlist should be updated to reflect the canonical entity fleet.

---

## §6 — RECOMMENDED SEQUENCE

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Create `release/debut-v1.6.0` from `main` | Kali | 5 min |
| 2 | Run `scripts/apply_public_allowlist.sh --confirm` on that branch | Roc | 10 min |
| 3 | Fix `omega.library` import in `sovereign_search_service.py:39` | Ma'at | 30 min |
| 4 | Remove 118MB DB backup from working tree | Roc | 1 min |
| 5 | Remove tracked `.pyc` files | Roc | 1 min |
| 6 | Commit, push, run CI to green | Kali | 30 min |
| 7 | Tag `v1.6.0`, make repo public | Architect | 5 min |
| 8 | Post-debut: Execute entity cleanup (D-400-410) | Ma'at + Roc | 2-4h |
| 9 | Post-debut: Update CHANGELOG.md, STATUS_REPORT.md | Roc | 30 min |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_post_merge_review ⬡ DIALECTIC-READY*