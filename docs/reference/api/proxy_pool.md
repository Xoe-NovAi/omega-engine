# WARP Proxy Pool API Reference

**Module**: `src/omega/proxy_pool.py`
**Status**: Production (Researcher Session, Carmack Approved)
**Lines**: 368

## Overview

`EphemeralWarpPool` provides an AnyIO-native interface to the multi-namespace WARP proxy pool. It manages round-robin port selection, canary health probes, and graceful degradation.

## Classes

### NodeHealth

```python
@dataclass
class NodeHealth:
    node_id: int
    port: int
    active: bool = False
    exit_ip: Optional[str] = None
    latency_ms: Optional[float] = None
    last_checked: Optional[float] = None
    error: Optional[str] = None
```

### PoolState

```python
@dataclass
class PoolState:
    current_index: int
    ports: List[int]
    health: List[NodeHealth]
    timestamp: float
```

### EphemeralWarpPool

```python
class EphemeralWarpPool:
    def __init__(self, ports: Optional[List[int]] = None)
    
    # Properties
    @property
    def ports(self) -> List[int]
    
    @property
    def current_port(self) -> int
    
    # Core methods
    async def get_active_port(self) -> int
    async def get_proxy_url(self) -> str  # Returns "socks5h://..."
    async def rotate(self) -> bool
    async def get_healthy_port(self) -> Optional[int]
    async def get_exit_ip(self) -> Optional[str]
    async def get_pool_state(self) -> PoolState
```

## Key Methods

### get_proxy_url()

Returns the SOCKS5 proxy URL for the active node.

```python
pool = EphemeralWarpPool()
proxy_url = await pool.get_proxy_url()
# Returns: "socks5h://127.0.0.1:8081"
```

**Important**: Uses `socks5h://` (not `socks5://`) to force DNS resolution through the WARP exit node, preventing local DNS leaks.

### rotate()

Forces rotation to the next WARP node.

```python
success = await pool.rotate()
if success:
    print(f"New IP: {await pool.get_exit_ip()}")
else:
    print("Rotation failed, rolled back")
```

The rotation sequence:
1. Increment round-robin index
2. Trigger recycle via `spawn_warp_node.sh` (root-privileged)
3. Wait for Cloudflare to release tunnel (1s)
4. Verify new node is healthy via canary probe

### get_healthy_port()

Returns a healthy port with verified exit IP, or `None` if all nodes are unhealthy.

```python
healthy_port = await pool.get_healthy_port()
if healthy_port:
    proxy_url = f"socks5h://127.0.0.1:{healthy_port}"
else:
    # Fallback to direct connection
    proxy_url = None
```

## Features

- **Round-robin port selection**: Cycles through available ports
- **Canary probe verification**: Uses `https://1.1.1.1/cdn-cgi/trace` to verify exit IP
- **Health caching**: Caches health results for 30s TTL
- **Atomic rotation**: Rolls back on failure
- **Graceful degradation**: Returns `None` on complete failure

## Configuration

```python
DEFAULT_PORTS = [8081, 8082, 8083]
SPAWN_SCRIPT = Path("/usr/local/bin/spawn_warp_node.sh")
CANARY_URL = "https://1.1.1.1/cdn-cgi/trace"
CANARY_TIMEOUT_SECONDS = 2.5
HEALTH_CACHE_TTL_SECONDS = 30.0
RECYCLE_DELAY_SECONDS = 1.0
```

## Integration Points

- **ModelGateway**: Injects proxy URL for `opencode-zen` provider
- **OpenAICompatProvider**: Reads `config.extra["proxy_url"]` for httpx

## Heritage

`[id-soft: doom-1993] BSP Culling — O(1) health check before routing`
`[id-soft: doom-1993] Precomputed Lookup — cached health results`
