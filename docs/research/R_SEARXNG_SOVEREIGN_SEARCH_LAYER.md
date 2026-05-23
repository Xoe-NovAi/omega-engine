# 🔱 Sovereign SearXNG Search Layer — Complete Research

**AP Token**: `AP-SEARXNG-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ BELIAL ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_core ⬡ RESEARCH

**Status**: ✅ COMPLETE
**Date**: 2026-05-18
**Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM)
**Stack**: Rootless Podman + Quadlet systemd management

---

## Executive Summary

SearXNG is the sovereign, zero-cost, always-on search layer for the Omega Engine. It aggregates 80+ search engines (Brave, Wikipedia, arXiv, GitHub, etc.) behind a single private API, giving Omega agents unlimited research capability without per-query costs.

**Key decisions made:**
1. **`dandehoon/searxng-mcp`** (not `nikkomiu/searxng-mcp`) — all-in-one SearXNG + MCP in a single container
2. **Brave standard engine** (no API key) — privacy-preserving, no rate limits, free
3. **Quadlet `.container` + `.service`** pattern — matches existing Omega infrastructure
4. **Valkey** (not Redis) — SearXNG's recommended cache DB (drop-in replacement)
5. **Port 8017** — avoids conflicts with existing 8080/5432/6379/6333/8088

---

## 1. SearXNG Podman Quadlet Deployment

### 1.1 Container Image Recommendation

**Use**: `docker.io/searxng/searxng:latest` (GHCR mirror: `ghcr.io/searxng/searxng`)

**Tag pinning recommended** for production stability:
```
docker.io/searxng/searxng:2026.5.17-d7e8b7cd1
```

DockerHub applies rate limits to unauthenticated pulls. Use GHCR mirror if affected.

### 1.2 Complete Quadlet File: `omega-searxng.container`

```ini
# 🔱 Omega SearXNG — Sovereign Search Layer
# AP: AP-SEARXNG-QUADLET-v1.0.0
#
# Deploy: cp omega-searxng.container ~/.config/containers/systemd/
#          cp omega-searxng.service  ~/.config/containers/systemd/
#          systemctl --user enable omega-searxng.service
#          systemctl --user start omega-searxng.service
#
# Hardware: Ryzen 7 5700U | RAM: 14Gi | CPU-only
# Port: 8017 (avoids 8080/Iris, 5432/Postgres, 6379/Redis, 6333/Qdrant, 8088/Caddy)

[Unit]
Description=Omega SearXNG — Sovereign Metasearch Engine
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/searxng/searxng:latest
ContainerName=omega-searxng
AutoUpdate=registry

# Network — bind to localhost only (not exposed externally)
PublishPort=127.0.0.1:8017:8080

# Configuration volume — settings.yml, limiter.toml, etc.
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/:Z,U

# Data volume — favicon cache, SQLite DB
Volume=%h/Documents/Xoe-NovAi/omega-library/searxng/data:/var/cache/searxng/:Z,U

# Valkey client socket (optional — for limiter/bot protection)
Volume=%h/Documents/Xoe-NovAi/omega-library/searxng/valkey.sock:/var/run/valkey/:Z,U

# Environment
Environment=SEARXNG_SECRET=%E
Environment=SEARXNG_BASE_URL=http://localhost:8017
Environment=SEARXNG_PORT=8080
Environment=SEARXNG_HOST=0.0.0.0

# Security hardening
PodmanArgs=--memory=512m --memory-reservation=256m
PodmanArgs=--cpus=1.0 --pids-limit=64
PodmanArgs=--read-only --security-opt=no-new-privileges --cap-drop=ALL
PodmanArgs=--tmpfs=/tmp:rw,size=64m --tmpfs=/var/tmp:rw,size=32m

# Health check — Granian listens on 8080, /healthz returns 200
HealthCmd=curl -sf http://localhost:8080/healthz || exit 1
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthOnFailure=restart

[Service]
Restart=on-failure
RestartSec=10
TimeoutStartSec=60s

