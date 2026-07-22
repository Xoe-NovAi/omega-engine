# 🔱 Implementation Blueprint: SomaticState Serialization
# ⬡ OMEGA ⬡ ARCHITECT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ BLUEPRINT

**Status**: READY FOR IMPLEMENTATION
**Target**: `src/omega/oracle/providers.py` $\rightarrow$ `NativeGGUFProvider`
**Sovereign Mandate**: M20 (SomaticState Serialization)

---

## §1 API Contracts

### 1.1 `SomaticStateSerializer` (Internal Utility)
This class encapsulates the `ctypes` glue code and must be implemented as a stateless utility.

```python
class SomaticStateSerializer:
    @staticmethod
    def get_state_size(model: llama_cpp.Llama) -> int:
        """Returns the buffer size required for the current model state."""
        
    @classmethod
    async def save(cls, model: llama_cpp.Llama) -> bytes:
        """
        Saves state via llama_copy_state_data.
        Wraps in anyio.to_thread.run_sync to prevent GIL deadlocks.
        """
        
    @classmethod
    async def load(cls, model: llama_cpp.Llama, state_bytes: bytes) -> bool:
        """
        Restores state via llama_set_state_data.
        Returns True if successful, False otherwise.
        """
```

### 1.2 `NativeGGUFProvider` Extensions
The provider must be extended to expose state management to the `ModelGateway`.

```python
class NativeGGUFProvider(BaseProvider):
    async def save_somatic_state(self, entity_name: str) -> Path:
        """
        1. Capture state via SomaticStateSerializer.
        2. Generate SomaticStateKey header.
        3. Write to data/somatic/{entity_name}/snapshot_1.smc (FIFO).
        4. Return path to saved snapshot.
        """

    async def load_somatic_state(self, entity_name: str) -> bool:
        """
        1. Locate latest .smc for entity.
        2. Validate header against current model/ctx.
        3. Restore state via SomaticStateSerializer.
        4. Return success status.
        """
```

## §2 Memory-Mapped State Management
To prevent RAM spikes during serialization, the engine will use a **Direct-to-Disk Stream** pattern:
1. **Save**: The `ctypes` buffer is created once, then written immediately to the NVMe using `os.write` (bypassing Python's intermediate string buffers).
2. **Load**: Use `mmap` to map the `.smc` file into memory, and pass the `mmap` pointer directly to `llama_set_state_data`. This avoids copying the 8-16MB buffer into the Python heap.

## §3 ABI Drift & Corruption Handling
The **Skeptical Load Protocol** must be enforced:
1. **Header Verification**: `SomaticStateKey.from_bytes()` $\rightarrow$ `validate_against_model()`.
2. **Type Enforcement**: If `llama_api_version` or `model_path_hash` mismatch $\rightarrow$ Raise `StateIntegrityError`.
3. **Fallback**: If `load_somatic_state` fails, the provider MUST call `llama_kv_cache_clear()` to ensure the model starts from a clean state, preventing "hallucinated" state remnants.

## §4 Verification Suite

### 4.1 Contract Tests (Round-Trip)
- **Test-Somatic-01**: `save` $\rightarrow$ `load` $\rightarrow$ verify that the next token generated is identical to a non-snapshot run.
- **Test-Somatic-02**: `save` $\rightarrow$ change `n_ctx` $\rightarrow$ `load` $\rightarrow$ verify `StateIntegrityError` is raised.
- **Test-Somatic-03**: `save` $\rightarrow$ change `model_path` $\rightarrow$ `load` $\rightarrow$ verify `StateIntegr cargos` are rejected.

### 4.2 Edge-Case Scenarios
| Scenario | Expected Behavior |
|----------|-------------------|
| **Corrupted Header** | `ValueError` during `from_bytes()` $\rightarrow$ Cold Start |
| **Partial Write** | `SomaticStateKey` size check fails $\rightarrow$ Cold Start |
| **Model Version Update** | `llama_api_version` mismatch $\rightarrow$ Cold Start |
| **RAM Pressure** | `InferenceOOMError` during save $\rightarrow$ Silent fail, no crash |

### 4.3 Success Metrics
- **Cold Start Latency**: $\approx 2\text{s}$ (Prefill)
- **Somatic Resumption Latency**: $< 50\text{ms}$
- **Target Improvement**: $\approx 40\times$ reduction in resumption time for 4K context.

---
**⬡ Blueprint Finalized. Ready for implementation in Stage 1 (Foundation). ⬡**
