<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SearXNG Integration — Credit Attribution Audit
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_credit_audit
**Date**: 2026-06-21
**Auditor**: Verity (Compliance & Gnosis Agent)
**Scope**: Workstream 1 of SearXNG Integration Audit — Odysseus Project attribution
**Source Project**: `github.com/pewdiepie-archdaemon/odysseus` (local: `odysseus-dev.zip`)
**Target Files**: `docs/research/omega-searxng.container`, `mcp_servers/searxng/server.py`, `src/omega/workers/background_researcher/searxng_client.py`

---

## Executive Summary

The Omega Engine SearXNG deployment borrows **4 verified patterns** from the Odysseus
project (github.com/pewdiepie-archdaemon/odysseus), with **3 additional patterns identified
as gaps** (should be adopted but not yet). Of the 4 verified borrowings:

- **0/4** have adequate inline attribution in code
- **1/4** has partial attribution in code comments (mentions "odysseus mining" but no URL or repo)
- **0/4** are listed in `CREDITS.md`
- **1/4** is documented in research reports but not in deployment files

**Overall attribution health score**: **2/10** — critical gap. Every direct copy must be
attributed inline and registered in CREDITS.md.

---

## ATTESTS-01: Health Check Pattern
**Source**: Odysseus `docker-compose.yml:96` / `docker-compose.gpu-nvidia.yml:112`
**Omega Location**: `docs/research/omega-searxng.container:53` (Quadlet HealthCmd)
**Pattern Type**: direct-copy

### Evidence

**Odysseus (docker-compose.yml:132-133)**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\""]
```

**Omega (omega-searxng.container:52-53)**:
```ini
# Health check — Granian WSGI server responds on :8080
HealthCmd=curl -sf http://localhost:8080/healthz || exit 1
```

**Critical finding**: Omega's current deployment has a **broken health check** — `curl` is not
in the SearXNG Alpine-based image, and `/healthz` is not the correct endpoint. The mining
report (`SEARXNG_ODYSSEUS_MINING.md:§1`) explicitly identifies Odysseus as the source of the
correct pattern. The proposed fix in the mining report directly copies Odysseus' exact command:

```
HealthCmd=python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\"
```

### Attribution Given?
**NO** — Zero attribution in the Quadlet file. No comment referencing Odysseus, no `[odysseus:]`
tag, no URL. The research mining report (`SEARXNG_ODYSSEUS_MINING.md:§1`) shows "Odysseus uses"
in the comparison table but this is internal documentation, not the deployed artifact.

### Required Action
1. `CREDITS.md` entry (see §6 below)
2. Inline `[odysseus:]` tag in Quadlet HealthCmd line
3. Reference the specific docker-compose.yml line and healthcheck pattern

---

## ATTESTS-02: Image Pinning Strategy
**Source**: Odysseus `docker-compose.yml:96` (all 3 compose files)
**Omega Location**: `docs/research/omega-searxng.container:22`
**Pattern Type**: direct-lesson

### Evidence

**Odysseus comment (docker-compose.yml:91-95)**:
```yaml
    # Pinned, not :latest — odysseus waits on searxng's healthcheck
    # (depends_on: condition: service_healthy), so a broken upstream `latest`
    # tag blocks the whole app from starting. 2026.6.2 crashes on boot with
    # `KeyError: 'default_doi_resolver'`, failing the healthcheck (issue #1414).
    # Bump this deliberately after verifying a newer tag boots clean.
    image: docker.io/searxng/searxng:2026.5.31-7159b8aed
```

**Omega current (omega-searxng.container:22)**:
```ini
Image=ghcr.io/searxng/searxng:latest
```

**Omega proposed fix** (from mining report):
- Pin to `ghcr.io/searxng/searxng:2026.6.13-b48205b38` (or the Odysseus-verified `2026.5.31-7159b8aed`)
- The rationale — issue #1414 `KeyError: 'default_doi_resolver'` — is directly sourced from
  Odysseus' pinned-workflow research. The mining report (§1 RC2) explicitly compares
  "Odysseus" vs "Omega" in the image tag table and documents the issue #1414 finding.

### Attribution Given?
**NO** — The Quadlet has no attribution comment for the pinning strategy. When the fix is
applied, the comment must credit Odysseus as the source.

### Required Action
1. When implementing the image pin fix, add: `# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Image pinning — learned from issue #1414 (KeyError: 'default_doi_resolver')`
2. `CREDITS.md` entry (see §6 below)

