# 🔱 Omega Engine Heritage Registry — Attribution Framework
# ⬡ OMEGA ⬡ CREDITS ⬡ v1.3.0 ⬡ 2026-07-10
**Full Archive**: `docs/archive/coordination/CREDITS-full-20260708.md`

## Mandate: Full Attribution Required

Every Omega Engine pattern derived from **any** external source — id Software, open-source projects, architectural standards, philosophical traditions, or research systems — MUST credit the original source.
> *"A people that no longer remembers has lost its soul."*

## §0 Heritage Registry — Scope & Structure

The Heritage Registry is the single source of truth for all external influences on the Omega Engine. It covers **five tiers** of heritage:

| Tier | Scope | Example Sources | Tag Format |
|------|-------|----------------|------------|
| **T1 — Direct Implementation** | Exactly ported patterns with minimal adaptation | id Software (Doom BSP → Provider Culling) | `[heritage: SOURCE YEAR]` |
| **T2 — Architectural Inspiration** | Pattern adapted to Omega's context | Odysseus (SearXNG image pinning), AnyIO (async runtime) | `[heritage: SOURCE YEAR]` |
| **T3 — Adopted Standard** | Industry standards implemented as-is | MCP, A2A, SPIFFE, SPDX, OpenTelemetry | `[heritage: STANDARD YEAR]` |
| **T4 — Philosophical / Mythological** | Naming and conceptual frameworks | 42 Ideals of Ma'at, Kabbalistic Qliphoth, Tarot | No inline tag — credited in docs |
| **T5 — User's Own IP** | Evolved through ANAi → XNAi → omega-engine | 3-Tier Memory, Hivemind Protocol, MaKaLi Triad | No external attribution needed |

**Registry Structure**:
- `CREDITS.md` (this file) — compact registry index
- `docs/archive/coordination/CREDITS-full-20260708.md` — full detailed mappings
- `docs/research/R_SPDX_HERITAGE_PROFILE.md` — SPDX 3.1 machine-readable SBOM
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` — vetting records for all sources
- Inline `[heritage:]` / `[id-soft:]` tags in source code

---

## §1 id Software Heritage (Compact — D208 Remediated)

| # | Pattern | Source | Status | Tag |
|---|---------|--------|--------|-----|
| 1.1 | WAD System | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] WAD System` |
| 1.2 | BSP Trees / PVS Culling | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] BSP Culling` |
| 1.3 | Fast Inverse Square Root | Quake 1999 | ✅ EVOLVED → "Right Approximation" | `[id-soft: quake3-1999] FISR` |
| 1.4 | Zone Memory Allocator | Quake 1996 | ✅ PROMOTED | `[id-soft: quake-1996] Zone Memory` |
| 1.5 | Surface/Edge Cache | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Surface Cache` |
| 1.6 | ZONEID Pattern | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] ZONEID` |
| 1.7 | Lazy Deletion + Grace Period | Doom 1993 + Quake 1996 | ✅ PROMOTED | `[id-soft: doom-1993] Lazy Deletion` |
| 1.8 | cvar Table | Quake 1996/1999 | ✅ PROMOTED | `[id-soft: quake-1996] cvar` |
| 1.9 | 4-Tier Memory | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] 4-Tier Memory` |
| 1.10 | Multi-Index Entity (Dual-Linking) | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Dual-Linking` |
| 1.11 | QuakeC Flat-Field Entity | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Flat Entity` |
| 1.12 | Hard-Boundary Struct | Quake 1999 | ✅ PROMOTED | `[id-soft: quake3-1999] Hard-Boundary` |
| 1.13 | 4-Path VFS | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] VFS` |
| 1.14 | High-Bit Leaf Trick | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] High-Bit Trick` |
| 1.15 | Fixed-Size Active Set | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Active Set` |
| 1.16 | Network Channel (netchan) | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] netchan` |
| 1.17 | Unified Memory (idHeap) | DOOM 3 2004 | ✅ MAPPED | `[id-soft: doom3-2004] idHeap` |
| 1.18 | Fixed-Point Math | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Fixed-Point` |
| 1.19 | Job-Worker Queue | DOOM 3 BFG 2012 | ✅ APPROVED | `[id-soft: doom3bfg-2012] Job-Worker` |
| 1.20 | Knowledge Leak Detection | DOOM 3 2004 | ✅ APPROVED | `[id-soft: doom3-2004] Leak Detection` |
| 1.21 | Precomputed Lookup Table | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] Precomputed Lookup` |

