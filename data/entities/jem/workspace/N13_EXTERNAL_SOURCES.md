# N13 arcana — External Sources (T5)

**AP Token**: `AP-N13-EXTERNAL-SOURCES-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ N13-ARCANA ⬡ opencode ⬡ trc_external_sources ⬡ CONSULTABLE
**Date**: 2026-08-22 · **Policy**: Core = PD-primary only (Kali ruling Q3). Modern tools (Tarotoo MCP, kerykeion, pyswisseph) = **reference-only** — never PD-primary corpus.

---

## Prioritized Queue

| # | Title / Source | Tier | Why | Target Format |
|---|---------------|------|-----|---------------|
| 1 | **Golden Dawn *Book T*** (c.1890s MS; GD tarot attributions) | **P0** | The founding PD primary for decan/planetary/zodiac attribution system; basis of entire correspondence DB | Structured rows: card ↔ decan ↔ planet ↔ sign ↔ Hebrew letter, each with provenance FK |
| 2 | **Waite, *The Pictorial Key to the Tarot* (1910/1911)** — sacred-texts.com full text | **P0** | Complete divinatory meanings for all 78 cards; PD-clean; Tarotoo's own cited anchor | Per-card upright/reversed meaning fields; cross-ref vs Tarotoo editorial layer |
| 3 | **Mathers, *"The Tarot"* essay (1888)** — sacred-texts.com | **P0** | Earliest GD published tarot-Kabbalah attribution set; short, fully extractable | Path↔card↔Hebrew letter table |
| 4 | **Mathers, *The Kabbalah Unveiled* (1888)** | **P0** | Sephiroth/Divine Names primary text for Tree-of-Life columns of DB | Sephirah records: name, translation, divine name, archangel, order of angels |
| 5 | **Papus, *Tarot of the Bohemians* (1896 Eng. trans.)** — sacred-texts.com | **P1** | Cross-reference source (OQ-010 requires ≥2 PD sources per entry); numerology/arcana correspondences | Secondary confirmation column in provenance join |
| 6 | **Kircher, *Oedipus Aegyptiacus* (1652)** | **P1** | Historical path schema provenance (W4-cited); deep-history column | Schema-provenance notes only (heavy extraction deferred) |
| 7 | **Sacred Texts Archive** esoteric sections (tarot/, kabbalah/, gem/) | **P1** | Bulk PD host for items 2-5 + Ouspensky 1913, Thierens 1930 | Crawl manifest → per-work extraction tickets |
| 8 | **Project Gutenberg** occult/Hermetic catalog | **P2** | Supplementary bulk PD texts (e.g., Waite's other works, Levi translations) | On-demand pulls as DB gaps appear |
| 9 | **multimodalart/1920-raider-waite-tarot-public-domain** (HF) | **P2** | PD image corpus (Pamela-A era scans) for deck-design lineage (Lilith Deck work) | Image refs keyed by card id — no text extraction |

## Reference-Only (modern tools — NOT corpus sources)

| # | Tool / Dataset | License | Use Boundary | Routed To |
|---|---------------|---------|--------------|-----------|
| R1 | **Tarotoo dataset** (github/HF/Kaggle/PyPI `tarotoo-tarot` v1.7.1) | MIT | Methodology template: 22-field schema, CI validation pattern. Content stays out of sovereign DB except as cross-check annotations | N4 (MCP integration, OQ-005) |
| R2 | **Tarotoo MCP server** (`io.github.Tarotoo-com/tarotoo-mcp-server`, stdio, Node≥18) | MIT | Live lookup interface for AI assistants; 5 stable tools (`get_card_meaning`, `list_cards`, `search_cards`, `yes_no_answer`, `draw_cards`). License inconsistency (README CC-BY vs LICENSE MIT) → contract review before wiring | N4 (OQ-005) |
| R3 | **pyswisseph** ≥2.10.3.2 | GPL-2.0+ | Swiss Ephemeris bindings; CPU-only ~few MB (+~50MB ephemeris data). Preferred astrology engine path — process-boundary keeps engine license-clean | N3 (OQ-009) |
| R4 | **Kerykeion** v5.12.9 (stable) / v6.0.0a26 (alpha) | **AGPL-3.0** ⚠️ | Viral license — optional-extra-with-boundary at most; never core-linked. Hosted Astrologer API alternative violates M7 spirit | N3 (OQ-009) |
| R5 | `nosleepcassette/sephiroth` CLI | modern code | Study reference for correspondence UX; content derived from Liber 777 → do NOT ingest data | monitor only |
| R6 | `gadicc/magickli` `sephirot.json5` | open data | Structure comparison for sephirah record design | schema-design input |
| R7 | Deckaura 12-dimension dataset (SSRN/Zenodo) | check | Numerology dimensions; license unverified | P2 watchlist |
| R8 | Global Spiritual Studies GD attribution tables (Jul 2026) | web | Modern secondary — use to locate PD primaries, not as source | navigation aid |

## Excluded (copyright-encumbered — hard ban)

*Liber 777* (Crowley, most editions) · Regardie *The Golden Dawn* (1937+) · DuQuette titles · Wang *Introduction to the Golden Dawn Tarot* (1978, access-restricted IA copy).

---

**Queue stats**: 9 PD-primary targets (4×P0, 3×P1, 2×P2) · 8 reference-only · 4 hard-excluded.
**Cold-reader test**: a fresh agent can determine what to ingest, from where, under which license boundary, and who owns integration — without reading the KB.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: N13-ARCANA | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
