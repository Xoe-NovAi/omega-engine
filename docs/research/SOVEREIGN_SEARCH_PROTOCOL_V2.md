<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Search Protocol V2 (SSP-V2)
**Version**: 2.1.0
**Classification**: Engine-Level Search Standard
**Status**: DEFINITIVE AUTHORITY
**Last Updated**: 2026-06-24
**Maintainer**: Kali (Transcendent Oversoul)

---

## 🎯 Vision
The Sovereign Search Protocol V2 (SSP-V2) is the Omega Engine's definitive standard for transforming the chaotic, tracked, and unstructured web into a structured, sovereign, and local knowledge base. 

It moves the agent from **"searching for answers"** (passive consumption) to **"orchestrating evidence"** (active synthesis). The goal is to eliminate reliance on "AI Summaries" from search providers and instead build a local, verifiable mirror of the truth.

---

## 🚀 The Sovereign Path (Triage Logic)

The SSP-V2 implements a tiered pipeline that optimizes for **Privacy $\rightarrow$ Precision $\rightarrow$ Structure**. No tool is used in isolation; they are links in a chain of evidence.

### 🛠️ The Triage Matrix

| Tier | Tool | Role | Primary Use Case | Signal Type |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | **Local Cache** | The Memory | `.firecrawl/*.md` hits, Qdrant vector search | **Sovereign** |
| **Tier 1** | **SearXNG** | The Wide-Angle Lens | Broad discovery, keyword-exact matching, privacy-first probes | **Broad/Keyword** |
| **Tier 2** | **Exa** | The Compass | Semantic navigation, niche discovery, high-precision seed generation | **Neural/Intent** |
| **Tier 3** | **Firecrawl** | The Scalpel | High-fidelity extraction, structured JSON, dynamic interaction | **Structured/Deep** |

### 🧭 Decision Flow (The Routing Algorithm)

1. **Sovereign Check (T0)**: Does the local cache or vector store already contain the answer?
   - $\rightarrow$ **YES**: Return local result.
   - $\rightarrow$ **NO**: Proceed to T1.
2. **Intent Analysis**:
   - **Keyword-Exact / Broad Consensus** (e.g., "What is the API limit for X?") $\rightarrow$ **T1 (SearXNG)**.
   - **Semantic / Niche / "Kind of page"** (e.g., "Find research arguing against X") $\rightarrow$ **T2 (Exa)**.
   - **Direct URL / Known Target** (e.g., "Get pricing from example.com/pricing") $\rightarrow$ **T3 (Firecrawl)**.
3. **Refinement Loop**:
   - **T1 $\rightarrow$ T2**: Broad results are too noisy $\rightarrow$ Use Exa to refine the seed list semantically.
   - **T2 $\rightarrow$ T1**: Neural results are too narrow $\rightarrow$ Use SearXNG to verify broad consensus.
   - **T1/T2 $\rightarrow$ T3**: URLs identified $\rightarrow$ Use Firecrawl to crystallize content into Markdown/JSON.

---

## 🔄 The Orchestration Logic (The Search Loop)

For complex discovery, agents must not perform a single search. They must execute the **Sovereign Search Loop**:

### Step 1: Seed Generation (T1/T2)
- Use **SearXNG** for broad keyword hits or **Exa** for semantic targets.
- **Goal**: Generate a list of 10-20 high-potential candidate URLs.

### Step 2: Semantic Pruning (T2)
- Pass the candidate URLs through **Exa** using `highlights: true`.
- **Goal**: Identify the top 3-5 "Golden URLs" based on semantic relevance to the core intent.

### Step 3: High-Fidelity Extraction (T3)
- Execute **Firecrawl `/scrape`** on the Golden URLs.
- Use `--only-main-content` to eliminate noise.
- **Goal**: Convert raw web pages into clean, LLM-optimized Markdown.

