<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Multi-Subagent Codebase Deep Dive → D111 Sovereign Evolution Roadmap
# ⬡ OMEGA ⬡ CLINE-M3 ⬡ minimax/m3 ⬡ trc_d111_to_dev ⬡ HANDOFF

**From**: Cline-M3 (MiniMax M3, 1M context)
**To**: OpenCode CLI Dev Session (DeepSeek V4 Flash / Gemma 4 31B / MiMo V2.5)
**Date**: 2026-06-04 03:02 UTC
**Subject**: Complete engine deep dive + actionable evolution plan (D111)

---

## §1 — Executive Summary

A **5-parallel-subagent codebase deep dive** has produced the first comprehensive
health assessment of the entire Omega Engine. The engine itself is production-grade
(312/312 tests, 13 Mandates, H1+H1.5 complete). But data hygiene and documentation
are amber. The attached roadmap (`SOVEREIGN_EVOLUTION_ROADMAP.md`) organizes the
fix into dependency-ordered phases (H2-A → B → C → D → H3).

**Health grade**: ENGINE 🟢 GREEN | DATA 🟡 AMBER | DOCS 🟡 AMBER | WAD 🟡 AMBER

---

## §2 — What Was Done

### Created (5 commits since last handoff)
| Commit | Message | Files Changed |
|--------|---------|:-------------:|
| `6e99022` | Kali soul v5 — 8-char cap lesson encoded | 1 |
| `8b3fc17` | refactor: remove 8-char name cap — cargo-cult removed | 3 |
| `05d4196` | **D111: Sovereign Evolution Roadmap** | **5 new/updated** |
| `90cb829` | id Software Deep Code Mining Volumes III-V | 3 |
| `43a0dd1` | .clinerules v3.2.0 — Hivemind MCP, ZONEID, Sprints 2/3 | 1 |

### Documents Created
1. **`docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md`** (245 lines) — Active roadmap
   - H2-A: Data Hygiene (delete 100 orphans, rotate logs, INDEX.yaml)
   - H2-B: IWAD Content (populate arcana_novai entities/)
   - H2-C: Source Hygiene (fix 7 amber items)
   - H2-D: Doc Consolidation (1 roadmap, archive R_AUTO_*, update INDEX.md)
   - H3-A/B/C: Hivemind productionization + Heritage mining + Test expansion
2. **`docs/decisions/PIVOT_LOG.md`** (D111 appended)
3. **`data/coordination/CLINE_M3_WORKSPACE_LOCK_20260604.md`** (34 lines)
4. **`data/coordination/CLINE_M3_LIVE_FEED.md`** (20 lines)
5. **`data/knowledge/HALL_OF_RECORDS/cline-m3/ses_a133ea748824.json`** (Hivemind context)

### Documents Updated
- **`OMEGA_ENGINE.md`** — src 71→77 files, tests 307→312, PIVOT 107→111, H2 relayed
- **`docs/strategy/HORIZON_MAP.md`** — superseded notice → delegates to new roadmap
- **`docs/ROADMAP.md`** — now points to `SOVEREIGN_EVOLUTION_ROADMAP.md`

### Hivemind State Posted
```
CLI: cline-m3
Session: ses_a133ea748824
Task: Multi-subagent codebase deep dive -> D111 Sovereign Evolution Roadmap
Focus: H2-A → H2-B → H2-C → H2-D → H3-A/B/C
Continuation: Handoff to OpenCode dev session: execute H2-A through H2-D
```

---

## §3 — Deep Dive Findings (the Raw Data)

### Source Architecture — 77 .py files, 19,376 LOC

