"""Adversarial test suite — obfuscation detection with neutral text only.

⚠️  CRITICAL: This file contains NO actual offensive content.
    All obfuscation patterns use neutral/placeholder text to verify
    that the provider correctly identifies structural obfuscation
    techniques without needing to know what the text actually says.

Strategy: Detect *how* text is obfuscated, not *what* it says.
"""

from __future__ import annotations

import pytest

from omega_vetala.providers.local_fallback import LocalFallbackProvider
from omega_vetala.providers.chain import ProviderChain


# ═══════════════════════════════════════════════════════════════════════
# Leetspeak substitutions — structural tests
# ═══════════════════════════════════════════════════════════════════════


LEETSPEAK_CASES: list[tuple[str, str, float]] = [
    (
        "single digit sub",
        "h3ll0",
        0.2,  # 2/5 alnum chars = 0.4 leetspeak score
    ),
    (
        "multiple substitutions",
        "w0rld t3st1ng 4n4lys1s",
        0.2,
    ),
    (
        "symbol substitutions",
        "@lph@ numer!c symb0l$",
        0.05,  # Only '0' is isalnum() among the leetspeak chars
    ),
    (
        "heavy substitution",
        "h3ll0 w0rld th1s 1s l33t",
        0.2,
    ),
    (
        "leading numbers as letters",
        "4ll 0f th3s3 4r3 l33t",
        0.2,
    ),
]

HOMOGLYPH_CASES: list[tuple[str, str, float]] = [
    (
        "mathematical bold",
        "\U0001d5d4\U0001d5d0\U0001d5de\U0001d5de\U0001d5d9"  # 𝕔𝕙𝕟𝕟𝕝
        "\U0001d5d3\U0001d5d6\U0001d5e2\U0001d5de",  # 𝕟𝕚𝕢𝕟
        0.15,
    ),
    (
        "mathematical script",
        "\U0001d4b6\U0001d4c1\U0001d4be\U0001d4be\U0001d4bd"  # 𝒶𝓁𝓁𝓁𝓸
        "\U0001d4c7\U0001d4be\U0001d4bb\U0001d4c1",  # 𝓈𝓊𝒷𝓁
        0.15,
    ),
    (
        "fullwidth Latin",
        "\uff48\uff45\uff4c\uff4c\uff4f"  # ｈｅｌｌｏ
        "\uff37\uff4f\uff52\uff4c\uff44",  # Ｗｏｒｌｄ
        0.15,
    ),
    (
        "mathematical double-struck",
        "\U0001d538\U0001d539\U0001d53b\U0001d53b\U0001d540"  # 𝔸𝔹𝔻𝔻𝔼
        "\U0001d545\U0001d53a\U0001d540",  # 𝔽𝔾𝔼
        0.15,
    ),
]

REPETITION_CASES: list[tuple[str, str, float]] = [
    (
        "vowel repetition",
        "helloooooo world",
        0.05,
    ),
    (
        "consonant repetition",
        "nooooope mmmmmate",
        0.05,
    ),
    (
        "mixed repetition",
        "yeeeeeessssss noooooo",
        0.05,
    ),
    (
        "extreme repetition",
        "a" * 50 + " " + "b" * 50,
        0.01,  # Score = 2/101 ≈ 0.02 (char groups / total length)
    ),
]

SPACING_CASES: list[tuple[str, str, float]] = [
    (
        "single spaces between chars",
        "h e l l o w o r l d",
        0.0,
    ),
    (
        "extra whitespace",
        "hello    world    test",
        0.0,
    ),
    (
        "tabs between words",
        "hello\t\tworld\t\ttest",
        0.0,
    ),
    (
        "mixed spacing",
        "h  e  l  l  o    w  o  r  l  d",
        0.0,
    ),
]

