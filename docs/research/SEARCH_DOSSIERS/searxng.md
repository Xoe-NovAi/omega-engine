# 🔱 Sovereign Search Intelligence: SearXNG Technical Dossier
**Status**: VERIFIED
**Sovereignty Tier**: Tier 0 (Absolute - Self-Hostable)
**Protocol Alignment**: Local-First / No-Telemetry

## 1. Architecture & Core Mechanics
SearXNG is a **metasearch engine** (aggregator). It does not maintain its own index of the web; instead, it acts as a sophisticated proxy between the user and a vast array of upstream search services.

### Core Workflow:
`Query` $\to$ `SearXNG Instance` $\to$ `Parallel Requests to N Engines` $\to$ `Result Aggregation` $\to$ `Anonymization` $\to$ `User`

### Key Mechanical Features:
- **Engine Aggregation**: Supports up to 276 search services (Google, Bing, DuckDuckGo, Brave, etc.).
- **Request Anonymization**: Generates random browser profiles for every request and strips cookies/tracking parameters before forwarding to upstream engines.
- **Privacy Layer**: Can be configured to route all outbound traffic through Tor or a set of SOCKS5 proxies to hide the instance's IP.
- **Result De-duplication**: Aggregates results from multiple sources and removes duplicates to provide a unified, clean list.

## 2. Sovereignty Analysis
SearXNG represents the gold standard for search sovereignty.

- **Self-Hosting**: Fully open-source and designed for self-hosting. Can be deployed via Docker/Podman on minimal hardware.
- **Data Privacy**: Zero user tracking. No profiling. No centralized database of user queries.
- **Umbilical Cord Risk**: Extremely low. While it depends on upstream engines, the *control* of the aggregation and the *privacy* of the user are entirely local.
- **Local-First Alignment**: Perfect. It allows the Omega Engine to maintain a "Private Search Gateway" that prevents Big Tech from linking search queries to a specific user/IP.

## 3. API Specification & Integration Patterns
SearXNG provides a simple, stateless HTTP API.

### Endpoints:
- `GET/POST /search`
- `GET/POST /`

### Key Parameters:
| Parameter | Type | Description |
|-----------|------|------------------------------------------------------|
| `q` | String | **Required**. The search query. Supports engine-specific syntax (e.g., `site:github.com`). |
| `format` | Enum | `json`, `csv`, `rss`. **Required for agentic use**. |
| `engines` | String | Comma-separated list of specific engines to query. |
| `categories` | String | Comma-separated list of categories (e.g., `it`, `science`, `news`). |
| `language` | String | ISO language code. |
| `pageno` | Integer | Pagination index (default: 1). |
| `time_range` | Enum | `day`, `month`, `year`. |

### Integration Pattern for Omega Engine:
SearXNG should be used as the **Broad Discovery Layer (Tier 1)**.
`Omega Search` $\to$ `Local SearXNG` $\to$ `Upstream Engines` $\to$ `Filtered Link List` $\to$ `Firecrawl Deep Extraction`.

## 4. Capability Mapping
- **Metasearch**: Superior. Ability to "blend" results from 200+ sources.
- **Local-First**: Absolute.
- **Privacy**: High (Sovereign).
- **Configuration**: High. Administrator can enable/disable specific engines per category.

## 5. Performance Benchmarks
- **Latency**: Variable. Latency is determined by the slowest requested upstream engine.
- **Accuracy**: High (due to aggregation), but results are "shallow" (links and snippets only).
- **Cost**: Free (excluding hosting costs).

## 6. Integration Gaps for Omega Engine
- **No Deep Extraction**: SearXNG provides links, not content. It must be paired with a tool like Firecrawl for content hydration.
- **No Neural Search**: It relies on the keyword/semantic logic of upstream engines.
- **CAPTCHA Risk**: Public instances often hit CAPTCHAs. A sovereign instance requires a robust proxy rotation strategy to remain stable.
