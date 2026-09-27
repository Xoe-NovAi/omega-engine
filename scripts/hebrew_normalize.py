#!/usr/bin/env python3
"""Hebrew normalization for FTS5 index and query paths (R1 / P4.8).

Implements the frozen pipeline of
  docs/research/R1_HEBREW_NORMALIZATION_BRIEF.md  §2 (steps 0–11)
with the pre-execution addenda of
  docs/research/R1_PREEXEC_GNOSIS_20260925.md:
    A0  compound column must declare tokenchars '_' (underscore is NOT a
        default unicode61 tokenchar on SQLite 3.46.1 — measured)
    A1  ASCII ' and " are geresh-family marks when they sit between two
        Hebrew letters (Latin-keyboard typing: דו"ח → דוח)
    A3  text_exact = "steps 0–4 only" (vowels + dagesh survive; cantillation
        and step-4 specials are removed)

Column variants (brief §3):
  text_display    NFC(input)                       byte-faithful display form
  text_index      normalize_hebrew_index(input)    FTS5 + embedding input
  text_compound   same pipeline, maqaf → '_'       exact-compound backstop
  text_exact      steps 0–4 only                   pointed, cantillation-free

FTS5 DDL (verified on this machine, SQLite 3.46.1):
  primary  table: tokenize = "unicode61"
  compound table: tokenize = "unicode61 tokenchars '_'"     # A0

Pipeline version tag for indexed rows (brief §6): PIPELINE_VERSION.
This module is sync and stdlib-only (CODE_QUALITY §1): no asyncio, no torch.
"""

import logging
import re
import unicodedata

PIPELINE_VERSION = "hebrew-norm-v1"

log = logging.getLogger(__name__)

# --- codepoint sets ---------------------------------------------------------
# Step 3: cantillation U+0591–U+05AF (sof-pasuq U+05C3 arrives via step 4).
_CANTILLATION = "".join(chr(c) for c in range(0x0591, 0x05B0))

# Step 4: punctuation/ornaments + invisible joiners (maqaf U+05BE NOT here:
# it is converted in step 7).
_SPECIALS = "".join(
    map(
        chr,
        (0x05C3, 0x05C0, 0x05C6, 0x05C4, 0x05C5, 0x05BD, 0x05BF, 0xFB1E,
         0x034F, 0x200C, 0x200D),
    )
)

# Step 5: vowels/modifiers (05B0–05BB), dagesh 05BC, shin/sin dots 05C1/05C2,
# 05C7. Accepted merges: שׁ/שׂ → ש, בּ/ב (precision backstop = text_exact).
_VOWELS = "".join(
    map(chr, list(range(0x05B0, 0x05BC)) + [0x05BC, 0x05C1, 0x05C2, 0x05C7])
)

# Steps 3+4+5 are pure deletions, so they commute — one translate table.
# Excludes 05BE (maqaf) and 05F3/05F4 (geresh family, step 6).
_DELETE_345 = str.maketrans("", "", _CANTILLATION + _SPECIALS + _VOWELS)

# Step 6: geresh U+05F3 / gershayim U+05F4 are deleted unconditionally —
# loan-phoneme (ג׳) and abbreviation/gematria (דו״ח) skeletons are both the
# bare letters; unicode61 would otherwise SPLIT דו״ח into דו + ח.
_GERESH_FAMILY = str.maketrans("", "", "\u05f3\u05f4")  # ׳ ״

# Step 7: hyphen-likes that may stand in for a maqaf in online writing
# (the Hebrew keyboard has no maqaf): U+002D and U+2010–U+2015.
_HYPHEN_BETWEEN_HEBREW = re.compile(
    r"(?<=[\u05d0-\u05ea])[\u002d\u2010-\u2015]+(?=[\u05d0-\u05ea])"
)

_HEBREW_RE = re.compile(r"[\u05d0-\u05ea]")  # א–ת incl. finals

# Step 8: Yiddish digraphs → Hebrew-letter equivalents.
_DIGRAPHS = str.maketrans({"\u05f0": "וו", "\u05f1": "וי", "\u05f2": "יי"})  # װ ױ ײ

# Step 9: final forms → regular forms (OCR-recall default, brief §2.9).
_FINALS = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})

# Step 10: ASCII-lowercase only (Hebrew has no case).
_ASCII_LOWER = str.maketrans({c: c + 32 for c in range(ord("A"), ord("Z") + 1)})

# FTS5 tokenizer specs, verified against SQLite 3.46.1 (A0).
FTS5_TOKENIZE_PRIMARY = "unicode61"
FTS5_TOKENIZE_COMPOUND = "unicode61 tokenchars '_'"


# --- helpers ----------------------------------------------------------------

def _strip_ascii_quotes_between_hebrew(text: str) -> str:
    """Addendum A1: drop ASCII ' and \" only between two Hebrew letters.

    Latin-keyboard `דו"ח` must become one token `דוח`; unicode61 treats the
    quote as a separator and would yield `דו` + `ח`. Outside Hebrew-letter
    context (don't, 'quoted') the quote is untouched.
    """
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        if (
            ch in ("'", '"')
            and 0 < i < n - 1
            and "\u05d0" <= text[i - 1] <= "\u05ea"
            and "\u05d0" <= text[i + 1] <= "\u05ea"
        ):
            continue
        out.append(ch)
    return "".join(out)


# Points text_exact is ALLOWED to keep (step 5 not applied there): vowels
# 05B0–05BB, dagesh 05BC, shin/sin dots 05C1/05C2, 05C7.
_EXACT_PRESERVED = frozenset(
    list(range(0x05B0, 0x05BC)) + [0x05BC, 0x05C1, 0x05C2, 0x05C7]
)


