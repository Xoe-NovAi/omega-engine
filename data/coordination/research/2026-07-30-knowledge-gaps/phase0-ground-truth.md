<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Phase 0 — Ground Truth Snapshot

**Timestamp**: 2026-07-30T05:50Z  
**Source**: live probes + repo scan

## Tests
- Focused suite: **27 passed, 1 skipped, 8 warnings** in 14.73s
- Command: `source .venv/bin/activate && python -m pytest tests/test_vault_integrity.py tests/property/ tests/test_hivemind.py -q --tb=line`
- Full suite count unknown from `make test` timeout; prior claim **1706 collected** needs rerun with longer timeout

## Listening ports
- `8015` Firecrawl UP (pid 2751)
- `8016` Omega Hub UP (pid 2752)
- `8083` WARP SOCKS UP
- `8081`/`8082` not listening

## Restic
- timer: `active`
- service: `failed` (since 01:34Z) — vault passphrase/env not set; `.env.backup` missing
- override PATH present: `/etc/systemd/system/omega-restic-backup.service.d/override.conf`

## MCP
- venv: **1.28.1**
- pyproject pin: see board; schedule says `>=1.28.1,<2`

## Phase D gate script
- `python scripts/verify_phase_d_gate.py` not runnable as `python`; needs `python3` or venv python
- Need to re-run under `.venv/bin/python` to validate mechanical PASS claim and V-1 pipe masking risk

## Code patterns scan
- `anyio.to_thread.run_sync(...)` present in many files
- `yaml.safe_load` present in: `soul_utils.py`, `entity_registry.py`, `config/loader.py`, `cli/bundle.py`, `agents/scribe/...`, `eval/runner.py`
- `fcntl.flock` present in: `oracle/entity_registry.py`
- `threading.Lock` scan not hits in shown output
- `class.*Breaker` hits not counted here; prior count 17

## Next
- Run phase_d_gate under `.venv/bin/python`
- Web research P0 gaps: G-1 paths, W-1 warp state, MCP v2 migration delta, C3-6 backup verification