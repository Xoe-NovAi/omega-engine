# R1 EXECUTION BRIEF — Hebrew FTS5 Normalization (ready post-compact)

**Status:** READY TO EXECUTE. Research complete (folios: `GAP_SWEEP_HEBREW_NORMALIZATION_20260925.md`, `GAP_SWEEP_ENGINEERING_HUMBOLDT_20260925.md` §1). **Do not re-research. Execute.**
**Roadmap:** P4.8 Tier-0 R1. **Effort:** ~2h. **Risk:** low (new code + re-index; no schema migration on live data until gated).

## 0. Problem (measured, not hypothesized)

FTS5 `unicode61` shatters vocalized Hebrew (Gen 1:1 → 25 fragments); maqaf U+05BE splits; `remove_diacritics` 0/1/2 byte-identical (Latin/Greek only). Unvocalized Rabbinic prose is fine. Lexical channel is currently noise for pointed text while dense retrieval carries 100% of Hebrew recall.

## 1. Build

**New file:** `scripts/hebrew_normalize.py` — one pure function `normalize_hebrew_index(s: str) -> str` implementing the pipeline below, plus `normalize_hebrew_query = normalize_hebrew_index` (same function, symmetric path — assert identity in tests).
**Tests:** `tests/test_hebrew_normalize.py` — Gen 1:1 → ~7 consonantal tokens; no Mn/Me/Cf remain (regex `[\p{Mn}\p{Me}\p{Cf}]` empty — use `unicodedata.category`); maqaf-split neighbors; idempotence (normalize(normalize(x)) == normalize(x)); NFC-order convergence case.

## 2. Pipeline (exact order — strip order matters)

0. Input: logical-order UTF-8 (never reorder, never store visual order).
1. **NFKC** — fold U+FBxx presentation forms, widths, ligatures (retrieval fields only, never display).
2. **NFC** — canonical-compose + ccc-sort marks (converges meteg/vowel order variants).
3. **Delete** cantillation U+0591–U+05AF.
4. **Delete** U+05C3, U+05C0, U+05C6, U+05C4, U+05C5, U+05BD, U+05BF, U+FB1E, U+034F, U+200C, U+200D.
5. **Delete** vowels/modifiers U+05B0–U+05BB, U+05BC, U+05C1, U+05C2, U+05C7 (merges שׁ/שׂ, בּ/ב — accepted recall trade; precision backstop is `text_exact`).
6. **Geresh:** loan-phoneme (ג׳ז׳צ׳ etc.) → delete geresh, keep base; abbreviation/gematria → delete geresh+gershayim, keep bare skeleton.
7. **Maqaf** U+05BE → ASCII space (DEFAULT D4: split-primary). Also fold hyphen-likes U+002D/U+2010–U+2015 → space ONLY between Hebrew letters (`[\u05D0-\u05EA]` both sides); between digits keep as-is.
8. **Yiddish digraphs** U+05F0–U+05F2 → expand (וו/וי/יי).
9. **Final-form fold** ךםןףץ→כמנפצ (default ON — recovers OCR's #1 Hebrew failure mode).
10. Collapse whitespace; ASCII-lowercase Latin runs (Hebrew has no case).
11. Assert + log violations with source_file.

## 3. Schema (three columns)

- `text_display` — byte-faithful original (NFC only). Never searched, always shown.
- `text_index` — pipeline output. FTS5 (`unicode61`, defaults) + embedding input.
- `text_compound` — pipeline output EXCEPT maqaf→underscore U+005F (tokenchar by default) instead of space. Exact-compound precision backstop.
- `text_exact` (optional, cheap, recommended) — NFC + cantillation-stripped, vowel-preserving (steps 0–4 only). Routes quoted pointed queries.

## 4. Defaults pending operator confirm at session start (D4/D5)

D4 = split-primary + compound backstop. D5 = stripped-primary + pointed auxiliary. Both reversible at re-index cost — **do not let confirmation block execution**; proceed on defaults unless overridden.

## 5. Gate (all must pass before R1 is DONE)

1. `fts5vocab` on a dev sample: Gen 1:1 → ~7 consonantal tokens; zero terms containing U+0591–U+05C7; maqaf-split compounds adjacent.
2. Query symmetry test: pointed query and stripped query return identical sets on the pilot corpus.
3. `make lint && make test && make docs` green.
4. Non-goals (explicitly OUT): custom C tokenizer, trigram primary, ICU, Dicta runtime, embedding eval (that's R6, separate).

## 6. Provenance to record on completion

Pipeline version tag on every indexed row; drawer in `wing_lilith/grimoire` with before/after token counts; diary entry; P4.8 status flip R1 → done.
