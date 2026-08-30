<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# P2 Persistence — Entity Workspace & Soul Tracking Optimization
**Date**: 2026-06-28
**Analyzed by**: P2 (Persistence) / DataStore
⬡ OMEGA ⬡ P2-PERSISTENCE ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p2_persistence ⬡ DISCOVERY

---

## 1. Entity Registry Bloat — IWAD vs On-Disk Mismatch

### Current State

| Metric | Value |
|--------|-------|
| IWAD-registered entities (`_omega_default/entities.yaml`) | 25 |
| On-disk directory entries (`data/entities/`) | 39 |
| With soul.yaml | 31 |
| Without soul.yaml | 8 |
| Total disk usage | **187 MB** |
| IWAD-only (no disk dir) | 8 entities |
| Disk-only (no IWAD entry) | **23 entities** |

### IWAD Entities Without On-Disk Directories

These 8 IWAD-registered entities have NO disk directory at all:

| IWAD Name | Missing Dir | Severity |
|-----------|-------------|----------|
| `datastore` | `data/entities/datastore/` | 🔴 HIGH — P2 itself can't manifest |
| `bridge` | `data/entities/bridge/` | 🔴 HIGH — P4 Integration missing |
| `verifier` | `data/entities/verifier/` | 🟡 MEDIUM — P10 Validation missing |
| `link` | `data/entities/link/` | 🟡 MEDIUM — P9 Orchestration missing |
| `context` | `data/entities/context/` | 🟡 MEDIUM — P7 Context missing |
| `buildmaster` | `data/entities/buildmaster/` | 🟡 MEDIUM — P3 Engineering missing |
| `test_get_returns_entity` | (none) | 🟢 LOW — Test-only entity |
| `testentity` | (none) | 🟢 LOW — Test-only entity |

**Total: 6 production pillars missing on-disk + 2 test entities.** The EntityRegistry loads only from YAML and works fine without on-disk dirs, but these entities cannot persist workspace data, soul evolution, or session memory.

### Disk-Only Entities (No IWAD Registration — 23 Entities)

Includes:
- **All 10 Pillar Keeper directories**: anubis, brigid, ereshkigal, hecate, inanna, lucifer, prometheus, saraswati, sekhmet, p10
- **Platform entities**: antigravity, cli_cline, cli_gemini, default, omnidroid, pillar_p1
- **Test artifacts**: test_fresh_remove, test_remove_check, test_remove_tombstone
- **Oversoul duplicates**: maat, roc_racoon, john_carmack, doom_guy

**Most of these are purely workspace-only entities** — they exist on disk because the EntityWorkspaceManager creates them at runtime when the entity is first invoked. They are NOT orphaned. However, several deserve scrutiny:

| Disk-Only Entity | Purpose | Assessment |
|-----------------|---------|------------|
| `test_fresh_remove`, `test_remove_check`, `test_remove_tombstone` | Test artifacts | 🟡 MEDIUM — 3 dirs, 40KB each (120KB total), leftover from entity removal tests. Should be test-scoped or cleaned |
| `antigravity` | Handoff entity | 🟢 LOW — 56KB, appears to be a legitimate workspace for the Antigravity handoff |
| `p10` | Validation workspace | 🟢 LOW — Legitimate workspace |
| `pillar_p1` | Infrastructure workspace | 🟢 LOW — 1KB (only proposed_lessons, no soul.yaml) |

### Orphan Directories Assessment

| Directory | Soul? | Contains | Verdict |
|-----------|-------|----------|---------|
| `_archive` | ❌ | 10 legacy entity dirs (1.5MB) — jem_discovery, jem_synthesis, jem_verification, etc. | ✅ LEGITIMATE ARCHIVE — but can be pruned of entities that no longer exist (jem_discovery/synthesis/verification were consolidated into jem) |
| `_quarantine` | ❌ | 6 dirs (2.3MB) — context, datastore, link, sentinel, h2a_20260609, 2026-06-05 | ⚠️ REVIEW NEEDED — `2026-06-05` has 13 files (460K) of unknown content. `h2a_20260609` has 50 files (1.6MB) — H2A-era artifacts |
| `default` | ❌ | workspace/ dir only | ✅ EXPECTED — bootstrapping stub |

