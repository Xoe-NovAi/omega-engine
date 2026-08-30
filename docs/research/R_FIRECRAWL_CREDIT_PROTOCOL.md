---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

title: Firecrawl Credit Protocol & Caching Strategy
ap_token: AP-FIRECRAWL-CREDITS-v1.0.0
date: 2026-06-11
status: FINAL
owner: researcher
---

# 🔱 Firecrawl Credit Protocol & Caching Strategy

## §0 Executive Summary
This document defines the operational constraints and optimization strategies for the use of Firecrawl within the Omega Engine. Given the limited credit budget of the free tier (1,000 credits/month), this protocol mandates a "Cache-First, Scrape-Last" approach to ensure maximum utility of available resources.

## §1 Credit Economics
Firecrawl operations are billed based on the complexity of the task.

| Operation | Estimated Cost | Description |
|----------|-----------------|---------------------------------------------------|
| `scrape` | 1 credit | Single page extraction. |
| `search` | 1-5 credits | Web search with optional scraping of top results. |
| `crawl` | 1 credit / page | Bulk extraction of multiple pages. |
| `agent` | 5-20 credits | AI-powered structured extraction (multi-step). |
| `map` | Minimal | URL discovery (often free or very low cost). |

**Critical Thresholds:**
- **Safe Zone (> 200 credits)**: Standard protocol execution.
- **Caution Zone (100-200 credits)**: Disable `crawl` and `agent` operations; prioritize `scrape` and `websearch`.
- **Exhaustion Zone (< 100 credits)**: Mandatory fallback to Tier 1 (`websearch`) and Tier 0 (Local Cache).

## §2 The Sovereign Caching Strategy (Tier 0)
To prevent redundant credit expenditure, all Firecrawl outputs MUST be cached locally.

### 2.1 Cache Location & Naming
- **Root**: `.firecrawl/`
- **Naming Convention**: `{site}-{path}.md`
- **Example**: `github.com-docs-mcp.md`

### 2.2 The Cache-First Workflow
Before any Tier 2 tool call:
1. **Check Cache**: `grep` the `.firecrawl/` directory for the target URL or site.
2. **Evaluate Freshness**: If the file exists and is < 7 days old, use the cached version.
3. **Escalate**: Only if the cache is missing or stale, execute the Firecrawl call.
4. **Commit**: Immediately save the result to `.firecrawl/` upon success.

## §3 CLI Fallback Pattern
When the Firecrawl MCP returns a `402 Payment Required` or is otherwise unavailable, agents MUST attempt the CLI fallback.

**Command**: `bash(firecrawl scrape <url>)`
**Reason**: The CLI may have different rate limits or access to cached data that the MCP does not.

## §4 Credit-Sensing Guard (SR-5 Integration)
The `sovereign-search` skill will implement a "Credit-Sensing Guard":
- **Check**: Call `firecrawl --status` before initiating a Tier 2 operation.
- **Action**: If credits < 100, the skill will automatically downgrade the request to Tier 1 (`websearch`) or Tier 3 (Hub Research) and log a `[CREDIT-LOW]` warning to the Hivemind.

## §5 Error Handling Matrix (Search Protocol v1)
| Error | Meaning | Action |
|-------|---------|--------|
| **402** | Credits Exhausted | Fall back to Tier 1 $\rightarrow$ Tier 3. |
| **429** | Rate Limited | Exponential backoff (5s $\rightarrow$ 15s $\rightarrow$ 30s). |
| **500** | Server Error | Retry once $\rightarrow$ Fall back to Tier 1. |

---
*⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_firecrawl_credits ⬡ FINAL*
