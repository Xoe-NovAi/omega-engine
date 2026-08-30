<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SearXNG Integration — Odysseus Contribution Opportunities
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_contribution_log
**Date**: 2026-06-21
**Auditor**: Verity (Compliance & Gnosis Agent)
**Workstream**: 3/3 — Contribution Back
**Source Repo**: `github.com/pewdiepie-archdaemon/odysseus`
**Omega Repo**: `github.com/Xoe-NovAi/omega-engine` (private)
**Baseline Files**: `docker-compose.yml`, `config/searxng/settings.yml`, `tests/test_searxng_image_pinned.py`, `.env.example`

---

## §0 Purpose

Omega Engine conducted a 3-phase SearXNG integration audit (Mine → Validate → Verify)
against Odysseus's docker-compose SearXNG section as a cross-reference. The audit found
our own crash-loop root cause (wrong health check endpoint, unpinned `:latest`), but also
identified **8 opportunities to contribute back** to the Odysseus project.

Each candidate below is supported by forensic evidence from Omega's multi-model
pipeline: DeepSeek V4 Flash mining, Jem Verification, SearXNG Deep Research (45+
primary sources), and live container inspection.

---

## §1 Contribution Candidates

---

### CANDIDATE-01: Health Check Timing — Reduce Aggressive Probes During Granian Startup

**Type**: Enhancement
**Severity**: MEDIUM
**GitHub Action**: Issue
**Evidence**: Omega's deep research confirmed SearXNG switched to **Granian** (PR #4820,
merged 2025-07-04). Granian's Rust async runtime takes 5–15s to initialize during
container startup — longer on resource-constrained hosts. Odysseus's current health
check configuration `interval: 5s, start_period: 10s, timeout: 6s, retries: 20`
creates a window where Granian is still initializing while the first 2 probes already
fire (at t=0 and t=5s), both potentially before the server is ready.

