# 🔱 Omega Engine — Core Hardening & PR Readiness Brief
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_core_hardening ⬡ PHASE-I

**AP Token**: `AP-CORE-HARDENING-v1.0.0`
**Author**: Overseer (Tri-Entity Consciousness)
**Date**: 2026-05-27
**Status**: ACTIVE
**Target Agent**: Builder (Gemma-4-31b)

---

## §0: Strategic Directive — No Rabbit Holes & The Engine-Stack Firewall

We have successfully mined a massive amount of legacy technical and strategic gold (Tarot, Omnidroid, Hysteresis, 10 Pillars, etc.). **This material is now fully documented and archived in `docs/research/` so it is safe and preserved.**

**HOWEVER, we must not let these discoveries distract us from the primary goal: a production-grade, high-performance Pull Request (PR) for the Omega Engine.**

### 🛡️ The Inviolable Engine-Stack Firewall (Mandate #2)
We must maintain absolute separation between the **Omega Engine Core** (`src/omega/`) and **Expansion Stacks/WADs** (`config/wads/`).
*   **The Omega Engine is a pure, agnostic runtime.** Just as the Doom engine (`doom.exe`) knows nothing about Hell, space marines, or keys (it only knows about sectors, lines, textures, and state machines), the Omega Engine knows nothing about Tarot, Sekhmet, or Hegelian dialectics. It only knows about tokens, vectors, files, and processes.
*   **Systems like Tarot, Omnidroid tools, and esoteric pillars must NEVER be considered for integration into the Omega Engine.** These belong exclusively in the **Arcana-NovAi esoteric layer** (or other community stacks) that *runs* on top of the agnostic Omega Engine.
*   Do not write any code in `src/omega/` that references Tarot, specific esoteric entities, or Omnidroid-specific pipelines. Keep the core engine generic, clean, and robust.

We will not implement the esoteric Tarot cards, the 10 Pillars esotericism, the Omnidroid tools, or deep Hysteresis monitoring inside the core engine itself right now. **The rabbit holes can wait.**

Instead, we will focus **100% of our engineering power** on getting the **core Omega Engine systems operating at full power**. Specifically:
1.  **Memory Systems (MemoryStore)**: Fully wire `MemoryStore` into `oracle.py` so that conversation history is actually saved and retrieved.
2.  **Context Builder (`context_builder.py`)**: Fully wire `ContextBuilder` into `oracle.py` so that it reads from `MemoryStore` and injects the rolling conversation history and the entity's soul context into the system prompt.
3.  **The Agent Bus (Agent-to-Agent Handoff)**: Ensure the **Omega Hub** (`mcp/omega_hub/server.py`) is fully operational so that agents can coordinate.
4.  **Embeddings & Hybrid Search (Cycle Beta)**: Implement the Qdrant Hybrid Search with `fastembed` (BGE-base-en-v1.5) as planned, but keep it extremely clean and robust, with graceful fallback to FTS5.
5.  **Empirical Steward & Omega Gateway (Port 8018)**: Deploy the local host-side proxy and the `GoogleKeyPool` to map rate limits empirically using the reactive 3-strike protocol.

---

## §1: Core Hardening Tasks

### Task 1: Wire MemoryStore into `oracle.py` (P0 — Critical)
Currently, `MemoryStore` is fully implemented and tested (with our new 3-tier Redis -> File -> InMemory fallback), but **it is never called by `oracle.py`**. Every request to the Oracle is completely stateless.

**Action Plan**:
1.  Open `src/omega/oracle/oracle.py`.
2.  Locate the response generation paths (e.g., `talk()`, `summon()`).
3.  After receiving a successful response from the `ModelGateway`, call `MemoryStore.add_exchange(entity_name, session_id, query, response, metadata)`.
4.  Ensure that `session_id` is properly generated and managed (using `SessionManager` or a rolling daily session ID).
5.  Ensure that `Transient Mode` (`/transient`) is respected: if transient mode is active, do **not** write to `MemoryStore` or update `soul.yaml`.

