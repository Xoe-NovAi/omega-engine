# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-24

---

## §5 Execution Patterns and Decision Rules

### 5.1 Forensic Context — Why Execution Patterns Matter

Before execution patterns were formalized, Omega Engine research suffered from:

- **Pattern mismatch**: Simple tasks routed to expensive deep agents (15× token premium for no benefit)
- **Context pollution**: Sub-agents shared intermediate reasoning states, contaminating each other
- **No autonomy progression**: Fresh research tools launched at full autonomy, failing catastrophically
- **Missing observability**: Token costs spiraled without attribution to specific sub-tasks
- **No recovery strategy**: Failed sub-agents blocked all progress rather than being retried or bypassed

**The Turning Point**: The GEMMA4_WORKHORSE research was executed as a single-loop pattern (~15 iterations over 4 domains) and succeeded because sub-questions were tightly coupled. The WARP_PROXY_POOL research, by contrast, required deep agent pattern with isolated sub-agents for each Docker image investigation. Choosing the right pattern directly determined the research's success.

---

### 5.2 The Deep Agent Decision Rule (Particula 2026)

The single most important guideline for choosing between single-loop and deep agent patterns:

> "**Under ~15-20 steps with tightly coupled work, stay single-loop. Beyond that, with separable exploratory sub-tasks, the deep-agent pattern pays for its 15× token premium.**"

#### Decision Flow Diagram

```
Research Request
    │
    ▼
Estimate Total Steps
    │
    ├── < 15 steps AND tightly coupled?
    │   └── YES → Single-Loop Pattern (1× token cost)
    │            Examples: Ticket classification, field extraction, heritage vetting
    │
    ├── 15-25 steps with SOME separable aspects?
    │   └── YES → Single-Loop with Careful Context Engineering
    │            Examples: Technical specification, single-component design
    │            Key: Apply PART3 rules (compression, scratchpad, isolation thinking)
    │
    ├── > 25 steps with CLEARLY separable sub-tasks?
    │   └── YES → Deep Agent Pattern (15× token cost)
    │            Examples: Multi-component specs, architectural decisions
    │            Architecture: Planner → Sub-agents → Aggregator → Verifier
    │
    ├── High-stakes, irreversible decision?
    │   └── YES → Collaborative Planning (human-in-the-loop)
    │            Examples: Governance policies, versioning strategies, fleet doctrines
    │
    └── UNSURE?
        └── Start single-loop; escalate to deep agent only if context engineering fails
```

---

### 5.3 Single-Loop Agent Pattern

**When to use**: Under ~15-20 steps with tightly coupled work

**Real Omega Example — GEMMA4_WORKHORSE Research**:
- ~15 iterations across 4 domains (Google tier catalog, alternative providers, local fallback, synthesis)
- Tightly coupled: all domains answered the same core question ("what replaces Gemma 4?")
- Executed as single agent with careful context engineering
- Scratchpad rewrites every 5 iterations kept context lean
- Result: actionable deliverable in 2 days, directly informed C-10.5 quota tracker

**Characteristics**:
- Single agent loop: observe → reason → act → observe again
- All context in one window
- Simpler, faster, cheaper, easier to debug
- Token cost: ~1× baseline chat

**Omega Implementation**:
- Single researcher agent execution
- No sub-agent delegation via `task()` tool
- Context engineering within single agent (scratchpad, compression, selection)
- Typical for: focused analysis, estimation, validation, single-component design

**Success Criteria**:
- All sub-questions answerable from a single perspective
- No sub-task requires fundamentally different domain expertise
- Research can be completed in 1-3 hours of wall-clock time

---

### 5.4 Deep Agent Pattern

**When to use**: Beyond ~15-20 steps with separable exploratory sub-tasks

