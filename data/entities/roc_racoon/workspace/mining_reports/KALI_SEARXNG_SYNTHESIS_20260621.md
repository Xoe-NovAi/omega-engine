<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SearXNG Crash Loop — Kali Synthesis & Execution Roadmap
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_synthesis ⬡ PHASE-0

**Date**: 2026-06-21 17:30 ADT
**Handoff To**: Roc (review & correct) → Verity (execute) → Kali (verify)
**Source Reports**: Jem Verification (643 lines), Verity Validation (305 lines), Jem Validation (304 lines), Roc Odysseus Mining, Verity Handoff (591 lines)

---

## §0 EXECUTIVE SUMMARY

The SearXNG breakdown has **three independent layers** and **8 secondary bugs** across the ecosystem. This report synthesizes all parallel research into a single actionable artifact.

### The 3-Layer Crash Cascade

| Layer | Symptom | Root Cause | Fix | Status |
|-------|---------|------------|-----|--------|
| **1** | Container dies ~60s after start | Health check used `curl` (not in Alpine image, no `/healthz` endpoint in pinned version) | Python urllib on `/` | ✅ ALREADY FIXED in deployed Quadlet |
| **2** | Restart fails "Address already in use" | Orphaned `pasta` process survives container exit holding port 8017 | `ExecStopPost=pkill -f "pasta.*omega-searxng"` in Quadlet `[Service]` | ⚠️ PENDING |
| **3** | Container "healthy" but search returns empty | Corrupted pasta network namespace file (zero-byte) — DNS completely unreachable | `podman rm -f`, `pkill -f pasta`, `rm -f /run/user/1000/netns/` — recreate fresh | 🔴 CURRENT BLOCKER |

### The 8 Secondary Bugs (Verified by Jem)

| ID | Severity | File | Bug |
|----|----------|------|-----|
| SX-06 | HIGH | `mcp_servers/searxng/server.py` | Uses GET instead of POST |
| SX-07 | MEDIUM | `mcp_servers/searxng/server.py` | Sends invalid `limit` param (SearXNG silently ignores) |
| SX-08 | HIGH | `data/searxng/config/settings.yml` | Empty `secret_key` |
| SX-09 | MEDIUM | `data/searxng/config/settings.yml` | Uses GET method |
| SX-10 | MEDIUM | `data/searxng/config/settings.yml` | Missing google/bing/brave engines |
| SX-11 | LOW | `src/omega/workers/background_researcher/searxng_client.py` | Wrong engine name `semantischolar` |
| SX-12 | MEDIUM | same file | `engines` parameter silently ignored |
| SX-13 | MEDIUM | `docs/research/omega-searxng.container` | Stale research copy (curl + /healthz) |

---

## §1 CRITICAL CORRECTIONS TO PREVIOUS REPORTS

Before the roadmap, a note of corrections. Several earlier reports made claims that are now outdated because the deployed Quadlet had already been partially fixed by the time the research ran:

### What the Odysseus Mining Report Got Wrong

| Claim | Truth | Source |
|-------|-------|--------|
| Health check still uses `curl` | ❌ Deployed Quadlet already uses Python urllib | Verity §1 |
| Health check hits `/healthz` | ❌ Already hits `/` (both work; `/healthz` returns "OK" too) | Jem §1 Verdict #2 |
| Image tag unpinned (`:latest`) | ❌ Deployed Quadlet already pins `2026.5.31-7159b8aed` | Deployed Quadlet line 12 |
| Missing capabilities | ❌ Already has `DropCapability=ALL` + `AddCapability=...` | Deployed Quadlet lines 48-49 |

**Root cause of confusion**: There were TWO containers:
1. `omega-searxng` (Quadlet-managed, pinned image, Python health check) — was failing from stale pasta/network namespace
2. `omega-searxng-test` (manual `podman run`, `:latest`, no health check) — created during debugging, inherited corrupted netns

The research teams analyzed the wrong container for some claims.

### What the Jem Report Got Right (with nuance)

| Claim | Verdict |
|-------|---------|
| Health check was already partially fixed | ✅ Correct — deployed Quadlet had Python urllib |
| DNS is broken | ✅ Correct — the real current blocker |
| Fresh container would fix DNS | ✅ Correct — verified with `podman run alpine:3.20 wget httpbin.org/ip` |
| MCP uses GET, invalid `limit` | ✅ Correct |
| `limit` param is invalid | ✅ Correct — SearXNG silently ignores it |
| `/healthz` doesn't exist | ❌ REFUTED — it does exist, returns "OK" 200 (`webapp.py:616-618`) |