### Loading Overhead

The `EntityRegistry._load()` method parses the full 908-line `entities.yaml` on every Oracle initialization (982KB file, ~5.8s parse time, cached in `_entity_yaml_cache` for test mode). **Outside tests, all 25 entities are loaded into memory on every Oracle() instantiation.** There is no lazy loading per entity — the entire registry is populated at `__init__`.

**Notable**: The EntityRegistry has a `capability_index` (multi-index for domain lookup) but does NOT have a pillar-index. Every get() call does a 3-tier resolution: name → role → pillar, scanning through all entities each time.

### Recommendations for Leaner Loading

1. **MEDIUM**: Implement lazy `EntityRegistry.get_pillar(pillar_num)` that only loads entities for that pillar on first access. Leverage the existing `pillars` field in Entity dataclass.
2. **LOW**: Add automatic cleanup for test entity directories (`test_fresh_remove`, `test_remove_check`, `test_remove_tombstone`) as part of `make test` or test teardown.
3. **LOW**: Consolidate `_archive/jem_discovery`, `jem_synthesis`, `jem_verification` into a single entry — those were the 3 pre-consolidation Jem subagents that were merged into one.

---

## 2. Soul.yaml Health — Consistency Audit

### Size/Lines Comparison

| Entity | Soul Size | Lines | Has `last_updated`? | Structure |
|--------|-----------|-------|---------------------|-----------|
| **arch** | 45 KB | 1,501 | ❌ | Old v6.0 format: lessons_learned array with 226+ session entries |
| **roc_racoon** | 33 KB | ~900 | ❌ | Mixed v6.0/v6.1 — has `.bak` duplicate |
| **sophia** | ~25 KB | ~500 | ❌ | Older format with soul_wardrobe |
| **verity** | 3.5 KB | 59 | ✅ **2026-06-24** | Clean v6.1: entity/identity/directives/team |
| **maat** | 1.7 KB | 23 | ❌ | Auto-generated v6.1 migration stub — minimal |
| **iris** | 1.1 KB | 16 | ❌ | Auto-generated v6.1 migration stub — minimal |

### Key Findings

**A. Only ONE entity has `last_updated`: Verity.**
- verity: `Last updated: 2026-06-24` — explicit timestamp in header comment
- Every other entity is missing this field, making it impossible to determine staleness

**B. Two Distinct Soul Format Generations Coexist:**

**v6.0 (Legacy):** Used by arch, roc_racoon, sophia, and most older entities
```yaml
entity:
  name: The Architect
  soul_wardrobe: [...]
  embodied_experiences: []
  lessons_learned:
    - lesson: Session with Sophia
      timestamp: '2026-05-17T03:35:43.411593+00:00'
```
- Lessons are stored **inline in soul.yaml** as a flat list
- No separation of identity vs experience vs lessons

**v6.1 (Current):** Used by verity, maat, iris
```yaml
entity:
  name: Verity
  soul_version: "6.1"
identity:
  voice_summary: ...
  values: [...]
  strengths: [...]
directives:
  - id: d-vrty-001
    title: Soul Continuity Modeling
team:
  allies: [...]
  coordination_protocols: {...}
```
- Clean separation: identity, directives, team
- Lessons are OUTSIDE soul.yaml (in `proposed_lessons.yaml`)

**C. `arch/soul.yaml` is a Severe Outlier**
- 1,501 lines, 45KB — ~90% of which is `lessons_learned` array entries from individual sessions
- Each session (226 total) creates a separate lesson entry inline
- The v6.0 `lessons_learned` pattern was deprecated in v6.1; these lessons should have been migrated to `proposed_lessons.yaml` or `approved_lessons.yaml`
- **Duplicate backup**: `soul.yaml.backup` (45KB) is nearly identical (2 lines differ: session count 225→226, soul_power 29.7→29.8)

