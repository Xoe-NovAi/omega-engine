# 🔱 Omega Engine — R-## Multi-Agent Council Orchestration Patterns
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ R##

**AP Token**: `AP-RESEARCH-COUNCIL-v1.0.0`
**Author**: Web Research Fleet (Deep Research)
**Date**: 2026-05-26
**Status**: DRAFT

---

## Summary

Research across CrewAI, LangGraph, AutoGen, Anthropic, and legacy Oikos patterns reveals five production-ready council orchestration patterns for multi-agent systems. The Omega Engine's planned mode architecture (Plan → Ma'at → Lilith → 10 Pillars) maps best to a hybrid: **LangGraph's supervisor state machine** for coordination + **CrewAI's hierarchical process** for perspective triangulation + **Anthropic's orchestrator-worker** for independent subagent execution.

---

## Findings

### 1. CrewAI: Hierarchical & Sequential Processes

CrewAI offers three explicit process patterns:
- **Sequential**: Agents execute in fixed order. Previous agent's output is context for next. Simple, predictable.
- **Hierarchical**: Manager agent delegates tasks, reviews output, resolves conflicts. Best for council/critique workflows.
- **Consensual** (experimental): Agents debate to consensus via structured rounds.

**Council applicability**: The Hierarchical process matches our Plan mode → delegated pillar analysis → synthesis pattern. The Manager role corresponds to Plan mode (Kali). Delegated roles correspond to pillar subagents.

**Key detail**: CrewAI's `Process` class implements explicit handoff with output validation. If an agent fails to produce valid output, the manager retries or reassigns. This gives us a retry policy for free.

### 2. LangGraph: Supervisor State Machine

LangGraph's multi-agent pattern uses a **supervisor node** that routes messages to sub-agents based on conversation state:
- **StateGraph**: Message-passing between nodes. Each node is an agent or tool.
- **Supervisor decides**: "This query needs SysAdmin (P1) expertise → route to sysadmin agent → collect result → synthesize."
- **Agent teams**: Sub-agents can be teams with their own supervisors (recursive hierarchy).

