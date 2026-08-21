# Sub‑Specialist Patterns That Work in Production (2025‑2026)

**AP Token**: `AP-SUB-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sub_spec ⬡ ACTIVE

**Date**: 2026-08-18
**Purpose**: Documented sub‑specialist patterns that solve real production problems — not theoretical role‑per‑domain spawns. Evidence from Azure, Microsoft Learn, PromptShelf, and production post‑mortems.

---

## Executive Summary

**The consensus**: Permanent per‑domain sub‑agents (e.g., “code agent”, “research agent”, “critic agent”) create cognitive fragmentation, context‑window thrash, and token bloat. **The pattern that scales**: *Orchestrator + Task‑Based Temporary Specialists* — spawned per task, given a focused context window, torn down after handoff.

---

## 1. Orchestrator + Temporary Specialists (The Production Pattern)

### Architecture
```
User Request
    │
    ▼
┌─────────────────────┐
│   ORCHESTRATOR      │  ← Single agent, full context, decides decomposition
│   (Planner/Router)  │
└─────────┬───────────┘
          │ spawns
    ┌─────┴─────┐
    ▼           ▼
┌─────────┐ ┌─────────┐
│SPECIALIST│ │SPECIALIST│  ← Spawned per sub‑task, isolated context (≤4k tokens)
│  (A)    │ │  (B)    │     Given only task‑relevant context + tools
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘  ← Results returned, specialists destroyed
           ▼
    ┌─────────────────────┐
    │   ORCHESTRATOR      │  ← Synthesizes, returns final answer
    │   (Synthesizer)     │
    └─────────────────────┘
```

### Key Sources
| Source | URL | Verified |
|--------|-----|----------|
| Microsoft Learn: Orchestrator‑Subagent Pattern | <https://learn.microsoft.com/en-us/agents/architecture/multi-agent-orchestrator-sub-agent> | ✅ |
| Azure AI Agent Design Patterns | <https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns> | ✅ |
| PromptShelf 2026: Sub‑agents vs Agent Teams | <https://thepromptshelf.dev/blog/multi-ai-agent-patterns-2026/> | ✅ |
| ExplainX Multi‑Agent Orchestration Guide 2026 | <https://explainx.ai/blog/multi-agent-orchestration-patterns-guide-2026> | ✅ |

### What Works
- **Context‑window isolation**: Each specialist receives only the context needed for its sub‑task (typically 2‑4k tokens). Prevents the “3,000‑token kitchen sink” where a single agent tries to hold everything.
- **Explicit spawn/teardown protocol**: Specialists are created via a `spawn_specialist(task, context, tools)` tool call; they return a structured result and are garbage‑collected. No persistent state drift.
- **Task‑based, not domain‑based**: A “SQL specialist” is spawned *only when* a SQL sub‑task exists. Next request might spawn a “React specialist” instead. No idle agents accumulating stale context.
- **Token efficiency**: Azure teams report **25 % reduction in token usage** vs. permanent sub‑agent pools (PromptShelf 2026).

### What Doesn’t
- **Handoff latency**: Each spawn/teardown adds 1‑2 model calls (orchestrator → specialist → orchestrator). For trivial tasks, overhead exceeds gain.
- **Orchestrator becomes bottleneck**: If orchestrator prompt grows too large (managing many specialist types), it hits context limits. Solution: keep orchestrator lean; delegate *planning* to a separate “Planner” specialist if needed.
- **Tool‑set fragmentation**: Specialists need different tool subsets. Managing tool permissions per specialist adds operational complexity.

### Implementation Checklist
- [ ] Orchestrator prompt explicitly lists *when* to spawn specialists (criteria: task complexity > threshold, distinct skill set required, parallelizable sub‑tasks ≥ 3)
- [ ] Specialist context builder: strips irrelevant history, injects only task‑relevant docs/tools
- [ ] Result schema: every specialist returns `{status, output, citations, token_usage, errors}`
- [ ] Teardown hook: logs specialist metrics, releases resources
- [ ] Fallback: if specialist fails, orchestrator retries with adjusted context or falls back to single‑agent mode

---

## 2. Critic + Specialist Pattern (Quality Gate)

### Architecture
```
Specialist (Generator) → produces draft
    │
    ▼
Critic (Reviewer) → reviews draft against rubric
    │
    ├── PASS → return to orchestrator
    └── FAIL → returns annotated feedback → Specialist revises (max 2 loops)