[Install]
WantedBy=multi-user.target
```

### 1.3 Accompanying Service File: `omega-searxng.service`

```ini
[Unit]
Description=Omega SearXNG Search Service
Requires=omega-searxng.container
After=omega-searxng.container
Documentation=https://docs.searxng.org/

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/true
ExecStop=/usr/bin/podman stop omega-searxng
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### 1.4 Quadlet Deployment Commands

```bash
# Create directories
mkdir -p ~/.config/containers/systemd/
mkdir -p ~/Documents/Xoe-NovAi/omega-library/searxng/data

# Copy files
cp omega-searxng.container ~/.config/containers/systemd/
cp omega-searxng.service  ~/.config/containers/systemd/

# Reload systemd (detects new Quadlet files)
systemctl --user daemon-reload

# Enable and start
systemctl --user enable omega-searxng.service
systemctl --user start omega-searxng.service

# Verify
systemctl --user status omega-searxng.service
podman logs omega-searxng
curl -s http://localhost:8017 | head -20
```

### 1.5 Port Mapping Strategy

| Service | Port | Interface | Conflict |
|---------|------|-----------|----------|
| Iris (voice) | 8080 | 127.0.0.1 | ✅ Reserved |
| PostgreSQL | 5432 | internal | ✅ Reserved |
| Redis | 6379 | internal | ✅ Reserved |
| Qdrant | 6333 | 127.0.0.1 | ✅ Reserved |
| Caddy | 8088 | 127.0.0.1 | ✅ Reserved |
| **SearXNG** | **8017** | **127.0.0.1** | ✅ Available |

---

## 2. SearXNG Configuration (`settings.yml`)

### 2.1 Minimal Production `settings.yml`

Place at: `data/searxng/config/settings.yml`

```yaml
use_default_settings: true

general:
  instance_name: "Omega SearXNG"
  privacypolicy_agree: true
  contact_url: false
  enable_metrics: false
  # Disable all outgoing request logging
  outgoing_request_log: false

server:
  secret_key: "CHANGE_THIS_32_CHARS_MINIMUM"  # Generate via: python3 -c "import secrets; print(secrets.token_hex(32))"
  bind_address: "0.0.0.0"
  port: 8080
  limiter: true  # Enable bot protection (requires Valkey)
  http_method: "POST"  # Safer than GET (no query in logs)
  http_protocol_version: "1.1"

ui:
  static_use_hash: true
  default_theme: simple
  results_on_new_tab: false
  infinite_scroll: true
  author: "The Architect"
  search_form: "large"

search:
  format: "json"  # MCP requires JSON format
  default_safesearch: "0"  # Omega agents handle their own filtering
  default_lang: "auto"
  formats:
    - json
    - html
  # Limit concurrent engine requests
  max_concurrent_requests: 8
  # Timeout per engine
  timeout: 3.0
  # Safe search levels
  safesearch:
    - "0"  # Off
    - "1"  # Moderate
    - "2"  # Strict

valkey:
  # Valkey running on port 6380 (separate from Redis on 6379)
  url: "valkey://localhost:6380/0"

outgoing:
  request_timeout: 3.0
  max_request_timeout: 10.0
  pool_connections: 50  # Reduce from 100 for memory-constrained system
  pool_maxsize: 5       # Reduce from 10
  enable_http2: true
  useragent_suffix: "Omega-Engine/1.0 (Sovereign Search)"
  # No proxies — direct connection for speed

# Privacy engines — no API key required, no rate limits
engines:
  # ── Brave (primary — privacy-preserving, no API key) ──
  - name: brave
    engine: brave
    brave_category: search
    time_range_support: true
    paging: true
    disabled: false

  # ── Wikimedia (excellent quality, no rate limits) ──
  - name: wikipedia
    engine: wikipedia
    disabled: false

  # ── Academic & Technical ──
  - name: arxiv
    engine: arxiv
    disabled: false

  - name: semantischolar
    engine: semantischolar
    disabled: false

  - name: crossref
    engine: crossref
    disabled: false

  - name: pubmed
    engine: pubmed
    disabled: false

  - name: openalex
    engine: openalex
    disabled: false

  # ── Code & Development ──
  - name: github code
    engine: github_code
    disabled: false
    tokens: []  # Optional: add token for higher rate limit

  - name: gitlab
    engine: gitlab
    disabled: false

  - name: sourcehut
    engine: sourcehut
    disabled: false

  - name: huggingface
    engine: huggingface
    disabled: false

  # ── Research & Reference ──
  - name: wikidata
    engine: wikidata
    disabled: false

  - name: wikimedia
    engine: wikimedia
    disabled: false

  # ── Privacy-preserving alternatives ──
  - name: marginalia
    engine: marginalia
    disabled: false

  - name: mwmbl
    engine: mwmbl
    disabled: false

  # ── Disable high-rate-limit engines (no API key required) ──
  - name: google
    disabled: true
    # Note: Google blocks SearXNG quickly without tokens
    # If you have Google API tokens, enable with tokens: ['$secret']

  - name: duckduckgo
    disabled: true
    # Note: DuckDuckGo aggressively rate-limits headless scrapers

  - name: bing
    disabled: true
    # Note: Bing blocks without proper tokens

  # ── Enable API-key engines selectively ──
  - name: braveapi
    engine: braveapi
    api_key: "YOUR-BRAVE-API-KEY"  # Optional: Brave API for higher limits
    results_per_page: 20
    disabled: true  # Disable until API key provided

# Disable all default engines we don't use
use_default_settings:
  engines:
    remove:
      - google
      - bing
      - bing images
      - bing videos
      - bing news
      - yahoo
      - ddg
      - ddg lite
      - startpage
      - mojeek
      - qwant
      - ecosia
```