**Real Omega Example — WARP_PROXY_POOL Research**:
- Multiple Docker image investigations (gdtiti, alkaid, ErcinDedeoglu)
- Each investigation required independent source gathering (different GitHub repos, docs)
- Sub-agents could run in parallel without cross-contamination
- Aggregator synthesized per-image patterns into unified "2-service model" solution
- Result: verification that per-instance mdm.xml self-enrollment was a proven pattern

**Characteristics**:
- **4-Pillar Pattern**:
  1. **Planning Tool** (`write_todos`): Author/rewrite structured plan
  2. **Virtual Filesystem**: Offload context to files; keep only references/summaries in window
  3. **Isolated Subagents**: Spawn fresh-context agents for sub-tasks; return only clean results
  4. **Long-Term Memory**: Persistent across runs
- **Architecture**: Planner → parallel isolated sub-agents → aggregator → verifier
- **Token cost**: ~15× baseline chat (but enables complex tasks impossible for single-loop)

**Omega Implementation**:
- Planner agent creates `todo.md` with sub-tasks
- Each sub-task executed by isolated agent via `task()` tool (fresh context)
- Results stored in `data/coordination/research_findings/{job_id}/subtask_*.md`
- Aggregator agent synthesizes subtask results
- Verifier agent checks completeness and quality
- Typical for: complex specifications, architectural decisions, multi-component designs

**Success Criteria**:
- Sub-tasks are genuinely independent (no shared intermediate state needed)
- Each sub-task takes 5-15 steps (would benefit from isolated context)
- Aggregation requires synthesis, not just concatenation

---

### 5.5 Collaborative Planning Pattern

**When to use**: High-stakes, irreversible decisions requiring human judgment

**Characteristics**:
- Agent proposes plan → Human refines → Human approves → Agent executes
- Multiple rounds of human-agent interaction before execution
- Reduces risk of costly misalignment

**Omega Implementation**:
- Agent returns proposed research plan instead of executing
- Human reviews, modifies, approves plan
- Once approved, agent executes the plan
- Typical for: governance policies, strategic decisions, framework designs

---

### 5.6 Execution Pattern Selection Guide

| Job Complexity | Indicators | Pattern | Omega Examples |
|----------------|------------|---------|---------------|
| **Low** | <15 steps, tightly coupled, focused analysis | Single-loop | Heritage vetting, token budget estimation, field extraction |
| **Medium** | 15-25 steps, some separable aspects, technical specification | Single-loop with careful context engineering | GEMMA4_WORKHORSE (4 domains, 15 iterations), C-0.5 Scribe spec |
| **High** | >25 steps, clearly separable sub-tasks, architectural decision | Deep Agent | WARP Proxy Pool (multi-Docker investigation), Soul Schema design |
| **Strategic** | High stakes, irreversible, needs human judgment | Collaborative Planning | Governance policies, versioning, fleet doctrines |

**Note**: The same research can escalate through patterns. Start single-loop, escalate to deep agent only if context engineering proves insufficient. This prevents premature complexity.

---

### 5.7 The Planner's Role in Deep Agents

When using the deep agent pattern, the planner agent follows this protocol:

#### 5.7.1 Planning Tool (`write_todos`)
- **Purpose**: Author and continuously rewrite a structured plan (often `todo.md`)
- **Why it matters**: Counters attention decay in long context windows
- **Mechanism**: Rewrite todo list near end of context on every iteration
- **Effect**: Recites goals back into recent attention, reducing goal drift
- **Bonus**: Provides human-readable trace of agent's intent (invaluable for debugging)

#### 5.7.2 Planner Output Structure
The planner emits a dynamic task list (not static, hardcoded graph):

```yaml
tasks:
  - task_id: "subtask-001"
    goal: "Extract exact llama.cpp GBNF grammar for L1/L2/L3 fields"
    tools: ["webfetch", "searxng_search", "think_tool"]
    output_schema: {type: "object", properties: {grammar: {type: "string"}}}
    confidence_threshold: 8/10  # minimum confidence for acceptance
  - task_id: "subtask-002"
    goal: "Define sliding window chunking algorithm (4k tokens, 500 overlap)"
    tools: ["webfetch", "think_tool"]
    output_schema: {type: "object", properties: {algorithm: {type: "string"}}}
    confidence_threshold: 7/10
  # ... more tasks
```

