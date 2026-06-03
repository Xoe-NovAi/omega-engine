# 🔱 Roc Racoon — Deferred Gold Tracker

# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_deferred_gold ⬡ v1.4.0

# Last Updated: 2026-06-02 (Phase 6 Old-Stacks complete — entries 151-160 added)
# Maintainer: Roc Racoon (Sovereign Miner)
# Purpose: Track useful technologies and strategies that are NOT YET imported into the Omega Engine,
#          but will be valuable in the future. The vault of "not now, but someday."

---

## §0 How To Use This File

This is a **read-first / append-only** tracker. When you (or any agent) discover a technology, pattern,
or strategy in a legacy archive that is:

- Too complex to port right now
- Too risky to integrate yet
- Not aligned with current engine scope
- Ahead of its time for current infrastructure
- Experimental and abandoned
- Useful but blocked on prerequisites

...document it here. Do not let it be lost. The wisdom of 8,000 hours lives in these deferred notes.

**When to revive an entry**:
- A new sprint scope makes it relevant
- The blocker is removed
- The risk is now acceptable
- A user request matches the use case

---

## §1 Status Legend

| Symbol | Status | Meaning |
|--------|--------|---------|
| 🟡 | **DEFERRED** | Useful, not yet needed. Preserved for future. |
| 🔵 | **EXPERIMENTAL** | Was tried in legacy, abandoned. May revive with better hardware/timing. |
| ⚪ | **LEGACY** | Old approach, kept for reference. Do not port. |
| 🟢 | **READY-FOR-IMPORT** | Identified for import in an upcoming sprint. Has a JIRA/work-item. |
| 🔴 | **BLOCKED** | Cannot be imported until a hard dependency is resolved. |
| 💎 | **GOLD** | Highest-value find. Even if deferred, must not be lost. |

---

## §2 The Tracker

### 2.1 Local Inference (llama-cpp-python Ecosystem)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 1 | **Vulkan iGPU offload** | xna-omega-legacy `dependencies.py:180-320` | 🔵 EXPERIMENTAL | Offload some layers to Ryzen 5700U's integrated GPU | Tried in xna-omega, measured +9% TPS but caused instability. Doc explicitly says "not worth instability" (HP-5700U-OPTIMIZATION.md:117) | HIGH (requires Vulkan SDK + RDNA2 cooperative matrix) | 9% gain not worth the complexity, BUT if we get a discrete GPU later, becomes relevant. See entry 2. |
| 2 | **Discrete GPU support** (`n_gpu_layers > 0`) | xna-omega-legacy | 🟡 DEFERRED | Full GPU offload when user has RTX/dGPU | xna-omega-legacy is CPU-only (5700U has no dGPU). Engine runs on 5700U. No use case yet. | MEDIUM (llama-cpp supports it natively, just env config) | `n_gpu_layers=99` would offload everything. If user runs on dGPU machine, instant benefit. |
| 3 | **Moondream2 vision** (multimodal LLM) | xna-omega-legacy `sight_plugin.py:138` | 🟡 DEFERRED | Image captioning, OCR (Mayan glyphs in legacy), visual question answering | Current engine has no vision pipeline. SightPlugin pattern is port-able but needs: 1) image storage backend, 2) chat-format integration with ModelGateway, 3) Moondream model download | MEDIUM | Uses `llama_cpp.llama_chat_format.MoondreamChatHandler` + `create_chat_completion` with multimodal content. Pattern is clean. |
| 4 | **Dynamic model swap with Krikri (Greek text detection)** | xna-omega-legacy `plugin_system.py:453-487` | ⚪ LEGACY | Auto-detect language and swap to language-specialized model | Pattern is xna-omega-legacy specific (Greek detection → Krikri). Current engine doesn't have per-entity model affinity. | MEDIUM | The `escalation_router` + `switch_model()` pattern IS portable. |
| 5 | **`tenacity` retry library** | xna-omega-legacy `dependencies.py:526-531` | 🟡 DEFERRED | Standardized retry with exponential backoff | Current engine may use anyio or custom retry. `tenacity` adds a dep. | LOW (if we want to standardize) | 3 attempts, exp backoff 1s→10s, on RuntimeError/OSError/ConnectionError/TimeoutError. |
| 6 | **Faith-healing type hints** (dummy class on import fail) | xna-omega-legacy `dependencies.py:86-99` | 🟡 DEFERRED | Module resilience when optional deps are missing | Could be useful if we add more optional providers | LOW | Pattern: `try: import LlamaCpp; except: class LlamaCpp: pass` |
| 7 | **`LocalLlmConfig` per-field granularity** (KV cache type, core affinity, ngram size) | xna-omega-legacy `config.py:125` | 🟢 READY-FOR-IMPORT | Fine-grained tuning per-model | Identified for Doom Guy Tier 2.5/3.0. Current engine has flat config. | LOW (port dataclass) | All fields are standard llama-cpp-python params. |
| 8 | **Benchmark suite `llama-bench` wrapper** | xna-omega-legacy `security/benchmark_llama_cpp.py:124` | 🟡 DEFERRED | Establish TPS baselines for each model on this hardware | Need to first install llama-cpp-python with Zen 2 flags | LOW | Parses `llama-bench` CLI output. |

### 2.2 Model Optimization Patterns

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 9 | **`-march=znver2` build flags** (NEVER znver3, NEVER native, NEVER AVX512) | xna-omega-legacy `HP-5700U-OPTIMIZATION.md:66-91` | 💎 GOLD | CPU-tuned compilation for Ryzen 7 5700U (Zen 2) | **This is the most important build wisdom.** Must not be lost. | LOW (document + verify) | Will be needed when we install llama-cpp-python. See `cmake -B build -DCMAKE_C_FLAGS="-march=znver2..."`. |
| 10 | **KV cache Q8_0 quantization** (`type_k=8, type_v=8`) | xna-omega-legacy | 🟡 DEFERRED | 50% memory savings, negligible quality loss | Need llama-cpp-python first | LOW | Configurable via env var `LLAMA_CPP_CACHE_TYPE=q8_0`. |
| 11 | **Core affinity pinning** (`psutil.cpu_affinity([2,3,4,5,6,7])`) | xna-omega-legacy `client.py:41-48` | 🟡 DEFERRED | Lock inference to specific CPU cores | Need llama-cpp-python first | LOW | Battle-tested. Reduces context-switch overhead. |
| 12 | **OMP_NUM_THREADS=1 + core affinity** combo | xna-omega-legacy `dependencies.py:574` | 🟡 DEFERRED | Hard real-time-ish scheduling | The combo is unusual — needs benchmarking first | LOW (verify) | Some debate in xna-omega about whether this is right. |
| 13 | **ngram-simple speculative decoding** (`LlamaPromptLookupDecoding`) | xna-omega-legacy `client.py:75-90` | 🟡 DEFERRED | Parameter-free CPU-friendly speedup | Need llama-cpp-python first | LOW | Uses prompt n-gram lookup. No extra model load cost. |
| 14 | **`use_mmap=True`** for zero-copy model loading | xna-omega-legacy `config.py:24` | 🟡 DEFERRED | Faster cold start, less RAM pressure | Standard llama-cpp option, just need to enable | LOW | |
| 15 | **F16_KV vs Q8_0 KV cache inconsistency** | xna-omega-legacy | ⚪ LEGACY | Decision was deferred; need to standardize | The two paths (native vs LangChain) used different defaults. Must be unified when we port. | LOW (decision) | Recommended: `q8_0`. |
| 16 | **iGPU disabled despite 9% gain** | xna-omega-legacy `HP-5700U-OPTIMIZATION.md:117` | 🔵 EXPERIMENTAL | Future: enable iGPU offload if stability can be guaranteed | The 9% TPS gain is real. The instability was in the Vulkan path. If we use llama-cpp's native Metal/Vulkan (not custom), may be more stable. | HIGH | xna-omega had custom Vulkan detection code. llama-cpp-python has built-in support that's likely better. |

