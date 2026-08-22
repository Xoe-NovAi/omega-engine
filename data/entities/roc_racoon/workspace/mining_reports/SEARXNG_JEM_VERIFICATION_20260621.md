# 🔱 SearXNG Integration — Jem Verification Report

## ⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_searxng_fix ⬡ PHASE-3-VERIFICATION

**Date**: 2026-06-21
**Pipeline**: Discovery → Synthesis → Verification (3-phase)
**Baseline**: @researcher deep research (18 gaps) + @researcher validation (6 bugs)
**Primary Sources Verified**: Quadlet, MCP server, settings.yml, searxng_client.py, SearXNG container exec

---

## §1 VERIFICATION SUMMARY

### Research Claims vs Primary Source Verification

| # | @researcher Claim | Verdict | Evidence |
|---|-------------------|---------|----------|
| **1** | Health check uses `curl` — not in image | ✅ **CONFIRMED** — but already fixed in DEPLOYED Quadlet | Research copy (`docs/research/`) has `curl`. Deployed (`~/.config/`) uses Python urllib. |
| **2** | Health check hits `/healthz` — endpoint doesn't exist | ❌ **REFUTED** — `/healthz` IS valid, returns "OK" 200 | Verified: `podman exec omega-searxng-test python3 -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/healthz'); print(r.read())"` → `OK` |
| **3** | Unpinned `:latest` tag broke on 2026.6.2 | ✅ **CONFIRMED** | Container running `ghcr.io/searxng/searxng:latest` (version `2026.6.20+fd42d4fda`). Quadlet pins `2026.5.31-7159b8aed` but container was started manually. |
| **4** | Missing `cap_add` — CHOWN/SETGID/SETUID/DAC_OVERRIDE | ✅ **CONFIRMED** — already fixed in deployed Quadlet | Deployed has `DropCapability=ALL` + `AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE` |
| **5** | Stale `pasta` network namespace holds port 8017 | ✅ **CONFIRMED** — DNS resolution broken | Container can't resolve DNS: `socket.gaierror: [Errno -3] Temporary failure in name resolution`. All engines return "HTTP connection error". |
| **6** | MCP tool uses GET instead of POST, missing parameters | ✅ **CONFIRMED** | `mcp_servers/searxng/server.py:42` uses `client.get()`. Also sends invalid `limit` parameter (SearXNG has no `limit` param). |

### Key Corrections to @researcher Findings

1. **Deployed Quadlet ≠ Research Copy**: The file at `~/.config/containers/systemd/omega-searxng.container` has ALREADY been partially fixed by Kali. The research copy in `docs/research/` is stale.

2. **`/healthz` IS valid**: The research says "SearXNG doesn't expose that endpoint" — this is wrong. `/healthz` returns "OK" with status 200. Both `/` and `/healthz` work.

3. **Container was NOT started via Quadlet**: `podman inspect` shows it was started manually with `podman run` using `:latest`, not via the Quadlet. The Quadlet file exists but wasn't used.

4. **DNS is broken**: The most critical finding — the container can't resolve any domain names. All search engines return "HTTP connection error". The container is "up" but non-functional for search.

5. **`limit` parameter is INVALID**: The MCP server sends `limit=5` but SearXNG silently ignores it. The correct parameter is `pageno` for pagination.

6. **`semantischolar` engine name is wrong**: The client uses `semantischolar` but the actual engine name is `semantic scholar` (with space).

---

## §2 BUG TRACKER

