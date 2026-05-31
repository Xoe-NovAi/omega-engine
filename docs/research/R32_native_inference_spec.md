# 🔱 Omega Engine — Native GGUF Inference Spec
**AP Token**: `AP-NATIVE-GGUF-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ PHASE-0.18

## 1. Executive Summary
This specification defines the implementation of the **Native GGUF Backend**, the core of the Omega Engine's local-first autonomy. By integrating `llama-cpp-python` directly into the Provider Fabric, we eliminate network overhead and ensure absolute data sovereignty.

## 2. Reclaimed Legacy Patterns
The following patterns have been recovered from `xna-omega-backup-20260502135803`:
- **Client/Config Split**: Use of `LocalLlmConfig` (dataclass) and `LocalLlmClient` (lifecycle manager).
- **Lifecycle Management**: `LocalLlmClient.reload()` for dynamic model switching.
- **Resource Guard**: Integration with `anyio.Semaphore(1)` to prevent OOM during native inference.
- **Memory Strategy**: Use of `mmap=True` for fast loading and `mlock=False` to allow OS paging on 14GB RAM systems.

## 3. SOTA Implementation Spec

### 3.1 Architecture
The native backend must be implemented as a `NativeGGUFProvider` inheriting from `BaseProvider`.

```python
class NativeGGUFProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None # Lazy loaded LocalLlmClient

    async def complete(self, prompt: str, **kwargs) -> str:
        if not self.client:
            self.client = LocalLlmClient(LocalLlmConfig(**self.config.params))
        return await self.client.generate(prompt, **kwargs)
```

### 3.2 Logic Flow
1. **Initialization**: `LocalLlmConfig` reads model path, `n_ctx`, `n_threads`, and `cache_type`.
2. **Instantiation**: `LocalLlmClient` initializes the `llama_cpp.Llama` object.
3. **Execution**:
    - Prompt is passed to `client.generate()`.
    - `ResourceGuard` ensures mutual exclusion.
    - Output is streamed or returned as a complete string.
4. **Cleanup**: `client.reload()` handles the unloading of models to free VRAM/RAM.

### 3.3 Performance Targets (Ryzen 5700U)
- **Latency**: < 200ms Time-To-First-Token (TTFT) for 1B-3B models.
- **Throughput**: 15-30 tokens/sec for Q4_K_M quantization.
- **RAM Footprint**: < 4GB for 3B models, < 8GB for 7B models.

## 4. Caveats & Pitfalls
- **Thread Contention**: Setting `n_threads` too high (> 8) causes context-switching overhead on Zen 2. **Target: 6**.
- **OOM Risks**: Large context windows (`n_ctx > 8192`) can crash the process. Implement a hard limit in `LocalLlmConfig`.
- **Library Versioning**: `llama-cpp-python` must be compiled with `GGML_BLAS=ON` (OpenBLAS) for AVX2 acceleration.

## 5. Validation Criteria
- [ ] `make test` passes for `NativeGGUFProvider`.
- [ ] Benchmarks show $\geq 15$ t/s for Qwen-1.5B.
- [ ] `ResourceGuard` successfully blocks concurrent native calls.
