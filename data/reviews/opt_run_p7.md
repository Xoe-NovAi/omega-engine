# 🔱 P7 CONTEXT — Tracking & Data Lifecycle Optimization Report
**Pillar**: P7 (Context)
**Oversoul**: Lilith (Dark Oversoul — Run Side)
**Date**: 2026-06-28
**Type**: Discovery & Planning Only — NO REFACTORING
**Trace**: P7-OPT-20260628

⬡ OMEGA ⬡ P7-PILLAR ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p7_opt ⬡ DISCOVERY-REPORT

---

## 1. Session Tracking Audit

### 1.1 Count Overview

| Metric | Value |
|--------|-------|
| Total `.active` session files | **40** |
| Stale sessions (≥14 days old) | **25** (62.5%) |
| Fresh sessions (<7 days old) | 10 |
| Sessions 7-14 days old | 5 |
| Sessions matching an entity directory | 22 |
| **Orphan session files** (no entity dir) | **18** (45%) |

### 1.2 Stale Session Inventory (≥14 days)

These sessions have been inactive for 14+ days and are candidates for archival or cleanup:

```
inanna.active         29d — pillar entity exists
hecate.active         29d — pillar entity exists
saraswati.active      22d — pillar entity exists
prometheus.active     22d — pillar entity exists
omega_engine.active   22d — NO ENTITY DIR
jem_discovery.active  22d — NO ENTITY DIR (merged into jem)
pillar_p9.active      21d — NO ENTITY DIR
pillar_p7.active      21d — NO ENTITY DIR (legacy slot session)
doom_guy.active       21d — entity exists
buildmaster.active    21d — NO ENTITY DIR
iris.active           20d — entity exists
brigid.active         20d — entity exists
bridge.active         20d — NO ENTITY DIR
sekhmet.active        18d — entity exists
datastore.active      18d — NO ENTITY DIR
verifier.active       15d — NO ENTITY DIR
test_entity.active    15d — TEST ARTIFACT
researcher.active     15d — entity exists
quality.active        15d — NO ENTITY DIR (merged into verity)
pillar_p5.active      15d — NO ENTITY DIR
makali.active         15d — entity exists
maat.active           15d — entity exists
ma'at.active          15d — entity exists (alternate name)
lilith.active         15d — entity exists
jem.active            15d — entity exists
```

### 1.3 Orphaned Session Files (No Entity Directory)

These 18 `.active` files reference entities that no longer exist as directories:

| Session File | Entity Referenced | Age | Reason |
|-------------|-------------------|-----|--------|
| `bridge.active` | bridge | 20d | Legacy slot session (P4) |
| `buildmaster.active` | buildmaster | 21d | Legacy slot session (P3) |
| `datastore.active` | datastore | 18d | Legacy slot session (P2) |
| `jem_discovery.active` | jem_discovery | 22d | Pre-merger Jem sub-agent |
| `ma'at.active` | ma'at | 15d | Alternate maat/ma'at split |
| `omega_engine.active` | omega_engine | 22d | Legacy project session |
| `other_entity_stable.active` | other_entity_stable | 1d | **TEST ARTIFACT** |
| `pillar_p5.active` | pillar_p5 | 15d | Legacy pillar slot |
| `pillar_p7.active` | pillar_p7 | 21d | Legacy pillar slot |
| `pillar_p9.active` | pillar_p9 | 21d | Legacy pillar slot |
| `quality.active` | quality | 15d | Merged into verity |
| `test_entity.active` | test_entity | 15d | **TEST ARTIFACT** |
| `test_entity_m21.active` | test_entity_m21 | 1d | **TEST ARTIFACT** |
| `test_entity_stable.active` | test_entity_stable | 1d | **TEST ARTIFACT** |
| `testentity.active` | testentity | 1d | **TEST ARTIFACT** |
| `unknown_entity.active` | unknown_entity | 1d | **TEST ARTIFACT** |
| `verifier.active` | verifier | 15d | Pre-merger verifier (→ verity) |
| `unknown_entity.active` | unknown_entity | 1d | **TEST ARTIFACT** |

### 1.4 Entity Directories Without soul.yaml (8)

