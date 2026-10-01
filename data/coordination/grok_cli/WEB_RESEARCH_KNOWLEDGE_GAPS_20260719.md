<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🌐 Web Research + Claim Verification — Knowledge Gaps (2026-07-19)

**Agent**: `grok-cli/grok`  
**Method**: Live verification via **SearXNG** + **omega-hub library_web_search** + **direct `web_fetch`** of primary sources  
**Note**: Built-in `web_search` returned **402 spending-limit** — sovereign fallback used (not silent synthesis).  
**Companions**:  
- Prior pass: `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20260717.md`  
- Matrix: `docs/research/KNOWLEDGE_GAP_MATRIX_20260717.md` (status partially stale — see §0)  
- Decision tools review: `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md`

---

## 0. Live codebase delta (since 2026-07-17 matrix)

| Claim in old matrix | Live 2026-07-19 | Status |
|---------------------|-----------------|--------|
| `recall.py` MISSING | **Present** (~793 LOC: `append`, `window`, `decay_pass`, power-law) | **CLOSED as missing-module gap** — wire/test/adoption still open |
| WAD first_breath / heritage fields | `MANIFEST_V2_OPTIONAL_FIELD_TYPES` + test **passes** | **CLOSED** (e80f6df lineage) |
| `speculative_decode` missing in models.yaml | **Present** (`gemma4_mtp` section) | **Likely CLOSED** as config gap (re-run full gemma test still recommended) |
| adapter `cache_size` 512MB | adapter **32MB** (`-32768`); archival/block_store/recall still **512MB** | **PARTIAL** — SSOT not global |
| concurrency tests file | **Still missing** `tests/test_sqlite_vec_concurrency.py` | **OPEN** |
| Decision tooling | Review shipped; no `DecisionEngine` code yet | **OPEN (implementation)** |

---

## 1. Claim verification matrix

Legend: **V** = verified primary source · **P** = partial / secondary · **R** = rejected or overstated · **U** = unconfirmed this pass