#### 5.7.3 Planner Responsibilities
1. **Receive raw research query**
2. **Determine independent units of work needed**
3. **Specify what each unit needs to know** (goal, tools, output schema, confidence threshold)
4. **Emit dynamic task list** (scales from 1-step lookup to 12+ parallel investigations)
5. **Do NOT share state with task workers during execution**
6. **Specify confidence thresholds** for each sub-task's acceptance

---

### 5.8 Task Worker Isolation (Critical for Deep Agents)

Each task worker receives **only**:
1. Specific instructions scoped to its subtask
2. Required JSON output schema
3. Access to a set of retrieval tools
4. Confidence threshold for acceptance
5. **Nothing else** — no shared state, no intermediate reasoning chains from other workers

**Why this isolation matters**:
- Prevents context window bloat from other workers' chain-of-thought
- Eliminates cross-contamination of reasoning
- Makes failures easy to attribute to specific sub-tasks
- Each worker's reasoning stays clean and focused

#### 5.8.1 Task Worker Execution
1. Receives: instructions, output schema, available tools, confidence threshold
2. Attempts to satisfy output schema using available tools
3. Uses **progressive content retrieval** (try snippets first, full page only if needed)
4. Returns only clean result matching output schema with confidence score
5. If confidence threshold not met: mark as [LOW CONFIDENCE] with explanation
6. **Never** shares intermediate reasoning, only final output

---

### 5.9 Progressive Content Retrieval (Agentmelt 2026)

Addresses the tension between information completeness and token efficiency:

#### 5.9.1 Two-Stage Decision Process
1. **Stage 1: Snippet-Only Attempt**
   - Use `T1 websearch` (or `T3 SearXNG` for precision)
   - Try to answer sub-question using only search result snippets
   - Many queries answerable from metadata: publication date, domain, headline, first few sentences
   - **Token efficient**: Snippets use far fewer tokens than full pages

2. **Stage 2: Full-Page Fetch (Only if Needed)**
   - Only trigger `T2 webfetch` if snippet-level context is insufficient
   - Model detects when it cannot satisfy output schema with snippets alone
   - **Token expensive**: Reserved for cases where depth genuinely matters
   - **Examples**: Legal texts, complex specifications, primary source verification

**Sovereign Verification**: If a finding is critical (confidence must be ≥8/10), always escalate from snippet to full-page fetch. Snippets alone cannot support high-confidence claims.

---

### 5.10 Structured Output as a First-Class Contract

Every layer of the system emits validated JSON against a schema:

#### 5.10.1 Why Structured Output Matters
- **Consumer research tools** can get away with prose reports
- **API-first research systems** cannot — every layer needs machine-readable output
- **Composability**: Downstream pipelines that need specific formats simply pass that schema at invocation
- **Observability**: Validation, diffing, and aggregation become programmatic (not text parsing)