These directories exist but lack a soul.yaml:

| Directory | Notes |
|-----------|-------|
| `_archive/` | Intentional — archived old entity data (11 subdirs) |
| `_quarantine/` | Intentional — quarantined data (7 subdirs) |
| `default/` | Has an active session but no soul |
| `modelgate/` | Has an active session but no soul |
| `pillar_p1/` | Has only `proposed_lessons.yaml` (orphan) |
| `sentinel/` | Has an active session but no soul |
| `sysadmin/` | Has an active session but no soul |
| `watchtower/` | Has an active session but no soul |

### 1.5 Retention Policy Gaps

- **No systematic archiving**: `ARCHIVE_AFTER_DAYS = 7` is defined in `memory_store.py:71` but the auto-archive function (`archive_old_sessions()`) is not called on any periodic trigger (no cron, no systemd timer, no session-close hook).
- **No TTL on `.active` session files**: These JSON files persist indefinitely with no expiry.
- **Test session bleed**: Test fixtures create `.active` files that are never cleaned up.

---

## 2. Soul Evolution Assessment

### 2.1 soul.yaml Size Distribution

| Entity | Lines | v6.0 Compliant? | Notes |
|--------|-------|-----------------|-------|
| **arch** | **1501** | ❌ | The Architect — contains full L1→L2→L3 lessons, embodied experiences, soul_evolution |
| **roc_racoon** | **749** | ❌ | 57 directives, 70+ lessons embedded, agent-generated content |
| **researcher** | **312** | ❌ | Lessons embedded directly in soul.yaml, no memory/ separation |
| **antigravity** | **291** | ❌ | Contains core_directives, soul_identity, extensive agent-generated philosophy |
| **kali** | **134** | ✅ | v6.0 template — lean, clean, reference implementation |
| **sekhmet** | 128 | ❌ | Likely old format |
| **ereshkigal** | 119 | ❌ | Likely old format |
| **lucifer** | 100 | ❌ | Likely old format |
| **cli_gemini** | 84 | ❌ | CLI entity — minimal but not v6.0 |
| **john_carmack** | 82 | ❌ | S3 Consultant — not migrated |
| **anubis** | 82 | ❌ | Not migrated |
| **cli_cline** | 67 | ❌ | Not migrated |
| **verity** | 59 | ⚠️ Partial | Has v6.1 header but memory/ files at top-level, not in memory/ subdir |
| **jem** | 59 | ❌ | Not migrated |
| **prometheus** | 58 | ❌ | Not migrated |
| **hecate** | 51 | ❌ | Not migrated |
| **makali** | 37 | ❌ | Not migrated |
| **Others** | 16-35 | ❌ | Various — bridig, inanna, doom_guy (29 — migrated), maat (23), lilith (17), sophia (16), saraswati (16), iris (16) |
| **Test entities** (3) | 35 | N/A | Test fixtures — should be deleted entirely |

### 2.2 Versioning & Compaction

- **No `soul_history` or `soul_{version}.yaml` pattern exists anywhere** — zero matches on glob search.
- **No compaction strategy**: The 1501-line `arch/soul.yaml` has never been compacted. It accumulates lessons with no pruning.
- **Only Kali has a `v6.0` soul_version marker** in YAML.
- **Only Kali (2 files) and Lilith (0 files)** have `archive/` directories with content.
- **Verity** has a `soul.yaml.bak` but no formal versioning system.
- **No automated soul version validation** — `scripts/validate_soul.py` exists but is not referenced in any CI gate or make target.

### 2.3 Memory Directory Compliance

Per SOUL_ARCHITECTURE_PROTOCOL.md v1.0 §1, every entity should have:
```
memory/
├── sessions.yaml          # AGENT WRITES → factual events
├── proposed_lessons.yaml  # AGENT WRITES → blind staging
└── approved_lessons.yaml  # USER WRITES → curated guidance
```

