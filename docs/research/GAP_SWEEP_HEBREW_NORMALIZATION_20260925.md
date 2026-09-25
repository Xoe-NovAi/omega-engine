# Hebrew Normalization Expertise — Research Folio (Humboldt, 2026-09-25)

**Mode:** research-only. **Legend:** `[VERIFIED live-fetch]` = fetched this session; `[REPORTED-NOT-VERIFIED]` = excerpts only, confirm before building.

## 0. Posture

Normalize in the **application layer, not in FTS5**. Keep FTS5 stock `unicode61`. Canonical (display) text ≠ index text — every serious system surveyed separates them. The FTS5 defect is lexical-only: Qwen byte-BPE does not shatter on Unicode categories (fertility rises, sequence preserved), so feed embeddings the same stripped text for chunk-consistency and verify via eval.

## 1. Code-point inventory (Unicode Ch.9 §9.1.1–9.1.2 verified)

Consonants U+05D0–U+05EA + finals ךםןףץ (**do NOT auto-convert final↔non-final**). Vowels U+05B0–U+05BB + U+05C7. Dagesh/mappiq/shuruq all U+05BC (one point, three functions). Holam U+05B9 (+U+05BA vav-only). Shin/sin dots U+05C1/U+05C2 (strip merges שׁ/שׂ — accepted recall trade). Cantillation U+0591–U+05AF. Maqaf U+05BE = category **Pd** (why unicode61 splits). Sof pasuq U+05C3, paseq U+05C0, geresh/gershayim U+05F3/U+05F4 (dual role: loan phoneme vs abbreviation), Yiddish digraphs U+05F0–U+05F2 (independent characters — expand for Hebrew-primary index), presentation forms U+FB00–U+FB4F (normalize to canonical), CGJ/ZWJ/ZWNJ strip.

