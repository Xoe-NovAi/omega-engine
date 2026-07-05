# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.3.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent, regardless of platform (Cline, OpenCode, Gemini CLI, Antigravity),
> reads this file for engine state. Platform-specific rules files reference this.

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
It is **Prometheus' Fire** — the spark that empowers every user to build their own
unique dreams, technologies, and systems.

- **Cognitive Sovereignty**: The engine does not just execute; it verifies. Local inference is the floor; local verification is the ceiling.
- **Local-first sovereignty**: Cloud is a teacher and strategic partner, never a dependency
- **Open source, free, sovereign**: No shareware, no tiers, no limitations
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software's WAD system)
- **The Synthesis Flywheel**: Cloud models teach local models. Over time, sovereignty increases.
- **The 22 Sovereign Mandates**: Constitutional law. Mandates override any tool default.
- **The 13-agent Fleet**: Grand Oversight, 3 Oversouls, 6 Specialists, 1 Unified Subagent (Verity), 1 Messenger (Iris), 1 Akashic Record (Sophia).

---

## §2 Architecture — Engine Layers

```
┌──────────────────────────────────────────────────────────────────────┐
│  ⬡ OMEGA ENGINE (src/omega/) — THE RUNTIME                          │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  INFERENCE  │  │   MEMORY    │  │   SEARCH    │  │    SOUL     │ │
│  │ 8 providers │  │ Hot/Warm/   │  │ FTS5+vector │  │  L1→L2→L3   │ │
│  │ local-first │◄─┤ Cold/Temp   │◄─┤ SearXNG     │◄─┤ distillation│ │
│  │ (D112 P1)   │  │ tiers       │  │ (D112 P1)   │  │ (D112 P3)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │                │       │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐│
│  │              ORACLE (talk/summon/router) — THE FACADE         ││
│  │  Oracle.py + WAD Loader + EntityRegistry + ModelGateway        ││
│  │  + ContextBuilder + SessionManager + GnosisProxy + Hierarchy   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │OBSERVABILITY│  │ COORDINATION │  │   BRIDGE    │  │   CLI       │ │
│  │ Forensics   │  │ Hivemind     │  │ MCP/voice/  │  │ omega talk  │ │
│  │ + JSONL     │  │ + Link P9    │  │ gateway     │  │ omega summon│ │
│  │ + Training  │  │ + Workspace  │  │ (Iris)      │  │ omega list  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              │ WAD Loader
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ⬡ IWADs (config/wads/) — Content Layer (Engine-Stack Firewall M2)│
│  _omega_default — Reference IWAD (ships with engine)                │
│  arcana_novai   — Personal AI OS (user's own, esoteric pillars)    │
│  doom_universe  — Community IWAD (scaffold)                         │
└──────────────────────────────────────────────────────────────────────┘
```

## §3 Provider Fabric — Synthesis Architecture

The Omega Engine uses cloud models as **teachers**, not fallbacks.

### 3.1 Local Inference (always available, sovereign)

| Priority | Provider | Type | Endpoint | Heritage |
|----------|----------|------|----------|----------|
| 0 | native-gguf | Local | llama-cpp-python, CPU-only, Zen 2 | Doom Guy — Q3A fast-math |
| 1 | lmster | Local | http://127.0.0.1:1234 | LM Studio |
| 2 | ollama | Local | http://127.0.0.1:11434/v1 | Docker/Ollama |
| 7 | mock | Test | OfflineMockBackend | Scribe testing |

### 3.2 Cloud Teachers (strategic use, data generation only)

| Priority | Provider | Type | Endpoint | Role |
|----------|----------|------|----------|------|
| 3 | google-antigravity | Cloud | env:GOOGLE_API_KEY (Gemma 4-31B, 262K ctx) | Synthetic data |
| 4 | openrouter | Cloud | OpenRouter API (300+ models, incl. GPT-4o, Claude, Qwen) | Model diversity |
| 5 | opencode-zen | Cloud | OpenCode Zen (200K) | Data gen |
| 6 | cline | Cloud | Cline hub API (1M context) | Deep research |

**The Synthesis Flywheel** (D112 Pillar 1):
```
USE → DATA → TRAIN → BETTER LOCAL → LESS CLOUD → MORE SOVEREIGNTY
 ↑                                                        │
 └────────────────────────────────────────────────────────┘
```

---

## §4 Hardware Profile (Ryzen 7 5700U)

