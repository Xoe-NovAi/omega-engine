"""Tests for Body-Level Error Guards (BLEG) — IW-3.

[IW-3] Body-Level Error Guards inspect HTTP 200 OK bodies for error
signatures (Silent 200s). The circuit breaker must trip on these.

[M21 Gate Integrity] Every BLEG error path must be exercised by a
contract test that validates both the error type and forensic ledger entry.

AP: AP-BLEG-TEST-v1.0.0
"""

import json
import pytest
from omega.errors import ProviderError, ProviderRateLimitError, ProviderAuthError
from omega.observability.bleg import BLEGMiddleware, ERROR_SIGNATURES


@pytest.fixture
def guard():
    """Create a BLEG middleware instance."""
    return BLEGMiddleware(enabled=True)


class TestBLEGInspect:
    """BLEG.inspect() must convert Silent 200s to typed errors."""

    def test_no_error_on_normal_200(self, guard):
        """A normal 200 OK with no error body must NOT raise."""
        guard.inspect(200, {"result": "ok", "data": []}, provider="test", trace_id="trc_test")
        # No exception = pass

    def test_raises_on_error_key(self, guard):
        """{'error': 'message'} must raise ProviderError."""
        with pytest.raises(ProviderError) as exc_info:
            guard.inspect(200, {"error": "Something went wrong"}, provider="test", trace_id="trc_test")
        assert "Something went wrong" in str(exc_info.value)

    def test_raises_on_error_code_429(self, guard):
        """{'error': {'code': 429}} must raise ProviderRateLimitError."""
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, {"error": {"code": 429, "message": "Quota exceeded"}},
                          provider="test", trace_id="trc_test")

    def test_raises_on_error_type_rate_limit(self, guard):
        """{'error': {'type': 'rate_limit_error'}} must raise ProviderRateLimitError."""
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, {"error": {"type": "rate_limit_error"}},
                          provider="test", trace_id="trc_test")

    def test_raises_on_code_429(self, guard):
        """{'code': 429} must raise ProviderRateLimitError."""
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, {"code": 429, "message": "Too Many Requests"},
                          provider="test", trace_id="trc_test")

    def test_raises_on_quota_exceeded(self, guard):
        """{'quota_exceeded': true} must raise ProviderRateLimitError."""
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, {"quota_exceeded": True}, provider="test", trace_id="trc_test")

    def test_raises_on_status_429(self, guard):
        """{'status': 429} must raise ProviderRateLimitError."""
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, {"status": 429}, provider="test", trace_id="trc_test")

    def test_raises_on_auth_error_401(self, guard):
        """{'error': {'code': 401}} must raise ProviderAuthError."""
        with pytest.raises(ProviderAuthError):
            guard.inspect(200, {"error": {"code": 401, "message": "Invalid key"}},
                          provider="test", trace_id="trc_test")

    def test_ignores_non_json_body(self, guard):
        """Non-JSON text body must be ignored (no error)."""
        guard.inspect(200, "<html>OK</html>", provider="test", trace_id="trc_test")
        # No exception = pass

    def test_ignores_non_200_status(self, guard):
        """Non-2xx status must be ignored by BLEG (already handled by HTTP layer)."""
        guard.inspect(500, {"error": "Server Error"}, provider="test", trace_id="trc_test")
        # No exception = pass — BLEG only inspects 200-range responses

    def test_raises_on_string_body_with_error(self, guard):
        """JSON string body containing error must be parsed and detected."""
        body = json.dumps({"error": "Something wrong"})
        with pytest.raises(ProviderError):
            guard.inspect(200, body, provider="test", trace_id="trc_test")

    def test_raises_on_bytes_body_with_error(self, guard):
        """Bytes body containing error must be parsed and detected."""
        body = json.dumps({"code": 429}).encode("utf-8")
        with pytest.raises(ProviderRateLimitError):
            guard.inspect(200, body, provider="test", trace_id="trc_test")

    def test_disabled_guard_does_nothing(self):
        """Disabled guard must not inspect or raise."""
        disabled = BLEGMiddleware(enabled=False)
        disabled.inspect(200, {"error": "Should not raise"}, provider="test", trace_id="trc_test")
        # No exception = pass


class TestBLEGErrorSignatures:
    """All ERROR_SIGNATURES must be valid (contract test per M21)."""

    def test_all_signatures_have_valid_structures(self):
        """Each signature entry must have a valid structure (dict or tuple)."""
        VALID_ERROR_CLASSES = (ProviderError, ProviderRateLimitError, ProviderAuthError)
        for path, match_spec in ERROR_SIGNATURES.items():
            assert isinstance(path, str), f"Path {path!r} must be a string"
            if isinstance(match_spec, dict):
                # Dict-based: {code: error_cls, ...}
                for code, error_cls in match_spec.items():
                    assert isinstance(code, int), f"Path {path} code {code!r} must be int"
                    assert error_cls in VALID_ERROR_CLASSES, \
                        f"Path {path} code {code} has invalid class {error_cls}"
            elif isinstance(match_spec, tuple):
                match_val, error_cls = match_spec
                assert error_cls in VALID_ERROR_CLASSES, \
                    f"Path {path} has invalid error class {error_cls}"
                assert match_val is None or isinstance(match_val, (int, str)), \
                    f"Path {path} has invalid match_value {match_val}"
            else:
                pytest.fail(f"Path {path} has invalid signature type {type(match_spec)}")
