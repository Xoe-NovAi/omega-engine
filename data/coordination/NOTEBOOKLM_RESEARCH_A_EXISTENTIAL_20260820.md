<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# NOTEBOOKLM RESEARCH A — EXISTENTIAL GAPS (GAP-3, GAP-4, GAP-1, GAP-2)

**Subagent**: Researcher (NLG-A) · dispatched by Kali (Transcendent Oversoul)
**Date**: 2026-08-20
**Scope**: Close 4 existential gaps in the Omega Engine NotebookLM strategy
**Workspace lock**: `notebooklm-research` (held by Kali)
**Tools used**: `parallel-search_web_search`, `websearch`, `webfetch` (exa/google_search confirmed BROKEN — not used)

---

## 1. EXISTENTIAL VERDICT — Deep Research Automation

**VERDICT: GO (conditional).** The automation premise **survives**. At least two libraries can programmatically trigger NotebookLM **Deep Research** and export the resulting report. The strategy does **NOT** revert to manual mode.

### Evidence (documented Deep Research trigger + report export)

| Library | Deep Research trigger | Report export | Runtime | Source |
|---|---|---|---|---|
| **notebooklm-py** (teng-lin) | `notebooklm source add-research "topic" --mode deep` — documented as "Run Deep Research" | Reports downloadable as **Markdown** (`download <type>` / `download <type> --all`); "reports as Markdown" listed among export formats | RPC (undocumented Google APIs); browser extra optional | https://pypi.org/project/notebooklm-py · https://github.com/teng-lin/notebooklm-py |
| **notebooklm-go** (LocalKinAI) | `Research: Start Deep` (marked 🟢 stable) | "trigger … Deep Research, and download generated artifacts. No browser automation" | Direct HTTPS to `batchexecute` RPC, no Selenium | https://pkg.go.dev/github.com/LocalKinAI/notebooklm-go |

### Critical caveat — `research_start` is NOT the Deep Research report

The `notebooklm-mcp` (TheSethRose/PleasePrompto) `research_start` tool with `mode: fast|deep` performs **web/Drive source discovery & import** ("Search web or Google Drive to FIND NEW sources"), **not** the quota-consuming Deep Research **report** generation. The monthly "Deep Research" quota (10/month free) is the report feature. Do **not** assume `research_start --mode deep` consumes that quota or yields an exportable report.

- `research_start` behavior (source-finding): https://glama.ai/mcp/servers/ran-ai-agency/Notebooklm-mcp/tools/research_start
- TheSethRose repo (Patchright/browser-driven): https://github.com/PleasePrompto/notebooklm-mcp · https://www.npmjs.com/package/notebooklm-mcp

**Conclusion**: Automation is feasible **only** via libraries that explicitly trigger the Deep Research report + export it (notebooklm-py, notebooklm-go). The MCP servers built on browser automation (TheSethRose) do not clearly provide this in their `research_start` surface.

---

## 2. ToS RISK ASSESSMENT — 8-Account Fleet

**VERDICT: CONDITIONAL GO / HIGH RISK.** An 8-account fleet is **not explicitly prohibited per se**, but Google's abuse detection actively targets (a) bot-created/linked accounts and (b) multi-account correlation by IP/fingerprint/behavior. The fleet is viable **only** with the documented safe-pattern mitigations below. Without them → NO-GO.

### (a) Explicit ToS prohibition
Google ToS prohibits accounts "created or used with multiple other accounts to violate Google's policies" and accounts "created by a computer program or bot." Disabling/termination is authorized for "spamming, misleading others, or scraping."
- https://policies.google.com/terms

### (b) Real ban reports (not theoretical)
- **notebooklm-py issue #228**: A manually-created, 8-month-old account was **disabled after a single NotebookLM request**. Google message: *"created or used with multiple other accounts to violate Google's policies … created by a computer program or bot."* Account **restored on appeal, but the warning flag remains**. Maintainer traced root cause to **Python's default TLS fingerprint (`python-httpx` UA)** being trivially distinguishable from real Chrome traffic → correlation across thousands of accounts using the library. Hardening (JA3/JA4 browser-identical fingerprints) was pending as of the issue.
  - https://github.com/teng-lin/notebooklm-py/issues/228