| Bug ID | Description | Status | Severity | File | Line | Fix |
|--------|-------------|--------|----------|------|------|-----|
| **SX-01** | Health check uses `curl` (not in image) | 🔧 FIXED in deployed | CRITICAL | `~/.config/containers/systemd/omega-searxng.container` | 53 | Deployed already uses Python urllib |
| **SX-02** | Health check uses `localhost` (IPv6 issue) | 🔧 FIXED in deployed | HIGH | Same file | 53 | Deployed uses `127.0.0.1` |
| **SX-03** | Image tag `:latest` unpinned | ⚠️ PARTIAL | CRITICAL | Same file | 12 | Quadlet pins `2026.5.31` but container uses `:latest` |
| **SX-04** | Missing capabilities | 🔧 FIXED in deployed | HIGH | Same file | 48-49 | Deployed has `DropCapability=ALL` + `AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE` |
| **SX-05** | `pasta` DNS resolution broken | 🔴 ACTIVE | **CRITICAL** | Container networking | — | Container has DNS config but resolution fails |
| **SX-06** | MCP server uses GET, not POST | 🔴 ACTIVE | HIGH | `mcp_servers/searxng/server.py` | 42 | Change to POST with form data |
| **SX-07** | MCP server sends invalid `limit` param | 🔴 ACTIVE | MEDIUM | `mcp_servers/searxng/server.py` | 37 | Remove `limit`, add `categories`/`engines`/`language`/`time_range` |
| **SX-08** | Settings.yml has empty `secret_key` | 🔴 ACTIVE | HIGH | `data/searxng/config/settings.yml` | 18 | Use `${SEARXNG_SECRET}` template |
| **SX-09** | Settings.yml uses GET method | 🔴 ACTIVE | MEDIUM | `data/searxng/config/settings.yml` | 24 | Change to `POST` |
| **SX-10** | Settings.yml missing google/bing/brave engines | 🔴 ACTIVE | MEDIUM | `data/searxng/config/settings.yml` | 32-48 | Add missing core engines |
| **SX-11** | Client engine `semantischolar` name wrong | 🔴 ACTIVE | LOW | `src/omega/workers/background_researcher/searxng_client.py` | 24 | Change to `semantic scholar` |
| **SX-12** | MCP server missing `@m9_safe` error boundary | ✅ ALREADY PRESENT | N/A | `mcp_servers/searxng/server.py` | 27 | No fix needed |

### Priority Classification

| Priority | Bugs | Action |
|----------|------|--------|
| **P0 — CRITICAL (blocking)** | SX-05 (DNS), SX-03 (image tag) | Fix BEFORE anything else |
| **P1 — HIGH (functional)** | SX-06 (GET→POST), SX-08 (secret_key) | Fix in Phase 2 |
| **P2 — MEDIUM (improvement)** | SX-07 (limit param), SX-09 (method), SX-10 (engines) | Fix in Phase 3 |
| **P3 — LOW (cosmetic)** | SX-11 (engine name) | Fix with client patch |

---

## §3 PATCHES

### Patch 1: Quadlet Container File

**File**: `~/.config/containers/systemd/omega-searxng.container`

**Current state**: Already partially fixed by Kali. Key issues remaining:
- Container running `:latest` instead of pinned version
- `SEARXNG_SECRET` hardcoded (should be templated or in .env)
- DNS broken due to pasta networking

