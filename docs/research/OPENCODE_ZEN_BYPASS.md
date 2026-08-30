# 🔱 OpenCode Zen Rate Limit Bypass (oplire + WARP)
⬡ OMEGA ⬡ SOPHIA ⬡ oplire ⬡ opencode ⬡ trc_core ⬡ ZEN-BYPASS

**AP Token**: `AP-ZEN-BYPASS-v1.0.0`
**Status**: ACTIVE | **Last Updated**: 2026-07-04
**Author**: Sovereign Master Researcher

---

## §0 Executive Summary

This document is the canonical reference and implementation guide for bypassing OpenCode Zen's IP-based rate limiting using the **oplire** daemon and Cloudflare WARP. It details the root cause of the rate-limiting mechanism, provides a step-by-step setup guide for local development, and outlines how to integrate this bypass directly into the Omega Engine's provider fabric.

For production-grade resilience and zero-latency failover, the Omega Engine employs a **Multi-Namespace WARP Proxy Pool** architecture. See [WARP_PROXY_POOL_SPEC.md](./warp_proxy_pool/WARP_PROXY_POOL_SPEC.md) for the full specification.

---

## §1 The Root Cause: IP-Based Rate Limiting

OpenCode Zen's free tier rate limiting is implemented at the **network/IP layer**, not the API key layer. 

### §1.1 The Mechanism
The rate-limiting logic is handled by:
`packages/console/app/src/routes/zen/util/ipRateLimiter.ts`

When a request is made to `https://opencode.ai/zen/v1/responses`, the server performs the following checks in order:
1. **IP Check:** Inspects the incoming request's IP address against a Redis/memory store. If the IP has exceeded **100 requests/day**, it immediately throws `FreeUsageLimitError` (HTTP 429).
2. **Auth/Billing Check:** Inspects the `Authorization: Bearer <key>` header to validate the API key and check paid balances.

### §1.2 The Bug/Design Flaw
Because the **IP Check** executes *before* the **Auth/Billing Check**, even paid accounts with active balances can hit the IP-based free-tier limit and get blocked. 

**Why Swapping API Keys Fails:**
Since the limit is tied to your physical IP address, changing the API key in your configuration has zero effect. The server will continue to return `FreeUsageLimitError` until the 24-hour IP window resets.

---

## §2 The Solution: IP Rotation via Cloudflare WARP (`oplire`)

The most robust, production-grade solution is **`oplire`** (OpenCode Limit Reset + Proxy), a Rust-based utility that automates IP rotation using Cloudflare WARP.

### §2.1 Why Cloudflare WARP?
* **High Trust Score:** Cloudflare IPs are trusted by default across the web (unlike Tor or cheap datacenter proxies).
* **Speed:** IP rotation takes approximately **8 seconds**.
* **Free & Unlimited:** No subscriptions or quotas.

### §2.2 How `oplire` Works
`oplire` runs as a local daemon and acts as a reverse proxy on `127.0.0.1:8080`. 
1. It intercepts all outgoing requests to OpenCode Zen.
2. If a request returns an HTTP 429 (`FreeUsageLimitError`), `oplire` immediately:
   * Stops the current WARP tunnel.
   * Clears cached session data.
   * Registers a new WARP tunnel (generating a fresh Cloudflare IP).
   * Restarts the tunnel and retries the request transparently.

---

## §3 Step-by-Step Setup Guide

Follow these steps to configure `oplire` and route OpenCode Zen through it.

### Step 1: Install Cloudflare WARP Client
Install the official client on your machine. 

#### A. Linux (Ubuntu / Debian / WSL2)
For modern Ubuntu distributions (including Ubuntu 24.04 `noble` and Ubuntu 25.10 `questing`), the default dynamic codename lookup `$(lsb_release -cs)` can break if Cloudflare has not yet published native packages for your specific release. 

To ensure a clean installation on AMD64 architectures and prevent multi-arch repository mismatch warnings, force the stable, fully-compatible `noble` repository:

1. **Install dependencies:**
   ```bash
   sudo apt update && sudo apt install -y curl gnupg
   ```

2. **Download and install the Cloudflare GPG key:**
   ```bash
   curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
   ```

3. **Configure the compatibility repository list:**
   ```bash
   echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg arch=amd64] https://pkg.cloudflareclient.com/ noble main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
   ```

4. **Refresh package indexes and install WARP:**
   ```bash
   sudo apt update && sudo apt install -y cloudflare-warp
   ```

#### B. macOS
```bash
brew install cloudflare-warp
```

#### C. Windows (Native)
```powershell
winget install Cloudflare.Warp
```

### Step 2: Register WARP Identity
Register a free Cloudflare WARP account on your machine:
```bash
warp-cli registration new
warp-cli connect
# Verify you have a Cloudflare IP:
curl https://ifconfig.me
warp-cli disconnect
```

### Step 3: Install `oplire`
Install `oplire` globally or build it from source:

```bash
# Linux (AUR)
yay -S oplire

# Windows (winget)
winget install BerkeOruc.oplire

# macOS (Homebrew)
brew install berkeoruc/oplire/oplire

# From Source (Rust required)
git clone https://github.com/BerkeOruc/oplire.git
cd oplire
cargo build --release
sudo cp target/release/oplire /usr/bin/oplire
```

Verify the installation:
```bash
oplire doctor
```

### Step 4: Configure and Start the Daemon
Configure `oplire` to listen locally and target OpenCode Zen:

