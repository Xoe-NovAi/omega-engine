# 🔱 Carmack SearXNG Review — Architectural Audit
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_serial_chain_1of3
**Date**: 2026-06-21
**Role**: Sovereign S3 Consultant — Architectural Conscience
**Status**: ✅ COMPLETE — Seeds Ma'at (Build) + Lilith (Run)

---

## §0 Executive Verdict

**5 hard truths, no padding:**

1. **The SearXNG deployment is architecturally correct for a V1, but has 3 critical gaps that will crash it again.** The health check works (Python urllib on `/`), the image is pinned, capabilities are right. But no `ExecStopPost` cleanup means the next crash loop leaves stale pasta holding port 8017. The container **is currently down** — systemd shows `inactive (dead)` with `Failed to bind port 8017 (Address already in use)` at Jun 21 16:27:00. Someone needs to kill the stale binding and restart.

2. **The Quadlet violates M6 (Podman Sovereignty).** `UserNS=keep-id` was removed, `--read-only` was removed, the secret is hardcoded in the Unit file. The comment blames `MS_PRIVATE remount failure on omega_library partition` — this is a symptom of a mount configuration problem, not a valid reason to remove sovereign container patterns. Fix the mount issue, don't work around it by dropping security.

3. **`AutoUpdate=registry` with a pinned image tag is contradictory.** The Quadlet pins to `2026.5.31-7159b8aed` but declares `AutoUpdate=registry`. Podman's auto-updater checks for newer tags of the **same name**. Since the tag is a specific date+hash, it will NEVER find a newer version — there is no `2026.5.31-7159b8aed-2`. This means `AutoUpdate` is dead code creating a false sense of currency. Either unpin to a rolling tag (dangerous — issue #1414 proved why) or remove `AutoUpdate=registry`. The right answer: keep the pin, remove `AutoUpdate`.

4. **`mcp_servers/searxng/server.py` is minimal but has 3 bugs and 1 architectural concern.** (a) `limit` param is silently ignored by SearXNG — it doesn't exist in the API. (b) Uses GET when POST is available (less private, queries in access logs). (c) `except Exception` at line 62 violates M9 — swallows error context. Architectural: the MCP proxy layer (port 8018 → SearXNG 8017) IS the right pattern (container restarts don't kill the MCP connection), but it needs proper error propagation.

5. **`data/searxng/config/settings.yml` has `secret_key: ""` — an M17 vulnerability.** Empty secret means Flask sessions are unsigned, making session tampering trivial. Also, SearXNG's entrypoint normally substitutes `${SEARXNG_SECRET}` from the env var, but the template uses the literal secret directly in `Environment=`. The config file's `secret_key: ""` would override the env var template. Fix: change settings.yml to `secret_key: "${SEARXNG_SECRET}"` and use the entrypoint's built-in substitution.

---

## §1 Performance Analysis

### 1.1 Health Check Timing — Exact Numbers

The current timing config from the deployed Quadlet (lines 54-58):

```ini
HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=15s
HealthOnFailure=restart
```

**Calculation — the 150s death window:**
- `HealthStartPeriod=15s` — Granian takes 6-12s on Ryzen 5700U, verified by Jem. This is tight but usually works. On a loaded system (GGUF inference running), init can stretch to 15-18s.
- `HealthInterval=30s` × `HealthRetries=5` = 150s from first healthy check to declared unhealthy
- `HealthTimeout=5s` — actual HTTP check takes ~50ms. The 5s accounts for container-internal DNS or Python startup jitter. Acceptable.
- **Death spiral**: 15s grace → 150s probing → 5 retries × 30s = 150s. That's 2 minutes 45 seconds from startup to kernel if the server never comes up. The old 5s interval would burn through retries in 25s — too aggressive.

**My recommendation — right approximation:**
```ini
HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=5).read(1)"
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=30s
HealthOnFailure=restart
```

