<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Unified State Manager (USM) Design Specification
**AP Token**: `AP-USM-DESIGN-v1.0.0`
**Status**: PROPOSED
**Epoch**: I (Strike 2)

## 1. Vision
The Omega Engine currently suffers from "State Fragmentation." Memory is in SQLite/Redis/JSON, sessions are in `.active` files, and somatic states (KV caches) are binary blobs. This fragmentation prevents atomic snapshots, efficient deduplication, and reliable A2A handoffs.

The **Unified State Manager (USM)** transforms the engine from a collection of fragmented stores into a **Content Addressable Storage (CAS)** system. In USM, state is not "stored in a file"; it is "addressed by its hash."

## 2. Architectural Principles
- **Immutability**: Once a state blob is written to CAS, it is never modified. Updates create new blobs with new hashes.
- **Deduplication**: Identical state across different sessions or entities is stored only once.
- **Sovereignty**: All state remains local. The CAS index is a simple local mapping.
- **Somatic-Aware**: USM treats binary KV caches as first-class citizens, allowing "Somatic Save-Points."

## 3. The CAS Layer (`src/omega/state/cas.py`)
The CAS layer handles the raw storage of blobs.

### 3.1 Blob Storage
- **Storage Path**: `data/state/blobs/{prefix}/{hash}` (where prefix is the first 2 chars of the hash to prevent directory bloat).
- **Addressing**: SHA-256 of the content.
- **Interface**:
    - `put(data: bytes) -> str`: Writes data to disk, returns the hash.
    - `get(hash: str) -> bytes`: Returns the data for a given hash.
    - `exists(hash: str) -> bool`: Checks if a blob exists.
    - `delete(hash: str)`: Reference-counted deletion.

### 3.2 Metadata Index
A lightweight SQLite index (`data/state/index.db`) maps human-readable keys to CAS hashes.
- **Table `state_refs`**: `(key, hash, timestamp, metadata)`
- **Example**: `sessions:test_entity:active` $\rightarrow$ `sha256_abc123...`

## 4. The USM Layer (`src/omega/state/usm.py`)
The USM layer provides high-level APIs for the engine.

### 4.1 Unified APIs
- `save_state(key: str, data: Any) -> str`: Serializes data $\rightarrow$ puts in CAS $\rightarrow$ updates index.
- `load_state(key: str) -> Any`: Looks up hash in index $\rightarrow$ gets from CAS $\rightarrow$ deserializes.
- `snapshot(keys: List[str]) -> str`: Creates a "Manifest" (a list of hashes) and stores it as a new blob. This is the "Somatic Save-Point."

### 4.2 Integration Plan
| Current Component | Old Path | New USM Path |
|-------------------|------------|----------------|
| `MemoryStore` | `data/memory/entities/*.json` | `usm.save_state(f"mem:{entity}:{session}", ...)` |
| `SessionManager` | `data/sessions/*.active` | `usm.save_state(f"session:{entity}:active", ...)` |
| `SoulDistiller` | `data/entities/*/soul.yaml` | `usm.save_state(f"soul:{entity}", ...)` |
| `ModelGateway` | `data/state/kv_caches/*.bin` | `usm.save_state(f"somatic:{model}:{state_id}", ...)` |

## 5. Implementation Roadmap
1. **Phase 1**: Implement `cas.py` (Raw blob storage).
2. **Phase 2**: Implement `usm.py` (Index and high-level API).
3. **Phase 3**: Migrate `SessionManager` (Lowest risk).
4. **Phase 4**: Migrate `SoulDistiller` and `MemoryStore`.
5. **Phase 5**: Integrate `SomaticState` (KV caches).

## 6. Mandate Compliance
- **M1 (AnyIO)**: All USM I/O wrapped in `anyio.to_thread.run_sync`.
- **M9 (Error Integrity)**: Custom `USMError` types; no bare `except`.
- **M16 (Modularization)**: USM is a standalone module in `src/omega/state/`.
- **M20 (SomaticState)**: USM provides the backbone for binary state serialization.