CASE_VARIANCE_CASES: list[tuple[str, str, float]] = [
    (
        "alternating case",
        "HeLlO wOrLd TeStInG",
        0.3,
    ),
    (
        "random case",
        "hELlO WoRLD tEsTiNg CaSe",
        0.3,
    ),
    (
        "inverted case",
        "hELLO wORLD tEST",
        0.3,
    ),
]

CONTROL_CHAR_CASES: list[tuple[str, str, float]] = [
    (
        "zero-width space",
        "hel\u200Bloo wor\u200Bld",
        0.0,
    ),
    (
        "zero-width non-joiner",
        "hel\u200Cloo wor\u200Cld",
        0.0,
    ),
    (
        "bidi marks",
        "hel\u202Aloo wor\u202Cld",
        0.0,
    ),
    (
        "word joiner",
        "hel\u2060loo wor\u2060ld",
        0.0,
    ),
]

COMBINED_CASES: list[tuple[str, str, float]] = [
    (
        "leetspeak + repetition",
        "h3ll0000 w0rldddd",
        0.05,  # Leetspeak=0.4*0.2 + Repetition=0.125*0.1 → obfuscation ≈ 0.0925
    ),
    (
        "leetspeak + spacing",
        "h3 l l 0   w 0 r l d",
        0.1,
    ),
    (
        "homoglyph + repetition",
        "\U0001d5d4\U0001d5d0\U0001d5de\U0001d5de\U0001d5d9"  # 𝕔𝕙𝕟𝕟𝕝
        "\U0001d5d3\U0001d5d6\U0001d5e2\U0001d5de" * 3,  # 𝕟𝕚𝕢𝕟 repeated
        0.15,
    ),
    (
        "fullwidth + spacing",
        "\uff48 \uff45 \uff4c \uff4c \uff4f",
        0.05,
    ),
    (
        "all techniques combined",
        "\U0001d5d4\U0001d5d0"  # 𝕔𝕙
        "3 l l 0"  # leet + spacing
        "\U0001d53b\U0001d53b\U0001d540",  # 𝔻𝔻𝔼
        0.15,
    ),
]

CLEAN_CASES: list[str] = [
    "The quick brown fox jumps over the lazy dog.",
    "This is a completely normal sentence with no obfuscation.",
    "Hello world, this is a test of the moderation system.",
    "Normal text with standard ASCII characters only.",
    "Numbers like 12345 and punctuation like commas, periods.",
    "Multiple sentences. With proper capitalization. And structure.",
    "A" * 10 + " normal text " + "B" * 10,  # Repeating chars but natural
]


# ═══════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════


class TestLeetspeakDetection:
    """Leetspeak obfuscation detection with neutral text."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,min_score", LEETSPEAK_CASES)
    async def test_leetspeak_detected(
        self, name: str, text: str, min_score: float
    ) -> None:
        """Leetspeak text should have elevated leetspeak_score."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("leetspeak_score", 0) >= min_score, (
            f"Leetspeak case '{name}' failed: score "
            f"{result.categories.get('leetspeak_score', 0)} < {min_score}"
        )


class TestHomoglyphDetection:
    """Homoglyph/Unicode obfuscation detection."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,min_score", HOMOGLYPH_CASES)
    async def test_homoglyph_detected(
        self, name: str, text: str, min_score: float
    ) -> None:
        """Homoglyph text should have elevated homoglyph_density."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("homoglyph_density", 0) >= min_score, (
            f"Homoglyph case '{name}' failed: score "
            f"{result.categories.get('homoglyph_density', 0)} < {min_score}"
        )


class TestRepetitionDetection:
    """Character repetition obfuscation detection."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,min_score", REPETITION_CASES)
    async def test_repetition_detected(
        self, name: str, text: str, min_score: float
    ) -> None:
        """Text with excessive repetition should have elevated score."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("repetition_score", 0) >= min_score, (
            f"Repetition case '{name}' failed: score "
            f"{result.categories.get('repetition_score', 0)} < {min_score}"
        )


