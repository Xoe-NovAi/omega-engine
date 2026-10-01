# 🌐 Web Research Brief — Open Knowledge Gaps (2026-07-17)
**Agent**: `grok-cli/grok`  
**Method**: Live web search (2026-oriented queries) + map onto Omega open gaps  
**Companion**: `docs/research/KNOWLEDGE_GAP_MATRIX_20260717.md`  
**Free-tier copy**: `data/coordination/grok_cli/WEB_RESEARCH_KNOWLEDGE_GAPS_20260717.md`

---

## 1. D-282 — SQLite / WAL / PRAGMA / concurrency

### What the web says (2026 consensus)

| Practice | Source signal | Implication for Omega |
|----------|---------------|------------------------|
| **WAL + `synchronous=NORMAL`** | Android SQLite best practices (2026), PowerSync, phiresky tuning | Already correct in adapter |
| **`busy_timeout`** | Production baselines often **5s**; multi-process servers use longer | Code uses **30s** — good for multi-agent + researcher; Forge table at 5s is *too aggressive* for Hivemind contention |
| **`cache_size = -N` (KiB)** | Coddy production baseline ~**20MB** (`-20000`); server blogs allow larger | Live **512MB** (`-524288`) is **outlier-high** for 14Gi + zRAM + GGUF; **32MB (`-32768`)** remains the safer SSOT for 5700U |
| **`mmap_size`** | phiresky: large mmap = *virtual* address space, not necessarily RSS | 256–512MB fine; do not stack 512MB mmap + 512MB page cache blindly |
| **`BEGIN IMMEDIATE` on writes** | SQLite forum / 2026 Medium concurrency essays | Use for **write** transactions (prevents mid-tx upgrade races); **not** for pure reads (hurts concurrency) |
| **One writer** | Universal | Match Omega multi-process: IMMEDIATE + busy_timeout + retry |

