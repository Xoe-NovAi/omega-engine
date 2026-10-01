<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Exa Sovereign Master Guide: Neural Retrieval & Semantic Discovery

⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_research ⬡ EXA-GUIDE

## 📋 Executive Summary (The Cheat Sheet)

Exa is a **neural search engine** designed specifically for LLMs. Unlike traditional keyword search (BM25), Exa retrieves pages based on **semantic meaning**, allowing agents to find "the kind of page that would contain X" rather than just pages containing the word "X".

### ⚡ Quick-Start Matrix
| Goal | Search `type` | Content Mode | Freshness | Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Real-time Chat** | `instant` | `highlights: true` | Default | $\sim$250ms |
| **General Discovery** | `auto` | `highlights: true` | Default | $\sim$1s |
| **Deep Research** | `deep` | `text: {maxCharacters: 15k}` | `maxAgeHours: 0` | 4-15s |
| **Complex Analysis** | `deep-reasoning` | `outputSchema: { ... }` | `maxAgeHours: 0` | 12-40s |

### 🚩 Critical Alerts
- **DEPRECATED**: `useAutoprompt` is dead. Remove it from all prompts.
- **NESTING**: `text`, `highlights`, and `summary` MUST be nested inside the `contents` object on the `/search` endpoint.
- **RESTRICTIONS**: `category: "company"` and `"people"` do NOT support date filters or `excludeDomains`.

---

## 🏛️ Detailed Dialectic: Perspective Triangulation

### 1. The Architect (Systemic Logic)
**Focus: Token Efficiency & Latency Orchestration**
The core strength of Exa is its **Content Compression Pipeline**. By shifting from `text` (full page) to `highlights` (relevant snippets), agents achieve a $\sim$10x reduction in token cost without significant loss in RAG performance. 
- **Systemic Win**: The tiered latency model (`instant` $\rightarrow$ `deep-reasoning`) allows the Omega Engine to implement an **Adaptive Search Pipeline**: 
  1. `instant` for initial triage.
  2. `auto` for factual gathering.
  3. `deep` for synthesis and structured extraction.
- **Structured Integration**: The `outputSchema` parameter transforms search from a "retrieval" task into a "synthesis" task, eliminating the need for a second LLM pass to structure the results.

### 2. The Adversary (Critical Rigor)
**Focus: Failure Modes & Hidden Constraints**
- **The "Freshness Trap"**: Defaulting to cached content is fast, but for breaking news, `maxAgeHours: 0` is mandatory. However, this introduces a significant latency penalty and potential live-crawl failures.
- **The Deprecation Gap**: Many agents still hallucinate `useAutoprompt`. Relying on this flag leads to "invisible failures" where the agent believes it is optimizing a query that the engine is ignoring.
- **Category Blind-spots**: The strict constraints on `company` and `people` categories (no `excludeDomains`, no date filters) create a "hard wall" for agents attempting to perform temporal research on specific organizations.

### 3. The Alchemist (Creative Synthesis)
**Focus: Divergent Retrieval Patterns**
- **The "Zoom-In" Pattern**: Request `highlights: true` and `text: true` simultaneously. Use highlights for rapid semantic routing across 20 results, then isolate the top 3 for full-text deep analysis.
- **Multi-Angle Synthesis**: Leveraging `additionalQueries` in `deep` mode allows an agent to attack a problem from multiple semantic vectors (e.g., "technical specs", "user complaints", "competitor comparisons") in a single API call, synthesizing a 360-degree view of the truth.

### 4. The Archivist (Historical Truth)
**Focus: Evolution of the Neural Paradigm**
The transition from `type: "neural"` (legacy) to `type: "auto"` marks a shift in the search paradigm: optimization is no longer a "mode" the user selects, but a systemic property of the engine. The deprecation of `useAutoprompt` confirms that the "prompt engineering" of the query has been moved from the client-side (flag) to the server-side (latent optimization).

---

## 📉 Raw Signal: Technical Specifications