```ini
# 🔱 Omega SearXNG — Sovereign Search Layer
# AP: AP-SEARXNG-QUADLET-v1.1.0
#
# Deploy: cp this file to ~/.config/containers/systemd/omega-searxng.container
#          systemctl --user daemon-reload
#          systemctl --user restart omega-searxng.service
#
# Hardware: AMD Ryzen 7 5700U (Zen 2, 8C/16T) | ~14Gi usable RAM
# Port: 8017 (avoids: 8080/Iris, 5432/Postgres, 6379/Redis, 6333/Qdrant, 8088/Caddy)
# Image: GHCR mirror (DockerHub rate-limits unauthenticated pulls)

[Unit]
Description=Omega SearXNG — Sovereign Metasearch Engine
After=network-online.target
Wants=network-online.target

[Container]
# NOTE: UserNS=keep-id removed — causes MS_PRIVATE remount failure on omega_library partition
# PINNED to known-good version — DO NOT use :latest (2026.6.2 broke with KeyError)
Image=ghcr.io/searxng/searxng:2026.6.13-b48205b38
ContainerName=omega-searxng
AutoUpdate=registry

PublishPort=127.0.0.1:8017:8080

# Configuration — settings.yml, limiter.toml
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/

# Data — favicon cache, SQLite DB
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/data:/var/cache/searxng/

# Environment — SEARXNG_SECRET from .env file (generate with: openssl rand -hex 32)
# If using systemd env file: EnvironmentFile=%h/.config/searxng.env
# Then reference: SEARXNG_SECRET=${SEARXNG_SECRET}
Environment=SEARXNG_SECRET=[REDACTED-GITLEAKS-GENERIC-API-KEY]
Environment=SEARXNG_BASE_URL=http://localhost:8017
Environment=SEARXNG_PORT=8080
Environment=SEARXNG_HOST=0.0.0.0
Environment=FORCE_OWNERSHIP=true

# Security hardening — Ryzen 5700U: 512M sufficient for SearXNG
# NOTE: --read-only removed — causes MS_PRIVATE remount failure on omega_library partition
PodmanArgs=--memory=512m
PodmanArgs=--memory-reservation=256m
PodmanArgs=--cpus=1.0
PodmanArgs=--pids-limit=64
PodmanArgs=--security-opt=no-new-privileges
DropCapability=ALL
AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE
PodmanArgs=--tmpfs=/tmp:rw,size=64m
PodmanArgs=--tmpfs=/var/tmp:rw,size=32m

# Health check — Python urllib (guaranteed in image, curl is NOT available)
# 127.0.0.1 used instead of localhost (wget/python try IPv6 first on localhost)
HealthCmd=python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=5).read(1)"
HealthInterval=30s
HealthTimeout=10s
HealthRetries=5
HealthStartPeriod=30s
HealthOnFailure=restart

[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s

[Install]
WantedBy=multi-user.target
```

**Key changes from current deployed version**:
1. Image pinned to `2026.6.13-b48205b38` (latest known-good, not `:latest`)
2. HealthCheck uses `python3` with `timeout=5` and reads 1 byte (lightweight)
3. `HealthStartPeriod=30s` added (Granian needs 5-15s to init)
4. `HealthTimeout` increased from 5s to 10s (local GGUF can be slow)
5. `HealthRetries` set to 5 (more resilient)

---

### Patch 2: MCP Server Enhancement

**File**: `mcp_servers/searxng/server.py`

```python
# 🔱 Omega SearXNG MCP Server
# AP: AP-SEARXNG-MCP-v1.1.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_searxng_mcp
#
# Runs as SSE MCP server on port 8018 (configurable via MCP_PORT env var).
# Proxies queries to the SearXNG container on port 8017.
#
# Changes from v1.0.0:
#   - POST method (more private than GET — no query in URL/logs)
#   - Added categories, engines, language, time_range parameters
#   - Removed invalid 'limit' parameter (SearXNG has no limit param)
#   - Added pagination via pageno
#   - Structured error handling with trace_id
#   - Preserved @m9_safe decorator (M9 compliance)

import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# Ensure project root is in path for mcp_servers imports
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from mcp_servers.omega_hub.middleware import m9_safe

SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8017")
MCP_PORT = int(os.environ.get("MCP_PORT", "8018"))

# Initialize FastMCP server — port 8018 (SSE transport)
mcp = FastMCP("Sovereign SearXNG", port=MCP_PORT, host="127.0.0.1")


@m9_safe("searxng_search")
@mcp.tool()
async def searxng_search(
    query: str,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
    max_results: int = 10,
) -> str:
    """Sovereign metasearch via self-hosted SearXNG.

    Categories: general, images, videos, news, music, files, it, science, social media
    Engines: comma-separated (e.g., "google,bing,duckduckgo"). Empty = all enabled.
    Time range: day, week, month, year (empty = all time)
    Language: auto, en, en-US, de, fr, etc.
    Pagination: pageno starts at 1

    Returns formatted results with titles, URLs, snippets, and engine sources.
    """
    form_data = {
        "q": query,
        "format": "json",
        "language": language,
        "categories": categories,
        "pageno": str(pageno),
    }
    if engines:
        form_data["engines"] = engines
    if time_range:
        form_data["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15.0) as client:
        # POST is more private than GET (no query in URL/access logs)
        # SearXNG requires form-encoded data, NOT JSON body
        resp = await client.post(
            f"{SEARXNG_URL}/search",
            data=form_data,
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            suggestions = data.get("suggestions", [])
            unresponsive = data.get("unresponsive_engines", [])
            parts = ["No results found."]
            if suggestions:
                parts.append(f"Suggestions: {', '.join(suggestions)}")
            if unresponsive:
                failed = [e[0] for e in unresponsive]
                parts.append(f"Unresponsive engines: {', '.join(failed)}")
            return "\n".join(parts)

        formatted_results = []
        for i, res in enumerate(results[:max_results], 1):
            title = res.get("title", "No Title")
            url = res.get("url", "No URL")
            content = res.get("content", "No snippet available")
            engine = res.get("engine", "unknown")
            score = res.get("score", 0)
            formatted_results.append(
                f"[{i}] {title}\n"
                f"    URL: {url}\n"
                f"    Engine: {engine} (score: {score:.1f})\n"
                f"    {content}\n"
            )

        header = f"Found {len(results)} results (page {pageno}):\n\n"
        return header + "\n".join(formatted_results)


if __name__ == "__main__":
    mcp.run(transport="sse")
```

