<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🆘 Cline Assist Handoff — OpenCode DB Reclaim (Mid-Cleanup)

**Task ID**: `opencode-db-reclaim-20261013`
**From**: roc_racoon (OpenCode channel)
**To**: cline
**Date**: 2026-10-13
**Priority**: 2 (critical) — only needed if the operator needs help mid-cleanup

---

## 🎯 Why You Exist

The operator is running a **multi-step reclaim of a 26.6 GB SQLite database**
(`~/.local/share/opencode/opencode.db`). If something goes wrong mid-process and the
operator **cannot open OpenCode** (the TUI is closed during the swap), **you are the
fallback agent.**

You are NOT the primary executor. roc_racoon runs the steps. You exist to:
- diagnose a failed step,
- run bounded verification queries,
- restore from backup if something broke.

---

## ⛔ HARD RULES — READ BEFORE ANYTHING

**These exist because they already broke the operator twice.**

1. ❌ **NEVER `cp`, `rsync`, or `dd` the opencode.db.** It is 26.6 GB on a 14 GiB RAM
   box. This **OOM-killed the OpenCode TUI twice** and produced a **torn file** (26.7 GB
   written of 28.2 GB, `database disk image is malformed`). Streaming via `VACUUM INTO`
   is the ONLY sanctioned way to copy this DB.
2. ❌ **NEVER run aggregates over blob/text columns** (`SUM(LENGTH(data))`, `GROUP BY`
   on a data column). Materialises the 20 GB `event.data` column → OOM / `disk is full`.
3. ❌ **NEVER `dbstat` without `WHERE aggregate=TRUE`.**
4. ❌ **NEVER read-write / DELETE / VACUUM the live production DB** except during the
   explicitly-authorized Phase 2.
5. ✅ **Read the live DB only via `ocdb-ro`** (read-only, ~/.local/bin/ocdb-ro). Bounded
   queries only (indexed WHERE, COUNT of ids, LIMIT).
6. ✅ **Keep memory under ~1 GB.** If a query needs more, it is the wrong query.

---

## 📍 Paths

| Thing | Path |
|---|---|
| Live DB | `~/.local/share/opencode/opencode.db` (+ `-wal`, `-shm`) |
| Staging copy (Oct-5 compacted) | `/media/arcana-novai/omega_library/staging/opencode-compact.db` |
| **8TB external (backup target)** | `/media/arcana-novai/8TB/opencode_backups/` |
| Reclaimed-file scratch | `/media/arcana-novai/omega_library/staging/` |
| Sanctioned read tool | `ocdb-ro` |
| Research + protocol docs | `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_DB_*.md`, `OPENCODE_2X_UPGRADE_RESEARCH_20261013.md` |

---

## 📋 Phases (roc_racoon runs these; you only help if asked)

**Phase 1 — Backup (live-safe, source read-only):**
1. `VACUUM INTO '/media/arcana-novai/8TB/opencode_backups/opencode.db.20261013.sqlite'`
2. Verify: `quick_check` → `foreign_key_check` → `integrity_check` → 21-table row parity vs source
3. sha256 manifest

**Phase 2 — Reclaim (operator must have CLOSED the OpenCode TUI):**
4. Batched DELETE of duplicated `event` rows `type='message.updated.1'` (only where the
   message exists). 2,000–5,000 rows/transaction, `wal_checkpoint(PASSIVE)` each batch,
   resumable/idempotent.
5. `VACUUM INTO /media/arcana-novai/omega_library/staging/opencode-reclaimed.db` (~6.5 GB)
6. Verify reclaimed file vs backup
7. Atomic `mv` into live path

---

## 🎯 PRIMARY MECHANISM — Standalone Script (Option A)

**The reclaim is fully scripted.** Cline's job is to *run and monitor* it, not to
hand-execute SQL.

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Confirm OpenCode is CLOSED (the script refuses otherwise, but check first):
fuser ~/.local/share/opencode/opencode.db 2>/dev/null && echo "STILL OPEN - abort" || echo "clear"

# 2. Dry run (read-only, safe):
./scripts/opencode_db_reclaim.sh --dry-run

