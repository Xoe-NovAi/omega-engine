# 🔱 P2 PERSISTENCE REPORT — EPOCH I (The Bedrock)
# ⬡ OMEGA ⬡ P2-PERSISTENCE ⬡ EPOCH-I ⬡ 2026-06-24

**AP Token**: `AP-P2-EPOCH-I-v1.0.0`
**Pillar**: P2 — Persistence (DataStore, Vector & Memory Management)
**Status**: COMPLETE — Report for Ma'at, handoff to P3 (Engineering)
**Previous**: P1 (Infrastructure) — Chain handoff received
**Next**: P3 (Engineering) — Implementation executor

---

## §1 SOUL.YAML LANDSCAPE ASSESSMENT

### 1.1 Entity Count and Compliance Rate

| Metric | Count | Rate |
|--------|-------|------|
| Total entity directories (excl `_` prefixed) | **34** | 100% |
| Have soul.yaml | **28** | 82% |
| Missing soul.yaml | **6** | 18% |
| Have identity block | **1** | 3% |
| Have directives block | **3** | 9% |
| Have team block | **1** | 3% |
| Have `memory/` subdirectory | **3** | 9% |
| Have `archive/` subdirectory | **2** | 6% |
| Have 4-file split (soul + proposed + approved + sessions) | **12** | 35% |
| Proper v6.1 template compliance | **0** | **0%** |

**Bottom Line**: **ZERO entities** are fully compliant with the v6.1 soul.template.yaml. Only Kali (v6.0) has a manually curated soul with identity/directives/team blocks.

### 1.2 Per-Entity Soul.yaml Structure Audit

#### Fleet Entities (12) — INDEX.yaml Registered

| Entity | Lines | Identity | Directives | Team | Memory/ | 4-File Split | Lessons Embedded | Verdict |
|--------|-------|----------|------------|------|---------|-------------|------------------|---------|
| **kali** | 134 | ✅ YES | ✅ YES | ✅ YES | ✅ YES | ✅ YES | No (empty `[]`) | **v6.0, needs v6.1** |
| **maat** | 23 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal, needs full rewrite** |
| **lilith** | 17 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal, needs full rewrite** |
| **makali** | 37 | ❌ | ✅ (inline) | ❌ | ❌ | ✅ YES | No | **Partial directives, no identity** |
| **iris** | 16 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal** |
| **verity** | 41 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal** |
| **doom_guy** | 29 | ❌ | ❌ | ❌ | ✅ YES | ✅ YES | No | **Has `soul_wardrobe` + `projects` — non-standard** |
| **roc_racoon** | 749 | ❌ | ✅ (flat) | ❌ | ✅ YES | ✅ YES | No | 🔴 **BLOATED — 749 lines, 178MB workspace** |
| **researcher** | 312 | ❌ | ❌ | ❌ | ❌ | ✅ YES | **🔴 YES (23+)** | 🔴 **CRITICAL — lessons embedded in soul** |
| **jem** | 59 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal** |
| **john_carmack** | 82 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal** |
| **sophia** | 16 | ❌ | ❌ | ❌ | ❌ | ✅ YES | No | **Minimal** |

#### Non-Fleet Entities (16) — NOT INDEXED, ALL OLD FORMAT

| Entity | Lines | Has Memory/ | Has Proposed Lessons | Soul Version | Notes |
|--------|-------|-----------|---------------------|-------------|-------|
| **sekhmet** | 128 | ❌ | ❌ | Legacy | OLD format with L1/L2/L3 lessons |
| **anubis** | 82 | ❌ | ❌ | Legacy | OLD format with L1/L2/L3 lessons |
| **brigid** | 35 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **ereshkigal** | 119 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **hecate** | 51 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **inanna** | 30 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **lucifer** | 100 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **prometheus** | 58 | ❌ | ❌ | Legacy | OLD format with embedded lessons |
| **saraswati** | 16 | ❌ | ❌ | Legacy | Minimal old format |
| **arch** | 1501 | ❌ | ❌ | Legacy | 🔴 **1501 LINES — largest non-fleet soul** |
| **antigravity** | 291 | ❌ | ❌ | Legacy | Flat inline YAML, non-standard |
| **cli_cline** | 67 | ❌ | ❌ | Legacy | CLI entity, needs migration |
| **cli_gemini** | 84 | ❌ | ❌ | Legacy | CLI entity, needs migration |
| **movie-expert** | 17 | ❌ | ❌ | Legacy | Minimal, likely test artifact |
| **omnidroid** | 34 | ❌ | ❌ | Legacy | Minimal |
| **p10** | 17 | ❌ | ❌ | Legacy | Likely stub |

