# 🔧 Local Inference — Wiring, Benchmarking & Troubleshooting

**AP Token**: `AP-LOCAL-INFERENCE-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ local-first ⬡ llama.cpp ⬡ ZEN2

---

## 🎯 Purpose

This document is the single source of truth for how local inference works in the Omega Engine. It covers:

1. **Provider fabric wiring** — how models flow from config → provider → inference
2. **Model registry** — `models.yaml` as the single source of truth for paths, context, RAM, KV cache
3. **Resource guard** — three-signal OOM protection (PSI + MemAvailable + cgroup v2)
4. **Benchmarking** — how to measure latency, throughput, memory on Zen 2
5. **Troubleshooting** — common failure modes and fixes

---

## 🏗️ Architecture Overview

```
User Query
    │
    ▼
Oracle.talk() / Oracle.summon()
    │
    ▼
ModelGateway.generate()
    │
    ├──► ProviderSelector (local-first: native-gguf → lmster → ollama → cloud)
    │
    ▼
ResourceGuard.lock(weight=model_ram_mb)
    │
    ├──► OOMProtector.check_available(required_gb)
    │       ├── PSI (Pressure Stall Info) — /proc/pressure/memory
    │       ├── MemAvailable — /proc/meminfo (kernel reclaimable)
    │       └── cgroup v2 memory.pressure — container-aware
    │
    ▼
NativeGGUFProvider.generate()
    │
    ├──► _ensure_loaded() — loads llama_cpp.Llama directly (no worker process)
    │       ├── CPU affinity pinned to cores [0,2,4,6] (Zen 2 CCX-aware)
    │       ├── KV cache q8_0 (50% memory vs f16, negligible quality loss)
    │       ├── n_threads = 6 (configurable via cvar `config.gguf.n_threads`)
    │       └── n_ctx auto-selected by memory pressure (32K → 16K → 8K → 4K)
    │
    ├──► create_chat_completion() — applies GGUF embedded Jinja chat template
    │       ├── enable_thinking=False via chat_handler wrapper
    │       ├── logit_bias supported (token-level steering)
    │       └── repetition_penalty supported
    │
    ▼
GenerateResult(text, provider_name="native-gguf", is_cloud=False, logprobs, latency_ms)
```

---

## 📋 Configuration Files

### 1. `config/providers.yaml` — Provider Fabric

```yaml
inference:
  fallback_chain:
    - provider: native-gguf
      priority: 0
      enabled: true
      model_path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf
      n_threads: 4
      max_concurrent: 1
      numa: "disable"
      supported_models:
        - qwen3-1.7b-local
        - qwen3-4b-thinking-local
        # ... 138 total models listed
```

**Key fields:**
- `model_path` — supports `env:VAR/path` prefix (resolved in `_merge_native_gguf_config()`)
- `max_concurrent` — enforced by AdmissionController (C-10)
- `numa: "disable"` — prevents cross-CCX migration on Zen 2
- `supported_models` — declarative list; must match `models.yaml` entries

### 2. `config/models.yaml` — Model Registry (Single Source of Truth)

```yaml
models:
  qwen3-1.7b:
    context_budget: 15000
    provider: native-gguf
    path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf
    size_gb: 1.6
    ram_mb: 2048
    context_window: 8192
    role: "P1-P10 pillars, fast inference"
    kv_cache:
      key_type: "q8_0"
      value_type: "q8_0"
```

**Required fields per model:**
| Field | Purpose |
|-------|---------|
| `path` | GGUF file path (supports `env:VAR/`) |
| `size_gb` | Model file size on disk |
| `ram_mb` | Estimated RAM for model weights + overhead |
| `context_window` | Max context tokens (maps to `n_ctx`) |
| `kv_cache.key_type/value_type` | `q8_0` (default), `q4_0`, `q5_0`, `f16` |
| `provider` | Which provider owns this model |

### 3. `config/entity_model_affinity.yaml` — Entity → Model Routing

```yaml
roc_racoon:
  preferred_models:
    local_fast:
      model: "qwen3-1.7b"
      provider: "native-gguf"
      size: "~1.7B"
    local_deep:
      model: "qwen3-4b-thinking-q4_k_m"
      provider: "native-gguf"
      size: "~4B"
  routing_rules:
    - match:
        domain: ["mining", "archaeology", "legacy"]
      use: local_fast
