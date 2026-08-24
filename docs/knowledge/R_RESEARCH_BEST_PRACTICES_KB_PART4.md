# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-KB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22

---

## §5 Execution Patterns and Decision Rules

### 5.1 The Deep Agent Decision Rule (Particula 2026)

The single most important guideline for choosing between single-loop and deep agent patterns:

> "**Under ~15-20 steps with tightly coupled work, stay single-loop. Beyond that, with separable exploratory sub-tasks, the deep-agent pattern pays for its 15× token premium.**"

#### Single-Loop Agent Pattern (Best for GAP-007, GAP-012)
- **When to use**: Under ~15-20 steps with tightly coupled work
- **Examples**: Classify this ticket, extract these fields, answer from this document, heritage vetting for a single proposal, token budget estimation for a specific component
- **Characteristics**:
  - Single agent loop: observe → reason → act → observe again
  - All context in one window
  - Simpler, faster, cheaper, easier to debug
  - Token cost: ~1× baseline chat
- **Omega Implementation**:
  - Single researcher agent execution
  - No sub-agent delegation via `task()` tool
  - Context engineering within single agent (scratchpad, compression, selection)
  - Typical for: focused analysis, estimation, validation, single-component design

#### Deep Agent Pattern (Best for GAP-001, GAP-003)
- **When to use**: Beyond ~15-20 steps with separable exploratory sub-tasks
- **Examples**: Multi-faceted technical specifications, architectural decisions, comparative analyses, comprehensive literature reviews
- **Characteristics**:
  - 4-Pillar Pattern:
    1. **Planning Tool** (`write_todos`): Author/rewrite structured plan
    2. **Virtual Filesystem**: Offload context to files; keep only references/summaries in window
    3. **Isolated Subagents**: Spawn fresh-context agents for sub-tasks; return only clean results
    4. **Long-Term Memory**: Persistent across runs
  - **Architecture**: Planner → parallel isolated sub-agents → aggregator → verifier
  - **Token cost**: ~15× baseline chat (but enables complex tasks impossible for single-loop)
  - **Omega Implementation**:
    - Planner agent creates `todo.md` with sub-tasks
    - Each sub-task executed by isolated agent via `task()` tool (fresh context)
    - Results stored in `data/coordination/research_findings/{job_id}/subtask_*.md`
    - Aggregator agent synthesizes subtask results
    - Verifier agent checks completeness and quality
    - Typical for: complex specifications, architectural decisions, multi-component designs

#### Collaborative Planning Pattern (Best for GAP-002, GAP-008, GAP-010, GAP-011)
- **When to use**: High-stakes, irreversible decisions requiring human judgment
- **Examples**: Promotion governance policies, versioning strategies, fleet doctrines, soul-as-code evolution
- **Characteristics**:
  - Agent proposes plan → Human refines → Human approves → Agent executes
  - Multiple rounds of human-agent interaction before execution
  - Reduces risk of costly misalignment
  - **Omega Implementation**:
    - Agent returns proposed research plan instead of executing
    - Human reviews, modifies, approves plan
    - Once approved, agent executes the plan
    - Typical for: governance policies, strategic decisions, framework designs

### 5.2 Execution Pattern Selection Guide

| Job Complexity | Indicators | Pattern | Example Gaps |
|----------------|------------|---------|--------------|
| **Low** | <15 steps, tightly coupled, focused analysis | Single-loop | GAP-007 (Heritage Vetting), GAP-012 (Token Budget) |
| **Medium** | 15-25 steps, some separable aspects, technical specification | Single-loop with careful context engineering | GAP-001 (Scribe Spec) - *borderline case* |
| **High** | >25 steps, clearly separable sub-tasks, architectural decision | Deep Agent | GAP-003 (Soul Schema v7.0) - *if >25 steps* |
| **Strategic** | High stakes, irreversible, needs human judgment | Collaborative Planning | GAP-002 (Governance), GAP-008 (Versioning), GAP-010 (Fleet Doctrine), GAP-011 (Soul-as-Code) |

**Note**: GAP-001 (Scribe Spec) is evaluated as **Medium complexity**:
- ~12-18 steps (7 sub-questions × 1-3 iterations each)
- Moderately coupled (all about one pipeline, but distinct components)
- **Recommendation**: Start with single-loop pattern; if context engineering proves insufficient, evolve to deep agent

### 5.3 The Planner's Role in Deep Agents

When using the deep agent pattern, the planner agent follows this protocol:

#### 5.3.1 Planning Tool (`write_todos`)
- **Purpose**: Author and continuously rewrite a structured plan (often `todo.md`)
- **Why it matters**: Counters attention decay in long context windows
- **Mechanism**: Rewrite todo list near end of context on every iteration
- **Effect**: Recites goals back into recent attention, reducing goal drift
- **Bonus**: Provides human-readable trace of agent's intent (invaluable for debugging)

#### 5.3.2 Planner Output Structure
The planner emits a dynamic task list (not static, hardcoded graph):

```yaml
tasks:
  - task_id: "subtask-001"
    goal: "Extract exact llama.cpp GBNF grammar for L1/L2/L3 fields"
    tools: ["webfetch", "searxng_search", "think_tool"]
    output_schema: {type: "object", properties: {grammar: {type: "string"}}}
  - task_id: "subtask-002"
    goal: "Define sliding window chunking algorithm (4k tokens, 500 overlap)"
    tools: ["webfetch", "think_tool"]
    output_schema: {type: "object", properties: {algorithm: {type: "string"}}}
  # ... more tasks
```

