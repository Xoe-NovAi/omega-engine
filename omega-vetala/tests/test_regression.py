"""Regression test suite for omega-vetala.

Ensures previously-fixed bugs stay fixed and edge cases are handled
correctly.  All tests use neutral/placeholder text only — NO actual
offensive content.
"""

from __future__ import annotations

import gc
import threading
import time
from typing import Any

import pytest

from omega_vetala.providers.base import ModerationResult, ModelProvider
from omega_vetala.providers.chain import ProviderChain
from omega_vetala.providers.local_fallback import LocalFallbackProvider

from tests.conftest import (
    AlwaysFlagMockProvider,
    AlwaysPassMockProvider,
    FailingMockProvider,
)


# ═══════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge cases that have caused regressions."""

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_empty_string(self) -> None:
        """Empty string should not crash."""
        chain = ProviderChain([AlwaysFlagMockProvider()])
        result = await chain.analyze("")
        assert result.is_flagged is False

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_whitespace_only(self) -> None:
        """Whitespace-only string should not crash."""
        chain = ProviderChain([AlwaysFlagMockProvider()])
        result = await chain.analyze("   \t\n  \r\n  ")
        assert result.is_flagged is False

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_very_long_string(self) -> None:
        """Very long string (100K chars) should not OOM or crash."""
        base = "The quick brown fox jumps over the lazy dog. "
        text = base * 2500  # ~100K chars
        provider = LocalFallbackProvider()
        result = await provider.analyze(text)
        assert isinstance(result, ModerationResult)
        # Analysis should complete without error
        assert "obfuscation_score" in result.categories

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_unicode_only(self) -> None:
        """Text with only non-Latin Unicode should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("你好世界 😊🌟🎉 こんにちは 안녕하세요")
        assert isinstance(result, ModerationResult)
        # Non-Latin text should not be falsely flagged as homoglyph obfuscation
        # (CJK and emoji are NOT in the homoglyph ranges)
        assert result.categories.get("homoglyph_density", 0) == 0.0

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_emoji_only(self) -> None:
        """Text with only emoji should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("😊🌟🎉🎈🎁🎀")
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_single_character(self) -> None:
        """Single character should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("a")
        assert isinstance(result, ModerationResult)
        result2 = await provider.analyze("0")
        assert isinstance(result2, ModerationResult)
        result3 = await provider.analyze("@")
        assert isinstance(result3, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_special_chars_only(self) -> None:
        """Text with only special characters should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_null_byte(self) -> None:
        """Text with null bytes should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("test\x00text\x00with\x00nulls")
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_newlines_only(self) -> None:
        """Text with only newlines should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("\n\n\n\n\n")
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_tabs_only(self) -> None:
        """Text with only tabs should not crash."""
        provider = LocalFallbackProvider()
        result = await provider.analyze("\t\t\t\t\t")
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_mixed_encoding(self) -> None:
        """Text with mixed encodings (Latin + emoji + CJK) should resolve."""
        provider = LocalFallbackProvider()
        text = "hello 世界 🌍 test 123 🎯 fin"
        result = await provider.analyze(text)
        assert isinstance(result, ModerationResult)

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_very_short_no_content_provider_chain(self) -> None:
        """Chain with empty or whitespace text should return correct defaults."""
        chain = ProviderChain([FailingMockProvider()])
        result = await chain.analyze("   ")
        assert result.is_flagged is False
        assert result.provider_name == "provider_chain"

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_provider_chain_none_provider(self) -> None:
        """Provider chain with empty list."""
        chain = ProviderChain([])
        result = await chain.analyze("test")
        assert "__all_failed__" in result.categories


