# R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826

**AP Token**: `AP-GROKSTER-AG-20260826`
⬡ OMEGA ⬡ GROKSTER (Antigravity Specialist Session) ⬡ opencode ⬡ trc_antigravity_deep_mine ⬡ WEB-PRIMARY

**Date**: 2026-08-26
**Researcher**: grokster — dedicated Antigravity specialist session (charter §0)
**Method**: Web-primary sources (M23 honesty: every claim sourced; unverified items flagged). No local probes executed this session — probe list in §I.
**House context assumed (not re-litigated)**: plugin internals source-verified at commit 7db338b; Antigravity = priority-3 cloud backend.

---

## §0 SESSION CHARTER — Standing Antigravity Specialist

This document doubles as the specialist handoff page. Future sessions working this file should know:

1. **Scope**: Google Antigravity platform (IDE + CLI + underlying Cloud Code Assist API), the `opencode-antigravity-auth` plugin ecosystem, and direct-API usage outside any harness.
2. **The single most important fact in this file**: direct API access is *technically trivial* (fully reverse-engineered, stable, documented by multiple independent projects) but is an **explicit, named ToS breach with demonstrated mass enforcement** (§G). Any house strategy must price ban risk per-account.
3. **Second most important fact**: the NoeFabris plugin house currently depends on was **archived ~Jun 25, 2026** (§H). House is running a dead upstream. This changes maintenance posture regardless of the ToS question.
4. **Verification status legend**: ✅ = verified against primary source / multiple independent sources · ⚠️ = single-source or partially verified · ❓ = unverified claim, treat as hypothesis.
5. **Do not trust**: any claim about quota numbers without a date stamp — Google has changed limit structures at least three times in 2026 (§D).

---

## §A ENDPOINT ANATOMY

✅ **The plugin ecosystem ultimately hits the Cloud Code Assist "Unified Gateway" API — NOT generativelanguage.googleapis.com and NOT Vertex AI directly.**

### A.1 Base URLs

| Environment | URL | Status |
|---|---|---|
| **Production** | `https://cloudcode-pa.googleapis.com` | ✅ Active |
| Daily (sandbox) | `https://daily-cloudcode-pa.sandbox.googleapis.com` | ✅ Active |
| Autopush | `https://autopush-cloudcode-pa.sandbox.googleapis.com` | ❌ Unavailable (per NoeFabris spec Dec 2025) |

⚠️ One community plugin (asifrpatel fork) implements endpoint fallback across daily → autopush → prod for reliability.

### A.2 Actions (all POST, all under `/v1internal`)

| Action | Path | Purpose |
|---|---|---|
| Load Code Assist | `/v1internal:loadCodeAssist` | Project discovery, tier/plan info, onboarding state |
| Onboard User | `/v1internal:onboardUser` | First-run provisioning |
| Fetch Available Models | `/v1internal:fetchAvailableModels` | Model list + `remainingFraction` quota + reset times |
| Generate Content | `/v1internal:generateContent` | Non-streaming completion |
| Stream Generate | `/v1internal:streamGenerateContent?alt=sse` | SSE streaming completion |

Secondary surface for the "Gemini CLI" fallback pool: `https://cloudaicompanion.googleapis.com` ("Gemini for Google Cloud API") — requires the account to have a real GCP project with that API enabled (`cloudaicompanion.companions.generateChat` permission). The Antigravity pool works with Google's internal default project (`rising-fact-p41fc` family); the Gemini-CLI pool needs your own projectId.

### A.3 Request envelope (Gemini-style, mandatory)

```json
{
  "project": "<project_id>",
  "model": "claude-sonnet-4-6",
  "request": {
    "contents": [ { "role": "user", "parts": [{"text": "..."}] } ],
    "systemInstruction": { "parts": [{"text": "..."}] },
    "generationConfig": {
      "maxOutputTokens": 1000,
      "temperature": 0.7,
      "thinkingConfig": { "thinkingBudget": 8000, "includeThoughts": true }
    },
    "tools": [ { "functionDeclarations": [...] } ]
  },
  "requestType": "agent",
  "userAgent": "antigravity",
  "requestId": "agent-<timestamp>-<random>"
}
```

