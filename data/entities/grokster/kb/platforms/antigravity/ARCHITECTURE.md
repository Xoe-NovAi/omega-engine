<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Antigravity — Gateway Architecture Reference

**KB Entry**: grokster/platforms/antigravity/ARCHITECTURE
**last_verified**: 2026-08-26 · **rot_class**: medium (protocol stable since Dec 2025; headers/quotas drift)
**Sources**: NoeFabris `docs/ANTIGRAVITY_API_SPEC.md` v1.0 ("Verified by Direct API Testing", 2025-12-13), docs.picoclaw.io provider guide (independent implementation), `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` §A/§B/§D, house source verification of plugin @7db338b

---

## §1 The Gateway — What Antigravity Actually Is

Antigravity's model access is the **Cloud Code Assist "Unified Gateway"** — a single Gemini-format API fronting multiple backends (Vertex AI for Claude, Gemini API for Gemini, other for GPT-OSS). It is NOT `generativelanguage.googleapis.com` and NOT direct Vertex.

### Base URLs

| Environment | URL | Status |
|---|---|---|
| Production | `https://cloudcode-pa.googleapis.com` | ✅ active |
| Daily sandbox | `https://daily-cloudcode-pa.sandbox.googleapis.com` | ✅ active |
| Autopush | `https://autopush-cloudcode-pa.sandbox.googleapis.com` | ❌ unavailable (Dec 2025) |

Secondary surface (Gemini-CLI fallback pool): `https://cloudaicompanion.googleapis.com` — requires a real GCP project with "Gemini for Google Cloud API" enabled. Antigravity pool works against Google's internal default project; the CLI pool needs your own `projectId`.

### Actions (all POST, `/v1internal` namespace)

| Action | Path |
|---|---|
| loadCodeAssist | `/v1internal:loadCodeAssist` — project discovery, tier, onboarding state |
| onboardUser | `/v1internal:onboardUser` |
| fetchAvailableModels | `/v1internal:fetchAvailableModels` — models + `remainingFraction` + `resetTime` |
| generateContent | `/v1internal:generateContent` |
| streamGenerateContent | `/v1internal:streamGenerateContent?alt=sse` |

## §2 Request Anatomy

Auth is a plain OAuth Bearer token + client-impersonation headers:

```
Authorization: Bearer <access_token>
Content-Type: application/json
User-Agent: antigravity/1.15.8 windows/amd64
X-Goog-Api-Client: google-cloud-sdk vscode_cloudshellededitor/0.1
Client-Metadata: {"ideType":"ANTIGRAVITY","platform":"MACOS","pluginType":"GEMINI"}
Accept: text/event-stream          ← streaming only
```

Envelope (Gemini-style, mandatory):

```json
{
  "project": "<project_id>",
  "model": "claude-sonnet-4-6",
  "request": {
    "contents": [{"role": "user", "parts": [{"text": "..."}]}],
    "systemInstruction": {"parts": [{"text": "..."}]},
    "generationConfig": {
      "maxOutputTokens": 10000,
      "thinkingConfig": {"thinkingBudget": 8000, "includeThoughts": true}
    },
    "tools": [{"functionDeclarations": [...]}]
  },
  "requestType": "agent",
  "userAgent": "antigravity",
  "requestId": "agent-<ts>-<rand>"
}
```

Hard protocol quirks (all 400-generators):
- Roles `user`/`model` only; Anthropic `messages[]` rejected.
- `systemInstruction` must be `{parts:[...]}` object.
- JSON Schema: no `const`/`$ref`/`$defs`/`$schema`/`$id`/`default`/`examples`.
- Tool names: no `/`, no leading digit, ≤64 chars; `_ . : -` allowed.
- `googleSearch`/`urlContext` cannot combine with `functionDeclarations` (plugin makes separate search calls).
- Thinking: `maxOutputTokens` MUST exceed `thinkingBudget`.

## §3 Response Anatomy

SSE frames: `{"response": {candidates:[...], usageMetadata:{...}, modelVersion, responseId}, "traceId": "..."}`.
- Claude `responseId` = `msg_vrtx_...` (Vertex routing visible); Gemini/GPT-OSS = base64-like.
- Claude thinking parts: `{thought: true, text, thoughtSignature}` inside Gemini candidates. Signature format regex: `^[A-Za-z0-9+/]+={0,2}$` (PicoClaw sanitization pattern).
- Debug header: `x-cloudaicompanion-trace-id`.

## §4 OAuth Flow & Token Lifecycle

✅ from two independent implementations (NoeFabris, PicoClaw):

