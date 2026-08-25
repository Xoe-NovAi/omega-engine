# 📊 FLE COUNCIL SCORECARD SPECIFICATION (v1.0)
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_fle_scorecard
**Status:** ACTIVE for Track-D (Sprint-1)

## §1 THE HYBRID MEASUREMENT DOCTRINE
LLM self-reporting is subject to survivorship bias and ceremonial compliance. To achieve cryptographic ground truth, the Omega Engine Scorecard fuses two data streams:
1. **The Milestone Stream (Git/Flash):** Parsed via `scripts/collect_telemetry.py`. Captures agent-reported duration, gate status, and ceremony census at successful commit boundaries.
2. **The Dark Matter Stream (DB/Pro):** Queried via `opencode-sessions-explorer`. Captures absolute token burn, hidden tool failures, and aborted sessions that never reached a commit.

## §2 THE CORE METRICS

### M1: The Semantic Yield Ratio (Tokens per Finding)
*   **Formula:** `Total DB Tokens (Input + Output) / Number of Resolved Specs`
*   **Purpose:** Measures the true cost of intelligence. If this ratio spikes, the coordination tier is suffocating the execution tier (Theorem 2).

### M2: The Ceremony Index
*   **Formula:** `Count of Gates Passed / Count of Gates Falsified (Proven Red before Green)`
*   **Purpose:** Defeats Theorem 4. A perfect score is 1.0. If the index is > 1.0, agents are running gates that cannot fail (e.g., `make temple-grade` stubs).

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
