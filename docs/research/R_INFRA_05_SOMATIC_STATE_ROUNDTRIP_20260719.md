# 🔬 R-INFRA-05: SomaticState Round-Trip Validation — llama.cpp Cognitive Continuity
**AP Token**: `AP-INFRA-05-SOMATIC-STATE-v1.0.0`
⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_05_somatic_state ⬡ 2026-07-19

---

## 🎯 MISSION
Validate **llama.cpp state serialization round-trip** (`llama_copy_state_data` / `llama_set_state_data`) with strict constraints. This is the "cognitive tattoo" — full KV cache capture/restore for death/rebirth continuity.

---

## 📋 CONTEXT FROM PRIOR RESEARCH

### HG-005 Findings (from R_CARMACK_HG-005_SOMATIC_STATE_20260719.md)
**llama.cpp State Serialization API:**
```c
// Copy state to buffer
size_t llama_copy_state_data(struct llama_context *ctx, uint8_t *dst);

// Restore state from buffer  
size_t llama_set_state_data(struct llama_context *ctx, const uint8_t *src);
```

**Critical Constraints (MUST match exactly):**
| Parameter | Must Match | Why |
|-----------|------------|-----|
| `n_ctx` | Context window size | KV cache dimensions |
| `n_embd` | Embedding dimension | State vector size |
| `n_layer` | Number of layers | Layer count in cache |
| `n_head` | Attention heads | Head dimension |
| `n_kv` | KV cache size | Buffer allocation |
| Model architecture | GGUF metadata | Tensor layout |
| Quantization | GGUF metadata | Memory layout |

**Buffer Size**: `n_layer * 2 * n_ctx * n_embd * sizeof(float16)` ≈ **2-8 GB** for 7B-70B models

### Integration Points
- **M20 SomaticState**: Mandate requires serialization via `anyio.to_thread.run_sync()`
- **MIAP Replay**: State capture → MIAP execution log → replay with state restore
- **Death/Rebirth**: On compaction → capture SomaticState → on hydration → restore

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. SomaticState Manager
**Location**: `src/omega/inference/somatic_state.py` (NEW)
```python
class SomaticStateManager:
    """Manages llama.cpp state capture/restore for cognitive continuity."""
    
    def __init__(self, model_path: str, n_ctx: int, n_gpu_layers: int):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.ctx = None
        
    async def capture_state(self, context_ptr: int) -> bytes:
        """Capture full KV cache state via llama_copy_state_data."""
        # 1. Get buffer size
        size = await anyio.to_thread.run_sync(llama_copy_state_data, context_ptr, None)
        # 2. Allocate buffer
        buffer = bytearray(size)
        # 3. Copy state
        await anyio.to_thread.run_sync(llama_copy_state_data, context_ptr, buffer)
        return bytes(buffer)
    
    async def restore_state(self, context_ptr: int, state_data: bytes) -> bool:
        """Restore KV cache state via llama_set_state_data."""
        result = await anyio.to_thread.run_sync(
            llama_set_state_data, context_ptr, state_data
        )
        return result == len(state_data)
    
    def validate_compatibility(self, other_model_path: str) -> CompatibilityReport:
        """Verify n_ctx, n_embd, n_layer, n_head, n_kv match exactly."""
```

### 2. Round-Trip Test
```python
# tests/test_somatic_state_roundtrip.py
async def test_somatic_state_roundtrip():
    """Full capture → save → load → restore → verify identical output."""
    
    # 1. Load model, run inference, capture state
    state = await somatic.capture_state(ctx_ptr)
    
    # 2. Save to disk (atomic write)
    await atomic_write(f"somatic_{session_id}.bin", state)
    
    # 3. New context, restore state
    new_ctx = await load_model(same_model_path, same_n_ctx)
    await somatic.restore_state(new_ctx, state)
    
    # 4. Verify identical next-token distribution
    logits_before = await infer(ctx, "The meaning of life is")
    logits_after = await infer(new_ctx, "The meaning of life is")
    assert np.allclose(logits_before, logits_after, rtol=1e-5)
```