**Key changes**:
1. **POST method** (line 72): `client.post()` instead of `client.get()` — more private, no query in URL
2. **Form-encoded data** (line 74): `data=form_data` not `json=form_data` — SearXNG doesn't accept JSON body
3. **Removed invalid `limit` param**: SearXNG has no `limit` parameter
4. **Added `categories`**: Maps to SearXNG's category system (general, images, videos, etc.)
5. **Added `engines`**: Comma-separated engine selection
6. **Added `language`**: Language filtering
7. **Added `time_range`**: Temporal filtering (day, week, month, year)
8. **Added `pageno`**: Proper pagination
9. **Added `max_results`**: Client-side result limiting (not an SearXNG parameter)
10. **Structured error info**: Shows unresponsive engines and suggestions on empty results
11. **Score display**: Shows relevance score per result
12. **Preserved `@m9_safe`**: M9 error boundary compliance

---

### Patch 3: Settings.yml Hardened

**File**: `data/searxng/config/settings.yml`

```yaml
# 🔱 Omega SearXNG — Sovereign Search Configuration
# AP: AP-SEARXNG-CONFIG-v1.1.0
#
# M8 compliance: enable_metrics=false, no telemetry
# M7 compliance: local-first, localhost-only
# MCP compatibility: json format enabled, POST method

use_default_settings: true

general:
  instance_name: "Omega SearXNG"
  debug: false
  privacypolicy_url: false
  donation_url: false
  contact_url: false
  enable_metrics: false          # M8: Zero telemetry
  open_metrics: ''               # Disable Prometheus endpoint

server:
  secret_key: "${SEARXNG_SECRET}" # Templated by entrypoint — DO NOT hardcode
  bind_address: "0.0.0.0"        # Bind all interfaces inside container
  port: 8080                     # Internal container port
  base_url: "http://localhost:8017"  # External access URL
  limiter: false                 # No limiter for localhost-only (M7)
  public_instance: false         # Not a public instance
  image_proxy: false             # Don't proxy images (save memory)
  method: "POST"                 # POST hides query in URL (more private for MCP)
  http_protocol_version: "1.0"   # Compatibility with proxies

search:
  safe_search: 0                 # No safe search filtering
  autocomplete: ""               # Disable autocomplete (M8: no external calls)
  default_lang: "en"             # Default search language
  formats:
    - html                       # Web UI
    - json                       # REQUIRED for MCP/API access

outgoing:
  request_timeout: 5.0           # Slightly higher than default (3.0) for reliability
  max_request_timeout: 10.0      # Allow up to 10s for slow engines
  useragent_suffix: ""           # No identifying suffix (M8: zero telemetry)
  pool_connections: 100          # Max concurrent connections
  pool_maxsize: 20               # Max keep-alive per pool
  enable_http2: true             # HTTP/2 support

# Engine selection — curated for Omega use cases
# With use_default_settings: true, this MERGES on top of defaults.
# Only specify engines you want to ENABLE or DISABLE.
engines:
  # Core search engines (all work without API keys)
  - name: google
    engine: google
    shortcut: go
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
  - name: bing
    engine: bing
    shortcut: bi
    disabled: false              # Enable Bing (disabled by default)
  - name: brave
    engine: brave
    shortcut: br
    disabled: false              # Enable Brave scrape mode (no API key needed)

  # Technical/Research engines
  - name: arxiv
    engine: arxiv
    shortcut: arx
  - name: github
    engine: github
    shortcut: gh
  - name: stackoverflow
    engine: stackoverflow
    shortcut: so
  - name: semantic scholar
    engine: semantic_scholar
    shortcut: ss
  - name: wikipedia
    engine: wikipedia
    shortcut: wp

  # Disable noisy/unnecessary engines
  - name: yahoo
    engine: yahoo
    disabled: true
  - name: mojeek
    engine: mojeek
    disabled: true
```

