# WARP Proxy Pool Integration Guide

**Module**: `src/omega/proxy_pool.py`
**Status**: Production (Researcher Session, Carmack Approved)
**Tests**: Validation via `scripts/validate_warp_pool.sh` (8 scenarios)

---

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
Linux Network Namespace → WARP Tunnel (MASQUE) → Cloudflare Exit IP
```

---

## 2026 Research Findings Summary

| Finding | Confidence | Implication |
|---------|------------|-------------|
| **MASQUE required for proxy mode** | 10/10 | WireGuard deprecated; device profile MUST use MASQUE |
| **Use `socks5h://` for DNS sovereignty** | 10/10 | Remote DNS resolution through WARP tunnel |
| **systemd v254: `PrivateMounts` implied by `NetworkNamespacePath`** | 10/10 | Host-based `ip netns exec` approach avoids this |
| **Circuit breaker: 5 failures → 30s cooldown** | 9/10 | Production pattern from resilient-httpx |
| **One httpx.AsyncClient per proxy** | 9/10 | HTTP/2 connection reuse, no TLS handshake per request |

---

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
    client_kwargs["proxy"] = proxy_url
```

---

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

---

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

### Full Pool State

```python
state = await pool.get_pool_state()
print(f"Current: {state.current_index}, Ports: {state.ports}")
for h in state.health:
    print(f"  Node {h.node_id}: active={h.active}, ip={h.exit_ip}, latency={h.latency_ms}ms")
```

---

## Production Proxy Pool Pattern (2026)

Based on research from Hex Proxies, resilient-httpx, and pyroxi:

```python
import httpx
import asyncio
import random
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ProxyEndpoint:
    url: str                    # "socks5h://127.0.0.1:8081"
    label: str                  # "warp-node-1"
    max_concurrent: int = 25    # Semaphore limit

@dataclass
class ProxyState:
    endpoint: ProxyEndpoint
    client: httpx.AsyncClient
    semaphore: asyncio.Semaphore
    failures: int = 0
    cooldown_until: float = 0.0
    last_used: float = 0.0

    def is_available(self) -> bool:
        import time
        return time.time() > self.cooldown_until

    def record_success(self):
        self.failures = 0
        import time
        self.last_used = time.time()

    def record_failure(self):
        self.failures += 1

    def trip_circuit(self, cooldown: float):
        import time
        self.cooldown_until = time.time() + cooldown


class WarpProxyPool:
    """Async SOCKS5 proxy pool for WARP nodes with circuit breaking."""

    FAILURE_THRESHOLD = 5
    COOLDOWN_SECONDS = 30.0
    TIMEOUT = httpx.Timeout(connect=5.0, read=15.0, write=10.0, pool=5.0)
    LIMITS = httpx.Limits(max_connections=25, max_keepalive_connections=10)

    def __init__(self, endpoints: list[ProxyEndpoint]) -> None:
        if not endpoints:
            raise ValueError("at least one proxy endpoint is required")
        self._states: list[ProxyState] = [
            ProxyState(
                endpoint=ep,
                client=httpx.AsyncClient(
                    proxy=ep.url,
                    timeout=self.TIMEOUT,
                    limits=self.LIMITS,
                    follow_redirects=True,
                ),
                semaphore=asyncio.Semaphore(ep.max_concurrent),
            )
            for ep in endpoints
        ]

    async def aclose(self) -> None:
        await asyncio.gather(
            *(s.client.aclose() for s in self._states),
            return_exceptions=True,
        )

    def _pick(self) -> Optional[ProxyState]:
        candidates = [s for s in self._states if s.is_available()]
        if not candidates:
            return None
        weights = [1.0 / (1 + s.failures) for s in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]

    async def request(
        self, method: str, url: str, *, max_attempts: int = 4, **kwargs
    ) -> httpx.Response:
        last_exc = None
        for attempt in range(1, max_attempts + 1):
            state = self._pick()
            if state is None:
                await asyncio.sleep(1.0)
                continue
            async with state.semaphore:
                try:
                    response = await state.client.request(method, url, **kwargs)
                    if response.status_code >= 500 or response.status_code == 429:
                        raise httpx.HTTPStatusError(
                            f"retryable status {response.status_code}",
                            request=response.request,
                            response=response,
                        )
                    state.record_success()
                    return response
                except (httpx.HTTPError, httpx.HTTPStatusError) as exc:
                    state.record_failure()
                    last_exc = exc
                    if state.failures >= self.FAILURE_THRESHOLD:
                        state.trip_circuit(self.COOLDOWN_SECONDS)
                    delay = min(2 ** attempt, 10) + random.uniform(0, 0.5)
                    await asyncio.sleep(delay)
        raise last_exc
```

### Key Design Principles

1. **One client per proxy** — HTTP/2 connection reuse, no TLS handshake per request
2. **Per-proxy semaphore** — Caps concurrency to avoid rate limits (25-50 per proxy)
3. **Circuit breaker** — 5 consecutive failures → 30s cooldown
4. **Weighted random selection** — Prefer proxies with fewer failures
5. **Exponential backoff with jitter** — Prevents thundering herd

---

## httpx-socks Integration

```python
from httpx_socks import AsyncProxyTransport

transport = AsyncProxyTransport.from_url('socks5h://127.0.0.1:8081')
async with httpx.AsyncClient(transport=transport) as client:
    response = await client.get('https://1.1.1.1/cdn-cgi/trace')
```

**Dependencies**: `httpx-socks[asyncio]`, `python-socks>=2.4.3,<3.0.0`

---

## Health Check Pattern

```python
async def health_check_all(self, test_url='https://1.1.1.1/cdn-cgi/trace'):
    async with httpx.AsyncClient(timeout=10) as client:
        for proxy in self.proxies:
            try:
                response = await client.get(test_url, proxy=proxy.url)
                if response.status_code == 200 and 'warp=on' in response.text:
                    self.report_success(proxy)
                else:
                    self.report_failure(proxy)
            except Exception:
                self.report_failure(proxy)
```

**Recommended Health Check**: `https://1.1.1.1/cdn-cgi/trace` — returns WARP status, exit IP, and connection details.

---

## Deployment

### Prerequisites

1. Cloudflare WARP installed and registered
2. `spawn_warp_node.sh` installed at `/usr/local/bin/`
3. Root access for network namespace creation
4. Device profile in Cloudflare Zero Trust: **MASQUE** + **Local proxy mode**

### Deploy

```bash
sudo ./scripts/deploy_warp_pool.sh
bash scripts/validate_warp_pool.sh
```

---

## Heritage

`[id-soft: doom-1993] BSP Culling — O(1) health check before routing`
`[id-soft: doom-1993] Precomputed Lookup — cached health results`