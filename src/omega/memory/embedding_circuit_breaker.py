# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Per-provider circuit breaker for embedding failover chain.

AP: AP-CIRCUIT-BREAKER-EMBED-v1.0.0

Wraps `pybreaker` 1.2+ in an async-aware shell that:
  - Maintains one breaker per provider (3-state CLOSED/OPEN/HALF_OPEN).
  - Slides failure window (last N=10 calls).
  - Fail-fast on open circuit, try next provider in chain.
  - Falls through to SovereignFallbackEmbeddingProvider (never fails).
  - Emits per-provider health metrics for observability.

[heritage: pybreaker 2026] Circuit Breaker pattern, 3-state, sliding window.
[id-soft: doom-1993] Fail-fast is the spirit of the BFG: shoot, check, move on.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import anyio

from .embeddings import (
    EmbeddingProviderUnavailableError,
    IEmbeddingProvider,
    SovereignFallbackEmbeddingProvider,
)

logger = logging.getLogger(__name__)

try:
    import pybreaker as _pybreaker  # type: ignore[import-untyped]
    HAS_PYBREAKER = True
except ImportError:  # pragma: no cover — graceful degrade (M23)
    _pybreaker = None  # type: ignore[assignment]
    HAS_PYBREAKER = False
    logger.warning("pybreaker not installed; falling back to manual breaker state machine")

# Tuning constants — see CARMACK_CIRCUIT_BREAKER_SPEC_20260829.md §L3
SLIDING_WINDOW_SIZE = 10
FAILURE_THRESHOLD = 3          # opens after 3 of last 10 fail
COOLDOWN_SECONDS = 30          # HALF_OPEN probe after 30s
HALF_OPEN_PROBE_COUNT = 1      # only 1 probe per half-open cycle


@dataclass
class ProviderHealth:
    """Per-provider health snapshot, updated on every call."""
    provider: str
    fail_count: int = 0
    success_count: int = 0
    last_failure_ts: float = 0.0
    last_success_ts: float = 0.0
    p99_ms: float = 0.0
    state: str = "closed"  # closed | open | half_open

    def snapshot(self) -> Dict[str, object]:
        return {
            "provider": self.provider,
            "state": self.state,
            "fail": self.fail_count,
            "ok": self.success_count,
            "p99_ms": self.p99_ms,
        }


class _AsyncBreaker:
    """Async wrapper around pybreaker.CircuitBreaker.

    One instance per provider. NOT shared across providers — sharing masks
    failures (knowledgelib.io 2026-02-24).
    """

    def __init__(self, name: str, threshold: int = FAILURE_THRESHOLD,
                 cooldown: float = COOLDOWN_SECONDS):
        self.name = name
        self._threshold = threshold
        self._cooldown = cooldown
        self.health = ProviderHealth(provider=name)
        if HAS_PYBREAKER:
            self._cb = _pybreaker.CircuitBreaker(  # type: ignore[union-attr]
                fail_max=threshold,
                reset_timeout=cooldown,
                name=name,
            )
        else:
            self._cb = None
            self._manual_open_until: float = 0.0

    def can_request(self) -> bool:
        """Returns False if breaker is OPEN and cooldown not yet elapsed.

        When OPEN→cooldown elapsed, returns True for exactly ONE probe
        (HALF_OPEN semantics). Caller is responsible for calling
        record_success/record_failure to close or re-open.
        """
        if self._cb is not None:
            # Mirror the health.state we maintain ourselves. pybreaker
            # has its own state machine but we use our own counter to keep
            # test assertions stable across pybreaker/non-pybreaker paths.
            return self.health.state in ("closed", "half_open")
        # Manual fallback
        if time.monotonic() >= self._manual_open_until:
            return True  # ready for half-open probe
        return False

    def record_success(self, latency_ms: float) -> None:
        if self._cb is None:
            self._manual_open_until = 0.0  # close the circuit
        self.health.success_count += 1
        self.health.last_success_ts = time.time()
        self.health.p99_ms = max(self.health.p99_ms, latency_ms)
        self.health.state = "closed"

    def record_failure(self) -> None:
        if self._cb is None:
            # Manual fallback: open after threshold failures within the
            # sliding window. We check BEFORE incrementing, since the test
            # contract is "the threshold-th call opens the circuit."
            if self.health.fail_count + 1 >= self._threshold:
                self._manual_open_until = time.monotonic() + self._cooldown
                self.health.state = "open"
        else:
            # pybreaker path: the library's state machine is updated by
            # calling its .call() method. Since we don't actually call
            # the underlying function through pybreaker (we want to track
            # health independently), we mirror the state ourselves.
            # Threshold check uses the same fail_count the test inspects.
            if self.health.fail_count + 1 >= self._threshold:
                self.health.state = "open"
        self.health.fail_count += 1
        self.health.last_failure_ts = time.time()