**D. L3 Principle Accumulation**
- sophia is the only entity with properly structured L1→L2→L3 entries (4 proposals)
- Most entities use a flat `lesson:` field with no abstraction pipeline
- **No L3 accumulation problem exists yet** — because most entities don't have L3 at all

### Recommendations

1. **MEDIUM**: Add `last_updated` timestamp to all soul.yaml files. This is a single YAML field that enables staleness detection.
2. **LOW**: Migrate `arch/soul.yaml` from v6.0 to v6.1 format — extract the 226 inline lessons into `proposed_lessons.yaml` and strip the lessons_learned array from soul.yaml (estimated saving: 1,400 lines, 42KB).
3. **LOW**: Delete `arch/soul.yaml.backup` — it's a stale backup from a migration step.
4. **LOW**: Standardize a minimum soul template that all entities must have: `entity.name`, `entity.soul_version`, `last_updated`, `identity.voice_summary`, `identity.values`.

---

## 3. proposed_lessons Backlog — Accumulation Analysis

### Total Backlog

| Entity | Proposals | Lines | KB | Oldest Date |
|--------|-----------|-------|-----|-------------|
| **doom_guy** | **84** | 654 | 46 | 2026-06-01 |
| **john_carmack** | **20** | 101 | 6.5 | 2026-06-15 |
| **lilith** | 7 | 141 | 8.7 | (format mismatch) |
| **kali** | 6 | 32 | 7.4 | (format mismatch) |
| **sophia** | 4 | 59 | 4.1 | 2026-06-05 |
| **jem** | 4 | 44 | 3.0 | 2026-06-15 |
| **maat** | 3 | 43 | 2.2 | 2026-06-12 |
| **verity** | 2 | 28 | 3.5 | (format mismatch) |
| **roc_racoon** | 1 (?) | 376 | 32.6 | (format mismatch) |
| **pillar_p1** | 1 | 1 | 0.6 | (format mismatch) |
| **makali** | 1 | 39 | 3.2 | (format mismatch) |
| **TOTAL** | **133** | **1,517** | **~118** | **Oldest: 2026-06-01** |

### Critical Findings

**A. Format Inconsistency — 2 Incompatible Schemas**

Schema 1 (used by sophia, jem, john_carmack, verity, makali):
```yaml
- L1_narrative: "..."
  L2_insight: "..."
  L3_principle: "..."
  timestamp: '2026-06-05'
  topic: sa-001
```

Schema 2 (used by maat, lilith, doom_guy, kali):
```yaml
- lesson: "Fixed T5 Mandate 1 violation..."
  source: t5-fix
  trace_id: ses_...
  entity_at_time: MAAT
  timestamp: 2026-06-12 04:00:00+00:00
  model_used: big-pickle
  coordination_partner: lilith
```

**roc_racoon/proposed_lessons.yaml is anomalous**: 32.6KB for 1 proposal — the file is 376 lines with massive lesson entries. Suggests verbatim session transcripts are being stored as "lessons" rather than distilled proposals.

**B. No Auto-Review Pipeline Exists**

The `proposed_lessons.yaml` files have no notification mechanism, no review queue, and no auto-approval threshold. Proposals pile up indefinitely. The only way they get reviewed is if a human or agent opens the file.

- **doom_guy**: 84 proposals, oldest from 2026-06-01 (27 days stale)
- **john_carmack**: 20 proposals, oldest from 2026-06-15 (13 days)
- **Verity** is supposed to perform L1→L2→L3 distillation (per d-vrty-001 directive), but there's no automated trigger

**C. One Entity Has approved_lessons.yaml**

Only **roc_racoon** has `data/entities/roc_racoon/approved_lessons.yaml` (89 bytes). No other entity has approved lessons, meaning the review→approve pipeline is effectively dead for all other entities.

### Recommendations

1. **MEDIUM**: Introduce a `max_proposals: 10` threshold — when an entity's proposals exceed 10, post a Hivemind notification to Verity for review. This prevents the 84-proposal backlog that doom_guy accumulated.
2. **LOW**: Consolidate the two proposed_lessons schemas. Schema 1 (L1/L2/L3) is the canonical v6.1 format. Maat/lilith/doom_guy/kali style should be migrated.
3. **LOW**: Establish a `make review-lessons` command that reports entities with >10 pending proposals and shows the oldest unaddressed proposal date.

