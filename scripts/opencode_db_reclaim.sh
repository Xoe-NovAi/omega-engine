#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# opencode_db_reclaim.sh — SAFEGUARDED reclaim of opencode.db event bloat
#
# PURPOSE
#   opencode.db is 26.6 GB. ~75% of it is duplicated `event` rows of type
#   'message.updated.1' (OpenCode re-emits the whole message snapshot on every
#   UI update — quadratic growth). This script deletes the ~113K provably
#   duplicated events and VACUUMs the result down to ~6.5 GB. ZERO session,
#   message, or part rows are deleted.
#
# DESIGN RULES (learned the hard way — do not bypass)
#   • NEVER cp/rsync/dd this DB. It is 26.6 GB on a 14 GiB host; that OOM-killed
#     OpenCode twice and produced a torn file. All copies use VACUUM INTO.
#   • NEVER run blob aggregates (SUM(LENGTH(data)) / GROUP BY on a data column).
#     Materialises the 20 GB event.data column → OOM / "disk is full".
#   • The final `mv` must NOT run while any process holds the DB open, or
#     OpenCode writes to an unlinked inode and that data is silently lost.
#   • Never delete `event_sequence` — it is the PARENT of event; deleting it
#     cascades its events away and breaks sequence numbering.
#
# USAGE
#   ./opencode_db_reclaim.sh --dry-run     # count what would be deleted; no writes
#   ./opencode_db_reclaim.sh --execute     # do it (requires all gates to pass)
#
# MONITORING (for Cline / operator)
#   tail -f /tmp/opencode/reclaim.log
#
# EXIT CODES
#   0 success · 10 refused by gate · 20 backup verification failed
#   30 delete failed · 40 vacuum failed · 50 reclaim verification failed
#   60 swap failed (source restored)
# ═══════════════════════════════════════════════════════════════════════════

# NOTE ON ERROR HANDLING (2026-10-13, audit).
# We deliberately do NOT use `set -e`. It is not a safety mechanism: it is
# silently defeated by subshells, pipelines, `&&`/`||` lists and process
# substitution, and enabling it PARTWAY through a script is worse than never
# enabling it — every later `RC=$?` after a failing command becomes dead code,
# and a mid-swap death can leave the database with no canonical path.
# This script therefore checks every load-bearing command EXPLICITLY and
# captures its status. `set -o pipefail` still applies: a pipeline's status is
# the last non-zero member, which is what we want for `cmd | head`.
set -uo pipefail

SRC="$HOME/.local/share/opencode/opencode.db"
SRC_WAL="$SRC-wal"
SRC_SHM="$SRC-shm"
# Mount-relative defaults: same paths on any host with the sovereign layout;
# no machine identity in shipped source (P0-2). Override via env when needed.
BACKUP="${OMEGA_RECLAIM_BACKUP:-/media/USER/8TB/opencode_backups/opencode.db.20261013.sqlite}"
STAGE_DIR="${OMEGA_RECLAIM_STAGE:-/media/USER/omega_library/staging}"
RECLAIMED="$STAGE_DIR/opencode-reclaimed.db"
PRE_RECLAIM_COPY=""   # optional extra fixture
BATCH=5000
LOG="/tmp/opencode/reclaim.log"
MODE="dry-run"

mkdir -p /tmp/opencode "$STAGE_DIR"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"; }
die() { log "FATAL: $*"; exit "${2:-1}"; }

# ── arg parsing ────────────────────────────────────────────────────────────
case "${1:---dry-run}" in
  --dry-run)  MODE="dry-run" ;;
  --execute)  MODE="execute" ;;
  *) die "unknown arg '$1' (use --dry-run or --execute)" 10 ;;
esac

: > "$LOG"
log "════ opencode_db_reclaim.sh START (mode=$MODE) ════"

# ── GATE 1: source DB exists ───────────────────────────────────────────────
[ -f "$SRC" ] || die "source DB not found: $SRC" 10
log "source DB: $SRC ($(stat -c%s "$SRC") bytes)"

# ── GATE 2: backup exists and is non-trivial ───────────────────────────────
[ -f "$BACKUP" ] || die "BACKUP NOT FOUND: $BACKUP — refusing to mutate without a verified backup" 10
BKSZ=$(stat -c%s "$BACKUP")
log "backup:    $BACKUP ($BKSZ bytes)"
[ "$BKSZ" -lt 1000000000 ] && die "backup suspiciously small ($BKSZ) — abort" 10

