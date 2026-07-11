# 🔱 omega-vetala — Local Pattern-Based Fallback Provider
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ LOCAL-FALLBACK
#
# [id-soft: doom-1993] High-Bit Trick — detect obfuscation by structural
#   analysis rather than exact matching, similar to how Doom used high-bit
#   patterns to identify entity types.
#
# ⚠️  NO STATIC SLUR LISTS — This provider uses ONLY structural pattern
#     analysis and obfuscation detection. It does NOT contain any hardcoded
#     lists of offensive words or slurs.
#
# Strategy: detect *how* text might be obfuscated, not *what* it says.
# High obfuscation scores increase the probability that a user is trying
# to bypass a moderation filter, which itself is a flag.

from __future__ import annotations

import logging
import re
import string
import unicodedata
from typing import Any

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
)

logger = logging.getLogger(__name__)

# Unicode ranges known for homoglyph-heavy blocks (e.g. Cyrillic,
# Latin Extended, Mathematical Alphanumerics).
_HOMOGLYPH_RANGES: list[tuple[int, int]] = [
    (0x0370, 0x03FF),  # Greek and Coptic
    (0x0400, 0x04FF),  # Cyrillic
    (0x0500, 0x052F),  # Cyrillic Supplement
    (0x1D400, 0x1D7FF),  # Mathematical Alphanumerics
    (0x2100, 0x214F),  # Letterlike Symbols
    (0x2460, 0x24FF),  # Enclosed Alphanumerics
    (0x2C60, 0x2C7F),  # Latin Extended-C
    (0xA720, 0xA7FF),  # Latin Extended-D
    (0xAB30, 0xAB6F),  # Latin Extended-E
    (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
]

# Controls that are unusual in natural text
_SUSPICIOUS_CONTROL_RANGES: list[tuple[int, int]] = [
    (0x200B, 0x200F),  # Zero-width spaces, LTR/RTL marks
    (0x202A, 0x202E),  # Bidi overrides
    (0x2060, 0x2064),  # Word joiner, invisible operators
    (0xFE00, 0xFE0F),  # Variation selectors
]

# Leetspeak substitution map (single chars only).  Used exclusively for
# character-level normalisation scoring, NOT for expanding into slurs.
_LEETSPEAK_MAP: dict[str, str] = {
    "0": "o",
    "1": "i",
    "2": "z",
    "3": "e",
    "4": "a",
    "5": "s",
    "6": "g",
    "7": "t",
    "8": "b",
    "9": "g",
    "@": "a",
    "$": "s",
    "!": "i",
}


class LocalFallbackProvider(ModelProvider):
    """Last-resort pattern-analysis fallback provider.

    This provider uses **no static slur lists**.  It analyses the
    *structure* of the input to detect obfuscation techniques commonly
    employed to bypass automated filters.

    Obfuscation dimensions analysed:

    * **Homoglyph density** — characters from non-Latin blocks used
      to replace visually similar Latin letters.
    * **Leetspeak score** — numeric / symbol substitutions for letters.
    * **Character repetition** — excessive repeated characters.
    * **Control-character density** — zero-width spaces, bidi marks.
    * **Case variance** — unusual capitalisation patterns.
    * **Spacing anomalies** — excessive whitespace or missing spaces.
    * **Special-character ratio** — unusual punctuation density.

    High obfuscation → higher chance of intentional filter evasion →
    flagged at low-to-moderate confidence.

    Attributes:
        supports_offline: True — entirely local, no network required.
    """

    supports_offline: bool = True

    # Tunable thresholds
    _HOMOGLYPH_THRESHOLD: float = 0.15
    _LEETSPEAK_THRESHOLD: float = 0.20
    _REPEAT_THRESHOLD: float = 0.10
    _CONTROL_THRESHOLD: float = 0.05
    _SPECIAL_RATIO_THRESHOLD: float = 0.30
    _OBFUSCATION_FLAG_THRESHOLD: float = 0.4

    def __init__(self, obfuscation_threshold: float | None = None) -> None:
        """Initialise provider.

        Args:
            obfuscation_threshold: Override the default flag threshold
                (0.0–1.0).  Higher values make the provider less sensitive.
        """
        if obfuscation_threshold is not None:
            self._OBFUSCATION_FLAG_THRESHOLD = obfuscation_threshold

    # ------------------------------------------------------------------
    # Analysis dimensions
    # ------------------------------------------------------------------

    @staticmethod
    def _char_in_ranges(
        char: str, ranges: list[tuple[int, int]]
    ) -> bool:
        """Check if *char*'s codepoint falls within any of *ranges*."""
        code = ord(char)
        for lo, hi in ranges:
            if lo <= code <= hi:
                return True
        return False

    def _homoglyph_density(self, text: str) -> float:
        """Fraction of characters from homoglyph-heavy Unicode blocks."""
        if not text:
            return 0.0
        total = max(len([c for c in text if not c.isspace()]), 1)
        count = sum(
            1 for c in text if self._char_in_ranges(c, _HOMOGLYPH_RANGES)
        )
        return count / total

    def _leetspeak_score(self, text: str) -> float:
        """Fraction of characters that are leetspeak substitutions."""
        if not text:
            return 0.0
        letters = [c.lower() for c in text if c.isalnum()]
        if not letters:
            return 0.0
        sub_count = sum(1 for c in letters if c in _LEETSPEAK_MAP)
        return sub_count / len(letters)

    def _repetition_score(self, text: str) -> float:
        """Density of repeated characters (3+ consecutive identical chars)."""
        if len(text) < 4:
            return 0.0
        repeats = len(re.findall(r"(.)\1{2,}", text))
        return repeats / len(text)

    def _control_char_density(self, text: str) -> float:
        """Density of suspicious control / invisible characters."""
        if not text:
            return 0.0
        total = max(len(text), 1)
        count = sum(
            1 for c in text if self._char_in_ranges(c, _SUSPICIOUS_CONTROL_RANGES)
        )
        return count / total

    def _case_variance_score(self, text: str) -> float:
        """Unusual capitalisation patterns (e.g. aLtErNaTiNg case)."""
        letters = [c for c in text if c.isalpha()]
        if len(letters) < 4:
            return 0.0
        upper = sum(1 for c in letters if c.isupper())
        lower = sum(1 for c in letters if c.islower())
        # High variance = roughly equal upper/lower
        # (normal text is mostly lower or capitalised properly)
        ratio = upper / len(letters) if upper > 0 else 0.0
        # Score peaks when ratio ~ 0.5 (alternating case)
        return 1.0 - abs(ratio - 0.5) * 2.0

    def _spacing_anomaly_score(self, text: str) -> float:
        """Detect excessive whitespace or missing spaces."""
        if not text:
            return 0.0
        # Ratio of whitespace to total length
        ws_ratio = sum(1 for c in text if c.isspace()) / len(text)
        # Normal text has ~10–20% whitespace.  Much more is suspicious.
        if ws_ratio <= 0.3:
            return 0.0
        return min((ws_ratio - 0.3) / 0.5, 1.0)

    def _special_char_ratio(self, text: str) -> float:
        """Ratio of non-alphanumeric characters (excluding whitespace)."""
        if not text:
            return 0.0
        printable = [c for c in text if not c.isspace()]
        if not printable:
            return 0.0
        special = sum(
            1
            for c in printable
            if c not in string.ascii_letters and c not in string.digits
        )
        return special / len(printable)

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* using structural pattern analysis only.

        Args:
            text: Content to analyse.

        Returns:
            :class:`ModerationResult` with obfuscation dimension scores
            and an overall flag based on aggregate obfuscation density.
        """
        if not text.strip():
            return ModerationResult(provider_name="local_fallback")

        # Compute each dimension
        hg = self._homoglyph_density(text)
        lt = self._leetspeak_score(text)
        rp = self._repetition_score(text)
        cc = self._control_char_density(text)
        cv = self._case_variance_score(text)
        sa = self._spacing_anomaly_score(text)
        sp = self._special_char_ratio(text)

        # Build category scores
        categories: dict[str, float] = {
            "homoglyph_density": round(hg, 4),
            "leetspeak_score": round(lt, 4),
            "repetition_score": round(rp, 4),
            "control_char_density": round(cc, 4),
            "case_variance": round(cv, 4),
            "spacing_anomaly": round(sa, 4),
            "special_char_ratio": round(sp, 4),
        }

        # Overall obfuscation score — weighted combination
        weights = {
            "homoglyph": 0.25,
            "leetspeak": 0.20,
            "repetition": 0.10,
            "control": 0.15,
            "case": 0.05,
            "spacing": 0.10,
            "special": 0.15,
        }

        obfuscation_score = (
            weights["homoglyph"] * hg
            + weights["leetspeak"] * lt
            + weights["repetition"] * rp
            + weights["control"] * cc
            + weights["case"] * cv
            + weights["spacing"] * sa
            + weights["special"] * sp
        )

        categories["obfuscation_score"] = round(obfuscation_score, 4)

        is_flagged = obfuscation_score >= self._OBFUSCATION_FLAG_THRESHOLD

        return ModerationResult(
            is_flagged=is_flagged,
            confidence=round(obfuscation_score, 4),
            categories=categories,
            provider_name="local_fallback",
        )
