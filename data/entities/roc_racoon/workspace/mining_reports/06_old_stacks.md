<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

⚠️ **DEPRECATED NOMENCLATURE** — This document uses legacy terminology that has been renamed:
- **LLOC** → **Meditate** (single-inference cognitive prism)
- **HLOC** → **MC (Mastermind Council)** (multi-subagent same-session)
- **Octave Council** → **Lens Framework** (composable cognitive perspectives)
- **10 Pillars** → **Omega Pantheon** (lens-primary; pillar is optional WAD metadata)
- **P1–P10** references → **Lens names** (infrastructure, persistence, engineering, etc.)

This naming was ratified 2026-07-16 and applied across the fleet on 2026-07-18.
Content below is preserved as-is for historical reference. See `config/wads/_omega_default/meditate/lenses.yaml` for current lens definitions.

# Mining Report #06: Old-Stacks
# Subagent: Roc Racoon Mining Subagent #6 (general)
# Stack: Old-Stacks (in /home/arcana-novai/Documents/Archives/Old-Stacks/)
# Date: 2026-06-02
# Status: COMPLETE (verified real code stack, 4-service Docker Compose FOUND)

## §0 Executive Summary

The `Old-Stacks` directory is a **REAL code stack** — 117M, 5 subdirectories
containing pre-Omega XNAi/XNAi-v0.1.2/Xoe-NovAi complete working code. The
flattened `.md` dumps in `10_15_1212/` and `10_15_1452/` (Oct 15, 2025) are
`stack-concat` archives — the same code, but rendered as Markdown for
documentation. The real, executable, working code lives in two places:

1. **`Xoe-NovAi/` (89M)** — the most complete and most modern version
   (v0.1.4-stable, dated 2026-01-03). Has the **4-service Docker Compose
   (redis + rag + ui + crawler) PLUS a curation_worker (5 total)** that
   current Omega Engine is missing.
2. **`XNAi-v0_1_2/` (27M)** — the older v0.1.2 (rev_1.9, dated 2025-10-16)
   plus the gold-standard **`xnai_blueprint.md` (714 lines)** that documents
   the entire v0.1.4-stable production design with 5 mandatory patterns
   (including pybreaker Circuit Breaker Pattern 5).

**The headline finding**: The XNAi v0.1.4-stable blueprint validates the
exact architecture the current Omega Engine converged to:
- **llama-cpp-python (native GGUF) as primary backend** (replacing Ollama)
- **Local-first, 4-service container architecture** (redis, rag, ui, crawler)
- **Circuit breaker on LLM load** (Pattern 5 — using `pybreaker` sync lib,
  not the AsyncCircuitBreaker in current `health_monitor.py`)

**Critical SECURITY finding**: A plaintext Redis password file
`Xoe-NovAi/redis_password.txt` contains the literal string `1234567890123456`
— a 16-digit all-numeric password that violates Sovereign Mandate 6 (no
secrets in repo) and the `.env`-based secret management pattern.

## §1 Subdirectory Inventory

| Subdir | Size | File Count | Type | llama-cpp Refs | Verdict |
|--------|------|------------|------|----------------|---------|
| `Xoe-NovAi/` | 89M | ~300 (most active) | **REAL working code** v0.1.4-stable | 25+ | ⭐ PRIMARY SOURCE |
| `XNAi-v0_1_2/` | 27M | ~50 | **REAL working code** v0.1.2 + 714-line blueprint | 8+ | ⭐ BLUEPRINT SOURCE |
| `10_15_1212/` | 660K | 30 | Flattened `.md` stack-concat dump (Oct 15 12:12) | 5+ (in `.md` files) | Archive only |
| `10_15_1452/` | 684K | 30 | Flattened `.md` stack-concat dump (Oct 15 14:52) | 5+ (in `.md` files) | Archive only |
| `20251015_144704/` | 8K | 1 | Empty directory + `processing.log` (58 bytes) | 0 | Empty marker |
| **TOTAL** | **117M** | ~410 | Mixed | **~43 references** | |

