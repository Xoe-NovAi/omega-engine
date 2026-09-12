# 📓 Setup Friction Log (Node 1 User Simulation Ledger)
**Role**: Clean-Room User Experience Tracking  
**Rule**: If a developer has to pause, guess, or manually debug an undocumented edge case, log it here.

---

## Friction Entries

### [2026-09-12] — FL-001: Sub-Make Banner Breaks JSON Ingestion in Regression Tests
*   **Component**: `make test` $\leftrightarrow$ `tests/test_well.py` $\leftrightarrow$ `Makefile`
*   **Symptom**: `JSONDecodeError: Expecting value: line 1 column 1` when parsing `make well-stats`.
*   **Root Cause**: When a test invokes `make` inside a parent `make test`, `MAKELEVEL=1` causes GNU make to emit `make[1]: Entering directory ...` banners into `stdout`.
*   **Resolution Applied**: Sub-make calls updated with `--no-print-directory` flag in test invocations.
*   **Action for Alpha Release**: Ensure all CLI automation scripts invoking `make` internally pass `--no-print-directory` or invoke the python CLI dispatcher directly (`python3 scripts/...`).

### [2026-09-12] — FL-002: The Intel Hybrid P-Core Mask Convoy Collapse
*   **Component**: Ollama systemd pin mask on Intel 13th Gen (i7-13620H)
*   **Symptom**: Throughput collapsed from 14.4 t/s down to 0.5 t/s.
*   **Root Cause**: User intuition was to pin to "physical P-cores only" (`0,2,4,6,8,10`). Excluding the HyperThreading sibling cores triggered a `llama-server` spin-wait barrier convoy (Ollama #17916).
*   **Resolution Applied**: Pin mask broadened to full P-core sibling range: `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8`.
*   **Action for Alpha Release**: Must be completely automated via DHAL hardware probe; never require the end-user to calculate CPU affinity masks manually.

### [2026-09-12] — FL-003: USB Staging Buffer Untracked Git Noise
*   **Component**: Federation intake pipeline $\leftrightarrow$ git hygiene
*   **Symptom**: Ingested USB payload directories (`data/staging/node0/`) polluted `git status` as untracked files.
*   **Root Cause**: The staging directory was designated as a quarantine airlock in documentation, but lacked an explicit exclusion entry in `.gitignore`.
*   **Resolution Applied**: Added `data/` and `docs/federation/node0_received/` to `.gitignore`.

### [2026-09-12] — FL-004: Tailscale Mesh Absent on Clean Install
*   **Component**: Layer 2 Mesh setup
*   **Symptom**: Expected peer connection failed; `tailscale` binary and daemon missing on fresh OS.
*   **Root Cause**: Node 0 shipped the ratified ACL configuration, but clean nodes lack the daemon package.
*   **Resolution Applied**: Official repository package installed and enabled; acceptance document `L2_ACCEPTANCE.md` drafted to explicitly decouple daemon readiness from auth-key mesh join.