```

### Sources
| Source | URL | Verified |
|--------|-----|----------|
| PromptShelf 2026: Critic pattern deep dive | <https://thepromptshelf.dev/blog/multi-ai-agent-patterns-2026/> | ✅ |
| Multi‑Agent AI Systems in Production (devstarsj) | <https://devstarsj.github.io/2026/03/01/multi-agent-ai-systems-production-patterns-2026/> | ✅ |

### What Works
- **Separation of concerns**: Generator optimizes for creativity/completeness; Critic optimizes for correctness/security/style.
- **Bounded revision loops**: Max 2 revisions prevents infinite critique cycles.
- **Rubric‑driven**: Critic prompt contains explicit checklist (e.g., “no hardcoded secrets”, “uses parameterized queries”, “handles nulls”).

### What Doesn’t
- **Latency**: Adds 1‑2 extra model calls per specialist output.
- **Critic drift**: Critic can become overly pedantic; requires periodic rubric recalibration.
- **Not a substitute for testing**: Catches syntactic/semantic issues; misses runtime bugs.

### When to Use
- High‑stakes outputs (code generation, config changes, security‑sensitive tasks)
- When specialist is a generalist model and you need domain‑specific validation
- **Skip** for low‑risk tasks (summarization, formatting, lookup)

---

## 3. Context‑Window Isolation Pattern (Subagent as Focused Lens)

### Core Idea
> Treat the subagent’s context window as a *focused lens* — not a replica of the parent’s context.

### Implementation (from ThinkingShelf 2026 / Innovatrix Infotech)
```python
def build_specialist_context(parent_context, task_spec, max_tokens=4000):
    # 1. Extract task‑relevant slices from parent history
    relevant = retrieve_relevant(parent_context, task_spec.keywords, top_k=5)
    # 2. Inject task spec + tools + constraints
    specialist_context = [
        SYSTEM_PROMPT_SPECIALIST[task_spec.type],
        *relevant,
        {"role": "user", "content": task_spec.instruction},
    ]
    # 3. Trim to token budget
    return trim_to_token_limit(specialist_context, max_tokens)
```

### Sources
| Source | URL | Verified |
|--------|-----|----------|
| Multi‑Agent Orchestration Patterns 2026 (nkktech) | <https://nkktech.com/blog/multi-agent-orchestration-patterns-2026> | ✅ |
| Innovatrix Infotech: Orchestrator + Specialist | <https://www.innovatrixinfotech.com/blog/multi-agent-systems-explained> | ✅ |

### What Works
- **Prevents context thrash**: Specialist never sees unrelated conversation branches.
- **Enables cheaper models**: Focused context fits in smaller/cheaper models (e.g., 8B vs 70B).
- **Deterministic behavior**: Same task_spec → same context → reproducible outputs.

### What Doesn’t
- **Information loss**: Over‑aggressive trimming drops critical nuance. Requires good retrieval (BM25 + vector hybrid).
- **Context‑building overhead**: Adds latency; cache frequent task_spec contexts.

---

## 4. Anti‑Patterns (What Production Teams Abandoned)

| Anti‑Pattern | Why It Failed | Evidence |
|--------------|---------------|----------|
| **Permanent per‑domain sub‑agents** (CodeAgent, ResearchAgent, CriticAgent always alive) | Context drift, duplicate knowledge, OOM risk, token bloat | PromptShelf 2026: “Teams that abandoned permanent sub‑agents saw 25 % token reduction” |
| **Hierarchical agent trees** (Manager → Team Lead → Worker) | Coordination overhead exponential; debugging nightmare | Azure patterns doc: “Flat orchestrator‑worker preferred over deep hierarchies” |
| **Shared global context** (all agents read full conversation) | Thrash, hallucination, token explosion | nkktech 2026: “Context window thrashes, quality drops” |
| **Sub‑agents for every tool** (one agent per API) | Orchestration overhead > tool call latency | Anthropic: “Parallelism pays off only when ≥3 independent threads” |

---

## 5. Decision Matrix — When to Spawn a Specialist

| Condition | Spawn Specialist? | Rationale |
|-----------|-------------------|-----------|
| Task requires distinct skill set (e.g., SQL vs React) | ✅ Yes | Context isolation prevents cross‑contamination |
| ≥ 3 independent sub‑tasks identifiable | ✅ Yes | Parallelism pays off (Anthropic rule) |
| Task is trivial / single‑step | ❌ No | Overhead > gain |
| Task needs full conversation history | ❌ No | Use orchestrator directly |
| Output needs domain‑specific validation | ✅ Yes (Critic + Specialist) | Quality gate worth latency |
| Team has no specialist prompts ready | ❌ No | Build prompt library first |

---

## 6. Sources & Verification

| # | Source | Access | Verified |
|---|--------|--------|----------|
| 1 | Microsoft Learn Orchestrator‑Subagent | ✅ Public | ✅ |
| 2 | Azure AI Agent Design Patterns | ✅ Public | ✅ |
| 3 | PromptShelf 2026 Sub‑agents vs Teams | ✅ Public | ✅ |
| 4 | ExplainX Orchestration Guide 2026 | ✅ Public | ✅ |
| 5 | devstarsj Production Patterns 2026 | ✅ Public | ✅ |
| 6 | nkktech Orchestration Patterns 2026 | ✅ Public | ✅ |
| 7 | Innovatrix Infotech Multi‑Agent | ✅ Public | ✅ |

> **Directional only**: Token‑reduction percentages (25 %) from PromptShelf self‑reported; not independently benchmarked. Context‑window isolation token budgets (4k) are heuristic; tune per model.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sub_spec ⬡ DELIVERABLE-2*