## Architecture Plan
1. **Key Pool (Empirical Steward)**: 
   - Implement reactive exponential backoff starting at 60s (60s $\rightarrow$ 120s $\rightarrow$ 240s).
   - Pivot to next key ONLY after 3 consecutive denials.
   - Move failed keys to 60-minute COOLDOWN.
   - Load keys from `config/keys/google_pool.yaml`.
2. **Metric Engine (Rate-Limit Mapping)**:
   - Intercept and log every 429, retry attempt number, and success/failure delta.
   - Use `metrics.db` to empirically map the actual Google API rate limits.
   - Implement `omega metrics` CLI for fleet health and boundary analysis.
3. **Integration**:
   - Wire `BackgroundResearcher` to use this empirical provider for synthesis.
4. **Sovereign UID Guard**:
   - Implement `scripts/uid_guard.sh` to detect and automatically remediate UID drift (100999 $\rightarrow$ 1000) using `podman unshare`.
   - Enforce zero-tolerance for `:U`, `:Z`, `:z` flags in all Quadlets.
