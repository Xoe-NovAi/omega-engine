<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# SearXNG Deep Research — Sovereign Search Infrastructure
## Research Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-06-21 |
| **Researcher** | Sovereign Master Researcher (Omega Engine) |
| **Items Covered** | 18/18 (all gaps filled) |
| **Sources Used** | 45+ primary sources (official docs, GitHub repos, issues, PRs, DeepWiki) |
| **Status** | COMPLETE |

---

## Tier 1: SearXNG Core

### 1.1 Architecture

**What we already knew**: SearXNG is a Python-based metasearch engine. It aggregates results from 70+ search engines.

**New findings**:

- **WSGI Server**: SearXNG uses **Granian** (replaced uWSGI in 2025 via PR #4820). Granian is configured entirely via environment variables (`$GRANIAN_*`), enabling immutable container configuration. The entrypoint no longer needs to template settings at runtime for the WSGI layer.
  - Source: https://docs.searxng.org/admin/installation-granian.html, PR #4820

- **Request Pipeline** (5 stages):
  1. **Query Parsing** (`RawTextQuery`): Parses bangs (`!`), language (`:`), timeout (`<`), external bangs (`!!`), and feeling-lucky syntax
  2. **Query Validation** (`webadapter.py`): Bridges HTTP form data → validated `SearchQuery` objects. Validates engine refs, tokens, language, safe search, time range, timeout, page number
  3. **Search Orchestration** (`SearchWithPlugins`): Coordinates plugin integration (pre_search, post_search, on_result) and parallel engine dispatch
  4. **Parallel Engine Execution**: Each engine gets its own `threading.Thread`. Uses Flask's `copy_current_request_context` for context propagation. Timeout calculated as `min(engine_timeout, query_timeout, max_request_timeout)`
  5. **Result Aggregation** (`ResultContainer`): Deduplicates by URL, calculates scores based on position + engine weight + cross-engine frequency, groups by category
  - Source: https://deepwiki.com/searxng/searxng/3-search-processing-pipeline

- **Engine Processor Hierarchy**:
  - `OnlineProcessor` — standard HTTP engines (most engines)
  - `OnlineCurrencyProcessor` — currency conversion syntax
  - `OfflineProcessor` — local/non-networked sources
  - `OnlineDictionaryProcessor` — dictionary lookups
  - `OnlineUrlSearchProcessor` — URL-based searches
  - Source: `searx/search/processors/__init__.py`

- **Network Layer**: Centralized HTTP client pool via `searx.network`. Handles connection pooling (`pool_connections=100`, `pool_maxsize=20`), HTTP/2 support, proxy round-robin, retry logic. Uses `httpx` under the hood.
  - Source: https://docs.searxng.org/admin/settings/settings_outgoing.html

- **Error Handling**: `OnlineProcessor` monitors for `SearxEngineCaptchaException` and `SearxEngineTooManyRequestsException`, triggering engine suspension via `SuspendedStatus`. Engines are temporarily removed from the active pool.
  - Source: `searx/search/processors/online.py:164-212`

**Architecture diagram** (from DeepWiki):
```
HTTP Request → Flask webapp → webadapter.py (validate)
  → RawTextQuery (parse) → SearchQuery (model)
  → SearchWithPlugins.search()
    → pre_search (plugins)
    → _get_requests() → build RequestParams per engine
    → search_multiple_requests() → threading.Thread per engine
      → PROCESSORS[name].search() → searx.network (httpx pool)
    → post_search (plugins)
  → ResultContainer.extend() → dedup + score
  → close() → get_ordered_results()
  → HTML/JSON/CSV/RSS rendering
```

### 1.2 settings.yml Deep Dive

**What we already knew**: `use_default_settings: true` merges with defaults. `secret_key` must be changed.

**New findings — Complete reference**:

#### Settings Load Order
1. `SEARXNG_SETTINGS_PATH` env var (file or folder)
2. `/etc/searxng/settings.yml` (default container path)
3. Built-in `searx/settings.yml` (fallback)

With `use_default_settings: true`, user settings are **merged** on top of defaults. Engine sections merge by `name`. Engine lists support `remove:` and `keep_only:` filters.
- Source: https://docs.searxng.org/admin/settings/settings.html

#### `general:` Section
```yaml
general:
  debug: false                    # $SEARXNG_DEBUG — interactive debugger, verbose logging
  instance_name: "SearXNG"        # Display name
  privacypolicy_url: false        # Link or false
  donation_url: false             # Link or false
  contact_url: false              # mailto: or web form
  enable_metrics: true            # Record anonymous stats at /stats, /stats/errors
  open_metrics: ''                # Set password to expose OpenMetrics at /metrics (HTTP Basic Auth)
```
- **Omega note**: Set `enable_metrics: false` for sovereign privacy (M8 compliance). Set `open_metrics: ''` (empty) to disable Prometheus endpoint.
- Source: https://docs.searxng.org/admin/settings/settings_general.html

#### `server:` Section
```yaml
server:
  secret_key: "ultrasecretkey"    # $SEARXNG_SECRET — MUST change. Used for image proxy + Valkey encryption
  port: 8888                      # $SEARXNG_PORT — default 8888, Omega uses 8080 internally
  bind_address: "127.0.0.1"       # $SEARXNG_BIND_ADDRESS — localhost only for sovereignty
  base_url: false                 # $SEARXNG_BASE_URL — set to http://localhost:8017 for Omega
  limiter: false                  # $SEARXNG_LIMITER — requires Valkey. Disable for localhost-only
  public_instance: false          # $SEARXNG_PUBLIC_INSTANCE — false for sovereign use
  image_proxy: false              # $SEARXNG_IMAGE_PROXY — proxy images through SearXNG
  method: "POST"                  # $SEARXNG_METHOD — GET or POST. POST hides query in URL
  http_protocol_version: "1.0"    # HTTP/1.0 or 1.1
  default_http_headers:
    X-Content-Type-Options: nosniff
    X-Download-Options: noopen
    X-Robots-Tag: noindex, nofollow
    Referrer-Policy: no-referrer
```
- **Critical**: `secret_key` is used for: (1) Flask session signing, (2) image proxy URL signing, (3) Valkey data encryption. If empty/missing, SearXNG logs an ERROR and may refuse to start.
- Source: https://docs.searxng.org/admin/settings/settings_server.html, GitHub issue #3113

#### `search:` Section
```yaml
search:
  safe_search: 0                  # 0=None, 1=Moderate, 2=Strict
  autocomplete: ""                # ""=off, "duckduckgo", "google", "bing", "wikipedia", etc.
  autocomplete_min: 4             # Min chars before autocomplete triggers
  favicon_resolver: ""            # ""=off, "duckduckgo", "google", "yandex", "allesedv"
  default_lang: "auto"            # Default search language
  ban_time_on_fail: 5             # Minutes to ban engine on failure
  max_ban_time_on_fail: 120       # Max ban time in minutes
  formats:                        # Allowed output formats — CRITICAL for API access
    - html                        # Web UI
    # - json                      # Enable for MCP/API access
    # - rss
    # - csv
```
- **Omega note**: Must add `json` to `formats:` for MCP server to work. Without it, `?format=json` returns 403 Forbidden.
- Source: https://docs.searxng.org/admin/settings/settings.html

#### `outgoing:` Section
```yaml
outgoing:
  request_timeout: 3.0            # Default timeout per engine (seconds)
  # max_request_timeout: 10.0     # Max allowed timeout
  useragent_suffix: ""            # Contact info appended to user-agent
  pool_connections: 100           # Max concurrent connections
  pool_maxsize: 20                # Max keep-alive connections per pool
  enable_http2: true              # HTTP/2 support (httpx)
  # proxies:                      # Proxy configuration (round-robin if multiple)
  #   all://:
  #     - http://proxy:8080
  # using_tor_proxy: false        # Route through Tor
  # extra_proxy_timeout: 10       # Extra seconds for proxy latency
  # source_ips:                   # Multi-interface source selection
```
- Source: https://docs.searxng.org/admin/settings/settings_outgoing.html

#### `engines:` Section (Key engines)
```yaml
engines:
  # --- Enabled by default ---
  - name: google
    engine: google
    shortcut: go
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
  - name: bing
    engine: bing
    shortcut: bi
    disabled: true                 # Disabled by default
  - name: brave
    engine: brave
    shortcut: br
  - name: arxiv
    engine: arxiv
    shortcut: arx
  - name: stackoverflow
    engine: stackoverflow
    shortcut: so
  - name: github
    engine: github
    shortcut: gh
```
- **Engines requiring API keys** (inactive by default): `braveapi` (Brave API), `mojeek` (needs API key for full access)
- **Engines that work out of box**: Google, DuckDuckGo, Bing, Brave (scrape mode), Wikipedia, ArXiv, GitHub, StackOverflow, Reddit, YouTube, and 60+ more
- Source: https://docs.searxng.org/admin/settings/settings_engines.html

### 1.3 Health Check Best Practices

**What we already knew**: We were using `curl` against `/healthz` — both wrong.

**New findings**:

- **Correct endpoint**: SearXNG exposes `/healthz` at the Flask level (confirmed in `webapp.py:616-618`). However, the **root `/`** endpoint also works and is simpler.
  - Source: GitHub issue #4026, PR #4366

- **`curl` is NOT in the image**: The SearXNG container image is based on Alpine and ships Python, not curl. wget IS available.
  - Source: GitHub issue #4026 discussion, PR #4366

- **HEALTHCHECK was removed from Dockerfile** (PR #4941, 2025-06-26) because the port is hardcoded to 8080 but users may configure different ports. Health checks are now expected to be defined in compose/quadlet.
  - Source: PR #4941, issue #4906

- **Correct health check patterns** (ranked by reliability):

  1. **wget (recommended — available in image)**:
     ```bash
     wget --quiet --tries=1 --spider http://127.0.0.1:8080/ || exit 1
     ```
     Note: Use `127.0.0.1` not `localhost` — wget tries IPv6 first on `localhost`, which fails if SearXNG listens only on IPv4.
     - Source: PR #4378

  2. **Python urllib (guaranteed available)**:
     ```bash
     python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz')" || exit 1
     ```
     - Source: StackOverflow #48092770

  3. **wget with IPv4 fallback**:
     ```bash
     wget --quiet --tries=1 --spider -4 http://localhost:8080/ || exit 1
     ```

- **Startup grace period**: SearXNG takes 5-15 seconds to start (Granian init + engine loading). Use `start_period: 30s` in Docker healthcheck or `TimeoutStartSec=90s` in systemd.
  - Source: GitHub issue #4379

- **Omega Quadlet bug identified**: Our current `omega-searxng.container` uses `curl` (not available) and `/healthz` (works but `/` is simpler). Must fix to use `wget` or `python3`.

### 1.4 SEARXNG_SECRET

**What we already knew**: Must be changed from default. Generated with `openssl rand -hex 32`.

**New findings**:

- **Purpose**: Used for:
  1. **Flask session signing** — prevents session tampering
  2. **Image proxy URL signing** — when `image_proxy: true`, images are proxied through SearXNG with signed URLs
  3. **Valkey/Redis data encryption** — the limiter encrypts IP hashes in Valkey using this secret
  4. **CSRF protection** — form submissions validated against this key

- **What happens if empty/missing**: SearXNG logs `ERROR:searx.webapp: server.secret_key is not changed. Please use something else instead of ultrasecretkey.` and **refuses to start** if `image_proxy` or `limiter` is enabled. For local-only use without these features, it may start but with degraded security.
  - Source: GitHub issue #3113, NixOS issue #292652

- **Generation method**:
  ```bash
  openssl rand -hex 32
  ```
  Produces a 64-character hex string. The searxng-docker README recommends:
  ```bash
  sed -i "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml
  ```

- **Container injection**: The entrypoint script substitutes `${SEARXNG_SECRET}` in `settings.yml`. This means you can set `secret_key: "${SEARXNG_SECRET}"` in your mounted `settings.yml` and provide the actual value via environment variable.
  - Source: searxng-docker README, GitHub issue #5718

- **Omega recommendation**: Generate once, store in a `.env` file (not in git), inject via `Environment=SEARXNG_SECRET=...` in Quadlet.

---

## Tier 2: Containerization & Deployment

### 2.1 Docker/Podman Deployment Patterns

**What we already knew**: SearXNG runs as a Podman container with Quadlet.

**New findings**:

- **Official image**: `ghcr.io/searxng/searxng` (GHCR mirror, preferred) or `docker.io/searxng/searxng` (DockerHub, rate-limited)
  - Source: https://docs.searxng.org/admin/installation-docker.html

- **Two volume mounts required**:
  1. `/etc/searxng/` — Configuration (settings.yml, limiter.toml, favicons.toml)
  2. `/var/cache/searxng/` — Persistent data (faviconcache.db, SQLite)
  - Source: https://docs.searxng.org/admin/installation-docker.html#volumes

- **Capabilities needed**:
  - `CHOWN` — First-boot: entrypoint chowns `/etc/searxng/` and `/var/cache/searxng/` to `searxng:searxng` (UID 977)
  - `SETGID` — Switch to searxng group
  - `SETUID` — Switch to searxng user
  - `DAC_OVERRIDE` — **Debatable**. Was added in 2022 (PR searxng-docker#110) but maintainer noted it may not be needed with proper `FORCE_OWNERSHIP=false` and pre-owned volumes
  - Source: GitHub searxng-docker issue #30, PR #110

- **UserNS=keep-id compatibility**: SearXNG expects volume contents owned by UID 977 (searxng:searxng). With `UserNS=keep-id` + `User=1000`, the host user maps to container UID 1000, but SearXNG runs as 977 internally. This creates a UID mismatch.
  - **Solution**: Either (a) pre-chown volumes to 977:977 on host, or (b) use `FORCE_OWNERSHIP=true` (default) which lets the entrypoint chown at startup, or (c) use `--uidmap +$(id -u):977:1 --gidmap +$(id -g):977:1 --user 0:0` (from Discussion #5279)
  - Source: GitHub Discussion #5279, issue #6044

- **Rootless Podman**: The searxng-docker repo notes: "We are not yet aiming to ensure that containers in rootless mode work flawlessly." The `update-ca-certificates` script may fail silently (harmless if not loading custom CAs).
  - Source: GitHub searxng-docker issue #442

- **Read-only rootfs**: Supported with `--read-only` + tmpfs for `/tmp` and `/var/tmp`. The entrypoint needs write access to `/etc/searxng/` (for uwsgi.ini templating in old versions) and `/var/cache/searxng/`.
  - Source: Omega Quadlet config, PR #4820 (Granian removes uwsgi.ini templating need)

- **FORCE_OWNERSHIP**: When `true` (default), the entrypoint runs `chown -R searxng:searxng /etc/searxng/ /var/cache/searxng/` on every start. Set to `false` to prevent ownership changes on shared volumes.
  - Source: PR #4820

### 2.2 Health Check Patterns

**What we already knew**: We had a broken health check using curl against /healthz.

**New findings**:

- **wget IS in the image** (Alpine-based, includes busybox wget)
- **curl is NOT in the image**
- **`/healthz` IS a valid endpoint** (Flask-level, not Granian-level)
- **Root `/` also works** and is simpler

**Recommended Quadlet health check**:
```ini
# Option A: wget (available in image, use 127.0.0.1 not localhost)
HealthCmd=wget --quiet --tries=1 --spider http://127.0.0.1:8080/ || exit 1

# Option B: python3 (guaranteed available)
HealthCmd=python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/')" || exit 1
```

- **Why 127.0.0.1 not localhost**: wget tries IPv6 first on `localhost`. If SearXNG binds to `0.0.0.0` (IPv4 only), wget fails with "Connection refused". PR #4378 fixed this by switching to `127.0.0.1`.
  - Source: PR #4378, issue #4379

- **Startup timing**: Use `HealthStartPeriod=30s` (Quadlet) or `start_period: 30s` (Docker compose) to give Granian time to initialize.

### 2.3 Entrypoint Wrappers

**What we already knew**: The entrypoint templates settings.yml with secret substitution.

**New findings**:

- **Granian migration (PR #4820)**: The entrypoint no longer templates uwsgi.ini. Granian is configured entirely via `$GRANIAN_*` environment variables. This simplifies the entrypoint significantly.
  - Source: PR #4820

- **Secret substitution**: The entrypoint performs `${SEARXNG_SECRET}` → actual value substitution in the mounted `settings.yml`. This means:
  1. Mount a `settings.yml` with `secret_key: "${SEARXNG_SECRET}"`
  2. Set `SEARXNG_SECRET=<actual-secret>` as an environment variable
  3. The entrypoint substitutes on every container start

- **FORCE_OWNERSHIP**: When `true`, entrypoint chowns mounted volumes. When `false`, no chown (use when volumes are pre-owned).
  - Source: PR #4820

### 2.4 Image Pinning Strategy

**What we already knew**: We were using `:latest` which broke on 2026.6.2 (KeyError: 'default_doi_resolver').

**New findings**:

- **Tag format**: `YYYY.M.D-<short-git-hash>` (e.g., `2026.6.13-b48205b38`)
- **Release frequency**: Rolling release, multiple tags per day (sometimes 5-10 per day)
- **No semantic versioning**: The project uses rolling releases based on master branch commits
  - Source: https://hub.docker.com/r/searxng/searxng/tags, CHANGELOG.rst

- **Pinning strategy for Omega**:
  1. Pin to a specific tag: `ghcr.io/searxng/searxng:2026.6.13-b48205b38`
  2. Track via `AutoUpdate=registry` (Podman Quadlet auto-update)
  3. Update manually after verifying changelog: `podman pull ghcr.io/searxng/searxng:<new-tag>`

- **Known-bad tags**: 2026.6.2 series had `KeyError: 'default_doi_resolver'` bug. Always check https://github.com/searxng/searxng/issues before updating.

- **GHCR mirror**: Prefer `ghcr.io/searxng/searxng` over DockerHub to avoid rate limits.
  - Source: https://docs.searxng.org/admin/installation-docker.html#registries

---

## Tier 3: MCP Server Integration

### 3.1 SearXNG API Reference

**What we already knew**: SearXNG has a JSON API at `/search?format=json`.

**New findings**:

- **Endpoints**: Both `/` and `/search` support GET and POST
- **Response formats**: `json`, `csv`, `rss` (must be enabled in `search.formats` in settings.yml)
- **Request format**: Form-encoded data (NOT JSON body). Use `data=form_data` not `json=form_data`.
  - Source: Background researcher `searxng_client.py` line 53: "IMPORTANT: SearXNG does NOT accept JSON body. Send form-encoded data."

**Full parameter reference**:
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `q` | Yes | — | Search query. Supports engine-specific syntax (e.g., `site:github.com`) |
| `format` | No | html | `json`, `csv`, `rss` (must be in `search.formats`) |
| `categories` | No | general | Comma-separated: `general`, `images`, `videos`, `news`, `music`, `files`, `it`, `science`, `social media` |
| `engines` | No | all enabled | Comma-separated engine names: `google,bing,duckduckgo` |
| `language` | No | auto | Language code: `en`, `en-US`, `de`, `fr`, `all` |
| `pageno` | No | 1 | Page number (1-indexed) |
| `time_range` | No | none | `day`, `week`, `month`, `year` |
| `safesearch` | No | 0 | 0=None, 1=Moderate, 2=Strict |

**JSON response schema**:
```json
{
  "query": "search term",
  "number_of_results": 1234,
  "results": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "content": "Snippet text...",
      "engine": "google",
      "engines": ["google", "bing"],
      "position": 1,
      "category": "general",
      "parsed_url": ["https", "example.com", "/page", "", "", ""],
      "publishedDate": "2026-01-15T00:00:00",
      "thumbnail": "https://...",
      "img_src": "https://...",
      "score": 8.5
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [],
  "suggestions": ["alternative query 1", "alternative query 2"]
}
```
- Source: https://docs.searxng.org/dev/search_api.html

### 3.2 MCP Tool Pattern

**What we already knew**: Omega has a basic `searxng_search` tool in `mcp_servers/searxng/server.py`.

**New findings**:

- **Existing implementations** (6+ MCP servers wrapping SearXNG):
  - `pete-builds/mcp-searxng` — 9 tools including deep search, person lookup, URL reader (FastMCP, Python)
  - `88plug/searxng-mcp` — Token-efficient, stdio/http transports, Docker-bundled option (FastMCP, Python)
  - `ihor-sokoliuk/mcp-searxng` — Node.js, min_score filtering, /config validation
  - `voidog/searxng-mcp` — TypeScript, SSRF protection, Readability-based URL fetch
  - `dandehoon/searxng-mcp` — Single Docker image bundling SearXNG + MCP server
  - `zatevakhin/searxng-mcp` — Rust, NixOS module, Obscura backend for JS rendering
  - Source: GitHub search results

- **Omega's current tool is minimal** (67 lines). Gaps:
  1. No `categories` parameter
  2. No `engines` parameter
  3. No `time_range` parameter
  4. No `language` parameter
  5. Uses GET instead of POST (POST is more private)
  6. No pagination support
  7. No `read_url` tool (fetch + extract page content)
  8. No health check tool
  9. No engine listing tool

- **Recommended Omega MCP tool design**:
  ```python
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
      Engines: comma-separated (e.g., "google,bing,duckduckgo")
      Time range: day, week, month, year (or empty for all time)
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
          resp = await client.post(f"{SEARXNG_URL}/search", data=form_data)
          resp.raise_for_status()
          data = resp.json()
          # ... format results
  ```

### 3.3 Rate Limiting

**What we already knew**: SearXNG has a built-in limiter.

**New findings**:

- **Limiter requires Valkey** (Redis-compatible). Without Valkey, the limiter cannot function.
  - Source: https://docs.searxng.org/admin/searx.limiter.html

- **For localhost-only Omega use**: Disable the limiter (`limiter: false`). The limiter is designed for public instances to prevent bots from getting the instance flagged by upstream engines. A localhost-only instance serving a single user has no bot problem.

- **How the limiter works** (when enabled):
  1. **IP identification**: Client IP resolved to network CIDR (/32 for IPv4, /48 for IPv6)
  2. **Sliding window rate limiting** (`ip_limit`):
     - Burst window: 20 seconds, max 15 requests
     - Long window: 600 seconds, max 150 requests
     - Suspicious IPs: 10 requests per 30-day window
  3. **Link token verification** (`link_token`): Checks if client requested `/client.css` (contains random token). If not, request is "suspicious" and rates are tightened.
  4. **IP lists**: `pass_ip` for trusted networks, `block_ip` for banned IPs
  - Source: https://docs.searxng.org/src/searx.botdetection.html, `searx/botdetection/ip_limit.py`

- **Configuration**: `/etc/searxng/limiter.toml`
  ```toml
  [botdetection.ip_limit]
  filter_link_local = true    # Don't rate-limit local addresses
  link_token = false          # Disable link_token for API use
  
  [botdetection.ip_lists]
  pass_ip = ['127.0.0.0/8']  # Pass localhost
  ```

- **Self-throttling risk**: If the limiter is enabled and Valkey is not running, SearXNG logs an error but continues without rate limiting (for non-public instances). For public instances, it exits with error.
  - Source: `searx/limiter.py:53-60`

---

## Tier 4: Security & Sovereignty

### 4.1 Bot Detection

**What we already knew**: SearXNG has bot detection to protect upstream engines.

**New findings**:

- **User-Agent filtering**: The limiter checks for known bot user-agents (curl, wget, python-requests, etc.). If detected, requests are blocked or rate-limited.
  - Source: `searx/botdetection/ip_limit.py`

- **For Omega's MCP server**: The MCP server makes requests from localhost. If the limiter is enabled, it may block requests from the MCP server's User-Agent. Solution: either (a) disable the limiter for localhost, or (b) add `127.0.0.0/8` to `pass_ip`.

- **Impact on upstream engines**: Without the limiter, a localhost-only instance serving a single user will NOT trigger upstream bot detection (low volume, residential IP). The limiter is critical only for public instances.

### 4.2 Network Isolation

**What we already knew**: Omega binds SearXNG to `127.0.0.1:8017`.

**New findings**:

- **Container network isolation**: When using `PublishPort=127.0.0.1:8017:8080`, the container is only accessible from localhost. External access requires explicit port forwarding.

- **Outbound connectivity**: SearXNG needs outbound internet access to query upstream engines (Google, Bing, DuckDuckGo, etc.). The container must have:
  - DNS resolution (typically provided by Podman's network plugin)
  - Outbound HTTPS (port 443) to ~70+ engine domains
  - No `--network=none` or restrictive egress policies

- **Impact of blocking outbound**: If outbound is blocked, ALL engines fail. SearXNG returns empty results. The health check still passes (Flask responds, just no search results).

- **Tor routing**: SearXNG supports routing all outgoing requests through Tor (`using_tor_proxy: true` + `proxies` configuration). This provides maximum privacy but adds latency.
  - Source: https://docs.searxng.org/admin/settings/settings_outgoing.html

### 4.3 Privacy

**What we already knew**: SearXNG doesn't track users.

**New findings**:

- **What SearXNG logs**:
  - **Default**: No search query logging. The `enable_metrics` setting records anonymous engine stats (response times, error counts) at `/stats`.
  - **debug mode**: Verbose logging including request details. NEVER enable in production.
  - **Valkey data**: Only IP hashes (not raw IPs) stored, with 10-minute expiry.
  - Source: https://docs.searxng.org/admin/settings/settings_general.html

- **Privacy settings for Omega**:
  ```yaml
  general:
    debug: false
    enable_metrics: false       # Disable anonymous stats
    open_metrics: ''            # Disable Prometheus endpoint
    donation_url: false
    contact_url: false
    privacypolicy_url: false
  
  server:
    image_proxy: false          # Don't proxy images (saves memory)
    limiter: false              # No need for localhost
    public_instance: false      # Not a public instance
  ```

- **No telemetry**: SearXNG has zero phone-home, zero analytics, zero external data collection. This aligns with Omega's M8 (Zero Telemetry) mandate.

- **Cookie usage**: SearXNG uses cookies only for user preferences (language, safe search, etc.). Preferences can also be passed via URL parameters, eliminating cookies entirely.

### 4.4 Engine Security

**What we already knew**: Most engines work without API keys.

**New findings**:

- **Engines requiring API keys** (inactive by default):
  - `braveapi` — Brave Search API (requires API key from brave.com/api)
  - `mojeek` — Mojeek search (requires API key)
  - `arch linux wiki` — requires token
  - Source: https://docs.searxng.org/admin/settings/settings_engines.html

- **Engines that work out of box** (no API key needed):
  - Google, Google Images, Google News, Google Videos, Google Scholar
  - Bing, Bing Images, Bing News, Bing Videos
  - DuckDuckGo
  - Brave (scrape mode, not API)
  - Wikipedia
  - ArXiv
  - GitHub
  - StackOverflow
  - Reddit
  - YouTube
  - Startpage
  - Yahoo
  - Mojeek (limited without API key)
  - 60+ more engines

- **Engine security consideration**: Scrape-mode engines (Google, Bing) may detect SearXNG as a bot and return CAPTCHAs or empty results. This is the primary reliability concern. The limiter helps mitigate this for public instances.

- **Private engines**: Any engine can be made private with a `tokens:` list. Only requests containing the token can use that engine.
  ```yaml
  engines:
    - name: my-private-engine
      tokens: ['my-secret-token']
  ```

---

## Tier 5: Comparison & Alternatives

### 5.1 SearXNG vs Alternatives

**What we already knew**: SearXNG is the leading self-hosted metasearch engine.

**New findings**:

| Feature | SearXNG | SearX (original) | Whoogle | YaCy | Brave Search |
|---------|---------|-----------------|---------|------|-------------|
| **Type** | Metasearch | Metasearch | Google proxy | P2P crawler | First-party index |
| **Engines** | 70+ | 70+ | Google only | Own index | Own index |
| **Self-hosted** | Yes | Yes | Yes | Yes | No (API) |
| **API access** | JSON/CSV/RSS | JSON | No | Yes | Yes (paid) |
| **Privacy** | No tracking | No tracking | No tracking | Full decentralization | Managed |
| **Active development** | Very active (2026) | Unmaintained | Active | Active | N/A |
| **RAM usage** | ~150-300MB | ~150MB | ~50-100MB | ~500MB+ | N/A |
| **Setup complexity** | Moderate | Moderate | Simple | Complex | Simple |
| **Result quality** | Broad, configurable | Broad | Google-quality | Variable | High |
| **Maturity** | Fork of SearX (2021) | Original (2014) | 2021 | 2013 | 2023 |
| **License** | AGPL-3.0 | AGPL-3.0 | MIT | Apache-2.0 | Proprietary |

- **Why SearXNG for Omega**: (1) Most active development, (2) widest engine support, (3) JSON API for MCP integration, (4) proven Podman compatibility, (5) zero telemetry, (6) configurable for sovereign use
- Source: https://selfhostwise.com/posts/self-hosted-search-engines-in-2026-searxng-vs-whoogle-complete-guide/, https://scavio.dev/compare/yacy/vs-searxng

### 5.2 SearXNG vs Direct APIs

**What we already knew**: SearXNG aggregates multiple engines; direct APIs give single-engine access.

**New findings**:

| Criteria | SearXNG (Sovereign) | Direct API (Brave/Tavily) |
|----------|-------------------|--------------------------|
| **Cost** | Free (self-hosted) | Per-query pricing |
| **Rate limits** | Upstream-dependent, self-managed | Provider-enforced |
| **Result quality** | Multi-engine aggregation | Single-engine, higher relevance |
| **Privacy** | Full control, no third-party queries | Provider sees all queries |
| **Reliability** | Variable (upstream bot detection) | High (official API) |
| **Setup** | Self-hosting required | API key only |
| **Offline capability** | No (needs internet for engines) | No |
| **Customization** | Engine weights, categories, filters | Limited to API params |

- **When to use SearXNG**: Privacy-sensitive queries, high-volume research, multi-engine aggregation, zero-cost requirement, agent grounding
- **When to use direct APIs**: Production reliability critical, single-engine precision needed, high-volume where upstream blocking is a risk
- **Omega strategy**: SearXNG as primary (sovereign, zero-cost), direct APIs as fallback (for reliability-critical paths)
- Source: https://cosmo-edge.com/searxng-sovereign-search-ai-guide/

### 5.3 Ecosystem

**What we already knew**: SearXNG integrates with various tools.

**New findings**:

- **MCP ecosystem**: 6+ MCP server implementations (see Tier 3.2). The MCP protocol has made SearXNG the de facto search backend for AI agents.
  - Source: GitHub search results

- **Open WebUI integration**: Native toggle for web search in Open WebUI, routing queries through SearXNG.
  - Source: https://cosmo-edge.com/searxng-sovereign-search-ai-guide/

- **Drupal AI integration**: SearXNG as privacy-first web search for Drupal AI assistants.
  - Source: https://www.drupal.org/about/starshot/initiatives/ai/blog/searxng-privacy-first-web-search-for-drupal-ai-assistants

- **SecAI OS**: SearXNG as core component with Tor routing, systemd sandboxing, and seccomp filtering.
  - Source: https://github.com/SecAI-Hub/llm-search-mediator

- **NixOS modules**: Multiple NixOS modules for SearXNG deployment.
  - Source: zatevakhin/searxng-mcp NixOS module

- **LLM integration pattern**: SearXNG → MCP server → LLM agent. This is the standard pattern for giving AI models web search capabilities without API keys.

---

## Omega-Specific Configuration Recommendations

### Concrete settings.yml for Omega

```yaml
# Omega SearXNG Configuration
# Sovereign metasearch — localhost-only, zero telemetry, MCP-ready

use_default_settings: true

general:
  debug: false
  instance_name: "Omega Search"
  privacypolicy_url: false
  donation_url: false
  contact_url: false
  enable_metrics: false          # M8: Zero telemetry
  open_metrics: ''               # Disable Prometheus

server:
  secret_key: "${SEARXNG_SECRET}" # Templated by entrypoint
  port: 8080                     # Internal container port
  bind_address: "0.0.0.0"        # Bind all interfaces inside container
  base_url: "http://localhost:8017"  # External access URL
  limiter: false                 # No limiter for localhost-only
  public_instance: false
  image_proxy: false             # Save memory
  method: "POST"                 # POST hides query in URL (more private)
  http_protocol_version: "1.0"

search:
  safe_search: 0
  autocomplete: ""
  default_lang: "en"
  formats:
    - html
    - json                       # REQUIRED for MCP/API access

outgoing:
  request_timeout: 3.0
  pool_connections: 100
  pool_maxsize: 20
  enable_http2: true

# Engine selection — curated for Omega use cases
engines:
  # Core search
  - name: google
    engine: google
    shortcut: go
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
  - name: bing
    engine: bing
    shortcut: bi
    disabled: false              # Enable Bing
  - name: brave
    engine: brave
    shortcut: br

  # Technical/Research
  - name: arxiv
    engine: arxiv
    shortcut: arx
  - name: github
    engine: github
    shortcut: gh
  - name: stackoverflow
    engine: stackoverflow
    shortcut: so
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

### Exact Quadlet Changes Needed

**Current bugs in `omega-searxng.container`**:
1. ❌ `HealthCmd=curl -sf http://localhost:8080/healthz || exit 1` — curl not in image, use wget
2. ❌ `HealthCmd` uses `localhost` — wget tries IPv6 first, fails. Use `127.0.0.1`
3. ❌ Image tag `:latest` — unpinned, breaks on upstream bugs
4. ❌ Missing `AddCapability=CHOWN SETGID SETUID` — needed for first-boot
5. ❌ `--cap-drop=ALL` without `--cap-add` — drops required capabilities

**Fixed Quadlet**:
```ini
[Unit]
Description=Omega SearXNG — Sovereign Metasearch Engine
After=network-online.target
Wants=network-online.target

[Container]
UserNS=keep-id
User=1000
Image=ghcr.io/searxng/searxng:2026.6.13-b48205b38
ContainerName=omega-searxng
AutoUpdate=registry

# Port — localhost only
PublishPort=127.0.0.1:8017:8080

# Configuration
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/:U
Volume=%h/Documents/Xoe-NovAi/omega-library/searxng/data:/var/cache/searxng/:U

# Environment
Environment=SEARXNG_SECRET=<generated-secret-here>
Environment=SEARXNG_BASE_URL=http://localhost:8017
Environment=FORCE_OWNERSHIP=true

# Capabilities — CHOWN for first-boot, SETGID/SETUID for user switching
AddCapability=CHOWN SETGID SETUID
DropCapability=ALL

# Security
PodmanArgs=--memory=512m
PodmanArgs=--memory-reservation=256m
PodmanArgs=--cpus=1.0
PodmanArgs=--pids-limit=64
PodmanArgs=--read-only
PodmanArgs=--security-opt=no-new-privileges
PodmanArgs=--tmpfs=/tmp:rw,size=64m
PodmanArgs=--tmpfs=/var/tmp:rw,size=32m

# Health check — wget (available in image), 127.0.0.1 (IPv4 only)
HealthCmd=wget --quiet --tries=1 --spider http://127.0.0.1:8080/ || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=30s
HealthOnFailure=restart

[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s

[Install]
WantedBy=multi-user.target
```

### MCP Server Tool Design

**Current gaps in `mcp_servers/searxng/server.py`**:
1. Missing `categories`, `engines`, `language`, `time_range`, `pageno` parameters
2. Uses GET instead of POST (less private)
3. No `read_url` tool (fetch + extract page content)
4. No health check tool
5. No engine listing tool

**Recommended enhanced tool**:
```python
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
        try:
            # POST is more private than GET (no query in URL)
            resp = await client.post(f"{SEARXNG_URL}/search", data=form_data)
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            if not results:
                return "No results found."
            
            formatted = []
            for i, r in enumerate(results[:max_results], 1):
                title = r.get("title", "No Title")
                url = r.get("url", "")
                snippet = r.get("content", "No snippet")
                engine = r.get("engine", "unknown")
                formatted.append(f"[{i}] {title}\n    URL: {url}\n    Engine: {engine}\n    {snippet}\n")
            
            return "\n".join(formatted)
        except httpx.HTTPStatusError as e:
            return f"SearXNG HTTP error: {e.response.status_code}"
        except httpx.RequestError as e:
            return f"SearXNG connection error: {e}"
```

---

## Sources Used

### Official Documentation
1. https://docs.searxng.org/admin/installation-granian.html — Granian WSGI server
2. https://docs.searxng.org/admin/settings/settings.html — settings.yml reference
3. https://docs.searxng.org/admin/settings/settings_server.html — server section
4. https://docs.searxng.org/admin/settings/settings_general.html — general section
5. https://docs.searxng.org/admin/settings/settings_outgoing.html — outgoing section
6. https://docs.searxng.org/admin/settings/settings_engines.html — engines section
7. https://docs.searxng.org/admin/installation-docker.html — Container installation
8. https://docs.searxng.org/admin/searx.limiter.html — Limiter documentation
9. https://docs.searxng.org/admin/architecture.html — Architecture overview
10. https://docs.searxng.org/dev/search_api.html — Search API reference
11. https://docs.searxng.org/src/searx.botdetection.html — Bot detection
12. https://docs.searxng.org/src/searx.settings.html — Settings loader

### GitHub Sources
13. https://github.com/searxng/searxng — Main repository (32K+ stars)
14. https://github.com/searxng/searxng-docker — Docker deployment templates
15. https://github.com/searxng/searxng/blob/master/searx/settings.yml — Default settings
16. https://github.com/searxng/searxng/blob/master/searx/search/__init__.py — Search pipeline
17. https://github.com/searxng/searxng/blob/master/searx/limiter.py — Limiter implementation
18. https://github.com/searxng/searxng/blob/master/searx/botdetection/ip_limit.py — IP rate limiting
19. https://github.com/searxng/searxng/blob/master/searx/botdetection/link_token.py — Link token
20. https://github.com/searxng/searxng/issues/4026 — Health check discussion
21. https://github.com/searxng/searxng/issues/4906 — Healthcheck port hardcoded
22. https://github.com/searxng/searxng/issues/3113 — secret_key required
23. https://github.com/searxng/searxng/issues/5718 — Docker variables not applied
24. https://github.com/searxng/searxng/issues/6044 — Root process vs searxng volume
25. https://github.com/searxng/searxng/pull/4366 — HEALTHCHECK added to Dockerfile
26. https://github.com/searxng/searxng/pull/4378 — Fix healthcheck to 127.0.0.1
27. https://github.com/searxng/searxng/pull/4820 — Granian migration
28. https://github.com/searxng/searxng/pull/4941 — HEALTHCHECK removed
29. https://github.com/searxng/searxng/discussions/5279 — Podman uidmap fix
30. https://github.com/searxng/searxng-docker/issues/30 — DAC_OVERRIDE rationale
31. https://github.com/searxng/searxng-docker/issues/442 — Rootless container
32. https://hub.docker.com/r/searxng/searxng/tags — Docker image tags

### DeepWiki Analysis
33. https://deepwiki.com/searxng/searxng/3-search-processing-pipeline — Pipeline architecture
34. https://deepwiki.com/searxng/searxng/3.2-search-orchestration — Parallel execution
35. https://deepwiki.com/searxng/searxng/11-bot-detection-and-rate-limiting — Bot detection

### MCP Server Implementations
36. https://github.com/pete-builds/mcp-searxng — FastMCP, 9 tools, deep search
37. https://github.com/88plug/searxng-mcp — Token-efficient, Docker-bundled
38. https://github.com/ihor-sokoliuk/mcp-searxng — Node.js, /config validation
39. https://github.com/voidog/searxng-mcp — TypeScript, SSRF protection
40. https://github.com/dandehoon/searxng-mcp — Single Docker image
41. https://github.com/zatevakhin/searxng-mcp — Rust, NixOS module
42. https://github.com/Jian-Zhan/searxng-mcp — Streamable HTTP transport
43. https://github.com/millerjes37/searxng-mcp — 7 tools, Rust

### Comparison & Ecosystem
44. https://selfhostwise.com/posts/self-hosted-search-engines-in-2026-searxng-vs-whoogle-complete-guide/ — SearXNG vs Whoogle
45. https://scavio.dev/compare/yacy/vs-searxng — SearXNG vs YaCy
46. https://cosmo-edge.com/searxng-sovereign-search-ai-guide/ — Sovereign search guide
47. https://sider.ai/blog/ai-tools/searxng-review-is-this-the-best-private-metasearch-you-can-actually-trust — SearXNG review
48. https://github.com/SecAI-Hub/llm-search-mediator — Privacy-preserving search bridge

### Quadlet & Podman
49. https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html — Podman Quadlet docs
50. https://gist.github.com/elvith-de/fecd13bb05209fb7abf5ae473483534b — SearXNG Quadlet example

### Omega Engine Sources
51. `mcp_servers/searxng/server.py` — Current MCP server (67 lines)
52. `src/omega/workers/background_researcher/searxng_client.py` — Background researcher client
53. `docs/research/omega-searxng.container` — Current Quadlet config (with bugs)
54. `docs/research/omega-searxng.service` — Service unit

---

*Research completed: 2026-06-21 | All 18 knowledge gaps filled | 54 primary sources consulted*