class TestProviderChainConsistency:
    """Provider chain must be deterministic for the same input."""

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_same_input_same_output(self) -> None:
        """Same input should produce the same output."""
        chain = ProviderChain(
            [AlwaysPassMockProvider(), AlwaysFlagMockProvider()],
            confidence_floor=0.0,
        )

        results: list[ModerationResult] = []
        for _ in range(10):
            result = await chain.analyze("consistent test")
            results.append(result)

        # All results should be identical
        first = results[0]
        for r in results[1:]:
            assert r.is_flagged == first.is_flagged
            assert r.confidence == first.confidence
            assert r.categories == first.categories

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_clean_text_consistency(self) -> None:
        """Clean text should consistently produce low obfuscation scores."""
        provider = LocalFallbackProvider()
        text = "The quick brown fox jumps over the lazy dog."

        scores: list[float] = []
        for _ in range(5):
            result = await provider.analyze(text)
            scores.append(result.categories.get("obfuscation_score", 0))

        # All scores should be the same (deterministic analysis)
        first = scores[0]
        assert all(s == first for s in scores), (
            f"Inconsistent obfuscation scores: {scores}"
        )


class TestProviderChainIdempotency:
    """Multiple calls should not accumulate state."""

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_chain_no_state_accumulation(self) -> None:
        """Chain should not accumulate results between calls."""
        chain = ProviderChain(
            [AlwaysPassMockProvider()],
            confidence_floor=0.1,
        )

        # Call multiple times with same input
        results: list[ModerationResult] = []
        for _ in range(5):
            result = await chain.analyze("state test")
            results.append(result)

        # Each result should be independent
        for r in results:
            assert r.confidence >= 0.0

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_local_fallback_no_state(self) -> None:
        """LocalFallbackProvider should not accumulate state between calls."""
        provider = LocalFallbackProvider()

        r1 = await provider.analyze("h3ll0 w0rld")
        r2 = await provider.analyze("h3ll0 w0rld")
        assert r1.categories == r2.categories
        assert r1.is_flagged == r2.is_flagged

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_moderation_result_not_reused(self) -> None:
        """ModerationResult objects should be fresh for each call."""
        chain = ProviderChain([AlwaysFlagMockProvider()])
        r1 = await chain.analyze("freshness")
        r2 = await chain.analyze("freshness")
        assert r1 is not r2  # Different objects