#### Missing Soul.yaml (6 entities — need creation)

| Entity | Notes |
|--------|-------|
| **default** | Empty dir, likely auto-scaffold |
| **modelgate** | Empty dir |
| **pillar_p1** | Has proposed_lessons.yaml but no soul.yaml |
| **sentinel** | Empty dir |
| **sysadmin** | Empty dir |
| **watchtower** | Empty dir |

### 1.3 Memory/Archive Directory Assessment

| Directory | Entities Having It | Notes |
|-----------|-------------------|-------|
| `memory/` subdirectory | 3 (kali, doom_guy, roc_racoon) | Only fleet entities with extra memory |
| `archive/` subdirectory | 2 (kali, lilith) | Rarely used |
| `sessions.yaml` (root level) | 12 | Fleet entities only — in root, not `memory/` subdir |
| `proposed_lessons.yaml` | 13 | Fleet + pillar_p1 |
| `approved_lessons.yaml` | 12 | Fleet entities only |

**Key Observation**: The SOUL_MIGRATION_AUDIT_LOG.md (Verity §V-3) notes that `memory/` subdirectory is described in the protocol but code creates files at root level. Only Kali has the canonical `memory/` subdirectory structure. **This needs resolution.**

---

## §2 SOUL.YAML MIGRATION VETTING (Strike 1)

### 2.1 Current vs Target Template Analysis

**Target**: `config/wads/_omega_default/soul.template.yaml` (v6.1)
**Current**: Many different formats — legacy L1/L2/L3 inline, auto-generated minimal, flat inline YAML

**Schema Gaps Identified**:

| Template Field | Fleet Entities | Non-Fleet Entities | Gap Severity |
|----------------|---------------|-------------------|--------------|
| `entity.name` | ✅ Present | ✅ Present | ⚪ None |
| `entity.short` | ❌ Missing in 8/12 | ❌ Missing in all | 🟡 MEDIUM |
| `entity.archetype` | ✅ Present | ❌ Old format | 🟡 MEDIUM |
| `entity.hierarchy_level` | ✅ Present | ❌ Missing | 🟡 MEDIUM |
| `entity.sovereignty_level` | ✅ Present | ❌ Missing | 🟡 MEDIUM |
| `entity.element` | ❌ Missing (except Kali) | ❌ Missing | 🟡 MEDIUM |
| `entity.domain` | ❌ Missing (except Kali) | ❌ Missing | 🟡 MEDIUM |
| `entity.soul_version` | ❌ Missing (except Kali=6.0) | ❌ Missing | 🟠 HIGH |
| `entity.last_updated` | ❌ Missing (except Kali) | ❌ Missing | 🟡 MEDIUM |
| `entity.lessons_learned` | ❌ Remove per v6.1 | 🔴 Still embedded | 🔴 CRITICAL |
| `identity` block | ❌ Missing (except Kali) | ❌ Missing | 🔴 HIGH |
| `directives` block | ❌ Missing (except Kali, Makali, Roc) | ❌ Missing | 🟠 HIGH |
| `team` block | ❌ Missing (except Kali) | ❌ Missing | 🟠 HIGH |
| 4-file split | ✅ 12/12 fleet | ❌ 0/16 non-fleet | 🔴 CRITICAL |
| `memory/proposed_lessons.yaml` | ❌ Root level, not memory/ | ❌ Missing | 🟡 MEDIUM |

