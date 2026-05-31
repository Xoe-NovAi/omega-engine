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

### BUG-002: 100+ Bare `except Exception:` Clauses Across Codebase
**Date**: 2026-05-31
**Priority**: 🔴 High
**Reporter**: The Artisan (Cline/MiMo-2.5)
**Status**: OPEN

**Description**:
Codebase audit found 100+ `except Exception:` clauses that swallow errors without structured logging, trace_id propagation, or typed exception handling. This was the root cause of the "start-limit-hit" systemd failure and the Gemini CLI server deletion event — both silent failures that could have been caught earlier with proper error infrastructure.

**Affected Modules**:
- `src/omega/oracle/oracle.py` — 9 bare `except Exception:`
- `src/omega/memory_store.py` — 8 bare `except Exception:`
- `src/omega/workers/background_researcher/` — 40+ bare `except Exception:`
- `src/omega/library/` — 10+ bare `except Exception:`
- `src/omega/oracle/providers.py` — 4+ bare `except Exception:`
- `src/omega/iris/server.py` — 2 bare `except Exception:`
- `mcp_servers/omega_hub/server.py` — 5+ bare `except Exception:`

**Reproduction Path**:
1. Review source tree with `grep -rn "except Exception:" --include="*.py" src/omega/ mcp_servers/`
2. Count occurrences (100+ as of 2026-05-31)
3. Observe that none propagate `trace_id`, use `OmegaError`, or emit structured logs

**Proposed Fix**:
- Create `src/omega/oracle/exceptions.py` with full `OmegaError` hierarchy (P0)
- Progressive migration: convert source modules one at a time to typed exceptions
- Add error path tests per `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §7

**Reference**:
- `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` — Full architecture spec
- `SOVEREIGN_MANDATES.md` — Mandate #9 (Error Integrity)
- Implementation delegated to OpenCode builder agents via handoff

### BUG-003: Bug Tracking Infrastructure Not Connected to Engine
**Date**: 2026-05-31
**Priority**: 🟡 Medium
**Reporter**: The Artisan (Cline/MiMo-2.5)
**Status**: OPEN

**Description**:
The BUG_LOG.md is a standalone markdown file with no connection to the engine runtime. Bugs are tracked manually, and there is no MCP tool to query/create/resolve bugs. The error recovery matrix defined in the logging architecture cannot be verified or tracked.

**Proposed Fix**:
- Implement an MCP tool `omega_hub.bug_create` / `omega_hub.bug_list` / `omega_hub.bug_resolve`
- Store bugs in `data/bugs/bugs.jsonl` (persistent, machine-readable)
- Wire `ObservabilityEngine` to auto-report when error thresholds are crossed

---

## ✅ Resolved Issues

### BUG-001-RESOLVED: Omega Hub Server Deletion (Recovered from .bak)
**Date**: 2026-05-31
**Priority**: 🔴 High (previously OPEN)
**Status**: RESOLVED

**Resolution**:
- The 40-tool server was deleted by Gemini CLI (never committed to git)
- Recovery: merged `mcp_servers/omega_hub/__init__.py.bak` (40 tools, truncated) + `docs/intake/server.py` (backup from 2026-05-16, 28 tools) + Gemini's HTTP handshake endpoints
- Result: Full 41-tool server committed to git as `mcp_servers/omega_hub/server.py`
- Lesson: All MCP servers are now committed to git. Systemd socket activation prevents deletion.

### BUG-001: `omega-core-library` Search Index Latency/Failure (Open — Moved to P1)
**Date**: 2026-05-14 → 2026-05-31 (Re-prioritized)
**Priority**: 🟡 Medium (reduced from High)
**Status**: OPEN (P1 — Qdrant wiring)

**Note**: This is a Qdrant hybrid search wiring issue. The bag-of-words fallback works, but Qdrant (:6333) is not wired into the library. Moved to P1 as Qdrant integration is the appropriate scope.