1. **OAuth 2.0 + PKCE (S256)**, `access_type=offline`, `prompt=consent`.
2. Auth URL `accounts.google.com/o/oauth2/v2/auth`; token exchange `oauth2.googleapis.com/token`.
3. Local callback listener **port 51121** (plugin default); manual paste fallback after 30s (headless/containers).
4. **Scopes**: `cloud-platform`, `userinfo.email`, `userinfo.profile`, `cclog`, `experimentsandconfigs`. Master scope — refresh tokens are powerful credentials.
5. Post-exchange: email via `oauth2/v1/userinfo`; projectId via `loadCodeAssist`.
6. Access-token TTL ~1h ❓(standard Google default, not explicitly documented); plugins refresh proactively with 5-min expiry buffer.
7. Refresh tokens persist until revoked (`invalid_grant` on password change/security event); plugin auto-prunes revoked accounts.

## §5 Account Pool Mechanics

File: `~/.config/opencode/antigravity-accounts.json`, schema v3:

```json
{
  "version": 3,
  "accounts": [{"email": "...", "refreshToken": "1//0...", "projectId": "...", "enabled": true}],
  "activeIndex": 0,
  "activeIndexByFamily": {"claude": 0, "gemini": 0}
}
```

House file (8.3KB, 7 accounts, all enabled) matches schema shape — confirmed 2026-08-26 v3, re-verified 2026-08-27 as **v4 schema** (drift-001, see R_VAULT_ANTIGRAVITY_20260827.md §D.1). All 7 accounts: refreshToken present, enabled=True, projectId=**False** (G7 dual-pool fallback structurally broken — see R_VAULT_ANTIGRAVITY_20260827.md §C.3). `antigravity.json` does NOT set `pid_offset_enabled` (drift-003, latent risk for parallel subagent dispatch).

Selection strategies (`antigravity.json` → `account_selection_strategy`): house-patched schema offers **`sticky` (default) / `hybrid`** only — `round-robin` REMOVED per D-1 directive (2026-06-29; rapid switching triggers anti-bot detection). Per-model-family rotation cursors. Short 429s (≤5s retryDelay) retried same-account; longer → rotate with exponential backoff. Parallel-process collision fix: `pid_offset_enabled: true`.

**Dual quota pools per account**: Gemini requests use the Antigravity pool first; when ALL accounts' Antigravity quotas exhaust, fall back to the Gemini-CLI pool (same account, model names auto-transformed e.g. `gemini-3-flash` → `gemini-3-flash-preview`). ⚠️ Capacity caveat (specialist M2): "≈2× quota" ≠ 2× availability — during a drought (2026-08-26 observed: ALL accounts ~0% with 100–160h resets) effective Gemini capacity is ZERO for days regardless of pool count; fallback is also conditional on per-account projectId + cloudaicompanion API (G7, unprobed); and both pools sit behind the same hidden throttle (G3) — not independent capacity.

## §6 Two-Layer Rate Limiting

Evidence-backed model (CLIProxyAPI #1015, Mirrowel #54):

1. **Visible quota layer** — daily/weekly windows reported by `fetchAvailableModels` (`remainingFraction`, `resetTime`).
2. **Hidden throttle layer** — short-window rate/abuse limiting NOT reflected in the quota API. Documented case: 17 accounts all 429 while quota reads 100%; IP change did not clear it → account-level flagging suspected. Separate evidence (#54) of simultaneous multi-account 429s suggests an IP-based component too. Likely BOTH: short-window per-IP + long-window per-account abuse flags.

Official docs add: limits correlate with *agent work done*, not request count — volume-based prediction is unreliable by design.

## §7 Plugin Internal Pipeline (@7db338b, house source-verified)

```
OpenCode request (example model: antigravity-claude-opus-4-6-thinking — NOTE: sonnet-thinking variant of this example is DEAD, G11)
  → transform/model-resolver.js   strips `antigravity-` prefix;
      supportsThinkingTiers() matches claude+thinking;
      applies budget family {low:8192, medium:16384, high:32768}
  → dist/src/plugin/request.js    reads variantConfig?.thinkingBudget
      at FLAT keys (:591/:669) — nested schemas silently drop
  → envelope build (§2) → SSE stream → response unwrap (§3)
Preset catalog: config/models.js
```

## §8 Copy-Provenance Note — fingerprint.js divergence RESOLVED BENIGN (2026-08-26)

The former npm-cache copy's `fingerprint.js` differed from the checkout by 26 diff lines (4622 vs 4617 bytes, both built Jul 21). Full content diff classified: **pure refactor, ZERO behavioral difference**.
- Cache: inline ternary `platform === "win32" ? "WINDOWS" : "MACOS"` duplicated at two sites.
- Checkout: hoisted `PLATFORM_CHOICES = ["darwin", "win32"]` const + extracted `platformToDisplayName()` helper used at both sites.
- Identical platform choice set, identical win32→WINDOWS / else→MACOS mapping, no changes to header construction, ordering, or values. Verdict: build/source-state nondeterminism between the npm tarball packaging and the git commit (timestamps 14:59 vs 16:02 same day) — not a functional fork.
- Moot operationally since the file:-switch (M3): cache copies are inert; checkout is the single canonical source (PLAYBOOK §3).

---


*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
