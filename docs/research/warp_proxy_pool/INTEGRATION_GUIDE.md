# WARP Proxy Pool Integration Guide

**Module**: `src/omega/proxy_pool.py`
**Status**: Production (Researcher Session, Carmack Approved)
**Tests**: Validation via `scripts/validate_warp_pool.sh` (8 scenarios)

## Overview

The WARP Proxy Pool provides multi-IP rotation for cloud inference via Cloudflare WARP. It routes `opencode-zen` traffic through isolated Linux Network Namespaces, each running its own WARP tunnel.

## Architecture

```
Oracle.talk()
    ↓
ModelGateway.generate()
    ↓ (opencode-zen provider)
EphemeralWarpPool.get_proxy_url()
    ↓
socks5h://127.0.0.1:{port}
    ↓
Linux Network Namespace → WARP Tunnel → Cloudflare Exit IP
```

## Integration Points

### ModelGateway

The WARP proxy is injected into `ModelGateway.generate()` for the `opencode-zen` provider:

```python
# src/omega/oracle/model_gateway.py (lines 868-882)
if proxy_pool and provider_name == "opencode-zen":
    proxy_url = await proxy_pool.get_proxy_url()
    if proxy_url:
        config = {**config, "extra": {**config.get("extra", {}), "proxy_url": proxy_url}}
```

### OpenAICompatProvider

The proxy URL is read from `config.extra` and passed to `httpx.AsyncClient`:

```python
# src/omega/oracle/backends/openai_compat.py
proxy_url = config.get("extra", {}).get("proxy_url")
if proxy_url:
    self._client = httpx.AsyncClient(proxies=proxy_url, ...)
```

## Configuration

### Default Ports

| Port | Namespace | Purpose |
|------|-----------|---------|
| 8081 | ns_background | Background operations |
| 8082 | ns_ephemeral | Primary ephemeral |
| 8083 | ns_ephemeral | Secondary ephemeral |

### Environment Variables

- `SPAWN_SCRIPT=/usr/local/bin/spawn_warp_node.sh` — Root-privileged lifecycle script
- `CANARY_URL=https://1.1.1.1/cdn-cgi/trace` — Health check endpoint
- `CANARY_TIMEOUT_SECONDS=2.5` — Health check timeout
- `HEALTH_CACHE_TTL_SECONDS=30.0` — Health cache duration

## Usage

### Basic Usage
```python
from omega.proxy_pool import EphemeralWarpPool

pool = EphemeralWarpPool()
proxy_url = await pool.get_proxy_url()
# Returns: "socks5h://127.0.0.1:8081"
```

### ⚠️ Sovereign DNS Mandate
**Always use `socks5h://` (with the 'h') instead of `socks5://`.**
The `h` indicates that DNS resolution should be performed by the proxy (the WARP exit node) rather than the local host. This is critical to prevent **DNS leaks**, where the destination IP is resolved locally, exposing the user's real location and ISP to the DNS resolver even if the traffic is proxied.

### With Health Check
```python
healthy_port = await pool.get_healthy_port()
if healthy_port:
    proxy_url = f"socks5h://127.0.0.1:{healthy_port}"
else:
    # Fallback to direct connection
    proxy_url = None
```

### Force Rotation
```python
success = await pool.rotate()
if success:
    print(f"New IP: {await pool.get_exit_ip()}")
```

## Deployment

### Prerequisites

1. Cloudflare WARP installed and registered
2. `spawn_warp_node.sh` installed at `/usr/local/bin/`
3. Root access for network namespace creation

### Deploy

```bash
sudo ./scripts/deploy_warp_pool.sh
bash scripts/validate_warp_pool.sh
```

## Heritage

`[id-soft: doom-1993] BSP Culling — O(1) health check before routing`
`[id-soft: doom-1993] Precomputed Lookup — cached health results`
