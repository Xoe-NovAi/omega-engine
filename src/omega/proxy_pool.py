# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Sovereign WARP Proxy Pool — Delegation Layer
AP: AP-WARP-POOL-v1.1.0

This module delegates all proxy pool orchestration to the standalone
`warp-proxy-pool` package.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

from __future__ import annotations

from typing import Optional

try:
    import warp_proxy_pool
except ImportError:  # pragma: no cover — optional [warp] extra
    warp_proxy_pool = None  # type: ignore[assignment]

# Export the class for the Oracle's type checking and attachment
EphemeralWarpPool = getattr(warp_proxy_pool, "EphemeralWarpPool", None) if warp_proxy_pool else None

# ── Configuration ──────────────────────────────────────────────────────────────
SOCKS5_TEMPLATE = "socks5h://127.0.0.1:{port}"


def get_pool():
    """Return the global singleton pool instance from the sovereign package."""
    if warp_proxy_pool is None:
        raise ImportError("warp-proxy-pool not installed (optional [warp] extra)")
    return warp_proxy_pool.get_pool()


async def get_proxy_url() -> str:
    """
    Convenience function to get the current proxy URL.
    """
    port = await get_pool().get_active_port()
    return SOCKS5_TEMPLATE.format(port=port)


async def get_healthy_proxy_url() -> Optional[str]:
    """
    Convenience function to get a verified healthy proxy URL.
    """
    port = await get_pool().get_healthy_port()
    if port:
        return SOCKS5_TEMPLATE.format(port=port)
    return None
