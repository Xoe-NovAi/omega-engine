<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Planner/Executor Architectures with Context Window Differentiation
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-PLANNER-EXECUTOR-CW-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_planner_executor_cw ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **planner/executor architectures** where a large-context planner (64K–1M tokens) delegates to small-context executors (4K–32K tokens). The frontier has converged on **explicit plan-first, execute-later** patterns with **structured plan formats** (DAG/JSON), **context packing for executors**, and **multi-model deployment** (different models per role). Critical finding: The planner writes a plan that fits the executor's context window — not the planner's.

---

## 1. Core Architectural Patterns

### 1.1 Plan-and-Execute vs. ReAct (LangChain Blog, 2024; EmergentMind, 2026)
> **Sources**: [LangChain Plan-and-Execute Agents](https://www.langchain.com/blog/planning-agents), [EmergentMind Planner-Executor](https://www.emergentmind.com/topics/planner-executor-model)

| Aspect | Plan-and-Execute | ReAct |
|--------|------------------|-------|
| Planning | Upfront, explicit | Step-by-step, implicit |
| Visibility | Full plan visible before execution | No visibility into future steps |
| Token Efficiency | Higher (plan once, execute many) | Lower (full context each step) |
| Adaptability | Replanning after plan completion | Continuous adaptation |
| Model Flexibility | **Can use different models per node** | Single model |
| Debugging | Easy (inspect plan and execution) | Harder (no explicit strategy) |

**Key insight**: "This agent design can be more effective than a naive plan-and-execute agent since each task can have only the required context (its input and variable values)."

### 1.2 LLMCompiler — Parallel DAG Execution (LangChain Blog, 2024)
> **Source**: [LangChain Plan-and-Execute Agents](https://www.langchain.com/blog/planning-agents)

LLMCompiler components:
1. **Planner** — Streams a DAG of tasks. Each task contains: tool, arguments, list of dependencies
2. **Task Fetching Unit** — Schedules and executes tasks, accepts stream of tasks
3. **Executor** — Runs tasks in parallel respecting dependencies

> "LLMCompiler is designed to further increase the speed of task execution beyond plan-and-execute and ReWOO agents, and even beyond OpenAI's parallel tool calling."

### 1.3 Hierarchical Decomposition Variants (EmergentMind, 2026)
> **Source**: [Planner-Executor Multi-Agent Architecture](https://www.emergentmind.com/topics/planner-executor-multi-agent-architecture)

Four decomposition algorithms in production:

| Algorithm | Structure | Best For |
|-----------|-----------|----------|
| **HTN (Hierarchical Task Networks)** | Recursive split to primitives, topological sort | General planning |
| **LEG (Layer Execution Graph)** | DAG with synchronization barriers, parallel tracks | Scientific workflows |
| **DAG (Directed Acyclic Graph)** | Sub-queries with dependencies, parallel optimization | RAG, search systems |
| **ROMA (Recursive Open Meta-Agent)** | Dynamic decide: decompose further or delegate | Bounded context windows |

**ROMA key insight**: "Maintains context windows by aggregating only summaries upward" — each node decides whether to further decompose or delegate to executor.

---

## 2. Context Window Differentiation Strategies

### 2.1 Cloud Planner + Local Executor (GrandLinux/Saeree ERP, 2026-05-24)
> **Source**: [Claude Plans + Local AI Executes](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)

**The pattern**: Claude (cloud, 200K–1M context) plans → Local AI (32K–128K context) executes

```
Claude reads 8 files → designs plan naming edits per file → sends ~2,000 token plan to Local AI
Local AI does real editing (hundreds of thousands of tokens) → returns diff
Claude reads diff (~5,000 tokens) → approves or requests revisions
Net: Claude burned ~10,000 tokens instead of ~150,000
```

**Executor model requirements (2026 verified)**:
| Model | Params | VRAM (4-bit) | Fit |
|-------|--------|--------------|-----|
| Qwen2.5-Coder-7B | 7B | ~6GB | Autocomplete only — instruction following too weak |
| Qwen2.5-Coder-14B | 14B | ~10GB | Single-file refactors — floor for usable executor |
| **Qwen2.5-Coder-32B** | **32B** | **~22GB** | **Multi-file + tool use — sweet spot** |
| DeepSeek-V3 | 671B (MoE) | ~380GB | Enterprise — multi-GPU cluster |
| Llama 3.3 70B | 70B | ~42GB | General-purpose — very strong instruction following |

### 2.2 Multi-Model LangGraph Implementation (LocalGraph Tutorial, 2025)
> **Source**: [Plan-and-Execute Pattern | LocalGraph](https://abhinaavramesh.github.io/langgraph-ollama-tutorial/tutorials/advanced/21-plan-and-execute.html)

```python
# Large model for strategic planning
planner_llm = ChatOllama(model="llama3.1:70b")

# Small, fast model for execution
executor_llm = ChatOllama(model="llama3.2:3b")

# Large model for replanning decisions
replanner_llm = ChatOllama(model="llama3.1:70b")

workflow.add_node("planner", create_planner_node(planner_llm))
workflow.add_node("executor", create_executor_node(executor_llm, tools))
workflow.add_node("replanner", create_replanner_node(replanner_llm))
```

**Benefits**: Strategic decisions use powerful models; routine execution uses fast models; cost and latency optimization.

### 2.3 Model Size vs. Plan Complexity (LocalGraph, 2025)
> **Source**: [Plan-and-Execute Pattern | LocalGraph](https://abhinaavramesh.github.io/langgraph-ollama-tutorial/tutorials/advanced/21-plan-and-execute.html)

| Model Size | Max Plan Steps | Use Case |
|------------|----------------|----------|
| 3B–8B | 3–4 | Simple multi-step tasks |
| 13B–34B | 4–6 | Moderate complexity |
| **70B+** | **5–7** | **Complex reasoning, strategic planning** |

---

## 3. Plan Formats & Contracts

### 3.1 Structured Plan Schema (AgenticPrep.ai, 2026-06-12)
> **Source**: [Planner-Executor Complete Guide](https://agenticprep.ai/topics/planner-executor)

The plan becomes a **first-class artifact** — you can read it, diff it, edit it, gate it, and parallelize it before a single side effect fires.

**Plan formats in production**:

| Format | Structure | Used By |
|--------|-----------|---------|
| **Linear JSON** | `[{step, tool, args, success_criteria}]` | Simple pipelines |
| **DAG/Graph** | `{nodes: [{id, tool, args, deps}], edges: []}` | LLMCompiler, LangGraph |
| **YAML Spec** | Structured spec with inputs/outputs/constraints | MetaGPT, Deep Agents |
| **Natural Language + Schema** | Human-readable steps + machine-readable contract | Cline, Anthropic Agents |

### 3.2 Cline's Gold Standard Implementation (AI Agent Handbook, 2026)
> **Source**: [COMPREHENSIVE_AGENT_ENGINEERING_GUIDE_2026.md](https://github.com/vasilyevdm/ai-agent-handbook/blob/main/COMPREHENSIVE_AGENT_ENGINEERING_GUIDE_2026.md)

```python
def plan_and_execute(task: str):
    # Phase 1: Plan (no tool execution)
    plan = planner_llm.generate(
        system="You are a planner. Analyze the task and create a step-by-step plan. Do NOT execute anything.",
        user=task
    )

    # Phase 2: Execute (follow the plan)
    for step in plan.steps:
        result = executor_llm.generate(
            system="You are an executor. Complete the given step using tools.",
            user=f"Plan context: {plan}\nCurrent step: {step}"
        )
        # ... execute tools from result
```

**Cline's two modes**:
- **Plan Mode**: AI analyzes requirements, reads codebase, builds step-by-step plan. No modifications. User reviews plan.
- **Act Mode**: AI executes the plan, editing files and running commands. Human approval at each step.

### 3.3 Structured Task Contracts (Bharat Bhavnasi, 2026-03-12)
> **Source**: [Deep Agents: Planner/Executor/Critic](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)

> "The most common failure mode: the planner writes a task description that's clear to the planner and ambiguous to the executor. The executor does the wrong thing. The critic approves the wrong thing. The plan is wrong from there."

**Fix**: Structured task contracts — planner's output isn't a sentence, it's a schema with:
- Explicit inputs
- Expected outputs
- Success criteria
- Tool allowlist for this step

---

## 4. Context Packing for Executors

### 4.1 Executor Receives Only Task-Relevant Context (EmergentMind, 2026)
> **Source**: [Planner-Executor Multi-Agent Architecture](https://www.emergentmind.com/topics/planner-executor-multi-agent-architecture)

Executors are instantiated per subtask with:
- **System Prompt Templates** — Domain-specific framing ("You are an agent tasked with extracting alloy compositions…")
- **Tailored Toolsets** — Minimal subset of tools required for designated subtask
- **I/O Contract** — Unique input/output specification per subtask

> "Executors are agnostic to memory beyond their immediate context, and their stateless execution ensures scalability."

### 4.2 Context Budget Management (Solana Garden, 2026-06-10)
> **Source**: [LLM Plan-and-Execute Explained](https://solana.garden/guides/llm-plan-and-execute-explained)

Key rules:
- "Split until each step fits one executor context window"
- "Full log forwarding — passing raw tool JSON from every prior step recreates context bloat. Summarize aggressively."
- "No replan without cause — but replan when executor discovers new information"

### 4.3 Semi-Centralized Protocol (EmergentMind, 2025)
> **Source**: [Planner-Executor Multi-Agent Architecture](https://www.emergentmind.com/topics/planner-executor-multi-agent-architecture)

> "Semi-centralized protocols (as in Anemoi) dramatically reduce communication cost, shrinking redundant context passing by up to 75% compared to centralized prompt-passing designs, while improving accuracy by up to 9.09 percentage points over centralized baselines."

---

## 5. Communication Protocols & State Management

### 5.1 Shared State as Connective Tissue (Bharat Bhavnasi, 2026)
> **Source**: [Deep Agents](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)

> "Shared state — a todo list and a scratchpad — is the connective tissue. None of the three roles holds the full plan in its context window; the plan lives in the state."

**State schema**:
```python
class PlanExecuteState(TypedDict):
    input: str
    plan: list[Step]           # Structured plan
    past_steps: list[Tuple[Step, str]]  # (step, result)
    current_step: int
    needs_replanning: bool
```

### 5.2 Replanning Triggers (LangGraph, LocalGraph)
- Executor fails a step (tool error, validation failure)
- Executor discovers new information requiring plan change
- Critic rejects output with specific feedback
- Max retry budget exceeded

---

## 6. Production Frameworks & Implementations

| Framework | Planner | Executor | Replanner | Plan Format | Multi-Model |
|-----------|---------|----------|-----------|-------------|-------------|
| **LangGraph** | LLM node | ReAct agent | Optional LLM node | DAG (TypedDict) | ✅ Native |
| **Claude Agent SDK** | Claude | Sub-agents | Built-in | JSON + natural language | ✅ |
| **MetaGPT** | PM/Architect | Engineers | QA Engineer | SOP (YAML) | ❌ Single model |
| **Cline** | Plan Mode | Act Mode | Human gate | Markdown plan | ❌ Single model |
| **Deep Agents (LangChain)** | Planner | Executor | Critic | Todo list + scratchpad | ✅ |
| **LLMCompiler** | DAG streamer | Task Fetching Unit | N/A | DAG | ✅ |
| **ROMA** | Recursive meta-agent | Dynamic delegation | Self | Hierarchical summaries | ✅ |

---

## 7. Critical Failure Modes & Mitigations

### 7.1 Plan-Execute Mismatch (GrandLinux, 2026)
> **Source**: [Claude Plans + Local AI Executes](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)

**Problem**: Claude writes perfect plan, Local AI reads incompletely, follows halfway, improvises.
**Root cause**: Executor model isn't strong enough.
**Fix**: Verify every batch, retry when diff doesn't match plan.

### 7.2 Context Drift Between Models (GrandLinux, 2026)
**Problem**: Planner has 200K–1M context, executor has 32K–128K. Long plan + code reading = truncation.
**Mitigation**: Keep plans short, split sub-tasks small, summarize files.

### 7.3 Debugging Complexity (GrandLinux, 2026)
**Problem**: Output wrong → was plan wrong (planner) or execution wrong (executor)?
**Fix**: Centralized logging, replay infrastructure, full-stack observability.

### 7.4 Cross-Role Miscommunication (Bharat, 2026)
**Problem**: Planner writes task clear to planner, ambiguous to executor.
**Fix**: Structured task contracts with explicit inputs, outputs, success criteria.

---

## 8. Recommendations for Omega Engine

### 8.1 Adopt LangGraph as Orchestration Backbone
- Native multi-model support per node
- DAG-based plan format with typed state
- Built-in replanning via conditional edges
- Checkpointing/resumability for long runs

### 8.2 Implement Context Window-Aware Plan Generation
```python
class ContextAwarePlanner:
    def __init__(self, executor_context_window: int = 32768):
        self.executor_budget = executor_context_window
    
    def generate_plan(self, task: str, available_context: dict) -> Plan:
        # Planner uses full context (64K+)
        # But generates steps that each fit executor_budget
        plan = self.llm.generate(
            system=f"Create a plan where EACH STEP fits in {self.executor_budget} tokens. "
                   f"Include only task-relevant context per step. "
                   f"Output structured DAG with explicit inputs/outputs per step.",
            user=task
        )
        return self.validate_plan_fits_executor(plan)
```

### 8.3 Executor Context Packing Protocol
```python
def pack_executor_context(step: Step, plan: Plan, knowledge_base: KnowledgeBase) -> str:
    # Only what the executor needs for THIS step
    context = f"""
    ROLE: {step.executor_role}
    TASK: {step.description}
    INPUTS: {step.inputs}
    SUCCESS_CRITERIA: {step.success_criteria}
    ALLOWED_TOOLS: {step.allowed_tools}
    RELEVANT_KNOWLEDGE: {knowledge_base.retrieve(step.query, budget=step.context_budget)}
    """
    return compress_if_needed(context, step.context_budget)
```

### 8.4 Model Assignment for Omega (16GB RAM, CPU-only)
| Role | Model | Quantization | Context | Rationale |
|------|-------|--------------|---------|-----------|
| **Planner** | Qwen3-14B or Llama-3.1-8B | Q4_K_M | 32K | Strong reasoning, fits 16GB |
| **Executor** | Qwen2.5-Coder-7B | Q4_K_M | 16K | Fast, good instruction following |
| **Critic** | Qwen3-1.7B | Q4_K_M | 8K | Lightweight verification |
| **Replanner** | Same as Planner | Q4_K_M | 32K | Strategic decisions |

### 8.5 Plan Format: Hybrid JSON + Natural Language
```json
{
  "goal": "Refactor authentication module to use JWT",
  "steps": [
    {
      "id": "step_1",
      "description": "Analyze current auth implementation in src/auth/",
      "executor_role": "code_analyst",
      "inputs": {"files": ["src/auth/*.py"]},
      "outputs": {"analysis": "markdown_summary"},
      "success_criteria": "Identifies all token handling, session management, and middleware",
      "allowed_tools": ["read", "grep", "glob"],
      "context_budget": 16384,
      "dependencies": []
    }
  ]
}
```

---

## 9. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | GrandLinux/Saeree ERP (2026-05-24) | Case study | ✅ Direct fetch | Production deployment details, model specs |
| 2 | LangChain Blog (2024-02-13) | Official blog | ✅ Direct fetch | LLMCompiler, Plan-and-Execute patterns |
| 3 | EmergentMind (2026) | Research aggregation | ✅ Direct fetch | Multiple papers cited, HTN/LEG/DAG/ROMA |
| 4 | LocalGraph Tutorial (2025) | Code + tutorial | ✅ Direct fetch | Working LangGraph + Ollama multi-model code |
| 5 | AI Agent Handbook (2026) | GitHub guide | ✅ Direct fetch | Cline implementation details |
| 6 | Bharat Bhavnasi (2026-03-12) | Engineering blog | ✅ Direct fetch | Deep Agents pattern, shared state |
| 7 | AgenticPrep.ai (2026-06-12) | Interview prep | ✅ Direct fetch | Plan formats, human gate |
| 8 | Solana Garden (2026-06-10) | Technical guide | ✅ Direct fetch | Context packing rules |
| 9 | Anthropic Engineering (2024) | Official blog | ⚠️ Cited by GrandLinux | Orchestrator-workers pattern |
| 10 | MetaGPT (2023) | arXiv:2308.00352 | ⚠️ Cited by multiple | SOP pattern, role specialization |

---

## 10. Unverified Claims (Flagged)

- **75% context passing reduction** (Anemoi semi-centralized) — single paper claim, no independent benchmark
- **9.09 pp accuracy improvement** — same source, needs replication
- **Qwen2.5-Coder-32B as "sweet spot"** — GrandLinux claim, no comparative benchmark shown
- **85% cost savings from hierarchical prompting** — LocalAIMaster, no methodology
- **ROMA "maintains context windows by aggregating summaries upward"** — paper claim, no open implementation found

---

*End of R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
