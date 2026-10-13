<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# ✅ Reclaim Handoff Part 3/3: D4–D6, Corrections, Caveats, Next Actions

## 🔍 D4. All `$(sqlite3…)` captures were silent-death/garbage vectors — MEDIUM
Failed/timed-out count kills silently under `set -e`, or empty text compares numerically. Hardened ALL: dry-run DEL/KEEP (`timeout 600`, rc + numeric `case`, `die 10`), Phase A pre-state (`die 30`), post-state (`die 30`), Phase D counts (`die 50`).
**Pattern:** `set +e` → `OUT; RC=$?` → `set -e` → 124-check → nonzero-check → numeric `case` → compare.

## 🔍 D5. Serialize giant-file ops on Node 0 — LOW
Rollback `mv` ≈2.5 GB/min under `ionice -c 3`, survived once 27 GB scanners were dead. OOM = `integrity_check` + `sha256sum` + reclaim + 99% root colliding. Rule: **one giant-file reader/writer at a time** on 14 GiB box.

## 🔍 D6. Live-vs-backup sha256 differ while OpenCode live — not a signal
WAL + in-flight writes. Parity + FK is the gate; hash is provenance only.

## 🔧 Corrections in `scripts/opencode_db_reclaim.sh` (`bash -n` clean)

| # | Location | Before | After |
|---|---|---|---|
| 1 | Gate 3 FK | `timeout 300 \| head -3`, kill ⇒ false PASS | `BK_FK_TIMEOUT` 1800s, rc capture, 124 ⇒ `die 20` |
| 2 | Gate 3 parity | Bare captures, numeric compare | OUT+rc; 124/non-numeric ⇒ `die 20` |
| 3 | Gate 4 | `HOLDERS=$(fuser …)` silent-death + self-trigger | Settle + 5-poll, own-tree filter, `\|\| true` |
| 4 | Dry-run counts | Bare captures | rc + shape guards, `die 10` |
| 5 | Phase A pre-state | 5 bare captures | Hardened, `die 30` |
| 6 | Post-delete state | 5 bare captures | Hardened, `die 30` |
| 7 | Phase D FK+counts | 300s FK, bare captures | 1800s FK w/ rc (`die 50`), counts hardened |
| 8 | Phase E swap gate | `fuser "$SRC" "$SRC_WAL"` bare | `set +e` + `\|\| true`, own-tree filter, `die 60` |

No gate can now pass on unexecuted work, die without a log line, or mistake our helpers for OpenCode. Exit contract 0/10/20/30/40/50/60 honored on timeout paths.

## ⚠️ Caveats

1. `integrity_check` never completed — declared moot (see D1). Do not re-run concurrently; solo + `ionice -c 3` + hours if ever wanted.
2. OOM root cause is best-evidence (D5), no kernel log access. If OOMs recur without giant-file concurrency, escalate to host diagnostics.
3. `sha256.txt` live-hash predates the swap — provenance for the backup only. Live integrity rests on quick_check + parity (stronger claim).
4. Staging `opencode-reclaimed.db` (6.6 GB) now redundant — remove after soak to free `omega_library` space.
5. Two 42 GB Oct-1 backups + Oct-5 27 GB compact remain; expendable if HDD needed (6.7 TB free — not urgent).

## 📋 Next Actions for Makali (none blocking)

1. Reopen OpenCode; confirm session list + open one.
2. After one clean session: delete staging duplicate; keep rollback ≥ 7 days.
3. Move `OPENCODE_DB_RECLAIM_CLINE_ASSIST_20261013.md` to `data/handoff/completed/` (superseded by P1–P3).
4. Consider D2 `|| true` grep-audit across `scripts/`.
5. M11 candidates: timeout-kill false-PASS antipattern (capture rc); `fuser`-under-`set -e` silent death; serialize giant-file ops on Node 0.

*⬡ OMEGA ⬡ CLINE ⬡ COMPLETION-HANDOFF-3/3 ⬡ opencode-db-reclaim-20261013 ⬡ 2026-10-13*
