"""
Headless Subagent Pool — Account Registry

Manages 24 accounts with health tracking, rate limits, and credential integration.

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ ACCOUNT_REGISTRY
"""

from __future__ import annotations

import anyio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .models import (
    Account,
    AccountHealth,
    PoolHealthReport,
    PoolStatus,
    PoolType,
    RebalanceReport,
)

logger = logging.getLogger(__name__)


class AccountRegistry:
    """
    Manages the pool of 24 CLI agent accounts with health tracking,
    rate limiting, and credential integration via Omega-Vault.
    """

    def __init__(
        self,
        registry_path: Path | None = None,
        vault_client: Any = None,
    ):
        self._accounts: dict[str, Account] = {}
        self._lock = anyio.Lock()
        self._registry_path = registry_path or Path("data/state/subagent_pool_registry.json")
        self._vault_client = vault_client
        self._health_check_interval = 60  # seconds
        self._rate_limit_window = 60  # seconds

    async def initialize(self, mock_data: bool = True) -> None:
        """Initialize the registry, loading from disk or creating mock data."""
        async with self._lock:
            if self._registry_path.exists() and not mock_data:
                await self._load_from_disk()
            elif mock_data:
                await self._create_mock_accounts()
                await self._persist()

    async def _create_mock_accounts(self) -> None:
        """Create 24 mock accounts (8 per pool) for development."""
        # Grok CLI - 8 accounts
        grok_models = ["grok-3", "grok-2", "grok-1.5"]
        grok_contexts = [1_000_000, 128_000, 128_000]
        grok_caps = {"web_search", "reasoning", "synthesis"}

        for i in range(1, 9):
            model_idx = (i - 1) % 3
            account = Account(
                id=f"grok-cli-{i}",
                pool=PoolType.GROK,
                model=grok_models[model_idx],
                context_window=grok_contexts[model_idx],
                credentials_ref=f"vault:grok/cli-{i}",
                capabilities=grok_caps.copy(),
                rate_limit_remaining=100,
                rate_limit_reset=datetime.now() + timedelta(minutes=5),
            )
            self._accounts[account.id] = account

        # Copilot CLI - 8 accounts
        copilot_models = ["gpt-4o", "gpt-4o-mini", "o1"]
        copilot_contexts = [128_000, 128_000, 128_000]
        copilot_caps = {"code_gen", "code_review", "reasoning"}

        for i in range(1, 9):
            model_idx = (i - 1) % 3
            account = Account(
                id=f"copilot-cli-{i}",
                pool=PoolType.COPILOT,
                model=copilot_models[model_idx],
                context_window=copilot_contexts[model_idx],
                credentials_ref=f"vault:copilot/cli-{i}",
                capabilities=copilot_caps.copy(),
                rate_limit_remaining=50,
                rate_limit_reset=datetime.now() + timedelta(minutes=10),
            )
            self._accounts[account.id] = account

        # Cline CLI - 8 accounts
        cline_models = ["deepseek-v4-flash", "mimo-v2.5", "claude-3.5-sonnet", "gpt-4o"]
        cline_contexts = [1_000_000, 512_000, 200_000, 128_000]
        cline_caps = {"deep_research", "large_refactor", "code_gen", "reasoning"}

        for i in range(1, 9):
            model_idx = (i - 1) % 4
            account = Account(
                id=f"cline-cli-{i}",
                pool=PoolType.CLINE,
                model=cline_models[model_idx],
                context_window=cline_contexts[model_idx],
                credentials_ref=f"vault:cline/cli-{i}",
                capabilities=cline_caps.copy(),
                rate_limit_remaining=200,
                rate_limit_reset=datetime.now() + timedelta(minutes=3),
            )
            self._accounts[account.id] = account

        logger.info(f"Created {len(self._accounts)} mock accounts")

    async def _load_from_disk(self) -> None:
        """Load account registry from JSON file."""
        try:
            content = await anyio.to_thread.run_sync(self._registry_path.read_text)
            data = json.loads(content)
            for acc_data in data.get("accounts", []):
                account = Account(**acc_data)
                self._accounts[account.id] = account
            logger.info(f"Loaded {len(self._accounts)} accounts from registry")
        except Exception as e:
            logger.warning(f"Failed to load registry: {e}, creating mock data")
            await self._create_mock_accounts()

    async def _persist(self) -> None:
        """Persist account registry to JSON file."""
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "accounts": [
                {
                    "id": acc.id,
                    "pool": acc.pool.value,
                    "model": acc.model,
                    "context_window": acc.context_window,
                    "health": acc.health.value,
                    "rate_limit_remaining": acc.rate_limit_remaining,
                    "rate_limit_reset": acc.rate_limit_reset.isoformat()
                    if acc.rate_limit_reset
                    else None,
                    "last_used": acc.last_used.isoformat() if acc.last_used else None,
                    "credentials_ref": acc.credentials_ref,
                    "capabilities": list(acc.capabilities),
                    "tmux_session": acc.tmux_session,
                    "mcp_endpoint": acc.mcp_endpoint,
                    "created_at": acc.created_at.isoformat(),
                    "updated_at": acc.updated_at.isoformat(),
                }
                for acc in self._accounts.values()
            ],
            "updated_at": datetime.now().isoformat(),
        }
        await anyio.to_thread.run_sync(
            self._registry_path.write_text,
            json.dumps(data, indent=2),
        )

    # --- Public API ---

    async def get_available(
        self,
        pool: PoolType | None = None,
        min_context: int = 0,
        required_capabilities: set[str] | None = None,
    ) -> list[Account]:
        """Get healthy accounts with sufficient context and capabilities."""
        async with self._lock:
            available = []
            for account in self._accounts.values():
                if pool and account.pool != pool:
                    continue
                if not account.is_available(min_context):
                    continue
                if required_capabilities and not required_capabilities.issubset(
                    account.capabilities
                ):
                    continue
                available.append(account)

            # Sort by least recently used (LRU)
            available.sort(key=lambda a: a.last_used or datetime.min)
            return available

    async def get_least_loaded(self, pool: PoolType) -> Account | None:
        """Get the least recently used healthy account in a pool."""
        available = await self.get_available(pool=pool)
        return available[0] if available else None

    async def get_account(self, account_id: str) -> Account | None:
        """Get a specific account by ID."""
        async with self._lock:
            return self._accounts.get(account_id)

    async def get_all_accounts(self, pool: PoolType | None = None) -> list[Account]:
        """Get all accounts, optionally filtered by pool."""
        async with self._lock:
            accounts = list(self._accounts.values())
            if pool:
                accounts = [a for a in accounts if a.pool == pool]
            return accounts

    async def mark_rate_limited(self, account_id: str, retry_after: int) -> None:
        """Mark an account as rate limited with retry timestamp."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.health = AccountHealth.RATE_LIMITED
                account.rate_limit_remaining = 0
                account.rate_limit_reset = datetime.now() + timedelta(seconds=retry_after)
                account.updated_at = datetime.now()
                await self._persist()
                logger.warning(f"Account {account_id} rate limited, retry after {retry_after}s")

    async def mark_credential_error(self, account_id: str) -> None:
        """Mark an account as having credential issues."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.health = AccountHealth.CREDENTIAL_ERROR
                account.updated_at = datetime.now()
                await self._persist()
                logger.error(f"Account {account_id} credential error")

    async def mark_offline(self, account_id: str) -> None:
        """Mark an account as offline."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.health = AccountHealth.OFFLINE
                account.updated_at = datetime.now()
                await self._persist()
                logger.warning(f"Account {account_id} marked offline")

    async def restore_health(self, account_id: str) -> None:
        """Restore account to healthy state."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.health = AccountHealth.HEALTHY
                account.rate_limit_remaining = 100
                account.rate_limit_reset = None
                account.updated_at = datetime.now()
                await self._persist()
                logger.info(f"Account {account_id} restored to healthy")

    async def update_credentials(self, account_id: str, new_creds_ref: str) -> None:
        """Update credentials reference (called by CredentialWatcher on rotation)."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.credentials_ref = new_creds_ref
                account.updated_at = datetime.now()
                await self._persist()
                logger.info(f"Updated credentials for {account_id}: {new_creds_ref}")

    async def update_tmux_session(self, account_id: str, session_name: str | None) -> None:
        """Update the tmux session name for an account."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.tmux_session = session_name
                account.updated_at = datetime.now()
                await self._persist()

    async def update_mcp_endpoint(self, account_id: str, endpoint: str | None) -> None:
        """Update the MCP endpoint for an account."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.mcp_endpoint = endpoint
                account.updated_at = datetime.now()
                await self._persist()

    async def record_usage(self, account_id: str, tokens: int = 0) -> None:
        """Record task completion for an account."""
        async with self._lock:
            account = self._accounts.get(account_id)
            if account:
                account.mark_used()
                if tokens > 0:
                    account.rate_limit_remaining = max(0, account.rate_limit_remaining - tokens)
                await self._persist()

    async def get_health_report(self) -> PoolHealthReport:
        """Generate a health report for the entire pool."""
        async with self._lock:
            report = PoolHealthReport()
            report.total_accounts = len(self._accounts)

            for account in self._accounts.values():
                if account.health == AccountHealth.HEALTHY:
                    report.healthy += 1
                elif account.health == AccountHealth.RATE_LIMITED:
                    report.rate_limited += 1
                elif account.health == AccountHealth.CREDENTIAL_ERROR:
                    report.credential_errors += 1
                elif account.health == AccountHealth.OFFLINE:
                    report.offline += 1

                pool_key = account.pool
                if pool_key not in report.by_pool:
                    report.by_pool[pool_key] = {
                        "total": 0,
                        "healthy": 0,
                        "rate_limited": 0,
                        "credential_error": 0,
                        "offline": 0,
                    }
                report.by_pool[pool_key]["total"] += 1
                report.by_pool[pool_key][account.health.value] += 1

            return report

    async def get_status(self) -> PoolStatus:
        """Get real-time pool status."""
        async with self._lock:
            status = PoolStatus()
            for account in self._accounts.values():
                if account.health == AccountHealth.HEALTHY and account.rate_limit_remaining > 0:
                    status.available_accounts += 1
                else:
                    status.busy_accounts += 1

                pool_key = account.pool
                if pool_key not in status.by_pool:
                    status.by_pool[pool_key] = {"available": 0, "busy": 0}
                if account.health == AccountHealth.HEALTHY and account.rate_limit_remaining > 0:
                    status.by_pool[pool_key]["available"] += 1
                else:
                    status.by_pool[pool_key]["busy"] += 1

            return status

    async def rebalance(self) -> RebalanceReport:
        """Check for rate limit resets and restore accounts."""
        async with self._lock:
            report = RebalanceReport()
            now = datetime.now()

            for account in self._accounts.values():
                if account.health == AccountHealth.RATE_LIMITED:
                    if account.rate_limit_reset and account.rate_limit_reset <= now:
                        account.health = AccountHealth.HEALTHY
                        account.rate_limit_remaining = 100
                        account.rate_limit_reset = None
                        account.updated_at = now
                        report.accounts_restored.append(account.id)

            if report.accounts_restored:
                await self._persist()
                logger.info(f"Restored {len(report.accounts_restored)} accounts from rate limit")

            return report

    async def get_accounts_by_pool(self, pool: PoolType) -> list[Account]:
        """Get all accounts in a specific pool."""
        async with self._lock:
            return [a for a in self._accounts.values() if a.pool == pool]

    async def get_accounts_with_capability(self, capability: str) -> list[Account]:
        """Get all accounts that have a specific capability."""
        async with self._lock:
            return [a for a in self._accounts.values() if capability in a.capabilities]