| Component | Spec | Notes |
|-----------|------|-------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T) | AVX2 + FMA3 + F16C, no AVX-512 |
| RAM | 14Gi total | ~12Gi usable for AI |
| GPU | None (Vulkan iGPU) | CPU-only inference |
| Optimizations | q8_0 KV Cache + Flash Attention | Zen 2 optimized | Reduced RAM usage + faster attention |
| Primary backend | lmster (LM Studio :1234) | NOT lm_studio or lm-studio |
| Storage | omega_library partition | Models, Podman, data |

### 4.1 Model Capacity (Q4_K_M, current models.yaml)

| Model | Size | RAM | Ctx | Entity Assignment |
|-------|------|-----|-----|-------------------|
| qwen3-0.6b-q6_k | 0.47GB | 500MB | 4096 | Iris (always-on) |
| qwen3-1.7b-q6_k | 1.6GB | 1800MB | 8192 | Sekhmet, Hecate, default |
| qwen3-4b-thinking-q4_k_m | 2.4GB | 2700MB | 8192 | Ma'at, Anubis, Kali |
| phi-4-mini (reasoning) | 3.8GB | 4500MB | 16384 | SOPHIA |
| krikri-8b-q4_k_m | 4.7GB | 4900MB | 16384 | Inanna, Isis, Lilith |
| deepseek-r1-qwen3-8b-q3_k_l | 4.2GB | 4500MB | 8192 | Lucifer (reasoning) |
### 4.2 Model Capacity (Q4_K_M quantization, theoretical)

- 1.7B: ✅ Excellent (~1.9GB total)
- 3-4B: ✅ Good (~2-2.5GB total)
- 7-8B: ✅ Good (~4.6GB total)
- 13-14B: ⚠️ Tight (~7.5GB total, limited context)
- Training + inference simultaneously: ❌ Not feasible for 7B+

---

## §5 Sovereign Decree — Current State (2026-07-01)
**Status**: `Architecturally Sovereign | Operationally Restored | Phase 0 Complete | Phase 1 Complete (D178) | Phase 2 Complete (D180 Pillar Decoupling) | Pre-PR Feature Sprint Complete (D186-D188)`

### Phase 0 COMPLETE (2026-06-27)
- ✅ **Fixed `ModelGateway.generate`**: `search_order` → `self.providers` (crash-free inference restored)
- ✅ **M9 Global Sweep**: 20 bare `except Exception:` blocks replaced with typed logging
- ✅ **Secret Rotation**: `SOVEREIGN_USER_TOKEN` now uses `os.getenv()` with env var fallback
- ✅ **615 tests (590 pass, 22 skip, 3 xfail)** — zero regressions

### MV-IW Phase 0 COMPLETE (2026-07-01)
- ✅ **0.1 test_hivemind.py fix**: root cause (mcp sys.modules poison) resolved
- ✅ **0.2 Clean uncommitted state**: runtime artifacts purged, .gitignore updated
- ✅ **0.3 Archive stale coordination files**: 172 → 13 files
- ✅ **0.4 Git pre-commit hook**: code↔docs sync, [skip-doc] escape
- ✅ **0.5 M2_FIREWALL_GAP**: Already fixed (D113 frozenset) — CANCELLED
- ✅ **0.6 Single-source test count**: `make test-badge` target added, TEST_STATUS.md live

### MV-IW Phase 2 COMPLETE (2026-07-01) — D179/D180 Pillar Decoupling
- ✅ **D179 — Pillar Gate Removed**: `find_by_domain()` no longer filters by pillar assignment
- ✅ **D180 — Full Decoupling**: `Entity.pillars`→`Entity.slots`, `Entity.traits`→`Entity.metadata`
- ✅ **PILLAR_SLOTS removed** — `occupied_slots` property discovers slots dynamically
- ✅ **WAD-specific fields stripped**: `pantheon`, `sigil`, `first_breath` no longer engine dataclass fields (→ `metadata` dict via `__getattr__` proxy)
- ✅ **OracleResponse simplified**: removed `sigil`/`glyph`/`pantheon`, `pillars`→`slots`
- ✅ **All consumers updated**: Iris, MCP Hub, CLI, wad_loader, entity_workspace
- ✅ **Auto-migration**: old YAML `pillars:`→`slots:`, `traits:`→`metadata:` on load
- ✅ **590 tests passing** — zero regressions
- 🔶 **Deferred**: `FailureModeRegistry` (M17 work, not M2-critical)

