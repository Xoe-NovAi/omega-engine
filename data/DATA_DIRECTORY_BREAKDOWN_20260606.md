# 🔱 DATA/ DIRECTORY COMPLETE BREAKDOWN TABLE

**Generated**: 2026-06-06  
**Total**: 754M | 16,346 files  
**Audit Status**: ✅ COMPLETE

---

## DIRECTORY INVENTORY (All subdirectories in data/)

| # | Path | Size | Files | Status | What it stores | Cleanup Needed? | Work Package |
|---|------|------|-------|--------|---|---|---|
| 1 | **data/library/** | 451M | 14,561 | ⚠️ STALE | Document corpus (PDFs, text, software) | **Y** | CP-2 Migration |
| 2 | **data/entities/** | 156M | 549 | ✅ ACTIVE | Entity workspaces, soul.yaml, knowledge | **N** | CORE |
| 3 | **data/logs/** | 139M | 3 | 🗑️ DEAD | System capture syscap files (2026-05-29) | **Y** | CP-6 Hygiene |
| 4 | **data/datasets/** | 4.1M | 735 | ⚠️ STALE | Synthetic training data | **M** | CP-7 Training |
| 5 | **data/handoff/** | 992K | 68 | ✅ ACTIVE | Sprint handoffs, decision logs, reports | **M** | CP-3 Docs |
| 6 | **data/kb/** | 960K | 47 | ✅ ACTIVE | Knowledge base staging area | **M** | CP-2 Migration |
| 7 | **data/coordination/** | 800K | 105 | ✅ ACTIVE | Hivemind ACKs, live feeds, workspace locks | **N** | CORE |
| 8 | **data/knowledge/** | 712K | 131 | ✅ ACTIVE | HALL_OF_RECORDS session history | **N** | CP-5 Session |
| 9 | **data/research/** | 296K | 35 | ⚠️ STALE | Checkpoints, metrics, mining logs | **M** | CP-8 Research |
| 10 | **data/workbench/** | 280K | 2 | ✅ ACTIVE | SQLite DB (workbench.db + .bak) | **N** | CORE |
| 11 | **data/memory/** | 264K | 73 | ✅ ACTIVE | Memory store snapshots, entities, traces | **N** | CORE |
| 12 | **data/sessions/** | 108K | 26 | ✅ ACTIVE | Entity .active session files (26 entities) | **M** | CP-5 Session |
| 13 | **data/team/** | 60K | 2 | ⚠️ STALE | Team documents | **M** | CP-3 Docs |
| 14 | **data/searxng/** | 24K | 4 | 🟢 MINIMAL | Search configuration | **N** | Infrastructure |
| 15 | **data/requests/** | 20K | 1 | 🟢 MINIMAL | Request index (INDEX.json) | **N** | CORE |
| 16 | **data/jobs/** | 20K | 0 | 🟢 MINIMAL | Job state (empty) | **N** | CORE |
| 17 | **data/processed/** | 16K | 2 | 🟢 MINIMAL | Processed inbox items | **N** | CP-6 Hygiene |
| 18 | **data/inbox/** | 16K | 0 | 🟢 MINIMAL | Inbox queue (empty) | **N** | CP-6 Hygiene |
| 19 | **data/rejected/** | 8.0K | 0 | 🟢 MINIMAL | Rejected items (empty) | **N** | CP-6 Hygiene |
| 20 | **data/benchmarks/** | 8.0K | 1 | 🟢 MINIMAL | Benchmark results | **N** | CP-10 Performance |
| 21 | **data/audit/** | 8.0K | 0 | 🟢 MINIMAL | Audit logs (empty) | **N** | Infrastructure |
| 22 | **data/traces/** | 4.0K | 0 | 🟢 MINIMAL | Trace files (empty) | **N** | Infrastructure |
| 23 | **data/p2p/** | 4.0K | 0 | 🟢 MINIMAL | P2P state (empty) | **N** | Infrastructure |
| 24 | **data/mining_queue/** | 4.0K | 0 | 🟢 MINIMAL | Mining queue (empty) | **N** | CP-1 Mining |

---

## ENTITY WORKSPACES BREAKDOWN (data/entities/ = 156M, 549 files)

### Real Entities (KEEP) — 96 entities, ~154M

| Rank | Entity | Size | Files | Lessons | Type | Status |
|------|--------|------|-------|---------|------|--------|
| 1 | **roc_racoon** | 149M | 71 | 145 | Miner | 🔴 BLOATED (audit.log=518K) |
| 2 | **maat** | 1.6M | 5 | 38 | Oversoul | ✅ ACTIVE |
| 3 | **doom_guy** | 792K | 15 | 0 | Architect | ✅ ACTIVE |
| 4 | **sophia** | 316K | 3 | 1 | Oversoul | ✅ ACTIVE |
| 5 | **researcher** | 252K | 24 | 15 | JEM | ✅ ACTIVE |
| 6 | **kali** | 116K | 3 | 13 | Counsel | ✅ ACTIVE |
| 7 | **arch** | 100K | 2 | 183 | Knowledge | ✅ EXCELLENT |
| 8 | **lilith** | 92K | 6 | 8 | Oversoul | ✅ ACTIVE |
| 9 | **p10** | 92K | 2 | 1 | Pillar | ✅ ACTIVE |
| 10 | **p2** | 60K | 2 | 15 | Pillar | ✅ ACTIVE |
| 11 | **p8** | 60K | 2 | 1 | Pillar | ✅ ACTIVE |
| 12 | **p1** | 56K | 2 | 7 | Pillar | ✅ ACTIVE |
| 13 | **p6** | 56K | 2 | 3 | Pillar | ✅ ACTIVE |
| 14 | **context** | 76K | 6 | 20 | Knowledge | ✅ ACTIVE |
| 15 | **p9** | 72K | 2 | 1 | Pillar | ✅ ACTIVE |
| ... | (81 more real entities) | ... | ... | ... | ... | ✅ |

### Orphan Entities (DELETE) — 50 entities, 1.8M

| Category | Count | Size | Status | Action |
|----------|-------|------|--------|--------|
| **ent_0..ent_49** | 50 | 1.8M | 🗑️ DEAD | **DELETE immediately (H2-A1)** |
| Test scaffold: flatentity, myentity, preexisting, duplicate, etc. | ~12 | ~100K | 🗑️ DEAD | DELETE after INDEX audit |

### Archive & Quarantine — 190 items, 1.7M

| Path | Count | Size | Status | Action |
|------|-------|------|--------|--------|
| **data/entities/_archive/** | 150 | 1.2M | 🟡 STALE | Review, move to cold storage |
| **data/entities/_quarantine/** | 40 | 488K | ⚠️ STALE | Review, rehabilitate or delete |

**Total entity bloat**: 1.8M + 488K = 2.3M (immediate cleanup target)

---

## CRITICAL FINDINGS

### Finding 1: Orphan Entity Bloat (1.8M)
- **Issue**: 50 test scaffold entities (ent_0..ent_49) consuming 1.8M
- **Impact**: 🔴 HIGH — Pollutes entity list, no value
- **Action**: DELETE immediately (H2-A1, 15 min)
- **Freed**: 1.8M

### Finding 2: Dead Logs (139M)
- **Issue**: System capture files from 2026-05-29 (14M + 125M)
- **Impact**: 🔴 HIGH — Dead weight, no code references
- **Action**: DELETE or archive to /media (H2-A4, 15 min)
- **Freed**: 139M

### Finding 3: Library Unmigrated (451M)
- **Issue**: Document corpus should move to data/kb/_curated/ (does not exist!)
- **Impact**: 🟡 MED — KB migration blocked
- **Action**: Create data/kb/_curated/, plan CP-2 (1 hr planning)
- **Freed**: 451M (pending)

### Finding 4: Soul Integrity Gap (Mandate 11)
- **Issue**: Only 25 of 158 entities populate lessons (16% adoption)
- **Impact**: ⚠️ LOW — Mandate 11 (Soul Integrity) not adopted
- **Action**: Populate jem_discovery/synthesis/verification in next sprint
- **JEM entities status**: 0 lessons (should have 50+)

### Finding 5: Data/kb/_curated/ Missing
- **Issue**: Migration target directory does not exist
- **Impact**: 🟡 MED — Cannot proceed with library migration
- **Action**: Create directory + establish pipeline
- **Timeline**: CP-2 (WEEK 1)

---

## SOUL.YAML COMPLETENESS (Mandate 11 Tracking)

### Coverage: 158/158 (100%)
✅ Every entity has a soul.yaml file

### Lessons Adoption: 25/158 (16%)
⚠️ Only 25 entities have non-empty lessons arrays

### Top Distillers
| Entity | Lessons | Category |
|--------|---------|----------|
| **arch** | 183 | Architecture knowledge |
| **roc_racoon** | 145 | Mining experience |
| **datastore** | 120 | Memory insights |
| **maat** | 38 | Synthesis knowledge |
| **saraswati** | 23 | Knowledge/speech |
| **context** | 20 | Context entity |
| **antigravity** | 18 | Experimental |
| **researcher** | 15 | Research meta |
| **p2** | 15 | Persistence pillar |
| **kali** | 13 | Counsel entity |

**Total lessons**: 262 entries (good start, but 84% of entities have zero entries)

---

## CLEANUP ROADMAP

### Phase H2-A: Data Hygiene (Shortest Path to GREEN)

| Task | Target | Size | Effort | Frees | Priority |
|------|--------|------|--------|-------|----------|
| **H2-A1** | Delete ent_0..ent_49 | 1.8M | 15 min | 1.8M | 🔴 P0 |
| **H2-A2** | Create entity INDEX.yaml | — | 30 min | — | 🟡 P1 |
| **H2-A3** | Delete stale HALL_OF_RECORDS (>7d) | ~50K | 15 min | 50K | 🟢 P3 |
| **H2-A4** | Archive/delete logs | 139M | 15 min | 139M | 🔴 P0 |
| **H2-A5** | Eradicate rag-v1/ | — | 5 min | — | 🟢 P3 |
| **H2-A6** | Delete .coverage + gitignore | 69K | 5 min | 69K | 🟢 P3 |
| **H2-A7** | Delete opencode.json.bak | 1K | 1 min | 1K | 🟢 P3 |
| **H2-A8** | Archive old handoffs (>3d) | ~100K | 15 min | 100K | 🟡 P2 |
| **H2-A9** | Plan KB migration (CP-2) | 451M | 1 hr | 451M (pending) | 🔴 P0 |

**Quick wins (P0, 30 min total)**: H2-A1 + H2-A4 → **141M freed**
**Full cleanup (including P2/P3)**: ~593M (library decision pending)

---

## ENTITY HEALTH AUDIT

### Categories

| Category | Members | Count | Size | Status |
|----------|---------|-------|------|--------|
| 10 Pillar Keepers | Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali | 10 | ~240K | ✅ ACTIVE |
| 4 Oversouls | Sophia, Maat, Lilith, Iris | 4 | ~1.5M | ✅ ACTIVE |
| JEM Pipeline | Jem, Jem_discovery, Jem_synthesis, Jem_verification | 4 | ~104K | ⚠️ NEEDS LESSONS |
| Pillar Slots | P1, P2, P3, P4, P5, P6, P7, P8, P9, P10 | 10 | ~520K | ✅ ACTIVE |
| Agents & Admins | Quality, Scribe, Researcher, Sentinel, Link, Doom_guy, Roc_racoon | 7 | ~1.3M | ✅ ACTIVE |
| Domain Knowledge | Arch, Context, Datastore, etc. | ~50 | ~700K | ✅ ACTIVE |
| **ORPHAN BLOAT** | **ent_0..ent_49, test scaffolds** | **~60** | **~2.3M** | **🗑️ DELETE** |

---

## WORK PACKAGES (PRIORITY ORDER)

| CP | Phase | Task | Size | Effort | Timeline | Frees |
|----|-------|------|------|--------|----------|-------|
| H2-A1 | P0 | Delete orphan entities (ent_0..ent_49) | 1.8M | 15 min | **NOW** | 1.8M |
| H2-A4 | P0 | Archive/delete 139M logs | 139M | 15 min | **NOW** | 139M |
| H2-A2 | P1 | Create entity INDEX.yaml + audit | — | 30 min | **TODAY** | — |
| H2-A8 | P2 | Archive old handoffs | 100K | 15 min | **TODAY** | 100K |
| CP-2 | P1 | KB migration plan (library→kb/_curated/) | 451M | 1 hr | **WEEK 1** | 451M (pending) |
| CP-5 | P2 | Session chainlit map (_chainlit_map.json) | — | 30 min | **WEEK 1** | — |
| CP-6 | P2 | Quarantine review + hygiene | 488K | 1 hr | **WEEK 1** | 488K |

---

## FINAL STATS

| Metric | Value | Status |
|--------|-------|--------|
| **Total data/ size** | 754M | 🔴 HIGH |
| **Immediate cleanup** | 141M (H2-A1 + H2-A4) | 🟡 MEDIUM |
| **Planned cleanup** | 451M+ (CP-2 pending) | 🟡 MEDIUM |
| **Entity souls** | 158 (100%) | ✅ COMPLETE |
| **Real entities** | 96 | ✅ ACTIVE |
| **Orphan entities** | 50 | 🗑️ DELETE |
| **Soul lessons** | 262 total | ⚠️ 16% adoption |
| **Files >30 days** | 14,536 (89%) | ⚠️ ARCHIVE |

---

*⬡ OMEGA ⬡ Data/ Audit Complete | 2026-06-06*