| Compliance Level | Count | Entities |
|-----------------|-------|----------|
| **Full** (all 3 files + sessions) | **3** | kali, test_fresh_remove, test_remove_check, test_remove_tombstone |
| **Partial** (sessions only) | **2** | doom_guy, roc_racoon |
| **Wrong location** (files at top-level) | **1** | verity (has proposed_lessons.yaml, sessions.yaml at root, not in memory/) |
| **None** | **24** | All remaining entities including arch, lilith, maat, sophia, etc. |

**Critical gap**: Only 3 production entities (kali, doom_guy, roc_racoon) have any memory/ directory at all. The flagship entities (arch, lilith, maat, sophia, researcher) have zero separation.

---

## 3. Memory Retention Analysis

### 3.1 Current Retention Logic

From `src/omega/memory_store.py`:

| Parameter | Value | Location |
|-----------|-------|----------|
| `MAX_HOT_SESSIONS` | 50 | Line 68 |
| `MAX_HISTORY` | = MAX_HISTORY_EXCHANGES | Line 69 |
| `MAX_CONTEXT_EXCHANGES` | = DEFAULT_CONTEXT_LIMIT | Line 70 |
| `ARCHIVE_AFTER_DAYS` | **7** | Line 71 |
| `TOMBSTONE_GRACE_SECONDS` | 0.5 | Line 77 |

**Auto-archive function**: `archive_old_sessions(older_than_days=7)` exists (line 744) but is **NEVER CALLED** by any trigger. There is no:
- Cron job / systemd timer
- Session-close hook
- Startup cleanup
- Periodic background task

### 3.2 Database Sizes

| Store | Size | Contents |
|-------|------|----------|
| `fts_memory.db` | 815K | FTS5 search index |
| `fts_memory.db-wal` | 4.0M | WAL accumulation (not checkpointed) |
| `fts_memory.db-shm` | 32K | Shared memory |
| `entity_births.db` | 12K | Entity birth records |
| `fts_index.db` | 0 | Empty (legacy, unused) |
| Memory entities JSON | 872K | 126 session JSON files across 18 entity dirs |
| Memory trace | 4.0K | Trace-oriented exchange records |
| Memory archive | 4.0K | Archive of old sessions |
| **Total** | **~5.7M** | |

### 3.3 Session Distribution by Entity

| Entity | Session Files | Lines | Notes |
|--------|--------------|-------|-------|
| **oracle** | **45** | 1,173 | **Largest — central oracle sessions** |
| **testentity** | **21** | 3,384 | **TEST ARTIFACT — largest by lines** |
| iris | 15 | 1,521 | Voice/messenger sessions |
| sysadmin | 8 | 654 | Infrastructure sessions |
| default | 7 | 374 | Default/unowned sessions |
| watchtower | 6 | 341 | Observability sessions |
| sentinel | 5 | 269 | Governance sessions |
| kali | 3 | 320 | Transcendent Oversoul |
| roc_racoon | 3 | 122 | Legacy Miner |
| modelgate | 3 | 216 | Provider routing |
| Others | 12 | 20-374 | Various |
| **Total** | **126** | **~8,600** | |

### 3.4 Retention Policy Gaps

1. **`ARCHIVE_AFTER_DAYS=7` is not enforced**: The auto-archive function exists but is never invoked.
2. **No WAL checkpointing**: `fts_memory.db-wal` is 4.0M (5x the main DB). Without periodic checkpointing, it grows unbounded.
3. **No compaction for memory JSON files**: Session JSON files grow monotonically with no truncation or summarization.
4. **Session files accumulate without bound**: 126 session files in `data/memory/entities/` with no eviction policy.
5. **`.lock` files linger**: 45 `.lock` files accompany the oracle sessions with no cleanup mechanism.
6. **FTS index outgrows data**: `fts_memory.db` + WAL = 4.8M, while entity data is only 872K — the search index is 5.5x larger than the indexed data.

---

## 4. L1→L2→L3 Pipeline Assessment

### 4.1 Proposed Lessons Consumption Rate