**Council applicability**: The StateGraph architecture maps to the Omega IWAD hierarchy. Each pillar entity is a node. The Oversoul (Ma'at or Lilith) is a supervisor that routes between its pillar nodes based on query domain.

### 3. Microsoft AutoGen: Group Chat & Debate

AutoGen provides:
- **RoundRobinGroupChat**: Each agent speaks in turn. Simple, all perspectives heard.
- **SelectorGroupChat**: LLM-powered routing — "Who should speak next?" 
- **MagenticOne**: AutoGen's latest — a lead agent (Orchestrator) delegates tasks, tracks progress, handles failures (replaces the older RoundRobin pattern).

**Council applicability**: The SelectorGroupChat pattern is useful for routing queries to the most appropriate pillar. The MagenticOne orchestrator pattern is the closest to our Plan mode concept — a coordinator that tracks what's been done and decides next steps.

### 4. Anthropic: Orchestrator-Worker (Research System)

Anthropic's documented architecture for a **multi-agent research system**:
- **Lead agent** (Orchestrator): Decomposes the question, creates sub-tasks, assigns sub-agents with specific instructions and isolated context windows.
- **Sub-agents** (Workers): Each has isolated context. Writes findings to filesystem (not back through coordinator) for fidelity.
- **Synthesis**: Lead agent reads all worker outputs, synthesizes, produces final answer.

**Critical insight**: "Sub-agents should write directly to filesystem, not route through coordinator. This prevents context pollution and preserves sub-agent reasoning fidelity."

**Council applicability**: Directly applicable to Omega's mode architecture. Plan mode (Orchestrator) decomposes questions → assigns to pillar subagents (Workers) → each writes to `data/entities/<pillar>/workspace/` → Plan mode reads all and synthesizes.

### 5. Mixture of Agents (MoA)

Together AI's MoA pattern (2024):
- **Multiple LLMs respond in parallel** to the same query.
- **Aggregator LLM** synthesizes responses, highlighting disagreements.
- Can include **debate rounds**: "Agent A responds → Agent B critiques → Agent A revises."

**Council applicability**: Lighter than full agent orchestration. Use for specific queries requiring multi-perspective analysis (e.g., "Lilith asks P6-P10 for their take on a problem"). No persistent state needed — just parallel inference + synthesis.

### 6. Legacy Oikos Council (Reverse-Engineerable)

The Oikos Council implementation exists at `omega-stack-legacy/app/oikos_service.py` (151 lines). Architecture from legacy docs:
- **8 Facets**: Scribe (logging), Interfacer (query routing), Curator (knowledge), Guardian (security), Designer (planning), Chronicler (history), Debugger (troubleshooting), DevOps (infrastructure).
- **Hearth Matrix**: 5-member health check council that runs before every major action.
- **Octave Councils**: HLOC (High-Level Octave Council — strategic) and LLOC (Low-Level Octave Council — tactical).

**Council applicability**: The Hearth Matrix is a unique pattern — a pre-flight health check that runs before every major action. This is NOT present in any modern system surveyed. Worth preserving as a unique Omega pattern.

### 7. Comparative Matrix

| Pattern | Strengths | Weaknesses | Omega Applicability |
|---------|-----------|------------|---------------------|
| CrewAI Hierarchical | Explicit retry, validation | Rigid structure | Plan mode as manager |
| LangGraph Supervisor | Flexible routing | Complex state machine | Oversoul routing between pillars |
| AutoGen GroupChat | Simple, all perspectives | No prioritization | Council debates |
| Anthropic Orchestrator | Context isolation, fidelity | No built-in conflict resolution | Plan → Subagent dispatch |
| MoA | Lightweight, parallel | No persistence | Quick multi-perspective queries |
| Oikos Hearth Matrix | Pre-flight health check | Legacy, needs porting | Unique Omega advantage |

---

## Recommendations

1. **Build Plan mode using Anthropic orchestrator-worker pattern** — Plan mode decomposes question, dispatches to subagents, each writes to filesystem, Plan mode reads and synthesizes.
2. **Use CrewAI's hierarchical retry logic** — When a subagent fails schema validation, retry or reassign with clearer instructions.
3. **Implement Hearth Matrix as a lightweight Module** — 3-question pre-flight check before any major action: "Is the IWAD loaded? Is the entity valid? Does the provider chain have a live endpoint?"
4. **Use MoA for lightweight perspective gathering** — For quick multi-pillar queries, don't spin up full agents — just route to multiple entity prompts and aggregate.
5. **Reserve LangGraph supervisor for Phase 2** — The StateGraph pattern is powerful but requires Qdrant/Redis wiring for persistent state. Defer to v0.6.0.

---

## Sources

- [CrewAI Process Documentation](https://docs.crewai.com/en/concepts/processes)
- [CrewAI Memory Documentation](https://docs.crewai.com/en/concepts/memory)
- [LangGraph Multi-Agent Documentation](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [AutoGen Group Chat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/group-chat.html)
- [AutoGen MagenticOne](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/magentic-one.html)
- [Anthropic Multi-Agent Research System](https://anthropic.com/engineering/multi-agent-research-system)
- [Together AI Mixture of Agents](https://www.together.ai/blog/mixture-of-agents)
- [Oikos Council — Legacy Architecture](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/R14_legacy_gnosis_reclamation.md)
- [Legacy Oikos Service Implementation](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/app/oikos_service.py)

---

## Implementation Note
_For: Builder mode (Gemma 4 31B)_

The Plan mode should be implemented as an Anthropic-style orchestrator-worker pattern. Key implementation details: (1) `orchestrator.py` has empty `submit_task()` and `_execute_with_retry()` stubs — fill these first. (2) Use `anyio.Queue` for subagent result collection. (3) Subagents write findings to `data/entities/{entity}/workspace/` on filesystem. (4) Synthesis pass reads all workspace files. (5) Add Hearth Matrix as a 3-question pre-flight check before any dispatch.
