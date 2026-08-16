# 🔱 Omega Engine — Per-Domain Token Bucket Rate Limiter
# AP: AP-RATE-LIMITER-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ sovereign ⬡ RATE-LIMITER ⬡ PHASE-3
#
# [id-soft: vet-009] netchan Rate Limiting — legacy of qport pacing,
# evolved to per-domain token buckets for fair bandwidth allocation.


# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md
from __future__ import annotations

import anyio
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """A single token bucket for rate limiting.

    Attributes:
        rate: Tokens per second (allows burst by default via max_tokens).
        max_tokens: Maximum accumulated tokens (burst cap).
        tokens: Current token count.
        last_refill: Timestamp of the last token refill.
    """

    rate: float
    max_tokens: float
    tokens: float = 0.0
    last_refill: float = 0.0

    def __post_init__(self) -> None:
        self.tokens = self.max_tokens
        self.last_refill = time.time()

    def refill(self) -> None:
        """Replenish tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        """Try to consume *tokens* from the bucket.

        Returns:
            True if the tokens were consumed (rate-limited allowed).
            False if insufficient tokens (rate-limited denied).
        """
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    @property
    def fill_ratio(self) -> float:
        """Fraction of bucket capacity filled (0.0 to 1.0)."""
        if self.max_tokens <= 0:
            return 1.0
        return min(1.0, self.tokens / self.max_tokens)

    @property
    def wait_seconds(self) -> float:
        """Estimated seconds until one token is available (0 if available now)."""
        if self.consume(0):
            return 0.0
        deficit = 1.0 - self.tokens
        if self.rate <= 0:
            return float("inf")
        return deficit / self.rate


@dataclass
class RateLimiterConfig:
    """Configuration for the TokenBucketRateLimiter.

    Each domain gets its own bucket with these defaults.

    Attributes:
        default_rate: Default tokens per second for unknown domains.
        default_max_tokens: Default burst cap for unknown domains.
        domain_overrides: Per-domain overrides keyed by hostname.
                          E.g. {"arxiv.org": {"rate": 1.0, "max_tokens": 5}}
    """

    default_rate: float = 2.0
    default_max_tokens: float = 10
    domain_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)


# Standard presets for known free API sources
DEFAULT_PRESETS: Dict[str, Dict[str, float]] = {
    "gutenberg.org": {"rate": 5.0, "max_tokens": 20},
    "arxiv.org": {"rate": 3.0, "max_tokens": 15},
    "openlibrary.org": {"rate": 10.0, "max_tokens": 30},
    "archive.org": {"rate": 10.0, "max_tokens": 50},
    "wikipedia.org": {"rate": 100.0, "max_tokens": 200},
}


class TokenBucketRateLimiter:
    """Per-domain token bucket rate limiter.

    Manages a separate token bucket for each domain, ensuring fair
    bandwidth allocation across sources. Prevents any single source
    from overwhelming the engine.

    Usage:
        limiter = TokenBucketRateLimiter()
        await limiter.wait("https://arxiv.org/abs/1234.5678")
        # Proceed with HTTP request...
    """

    def __init__(self, config: Optional[RateLimiterConfig] = None) -> None:
        self._config = config or RateLimiterConfig()
        self._buckets: Dict[str, TokenBucket] = {}

        # Apply presets as domain_overrides
        for domain, overrides in DEFAULT_PRESETS.items():
            if domain not in self._config.domain_overrides:
                self._config.domain_overrides[domain] = overrides

    def _get_domain(self, url: str) -> str:
        """Extract the domain from a URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname or "unknown"
        # Strip leading www. for normalization
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname

    def _get_or_create_bucket(self, url: str) -> TokenBucket:
        """Get the token bucket for a URL's domain, creating if necessary."""
        domain = self._get_domain(url)
        if domain not in self._buckets:
            overrides = self._config.domain_overrides.get(domain, {})
            rate = overrides.get("rate", self._config.default_rate)
            max_tokens = overrides.get("max_tokens", self._config.default_max_tokens)
            self._buckets[domain] = TokenBucket(rate=rate, max_tokens=max_tokens)
            logger.debug(
                "Rate limit bucket created: %s (%.1f/s, burst=%d)",
                domain, rate, int(max_tokens),
            )
        return self._buckets[domain]

    async def wait(self, url: str, tokens: float = 1.0) -> None:
        """Block until enough tokens are available for *url*.

        Args:
            url: The URL to rate-limit.
            tokens: Number of tokens to consume (default 1.0 per request).
        """
        domain = self._get_domain(url)
        bucket = self._get_or_create_bucket(url)

        while not bucket.consume(tokens):
            wait_time = bucket.wait_seconds
            if wait_time > 0 and math.isfinite(wait_time):
                await anyio.sleep(min(wait_time, 1.0))
            else:
                await anyio.sleep(0.5)

        logger.debug(
            "Rate limit passed: %s (%.1f tokens, %.1f/%.1f remaining)",
            domain, tokens, bucket.tokens, bucket.max_tokens,
        )

    async def try_acquire(self, url: str, tokens: float = 1.0) -> bool:
        """Try to acquire tokens without blocking.

        Returns:
            True if tokens were acquired, False if rate-limited.
        """
        bucket = self._get_or_create_bucket(url)
        return bucket.consume(tokens)

    async def reset(self, url: Optional[str] = None) -> None:
        """Reset a specific URL's bucket or all buckets."""
        if url:
            domain = self._get_domain(url)
            self._buckets.pop(domain, None)
        else:
            self._buckets.clear()

    async def stats(self) -> Dict[str, Dict[str, float]]:
        """Get per-domain rate limiter statistics."""
        result: Dict[str, Dict[str, float]] = {}
        for domain, bucket in self._buckets.items():
            result[domain] = {
                "rate": bucket.rate,
                "max_tokens": bucket.max_tokens,
                "current_tokens": round(bucket.tokens, 1),
                "fill_pct": round(bucket.fill_ratio * 100, 1),
            }
        return result


# ── Named singleton for module-level import ──────────────────────────

RATE_LIMITER = TokenBucketRateLimiter()
"""Module-level singleton. Import this for convenience:

    from omega.library.rate_limiter import RATE_LIMITER
    await RATE_LIMITER.wait("https://arxiv.org/abs/1234.5678")
"""