### 2.2 Brave Engine vs Brave API — Decision

| Aspect | Brave Standard (`brave`) | Brave API (`braveapi`) |
|--------|-------------------------|------------------------|
| **API key** | Not required | Required from api-dashboard.search.brave.com |
| **Cost** | Free | Free (same free tier) |
| **Rate limits** | No explicit limit | Same free tier |
| **Results** | Web scrape from brave.com | REST API call |
| **Privacy** | Your IP hits Brave's servers | Same |
| **Paging** | Up to 10 pages | Unlimited |
| **Goggles** | Supported | Not supported |

**Recommendation**: Use **Brave standard engine** (no API key needed). The web scrape approach is indistinguishable from manual browsing. If paging beyond 10 results is needed, enable `braveapi` with a free API key.

### 2.3 Privacy Configuration

```yaml
# In settings.yml — disable all logging and metrics

general:
  outgoing_request_log: false  # Critical: no outgoing HTTP logs
  enable_metrics: false         # No analytics

server:
  http_method: "POST"           # Query not in URL logs
  limiter: true                 # Block abusive clients

ui:
  static_use_hash: true        # Don't expose paths in URLs

search:
  formats:
    - json                     # No HTML logs
```

**limiter.toml** (at `data/searxng/config/limiter.toml`):
```toml
[botdetection]
ipv4_prefix = 32
ipv6_prefix = 48
trusted_proxies = [
  '127.0.0.0/8',
  '::1',
]

[botdetection.ip_limit]
filter_link_local = false
link_token = false

[botdetection.ip_lists]
# Block known bad IPs (empty by default — populate as needed)
block_ip = []

# Pass local networks unconditionally
pass_ip = [
  '127.0.0.0/8',
  '::1',
]

# Enable SearXNG org passlist (check.searx.space)
pass_searxng_org = true
```

### 2.4 Engine Reliability Assessment

