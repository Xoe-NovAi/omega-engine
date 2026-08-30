# N12 Domain Index — Research, Curation & Personal Corpus

**AP Token**: `AP-N12-DOMAIN-INDEX-v1.0.0`
**Node**: N12 curator (overseen by Jem) · **Date**: 2026-08-22 · `last_verified: 2026-08-22`
**KB of record**: `data/entities/jem/workspace/N12_CURATOR_KB_20260822.md`
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N12)

---

## 1. Systems & Wiring

```
                        SOVEREIGN CORPUS ACQUISITION→STEWARDSHIP STACK (3 layers)

 ┌─────────────────────────── LAYER A: LIBRARY (lifecycle owner) ───────────────────────────┐
 │  src/omega/library/                                                                      │
 │  InboxManager.add_url/file/note ──► Library.ingest_from_inbox(limit=5)                   │
 │        │                                  │                                              │
 │        ▼                                  ▼                                              │
 │  InboxStatus state machine       CurationPipeline.process ─► threshold 0.6 gate          │
 │  (pending/processing/…)                  │      (classify_domain, quality score)         │
 │                                          ▼                                               │
 │  EnrichmentEngine ──────────────► Library.store ─► $DATA/library/documents/{id}.json     │
 │  (bibliographic)                         │                                               │
 │                                          ▼                                               │
 │  Indexer.index_document ──► FTS5 + vector (SQLiteVecAdapter, memory fallback)            │
 │                                          │                                               │
 │                                          ▼                                               │
 │                          BRIDGE.publish_new_document (Hivemind notify)                   │
 │  Catalog: LibraryCatalog (SQLite) ◄── CLI oracle_cli.py ONLY (not engine SSOT)           │
 │  Discovery/Research: DiscoveryOrchestrator(depth tiers) / ResearchEngine                 │
 │  Guards: rate_limiter.TokenBucket(per-domain) · security.SSRFGuard                       │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
                      ▲ imports CurationPipeline/ExtractedContent/EnrichmentEngine
 ┌─────────────────────────── LAYER B: INGESTION (resilience/extraction) ───────────────────┐
 │  src/omega/ingestion/                                                                    │
 │  IngestionPipeline.run_source: URL → SovereignScraper T1 fast → T3 deep                  │
 │    → TriangulationVerifier (delta+metadata+provenance; drop <0.4 confidence)             │
 │  guards.SovereignSentry(probe) + BudgetGuard(token ceiling)                              │
 │  persistence.IngestionPersistence: Tri-Anchor (raw_anchor/SCA/extraction, quarantine)    │
 │  WAD gate: config/wads/ingestion/domains.yaml allowlist (gutenberg/arxiv/pubmed/…),      │
 │    tiers fast|surgical|deep, CAS archive data/archive/cas, queue curation_queue          │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
                      ▲ imports IngestionPersistence + PIIMasker
 ┌─────────────────────────── LAYER C: SIEVE-AND-SIGN (sanitize/provenance) ────────────────┐
 │  src/omega/oracle/ingestion.py                                                           │
 │  SovereignSieve.sieve (PII mask) → SovereignSigner.sign (HMAC-SHA256;                    │
 │    ⚠ fallback secret "omega-sovereign-change-me" if OMEGA_INGESTION_SECRET unset)        │
 │  SovereignIngestionCoordinator.process_and_anchor → Tri-Anchor quarantine stores         │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────── SEARCH CHAIN (SSP-V2) ────────────────────────────────────────┐
 │  query → SearchRouter.route (rule-based 6-signal, no LLM)                                │
 │    T0 LOCAL (MemoryStore) → T1 SEARXNG (:8017) → T2 EXA → T3 FIRECRAWL                   │
 │  sovereign_search_service: parallel/sequential tier exec; health cache TTL 30s           │
 │  search_cache.SovereignCache: .firecrawl/cache_<sha256>.json, TTL 24h (T3-focused)       │
 │  breakers: HealthMonitor-backed (canonical C-6′) ⚠ + legacy deprecated (dual path)       │
 │  observability → search_persistence.SearchDB ($DATA/search/search_history.db)            │
 │    ⚠ tool-tier vocabulary here ≠ router T0–T3                                            │
 │  BYPASS PATHS: tools/searxng_direct.py + firecrawl_direct.py (NO callers; ad-hoc CLI)    │
 │  MCP: omega-hub :8016 ✓ · searxng :8018 ✓ · firecrawl :8015 ✗(disabled) · exa hosted     │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────── MEDIA PIPELINE (youtube_worker daemon) ───────────────────────┐
 │  submit_url/playlist/topic/file → Redis youtube_queue (LPUSH/BRPOP, :6379/0)             │
 │  run_cycle: IDLE→[DEQUEUE→FETCH→INGEST→SAVE]×N→[SYNTHESIZE ≥5 videos]→IDLE               │
 │  FETCH = transcript-FIRST (youtube-transcript-api v1.2.x upstream, delay 2.0s)           │
 │    ⚠ T2 whisper / T3 firecrawl exist ONLY in config/youtube_research.yaml (aspirational) │
 │  INGEST = Sieve-and-Sign path (Layer C) · SYNTH = qwen3-1.7b under ResourceGuard 2048MB  │
 │  systemd: omega-youtube-worker.{service,timer} MemoryMax=768M Requires searxng+redis     │
 │  state: data/workers/youtube_worker_state.json (Somatic Save-Point) · lock $TMPDIR       │
 │  backlog: youtube-links-for-ingestion.txt (114) + mind-science-esoteric.txt (15)         │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────── DOC-READER & STAGED CORPUS ───────────────────────────────────┐
 │  scripts/universal_doc_reader.py (agent-skill wrapper) ⇄ src/omega/doc_reader/ (tested)  │
 │    formats: docx/pdf(fitz)/odt/rtf/html/text · NO OCR · errors as [FORMAT ERROR:] str    │
 │  PP-2 Grok corpus (POST-DEBUT staging):                                                  │
 │    ABS /media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/             │
 │    grok_unified_index.db ← LIVE HERE (48.64MB, 274 convos/6,565 responses/22 projects)   │
 │    FTS5 index (796 entries) · gnosis packs = PROJECT-LINK counts (~1,268≠unique)         │
 │  KD content layer: config/domains/curators.yaml = 13 domains declared, 2 dirs exist      │
 │    (engineering, gemini-notebook); jem curates "Synthesis/Cognitive Architecture" only   │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Tier-vocabulary mapping (cross-system Rosetta — none existed before 2026-08-22)

| Concept | SSP router | search_persistence | scraper WAD | YouTube specs |
|---------|-----------|--------------------|-------------|---------------|
| local/free | T0 | 0=local | — | — |
| broad/self-hosted | T1 SearXNG | 3=searxng | fast | T1 transcript-api |
| mid cloud | T2 Exa | 5=exa | surgical | T2 yt-dlp+whisper |
| deep/expensive | T3 Firecrawl | 6=firecrawl | deep | T3 firecrawl+comments |
## 2. Key Files

| File | One-line purpose |
|------|------------------|
| `src/omega/library/library.py` | Lifecycle driver — `Library.ingest_from_inbox()` is THE end-to-end hop |
| `src/omega/library/inbox.py` | Intake state machine (add_url/file/note, mark_*) |
| `src/omega/library/curator.py` | Classification + quality gate (threshold 0.6) |
| `src/omega/library/indexer.py` | FTS5+vector indexing via SQLiteVecAdapter |
| `src/omega/library/rate_limiter.py` | Per-domain token buckets (library-side fetching) |
| `src/omega/library/security.py` | SSRFGuard / path scope / download size |
| `src/omega/oracle/search_router.py` | SSP-V2 rule-based tier routing (T0–T3 canonical) |
| `src/omega/oracle/sovereign_search_service.py` | Tier execution orchestrator + health cache |
| `src/omega/oracle/search_cache.py` | SovereignCache (.firecrawl/, TTL 24h lazy) |
| `src/omega/oracle/search_circuit_breaker.py` | Legacy breakers (deprecated; HealthMonitor canonical) |
| `src/omega/search/search_persistence.py` | Search history DB + M22 provider provenance sink |
| `src/omega/oracle/ingestion.py` | Sieve-and-Sign sanitize/provenance layer |
| `src/omega/ingestion/pipeline.py` | Two-tier scrape + triangulation orchestrator |
| `src/omega/ingestion/persistence.py` | Tri-Anchor backend (raw/SCA/extraction, quarantine) |
| `src/omega/workers/youtube_worker.py` | YouTube daemon (transcript-first T1 only) |
| `config/youtube_worker.yaml` | Worker runtime knobs (REAL config the daemon reads) |
| `config/youtube_research.yaml` | 9-layer aspirational spec-config (NOT runtime truth) |
| `config/wads/ingestion/domains.yaml` | Scrape allowlist + fast/surgical/deep tiers |
| `scripts/universal_doc_reader.py` | Agent-skill doc reader (docx/pdf/odt/rtf/html) |
| `config/domains/curators.yaml` | KD spec: 13 domains, model routing, proposals flow |
| ABS `…/grok-accounts-exports/grok-data-indexed/grok_unified_index.db` | Live Grok corpus DB (274 convos) |

## 3. Entry Points

**"I want to add a document to the library"** → MCP `library_inbox_add_url/note/file` → `library_ingest_pending`. TDP-wrapped at hub.
**"I want to search the web sovereignly"** → MCP `sovereign_search` / oracle cluster. Never assume firecrawl MCP (:8015 disabled); use oracle cluster or direct clients.
**"I want to ingest YouTube videos"** → write watch-URLs to `youtube-links-for-ingestion.txt`, or CLI `python -m omega.cli.youtube_cli ingest <url>`; daemon drains Redis queue.
**"I need to read a doc file"** → `.venv/bin/python scripts/universal_doc_reader.py <file>` (check output for `[FORMAT ERROR:` prefix).
**"Where is the Grok corpus?"** → omega_library ABS path above; DB moved WITH corpus; build docs' paths are stale.
**"What does a KD domain need?"** → read curators.yaml §DOMAIN MODULE STRUCTURE + bootstrap table; dirs are greenfield except engineering/gemini-notebook.
**"Is a transcript fetchable?"** → `youtube_cli verify <url>`.
**"What did a search cost/provenance?"** → query `$DATA/search/search_history.db` (`provider_name`, tier, latency).

## 4. Doc Map

| Layer | Location |
|-------|----------|
| Charter/law | `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §2/§4 · `SOVEREIGN_MANDATES.md` |
| KB of record | `data/entities/jem/workspace/N12_CURATOR_KB_20260822.md` (24 digests, 15 gotchas, W-pass) |
| Provider dossiers | `docs/research/SEARCH_DOSSIERS/` (two complementary series: technical + SSP-role) |
| YouTube design lineage | `R_YOUTUBE_BACKGROUND_WORKER_SPEC` → `ENHANCEMENT_PLAN` → `V2_SYNTHESIS` → `ENHANCED_SPEC_V2`; meta: `R_KNOWLEDGE_FABRIC_SYNTHESIS_20260712` |
| Gap evidence | `NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md` · `NODE_GAP_WEB_RESEARCH_JEM_20260822.md` |
| PP-2 pattern | PLAN §6 row PP-2 |
| Prior grok mining | `data/entities/roc_racoon/workspace/mining_reports/grok_exports_surgical_strike_report.md` |
| Web register | KB `## Source Register` (SR1–SR8) + NODE_GAP Continuation 1 |

## 5. Known Hazards

| ID | Hazard | Evidence |
|----|--------|----------|
| HZ-1 | Fallback signing secret `"omega-sovereign-change-me"` → forgeable provenance by default. **Top escalation to N5/N10** | `oracle/ingestion.py:76` (V2-verified) |
| HZ-2 | Tier-vocabulary collision across 4 subsystems — analytics joins break silently; use §1 mapping table | router:21–24 vs persistence:40 vs WAD vs YT specs |
| HZ-3 | Config-aspirational drift: youtube_research.yaml T2/T3 NOT implemented; 11/13 KD domains dirless. Code = truth, configs = roadmap | KB digests #9/#19 |
| HZ-4 | Dual breaker path (HealthMonitor canonical + legacy deprecated) until C-6′ P-5 removal | service lines 165–188 |
| HZ-5 | Stray FTS index in source tree `src/data/library/index/fts_index.db{,-shm,-wal}` — DATA_DIR resolution fragility evidence | ls-verified 2026-08-22 |
| HZ-6 | `.firecrawl/` mixes governed cache (TTL) with ~25 ungoverned topic dumps + 1.26MB markdown (no expiry/manifest) | KB digest #14 |
| HZ-7 | Grok DB stale paths in ALL build docs; live DB at omega_library. Gnosis "1,268" = project-link count ≠ unique 274 | DD-1/DD-3 |
| HZ-8 | PP-2 privacy allowlist doc DOES NOT EXIST yet — must be authored before any staging work (distinct from N5 PUBLIC_ALLOWLIST) | pager ruling + negative finding |
| HZ-9 | Port confusion: SearXNG engine 8017, searxng MCP 8018, firecrawl MCP 8015 DISABLED | opencode.json + providers default |
| HZ-10 | Duplicate provider-client stacks (tools/*_direct vs search_providers) — endpoint changes must land twice or unify | DD-2 |
| HZ-11 | YT/vector/queue deps are CORE not extras — no slim installs possible | pyproject:58–67 |
| HZ-12 | Doc-reader silent-failure style ([FORMAT ERROR:] strings) + no OCR | digest #7 |
| HZ-13 | youtube-transcript-api rides undocumented YouTube API — upstream breakage windows are expected, not exceptional (WR-1) | Source Register SR1–SR3 |
| HZ-14 | If yt-dlp download tiers ever ship: PO Token regime mandatory (video-bound tokens ~12h life, client defaults rotate) — needs bgutil pot-provider plugin + monitoring loop | SR6/SR7 |
| HZ-15 | NotebookLM→Gemini Notebook rebrand (Jul 2026): watch post-rebrand API drift; pin ≥0.8.1 | SR4/SR5 |

*Cold-reader test: "where does X live and what's broken?" answerable from §1–§5 alone. Deep detail: consult the KB.*

