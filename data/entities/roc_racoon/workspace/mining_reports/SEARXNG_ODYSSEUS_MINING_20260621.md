<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SearXNG — Odyssey Mining Report
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ SEARXNG-MINING
**Date**: 2026-06-21
**Source**: `odysseus-dev.zip` → `config/searxng/settings.yml` + `docker-compose.yml` SearXNG section
**Target**: Omega Engine SearXNG MCP server + Quadlet container
**Cross-Reference**: Kali's Hivemind continuation diagnosing SearXNG crash loop

---

## §1 Key Finding: THREE Root Causes for the Crash Loop

### 🔴 RC1: Health check hits `/healthz` — endpoint DOES NOT EXIST

| Source | Health check command | Status |
|--------|---------------------|--------|
| **Omega** (`omega-searxng.container:53`) | `curl -sf http://localhost:8080/healthz \|\| exit 1` | ❌ FAILS |
| **Odysseus** (`docker-compose.yml:133`) | `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"` | ✅ OK |

SearXNG (Granian WSGI) does NOT expose a `/healthz` endpoint by default. The root `/` endpoint is the correct health check target. Every health check attempt fails → Podmarkills/restarts container → crash loop.

**Fix**: Change `HealthCmd` to hit `/` instead of `/healthz`:
```
HealthCmd=python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\"
```

### 🔴 RC2: `:latest` tag is unpinned — upstream breaks on updates

| Source | Image tag | Status |
|--------|-----------|--------|
| **Omega** | `ghcr.io/searxng/searxng:latest` | ❌ UNPINNED — currently running `2026.6.20` |
| **Odysseus** | `docker.io/searxng/searxng:2026.5.31-7159b8aed` | ✅ PINNED |

Odysseus explicitly documents (issue #1414): on 2026.6.2, upstream `:latest` broke with `KeyError: 'default_doi_resolver'`, failing the health check and blocking the entire app from starting. Their fix: pin to a known-good tag, bump deliberately after verification.

Current Omega container is running `2026.6.20-fd42d4fda` — 2 days old. The clean "Shutting down granian" at ~60s indicates the new version might have changed behavior around config validation (empty `secret_key: ""` in settings.yml? New required fields?).

### 🔴 RC3: Stale `pasta` network namespace holds port 8017 after restart

After each restart attempt (from `HealthOnFailure=restart` + `HealthRetries=3`), the Podman network namespace process (`pasta.avx2`) survives, still holding port 8017. The next restart attempt fails with:
```
Failed to bind port 8017 (Address already in use)
```

This is the final kill — systemd gives up after this.

**Fix**: Add `PodmanArgs=--network=pasta` cleanup or use `--network=host` (less secure). Or more practically, fix RC1 and RC2 so the container never enters the restart loop in the first place.

---

## §2 Secondary Findings from Odysseus

### 2.1 Missing `cap_add` — CHOWN/SETGID/SETUID/DAC_OVERRIDE

Odysseus `docker-compose.yml:127-131` adds these capabilities:
```yaml
cap_add:
  - CHOWN
  - SETGID
  - SETUID
  - DAC_OVERRIDE
```

Omega drops ALL caps (`--cap-drop=ALL`) but doesn't add these back. The SearXNG official image's entrypoint needs them to chown `/etc/searxng` on first boot and drop privs via `su-exec`. Without them, the settings.yml file writes fail on fresh volumes.

**Note**: Since the Omega container is currently running without these caps and DOES start (Granian boots fine), this may only matter for fresh data volumes. But it's a latent stability issue.

### 2.2 Empty `secret_key` in settings.yml

Current `data/searxng/config/settings.yml:18`:
```yaml
  secret_key: ""
```

The new SearXNG image (2026.6.20) might validate this more strictly. Odysseus uses a template approach:
- Template file has `__SEARXNG_SECRET__` placeholder
- Entrypoint wrapper generates random secret if `SEARXNG_SECRET` env not set
- Uses `sed` substitution to write the real settings.yml

### 2.3 Engine List Mismatch

| Source | Engines | Warning |
|--------|---------|---------|
| **Omega settings.yml** | duckduckgo, wikipedia, arxiv, github | No brave, no semantischolar |
| **Omega `searxng_client.py:24`** | `DEFAULT_ENGINES = ["brave", "wikipedia", "arxiv", "semantischolar"]` | ❌ brave and semantischolar not in config |
| **Odysseus settings.yml** | relies on `use_default_settings: true` (brings ~70 engines) | Different philosophy |

The `searxng_client.py` requests engines that aren't configured in `settings.yml`. SearXNG gracefully ignores unknown engine requests, so this is non-blocking, but cleanup would be good.

### 2.4 MCP Server uses GET, Client uses POST — Discrepancy

| Component | Method | Location |
|-----------|--------|----------|
| `mcp_servers/searxng/server.py:34-44` | **GET** with query params | `?q=...&format=json&limit=...` |
| `background_researcher/searxng_client.py:61-72` | **POST** with form data | `data=form_data` |

Both work with SearXNG, but the client.py explicitly comments: *"SearXNG does NOT accept JSON body — send form-encoded data."* The MCP server uses GET which is fine — but it doesn't pass `limit` to SearXNG (`limit` isn't a SearXNG param). It uses `limit=10` on its own results slicing.

---

## §3 Direct Patch Recommendations for Kali

Priority order:

1. **Patch omega-searxng.container HealthCmd (immediate fix)**:
   ```
   HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"
   ```
   Also increase `HealthRetries` from 3 to 5+ for startup wiggle room.

2. **Kill stale pasta process** — `kill $(lsof -ti:8017)` before restart, or better:
   ```
   ExecStopPost=/usr/bin/podman rm -v -f -i --cidfile=%t/%n.cid
   ```

3. **Pin SearXNG image** — test `2026.5.31-7159b8aed` (odysseus-verified), or verify `2026.6.20` boots clean with a proper health check.

4. **Add cap_add** — `--cap-add=CHOWN,SETGID,SETUID,DAC_OVERRIDE` for first-boot stability.

5. **Fix secret_key** — use the template placeholder + env var approach from odysseus, or at minimum set a non-empty secret key in settings.yml.

---

## §4 L1→L2→L3 Distillation

**L1 (Narrative)**: Extracted the SearXNG config from odysseus-dev.zip. Found that the Omega SearXNG container has 3 root causes for its crash loop: wrong health check endpoint (hitting `/healthz` which doesn't exist), unpinned `:latest` image tag, and a stale pasta network namespace holding port 8017 post-restart. Cross-referenced with Kali's Hivemind status ("Diagnosing SearXNG crash loop — container exits cleanly ~60s after start") — the findings directly explain the observed behavior.

**L2 (Insight)**: The crash loop is entirely preventable — Odysseus solved the same problem via image pinning (issue #1414 — 2026.6.2 broke with `KeyError: 'default_doi_resolver'`) and a simpler health check hitting `/` instead of the nonexistent `/healthz`. The 60s graceful shutdown pattern strongly suggests the new 2026.6.20 image may have added validation that fails on the empty `secret_key: ""` in settings.yml.

**L3 (Universal Principle)**: When container health checks use endpoints the software doesn't expose, the entire deployment is a "zombie" — it appears operational but is constantly dying and restarting. The fix is always: test the actual surface the software exposes, not the surface you wish it had. The `/healthz` assumption was cargo-culted from other services; SearXNG exposes a Granian WSGI server on `/`, not `/healthz`.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