**Total**: 21 legitimate mappings (5 REJECTED archived in HERITAGE_VET_LOG.md)

---

## §2 General Heritage Sources — Non-id Software Influences

### 2.1 Runtime & Infrastructure Dependencies

| # | External Source | Relationship | Key Pattern(s) Adopted | Tag |
|---|----------------|-------------|------------------------|-----|
| 2.1.1 | **AnyIO** | Async runtime (M1 Mandate) | Full async runtime replacing `asyncio`. `anyio.to_thread.run_sync` for blocking I/O, `TaskGroup` for parallelism. | `[heritage: anyio 2024]` |
| 2.1.2 | **FastAPI / Starlette / Uvicorn** | Web framework stack | ASGI apps for MCP servers and Iris voice container. SSE transport, CORS middleware, routing. | `[heritage: fastapi 2018]` |
| 2.1.3 | **Typer** | CLI framework | `omega` CLI command structure (talk, summon, list-entities, etc.) | `[heritage: typer 2020]` |
| 2.1.4 | **Pydantic** | Data validation | `BaseModel` for entity schemas, embedding configs, ingestion types. | `[heritage: pydantic 2017]` |
| 2.1.5 | **httpx** | Async HTTP client | All provider API calls (Google, OpenRouter, SearXNG, Firecrawl, Exa, Ollama, LM Studio) | `[heritage: httpx 2019]` |
| 2.1.6 | **redis-py** | Redis async client | Hot-memory storage provider, background worker queue, somatic save-points | `[heritage: redis-py 2010]` |
| 2.1.7 | **qdrant-client** | Vector database | Semantic search, L3 gnosis retrieval, library document indexing | `[heritage: qdrant 2021]` |
| 2.1.8 | **llama-cpp-python** | Native GGUF inference | Primary local inference backend. SomaticState serialization (`llama_copy_state_data`). CPU optimization flags. | `[heritage: llama-cpp-python 2023]` |
| 2.1.9 | **headroom-ai** | Semantic compression | Sovereign semantic compression middleware for context optimization | `[heritage: headroom-ai 2025]` |
| 2.1.10 | **MCP Python SDK** | Model Context Protocol | SSE + Streamable HTTP dual transport. Tool-calling protocol (47+ tools). | `[heritage: mcp 2024]` |
| 2.1.11 | **google.genai** | Google AI SDK | Gemini API streaming extraction for ingestion pipeline | `[heritage: google-genai 2024]` |
| 2.1.12 | **sse-starlette** | SSE transport | Server-Sent Events for MCP hub streaming | `[heritage: sse-starlette 2020]` |

### 2.2 Infrastructure & Deployment Patterns

