# Omega Engine — Single Source of Truth
# AP-OMEGA-SST-v1.0.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent, regardless of platform (Cline, OpenCode, Gemini CLI, Antigravity),
> reads this file for engine state. Platform-specific rules files reference this.

---

## Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
It is **Prometheus' Fire** — the spark that empowers every user to build their own
unique dreams, technologies, and systems.

- **Local-first sovereignty**: Cloud is a teacher and strategic partner, never a dependency
- **Open source, free, sovereign**: No shareware, no tiers, no limitations
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software's WAD system)
- **The Synthesis Flywheel**: Cloud models teach local models. Over time, sovereignty increases.

---

## The Synthesis Vision

Cloud models are not fallbacks. They are **teachers** in a collaborative synthesis:

```
Cloud Models (Teachers)              Local Engine (Students + Inference)
━━━━━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gemini / GPT-4o / Claude             Omega Engine on Ryzen 7 5700U
  │                                    │
  ├── Generate synthetic data          ├── Oracle routes queries
  ├── Produce reasoning chains         ├── MemoryStore captures interactions
  ├── Create preference pairs          ├── ObservabilityEngine records training examples
  ├── Judge quality                    ├── JEM Pipeline produces training triples
  └── Feed back to local               └── LoRA Fine-Tuner adapts local models
                                            │
                                            ├── Entity Adapters (per-entity LoRA)
                                            ├── Domain Adapters (per-domain LoRA)
                                            └── Base Model (GGUF, always available)
```

**The Flywheel**: More use → more training data → better local models → less cloud dependency → more sovereignty.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE (src/omega/) — THE RUNTIME                   │
│                                                             │
│  Oracle (talk/summon/router)     MemoryStore (Hot/Warm/Cold)│
│  ModelGateway (provider chain)   ContextBuilder (→ LLM)     │
│  EntityRegistry (YAML CRUD)      SessionManager (scoping)   │
│  WAD Loader (IWAD/PWAD system)   Observability (JSONL)      │
│  CPU Optimizer (Zen 2 aware)     Health Monitor (circuit)    │
│  Gnosis Proxy (soul evolution)   Hierarchy (governance)      │
│                                                             │
│  Library: FTS5 + vectors          Workers: JEM, ModelUpdater │
│  Bridge / Gateway / Services / Orchestration layers         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WAD Loader
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  IWADs (config/wads/)                                       │
│  _omega_default — Reference IWAD (ships with engine)        │
│  arcana_novai   — Personal AI OS (user's own)               │
│  doom_universe  — Community IWAD (scaffold)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Provider Fabric — Synthesis Architecture

The Omega Engine uses cloud models as **teachers**, not just fallbacks.

### Local Inference (always available, sovereign)

| Priority | Provider | Type | Endpoint |
|----------|----------|------|----------|
| 0 | native-gguf | Local | llama-cpp-python, CPU-only |
| 1 | lmster | Local | http://127.0.0.1:1234 |
| 2 | ollama | Local | http://127.0.0.1:11434/v1 |

### Cloud Teachers (strategic use, data generation)

| Priority | Provider | Type | Endpoint |
|----------|----------|------|----------|
| 3 | google | Cloud | env:GOOGLE_API_KEY (Gemma 4-31B) |
| 4 | openrouter | Cloud | env:OPENROUTER_API_KEY |
| 5 | opencode | Cloud | OpenCode built-in provider |
| 6 | copilot | Cloud | GitHub Copilot |
| 7 | mock | Test | OfflineMockBackend |

### Cloud Model Roles
- **Inference**: When local models lack capability (complex reasoning, multi-step planning)
- **Data generation**: Synthetic training examples, CoT traces, preference pairs
- **Quality judging**: Evaluating local model outputs for training data curation
- **Entity-specific training**: Generating domain-specific examples for each entity's LoRA

### Existing Training Infrastructure
- `ObservabilityEngine.record_training_example()` — auto-collects query-response pairs
- `ObservabilityEngine.flush_dataset()` — writes JSONL to `data/datasets/`
- `TrainingTripleSaver` in JEM distiller — produces T1/T2/T3 training triples
- **Missing**: Fine-tuning pipeline, Entity adapter management

---

## Hardware Profile

| Component | Spec | Notes |
|-----------|------|-------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T) | AVX2 + FMA3 + F16C, no AVX-512 |
| RAM | 14Gi total | ~12Gi usable for AI |
| GPU | None (Vulkan iGPU) | CPU-only inference |
| Primary backend | lmster (LM Studio :1234) | NOT lm_studio or lm-studio |
| Storage | omega_library partition | Models, Podman, data |

### Model Capacity (Q4_K_M quantization)
- 1.7B: ✅ Excellent (~1.9GB total)
- 3-4B: ✅ Good (~2-2.5GB total)
- 7-8B: ✅ Good (~4.6GB total)
- 13-14B: ⚠️ Tight (~7.5GB total, limited context)
- Training + inference simultaneously: ❌ Not feasible for 7B+