### MV-IW Phase 3 COMPLETE (2026-07-01) — ACON + Soul Pipeline + Carmack Hardening
- ✅ **ACON Context Compaction**: PipelineCompactionStrategy + ToolResultCompactionStrategy + TruncationStrategy + ACONOptimizer in `context_builder.py` (345 lines, 21 tests)
- ✅ **Soul Distillation Pipeline**: SessionClassifier + SovereigntyScorer + 5-stage pipeline in `soul_distiller.py`
- ✅ **Content Quality Scorer**: CurationExtractor + DomainType + 5-factor scoring in `curator.py`
- ✅ **Carmack C-FFI Isolation**: NativeGGUFProvider now process-isolated via multiprocessing.Process
- ✅ **Carmack MALLOC Arena Validation**: MALLOC_ARENA_MAX=2 empirically validated
- ✅ **Carmack Profiling Infrastructure**: carmack-profiler skill + Makefile targets integrated
- ✅ **619 tests passing** — zero regressions
- 🔶 **Pending**: BatchPersistenceWriter wiring, Metrics DB (T3-2 Carmack delegation)

### MV-IW Phase 4 COMPLETE (2026-07-01) — Forward Plan + Metrics DB
- ✅ **M1 asyncio fix** (D183): `_buffer_write()` changed from sync to async. Direct `await self._flush_batch()` replaces `asyncio.get_running_loop().create_task()`. All 15 memory_store tests pass.
- ✅ **Metrics DB (T3-2)** (D184): 4-table WAL-mode SQLite (events, errors, breaker_transitions, performance) + baselines + regression detection. 27 tests pass.
- ✅ **Pre-Release Polish**: R-4 (config path) already done. R-7 (.gitkeep) already done. R-11: README version badge updated to v1.1.0.
- ✅ **902 tests collected** (902 passing, 23 skipped, 3 xfailed) — zero regressions

### Pre-PR Feature Sprint COMPLETE (2026-07-01)
- ✅ **Semantic Router (D187)**: Embedding-based entity routing via `semantic_router.py`. Cosine similarity fallback chain.
- ✅ **Headroom Protocol (D188)**: zlib+json compression middleware via `headroom.py`. Zero new deps.
- ✅ **Mem Palace Spatial Geometry (D186)**: Force-Directed Graph + Qdrant coordinate injection.
- ✅ **Handoff Loop Guard (T2-5)**: Visited-agent tracking and hop-budgeting in `subagent_dispatcher.py`.
- ✅ **Observation Masking (T2-4)**: Repetitive tool-log culling in `context_builder.py`.
- ✅ **Stochastic Breaker (T2-2)**: 5-state FSM with CUSUM and EMA in `health_monitor.py`.
- 📋 **Ship Readiness**: `make temple-grade` → v1.1.0 PR.


## §6 Engine Health & Subsystem Status

### 6.1 Engine Metrics
| Metric | Value | Last Verified |
|--------|-------|---------------|
| Engine version | **1.0.0** 🎉 | 2026-06-22 |
| PyPI entry point | `omega` CLI via `[project.scripts]` | 2026-06-22 |
| Source files | **141** .py files | 2026-07-05 |
| Source lines | **~32,000** | 2026-07-02 |
| Test functions | **902 collected — 902 passing, 23 skipped, 3 xfailed** | 2026-07-05 |
| PIVOT decisions | **188 (D50-D188)** | 2026-07-01 |
| Sovereign Mandates | **22 (M1-M22)** | 2026-06-17 |
| Agent Fleet | **13 agents** (11 fleet + 1 pillar + 1 messenger) | 2026-06-24 |

