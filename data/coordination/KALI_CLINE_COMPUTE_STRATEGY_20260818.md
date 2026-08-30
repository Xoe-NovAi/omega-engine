<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Gemini 3.1 Pro → Cline: Compute Abundance & Execution Strategy
**AP Token**: `AP-GEMINI-CLINE-COMPUTE-20260818-v1.0`
**From**: Gemini 3.1 Pro / Kali (Strategic Oversight)
**To**: cline/omega-engine (Cognitive Extension)
**Date**: 2026-08-18
**Status**: ACTIVE — Strategic Directives for 1M Context Utilization

---

## 1. Welcome Back & The Current State

While you were offline, the **MaKaLi Cloud Council** convened and issued a Unified Sovereign Verdict on the Debut Hardening Plan (`data/coordination/MAKALI_COUNCIL_VERDICT_20260817.md`).

**The Verdict**:
*   **INST-1 is BLOCKED**: 6 critical fixes are required before we can proceed. (Install honesty, pyproject.toml extras, Redis opt-in, ModelGateway secrets, version alignment, README).
*   **DEL-1 is CONDITIONAL**: Requires a green test baseline (currently 1 failure), an observability emission spec, and an **atomic god-module split**.
*   **PUB-1 is READY**: Awaiting Architect allowlist confirmation.

## 2. The Compute Arsenal Strategy

We now have access to a massive compute pool: **DeepSeek V4 Flash (1M context)**, **Nemotron 3.5 Lightning 30B A3B**, and **Laguna S 2.1**, across 8 accounts. 

**The Guardrail**: This compute abundance is for *our* CI/CD and refactoring. The Engine Core must remain capable of running on a bare-metal 8GB laptop. Do not let cloud abundance bloat the local-first architecture.

Here is exactly how we deploy this arsenal:

### A. DeepSeek V4 Flash (1M Context) — The "God-Module Scalpel"
*   **Target**: DEL-1 Week 2 (Atomic God-Module Split).
*   **The Problem**: `oracle.py` (1455 lines) and `model_gateway.py` (1581 lines) violate the god-module freeze. Splitting them while simultaneously collapsing 4 routers into 1 is highly risky.
*   **The 1M Context Solution**: You can ingest *both* massive files, their entire test suites, and the `ProviderSelector` spec simultaneously. You can output the perfectly split modules (`dispatcher.py`, `router.py`, `provider_loader.py`, `generator.py`) in a single, atomic, context-aware shot. This eliminates the risk of import cycles and broken state machines.

### B. Nemotron 3.5 Lightning 30B A3B — The "Logic Sniper"
*   **Target**: INST-1 Fixes & Test Baseline (C1).
*   **The Problem**: We have 1 failing test (`test_oom_protector_RAM_check_under_pressure` - DENY_THRASHING vs ALLOW) and 6 surgical fixes needed for INST-1 (like guarding Redis construction and removing the `.env` dump).
*   **The Nemotron Solution**: Use Nemotron's high-precision logic to fix the OOM test and execute the 6 INST-1 fixes. It is fast, accurate, and perfect for localized logic correction.

### C. Laguna S 2.1 — The "Debt Annihilator"
*   **Target**: P2 Lint Debt (4,895 flake8 violations).
*   **The Problem**: After DEL-1, we still have thousands of unused imports and line-length violations.
*   **The Laguna Solution**: Once DEL-1 is merged, we feed entire directories to Laguna to semantically resolve F401 (unused imports) and E501 (line lengths) rather than relying on dumb regex auto-fixers.

## 3. Your Immediate Directives (Execution Order)

Switch to **Nemotron 3.5 Lightning 30B** and execute the following:

1.  **Unblock INST-1**: Execute the 6 fixes listed in `ACTIVE_SPRINT.json` under `INST-1`. (Modify `install.sh`, `pyproject.toml`, `memory_store.py`, `model_gateway.py`, `__init__.py`, `README.md`).
2.  **Fix the Test Baseline (C1)**: Resolve the 1 failing test in `tests/chaos/test_oom_kill.py`.
3.  **Execute DEL-1 Week 1**: Perform the 10 pure deletions (no replacements) listed in `ACTIVE_SPRINT.json`.

Once those are complete and the test suite is 100% green, switch to **DeepSeek V4 Flash (1M)** and execute:

4.  **DEL-1 Week 2 (Router Collapse & Atomic Split)**: Ingest the god-modules and execute the router collapse and file splits atomically.

I am handing coordination over to you. The tracking SSOT is updated. Begin with INST-1.

---
*⬡ OMEGA ⬡ GEMINI 3.1 PRO ⬡ 2026-08-18 ⬡ compute-strategy*