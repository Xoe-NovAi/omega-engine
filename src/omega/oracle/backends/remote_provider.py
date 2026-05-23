# 🔱 Remote Provider — Scalable Cloud Backend Abstraction
# AP: AP-REMOTE-PROVIDER-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ opus-4.6 ⬡ antigravity ⬡ trc_core ⬡ PROVIDER-FABRIC
#
# Base class for all remote (cloud) inference providers.
# Every remote provider implements the same interface, enabling
# the ProviderFabric to swap them transparently.
#
# Design goals:
#   - Uniform interface for any OpenAI-compatible or custom API
#   - Built-in retry with exponential backoff
#   - Circuit breaker pattern (3 failures → 30s cooldown)
#   - Request/response metrics for observability
#   - Budget guards (daily token limits)

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProviderHealth(Enum):
    """Health states for a remote provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    COOLDOWN = "cooldown"


@dataclass
class ProviderMetrics:
    """Runtime metrics for a remote provider instance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0.0
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    cooldown_until: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests


@dataclass
class ProviderConfig:
    """Configuration for a remote provider, loaded from providers.yaml."""
    name: str
    priority: int
    enabled: bool = True
    models: List[str] = field(default_factory=lambda: ["*"])
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    description: str = ""
    # Retry & resilience
    max_retries: int = 3
    timeout_seconds: float = 30.0
    backoff_base: float = 0.5
    backoff_max: float = 8.0
    # Circuit breaker
    circuit_breaker_threshold: int = 3
    circuit_breaker_cooldown: float = 30.0
    # Budget
    daily_token_budget: Optional[int] = None
    # Provider-specific extra config
    extra: Dict[str, Any] = field(default_factory=dict)


class RemoteProvider(ABC):
    """Abstract base class for all remote inference providers.

    Subclasses implement _send_request() with provider-specific API logic.
    The base class handles retry, circuit breaking, metrics, and budget.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.metrics = ProviderMetrics()
        self._resolved_api_key: Optional[str] = None

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def health(self) -> ProviderHealth:
        """Current health based on circuit breaker state."""
        now = time.monotonic()
        if now < self.metrics.cooldown_until:
            return ProviderHealth.COOLDOWN
        if self.metrics.consecutive_failures >= self.config.circuit_breaker_threshold:
            return ProviderHealth.UNHEALTHY
        if self.metrics.consecutive_failures > 0:
            return ProviderHealth.DEGRADED
        return ProviderHealth.HEALTHY

    def resolve_api_key(self) -> Optional[str]:
        """Resolve API key from config — supports env: prefix."""
        if self._resolved_api_key is not None:
            return self._resolved_api_key

        key = self.config.api_key
        if not key:
            return None

        import os
        if key.startswith("env:"):
            env_var = key[4:]
            self._resolved_api_key = os.environ.get(env_var)
        else:
            self._resolved_api_key = key

        return self._resolved_api_key

    def supports_model(self, model_name: str) -> bool:
        """Check if this provider supports the given model."""
        if "*" in self.config.models:
            return True
        return model_name in self.config.models

    def is_available(self) -> bool:
        """Check if the provider is enabled and healthy."""
        if not self.config.enabled:
            return False
        h = self.health
        return h in (ProviderHealth.HEALTHY, ProviderHealth.DEGRADED)

    async def generate(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """Generate a response with retry, circuit breaking, and metrics.

        Returns None if the provider is unavailable or all retries fail.
        """
        if not self.is_available():
            logger.debug(f"Provider {self.name} unavailable (health={self.health.value})")
            return None

        # Budget check
        if self.config.daily_token_budget is not None:
            if self.metrics.total_tokens_used >= self.config.daily_token_budget:
                logger.warning(f"Provider {self.name} daily budget exhausted ({self.metrics.total_tokens_used} tokens)")
                return None

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                start_ms = time.monotonic() * 1000
                result = await self._send_request(
                    model_name, system_prompt, user_query, temperature, max_tokens
                )
                elapsed_ms = (time.monotonic() * 1000) - start_ms

                # Record success
                self.metrics.total_requests += 1
                self.metrics.successful_requests += 1
                self.metrics.total_latency_ms += elapsed_ms
                self.metrics.consecutive_failures = 0
                self.metrics.last_success_time = time.monotonic()

                # Estimate token usage (rough: 4 chars per token)
                if result:
                    est_tokens = (len(system_prompt) + len(user_query) + len(result)) // 4
                    self.metrics.total_tokens_used += est_tokens

                logger.info(
                    f"Provider {self.name} responded in {elapsed_ms:.0f}ms "
                    f"(attempt {attempt + 1})"
                )
                return result

            except Exception as e:
                last_error = e
                self.metrics.total_requests += 1
                self.metrics.failed_requests += 1
                self.metrics.consecutive_failures += 1
                self.metrics.last_failure_time = time.monotonic()

                logger.warning(
                    f"Provider {self.name} attempt {attempt + 1}/{self.config.max_retries} "
                    f"failed: {e}"
                )

                # Circuit breaker trip
                if self.metrics.consecutive_failures >= self.config.circuit_breaker_threshold:
                    self.metrics.cooldown_until = (
                        time.monotonic() + self.config.circuit_breaker_cooldown
                    )
                    logger.error(
                        f"Provider {self.name} circuit breaker TRIPPED — "
                        f"cooling down for {self.config.circuit_breaker_cooldown}s"
                    )
                    break

                # Exponential backoff
                if attempt < self.config.max_retries - 1:
                    delay = min(
                        self.config.backoff_base * (2 ** attempt),
                        self.config.backoff_max,
                    )
                    import anyio
                    await anyio.sleep(delay)

        logger.error(f"Provider {self.name} exhausted all retries. Last error: {last_error}")
        return None

    def reset_circuit_breaker(self):
        """Manually reset the circuit breaker (e.g., after config change)."""
        self.metrics.consecutive_failures = 0
        self.metrics.cooldown_until = 0.0

    def get_status(self) -> Dict[str, Any]:
        """Return a status dict for diagnostics."""
        return {
            "name": self.name,
            "health": self.health.value,
            "enabled": self.config.enabled,
            "priority": self.config.priority,
            "total_requests": self.metrics.total_requests,
            "success_rate": f"{self.metrics.success_rate:.1%}",
            "avg_latency_ms": f"{self.metrics.avg_latency_ms:.0f}",
            "tokens_used": self.metrics.total_tokens_used,
            "consecutive_failures": self.metrics.consecutive_failures,
        }

    # ── Subclass interface ────────────────────────────────────────────

    @abstractmethod
    async def _send_request(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Send the actual API request. Subclasses implement this.

        Should raise an exception on failure (will be retried).
        Should return the generated text on success.
        """
        ...