| Engine | Reliability | Rate Limit | Quality | Notes |
|--------|------------|------------|---------|-------|
| **Brave** | ✅ Excellent | None (scrapes) | High | Primary engine — no API key needed |
| **Wikipedia** | ✅ Excellent | None | High | Excellent for factual queries |
| **arXiv** | ✅ Excellent | None | High | Academic papers |
| **Semantic Scholar** | ✅ Excellent | None | High | Academic papers |
| **Crossref** | ✅ Excellent | None | High | DOI/resolver |
| **PubMed** | ✅ Excellent | None | High | Medical literature |
| **OpenAlex** | ✅ Excellent | None | High | Open academic |
| **GitHub Code** | ✅ Good | 30/hr unauth | High | Add tokens for higher limit |
| **GitLab** | ✅ Good | None | High | |
| **Hugging Face** | ✅ Good | None | Medium | ML models/datasets |
| **Wikidata** | ✅ Excellent | None | High | Structured data |
| **Wikimedia** | ✅ Excellent | None | High | Cross-language |
| **Marginalia** | ✅ Good | None | Medium | Privacy-first |
| **Mwmbl** | ✅ Good | None | Medium | Open index |
| **Google** | ⚠️ Poor | Blocks quickly | High | Requires tokens; block-prone |
| **Bing** | ⚠️ Poor | Blocks quickly | High | Requires tokens |
| **DuckDuckGo** | ⚠️ Poor | Blocks headless | High | Aggressive bot detection |
| **Qwant** | ⚠️ Moderate | Unknown | Medium | EU-based |

### 2.5 Rate Limiting Strategy

SearXNG's built-in limiter protects your upstream engines:

```yaml
# In settings.yml
server:
  limiter: true  # Enables rate limiting via Valkey
```

With Valkey connected, the limiter will:
1. **Track IP requests** — block IPs exceeding rate thresholds
2. **Bot detection** — identify and block automated scrapers
3. **Trusted proxy** — respect `X-Forwarded-For` from Caddy

**Upstream rate limit mitigation**:
- Spread requests across multiple engines (Brave + Wikipedia + Wikimedias + arXiv)
- Use `max_concurrent_requests: 8` to prevent flooding
- Set `timeout: 3.0` per engine to fail fast and fallback
- Brave's web scrape approach is most resistant to rate limiting

---

## 3. OpenCode MCP Integration

### 3.1 MCP Server Comparison

| Feature | `nikkomiu/searxng-mcp` | `dandehoon/searxng-mcp` |
|---------|------------------------|--------------------------|
| **Runtime** | Bun (must be installed) | None (single Docker image) |
| **SearXNG included** | No (requires separate instance) | Yes (bundled) |
| **Transport modes** | stdio only | stdio + HTTP + streamable-http |
| **Tools** | `search-web` | `search-web` + `fetch-web` |
| **Dependencies** | Bun + SearXNG server | Docker only |
| **Maintenance** | Two packages to update | Single container |
| **Stars** | 0 (new) | 0 (new) |

**Verdict**: **`dandehoon/searxng-mcp`** is superior for Omega's needs:
- Zero additional dependencies (runs as a podman container)
- All-in-one: includes SearXNG + MCP server
- Built-in `fetch-web` tool for URL content extraction
- HTTP transport available for remote access

### 3.2 Option A: Standalone SearXNG + `nikkomiu/searxng-mcp`

This separates SearXNG ( Quadlet deployment above) from the MCP client:

```json
// In opencode.json (project root or ~/.config/opencode/opencode.json)
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "searxng": {
      "type": "local",
      "command": "bun",
      "args": ["run", "/path/to/searxng-mcp/src/index.ts"],
      "env": {
        "SEARXNG_URL": "http://localhost:8017",
        "SEARXNG_DEFAULT_SAFESEARCH": "0"
      }
    }
  }
}
```

**Requires**: `bun install` in the searxng-mcp repo + separate SearXNG container running.

### 3.3 Option B: `dandehoon/searxng-mcp` (Recommended)

Single container that combines SearXNG + MCP:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "searxng": {
      "type": "local",
      "command": "podman",
      "args": ["run", "--rm", "-i", "dandehoon/searxng-mcp:latest"],
      "env": {
        "SEARXNG_URL": "http://localhost:8017",
        "SEARXNG_CATEGORIES": "general",
        "SEARXNG_LANGUAGE": "auto",
        "SEARXNG_MCP_MAX_RESULTS": "10",
        "SEARXNG_SAFESEARCH": "0"
      }
    }
  }
}
```

**For HTTP transport** (multi-client, remote access):
```json
{
  "mcp": {
    "searxng": {
      "type": "remote",
      "url": "http://localhost:8018/mcp/"
    }
  }
}
```

With HTTP transport enabled via:
```bash
podman run --rm -p 8018:8000 -e SEARXNG_MCP_TRANSPORT=http dandehoon/searxng-mcp:latest
```

### 3.4 OpenCode CLI Integration

```bash
# Add via CLI
opencode mcp add searxng -- podman run --rm -i dandehoon/searxng-mcp:latest