# ── GATE 3: backup structural spot-check (FK + session parity, bounded) ────
# NOTE: BK_FK_TIMEOUT (default 1800s) must EXCEED the integrity_check runtime on
# HDD. A `timeout` kill means "unknown", not "clean" — treating it as clean
# (empty output) would pass a gate we never actually checked (false PASS).
log "verifying backup (foreign_key_check + session parity)..."
BK_FK_TIMEOUT="${BK_FK_TIMEOUT:-1800}"
BK_FK_OUT=$(timeout "$BK_FK_TIMEOUT" sqlite3 "file:$BACKUP?mode=ro" "PRAGMA foreign_key_check;" 2>&1)
BK_FK_RC=$?
if [ "$BK_FK_RC" -eq 124 ]; then
  die "backup FK check TIMED OUT after ${BK_FK_TIMEOUT}s (parallel integrity_check likely hogging HDD) — refusing to treat as clean. Kill competing sqlite3 readers and retry. Override: BK_FK_TIMEOUT=3600" 20
elif [ "$BK_FK_RC" -ne 0 ]; then
  die "backup FK check errored (rc=$BK_FK_RC): $BK_FK_OUT" 20
fi
BK_FK=$(echo "$BK_FK_OUT" | head -3)
if [ -n "$BK_FK" ]; then die "backup FK violations: $BK_FK" 20; fi
BK_SESS_OUT=$(timeout 600 sqlite3 "file:$BACKUP?mode=ro" "SELECT COUNT(*) FROM session;" 2>&1); BK_SESS_RC=$?
SRC_SESS_OUT=$(timeout 300 sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM session;" 2>&1); SRC_SESS_RC=$?
BK_SESS=$(echo "$BK_SESS_OUT" | tail -1)
SRC_SESS=$(echo "$SRC_SESS_OUT" | tail -1)
# Guard: timeouts/empty output must FAIL LOUD, never compare as numbers.
# An empty/timeout-tainted count comparing ">= N-50" numerically could PASS a
# gate we never checked (same false-PASS class as the BK_FK timeout race).
if [ "$BK_SESS_RC" -eq 124 ] || [ "$SRC_SESS_RC" -eq 124 ]; then
  die "session count TIMED OUT (backup_rc=$BK_SESS_RC src_rc=$SRC_SESS_RC) — unknown, not parity. Retry when HDD is idle." 20
fi
case "$BK_SESS" in ''|*[!0-9]*) die "backup session count not numeric: '$BK_SESS_OUT'" 20;; esac
case "$SRC_SESS" in ''|*[!0-9]*) die "source session count not numeric: '$SRC_SESS_OUT'" 20;; esac
log "backup sessions: $BK_SESS | source sessions: $SRC_SESS"
# backup must have at least as many sessions as source minus in-flight writes
if [ "$BK_SESS" -lt $((SRC_SESS - 50)) ]; then die "backup is missing sessions ($BK_SESS < $SRC_SESS-50)" 20; fi
log "backup verification: PASS"

