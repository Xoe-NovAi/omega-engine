⚠️ **DEPRECATED NOMENCLATURE** — This document uses legacy terminology that has been renamed:
- **LLOC** → **Meditate** (single-inference cognitive prism)
- **HLOC** → **MC (Mastermind Council)** (multi-subagent same-session)
- **Octave Council** → **Lens Framework** (composable cognitive perspectives)
- **10 Pillars** → **Omega Pantheon** (lens-primary; pillar is optional WAD metadata)
- **P1–P10** references → **Lens names** (infrastructure, persistence, engineering, etc.)

This naming was ratified 2026-07-16 and applied across the fleet on 2026-07-18.
Content below is preserved as-is for historical reference. See `config/wads/_omega_default/meditate/lenses.yaml` for current lens definitions.

# Mining Report #03: foundation-legacy (Xoe-NovAi v0.1.5-stable)
# Subagent: Roc Racoon Mining Subagent #3 (explore)
# Stack: foundation-legacy (Era 2 — Oct/Nov 2025, XNAi v0.1.5-stable "Polymath Foundation")
# Size: 861M
# Date: 2026-06-02
# Trace: mining-foundation-llama-cpp-20260602
# Status: COMPLETE
# AP Token: AP-MINING-FOUNDATION-LLAMA-CPP-v1.0.0

---

## Section 0 Executive Summary

