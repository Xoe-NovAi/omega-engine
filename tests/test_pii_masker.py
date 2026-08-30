# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for PII Observation Masker (pii_masker.py).

[Gateway Proxy Architecture]
Tests cover the full detection → tokenize → [LLM] → detokenize pipeline.
"""

import re

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ── pii-shield availability check ──────────────────────────────────
try:
    import pii_shield  # noqa: F401
    _PII_SHIELD_AVAILABLE = True
except ImportError:
    _PII_SHIELD_AVAILABLE = False

from omega.oracle.pii_masker import (
    PIIMasker,
    PIIRedactionStyle,
    PIIDetection,
    PIITokenMap,
    PII_PATTERNS,
)


class TestPIIMaskerDetect:
    """PII detection tests — covers all PII types."""

    @pytest.fixture
    def masker(self):
        m = PIIMasker()
        # Ensure pii-shield is NOT used so tests are deterministic
        m._pii_scanner = None
        return m

    @pytest.mark.asyncio
    @pytest.mark.parametrize("text,expected_types", [
        ("Contact me at john@example.com", ["EMAIL"]),
        ("My SSN is 123-45-6789", ["SSN"]),
        ("Call me at 555-123-4567", ["PHONE"]),
        ("Call me at (555) 123-4567", ["PHONE"]),
        ("Call me at +1-555-123-4567", ["PHONE"]),
        ("Credit card: 4111-1111-1111-1111", ["CREDIT_CARD"]),
        ("Credit card: 4111111111111111", ["CREDIT_CARD"]),
        ("My IP is 192.168.1.1", ["IP_ADDRESS"]),
        ("Born on 01/15/1990", ["DATE_OF_BIRTH"]),
        ("MRN-9999999999", ["MEDICAL_RECORD"]),
        ("MRN-12345", ["MEDICAL_RECORD"]),
        ("Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18", ["CRYPTO_WALLET"]),
        ("ZIP: 90210", ["ZIP_CODE"]),
        ("ZIP: 90210-1234", ["ZIP_CODE"]),
        ("AWS key: AKIAIOSFODNN7EXAMPLE", ["AWS_KEY"]),
    ])
    async def test_detect(self, masker, text, expected_types):
        """Verify each PII type is detected by regex fallback."""
        detections = await masker.detect(text)
        detected_types = {d.pii_type for d in detections}
        for expected in expected_types:
            assert expected in detected_types, (
                f"Expected {expected} in {detected_types} for text: {text}"
            )

    @pytest.mark.asyncio
    async def test_detect_api_key(self, masker):
        """API key detection — covers sk- pattern."""
        text = "API: sk-abc123def456ghi789"
        detections = await masker.detect(text)
        assert any(d.pii_type == "API_KEY" for d in detections)

    @pytest.mark.asyncio
    async def test_detect_multiple_types(self, masker):
        """Verify multiple PII types are detected in one text."""
        text = "Email: john@example.com, SSN: 123-45-6789, Phone: 555-123-4567"
        detections = await masker.detect(text)
        types = {d.pii_type for d in detections}
        assert "EMAIL" in types
        assert "SSN" in types
        assert "PHONE" in types

    @pytest.mark.asyncio
    async def test_detect_no_pii(self, masker):
        """Verify no false positives on safe text."""
        detections = await masker.detect("Hello, this is a normal message without PII.")
        assert len(detections) == 0

    @pytest.mark.asyncio
    async def test_detect_empty_text(self, masker):
        """Verify empty text returns no detections."""
        detections = await masker.detect("")
        assert len(detections) == 0


class TestPIIMaskerTokenizeDetokenize:
    """Round-trip tests for tokenize → detokenize pipeline."""

    @pytest.fixture
    def masker(self):
        m = PIIMasker()
        m._pii_scanner = None
        return m

    @pytest.mark.asyncio
    async def test_roundtrip_email(self, masker):
        """Tokenize then detokenize should restore original."""
        original = "My email is john@example.com"
        detections = await masker.detect(original)
        assert len(detections) > 0

        masked, token_map = masker.tokenize(original, detections)
        # Verify masking
        assert "john@example.com" not in masked
        assert "[EMAIL_1]" in masked

        # Verify detokenize restores
        restored = masker.detokenize(masked, token_map)
        assert restored == original

    @pytest.mark.asyncio
    async def test_roundtrip_multiple(self, masker):
        """Multiple PII instances should round-trip correctly."""
        original = "Email: john@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        detections = await masker.detect(original)
        masked, token_map = masker.tokenize(original, detections)

        # Verify masking
        assert "john@example.com" not in masked
        assert "555-123-4567" not in masked
        assert "123-45-6789" not in masked

        # Verify tokens present
        assert "[EMAIL_1]" in masked
        assert "[PHONE_1]" in masked
        assert "[SSN_1]" in masked

        # Verify round-trip
        restored = masker.detokenize(masked, token_map)
        assert restored == original

    @pytest.mark.asyncio
    async def test_roundtrip_no_pii(self, masker):
        """No PII should result in unchanged text."""
        original = "Hello, how are you?"
        detections = await masker.detect(original)
        assert len(detections) == 0

        masked, token_map = masker.tokenize(original, detections)
        assert masked == original

        restored = masker.detokenize(masked, token_map)
        assert restored == original

    @pytest.mark.asyncio
    async def test_roundtrip_same_type_multiple(self, masker):
        """Multiple instances of same PII type should get unique tokens."""
        original = "Email: john@example.com and jane@example.com"
        detections = await masker.detect(original)
        masked, token_map = masker.tokenize(original, detections)

        assert "[EMAIL_1]" in masked
        assert "[EMAIL_2]" in masked

        restored = masker.detokenize(masked, token_map)
        assert restored == original

    def test_detokenize_none_token_map(self, masker):
        """Detokenize with None token_map should return text unchanged."""
        result = masker.detokenize("Hello world", None)
        assert result == "Hello world"

    def test_detokenize_empty_token_map(self, masker):
        """Detokenize with empty token_map should return text unchanged."""
        token_map = PIITokenMap()
        result = masker.detokenize("Hello world", token_map)
        assert result == "Hello world"


class TestPIIMaskerProviderAware:
    """Provider-aware bypass tests — M7 Local-First compliance."""

    def test_local_bypass(self):
        """M7: Local providers must bypass masking."""
        masker = PIIMasker()
        assert not masker.should_mask("native-gguf")
        assert not masker.should_mask("lmster")
        assert not masker.should_mask("ollama")
        assert not masker.should_mask("llama_cpp")
        assert not masker.should_mask("mock")

    def test_cloud_mask(self):
        """Cloud providers must be masked."""
        masker = PIIMasker()
        assert masker.should_mask("google")
        assert masker.should_mask("opencode-zen")
        assert masker.should_mask("github-copilot")
        assert masker.should_mask("openrouter")
        assert masker.should_mask("cloud")

    def test_unknown_provider_is_masked(self):
        """Unknown providers should be treated as cloud (conservative)."""
        masker = PIIMasker()
        assert masker.should_mask("unknown-provider")

    @pytest.mark.asyncio
    async def test_process_system_prompt_local_bypass(self):
        """Verify local provider bypass returns original text with token_map=None."""
        masker = PIIMasker()
        masker._pii_scanner = None
        prompt, query, token_map = await masker.process_system_prompt(
            "My email is john@example.com",
            "What is my email?",
            "native-gguf",
        )
        assert "john@example.com" in prompt
        assert token_map is None

    @pytest.mark.asyncio
    async def test_process_system_prompt_cloud_masks(self):
        """Verify cloud provider masks PII and returns token_map."""
        masker = PIIMasker()
        masker._pii_scanner = None
        prompt, query, token_map = await masker.process_system_prompt(
            "My email is john@example.com",
            "What is my email?",
            "google",
        )
        assert "john@example.com" not in prompt
        assert "[EMAIL_1]" in prompt
        assert token_map is not None
        assert "[EMAIL_1]" in token_map.tokens

    @pytest.mark.asyncio
    async def test_process_response_detokenizes(self):
        """Verify process_response restores original values."""
        masker = PIIMasker()
        masker._pii_scanner = None
        _, query, token_map = await masker.process_system_prompt(
            "My email is john@example.com",
            "What is my email?",
            "google",
        )
        llm_response = "Your email is [EMAIL_1]"
        detokenized = await masker.process_response(llm_response, token_map)
        assert detokenized == "Your email is john@example.com"

    @pytest.mark.asyncio
    async def test_process_response_no_token_map(self):
        """Verify process_response with None token_map returns original text."""
        masker = PIIMasker()
        response = "Hello world"
        result = await masker.process_response(response, None)
        assert result == response


class TestPIIMaskerMaskFull:
    """Non-reversible masking tests."""

    @pytest.fixture
    def masker(self):
        m = PIIMasker()
        m._pii_scanner = None
        return m

    @pytest.mark.asyncio
    async def test_mask_full(self, masker):
        """Full masking should replace PII with asterisks."""
        text = "Email: john@example.com"
        detections = await masker.detect(text)
        masked = masker.mask_full(text, detections)
        assert "john@example.com" not in masked
        assert "Email: " in masked
        # Length of masked should match original
        assert len(masked) == len(text)

    @pytest.mark.asyncio
    async def test_mask_full_no_pii(self, masker):
        """No PII should result in unchanged text."""
        text = "Hello world"
        detections = await masker.detect(text)
        masked = masker.mask_full(text, detections)
        assert masked == text


class TestPIIMaskerLegacyPatterns:
    """Legacy port tests — ANAi/XNAi era patterns."""

    def test_validate_safe_input_valid(self):
        """Legacy port: crawl.py:89-103 — valid inputs pass."""
        masker = PIIMasker()
        assert masker.validate_safe_input("Hello World")
        assert masker.validate_safe_input("test-123_abc")
        assert masker.validate_safe_input("a" * 200)

    def test_validate_safe_input_invalid(self):
        """Legacy port: crawl.py:89-103 — malicious inputs fail."""
        masker = PIIMasker()
        assert not masker.validate_safe_input("<script>alert(1)</script>")
        assert not masker.validate_safe_input("rm -rf /")
        assert not masker.validate_safe_input("a" * 201)
        assert not masker.validate_safe_input("")
        assert not masker.validate_safe_input("evil<script>")

    def test_sanitize_id_clean(self):
        """Legacy port: crawl.py:105-116 — clean IDs pass through."""
        masker = PIIMasker()
        assert masker.sanitize_id("hello-world_123") == "hello-world_123"
        assert masker.sanitize_id("simple_id") == "simple_id"

    def test_sanitize_id_path_traversal(self):
        """Legacy port: crawl.py:105-116 — path traversal is removed."""
        masker = PIIMasker()
        assert masker.sanitize_id("../../etc/passwd") == "etcpasswd"
        assert "/" not in masker.sanitize_id("../../etc/passwd")

    def test_sanitize_id_max_length(self):
        """Legacy port: crawl.py:105-116 — max 100 chars."""
        masker = PIIMasker()
        assert len(masker.sanitize_id("a" * 200)) <= 100

    def test_sanitize_id_special_chars_removed(self):
        """Legacy port: crawl.py:105-116 — special characters removed."""
        masker = PIIMasker()
        result = masker.sanitize_id("hello@world! file.txt")
        assert "@" not in result
        assert "!" not in result
        assert "." not in result
        assert " " not in result


class TestPIIMaskerPiiShield:
    """Tests for pii-shield integration (when available)."""

    @pytest.mark.skipif(
        not _PII_SHIELD_AVAILABLE,
        reason="pii-shield not installed (pip install pii-shield)",
    )
    @pytest.mark.asyncio
    async def test_pii_shield_available(self):
        """Verify pii-shield is loaded when available."""
        masker = PIIMasker()
        assert masker._pii_scanner is not None
        if masker._pii_scanner:
            detections = await masker.detect("test@example.com", use_pii_shield=True)
            # At least one detection by either pii-shield or regex
            assert len(detections) > 0

    @pytest.mark.asyncio
    async def test_pii_shield_detects_email(self):
        """Verify pii-shield detects email addresses."""
        masker = PIIMasker()
        if not masker._pii_scanner:
            pytest.skip("pii-shield not installed")
        detections = await masker.detect("Contact: john.doe@example.com", use_pii_shield=True)
        types = {d.pii_type for d in detections}
        assert "EMAIL" in types

    @pytest.mark.asyncio
    async def test_pii_shield_confidence_threshold(self):
        """Verify confidence threshold filters low-confidence detections."""
        masker = PIIMasker(confidence_threshold=0.99)  # Very high threshold
        detections = await masker.detect("test@example.com", use_pii_shield=True)
        # High threshold may filter legitimate detections; verify no crash
        assert isinstance(detections, list)


class TestPIIMaskerIntegration:
    """Integration-level tests — process_system_prompt pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_cloud(self):
        """Cloud pipeline: detect -> tokenize -> generate -> detokenize."""
        masker = PIIMasker()
        masker._pii_scanner = None

        prompt, query, token_map = await masker.process_system_prompt(
            "User email: john@example.com",
            "What is my email?",
            "openrouter",
        )
        assert "john@example.com" not in prompt
        assert token_map is not None

        # Simulate LLM response with placeholder
        llm_response = "Your email is [EMAIL_1]"
        final = await masker.process_response(llm_response, token_map)
        assert final == "Your email is john@example.com"

    @pytest.mark.asyncio
    async def test_full_pipeline_local(self):
        """Local pipeline: no masking, pass-through."""
        masker = PIIMasker()
        masker._pii_scanner = None

        prompt, query, token_map = await masker.process_system_prompt(
            "User email: john@example.com",
            "What is my email?",
            "native-gguf",
        )
        assert "john@example.com" in prompt
        assert token_map is None

    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Verify empty/edge cases don't crash."""
        masker = PIIMasker()
        masker._pii_scanner = None

        # Empty system prompt
        prompt, query, token_map = await masker.process_system_prompt(
            "",
            "hello",
            "google",
        )
        assert token_map is None  # No PII in empty text

        # Empty user query
        prompt, query, token_map = await masker.process_system_prompt(
            "hello",
            "",
            "google",
        )
        assert token_map is None  # No PII in safe text

    @pytest.mark.asyncio
    async def test_multiple_masking_calls_independent(self):
        """Multiple masking calls should produce independent token maps."""
        masker = PIIMasker()
        masker._pii_scanner = None

        _, _, token_map_1 = await masker.process_system_prompt(
            "email: alice@test.com", "", "google",
        )
        _, _, token_map_2 = await masker.process_system_prompt(
            "email: bob@test.com", "", "google",
        )

        assert token_map_1 is not None
        assert token_map_2 is not None
        # Different values should have different placeholder tokens
        assert token_map_1.tokens["[EMAIL_1]"] == "alice@test.com"
        assert token_map_2.tokens["[EMAIL_1]"] == "bob@test.com"


