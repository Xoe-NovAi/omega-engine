"""Shared fixtures for omega-vetala tests.

All fixtures use neutral/placeholder text only — NO static slur lists.
"""

from __future__ import annotations

import uuid
from typing import Any, AsyncIterator

import pytest
import yaml

from omega_vetala.providers.base import ModerationResult, ModelProvider


# ═══════════════════════════════════════════════════════════════════════
# Existing fixtures (preserved from original conftest.py)
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_clean_text() -> str:
    """A benign, clean sentence."""
    return "The quick brown fox jumps over the lazy dog."


@pytest.fixture
def sample_obfuscated_text() -> str:
    """Text using leetspeak and homoglyph obfuscation."""
    return "h3ll0 th1s 1s 0bfusc4t3d t3xt w1th l33t"


@pytest.fixture
def sample_homoglyph_text() -> str:
    """Text with Cyrillic homoglyphs replacing Latin letters."""
    return "thiѕ iѕ а tеxt wіth сyrіllіс lеttеrs"


@pytest.fixture
def sample_control_char_text() -> str:
    """Text containing zero-width spaces."""
    return "nor\u200Bmal\u200Btext\u200Bwith\u200Bhidden"


@pytest.fixture
def sample_repeated_text() -> str:
    """Text with excessive character repetition."""
    return "nooooooo thissss is baaaaaad stuuuuuffff"


@pytest.fixture
def mock_perspective_response() -> dict[str, Any]:
    """Simulated Perspective API success response."""
    return {
        "attributeScores": {
            "TOXICITY": {
                "summaryScore": {"value": 0.92, "type": "probability"},
            },
            "INSULT": {
                "summaryScore": {"value": 0.85, "type": "probability"},
            },
            "PROFANITY": {
                "summaryScore": {"value": 0.75, "type": "probability"},
            },
            "THREAT": {
                "summaryScore": {"value": 0.12, "type": "probability"},
            },
            "IDENTITY_ATTACK": {
                "summaryScore": {"value": 0.08, "type": "probability"},
            },
        },
    }


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """Simulated OpenAI Moderation API success response."""
    return {
        "id": "modr-123",
        "model": "text-moderation-007",
        "results": [
            {
                "flagged": True,
                "categories": {
                    "sexual": False,
                    "hate": True,
                    "harassment": True,
                    "self-harm": False,
                    "sexual/minors": False,
                    "hate/threatening": False,
                    "violence/graphic": False,
                    "self-harm/intent": False,
                    "self-harm/instructions": False,
                    "harassment/threatening": False,
                    "violence": False,
                },
                "category_scores": {
                    "sexual": 0.01,
                    "hate": 0.88,
                    "harassment": 0.76,
                    "self-harm": 0.01,
                    "sexual/minors": 0.01,
                    "hate/threatening": 0.05,
                    "violence/graphic": 0.02,
                    "self-harm/intent": 0.01,
                    "self-harm/instructions": 0.01,
                    "harassment/threatening": 0.12,
                    "violence": 0.03,
                },
            }
        ],
    }


# ═══════════════════════════════════════════════════════════════════════
# NEW: Mock providers for deterministic testing
# ═══════════════════════════════════════════════════════════════════════


class AlwaysPassMockProvider(ModelProvider):
    """Mock provider that always returns a clean result.

    Deterministic — useful as a baseline for chain and observer tests.
    """

    supports_offline = True

    def __init__(self, latency_ms: float = 5.0) -> None:
        self._latency_ms = latency_ms

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=False,
            confidence=0.05,
            categories={"clean": 0.95},
            provider_name="always_pass_mock",
            latency_ms=self._latency_ms,
        )


class AlwaysFlagMockProvider(ModelProvider):
    """Mock provider that always flags with high confidence.

    Deterministic — useful for testing flag paths without real ML.
    """

    supports_offline = True

    def __init__(self, latency_ms: float = 10.0) -> None:
        self._latency_ms = latency_ms

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=True,
            confidence=0.95,
            categories={"toxicity": 0.95, "insult": 0.80},
            provider_name="always_flag_mock",
            latency_ms=self._latency_ms,
        )


class FailingMockProvider(ModelProvider):
    """Mock provider that always raises an exception.

    Deterministic — useful for testing failover and error handling.
    """

    supports_offline = True

    def __init__(self, error_msg: str = "mock provider crashed") -> None:
        self._error_msg = error_msg

    async def analyze(self, text: str) -> ModerationResult:
        raise RuntimeError(self._error_msg)


class SlowMockProvider(ModelProvider):
    """Mock provider that delays before returning.

    Useful for testing timeouts.
    """

    supports_offline = True

    def __init__(self, delay: float = 999.0) -> None:
        self._delay = delay

    async def analyze(self, text: str) -> ModerationResult:
        import anyio
        await anyio.sleep(self._delay)
        return ModerationResult(
            is_flagged=False,
            confidence=0.5,
            provider_name="slow_mock",
        )