#### 5.10.2 Implementation Pattern
```python
def run_task_worker(instructions: str, output_schema: dict, context: str, confidence_threshold: float) -> dict:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a research assistant. Always respond with valid JSON matching the provided schema."},
            {"role": "user", "content": f"Task: {instructions}\n\nContext:\n{context}\n\nOutput schema:\n{json.dumps(output_schema)}\n\nMinimum confidence: {confidence_threshold}/10"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

#### 5.10.3 Omega Application
- Task workers return JSON matching their `output_schema`
- Aggregator agent validates and combines JSON results
- Final output validated against required format (e.g., `proposed_lessons.yaml` schema)
- Enables contract tests (M21): `isinstance(result, ExpectedType)`

---

### 5.11 Observability Requirements (Agentmelt 2026)

#### 5.11.1 Essential Metrics to Instrument
At minimum, each node (planner, task worker, aggregator, verifier) must emit:
- Total prompt tokens
- Completion tokens
- Cache hit rate (if applicable)
- Tool call count and types used
- Execution time
- Success/failure status
- Confidence score of result
- Provider used (M22 provenance tracking)

#### 5.11.2 Aggregation for Cost Correlation
- Aggregate metrics at run level
- Correlate query complexity (number of tasks spawned) with cost
- This data directly informs:
  - Rate limits
  - Per-query pricing tiers
  - Timeout thresholds
  - Resource allocation decisions

#### 5.11.3 Critical Insight
> "The reasoning token budget for an observer synthesizing twelve task outputs can be an order of magnitude larger than a single-step query. Discovering this in production billing rather than pre-launch profiling is painful."

**Omega Implementation**:
- Instrument all research job components
- Log metrics to `data/coordination/research_metrics/{job_id}/metrics.json`
- Use for capacity planning and cost optimization

---

### 5.12 Error Recovery and Resilience

#### 5.12.1 Retry Logic
- **Tool level**: Exponential backoff with jitter (max 3 retries)
- **Task level**: Retry failed sub-tasks (max 2 attempts)
- **Job level**: Retry entire research job (max 1 attempt) — then escalate to human

#### 5.12.2 Circuit Breaker Pattern
- Open after 3 consecutive sub-agent timeouts in a run
- Allows aggregator to produce report from partial set
- Prevents cascading failures from blocking all progress

#### 5.12.3 Checkpointing
- Save intermediate results after each major phase
- Enable restart from last checkpoint rather than beginning
- Critical for long-running research jobs

#### 5.12.4 Dead Letter Queue
- Failed sub-tasks go to DLQ for manual inspection
- Prevents lost work and enables root cause analysis
- Format: `data/coordination/research_dlq/{job_id}/subtask_{id}_failure.json`

#### 5.12.5 Partial Completion Protocol (NEW)
When some sub-tasks succeed and others fail:
- Aggregator synthesizes from available results
- Marks missing data as [SUB-TASK FAILED] with reason
- Includes partial results in final deliverable with caveats
- Human reviews failed sub-tasks for potential retry or manual completion

---

### 5.13 The Autonomy Ladder (Mind the Product)

Agent autonomy should escalate gradually based on proven performance:

| Level | Description | When to Advance |
|-------|-------------|-----------------|
| **0: Suggestion Only** | Agent makes recommendations; human executes | Start here for all new research job types |
| **1: Partial Approval** | Agent proposes action; human approves before execution | After 5+ successful suggestions with <10% error rate |
| **2: Full Autonomy** | Agent executes actions autonomously | After 20+ successful actions with <5% error rate |

**Omega Application**:
- New research job types start at Level 0 (suggestion only)
- After demonstrating reliability, advance to Level 1
- After sustained reliability, advance to Level 2 (full autonomy)
- **Never skip levels**; jumping to full autonomy too early causes failures
- Each research job spec includes `autonomy_level` field (0, 1, or 2)

**Failure Scenario**: A new type of heritage vetting research launched at Level 2 would miss critical approval gates. Always start new types at Level 0.

---

### 5.14 Cross-Agent Research Coordination Pattern (NEW — 2026-07-24 Research)

> "Multi-agent collaboration follows an ensemble → blackboard → iterative refinement pipeline. This composable three-phase pipeline unifies breadth, transparency, and depth." (Dova architecture, ACL 2026)

**When to Use**: Complex research requiring multiple specialized perspectives, adversarial verification, or synthesis across diverse domains.

**The 2026 Research Consensus**: Single-agent systems exhibit fundamental limitations when faced with complex research tasks demanding multi-source synthesis, adversarial verification, and personalized delivery. The highest-impact architecture is **deliberation-first orchestration** with hybrid collaborative reasoning.

#### Three-Phase Coordination Pipeline

**Phase 1: Ensemble (Breadth)**
- Dispatch parallel sub-agents with diverse tool access
- Each agent independently investigates from its perspective
- Results posted to shared workspace with weighted confidence
- **Omega Pattern**: `task()` with different subagent_types, each getting isolated context
- **Key Metric**: Source coverage (distinct sources across all agents)

**Phase 2: Blackboard (Transparency)**
- All results visible to all agents on shared workspace
- Agents cross-reference: post agreements, conflicts, gaps
- Orchestrator aggregates collective evidence
- **Critical Rule**: Only findings corroborated across ≥2 agents are "verified"
- **Omega Implementation**: Aggregator agent receives all subtask outputs, identifies conflicts, runs consensus

**Phase 3: Iterative Refinement (Depth)**
- Top-ranked synthesis iteratively refined through multi-round critique
- Debate pattern: Bull-vs-Bear adversarial analysis for evaluative queries
- Each round engages with counterpoints, not monologues
- **Stop Condition**: Converged confidence or max rounds reached

#### When to Use vs. Simpler Patterns

| Factor | Use Cross-Agent | Use Deep Agent |
|--------|----------------|----------------|
| **Question type** | "What is the best approach?" (evaluative) | "How does X work?" (informational) |
| **Multi-perspective needed** | Yes (pro/con, compare/contrast) | No (single authoritative answer) |
| **Token budget** | High (5-30× single agent) | Medium (3-10× single agent) |
| **Confidence requirement** | Critical (decisions impact architecture) | Moderate (informational decisions) |
| **Adversarial verification** | Required (claims must survive challenge) | Optional (single verification pass) |

#### Omega Implementation
```yaml
coordination_pattern:
  type: "cross_agent_ensemble"
  phases:
    ensemble:
      agents: ["researcher", "roc_racoon", "grok_cli"]
      tool_access: "isolated_per_agent"
      output: "confidence_annotated_findings"
    blackboard:
      aggregator: "kali"
      consensus_threshold: 2  # min agents corroborating
      conflict_handling: "surface_with_attribution"
    refinement:
      rounds: 3
      debate_mode: "bull_vs_bear"
      stop_condition: "convergence_or_max_rounds"