The `foundation-legacy` stack is the **production-predecessor to omega-stack-legacy** — it is the working "Polymath Foundation" codebase that shipped as the v0.1.4-stable / v0.1.5 release of the XNAi RAG stack. It **confirms** the LangChain `LlamaCpp` wrapper pattern (vs xna-omega's native `llama_cpp.Llama`) and **extends** with three notable new artifacts:

1. **`pybreaker==0.7.0` standardization** — explicit `CircuitBreaker(fail_max=3, reset_timeout=60)` as "Pattern 5" with chaos tests (`test_circuit_breaker_chaos.py`) — this is the **canonical**, more portable pattern than the 579-line Redis-backed one in omega-stack-legacy
2. **`check_telemetry()` 8-disables runtime audit** — a health-check function that *enforces* Mandate 8 (Zero Telemetry) at runtime, not just at config
3. **The "5 mandatory design patterns" framework** — the blueprint's Pattern 1-5 is the cleanest articulation of the v0.1 era's design discipline (Import Path Resolution, Retry, Non-Blocking Subprocess, Atomic fsync, Circuit Breaker)

The 4-service Docker Compose (redis, rag, ui, crawler) is **different** from omega-stack-legacy's compose, and the **5th `curation_worker` service** (a `blpop` Redis queue worker) is a unique piece not seen in the other stacks. The Stack-Cat documentation generator (15K line bash) and Code-Weaver project docs (multi-agent orchestration prompts) are also unique.

The current engine has **already ported** the core llama-cpp wisdom (Zen 2 build flags, q8_0 KV cache, n_threads=6, `f16_kv`, `use_mlock`). The **new actionable value** is the `pybreaker` pattern (simpler than the 36-line or 579-line alternatives), the `check_telemetry()` audit, the `VoiceCircuitBreaker` class, the curation_worker Redis pattern, and the 5-patterns framework.

---

## Section 1 Inventory — llama-cpp / GGUF / Native Inference Artifacts

### 1.1 Primary Source Code

| File | Lines | Description |
|------|-------|-------------|
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/dependencies.py` | 738 | **`get_llm()` / `get_embeddings()`** — LangChain `LlamaCpp` + `LlamaCppEmbeddings` wrappers, `filter_llama_kwargs()` validator, `get_vectorstore()` with FAISS backup fallback (up to 5 backups). |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/healthcheck.py` | 713 | **`check_ryzen()` lines 336-394** + **`check_telemetry()` lines 447-503** — 8-telemetry-disable runtime audit, 7 modular health probes. |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/verify_imports.py` | 285 | **`check_llama_compilation()` lines 114-129** — verifies `llama_cpp.llama_model_default_params()` has `n_threads=6` and `f16_kv=true`. |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/main.py` | 737 | Uses `get_llm()` (line 542, 623); `pybreaker` referenced in blueprint (Section 1 Pattern 5). |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/crawl.py` | 1209 | Uses `LlamaCppEmbeddings` (line 1014-1019) for in-crawl embedding. |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/voice_interface.py` | 1031 | **`VoiceCircuitBreaker` class lines 241-281** — unique domain-specific circuit breaker for STT/TTS. |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/scripts/curation_worker.py` | 107 | **5th service** — `blpop` Redis queue worker pattern. |
| `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/tests/test_circuit_breaker_chaos.py` | 230 | **Chaos test** — validates `pybreaker` 3-failure-then-OPEN behavior. |

### 1.2 Dockerfiles (3 distinct images)

| Dockerfile | Lines | llama-cpp Version | CMAKE Args | Notes |
|------------|-------|-------------------|-----------|-------|
| `Dockerfile.api` | 247 | 0.3.16 (built from source) | `-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON` (line 133) | **NO Vulkan** — VULKAN explicitly NOT enabled. Uses 5-retry `apt-get update` with exp backoff (lines 38-53) |
| `Dockerfile.chainlit` | 166 | (chainlit-only, no llama-cpp) | n/a | BuildKit cache mounts (lines 50-60), 12% size reduction via site-packages cleanup |
| `Dockerfile.crawl` | (similar) | (crawler-only) | n/a | crawl4ai only |
| `Dockerfile.curation_worker` | (similar) | (queue worker only) | n/a | blpop consumer only |

### 1.3 Configuration & Build Files

| File | Lines | Purpose |
|------|-------|---------|
| `requirements-api.txt` | 100 | Pinned deps: `langchain-core==0.3.79`, `langchain-community==0.3.31`, `faiss-cpu==1.12.0`, **`pybreaker==0.7.0`** (line 88), `tenacity==9.1.2` (line 86). **llama-cpp-python is commented out** (line 30) — must be compiled in build. |
| `requirements-chainlit.txt` | 109 | Voice stack: `faster-whisper==1.2.1`, `ctranslate2>=4.0.0`, **`piper-tts==1.3.0`** (PRIMARY ONNX TTS, no torch), `pyttsx3==2.90` fallback |
| `versions/versions.toml` | 50 | Centralized version matrix (used by `update_versions.py` for version sync) |
| `versions/scripts/update_versions.py` | (any) | **Version sync script** — automatically syncs requirements files from versions.toml |
| `versions/scripts/build_monitor.py` | (any) | Build progress monitor |
| `config.toml` | 524 | `[models]` (line 36-45): `llm_path = "/models/local/all/gemma-3-4b-it-UD-Q5_K_XL.gguf"`, `embedding_path = "/embeddings/all-MiniLM-L12-v2.Q8_0.gguf"`, `llm_context_window = 2048`. `[healthcheck]` (line 275-282): 8 health targets. |
| `Makefile` | 778 | 75+ targets including `wheelhouse`, `download-models`, `voice-test`, `stack-cat`, `benchmark`. **wget lines 44-47** for `gemma-3-4b-it-UD-Q5_K_XL.gguf` and `all-MiniLM-L12-v2.Q8_0.gguf`. |

### 1.4 Docker Compose (`docker-compose.yml`)

**Lines: 358 | 5 services (4 persistent + curation_worker) | 4 networks: `xnai_network`**

| Service | Image | Port | Memory | CPU | Notes |
|---------|-------|------|--------|-----|-------|
| `redis` | redis:7.4.1 | 6379 | (unlimited) | (none) | `maxmemory 512mb`, `appendfsync everysec`, `--protected-mode yes`, `tmpfs: /tmp:mode=1777,size=512m` (line 48) |
| `rag` | (built from `Dockerfile.api`) | 8000 + 8002 | 4G | 2.0 | `cap_add: [SETGID, SETUID, CHOWN]` (line 127-130), `cap_drop: ALL` (line 126), `user: ${APP_UID}:${APP_GID}` (line 124), `tmpfs: /tmp:mode=1777,size=512m` (line 133) |
| `ui` | (built from `Dockerfile.chainlit`) | 8001 | 2G | 1.0 | Chainlit UI, no llama-cpp |
| `crawler` | (built from `Dockerfile.crawl`) | (none) | 3G | 1.5 | crawl4ai worker |
| `curation_worker` | (built from `Dockerfile.curation_worker`) | (none) | 2G | 1.0 | **5th service — blpop Redis queue** |

**Permission model** (UNIQUE pattern):
- `user: "${APP_UID}:${APP_GID}"` (line 124) — UID 1001 (NOT 1000 — see "Contradictions" Section 8)
- `cap_drop: ALL` (line 126) — defense-in-depth
- `cap_add: [SETGID, SETUID, CHOWN]` (line 127-130) — minimal capabilities
- `security_opt: - no-new-privileges:true` (line 132) — prevent privilege escalation
- `tmpfs: /tmp:mode=1777,size=512m` (line 133) — Sticky 1777 pattern (matches deferred item #105)

### 1.5 Blueprint & Documentation (CRITICAL REFERENCE DOCS)

| File | Lines | Purpose |
|------|-------|---------|
| `docs/reference/blueprint.md` | 716 | **The Ultimate Blueprint v0.1.5** — "5 mandatory design patterns" (Section 1), 4-service topology (Section 3), 8-target health checks (Section 5.3), 42-issue resolution matrix (Appendix A), 11 Prometheus metrics (Section 6.3). The cleanest reference doc of this era. |
| `docs/implementation/phase-1.md` | 1080 | Phase 1 implementation: metadata enricher, semantic chunking, delta detection, groundedness observability |
| `docs/implementation/phase-2-3.md` | (large) | Phase 2-3 implementation |
| `docs/implementation/library-api.md` | 465 | Library API design |
| `docs/implementation/qdrant-integration.md` | 400 | Qdrant integration spec |
| `docs/runbooks/docker-build-troubleshooting.md` | 191 | **DNS retry logic, FastAPI version conflict, `importlib.util` syntax fix** — first known `importlib.util` fix (line 98-104) |
| `docs/runbooks/build-logging.md` | (mid) | Build log organization: `logs/wheelhouse/`, `logs/docker_build/`, `logs/build/downloads_*.json` |
| `docs/runbooks/voice-deployment.md` | 510 | Voice deployment runbook |
| `docs/runbooks/ingestion-system-enhancements.md` | 485 | Ingestion patterns |
| `docs/runbooks/docker-testing.md` | 335 | Docker testing approach |
| `docs/runbooks/security-fixes-runbook.md` | 195 | Security fixes |
| `docs/runbooks/make-up-test-results.md` | (any) | Makefile test results |
| `docs/runbooks/updates-running.md` | 35 | Updates tracker |
| `docs/STACK_STATUS.md` | 90 | **v0.1.5 deployment status** — Voice-to-voice + FAISS + Redis sessions + 8 telemetry disables |
| `docs/AI_ASSISTANT_GUIDE.md` | 165 | AI assistant guide (Gemini/Claude/Cline patterns) |
| `docs/START_HERE.md` | 140 | Onboarding doc |
| `docs/README.md` | 240 | Stack README |
| `docs/archive/code-review-sessions/Grok - Vulkan Enhancement code guide - January 10, 20.md` | 129 | **Vulkan integration guide** with proven `DGGML_VULKAN=ON` patterns |
| `docs/archive/code-review-sessions/Grok Code Audit - January 10 2026.md` | (any) | Holistic code audit (v0.1.5) |
| `docs/archive/code-review-sessions/Grok - Voice to Voice Code Audit - January 10, 20.md` | (any) | Voice-to-voice audit |
| `docs/archive/code-review-sessions/Grok - Vulkan Enhancement Audit - January 10, 20.md` | (any) | Vulkan audit (Phase 2 prep) |
| `docs/projects/Code-Weaver/Code_Weaver - Claude system prompt v1.0 - by Claude.md` | 970 | **Code-Weaver system prompt** — Claude orchestrator for multi-file edits |
| `docs/projects/Code-Weaver/xnai_v0.1.5_complete_stack_guide.md` | 1400 | Complete stack guide |
| `docs/projects/stack-butler/XNAi_v_012_Phase_1_Grok_10-14.md` | 1050 | Stack-butler era Grok session |
| `docs/projects/stack-scribe/` | (multi) | Stack-scribe project docs |
| `docs/projects/PIE/` | (multi) | Personal Intelligence Engine concept |
| `scripts/stack-cat/stack-cat` | 1023 | **Stack-Cat v0.1.5** — bash doc generator (de-concatenates markdown into individual files, generates `stack-cat-output/[timestamp]/`) |
| `scripts/stack-cat/groups.json` | (mid) | Group definitions for stack-cat |
| `scripts/stack-cat/whitelist.json` | (small) | File allowlist |
| `docs/personas/lilith.json` | 105 | Lilith persona (JSON, archetype=goddess) — **earliest known Lilith persona** |
| `docs/personas/odin.json` | 110 | Odin persona (JSON, archetype=god) |
| `knowledge/personas/{isis,lilith,odin,thoth}/` | (dirs) | Per-persona knowledge dirs (empty in this snapshot but structure documented) |

### 1.6 Scripts & Build Tools

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/preflight_checks.py` | 154 | Preflight security + env validation |
| `scripts/validate_config.py` | 175 | Config validation (TOML structure) |
| `scripts/telemetry_audit.py` | 180 | **8 telemetry disables runtime audit** (companion to `check_telemetry()`) |
| `scripts/doc_checks.sh` | 280 | Doc consistency checks |
| `scripts/build_logging.sh` | 150 | Build logging orchestrator |
| `scripts/enhanced_build_logging.sh` | 225 | Enhanced build logger |
| `scripts/verify_offline_build.sh` | 175 | Offline build verification |
| `scripts/download_wheelhouse.sh` | 300 | Wheelhouse downloader (offline build support) |
| `scripts/build_wheelhouse.sh` | 50 | Wheelhouse build trigger |
| `scripts/clean_wheelhouse_duplicates.sh` | 300 | Wheelhouse dedupe |
| `scripts/build_tracking.py` | 300 | Build tracking + reporting |
| `scripts/prebuild_validate.py` | 65 | Pre-build validation |
| `scripts/ingest_from_library.py` | 95 | Ingest from library (entry point) |
| `scripts/ingest_library.py` | 670 | Full ingestion pipeline (PIP version) |
| `scripts/curation_worker.py` | 107 | **5th service** — `blpop` queue worker |
| `scripts/query_test.py` | 490 | Query test runner |

### 1.7 Versions Management

| File | Lines | Purpose |
|------|-------|---------|
| `versions/versions.toml` | 50 | Centralized version matrix (single source of truth) |
| `versions/scripts/update_versions.py` | (mid) | Syncs requirements files from versions.toml |
| `versions/scripts/build_monitor.py` | (any) | Build progress monitor |
| `versions/version_report.md` | 30 | Version report output |
| `versions/logs/` | (dir) | Version history logs |

---

## Section 2 Delta from Prior Phases

### 2.1 xna-omega-legacy (Phase 1)

| Aspect | xna-omega-legacy (Phase 1) | foundation-legacy (Phase 3) | Status |
|--------|----------------------------|----------------------------|--------|
| **Provider class** | `LocalLlmClient` (291L) + `LocalLlmConfig` (125L) — **native `llama_cpp.Llama`** | LangChain `LlamaCpp` wrapper in `dependencies.py:223-310` | **DIFFERENT APPROACH** |
| **Embeddings** | (not in Phase 1) | `LlamaCppEmbeddings` (lines 336-393) — 50% memory savings vs HF | **NEW** |
| **Circuit breaker** | (not in Phase 1) | **`pybreaker==0.7.0`** (Pattern 5) + chaos test | **NEW — clean implementation** |
| **Vector store** | (not in Phase 1) | FAISS with **backup fallback chain** (up to 5 backups, `get_vectorstore()` lines 413-540) | **NEW PATTERN** |
| **KV cache** | `q8_0` per HP-5700U-OPTIMIZATION.md | `f16_kv=true` (line 67) + `use_mlock=true` + `use_mmap=true` | **DIFFERENT (f16 default, q8 deferred)** |
| **Build flags** | Zen 2 only, no Vulkan, `-march=znver2` | **OpenBLAS + AVX2 + FMA + F16C, NO Vulkan** (Dockerfile.api:133) | **SAME: no Vulkan** |
| **Build retries** | (not in Phase 1) | **5-retry `apt-get update` with exponential backoff** (Dockerfile.api:38-53) | **NEW — first occurrence in our corpus** |
| **Wheelhouse** | (not in Phase 1) | **Full wheelhouse system** (offline build, version matrix sync) | **NEW** |
| **Test coverage** | (not in Phase 1) | 94.2% (215/230) per blueprint Section 6.1 | **NEW** |
| **5 mandatory patterns** | (not in Phase 1) | **Documented and enforced** — Pattern 1 (imports), 2 (retry), 3 (non-blocking), 4 (fsync), 5 (pybreaker) | **NEW FRAMEWORK** |

### 2.2 omega-stack-legacy (Phase 2)

| Aspect | omega-stack-legacy (Phase 2) | foundation-legacy (Phase 3) | Status |
|--------|------------------------------|----------------------------|--------|
| **Provider class** | LangChain `LlamaCpp` in `dependencies.py:460-580` | LangChain `LlamaCpp` in `dependencies.py:223-310` | **SAME APPROACH** (confirms Phase 2 finding) |
| **Circuit breaker** | 36L `src/omega/circuit_breaker.py` (current engine source); 579L `core/circuit_breakers/circuit_breaker.py` (Redis, rejected) | **`pybreaker==0.7.0`** standardized, 5-line decorator | **DIFFERENT** — Phase 3 uses clean library, not custom |
| **Vulkan** | ENABLED in `infra/docker/Dockerfile:36-43` | **NOT ENABLED** in `Dockerfile.api:133` | **CONTRADICTS Phase 2** |
| **Embeddings** | `LlamaCppEmbeddings` shim in `core/embeddings_shim.py` | `LlamaCppEmbeddings` directly in `dependencies.py:336-393` | **SAME PATTERN, no shim** |
| **Vulkan in Grok audit** | (not in Phase 2) | **Detailed Grok Vulkan enhancement guide** (docs/archive/code-review-sessions/) | **NEW — Ph2 prep docs** |
| **Test coverage** | 276 tests (per Phase 2) | **215 tests, 94.2% coverage** per blueprint Section 6.1 | **PHASE 2 > PHASE 3** |
| **Entity system** | `EnhancedEntityHandler` 5-pattern routing (DIRECT/CONSULT/COMPARE/PANEL/CONSULT_OTHER) | (no entity system — RAG-only) | **PHASE 2 SUPERIOR** |
| **Voice** | (not in Phase 2) | **Full voice stack**: `VoiceCircuitBreaker`, `faster-whisper`, `piper-tts` (ONNX) | **NEW IN PHASE 3** |
| **5th service** | (4 services: redis, rag, ui, crawler) | **5 services: + curation_worker** (blpop Redis worker) | **NEW IN PHASE 3** |
| **Stack-Cat** | (not in Phase 2) | **1023-line bash doc generator** with de-concatenation | **NEW** |
| **Code-Weaver** | (not in Phase 2) | **Multi-agent orchestration prompts** (Claude system prompt) | **NEW** |
| **Personas** | (not in Phase 2) | **Lilith (goddess) + Odin (god)** JSON — earliest known in this lineage | **NEW** |
| **Telemetry audit** | (5 disables via env) | **`check_telemetry()` runtime audit** (8 disables) + `scripts/telemetry_audit.py` | **NEW** |
| **Health checks** | 8 modular probes in `healthcheck.py:320-410` | **8 modular probes** including telemetry check | **SAME COUNT, telemetry added** |

### 2.3 Confirmed Patterns (Consensus Across All 3 Stacks)

1. **LangChain `LlamaCpp` wrapper** is the dominant pattern in foundation + omega-stack (xna-omega is the outlier with native `llama_cpp.Llama`)
2. **`n_threads=6`** for Ryzen 7 5700U is universal
3. **`f16_kv=true` / q8_0** for KV cache (foundation says f16, others say q8_0; both are memory-optimized)
4. **`use_mlock=true` + `use_mmap=true`** for model loading
5. **`/dev/dri` iGPU passthrough** for Vulkan (only in omega-stack-legacy, the production-tested one)
6. **`Ollama` is rejected** as dependency (replaced by native `llama_cpp`)
7. **`HuggingFace transformers` is rejected** (zero-telemetry — `verify_imports.py:104-112`)
8. **No `:U` flag** (foundation uses `user: ${APP_UID}:${APP_GID}` instead, line 124)
9. **Sticky 1777 tmpfs** for `/tmp` (foundation line 48, 134, 188, 268; matches deferred #105)
10. **No CUDA/ROCm** (Vulkan only for AMD iGPU)

---

## Section 3 Core Implementation — Key Code Snippets

### 3.1 `get_llm()` — LangChain LlamaCpp wrapper (lines 223-310)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/dependencies.py:223-310`

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RuntimeError, OSError, ConnectionError, TimeoutError)),
    reraise=True
)
def get_llm(model_path: Optional[str] = None, **kwargs) -> LlamaCpp:
    """Initialize LlamaCpp LLM with Ryzen optimization."""
    # ... model_path from env or config.toml ...
    os.environ['OMP_NUM_THREADS'] = '1'  # Ryzen tuning
    
    llm_params = {
        'model_path': model_path,
        'n_ctx': int(os.getenv('LLAMA_CPP_N_CTX', CONFIG['models']['llm_context_window'])),
        'n_batch': int(os.getenv('LLAMA_CPP_N_BATCH', 512)),
        'n_threads': int(os.getenv('LLAMA_CPP_N_THREADS', CONFIG['performance']['cpu_threads'])),
        'n_gpu_layers': 0,  # CPU-only
        'f16_kv': os.getenv('LLAMA_CPP_F16_KV', 'true').lower() == 'true',
        'use_mlock': os.getenv('LLAMA_CPP_USE_MLOCK', 'true').lower() == 'true',
        'use_mmap': os.getenv('LLAMA_CPP_USE_MMAP', 'true').lower() == 'true',
        'verbose': os.getenv('LLM_VERBOSE', 'false').lower() == 'true',
        'max_tokens': int(os.getenv('LLM_MAX_TOKENS', 512)),
        'temperature': float(os.getenv('LLM_TEMPERATURE', 0.7)),
        'top_p': float(os.getenv('LLM_TOP_P', 0.95)),
        'top_k': int(os.getenv('LLM_TOP_K', 40)),
        'repeat_penalty': float(os.getenv('LLM_REPEAT_PENALTY', 1.1)),
    }
    llm_params.update(kwargs)
    filtered_params = filter_llama_kwargs(**llm_params)
    llm = LlamaCpp(**filtered_params)