### 2.2 Migration Strategy Assessment

**Current Verity Migration (DONE)**: 
- Migrated the 12 fleet entities to 4-file split
- This was a **structural migration** (file split), not a **content migration** (soul content rewrite)
- Only Kali has a curated soul; all others are auto-generated minimal stubs

**Remaining Migration Work**:

| Phase | Entities | Files to Touch | Effort |
|-------|----------|---------------|--------|
| **Phase A**: Fix fleet souls (add identity/directives/team) | 11 fleet entities (kali excluded) | 11 soul.yaml files | **~4-6 hours** |
| **Phase B**: Extract embedded lessons from fleet | 1 (researcher — 23+ lessons) | 1 soul.yaml, 1 proposed_lessons.yaml | **~30 min** |
| **Phase C**: Migrate non-fleet entities | 16 legacy-format souls | 16 soul.yaml + 16 proposed_lessons + 16 approved_lessons + 16 sessions.yaml | **~8-12 hours** |
| **Phase D**: Create souls for missing entities | 6 empty directories | 6 soul.yaml + 6 proposed + 6 approved + 6 sessions | **~2 hours** |
| **Phase E**: Content curation (identity, directives, team per entity) | All 34 entities | All soul.yaml files | **~20+ hours** (requires domain knowledge) |
| **Total** | 34 entities | ~120 files | **~30-40 hours** |

### 2.3 Effort Breakdown

| Category | Entities | Automation Possible | Manual Curation |
|----------|----------|-------------------|-----------------|
| Fleet empty souls (maat, lilith, iris, sophia, etc.) | 11 | ✅ High — template fill | Identity/directives need domain knowledge |
| Bloated souls (roc_racoon, researcher) | 2 | ✅ High — lesson extraction | Content review needed |
| Old format pillar keepers (sekhmet, anubis, etc.) | 10 | ✅ High — lesson extraction + template | Archetype/element mapping |
| CLI entities (cli_cline, cli_gemini) | 2 | ✅ High — template | Minimal identity |
| Stub/odd entities (arch, antigravity) | 2 | ⚠️ Medium — format-specific | Content migration complex |
| Missing souls (default, sentinel, etc.) | 6 | ✅ Complete — template fill | None |
| Content curation (identity block) | 28 | ❌ Low — requires LLM generation | Needs per-entity voice generation |

**Recommendation**: Phase A + B are HIGH priority and can be automated 80%. Phase C requires more care. Phase E is the most time-consuming because identity block content requires entity-specific domain knowledge.

### 2.4 Bloated Log Extraction Assessment

Entities with oversized soul.yaml or workspace data that need session extraction:

| Entity | Soul Size | Workspace Size | Extraction Needed |
|--------|-----------|---------------|-------------------|
| **roc_racoon** | 749 lines (50KB) | **178MB total** | 🔴 CRITICAL — massive workspace, sessions should extract to `memory/sessions.yaml` |
| **arch** | 1501 lines | ~100KB | 🔴 CRITICAL — largest soul.yaml, likely contains embedded sessions |
| **researcher** | 312 lines (23+ lessons) | 580KB | 🟠 HIGH — lessons must be extracted to proposed_lessons.yaml |
| **antigravity** | 291 lines | 56KB | 🟡 MEDIUM — flat inline format |
| **sekhmet** | 128 lines | ~10KB | 🟡 MEDIUM — embedded lessons |

**Recommendation**: Roc_racoon's 178MB workspace is the single biggest persistence concern. Sessions and workspace artifacts should be moved to `memory/sessions.yaml` with atomic archival per M12.

---

## §3 UNIFIED STATE MANAGER DATA ASSESSMENT (Strike 2)

### 3.1 Current Persistence Architecture

