# 🔱 omega-vetala — Abstract Provider Base
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ PROVIDER-BASE
#
# [id-soft: quake-1996] Zone Memory — allocated context per provider instance
#
# Abstract base class and shared data types for all moderation providers.
# All providers MUST inherit from ModelProvider and return ModerationResult.

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModerationResult:
    """Standardised result from any moderation provider.

    Every provider in the chain returns this type, enabling transparent
    aggregation, comparison, and failover in ProviderChain.

    Attributes:
        is_flagged: Whether the text is considered harmful.
        confidence: Overall confidence score (0.0–1.0).
        categories: Per-category scores keyed by category name.
        provider_name: Name of the provider that produced this result.
        latency_ms: Wall-clock time spent by the provider, in milliseconds.
        trace_id: Unique identifier for this analysis request.
    """

    is_flagged: bool = False
    confidence: float = 0.0
    categories: dict[str, float] = field(default_factory=dict)
    provider_name: str = ""
    latency_ms: float = 0.0
    trace_id: str = ""

    def __post_init__(self) -> None:
        """Auto-generate a trace_id if none was provided."""
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex[:16]


class ModelProvider(ABC):
    """Abstract base class for all moderation providers.

    Subclasses must implement :meth:`analyze` and may optionally
    override :meth:`__aenter__` / :meth:`__aexit__` for resource
    lifecycle management (e.g. model loading, connection pooling).

    Class Attributes:
        supports_offline: True if the provider can operate without network.
    """

    supports_offline: bool = False

    @abstractmethod
    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* for harmful content.

        Args:
            text: The user-generated content to classify.

        Returns:
            A :class:`ModerationResult` with scores and metadata.

        Raises:
            ProviderError: On unrecoverable provider failure.
        """
        ...

    async def __aenter__(self) -> "ModelProvider":
        """Context-manager entry — acquire resources if needed."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context-manager exit — release resources."""
        ...

    async def _measure(
        self, text: str, provider_name: str
    ) -> ModerationResult:
        """Wrap *analyze* with latency measurement.

        Subclasses call this from their :meth:`analyze` implementation
        to automatically populate latency and provider metadata.

        Args:
            text: The content to analyse.
            provider_name: Human-readable name for this provider.

        Returns:
            A :class:`ModerationResult` with timing metadata filled in.
        """
        start = time.monotonic()
        try:
            result = await self.analyze(text)
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return ModerationResult(
                is_flagged=False,
                confidence=0.0,
                provider_name=provider_name,
                latency_ms=elapsed,
                trace_id=uuid.uuid4().hex[:16],
                categories={"__error__": 1.0},
            )
        else:
            elapsed = (time.monotonic() - start) * 1000
            result.provider_name = provider_name
            result.latency_ms = elapsed
            if not result.trace_id:
                result.trace_id = uuid.uuid4().hex[:16]
            return result


class ProviderError(Exception):
    """Raised when a provider encounters an unrecoverable failure."""
