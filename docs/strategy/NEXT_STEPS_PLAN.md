# Omega Engine — Detailed Next Steps Plan
**Date**: 2026-07-12
**Baseline**: 1189 tests passing

---

## Executive Summary

9 gaps identified. WEB-1 blocker appears resolved in prior commits. Phase 1A is **unblocked**.

## Gap Inventory — Prioritized

| Phase | Gap | Description | Effort | Owner | Blocker |
|-------|-----|-------------|--------|-------|---------|
| **1A** | 1 | YouTube TranscriptFetcher Hardening | 8h | Kali/P3 | None |
| **1B** | 2 | YouTube RAG Synthesis | 6h | Jem/Lilith | Phase 1A |
| **2** | 8 | Contract Tests (M21) | 4h | Verity | Phase 1A/1B |
| **3** | 3 | Ingestion Dedup + 429 Handling | 4h | Ma'at/P3 | None |
| **4** | 6 | Qdrant Payload Indexes | 2h | Ma'at/P2 | None |
| **5** | 5 | MCP Streamable HTTP | 3h | Doom Guy | None |
| **6** | 4 | AGB-0 Local Embeddings | 12h | Roc+Researcher | JEM-1 |
| **7** | 7 | Podman Header Injection | 2h | Doom Guy | None |
| **8** | 9 | Documentation Drift | 2h | Verity | None |

**Total**: ~43h

## Execution Timeline

```
WEEK 1: Phase 1A (TranscriptFetcher) + Phase 3 (Ingestion) + Phase 4 (Qdrant)
WEEK 2: Phase 1B (RAG Synthesis) + Phase 2 (Tests) + Phase 5 (MCP)
WEEK 3: Phase 6 (AGB-0) + Phase 7 (Podman) + Phase 8 (Docs)
```

## Immediate: Phase 1A Files

- `src/omega_youtube_research/errors.py` — add EmptyTranscriptError
- `src/omega/workers/youtube_worker.py` lines 265-310 — rewrite TranscriptFetcher
- `config/youtube_worker.yaml` — add transcript_fetcher config
- `tests/test_youtube_worker_contract.py` — add M21 tests

## Quick Wins (Parallel, No Dependencies)

- **Qdrant Payload Indexes** (2h): `curl localhost:6333/collections/omega_memory/index`
- **Ingestion 429 Handling** (1h): `pipeline.py` check_http_status
- **Documentation Drift** (2h): Fix 3 false claims in Ark Blueprint

## Blocker Status

| Blocker | Status | Notes |
|---------|--------|-------|
| WEB-1 (B8/B5/SEC) | RESOLVED | No fnmatch/xml_escape/PII issues in current code |
| JEM-1 Phase 1 | ACTIVE | Creates omega_agb/ for AGB-0 |

---

*Full plan with code: `docs/strategy/INFRA_HARDENING_PLAN.md`*
*Gap audit: `docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md`*
