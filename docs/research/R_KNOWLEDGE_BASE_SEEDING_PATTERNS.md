# 🔱 Omega Engine — R-## Knowledge Base Seeding & Entity Knowledge Patterns
# ⬡ OMEGA ⬡ SARASWATI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ R##

**AP Token**: `AP-RESEARCH-KB-SEED-v1.0.0`
**Author**: Web Research Fleet (Deep Research)
**Date**: 2026-05-26
**Status**: DRAFT

---

## Summary

Production consensus in 2026 converges on **file-based JIT retrieval** for bounded, curated domains — which validates Omega Engine's current filesystem-first approach. Key finding from comprehensive benchmarks: a compressed index + selective file reads beats or matches full RAG pipelines on curated knowledge corpora under 5,000 items. For Omega's 10 pillar entities, the recommended pattern is: (1) seed from `docs/research/` with curated abstracts, (2) use FTS5 keyword search (already implemented), (3) grow through agent-contributed findings rather than bulk web ingestion.

---

## Findings

### 1. The Curated File > RAG Finding (Vercel Research)

Vercel's agent engineering research showed **100% pass rate** for file-based JIT retrieval vs 79% for vector RAG on curated documentation. The reason: documents written by humans have clear titles, hierarchies, and cross-references — keyword search (FTS5) is sufficient because the corpus is curated. Vector embeddings add latency, cost, and failure modes without proportional benefit.

**Omega implication**: Our Library pipeline is architecturally correct. FTS5 is the right primary backend for Phase 1. Qdrant vector search should be Phase 2 (v0.6.0) as an enhancement, not a replacement.

### 2. The Karpathy LLM Wiki Pattern

Alternate pattern for entity knowledge: instead of RAG, the LLM reads raw documents once and compiles a structured markdown wiki:
- `raw/` — immutable source documents
- `wiki/` — generated markdown, organized by entity/concept
- `CLAUDE.md` — schema + compilation workflow

**Omega implication**: Each entity's `knowledge/` directory could work as a mini LLM Wiki. The background researcher's L1→L2→L3 pipeline already produces distiller output — this IS the wiki generation step. The gap is that distiller output is written to `docs/research/` but not to entity `knowledge/` dirs.

### 3. Scale Tier Decision Framework

| Tier | Size | Best Pattern | Omega Status |
|------|------|-------------|-------------|
| **Small** | <500 items | Curated Markdown + FTS5 | ✅ Current architecture |
| **Medium** | 500-50K | Chunked → Vector DB → RAG | ➕ Qdrant (v0.6.0) |
| **Large** | 50K-1M | Hybrid: Vector + BM25 + Filters | 🔮 Future |
| **Enterprise** | 1M+ | Graph + Vector | 🔮 Omegaverse |

**Omega implication**: Phase 1 should stay in Small tier. FTS5 + curated knowledge is correct and sufficient.

### 4. Knowledge Organization Patterns (3-Layer JIT Index)

From Vercel/Catalyzed production systems:
- **L1 (Always in context)**: Pipe-delimited index file mapping every KB entry to description + tags (~200 tokens)
- **L2 (On-demand)**: Self-contained markdown files <500 lines per domain
- **L3 (Source)**: Original docs (HTML/PDF), used only during KB generation

**Omega implication**: We need an L1 index for each entity's knowledge/ directory. Currently there's no index — the agent must discover knowledge/ contents by `ls` or `glob`. Add an `INDEX.md` to each knowledge/ dir.

### 5. Tool Description Overload Pattern

Research shows RAG applied to tool descriptions improves selection accuracy **3-fold**. Without it, 100+ tool descriptions cause model confusion.

**Omega implication**: As entities accumulate tools/knowledge, we need tool description RAG. For Phase 1, keep entity tool descriptions under 30 per entity to avoid overload.

### 6. Auto-Population from Codebase

Tools exist for auto-seeding knowledge from source code:
- **source-kb**: AST parsing → method-level injection → structured KB docs
- **Secrin**: Code → Neo4j knowledge graph → LLM summaries → markdown wiki
- **doc2vec**: Crawl websites/GitHub/local dirs → chunk → embed → SQLite-vec

**Best pattern for Omega**: Use the background researcher pipeline (already exists!) rather than external tools. The researcher's `_grow_frontier()` method is designed to auto-discover knowledge sources — it just needs to WRITE to entity `knowledge/` dirs instead of just `docs/research/`.

---

## Recommendations

1. **Write L1 INDEX.md to each entity's knowledge/ directory** — The highest-impact, lowest-effort change. A pipe-delimited index of what the entity knows.
2. **Route background researcher output to entity knowledge/ directories** — Currently writes only to `docs/research/`. Add step: if research topic matches entity domain, write L2 summary to `data/entities/{entity}/knowledge/`.
3. **Keep FTS5 as primary search backend** — Don't prioritize Qdrant wiring. File-based + FTS5 is the correct phase 1 pattern.
4. **Seed from existing research docs** — 180+ entries in `docs/research/INDEX.md`. Route domain-relevant docs into entity knowledge/ dirs programmatically.
5. **Add tool description limit enforcement** — Flag when any entity exceeds 30 tool descriptions. Implement tool RAG at that threshold.

---

## Sources

- [LangChain Knowledge Base Docs](https://docs.langchain.com/oss/python/langchain/knowledge-base)
- [CrewAI Knowledge Concepts](https://docs.crewai.com/en/concepts/knowledge)
- [Vercel Agent Engineering (Catalyzed)](https://docs.catalyzed.ai/guides/knowledge-base-reconciliation)
- [Karpathy LLM Wiki Pattern](https://pasqualepillitteri.it/en/news/1496/rag-llm-wiki-agentic-search-differences-costs-2026)
- [Ikigai: Knowledge Bases vs RAG Pipelines](https://ikigaidigital.io/insights/why-we-build-knowledge-bases-not-rag-pipelines-part-1)
- [source-kb (PyPI)](https://pypi.org/project/source-kb/)
- [Secrin (GitHub)](https://github.com/secrinlabs/secrin)
- [doc2vec (GitHub)](https://github.com/kagent-dev/doc2vec)
- [OpenAI Knowledge Retrieval Starter Kit](https://github.com/openai/openai-knowledge-retrieval)
- [RAG Freshness Index Rot](https://tianpan.co/blog/2026-04-20-rag-knowledge-base-freshness-index-rot)

---

## Implementation Note
_For: Builder mode (Gemma 4 31B)_

Two concrete tasks: (1) Write a `seed_knowledge_bases.py` script that scans `docs/research/` for domain tags and copies L2 abstracts into `data/entities/{entity}/knowledge/` — this is a one-shot seed. (2) Modify `background_researcher/soul_updater.py` to write research findings to entity knowledge dirs based on topic matching. (3) Add INDEX.md generation to entity scaffold in `entity_registry.py`.
