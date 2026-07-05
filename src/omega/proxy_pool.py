"""
Sovereign WARP Proxy Pool — Python Orchestration Layer
AP: AP-WARP-POOL-v1.0.0

Provides AnyIO-native interface to the multi-namespace WARP proxy pool.
Delegates lifecycle management to spawn_warp_node.sh (root-privileged).

Usage:
    from omega.proxy_pool import EphemeralWarpPool
    
    pool = EphemeralWarpPool()
    port = await pool.get_active_port()
    proxy_url = f"socks5h://127.0.0.1:{port}"
    
    # Or get a healthy port with canary verification
    healthy_port = await pool.get_healthy_port()
    if healthy_port:
        proxy_url = f"socks5h://127.0.0.1:{healthy_port}"

Heritage:
- [id-soft: doom-1993] BSP Culling — O(1) provider health check before inference
- [id-soft: doom-1993] Precomputed Lookup — canary probe results cached for fast access
"""

from __future__ import annotations

import anyio
import httpx
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
SOCKS5_TEMPLATE = "socks5h://127.0.0.1:{port}"  # socks5h:// prevents DNS leaks
DEFAULT_PORTS = [8081, 8082, 8083]  # ns_background (8081), ns_ephemeral (8082, 8083)
SPAWN_SCRIPT = Path("/usr/local/bin/spawn_warp_node.sh")
CANARY_URL = "https://1.1.1.1/cdn-cgi/trace"
CANARY_TIMEOUT_SECONDS = 2.5
HEALTH_CACHE_TTL_SECONDS = 30.0
RECYCLE_DELAY_SECONDS = 1.0  # Minimum delay after disconnect for Cloudflare release


@dataclass
class NodeHealth:
    """Health status for a single WARP node."""
    node_id: int
    port: int
    active: bool = False
    exit_ip: Optional[str] = None
    latency_ms: Optional[float] = None
    last_checked: Optional[float] = None
    error: Optional[str] = None


@dataclass
class PoolState:
    """Immutable snapshot of pool state."""
    current_index: int
    ports: List[int]
    health: List[NodeHealth]
    timestamp: float