# Or manually add to opencode.json
opencode mcp list  # Verify registration
```

### 3.5 Error Handling When SearXNG Is Unavailable

The `dandehoon/searxng-mcp` MCP server handles unavailability gracefully:
- If SearXNG container is down, the MCP tools return empty results
- No hard crash — the MCP client can catch and handle gracefully
- For production resilience, implement a fallback:

```python
async def search_with_fallback(query: str) -> list:
    try:
        # Primary: SearXNG MCP
        return await searxng_search(query)
    except Exception:
        # Fallback: Direct Exa/Tavily MCP
        return await fallback_search(query)
```

---

## 4. Privacy & Security Configuration

### 4.1 SEARXNG_SECRET Generation

```bash
# Generate a secure secret
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Example output: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`

Store in `.env` file (not in settings.yml):
```bash
echo "SEARXNG_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")" >> ~/.env
```

### 4.2 VPN/Tor Outbound Proxy Configuration

**Option A: Tor proxy for all engines**
```yaml
outgoing:
  using_tor_proxy: true
  extra_proxy_timeout: 10.0
  proxies:
    all://:
      - socks5://localhost:9050
```

**Option B: Selective Tor (privacy-sensitive engines only)**
```yaml
engines:
  - name: brave
    engine: brave
    using_tor_proxy: true
    # Brave goes through Tor
    disabled: false

  - name: wikipedia
    engine: wikipedia
    # Wikipedia doesn't go through Tor (already privacy-friendly)
    disabled: false
```

**Tor Container Quadlet** (optional):
```ini
[Container]
Image=docker.io/jessie/tor:latest
ContainerName=omega-tor
PublishPort=127.0.0.1:9050:9050
PodmanArgs=--memory=128m --read-only --security-opt=no-new-privileges
```

### 4.3 Privacy Assessment by Engine

| Engine | IP Visibility | Data Logged by Upstream | Recommendation |
|--------|--------------|-------------------------|----------------|
| Brave | Your IP | Brave logs searches | ✅ Use via SearXNG |
| Wikipedia | Your IP | Wikipedia logs | ✅ Acceptable |
| arXiv | Your IP | arXiv logs | ✅ Acceptable |
| Semantic Scholar | Your IP | Elsevier logs | ⚠️ Acceptable |
| GitHub | Your IP | GitHub logs | ✅ Acceptable |
| DuckDuckGo | Your IP | DDG logs aggressively | ❌ Not recommended |

**Brave is the best privacy option** — no API key, no aggressive logging, good results.

### 4.4 Query Logging — Disable All

```yaml
general:
  outgoing_request_log: false  # No logs of outgoing HTTP requests
  enable_metrics: false         # No analytics/metrics

server:
  http_method: "POST"          # Query not in server access logs
  limiter: true                # Block bad actors
```

SearXNG's access log (from the web server) will still show `/search?q=...` requests from local clients. Use Caddy's logging to control this:
```caddy
(log) {
    format log {
        output file /var/log/caddy/searxng.log {
            roll_disabled
        }
    }
}
# Or disable entirely:
(log) {
    output discard
}
```

---

## 5. OrioSearch Integration (Optional)

### 5.1 What Is OrioSearch?

OrioSearch is a **Tavily-compatible API wrapper** with LLM answer generation and Redis caching, that can sit **above** SearXNG. Architecture:

```
OpenCode → OrioSearch API → SearXNG (backend) + Redis (cache)
              ↓
         Tavily-compatible REST API