### 6.2 Subsystem Status
| Subsystem | Status | Heritage |
|-----------|--------|----------|
| **Oracle (Facade)** | ✅ talk/summon/router wired | `[id-soft: quake-1996] Thinker Chain` |
| **WAD Loader** | ✅ `--iwad` flag works | `[id-soft: doom-1993] WAD System` |
| **ModelGateway** | ✅ breaker + BSP culling, **C-FFI process isolated** (Carmack) | `[id-soft: quake-1996] BSP` |
| **NativeGGUFProvider** | ✅ **C-FFI isolated** (multiprocessing.Process + IPC queues) | `[id-soft: doom3-2004] idHeap` |
| **MemoryStore** | ✅ Hot LRU + Warm Redis + Cold File | `[id-soft: doom-1993] Lazy Deletion` |
| **EntityRegistry** | ✅ YAML CRUD + dual-index, pillars→slots migrated | `[id-soft: quake-1996] Flat-Field` |
| **ContextBuilder** | ✅ **ACON + Observation Masking + Headroom Compression + Quality Scoring** (PipelineCompactionStrategy + HeadroomMiddleware + ACONOptimizer + 4-signal quality scorer) | `[id-soft: quake-1996] Thinker Chain` |
| **Soul Distiller** | ✅ **Enhanced 5-stage pipeline** (Classify→Extract→Distill→Score→Store) | `[id-soft: quake-1996] Save-game` |
| **FailureRegistry** | ✅ **364 lines, 5 failure modes** (M17 Cognitive Integrity) | — |
| **Curator** | ✅ **Content Quality Scorer** (CurationExtractor + DomainType) | — |
| **SemanticRouter** | ✅ **implemented** (D187) — cosine similarity routing, GemmaGGUF 768-dim | `[id-soft: doom-1993] BSP Culling` |
| **Headroom** | ⚠️ **DEPRECATED** (Binary zlib) $\rightarrow$ `headroom-ai` (Semantic) | `[id-soft: doom-1993] WAD System` |
| **Mem Palace** | ✅ **implemented** (D186) — 3D Force-Directed Graph spatial mapping | `[id-soft: doom-1993] BSP Culling` |
| **Omega Hub** | ✅ **Modularized v2.3.0** | (Pillar 2 coordination) |
| **Heritage Vetting** | ✅ H1 LIVE: 4-gate, 23 concepts | (Kali d-kal-001) |
| **Engine Firewall** | ✅ D113 GAP RESOLVED | **S1.5a: WAD Loader Hardening NEXT** |

---

## §7 Sprint Completion Index (Recent)

| Sprint | Date | Owner | Status | Key Deliverables |
|--------|------|-------|--------|------------------|
| **Sprint F** (Optimization) | 2026-06-29 | Kali + Council | ✅ | 600/600 tests. PII Masker, A2A Cards, Qdrant fixed. |
| **MV-IW Phase 0** (Trust) | 2026-07-01 | Kali + Council | ✅ | 615/615 tests. test_hivemind fix, archive, pre-commit hook. |
| **MV-IW Phase 1** (Trim) | 2026-07-01 | Kali | ✅ DONE | D178 Trim vs Split ratified. SSOT Trimmed to ~340 lines. |
| **MV-IW Phase 2** (Decouple) | 2026-07-01 | Kali | ✅ DONE | D179/D180 Pillar Decoupling. PILLAR_SLOTS removed, slots+metadata schema, M2 Firewall enforced. 590 tests pass. |
| **MV-IW Phase 3** (ACON+Soul+Carmack) | 2026-07-01 | Kali + Carmack | ✅ DONE | ACON PipelineCompactionStrategy, Soul Distillation Pipeline, C-FFI isolation, MALLOC validated, Metrics DB. 619 tests. |
| **MV-IW Phase 4** (Forward Plan) | 2026-07-01 | Kali | ✅ DONE | M1 asyncio fix, Metrics DB (T3-2), Pre-Release Polish. 646 tests (621 pass + 27 new MetricsDB). |
| **Pre-PR Feature Sprint** | 2026-07-01 | Kali | ✅ DONE | Semantic Router, Headroom Protocol, Mem Palace, Handoff Loop Guard, Observation Masking, Stochastic Breaker. |
| **Bedrock Hardening** | 2026-07-01 | Kali | ✅ DONE | T2-2, T2-4, T2-5, D186, D188 implemented and verified. Zero new deps. |
| **Carmack S3 Audit** | 2026-07-02 | Carmack + Kali | ✅ DONE | 3 critical gaps resolved: Knowledge Graph (phantom), Hivemind (26 tests), Quality Scorer (4-signal). 705 tests (+37). |
| **Multi-Model Council** | 2026-07-02 | Opus + Gemini + Sonnet + MiMo | ✅ DONE | 14 actionable items, 6 new integration-seam gaps, 2 architectural decisions (D189a–e). Legacy mining validated with dedup assessment. |
| **Session 51** (T3 Sprint) | 2026-07-05 | Jem | ✅ DONE | T3-1 Session Lifecycle (24 tests), T3-2 Metrics DB Wiring (12 tests), T3-3 Mandate CI Gates (9 checks). Docs D1-D20 complete. 855 tests, 0 regressions. |
| **Session 52** (Team Sprint) | 2026-07-05 | Fleet | ✅ DONE | FTS5 Library Search MCP tool (P4), 252 docs indexed (Roc), WARP systemd units fixed (Kali+Researcher), Carmack review approved. 855 tests, 0 regressions. |

