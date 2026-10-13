# Reclaiming a Bloated SQLite Database

**How to shrink a SQLite database that has grown far larger than its data — safely, without losing a single row.**

> **Verified result:** a 26.6 GB session database reduced to **6.58 GB** (75% reclaimed),
> 113,534 redundant rows deleted, **zero sessions, messages, or parts lost**,
> foreign keys intact, `quick_check` clean.

---

## The shape of the problem

Almost every bloated SQLite database has the same cause: **an append-only event
log that re-emits full state snapshots on every update.**

A UI streams "message updated" events. Each event carries the *entire* message
as it stands at that moment. The application only ever displays the newest one —
but the database keeps all of them, forever. Growth becomes **quadratic** in the
number of updates.

In the measured case:

| consumer | size | share |
|---|---:|---:|
| `event` rows of type `message.updated.1` | 20,358 MiB | **74.7%** |
| `message.data` | 3,494 MiB | 12.8% |
| `part.data` | 1,846 MiB | 6.8% |
| other events | 764 MiB | 2.8% |
| indexes + headers | ~765 MiB | 2.8% |

**114,708 redundant snapshot rows across 270 conversations.** One conversation
alone accounted for 37,480 snapshots — 6.76 GiB. Its actual text was a few
megabytes.

### The diagnostic that settles it

Before deleting anything, find out where the bytes actually are. On any recent
SQLite (3.31+):

```sql
SELECT name, SUM(pgsize) AS bytes
FROM dbstat
WHERE aggregate = TRUE          -- 1 row per btree, not one per page
GROUP BY name
ORDER BY bytes DESC;
```

> **The `aggregate = TRUE` clause is not optional.** Without it you get one row
> per *page* — 6.97 million rows on a 26 GB database. On a memory-constrained
> host that will OOM-kill the process reading it. We learned that the expensive
> way.

Then check whether the file has any slack at all:

```sql
PRAGMA page_size;
PRAGMA page_count;
PRAGMA freelist_count;
PRAGMA auto_vacuum;
```

If `freelist_count` is **0**, the file is fully allocated and **a plain `VACUUM`
will recover almost nothing.** The space is not free — it is *duplicated data*.
You have to delete the duplicates.

---

## What `VACUUM` can and cannot do

| operation | reclaims freelist pages? | repacks partially-filled pages? | shrinks a `freelist=0` file? |
|---|:---:|:---:|:---:|
| `DELETE` | no — it *grows* the freelist | no | no |
| `VACUUM` (in place) | yes | yes | partially, once |
| `VACUUM INTO` + rename | yes | yes | partially, once |

Two things surprise people here:

1. **Deleting rows does not shrink the file.** With `auto_vacuum=NONE` (the
   default), `DELETE` just marks pages free for reuse. The file stays exactly
   the same size until you repack.
2. **The repacking lever is not repeatable.** `VACUUM` genuinely can shrink a
   file with `freelist=0`, because it rewrites partially-filled pages more
   densely. In the measured case it recovered **18.3 GB from a 46.5 GB file**.
   But after a full repack, the next `VACUUM` returned **765 MiB**. Do the
   delete first; do not rely on `VACUUM` alone.

**In-place `VACUUM` needs roughly twice the file size in free space.** If you do
not have that, in-place `VACUUM` is not an option — use `VACUUM INTO`.

---

## The procedure

Five phases. Each one is a gate on the next.

### Phase 1 — Back up (streaming, never a file copy)

```bash
SRC="/path/to/live.db"
DEST="/mnt/backup/live-backup.db"
test ! -e "$DEST" || { echo "destination exists — resolve it first"; exit 1; }

sqlite3 -cmd ".timeout 30000" "file:$SRC?mode=ro" \
  "PRAGMA synchronous=FULL; VACUUM INTO '$DEST';"
```

Why each part:

- **`mode=ro`** — `VACUUM INTO` is a *read* on the source. It snapshots and
  writes a new file. This is safe to run while your application has the database
  open; it takes no write lock.
