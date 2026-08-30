<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Search Dossier: Exa (Neural Search)
**Version**: 1.0.0
**Classification**: Sovereign Navigation Layer
**Role in SSP V2**: The Compass (Semantic Discovery & High-Precision Navigation)

---

## ⚙️ Technical Architecture

Exa is a **neural search engine**. Unlike traditional engines that use keyword matching (BM25/TF-IDF), Exa indexes the web as a massive graph of embeddings.

### Neural vs. Keyword Search
- **Keyword Search (SearXNG)**: Finds pages that contain the *exact words* of the query. Great for "find the manual for X model."
- **Neural Search (Exa)**: Finds pages that share the same *meaning* or *intent* as the query. Great for "find research papers that argue against X theory."

### Core Mechanisms
- **Embedding-Based Retrieval**: Every page is represented as a high-dimensional vector. The query is embedded, and the closest vectors are returned.
- **Link-Graph Analysis**: Exa uses the structure of the web (who links to whom) to determine the "authority" and "relevance" of a page.
- **Semantic Filtering**: Allows filtering based on the *type* of content (e.g., "technical documentation," "blog post") rather than just keywords.

---

## 🛠️ Expert Usage Patterns

### 1. The "Semantic Seed" Technique
Instead of a query, provide a URL of a high-quality page you already trust.
- **Pattern**: `similarity_search(url="https://arxiv.org/abs/...", query="similar research")`.
- **Outcome**: Exa finds pages that are semantically similar to the *content* of the seed URL, bypassing the limitations of search terms.

### 2. Precision Filtering
Narrow the search space to high-trust domains.
- **Domain Filters**: Restrict results to `.gov`, `.edu`, or a specific list of trusted technical blogs.
- **Recency Gates**: Use strict date filters to avoid stale AI-generated content from 2023.

### 3. "Needle in the Haystack" Discovery
Use neural search to find niche content that lacks standardized terminology.
- **Example**: Searching for "unconventional methods for cooling Zen 2 CPUs" will find forum posts and obscure blogs that a keyword search for "Zen 2 cooling" might miss.

---

## ⚖️ Strengths & Weaknesses

| Strength | Description | Weakness | Description |
| :--- | :--- | :--- | :--- |
| **Precision** | Finds content by meaning, not words. | **Black Box** | Opaque ranking algorithms. |
| **Discovery** | Uncovers niche, high-value sources. | **Cost** | High API cost per request. |
| **Clean Data** | Returns high-quality, curated links. | **Coverage** | Not as comprehensive as Google. |
| **Semantic** | Understands complex intent. | **Lack of Exactness** | Can miss specific "exact phrase" matches. |

---

## 🛡️ Sovereign Usage

To maximize sovereignty and minimize reliance on centralized providers:
1. **Discovery Layer Only**: Use Exa solely as a "Discovery Layer." Use it to find 5-10 high-precision seed URLs, then immediately switch to Firecrawl for extraction.
2. **Minimize "Black Box" Time**: Do not rely on Exa's summaries. Fetch the raw content and perform the synthesis using a local LLM.
3. **Local Embedding Mirror**: When Exa finds a high-value cluster of pages, scrape them all and generate local embeddings. This effectively "downloads" a slice of the neural web into your own sovereign vector store.
4. **Hybrid Search**: Always combine Exa (Neural) with SearXNG (Keyword) to ensure that semantic "vibes" are backed by factual "exact matches."
