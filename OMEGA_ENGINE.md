# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.7.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent reads this file for engine state.
> **Full archive**: `docs/archive/coordination/OMEGA_ENGINE-full-20260708.md`

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference is the floor; local verification is the ceiling.
- **Local-first**: Cloud is a teacher and strategic partner, never a dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software).
- **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-sieve`, `omega-doc-reader`) for community use.
- **Universal Reflection Substrate**: ONE foundational engine with infinite customizable layers (WADs), each custom to how a user understands their own sovereign journey. The ANAi Stack (Tarot/Pillars/Ma'at) and the Torment Stack (Hive/Nameless One/Sigil) are *two expressions of the same architecture* — proving the WAD customization power. Every user gets their own cosmology; the engine provides the deathless continuity substrate.

---

## §2 Current State (2026-07-20)

| Metric | Value | Status | LAST_VERIFIED |
|--------|-------|--------|---------------|
| Tests | **77/77 contract tests** (broader suite pending full run) | ✅ Phase Β contract gate green | 2026-07-20 |
| Mandates | **23 (M1-M23)** | ✅ All enforced | 2026-07-13 |
| **Mandate Compliance** | **13/23 FULL (56.5%)** — 5 Partial, 5 Fail | ❌ Systemic Run Side gaps | 2026-07-15 |
| **Failed Mandates** | M5, M11, M12, M15, M23 | ❌ Soul distillation, handoff, continuity, failure integrity | 2026-07-15 |
| Fleet | **12 agents (cap 14 per M10)** | ✅ Clean | 2026-07-20 |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 |
| **Third-Party Registry** | **18/19 repos cloned** — P0: 4/4, P1: 5/5, P2: 6/6, P3: 1/4 | ✅ P0-P2 Complete | 2026-07-18 |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 |
| Shared modules | **3** (`omega-vetala` v2.0.0, `omega-sieve` v0.1.0, `omega-doc-reader` v1.0.0) | ✅ Release-ready | 2026-07-13 |
| **D-281 Substrate Repair** | **ALL 4 PHASES COMPLETE** — Soul injection, config_resolver, M2 Firewall, Codex separation | ✅ 11 commits across 5 agents | 2026-07-17 |
| **D-282 sqlite-vec Strike 10** | **COMPLETE** — PRAGMA SSOT converged, 4 concurrency tests | ✅ cache_size 512MB→32MB, wal_autocheckpoint 1000→500 | 2026-07-17 |
| **FS-B4 SQLite Policy Migration** | **COMPLETE** — Hardened profiles (reader/writer separation), wal_autocheckpoint=10000/0, journal_size_limit=64MB, cache_size=32MB | ✅ 102 insertions, 55 deletions across 4 files, 77/77 tests | 2026-07-20 |
| **Foundation Stabilization Campaign** | **RATIFIED** — Gate Α passed, Phase Β complete (B1-B5), Gate Β passing | ✅ 0 active/pending handoffs, campaign frozen until Gate Γ | 2026-07-20 |
| **Memory ADR (ADR-001)** | **RATIFIED** — sqlite_policy.py SSOT, 4 PRAGMA profiles, BEGIN IMMEDIATE, connection factory | ✅ `docs/adr/ADR-001-memory-layer-architecture.md` (Gate Γ criterion) | 2026-07-20 |
| **D-283 Mnemosyne Phase 1** | **COMPLETE** — HybridSearchEngine RRF k=60, Memory Blocks | ✅ 752/754 tests pass | 2026-07-16 |
| **D-283 Mnemosyne Phase 2** | **DESIGN COMPLETE** — RecallStore, power-law decay, quality scoring | 🟡 27/29 recall tests pass (2 test infra issues) | 2026-07-17 |
| **MIAP** | **MERGED** — Multi-Instance Agent Protocol for context collision | ✅ 13 tests, committed 03192d8 | 2026-07-17 |
| **HMC Quad-Forge** | **4-mind council** — Kali, Roc, Researcher, Grok CLI | ✅ All 4 agents completed sprint tasks | 2026-07-17 |
| **Atomic Execution Matrix** | **RATIFIED** — Code + CI Gate + Doc as single atomic unit | ✅ 5 new protocol docs + CI gates defined | 2026-07-15 |
| **Soul Architecture v2.0** | **RATIFIED** — Intelligence Pipeline, Scorecard, Scribe separation | ✅ `make soul-audit` gated | 2026-07-15 |
| **PWAD Capability Lattice** | **RATIFIED** — Security boundary for active code in PWADs | ✅ `make capability-check` gated | 2026-07-15 |
| **Mandate Governance Protocol** | **RATIFIED** — Amendment, exemption, conflict resolution | ✅ `make mandate-amendment-check` gated | 2026-07-15 |
| **Omega Kernel Architecture** | **RATIFIED** — `kernel/` vs `runtime/` boundary | ✅ `make kernel-import-check` gated | 2026-07-15 |
| SearXNG MCP | **Streamable HTTP on :8018** | ✅ Migration complete | 2026-07-13 |
| Omega Hub MCP | **Dual-transport** (SSE /sse + Streamable HTTP /mcp) on :8016 | ✅ Already dual | 2026-07-13 |
| Firecrawl MCP | **SSE on :8015** | ⏳ Needs Streamable HTTP migration | 2026-07-13 |
| Local inference ratio | **TARGET: ≥80%** (configurable gate, default OFF) | 🟡 Aspirational | 2026-07-13 |
| **KV Cache Quantization** | **LOCKED: q8_0 on CPU (Zen 2)** — No Flash Attention/GPU required | ✅ Research complete | 2026-07-13 |
| **YouTube Researcher V2** | **9-Layer Temporal Knowledge Observatory** — L1-L9 complete, 15 contract tests pass | ✅ Operational | 2026-07-13 |
| **Session Namespace Isolation** | **DESIGN COMPLETE (D-290)** — MIAP-wired session-scoped directories | 🟡 5 preconditions, 5 critical fixes from Nemotron review | 2026-07-18 |
| **MIAP Phase 0** | **PLANNED (D-291)** — ReplayMode, Two-Log, IntentionValidator, CheckFunctions, LiteTopic | 🟡 6 sessions estimated | 2026-07-18 |
| **MACP Alignment** | **PLANNED (D-292)** — Hivemind handoffs with `macp_mode` for interoperability | 🟡 Aligns with IETF draft-li-dmsc-macp-05 | 2026-07-18 |
| **Experience Repository** | **PLANNED (D-294)** — AgentRR-style L0→L1→L2 distillation via Scribe | 🟡 Trace-to-eval loop (D-295) | 2026-07-18 |
| **D-298 Decision Workspace** | **GROUNDED MEDITATION COMPLETE** — T0+T1-core verdict (7h), 23 decisions cataloged, Grok CLI handoff submitted | ✅ 102 files committed at 3542188, ho_749ed27155cd | 2026-07-19 |
| **D-300 Autonomous Meditation** | **PRODUCT DELIVERED** — 7-stage pipeline, `pip install omega-meditation`, OpenCode integrated, 15 L3 principles | ✅ Engine core + standalone package + 9 docs + 3 skills | 2026-07-19 |
| **D-301 MaKaLi Parallel Council** | **RATIFIED** — 5-session T0 spec, 13 gaps resolved, 35+ sources, Carmack S3 review 10/10 | ✅ 1639-line spec, hierarchical orchestration, two modes | 2026-07-19 |
| **D-302 CPR** | **RATIFIED** — 7 projects with CONTEXT.md one-turn hydration | ✅ Registry = infrastructure, not documentation | 2026-07-19 |
| **D-303 Headless Subagent Pool** | **PLANNED** — 24 accounts (8 Grok + 8 Copilot + 8 Cline) as unified compute | 🟡 Routing matrix: Deep Research→Cline, Web Search→Grok, Code Gen→Copilot | 2026-07-19 |
| **D-304 Antigravity Two-Track** | **PLANNED** — Track 1: Antigravity Tools (today) | Track 2: Omega-Vault provider (D-299) | 🟡 WARP Pool (3 IPs) for OCZ + Omega-Vault for AGY = complementary rate-limit keys | 2026-07-19 |
| **D-305 Hive Evolution** | **ARCHITECTURE DESIGNED** — Hivemind → Hive (cranium rat collective consciousness) | 🟡 5 layers, 7 sprints, Researcher Phase 1 critical path | 2026-07-19 |
| **D-306 Arch Soul Integration** | **DESIGN COMPLETE** — Nameless One's journey externalized as sovereign architecture | 🟡 24 entities = incarnations, Mandates = regret-prevention physics, Qliphoth = Fortress of Regrets | 2026-07-19 |
| **D-307 Torment WAD** | **SCAFFOLD DEFINED** — Living philosophy engine: Nameless One entity, companions, factions, Hive as coordination | 🟡 Awaiting Researcher Phase 1-4 for parameterization | 2026-07-19 |
| **D-308 Ubuntu 25.10 Toolchain Verification** | **P0 GATE TRIGGERED** — 30 claims verified, 13 actionable changes (7 refuted, 6 corrected). Critical path update required before Phase 2. | 🚨 **BLOCKING** — Kernel 6.17, no free-threaded Python, no distro packages for uv/ruff/pyright/llama-cpp-python/ollama/sqlite-vec, AppArmor breaks rootless podman, dbus-broker not default until 26.10 | 2026-07-19 |

---

## §3 Core Subsystems

| Subsystem | Module | Status | Description |
|-----------|--------|--------|-------------|
| **Oracle** | `src/omega/oracle/` | ✅ Operational | Intent detection, entity routing, Iris speculative decode |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | ✅ Operational | YAML-backed entity CRUD, auto-scaffolds sovereign workspaces |
| **Model Gateway** | `src/omega/oracle/model_gateway.py` | ✅ Operational | 8-backend provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock). P3 fixed graceful fallback + path/spec resolution |
| **Memory Store** | `src/omega/memory_store.py` | ✅ Operational | Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector search |
| **Vector Store** | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE | `IVectorStoreAdapter` impl: sqlite-vec (FTS5 + vec0 + SQL edges). PRAGMA SSOT converged: cache_size 32MB, wal_autocheckpoint 500 |
| **Config Resolver** | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE | Pure Path constants, lazy `get_active_iwad()`, single source of truth for all WAD paths |
| **Hybrid Search** | `src/omega/memory/hybrid_search.py` | ✅ D-283 Phase 1 COMPLETE | RRF k=60 fusion of FTS5 + vector results. 20 contract tests + 8 RRF math vectors |
| **Recall Store** | `src/omega/memory/recall.py` | 🟡 D-283 Phase 2 DESIGN COMPLETE | Quality-weighted warm memory tier with power-law decay. 27/29 tests pass |
| **MIAP** | `src/omega/coordination/miap.py` | ✅ MERGED | Multi-Instance Agent Protocol for context collision prevention. 13 tests |
| **Soul Utils** | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE | Multi-path soul context extractor for 31 entities |
| **WAD Loader** | `src/omega/oracle/wad_loader.py` | ✅ Operational | V2 schema with heritage fields. Sovereign WAD Protocol (SWP) pending |
| **Ingestion Pipeline** | `src/omega/ingestion/` | ✅ Operational | T1→T2→T3 tiered extraction, TriangulationVerifier, CAS |
| **Sovereign Sieve (Standalone)** | `packages/omega-sieve/` | ✅ v0.1.0 | `pip install omega-sieve` — T1(Trafilatura)→T2(Surgical)→T3(Crawl4AI) |
| **Document Reader (Standalone)** | `scripts/universal_doc_reader.py` | ✅ v1.0.0 | Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml |
| **Observability** | `src/omega/observability.py` | ✅ Operational | Trace IDs, event logging, fine-tuning dataset collection |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Operational | 6 MCP tools for cross-agent coordination, workspace locks, live feeds |
| **Hive (NEW)** | `src/omega/hive/` | 🟡 Design Complete | 5-layer collective consciousness: Sensorium, Thought Transmission, Neural Synchrony, Territorial Instinct, Incarnation Engine. Hivemind API compatible. |
| **Arch Soul (NEW)** | `data/entities/arch/` | 🟡 Design Complete | User's sovereign journey externalized: 24 entity facets = Nameless One incarnations, Mandates = regret-prevention physics, Qliphoth = Fortress of Regrets, Death/Rebirth = session lifecycle hooks |
| **CLI** | `src/omega/cli/oracle_cli.py` | ✅ Operational | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version) |
| **Resource Guard** | `src/omega/oracle/resource_guard.py` | ✅ Operational | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | ✅ Operational | Zen 2 compilation flags, KV cache sizing, speculative decode tuning |

---

## §4 Key Files (Source of Truth)

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` (this file) | System state SSOT — read first |
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws (M1-M23) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap (active) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions (active index) |
| `CREDITS.md` | id Software heritage attribution (active) |
| `docs/strategy/HMC_STRATEGIC_PLAN.md` | 4-mind council roadmap (Quad-Forge) |
| `docs/strategy/D281_PHASE_II_IV_EXECUTION.md` | D-281 Phase II-IV execution plan |
| `docs/archive/coordination/` | Historical session records |
| `data/entities/kali/session_gnosis.md` | Kali's session anchor (M15) |
| `data/coordination/ACTIVE_SPRINT.json` | HMC-SPRINT-04 active sprint config |
| `.opencode/anchored-summary.md` | Post-compaction recovery state |
| `.opencode/agents/grok_cli.md` | Grok CLI sovereign agent (Consulting Cloud Mind) |
| `docs/strategy/SOUL_ARCHITECTURE_V2.md` | Soul Architecture v2.0 (supersedes v1.0) |
| `docs/strategy/PWAD_CAPABILITY_LATTICE.md` | PWAD security capability model |
| `docs/strategy/MANDATE_GOVERNANCE_PROTOCOL.md` | Mandate amendment & exemption process |
| `docs/strategy/OMEGA_KERNEL_ARCHITECTURE.md` | Kernel/Runtime boundary spec |
| `docs/strategy/NEMOTRON3_ULTRA_BRIEFING.md` | Master strategy synthesis (D258-D263) |
| `docs/architecture/SOVEREIGN_BUS_SPEC.md` | Reconstructed event bus spec |
| `docs/research/R_PWAD_SCHEMA_JEM_RESEARCH_20260715.md` | Jem's 2026 PWAD SOTA research |
| `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20260717.md` | Grok's web research brief |
| `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` | 3-tier knowledge gap matrix |
| `docs/strategy/MEDITATE_MIAP_WIRE_SYNTHESIS_20260718.md` | 13-voice meditation synthesis on session isolation |
| `docs/strategy/NEURON3_REVIEW_MIAP_WIRE_20260718.md` | Nemotron 3 Ultra independent review + web research |
| **NEW**: `data/coordination/HIVE_EVOLUTION_ARCHITECTURE_20260719.md` | Hive architecture: 5 layers, 7 sprints, Hivemind compatibility |
| **NEW**: `data/coordination/ARCH_SOUL_NAMELESS_ONE_INTEGRATION_20260719.md` | Arch Soul = Nameless One externalized: death/rebirth, regret, companions |
| **NEW**: `data/coordination/RESEARCH_BRIEF_TORMENT_HIVE_20260719.md` | 4-phase Researcher dispatch for Torment lore parameterization |
| **NEW**: `data/entities/roc_racoon/workspace/mining_reports/TORMENT_PLANESCAPE_ARCHAEOLOGICAL_REPORT_20260719.md` | Complete local Torment inventory: 12 files, 15 lore elements, 8 mappings |

---

## §5 Platform Distinction

The Omega Engine is runtime-agnostic. Any MCP client can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## §6 References

| Document | Purpose |
|----------|---------|
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap (active) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions (active index) |
| `CREDITS.md` | id Software heritage attribution (active) |
| `docs/archive/coordination/` | Historical session records |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-07-19 | Version: v1.5.0 | Tests: 1398 passing (27/29 recall tbd) | SSOT: ~450 lines | Sessions: D-281 Substrate Repair COMPLETE | D-282 sqlite-vec Strike 10 COMPLETE | D-283 Phase 2 RecallStore DESIGN COMPLETE | D-298 Decision Workspace GROUNDED MEDITATION COMPLETE (T0+T1-core verdict, 23 decisions) | HMC Quad-Forge COMPLETE (Kali/Roc/Researcher/Grok CLI) | MIAP merged | **D-305 Hive Evolution ARCHITECTURE DESIGNED** | **D-306 Arch Soul Integration DESIGN COMPLETE** | **D-307 Torment WAD SCAFFOLD DEFINED** | Commit 3542188 (102 files) | ho_749ed27155cd submitted to Grok CLI | Net acceleration: ~120h by parallel fleet dispatch*