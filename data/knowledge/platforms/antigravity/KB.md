<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 Antigravity CLI/IDE — Knowledge Base
# ⬡ OMEGA ⬡ KALI ⬡ trc_platform_kb ⬡ v1.1.0
**Source**: Forensic Research Wave 5 (2026-06-07)
**Status**: FULLY SEEDED
**Last Updated**: 2026-06-07

---

## §1: Overview
Antigravity is an external plugin system (`npm:opencode-antigravity-auth`) that intercepts OpenCode's HTTP fetch calls to `generativelanguage.googleapis.com` and routes them through a multi-account infrastructure.

- **Integration**: Hooks into OpenCode via a custom `fetch` wrapper in `src/plugin.ts` $\rightarrow$ `auth.loader`.
- **Core Purpose**: Account rotation, OAuth token management, and request transformation.

---

## §2: Rotation Logic (Sovereign Analysis)
**Strategy**: `"account_selection_strategy": "sticky"`
- **Behavior**: Implements a "prefer-current" policy. It applies a `STICKINESS_BONUS` to the current account's score.
- **Rotation Trigger**: Rotation only occurs if the current account is:
    1. Rate-limited (429 response).
    2. Over soft quota threshold.
    3. Cooling down from consecutive failures.
- **Verdict**: "Sticky" is the optimal setting for prompt cache preservation.

---

## §3: Auth & Token Management
- **Storage**: Tokens stored in `~/.config/opencode/antigravity-accounts.json` (v4 schema).
- **Refresh Cycle**: On-demand refresh (`accessTokenExpired` $\rightarrow$ `refreshAccessToken`) supplemented by a `ProactiveRefreshQueue`.
- **Fingerprinting**: Generates randomized `deviceId`, `sessionToken`, and `userAgent` to mislead identity tracking.

---

## §4: Interception Mechanism
- **Fetch Wrapper**: Intercepts all calls to `generativelanguage.googleapis.com`.
- **Payload Modification**: Injects `Authorization: Bearer <token>` and `x-goog-user-project` headers.
- **Error Handling**: Surfaces `NoAvailableAccountsError` and `AntigravityTokenRefreshError` back to the engine.

---

## §5: Sovereign Risks
- **Privacy**: Fingerprinting captures device data.
- **Security**: Refresh tokens are stored in plain text.
- **Identity**: Accounts are still linked at the Google account level via `projectId` and `email` headers.

---

## §6: Key File Path Summary

| Component | Absolute Path |
| :--- | :--- |
| **Config** | `~/.config/opencode/antigravity.json` |
| **Accounts** | `~/.config/opencode/antigravity-accounts.json` |
| **Plugin Source** | `github.com/NoeFabris/opencode-antigravity-auth` |
| **Logs** | `~/.config/opencode/antigravity-logs/` |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_platform_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