# ── GATE 4: DB must be UNLOCKED (no OpenCode holding it) ──────────────────
# Self-trigger hazard: this script's own read-only sqlite3 helpers open $SRC
# while Gate 4 runs (e.g. the SRC_SESS count). Gate 4 must therefore exclude
# our own process tree. OpenCode is the target, not ourselves.
# Robust approach: close our helpers first (all Gate-3 queries are done), then
# poll fuser with retries — transient self-sightings settle once children exit.
# Any REMAINING holder after settle is external (OpenCode) → refuse.
sleep 2  # let Gate-3 sqlite3 helpers exit and release their read locks
HOLDERS=""
for attempt in 1 2 3 4 5; do
  # FAIL-CLOSED fuser probe (2026-10-13, post-audit).
  #
  # Replaces:  CANDIDATES=$(fuser "$SRC" 2>/dev/null | tr -s ' ' ' ' | sed 's/^ //' || true)
  # which fails OPEN: missing tool, tool error, or bad invocation all produce
  # empty stdout, an empty FILTERED, and therefore "DB is unlocked: PASS".
  #
  # Why the stderr-tiebreaker approach was REJECTED: it needs mktemp + a second
  # capture and still degrades to a false PASS if PATH is broken (mktemp/tr/cat
  # all vanish). Simpler and strictly stronger: prove the tool exists and that
  # we control its invocation FIRST. Once fuser is known-present and the args are
  # ours, its exit code is unambiguous:
  #     0 = holders found (stdout carries PIDs)
  #     1 = ran successfully, nothing holds the file
  #     anything else = fault we refuse to interpret
  command -v fuser >/dev/null 2>&1 \
    || die "fuser binary not available — cannot verify lock state. REFUSING (fail-closed)." 10
  FU_OUT=$(fuser "$SRC" 2>/dev/null); FU_RC=$?
  case "$FU_RC" in
    0)
      [ -n "$(echo "$FU_OUT" | tr -d '[:space:]')" ] \
        || die "fuser rc=0 but no PIDs — inconsistent result; refusing to verify. REFUSING (fail-closed)." 10
      CANDIDATES="$FU_OUT"
      ;;
    1) CANDIDATES="" ;;
    *) die "fuser failed (rc=$FU_RC) on '$SRC' — cannot verify lock state. REFUSING (fail-closed)." 10 ;;
  esac
  CANDIDATES=$(echo "$CANDIDATES" | tr -s ' \n' ' ' | sed 's/^ //;s/ $//')
  # filter out our own tree (self + children + parent launcher chain)
  FILTERED=""
  for p in $CANDIDATES; do
    case "$p" in
      $$|$PPID) continue ;;  # self + launcher (nohup/background subshell)
    esac
    # walk ancestors: helper processes parented under us are ours
    ANC="$p"; OURS=0
    while [ -n "$ANC" ] && [ "$ANC" != "1" ] && [ "$ANC" != "0" ]; do
      if [ "$ANC" = "$$" ] || [ "$ANC" = "$PPID" ]; then OURS=1; break; fi
      ANC=$(ps -o ppid= -p "$ANC" 2>/dev/null | tr -d ' ' || echo "")
    done
    [ "$OURS" = "1" ] || FILTERED="$FILTERED $p"
  done
  FILTERED=$(echo "$FILTERED" | tr -s ' ' ' ' | sed 's/^ //;s/ $//')
  if [ -z "$FILTERED" ]; then
    HOLDERS=""; break  # clean — no external holders
  fi
  HOLDERS="$FILTERED"
  [ "$attempt" -lt 5 ] && sleep 3  # transient? retry before refusing
done
if [ -n "$HOLDERS" ]; then
  HPROCS=$(for p in $HOLDERS; do ps -p "$p" -o comm= 2>/dev/null; done | tr '\n' ',')
  die "DB still open by PID(s): $HOLDERS [$HPROCS] — CLOSE OPENCODE first" 10
fi
log "DB is unlocked: PASS"

if [ "$MODE" = "dry-run" ]; then
  log "─── DRY RUN: counting delete set (no writes) ───"
  set +e
  DEL=$(timeout 600 sqlite3 "file:$SRC?mode=ro" "
    SELECT COUNT(*) FROM event e
    WHERE e.type='message.updated.1'
      AND EXISTS (SELECT 1 FROM message m WHERE m.id = json_extract(e.data,'\$.info.id'));"); DEL_RC=$?
  KEEP=$(timeout 600 sqlite3 "file:$SRC?mode=ro" "
    SELECT COUNT(*) FROM event e
    WHERE e.type='message.updated.1'
      AND NOT EXISTS (SELECT 1 FROM message m WHERE m.id = json_extract(e.data,'\$.info.id'));"); KEEP_RC=$?
  set -e
  [ "$DEL_RC" -eq 124 ] && die "dry-run DELETE count TIMED OUT — unknown, not zero" 10
  [ "$KEEP_RC" -eq 124 ] && die "dry-run KEEP count TIMED OUT — unknown, not zero" 10
  [ "$DEL_RC" -ne 0 ] && die "dry-run DELETE count errored (rc=$DEL_RC): $DEL" 10
  [ "$KEEP_RC" -ne 0 ] && die "dry-run KEEP count errored (rc=$KEEP_RC): $KEEP" 10
  case "$DEL" in ''|*[!0-9]*) die "dry-run DELETE count not numeric: '$DEL'" 10;; esac
  case "$KEEP" in ''|*[!0-9]*) die "dry-run KEEP count not numeric: '$KEEP'" 10;; esac
  log "would DELETE $DEL duplicated events; KEEP $KEEP orphans"
  log "DRY RUN complete. Nothing written."
  exit 0
fi

