# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-24

---

## §3 Context Engineering Rules

### 3.1 Forensic Context — Why Context Engineering Matters

Before context engineering rules were standardized, Omega Engine research suffered from:

- **Context poisoning**: Raw text dumps in the scratchpad confused the agent (avg. 65% token waste)
- **Distraction**: Full conversation history loaded every turn, burying critical conclusions
- **Confusion**: All retrieved knowledge dumped in one unordered mass → agent couldn't distinguish signal from noise
- **Clash**: Conflicting sources presented without explicit resolution → agent synthesized contradictions silently

**The Turning Point**: The GEMMA4_WORKHORSE research demonstrated disciplined context engineering. After each `webfetch` call, the agent wrote "Key finding: [conclusion]. Source: [URL]." — 50 tokens instead of 5,000. The scratchpad accumulated only these conclusions, enabling clear synthesis without context poisoning.

---

### 3.2 The 7 Context Slots (In Order)

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

---

### 3.3 Context Engineering Techniques (The 5 That Move Agents from Demo to Reliable)

#### Technique 1: Write Context, Don't Dump It
- **Problem**: Treating raw text as ground truth leads to poisoning
- **Solution**: Agent writes down **conclusions** from each retrieval, not the raw text
- **Omega Implementation**:
  - After each `webfetch` or `websearch`, agent writes: "Key finding: [conclusion]. Source: [URL]."
  - Scratchpad accumulates only these conclusions (50 tokens vs 5,000 for raw text)
  - Next turn, scratchpad carries the conclusion, not the source material

**⚠️ CRITICAL: The Sovereign Verification Mandate (R_SEARCH_TOOL_PROTOCOL_V1)**
Search snippets (T1/T2) are **indicators**, NOT evidence. For any critical finding:
1. Write the conclusion to scratchpad: "Indication: [finding]. Source: [snippet URL]."
2. Perform a Sovereign Verification Step: extract the full page using `webfetch` or `firecrawl_scrape`
3. Update scratchpad: "CONFIRMED: [finding]. Primary source: [URL]." or "REJECTED: [finding]. Page did not contain expected content."

Relying on unverified snippets is a violation of the Temple-Grade standard (M13).

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

**Real Example from GEMMA4 Research**:
After 10+ iterations investigating cloud providers, the scratchpad was rewritten from:
```
Found that Groq has 30 RPM, TPM 12000 for Llama 3.3 70B
Also NVIDIA NIM has 40 RPM for Nemotron 3 Ultra
OpenRouter shows 20 RPM for Gemma 4
Google free tier is 250K TPM for Gemini models
But only 16K for Gemma 4 specifically
```
→
```
Top 3 conclusions:
1. Groq Llama 3.3 70B: Best latency (280-394 tok/s), 30 RPM, 12K TPM
2. NVIDIA NIM Nemotron: Best RPM (40), free tier active
3. Google Gemma 4: DEAD for workhorse (16K TPM across all tiers)
```

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
  - Tool-routing decision inside agent: `T1 websearch` vs `T2 webfetch`
  - Many research queries answerable from snippet metadata (publication date, domain, headline, first few sentences)
  - Full crawls reserved for cases where depth genuinely matters (e.g., legal texts, complex specifications)

---

### 3.4 Context Assembly Order (Critical!)

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

**Failure Mode: Reversed Assembly Order**
If you put the scratchpad first and system prompt last:
- Conclusions are de-emphasized (less recent attention)
- System role/scope/constraints are less accessible
- Agent is more likely to drift from its defined mission
- Context window prefix becomes unstable

---

### 3.5 Practical Omega Implementation Guidelines

#### For Internal Artifact Mining (Phase 1):
- **Do**: Write conclusions to `data/coordination/research_findings/{job_id}/artifact_name.md`
- **Don't**: Dump raw file contents into context
- **Example**: After reading `C-0.5-scribe-agent.md`, write: "Key finding: Scribe agent must implement llama.cpp GBNF grammar for L1/L2/L3 extraction with 4k/500 chunking. Source: C-0.5 ticket."

#### For External Search (Phase 2):
- **Do**: Use specificity scaling (broad → narrow), multi-perspective ("X vs Y"), date-bounded ("2026", "last 6 months")
- **Don't**: Use broad/vague queries like "LLM distillation techniques"
- **Tool Budget**: Max 5 search calls per sub-question; stop after 3 consecutive searches yield no new high-credibility info
- **Sovereign Verification**: Always verify critical snippets with full-page fetch (M13)

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

### 3.6 Common Context Engineering Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| **Raw text dump** | Agent repeats source text verbatim instead of synthesizing | Force conclusion extraction: "Write 1-sentence finding from each source" |
| **Missing Sovereign Verification** | Action taken on snippet alone, full page contradicts | Mandate sovereign verification step before ANY action on critical findings |
| **Scratchpad not rewritten** | Conclusions diluted by accumulated noise | Every 5 iterations: "What are the 3 most important conclusions?" |
| **Wrong assembly order** | Agent drifts from mission early in execution | Keep system prompt first, scratchpad near end, current instruction last |
| **Sub-agent pollution** | Synthesizer contaminated by sub-agent reasoning noise | Enforce isolation: sub-agents return ONLY clean results matching output schema |
| **Premature full-page fetch** | Token budget exhausted on low-value content | Use progressive retrieval: try snippets first, fetch only if needed |
| **No compression trigger** | Context window fills, agent performance degrades | Set compression at 50% window threshold; compress tail AND rewrite scratchpad |

---

### 3.7 Cross-Reference: How This Connects to Other Parts

| Part | Connection | How to Use Together |
|------|------------|---------------------|
| **PART1 — Core Principles** | Context engineering > prompt engineering is a core principle | Read PART1 for the philosophical foundation, then apply techniques here |
| **PART2 — Job Design Framework** | Context engineering section of the YAML spec references these rules | When filling the spec template, use this section to populate `context_engineering` fields |
| **PART4 — Tool Design Principles** | Tool descriptions must include "when/when not" that aligns with context assembly order | Use PART4 to refine tool selection BEFORE retrieving knowledge |
| **PART5 — Execution Patterns** | Single-loop vs deep agent decisions affect context isolation strategy | Use PART5 to determine isolation needs, then apply Technique 4 |
| **PART6 — Quality Gates** | Context engineering compliance is an in-progress quality gate | Use PART6 §6.2 to verify context engineering is working during execution |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-BEST-PRACTICES ⬡ v2.0.0 ⬡ 2026-07-24*
*Part 3/6: Context Engineering Rules — Enhanced with GEMMA4 example, Sovereign Verification Mandate, and common mistakes*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*
