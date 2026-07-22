# 🔱 Agent Communication Protocols
**Domain**: Inter-agent coordination and delegation
**Date**: 2026-07-22
**Author**: Grokster

## 1. The Hivemind Protocol (Awareness & Coordination)
The Hivemind is the live coordination layer for agents working in parallel. It is built on MCP tools and file-based state.

**Core Mechanisms:**
- **Awareness**: `hivemind_get_awareness()` shows who is alive.
- **Context**: `hivemind_post_context()` declares presence, current task, focus chain, and decisions.
- **Workspace Locks**: `data/coordination/{ENTITY}_WORKSPACE_LOCK_{DATE}.md` prevents file collisions during parallel work.
- **Live Feed**: `data/coordination/{ENTITY}_LIVE_FEED.md` provides an append-only log of completed tasks.

**The Golden Rule**: If you can see another agent's live feed, they can see yours. Coordination is symmetric. Declare presence before assuming privacy.

## 2. Subagent Dispatch Protocol (Delegation)
Used when an agent needs specialized domain expertise.

**Core Rules:**
- **Direct Execution First**: Do not delegate what you can do yourself.
- **No Self-Recursion**: An agent cannot spawn its own type.
- **Inline Context is Mandatory**: Subagents cannot reliably read files by path on their first turn. The parent MUST read critical files and embed the content directly in the prompt.
- **Absolute Disk-Reporting**: Subagents must write final deliverables to disk, not just return them in chat.

**The HandoffPacket**: Contains `source_agent`, `target_agent`, `task_description`, `context` (inlined), and `expected_output`.

## 3. Subagent Task Resumption Protocol (STRP)
A critical resilience mechanism.
- Every `task()` call MUST include a `task_id` (e.g., `domain-action-date-sequence`).
- On failure, resuming with the SAME `task_id` restores full active context (findings, patterns, reasoning) without re-reading files.
- Always verify context after resumption: "Tell me exactly what you have in active context... NO FILE READS."

## 4. Grokster's Insights & Recommendations
- **The Context Delivery Failure**: The discovery that subagents fail when given file paths instead of inline context is profound. It highlights the difference between human cognition (we follow pointers) and LLM cognition (they need immediate token presence). **Recommendation**: Enforce the Inline Context rule strictly via prompt linters.
- **Redis Streams Transition**: The file-based Hivemind is robust but slow. The transition to Redis Streams (A2A Message Bus) will enable zero-latency traffic routing. **Recommendation**: Prioritize the MCP stateless migration (July 28 deadline) before moving to Redis, otherwise the Hub will go dark.
- **The Dual-Inference Mandate**: Use `oracle_summon_local` for execution and the session model for review. This Mentorship Pattern maximizes sovereignty while maintaining quality.