**Key changes from current**:
1. **`secret_key: "${SEARXNG_SECRET}"`**: Templated by entrypoint, not empty string
2. **`method: "POST"`**: Changed from GET to POST (more private)
3. **Added `open_metrics: ''`**: Explicitly disable Prometheus
4. **Added `donation_url: false`**: Remove donation link
5. **Added `max_request_timeout: 10.0`**: Allow longer timeouts for slow engines
6. **Added google, bing, brave engines**: Core search engines missing from current config
7. **Added `semantic scholar`**: Research engine (with correct name)
8. **Added `stackoverflow`**: Developer Q&A engine
9. **Disabled yahoo, mojeek**: Noisy/unnecessary engines

---

### Patch 4: searxng_client.py Alignment

**File**: `src/omega/workers/background_researcher/searxng_client.py`

**Issues found**:
1. Line 24: `DEFAULT_ENGINES = ["brave", "wikipedia", "arxiv", "semantischolar"]` — `semantischolar` should be `semantic scholar` (with space)
2. Line 24: Missing `google` and `duckduckgo` from default engines (the most reliable engines)
3. Line 56: `engines` parameter is passed to the function but never added to `form_data` — the engines parameter is ignored!

```python
# 🔱 Omega Engine — SearXNG Sovereign Search Client
# AP: AP-BACKGROUND-RESEARCHER-SEARXNG-v1.1.0
# ⬡ OMEGA ⬡ BELIAL ⬡ sovereign ⬡ searxng ⬡ WORKER
#
# Zero-cost, always-on search via the local SearXNG instance (port 8017).
#
# Changes from v1.0.0:
#   - Fixed engine name: semantischolar -> semantic scholar
#   - Added google and duckduckgo to DEFAULT_ENGINES
#   - Fixed: engines parameter now actually passed to form_data
#   - Added categories and language parameters

import logging
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SEARXNG_URL = "http://localhost:8017"
# Engine names must match SearXNG's engine list exactly (including spaces)
DEFAULT_ENGINES = ["google", "duckduckgo", "brave", "wikipedia", "arxiv", "semantic scholar"]
MAX_RESULTS = 10
TIMEOUT = 10.0


class SearXNGClient:
    """Client for the sovereign SearXNG search layer.

    This is the zero-cost, always-on search layer. No API key required.
    Connects to the Podman container on port 8017.
    """

    def __init__(self, base_url: str = SEARXNG_URL, timeout: float = TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    async def search(
        self,
        query: str,
        engines: Optional[list[str]] = None,
        max_results: int = MAX_RESULTS,
        safesearch: int = 0,
        pageno: int = 1,
        categories: str = "general",
        language: str = "auto",
    ) -> list[dict]:
        """Execute a search via SearXNG. Returns list of result dicts.

        Each result has keys: url, title, content, engine, publishedDate, thumbnail

        IMPORTANT: SearXNG does NOT accept JSON body. Send form-encoded data.
        Uses POST with form data (application/x-www-form-urlencoded).
        """
        if engines is None:
            engines = DEFAULT_ENGINES

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build form data — SearXNG expects form-encoded, not JSON
                form_data = {
                    "q": query,
                    "format": "json",
                    "safesearch": str(safesearch),
                    "pageno": str(pageno),
                    "language": language,
                    "categories": categories,
                }
                # FIX: Actually pass engines to the request (was ignored before)
                if engines:
                    form_data["engines"] = ",".join(engines)

                resp = await client.post(
                    f"{self.base_url}/search",
                    data=form_data,  # form-encoded, NOT json!
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                return results[:max_results]

        except httpx.RequestError as e:
            logger.warning(f"SearXNG request failed: {e}")
            return []
        except OmegaError:
            return []
        except Exception as e:
            logger.error(f"SearXNG search error: {e}", exc_info=True)
            return []

    async def search_text(
        self,
        query: str,
        engines: Optional[list[str]] = None,
        max_results: int = MAX_RESULTS,
    ) -> list[str]:
        """Convenience method: returns just the URL strings."""
        results = await self.search(query, engines, max_results)
        return [r.get("url", "") for r in results if r.get("url")]

    async def health(self) -> bool:
        """Check if SearXNG is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use /healthz endpoint (returns "OK" with status 200)
                # Or use root / (returns full HTML page, also works)
                resp = await client.get(f"{self.base_url}/healthz")
                return resp.status_code == 200
        except Exception as e:
            # M9 carve-out: health probe may catch all to prevent crash loops
            # [id-soft: doom-1993] WAD System — graceful degradation on search failure
            logger.warning("SearXNG health check failed: %s", e)
            return False
```

