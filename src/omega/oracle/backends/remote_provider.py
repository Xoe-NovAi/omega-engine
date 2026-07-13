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


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import httpx2 as httpx
from pathlib import Path
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import time
import anyio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── MetricsDB singleton (D203 — sovereignty ratio tracking) ────────
_metrics_db = None

def _record_perf(provider: str, model: str, latency_ms: float, tokens: int, is_cloud: bool = False) -> None:
    """Record a performance entry to MetricsDB for sovereignty tracking.

    Lazily initializes the MetricsDB singleton on first call.
    Swallows all errors to avoid disrupting inference.
    """
    global _metrics_db
    try:
        if _metrics_db is None:
            from omega.observability.metrics_db import MetricsDB
            _metrics_db = MetricsDB(Path("data/observability/metrics.db"))
            _metrics_db.initialize()
        _metrics_db.record_performance(
            latency_ms=latency_ms,
            provider=provider,
            model_used=model,
            prompt_tokens=tokens,
            completion_tokens=tokens // 2,
            is_cloud=is_cloud,
            trace_id=f"trc_{int(time.monotonic() * 1000000):012d}",
        )
    except Exception as e:
        logger.debug("MetricsDB recording failed (best-effort): %s", e)
        pass  # MetricsDB recording is best-effort


# ── BudgetGate integration (SPRINT-04 — cloud cost enforcement) ───
_budget_gate = None

def _check_cloud_budget(provider: str, est_tokens: int) -> bool:
    """Check if cloud request would exceed daily budget.

    Returns True if allowed, False if blocked.
    Best-effort — always allows if BudgetGate unavailable.
    [id-soft: quake-1996] cvar — lazy singleton pattern for budget gate.
    """
    global _budget_gate
    try:
        if _budget_gate is None:
            from omega.observability import get_engine
            _budget_gate = get_engine().budget_gate
        if _budget_gate is None:
            return True
        # Estimate: split tokens 70/30 prompt/completion
        est_prompt = int(est_tokens * 0.7)
        est_completion = int(est_tokens * 0.3)
        allowed, reason = _budget_gate.check_budget(provider, est_prompt, est_completion)
        if not allowed:
            logger.warning(f"BudgetGate BLOCKED {provider}: {reason}")
        return allowed
    except Exception as e:
        logger.debug("BudgetGate check failed (allowing request): %s", e)
        return True