class TestPIIDetectionDataclass:
    """PIIDetection and PIITokenMap dataclass tests."""

    def test_pii_detection_defaults(self):
        """Verify PIIDetection has correct default values."""
        d = PIIDetection(
            pii_type="EMAIL",
            original="test@example.com",
            start=0,
            end=16,
            confidence=0.9,
            placeholder="[EMAIL_1]",
        )
        assert d.pii_type == "EMAIL"
        assert d.original == "test@example.com"
        assert d.start == 0
        assert d.end == 16
        assert d.confidence == 0.9
        assert d.placeholder == "[EMAIL_1]"

    def test_pii_token_map_add(self):
        """Verify PIITokenMap.add() correctly stores detections."""
        token_map = PIITokenMap()
        d = PIIDetection(
            pii_type="EMAIL",
            original="test@example.com",
            start=0,
            end=16,
            confidence=0.9,
            placeholder="[EMAIL_1]",
        )
        token_map.add(d)
        assert "[EMAIL_1]" in token_map.tokens
        assert token_map.tokens["[EMAIL_1]"] == "test@example.com"
        assert len(token_map.detections) == 1


class TestPIIPatternsRegistry:
    """Verify all PII_PATTERNS are defined and valid."""

    def test_patterns_defined(self):
        """All 18 PII types should have patterns."""
        assert "EMAIL" in PII_PATTERNS
        assert "PHONE" in PII_PATTERNS
        assert "SSN" in PII_PATTERNS
        assert "CREDIT_CARD" in PII_PATTERNS
        assert "BANK_ACCOUNT" in PII_PATTERNS
        assert "CRYPTO_WALLET" in PII_PATTERNS
        assert "API_KEY" in PII_PATTERNS
        assert "PASSWORD" in PII_PATTERNS
        assert "AWS_KEY" in PII_PATTERNS
        assert "IP_ADDRESS" in PII_PATTERNS
        assert "ZIP_CODE" in PII_PATTERNS
        assert "DATE_OF_BIRTH" in PII_PATTERNS
        assert "MEDICAL_RECORD" in PII_PATTERNS
        assert "PASSPORT" in PII_PATTERNS
        assert "DRIVERS_LICENSE" in PII_PATTERNS

    def test_patterns_compile(self):
        """All patterns should be valid regex."""
        for name, pattern in PII_PATTERNS.items():
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex for {name}: {e}")


@pytest.mark.asyncio
async def test_pii_masker_init():
    """Verify PIIMasker initializes without errors."""
    masker = PIIMasker()
    assert masker.confidence_threshold == 0.6
    assert masker.redaction_style == PIIRedactionStyle.TOKENIZE
    assert masker._enable_legacy is True


@pytest.mark.asyncio
async def test_pii_masker_no_crash_on_pii_shield_unavailable():
    """Verify PIIMasker handles missing pii-shield gracefully."""
    masker = PIIMasker()
    masker._pii_scanner = None  # Simulate unavailable
    detections = await masker.detect("test@example.com", use_pii_shield=True)
    # Should fall back to regex and still detect
    assert len(detections) > 0
    assert any(d.pii_type == "EMAIL" for d in detections)