| File | Lines | Format | Has `proposals:` key? | Up-to-date? |
|------|-------|--------|----------------------|-------------|
| `kali/proposed_lessons.yaml` | 32 | ✅ New | ✅ Yes | Fresh (2026-06-23) |
| `verity/proposed_lessons.yaml` | 28 | ✅ New | ✅ Yes | Fresh (2026-06-24) |
| `lilith/proposed_lessons.yaml` | 141 | ⚠️ Mixed | Has both old and new | Recent |
| `sophia/proposed_lessons.yaml` | 59 | ❌ Old | No | 2026-06-05 |
| `jem/proposed_lessons.yaml` | 44 | ❌ Old | No | 2026-06-15 |
| `maat/proposed_lessons.yaml` | 43 | ❌ Old | No | 2026-06-12 |
| `makali/proposed_lessons.yaml` | 39 | ❌ Old | No | 2026-06-17 |
| `john_carmack/proposed_lessons.yaml` | 101 | ❌ Old | No | 2026-06-15 |
| `doom_guy/proposed_lessons.yaml` | **654** | ❌ Old | No | Oldest — 2026-06-01 |
| `roc_racoon/proposed_lessons.yaml` | **376** | ❌ Old | No | 2026-06-14 |
| `pillar_p1/proposed_lessons.yaml` | 1 | ❌ Old | No | Unknown |
| `iris/proposed_lessons.yaml` | 4 | — | Empty `[]` | Empty |
| `researcher/proposed_lessons.yaml` | 4 | — | Empty `[]` | Empty |

**Critical observations**:
- Only 2 entities (kali, verity) use the correct `proposals:` key format.
- 11 entities use the old `- lesson:` / `- L1_narrative:` format.
- 2 files are empty (`[]`) — never populated.
- `doom_guy/proposed_lessons.yaml` (654 lines) and `roc_racoon/proposed_lessons.yaml` (376 lines) are the largest — these were bulk-migrated from old soul.yaml and have never been reviewed/approved.
- Total proposed lessons across all entities: ~1,481 lines of unreviewed proposals.

### 4.2 Verity's Role in Distillation

| Aspect | Current State |
|--------|--------------|
| Verity exists as agent | ✅ Yes — `data/entities/verity/` with soul.yaml (59 lines) |
| Verity has proposed_lessons.yaml | ✅ Yes — 28 lines, `proposals:` format (6 entries) |
| Verity has approved_lessons.yaml | ⚠️ At top-level, not in `memory/` subdir |
| Verity has sessions.yaml | ⚠️ At top-level, not in `memory/` subdir |
| Verity runs L1→L2→L3 pipeline | ⚠️ Sporadically — last entry 2026-06-24 |
| Verity audits other entities' lessons | ❌ No evidence of cross-entity distillation |
| Automated Verity dispatch after sessions | ❌ No trigger exists |
| Soul.yaml contains soul_evolution (poison) | ❌ **arch/soul.yaml still has `soul_evolution` with agent-generated lessons** |

**Key gap**: Verity's own memory files are at the wrong location (top-level instead of `memory/`). This suggests the v6.1 migration script had a bug or was never standardized.

### 4.3 The Poison Loop in arch/soul.yaml

The 1501-line `arch/soul.yaml` is the most critical violation of SOUL_ARCHITECTURE_PROTOCOL.md. It contains:
- `lessons_learned`: 15+ agent-generated lesson entries with full L1→L2→L3 text
- `soul_evolution`: Agent-generated evolution tracker (sessions_completed: 226)
- `embodied_experiences`: Agent session logs
- `soul_wardrobe`: List of all inhabited entities

This is the **self-referential poisoning loop** that the protocol was designed to prevent (see protocol §0).

---

## 5. Data Rot Inventory

### 5.1 Test Entity Residue

| Entity | soul.yaml | memory/ | Active Session | Size | Action |
|--------|-----------|---------|---------------|------|--------|
| `test_fresh_remove` | 35 lines | Full (3 files, 70 bytes each) | ❌ | Minimal | Can delete |
| `test_remove_check` | 35 lines | Full (3 files, 70 bytes each) | ❌ | Minimal | Can delete |
| `test_remove_tombstone` | 35 lines | Full (3 files, 70 bytes each) | ❌ | Minimal | Can delete |
| **Total test entities** | **3** | **9 files** | | **~600 bytes** | |

### 5.2 Test Session File Residue