def _violations(text: str, preserved: frozenset = frozenset()) -> list:
    """Step 11: marks that survived normalization.

    Returns (kind, codepoint, char) tuples:
      ("hebrew-mark", …)  U+0591–U+05C7 residue NOT in the column's preserved
                          set — impossible by construction, so any hit is a
                          pipeline bug (asserts upstream).
      ("foreign-mark", …) other Mn/Me/Cf (e.g. Arabic harakat in mixed-script
                          content) — logged with source_file, not fatal.
    `preserved` = points this column intentionally keeps (text_exact).
    """
    bad = []
    for ch in text:
        cp = ord(ch)
        if cp in preserved:
            continue
        if 0x0591 <= cp <= 0x05C7:
            bad.append(("hebrew-mark", cp, ch))
        elif unicodedata.category(ch) in ("Mn", "Me", "Cf"):
            bad.append(("foreign-mark", cp, ch))
    return bad


def _check_violations(
    text: str, source_file: str, preserved: frozenset = frozenset()
) -> str:
    """Step 11 (brief §2): assert Hebrew residue, log the rest with src file."""
    bad = _violations(text, preserved)
    hebrew_residue = [v for v in bad if v[0] == "hebrew-mark"]
    if hebrew_residue:
        raise AssertionError(
            f"hebrew_normalize {PIPELINE_VERSION}: Hebrew combining marks "
            f"survived pipeline: {[(hex(c), repr(ch)) for _, c, ch in hebrew_residue]}"
            f" source_file={source_file!r}"
        )
    if bad:
        log.warning(
            "hebrew_normalize %s: residual foreign marks src=%r marks=%s",
            PIPELINE_VERSION,
            source_file,
            [(kind, hex(cp)) for kind, cp, _ in bad],
        )
    return text


# --- pipeline ---------------------------------------------------------------

def _pipeline(text: str, *, maqaf_replacement: str) -> str:
    """Brief §2 steps 0–10. maqaf_replacement: ' ' (primary) or '_' (compound).

    Step 7 hyphen-fold always yields a space (brief: the EXCEPT clause covers
    only the maqaf conversion — see gnosis A0 note).
    """
    # 0 logical-order input assumed (never reordered — documented contract)
    # 1 NFKC: presentation forms U+FBxx, widths, ligatures → canonical chars
    text = unicodedata.normalize("NFKC", text)
    # 2 NFC: canonical compose + ccc-sort (converges mark-order variants)
    text = unicodedata.normalize("NFC", text)
    # 3+4+5 delete cantillation / specials / vowels (commuting deletions)
    text = text.translate(_DELETE_345)
    # 6 geresh family (unconditional U+05F3/U+05F4 + ASCII A1)
    text = text.translate(_GERESH_FAMILY)
    text = _strip_ascii_quotes_between_hebrew(text)
    # 7 maqaf → replacement; hyphen-likes → space only Hebrew↔Hebrew
    text = text.replace("\u05be", maqaf_replacement)
    text = _HYPHEN_BETWEEN_HEBREW.sub(" ", text)
    # 8 Yiddish digraphs
    text = text.translate(_DIGRAPHS)
    # 9 final-form fold
    text = text.translate(_FINALS)
    # 10 collapse whitespace + ASCII-lowercase
    text = " ".join(text.split())
    text = text.translate(_ASCII_LOWER)
    return text


def normalize_display(s: str) -> str:
    """text_display: byte-faithful original, NFC only. Never searched."""
    return unicodedata.normalize("NFC", s)


def normalize_hebrew_index(s: str, source_file: str = "") -> str:
    """text_index: full pipeline (brief §1). Also the query path — identity
    with normalize_hebrew_query is asserted in tests (symmetric indexing)."""
    out = _pipeline(s, maqaf_replacement=" ")
    return _check_violations(out, source_file)


def normalize_hebrew_compound(s: str, source_file: str = "") -> str:
    """text_compound: full pipeline EXCEPT maqaf → underscore (brief §3).

    Pairs with FTS5_TOKENIZE_COMPOUND (A0) so `ארץ־ישראל` indexes as the
    single token `ארץ_ישראל` — the exact-compound precision backstop.
    """
    out = _pipeline(s, maqaf_replacement="_")
    return _check_violations(out, source_file)


def normalize_text_exact(s: str, source_file: str = "") -> str:
    """text_exact: steps 0–4 only (brief §6/A3) — NFKC, NFC, cantillation and
    step-4 specials removed; vowels, dagesh and maqaf PRESERVED."""
    out = unicodedata.normalize("NFKC", s)
    out = unicodedata.normalize("NFC", out)
    out = out.translate(str.maketrans("", "", _CANTILLATION + _SPECIALS))
    return _check_violations(out, source_file, preserved=_EXACT_PRESERVED)


# Brief §1: same function object — query normalization IS index normalization.
normalize_hebrew_query = normalize_hebrew_index


def normalize_row(s: str, source_file: str = "") -> dict:
    """All four columns for one source text (brief §3)."""
    return {
        "text_display": normalize_display(s),
        "text_index": normalize_hebrew_index(s, source_file),
        "text_compound": normalize_hebrew_compound(s, source_file),
        "text_exact": normalize_text_exact(s, source_file),
        "pipeline_version": PIPELINE_VERSION,
    }


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:] or ["בְּרֵאשִׁית בָּרָא אֱלֹהִים"]:
        src = arg
        row = normalize_row(src, source_file="<cli>")
        print(f"source   : {src}")
        print(f"display  : {row['text_display']}")
        print(f"index    : {row['text_index']}   ({len(row['text_index'].split())} tokens)")
        print(f"compound : {row['text_compound']}")
        print(f"exact    : {row['text_exact']}")
        print(f"version  : {row['pipeline_version']}")