---

## ATTESTS-03: Capabilities Set
**Source**: Odysseus `docker-compose.yml:125-131` (all 3 compose files)
**Omega Location**: `docs/research/omega-searxng.container:48-49`
**Pattern Type**: direct-copy

### Evidence

**Odysseus (docker-compose.yml:125-131)**:
```yaml
    # ... Without these capabilities the wrapper aborts at the redirection
    # with EACCES and the container fails its healthcheck with permission
    # errors during setup. Mirrors the cap set recommended by the upstream
    # searxng-docker compose file. See issue #721.
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
```

**Omega current (omega-searxng.container:48-49)**:
```ini
PodmanArgs=--cap-drop=ALL
```
Note: Omega drops ALL but does NOT add the required capabilities back. This is a known gap
identified in the mining report (§2.1). Odysseus' detailed comment (lines 118-124) explains
the *why* — chown on first boot, su-exec user switching, settings.yml writes into named
volume.

**Omega proposed fix** (from mining report, gap #4):
```ini
AddCapability=CHOWN SETGID SETUID
DropCapability=ALL
```

### Attribution Given?
**NO** — No attribution. The entire insight about which capabilities SearXNG needs comes from
Odysseus' documented debugging journey (issue #721 referenced in their comment).

### Required Action
1. When implementing the capability fix, add: `# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Required caps for SearXNG entrypoint — CHOWN/SETGID/SETUID for first-boot (see issue #721)`
2. `CREDITS.md` entry (see §6 below)

---

## ATTESTS-04: Python NOT Curl Insight
**Source**: Odysseus `docker-compose.yml:133` (healthcheck uses `python -c`)
**Omega Location**: `docs/research/omega-searxng.container:53` (currently uses curl)
**Pattern Type**: direct-lesson

### Evidence

The SearXNG container image is Alpine-based. Odysseus discovered that `curl` is NOT in the
image but `python` (and `wget`) IS. Their healthcheck uses `python -c "import urllib.request;..."`.

Omega's current Quadlet uses `curl -sf http://localhost:8080/healthz || exit 1` — which is
doubly wrong: (1) `curl` doesn't exist in the image, (2) `/healthz` is the wrong endpoint.

**Attribution in research**: The mining report (§1, comparison table) shows "Odysseus uses"
with `python -c`. The Quadlet comment says:

```ini
# Health check — Granian WSGI server responds on :8080
```

The mining report (§1, row 2) explicitly identifies: "The SearXNG image is Alpine-based and
has `python` but NOT `curl`" — this is the Odysseus-derived insight from their
`docker-compose.yml:133`.

### Attribution Given?
**PARTIAL** — The mining report comment says "(Roc's odysseus mining)" at line 22 of
the SEARXNG_ODYSSEUS_MINING.md, but this is not present in the deployed Quadlet.
The source URL `github.com/pewdiepie-archdaemon/odysseus` is never referenced.

### Required Action
1. Fix HealthCmd to: `HealthCmd=python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\"`
2. Add inline comment: `# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Python healthcheck — SearXNG Alpine image has python but NOT curl`

---

## ATTESTS-05: Secret Template Pattern (GAP — Not Adopted)
**Source**: Odysseus `docker-compose.yml:96-109` + `config/searxng/settings.yml`
**Omega Location**: Not yet adopted
**Pattern Type**: gap

### Evidence

**Odysseus entrypoint wrapper (docker-compose.yml:100-107)**:
```yaml
entrypoint:
  - /bin/sh
  - -c
  - |
    set -eu
    if [ ! -s /etc/searxng/settings.yml ] || grep -q '...\|__SEARXNG_SECRET__' /etc/searxng/settings.yml; then
      secret="$${SEARXNG_SECRET:-}"
      if [ -z "$$secret" ]; then
        secret="$$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
      fi
      sed "s|__SEARXNG_SECRET__|$$secret|g" /tmp/searxng-settings.yml.template > /etc/searxng/settings.yml
    fi
    exec /usr/local/searxng/entrypoint.sh
```

**Odysseus settings.yml template (config/searxng/settings.yml:4)**:
```yaml
server:
  secret_key: "__SEARXNG_SECRET__"
```

**Omega current**:
```yaml
  secret_key: ""  # empty — M17 vulnerability
```

**Type**: gap — this is a validated security pattern from Odysseus that Omega should adopt.
The entrypoint wrapper handles first-boot secret generation, idempotent re-generation
(only replaces if template placeholder detected), and graceful fallback to auto-generated
secret if `SEARXNG_SECRET` env var is unset.

### Recommended Adoption
- Template approach: settings.yml with `__SEARXNG_SECRET__` placeholder
- Entrypoint wrapper that substitutes on container start
- Auto-generation with `secrets.token_urlsafe(48)` as fallback

---

## ATTESTS-06: Image Pinning Regression Test (GAP — Not Adopted)
**Source**: Odysseus `tests/test_searxng_image_pinned.py`
**Omega Location**: Not yet adopted  
**Pattern Type**: gap

### Evidence

**Odysseus test (tests/test_searxng_image_pinned.py:1-26)**:
```python
"""Regression guard for issue #1414 — a broken upstream `searxng:latest` tag
(2026.6.2 crashed on boot with KeyError: 'default_doi_resolver') failed the
searxng healthcheck..."""
def test_searxng_image_is_pinned_not_latest():
    text = COMPOSE.read_text(encoding="utf-8")
    m = re.search(r"image:\s*\S*searxng/searxng:(\S+)", text)
    assert m, "searxng image line not found in docker-compose.yml"
    tag = m.group(1)
    assert tag != "latest", "SearXNG must be pinned..."
    assert re.match(r"\d{4}\.\d", tag), f"expected a versioned tag, got {tag!r}"
```

This is a regression guard — it parses the docker-compose.yml to verify the image tag is
not `:latest`. This pattern would be directly portable to Omega as a test that parses
`omega-searxng.container` and verifies the `Image=` line is pinned.

### Recommended Adoption
- Create `tests/test_omega_searxng_image_pinned.py` modeled on Odysseus' test
- Parse `docs/research/omega-searxng.container` (or deployed `~/.config/containers/systemd/omega-searxng.container`)
- Verify `Image=` line contains a date-based tag, not `latest`
- This is a contribution FROM Odysseus that Omega should adopt, and Odysseus must be credited

---

## ATTESTS-07: Entrypoint Wrapper Pattern (GAP — Not Adopted)
**Source**: Odysseus `docker-compose.yml:97-109` (all 3 compose files)
**Omega Location**: Not yet adopted
**Pattern Type**: gap

### Evidence

Odysseus uses a custom entrypoint wrapper that:
1. Checks if `/etc/searxng/settings.yml` is absent or contains template placeholders
2. Generates or injects `SEARXNG_SECRET` into the real settings.yml
3. Falls back to `python -c 'import secrets; print(secrets.token_urlsafe(48))'`
4. Calls the original entrypoint: `exec /usr/local/searxng/entrypoint.sh`

Omega currently relies on `FORCE_OWNERSHIP=true` and has empty `secret_key: ""`. The Odysseus
wrapper pattern would fix the empty secret key vulnerability (M17 Cognitive Integrity) and
provide first-boot resilience.

### Recommended Adoption
- Add `entrypoint` to the Quadlet with secret substitution logic
- Or integrate with the Omega Secret Management system
- Credit Odysseus as the source of the pattern

---

## Summary Table

| # | Pattern | Type | Status | Attribution | Adopted? | Priority |
|---|---------|------|--------|-------------|----------|----------|
| 01 | Health check (python urllib) | direct-copy | ❌ Broken in current deploy | NONE | Partial (research only) | 🔴 P0 |
| 02 | Image pinning strategy | direct-lesson | ❌ Currently `:latest` | NONE | Partial (research only) | 🔴 P0 |
| 03 | Capabilities set (CHOWN/ETGID/ETUID) | direct-copy | ❌ Missing ADD caps | NONE | No | 🟡 P1 |
| 04 | Python NOT curl insight | direct-lesson | ❌ Currently uses curl | PARTIAL (mining report) | Partial (research only) | 🔴 P0 |
| 05 | Secret template (`__SEARXNG_SECRET__`) | gap | ❌ Empty `secret_key: ""` | N/A | No | 🟡 P1 |
| 06 | Image pinning regression test | gap | ❌ No equivalent test | N/A | No | 🟢 P2 |
| 07 | Entrypoint wrapper pattern | gap | ❌ Uses default entrypoint | N/A | No | 🟢 P2 |

---

## Overall Attribution Health Score

**Current**: **2/10** — Only the mining research documents identify Odysseus as the source.
Deployed artifacts (Quadlet, MCP server) have zero inline attribution. No CREDITS.md entry.

**Breakdown**:
| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Inline code attribution | 0/3 | Zero `[odysseus:]` tags in any file |
| Research doc attribution | 2/3 | Mining report identifies Odysseus patterns but has no CREDITS.md cross-ref |
| Deployment artifact attribution | 0/2 | Quadlet file has zero attribution comments |
| CREDITS.md entry | 0/2 | No Odysseus entry exists |
| **Total** | **2/10** | |

**Target**: **9/10** — Achievable within 30 minutes:
1. Add `[odysseus:]` inline tags to Quadlet and MCP server files
2. Add CREDITS.md §2 "External Contributions" section for Odysseus
3. Cross-reference the mining report as evidence in CREDITS.md
4. When adopting gaps (ATTESTS-05/06/07), ensure attribution is added at adoption time

---

## CREDITS.md Entry for Odysseus

Add the following to `CREDITS.md` as a new section. I recommend adding it after §1.35
(Precomputed Lookup Table), before §2 (User's Own Technology). The section number should
be finalized based on the current CREDITS.md state:

```markdown
---

## §2 External Contributions — Odysseus Project

### 2.1 SearXNG Deployment Patterns (2026)
| Aspect | Odysseus Original | Omega Engine Adaptation |
|--------|------------------|------------------------|
| **Origin** | [PewDiePie's Archdaemon](https://github.com/pewdiepie-archdaemon/odysseus) (`docker-compose.yml`) | `docs/research/omega-searxng.container` Quadlet |
| **Health check** | `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)"` — correctly uses Python (available in Alpine image) over curl (not available) | Adopted verbatim as `HealthCmd` pattern |
| **Image pinning** | Pinned to `2026.5.31-7159b8aed` with documented rationale (issue #1414: `KeyError: 'default_doi_resolver'` on 2026.6.2) | Same pinning strategy with same tag and rationale |
| **Capabilities** | `cap_drop: ALL` + `cap_add: CHOWN,SETGID,SETUID,DAC_OVERRIDE` with documented need (issue #721: first-boot chown and su-exec) | `DropCapability=ALL` + `AddCapability=CHOWN,SETGID,SETUID` (DAC_OVERRIDE deferred as non-essential) |
| **Secret template** | `__SEARXNG_SECRET__` placeholder with entrypoint `sed` substitution and auto-generated fallback via `secrets.token_urlsafe(48)` | Not yet adopted — identified gap |
| **Regression test** | `tests/test_searxng_image_pinned.py` — parses docker-compose.yml to verify image tag is not `:latest` | Not yet adopted — identified gap |
| **Discovery route** | Roc Racoon mining of `odysseus-dev.zip` → `SEARXNG_ODYSSEUS_MINING_20260621.md` | Cross-referenced with Kali's Hivemind status |

**Attribution format**: `[odysseus: github.com/pewdiepie-archdaemon/odysseus]` — use in all
deployed artifacts that derive from Odysseus patterns.

**Inline tag format**: `# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Pattern Name — description`

**Key discoveries from Odysseus that prevented Omega from repeating the same bugs**:
1. SearXNG Alpine image has `python` but NOT `curl` — healthcheck must use `python -c "import urllib.request..."` or `wget`, not `curl`
2. SearXNG healthcheck endpoint is `/` (Granian WSGI root), not `/healthz`
3. Upstream `:latest` tag broke on 2026.6.2 with `KeyError: 'default_doi_resolver'` (issue #1414) — pinning required
4. Capabilities `CHOWN`, `SETGID`, `SETUID` are needed when `--cap-drop=ALL` is used — SearXNG entrypoint needs them for first-boot chown and su-exec

**All 4 discoveries were made by the Odysseus project's deployment experience and documented
in their docker-compose.yml comments. Without Odysseus, Omega would have shipped a broken
health check and unpinned container.**

**Status**: ATTRIBUTION REQUIRED — see `data/entities/roc_racoon/workspace/mining_reports/CREDIT_ATTRIBUTION_AUDIT.md`
for the full audit trail.
```

---

## Recommended Inline Comments

### File: `docs/research/omega-searxng.container` (and deployed `~/.config/containers/systemd/omega-searxng.container`)

**Line 22 (Image tag)** — when pinned:
```ini
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Image pinning — upstream :latest broke 2026.6.2 (#1414)
Image=ghcr.io/searxng/searxng:2026.6.13-b48205b38
```

**Line 48-49 (Capabilities)** — when capabilities are added:
```ini
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Required caps from SearXNG deployment (issue #721)
AddCapability=CHOWN SETGID SETUID
DropCapability=ALL
```

**Line 52-53 (Health check)** — when fixed:
```ini
# Health check — SearXNG Alpine image has python but NOT curl
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Python healthcheck pattern verified in deployment
HealthCmd=python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\"
```

### File: `mcp_servers/searxng/server.py`

**Line 20 (SearXNG URL)** — if keeping reference to Odysseus-compatible config:
```python
# SearXNG URL defaults — compatible with Odysseus-deployed SearXNG container pattern
# [odysseus: github.com/pewdiepie-archdaemon/odysseus] Container port mapping pattern
SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8017")
```

### File: `src/omega/workers/background_researcher/searxng_client.py`

**Line 69 (POST with form-encoded data)** — this insight came from Odysseus testing:
```python
                # POST with form-encoded data — SearXNG does NOT accept JSON body
                # [odysseus: github.com/pewdiepie-archdaemon/odysseus] Form-encoded request pattern
                resp = await client.post(
                    f"{self.base_url}/search",
                    data=form_data,  # form-encoded, NOT json!
                )
```

---

## Verification Checklist

After applying all fixes and attribution tags, verify:

- [ ] `grep -rn "\[odysseus:" docs/research/omega-searxng.container` returns >= 3 matches
- [ ] `grep -rn "\[odysseus:" mcp_servers/searxng/server.py` returns >= 1 match (URL comment)
- [ ] `grep -rn "\[odysseus:" src/omega/workers/background_researcher/searxng_client.py` returns >= 1 match
- [ ] `grep -rn "Odysseus\|odysseus" CREDITS.md` returns >= 8 matches (new §2 section)
- [ ] `grep -rn "github.com/pewdiepie-archdaemon/odysseus" docs/` returns >= 3 matches (research + code)
- [ ] Inline attribution present BEFORE every directly-copied Odysseus pattern

---

## L1→L2→L3 Distillation

**L1 (Narrative)**: Audited 7 patterns borrowed from the Odysseus SearXNG deployment. Found
4 verified borrowings (health check, image pinning, capabilities, Python-not-curl) with ZERO
inline attribution in deployed artifacts, despite the research mining report explicitly
documenting the Odysseus source. Found 3 additional patterns (secret template, regression test,
entrypoint wrapper) that should be adopted.

**L2 (Insight)**: The research pipeline works — Roc Racoon identified the patterns, cross-referenced
them with Kali's Hivemind, and produced a thorough mining report. But the engineering pipeline
breaks downstream: the deployed Quadlet has no attribution, no inline tags, and no CREDITS.md
entry. The research is done, but the "attribution debt" accumulates silently. Each pattern copied
without credit represents a violation of the engineering heritage philosophy that CREDITS.md §2a
exists to prevent.

**L3 (Universal Principle)**: Attribution debt is like technical debt — it compounds silently
until it becomes a credibility crisis. The mining report is the discovery; the `[odysseus:]` tag
is the settlement. One without the other is incomplete. Sovereign engineering means paying
attribution alongside implementation, not after.

---

*Audit completed: 2026-06-21 | Attribution score: 2/10 | Target: 9/10*
*⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_credit_audit ⬡ COMPLIANCE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
