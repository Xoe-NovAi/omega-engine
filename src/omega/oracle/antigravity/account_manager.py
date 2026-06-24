# AP: AP-PR-READINESS-v1.0.0
# ── Antigravity Account Manager ──
# Port of the plugin's AccountManager (TypeScript → Python).
# Handles account loading, selection, rate limit tracking, and cooldown management.
# [Mandate 16: Modularization & Portability] — config-driven, no hardcoded paths.

"""Account manager for the Antigravity module.

Manages 8 Google accounts with per-family (claude/gemini) sticky rotation,
rate limit tracking, and cooldown management. Reads from the plugin's
`antigravity-accounts.json` file.

Key constraints:
- NEVER auto-rotated by the gateway search order (Google ban detection)
- Only invoked explicitly when the gateway determines it's the right backend
- Anti-thrashing: 3 failures/5min → 1hr cooldown, 5 quota/day → 24hr drain
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import AntigravityConfig
from .client import (
    AntigravityRateLimitError,
    classify_rate_limit_reason,
    calculate_backoff_ms,
)

logger = logging.getLogger(__name__)

# Anti-thrashing constants (from soul.yaml §PoolStateWiring)
_COOLING_FAILURE_COUNT = 3
_COOLING_WINDOW_S = 300  # 5 minutes
_COOLING_DURATION_S = 3600  # 1 hour

# Cooldown reasons
CooldownReason = str  # "rate_limit" | "quota_exhausted" | "server_error"


@dataclass
class ManagedAccount:
    """A managed Antigravity account with runtime state."""

    index: int
    email: str
    refresh_token: str
    project_id: Optional[str] = None
    managed_project_id: Optional[str] = None
    added_at: float = 0.0
    last_used: float = 0.0
    enabled: bool = True

    # Rate limit tracking: quota_key -> reset_timestamp
    rate_limit_reset_times: Dict[str, float] = field(default_factory=dict)

    # Cooldown tracking
    cooling_down_until: Optional[float] = None
    cooldown_reason: Optional[CooldownReason] = None

    # Failure tracking
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None

    # Cached quota data
    cached_quota: Optional[Dict[str, Any]] = None
    cached_quota_updated_at: Optional[float] = None

    @property
    def is_cooling_down(self) -> bool:
        if self.cooling_down_until is None:
            return False
        if time.time() >= self.cooling_down_until:
            self.cooling_down_until = None
            self.cooldown_reason = None
            return False
        return True

    def is_rate_limited(self, quota_key: str) -> bool:
        """Check if this account is rate-limited for a specific quota key."""
        self._clear_expired_rate_limits()
        reset_time = self.rate_limit_reset_times.get(quota_key)
        return reset_time is not None and time.time() < reset_time

    def is_rate_limited_for_family(self, family: str, model: Optional[str] = None) -> bool:
        """Check if this account is rate-limited for a model family."""
        if family == "claude":
            return self.is_rate_limited("claude")
        # For gemini, check both antigravity and gemini-cli pools
        ag_key = _get_quota_key(family, "antigravity", model)
        cli_key = _get_quota_key(family, "gemini-cli", model)
        return self.is_rate_limited(ag_key) and self.is_rate_limited(cli_key)

    def _clear_expired_rate_limits(self) -> None:
        now = time.time()
        expired = [k for k, v in self.rate_limit_reset_times.items() if now >= v]
        for k in expired:
            del self.rate_limit_reset_times[k]

    def mark_rate_limited(self, quota_key: str, retry_after_ms: int) -> None:
        """Mark this account as rate-limited for a quota key."""
        self.rate_limit_reset_times[quota_key] = time.time() + (retry_after_ms / 1000)

    def mark_rate_limited_with_reason(
        self, family: str, header_style: str, model: Optional[str],
        reason: str, retry_after_ms: Optional[int] = None,
    ) -> int:
        """Mark rate limit with reason-based backoff. Returns the backoff in ms."""
        now = time.time()
        # TTL-based reset: if last failure was > 1hr ago, reset count
        if self.last_failure_time and (now - self.last_failure_time) > 3600:
            self.consecutive_failures = 0

        self.consecutive_failures += 1
        self.last_failure_time = now

        backoff_ms = calculate_backoff_ms(reason, self.consecutive_failures - 1, retry_after_ms)
        key = _get_quota_key(family, header_style, model)
        self.rate_limit_reset_times[key] = now + (backoff_ms / 1000)
        return backoff_ms

    def mark_success(self) -> None:
        """Mark a successful request — resets consecutive failures."""
        self.consecutive_failures = 0

    def mark_cooling_down(self, duration_ms: int, reason: CooldownReason) -> None:
        """Put this account into cooldown."""
        self.cooling_down_until = time.time() + (duration_ms / 1000)
        self.cooldown_reason = reason

    def clear_cooling_down(self) -> None:
        """Clear cooldown."""
        self.cooling_down_until = None
        self.cooldown_reason = None


@dataclass
class AccountSelection:
    """Result of account selection."""

    account: ManagedAccount
    header_style: str  # "antigravity" | "gemini-cli"
    family: str  # "claude" | "gemini"


def _get_quota_key(family: str, header_style: str, model: Optional[str] = None) -> str:
    """Build a quota key from family, header style, and optional model."""
    if family == "claude":
        return "claude"
    base = "gemini-cli" if header_style == "gemini-cli" else "gemini-antigravity"
    if model:
        return f"{base}:{model}"
    return base


class AccountManager:
    """Multi-account manager with sticky and round-robin selection.

    Reads from the plugin's `antigravity-accounts.json` file.
    Manages per-family (claude/gemini) account rotation with rate limit
    tracking and cooldown management.
    """

    def __init__(self, config: Optional[AntigravityConfig] = None) -> None:
        self._config = config or AntigravityConfig()
        self._accounts: List[ManagedAccount] = []
        self._cursor = 0
        self._current_index_by_family: Dict[str, int] = {"claude": 0, "gemini": 0}
        self._loaded = False

    @property
    def account_count(self) -> int:
        return len([a for a in self._accounts if a.enabled])

    @property
    def all_accounts(self) -> List[ManagedAccount]:
        return list(self._accounts)

    @property
    def enabled_accounts(self) -> List[ManagedAccount]:
        return [a for a in self._accounts if a.enabled]

    async def load(self) -> None:
        """Load accounts from disk. Must be called before select_account()."""
        if self._loaded:
            return

        accounts_path = self._config.accounts_path
        if not accounts_path.exists():
            logger.warning("Antigravity accounts file not found at %s", accounts_path)
            self._loaded = True
            return

        try:
            with open(accounts_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load accounts from %s: %s", accounts_path, e)
            self._loaded = True
            return

        version = data.get("version", 0)
        if version < 4:
            logger.warning("Accounts file version %d is outdated — expected v4", version)

        raw_accounts = data.get("accounts", [])
        self._accounts = []
        for i, acc in enumerate(raw_accounts):
            refresh_token = acc.get("refreshToken", "")
            if not refresh_token:
                logger.warning("Account %d has no refresh token — skipping", i)
                continue

            self._accounts.append(ManagedAccount(
                index=i,
                email=acc.get("email", f"unknown-{i}"),
                refresh_token=refresh_token,
                project_id=acc.get("projectId"),
                managed_project_id=acc.get("managedProjectId"),
                added_at=acc.get("addedAt", 0),
                last_used=acc.get("lastUsed", 0),
                enabled=acc.get("enabled", True),
            ))

        # Set active indices
        active_index = data.get("activeIndex", 0)
        active_by_family = data.get("activeIndexByFamily", {})
        n = len(self._accounts) or 1
        self._cursor = active_index % n
        self._current_index_by_family["claude"] = active_by_family.get("claude", 0) % n
        self._current_index_by_family["gemini"] = active_by_family.get("gemini", 0) % n

        self._loaded = True
        logger.info("Loaded %d Antigravity accounts from %s", len(self._accounts), accounts_path)

    def select_account(
        self,
        family: str,
        model: Optional[str] = None,
    ) -> Optional[AccountSelection]:
        """Select the best account for a model family.

        Args:
            family: "claude" or "gemini"
            model: Optional model name for model-specific rate limits

        Returns:
            AccountSelection or None if no accounts available.
        """
        if not self._loaded:
            raise RuntimeError("AccountManager.load() must be called before select_account()")

        enabled = [a for a in self._accounts if a.enabled]
        if not enabled:
            return None

        return self._select_sticky(family, model, enabled)

    def _select_sticky(
        self, family: str, model: Optional[str], enabled: List[ManagedAccount],
    ) -> Optional[AccountSelection]:
        """Sticky selection: use current account until rate-limited, then find next."""
        current_idx = self._current_index_by_family.get(family, 0)
        current = self._accounts[current_idx] if current_idx < len(self._accounts) else None

        if current and current.enabled:
            if not current.is_rate_limited_for_family(family, model) and not current.is_cooling_down:
                header = self._get_best_header_style(current, family, model)
                if header:
                    return AccountSelection(account=current, header_style=header, family=family)

        # Current account is rate-limited — find next
        return self._find_next_available(family, model, enabled)

    def _find_next_available(
        self, family: str, model: Optional[str], enabled: List[ManagedAccount],
    ) -> Optional[AccountSelection]:
        """Find the next available account for a family."""
        for _ in range(len(enabled)):
            self._cursor = (self._cursor + 1) % len(self._accounts)
            account = self._accounts[self._cursor]
            if not account.enabled:
                continue
            if account.is_rate_limited_for_family(family, model):
                continue
            if account.is_cooling_down:
                continue
            header = self._get_best_header_style(account, family, model)
            if header:
                self._current_index_by_family[family] = account.index
                return AccountSelection(account=account, header_style=header, family=family)

        return None

    def _get_best_header_style(
        self, account: ManagedAccount, family: str, model: Optional[str],
    ) -> Optional[str]:
        """Determine the best header style for an account/family/model."""
        if family == "claude":
            return "antigravity" if not account.is_rate_limited("claude") else None

        # For Gemini, prefer antigravity, fall back to gemini-cli
        ag_key = _get_quota_key(family, "antigravity", model)
        if not account.is_rate_limited(ag_key):
            return "antigravity"

        cli_key = _get_quota_key(family, "gemini-cli", model)
        if not account.is_rate_limited(cli_key):
            return "gemini-cli"

        return None

    def handle_rate_limit(
        self, account: ManagedAccount, family: str, model: Optional[str],
        error: AntigravityRateLimitError,
    ) -> None:
        """Handle a rate limit error for an account."""
        reason = classify_rate_limit_reason(error.status_code, str(error))
        backoff_ms = account.mark_rate_limited_with_reason(
            family=family,
            header_style="antigravity",
            model=model,
            reason=reason,
            retry_after_ms=error.retry_after_ms,
        )
        logger.warning(
            "Account %s rate-limited: %s (backoff=%dms, failures=%d)",
            account.email, reason, backoff_ms, account.consecutive_failures,
        )

        # Check if we should enter anti-thrashing cooldown
        if account.consecutive_failures >= _COOLING_FAILURE_COUNT:
            window = time.time() - (account.last_failure_time or 0)
            if window <= _COOLING_WINDOW_S:
                account.mark_cooling_down(_COOLING_DURATION_S * 1000, reason)
                logger.warning(
                    "Account %s entering cooldown for %ds (reason=%s)",
                    account.email, _COOLING_DURATION_S, reason,
                )

    def mark_used(self, account: ManagedAccount) -> None:
        """Mark an account as used after a successful request."""
        account.last_used = time.time()
        account.mark_success()

    def get_min_wait_ms(self, family: str, model: Optional[str] = None) -> int:
        """Get minimum wait time in ms until any account is available."""
        enabled = self.enabled_accounts
        if not enabled:
            return 0

        # If any account is available, no wait needed
        for a in enabled:
            if not a.is_rate_limited_for_family(family, model) and not a.is_cooling_down:
                return 0

        # Find earliest reset time
        wait_times = []
        for a in enabled:
            if family == "claude":
                reset_time = a.rate_limit_reset_times.get("claude")
            else:
                ag_key = _get_quota_key(family, "antigravity", model)
                cli_key = _get_quota_key(family, "gemini-cli", model)
                t1 = a.rate_limit_reset_times.get(ag_key)
                t2 = a.rate_limit_reset_times.get(cli_key)
                reset_time = min(
                    (t for t in [t1, t2] if t is not None),
                    default=None,
                )
            if reset_time:
                wait = max(0, (reset_time - time.time()) * 1000)
                wait_times.append(wait)

        return int(min(wait_times)) if wait_times else 0
