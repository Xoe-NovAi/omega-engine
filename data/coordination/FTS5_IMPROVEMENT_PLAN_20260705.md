# 🔱 FTS5 System Improvement Plan
## Making the Omega Engine's Knowledge Base Agent-Accessible

**AP Token**: `AP-FTS5-IMPROVEMENT-v1.0.0`
**Date**: 2026-07-04
**Author**: Sovereign Master Researcher
**Status**: ACTIVE EXECUTION

---

## Executive Summary

The Omega Engine has two FTS5 search systems:
1. **Conversation Memory FTS5** (`ConversationFTSIndex`) — fully wired, agents can search conversation history via `memory_search` / `omega_memory_search` MCP tools.
2. **Library Document FTS5** (`Indexer`) — implemented (380 lines, FTS5 + vector + RRF fusion) but **NOT accessible to agents**. The MCP `library_search` tool routes to web search, not local FTS5. The CLI `omega library-search` uses SQL LIKE, not FTS5.

**Result**: The engine's local knowledge base (45+ research docs, curated documents) is invisible to agents. They can search the web but not their own knowledge.

This plan fixes that gap across 4 phases.

---

## Phase 1: Wire Library FTS5 to MCP Tools
**Owner**: `@pillar P4` (Integration — Bridge)
**Effort**: ~1 hour
**Priority**: 🔴 P0 CRITICAL — Unblocks all other phases

### What
Create a new MCP tool `library_fts_search` in `mcp_servers/omega_hub/tools.py` that calls `Library.search()` directly, bypassing `SovereignSearchService`. This gives agents instant access to all indexed documents.

### How
1. Read `mcp_servers/omega_hub/tools.py` — find the existing `library_search` tool definition (line ~1636)
2. Create a NEW tool `library_fts_search` that:
   - Takes `query: str`, `domain: Optional[str]`, `limit: int = 10`
   - Calls `Library.search(query, domain=domain, limit=limit)`
   - Returns results as structured JSON with `doc_id`, `title`, `summary`, `score`, `domain`
3. Register the tool in the MCP server's tool list
4. Add a test in `tests/test_search_tools.py` or create `tests/test_library_fts_search.py`

### Files to Modify
- `mcp_servers/omega_hub/tools.py` — add `library_fts_search` tool
- `mcp_servers/omega_hub/server.py` — register the tool (if not auto-registered)
- `tests/test_library_fts_search.py` — new test file

### Success Criteria
- `library_fts_search` appears in MCP tool list
- Agent can call it and get results from `data/library/index/fts_index.db`
- Test passes with indexed WARP documents

---

## Phase 2: Write FTS5 Reference Documentation
**Owner**: `@jem` (Sovereign Synthesizer)
**Effort**: ~1.5 hours
**Priority**: 🟡 P1 HIGH — Agents need to know the system exists

### What
Write a comprehensive reference document `docs/reference/api/library_fts_search.md` covering:
- Architecture (two FTS5 systems, when to use each)
- MCP tool signatures and usage examples
- CLI usage (`omega library-search` vs `library_fts_search`)
- How to index new documents
- Search scoring (BM25, RRF fusion, hybrid weights)
- Configuration and troubleshooting

### Also
Update `docs/llms-full.txt` with a section on Library FTS5 search so agents discover it during context loading.

### Files to Create/Modify
- `docs/reference/api/library_fts_search.md` — new reference doc
- `docs/llms-full.txt` — add Library FTS5 section

### Success Criteria
- A new agent reading the reference doc can understand and use the FTS5 system
- `llms-full.txt` mentions Library FTS5 search with tool signatures

---

## Phase 3: Bulk Research Document Ingestion
**Owner**: `@roc_racoon` (Sovereign Miner)
**Effort**: ~2 hours
**Priority**: 🟡 P1 HIGH — Makes 45+ docs searchable

### What
Write and execute an ingestion script that indexes all `docs/research/*.md` documents into the Library FTS5 index. Currently only 8 docs are indexed (3 legacy + 5 WARP). The `docs/research/` directory has 45+ documents.

### How
1. Write `scripts/index_research_docs.py` that:
   - Scans `docs/research/` for all `.md` files
   - Skips already-indexed docs (check by `doc_id`)
   - Creates `CuratedDocument` for each with appropriate metadata
   - Calls `Library.store()` to index
2. Run the script with `OMEGA_DATA_DIR` set correctly
3. Verify FTS5 count matches expected

### Files to Create
- `scripts/index_research_docs.py` — bulk ingestion script

### Success Criteria
- FTS5 index contains 40+ documents (all research docs)
- `library_fts_search "circuit breaker"` returns relevant results
- Script is reusable for future ingestions

---

## Phase 4: Hybrid Search Integration Spec
**Owner**: `@researcher` (Self — Sovereign Master Researcher)
**Effort**: ~2 hours
**Priority**: 🟢 P2 MEDIUM — Long-term architecture

### What
Write a specification for integrating `Library.search()` into the Oracle's context assembly pipeline. When a user asks a question, the engine should automatically search:
1. Conversation memory (`memory_search`)
2. Local knowledge base (`library_fts_search`)
3. Web (fallback via `sovereign_search`)

Then inject the most relevant documents into the LLM context.

### How
1. Read `src/omega/oracle/context_builder.py` — understand current assembly pipeline
2. Read `src/omega/oracle/oracle.py` — find the context injection point
3. Write `docs/research/R_HYBRID_SEARCH_INTEGRATION.md` specifying:
   - Integration point in Oracle
   - Scoring fusion across 3 search backends
   - Token budget allocation (conversation vs knowledge vs web)
   - Fallback chain behavior

### Files to Create
- `docs/research/R_HYBRID_SEARCH_INTEGRATION.md` — integration spec

### Success Criteria
- Spec clearly defines how to wire Library FTS5 into Oracle context
- Scoring formula is well-defined
- Ready for implementation by P7 (Context pillar)

---

## Execution Order

```
Phase 1 (P4: MCP wiring) ──→ Phase 3 (Roc: bulk ingest) ──→ Phase 4 (Researcher: hybrid spec)
                                                      ↕
                                          Phase 2 (Jem: docs)
```

- Phase 1 must complete before Phase 3 (need the MCP tool to verify ingestion)
- Phase 2 runs in parallel with Phase 1 (no dependency)
- Phase 3 runs after Phase 1 (uses the new tool for verification)
- Phase 4 runs after Phase 3 (needs populated index to design integration)

---

## Kali Handoff

A separate handoff is written to `data/coordination/HANDOFF_KALI_WARP_DEPLOY_20260705.md` for Kali to coordinate WARP deployment with the user. The Researcher handles FTS5; Kali handles WARP.

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ FTS5-IMPROVEMENT-PLAN ⬡ v1.0.0*