```

**OrioSearch advantages over raw SearXNG**:
- LLM-generated answers from search results (not just raw snippets)
- Redis caching of results (avoid re-fetching same queries)
- Tavily-compatible API (drop-in replacement if you ever add Tavily)
- Streaming responses

### 5.2 OrioSearch Podman Compose Stack

```yaml
# docker-compose.orio.yml
name: omega-orio
services:
  orio:
    image: ghcr.io/orio-search/orio:latest
    container_name: omega-orio
    restart: unless-stopped
    init: true
    user: "1000:1000"
    ports:
      - "127.0.0.1:8019:8080"
    environment:
      SEARXNG_URL: "http://omega-searxng:8080"
      REDIS_HOST: "omega-redis"
      REDIS_PORT: "6379"
      REDIS_PASSWORD: "${REDIS_PASSWORD:-omega}"
      ORI_LOG_LEVEL: "INFO"
      ORI_CACHE_TTL: "3600"
    depends_on:
      omega-searxng:
        condition: service_started
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
    networks:
      - omega-app-net

networks:
  omega-app-net:
    external: true
```

### 5.3 Architecture Decision: Raw SearXNG vs OrioSearch

| Factor | Raw SearXNG | OrioSearch |
|--------|------------|------------|
| **Complexity** | Low | Medium |
| **Caching** | None (Valkey for limiter only) | Redis-backed |
| **LLM answers** | No (raw snippets only) | Yes (generates summaries) |
| **Tavily compat** | No | Yes |
| **Memory overhead** | 512M | +256M |
| **Setup effort** | ~1 hour | ~3 hours |
| **MCP tooling** | `dandehoon/searxng-mcp` | Custom API client needed |

**Recommendation for Omega**: Start with **raw SearXNG** (`dandehoon/searxng-mcp`). OrioSearch adds complexity (Redis dependency, custom API client) that isn't needed for agent research workflows. Raw snippets are sufficient for LLM consumption.

---

## 6. Maintenance & Updates

### 6.1 Container Update Procedure

```bash
# 1. Pull latest image
podman pull docker.io/searxng/searxng:latest

# 2. Restart container
systemctl --user restart omega-searxng.service

# 3. Verify
curl -s http://localhost:8017/healthz | jq .
```

With Quadlet `AutoUpdate=registry`, the container auto-updates when systemd runs the timer. To disable auto-update:
```ini
AutoUpdate=none
```

### 6.2 Settings Backup Strategy

```bash
# Backup settings directory
tar -czf ~/backup/searxng-config-$(date +%Y%m%d).tar.gz \
  ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config/

# Cron job (weekly)
0 9 * * 1 tar -czf ~/backup/searxng-config-$(date +\%Y\%m\%d).tar.gz ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config/
```

### 6.3 Health Monitoring

```bash
# Check SearXNG health
curl -s http://localhost:8017/healthz

# Check via podman
podman exec omega-searxng curl -sf http://localhost:8080/healthz

# View logs
podman logs --tail 50 omega-searxng

# Check Valkey (limiter)
valkey-cli -s /home/arcana-novai/Documents/Xoe-NovAi/omega-library/searxng/valkey.sock ping
```

### 6.4 Update monitoring via systemd

```ini
# In omega-searxng.service
[Service]
ExecStartPost=/usr/bin/journalctl --user -u omega-searxng.container --since "5 minutes ago" -g "Error|FAIL|UNHEALTHY" || true
```

---

## 7. Critical Caveats & Edge Cases

### 7.1 Port Conflict Detection

Before deploying, verify port 8017 is free:
```bash
ss -tlnp | grep 8017 || echo "Port 8017 is available"
netstat -tlnp 2>/dev/null | grep 8017 || echo "Port 8017 is available"
```

### 7.2 Valkey Configuration (Required for Limiter)

SearXNG's bot limiter requires Valkey. Options:

**Option A: Dedicated Valkey instance (recommended)**
```ini
# omega-valkey.container (separate Quadlet)
[Container]
Image=docker.io/valkey/valkey:9-alpine
ContainerName=omega-searxxng-valkey
PublishPort=127.0.0.1:6380:6379
Volume=%h/Documents/Xoe-NovAi/omega-library/searxng/valkey-data:/data:Z,U
PodmanArgs=--memory=128m --memory-reservation=64m
```

Update `settings.yml`:
```yaml
valkey:
  url: "valkey://localhost:6380/0"