```

**Key insight**: Uses `filter_llama_kwargs()` (lines 69-98) to whitelist valid params, preventing Pydantic validation errors from extra kwargs.

### 3.2 `get_vectorstore()` with Backup Fallback (lines 413-540)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/dependencies.py:413-540`

```python
def get_vectorstore(embeddings, index_path=None, backup_path=None):
    """Load FAISS vectorstore with backup fallback."""
    # 1. Try primary index
    if index_dir.exists() and (index_dir / "index.faiss").exists():
        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        # 2. Validate (if enabled)
        if CONFIG["backup"]["faiss"].get("verify_on_load", True):
            test_result = vectorstore.similarity_search("test", k=1)
            vector_count = vectorstore.index.ntotal
        return vectorstore
    
    # 3. Fallback to backups (up to max_count, sorted by mtime desc)
    if backup_dir.exists():
        backup_dirs = sorted(
            [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith("faiss_")],
            key=lambda x: x.stat().st_mtime, reverse=True
        )
        for backup in backup_dirs[:max_backups_to_try]:
            backup_index = backup / "index.faiss"
            if not backup_index.exists():
                continue
            try:
                vectorstore = FAISS.load_local(str(backup), embeddings, allow_dangerous_deserialization=True)
                # Restore to primary
                if index_dir.exists():
                    shutil.rmtree(index_dir)
                shutil.copytree(backup, index_dir)
                return vectorstore
            except Exception:
                continue
    return None
```