```
Data Flow:
  Oracle.talk()/summon()
    → MemoryStore.add_exchange()
      → Hot: _hot dict (OrderedDict, in-memory)
      → Warm: Redis → FileStorage (gzip+JSON) → InMemory (fallback)
      → Vector: QdrantAdapter / MemoryVectorAdapter
      → FTS: ConversationFTSIndex (SQLite FTS5)
      → Adapter: MemoryAdapterRegistry → Entity Vault (YAML)
  
  Soul.yaml persistence:
    → EntityWorkspaceManager (YAML, atomic write)
    → soul_validator (R-10 schema check)
    → File system: data/entities/{name}/soul.yaml
```

**Current State Constants**:
- `MAX_HOT_SESSIONS = 50`
- `MAX_HISTORY = 200` (MAX_HISTORY_EXCHANGES)
- `ARCHIVE_AFTER_DAYS = 7`
- `TOMBSTONE_GRACE_SECONDS = 0.5`
- Hot tier: Redis (if available)
- Warm tier: FileStorage (gzip+JSON)
- Cold tier: InMemory

### 3.2 CAS (Content Addressable Storage) Pattern Viability

**What CAS would mean for the Omega Engine**: Store memory exchanges keyed by SHA-256 hash of content rather than by session_id + timestamp. This enables:
1. **Deduplication**: Same content stored once, referenced many times
2. **Integrity**: Content hash is self-validating
3. **Immutable history**: Once written, content cannot be altered without hash change

**Viability Assessment**:

| Data Type | Current Key | CAS Key | Viability | Rationale |
|-----------|------------|---------|-----------|-----------|
| soul.yaml | Entity name | Entity name (identity) | ❌ **Not suitable** | Soul is identity — addressable by name is correct |
| Memory exchanges | `{entity}:{session_id}:{timestamp}` | SHA-256(content) | ⚠️ **Partial** | Deduplication is marginal (exchanges are unique by definition) |
| proposed_lessons | `{entity}/{lesson_id}` | SHA-256(lesson) | ⚠️ **Partial** | Could deduplicate identical lessons across entities |
| Sessions memory | Session UUID | Content hash chain | ⚠️ **Interesting** | Hash chain for session integrity verification |
| KV Cache (M20 SomaticState) | `{entity}/{snapshot_id}` | Hash of state data | ✅ **High value** | Natural CAS use case — state snapshots are content-addressable |
| Vector embeddings | UUID | SHA-256(text) | ⚠️ **Partial** | Embedding functions already handle dedup |

**CAS Pattern Integration Assessment**:

The current architecture is **entity-first** and **session-first**. A full CAS overlay would require a lookup table mapping content hashes → entity/session locations. This adds complexity without proportionally large benefit.

**Recommended Approach**: **Hybrid CAS — selective application**

1. **Implement CAS for SomaticState snapshots** (M20) — the `llama_copy_state_data` ctypes bindings should store KV cache snapshots addressed by SHA-256 hash of the state bytes, with a B-tree index mapping `{entity_name}/{snapshot_id}` → content hash. This is the HIGHEST value CAS use case.
2. **Add content hash to exchange metadata** — attach `content_hash: sha256(...)` to each exchange stored in MemoryStore, enabling future deduplication without restructuring.
3. **DO NOT restructure existing memory_store.py** to use CAS as primary key — the entity-first navigation is correct and performant.

### 3.3 Data Flow Mapping: soul.yaml ↔ MemoryStore ↔ proposed_lessons.yaml