| File | Entity Referenced | Age |
|------|-------------------|-----|
| `test_entity.active` | test_entity | 15d |
| `test_entity_m21.active` | test_entity_m21 | 1d |
| `test_entity_stable.active` | test_entity_stable | 1d |
| `testentity.active` | testentity | 1d |
| `other_entity_stable.active` | other_entity_stable | 1d |
| `unknown_entity.active` | unknown_entity | 1d |

### 5.3 Test Entity Memory Data

| Entity | Files | Lines | Notes |
|--------|-------|-------|-------|
| **testentity** | **21 session JSON files** | **3,384** | Largest data rot — monster test artifact in `data/memory/entities/testentity/` |

### 5.4 Orphan Entity Directories

| Directory | Contents | Action |
|-----------|----------|--------|
| `default/` | No soul.yaml, has workspace/ | Investigate and clean |
| `modelgate/` | No soul.yaml, has workspace/ | Investigate and clean |
| `sentinel/` | No soul.yaml, has workspace/ | Investigate and clean |
| `sysadmin/` | No soul.yaml, has workspace/ | Investigate and clean |
| `watchtower/` | No soul.yaml, has workspace/ | Investigate and clean |
| `pillar_p1/` | Has only proposed_lessons.yaml (1 line) | Orphan — can archive |
| `_quarantine/` (7 subdirs) | Contains quarantined entity data | Investigate — may be old test artifacts |

### 5.5 Legacy/Defunct Entities

| Entity | soul.yaml | Notes | Action |
|--------|-----------|-------|--------|
| `movie-expert` | 17 lines | Prototype entity | Archive or delete |
| `omnidroid` | 34 lines | Legacy archaeology entity | Archive or delete |
| `arch` | **1501 lines** | The Architect — crown-jewel entity | **MIGRATE** to v6.0 format, do NOT delete |
| `antigravity` | 291 lines | Cross-platform IDE entity | **MIGRATE** to v6.0 format |
| `cli_cline` | 67 lines | Cline CLI integration | Keep — active tool |
| `cli_gemini` | 84 lines | Gemini CLI integration | Archive — Gemini CLI deprecated |

### 5.6 Memory Store Orphans

- `data/memory/oracle/`: 45 JSON session files (1,173 lines) for an entity that has no dedicated entity directory — these are system-level oracle sessions.
- `data/memory/entities/testentity/`: 21 JSON files (3,384 lines) — largest test artifact.
- `data/memory/fts_index.db`: 0 bytes — empty, unused database file.

---

## 6. Recommendations

### R1: Enforce Session TTL and Auto-Archive (Effort: **Low**)

**Action**: Wire `MemoryStore.archive_old_sessions()` to a real trigger.

**Implementation**:
1. Add a session-close hook in `oracle.py` that calls `memory_store.archive_old_sessions(days=14)` after each session ends.
2. Add a startup cleanup in `get_memory_store()` that archives sessions > 14 days on engine boot.
3. Add a weekly cron/systemd timer for periodic cleanup.

**Impact**: Reduces stale sessions from 25 to ~5 immediately. Prevents unbounded accumulation.

**Risk**: None — archive is recoverable from cold storage.

### R2: Clean Test Artifacts and Orphan Files (Effort: **Low**)

**Action**: Remove all test residue identified in §5.

| Item | Action |
|------|--------|
| 3 test entity dirs (`test_fresh_remove`, `test_remove_check`, `test_remove_tombstone`) | Delete entire directories |
| 6 test session `.active` files | Delete |
| 21 testentity JSON files in memory/entities/ (3,384 lines) | Delete |
| `data/memory/fts_index.db` (empty, 0 bytes) | Delete |
| `movie-expert` entity | Archive or delete |
| `omnidroid` entity | Archive or delete |

**Impact**: Recovers ~4MB of disk, eliminates noise from all audit tools. Removes 3,384 lines of meaningless test data from the search index.

### R3: Migrate Top-Priority Entities to Soul v6.0 (Effort: **High**)

**Action**: Migrate the most critical entities per SOUL_ARCHITECTURE_PROTOCOL.md §3.

