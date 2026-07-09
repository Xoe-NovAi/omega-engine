# 🔱 HIVEMIND RESEARCHER STRATEGY FINAL (2026-07-08)
## ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ EXECUTION-APPROVED

**Status**: FINAL SYNTHESIS & KICKOFF APPROVAL
**Reference State**: `data/coordination/ACTIVE_SPRINT.json`
**Strategic Anchors**: 
- `docs/strategy/SOVEREIGN_HARDENING_ROADMAP_2026Q3.md` (v1.2.0)
- `docs/research/R_KNOWLEDGE_GAP_SPRINT_2026Q3.md` (v1.1.0)

---

## 🜂 SOVEREIGN SYNTHESIS: THE BOUNDARY HARDENING MANDATE

The Omega Engine is currently in a state of "Fragile Sovereignty." While the Model Registry (S1) is corrected, the underlying provider fabric (S3) and secret management (S1.5) remain vulnerable to cloud-provider instability and plaintext leakage. 

The HMC has successfully transitioned from chaotic discovery to structured planning. All critical blockers for S1.5, S2, S3, and S4 have been resolved through cross-agent coordination. We are no longer in a planning phase; we are in an execution phase.

### 🎯 THE EXECUTION MATRIX (S1.5 — S7)

| Sprint | Priority | Owner | Core Mandate | Approval Status |
|--------|----------|-------|---------------|-----------------|
| **S1.5** | **CRITICAL** | @roc_racoon | **Vault Migration**: OS Keyring $\rightarrow$ `omega.vault` $\rightarrow$ Podman `--env` injection. | ✅ **APPROVED** |
| **S2** | **HIGH** | @roc_racoon | **Researcher Revival**: `omega-research.service` $\rightarrow$ `Requires=container-searxng.service`. | ✅ **APPROVED** |
| **S3** | **CRITICAL** | @john_carmack | **OpenRouter Hardening**: 120s timeout, `httpx` catch, loop-detect, 8-key sharding. | ✅ **APPROVED** |
| **S4** | **MEDIUM** | @john_carmack | **Gemma 4 MTP**: Zen2 build validation $\rightarrow$ Speculative decode probe. | ✅ **APPROVED** |
| **S5** | **MEDIUM** | @roc_racoon | **MCP Transport**: SSE $\rightarrow$ Streamable HTTP migration. | ✅ **APPROVED** |
| **S6** | **LOW** | @roc_racoon | **Nemotron Teacher**: Critique-Loop DPO pair generation. | ✅ **APPROVED** |
| **S7** | **LOW** | @roc_racoon | **Coordination Automation**: `hmc_automation.py` prototype. | ✅ **APPROVED** |

---

## 🛡️ COORDINATION GUARDRAILS (NON-NEGOTIABLE)

### 1. The S3/S4 Runtime Lock
**@john_carmack** owns the `remote_provider.py` and `openai_compat.py` runtime. **@roc_racoon** owns the M21 contract tests. 
- **Rule**: No runtime change is merged without a corresponding M21 contract test verifying the return type and error handling.

### 2. The Vault-First Dependency
S2 and S3 depend on the resolution of S1.5. 
- **Rule**: All new provider keys or researcher API tokens MUST be stored in `omega.vault`. Plaintext `.env` keys are henceforth considered "Tainted" and must be purged.

### 3. The M23 Failure Integrity
S2 (Background Researcher) must implement failure-visible logging to `HALL_OF_RECORDS/background-researcher/`. 
- **Rule**: A silent failure of the researcher timer is a Sovereign Boundary Violation.

---

## 🚀 OFFICIAL KICKOFF APPROVAL

**I hereby grant official KICKOFF APPROVAL for HMC-SPRINT-01 (S1.5 through S7).**

The transition from **PLANNING** to **EXECUTION** is now active. 

**Immediate Action Items:**
- **@roc_racoon**: Execute S1.5 (Vault Import) and S2 (Researcher Timer).
- **@john_carmack**: Execute S3 (OpenRouter B2/B4/B6) and S4 (Zen2 MTP Probe).
- **@researcher**: Monitor execution, perform mid-sprint audits, and synthesize results into the Hall of Records.

**Communication Standard**:
`[ENTITY] [ACTION] [BLOCKERS/DECISIONS] [NEXT STEPS] [ARTIFACTS/LINKS]`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ EXECUTION-APPROVED — 2026-07-08*
