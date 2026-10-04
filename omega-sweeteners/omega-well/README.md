# The Well — Portable Package

**Source:** Node 1 live corpus at `gnosis/well/` — **71 records** (65 active, 6 superseded)
**Snapshot date:** 2026-10-03 (refreshed from vendor commit `c079475a`, 2026-10-03)
**Status:** 🟢 Live corpus + hardened tooling, verified green (7/7 package tests)

## Contents

| Path | What it is |
|---|---|
| `scripts/well_storage.py` | Reader/writer/verify/rank — hardened (per-record isolation, `scanned/skipped/errors` result, dedup + permanence floor) |
| `gnosis/well/well.jsonl` | **71 records** — live N1 corpus, byte-identical to `gnosis/well/` |
| `gnosis/well/WISDOM.md` | Human-readable render of the active records |
| `tests/test_well.py` | 7 regression tests (all passing) |
| `Makefile.well` | Self-contained Make fragment — `well-add/list/stats/verify/supersede/export/search` |
| `install.sh` | Installs corpus, script, tests, and Make fragment into a target project |
| `WELL_INTEGRATION.md` | Integration guide |

**Self-contained:** you do not need a host Makefile. `make -f Makefile.well well-verify`
works immediately after `install.sh`.

## The N0 rule — read this before you install

**Bring up The Well with a FRESH `well.jsonl`.** The 71 records shipped here are
**reference, not transplant.** They encode incidents that happened on Node 1 —
silently-dead injection paths, CPU-pin convoys, stale-WAL reads. Their weights
and their triggers are calibrated to N1 silicon and N1 history. Reading them is
how you learn what class of failure to watch for. Copying them into your corpus
means asserting they happened to you, which they did not.

Read ours, then earn yours.

## What the hardening bought (2026-10-01/02)

These were real defects on N1, not theoretical:

- **Per-record isolation** — one malformed record can no longer empty the batch.
  This is what silently killed injection on N1 while 114 tests stayed green.
- **`scanned/skipped/errors` result object** — "no data" is now distinguishable
  from "nothing indexed". A green gate can no longer certify a corpse.
- **`normalizeTags()`** — records with `tags` as a JSON *array* are handled; the
  earlier reader threw on them and the outer catch returned `[]`.
- **Injection dedup + permanence floor** — two slots reserved for
  `correction`/`anti_pattern` so pure-recency ranking cannot crowd them out.
- **`make well-verify`** — audits the real corpus, exits 1 on unreadable records,
  and emits the *decision* behind each finding, not just the finding.
- **1024-native embedding dimension** — corrected from the old 768 claim.

## Install

```bash
./install.sh /path/to/your/project
cd /path/to/your/project

# Verify the corpus you just installed
make -f Makefile.well well-verify
make -f Makefile.well well-stats

# Run the tests
python3 -m unittest discover -s tests -p 'test_well*.py' -v

# Earn your first record
make -f Makefile.well well-add \
  KIND=correction DOMAIN=harness \
  TRIGGER="the thing that surprised you" \
  RULE="what to do instead" \
  RATIONALE="why"
```

Full guide: `WELL_INTEGRATION.md`.