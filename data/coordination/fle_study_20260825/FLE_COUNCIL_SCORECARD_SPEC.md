# 📊 FLE COUNCIL SCORECARD SPECIFICATION (v1.1)
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode ⬡ trc_fle_scorecard
**Status:** ACTIVE for Track-D (Sprint-1) · **v1.1**: M2 formula fixed, hypotheses renamed H1-H5 with falsification criteria (Carmack campaign audit F5/F7)

## §0 FLE HYPOTHESES (renamed from "theorems" — n=1 origin, Carmack audit F5)
These are HYPOTHESES from a single run (n=1). They earn the word "law" only via replication across future councils.
- **H1 Generative Anti-Compression** — claim: LLM summarization of LLM output expands text. *Falsified if*: any generative digest stage measurably shrinks its source corpus (bytes) without losing decree-cited findings in trace tests.
- **H2 Coordination Tax Divergence** — claim: orchestration overhead scales ~O(N) on tree width. *Falsified if*: a wider tree shows flat or sublinear orchestrator share across ≥3 runs.
- **H3 Ambiguity Attractor** — claim: unassigned identity fields converge on parent-context values, uniformly. *Falsified if*: packets with unspecified fields produce correct registrations ≥80% across ≥10 leaves.
- **H4 Ceremonial Compliance** — claim: rule-bound agents perform ritual steps whose mechanisms are absent rather than fabricating facts. *Falsified if*: ceremony census stays 0 across a full sprint under deletion-probe sampling.
- **H5 Dual-Pass Adversarial Value** — claim: async adversarial audit catches high-severity leaks that synchronous synthesis misses. *Falsified if*: two consecutive councils produce audits with zero CRITICAL/HIGH findings.

## §1 THE HYBRID MEASUREMENT DOCTRINE
LLM self-reporting is subject to survivorship bias and ceremonial compliance. To achieve cryptographic ground truth, the Omega Engine Scorecard fuses two data streams:
1. **The Milestone Stream (Git/Flash):** Parsed via `scripts/collect_telemetry.py`. Captures agent-reported duration, gate status, and ceremony census at successful commit boundaries.
2. **The Dark Matter Stream (DB/Pro):** Queried via `opencode-sessions-explorer`. Captures absolute token burn, hidden tool failures, and aborted sessions that never reached a commit.

## §2 THE CORE METRICS

### M1: The Semantic Yield Ratio (Tokens per Finding)
*   **Formula:** `Total DB Tokens (Input + Output) / Number of Resolved Specs`
*   **Purpose:** Measures the true cost of intelligence. If this ratio spikes, the coordination tier is suffocating the execution tier (Theorem 2).

### M2: The Ceremony Index (v1.1 — formula fixed per audit)
*   **Formula:** `Gates lacking falsification evidence / Total gates evaluated`
*   **Protocol:** a gate "has falsification evidence" only if the executor ran it BEFORE the fix (observed RED) and AFTER (observed GREEN). 
*   **Purpose:** 0.0 = honest. >0.0 = ceremony suspected. The old v1.0 formula (passed/falsified) was self-defeating — honest execution always yielded 1.0, detecting nothing.

### M3: The Friction Coefficient
*   **Formula:** `Total opencode.db Tool Errors / Total Tool Calls`
*   **Purpose:** Measures environment hostility. Tracked via `opencode-sessions-explorer-list-tool-failures`. High friction indicates broken infrastructure (e.g., dead plugin paths), not agent incompetence.

## §3 EXECUTION PROTOCOL (For Track-S)
While Track-D executes in `feat/sprint-1-execution`, Track-S will run the following sequence at SYNC-2 and SYNC-3:

1. **Ingest Milestones:** 
   `python scripts/collect_telemetry.py --since-commit <start_sha> --summary`
2. **Ingest Dark Matter:**
   `opencode-sessions-explorer-cost-by-project` (filtered by timestamp)
   `opencode-sessions-explorer-list-tool-failures`
3. **Fuse & Report:**
   Compile M1, M2, and M3 into `FLE_METRICS_BASELINE.md`.
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

