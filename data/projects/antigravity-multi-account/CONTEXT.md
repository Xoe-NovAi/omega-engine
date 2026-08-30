<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: antigravity-multi-account
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**8 Google accounts → unified Antigravity quota dashboard + OAuth token rotation pool**. Solves "sign in/out of 8 accounts to check quota" pain point.

### STATUS (2026-07-19)
- **Research**: ✅ Complete (6 gaps resolved, 35+ sources)
- **Immediate Tool**: ✅ Available — [Antigravity Tools](https://github.com/lbjlaq/Antigravity-Manager) (30K⭐, Tauri desktop app)
- **CLI Tool**: ✅ Available — `npm install -g antigravity-usage` (dual-fetch: local IDE + cloud)
- **Custom Integration**: ❌ Not started — D-299 `omega-vault` workstream

### KEY FILES
| Type | Path |
|------|------|
| Research Report | (in context — researcher output 2026-07-19) |
| Immediate Tool | `https://github.com/lbjlaq/Antigravity-Manager/releases` |
| CLI Tool | `npm install -g antigravity-usage` |
| Python Lib | `pip install antigravity-auth` |
| Target Integration | `src/omega/infra/vault/providers/antigravity/` (to create) |

### ARCHITECTURE
```
Antigravity Cloud Code API
  POST cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels
  Auth: OAuth 2.0 PKCE → Bearer access_token (55 min) ← refresh_token (1//...)
  Response: remainingFraction (0.0-1.0) per model + resetTime

Account Pool (8 accounts)
  ├── Rotation Strategy: sticky (<2) → hybrid (2-5) → round-robin (5+)
  ├── Soft Threshold: 90% (skip account to avoid Google throttling)
  ├── Storage: OS keyring (not plaintext JSON)
  └── Dashboard: Textual TUI + SQLite history
```

### WHAT IT DOES / DOESN'T DO
| ✅ DOES | ❌ DOESN'T |
|---------|------------|
| Unified quota view across 8 accounts | WARP IP rotation (different problem) |
| Auto-rotate on quota exhaustion / 429 | Fix Google's burst limiter (unqueryable) |
| 90% soft threshold prevents bans | Guarantee no bans (ToS risk exists) |
| Machine-readable quota data | Official API (all reverse-engineered) |

### CRITICAL RISKS (from research)
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Account ban (ToS violation)** | Medium-High | Use established accounts only, 90% soft threshold, no fresh accounts |
| **OAuth client ID revocation** | Low | Track zeklop fork; support custom `ANTIGRAVITY_CLIENT_ID/SECRET` |
| **Burst rate limiter (429 despite quota)** | High | Empirical detection only; auto-rotate on 429 |
| **AI Credit Overages API unknown** | Medium | Track issue #536; use Cloud API directly |

### IMMEDIATE ACTIONS
1. **Today**: Install Antigravity Tools desktop app → add 8 accounts → instant dashboard
2. **This Week**: `npm install -g antigravity-usage` for CLI/scripting
3. **D-299**: Build `omega-vault` Antigravity provider (OS keyring + 60s polling + TUI)

### DECISIONS LOG
- **D-XXX**: WARP pool ≠ Antigravity pool (IP vs OAuth rotation)
- **D-XXX**: 90% soft threshold mandatory (ban prevention)
- **D-XXX**: Layer on `antigravity-auth` Python lib, don't reimplement OAuth
- **D-XXX**: Custom integration lives in `omega-vault` (D-299), not WARP pool

---

*⬡ OMEGA ⬡ CPR ⬡ antigravity-multi-account ⬡ 2026-07-19*