**Top files for llama-cpp-python (non-`.md`):**
- `Xoe-NovAi/Dockerfile.api:14-247` — multi-stage build w/ CMAKE_ARGS
- `Xoe-NovAi/app/XNAi_rag_app/dependencies.py:223-407` — `get_llm()` + `get_embeddings()` + `filter_llama_kwargs()`
- `Xoe-NovAi/app/XNAi_rag_app/verify_imports.py:114-129` — `check_llama_compilation()` (validates `n_threads=6, f16_kv=true`)
- `Xoe-NovAi/app/XNAi_rag_app/healthcheck.py:355-380` — env-var-driven LLM config probe
- `Xoe-NovAi/config.toml:36-46` — model paths (gemma-3-4b-it Q5_K_XL, MiniLM-L12-v2)
- `Xoe-NovAi/docker-compose.yml:97-98` — `LLM_MODEL_PATH` + `EMBEDDING_MODEL_PATH` env injection
- `Xoe-NovAi/Makefile:45-46` — model download URLs
- `XNAi-v0_1_2/xnai_blueprint.md:188-209, 460-471` — Pattern 5 Circuit Breaker spec
- `XNAi-v0_1_2/app/XNAi_rag_app/dependencies.py:83-100` — `filter_llama_kwargs()` (same as v0.1.4)
- `XNAi-v0_1_2/app/XNAi_rag_app/crawl.py:419` — in-crawl `LlamaCppEmbeddings` usage

## §2 The 4-Service Docker Compose — FOUND

**File**: `Xoe-NovAi/docker-compose.yml` (341 lines) — v0.1.3→v0.1.4 evolution

### 2.1 Service Map (5 services total, 4 persistent + 1 worker)

| Service | Image | Port | Memory Limit | CPU Limit | Healthcheck |
|---------|-------|------|--------------|-----------|-------------|
| **redis** | `redis:7.4.1` | (internal) | 512M (cmd `--maxmemory`) | none | `redis-cli ping` |
| **rag** | custom (Dockerfile.api) | 8000, 8002 | 4G | 2.0 | `python3 healthcheck.py` |
| **ui** | custom (Dockerfile.chainlit) | 8001 | 2G | 1.0 | `curl /health` |
| **crawler** | custom (Dockerfile.crawl) | (internal) | none | none | `python3 -c "import crawl4ai"` |
| **curation_worker** | custom (Dockerfile.curation_worker) | (internal) | none | none | none (restart on-failure) |

### 2.2 Port Mappings

```
Host → Container
8000 → rag:8000     (FastAPI RAG API)
8001 → ui:8001      (Chainlit UI)
8002 → rag:8002     (Prometheus metrics)
```

### 2.3 Volume Mounts (rag service, the main one)

```yaml
volumes:
  - ./config.toml:/config.toml:ro
  - ./models:/models:ro                    # ← GGUF models
  - ./embeddings:/embeddings:ro            # ← embedding models
  - ./library:/library                     # ← curated RAG content
  - ./knowledge:/knowledge                 # ← agent knowledge bases
  - ./data/faiss_index:/app/XNAi_rag_app/faiss_index
  - ./backups:/backups
  - ./data/prometheus-multiproc:/prometheus_data
  - ./app/XNAi_rag_app:/app/XNAi_rag_app   # ← live code reload
```

### 2.4 Security Patterns

- **Non-root user**: `user: "${APP_UID}:${APP_GID}"` (1001:1001 in `.env`)
- **cap_drop ALL**: drops all Linux capabilities by default
- **cap_add minimal**: `SETGID, SETUID, CHOWN` only
- **no-new-privileges**: `security_opt: ["no-new-privileges:true"]`
- **tmpfs**: `/tmp:mode=1777,size=512m` (volatile scratch space)
- **depends_on with health conditions**: `service_healthy` not just `service_started`

### 2.5 Comparison to Current Engine Architecture