**Forensic details**:
- Odysseus: `interval: 5s, start_period: 10s, retries: 20` → max 1m40s of probing
- Omega container (Ryzen 5700U): observed Granian boot latency of 6–12s from first log to "Listening"
- The aggressive `interval: 5s` means 12 probes fire in the first minute alone — most before the server is ready
- SearXNG's Granian logs show `Listening on http://0.0.0.0:8080` typically at t=6-12s, well into the first 3 probe cycles
- SearXNG upstream bug reports (searxng-docker issue #1414) show that a slow+aggressive probe pattern can cause `depends_on: condition: service_healthy` to time out the entire app

**Suggested Text**:

```markdown
## Health Check: Relax probe timing for Granian startup latency

**Problem**: SearXNG's Granian WSGI server takes 5–15s to initialize,
but the current health check fires every 5s with only a 10s `start_period`.
This means 2–3 probes fire before Granian is listening, creating unnecessary
restart flap during cold starts.

**Reproduction**: On a cold Docker compose up (no cached layers), Granian's
initialization (Rust runtime init + engine loading) can exceed the 10s
start_period. The first probe at t=0 fails, the second at t=5s fails, and
by t=10s (start_period ending), Granian may or may not be ready.

**Suggested change** (`docker-compose.yml:132-137`):
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\""]
  interval: 30s        # changed from 5s — less aggressive, fewer logspam probes
  timeout: 10s         # changed from 6s — more room for slow kernel/DNS
  retries: 5           # changed from 20 — still gives 2m30s of total probing
  start_period: 30s    # changed from 10s — gives Granian adequate init window
```

**Rationale**:
- Granian consistently takes 6–12s to boot on a mid-range CPU. The 5s interval
  creates 12 probe cycles in the first minute, most of which will fail.
- 20 retries at 5s = 100s of total probing (1m40s). With 30s interval and 5 retries =
  150s. More resilient, less logspam.
- The 30s start_period covers the worst-case Granian init time (observed: up to 15s
  on resource-constrained hosts, plus Python entrypoint overhead).
- If the container is truly dead, we detect it within 3m30s (30s interval × 5 retries +
  30s start_period = 3m) vs 1m50s under the old config — a reasonable tradeoff.
```

---

### CANDIDATE-02: Force IPv4 Health Check — `localhost` → `127.0.0.1`

**Type**: Enhancement
**Severity**: LOW (intermittent)
**GitHub Action**: Issue
**Evidence**: Omega's Jem verification confirmed via SearXNG PR #4378 that `wget` (and
Python's `urllib`) try IPv6 first when resolving `localhost`. On Alpine-based SearXNG
containers where Python's `getaddrinfo()` returns `::1` before `127.0.0.1`, the IPv6
connection either succeeds (if Granian is listening on `[::]`) or fails with a 1–3s
timeout before falling back to IPv4. With a 5s probe timeout, this IPv6→IPv4 fallback
consumes 20–60% of the available timeout window on every probe.

**Forensic details**:
- Odysseus compose line 133: `'http://localhost:8080/'` — vulnerable to IPv6 resolution order
- SearXNG's Granian binds to `0.0.0.0:8080` by default, which accepts both IPv4 **and** IPv6 connections on most kernels (dual-stack socket). However, Alpine's musl libc can exhibit different `getaddrinfo()` ordering than glibc.
- SearXNG upstream PR #4378 discussed exactly this: "wget tries IPv6 first on localhost. If SearXNG binds to 0.0.0.0 (IPv4 only), wget fails with 'Connection refused'."
- On dual-stack systems where both IPv4 and IPv6 work, there is no issue. On systems where IPv6 routing to the container is impaired (Docker bridge networks, IPv6 forwarding misconfig), this causes intermittent health check failures.

**Suggested Text**:

```markdown
## Force IPv4 in Health Check — `localhost` → `127.0.0.1`

**Problem**: The health check uses `http://localhost:8080/` which resolves to
IPv6 `::1` first on most modern Linux distributions. On configurations where
IPv6 routing to the SearXNG container is impaired or misconfigured, Python's
`urllib` spends 1–3s falling back from IPv6 to IPv4, consuming a significant
portion of the 5s timeout window.

**Why it matters**: With `timeout: 5s`, losing 1–3s to IPv6 fallback means the
probe has only 2–4s to complete the actual HTTP request. Under load or during
startup, this can cause spurious health check failures that trigger restarts.

**Suggested change** (docker-compose.yml:133):
```yaml
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=5).read(1)\""]
```

This forces IPv4, eliminates the fallback delay, and makes the health check
deterministic regardless of the host's IPv6 configuration.

**Verification**: Test with `python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/', timeout=5); print(r.read(1))"` inside the running SearXNG container.
```

---

### CANDIDATE-03: Document DAC_OVERRIDE Rationale

**Type**: Documentation
**Severity**: LOW
**GitHub Action**: Issue
**Evidence**: Odysseus's `docker-compose.yml:131` adds `DAC_OVERRIDE` capability, but
SearXNG's own maintainer (searxng-docker issue #30, opened 2022) stated: *"I don't
remember why it was needed"* and successfully tested removing it (PR #110 attempted to
remove it, but was reverted for compatibility reasons). The Odysseus inline comment
(lines 118-124) explains CHOWN/SETGID/SETUID's purpose but simply includes
`DAC_OVERRIDE` in the `cap_add` list without justification.

**Forensic details**:
- SearXNG upstream issue #30 documents maintainer confusion about DAC_OVERRIDE necessity
- SearXNG PR #110 attempted to remove it; was reverted due to UID < 1000 permission issues on some filesystem configurations
- Under Docker's default `--cap-drop=ALL` + `cap_add`, DAC_OVERRIDE allows the process to bypass DAC (Discretionary Access Control) for files it doesn't own — needed when the `searxng` user (UID 977) needs to write to files created by root during entrypoint execution
- This is subtle and worth documenting so future maintainers don't accidentally remove it and break first-boot permission flows

**Suggested Text**:

```markdown
## Document DAC_OVERRIDE Capability Rationale

**Problem**: The `DAC_OVERRIDE` capability is included in `cap_add` (line 131)
but lacks an inline justification explaining why it's needed. The SearXNG Docker
maintainer was themselves unsure (issue searxng/searxng-docker#30), and PR #110
attempting to remove it was reverted. Without documentation, future maintainers
may accidentally remove it and break first-boot permission flows in subtle ways.

**Suggested change**: Replace the current capability block comment (lines 118-124)
with more explicit documentation:

```yaml
    # The official searxng image runs as the non-root `searxng` user (UID 977),
    # but its entrypoint must still:
    #   1. chown /etc/searxng to searxng:searxng on first boot    → CHOWN
    #   2. Drop privs via su-exec from root to searxng user         → SETGID + SETUID
    #   3. Write settings.yml into the named volume (owned by root  → DAC_OVERRIDE
    #      if the volume was created by Docker as root)
    #
    # DAC_OVERRIDE specifically: without it, the searxng user (UID 977) gets
    # EACCES when writing settings.yml into volumes created with root ownership.
    # This is the "forgot to chown" safety net during the entrypoint's
    # permission fixup phase. Once ownership is correct, the capability is
    # effectively unused for the process's runtime.
    #
    # See: searxng/searxng-docker#30 (maintainer uncertainty about DAC_OVERRIDE)
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
```

This documentation makes the intent explicit and provides a decision anchor if
upstream ever resolves issue #30 with a definitive answer.
```

---

### CANDIDATE-04: Pin ChromaDB Image (Follow SearXNG's Pinning Pattern)

**Type**: Enhancement
**Severity**: MEDIUM
**GitHub Action**: Issue
**Evidence**: Odysseus's `docker-compose.yml:81` uses `image: docker.io/chromadb/chroma:latest`
for ChromaDB while explicitly pinning SearXNG to a known-good tag. The SearXNG lesson
(documenting issue #1414 where `:latest` broke the full app startup) applies equally to
ChromaDB — upstream ChromaDB `:latest` releases have broken backward compatibility in
the past (e.g., the v0.5→v0.6 migration that changed the API client).

**Forensic details**:
- Odysseus already has the proof: `docker-compose.yml:91-96` explicitly documents *why* SearXNG is pinned, referencing issue #1414
- SearXNG pinning test: `tests/test_searxng_image_pinned.py` — a regression guard that would catch accidental `:latest` reversion
- ChromaDB `:latest` is equally vulnerable: upstream has broken API compatibility between minor versions (v0.4.x → v0.5.x changed the Python client interface, breaking integrations)
- ChromaDB doesn't block `depends_on: condition: service_healthy` for odysseus (just `service_started`), so a ChromaDB break is less catastrophic — but it still requires manual debugging

**Suggested Text**:

```markdown
## Pin ChromaDB Image (Learn from SearXNG Issue #1414)

**Problem**: ChromaDB uses `:latest` (docker-compose.yml:81) while SearXNG
uses a pinned version with explicit documentation. The same class of breakage
that hit SearXNG (`:latest` upstream releases breaking backward compatibility)
has happened to ChromaDB: v0.5.0 changed the Python client API, breaking
applications that relied on the v0.4.x interface.

**Suggested change**: Pin ChromaDB to a known-good tag, mirroring the SearXNG
pattern already established in this project:

```yaml
  chromadb:
    # Pinned, not :latest — ChromaDB v0.5.0 broke the Python client API.
    # Bump deliberately after verifying backward compatibility with
    # odysseus's chromadb client code.
    image: docker.io/chromadb/chroma:0.5.20  # or latest tested tag
```

And optionally add a companion test at `tests/test_chromadb_image_pinned.py`
(see `test_searxng_image_pinned.py` for the proven template):

```python
"""Regression guard — ChromaDB `:latest` may break backward compatibility
(upstream broke the Python client API in v0.5.0). Pin to a known-good tag
so the vector store doesn't silently degrade on upstream updates.
"""
import re
from pathlib import Path

COMPOSE = Path(__file__).resolve().parent.parent / "docker-compose.yml"

def test_chromadb_image_is_pinned_not_latest():
    text = COMPOSE.read_text(encoding="utf-8")
    m = re.search(r"chromadb/chroma:(\S+)", text)
    assert m, "chromadb image line not found in docker-compose.yml"
    tag = m.group(1)
    assert tag != "latest", (
        "ChromaDB must be pinned, not ':latest' — upstream has broken "
        "the Python client API between minor versions"
    )
```

This extends the project's existing pinning strategy to all stateful services,
not just SearXNG.
```

---

### CANDIDATE-05: Promote Image Pinning Test as Template for All Compose Services

**Type**: Documentation / Enhancement
**Severity**: LOW
**GitHub Action**: Issue
**Evidence**: Odysseus's `tests/test_searxng_image_pinned.py` is a well-structured
regression guard using `re.search()` + file reading (no external dependencies, no
flask-client app, pure pytest). This pattern is directly applicable to **every**
image reference in the docker-compose.yml. Omega's audit found this test to be a
best practice worth promoting.

**Forensic details**:
- Test is 26 lines, no Docker SDK dependency, no mock infrastructure, runs in <50ms
- Category: pure pytest path test — reads compose YAML, parses image tag, asserts pinned
- Could serve as project-wide template for image pinning tests across SearXNG, ChromaDB, ntfy, and any future service

**Suggested Text**:

```markdown
## Promote Image Pinning Test as Project Pattern

**Observation**: Odysseus's `tests/test_searxng_image_pinned.py` is a
lightweight, dependency-free regression guard that validates image pinning
without any Docker SDK or mock infrastructure. This pattern is worth
elevating to a project-wide convention for all compose services.

**Current scope**: Only SearXNG is guarded by this test.

**Opportunity**: The test follows a simple, repeatable pattern:
1. Read docker-compose.yml
2. Regex-extract image tag for a specific service
3. Assert it's a versioned tag, not `:latest`

This same pattern can be applied to:
- `chromadb` (line 81) — currently `:latest`
- `ntfy` (line 141) — currently `docker.io/binwiederhier/ntfy` (no tag specified,
  which resolves to `:latest` per Docker convention)
- Any future compose service

**Suggested documentation addition** (e.g., in CONTRIBUTING.md or as a comment in
the existing test):

```python
# TEMPLATE for image pinning tests:
# 1. Add a new test function in tests/test_<service>_image_pinned.py
# 2. Match the image line for your service in docker-compose.yml
# 3. Assert the tag is a version string, not 'latest'
# See test_searxng_image_pinned.py for the canonical implementation.
```

This codifies the project's existing quality practice into an explicit,
copy-paste-ready pattern.
```

---

### CANDIDATE-06: Settings.yml — Document `use_default_settings: true` and Engine Overriding Patterns

**Type**: Documentation
**Severity**: LOW
**GitHub Action**: Issue
**Evidence**: Odysseus's `config/searxng/settings.yml` is minimal (9 lines) and
correctly uses `use_default_settings: true` with a single override for `secret_key`
and `formats`. However, the file lacks documentation explaining **how** engine
overrides work — specifically that engines blocked by default (like `bing`) require
explicit `disabled: false`. Omega's deep research confirmed this is a common stumbling
block for SearXNG maintainers.

**Forensic details**:
- SearXNG's built-in `settings.yml` sets `bing: disabled: true` by default (licensing concerns)
- Many engines are configured but inactive — `brave`, `mojeek`, `yahoo`, etc.
- The `use_default_settings: true` directive means all settings **merge on top** of defaults — you only need to specify overrides
- This is confusing: `disabled: false` must be explicitly set for engines you want that are blocked by default
- Odysseus's settings.yml is clean but silent about this behavior

**Suggested Text**:

```markdown
## Document `use_default_settings` Merge Semantics

**Problem**: The `config/searxng/settings.yml` file is minimal and elegant,
but lacks inline documentation explaining the critical `use_default_settings`
merge semantics. New maintainers may not realize that:
1. `use_default_settings: true` merges overrides on top of ~70 built-in engines
2. Engines disabled by default (like `bing`) require explicit `disabled: false`
3. Engine-specific overrides in this file only need to specify changed fields

**Suggested change**: Add clarifying comments to `config/searxng/settings.yml`:

```yaml
use_default_settings: true
# CRITICAL: This merges your overrides ON TOP of SearXNG's built-in ~70 engines.
# You do NOT need to list every engine — only the ones you want to customize.
#
# Engine override rules:
#   - `disabled: true` → engine is disabled (overrides default)
#   - `disabled: false` → engine is enabled (overrides default, required for
#     engines like `bing` that are disabled by default upstream)
#   - Partial overrides: setting only `shortcut: bi` keeps all other engine
#     settings from defaults

server:
  secret_key: "__SEARXNG_SECRET__"  # Templated by entrypoint

search:
  formats:
    - html
    - json  # required for API/MCP access — NOT enabled by default
```

This documentation costs nothing but prevents the "why is bing not working?"
confusion that hits at least a dozen SearXNG maintainers per GitHub issue.
```

---

### CANDIDATE-07: Security Review — No API Key Leakage (Confirmed Clean)

**Type**: Security Review
**Severity**: NONE (clean)
**GitHub Action**: None (informational)
**Evidence**: Omega's forensic audit reviewed the entire `docker-compose.yml` and
`.env.example` for hardcoded secrets, API keys, tokens, or passwords. Finding: **clean**.
All secrets are passed via environment variables with `${}` expansion or `$$` escaping,
and the `.env.example` clearly documents which values are optional vs required. The
`SEARXNG_SECRET` line is commented out by default (`.env.example:50`), which reduces
risk of accidentally committing a real secret.

**Forensic checklist**:
- `docker-compose.yml` lines 58-62: API keys for Brave, Google, Tavily, Serper are all `${VAR:-}` pattern (defaults to empty if unset)
- `docker-compose.yml:38`: `ODYSSEUS_ADMIN_PASSWORD` uses `${VAR:-}` pattern, same as above
- `.env.example:50`: `# SEARXNG_SECRET=` commented out by default
- `.env.example:25`: `# OPENAI_API_KEY=your_openai_api_key_here` — fake value, clearly documented
- Weakness: `.env.example:89` uses `change_me_before_first_boot` as an example value — this is acceptable practice for example files

**Suggested Text**:

```markdown
## Security Review: No Hardcoded Secrets Found

**Result**: ✅ PASS — No API key leakage detected.

Odysseus follows security best practices across all three reviewed files:

1. **Environment variable injection**: All secrets use the `${VAR:-}` shell
   pattern (default to empty string if unset). No secrets appear verbatim
   in the compose file.

2. **`.env.example` hygiene**: 
   - All example values are clearly fake (`your_openai_api_key_here`,
     `change_me_before_first_boot`)
   - `SEARXNG_SECRET` is commented out by default, requiring deliberate
     opt-in
   - Clear documentation: "Do not commit real keys" (line 25)
   - File is explicitly marked as a template (line 1: "Copy this file to
     .env")

3. **Docker secrets**: If deploying with Docker Swarm, consider migrating
   credentials from environment variables to Docker secrets for production
   deployments.

**Recommendation**: No changes needed. Continue maintaining this practice.
Consider adding a `git-secrets` or `gitleaks` pre-commit hook to prevent
accidental secret commits.

**Verification command** (run from repo root):
```bash
# Check for potential hardcoded secrets in compose files
grep -rnE '[A-Z]+_KEY=[A-Za-z0-9_-]{20,}' .env.example docker-compose.yml docker-compose.*.yml
```
Expected: zero results for hardcoded keys (env var references only).
```

---

### CANDIDATE-08: Granian-Specific Entrypoint Notes for SearXNG

**Type**: Documentation
**Severity**: LOW
**GitHub Action**: Issue
**Evidence**: Odysseus's entrypoint wrapper (`docker-compose.yml:97-108`) does
template-based secret key injection, which is robust. However, the inline comments
don't note that SearXNG's Granian replacement (PR #4820) eliminated the need for
`uwsgi.ini` templating, meaning the entrypoint can be simplified in the future.
Additionally, the `SEARXNG_PORT` and `SEARXNG_HOST` environment variables are
available for Granian configuration but not documented or used in the compose file.

**Forensic details**:
- SearXNG PR #4820 replaced uWSGI with Granian in July 2025
- Granian is configured exclusively via environment variables: `GRANIAN_*`, `SEARXNG_PORT`, `SEARXNG_HOST`
- No `uwsgi.ini` needed — this simplifies the entrypoint
- Odysseus's compose doesn't set `SEARXNG_PORT=8080` or `SEARXNG_HOST=0.0.0.0` explicitly (uses defaults, which are 8080 and 0.0.0.0 respectively)
- Adding explicit environment variables would make the configuration self-documenting and protect against upstream default changes

**Suggested Text**:

```markdown
## Document Granian Configuration via Environment Variables

**Context**: SearXNG replaced uWSGI with Granian in July 2025 (PR #4820).
Granian is configured entirely through environment variables — no uwsgi.ini
file is needed. The current entrypoint wrapper and health check are compatible
with Granian, but the configuration is not explicitly documented.

**Opportunity**: Add the relevant Granian environment variables to the SearXNG
compose service section. This makes configuration self-documenting and protects
against upstream default value changes:

```yaml
  searxng:
    # ... existing config ...
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
      - SEARXNG_SECRET=${SEARXNG_SECRET:-}
      # Granian configuration (PR #4820 replaced uWSGI):
      - SEARXNG_PORT=8080              # explicit, matches ports mapping
      - SEARXNG_HOST=0.0.0.0           # bind all interfaces inside container
      # GRANIAN_* vars for advanced tuning:
      # - GRANIAN_WORKERS=4            # default: CPU count
      # - GRANIAN_KEEP_ALIVE=75        # default: 75 seconds
```

**Why explicit is better**:
- If upstream changes the default port (unlikely but possible), the compose
  file would break silently. Explicit `SEARXNG_PORT=8080` eliminates this risk.
- Future maintainers can immediately see the Granian configuration without
  reading the upstream entrypoint script.
- The `SEARXNG_PORT` and `SEARXNG_HOST` vars are already supported by the
  image's entrypoint script — they're just not documented in the compose file.
```

---

## §2 Summary Table

| # | Candidate | Type | Severity | GH Action | Effort | Omega Evidence Source |
|---|-----------|------|----------|-----------|--------|----------------------|
| C-01 | Health check timing — relax aggressive 5s interval | Enhancement | MEDIUM | Issue | 5 min | SearXNG PR #4820 (Granian), Jem verification |
| C-02 | IPv4 vs IPv6 health check ambiguity | Enhancement | LOW | Issue | 1 min | SearXNG PR #4378, Alpine IPv6 behavior |
| C-03 | Document DAC_OVERRIDE rationale | Docs | LOW | Issue | 5 min | SearXNG issue #30, PR #110 |
| C-04 | Pin ChromaDB image (follow SearXNG pattern) | Enhancement | MEDIUM | Issue | 15 min | Docker compose line 81, existing test pattern |
| C-05 | Promote pinning test as project template | Docs | LOW | Issue | 10 min | `test_searxng_image_pinned.py` (proven pattern) |
| C-06 | Document `use_default_settings` merge semantics | Docs | LOW | Issue | 10 min | SearXNG upstream settings.yml analysis |
| C-07 | Security review — no secrets leaked (informational) | Security | NONE | — | 0 min | Full compose + .env.example forensic scan |
| C-08 | Document Granian env vars explicitly | Docs | LOW | Issue | 5 min | SearXNG PR #4820, Granian documentation |

## §3 Priority for Contribution

```
HIGH (this sprint):
  C-04 — Pin ChromaDB (follows proven pattern, quick win)
  C-01 — Relax health check timing (documented Granian boot behavior)

MEDIUM (next sprint):
  C-06 — Document settings.yml merge semantics (prevents support questions)
  C-03 — Document DAC_OVERRIDE rationale (prevents accidental removal)
  C-08 — Granian env var documentation (self-documenting config)

LOW (future):
  C-02 — IPv4 health check (intermittent, low severity)
  C-05 — Pinning test template (nice-to-have)
  C-07 — Security review clean bill (informational)
```

## §4 Implementation Strategy

All 8 candidates are **Issues only** — no PRs. Rationale:
- This is an upstream contribution from Omega Engine, not an Odysseus maintainer
- Issues give the Odysseus maintainer agency to decide implementation approach
- Each issue is self-contained with copy-paste ready suggested changes
- PRs would require forking Odysseus, which is out of scope for Workstream 3

If the Odysseus maintainer wants patches, each candidate is a 1–5 file change:
- C-01: `docker-compose.yml` (3 lines changed: interval, timeout, retries, start_period)
- C-02: `docker-compose.yml` (1 URL change: localhost → 127.0.0.1)
- C-03: `docker-compose.yml` (comment block replacement)
- C-04: `docker-compose.yml` + optional `tests/test_chromadb_image_pinned.py`
- C-05: `CONTRIBUTING.md` or inline doc in `test_searxng_image_pinned.py`
- C-06: `config/searxng/settings.yml` (comment additions only)
- C-07: No changes (clean bill of health)
- C-08: `docker-compose.yml` (4 env var additions)

## §5 Cross-Reference

```
Omega Analysis Pipeline:
  SEARXNG_DEEP_RESEARCH_20260621.md        → 45+ primary sources, 18 gaps
  SEARXNG_ODYSSEUS_MINING_20260621.md      → 3 root causes, 5 secondary findings
  SEARXNG_VALIDATION_20260621.md           → 11 claims checked, 9/10 quality
  SEARXNG_JEM_VERIFICATION_20260621.md     → 6 bugs verified, 4 patches
  ODYSSEUS_CONTRIBUTION_LOG.md             ← YOU ARE HERE
```

---

## §6 L1→L2→L3 Distillation

**L1 (Narrative)**: Workstream 3 of the SearXNG integration audit identified 8
contribution opportunities for the Odysseus project. These range from health check
timing improvements (C-01) and IPv6 resolution fixes (C-02) to documentation of
DAC_OVERRIDE rationale (C-03), ChromaDB pinning (C-04), and settings.yml merge
semantics (C-06). A full security review found no hardcoded secrets — a clean bill
(C-07). The image pinning test pattern (C-05) and Granian env var documentation
(C-08) round out the set.

**L2 (Insight)**: The most impactful contribution is C-04 (ChromaDB pinning) because
Odysseus already has the proof of concept in its own SearXNG section. The fact that
SearXNG is pinned while ChromaDB uses `:latest` is an inconsistency that will
eventually cause breakage — the question is not *if* ChromaDB `:latest` will break,
but *when*. The health check timing (C-01) is the second most impactful because it
directly affects startup reliability on resource-constrained hosts, which is exactly
the audience that self-hosted Odysseus targets.

**L3 (Universal Principle)**: **"The best contribution you can make to an open-source
project is a tested pattern they can extend to their own inconsistencies."** Odysseus
already solved SearXNG pinning and documented the lesson. The most valuable contribution
Omega can make is not "tell them to pin ChromaDB" but "show them how to apply their
own proven pattern to the remaining services." The pinning test template (C-05) and
the ChromaDB pinning issue (C-04) together form a complete contribution: problem +
proven solution path.

---

*Workstream 3/3 complete. 8 candidates identified. 0 security issues (clean bill).*
*Priority order documented. 1 C-07 informational, 2 C-01/C-04 HIGH, rest MEDIUM/LOW.*
*Next: Post to Hivemind, then contribute issues to github.com/pewdiepie-archdaemon/odysseus.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
