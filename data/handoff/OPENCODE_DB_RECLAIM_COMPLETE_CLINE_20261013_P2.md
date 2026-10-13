<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# ✅ Reclaim Handoff Part 2/3: Timeline + Discoveries D1–D3

## 📜 Timeline (UTC 2026-10-13)

1. **01:14 — Dry-run gate refusal (correct).** Backup verified (FK-clean, parity 3139/3139), Gate 4 found OpenCode PID 264270 → exit 10, no mutation.
2. **01:20–01:23 — Operator closed OpenCode.** Lock clear (`fuser` exit 1). Relaunched `--dry-run`.
3. **01:23–01:29 — Two silent dry-run deaths (bug hunt).** Exited with NO log line, NO code after `backup verification: PASS`. Root-caused to D1+D2. Fixed + hardened all captures.
4. **01:33–01:38 — Dry-run PASSED.** Gates green; **DELETE 114,021 / KEEP 1,033 orphans**. Zero writes.
5. **01:45–01:49 — `--execute` A→E clean.** Pre: `session=3139 message=168277 part=702387 event=461150 event_sequence=1907`. Phase B: 24 batches → 114,021 removed. Post-delete: non-event tables unchanged ✅. VACUUM INTO → 6.56 GB. Reclaimed FK-clean + parity ✅. Swap → `quick_check: ok` → COMPLETE.
6. **01:49–01:53 — Root 99%.** 27 GB rollback on `/`. Started `mv` to HDD.
7. **~01:53 — OOM killed Cline CLI + `mv` mid-copy.** 2.6 GB partial on HDD. Cause: `integrity_check` + `sha256sum` + reclaim + 99% root on 14 GiB box. Removed partial, retried under `ionice -c 3`.
8. **01:56–02:08 — Move completed.** Root 99% → 73% (29 GB free).
9. **02:08–02:10 — Verified.** `quick_check`=ok; 3139/168277/347129 match log.

## 🔍 D1. `timeout`-kill ⇒ false-PASS — HIGH
`BK_FK=$(timeout 300 sqlite3 … "PRAGMA foreign_key_check;" | head -3)`: kill (rc=124) yields EMPTY output, `[ -n "$BK_FK" ]` false → gate PASSES unexecuted work. 300s was unachievable: parallel `integrity_check` on the same HDD file starved the FK scan (in `D` state at 5+ min).
**Fix:** `BK_FK_TIMEOUT` (1800s default, env-override), rc capture under `set +e`, 124 → `die 20` naming contention + override. Same for Phase D FK.
**Residual:** standalone `integrity_check` never finished (OOM in `D` state). Declared moot: quick_check + FK + 3139/3139 parity + sha256 suffice. Never re-run concurrently.

## 🔍 D2. `fuser` exit-1 + `set -euo pipefail` = silent death — HIGH
`HOLDERS=$(fuser "$SRC" …)`: `fuser` exits **1** when nothing holds the file — Gate 4's SUCCESS case. Nonzero in `$(…)` under `set -e -o pipefail` kills the script with NO log, NO code. Reproduced isolated. Caused both silent deaths.
**Fix:** `|| true` on every `$(fuser …)` (Gate 4 + Phase E) with load-bearing comment. Verified: `DB is unlocked: PASS`.
**Rule:** any `$(…)` over clean-nonzero commands (`fuser`, `grep -c` zero, `diff`) MUST carry `|| true` under `set -euo pipefail`. Recommend audit of `scripts/`.

## 🔍 D3. Gate 4 must exclude own tree — MEDIUM
Own read-only sqlite3 helpers briefly hold `$SRC` during Gate 4 → naive `fuser` self-triggers false exit-10. Observed once.
**Fix:** `sleep 2` settle + 5-attempt poll, `$$`/`$PPID` + ancestor-chain filter; only external holders refuse. Phase E same.

*Continues in P3 (D4–D6, corrections table, caveats, next actions).*

*⬡ OMEGA ⬡ CLINE ⬡ COMPLETION-HANDOFF-2/3 ⬡ opencode-db-reclaim-20261013 ⬡ 2026-10-13*