Hard quirks (✅ from NoeFabris ANTIGRAVITY_API_SPEC.md, "Verified by Direct API Testing", Dec 13 2025):
- Roles are `user`/`model` only — Anthropic-style `messages` array is rejected.
- `systemInstruction` MUST be `{parts:[...]}` object; plain string → 400.
- JSON Schema: no `const`, `$ref`, `$defs`, `$schema`, `$id`, `default`, `examples` (400s) — plugins transform these client-side.
- Tool names: no `/`, no leading digit; max 64 chars; `_ . : -` allowed.
- `googleSearch`/`urlContext` tools CANNOT combine with `functionDeclarations` in one request (hence plugin's separate search call).
- Thinking: `maxOutputTokens` must be > `thinkingBudget`.
- Claude thinking parts come back as `{thought: true, text, thoughtSignature}` inside Gemini-format candidates.

### A.4 Response envelope

SSE frames wrap standard Gemini response: `{"response": {candidates:[...], usageMetadata:{...}, modelVersion, responseId}, "traceId": "..."}`. Claude `responseId`s look like `msg_vrtx_...` (confirming Vertex routing behind the gateway); Gemini/GPT-OSS use base64-like IDs. Debug header: `x-cloudaicompanion-trace-id`.

### A.5 Direct-call verdict anatomy

Nothing in the protocol requires OpenCode, the plugin, or any specific client. Auth is a plain OAuth Bearer token + spoofable client headers:

```
Authorization: Bearer <access_token>
Content-Type: application/json
User-Agent: antigravity/1.15.8 windows/amd64        ← client impersonation string
X-Goog-Api-Client: google-cloud-sdk vscode_cloudshellededitor/0.1
Client-Metadata: {"ideType":"ANTIGRAVITY","platform":"MACOS","pluginType":"GEMINI"}
```

⚠️ The degree to which Google fingerprints these headers vs. actual TLS/client behavior is unknown (see §I).

---

## §B OAUTH FLOW & POOL MANAGEMENT

### B.1 Flow anatomy ✅

- **OAuth 2.0 + PKCE (S256)**, `access_type=offline`, `prompt=consent`.
- Authorization: `https://accounts.google.com/o/oauth2/v2/auth`; Token exchange: `https://oauth2.googleapis.com/token`.
- Local callback listener on **port 51121** (plugin default; some forks use 36742); manual URL-paste fallback after 30s for headless/containers.
- **Scopes requested**: `cloud-platform`, `userinfo.email`, `userinfo.profile`, `cclog`, `experimentsandconfigs`. Note breadth: `cloud-platform` is a master scope — these refresh tokens are powerful. Treat `antigravity-accounts.json` as a credential vault (house already does).
- After token exchange: email fetched via `oauth2/v1/userinfo`; projectId via `loadCodeAssist` with `Client-Metadata` headers.
- Access-token lifetime: standard Google ~1h ❓(not explicitly documented in sources); plugins refresh proactively with ~5-min expiry buffer (PicoClaw pattern).
- Refresh tokens persist indefinitely unless revoked (`invalid_grant` on password change/security event) — plugins auto-prune revoked accounts.

### B.2 Pool management mechanics ✅ (from NoeFabris MULTI-ACCOUNT.md)

- Storage: `~/.config/opencode/antigravity-accounts.json` v3 schema — accounts[] with `email`, `refreshToken`, optional `projectId`, `enabled`; plus `activeIndex` and `activeIndexByFamily: {claude, gemini}` (per-model-family rotation cursors).
- Strategies (in `antigravity.json`): `sticky` (until rate-limited; preserves Anthropic prompt cache), `round-robin`, `hybrid` (health score + token bucket + LRU).
- Short 429s (≤5s retryDelay) retried on same account; longer ones trigger rotation; exponential backoff on consecutive limits.
- Parallel-process collision: PID-offset mode (`pid_offset_enabled`) distributes processes across accounts.
- **Dual quota pools**: Gemini requests try Antigravity pool first, fall back to Gemini-CLI pool (same account) when all accounts' Antigravity quotas exhaust — model names auto-transformed (e.g., `gemini-3-flash` → `gemini-3-flash-preview`). Effectively ~2× Gemini quota.
- Quota inspection without harness: `fetchAvailableModels` returns per-model `remainingFraction` + `resetTime`. NoeFabris ships standalone `scripts/check-quota.mjs`.

### B.3 Pool conflict findings ⚠️

- CLIProxyAPI issue #1015 (Jan 2026): 17 accounts ALL 429 while `fetchAvailableModels` shows 100% remaining → evidence of a **second, hidden rate-limit layer** (per-minute/per-hour and/or abuse-detection throttling) not reflected in the quota API. VPN/IP change did NOT clear it → account-level flagging suspected.
- Mirrowel proxy issue #54: two accounts rate-limit **simultaneously** → possible IP-based limiting component or org/project coupling. Conflicting evidence with #1015 (account-based). Likely BOTH layers exist: short-window per-IP + long-window per-account.

---

## §C ANTIGRAVITY CLI REFERENCE (`agy`)

✅ Primary sources: developers.googleblog.com transition post (May 19, 2026), antigravity.google/docs/cli/*, github.com/google-antigravity/antigravity-cli.

- **What it is**: Google's official terminal coding agent, binary `agy`, **written in Go**, single compiled binary (no Node runtime — unlike gemini-cli). Launched at I/O 2026 (May 19); shares the agent harness with Antigravity 2.0 desktop IDE.
- **Succession**: Gemini CLI + Gemini Code Assist IDE extensions stopped serving free/Pro/Ultra tiers **June 18, 2026**. Enterprise Code Assist Standard/Enterprise retains old CLI. Confirms house inline context exactly.
- **Install**: `curl -fsSL https://antigravity.google/cli/install.sh | bash` (macOS/Linux); PowerShell installer on Windows. Repo: `github.com/google-antigravity/antigravity-cli` (public as of Jul 14, 2026).
- **Headless/print mode** (relevant to house automation): `agy -p "prompt"` runs once, streams to stdout, diagnostics to stderr, exit code 0/non-zero. `--output-format text|json|stream-json`. Unknown `--model` fails loudly (no silent fallback). Uses cached credentials — auth once interactively first; unauthenticated CI runs exit with `authentication required`.
- **Model/effort control**: `agy models` lists slugs; `--model <slug>`, `--effort low|medium|high`, `--agent <name>`; multi-agent by default (session dispatches its own subagents); background tasks supported.
- **Permissions**: headless soft-denies Ask-mode tools unless allowed via `~/.gemini/antigravity-cli/settings.json` `permissions.allow` rules (e.g. `"command(git)"`), or `--dangerously-skip-permissions`.
- **Config migration**: reuses `~/.gemini` home; reads `~/.gemini/GEMINI.md`; first-run import of MCP servers/allowed commands/keybindings. Not a fork of the TS gemini-cli codebase — it's a new Go codebase with config compatibility (❓ exact lineage; "Go-based" per multiple secondary sources, consistent with single-binary claims).
- **Does it expose raw API access?** No public HTTP/API mode documented — headless mode is process-level (stdout/json), not an HTTP endpoint. For API-shaped access, community uses CLIProxyAPI-style bridges instead (§F). ⚠️ Whether `agy` hits the SAME `cloudcode-pa` endpoints with the same quotas is UNVERIFIED — plausible but unprobed (§I).

---

## §D QUOTAS & RATE LIMITS

⚠️ All numbers below are time-sensitive; structure changed repeatedly through 2026.

- **Free tier**: exists, no card required, described as "generous" during preview but community consensus (antigravitylab.net, Jun 2026): "a handful of consecutive agent requests can end the day's allowance." Limits correlate with *agent work done*, not prompt count (official plans doc: limits "correlated with the amount of work done by the agent").
- **Reset cadence**: quota checks show daily resets (~24h) for Pro-tier and weekly (7-day) windows reported for free tier ⚠️. Reset times come back per-model-family from `fetchAvailableModels` (e.g. `resetTime` fields ~5h out in one Jan 2026 capture).
- **Two-layer limiting** (high confidence, §B.3): visible daily/weekly quota via `fetchAvailableModels` + hidden short-window rate/abuse throttle that can 429 you while quota reads 100%.
- **Legacy reference point**: pre-sunset Gemini CLI free tier was 60 req/min, 1000 req/day (netcomlearning retrospective). Do NOT assume these carry into Antigravity pools.
- **Pooling strategies observed in the wild**: 6–17+ account pools via CLIProxyAPI (§F); profile-switcher extensions for the IDE (m4stanuj/antigravity-account-switcher, 5 slots); dual-pool exploitation (Antigravity + Gemini-CLI pools per account ≈ 2× Gemini).
- **Detection signals** (from enforcement reports, §G): third-party client usage itself, "third-party chaining"/automation of prompts, high request volume, many accounts per user. IP rotation did NOT evade account-level flags (#1015).

---

## §E MODEL CATALOG UPSTREAM

✅ Verified server-side IDs (NoeFabris API spec, direct testing Dec 2025):
`claude-sonnet-4-6` · `claude-opus-4-6-thinking` · `gemini-3-pro-high` · `gemini-3-pro-low` · `gpt-oss-120b-medium`

✅ `agy models` output (mid-2026 docs) shows newer slugs:
`gemini-3.7-flash-high/medium` · `gemini-3.6-flash-high/medium` · `gemini-3.5-flash-medium` · `gemini-3.1-pro-high` · `claude-sonnet-4-6` (Thinking) … (~8 models total incl. GPT-OSS 120B and Claude Opus 4.6 per CodeAgentSwarm)

Beyond house presets (house knows: gemini-3-pro/3.1-pro/3-flash, claude-opus-4-6-thinking, claude-sonnet-4-6 custom SKU):
1. **`gpt-oss-120b-medium`** — OpenAI open-weights model served through the same gateway. House presets likely don't expose it. Free Claude-competitor tier.
2. **Gemini 3.5/3.6/3.7 flash generations** with `-high/-medium` effort suffixes baked into slugs (vs. house's thinkingBudget approach for Claude).
3. **Sonnet 4.6 ships as "(Thinking)" natively in agy catalog** — corroborates house finding that Sonnet thinking works via custom SKU despite preset omission (upstream issue #495).
4. ❓ Whether `*-thinking` Opus variants beyond opus-4-6 exist server-side — unprobed.

---

## §F DIRECT-USAGE PATTERNS (OUTSIDE HARNESS)

Direct calling is a solved problem in the community. Viable patterns, ranked by house relevance:

### F.1 Thin direct calls (curl / anyio httpx)
Fully specified by §A. Minimal viable flow: OAuth PKCE dance once → store refresh token → refresh → `loadCodeAssist` for project → `streamGenerateContent?alt=sse`. PicoClaw's provider guide documents the entire implementation contract including thinking-signature sanitization regex (`^[A-Za-z0-9+/]+={0,2}$`). Effort estimate for an Omega native-gguf-style backend module: **1–2 days**.

### F.2 CLIProxyAPI (router-for-me) — the ecosystem hub ✅
Wraps Antigravity (+ Codex, Claude Code, Grok Build) OAuth logins into local OpenAI/Gemini/Claude-compatible API endpoints. Massive satellite ecosystem (Quotio, ProxyPal, CPA-Manager-Plus, tunnel-agent…) doing pool management, quota dashboards, per-account health. This IS the "OAuth-to-API bridge" pattern at maturity. If house ever wants harness-free access WITHOUT writing a backend, running CLIProxyAPI as a local sidecar and pointing the Omega provider fabric at it is the lowest-effort path — but see §G: it is also the most-banned pattern (it's the tool the ban waves targeted).

### F.3 Purpose-built proxies
Mirrowel/LLM-API-Key-Proxy (Python rotator with cooldown manager), elad12390/antigravity-proxy, badrisnarayanan/antigravity-claude-proxy, lbjlaq/Antigravity-Manager. Multiple independent implementations confirm protocol stability.

### F.4 Risks of direct patterns
- Client fingerprinting (headers alone may not suffice long-term).
- Hidden throttle layer punishes volume regardless of client (§B.3).
- Prompt-cache locality lost if rotating accounts aggressively (why sticky strategy exists).
- ToS exposure identical whether you roll your own or use a plugin — the *terms* name third-party access, not a specific tool (§G).

---

## §G ToS RISK ASSESSMENT — 🔴 SEVERE, EXPLICIT, ENFORCED

This section should change house posture. All ✅ primary-sourced.

### G.1 The terms say it plainly
Google Antigravity Additional Terms of Service (antigravity.google/terms), §6:

> "This includes, but is not limited to, using the Service in connection with products not provided by us. **Using third party software, tools, or services to access the Service (e.g. using OpenClaw with Antigravity OAuth) is a breach of this Agreement. Such actions may be grounds for suspension or termination of your account.**"

This is not ambiguity to be exploited — third-party-client access is named as breach per se. Every OpenCode-plugin session, and any direct API call we make, falls under it.

### G.2 Enforcement is real and was mass-scale
- **Feb–Mar 2026 ban waves**: CLIProxyAPI discussion #1558 — user reports 5 of 6 pooled accounts banned; multiple "same here" replies. Issue #1823 — canonical ban error: HTTP 403, `reason: TOS_VIOLATION`, `domain: cloudcode-pa.googleapis.com`, with official appeal form (`forms.gle/hGzM9MEUv2azZsrb9`). Ban hits Antigravity + Gemini CLI + Code Assist simultaneously on the account.
- **Paid tiers not spared**: forum thread "Paid Pro Subscriber Banned Instantly for Testing Opencode OAuth" (1.4k views, May 2026); multiple appeal threads Mar–Apr 2026 including users who used the plugin "unknowingly."
- **One appeal post references a Google "system-wide automated unban for affected accounts"** ⚠️ (single-source; suggests Google oscillates between enforcement and amnesty — possibly wave-based).
- Forum guidance (discuss.ai.google.dev): third-party "chaining"/automation triggers abuse filters → often immediate **7-day lockout**, distinct from permanent TOS_VIOLATION disable.

### G.3 Risk model for house
| Activity | Detection risk | Blast radius |
|---|---|---|
| Plugin use, 1–2 accounts, human-cadence | Moderate (waves caught "unknowing" users) | Account loss (incl. paid plans, Gmail-adjacent services ❓) |
| Multi-account pool, automation cadence | High (this is what waves targeted) | Whole pool + possible link-graph escalation |
| Direct API, careful cadence, few accounts | Same as plugin (terms are client-agnostic) | Same |

**Honest verdict**: there is no compliant configuration for non-official-client use. Mitigation is containment, not compliance: dedicated burner accounts never holding paid plans or irreplaceable data; expect and budget for periodic pool attrition; never let Antigravity become load-bearing for anything that cannot survive a total pool loss overnight. House's local-first mandate (M7) is the real protection — Antigravity stays a burst/fallback cloud tier, never primary capacity.

---

## §H PLUGIN ECOSYSTEM WATCH

- **NoeFabris/opencode-antigravity-auth**: 11,004 stars, 92 forks, 43 open issues — **ARCHIVED (read-only) as of last push 2026-06-25**. Last release v1.6.5-beta.0 (Feb 23, 2026). ✅ GitHub API, checked 2026-08-26. Plausible motive given §G enforcement climate (unconfirmed — repo has no archived-at rationale captured here).
- **House implication**: house runs a local checkout @7db338b wired as file: dependency — functionally insulated from npm disappearance, but ZERO upstream fixes incoming (new model slugs, quota-API changes, header changes will all require house-side patches now).
- **Live alternatives** (activity levels vary; verify before adopting): shekohex/opencode-google-antigravity-auth (374★, 148 commits, active fork lineage), vibheksoni/opencode-antigravity-auth (TUI split architecture), asifrpatel fork (endpoint-fallback variant), theblazehen/opencode-antigravity-multi-auth. DeepWiki coverage exists for several (shekohex constants.ts confirms same CODE_ASSIST_ENDPOINT set).
- **Ecosystem-wide note**: the whole category is legally exposed per §G; expect continued churn/archivals. Long-term, house should assume plugin-supplied Antigravity access is a depreciating asset.

---

## §I RESEARCH TARGETS REMAINING (LOCAL PROBES)

Ranked. All require Architect sign-off given §G risk — do NOT run pool-wide experiments on house accounts.

1. **Header sensitivity probe** (lowest risk, highest value): replay a captured request with mutated `User-Agent`/`Client-Metadata` on ONE burner account; observe 403/429/200. Answers whether fingerprinting is header-deep.
2. **agy endpoint capture**: run `agy -p` under mitmproxy/strace-equivalent; confirm whether Antigravity CLI hits `cloudcode-pa` with same scopes/quotas. If yes, `agy` headless becomes a sanctioned-ish channel worth prioritizing over plugin.
3. **Token lifetime measurement**: timestamp access-token issuance vs. 401 to pin exact TTL (assumed ~1h).
4. **Local artifact audit**: diff house `antigravity-accounts.json` v3 schema vs. documented schema; verify `zen_accounts_state.json` role; inventory `~/.config/opencode/antigravity.json` keys against CONFIGURATION.md.
5. **Quota ground-truth**: run NoeFabris `check-quota.mjs` equivalent against house accounts; log `remainingFraction`/`resetTime` daily for a week to empirically map the hidden throttle layer (§B.3/D).
6. **gpt-oss-120b-medium smoke test**: single direct call on burner account; verify availability + quality for house mining tasks.
7. **Archive forensics**: fetch NoeFabris repo README/archive banner + final issues for official shutdown rationale and any recommended successor.
8. **Appeal-form intel**: monitor forum/GitHub for whether the "automated unban" recurred — informs pool-replacement economics.

---

## §J SOURCE INDEX

Primary:
- antigravity.google/terms — ToS §6 third-party-access clause (retrieved 2026-08-26)
- github.com/NoeFabris/opencode-antigravity-auth — README, docs/ANTIGRAVITY_API_SPEC.md (v1.0, 2025-12-13, "Verified by Direct API Testing"), docs/MULTI-ACCOUNT.md, docs/TROUBLESHOOTING.md; repo metadata via GitHub API 2026-08-26 (archived:true)
- developers.googleblog.com "Transitioning Gemini CLI to Antigravity CLI" (2026-05-19)
- antigravity.google/docs/cli/headless + /getting-started + /plans (official docs)
- github.com/google-antigravity/antigravity-cli (public repo, 2026-07-14)
- docs.picoclaw.io/docs/providers/antigravity/ — full independent implementation contract (scopes, endpoints, envelope, sanitization)
- router-for-me/CLIProxyAPI — README (ecosystem hub), issue #1015 (hidden throttle), issue #1823 + discussion #1884 (TOS_VIOLATION ban error + appeal form), discussion #1558 (pool ban wave)
- discuss.ai.google.dev threads #130898 (ban appeal, automated-unban mention), #175537 (multi-account ToS question), #130212 (quota limits, chaining lockouts)
- Mirrowel/LLM-API-Key-Proxy issue #54 (simultaneous 429s / IP-limit evidence)
- m4stanuj/antigravity-account-switcher (IDE profile pooling)
- Secondary/contextual: computingforgeeks.com install guide (2026-06-15), codeagentswarm.com agy guide (2026-06-29), netcomlearning gemini-cli retrospective (2026-07-06), antigravitylab.net pricing analysis (2026-06-12), deepwiki.com mirrors (shekohex, theblazehen, elad12390), lobehub skill listing (auth-store bootstrap quirk)

Unverified/hypothesis items flagged inline: ❓ access-token TTL, ❓ agy↔cloudcode-pa endpoint identity, ❓ automated-unban recurrence, ⚠️ free-tier weekly window specifics, ⚠️ fingerprinting depth.

---

*⬡ OMEGA ⬡ GROKSTER-AG-SPECIALIST ⬡ R_ANTIGRAVITY_DIRECT_API_DEEP_MINE ⬡ 2026-08-26*