- **`.timeout 30000`** — retries transient `SQLITE_BUSY`.
- **`synchronous=FULL`** — **without this the output is never fsynced.** An
  interrupted run leaves a corrupt file *with a valid header*, which is the
  worst kind of broken.
- **`test ! -e "$DEST"`** — SQLite refuses to overwrite. A pre-existing
  destination is either a half-finished run or a different database. A human
  should decide, not the script.

> **Never `cp`, `rsync`, or `dd` a large SQLite database.**
> On a 14 GiB host, `cp`-ing a 26.6 GB file OOM-killed the agent process — *and*
> wrote a torn file: 26.7 GB of 28.2 GB, valid header, `database disk image is
> malformed (11)`. It looks fine right up until you query it.

`VACUUM INTO` output is **self-contained** — WAL contents are merged in, no
sidecar needed — and needs only the *compacted* size at the destination.

### Phase 2 — Verify the backup

```bash
D=/mnt/backup/live-backup.db

sqlite3 "file:$D?mode=ro" "PRAGMA quick_check;"          # expect: ok
sqlite3 "file:$D?mode=ro" "PRAGMA foreign_key_check;"    # expect: EMPTY
sqlite3 "file:$D?mode=ro" "PRAGMA integrity_check;"      # expect: ok
sha256sum "$D" > "$D.sha256"
```

> **`quick_check` does not verify foreign keys.** A database with broken
> referential integrity can pass it. Run `foreign_key_check` separately.

Then compare row counts per table. Differences in actively-written tables are
expected — the source kept receiving writes during the copy. What must be zero
is **anything structurally missing**, e.g. rows in the backup that do not exist
in the source.

### Phase 3 — Quiesce the application

You cannot safely swap a database file underneath a running reader. See the
hazard in Phase 5.

### Phase 4 — Delete the duplicates, in batches

Identify rows that are provably redundant — those whose current state already
exists in the authoritative table:

```sql
-- 7,881 deletable / 96 orphans retained = 7,977 on the measured slice
SELECT COUNT(*) FROM event e
WHERE e.type='message.updated.1'
  AND EXISTS (SELECT 1 FROM message m WHERE m.id = json_extract(e.data,'$.info.id'));
```

> ⚠️ **Qualify your column references.**
> Written unqualified, `data` inside the correlated subquery binds to the
> *inner* table. The predicate then silently matches **nothing** — reporting
> success while deleting zero rows. Our first full-population check returned
> `found: 0` for all 114,475 rows. `e.data` versus `m.data` is a safety gate,
> not a style choice.

Delete in batches, with foreign keys **on**:

```bash
sqlite3 "$DB" <<SQL
PRAGMA foreign_keys=ON;
BEGIN IMMEDIATE;
DELETE FROM event WHERE id IN (
  SELECT e.id FROM event e
  WHERE e.type='message.updated.1'
    AND EXISTS (SELECT 1 FROM message m WHERE m.id = json_extract(e.data,'$.info.id'))
  LIMIT 5000
);
SELECT changes();
COMMIT;
SQL
sqlite3 "$DB" "PRAGMA wal_checkpoint(PASSIVE);"
```

- **Batch** (2,000–5,000 rows) to bound WAL growth and rollback size.
- **`foreign_keys=ON`** turns silent corruption into a loud error. That is
  precisely what you want.
- **Know which side of the cascade you are on.** `event` is the *child* of
  `event_sequence`; deleting children is safe. Deleting the parent cascades
  its children away — that is how you destroy data you did not mean to touch.
- **Make it idempotent** so an interrupted run can simply be re-run.

### Phase 5 — Reclaim and swap

```bash
sqlite3 "file:$DB?mode=ro" "VACUUM INTO '/path/to/reclaimed.db';"

# verify the reclaimed file the same way you verified the backup
# then, with the application fully stopped:
fuser "$DB" 2>/dev/null && echo "STOP — still open" && exit 1
rm -f "$DB-wal" "$DB-shm"
mv reclaimed.db "$DB"
```