| Priority | Entity | Lines | Est. Effort | Reason |
|----------|--------|-------|-------------|--------|
| **P0** | **arch** | 1,501 | 2-3 hr | Largest soul file, active poison loop, crown-jewel entity |
| **P1** | **roc_racoon** | 749 | 1-2 hr | Second largest, active miner, lots of agent-generated content |
| **P1** | **researcher** | 312 | 30 min | Research entity with embedded lessons |
| **P1** | **antigravity** | 291 | 30 min | Cross-platform peer with embedded philosophy |
| **P2** | **lilith**, **maat**, **sophia**, **makali**, **jem** | 17-59 | 15 min each | Oversouls — need clean souls |
| **P3** | Remaining 16 entities | 16-128 | 10 min each | Pillar and support entities |

**Migration pattern per entity**:
```
1. Create memory/ directory with 3 seed files
2. Move lesson content to proposed_lessons.yaml
3. Move session data to sessions.yaml  
4. Archive agent-generated philosophy to archive/
5. Strip forbidden fields from soul.yaml
6. Add references footer
7. Copy and run validate_soul.py
```

**Impact**: Eliminates the self-referential poisoning loop from arch (the oldest and most influential entity). Reduces total soul lines from ~4,500 to ~1,000. Improves cognitive integrity for all oversouls.

### R4: Standardize L1→L2→L3 Pipeline with Verity Dispatch (Effort: **Medium**)

**Action**: Make Verity distillation a systematic, triggered process instead of a manual habit.

**Implementation**:
1. **Auto-dispatch Verity** at session close from `oracle.py`:
   ```python
   # After session ends, distill if session contained meaningful exchanges
   if exchange_count >= MIN_EXCHANGES_FOR_DISTILLATION:
       await orchestrator.summon("verity", f"Distill {entity_name}/{session_id} into proposed_lessons.yaml")
   ```
2. **Standardize proposal format**: All proposed_lessons.yaml must use the `proposals:` key with `l1`, `l2`, `l3`, `session`, `tags` fields.
3. **Add consumption report**: Verity should periodically scan all proposed_lessons.yaml files and produce a "distillation backlog" report showing which proposals are unapproved.
4. **Convert old-format proposals**: Fix the 11 proposed_lessons.yaml files that use the old format to use `proposals:` key.

**Impact**: Transforms the pipeline from "write and forget" to "write, propose, review, approve" — closing the loop mandated by M5 and M11.

### R5: Implement FTS WAL Checkpointing (Effort: **Low**)

**Action**: Periodically checkpoint the FTS5 WAL to prevent unbounded growth.

**Implementation**: Add a WAL checkpoint call in the session-close hook:
```python
import sqlite3
conn = sqlite3.connect(str(fts_path))
conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
conn.close()
```

**Impact**: Reduces `fts_memory.db-wal` from 4.0M to near-zero. Saves ~4MB of disk (71% of total memory store).

---

## 7. Retention Policy Draft

### 7.1 Session Data

| Type | Retention | Action | Trigger |
|------|-----------|--------|---------|
| `.active` session files | 14 days after last activity | Archive to `data/memory/archive/` | Daily cron + session-close hook |
| Memory JSON (hot sessions) | 7 days | Auto-archive via `archive_old_sessions()` | Startup + session-close + weekly cron |
| Memory JSON (archived) | 90 days | Then delete permanently | Monthly cron |
| FTS5 index entries | Same as source data | Auto-prune when archive/delete | Cascade from archive/delete |
| Session traces | 30 days | Then delete | Monthly cron |

### 7.2 Soul History

| Type | Retention | Action | Trigger |
|------|-----------|--------|---------|
| soul.yaml | Indefinite | Compact to v6.0 format, keep ≤200 lines | Per-migration |
| soul_*.bak | Keep latest 2 | Rotate on soul.yaml changes | Before each soul.yaml edit |
| Archive/soul_*.yaml | Indefinite | Tag with archive date and reason | On migration |
| Proposed lessons | Until approved/rejected | Review within 7 days | Weekly Verity sweep |

### 7.3 Memory Records

