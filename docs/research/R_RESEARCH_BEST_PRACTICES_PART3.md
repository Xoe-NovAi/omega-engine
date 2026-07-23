# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22

---

## §3 Context Engineering Rules

### 3.1 The 7 Context Slots (In Order)

Based on Agentmelt 2026 and Anthropic context engineering research, assemble the context window deliberately:

| Slot | Content | Purpose | Omega Implementation |
|------|---------|---------|----------------------|
| **1. System Prompt** | Role, scope, constraints, stopping conditions | Stable across turns; defines agent identity | From AGENTS.md + job-specific additions |
| **2. Tool Definitions** | JSON schemas for available tools | Stable across turns; large but static | Auto-injected by Omega Hub; reference in spec |
| **3. Long-Term Memory** | Selective retrieval of user/past decisions/prior conversations | Facts about user, past decisions; retrieved selectively | `omega-hub_memory_search` with entity_name; **never dump wholesale** |
| **4. Retrieved Knowledge** | RAG chunks from vector store, SQL results, web fetches, other agent outputs | The "RAG" slot; task-specific information | `webfetch`, `websearch`, `searxng_search`, `omega-hub_sovereign_search` |
| **5. Conversation History** | Prior user turns and assistant responses (compressed) | Often compressed once turn count gets high | Managed by Omega Hub; **compress when >50% window** |
| **6. Scratchpad / Working Memory** | **EXPLICIT CONCLUSIONS** from each retrieval, not raw text | Intermediate thoughts, plans, state; **this is what carries the agent** | Write conclusions to `data/coordination/research_findings/{job_id}/scratchpad.md` |
| **7. Current Step's Instruction** | The actual prompt for this turn | Usually short; the least important slot | The specific sub-question being addressed |

### 3.2 Context Engineering Techniques (The 5 That Move Agents from Demo to Reliable)

#### Technique 1: Write Context, Don't Dump It
- **Problem**: Treating raw text as ground truth leads to poisoning
- **Solution**: Agent writes down **conclusions** from each retrieval, not the raw text
- **Omega Implementation**:
  - After each `webfetch` or `websearch`, agent writes: "Key finding: [conclusion]. Source: [URL]."
  - Scratchpad accumulates only these conclusions (50 tokens vs 5,000 for raw text)
  - Next turn, scratchpad carries the conclusion, not the source material

#### Technique 2: Select Context, Don't Include It
- **Problem**: Including all available tools/memory/context causes distraction
- **Solution**: Retrieve only the relevant subset for the current step
- **Omega Implementation**:
  - For long-term memory: Use `omega-hub_memory_search` with specific query, don't load all memories
  - For tool definitions: Reference only tools needed for current sub-question
  - For retrieved knowledge: Fetch only what's needed for current synthesis step

#### Technique 3: Compress When Window Crosses Threshold
- **Problem**: Long-running agents fill any window given, causing distraction
- **Solution**: Two compression patterns:
  - **Summarize the conversation tail**: Once history >50% of window, replace oldest turns with model-written summary
  - **Rewrite the scratchpad**: Every N turns, ask agent to rewrite own scratchpad to keep only load-bearing conclusions
- **Omega Implementation**:
  - Track context window usage via `omega-hub_get_hardware_stats`
  - At 50%: Trigger conversation history summarization
  - Every 5 iterations: Trigger scratchpad rewrite ("What are the 3 most important conclusions so far?")

#### Technique 4: Isolate Context Across Sub-Agents
- **Problem**: Context pollution when sub-agents share exploration noise
- **Solution**: When hitting a sub-task requiring heavy exploration, spawn subagent with **fresh, isolated context**
- **Omega Implementation**:
  - Use `task()` tool with isolated context for sub-agents
  - Sub-agents receive only: specific instructions, required JSON output schema, access to retrieval tools
  - Sub-agents **do not share state** with each other or main agent during execution
  - Only **clean results** returned to orchestrator (aggregator/verifier)

#### Technique 5: Progressive Content Retrieval
- **Problem**: Fetching full page content burns tokens fast; snippets may miss critical detail
- **Solution**: Two-stage decision:
  1. First attempt: Answer sub-question using search snippets alone
  2. Only if snippet-level context insufficient → trigger full-page fetch
- **Omega Implementation**:
  - Tool-routing decision inside agent: `search_snippets` tool vs `fetch_full_page` tool
  - Many research queries answerable from snippet metadata (publication date, domain, headline, first few sentences)
  - Full crawls reserved for cases where depth genuinely matters (e.g., legal texts, complex specifications)

### 3.3 Context Assembly Order (Critical!)

The order matters for attention and token efficiency:

```
[System Prompt]          ← Stable, defines agent
[Tool Definitions]       ← Stable, large but static
[Long-Term Memory]       ← Selective retrieval (not dump)
[Retrieved Knowledge]    ← Task-specific, varies per turn
[Conversation History]   ← Compressed, varies per turn
[Scratchpad]             ← **EXPLICIT CONCLUSIONS ONLY** (this is key!)
[Current Instruction]    ← Usually short, least important
```

**Why this order?**
- Stable, large components first (system, tools) → loaded once
- Variable components later (memory, knowledge, history, scratchpad, instruction)
- **Scratchpad near the end** → conclusions stay in recent attention for synthesis
- Current instruction last → least important, changes frequently

### 3.4 Practical Omega Implementation Guidelines

#### For Internal Artifact Mining (Phase 1):
- **Do**: Write conclusions to `data/coordination/research_findings/{job_id}/artifact_name.md`
- **Don't**: Dump raw file contents into context
- **Example**: After reading `C-0.5-scribe-agent.md`, write: "Key finding: Scribe agent must implement llama.cpp GBNF grammar for L1/L2/L3 extraction with 4k/500 chunking. Source: C-0.5 ticket."

#### For External Search (Phase 2):
- **Do**: Use specificity scaling (broad → narrow), multi-perspective ("X vs Y"), date-bounded ("2026", "last 6 months")
- **Don't**: Use broad/vague queries like "LLM distillation techniques"
- **Tool Budget**: Max 5 search calls per sub-question; stop after 3 consecutive searches yield no new high-credibility info

#### For Synthesis (Phase 3):
- **Do**: Apply thematic grouping, build comparative matrices, construct evidence pyramids
- **Don't**: Freeform narrative without structure
- **Output**: Match required format exactly (executive summary, full report, etc.)

#### For Quality Assurance (Phase 4):
- **Do**: Check completeness, bias detection, citation audit, contradiction flag, mandate cross-check, heritage tag validation
- **Don't**: Skip any gate; assume "it's probably fine"

#### For Drafting (Phase 5):
- **Do**: Write to target location, follow doc standards, include machine-readable artifacts, write contract tests
- **Don't**: Forget `make doc-llm-validate` or `make test` for code deliverables

#### For Review (Phase 6):
- **Do**: Incorporate feedback into spec (living principle), not just implementation
- **Don't**: Treat spec as immutable; update it when incidents teach new lessons

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22*
*Part 3/8: Context Engineering Rules*