**Pattern**: 3-tier fallback — primary -> 5 most recent backups -> None. Backup dirs are named `faiss_YYYYMMDD_HHMMSS` and sorted by mtime desc.

### 3.3 `check_telemetry()` — 8-Disables Runtime Audit (lines 447-503)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/healthcheck.py:447-503`

```python
def check_telemetry() -> Tuple[bool, str]:
    """Verify all 8 telemetry disables are enforced (NEW v0.1.4)."""
    disables = {
        'CHAINLIT_NO_TELEMETRY': 'true',
        'CRAWL4AI_TELEMETRY': '0',
        'LANGCHAIN_TRACING_V2': 'false',
        'SCARF_NO_ANALYTICS': 'true',
        'DO_NOT_TRACK': '1',
        'PYTHONDONTWRITEBYTECODE': '1',
    }
    failed = []
    for var, expected in disables.items():
        value = os.environ.get(var, '')
        if value.lower() != expected.lower():
            failed.append(f"{var}={value or 'unset'}")
    # Plus config: project.telemetry_enabled=false, chainlit.no_telemetry=true
    if failed:
        return False, f"Telemetry disables incomplete: {', '.join(failed)}"
    return True, "Telemetry: 8/8 disables verified"
```

**Key insight**: This is a **runtime auditor** for Mandate 8 (Zero Telemetry). Not just env config — it actually checks at health-probe time and fails the health check if any disable is missing. This is the kind of pattern the current engine should consider for the `observability` module.

### 3.4 `check_ryzen()` — Ryzen Optimization Audit (lines 336-394)

```python
def check_ryzen() -> Tuple[bool, str]:
    """Verify Ryzen-specific optimizations are active."""
    checks = []
    warnings = []
    n_threads = int(os.getenv('LLAMA_CPP_N_THREADS', '0'))
    expected_threads = CONFIG['performance']['cpu_threads']
    if n_threads != expected_threads:
        warnings.append(f"N_THREADS={n_threads} (expected: {expected_threads})")
    else:
        checks.append(f"N_THREADS={n_threads}")
    
    f16_kv = os.getenv('LLAMA_CPP_F16_KV', 'false').lower() == 'true'
    if f16_kv != CONFIG['performance']['f16_kv_enabled']:
        warnings.append(f"F16_KV={f16_kv} (expected: ...)")
    else:
        checks.append(f"F16_KV={f16_kv}")
    
    coretype = os.getenv('OPENBLAS_CORETYPE', '')
    if coretype != 'ZEN':
        warnings.append(f"CORETYPE={coretype or 'unset'} (expected: ZEN)")
    else:
        checks.append("CORETYPE=ZEN")
    
    use_mlock = os.getenv('LLAMA_CPP_USE_MLOCK', 'false').lower() == 'true'
    if not use_mlock:
        warnings.append("USE_MLOCK=false (recommended: true)")
    
    if warnings:
        return True, f"Ryzen optimizations: {', '.join(checks)} | Warnings: {', '.join(warnings)}"
    return True, f"Ryzen optimizations active: {', '.join(checks)}"
```

**Note**: Returns True even with warnings (just includes them in message). The current engine should consider this — it's more diagnostic than blocking.

### 3.5 `pybreaker` Circuit Breaker Pattern 5 (blueprint.md Section 1 Pattern 5)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/docs/reference/blueprint.md:189-237`

```python
from pybreaker import CircuitBreaker, CircuitBreakerError

# Standardized: fail_max=3, reset_timeout=60s
llm_cb = CircuitBreaker(fail_max=3, reset_timeout=60)

@llm_cb
def load_llm_with_circuit_breaker():
    try:
        llm = get_llm()
        logger.info("LLM loaded")
        return llm
    except Exception:
        logger.exception("LLM failed to load")
        raise

@app.post("/query")
async def query_endpoint(request: Request, query_req: QueryRequest):
    try:
        llm = load_llm_with_circuit_breaker()
        # ... normal RAG flow
    except CircuitBreakerError:
        return JSONResponse(
            status_code=503,
            content={"error": "LLM service unavailable (circuit open)", "retry_after": 60}
        )
```

**Test** (`tests/test_circuit_breaker_chaos.py:24-67`):
```python
# First 3 calls fail with Exception
with pytest.raises(Exception): load_llm_with_circuit_breaker()
with pytest.raises(Exception): load_llm_with_circuit_breaker()
with pytest.raises(Exception): load_llm_with_circuit_breaker()
# 4th call blocked by circuit breaker
with pytest.raises(CircuitBreakerError): load_llm_with_circuit_breaker()
```

**Verdict**: This is the **cleanest, most portable circuit breaker** of all 3 stacks. The 36-line custom version in `src/omega/circuit_breaker.py` is a re-implementation. The 579-line Redis-backed version in `core/circuit_breakers/circuit_breaker.py` is over-engineered. **The pybreaker library IS the right pattern.**

### 3.6 `VoiceCircuitBreaker` — Domain-Specific CB (lines 241-281)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/voice_interface.py:241-281`

