# 🔱 Strategic Roadmap: Session-End Orchestration & Soul Distillation Pivot
**AP Token**: `AP-STRATEGY-SESSION-END-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_strategy ⬡ ACTIVE
**Date**: 2026-07-30

---

## 1. Executive Summary: The "Carmack Pivot"

Extensive research into the Omega Engine's session lifecycle, MemoryStore, and Soul Distillation pipelines revealed a state of "Distillation Theater." The system possessed a beautiful philosophical architecture (L1→L2→L3) but lacked the mechanical wiring to execute it. The `approved_lessons.yaml` files across all entities are completely empty.

Applying the "Unoverengineering" (Carmack) philosophy, this roadmap outlines a pivot away from maintaining a complex, buggy, 5-layer custom `MemoryStore` for raw transcripts, and away from brittle regex-based text extraction. 

**The New Paradigm:** We will utilize OpenCode's native, WAL-enabled SQLite database as the absolute Single Source of Truth (SSOT) for conversation history, and we will use actual Local LLM inference to perform semantic soul distillation.

---

## 2. The Hard Truths (Research Findings)

### 2.1 The Distillation Theater
*   **The Scribe Distiller is Trivial:** The current `session_end.py` hook uses the Scribe distiller, which performs mechanical text-truncation (e.g., prefixing text with `"Pattern observed:"`) rather than semantic analysis.
*   **The Oracle Distiller is Dead Code:** The feature-rich Oracle distiller (with 12+ regex patterns and quality gates) is never called by the session-end hook.
*   **Zero Approval Rate:** Because the pipeline was broken and the output was trivial, no automated proposal has ever passed the staging gate into `approved_lessons.yaml`.

### 2.2 The MemoryStore Overengineering
*   **The Batch Writer is Never Started:** `BatchPersistenceWriter.start()` is never called. All writes fall back to a synchronous, direct-write path.
*   **Redundant Storage:** Omega attempts to store raw transcripts in Redis, USM, and File systems, duplicating data that OpenCode already perfectly persists in `~/.local/share/opencode/opencode.db`.
*   **The Flush Bug:** The `flush()` method on the batch writer is a no-op, meaning read-your-writes consistency was purely accidental.

### 2.3 The Env Var Gap
*   The `wrapper.sh` script successfully catches all process exits (normal, crash, kill), but it fails to pass `OPENCODE_ENTITY` or `OPENCODE_SESSION_ID` to the Python hook, causing distillation to be skipped 100% of the time in normal usage.

---

## 3. The Strategic Pivot

### 3.1 SQLite as the Transcript SSOT
We will cease attempting to duplicate raw conversation transcripts in Omega's `MemoryStore`. OpenCode's SQLite database is robust, WAL-enabled, and crash-safe. Omega's storage will be reserved strictly for extracted, high-value gnosis (Vector indexes, `soul.yaml`, `proposed_lessons.yaml`).

### 3.2 Native Tooling over Third-Party Dependencies
We evaluated community tools like `opencode-db` and `opencode-session-toolkit`. To minimize supply-chain risk and deployment friction, we reject adding third-party Python CLI wrappers. 
*   **Resolution:** We will use the native `opencode db "SQL"` command to fetch session metadata, and the native `opencode export <session-id>` command to fetch perfectly formatted JSON transcripts.

### 3.3 LLM-Driven Semantic Distillation
Regex cannot extract universal principles. We will deprecate both the Scribe and Oracle rule-based distillers.
*   **Resolution:** `session_end.py` will pass the exported JSON transcript to the local Provider Fabric (e.g., Qwen, Llama-3) with a strict JSON-schema prompt to semantically extract L1 (Narrative), L2 (Insight), and L3 (Universal Principles).

### 3.4 Session Ownership Model
Sessions frequently ping-pong between agents (e.g., `kali` → `plan` → `makali`). Attempting to distill this into three separate souls creates fragmented memory.
*   **Resolution:** The entity that *started* the session (`session.agent` in the DB) "owns" the session. All insights, including delegated work, are distilled into the owner's soul, preserving narrative continuity.

### 3.5 Agent Memory Expansion via Community Plugin
While we reject third-party CLI wrappers, we **accept** the `opencode-sessions-explorer` plugin.
*   **Resolution:** We will add this to `opencode.json`. It runs *inside* OpenCode, giving agents 18 native tools to search, grep, and recall their own SQLite session history, granting them superhuman memory during active sessions.

---

## 4. Execution Roadmap

### Phase 1: The Wrapper & DB Integration (P0)
*Goal: Ensure `session_end.py` knows exactly what session just ended.*
1.  Modify `.opencode/wrapper.sh` to query `opencode db` for the most recent `id`, `agent`, and `model` immediately after the OpenCode process exits.
2.  Export these as `OPENCODE_SESSION_ID`, `OPENCODE_ENTITY`, and `OPENCODE_MODEL`.

### Phase 2: The Semantic Distillation Pipeline (P0)
*Goal: Replace regex truncation with actual AI reasoning.*
1.  Update `session_end.py` to run `opencode export <session_id>`.
2.  Parse the JSON output to extract the conversation transcript.
3.  Send the transcript to the local LLM via the Provider Fabric to extract L1/L2/L3 lessons.
4.  Write the structured output to `data/entities/<entity>/proposed_lessons.yaml`.

### Phase 3: Agent Memory Expansion (P1)
*Goal: Give agents access to their past.*
1.  Add `opencode-sessions-explorer` to the `plugin` array in `opencode.json`.
2.  Ensure `external_directory` permissions allow access to `~/.local/share/opencode/**`.

### Phase 4: MemoryStore Deprecation (P2 - Tech Debt Cleanup)
*Goal: Remove the overengineered transcript storage.*
1.  Deprecate the `BatchPersistenceWriter`.
2.  Remove `FileStorageProvider` and `RedisStorageProvider`'s responsibilities for storing raw, turn-by-turn transcripts.
3.  Retain `USMStorageProvider` for state and Vector/FTS5 for semantic search of *distilled* gnosis.

---
*Documented by: Gemini 3.1 Pro (Polymathic Council / Architect)*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
