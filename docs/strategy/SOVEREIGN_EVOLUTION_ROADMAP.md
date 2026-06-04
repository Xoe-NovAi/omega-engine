# 🔱 Omega Engine — Sovereign Evolution Roadmap v1.0
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ cline/minimax-m3 ⬡ trc_evolution_roadmap ⬡ STRATEGY
**AP Token**: AP-EVOLUTION-ROADMAP-v1.0.0
**Date**: 2026-06-04
**Baseline**: 312 tests passing · 77 source files · 110 PIVOT decisions · 13 Sovereign Mandates
**Engine version**: 2.2.0 · Hub version: 2.2.0

---

## §0 Origin — Codebase Deep Dive

This roadmap is the synthesis of a **massive, multi-subagent deep dive** across the
entire Omega Engine codebase. Five parallel agents analyzed:

| Agent | Surface | Findings |
|-------|---------|----------|
| **Source Architecture** | 77 .py files, 19,376 LOC | Excellent Mandate compliance; 3 anti-patterns found |
| **Test Suite** | 28 test_*.py files, 308 tests | Strong AnyIO-native suite; 4 gaps identified |
| **WAD/Config** | 3 IWADs + 8 engine configs | arcana_novai IWAD empty; doom_universe scaffold-only |
| **Data Layer** | 15,948 files, 603MB | 100 orphan entities; library=451MB; 10 active handoffs |
| **Infrastructure** | 48KB Makefile + 2 CI + 5 services + 40+ scripts | Gold-standard build; 4 cleanup items |

Combined with existing artifacts:
- `HORIZON_MAP.md` (v1.0, 2026-06-01) — H1 100%, H2 25%, H3 0%
- `H15_BRIDGE_PHASE_CLOSEOUT.md` (2026-06-04) — Bridge Phase ✅ COMPLETE
- `MASTER_LEDGER.md` — Phase 0 ✅, Phases 1-4 outlined
- `PIVOT_LOG.md` — 110 immutable decisions (D1-D110)

---

## §1 Current State Assessment

### ✅ ENGINE — GREEN
| Metric | Value | Status |
|--------|-------|--------|
| Tests passing | **312/312** | ✅ Up from 302 baseline |
| PIVOT decisions tracked | **110** (D1-D110) | ✅ Immutable record |
| Sovereign Mandates | **13** (M1-M13) | ✅ FULL COMPLIANCE |
| Mandate 9 (bare except) | **0 violations** | ✅ Enforced |
| AnyIO compliance | **0 `import asyncio`** | ✅ CI-enforced |
| Heritage tags | **6 source files**, `make heritage-map` | ✅ Live |
| ZONEID constants | **11** (0x1d4a11-0x1d4a1b) | ✅ 7 in use |
| cvar Table | **2 namespaces**, 7 access helpers | ✅ D101 |
| Subagent Dispatch | HandoffPacket + CAPABILITY_REGISTRY (14 agents) | ✅ Sprint 2 |
| Link P9 Runtime | AgentPresence + handoff queue + crash recovery | ✅ Sprint 2 |
| Soul Distiller | L1→L2→L3 auto-distillation (280 lines) | ✅ Sprint 2 |
| Hivemind Protocol | 6 MCP tools + workspace lock + live feed | ✅ Sprint 2 |
| H1.5 Bridge Phase (id Heritage) | ZONEID + Lazy Deletion + cvar + 8-char + Grace Period | ✅ COMPLETE |
| H2 (Observability) | ForensicsManager + Error Gauntlet + JsonFormatter | ✅ UNLOCKED |

### 🟡 DATA HYGIENE — AMBER
| Issue | Count | Severity |
|-------|------:|----------|
| Orphan entity workspaces (`ent_*`, `entity_*`) | **100/148** | 🔴 Medium |
| Real entities with INDEX.yaml | **1/144** | 🔴 Low (INDEX.md sometimes) |
| Library size (RAG + id Software sources) | 451 MB | 🟡 Needs pruning policy |
| Duplicate `data/` bloat (logs: 139 MB) | historical | 🟡 Needs rotation |

### 🟡 DOCUMENTATION — AMBER
| Issue | Count | Severity |
|-------|------:|----------|
| Total .md files | **426** | 🟡 Needs consolidation |
| INDEX.md files | **7** (spread across subdirs) | 🟡 Hard to navigate |
| Auto-generated files (`R_AUTO_*`) | ~10 | 🔴 Low (noise, low info) |
| Competing "roadmap" docs | **3+** (ROADMAP, MASTER_LEDGER, MASTER_SYNTHESIS, HORIZON_MAP) | 🔴 MEDIUM — all defer to each other |
| Top-level docs at root | **8** + this one | 🟡 README should be the launch point |