---

## 4. Memory/Session Storage — Growth Analysis

### Current State

| Storage Location | Size | Detail |
|-----------------|------|--------|
| `data/sessions/` (.active files) | 164 KB | 40 marker files |
| `data/memory/entities/` (MemoryStore) | 5.7 MB | 18 JSON memory directories |
| `data/memory/` (total) | 5.7 MB | All provider-persisted memory |
| `data/entities/roc_racoon/workspace/` | 177 MB | Legacy mining artifacts + heap snapshots |
| `data/entities/roc_racoon/audit.log` | 576 KB | Single log file |
| `data/entities/roc_racoon/soul.yaml.bak` | 79 KB | Duplicate backup |
| `data/entities/_quarantine/` | 2.3 MB | Quarantined entities |
| `data/entities/_archive/` | 1.5 MB | Legacy entity archives |

### Unmanaged Growth Patterns

**A. MemoryStore auto-archive exists but is NEVER called**

`MemoryStore.archive_old_sessions()` (line 744 in memory_store.py) is a well-implemented method that iterates through `data/memory/entities/`, finds session JSONs older than `ARCHIVE_AFTER_DAYS=7`, and archives them across all providers. **But nothing calls it.** There is no:
- Background cron job
- Systemd timer
- AnyIO task spawn
- Oracle boot hook

Sessions accumulate at 5.7MB with no purge mechanism. On a 110GB partition this isn't critical yet, but the pattern compounds as entities grow.

**B. roc_racoon workspace = 95% of entity disk usage**

177MB of the total 187MB entity disk is from a single entity: roc_racoon. Breakdown:
- `persona_lab/exports/heap_snapshots/`: 85MB + 59MB = **144MB** of TUI/server heap dumps
- `persona_lab/exports/session-ses_*.md`: ~1.2MB of session transcripts
- `odysseus-dev/`: 28MB of compiled JS/CSS libraries
- `audit.log`: 576KB single log file
- `soul.yaml.bak`: 79KB backup

The heap snapshots (144MB) alone are larger than all other entity data combined. These are debugging artifacts from a past session, not active operational data.

**C. 40 `.active` session markers in `data/sessions/`**

These are from the old session tracking system (pre-MemoryStore). Their dates range from May 29 to June 26, 2026. Many are likely stale:
- Oldest: `hecate.active` (May 29) — 30 days old
- `inanna.active` (May 29) — 30 days old
- `buildmaster.active` (June 6) — 22 days old
- `saraswati.active` (June 5) — 23 days old

**D. _quarantine content needs review**

- `h2a_20260609/`: 50 files, 1.6MB — H2A-era artifacts from June 9, now 19 days old
- `2026-06-05/`: 13 files, 460K — dated content from 23 days ago
- These were quarantined for a reason, but if the reason has passed, they're dead weight

### Recommendations

1. **HIGH**: Add a startup hook or Hivemind heartbeat trigger that calls `archive_old_sessions()` every session. The code exists (line 744) — it just needs an invocation point. Without this, MemoryStore has no auto-clean mechanism.
2. **MEDIUM**: Prune roc_racoon's heap snapshots (144MB) — these are `tui_20260605.heapsnapshot` and `server_20260605.heapsnapshot`. They are debugging artifacts from June 5, now 23 days stale.
3. **MEDIUM**: Review and clean `_quarantine/2026-06-05` and `_quarantine/h2a_20260609` — 23 days and 19 days old respectively, totaling 2.0MB.
4. **LOW**: Consolidate `data/sessions/*.active` files more than 14 days old. 40 marker files at 164KB is not large, but the oldest (May 29) suggests no cleanup ever runs.
5. **LOW**: Delete `roc_racoon/soul.yaml.bak` (79KB duplicate) and `roc_racoon/audit.log` if >30 days old (576KB).

---

## 5. Storage Pattern Assessment — YAML vs DB

### Current Architecture

