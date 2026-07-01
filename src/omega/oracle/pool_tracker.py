# AP: AP-PR-READINESS-v1.0.0
"""
UsagePoolTracker — Runtime key rotation, usage tracking, and pool health.

Closes the "phantom tracking" gap (ag-002): USAGE_POOL_LOG.json is now
read and written by this module using atomic JSON writes.

⚠️ D-1 (2026-06-29): Round-robin with anti-thrashing algorithm ERADICATED.
Google bans rapid multi-account switching. This module still contains
anti_thrashing logic that was never wired into any engine component
(confirmed dead code — ag-002). The default algorithm is now "sticky".
When this module is activated, algorithm MUST be verified against the
updated pool_state.py default.

⬡ OMEGA ⬡ POOLTRACKER ⬡ v1.0.0 ⬡ 2026-06-18
D-1 NOTICE: 2026-06-29 — anti_thrashing refers to removed algorithm
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import anyio

from omega.oracle.pool_state import (
    AccountMapping,
    KeyHealth,
    PoolConfig,
    PoolHealth,
    PoolState,
)


# ── Tracking Record Types ───────────────────────────────────────────────────


@dataclass
class KeyUsageRecord:
    """Per-key usage record stored in USAGE_POOL_LOG.json."""

    key_id: str
    email: Optional[str] = None
    status: str = "active"  # active | cooling | drained | error
    cool_until: Optional[float] = None  # epoch ms
    last_used_at: Optional[float] = None  # epoch ms
    last_model_used: Optional[str] = None
    last_error: Optional[str] = None

    # Pool G (Gemini) usage
    pool_g_calls: int = 0
    pool_g_tokens: int = 0
    pool_g_quota_hit_at: Optional[float] = None
    pool_g_failures: List[float] = field(default_factory=list)  # timestamps
    pool_g_remaining_fraction: Optional[float] = None
    pool_g_reset_time: Optional[str] = None

    # Pool C (Claude) usage
    pool_c_calls: int = 0
    pool_c_tokens: int = 0
    pool_c_quota_hit_at: Optional[float] = None
    pool_c_failures: List[float] = field(default_factory=list)
    pool_c_remaining_fraction: Optional[float] = None
    pool_c_reset_time: Optional[str] = None

    # Thinking levels used
    low_calls: int = 0
    medium_calls: int = 0
    high_calls: int = 0


@dataclass
class PoolTrackingData:
    """Top-level tracking data structure for USAGE_POOL_LOG.json."""

    schema_version: str = "2.0"
    last_updated: str = ""
    weekly_reset_date: str = ""
    keys: Dict[str, KeyUsageRecord] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dict for JSON export."""
        result = {
            "schema_version": self.schema_version,
            "last_updated": self.last_updated,
            "weekly_reset_date": self.weekly_reset_date,
            "keys": [],
        }
        for key_id in sorted(self.keys.keys()):
            record = self.keys[key_id]
            key_dict = asdict(record)
            key_dict["key_id"] = key_id
            result["keys"].append(key_dict)
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "PoolTrackingData":
        """Deserialize from a dict loaded from JSON."""
        tracking = cls(
            schema_version=data.get("schema_version", "2.0"),
            last_updated=data.get("last_updated", ""),
            weekly_reset_date=data.get("weekly_reset_date", ""),
        )
        for key_entry in data.get("keys", []):
            key_id = key_entry.pop("key_id")
            record = KeyUsageRecord(
                key_id=key_id,
                email=key_entry.get("email"),
                status=key_entry.get("status", "active"),
                cool_until=key_entry.get("cool_until"),
                last_used_at=key_entry.get("last_used_at"),
                last_model_used=key_entry.get("last_model_used"),
                last_error=key_entry.get("last_error"),
                pool_g_calls=key_entry.get("pool_g_calls", 0),
                pool_g_tokens=key_entry.get("pool_g_tokens", 0),
                pool_g_quota_hit_at=key_entry.get("pool_g_quota_hit_at"),
                pool_g_failures=key_entry.get("pool_g_failures", []),
                pool_g_remaining_fraction=key_entry.get(
                    "pool_g_remaining_fraction"
                ),
                pool_g_reset_time=key_entry.get("pool_g_reset_time"),
                pool_c_calls=key_entry.get("pool_c_calls", 0),
                pool_c_tokens=key_entry.get("pool_c_tokens", 0),
                pool_c_quota_hit_at=key_entry.get("pool_c_quota_hit_at"),
                pool_c_failures=key_entry.get("pool_c_failures", []),
                pool_c_remaining_fraction=key_entry.get(
                    "pool_c_remaining_fraction"
                ),
                pool_c_reset_time=key_entry.get("pool_c_reset_time"),
                low_calls=key_entry.get("low_calls", 0),
                medium_calls=key_entry.get("medium_calls", 0),
                high_calls=key_entry.get("high_calls", 0),
            )
            tracking.keys[key_id] = record
        return tracking


