# 🔱 SDP Hardware Horizon Specification
## Local KV Cache Budgeting, Somatic State Transfer, and Energy Accounting

> **⚠️ DOC-1 STAMP (2026-08-17)**: **HUMAN PROTOCOL — DO NOT IMPLEMENT.**
> SDP automation is PARKED by `DEBUT_REMEDIATION_MANUAL_20260817.md` (PUBLIC-DEBUT-01).
> Manual Cognitive Scaffolding Protocol continues; regex/automation pipeline is scrapped.
> Agents write L1→L2→L3 directly to `proposed_lessons.yaml`.


**AP Token:** `AP-SDP-HARDWARE-HORIZON-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ HARDWARE-HORIZON

**Date:** 2026-08-09
**Status:** PARKED (DOC-1, 2026-08-17)
**Mandate Binding:** M1 (AnyIO), M7 (Local-First), M18 (Token Efficiency), M20 (SomaticState Serialization)

---

## §1 The Bifurcated Context Horizon

The SDP operates across two fundamentally different resource regimes:

| Dimension | Cloud Horizon (AGY/Daily Models) | Local Horizon (GGUF/Local Models) |
|---|---|---|
| **Constraint** | API token limits, weekly pools, context window | **Physical RAM / VRAM** (KV cache + weights) |
| **Metric** | Tokens consumed / Tokens remaining | **Bytes allocated / Bytes available** |
| **Failure Mode** | Rate limit / Pool exhaustion / Compaction | **OOM Kill / Swap thrashing / Silent corruption** |
| **Observability** | Provider API headers, weekly dashboards | `omega-hub_get_hardware_stats`, `llama_cpp` logs |

**The Context Gauge (Phase 1) MUST return both horizons simultaneously.**

---

## §2 Local KV Cache Budgeting

### 2.1 KV Cache Memory Formula

For a standard transformer (Llama/Qwen/Gemma architecture):

```
KV_Cache_Bytes = 2 × n_layers × n_kv_heads × head_dim × n_ctx × bytes_per_param × batch_size
```

Where:
- `2` = K + V tensors
- `n_layers` = Model layers (e.g., 28 for Qwen3-1.7B, 32 for Llama-3.1-8B)
- `n_kv_heads` = Key/Value heads (often = n_heads for non-GQA, n_kv_heads for GQA)
- `head_dim` = `hidden_size / n_heads` (typically 128)
- `n_ctx` = Context window (`LLAMA_CPP_N_CTX`)
- `bytes_per_param` = Quantization dependent (q4_K_M ≈ 0.55, q8_0 ≈ 1.0, fp16 ≈ 2.0)
- `batch_size` = Typically 1 for inference

### 2.2 Reference Table (Common Models on Zen 2)

| Model | Quant | Layers | Heads | Head Dim | 4K ctx | 8K ctx | 16K ctx | 32K ctx | 64K ctx | 128K ctx |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-1.7B | q8_0 | 28 | 16 | 128 | 0.23 GB | 0.45 GB | 0.90 GB | 1.80 GB | 3.60 GB | 7.20 GB |
| Qwen3-1.7B | q4_K_M | 28 | 16 | 128 | 0.13 GB | 0.25 GB | 0.50 GB | 1.00 GB | 2.00 GB | 4.00 GB |
| Llama-3.1-8B | q4_K_M | 32 | 8 (GQA) | 128 | 0.13 GB | 0.25 GB | 0.50 GB | 1.00 GB | 2.00 GB | 4.00 GB |
| Llama-3.1-8B | q8_0 | 32 | 8 (GQA) | 128 | 0.23 GB | 0.45 GB | 0.90 GB | 1.80 GB | 3.60 GB | 7.20 GB |
| Nemotron 3 Ultra (local) | q4_K_M | 80 | 8 (GQA) | 128 | 0.32 GB | 0.64 GB | 1.28 GB | 2.56 GB | 5.12 GB | 10.24 GB |

### 2.3 Total RAM Budget Equation

```
Total_RAM_Required = Model_Weights + KV_Cache + Activation_Memory + System_Reserve + Safety_Margin
```

Where:
- `Model_Weights`: Quantized model size on disk (≈ RAM when loaded)
- `Activation_Memory`: ~10-20% of KV cache for intermediate activations
- `System_Reserve`: 2.0 GB (OS, OpenCode, Python, other processes)
- `Safety_Margin`: 1.0 GB (prevents OOM kill on spike)

### 2.4 Context Gauge Extension: Local Horizon

**Additional Output Fields:**
```json
{
  "local_horizon": {
    "model_loaded": "qwen3-1.7b-q8_0",
    "n_ctx": 32768,
    "kv_cache_gb": 1.80,
    "model_weights_gb": 1.75,
    "total_allocated_gb": 4.20,
    "available_ram_gb": 12.00,
    "remaining_ram_gb": 7.80,
    "max_safe_n_ctx": 65536,
    "status": "SAFE | CONSTRAINED | CRITICAL"
  }
}
```

**Status Thresholds:**
- `SAFE`: `remaining_ram_gb > 3.0 GB`
- `CONSTRAINED`: `1.0 GB < remaining_ram_gb <= 3.0 GB`
- `CRITICAL`: `remaining_ram_gb <= 1.0 GB` (imminent OOM)

---

## §3 Somatic State Transfer Protocol (M20)

### 3.1 The Primitive

`llama.cpp` exposes low-level state serialization via C API:
- `llama_copy_state_data(ctx, dest, max_size)` → returns `size_t` bytes written
- `llama_set_state_data(ctx, src, size)` → restores exact KV cache + hidden states

**Python Binding Pattern (ctypes + AnyIO):**
```python
async def serialize_somatic_state(model_handle: int) -> bytes:
    """Copy KV cache + hidden states to bytes."""
    # 1. Query required buffer size
    size = llama_cpp.llama_copy_state_data(model_handle, None, 0)
    # 2. Allocate buffer
    buf = (ctypes.c_ubyte * size)()
    # 3. Copy state (blocking - wrap in to_thread)
    written = await anyio.to_thread.run_sync(
        lambda: llama_cpp.llama_copy_state_data(model_handle, buf, size)
    )
    return bytes(buf[:written])