```python
class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class VoiceCircuitBreaker:
    """Circuit breaker pattern for voice operations."""
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._last_failure_time and (time.time() - self._last_failure_time) > self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
            return self._state
    
    def allow_request(self) -> bool:
        return self.state != CircuitState.OPEN
    
    def record_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= 3:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            voice_metrics.update_circuit_breaker(self.name, open=False)
    
    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
            voice_metrics.update_circuit_breaker(self.name, open=True)
```

**Usage** (line 818-819): `self.stt_circuit = VoiceCircuitBreaker("stt")`, `self.tts_circuit = VoiceCircuitBreaker("tts")`

**Key insight**: Custom CB because pybreaker doesn't expose state queries cleanly for metrics integration. Has Prometheus integration via `voice_metrics.update_circuit_breaker(name, open=...)`. The current engine's `AsyncCircuitBreaker` in `health_monitor.py` is the modern equivalent.

### 3.7 `Dockerfile.api` — 5-Retry `apt-get update` Pattern (lines 37-53)

```dockerfile
# Install build dependencies (llama-cpp-python requires cmake, build-essential, ninja) with retry logic
RUN set -ex && \
    mkdir -p /app && \
    # Retry apt-get update with exponential backoff
    for i in 1 2 3 4 5; do \
        if apt-get update 2>&1 | tee /app/apt-update.log; then \
            echo "apt-get update succeeded on attempt $i"; \
            break; \
        else \
            echo "apt-get update failed on attempt $i, retrying in $((i*5)) seconds..."; \
            sleep $((i*5)); \
        fi; \
        if [ $i -eq 5 ]; then \
            echo "apt-get update failed after 5 attempts"; \
            exit 1; \
        fi; \
    done && \
    apt-get install -y --no-install-recommends \
    build-essential cmake git libopenblas-dev pkg-config curl ca-certificates ninja-build \
    2>&1 | tee /app/apt-build.log && \
    mkdir -p /app/apt-archives && \
    cp -r /var/cache/apt/archives /app/apt-archives || true && \
    rm -rf /var/lib/apt/lists/* && apt-get clean
```

**Key insight**: 5-retry exp-backoff (`sleep $((i*5))` — 5s, 10s, 15s, 20s) for `apt-get update`. The same pattern is repeated for the runtime stage (lines 146-160). **This pattern is unique to foundation-legacy** — not in xna-omega-legacy or omega-stack-legacy.

### 3.8 `Curation Worker` — 5th Service (lines 88-107)

```python
def main():
    logger.info(f"{WORKER_NAME} started, listening on {QUEUE_KEY}")
    while True:
        try:
            job = rdb.blpop(QUEUE_KEY, timeout=5)
            if not job:
                time.sleep(1)
                continue
            job_id = job[1]
            process_job(job_id)
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection lost: {e}")
            time.sleep(5)
            rdb = connect_redis()
        except Exception as e:
            logger.error(f"Unhandled exception: {e}")
            time.sleep(2)
```

**Pattern**: `blpop(QUEUE_KEY, timeout=5)` blocks 5s, returns `None` if timeout, returns `(key, value)` if job available. On any error, reconnects via `connect_redis()` (which has its own retry decorator).

**Why this matters**: This is a **clean Redis Streams alternative** — uses Redis Lists (`blpop`/`brpop`) instead of Streams (`xread`). Simpler, lower-overhead, but no consumer groups. Current engine's `request_queue.py` uses a similar pattern (Dead-Letter queue, Mandate 12).

### 3.9 Stack-Cat Doc Generator (lines 1-50 header)

**Path**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/scripts/stack-cat/stack-cat:1-50`

```bash
#!/bin/bash
set -euo pipefail
# stack-cat v0.1.5 - Enhanced Stack Documentation Generator
# Last Updated: 2026-01-08
# New Features:
#   - De-concatenation function to extract individual files from markdown
#   - Option to concatenate all files in current directory
#   - Improved code organization and error handling
#   - Separate markdown files with .md extension preservation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_BASE="${SCRIPT_DIR}/stack-cat-output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}/${TIMESTAMP}"
SEPARATE_MD_DIR="${OUTPUT_DIR}/separate-md"

