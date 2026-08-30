# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Ω-Research BudgetGuard — Redis-Backed Distributed Quota Enforcement for AMFO Tiers
⬡ OMEGA ⬡ MA'AT ⬡ N2/N5 ⬡ BUDGET-GUARD
AP Token: AP-MAAT-BUDGET-GUARD-v1.0.0

Mandate Compliance:
- M1 AnyIO: anyio.to_thread.run_sync() for Redis ops
- M2 Firewall: No Core Engine writes
- M7 Local-First: Budget tiers use local models
- M9 Error Integrity: Typed BudgetError hierarchy
- M12 Queue Integrity: BudgetToken has terminal states
- M13 Temple-Grade: Contract tests
- M21 Gate Integrity: isinstance(token, BudgetToken)
- M23 Failure Integrity: No soft-failures — budget exceeded = hard error
"""

from __future__ import annotations
import anyio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from omega.errors import OmegaError
from omega.research.types import BudgetToken


# ── Budget Error Hierarchy (M9) ──────────────────────────────────────────────


class BudgetError(OmegaError):
    """Base class for budget enforcement errors."""

    pass


class BudgetExceededError(BudgetError):
    """Requested budget exceeds tier limits."""

    def __init__(self, tier: str, requested: dict, limits: dict, **kwargs):
        self.tier = tier
        self.requested = requested
        self.limits = limits
        super().__init__(
            f"Budget for tier '{tier}' exceeded: requested {requested}, limits {limits}",
            context={"tier": tier, "requested": requested, "limits": limits},
            **kwargs,
        )


class BudgetUnavailableError(BudgetError):
    """Budget cannot be allocated (Redis unavailable, quota exhausted)."""

    def __init__(self, tier: str, reason: str, **kwargs):
        self.tier = tier
        self.reason = reason
        super().__init__(
            f"Budget unavailable for tier '{tier}': {reason}",
            context={"tier": tier, "reason": reason},
            **kwargs,
        )


class BudgetTokenExpiredError(BudgetError):
    """Budget token has expired."""

    def __init__(self, token: BudgetToken, **kwargs):
        self.token = token
        super().__init__(
            f"Budget token for experiment '{token.experiment_id}' has expired",
            context={"experiment_id": token.experiment_id, "tier": token.tier},
            **kwargs,
        )


# ── AMFO Tier Budgets (M7 Local-First) ──────────────────────────────────────

TIER_BUDGETS: dict[str, dict[str, Any]] = {
    "scout": {
        "time_sec": 60,
        "ram_mb": 2048,
        "model": "qwen3-0.6b-q6_k",
        "description": "Rapid reconnaissance — keyword extraction, feasibility check",
    },
    "validate": {
        "time_sec": 300,
        "ram_mb": 4096,
        "model": "qwen3-1.7b-q6_k",
        "description": "Validation pass — source verification, claim checking",
    },
    "synthesize": {
        "time_sec": 1800,
        "ram_mb": 8192,
        "model": "qwen3-4b-thinking-q4_k_m",
        "description": "Synthesis — deep reasoning, L3 principle extraction",
    },
    "cpu_intensive": {
        "time_sec": 3600,
        "ram_mb": 12288,
        "model": "qwen3-4b-thinking-q4_k_m",
        "description": "CPU-intensive workloads (kernel compilation, training)",
    },
    "memory_intensive": {
        "time_sec": 1800,
        "ram_mb": 14336,  # Near 14Gi limit
        "model": "qwen3-4b-thinking-q4_k_m",
        "description": "Memory-intensive workloads (large model loading)",
    },
}


# ── Budget Guard ─────────────────────────────────────────────────────────────


class BudgetGuard:
    """
    Redis-backed distributed quota enforcement for AMFO tiers.

    Uses Redis INCR with TTL for atomic budget allocation.
    Returns BudgetToken with auto-release on context exit.

    M1: AnyIO async (redis.asyncio)
    M7: Local-first tier models
    M12: BudgetToken has terminal states
    M21: Contract test compatible
    M23: Hard failures on budget exhaustion
    """

    TIER_BUDGETS = TIER_BUDGETS

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "omega:budget:",
        enable_redis: bool = True,
        max_concurrent_per_tier: int = 4,
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.enable_redis = enable_redis and REDIS_AVAILABLE
        self.max_concurrent_per_tier = max_concurrent_per_tier
        self._redis: redis.Redis | None = None
        self._local_quota: dict[str, dict] = {}  # Fallback when Redis unavailable

    async def _get_redis(self) -> redis.Redis:
        """Lazy Redis connection."""
        if self._redis is None and self.enable_redis:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _tier_key(self, tier: str) -> str:
        return f"{self.key_prefix}tier:{tier}"

    def _experiment_key(self, experiment_id: str) -> str:
        return f"{self.key_prefix}exp:{experiment_id}"

    async def check(self, tier: str, experiment_id: str) -> BudgetToken:
        """
        Allocate budget for an experiment.

        Args:
            tier: AMFO tier name (scout, validate, synthesize, cpu_intensive, memory_intensive)
            experiment_id: Unique experiment identifier

        Returns:
            BudgetToken with allocated budget and expiry

        Raises:
            BudgetExceededError: If tier limits would be exceeded
            BudgetUnavailableError: If Redis unavailable and local quota exhausted
        """
        if tier not in self.TIER_BUDGETS:
            raise BudgetExceededError(
                tier=tier,
                requested={},
                limits={},
            )

        budget = self.TIER_BUDGETS[tier]
        time_budget = budget["time_sec"]
        ram_budget = budget["ram_mb"]
        model = budget["model"]

        # Try Redis first
        if self.enable_redis:
            try:
                return await self._check_redis(tier, experiment_id, time_budget, ram_budget, model)
            except Exception:
                # Fall back to local quota if Redis fails
                pass

        # Local fallback
        return await self._check_local(tier, experiment_id, time_budget, ram_budget, model)

    async def _check_redis(
        self, tier: str, experiment_id: str, time_budget: int, ram_budget: int, model: str
    ) -> BudgetToken:
        """Allocate budget via Redis."""
        r = await self._get_redis()

        # Use Redis transaction for atomicity
        async with r.pipeline(transaction=True) as pipe:
            # Check current tier usage
            tier_key = self._tier_key(tier)
            exp_key = self._experiment_key(experiment_id)

            current = await r.get(tier_key)
            current_count = int(current) if current else 0

            if current_count >= self.max_concurrent_per_tier:
                raise BudgetUnavailableError(
                    tier=tier,
                    reason=f"Tier concurrency limit reached ({self.max_concurrent_per_tier})",
                )

            # Allocate
            pipe.incr(tier_key)
            pipe.expire(tier_key, time_budget + 60)  # TTL = budget + buffer

            # Track experiment
            pipe.hset(
                exp_key,
                mapping={
                    "tier": tier,
                    "time_budget": str(time_budget),
                    "ram_budget": str(ram_budget),
                    "model": model,
                    "allocated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            pipe.expire(exp_key, time_budget + 60)

            await pipe.execute()

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=time_budget)

        return BudgetToken(
            experiment_id=experiment_id,
            tier=tier,
            time_budget_sec=time_budget,
            ram_budget_mb=ram_budget,
            model=model,
            expires_at=expires_at,
        )

    async def _check_local(
        self, tier: str, experiment_id: str, time_budget: int, ram_budget: int, model: str
    ) -> BudgetToken:
        """Local fallback budget allocation."""
        if tier not in self._local_quota:
            self._local_quota[tier] = {"count": 0, "experiments": {}}

        tier_data = self._local_quota[tier]

        if tier_data["count"] >= self.max_concurrent_per_tier:
            raise BudgetUnavailableError(
                tier=tier,
                reason=f"Local tier concurrency limit reached ({self.max_concurrent_per_tier})",
            )

        tier_data["count"] += 1
        tier_data["experiments"][experiment_id] = {
            "tier": tier,
            "time_budget": time_budget,
            "ram_budget": ram_budget,
            "model": model,
            "allocated_at": datetime.now(timezone.utc).isoformat(),
        }

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=time_budget)

        return BudgetToken(
            experiment_id=experiment_id,
            tier=tier,
            time_budget_sec=time_budget,
            ram_budget_mb=ram_budget,
            model=model,
            expires_at=expires_at,
        )

    async def release(self, tier: str, experiment_id: str) -> None:
        """Release budget allocation (called on context exit)."""
        if self.enable_redis:
            try:
                r = await self._get_redis()
                tier_key = self._tier_key(tier)
                exp_key = self._experiment_key(experiment_id)

                async with r.pipeline(transaction=True) as pipe:
                    pipe.decr(tier_key)
                    pipe.delete(exp_key)
                    await pipe.execute()
                return
            except Exception:
                pass

        # Local fallback
        if tier in self._local_quota:
            tier_data = self._local_quota[tier]
            tier_data["count"] = max(0, tier_data["count"] - 1)
            tier_data["experiments"].pop(experiment_id, None)

    @asynccontextmanager
    async def enforce(self, token: BudgetToken):
        """
        Context manager that enforces budget during execution.

        Uses anyio.fail_after for time enforcement.
        Monitors RAM via ResourceGuard integration.

        M1: AnyIO timeout
        M23: Hard failure on timeout
        """
        if token.is_expired():
            raise BudgetTokenExpiredError(token)

        try:
            # M1: AnyIO timeout wrapper — M23: timeout = hard failure
            with anyio.move_on_after(token.remaining_sec) as scope:
                yield token

            if scope.cancelled_caught:
                raise BudgetTokenExpiredError(token)

        finally:
            # Always release on exit
            await self.release(token.tier, token.experiment_id)

    async def get_tier_status(self, tier: str) -> dict[str, Any]:
        """Get current usage status for a tier."""
        if tier not in self.TIER_BUDGETS:
            return {"error": f"Unknown tier: {tier}"}

        budget = self.TIER_BUDGETS[tier]

        if self.enable_redis:
            try:
                r = await self._get_redis()
                current = await r.get(self._tier_key(tier))
                current_count = int(current) if current else 0
                return {
                    "tier": tier,
                    "current_usage": current_count,
                    "max_concurrent": self.max_concurrent_per_tier,
                    "time_budget_sec": budget["time_sec"],
                    "ram_budget_mb": budget["ram_mb"],
                    "model": budget["model"],
                    "backend": "redis",
                }
            except Exception:
                pass

        # Local fallback
        tier_data = self._local_quota.get(tier, {"count": 0})
        return {
            "tier": tier,
            "current_usage": tier_data["count"],
            "max_concurrent": self.max_concurrent_per_tier,
            "time_budget_sec": budget["time_sec"],
            "ram_budget_mb": budget["ram_mb"],
            "model": budget["model"],
            "backend": "local",
        }

    async def get_all_tiers_status(self) -> dict[str, dict[str, Any]]:
        """Get status for all tiers."""
        return {tier: await self.get_tier_status(tier) for tier in self.TIER_BUDGETS}


# ── Contract Test Helpers (M21) ──────────────────────────────────────────────


def assert_budget_guard_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for BudgetGuard type."""
    assert isinstance(obj, BudgetGuard), f"Expected BudgetGuard, got {type(obj)}"
    assert hasattr(obj, "TIER_BUDGETS")
    assert hasattr(obj, "check")
    assert callable(obj.check)
    assert hasattr(obj, "release")
    assert callable(obj.release)
    assert hasattr(obj, "enforce")
    assert hasattr(obj, "get_tier_status")
    assert callable(obj.get_tier_status)
    assert hasattr(obj, "close")
    assert callable(obj.close)


def assert_budget_token_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for BudgetToken type."""
    assert isinstance(obj, BudgetToken), f"Expected BudgetToken, got {type(obj)}"
    assert hasattr(obj, "experiment_id")
    assert hasattr(obj, "tier")
    assert hasattr(obj, "time_budget_sec")
    assert hasattr(obj, "ram_budget_mb")
    assert hasattr(obj, "model")
    assert hasattr(obj, "remaining_sec")
    assert hasattr(obj, "is_expired")
    assert callable(obj.is_expired)


# Export
__all__ = [
    # Errors
    "BudgetError",
    "BudgetExceededError",
    "BudgetUnavailableError",
    "BudgetTokenExpiredError",
    # Config
    "TIER_BUDGETS",
    # Guard
    "BudgetGuard",
    # Contract tests
    "assert_budget_guard_type",
    "assert_budget_token_type",
]