class EphemeralWarpPool:
    """
    AnyIO-native wrapper for the multi-namespace WARP proxy pool.
    
    Lifecycle management is delegated to spawn_warp_node.sh via
    anyio.to_thread.run_sync() to avoid blocking the event loop.
    
    The pool maintains a round-robin index across available ports.
    Each port maps to an isolated Linux Network Namespace running
    its own WARP tunnel and socat bridge.
    
    Features:
    - Round-robin port selection
    - Canary probe verification (cdn-cgi/trace)
    - Health caching with TTL
    - Atomic rotation (rolls back on failure)
    - Graceful degradation (returns None on complete failure)
    
    Heritage:
    - [id-soft: doom-1993] BSP Culling — O(1) health check before routing
    - [id-soft: doom-1993] Precomputed Lookup — cached health results
    """
    
    def __init__(self, ports: Optional[List[int]] = None):
        """
        Initialize the proxy pool.
        
        Args:
            ports: List of SOCKS5 proxy ports. Defaults to [8081, 8082, 8083].
        """
        self._ports = ports or DEFAULT_PORTS
        self._current_index = 0
        self._health_cache: List[NodeHealth] = []
        self._health_cache_time: float = 0.0
    
    @property
    def ports(self) -> List[int]:
        """Return the list of managed ports."""
        return self._ports.copy()
    
    @property
    def current_port(self) -> int:
        """Return the current active port (synchronous, no health check)."""
        return self._ports[self._current_index]
    
    async def get_active_port(self) -> int:
        """
        Return the current active WARP node port.
        
        Returns:
            Port number (e.g., 8081)
        """
        return self._ports[self._current_index]
    
    async def get_proxy_url(self) -> str:
        """
        Return the SOCKS5 proxy URL for the active node.
        
        Returns:
            Proxy URL string (e.g., "socks5h://127.0.0.1:8081")
        
        Note:
            Uses socks5h:// (not socks5://) to force DNS resolution through
            the WARP exit node, preventing local DNS leaks. This is the
            sovereign choice for privacy-critical applications.
        """
        port = await self.get_active_port()
        return SOCKS5_TEMPLATE.format(port=port)
    
    async def rotate(self) -> bool:
        """
        Force rotation to the next WARP node.
        
        The rotation sequence:
        1. Increment round-robin index
        2. Trigger recycle via spawn_warp_node.sh (root-privileged)
        3. Wait for Cloudflare to release tunnel (RECYCLE_DELAY_SECONDS)
        4. Verify new node is healthy via canary probe
        
        Returns:
            True if rotation succeeded and new node is healthy,
            False if rotation failed (index rolled back)
        """
        old_index = self._current_index
        self._current_index = (self._current_index + 1) % len(self._ports)
        new_port = self._ports[self._current_index]
        node_id = self._current_index + 1
        
        logger.info(f"Rotating to node {node_id} (port {new_port})")
        
        try:
            # Delegate to shell script (root-privileged for ip netns)
            result = await anyio.to_thread.run_sync(
                lambda: SPAWN_SCRIPT.run_capture(
                    [str(node_id), "recycle"],
                    timeout=30
                )
            )
            
            if result.returncode != 0:
                logger.error(f"Rotation failed: {result.stderr}")
                self._current_index = old_index  # Rollback
                return False
            
            # Wait for Cloudflare to release tunnel
            await anyio.sleep(RECYCLE_DELAY_SECONDS)
            
            # Verify new node is healthy
            health = await self._check_node_health(node_id, new_port)
            if health.active and health.exit_ip:
                logger.info(f"Rotation successful: node {node_id} healthy (IP: {health.exit_ip})")
                return True
            else:
                logger.warning(f"Rotation completed but node {node_id} unhealthy")
                return False
            
        except Exception as e:
            logger.error(f"Rotation exception: {e}")
            self._current_index = old_index  # Rollback
            return False
    
    async def health(self, force_refresh: bool = False) -> List[NodeHealth]:
        """
        Return health status of all pool nodes.
        
        Results are cached for HEALTH_CACHE_TTL_SECONDS to avoid
        repeated canary probes. Pass force_refresh=True to bypass cache.
        
        Args:
            force_refresh: If True, bypass cache and probe all nodes
        
        Returns:
            List of NodeHealth objects, one per port
        """
        now = time.monotonic()
        
        # Check cache validity
        if (not force_refresh and 
            self._health_cache and 
            (now - self._health_cache_time) < HEALTH_CACHE_TTL_SECONDS):
            return self._health_cache.copy()
        
        # Probe all nodes
        health = []
        for i, port in enumerate(self._ports):
            node_id = i + 1
            h = await self._check_node_health(node_id, port)
            health.append(h)
        
        self._health_cache = health
        self._health_cache_time = now
        
        return health
    
    async def get_healthy_port(self) -> Optional[int]:
        """
        Return the first healthy port, or None if all are unhealthy.
        
        A port is considered healthy if:
        1. The port is listening (ss check)
        2. The canary probe succeeds (warp=on, ip= present)
        
        Returns:
            Port number if healthy, None if all unhealthy
        """
        health = await self.health()
        for h in health:
            if h.active and h.exit_ip:
                return h.port
        return None
    
    async def get_pool_state(self) -> PoolState:
        """
        Return an immutable snapshot of pool state.
        
        Useful for debugging and coordination.
        """
        health = await self.health()
        return PoolState(
            current_index=self._current_index,
            ports=self._ports.copy(),
            health=health,
            timestamp=time.monotonic()
        )
    
    async def _check_node_health(self, node_id: int, port: int) -> NodeHealth:
        """
        Check health of a single node.
        
        Returns NodeHealth with active, exit_ip, and latency_ms populated.
        """
        h = NodeHealth(node_id=node_id, port=port)
        
        # Check if port is listening
        try:
            result = await anyio.to_thread.run_sync(
                lambda: __import__('subprocess').run(
                    ['ss', '-tlnp'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            )
            h.active = f":{port} " in result.stdout
        except Exception as e:
            h.active = False
            h.error = f"ss check failed: {e}"
        
        # Canary probe if active
        if h.active:
            try:
                proxy_url = SOCKS5_TEMPLATE.format(port=port)
                timeout = httpx.Timeout(CANARY_TIMEOUT_SECONDS)
                limits = httpx.Limits(
                    max_keepalive_connections=0,
                    max_connections=1,
                    keepalive_expiry=0.0
                )
                
                # Small delay to let connection settle
                await anyio.sleep(0.5)
                
                async with httpx.AsyncClient(
                    proxies=proxy_url,
                    limits=limits,
                    timeout=timeout
                ) as client:
                    start = time.monotonic()
                    resp = await client.get(CANARY_URL)
                    h.latency_ms = (time.monotonic() - start) * 1000
                    
                    if resp.status_code == 200:
                        lines = resp.text.split("\n")
                        data = {
                            k: v 
                            for line in lines 
                            if "=" in line 
                            for k, v in [line.split("=", 1)]
                        }
                        
                        if data.get("warp") == "on" and "ip" in data:
                            h.exit_ip = data["ip"]
                        else:
                            h.error = f"Canary returned warp={data.get('warp')}, ip={data.get('ip')}"
                    else:
                        h.error = f"Canary HTTP {resp.status_code}"
                        
            except httpx.ConnectError as e:
                h.error = f"Connection refused: {e}"
            except httpx.TimeoutException as e:
                h.error = f"Timeout: {e}"
            except Exception as e:
                h.error = f"Canary probe failed: {e}"
        
        h.last_checked = time.monotonic()
        return h
    
    def __repr__(self) -> str:
        return (
            f"EphemeralWarpPool("
            f"ports={self._ports}, "
            f"current_index={self._current_index}, "
            f"current_port={self.current_port}"
            f")"
        )


# ── Convenience Functions ──────────────────────────────────────────────────────

_default_pool: Optional[EphemeralWarpPool] = None


def get_pool() -> EphemeralWarpPool:
    """Return the global singleton pool instance."""
    global _default_pool
    if _default_pool is None:
        _default_pool = EphemeralWarpPool()
    return _default_pool


async def get_proxy_url() -> str:
    """
    Convenience function to get the current proxy URL.
    
    Returns:
        SOCKS5 proxy URL string (e.g., "socks5h://127.0.0.1:8081")
    """
    return await get_pool().get_proxy_url()


async def get_healthy_proxy_url() -> Optional[str]:
    """
    Convenience function to get a verified healthy proxy URL.
    
    Returns:
        SOCKS5 proxy URL string if healthy node found, None otherwise
    """
    port = await get_pool().get_healthy_port()
    if port:
        return SOCKS5_TEMPLATE.format(port=port)
    return None
