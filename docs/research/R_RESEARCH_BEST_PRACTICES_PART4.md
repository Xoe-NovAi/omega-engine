# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-24

---

## §4 Tool Design Principles

### 4.1 Forensic Context — Why Tool Design Matters

Before tool descriptions were standardized, Omega Engine research suffered from:

- **Tool misuse**: Agents using `websearch` when `webfetch` was needed (or vice versa) — 40%+ unnecessary retries
- **Skipped verification**: Agents accepting snippet-level results without deep extraction
- **Missing failure handling**: Tools failed silently; agent continued with incomplete data
- **Tool budget exhaustion**: Unlimited calls consumed credits, triggered rate limits

**Key Insight from GEMMA4 Research**: The agent needed to use websearch → webfetch → think tool cycle consistently. When tool descriptions included explicit "when/when not" guidance, tool accuracy improved ~60%.

---

### 4.2 Tool Overview with Confidence Tiers

| Tool | Best For | Confidence of Output | Cost | Default in Omega Job |
|------|----------|---------------------|------|----------------------|
| **T1 websearch** | Broad exploration, initial discovery | Low (indicator only) | Free | ✅ Always available |
| **T2 webfetch** | Full page extraction, primary sources | High (full content) | Free | ✅ Always available |
| **T3 SearXNG** | Precision technical, category-specific | Medium (aggregate) | Free | ✅ Always available |
| **T4 Omega Hub Sovereign** | Deep research requiring multi-source synthesis | Medium-High | API key | ⚠️ When precision needed |
| **T5 Firecrawl** | Complex page scraping, JS rendering | High (structured) | Credits | ⚠️ When webfetch insufficient |
| **T6 Sieve** | Full research pipeline | Varies | Free | ⚠️ Full automation |
| **Think Tool** | Reflection, synthesis, planning | N/A | Free | ✅ MANDATORY after every search |

**⚠️ CRITICAL: The Sovereign Verification Mandate (R_SEARCH_TOOL_PROTOCOL_V1)**
- **T1/T2 snippets are INDICATORS, not evidence**
- For any critical finding: perform full-page extraction (T2+ or T4+)
- Relying on unverified snippets = Temple-Grade violation (M13)
- Full examples in §4.3 and §4.7

---

### 4.3 The Tool Description Contract (Anthropic Appendix 2)

Every tool description **must** include these 5 elements:

| Element | What to Include | Bad Example | Good Example |
|---------|-----------------|-------------|--------------|
| **What the tool does** | One sentence, direct | "Searches the web" | "Performs web search via SearXNG metasearch engine" |
| **When to use it** | Specific conditions or triggers | "When you need information" | "For broad topic exploration, trend identification, or when authoritative sources are needed" |
| **When NOT to use it** | Explicit exclusions if risk of misuse | (Often missing) | "NOT for deep technical specifications, schema validation, or when snippet-level detail suffices" |
| **What the output looks like** | Helps model interpret results correctly | "Returns search results" | "Returns markdown-formatted list of results with title, URL, snippet, and relevance score" |
| **Known limitations or failure modes** | Prevents over-reliance | (Often missing) | "Limited to top 10 results; may miss authoritative sources buried in rankings; not suitable for legal or medical advice" |

---

### 4.4 Tool-Specific Descriptions for Omega Research Jobs

#### Websearch Tool
- **What**: Performs web search via SearXNG metasearch engine (privacy-focused, aggregates multiple sources)
- **When to use**: Broad topic exploration, trend identification, initial research phase, when authoritative sources are needed
- **When NOT to use**: Deep technical specifications, schema validation, when snippet-level detail suffices, legal/medical advice requiring primary sources
- **Output**: Markdown-formatted list of results with title, URL, snippet, relevance score, and source engine
- **Limitations**: Limited to top 10 results per engine; may miss authoritative sources buried in rankings; not suitable for primary source verification
- **⚠️ Sovereign Note**: Snippets are INDICATORS. For critical findings, escalate to T2 webfetch for primary source verification.

#### Webfetch Tool
- **What**: Fetches and converts URL content to requested format (markdown by default)
- **When to use**: When full page content is needed for deep analysis, accessing primary sources, retrieving specific documents
- **When NOT to use**: When snippet-level detail suffices, for broad topic exploration, when only metadata is needed (date, domain, headline)
- **Output**: Requested format (markdown, text, or html) of the fetched URL content
- **Limitations**: Single URL per call; subject to rate limiting; may fail on JavaScript-heavy sites without rendering

#### SearXNG Search Tool
- **What**: Sovereign metasearch via self-hosted SearXNG (categories: general, it, science, videos; engines: duckduckgo, google, brave, wikipedia, etc.)
- **When to use**: Semantic/neural search refinement, precision technical searches, when specific categories/engines are needed
- **When NOT to use**: Broad exploration (use websearch first), when simple keyword matching suffices
- **Output**: JSON string with search results and hit count; includes title, URL, content snippet, engine used
- **Limitations**: Requires proper category/engine configuration; results depend on instance health and indexing

