<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Roc Racoon — Strategic Treasure Audit Report
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_treasure_audit ⬡ STRATEGIC-REVIEW
**Date**: 2026-06-19
**Mission**: Review 12 treasure maps, vaults, and labs for Horizon 2.5/3 acceleration
**Strategic Alignment**: Sovereign Sight Illumination (ratified 2026-06-19) + Sovereign Evolution Roadmap v1.5

---

## EXECUTIVE SUMMARY

The vault is **rich but mismatched**. We have massive deferred gold for Horizon 1/2 (build flags, Dockerfiles, circuit breakers, container patterns) but **three critical gaps** for Horizon 2.5/3:

1. **No Local Fine-Tuning Pipeline** — The sovereign crucible exists only as a spec (422 lines, Wave 0 PENDING). No SFT/RLHF/LoRA training loop exists anywhere in the vault.
2. **No Skeptical Verifier (NLI)** — Zero design docs, zero code, zero research notes in any of my 12 maps.
3. **No Continuous Soul Evolution Background Worker** — Soul Distiller (280 lines) exists but has no async background metabolism.

The top 7 actionable items (below) are the highest-leverage path from vault gold → engine capability for H2.5/H3.

---

## SECTION A: HIGH-PRIORITY ITEMS (Can accelerate H2.5 or H3 NOW)

