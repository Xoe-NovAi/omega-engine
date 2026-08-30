# 🔱 Legacy Stack Technology Map — Where Everything Lives
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_tech_map ⬡ v1.0.0
# Last Updated: 2026-06-02
# Purpose: Map every legacy stack, its size, its llama-cpp artifacts, and how to navigate to them.
# This is the "I forgot where it was" rescue file.

---

## §0 The Master Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LEGACY STACK TERRITORY                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  /home/arcana-novai/Documents/                                           │
│  ├── Xoe-NovAi/                          [active — DO NOT MINE]         │
│  │   ├── omega-engine/                   ← CURRENT ENGINE                │
│  │   ├── omega-stack-legacy/             🔥 2.9G (5 refs)               │
│  │   └── xna-omega-legacy/               💎 560M (5 refs)               │
│  │                                                                          │
│  ├── Archives/                                                          │
│  │   └── Old-Stacks/                     📦 117M (5 refs)               │
│  │       ├── Xoe-NovAi/                  [4-service complete stack]     │
│  │       ├── stack-cat-v0_1_2-full/                                       │
│  │       ├── XNAi-v0_1_2/                                                │
│  │       └── 10_15_1212/                 [latest stack-concat]          │
│  │                                                                          │
│  ├── Cursor.old/                        🔥 21 llama-cpp refs            │
│  ├── .cursor.old/                       💎 4 llama-cpp refs             │
│  ├── docs-backup/                        📚 46M (5 refs)                │
│  ├── docs_1/                             📚 17M (5 refs)                │
│  └── xnaif-files/                        📋 58M (5 refs)                │
│                                                                          │
│  /home/arcana-novai/archive/                                            │
│  └── foundation-legacy/                  🔥 861M (5 refs)               │
│      └── versions/Xoe-NovAi/             [XNAi rag_app]                 │
│                                                                          │
│  /media/arcana-novai/omega_library/                                     │
│  ├── intake/                             🔥 20 llama-cpp refs            │
│  │   ├── mining_queue/                                                 │
│  │   ├── inbox/                                                        │
│  │   └── RoC Racoon Test v1 - LM Studio.md                            │
│  └── podman-storage/                     💎 32 llama-cpp refs            │
│                                                                          │
│  /media/arcana-novai/omega_vault/                                       │
│  └── from main partition/                📦 12G (9 refs)                │
│      └── GitHub/Xoe-NovAi/                                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## §1 Stack Profiles

### 1.1 xna-omega-legacy 💎
- **Path**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/`
- **Size**: 560M
- **Era**: Temple Grade (2025-2026)
- **Quality**: Battle-tested, has unit tests, has benchmarks
- **Mining Status**: ✅ MINED (Phase 1 complete — see `mining_reports/01_xna_omega_legacy.md`)

#### Key llama-cpp Artifacts (paths you can return to)

```
src/omega/providers/local/
├── client.py                    # LocalLlmClient — THE native llama-cpp wrapper
├── config.py                    # LocalLlmConfig — full dataclass schema
├── plugin.py                    # LocalLlmPlugin — ProviderPlugin base class
├── library_augmented.py         # RAG bridge
└── __init__.py

src/omega/plugins/sight/
└── sight_plugin.py              # Moondream2 vision (llama_cpp.MoondreamChatHandler)

src/omega/security/
└── benchmark_llama_cpp.py       # llama-bench CLI wrapper

tests/benchmarks/
└── local_llm_benchmark.py       # Direct LocalLlmClient benchmark (18.50 tok/s target)

config/
├── config.toml                  # [models] and [performance] sections
├── entity_model_affinity.yaml   # 10 Pillar Keeper model mapping
└── domain-routing.yaml

