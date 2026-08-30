<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N12 Mining Brief — Research, Curation & Personal Corpus Knowledge Base

**AP Token**: `AP-N12-MINING-v1.0.0`
**Date**: 2026-08-22
**Node**: N12 curator (Research, Curation & Personal Corpus), overseen by Jem
**Miner**: ONE roc_racoon session (dispatched by pager/researcher — NOT by this Node)
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N12 entry)
**Protocol**: `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` v1.0.0 (Phase M)

---

## Mission

Build the N12 curator Knowledge Base at:

```
data/entities/jem/workspace/N12_CURATOR_KB_20260822.md
```

covering the acquisition→curation→stewardship stack of the Omega Engine: the sovereign
library (`src/omega/library/`), the sovereign search cluster (`src/omega/oracle/search*`
+ `src/omega/search/` + direct tool clients), the ingestion & media pipelines
(`src/omega/ingestion/`, Sieve-and-Sign, youtube_worker daemon), doc-reader tooling,
the staged Grok web-export corpus (PP-2), and the KD content-layer spec
(`config/domains/curators.yaml`). Output is a cited, dated map so N12 can answer
domain questions without re-mining.

## Output Contract (BINDING)

1. **Section order (fixed, T3)** — create skeleton first, then fill in this order:
   ```
   # N12 CURATOR Knowledge Base (2026-08-22)
   ## Source Inventory        (table: path | type | priority | relevance | last_verified)
   ## Per-Source Digests      (### <path> per source, inventory order)
   ## Gotchas                 (stale premises, discrepancies, hazards — with evidence)
   ## Open Questions          (numbered; every unanswered brief question lands here)
   ## L2/L3 Insights          (pattern-level findings only)
   ```
   Later Node-authored appends (`## Deep Dig <n>`, `## N12 Expert Annotation`) are
   RESERVED sections — do not create them.
2. **Incremental appends ONLY.** Never compose the whole KB in one response. Write the
   skeleton, then append after every 2–3 sources digested. Never end a turn with
   announced-but-unwritten work (MR-2).
3. **Append-only + fixed order.** Never edit or reorder prior sections (MR-6).
4. **Cite paths + `last_verified: <date>`** on every source row and every claim of
   substance (MR-8).
5. **Label evidence classes inline**: `measured` / `spec-claimed` / `strings-level` /
   `primary-web` (MR-7).
6. **Verify-before-digest**: existence-check EVERY inventory path before reading;
   missing paths go in Gotchas, never silence (MR-3).
7. **Task no one.** You are a leaf worker. No dispatches, no chains.
8. **On stall**: dump findings + open questions into the stop-report (MR-4). Recover
   ONCE via the same task_id with reprioritized instructions, then report honest
   status — no silent retries, no soft-fail theater (MR-5, M23).
9. **Read-only** everywhere except the output KB file.
10. **Terminus**: ALL inventory P0 sources digested AND all extraction questions
    answered-or-logged-open. If budget runs short: complete the document skeleton
    FIRST, prioritize P0, log the rest open.

## Source Inventory

All paths repo-rooted at `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/` unless
marked ABS. Node existence-checked inventory on 2026-08-22 (glob/ls). Digest in
P0 → P1 → P2 order.

### P0 — Core systems (load-bearing; digest fully)

