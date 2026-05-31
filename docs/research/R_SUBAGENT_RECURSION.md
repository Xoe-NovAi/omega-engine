# 🔱 Omega Engine — Subagent Recursion Analysis
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-SUB-REC

**AP Token**: `AP-RESEARCH-SUB-REC-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-14
**Status**: READY

---

## Summary
Analysis of nested subagent capabilities in OpenCode. Confirms that recursion is technically supported but governed by a permission-based system rather than a depth limit.

## Findings

### Recursion Mechanism
OpenCode implements subagent spawning via the `TaskTool` in `packages/opencode/src/tool/task.ts`. Each spawned subagent is assigned a `parentID`, creating a hierarchical tree of sessions.

### Permission-Based Gating
Recursion is not limited by a hard integer (e.g., `max_depth=5`), but by the `Permission.Ruleset` of the spawned agent.
- If the subagent is granted the `task` permission, it can spawn its own sub-subagents.
- Specialized agents (e.g., `explore`, `scout`) use strict whitelists that omit the `task` permission, making them "leaf nodes" in the hierarchy.

### Data Flow
Subtask results are returned to the parent as tool outputs wrapped in `<task_result>` tags, which the parent agent then synthesizes.

## Recommendations
1. **Dynamic Depth Control**: Implement a `Recursion Guard` in the `OmegaSovereignPlugin`'s `tool.execute.before` hook to prevent infinite loops.
2. **Sovereign Hierarchy**: Use this to implement a tiered intelligence structure:
   - `Root` $\rightarrow$ `Pillar Keeper` $\rightarrow$ `Analyst` $\rightarrow$ `Worker`.
3. **Boundary Enforcement**: Ensure deep-nested subagents inherit the boundaries of their parent to prevent "boundary leaks".

## Sources
- `packages/opencode/src/tool/task.ts`
- `packages/opencode/src/session/prompt.ts`
- `packages/opencode/src/agent/agent.ts`

## Implementation Note
_For: Sovereign Builder_
To implement a depth limit, track the `parentID` chain in `omega-hub` and block the `task` tool once the chain length exceeds a predefined sovereign limit (e.g., 3).