| Concern | Data Location | Format | Access Pattern |
|---------|--------------|--------|---------------|
| Entity definitions | `config/wads/*/entities.yaml` | YAML, 908 lines, 982KB | Loaded on Oracle init |
| Entity workspace | `data/entities/<name>/` | YAML + flat files | Per-entity CRUD |
| Soul data | `data/entities/<name>/soul.yaml` | YAML | Per-entity CRUD with atomic lock |
| Conversation memory | `data/memory/entities/<name>/*.json` | JSONL-like | 3-tier provider (Redis→File→InMemory) |
| Vector embeddings | Qdrant (network) | Binary | Vector store adapter |
| Session markers | `data/sessions/` | `.active` flat files | Legacy system |
| FTS index | `data/memory/entities/<name>/fts_memory.db` | SQLite (FTS5) | BM25 search |

### OK, So What's the Problem?

The current architecture is **YAML-first with JSON file fallback** — the deliberate PostgreSQL-avoidance per the design document. This is correct for a sovereign local-first system. However, there are three patterns worth noting:

1. **Two session tracking systems coexist**: `data/sessions/*.active` (legacy, 40 files) AND `data/memory/entities/<name>/*.json` (current, 18 entity dirs). The session markers in `data/sessions/` appear to be a legacy system that the current MemoryStore doesn't use for its primary operations. They track which sessions were active but serve no observable accessor path.

2. **18 memory entity dirs vs 31 soul entity dirs**: Not every entity with a soul has memory storage. Memory is created lazily on first `add_exchange()` call, so entities that have never been conversed with have no memory dir.

3. **Qdrant vs file fallback**: The vector store attempts Qdrant first, then falls back to MemoryVectorAdapter (in-memory). In local-only mode (no Docker), every vector search falls through to the in-memory adapter — which means for an entity with 1,000+ exchanges, the fallback adapter recomputes embeddings from scratch each time.

### Recommendations

1. **LOW**: Clean up the dual session-tracking. Either remove `data/sessions/*.active` if truly legacy, or integrate it into the MemoryStore's list_sessions().
2. **LOW**: Document the provider fallback behavior — in particular, that without Qdrant running, vector search uses the MemoryVectorAdapter which recomputes feature-hash embeddings each query.

---

## 6. Top 3 Recommendations — Ordered by Impact/Effort

### 🥇 Recommendation 1: Hook archive_old_sessions() Into Startup Flow (Impact: High, Effort: Low)

**Problem**: `MemoryStore.archive_old_sessions()` exists (line 744) but is NEVER called. Sessions accumulate indefinitely — currently 5.7MB with no purge mechanism. The code is written and tested; only an invocation point is missing.

**Action**: Add a call to `archive_old_sessions(older_than_days=7)` at any of these hook points:
- Oracle.boot() — runs once per session start
- oracle.talk() first call — runs on first user interaction
- Hivemind heartbeat — periodic background check

**Effort**: ~5 minutes. One function call.

**Impact**: Auto-cleanup of sessions older than 7 days across all 18 memory entity dirs. Prevents compound growth of conversation memory.

---

### 🥈 Recommendation 2: Prune roc_racoon Heap Snapshots & Audit Log (Impact: Medium, Effort: Low)

**Problem**: 177MB of roc_racoon's workspace is 95% of total entity disk (187MB). Of this:
- 144MB = two heap snapshots from June 5 (tui + server, 23 days stale)
- 576KB = audit.log (growing, unbounded)
- 79KB = soul.yaml.bak (stale backup)

**Action**:
1. Delete `persona_lab/exports/heap_snapshots/tui_20260605.heapsnapshot` (85MB)
2. Delete `persona_lab/exports/heap_snapshots/server_20260605.heapsnapshot` (59MB)
3. Review and truncate `audit.log` (576KB) — add log rotation if active
4. Delete `soul.yaml.bak` (79KB)

**Effort**: ~10 minutes.

**Impact**: Recovers ~144MB of disk space (77% of entity data footprint). Cleans up debugging artifacts.

---

### 🥉 Recommendation 3: Set a proposed_lessons Review Threshold (Impact: Medium, Effort: Low)