#### 5.3.3 Planner Responsibilities
1. **Receive raw research query**
2. **Determine independent units of work needed**
3. **Specify what each unit needs to know** (goal, tools, output schema)
4. **Emit dynamic task list** (scales from 1-step lookup to 12+ parallel investigations)
5. **Do NOT share state with task workers during execution**

### 5.4 Task Worker Isolation (Critical for Deep Agents)

Each task worker receives **only**:
1. Specific instructions scoped to its subtask
2. Required JSON output schema
3. Access to a set of retrieval tools
4. **Nothing else** - no shared state, no intermediate reasoning chains from other workers

**Why this isolation matters**:
- Prevents context window bloat from other workers' chain-of-thought
- Eliminates cross-contamination of reasoning
- Makes failures easy to attribute to specific sub-tasks
- Each worker's reasoning stays clean and focused

#### 5.4.1 Task Worker Execution
1. Receives: instructions, output schema, available tools
2. Attempts to satisfy output schema using available tools
3. Uses **progressive content retrieval** (see Section 3.2.5):
   - First: Try to answer with search snippets alone (cheap)
   - Only if insufficient: Trigger full-page fetch (expensive)
4. Returns only clean result matching output schema
5. **Never** shares intermediate reasoning, only final output

### 5.5 Progressive Content Retrieval (Agentmelt 2026)

Addresses the tension between information completeness and token efficiency:

#### 5.5.1 Two-Stage Decision Process
1. **Stage 1: Snippet-Only Attempt**
   - Use `search_snippets` tool (or equivalent)
   - Try to answer sub-question using only search result snippets
   - Many queries answerable from metadata: publication date, domain, headline, first few sentences
   - **Token efficient**: Snippets use far fewer tokens than full pages

2. **Stage 2: Full-Page Fetch (Only if Needed)**
   - Only trigger `fetch_full_page` if snippet-level context is insufficient
   - Model detects when it cannot satisfy output schema with snippets alone
   - **Token expensive**: Reserved for cases where depth genuinely matters
   - **Examples**: Legal texts, complex specifications, primary source verification

#### 5.5.2 Implementation in Omega Research Jobs
- In tool descriptions, specify when to use snippets vs full pages
- In planner's task definitions, indicate preferred approach for each subtask
- Task workers follow: try snippets first → escalate to full page only if needed
- This implements the "write context, don't dump it" principle at the tool level

### 5.6 Structured Output as a First-Class Contract

Every layer of the system emits validated JSON against a schema:

#### 5.6.1 Why Structured Output Matters
- **Consumer research tools** can get away with prose reports
- **API-first research systems** cannot - every layer needs machine-readable output
- **Composability**: Downstream pipelines that need specific formats simply pass that schema at invocation
- **Observability**: Validation, diffing, and aggregation become programmatic (not text parsing)

#### 5.6.2 Implementation Pattern
```python
def run_task_worker(instructions: str, output_schema: dict, context: str) -> dict:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a research assistant. Always respond with valid JSON matching the provided schema."},
            {"role": "user", "content": f"Task: {instructions}\n\nContext:\n{context}\n\nOutput schema:\n{json.dumps(output_schema)}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

#### 5.6.3 Omega Application
- Task workers return JSON matching their `output_schema`
- Aggregator agent validates and combines JSON results
- Final output validated against required format (e.g., `proposed_lessons.yaml` schema)
- Enables contract tests (M21): `isinstance(result, ExpectedType)`

### 5.7 Observability Requirements (Agentmelt 2026)

#### 5.7.1 Essential Metrics to Instrument
At minimum, each node (planner, task worker, aggregator, verifier) must emit:
- Total prompt tokens
- Completion tokens
- Cache hit rate (if applicable)
- Tool call count
- Execution time
- Success/failure status

#### 5.7.2 Aggregation for Cost Correlation
- Aggregate metrics at run level
- Correlate query complexity (number of tasks spawned) with cost
- This data directly informs:
  - Rate limits
  - Per-query pricing tiers
  - Timeout thresholds
  - Resource allocation decisions

#### 5.7.3 Critical Insight
> "The reasoning token budget for an observer synthesizing twelve task outputs can be an order of magnitude larger than a single-step query. Discovering this in production billing rather than pre-launch profiling is painful."

**Omega Implementation**:
- Instrument all research job components
- Log metrics to `data/coordination/research_metrics/{job_id}/metrics.json`
- Use for capacity planning and cost optimization

### 5.8 Error Recovery and Resilience

#### 5.8.1 Retry Logic
- **Tool level**: Exponential backoff with jitter (max 3 retries)
- **Task level**: Retry failed sub-tasks (max 2 attempts)
- **Job level**: Retry entire research job (max 1 attempt) - then escalate to human

#### 5.8.2 Circuit Breaker Pattern
- Open after 3 consecutive sub-agent timeouts in a run
- Allows aggregator to produce report from partial set
- Prevents cascading failures from blocking all progress

#### 5.8.3 Checkpointing
- Save intermediate results after each major phase
- Enable restart from last checkpoint rather than beginning
- Critical for long-running research jobs

#### 5.8.4 Dead Letter Queue
- Failed sub-tasks go to DLQ for manual inspection
- Prevents lost work and enables root cause analysis
- Format: `data/coordination/research_dlq/{job_id}/subtask_{id}_failure.json`

### 5.9 The Autonomy Ladder (Mind the Product)

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

### 5.9.1 Implementation in Omega
- Research job specs include `autonomy_level` field (0, 1, or 2)
- Execution framework enforces level-appropriate behavior
- Metrics tracked per job type to inform promotion decisions
- Escalation criteria documented in spec

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22*
*This is Part 4 of 8. Continue to Part 5 for Quality Gates and Evaluation.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_research_bp_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