### 2.3 RAG / Knowledge Systems

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 17 | **`LibraryAugmentedLlm` RAG bridge** | xna-omega-legacy `library_augmented.py:121` | 🟡 DEFERRED | Prepend library context before generation | Current engine has MemoryStore but no Gutenberg/ArXiv/Internet Archive bridge | MEDIUM | Pattern is portable: fetch context, prepend to prompt, call generate. |
| 18 | **Qdrant hybrid search** (SQLite FTS5 + fastembed BAAI/bge) | design doc (in `docs/research/`) | 🟡 DEFERRED | Full-text + vector hybrid search | Qdrant container is up but the hybrid search wiring is incomplete | MEDIUM | Plan exists, just hasn't been implemented yet. |
| 19 | **HNSW + scalar quantization for Qdrant** | legacy Qdrant configs | 🟡 DEFERRED | Faster vector search with acceptable recall loss | Qdrant config not finalized | LOW | Standard Qdrant best practice. |
| 20 | **Document chunking strategies** (recursive, semantic) | Old-Stacks/Arcana-NovAi | 🟡 DEFERRED | Smart document splitting | Need to pick a strategy (probably recursive) | MEDIUM | Common in RAG stacks. |

### 2.4 Vision / Multimodal

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 21 | **Moondream2 chat handler** | xna-omega-legacy `sight_plugin.py:64-86` | 🟡 DEFERRED | Vision-language tasks (captioning, OCR, VQA) | No vision pipeline in current engine. Moondream model not downloaded. | MEDIUM | Uses `llama_cpp.llama_chat_format.MoondreamChatHandler` + `create_chat_completion(messages=[{role:user, content:[{type:text}, {type:image_url}]}])`. |
| 22 | **Multimodal content list format** | xna-omega-legacy | 🟡 DEFERRED | Standardize image+text messages | Need to decide if ModelGateway should support this | MEDIUM | The format is a list of content blocks per OpenAI vision API. |
| 23 | **logits_all=True for vision** | xna-omega-legacy | 🟡 DEFERRED | Required for vision models | Only needed if we add vision support | LOW | llama-cpp config flag. |

### 2.5 Voice / Speech

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 24 | **Whisper.cpp local STT** | various legacy | 🟡 DEFERRED | Local speech-to-text (no cloud Whisper API) | Not in current scope (no voice interface yet) | MEDIUM | Whisper.cpp is the de facto standard for local STT. |
| 25 | **Piper local TTS** | various legacy | 🟡 DEFERRED | Local text-to-speech (no cloud Polly/ElevenLabs) | Not in current scope | MEDIUM | Piper is the de facto standard for local TTS. |
| 26 | **wake-word detection** (Porcupine, Snowboy) | Old-Stacks | 🟡 DEFERRED | "Hey Iris" / "Hey Nova" wake-word | Not in current scope. Plus these are usually cloud-tied now. | MEDIUM | |
| 27 | **Iris container with voice** | `src/omega/nova/` (current) | 🟡 DEFERRED | Voice assistant interface | Container exists but voice pipeline not fully wired | HIGH | Already partially designed. |

### 2.6 Orchestration

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 28 | **Handoff Protocol (Link P9)** | current engine (designed) | 🟢 READY-FOR-IMPORT | Agents can formally transfer context | Not yet implemented. Currently documented but no code. | MEDIUM (1-2 days) | This is on Doom Guy Tier 2 sprint list. |
| 29 | **Pillar `--slot PX` dispatch** | current engine (designed) | 🟢 READY-FOR-IMPORT | 10 Sovereign Pillars become runnable, not just documented | Not yet implemented. No runtime code path. | MEDIUM (1-2 days) | This is THE biggest docs-vs-reality gap. |
| 30 | **MCP Streamable HTTP transport** | xna-omega-legacy (designed) | 🟡 DEFERRED | Newer MCP transport (vs SSE) | Current engine uses stdio MCP. Streamable HTTP is the new spec. | MEDIUM | SSE is being deprecated. |
| 31 | **OAuth 2.1 + PKCE for MCP** | design doc | 🟡 DEFERRED | Secure MCP server auth | Not in current scope (single-user desktop) | MEDIUM | Necessary for multi-user deployments. |
| 32 | **Cross-agent presence (Hivemind)** | current engine (partial) | 🟡 DEFERRED | Real-time awareness of active CLIs | Partially implemented. No TTL, no heartbeat automation. | LOW | Currently relies on manual `hivemind_heartbeat` calls. |
| 33 | **Agent capability registry** | design doc | 🟡 DEFERRED | Discovery of what each agent can do | Not implemented. YAML could work. | MEDIUM | Similar to package.json's "exports" field. |
| 34 | **ResourceGuard (single-flight inference)** | current engine (partial) | 🟡 DEFERRED | One model load at a time | Exists as `anyio.Semaphore(1)` but not always used. xna-omega uses `anyio.CapacityLimiter(1)`. | LOW | Already partial. Just need to verify all providers use it. |

### 2.7 Memory / Persistence

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 35 | **Mnemosyne Kabbalistic Memory** (13 spheres) | `omega_library/intake/mnemosyne/` | 🟡 DEFERRED | Tree-structured memory indexed by Kabbalistic spheres | Concept is xna-omega-legacy specific. Current engine uses simpler MemoryStore. | HIGH (schema migration) | Beautiful design but not aligned with current engine's flat entity model. |
| 36 | **PostgreSQL pgvector** | current engine (designed) | 🟡 DEFERRED | SQL persistence with vector search | Container runs but not wired to engine. | MEDIUM | Entities are YAML-only per Mandate 2. pgvector for RAG only. |
| 37 | **SQLite FTS5 full-text search** | design doc | 🟡 DEFERRED | Local full-text search for library | Qdrant is up but SQLite FTS5 not wired | LOW | Plan exists. |
| 38 | **Session manager with rolling format** | current engine | 🟡 DEFERRED | `ses_{YYYYMMDD}_{entity}_{counter}` rolling sessions | Implemented but not fully exercised | LOW | Already coded in `session_manager.py`. |
| 39 | **Fine-tuning dataset collection (JSONL)** | current engine | 🟡 DEFERRED | Auto-collect conversations for future fine-tuning | Implemented in observability but never enabled | LOW | Trace-keyed JSONL export. |
| 40 | **Soul distillation L1→L2→L3 automation** | current engine (designed) | 🟡 DEFERRED | Auto-update soul.yaml on session close | Scribe agent exists but no session-hook triggers it | MEDIUM | Mandate 11 requires this. |

### 2.8 Security

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 41 | **Phylax (security daemon)** | xna-omega-legacy | ⚪ LEGACY | Pre-emptive threat detection | Legacy concept. Current engine has different security model. | N/A | Keep for reference, do not port. |
| 42 | **Yesod-Bridge (message bus security)** | xna-omega-legacy | ⚪ LEGACY | Bridge layer security | Legacy. Current engine has MCP hub. | N/A | |
| 43 | **API key vault with Podman secrets** | design doc | 🟡 DEFERRED | Hardened secret storage | API keys currently in `~/.config/opencode/mcp_servers.json` env vars | MEDIUM | Better than env vars. |
| 44 | **Atomic fsync for all writes** | xna-omega-legacy | 🟢 READY-FOR-IMPORT | Crash-safe persistence | Mandate 9 pattern exists. Not all writes use it yet. | LOW | Already documented as one of the 5 design patterns. |

