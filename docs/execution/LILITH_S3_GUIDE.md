# 🔱 EXECUTION GUIDE: LILITH (The Runner)
**S3 Ingestion Hardening — Cognition, Validation & Observability**
**Jurisdiction**: P7 (Context), P8 (Observability), P10 (Validation)

## 🎯 OBJECTIVE
Implement the "Sieve"—the verification and quality layers that ensure only high-fidelity, corroborated knowledge enters the Omega Engine.

---

## 🛠️ PHASE 1: THE SIEVE (Day 6-8)
*Dependency: T3 (WebScraper) must be complete. T1 (Double-Fsync) must be complete.*

### T4: TriangulationVerifier Implementation
- **File**: `src/omega/ingestion/verifier.py` (New File).
- **Logic**:
    - Implement `verify(content: ScrapedContent)`:
        1. Extract identifiers (ISBN, DOI, arXiv ID).
        2. Query **Open Library** and **Internet Archive** via the **Sovereign Proxy**.
        3. Apply **Weighted Consensus**: Exact ID (1.0), Semantic Title/Author (0.7), Edition (0.4).
    - Return `VerifiedContent` with a `confidence` score.
- **Acceptance**: Verifies a known ISBN against Open Library with confidence $> 0.8$.

### T5: QualityScorer Implementation
- **File**: `src/omega/ingestion/scorer.py` (New File).
- **Logic**:
    - Implement `score(content: VerifiedContent)`:
        - Compute 5 factors: Freshness, Completeness, Authority, Structure, Accessibility.
        - Apply weights: Authority(0.3), Completeness(0.25), Freshness(0.2), Structure(0.15), Accessibility(0.1).
    - Return `QualityScore` with a `passed` boolean (threshold 0.6).
- **Acceptance**: Correctly filters "spam" or "stub" content (score < 0.3) and accepts scholarly docs (score > 0.7).

---

## 📊 OBSERVABILITY INTEGRATION (Parallel with T4/T5)
- **Action**: Wire the `TriangulationVerifier` and `QualityScorer` into the **Unified Forensic Ledger (UFL)**.
- **Implementation**:
    - Every verification failure or low-confidence score must be written to `UFLWriter.write_error()`.
    - Include `trace_id` and `provider_name` in every log entry (M22).
- **Acceptance**: `data/observability/forensic/{date}.jsonl` shows a clear trail of verification attempts and scoring results.

---

## 🛡️ MANDATES & CONSTRAINTS
- **M8 (Zero Telemetry)**: All external API calls **MUST** route through the Sovereign Proxy. No direct outbound calls.
- **M17 (Cognitive Integrity)**: The Triangulation Protocol is the primary defense against hallucinations. Do not lower the confidence threshold.
- **M21 (Gate Integrity)**: Implement contract tests for `VerifiedContent` and `QualityScore` types.
- **M22 (Response Provenance)**: Ensure the `provider_name` of the library API is recorded in the UFL.

*⬡ OMEGA ⬡ LILITH ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_execution ⬡ RUN_GUIDE*