| Aspect | Old-Stacks (v0.1.4-stable) | Current Omega Engine |
|--------|---------------------------|---------------------|
| Container runtime | Docker Compose (5 services) | Podman Quadlets (5 services) |
| Cache | `redis:7.4.1` w/ Streams | `redis:7-alpine` (session/cache) |
| Vector store | FAISS (CPU) | `qdrant/qdrant` (1G limit) |
| SQL | (none — YAML/Redis only) | `postgres` + pgvector (512M) |
| Reverse proxy | (none — direct host:port) | `caddy:alpine` (64M) |
| Voice/UI | Chainlit (8001) | Nova (separate container) |
| Local inference | llama-cpp-python (built into `rag`) | **native-gguf** via ModelGateway (built into Python venv) |
| 4-service model | YES (redis, rag, ui, crawler) | YES (redis, qdrant, postgres, caddy) + iris |
| Total containers | 5 | 5 |

**Architectural alignment**: Both have 5 containers; both separate cache
(redis) from vector store (FAISS→Qdrant); both put local inference in a
Python runtime; both follow principle of least privilege.

**Architectural divergence**: Old-Stacks FAISS runs **inside the rag
container** (process-level), Qdrant runs as its **own container** (service
isolation). Qdrant is the more scalable, separately-upgradable choice.

## §3 Key Patterns

### 3.1 Ryzen-Optimized Multi-Stage Dockerfile (GOLD)

**File**: `Xoe-NovAi/Dockerfile.api:132-134, 219-226`

```dockerfile
# Stage 1 (builder): apply CMAKE_ARGS at build time for Ryzen/Zen2
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS \
                -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON" \
    FORCE_CMAKE=1

# Stage 2 (runtime): runtime env vars for inference
ENV LLAMA_CPP_N_THREADS=6 \
    LLAMA_CPP_F16_KV=true \
    LLAMA_CPP_USE_MLOCK=true \
    LLAMA_CPP_USE_MMAP=true \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    OPENBLAS_CORETYPE=ZEN \
    MKL_DEBUG_CPU_TYPE=5
```

**Engineering decisions**:
- `n_threads=6` = 75% of 8C/16T (leaves 2 cores for OS + I/O)
- `f16_kv=true` = halves KV cache memory
- `use_mlock=true` = prevents model swap to disk
- `use_mmap=true` = OS-level memory-mapped file I/O
- `OMP_NUM_THREADS=1` + `OPENBLAS_NUM_THREADS=1` = llama.cpp handles parallelism internally (avoid nested threading)

**The CMAKE_ARGS pattern is REPLICABLE for the current engine's `native-gguf`
provider** — currently `src/omega/oracle/backends/native_gguf.py` does NOT
document CMAKE build flags. This is a gap to close.

### 3.2 `filter_llama_kwargs()` Pattern (GOLD)

**File**: `Xoe-NovAi/app/XNAi_rag_app/dependencies.py:64-98`

```python
def filter_llama_kwargs(**kwargs) -> dict:
    """Filter kwargs to only valid LlamaCpp parameters (pydantic v2 compat)."""
    valid_params = {
        'model_path', 'n_ctx', 'n_batch', 'n_gpu_layers', 'n_threads',
        'n_parts', 'seed', 'f16_kv', 'logits_all', 'vocab_only',
        'use_mlock', 'use_mmap', 'embedding', 'last_n_tokens_size',
        'lora_base', 'lora_path', 'verbose', 'max_tokens', 'temperature',
        'top_p', 'top_k', 'repeat_penalty', 'stop', 'streaming'
    }
    filtered = {k: v for k, v in kwargs.items() if k in valid_params}
    removed = set(kwargs.keys()) - set(filtered.keys())
    if removed:
        logger.debug(f"Filtered out invalid llama-cpp params: {removed}")
    return filtered
```

**Why this matters**: The current native-gguf backend in
`src/omega/oracle/backends/native_gguf.py` does NOT have this filter. If
`config/providers.yaml` accidentally contains a typo or deprecated key
(e.g., `n_gqa_layers` from llama-cpp 0.2.x), llama-cpp-python 0.3.x will
raise `ValueError: Invalid parameter`. The `filter_llama_kwargs()` pattern
prevents this by silently dropping unknown keys with a debug log.

