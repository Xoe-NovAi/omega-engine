# R1 PRE-EXECUTION GNOSIS — final Hebrew-normalization research pass

**Date:** 2026-09-25 (post-compact, before executing the frozen R1 brief).
**Order:** operator-ordered "final deep web research … then execute R1".
**Scope:** tips, gnosis, tools, caveats. **Execution spec stays frozen** in
`R1_HEBREW_NORMALIZATION_BRIEF.md`; this document records what the final pass
changed, validated, and catalogued.

Provenance layers: **[M]** = measured live on Node 1 this session (primary),
**[W]** = web source (primary for its own claims), **[I]** = interpretation.

---

## 1. Corrections to the frozen spec (2 — both applied before coding)

### A0. Compound-column tokenizer correction **[M]**
The brief §3 parenthetical "underscore U+005F (tokenchar by default)" is
**false on this machine's SQLite 3.46.1**: `unicode61` classifies `_` as a
separator (Pc), so `ארץ_ישראל` shatters into `ארץ` + `ישראל` — the compound
backstop would silently store nothing usable. Verified fix **[M]**:

```sql
tokenize = "unicode61 tokenchars '_'"   -- → single vocab term ארץ_ישראל
```

Primary column stays `tokenize = "unicode61"`. Digits split on `-` either way
(`2020-2024` → `2020`,`2024`) — unaffected by the option.

### A1. ASCII quotes are a geresh-family hazard (addendum) **[W]+[M]**
Latin-keyboard typing produces `דו"ח` (U+0022) and `ג'` (U+0027) instead of
gershayim U+05F4 / geresh U+05F3. Measured: `דו"ח` tokenizes to `דו`+`ח` —
two tokens where the reader means one **[M]**. HebrewFTS solves this query-side
via `_normalise_quotes` (ASCII `"` between two Hebrew letters → gershayim) **[W]**.
**Applied to R1:** extend step 6 — delete ASCII `'`/`"` **only when both
neighbors are Hebrew letters** (safe: never fires inside Latin text such as
`don't`). Marks typed as U+2018–U+201F (smart quotes from word processors) are
logged as a possible future A2, not handled now.

### A3. `text_exact` wording reconciliation **[I]**
Brief §3 says "NFC + cantillation-stripped" but §6 says "steps 0–4 only".
Steps 0–4 = NFKC + NFC + cantillation delete + specials delete; dagesh (05BC)
and vowels (05B0–05BB) live in step 5, so **vowels and dagesh survive** —
consistent with the §3 intent ("vowel-preserving"). Implemented as "steps 0–4
only", §3 read as shorthand. Cantillation range delete confirmed: it does not
touch maqaf (05BE), which sits between the deleted ranges.

---

## 2. Validations of the frozen spec (defense-in-depth)

| Frozen decision | Independent confirmation |
|---|---|
| Order NFKC→NFC→delete | Cuénod (BibleTech 2018): manual stripping breaks when "the accent is not the last mark to be added" — canonical reorder-before-delete is exactly why step 2 exists **[W]** |
| D4: maqaf → split; hyphen-likes → space only between Hebrew letters; digits untouched | Maqaf is absent from the Windows Hebrew keyboard, so online writing substitutes ASCII `-`; numbers/dates use Latin hyphen/en-dash and **never** maqaf (elon.io; liquisearch) — the digit exception and hyphen fold are load-bearing **[W]** |
| `remove_diacritics` useless for Hebrew | Official + community docs scope it to Latin/Greek diacritics (GRDB/toba FTS5 docs); our byte-identical measurement is per-spec **[M]+[W]** |
| `text_display` keeps pointed original; `text_index` stripped | HebrewFTS does precisely this: `_strip_nikkud` on the indexed copy, `chunks` keeps pointed text so `snippet()` renders what the reader expects **[W]** |
| App-layer strip + stock unicode61 (no custom tokenizer) | HebrewFTS ships the same stack (pure stdlib + FTS5, `remove_diacritics 2`) and beats plain FTS5 by +0.43 mean recall with *query-time* expansion — i.e. app-layer is a proven architecture on this substrate **[W]** |
| Pointed Gen 1:1 shatters (~25 fragments) | Reconfirmed live during gate prep: `בְּרֵאשִׁית בָּרָא` → `ב`,`אש`,`ית`,`ר`,`ר`,`ב` … **[M]** |

---

## 3. The layer map — what R1 is, and what it is not **[W]**

HebrewFTS orders Hebrew handling by measured impact:

1. **ktiv male/haser synonym expansion** — the big one (+0.43 mean recall;
   e.g. `תכנית`/`תוכנית` pairs) — "most missed Hebrew matches come from here"
2. **clitic-prefix `stems` column** — `הספרייה` reaches a `ספרייה` query
   (prefixes: ב ה ו ל מ ש כ + two/three-letter combinations)
3. **gershayim acronym expansion** — `לדו״ח` → also `דו״ח`
4. **nikkud normalization** — their own words: "a secondary nicety — vowel
   points are rare in real queries, but cheap to handle"

