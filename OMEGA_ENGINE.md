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
- **Engine = Pure Runtime; WAD = Cosmology.** The Engine is a universal, opinion-free runtime. Each WAD supplies its own cosmology (entities, traits, governance, guidance) via Base IWAD + PWADs. **Users never fork core code** — they add layers. This is the deathless continuity substrate.
- **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-doc-reader`, `omega-meditation`) for community use.
- **Universal Reflection Substrate**: ONE foundational engine with infinite customizable layers (WADs), each custom to how a user understands their own sovereign journey. The ANAi Stack (Tarot/Nodes/Ma'at) and the Torment Stack (Hive/Nameless One/Sigil) are *two expressions of the same architecture* — proving the WAD customization power. Every user gets their own cosmology; the engine provides the deathless continuity substrate.

---

## §2 Current State (2026-08-28)

| Metric | Value | Status | LAST_VERIFIED | PROBE_COMMAND |
|--------|-------|--------|---------------|---------------|
| **Strategy SSOT (long-horizon)** | **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` v5.2** + `STRATEGY_CORPUS_MAP.md` | ✅ Ark remains long-horizon law | 2026-07-30 | `head -5 docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` |
| **Sprint control (near-term)** | **`PUBLIC-DEBUT-01`** — `data/coordination/ACTIVE_SPRINT.json` + `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` (P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1) | ✅ ACTIVE; UNOVERENGINEER-01 **SUPERSEDED** for sprint control (DOC-1, 2026-08-17) | 2026-08-17 | `cat data/coordination/ACTIVE_SPRINT.json` |
| **UO-4 Doc Sanity** | **COMPLETE** — PART 1 archival (67 files) + PART 2 web reconciliation (Phase 3/4 docs) + core strategy docs freshened (Pillar→Node, co-equal MaKaLi) | ✅ Freeze **LIFTED** (DOC_SANITY_COMPLETE met 2026-08-07) | 2026-08-07 | `cat data/coordination/ACTIVE_SPRINT.json` |
| **Phase D gate** | Mechanical **PASS 11/11** · Operational **NO-GO** (C-3/W-1/G-1) | 🟡 Dual-layer — see verdict | 2026-07-30 | `python scripts/verify_phase_d_gate.py` · `cat data/coordination/PHASE_D_GATE_VERDICT_20260730.md` |
| Tests | Focused **27 passed** (vault+property+hivemind 2026-07-30) · Full suite **1706 collected** (make test timeout risk) | ✅ Focused green; full suite needs longer budget | 2026-07-30 | `pytest tests/test_vault_integrity.py tests/property/ tests/test_hivemind.py -q` |
| Mandates | **28 (M1-M28)** | ✅ All enforced (v3.8.0) | 2026-09-20 | `grep -c "^### [0-9]" SOVEREIGN_MANDATES.md` |
| **Mandate Compliance** | **25/27 FULL (92%)** — 0 Partial, 2 Fail | ✅ M5, M11 fixed via wrapper (EXIT trap + DB integration) | 2026-07-30 | `grep -r "M5\|M11" SOVEREIGN_MANDATES.md \| head -5` |
| Fleet | **13 agents (cap 14 per M10)** | ✅ Clean | 2026-08-22 | `ls .opencode/agents/ \| wc -l` |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 | `ls config/wads/ \| wc -l` |
| **Third-Party Registry** | **18/19 repos cloned** — wave-0: 4/4, wave-1: 5/5, wave-2: 6/6, wave-3: 1/4 | ✅ waves 0-2 complete | 2026-07-18 | ⚠️ `data/coordination/THIRD_PARTY_REGISTRY.yaml` **no longer exists** — historical row, re-derive before citing |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 | `grep -r "\[id-soft:" src/ \| wc -l` |
| Shared modules | **1** (`omega-meditation` — local editable only) | ✅ 0 on PyPI | 2026-08-08 | `pip list \| grep omega-meditation` |
| **Foundation Stabilization** | **HISTORICAL** — Gate Α/Β done; not current sprint | 📦 Superseded by PUBLIC-DEBUT-01 | 2026-08-17 | `cat data/coordination/ACTIVE_SPRINT.json` |
| **Memory ADR (ADR-001)** | **RATIFIED** — sqlite_policy.py SSOT, 4 PRAGMA profiles | ✅ Gate Γ criterion met | 2026-07-20 | `head -30 src/omega/memory/sqlite_policy.py` |
| **C-0.5 Soul distillation hook** | **SCRAPPED per Carmack Verdict 2026-07-30** — Regex-based L1/L2/L3 extraction was fortune-cookie generation. Now: minimal timestamp write + codex refresh (~40 lines, no false promises). Agents write their own lessons. That works. | ✅ M5/M11 compliant | 2026-07-30 | `.opencode/wrapper.sh` + `.opencode/hooks/session_end.py` |
| **Nemotron 3 Ultra Streaming Fix** | **PIVOTED TO HUMAN-IN-THE-LOOP** — Auto-retry plugin removed (blinded agents). Implemented `error-capture.ts` and `awareness.ts` plugins. Subagent errors now pause the session and notify parent agent via Hivemind. Agents now have real-time event stream awareness. | ✅ M25 Streaming Resilience (via observability) | 2026-07-30 | `.opencode/plugin/error-capture.ts` + `.opencode/plugin/awareness.ts` |
| **Antigravity OAuth** | **PARTIAL** — Plugin present; auth often **API-key only**; re-login may be required for Path B | 🟡 G-1b path | 2026-07-22 | `opencode run -m google/antigravity-gemini-3-flash "Reply PONG" 2>&1 \| head -3` |
| **Gemma 4 31B free workhorse** | **DEAD for fat OpenCode** — free-tier input TPM **16k** since **2026-07-15** | 🚨 **G-1 P0** — billing/OAuth **or G-1e local GGUF** | 2026-07-30 | see critical-path + Cline ops results |
| **WARP Proxy Pool (W-1)** | **PARTIAL 1/3** — SOCKS **8083** listening; 8081/8082 down; ns-prep@1/2/3 active; node units flaky; SystemCallFilter fix applied | 🟡 Bridges + canary still open | 2026-07-30 | `ss -lntp \| rg '808[123]'` |
| **Circuit Breakers** | **~17** `class.*Breaker` hits in src/+mcp_servers (was underestimated as 6) · HealthMonitor remains intended canonical | 🟡 Un-overengineering Phase 1 → pybreaker | 2026-07-30 | `rg -n 'class.*Breaker' src/ mcp_servers/ --glob '*.py' \| wc -l` |
| **C-3 Restic backup** | PATH drop-in **FIXED**; timer **enabled+active**; oneshot **FAILED** (`OMEGA_VAULT_PASSPHRASE` / `.env.backup` missing); restic **0.17.3** at `~/.local/bin` | 🟡 Architect secrets required | 2026-07-30 | `systemctl is-enabled omega-restic-backup.timer; journalctl -u omega-restic-backup.service -n 20` |
| **MCP pin (CG-01)** | pyproject `mcp>=1.28.1,<2` · venv **1.28.1** · SDK **v2.0.0 stable 2026-07-28** = P0 migration debt (Hub still `mcp.server.fastmcp`) | 🟡 Pin holds; migrate scheduled | 2026-07-30 | `.venv/bin/pip show mcp \| rg Version` |
| **Doc hygiene** | Coordination/sprint thrash; Cline **DOC_SANITY** handoff ready (1M context) | 🟡 In flight | 2026-07-30 | `cat data/coordination/CLINE_DOC_SANITY_HANDOFF_20260730.md \| head -30` |