knowledge/strategy/
└── HP-5700U-OPTIMIZATION.md     # 💎 THE optimization doc (165 lines)
```

#### Best Gold From This Stack

| Item | Path | Why Important |
|------|------|---------------|
| **`LocalLlmClient`** | `src/omega/providers/local/client.py:1-291` | The actual native llama_cpp.Llama wrapper. Port 1:1. |
| **`LocalLlmConfig`** | `src/omega/providers/local/config.py:19-86` | Full schema for fine-grained tuning. |
| **`_enforce_affinity()`** | `client.py:41-48` | psutil.cpu_affinity() core pinning. |
| **`reload()` with fallback** | `client.py:142-197` | Atomic model swap with revert. |
| **`LlamaPromptLookupDecoding`** | `client.py:75-90` | ngram-simple speculative decoding. |
| **`HP-5700U-OPTIMIZATION.md`** | `knowledge/strategy/HP-5700U-OPTIMIZATION.md:1-165` | THE optimization doc. Build flags, runtime config, thermal limits. |
| **`CapacityLimiter(1)`** | `plugin.py:60` | Single-flight inference (no OOM). |
| **Lazy import pattern** | `client.py:60-67` | Optional-dep pattern (import llama_cpp inside method, not at module top). |
| **`local_llm_benchmark.py`** | `tests/benchmarks/local_llm_benchmark.py` | Establishes 18.50 tok/s baseline. |
| **`Hp CPU Zen 2 flags`** | `HP-5700U-OPTIMIZATION.md:66-91` | The cmake command. NEVER znver3, NEVER native, NEVER AVX512. |

#### Key Warnings (Gotchas Found)

1. **Don't use `-march=znver3`** — it's Zen 3/4 only and crashes on Zen 2
2. **Don't use `-march=native`** — enables AVX512 on Zen 2 → SIGILL
3. **Don't use `DGGML_AVX512=ON`** — not supported on Zen 2
4. **Don't trust `config.toml:78`** — it says "Zen 3" but actual CPU is Zen 2
5. **Don't enable Vulkan iGPU** — 9% gain not worth instability
6. **Don't use `["User:", "\nUser:"]` stop sequences** — base-model legacy, not chat-tuned
7. **Don't use LangChain `LlamaCpp` wrapper** — adds dep for no functional gain
8. **Don't use `use_mlock=true`** — requires CAP_IPC_LOCK capability

---

### 1.2 omega-stack-legacy 🔥 (✅ MINED — Phase 2 + 2.5 complete)
- **Path**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/`
- **Size**: 2.9G (largest legacy stack)
- **Era**: Era 4 (Mar-Apr 2026) — Unified repo, 33K files, ODE v1.3
- **Quality**: High — has unit tests, has benchmarks, has 3 Dockerfiles
- **Mining Status**: ✅ MINED (Phases 2 + 2.5 complete)

#### Key llama-cpp Artifacts (verified)

```
dependencies.py                                   # 1136L — LangChain LlamaCpp wrapper (lines 460-580)
sight_plugin.py                                   # 86L — Moondream2 vision (native Llama.from_pretrained)
infra/docker/Dockerfile:36-43                     # Vulkan + OpenBLAS + AVX2 + F16C + FMA production build
hf-spaces-demo/Dockerfile                         # CPU-only wheel install
hf-spaces-deploy/Dockerfile:14-16                 # JamePeng prebuilt wheel (llama-cpp 0.3.22)
hf-spaces-demo/app.py                             # Native Llama() loader (n_ctx=4096, n_batch=512)
infra/containers/Containerfile.production        # Non-ML RAG API
Makefile:2362-2403                                # chat-llama, infer-llama targets
config.toml                                       # 459L — codename "Gnostic Vault"
app/XNAi_rag_app/core/
├── config_loader.py                              # 812L — Pydantic-validated TOML config
├── embeddings_shim.py                            # LlamaCppEmbeddings compatibility
├── entities/enhanced_handler.py                  # 262L — 5-pattern entity routing
├── entities/registry.py                          # PersistentEntity registry
├── vulkan_acceleration.py                        # Vulkan GPU framework
├── degradation.py                                # 4-tier DegradationManager
├── multi_provider_dispatcher.py:789              # _dispatch_local() STUB (the gap!)
├── health/health_monitoring.py                   # 627L — Ryzen health probes
├── health/health_checker.py                      # 569L — base HealthChecker
└── health/recovery_manager.py                    # graceful degradation
app/XNAi_rag_app/api/healthcheck.py:320-410       # check_ryzen() validates n_threads, f16_kv, OPENBLAS_CORETYPE
app/XNAi_rag_app/workers/knowledge_miner.py       # 426L — background miner (CapacityLimiter(1))
app/XNAi_rag_app/api/main.py, middleware.py       # FastAPI app skeleton
src/omega/circuit_breaker.py                      # 36L — ORIGINAL simple port (confirmed source)
```