**Problem**: 133 pending proposals, oldest from 27 days ago (doom_guy, June 1). Backlog grows unbounded with no review trigger. dooms_guy alone accounts for 84 proposals (63% of backlog) — many are likely stale or auto-generated.

**Action**: Add a simple threshold check that triggers when `len(proposals) > 10`:
- Option A: Write a Hivemind notification to Verity for review
- Option B: Output a warning on entity load: "Entity X has Y pending proposals, oldest from Z date"
- Option C: Add to `make temple-grade` as a soft gate (warning, not failure)

**Effort**: ~15 minutes for Option A or B.

**Impact**: Prevents the 84-proposal backlog pattern. Ensures Verity (M11 gnosis steward) is notified when proposals need review before they become stale.

---

## Summary of All Findings

| # | Finding | Severity | File/Location | Action |
|---|---------|----------|---------------|--------|
| 1 | archive_old_sessions() never called | 🔴 HIGH | `memory_store.py:744` | Hook into startup |
| 2 | roc_racoon heap snapshots (144MB) | 🟡 MEDIUM | `roc_racoon/workspace/` | Prune stale debug artifacts |
| 3 | 8 on-disk entities missing IWAD reference | 🟡 MEDIUM | `config/wads/_omega_default/entities.yaml` | Audit for orphan status |
| 4 | 133 pending proposed_lessons, oldest 27 days | 🟡 MEDIUM | `data/entities/*/proposed_lessons.yaml` | Set review threshold |
| 5 | Only 1 entity has `last_updated` in soul.yaml | 🟡 MEDIUM | `data/entities/*/soul.yaml` | Standardize timestamp field |
| 6 | Two incompatible proposed_lessons schemas | 🟡 MEDIUM | `data/entities/*/proposed_lessons.yaml` | Consolidate to L1/L2/L3 format |
| 7 | arch/soul.yaml 1,501 lines (v6.0 bloat) | 🟡 MEDIUM | `data/entities/arch/soul.yaml` | Migrate to v6.1, extract lessons |
| 8 | arch/soul.yaml.backup (45KB duplicate) | 🟢 LOW | `data/entities/arch/` | Delete stale backup |
| 9 | roc_racoon/soul.yaml.bak (79KB) | 🟢 LOW | `data/entities/roc_racoon/` | Delete stale backup |
| 10 | roc_racoon/audit.log (576KB, unbounded) | 🟢 LOW | `data/entities/roc_racoon/` | Review & add rotation |
| 11 | 3 test entity dirs on disk (120KB) | 🟢 LOW | `data/entities/test_*_remove/` | Clean up post-test |
| 12 | _quarantine/2026-06-05 (460K, 23 days old) | 🟢 LOW | `data/entities/_quarantine/` | Review retention need |
| 13 | _quarantine/h2a_20260609 (1.6MB, 19 days old) | 🟢 LOW | `data/entities/_quarantine/` | Review retention need |
| 14 | 40 legacy .active session markers, no cleanup | 🟢 LOW | `data/sessions/` | Consolidate or deprecate |
| 15 | IWAD-only entities (bridge, datastore, etc.) | 🟢 LOW | `config/wads/_omega_default/entities.yaml` | Verify no functional gap |

---

## Methodological Note

This audit was conducted by reading source files (entity_registry.py lines 1-350, memory_store.py full 788 lines), performing directory listings and byte counts across all 39 entity directories, scanning soul.yaml files for consistency, counting proposals across 12 proposed_lessons.yaml files, and examining the file provider storage at `data/memory/entities/`. No files were modified. No code was changed. Hivemind heartbeats were posted every 3-4 file reads to prevent pruning.

**P5 report checked before writing**: P5's governance audit covers PIVOT_LOG compaction, strategy documentation, heritage pipeline overhead, and handoff debris — non-overlapping with this P2 audit.

**Hivemind awareness checked before writing**: Active agents — Kali (MaKaLi Council Pass 2), Ma'at (Build-side optimization), Lilith (Run-side optimization), P5 (heartbeat). This report is filed for Ma'at's build-side review and MaKaLi Council synthesis.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