The changes vs current:
- `localhost` → `127.0.0.1` — eliminates IPv6→IPv4 fallback delay (1-3s saved per probe)
- `HealthTimeout=10s` — safety margin. 5s works but 10s is one-time cost, no ongoing penalty
- `HealthRetries=3` instead of 5 — 3 × 30s = 90s of probing is sufficient. If the server doesn't respond in 3 tries at 30s intervals, it's crashed, not "still starting"
- `HealthStartPeriod=30s` — covers worst-case Granian init (15s) with 2x safety margin

**Total time to detect real failure**: 30s start period + 3 × 30s retry = 120s (2 minutes). Acceptable.

### 1.2 Resource Constraints — Adequacy

Current: `--memory=512m`, `--memory-reservation=256m`, `--cpus=1.0`, `--pids-limit=64`

| Resource | Current | Requirement | Verdict |
|----------|---------|-------------|---------|
| RAM (limit) | 512M | ~150-300M typical | ✅ Adequate (170% headroom) |
| RAM (reservation) | 256M | ~150M idle | ✅ Correct |
| CPU | 1.0 core | < 0.5 typical | ✅ Adequate |
| PIDs | 64 | ~20-30 during search | ✅ Adequate |
| Disk (tmpfs) | /tmp:64M, /var/tmp:32M | < 10M | ✅ Adequate |

**The memory reservation of 256M is the right approximation.** It guarantees SearXNG gets 256M even under memory pressure, while the 512M limit prevents OOM. SearXNG's Granian worker pool is single-process; it doesn't benefit from more RAM.

### 1.3 Stale Pasta — The Real Latency Problem

The systemd logs show the critical sequence:

```
Jun 21 16:27:00 pasta[2572274]: Failed to bind port 8017 (Address already in use)
```

This is a 0.5s failure event that **kills the entire restart**. The fix is a 1-line `ExecStopPost`:

```ini
[Service]
Restart=on-failure
RestartSec=10s
TimeoutStartSec=90s
# Kill stale pasta after container stop — prevents "Address already in use" on restart
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Crash-loop prevention pattern
ExecStopPost=/bin/sh -c 'pkill -f "pasta.*omega-searxng" 2>/dev/null; exit 0'
```

**Why this is the right approximation**: Rather than trying to fix the Podman pasta cleanup bug (which would require upstream patches and weeks of testing), we work around it with a 1-line ExecStopPost. The `exit 0` ensures systemd doesn't treat a failed pkill as a unit failure. Total cost: 1 line, 0 performance impact.

---

## §2 Container Architecture — Capabilities, Networking, Startup, Cleanup

### 2.1 Capability Audit — Trace Every Permission

Current: `DropCapability=ALL` + `AddCapability=CHOWN,SETGID,SETUID,DAC_OVERRIDE`