---

## §2 COMPLETE FIX — ONE COMMAND SEQUENCE

### Phase 1: Container Stability (5 min, Kali)

**Step 1**: Kill broken containers and stale pasta:
```bash
podman rm -f omega-searxng-test 2>/dev/null || true
podman rm -f omega-searxng 2>/dev/null || true
pkill -f "pasta.*8017" 2>/dev/null || true
pkill -f "pasta.*searxng" 2>/dev/null || true
pkill -f "netns.*f798fb44" 2>/dev/null || true
rm -f /run/user/1000/netns/netns-* 2>/dev/null || true
ss -tlnp | grep 8017 || echo "✅ Port 8017 is free"
```

**Step 2**: Add ExecStopPost to Quadlet (`~/.config/containers/systemd/omega-searxng.container`):
```ini
[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s
ExecStopPost=/bin/sh -c 'pkill -f "pasta.*omega-searxng" 2>/dev/null; exit 0'
```

**Step 3**: Reload and start fresh:
```bash
systemctl --user daemon-reload
systemctl --user start omega-searxng.service
```

**Step 4**: Verify:
```bash
systemctl --user status omega-searxng
sleep 10
podman exec omega-searxng python3 -c "import socket; print('DNS:', socket.gethostbyname('google.com'))"
curl -s "http://127.0.0.1:8017/search?q=test&format=json" | python3 -m json.tool | head -10
```

### Phase 2: Config Hardening (15 min, Verity)

**Step 5**: Apply hardened `settings.yml` — key changes:
- `secret_key: "${SEARXNG_SECRET}"` (templated, not empty)
- `method: "POST"`
- `search.formats: [html, json]` (add json for MCP)
- Add google, bing, brave, semantic scholar engines
- Disable yahoo, mojeek (noisy/unnecessary)
- `enable_metrics: false`, `open_metrics: ''` (M8 compliance)

**Step 6**: Restart container:
```bash
podman restart omega-searxng
sleep 10
curl -s -X POST -d "q=test&format=json" http://127.0.0.1:8017/search | python3 -m json.tool | head -10
```

### Phase 3: MCP & Client Patches (15 min, Verity)

**Step 7**: Update `mcp_servers/searxng/server.py`:
- Change `client.get()` → `client.post()` with form data
- Remove invalid `limit` param
- Add `categories`, `engines`, `language`, `time_range`, `pageno` params
- Preserve `@m9_safe` decorator

**Step 8**: Update `src/omega/workers/background_researcher/searxng_client.py`:
- Fix `semantischolar` → `semantic scholar`
- Add `google` and `duckduckgo` to `DEFAULT_ENGINES`
- Actually pass `engines` to `form_data` (currently ignored!)
- Add `categories` and `language` params

### Phase 4: Quadlet Deployment (5 min, Kali)

**Step 9**: Apply final Quadlet — key decisions for Roc to weigh:

| Setting | Proposed | Rationale | Question for Roc |
|---------|----------|-----------|------------------|
| Image | `docker.io/searxng/searxng:2026.5.31-7159b8aed` | Odysseus-proven working | Use pinned tag or `ghcr.io` mirror? |
| HealthCmd | `/usr/sbin/python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:8080/", timeout=5).read(1)'` | Full path, IPv4, no quoting edge cases | ✅ Verified working |
| HealthTimeout | 5s or 10s? | Current 5s works but tight | Recommend 10s? |
| HealthStartPeriod | 15s or 30s? | Granian needs 5-15s init | 30s generous but safe |
| ExecStopPost | `pkill -f "pasta.*omega-searxng"` | Prevent port-hold on crash | ✅ Critical addition |

### Phase 5: Deep Health Check (next session, Verity design → Kali implement)

Current health check tests only Layer 1 (is Granian running?). Need:

- **Layer 2 probe**: DNS resolution test (`socket.gethostbyname('google.com')`)
- **Layer 3 probe**: End-to-end search test (submit query, verify at least 1 result)

These should run as a **separate systemd timer** (not Podman HealthCmd) to avoid false restarts from transient upstream failures.

### Phase 6: Cleanup (5 min, Verity)

- Archive stale `docs/research/omega-searxng.container` to docs/archive/
- Update OMEGA_ENGINE.md SearXNG section if needed

---

## §3 OPEN QUESTIONS FOR ROC

I need your forensic eye on these before executing:

