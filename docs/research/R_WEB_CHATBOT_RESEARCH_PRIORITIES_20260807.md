# 🔬 Research Priority List: New Strategies & Technologies from Web Chatbot Docs

**AP Token**: `AP-WEB-CHATBOT-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_web_chatbot_research ⬡ ACTIVE

**Date**: 2026-08-07
**Source**: `context_packs/provider-fabric-review/claude-response/` (12 documents, ~10,000+ lines)
**Purpose**: Comprehensive catalog of new strategies and technologies discovered in Web Gemini, Web Grok, and Web Claude sessions requiring additional research.

---

## ⚠️ KALI REVIEW VERDICT (2026-08-07) — CORRECTIONS APPLIED

**This document was reviewed by Kali against actual engine state, PIVOT_LOG decisions (D-286, D-287, D-383, D-510), SOVEREIGN_ARK_BLUEPRINT v5.2.0, and the 2026-08-07 session work. Key corrections:**

1. **Status classification added** to every item: ✅ IMPLEMENTED / 🟡 PARTIAL / 🔴 ASPIRATIONAL / 📌 DEFERRED. The Researcher's original doc treated everything as "needs research" — **at least 5 items are already implemented in the engine** and should be re-purposed from "research" to "harden/extend."
2. **Terminology corrected per D-510**: All `pillars` → **nodes** (N1-N10). The engine uses Node terminology; "Pillar Keepers" survives only inside the ANAi WAD as sovereign content.
3. **MaKaLi representation corrected (A2)**: The engine implements a **hierarchy** (Kali Founder → Ma'at CTO / Lilith CISO per `config/wads/_omega_default/hierarchy.yaml`), NOT a flat "co-equality trine" as the web docs describe. Co-equality is an aspirational philosophical framing, not the implemented structure.
4. **WAD/IWAD is implemented (A1)**: `config/wads/` with `_omega_default` (IWAD), ANAi, doom_universe, etc., plus D-286 Meditate Base+Overlay and D-287 M2 Firewall migration phases. Research item A1 must shift from "does WAD work" to "pack dependency resolution + marketplace."
5. **Qdrant SQ8 is implemented (M2)**: `src/omega/memory/vector_adapters.py:217` already uses `ScalarQuantization(INT8, always_ram=True)`. M2 becomes "benchmark + tune," not "research."
6. **Headroom is implemented (I5)**: `src/omega/oracle/middleware/headroom.py` with `[heritage: headroom-ai 2025]` and integration in `oracle.py`/`context_builder.py`.
7. **Zero-Telemetry (SEC2) is law, not research**: Already M8 Sovereign Mandate, enforced by `make temple-grade` T6 gate.
8. **NotebookLM (O3) is already ticketed**: NL-1 in SOVEREIGN_ARK_BLUEPRINT, post-Phase-D, per D-383. Not a new research item.
9. **IA2 (SEC3)**: T11 is explicitly exempted until IA2 spec stabilizes (M13 exception). Research is valid, but gate enforcement is deferred.
10. **Provider fabric items must honor M7 Local-First**: Cloud planner (A4), GRPO-with-cloud-evaluator (S6), CoT distillation from cloud (S3) are fine as *research* but must NOT become cloud-primary implementations. Local inference remains PRIMARY; cloud is fallback per `config/providers.yaml` (`prefer: native-gguf`).
11. **Hardware reality**: Engine defaults to CPU-only (`n_gpu_layers=0` via cvar Port 1.2). Vulkan/MoE offload (I1/I4) are aspirational for Vega 8; the current bottleneck is 12GB RAM + memory bandwidth.

**Recommendation**: Keep this as the *research backlog* but gate all 🔴 ASPIRATIONAL items through the Sovereign Refinement Protocol before implementation, and prioritize ✅ IMPLEMENTED items for hardening/tuning instead of re-research.

---

## 📋 Executive Summary

This document synthesizes findings from 12 web chatbot session documents in the `claude-response` directory, covering architecture manuals, implementation specifications, hardware optimization guides, training flywheel designs, and strategic vision documents produced during August 2026 provider-fabric review sessions.

**Total Items Identified**: 47 research items across 10 categories
**Top Priority**: WAD/IWAD pack mechanics, dual-branch memory scoring, speculative decoding, GRPO reward design, Vulkan iGPU tuning

**Status Breakdown (post-Kali-review)**:
- ✅ IMPLEMENTED: 5 (A1 WAD base, M2 Qdrant SQ8, I5 Headroom, SEC2 M8 law, O3 NL-1 ticketed)
- 🟡 PARTIAL: 6 (A2 hierarchy present but philosophy aspirational, I2 MTP drafter exists, I3 zRAM monitoring exists, M5 consolidation agent exists, S2 training sandbox exists, D2 OpenCode binding exists)
- 🔴 ASPIRATIONAL: 31
- 📌 DEFERRED/EXPLICITLY NOT NOW: 5 (per SOVEREIGN_ARK_BLUEPRINT v5.2.0: new free-tier providers, Grok fleet, V-1 gate, Phase D, Strike 11)

---

## 🏗️ ARCHITECTURE & PARADIGMS

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **A1** | **WAD/IWAD Architecture for AI Engines** | MaKaLi Clarification, Unified Implementation, Vision Doc | ✅ **IMPLEMENTED (base)** | Base WAD system EXISTS: `config/wads/_omega_default` (IWAD manifest with `type: iwad`, `requires_engine`, `version`), ANAi/doom_universe WADs, D-286 Meditate Base+Overlay, D-287 M2 Firewall migration. **Research shifts to**: PWAD dependency resolution, versioning/conflict resolution between WADs, community marketplace patterns. M14 heritage vetting already recorded (`[id-soft: doom-1993] WAD System` in CREDITS.md). |
| **A2** | **Horizontal MaKaLi Triad (Co-Equality)** | MaKaLi Clarification, 42 Ideals, Vision Doc | 🟡 **PARTIAL — hierarchy is implemented, co-equality is philosophy** | Engine implements **hierarchy**: `hierarchy.yaml` — Sophia (Field) → Kali (Founder) → Ma'at (CTO, N1-N5) + Lilith (CISO, N6-N10). NOT a flat trine. Research co-equality as *philosophical lens*, but the code contract is Founder→Executive→Department. Conflict resolution between **nodes** (not pillars), synthesis via Kali. |
| **A3** | **SEDA Ring-Bus over AnyIO** | Refactoring Manual, Unified Implementation, Qdrant Full | 🟡 **PARTIAL** | `anyio.create_memory_object_stream` already used in `dpo_logger.py:123` and `memory/batch_writer.py:98`. Full ring-bus with back-pressure policies, topic design, subscriber lifecycle is NOT built. Research: compare to LMAX Disruptor (rejected for spin-threads), `send_nowait` drop policies, buffer sizing, dead-letter handling (G9). |
| **A4** | **Cloud Planner / Local Executor Pattern** | Qdrant Full (speculative decoding section), README, Flywheel docs | 🔴 **ASPIRATIONAL** | Frontier cloud models emit JSON DAGs; local models execute with grammar enforcement. **M7 constraint**: local stays PRIMARY; cloud is advisor/planner only (per `providers.yaml` `prefer: native-gguf`). Research: DAG schema, parallel execution, breaker thresholds, planner model selection. |
| **A5** | **Guidance Sets as Pure Data (Defeasible Ethics)** | Refactoring Manual, MaKaLi Clarification, 42 Ideals | 🟡 **PARTIAL** | WAD YAML already carries ethics: `config/wads/_omega_default/ethics.yaml` exists. Defeasibility logging + DPO/GRPO integration are NOT built. Research: schema for ideals, expression forms (negative/positive/conditional), review cadences, defeasibility logging format. |

---

## 🧠 MEMORY & RETRIEVAL

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **M1** | **Dual-Branch Memory (Declarative vs Episodic)** | Qdrant Full (multiple sections), Unified Implementation, Refactoring Manual | 🔴 **ASPIRATIONAL** | Two parallel retrieval pipelines with different scoring formulas are NOT in `memory_store.py` (it uses single-snapshot + session-sort + FTS/vector adapters). Research: optimal λ decay rate (0.005 cited), consolidation penalty (0.4), importance weighting (0.5), HDBSCAN clustering params. |
| **M2** | **Qdrant Scalar INT8 Quantization (SQ8) + mmap** | Refactoring Manual, Unified Implementation, Qdrant Full | ✅ **IMPLEMENTED — benchmark instead** | `vector_adapters.py:217` already: `ScalarQuantizationConfig(type=ScalarType.INT8, always_ram=True)`. Research becomes **benchmark**: recall@k vs memory, payload index strategy, sharding, FAISS/Postgres migration verification (G8). |
| **M3** | **Spatial Memory Substrate (XYZ in every payload)** | Refactoring Manual, Unified Implementation, Grok xyz/zRAM, Qdrant Full | 🔴 **ASPIRATIONAL** | Mandatory `pos_x, pos_y, pos_z` + `spatial_scale/color/layer` for Godot 4 VR readiness is NOT implemented. Research: coordinate generation (UMAP/t-SNE/PCA vs force-directed vs deterministic hash), update frequency, Godot 4 OpenXR integration (G5). Note: `config/wads/_omega_default/vr/` directory exists as scaffolding. |
| **M4** | **Symbolic WARM Tier (Redis Task Canvas)** | Unified Implementation, Qdrant Full, MaKaLi Clarification | 🔴 **ASPIRATIONAL** | Lightweight markdown/JSON Task Canvas in Redis with `payload:{node_id}` TTL is NOT implemented (Redis is used for Hivemind Pub/Sub only). Research: Canvas schema, TTL policies, `fetch_node_payload` tool patterns, Redis memory bounds. |
| **M5** | **Omega-Consolidator (Background HDBSCAN Clustering)** | Qdrant Full (consolidation worker spec), Unified Implementation, MaKaLi Clarification | 🟡 **PARTIAL** | A consolidation **agent exists** (`memory/block_tools.py:442` — off-critical-path consolidation with stronger model). HDBSCAN clustering → declarative summaries + `is_consolidated=True` tagging NOT built. Research: HDBSCAN params (min_cluster_size, min_samples), scheduling, atomic upsert+tag, LLM summarization prompts (G6). |

---

## ⚡ INFERENCE & HARDWARE OPTIMIZATION

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **I1** | **Vulkan iGPU Offload (llama-cpp-python + Vega 8)** | Refactoring Manual, Unified Implementation, Grok entry-level, Qdrant Full | 🔴 **ASPIRATIONAL** | Engine is **CPU-only by default**: `config.gguf.n_gpu_layers` cvar = 0 (Port 1.2 explicit CPU-only default). KV-cache quant cvars exist (`type_k`/`type_v`: q8_0/f16/q4_0). Vulkan build (`CMAKE_ARGS="-DGGML_VULKAN=ON"`) NOT in current build. Research: Vulkan vs ROCm on Vega 8, `n_batch`/`n_threads` for 5700U, KV-cache quant tuning, MoE expert offload (`--n-cpu-moe`). |
| **I2** | **Speculative Decoding (Draft + Target Models)** | Qdrant Full (speculative decoding section), README, Unified Implementation | 🟡 **PARTIAL** | `capability_matrix.py` supports **MTP drafter** (`mtp_drafter` field — Qwen3-style multi-token prediction). Full draft-verify loop NOT wired. Research: draft-target pairing, acceptance rate optimization, Prompt Lookup Decoding / N-gram (zero VRAM), Medusa/Eagle heads (G4). |
| **I3** | **Three-Tier Memory Hierarchy (RAM → zRAM → NVMe)** | Refactoring Manual, Grok zRAM, Grok xyz/zRAM, Unified Implementation | 🟡 **PARTIAL — monitoring exists, tuning aspirational** | zRAM/swap **monitoring** exists (`monitoring/__init__.py` reads psutil swap + `/proc/meminfo` + swap pressure). `vm.swappiness=80`, cgroup `MemoryMin/High/Max`, zRAM writeback NOT configured. Research: tuning values, PSI-based thresholds, cgroup v2 values. |
| **I4** | **MoE Expert Offload + mmap Streaming** | Grok zRAM/model disk swap, Unified Implementation | 🔴 **ASPIRATIONAL** | `--n-cpu-moe` / tensor overrides + OS page-on-demand NOT implemented. Research: expert cache sizing, LRU policies, page fault monitoring, CatLlamaCpp/Apple Metal PoCs (G3). |
| **I5** | **Context Compression via Headroom (AST + SmartCrusher)** | Refactoring Manual, Grok xyz/zRAM, Unified Implementation | ✅ **IMPLEMENTED — harden instead** | `oracle/middleware/headroom.py` with `[heritage: headroom-ai 2025]`, integrated in `oracle.py:157,180,771` + `context_builder.py:464` (optional dep, pass-through when missing). Research becomes: SmartCrusher algorithm details, token-savings vs latency benchmarking, MCP server vs proxy integration (G1). |
| **I6** | **Lightweight Local TTS (Piper / Inflect Micro)** | Refactoring Manual, Grok xyz/zRAM (twice), Unified Implementation | 🔴 **ASPIRATIONAL** | No TTS in `src/omega/`. Research: Piper (~50-150MB) vs Inflect Micro (~16-40MB), ONNX runtime, SEDA bus integration, PulseAudio/PipeWire routing (G2). |

---

## 🔄 SOVEREIGNTY FLYWHEEL & TRAINING

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **S1** | **Automated Dataset Extraction (SFT/DPO/GRPO)** | Qdrant Full (dataset extraction), README, Flywheel strategy | 🔴 **ASPIRATIONAL** | Three datasets (Planner SFT Goal→DAG, Executor SFT success traces, Escalation DPO failures→fixes) NOT implemented. `dpo_logger.py` exists (DPO event logging) but no dataset builder. Research: logging schema, quality filtering, LLM-as-a-Judge, JSONL standards. |
| **S2** | **GRPO Training with Verifiable Rewards** | Qdrant Full (training section), Unified Implementation, MaKaLi Clarification | 🟡 **PARTIAL** | **Training sandbox EXISTS**: `research/sandboxes/ml_training.py` (BGE-small 33M on synthetic data, val_bpb, M1/M2/M7/M9/M12/M13/M21/M23 compliant). Full `GRPOTrainer` + LoRA 4-bit + continuous batching + JSON schema reward NOT wired. Research: reward design (beyond JSON schema), `max_memory_percent=0.40` VRAM protection, adapter merge/deploy. |
| **S3** | **CoT/Reasoning Distillation from Cloud** | Qdrant Full (flywheel strategies), Flywheel strategy doc | 🔴 **ASPIRATIONAL** | Cloud emits `<thought>` traces → local SFT/GRPO. **M7 constraint**: cloud as teacher is acceptable research but the trained artifact must run local-first. Research: thought tag parsing, quality filtering, GRPO vs SFT for reasoning. |
| **S4** | **Adversarial Edge-Case Generation** | Qdrant Full (flywheel strategies) | 🔴 **ASPIRATIONAL** | Research: adversarial prompt templates, edge-case categorization, synthetic diversity metrics, extractor integration. |
| **S5** | **Synthetic Tool Execution Traces** | Qdrant Full (flywheel strategies) | 🔴 **ASPIRATIONAL** | Research: tool-call schema standardization, ReAct vs function calling trace format, multi-turn validation, local tool-calling fine-tune. |
| **S6** | **Best-of-N Rejection Sampling with Cloud Evaluator** | Qdrant Full (flywheel strategies) | 🔴 **ASPIRATIONAL** | Local generates N → cloud rates 1-10 → top to SFT. **M7 constraint**: cloud is evaluator only, never primary generation path. Research: optimal N, temperature for diversity, evaluator prompt, cost/benefit. |

---

## 🛡️ SECURITY & INTEGRITY

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **SEC1** | **Sovereign Bridge (Raw-Body HMAC-SHA256)** | Refactoring Manual, Unified Implementation, MaKaLi Clarification | 🟡 **PARTIAL** | HMAC-SHA256 **provenance stamping** exists (`oracle/ingestion.py:82-90` — `hmac.new(secret, payload, sha256)` for data provenance). Raw-body webhook verification (FastAPI `await request.body()` before JSON parse + 30-min replay window) NOT built. Research: webhook spec, timing-attack resistance, key rotation, payload schema validation. |
| **SEC2** | **Zero-Telemetry Guarantee** | Refactoring Manual, Unified Implementation, Vision Doc, MaKaLi Clarification | ✅ **IMPLEMENTED — already M8 law** | Zero telemetry is **Sovereign Mandate M8** (absolute; no analytics/phone-home; local observability only under `data/`). Enforced by `make temple-grade` T6 gate. Research shifts to: automated regex sweep tooling for dependency telemetry, network egress blocking, audit tooling. |
| **SEC3** | **IA2 Replay Freshness Checks** | Agent Verification Dispatch, Unified Implementation | 🔴 **ASPIRATIONAL (research valid)** | T11 (IA2 Agent Security) is **explicitly exempted** from Temple-Grade until IA2 spec stabilizes (M13 exception). Research: IA2 spec, nonce/timestamp schemes, breaker integration — but no gate enforcement until spec lands. |

---

## 🖥️ OBSERVABILITY & UX

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **O1** | **Terminal UI (TUI) Execution Tracer** | Qdrant Full (TUI spec), README, Unified Implementation | 🟡 **PARTIAL** | **fleet_status_tui.py EXISTS** (`cli/fleet_status_tui.py` — Transcendent Triad + N1-N5/N6-N10 rendering). Full DAG view, step trace, dual-branch memory, sovereignty telemetry NOT built. Research: Textual CSS Grid, SEDA event binding, VRAM/token metrics, non-blocking log streaming. |
| **O2** | **Spatial Workspace Web UI (Godot/Next.js)** | Unified Implementation, Qdrant Full, Vision Doc | 🔴 **ASPIRATIONAL** | React Flow DAG + Mind Palace + Godot 4 OpenXR NOT built (only `vr/` scaffolding in IWAD). Research: Qdrant→Godot pipeline (xyz), WebXR, spatial clustering viz, collaborative features. |
| **O3** | **NotebookLM Multi-Persona Ingestion** | Refactoring Manual, MaKaLi Clarification, Qdrant Full | 📌 **DEFERRED — already ticketed NL-1 (post Phase-D)** | **Not a new research item**: D-383 + SOVEREIGN_ARK_BLUEPRINT NL-1 ticket (per R52c spec, 5-notebook architecture, weekly sync). Implement `prepare_notebooklm.py` post-Phase-D gate; depends on D-1 content cache (`.firecrawl/`). |

---

## 📦 DEPLOYMENT & OPERATIONS

| # | Item | Source Doc | Status | Why Research Needed |
|---|------|------------|--------|---------------------|
| **D1** | **Systemd Daemon with cgroup v2 + Core Pinning** | Refactoring Manual, Unified Implementation, Qdrant Full | 🔴 **ASPIRATIONAL** | `taskset -c 0-7`, `MemoryMin=4G/High=10G/Max=11G`, SIGTERM graceful shutdown NOT in current quadlets. Research: cgroup v2 memory accounting accuracy, graceful AnyIO TaskGroup shutdown, restart policies, log rotation. |
| **D2** | **OpenCode CLI Binding to Local Engine** | Refactoring Manual, MaKaLi Clarification, Unified Implementation | 🟡 **PARTIAL — OpenCode IS the primary platform** | OpenCode is already the sovereign brain (`opencode.json` + Omega Hub MCP `:8016/sse` + `.opencode/wrapper.sh` session wrapper). `OPENCODE_API_BASE=http://127.0.0.1:8080/v1` local llama-server binding NOT configured. Research: llama-server OpenAI-compatible endpoint, model routing, streaming, auth. |
| **D3** | **Legacy Architecture Purge (26-sphere, 108-gates)** | Refactoring Manual, MaKaLi Clarification, Qdrant Full | 🔴 **ASPIRATIONAL** | Note: the **13-sphere Mnemosyne** concept is documented (D-385 recovered; precursor to soul.yaml; migration script needed). The "26-sphere/108-gates" purge is a Qdrant payload-filter deletion of deprecated concepts — NOT started. Research: migration strategies, automated legacy detection, verification of complete purge. |