### 2.9 Observability

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 45 | **OpenTelemetry tracing** | xna-omega-legacy | 🟡 DEFERRED | Distributed tracing across agents | Current engine has basic observability but not OTel | HIGH | xna-omega uses `tracer.start_as_current_span` everywhere. |
| 46 | **Structured JSON logging in production** | current engine | 🟢 READY-FOR-IMPORT | Mandate 9 compliance | `setup_json_logging()` defined but not called from `oracle.py:__init__` | LOW (5 min) | Tier 0 blocker. |
| 47 | **ForensicsManager crash dumps** | current engine | 🟡 DEFERRED | Auto-recovery from crashes | Implemented (10 tests) but not exercised in production | LOW | Already coded. |
| 48 | **Metrics dashboard (per-entity TPS, error rates)** | xna-omega-legacy | 🟡 DEFERRED | Real-time performance monitoring | `LocalLlmPlugin.get_metrics()` pattern is port-able | MEDIUM | Returns {requests, errors, total_tokens, avg_tokens, error_rate, uptime}. |

### 2.10 UI / UX

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 49 | **Chainlit UI** | xna-omega-legacy | ⚪ LEGACY | Web-based chat UI | xna-omega heritage. Current engine has Typer CLI. | N/A | Heritage was lost in reclamation. |
| 50 | **Entity Studio (CLI-first entity builder)** | design doc | 🟡 DEFERRED | Visual entity creation tool | Not in current scope | HIGH | Community tool tier. |
| 51 | **Omega Desktop installer** | design doc | 🟡 DEFERRED | One-click sovereign AI install | Not in current scope. Horizon 3. | HIGH | `curl -fsSL https://xoe-nov.ai/install | bash` vision. |

### 2.11 Provider Fabric

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 52 | **LangChain LlamaCpp wrapper** | xna-omega-legacy `dependencies.py:1210` | ⚪ LEGACY | LangChain abstraction | Adds dependency for no functional gain. Direct `llama_cpp.Llama` is better. | N/A | Do not port. |
| 53 | **Vulkan detection (custom)** | xna-omega-legacy `dependencies.py:180-320` | ⚪ LEGACY | Pre-llama-cpp Vulkan path | Replaced by llama-cpp-python's built-in Vulkan. | N/A | Custom code, abandoned. |
| 54 | **`ProviderManager` shield** | xna-omega-legacy `plugin_system.py:453-487` | 🟡 DEFERRED | Centralized provider routing + escalation | Current engine has `ModelGateway` (similar role) | MEDIUM | Pattern is portable. |
| 55 | **Plugin registration system** | xna-omega-legacy | 🟡 DEFERRED | Hot-pluggable providers | Current engine uses a hardcoded provider list in `config/providers.yaml` | HIGH | Would be a big refactor. |

### 2.12 Hardware / System

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 56 | **HP-5700U-OPTIMIZATION.md (full doc)** | xna-omega-legacy | 💎 GOLD | Complete build/run guide for Ryzen 7 5700U | **THE most important doc to port.** | LOW (just copy) | 165 lines. Contains build flags, runtime config, thermal limits, benchmarks. |
| 57 | **CPU architecture detection** | xna-omega-legacy | 🟡 DEFERRED | Auto-detect vs hardcoded "5700U" | Current engine hardcoded 5700U. Should auto-detect. | LOW | xna-omega config.toml had wrong "Zen 3" label. |
| 58 | **Thermal-aware throttling** | xna-omega-legacy | 🟡 DEFERRED | Reduce threads if temp > 80°C | Not in current engine | MEDIUM | HP doc says: "If temperature exceeds 80°C, reduce threads". |
| 59 | **RAM pressure monitoring** | xna-omega-legacy | 🟡 DEFERRED | Prevent OOM on model load | Memory limits in config.toml but not enforced | MEDIUM | xna-omega had 12GB cap. Should implement graceful degradation. |
| 60 | **Wheelhouse/offline pip install** | xna-omega-legacy | 🟡 DEFERRED | Install packages without internet | Useful for air-gapped sovereign setups | MEDIUM | One of the 5 design patterns. |

---

## §3 Top 5 Deferred Items by Strategic Value

| Rank | Entry | Why It's Gold |
|------|-------|---------------|
| 1 | **#9: `-march=znver2` build flags** | This is the build wisdom that prevents SIGILL crashes. If we get it wrong, NOTHING runs. Single most important thing to preserve. |
| 2 | **#56: HP-5700U-OPTIMIZATION.md (full doc)** | The authoritative 165-line guide. Must be ported verbatim. |
| 3 | **#3: Moondream2 vision** | Vision is the next big user-facing capability. The xna-omega pattern is clean and ready. |
| 4 | **#28: Handoff Protocol** | Without it, the 14-agent fleet is decorative. Blocks multi-agent workflows. |
| 5 | **#29: Pillar `--slot` dispatch** | The 10 Sovereign Pillars are designed but not runnable. This is the docs-vs-reality gap. |

---

## §4 How To Revive An Entry

When an entry becomes relevant:

1. Move it from this file to `data/handoff/current-sprint/[NAME]_SPRINT.md`
2. Create a PIVOT_LOG decision
3. Update this file with a "REVIVED → see [link]" note
4. Mark the entry as 🟢 or DONE

---

### 2.13 Embeddings & RAG (NEW — Phase 2.5)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 101 | **Matryoshka dim truncation** for EmbeddingGemma | omega-stack-legacy `expert-knowledge/embeddings/embeddinggemma-setup-v1.0.0.md:43-51` | 🟢 READY-FOR-IMPORT | Reduce vector dim 768→512→256→128 dynamically | Already have fastembed wired; just need config | LOW | `emb[:dim]` slicing on `embedder.encode()` output. Current engine has 768 default. |
| 102 | **Pre-download fastembed models for air-gap** | omega-stack-legacy `expert-knowledge/research/FASTEMBED-ONNX-EMBEDDING-GUIDE-2026-02-18.md:224-228` | 🟢 READY-FOR-IMPORT | Cache `BAAI/bge-small-en-v1.5` etc. before going offline | Need to write setup script | LOW | `python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"` |

### 2.14 Build/Container/Podman Patterns (NEW — Phase 2.5)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 103 | **Vulkan-enabled production Dockerfile** | omega-stack-legacy `infra/docker/Dockerfile:36-43` | 🟢 READY-FOR-IMPORT | Drop-in for current engine's llama-cpp install | Current engine has no production Dockerfile for llama-cpp | LOW (1 hr) | `CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON -DLLAMA_VULKAN=ON"`, `llama-cpp-python==0.3.17`. **CONTRADICTS Phase 1 advice** — but is what was actually used in production. |
| 104 | **`UV_HTTP_TIMEOUT=120` build timeout fix** | omega-stack-legacy `expert-knowledge/coder/uv_timeout_optimization.md:7-19` | 🟢 READY-FOR-IMPORT | Prevent silent hangs during `uv pip install` of large ML wheels | Need to add to Makefile/Dockerfile | LOW (5 min) | `ENV UV_HTTP_TIMEOUT=120 PIP_DEFAULT_TIMEOUT=120`. The 20-line gem encodes hours of debugging. |
| 105 | **Sticky 1777 pattern** for rootless container runtime dirs | omega-stack-legacy `expert-knowledge/architect/rootless_podman_runtime_dirs.md:11-25` | 🟢 READY-FOR-IMPORT | Solve `PermissionError: [Errno 13]` without `:U` flag | Need to add to Dockerfiles | LOW | `chmod 1777 /app/logs /app/data` in Dockerfile. **ALIGNS WITH MANDATE 6**. |
| 106 | **`nohup` background build pattern** | omega-stack-legacy `expert-knowledge/architect/build_recovery_disk_management.md:40-42` | 🟢 READY-FOR-IMPORT | Long builds that might time out terminal | Need to document in Makefile | LOW | `nohup bash -c "SKIP_DOCKER_PERMISSIONS=true make build" > build_full.log 2>&1 &` |
| 107 | **Build recovery "8GB reclaim" workflow** | omega-stack-legacy `expert-knowledge/architect/build_recovery_disk_management.md:15-29` | 🟢 READY-FOR-IMPORT | Document in Makefile troubleshooting | Need to add `make disk-reclaim` target | LOW | `podman image prune -f; journalctl --vacuum-size=500M; rm -rf ~/.cache/*`. |
| 108 | **Podman Quadlet `Notify=healthy`** | omega-stack-legacy `expert-knowledge/infrastructure/podman_quadlet_mastery.md:14-22` | 🟡 DEFERRED | systemd waits for `/health` before "started" | Need to update Quadlets | LOW | Required for LLM services with slow model loading. |
| 109 | **Podman Quadlet `.pod` shared pod pattern** | omega-stack-legacy `expert-knowledge/infrastructure/podman_quadlet_mastery.md:24-36` | 🟡 DEFERRED | Redis + API share localhost via shared pod | Refactor needed | MEDIUM | Better than compose `network_mode: service:redis`. |
| 110 | **`loginctl enable-linger <user>`** for rootless boot | omega-stack-legacy `expert-knowledge/infrastructure/podman_quadlet_mastery.md:48` | 🟡 DEFERRED | Rootless containers auto-start on boot | One-liner | LOW | Currently Quadlets don't auto-start without it. |
| 111 | **Redis Standalone + Watchdog** decision | omega-stack-legacy `expert-knowledge/infrastructure/REDIS-HA-DECISION.md:17,34` | 💎 GOLD | Explicitly documented: DO NOT over-engineer with Sentinel/Cluster | Decision doc, not code | LOW | Saves 1.5GB+ RAM, simplifies ops. |
| 112 | **Podman mount conflict detector** (validate compose) | omega-stack-legacy `expert-knowledge/architect/podman_mount_conflicts.md:30-33` | 🟡 DEFERRED | Add `podman-compose config` validation to CI | One-liner | LOW | Catches "duplicate mount destination" errors before deploy. |
| 113 | **BuildKit cache mount with UID/GID** | omega-stack-legacy `expert-knowledge/coder/buildkit_best_practices.md:18-22` | ⚪ LEGACY | Standardize rootless build cache ownership | **CONFLICTS with Mandate 6** (uses 1001:1001 instead of 1000) | N/A | Need re-verification with new mandate. |