### 🔍 Search Type Matrix
| Type | Latency | Reasoning Depth | Use Case |
| :--- | :--- | :--- | :--- |
| `instant` | $\sim$250ms | Low | Autocomplete, Voice, Chat triage |
| `fast` | $\sim$450ms | Low-Mid | User-facing search, fast factual lookups |
| `auto` | $\sim$1s | Mid | General purpose research (Default) |
| `deep-lite` | 4s | Mid-High | Lightweight synthesis, structured summaries |
| `deep` | 4-15s | High | Multi-step research, complex synthesis |
| `deep-reasoning` | 12-40s | Maximum | Hard research tasks, decision-making support |

### 📦 Content Extraction Trade-offs
| Mode | Token Cost | Latency | Fidelity | Best For |
| :--- | :--- | :--- | :--- | :--- |
| `highlights` | $\text{Low} (\times 0.1)$ | $\text{Low}$ | $\text{Medium}$ | Agent workflows, factual extraction |
| `summary` | $\text{Low}$ | $\text{Mid}$ | $\text{Low}$ | Quick overviews, high-level triage |
| `text` | $\text{High}$ | $\text{Mid}$ | $\text{High}$ | Deep analysis, nuance, broad research |

### 🕒 Freshness Controls
- **`maxAgeHours: 0`**: Forces livecrawl. Essential for breaking news.
- **`startPublishedDate`**: ISO 8601. Filters results by publication date.
- **`startCrawlDate`**: ISO 8601. Filters results by discovery date.

---

## 🚀 Agent-Facing Quick Reference (Sovereign Injection)

Copy and paste this block directly into the system prompt of any agent utilizing Exa for maximum token efficiency and zero-hallucination parameter usage.

```xml
<exa_sovereign_protocol>
  <parameter_guard>
    - NEVER use "useAutoprompt" (Deprecated).
    - ALWAYS nest "text", "highlights", and "summary" inside the "contents" object.
    - For "category": "company" or "people", REMOVE "excludeDomains" and date filters.
  </parameter_guard>

  <neural_zoom_pattern>
    1. TRIAGE PHASE: Use type="auto", contents={"highlights": true}. Scan 10-20 results to identify high-signal URLs.
    2. ZOOM PHASE: Use type="deep", contents={"text": {"maxCharacters": 15000}}, maxAgeHours: 0 for the top 3-5 targets.
    3. SYNTHESIS PHASE: Use type="deep" + outputSchema for structured data extraction.
  </neural_zoom_pattern>

  <query_optimization>
    - Use NEURAL queries: Describe the TYPE of page you want.
    - Bad: "AI research 2024 transformer"
    - Good: "High-impact research papers from 2024 describing novel innovations in transformer architectures"
  </query_optimization>
</exa_sovereign_protocol>
```

---

## 🤖 Agent-Facing XML Prompt Snippets


Include these snippets in the system prompt of any agent using Exa to prevent hallucinations and optimize costs.

### 1. The "Correct Parameter" Guard
```xml
<exa_parameter_constraints>
  - NEVER use "useAutoprompt". It is deprecated.
  - ALWAYS nest "text", "highlights", and "summary" inside the "contents" object.
  - WRONG: { "query": "...", "highlights": true }
  - RIGHT: { "query": "...", "contents": { "highlights": true } }
  - When using "category": "company" or "people", REMOVE "excludeDomains" and date filters to avoid 400 errors.
</exa_parameter_constraints>
```

### 2. The "Research Depth" Strategy
```xml
<exa_search_strategy>
  - FAST TRIAGE: Use type="fast", contents={"highlights": true} to identify relevant URLs.
  - DEEP DIVE: Use type="deep", contents={"text": {"maxCharacters": 15000}}, maxAgeHours: 0 for the final target URLs.
  - STRUCTURED EXTRACT: Use type="deep" + outputSchema for final data synthesis.
</exa_search_strategy>
```

### 3. The "Neural Query" Pattern
```xml
<exa_query_optimization>
  - Exa is NEURAL, not keyword. Avoid "keyword-stuffing".
  - Instead of: "AI research papers 2024 transformer architecture"
  - Use: "High-impact research papers from 2024 describing novel innovations in transformer architectures"
  - Describe the TYPE of page you want to find.
</exa_query_optimization>
```

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