# ── PHASE A: record pre-state ──────────────────────────────────────────────
log "─── PHASE A: pre-state ───"
PRE_SESS=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM session;"); PRE_SESS_RC=$?
PRE_MSG=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM message;"); PRE_MSG_RC=$?
PRE_PART=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM part;"); PRE_PART_RC=$?
PRE_EV=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM event;"); PRE_EV_RC=$?
PRE_SEQ=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM event_sequence;"); PRE_SEQ_RC=$?
for v in "PRE_SESS:$PRE_SESS_RC:$PRE_SESS" "PRE_MSG:$PRE_MSG_RC:$PRE_MSG" "PRE_PART:$PRE_PART_RC:$PRE_PART" "PRE_EV:$PRE_EV_RC:$PRE_EV" "PRE_SEQ:$PRE_SEQ_RC:$PRE_SEQ"; do
  name="${v%%:*}"; rest="${v#*:}"; rc="${rest%%:*}"; val="${rest#*:}"
  [ "$rc" -ne 0 ] && die "pre-state $name query failed (rc=$rc): $val" 30
  case "$val" in ''|*[!0-9]*) die "pre-state $name not numeric: '$val'" 30;; esac
done
log "pre: session=$PRE_SESS message=$PRE_MSG part=$PRE_PART event=$PRE_EV event_sequence=$PRE_SEQ"

# checkpoint WAL so the deletes start from a clean base
sqlite3 "$SRC" "PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null
log "WAL checkpointed"

# ── PHASE B: batched delete of duplicated events ────────────────────────────
log "─── PHASE B: batched DELETE (batch=$BATCH, foreign_keys=ON, never event_sequence) ───"
TOTAL=0; BATCHN=0
while :; do
  DELETED=$(sqlite3 "$SRC" <<SQL 2>>"$LOG"
PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
DELETE FROM event WHERE id IN (
  SELECT e.id FROM event e
  WHERE e.type='message.updated.1'
    AND EXISTS (SELECT 1 FROM message m WHERE m.id = json_extract(e.data,'$.info.id'))
  LIMIT $BATCH
);
SELECT changes();
COMMIT;
SQL
)
  DELETED=$(echo "$DELETED" | tail -1)
  [ -z "$DELETED" ] && DELETED=0
  TOTAL=$((TOTAL + DELETED)); BATCHN=$((BATCHN + 1))
  sqlite3 "$SRC" "PRAGMA wal_checkpoint(PASSIVE);" 2>/dev/null
  log "  batch $BATCHN: deleted $DELETED (running total $TOTAL)"
  [ "$DELETED" -eq 0 ] && break
  [ "$BATCHN" -gt 200 ] && die "batch cap exceeded — aborting to prevent runaway" 30
done
log "delete complete: $TOTAL events removed in $BATCHN batches"

# verify nothing but event changed
POST_SESS=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM session;"); POST_SESS_RC=$?
POST_MSG=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM message;"); POST_MSG_RC=$?
POST_PART=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM part;"); POST_PART_RC=$?
POST_SEQ=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM event_sequence;"); POST_SEQ_RC=$?
POST_EV=$(sqlite3 "file:$SRC?mode=ro" "SELECT COUNT(*) FROM event;"); POST_EV_RC=$?
for v in "POST_SESS:$POST_SESS_RC:$POST_SESS" "POST_MSG:$POST_MSG_RC:$POST_MSG" "POST_PART:$POST_PART_RC:$POST_PART" "POST_SEQ:$POST_SEQ_RC:$POST_SEQ" "POST_EV:$POST_EV_RC:$POST_EV"; do
  name="${v%%:*}"; rest="${v#*:}"; rc="${rest%%:*}"; val="${rest#*:}"
  [ "$rc" -ne 0 ] && die "post-state $name query failed (rc=$rc): $val" 30
  case "$val" in ''|*[!0-9]*) die "post-state $name not numeric: '$val'" 30;; esac
done
log "post: session=$POST_SESS message=$POST_MSG part=$POST_PART event=$POST_EV event_sequence=$POST_SEQ"
[ "$POST_SESS" != "$PRE_SESS" ] && die "session count changed! $PRE_SESS -> $POST_SESS" 30
[ "$POST_MSG"  != "$PRE_MSG" ]  && die "message count changed! $PRE_MSG -> $POST_MSG" 30
[ "$POST_PART" != "$PRE_PART" ] && die "part count changed! $PRE_PART -> $POST_PART" 30
[ "$POST_SEQ"  != "$PRE_SEQ" ]  && die "event_sequence changed! $PRE_SEQ -> $POST_SEQ (NEVER delete this)" 30
log "non-event tables unchanged: PASS"