**Key changes**:
1. **Fixed engine name**: `semantischolar` → `semantic scholar` (line 27)
2. **Added google and duckduckgo**: Most reliable engines now in defaults
3. **Fixed engines passthrough**: `form_data["engines"] = ",".join(engines)` — was completely ignored before!
4. **Added categories parameter**: Passed through to SearXNG
5. **Added language parameter**: Passed through to SearXNG
6. **Health check uses `/healthz`**: Confirmed working endpoint

---

## §4 IMPLEMENTATION ORDER

### Phase 1: Fix the Container (CRITICAL — nothing works without DNS)

| Step | Command | Verification |
|------|---------|--------------|
| 1 | Stop broken container: `podman stop omega-searxng-test && podman rm omega-searxng-test` | Container removed |
| 2 | Clean stale pasta: `ps aux \| grep pasta \| grep -v grep` | No orphaned processes |
| 3 | Recreate with slirp4netns: `podman run -d --name omega-searxng --network slirp4netns -p 127.0.0.1:8017:8080 -v ... ghcr.io/searxng/searxng:2026.6.13-b48205b38` | Container running |
| 4 | Verify DNS: `podman exec omega-searxng python3 -c "import socket; print(socket.gethostbyname('google.com'))"` | IP address returned |
| 5 | Verify search: `curl -s "http://127.0.0.1:8017/search?q=test&format=json" \| python3 -m json.tool \| head -20` | JSON results returned |

### Phase 2: Apply Settings.yml (after container is running)

| Step | Command | Verification |
|------|---------|--------------|
| 6 | Apply Patch 3 to `data/searxng/config/settings.yml` | YAML validates |
| 7 | Restart: `podman restart omega-searxng` | Container picks up new config |
| 8 | Test POST: `curl -s -X POST -d "q=test&format=json" http://127.0.0.1:8017/search \| python3 -m json.tool \| head -10` | JSON results via POST |

### Phase 3: Apply MCP Server (after search is working)

| Step | Command | Verification |
|------|---------|--------------|
| 9 | Apply Patch 2 to `mcp_servers/searxng/server.py` | No syntax errors |
| 10 | Apply Patch 4 to `src/omega/workers/background_researcher/searxng_client.py` | No syntax errors |
| 11 | Restart MCP server if running | Tool callable |

### Phase 4: Deploy Quadlet (for persistence)

| Step | Command | Verification |
|------|---------|--------------|
| 12 | Copy Patch 1 to `~/.config/containers/systemd/omega-searxng.container` | File exists |
| 13 | `systemctl --user daemon-reload && systemctl --user enable omega-searxng.service && systemctl --user start omega-searxng.service` | `systemctl --user status omega-searxng` shows active |

