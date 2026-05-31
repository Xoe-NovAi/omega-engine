# 🔱 Sovereign Subagent Fleet — Operational Lessons Compilation
**AP Token**: `AP-SUBAGENT-LESSONS-v1.0.0`
**Status**: CURATED | **Source**: 3+ Fleet Deployments (May 16, 2026)
⬡ OMEGA ⬡ MAAT ⬡ overseer ⬡ trc_ops ⬡ FLEET-LESSONS

---

## §0 Purpose

This document captures the systemic failures, workarounds, and structural improvements discovered during the operation of the subagent fleet across multiple research sprints. These lessons inform how custom agent and subagent instructions should be written going forward.

---

## §1 Observed Failure Patterns

### 1.1 Silent Task Failures
**Observation**: Subagents would complete a task, return a `task_id`, but their output file was never written to disk. The `task_result` block was empty or contained only a confirmation without the actual deliverable.

**Root Cause**: Subagents do not automatically write files unless explicitly instructed at the *end* of their execution. If the prompt says "create a report" but doesn't mandate a specific file path, the agent may return the content in the `task_result` (which gets lost) instead of writing to the filesystem.

**Solution**: Every subagent prompt MUST end with an explicit file-writing directive:
> "You MUST write this deliverable to `docs/research/FILENAME.md`. Confirm in your final message that the file was written."

### 1.2 The "Empty Result" Trap
**Observation**: Some subagents types (`gnosis-analyst`, `general`) would occasionally return empty `task_result` blocks despite the task completing successfully.

**Root Cause**: The subagent's communication channel back to the caller is unreliable for large payloads or complex outputs. The agent may consider the task "complete" the moment it writes the file, without returning a summary.

**Solution**: 
- Always verify file creation with `glob` or `read` after task completion.
- Use `architect` subagent for design specs (they reliably write files).
- Use `scribe` for documentation (they reliably write files and return confirmation).

### 1.3 Context Erosion Across Subagent Calls
**Observation**: When a subagent is spawned from a primary mode, it starts with zero context about the parent session's goals, active entity, or current `session_gnosis.md`.

**Root Cause**: The `task` tool initializes the subagent with the prompt only. It does not inherit the parent's session state or system prompt.

**Solution**: Every subagent prompt MUST include:
1. A "Connect" directive: "Read the current `session_gnosis.md` to establish context."
2. A "Report Back" directive: "Before terminating, append your key finding to `session_gnosis.md`."

---

## §2 Structural Improvements for Agent Definitions

### 2.1 Permission Boundaries
**Observation**: Subagents would fail silently when they lacked permission to write to a target directory.

**Fix**: Every `.opencode/agents/*.md` file in the Omega Engine must include:
```yaml
permission:
  read: allow
  glob: allow
  grep: allow
  bash: ask
  edit: ask
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
```

### 2.2 The "Cognitive Tier" Field
**Observation**: Subagents without a cognitive tier designation would attempt T3-level reasoning on T1-level tasks, wasting context and compute.

**Fix**: Every agent definition should include a `tier` field:
```yaml
tier: "T2"  # T1: Reflex, T2: Reason, T3: Gnosis
```
This allows the `ModelGateway` to route to the appropriate model.

### 2.3 The "Sovereign Mandate" Block
**Observation**: Subagents designed for generic tasks (like `explore` or `general`) lacked project-specific constraints, causing them to suggest non-sovereign solutions (e.g., cloud dependencies).

**Fix**: Every Omega Engine agent definition should include a "Sovereign Mandate" block:
```markdown
## 🛡️ Sovereign Mandate
- Local-first: No hard dependencies on cloud APIs.
- Zero telemetry: Do not suggest analytics, tracking, or external logging.
- YAML persistence: Prefer YAML over databases for entity config.
- AnyIO compliance: Use `anyio` not `asyncio`.
```

---

## §3 Recommendations for Custom Agent/Subagent Instructions

1. **Always end with a file path**: Every agent prompt should explicitly name the file it must produce. Never rely on the `task_result` block for critical data.

2. **Mandate a "Connect" step**: Subagents must read the `session_gnosis.md` before starting and write to it before ending.

3. **Include a "Failure Log"**: Add a directive: "If you encounter a blocker, document it in a 'Lessons Learned' section at the end of your deliverable. Do not silently abort."

4. **Use `architect` for Design, `scribe` for Docs, `general` for Exploration**: Route subagent types to their strengths.

5. **Verification Loop**: After spawning a subagent, always run a `glob` check to confirm the file was created before proceeding.