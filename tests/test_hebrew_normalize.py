"""R1 tests — hebrew_normalize (brief §1, §5 gates, gnosis A0/A1).

Covers: Gen 1:1 → ~7 consonantal tokens, no Mn/Me/Cf residue, maqaf split,
idempotence, NFC-order convergence, final-form fold, geresh/gershayim (incl.
A1 ASCII quotes), Yiddish digraphs, query-identity, compound underscore,
display/exact columns, and both execution gates:

  Gate 1  fts5vocab dev sample: 7 consonantal tokens, zero terms in
          U+0591–U+05C7, maqaf-split neighbours present, compound underscore
          token intact (A0 tokenizer).
  Gate 2  pointed vs stripped query → identical rowid sets on a pilot corpus,
          with pointed docs matching stripped queries (the recall point).

Run:  python3 -m unittest discover -s tests -v
"""

import sqlite3
import sys
import unittest
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import hebrew_normalize as hn  # noqa: E402

# Genesis 1:1 (pointed, logical order)
GEN1 = "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ"

BATTERY = [
    GEN1,
    "ארץ־ישראל היא מדינה",          # maqaf compound
    "דו-ברכה ודו״ח ודו\"ח",          # hyphen + gershayim + ASCII quote (A1)
    "ג׳יין אכלה ג'ינג׳ר",            # geresh loan-phonemes + ASCII geresh
    "װיל איז דאָס",                 # Yiddish digraphs + remaining vowels
    "עם ספר וגן־בהם",                # final forms + maqaf
    "שלום world 2020-2024",          # mixed script + digits
]


def _no_mn_me_cf(s: str) -> bool:
    return not any(
        unicodedata.category(c) in ("Mn", "Me", "Cf") for c in s
    )


class TestPipelineCore(unittest.TestCase):
    def test_gen1_is_seven_consonantal_tokens(self):
        out = hn.normalize_hebrew_index(GEN1)
        tokens = out.split()
        self.assertEqual(7, len(tokens), f"expected 7 tokens, got {tokens}")
        for tok in tokens:
            self.assertRegex(tok, r"^[\u05d0-\u05ea]+$", f"non-Hebrew token {tok!r}")

    def test_no_mn_me_cf_remain(self):
        for src in BATTERY:
            out = hn.normalize_hebrew_index(src, source_file="test")
            self.assertTrue(
                _no_mn_me_cf(out),
                f"Mn/Me/Cf survived for {src!r}: "
                f"{[(c, unicodedata.category(c)) for c in out if unicodedata.category(c) in ('Mn','Me','Cf')]}",
            )

    def test_maqaf_splits(self):
        self.assertEqual("ארצ ישראל", hn.normalize_hebrew_index("ארץ־ישראל"))

    def test_ascii_hyphen_between_hebrew_splits(self):
        self.assertEqual("דו ברכה", hn.normalize_hebrew_index("דו-ברכה"))

    def test_hyphen_between_digits_preserved(self):
        self.assertEqual("2020-2024", hn.normalize_hebrew_index("2020-2024"))

    def test_idempotent(self):
        for src in BATTERY:
            once = hn.normalize_hebrew_index(src)
            twice = hn.normalize_hebrew_index(once)
            self.assertEqual(once, twice, f"not idempotent for {src!r}")

    def test_nfc_order_convergence(self):
        # dagesh-then-shva vs shva-then-dagesh (non-canonical mark order)
        raw = "ב" + chr(0x05BC) + chr(0x05B0)
        canonical = unicodedata.normalize("NFC", raw)
        self.assertEqual(
            hn.normalize_hebrew_index(raw),
            hn.normalize_hebrew_index(canonical),
        )

    def test_final_form_fold(self):
        final_mem = "ע" + "\u05dd"   # ם
        reg_mem = "ע" + "\u05de"     # מ
        self.assertNotEqual(final_mem, reg_mem)
        self.assertEqual(
            hn.normalize_hebrew_index(final_mem),
            hn.normalize_hebrew_index(reg_mem),
        )

    def test_geresh_family(self):
        self.assertEqual("גיינ", hn.normalize_hebrew_index("ג׳יין"))
        self.assertEqual("דוח", hn.normalize_hebrew_index("דו״ח"))

    def test_a1_ascii_quotes_between_hebrew_only(self):
        self.assertEqual("דוח", hn.normalize_hebrew_index('דו"ח'))
        self.assertEqual("גינ", hn.normalize_hebrew_index("ג'ין"))
        # Latin context untouched (quote not between Hebrew letters)
        self.assertEqual("don't", hn.normalize_hebrew_index("Don't"))

    def test_yiddish_digraphs(self):
        self.assertEqual("וויל", hn.normalize_hebrew_index("װיל"))

    def test_query_is_index_function(self):
        self.assertIs(hn.normalize_hebrew_query, hn.normalize_hebrew_index)

    def test_violation_checker_catches_injection(self):
        bad = hn._violations("א" + chr(0x05B0))  # shva where none may survive
        self.assertTrue(any(kind == "hebrew-mark" for kind, _, _ in bad))
        self.assertEqual([], hn._violations(hn.normalize_hebrew_index(GEN1)))