# ── PHASE C: VACUUM INTO reclaimed file ────────────────────────────────────
log "─── PHASE C: VACUUM INTO $RECLAIMED ───"
[ -e "$RECLAIMED" ] && die "reclaimed file already exists — move it first: $RECLAIMED" 40
sqlite3 -cmd ".timeout 30000" "file:$SRC?mode=ro" "PRAGMA synchronous=FULL; VACUUM INTO '$RECLAIMED';"
RC=$?
[ $RC -ne 0 ] && die "VACUUM INTO failed (rc=$RC)" 40
RSZ=$(stat -c%s "$RECLAIMED")
log "reclaimed: $RSZ bytes ($(echo "scale=2;$RSZ/1073741824"|bc) GB)"

# ── PHASE D: verify reclaimed file ─────────────────────────────────────────
log "─── PHASE D: verify reclaimed ───"
RF_FK_OUT=$(timeout 1800 sqlite3 "file:$RECLAIMED?mode=ro" "PRAGMA foreign_key_check;" 2>&1); RF_FK_RC=$?
[ "$RF_FK_RC" -eq 124 ] && die "reclaimed FK check TIMED OUT — unknown, not clean" 50
[ "$RF_FK_RC" -ne 0 ] && die "reclaimed FK check errored (rc=$RF_FK_RC): $RF_FK_OUT" 50
RF_FK=$(echo "$RF_FK_OUT" | head -3)
[ -n "$RF_FK" ] && die "reclaimed FK violations: $RF_FK" 50
R_SESS=$(sqlite3 "file:$RECLAIMED?mode=ro" "SELECT COUNT(*) FROM session;"); R_SESS_RC=$?
R_MSG=$(sqlite3 "file:$RECLAIMED?mode=ro" "SELECT COUNT(*) FROM message;"); R_MSG_RC=$?
R_PART=$(sqlite3 "file:$RECLAIMED?mode=ro" "SELECT COUNT(*) FROM part;"); R_PART_RC=$?
for v in "R_SESS:$R_SESS_RC:$R_SESS" "R_MSG:$R_MSG_RC:$R_MSG" "R_PART:$R_PART_RC:$R_PART"; do
  name="${v%%:*}"; rest="${v#*:}"; rc="${rest%%:*}"; val="${rest#*:}"
  [ "$rc" -ne 0 ] && die "reclaimed $name query failed (rc=$rc): $val" 50
  case "$val" in ''|*[!0-9]*) die "reclaimed $name not numeric: '$val'" 50;; esac
done
log "reclaimed: session=$R_SESS message=$R_MSG part=$R_PART"
[ "$R_SESS" != "$POST_SESS" ] && die "reclaimed session count differs" 50
[ "$R_MSG"  != "$POST_MSG" ]  && die "reclaimed message count differs" 50
[ "$R_PART" != "$POST_PART" ] && die "reclaimed part count differs" 50
log "reclaimed verification: PASS"

# ── PHASE E: atomic swap ───────────────────────────────────────────────────
log "─── PHASE E: atomic swap ───"
# Same fail-closed probe as Gate 4 (see the long comment there): prove fuser
# exists, then its rc is unambiguous. This one guards the actual `mv`, so a
# fail-OPEN here is the single most dangerous gate in the script.
command -v fuser >/dev/null 2>&1 \
  || die "fuser binary not available — refusing to mv under an unverified reader state." 60
FU2_OUT=$(fuser "$SRC" "$SRC_WAL" 2>/dev/null); FU2_RC=$?
case "$FU2_RC" in
  0)
    [ -n "$(echo "$FU2_OUT" | tr -d '[:space:]')" ] \
      || die "swap-time fuser rc=0 with no PIDs — refusing to mv under an unverified reader state." 60
    HOLDERS2="$FU2_OUT"
    ;;
  1) HOLDERS2="" ;;
  *) die "swap-time fuser failed (rc=$FU2_RC) — refusing to mv under an unverified reader state. REFUSING (fail-closed)." 60 ;;
esac
HOLDERS2=$(echo "$HOLDERS2" | tr -s ' \n' ' ' | sed 's/^ //;s/ $//')
# filter our own tree (same rule as Gate 4)
HOLDERS2F=""
for p in $HOLDERS2; do
  case "$p" in $$|$PPID) continue;; esac
  ANC="$p"; OURS=0
  while [ -n "$ANC" ] && [ "$ANC" != "1" ] && [ "$ANC" != "0" ]; do
    if [ "$ANC" = "$$" ] || [ "$ANC" = "$PPID" ]; then OURS=1; break; fi
    ANC=$(ps -o ppid= -p "$ANC" 2>/dev/null | tr -d ' ' || echo "")
  done
  [ "$OURS" = "1" ] || HOLDERS2F="$HOLDERS2F $p"