# ── UsagePoolTracker ────────────────────────────────────────────────────────


class UsagePoolTracker:
    """
    Runtime tracker for Antigravity dual-pool usage.

    Reads/writes USAGE_POOL_LOG.json with atomic patterns.
    Provides pool health queries and key rotation.

    Usage:
        tracker = UsagePoolTracker(
            pool_state=PoolState.from_soul(soul_path)
        )
        await tracker.load()
        health = await tracker.get_pool_health("pool_g")
        next_key = await tracker.select_key("pool_g", "gemini-3.5-flash")
        await tracker.track_usage(
            "pool_g", "gemini-3.5-flash", "agy_key_03",
            tokens=45000, success=True
        )
    """

    def __init__(
        self,
        pool_state: PoolState,
        tracking_path: Optional[Path] = None,
        account_map_path: Optional[Path] = None,
    ) -> None:
        self.pool_state = pool_state
        self._tracking_path = (
            tracking_path
            or pool_state.tracking.tracking_path
        )
        self._account_map: Optional[AccountMapping] = None
        if account_map_path and account_map_path.exists():
            self._account_map = AccountMapping.from_yaml(account_map_path)
        self._data: PoolTrackingData = PoolTrackingData()
        self._loaded = False

    # ── Loading / Saving ────────────────────────────────────────────────

    async def load(self) -> None:
        """Load tracking data from disk. Creates default if missing."""
        path = Path(self._tracking_path)
        if path.exists():
            def _read():
                with open(path, "r") as f:
                    return json.load(f)

            raw = await anyio.to_thread.run_sync(_read)
            self._data = PoolTrackingData.from_dict(raw)
        else:
            # Initialize from pool_state config
            self._data = PoolTrackingData(
                schema_version="2.0",
                last_updated=time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
            )
            for key_id in self.pool_state.all_keys:
                email = None
                if self._account_map:
                    email = self._account_map.get_email(key_id)
                self._data.keys[key_id] = KeyUsageRecord(
                    key_id=key_id,
                    email=email,
                    status="active",
                )
            await self._save()

        self._loaded = True

    async def _save(self) -> None:
        """Atomic write to USAGE_POOL_LOG.json."""
        self._data.last_updated = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        )
        path = Path(self._tracking_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = path.with_suffix(".tmp")

        def _write():
            with open(tmp_path, "w") as f:
                json.dump(self._data.to_dict(), f, indent=2, default=str)
            tmp_path.replace(path)

        await anyio.to_thread.run_sync(_write)

    # ── Usage Tracking ──────────────────────────────────────────────────

    async def track_usage(
        self,
        pool: str,
        model: str,
        key_id: str,
        tokens: int = 0,
        success: bool = True,
        thinking_level: Optional[str] = None,
        remaining_fraction: Optional[float] = None,
        reset_time: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Record an API call for a specific key.

        Args:
            pool: "pool_g" or "pool_c"
            model: Model name used (e.g. "gemini-3.5-flash")
            key_id: Key ID (e.g. "agy_key_03")
            tokens: Tokens consumed
            success: True if the API call succeeded
            thinking_level: "low", "medium", or "high"
            remaining_fraction: Quota remaining (0.0-1.0) from fetchAvailableModels
            reset_time: ISO timestamp of quota reset
            error: Error message if failed
        """
        if not self._loaded:
            await self.load()

        record = self._data.keys.get(key_id)
        if not record:
            # Auto-create record for unknown keys
            email = None
            if self._account_map:
                email = self._account_map.get_email(key_id)
            record = KeyUsageRecord(key_id=key_id, email=email)
            self._data.keys[key_id] = record

        now = time.time() * 1000  # epoch ms
        record.last_used_at = now
        record.last_model_used = model

        if success:
            if pool == "pool_g":
                record.pool_g_calls += 1
                record.pool_g_tokens += tokens
                if remaining_fraction is not None:
                    record.pool_g_remaining_fraction = remaining_fraction
                if reset_time:
                    record.pool_g_reset_time = reset_time
            elif pool == "pool_c":
                record.pool_c_calls += 1
                record.pool_c_tokens += tokens
                if remaining_fraction is not None:
                    record.pool_c_remaining_fraction = remaining_fraction
                if reset_time:
                    record.pool_c_reset_time = reset_time

            # Track thinking level
            if thinking_level:
                if thinking_level == "low":
                    record.low_calls += 1
                elif thinking_level == "medium":
                    record.medium_calls += 1
                elif thinking_level == "high":
                    record.high_calls += 1

            # Check if key was in cooling — mark it available again
            if record.status in ("cooling", "drained") and self._is_cool_expired(record):
                record.status = "active"
                record.cool_until = None
        else:
            # Track failure
            if pool == "pool_g":
                record.pool_g_failures.append(now)
                # Prune old failures outside the anti-thrashing window
                window = self.pool_state.key_rotation.anti_thrashing.cooling_window_seconds * 1000
                cutoff = now - window
                record.pool_g_failures = [t for t in record.pool_g_failures if t >= cutoff]
                record.pool_g_quota_hit_at = now
            elif pool == "pool_c":
                record.pool_c_failures.append(now)
                window = self.pool_state.key_rotation.anti_thrashing.cooling_window_seconds * 1000
                cutoff = now - window
                record.pool_c_failures = [t for t in record.pool_c_failures if t >= cutoff]
                record.pool_c_quota_hit_at = now

            record.last_error = error

            # Apply anti-thrashing: check if key should be cooled or drained
            self._apply_anti_thrashing(record, pool)

        await self._save()

    def _is_cool_expired(self, record: KeyUsageRecord) -> bool:
        """Check if a cooling/drained key has expired its cooldown."""
        if record.cool_until is None:
            return True
        return (time.time() * 1000) >= record.cool_until

    def _apply_anti_thrashing(
        self, record: KeyUsageRecord, pool: str
    ) -> None:
        """
        Apply anti-thrashing rules to a failed key.

        3 failures in 5 min → COOLING for 1 hour
        5 quota hits in day → DRAINED for 24 hours
        """
        failures = (
            record.pool_g_failures
            if pool == "pool_g"
            else record.pool_c_failures
        )
        now = time.time() * 1000

        # Check DRAINED first (5 quota hits in day)
        drained_count = self.pool_state.key_rotation.anti_thrashing.drained_failure_count
        drained_window = self.pool_state.key_rotation.anti_thrashing.drained_window_seconds * 1000
        recent_failures = [t for t in failures if (now - t) <= drained_window]
        if len(recent_failures) >= drained_count:
            record.status = "drained"
            record.cool_until = now + (
                self.pool_state.key_rotation.anti_thrashing.drained_duration_seconds * 1000
            )
            return

        # Check COOLING (3 failures in 5 min)
        cooling_count = self.pool_state.key_rotation.anti_thrashing.cooling_failure_count
        cooling_window = self.pool_state.key_rotation.anti_thrashing.cooling_window_seconds * 1000
        recent = [t for t in failures if (now - t) <= cooling_window]
        if len(recent) >= cooling_count:
            record.status = "cooling"
            record.cool_until = now + (
                self.pool_state.key_rotation.anti_thrashing.cooling_duration_seconds * 1000
            )

    # ── Pool Health ─────────────────────────────────────────────────────

    async def get_pool_health(self, pool: str) -> PoolHealth:
        """
        Get current health snapshot for a pool.

        Args:
            pool: "pool_g" or "pool_c"

        Returns:
            PoolHealth with available/cooling/drained key lists.
        """
        if not self._loaded:
            await self.load()

        pool_config = self.pool_state.get_pool(pool)
        if not pool_config:
            return PoolHealth(pool_name=pool)

        health = PoolHealth(
            pool_name=pool,
            total_keys=pool_config.key_count,
        )

        # Refresh cooling/drained state (time-based expiry)
        for key_id in pool_config.key_ids:
            record = self._data.keys.get(key_id)
            if not record:
                continue

            # Check if cooling has expired
            if record.status in ("cooling", "drained") and self._is_cool_expired(record):
                record.status = "active"
                record.cool_until = None

            key_health = KeyHealth(
                key_id=key_id,
                email=record.email,
                status=record.status,
                cool_until=record.cool_until,
                calls_this_week=(
                    record.pool_g_calls
                    if pool == "pool_g"
                    else record.pool_c_calls
                ),
                tokens_this_week=(
                    record.pool_g_tokens
                    if pool == "pool_g"
                    else record.pool_c_tokens
                ),
                remaining_fraction=(
                    record.pool_g_remaining_fraction
                    if pool == "pool_g"
                    else record.pool_c_remaining_fraction
                ),
                reset_time=(
                    record.pool_g_reset_time
                    if pool == "pool_g"
                    else record.pool_c_reset_time
                ),
                last_error=record.last_error,
            )

            if record.status == "cooling":
                health.cooling_keys.append(key_id)
            elif record.status == "drained":
                health.drained_keys.append(key_id)
            elif record.status == "error":
                health.error_keys.append(key_id)
            else:
                health.available_keys.append(key_id)

            health.keys[key_id] = key_health

        # Calculate remaining quota percentage across the pool
        remaining = [
            k.remaining_fraction
            for k in health.keys.values()
            if k.remaining_fraction is not None
        ]
        if remaining:
            health.remaining_quota_pct = (
                sum(remaining) / len(remaining)
            ) * 100.0

        return health

    # ── Key Selection ───────────────────────────────────────────────────

    async def select_key(
        self,
        pool: str,
        model: Optional[str] = None,
        preferred_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Select the best key for a model in the given pool.

        Implements round_robin_with_anti_thrashing:
        1. Preferred key if available (for prompt cache stickiness)
        2. Available keys sorted by remaining quota (highest first)
        3. Any available key

        Args:
            pool: "pool_g" or "pool_c"
            model: Model name to route (for model-specific pool matching)
            preferred_key: Preferred key ID (for stickiness)

        Returns:
            Key ID to use, or None if no keys are available.
        """
        health = await self.get_pool_health(pool)
        if not health.is_healthy:
            return None

        # If preferred key is available, use it (stickiness)
        if preferred_key and preferred_key in health.available_keys:
            return preferred_key

        # Sort available keys by remaining quota (highest first)
        available_with_quota = []
        for key_id in health.available_keys:
            kh = health.keys.get(key_id)
            remaining = kh.remaining_fraction if kh else None
            available_with_quota.append((key_id, remaining or 0.0))

        available_with_quota.sort(key=lambda x: x[1], reverse=True)

        if available_with_quota:
            return available_with_quota[0][0]

        return None

    # ── Batch Quota Update ──────────────────────────────────────────────

    async def update_quota_from_check(
        self, quota_results: List[dict]
    ) -> None:
        """
        Batch update quota data from check-quota results.

        Args:
            quota_results: List of dicts with keys:
                - position (int): 0-based position in accounts file
                - email (str): Account email
                - groups (dict): Per-model-family quota data
                    e.g. {"gemini-flash": {"remaining": 0.6, "resetTime": "..."}}
        """
        if not self._loaded:
            await self.load()

        key_ids = self.pool_state.all_keys

        for result in quota_results:
            position = result.get("position", 0)
            if position >= len(key_ids):
                continue

            key_id = key_ids[position]
            record = self._data.keys.get(key_id)
            if not record:
                record = KeyUsageRecord(key_id=key_id, email=result.get("email"))
                self._data.keys[key_id] = record

            record.email = result.get("email") or record.email

            # Update Pool G quota from gemini-flash / gemini-pro
            groups = result.get("groups", {})
            for group_name in ("gemini-flash", "gemini-pro"):
                group_data = groups.get(group_name, {})
                remaining = group_data.get("remaining")
                reset_time = group_data.get("resetTime")
                if remaining is not None:
                    # Take the minimum across models in the pool
                    current = record.pool_g_remaining_fraction
                    if current is None or remaining < current:
                        record.pool_g_remaining_fraction = remaining
                if reset_time:
                    record.pool_g_reset_time = reset_time

            # Update Pool C quota from claude
            claude_data = groups.get("claude", {})
            if claude_data:
                remaining = claude_data.get("remaining")
                reset_time = claude_data.get("resetTime")
                if remaining is not None:
                    current = record.pool_c_remaining_fraction
                    if current is None or remaining < current:
                        record.pool_c_remaining_fraction = remaining
                if reset_time:
                    record.pool_c_reset_time = reset_time

        await self._save()

    # ── Utilities ───────────────────────────────────────────────────────

    async def reset_weekly(self) -> None:
        """Reset weekly counters (should be called Monday 00:00 UTC)."""
        if not self._loaded:
            await self.load()

        for record in self._data.keys.values():
            record.pool_g_calls = 0
            record.pool_g_tokens = 0
            record.pool_g_failures = []
            record.pool_c_calls = 0
            record.pool_c_tokens = 0
            record.pool_c_failures = []
            record.low_calls = 0
            record.medium_calls = 0
            record.high_calls = 0
            record.status = "active"
            record.cool_until = None

        self._data.weekly_reset_date = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        )
        await self._save()

    async def get_tracking_summary(self) -> dict:
        """Get a human-readable summary of tracking data."""
        if not self._loaded:
            await self.load()

        total_keys = len(self._data.keys)
        active = sum(
            1 for r in self._data.keys.values() if r.status == "active"
        )
        cooling = sum(
            1 for r in self._data.keys.values() if r.status == "cooling"
        )
        drained = sum(
            1 for r in self._data.keys.values() if r.status == "drained"
        )

        pool_g_total_calls = sum(
            r.pool_g_calls for r in self._data.keys.values()
        )
        pool_g_total_tokens = sum(
            r.pool_g_tokens for r in self._data.keys.values()
        )
        pool_c_total_calls = sum(
            r.pool_c_calls for r in self._data.keys.values()
        )
        pool_c_total_tokens = sum(
            r.pool_c_tokens for r in self._data.keys.values()
        )

        return {
            "total_keys": total_keys,
            "active": active,
            "cooling": cooling,
            "drained": drained,
            "pool_g_calls": pool_g_total_calls,
            "pool_g_tokens": pool_g_total_tokens,
            "pool_c_calls": pool_c_total_calls,
            "pool_c_tokens": pool_c_total_tokens,
            "last_updated": self._data.last_updated,
            "weekly_reset": self._data.weekly_reset_date,
        }
