# 🔱 Search Dossier: SearXNG (Local Metasearch)
**Version**: 1.0.0
**Classification**: Sovereign Discovery Layer
**Role in SSP V2**: The Wide-Angle Lens (Broad, Privacy-Preserving Discovery)

---

## ⚙️ Technical Architecture & Privacy Model

### Architecture
SearXNG is a **metasearch engine**. It does not maintain its own index of the web. Instead, it acts as a high-performance proxy that aggregates results from hundreds of search services (Google, Bing, DuckDuckGo, Wikipedia, etc.) in real-time.

- **Aggregation Layer**: Dispatches parallel requests to configured engines.
- **Unification Layer**: Normalizes disparate result formats into a single, unified stream.
- **Privacy Shield**: Strips identifying information (User-Agent, IP, Cookies) before forwarding requests to the upstream engines.
- **Storage**: Uses a local **Valkey/Redis** instance for result caching and request limiting (preventing bot detection).

### Privacy Model
SearXNG achieves "Zero-Tracking" by:
1. **Proxying**: The upstream engine sees the SearXNG server's IP, not the user's.
2. **Non-Profiling**: No user accounts, no cookies, and no history stored on the server.
3. **Sovereign Hosting**: When self-hosted, the user owns the logs and the configuration, eliminating third-party telemetry.

---

## 🛠️ Expert Query Patterns

### 1. Engine & Category Filtering (The `!` Operator)
Directly control where the search is performed to reduce noise.
- **Specific Engine**: `!wp paris` $\rightarrow$ Search only Wikipedia for "paris".
- **Category Search**: `!map paris` $\rightarrow$ Search only in the 'map' category.
- **Chained Filters**: `!map !ddg !wp paris` $\rightarrow$ Search both DuckDuckGo and Wikipedia within the map category.

### 2. Language Filtering (The `:` Operator)
Force results from a specific locale to find non-English perspectives.
- **Pattern**: `:fr query` $\rightarrow$ Search for "query" in French.

### 3. External Bangs (`!!`)
Leverage the massive library of DuckDuckGo bangs for instant navigation.
- **Pattern**: `!!wfr query` $\rightarrow$ Jump directly to French Wikipedia.

### 4. Automatic Redirect (`!!` space)
The "Feeling Lucky" mode for agents.
- **Pattern**: `!! query` $\rightarrow$ Immediately redirect to the first result.

---

## 🔌 Integration Patterns for Local-First Agents

### 1. The API Proxy Pattern
Agents should query the SearXNG JSON API rather than the HTML frontend.
- **Endpoint**: `/search?q=query&format=json`
- **Workflow**: `Agent $\rightarrow$ Local SearXNG $\rightarrow$ [Multi-Engine Aggregation] $\rightarrow$ Unified JSON $\rightarrow$ Agent`.

### 2. The "Clean-Sweep" Discovery
Use SearXNG to generate a list of 10-20 high-confidence URLs, which are then passed to a structured scraper (Firecrawl) for deep extraction.

---

## ⚖️ Strengths & Weaknesses

| Strength | Description | Weakness | Description |
| :--- | :--- | :--- | :--- |
| **Privacy** | Total anonymity via proxying. | **Noise** | Aggregation can lead to duplicates. |
| **Breadth** | Access to 200+ engines. | **Unstructured** | Returns links/snippets, not data. |
| **Sovereignty** | 100% self-hostable. | **Fragility** | Upstream engines may block IP. |
| **Cost** | Free (Open Source). | **Latency** | Limited by the slowest engine. |

---

## 🛡️ Sovereign Usage

To maximize sovereignty and minimize reliance on centralized providers:
1. **Self-Host via Docker**: Never use a public instance for sensitive research.
2. **Local Valkey**: Deploy a local Valkey container to manage caches.
3. **Custom Engine Set**: Edit `settings.yml` to remove engines known for aggressive tracking or poor quality.
4. **Tor Integration**: Route the SearXNG instance through a Tor proxy to further obfuscate the source of the requests.