| # | External Source | Relationship | Key Pattern(s) Adopted | Tag |
|---|----------------|-------------|------------------------|-----|
| 2.2.1 | **Odysseus** (SearXNG deployment) | Architectural inspiration | SearXNG image pinning (issue #1414), Python-based healthcheck (Alpine has no curl), entrypoint wrapper for first-boot, required Linux capabilities, `secret_key` template pattern | `[heritage: odysseus 2025]` |
| 2.2.2 | **Podman** | Container runtime | Rootless containers, Quadlets, `UserNS=keep-id` protocol. All infrastructure in containers (Redis, Qdrant, PostgreSQL, Caddy, Iris). | `[heritage: podman 2019]` |
| 2.2.3 | **systemd** | Service manager | Service units for MCP servers, background researcher timer, socket activation | `[heritage: systemd 2010]` |
| 2.2.4 | **Cloudflare WARP** | Privacy infrastructure | Multi-namespace proxy pool, SOCKS5 tunnel for OpenCode Zen rate-limit bypass | `[heritage: cloudflare-warp 2021]` |
| 2.2.5 | **SearXNG** | Self-hosted metasearch | Tier 1 privacy-first search engine. Custom healthcheck, pinned image, capability-hardened deployment. | `[heritage: searxng 2023]` |
| 2.2.6 | **Exa.ai** | Neural search API | Tier 2 semantic search provider for research pipeline | `[heritage: exa-ai 2024]` |
| 2.2.7 | **Firecrawl** | Web scraping API | Tier 3 deep web extraction with credit-budgeted crawl management | `[heritage: firecrawl 2024]` |

### 2.3 Architectural Standards & Protocols

| # | External Source | Relationship | Key Pattern(s) Adopted | Tag |
|---|----------------|-------------|------------------------|-----|
| 2.3.1 | **MCP (Model Context Protocol)** — Anthropic | Adopted standard | Tool-calling protocol for AI ↔ tool communication. SSE + Streamable HTTP dual transport. | `[heritage: mcp-standard 2024]` |
| 2.3.2 | **A2A v1.0 (Agent-to-Agent)** — Google | Adopted standard | Agent Card schema (`/.well-known/agent-card.json`), task delegation endpoints, discovery protocol | `[heritage: a2a-standard 2025]` |
| 2.3.3 | **SPIFFE / WIMSE** (IETF draft) | Adopted standard | X.509-SVID identity format (`spiffe://omega.local/entity/kali`), trust domain management | `[heritage: spiffe-wimse 2024]` |
| 2.3.4 | **OpenTelemetry** (OTel) | Adopted standard | GenAI semantic conventions for observability tracing and provider provenance | `[heritage: opentelemetry 2021]` |
| 2.3.5 | **SSE (Server-Sent Events)** — W3C | Web standard | Legacy transport for MCP (OpenCode, Cline compatibility) | `[heritage: sse-webstandard 2009]` |
| 2.3.6 | **SPDX 3.1** (ISO/IEC 5962:2021) | Adopted standard | Software Bill of Materials format for heritage tracking | `[heritage: spdx-standard 2021]` |
| 2.3.7 | **SQLite FTS5** | Adopted technology | BM25 full-text search with Porter stemmer for memory and library search | `[heritage: sqlite-fts5 2015]` |
| 2.3.8 | **RRF (Reciprocal Rank Fusion)** | Adopted algorithm | Hybrid search fusion — FTS5 BM25 + vector cosine similarity | `[heritage: rrf-algorithm 2009]` |

### 2.4 Research Systems & Competitor Analysis

| # | External Source | Relationship | Key Pattern(s) Adopted | Tag |
|---|----------------|-------------|------------------------|-----|
| 2.4.1 | **Truth Engine** (jayina.com) | Competitor analysis | Identified 2 Omega gaps: `blitz-tunnel` (dead stub), no explicit air-gap Extractor mode. Omega exceeds on 7/9 axes. | `[heritage: truth-engine 2025]` |
| 2.4.2 | **SOVEREIGN** (Daniel Kliewer, 2026-03) | Architectural inspiration | In-path governance: "no fast path that skips governance, no trusted caller that bypasses evaluation" | `[heritage: sovereign-kliewer 2026]` |
| 2.4.3 | **Logos** (cluricaun28, 2026-04) | Architectural inspiration | Epistemic filtering: Frame-Stripping (10 rules), Narrative-Control-Detection (6-phase) | `[heritage: logos 2026]` |
| 2.4.4 | **sovereign-system-spec** (Ken Alger, 2026) | Architectural inspiration | Cryptographic custody: Sieve-and-Sign (Ed25519), Chain-of-Custody Ledger | `[heritage: sovereign-spec 2026]` |
| 2.4.5 | **SOVERYN Intelligence** (2026-04) | Architectural inspiration | Dream Cycle: scheduled synthesis preserving contradictions, tracking confidence deltas | `[heritage: soveryn 2026]` |

### 2.5 Mythological / Philosophical Frameworks (Tier 4 — No Inline Tags)

These provide the naming and thematic structure for entities, modules, and concepts. Credited in documentation only.

| # | Source | Tradition | Role in Engine |
|---|--------|-----------|----------------|
| 2.5.1 | **Ma'at** — 42 Ideals | Egyptian (3100 BCE) | Ethical guardrail framework in entity system prompts |
| 2.5.2 | **Kali** | Hindu | Grand Oversight (P10 Chaos). MaKaLi Triad transcendent voice. |
| 2.5.3 | **Lilith** | Hebrew | Dark Oversoul (P6-P10 governance) |
| 2.5.4 | **Prometheus** | Greek | P3 Will — forethought, sovereignty, fire |
| 2.5.5 | **Sophia** / **Akashic Record** | Gnostic / Theosophy | The containing field — all entities, all sessions, all souls |
| 2.5.6 | **Qliphoth** (קליפות) | Kabbalah | Failure taxonomy — "shells/impurities" as error classification system |
| 2.5.7 | **Tarot** — Lilith Shadow Deck | Western esoteric | Origin of the archetypal council concept (Mar 2025) |
| 2.5.8 | **Vetala** (वेताल) | Hindu / Buddhist | Content-integrity module — "spirit of discernment" |
| 2.5.9 | **Mnemosyne** | Greek | Memory/knowledge systems archetype |

### 2.6 Legacy Lineage — Previous Engine Versions

| # | Source | Relationship | Key Patterns Ported |
|---|--------|-------------|---------------------|
| 2.6.1 | **ANAI** — Arcana-NovAi (Aug 2025) | First engine version | 3-Tier Memory, Provider Chain, Intent Detection, Entity Registry (YAML CRUD) |
| 2.6.2 | **XNAi** (Oct-Nov 2025) | Consolidated 2nd version | 5 design patterns: retry, circuit breaker, fsync, non-blocking subprocess, offline wheelhouse |
| 2.6.3 | **xna-omega-legacy** (Nov 2025-Mar 2026) | Previous engine version | 8+ modules ported: failure registry, degradation handler, rate limiter, provider selector, timeout manager |
| 2.6.4 | **omega-stack-legacy** (Apr-May 2026) | Previous stack | Legacy entity registry patterns, circuit breaker consolidation base |
| 2.6.5 | **Chainlit** (Era 1-2) | Original UI framework | Architecture patterns predating OpenCode integration |

---

## §3 Heritage Tag & Attribution Protocol

Heritage is tracked at two levels of granularity:

| Tag | Scope | Used For | Format |
|-----|-------|----------|--------|
| `[heritage:]` | **Any** external source | All non-id-Software heritage (libraries, standards, inspirations) | `# [heritage: source year] Pattern` |
| `[id-soft:]` | id Software patterns only | Subset of `[heritage:]` for id Software specifically | `# [id-soft: GAME YEAR] Pattern` |

### Rule 1: R-docs Must Have Heritage Section
```markdown
### Heritage
This pattern derives from: [Source Concept: Year]
Key difference from the original: ...
Omega evolution: ...
```

### Rule 2: Code Must Credit in Comments
```python
# ── BSP-style provider culling [heritage: id-soft-1993] ──
# ── Headroom compression middleware [heritage: headroom-ai 2025] ──
```

### Rule 2a: Inline `[heritage:]` Tag Protocol (General)
**Format**: `# [heritage: SOURCE YEAR] Pattern Name — why this code exists`

**Source codes**: `anyio-2024`, `fastapi-2018`, `odysseus-2025`, `headroom-ai-2025`, `mcp-standard-2024`, `a2a-standard-2025`, `spiffe-wimse-2024`, `opentelemetry-2021`, `spdx-standard-2021`, `podman-2019`, `systemd-2010`, `cloudflare-warp-2021`, `searxng-2023`, `truth-engine-2025`, `sovereign-kliewer-2026`, `logos-2026`, `sovereign-spec-2026`, `soveryn-2026`, `redis-py-2010`, `qdrant-2021`, `llama-cpp-python-2023`, `rrf-algorithm-2009`, `sqlite-fts5-2015`

### Rule 2b: Inline `[id-soft:]` Tag Protocol (id Software Subset)
**Format**: `# [id-soft: GAME YEAR] Pattern Name — why this code exists`

**Game codes**: `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`

### Rule 2c: Tag Enforcement
| Check | Command | Gate |
|-------|---------|------|
| All `[id-soft:]` tags have vet records | `make heritage-vet` | M14 |
| Heritage map completeness | `make heritage-map` | CI |
| SPDX SBOM matches code tags | `make heritage-spdx` | Proposed CI |
| All `[heritage:]` tags documented in CREDITS.md | Manual review | Best practice |

### Rule 3: Decisions Must Cite Source
```markdown
- **Decision XX**: Chose X per [Carmack's Law: id Software].
- **Decision YY**: Adopted AnyIO per [AnyIO 2024].
```

### Rule 4: Evolution Must Be Explicit
Show: (1) original (2) what changed (3) why

### Rule 5: No Erasure
Credit stays even if pattern is refactored. Heritage is gratitude, not IP.

---

## §4 The "Right Approximation" Principle

> **"The right approximation for the problem is better than the exact solution you can't afford."**

| Tier | Domain | Approximation | Why |
|------|--------|---------------|-----|
| 1 | Provider health | BSP culling: O(1) breaker check | Stale-read skip cheaper than guaranteed failure |
| 2 | Memory | Tiered hot/warm/cold | Not all entities need full vector context |
| 3 | Entity dispatch | Domain matching, not perfect | Route to closest, re-route if wrong |
| 4 | Model inference | Local-first, cloud-fallback | Local "good enough" for 90% of queries |

---

## §5 User's Own Technology (No Attribution Required)

These patterns are the user's OWN IP — evolved through ANAi → XNAi → omega-stack → omega-engine:

| Pattern | First Appearance | Current Location |
|---------|-----------------|------------------|
| 3-Tier Memory (Hot/Warm/Cold) | ANAi Aug 2025 | `memory_store.py` |
| Provider Chain (Redis→File→InMemory) | ANAi Sep 2025 | `memory/providers.py` |
| Intent Detection | ANAi Aug 2025 | `oracle.py` |
| Entity Registry (YAML CRUD) | ANAi Oct 2025 | `entity_registry.py` |
| ResourceGuard (OOM protection) | omega-stack May 2026 | `resource_guard.py` |
| MCP Hub (47 tools) | omega-stack May 2026 | `omega_hub/server.py` |
| Hivemind Protocol | omega-engine Jun 2026 | `omega_hub/server.py` |
| Soul Distiller (L1→L2→L3) | omega-engine Jun 2026 | `soul_distiller.py` |
| MaKaLi Triad | omega-engine Jun 2026 | `makali.md` |
| Sovereign Mandates | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` |
| Engine-Stack Firewall | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` (M2) |
| Circuit Breaker Consolidation | omega-engine Jun 2026 | `model_gateway.py` |
| PEM (Personality Enhancement Module) | Lilith Deck Mar 2025 | `entity_registry.py` |

---

## §6 How to Add New Mapping

```markdown
### N.x [Concept Name] (Game, Year)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Creator — description | Omega implementation |
| **Core idea** | What it did | What we do |
| **Omega evolution** | How we changed it | Why we changed it |

**Attribution format**: `[Tag: source]`
```

---

**Full detailed tables**: `docs/archive/coordination/CREDITS-full-20260708.md`
**SPDX 3.1 Heritage Profile**: `docs/research/R_SPDX_HERITAGE_PROFILE.md`

*Last Updated: 2026-07-10 | 21 id Software Mappings | 55+ General Heritage Sources | D208 Heritage Remediation Complete*