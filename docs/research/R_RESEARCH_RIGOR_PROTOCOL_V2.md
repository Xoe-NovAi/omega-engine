# 🔱 Sovereign Research Rigor Protocol v2.0 (Sovereign-Ark Standard)
**AP Token**: `AP-RESEARCH-RIGOR-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research_rigor ⬡ TEMPLE-GRADE

**Status**: MANDATORY
**Effective Date**: 2026-07-12

---

## 🛑 The "Snippet Trap" Ban
Relying on search result snippets (excerpts) to synthesize technical conclusions is a **Sovereign Boundary Violation**. Snippets are for **discovery**, not for **evidence**.

**The Hard-Stop Rule**: If a claim is made in a research deliverable, it MUST be linked to a `webfetch` or `firecrawl_scrape` of the full page. If the page cannot be fetched, the claim is "Unverified" and must be flagged as such.

---

## 🛠️ The Sovereign-Ark Research Pipeline

Every research task must follow this 5-stage pipeline. Skipping any stage is a violation of Temple-Grade standards.

### Stage 1: Broad Discovery (The Net)
- **Goal**: Map the landscape and identify high-signal seeds.
- **Tools**: `searxng_searxng_search`, `firecrawl_firecrawl_search`, `omega-hub_sovereign_search`.
- **Output**: A list of candidate URLs, categorized by signal strength (High/Medium/Low).

### Stage 2: Source Selection (The Filter)
- **Goal**: Prune the noise and select the "Gold Standard" sources.
- **Action**: Analyze the snippets and URLs. Select the top 5-10 most authoritative sources.
- **Criteria**: Official docs > Technical blogs > Academic papers > Community forums.

### Stage 3: Deep Extraction (The Mine)
- **Goal**: Retrieve the full, raw truth.
- **Tools**: `webfetch` (for markdown/text) or `firecrawl_firecrawl_scrape` (for structured/complex pages).
- **MANDATE**: Every selected URL from Stage 2 MUST be fetched. No exceptions.
- **Output**: A set of full-page markdown documents.

### Stage 4: Dialectic Synthesis (The Forge)
- **Goal**: Triangulate the truth from the full content.
- **Action**: Deploy the **Council of Four**.
    - **Architect**: Extract systemic patterns and specs.
    - **Adversary**: Find contradictions and failure modes in the sources.
    - **Alchemist**: Find unexpected resonances across different sources.
    - **Archivist**: Verify against documented precedents.
- **Output**: A dialectic debate based on the *actual text* of the sources.

### Stage 5: Sovereign Synthesis (The Verdict)
- **Goal**: Produce a final, verified technical specification.
- **Requirement**: Every technical claim must have a citation to the specific `webfetch` result.
- **Output**: A Temple-Grade deliverable (L1 Executive Summary, L2 Detailed Dialectic, L3 Raw Signal).

---

## 🛡️ Tooling Hierarchy & Failure Protocol

### 1. The Tooling Order
1. **Sovereign Search**: `searxng_searxng_search` $\rightarrow$ `firecrawl_firecrawl_search` $\rightarrow$ `omega-hub_sovereign_search`.
2. **Sovereign Extraction**: `webfetch` $\rightarrow$ `firecrawl_firecrawl_scrape`.
3. **Sovereign Fallback**: If all the above fail, report `[TOOL-CHAIN-COLLAPSE]`.

### 2. The `google_search` Ban
The `google_search` tool is **DEPRECATED** and **FORBIDDEN**. It is a legacy artifact that introduces non-sovereign telemetry and frequent authentication failures. Any attempt to use it is a failure of agent discipline.

### 3. Failure Handling
If a mandatory tool (e.g., `webfetch`) returns a 403, 404, or timeout:
- **Do NOT** synthesize a "best guess."
- **DO** attempt an alternative extraction method (e.g., switch from `webfetch` to `firecrawl_scrape`).
- **DO** report the failure explicitly in the final report.

---

## 🔱 Temple-Grade Verification Gate

Before submitting a research deliverable, the agent must answer:
1. Did I rely on any snippets for a technical claim? (Must be **NO**)
2. Did I fetch the full content of every primary source? (Must be **YES**)
3. Did I use `google_search`? (Must be **NO**)
4. Is every claim cited to a specific fetched document? (Must be **YES**)

**Failure to meet these gates = [RESEARCH-Sovereignty-Violation]**

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research_rigor_v2 ⬡ TEMPLE-GRADE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