WHITELIST_FILE="${SCRIPT_DIR}/whitelist.json"
GROUPS_FILE="${SCRIPT_DIR}/groups.json"
```

**Unique value**: 1023-line bash script that generates `stack-cat-output/[timestamp]/` with all project files concatenated, de-concatenated, grouped by category. Was used to package the entire stack for AI context.

---

## Section 4 Top 5 NEW Findings (What Foundation-Legacy Has That Others Don't)

### 4.1 `pybreaker==0.7.0` — The Cleanest Circuit Breaker

- **Source**: `requirements-api.txt:88`, `tests/test_circuit_breaker_chaos.py`, blueprint.md Section 1 Pattern 5
- **Why gold**: Standardized, battle-tested, 5-line decorator, chaos-tested. The current engine's `src/omega/circuit_breaker.py` (36 lines) is a hand-rolled re-implementation of the same idea. The omega-stack-legacy's `core/circuit_breakers/circuit_breaker.py` (579 lines, Redis-backed) is over-engineered.
- **Verdict**: **The `pybreaker` library is the right answer.** Consider adopting it for the current engine.
- **Effort to port**: 1-2 hours (replace `src/omega/circuit_breaker.py` with `pybreaker`)

### 4.2 `check_telemetry()` — 8-Disable Runtime Audit

- **Source**: `app/XNAi_rag_app/healthcheck.py:447-503`, `scripts/telemetry_audit.py`
- **Why gold**: Direct implementation of Mandate 8 (Zero Telemetry) as a **runtime health probe**, not just config. Fails the health check if any of 6 env vars + 2 config values are missing. Can be called by Docker HEALTHCHECK, CI, or monitoring.
- **Verdict**: Add `check_telemetry()` to current engine's `observability` module. Reuses the `healthcheck.py` pattern.
- **Effort to port**: 30 min

### 4.3 `get_vectorstore()` with 3-Tier Backup Fallback

- **Source**: `app/XNAi_rag_app/dependencies.py:413-540`
- **Why gold**: Vectorstore loading with primary -> 5 most-recent backups -> None fallback. The backup dirs are named `faiss_YYYYMMDD_HHMMSS` and auto-restored to primary. This is the **defensive pattern** the current engine's Qdrant should consider as a fallback.
- **Verdict**: Port the `cleanup_old_backups()` (lines 619-668) retention policy (max_count=5, retention_days=7).
- **Effort to port**: 2 hours

### 4.4 5-Service Docker Compose (with `curation_worker`)

- **Source**: `docker-compose.yml:1-358`
- **Why gold**: 4 persistent services (redis, rag, ui, crawler) **+ 1 queue worker (curation_worker)** that consumes Redis lists via `blpop`. The current engine's docker-compose equivalent is just 1 service. The `curation_worker` pattern is the **template for distributed task processing** that aligns with Mandate 12 (Queue Integrity).
- **Verdict**: Use this as the **template** for the engine's queue worker pattern. The `user: ${APP_UID}:${APP_GID}` + `cap_drop: ALL` + `cap_add: [SETGID, SETUID, CHOWN]` + `tmpfs: /tmp:mode=1777` is the **right permission model** for rootless Podman (matches Mandate 6 + deferred #105).
- **Effort to port**: 4 hours (compose + worker code)

### 4.5 `Grok Vulkan Enhancement Code Guide` — Production-Ready Vulkan Path

- **Source**: `docs/archive/code-review-sessions/Grok - Vulkan Enhancement code guide - January 10, 20.md:1-129`
- **Why gold**: A complete Vulkan integration plan with:
  - Build-time: `ARG CMAKE_ARGS` conditional on Vulkan
  - Runtime: `VULKAN_ENABLED`, `N_GPU_LAYERS=30`, `GGML_VK_VISIBLE_DEVICES=0`
  - Code: `get_llm()` update with conditional offload (line 64-93)
  - Docker: `devices: /dev/dri:/dev/dri` for iGPU passthrough
  - Benchmark: `./llama-bench -m /models/... -ngl 30` to compare vs `-ngl 0`
- **Verdict**: This is the **unified plan** that combines omega-stack-legacy's `infra/docker/Dockerfile` (Vulkan enabled) with the runtime toggles. The current engine should adopt this conditional `VULKAN_ENABLED` approach.
- **Effort to port**: 1 day (the Vulkan `DGGML_VULKAN=ON` build + iGPU passthrough + runtime toggle)

---

## Section 4.5 Bonus: The 5 Mandatory Design Patterns (Blueprint Section 1)

The foundation-legacy's **cleanest contribution** is the "5 mandatory design patterns" framework. This is the **design discipline** that the current engine should adopt wholesale:

| Pattern | Purpose | File | Current Engine Status |
|---------|---------|------|----------------------|
| **Pattern 1: Import Path Resolution** | `sys.path.insert(0, str(Path(__file__).parent))` to fix container ModuleNotFoundError | `main.py:30`, `dependencies.py:30`, `healthcheck.py:25` | **NOT YET — but needed for venv mode** |
| **Pattern 2: Retry with Exponential Backoff** | `@retry(stop_after_attempt(3), wait=wait_exponential(...))` | `dependencies.py:217-221` | Already used in `tenacity` imports |
| **Pattern 3: Non-Blocking Subprocess** | `subprocess.Popen(..., start_new_session=True)` for chainlit UI responsiveness | `chainlit_app.py` | **NOT YET** — current engine uses `anyio.run_process` |
| **Pattern 4: Atomic Checkpointing with fsync** | tmp write -> fsync all files -> atomic rename -> fsync parent dir | `ingest_library.py` | Current engine has atomic writes in `request_queue.py` |
| **Pattern 5: Circuit Breaker (pybreaker)** | `@llm_cb` decorator, 503 on OPEN | `main.py:463` | **REJECTED in current engine** (uses 36L custom instead) — should reconsider |

**Verdict**: Adopt the **5 mandatory patterns** framework in the current engine's docs. Even where the engine uses different implementations, document the **5 patterns** as the canonical design discipline.

---

## Section 5 Top 5 NEVER Rules (Distilled From Foundation-Legacy)

1. **NEVER use `n_threads=16` or all-SMT threads** — causes context-switching thrashing. Use `n_threads=6` (75% of 8C/16T). [Source: blueprint.md:285, dependencies.py:274, Dockerfile.api:219]
2. **NEVER use bare `subprocess.run` in async context** — UI hangs. Use `subprocess.Popen(..., start_new_session=True)` for non-blocking. [Source: blueprint.md:121-136, Pattern 3]
3. **NEVER commit `.env` with secrets** — but DO commit `.env.example` for reference. [Source: docker-compose.yml:22, 96-108, `.env` is gitignored per `.gitignore`]
4. **NEVER use `:U` flag on volume mounts** — destructively chowns host dirs. Use `user: ${APP_UID}:${APP_GID}` + `cap_drop: ALL` + `cap_add: [SETGID, SETUID, CHOWN]`. [Source: docker-compose.yml:124-132, note: contradicts some legacy docs but matches Mandate 6]
5. **NEVER use HuggingFace `transformers`** — zero-telemetry violation. Use `LlamaCppEmbeddings` (50% memory savings, no torch). [Source: verify_imports.py:104-112, dependencies.py:42]

**Additional NEVER rules** (operational):
- **NEVER skip the `importlib.util` import** — must be `import importlib.util` not `import importlib` [Source: runbook docker-build-troubleshooting.md:98-104]
- **NEVER use `Ollama` as a dependency** — direct llama-cpp-python instead. [Source: blueprint.md:30-35, "v0.1.3-beta Ollama" to "v0.1.5 llama-cpp-python"]
- **NEVER use `asyncio.run_in_executor` without `None` for default executor** — works in foundation but should be `anyio.to_thread.run_sync` per Mandate 1. [Source: dependencies.py:323, 406, 558 — uses asyncio, not AnyIO!]

---

## Section 6 New DEFERRED_GOLD_TRACKER Entries (IDs 121-130)

| # | Tech/Strategy | Source Path | Status | Future Use Case | Effort to Import | Notes |
|---|---------------|-------------|--------|-----------------|------------------|-------|
| 121 | **`pybreaker==0.7.0` circuit breaker** (replaces custom 36L + 579L) | `requirements-api.txt:88`, `tests/test_circuit_breaker_chaos.py:1-230`, `docs/reference/blueprint.md:189-237` | READY-FOR-IMPORT | Replace `src/omega/circuit_breaker.py` (36L custom) with `pybreaker` decorator. Aligns with `health_monitor.py::AsyncCircuitBreaker` | LOW (2 hr) | 5-line decorator, battle-tested, chaos-tested. Standardized across XNAi + foundation eras. |
| 122 | **`check_telemetry()` 8-disable runtime audit** | `app/XNAi_rag_app/healthcheck.py:447-503` + `scripts/telemetry_audit.py:1-180` | READY-FOR-IMPORT | Add to `src/omega/observability.py` — fails health if any of 6 env + 2 config telemetry disables missing | LOW (30 min) | Direct implementation of Mandate 8 (Zero Telemetry). 6 env vars: `CHAINLIT_NO_TELEMETRY=true`, `CRAWL4AI_TELEMETRY=0`, `LANGCHAIN_TRACING_V2=false`, `SCARF_NO_ANALYTICS=true`, `DO_NOT_TRACK=1`, `PYTHONDONTWRITEBYTECODE=1`. 2 config: `project.telemetry_enabled=false`, `chainlit.no_telemetry=true`. |
| 123 | **`get_vectorstore()` 3-tier backup fallback** | `app/XNAi_rag_app/dependencies.py:413-540` | READY-FOR-IMPORT | FAISS primary -> 5 most-recent backups -> None. Backup dirs named `faiss_YYYYMMDD_HHMMSS`, sorted by mtime desc, auto-restored to primary | MEDIUM (2 hr) | Add `cleanup_old_backups()` (lines 619-668) with retention policy `max_count=5, retention_days=7`. Aligns with current engine's Qdrant pattern. |
| 124 | **`curation_worker` 5th-service blpop queue worker** | `scripts/curation_worker.py:1-107` + `docker-compose.yml:270-296` | READY-FOR-IMPORT | Use as template for current engine's distributed task processing | MEDIUM (4 hr) | `blpop(QUEUE_KEY, timeout=5)` blocks 5s, returns `None` on timeout. Reconnects via `connect_redis()` (tenacity retry). Note: current engine uses AnyIO semaphores + `request_queue.py`. Port the Redis blpop pattern as alternative to Redis Streams. |
| 125 | **5-retry `apt-get update` with exp backoff** | `Dockerfile.api:37-53` (builder), `Dockerfile.api:146-160` (runtime) | READY-FOR-IMPORT | Add to current engine's Dockerfile for llama-cpp builds | LOW (15 min) | `for i in 1 2 3 4 5; do apt-get update 2>&1 || (sleep $((i*5)) && retry); done`. First occurrence in our corpus — not in xna-omega or omega-stack. |
| 126 | **`VoiceCircuitBreaker` (STT/TTS-specific CB with metrics)** | `app/XNAi_rag_app/voice_interface.py:241-281` | DEFERRED | Domain-specific CB for voice ops with Prometheus integration | MEDIUM | Custom CB with `voice_metrics.update_circuit_breaker(name, open=...)` integration. Current engine has `AsyncCircuitBreaker` in `health_monitor.py` — this is the simpler, metrics-coupled version. Useful when voice is added. |
| 127 | **Grok Vulkan Code Guide** (production-ready Vulkan path) | `docs/archive/code-review-sessions/Grok - Vulkan Enhancement code guide - January 10, 20.md:1-129` | READY-FOR-IMPORT | Unifies omega-stack's `infra/docker/Dockerfile` Vulkan build with runtime toggle | MEDIUM (1 day) | Build-time: `ARG CMAKE_ARGS` conditional. Runtime: `VULKAN_ENABLED`, `N_GPU_LAYERS=30`, `GGML_VK_VISIBLE_DEVICES=0`. Docker: `devices: /dev/dri:/dev/dri`. Benchmark: `./llama-bench -ngl 30` vs `-ngl 0`. The unified Vulkan plan. |
| 128 | **5 Mandatory Design Patterns** framework | `docs/reference/blueprint.md:82-237` (Section 1) | READY-FOR-IMPORT | Adopt as the canonical design discipline in current engine docs | LOW (1 hr) | Pattern 1 (imports), 2 (retry), 3 (non-blocking subprocess), 4 (atomic fsync), 5 (pybreaker). The cleanest articulation of v0.1 era discipline. |
| 129 | **Stack-Cat v0.1.5 doc generator** | `scripts/stack-cat/stack-cat:1-1023` | DEFERRED | Bash script that concatenates + de-concatenates project files for AI context | LOW (1 hr to port, 2 hr to adopt) | Output: `stack-cat-output/[timestamp]/`. Unique to foundation-legacy — not in other stacks. Useful for documentation generation in community tools. |
| 130 | **Voice + Persona foundation** (Lilith/Odin JSON + Faster-Whisper + Piper-ONNX) | `docs/personas/lilith.json:1-105`, `docs/personas/odin.json:1-110`, `requirements-chainlit.txt:60-100` | DEFERRED | Lilith + Odin persona templates (earliest in this lineage) + voice stack (Piper ONNX, no torch) | MEDIUM (1 day) | Earliest known Lilith persona (March 2025 origin). Piper ONNX TTS is the torch-free alternative to XTTS — perfect for 5700U. Faster-Whisper is the CT2-accelerated Whisper (4x faster). |

---

## Section 7 Implementation Cheat Sheet — Top 3 Patterns

### Pattern A: Adopt `pybreaker` for circuit breaker (2 hours)

```bash
# 1. Add to requirements (any current file)
pip install pybreaker==0.7.0