### 3. Compatibility Validator
```python
def validate_model_compatibility(model_a: str, model_b: str) -> CompatibilityReport:
    """Extract GGUF metadata, compare critical parameters."""
    meta_a = extract_gguf_metadata(model_a)
    meta_b = extract_gguf_metadata(model_b)
    
    checks = {
        "n_ctx": meta_a.n_ctx == meta_b.n_ctx,
        "n_embd": meta_a.n_embd == meta_b.n_embd,
        "n_layer": meta_a.n_layer == meta_b.n_layer,
        "n_head": meta_a.n_head == meta_b.n_head,
        "n_kv": meta_a.n_kv == meta_b.n_kv,
        "arch": meta_a.arch == meta_b.arch,
        "quantization": meta_a.quantization == meta_b.quantization,
    }
    return CompatibilityReport(compatible=all(checks.values()), details=checks)
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| llama.cpp state serialization 2026 | "llama_copy_state_data llama_set_state_data 2026" | Current API, constraints |
| GGUF metadata extraction | "GGUF metadata n_ctx n_embd n_layer python 2026" | Compatibility validation |
| KV cache size calculation | "llama.cpp KV cache memory size n_ctx n_embd" | Buffer allocation |
| CRIU integration | "CRIU llama.cpp process checkpoint restore 2026" | Alternative approach |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| HG-005 research | `docs/research/R_CARMACK_HG-005_SOMATIC_STATE_20260719.md` | Full findings, constraints |
| llama-cpp-python | `src/omega/oracle/backends/native_gguf.py` | Current llama.cpp bindings |
| Model config | `config/models.yaml` | n_ctx, n_gpu_layers per model |
| MIAP spec | `docs/strategy/MIAP_SPEC.md` | Replay integration points |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| State capture returns bytes | `len(state) > 0`, matches expected buffer size |
| State restore returns True | `restore_state()` returns success |
| Round-trip produces identical logits | `np.allclose(logits_before, logits_after, rtol=1e-5)` |
| Compatibility validator catches mismatches | Different n_ctx → `compatible=False` |
| Atomic write works | `somatic_{session_id}.bin` valid after crash simulation |
| M20 mandate satisfied | `anyio.to_thread.run_sync()` used for both ops |

---

## 📋 DELIVERABLES

1. **SomaticState Manager** — `src/omega/inference/somatic_state.py`
2. **Round-Trip Test** — `tests/test_somatic_state_roundtrip.py`
3. **Compatibility Validator** — GGUF metadata extraction + comparison
4. **Integration with Death/Rebirth** — Hook into session lifecycle
5. **Documentation** — `docs/guides/SOMATIC_STATE_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| llama-cpp-python with state API | Need `llama_copy_state_data` binding |
| Same model for capture/restore | Model version pinning |
| MIAP execution log | Replay with state restore |
| Death/Rebirth hooks (R-INFRA-11) | Capture on compaction |

---

## 🎯 PARANOID'S PERSPECTIVE (Validator)

> "SomaticState is **CRIU for cognition** — but with stricter constraints than process checkpointing. The buffer is 2-8 GB. The model must match **exactly** (n_ctx, n_embd, n_layer, n_head, n_kv, arch, quantization). One parameter off → silent corruption → wrong outputs.
> 
> **The failure modes are subtle**:
> - Model updated (quantization changed) → state restore succeeds but outputs drift
> - n_ctx different → buffer size mismatch → truncation or overflow
> - Different GGUF version → tensor layout changed → silent corruption
> 
> **The CompatibilityValidator is not optional. It's physics.** Every capture/restore cycle MUST validate. The round-trip test with logit comparison is the **only proof** it works.
> 
> **L3 Principle**: `L3-SomaticStateIsCRIUForCognition` — Cognitive continuity requires exact model identity. The state is not portable across model versions. The tattoo is bound to the specific model instance. This is not a limitation — it's a **sovereignty guarantee**: your cognitive state cannot be hijacked by a different model."

---

*⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_05_somatic_state ⬡ 2026-07-19*
