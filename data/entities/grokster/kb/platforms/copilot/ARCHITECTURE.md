# GitHub Copilot — Architecture (Auth Chain & API Anatomy)

**KB Entry**: grokster/platforms/copilot/ARCHITECTURE
**last_verified**: 2026-08-26 · **rot_class**: slow (wire protocol stable; endpoint list medium)
**Scope**: Wire-level anatomy of Copilot authentication and model-API access, reconstructed from four independent implementations (pi/earendil-works TS, LobsterAI TS, oxo-call Rust, agent-zero Python) + OpenCode plugin source. CONFIDENCE: HIGH throughout unless tagged.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md §B/§H; pi `packages/ai/src/auth/oauth/github-copilot.ts`; opencode issues #20759/#3936; messense/copilot-api-proxy README.

---

## §1 Client ID Registry (memorize)

| Client ID | App type | Token | Notes |
|---|---|---|---|
| `Iv1.b507a08c87ecfe98` | VS Code Copilot **GitHub App** | `ghu_` | Accepted by token exchange; broadest server-side model allowlist; every working third-party tool uses it |
| `Ov23li8tweQw6odWQebz` | OpenCode's own OAuth App | `gho_` | 404 on `/copilot_internal/v2/token` on some paths; narrower allowlist |
| `Ov23ctDVkRmgkPke0Mmm` | Copilot CLI OAuth App | `gho_` | Works on ghe.com device flow |
| `01ab8ac9400c4e429b23` | VS Code OAuth App | `gho_` | Used by community plugins; maintainer sentiment: "not allowed" |