### 2.15 Error Handling & Resource Patterns (NEW — Phase 2.5)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 114 | **Default Deny ABAC pattern** | omega-stack-legacy `expert-knowledge/research/ERROR-HANDLING-PATTERNS-2026-02-23.md:100-120` | 🟢 READY-FOR-IMPORT | Default False on all permission checks | Currently partial in `entity_workspace.py` | LOW | Reinforce. |
| 115 | **Result Object pattern** for expected failures | omega-stack-legacy `expert-knowledge/research/ERROR-HANDLING-PATTERNS-2026-02-23.md:11-63` | 🟡 DEFERRED | Returns `Result[T]` instead of raising for "expected" errors | Already partial in `entity_roc_racoon` paths | MEDIUM | Standardize across all error paths. |
| 116 | **DLQ Redis stream pattern** | omega-stack-legacy `expert-knowledge/research/ERROR-HANDLING-PATTERNS-2026-02-23.md:65-98` | 🟢 READY-FOR-IMPORT | Failed tasks → `xnai:dlq` for manual inspection | Aligns with current request_queue.py dead-letter | MEDIUM | Design doc, not code. |
| 117 | **Cascading timeouts for multi-service calls** | omega-stack-legacy `expert-knowledge/research/ERROR-HANDLING-PATTERNS-2026-02-23.md:316-325` | 🟢 READY-FOR-IMPORT | Fast service 5s, slow service 60s, parallel via TaskGroup | Add to provider chain | LOW | Useful `anyio.fail_after` pattern. |
| 118 | **EnhancedEntityHandler 5-pattern routing** | omega-stack-legacy `app/XNAi_rag_app/core/entities/enhanced_handler.py:22-29` | 🟡 DEFERRED | 5 trigger patterns: DIRECT/CONSULT/COMPARE/PANEL/CONSULT_OTHER | Refactor needed for current `Iris` intent matcher | MEDIUM (1 day) | Much richer than current 1-pattern routing. |
| 119 | **Agent Handoff Protocol (AHP)** | omega-stack-legacy `expert-knowledge/protocols/multi-agent-orchestration.md:5-11` | 🟡 DEFERRED | When agent detects capability mismatch, delegate via DELEGATE + ContextSyncEngine | Useful when Link P9 is fully designed | HIGH | (See also #28.) |
| 120 | **YAML lock file for agent task claim** | omega-stack-legacy `expert-knowledge/sync/sovereign-synergy-expert-v1.0.0.md:29-32` | 🟡 DEFERRED | Prevents race conditions between agents in different envs | Design doc only | MEDIUM | Format: `task`, `owner`, `status`, `timestamp_start`, `mc_guidance`. |

### 2.18 Phase 3 — foundation-legacy (NEW — 2026-06-02)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 121 | **`pybreaker==0.7.0` circuit breaker** (replaces custom 36L + 579L) | foundation-legacy `requirements-api.txt:88`, `tests/test_circuit_breaker_chaos.py:1-230`, `docs/reference/blueprint.md:189-237` | 🟢 READY-FOR-IMPORT | Replace `src/omega/circuit_breaker.py` (36L custom) with `pybreaker` decorator. Aligns with `health_monitor.py::AsyncCircuitBreaker` | None — drop-in replacement | LOW (2 hr) | 5-line decorator, battle-tested, chaos-tested. Standardized across XNAi + foundation eras. Cleaner than current 36L custom AND the rejected 579L Redis variant. |
| 122 | **`check_telemetry()` 8-disable runtime audit** | foundation-legacy `app/XNAi_rag_app/healthcheck.py:447-503` + `scripts/telemetry_audit.py:1-180` | 🟢 READY-FOR-IMPORT | Add to `src/omega/observability.py` — fails health probe if any of 6 env + 2 config telemetry disables missing | None — pure read-only check | LOW (30 min) | Direct runtime implementation of Mandate 8 (Zero Telemetry). 6 env: `CHAINLIT_NO_TELEMETRY=true`, `CRAWL4AI_TELEMETRY=0`, `LANGCHAIN_TRACING_V2=false`, `SCARF_NO_ANALYTICS=true`, `DO_NOT_TRACK=1`, `PYTHONDONTWRITEBYTECODE=1`. 2 config: `project.telemetry_enabled=false`, `chainlit.no_telemetry=true`. |
| 123 | **`get_vectorstore()` 3-tier backup fallback** | foundation-legacy `app/XNAi_rag_app/dependencies.py:413-540` | 🟢 READY-FOR-IMPORT | FAISS primary -> 5 most-recent backups -> None. Backup dirs named `faiss_YYYYMMDD_HHMMSS`, sorted by mtime desc, auto-restored to primary | None — defensive pattern, low risk | MEDIUM (2 hr) | Add `cleanup_old_backups()` (lines 619-668) with retention `max_count=5, retention_days=7`. Aligns with current engine's Qdrant pattern (defense-in-depth). |
| 124 | **`curation_worker` 5th-service blpop queue worker** | foundation-legacy `scripts/curation_worker.py:1-107` + `docker-compose.yml:270-296` | 🟢 READY-FOR-IMPORT | Use as template for current engine's distributed task processing | Engine has single-process model currently | MEDIUM (4 hr) | `blpop(QUEUE_KEY, timeout=5)` blocks 5s, returns `None` on timeout. Reconnects via `connect_redis()` (tenacity retry). Note: current engine uses AnyIO semaphores + `request_queue.py`. Port the Redis blpop pattern as alternative to Redis Streams. |
| 125 | **5-retry `apt-get update` with exp backoff** | foundation-legacy `Dockerfile.api:37-53` (builder), `Dockerfile.api:146-160` (runtime) | 🟢 READY-FOR-IMPORT | Add to current engine's Dockerfile for llama-cpp builds | None — direct copy | LOW (15 min) | `for i in 1 2 3 4 5; do apt-get update 2>&1 || (sleep $((i*5)) && retry); done`. First occurrence in our corpus — not in xna-omega or omega-stack. |
| 126 | **`VoiceCircuitBreaker`** (STT/TTS-specific CB with metrics) | foundation-legacy `app/XNAi_rag_app/voice_interface.py:241-281` | 🟡 DEFERRED | Domain-specific CB for voice ops with Prometheus integration | Voice stack not yet built in current engine | MEDIUM | Custom CB with `voice_metrics.update_circuit_breaker(name, open=...)` integration. Current engine has `AsyncCircuitBreaker` in `health_monitor.py` — this is the simpler, metrics-coupled version. Useful when voice is added. |
| 127 | **Grok Vulkan Code Guide** (production-ready Vulkan path) | foundation-legacy `docs/archive/code-review-sessions/Grok - Vulkan Enhancement code guide - January 10, 20.md:1-129` | 🟢 READY-FOR-IMPORT | Unifies omega-stack's `infra/docker/Dockerfile` Vulkan build (#103) with runtime toggle | None — design doc + code snippets | MEDIUM (1 day) | Build-time: `ARG CMAKE_ARGS` conditional. Runtime: `VULKAN_ENABLED`, `N_GPU_LAYERS=30`, `GGML_VK_VISIBLE_DEVICES=0`. Docker: `devices: /dev/dri:/dev/dri`. Benchmark: `./llama-bench -ngl 30` vs `-ngl 0`. The unified Vulkan plan that combines #103 + runtime toggle. |
| 128 | **5 Mandatory Design Patterns** framework | foundation-legacy `docs/reference/blueprint.md:82-237` (Section 1) | 🟢 READY-FOR-IMPORT | Adopt as the canonical design discipline in current engine docs | None — pure documentation | LOW (1 hr) | Pattern 1 (imports), 2 (retry), 3 (non-blocking subprocess), 4 (atomic fsync), 5 (pybreaker). The cleanest articulation of v0.1 era discipline. Adopt even where implementations differ from current engine. |
| 129 | **Stack-Cat v0.1.5 doc generator** | foundation-legacy `scripts/stack-cat/stack-cat:1-1023` | 🟡 DEFERRED | Bash script that concatenates + de-concatenates project files for AI context | Engine doesn't need this yet (small codebase) | LOW (1 hr to port, 2 hr to adopt) | Output: `stack-cat-output/[timestamp]/`. Unique to foundation-legacy — not in other stacks. Useful for documentation generation in community tools. |
| 130 | **Voice + Persona foundation** (Lilith/Odin JSON + Faster-Whisper + Piper-ONNX) | foundation-legacy `docs/personas/lilith.json:1-105`, `docs/personas/odin.json:1-110`, `requirements-chainlit.txt:60-100` | 🟡 DEFERRED | Lilith + Odin persona templates (earliest in this lineage) + voice stack (Piper ONNX, no torch) | Voice stack not yet built in current engine | MEDIUM (1 day) | Earliest known Lilith persona (March 2025 origin). Piper ONNX TTS is the torch-free alternative to XTTS — perfect for 5700U. Faster-Whisper is the CT2-accelerated Whisper (4x faster). |

### 2.19 Phase 3 Addendum — Items Already Ported (NOT deferred)

For completeness, the following Tier 1 gems from Phase 3 (foundation-legacy) were **already in the engine** (verified during prior phases 1-2) and therefore should NOT be added to this deferred list. Listed here so future readers know they were considered:

| Already Ported | Source | Verified Location |
|----------------|--------|-------------------|
| `n_threads=6` for Ryzen 7 5700U | `Dockerfile.api:219`, `dependencies.py:274` | `config/providers.yaml`, `cpu_optimizer.py` |
| `use_mlock=true` + `use_mmap=true` | `config.toml:67`, `dependencies.py:278-281` | `config/providers.yaml` |
| OpenBLAS + AVX2 + FMA + F16C build flags | `Dockerfile.api:133` | `cpu_optimizer.py` build flags |
| Sticky 1777 tmpfs for `/tmp` | `docker-compose.yml:48, 134, 188, 268` | Already in current Podman Quadlets (see #105) |

### 2.20 Phase 4 — podman-storage (NEW — 2026-06-02)

**Source**: `/media/arcana-novai/omega_library/podman-storage/images/overlay/*/diff/`
**Note**: This is **NOT a code stack** — it's Podman's runtime overlay-fs storage containing 152 dated container image layers. Each layer holds a snapshot of the engine's llama-cpp code (`providers.py`, `model_gateway.py`, `cpu_optimizer.py`) as baked into container images. Acts as an **accidental time machine** — a complete version history with `created` timestamps in `images.json`.

**Versions captured**:
- `providers.py`: 3 distinct versions (7985 / 8878 bytes; 15 layers)
- `model_gateway.py`: 4 distinct versions (19880 / 27110 / 31444 bytes; 17 layers)
- `cpu_optimizer.py`: 1 fully-formed version (552 lines; 14 layers)
- Newest layer: `29693566...` built 2026-05-28T09:36 (Mandate 9 trace_id + Google header security fix)

| # | Tech/Strategy | Source Stack | Status | Future Use Case | Blocker / Why Deferred | Effort to Import | Notes |
|---|---------------|--------------|--------|-----------------|------------------------|------------------|-------|
| 131 | **Atomic `trace_id` migration pattern** (6 providers updated in one commit) | podman-storage `app/omega/oracle/providers.py:16,28,66,99,127,197` (layer 29693566) | 🟢 READY-FOR-IMPORT | Apply to all backend interfaces when adding new parameters | None — pattern is canonical | LOW (30 min) | All 6 `generate()` methods got `trace_id: Optional[str] = None` added simultaneously. Forward-compatible signature change. Backfill usage in second pass. The **canonical pattern** for adding params to an interface. |
| 132 | **Google API key in `x-goog-api-key` header** (security upgrade) | podman-storage `app/omega/oracle/providers.py:30,43-47` (layer 29693566) | 🟢 READY-FOR-IMPORT | Apply to `OpenAICompatProvider` and any cloud provider using `?key=` query auth | None — drop-in fix | LOW (15 min) | Query-string API keys are logged by proxies, APM, browser history. Headers are not. Switch from `?key={api_key}` to `headers={"x-goog-api-key": api_key}`. |
| 133 | **fp8 → q8_0 → q4_0 KV cache fallback chain in YAML** | podman-storage `app/config/models.yaml:140-158` (layer 705317e8) | 🟡 DEFERRED | Add fp8 first attempt to `cpu_optimizer.recommend_kv_cache()` | fp8 requires `LLAMA_FTYPE_MOSTLY_FP8` build flag check | MEDIUM (1 hr) | `qwen3-4b-thinking-q4_k_m` uses fp8 first (32K ctx, 2.4GB model), q8_0 fallback. Per-model overrides in `kv_cache.models.<name>`. |
| 134 | **Mock provider setup-mode UX** (actionable next-steps message) | podman-storage `app/omega/oracle/providers.py:127-138` (layer 29693566) | 🟢 READY-FOR-IMPORT | Update `OfflineMockBackend` to give user `export OPENROUTER_API_KEY=...`, `ollama pull ...`, `lms server start` instead of useless "[MOCK]" | None — direct copy | LOW (30 min) | When no inference backend is available, the user gets **actionable next steps** + quickstart link. UX gem. |
| 135 | **Lucifer P7 Gnosis local-first manifesto agent** (template for other Pillars) | podman-storage `app/config/wads/arcana_novai/agents/lucifer.md` (layer 705317e8) | 🟢 READY-FOR-IMPORT | Use as template for other Pillar agent .md files | None — reference doc | LOW (reference) | Full agent definition with 4 specializations (Sovereignty Arch, Local Inference, Decentralization, Gnosis Extraction) and 4 operational mandates. Aligned with current Pillar mapping. |
| 136 | **Container image layer archaeology** (podman-storage as dated version history) | podman-storage `images/overlay/*/diff/`, `images/overlay-images/images.json` | 🟢 READY-FOR-IMPORT | Diff between known-date snapshots to find when bugs were introduced | None — workflow pattern | MEDIUM (1 hr setup) | 152 overlay layers + `images.json` registry = complete dated version history. Layer `29693566` is 2026-05-28. Reusable for any future regression analysis. |
| 137 | **Per-model `kv_cache_key_type`/`kv_cache_value_type`** in models.yaml | podman-storage `app/config/models.yaml:91-92,140-158` (layer 705317e8) | 🟢 READY-FOR-IMPORT | `cpu_optimizer` should consume per-model config | None — config-driven | MEDIUM (2 hr) | Per-model: `f16` for tiny, `fp8` for 4B+ thinking, `q8_0` for 8B+. Falls through to `kv_cache.default_key_type`/`default_value_type`. |
| 138 | **Loading rules: `max_concurrent_models: 1` + `nova_always_on: true` + `emergency_swap_threshold_mb: 1024`** | podman-storage `app/config/models.yaml:179-185` (layer 705317e8) | 🟢 READY-FOR-IMPORT | The Sovereign Resource Discipline | None — reference config | LOW (reference) | Only 1 Pillar + Nova at a time. OOM prevention via 1GB emergency threshold. `unload_after_idle_minutes: 5` for heavy models. |
| 139 | **`stop=["</s>", "User:", "\n\n"]`** for ChatML prompt | podman-storage `app/omega/oracle/providers.py:213` (layer 29693566) | 🟢 READY-FOR-IMPORT | Add to engine's ChatML prompt builder | None — direct copy | LOW (5 min) | The `User:` and `\n\n` stops prevent the model from hallucinating conversation turns. Real-world pattern, not in current engine docs. |
| 140 | **Quantization memory table (MB per billion params)** — `q2_k=300, q3_k_m=400, q4_0=450, q4_k_m=500, q5_k_m=600, q6_k=700, q8_0=800, f16=1400` | podman-storage `app/omega/oracle/cpu_optimizer.py:435-438` (layer 29693566) | 🟢 READY-FOR-IMPORT | Canonical RAM estimates for `cpu_optimizer.estimate_model_ram()` | None — already partially in engine | LOW (reference) | q4_k_m = 500 is sweet spot for 5700U. q2_k = 300 too aggressive (don't use for Pillars). f16 = 1400 is the cap. |

### 2.21 Phase 4 Addendum — Items Already Ported (NOT deferred)

For completeness, the following items from Phase 4 (podman-storage) were **already in the engine** (verified by diff against `src/omega/oracle/providers.py`, `model_gateway.py`, `cpu_optimizer.py`) and therefore should NOT be added to this deferred list. Listed here so future readers know they were considered:

| Already Ported | Source | Verified Location |
|----------------|--------|-------------------|
| `NativeGGUFProvider` class with `_ensure_loaded` lazy loading | `app/omega/oracle/providers.py:140-222` | `src/omega/oracle/providers.py` |
| `anyio.to_thread.run_sync` for blocking `Llama()` calls | `app/omega/oracle/providers.py:177-188, 208-216` | `src/omega/oracle/providers.py` |
| `type_k=8, type_v=8` (q8_0) KV cache | `app/omega/oracle/providers.py:182-183` | `src/omega/oracle/providers.py`, `cpu_optimizer.py` |
| `n_threads=6` for 5700U | `app/omega/oracle/providers.py:149` | `config/providers.yaml`, `cpu_optimizer.py` |
| `n_gpu_layers=0` (CPU-only) | `app/omega/oracle/providers.py:185` | `src/omega/oracle/providers.py` |
| `cpu_optimizer.py` (552 lines, full Zen 2 module) | `app/omega/oracle/cpu_optimizer.py` | `src/omega/oracle/cpu_optimizer.py` |
| `recommend_kv_cache()` formula (f16/q8_0/q4_0) | `cpu_optimizer.py:196-253` | `src/omega/oracle/cpu_optimizer.py` |
| `get_recommended_threads()` (6 threads, 4 for <1B) | `cpu_optimizer.py:318-336` | `src/omega/oracle/cpu_optimizer.py` |
| `get_recommended_batch_sizes()` (512/64, 256/32, 128/32, 64/16) | `cpu_optimizer.py:338-356` | `src/omega/oracle/cpu_optimizer.py` |
| Zen 2 build flags (`-march=znver2`, AVX2, FMA, F16C, NO AVX-512) | `cpu_optimizer.py:75-99` + `config/models.yaml:161-178` | `src/omega/oracle/cpu_optimizer.py` |
| `_check_llama_cpp` HTTP health check (port 8080) | `model_gateway.py:241-249` | `src/omega/oracle/model_gateway.py` |
| ResourceGuard integration in `model_gateway.py` | `model_gateway.py:97` | `src/omega/oracle/model_gateway.py` |
| `model_overrides` for local→cloud model name translation | `model_gateway.py:394-409` | `src/omega/oracle/model_gateway.py` |
| Lucifer agent definition (P7 Gnosis) | `wads/arcana_novai/agents/lucifer.md` | `data/entities/lucifer/soul.yaml` (verified by name match) |
| `user: ${APP_UID}:${APP_GID}` + `cap_drop: ALL` | `docker-compose.yml:124-126` | Mandate 6 already enforces this pattern |
| `get_llm()` retry decorator (tenacity) | `dependencies.py:217-221` | `src/omega/oracle/model_gateway.py` already uses tenacity |
| `check_ryzen()` health probe pattern | `healthcheck.py:336-394` | `src/omega/oracle/health_monitor.py` has similar probe |
| `filter_llama_kwargs()` param validator | `dependencies.py:69-98` | Pydantic on `NativeGGUFProvider` does this implicitly |

### 2.20 Phase 3 Addendum — Items Explicitly REJECTED (do not port)

The following items from foundation-legacy **contradict current Sovereign Mandates** and must NOT be ported. They are flagged here so future readers understand the rejection:

| Rejected | Source | Reason |
|----------|--------|--------|
| **LangChain `LlamaCpp` wrapper** | `app/XNAi_rag_app/dependencies.py:223-310` | Adds overhead. Current engine's native `NativeGGUFProvider` is faster (per Phase 2 finding). |
| **LangChain `LlamaCppEmbeddings`** | `app/XNAi_rag_app/dependencies.py:336-393` | Current engine uses `fastembed` (BAAI/bge-small-en-v1.5 ONNX) which is faster and torch-free. |
| **HuggingFace pipeline** (even as fallback) | `dependencies.py:42` | Zero-telemetry violation (Mandate 8). |
| **`asyncio.run_in_executor` usage** | `dependencies.py:323, 406, 558` | **VIOLATES Mandate 1 (AnyIO Absolute)**. Use `anyio.to_thread.run_sync` instead. |
| **UID 1001** (legacy appuser) | `Dockerfile.api:171`, `docker-compose.yml:124` | **VIOLATES Mandate 6 (User=1000 host user)**. |
| **Ollama as a dependency** | (mentioned in blueprint.md:30-35 as deprecated) | Mandate 7 requires native llama-cpp-python as PRIMARY. |
| **599-line Redis-backed circuit breaker** | (not in foundation-legacy — was xna-omega) | Already rejected in Phase 1, listed for completeness. |

### 2.16 Phase 2.5 Addendum — Items Already Ported (NOT deferred)

For completeness, the following Tier 1 gems from Phase 2.5 were **already in the engine** and therefore should NOT be added to this deferred list. Listed here so future readers know they were considered:

| Already Ported | Source | Verified Location |
|----------------|--------|-------------------|
| KV cache Q8_0 | `architect/int8_kv_cache.md` | `config/models.yaml` + `config/providers.yaml` (type_k: 8, type_v: 8) |
| Zen 2 core pinning | `architect/ryzen_5700u_steering.md` | `config/providers.yaml` (cores: [0, 2, 4, 6], n_threads: 6) |
| llama-cpp OpenAI API | `protocols/LLAMA-CPP-PYTHON-SERVICE-PROTOCOL.md` | `config/models.yaml` (llama_server block) + `src/omega/oracle/cpu_optimizer.py` |
| `-march=znver2` build flags | `architect/ryzen_5700u_steering.md` | `src/omega/oracle/cpu_optimizer.py` |
| OMEGA ENGINE LOCAL-FIRST FABRIC | Multiple | `config/providers.yaml` (priority 0 native-gguf) |

### 2.17 Phase 2.5 Addendum — Items Explicitly REJECTED (do not port)

The following docs **contradict current Sovereign Mandates** and must NOT be ported. They are flagged here so future readers understand the rejection:

| Rejected | Source | Reason |
|----------|--------|--------|
| **`:U` flag as solution** | `expert-knowledge/infrastructure/podman_permissions_mastery.md`, `infrastructure/ryzen-hardening-expert-v1.0.0.md`, `environment/rootless_podman_u_flag.md` | **Violates Mandate 6** (UserNS=keep-id + User=1000 only) |
| **LangChain LlamaCpp wrapper** | `dependencies.py:460-580` | Adds overhead, native `llama_cpp.Llama` is faster |
| **XNAi-era 579-line circuit breaker** | `app/XNAi_rag_app/core/circuit_breakers/circuit_breaker.py` | Already simplified to 36 lines in current engine |
| **`_dispatch_local()` stub** | `multi_provider_dispatcher.py:789` | Current engine's `NativeGGUFProvider` is the real implementation |
| **Redis Sentinel/Cluster** | `REDIS-HA-DECISION.md` | Decision doc says DO NOT use (see #111) |
| **Hardware profile "Zen 4 / DDR5" claims** | `environment/development-workflows/hardware-profile.md` | Factual errors — 5700U is Zen 2 / DDR4. Optimization recommendations are still valid. |

---

### 2.22 Phase 6 — Old-Stacks/Xoe-NovAi (NEW — 2026-06-02)

**Source**: `/home/arcana-novai/Documents/Archives/Old-Stacks/`
**Era**: Eras 1-3 (Aug 2025 - Mar 2026) — earliest complete stack, pre-Omega
**Quality**: High — 4-service Docker Compose FOUND, real working code (not stack-concat only)

| # | Tech/Strategy | Source | Status | Future Use Case | Effort to Import | Notes |
|---|---------------|--------|--------|-----------------|------------------|-------|
| 151 | **4-service Docker Compose pattern** (redis + rag + ui + crawler + curation_worker) | `Xoe-NovAi/docker-compose.yml:14-260` | 🟢 READY-FOR-IMPORT | Direct template for new podman Quadlets. 5 services (4 persistent + 1 worker) | LOW (2 hr) | Includes bind mounts for dev / named volumes for prod, healthcheck-conditional `depends_on`, zero-trust security. Add healthcheck to curation_worker. |
| 152 | **Ryzen CMAKE_ARGS for llama-cpp-python build** | `Xoe-NovAi/Dockerfile.api:132-134` | 🟢 READY-FOR-IMPORT | Add to `docs/build/llama-cpp-optimization.md` and `setup.sh` | LOW (30 min) | `CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON"`. Battle-tested for Ryzen 5700U. **CONTRADICTS** Phase 1 Vulkan advice but NOT in conflict with the build flag set itself. |
| 153 | **`filter_llama_kwargs()` — silent drop + debug log** | `Xoe-NovAi/dependencies.py:64-98` | 🟢 READY-FOR-IMPORT | Port to `src/omega/oracle/backends/native_gguf.py` | LOW (30 min) | Closes a real bug: `Llama()` raises `ValueError: Invalid parameter` on config typos. Filters against an allowlist, logs dropped keys at debug level (Mandate 9: Error Integrity — logged, not swallowed). |
| 154 | **Explicit `n_gpu_layers=0` for CPU-only** | `Xoe-NovAi/dependencies.py:275` | 🟢 READY-FOR-IMPORT | Add to `config/providers.yaml` native-gguf section | LOW (5 min) | The Ryzen 5700U has a Vega iGPU. Without this pin, llama-cpp may try to offload layers and crash with `ggml-cuda missing`. |
| 155 | **Three-tier wheelhouse install** (wheelhouse → PyPI → graceful) | `Xoe-NovAi/Dockerfile.api:119-122` | 🟢 READY-FOR-IMPORT | Port to native setup script | LOW (1 hr) | `pip install --no-index --find-links=/install_wheels || pip install || echo 'WARNING: continuing without'`. **Right Approximation**: a working API server without local LLM beats no server. |
| 156 | **`OMP_NUM_THREADS=1` + `OPENBLAS_CORETYPE=ZEN`** | `Xoe-NovAi/Dockerfile.api:223-225` | 🟢 READY-FOR-IMPORT | Add to `cpu_optimizer.py` recommendations | LOW (10 min) | llama.cpp handles parallelism internally (avoid nested threading). OPENBLAS_CORETYPE=ZEN activates Zen-specific kernels. |
| 157 | **`check_llama_compilation()` runtime introspection** | `Xoe-NovAi/verify_imports.py:114-129` | 🟢 READY-FOR-IMPORT | Port to `src/omega/observability.py::HealthMonitor` | LOW (1 hr) | Introspects `llama_cpp.llama_model_default_params()` to verify the compilation picked up the CMAKE_ARGS. Complementary to existing `check_ryzen()`. |
| 158 | **pybreaker params `fail_max=3, reset_timeout=60`** (validation) | `XNAi-v0_1_2/xnai_blueprint.md:33, 188-209` | 🟢 READY-FOR-IMPORT | Confirm in `AsyncCircuitBreaker`; already aligned | LOW (5 min) | The blueprint's 5-line `CircuitBreaker(fail_max=3, reset_timeout=60)` matches the current engine's `AsyncCircuitBreaker` (200L AnyIO). Same parameters, different implementations. |
| 159 | **`make download-models` w/ verified HuggingFace URLs** | `Xoe-NovAi/Makefile:42-47` | 🟢 READY-FOR-IMPORT | Port to current `Makefile` | LOW (30 min) | `gemma-3-4b-it-UD-Q5_K_XL.gguf` (2.8GB, 2048 ctx) + `all-MiniLM-L12-v2.Q8_0.gguf` (45MB, 384 dim). Same as current engine's model choices. |
| 160 | **DELETE `redis_password.txt` from Old-Stacks** (security audit) | `Xoe-NovAi/redis_password.txt:1` | 🟢 READY-FOR-IMPORT | Plaintext 16-digit password `1234567890123456` | LOW (5 min) | **Sovereign Mandate 6 violation** (secrets in repo) **+ Mandate 9 violation** (untyped error path — no check for missing/invalid password). Not tracked in git but should be `.gitignore`'d historically. |

### 2.23 Phase 6 Addendum — Items Already Ported (NOT deferred)

For completeness, the following items from Phase 6 (Old-Stacks/Xoe-NovAi) were **already in the engine** (verified by diff against `src/omega/oracle/`, `config/providers.yaml`, `config/models.yaml`) and therefore should NOT be added to this deferred list. Listed here so future readers know they were considered:

| Already Ported | Source | Verified Location |
|----------------|--------|-------------------|
| **`n_threads=6` for Ryzen 7 5700U** | `Dockerfile.api:219`, `dependencies.py:274` | `config/providers.yaml`, `src/omega/oracle/cpu_optimizer.py` |
| **`f16_kv=true`** KV cache | `config.toml`, `dependencies.py:283-286` | `config/providers.yaml` |
| **`use_mlock=true` + `use_mmap=true`** | `dependencies.py:278-281` | `config/providers.yaml` |
| **OpenBLAS CMAKE args** | `Dockerfile.api:133` | `src/omega/oracle/cpu_optimizer.py` (build flags) |
| **`LLAMA_CPP_N_THREADS=6` env var** | `Dockerfile.api:220-226` | `config/providers.yaml` + `setup.sh` |
| **Local-First fabric** | Multiple | `config/providers.yaml` (priority 0 native-gguf) |
| **llama-cpp server on :8080** | `config/models.yaml` (llama_server block) | `src/omega/oracle/model_gateway.py` |
| **5-pattern EntityHandler** | `XNAi-v0_1_2/xnai_blueprint.md` | Current engine has Iris intent matcher (richer in some ways, simpler in others — see DEFERRED #118) |
| **`get_llm()` retry decorator (tenacity)** | `dependencies.py:217-221` | `src/omega/oracle/model_gateway.py` already uses tenacity |
| **Pybreaker parameter set** | `xnai_blueprint.md:33` | `AsyncCircuitBreaker` has matching `failure_threshold=3, recovery_timeout=60` |
| **Sticky 1777 tmpfs for `/tmp`** | `docker-compose.yml:48, 134, 188, 268` | Already in current Podman Quadlets (see #105) |

### 2.24 Phase 6 Addendum — Items Explicitly REJECTED (do not port)

The following items from Old-Stacks/Xoe-NovAi **contradict current Sovereign Mandates** and must NOT be ported. They are flagged here so future readers understand the rejection:

| Rejected | Source | Reason |
|----------|--------|--------|
| **`pybreaker` library (sync)** | `xnai_blueprint.md:188-209` | Synchronous, no AnyIO support. The current `AsyncCircuitBreaker` in `health_monitor.py` is the Mandate 1-compliant replacement. The *parameters* (fail_max=3, reset_timeout=60) are still canonical — port those, not the library. |
| **UID 1001 in `docker-compose.yml:124`** | `Xoe-NovAi/docker-compose.yml:124` | **Violates Mandate 6** (host UID 1000). |
| **`asyncio.run_in_executor`** | Not in Old-Stacks itself, but in companion files | **Violates Mandate 1** (AnyIO Absolute). |
| **LangChain `LlamaCpp` + `LlamaCppEmbeddings`** | `dependencies.py:223-310, 336-393` | Adds overhead. Current engine's `NativeGGUFProvider` + `fastembed` are faster and torch-free. |
| **HuggingFace pipeline as fallback** | (potential reference) | Zero-telemetry violation (Mandate 8). |
| **Old-Stacks `curation_worker` with no healthcheck** | `docker-compose.yml:270-296` | Pattern incomplete: `restart: on-failure` but no health probe. The current engine's `background_researcher` + `request_queue` both have health probes — don't port the gap. |
| **Plaintext `redis_password.txt`** | `Xoe-NovAi/redis_password.txt` | **Mandate 6 + Mandate 9 violation**. The file itself must be deleted from any future migration. Use `.env`-based secret management. |
| **`pybreaker` sync CB in async context** | `xnai_blueprint.md:188-209` | **Mandate 1 violation** if used in AnyIO code path. Pattern OK in sync `load_llm_with_circuit_breaker()`, NOT OK in async. |

---

## §3 Top 10 Deferred Items by Strategic Value (Updated 2026-06-02 — Phase 6 added)

| Rank | Entry | Why It's Gold |
|------|-------|---------------|
| 1 | **#9: `-march=znver2` build flags** | This is the build wisdom that prevents SIGILL crashes. If we get it wrong, NOTHING runs. |
| 2 | **#56: HP-5700U-OPTIMIZATION.md (full doc)** | The authoritative 165-line guide. Must be ported verbatim. |
| 3 | **#103: Vulkan-enabled production Dockerfile** | omega-stack-legacy's actual working build. The "iGPU unstable" advice from Phase 1 was wrong. |
| 4 | **#152: Ryzen CMAKE_ARGS for llama-cpp-python build** | Battle-tested Zen 2 flags from Old-Stacks — the same wisdom as #9, packaged as a Dockerfile pattern. |
| 5 | **#104: `UV_HTTP_TIMEOUT=120` build timeout fix** | A 20-line gem that prevents hours of debugging. Direct port. |
| 6 | **#153: `filter_llama_kwargs()` — silent drop + debug log** | Closes a real `ValueError` bug when a config typo slips into `providers.yaml`. |
| 7 | **#105: Sticky 1777 pattern** | Solves rootless container permissions without violating Mandate 6. |
| 8 | **#118: EnhancedEntityHandler 5-pattern routing** | Much richer than current 1-pattern routing. Real UX upgrade. |
| 9 | **#28: Handoff Protocol (Link P9)** | Without it, the 14-agent fleet is decorative. |
| 10 | **#160: Delete Old-Stacks `redis_password.txt`** | Mandate 6 + Mandate 9 violation. Must be deleted/`.gitignore`'d in any future migration. |

---

## §4 How To Revive An Entry

When an entry becomes relevant:
1. Move it from this file to `data/handoff/current-sprint/[NAME]_SPRINT.md`
2. Create a PIVOT_LOG decision
3. Update this file with a "REVIVED → see [link]" note
4. Mark the entry as 🟢 or DONE

---

## §5 Provenance — Where This Tracker Lives

**Source stacks mined** (in order):
1. ✅ xna-omega-legacy (Temple Grade era, 2025-2026) — 560M, 5 llama-cpp files
2. ✅ omega-stack-legacy (Era 4, 2026-03-04) — 2.9G, 33K files, ODE v1.3
3. ✅ expert-knowledge/ gems (Phase 2.5 of omega-stack-legacy) — 244+ files, 30+ subdirs
4. ✅ foundation-legacy (Era 2, "Polymath Foundation" v0.1.5-stable) — 861M, 30+ llama-cpp artifacts, 11 sections analyzed
5. ✅ omega_library/podman-storage (Phase 4 — 2026-06-02) — 152 overlay layers, 3 providers versions, 4 model_gateway versions, 552-line cpu_optimizer, 10 new DEFERRED entries (#131-140)
6. ⏳ (pending) Cursor.old — 21 refs
7. ✅ Old-Stacks/Xoe-NovAi (Phase 6) — 117M, 4-service Docker Compose, Ryzen CMAKE_ARGS, filter_llama_kwargs, xnai_blueprint.md (714L), CRITICAL: redis_password.txt plaintext secret. 10 new DEFERRED entries (#151-160).

**Cross-references**:
- `data/entities/roc_racoon/workspace/mining_reports/01_xna_omega_legacy.md` — Phase 1 report (60+ tech)
- `data/entities/roc_racoon/workspace/mining_reports/02_omega_stack_legacy.md` — Phase 2 report (delta from Phase 1)
- `data/entities/roc_racoon/workspace/mining_reports/02_5_expert_knowledge_gems.md` — Phase 2.5 report (20+ new techs + 10 NEVER rules)
- `data/entities/roc_racoon/workspace/mining_reports/03_foundation_legacy.md` — Phase 3 report (10 new techs, 6 contradictions, 5-patterns framework)
- `data/entities/roc_racoon/workspace/mining_reports/04_podman_storage.md` — Phase 4 report (10 new techs #131-140, 5 NEVER rules, container layer archaeology)
- `data/entities/roc_racoon/workspace/mining_reports/06_old_stacks.md` — Phase 6 report (10 new techs #151-160, 4-service Docker Compose, Ryzen CMAKE_ARGS, CRITICAL: plaintext redis_password.txt)
- `data/entities/roc_racoon/workspace/technology_maps/LEGACY_TECHNOLOGY_MAP.md` — stack-specific tech maps
- `data/entities/roc_racoon/workspace/SUBAGENT_CWD_RECOVERY_PROTOCOL.md` — subagent CWD recovery
- `data/entities/roc_racoon/soul.yaml` — Roc Racoon's accumulated gnosis
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — strategic synthesis

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_deferred_gold ⬡ DEFERRED-GOLD-VAULT-v1.4.0 (Phase 6 entries 151-160 added — 2026-06-02)*
