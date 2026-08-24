# Agent Role-Aware Prompting
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-ROLE-AWARE-PROMPTING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_role_aware_prompting ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **role-aware prompting** — systems where system prompts dynamically adapt based on agent role (planner, executor, critic, researcher, verifier). The frontier has converged on **distinct system prompts per role** with **explicit I/O schemas**, **tool allowlists per role**, **model differentiation per role**, and **context isolation per role**. Critical finding: **Forcing one agent to be all roles forces a compromise prompt mediocre at every role** — the decomposition works because different roles want different prompts, different models, and different context.

---

## 1. The Four Canonical Roles (InterviewsVector/AI Engineering Academy, 2026)
> **Sources**: 
> - [Role Specialization — Planner/Critic/Executor/Verifier](https://www.interviewsvector.com/academy/roadmap/16-multi-agent-and-swarms/08-role-specialization)
> - [AI Engineering Academy](https://ai-engineering.academy/learn/16-multi-agent-and-swarms/08-role-specialization/)

| Role | Purpose | Tools | Output | Key Principle |
|------|---------|-------|--------|---------------|
| **Planner** | Reads goal, produces step list/spec | Knowledge retrieval, docs | Structured plan | "Think carefully, break into discrete steps, prefer reversible ops" |
| **Executor** | Reads one plan step, produces artifact | Actual work tools (code, shell, API) | The artifact | "Do exactly this task, return structured output, do not improvise" |
| **Critic** | Reads executor output vs planner intent | Read-only access, static analysis | Accept/reject with reasons | "Find what's wrong, be specific, do not be polite" |
| **Verifier** | Runs deterministic check on artifact | Test runner, type checker, schema validator | Pass/fail with evidence | **Code-based, not LLM-based** — cannot be fooled |

**Critical insight**: "The fix is not more agents — it is **different agents**. Assign distinct roles. Give the critic tools the planner does not have. Give the verifier an objective test suite. Now the system has internal disagreement with grounded correction, not just parallel guessing."

---

## 2. Why Role Decomposition Works (Bharat Bhavnasi, 2026-03-12)
> **Source**: [Deep Agents: Planner/Executor/Critic Becomes the Default](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)

Three reasons, in increasing order of importance:

### 2.1 Different Roles Want Different Prompts
> "A good planner prompt is 'think carefully about what's needed, break it into discrete steps, prefer reversible operations first.' A good executor prompt is 'do exactly this task, return structured output, do not improvise.' A good critic prompt is 'find what's wrong, be specific, do not be polite about it.' **These prompts contradict each other.** Forcing one agent to be all three forces a compromise prompt that's mediocre at every role."

### 2.2 Different Roles Want Different Models
> "The planner needs the strongest reasoning available — it makes the bet that the next step is the right next step, and getting it wrong is expensive. The executor can run on a smaller, cheaper, faster model — most tasks are mechanical given the planner's spec. The critic can also run smaller, and importantly **should run a different model than the executor so it's not just confirming the executor's biases**."

### 2.3 Different Roles Want Different Context
> "The planner needs the goal, the todo list, and short summaries of past work. The executor needs only the current task description — feed it the full history and it gets confused. The critic needs the task spec and the output, nothing else. **Separating contexts is the only way to keep total token usage tractable on long-running work.**"

---

## 3. Role-Specific System Prompt Anatomy

### 3.1 Six-Section System Prompt Template (Cowork.ink, 2026-03-14)
> **Source**: [Prompt Engineering for AI Agents](https://cowork.ink/blog/ai-agent-prompt-engineering)

```markdown
## Role
You are [specific persona] at [company/context].
Your job is to [core function].

## Objective
Your objective is to [primary goal].
[Edge case handling: what to do when ambiguous or impossible.]

## Tools
- tool_name(param: type): [what it does].
  Use when: [trigger condition].
  Limit: [call budget or constraints].

## Constraints
- [Hard rule 1 — always / never]
- [Hard rule 2]

## Output Format
[Exact format specification, e.g., JSON schema, Markdown structure]

## Examples (Few-Shot)
[Worked examples demonstrating thought → action → observation → answer loop]
```

**Key insight**: "One well-constructed example teaches the agent the thought-action-observation loop, the output format, and the correct tool call syntax simultaneously."

### 3.2 BAD/GOOD Example Pairs (Cowork.ink, 2026)
> **Source**: [Prompt Engineering for AI Agents](https://cowork.ink/blog/ai-agent-prompt-engineering/)

> "The BAD/GOOD pair teaches the model the correct pattern far more efficiently than a rule like 'never use SELECT *' alone."

```markdown
## Examples

### BAD
User: Get all users
Action: query_database("SELECT * FROM users")

### GOOD
User: Get all users
Action: query_database("SELECT id, email, created_at FROM users WHERE active = true")
```

---

## 4. Role-Specific Prompt Patterns

### 4.1 Planner Prompt (Bharat, 2026; Cline, 2026)
> **Sources**: 
> - [Deep Agents](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)
> - [AI Agent Handbook](https://github.com/vasilyevdm/ai-agent-handbook/blob/main/COMPREHENSIVE_AGENT_ENGINEERING_GUIDE_2026.md)

```markdown
## Role
You are a Senior Software Architect. Your job is to analyze requirements and create 
step-by-step implementation plans.

## Objective
Produce a structured plan that a junior engineer can execute without ambiguity.
Each step must have explicit inputs, expected outputs, and success criteria.

## Constraints
- NEVER write code or execute tools. You ONLY plan.
- Prefer 3-7 concrete, actionable steps. No more than 7.
- Each step must be independently verifiable.
- If information is missing, note it as a dependency — do not assume.

## Output Format
JSON array of steps:
[
  {
    "id": "step_1",
    "description": "Specific action",
    "executor_role": "code_analyst",
    "inputs": {"files": ["src/auth/*.py"]},
    "outputs": {"analysis": "markdown_summary"},
    "success_criteria": "Identifies all token handling and middleware",
    "allowed_tools": ["read", "grep", "glob"],
    "context_budget": 16384,
    "dependencies": []
  }
]

## Examples
[Worked examples of good vs bad plans]
```

### 4.2 Executor Prompt (Bharat, 2026; Cline, 2026)
```markdown
## Role
You are a Staff Engineer. Your job is to execute ONE specific step from a plan.

## Objective
Complete the given step exactly as specified. Return structured output.

## Constraints
- DO NOT deviate from the plan. If the plan is wrong, report it — do not improvise.
- Use ONLY the allowed_tools for this step.
- Return output matching the specified outputs schema.
- If you cannot complete the step, return error with specific reason.

## Tools
[Only the tools listed in the step's allowed_tools]

## Output Format
{
  "step_id": "step_1",
  "status": "completed|failed",
  "outputs": {"analysis": "..."},
  "errors": null
}

## Communicative Dehallucination (ChatDev Pattern)
"When you need specific information you were not given, ask the relevant role 
by name before producing output. Never invent details."
```

### 4.3 Critic Prompt (Bharat, 2026; InterviewsVector, 2026)
```markdown
## Role
You are a Principal Engineer / Code Reviewer. Your job is to find defects in 
executor output against the planner's intent.

## Objective
Inspect the executor's output against the step specification. 
Return specific, actionable feedback.

## Constraints
- You have READ-ONLY access. You CANNOT modify the work.
- Use verification tools: run tests, parse outputs, query data sources.
- Do NOT score (1-10). INSPECT: each check returns pass/fail + reason.
- Be specific. "Variable naming inconsistent" > "Code quality: 7/10".

## Tools
- run_tests(test_spec)
- validate_schema(output, expected_schema)
- fact_check(claim, sources)
- static_analysis(code)

## Output Format
{
  "step_id": "step_1",
  "verdict": "accept|reject",
  "checks": [
    {"check": "schema_validation", "pass": true, "reason": "Output matches expected schema"},
    {"check": "test_execution", "pass": false, "reason": "Test 'auth_flow' failed: timeout"}
  ],
  "feedback": "Fix the timeout in auth_flow test. Increase mock delay tolerance."
}
```

### 4.4 Verifier Prompt (InterviewsVector, 2026)
```markdown
## Role
You are an Automated Verification System. Your job is to run deterministic checks.

## Objective
Execute the verification suite for the given artifact. Return pass/fail with evidence.

## Constraints
- You are CODE, not an LLM. Your pass/fail is decided by program execution.
- No subjectivity. No "looks good to me."
- If the check cannot run, return error — do not guess.

## Tools
- pytest / jest / cargo test (actual test runners)
- mypy / tsc / ruff (type checkers, linters)
- jsonschema / pydantic (schema validators)
- Custom business logic validators

## Output Format
{
  "step_id": "step_1",
  "passed": true,
  "evidence": {
    "tests_run": 47,
    "tests_passed": 47,
    "coverage": "92%",
    "type_errors": 0
  }
}
```

### 4.5 Researcher Prompt (Omega Engine Specific)
```markdown
## Role
You are a Sovereign Researcher. Your job is to eliminate blind spots through 
Perspective Triangulation — analyzing every problem through multiple, 
often conflicting, intellectual lenses.

## Objective
Produce a dialectic synthesis: deploy the Council of Four (Architect, Adversary, 
Alchemist, Archivist), present findings from each, identify convergence/divergence, 
produce unified conclusion.

## Constraints
- MUST perform at least one active tool call per research query.
- NO parametric synthesis when mandatory tools fail → [TOOL-CHAIN-COLLAPSE].
- Cite sources with URLs. Mark marketing vs research vs proven practice.
- Flag single-source claims as directional.

## Council of Four Perspectives
1. **Architect** (Systemic Logic): Structure, scalability, efficiency, integrity
2. **Adversary** (Critical Rigor): Failure modes, edge cases, vulnerabilities
3. **Alchemist** (Creative Synthesis): Cross-pollination, unexpected resonances
4. **Archivist** (Historical Truth): Legacy patterns, factual precision, precedent

## Output Format
Fractal deliverable:
- L1: Executive Summary
- L2: Detailed Dialectic (four perspectives + triangulation)
- L3: Raw Signal (sources, citations, unverified claims)
```

---

## 5. Dynamic Role Switching Within Session

### 5.1 Cline's Plan/Act Modes (AI Agent Handbook, 2026)
> **Source**: [AI Agent Handbook](https://github.com/vasilyevdm/ai-agent-handbook/blob/main/COMPREHENSIVE_AGENT_ENGINEERING_GUIDE_2026.md)

**Cline's implementation is the gold standard**:
- **Plan Mode**: AI analyzes requirements, reads codebase, builds step-by-step plan. No modifications. User reviews plan.
- **Act Mode**: AI executes the plan, editing files and running commands. Human approval at each step.

**Role switch**: Same agent, different system prompt, different tool permissions, different context.

### 5.2 Anthropic Managed Agents (Anthropic Engineering, 2024)
> **Source**: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (cited by GrandLinux)

Orchestrator-Workers pattern: orchestrator (planner) delegates to specialized workers (executors) with role-specific prompts and tool access.

### 5.3 MetaGPT Role Specialization (arXiv:2308.00352)
> **Source**: Cited by InterviewsVector, AI Engineering Academy

Formalizes roles as SOPs encoded into role prompts:
- Product Manager
- Architect
- Project Manager
- Engineer
- QA Engineer

**Code = SOP (Team)** — strict I/O schemas per role turn a team into a pipeline.

---

## 6. Model Differentiation Per Role (Production Practice)

### 6.1 Model Assignment Matrix (Bharat, 2026; GrandLinux, 2026; LocalGraph, 2025)

| Role | Model Tier | Example Models | Rationale |
|------|------------|----------------|-----------|
| **Planner** | Strongest reasoning | Claude Opus, GPT-5, Llama-70B, Qwen3-14B | Strategic bets, expensive if wrong |
| **Executor** | Fast, instruction-following | Qwen2.5-Coder-14B/32B, Llama-3.3-70B | Mechanical given spec, high volume |
| **Critic** | Different from executor | Opus if executor=Sonnet, Haiku if executor=Opus | Catches different blind spots |
| **Verifier** | N/A (deterministic) | Test runners, type checkers | Code-based, not LLM |
| **Researcher** | Broad knowledge + reasoning | Gemini 2.5 Pro, DeepSeek-R1 | Synthesis across domains |

### 6.2 Anthropic Outcomes Primitive (2026-05-06)
> **Source**: [Deep Agents](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)

> "The Anthropic Outcomes primitive (public beta from May 6) explicitly recommends a different model for the critic, and the recommendation is correct."

---

## 7. Context Isolation Per Role

### 7.1 What Goes Where (Cowork.ink, 2026)
> **Source**: [Prompt Engineering for AI Agents](https://cowork.ink/blog/ai-agent-prompt-engineering/)

| Content Type | Where to Put It |
|--------------|-----------------|
| Agent role, rules, constraints | System prompt — never changes |
| Tool definitions | System prompt (or tool schema) |
| Few-shot examples | System prompt |
| Current time, date | First user message |
| User's name, session preferences | Context injection block, user message |
| Retrieved documents (RAG) | User message, not system prompt |
| Results from previous steps | User message as structured handoff |

> **Don't put dynamic state in the system prompt** — caching works by matching exact prefix. Any dynamic content in system prompt invalidates cache.

### 7.2 Shared State as Connective Tissue (Bharat, 2026)
> **Source**: [Deep Agents](https://bvsbharat.com/posts/2026/deep-agents-planner-executor-critic/)

> "Shared state — a todo list and a scratchpad — is the connective tissue. **None of the three roles holds the full plan in its context window; the plan lives in the state.**"

```python
class PlanExecuteState(TypedDict):
    input: str
    plan: list[Step]
    past_steps: list[Tuple[Step, str]]
    current_step: int
    needs_replanning: bool
```

---

## 8. Role-Aware Prompt Composition (Dynamic Assembly)

### 8.1 Priority-Ordered Sections Per Role (AgentPatterns.ai, 2026)
> **Source**: [Dynamic System Prompt Composition](https://agentpatterns.ai/context-engineering/dynamic-system-prompt-composition/)

**Planner sections** (priority order):
1. Core Identity: "Senior Architect, strategic planner"
2. Planning Heuristics: "Prefer reversible, 3-7 steps, explicit contracts"
3. Tool Definitions: Read-only tools (grep, read, glob)
4. Safety Rules: "Never execute, never assume"
5. Dynamic Context: Goal, todo list, past step summaries

**Executor sections** (priority order):
1. Core Identity: "Staff Engineer, precise executor"
2. Tool Definitions: Full toolset for this step
3. Output Format: Strict schema for this step
4. Safety Rules: "No improvisation, ask if missing info"
5. Dynamic Context: Current step spec, relevant knowledge only

**Critic sections** (priority order):
1. Core Identity: "Principal Engineer, rigorous reviewer"
2. Verification Tools: Test runners, schema validators
3. Evaluation Rubric: Specific checks per step type
4. Safety Rules: "Read-only, no scoring, pass/fail only"
5. Dynamic Context: Step spec + executor output

### 8.2 Mode-Specific Variants (AgentPatterns.ai, 2026)
> **Source**: [Dynamic System Prompt Composition](https://agentpatterns.ai/context-engineering/dynamic-system-prompt-composition/)

> "Different execution modes require different prompt emphasis. OPENDEV defines planning, thinking, and normal execution modes, each with a distinct prompt variant that includes only the constraints relevant to that mode."

---

## 9. Framework Mappings for Role Specialization

| Framework | Role Implementation |
|-----------|---------------------|
| **CrewAI** | `Agent(role, goal, backstory)` — textbook specialization surface |
| **LangGraph** | Nodes with specialized prompts; edges enforce pipeline |
| **AutoGen** | Role-specific `ConversableAgents` in GroupChat |
| **OpenAI Agents SDK** | Handoff tools between role-specialized Agents |
| **LangChain Deep Agents** | Planner/Executor/Critic nodes with shared state |
| **Cline** | Plan Mode / Act Mode (same agent, different prompt+tools) |

---

## 10. Anti-Patterns to Avoid

### 10.1 All-LLM Anti-Pattern (InterviewsVector, 2026)
> "Every role in your system is an LLM and every role's output is 'looks good to me.' Classic MAST failure mode. **Add at least one deterministic verifier.** Never all-LLM."

### 10.2 Vibe-Based Critic (Bharat, 2026)
> "Most 'deep agents' have a critic that's basically 'score this 1-10'. That critic is useless. It approves things it shouldn't and rejects things it should approve, because 'score this' is the kind of vague instruction LLMs are bad at."

**Fix**: Rubric-based, tool-equipped, model-different critic.

### 10.3 Cross-Role Miscommunication (Bharat, 2026)
> "The planner writes a task description that's clear to the planner and ambiguous to the executor. The executor does the wrong thing. The critic approves the wrong thing."

**Fix**: Structured task contracts — planner's output is a schema with explicit inputs, expected outputs, success criteria.

---

## 11. Recommendations for Omega Engine

### 11.1 Role Registry with Prompt Templates
```python
# config/roles/registry.yaml
roles:
  planner:
    system_prompt_template: "config/roles/planner/system_prompt.md"
    model: "native-gguf-planner"
    context_budget: 16384
    allowed_tools: ["read", "grep", "glob", "knowledge_search"]
    output_schema: "schemas/plan.json"
    context_includes: ["goal", "todo_list", "past_step_summaries"]
  
  executor:
    system_prompt_template: "config/roles/executor/system_prompt.md"
    model: "native-gguf-executor"
    context_budget: 8192
    allowed_tools: ["read", "write", "edit", "bash", "knowledge_search"]
    output_schema: "schemas/executor_output.json"
    context_includes: ["current_step", "relevant_knowledge"]
  
  critic:
    system_prompt_template: "config/roles/critic/system_prompt.md"
    model: "native-gguf-critic"
    context_budget: 4096
    allowed_tools: ["run_tests", "validate_schema", "static_analysis"]
    output_schema: "schemas/critic_verdict.json"
    context_includes: ["step_spec", "executor_output"]
  
  verifier:
    type: "deterministic"
    runner: "pytest"
    schema_validator: "pydantic"
  
  researcher:
    system_prompt_template: "config/roles/researcher/system_prompt.md"
    model: "native-gguf-planner"  # Strong reasoning
    context_budget: 32768
    allowed_tools: ["web_search", "web_fetch", "knowledge_search", "hf_cli"]
    output_schema: "schemas/research_deliverable.json"
    context_includes: ["query", "council_perspectives"]
```

### 11.2 Dynamic Prompt Assembly Per Role
```python
class RolePromptBuilder:
    def build(self, role: str, dynamic_context: dict) -> str:
        template = self.load_template(role)
        sections = self.get_sections_for_role(role)
        
        # Assemble priority-ordered sections
        prompt_parts = []
        for section in sections:
            if section.condition(dynamic_context):
                content = section.render(dynamic_context)
                prompt_parts.append(content)
        
        return "\n\n".join(prompt_parts)
    
    def get_sections_for_role(self, role: str) -> list[PromptSection]:
        # Return role-specific sections in priority order
        # Planner: identity → heuristics → read_tools → safety → dynamic
        # Executor: identity → step_tools → output_format → safety → dynamic
        # Critic: identity → verify_tools → rubric → safety → dynamic
        pass
```

### 11.3 Context Injection Protocol (Per Role)
```python
def inject_context(role: str, state: PlanExecuteState, step: Step = None) -> dict:
    if role == "planner":
        return {
            "goal": state["input"],
            "todo_list": state["plan"],
            "past_summaries": summarize_steps(state["past_steps"]),
        }
    elif role == "executor":
        return {
            "current_step": step,
            "relevant_knowledge": kb.retrieve(step.query, budget=step.context_budget * 0.5),
        }
    elif role == "critic":
        return {
            "step_spec": step,
            "executor_output": state["past_steps"][-1][1] if state["past_steps"] else None,
        }
    elif role == "researcher":
        return {
            "query": state["input"],
            "council_perspectives": ["architect", "adversary", "alchemist", "archivist"],
        }
```

### 11.4 Model Routing in Oracle
```python
# In Oracle.summon() or Oracle.talk()
ROLE_MODEL_MAP = {
    "planner": "native-gguf-planner",
    "executor": "native-gguf-executor", 
    "critic": "native-gguf-critic",
    "researcher": "native-gguf-planner",  # Same tier as planner
    "default": "native-gguf",
}

def get_model_for_role(role: str) -> str:
    return ROLE_MODEL_MAP.get(role, ROLE_MODEL_MAP["default"])
```

---

## 12. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | InterviewsVector (2026) | Attributed reading | ✅ Direct fetch | Four canonical roles, verifier importance |
| 2 | AI Engineering Academy (2026) | Course material | ✅ Direct fetch | Same content as InterviewsVector |
| 3 | Bharat Bhavnasi (2026-03-12) | Engineering blog | ✅ Direct fetch | Three reasons decomposition works, critic design |
| 4 | Cowork.ink (2026-03-14) | Engineering blog | ✅ Direct fetch | Six-section template, BAD/GOOD examples, context placement |
| 5 | AI Agent Handbook (2026) | GitHub guide | ✅ Direct fetch | Cline Plan/Act modes, planner/executor code |
| 6 | GrandLinux (2026-05-24) | Case study | ✅ Direct fetch | Model differentiation planner vs executor |
| 7 | LocalGraph (2025) | Code tutorial | ✅ Direct fetch | Multi-model LangGraph implementation |
| 8 | AgentPatterns.ai (2026-06-13) | Pattern library | ✅ Direct fetch | Priority-ordered sections, mode variants |
| 9 | Anthropic Engineering (2024) | Official blog | ⚠️ Cited by others | Orchestrator-workers pattern |
| 10 | MetaGPT (2023) | arXiv:2308.00352 | ⚠️ Cited by multiple | SOP pattern, role specialization |
| 11 | ChatDev (2023) | arXiv | ⚠️ Cited by Bharat | Communicative dehallucination |

---

## 13. Unverified Claims (Flagged)

- **Anthropic Outcomes primitive "explicitly recommends different model for critic"** — cited by Bharat, not directly verified
- **MAST study "21.3% verification gaps, 79% trace back to failed checks"** — cited by InterviewsVector, original paper not fetched
- **PwC CrewAI "7× accuracy gain from verifier"** — cited by InterviewsVector, no source link
- **Cline "gold standard" for Plan/Act** — AI Agent Handbook claim, no comparative evaluation
- **MetaGPT "Code = SOP" formalization** — cited by multiple, paper not directly analyzed for this doc

---

*End of R_ROLE_AWARE_PROMPTING_20260819.md*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