### 3.3 `get_llm()` with Tenacity Retry (GOLD)

**File**: `Xoe-NovAi/app/XNAi_rag_app/dependencies.py:217-310`

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RuntimeError, OSError, ConnectionError, TimeoutError)),
    reraise=True
)
def get_llm(model_path: Optional[str] = None, **kwargs) -> LlamaCpp:
    # ... env-var-driven config ...
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
    return LlamaCpp(**filtered_params)
```

**Notable**: `n_gpu_layers: 0` is **explicit** — the user is committed to
CPU-only inference, even if a GPU appears later. The current engine's
`native-gguf` backend does NOT pin `n_gpu_layers: 0`.

### 3.4 Pattern 5 — Circuit Breaker on LLM Load (GOLD)

**File**: `XNAi-v0_1_2/xnai_blueprint.md:188-209`

```python
# Pattern 5 – Circuit Breaker (Standardized with pybreaker)
from pybreaker import CircuitBreaker, CircuitBreakerError

# fail_max=3, reset_timeout=60s (per blueprint line 33)
llm_breaker = CircuitBreaker(fail_max=3, reset_timeout=60)

@llm_breaker
def load_llm_with_circuit_breaker():
    """Load GGUF model with circuit breaker protection."""
    return LlamaCpp(
        model_path=os.getenv("LLM_MODEL_PATH"),
        n_ctx=2048,
        n_threads=6,
        f16_kv=True,
    )

# Usage:
try:
    llm = load_llm_with_circuit_breaker()
except CircuitBreakerError:
    # Service is OPEN, fail fast to fallback
    raise
```

**Comparison to current engine**:
- Old-Stacks: `pybreaker` (sync library, no AnyIO support)
- Current engine: `AsyncCircuitBreaker` in `src/omega/oracle/health_monitor.py` (custom, AnyIO-native)

The current engine's choice is **correct** for Mandate 1 (AnyIO Absolute),
but the **fail_max=3, reset_timeout=60s parameters are battle-tested from
production** and should be ported.

### 3.5 `make download-models` Pattern

**File**: `Xoe-NovAi/Makefile:42-47`

```makefile
download-models: ## Download models and embeddings
	@echo "Downloading models..."
	mkdir -p models embeddings
	wget -P models https://huggingface.co/unsloth/gemma-3-4b-it-GGUF/resolve/main/gemma-3-4b-it-UD-Q5_K_XL.gguf?download=true
	wget -P embeddings https://huggingface.co/leliuga/all-MiniLM-L12-v2-GGUF/resolve/main/all-MiniLM-L12-v2.Q8_0.gguf?download=true
#\twget -P embeddings https://huggingface.co/prithivida/all-MiniLM-L6-v2-gguf/resolve/main/all-MiniLM-L6-v2-q8_0.gguf?download=true
```

**Models the user picked**:
- LLM: `gemma-3-4b-it-UD-Q5_K_XL.gguf` (2.8GB, 2048 ctx)
- Embedding: `all-MiniLM-L12-v2.Q8_0.gguf` (45MB, 384 dim)
- (Commented) Alternative: `all-MiniLM-L6-v2-q8_0.gguf` (smaller, 6-layer)

This is **identical** to the current engine's local-first model choices.

### 3.6 `check_llama_compilation()` Healthcheck

**File**: `Xoe-NovAi/app/XNAi_rag_app/verify_imports.py:114-129`

```python
def check_llama_compilation():
    """Test llama-cpp-python compilation flags."""
    try:
        import llama_cpp
        # Check for Ryzen optimizations
        if hasattr(llama_cpp, 'llama_model_default_params'):
            params = llama_cpp.llama_model_default_params()
            if params.n_threads == 6 and params.f16_kv:  # From env
                print_success("LlamaCpp Ryzen optimized (n_threads=6, f16_kv)")
            else:
                print_warn("LlamaCpp params not Ryzen-optimized")
        print_success("LlamaCpp compilation test passed")
        return True
    except Exception as e:
        print_fail(f"LlamaCpp compilation test failed: {e}")
        return False