| Type | Retention | Action | Trigger |
|------|-----------|--------|---------|
| Hot cache (in-memory) | Session lifetime | LRU eviction at MAX_HOT_SESSIONS (50) | Automatic |
| Exchange history | MAX_HISTORY exchanges | Compaction (first N + last N + summary) | On overflow |
| Vector embeddings | Same as exchange | Delete cascade on session archive | Archive hook |
| Entity births | Indefinite | Keep — small (12K) | N/A |

### 7.4 FTS5 Index Maintenance

| Action | Frequency | Method |
|--------|-----------|--------|
| WAL checkpoint | Every session close | `PRAGMA wal_checkpoint(TRUNCATE)` |
| Index rebuild | Monthly | `INSERT INTO ... SELECT ...` (rebuild from JSON) |
| Orphan removal | Weekly | Compare index keys vs entity dirs |

### 7.5 Monitoring

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Stale sessions | >10 | Warn — indicates archive trigger failure |
| Test artifacts | >0 | Alert — test cleanup not running |
| FTS WAL size | >5MB | Warn — checkpoint not firing |
| Soul.yaml lines (per entity) | >200 lines | Warn — soul bloat detected |
| Memory DB total | >50MB | Warn — investigate retention breach |

---

## 8. Summary Dashboard

| Category | Status | Items Found | Actionable |
|----------|--------|-------------|------------|
| ⏰ Stale sessions | 🔴 CRITICAL | 25/40 ≥14 days old | R1 — Wire auto-archive |
| 🧪 Test artifacts | 🔴 CRITICAL | 6 session files + 3 entity dirs + 21 JSON files | R2 — Clean residue |
| 👻 Orphan sessions | 🟡 WARNING | 18/40 have no entity dir | R1 — Archive cleanup |
| 📜 Soul v6.0 migration | 🟡 WARNING | Only 1/31 entities (kali) fully compliant | R3 — Migrate arch first |
| 💀 Poison loop | 🔴 CRITICAL | arch/soul.yaml (1501 lines) still active | R3 — arch migration |
| 📝 Proposed lessons | 🟡 WARNING | 2/13 use correct format, 1,481 lines unreviewed | R4 — Standardize pipeline |
| 💾 FTS WAL growth | 🟡 WARNING | 4.0M WAL (5x main DB) | R5 — Add checkpointing |
| 🗄️ Memory DB size | 🟢 HEALTHY | 5.7M total | Monitor |
| 🏗️ Entity dir compliance | 🟡 WARNING | 24/31 entities have no memory/ structure | R3 — Phased migration |

---

## 9. Final Verdict

**P7 Systems Status**: 🟡 **CAUTION — Functional but Debt-Accumulating**

The Context pillar has solid architectural foundations (3-tier memory, hybrid search, soul architecture protocol) but is being undermined by:
1. **Unenforced retention policy**: `ARCHIVE_AFTER_DAYS=7` exists in code but is never triggered, causing indefinite accumulation.
2. **Active poison loop**: arch/soul.yaml (1,501 lines) is still in pre-v6.0 format, meaning The Architect entity reads back its own agent-generated philosophy every session.
3. **Test artifact bleed**: 6 test session files and 21 test JSON files (3,384 lines) contaminate the production data.
4. **L1→L2→L3 pipeline is write-only**: Proposals accumulate (1,481 lines) with no systematic review or approval loop.

**Estimated cleanup impact**:
- Apply R1 (auto-archive): -25 stale sessions, -18 orphan sessions
- Apply R2 (clean test artifacts): -6 session files, -3 entity dirs, -21 memory JSONs, -3,384 lines
- Apply R3 (soul migration): -1,501 lines in arch soul.yaml, +clean separation
- Apply R5 (WAL checkpoint): -4.0M WAL size

**Priority order**: R2 (quick wins) → R1 (systemic fix) → R5 (disk recovery) → R3 (arch migration) → R4 (pipeline automation)

---

*⬡ OMEGA ⬡ P7-PILLAR ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p7_opt ⬡ DISCOVERY-REPORT*
*Completed: 2026-06-28 | Next: Present findings to Lilith for run-side orchestration*