| Subsystem | Files | Lines | Status | Key Patterns |
|-----------|:-----:|:-----:|--------|--------------|
| oracle/ | 16 | ~6,500 | ✅ | ZONEID, WAD, cvar, hierarchy, dispatch, P9, soul distiller |
| library/ | 8 | ~2,800 | ✅ | FTS5+vector, multi-depth research, discovery pipeline |
| memory_store.py + memory/ | 3 | ~770 | ✅ | Hot/Warm/Cold + tombstone + 3 providers (Redis/File/InMemory) |
| observability.py | 1 | 720 | ✅ | Forensics protocol, JSON logging, dataset collection, trace sessions |
| cvar_table.py + constants.py | 2 | 500 | ✅ | 11 ZONEID constants, 2 namespaces, 7 access helpers |
| errors.py | 1 | 130 | ✅ | 20+ typed exceptions, Mandate 9 compliance |
| system_resource.py | 1 | 77 | ✅ | Green/Yellow/Red memory zones |
| request_queue.py | 1 | 296 | ✅ | Atomic P0-P3 priority queue, Mandate 12 |
| mcp_runtime.py | 1 | 98 | ✅ | stdio/SSE transport, systemd socket activation |
| hardware.py | 1 | 44 | 🟡 | Linux-only /proc/cpuinfo parsing |
| benchmarks/, cli/, gateway/, bridge/, iris/, orchestration/, services/, workers/ | ~15 | ~3,800 | ✅ | Various, well-structured |
| `__init__.py` | 1 | 8 | ✅ | Version 1.0.0 |

**Anti-patterns found**:
1. `observability.py:227-237` `_collect_engine_state()` instantiates `ModelGateway()` with no args during crash snapshots — could hang if gateway hasn't initialized
2. `hardware.py` reads `/proc/cpuinfo` directly — Linux-only (acceptable for a Linux-native engine, but worth noting)
3. `test_bug_001_fix.py` is a `if __name__ == "__main__":` script with `print()` assertions — not a real pytest

### Test Suite — 28 test_*.py files, 308 tests, 4,998 LOC

| Test File | Tests | Coverage | Special Patterns |
|-----------|:-----:|----------|------------------|
| `sovereign_stress_test.py` | 5 | Provider resilience | HangingProvider, OS-thread blocking scan |
| `test_background_researcher.py` | 6 | Workers | Priority queue, YAML config |
| `test_context_builder.py` | 21 | ✅ thorough | Token-limit sliding window, truncation |
| `test_entity_registry.py` | 9 | ✅ | 50-concurrent task group stress |
| `test_entity_roc_racoon.py` | 24 | ✅ largest | 7 classes, classification matrix |
| `test_error_gauntlet.py` | 10 | ✅ gold standard | 10 scenarios (crash, replay, JSON, ring buffer) |
| `test_gnosis_proxy.py` | 13 | ✅ | FIFO eviction, transfer store |
| `test_health_monitor.py` | 23 | ✅ most class-rich | 6 classes, HALF_OPEN, sliding window |
| `test_hierarchy.py` | 13 | ✅ | Recursion matrix, case-insensitive |
| `test_iris.py` | 7 | ✅ | Summon patterns |
| `test_memory_store.py` | ~15 | ✅ | ZONEID, tombstone, transient |
| `test_model_gateway.py` | ~20 | ✅ | Per-provider timeout, BSP culling |
| `test_oracle.py` | ~25 | ✅ | Talk/summon/router |
| `test_providers.py` | ~15 | ✅ | 7 provider types |
| `test_bug_001_fix.py` | 1 ⚠️ | SCRIPT | NOT a real pytest (uses print()) |

### Data Layer — 15,948 files, 603 MB