### Active Deferred Items
| Item | Status | Details | LAST_VERIFIED |
|------|--------|---------|---------------|
| **VaultCore (src/omega/vault/)** | **EXEC-PARTIAL** | Module present; backup cannot unlock without passphrase; gate V-1 may false-PASS via `pytest\|tail` | 2026-07-30 |
| **MCP v2 migration** | **P0 DEBT** | Prefer external FastMCP (SearXNG precedent); Hub+Firecrawl still SDK v1 FastMCP | 2026-07-30 |
| **C-3 Backup operational** | **BLOCKED** | Timer OK; need `.env.backup` + successful oneshot + ≥1 snapshot | 2026-07-30 |
| Firecrawl MCP | ⏳ Streamable HTTP / FastMCP align with Hub migrate | SSE on :8015 | 2026-07-30 |
| Local inference ratio ≥80% | 🟡 Aspirational | Gate configurable, default OFF | 2026-07-22 |
| Session Namespace Isolation (D-290) | 🟡 Design complete | 5 preconditions pending | 2026-07-22 |
| MIAP / Hive Evolution (D-291, D-305) | ⏸ **CANCELLED per D-495** (un-overengineering) — Hivemind shipped | Do not re-open without production bug | 2026-07-30 |
| Headless Subagent Pool (D-303) | 🟡 Planned | Frozen until doc sanity / later gate | 2026-07-30 |
| **G-1 Workhorse continuity** | 🚨 **P0 ACTIVE** | billing/OAuth **or G-1e** local Gemma 4 GGUF (32GB CPU viable) | 2026-07-30 |
| **W-1 WARP pool** | 🟡 **PARTIAL** | 1/3 SOCKS; bridges for 1/2; canary timeout | 2026-07-30 |
| Arch Soul / Torment WAD (D-306/307) | 🟡 Design/scaffold | Not current sprint | 2026-07-22 |
| **D-308 Ubuntu 25.10** | 🚨 **P0 GATE** residual | Kernel/AppArmor/Podman notes remain. **OS deployment target = Ubuntu 24.04 LTS or 26.04 LTS** (25.10 is EOL — not a support target) | 2026-07-22 |
| **V-10 AppArmor** | 🚨 **GAP** | Containers unconfined — no `podman` AppArmor profile applied to running containers | 2026-08-07 |
| **V-9 IA2 envelope** | ⚠️ **GAP** | `_meta` envelope in `mcp_core/compliance.py` lacks freshness/signature check | 2026-08-07 |