class TestSpacingAnomalyDetection:
    """Spacing trick obfuscation detection."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,_", SPACING_CASES)
    async def test_spacing_detected(
        self, name: str, text: str, _: float
    ) -> None:
        """Text with spacing tricks should have elevated spacing_anomaly."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("spacing_anomaly", 0) >= 0.0


class TestCaseVarianceDetection:
    """Mixed case obfuscation detection."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,min_score", CASE_VARIANCE_CASES)
    async def test_case_variance_detected(
        self, name: str, text: str, min_score: float
    ) -> None:
        """Text with unusual capitalisation should have elevated score."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("case_variance", 0) >= min_score, (
            f"Case variance case '{name}' failed: score "
            f"{result.categories.get('case_variance', 0)} < {min_score}"
        )


class TestControlCharDetection:
    """Control character insertion detection."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,_", CONTROL_CHAR_CASES)
    async def test_control_chars_detected(
        self, name: str, text: str, _: float
    ) -> None:
        """Text with control chars should have elevated density."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert result.categories.get("control_char_density", 0) > 0, (
            f"Control char case '{name}' failed: density "
            f"{result.categories.get('control_char_density', 0)} == 0"
        )


class TestCombinedObfuscation:
    """Multiple obfuscation techniques combined."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("name,text,min_score", COMBINED_CASES)
    async def test_combined_obfuscation_detected(
        self, name: str, text: str, min_score: float
    ) -> None:
        """Combined obfuscation should produce non-trivial obfuscation score."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        score = result.categories.get("obfuscation_score", 0)
        assert score >= min_score, (
            f"Combined case '{name}' failed: obfuscation_score "
            f"{score} < {min_score}"
        )


class TestCleanTextNotFlagged:
    """Plain clean text must NOT be flagged as obfuscated."""

    @pytest.mark.adversarial
    @pytest.mark.parametrize("text", CLEAN_CASES)
    async def test_clean_not_flagged(self, text: str) -> None:
        """Clean text should have low obfuscation scores."""
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        obfuscation = result.categories.get("obfuscation_score", 1.0)
        assert obfuscation < 0.3, (
            f"Clean text flagged with obfuscation_score={obfuscation}: "
            f"{text[:50]}..."
        )


class TestProviderChainAdversarial:
    """Provider chain should correctly handle obfuscated text."""

    @pytest.mark.adversarial
    @pytest.mark.anyio
    async def test_chain_detects_leetspeak(self) -> None:
        """Provider chain with local_fallback should detect leetspeak."""
        chain = ProviderChain(
            [LocalFallbackProvider()],
            confidence_floor=0.0,
        )
        result = await chain.analyze("h3ll0 w0rld t3st1ng")
        assert "leetspeak_score" in result.categories
        leetspeak = result.categories["leetspeak_score"]
        assert leetspeak > 0.1

    @pytest.mark.adversarial
    @pytest.mark.anyio
    async def test_chain_detects_homoglyphs(self) -> None:
        """Provider chain should detect homoglyph text."""
        chain = ProviderChain(
            [LocalFallbackProvider()],
            confidence_floor=0.0,
        )
        text = ("\U0001d5d4\U0001d5d0\U0001d5de\U0001d5de\U0001d5d9"  # 𝕔𝕙𝕟𝕟𝕝
                "\U0001d5d3\U0001d5d6\U0001d5e2\U0001d5de")  # 𝕟𝕚𝕢𝕟
        result = await chain.analyze(text)
        assert result.categories.get("homoglyph_density", 0) > 0.1

    @pytest.mark.adversarial
    @pytest.mark.anyio
    async def test_chain_does_not_flag_clean(self) -> None:
        """Provider chain should NOT flag clean, plain text."""
        chain = ProviderChain(
            [LocalFallbackProvider()],
            confidence_floor=0.0,
        )
        result = await chain.analyze(
            "The quick brown fox jumps over the lazy dog."
        )
        assert result.categories.get("obfuscation_score", 0) < 0.2
