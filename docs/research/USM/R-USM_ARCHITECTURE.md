# 🔱 Unified State Manager (USM) Architecture Spec
# AP: AP-USM-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_usm_spec ⬡ ARCHITECTURE

## 1. Objective
Replace fragmented state management (SQLite for memory, YAML for sessions, binary for KV cache) with a unified, Content Addressable Storage (CAS) interface. This enables high-fidelity "Freeze/Resume" capabilities for LLM cognitive states (SomaticState) and ensures data immutability.

## 2. The CAS Pattern (Content Addressable Storage)
Instead of mapping state to a filename (e.g., `session_123.json`), the USM maps state to the hash of its content.

**Workflow**:
1. **Freeze**: `Data` $\rightarrow$ `SHA256(Data)` $\rightarrow$ `Save to data/somatic/blobs/<hash>.bin`
2. **Resume**: `Hash` $\rightarrow$ `Load from data/somatic/blobs/<hash>.bin` $\rightarrow$ `Data`

**Benefits**:
- **Deduplication**: Identical states across different sessions share the same blob.
- **Immutability**: Blobs are never edited, only created.
- **Integrity**: The hash serves as a built-in checksum.

## 3. Component Design

### 3.1 `CASBlobStore`
The low-level I/O layer.
- **Path**: `data/somatic/blobs/`
- **Methods**:
    - `put(data: bytes) -> str`: Writes data to a `.tmp` file, then renames to `<hash>.bin`. Returns the hash.
    - `get(hash: str) -> bytes`: Reads the blob.
    - `exists(hash: str) -> bool`: Checks for blob presence.
- **Constraint**: Must use `anyio.to_thread.run_sync` for all file I/O (M1).

### 3.2 `SomaticStateSerializer`
Handles the binary bridge to `llama-cpp-python`.
- **Binding**: Wraps `llama_copy_state_data` and `llama_set_state_data`.
- **Somatic-Check**: Before loading, it verifies:
    - `model_hash`: The model used to create the state must match the current model.
    - `kv_size`: The KV cache size must match.
- **Sovereignty**: Ensures binary states are stored locally (M7).

### 3.3 `UnifiedStateManager`
The high-level orchestrator.
- **Interface**:
    - `snapshot(entity_id: str) -> str`: Captures current memory, session, and KV cache $\rightarrow$ returns a master hash.
    - `restore(hash: str)`: Restores all components from the CAS.
- **State Bundle**: A snapshot is a JSON manifest containing hashes for:
    - `memory_blob`
    - `session_blob`
    - `somatic_blob` (binary KV cache)

## 4. Mandate Compliance
- **M1 (AnyIO)**: All I/O wrapped in `run_sync`.
- **M12 (Queue Integrity)**: Atomic renames for all blob writes.
- **M20 (SomaticState)**: Direct C-API bindings for high-fidelity state.
- **M7 (Local-First)**: All blobs stored in `data/somatic/`.

## 5. Verification Plan
1. **Unit Test**: `CASBlobStore` handles collisions and atomic writes.
2. **Integration Test**: `SomaticStateSerializer` can save/load a state without crashing.
3. **End-to-End**: `UnifiedStateManager` can freeze an entity's state, restart the engine, and resume the state perfectly.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_usm_spec | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
