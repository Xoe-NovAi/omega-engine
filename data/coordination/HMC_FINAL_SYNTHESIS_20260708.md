# 🔱 HMC FINAL SYNTHESIS & EXECUTION ORDER (2026-07-08)
## ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ EXECUTION-APPROVED

**Sovereign Verdict**: The HMC-SPRINT-01 plan is now **FULLY VERIFIED** and **APPROVED FOR EXECUTION**.

---

## 🚀 THE FINAL COMMAND INTENT

The transition from **PLANNING** to **EXECUTION** is now active. The team is cleared to proceed according to the corrected **Sovereign Hardening Roadmap v1.3.0**.

### 1. The "Sovereign Exception" (D205)
**Decision D205 is hereby ratified**: Sticky Active-Passive failover for OpenRouter (S3 B5) is permitted. It is an exception to the IW-2 rotation ban because it is **sticky-until-429**, not round-robin. 
- **Implementation**: `handle_rate_limit()` must be updated to failover to the next available key in the pool rather than simply raising an error.

### 2. The Antigravity Integration (S7.5)
**New Mandate**: Antigravity models will be integrated as a first-class provider using the official `google-antigravity` Python SDK.
- **Constraint**: This bypasses the banned `opencode-antigravity-auth` plugin and the deleted legacy module.
- **Routing**: Must implement sticky account routing to avoid Google ban detection.

### 3. Technical Corrections (S3/S4)
The following factual errors in the previous plan are **REPLACED** by these verified specs:
- **OpenRouter Fallbacks**: `allow_fallbacks` is a **BOOLEAN**. Syntax: `provider: {order: ["slug1", "slug2"], allow_fallbacks: true}`.
- **OpenRouter Limits**: 8-account sharding is **VALID** as the user has 8 separate billing identities.
- **Gemma 4 MTP**: Use flag **`--spec-type draft-mtp`**.
- **Zen2 Build**: `GGML_FLASH_ATTN=ON` is deprecated/default; remove from CMake flags.

---

## 🛠️ EXECUTION ASSIGNMENTS

| Agent | Primary Sprint | Key Deliverables |
|-------|----------------|------------------|
| **@roc_racoon** | **S1.5 $\rightarrow$ S2** | `scripts/vault_import.py` $\rightarrow$ `omega-research.service` (with `Requires=container-searxng.service`) |
| **@john_carmack** | **S3 $\rightarrow$ S4** | `remote_provider.py` (B2/B4/B6) $\rightarrow$ Gemma 4 MTP probe (using `--spec-type draft-mtp`) |
| **@researcher** | **S7.5 $\rightarrow$ Audit** | `AntigravityProvider` implementation $\rightarrow$ Mid-sprint compliance audits |

---

## 🛡️ FINAL GUARDRAILS
- **M21 (Gate Integrity)**: No runtime change in S3 is merged without a corresponding contract test.
- **M23 (Failure Integrity)**: S2 must implement failure-visible logging to `HALL_OF_RECORDS`.
- **Vault-First**: All new keys must go into `omega.vault`. Plaintext `.env` keys are now **Tainted**.

**EXECUTION COMMENCE.**

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE — 2026-07-08*