#### Expert Knowledge Gems (Phase 2.5 — 244+ files)

```
expert-knowledge/
├── architect/
│   ├── int8_kv_cache.md                          # Q8_0 KV cache pattern
│   ├── ryzen_5700u_steering.md                   # Zen 2 core pinning
│   ├── build_recovery_disk_management.md         # 8GB reclaim workflow
│   ├── podman_mount_conflicts.md                 # mount validator
│   ├── podman_rootless_permissions.md            # ⚠️ uses :U (CONTRADICTS M6)
│   ├── rootless_podman_runtime_dirs.md           # Sticky 1777 pattern ✅
│   ├── architect-expert-knowledge-base.md        # 230L Sec-Architect-20260120
│   └── lore-extraction.md                        # 5 Golden Rules + 5 Anti-Patterns
├── infrastructure/
│   ├── llama-cpp-optimization.md                 # n_threads=6, n_gpu_layers=0
│   ├── podman_permissions_mastery.md             # ⚠️ uses :U (CONTRADICTS M6)
│   ├── podman_quadlet_mastery.md                 # .pod, Notify=healthy patterns
│   ├── ryzen-hardening-expert-v1.0.0.md          # ⚠️ uses :U (CONTRADICTS M6)
│   └── REDIS-HA-DECISION.md                      # 💎 "Keep Standalone + Watchdog"
├── agent-tooling/
│   ├── anyio-structured-concurrency.md           # ✅ Enforces Mandate 1
│   └── redis-stream-bus-patterns.md              # Multi-agent comms
├── environment/
│   ├── rootless_podman_u_flag.md                 # ⚠️ CONTRADICTS M6
│   ├── ryzen-5700u-optimization.md               # zRAM swappiness=180
│   ├── multi-agent-resource-limits.md            # 6.6GB RAM budget
│   └── development-workflows/hardware-profile.md # ⚠️ factual errors (Zen 4/DDR5)
├── patterns/
│   ├── ERROR-HANDLING-PATTERNS.md                # Default Deny, Circuit Breaker, DLQ
│   ├── ASYNC-ANYIO-BEST-PRACTICES.md             # ✅ migration table from asyncio
│   └── phase5a-best-practices.md                 # zRAM production defaults
├── research/
│   ├── ERROR-HANDLING-PATTERNS-2026-02-23.md     # 418L — comprehensive error reference
│   ├── MODEL-DISCOVERY-SYSTEM-v1.0.0.md          # 810L — mandatory verification protocol
│   ├── FASTEMBED-ONNX-EMBEDDING-GUIDE-2026-02-18.md # 247L — DO NOT USE table
│   ├── ekb-research-master-v1.0.0.md             # Sovereign Research Expert
│   └── ...
├── protocols/
│   ├── LLAMA-CPP-PYTHON-SERVICE-PROTOCOL.md      # 264L — full server config
│   └── multi-agent-orchestration.md              # AHP + Static Priority
├── model-reference/
│   ├── QUICK-REFERENCE.md                         # Compact model cheat sheet
│   ├── XNAI-MODEL-INTELLIGENCE-MASTER.md         # 93L — master report
│   └── phi/phi-3-omnimatrix.md                   # Phi-3 evaluation
├── embeddings/
│   └── embeddinggemma-setup-v1.0.0.md            # Matryoshka Representation Learning
├── coder/
│   ├── uv_timeout_optimization.md                # 20L — build timeout fix
│   └── buildkit_best_practices.md                # cache mount pattern
├── sync/
│   └── sovereign-synergy-expert-v1.0.0.md        # Context Concatenation, YAML lock
└── AGENT-CLI-MODEL-MATRIX-v3.0.0.md              # 421L — tiered model map
```

#### Best Gold From This Stack (NEW Phase 2 + 2.5)

