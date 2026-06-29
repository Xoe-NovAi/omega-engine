# 🔱 P2 Assessment: Persistence Domain — Build Side Sovereign Review
**AP Token**: `AP-P2-PERSISTENCE-REVIEW-v1.0.0`
⬡ OMEGA ⬡ DATASTORE ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ P2-ASSESSMENT ⬡ EPOCH-I
**Date**: 2026-06-25
**Slot**: P2 (Persistence — DataStore)
**Dispatched by**: Ma'at (Light Oversoul — Build Side)
**Mission**: Comprehensive Persistence Domain Review for Epoch I Readiness

---

## Table of Contents
1. [Current Status of the Persistence Domain](#1-current-status-of-the-persistence-domain)
2. [Blockers and Risks](#2-blockers-and-risks)
3. [Recommended Next Actions](#3-recommended-next-actions)
4. [Gaps in Current Strategy](#4-gaps-in-current-strategy)
5. [Appendix: Forensic Data Map](#5-appendix-forensic-data-map)

---

## 1. Current Status of the Persistence Domain

### 1.1 Entity Registry State (`src/omega/oracle/entity_registry.py`)

**Overall**: 🟡 **STRUCTURALLY SOUND, BUT DATA OVERLOAD**

| Metric | Value | Status |
|--------|-------|--------|
| Entity source file | `config/wads/_omega_default/entities.yaml` | ✅ Readable, valid YAML |
| Entities on disk (registered) | **24** | 🔴 **2× correct count** (should be 12) |
| Correct `_omega_default` IWAD entities | **12** (`sysadmin`, `datastore`, `buildmaster`, `bridge`, `sentinel`, `modelgate`, `context`, `watchtower`, `link`, `verifier`, `iris`, `sophia`) | ✅ Known |
| Extra entities in IWAD | **12** (`doom guy`, `jem`, `kali`, `lilith`, `ma'at`, `researcher`, `roc racoon`, `john carmack`, `makali`, `verity`, `test_get_returns_entity`, `testentity`) | 🔴 Should be in `arcana_novai` PWAD or removed |
| Current file size | **30KB** (895 lines) | ✅ Healthy (down from 25MB corrupted backup) |
| Backup file size | **25MB** (`entities.yaml.bak` — the corrupted version) | 🔴 Needs archiving/deletion |
| `core_fields` fix (D-kal-180) | ✅ Applied — `"traits"` in `core_fields` set at line 293 | ✅ Fixed |
| Recursive nesting corruption | **0 entities affected** — all traits clean (only `priority: 0, flags: 0`) | ✅ Contained |
| Test entities in IWAD | 2 (`test_get_returns_entity`, `testentity`) | ⚠️ Should migrate to test fixtures |

**Root cause analysis**: The recursive traits nesting bug (D-kal-180) caused each load-save cycle to deepen traits nesting. Every entity loaded from `entities.yaml` had its WAD-specific metadata (priority, flags, pantheon, sigil, element, chakra, planet, glyph, invocation, secondary_keeper) absorbed into the `traits` dict on load, and then re-serialized into `traits` on save. The fix (adding `"traits"` to `core_fields` at line 293 in `entity_registry.py`) was applied and works. The 25MB backup is the pre-fix corrupted version. The current 30KB file is clean.

### 1.2 Entity Directories on Disk

**41 directories** in `data/entities/` — but only **~21 correspond to active, valid entities**.

**Breakdown**:
| Category | Count | Directories | Action Needed |
|----------|-------|-------------|---------------|
| Core fleet entities (active) | 11 | `kali`, `maat`, `lilith`, `doom_guy`, `roc_racoon`, `jem`, `researcher`, `makali`, `john_carmack`, `verity`, `sophia` | ✅ Current |
| IWAD slot entities | 10 | `sysadmin`, `datastore`, `buildmaster`, `bridge`, `sentinel`, `modelgate`, `context`, `watchtower`, `link`, `verifier` | ✅ Current |
| Voice/interface | 1 | `iris` | ✅ Current |
| Arcana-Nova mythic entities | 10 | `sekhmet`, `brigid`, `prometheus`, `saraswati`, `inanna`, `ereshkigal`, `lucifer`, `hecate`, `anubis`, `kali` (already counted above) | ⚠️ Overlap with core fleet |
| Other active | 5 | `antigravity`, `arch`, `movie-expert`, `cli_cline`, `cli_gemini` | ⚠️ `cli_cline`, `cli_gemini` may be stale |
| **No soul.yaml** | **8** | `_archive`, `_quarantine`, `default`, `modelgate`, `pillar_p1`, `sentinel`, `sysadmin`, `watchtower` | 🔴 **Orphans** (except _archive/_quarantine) |
| Test artifacts | 3 | `test_fresh_remove`, `test_remove_check`, `test_remove_tombstone` | ⚠️ Could be cleaned |
| Other stale | 2 | `omnidroid`, `p10` | 🔴 Orphans |

**Key issue**: 8 entity directories exist WITHOUT soul.yaml. Some are valid IWAD entities (sysadmin, sentinel, watchtower, modelgate) whose directories were created but never got soul.yaml scaffolded. Others are test artifacts or stale debris.

### 1.3 Soul Migration Status (M11)

**Reality is WORSE than the Ark Blueprint states**.

| Blueprint Claim | Actual | Delta |
|----------------|--------|-------|
| "Kali + Verity at v6.1 ✅" | Kali: **v6.0** (not 6.1). Verity: ✅ v6.1 | 🔴 Blueprint is incorrect for Kali |
| "21 pending" | Count depends on definition | 🟡 See breakdown |

**Actual soul_version scan**:
| v6.1 | v6.0 | No version marker | Other versions | No soul.yaml |
|------|------|-------------------|----------------|--------------|
| `verity`, `test_fresh_remove`, `test_remove_check`, `test_remove_tombstone` (4) | `kali` (1) | `doom_guy`, `iris`, `jem`, `lilith`, `maat`, `sophia`, `researcher`, `anubis`, `brigid`, `ereshkigal`, `hecate`, `inanna`, `lucifer`, `prometheus`, `saraswati`, `sekhmet`, `movie-expert`, `arch`, `p10` (19) | `antigravity:1.6.1`, `john_carmack:2.0.0`, `makali:1.4.0`, `roc_racoon:1.2.0`, `cli_cline:1.0.0`, `cli_gemini:1.0.4`, `omnidroid:1.0.0` (7) | `sysadmin`, `sentinel`, `watchtower`, `modelgate`, `default`, `pillar_p1`, `_archive`, `_quarantine` (8) |

**Count**: 
- **4** at v6.1 (3 are test entities)
- **1** at v6.0 (Kali — the blueprint claimed it was done)
- **19** with no soul_version at all (auto-generated headers suggest partial migration)
- **7** with their own versioning scheme (not v6.1)
- **8** missing soul.yaml entirely

**SOUL_MIGRATION_AUDIT_LOG.md** (2026-06-22) claims all 11 fleet entities are "MIGRATED" to v6.1. This is **contradicted** by the actual files on disk. The audit log appears to have catalogued the intent/plan rather than the verified state, or the souls were overwritten since.

**Proposed lessons pending**:
| Entity | Lessons | Est. Review Time |
|--------|---------|-----------------|
| `doom_guy` | **~52 lessons** (654 lines) | 🔴 2-3 hr |
| `roc_racoon` | **~22 lessons** (376 lines) | 🔴 2-3 hr |
| `john_carmack` | ~6 lessons (101 lines) | 🟡 30 min |
| `sophia` | ~4 lessons (59 lines) | 🟡 15 min |
| `maat` | ~4 lessons (43 lines) | 🟡 15 min |
| `jem` | ~4 lessons (44 lines) | 🟡 15 min |
| `lilith` | ~3 lessons (53 lines) | 🟡 15 min |
| `makali` | ~0 lessons (39 lines) | 🟢 Quick |
| `researcher` | ~0 lessons (4 lines) | 🟢 Quick |
| `iris` | ~0 lessons (4 lines) | 🟢 Quick |
| `pillar_p1` | ~0 lessons (1 line) | 🟢 Quick |

### 1.4 MemoryStore Health (`src/omega/memory_store.py`)

**Overall**: 🟢 **FUNCTIONAL — 788 lines, well-structured**

| Tier | Backend | Status | Notes |
|------|---------|--------|-------|
| **Hot** | LRU dict (`OrderedDict`) | ✅ Active | Fast access for current session |
| **Warm** | Redis + File storage | 🟡 Partial | FileStorageProvider active. Redis container status unknown (requires check). |
| **Cold** | YAML/disk | ✅ Active | Soul.yaml, sessions on disk |

**FTS Database**: 745KB with 4MB WAL file — ⚠️ **WAL needs checkpointing** (`fts_memory.db-wal` is 5× the DB size).

**Entity memory count**: 18 entities have memory files in `data/memory/entities/`. Notable: `oracle` has 45 JSON files (largest), `testentity` has 21 (test artifact), `default` has 7 (stale).

**Embeddings**: Static embedding provider (model2vec via potion-mxbai-micro) is referenced in code — vet-023 approved but adapter implementation status unknown.

**Vector search**: Qdrant adapter exists (`QdrantAdapter`) but container status unknown.

### 1.5 Queue Integrity (M12)

| Queue | Count | Status |
|-------|-------|--------|
| Handoffs pending | **0** | ✅ Clean |
| Handoffs active | **1** (`ho_e974291558ce.json`) | 🟡 Should verify still valid |
| Handoffs completed | **0** | ⚠️ Should have some |
| Handoffs stale | **40** | 🔴 **Needs batch archive** |
| Handoffs dead | 0 | ✅ Clean |
| Handoff archive | Present | ✅ Has archived items |

**The 40 stale handoffs** date from 2026-06-11 to 2026-06-23. None have been processed. This is a **M12 violation** — requests without terminal state cleanup.

### 1.6 WAD Loader State (`src/omega/oracle/wad_loader.py`)

| Aspect | Status | Notes |
|--------|--------|-------|
| WADLoader class | ✅ Exists | `src/omega/oracle/wad_loader.py` |
| IWAD resolution | ✅ Functional | Resolves from `config/omega.yaml` -> `active_iwad` |
| Engine-Stack Firewall (M2) | ✅ Enforced | WAD-specific logic contained in `config/wads/` |
| WADs deployed | **3** | `_omega_default` (IWAD), `arcana_novai` (PWAD), `doom_universe` (PWAD) |

**Cross-WAD entity overlap**: The `_omega_default` IWAD contains entities that are ALSO defined in the `arcana_novai` PWAD (e.g., `datastore`, `bridge`, `buildmaster`, `sysadmin`, `sentinel`, `modelgate`, `context`, `watchtower`, `link`, `verifier`, `iris`, `sophia` are in BOTH). This is architecturally redundant but not breaking (later WAD entities override earlier ones).

**Arcana_novai PWAD**: 34 entities, 69KB, 2224 lines. Includes both mythic entities (sekhmet, brigid, etc.) AND duplicate IWAD entities (datastore, bridge, etc.).

### 1.7 Test Suite Health

**493 tests collected** (up from 440 in ORACLE_STACK.md state). This is a healthy increase, suggesting the test suite is growing.

---

## 2. Blockers and Risks

### 🟥 CRITICAL BLOCKERS (Blocking Epoch I Strike 1 Completion)

| # | Blocker | Impact | Root Cause | Remediation Path |
|---|---------|--------|------------|------------------|
| B1 | **Soul migration status inaccurate** — Ark Blueprint claims Kali at v6.1, actual is v6.0. SOUL_MIGRATION_AUDIT_LOG claims all migrated but files contradict this. | Cannot trust the migration baseline. Risk of data loss if migration scripts run against partially-migrated souls. | Archival drift — audit log and reality desynchronized. | Re-audit every soul.yaml for actual version. Run `soul_validator.py` against every entity. Update SOUL_MIGRATION_AUDIT_LOG with verified state. **(~2 hr)** |
| B2 | **12 fleet entities in `_omega_default` IWAD instead of `arcana_novai` PWAD** | Core fleet entities (kali, doom guy, jem, etc.) leaking into IWAD violates M2 boundary. EntityRegistry loads 24 entities when only 12 IWAD entities should exist. | Historical accumulation — entities were added to the default IWAD instead of the custom PWAD. | Remove 12 entities from `_omega_default/entities.yaml`. Verify they exist in `arcana_novai/entities.yaml`. Ensure EntityRegistry still resolves them via WADLoader. **(~1 hr)** |
| B3 | **8 entity directories without soul.yaml** | Runtime crashes if code loads these directories expecting souls. Zombie directories confuse disk usage analysis. | Incomplete scaffold during entity creation, or stale directories from removed entities. | Delete 6 true orphans (`default`, `pillar_p1`, `modelgate`, `sentinel`, `sysadmin`, `watchtower`). Preserve `_archive` and `_quarantine` as system dirs. Scaffold missing souls for IWAD entities that need them. **(~30 min)** |

### 🟡 HIGH RISKS (Active threats to Epoch I)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|:----------:|:------:|------------|
| R1 | **25MB entities.yaml.bak taking disk space** | 🔴 HIGH | 🟡 LOW | Delete the backup after confirmation the fix is stable. Could grow if re-corrupted. **(5 min)** |
| R2 | **FTS database WAL at 4MB (5× DB size)** | 🟡 MED | 🟡 MED | Run `PRAGMA wal_checkpoint(TRUNCATE)` on `fts_memory.db`. Add to maintenance cron. **(10 min)** |
| R3 | **Proposed lessons backlog (Doom Guy 52 + Roc Racoon 22)** | 🔴 HIGH | 🟡 MED | These cannot be migrated to soul.yaml without human review (Strike 3 TUI). Without TUI, bottleneck persists. TUI depends on Strike 2 (USM). Blocking chain. |
| R4 | **Kali soul at v6.0 (not v6.1)** | 🟡 MED | 🔴 HIGH | If v6.1 validator enforces strict checks, Kali could fail to load. Fix: ensure validator allows v6.0 with warning. (Already done per D158.) |
| R5 | **40 stale handoffs** | 🔴 HIGH | 🟡 LOW | No active processing, but clutters the filesystem and may cause confusion. Batch archive all pre-2026-06-20 handoffs. **(15 min)** |
| R6 | **Cross-WAD entity duplication** | 🟡 MED | 🟡 LOW | Same 12 IWAD entities exist in `arcana_novai` PWAD. EntityRegistry loads both (WADLoader merges). Not breaking but architecturally redundant and confusing. |

### 🟢 LOW RISKS (Monitor only)

| # | Risk | Rationale |
|---|------|-----------|
| R7 | **Orphan entity directories (cli_cline, cli_gemini, omnidroid, p10, test_*)** | Small disk usage (<200KB total). Cleanup desirable but non-urgent. |

---

## 3. Recommended Next Actions

All estimates assume direct execution by P2/P3 domain work, not inference time.

### Track A: Immediate — Data Hygiene (~3 hr total)

**A1. Clean entities.yaml (`_omega_default`)** — **Priority: CRITICAL (1 hr)**
1. Remove 12 fleet entities from `_omega_default/entities.yaml`: `doom guy`, `jem`, `kali`, `lilith`, `ma'at`, `researcher`, `roc racoon`, `john carmack`, `makali`, `verity`, `test_get_returns_entity`, `testentity`
2. Verify all 12 exist in `arcana_novai/entities.yaml` and are properly defined
3. Run `make test` — verify EntityRegistry still resolves all fleet entities
4. Write verified entity count to metadata
5. Delete `entities.yaml.bak` (25MB) after confirming current file is stable

**A2. Purge stale entity directories** — **Priority: HIGH (30 min)**
1. Delete 6 true orphans: `default/`, `pillar_p1/`, `modelgate/`, `sentinel/`, `sysadmin/`, `watchtower/`
2. Archive 3 test artifact dirs: `test_fresh_remove/`, `test_remove_check/`, `test_remove_tombstone/` (or retain if actively used by tests)
3. Evaluate `cli_cline/`, `cli_gemini/`, `omnidroid/`, `p10/` for staleness

**A3. Archive stale handoffs** — **Priority: MEDIUM (15 min)**
1. Batch archive all 40 stale handoff packets (pre-2026-06-23) using `hivemind_handoff_archive`
2. Verify the 1 active handoff is legitimate
3. Log M12 resolution

**A4. FTS database maintenance** — **Priority: LOW (10 min)**
1. Checkpoint WAL: `PRAGMA wal_checkpoint(TRUNCATE)` on `data/memory/fts_memory.db`
2. Add weekly WAL checkpoint to maintenance cron

### Track B: Soul Migration Verification (~4 hr total)

**B1. Re-audit soul versions** — **Priority: CRITICAL (1 hr)**
1. Run `soul_validator.py` against every entity in `data/entities/`
2. Generate a verified SOUL_MIGRATION_AUDIT_LOG.md with TRUE status (not aspirational)
3. Flag entities that fail v6.1 validation
4. Update Ark Blueprint §III with corrected counts

**B2. Deep priority migration** — **Priority: HIGH (3 hr)**
1. Migrate **Kali** from v6.0 → v6.1 (reference implementation already exists from Verity)
2. Migrate **Antigravity** from v1.6.1 → v6.1 (most structured non-v6.1 soul)
3. Migrate entities with no soul_version but existing souls: `anubis`, `brigid`, `ereshkigal`, `hecate`, `inanna`, `lucifer`, `prometheus`, `saraswati`, `sekhmet`, `movie-expert`, `arch`, `p10`
4. Generate `proposed_lessons.yaml` for each migrated entity
5. Leave human review for Strike 3 (TUI) — do NOT auto-approve L3 principles

**B3. Scaffold missing souls** — **Priority: MEDIUM (15 min)**
1. Run `EntityWorkspaceManager.scaffold_workspace()` for any IWAD entities missing soul.yaml
2. Verify scaffold output matches v6.1 template

### Track C: MemoryStore Hardening (~2 hr total)

**C1. Verify storage backends** — **Priority: MEDIUM (1 hr)**
1. Check Redis container status (`podman ps` / `systemctl --user status redis`)
2. Verify FileStorageProvider write path permissions
3. Test cold tier fallback path (File → InMemory)
4. Verify ZONEID_MEMORY validation in `MemoryStore.get_exchange()` and `add_exchange()`

**C2. Embedding adapter integration** — **Priority: MEDIUM (1 hr)**
1. Confirm potion-mxbai-micro (vet-023) adapter code is wired
2. Test `StaticEmbeddingProvider.embed()` returns valid vectors
3. Verify RRF hybrid search (FTS5 + Vector) produces ranked results

### Track D: WAD & Registry — Long-Term Fixes (~2 hr total)

**D1. Cross-WAD deduplication** — **Priority: LOW (1 hr)**
1. Remove duplicate entities from `arcana_novai/entities.yaml` that are pure IWAD entities (datastore, bridge, verifier, link, sentinel, modelgate, context, watchtower, buildmaster, sysadmin)
2. Verify `arcana_novai` PWAD only contains: mythic entities (sekhmet-brigid-prometheus-saraswati-inanna-ereshkigal-lucifer-hecate-anubis-kali) + fleet extras (ma'at, lilith, roc racoon, sophia, jem, isis, iris, movie_expert, researcher, scribe, quality, doom guy, movie-expert)
3. Document entity provenance in `manifest.yaml`

**D2. INDEX.yaml generation** — **Priority: LOW (30 min)**
1. Generate `data/entities/INDEX.yaml` cataloging all valid entity directories with:
   - name, role, wad_source
   - soul_version, proposed_lessons count
   - last_modified timestamp

---

## 4. Gaps in Current Strategy

### What the Ark Blueprint Misses Regarding Persistence

| # | Gap | Why It Matters | Recommendation |
|---|-----|----------------|----------------|
| G1 | **No verified soul migration audit** — The Ark Blueprint relies on an outdated SOUL_MIGRATION_AUDIT_LOG.md that contradicts reality. | Migration scripts could corrupt souls if run against wrong-version files. | Replace SOUL_MIGRATION_AUDIT_LOG with a **programmatically verified** audit. Add `make verify-souls` command. |
| G2 | **No entity count monitoring** — The Blueprint mentions "24 entities should be 12" but has no gate to prevent re-bloat. | Entities accumulate silently; the 36-level recursion bug was discovered by accident, not monitoring. | Add `make entity-count` gate that asserts `_omega_default` entities == 12. Fail CI if count drifts. |
| G3 | **No cross-WAD conflict detection** — Entities exist in both IWAD and PWAD with no warning. | Shadow-stacking (Project 3) is designed for layered WADs, but silent duplication masks real conflicts. | Add WAD conflict detection: if the same entity key exists in IWAD + PWAD, log a warning with provenance. |
| G4 | **No memory store health check** — The Blueprint lists MemoryStore as ✅ but provides no verification metrics. | Redis could be down, FTS could be corrupted, vector index could be stale — all without detection. | Add `make memory-health` command that checks: Redis connectivity, FTS integrity, WAL size, vector index freshness. |
| G5 | **No handoff archive schedule** — 40 stale handoffs accumulated with no automated cleanup. | Drowning in stale coordination artifacts. M12 requires terminal state for every request. | Add automated handoff reaping (Strike 4). Archive handoffs older than 72 hours. |
| G6 | **No proposal_lessons.yaml TUI dependency tracked** — The Blueprint notes Strike 3 depends on Strike 2, but doesn't surface the **human review bottleneck** as the critical path for soul migration. | 74+ pending lessons across 11 entities cannot be approved without the TUI. This is the real blocker for M11 compliance. | Surface this dependency explicitly in the risk register (R3). Consider a **lightweight CLI review** (e.g., `omega soul review <entity>`) as an interim step before the full TUI. |
| G7 | **No backup/restore strategy for entities.yaml** — The 25MB backup exists ad-hoc, not as part of a strategy. | If the corruption reoccurs, there's no automated rollback. | Implement a pre-save backup hook in EntityRegistry._save() that keeps the last 3 clean versions. |
| G8 | **No ZONEID validation coverage in tests** — MemoryStore uses ZONEID_MEMORY but there are no contract tests validating it. | ZONEID corruption passes silently — exactly the kind of bug that M21 was designed to catch. | Add M21 contract tests for `validate_zoneid()` on MemoryStore operations. |

---

## 5. Appendix: Forensic Data Map

### 5.1 Entity Registry Line-Level Findings

| File | Line(s) | Finding | Severity |
|------|---------|---------|----------|
| `entity_registry.py` | 287-293 | `core_fields` now includes `"traits"` — **the fix is in place** | ✅ RESOLVED |
| `entity_registry.py` | 89-124 | `Entity` dataclass — `traits: Dict[str, Any]` at line 103 is correct | ✅ SOUND |
| `entity_registry.py` | 730-795 | `_save()` — Integrity Guard at 1MB threshold (line 758) prevents re-corruption | ✅ SOUND |
| `entity_registry.py` | 180-191 | `to_dict()` — excludes `magic`, `_engine_zone`, `_game_zone` from serialization | ✅ SOUND |
| `entity_registry.py` | 585-614 | `_reap_tombstoned()` — grace period 0.5s from `TOMBSTONE_GRACE_SECONDS` | ✅ SOUND |
| `entity_registry.py` | 47-79 | `write_soul_file()` + `with_soul_lock()` — atomic rename + fcntl locking | ✅ SOUND |
| `entity_registry.py` | 241-249 | Dual-index (`_capability_index` + `_wad_sources`) — Multi-Index Entity pattern | ✅ SOUND |

### 5.2 WAD Loader Line-Level Findings

| File | Line(s) | Finding | Severity |
|------|---------|---------|----------|
| `wad_loader.py` | 33-36 | `WADLoader` class — exists and functional | ✅ SOUND |
| `wad_loader.py` | ~30-60 | IWAD resolution from `config/omega.yaml` | ✅ SOUND |
| `wad_loader.py` | — | PWAD merge semantics (later overrides earlier) | ✅ SOUND |

### 5.3 Disk Usage Summary

| Location | Size | Notes |
|----------|------|-------|
| `data/entities/` | ~221MB total | Roc Racoon dominates (178MB — knowledge workspace) |
| `config/wads/_omega_default/entities.yaml` | 30KB | Clean post-fix |
| `config/wads/_omega_default/entities.yaml.bak` | **25MB** | 🔴 Can be deleted post-verification |
| `config/wads/arcana_novai/entities.yaml` | 69KB | 34 entities, 2224 lines |
| `data/memory/fts_memory.db` | 745KB | +4MB WAL (⚠️ needs checkpoint) |
| `data/coordination/` | ~500KB | Mostly handoff markdowns |
| `data/handoff/` | ~280KB | Stale + active packets |

### 5.4 Entity Count Reconciliation

```
_config/wads/_omega_default/entities.yaml_ → 24 entities (should be 12)
  │
  ├── 12 correct IWAD entities (sysadmin, datastore, buildmaster, bridge, sentinel,
  │         modelgate, context, watchtower, link, verifier, iris, sophia)
  │
  ├── 10 fleet entities that should be PWAD-only (doom guy, jem, kali, lilith,
  │         ma'at, researcher, roc racoon, john carmack, makali, verity)
  │
  └── 2 test entities (test_get_returns_entity, testentity)
  
_data/entities/_ → 41 directories (should be ~21-22)
  │
  ├── 21 active entity dirs with souls ✅
  ├── 8 without soul.yaml (5 orphans + 2 system + 1 test)
  ├── 9 additional system/test/legacy dirs
  └── 3 borderline (cli_cline, cli_gemini, omnidroid)
```

---

## Final Verdict

**Persistence domain is STRUCTURALLY SOUND but DATA-OVERWEIGHT.** The core architecture (EntityRegistry with ZONEID, Hard-Boundary, lazy deletion, atomic writes) is correct and well-implemented. The data hygiene issues are an accumulation problem, not a design problem.

**Epoch I Readiness**: ⚠️ **NOT READY**

| Precondition | Status | Why |
|-------------|--------|-----|
| ✅ 1. entities.yaml corruption fixed | ✅ PASS | D-kal-180 applied, file is 30KB clean |
| 🔴 2. Entities reduced to 12 | **FAIL** | 24 entities in IWAD, 12 must be removed |
| 🔴 3. Orphan directories cleaned | **FAIL** | 6-8 directories need purge |
| 🟡 4. Soul versions verified | **PARTIAL** | SOUL_MIGRATION_AUDIT_LOG is inaccurate |
| 🟡 5. Handoff queue clean | **PARTIAL** | 40 stale handoffs remain |
| 🟡 6. FTS database healthy | **PARTIAL** | 4MB WAL needs checkpoint |

**Estimated time to unblock**: **~7-9 hours** of direct engineering work (not inference), broken into parallelizable tracks A (3 hr), B (4 hr), C (2 hr), D (2 hr). Track A + B1 are the critical path.

---

*⬡ OMEGA ⬡ DATASTORE (P2) ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ P2-ASSESSMENT ⬡ EPOCH-I*
*Next action: Submit this report to Hivemind and signal to Ma'at for Build Side synthesis.*
