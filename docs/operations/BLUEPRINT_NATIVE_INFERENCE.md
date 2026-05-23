# 🔱 Blueprint: Native Inference Engine
**AP Token**: `AP-OMEGA-BLUEPRINT-NATIVE-v1.0.0`
**Context**: Implementation Strategy for Tier 1

## 1. Class: `NativeConfig`
**File**: `src/omega/oracle/backends/native_config.py`
**Source**: Ported from legacy `LocalLlmConfig` with schema alignment.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model_path` | str | "" | Full path to GGUF |
| `n_ctx` | int | 8192 | Context window |
| `n_threads` | int | 6 | Zen 2 optimal (75% cores) |
| `n_gpu_layers` | int | 0 | CPU-only default |
| `type_k` / `type_v` | int | 8 | GGML_TYPE_Q8_0 (Int8 KV) |
| `use_mmap` | bool | True | Fast loading |
| `num_pred_tokens` | int | 4 | Speculative draft length |

---

## 2. Class: `NativeBackend`
**File**: `src/omega/oracle/backends/native.py`
**Source**: Ported from `LocalLlmClient`.

### 2.1 Interface
```python
class NativeBackend:
    def __init__(self, config: NativeConfig): ...
    async def initialize(self) -> bool: ... # anyio.to_thread
    async def shutdown(self): ...
    async def generate(self, prompt: str, **kwargs) -> str: ... # anyio.to_thread
    async def stream(self, prompt: str, **kwargs): ... # yield via anyio
    def tokenize(self, text: str) -> List[int]: ...
```

---

## 3. Class: `CpuOptimizer` (Update)
**File**: `src/omega/oracle/cpu_optimizer.py`
**Task**: Integrate legacy hardware detection.

- **`detect_vulkan()`**: Check for RDNA2 iGPU acceleration.
- **`enforce_affinity()`**: Use `psutil` to pin process to physical cores (0, 2, 4, 6).

---

## 4. `ModelGateway` Integration
**File**: `src/omega/oracle/model_gateway.py`

1.  **Initialize**: `self._native = NativeBackend(config)` in `__init__`.
2.  **Fallback Chain**:
    ```python
    # 0. Try Native (Priority 1)
    if self.provider_strategy == "native":
        response = await self._native.generate(...)
        if response: return response
    ```
3.  **ResourceGuard**: All `NativeBackend` calls MUST be wrapped in `async with self.resource_guard.lock():`.

---

## 5. Test Specifications

### 5.1 Unit Tests (`tests/test_native_backend.py`)
- `test_native_initialization`: Verify model loads with specified `n_ctx`.
- `test_native_generation`: Verify synchronous-wrapped-async generation returns text.
- `test_native_tokenization`: Verify text → tokens roundtrip.
- `test_core_affinity`: Verify process affinity matches config.

### 5.2 Integration Tests
- `test_gateway_to_native`: Set `OMEGA_ENV=native` and verify `ModelGateway` routes to `NativeBackend`.

---

## 6. Implementation Roadmap (Effort Estimates)

| Step | Task | Effort |
|------|------|--------|
| 1 | `native_config.py` creation | 2h |
| 2 | `native.py` (Core logic + AnyIO conversion) | 6h |
| 3 | `cpu_optimizer.py` merge (Vulkan + Affinity) | 4h |
| 4 | `model_gateway.py` wiring | 4h |
| 5 | `test_native_backend.py` + verification | 4h |
| **Total** | | **2.5 Days** |