| Item | Path | Why Important |
|------|------|---------------|
| **`int8_kv_cache.md`** | `expert-knowledge/architect/int8_kv_cache.md:1-36` | Validates current engine's q8_0 config. |
| **`ryzen_5700u_steering.md`** | `expert-knowledge/architect/ryzen_5700u_steering.md:1-36` | Validates Zen 2 core pinning. **CONTRADICTS** on OMP_NUM_THREADS (1 vs 6). |
| **`LLAMA-CPP-PYTHON-SERVICE-PROTOCOL.md`** | `expert-knowledge/protocols/...md:1-264` | Full operational protocol for the server mode. |
| **`uv_timeout_optimization.md`** | `expert-knowledge/coder/uv_timeout_optimization.md:1-20` | The build timeout fix that prevents silent hangs. **Top 5 deferred**. |
| **`AGENT-CLI-MODEL-MATRIX-v3.0.0.md`** | `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md:1-421` | Authoritative tiered model map. **Tier 5 only relevant** to current engine. |
| **`check_ryzen()` health probe** | `app/XNAi_rag_app/api/healthcheck.py:320-410` | Runtime validation of n_threads, f16_kv, OPENBLAS_CORETYPE. Drop-in port candidate. |
| **`check_llama_compilation()` test** | `app/XNAi_rag_app/core/verify_imports.py:110-118` | Build verification — verifies CMAKE flags took effect. Drop-in port candidate. |
| **`Sticky 1777 pattern`** | `expert-knowledge/architect/rootless_podman_runtime_dirs.md:11-25` | Solves rootless container perms without `:U` flag. |
| **`REDIS-HA-DECISION.md`** | `expert-knowledge/infrastructure/REDIS-HA-DECISION.md:17,34` | Explicit decision: don't over-engineer. **💎 GOLD**. |
| **`MODEL-DISCOVERY-SYSTEM-v1.0.0.md`** | `expert-knowledge/research/MODEL-DISCOVERY-SYSTEM-v1.0.0.md:1-810` | Mandatory verification protocol before claiming a model doesn't exist. |
| **`FASTEMBED-ONNX-EMBEDDING-GUIDE-2026-02-18.md`** | `expert-knowledge/research/...md:1-247` | DO NOT USE table — why PyTorch embeddings are wrong. |
| **`anyio-structured-concurrency.md`** | `expert-knowledge/agent-tooling/anyio-structured-concurrency.md:1-35` | Directly enforces Mandate 1. |
| **`ASYNC-ANYIO-BEST-PRACTICES.md`** | `expert-knowledge/patterns/ASYNC-ANYIO-BEST-PRACTICES.md:1-149` | Migration table from asyncio to AnyIO. |
| **`OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md:458-463`** | (full path) | ⚠️ OpenCode memory leak warning — restart every 2-3 hrs. |

#### Confirmed (Validates Current Engine)

| Phase 2.5 finding | Current Engine Implementation |
|-------------------|-------------------------------|
| `type_k=8, type_v=8` (Q8_0 KV cache) | `config/providers.yaml` (native-gguf type_k: 8, type_v: 8) ✅ |
| Zen 2 physical cores `[0,2,4,6]` | `config/providers.yaml` (cores: [0, 2, 4, 6]) ✅ |
| OMP_NUM_THREADS=6, OMP_PROC_BIND=close | `config/models.yaml` ✅ |
| `-march=znver2` build flags | `src/omega/oracle/cpu_optimizer.py` ✅ |
| Local-First fabric | `config/providers.yaml` (priority 0 native-gguf) ✅ |
| llama-cpp server on :8080 | `config/models.yaml` (llama_server block) ✅ |
| Vulkan-enabled Dockerfile pattern | NOT YET — but in `infra/docker/Dockerfile:36-43` is drop-in |
| `UV_HTTP_TIMEOUT=120` build env | NOT YET — in DEFERRED_GOLD_TRACKER #104 |

---

