# 🔱 Firecrawl Skill Audit & Consolidation Report
**Version**: 1.0.0
**Status**: PROPOSED
**Audit Date**: 2026-06-24

## 📉 Current State Analysis

### The "Bloat" Inventory
The current `.agents/skills/` directory contains **30+ Firecrawl-related skills**. 
These are divided into two distinct categories:
1. **Core Capabilities** (e.g., `firecrawl-scrape`, `firecrawl-search`): Direct wrappers for API endpoints.
2. **Workflow Templates** (e.g., `firecrawl-lead-gen`, `firecrawl-market-research`): Prompt-heavy guides that instruct the agent on *how* to use the core capabilities for a specific business outcome.

### The Redundancy Problem
Workflow skills like `firecrawl-company-directories` do not provide new *tools*; they provide new *instructions*. 
- **Cognitive Load**: The agent must search through 30+ skills to find the "right" one, even though they all use the same 6 underlying tools.
- **Maintenance Debt**: Updating the core CLI syntax requires updating every single workflow skill.
- **Overlap**: `firecrawl-lead-gen` and `firecrawl-company-directories` are 90% identical in their execution pattern.

---

## 🛠️ Proposed Canonical Skill Set

To eliminate cognitive bloat, we will collapse the 30+ skills into a **Three-Tier Hierarchy**.

### Tier 1: The Core Toolkit (`firecrawl-core`)
A single, unified skill (or a small set of core skills) that provides raw access to the endpoints.
- `firecrawl-search`
- `firecrawl-scrape`
- `firecrawl-map`
- `firecrawl-crawl`
- `firecrawl-interact`
- `firecrawl-agent`
- `firecrawl-parse`

### Tier 2: The Workflow Library (`firecrawl-workflows`)
A single skill containing a **Library of Templates**. Instead of a separate skill for "Lead Gen", the agent loads the `firecrawl-workflows` skill and selects the appropriate template:
- **Template: Lead Generation** (Targets, Field Mapping, Deduplication)
- **Template: Market Research** (Financials, Trends, Comparison Tables)
- **Template: Company Directories** (Sourcing, Filtering, CSV Export)
- **Template: SEO Audit** (Metadata, Heading Structure, Sitemap Analysis)

### Tier 3: The Utilities (`firecrawl-utils`)
Supporting tools for data management.
- `firecrawl-download` (Bulk local saving)
- `firecrawl-qa` (Browser-based validation)

---

## 🔌 Integration Gap: The Sovereign Wrapper

The current implementation relies on `Bash(firecrawl *)`. This is fragile and exposes the raw CLI to the agent.

### Missing Component: `.opencode/firecrawl_wrapper.sh`
We require a platform-agnostic wrapper to act as the "Sovereign Gatekeeper".

**Required Functional Specifications**:
1. **Key Encapsulation**: Handle `FIRECRAWL_API_KEY` internally so it never appears in LLM logs.
2. **Sovereign Guard (Credit Limiter)**:
    - Intercept `crawl` and `map` requests.
    - If `--limit` is missing, inject a default (e.g., 50).
    - Warn the agent if a request is likely to cost > 100 credits.
3. **Output Standardization**:
    - Automatically save all outputs to `.firecrawl/` using a consistent naming convention: `{timestamp}_{modality}_{hash}.json`.
    - Ensure JSON output is always pretty-printed for LLM readability.
4. **Escalation Logic**:
    - Provide a simplified command `firecrawl escalate <url>` that attempts `scrape` $\rightarrow$ `map` $\rightarrow$ `interact` automatically until content is retrieved.
5. **Automatic Feedback Loop**:
    - Hook into `search` calls to automatically prompt the agent for `search-feedback` after the results are processed.

---

## 🎯 Implementation Roadmap

1. **Phase 1 (Consolidation)**: 
   - Create `firecrawl-core` and `firecrawl-workflows`.
   - Deprecate the 20+ use-case skills.
2. **Phase 2 (Wrapper)**: 
   - Implement `.opencode/firecrawl_wrapper.sh`.
   - Update `allowed-tools` in core skills to use the wrapper.
3. **Phase 3 (Verification)**: 
   - Run a "Sovereign Stress Test" to ensure the credit limiter prevents "Crawl Traps".