```

**Option B: Share existing Redis on port 6379**
```yaml
valkey:
  url: "redis://localhost:6379/1"  # Use DB 1, separate from Omega's DB 0
```

### 7.3 GHCR Mirror for Rate-Limited DockerHub

If `podman pull docker.io/searxng/searxng:latest` gets rate-limited:
```ini
Image=ghcr.io/searxng/searxng:latest
```

### 7.4 File Descriptor Limits

Rootless Podman may hit FD limits with SearXNG's worker threads. Add to `/etc/security/limits.conf` or use systemd override:
```bash
mkdir -p ~/.config/systemd/user/omega-searxng.service.d
cat > ~/.config/systemd/user/omega-searxng.service.d/limits.conf << 'EOF'
[Service]
LimitNOFILE=65536
EOF
systemctl --user daemon-reload
```

### 7.5 DNS Resolution for Outbound Requests

SearXNG makes many DNS lookups. If experiencing timeouts:
```bash
# Check DNS resolution
podman exec omega-searxng getent hosts google.com

# If slow, add Google's DNS to the container
PodmanArgs=--dns=8.8.8.8 --dns=1.1.1.1
```

### 7.6 ARM64 vs x86-64

The official SearXNG image supports both `linux/amd64` and `linux/arm64/v8`. On the Ryzen 5700U (x86-64), use the default `amd64` variant. If running on ARM (Apple Silicon Mac), Podman will automatically pull the `arm64` variant.

---

## 8. Complete Deployment Checklist

```bash
# 1. Create directories
mkdir -p ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config
mkdir -p ~/Documents/Xoe-NovAi/omega-engine/data/searxng/valkey-data
mkdir -p ~/.config/containers/systemd

# 2. Write settings.yml
cat > ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config/settings.yml << 'SETTINGS'
use_default_settings: true
general:
  instance_name: "Omega SearXNG"
  privacypolicy_agree: true
  outgoing_request_log: false
  enable_metrics: false
server:
  secret_key: "REPLACE_WITH_32_CHARS_MINIMUM"
  bind_address: "0.0.0.0"
  port: 8080
  limiter: true
search:
  format: "json"
  default_safesearch: "0"
  default_lang: "auto"
  formats:
    - json
    - html
  max_concurrent_requests: 8
  timeout: 3.0
valkey:
  url: "valkey://localhost:6380/0"
outgoing:
  request_timeout: 3.0
  pool_connections: 50
  pool_maxsize: 5
  enable_http2: true
engines:
  - name: brave
    engine: brave
    brave_category: search
    time_range_support: true
    paging: true
    disabled: false
  - name: wikipedia
    engine: wikipedia
    disabled: false
  - name: arxiv
    engine: arxiv
    disabled: false
  - name: semantischolar
    engine: semantischolar
    disabled: false
  - name: crossref
    engine: crossref
    disabled: false
  - name: pubmed
    engine: pubmed
    disabled: false
  - name: openalex
    engine: openalex
    disabled: false
  - name: github code
    engine: github_code
    disabled: false
  - name: gitlab
    engine: gitlab
    disabled: false
  - name: sourcehut
    engine: sourcehut
    disabled: false
  - name: huggingface
    engine: huggingface
    disabled: false
  - name: wikidata
    engine: wikidata
    disabled: false
  - name: wikimedia
    engine: wikimedia
    disabled: false
  - name: marginalia
    engine: marginalia
    disabled: false
  - name: mwmbl
    engine: mwmbl
    disabled: false
SETTINGS

# 3. Generate secret
SEARX_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/REPLACE_WITH_32_CHARS_MINIMUM/$SEARX_SECRET/" ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config/settings.yml