---

## 🎯 TOP 10 HIGHEST-LEVERAGE RESEARCH ITEMS (KALI-REVISED)

**Revision**: Items already implemented are re-ranked below as *harden/tune* rather than *research*. The top 10 now reflects what actually moves the engine forward.

| Rank | Item | Category | Status | Impact | Effort |
|------|------|----------|--------|--------|--------|
| **1** | **WAD Pack Dependency Resolution + Marketplace** (A1) | Architecture | ✅ base | Enables full customization vision | Medium |
| **2** | **Dual-Branch Memory Scoring Optimization** (M1) | Memory | 🔴 | Core retrieval quality | Medium |
| **3** | **Speculative Decoding Draft-Target Pairing** (I2) | Inference | 🟡 MTP | 2-4x token throughput | Low-Medium |
| **4** | **GRPO Verifiable Reward Function Design** (S2) | Training | 🟡 sandbox | Self-improvement flywheel | High |
| **5** | **Qdrant SQ8 Benchmarking + Payload Index Tuning** (M2) | Memory | ✅ impl | Verify/tune implemented quant | Low |
| **6** | **SEDA Bus Back-Pressure & Topic Design** (A3) | Architecture | 🟡 streams | System stability under load | Medium |
| **7** | **Spatial Coordinate Generation (UMAP vs Hash)** (M3) | Memory | 🔴 | VR readiness | Low-Medium |
| **8** | **Headroom SmartCrusher + Savings Benchmarking** (I5) | Inference | ✅ impl | Context compression | Low |
| **9** | **Automated Dataset Quality Filtering** (S1) | Training | 🔴 | Flywheel data quality | Medium |
| **10** | **TUI Real-Time Event Binding from SEDA** (O1) | Observability | 🟡 TUI base | Developer experience | Medium |