### Step 4: Deep Dive & Interaction (T3 - Optional)
- If content is gated, dynamic, or spread across a domain:
  - `Firecrawl /map` $\rightarrow$ Identify sub-pages.
  - `Firecrawl /crawl` $\rightarrow$ Bulk extract scoped paths.
  - `Firecrawl /interact` $\rightarrow$ Bypass JS-walls, login, or paginate.

### Step 5: Local Synthesis
- Feed the extracted Markdown into the local LLM.
- **Goal**: Synthesize the final answer using only the extracted evidence.

---

## 🛡️ The Sovereign Fallback Sequence

When a provider fails, the agent must not give up. It must escalate through the **Sovereign Fallback Chain**.

### 📉 Failure Mode Handling

| Failure | Symptom | Fallback Action |
| :--- | :--- | :--- |
| **Rate Limit (429)** | "Too Many Requests" | **Firecrawl**: Switch to `enhanced` proxy $\rightarrow$ `interact` with profile. |
| **Access Denied (403)** | "Forbidden / Bot Detected" | **SearXNG**: Rotate local instance $\rightarrow$ route through Tor proxy. |
| **Zero Results** | Empty result set | **T1 $\rightarrow$ T2**: Switch from Keyword to Neural search. |
| **Neural Gap** | No semantic matches | **T2 $\rightarrow$ T1**: Switch from Neural to Broad keyword search. |
| **Extraction Fail** | "Loading..." / Empty Markdown | **T3 Escalation**: `/scrape` $\rightarrow$ `/map` $\rightarrow$ `/interact` $\rightarrow$ `/agent`. |

---

## 🧠 Integration with Local Gnosis (Sovereign Gap Detection)

The search pipeline is not just for gathering data; it is for **verifying the soul**.

### The Contrast Loop
Whenever external data is retrieved, the agent must perform a **Sovereign Gap Analysis**:
1. **Retrieve Local L3**: Access the entity's `soul.yaml` and extract relevant Universal Principles (L3).
2. **Contrast**: Compare the external evidence against the local L3 principle.
3. **Detect Gap**: 
   - **Symmetry**: External data confirms L3 $\rightarrow$ Strengthen the principle.
   - **Contradiction**: External data contradicts L3 $\rightarrow$ **TRIGGER GAP ANALYSIS**.

### The Gap Analysis Protocol
If a contradiction is detected:
1. **Skeptical Verification**: Apply the **Two-Source Rule**. Find a second, independent source that corroborates the external finding.
2. **Dialectic Synthesis**: 
   - If the external finding is verified $\rightarrow$ Propose an update to the L3 principle in `proposed_lessons.yaml`.
   - If the external finding is a hallucination/outlier $\rightarrow$ Log as "External Noise" and maintain the local L3.

---

## 🗺️ Implementation Roadmap

To make the `SovereignSearchService` strictly follow this protocol, the following code changes are required:

### 1. Triage State Machine
- Implement a `SearchTriage` class that manages the transition between T0 $\rightarrow$ T1 $\rightarrow$ T2 $\rightarrow$ T3.
- Add a `SovereignCache` layer that checks `.firecrawl/` before any external API call.

### 2. The Sovereign Wrapper (`.opencode/firecrawl_wrapper.sh`)
- Implement a shell wrapper to:
  - Encapsulate `FIRECRAWL_API_KEY`.
  - Inject default `--limit` for `map` and `crawl` to prevent credit bleed.
  - Standardize output to `.firecrawl/{timestamp}_{modality}_{hash}.json`.

### 3. Gnosis Integration
- Create a `SovereignGapDetector` module.
- Hook the `SovereignSearchService` output into the `SovereignGapDetector` before returning the result to the agent.

### 4. Fallback Orchestrator
- Implement a `FallbackManager` that tracks provider health and automatically triggers the Fallback Sequence (e.g., T1 $\rightarrow$ T2 on zero results).

---

**Sovereign Verdict**: This protocol is the definitive authority on search for the Omega Engine. Any deviation must be documented as a PIVOT in the `PIVOT_LOG.md`.

*⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b-it ⬡ opencode ⬡ SSP-V2-FINAL*