### Recent Milestones (Completed)
D-281 Substrate Repair ✅ | D-282 sqlite-vec Strike 10 ✅ | D-283 Mnemosyne ✅ | MIAP merged ✅ | D-298 Decision Workspace ✅ | D-300 Omega-Meditation ✅ | D-301 MaKaLi Council ✅ | D-302 CPR ✅ | **MaKaLi Apex Mind deployed (Sophia replaced)** ✅ | All Phase 5 ratified items ✅ | **C-10 Admission Control** ✅ | **C-2' RAM Truth** ✅ | **C-4a MCP Audit** ✅ | **C-5 MaKaLi Routing** ✅ | **C-6' Breaker Unification** ✅ | **C-1' SoulStore** ✅ | **UO-4 Doc Sanity COMPLETE (PART 1 + PART 2 + core docs freshened)** ✅
*(For full details see `scripts/codex/ENGINE_CONDENSED.md` §5)*

---

## §3 Core Subsystems

| Subsystem | Module | Status | Description |
|-----------|--------|--------|-------------|
| **Oracle** | `src/omega/oracle/` | ✅ Operational | Intent detection, entity routing, Iris speculative decode |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | ✅ Operational | YAML-backed entity CRUD, auto-scaffolds sovereign workspaces |
| **Model Gateway** | `src/omega/oracle/model_gateway.py` | ✅ Operational | **12-provider fabric, 10 enabled** — local: `native-gguf` (primary, llama-cpp-python) + `ollama`; cloud: antigravity, google, google-compat, openrouter, opencode-zen, cline, anthropic, xai; disabled: `lmster` (de-scoped to a post-release update), `mock` (test-only). S3 fixed graceful fallback + path/spec resolution |
| **Memory Store** | `src/omega/memory_store.py` | ✅ Operational | Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector search |
| **Vector Store** | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE | `IVectorStoreAdapter` impl: sqlite-vec (FTS5 + 7 per-model vec0 collections + SQL edges). PRAGMA SSOT converged: cache_size 32MB, wal_autocheckpoint 500 |
| **Vector Adapter Pattern** | `src/omega/memory/vector_adapters.py` | ✅ Operational | `IVectorStoreAdapter` ABC with 3 implementations: `SQLiteVecAdapter` (core), `MemoryVectorAdapter` (fallback), `QdrantAdapter` (deprecated heritage ref) |