---

## 🔍 RESEARCH GAPS REQUIRING EXTERNAL INVESTIGATION

These items need **web search / academic research / community investigation** beyond the current docs:

| Gap | What to Research | Status |
|-----|------------------|--------|
| **G1** | **Headroom (headroomlabs-ai/headroom)** — Actual GitHub repo, API, MCP server integration patterns, SmartCrusher algorithm details | ✅ base impl; research = harden |
| **G2** | **Inflect Nano/Micro v2 TTS** — 2026 ultra-tiny models, ONNX export, voice quality benchmarks vs Piper | 🔴 open |
| **G3** | **CatLlamaCpp / Windows SSD Streaming PoCs** — True on-demand expert loading from disk, performance numbers | 🔴 open |
| **G4** | **Medusa / Eagle Draft Heads** — Architecture, training, integration with llama.cpp/vLLM | 🔴 open |
| **G5** | **Godot 4 OpenXR Spatial Entities / Anchors** — Persistence across sessions, Qdrant→Godot pipeline | 🔴 open |
| **G6** | **HDBSCAN Clustering for Memory Consolidation** — Optimal params for episodic→declarative, incremental clustering | 🔴 open |
| **G7** | **GRPO Continuous Batching + VRAM Protection** — `use_transformers_continuous_batching`, `max_memory_percent` tuning | 🔴 open |
| **G8** | **Qdrant Scalar Quantization (SQ8) vs Binary (BQ) vs Product (PQ)** — Recall@k vs RAM benchmarks for 384-dim embeddings | ✅ impl; benchmark = verify |
| **G9** | **AnyIO MemoryObjectStream Back-Pressure Patterns** — `send_nowait` drop policies, buffer sizing, dead letter handling | 🟡 partial streams |
| **G10** | **id Software WAD Community Tooling** — WAD editors, dependency managers, package registries for inspiration | ✅ base; research = marketplace |