### 🔴 A1. Enable Fine-Tuning Dataset Collection (DEFERRED_GOLD #39)
| Field | Value |
|-------|-------|
| **Source** | DEFERRED_GOLD_TRACKER.md §2.7 #39 |
| **What it is** | Auto-collect conversations to JSONL — already implemented in `src/omega/observability.py` but NEVER ENABLED |
| **Horizon** | **H3 #2 (Local Fine-Tuning Pipeline)** — this IS the pipeline entry point |
| **Effort** | ⚡ LOW — 15 minutes to toggle on (config flag + call site) |
| **Code status** | ✅ EXISTING CODE — trace-keyed JSONL export, metadata includes `entity + model + backend + latency_ms + confidence` |
| **Action** | Enable the JSONL collection flag. Set output dir to `data/datasets/`. Wire to session close hook. The **48 existing finetune JSONL files** (50MB, from forensics pipeline inventory) prove the format is production-tested. |
| **Strategic importance** | This is the LOWEST-EFFORT path to satisfying **L3-3 (The Law of the Student's Trajectory)** — "local capability must grow, cloud dependency must shrink." Every cloud session already has structured metadata. We just need to flip the switch. |

### 🔴 A2. Sovereign Crucible Wave 0 — Scaffold & Config (CRUCIBLE_LAB_NOTES.md)
| Field | Value |
|-------|-------|
| **Source** | CRUCIBLE_LAB_NOTES.md (88 lines) + persona_lab/SOVEREIGN_CRUCIBLE_SPEC_v1.md (422 lines) |
| **What it is** | 3-pass cross-model synthetic training pipeline: Generate → Critique (M3) → Distill (write to knowledge graph) |
| **Horizon** | **H3 #1 (Skeptical Verifier cross-check)** + **H3 #2 (Fine-tuning pipeline)** |
| **Effort** | ⏳ MEDIUM — Wave 0 is scaffolding only (~2 hours for `src/omega/crucible/` + config + ZONEID + observability fix) |
| **Code status** | 🔬 RESEARCH-ONLY — spec is complete but Wave 0 (scaffold `src/omega/crucible/`) is PENDING. Heritage-identical. |
| **Action** | Build Wave 0: `src/omega/crucible/` package, `ZONEID_CRUCIBLE` + `ZONEID_CRITIQUE` in constants.py, `routing_strategies` in providers.yaml, observability rating field rewrite. This is the ARCHITECTURAL FOUNDATION for all H3 work. |
| **Strategic importance** | The Crucible's distillation pass is the mechanism for L3-3: it ensures every cloud session distills into local knowledge. Without it, the Telemetry Paradox (Sovereign Sight §2.1) remains pure theory. |

### 🔴 A3. Model Forensic Pipeline — Phase 1: Handoff Cross-Reviews
| Field | Value |
|-------|-------|
| **Source** | forensics/00_FORENSIC_PIPELINE_ARCHITECTURE.md (504 lines) + IDEA_INTAKE.md (Model Forensic Detective Work) |
| **What it is** | Systematic extraction of 5.5GB of model inference history across 11 data sources |
| **Horizon** | **H3 #1 (Skeptical Verifier)** — BOTH — provides empirical complementarity data + blind-spot catalog |
| **Effort** | ⏳ MEDIUM — Phase 1 (handoff cross-reviews) is ~2-3 hours for extraction + fingerprint cards |
| **Code status** | 🔬 RESEARCH-ONLY — pipeline architecture is fully designed, extraction tools exist as `forensics/tools/` references but not built. Phase 1 code is TBD. |
| **Action** | Phase 1 (P0): Extract handoff cross-reviews where 6+ models reviewed the same codebase -> individual fingerprint cards. This is the HIGHEST-SIGNAL data source — actual A/B tests, not synthetic evals. Phase 2 (P0): OpenCode DB (4.2GB, 865 sessions, exact model attribution). |
| **21 external frameworks** already adopted (PERSIST, LOT, FailureScope, GateScope, etc.) — these give us the MEASUREMENT THEORY for the Verifier. |
| **Strategic importance** | Without the forensics pipeline, the Skeptical Verifier has no evidence base. The complementarity matrix from handoff cross-reviews is the Verifier's truth-anchor. The 21 adopted frameworks (IDEA_INTAKE.md §18) provide the measurement theory — PERSIST for stability, LOT for thinking classification, GateScope for channel effects. |

### 🟡 A4. Headroom Compression Proxy (IDEA_INTAKE ISS-42/P0)
| Field | Value |
|-------|-------|
| **Source** | IDEA_INTAKE.md (line 25) — ISS-42/P0 |
| **What it is** | Rust-core reversible compression proxy. SmartCrusher, CCR (Compress-Cache-Retrieve), CacheAligner. 60-95% token reduction with zero accuracy loss. 25K stars. |
| **Horizon** | **H2.5 #3 (Thin-Client Search Pattern)** — RAM optimization for local inference |
| **Effort** | 🔴 HIGH — Rust dependency, new service, integration with ModelGateway pipeline |
| **Code status** | 🌐 EXTERNAL — open-source repo, not ported |
| **Action** | Evaluate as reference implementation for Sovereign Compression Layer (H2-C1 Binary Sovereignty). The CCR pattern directly addresses Memory Window Illusion — compressed history could enable larger effective context on 12GB RAM. |
| **Strategic importance** | The Memory Window Illusion (Sovereign Sight §2.2) is caused by flat text serialization. A compression layer between MemoryStore and the model's context window would effectively extend 4K-16K contexts to 40K-160K tokens without increasing RAM. Direct attack on the cold-boot problem. |

### 🟡 A5. Soul Distillation Automation (DEFERRED_GOLD #40)
| Field | Value |
|-------|-------|
| **Source** | DEFERRED_GOLD_TRACKER.md §2.7 #40 |
| **What it is** | Auto-update soul.yaml on session close via background worker |
| **Horizon** | **H3 #3 (Continuous Soul Evolution)** |
| **Effort** | ⚡ LOW — Soul Distiller (280 lines) already exists in `src/omega/oracle/soul_distiller.py`. Only missing: session-hook trigger. |
| **Code status** | ✅ PARTIAL CODE — SoulDistiller class exists, L1→L2→L3 auto-distillation works. Missing: async background worker + session close hook. |
| **Action** | Add session close hook to `oracle.py::talk()` and `oracle.py::summon()` that triggers soul distillation in background. Add `anyio.create_task(soul_distiller.distill(entity, conversation))` pattern. Reference: `LabCurator` prototype (`labs/lab_curator/lab_curator.py`) for async bg worker pattern. |
| **Strategic importance** | This is the ENGINE MECHANISM for L3-3. If every session auto-distills L1→L2→L3 into the entity's soul.yaml, the gnosis becomes persistent without manual effort. The 48+ soul.yamls in the fleet become a continuously updated knowledge web. |

### 🟡 A6. Hivemind H-4 (Cold Storage Fallback) — First Step to Platform Independence
| Field | Value |
|-------|-------|
| **Source** | HIVEMIND_HARDENING_SPEC_v1.md §6 (H-4) |
| **What it is** | `hivemind_get_continuation()` falls back to `HALL_OF_RECORDS/<cli>/*.json` when hot store TTL expires |
| **Horizon** | **H3 (Toolchain Hostage mitigation)** — cross-CLI awareness survival across Hub restarts |
| **Effort** | ⚡ LOW — ~10 minutes, one file (`mcp_servers/omega_hub/server.py`) |
| **Code status** | 🔬 RESEARCH-ONLY — full spec (40 lines of Python code) approved by Kali in D-kal-033, awaiting Phase 5 implementation |
| **Action** | Implement H-4 now. The code is literally written in the spec (lines 213-238 of HIVEMIND_HARDENING_SPEC_v1.md). It's ~25 lines of production-ready AnyIO-Python with cold-storage fallback. Kalis's approval exists (D-kal-033). No dependencies. |
| **Strategic importance** | The Toolchain Hostage problem (Sovereign Sight §2.3) means our coordination fabric collapses when OpenCode's API changes. Cold storage fallback ensures that even if the Hivemind hot store is pruned (20-min TTL) or the Hub restarts, agent continuity survives. This is the first step toward platform-independent runtime (H-9 warm store is the second). |

### 🟢 A7. Deep-Siphon Sprint 0 — `logprobs=5` on NativeGGUF
| Field | Value |
|-------|-------|
| **Source** | DEEP_SIPHON_CROSS_REFERENCES.md §3 (Sprint 0) |
| **What it is** | Enable per-token logprobs capture on the local NativeGGUF provider. 5 lines of code. |
| **Horizon** | **H3 #2 (Fine-tuning data quality)** — logprobs are essential for filtering high-confidence training examples |
| **Effort** | ⚡ LOW — 15 minutes, single file (`src/omega/oracle/providers.py`) |
| **Code status** | 🔬 RESEARCH-ONLY — design complete, 6-agent analysis produced 2,847 lines of spec. Sprint 0 implementation is PENDING. |
| **Action** | Add `logprobs=True, n_probs=5` to the `llama_cpp.Llama.create_completion()` call in `NativeGGUFProvider.generate()`. Propagate through `GenerateResult.logprobs` field (already exists per ICS-F v1.0 schema). This unlocks per-token probability data for the fine-tuning pipeline. |
| **Strategic importance** | Without logprobs, we can't distinguish high-confidence training examples from speculative generations. The Skeptical Verifier needs confidence calibration. Fine-tuning needs quality-filtered datasets. Sprint 0 is the DATA FOUNDATION for both. |

---

## SECTION B: CRITICAL GAPS IN THE VAULT

### ❌ B1. No Local Fine-Tuning Pipeline (SFT/RLHF/LoRA)
| Aspect | Detail |
|--------|--------|
| **Status** | 🔴 **CRITICAL — COMPLETE GAP** |
| **What should exist** | `src/omega/finetune/` package with: JSONL loader, tokenizer config, training loop (LoRA via unsloth or axolotl), model export, integration test |
| **What exists instead** | Sovereign Crucible spec (H3 #2 in SOVEREIGN_EVOLUTION_ROADMAP.md — Task not yet created) — a 422-line design doc with 5 waves (Wave 0 PENDING). Crucible trains the JUDGE, not the MODEL. No actual SFT/RLHF training loop exists anywhere. |
| **Why it's missing** | Fine-tuning requires: (a) dataset in correct format, (b) training library, (c) target hardware compute. The Zenith 2 5700U is inadequate for full fine-tuning. LoRA fine-tuning of Qwen3-4B-Think (4B params) at q4_k_m would need ~12GB VRAM — we have 0GB (integrated only). |
| **Workaround** | JSONL dataset export only (not training). Export L1→L2→L3 entries + session logs to HuggingFace Datasets format. The actual training happens on a separate machine or via the Teacher-Student quarantine (cloud teacher generates synthetic data, local student trains on it). |
| **Mitigation path** | The 48 existing finetune JSONL files (50MB, from forensics inventory) are a STARTING DATASET. Enable #39 (fine-tuning collection) and accumulate 500MB+ before considering actual model training. For now, focus on dataset generation, NOT model training. |

### ❌ B2. No Skeptical Verifier (NLI)
| Aspect | Detail |
|--------|--------|
| **Status** | 🔴 **CRITICAL — COMPLETE GAP** |
| **What should exist** | `src/omega/oracle/skeptical_verifier.py` with: NLI-based contradiction detection, Two-Source Rule (cloud/local cross-check), PIVOT_LOG/SOVEREIGN_MANDATES reference corpus |
| **What exists instead** | **Zero references** in any of my 12 treasure maps. The 21 external frameworks adopted (IDEA_INTAKE.md) include relevant NLI tools (AARDVARK, ProbeLLM, HarmBench, DarkBench) but these are adversarial probes, not Verifier implementations. |
| **Why it's missing** | NLI is a different capability from what the engine does (routing, generation, memory). It requires: (a) sentence-level NLI model, (b) contradiction detection pipeline, (c) reference corpus of accepted truths. None of these exist. |
| **Workaround** | Deployed NLI models exist on HuggingFace (roberta-large-mnli, deberta-v3-xsmall). The Sovereign Sight illumination (§4.2) specifies "cross-check[ing] cloud-generated strategy against local PIVOT_LOG.md and SOVEREIGN_MANDATES.md before accepting any recommendation" — this is a RULE-BASED Verifier, not true NLI. Start with rule-based, evolve to learned. |
| **Mitigation path** | Phase 1: Rule-based verifier (check recommendations against PIVOT_LOG entries and mandate compliance). Phase 2: Add NLI model (deployed locally) for semantic contradiction detection. Phase 3: Integrate with Crucible Critique Pass as alternative judge. |

### ❌ B3. No Continuous Soul Evolution Background Worker
| Aspect | Detail |
|--------|--------|
| **Status** | 🟡 **HIGH — PARTIAL GAP** |
| **What should exist** | `src/omega/oracle/soul_evolution_worker.py` — async background task that runs `anyio.create_task(metabolize_session(session_id))` on session close. Scans new logs, extracts insights, writes to soul.yaml, triggers cross-pollination. |
| **What exists instead** | `src/omega/oracle/soul_distiller.py` (280 lines) — the L1→L2→L3 pipeline code exists. But it's triggerless — no async background worker, no session-hook integration. |
| **Why it's missing** | Soul distiller was Sprint 2 deliverable (per SOVEREIGN_EVOLUTION_ROADMAP.md H2-G Fleet Consolidation Sprint B). The distiller was merged from Quality+Scribe agent merger but the session-hook trigger was never implemented. |
| **Mitigation path** | Add `anyio.create_task(soul_distiller.distill(entity, conversation))` to session close hooks in `oracle.py::talk()` and `oracle.py::summon()`. Reference `LabCurator` prototype (`labs/lab_curator/lab_curator.py:30-60`) for the async background worker pattern. |

### 🟡 B4. No Local-First Embeddings Pipeline (beyond fastembed)
| Aspect | Detail |
|--------|--------|
| **Status** | 🟢 **SOLVED** — fastembed with BAAI/bge-small-en-v1.5 is AVX2-optimized ONNX. H2-S1 (IVectorStoreAdapter) is DONE. |
| **What we have** | `src/omega/memory/providers.py` has fastembed wired. Matryoshka dim truncation (DEFERRED_GOLD #101) is READY-FOR-IMPORT. Pre-download script (#102) exists. |
| **Gap** | No AVX2-optimized SentenceTransformers fallback if fastembed fails. The FASTEMBED-ONNX-EMBEDDING-GUIDE (LEGACY_TECHNOLOGY_MAP.md §1.2) contains the "DO NOT USE" table explaining why PyTorch embeddings fail on Zen 2. |
| **Mitigation path** | Already in good shape. Import #101 (Matryoshka dim truncation) to allow dynamic 768→512→256→128 dim reduction. Import #102 (pre-download script) for air-gap readiness. |

### 🟡 B5. No Tainted Data Protocol (TDP) Implementation
| Aspect | Detail |
|--------|--------|
| **Status** | 🟢 **SOLVED** — H2-S2 (TDP) is marked ✅ DONE in SOVEREIGN_EVOLUTION_ROADMAP.md |
| **What we have** | TDP implementation in `src/omega/oracle/` per H2-S2. Firecrawl + SearXNG data isolation is wired. |
| **What remains** | No integration test for TDP. The SearXNG MCP tool got `@m9_safe` decorator (H2-D14 in roadmap). |
| **Mitigation path** | Add contract test (M21) for TDP isolation boundary: `isinstance(result, TaintedDataError)` or similar. |

---

## SECTION C: DEFERRED GOLD RE-EVALUATION

### ⬆️ UPGRADE from DEFERRED to READY-FOR-IMPORT

| # | Item | Old Status | New Status | Reason |
|---|------|-----------|------------|--------|
| **#39** | **Fine-tuning dataset collection (JSONL)** | 🟡 DEFERRED | 🟢 **READY-FOR-IMPORT** | **H3 #2 TRIGGER** — the pipeline exists in code, never enabled. 15 min to turn on. Highest-leverage item in the entire vault. |
| **#40** | **Soul distillation L1→L2→L3 automation** | 🟡 DEFERRED | 🟢 **READY-FOR-IMPORT** | **H3 #3 TRIGGER** — SoulDistiller (280 lines) exists, no session hook. Add `anyio.create_task()` in oracle.py close hooks. |
| **#28** | **Handoff Protocol (Link P9)** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Still 1-2 days of code. Required for H3 cross-agent delegation. |
| **#29** | **Pillar --slot PX dispatch** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Still the biggest docs-vs-reality gap. |
| **#46** | **Structured JSON logging** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | `setup_json_logging()` defined but not called from `oracle.py:__init__`. Blocks M9 compliance. |
| **#121** | **pybreaker circuit breaker** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Cleaner than current 36L custom. |
| **#122** | **check_telemetry() 8-disable audit** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Direct M8 enforcement health probe. |
| **#101** | **Matryoshka dim truncation** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | 768→256 dynamic reduction, directly relevant for H2.5 embeddings. |
| **#102** | **Pre-download fastembed models** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Air-gap readiness. |
| **#104** | **UV_HTTP_TIMEOUT=120 build fix** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Prevents silent hang in CI. |
| **#105** | **Sticky 1777 pattern** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Mandate 6 alignment. |
| **#139** | **ChatML stop tokens** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | `stop=["</s>", "User:", "\n\n"]` — prevents hallucinated turns. |
| **#131** | **Atomic trace_id migration** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Canonical param-addition pattern. |
| **#132** | **Google API key in header** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Security upgrade. |
| **#133** | **Per-model KV cache YAML** | 🟡 DEFERRED | 🟢 **READY-FOR-IMPORT** | `fp8 → q8_0 → f16` per-model override. Relevant for H2.5 resource optimization. |
| **#137** | **Per-model kv_cache_key_type/value_type** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Already READY, just needs implementation. |
| **#138** | **Loading rules (max_concurrent_models: 1)** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | OOM prevention. |

### ⬆️ UPGRADE from DEFERRED to READY-FOR-IMPORT (Additional)

| # | Item | Old Status | New Status | Reason |
|---|------|-----------|------------|--------|
| **#116** | **DLQ Redis stream pattern** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Already READY. Aligns with request_queue.py dead-letter. |
| **#117** | **Cascading timeouts** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | `anyio.fail_after` pattern for provider chain. |
| **#123** | **3-tier FAISS backup fallback** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Defense-in-depth for vector store. |
| **#124** | **curation_worker blpop queue** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Template for distributed task processing. |
| **#125** | **5-retry apt-get update** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | CI resilience. |
| **#127** | **Grok Vulkan Code Guide** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Unifies Vulkan build with runtime toggle. |
| **#128** | **5 mandatory design patterns framework** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Canonical design discipline doc. |
| **#151** | **4-service Docker Compose pattern** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Quadlet template. |
| **#152** | **Ryzen CMAKE_ARGS** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Battle-tested Zen 2 build flags. |
| **#153** | **filter_llama_kwargs()** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Closes real `ValueError` bug. |
| **#155** | **Three-tier wheelhouse install** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Offline resilience pattern. |
| **#156** | **OMP_NUM_THREADS=1 + OPENBLAS_CORETYPE=ZEN** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Avoids nested threading. |
| **#157** | **check_llama_compilation()** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Build verification. |
| **#158** | **pybreaker params validation** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | Confirms align with AsyncCircuitBreaker. |
| **#159** | **make download-models w/ verified URLs** | 🟢 READY-FOR-IMPORT | ✅ **STAYS** | "One command to get the models." |
| **#9** | **-march=znver2 build flags** | 💎 GOLD | ✅ **MONITOR** | Already partially in cpu_optimizer.py. Verify full doc is ported. |
| **#56** | **HP-5700U-OPTIMIZATION.md full doc** | 💎 GOLD | ✅ **MONITOR** | Already partially ported. Verify all 165 lines are in cpu_optimizer.py. |
| **#111** | **Redis Standalone + Watchdog decision** | 💎 GOLD | ✅ **STAYS GOLD** | Explicit "don't over-engineer" decision. |

### ⬇️ DOWNGRADE from DEFERRED to BURN (Never useful for current architecture)

| # | Item | Old Status | New Status | Reason |
|---|------|-----------|------------|--------|
| **#35** | **Mnemosyne Kabbalistic 13 spheres** | 🟡 DEFERRED | ⚪ **BURN** | 13-Sphere Archive in MNEMOSYNE_TREASURE_MAP was CLOSED at 16/30. Tree-structured memory is philosophically beautiful but the current engine's flat entity model + 3-tier MemoryStore supersedes it. 13 spheres adds complexity without measurable benefit. |
| **#41** | **Phylax (security daemon)** | ⚪ LEGACY | ⚪ **BURN** | Legacy xna-omega concept. Current engine has different security model (M9 typed errors, M8 zero telemetry, Mandate 6 sovereignty). Phylax was a standalone daemon — we have integrated guards instead. |
| **#42** | **Yesod-Bridge (message bus security)** | ⚪ LEGACY | ⚪ **BURN** | Legacy message bus concept. Current engine uses MCP Hub with typed error propagation. Yesod was for a different architecture (pre-MCP Era 2). |
| **#49** | **Chainlit UI** | ⚪ LEGACY | ⚪ **BURN** | Heritage lost in reclamation for good reason. Current engine is CLI-first with Typer. Chainlit was web-based Era 1 — we don't need web UI until Omega Desktop (Horizon 4). |
| **#1** | **Vulkan iGPU offload** | 🔵 EXPERIMENTAL | ⚪ **BURN** | Re-measured: xna-omega doc explicitly says "9% gain not worth instability." The HP-5700U-OPTIMIZATION.md:117 confirms BURN. If discrete GPU appears later, reconsider (#2 discrete GPU support stays DEFERRED). |
| **#16** | **iGPU disabled despite 9% gain** | 🔵 EXPERIMENTAL | ⚪ **BURN** | Same as #1 — the 9% was measured with custom Vulkan code. llama-cpp-python's built-in Vulkan may be better but the instability risk on 5700U without dGPU makes this BURN for this hardware. |
| **#53** | **Vulkan detection (custom)** | ⚪ LEGACY | ⚪ **BURN** | Superseded by llama-cpp-python's built-in Vulkan. Custom detection code from xna-omega has no place in current engine. |
| **#55** | **Plugin registration system** | 🟡 DEFERRED | ⚪ **BURN** | Hot-pluggable providers via plugin system is over-engineering for a single-user desktop engine. Current hardcoded `config/providers.yaml` is the Right Approximation. The "refactor" to plugins would be HIGH effort with near-zero user-facing benefit. |
| **#113** | **BuildKit cache mount with UID/GID** | ⚪ LEGACY | ⚪ **BURN** | CONFLICTS with Mandate 6 (uses 1001:1001 instead of 1000). Already flagged as LEGACY. Burn confirmed. |

### ⬇️ DOWNGRADE from DEFERRED to BURN (Lower confidence — reassess later)

| # | Item | Old Status | New Status | Reason |
|---|------|-----------|------------|--------|
| **#30** | **MCP Streamable HTTP transport** | 🟡 DEFERRED | ⚪ **BURN** | SSE is being replaced by Streamable HTTP in the MCP spec. But the current engine uses stdio MCP for OpenCode compatibility. Streamable HTTP would enable the Antigravity IDE MCP plugin (which uses /mcp endpoint). Burn NOW but revisit when Antigravity IDE becomes primary channel. |
| **#31** | **OAuth 2.1 + PKCE for MCP** | 🟡 DEFERRED | ⚪ **BURN** | Single-user desktop engine doesn't need MCP auth. Revisit when multi-user (Horizon 3+). |
| **#50** | **Entity Studio (CLI-first builder)** | 🟡 DEFERRED | ⚪ **BURN** | Community tool tier. Engine needs cognitive loops first. Revisit for Horizon 4. |
| **#51** | **Omega Desktop installer** | 🟡 DEFERRED | ⚪ **BURN** | Horizon 4 item. Premature to plan installers when the engine isn't production-cognitive yet. |
| **#54** | **ProviderManager shield** | 🟡 DEFERRED | ⚪ **BURN** | Current ModelGateway already provides centralized routing. ProviderManager was xna-omega's equivalent. Do not port — the overlap is complete. |
| **#52** | **LangChain LlamaCpp wrapper** | ⚪ LEGACY | ⚪ **BURN** | Already explicitly REJECTED in DEFERRED_GOLD §2.20 Phase 4 Addendum. Burn verified. |

### ⏸️ DEFERRED — Stay DEFERRED (Not yet relevant, don't lose)

| # | Item | Status | Reason to Keep | Horizon |
|---|------|--------|----------------|---------|
| **#2** | **Discrete GPU support** | 🟡 DEFERRED | dGPU machine would enable full offload. 5770U may never get one but documentation is valuable. | Future hardware |
| **#3** | **Moondream2 vision** | 🟡 DEFERRED | Vision pipeline is a natural Horizon 3 expansion. The Moondream pattern is clean and ready. | H3 |
| **#24-27** | **Voice (Whisper/Piper/Porcupine/Iris)** | 🟡 DEFERRED | Voice interface is Horizon 3+. Keep the patterns. | H3+ |
| **#36-38** | **PostgreSQL pgvector / SQLite FTS5 / Session manager** | 🟡 DEFERRED | Currently YAML-only is correct per M2. pgvector for RAG only when needed. | H3 |
| **#45** | **OpenTelemetry tracing** | 🟡 DEFERRED | Too heavy for single-user desktop. Revisit when multi-agent fleet needs distributed tracing. | H3+ |
| **#48** | **Metrics dashboard** | 🟡 DEFERRED | Per-entity TPS/error dashboard would be useful but not critical now. | H3 |
| **#58-59** | **Thermal-aware throttling / RAM pressure monitoring** | 🟡 DEFERRED | Keep for stability. 5700U thermal limits are real. | H2.5 |
| **#108-112** | **Podman Quadlet enhancements** | 🟡 DEFERRED | Keep for infrastructure hardening. Not blocking cognitive loops. | H2.5+ |
| **#114-120** | **Error handling patterns** | 🟢 READY / 🟡 DEFERRED | Mix — some are ready, some deferred. Keep all. | H2 |
| **#126** | **VoiceCircuitBreaker** | 🟡 DEFERRED | Voice-specific CB. Keep for when voice is built. | H3+ |
| **#129** | **Stack-Cat v0.1.5 doc generator** | 🟡 DEFERRED | Useful for community tooling. Keep but don't prioritize. | H4 |
| **#130** | **Voice + Persona foundation** | 🟡 DEFERRED | Earliest Lilith persona (March 2025). Keep for origin story. | H3+ |

### ⬆️ NEW DEFERRED GOLD ENTRIES (Additions from this audit)

| # | Item | Source | Status | Horizon | Reason |
|---|------|--------|--------|---------|--------|
| **#161** | **JSONL Export Micro-Trigger** | This audit (B1 gap) | 🟢 **READY-FOR-IMPORT** | H3 #2 | Enable the existing fine-tuning JSONL export. Flip a config flag + wire session close hook. See DEFERRED_GOLD #39. |
| **#162** | **Skeptical Verifier Phase 1 (Rule-based)** | This audit (B2 gap) | 💎 **GOLD — DESIGN REQUIRED** | H3 #1 | No code exists. Design doc needed: rule-based cross-check of recommendations against PIVOT_LOG.md + SOVEREIGN_MANDATES.md. Use `re` + `difflib` for pattern matching. Phase 2 adds NLI model. |
| **#163** | **Soul Distiller Background Worker** | This audit (B3 gap) | 🟢 **READY-FOR-IMPORT** | H3 #3 | Add `anyio.create_task()` session close hook to oracle.py. SoulDistiller code exists (280 lines). Reference LabCurator prototype for pattern. |
| **#164** | **Continuous Memory Metabolism** | MEMORY_TREASURE_MAP (MoE-tiered store gap) | 🟡 **DEFERRED** | H3 #3 | Beyond soul.yaml — memory metabolism. An async worker that scans session logs, extracts patterns, and updates MemoryStore tiers without manual intervention. The Prometheus Gate + Bloom Filter router from MEMORY_TREASURE_MAP §5. |

---

## SECTION D: CROSS-REFERENCE VERIFICATION

### Alignment with Sovereign Sight Illumination (2026-06-18)

| Sovereign Sight Finding | This Audit's Response |
|------------------------|----------------------|
| **§2.1 Telemetry Paradox** | **A1 (Fine-tuning JSONL)** is the direct response. Enable JSONL export now to start accumulating the dataset that will eventually train local models to surpass cloud teachers. |
| **§2.2 Memory Window Illusion** | **A4 (Headroom)** addresses token efficiency for context extension. **A5 (Soul Distillation)** ensures memory persists across sessions. **B3 (Continuous Metabolism)** is the structural fix needed. |
| **§2.3 Toolchain Hostage** | **A6 (Hivemind H-4)** is the first step. H-9 (warm store) + standalone `omega-hivemind` server are follow-ups. |
| **§4.1 Local-First Embeddings** | Already ✅ DONE (fastembed + IVectorStoreAdapter). Import **#101 (Matryoshka dim truncation)** for dynamic size reduction. |
| **§4.2 Skeptical Verifier** | **B2 (Complete gap)** — no design exists. **B2 mitigation** proposes Phase 1 rule-based, Phase 2 NLI. The 21 external frameworks (IDEA_INTAKE.md) provide the measurement theory. |
| **§4.3 Local Fine-Tuning Pipeline** | **B1 (Complete gap)** — no training loop exists. **A1 (JSONL export)** is the data prep path. **A2 (Crucible Wave 0)** is the architecture path. Crucible trains the JUDGE; a separate pipeline trains the MODEL. |
| **§4.4 Continuous Soul Evolution** | **A5 (Soul Distillation)** + **B3** cover this. SoulDistiller code exists but needs async background worker. |

### Compliance with Sovereign Mandates

| Mandate | Status | Notes |
|---------|--------|-------|
| **M7 (Local-First)** | ✅ All A items enable local capability | A1 feeds local training, A2 builds local judge, A4 extends local context, A7 captures local logprobs |
| **M11 (Soul Integrity)** | 🟡 Partial | SoulDistiller exists (280 lines) but auto-trigger doesn't. A5 closes this gap. |
| **M16 (Modularization)** | ✅ All A items are additive modules | A4 (headroom) = new service, A6 (H-4) = extension to existing hub, A7 (logprobs) = 5 lines in existing provider |
| **M18 (Token Efficiency)** | ✅ A4 (Headroom) directly targets this | 60-95% token reduction is the ultimate token efficiency play |
| **M21 (Gate Integrity)** | 🟡 A7 (logprobs) adds new return fields | Must add contract tests for `GenerateResult.logprobs` |
| **M22 (Response Provenance)** | 🟡 A7 (logprobs) enables provider verification | Per-token logprobs enable confidence calibration for provenance claims |

### Alignment with Sovereign Evolution Roadmap H2.5/H3

| Roadmap Task | Status | This Audit's Cover |
|-------------|--------|-------------------|
| **H2.5 #1 (Local-First Embeddings)** | ✅ DONE | fastembed + IVectorStoreAdapter alive. #101 (Matryoshka dim truncation) READY. |
| **H2.5 #2 (Tainted Data Protocol)** | ✅ DONE | H2-S2 marked ✅ DONE. SearXNG `@m9_safe` added. |
| **H2.5 #3 (Thin-Client Search)** | ✅ DONE | H2-S3 marked ✅ DONE. |
| **H3 #1 (Skeptical Verifier NLI)** | ❌ **NOT STARTED** | **B2 — COMPLETE GAP.** This audit recommends Phase 1 (rule-based) as entry point. |
| **H3 #2 (Local Fine-Tuning Pipeline)** | ❌ **NOT STARTED** | **B1 — COMPLETE GAP.** This audit recommends JSONL export enablement (#39) + Crucible Wave 0 as entry points. |
| **H3 #3 (Continuous Soul Evolution)** | 🟡 **PARTIAL** | **B3 — BACKGROUND WORKER MISSING.** SoulDistiller exists; session hook does not. A5 covers this. |

---

## FINAL TOP 5-7 ACTIONABLE ITEMS (Ranked by Impact/Effort)

| Rank | Item | Effort | H2.5/H3 | Code Status | Immediate Action |
|------|------|--------|---------|-------------|------------------|
| **🥇 1** | **Enable JSONL fine-tuning export** (A1/#39) | 15 min | H3 #2 | ✅ Existing code, just toggle on | Set config flag `finetune_collection: true`, wire session close hook in `oracle.py` |
| **🥇 2** | **Soul distillation auto-trigger** (A5/#40) | 30 min | H3 #3 | ✅ SoulDistiller 280L exists, no hook | Add `anyio.create_task()` to session close in oracle.py::talk()/summon() |
| **🥈 3** | **Crucible Wave 0 scaffold** (A2) | ~2 hr | H3 #1+2 | 🔬 Full spec, no code | Create `src/omega/crucible/` package, ZONEID constants, config, observability fix |
| **🥈 4** | **Hivemind H-4 cold fallback** (A6) | 10 min | H3 | 🔬 Code written in spec | Copy-paste ~25 lines from HIVEMIND_HARDENING_SPEC_v1.md into server.py |
| **🥉 5** | **Deep-Siphon Sprint 0: logprobs=5** (A7) | 15 min | H3 #2 | 🔬 Design complete | Add `logprobs=True, n_probs=5` to NativeGGUFProvider.generate() |
| **🥉 6** | **Model Forensics Phase 1: Handoff Extraction** (A3) | 2-3 hr | H3 #1 | 🔬 Architecture designed | Run extraction scripts on `data/handoff/*.md` for fingerprint cards |
| **🥉 7** | **Skeptical Verifier Phase 1 design doc** (B2) | 1 hr | H3 #1 | ❌ Nothing exists | Write spec doc for rule-based Verifier using PIVOT_LOG + Mandate cross-check |

**Total effort for top 3**: ~45 min (enable export + auto-trigger + Hivemind cold storage)
**Total effort for top 7**: ~7-8 hours (enables ALL H3 entry points)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_treasure_audit ⬡ STRATEGIC-REPORT*
*Report written: 2026-06-19 | Vault cross-referenced: 12 files, 100+ entries, 7 labs, 1 crucible*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