**NFC/NFD/NFKC/NFKD (UAX #15 verified):** reorder marks into canonical order — the only Hebrew-relevant effect. They do NOT strip, unify שׁ/שׂ, or unify qamats variants. NFKC additionally folds U+FBxx compat forms (desirable for OCR/Sefaria-mixed text, never for display). Composition exclusions (§5.1): NFC will NOT recompose some Hebrew letter+dagesh/vowel combos — never assume one-code-point-per-visual. Not closed under concatenation: normalize full field values, or re-normalize after join.

**UAX #29 verified for framework; FTS5 negative result verified:** `unicode61` splits on L\*/N\*/Co runs per sqlite.org/fts5 §4.3.1 — Mn/Pd/Po are separators **by construction**. `remove_diacritics` folds Latin-script diacritics only. Our byte-identical measurement is per-spec behavior, not a bug.

## 2. Pipeline order (strip order matters — apply identically to docs, embeddings, queries)

0. Logical-order UTF-8 in (never reorder for storage). 1. NFKC (fold U+FBxx/width/ligatures). 2. NFC (canonical order). 3. Delete cantillation U+0591–U+05AF. 4. Delete U+05C3/05C0/05C6/05C4/05C5/05BD/05BF/FB1E/034F/200C/200D. 5. Delete vowels+modifiers U+05B0–05BB/05BC/05C1/05C2/05C7. 6. Geresh: loan-phoneme → delete; abbreviation/gematria → delete + index bare skeleton. 7. Maqaf U+05BE → space (also hyphen-likes between Hebrew letters only). 8. Yiddish digraphs → expand. 9. Final-form fold ךםןףץ→כמנפצ (default ON — recovers OCR's #1 Hebrew failure). 10. Whitespace collapse + Latin lowercase. 11. Assert no Mn/Me/Cf remain; log violations with source_file.

## 3. Maqaf decision (D4) — RECOMMEND SPLIT

Academy prescribes maqaf as the native-compound binder (distinct from loanword hyphen). Sefaria docs describe `exact` (standard analyzer) + `sefaria-naive-lemmatizer` (prefix-strip, plural→singular, full/defective spelling) — plugin source exists (GPL-3.0) but internals unverified; community consensus pattern is "vowels/cantillation removed, maqaf as space". HebMorph lineage: split-then-link (Smichut tagging), not keep-whole. Linguistic fact: maqaf units are phonological words but morphological phrases — retrieval wants morphology (אָדָם must match אֵת־הָאָדָם). **Primary: split. Backstop: second FTS5 column with maqaf→underscore for exact-compound precision** (no custom tokenizer needed).

## 4. Niqqud decision (D5) — RECOMMEND STRIPPED-PRIMARY

Universal pattern (Sefaria, HebMorph, Logos, Mechon Mamre dual editions): strip/fold before the inverted index; display preserves. Precision loss is narrow: homographs distinguished ONLY by pointing (דָּבָר/דִּבֵּר, סֵפֶר/סָפַר/סִפֵּר, בֹּקֶר/בָּקָר, qamats gadol/qatan, shin/sin, dagesh functions) — costs precision on contrastively-pointed expert queries, ~0 on recall. **Three columns:** `text_display` (byte-faithful, never searched), `text_index` (stripped — FTS5 + embedding input), `text_exact` (optional: NFC + cantillation-stripped, vowel-preserving, for quoted pointed queries).

## 5. FTS5 options ranked

1. **App-layer strip + stock unicode61** — S–M effort, sovereign, testable via fts5vocab. DO THIS.
2. `tokenchars '־'` for compound-whole column only — one-line DDL, never primary.
3. Trigram secondary for OCR-fuzzy/LIKE — 3–5× bloat on that column, ranking-insensitive use only.
4. Custom C tokenizer (strip+split+COLOCATED synonyms) — weeks, only if Phase-2 recall demands it.
5. ICU `icu_he` — NOT recommended as primary (Latinizes Hebrew, breaks single-binary sovereignty).
Never: `categories ... Mn` (explodes vocabulary), `porter` on Hebrew, trigram as primary.
**fts5vocab gate:** Gen 1:1 → ~7 consonantal tokens; no U+0591–U+05C7 terms; maqaf-split neighbors present.

## 6. Multilingual + transliteration

One FTS5 table (Hebrew/Aramaic share the pipeline; Latin case-folded; Yiddish digraphs expanded); `lang` column for filtering, never split tables. **Transliteration never meets Hebrew script in stock unicode61** — start with a versioned `synonyms_he_translit` table applied as query-time OR-expansion (tractates, divine/demonic names, places), with provenance per row; no algorithmic transliteration. Judeo-Aramaic: same mechanics; Bavli proclitics (בכ״למשוהד״ש) handled as query-time OR heuristic, not index destruction. Syriac script mapped now, handled when corpus arrives. RTL: storage is logical-order UTF-8, rendering is viewer concern — strip bidi controls from index strings.

## 7. Embeddings + eval

No published GTE-multilingual-base vs Qwen3-0.6b comparison **on Hebrew religious retrieval** exists — say so explicitly, claim no winner. Default: keep qwen3@768 (federated-compatibility seed wins over speculation), GTE as challenger. Tokenizer note: byte-BPE preserves the sequence (fertility ↑, no loss) — defect is lexical-only. **Eval:** ≥500-chunk pilot; 40 queries across 4 strata (vocalized Tanakh pointed+stripped variants / unvocalized Rabbinic / Aramaic both scripts / transliteration-only); graded 0–3 relevance (operator or Sefaria-link weak labels), blinded; ablate FTS5 raw vs stripped, query pointed vs stripped, compound on/off, Qwen vs GTE, hybrid RRF; NDCG@10 primary, MRR secondary, per-stratum reporting. **Gate:** ship iff stripped ≥ raw on recall and hybrid ≥ either alone. Re-run on any pipeline change.

## 8. OCR-to-index

Hebrew confusables: ד/ר, ב/כ, ה/ח/ת, ו/ז/ן, ם/ס, ג/נ, ך/ד, י/ו, final forms, geresh dropped/hallucinated, maqaf↔hyphen↔space. Literature (Kissos & Dershowitz 2016/17 via LDK 2025): confusion-matrix + classifier first, then LM correction; **image-enhancement selection beats lexicon-only correction 2×**. Index corrected-primary + raw-OCR secondary (dual fields); preserve page-image coordinates for future word-spotting (Friedberg model). Never train on unmeasured CER claims — measure on ~20 pages against known transcription.