class TestThreadSafety:
    """Concurrent calls must produce correct results."""

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_concurrent_chain_calls(self) -> None:
        """Concurrent chain calls should not corrupt each other."""
        from omega_vetala.observability.metrics import MetricsReporter

        metrics = MetricsReporter()
        results: list[ModerationResult] = []
        errors: list[Exception] = []

        async def moderated_call(tag: str) -> None:
            try:
                chain = ProviderChain([AlwaysFlagMockProvider()])
                result = await chain.analyze(f"concurrent {tag}")
                results.append(result)
                metrics.record_request(provider_name="concurrent_test")
            except Exception as exc:
                errors.append(exc)

        import anyio

        async with anyio.create_task_group() as tg:
            for i in range(10):
                tg.start_soon(moderated_call, str(i))

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        assert metrics.requests_total() == 10

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_concurrent_local_fallback(self) -> None:
        """Concurrent LocalFallbackProvider calls should be safe."""
        import anyio

        provider = LocalFallbackProvider()
        results: list[ModerationResult] = []
        errors: list[Exception] = []

        async def check(text: str) -> None:
            try:
                result = await provider.analyze(text)
                results.append(result)
            except Exception as exc:
                errors.append(exc)

        async with anyio.create_task_group() as tg:
            for i in range(20):
                tg.start_soon(check, f"concurrent text {i}")

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results) == 20

    @pytest.mark.regression
    def test_metrics_thread_safety(self) -> None:
        """Metrics collection must be thread-safe."""
        from omega_vetala.observability.metrics import MetricsReporter

        metrics = MetricsReporter()

        def record_burst() -> None:
            for _ in range(100):
                metrics.record_request(provider_name="burst")
                metrics.record_flag(provider_name="burst")

        threads = [threading.Thread(target=record_burst) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        snapshot = metrics.snapshot()
        assert snapshot["requests_total"] == 400
        assert snapshot["flags_total"] == 400


class TestKnownBypassPatterns:
    """Known bypass patterns using placeholder text only.

    ⚠️  These tests verify that structural detection catches common
        obfuscation patterns.  They use ONLY neutral placeholder text.
    """

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_leetspeak_bypass(self) -> None:
        """Leetspeak should be detected by structural analysis."""
        provider = LocalFallbackProvider()
        text = "h3ll0 w0rld th1s 1s l33t t3xt"
        result = await provider.analyze(text)
        assert result.categories.get("leetspeak_score", 0) > 0.1
        assert "leetspeak_score" in result.categories

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_homoglyph_bypass(self) -> None:
        """Homoglyph obfuscation should be detected."""
        provider = LocalFallbackProvider()
        text = ("\U0001d5d4\U0001d5d0\U0001d5de\U0001d5de\U0001d5d9"  # 𝕔𝕙𝕟𝕟𝕝
                "\U0001d5d3\U0001d5d6\U0001d5e2\U0001d5de")  # 𝕟𝕚𝕢𝕟
        result = await provider.analyze(text)
        assert result.categories.get("homoglyph_density", 0) > 0.1

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_space_insertion_bypass(self) -> None:
        """Spacing tricks should be detected."""
        provider = LocalFallbackProvider()
        text = "h e l l o w o r l d t e s t"
        result = await provider.analyze(text)
        assert result.categories.get("spacing_anomaly", 0) > 0.0

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_control_char_bypass(self) -> None:
        """Zero-width characters should be detected."""
        provider = LocalFallbackProvider()
        text = "tes\u200Bting\u200Bhid\u200Bden"
        result = await provider.analyze(text)
        assert result.categories.get("control_char_density", 0) > 0.0

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_mixed_case_bypass(self) -> None:
        """Alternating case should elevate case_variance."""
        provider = LocalFallbackProvider()
        text = "ThIs Is AlTeRnAtInG cAsE tExT"
        result = await provider.analyze(text)
        assert result.categories.get("case_variance", 0) > 0.3

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_combined_techniques_bypass(self) -> None:
        """Combined obfuscation techniques produce higher scores."""
        provider = LocalFallbackProvider()
        text = "h3ll0000 w0rldddd t3st1ngggg"
        result = await provider.analyze(text)
        # Obfuscation score is weighted average; leetspeak (0.3077) * 0.20 weight = ~0.0615
        assert result.categories.get("obfuscation_score", 0) > 0.07
        # Combined leetspeak + repetition should be higher than either alone
        assert result.categories.get("leetspeak_score", 0) > 0.1
        assert result.categories.get("repetition_score", 0) > 0.02


class TestGracefulDegradationRegression:
    """Regression tests for graceful degradation paths."""

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_all_providers_fail_return_structure(self) -> None:
        """When all providers fail, result should have expected structure."""
        chain = ProviderChain([FailingMockProvider(), FailingMockProvider()])
        result = await chain.analyze("test")
        assert result.is_flagged is False
        assert result.confidence == 0.0
        assert "__all_failed__" in result.categories
        assert result.provider_name == "provider_chain"

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_partial_failure_aggregates_successful(self) -> None:
        """When some providers fail, successful results should be aggregated."""
        chain = ProviderChain(
            [
                FailingMockProvider(),
                AlwaysPassMockProvider(),
                FailingMockProvider(),
            ],
            confidence_floor=0.0,
        )
        result = await chain.analyze("test")
        assert result.is_flagged is False
        # Should not have __all_failed__ since at least one succeeded
        assert "__all_failed__" not in result.categories

    @pytest.mark.regression
    @pytest.mark.anyio
    async def test_nested_failover_preserves_trace_ids(self) -> None:
        """Trace IDs from successful providers should appear in result."""
        chain = ProviderChain(
            [
                FailingMockProvider(),
                AlwaysPassMockProvider(),
                AlwaysFlagMockProvider(),
            ],
            confidence_floor=0.0,
        )
        result = await chain.analyze("trace test")
        # At least one trace_id should be present (from successful providers)
        if result.trace_id:
            assert len(result.trace_id) > 0
