# 🔱 Omega Engine — Single Source of Truth (Condensed)
**Source**: `OMEGA_ENGINE.md` (163 lines) — this is the ~55-line state card.
**Last Updated**: 2026-07-19 | **Version**: v1.5.0

---

## §1 Identity

**Omega Engine** = Universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference floor; local verification ceiling.
- **Local-first**: Cloud = teacher, never dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (id Software heritage).
- **Standalone Packages**: `omega-sieve`, `omega-doc-reader` on PyPI.

---

## §2 Current State

| Metric | Value | Status |
|--------|-------|--------|
| Tests | **1398 passed** (43 skipped, 7 xfailed) | ✅ |
| Mandates | **23 enforced** (M1-M23) | ✅ |
| Compliance | **13/23 FULL** (56.5%) — 5 Partial, 5 Fail | ❌ |
| Fleet | **14 agents** (cap: 14) | ✅ |
| WADs | **4** (arcana_novai, torment, youtube_research, youtube_worker) | ✅ |
| Heritage | **121 [id-soft:] tags** — all vetted | ✅ |
| Shared Modules | **3** (omega-vetala, omega-sieve, omega-doc-reader) | ✅ |
| Third-Party Registry | **18/19 repos** — P0: 4/4, P1: 5/5, P2: 6/6, P3: 1/4 | ✅ |

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
| Soul Utils | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE |
| WAD Loader | `src/omega/oracle/wad_loader.py` | ✅ V2 schema |
| Hivemind | `mcp_servers/omega_hub/` | ✅ 6 MCP tools |
| CLI | `src/omega/cli/oracle_cli.py` | ✅ Typer CLI |

---

## §4 Recent Milestones

| Milestone | Status |
|-----------|--------|
| D-281 Substrate Repair (4 phases) | ✅ COMPLETE |
| D-282 sqlite-vec Strike 10 | ✅ COMPLETE |
| D-283 Phase 2 RecallStore | 🟡 27/29 tests |
| MIAP (context collision) | ✅ MERGED |
| HMC Quad-Forge (4-mind council) | ✅ COMPLETE |
| D-298 Decision Workspace | ✅ GROUNDED MEDITATION |
| Soul Evolution v7.0 | ✅ 15 L3 principles promoted |
| Heritage vet Pi PR #2903 | ✅ vet-072 APPROVED |

---

## §5 Key Files

| File | Purpose |
|------|---------|
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions |
| `CREDITS.md` | Heritage attribution |
| `data/entities/kali/session_gnosis.md` | Session anchor (M15) |
| `.opencode/anchored-summary.md` | Post-compaction recovery |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

**Full engine docs**: `OMEGA_ENGINE.md` | **Roadmap**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