# 3. Execute:
nohup ./scripts/opencode_db_reclaim.sh --execute > /tmp/opencode/reclaim.out 2>&1 &

# 4. MONITOR (this is the main job):
tail -f /tmp/opencode/reclaim.log
```

### Exit codes Cline must interpret
| Code | Meaning | Action |
|---:|---|---|
| 0 | Success | Verify, report reclaimed size |
| 10 | Refused by a gate (DB open / no backup) | **Do not bypass.** Tell operator to close OpenCode |
| 20 | Backup verification failed | **STOP.** Do not proceed |
| 30 | Delete failed / non-event table changed | **STOP.** Restore |
| 40 | VACUUM INTO failed | Investigate disk space |
| 50 | Reclaimed verification failed | **STOP.** Do not swap |
| 60 | Swap failed (original auto-restored) | Report; original is safe |

### What the script does automatically (do NOT duplicate these by hand)
- Verifies the backup exists + FK-clean + session parity
- **Refuses to run if any process holds the DB open** (the `mv` safety gate)
- Batched delete (5000/txn), `foreign_keys=ON`, checkpoint per batch
- Asserts session/message/part/event_sequence counts **unchanged** after delete
- `VACUUM INTO` the reclaimed file, verifies it, atomic swap
- Keeps the pre-swap DB as `opencode.db.rollback-<timestamp>` and auto-restores on failure

### Expected output
- `event` drops by ~113,000; `session`/`message`/`part`/`event_sequence` unchanged
- Live DB shrinks 26.61 GB → ~6.5 GB
- Log ends with `════ RECLAIM COMPLETE ════`

---

## 🔧 If You Need To Help (diagnostics only)

**Diagnose a failed verification:**
```bash
ocdb-ro "PRAGMA quick_check"          # note: quick_check SKIPS foreign keys
ocdb-ro "SELECT COUNT(*) FROM session"
ocdb-ro "SELECT COUNT(*) FROM event"
```
`quick_check` on a 26 GB DB may take a while — be patient, don't kill it.

**Restore from the 8TB backup (last resort):**
```bash
# ONLY if roc_racoon explicitly authorizes AND OpenCode is closed.
# Use streaming, never cp:
sqlite3 "/media/arcana-novai/8TB/opencode_backups/opencode.db.20261013.sqlite" \
        "VACUUM INTO '/home/arcana-novai/.local/share/opencode/opencode.db'"
```

**Rollback files that already exist (DO NOT DELETE):**
- `/media/arcana-novai/8TB/opencode_backups/opencode.db.backup.20261001-185446.sqlite` (41.4 GB)
- `/media/arcana-novai/8TB/opencode_backups/opencode.db.backup.20261001-191216.sqlite` (41.4 GB)
- `/media/arcana-novai/omega_library/staging/opencode-compact.db` (26.3 GB)

---

## 🧠 Key Facts (so you don't have to re-derive)

- DB is 26.6 GB but **only ~1.8 GB is `part.data`**; **74.7% is duplicated
  `event` rows of type `message.updated.1`** (streaming UI snapshots re-emitted per update).
- `freelist_count=0` → the file is fully allocated; a plain VACUUM returns ≤765 MiB.
  **The reclaim deletes redundant events, then VACUUM INTO.** Deleting alone won't shrink
  the file.
- ~113K of ~114K `message.updated.1` events are provably duplicated in `message`; ~1,033
  are orphans that MUST be retained (the `EXISTS` gate handles this).
- **Never delete `event_sequence`** (it cascades its events away — wrong direction).
- The event delete-set is invisible to the pending OpenCode 2.0 migration (which reads
  `session`/`message`/`part`, not `event`).

---

## 📎 Referenced prior art

- `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_DB_AGENT_PROTOCOL_20261013.md`
  — the OOM-safe protocol codified after 2 crashes.
- Skill: `~/.agents/skills/opencode-db/SKILL.md` — sanctioned read tooling; documents
  a prior read-write incident on production (records `3becf4f3`, `a3675a88`).

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ CLINE-ASSIST-HANDOFF ⬡ opencode-db-reclaim-20261013 ⬡ 2026-10-13*