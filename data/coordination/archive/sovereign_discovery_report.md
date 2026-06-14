# 🔱 Sovereign Discovery Report: Architectural Patterns & Ghost Dependencies
**Date**: 2026-06-12
**Trace**: trc_sovereign_discovery_audit
**Status**: DRAFT (for Hivemind review)

## §1 Untapped Architectural Patterns
These patterns are implemented in the codebase but are not formally documented in `OMEGA_ENGINE.md` or `PIVOT_LOG.md`.

### 1.1 The 5-Tier Sovereign Search Protocol (SSP)
Implemented in `src/omega/oracle/sovereign_search_service.py`.
- **Pattern**: A strictly ordered fallback hierarchy for information retrieval.
- **Tiers**:
    - **T0 (Local)**: `.firecrawl/` cache + `MemoryStore` hybrid.
    - **T1 (Broad)**: WebSearch discovery.
    - **T2 (Deep)**: Firecrawl extraction.
    - **T3 (Gnosis)**: Omega Hub (local sovereign knowledge).
    - **T4 (Neural)**: Exa/Tavily neural search.
- **Sovereign Value**: Ensures that the engine always attempts the most sovereign (local) source before escalating to cloud-dependent tiers.

### 1.2 Skeptical Verification Loop
Implemented in `src/omega/oracle/skeptical_verifier.py` and integrated into `SovereignSearchService` and `IterativeResearcher`.
- **Pattern**: A "Zero-Trust" verification layer that treats all synthesized claims as hypotheses until they are corroborated by multiple independent sources (Two-Source Rule).
- **Mechanism**: `SkepticalVerifier.verify()` evaluates a claim against an evidence pool and returns a status (`VERIFIED` | `CONTRADICTED` | `UNVERIFIED`).

### 1.3 Iterative Research Loop (Cognitive Retrieval)
Implemented in `src/omega/oracle/iterative_research.py`.
- **Pattern**: A recursive feedback loop: `Search` $\rightarrow$ `Gap Analysis` $\rightarrow$ `Refinement` $\rightarrow$ `Search`.
- **Mechanism**: Uses a specialized "Sovereign Research Auditor" (Thinking Model) to identify information gaps in gathered evidence and generate refined search queries.

### 1.4 Tainted Data Protocol (TDP)
Implemented in `src/omega/oracle/security.py`.
- **Pattern**: All external data is encapsulated in a `TaintedData` container.
- **Mechanism**: Data remains "tainted" and is subject to the `TDPGate` until it has passed through a verification step (like the Skeptical Verifier). This prevents "prompt injection" or "hallucinated facts" from leaking into the engine's core gnosis.

### 1.5 Sovereign Bridge Adapters
Implemented in `src/omega/bridge/`.
- **Pattern**: Adapter/Bridge pattern used to map external communication protocols (OpenCode WebSockets, ElevenLabs Webhooks) to the internal `Oracle` interface.
- **Examples**: `OpenCodeBridge`, `ElevenLabsBridge`.

---

## §2 Ghost Dependencies & Configuration Drift
A comparison between `pyproject.toml` and `requirements.txt` reveals significant "ghost dependencies" — libraries used in the code and declared in the project spec but missing from the installation requirements.

### 2.1 Missing in `requirements.txt`
The following critical dependencies are declared in `pyproject.toml` but are **MISSING** from `requirements.txt`:
- `qdrant-client` (Critical for Vector search)
- `fastembed` (Critical for local embeddings)
- `redis` (Critical for Warm memory tier)
- `fastmcp` (Critical for MCP server implementation)
- `prometheus-client` (Observability)
- `psutil` (Hardware monitoring)
- `beautifulsoup4` (Document parsing)
- `markdown` (Document parsing)

### 2.2 Impact
This is a **Sovereignty Risk**. A new user running `pip install -r requirements.txt` will experience immediate crashes in the `MemoryStore`, `SovereignSearchService`, and `Omega Hub` because these libraries will be missing. The system is currently relying on the environment's pre-installed packages rather than a reproducible specification.

---

## §3 Data Flow Mapping: Legacy $\rightarrow$ Engine
Mapping how legacy knowledge and architectural intent are transformed into runtime logic.

### 3.1 The Gnosis Pipeline
`Legacy Archives` $\rightarrow$ `Roc Racoon Mining` $\rightarrow$ `Scribe Distillation (L1→L2→L3)` $\rightarrow$ `soul.yaml` $\rightarrow$ `ContextBuilder` $\rightarrow$ `ModelGateway`.

### 3.2 The Heritage Pipeline
`id Software Source` $\rightarrow$ `Heritage Vetting Pipeline (4-gate)` $\rightarrow$ `CREDITS.md` $\rightarrow$ `[id-soft:]` tags in `src/omega/`.

### 3.3 The Research Pipeline
`SovereignSearchService (5-tier)` $\rightarrow$ `IterativeResearcher (Gap Analysis)` $\rightarrow$ `SkepticalVerifier (Two-Source Rule)` $\rightarrow$ `TaintedData` $\rightarrow$ `Sovereign Gnosis (Omega Hub)`.

---

## §4 Recommendations
1. **Synchronize Dependencies**: Immediately update `requirements.txt` to match `pyproject.toml`.
2. **Formalize SSP**: Document the 5-Tier Sovereign Search Protocol in `OMEGA_ENGINE.md` as a core architectural pattern.
3. **Promote TDP**: Elevate the Tainted Data Protocol to a Sovereign Mandate (M16) to ensure all future data ingestion follows the "Tainted $\rightarrow$ Verified" flow.
4. **Audit Bridge Patterns**: Ensure all new bridges follow the `OpenCodeBridge` pattern to maintain a clean separation between the Oracle and external interfaces.