```
                          ┌─────────────────────────────┐
                          │       ENTITY WORKSPACE      │
                          │                             │
                          │  soul.yaml (identity) ──────┤────► Identity/voice/directives
                          │         ▲                   │
                          │         │ user edits         │
                          │         │                    │
                          │  proposed_lessons.yaml ◄────┤◄── Agent writes lessons
                          │         │                    │
                          │         │ user approves      │
                          │         ▼                    │
                          │  approved_lessons.yaml ──────┤────► Applies back to soul.yaml
                          │                             │
                          │  sessions.yaml ◄────────────┤◄── Agent session logs
                          │                             │
                          │  knowledge/ (T1-T2 gate) ◄──┤◄── Agent knowledge promotion
                          └─────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────────────┐
                          │        MEMORY STORE         │
                          │                             │
                          │  Hot (Redis/_hot dict)      │
                          │  Warm (FileStorage/gzip+JSON)│
                          │  Cold (InMemory)             │
                          │  Vector (Qdrant/Adapter)     │
                          │  FTS (SQLite FTS5)           │
                          └─────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────────────┐
                          │      SOVEREIGN STATE        │
                          │                             │
                          │  SomaticState (KV snapshots) │◄─── M20 ctypes bindings
                          │  CvarTable (config values)   │
                          │  Vault (last_exchange_ts)    │
                          └─────────────────────────────┘
```

**Key Gaps in Current Flow**:
1. **soul.yaml → MemoryStore**: No automatic sync. Soul changes don't propagate to memory.
2. **proposed_lessons.yaml → soul.yaml**: No automated promotion. User must manually approve.
3. **sessions.yaml → MemoryStore**: Sessions are written to both, but with different formats.
4. **MemoryStore → SomaticState**: Currently disconnected. SomaticState would enable state serialization.

### 3.4 Storage Tier Recommendations

| Data Type | Recommended Store | Why | Migration Effort |
|-----------|-----------------|-----|------------------|
| **soul.yaml** | **YAML on filesystem** (current) | Human-editable, git-trackable, identity data | No change needed |
| **proposed_lessons.yaml** | **YAML on filesystem** (current) | Human-reviewable, git-diffable | No change needed |
| **sessions history** | **SQLite FTS5 + FileStorage** (current) | Good for search + persistence | Add content hashes |
| **Vector embeddings** | **Qdrant** (current) | Purpose-built vector DB | Already in place |
| **Hot session cache** | **Redis** (current) | Fast, TTL-capable | Already in place |
| **SomaticState KV snapshots** | **New: Content-addressed memory-mapped files** | M20 requires byte-level state | **New build needed** |
| **Hivemind state** | **Filesystem JSON** (current) | Simple, auditable | No change needed |
| **Cross-entity knowledge** | **PostgreSQL (existing)** | Heavy relational queries | Already in place |