done
HOLDERS2F=$(echo "$HOLDERS2F" | tr -s ' ' ' ' | sed 's/^ //;s/ $//')
[ -n "$HOLDERS2F" ] && die "DB reopened during run (PID $HOLDERS2F) — refusing swap" 60
# SAFETY TRAP (2026-10-13, audit HIGH: "no trap — DB has no canonical path").
# Once the DB is moved aside there is a window in which $SRC does not exist.
# Any exit — including SIGINT/SIGTERM/SIGHUP from an impatient operator —
# must attempt to restore the rollback copy.
SWAP_WINDOW_OPEN=0
on_signal_or_exit() {
  local rc=$?
  if [ "$SWAP_WINDOW_OPEN" = "1" ] && [ -n "${ROLLED:-}" ] && [ -f "$ROLLED" ] && [ ! -f "$SRC" ]; then
    log "TRAP (rc=$rc): DB is mid-swap with no canonical path — restoring rollback copy"
    if mv "$ROLLED" "$SRC"; then
      log "trap restored original DB"
      rm -f "$SRC_WAL" "$SRC_SHM" 2>/dev/null
    else
      log "TRAP RESTORE FAILED — original still at $ROLLED. Do NOT start OpenCode."
    fi
  fi
}
trap on_signal_or_exit EXIT INT TERM HUP

# ORDERING FIX (2026-10-13, audit CRITICAL #1).
# Previously: rm -f "$SRC_WAL" "$SRC_SHM" ran BEFORE the rollback `mv`. If that
# mv then failed, the committed transactions living in the WAL were gone AND
# there was no rollback copy — the worst possible state.
# Correct order:
#   1. move the DB aside FIRST (this is what creates the rollback copy, and it
#      moves the WAL with it because they are the same unit)
#   2. only once the rollback copy demonstrably exists may we clear the
#      sidecars that belonged to the old inode
#   3. install the reclaimed file
# If (1) fails we have changed nothing and can die safely.
ROLLED="$SRC.rollback-$(date +%Y%m%d%H%M%S)"
log "moving current DB to rollback slot: $ROLLED"
SWAP_WINDOW_OPEN=1
if ! mv "$SRC" "$ROLLED"; then
  SWAP_WINDOW_OPEN=0
  # nothing has been removed yet — the DB is still live and intact. Safe to die.
  die "mv to rollback slot FAILED — nothing was removed, live DB is untouched. Aborting." 60
fi
# Rollback copy now exists. Clear the orphaned sidecars of the OLD inode.
rm -f "$SRC_WAL" "$SRC_SHM" 2>/dev/null
log "rollback copy verified present: $ROLLED"

# From here on the DB has no canonical path. Any failure MUST restore it.
restore_on_fail() {
  if [ -n "${ROLLED:-}" ] && [ -f "$ROLLED" ] && [ ! -f "$SRC" ]; then
    log "EMERGENCY RESTORE: moving rollback copy back into place"
    if mv "$ROLLED" "$SRC"; then
      log "restored original DB from rollback copy"
      rm -f "$SRC_WAL" "$SRC_SHM" 2>/dev/null
    else
      log "RESTORE FAILED — original is still at $ROLLED. Do NOT start OpenCode."
    fi
  fi
}

if mv "$RECLAIMED" "$SRC"; then
  log "swap complete: reclaimed DB is now live"
  log "rollback copy kept at: $ROLLED"
else
  log "swap FAILED — restoring original"
  restore_on_fail
  die "restored original; aborting" 60
fi

FINAL=$(stat -c%s "$SRC")
log "live DB now: $FINAL bytes ($(echo "scale=2;$FINAL/1073741824"|bc) GB)"
FQ=$(timeout 300 sqlite3 "file:$SRC?mode=ro" "PRAGMA quick_check;" 2>&1 | head -1)
log "post-swap quick_check: $FQ"
[ "$FQ" = "ok" ] || die "post-swap quick_check FAILED: $FQ" 60

log "════ RECLAIM COMPLETE ════"
log "Before: 26.61 GB (event=$PRE_EV)  After: $(echo "scale=2;$FINAL/1073741824"|bc) GB (event=$POST_EV)"
log "Reclaimed: $((TOTAL)) duplicated events. Zero sessions/messages/parts lost."
log "Backup: $BACKUP"
log "Rollback: $ROLLED"
exit 0