# 2. In src/omega/oracle/model_gateway.py
from pybreaker import CircuitBreaker, CircuitBreakerError

# Standardized: fail_max=3, reset_timeout=60s (per blueprint Pattern 5)
provider_cb = CircuitBreaker(fail_max=3, reset_timeout=60)

@provider_cb
async def generate_with_cb(provider_name: str, prompt: str) -> str:
    """Generate with circuit breaker protection."""
    return await generate_via_provider(provider_name, prompt)

# 3. In the route handler
try:
    return await generate_with_cb(provider, prompt)
except CircuitBreakerError:
    raise OmegaError(
        code="PROVIDER_CIRCUIT_OPEN",
        message=f"Provider {provider} circuit is open (retry after 60s)",
        retry_after=60
    )
```

### Pattern B: Add `check_telemetry()` to observability (30 min)

```python
# In src/omega/observability.py (or new src/omega/audit/telemetry.py)

TELEMETRY_DISABLES = {
    'CHAINLIT_NO_TELEMETRY': 'true',
    'CRAWL4AI_TELEMETRY': '0',
    'LANGCHAIN_TRACING_V2': 'false',
    'SCARF_NO_ANALYTICS': 'true',
    'DO_NOT_TRACK': '1',
    'PYTHONDONTWRITEBYTECODE': '1',
    'HF_HUB_DISABLE_TELEMETRY': '1',  # bonus for HF
    'TRANSFORMERS_VERBOSITY': 'error',  # bonus for transformers
}

def check_telemetry() -> Tuple[bool, str]:
    """Verify all 8+ telemetry disables are enforced (Mandate 8)."""
    failed = []
    for var, expected in TELEMETRY_DISABLES.items():
        value = os.environ.get(var, '')
        if value.lower() != expected.lower():
            failed.append(f"{var}={value or 'unset'}")
    
    if failed:
        return False, f"Telemetry disables incomplete: {', '.join(failed)}"
    return True, f"Telemetry: {len(TELEMETRY_DISABLES)}/{len(TELEMETRY_DISABLES)} disables verified"
