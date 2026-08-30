# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-RATE-LIMIT-v1.0.0
# AP: AP-RATE-LIMIT-v1.0.0
# 🔱 Rate Limiter — Token Bucket / Sliding Window per Provider
# Ported from xna-omega-legacy/src/omega/core/rate_limiter.py


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Implements a Token Bucket rate limiting algorithm to prevent provider
    throttling and ensure fair usage across entities.
    """

    def __init__(self):
        # provider_name -> (current_tokens, last_refill_time)
        self._buckets: Dict[str, Tuple[float, float]] = {}
        # provider_name -> (capacity, refill_rate_per_sec)
        self._configs: Dict[str, Tuple[float, float]] = {
            "native-gguf": (100.0, 10.0),
            "lmster": (50.0, 5.0),
            "ollama": (50.0, 5.0),
            "google": (10.0, 1.0),
            "openrouter": (20.0, 2.0),
            "opencode-zen": (20.0, 2.0),
            "cline": (10.0, 1.0),
        }

    async def check_limit(self, provider_name: str) -> bool:
        """
        Checks if a provider has available tokens.
        If tokens are available, consumes one and returns True.
        """
        now = time.time()
        capacity, refill_rate = self._configs.get(provider_name, (20.0, 2.0))

        # Initialize bucket if not present
        if provider_name not in self._buckets:
            self._buckets[provider_name] = (capacity, now)

        tokens, last_refill = self._buckets[provider_name]

        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        new_tokens = min(capacity, tokens + (elapsed * refill_rate))

        if new_tokens >= 1.0:
            # Consume token and update bucket
            self._buckets[provider_name] = (new_tokens - 1.0, now)
            return True

        logger.warning(
            f"Rate limit exceeded for provider {provider_name}. Tokens: {new_tokens:.2f}"
        )
        return False

    def update_config(self, provider_name: str, capacity: float, refill_rate: float):
        """Update rate limit config for a specific provider."""
        self._configs[provider_name] = (capacity, refill_rate)