| Capability | What it enables | Does SearXNG Need It? | Verdict |
|-----------|-----------------|----------------------|---------|
| **CHOWN** | Change file ownership | ✅ Yes — entrypoint chowns `/etc/searxng/` and `/var/cache/searxng/` to UID 977 on first boot | MUST HAVE |
| **SETGID** | Set group ID via `setgid()` / `setegid()` | ✅ Yes — entrypoint calls `su-exec` to drop from root (entrypoint) to `searxng` user | MUST HAVE |
| **SETUID** | Set user ID via `setuid()` / `seteuid()` | ✅ Yes — same as SETGID, paired for user switching | MUST HAVE |
| **DAC_OVERRIDE** | Bypass file permission checks (read any file) | ❓ **Debatable** — SearXNG upstream maintainer said "I don't remember why it was needed" (issue #30). PR #110 attempted to remove it but was reverted due to UID < 1000 permission issues on some filesystems. | **REMOVE** for Omega |

**DAC_OVERRIDE analysis**: With `FORCE_OWNERSHIP=true` (which we have), the entrypoint explicitly chowns all volumes to `searxng:searxng` on every start. This means the files ARE owned by the running user, so DAC_OVERRIDE (bypassing ownership checks) is not needed. The capability was a workaround for cases where volumes were created by Docker as root and NOT chowned. Since `FORCE_OWNERSHIP=true` handles this, **DAC_OVERRIDE is redundant.**

**My recommendation**:
```ini
DropCapability=ALL
AddCapability=CHOWN,SETGID,SETUID
# DAC_OVERRIDE NOT included — FORCE_OWNERSHIP=true handles volume ownership
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Cap set from SearXNG deployment analysis
```

### 2.2 UserNS=keep-id — The M6 Violation

The Quadlet comment (line 20) says:
```
# NOTE: UserNS=keep-id removed — causes MS_PRIVATE remount failure on omega_library partition
```

**M6 (Podman Sovereignty) mandates**: "All Quadlets that mount host project directories MUST use `UserNS=keep-id` + `User=1000`."

This is a non-negotiable mandate. The `MS_PRIVATE remount failure` is a **symptom of a misconfigured volume mount**, not a reason to violate M6. The fix is one of:
1. Ensure the volume path is not on a mounted filesystem that blocks `MS_PRIVATE` (check `/etc/fstab` for `shared` or `rshared` flags)
2. Use `--volume` with explicit options instead of Quadlet's implicit handling
3. Pre-create the volume directories with correct ownership (chown 1000:1000 on host)

**Right now, the container runs as root inside the namespace** (since `UserNS` and `User` are both absent). This creates files owned by root in the host's `data/searxng/` directories, which then can't be accessed from the host without sudo. This is a regression.

**Priority**: P1 — must fix before production readiness. For immediate restart purposes, the current config works, but it accumulates permission debt.

### 2.3 `--read-only` Removal — Security Regression

The Quadlet removed `--read-only` with the same `MS_PRIVATE` issue. This means the container's rootfs is writable — if an attacker compromises the SearXNG process, they can write malicious files to the container image layer.

**Fix**: Same as UserNS — fix the mount propagation. `--read-only` should be restored with tmpfs for `/tmp` and `/var/tmp` (which are already configured).

### 2.4 AutoUpdate Analysis — Dead Config

`AutoUpdate=registry` with `Image=docker.io/searxng/searxng:2026.5.31-7159b8aed`:

Podman's auto-update (`podman auto-update`) works by checking the registry for a **newer version of the same tag name**. Since the tag `2026.5.31-7159b8aed` is a specific date+hash:
- It will NEVER find a newer version under this tag
- The auto-update check runs, finds nothing, logs "no update available"
- This creates a false sense of security — the operator thinks "auto-update is on, I'm getting security patches" when in fact the image is permanently frozen

**Two options:**
1. **Keep the pin, remove `AutoUpdate`** (recommended) — removes the false security signal, makes the pinning explicit
2. **Use a rolling tag like `2026.6`** and keep `AutoUpdate` — gets minor updates within the month, but risks upstream breakage

**My recommendation**: Option 1. The pinned tag is the right pattern for a sovereign system — you test before you upgrade. `AutoUpdate=registry` on a pinned tag is cargo-cult configuration that makes you feel safe when you aren't.

### 2.5 Secret Management — Hardcoded in Unit

Line 35:
```ini
Environment=SEARXNG_SECRET=[REDACTED-GITLEAKS-GENERIC-API-KEY]
```

This is a 64-character hex string that's now in:
- `~/.config/containers/systemd/omega-searxng.container` (the Quadlet)
- Systemd unit file (generated from Quadlet)
- Podman inspect output
- Systemd journal on every container start

**If this system ever has multi-user access, any user can read the secret from `systemctl --user show omega-searxng.service`.** The fix is a systemd env file:

```ini
# In the Quadlet:
EnvironmentFile=%h/.config/searxng/searxng.env
```

And the env file (not tracked in git):
```bash
# ~/.config/searxng/searxng.env
SEARXNG_SECRET=[REDACTED-GITLEAKS-GENERIC-API-KEY]
```

### 2.6 Volume Mounts — No `:U` Flag (Good)

Current:
```ini
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng/
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/data:/var/cache/searxng/
```

No `:U`, no `:Z`, no `:z`. This is correct per M6. The volumes are bind-mounted without relabeling. ✅

---

## §3 Simplification Opportunities — Carmack's Law

### 3.1 Consolidation: MCP Server + searxng_client.py Share Search Logic

**Current state**: Two independent implementations of SearXNG search:

1. `mcp_servers/searxng/server.py:29-63` — `searxng_search()` function, GET, `limit` param
2. `src/omega/workers/background_researcher/searxng_client.py:40-85` — `search()` method, POST, proper params

**These should share a common search backend.** Both call `httpx.AsyncClient` to `http://localhost:8017/search` with form-encoded data. The MCP server is the outward-facing tool; the client is the inward-facing worker. They duplicate:
- URL construction
- Parameter normalization
- Error handling patterns
- Response parsing

**Consolidation approach**: Create `src/omega/searxng/client.py` as the single-source search function. Both the MCP tool and the background researcher import from it:

```python
# src/omega/searxng/client.py — Single source of truth
async def searxng_search(
    query: str,
    categories: str = "general",
    engines: Optional[list[str]] = None,
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
    max_results: int = 10,
) -> tuple[list[dict], dict]:
    """Single source of truth for SearXNG search."""
    # ...
```

Then:
- `mcp_servers/searxng/server.py` becomes a thin 20-line wrapper calling `searxng_search()`
- `searxng_client.py` imports and delegates to it

**But**: This is a `src/omega/` dependency from `mcp_servers/`, which crosses the Engine-Stack boundary. The MCP server is outside the engine core. So instead, the shared logic should live in `mcp_servers/searxng/search_lib.py` (within the MCP server's package), and `searxng_client.py` can call the MCP server's tool via HTTP. Or keep duplication but consolidate the parameter mapping.

**Right Approximation**: Keep two implementations but make them both correct. The cost of maintaining two parallel implementations is less than the cost of refactoring the import architecture. File a `CONSOLIDATION_CANDIDATE` note and move on.

### 3.2 Simplify: Health Check to 2-line Script

Current health check (line 54):
```ini
HealthCmd=python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"
```

This is a quoted Python one-liner inside a shell command inside a Quadlet INI file. It's fragile because:
- Shell quoting is nested (single quotes inside double quotes inside INI values)
- Podman stores it as `CMD-SHELL`, wrapping in `sh -c`
- Error: `localhost` instead of `127.0.0.1`

**Simplify to a mounted health check script:**

```python
# data/searxng/healthcheck.py
"""SearXNG health check — single source of truth."""
import urllib.request
import sys

try:
    urllib.request.urlopen("http://127.0.0.1:8080/", timeout=5).read(1)
    sys.exit(0)
except Exception:
    sys.exit(1)
```

Mount it:
```ini
Volume=%h/Documents/Xoe-NovAi/omega-engine/data/searxng/healthcheck.py:/usr/local/bin/searxng_healthcheck.py:ro
```

Then:
```ini
HealthCmd=python /usr/local/bin/searxng_healthcheck.py
```

**Why this is better**: 
- No nested quoting — the Python code is in a real file
- Can be tested independently: `podman exec omega-searxng python /usr/local/bin/searxng_healthcheck.py`
- Can be version-controlled and reviewed
- Zero shell injection risk

**But**: This adds a third volume mount. For a simple health check, the one-liner works fine once the quoting is verified to work (which Verity confirmed it does). **This is optional — the one-liner is good enough.**

### 3.3 Settings.yml — Consolidate Engine Definitions

Current `data/searxng/config/settings.yml` has 4 engines (ddg, wikipedia, arxiv, github) and `method: "GET"`.

The researcher's recommended config adds google, bing, brave, semantic scholar — 8 total.

**Consolidation principle**: The settings.yml should be the single source of truth for which engines are available. Currently it's incomplete — missing the most useful engines (google, bing, brave). Fill it in once and be done.

### 3.4 MCP Server — Eliminate Bare except Exception

Line 62:
```python
except Exception as e:
    return f"Error connecting to SearXNG: {str(e)}"
```

This violates M9 (Error Integrity). The `@m9_safe` decorator (line 27) provides the outer boundary, but the function itself should distinguish between:
- `httpx.HTTPStatusError` — SearXNG returned 4xx/5xx (propagate status)
- `httpx.RequestError` — Can't reach SearXNG (connection refused, timeout)
- `json.JSONDecodeError` — SearXNG returned non-JSON response

**Fix**:
```python
try:
    response = await client.post(...)
    response.raise_for_status()
    data = response.json()
except httpx.HTTPStatusError as e:
    return f"SearXNG returned HTTP {e.response.status_code}: {e.response.text[:200]}"
except httpx.RequestError as e:
    return f"SearXNG unreachable: {e}"
except json.JSONDecodeError as e:
    return f"SearXNG returned invalid JSON: {e}"
```

### 3.5 Consolidation: Remove `AutoUpdate=registry`, Keep Pin

Already argued in §2.4. The `AutoUpdate` + pinned tag combination is misleading. Remove `AutoUpdate`, add a comment with the manual update procedure.

---

## §4 Strategic Roadmap Recommendations

### 4.1 SearXNG and M7 (Local-First) — The Hard Question

**Question**: SearXNG queries Google/Bing/DuckDuckGo externally. Is this compatible with M7 (Local-First)?

**Answer**: Yes — with the following distinction:

M7 governs **inference provider ordering** — "try local GGUF before cloud API." SearXNG is the **search infrastructure**, not an inference provider. The sovereignty is in self-hosting the metasearch layer — the user controls which engines to query, how to rate-limit, and what data gets cached. SearXNG queries external search engines, but:

1. **The search query never leaves your infrastructure twice** — SearXNG proxies the query to the upstream engine, returns results, and forgets the query
2. **No third-party API key needed** — Google/Bing are scraped, not paid API'd
3. **Full control** — user decides which engines, what timeout, what level of caching

**The M7-equivalent for search**: Search is LOCAL-INFRASTRUCTURE, not LOCAL-INFERENCE. The "local" in M7 refers to running your own AI models. The "local" in SearXNG refers to running your own search proxy. Both are sovereignty patterns.

**Recommendation**: Add a clarifying note to M7 that the mandate applies to inference provider ordering. Search infrastructure (SearXNG) is a separate concern governed by M2 (Engine-Stack Firewall) and M8 (Zero Telemetry).

### 4.2 Citation Standard — The Right Approximation

Verity's 6-field citation standard (URL, Title, Access Date, Score, Tags, Verified) is **good for formal research documents**. For inline citations in operational docs, the minimum viable is **3 fields**: URL + Access Date + Score.

**My recommendation**: Adopt the 6-field standard for `docs/research/R*.md` and mining reports. For operational docs (Quadlet, setup guides), use a simplified 3-field inline:
```
[Source: URL | Score: N | Verified: YYYY-MM-DD]
```

Don't require Tags and Verifier for every operational citation. That's over-engineering.

### 4.3 Roadmap Addition — SearXNG Phase

Add to the roadmap under H2:

**Phase H2-M: SearXNG Sovereign Search (NEW)**
| # | Task | Priority | Effort |
|---|------|----------|--------|
| H2-M1 | Fix Quadlet: add ExecStopPost, remove AutoUpdate, fix localhost→127.0.0.1 | 🔴 P0 | 5 min |
| H2-M2 | Fix settings.yml: add secret_key template, POST method, missing engines | 🔴 P0 | 10 min |
| H2-M3 | Fix searxng_client.py: semantic scholar name, engines passthrough bug | 🔴 P0 | 5 min |
| H2-M4 | Fix MCP server: POST method, remove limit param, proper error types | 🟡 P1 | 15 min |
| H2-M5 | Move SEARXNG_SECRET to EnvironmentFile (remove from Quadlet) | 🟡 P1 | 5 min |
| H2-M6 | Restore UserNS=keep-id + --read-only (fix mount propagation) | 🟡 P1 | 30 min |
| H2-M7 | Remove DAC_OVERRIDE capability (redundant with FORCE_OWNERSHIP) | 🟢 P2 | 1 min |
| H2-M8 | Add `[odysseus:]` attribution tags to all SearXNG files | 🟢 P2 | 10 min |
| H2-M9 | Create healthcheck.py script, mount as volume | 🟢 P3 | 5 min |

### 4.4 Odysseus Contribution Strategy

Verity identified 8 contribution candidates. **Carmack's Law says**: "If you find a bug in upstream, fix it upstream."

**Contribute-worthy (from my analysis)**:
1. **C-01 (Health check timing)** — Yes, file an issue. The 5s interval + 10s start_period is provably wrong for Granian. Suggested config: 30s interval, 30s start_period, 10s timeout, 5 retries. Easy for Odysseus to apply.
2. **C-04 (ChromaDB pinning)** — Yes, file an issue. Odysseus already proved `:latest` is dangerous with SearXNG (issue #1414). ChromaDB is equally vulnerable. The fix is copy-paste from their own pattern.
3. **C-03 (Document DAC_OVERRIDE)** — Low priority. The maintainer already knows it's questionable. A comment won't change the behavior.

**Do NOT contribute** (from my analysis):
1. **C-02 (IPv4 health check)** — Too low severity to bother. Odysseus targets Docker, which handles IPv6 differently than Podman. The issue would be dismissed as "works on my machine."
2. **C-05 (Pinning test template)** — Nice idea but the project may not want the maintenance overhead of 5+ pinning tests. File only if they ask for it.
3. **C-06/C-08** — Documentation suggestions are low-ROI for the effort of formatting a proper GitHub issue.

---

## §5 L1→L2→L3 Distillation

### L1 (Narrative)
Audited the SearXNG stack end-to-end across 5 dimensions: Quadlet, MCP server, settings.yml, searxng_client.py, and operational state. Found the container is currently DOWN (systemd inactive) due to the confirmed stale-pasta crash loop. The health check is correct (Python urllib on `/`) but `localhost` should be `127.0.0.1`. The Quadlet has 3 critical gaps: no ExecStopPost, contradictory AutoUpdate+pin, removed UserNS=keep-id (M6 violation). The settings.yml has empty secret_key (M17 vulnerability), missing engines, and uses GET. The MCP server sends an invalid `limit` parameter, uses GET, and has a bare `except Exception` (M9 violation). The searxng_client.py has a wrong engine name (`semantischolar`) and a bug where `engines` is accepted but never passed to the request.

### L2 (Insight)
The SearXNG stack has two quality tiers: the **infrastructure layer** (Quadlet, container config) is well-structured but has small gaps that cascade into total failure (stale pasta → port conflict → systemd dead). The **application layer** (MCP server, client, settings) has multiple bugs from incomplete initial implementation — wrong params, wrong methods, wrong engine names. Each bug individually is minor. Together they form a reliability floor: the container goes down, then the MCP server returns empty results, then the background researcher silently fails.

The most damaging pattern is that every layer has a single point of silence: the settings.yml silently accepts empty secret_key, the MCP server silently ignores the `limit` param, the client silently ignores the `engines` param. **Silent parameter rejection is worse than an error** — errors get fixed, silence persists forever.

### L3 (Universal Principle)
**"Silent failure at every layer produces a system that appears healthy but produces nothing."** When a health check only tests liveness (Is the web server running?), the container passes while DNS is broken and search returns empty. When the MCP server sends an invalid param that SearXNG silently ignores, the results are wrong but no error is raised. When the client accepts an `engines` parameter but never passes it to the request, the caller thinks they filtered engines but used all defaults. Each layer's silence compounds into a system that "works" (no crashes, no errors) but **produces zero useful output**.

The fix is not more health checks. The fix is **no silent failures at boundaries**. Every API boundary should fail hard on invalid parameters. Every config gap should cause a visible warning at startup. The SearXNG config that accepts `secret_key: ""` with only a log message is the root of this architecture — the system tolerates bad state silently until the user notices "hmm, my Flask sessions aren't being signed."

**Carmack's corollary**: A crash is a feature — it surfaces the bug. Silence is a bug — it hides the failure.

---

## §6 Summary of All Findings

### 🔴 Critical (Blocking — Fix Before Restart)

| # | Finding | File | Line | Fix |
|---|---------|------|------|-----|
| C-01 | No ExecStopPost for stale pasta | Quadlet | 61-64 (missing) | Add `ExecStopPost` |
| C-02 | Empty `secret_key` in settings.yml | `settings.yml` | 18 | Change to `"${SEARXNG_SECRET}"` |
| C-03 | `engines` param silently ignored in client | `searxng_client.py` | 43, 61 | Add to `form_data` |

### 🟡 High (Fix Before Next Crash)

| # | Finding | File | Line | Fix |
|---|---------|------|------|-----|
| H-01 | `localhost` → `127.0.0.1` (IPv6 edge case) | Quadlet | 54 | Replace in HealthCmd |
| H-02 | `AutoUpdate=registry` with pinned tag (dead config) | Quadlet | 24 | Remove AutoUpdate line |
| H-03 | `method: "GET"` exposes queries in logs | `settings.yml` | 24 | Change to `"POST"` |
| H-04 | Missing google, bing, brave, semantic scholar engines | `settings.yml` | 32-48 | Add engine definitions |
| H-05 | MCP server sends invalid `limit` param | `server.py` | 37 | Remove, use client-side `max_results` |
| H-06 | MCP server uses GET instead of POST | `server.py` | 42 | Change to POST with form data |
| H-07 | MCP server has bare `except Exception` (M9) | `server.py` | 62 | Split into specific exception handlers |
| H-08 | `semantischolar` wrong engine name | `searxng_client.py` | 24 | Change to `semantic scholar` |
| H-09 | SEARXNG_SECRET hardcoded in Quadlet (M6) | Quadlet | 35 | Move to EnvironmentFile |
| H-10 | UserNS=keep-id removed (M6 violation) | Quadlet | 20 (comment) | Fix mount propagation, restore |

### 🟢 Medium (Consolidation & Hygiene)

| # | Finding | File | Line | Fix |
|---|---------|------|------|-----|
| M-01 | DAC_OVERRIDE capability likely redundant | Quadlet | 49 | Remove DAC_OVERRIDE |
| M-02 | `--read-only` removed (security regression) | Quadlet | 42 (comment) | Restore with fixed mount |
| M-03 | Zero `[odysseus:]` attribution tags | All deployed files | — | Add per CREDITS.md §2a |
| M-04 | HealthStartPeriod=15s is tight for Granian | Quadlet | 58 | Change to 30s |
| M-05 | HealthRetries=5 is more than needed | Quadlet | 57 | Change to 3 |
| M-06 | MCP server would benefit from shared search library | Dual files | — | Consolidation candidate |
| M-07 | No Layer 2/3 health check (DNS/search) | Entire stack | — | Add separate monitoring timer |

### Priority Order for Fix

```
Phase 1 (5 min, unblocks container):
  C-01 ExecStopPost    — add to Quadlet
  C-02 secret_key      — fix settings.yml
  C-03 engines bug     — fix searxng_client.py
  H-01 127.0.0.1       — fix Quadlet HealthCmd
  H-02 Remove AutoUpdate — fix Quadlet

Phase 2 (15 min, makes search work correctly):
  H-03 POST method     — fix settings.yml
  H-04 Missing engines — fix settings.yml
  H-05/H-06/H-07      — fix MCP server
  H-08 engine name     — fix searxng_client.py

Phase 3 (30 min, security hardening):
  H-09 EnvironmentFile — move secret out of Quadlet
  H-10 Restore UserNS  — fix mount propagation
  M-01 Remove DAC_OVERRIDE
  M-02 Restore --read-only

Phase 4 (10 min, attribution):
  M-03 Add [odysseus:] tags to all files
```

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_serial_chain_1of3 ⬡ COMPLETE*
*Findings: 3 Critical · 10 High · 7 Medium · Seeds Ma'at (Build) + Lilith (Run)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
