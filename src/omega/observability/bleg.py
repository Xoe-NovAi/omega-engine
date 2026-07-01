# 🔱 Body-Level Error Guards (BLEG)
# AP: AP-BLEG-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ bleg ⬡ OBSERVABILITY
#
# Middleware that inspects HTTP 200 (OK) response bodies for error
# signatures. Many cloud APIs return HTTP 200 with an error payload
# when quota is exhausted or auth is invalid — BLEG catches these
# "Silent 200s" and converts them to typed OmegaErrors so the circuit
# breaker trips correctly.
#
# [M9 Error Integrity] — No error goes undetected, even in a 200 OK.
# [M22 Response Provenance] — Every detected error records the provider.
#
# [id-soft: quake-1996] Right Approximation — a simple JSON-keyword
# scan is "good enough" for 99% of cases. Full schema validation is
# not needed at this layer.

import json
import logging
from typing import Any, Dict, Optional
from omega.errors import ProviderError, ProviderRateLimitError, ProviderAuthError
from omega.observability.ufl import get_ufl_writer

logger = logging.getLogger(__name__)

# ── Error signatures to scan in response bodies ──────────────────────
# Each entry is (keyword_path, error_factory).
# keyword_path is a dot-separated path into the JSON body.
# If the key exists AND its value is truthy, the factory is called.

ERROR_SIGNATURES: Dict[str, tuple] = {
    # Numeric code matches FIRST — exact status codes.
    "error.code": {                            # {"error": {"code": 429}}
        429: ProviderRateLimitError,
        401: ProviderAuthError,
        403: ProviderAuthError,
    },
    "code": {                                  # {"code": 429}
        429: ProviderRateLimitError,
        401: ProviderAuthError,
        403: ProviderAuthError,
    },
    "status": {                                # {"status": 429}
        429: ProviderRateLimitError,
        401: ProviderAuthError,
        403: ProviderAuthError,
    },
    # Keyword matches — rate limit indicators.
    "quota_exceeded": (None, ProviderRateLimitError),  # {"quota_exceeded": true}
    "error.type": (                            # {"error": {"type": "rate_limit_error"}}
        "rate_limit", ProviderRateLimitError
    ),
    # Generic string matches — last resort.
    "error.message": (None, ProviderError),    # {"error": {"message": ...}}
    "error": ("__string__", ProviderError),    # {"error": "string message"}
}


class BLEGMiddleware:
    """Body-Level Error Guard — inspects HTTP 200 OK bodies for errors.

    This is NOT an ASGI/WSGI middleware. It's a response inspection
    function to be called after any httpx (or similar) request, before
    the caller processes the response.

    Usage::

        guard = BLEGMiddleware()
        response = await client.post(...)
        guard.inspect(response, provider="firecrawl", trace_id="trc_abc")
        # If a Silent 200 was detected, inspect() raises the error.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._ledger = get_ufl_writer() if enabled else None

    def inspect(
        self,
        status_code: int,
        body: Any,
        provider: str = "unknown",
        trace_id: str = "unknown",
        url: str = "",
    ) -> None:
        """Inspect an HTTP response body for error signatures.

        Args:
            status_code: The HTTP status code.
            body: The response body — JSON-deserialized dict, a string,
                or bytes. Strings/bytes will be parsed as JSON if possible.
            provider: The provider name for error attribution.
            trace_id: Current trace_id for forensic logging.
            url: The request URL for diagnostic context.

        Raises:
            ProviderRateLimitError: If a rate-limit error signature is found.
            ProviderAuthError: If an auth error signature is found.
            ProviderError: If a generic error signature is found.
        """
        if not self._enabled:
            return

        # Only inspect 200-range responses for Silent 200s
        if not (200 <= status_code < 300):
            return

        # Parse the body if needed
        parsed = self._parse_body(body)
        if parsed is None:
            return  # Body is not JSON — nothing to inspect

        # Scan for error signatures
        error_info = self._scan_for_errors(parsed)
        if error_info is None:
            return  # No error signature found

        error_cls, message = error_info

        # Log the silent failure to the forensic ledger
        if self._ledger:
            self._ledger.write(
                event_type="silent_200",
                trace_id=trace_id,
                provider=provider,
                payload={
                    "url": url,
                    "status_code": status_code,
                    "error_signature": error_cls.__name__,
                    "error_message": message[:300],
                    "body_sample": str(parsed)[:500],
                },
            )

        # Raise the typed error so the circuit breaker trips
        raise error_cls(provider, message)

    # ── Internal ───────────────────────────────────────────────────

    @staticmethod
    def _parse_body(body: Any) -> Optional[Dict[str, Any]]:
        """Parse a response body into a dict if it's JSON."""
        if isinstance(body, dict):
            return body
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")
        if isinstance(body, str):
            try:
                return json.loads(body)
            except (json.JSONDecodeError, ValueError):
                return None
        return None

    @staticmethod
    def _scan_for_errors(parsed: Dict[str, Any]) -> Optional[tuple]:
        """Scan a parsed JSON dict for known error signatures.

        Returns (error_class, message) if a signature matches, else None.
        """
        # Check each signature path
        for path, match_spec in ERROR_SIGNATURES.items():
            value = _get_nested(parsed, path)
            if value is None:
                continue

            # Determine the error message from a meaningful source
            msg = str(value) if isinstance(value, (str, int, float)) else str(
                parsed.get("error", {}).get("message",
                parsed.get("message", str(parsed)))
            )

            if isinstance(match_spec, dict):
                # Dict-based numeric code match
                try:
                    int_val = int(value)
                    if int_val in match_spec:
                        return (match_spec[int_val], msg[:500])
                except (ValueError, TypeError):
                    continue

            elif isinstance(match_spec, tuple):
                match_value, error_cls = match_spec

                if match_value == "__string__":
                    # Generic "error" key — only match if value is a string
                    if isinstance(value, str) and value:
                        return (error_cls, value[:500])
                    continue

                if match_value is None:
                    # Any truthy value at this path is an error
                    if value:
                        return (error_cls, msg[:500])

                elif isinstance(match_value, str):
                    # String match — check if value CONTAINS the keyword
                    # e.g. "rate_limit_error" contains "rate_limit"
                    str_val = str(value).lower()
                    keyword = match_value.lower()
                    if keyword in str_val or keyword.replace("_", "") in str_val:
                        return (error_cls, msg[:500])

        return None


def _get_nested(d: Dict[str, Any], path: str) -> Any:
    """Get a nested value from a dict using dot-separated path."""
    parts = path.split(".")
    current = d
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current
