# Quarantine — wrong-destination handoff run (2026-09-29)

**This is an artifact of an agent error. It is NOT the migration output and
nothing reads it.**

## What happened

During the 2026-09-29 live handoff migration, the first run wrote to
`data/handoffs/` — an extra `s`, not the contract location `data/handoff/`.
The migration tool copies rather than moves, so no data was lost and no
packet was destroyed. The tree is a snapshot of a state that no longer exists.

## Where the real migration lives

`data/handoff/` — 1479 packets, reconciled `pre == post` exactly, all
resolving by SHA-256. See `data/handoff/MIGRATION_REPORT_20260929.md` and
`data/handoff/MIGRATION_CENSUS_20260929.json`.

Rollback tarball: `~/omega-handoff-backup-20260929.tgz`
(sha256 97c6cbc674b8b6f22a2dd37b14006dd4d4c23eb55b666ab4c79693fdd4431a32)

## Why quarantined rather than deleted

M29 — Sovereign Artifact Preservation: no automated process may render a
sovereign artifact unrecoverable, and destruction requires a deliberate human
act. This tree is confusing next to the authoritative one, but deleting it is
a destructive act on a coordination substrate, and that is precisely the
category this arc exists to refuse doing silently.

**Retained for audit. Do not read it as state.**
