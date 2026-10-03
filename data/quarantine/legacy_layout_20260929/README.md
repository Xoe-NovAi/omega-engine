# Quarantine — pre-migration handoff layout (2026-09-29)

**Not authoritative. Nothing reads this. `data/handoff/{hot,cold,envelopes,retired}` is the
single authoritative surface (SAHS Rule).**

## Why this exists

The 2026-09-29 live migration verified and copied 1479 packets into the four-directory
layout, then left the originals in place. It was a verified **copy**, not a move — which is
why nothing was ever at risk, and also why two trees existed side by side for a period.

Verification at quarantine time:
- 1479/1479 census ids present in the new layout, `pre == post` exact
- 723 ids were present in BOTH trees, **byte-identical** (sha256 compared on a 40-id sample,
  0 mismatches)
- 14 ids existed ONLY here and were never migrated — all 14 are `[M36 CROSS-VALIDATOR]`
  test packets (`/tmp/...`, `/nonexistent/...`), not real work orders

## Rollback

`~/omega-handoff-backup-20260929.tgz`
sha256 `97c6cbc674b8b6f22a2dd37b14006dd4d4c23eb55b666ab4c79693fdd4431a32`

Restore a single packet by copying it from here and verifying its sha256 against
`data/handoff/MIGRATION_CENSUS_20260929.json`.

## Why quarantined rather than deleted

M29 — Sovereign Artifact Preservation: no automated process may render a sovereign artifact
unrecoverable; destruction requires a deliberate human act. Two trees where one is
authoritative is the exact condition SAHS exists to prevent, and leaving it indefinitely
invites a future reader to trust the wrong one. Quarantine removes the ambiguity without
destroying anything.
