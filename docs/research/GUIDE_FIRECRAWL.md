# 🔱 Firecrawl Sovereign Master Guide
**Version**: 1.0.0
**Status**: ACTIVE
**Focus**: The "Golden Path" for AI-Driven Web Extraction

## ⚡ Executive Summary (The Cheat Sheet)

Firecrawl is not a "scraper"; it is a **Web Context API**. To maximize information gain and minimize credit bleed, follow the **Sovereign Escalation Protocol**.

### Modality Mapping & Golden Path
| Step | Modality | Tool | Use Case | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Discovery** | `/search` | Find URLs when you don't have one. | 2 credits / 10 results |
| **2** | **Extraction** | `/scrape` | Get clean markdown from a specific URL. | 1 credit / page |
| **3** | **Mapping** | `/map` | Find specific sub-pages on a large site. | 1 credit / page |
| **4** | **Bulk** | `/crawl` | Extract an entire section (e.g., `/docs`). | 1 credit / page |
| **5** | **Interaction**| `/interact` | Bypass JS-walls, login, paginate, click. | 2 credits / min |
| **6** | **Autonomy** | `/agent` | Complex, multi-step autonomous research. | Dynamic / Preview |

**The Golden Path**: `search` $\rightarrow$ `scrape` $\rightarrow$ `map` $\rightarrow$ `crawl` $\rightarrow$ `interact` $\rightarrow$ `agent`.
*Never start with `crawl` if `map` can narrow the scope. Never start with `interact` if `scrape` works.*

---

## 🏛️ Detailed Dialectic (Perspective Triangulation)

### 1. The Architect (Systemic Logic)
**Verdict**: The current implementation is fragmented. The "Skill Bloat" (30+ separate skills) creates cognitive noise. 
**Strategic Recommendation**: Move from "Use-Case Skills" (e.g., `firecrawl-lead-gen`) to "Capability-Based Skills" supported by a "Workflow Library". The logic should be: `Core API` $\rightarrow$ `Sovereign Wrapper` $\rightarrow$ `Workflow Template`.

### 2. The Adversary (Critical Rigor)
**Verdict**: "Credit Bleed" is the primary failure mode. An unconstrained `/crawl` on a high-depth site can liquidate a budget in minutes.
**Failure Modes**:
- **The Crawl Trap**: Recursive links or infinite calendars causing unlimited page fetches.
- **The JS-Wall**: `/scrape` returning "Loading..." or "Enable JavaScript" for SPAs.
- **The Token Overflow**: Large `/crawl` results exceeding the LLM context window.
- **The Shadow-Block**: Enhanced proxies (5 credits) failing against high-tier Cloudflare/Akamai walls.

### 3. The Alchemist (Creative Synthesis)
**Verdict**: The real power lies in **Modality Chaining**.
**Synthesis Patterns**:
- **Deep Discovery**: `/map --search "X"` $\rightarrow$ Filter URLs $\rightarrow$ `/scrape` (Parallel) $\rightarrow$ Synthesize.
- **Stateful Extraction**: `/scrape` $\rightarrow$ `scrapeId` $\rightarrow$ `/interact` (Login) $\rightarrow$ `/interact` (Navigate) $\rightarrow$ `/interact` (Extract).
- **Autonomous Pivot**: `/agent` for initial landscape $\rightarrow$ `/scrape` for high-fidelity verification of the agent's findings.

### 4. The Archivist (Historical Truth)
**Verdict**: Firecrawl represents the transition from *Document Extraction* (BeautifulSoup/Scrapy) to *Context Retrieval*.
**Historical Context**: Earlier tools focused on HTML selectors (CSS/XPath), which were brittle. Firecrawl's approach—rendering the page and using LLMs to structure the output—shifts the burden from the developer to the model, trading compute cost for architectural resilience.

---

## 📡 Raw Signal (Technical Specs)

### Endpoint Matrix
| Endpoint | Primary Input | Key Output | Critical Options |
| :--- | :--- | :--- | :--- |
| `/search` | `query` | `JSON (urls, snippets)` | `--scrape` (hydrate results), `--sources` |
| `/scrape` | `url` | `Markdown / JSON` | `--only-main-content`, `--wait-for <ms>` |
| `/map` | `url` | `URL List` | `--search <query>`, `--limit` |
| `/crawl` | `url` | `Bulk Markdown` | `--include-paths`, `--max-depth`, `--limit` |
| `/interact`| `scrapeId` | `Page State / Content` | `--prompt`, `--code`, `--profile` |
| `/agent` | `prompt` | `Structured JSON` | `--schema`, `--urls`, `--max-credits` |

### Credit & Latency Matrix
| Modality | Cost | P95 Latency | Risk Level |
| :--- | :--- | :--- | :--- |
| Search | 2 cr / 10 res | ~3-5s | Low |
| Scrape | 1 cr / page | ~2-8s | Low |
| Map | 1 cr / page | ~5-15s | Medium |
| Crawl | 1 cr / page | Async (mins) | High (Credit Bleed) |
| Interact | 2 cr / min | ~10-30s / step | Medium |
| Agent | Dynamic | 2-5 mins | Medium (Token Cost) |

---

## 🤖 Agent-Facing Integration (XML Prompt Snippets)

Inject these into the system prompt of any agent using Firecrawl to enforce the Sovereign Protocol.

```xml
<firecrawl_protocol>
  <escalation_path>
    search -> scrape -> map -> crawl -> interact -> agent
  </escalation_path>
  <constraints>
    - Use 'firecrawl_search' to discover URLs.
    - Use 'firecrawl_scrape' for single pages. Use '--only-main-content' to reduce noise.
    - Use 'firecrawl_map' with '--search' to find specific pages on large domains before crawling.
    - Use 'firecrawl_crawl' only for scoped paths (e.g., /docs) with a strict '--limit'.
    - Use 'firecrawl_interact' ONLY if scrape fails or interaction (clicks/forms) is required.
    - Use 'firecrawl_agent' for high-complexity autonomous research with a JSON schema.
  </constraints>
  <budget_guard>
    - Always specify '--limit' for map and crawl.
    - Use 'firecrawl_feedback' after every search to reclaim 1 credit.
  </budget_guard>
</firecrawl_protocol>
```