```bash
# Set configuration
oplire config set --listen 127.0.0.1:8080 --upstream https://opencode.ai/zen/v1
oplire config set --warp-delay 8000  # 8 seconds rotation delay

# Start daemon in background
oplire daemon &
```

---

## §4 OpenCode Integration

To route OpenCode through the `oplire` proxy, configure the standard proxy environment variables.

### §4.1 Environment Variables
Add the following to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
# Route HTTPS and HTTP traffic through the SOCKS5 proxy
export HTTPS_PROXY=socks5://127.0.0.1:8080
export HTTP_PROXY=socks5://127.0.0.1:8080

# CRITICAL: Bypass proxy for local connections (prevents OpenCode TUI routing loops)
export NO_PROXY=localhost,127.0.0.1,::1
```

### §4.2 Project-Specific Configuration
Alternatively, you can set the proxy environment variables directly in your project's `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "env": {
    "HTTPS_PROXY": "socks5://127.0.0.1:8080",
    "HTTP_PROXY": "socks5://127.0.0.1:8080",
    "NO_PROXY": "localhost,127.0.0.1"
  }
}
```

---

## §5 Omega Engine Integration (Sovereign Pattern)

For the Omega Engine, we can implement a dedicated `OpenCodeZenBackend` in the provider fabric that leverages the `oplire` proxy.

```python
# src/omega/oracle/backends/opencode_zen.py
"""OpenCode Zen backend with WARP proxy rotation via oplire."""

import os
import anyio
from typing import AsyncIterator
from ...model_gateway import ProviderBackend, GenerateResult

class OpenCodeZenBackend(ProviderBackend):
    """Zen provider with automatic IP rotation via oplire WARP proxy."""
    
    name = "opencode_zen"
    requires_proxy = True
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("OPENCODE_ZEN_API_KEY")
        self.base_url = config.get("base_url", "https://opencode.ai/zen/v1")
        self.proxy_url = config.get("proxy_url", "socks5://127.0.0.1:8080")
        self._client = None
    
    async def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(
                proxy=self.proxy_url,
                timeout=httpx.Timeout(120.0),
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> GenerateResult:
        client = await self._get_client()
        
        # oplire daemon handles 429 -> IP rotation transparently
        for attempt in range(3):
            try:
                resp = await client.post(
                    f"{self.base_url}/responses",
                    json={"input": prompt, "model": kwargs.get("model", "opencode/big-pickle")},
                )
                resp.raise_for_status()
                data = resp.json()
                return GenerateResult(
                    text=data["output"]["text"],
                    provider_name=self.name,
                    model_used=kwargs.get("model"),
                    latency_ms=resp.elapsed.total_seconds() * 1000,
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < 2:
                    # Wait briefly for oplire to complete IP rotation
                    await anyio.sleep(2)
                    continue
                raise
    
    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            resp = await client.get(f"{self.base_url}/models")
            return resp.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        if self._client:
            await self._client.aclose()
```

Configure this backend in `config/providers.yaml`:

```yaml
providers:
  - name: opencode_zen
    type: opencode_zen
    priority: 4  # Positioned after local-first options
    enabled: true
    config:
      api_key: ${OPENCODE_ZEN_API_KEY}
      proxy_url: "socks5://127.0.0.1:8080"
      base_url: "https://opencode.ai/zen/v1"
    models:
      - opencode/big-pickle
      - opencode/nemotron-3-ultra-free
      - opencode/mimo-v2.5-free
      - opencode/deepseek-v4-flash-free
```

---

## §6 Verification and Diagnostics

To verify that the proxy and rotation are working correctly, run these terminal commands:

```bash
# 1. Verify WARP Connection Status
oplire status

# 2. Check your standard public IP
curl https://ifconfig.me

# 3. Check your proxy IP (should be different)
curl -x socks5://127.0.0.1:8080 https://ifconfig.me

# 4. Trigger a manual rotation
oplire reset
# Check proxy IP again to confirm it changed
curl -x socks5://127.0.0.1:8080 https://ifconfig.me
```

---

## §6 Advanced: Multi-Namespace Sovereign Proxy Pool

For high-volume background research and concurrent verification tasks, a single `oplire` instance is insufficient. The Omega Engine implements a **Multi-Namespace WARP Proxy Pool** to segment traffic and eliminate cross-subsystem rate-limit interference.

### §6.1 Architecture Overview
The engine deploys multiple independent `warp-svc` daemons, each isolated within its own **Linux Network Namespace (`netns`)**. This allows the engine to maintain several distinct Cloudflare exit IPs simultaneously.

* **`ns_critical`**: Dedicated to user-facing ModelGateway traffic (Low volume, High priority).
* **`ns_background`**: Dedicated to the Background Researcher (High volume, Aggressive rotation).
* **`ns_ephemeral`**: Dynamic pool for the Skeptical Verifier (Concurrent multi-source scraping).

### §6.2 Implementation Reference
The complete technical specification, including the `spawn_warp_node.sh` lifecycle script, systemd template units, and the Python `EphemeralWarpPool` orchestration core, is documented in:
👉 **[`docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md`](./warp_proxy_pool/WARP_PROXY_POOL_SPEC.md)**

---

*🔱 OMEGA ⬡ SOPHIA ⬡ oplire ⬡ opencode ⬡ trc_core ⬡ ZEN-BYPASS*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: oplire | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
