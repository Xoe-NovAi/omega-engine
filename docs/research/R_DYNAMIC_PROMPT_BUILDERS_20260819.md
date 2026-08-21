# Dynamic System Prompt Builders / Context-Aware Prompt Composition
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-DYNAMIC-PROMPT-BUILDERS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_dynamic_prompt_builders ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **dynamic system prompt builders** — systems that compose prompts at runtime from modular components based on context window size, task type, available knowledge, and execution mode. The frontier has moved from static templates to **priority-ordered modular assembly** with **cache-aware structure**, **mode-specific variants**, and **provider-specific guidance injection**.

Key finding: The dominant pattern is **Substrate/Projection Architecture** — persistent substrate (all state) vs. ephemeral projection (context window as materialized view). The assembly engine is the critical piece deciding what makes it into each inference call.

---

## 1. Core Architectural Patterns

### 1.1 Substrate/Projection Abstraction (Zylos Research, 2026-03-17)
> **Source**: [Dynamic Context Assembly and Projection Patterns for LLM Agent Runtimes](https://zylos.ai/research/2026-03-17-dynamic-context-assembly-projection-llm-agent-runtimes)

The solution that has emerged across production agent systems is a clean architectural separation:
- **Persistent Substrate** (disk/memory/vector DB): Long-term memory, session history, knowledge base, system configuration, working state
- **Ephemeral Projection** (context window, ~8K–128K tokens): System prompt, relevant knowledge, recent history, current observation
- **Context Assembly Engine**: Decides what makes it into the projection for each inference call

> "The context window is not storage; it is a **projection** — a temporary, purpose-built view assembled from substrate on demand for each inference step."

### 1.2 Priority-Ordered Modular Sections (AgentPatterns.ai, 2026-06-13)
> **Source**: [Dynamic System Prompt Composition](https://agentpatterns.ai/context-engineering/dynamic-system-prompt-composition/)

Each section carries a numeric priority that sets assembly order:

| Priority Range | Functional Tier | Example Content |
|---------------|-----------------|-----------------|
| 10–30 | Core Identity | Agent role, capabilities, boundaries |
| 40–50 | Tool Definitions | Tool schemas, capability declarations |
| 55–65 | Safety & Rules | Style rules, safety constraints |
| 70–80 | Provider-Specific Guidance | Provider-optimized instructions |
| 85–95 | Dynamic Context | Session state, memory injection |

**Key principle**: "The prompt is a view, not storage." Reserve dynamic sections for the end of the priority stack to preserve cache hits.

### 1.3 Three-Layer Dynamic Construction (Hoomanely, 2025-12-04)
> **Source**: [Dynamic Prompt Construction: Building Context-Aware Prompts at Runtime](https://tech.hoomanely.com/dynamic-prompt-construction-building-context-aware-prompts-at-runtime/)

Three distinct layers separated at runtime:
1. **Base Instructions** — Foundational behavior and constraints (tone, safety guardrails)
2. **Situational Context** — Runtime data from user profile, relevant history, retrieved documents
3. **Task Specification** — Immediate goal from user input and application logic

The system assembles these layers dynamically with **context relevance scoring** and **tiered context priority**:
- **Critical** (must include)
- **High Value** (include if space allows)
- **Supplementary** (add opportunistically)

### 1.4 Microsoft Dynamic Context-Aware Prompt Recommendation (Tang et al., 2025)
> **Source**: [arXiv:2506.20815](https://arxiv.org/abs/2506.20815) — Microsoft Research

A modular end-to-end architecture combining:
- **Contextual query processing** — Analyzes query type, intent, complexity
- **Retrieval-augmented knowledge grounding** — Retrieves from hierarchical skill organization
- **Adaptive skill ranking** — Two-stage reasoning with behavioral telemetry
- **Template synthesis** — Predefined + dynamically generated templates with few-shot learning

**Finding**: Lightweight models offer cost efficiency for skill inference but are less effective at generating diverse, contextually rich prompts compared to larger models. Hybrid approach (LM + statistical methods + behavioral telemetry) balances efficiency with quality.

---

## 2. Context Window Adaptation Strategies

### 2.1 Adaptive Instruction Layering (Hoomanely, 2025)
> **Source**: [Dynamic Prompt Construction](https://tech.hoomanely.com/dynamic-prompt-construction-building-context-aware-prompts-at-runtime/)

Different queries need different instruction depth:
- **Light Mode** — Basic role definition + minimal constraints (simple queries)
- **Standard Mode** — Role + context summary + task (typical requests)
- **Deep Mode** — Comprehensive background + multi-step instructions (complex tasks)

System selects mode based on query analysis, user expertise level, expected response complexity.

### 2.2 Hierarchical Prompting / Progressive Context Expansion (LocalAIMaster, 2026-06-21)
> **Source**: [AI Context Windows: 4K vs 128K vs 1M Tokens Explained](https://localaimaster.com/models/context-windows-coding-explained)

Three-phase approach minimizing cost while ensuring results:
```
Level 1: Scoping (4K context)      → "Which files handle user authentication?"
Level 2: Analysis (32K context)    → Load only identified files for deeper analysis
Level 3: Implementation (128K)     → Expand to related files only if needed
```
**Result**: 85% cost savings vs. direct large-context approach.

### 2.3 Context Compression Techniques (LocalAIMaster, 2026)
> **Source**: [AI Context Windows](https://localaimaster.com/models/context-windows-coding-explained)

Pre-process code to reduce token usage:
- Remove comments: **20-30% token savings**
- Strip whitespace: **10-15% savings**
- Remove unused imports: **5-10% savings**
- Minify config files: **40% savings**

---

## 3. Cache-Aware Prompt Structure

### 3.1 Static Content First for Cache Efficiency (AgentPatterns.ai, 2026)
> **Source**: [Dynamic System Prompt Composition](https://agentpatterns.ai/context-engineering/dynamic-system-prompt-composition/)

Anthropic's prompt caching matches prefix up to designated breakpoint. Any change to earlier tokens invalidates cache for everything following.

**Enforcement**: Identity and tool schemas always assembled first → cacheable prefix remains constant even as dynamic sections vary.

### 3.2 Two-Tier Fallback (AgentPatterns.ai, 2026)
If custom section loading fails (corrupted config, missing files), prompt assembly falls back to default sections. Agent remains functional with baseline capabilities rather than failing entirely.

---

## 4. Mode-Specific & Provider-Specific Variants

### 4.1 Execution Mode Variants (AgentPatterns.ai, 2026)
Different modes require different prompt emphasis:
- **Planning Mode** — Omits code quality rules, includes planning heuristics
- **Execution Mode** — Omits planning heuristics, includes code quality rules
- **Normal Mode** — Balanced default

### 4.2 Provider-Specific Guidance (AgentPatterns.ai, 2026)
Conditional blocks inject provider-optimized instructions:
- Claude-specific (extended thinking, prompt caching)
- GPT-specific (structured outputs, function calling)
- Open-source model instructions (llama.cpp, vLLM specific)

Assembly layer picks right blocks based on active model.

---

## 5. Implementation Patterns & Code

### 5.1 Python Assembly Engine (AgentPatterns.ai)
```python
from dataclasses import dataclass, field

@dataclass
class PromptSection:
    priority: int
    content: str
    modes: list[str] = field(default_factory=lambda: ["planning", "execution", "normal"])
    providers: list[str] = field(default_factory=lambda: ["anthropic", "openai"])

def assemble_prompt(sections: list[PromptSection], mode: str, provider: str) -> str:
    enabled = [s for s in sections if mode in s.modes and provider in s.providers]
    enabled.sort(key=lambda s: s.priority)
    return "\n\n".join(s.content for s in enabled)
```

### 5.2 Context Aggregator Pattern (Hoomanely, 2025)
```python
class ContextAggregator:
    def __init__(self):
        self.sources = {
            "user_profile": UserProfileService(),
            "session_history": SessionStore(),
            "knowledge_base": VectorDB(),
            "external_apis": APIClient()
        }
    
    def gather(self, query: str, mode: str) -> dict:
        # Relevance scoring per source
        scored = {}
        for name, source in self.sources.items():
            items = source.retrieve(query)
            scored[name] = self.score_relevance(items, query, mode)
        return self.select_by_priority(scored, mode)
```

---

## 6. Production Systems & Case Studies

| System | Approach | Key Innovation |
|--------|----------|----------------|
| **Claude Code** | CLAUDE.md files loaded at session start | Stable Markdown docs as persistent substrate |
| **Zylos Agent Runtime** | Substrate/Projection with assembly engine | Cache-topology-aware retrieval placement |
| **Microsoft Security Copilot** | Hierarchical skills + behavioral telemetry | Two-stage adaptive skill ranking |
| **AgentPatterns Reference** | Priority-ordered sections + mode toggles | Cache-aware structure enforcement |
| **Hoomanely** | Three-layer + tiered priority + relevance scoring | Temporal/relational awareness in context |

---

## 7. Critical Gaps & Open Problems

1. **No standardized prompt assembly protocol** — Each system invents its own section format, priority scheme, and composition logic
2. **Cache topology awareness is ad-hoc** — Few systems formally model cache breakpoint interactions with dynamic sections
3. **Context window adaptation is heuristic** — No principled method for "strip this section for 4K, keep for 64K"
4. **Provider-specific guidance is brittle** — Model updates break carefully tuned provider blocks
5. **Behavioral telemetry integration is rare** — Microsoft's approach is the only published system using usage data for skill ranking

---

## 8. Recommendations for Omega Engine

### 8.1 Adopt Substrate/Projection as Core Abstraction
- Persistent substrate: `data/entities/{entity}/knowledge/` + `soul.yaml` + session history
- Assembly engine: `src/omega/prompt/builder.py` with priority-ordered sections
- Projection: Built per-inference-call in `Oracle.talk()`

### 8.2 Implement Priority-Ordered Sections (10-95 range)
```python
SECTIONS = [
    PromptSection(10, CORE_IDENTITY),           # Always
    PromptSection(30, TOOL_DEFINITIONS),        # Always
    PromptSection(50, SAFETY_RULES),            # Always
    PromptSection(70, PROVIDER_GUIDANCE),       # Conditional on model
    PromptSection(85, DOMAIN_KNOWLEDGE),        # Dynamic, loaded per task
    PromptSection(90, SESSION_STATE),           # Dynamic, per conversation
    PromptSection(95, TASK_SPECIFICATION),      # Dynamic, per call
]
```

### 8.3 Mode-Specific Variants for Planner/Executor/Critic
- **Planner Mode**: Strategic reasoning, task decomposition, no tool schemas
- **Executor Mode**: Tool schemas, strict output format, no planning heuristics
- **Critic Mode**: Evaluation rubrics, verification tools, no write permissions

### 8.4 Cache-Aware Assembly
- Static prefix (identity + tools + safety) → cached
- Dynamic suffix (domain knowledge + session + task) → varies per call
- Never insert dynamic content before static prefix

### 8.5 Context Window Budget Enforcement
- Tiered priority: Critical → High Value → Supplementary
- When approaching token limit: compress/summarize Supplementary first, then High Value
- Hard stop: Never drop Critical

---

## 9. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | Zylos Research (2026-03-17) | Engineering blog | ✅ Direct fetch | Production patterns from multiple systems |
| 2 | AgentPatterns.ai (2026-06-13) | Pattern library | ✅ Direct fetch | References OPENDEV paper arXiv:2603.05344 |
| 3 | Hoomanely (2025-12-04) | Engineering blog | ✅ Direct fetch | Three-layer architecture, relevance scoring |
| 4 | Microsoft Research (2025-06-25) | arXiv paper | ✅ Direct fetch | arXiv:2506.20815, security domain focus |
| 5 | LocalAIMaster (2026-06-21) | Technical guide | ✅ Direct fetch | Context window tiers, compression techniques |
| 6 | Anthropic Docs (2026-01-23) | Official docs | ✅ GitHub issue | Prompt caching behavior, thinking block stripping |
| 7 | OPENDEV Paper (2026) | arXiv:2603.05344 | ⚠️ Cited by AgentPatterns | Not directly fetched — single source |

---

## 10. Unverified Claims (Flagged)

- **OPENDEV paper specifics** (priority ranges, five functional tiers) — cited by AgentPatterns but not directly verified
- **85% cost savings from hierarchical prompting** — LocalAIMaster claim, no benchmark methodology shown
- **Microsoft system "high performance across multiple model configurations"** — paper claims, no independent replication found

---

*End of R_DYNAMIC_PROMPT_BUILDERS_20260819.md*