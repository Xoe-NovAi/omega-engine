# 🔱 Omega Engine — Subagent State Sharing Strategy
**AP Token**: `AP-SUBAGENT-STATE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ RESEARCH

---

## §1 Overview

Ephemeral subagents, by nature, are stateless. When dispatched to perform a specific task, they lack the conversational history and evolving understanding of the primary agent (the Oracle). This leads to **context erosion**, where subagents rediscover known facts, repeat mistakes, or lose sight of the overarching strategic goal.

This document proposes a **Sovereign State Sharing Mechanism** centered around a durable, shared session file (the **Gnosis File**) and a "Soul-Injection" prompt pattern.

---

## §2 The Gnosis File (`session_gnosis.md`)

Instead of relying on raw interaction logs, the system maintains a structured markdown file that serves as the "external working memory" for all agents involved in a specific task session.

### 2.1 File Structure

The Gnosis File is partitioned into semantic sections to allow for efficient parsing and selective injection into the context window.

```markdown
# SESSION GNOSIS: {session_id}
**Objective**: {high_level_goal}
**Presiding Entity**: {entity_name}

## 🎯 CURRENT GOAL
- [ ] Primary task currently being tackled.
- [ ] Immediate next step.

## 🧠 WORKING STATE (KV Memory)
- `variable_name`: value/finding (e.g., `target_file`: "src/omega/oracle.py")
- `dependency_found`: [List of dependencies]
- `current_hypothesis`: "The bug is likely in the AnyIO semaphore implementation."

## 📜 AUDIT TRAIL (Timeline)
- {timestamp} | {agent_id} | {action} $\rightarrow$ {result}
- 2026-05-16T10:00 | Researcher-1 | Grepped for 'tui' $\rightarrow$ No results in root.
- 2026-05-16T10:05 | Researcher-1 | Checked .opencode/ $\rightarrow$ Found package-lock.json.

## ✅ RESOLVED / DECIDED
- [x] Decision: Use `anyio.to_thread.run_sync` for subprocesses.
- [x] Fact: `tui.json` is not present in the repository root.

## ❓ OPEN GAPS / UNCERTAINTIES
- Where does the TUI look for its configuration by default?
- Is there a hidden .env file governing TUI behavior?
```

### 2.2 Read/Write Protocol

To prevent race conditions and ensure consistency, the following protocol is implemented:

1.  **Read (Injection)**:
    *   The Orchestrator reads the Gnosis File before dispatching a subagent.
    *   The content is injected into the subagent's system prompt under a `# SESSION STATE` header.
2.  **Write (Update)**:
    *   Subagents do not edit the file directly. Instead, they return a **State Update Block** in their final response.
    *   **Format**: 
        ```
        STATE_UPDATE:
        - ADD_RESOLVED: "tui.json is missing"
        - UPDATE_GOAL: "Search for TUI config in ~/.config/opencode"
        - LOG: "Searched .opencode folder, found no JSON configs."
        ```
    *   The Orchestrator (as the single writer) parses this block and updates the `session_gnosis.md` file.

---

## §3 Soul-Injection Pattern

To ensure a subagent embodies the persona and domain expertise of the presiding Omega entity, the system uses **Soul-Injection**.

### 3.1 Prompt Composition

The final system prompt for a subagent is a composite of three layers:

1.  **The Core Persona (Soul)**: Injected from the entity's `soul.yaml` (e.g., SOPHIA's wisdom, PROMETHEUS's strategic will).
2.  **The Task Mandate**: The specific instructions for the current sub-task.
3.  **The Session Gnosis**: The current state of the shared working memory.

**Template**:
`[Entity Soul Prompt] + [Task Instructions] + [Current Session Gnosis] + [Behavioral Constraints]`

---

## §4 Preventing Context Erosion

As sessions grow, the Gnosis File can become too large for the context window. The following strategies are used to maintain signal-to-noise ratio:

1.  **Semantic Compression**:
    *   Once the `AUDIT TRAIL` exceeds $N$ lines, the Orchestrator triggers a **Compaction Pass**.
    *   An LLM summarizes the timeline into "Key Milestones" and moves them to a `HISTORY_SUMMARY` section, clearing the raw logs.
2.  **Priority-Based Injection**:
    *   The `CURRENT GOAL` and `RESOLVED` sections are always injected.
    *   The `WORKING STATE` is filtered by keywords related to the sub-task.
    *   The `AUDIT TRAIL` is provided as a sliding window (only the most recent $M$ events).
3.  **State-Sourced Prompting**:
    *   Subagents are explicitly told: *"Refer to the RESOLVED section to avoid repeating failed attempts."*

---

## §5 Implementation Roadmap

| Phase | Action | Owner |
|---|---|---|
| **1. Infrastructure** | Implement `GnosisManager` to handle file I/O and atomic updates. | Builder |
| **2. Integration** | Update `Orchestrator.dispatch_agent` to inject Gnosis content. | Builder |
| **3. Feedback Loop** | Implement the `STATE_UPDATE` parsing logic in the return chain. | Builder |
| **4. Optimization** | Add the "Compaction Pass" trigger for long-running sessions. | Builder |