class TestColumns(unittest.TestCase):
    def test_display_keeps_niqqud_nfc_only(self):
        disp = hn.normalize_display(GEN1)
        self.assertFalse(_no_mn_me_cf(disp), "display must keep points")
        self.assertEqual(unicodedata.normalize("NFC", GEN1), disp)

    def test_exact_keeps_vowels_drops_cantillation(self):
        pointed_with_tam = "בְּ" + chr(0x0591)  # + silluq/etnahta-class mark
        out = hn.normalize_text_exact(pointed_with_tam)
        self.assertNotIn(chr(0x0591), out)
        self.assertIn(chr(0x05B0), out, "shva must survive text_exact")
        self.assertIn(chr(0x05BC), out, "dagesh must survive text_exact")

    def test_compound_uses_underscore(self):
        self.assertEqual("ארצ_ישראל", hn.normalize_hebrew_compound("ארץ־ישראל"))
        # hyphen fold is space in BOTH columns (brief EXCEPT clause = maqaf only)
        self.assertEqual("דו ברכה", hn.normalize_hebrew_compound("דו-ברכה"))

    def test_normalize_row_shape(self):
        row = hn.normalize_row(GEN1, source_file="gen1")
        self.assertEqual(
            {"text_display", "text_index", "text_compound", "text_exact",
             "pipeline_version"},
            set(row),
        )
        self.assertEqual(hn.PIPELINE_VERSION, row["pipeline_version"])
        self.assertEqual(hn.normalize_hebrew_index(GEN1), row["text_index"])


class TestGate1Fts5Vocab(unittest.TestCase):
    """Gate 1: fts5vocab on a dev sample (brief §5.1)."""

    @classmethod
    def setUpClass(cls):
        con = sqlite3.connect(":memory:")
        con.execute(
            "CREATE VIRTUAL TABLE dev USING fts5(t_index, t_compound, "
            f'tokenize="{hn.FTS5_TOKENIZE_PRIMARY}")'
        )
        con.execute(
            "CREATE VIRTUAL TABLE devc USING fts5(t, "
            f'tokenize="{hn.FTS5_TOKENIZE_COMPOUND}")'
        )
        con.execute(
            "INSERT INTO dev(t_index, t_compound) VALUES (?, ?)",
            (hn.normalize_hebrew_index(GEN1), hn.normalize_hebrew_compound(GEN1)),
        )
        con.execute(
            "INSERT INTO dev(t_index, t_compound) VALUES (?, ?)",
            (
                hn.normalize_hebrew_index("ארץ־ישראל"),
                hn.normalize_hebrew_compound("ארץ־ישראל"),
            ),
        )
        con.execute(
            "INSERT INTO devc VALUES (?)",
            (hn.normalize_hebrew_compound("ארץ־ישראל"),),
        )
        con.execute("CREATE VIRTUAL TABLE vocab USING fts5vocab(dev, 'row')")
        con.execute("CREATE VIRTUAL TABLE vocabc USING fts5vocab(devc, 'row')")
        cls.terms = {r[0] for r in con.execute("SELECT term FROM vocab")}
        cls.compound_terms = {r[0] for r in con.execute("SELECT term FROM vocabc")}
        cls.gen1_tokens = set(hn.normalize_hebrew_index(GEN1).split())
        con.close()

    def test_gen1_terms_present(self):
        self.assertTrue(
            self.gen1_tokens <= self.terms,
            f"missing: {self.gen1_tokens - self.terms}",
        )

    def test_gen1_distinct_terms_about_seven(self):
        # 7 words, all distinct in GEN1 → 7 vocab terms
        self.assertEqual(7, len(self.gen1_tokens))
        self.assertEqual(7, len(self.gen1_tokens & self.terms))

    def test_zero_terms_in_diacritic_range(self):
        offenders = [
            t for t in self.terms
            if any(0x0591 <= ord(c) <= 0x05C7 for c in t)
        ]
        self.assertEqual([], offenders)

    def test_no_mn_me_cf_in_any_term(self):
        offenders = [t for t in self.terms if not _no_mn_me_cf(t)]
        self.assertEqual([], offenders)

    def test_maqaf_split_neighbours_present(self):
        self.assertIn("ארצ", self.terms)   # final tsadi folded
        self.assertIn("ישראל", self.terms)
        self.assertNotIn("ארץ־ישראל", self.terms)

    def test_compound_underscore_single_token_a0(self):
        # A0: underscore must be a declared tokenchar or this shatters
        self.assertIn("ארצ_ישראל", self.compound_terms)


class TestGate2QuerySymmetry(unittest.TestCase):
    """Gate 2: pointed vs stripped queries → identical sets (brief §5.2)."""

    @classmethod
    def setUpClass(cls):
        cls.con = sqlite3.connect(":memory:")
        cls.con.execute(
            "CREATE VIRTUAL TABLE pilot USING fts5(doc, "
            f'tokenize="{hn.FTS5_TOKENIZE_PRIMARY}")'
        )
        docs = [
            ("pointed", GEN1),
            ("stripped", hn.normalize_hebrew_index(GEN1)),  # indexed pre-stripped
            ("related", "בראשית ברא אלוהים"),
            ("other", "ארץ ישראל"),
        ]
        for label, text in docs:
            cls.con.execute(
                "INSERT INTO pilot(doc) VALUES (?)",
                (f"{label}\t{hn.normalize_hebrew_index(text, source_file=label)}",),
            )

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    @classmethod
    def _match_rowids(cls, raw_query: str):
        q = hn.normalize_hebrew_query(raw_query, source_file="query")
        expr = '"' + '" AND "'.join(q.split()) + '"'
        return {
            r[0]
            for r in cls.con.execute("SELECT rowid FROM pilot WHERE pilot MATCH ?", (expr,))
        }

    def test_pointed_and_stripped_queries_identical(self):
        pointed = self._match_rowids(GEN1)
        stripped = self._match_rowids(hn.normalize_hebrew_index(GEN1))
        self.assertEqual(pointed, stripped)
        self.assertTrue(pointed, "query must match something")

    def test_pointed_query_reaches_pointed_and_stripped_docs(self):
        hits = self._match_rowids(GEN1)
        self.assertEqual({1, 2}, hits, "pointed doc AND its stripped twin must both hit")


if __name__ == "__main__":
    unittest.main()