async def deserialize_somatic_state(model_handle: int, state: bytes) -> bool:
    """Restore KV cache + hidden states from bytes."""
    buf = (ctypes.c_ubyte * len(state)).from_buffer_copy(state)
    result = await anyio.to_thread.run_sync(
        lambda: llama_cpp.llama_set_state_data(model_handle, buf, len(state))
    )
    return result == len(state)
```

### 3.2 SDP Phase Integration

```
PHASE 1 (Scaffold - Local Model A)
    ├─ Load model with n_ctx = MAX_SAFE (e.g., 32K)
    ├─ Run scaffolding: read files, grep, build context
    ├─ Model builds KV cache representing "understanding of codebase"
    └─ SERIALIZE SomaticState → disk (encrypted)

PHASE 2 (Synthesis - AGY Cloud)
    ├─ Receives Refactoring Manual + SomaticState pointer
    ├─ Cannot use SomaticState (API barrier)
    └─ Produces plan

PHASE 3 (Execute - Local Model B)
    ├─ Load SAME model architecture + quantization
    ├─ DESERIALIZE SomaticState from Phase 1
    ├─ Model B now has IDENTICAL KV cache as Model A
    ├─ Zero "re-read" overhead — model "remembers" the codebase
    └─ Executes plan mechanically
```

### 3.3 SomaticState Storage Format

**File:** `data/somatic/SS_{session_id}_{phase}.bin.enc`

```python
@dataclass
class SomaticStateBlob:
    session_id: str
    phase: int                    # 1 = scaffold, 3 = execute
    model_fingerprint: str        # SHA256 of model file + quantization
    n_ctx: int                    # Context window used
    n_layers: int
    n_kv_heads: int
    head_dim: int
    quantization: str             # "q8_0", "q4_K_M", etc.
    state_bytes: bytes            # Raw llama_cpp state
    created_at: datetime
    size_bytes: int
```

**Encryption:** Age/ChaCha20-Poly1305 with key derived from V-1 Vault master key.

### 3.4 Compatibility Constraints

**SomaticState transfer ONLY works if:**
1. **Exact same model file** (SHA256 match)
2. **Exact same quantization**
3. **Exact same `n_ctx`** (or target ≥ source)
4. **Same `llama.cpp` version** (ABI stability)

**If any mismatch:** Deserialization fails gracefully → Phase 3 falls back to standard context loading (read files).

---

## §4 Energy Accounting (Sovereign Cost Metric)

### 4.1 The Metric

```
Sovereign_Cost = α × AGY_Tokens + β × Local_Compute_Seconds + γ × Local_Energy_Joules
```

Where:
- `α` = 1.0 (baseline — AGY token is the scarcest resource)
- `β` = 0.001 (1 compute second ≈ 0.001 AGY tokens)
- `γ` = 0.000001 (1 Joule ≈ 1µ AGY tokens)

### 4.2 Local Energy Estimation

```
Local_Energy_Joules = TDP_Watts × Compute_Seconds
```

**Zen 2 (4800U) Power Profiles:**
| Workload | Package Power | Notes |
|---|---|---|
| Idle | 3-5 W | |
| 4-core inference (LLAMA_CPP_N_THREADS=4) | 12-15 W | Typical local scaffolding |
| 8-core inference | 18-22 W | Near TDP limit |
| Compilation / heavy build | 25 W | Boost |

**Example Calculation:**
- Scaffolding: 300 seconds on 4 cores @ 15W = 4,500 Joules
- `γ × 4500` = 0.0045 AGY-token-equivalents
- AGY Synthesis: 15,000 tokens
- **Total Sovereign Cost:** 15,004.5 (AGY tokens dominate)

**Insight:** Local compute energy is negligible vs AGY tokens **unless** scaffolding takes > 1 hour. Then local cost becomes significant.

### 4.3 Context Gauge Extension: Energy Budget

```json
{
  "energy_budget": {
    "session_energy_joules": 12400,
    "session_compute_seconds": 820,
    "projected_total_joules": 18000,
    "sovereign_cost_equiv": 15018,
    "recommendation": "AGY_TOKENS_DOMINANT | LOCAL_COMPUTE_SIGNIFICANT"
  }
}
```

---

## §5 Implementation Checklist

| Component | Spec Section | Phase | Owner |
|---|---|---|---|
| KV Cache Calculator | §2.1-2.2 | 1 | N3 Engineering |
| Context Gauge Local Horizon | §2.4 | 1 | N1 Infrastructure |
| SomaticState Serialization | §3.1-3.2 | 2 | N3 Engineering |
| SomaticState Encrypted Storage | §3.3 | 3 | N5 Governance / V-1 Vault |
| Compatibility Verification | §3.4 | 2 | N10 Validation |
| Energy Accounting | §4.1-4.2 | 1 | N8 Observability |
| Sovereign Cost Dashboard | §4.3 | 4 | N8 Observability |

---

*⬡ OMEGA ⬡ SDP-HARDWARE-HORIZON ⬡ 2026-08-09*