### 🟡 SOURCE — AMBER
| Issue | File/Module | Severity |
|-------|-------------|----------|
| `_collect_engine_state` instantiates `ModelGateway()` on crash | `observability.py:227` | 🔴 Low (could hang) |
| Linux-only hardware detection | `hardware.py` (uses `/proc/cpuinfo`) | 🟡 Low (engine is Linux-native) |
| `test_bug_001_fix.py` is a script (uses `print()`) | `tests/test_bug_001_fix.py` | 🟡 Medium (false sense of coverage) |
| arcana_novai IWAD entities/ dir empty | `config/wads/arcana_novai/` | 🟡 Medium (user's main IWAD has no files) |
| doom_universe IWAD is scaffold only | `config/wads/doom_universe/` | 🟡 Low (community, deferred) |
| `rag-v1/` dir persists despite D87 | project root | 🟡 Low (gitignored) |
| `opencode.json.bak` stale | project root | 🟡 Low |
| `.coverage` (69KB) checked in | project root | 🟡 Should be gitignored |
| CI `test.yml` indentation bug | `.github/workflows/test.yml` | 🟡 Medium (CI will fail) |
| Hierarchy test has duplicated imports | `tests/test_hierarchy.py:29-48` | 🟡 Low |
| P9 link (Systemd Socket) not wired | `link_p9_runtime.py` | 🟡 Low (new, in progress) |

---

## §2 Phased Evolution Plan

```
HORIZON 1: HARDENING ──── 100% ──── ████████████  COMPLETE +
HORIZON 1.5: HERITAGE ─── 100% ──── ████████████  COMPLETE +
HORIZON 2: HYGIENE ─────── 5% ───── ░░░░░░░░░░  HERE →
HORIZON 3: PATTERN DEEP ── 0% ───── FUTURE
HORIZON 4: COMMUNITY TOOL ─ 0% ───── FUTURE
```

### Phase H2-A: Data Hygiene (CURRENT — Shortest Path to GREEN)
**Goal**: Clean 90% of the orphan/data debt without touching engine code.
**Time**: 1-2 focused sessions.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-A1 | **Delete 100 orphan entity workspaces** (`ent_0..49`, `entity_0..49`) and their references in handoffs/audit logs | `data/entities/ent_*`, `data/entities/entity_*` | 30 min | 🔴 HIGH — cleans 68% of entity bloat |
| H2-A2 | **Audit 48 remaining real entities** — tag each as ACTIVE|STUB|ARCHIVE in `data/entities/INDEX.yaml` | `data/entities/` | 30 min | 🟡 MED — creates entity map |
| H2-A3 | **Prune stale HALL_OF_RECORDS sessions** (sessions older than 7 days) | `data/knowledge/HALL_OF_RECORDS/` | 15 min | 🟡 MED — quarterly rotation |
| H2-A4 | **Rotate old logs** (archive >30d to `/media/omega_library/archives/logs`) | `data/logs/` (139 MB) | 15 min | 🟡 LOW — frees 139 MB |
| H2-A5 | **Reclaim `rag-v1/`** — ensure D87 permanent eradication, update `.gitignore` | `rag-v1/` directory | 5 min | 🟡 LOW |
| H2-A6 | **Delete `.coverage` from git** — add to `.gitignore` | `.coverage` (69KB) | 5 min | 🟡 LOW |
| H2-A7 | **Delete `opencode.json.bak`** — stale backup | `opencode.json.bak` | 1 min | 🟡 LOW |
| H2-A8 | **Archive old handoffs** (>3 days, not in current sprint) to `data/handoff/archive/` | `data/handoff/*.md` | 15 min | 🟡 MED — reduces top-level noise |

### Phase H2-B: WAD Content (USER-FACING IWAD Restoration)
**Goal**: Populate `arcana_novai` IWAD with real entity configs.
**Time**: 1 session.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-B1 | **Create arcana_novai entity files** — entity YAMLs for esoteric pillar entities (Sekhmet, Isis, Hecate, Anubis, etc.) in `config/wads/arcana_novai/entities/` | `config/wads/arcana_novai/entities/*.yaml` | 1 hr | 🔴 HIGH — enables user's main IWAD |
| H2-B2 | **Update `arcana_novai/manifest.yaml`** — set proper version, entity list | `config/wads/arcana_novai/manifest.yaml` | 10 min | 🟡 MED |
| H2-B3 | **Add vr/ and voices/ stubs** for arcana_novai IWAD | `config/wads/arcana_novai/vr/`, `voices/` | 10 min | 🟡 LOW |
| H2-B4 | **doom_universe IWAD scaffold** — placeholder README and minimal entity template | `config/wads/doom_universe/` | 15 min | 🟡 LOW — community deferred |

### Phase H2-C: Source Hygiene (LOW-RISK CODE FIXES)
**Goal**: Fix all amber-source items that don't require architectural changes.
**Time**: 1 session.

| # | Task | File/Module | Effort | Risk |
|---|------|-------------|--------|------|
| H2-C1 | **Fix `test_bug_001_fix.py`** — convert `print()` assertions to proper `assert`/`pytest.raises` | `tests/test_bug_001_fix.py` | 15 min | 🔴 LOW — false coverage fixed |
| H2-C2 | **Fix CI `test.yml` indentation** — broken YAML at lines ~22-24 | `.github/workflows/test.yml` | 5 min | 🟡 MED — CI was failing |
| H2-C3 | **Fix `test_hierarchy.py` duplicated imports** — lines 29-48 | `tests/test_hierarchy.py` | 5 min | 🟡 LOW |
| H2-C4 | **Add `.coverage` to `.gitignore`** | `.gitignore` | 1 min | 🟡 LOW |
| H2-C5 | **Weatherize `_collect_engine_state`** — wrap `ModelGateway()` in try/except with fallback | `src/omega/observability.py:227-237` | 10 min | 🟡 MED — potential crash hang |
| H2-C6 | **Delete `gnosis-analyst.md` references** from `.opencode` configs and handoffs (deleted in working tree) | `.opencode/agents/`, docs | 10 min | 🟡 LOW |
| H2-C7 | **Cvar migration audit** — find any remaining hardcoded values that should use `cvar_get()` | `src/omega/` | 20 min | 🟡 MED — D101 completeness |

### Phase H2-D: Documentation Consolidation
**Goal**: Reduce doc sprawl, clarify SSoTs, clean auto-generated clutter.
**Time**: 1-2 sessions.

| # | Task | File/Module | Effort | Impact |
|---|------|-------------|--------|--------|
| H2-D1 | **Consolidate roadmap docs** — `ROADMAP.md` → redirect to `SOVEREIGN_EVOLUTION_ROADMAP.md` (this doc); `MASTER_LEDGER.md` → appendix; `MASTER_SYNTHESIS_AND_ROADMAP.md` → archive | root + `docs/strategy/` | 20 min | 🔴 HIGH — stops doc confusion |
| H2-D2 | **Update `docs/INDEX.md`** — add links to this document, Hivemind Protocol, Subagent Dispatch | `docs/INDEX.md` | 15 min | 🟡 MED |
| H2-D3 | **Archive `R_AUTO_*` files** — these are auto-generated research notes, move to `docs/archives/` | `docs/research/R_AUTO_*.md` | 10 min | 🟡 LOW — noise reduction |
| H2-D4 | **Audit R-doc INDEX.md** — ensure all 200+ research R-docs are correctly cataloged | `docs/research/INDEX.md` | 1 hr | 🟡 MED — ongoing maintenance |
| H2-D5 | **Clean up `docs/` empty subdirs** — `docs/audit/`, `docs/hardening/` are empty | `docs/audit/`, `docs/hardening/` | 5 min | 🟡 LOW |
| H2-D6 | **Update `README.md`** — make it the true entry point (add badges: tests passing, temple grade, sovereignty ratio) | `README.md` | 20 min | 🟡 MED — first impression |

---

## §3 Horizon 3: Pattern Deep Mining (POST-HYGIENE)

After H2 (all GREEN), the engine is ready for deeper pattern extraction.

### H3-A: Hivemind Productionization
| # | Task | Priority |
|---|------|----------|
| H3-A1 | Wire Redis Pub/Sub as Hivemind backend (currently in-memory, TTL 300s) | P1 — cross-session persistence |
| H3-A2 | Add Hivemend SSE endpoint for real-time agent awareness in Iris/Gnosis | P2 — live awareness |
| H3-A3 | Hivemind CLI via `omega hivemind` (currently only via `link-p9` Makefile targets) | P3 — usability |
| H3-A4 | Cross-CLI awareness (Cline <-> OpenCode) via Hivemind pub/sub | P1 — agent coordination |

### H3-B: id Software Heritage Mining (CONTINUATION)
| # | Task | Priority | Reference |
|---|------|----------|-----------|
| H3-B1 | **QuakeC Flat Entity schema** — data-driven entity patterns (R-25) | P2 | R_ID_SOFTWARE_DEEP_MINING_VOL1..3 |
| H3-B2 | **4-Tier Memory full implementation** — Hunk/Zone/Cache/Temp with proper LRU (R-23) | P1 | CREDITS.md §1.23 |
| H3-B3 | **Fixed-Size Active Set** — O(1) culling for hot paths (R-29) | P3 | CREDITS.md §1.21 |
| H3-B4 | **4-Path Virtual Filesystem** — base + cd + home + current search order (R-27) | P3 | CREDITS.md §1.22 |
| H3-B5 | **High-Bit Leaf Trick** — type-tag reuse in constrained fields (R-28) | P3 | CREDITS.md §1.24 |
| H3-B6 | **Multi-Index Entity (Mobj)** — sector list + blockmap simultaneously (R-24) | P2 | CREDITS.md §1.20 |

### H3-C: Testing Coverage Expansion
| # | Task | Module | Current tests | Target | Priority |
|---|------|--------|:-------------:|:------:|----------|
| H3-C1 | Oracle main entry (`oracle.py`) | 965 LOC | ~25 | +10 | P1 — critical path |
| H3-C2 | WAD Loader edge cases (corrupt manifest, missing IWAD) | `wad_loader.py` | ~10 | +5 | P1 — critical path |
| H3-C3 | Multi-depth research (depth=4 scholarly path) | `library/research.py` | minimal | +3 | P2 |
| H3-C4 | Hivemind protocol (post_context + get_awareness + heartbeat) | `server.py` (hub) | 0 | +5 | P1 — new code |
| H3-C5 | CLI commands (talk, summon, library, queue, bench) | `cli/*` | 0 | +5 | P2 |
| H3-C6 | Iris FastAPI container | `iris/*` | 7 | +3 | P3 |

---

## §4 Horizon 4: Community & Production

After H2+H3 (all subsystems GREEN, doc consolidation complete):

| Phase | Goal | Estimated Window |
|-------|------|-----------------|
| H4-A: **Entity Studio CLI** | Visual entity editor (CLI->TUI->GUI) | Post-H3 |
| H4-B: **Stack Builder Wizard** | One-command community IWAD creation | Post-H3 |
| H4-C: **Omega Desktop** | Electron/Tauri wrapper with local-first steamlined UX | 2027 |
| H4-D: **Omegaverse P2P** | Cross-instance entity communication, shared VR realms | 2028+ |

---

## §5 Priority Execution Order

The above phases are **dependency-ordered**. Do H2-A → H2-B → H2-C → H2-D before
starting H3. Join work where possible:

```
Session 1:  H2-A (data hygiene) + H2-C1..4 (source fixes) = 1.5 hr
Session 2:  H2-B (IWAD content) + H2-D (doc consolidation) = 2 hr
Session 3:  H3-A (hivemind) + H3-C1..2 (oracle + wad tests) = 2 hr
Session 4:  H3-B (heritage mining) + H3-C3..6 (remaining tests) = 2 hr
Session 5:  H4 kickoff (entity studio design doc) = 1 hr
```

Each session ends with:
1. `make test` — 312/312 GREEN
2. `make temple-grade` — T1-T11 must pass
3. `git add -A && git commit -m "phase: <name> — <summary>"`
4. `git push origin main`
5. Distill L1→L2→L3 to soul.yaml if entity-touching

---

## §6 Success Criteria

| Phase | Green | Yellow | Red |
|-------|-------|--------|-----|
| **H2-A (Data Hygiene)** | < 10 orphan entities; < 50% bloat removed | < 50 orphans | ≥ 100 orphans |
| **H2-B (IWAD Content)** | arcana_novai has ≥ 12 entity files; `omega talk` works | ≥ 6 entity files | 0 entity files |
| **H2-C (Source Hygiene)** | 0 amber items; CI fully GREEN | 1-2 amber items | ≥ 3 amber items |
| **H2-D (Doc Consolidation)** | 1 roadmap SSoT; INDEX.md updated; `R_AUTO_*` archived | 2 roadmap docs remaining | ≥ 3 roadmap docs |
| **H3 (All)** | All H3 items GREEN; test count ≥ 330 | 1-2 items remaining | ≥ 3 items not started |

---

## §7 Heritage Attribution

This roadmap continues the id Software architectural lineage:
- `[id-soft: doom-1993] ZONEID Pattern` — every strategic constant carries heritage
- `[id-soft: quake-1996] Thinker Chain` — Hivemind lifecycle
- `[id-soft: quake3-1999] Cvar System` — cvar_table.py evolution
- `[id-soft: doom-1993] WAD System` — IWAD/PWAD architecture
- `[id-soft: doom3-2004] idHeap` — current Hot/Warm/Cold memory
- `[id-soft: quake-1996] net_chan.c` — Hivemind Pub/Sub future

---

*⬡ This document supersedes HORIZON_MAP.md as the active roadmap. ⬡*
*MASTER_LEDGER.md is incorporated as Appendix A. ROADMAP.md defers here.*
*Decision: D111 — Sovereign Evolution Roadmap adopted.*
