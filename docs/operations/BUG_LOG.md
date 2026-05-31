# 🔱 Omega Engine — Bug & Issue Log
**AP Token**: `AP-BUG-LOG-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b ⬡ opencode ⬡ trc_audit ⬡ MVE-PHASE

## Purpose
This log tracks technical defects, regressions, and architectural bugs discovered during the development of the Omega Engine. Every entry must include a reproduction path and a proposed fix.

---

## 🐛 Open Issues

### BUG-001: `omega-core-library` Search Index Latency/Failure
**Date**: 2026-05-14
**Priority**: 🔴 High
**Reporter**: Sovereign Master Researcher (Gemma 4-31B)
**Status**: OPEN

**Description**:
Curated documents are accessible via direct ID retrieval (`omega-core-library_get_document`), but are not immediately discoverable via the hybrid search index (`omega-core-library_search` or `omega-research_research`).

**Reproduction Path**:
1. Add a note via `omega-core-library_inbox_add_note`.
2. Ingest the note via `omega-core_library_ingest_pending`.
3. Verify document exists via `omega-core-library_get_document` using the returned `doc_id`.
4. Attempt to find the same document via `omega-core-library_search` using a keyword present in the body.
5. **Result**: Search returns zero results.

**Proposed Fix**:
- Investigate the indexing trigger in the `omega-core-library` server.
- Ensure that the vector index (Qdrant/FAISS) is flushed and committed immediately after ingestion.
- Verify if `index_flush` is an async operation that requires awaiting.

---

## ✅ Resolved Issues
(No issues resolved yet)