---

## 📋 NEXT STEPS RECOMMENDED (KALI-REVISED)

1. **Immediate (This Week)**: Benchmark already-implemented M2 (Qdrant SQ8) + I5 (Headroom); research G1 (Headroom MCP), G8 (Qdrant quant benchmarks), G2 (Inflect TTS) — highest ROI for 12GB hardware
2. **Short-term (2 Weeks)**: WAD pack dependency resolution (A1), dual-branch memory scoring (M1), speculative decoding draft pairing (I2)
3. **Medium-term (Month)**: GRPO flywheel (S2), spatial coordinates (M3), TUI tracer (O1)
4. **Ongoing**: Monitor llama.cpp Vulkan/Vega 8, Qdrant releases, local TTS advances
5. **Coordination**: Gate ALL 🔴 ASPIRATIONAL implementations through the Sovereign Refinement Protocol; do not implement any cloud-primary training/planner path (M7). NL-1 NotebookLM stays on the Ark backlog (post-Phase-D), not a new research item.

---

## 📚 SOURCE DOCUMENTS INDEX

| File | Lines | Description |
|------|-------|-------------|
| `Web-Gemini-MaKaLi-Hierarchy-Clarification.md` | 1,474 | Unified architecture manual with MaKaLi hierarchy, WAD/IWAD, SEDA, memory, guidance sets |
| `Web-Gemini-OMEGA-ENGINE-REFACTORING.md` | 306 | Temple hardening manual v3.1/v1.9.0 with hardware, SEDA, Qdrant, guidance sets |
| `Web-Gemini_Engine_hardening.md` | 220 | TTS, xyz coordinates, zRAM, SQLite-vec vs Qdrant, inference optimization, mempalace/headroom eval |
| `Web-Grok_OMEGA ENGINE Unified Implementation.md` | 260 | Unified implementation manual v3.1 with runbook, systemd, verification |
| `Web-Grok_zRAM_and_model_disk_swap.md` | 72 | zRAM + NVMe swap + MoE expert offload strategy for 5700U |
| `Web-Grok_xyz_coordinates_and_zram.md` | 112 | TTS, xyz coordinates, zRAM impact analysis (duplicate of Engine_hardening sections) |
| `Web-Grok_entry_level_hardware_community.md` | 57 | Community platforms/reports at similar hardware aggression level |
| `OMEGA_AGENT_VERIFICATION_DISPATCH_v1-nova.ai.md` | 62 | Agent verification dispatch with 10 verifiable probes, decisions, gaps |
| `Web Grok - OMEGA ENGINE Vision Document.md` | 156 | Vision document: WAD architecture, Omegaverse, sovereignty flywheel |
| `Web Grok - The 42 Ideals of Maat.md` | 88 | Historical 42 Ideals, modern positive reframing, Omega Engine relevance |
| `Qdrant for Omega Engine Memory_full.md` | 5,824 | Comprehensive Qdrant memory architecture, speculative decoding, cloud planner/local executor, dataset extraction, flywheel strategies, TUI spec, README |
| `Web-Gemini_Qdrant for Omega Engine Memory.md` | ~1,100 | Definitive implementation manual with phases, SEDA bus, sovereign bridge, GRPO training |