> **Never rename a database file under a live reader.**
> From [sqlite.org/howtocorrupt](https://sqlite.org/howtocorrupt.html):
> switching a database in and out of WAL mode around a `VACUUM` "can cause
> another process or thread that has the database file open to miss the fact
> that the database has changed." An atomic `mv` under a live reader is exactly
> that. The reader keeps writing to an unlinked inode and that data is silently
> gone.

---

## Safety gates must fail *closed*

The most dangerous bug we hit was not in SQLite — it was in our own script.

```bash
# WRONG
RESULT=$(timeout 300 sqlite3 "$DB" "PRAGMA quick_check;" | head -1)
[ -z "$RESULT" ] && ...        # timeout killed it → empty → indistinguishable from pass

# RIGHT
RESULT=$(timeout 300 sqlite3 "$DB" "PRAGMA quick_check;"); RC=$?
[ $RC -eq 124 ] && { echo "TIMED OUT — that is a FAIL"; exit 1; }
[ "$RESULT" = "ok" ] || { echo "FAILED: $RESULT"; exit 1; }
```

Similarly, a lock check that errors and passes is **worse than no check**, because
it manufactures confidence:

```bash
# WRONG — fuser exits non-zero when it finds nothing, i.e. in the normal case
HOLDERS=$(fuser "$DB" 2>/dev/null | sed 's/^ //')
[ -n "$HOLDERS" ] && die "locked"

# RIGHT — distinguish "no holders" from "the tool failed"
if OUT=$(fuser "$DB" 2>&1); then
  [ -n "$(echo "$OUT" | tr -s ' \n' ' ')" ] && die "locked"
else
  case "$OUT" in
    "") : ;;                                  # ran, found nothing → passes
    *)  die "fuser failed, cannot verify" ;;   # tool error → FAIL CLOSED
  esac
fi
```

Rules worth internalising:

1. **A gate that cannot determine the state must refuse.**
2. **`set -e` is not a safety mechanism** — subshells and `|| true` defeat it.
3. **Never `|| true` a safety check.** That is a check that always passes.
4. **Add `set -o pipefail`** where a pipeline is load-bearing.
5. **Assert on the success value, not the absence of output.**
6. **Never let a gate inspect the process performing the check.**

---

## Prove what you did *not* change

The highest-value assertion after any delete is the one about the tables you
were not targeting:

```bash
[ "$(count session)"       = "$PRE_SESSION" ] || die "session count changed"
[ "$(count message)"       = "$PRE_MESSAGE" ] || die "message count changed"
[ "$(count event_sequence)"= "$PRE_SEQ"     ] || die "event_sequence changed"
```

A reclaim that reports success while quietly dropping rows is the worst outcome
available — worse than failing, because it is believed.

In the verified run: 3,139 sessions, 168,280 messages, 702,396 parts, and 1,907
event sequences all unchanged; 1,033 orphan events correctly retained; 113,534
duplicates removed; 347,162 events remaining.

---

## Related tooling

| tool | use |
|---|---|
| `sqlite3 .backup` / Online Backup API | streaming backup; writes a byte-identical *uncompacted* copy (needs full source size at the destination) |
| `sqlite3_analyzer` | page-usage breakdown — run on a **copy**, never production |
| `sqldiff` | prove a reclaimed DB is a strict subset of a backup |
| `sqlite-utils` | safe transforms, good for inspecting schemas |
| `dbstat … WHERE aggregate=TRUE` | the only safe in-place byte attribution |
| litestream / litefs | continuous replication, *not* compaction |

---

## Primary sources

- [VACUUM](https://sqlite.org/lang_vacuum.html) — `VACUUM INTO` semantics; not a write on the source
- [Backup API](https://sqlite.org/backup.html) — and why file copies are unsafe
- [dbstat](https://sqlite.org/dbstat.html) — the `aggregate` virtual-table option
- [WAL](https://sqlite.org/wal.html) — snapshot isolation, BUSY conditions
- [How To Corrupt Your Database](https://sqlite.org/howtocorrupt.html) — the live-reader rename hazard
- [PRAGMA](https://sqlite.org/pragma.html) — what `quick_check` does and does not cover

---

*Recorded 2026-10-13. Reclaim verified end-to-end; research and runbooks in the
agent skill `opencode-db` and the general skill `sqlite-safe-ops`.*