**Server-side model allowlists are keyed to CLIENT ID** (opencode #20759) — this is the root cause of most "model not supported" failures and the reason identity-header impersonation exists.

## §2 The Canonical Auth Chain

```
Step 1 — OAuth Device Flow (RFC 8628)
  POST https://github.com/login/device/code          client_id=<above>, scope=read:user
  POST https://github.com/login/oauth/access_token   poll (authorization_pending | slow_down)
  → GitHub user token (gho_ or ghu_)
  GHE variant: same paths against https://<slug>.ghe.com

Step 2 — Token Exchange  ← THE CRITICAL GATE
  GET https://api.github.com/copilot_internal/v2/token
      Authorization: token <ghu_/gho_>        ← "token" prefix, NOT "Bearer"
      Editor-Version: vscode/1.96.2
      Editor-Plugin-Version: copilot-chat/0.26.7
      User-Agent: GitHubCopilotChat/<ver>
  → { token: "tid=...;exp=...;sku=...;proxy-ep=proxy.individual.githubcopilot.com;...",
      expires_at, refresh_in, endpoints: { api } }
  ghu_ accepted reliably; gho_ acceptance varies by issuing app (#20759: OpenCode app → 404 ON EXCHANGE ATTEMPT — but house ground truth 2026-08-26: the builtin flow stores the raw gho_ token with expires:0 and OpenCode PASSES IT THROUGH unchanged for individual plans (default endpoint, no identity headers), bypassing exchange entirely per PR #20758 behavior)
  SDK-documented supported refresh types: gho_, ghu_, github_pat_ (github_pat_ for SDK flows;
  ghp_ classic PATs NOT supported)

Step 3 — Model API Calls
  Base URL derived from token field proxy-ep=proxy.X → https://api.X
    individual → https://api.individual.githubcopilot.com
    business   → https://api.business.githubcopilot.com  (also in endpoints.api)
    GHE        → https://copilot-api.<slug>.ghe.com
  Auth: Authorization: Bearer <short-lived copilot bearer>   (~30 min TTL; refresh T-5min/T-2min)
  Required headers for ghu_ flows: Editor-Version, Editor-Plugin-Version,
    Copilot-Integration-Id: vscode-chat, matching User-Agent
```

## §3 Token Self-Description

The exchanged bearer is a semicolon-delimited KV string — a client routes itself with zero config:
- `sku=` → plan type (programmatic plan health-check)
- `proxy-ep=` → correct API host (§2 step 3 derivation rule: strip `proxy.` prefix → `api.`)
- `exp=` / `expires_at` → refresh scheduling
**NEVER hardcode base URLs** — always derive from `proxy-ep`. GitHub migrates plan-specific endpoints (legacy `api.githubcopilot.com` hardcode broke Business users; see GOTCHAS).

## §4 Model API Surface

| Endpoint | Purpose |
|---|---|
| `GET /models` | Catalog + policy-picker flags; may 429 w/ Retry-After (login-time policy drain); individual accounts may report false picker flags despite enabled policies [HIGH] |
| `POST /chat/completions` | OpenAI-compatible chat |
| `POST /responses` | OpenAI Responses API |
| `POST /v1/messages` | **NATIVE Anthropic Messages passthrough for Claude SKUs** — no translation needed |
| `POST /v1/messages/count_tokens` | Anthropic count-tokens (Claude only) |
| `POST /embeddings` | Embeddings |

Model ids are plain strings (`claude-sonnet-4.6`, `gpt-5.5`, `gemini-3-1-pro` style); treat `/models` output as advisory — probe actual calls at L4-b.

## §5 Why gho_-vs-ghu_ Matters (failure anatomy)

Three compounding failure modes when a raw credential hits model APIs directly (opencode #20759/#20758):
1. Raw `ghu_`/`gho_` is not accepted as Bearer → must exchange first.
2. Wrong endpoint (hardcoded legacy host) → Business tokens rejected.
3. Missing/mismatched identity headers → 400 "model not supported" even with valid bearer.
Fix pattern (PR #20758): detect `ghu_` at runtime → exchange → use `endpoints.api` → inject VS Code headers. For `gho_` tokens: pass through unchanged, default endpoint, no identity headers.

## §5a BUILTIN-PATH GROUND TRUTH (binary-verified 2026-08-26, OpenCode 1.18.23) — READ BEFORE ANY DIRECT-API WORK

Forensic extraction from the pinned binary (`strings ~/.opencode/bin/opencode`) **overturns two assumptions** in §2/§5 for the builtin provider path:

1. **NO token exchange exists in the binary.** `copilot_internal` appears **0 times**; `proxy-ep` appears **0 times**. The builtin auth loader does:
   ```js
   Authorization: `Bearer ${W.refresh}`   // raw stored gho_ device-flow token, sent directly
   ```
   The raw long-lived OAuth user token IS accepted as Bearer by the Copilot API on the sanctioned OpenCode surface. The §2 exchange gate applies to **third-party/direct-API integrations**, NOT the builtin path.
2. **`expires: 0` in auth.json is INERT for github-copilot.** The loader never reads `expires`, never schedules refresh, never exchanges. House credential (`refresh == access`, same gho_, `expires: 0`) works precisely because the field is unused. Verdict for M2 question #6b: **0 does NOT mean always-refresh-per-request; it means never-refresh-because-the-field-is-unread.** Zero latency/rate-limit exposure on `/copilot_internal/v2/token` — that endpoint is simply never called.
3. Additional binary facts: default fallback base URL is legacy `https://api.githubcopilot.com` (not api.individual) when no enterpriseUrl set; request headers are OpenCode-native identity (`User-Agent: opencode/<ver>`, `x-initiator: agent|user`, `Openai-Intent: conversation-edits`, `Copilot-Vision-Request: true` when vision) — **no VS Code impersonation**, consistent with sanctioned status; `_noop` placeholder-tool injection for GHE compatibility is built in; enterprise deployment-type prompt (github.com | enterprise + URL validation) is built into `auth login` methods.

**Tension flag [MEDIUM confidence reconciliation]**: #20759-era evidence (Apr 2026) reported raw-token rejection; the binary (1.18.23) and house operation show pass-through working. Most likely GitHub's server accepts long-lived OAuth tokens on the officially supported surface while exchange remains for other clients/endpoints. Do not generalize either direction without L4-e probe data.

## §6 Enterprise/GHE Topology

- Enterprise slot in OpenCode is domain-parameterized, not plan-locked: third-party implementations fall back to `https://api.individual.githubcopilot.com` when no enterprise domain set; **the OpenCode binary itself falls back to legacy `https://api.githubcopilot.com`** (binary-verified 2026-08-26) → plain github.com accounts plausibly work in an enterprise context [STRONG secondhand — PROBE L4-a].
- GHE device flow initially failed with OpenCode's client ID (app not installed on GHE instances); Copilot CLI's and VS Code GitHub App IDs both work on ghe.com (#3936). Later releases: OpenCode app began working EU-region; `/connect` gained deployment-type selection.
- EMU users authenticate identically to github.com users; enterprise policies (IP allowlists, SSO, model/MCP policy) enforced server-side.

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