```

#### Checklist
- [ ] Question suitable for multi-perspective investigation
- [ ] Tool access isolated per agent
- [ ] Aggregator identified for blackboard phase
- [ ] Consensus threshold defined (≥2 corroborations)
- [ ] Refinement rounds bounded (3-5 max)
- [ ] Token budget accounts for 5-30× single-agent cost
- [ ] Escalation path if convergence fails within budget

---

### 5.15 Common Execution Mistakes

---

### 5.16 Cross-Reference: How This Connects to Other Parts

| Part | Connection | How to Use Together |
|------|------------|---------------------|
| **PART2 — Job Design Framework** | The YAML spec tells you the step count and coupling | Use step/sub-question count from spec to choose execution pattern |
| **PART3 — Context Engineering** | Single-loop uses PART3 rules; deep agents add isolation | Apply context engineering for both patterns; add isolation for deep agent sub-tasks |
| **PART4 — Tool Design Principles** | Deep agents need per-sub-task tool budgets | Each sub-task in planner gets its own tool set with budget; NEW §4.10 addresses temporal blindness in tool decisions |
| **PART6 — Quality Gates** | Quality gates differ by pattern (deep agent needs more) | Deep agents require additional gates: isolation verification, sub-task completeness; cross-agent patterns require consensus verification gate |
| **PART1 §2.9 Temporal Awareness** | Cross-agent patterns need temporal coordination across agents | Ensure all agents share the same temporal scope; re-verify time-sensitive claims across agents |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-BEST-PRACTICES ⬡ v2.0.0 ⬡ 2026-07-24*
*Part 5/6: Execution Patterns — Enhanced with forensic context, GEMMA4/WARP examples, decision flow diagram, common mistakes, and §5.14 Cross-Agent Research Coordination Pattern (3-phase pipeline from 2026 ACL research)*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*