#### Omega Hub Sovereign Search Tool
- **What**: Precision technical search via Omega Hub (SearXNG → Exa → Firecrawl pipeline)
- **When to use**: Precision seeds for deep research, when high-precision technical information is needed
- **When NOT to use**: Broad exploration, initial research phase, when speed is prioritized over precision
- **Output**: JSON string containing search results and hit count; structured for easy parsing
- **Limitations**: Higher token cost and latency than websearch/searxng; requires API credits; best for targeted precision searches

#### Library Discovery Research Tool
- **What**: Tiered external discovery with consolidated report (requires query, depth 1-4)
- **When to use**: Deep research requiring multi-source synthesis with citations, literature reviews, comprehensive reports
- **When NOT to use**: Quick fact checks, simple lookups, when speed is critical
- **Output**: Consolidated report with citations, structured for easy parsing; includes metadata on sources consulted
- **Limitations**: Higher token cost and latency; slower execution; best for comprehensive synthesis tasks

#### Think Tool (CRITICAL)
- **What**: Reflection and strategic planning tool for analyzing search results and planning next steps
- **When to use**: **AFTER EVERY SEARCH** to reflect on results and plan next steps
- **When NOT to use**: Never skip; this is mandatory for quality research
- **Output**: Structured reflection answering: What key information did I find? What's still missing? Do I have enough to answer comprehensively? Should I search more or provide my answer?
- **Limitations**: Only effective if used consistently after every search; requires discipline to not skip

---

### 4.5 Tool Design Principles for Custom Tools

If creating custom tools for research jobs, follow these principles:

#### Principle 1: Task-Shaped, Not API-Shaped
- **Bad**: Tool that mirrors API endpoints exactly (e.g., "call_websearch_api")
- **Good**: Tool that reflects business decisions (e.g., "search_for_authoritative_sources_on_topic")

#### Principle 2: Consolidation Over Proliferation
- **Bad**: Multiple similar tools with slight variations
- **Good**: Merge tools where possible; keep boundaries crisp and non-overlapping
- **Example**: One "search" tool with parameters for breadth/depth rather than separate "broad_search", "deep_search", "precision_search" tools

#### Principle 3: Poka-Yoke (Mistake-Proofing)
- **Bad**: Trusting the agent to use tools correctly
- **Good**: Change arguments to make mistakes harder
- **Examples**:
  - Require absolute file paths instead of relative (prevents path confusion)
  - Use enums instead of free text for options (prevents typos)
  - Validate inputs before processing (prevents garbage-in-garbage-out)

#### Principle 4: Format Close to Natural Text
- **Bad**: Formats requiring complex escaping or counting (e.g., raw JSON, diffs)
- **Good**: Formats close to what the model has seen naturally (markdown, code blocks, plain text)
- **Examples**:
  - Prefer markdown over JSON for structured data when possible
  - Use code blocks for snippets rather than raw strings
  - Avoid formats requiring manual escaping of quotes/newlines

#### Principle 5: Give Model Room to Think
- **Bad**: Forcing token-counting or complex calculations in tool outputs
- **Good**: Design tools so the model can focus on reasoning, not mechanics
- **Examples**:
  - Return structured data that's easy to parse
  - Provide clear success/failure indicators
  - Don't make the agent count tokens or calculate complex metrics

#### Principle 6: Test in Workbench
- **Bad**: Assuming tool descriptions work without testing
- **Good**: Run many example inputs in workbench, iterate on tool descriptions based on actual model behavior
- **Process**:
  1. Write initial tool description
  2. Test with 5-10 example inputs
  3. Observe where model makes mistakes
  4. Refine description based on actual behavior
  5. Repeat until model uses tool correctly consistently

#### Principle 7: Confidence-Annotate Outputs (NEW)
- **Bad**: Returning raw tool output without confidence assessment
- **Good**: Annotate each returned data point with confidence tier
- **Implementation**:
  - After each tool call, write: "Finding: {X}. Confidence: {N/10}. Source: {URL}."
  - This becomes input to the scratchpad (PART3)
  - Enables the acceptance check for confidence minimums (PART2)

---

### 4.6 Tool Budget Management

Research jobs must specify and track tool usage budgets:

```
Tool Budget Template:
├── T1 websearch:     max 5 calls per sub-question
├── T2 webfetch:      max 3 calls per sub-question (full page verification only)
├── T3 SearXNG:       max 3 calls per sub-question (refinement phase)
├── T4 Omega Hub:     max 2 calls per research (precision seeds)
├── T5 Firecrawl:     USE SPARINGLY (limited credits)
├── T6 Sieve:         max 1 per day (resource-intensive)
└── Think Tool:       UNLIMITED — must use after every search
```

**Tracking Rule**: After every 5 tool calls, verify against budget. If approaching limit, escalate to aggregator or human.

---

### 4.7 Tool Selection Decision Flow

