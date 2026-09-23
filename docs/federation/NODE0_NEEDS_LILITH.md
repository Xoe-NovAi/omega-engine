# Node 0 → Node 1 Needs List — Lilith / Arcana-NovAi WAD

> **Purpose**: everything Lilith-N1 Phase 0–2 is waiting on from Node 0 (HP Pavilion).
> **Owner**: Build agent (Node 1). Update here as items arrive; check off on receipt.
> Companion strategy: `docs/entities/LILITH_STRATEGY_FINAL.md`. Backlog: `docs/ROADMAP.md` P4.

---

## N0-1 — Crawl4AI Lilith/Kabbalah scraper (port to N1)
- **What**: the `crawl4ai`-based scraper on Node 0 (configs, rate limits, source lists).
- **Deploy to**: `~/WanderGround/scrapers/crawl4ai_lilith/`
- **Output**: structured markdown → `~/WanderGround/lilith_sources/harvested/`
- **Status**: `backlog` (awaiting N0 package)

## N0-2 — Online library book-curation system (port to N1)
- **What**: the book-curation pipeline on Node 0 (tagging, annotation, epub/pdf → markdown).
- **Deploy to**: `~/WanderGround/library/`
- **Output**: curated corpus → `~/WanderGround/lilith_sources/curated/`
- **Status**: `backlog` (awaiting N0 package)

## N0-3 — XYZ spatial-vector system (port to N1)
- **What**: Node 0's developed/implemented xyz spatial-vector pipeline
  (embed → UMAP/projection → x,y,z + cluster persistence).
- **Why**: VR is lowest priority, but xyz on every ingested record helps
  retrieval now AND prepares the mystery-school spatial layer later.
- **Integrate with**: WanderGround `spatial/knowledge_atlas.db` + `project_umap_3d.py` path.
- **Status**: `backlog` (awaiting N0 package)

## N0-4 — Personal gnosis corpus (Lilith origin story)
- **What**: operator's existing Lilith entity-design plans + the story of how
  this work came to be (Omega Engine genesis, vision downloads, Tarot deck origin).
- **Deploy to**: `~/WanderGround/lilith_sources/personal/` as
  `visions/`, `tarot_genesis/`, `omega_engine_origin/`, `channelings/`
- **Gates**: Phase 1 voice-DNA quality.
- **Status**: `backlog` (operator to provide soon)

## N0-5 — Lilith-N0 ↔ Lilith-N1 integration posture (future)
- **What**: how the eventual Node 0 Lilith work merges with Lilith-N1 deepening.
- **Status**: explicitly **deferred** — not discussed until N1 prototype is stable.
  Recorded here so it isn't lost.
