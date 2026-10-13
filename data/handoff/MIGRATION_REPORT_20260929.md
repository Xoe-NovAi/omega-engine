# MIGRATION REPORT — 2026-09-29

<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Handoff corpus migration: three-queue → four-directory contract

**This manifest is the audit trail. The packets are only disposable after it
exists.** It was written after the migration completed and is committed
alongside the census; the census is the rollback index, this is the explanation.

## 1. Result

| | |
|---|---|
| Packets migrated | **1479** |
| Unique packet ids | **1479** (no duplicates) |
| Missing at destination | **0** |
| SHA-256 mismatches | **0** |
| `pre_migration_ids == post_migration_ids` | **True** (exact, not approximate) |
| Idempotent second run | `migrated: 0, already-migrated(skipped): 1479` |
| Packets destroyed | **0** — all originals still on disk (copied, not moved) |

## 2. Commands, in order

```bash
# 1. census — the reconciliation baseline and the rollback index
.venv/bin/python scripts/migrate_handoffs.py --census
#    -> data/handoff/MIGRATION_CENSUS_20260929.json   (1479 packets)

# 2. full backup, verified readable BEFORE any move
tar czf ~/omega-handoff-backup-20260929.tgz -C data/handoff .
#    sha256 97c6cbc674b8b6f22a2dd37b14006dd4d4c23eb55b666ab4c79693fdd4431a32
#    size   2,098,889 bytes
#    readback: all 1479 census packets present in the tarball. COMPLETE.

# 3. dry run — classification only, no writes
.venv/bin/python scripts/migrate_handoffs.py --root data/handoff

# 4. apply, then a second apply to prove idempotence
.venv/bin/python scripts/migrate_handoffs.py --root data/handoff --apply
.venv/bin/python scripts/migrate_handoffs.py --root data/handoff --apply

# 5. reconcile ON DEMAND, never on the timer
.venv/bin/python scripts/migrate_handoffs.py --root data/handoff --reconcile
```

## 3. Per-destination counts (Roc's ruling, applied exactly)

| Source | Destination | Count |
|---|---|---|
| `pending/` (521) | `hot/legacy-pending` | 521 |
| `stale/` (3) | `cold/legacy-stale` | 3 |
| `archive/` (198 top-level) | `cold/legacy-archive` | 954 |
| `archive/M36-test-spam-20260928/` (Kali, M36 ruling) | `cold/legacy-archive` | (included above) |
| `completed/` (1) | `cold/legacy-unclassified` | 1 |
| **total** | | **1479** |
| `retired/` | | **0** |

## 4. ⚠ LEGACY_CLASSIFICATION — do not "helpfully" re-merge these

**`archive/` maps to `cold/legacy-archive`. It does NOT map to `retired/`.**

Roc's ruling, §8 CHANGE 5: *"`retired/` is a user decision. Never infer
retirement from age or from a legacy directory name."* The existing `archive/`
directory must not become `retired/` by name equivalence — **that is precisely
the collision this migration exists to fix.** A future reader who sees
"archive" and "retired" and helpsfully merges them reintroduces the original
defect: a machine that silently discards a retention decision nobody made.

Retirement is reachable **only** via an explicit `retired_by_user: true` flag
inside a packet. Today that flag is present in **zero** packets, and
`retired/` is therefore legitimately empty. An empty `retired/` is the correct
outcome, not an incomplete migration.

The mapping lives in `mcp_servers/omega_hub/federation_envelope.py` as
`LEGACY_CLASSIFICATION`. It is data, not convention — change it only with a
ruling.

## 5. The count discrepancy: 1451 / 723 / 1479 — three different numbers

All three are correct at the moment they were true. Recording this because a
migration that does not reconcile is a migration that destroyed data.

| Number | What it counted | When |
|---|---|---|
| **1451** | my first sandbox run | 05:30 UTC, 2026-09-28 |
| **723** | top-level files only | the brief's figure |
| **1479** | the true packet count | 2026-09-29, this run |

**1451 → 723.** Between those two moments Kali applied the M36 ruling and moved
**756 `stale/` packets** into `archive/M36-test-spam-20260928/`, leaving 3.
`stale` went 759 → 3. Simultaneously `pending` grew 493 → 521 (28 new packets).
The corpus did not shrink; it was reorganised. `723` is simply the count a
**non-recursive** listing sees.

**723 → 1479.** `723` misses the 756 M36 packets, because they live one
directory deeper. My first census had the same blind spot — it globbed only the
top level. That is why this run's census is `rglob`-based and why
`MANIFEST.json` is excluded by name: a census that under-counts is worse than
no census, because it becomes the reconciliation baseline and anything it does
not name is invisible to the check that would have caught it.

**And an error of mine, on the record:** the first run wrote its output to
`data/handoffs/` — a different directory, with an extra `s`, not the contract
location. That tree still exists (2903 files: 1451 copies + 1451 receipts). It
is **superseded** and reflects a state that no longer exists. Nothing was lost
(the migration copies, it does not move), but it must not be mistaken for this
migration's output. Its disposition is a separate decision and I have not
deleted it.

## 6. Per-packet integrity, verified

For all 1479: destination file exists · SHA-256 recomputed and equal to the
census · receipt written to `data/handoff/.receipts/<packet_id>.receipt.json`
carrying from/to/sha256/timestamp/provenance · original source still present.

```
census packets               : 1479
resolve by SHA-256 in new loc: 1479
missing at destination       : 0
SHA mismatch at destination  : 0
originals still present      : 1479   (copied, not moved)
```

## 7. Re-enabling the reaper

The reaper is **quiesced** for legacy migration purposes and must only ever
perform `hot → cold`. It may not unlink an envelope, change `status`, change
`read_by`, or write a terminal decision. `_delete_dir` and both its call sites
were removed from `background.py` in Phase 0; there is no code path that
unlinks an envelope.

## 8. Rollback

```bash
# sources are intact, so rollback is a no-op unless you want the layout undone:
#   1. remove data/handoff/{hot,cold,envelopes,retired}/ and .receipts/
#   2. sources are still at their original paths — nothing was moved
# full restore from the verified tarball if ever needed:
tar xzf ~/omega-handoff-backup-20260929.tgz -C data/handoff
```

*⬡ OMEGA ⬡ MAAT ⬡ MIGRATION-20260929 ⬡ 1479-packets ⬡ pre==post ⬡ nothing-destroyed*