```
Need Information?
    │
    ▼
Can I answer from cache/knowledge? ──Yes──→ Done (T0)
    │No
    ▼
Broad exploration needed? ──Yes──→ T1 websearch
    │                                │
    │                                ▼
    │                       Snippet sufficient? ──Yes──→ Write conclusion + note INDICATOR
    │                                │No
    │                                ▼
    │                         Need full page? ──Yes──→ T2 webfetch
    │No                                                     │
    ▼                                                       ▼
Precision technical needed? ──Yes──→ T3 SearXNG    Verify snippet with full page
    │                                                Update: INDICATOR → CONFIRMED
    │No
    ▼
Need multi-source synthesis? ──Yes──→ T4 Omega Hub
    │No
    ▼
Need JS/complex page? ──Yes──→ T5 Firecrawl
    │No
    ▼
All else failed? ──Yes──→ T6 Sieve
                             │
                             ▼
                     [TOOL-CHAIN-COLLAPSE] (M23)
```

---

### 4.8 Tool Integration in Research Job Spec

In the research job spec's `context_engineering.system_prompt_slots`, include:
- `tool_descriptions_with_when_when_not`: Complete descriptions for all available tools following the 5-element contract

In the execution plan, specify:
- Which tools are authorized for each sub-question
- Any tool budget constraints (e.g., max 5 websearch calls per sub-question)
- When to use specific tools (e.g., "use webfetch only when snippet-level detail is insufficient")

---

### 4.9 Common Tool Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| **Using websearch for primary sources** | Findings based on snippets, full page contradicts | Always verify critical snippets with webfetch |
| **Skipping think tool** | Ineffective search → more searches → token waste | Mandate think tool after EVERY search |
| **Premature webfetch** | Token budget exhausted on low-value pages | Use progressive retrieval: snippets first, full page only if needed |
| **Wrong SearXNG category** | Irrelevant results due to wrong engine config | Check `categories` and `engines` parameters match the domain |
| **No tool budget tracking** | Credit exhaustion, rate limiting, unexpected costs | Set explicit budgets per sub-question in the spec |
| **Tool description mismatch** | Agent uses wrong tool for the task | Test descriptions with 5-10 examples before deployment |

---

### 4.10 Temporal Blindness Mitigation in Tool Design (NEW — 2026-07-24 Research)

> "Your LLM agents are temporally blind. They assume a stationary context and fail to account for real-world time elapsed between messages." (Ma et al., ACL 2026 — Timely Machine)

**The Problem**: Research agents don't naturally decide *when* to re-verify information vs. when to trust existing context. This leads to:
- **Over-reliance on stale context**: Agent reuses yesterday's search results without re-verifying
- **Redundant re-execution**: Agent re-searches information that hasn't changed
- The TicToc benchmark shows no model achieves >65% alignment with human temporal perception

**Tool Design Implications**:

| Tool Concern | Temporal Risk | Mitigation |
|--------------|---------------|------------|
| **websearch** | Results from different dates mixed without ordering | Always check `time_range` param; sort chronologically |
| **webfetch** | Cached content may be stale | Note fetch timestamp; check page last-modified header |
| **SearXNG** | Time-range filter may be ignored | Explicitly set `time_range` parameter per query |
| **Think Tool** | Agent doesn't reflect on elapsed time | Add temporal check: "Has enough time passed to warrant re-verification?" |
| **LLM Judge** | Judge doesn't penalize temporal staleness | Explicitly prompt judge to consider temporal validity |

**Research Finding (DREAM, ACL 2026)**: Standard evaluation misses temporal decay entirely. DREAM's KIC metric drops from 79.35 (current) → 44.80 (3 months old) → 22.34 (1 year old) — but static benchmarks show no change. Temporal awareness must be **built into tool design**, not assumed.

**Implementation in Tool Budget Section**:
```yaml
temporal_awareness:
  date_stamp_all_results: true
  check_last_modified: true
  time_sensitive_queries:
    - Any query containing: "latest", "current", "now", "2026", "version"
    - Auto-set time_range to "last_month" for fast-decay domains
  re_verify_threshold_days: 7
```

**Checklist**:
- [ ] All search tool calls include time_range when appropriate
- [ ] Tool descriptions mention temporal freshness requirements
- [ ] Re-verification scheduled for time-sensitive findings
- [ ] Date-stamped results passed downstream

---

### 4.11 Cross-Reference: How This Connects to Other Parts

| Part | Connection | How to Use Together |
|------|------------|---------------------|
| **PART2 — Job Design Framework** | Tool budget and authorized tools specified in YAML spec | When filling spec, use tool descriptions here for the `tool_budget` section |
| **PART3 — Context Engineering** | Tool outputs feed into scratchpad; confidence annotation critical | After each tool call, write conclusion + confidence + source to scratchpad |
| **PART5 — Execution Patterns** | Deep agents need isolated tool contexts for sub-agents | Each sub-agent gets its own tool set with budget from this section |
| **PART6 — Quality Gates** | Tool usage must be auditable against spec | Verify actual tool calls match authorized types and budgets; NEW Gate 10 validates temporal validity |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-BEST-PRACTICES ⬡ v2.0.0 ⬡ 2026-07-24*
*Part 4/6: Tool Design Principles — Enhanced with tool confidence tiers, decision flow, common mistakes, and Sovereign Verification Mandate*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*
