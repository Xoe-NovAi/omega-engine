# 🔱 Firecrawl Skill Audit & Refactoring Proposal
**Date**: 2026-06-24
**Orchestrator**: jem
**Context**: Sovereign Search Protocol V2 (SSP) Alignment

## 🔍 Current State Analysis
The `.opencode/skills/` directory contains 27+ Firecrawl-related skills. These are currently organized by **Business Use Case** (e.g., `firecrawl-lead-gen`, `firecrawl-market-research`, `firecrawl-company-directories`).

### Issues Identified:
1. **Cognitive Bloat**: Too many skills for the agent to choose from, leading to "skill paralysis" or suboptimal selection.
2. **Functional Overlap**: Many use-case skills are just wrappers around the same core API calls (`/scrape` or `/crawl`).
3. **SSP Misalignment**: The current structure focuses on *what* to extract (the business goal) rather than *how* to extract (the technical modality), which conflicts with the SSP's "The Scalpel" (Sovereign Extraction) philosophy.
4. **Maintenance Overhead**: Updating the core Firecrawl API requires updating dozens of individual skill files.

---

## 🏗️ Proposed Refactored Architecture

The skills should be reorganized to align with the **Core Modalities** of the Firecrawl API and the **SSP V2 Routing Logic**.

### 1. Core Modality Skills (The "Primitives")
These skills should be the only ones directly exposed as "tools" for the agent. They map 1:1 to the technical capabilities of the "Scalpel."

| Skill Name | API Endpoint | Purpose |
| :--- | :--- | :--- |
| `firecrawl-scrape` | `/scrape` | Single page $\rightarrow$ Markdown/JSON. |
| `firecrawl-crawl` | `/crawl` | Site-wide $\rightarrow$ Bulk Markdown/JSON. |
| `firecrawl-map` | `/map` | Domain $\rightarrow$ URL List. |
| `firecrawl-interact` | `/interact` | Live Session $\rightarrow$ Dynamic Interaction. |
| `firecrawl-agent` | `/agent` | Autonomous $\rightarrow$ Structured Data. |

### 2. Workflow Templates (The "Recipes")
The existing business use-case skills should be converted from **Skills** to **Workflow Templates**. A template is a structured prompt that tells the agent how to combine the Core Modality Skills to achieve a goal.

**Example: `lead-gen` Workflow**
- **Step 1**: Use `firecrawl-map` to find the `/team` or `/about` pages.
- **Step 2**: Use `firecrawl-scrape` with a specific `lead_gen` JSON schema.
- **Step 3**: Synthesize results into a CRM-ready list.

---

## 🚀 Implementation Roadmap

1. **Deprecation Phase**: Mark all use-case skills (e.g., `firecrawl-lead-gen`) as `[DEPRECATED]`.
2. **Primitive Hardening**: Ensure the 5 Core Modality Skills are robust, well-documented, and align with the SSP's "Sovereign Usage" patterns (Local LLM extraction, Markdown caching).
3. **Template Migration**: Move the logic from the deprecated skills into a `docs/workflows/firecrawl/` directory as Markdown templates.
4. **Pruning**: Delete the redundant skill files from `.opencode/skills/`.

## ⚖️ Expected Outcome
- **Reduced Latency**: Faster skill selection for the agent.
- **Increased Reliability**: Centralized logic for API interactions.
- **SSP Compliance**: Clear alignment between the "Sovereign Path" and the toolset.