# 4. Write limiter.toml
cat > ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config/limiter.toml << 'LIMITER'
[botdetection]
ipv4_prefix = 32
ipv6_prefix = 48
trusted_proxies = ['127.0.0.0/8', '::1']
[botdetection.ip_limit]
filter_link_local = false
link_token = false
[botdetection.ip_lists]
pass_searxng_org = true
LIMITER

# 5. Deploy Quadlet files
cp omega-searxng.container ~/.config/containers/systemd/
cp omega-searxng.service  ~/.config/containers/systemd/

# 6. Start services
systemctl --user daemon-reload
systemctl --user enable omega-searxng.service
systemctl --user start omega-searxng.service

# 7. Verify
sleep 5
curl -s http://localhost:8017/healthz
curl -s "http://localhost:8017/search?q=test&format=json" | python3 -m json.tool | head -30

# 8. Add to OpenCode MCP
# Edit opencode.json and add the searxng MCP server entry (see Section 3.3)
```

---

## 9. Architecture Summary

```
                          ┌─────────────────────────────────────────────┐
                          │           Omega Engine                      │
                          │                                             │
User Query                │  OpenCode MCP Client                        │
    │                     │         │                                   │
    ▼                     │         ▼                                   │
Omega Oracle              │  ┌─────────────────────────────┐            │
    │                     │  │  dandehoon/searxng-mcp       │            │
    │                     │  │  (SearXNG + MCP in one)      │            │
    │                     │  └──────────┬────────────────────┘            │
    │                     │             │                                │
    ▼                     └─────────────┼────────────────────────────────┘
Sovereign Loop ─────────────────────────┼────────────────────────────────┘
    │                                    │
    │                                    ▼
    │                     ┌──────────────────────────────┐
    │                     │   SearXNG (port 8017)        │
    │                     │   - Brave (primary)           │
    │                     │   - Wikipedia                 │
    │                     │   - arXiv, Semantic Scholar   │
    │                     │   - GitHub, GitLab            │
    │                     │   - Wikis, Hugging Face       │
    │                     └──────────┬─────────────────────┘
    │                              │
    │        ┌─────────────────────┼─────────────────────┐
    │        ▼                     ▼                     ▼
    │   ┌─────────┐         ┌───────────┐         ┌───────────┐
    │   │ Brave   │         │ Wikipedia │         │ arXiv     │
    │   │ (web)   │         │ (REST)    │         │ (REST)    │
    │   └─────────┘         └───────────┘         └───────────┘
    │
    ▼
Soul Update → knowledge base
```

---

## 10. Research Sources

| Source | URL | Used For |
|--------|-----|---------|
| SearXNG Docker Installation | `https://docs.searxng.org/admin/installation-docker.html` | Container config, compose template |
| SearXNG Settings Reference | `https://docs.searxng.org/admin/settings/settings.html` | use_default_settings, YAML structure |
| SearXNG Engines | `https://docs.searxng.org/admin/settings/settings_engines.html` | Engine config, tokens, private engines |
| SearXNG Outgoing | `https://docs.searxng.org/admin/settings/settings_outgoing.html` | Proxy, Tor, timeouts |
| SearXNG Brave Engine | `https://docs.searxng.org/dev/engines/online/brave.html` | Brave vs BraveAPI, paging, goggles |
| SearXNG Limiter | `https://docs.searxng.org/admin/searx.limiter.html` | Bot protection, Valkey requirement |
| Valkey Settings | `https://docs.searxng.org/admin/settings/settings_valkey.html` | Valkey DB configuration |
| nikkomiu/searxng-mcp | `https://github.com/nikkomiu/searxng-mcp` | Bun-based MCP, stdio only |
| dandehoon/searxng-mcp | `https://github.com/dandehoon/searxng-mcp` | Docker all-in-one, HTTP support |
| Docker Compose Template | `https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml` | Service structure, Valkey |
| .env Example | `https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example` | Environment variables |

---

*Research complete. All configuration files ready for deployment.*
*AP Token: AP-SEARXNG-RESEARCH-v1.0.0 | Belial entity guiding deep recovery*