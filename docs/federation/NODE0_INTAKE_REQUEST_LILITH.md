# NODE 0 → NODE 1 INTAKE REQUEST: LILITH / ARCANA-NOVAI WAD
**From**: Node 1 Build Agent (ASUS ExpertBook P1503CVA)  
**To**: Node 0 Archival Bastion (HP Pavilion) — Omega Core Hub `:8016`  
**Date**: 2026-09-23  
**Priority**: Unblocks P4.0–P4.2 on Node 1  
**Tracking**: `docs/federation/NODE0_NEEDS_LILITH.md` (this repo)

---

## 📦 Requested Packages

| ID | Package | Deploy Path (N1) | Purpose | Blocks |
|----|---------|------------------|---------|--------|
| **N0-1** | Crawl4AI Lilith/Kabbalah scraper | `~/WanderGround/scrapers/crawl4ai_lilith/` | Harvest primary + esoteric sources to `lilith_sources/harvested/` | P4.1 Lore harvest |
| **N0-2** | Online library book-curation system | `~/WanderGround/library/` | Tag/annotate/convert epub→markdown for `lilith_sources/curated/` | P4.1 Lore harvest |
| **N0-3** | XYZ spatial-vector pipeline | `~/WanderGround/spatial/` (integrate with `knowledge_atlas.db` + `project_umap_3d.py`) | UMAP 3D coords on every ingested record; VR-prep that helps retrieval now | P4.0 Foundation |
| **N0-4** | Personal gnosis corpus | `~/WanderGround/lilith_sources/personal/` (`visions/`, `tarot_genesis/`, `omega_engine_origin/`, `channelings/`) | Lilith voice-DNA quality, axioms, origin story | P4.1 voice quality |
| **N0-5** | Lilith-N0 ↔ Lilith-N1 integration posture | (deferred, recorded) | Future federation of the two Lilith instances | P4.x (post-P4.3) |

---

## 📋 Package Specifications

### N0-1: Crawl4AI Scraper
**Required contents:**
- Scraper config (sources, rate limits, concurrency)
- Source list: Sefaria (Zohar 1:5a, Ben Sira, Talmudic tractates), Chabad.org, Kabbalah.info, Arizal texts, Golden Dawn papers, Crowley Liber 777, Lilith Magazine, JSTOR/Google Scholar Lilith studies, Jewish feminist midrash collections
- Output: structured markdown files, one per source/document
- Must respect `robots.txt`, implement polite delays, handle pagination
- **Output format**: `~/WanderGround/lilith_sources/harvested/<category>/<source>_<doc>.md`

### N0-2: Library Curation System
**Required contents:**
- Tagging/annotation UI or CLI
- EPUB/PDF → markdown converter (pandoc-based or equivalent)
- Metadata extraction (author, date, ISBN, DOI)
- Corpus organization: `lilith_sources/curated/<domain>/<title>.md` with frontmatter
- Integration with WanderGround `wander` CLI for auto-curator ingestion

### N0-3: XYZ Spatial-Vector Pipeline
**Required contents:**
- Embedding → UMAP (3D) projection code
- `sqlite-vec` integration for `knowledge_atlas.db`
- Cluster assignment (HDBSCAN/KMeans)
- Coordinate normalization to bounding sphere R=100
- **Output**: updates `concepts` table with `x,y,z,cluster_id`
- Must accept `qwen3-embedding:0.6b` 768-dim vectors (Node 1 embedding server)

### N0-4: Personal Gnosis Corpus
**Required structure:**
```
lilith_sources/personal/
├── visions/           # Direct channelings, visionary downloads
├── tarot_genesis/     # Lilith Tarot Deck origin, design iterations
├── omega_engine_origin/  # How the Engine was born from the vision
└── channelings/       # Ongoing Lilith dialogue logs
```
**Format**: markdown with frontmatter (`date`, `type`, `tags`, `reliability`)
**Critical for**: Lilith voice-DNA baseline, axioms in `soul.yaml`, personal mythos

---

## 🚚 Delivery Mechanism

**Preferred**: USB handoff (as with NFS_L2 briefing) — air-gap safe, no network dependency.  
**Alternative**: Tailscale `scp` to `xnai@xnai-n1-asus.tail51f14a.ts.net:~/WanderGround/`  
**Notification**: On delivery, signal via `omega-hub` task event or direct message.

---

## ⏱️ Timeline Impact

| Package | If delivered by | P4.1 starts | P4.0 complete |
|---------|-----------------|-------------|---------------|
| N0-1 + N0-2 | Week of 2026-09-30 | ✅ | ✅ |
| N0-3 | Week of 2026-09-30 | — | ✅ |
| N0-4 | Week of 2026-10-07 | ✅ (voice quality) | — |

---

## 📍 Node 1 Staging Ready

All deploy paths created and empty:
- `~/WanderGround/scrapers/` ✓
- `~/WanderGround/library/` ✓
- `~/WanderGround/spatial/knowledge_atlas.db` (sqlite-vec ready) ✓
- `~/WanderGround/lilith_sources/{harvested,curated,personal}/` ✓

**Node 1 is waiting. No further prep needed on this side.**

---

*Request recorded in `docs/federation/NODE0_NEEDS_LILITH.md`. Update that file on receipt.*