> **Vector Store Decision (UO-4)**: `sqlite-vec` is the **SINGLE Core store** for the engine. It is native on SQLite (FTS5 + 7 per-model vec0 collections + SQL edges) and powers GraphRAG natively. **Qdrant** is an **optional WAD adapter only** — implements `IVectorStoreAdapter` for stacks that opt into external vector infrastructure. No new core dependency on Qdrant/FAISS/PostgreSQL is permitted.
>
> **Current Unified Fabric** (D-1024-DIM-NATIVE): canonical `omega_vec_qwen_1024` (1024-dim native, Qwen3-Embedding-0.6B) + `omega_vec_library_1024` + FTS5 BM25 + RRF fusion (k=60) via `HybridSearchEngine`. Pre-D-1024 tiers (`omega_vec_nomic_768/512/256`, `omega_vec_minilm_384`, `omega_vec_static_64`) retained as deprecated read targets only (Step 19 re-embed / Step 20 removal). The Gemma-era `omega_vec_gemma_768` primary is superseded by Qwen. All working in production.
>
> **Qdrant Migration Strategy**: Implement `QdrantAdapter` as a **swappable backend** implementing `IVectorStoreAdapter` (not a replacement). Add config toggle in `config/jit_rag.yaml`: `vector_store: {type: qdrant|sqlite_vec}`. Migrate primary collection (`omega_vec_qwen_1024` — canonical under D-1024, supersedes Gemma-era `omega_vec_gemma_768`) first, parity test per collection (≥95% recall), keep SQLite-vec as hot standby for 30 days.
| **Config Resolver** | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE | Pure Path constants, lazy `get_active_iwad()`, single source of truth for all WAD paths |
| **Hybrid Search** | `src/omega/memory/hybrid_search.py` | ✅ D-283 Phase 1 COMPLETE | RRF k=60 fusion of FTS5 + vector results. 20 contract tests + 8 RRF math vectors |
| **Recall Store** | `src/omega/memory/recall.py` | 🟡 D-283 Phase 2 DESIGN COMPLETE | Quality-weighted warm memory tier with power-law decay. 27/29 tests pass |
| **MIAP** | `src/omega/coordination/miap.py` | ✅ MERGED | Multi-Instance Agent Protocol for context collision prevention. 13 tests |
| **Soul Utils** | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE | Multi-path soul context extractor for 31 entities |
| **WAD Loader** | `src/omega/oracle/wad_loader.py` | ✅ Operational | V2 schema with heritage fields. Sovereign WAD Protocol (SWP) pending |
| **Ingestion Pipeline** | `src/omega/ingestion/` | ✅ Operational | T1→T2→T3 tiered extraction, TriangulationVerifier, CAS |
| **Document Reader (Standalone)** | `scripts/universal_doc_reader.py` | ✅ v1.0.0 | Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml |
| **Observability** | `src/omega/observability.py` | ✅ Operational | Trace IDs, event logging, fine-tuning dataset collection |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Operational | 6 MCP tools for cross-agent coordination, workspace locks, live feeds |
| **MaKaLi Apex Mind (NEW)** | `config/wads/_omega_default/entities.yaml` | ✅ Deployed | Mastermind agent — deep research, genius blueprinting, high-level strategy, philosophical deep dives. Replaces Sophia (Akashic Record) in default WAD. NOT a builder — directs ground troops (Kali, Lilith, Maat, Nodes, Carmack). |
| **Arch Soul (NEW)** | `data/entities/arch/` | 🟡 Design Complete | User's sovereign journey externalized: 24 entity facets = Nameless One incarnations, Mandates = regret-prevention physics, Qliphoth = Fortress of Regrets, Death/Rebirth = session lifecycle hooks |
| **CLI** | `src/omega/cli/oracle_cli.py` | ✅ Operational | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version) |
| **Resource Guard** | `src/omega/oracle/resource_guard.py` | ✅ Operational | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **Admission Controller** | `src/omega/oracle/admission_controller.py` | ✅ C-10 COMPLETE | LocalInferenceAdmission singleton, Semaphore(1) + OOMProtector integration, fail-fast to cloud |
| **OOM Protector** | `src/omega/oracle/oom_protector.py` | ✅ C-2' COMPLETE | Three-signal fusion (PSI + MemAvailable + cgroup), 5-tier decision logic |
| **Health Monitor** | `src/omega/oracle/health_monitor.py` | ✅ C-6' COMPLETE | Canonical circuit breaker factory (get_breaker), CUSUM + sliding-window modes, 5-state FSM |
| **SoulStore** | `src/omega/soul_store.py` | ✅ C-1' COMPLETE | Atomic file writer: tempfile → write → fsync → os.replace → fsync parent. 4-layer guarantee: AtomicVisibility, CrashDurability, WriterExclusion (flock), IntegrityDetection (.bak rotation) |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | ✅ Operational | Zen 2 compilation flags, KV cache sizing, speculative decode tuning |
| **Hardware Profile** | `config/hardware_profile.yaml` (generated by `scripts/detect_hardware_profile.py`) | ✅ UO-4 | **Actual UMA carve-out = 8GB** (512MB VRAM + 7.75GB GTT) — NOT 12GB. Ryzen 7 5700U Zen 2, 2 CCXs, ~8GB free RAM. CPU topology/threads detected dynamically from /proc/meminfo + /sys. |