### 1.1 SQLite / D-282

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| S1 | Negative `cache_size=-N` means ~N KiB page cache | **V** | [sqlite.org PRAGMA cache_size](https://www.sqlite.org/pragma.html#pragma_cache_size): negative N → abs(N×1024) bytes |
| S2 | Default suggested cache is small (~2MB class) | **V** | Same page: default suggested `-2000` (~2MB) |
| S3 | 512MB page cache is high for 14Gi + GGUF + zRAM | **V** (engineering) | Official docs do not forbid large caches; **product risk** is RSS competition — prior advisory still holds |
| S4 | 32MB (`-32768`) is a sane laptop SSOT | **P** | Industry blogs cite tens of MB; **not** a SQLite-mandated value. Good for Omega 5700U |
| S5 | Only one writer; many concurrent readers (WAL) | **V** | [sqlite.org lang_transaction](https://www.sqlite.org/lang_transaction.html) §2.1 |
| S6 | `BEGIN IMMEDIATE` starts write lock immediately; DEFERRED upgrades later and can race | **V** | Same page §2.2: IMMEDIATE fails with SQLITE_BUSY if another writer active; DEFERRED may upgrade mid-tx |
| S7 | Use IMMEDIATE on pure reads | **R** | Hurts concurrency; docs imply read starts on SELECT under DEFERRED |
| S8 | `busy_timeout=30000` is “always correct” | **P** | Pragma exists; value is **workload-specific**. 30s OK for multi-agent; 5s is common app default but harsh for Hivemind |
| S9 | `wal_autocheckpoint=500` better than 1000 under write load | **P** | Plausible; not mandated by SQLite docs — keep as Omega preference |
| S10 | SSOT helper needed across modules | **V** (repo) | Live: adapter 32MB; archival/block_store/recall still 512MB |

**Omega action**: Extract `apply_pragma_stack(conn)` once; align all four modules; add concurrency tests (still open).

### 1.2 RRF / hybrid search

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| R1 | RRF score uses `1/(k + rank)` | **V** | Azure AI Search hybrid ranking (updated 2026-06/07) |
| R2 | **k≈60** is the common default / experimental sweet spot | **V** | Azure: “best when k set to small value such as 60”; industry posts cite Cormack 2009 + ES/OpenSearch/Weaviate defaults |
| R3 | RRF is score-scale agnostic (BM25 vs cosine) | **V** | Rank-based fusion — Azure + Elastic docs |
| R4 | Omega must retune k without A/B | **R** | Keep **k=60** until measured |

**Omega status**: `HybridSearchEngine(DEFAULT_RRF_K=60)` — **research closed**. Dual module files remain engineering debt.

### 1.3 Agent memory tiers (Letta / MemGPT lineage)

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| M1 | Core / Recall / Archival three-tier hierarchy is real product architecture | **V** | [Letta “Agent Memory”](https://www.letta.com/blog/agent-memory/) (2025; still canonical 2026 comparisons) |
| M2 | Core = in-context editable blocks | **V** | Letta blog |
| M3 | Recall = conversational history on disk, searchable | **V** | Letta blog |
| M4 | Archival = explicit long-term knowledge (vector/graph tools) | **V** | Letta blog |
| M5 | RAG alone is not “agent memory” | **V** | Letta: retrieval is a tool, not memory itself |
| M6 | Sleep-time agents for async memory refinement | **V** | Letta sleep-time compute narrative |
| M7 | Power-law `score = base * (1+age)^(-α)` is scientifically mandatory | **P** | Psych literature is power-law-like; products also use exponential / access-based re-rank. Formula is **product choice** |
| M8 | α ∈ 0.01–0.60 is a physics constant | **R** | Heuristic product band only |
| M9 | Access-boost / re-rank better than hard delete for warm memory | **P** | Mem0-style practice; aligns with Letta “search when needed” |

**Omega status**: `recall.py` implements power-law + window — **design gap → implement gap (wiring, tests, ContextBuilder)**.

### 1.4 MCP Streamable HTTP + OAuth 2.1 PKCE (D-284)

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| C1 | MCP HTTP auth based on **OAuth 2.1** subset | **V** | [MCP Authorization 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) |
| C2 | Auth **optional** overall; HTTP SHOULD conform when supported | **V** | Same spec |
| C3 | STDIO should **not** use this OAuth flow (env credentials) | **V** | Same |
| C4 | **PKCE required** for clients | **V** | Spec: “MCP clients **MUST** implement PKCE” |
| C5 | Resource Indicators (RFC 8707) `resource` param required | **V** | Spec MUST on auth + token requests |
| C6 | Protected Resource Metadata (RFC 9728) required for servers | **V** | Spec MUST |
| C7 | Token passthrough forbidden | **V** | Spec security section |
| C8 | Streamable HTTP replaced pure SSE as remote path | **P** | Transport evolution widely documented; 405 class failures on SSE-only clients still a valid operational signal |

**Omega action**: D-284 design remains valid; implement against **iris/hub real paths**, not fictional `mcp_hub/`.

### 1.5 Pydantic / WAD strictness

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| P1 | Default `extra` is **ignore** | **V** | [Pydantic models docs](https://pydantic.dev/docs/validation/latest/concepts/models/) |
| P2 | `extra='forbid'` rejects unknown keys | **V** | Same |
| P3 | Per-call `extra` override on validate | **V** | Docs: validate methods accept optional `extra` |
| P4 | Loosen to `allow` for heritage WADs | **R** (security) | Prefer versioned optional fields (shipped V2 allow-list) |

**Omega status**: first_breath **PASS** — gap closed.

### 1.6 ADR / Decision tooling claims

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| A1 | ADRs should not be rewritten when decision changes; supersede + link | **V** | [Martin Fowler ADR](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html) (2026-03-24): “should not be modified… linked to a superseding decision” |
| A2 | Status: proposed → accepted → superseded | **V** | Same |
| A3 | Store in repo as numbered markdown/YAML | **V** | Fowler + adr-tools culture |
| A4 | Full MAD role/speech-act protocol required for T0 | **R** | Research frameworks ≠ minimal ADR tooling |
| A5 | Numeric Belief Engine u/a meaningful in single-inference MEDITATE | **R** as “true BE” | See §1.7 |

### 1.7 Belief Engine (arXiv:2605.15343)

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| B1 | Paper exists (May 2026) with uptake `u` and anchoring `a` | **V** | [arXiv:2605.15343](https://arxiv.org/abs/2605.15343) abstract |
| B2 | BE is log-odds update over structured evidence | **V** | Abstract |
| B3 | Multi-turn / multi-agent deliberation context | **V** | Abstract |
| B4 | Specific RMSE numbers (0.393 / 0.658 / 0.006) from grounded meditate | **U** | **Not in abstract**; treat as **unverified secondary** until PDF body audited |
| B5 | Dropping numeric u/a into a single prompt is equivalent to BE | **R** | BE requires extract→update loop + inspectable state; single-shot roleplay is at best a qualitative scaffold |

**Aligns with** Decision Tools Review: T1-scaffold = prompt only; real BE = T2+.

### 1.8 Speculative decode / local inference

| # | Claim | Verdict | Evidence |
|---|--------|---------|----------|
| I1 | Speculative / MTP remains active local-LLM research | **P** | Domain knowledge; not re-audited papers this pass |
| I2 | Omega gap was missing models.yaml section | **V** (repo) | `speculative_decode.gemma4_mtp` now present |
| I3 | Empty GGUF path tests may still fail without models on disk | **P** | Environment-dependent |

---

## 2. Open knowledge gaps (research-actionable)

### P0 — still open after verification

| ID | Gap | Web verdict | Next action |
|----|-----|-------------|-------------|
| **P0-PRAGMA** | PRAGMA stack not single SSOT (3 modules still 512MB) | 32MB safer on constrained host | Shared helper + converge |
| **P0-CONC** | No concurrency test suite | IMMEDIATE vs DEFERRED must be tested | `tests/test_sqlite_vec_concurrency.py` |
| **P0-PATH** | config_resolver adoption incomplete | Engineering, not web | Phase III-B file list |

### P1 — design closed / implement open

| ID | Gap | Web verdict | Next action |
|----|-----|-------------|-------------|
| **P1-RECALL-WIRE** | recall.py exists; ContextBuilder / SleepTime / promote paths | Letta tiers verified | Integration tests + wiring |
| **P1-DECISION** | DecisionEngine not built | ADR supersession verified | Implement under Conditional GO review |
| **P1-OPS-INFER** | Provider fabric operational knowledge | N/A web | Read providers.yaml / ResourceGuard |

### P2 — horizon

| ID | Gap | Web verdict | Next action |
|----|-----|-------------|-------------|
| **P2-MCP** | OAuth2.1 PKCE hub | Spec **verified** | D-284 when pain |
| **P2-BE** | Real Belief Engine loop | Paper **verified**; numeric RMSE U | Only multi-step deliberation |
| **P2-CROSSPOL** | Cross-entity L3 share | No new web blocker | After Recall maturity |
| **P2-EMB-DIM** | Qdrant vs embed dims | Ops probe | P2 Persistence |

### CLOSED this pass (research + code)

| ID | Item |
|----|------|
| RRF k=60 | Industry default confirmed Azure 2026 |
| WAD V2 heritage / first_breath | Code + test |
| Recall module existence | Code present |
| MCP PKCE / OAuth2.1 shape | Spec fetch |
| ADR supersession rule | Fowler 2026 |
| BE paper existence | arXiv |

---

## 3. Corrected recommendations (replace stale matrix rows)

### 3.1 PRAGMA SSOT (unchanged recommendation, stronger evidence)

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=30000;
PRAGMA foreign_keys=ON;
PRAGMA temp_store=MEMORY;
PRAGMA cache_size=-32768;          -- 32 MiB — not 512 MiB on 14Gi host
PRAGMA mmap_size=268435456;        -- 256 MiB VA; do not stack with huge page cache
PRAGMA wal_autocheckpoint=500;
PRAGMA journal_size_limit=67108864;
```

Apply via **one function** to: `sqlite_vec_adapter`, `archival`, `block_store`, `recall`.

### 3.2 Write transactions

```text
Writes: BEGIN IMMEDIATE → work → COMMIT  (retry on SQLITE_BUSY)
Reads:  no IMMEDIATE; rely on WAL snapshot reads
```

### 3.3 Decision tooling (web-backed)

- Supersede, don’t rewrite accepted bodies (Fowler).  
- Minimal status patch (`superseded` + link) is acceptable operational compromise.  
- Do not import full MAD speech-act graphs for T0.

### 3.4 MEDITATE / BE

- **Do not** treat YAML `uptake/anchoring` floats as calibrated BE without multi-step extract/update.  
- Scaffold qualitative stance hints by **slot**, not mythic entity names (M2).

---

## 4. Tool-chain honesty

| Tool | Result |
|------|--------|
| `web_search` (Grok) | **402** personal-team spending limit |
| `searxng_search` | Used (mixed relevance on some queries) |
| `omega-hub library_web_search` | Used (RRF confirmation) |
| `web_fetch` | Used (SQLite, MCP, Pydantic, Letta, Azure, arXiv, Fowler) |

No claim in §1 is invented to fill a tool outage. **U** marks remain **U**.

---

## 5. Sources (primary)

| Topic | URL |
|-------|-----|
| SQLite PRAGMA | https://www.sqlite.org/pragma.html |
| SQLite transactions | https://www.sqlite.org/lang_transaction.html |
| Azure RRF | https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking |
| Elastic RRF | https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion |
| MCP Authorization | https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization |
| Pydantic models / extra | https://pydantic.dev/docs/validation/latest/concepts/models/ |
| Letta agent memory | https://www.letta.com/blog/agent-memory/ |
| Belief Engine | https://arxiv.org/abs/2605.15343 |
| ADR (Fowler) | https://martinfowler.com/bliki/ArchitectureDecisionRecord.html |

---

## 6. What Kali / implementers should do next

1. **D-282 close**: SSOT pragma helper + 4 concurrency tests (web fully supports IMMEDIATE-on-write).  
2. **Recall Phase 2b**: wire + test existing `recall.py` (module gap closed).  
3. **Decision T0**: implement under Conditional GO (ADR rule verified).  
4. **Do not re-open** RRF k, MCP PKCE shape, or WAD forbid philosophy as research unknowns.  
5. **Audit** grounded-meditate BE RMSE numbers against PDF before citing in strategy.

---

*⬡ OMEGA ⬡ GROK-CLI ⬡ WEB-RESEARCH + CLAIM-VERIFY ⬡ 2026-07-19*  
*Fallback chain: web_search(402) → searxng + library_web_search + web_fetch*