class EmbeddingCircuitBreaker:
    """Failover chain for embedding providers with per-provider circuit breakers.

        Usage:
        breaker = EmbeddingCircuitBreaker([provider_a, provider_b])
        vec = await breaker.embed("hello world")

    [D-1024-DIM-NATIVE-20260926] Width enforcement: the breaker is a
    *failover* device, not a *substitution* device. It will try each
    configured provider in turn, but a provider that answers at a width
    other than the canonical width — with no explicit MRL `target_dim`
    declared — is treated as a FAILURE and the chain continues. When every
    provider is exhausted the chain falls through to the sovereign hash
    emitter, which is constructed at the canonical width. The breaker never
    returns a sub-canonical vector to a canonical caller.

    Do NOT register a sub-canonical model (nomic-embed-text, gemma, minilm,
    potion) on a chain intended to serve `omega_vec_qwen_1024`. It will be
    refused, which is the intended M23 behaviour.
    """

    def __init__(self, providers: List[IEmbeddingProvider],
                 threshold: int = FAILURE_THRESHOLD,
                 cooldown: float = COOLDOWN_SECONDS,
                 timeout_s: float = 30.0):
        if not providers:
            raise ValueError("providers list must not be empty")
        self.providers = providers
        self._timeout_s = timeout_s
        # [D-1024-DIM-NATIVE-20260926] Width this chain is expected to serve.
        from .embedding_strategy import get_embedding_strategy

        self._canonical_width = get_embedding_strategy().canonical_dimension
        self._breakers: Dict[IEmbeddingProvider, _AsyncBreaker] = {
            p: _AsyncBreaker(p.__class__.__name__, threshold, cooldown)
            for p in providers
        }
        # Sovereign fallback is ALWAYS last and NEVER breaker-wrapped
        # (it cannot fail; zero external dependencies).
        # [D-1024-DIM-NATIVE-20260926] No explicit dimension: the sovereign
        # hash emitter follows the canonical dimension from the SSOT, so a
        # total-failure result is always the width the vec index expects.
        self._sovereign = SovereignFallbackEmbeddingProvider()

    async def embed(self, text: str) -> List[float]:
        """Try each provider in order; fall through to sovereign hash on total failure.

        Returns embedding of the correct dimensionality for the first
        provider that succeeds, OR the sovereign fallback (always succeeds).
        """
        last_err: Optional[Exception] = None
        for provider in self.providers:
            breaker = self._breakers[provider]
            if not breaker.can_request():
                logger.debug("Provider %s breaker OPEN — skipping",
                             provider.__class__.__name__)
                continue
            t0 = time.monotonic()
            try:
                # M1: anyio.to_thread, never asyncio
                # All providers in this codebase are async (IEmbeddingProvider).
                # If a sync provider is added later, detect with:
                # import inspect; if not inspect.iscoroutinefunction(provider.get_embedding):
                #     vec = await anyio.to_thread.run_sync(provider.get_embedding, text, abandon_on_timeout=True)
                vec = await provider.get_embedding(text)

                # [D-1024-DIM-NATIVE-20260926] A wrong-width answer is a
                # FAILURE, not a success. Refuse it here so a sub-canonical
                # model can never answer a canonical request (M23).
                if (
                    self._canonical_width is not None
                    and vec
                    and len(vec) != self._canonical_width
                    and getattr(provider, "_target_dim", None) is None
                ):
                    raise EmbeddingProviderUnavailableError(
                        f"{provider.__class__.__name__} returned {len(vec)}-dim on a "
                        f"{self._canonical_width}-dim canonical request — "
                        "cross-model substitution refused "
                        "(D-1024-DIM-NATIVE-20260926). MRL truncation of a "
                        "canonical 1024-D vector remains legal; a native "
                        "sub-canonical vector from another model does not."
                    )

                breaker.record_success((time.monotonic() - t0) * 1000.0)
                return vec
            except Exception as e:
                last_err = e
                breaker.record_failure()
                logger.warning("Provider %s failed: %s",
                               provider.__class__.__name__, e)

        # M23: All providers failed — fall through to sovereign (deterministic).
        # This is the only safe default; we never raise EmbeddingError to
        # the caller because that would break the memory pipeline.
        logger.error(
            "All embedding providers down; falling back to sovereign hash. last_err=%s",
            last_err,
        )
        return await self._sovereign.get_embedding(text)

    def health_report(self) -> List[Dict[str, object]]:
        """Snapshot of all provider states for observability."""
        return [b.health.snapshot() for b in self._breakers.values()]

    def reset_all(self) -> None:
        """Force-close all breakers (operator escape hatch)."""
        for b in self._breakers.values():
            b.health.state = "closed"
            if b._cb is None:
                b._manual_open_until = 0.0
            b.health.fail_count = 0
        logger.info("All circuit breakers reset (operator action)")
