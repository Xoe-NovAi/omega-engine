<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — roc_racoon — OpenCode DB Compaction (2026-10-04→05)

**Model**: gemini-3.8-flash (switched 05:15) · **Session**: ses_ff78b71ebffeDNuypPTT1RL3hH
**Status**: ✅ **FINAL — CLEARED FOR EXECUTION (GO).** Four review rounds + self-review complete. Phase 0 (Issues 1–3) APPLIED; self-review fixed a B-2 KeyError, service drift, and a pre-delete ordering flaw. Battery 21/21 + J/K/L/M 12/12; live DB quick_check ok.
**Swap code v5.1**: hardened copy-verified-backup + 6 review patches; battery A–I 21/21 PASS.
**Synthesis**: `data/coordination/OPENCODE_DB_FINAL_REVIEW_SYNTHESIS_20261005.md`
**Reviews**: Sonnet 4.6 APPROVE WITH CHANGES + Opus 4.6 supplement → `data/coordination/OPENCODE_DB_REVIEW_ANTIGRAVITY_20261005.md` + `..._OPUS_SUPPLEMENT_20261005.md`

## Current numbers
- Live DB **43.30 GiB INTACT** (46,497,648,040 bytes · 3,109 sessions · quick_check ok)
- Compacted snapshot **26.25 GiB VERIFIED @03:06 but STALE ~2.5 h** → re-compact before swap
- Root free **5.8 GB** (`66306`) · omega_library **50 GB** (`66307`)
- Orphans/stray backups: none · services `searxng`+`qdrant` RUNNING (no DB lock) · `omega-iris` DOES NOT EXIST

## 🔴 THE CORE FACT (everything depends on this)
**A hard link cannot free space.** `unlink()` under an existing link decrements `nlink` only —
bytes free when the LAST link dies (probe: `6847.24 → 6847.24 MB` until both links gone).
So the backup must be a **full copy on a DIFFERENT filesystem**, validated BEFORE the original
is unlinked. A hard-link backup + unlink + copy-in would die `ENOSPC` at 5.8 GB free.

## SQLite facts (empirically verified)
- `VACUUM INTO` is READ-ONLY on source → runs live (WAL readers don't block writers)
- In-place `VACUUM` needs 2× DB size (~86 GiB) → structurally impossible here
- ⚠️ `VACUUM INTO` **drops `journal_mode`** → must `PRAGMA journal_mode=WAL` + `wal_checkpoint(TRUNCATE)` after
- `VACUUM INTO` DOES read uncheckpointed WAL content (no loss); preserves header/rows
- **`PRAGMA foreign_keys=0`** → declared `ON DELETE CASCADE` NOT enforced
- `event` (21.1 GiB, 78.9%) does NOT cascade from `session`

## Swap design v5 (canonical: KB §8 v1.2.0 / handoff)
1. refuse if ANY process holds DB open — **no `--force` override** (unlink under a live writer = invisible loss)
2. backup fs must be **different device** with ≥ source×1.02 free (omega: 50 ≥ 47.5 ✓)
3. projected space: `free_now + source_total ≥ target×1.05` (5.8+43.3=49.1 ≥ 27.6 ✓)
4. verify target (manifest) → capture source row counts
5. full-copy `db+wal+shm` → omega, fsync files + dir (progress every 15 s)
6. **VALIDATE backup**: byte size + read-only `quick_check` + row counts — original still intact
7. unlink wal/shm, then db → **trip-wire**: if projected space NOT freed → restore immediately
8. stream-copy compacted in, fsync + dir fsync
9. post-verify: `integrity_check`, `journal_mode=wal`, rows == target's; staleness reported as WARN
10. any post-unlink failure → **restore BY COPY** (`Path.rename()` = EXDEV cross-device)
11. backup RETAINED at `omega_library/staging/backup_pre_compact_<TS>/` until user deletes

## Five attempts (only #5 is correct)
1. `nohup &` compaction → reaped → **foreground only**
2. `copy2` before `unlink` → needed 112 GB, had 5.2 → OOM
3. hardlink on omega → `EXDEV` → fallback `copy2` filled omega to 100%; 4.8 GB root orphan (deleted)
4. hardlink on root → **passed rc=0 but would ENOSPC** — flat `net ±0.0 MiB` in its own test was the tell; caught in review, never run
5. copy-verified-backup cross-device → **tests A–F green** ✅

## Test evidence (this review)
A happy-path ✅ · B same-device refusal ✅ · C lock+`-f` refusal ✅ · D chaos-hook restore
(rows intact, `wal`) ✅ · E too-small backup fs ✅ · F **production 66306→66307** ✅
Real DB byte-identical after the suite; all test artifacts removed.

## Continuation

**Authoritative handoff**: `data/coordination/OPENCODE_DB_SWAP_HANDOFF_20261005.md`
**Live feed**: `data/coordination/ROC_RACOON_LIVE_FEED.md`
**KB (canonical design)**: `docs/kb/OPENCODE_DB_COMPACTION_GUIDE.md` **v1.2.0 §8**
**Tool**: `scripts/opencode_db_compact.py` · Lessons through `PL-ROC-402-014` (48)

### Patches (from review — ALL APPLIED + TESTED 21/21)
C-3 TOCTOU re-check · C-1 SHM cleanup · B-2 dynamic tables · NB-1 trip-wire vs projected ·
B-1 `-f` warning + force param removed · NF-3 staleness warning. R-4 freeze banner added.

### Next steps
1. ✅ ~~Apply 6 patches~~ — DONE (battery A–I: 21/21 PASS)
2. **User GO** → close OpenCode FIRST (R-2), then `run --overwrite` (foreground, NO `--await-exit`, ~5 min), then `swap` immediately
3. `swap` — 43.38 GiB backup copy takes **1.5–4 min** (progress every 15 s — not a stall)
4. Verify: root ≈ 22–24 GB free · `wal` · `quick_check` ok · **OpenCode UI check on old sessions** (R-3)
5. Confirm services healthy (`podman ps`) — no stop/start needed (old restart step was void)
6. Delete `backup_pre_compact_<TS>` on omega ONLY after UI verification