**R1 = layer 4.** It is the cheap, correct, foundational normalization; the
recall mass lives in layers 1–3, which the brief explicitly scopes out
(non-goals). Recommendation **[I]**: file layers 1–2 as a future **R5**
(synonym generator methodology is ready-made — see §4) rather than creeping
R1's scope.

---

## 4. Tool catalogue (all examined; none adopted into R1)

**Directly relevant (same substrate):**
- **HebrewFTS** (github.com/yevgeniyglider/HebrewFTS, MIT, stdlib+FTS5) —
  closest prior art. Reusable recipes:
  - *synonym-set methodology*: generate ktiv variants mechanically (yod/vav
    matres lectionis rules) → keep only sets with >1 form present in corpus
    (rank by orphan count) → human precision review ("same concept, different
    spelling" hard rule) → verify via FTS5 phrase match → keep sets disjoint →
    measure with `bench_recall`.
  - *query sanitising*: phrase-quote every token so user-typed `AND/OR/*/( )`
    are literals (injection defense); `prefix_last` for live typing.
  - **Carry-over caution for our future MATCH wiring: quote every token.**

**Custom-tokenizer alternatives (all out of scope per brief non-goals):**
- `cwt/fts5-icu-tokenizer` (Zig+ICU, has `icu_he` locale, transliteration) —
  **upgrade caveat**: token-form changes require a full FTS5 rebuild.
- `apsw` `apsw.fts5` tokenizers — `unicodewords` (grapheme-aware, "does a lot
  better than unicode61"), `simplify` (casefold + diacritics + combining +
  compatibility). Worth remembering if a custom tokenizer is ever unfrozen.
- `hideaki-t/sqlite-fts-python` — Python-written FTS5 tokenizers.

**Morphology/lemma layer (R6 territory, confirmed):**
- **HebMorph / elasticsearch-analysis-hebrew** (synhershko, hspell dictionary);
  warns: because Hebrew uses quote marks for acronyms, prefer match-family
  queries over `query_string`.
- **liladler/elasticsearch-analysis-hebrew-plugin** (Feb 2026): neural
  lemmatization in the analysis chain — DictaBERT ONNX/INT8, in-process;
  ~490 queries/s over 1M-doc Hebrew Wikipedia. Proof that lemma-level recall
  is the modern frontier — and that it needs a model, not regexes.
- `hotstar/hebrew-analyzer`: ngram/semi-exact analyzers with `$` exact-suffix
  markers (prefix-vs-exact disambiguation trick).

**Strip utilities (all redundant with our function):** Cuénod's hebrewHelper,
Aleph Tools (d7m.tg), `linkaiil1234/hebrew-text-utils` (JS), LingQ forum
recipes, Google-Sheets regex hacks.

**Corpus side:** Sefaria-Export layout already known (GCS JSON/txt);
Sefaria's search internals are not documented in the README — no additional
gnosis recovered there.

**Papers for the shelf:** DictaBERT (arXiv:2308.16687 — *prefix-segmentation
fine-tune*, directly matching layer 2); BEREL (arXiv:2208.01875 — Rabbinic
Hebrew BERT, relevant to the grimoire corpus); Joint diacritization/
lemmatization/normalization (arXiv:1910.02267); Nakdan (arXiv:2005.03312);
"What's Wrong with Hebrew NLP" (arXiv:1908.05453).

---

## 5. Caveat list (standing warnings)

1. **BM25 never errors on garbage** — pre-normalization the index "ships
   character soup" while reporting success (our own engineering folio). Any
   future corpus must run the pipeline version tag per row (brief §6).
2. **`remove_diacritics` will not save you** — per-spec Latin/Greek only;
   do not "fix" Hebrew by flipping it.
3. **Maqaf vs ASCII hyphen is a corpus reality**, not theory — both must fold
   (they do: step 7).
4. **Underscore is not a tokenchar** until declared (A0) — any doc/sample
   claiming otherwise on 3.46.1 is wrong.
5. **Query-side must mirror index-side** — `normalize_hebrew_query` is the
   same function (identity-asserted in tests); never strip only at index time.
6. **Acronym quotes are query-operator hazards** in raw FTS5/ES query
   strings — phrase-quote tokens at the MATCH layer (HebrewFTS/HebMorph).
7. **ZWNJ/ZWJ (200C/200D) and CGJ (034F)** are invisible — deleted here;
   watch for them in Persian/Arabic mixed content.
8. **Final-form fold trades precision for OCR recall** (accepted in brief);
   `text_exact` and `text_display` preserve the original for disambiguation.
9. **Geresh deletion merges some forms by design** (שׁ/שׂ → ש, בּ/ב) —
   precision backstop is `text_exact`, not the index column.
10. **Layer-4-only ceiling**: point-stripping alone will not reach
    cross-spelling or prefixed matches; do not read R1 as solving Hebrew
    recall — it makes the lexical channel *legible*, dense retrieval keeps
    carrying semantic recall until R5/R6.

---

## 6. Impact on execution

Pipeline order: **unchanged**. Changes applied: **A0** (compound tokenizer
DDL), **A1** (ASCII quotes in geresh step), **A3** (exact-column reading — no
behavior change). Everything else validated. **Execute the frozen brief.**
