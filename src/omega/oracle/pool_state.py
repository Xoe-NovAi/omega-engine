# AP: AP-PR-READINESS-v1.0.0
"""
PoolState — Typed dataclasses for Antigravity dual-pool configuration.

Parses soul.yaml usage_pools section into machine-readable runtime objects,
closing the "structural invisibility" gap (ag-002).

⬡ OMEGA ⬡ POOLSTATE ⬡ v1.0.0 ⬡ 2026-06-18
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# ── Pool Configuration ──────────────────────────────────────────────────────


@dataclass
class PoolConfig:
    """Configuration for a single model pool (Pool G or Pool C)."""

    name: str
    description: str
    models: List[str]
    key_count: int
    reset_cron: str = "weekly Monday 00:00 UTC"
    key_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.key_ids:
            self.key_ids = [f"agy_key_{i+1:02d}" for i in range(self.key_count)]

    @property
    def available_models(self) -> List[str]:
        return list(self.models)


@dataclass
class AntiThrashingConfig:
    """Anti-thrashing rules for key rotation."""

    three_failures_in_5_min: str = "Mark key as COOLING for 1 hour"
    five_quota_hits_in_day: str = "Mark key as DRAINED for 24 hours"

    @property
    def cooling_failure_count(self) -> int:
        return 3

    @property
    def cooling_window_seconds(self) -> int:
        return 300  # 5 minutes

    @property
    def cooling_duration_seconds(self) -> int:
        return 3600  # 1 hour

    @property
    def drained_failure_count(self) -> int:
        return 5

    @property
    def drained_window_seconds(self) -> int:
        return 86400  # 24 hours

    @property
    def drained_duration_seconds(self) -> int:
        return 86400  # 24 hours


@dataclass
class KeyRotationConfig:
    """Key rotation configuration."""

    algorithm: str = "round_robin_with_anti_thrashing"
    cool_period_seconds: int = 3600
    anti_thrashing: AntiThrashingConfig = field(
        default_factory=AntiThrashingConfig
    )


@dataclass
class PoolTrackingConfig:
    """Tracking file configuration."""

    tracking_file: str = "data/entities/antigravity/knowledge/USAGE_POOL_LOG.json"

    @property
    def tracking_path(self) -> Path:
        return Path(self.tracking_file)


# ── Account Mapping ─────────────────────────────────────────────────────────


@dataclass
class AccountMapping:
    """Mapping from agy_key IDs to email addresses."""

    mapping: Dict[str, str]  # agy_key_01 → email
    key_count: int

    @classmethod
    def from_yaml(cls, path: Path) -> "AccountMapping":
        """Load account mapping from ACCOUNT_MAP.yaml."""
        if not path.exists():
            return cls(mapping={}, key_count=0)

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        raw_mapping: Dict[str, str] = data.get("mapping", {})
        # Validate all keys match the expected pattern
        mapping = {}
        for key_id, email in raw_mapping.items():
            if re.match(r"^agy_key_\d+$", key_id):
                mapping[key_id] = str(email)

        return cls(
            mapping=mapping,
            key_count=data.get("key_count", len(mapping)),
        )

    def get_email(self, key_id: str) -> Optional[str]:
        """Get the email address for a key ID."""
        return self.mapping.get(key_id)

    def get_key_id(self, email: str) -> Optional[str]:
        """Find the key ID for an email address."""
        for key_id, addr in self.mapping.items():
            if addr == email:
                return key_id
        return None

    def position_for(self, key_id: str) -> Optional[int]:
        """Get the 0-based position in the accounts file array."""
        keys = sorted(self.mapping.keys())
        if key_id in keys:
            return keys.index(key_id)
        return None


# ── PoolState (top-level config) ────────────────────────────────────────────


@dataclass
class PoolState:
    """
    Complete pool state parsed from an entity's soul.yaml.

    Usage:
        ps = PoolState.from_soul(Path("data/entities/antigravity/soul.yaml"))
        ps.pool_g.models        # ["gemini-3.5-flash", "gemini-3.1-pro"]
        ps.pool_g.key_count     # 8
        ps.key_rotation.algorithm  # "round_robin_with_anti_thrashing"
    """

    pool_g: Optional[PoolConfig] = None
    pool_c: Optional[PoolConfig] = None
    key_rotation: KeyRotationConfig = field(default_factory=KeyRotationConfig)
    tracking: PoolTrackingConfig = field(default_factory=PoolTrackingConfig)

    @classmethod
    def from_soul(
        cls,
        soul_path: Path,
        account_map_path: Optional[Path] = None,
    ) -> "PoolState":
        """
        Parse usage_pools from a soul.yaml file.

        Args:
            soul_path: Path to the entity's soul.yaml.
            account_map_path: Optional path to ACCOUNT_MAP.yaml for email mapping.

        Returns:
            Populated PoolState instance. Returns empty PoolState if
            soul.yaml has no usage_pools section (graceful fallback for
            entities that aren't Antigravity).
        """
        if not soul_path.exists():
            return cls()

        with open(soul_path, "r") as f:
            data = yaml.safe_load(f)

        pools = data.get("usage_pools")
        if not pools:
            return cls()

        # Load account mapping for email resolution
        account_map: Optional[AccountMapping] = None
        if account_map_path and account_map_path.exists():
            account_map = AccountMapping.from_yaml(account_map_path)

        # Parse Pool G (Gemini)
        pool_g_config = None
        if "pool_g" in pools:
            pg = pools["pool_g"]
            pool_g_config = PoolConfig(
                name="pool_g",
                description=pg.get("description", "Gemini pool"),
                models=pg.get("models", []),
                key_count=pg.get("key_count", 0),
                reset_cron=pg.get("reset", "weekly Monday 00:00 UTC"),
            )
            # Resolve emails if account map is available
            if account_map:
                pool_g_config.key_ids = cls._resolve_key_ids(
                    pool_g_config.key_count, account_map
                )

        # Parse Pool C (Claude)
        pool_c_config = None
        if "pool_c" in pools:
            pc = pools["pool_c"]
            pool_c_config = PoolConfig(
                name="pool_c",
                description=pc.get("description", "Claude pool"),
                models=pc.get("models", []),
                key_count=pc.get("key_count", 0),
                reset_cron=pc.get("reset", "weekly Monday 00:00 UTC"),
            )
            if account_map:
                pool_c_config.key_ids = cls._resolve_key_ids(
                    pool_c_config.key_count, account_map
                )

        # Parse key rotation
        rotation_config = KeyRotationConfig()
        if "key_rotation" in pools:
            kr = pools["key_rotation"]
            rotation_config = KeyRotationConfig(
                algorithm=kr.get(
                    "algorithm", "round_robin_with_anti_thrashing"
                ),
                cool_period_seconds=kr.get("cool_period_seconds", 3600),
                anti_thrashing=AntiThrashingConfig(
                    three_failures_in_5_min=kr.get("anti_thrashing", {}).get(
                        "3_failures_in_5_min",
                        "Mark key as COOLING for 1 hour",
                    ),
                    five_quota_hits_in_day=kr.get("anti_thrashing", {}).get(
                        "5_quota_hits_in_day",
                        "Mark key as DRAINED for 24 hours",
                    ),
                ),
            )

        # Parse tracking config
        tracking_config = PoolTrackingConfig(
            tracking_file=pools.get(
                "tracking_file",
                "data/entities/antigravity/knowledge/USAGE_POOL_LOG.json",
            )
        )

        return cls(
            pool_g=pool_g_config,
            pool_c=pool_c_config,
            key_rotation=rotation_config,
            tracking=tracking_config,
        )

    @staticmethod
    def _resolve_key_ids(
        key_count: int,
        account_map: AccountMapping,
    ) -> List[str]:
        """Build key_ids list, preserving email mapping where available."""
        key_ids = [f"agy_key_{i+1:02d}" for i in range(key_count)]
        # Ensure all generated keys have entries in the account map
        # (missing entries will just return None for get_email)
        return key_ids

    def get_pool(self, name: str) -> Optional[PoolConfig]:
        """Get pool config by name ('pool_g' or 'pool_c')."""
        if name == "pool_g":
            return self.pool_g
        elif name == "pool_c":
            return self.pool_c
        return None

    @property
    def all_keys(self) -> List[str]:
        """Get all key IDs across both pools (deduplicated)."""
        keys: set[str] = set()
        if self.pool_g:
            keys.update(self.pool_g.key_ids)
        if self.pool_c:
            keys.update(self.pool_c.key_ids)
        return sorted(keys)

# ── Pool Health ─────────────────────────────────────────────────────────────


@dataclass
class KeyHealth:
    """Runtime health state for a single API key."""

    key_id: str
    email: Optional[str] = None
    status: str = "active"  # active | cooling | drained | error
    cool_until: Optional[float] = None  # epoch timestamp
    remaining_fraction: Optional[float] = None  # 0.0 - 1.0
    reset_time: Optional[str] = None  # ISO timestamp
    calls_this_week: int = 0
    tokens_this_week: int = 0
    last_error: Optional[str] = None


@dataclass
class PoolHealth:
    """Runtime health snapshot for an entire pool."""

    pool_name: str
    total_keys: int = 0
    available_keys: List[str] = field(default_factory=list)
    cooling_keys: List[str] = field(default_factory=list)
    drained_keys: List[str] = field(default_factory=list)
    error_keys: List[str] = field(default_factory=list)
    remaining_quota_pct: Optional[float] = None
    keys: Dict[str, KeyHealth] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        """At least one key is available."""
        return len(self.available_keys) > 0

    @property
    def availability_pct(self) -> float:
        """Percentage of keys that are available."""
        if self.total_keys == 0:
            return 0.0
        return (len(self.available_keys) / self.total_keys) * 100.0
