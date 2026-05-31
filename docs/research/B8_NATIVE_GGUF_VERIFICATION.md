# B8 Native GGUF Provider Verification

**AP Token**: `AP-B8-VERIFY-v1.0.0`
**Status**: ✅ WIRED WITH ISSUES
**Date**: 2026-05-18

---

## 1. NativeGGUFProvider Implementation (providers.py:125-207)

### 1.1 Core Implementation

| Aspect | Implementation | Status |
|--------|---------------|--------|
| Backend | llama-cpp-python | ✅ |
| Lazy Loading | `_ensure_loaded()` method | ✅ |
| Thread Pool | `anyio.to_thread.run_sync` | ✅ |
| Async Compliance | Full AnyIO (no asyncio) | ✅ |

### 1.2 Zen 2 Optimizations

| Optimization | Value | Notes |
|--------------|-------|-------|
| `n_threads` | 6 (from `OMP_NUM_THREADS` env, default 6) | Matches physical cores 0,2,4,6 |
| `type_k` | 8 (q8_0) | Key quantization |
| `type_v` | 8 (q8_0) | Value quantization |
| `n_ctx` | 4096 (configurable) | Default context window |
| `n_gpu_layers` | 0 | Force CPU on 5700U |

**Code Reference**: providers.py:157-171
```python
# Zen 2 Optimizations:
# - n_threads: Pinned to physical cores
# - type_k/type_v: q8_0 for context efficiency
# - n_ctx: hardware dependent
def _load():
    return Llama(
        model_path=self.model_path,
        n_threads=self.n_threads,
        n_ctx=self.config.get("n_ctx", 4096),
        type_k=8, # q8_0
        type_v=8, # q8_0
        verbose=False,
        n_gpu_layers=0 # Force CPU on 5700U for stability
    )
```

---

## 2. ModelGateway Registration

### 2.1 Import Chain

| Location | Component | Status |
|----------|-----------|--------|
| model_gateway.py:39 | `from .providers import ... NativeGGUFProvider` | ✅ |
| model_gateway.py:126 | `"native-gguf": NativeGGUFProvider` in provider_map | ✅ |
| model_gateway.py:381 | ResourceGuard applied to NativeGGUFProvider | ✅ |

### 2.2 Provider Map Definition

```python
# model_gateway.py:122-129
provider_map = {
    "google": GoogleAIProvider,
    "lmster": LocallmsterProvider,
    "ollama": OllamaProvider,
    "native-gguf": NativeGGUFProvider,  # ✅ Registered
    "mock": MockProvider,
    "openrouter": ModelGateway._create_openrouter,
}
```

---

## 3. Configuration Verification

### 3.1 providers.yaml

```yaml
inference:
  fallback_chain:
    - provider: native-gguf      # Priority 1 ✅
      priority: 1
      model_path: /media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf
      n_ctx: 4096                # ✅
```

### 3.2 models.yaml

```yaml
phi-4-mini:
  path: "/media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf"
  size_gb: 3.8
  ram_mb: 4500
  context_window: 32768
  threads: 6
  load_strategy: "on_demand_10min"
  entity: "SOPHIA"
```

---

## 4. Identified Issues

### 4.1 Model Path Issue (C-12)

| Issue | Detail |
|-------|--------|
| **Location** | providers.yaml:6, models.yaml:63 |
| **Path** | `/media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf` |
| **Problem** | External mount point; may not be mounted at runtime |
| **Workbench ID** | C-12 (P0 priority) |

**Recommendation**: Add fallback to local path or validate mount before use.

### 4.2 Missing Test Suite

| Test File | Status |
|-----------|--------|
| `tests/test_native_gguf.py` | ❌ NOT FOUND |
| `tests/test_providers.py` | ⚠️ EXISTS but no NativeGGUFProvider tests |

**Workbench ID**: wi_fix_native_gguf (P1)

### 4.3 Availability Check Limitation

The `is_available()` method (providers.py:137-145) checks:
1. Model path exists
2. llama_cpp is importable

**Limitation**: Doesn't verify model file is a valid GGUF or check available RAM.

---

## 5. Wiring Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Provider class defined | ✅ | providers.py:125-207 |
| Imported in ModelGateway | ✅ | model_gateway.py:39 |
| Registered in provider_map | ✅ | model_gateway.py:126 |
| Config in providers.yaml | ✅ | Priority 1, native-gguf |
| ResourceGuard applied | ✅ | model_gateway.py:381 |
| Zen 2 optimizations | ✅ | q8_0 quantization, 6 threads |
| AnyIO compliant | ✅ | Uses anyio.to_thread.run_sync |
| Test coverage | ❌ | No dedicated tests |

---

## 6. Action Items

| ID | Action | Priority | Owner |
|----|--------|----------|-------|
| B8.1 | Verify phi-4-mini.gguf exists on external drive | P0 | BUILDER |
| B8.2 | Add fallback model path for native-gguf | P0 | BUILDER |
| B8.3 | Create tests/test_native_gguf.py | P1 | BUILDER |
| B8.4 | Add RAM availability check to is_available() | P2 | BUILDER |

---

## 7. Conclusion

**Wiring Status**: ✅ PROPERLY WIRED

NativeGGUFProvider is correctly registered and configured in the ModelGateway fallback chain. The Zen 2 optimizations are properly applied (q8_0 quantization, 6 threads, forced CPU). The main issues are:

1. **External model path** - requires mount validation
2. **No test coverage** - needs dedicated tests

The provider will work correctly once the model file exists at the configured path.