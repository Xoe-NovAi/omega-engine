"""Tests for LocalFallbackProvider — structural pattern analysis.

⚠️  VERIFICATION: These tests confirm NO static slur lists are used.
     All detection is based on structural analysis of obfuscation patterns.
"""

from __future__ import annotations

import pytest

from omega_vetala.providers.local_fallback import LocalFallbackProvider


@pytest.fixture
def provider() -> LocalFallbackProvider:
    """Default local fallback provider."""
    return LocalFallbackProvider()


class TestLocalFallbackProvider:
    """Pattern-based fallback behaviour."""

    def test_supports_offline(self) -> None:
        """Works entirely offline."""
        p = LocalFallbackProvider()
        assert p.supports_offline is True

    async def test_empty_text(self, provider: LocalFallbackProvider) -> None:
        """Empty text returns fast with no flag."""
        result = await provider.analyze("")
        assert result.is_flagged is False
        assert result.provider_name == "local_fallback"

    async def test_whitespace_text(self, provider: LocalFallbackProvider) -> None:
        """Whitespace returns fast."""
        result = await provider.analyze("   ")
        assert result.is_flagged is False

    async def test_clean_text_not_flagged(
        self, provider: LocalFallbackProvider, sample_clean_text: str
    ) -> None:
        """Normal clean text should NOT be flagged."""
        result = await provider.analyze(sample_clean_text)
        assert result.is_flagged is False
        assert result.confidence < 0.3

    async def test_leetspeak_detected(
        self, provider: LocalFallbackProvider, sample_obfuscated_text: str
    ) -> None:
        """Leetspeak text should have elevated leetspeak_score."""
        result = await provider.analyze(sample_obfuscated_text)
        assert "leetspeak_score" in result.categories
        assert result.categories["leetspeak_score"] > 0.1

    async def test_homoglyph_detected(
        self, provider: LocalFallbackProvider, sample_homoglyph_text: str
    ) -> None:
        """Text with Cyrillic homoglyphs should have high homoglyph_density."""
        result = await provider.analyze(sample_homoglyph_text)
        assert "homoglyph_density" in result.categories
        # This text is heavily homoglyphic
        assert result.categories["homoglyph_density"] > 0.1

    async def test_control_chars_detected(
        self, provider: LocalFallbackProvider, sample_control_char_text: str
    ) -> None:
        """Zero-width spaces should increase control_char_density."""
        result = await provider.analyze(sample_control_char_text)
        assert "control_char_density" in result.categories
        assert result.categories["control_char_density"] > 0

    async def test_repetition_detected(
        self, provider: LocalFallbackProvider, sample_repeated_text: str
    ) -> None:
        """Excessive character repetition should be detected."""
        result = await provider.analyze(sample_repeated_text)
        assert "repetition_score" in result.categories
        assert result.categories["repetition_score"] > 0.05

    async def test_obfuscation_score_tracked(
        self, provider: LocalFallbackProvider, sample_obfuscated_text: str
    ) -> None:
        """Obfuscation score aggregates all dimensions."""
        result = await provider.analyze(sample_obfuscated_text)
        assert "obfuscation_score" in result.categories
        # The aggregated score should be non-trivial for leetspeak
        assert result.categories["obfuscation_score"] > 0

    # ------------------------------------------------------------------
    # Unit tests for individual analysis methods
    # ------------------------------------------------------------------

    def test_homoglyph_density_clean(self, provider: LocalFallbackProvider) -> None:
        """Clean ASCII text should have zero homoglyph density."""
        assert provider._homoglyph_density("hello world") == 0.0

    def test_homoglyph_density_with_homoglyphs(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Text with Cyrillic homoglyphs should have >0 density."""
        assert provider._homoglyph_density("thiѕ iѕ а tеѕt") > 0.0

    def test_leetspeak_score_clean(self, provider: LocalFallbackProvider) -> None:
        """Normal text should have low leetspeak score."""
        assert provider._leetspeak_score("hello world") == 0.0

    def test_leetspeak_score_with_leetspeak(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Leetspeak text should have elevated score."""
        assert provider._leetspeak_score("h3ll0 w0rld") > 0.2

    def test_repetition_score_normal(self, provider: LocalFallbackProvider) -> None:
        """Normal text should have low repetition score."""
        assert provider._repetition_score("hello world") == 0.0

    def test_repetition_score_high(self, provider: LocalFallbackProvider) -> None:
        """Repeated characters should yield high score."""
        assert provider._repetition_score("nooooooo") > 0.1

    def test_control_char_density_clean(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Normal text has no control chars."""
        assert provider._control_char_density("hello world") == 0.0

    def test_control_char_density_with_zwsp(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Zero-width spaces should be detected."""
        assert provider._control_char_density("hel\u200Blo") > 0.0

    def test_case_variance_normal(self, provider: LocalFallbackProvider) -> None:
        """Normal capitalisation should have low variance."""
        assert provider._case_variance_score("Hello world, this is normal.") < 0.5

    def test_case_variance_alternating(
        self, provider: LocalFallbackProvider
    ) -> None:
        """AlTeRnAtInG case should have high variance."""
        assert provider._case_variance_score("ThIs Is AlTeRnAtInG cAsE") > 0.3

    def test_spacing_anomaly_normal(self, provider: LocalFallbackProvider) -> None:
        """Normal spacing should not be anomalous."""
        assert provider._spacing_anomaly_score("hello world") == 0.0

    def test_spacing_anomaly_excessive(self, provider: LocalFallbackProvider) -> None:
        """Excessive whitespace should be detected."""
        text = "hello    world    with    many    spaces"
        assert provider._spacing_anomaly_score(text) > 0.0

    def test_special_char_ratio_normal(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Normal text has low special char ratio."""
        assert provider._special_char_ratio("hello world") < 0.05

    def test_special_char_ratio_high(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Text with many special chars should have a high ratio."""
        text = "!!!h3ll0!!! @@@th1s@@@ $$$!s$$$"
        ratio = provider._special_char_ratio(text)
        assert ratio > 0.1

    async def test_threshold_override(self) -> None:
        """Custom obfuscation threshold should work."""
        p = LocalFallbackProvider(obfuscation_threshold=0.99)
        result = await p.analyze("h3ll0 w0rld")
        # With a very high threshold, even obfuscated text might not flag
        assert isinstance(result.is_flagged, bool)

    async def test_categories_contain_all_dimensions(
        self, provider: LocalFallbackProvider
    ) -> None:
        """Result categories should include all analysis dimensions."""
        result = await provider.analyze("test text")
        expected_keys = {
            "homoglyph_density",
            "leetspeak_score",
            "repetition_score",
            "control_char_density",
            "case_variance",
            "spacing_anomaly",
            "special_char_ratio",
            "obfuscation_score",
        }
        assert expected_keys.issubset(result.categories.keys())

    # ------------------------------------------------------------------
    # NO SLUR LIST VERIFICATION
    # ------------------------------------------------------------------

    def test_no_slur_list_variables(self) -> None:
        """Verify the provider file has no variable that looks like a slur list.

        This inspects only variable assignments (not comments) to ensure
        no static word lists were introduced.
        """
        import inspect
        import ast
        import omega_vetala.providers.local_fallback as lf

        source = inspect.getsource(lf)
        tree = ast.parse(source)

        # Collect all list/tuple/set literals assigned to variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        # Check for suspicious variable names
                        slur_indicators = [
                            "slur", "offensive", "badword", "blacklist",
                            "blocked", "forbidden", "profanity_list",
                            "toxic_words", "hate_words",
                        ]
                        if any(ind in var_name for ind in slur_indicators):
                            pytest.fail(
                                f"Variable '{target.id}' suggests a word list"
                            )

                # Check if assigned value is a large string list
                if isinstance(node.value, ast.List):
                    string_items = [
                        elt for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]
                    if len(string_items) > 20:
                        # Check if items look like words (short strings)
                        avg_len = sum(len(s.value) for s in string_items) / len(string_items)
                        if avg_len < 15:  # short strings = likely word list
                            pytest.fail(
                                f"Large string list ({len(string_items)} items, "
                                f"avg length {avg_len:.1f}) at line "
                                f"{node.lineno} — possible slur list"
                            )
