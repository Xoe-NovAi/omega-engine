<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N12 External Sources — Offline-Expertise Queue

**AP Token**: `AP-N12-EXTERNAL-SOURCES-v1.0.0`
**Node**: N12 curator (overseen by Jem) · **Date**: 2026-08-22 · `last_verified: 2026-08-22`
**Purpose**: prioritized queue for the future background curation worker to pull and
ingest into the engine (charter §2 order #8). P0 = resolves live decisions ·
P1 = next-phase ammunition · P2 = background theory.

| Title | Source | Priority | Why it matters | Target ingestion format |
|-------|--------|----------|----------------|-------------------------|
| yt-dlp Wiki: PO Token Guide | https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide | **P0** | The canonical "perishable player_client" regime — required reading before ANY T2/T3 download-tier work; client table + token lifespans rotate continuously | markdown snapshot + quarterly re-pull |
| yt-dlp Wiki: Extractors (YouTube section) | https://github.com/yt-dlp/yt-dlp/wiki/Extractors | **P0** | Default-client behavior + extractor-args reference for the media pipeline's fallback tiers | markdown snapshot + quarterly re-pull |
| youtube-transcript-api docs | https://github.com/jdepoix/youtube-transcript-api | **P0** | Primary extraction dependency (v1.2.4); undocumented-API breakage windows land here first; API changed 0.6→1.x (list/fetch style) | markdown README + changelog RSS |
| notebooklm-py README + CHANGELOG | https://github.com/teng-lin/notebooklm-py | **P0** | KD-liaison duty target (monthly monitor per TRACK-with-managed-risk); v0.8.x breaking contract + Gemini Notebook rebrand drift | markdown + monthly release watch |
| SearXNG administrator docs | https://docs.searxng.org/admin/index.html | **P1** | Self-hosted T1 engine we operate on :8017 — settings.yml, engines config, rate-limiting, botdetection tuning | markdown (admin subset) |
| Firecrawl API docs (v2) | https://docs.firecrawl.dev | **P1** | T3 provider; staged capability snapshot is 2026-08-16 — re-verify v2 surface before building against it | openapi/markdown + version pin note |
| Exa docs | https://docs.exa.ai | **P1** | T2 provider (neural search); endpoint/credit semantics for the router's credit_status signal | markdown quickstart + API ref |
| yt-dlp README (embedding guide) | https://github.com/yt-dlp/yt-dlp | **P1** | Python embedding semantics (`cli_to_api` translation pitfalls documented in issues) for worker integration | markdown |
| Redis LPUSH/BRPOP patterns | https://redis.io/docs/latest/commands/brpop/ | **P2** | Queue backbone of youtube_worker + curation_queue; delayed-queue semantics (youtube_queue_delayed) | command reference pages |
| SQLite FTS5 documentation | https://www.sqlite.org/fts5.html | **P2** | Library indexer + grok-data-indexed FTS5 both ride FTS5; bm25 ranking, external-content tables | single-page reference |
| sqlite-vec usage | https://github.com/asg017/sqlite-vec | **P2** | Vector half of hybrid search (<500k vector regime per N2 boundary) | markdown README |
| Zettelkasten primer (Ahrens, "How to Take Smart Notes" summaries) | book / https://zettelkasten.de/introduction/ | **P2** | PKM craft canon for personal-corpus stewardship charter scope; informs future curation-worker design principles | markdown essay set |
| Building a Second Brain (PARA method summaries) | https://fortelabs.com/blog/para/ | **P2** | PKM craft: actionability-oriented corpus organization; complements Zettelkasten theory | markdown essay |
| id Software DOOM WAD lump design retrospectives | https://doomwiki.org/wiki/WAD | **P2** | Heritage context for our WAD config system ([id-soft: doom-1993] WAD System tag origin) — curator-relevant since ingestion domains live in a WAD | wiki page |

## Monitoring cadence (standing)

| Source | Cadence | Owner trigger |
|--------|---------|---------------|
| notebooklm-py releases | monthly | N12 KD-liaison duty (Gemini_Notebook workstream) |
| youtube-transcript-api releases | monthly (same pass) | HZ-13 breakage-window budgeting |
| yt-dlp releases + wiki Recent-Changes | quarterly | HZ-14 only if download tiers ship |
| Firecrawl changelog | before any T3 build work | HZ from stale capability snapshot |

*Feeds future curation worker; rows appended as sessions deepen. Format per charter §2.8(b).*
