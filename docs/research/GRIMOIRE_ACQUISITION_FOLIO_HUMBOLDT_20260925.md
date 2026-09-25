# OFFLINE GRIMOIRE LIBRARY — Humboldt Research Folio

**Date:** 2026-09-25 · **Researcher:** Humboldt (polymath lead) · **Mission:** Lilith-first sovereign offline corpus
**Node:** Node 1 (i7-13620H · 16GB · 79GB free · CPU-only) · **Budget:** `<5GB` curated
**Target:** `wing_lilith / room grimoire` · `qwen3-embedding:0.6b truncate_dim=768`
**Mode:** RESEARCH-ONLY. No code executed, no files written, no downloads performed.

> "Nature is a unified whole." The Lilith isotherm runs from Sumerian `lilitu` through Nippur bowls to Zohar — one gradient, many instruments. This folio calibrates every instrument before descent.

**Verification legend:**
- `[LIVE-VERIFIED]` — fetched live during this session (page body or search excerpt from primary source, Sept 2026)
- `[REPORTED]` — consistent secondary reporting, not live-fetched; verify before building
- Operator-verified baseline (accepted without re-verification): Sefaria-Export ~26GB/~85K GCS `gs://sefaria-export/`, Archive.org advancedsearch+metadata live, Montgomery 1913 full text, Alphabet-of-Sirach PDF, Gutenberg bulk protocol documented

---

## EXECUTIVE SUMMARY — Ranked isotherms

| Priority | Finding | Action |
|---|---|---|
| **1** | Sefaria bulk GCS is the trunk — everything else is branches | `books.json` + per-category `gcloud storage cp` filtered to Lilith ladder; never crawl `sefaria.org` HTML, never re-pull monthly |
| **2** | Archive.org APIs > scraping; `_djvu.txt` + `_djvu.xml`/`hOCR` + EPUB/PDF derivatives are sufficient | `advancedsearch.php` → `metadata/{id}` → `download/{id}/` selective fetch |
| **3** | Gutenberg via rsync + `pg_catalog.csv` filter, not crawl | `rsync gutenberg.pglaf.org::gutenberg` with `--include` for ~20 titles only |
| **4** | ETCSL has no bulk API; ORACC has ZIPs; CDLI has REST+client; Perseus has git+CTS | Clone/pull, do not scrape aggressively |
| **5** | sacred-texts.com is high-value PD but has **no API, polite-crawl only**, stale 1922 threshold language | crawl4ai at 1–2 concurrency, 1.5–3s delay, retain attribution |
| **6** | HebrewBooks has **no public API** `[LIVE-VERIFIED]`; per-book PDF handler only | Selective fetch of ~10–30 IDs, expect scans + poor OCR, quarantine Moznaim/JTS-rights pages |
| **7** | HathiTrust bulk is **infeasible** for this mission (approval + 480GB–5.4TB + Google-digitized exclusions) | Use catalog search for discovery, fetch single PD volumes via Data API only |
| **8** | Anna's Archive **EXCLUDE** — defensibility verdict below | Do not touch |
| **9** | Canonical format: **markdown+frontmatter**; retain sources; TEI only where native | Pandoc never as blind converter for Hebrew/Aramaic |
| **10** | Scale breaks at 100k files on inode/WAL/brute-force scan/watchers — pre-empt by sharding now | SQLite catalog + sqlite-vec + FTS5 hybrid, single-file portable, batch commits |

---

## FRONT 1 — ACQUISITION METHODS (ranked per source class)

### 1.1 Sefaria: bulk-vs-API-vs-per-text

**Rank: 1. BULK GCS FILTERED (default) > 2. Per-text curl (ladder gaps) > 3. Live API (updates/links only) > 4. NEVER crawl HTML**

`[LIVE-VERIFIED]` Bucket structure, `books.json` monthly regeneration (2nd of month), helper scripts confirmed via live fetch of `github.com/Sefaria/Sefaria-Export`:

```
gs://sefaria-export/
  json/{categories}/{title}/{language}/{versionTitle}.json
  txt/{categories}/{title}/{language}/{versionTitle}.txt
  cltk-full/ cltk-flat/ schemas/{title}.json
  links/links0.csv ... links12.csv
  table_of_contents.json
```

Concrete commands `[LIVE-VERIFIED]`:

```bash
# index (small, ~25MB repo)
git clone https://github.com/Sefaria/Sefaria-Export.git
# browse without downloading
./examples/browse_bucket.sh
./examples/browse_bucket.sh json/Talmud
# single Lilith rung
curl -O "https://storage.googleapis.com/sefaria-export/json/Tanakh/Torah/Genesis/English/merged.json"
# entire category (JSON or txt)
./examples/download_category.sh Talmud
./examples/download_category.sh Mishnah txt
gcloud storage cp -r "gs://sefaria-export/json/Talmud/" ./talmud/
# programmatic filter (Lilith-first: Tanakh, Talmud Bavli relevant tractates, Midrash, Kabbalah/Zohar Hebrew)
python examples/download_from_books_json.py --category Tanakh --list
python examples/download_from_books_json.py --category Kabbalah --language Hebrew
python examples/download_from_books_json.py --title "Genesis"
```

Live API (for deltas, links, versions — not bulk) `[REPORTED]`:

```
GET https://www.sefaria.org/api/texts/Genesis.1.1
GET https://www.sefaria.org/api/bulktext/Genesis.1.1|Isaiah.34.14|Shabbat.151b
GET https://www.sefaria.org/api/index  (TOC)
GET https://www.sefaria.org/api/v2/index/{title}  (schema, sectionNames, addressTypes)
GET https://www.sefaria.org/api/related/{ref}
GET https://www.sefaria.org/api/versions/{title}
```

Tradeoffs:

| Method | When | Cost on Node 1 | Note |
|---|---|---|---|
| Bulk filtered | Initial Lilith pull (Tanakh+selected Talmud/Midrash/Zohar-Hebrew) | MBs–1GB, not 26GB | Use `merged.*` only; keep `schemas/` alongside |
| Per-text curl | Filling 1–5 missing rungs | KBs | Prefer `txt/` for embedding candidate, `json/` for structure |
| API | Freshness check, links graph | Tiny | No auth; throttle politely; `bulktext` for verse batches |
| HTML crawl | NEVER | — | Loses JaggedArray structure, violates politeness, redundant |

**Licensing nuance (operator baseline, extend):** per-version `license` field must be read per file. JPS 1917 + Tanach text-only = PD; Masoretic Hebrew CC-BY-SA (allowed, share-alike — compatible with offline library if attribution retained, never relicensed); JPS gender-sensitive CC-BY-NC + Koren CC-BY-NC = **quarantine read-only**. Worker must parse license before promotion to `curated/`.

**Effort:** S (0.5 day to filter + pull Lilith subset). **Open question:** Does `books.json` expose `license` per entry or must worker open each JSON header? `[REPORTED]` — inspect one `merged.json` header before freezing normalizer.

### 1.2 Archive.org: metadata → derivatives (no crawl4ai needed)

**Rank: API-only. Never crawl `archive.org/details/*` HTML with a browser.**

`[REPORTED]` endpoints (stable for a decade, confirmed via developer portal excerpts):

```
# discovery
https://archive.org/advancedsearch.php?q=title%3A%28lilith+OR+%22incantation+bowls%22%29+AND+mediatype%3Atexts&fl[]=identifier,title,creator,date,licenseurl,downloads&rows=50&out
...[truncated 27072 chars]