### 1.3 foundation-legacy 🔥 (✅ MINED — Phase 3 complete)
- **Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/`
- **Size**: 861M
- **Era**: Era 2 (Oct-Nov 2025) — XNAi v0.1.5-stable "Polymath Foundation"
- **Quality**: High — 94.2% test coverage, 215 tests, 8 health checks
- **Mining Status**: ✅ MINED (Phase 3 complete)
- **Subagent used**: `explore` (had to use bash heredoc workaround — no write tool)

#### Key llama-cpp Artifacts (verified — 30+ files)

```
app/XNAi_rag_app/
├── dependencies.py                              # 738L — LangChain LlamaCpp + LlamaCppEmbeddings
├── healthcheck.py                               # 713L — check_ryzen() lines 336-394, check_telemetry() lines 447-503
├── verify_imports.py                            # 285L — check_llama_compilation() lines 114-129
├── main.py                                      # 737L — uses get_llm()
├── crawl.py                                     # 1209L — uses LlamaCppEmbeddings for in-crawl embedding
├── voice_interface.py                           # 1031L — VoiceCircuitBreaker class lines 241-281
├── get_llm() / get_embeddings()                 # get_vectorstore() with FAISS backup fallback (up to 5 backups)
├── filter_llama_kwargs()                        # validator
scripts/
├── curation_worker.py                           # 107L — 5th service, blpop Redis queue worker
tests/
├── test_circuit_breaker_chaos.py                # 230L — validates pybreaker 3-failure-then-OPEN
Dockerfile.api                                   # 247L — llama-cpp 0.3.16 (built from source), NO Vulkan
Dockerfile.chainlit                              # 166L — chainlit-only
Dockerfile.crawl                                 # crawler-only
Dockerfile.curation_worker                       # queue worker only
```

#### Best Gold From This Stack (NEW Phase 3)

| Item | Path | Why Important |
|------|------|---------------|
| **`pybreaker==0.7.0`** | `tests/test_circuit_breaker_chaos.py` | Standardized library. Replaces current 36L custom + rejected 579L Redis. Drop-in 2-hr port. **💎 GOLD** |
| **`check_telemetry()`** | `app/XNAi_rag_app/healthcheck.py:447-503` | 8-disables runtime audit. Direct enforcement of Mandate 8 (Zero Telemetry) as a health probe. **💎 GOLD** |
| **5 mandatory design patterns framework** | `app/XNAi_rag_app/blueprint/section-1.md` | Pattern 1-5: Import Path Resolution, Retry, Non-Blocking Subprocess, Atomic fsync, Circuit Breaker. **💎 GOLD** — adopt framework |
| **Grok Vulkan Code Guide** | `app/XNAi_rag_app/blueprint/grok-vulkan-code-guide.md` | Unifies omega-stack's Vulkan Dockerfile with runtime `VULKAN_ENABLED` toggle + `/dev/dri` iGPU passthrough. 1-day port. |
| **`VoiceCircuitBreaker`** | `app/XNAi_rag_app/voice_interface.py:241-281` | Domain-specific CB for STT/TTS — unique pattern. |
| **`get_vectorstore()` with FAISS backup fallback** | `app/XNAi_rag_app/dependencies.py` | Up to 5 backup stores. Resilience pattern. |
| **5th service: `curation_worker`** | `scripts/curation_worker.py:107` | `blpop` Redis queue worker. Different from 4-service Docker Compose. |
| **`filter_llama_kwargs()` validator** | `app/XNAi_rag_app/dependencies.py` | Validates llama-cpp config against allowed params. |
| **No-Vulkan Dockerfile.api:133** | (explicit) | Foundation's API Dockerfile DISABLES Vulkan. Contradicts omega-stack's enable. Both used in production at different times. |
| **UID 1001 in docker-compose.yml:124** | ⚠️ LEGACY | Conflicts with current Mandate 6 (UID 1000). Do not port. |

#### Already Ported (Validates Current Engine)

| Phase 3 finding | Current Engine Implementation |
|-----------------|-------------------------------|
| `n_threads=6, f16_kv=true` | `config/providers.yaml` (n_threads: 6) ✅ |
| `n_ctx=4096` context window | `config/models.yaml` (default n_ctx: 8192) ✅ |
| OpenBLAS CMAKE args | `src/omega/oracle/cpu_optimizer.py` ✅ |
| AVX2 + FMA + F16C | `src/omega/oracle/cpu_optimizer.py` ✅ |
| AnyIO semantics | ✅ Mandate 1 |

#### Items NOT to Port (Mandate Violations)

| Rejected | Source | Reason |
|----------|--------|--------|
| `asyncio.run_in_executor` | `dependencies.py:323,406,558` | **Violates Mandate 1** (AnyIO only) |
| UID 1001 in docker-compose.yml:124 | `docker-compose.yml` | **Violates Mandate 6** (host UID 1000) |
| 579L Redis circuit breaker | Not in foundation, but referenced | Already replaced with simpler versions |
| `Dockerfile.api` (no Vulkan) | `Dockerfile.api:133` | omega-stack's Vulkan Dockerfile is the better reference |

---

### 1.4 omega_library/podman-storage 💎 (✅ MINED — Phase 4 complete)
- **Path**: `/media/arcana-novai/omega_library/podman-storage/`
- **Size**: 152 overlay layers + 4 volume mounts
- **Era**: Operational container — currently or recently running
- **Quality**: ⭐ Accidental time machine — 3 providers.py + 4 model_gateway.py + cpu_optimizer.py (552L) + 5 configs. 32 llama-cpp refs is VERY high — complete working build
- **Mining Status**: ✅ MINED (Phase 4 complete — see `mining_reports/04_podman_storage.md`)

#### Key llama-cpp Artifacts (verified)

```
overlay/<layer-id>/diff/
├── app/omega/oracle/providers.py                    # 3 distinct versions
├── app/omega/oracle/model_gateway.py                # 4 distinct versions
├── app/omega/oracle/cpu_optimizer.py                # 552L, fully-formed
├── app/config/models.yaml                           # 459L "Gnostic Vault"
└── app/config/wads/arcana_novai/agents/lucifer.md   # P7 Gnosis agent
```

#### Best Gold From This Stack (Phase 4)

| Item | Path | Why Important |
|------|------|---------------|
| **Atomic `trace_id` migration pattern** | `app/omega/oracle/providers.py:16,28,66,99,127,197` (layer 29693566) | 6 `generate()` methods got `trace_id` added simultaneously. Canonical pattern for forward-compatible interface changes. |
| **Google API key in `x-goog-api-key` header** | `app/omega/oracle/providers.py:30,43-47` (layer 29693566) | Security upgrade from `?key={api_key}` query string. Headers are not logged by proxies/APM. |
| **Mock provider setup-mode UX** | `app/omega/oracle/providers.py:127-138` (layer 29693566) | Actionable next-steps message when no inference backend is available. |
| **Per-model KV cache YAML** | `app/config/models.yaml:140-158` (layer 705317e8) | `fp8 → q8_0 → f16` per-model override. |
| **Quantization memory table** | `app/omega/oracle/cpu_optimizer.py:435-438` | `q2_k=300, q3_k_m=400, q4_0=450, q4_k_m=500, q5_k_m=600, q6_k=700, q8_0=800, f16=1400` MB/billion params. |
| **ChatML stop tokens** | `app/omega/oracle/providers.py:213` | `stop=["</s>", "User:", "\n\n"]`. Prevents hallucinated conversation turns. |

---

### 1.5 Cursor.old ⚠️ (SKIPPED — Phase 5)
- **Path**: `/home/arcana-novai/Documents/Cursor.old/`
- **Size**: TBD
- **Era**: N/A
- **Quality**: ❌ NOT a code stack — Cursor editor's user data dir (Cache, Cookies, GPUCache, Code Cache)
- **Mining Status**: ⏭️ SKIPPED (false positive in original recon — see Roc Racoon directive d-rr-005)

**Lesson**: Always verify directory contents before assuming stack type.

---

### 1.6 Old-Stacks 📦 (✅ MINED — Phase 6 complete)
- **Path**: `/home/arcana-novai/Documents/Archives/Old-Stacks/`
- **Size**: 117M
- **Era**: Eras 1-3 (Aug 2025 - Mar 2026) — earliest complete stack
- **Quality**: ⭐ Real working code v0.1.4-stable + 714-line blueprint + 4-service Docker Compose
- **Mining Status**: ✅ MINED (Phase 6 complete — see `mining_reports/06_old_stacks.md`)

#### Key Subdirectories (verified)

```
Xoe-NovAi/                    [4-service complete stack — pre-Omega, 89M, ~300 files]
XNAi-v0_1_2/                  [XNAi version 0.1.2 + 714-line blueprint, 27M, ~50 files]
10_15_1212/                   [Oct 15 stack-concat .md dump, 660K, 30 files]
10_15_1452/                   [Oct 15 stack-concat .md dump, 684K, 30 files]
20251015_144704/              [Empty marker, 8K]
```

#### Best Gold From This Stack (Phase 6)

| Item | Path | Why Important |
|------|------|---------------|
| **4-service Docker Compose** | `Xoe-NovAi/docker-compose.yml:14-260` | redis + rag + ui + crawler + curation_worker. Healthcheck-conditional `depends_on`, zero-trust security. |
| **Ryzen CMAKE_ARGS** | `Xoe-NovAi/Dockerfile.api:132-134` | `-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON`. Battle-tested Zen 2 build. |
| **`filter_llama_kwargs()`** | `Xoe-NovAi/dependencies.py:64-98` | Closes the `ValueError: Invalid parameter` bug. |
| **`xnai_blueprint.md` (714 lines)** | `XNAi-v0_1_2/xnai_blueprint.md` | v0.1.4-stable production spec. 5 mandatory patterns. Validates current engine's architecture. |
| **`redis_password.txt`** | `Xoe-NovAi/redis_password.txt` | ⚠️ CRITICAL: plaintext `1234567890123456` — Mandate 6 + 9 violation. Must be deleted. |

---

## §2 Search Recipes (For Future Mining)

### 2.1 Find all llama-cpp references in any stack
```bash
grep -rln "llama_cpp\|llama-cpp\|Llama(" /path/to/stack/ \
  --include="*.py" --include="*.yaml" --include="*.md" --include="*.toml" --include="*.sh"