```

**Resolution order:**
1. Entity affinity → preferred model
2. ModelGateway.resolve_entity_affinity() → provider + model
3. ProviderSelector picks available provider from fallback chain
4. ResourceGuard admits based on `ram_mb` + KV cache estimate

---

## 🛡️ Resource Guard — Three-Signal OOM Protection

Located: `src/omega/oracle/oom_protector.py`

```python
# Decision logic (priority order):
1. MemAvailable < min_reserve_gb (2GB) → DENY_OOM_RISK
2. PSI full.avg10 > 5% → DENY_THRASHING (system frozen)
3. cgroup full.avg10 > 5% → DENY_THRASHING (container frozen)
4. PSI some.avg60 > 10% → THROTTLE (sustained pressure)
5. cgroup some.avg60 > 15% → THROTTLE (container pressure)
6. MemAvailable < throttle_gb (4GB) → THROTTLE (low headroom)
7. Otherwise → ALLOW
```

**Usage in ResourceGuard:**
```python
required_gb = (model_spec.ram_mb / 1024) + (context_window / 8192) * 0.5 + 1.0  # reserve
if not await oom_protector.check_available(required_gb):
    raise InferenceOOMError(...)
```

---

## 📊 Benchmarking Infrastructure

### Script: `scripts/benchmark_local.py`

```bash
# Run full benchmark suite
python scripts/benchmark_local.py \
  --models qwen3-1.7b,qwen3-4b-thinking,mimo-7b-rl \
  --prompts benchmark_prompts.jsonl \
  --runs 5 \
  --output benchmarks/$(date +%Y%m%d_%H%M%S).json
```

**Metrics captured per run:**
| Metric | Description |
|--------|-------------|
| `latency_ms` | Time to first token (TTFT) + total generation |
| `throughput_tps` | Tokens per second (completion_tokens / generation_time) |
| `peak_ram_mb` | Peak RSS during generation (via `psutil.Process`) |
| `kv_cache_mb` | Estimated from context_window × 2 bytes/token × layers |
| `cpu_util_pct` | Average across pinned cores |
| `thermal_c` | CPU package temp (if available) |

**Output format:**
```json
{
  "model": "qwen3-1.7b",
  "provider": "native-gguf",
  "timestamp": "2026-07-25T12:00:00Z",
  "hardware": "Ryzen 7 5700U (Zen 2, 8C/16T, 15W TDP)",
  "runs": [
    {
      "prompt_tokens": 128,
      "completion_tokens": 256,
      "latency_ms": 1842,
      "throughput_tps": 139.0,
      "peak_ram_mb": 2847,
      "cpu_util_pct": 78.3
    }
  ],
  "summary": {
    "avg_latency_ms": 1842,
    "avg_throughput_tps": 139.0,
    "avg_peak_ram_mb": 2847
  }
}
```

### Benchmark Prompts (`benchmark_prompts.jsonl`)

```jsonl
{"prompt": "Explain the Roc bird myth in 3 sentences.", "domain": "mythology", "expected_tokens": 64}
{"prompt": "Write a Python function to parse a WAD file header.", "domain": "coding", "expected_tokens": 256}
{"prompt": "Summarize the key differences between q8_0 and q4_0 KV cache quantization.", "domain": "technical", "expected_tokens": 128}
{"prompt": "You are a mischievous raccoon engineer. Debug this kernel panic.", "domain": "persona", "expected_tokens": 512}
```

---

## 🔧 Troubleshooting

### 1. "Worker process did not initialize within 30s"
**Cause**: Old NativeGGUFProvider used `multiprocessing.Process` to isolate llama.cpp. Forked processes inherit parent's memory but llama.cpp context creation fails in child.

**Fix**: Use direct-load pattern (see `NativeGGUFProvider._ensure_loaded()` rewrite). Load `llama_cpp.Llama` in main process, run inference via `anyio.to_thread.run_sync()`.

### 2. "Refusing model load: estimated 3.2 GB required exceeds available RAM"
**Cause**: OOMProtector `check_available(required_gb)` returned False.

**Debug:**
```bash
# Check current pressure
python -c "
from src.omega.oracle.oom_protector import create_oom_protector
import asyncio
p = asyncio.run(create_oom_protector())
snap = asyncio.run(p.get_snapshot())
print(f'MemAvailable: {snap.memavailable_gb:.2f}GB')
print(f'PSI some.avg60: {snap.psi_some_avg60:.1%}')
print(f'PSI full.avg10: {snap.psi_full_avg10:.1%}')
decision = asyncio.run(p.check())
print(f'Decision: {decision.value}')
"
```

**Remediation:**
- Close other apps / browser tabs
- Reduce `n_ctx` in model config (8192 → 4096)
- Use smaller model (qwen3-1.7b instead of mimo-7b-rl)
- Increase `min_reserve_gb` in `OOMProtectorConfig` if you have swap

### 3. "Model file not found: env:OMEGA_MODELS_DIR/..."
**Cause**: `OMEGA_MODELS_DIR` environment variable not set.

**Fix:**
```bash
export OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models/gguf
# Or add to .env:
echo "OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models/gguf" >> .env
```

### 4. "Segmentation fault in llama_cpp"
**Cause**: Usually AVX2 instruction mismatch or corrupted GGUF file.

**Debug:**
```bash
# Verify file integrity
sha256sum /media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf

# Test direct load
python -c "
import llama_cpp
llm = llama_cpp.Llama(model_path='/media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf', n_ctx=4096, n_threads=4, verbose=True)
print(llm('Hello', max_tokens=10))
"
```

### 5. "Logit bias not working"
**Cause**: `logit_bias` passed to `create_chat_completion()` but token IDs are model-specific.

**Fix**: Use tokenizer to get token IDs:
```python
token_id = llm.tokenize(b" hello")[0]  # Get token ID for " hello"
result = llm.create_chat_completion(..., logit_bias={token_id: -100.0})
```

---

## 📝 Adding a New Local Model

### Step 1: Place GGUF file
```bash
cp /path/to/model.gguf /media/arcana-novai/omega_library/models/gguf/
```

### Step 2: Add to `config/models.yaml`
```yaml
models:
  my-new-model:
    context_budget: 20000
    provider: native-gguf
    path: env:OMEGA_MODELS_DIR/model.gguf
    size_gb: 4.7
    ram_mb: 6144
    context_window: 32768
    role: "Reasoning/coding specialist"
    kv_cache:
      key_type: "q4_0"
      value_type: "q4_0"
```

### Step 3: Add to `config/providers.yaml`
```yaml
providers:
  native-gguf:
    supported_models:
      - my-new-model
      # ... existing models
```

### Step 4: Update entity affinity (if needed)
```yaml
# config/entity_model_affinity.yaml
some_entity:
  preferred_models:
    local_deep:
      model: "my-new-model"
      provider: "native-gguf"
```

### Step 5: Test
```bash
python -c "
import asyncio
from src.omega.oracle.model_gateway import ModelGateway
gw = ModelGateway()
result = asyncio.run(gw.generate(
    model_name='my-new-model',
    system_prompt='Test',
    user_query='Say hello',
    max_tokens=20
))
print(result.text)
"
```

---

## 🔗 Related Docs

| Doc | Purpose |
|-----|---------|
| `docs/architecture/ORACLE_DEEP_DIVE.md` | Full Oracle architecture |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | C-10 Admission Control, C-2′ OOM Protector |
| `src/omega/oracle/providers.py` | NativeGGUFProvider implementation |
| `src/omega/oracle/resource_guard.py` | ResourceGuard + OOM integration |
| `src/omega/oracle/oom_protector.py` | Three-signal fusion logic |
| `src/omega/oracle/model_gateway.py` | Provider fabric, model resolution |
| `config/providers.yaml` | Provider fabric config |
| `config/models.yaml` | Model registry |
| `config/entity_model_affinity.yaml` | Entity → model routing |

---

## 📌 Quick Reference

| Task | Command / Location |
|------|-------------------|
| Test local inference | `python -m src.omega.oracle.model_gateway --model qwen3-1.7b --prompt "hello"` |
| Check provider health | `curl http://localhost:8016/health/providers` (via Omega Hub) |
| View OOM decision | `python -c "from src.omega.oracle.oom_protector import quick_check_sync; print(quick_check_sync())"` |
| Run benchmark | `python scripts/benchmark_local.py --models qwen3-1.7b --runs 3` |
| List available models | `python -c "from src.omega.oracle.model_gateway import ModelGateway; gw=ModelGateway(); print([m for m in gw.models])"` |

---

*Last updated: 2026-07-25 by @roc_racoon — Local Inference Architecture Audit*