<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔄 Makali Session Handoff — Cline takeover complete, OpenCode limits reset

**Task ID**: `makali-handoff-20261013-cline-takeover`
**From**: cline (Cline channel — executor during daily-limit exile)
**To**: makali (OpenCode channel)
**Date**: 2026-10-13
**Supersedes**: the Makali custom-instruction refresh inside `session-ses_fc75.md` (reclaim P1–P3 handoffs remain the reclaim record)

---

## ⚠️ Context you lost during compaction (read first)

1. **The ses_fc75 thread is CLOSED.** You ended it at `5fb35852` (G1/G2 closed) with install.sh timing blocked on disk. I took over on the operator's instruction.
2. **Your opencode.db was reclaimed** — 26.61 GB → 6.56 GB, 114,021 duplicated `message.updated.1` events removed, zero sessions/messages/parts lost, `quick_check`=ok. Rollback copy on the 8TB drive.
3. **Root is at 73%** (was 99%) — the disk gate that blocked your doom_guy timing contract no longer exists.
4. **Two-repo split happened.** Public `Xoe-NovAi/omega-engine` is a FRESH repo (clean cut history, no internal files ever). Internal work lives in `Xoe-NovAi/omega-engine-internal` (Actions disabled). The old public repo is renamed `omega-engine-retired` (private, fully backed up, awaiting deletion via `gh auth refresh -s delete_repo`).
5. **The tag `v1.6.0-alpha` is dead.** GitHub's `release_immutable_tags` row from the old repo permanently poisoned that name (survives release+tag deletion; archiving does NOT clear it — researched). The release shipped as **`v1.6.0a0`** (same SHA `355cbf1a`, more PEP-440-correct). Never reference `v1.6.0-alpha` as a GitHub ref again.
6. **PyPI name is `the-omega-engine`** (`omega` = unrelated game-theory package; `omega-engine` = omegaengine.ai SDK v2.6.0, different author/domain — researched, not the operator's). Distribution renamed in pyproject; module `omega` + CLI `omega` unchanged. **Pending publisher registered; BLOCKED on org approval.** The instant it approves: run the Publish workflow, then flip the doc lines.

## ✅ Your remaining items from ses_fc75 — status now

| Item | Status |
|---|---|
| install.sh timing (<300s) | **PASS** — 202s (was blocked). Three fixes: `MODELS_DIR` unset crash, RAM-guard `-j6` moved before pre-fetch, aria2c for >1MB |
| Mock-provider follow-up | **CLOSED** — install.sh's talk probe now forces `OMEGA_PROVIDER=mock` (bare probe hung 60s) |
| G1/G2 doc-lint | Closed by you (`5fb35852`, internal lineage). Public cut needed its own test fixes — public CI now green |
| G22 secret-scan | **Open.** Related: issue #1 (May, possible Gemini key) archived in retired-repo backup — if that key was real and active, rotate it |
| Public cut test defect (NEW) | Cut shipped tests importing allowlist-removed modules (`youtube_research`, `arcana_novai` WAD) — Test red on every public push. Fixed on public tree. `apply_public_allowlist.sh` needs a test-parity check |
| Native-embeddings mount bug (NEW) | `embeddings.py` defaulted to `~/omega_library`, mount is `/media/<user>/omega_library` — fixed + missing llama_cpp now degrades instead of crashing |
| Announcement | Audited (4 M29 fixes), live as release notes. Tag refs → `v1.6.0a0`, wheel filenames → `the_omega_engine-*` |
| README | Audited both trees (entity count 14→12 + Quality row, Grokster dropped, aria2c wheel path, `[native]` extra noted) |

## 📋 Suggested queue for this session

1. **Verify debut state** — `data/coordination/SESSION_ANCHOR.md` (refreshed) + this file's §"Context you lost"
2. **D1/D2/D3/D6/D7 backlog** (architect-ranged; untouched by Cline) + alias suffix-strip blockers in `ACTIVE_SPRINT.json` steps 1–2
3. **WAD-authoring docs link** — last open AGY post-debut item
4. **G22** — close alongside the Gemini-key rotation question
5. **Watch for PyPI org approval** — dispatch + doc-flip + clean-venv verify are ready to run

## 🗺 Where everything is

- **Internal repo**: remote `internal`, tip `78ab6877` · **Public repo**: remote `origin`, tip `6307b204`; tag `v1.6.0a0` @ `355cbf1a`; release live (pre-release, audited notes, 4 assets)
- **Timing logs**: `/media/USER/omega_library/staging/install-timing-20261013/`
- **PyPI verify**: `/tmp/omega-rename-verify/` (`the_omega_engine` wheel `e452d8ed…`, smoke PASS)
- **Retired-repo backup**: `data/handoff/retired-repo-backup/` (issues #1, #7) + `retired/*` refs on internal
- **opencode.db rollback**: `/media/USER/8TB/opencode_backups/opencode.db.rollback-20261013014834`

## 🔑 Working rules to carry forward

- **Two remotes, two flows**: internal work → push `internal` ONLY. Public changes → develop on internal, cherry-pick onto the `public/main` worktree (`/media/USER/omega_library/staging/public-main`), push `origin main`.
- **`set -euo pipefail` + `fuser`-in-`$()` = silent death** (root-caused twice). `|| true` is load-bearing. Same class: `timeout`-kill read as empty = false-PASS on gates — always capture rc.
- **`OMEGA_*_MODEL` defaults must match the mount**, not `~/omega_library`.
- **Never reference GitHub tag `v1.6.0-alpha` again.** Use `v1.6.0a0`.
- **Never `cp/rsync/dd` opencode.db** — VACUUM INTO only. Serialize giant-file ops on Node 0 (the OOM came from three concurrent 27 GB streams).

*⬡ OMEGA ⬡ CLINE ⬡ MAKALI-HANDOFF ⬡ makali-handoff-20261013-cline-takeover ⬡ 2026-10-13 ⬡*
