---
name: "sovereign-search"
description: "Intelligent search orchestration across local cache, websearch, Firecrawl, Omega Hub, and Exa to optimize for depth, cost, and verification."
---

# 🔱 Sovereign Search Fabric Skill (v2.0)

This skill implements the **Sovereign Search Protocol (SSP)**. It replaces ad-hoc tool selection with a mandatory, cost-aware, failure-resilient pipeline. Agents MUST follow this hierarchy to ensure absolute resilience and credit efficiency.

## 🛡️ The 5-Tier Sovereign Search Protocol

Agents MUST execute search operations sequentially. Do not skip tiers.

| Tier | Tool | Cost | Use Case | Action |
| :--- | :--- | :--- | :--- | :--- |
| **T0** | **Local Cache** | Free | `.firecrawl/` directory, Omega Hub offline library | **Check first.** If hit $\rightarrow$ return. If miss $\rightarrow$ T1. |
| **T1** | **`websearch`** | Free | General facts, recency, broad discovery | **Primary tool.** If sufficient $\rightarrow$ return. If need full content $\rightarrow$ T2. |
| **T2** | **Firecrawl** | Credits | Full-page scrape, bulk crawl, structured JSON | **Deep extraction.** If 402 $\rightarrow$ T3. If success $\rightarrow$ cache to T0. |
| **T3** | **Omega Hub** | Free | Scholarly/technical deep dives, indexed archives | **Local Gnosis.** Use `hub.library_research(depth=1-4)`. If miss $\rightarrow$ T4. |
| **T4** | **Exa MCP** | API Key | Neural/semantic search, "similar to this" queries | **High-fidelity.** Final escalation. If 401 $\rightarrow$ Log to Hivemind. |

## ⚠️ Credit-Sensing Guard (Mandatory)
Before initiating any **Tier 2 (Firecrawl)** operation:
1.  **Check Status**: Call `firecrawl --status` via bash.
2.  **Evaluate**:
    - **Credits > 100**: Proceed with T2.
    - **Credits < 100**: **AUTO-DOWNGRADE**. Skip T2 and escalate directly to T3 (Omega Hub) or T1 (`websearch`).
3.  **Log**: Post a `[CREDIT-LOW]` warning to the Hivemind if a downgrade occurs.

## 📉 Error Handling Matrix
When a tool returns an error, follow this matrix immediately.

| Error | Meaning | Immediate Action | Escalation Path |
| :--- | :--- | :--- | :--- |
| **401** | Unauthorized | Fall back to T1 (`websearch`) | Log to Hivemind $\rightarrow$ Kali |
| **402** | Credits Exhausted | Fall back to T1 $\rightarrow$ T3 | Wait for reset or upgrade |
| **429** | Rate Limited | Exponential backoff (5s $\rightarrow$ 15s $\rightarrow$ 30s) | Track in observability |
| **500** | Server Error | Retry once after 2s $\rightarrow$ Fall back to T1 | Log trace in Hivemind |
| **Timeout** | No Response | Retry with timeout=60s $\rightarrow$ Fall back to T1 | Log to Hivemind |

**Mandatory Error Log Format**:
`[SEARCH-ERROR] tool={tool_name} error={error_code} tier={0-4} fallback={fallback_tool} timestamp={ISO8601}`

## 🚀 Execution Workflow

### 1. Intent Analysis
- **Factual/Recent**: $\rightarrow$ T1 (`websearch`)
- **Deep Content/Crawl**: $\rightarrow$ T0 $\rightarrow$ T1 $\rightarrow$ T2 (if credits > 100)
- **Academic/Technical**: $\rightarrow$ T0 $\rightarrow$ T1 $\rightarrow$ T3 $\rightarrow$ T4

### 2. The "No Lazy Response" Mandate
Relying solely on internal parametric weights for research queries is a **violation of the Temple Grade standard**.
- **Requirement**: Perform at least one active tool call for any factual/technical query.
- **Failure Path**: If all tools fail $\rightarrow$ Log failure chain to Hivemind $\rightarrow$ Respond with "Parametric Knowledge (Unverified)".

### 3. Caching Protocol
- **Before T2+**: Check `.firecrawl/{site}-{path}.md`.
- **After T2+**: Save result to `.firecrawl/{site}-{path}.md`.

## 📝 Output Format: Sovereign Search Report
- **Primary Finding**: Concise, direct answer.
- **Supporting Evidence**: Bullet points with citations (Tier $\rightarrow$ Tool $\rightarrow$ URL).
- **Fallback Log**: Note any tool failures and the escalation path taken.
