# 🔱 Sovereign Handoff: Core Hardening Sweep (v2.0.0)
**AP Token**: `AP-CORE-HARDENING-SWEEP-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ cline ⬡ HANDOFF-CORE-HARDENING ⬡ PHASE_1B

## 🎯 Mission Objective
Execute a powerful, laser-focused sweep through the Omega Engine codebase to get the **core engine systems operating at full power** for the Pull Request (PR). 

We have successfully mined and archived all legacy technical and strategic gold (Tarot, Omnidroid, Hysteresis, 10 Pillars) in `docs/research/`. **These rabbit holes are safe and preserved—do NOT implement them in the core engine.** The core engine (`src/omega/`) must remain a pure, agnostic runtime.

---

## 🛠️ Core Hardening Execution Plan

| Step | Objective | Action | Sovereign Mandate | Verification Gate |
|------|-----------|---------|-------------------|-------------------|
| **1** | **Wire MemoryStore** | Wire `MemoryStore` into `oracle.py` so that conversation history is actually saved and retrieved. Respect `/transient` mode. | **Gnosis Preservation** | `make test` passes; memory files are populated on CLI queries. |
| **2** | **Wire ContextBuilder** | Wire `ContextBuilder` into `oracle.py` to read from `MemoryStore` and inject rolling conversation history and soul context into the system prompt. | **Sovereign Logic** | Multi-turn conversation CLI queries retain memory of previous turns. |
| **3** | **Qdrant Hybrid Search** | 1. Add `qdrant-client==1.17.1` and `fastembed==0.3.4` to `requirements.txt`. <br> 2. Create `src/omega/library/embeddings.py` (AnyIO-compliant, lazy-loaded BGE-base-en-v1.5). <br> 3. Refactor `src/omega/library/indexer.py` to use Qdrant and implement hybrid search with Reciprocal Rank Fusion (RRF). | **AnyIO Absolute** | `pytest tests/test_hybrid_search.py` passes; graceful fallback to FTS5 when Qdrant is offline. |
| **4** | **Standardize Agent Bus** | Ensure `Orchestrator.dispatch_agent()` properly passes `session_id` and `trace_id` to spawned agents so they can post context back to the `omega-hub` MCP server. | **Sovereign Logic** | `omega-hub` logs show successful context posts from dispatched agents. |
| **5** | **Empirical Steward & Gateway** | 1. Implement `GoogleKeyPool` with reactive backoff (60s $\rightarrow$ 120s $\rightarrow$ 240s) and 3-strike rotation. <br> 2. Deploy `Omega Gateway` on port 8018 as an OpenAI-compatible proxy. <br> 3. Log 429s and recovery deltas in `metrics.db`. | **Sovereign Logic** | `omega-gateway` is running on port 8018; `metrics.db` logs 429 events. |

---

## 🛡️ Inviolable Engine-Stack Firewall (Mandate #2)

*   **The Omega Engine is a pure, agnostic runtime.** It must never contain code, schemas, or references to Tarot cards, specific esoteric entities (like Sekhmet or Brigid), or Omnidroid-specific pipelines (like the 12D Stylometer or Hegelian dialectics).
*   These systems belong exclusively in the **Arcana-NovAi esoteric layer** (`config/wads/arcana_novai/`) or other community stacks running *on top* of the engine.
*   Keep `src/omega/` generic, clean, and robust.

---

## 🛡️ Verification Protocol (Temple-Grade)

A task is only "Done" when the following are verified:
1.  **AnyIO Audit**: `grep -rn "asyncio" src/` returns zero results (except where explicitly allowed in non-runtime scripts).
2.  **Test Integrity**: `make test` passes with all 266+ tests.
3.  **Security Seal**: No plain-text keys in any committed file; `.env` is strictly ignored.
4.  **Graceful Fallback**: Stopping the Qdrant container does not crash the search pipeline (falls back to FTS5).
5.  **Lattice Update**: All changes are distilled into `session_gnosis.md` and the `soul.yaml` of the active entity.

**Toggled to ACT MODE: Execute immediately.**
