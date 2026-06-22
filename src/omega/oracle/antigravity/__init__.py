# AP: AP-PR-READINESS-v1.0.0
# ── Antigravity Standalone Module ──
# OAuth-based cloud inference provider for Google's internal Unified Gateway API.
# [Mandate 16: Modularization & Portability] — community-shareable, config-driven.
#
# Architecture decision (2026-06-18): Standalone module, NOT a provider class in the
# round-robin chain. Google bans rapid account switching. This module is invoked
# explicitly, never auto-rotated by the gateway search order.
#
# Reference: data/entities/researcher/workspace/ANTIGRAVITY_SYSTEM_DEEP_DIVE.md

"""Antigravity OAuth cloud inference module.

Usage::

    from omega.oracle.antigravity import AntigravityClient, AccountManager

    config = AntigravityConfig.from_env()  # reads configurable paths
    manager = AccountManager(config)
    client = AntigravityClient(config)

    account = manager.select_account("claude", "claude-sonnet-4.6")
    result = await client.generate(
        model="claude-sonnet-4.6",
        system_prompt="You are helpful.",
        user_query="Hello",
        account=account,
    )
    manager.mark_used(account)
"""

from .config import AntigravityConfig
from .client import AntigravityClient, AntigravityResponse
from .account_manager import AccountManager, ManagedAccount, AccountSelection

__all__ = [
    "AntigravityConfig",
    "AntigravityClient",
    "AntigravityResponse",
    "AccountManager",
    "ManagedAccount",
    "AccountSelection",
]
