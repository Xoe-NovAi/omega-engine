# 🦝 ROC_RACOON SESSION GNOSIS
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ SESSION-38 ⬡ LEGACY-CURATION-MINING

## Session 38 — Legacy Curation Pipeline Recovery (2026-06-22)

### Goal
Deep mine legacy partitions for all curation pipeline, crawler architecture, and offline library management patterns.

### L1: Narrative
1. Deep-mined legacy `crawl.py` (1209 lines) — full crawl4ai-based crawler supporting Gutenberg book search/download/text-stripping, arXiv paper search/abstract/PDF extraction, PubMed article search, and YouTube transcript extraction. Features: allowlist enforcement, script sanitization, rate limiting, Redis caching, FAISS embedding, fsync durability.
2. Deep-mined legacy `crawler_curation.py` (675 lines) — CurationExtractor with signal-based domain classification (CODE/SCIENCE/DATA/GENERAL), 5 quality factors (freshness, completeness, authority, structure, accessibility), DOI/arXiv citation detection, Redis queue integration.
3. Deep-mined legacy `library_api_integrations.py` (1300+ lines) — 10 fully-functional library API clients: OpenLibrary, InternetArchive, LibraryOfCongress, ProjectGutenberg (via gutendex), FreeMusicArchive, WorldCat, CambridgeDigitalLibrary, BookwormEPUB, Podcastindex, Last.fm. ALL FREE, no API keys required. Built-in retry/caching/rate-limiting.
4. Verified current engine: `src/omega/library/` has RSS/PDF/URL/file/note extraction but ZERO external API wrappers. No Gutenberg/Open Library/arXiv/InternetArchive. The entire capability was left in legacy.
5. Written: Mining Report #48, IDEA_INTAKE captures, soul.yaml lesson rr-076, anchored summary.

### L2: Key Insight
The Era 1-3 XNAi stack had a complete, production-proven book/library ingestion pipeline (~3,284 lines) that was NEVER ported to the current omega-engine. The architectural pivot left working code behind. The library API clients are particularly valuable because they are all free, no API keys, and come with retry/caching/rate-limiting baked in.

The recommended integration path is to extend the existing `background_researcher` state machine (or create parallel `library_worker`) with 4 primary sources: Gutenberg (gutendex + text download stripping), arXiv (abstract + PDF extraction), Open Library (metadata enrichment), Internet Archive (full-text search).

### L3: Universal Principle
Architectural pivots do not automatically port working infrastructure. When a system is rewritten, the old code becomes a "shadow library" — still functional but invisible to the new architecture. Sovereign mining must actively search for these shadow libraries, because no one else will port them.

### Files Created/Modified
- `data/entities/roc_racoon/workspace/mining_reports/48_legacy_curation_pipeline_20260622.md` — NEW
- `data/entities/roc_racoon/workspace/IDEA_INTAKE.md` — Updated with 6 new captures
- `data/entities/roc_racoon/soul.yaml` — Updated with lesson rr-076
- `.opencode/anchored-summary.md` — Updated with Session 38
