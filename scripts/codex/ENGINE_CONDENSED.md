# 🔱 Omega Engine — Single Source of Truth (Condensed)
**Source**: `OMEGA_ENGINE.md` (176 lines) — this is the ~85-line state card.
**Last Updated**: 2026-07-22 | **Version**: v1.8.0

---

## §1 Identity

**Omega Engine** = Universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference floor; local verification ceiling.
- **Local-first**: Cloud = teacher, never dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (id Software heritage).
- **Standalone Packages**: `omega-sieve`, `omega-doc-reader`, `omega-meditation` on PyPI.

---

## §2 Current State (2026-07-22)

| Metric | Value | Status |
|--------|-------|--------|
| Tests | **1,572 collected** · **50/50 core+contract+chaos+SoulStore pass** | ✅ C-0 complete |
| Mandates | **25 enforced** (M1-M25) | ✅ All enforced |
| Compliance | **21/25 FULL (84%)** — 2 Partial, 2 Fail | ⚠️ M5, M11 remain |
| Fleet | **12 agents** (cap: 14 per M10) | ✅ |
| WADs | **4** (arcana_novai, torment, youtube_research, youtube_worker) | ✅ |
| Heritage | **121 [id-soft:] tags** — all vetted | ✅ |
| Shared Modules | **4** (omega-vetala, omega-sieve, omega-doc-reader, omega-meditation) | ✅ 3 on PyPI |
| **WARP Proxy Pool** | **3-node pool operational** (8081/8082/8083) | ✅ **W-1 FIXED** |
| **Gemma 4 31B workhorse** | **DEAD** — 16k free input TPM since Jul 15 | 🚨 **G-1 PENDING** |
| **Antigravity OAuth** | **PARTIAL** — API-key only | 🟡 G-1b path |

---

## §3 Core Subsystems

| Subsystem | Module | Status |
|-----------|--------|--------|
| Oracle | `src/omega/oracle/` | ✅ Operational |
| Entity Registry | `src/omega/oracle/entity_registry.py` | ✅ YAML-backed CRUD |
| Model Gateway | `src/omega/oracle/model_gateway.py` | ✅ 8-backend provider fabric |
| Memory Store | `src/omega/memory_store.py` | ✅ Hot/Warm/Cold/Temp |
| Vector Store | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE |
| Config Resolver | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE |
| Hybrid Search | `src/omega/memory/hybrid_search.py` | ✅ RRF k=60 |
| MIAP | `src/omega/coordination/miap.py` | ✅ MERGED |
| sqlite_policy | `src/omega/persistence/sqlite_policy.py` | ✅ FS-B4 COMPLETE |
| Hivemind | `mcp_servers/omega_hub/` | ✅ 6 MCP tools |
| CLI | `src/omega/cli/oracle_cli.py` | ✅ Typer CLI |

---

## §4 Foundation Stabilization Campaign

**Status**: RATIFIED ✅ | **Gate A**: PASSED | **Phase B**: COMPLETE | **Gate B**: PASSING

| Workstream | Summary | Status |
|-----------|---------|--------|
| FS-B1 | Embedding SSOT (768 write-path, config_resolver fix, 8 tests) | ✅ |
| FS-B2 | Dispatch Registry (ics.py loader, correct API shape, 11 tests) | ✅ |
| FS-B3 | Path Resolver CI (77-entry allowlist, semantic CI) | ✅ |
| FS-B4 | SQLite Policy Migration (4 profiles, reader/writer, BEGIN IMMEDIATE) | ✅ 77/77 |
| FS-B5 | search_persistence (DATA_DIR path, missing imports) | ✅ |

**Next Phase Γ**: Hub split, policy extraction, Oracle DI

**Memory ADR**: `docs/adr/ADR-001-memory-layer-architecture.md` — RATIFIED ✅

---

## §5 Recent Milestones

| Milestone | Status |
|-----------|--------|
| FS-B4 SQLite Policy Migration | ✅ COMPLETE |
| Foundation Stabilization Campaign | ✅ RATIFIED |
| Memory ADR (ADR-001) | ✅ RATIFIED |
| D-282 sqlite-vec Strike 10 | ✅ COMPLETE |
| D-300 Autonomous Meditation (`omega-meditation`) | ✅ PRODUCT DELIVERED |
| D-301 MaKaLi Parallel Council | ✅ RATIFIED |
| D-308 Ubuntu 25.10 Toolchain Verification | 🚨 P0 GATE |
| Soul Evolution v7.0 | ✅ 15 L3 principles promoted |
| C-10.5 Quota-Aware Provider Routing | ✅ COMPLETE |
| V-1 VaultCore MVP | ✅ COMPLETE |
| C-3 Restic 3-2-1 Backup | ✅ COMPLETE |
| W-1 WARP Proxy Pool | ✅ FIXED |

---

## §6 Key Files

| File | Purpose |
|------|---------|
| `SOVEREIGN_MANDATES.md` | 25 Constitutional Laws (v3.7.0) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master roadmap (v5.2) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions |
| `CREDITS.md` | Heritage attribution (121 tags) |
| `data/coordination/SESSION_ANCHOR.md` | Session anchor (M15) |
| `.opencode/anchored-summary.md` | Post-compaction recovery |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

**Full engine docs**: `OMEGA_ENGINE.md` | **Roadmap**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
