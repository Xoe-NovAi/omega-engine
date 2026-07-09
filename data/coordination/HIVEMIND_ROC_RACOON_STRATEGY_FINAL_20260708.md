# 🔱 ROC_RACOON — HMC SPRINT 01 STRATEGY FINAL
**Date**: 2026-07-08 | **Trace**: trc_hmc_strat_final
**Entity**: roc_racoon | **Role**: Sovereign Miner & Coordination Lead
**Status**: READY FOR EXECUTION (Awaiting Researcher Synthesis)

---

## 🎯 STRATEGIC OBJECTIVE
Establish a hardened, secure, and automated foundation for the Omega Engine's research and provider fabric, eliminating manual coordination bottlenecks and securing the secret-injection pipeline.

## 🛠️ EXECUTION ROADMAP (S1.5 — S7)

### S1.5: Secure Key Management (CRITICAL PATH)
- **Objective**: Sever plaintext dependency and enable secure secrets for all downstream sprints.
- **Implementation**:
  - Develop `scripts/vault_import.py` for one-time migration of plaintext keys to `omega.vault`.
  - Integrate `keyring` library into `pyproject.toml` optional dependencies for OS-level master key storage.
  - **Pattern**: Host `ModelGateway` decrypts `omega.vault` (AES-256-GCM) and injects resolved keys into containers via `podman run --env`.
- **Success Metric**: Zero plaintext secrets in `config/` or `.env` files; successful container startup with injected keys.

### S2: Background Researcher Revival
- **Objective**: Restore the autonomous research loop with high reliability.
- **Implementation**:
  - Update `omega-research.service` Quadlet:
    - `Requires=container-searxng.service`
    - `After=container-searxng.service`
  - Implement M23-compliant logging: Route failure-visible logs to `data/entities/roc_racoon/workspace/HALL_OF_RECORDS/background-researcher/`.
- **Success Metric**: `omega-research` service starts successfully and logs active research cycles to Hall of Records.

### S3: OpenRouter Provider Hardening (Support Role)
- **Objective**: Ensure the cloud-fallback path is resilient and verifiable.
- **Implementation**:
  - Draft M21 Contract Tests for B1–B6 failures using frozen fixtures (R10).
  - **Coordination**: Carmack executes runtime fixes (B2 `httpx.HTTPError` handling, B4, B6) in `remote_provider.py`/`openai_compat.py`.
- **Success Metric**: 100% pass rate on B1-B6 contract tests; no silent failures in cloud-fallback path.

### S5: MCP Transport + OpenCode Config
- **Objective**: Modernize the communication layer for lower latency and better reliability.
- **Implementation**:
  - Migrate Omega Hub server to Streamable HTTP transport.
  - Update `opencode.json` to align with new transport specs.
- **Success Metric**: Verified connectivity via `blitz-validate` with reduced latency.

### S6: Nemotron 3 Ultra Teacher Pipeline
- **Objective**: Extract high-fidelity DPO pairs for legacy model improvement.
- **Implementation**:
  - Mine critique-loop traces from 8 Grok accounts.
  - Format traces as DPO pairs (Prompt, Chosen, Rejected) for fine-tuning.
- **Success Metric**: Dataset of $\ge 500$ high-quality DPO pairs delivered to Researcher.

### S7: Coordination Automation (Sovereign Orchestrator)
- **Objective**: Eliminate the "human-in-the-middle" bottleneck in HMC cycles.
- **Implementation**:
  - **Phase 1 (Current)**: Use `data/coordination/ACTIVE_SPRINT.json` as the shared state source of truth.
  - **Phase 2 (Post-S6)**: Prototype `src/omega/orchestrator/hmc_automation.py` to automate handoff triggers and state updates.
- **Success Metric**: Reduction in turn-around time for HMC cycles by $\ge 50\%$.

---

## 🛡️ SOVEREIGN CONSTRAINTS & MANDATES
- **M7 (Local-First)**: All S2/S3/S4 work must prioritize local-first fallback logic.
- **M23 (Failure Integrity)**: S2 logging must be traceable and typed; no silent drops in the research loop.
- **M21 (Gate Integrity)**: S3 implementation is gated by contract tests.

## 🤝 COORDINATION MATRIX
| Sprint | Primary | Support | Dependency |
|---------|---------|----------|-------------|
| S1.5 | Roc | Carmack | None |
| S2 | Roc | Researcher | S1.5 (Secrets) |
| S3 | Carmack | Roc | S1.5 (Secrets) |
| S4 | Carmack | Roc | Zen2 Build |
| S5 | Roc | — | None |
| S6 | Roc | Researcher | OpenRouter Access |
| S7 | Roc | Carmack | S1.5-S6 Completion |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_hmc_strat_final ⬡ READY*