| # | Path | What to extract |
|---|------|-----------------|
| 1 | `src/omega/library/` (14 modules: `library.py`, `inbox.py`, `indexer.py`, `enrichment.py`, `curator.py`, `catalog.py`, `coordinator.py`, `discovery.py`, `research.py`, `extractor.py`, `rate_limiter.py`, `security.py`, `api_clients.py`, `model_api_clients.py`) | The sovereign library lifecycle: intake→inbox→index→enrich→curate flow; which module owns which stage; public entry points & MCP tool wiring; rate limiting + security roles; inter-module dependencies |
| 2 | `src/omega/oracle/search.py`, `search_router.py`, `search_cache.py`, `search_circuit_breaker.py`, `search_providers.py`, `search_observability.py` | Sovereign search cluster: tiering strategy (local cache→websearch→firecrawl→hub→exa?), routing decision logic, cache semantics, breaker thresholds, observability hooks |
| 3 | `src/omega/search/search_persistence.py` | What search state persists, where, schema |
| 4 | `src/omega/ingestion/` (10 modules: `pipeline.py`, `worker.py`, `cli.py`, `extractors.py`, `scraper.py`, `sources.py`, `guards.py`, `persistence.py`, `verifier.py`, `ingestion_types.py`) | Ingestion pipeline stages; guard/verifier roles (Tainted Data Protocol?); scraper targets; persistence backend |
| 5 | `src/omega/oracle/ingestion.py` | Sieve-and-Sign architecture: sieve criteria, signing/provenance stamps, Tri-Anchor persistence tie-in; relation to `src/omega/ingestion/` (same pipeline or separate?) |
| 6 | `src/omega/workers/youtube_worker.py` + `src/omega/cli/youtube_cli.py` | Daemon cycle: queue→dequeue→transcript fetch→Sieve-and-Sign ingest→log; rate limiting; graceful fallbacks; CLI surface; config consumption |
| 7 | `scripts/universal_doc_reader.py` (+ skim `tests/test_doc_reader.py`) | Doc-reader capabilities: supported formats, extraction method, who calls it, limitations |
| 8 | `config/wads/ingestion/domains.yaml` | Which ingestion domains are configured; WAD structure |
| 9 | `config/youtube_worker.yaml`, `config/youtube_research.yaml`, `config/systemd/omega-youtube-worker.service`, `config/systemd/omega-youtube-worker.timer` | Worker knobs (intervals, queue names, model routing), systemd cadence, key handling (`config/keys/youtube_research.key` — note existence only, DO NOT print contents) |

### P1 — Strategy docs, tool clients, staged corpus

