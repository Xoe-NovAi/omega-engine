<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# 🎭 Antigravity Peer Review — Stage 2: Claude Sonnet 4.6
## Code Verification, Concurrency Hardening, and AST Static Enforcement

**Document ID:** `PROMPT-ANTIGRAVITY-STAGE-2-CLAUDE-SONNET-4.6`  
**Role:** Principal Systems Software Engineer & Adversarial Security/Concurrency Auditor  
**Context Inputs:**
1. Attach `ANTIGRAVITY_REVIEW_BRIEFING_20261001.md` (`FED-ANTIGRAVITY-REVIEW-BRIEFING-20261001-01`).
2. Attach the **Full Output from Stage 1 (Gemini 3.1 Pro)**.  
**Deliverable:** Concrete, production-grade Python implementations, AST static analysis tools, adversarial edge-case audits, and systemd supervisor configurations.

---

### INSTRUCTIONS FOR CLAUDE SONNET 4.6

You are acting as the **Principal Systems Software Engineer and Adversarial Code Auditor** for the **Omega Engine** (`Xoe-NovAi/omega-engine`). 

You have been provided with:
1. The architectural briefing (`ANTIGRAVITY_REVIEW_BRIEFING_20261001.md`).
2. The distributed systems and logical foundations delivered by **Gemini 3.1 Pro in Stage 1**.

Your mandate is to translate, stress-test, and harden these designs into **bulletproof, executable Python code and systems configuration**. You do not deal in vague generalities; you provide exact code, edge-case failure analysis, and concrete test assertions.

Address the following four engineering requirements:

---

### 1. Concrete Implementation of the Substrate Read-Path Fix (Domain 1)
* **The Task:** Review Carmack's "Option A-Minus" and Gemini 3.1 Pro's queue concurrency recommendation from Stage 1.
* **Requirements:**
  * Provide the exact Python patch for `mcp_servers/omega_hub/hub_tools/tools.py` (around lines 1350–1370) and `mcp_servers/omega_hub/federation_store.py`.
  * Ensure dual-key lookup: handles both legacy packets (`packet_id`) and modern envelopes (`handoff_id`) without throwing `KeyError` or schema validation errors.
  * Implement the receipt recording mechanism (either atomic in-place rewrite with `fcntl.flock` or Gemini's append-only journal) such that concurrent reads by two subagents within 5 milliseconds of each other will **never** corrupt the file or drop a reader's key.
  * Provide the complete, runnable pytest canary test (`tests/test_federation_read_canary.py`) that demonstrates the bug failing before the patch and passing after.

---

### 2. Standalone AST Enforcement for the M2 Firewall (Domain 2)
* **The Task:** The previous team mistook `import-linter` as an M2 enforcement tool, missing that WADs are data loaded via `Path` literals at runtime (`src/omega/oracle/wad_loader.py` and `src/omega/research/sandbox.py:548`).
* **Requirements:**
  * Write a clean, zero-dependency Python AST static analysis script: `scripts/check_m2_firewall_ast.py`.
  * Invariant: `src/omega/oracle/wad_loader.py` is the **only** permitted module in `src/omega/` that may reference `"config/wads"` (in strings, `Path` calls, imports, or variable names).
  * The script must traverse the AST of every `.py` file under `src/omega/`, detect string literals, joined paths, and imports pointing to `config/wads/`, report file/line numbers with clear error context, and exit 1 on violation.
  * Ensure it handles edge cases: ignore comments/docstrings, handle f-strings containing WAD paths, and distinguish legitimate core engine terminology from stack paths.

---

### 3. Identity Pipeline Implementation & Schema Adaptation (Domain 3)
* **The Task:** Implement the backward-compatible adapter in `tools.py:hivemind_handoff` for the 3-tuple `(Agent, Instance, Node)` based on Gemini's Stage 1 specification.
* **Requirements:**
  * Show the exact Python function signature and resolution logic that parses:
    * Legacy callers passing `source_entity="carmack"`
    * Modern callers passing `source_entity="carmack"`, `source_instance="ses_f0b67..."`, `source_channel="opencode"`
  * Implement the Fellegi-Sunter clerical review routing: if the resolution confidence is in the ambiguous zone, write the packet to `data/handoff/pending/clerical_review/` and return the structured warning payload.

---

### 4. Supervisor Hardening & Crash-Loop Prevention (Domain 5)
* **The Task:** The engine experienced an 81.5 MB error log accumulation over 2.5 months because `omega-research.service` was restarting every 30 seconds on `ModuleNotFoundError`.
* **Requirements:**
  * Provide the hardened, production-grade systemd user service definition: `config/systemd/omega-research.service`.
  * Include systemd restart-rate limiters (`StartLimitIntervalSec`, `StartLimitBurst`, `RestartSec`, `RestartPreventExitStatus`) to ensure that a missing module or persistent configuration error halts restarts and alerts the operator rather than spinning indefinitely.
  * Provide a companion log rotation / health check rule to prevent unmonitored log bloat.

---

### EXPECTED OUTPUT STRUCTURE
Your output must be structured under the following four clear headers:
1. `## 1. Substrate Read-Path Implementation & Boundary Canary Test`
2. `## 2. AST M2 Engine-Stack Firewall Checker (scripts/check_m2_firewall_ast.py)`
3. `## 3. Backward-Compatible Identity Resolution & Clerical Queue Logic`
4. `## 4. Hardened Systemd Service & Supervisor Crash-Loop Defense`

Provide full, production-ready code blocks without truncation. Your output, combined with Stage 1, will form the technical basis for Claude Opus 4.6 in Stage 3.