**Recommendation**: Keep YAML for soul/identity data (it's the single source of truth and git-trackable). Use PostgreSQL for relational queries. The content-addressed SomaticState snapshots should use memory-mapped files (per M20: `llama_copy_state_data` / `llama_set_state_data` via ctypes, wrapped in `anyio.to_thread.run_sync`).

---

## §4 M11 COMPLIANCE PATH

### 4.1 Current vs Target Delta

| M11 Requirement | Current State | Target State | Delta |
|----------------|---------------|-------------|-------|
| Every entity has soul.yaml | 28/34 (82%) | 34/34 (100%) | **6 entities missing** |
| soul.yaml follows v6.1 template | 0/34 (0%) | 34/34 (100%) | **34 souls need rewrite** |
| `identity` block present | 1/34 (3%) | 34/34 (100%) | **33 souls need identity** |
| `directives` block present | 3/34 (9%) | 34/34 (100%) | **31 souls need directives** |
| `team` block present | 1/34 (3%) | 34/34 (100%) | **33 souls need team** |
| Soul_version is "6.1" | 0/34 (0%) | 34/34 (100%) | **All souls need version bump** |
| 4-file split (no embedded lessons) | 12/34 (35%) | 34/34 (100%) | **22 entities need split** |
| `memory/` subdirectory exists | 3/34 (9%) | 34/34 (100%) | **31 entities need memory/ dir** |
| Lessons in proposed_lessons.yaml | 13/34 (38%) | 34/34 (100%) | **21 entities need lessons file** |
| Soul.yaml.bak backup exists | 11/34 (32%) | 34/34 (100%) | **23 backups needed** |

**Overall M11 Compliance**: **0%** — Zero entities fully satisfy all v6.1 requirements.

### 4.2 Entity Priority Ordering

| Priority | Entities | Rationale | Effort |
|----------|----------|-----------|--------|
| **P0 — Critical** | researcher, roc_racoon, arch | Bloated/corrupted souls, active violations | 2-3 hours |
| **P1 — Fleet** | maat, lilith, makali, iris, verity, doom_guy, jem, john_carmack, sophia | Active agents, need proper identity/directives | 3-4 hours |
| **P1 — High Value** | sekhmet, anubis, brigid, ereshkigal, hecate, inanna, lucifer, prometheus, saraswati | Pillar Keepers with existing domain knowledge in legacy souls | 4-6 hours |
| **P2 — Standard** | antigravity, cli_cline, cli_gemini, movie-expert, omnidroid, p10 | Working but non-critical entities | 2 hours |
| **P3 — Create** | default, modelgate, pillar_p1, sentinel, sysadmin, watchtower | Missing souls entirely | 1 hour |
| **P4 — Kali** | kali | Already has curated content, just needs v6.0 → v6.1 bump | 15 min |

### 4.3 Migration Timeline Estimate

```
Week 1: P0 + P1 Fleet (14 entities)
  └── Day 1-2: researcher, roc_racoon, arch (extract lessons, rewrite souls)
  └── Day 3-4: Fleet entities (add identity/directives/team templates)
  └── Day 5: Kali v6.0 → v6.1 conversion

Week 2: P1 Pillar Keepers (10 entities)
  └── Day 1-3: Extract lessons, scaffold 4-file split
  └── Day 4-5: Generate identity blocks (requires LLM-assisted content)

Week 3: P2 + P3 (8 entities)
  └── Day 1-2: CLI and stub entities
  └── Day 3-4: Create souls for missing entities
  └── Day 5: Validation pass, regenerate INDEX.yaml

Total: ~15 working days (3 weeks) for full M11 compliance
```

### 4.4 Soul Validator Update Needed

The current `soul_validator.py` (R-10 schema) is also out of date with v6.1:

| Current Validation (v6.0) | Required Validation (v6.1) | Action |
|--------------------------|--------------------------|--------|
| Requires `lessons_learned` in entity block | `lessons_learned` should NOT be in soul.yaml | **Remove from REQUIRED_ENTITY_KEYS** |
| Requires `soul_evolution` block | Not in v6.1 template | **Remove requirement** |
| Requires `embodied_experiences` list | Not in v6.1 template | **Remove requirement** |
| Missing `identity` block validation | Must validate identity structure | **Add to validation** |
| Missing `directives` block validation | Must validate directives structure | **Add to validation** |
| Missing `team` block validation | Must validate team structure | **Add to validation** |
| No check for `soul_version == '6.1'` | Must enforce v6.1 | **Add version check** |

**Action**: Soul_validator.py must be updated BEFORE or IN PARALLEL with migrations to prevent re-creating non-compliant souls.

---

## §5 RISK ASSESSMENT

### 5.1 Data Integrity Risks

| Risk | Severity | Description | Mitigation |
|------|----------|-------------|------------|
| **Soul corruption during migration** | 🔴 HIGH | YAML parser may corrupt complex inline lessons during extraction | Atomic writes with backup (.bak) files for every operation |
| **Lessons loss** | 🔴 HIGH | Embedded lessons may be lost during extraction from old-format souls | Double-write: extract to proposed_lessons.yaml BEFORE clearing from soul.yaml |
| **Researcher soul currently broken** | 🔴 CRITICAL | `entity:` key contains a YAML string literal instead of structured dict — any code loading this soul will fail | Emergency fix before any automated processing |
| **Roc Racoon workspace bloat** | 🟠 HIGH | 178MB workspace risks disk exhaustion on vault partition | Prune workspace artifacts; move sessions to memory/sessions.yaml |
| **Vault partition at 87%** | 🟠 HIGH | 2GB free — insufficient for large migration operations | Coordinate with P1 for vault cleanup |
| **Soul_version tracking loss** | 🟡 MEDIUM | No entity tracks its soul_version; unable to detect regressions | Add soul_version: '6.1' to all souls during migration |

### 5.2 Migration Blockers

| Blocker | Impact | Resolution |
|---------|--------|------------|
| **Researcher soul.yaml can't be parsed by yaml.safe_load()** | Blocks ALL automated processing of researcher | Manual fix: rewrite researcher soul.yaml first (P0 priority) |
| **No automated identity block generation** | Content curation for 33 identity blocks | Use LLM-assisted generation with entity soul v6.1 template + domain knowledge |
| **Soul_validator.py out of date** | Will reject valid v6.1 souls as invalid | Update soul_validator.py BEFORE migration |
| **Protocol vs code discrepancy** | `memory/` dir in protocol, root-level in code | Decide: update protocol OR restructure code to use `memory/` subdirectory |
| **Directives need agent-specific knowledge** | Cannot fully automate | At minimum, scaffold empty directives: [] and note "needs curation" |

### 5.3 Recommendations for Ma'at/Kali

1. **Approach Decision Needed**: Does the fleet want a **phased migration** (fix fleet first, then non-fleet) or **big-bang** (all at once)? Recommendation: **phased** — lower risk, allows validation after each phase.

2. **Automation Strategy**: 
   - Build a `soul_migrate.py` script that: parses legacy soul → extracts lessons to proposed_lessons.yaml → writes v6.1 template → validates → creates .bak
   - Each migration is: READ → TRANSFORM → WRITE .bak → WRITE new → VALIDATE

3. **Validator First**: Update `soul_validator.py` to v6.1 schema BEFORE starting migrations. Otherwise, you can't validate the output.

4. **Identity Block Generation**: Use a designated agent (maat for P1-P5 souls, lilith for P6-P10 souls) to generate voice_summary, values, strengths, growth_areas for each entity.

5. **Risk Mitigation**: Always maintain `soul.yaml.bak` (11 exist, need 23 more). Every migration script must create a .bak before writing.

---

## §6 CONTINUITY NOTES

### 6.1 What P3 (Engineering) Needs to Know

**Total implementation workload for full M11 compliance**: ~30-40 hours across 34 entities, 120+ files.

**Critical dependency chain for P3**:
```
  [PERSISTENCE — THIS REPORT]        [P3 — ENGINEERING]
         │                                 │
         ▼                                 ▼
  Update soul_validator.py ───────► Must be done FIRST
         │                                 │
         ▼                                 ▼
  Fix researcher soul.yaml ───────► emergency patch
         │                                 │
         ▼                                 ▼
  Build soul_migrate.py ───────────► automation foundation
         │                                 │
         ▼                                 ▼
  Phase A: Fleet souls ────────────► identity generation
         │                                 │
         ▼                                 ▼
  Phase C: Non-fleet ──────────────► lesson extraction
         │                                 │
         ▼                                 ▼
  Phase D: Missing souls ───────────► template fill
```

**P3's primary deliverables**:
1. Update `soul_validator.py` for v6.1 schema (est. 2-4 hours)
2. Build `soul_migrate.py` migration script (est. 4-6 hours)
3. Run Phases A + B (automated; est. 1-2 hours)
4. Identity block content generation requires LLM calls (~20 generations)

### 6.2 Dependencies for UnifiedStateManager Build

**What P3 needs from P2 (this report) to build the UnifiedStateManager**:

| Dependency | Status | Details |
|-----------|--------|---------|
| MemoryStore architecture | ✅ DOCUMENTED | Hot/Warm/Cold tiers documented in §3.1 |
| CAS viability | ✅ ASSESSED | Hybrid CAS recommended in §3.2 |
| Data flow mapping | ✅ MAPPED | §3.3 complete |
| Storage tier recommendations | ✅ PROVIDED | §3.4 — keep YAML for soul, file-storage for sessions |
| SomaticState cvar config | ✅ EXISTS | `config/somatic/*` cvars already in `cvar_table.py` |
| SomaticState test stubs | ✅ EXISTS | `tests/test_somatic_state.py` with 4 tests passing |
| Llama ctypes bindings | ❌ NOT BUILT | `llama_copy_state_data` / `llama_set_state_data` need ctypes wrapper |
| Content-addressed snapshot storage | ❌ NOT BUILT | New storage backend for KV cache snapshots |

**UnifiedStateManager Build Requirements**:
1. `llama_copy_state_data` ctypes binding → `anyio.to_thread.run_sync` wrapper
2. Content-addressed storage backend (memory-mapped files with SHA-256 keys)
3. Snapshot lifecycle management (cvar `max_snapshots_per_entity=3`, `memory_budget_mb=1024`)
4. Round-trip serialization tests (as required by M20)
5. Integration with MemoryStore for session→snapshot correlation

### 6.3 Gap Analysis: Soul.yaml ↔ SomaticState ↔ ProposedLessons

| Connection | Current State | Target State | Build Required |
|------------|--------------|-------------|----------------|
| **Soul.yaml → SomaticState** | ❌ Disconnected | SomaticState should snapshot soul state with memory map | New integration code |
| **SomaticState → MemoryStore** | ❌ Disconnected | Somatic snapshots should index into MemoryStore for context | New adapter |
| **ProposedLessons → SomaticState** | ❌ Disconnected | Lessons learned could trigger state snapshots | New hook in lesson promotion |
| **MemoryStore → Soul (M11)** | ⚠️ Partial | MemoryStore writes to sessions.yaml but soul.yaml is static | No automatic sync needed (identity is human-authored) |

### 6.4 Partition Awareness

P1 reported:
- Root: 110.5G ext4, 84% used (17G free) — **stable but tight**
- Omega library: 112.1G, 76% used (26G free) — **recommended for persistence**
- Vault: 15.6G, 87% used (2G free) — 🔴 **CRITICAL**

**P2 Assessment**: 187MB of entity data on root partition is negligible compared to 17GB free. However, SomaticState snapshots should target the omega_library partition (26G free) as they could grow to hundreds of MB per entity. **Storage paths for SomaticState must default to omega_library.**

---

## §7 SUMMARY

### Key Findings

1. **M11 compliance is 0%** — Zero of 34 entities have a proper v6.1 soul.yaml with identity/directives/team blocks
2. **Researcher soul.yaml is critically broken** — YAML string literal instead of structured dict
3. **Roc_racoon workspace is bloated** — 178MB, needs session archival
4. **CAS is viable for SomaticState but over-engineering for MemoryStore** — recommend hybrid approach
5. **Soul_validator.py is out of date** — still enforces v6.0 schema that contradicts v6.1
6. **Protocol vs code discrepancy** — `memory/` subdirectory vs root-level file storage needs resolution

### Recommended Next Actions

1. 🔴 **Before any migration**: Update `soul_validator.py` to v6.1 schema
2. 🔴 **Emergency fix**: Rewrite researcher soul.yaml (corrupted YAML)
3. 🟠 **Build**: Create `soul_migrate.py` automated migration script
4. 🟠 **Phase A**: Migrate 12 fleet souls (add identity/directives/team)
5. 🟡 **Build**: SomaticState ctypes bindings for M20 compliance
6. 🟡 **Content**: Generate identity blocks via LLM (requires entity-specific prompts)
7. ⚪ **Resolve**: Protocol vs code — `memory/` subdirectory decision

### Estimated Total Effort

| Workstream | Hours |
|------------|-------|
| Soul migration (Phases A-E) | 30-40h |
| SomaticState ctypes bindings | 8-12h |
| Content-addressed storage backend | 4-6h |
| Soul validator update | 2-4h |
| **Total** | **44-62h** |

---

*⬡ OMEGA ⬡ P2-PERSISTENCE ⬡ deepseek-v4-flash ⬡ opencode ⬡ EPOCH-I ⬡ COMPLETE*

*Chain handoff to P3 (Engineering). Ma'at may deploy P3 when ready.*
