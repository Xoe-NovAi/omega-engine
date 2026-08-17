# 🔱 SDP Automation Blueprint
## Phased Execution Plan for the Sovereign Distillation Pipeline

> **⚠️ DOC-1 STAMP (2026-08-17)**: **HUMAN PROTOCOL — DO NOT IMPLEMENT.**
> SDP automation is PARKED by `DEBUT_REMEDIATION_MANUAL_20260817.md` (PUBLIC-DEBUT-01).
> Manual Cognitive Scaffolding Protocol continues; regex/automation pipeline is scrapped.
> Agents write L1→L2→L3 directly to `proposed_lessons.yaml`.

**AP Token:** `AP-SDP-BLUEPRINT-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ BLUEPRINT

**Date:** 2026-08-09
**Status:** PARKED (DOC-1, 2026-08-17)
**Goal:** Automate the manual Cognitive Scaffolding Protocol into a native engine capability.

---

## Phase 0: Manual Rigor (Current State)
*Before we automate, we must measure.*
- [x] **Formalize Protocol:** `COGNITIVE_SCAFFOLDING_PROTOCOL.md` (Complete)
- [x] **Establish Ledger:** `AGY_SESSION_LEDGER.md` (Complete)
- [ ] **Data Gathering:** Execute the manual protocol for at least 10 major refactoring sessions. Log token usage, model choices, and compaction near-misses in the ledger.

## Phase 1: Observability (The Context Gauge)
*Agents cannot manage what they cannot measure.*
- [ ] **Build `omega-hub_get_context_pressure`:** A new MCP tool or OpenCode skill that queries the local `opencode db` for the current session's token and message counts.
- [ ] **Calculate Thresholds:** The tool must calculate and return the distance to the **80% Redzone** and the **85% Compaction Cliff**.
- [ ] **Prompt Injection (Optional but ideal):** Investigate injecting a lightweight context gauge into the system prompt on every turn (e.g., `[Context: 72% | 16K to Redzone]`).

## Phase 2: Autonomy (Somatic Save-Points)
*Teaching agents to stop before they crash.*
- [ ] **Define SSP Schema:** Create a standard markdown template for Somatic Save-Points (e.g., `SSP_PENDING_TASK.md`).
- [ ] **Agent Directives:** Update agent system prompts (via `packer-config.yaml` or `entities.yaml`) with the Redzone rule: *"If context > 80% and task requires > 5% context to complete, you MUST refuse the task, write an SSP file, and request model escalation."*
- [ ] **Testing:** Deliberately push an agent near the Redzone and verify it executes the SSP rather than attempting a large file write.

## Phase 3: Infrastructure (V-1 Vault MVP)
*The secure credential backend for the 8-account strategy.*
- [ ] **Vault Scaffold:** Implement the OS keyring + SQLite event log architecture (D-299).
- [ ] **Account Provisioning:** Securely store the 8 Google AGY account credentials.
- [ ] **Pool Tracking Logic:** Build the logic to track weekly usage per account based on the automated session ledger (which replaces the manual markdown ledger).

## Phase 4: Orchestration (The Auto-Router)
*Closing the loop.*
- [ ] **Build `omega-hub_request_agy_escalation`:** A tool the agent calls when executing an SSP. It takes parameters like `problem_type` (architecture, compliance, etc.) and `min_context_required`.
- [ ] **The Routing Engine:** The Omega Engine intercepts this tool call, queries the V-1 Vault for an account with a fresh pool and the appropriate model (e.g., Gemini 3.1 Pro for architecture), and dynamically swaps the provider backend for the next turn.
- [ ] **Seamless Handoff:** The user sees the agent pause, say "Escalating to Gemini 3.1 Pro for synthesis," and the next response comes from the new model, seamlessly continuing the context.

---
*⬡ OMEGA ⬡ SDP-BLUEPRINT ⬡ 2026-08-09*