```

### Pattern C: Add 5-retry `apt-get update` to Dockerfile (15 min)

```dockerfile
# In any current Dockerfile that does apt-get
RUN set -ex && \
    mkdir -p /app && \
    for i in 1 2 3 4 5; do \
        if apt-get update 2>&1; then \
            echo "apt-get update succeeded on attempt $i"; \
            break; \
        else \
            echo "apt-get update failed on attempt $i, retrying in $((i*5))s..."; \
            sleep $((i*5)); \
        fi; \
        if [ $i -eq 5 ]; then \
            echo "apt-get update failed after 5 attempts"; \
            exit 1; \
        fi; \
    done && \
    apt-get install -y --no-install-recommends \
        build-essential cmake ninja-build libopenblas-dev libgomp1 \
        && rm -rf /var/lib/apt/lists/* && apt-get clean
```

---

## Section 8 Contradictions With Prior Phases

### 8.1 Build Flags (Vulkan)

- **xna-omega-legacy (Phase 1)**: Zen 2 only, no Vulkan (`HP-5700U-OPTIMIZATION.md`).
- **foundation-legacy (Phase 3)**: OpenBLAS + AVX2 + FMA + F16C, **NO Vulkan** in `Dockerfile.api:133`. Same as Phase 1.
- **omega-stack-legacy (Phase 2)**: OpenBLAS + AVX2 + FMA + F16C + **VULKAN** in `infra/docker/Dockerfile:36-43`. **CONTRADICTS Phase 3.**

**Resolution**: Phase 2's Vulkan-enabled production Dockerfile is the **actually-shipped** version. The Grok Vulkan Enhancement guide in Phase 3 (deferred #127) is the **plan** for adopting it. The current engine should follow the Grok guide (conditional `CMAKE_ARGS`).

### 8.2 Circuit Breaker Pattern

- **xna-omega-legacy (Phase 1)**: Custom 579-line `app/XNAi_rag_app/core/circuit_breakers/circuit_breaker.py` (Redis-backed) — **rejected** in current engine.
- **foundation-legacy (Phase 3)**: `pybreaker==0.7.0` library, 5-line decorator — **the cleanest pattern**.
- **omega-stack-legacy (Phase 2)**: Custom 36-line `src/omega/circuit_breaker.py` (current engine's source) + 579L Redis variant (rejected).
- **Current engine**: 36L custom, no `pybreaker` dependency.

**Resolution**: **Adopt `pybreaker`** (Phase 3 pattern). The 36L custom is a re-implementation.

### 8.3 KV Cache Type

- **xna-omega-legacy (Phase 1)**: `q8_0` (type_k=8, type_v=8) per HP-5700U-OPTIMIZATION.md.
- **foundation-legacy (Phase 3)**: `f16_kv=true` (default) per `dependencies.py:276` + `config.toml:67`.
- **omega-stack-legacy (Phase 2)**: `f16_kv=true` in LangChain wrapper, but `q8_0` mentioned in `expert-knowledge/architect/int8_kv_cache.md`.
- **Current engine**: `q8_0` (per `models.yaml`).

**Resolution**: Both work. The `q8_0` saves 50% memory at <1% quality cost. The current engine's choice is correct for memory-constrained 14GB systems.

### 8.4 User ID (1000 vs 1001)

- **xna-omega-legacy (Phase 1)**: (not specified).
- **foundation-legacy (Phase 3)**: UID 1001 (`Dockerfile.api:171`, `docker-compose.yml:124`).
- **omega-stack-legacy (Phase 2)**: UID 1001 in early docs, conflicting with current Mandate 6 (UID 1000).
- **Current engine** (Mandate 6): UID 1000 (host user).

**Resolution**: The foundation-legacy uses UID 1001 (legacy appuser pattern). Current engine's UID 1000 is correct for the new Sovereign Mandate 6. The 1001/1000 mismatch is a **legacy artifact** that should be flagged but not ported.

### 8.5 Async Library (asyncio vs AnyIO)

- **xna-omega-legacy (Phase 1)**: Mixed (uses `asyncio.run_in_executor` in some places).
- **foundation-legacy (Phase 3)**: **`asyncio` in many places** — `dependencies.py:323, 406, 558` (uses `loop.run_in_executor`). **DIRECT VIOLATION of Mandate 1 (AnyIO Absolute).**
- **omega-stack-legacy (Phase 2)**: Mostly AnyIO (per Phase 2 audit).
- **Current engine**: AnyIO (Mandate 1).

**Resolution**: **Do NOT port the asyncio patterns from foundation-legacy.** Use AnyIO equivalents (`anyio.to_thread.run_sync`) per current engine's discipline.

### 8.6 LangChain Wrapper vs Native

- **xna-omega-legacy (Phase 1)**: Native `llama_cpp.Llama` (`LocalLlmClient`).
- **foundation-legacy (Phase 3)**: LangChain `LlamaCpp` wrapper.
- **omega-stack-legacy (Phase 2)**: LangChain `LlamaCpp` wrapper.
- **Current engine**: Native (`NativeGGUFProvider`).

**Resolution**: 2-of-3 stacks use LangChain. But the **current engine's native approach is faster** (per Phase 2 finding "native is faster, LangChain has more params"). The current engine is correct.

---

## Section 9 Cross-References

### Same Patterns In Multiple Stacks

| Pattern | xna-omega | omega-stack | foundation | Current engine |
|---------|-----------|-------------|------------|----------------|
| LangChain `LlamaCpp` wrapper | no | yes | yes | no (uses native) |
| Native `llama_cpp.Llama` | yes | no | no | yes |
| Custom circuit breaker (hand-rolled) | no | yes (36L) | no | yes (36L) |
| `pybreaker` library | no | no | yes | no |
| Redis-backed CB (579L) | no | yes | no | no (rejected) |
| LangChain `LlamaCppEmbeddings` | no | yes | yes | no |
| `f16_kv=true` (default) | no | yes | yes | no (q8_0 default) |
| `q8_0` KV cache (type_k=8) | yes | yes | no | yes |
| Vulkan iGPU support | no | yes (enabled) | no (deferred plan) | no |
| Persona JSON files (Lilith, Odin) | no | no | yes (earliest) | no |
| Code-Weaver multi-agent prompts | no | no | yes | no |
| Stack-Cat doc generator | no | no | yes (1023L bash) | no |
| FAISS backup fallback chain | no | no | yes (3-tier) | no |
| 5 mandatory design patterns | no | no | yes (Pattern 1-5) | no (uses AnyIO equivalent) |
| 8 telemetry disables runtime audit | no | no | yes (`check_telemetry()`) | no |
| 5-retry apt-get update with backoff | no | no | yes | no |
| Curation worker (5th service, blpop) | no | no | yes | no |

### Files NOT in xna-omega or omega-stack (UNIQUE to foundation-legacy)

1. `scripts/curation_worker.py` — 5th-service blpop worker
2. `app/XNAi_rag_app/voice_interface.py` — full voice stack + `VoiceCircuitBreaker`
3. `scripts/stack-cat/stack-cat` — 1023-line doc generator
4. `scripts/telemetry_audit.py` — runtime telemetry audit
5. `versions/versions.toml` + `versions/scripts/update_versions.py` — version matrix sync
6. `docs/projects/Code-Weaver/` — multi-agent Claude system prompt
7. `docs/projects/stack-butler/` — Stack-butler era Grok sessions
8. `docs/projects/PIE/` — Personal Intelligence Engine concept
9. `docs/personas/{lilith,odin}.json` — earliest persona JSON in this lineage
10. `docs/implementation/phase-1-5/{checklist,code-skeletons,index,visual-reference}.md` — phase-1.5 implementation guide

---

## Section 10 Top 3 Differences From Prior Phases — Summary

1. **Foundation-legacy is the "Polymath Foundation" v0.1.5-stable release** — the **first production-ready** version of XNAi (94.2% test coverage, 215 tests, 8 health checks). xna-omega was an evolution, omega-stack was the next iteration. Foundation is the **shipped baseline**.

2. **Foundation-legacy has the "5 Mandatory Design Patterns" framework** — the cleanest articulation of v0.1 era discipline. Pattern 1 (imports), 2 (retry), 3 (non-blocking), 4 (atomic fsync), 5 (pybreaker). The current engine should adopt this framework even where implementations differ.

3. **Foundation-legacy has the `check_telemetry()` runtime audit** — the only stack that **enforces** Mandate 8 (Zero Telemetry) as a health probe, not just config. This is the **defensive implementation** of telemetry sovereignty.

---

## Section 11 Statistics

- **Source files analyzed**: 50+
- **llama-cpp references found**: 50+ (Python) + 200+ (Markdown)
- **llama-cpp artifacts cataloged**: 30+ unique files
- **NEW patterns identified**: 5 (pybreaker, check_telemetry, vectorstore backup fallback, curation_worker, Vulkan plan)
- **5 mandatory patterns framework**: New (only in this stack)
- **Personas (Lilith, Odin)**: Earliest known in this lineage
- **Total code lines in `app/XNAi_rag_app/`**: 14,612
- **Total code lines in `scripts/`**: ~3,500
- **Blueprint reference doc**: 716 lines (the cleanest design doc)
- **DEFERRED_GOLD_TRACKER entries added**: 10 (IDs 121-130)
- **Contradictions identified**: 6 (Vulkan, CB pattern, KV cache, UID, asyncio, LangChain)
- **Aligned with current Mandates**: Yes (mostly — except the asyncio usage in `dependencies.py`)

**Verdict**: Foundation-legacy is the **cleanest, most production-tested** of the 3 stacks. The current engine has already ported the core llama-cpp wisdom. The new value is the `pybreaker` library, `check_telemetry()`, the 5 mandatory patterns framework, and the Vulkan integration plan.

---

*OMEGA ROC_RACOON opencode trc_mining_foundation_legacy MINING-REPORT-03*
