<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Disaster Recovery Architecture — Deep Research
**AP Token**: `AP-DISASTER-RECOVERY-20260726`
**Date**: 2026-07-26 | **Priority**: P0
**Researcher**: Sovereign Researcher

---

## Executive Summary

Restic backup scripts exist but are **not deployed**. `.env.backup` is missing, VaultCore (V-1) is required but not implemented, and 3 of 4 SQLite databases are excluded from backup. Qdrant snapshots rely solely on API (no offsite). Redis has no backup script.

## Current State

| Component | Status |
|-----------|--------|
| Restic backup script (v1, v2) | ✅ Scripts exist |
| Systemd timer | ✅ Defined (daily 3am ±15min) |
| `.env.backup` | ❌ MISSING — timer will fail |
| VaultCore (V-1) | ❌ Not implemented — scripts require `OMEGA_VAULT_PASSPHRASE` |
| SQLite backup (memory_store only) | ⚠️ Only 1 of 4 DBs backed up |
| Redis backup | ❌ No `redis-cli BGSAVE` script |
| Qdrant snapshots in restic | ❌ Excluded from restic, API-only |
| Monthly restore test | ⚠️ Script exists, no timer |
| Healthchecks.io | ⚠️ Not configured |

## Data at Risk

| Data | Tier | Current Protection |
|------|------|-------------------|
| soul.yaml (96 entities) | CRITICAL | SoulStore .bak + restic (if deployed) |
| proposed_lessons.yaml | SEVERE | SoulStore .bak + restic |
| memory_store.sqlite | SEVERE | SQLite .backup in restic (if deployed) |
| workbench.db | HIGH | NOT backed up |
| search_history.db | MEDIUM | NOT backed up |
| research.db | MEDIUM | NOT backed up |
| Qdrant collections | HIGH | API snapshots only |
| Redis session data | MEDIUM | AOF + RDB (no offsite) |

## Recommended Architecture

1. **Litestream** for continuous WAL replication (30s RPO) on all SQLite DBs
2. **Restic + B2** for daily offsite (3-2-1 rule)
3. **Redis BGSAVE** before restic run
4. **Qdrant snapshots** included in restic staging
5. **Healthchecks.io** dead-man's switch
6. **Monthly restore test** automated via systemd timer

## Implementation Plan

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Fix .env.backup + enable systemd timer | 30min |
| 2 | Add all SQLite DBs to restic staging | 1h |
| 3 | Add Redis BGSAVE to restic pre-backup | 1h |
| 4 | Include Qdrant snapshots in restic | 2h |
| 5 | Deploy V-1 VaultCore for credential retrieval | 8h |
| 6 | Install Litestream + configure for 3 DBs | 4h |
| 7 | Add monthly restore test timer | 1h |
| 8 | Configure Healthchecks.io | 30min |
| 9 | Write full DR runbook | 2h |
| **Total** | | **~20h** |

## Key Finding

C-3 ticket status "DONE" is **premature** — scripts exist but deployment prerequisites (VaultCore, .env.backup, B2 bucket, timer enablement) are unresolved.
