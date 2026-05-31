# 🔱 Discovery: Native Inference Engine
**AP Token**: `AP-OMEGA-DISCOVERY-NATIVE-v1.0.0`
**Context**: Phase 1 Research Sprint

## 1. Legacy Audit Summary

Target: `xna-omega-legacy/src/omega/providers/local/`

### 1.1 `client.py` (LocalLlmClient)
- **Core Library**: `llama-cpp-python`
- **Class Pattern**: Singleton-capable client that maintains a resident `Llama` instance.
- **Public Methods**:
    - `initialize()`: Sets up core affinity, imports `Llama`, handles speculative decoding (`LlamaPromptLookupDecoding`), and instantiates the model.
    - `shutdown()`: Explicit `llm.close()` or `gc.collect()` to free memory.
    - `reload(path)`: Async wrapper using `anyio.to_thread.run_sync` to swap models safely.
    - `generate(prompt, ...)`: Synchronous inference call.
    - `stream(prompt, ...)`: Synchronous generator for token streaming.
    - `tokenize()` / `detokenize()`: Direct access to model's vocabulary.
- **Optimizations**:
    - `psutil.cpu_affinity()`: Pinning threads to physical cores.
    - `draft_model`: Integration with `ngram-simple` speculative decoding.
- **Async Strategy**: Every heavy call is wrapped in `anyio.to_thread.run_sync`.

### 1.2 `config.py` (LocalLlmConfig)
- **Schema**:
    - `model_path`: str
    - `context_window`: int (4096 default)
    - `n_threads`: int (8 default)
    - `n_gpu_layers`: int (0 default)
    - `type_k` / `type_v`: int (2 = Q4_0)
    - `core_affinity`: List[int]
    - `speculative_type`: str
- **Loading**: Supports `from_dict` and `from_toml`.

### 1.3 `dependencies.py` (Hardware Logic)
- **Vulkan Detection**: Logic to check for AMD RDNA2 iGPU support via Vulkan ICD files and `VK_KHR_cooperative_matrix`.
- **Memory Safety**: Mentions of <6GB RAM thresholds (though recently bypassed in legacy).

---

## 2. Gap Analysis

Target: `omega-engine/src/omega/oracle/`

### 2.1 ModelGateway Gap
- **Native Backend**: Currently missing. The fallback chain starts at `lmster` (HTTP).
- **Interface Mismatch**: `ModelGateway.generate()` expects a stateless call, but `NativeBackend` must manage a stateful model instance in memory.
- **Resource Management**: `ModelGateway` already has `ResourceGuard`, which perfectly aligns with the legacy need for single-model loading.

### 2.2 CpuOptimizer Gap
- **Current state**: Excellent theory on Zen 2 flags.
- **Missing implementation**: Real-world Vulkan detection and core pinning (from `dependencies.py`) needs to be ported to `CpuOptimizer.get_environment_variables()` or a new `enforce_affinity()` method.

### 2.3 Async Transition
- **Legacy**: Mixed usage of `asyncio` and `anyio`.
- **Required**: Strict `AnyIO` for the engine. `anyio.to_thread.run_sync` is the correct path for all `llama-cpp-python` interactions.

### 2.4 Configuration Conflicts
- `config/providers.yaml` currently defines provider metadata.
- `LocalLlmConfig` contains low-level hardware flags.
- **Action**: `NativeConfig` should pull its model path from `config/models.yaml` and its hardware flags from `config/omega.yaml` or `CpuOptimizer`.

---

## 3. Findings & Risks
- **Risk**: `llama-cpp-python` compilation on the target system. Must ensure `CMAKE_ARGS` match the `CpuOptimizer` recommendations.
- **Risk**: Memory fragmentation. `shutdown()` + `gc.collect()` is critical for the 14GB RAM limit.
- **Finding**: Speculative decoding using `LlamaPromptLookupDecoding` is "free" performance for the Zen 2 CPU and should be enabled by default.