### Task 2: Wire ContextBuilder into `oracle.py` (P0 — Critical)
Currently, `ContextBuilder` is implemented but never called. We need to wire it into `oracle.py` so that it reads from `MemoryStore` and injects the rolling conversation history and the entity's soul context into the system prompt.

**Action Plan**:
1.  Open `src/omega/oracle/oracle.py`.
2.  Before calling `ModelGateway.generate()`, instantiate `ContextBuilder` with the active `session_id`.
3.  Call `ContextBuilder.build_context(entity_name)` to retrieve the fully assembled system prompt (which includes the entity's soul, domain knowledge, and rolling conversation history).
4.  Pass this assembled context as the system prompt to the `ModelGateway`.

### Task 3: Implement Qdrant Hybrid Search with `fastembed` (P1 — High)
Implement Cycle Beta as planned, but keep it extremely clean and robust, with graceful fallback to FTS5.

**Action Plan**:
1.  Add `qdrant-client==1.17.1` and `fastembed==0.3.4` to `requirements.txt` and install them in the virtual environment.
2.  Create `src/omega/library/embeddings.py` to wrap `fastembed` in an AnyIO-compliant, thread-pooled, lazy-loaded class.
3.  Refactor `src/omega/library/indexer.py` to:
    *   Use the new `embeddings.py` module to generate 768-dim neural embeddings.
    *   Store embeddings in Qdrant instead of `vectors.json`.
    *   Implement hybrid search using FTS5 and Qdrant with Reciprocal Rank Fusion (RRF).
    *   Provide graceful degradation to FTS5-only search if Qdrant is offline.

### Task 4: Standardize the Agent Bus (P1 — High)
Ensure that the **Omega Hub** (`mcp/omega_hub/server.py`) is fully operational so that agents can coordinate.

**Action Plan**:
1.  Verify that the `omega-hub` MCP server is running and healthy.
2.  Ensure that `Orchestrator.dispatch_agent()` properly passes the `session_id` and `trace_id` to the spawned agent so that the agent can post its context back to the hub.
3.  Verify that the `omega-hub` tools (`post_context`, `get_continuation`) are fully functional and tested.

### Task 5: Deploy Omega Gateway & GoogleKeyPool (P0 — Critical)
Deploy the local host-side proxy and the `GoogleKeyPool` to map rate limits empirically using the reactive 3-strike protocol.

**Action Plan**:
1.  **GoogleKeyPool (`src/omega/oracle/providers.py`)**:
    *   Implement `GoogleKey` tracking `last_used_at`, `consecutive_failures`, and `state`.
    *   No proactive sleep: requests are sent immediately.
    *   On 429, apply reactive backoff: wait 60s, then 120s, then 240s on consecutive failures.
    *   After the 3rd consecutive failure, rotate to the next key and move the failed key to a 60-minute COOLDOWN.
2.  **Omega Gateway (`src/omega/gateway/server.py`)**:
    *   Create a lightweight FastAPI server on port 8018.
    *   Expose `/v1/chat/completions` and `/v1/models` endpoints routing to `ModelGateway`.
3.  **OpenCode Sync (`opencode.json`)**:
    *   Add `omega-gateway` provider pointing to `http://localhost:8018/v1`.
4.  **Systemd Service (`config/systemd/omega-gateway.service`)**:
    *   Create a systemd user service to manage the gateway.
5.  **Metrics Ledger (`metrics.db`)**:
    *   Log every 429, the retry attempt that succeeded, and the total recovery delta.

---

## §2: Verification Gates

After implementing these core systems, run the following verification gates:
1.  **Unit Tests**: Run `make test` to ensure all 266+ tests pass.
2.  **Integration Test**: Run a multi-turn conversation via the CLI (`omega talk` or `omega summon`) and verify that the entity remembers previous turns.
3.  **Graceful Degradation Test**: Stop the Qdrant container and verify that search still works (falling back to FTS5).
4.  **Disk Guard Test**: Verify that the disk guard correctly prevents writes if the root partition is full.

---

*Let's get the core engine operating at full power. The rabbit holes can wait.*