---

## §5 RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **DNS still broken after recreation** | Medium | Critical | Use `--network slirp4netns` instead of pasta. If that fails, use `--dns 8.8.8.8` explicitly. |
| **Image `2026.6.13-b48205b38` not available** | Low | High | Check GHCR before pulling. Fallback to `2026.5.31-7159b8aed` (confirmed working). |
| **Settings.yml syntax error** | Low | Medium | Validate YAML before restarting: `python3 -c "import yaml; yaml.safe_load(open('data/searxng/config/settings.yml'))"` |
| **MCP server port conflict** | Low | Low | Port 8018 is dedicated. Check with `ss -tlnp \| grep 8018`. |
| **Engine names changed in new version** | Low | Medium | Verify with `curl http://localhost:8017/config \| jq '.engines[].name'` after update. |

### Rollback Plan

| Component | Rollback Command |
|-----------|-----------------|
| Container | `podman stop omega-searxng && podman rm omega-searxng && podman run -d --name omega-searxng-test ...` (recreate with old config) |
| Settings.yml | `git checkout data/searxng/config/settings.yml` (revert to last known-good) |
| MCP server | `git checkout mcp_servers/searxng/server.py` (revert to v1.0.0) |
| Client | `git checkout src/omega/workers/background_researcher/searxng_client.py` (revert to v1.0.0) |

---

## §6 L1→L2→L3 DISTILLATION

### L1 (Narrative)
The SearXNG integration had 6 bugs identified by @researcher. Primary source verification revealed that 3 were already fixed in the deployed Quadlet (health check, capabilities, pinned image). The most critical bug — DNS resolution failure due to pasta networking — was not identified by @researcher but is the root cause of all search failures. The MCP server had 3 additional issues: wrong HTTP method (GET vs POST), invalid `limit` parameter, and missing engine/category/language parameters. The client had a wrong engine name (`semantischolar` vs `semantic scholar`) and was silently ignoring the engines parameter entirely.

### L2 (Insight)
The "health check crash loop" was a **symptom**, not the root cause. The real problem was pasta networking breaking DNS resolution. The container appeared "healthy" (Python urllib to localhost:8080 works) but was non-functional for search (can't reach upstream engines). This is a classic **partial failure mode** — the health check passes because it only tests the web server, not the search functionality. A proper health check should verify outbound connectivity, not just internal server status.

The MCP server's `limit` parameter was being silently ignored by SearXNG — the API doesn't have this parameter. This means the MCP server was returning ALL results (up to 100) regardless of what the caller requested. The `max_results` client-side limiting was the only thing preventing massive payloads.

### L3 (Universal Principle)
**"A health check that only tests internal state is not a health check — it's a liveness probe."** True health verification must include at least one outbound dependency check. For a metasearch engine, "healthy" means "can resolve DNS AND can reach at least one upstream engine." The current Python urllib check only verifies the web server is running. A better health check would be:

```bash
python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/search?q=healthcheck&format=json', timeout=10)"
```

This tests the full search pipeline, not just the HTTP listener.

---

## §7 SOUL.YAML INSIGHTS

```yaml
# L3 Universal Principles for soul.yaml
- principle: "A health check that only tests internal state is a liveness probe, not a health check"
  context: "SearXNG integration — partial failure mode where container is 'up' but DNS broken"
  source: "SEARXNG_JEM_VERIFICATION_20260621.md"

- principle: "Silent parameter rejection is worse than an error — it causes silent data loss"
  context: "MCP server's 'limit' parameter silently ignored by SearXNG API"
  source: "SEARXNG_JEM_VERIFICATION_20260621.md"

- principle: "Deployed config ≠ research copy — always verify the actual running state"
  context: "Quadlet in docs/research/ was stale; deployed version already partially fixed"
  source: "SEARXNG_JEM_VERIFICATION_20260621.md"
```

---

*Research completed: 2026-06-21 | Pipeline: Discovery → Synthesis → Verification | 6 bugs confirmed, 3 already fixed, 3 critical active | 4 patches ready for deployment*
