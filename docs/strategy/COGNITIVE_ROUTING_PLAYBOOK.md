# 🔱 COGNITIVE ROUTING & PRIMING PLAYBOOK
**AP Token**: `AP-GEMINI-ROUTING-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ GEMINI-3.1-PRO ⬡ opencode ⬡ trc_cognitive_routing ⬡ ACTIVE

**Date**: 2026-08-24
**Origin**: Extracted from the Architect's manual orchestration techniques.

## §1 THE ARCHITECT'S PRIMING MANEUVER
The most efficient use of frontier weights is to separate **context gathering (I/O)** from **reasoning (Cognition)**. 

1. **The Primer Phase**: Use inexpensive, fast models (e.g., Haiku 4.5, Qwen local, Nemotron 3 Ultra) to execute tool calls, `grep` the codebase, read files, and build the active context window. 
2. **The Ceiling Rule**: Prime the context up to a maximum of **85%** of the target model's total window (e.g., ~150K for a 200K window model). Exceeding this triggers auto-compaction on model switch, destroying the evidentiary base.
3. **The Cognitive Switch**: Once the context is saturated with ground truth, switch to the frontier model (Opus 4.6, Sonnet 5, Gemini 3.1 Pro). 
4. **The Execution**: Instruct the frontier model to execute **zero tool calls**. Its entire token budget is spent on pure reasoning, synthesis, and adjudication over the primed context.

## §2 THE DUAL-REVIEW DIALECTIC (Ascending Windows)
When consensus is required, do not run models in parallel. Run them sequentially in order of ascending context windows.

*   **Step 1**: Prime context to ~140K.
*   **Step 2**: **Sonnet 4.6 / Opus 4.6** (200K Window) performs the primary review and writes its findings to disk (M11 Distill-Before-Switch).
*   **Step 3**: Switch to **Gemini 3.1 Pro** (1M Window). Because 200K < 1M, no compaction occurs. Gemini inherits the raw context *plus* the Claude-family verdict.
*   **Step 4**: Gemini's explicit mandate is to *adversarially cross-examine* the first verdict. 

## §3 THE 1M CONTEXT "FAT" WORKFLOW
For massive refactors or deep architectural analysis (e.g., Ox Alpha consuming 124K tokens per message):
*   Do not chunk the codebase. Load the entire subsystem.
*   The 1M window is not just for reading; it is for maintaining the *state of the system across time* during a long session. 
*   **Warning**: High-context messages carry high latency and cost (if not on free tiers). Use only when the relational complexity between files exceeds what a `grep` can reveal.
