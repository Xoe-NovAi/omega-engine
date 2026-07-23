# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22

---

## §4 Tool Design Principles

### 4.1 The Tool Description Contract (Anthropic Appendix 2)

Every tool description **must** include these 5 elements:

| Element | What to Include | Bad Example | Good Example |
|---------|-----------------|-------------|--------------|
| **What the tool does** | One sentence, direct | "Searches the web" | "Performs web search via SearXNG metasearch engine" |
| **When to use it** | Specific conditions or triggers | "When you need information" | "For broad topic exploration, trend identification, or when authoritative sources are needed" |
| **When NOT to use it** | Explicit exclusions if risk of misuse | (Often missing) | "NOT for deep technical specifications, schema validation, or when snippet-level detail suffices" |
| **What the output looks like** | Helps model interpret results correctly | "Returns search results" | "Returns markdown-formatted list of results with title, URL, snippet, and relevance score" |
| **Known limitations or failure modes** | Prevents over-reliance | (Often missing) | "Limited to top 10 results; may miss authoritative sources buried in rankings; not suitable for legal or medical advice" |

### 4.2 Tool-Specific Descriptions for Omega Research Jobs

#### Websearch Tool
- **What**: Performs web search via SearXNG metasearch engine (privacy-focused, aggregates multiple sources)
- **When to use**: Broad topic exploration, trend identification, initial research phase, when authoritative sources are needed
- **When NOT to use**: Deep technical specifications, schema validation, when snippet-level detail suffices, legal/medical advice requiring primary sources
- **Output**: Markdown-formatted list of results with title, URL, snippet, relevance score, and source engine
- **Limitations**: Limited to top 10 results per engine; may miss authoritative sources buried in rankings; not suitable for primary source verification

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

### 4.3 Tool Design Principles for Custom Tools

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
  - Require absolute file paths instead of relative (prevents path confusion
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

### 4.4 Tool Integration in Research Job Spec

In the research job spec's `context_engineering.system_prompt_slots`, include:
- `tool_descriptions_with_when_when_not`: Complete descriptions for all available tools following the 5-element contract

In the execution plan, specify:
- Which tools are authorized for each sub-question
- Any tool budget constraints (e.g., max 5 websearch calls per sub-question)
- When to use specific tools (e.g., "use webfetch only when snippet-level detail is insufficient")

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22*
*Part 4/8: Tool Design Principles*