---

## §4 Key Files (Source of Truth)

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` (this file) | **System state SSOT** — metrics & subsystems |
| `SOVEREIGN_MANDATES.md` | 27 Constitutional Laws (M1–M27) |
| **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`** | **Strategy & roadmap SSOT (v5.1 Unified)** |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained agent strategy preservation map |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Fleet teamwork playbook (how agents coordinate) |
| `docs/strategy/STRATEGY_INDEX.md` | Doc hierarchy (Layer 0–4) |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D detail (amended by Ark §3.2) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `AGENTS.md` | OpenCode agent how-to |
| `docs/decisions/PIVOT_LOG.md` | Immutable decisions index |
| `CREDITS.md` | id Software heritage attribution |
| `data/coordination/SESSION_ANCHOR.md` | Session recovery |
| `.opencode/anchored-summary.md` | Post-compaction recovery state |
| `.opencode/agents/makali.md` | MaKaLi Apex Mind agent |
| `.opencode/agents/grok_cli.md` | Grok CLI Consulting Cloud Mind |
| `docs/archive/strategy/2026-07-21/` | Archived roadmaps + Ark v4.4 body |
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Superseded tactical draft (trail only) |
| `docs/architecture/PROVIDER_FABRIC_RUNTIME.md` | Provider fabric runtime design (UO-4 Phase 3) |
| `docs/architecture/SOVEREIGN_FLYWHEEL_SECURITY.md` | Sovereignty flywheel + security (UO-4 Phase 4) |
| `docs/strategy/PHASE_0_VERIFICATION_REPORT_20260807.md` | V-1..V-10 verification probes (UO-4 Phase 4) |
| `docs/architecture/MEMORY_SUBSYSTEM_DESIGN.md` | Memory subsystem design (UO-4 Phase 2) |
| `docs/architecture/SYSTEMD_DEPLOYMENT_GUIDE.md` | systemd deployment guide (UO-4 Phase 2) |
| `docs/architecture/SOVEREIGN_WAD_PROTOCOL.md` | Sovereign WAD protocol (UO-4 Phase 2) |
| `docs/architecture/GUIDANCE_SET_SCHEMA.md` | Guidance set schema (UO-4 Phase 2) |
| `docs/strategy/UNOVERENGINEERING_PLAN.md` | Temple cleansing sprint (5 phases, ~5,500 lines) |

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
| `SOVEREIGN_MANDATES.md` | 27 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | **Strategy SSOT v5.1** |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained preservation map |
| `docs/strategy/STRATEGY_INDEX.md` | Documentation hierarchy |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | Decision history |
| `CREDITS.md` | id Software heritage |
| `docs/archive/strategy/2026-07-21/` | Archived strategy corpus |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-08-28 | Version: v1.8.9 | Ark SSOT: SOVEREIGN_ARK_BLUEPRINT v5.2 (vision, read-only) | Sprint: PUBLIC-DEBUT-01 (DEBUT_REMEDIATION_MANUAL_20260817) | P0-1d in_progress (SECURITY_AUDIT residual) | P0-2 test suite COMPLETE (1768/1768) | Mechanical lint pass COMPLETE (255 files, e2c16d3c, pre-Manual) — full P2 lint campaign PARKED per Manual until post-DEL-1 | DOC-1 stamps LANDED | PUB-1 allowlist drafted | INST-1 in_progress (maat) | DEL-1 in_progress | Mandate compliance: 27 laws (M26/M27 added 2026-08-14) | G-1/W-1/V-1/SDP/NL-1 PARKED | Team-Study #1 COMPLETE (converged R1, 10 rulings stamped — data/coordination/teamstudy_20260823/FINAL_SYNTHESIS.md); tracking-system closeout refined: pre-commit framework install pending per Ma'at F1 ordering, AST freeze gate supersedes wc-l, explicit evidence field day one, verify-mandate-claims P0, backfill = roc table × Lilith 23-cluster enumeration*