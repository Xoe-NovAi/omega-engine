# 🔱 Expert Guide: SearXNG (Local Metasearch)
**Classification**: Sovereign Discovery Layer
**Role**: The Wide-Angle Lens

## 🎯 Overview
SearXNG is the primary entry point for broad, privacy-preserving web discovery. It aggregates results from hundreds of engines, stripping tracking data and providing a unified, sovereign view of the web.

## 🛠️ Expert Usage Patterns

### 1. Precision Filtering (The `!` Operator)
Stop wasting tokens on noise. Directly target the source.
- **Targeted Engine**: `!wp [query]` $\rightarrow$ Search only Wikipedia.
- **Category Focus**: `!map [query]` $\rightarrow$ Search only in the 'map' category.
- **Combined Filters**: `!map !ddg [query]` $\rightarrow$ Search DuckDuckGo within the map category.

### 2. Locale & Perspective Shifting (The `:` Operator)
Bypass the English-centric bubble to find primary sources.
- **Pattern**: `:fr [query]` $\rightarrow$ Search in French.
- **Sovereign Tip**: Use this to find regional technical documentation or forum discussions that haven't been translated.

### 3. Instant Navigation (The `!!` Operator)
For agents, the "Feeling Lucky" mode is the fastest path to a known source.
- **Pattern**: `!! [query]` $\rightarrow$ Direct redirect to the top result.
- **Bangs**: `!!wfr [query]` $\rightarrow$ Jump directly to French Wikipedia.

## 🔌 Sovereign Integration
To integrate SearXNG into a sovereign agent workflow:
1. **JSON API**: Always use `/search?q=[query]&format=json`.
2. **Local-First**: Self-host via Docker. Never use public instances for sensitive research.
3. **Cache Strategy**: Use a local Valkey/Redis instance to prevent bot detection and reduce latency.
4. **Tor Routing**: For maximum anonymity, route the SearXNG container through a Tor proxy.

## ⚖️ Decision Matrix: When to use SearXNG
| Use Case | Recommendation | Why? |
| :--- | :--- | :--- |
| **Broad Discovery** | ✅ Primary | Best for seeing "what's out there" across multiple engines. |
| **Exact Phrase Match** | ✅ Primary | Keyword-based search is superior for specific IDs or quotes. |
| **Privacy-Critical** | ✅ Primary | Zero-tracking architecture. |
| **Structured Data** | ❌ Avoid | Returns snippets; requires a second pass with Firecrawl. |
| **Semantic Intent** | ⚠️ Secondary | Can find the "vibe" but lacks the precision of neural search. |