def _record_cloud_spend(provider: str, est_tokens: int, trace_id: Optional[str] = None) -> float:
    """Record cloud spend after successful inference. Returns cost in USD.

    Best-effort — returns 0.0 if BudgetGate unavailable.
    """
    global _budget_gate
    try:
        if _budget_gate is None:
            from omega.observability import get_engine
            _budget_gate = get_engine().budget_gate
        if _budget_gate is None:
            return 0.0
        est_prompt = int(est_tokens * 0.7)
        est_completion = int(est_tokens * 0.3)
        return _budget_gate.record_spend(provider, est_prompt, est_completion, trace_id)
    except Exception as e:
        logger.debug("BudgetGate spend recording failed (returning 0.0): %s", e)
        return 0.0


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
    api_keys: List[str] = field(default_factory=list)
    base_url: Optional[str] = None
    description: str = ""
    # Retry & resilience
    max_retries: int = 3
    timeout_seconds: float = 120.0
    backoff_base: float = 0.5
    backoff_max: float = 8.0
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
        self._resolved_api_keys: List[str] = []
        self._active_key_index = 0

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def health(self) -> ProviderHealth:
        """Current health based on metrics (breaker delegated to HealthMonitor)."""
        if self.metrics.consecutive_failures > 0:
            return ProviderHealth.DEGRADED
        return ProviderHealth.HEALTHY

    def resolve_current_api_key(self) -> Optional[str]:
        """Resolve the current active API key from config.
        
        Resolution chain:
        1. Config has api_keys list → return key at _active_key_index
        2. No keys → return None
        """
        if not self.config.api_keys:
            return None
        
        # Ensure index is within bounds
        self._active_key_index %= len(self.config.api_keys)
        return self.config.api_keys[self._active_key_index]

    def supports_model(self, model_name: str) -> bool:
        """Check if this provider supports the given model."""
        if "*" in self.config.models:
            return True
        return model_name in self.config.models

    async def is_available(self) -> bool:
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
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[str]:
        """Generate a response with retry, circuit breaking, and metrics.
        
        Returns None if the provider is unavailable or all retries fail.
        """
        if not await self.is_available():
            logger.debug(f"Provider {self.name} unavailable (health={self.health.value})")
            return None
        
        # Budget check (per-provider token limit)
        if self.config.daily_token_budget is not None:
            if self.metrics.total_tokens_used >= self.config.daily_token_budget:
                logger.warning(f"Provider {self.name} daily budget exhausted ({self.metrics.total_tokens_used} tokens)")
                return None

        # BudgetGate cloud cost check (SPRINT-04)
        if self._is_cloud_name():
            est_tokens = (len(system_prompt) + len(user_query)) // 4
            if not _check_cloud_budget(self.name, est_tokens):
                return None

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                start_ms = time.monotonic() * 1000
                result = await self._send_request(
                    model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id, session_id=session_id
                )
                elapsed_ms = (time.monotonic() * 1000) - start_ms
        
                # [S3 B4] Repetition Loop Detector — abort degenerate output
                # Moved to base class so ALL providers inherit this guard
                self._detect_repetition_loop(result, model_name)
        
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
                # Record performance to MetricsDB (D203 — sovereignty tracking)
                try:
                    _record_perf(self.name, model_name, elapsed_ms, est_tokens, is_cloud=self._is_cloud_name())
                except Exception as perf_err:
                    logger.debug(f"MetricsDB recording skipped: {perf_err}")
                # Record cloud spend to BudgetGate (SPRINT-04)
                if self._is_cloud_name():
                    try:
                        _record_cloud_spend(self.name, est_tokens, trace_id)
                    except Exception as spend_err:
                        logger.debug(f"BudgetGate spend recording skipped: {spend_err}")
                return result
        
            except (OmegaError, RuntimeError, OSError, httpx.HTTPError) as e:
                last_error = e
                self.metrics.total_requests += 1
                self.metrics.failed_requests += 1
                self.metrics.consecutive_failures += 1
                self.metrics.last_failure_time = time.monotonic()
        
                # D205: Sticky Active-Passive Key Sharding
                # If it's a rate limit (429), rotate to the next key immediately
                is_rate_limit = False
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                    is_rate_limit = True
                elif isinstance(e, ProviderRateLimitError):
                    is_rate_limit = True
                
                if is_rate_limit and len(self.config.api_keys) > 1:
                    self._active_key_index = (self._active_key_index + 1) % len(self.config.api_keys)
                    logger.info(f"Provider {self.name} rate limited. Rotating to key index {self._active_key_index}")
                
                logger.warning(
                    f"Provider {self.name} attempt {attempt + 1}/{self.config.max_retries} "
                    f"failed: {e}"
                )
        
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
        """Reset provider failure metrics. Circuit state managed by HealthMonitor."""
        self.metrics.consecutive_failures = 0

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

    # ── S3 B4: Repetition Loop Detector (base class guard) ────────────
    # [id-soft: doom-1993] Precomputed Lookup — fixed-size window scan

    @staticmethod
    def _detect_repetition_loop(content: str, model_name: str, threshold: int = 3) -> None:
        """[S3 B4] Repetition Loop Detector.

        Aborts if the last `threshold` chunks (of >=20 chars) are identical,
        indicating a degenerate generation loop. Raises RuntimeError to
        trigger retry via the base class loop.

        Inherited by ALL provider subclasses (OpenAICompat, Antigravity, etc.).
        """
        if not content or len(content) < 60:
            return
        
        # Split into ~20-char windows and check last `threshold` are identical
        window = 20
        chunks = [
            content[i:i+window]
            for i in range(max(0, len(content)-window*threshold), len(content), window)
        ]
        if len(chunks) >= threshold and all(c == chunks[0] for c in chunks):
            raise RuntimeError(
                f"Provider {model_name} produced repetitive loop (identical tail detected)"
            )

    def _is_cloud_name(self) -> bool:
        """Determine if this provider is cloud-based by name heuristic."""
        cloud_prefixes = {"google", "openai", "anthropic", "openrouter", "antigravity", "opencode", "copilot"}
        return any(self.name.lower().startswith(p) for p in cloud_prefixes)

    # ── Subclass interface ────────────────────────────────────────────

    @abstractmethod
    async def _send_request(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float,
        max_tokens: int,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Send the actual API request. Subclasses implement this.
        
        Should raise an exception on failure (will be retried).
        Should return the generated text on success.
        """
        ...
