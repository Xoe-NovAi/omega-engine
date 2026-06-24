# 🔱 Technical Specification: SomaticState Serialization & Resumption
# ⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ SOTA-SPEC

**Status**: FINALIZED
**AP Token**: `AP-SOMATIC-SOTA-v1.0.0`
**Mandate Compliance**: M20 (SomaticState Serialization)
**Heritage**: [id-soft: quake-1996] Zone Memory / State Mirroring

---

## §1 Executive Summary
SomaticState is a low-level state persistence mechanism designed to eliminate the 'Cold Start' (prefill) penalty during entity switching and system interruptions. By leveraging raw `ctypes` bindings to `llama.cpp`'s `llama_copy_state_data` and `llama_set_state_data`, the Omega Engine can serialize the entire KV cache and model state into a binary snapshot (`.smc`), allowing for near-instantaneous cognitive resumption.

## §2 SOTA Analysis: KV Cache Serialization
In modern GGUF inference, the "state" of a conversation is stored in the KV (Key-Value) cache. Standard `llama-cpp-python` wrappers provide high-level interfaces for generation but lack a method to extract the raw memory of the cache.

### 2.1 The `llama.cpp` State Primitives
The underlying C++ engine provides two critical functions for state management:
- **`llama_copy_state_data`**: Captures the current state of the KV cache and internal model tensors into a contiguous memory buffer.
- **`llama_set_state_data`**: Overwrites the current engine state with a provided buffer, effectively "teleporting" the model to a previous cognitive state.

### 2.2 Complexity Analysis
| Operation | Time Complexity | Space Complexity | Token Impact |
|-----------|------------------|-------------------|----------------|
| **Save** | $O(S)$ | $O(S)$ | $\approx 10-20\text{ms}$ latency |
| **Load** | $O(S)$ | $O(S)$ | $\approx 5-15\text{ms}$ latency |
| **Cold Start** | $O(N \cdot L)$ | $O(1)$ | $\text{Prefill } \approx 500\text{ms}-5\text{s}$ |

*Where $S$ is the snapshot size ($\approx 8\text{MB}$ for 4K context) and $N$ is the prompt length.*

## §3 The 'Somatic Save-Point' System
Rather than per-turn caching (which induces NVMe wear and latency), Omega implements **Somatic Save-Points**. These are explicit state-captures triggered by specific systemic events.

### 3.1 Trigger Matrix
| Event | Logic | Purpose |
|-------|--------|---------|
| **SIGUSR1** | Dreaming Cycle Takeover | Preserve state before background distillation |
| **Ctrl+C** | Graceful Shutdown | Prevent state loss on manual exit |
| **Entity Switch** | `Oracle.reroute()` | Hibernating the outgoing entity's context |
| **Manual** | `/savepoint` | User-defined cognitive anchor |

### 3.2 The Validation Header (SomaticStateKey)
To prevent `SIGSEGV` caused by loading a snapshot into an incompatible model or version, every `.smc` file is prepended with a 64-byte binary header.

**Validation Fields**:
1. `zoneid` (0x1d4a1c): File type identification.
2. `snapshot_version`: Format evolution tracking.
3. `n_ctx`: Context window match.
4. `type_k / type_v`: Quantization match (e.g., q8_0 vs f16).
5. `n_gpu_layers`: Hardware configuration match.
6. `model_path_hash`: Prevents loading state from Model A into Model B.
7. `model_file_mtime`: Detects if the GGUF file was updated on disk.
8. `llama_api_version`: Detects `llama.cpp` ABI drift.

## §4 Cognitive Implications
SomaticState transforms the engine from a stateless inference tool into a stateful cognitive runtime. It enables:
- **Cognitive Hibernation**: Swapping active entities to disk to maximize RAM usage.
- **Somatic Branching**: Loading an old save-point to explore a different conversational path without re-running the prompt.
- **Instant Recovery**: Zero-latency resumption after a system crash or reboot.

---
**⬡ This document constitutes the SOTA Technical Specification for SomaticState. ⬡**