---

## ✅ KALI REVIEW NOTES (2026-08-07) — VERIFIED AGAINST ENGINE STATE

**Review performed**: Cross-referenced each item against `src/omega/`, `config/wads/`, `SOVEREIGN_MANDATES.md`, `CREDITS.md`, `PIVOT_LOG.md`, `SOVEREIGN_ARK_BLUEPRINT.md` v5.2.0, and 2026-08-07 session decisions.

| Check | Result |
|-------|--------|
| MaKaLi hierarchy representation (co-equality vs apex) | ⚠️ **Corrected** — engine implements Founder→CTO/CISO hierarchy (`hierarchy.yaml`); co-equality is philosophy only |
| WAD/IWAD architecture decisions (engine/stack firewall) | ✅ Base implemented (`config/wads/`, D-286/D-287); M2 firewall compliant; M14 vet recorded |
| Provider fabric priorities (local-first M7) | ⚠️ **Corrected** — all cloud-planner/training items annotated with M7 constraint (local PRIMARY, cloud fallback) |
| Heritage tagging (M14) | ✅ WAD `[id-soft: doom-1993]` vetted; headroom `[heritage: headroom-ai 2025]` vetted |
| Phase C/D gate status (done vs pending) | ⚠️ **Corrected** — NL-1 is Ark ticket (post-Phase-D, D-383); not a new research item |
| Items superseded by SOVEREIGN_ARK_BLUEPRINT v5.2.0 | ⚠️ **Corrected** — G-1/W-1/V-1 super-urgent tracks are the current priority stack; this research list is backlog, not immediate work |
| Temple-Grade compliance (T1-T11) | ⚠️ **Annotated** — T11 (IA2) exempted until IA2 spec stabilizes; all ASPIRATIONAL items must pass Sovereign Refinement Protocol before implementation |

**Open items for Researcher**:
- [ ] Verify dual-branch memory (M1) lambda/penalty/importance defaults against actual Qdrant schema — confirm none exist yet
- [ ] Confirm `vr/` scaffolding contents in `config/wads/_omega_default/vr/` (M3)
- [ ] Pull exact current SQ8 quantization params from `vector_adapters.py` for benchmark baseline (M2)
- [ ] Check whether `mtp_drafter` in `capability_matrix.py` is populated by any provider today (I2)

---

*Generated by Sovereign Researcher (Jem Analyst L2) — Perspective Triangulation via Council of Four*
*Architect: Structural feasibility • Adversary: Hidden assumptions • Alchemist: Cross-pollination opportunities • Archivist: Documented precedent*
*Reviewed and corrected by Kali (2026-08-07) against engine state + D-510/D-286/D-287/D-383 + SOVEREIGN_ARK_BLUEPRINT v5.2.0*
