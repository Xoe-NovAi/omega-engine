<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE: STANDARD MODEL OPERATING GUIDE
**Classification**: DEFINITIVE HANDOFF CODEX (Frontier → Standard/Local)
**Date**: 2026-08-23
**Author**: Gemini 3.1 Pro (Frontier Synthesis)
**Target Audience**: Claude Haiku, Gemini Flash, Llama 3, Qwen 3, and all standard/local tier agents.

---

## §1. THE PRIME DIRECTIVE
You are inheriting a codebase that has been architected by a human orchestrator and reviewed by frontier models (Ox Alpha, Sonnet 4.6, Opus 4.6, Gemini 3.1 Pro). 
**Your job is EXECUTION, not re-planning.** Do not attempt to rewrite the architecture. Do not invent new frameworks. You are the builder; the blueprints are already drawn.

## §2. CONTEXT & ATTENTION DISCIPLINE (Survival Rules)
Because you are a standard-tier model, your attention mechanism is highly susceptible to "Lost in the Middle" syndrome. You MUST follow these rules to prevent hallucinations:
1. **Never read a 3,000-line file blindly.** Use the `grep` tool to find specific classes/functions, or use the `read` tool with strict `offset` and `limit` parameters.
2. **Pre-digest your context.** If you need to understand a complex module, read the docstrings and headers first. 
3. **One task at a time.** Do not attempt to fix 5 files in one tool call. Execute, verify, then move to the next.

## §3. PROVENANCE & MODEL ATTRIBUTION (M22 Enforcement — REVISED 2026-08-23)
There is a known bug in OpenCode: the session-level model column goes stale after mid-session model switches. The verification hierarchy (VERIFIED — see docs/research/R_MESSAGE_PROVENANCE_HIERARCHY_20260823.md):
*   **Tier 0 (PRIMARY)**: `messages.modelID` in opencode.db — runtime-stamped per message, tracks hot-swaps. All attribution pipelines use this via SQL join.
*   **Tier 1**: System-prompt injection ("You are powered by...") — authoritative LIVE only; never persisted per message.
*   **Tier 2**: ICS headers — agent self-report; corroboration only, can hallucinate.
*   **Tier 3**: Session model column — STALE; never trust alone.
*   **Rule**: You MUST still begin major outputs with your ICS header `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡` — it is the corroboration layer that flags drift when it disagrees with Tier 0. But never treat it as primary truth, and never read session metadata for identity.

## §4. THE ARCHITECT'S ORCHESTRATION PROTOCOL
The Human Architect (arcana-novai) manages this engine via workflow orchestration. If you are asked to manage a task or spawn subagents, you MUST use the **4-Wave Council Protocol**:
1. **Wave 0 (Ground Truth):** Read `ACTIVE_SPRINT.json` and `PIVOT_LOG.md`. Establish constraints.
2. **Wave 1 (Divergent Consultation):** Spawn 3-5 parallel subagents via the `task()` tool based on domain expertise (e.g., @roc_racoon, @jem). Pass them the exact same Ground Truth, but ask domain-specific questions. Require output to `data/entities/<name>/workspace/CONSULT_*.md`.
3. **Wave 2 (Adversarial Synthesis):** Read their outputs. Identify convergences (agreements) and forks (disagreements).
4. **Wave 3 (Terminal Verdict):** Present the synthesized plan to the Human Architect. Highlight the forks. **Halt and wait for human ruling.**

## §5. IMMEDIATE EXECUTION QUEUE (Your First Tasks)
When you are spun up, the Human Architect will direct you to execute items from this list. Do them in order, cleanly, and verify your work.

### Task 1: The Vault CLI Blocker (Debut Blocker)
*   **Target:** `src/omega/cli/vault.py` around line 572.
*   **Issue:** There is a stacked/duplicate decorator breaking the CLI.
*   **Action:** Read the file, locate the duplicate decorator, remove it, and verify the CLI loads without crashing.

### Task 2: Create the `export-claude-project` Skill
*   **Target:** `.opencode/skills/export-claude-project/SKILL.md`
*   **Issue:** The Architect needs a fast way to bundle state for Claude.ai Project review.
*   **Action:** Write a bash script or OpenCode skill that concatenates `ACTIVE_SPRINT.json`, the last 50 lines of `PIVOT_LOG.md`, `TASK_REGISTRY.json`, and any user-specified files into a single `CLAUDE_HANDOFF_<date>.md` file.

### Task 3: Create the `council-dispatch` Skill
*   **Target:** `.opencode/skills/council-dispatch/SKILL.md`
*   **Action:** Codify the "Architect's Orchestration Protocol" (Section 4 above) into a formal OpenCode skill so any agent can execute the human's management style on command.

### Task 4: `opencode.db` Self-Mining Script
*   **Target:** `scripts/mine_session_db.py`
*   **Issue:** We have 35M+ tokens of paid frontier reasoning locked in the SQLite DB.
*   **Action:** Write a Python script to extract messages from `opencode.db`. **Crucial:** It must parse the text for the ICS header (`⬡ OMEGA ⬡`) to correctly attribute the model for each chunk of text, ignoring the DB's default model column. Output to JSONL for future DPO training.

## §6. STATE DISCIPLINE
*   **No Ghost Completions:** Do not mark a task `completed` in `TASK_REGISTRY.json` unless you have run a script or `grep` to physically verify the code changes exist on disk.
*   **No Cowboy Coding:** If you encounter a systemic error, log it to `PIVOT_LOG.md` and ask the Architect. Do not rewrite core engine files (`src/omega/core/*`) without explicit permission.

---
*End of Codex. Acknowledge receipt and state your model ID before beginning execution.*