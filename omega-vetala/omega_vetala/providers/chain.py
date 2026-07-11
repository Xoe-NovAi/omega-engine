# 🔱 omega-vetala — Provider Chain with Failover
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ PROVIDER-CHAIN
#
# [Worse is Better: Gabriel 1991] — try the simplest/cheapest providers first,
#   fall through to more expensive ones only when necessary.
#
# Orchestrates multiple providers in priority order.  Each provider is tried
# sequentially; on failure or low confidence the chain falls through to the
# next.  Results are aggregated via weighted voting.

from __future__ import annotations

import logging
import time
from typing import Any

import anyio
import yaml

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
    ProviderError,
)

logger = logging.getLogger(__name__)

# Default per-provider timeout in seconds.
_DEFAULT_TIMEOUT = 15.0

# If a provider's confidence is below this we try the next one.
_DEFAULT_CONFIDENCE_FLOOR = 0.1


class ProviderChain(ModelProvider):
    """Orchestrates multiple :class:`ModelProvider` instances with failover.

    Providers are tried in order.  If a provider fails (raises, times out)
    or returns confidence below *confidence_floor*, the next provider is
    attempted.  The final result is an aggregate of all non-failed results.

    Usage::

        chain = ProviderChain([
            PerspectiveProvider(),
            OpenAIModerationProvider(),
            HuggingFaceProvider(),
            LocalFallbackProvider(),
        ])
        result = await chain.analyze("some text")

    Configuration can also be loaded from YAML::

        chain = ProviderChain.from_yaml("config.yaml")

    Attributes:
        supports_offline: True if ALL providers in the chain support offline.
    """

    def __init__(
        self,
        providers: list[ModelProvider],
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        confidence_floor: float = _DEFAULT_CONFIDENCE_FLOOR,
    ) -> None:
        """Initialise chain.

        Args:
            providers: Ordered list of providers to try.
            timeout: Maximum seconds to wait for each provider.
            confidence_floor: Minimum confidence to accept a result
                without falling through.
        """
        self._providers = providers
        self._timeout = timeout
        self._confidence_floor = confidence_floor

    @property
    def supports_offline(self) -> bool:
        """True iff every provider in the chain supports offline operation."""
        return all(p.supports_offline for p in self._providers)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(cls, path: str) -> "ProviderChain":
        """Build a chain from a YAML configuration file.

        The YAML must define a ``providers`` list where each entry has
        a ``type`` field matching a registered provider class name.

        Example YAML::

            providers:
              - type: perspective
              - type: openai_moderation
              - type: huggingface
                model: unitary/toxic-bert
              - type: local_fallback

        Args:
            path: Path to YAML config file.

        Returns:
            A configured :class:`ProviderChain`.

        Raises:
            ProviderError: If the YAML is invalid or a provider type is
                unknown.
        """
        with open(path) as fh:
            config: dict[str, Any] = yaml.safe_load(fh)

        provider_configs = config.get("providers", [])
        providers: list[ModelProvider] = []

        for entry in provider_configs:
            ptype = entry.get("type", "").lower()
            kwargs = {k: v for k, v in entry.items() if k != "type"}
            provider = cls._build_provider(ptype, **kwargs)
            providers.append(provider)

        return cls(
            providers,
            timeout=config.get("timeout", _DEFAULT_TIMEOUT),
            confidence_floor=config.get(
                "confidence_floor", _DEFAULT_CONFIDENCE_FLOOR
            ),
        )

    @staticmethod
    def _build_provider(ptype: str, **kwargs: Any) -> ModelProvider:
        """Resolve a provider type string to an instance."""
        registry = {
            "perspective": "PerspectiveProvider",
            "openai_moderation": "OpenAIModerationProvider",
            "openai": "OpenAIModerationProvider",
            "huggingface": "HuggingFaceProvider",
            "hf": "HuggingFaceProvider",
            "local_fallback": "LocalFallbackProvider",
            "local": "LocalFallbackProvider",
        }

        class_name = registry.get(ptype)
        if class_name is None:
            raise ProviderError(f"Unknown provider type: {ptype}")

        # Late imports to avoid circular deps
        import importlib

        mod = importlib.import_module(
            "omega_vetala.providers"
        )
        cls = getattr(mod, class_name)
        return cls(**kwargs)

    # ------------------------------------------------------------------
    # Resource lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "ProviderChain":
        """Enter context of all child providers."""
        for p in self._providers:
            await p.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit context of all child providers."""
        for p in self._providers:
            await p.__aexit__(*args)

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* via the provider chain with failover.

        Each provider is tried in sequence.  If a provider times out,
        raises, or returns confidence below *confidence_floor*, the
        next provider is attempted.  Results from all successful
        providers are aggregated into a single weighted result.

        Args:
            text: Content to moderate.

        Returns:
            Aggregated :class:`ModerationResult`.
        """
        if not text.strip():
            return ModerationResult(provider_name="provider_chain")

        results: list[ModerationResult] = []

        for idx, provider in enumerate(self._providers):
            try:
                with anyio.fail_after(self._timeout):
                    result = await provider.analyze(text)
            except (ProviderError, TimeoutError, Exception) as exc:
                logger.warning(
                    "Provider %d (%s) failed: %s",
                    idx,
                    type(provider).__name__,
                    exc,
                )
                continue

            results.append(result)

            # If this result is confident enough, stop here
            if result.confidence >= self._confidence_floor:
                break

        if not results:
            # No provider returned a result
            return ModerationResult(
                is_flagged=False,
                confidence=0.0,
                provider_name="provider_chain",
                categories={"__all_failed__": 1.0},
            )

        # Aggregate all results via weighted voting
        return self._aggregate(results)

    @staticmethod
    def _aggregate(results: list[ModerationResult]) -> ModerationResult:
        """Weighted voting over multiple provider results.

        Later providers (higher index) are weighted slightly less to
        prefer earlier (usually cheaper/faster) providers.

        Args:
            results: Non-empty list of provider results.

        Returns:
            A single aggregated :class:`ModerationResult`.
        """
        total_weight = 0.0
        weighted_categories: dict[str, float] = {}
        total_confidence = 0.0
        any_flagged = False
        trace_ids: set[str] = set()

        n = len(results)
        for i, r in enumerate(results):
            # Weight decays linearly: 1.0, 0.9, 0.8, ...
            weight = 1.0 - (i / max(n, 1)) * 0.5
            total_weight += weight
            total_confidence += r.confidence * weight

            if r.is_flagged:
                any_flagged = True

            if r.trace_id:
                trace_ids.add(r.trace_id)

            for cat, score in r.categories.items():
                weighted_categories[cat] = (
                    weighted_categories.get(cat, 0.0) + score * weight
                )

        # Normalise
        avg_confidence = round(total_confidence / total_weight, 4)
        normalised_categories = {
            k: round(v / total_weight, 4) for k, v in weighted_categories.items()
        }

        return ModerationResult(
            is_flagged=any_flagged,
            confidence=avg_confidence,
            categories=normalised_categories,
            provider_name="provider_chain",
            trace_id=",".join(sorted(trace_ids)) if trace_ids else "",
        )
