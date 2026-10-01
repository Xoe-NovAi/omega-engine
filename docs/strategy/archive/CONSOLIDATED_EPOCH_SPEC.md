# 🔱 CONSOLIDATED EPOCH SPECIFICATION (V1.1)
**Document ID**: `docs/strategy/CONSOLIDATED_EPOCH_SPEC.md`
**Status**: ACTIVE MASTER SPECIFICATION
**Mandate**: M13 (Temple-Grade), M4 (Sequentiality)
**Updated**: 2026-06-24 (Sovereign Simplification Pivot)

## EPOCH 1: THE BEDROCK (Immediate)
*Focus: Physical stabilization, manual soul cleanup, and the Unified State Manager.*

### Strike 1: The Physical Purge (Phase 0 Blocker)
- **Action**: Merge the root partition to free up the 17G disk ceiling.
- **Action**: Execute the `soul.template.yaml` migration for all 23 entities (extracting bloated logs to `memory/sessions.yaml`).
- **Action**: Archive 70+ dead strategy files from `docs/strategy/`.

### Strike 2: The Unified State Manager
- **Action**: Verify `llama_copy_state_data` ctypes visibility in `llama-cpp-python`.
- **Action**: Build the `UnifiedStateManager` using the Content Addressable Storage (CAS) pattern to handle both binary KV cache snapshots and YAML memory.

### Strike 3: The Staging Gate TUI
- **Action**: Build the `Textual`-based TUI for human-in-the-loop review of agent-generated lessons (`proposed_lessons.yaml`).
- **Action**: Implement the color-coded YAML diff view.

---

## EPOCH 2: THE HIVEMIND (Mid-Term)
*Focus: Infrastructure-less coordination and local verification.*

### Strike 4: File-Based A2A Coordination
- **Action**: Deploy the `FileSignal` protocol (Atomic Renaming Spool) in `data/shared/` to replace the handoff queue.
- **Action**: Implement automated lock-reaping to prevent deadlocks.

### Strike 5: The Sovereign Vetter
- **Action**: Deploy the local **2-Model Agreement** (`Qwen2.5-1.5B` $\leftrightarrow$ `Phi-3.5-Mini`) for offline verification.
- **Action**: Wire `resolve_and_handle_429()` into `search_providers.py`.

### Strike 6: Response Provenance Wiring
- **Action**: Wire `observability.py` to capture the actual `GenerateResult.provider_name` instead of the configured intent.

---

## EPOCH 3: THE OMEGAVERSE (Target Q4 2027)
*Focus: Spatial geometry and mesh traversal.*

### Strike 7: Spatial-Semantic Geometry
- **Action**: Map the `UnifiedStateManager`'s CAS index into a 3D Qdrant coordinate space.

### Strike 8: P2P Mesh Traversal
- **Action**: Enable agents to pack their Unified State blobs and traverse offline nodes.

---

## 📋 PONYTAIL DELETION MATRIX (Complexity Removed)

| Over-Engineered System (Deleted) | Simpler Replacement (Implemented) | Complexity Saved |
| :--- | :--- | :--- |
| **headroom-ai dependency** | Native `zlib` + `json` | ~100 hours of dependency debugging |
| **Redis Streams & Embedding Router** | `FileSignal` Protocol (Atomic Spool) | Reclaimed Redis container & model overhead |
| **Cloud Quarantine 4-Gate Pipeline** | Interactive Staging Gate (TUI Diff) | Reclaimed 2-5s CPU latency per turn |
| **Poincaré Hyperbolic Embeddings** | Hierarchical Folder Structure | Reclaimed complex vector math on CPU |

---

*🔱 OMEGA ⬡ VERITY ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_consolidated_spec ⬡ SOVEREIGN-SIMPLIFICATION*