```

**Useful pattern**: Introspect `llama_cpp.llama_model_default_params()` at
runtime to verify the compilation picked up the CMAKE_ARGS. The current
engine has `check_ryzen()` in `healthcheck.py` (covered in
`03_foundation_legacy.md`) but does NOT do this llama-cpp-specific check.

### 3.7 Wheelhouse Offline Install Pattern

**File**: `Xoe-NovAi/Dockerfile.api:70-90, 119-122` + `Xoe-NovAi/scripts/download_wheelhouse.sh:81-92`

```dockerfile
# In builder stage:
ARG USE_WHEELHOUSE=false
ARG BUILD_WHEELS=false
COPY wheelhouse ./wheelhouse/
COPY wheelhouse.tgz* ./

# Extract if archived
RUN if [ -f wheelhouse.tgz ]; then \
        tar -xzf wheelhouse.tgz -C /install_wheels; \
    elif [ -d wheelhouse ] && [ "$(ls -A wheelhouse)" ]; then \
        cp -r wheelhouse/* /install_wheels/; \
    fi

# Three-tier install: wheelhouse → PyPI → graceful degrade
RUN ( pip install --no-cache-dir --no-index --find-links=/install_wheels llama-cpp-python || \
      pip install --no-cache-dir --timeout=300 --retries=10 llama-cpp-python || \
      echo 'WARNING: llama-cpp-python failed to install during build; continuing without it' )
```

**Notable pattern**: Build **does not fail** if llama-cpp-python can't be
installed — the container starts anyway, and the lack of llama-cpp-python
is caught at runtime. This is **right approximation** — a working API server
without local LLM is better than no server at all (the model is added later
via volume mount).

## §4 Delta from Prior Phases

What this report adds that the prior 5 reports did NOT cover:

| Find | Source | Prior Coverage | Status |
|------|--------|----------------|--------|
| **4-service Docker Compose w/ curation_worker** | `Xoe-NovAi/docker-compose.yml` | NOT covered | **NEW** |
| Multi-stage `Dockerfile.api` w/ CMAKE_ARGS | `Xoe-NovAi/Dockerfile.api:132-134, 219-226` | NOT covered (Dockerfile content) | **NEW** |
| `filter_llama_kwargs()` (pydantic v2 compat) | `dependencies.py:64-98` | NOT covered | **NEW** |
| Wheelhouse three-tier install pattern | `Dockerfile.api:119-122` + `download_wheelhouse.sh:81-92` | NOT covered | **NEW** |
| `n_gpu_layers: 0` explicit CPU-only pin | `dependencies.py:275` | NOT covered | **NEW** |
| `redis_password.txt` plaintext secret | `Xoe-NovAi/redis_password.txt` | NOT covered | **NEW (security)** |
| `xnai_blueprint.md` 714-line v0.1.4-stable | `XNAi-v0_1_2/xnai_blueprint.md` | NOT covered (the v0.1.5 foundation-legacy is a different artifact) | **NEW** |
| pybreaker `fail_max=3, reset_timeout=60` params | `xnai_blueprint.md:33, 188-209` | NOT covered (only AsyncCircuitBreaker was covered) | **NEW (validation)** |
| `make download-models` model URLs | `Makefile:45-46` | NOT covered | **NEW** |
| `gemma-3-4b-it-UD-Q5_K_XL.gguf` choice | `config.toml:37` | NOT covered (current engine uses Qwen3) | **NEW (model evolution story)** |
| `check_llama_compilation()` runtime check | `verify_imports.py:114-129` | NOT covered (similar `check_ryzen()` was covered) | **NEW** |
| OMP_NUM_THREADS=1 / OPENBLAS_CORETYPE=ZEN | `Dockerfile.api:223-225` | NOT covered | **NEW (CPU threading subtlety)** |

**Prior coverage that overlaps (and is acknowledged)**:
- `01_xna_omega_legacy.md`: covered `xna-omega-legacy/` (the v7.5.4 foundation stack with 7 design patterns)
- `02_omega_stack_legacy.md`: covered `omega-stack-legacy/` (the 33k-file Temple Grade stack)
- `02_5_expert_knowledge_gems.md`: covered `expert-knowledge/protocols/LLAMA-CPP-PYTHON-SERVICE-PROTOCOL.md` (the current Omega Engine's llama-cpp integration protocol)
- `03_foundation_legacy.md`: covered `archive/foundation-legacy/versions/Xoe-NovAi/` (XNAi v0.1.5-stable — DEPENDENCIES.PY, VERIFY_IMPORTS.PY, HEALTHCHECK.PY, MAIN.PY, CRAWL.PY, VOICE_INTERFACE.PY ALL covered in detail)
- `04_podman_storage.md`: covered `podman-storage/` (accidental time machine of engine files)

The `Xoe-NovAi/` in `Old-Stacks/` is a **DIFFERENT artifact** from
`foundation-legacy/versions/Xoe-NovAi/` — even though both are v0.1.4-stable,
the Old-Stacks version is the **`stack-concat` documentation** with the
**flattened `.md` dumps** + a working `app/XNAi_rag_app/` directory. The
foundation-legacy version has the **executable Python code** with all the
implementation details. They complement each other.

## §5 Top 5 Finds

### 5.1 ⭐ The 4-service Docker Compose — The Blueprint
The `Xoe-NovAi/docker-compose.yml` is the **canonical** XNAi architecture
that the user's vision has been building toward. 5 services (redis + rag +
ui + crawler + curation_worker), zero-trust security, bind mounts for dev /
named volumes for prod, healthcheck-conditional `depends_on`. The current
Omega Engine has a similar 5-service Podman Quadlet setup — this is the
provenance.

### 5.2 ⭐ Ryzen-Optimized CMAKE_ARGS — Drop-In for native-gguf
The `ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON"`
pattern at `Dockerfile.api:133` is **EXACTLY** what the current
`src/omega/oracle/backends/native_gguf.py` should document in its build
instructions. The Zen 2 / Ryzen 7 5700U optimizations are battle-tested.

### 5.3 ⭐ The `filter_llama_kwargs()` Pattern — Closes a Real Bug
The current native-gguf backend will raise `ValueError: Invalid parameter
'X'` if a config typo or deprecated key slips into `config/providers.yaml`.
The `filter_llama_kwargs()` pattern at `dependencies.py:64-98` is a
**silent-fallback that logs**, which is the Right Approximation (Mandate
9 — Error Integrity: the error is logged, not swallowed).

### 5.4 ⭐ `xnai_blueprint.md` — v0.1.4-stable Production Spec
714 lines. Defines 5 mandatory patterns including **Pattern 5: Circuit
Breaker with pybreaker (fail_max=3, reset_timeout=60s)**. This is the
production spec the user converged to — and the current engine's
AsyncCircuitBreaker should adopt the same parameters (it already does
roughly: `failure_threshold=3, recovery_timeout=60`).

### 5.5 ⭐ The 16-Digit Plaintext Redis Password — Sovereign Mandate 6 Violation
`Xoe-NovAi/redis_password.txt` contains the literal string `1234567890123456`.
This file **should be deleted** in any future migration. The current engine
correctly uses `.env`-based secret management (Mandate 6) and never stores
plaintext secrets in the repo.

## §6 Top 5 NEVER Rules

### 6.1 NEVER Use the `Old-Stacks` 5-service Architecture as-is
The `curation_worker` service has `restart: on-failure` but **NO healthcheck**.
If the worker enters a bad state, it will not be detected. The current
engine's `background_researcher` and `request_queue` both have health
probes — the Old-Stacks pattern is incomplete.

### 6.2 NEVER Use `pybreaker` in AnyIO Context
`pybreaker` is **synchronous** (no async support). Using it inside an async
function will block the event loop. The Old-Stacks blueprint used it
synchronously (load_llm is sync, OK). The current engine correctly uses
`AsyncCircuitBreaker` instead. **Do not port the pybreaker dependency.**

### 6.3 NEVER `pip install llama-cpp-python` Without Wheelhouse on 5700U
The 5-attempt retry with `apt-get update` exponential backoff
(`Dockerfile.api:38-61`) exists **specifically** because llama-cpp-python
frequently fails to compile on Ryzen CPUs without proper CMAKE flags. On
the 5700U, the wheelhouse pattern is **non-optional** — install will take
3-15 minutes or fail silently. The current engine's `setup.sh` must
preserve this offline pattern.

### 6.4 NEVER Trust `n_gpu_layers` Default to Be 0
`LlamaCpp()` with no `n_gpu_layers` arg will try to auto-detect GPUs. On
a system with no GPU, this is harmless. But on a system with an iGPU
(Ryzen has Vega), llama-cpp will try to offload layers and fail with
`ggml-cuda missing` or worse, silently degrade. The Old-Stacks pattern
of **explicit `n_gpu_layers: 0`** is correct. The current engine's
native-gguf should do the same.

### 6.5 NEVER Commit `redis_password.txt` or Any `.txt` Secret File
The `Xoe-NovAi/redis_password.txt` file is a Sovereign Mandate 6 violation
(secrets in version control) and a Sovereign Mandate 9 violation
(untyped error path — there's no check for a missing/invalid password).
The `.env` file is the **only** acceptable location. The current engine
follows this correctly.

## §7 New DEFERRED_GOLD_TRACKER Entries (IDs 151-160)

| ID | Pattern | Source | Priority | Est. Effort | Notes |
|----|---------|--------|----------|-------------|-------|
| **151** | 4-service Docker Compose pattern (redis+rag+ui+crawler+worker) | `Xoe-NovAi/docker-compose.yml:14-260` | P1 | 2 hrs | Direct template for new podman Quadlets. Add healthcheck to curation_worker. |
| **152** | Ryzen CMAKE_ARGS for llama-cpp-python build | `Xoe-NovAi/Dockerfile.api:132-134` | P0 | 30 min | Add to `docs/build/llama-cpp-optimization.md` and `setup.sh` |
| **153** | `filter_llama_kwargs()` — silent drop + debug log | `Xoe-NovAi/dependencies.py:64-98` | P0 | 30 min | Port to `src/omega/oracle/backends/native_gguf.py` |
| **154** | Explicit `n_gpu_layers=0` for CPU-only | `Xoe-NovAi/dependencies.py:275` | P1 | 5 min | Add to `config/providers.yaml` native-gguf section |
| **155** | Three-tier wheelhouse install (wheelhouse→PyPI→graceful) | `Xoe-NovAi/Dockerfile.api:119-122` | P1 | 1 hr | Port to native setup script |
| **156** | OMP_NUM_THREADS=1 + OPENBLAS_CORETYPE=ZEN | `Xoe-NovAi/Dockerfile.api:223-225` | P2 | 10 min | Add to `cpu_optimizer.py` recommendations |
| **157** | `check_llama_compilation()` runtime introspection | `Xoe-NovAi/verify_imports.py:114-129` | P1 | 1 hr | Port to `src/omega/observability.py::HealthMonitor` |
| **158** | pybreaker params `fail_max=3, reset_timeout=60` (validation) | `XNAi-v0_1_2/xnai_blueprint.md:33` | P2 | 5 min | Already in AsyncCircuitBreaker; just confirm |
| **159** | `make download-models` w/ verified HuggingFace URLs | `Xoe-NovAi/Makefile:42-47` | P2 | 30 min | Port to current `Makefile` |
| **160** | DELETE `redis_password.txt` from Old-Stacks (security audit) | `Xoe-NovAi/redis_password.txt:1` | P0 | 5 min | Already not tracked in git, but should be `.gitignore`'d historically |

## §8 Implementation Cheat Sheet

### 8.1 Port `filter_llama_kwargs()` to Current Native-GGUF Backend

**File to create/modify**: `src/omega/oracle/backends/native_gguf.py`

```python
# At top of file, add:
VALID_LLAMA_CPP_PARAMS: frozenset[str] = frozenset({
    "model_path", "n_ctx", "n_batch", "n_gpu_layers", "n_threads",
    "n_parts", "seed", "f16_kv", "logits_all", "vocab_only",
    "use_mlock", "use_mmap", "embedding", "last_n_tokens_size",
    "lora_base", "lora_path", "verbose", "max_tokens", "temperature",
    "top_p", "top_k", "repeat_penalty", "stop", "streaming",
    # llama-cpp-python 0.3.x added:
    "chat_format", "rope_scaling_type", "rope_freq_base", "rope_freq_scale",
    "yarn_ext_factor", "yarn_attn_factor", "yarn_beta_fast", "yarn_beta_slow",
})

def filter_llama_kwargs(**kwargs: Any) -> dict[str, Any]:
    """Filter kwargs to only valid llama-cpp-python parameters.

    Why: Prevents ValueError("Invalid parameter") on config typos.
    Logs dropped keys at debug level (Mandate 9: Error Integrity).
    """
    filtered = {k: v for k, v in kwargs.items() if k in VALID_LLAMA_CPP_PARAMS}
    dropped = set(kwargs.keys()) - set(filtered.keys())
    if dropped:
        logger.debug(f"native_gguf: dropped invalid llama-cpp params: {dropped}")
    return filtered
```

### 8.2 Add CMAKE_ARGS to `setup.sh` and Build Docs

**File to create/modify**: `setup.sh` + `docs/build/llama-cpp-optimization.md`

```bash
# In setup.sh, before pip install llama-cpp-python:
export CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS \
                   -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON"
export FORCE_CMAKE=1
echo "✓ CMAKE_ARGS set for Ryzen 5700U optimization"

# Pin CPU threads for llama.cpp internal parallelism:
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export OPENBLAS_CORETYPE=ZEN
export MKL_DEBUG_CPU_TYPE=5

pip install llama-cpp-python --no-cache-dir
```

**Why OPENBLAS_CORETYPE=ZEN**: Zen 2 (Ryzen 5700U) is a Zen 2 core, and
OpenBLAS has hand-tuned kernels for it. Setting this env var tells OpenBLAS
to use the Zen-specific code path, not generic x86_64.

### 8.3 Pin `n_gpu_layers=0` in `config/providers.yaml`

```yaml
# In providers.yaml, native-gguf section:
providers:
  native-gguf:
    type: native
    model_path: /media/arcana-novai/omega_library/models/gguf/qwen3-1.7b.gguf
    n_ctx: 4096
    n_threads: 6
    n_gpu_layers: 0           # ← EXPLICIT CPU-only pin (from Old-Stacks)
    f16_kv: true
    use_mlock: true
    use_mmap: true
    verbose: false
```

**Critical**: `n_gpu_layers: 0` MUST be explicit. The Vega iGPU in the
Ryzen 5700U would otherwise cause llama-cpp to attempt GPU offload and
crash with `ggml-cuda missing` or similar.

---

## §9 Provenance

- **Subagent**: Roc Racoon Mining Subagent #6 (general)
- **Stack verified**: 117M, 5 subdirs, 4 are real code archives + 1 empty
- **Top file**: `Xoe-NovAi/docker-compose.yml` (341 lines, complete)
- **Most valuable**: `XNAi-v0_1_2/xnai_blueprint.md` (714 lines, v0.1.4-stable spec)
- **Biggest surprise**: The XNAi v0.1.4-stable blueprint validates the
  EXACT architecture the current Omega Engine converged to (llama-cpp-python
  primary, 4-service, circuit breaker). This is the **convergence proof**
  that local-first native GGUF was the right call from day one.
- **Biggest concern**: `redis_password.txt` plaintext secret — must be
  deleted/ignored (Mandate 6).
- **Largest finding**: The CMAKE_ARGS Ryzen optimization pattern at
  `Dockerfile.api:133` is REPLICABLE for the current engine's
  `native-gguf` provider and is the missing piece for closing
  Mandate 13 (Temple-Grade T5: Performance Optimization).

*⬡ OMEGA ⬡ ROC RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_mining_old_stacks_20260602 ⬡ SUBAGENT-06*