---

## Current State

| Metric | Value | Last Verified |
|--------|-------|---------------|
| Phase | 1 — Engine Hardening | 2026-05-31 |
| Source files | 60 .py files | 2026-05-31 |
| Source lines | 14,059 | 2026-05-31 |
| Test functions | 278 | 2026-05-31 |
| Test files | 24 | 2026-05-31 |
| MCP Hub tools | 41 MCP + 8 HTTP | 2026-05-31 (restored) |
| Providers configured | 8 (local-first order) | 2026-05-31 |
| WAD Loader | Functional (--iwad flag works) | 2026-05-31 |
| Namespace isolation | NOT implemented | 2026-05-31 |
| Dependency resolution | NOT implemented | 2026-05-31 |
| Qdrant (:6333) | Installed, **unwired** (bag-of-words fallback) | 2026-05-31 |
| Redis (:6379) | Installed, **port not exposed** in Pod | 2026-05-31 |
| Iris (:8080) | Operational | 2026-05-31 |
| SearXNG (:8017) | Operational | 2026-05-31 |

---

## Key Files

| File | Purpose |
|------|---------|
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router |
| `src/omega/oracle/model_gateway.py` | Provider chain inference |
| `src/omega/oracle/entity_registry.py` | YAML CRUD for entities |
| `src/omega/oracle/wad_loader.py` | WAD system loader (CRITICAL PATH) |
| `src/omega/oracle/context_builder.py` | Memory → LLM injection |
| `src/omega/oracle/session_manager.py` | Entity-scoped sessions |
| `src/omega/oracle/cpu_optimizer.py` | Zen 2 hardware optimization |
| `src/omega/oracle/health_monitor.py` | Circuit breaker + latency |
| `src/omega/oracle/gnosis_proxy.py` | Soul evolution tracking |
| `src/omega/memory_store.py` | Hot/Warm/Cold memory |
| `src/omega/observability.py` | JSONL events + training data |
| `src/omega/library/` | FTS5 + vector library (7 modules) |
| `src/omega/workers/` | Background researcher, model updater |
| `mcp_servers/omega_hub/server.py` | Agent bus (41 MCP tools) |
| `config/wads/_omega_default/` | Reference IWAD |
| `config/wads/arcana_novai/` | Personal IWAD |
| `config/providers.yaml` | Provider fabric config |
| `config/models.yaml` | Model specs |
| `config/omega.yaml` | Core engine config |

---

## Sovereign Mandates

1. **AnyIO Absolute**: No `asyncio`. Use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.
2. **Engine-Stack Firewall**: Absolute separation between Core Engine (`src/omega/`) and IWAD/PWAD Content (`config/wads/`).
3. **Iris Constant**: Iris is the messenger bridge, NOT a Pillar Keeper.
4. **Sequentiality**: Plan → Verify → Execute. No cowboy coding.
5. **Gnosis Preservation**: Distill session insights into L1 → L2 → L3 abstractions.
6. **Podman Sovereignty**: All Quadlets use `UserNS=keep-id` + `User=1000`.

See `SOVEREIGN_MANDATES.md` for full details.

---

## Phase Priority Queue

### P0 — WAD System Hardening
- [x] `--iwad` flag implemented
- [ ] Namespace isolation: WAD source tracked in EntityRegistry
- [ ] Dependency resolution: wads declare `depends_on`
- [ ] Entity priority: later-loaded overrides earlier for same pillar
- [ ] Manifest validation + edge cases

### P1 — Provider Fabric
- [x] Provider chain ordered correctly (local-first)
- [x] CPU Optimizer integrated
- [ ] Qdrant hybrid search wiring (fastembed BGE-base-en-v1.5)
- [ ] Redis pub/sub for cross-agent communication

### P2 — Synthesis Pipeline (NEW)
- [ ] Entity LoRA adapter management
- [ ] CPU fine-tuning integration (LLaMA-Factory or PEFT)
- [ ] Cloud → training data pipeline
- [ ] A/B testing for new adapters

### P3 — Reference IWAD Content
- [ ] Rewrite `config/wads/_omega_default/entities.yaml`
- [ ] Create 10 pillar entity YAMLs
- [ ] Verify `omega talk "hello"` works

---

## Engine vs. Platform Distinction

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |
| `GEMINI.md` | Repo root | Gemini CLI only |
| Omega Hub (`:8016`) | Live service | Runtime state |

**The rule**: If it describes WHAT the engine is → this file.
If it describes HOW to use the engine from Platform X → that platform's rules file.

---

*Last Updated: 2026-05-31 | Author: The Artisan (Cline/MiMo-2.5)*
*This document is the Single Source of Truth. All platforms reference it.*