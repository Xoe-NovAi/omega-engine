"""
Sovereign WARP Proxy Pool — Delegation Layer
AP: AP-WARP-POOL-v1.1.0

This module delegates all proxy pool orchestration to the standalone 
`warp-proxy-pool` package.
"""

from __future__ import annotations

from typing import List, Optional
import warp_proxy_pool

# Export the class for the Oracle's type checking and attachment
EphemeralWarpPool = warp_proxy_pool.EphemeralWarpPool

# ── Configuration ──────────────────────────────────────────────────────────────
SOCKS5_TEMPLATE = "socks5h://127.0.0.1:{port}"

def get_pool() -> warp_proxy_pool.EphemeralWarpPool:
    """Return the global singleton pool instance from the sovereign package."""
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