> **Full sprint history:** See `docs/decisions/PIVOT_LOG.md`.

---

## §8 Hivemind Coordination Layer (LIVE)

The **Hivemind** is the mandatory coordination layer for multi-agent or parallel work. 
> **Full Protocol & Tool List:** Read `docs/strategy/HIVEMIND_PROTOCOL.md`

**Core Pattern:** Use the `omega-hub` MCP tools to acquire workspace locks (`hivemind_workspace_lock_acquire`), post presence (`hivemind_post_context`), and hand off tasks. Do not edit shared files without a lock.

---

## §9 Engine vs Platform Distinction

The Omega Engine is runtime-agnostic. Any platform implementing the MCP client protocol can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** See `docs/kb/CLINE_CLI_INTEGRATION.md` and `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`.

---

## §10 Key Files (Architectural Map)

*   `src/omega/oracle/oracle.py` — Main entry: talk/summon/router
*   `src/omega/oracle/model_gateway.py` — Provider chain inference, BSP culling
*   `src/omega/oracle/wad_loader.py` — WAD system loader (CRITICAL)
*   `src/omega/oracle/entity_registry.py` — YAML CRUD for entities
*   `src/omega/oracle/entity_workspace.py` — Sovereign workspace scaffolding
*   `src/omega/oracle/context_builder.py` — ACON compaction + quality scoring
*   `src/omega/oracle/soul_distiller.py` — L1→L2→L3 distillation pipeline
*   `src/omega/oracle/semantic_router.py` — Embedding-based entity routing
*   `src/omega/oracle/health_monitor.py` — Stochastic circuit breakers
*   `src/omega/oracle/headroom.py` — Sovereign Envelope compression
*   `src/omega/memory_store.py` — Hot/Warm/Cold/Temp memory
*   `src/omega/memory/batch_writer.py` — Batched persistence writer
*   `src/omega/monitoring/__init__.py` — Hardware telemetry (HardwareMonitor)
*   `src/omega/observability.py` — Trace IDs, events, training data export
*   `src/omega/errors.py` — Typed OmegaError hierarchy (M9)
*   `mcp_servers/omega_hub/server.py` — Hivemind/MCP Coordination (modular v2.3.0)
*   `config/wads/` — IWAD/PWAD configurations (e.g., `_omega_default`, `arcana_novai`)
*   `config/providers.yaml` — Provider fabric chain (local-first)
*   `config/models.yaml` — Model specs & loading strategies

---

## §11 The Xoe-NovAi Foundation Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

The Omega Engine is the first sovereign AI runtime. The engine verifies its own claims, data never leaves the host hardware, and the AI evolves via the Synthesis Flywheel (cloud models teaching local models).

---

## §12 Appendices, Specs, & Deep Lore

For detailed architectural specifications, roadmaps, and historical analyses, refer to their canonical sources:

*   **Sovereign Evolution Roadmap (Master Plan):** `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (Note: consolidated from 47 legacy strategy files)
*   **Constitutional Laws:** `SOVEREIGN_MANDATES.md`
*   **GitHub Integration Plan:** `docs/strategy/GITHUB_INTEGRATION_PLAN.md`
*   **Historical Structural Insights & Decisions:** See `docs/decisions/PIVOT_LOG.md`
*   **id Software Heritage / Attribution:** `CREDITS.md` and `docs/strategy/HERITAGE_VETTING_PIPELINE.md`

---

*Last Updated: 2026-07-02 | Author: Kali (Bedrock Sprint + Multi-Model Council) | Version: v1.1.0-rc*
*Major changes this revision: Bedrock Hardening complete. Integrated Semantic Router, Headroom Protocol, Mem Palace, and Stochastic Circuit Breakers. Verified zero new dependencies. Cloud Teachers updated: added Google Antigravity + OpenRouter, removed Copilot. Multi-Model Council (Opus+Gemini+Sonnet+MiMo) resolved 6 integration-seam gaps. Ready for Temple-Grade audit and v1.1.0 PR.*