### Recommended PRAGMA SSOT (web-informed, 5700U)

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=30000;        -- keep (multi-agent), not 5000
PRAGMA foreign_keys=ON;
PRAGMA temp_store=MEMORY;
PRAGMA cache_size=-32768;         -- 32MB page cache
PRAGMA mmap_size=268435456;       -- 256MB
PRAGMA wal_autocheckpoint=500;    -- more frequent under writers
PRAGMA journal_size_limit=67108864;
```

### Test design (web + prior advisory)

1. Writer starvation under concurrent readers  
2. Checkpoint vs upsert  
3. Multi-process disjoint upserts  
4. IMMEDIATE wins where DEFERRED races  

**Owner**: Roc / D-282.

---

## 2. D-283 — Agent memory tiers (Letta / MemGPT lineage)

### Architecture (stable through 2026)

| Tier | Letta / MemGPT | Omega mapping |
|------|----------------|---------------|
| **Core** | Always-in-context blocks (persona, human, custom) | `blocks.py` / `block_store` / `block_tools` |
| **Recall** | Conversation history on disk; searchable / windowed | **`recall.py` MISSING** |
| **Archival** | Explicit long-term semantic store (vector/tools) | `archival.py` skeleton |

Sources: Letta “Agent Memory” blog; 2026 comparison articles (Vectorize, EverMind); MemGPT OS hierarchy.

### Design constraints from web + Omega

- Core is **small and self-edited** (or second-agent reviewed for safety — Omega already documents this).  
- Recall is **not** archival: it is **dialogue chronology** + quality window, not free-form fact RAG.  
- Archival is **tool-mediated** insert/search (Letta: `archival_memory_*` / passages APIs).  
- Filesystem/RAG attachments are a separate path (Letta Filesystem 2025+) — do not conflate with Recall.

### Sleep-time compute

Industry trend: **off-critical-path consolidation** (summarize, promote, invalidate). Omega `SleepTimeAgent` skeleton aligns; wire only after RecallStore exists.

---

## 3. Power-law / forgetting (Recall decay)

### Science vs product

| Claim | Support |
|-------|---------|
| Human forgetting often **power-law-like** over long spans | Classic psych (Wixted/Ebbinghaus literature); product blogs (Shodh) |
| **Exponential** curves still used operationally | SuperMemo; 2026 Oblivion (arXiv) uses interaction-based / Ebbinghaus-style with reinforcement |
| Agent systems | Mem0: **search-time decay re-rank** (boost recent access, dampen unused); access-based forgetting preferred over hard delete |

### Recommendation for Omega Recall

Keep planned form:

```text
score = base * (1 + age_days) ** (-alpha)
```

with:

- `alpha` **per entity** in block metadata (0.01–0.60 band is fine as *product* range, not a physics constant)  
- **Reset/boost on access** (retrieval strength)  
- Prefer **re-rank at window()** over destructive delete until archival promotion  

Optional later: dual storage vs retrieval strength (Bjork) — overkill for Phase 2.

---

## 4. Hybrid search / RRF k=60

### Consensus (2026)

- Formula: `score(d) = Σ 1/(k + rank_r(d))`  
- **k=60** is the industry default (Cormack et al. 2009; Elasticsearch; Azure AI Search; ParadeDB; MariaDB 2026 docs)  
- Higher k → more **consensus**, less top-1 domination  
- RRF ignores raw score scales (critical when fusing BM25 + cosine)

### Omega status

**CLOSED as research gap**: `HybridSearchEngine(k=60)` matches SOTA. Do not retune k without A/B.  
**Ops note**: dual modules (`hybrid_search.py` vs `hybrid_search_engine.py`) — engineering cleanup, not algorithm gap.

---

## 5. D-284 — MCP Streamable HTTP + OAuth 2.1 PKCE

### Spec landscape (2025–2026)

| Piece | Finding |
|-------|---------|
| **Transports** | **stdio** (local) + **Streamable HTTP** (remote; 2025-06-18 era specs) |
| **Auth** | OAuth **2.1** for HTTP transports; **PKCE required** (S256); no implicit grant |
| **Roles** | MCP client = OAuth client; MCP server = resource server; separate auth server |
| **Discovery** | Auth server metadata; dynamic client registration common in guides |
| **SSE** | Legacy / partial; Streamable HTTP is the remote path — explains Firecrawl **405** class failures on pure SSE assumptions |

Sources: modelcontextprotocol.io authorization specs; Stack Overflow Blog Jan 2026; Auth0 / WorkOS / Prefect MCP OAuth guides; Keycloak+Go implementers.

### Sovereignty recommendations (unchanged, now web-backed)

1. Self-hosted IdP (Keycloak / Ory Hydra) for M7  
2. Token store: SQLite single-node first  
3. SHIELDMCP-style **mutating-tool** draft-then-commit (policy layer above OAuth scopes)  
4. Hub-level agent card before per-entity cards  
5. Dual-run period: Streamable HTTP primary, SSE deprecation  

**Code gap**: no `mcp_hub/` package — remap to real entrypoints (e.g. iris) before implement.

---

## 6. Pydantic v2 / WAD strictness (first_breath failure)

### Web facts

- `ConfigDict(extra='forbid'|'ignore'|'allow')` — default **ignore** in v2 docs  
- `extra='forbid'` is correct for **security** of untrusted config  
- Pydantic 2.12+ allows **per-call** `model_validate(..., extra='forbid')` overrides  
- Heritage WAD fields (`author`, `license`, `voices`, …) fail forbid unless model includes them or uses versioned allowlists

### Recommendation

Do **not** globally loosen to ignore. Prefer:

1. **Versioned WAD manifest schema** (`schema_version`)  
2. Explicit optional heritage fields on model  
3. Or staged loader: forbid on engine-owned keys, allow extras into `metadata: dict`

Fixes `test_first_breath_world_query` class of bugs without abandoning M2.

---

## 7. Speculative decode / local inference (P2)

### Direction

- Speculative / multi-token prediction (EAGLE-class, draft models) remains active research for local stacks  
- Omega test expects `speculative_decode` in `models.yaml` — **config gap**, not “SOTA unknown”  
- On 5700U: draft model size + thread contention with sqlite writers is the real constraint (ResourceGuard)

**Action**: P6 owns models.yaml section + path fixtures (ties to empty GGUF path tests).

---

## 8. Cross-gap decision table (for Kali / Triad)

| Decision | Web-backed answer | Omega action |
|----------|-------------------|--------------|
| cache_size | Prefer tens of MB on constrained laptops | D-282: 32MB SSOT |
| busy_timeout | 5s baseline apps; multi-writer apps higher | Keep 30s |
| BEGIN IMMEDIATE | Writes only | Audit query paths; keep write IMMEDIATE |
| RRF k | 60 | Keep |
| Recall vs Archival | Dialogue history vs facts | Implement `recall.py` greenfield |
| Decay | Power-law OK; access-boost better than hard delete | Metadata alpha + window re-rank |
| MCP remote | Streamable HTTP + OAuth2.1 PKCE | D-284 design; not Phase now |
| WAD extras | forbid needs schema for heritage | Versioned model / optional fields |

---

## 9. Sources (selected)

### SQLite
- https://sqlite.org/pragma.html  
- https://developer.android.com/topic/performance/sqlite-performance-best-practices  
- https://phiresky.github.io/blog/2020/sqlite-performance-tuning/  
- https://coddy.tech/docs/sqlite/pragma-settings  
- SQLite forum / concurrency essays on BEGIN IMMEDIATE (2024–2026)

### MCP
- https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization  
- https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/  
- Auth0 / WorkOS / Prefect MCP OAuth articles (2025–2026)

### Memory
- https://www.letta.com/blog/agent-memory/  
- Letta 2026 comparison pieces (Vectorize, EverMind)  
- Mem0 forgetting blog (2026)  
- Oblivion arXiv memory decay (2026)

### RRF
- Cormack et al. 2009 lineage via Azure / Elasticsearch / 2026 hybrid RAG posts  
- https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking  

### Pydantic
- https://docs.pydantic.dev/ (ConfigDict extra; v2.12 per-call extra)

---

## 10. What this changes in the master matrix

| Gap | Before | After web research |
|-----|--------|--------------------|
| PRAGMA cache 512MB | “probably too high” | **Confirmed** vs 2026 laptop baselines |
| busy_timeout 30s vs 5s | conflict | **Keep 30s** for Omega |
| RRF k=60 | “researcher said so” | **Industry default** — closed |
| Recall design | advisory only | Letta definition **reinforced** |
| MCP OAuth | advisory | **Spec-mandated PKCE** for HTTP |
| first_breath WAD | mystery | **extra=forbid vs heritage fields** |

---

*Web research pass complete. No Core code changes in this deliverable.*
