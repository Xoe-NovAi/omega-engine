# 🔱 Web Claude Fleet Hardening Plan
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_fleet_hardened ⬡ PHASE-E

**AP Token**: `AP-WEB-CLAUDE-HARDEN-v1.0.0`
**Status**: PROPOSED
**Objective**: Transform the 8-account Web Claude fleet from a manual review process into a hardened, systematic orchestration layer.

---

## §1 Current State Analysis
The current fleet operates via `WEB_CLAUDE_FLEET_PROTOCOL.md` and `FLEET_MANAGEMENT.md`.
- **Strengths**: Clear role specialization, raw URL access, structured deep dive sequences.
- **Weaknesses**: 
  - **Manual State Tracking**: Progress is tracked in a markdown table, prone to drift.
  - **Manual Handoffs**: Prompts are manually copied and pasted.
  - **Lack of Cross-Verification**: Accounts work in silos; findings are only synthesized at the end.
  - **Fragile Context**: No systemic way to ensure "warm context" is maintained across deep dives beyond manual conversation management.

---

## §2 Proposed Hardening Layers

### Layer 1: Fleet Orchestration Layer (FOL)
Move fleet state from markdown to a structured `fleet_state.json` or a dedicated table in `workbench.db`.
- **Track**: `account_id`, `current_role`, `current_project`, `last_handoff_timestamp`, `deep_dive_level` (0-6), `token_estimate`, `report_status`.
- **Benefit**: Enables programmatic tracking and automated reminders for rate-limit resets.

### Layer 2: Automated Handoff Generator
Create a tool (or a specialized OpenCode mode) that:
1. Takes a list of files/topics.
2. Fetches the latest `raw.githubusercontent.com` URLs.
3. Injects the current `Sovereign Mandates` and `Project Instructions`.
4. Generates the exact prompt for the target account.
- **Benefit**: Eliminates manual prompt construction errors and ensures mandate consistency.

### Layer 3: The Verification Loop (Cross-Account Audit)
Introduce a "Verification" phase between Initial Review and Synthesis:
- **Pattern**: Account A finds a CRITICAL issue $\rightarrow$ Handoff is sent to Account B to attempt to reproduce/verify.
- **Benefit**: Reduces false positives and increases confidence in critical findings before they hit the Master Remediation Plan.

### Layer 4: Mandate Enforcement Protocol
Update all account system prompts to require **Evidence-Based Verification**:
- **Old**: "Check for AnyIO compliance."
- **New**: "For every AnyIO violation, provide the exact file:line and the specific `asyncio` call that must be replaced. For every PASS, provide one example of a correct `anyio.to_thread.run_sync` wrapper."
- **Benefit**: Forces the model to actually read the code rather than hallucinating compliance.

---

## §3 Implementation Roadmap

| Phase | Task | Priority | Target Date |
|-------|------|----------|-------------|
| **1** | Implement `fleet_state.json` tracking | HIGH | Next Session |
| **2** | Create Handoff Generator script | MEDIUM | Next Session |
| **3** | Update Account 1-8 System Prompts (Evidence-Based) | HIGH | Next Session |
| **4** | Pilot the Verification Loop (Account 1 $\leftrightarrow$ Account 2) | LOW | Following Session |

---

## §4 Next Critical Account: Account 4 (Research Director)
Account 4 is the primary target for hardening the background worker systems.
**Mission**: "The Background Worker Hardening Audit"
- **Focus**: Verify the transition from Roc Racoon $\rightarrow$ Roc Racoon.
- **Audit**: Ensure `distiller.py` and `soul_updater.py` are 100% firewall-compliant.
- **Verification**: Test the `roracoon-3b` model's ability to perform archaeological recovery without cloud leakage.