- **IP-level lockout**: A user reported **all 5 accounts simultaneously locked for 167 hours** from the same IP — Google applies a **shared IP-level rate-limit/abuse lockout**, not per-account. Multi-account from one IP is the "single loudest signal."
  - https://discuss.ai.google.dev/t/bug-google-ai-pro-all-5-accounts-simultaneously-locked-for-167-hours-ip-level-rate-limit-session-bleed/129724
- Google AI Pro free-promo abuse via "multiple burner accounts with fake IDs" is actively enforced.
  - https://discuss.ai.google.dev/t/thank-you-to-the-google-for-the-tos-enforcement-and-a-reality-check-for-the-abusers/127137

### (c) Safe automation patterns (documented)
Bans correlate accounts when they share **IP**, **browser fingerprint**, or **behavioral pattern**. Mitigations:
1. **One dedicated static ISP IP per account** — never shared/rotating VPN/datacenter IPs.
2. **Isolated browser profile per account** (antidetect / separate Chrome user-data-dir); never reuse one profile across accounts.
3. **Staggered, human-like, non-synchronized scheduling** — vary timing across hours/days; warm up new accounts gradually; no robotic fixed-interval loops.
4. **Exponential backoff with jitter** on 429/5xx; honor `Retry-After`; cap retries; never silent-drop (aligns with Omega M23).
5. **Browser-identical TLS/HTTP2 fingerprints** where RPC libraries are used (the notebooklm-py #228 lesson).

- Multi-account ban mechanics: https://hellworld.io/blog/multiple-accounts-without-bans-2026
- Backoff w/ jitter standard: https://fast.io/resources/ai-agent-retry-patterns/ · https://www.getknit.dev/blog/10-best-practices-for-api-rate-limiting-and-throttling

**Net**: 8 accounts × 10 Deep Research/month = 80/month is arithmetically valid, but only survivable with dedicated-IP + isolated-profile + staggered-backoff discipline. The strategy must bake these into the deployment plan or the fleet will be banned.

---

## 3. MCP SERVER RECOMMENDATION

### Tool-surface comparison (3 candidates)

| Criterion | **notebooklm-py** (teng-lin) | **notebooklm-mcp-cli** (jacob-bd) | **notebooklm-mcp** (TheSethRose/PleasePrompto) |
|---|---|---|---|
| Deep Research **report** trigger | ✅ `source add-research --mode deep` | ⚠️ `research_start` = source-finding (deep mode imports sources, ambiguous re: report quota) | ⚠️ `research_start` = source-finding (not report) |
| Report **export** (Markdown) | ✅ native `download` | ✅ `download_artifact` / `download all` | ⚠️ `report_create` exists but report-retrieval path unclear |
| Notebook CRUD | ✅ | ✅ | ✅ |
| Source add (URL/text/Drive/file) | ✅ | ✅ (broadest) | ✅ |
| Tool count | Moderate (library + MCP extra) | **43 MCP tools** (richest) | ~31 tools |
| Runtime model | **RPC (no browser at runtime)**; browser extra optional | Browser/CDP cookie extraction | **Real Chrome via Patchright** (browser automation) |
| Auth | Google session/cookie (RPC) | Browser cookie extraction (multi-browser CDP) | Patchright stealth + persistent fingerprint |
| Deployment | pip/uv + systemd (Docker via wrapper) | pip/uv + systemd; `.mcpb` one-click | npx/npm; Docker via forks |

Sources:
- notebooklm-py: https://pypi.org/project/notebooklm-py · https://github.com/teng-lin/notebooklm-py
- notebooklm-mcp-cli: https://pypi.org/project/notebooklm-mcp-cli · https://github.com/jacob-bd/gemini-notebook-mcp-cli
- notebooklm-mcp (TheSethRose): https://github.com/PleasePrompto/notebooklm-mcp · https://www.npmjs.com/package/notebooklm-mcp

### RECOMMENDATION: **notebooklm-py** (with `[mcp]` extra)

**Rationale**:
1. It is the **only candidate with unambiguous, documented Deep Research report triggering + Markdown export** — the existential requirement (GAP-4 gate). The other two expose `research_start` as *source-finding*, which does not satisfy the Deep Research quota/report premise.
2. **RPC-based, no browser at runtime** → lightest, most suitable for a headless local-first engine (Omega M7) under systemd. The khengyun/notebooklm-mcp wrapper is explicitly "Driven by an RPC backend (notebooklm-py), so there's no browser at runtime" and ships a Dockerfile/docker-compose if containerization is desired.
   - https://glama.ai/mcp/servers/@khengyun/notebooklm-mcp
3. Full pipeline coverage: notebook mgmt + source add + research (deep) + report export — exactly the four capabilities the strategy needs.

**Fallback / complement**: If richer studio tooling (43 tools: batch, cross-notebook query, pipelines, slides revise) is later required, add **notebooklm-mcp-cli** (jacob-bd) as a secondary, but note it is browser/cookie-based and its `research_start` deep mode is source-import, not the report quota.

---

## 4. DEPLOYMENT PATTERN

**RECOMMENDED PATTERN for Omega Engine: `pip install notebooklm-py[mcp]` + systemd unit (no Docker required).** Docker is *optional* (available via the khengyun RPC wrapper), but the sovereign, local-first, portable pattern is a venv + systemd service.

### Evidence
- **notebooklm-py** installs via `uv tool` / `pipx` / `pip` and runs locally via stdio MCP or self-hosted HTTP connector — no container needed.
  - https://pypi.org/project/notebooklm-py
- **khengyun/notebooklm-mcp** (RPC wrapper over notebooklm-py) provides `Dockerfile` + `docker-compose.yml` **and** stdio/HTTP transports — confirms Docker *is* possible but not mandatory; "no browser at runtime."
  - https://glama.ai/mcp/servers/@khengyun/notebooklm-mcp
- **Docker exists for browser-driven forks** (roomi-fields: full Docker + noVNC for Google auth, ports 3000/6080) — relevant only if a Patchright/browser MCP is chosen.
  - https://roomi-fields.github.io/notebooklm-mcp/DOCKER
- **notebooklm-mcp-cli** deploys via `uv tool install notebooklm-mcp-cli` / `pip install` + `nlm setup add <client>` (no Docker in primary path).
  - https://pypi.org/project/notebooklm-mcp-cli

### Concrete deployment sketch (per account)
```
# venv (M24 venv sovereignty)
source .venv/bin/activate && pip install "notebooklm-py[mcp]"

# Per-account isolated auth profile (mitigates ToS ban risk, GAP-3)
notebooklm profile create acct1 --auth <isolated-session>
export NOTEBOOKLM_PROFILE=acct1   # separate HOME/data dir per account

# systemd unit runs the MCP server (stdio) or REST server (guarded HTTP)
notebooklm mcp --transport stdio     # or: notebooklm server --http --host 127.0.0.1
```
- Each of the 8 accounts → **own venv profile + own isolated auth/session + own dedicated IP** (from GAP-3 safe patterns) + **exponential backoff with jitter** in the calling orchestrator.
- No Docker needed; if containerization is preferred for isolation, use the khengyun RPC wrapper image (browserless).

---

## SUMMARY FOR KALI
- **GAP-4 (Existential)**: GO — Deep Research automation is real via `notebooklm-py` (`source add-research --mode deep` + Markdown export) and `notebooklm-go`. Strategy stays automated.
- **GAP-3 (ToS)**: CONDITIONAL GO / HIGH RISK — explicit bot-account ToS prohibition + real ban reports (issue #228, IP-level 5-account lockout). Survives only with dedicated-IP + isolated-profile + staggered-backoff.
- **GAP-1 (Tool surface)**: Recommend **notebooklm-py** (only one with documented Deep Research report trigger + export; RPC/browserless).
- **GAP-2 (Deployment)**: `pip install notebooklm-py[mcp]` + systemd (Docker optional via khengyun wrapper).

*All claims cited inline. No parametric synthesis — every factual claim traces to a fetched URL.*