```

### 2.2 Find the actual Llama() instantiation
```bash
grep -rln "Llama(" /path/to/stack/ --include="*.py"
```

### 2.3 Find optimization config
```bash
grep -rln "n_ctx\|n_threads\|n_gpu_layers\|type_k\|type_v\|f16_kv\|speculative" /path/to/stack/
```

### 2.4 Find build/compile configs
```bash
grep -rln "cmake\|CMAKE_ARGS\|march=\|znver\|AVX" /path/to/stack/
```

### 2.5 Find Zen 2 / Ryzen optimization
```bash
grep -rln "zen2\|zen_2\|ryzen\|5700U\|AVX2\|cpu_optimizer" /path/to/stack/
```

### 2.6 Find test files
```bash
find /path/to/stack/tests/ -name "*llama*" -o -name "*local*" -o -name "*llm*"
```

---

## §3 Cross-Stack Patterns (When You See One, Look In All)

When you find a pattern in one stack, search for it in ALL stacks. The same code often lives in many places:

| Pattern | Search For |
|---------|-----------|
| Provider class | `class.*Provider\|class.*Backend\|class.*Plugin.*Provider` |
| Model loading | `Llama(\|model_path=\|n_ctx=` |
| Configuration schema | `model_path.*str\|n_ctx.*int.*=.*[0-9]` |
| Optimization | `march=\|znver\|AVX\|cpu_threads\|n_threads` |
| Observability | `tracer.start_as_current_span\|span.set_attribute` |
| Error handling | `except ImportError\|except RuntimeError\|retry_if_exception_type` |
| Resource control | `CapacityLimiter\|Semaphore\|anyio.to_thread.run_sync` |

---

## §4 File Path Decoder (for long legacy paths)

Common prefixes you might see in references:

| Prefix | Decodes To |
|--------|-----------|
| `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/` | xna-omega-legacy |
| `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/` | omega-stack-legacy |
| `/home/arcana-novai/Documents/Archives/Old-Stacks/` | Old-Stacks |
| `/home/arcana-novai/archive/foundation-legacy/` | foundation-legacy |
| `/media/arcana-novai/omega_library/` | omega_library |
| `/media/arcana-novai/omega_vault/` | omega_vault |
| `/home/arcana-novai/Documents/Cursor.old/` | Cursor.old |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_tech_map ⬡ TECHNOLOGY-MAP-v1.1.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