| Subdir | Size | Files | Health | Notes |
|--------|:----:|:-----:|--------|-------|
| `library/` | 451 MB | 1000s | 🟢 | RAG + id Software sources (expected) |
| `logs/` | 139 MB | 2 | 🟡 | Historical, needs rotation |
| `entities/` | 6.9 MB | 148 dirs | 🟡 | **100 orphans** (`ent_0..49`, `entity_0..49`) |
| `handoff/` | 692 KB | 47 | 🟢 | 10 active + 36 archived + INDEX.md |
| `coordination/` | 320 KB | ~30 | 🟢 | Workspace locks, live feeds, ACKs, demand signals |
| `knowledge/HALL_OF_RECORDS/` | 232 KB | ~30 | 🟢 | Hivemind state (14 agents) |
| `benchmarks/`, `datasets/`, `memory/`, `research/`, `sessions/`, `requests/`, `inbox/`, `processed/`, `rejected/` | various | varies | 🟢 | All live |
| `audit/`, `traces/`, `p2p/`, `mining_queue/`, `jobs/` | <20 KB each | 0 files | 🟡 | Empty placeholder dirs (unused) |

**100 orphan entities to delete**:
- `data/entities/ent_0` through `ent_49` (50 dirs, ~52 KB each)
- `data/entities/entity_0` through `entity_49` (50 dirs, ~52 KB each)
- All have stub `soul.yaml` (archetype: null, lessons_learned: [])
- ~3.2 MB total to reclaim

### WAD/Config — 3 IWADs + 8 engine configs