1. **Image source**: Deployed Quadlet uses `docker.io/searxng/searxng:2026.5.31-7159b8aed` (Docker Hub). Jem Patch 1 uses `ghcr.io/searxng/searxng:2026.6.13-b48205b38` (GHCR). Which is preferred? Docker Hub rate-limits unauthenticated pulls; GHCR may have faster pulls from our network. But `2026.6.13` is newer — any regression risk?

2. **HealthTimeout 5s vs 10s**: The current 5s works. Verity's optional improvement suggests 10s. Is there a measurement showing 5s is too tight?

3. **HealthStartPeriod 15s vs 30s**: The container logs show `[INFO] Spawning worker-1` at ~5s after boot. 15s start period should be enough. Is there evidence of slower boots (e.g., on cold cache)? 

4. **`AddCapability=DAC_OVERRIDE`**: Your mining report shows the odysseus maintainer debated whether this is still needed. Our Quadlet includes it. Keep or drop?

5. **`UserNS=keep-id`**: SearXNG uses UID 977 internally. If we add `UserNS=keep-id` + `User=1000`, the UID mapping might conflict with `FORCE_OWNERSHIP=true`. Should we avoid `UserNS=keep-id` for SearXNG?

6. **MCP server port 8018**: The MCP server currently runs on port 8018 (SSE). Is this already registered anywhere? Any risk of collision with other Omega services?

7. **Health check endpoint**: `/healthz` returns "OK" with 200. `/` returns full HTML page with 200. Which should the health check use? `/healthz` is semantically cleaner and lighter. `/` is simpler (no endpoint dependency). Both work — pick one.

---

## §4 RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **DNS still broken after recreation** | Low | Critical | Verify with `socket.gethostbyname('google.com')` immediately after start |
| **Image `2026.5.31-7159b8aed` pulled from Docker Hub rate-limited** | Medium | High | Pre-pull with `podman pull` first; fallback to `2026.6.13` on GHCR |
| **settings.yml syntax error kills container** | Low | Medium | Validate YAML before restart: `python3 -c "import yaml; yaml.safe_load(open('data/searxng/config/settings.yml'))"` |
| **Engine names changed in new image** | Low | Medium | Verify after update: `curl http://localhost:8017/config \| jq '.engines[].name'` |
| **ExecStopPost exits non-zero, systemd considers unit failed** | Low | Medium | `exit 0` is included — verified pattern |

### Rollback Plan

| Component | Rollback |
|-----------|----------|
| Container | `podman rm -f omega-searxng && podman run -d --name omega-searxng-fallback ...` (old config) |
| settings.yml | `git checkout data/searxng/config/settings.yml` |
| MCP server | `git checkout mcp_servers/searxng/server.py` |
| Client | `git checkout src/omega/workers/background_researcher/searxng_client.py` |

---

## §5 L1→L2→L3 DISTILLATION

### L1 (Narrative)
SearXNG crash loop had 3 layers: (1) original health check used `curl` not in image (ALREADY FIXED), (2) stale pasta processes hold port 8017 on restart (NEEDS ExecStopPost), (3) manual test container has corrupted network namespace — DNS broken, container "healthy" but non-functional (NEEDS clean deletion + recreation). Eight secondary bugs found across MCP server, client, settings.yml, and stale docs.

### L2 (Insight)
Three independent failures cascaded: wrong health check → crash loop → stale pasta → restarts fail → manual container inherits corrupted namespace → appears healthy but can't search. Each layer masked the next. **Always destroy and recreate the entire stack after a crash loop.** Partial recovery inherits partial corruption.

### L3 (Universal Principle)
**A health check that only tests internal state is a liveness probe, not a health check.** True sovereign health verification must test outbound dependencies. For SearXNG: "healthy" should mean "can resolve DNS AND can reach at least one upstream engine AND returns search results." Any system self-certifying without dependency testing will experience silent partial failure.

---

## §6 EXECUTION FLOW (for Roc's review)

```
Kali: This report ──→ Roc: Review, correct, enhance
                      ↓
                 Roc: Approved synthesis
                      ↓
              Kali: Executes Phase 1 (5 min)
                      ↓
              Verity: Executes Phases 2-3 (30 min)
                      ↓
              Kali: Executes Phase 4 (5 min)
                      ↓
              Verity: Designs Phase 5 (next session)
                      ↓
              Verity: Executes Phase 6 (5 min cleanup)
```

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali_synthesis ⬡ PHASE-0*
*Date: 2026-06-21 | 7 sources synthesized | 6 phases planned | 7 open questions for Roc*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