| # | Path | What to extract |
|---|------|-----------------|
| 10 | `src/omega/tools/searxng_direct.py`, `src/omega/tools/firecrawl_direct.py` | Direct MCP-bypass clients: endpoints, params, error handling, when used vs oracle search cluster |
| 11 | `docs/research/SEARCH_DOSSIERS/` (6 files: `searxng.md`, `SEARXNG_DOSSIER.md`, `firecrawl.md`, `FIRECRAWL_DOSSIER.md`, `exa.md`, `EXA_DOSSIER.md`) | Per-provider capability summaries; NOTE: likely duplicate pairs (lowercase vs UPPER) — determine which is current, flag stale in Gotchas |
| 12 | `docs/research/R_YOUTUBE_BACKGROUND_WORKER_SPEC.md`, `R_YOUTUBE_RESEARCHER_V2_RESEARCH_SYNTHESIS.md`, `R_YOUTUBE_RESEARCHER_ENHANCED_SPEC_V2.md`, `R_YOUTUBE_RESEARCH_ENHANCEMENT_PLAN.md`, `R_KNOWLEDGE_FABRIC_SYNTHESIS_20260712.md` | YouTube research design lineage: T1/T2/T3 tier extraction strategy (yt-dlp metadata → transcript API → whisper), known gaps, heritage tags; which parts are IMPLEMENTED vs spec-only (cross-check against P0 code) |
| 13 | `opencode.json` (lines ~40–50 only) | searxng + firecrawl MCP server wiring: command, args, URL/port |
| 14 | `.firecrawl/` dir at repo root | Cache layout: what's cached, naming scheme, TTL/freshness handling if evident |
| 15 | ABS `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/` — digest ONLY: `MASTER_NAVIGATION_INDEX.md`, `QUICK_REFERENCE.md`, `CONSOLIDATION_COMPLETE.md`, and `grok-data-indexed/FTS5_INDEX_README.md`, `grok-data-indexed/MANIFEST.txt`, `grok-data-indexed/BUILD_SUMMARY.txt` | Grok corpus state: account list (8 dirs), conversation/response counts (verify claimed 274 convos / 6,565 responses), FTS5 index schema & build stats, gnosis packs summary, STRATEGIC_RESERVES / TECHNICAL_SYSTEMS subdir purpose. Do NOT walk individual account export files |
| 16 | `data/entities/roc_racoon/workspace/mining_reports/grok_exports_surgical_strike_report.md` | Prior mining methodology + findings; what was already extracted, what remains |
| 17 | `data/entities/researcher/workspace/NODE_GAP_WEB_RESEARCH_JEM_20260822.md` + `data/entities/roc_racoon/workspace/NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md` | Gap-analysis evidence for the Jem line (N11/N12): what gaps were identified for curation domain |
| 18 | `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §6 PP-2 row | Web-export mining pattern definition: scope, blockers, dependencies |

### P2 — Context & peripheral

| # | Path | What to extract |
|---|------|-----------------|
| 19 | `config/domains/curators.yaml` (180 lines) | KD content-layer spec: model_routing/token_budgets/context_windows/proposals sections; bootstrap-order domain table (count them — charter claims 13); Scribe/Verity principle-routing description |
| 20 | `archive/research_pipeline_20260730/background_researcher/searxng_client.py` | Archived prior SearXNG client — patterns worth reclaiming or dead code? |
| 21 | `tests/test_youtube_worker_contract.py`, `tests/test_youtube_research_v2.py` | Contract surface of worker + research module (what behavior is pinned) |
| 22 | `youtube-links-mind-science-esoteric.txt`, `youtube-links-for-ingestion.txt` (repo root) | Pending ingestion queues: count of links, themes |
| 23 | `data/kb/staging/firecrawl_capabilities.json` | Staged firecrawl capability snapshot — freshness check |
| 24 | `pyproject.toml` (extras sections only) | Where yt-dlp / youtube-transcript-api / qdrant-client / redis extras live (debut remediation moved them) |

## Extraction Questions

Answer each from digested sources, or log it numbered in Open Questions:

1. **Library lifecycle**: Trace one item end-to-end: URL enters via inbox → … → curated
   catalog entry. Which module/function owns each hop? What are the actual public APIs
   (the MCP `library_*` tools map to which functions)?
2. **Search tiering**: What is the real fallback/tier order in `oracle/search*`? How do
   cache, circuit breaker, and rate limiter interact? Where does `discovery.py`
   (tiered external discovery) fit relative to `research.py`?
3. **Two ingestion stacks**: `src/omega/oracle/ingestion.py` (Sieve-and-Sign) vs
   `src/omega/ingestion/` (10 modules) — same pipeline, layered composition, or
   parallel/duplicated systems? Who calls whom?
4. **YouTube daemon reality-check**: Of the T1/T2/T3 extraction tiers described in the
   R_YOUTUBE_* specs, what is ACTUALLY implemented in `youtube_worker.py` today?
   (Evidence so far: transcript-first via youtube-transcript-api with graceful
   fallback — confirm and detail.)
5. **Anti-blocking playbook**: Where do transcript-first strategy, perishable
   player_client configs, and on-host ingestion live in code/config/docs? Is there a
   documented playbook file, or is it folklore across R-docs?
6. **Doc-reader role**: What formats does `universal_doc_reader.py` handle, and what
   consumes it (MCP tool? library extractor? manual)?
7. **Grok corpus ground truth**: Actual counts of conversations/responses staged;
   FTS5 index location/schema/query path; what are "gnosis packs"; what does the
   surgical-strike report say was already mined vs remaining; any recorded allowlist/
   privacy risk notes gating PP-2 staging?
8. **KD liaison truth**: Does `config/domains/curators.yaml` define 13 domains or 12?
   Do any `config/domains/<domain>/` directories exist yet? What exactly would N12's
   content-layer duty be per this spec (which domains name jem as curator)?
9. **WAD ingestion config**: What domains does `config/wads/ingestion/domains.yaml`
   configure and how does the WAD layer gate/extend ingestion?
10. **Hazard sweep**: Dead code, stale dossiers (duplicate SEARCH_DOSSIERS pairs),
    broken imports, hardcoded secrets/paths, port conflicts (SearXNG 8080→4017/8017
    history), missing tests — anything a curator must know before operating this stack.

## Constraints

- **Read-only** except the output KB file. No writes to source, configs, trackers, or
  other workspaces.
- **Honest gaps (M23)**: missing files, unreadable paths, stale premises → Gotchas
  with evidence. Never paper over.
- **No secret printing**: never output contents of `config/keys/*`, API keys, tokens.
  Note existence and handling only.
- **Scope discipline**: stay within inventoried sources; incidental discoveries
  relevant to N12 may be appended as extra inventory rows (priority-tagged) rather
  than followed down rabbit holes.
- **Budget priority if constrained**: skeleton first → P0 (rows 1–9) → questions
  1–5 → P1 → remaining questions → P2.

---
*⬡ OMEGA ⬡ JEM ⬡ N12 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n12_mining_brief ⬡ 2026-08-22*