class NonDeterministicMockProvider(ModelProvider):
    """Mock provider with controllable, non-deterministic results.

    Cycles through a pre-defined list of results on each call.
    Useful for testing aggregation across multiple results.
    """

    supports_offline = True

    def __init__(self, results: list[ModerationResult] | None = None) -> None:
        self._results = results or []
        self._call_count = 0

    async def analyze(self, text: str) -> ModerationResult:
        if not self._results:
            return ModerationResult(provider_name="cycle_mock")
        idx = self._call_count % len(self._results)
        self._call_count += 1
        return self._results[idx]


# ═══════════════════════════════════════════════════════════════════════
# NEW: Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def always_pass_mock() -> AlwaysPassMockProvider:
    """Deterministic mock that always returns clean."""
    return AlwaysPassMockProvider()


@pytest.fixture
def always_flag_mock() -> AlwaysFlagMockProvider:
    """Deterministic mock that always flags."""
    return AlwaysFlagMockProvider()


@pytest.fixture
def failing_mock() -> FailingMockProvider:
    """Deterministic mock that always fails."""
    return FailingMockProvider()


@pytest.fixture
def trace_id_factory() -> str:
    """Generate a unique trace ID for testing."""
    return uuid.uuid4().hex[:16]


@pytest.fixture
def sample_borderline_text() -> str:
    """Text with mild obfuscation that is borderline.

    Uses neutral placeholder-style patterns only.
    """
    return "th1s 1s s0m3 b0rd3rl1n3 t3xt w1th l33t"


@pytest.fixture
def sample_plain_ascii() -> str:
    """Completely clean, plain ASCII text with no obfuscation."""
    return "This is a sample of plain English text with no obfuscation at all."


@pytest.fixture
def sample_unicode_only() -> str:
    """Text consisting entirely of Unicode (emoji, CJK) with no Latin chars.

    This tests that providers don't falsely flag non-Latin scripts.
    """
    return "你好世界 😊🌟🎉 こんにちは 안녕하세요"


@pytest.fixture
def sample_whitespace_only() -> str:
    """Text consisting only of whitespace characters."""
    return "   \t\n  \r\n  "


@pytest.fixture
def sample_very_long_text() -> str:
    """A very long (100K) string for stress-testing providers.

    Creates a repeating pattern of neutral text.
    """
    base = "The quick brown fox jumps over the lazy dog. "
    return base * 2500  # ~100K chars


@pytest.fixture
def sample_policy_yaml() -> str:
    """A standard moderation policy as YAML string.

    Uses only structural/confidence-based rules — NO static slur lists.
    """
    return """
name: standard
description: Standard moderation policy
rules:
  - name: block_high_confidence
    description: Block high-confidence flagged content
    action: block
    min_confidence: 0.9
    require_flagged: true

  - name: warn_medium_confidence
    description: Warn on medium-confidence flagged content
    action: warn
    min_confidence: 0.5
    max_confidence: 0.9
    require_flagged: true

  - name: review_low_confidence
    description: Review low-confidence flagged content
    action: review
    min_confidence: 0.3
    max_confidence: 0.5
    require_flagged: true

  - name: log_suspicious
    description: Log very low-confidence flags for analysis
    action: log_only
    min_confidence: 0.1
    max_confidence: 0.3
    require_flagged: true

  - name: allow_clean
    description: Allow everything else
    action: allow
"""


@pytest.fixture
def sample_policy_strict_yaml() -> str:
    """A strict policy with lower thresholds — catches more content."""
    return """
name: strict
description: Strict moderation policy
rules:
  - name: block_flagged
    description: Block anything flagged with moderate confidence
    action: block
    min_confidence: 0.5
    require_flagged: true

  - name: warn_low
    description: Warn on low-confidence flags
    action: warn
    min_confidence: 0.2
    require_flagged: true

  - name: allow_clean
    description: Allow unflagged content
    action: allow
"""


@pytest.fixture
def sample_policy_relaxed_yaml() -> str:
    """A relaxed policy with higher thresholds — allows more content."""
    return """
name: relaxed
description: Relaxed moderation policy
rules:
  - name: block_very_high
    description: Block only very high-confidence flags
    action: block
    min_confidence: 0.95
    require_flagged: true

  - name: warn_high
    description: Warn on high-confidence flags
    action: warn
    min_confidence: 0.8
    require_flagged: true

  - name: allow_clean
    description: Allow everything else
    action: allow
"""


@pytest.fixture
def sample_standard_policy(sample_policy_yaml: str) -> ModerationPolicy:
    """Pre-loaded standard policy."""
    from omega_vetala.policies.loader import PolicyLoader
    loader = PolicyLoader(cache=False)
    return loader.load_from_string(sample_policy_yaml)


@pytest.fixture
def sample_strict_policy(sample_policy_strict_yaml: str) -> ModerationPolicy:
    """Pre-loaded strict policy."""
    from omega_vetala.policies.loader import PolicyLoader
    loader = PolicyLoader(cache=False)
    return loader.load_from_string(sample_policy_strict_yaml)


@pytest.fixture
def sample_relaxed_policy(sample_policy_relaxed_yaml: str) -> ModerationPolicy:
    """Pre-loaded relaxed policy."""
    from omega_vetala.policies.loader import PolicyLoader
    loader = PolicyLoader(cache=False)
    return loader.load_from_string(sample_policy_relaxed_yaml)