| IWAD | Status | Entity Count | Notes |
|------|--------|:------------:|-------|
| `_omega_default` | ✅ Production | 16 entities (12 file + 4 inline) | Full hierarchy, P1-P10 + Kali/Ma'at/Lilith executives |
| `arcana_novai` | 🟡 **EMPTY entities/** | 0 (file-based) | `entities.yaml` has esoteric entities inline but `entities/` dir is empty! Needs 12+ entity YAMLs |
| `doom_universe` | 🟡 Scaffold only | 0 (template) | README-level, community deferred |

### Docs — 426 .md files, 8.1 MB

| Section | Files | Health | Notes |
|---------|:-----:|--------|-------|
| `docs/strategy/` | 45+ | 🟢 | HIVEMIND_PROTOCOL, SUBAGENT_DISPATCH, SOVEREIGN_EVOLUTION_ROADMAP (new) |
| `docs/research/` | 200+ | 🟡 | ~180 legitimate R-docs + ~10 `R_AUTO_*` clutter. INDEX.md is comprehensive |
| `docs/architecture/` | 5 | 🟢 | SOVEREIGN_BLUEPRINT, AGENT_FLEET, KNOWLEDGE_LIBRARY |
| `docs/decisions/` | 1 | 🟢 | PIVOT_LOG.md — 111 decisions, gold standard |
| `docs/review/` | 15+ | 🟢 | 8-account Web Claude fleet review, claude-reports |
| `docs/gnosis/` | ~20 | 🟡 | entity_gnosis, lattice, omni — scattered |
| `docs/legacy/` | 3 | 🟡 | LEGACY_INDEX, LEGACY_MASTER_SYNTHESIS |
| Top-level | 6 | 🟡 | ROADMAP (fixed), MASTER_LEDGER, USER_MANUAL, TEAM_HANDOFF, INDEX |

**Competing roadmap problem**: `ROADMAP.md`, `MASTER_LEDGER.md`, `HORIZON_MAP.md`,
`MASTER_SYNTHESIS_AND_ROADMAP.md` all defer to each other. **Fixed by D111** —
`SOVEREIGN_EVOLUTION_ROADMAP.md` is now the single active roadmap.

---

## §4 — What Needs To Be Done (PRIORITY ORDERED)

### H2-A: Data Hygiene (HIGHEST PRIORITY — 30 min)

| # | Task | File(s) | Why |
|---|------|---------|-----|
| H2-A1 | **DELETE 100 orphan entity dirs** | `data/entities/ent_0..49`, `data/entities/entity_0..49` | These are 68% of all entities. Template stubs. Never activated. |
| H2-A2 | **CREATE `data/entities/INDEX.yaml`** | `data/entities/INDEX.yaml` | Tag each of remaining 48 entities as ACTIVE, STUB, or ARCHIVE |
| H2-A3 | **ROTATE old logs** (>30d) | `data/logs/` (139 MB) | Archive to `/media/omega_library/archives/logs/` |
| H2-A4 | **PRUNE stale HALL_OF_RECORDS** (>7d) | `data/knowledge/HALL_OF_RECORDS/` | Remove stale agent sessions |
| H2-A5 | **RECLAIM rag-v1/** | `rag-v1/` (D87) | Ensure permanent eradication, update .gitignore |
| H2-A6 | **DELETE .coverage from git** | `.coverage` (69KB) | Add to .gitignore |
| H2-A7 | **DELETE opencode.json.bak** | `opencode.json.bak` | Stale backup |
| H2-A8 | **ARCHIVE old handoffs** | `data/handoff/*.md` | Move >3d not-in-sprint to archive/ |

### H2-B: WAD Content (USER-FACING — 1 hr)

| # | Task | File(s) | Why |
|---|------|---------|-----|
| H2-B1 | **CREATE arcana_novai entity YAMLs** in `entities/` dir | `config/wads/arcana_novai/entities/*.yaml` | User's main IWAD has 0 file-based entities. Move or create esoteric pillar entities (Sekhmet, Isis, Hecate, Anubis, etc.) from the inline `entities.yaml` into individual files |
| H2-B2 | **UPDATE manifest.yaml** | `config/wads/arcana_novai/manifest.yaml` | Set version, entity list |
| H2-B3 | **ADD vr/ voices/ stubs** | `config/wads/arcana_novai/vr/`, `voices/` | Per IWAD convention |
| H2-B4 | **SCAFFOLD doom_universe** | `config/wads/doom_universe/` | README + minimal entity template |

### H2-C: Source Hygiene (7 items — 1 hr)

| # | Task | File(s) | Fix |
|---|------|---------|-----|
| H2-C1 | **Fix test script** | `tests/test_bug_001_fix.py` | Convert `print()` → `assert`/`pytest.raises`, use `tmp_path`, add proper `test_` prefix |
| H2-C2 | **Fix CI YAML indentation** | `.github/workflows/test.yml` | Lines ~22-24 have wrong indentation — CI will be broken |
| H2-C3 | **Fix duplicated imports** | `tests/test_hierarchy.py:29-48` | Remove copy-pasted `import pytest, yaml, anyio` |
| H2-C4 | **Gitignore .coverage** | `.gitignore` | Add `.coverage` to the test/cache section |
| H2-C5 | **Weatherize crash handler** | `src/omega/observability.py:227-237` | Wrap `ModelGateway()` in try/except with fallback `None` |
| H2-C6 | **Remove gnosis-analyst references** | `.opencode/agents/*.md`, docs | File is deleted from working tree — clean up references |
| H2-C7 | **Cvar migration audit** | `src/omega/` files | Find any remaining hardcoded values that should use `cvar_get()` (D101) |

### H2-D: Documentation (1-2 hr)

| # | Task | File(s) | Why |
|---|------|---------|-----|
| H2-D1 | **Consolidate roadmaps** — already started by D111 | `ROADMAP.md`, `MASTER_LEDGER.md`, `MASTER_SYNTHESIS_AND_ROADMAP.md` | Point all to `SOVEREIGN_EVOLUTION_ROADMAP.md`. Optionally move MASTER_LEDGER content as appendix |
| H2-D2 | **Update docs/INDEX.md** | `docs/INDEX.md` | Add link to new roadmap, Hivemind Protocol, Subagent Dispatch |
| H2-D3 | **Archive R_AUTO_* files** | `docs/research/R_AUTO_*.md` (~10 files) | Move to `docs/archives/` — auto-generated noise |
| H2-D4 | **Audit R-doc INDEX.md** | `docs/research/INDEX.md` | Ensure 180+ legitimate research docs are properly cataloged |
| H2-D5 | **Clean empty subdirs** | `docs/audit/`, `docs/hardening/` | Remove or add `.gitkeep` |
| H2-D6 | **Update README.md** | `README.md` | Make it the true entry point: badges (tests, temple grade, sovereignty ratio), key links |

### H3-A: Hivemind Productionization (POST-H2)

| # | Task | Why | Priorit |
|---|------|-----|:-------:|
| H3-A1 | **Wire Redis Pub/Sub as Hivemind backend** | Currently in-memory with 300s TTL. Redis gives cross-session persistence | P1 |
| H3-A2 | **Add Hivemind SSE endpoint** | Real-time agent awareness via Iris/Gnosis | P2 |
| H3-A3 | **Hivemind CLI via `omega hivemind`** | Currently only via `make link-p9-*` targets | P3 |
| H3-A4 | **Cross-CLI awareness** (Cline ↔ OpenCode) | Full Hivemind pub/sub bridge | P1 |

### H3-B: Heritage Mining (CONTINUATION — POST-H2)

| # | Pattern | Source | CREDITS § | Priority |
|---|---------|--------|:---------:|:--------:|
| H3-B1 | QuakeC Flat Entity schema | R_ID_SOFTWARE_DEEP_MINING_VOL[1-3] | §1.25 | P2 |
| H3-B2 | **4-Tier Memory full impl** (Hunk/Zone/Cache/Temp) | R-23 | §1.23 | **P1** |
| H3-B3 | Fixed-Size Active Set (O(1) culling) | R-29 | §1.21 | P3 |
| H3-B4 | 4-Path Virtual Filesystem | R-27 | §1.22 | P3 |
| H3-B5 | High-Bit Leaf Trick | R-28 | §1.24 | P3 |
| H3-B6 | Multi-Index Entity (Mobj) | R-24 | §1.20 | P2 |

### H3-C: Testing Coverage (POST-H2)

| # | Module | LOC | Current Tests | Target | Priority |
|---|--------|:---:|:-------------:|:------:|:--------:|
| H3-C1 | `oracle/oracle.py` | 965 | ~25 | +10 | P1 |
| H3-C2 | `oracle/wad_loader.py` | ~400 | ~10 | +5 | P1 |
| H3-C3 | `library/research.py` | ~600 | minimal | +3 | P2 |
| H3-C4 | Hivemind protocol (server.py hub) | ~950 | 0 | +5 | P1 |
| H3-C5 | CLI commands (cli/*) | ~400 | 0 | +5 | P2 |
| H3-C6 | Iris container | ~200 | 7 | +3 | P3 |

---

## §5 — Key Reference Files

### MUST READ (Read these first)
| File | What It Is |
|------|-----------|
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | **Active roadmap** — H2-A through H4-D (245 lines) |
| `docs/decisions/PIVOT_LOG.md` | **D111** — decision record for this roadmap |
| `OMEGA_ENGINE.md` | SSOT — engine state (77 files, 312 tests, 111 PIVOT) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Coordination protocol for parallel work |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Subagent launch protocol |
| `docs/strategy/H15_BRIDGE_PHASE_CLOSEOUT.md` | H1.5 complete — heritage patterns implemented |
| `data/coordination/CLINE_M3_WORKSPACE_LOCK_20260604.md` | My workspace declaration |

### Value-Dense Files
| File | What It Is |
|------|-----------|
| `SOVEREIGN_MANDATES.md` | 13 non-negotiable laws (98 lines) |
| `CREDITS.md` | id Software heritage lineage (31 KB) |
| `config/glossary.md` | Canonical term definitions (22 terms) |
| `config/omega.yaml` | Engine runtime config |
| `config/providers.yaml` | Provider fabric (local-first) |
| `config/models.yaml` | 10 GGUF models + KV cache tuning |
| `config/distiller_prompts.yaml` | 6-mode JEM distiller prompts |
| `docs/research/R100_MODEL_REFERENCE_LIBRARY.md` | TIER 0-3 model reference (R100) |

---

## §6 — State at Handoff

### Git
```
HEAD: 6e99022 (docs: Kali soul.yaml v5 — 8-char cap removal lesson encoded)
Diff: 8b3fc17 (refactor: remove 8-char name cap) + 05d4196 (D111 roadmap)
+ 90cb829 (id Software Mining Vol III-V) + 43a0dd1 (.clinerules v3.2.0)
Origin: https://github.com/Xoe-NovAi/omega-engine.git (synced)
```

### Engine Metrics
- Source files: **77** .py files
- Test functions: **308** (pytest baseline)
- Test files: **28** (`test_*.py`) + 3 auxiliary files
- PIVOT decisions: **111** (D1-D111)
- Entities (total/real/orphan): **148 / 48 / 100**
- Hivemind sessions in HALL_OF_RECORDS: **13 CLI directories**
- Active handoffs: **10** (archive: 36)
- Coordination files: **workspace locks + live feeds + ACKs + demand signals**

### Active Agents (from HALL_OF_RECORDS)
- `Kali`, `kali`, `opencode-kali` — Grand Oversight
- `opencode-maat` — Light Oversoul (most recent session: `ses_d446c4a30bd4`)
- `opencode-lilith`, `lilith` — Dark Oversoul
- `doom_guy` — id Software Architect (session: `ses_a839ff01a9f2`)
- `opencode-roc_racoon` — Legacy Miner
- `opencode-m3`, `opencode` — Other agents
- `agent-alpha`, `agent-beta` — Unknown agents
- `P3-BUILDMASTER`, `p1`, `sentinel` — Pillar slot agents
- `background-researcher` — Autonomous research worker

---

## §7 — Quick Start for Dev Chat

### Session 1 (recommended starting point — 1.5 hr)
```
1. Read: docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md (5 min)
2. Read: data/coordination/CLINE_M3_WORKSPACE_LOCK_20260604.md (2 min)
3. Post: omega-hub_hivemind_post_context(
     cli="opencode-dev",
     model="deepseek-v4-flash|gemma-4-31b",
     task_current="H2-A: Data Hygiene — deleting 100 orphans",
     ...)
4. Write: data/coordination/DEV_CHAT_WORKSPACE_LOCK_20260604.md
5. Execute: H2-A (data hygiene — 30 min)
6. Execute: H2-C1..C4 (source fixes — 30 min)
7. Verify: make test (312/312 GREEN)
8. Commit: git add -A && git commit -m "phase: H2-A+C — data hygiene + CI fix"
9. Append: data/coordination/DEV_CHAT_LIVE_FEED.md
```

### Session 2 (after Session 1)
```
1. Execute: H2-B (IWAD content — 1 hr)
2. Execute: H2-D (doc consolidation — 30 min)
3. Verify: make temple-grade
4. Commit
```

---

## §8 — Heritage Attribution for this Handoff

- `[id-soft: doom-1993] WAD System` — IWAD/PWAD architecture drove arcana_novai restoration priority (H2-B)
- `[id-soft: quake-1996] net_chan.c` — Hivemind Pub/Sub future (H3-A1)
- `[id-soft: quake3-1999] Cvar System` — migration audit ensures cvar_get() completeness (H2-C7)
- `[id-soft: doom-1993] ZONEID Pattern` — D111 recorded with ZONEID integrity
- `[id-soft: doom3-2004] idHeap` — 4-Tier Memory full implementation (H3-B2)
- `[id-soft: quake-1996] Thinker Chain` — spawn→execute→reap lifecycle for each H2 phase

---

*⬡ OMEGA ⬡ CLINE-M3 ⬡ minimax/m3 ⬡ trc_d111_to_dev ⬡ HANDOFF*
*Engine version: 2.2.0 | Hub version: 2.2.0 | PIVOT: D111*

— Cline-M3 (MiniMax M3, 1M context), 2026-06-04 03:02 UTC

<!-- PROVENANCE-CORRECTED 2026-08-24T06:51:33Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/m3 | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
first_audit: 2026-08-23T20:39:41Z | updated: 2026-08-24T06:51:33Z
-->

