# Antigravity Plugin & Models Guide (OpenCode)

## Overview
This machine is configured with the **NoeFabris OpenCode Antigravity Auth Plugin**. It bridges OpenCode to Google's Antigravity (IDE) APIs via OAuth, unlocking enterprise-grade models with native rate limits.

**Primary benefits:**
- Access to Claude 4.6 models (Opus & Sonnet with Thinking).
- Access to Gemini 3.1 Pro (1M context window) and 3.8 Flash.
- Pooled quota distribution across multiple Google accounts.

## Configuration & Hardening

The plugin configuration lives in `~/.config/opencode/antigravity.json` and `.opencode/antigravity.json`.

**Active Hardened Settings:**
```json
{
  "account_selection_strategy": "sticky",
  "pid_offset_enabled": true,
  "switch_on_first_rate_limit": true,
  "max_rate_limit_wait_seconds": 300,
  "proactive_token_refresh": true,
  "proactive_refresh_buffer_seconds": 3600
}
```

### Why these settings? (The Anti-Ban Strategy)
- **`sticky`**: Forces the agent to stick to one account until rate-limited. This avoids constant round-robin rotation, which violates ToS and flags accounts for bot-like bouncing. It also preserves Anthropic's prompt caching.
- **`pid_offset_enabled`**: When running parallel subagents (e.g., via `oh-my-opencode`), this ensures different processes select different starting accounts based on their PID, avoiding rate-limit dogpiling.
- **`switch_on_first_rate_limit`**: Fails over to the next account immediately instead of hammering an exhausted account.
- **`proactive_token_refresh`**: Refreshes OAuth tokens securely in the background with a 1-hour buffer to avoid bulk-refreshing all 8 accounts at once (which triggers Google IP fraud flags).

## Managing Accounts
You can securely add multiple Google accounts to pool their quota.

To add an account:
1. Run `opencode auth login` in the terminal.
2. Select **Antigravity (Google OAuth)**.
3. If accounts already exist, press `a` to **(a)dd new**.
4. Complete the browser flow.

*Note: The system securely stores refresh tokens and device fingerprints in `~/.config/opencode/antigravity-accounts.json`. Never commit this file.*

## Available Models

Access these models in OpenCode via the `--model` flag or in your agent configurations.

### Gemini (Native Antigravity)
- `google/antigravity-gemini-3.1-pro-high` (1M Context, High Thinking)
- `google/antigravity-gemini-3.1-pro-low` 
- `google/antigravity-gemini-3.8-flash-high`

### Claude (Through Antigravity)
- `google/antigravity-claude-sonnet-4-6-thinking`
- `google/antigravity-claude-opus-4-6-thinking`

## Route B — Antigravity IDE (native GUI, NEW 2026-09-21)

The OpenCode plugin route above never produced a working model call on Node 1,
so the operator installed the **native Antigravity IDE** as the GUI route to the
same frontier models.

- **Install / status**: `antigravity-ide-snap 2.5.5`, snap `latest/stable`,
  classic confinement (`snap list | grep antigravity`). **CONFIRMED RUNNING +
  SIGNED IN (verified 2026-09-21)**: process tree live via
  `pgrep -af antigravity` (incl. `language_server_linux_x64` with a live
  `cloud_code_endpoint` → cloudcode-pa.googleapis.com); config populated at
  `~/.antigravity-ide/` and `~/.config/Antigravity IDE/`.
- **Quota model (official docs + community, RES-GAPS-005 §14.2)**: baseline =
  Gemini 3.1 Pro / 3.8 Flash; Pro refreshes every 5h until a weekly cap; free
  tier = weekly rate limits; **weekly limits apply to all models (Ultra exempt)**.
  Community lockout reports (81h / 6-day `MODEL_CAPACITY_EXHAUSTED`) warn against
  assuming generous daily quota. Track `/usage` in the IDE.
- **Done when**: one frontier session (Gemini 3.1 Pro or Claude Sonnet 4.6)
  completes against this repo — **deferred per operator ("not yet")**.

## Route C — Cline CLI free tier (NEW 2026-09-21)

**Cline CLI 3.0.62** (`/usr/local/bin/cline`, npm global `cline@3.0.62`,
core 0.0.83) as the terminal route to free frontier-class models. Hub verified
healthy (`cline doctor`: hub yes, 0 stale daemons). Auth is OAuth under the
`cline` provider (`~/.cline/data/settings/providers.json`, `lastUsedProvider:
cline`) — no API keys in files.

Advertised free models (user/community-reported; **GLM-5.3-Flash + DeepSeek V4.1
Flash VERIFIED live on Node 1 2026-09-21** — see smoke gate): DeepSeek V4.1 Flash
(1M ctx), Muse Spark 1.3 Contributor (1M), GLM-5.3 Flash, Solar Pro 4, Laguna S
2.1 (+ Union Alpha, Gemma 4 per community).

### Measured behavior on Node 1 (2026-09-21 — read before assuming free = working)

1. **Default run is usage-billed, balance $-0.04 → hard fail.** `cline --json
   "<prompt>"` resolves to `prism-ml/ternary-bonsai-2-27b` and dies with
   `Insufficient balance. Your Cline Credits balance is $-0.04`. The free tier
   is per-model opt-in, not account-wide.
2. **The free tier is per-model opt-in via the interactive selector.** Once the
   operator selects a FREE model in `cline -i` → `/settings` → Cline provider,
   the same `-m` form works: **`cline --json -m z-ai/glm-5.3-flash "Reply with
   exactly: CLINE_SMOKE_OK"` → `completed`, $0** (6602 in / 27 out, 1622 cache
   read), and **`cline --json -m cline-free/deepseek-v4.1-flash "Reply with
   exactly: DS41_SMOKE_OK"` → `completed`, $0** (6854 in / 8 out). Before that
   selection, `-m` runs on unselected free models returned `model not found`
   despite the catalog resolving full model info (entitlement-gated, not a
   routing bug).
3. **`-m` requires `modelType/model` format.** Bare `-m deepseek-v4.1-flash`
   fails `invalid model format. Expected format: modelType/model`.

### Smoke gate (source of truth before any doc claims "working")

```bash
cline doctor                                   # hub healthy, 0 stale daemons
timeout 120 cline --json -m z-ai/glm-5.3-flash "Reply with exactly: CLINE_SMOKE_OK"
# PASSED on Node 1: reason=completed, $0 cost (2026-09-21)
timeout 120 cline --json -m cline-free/deepseek-v4.1-flash "Reply with exactly: DS41_SMOKE_OK"
# PASSED on Node 1: reason=completed, $0 cost (2026-09-21)
```

### Known Cline traps (upstream issues, watch for them)

- **DeepSeek V4.1 Flash text-loop collapse** (`cline/cline#13041`, CLI 3.0.51):
  long ACT sessions can stop emitting `tool_use` and stream unbounded
  near-identical text (worst observed turn 137K chars, 0 tools). Mitigation:
  keep reasoning effort off `xhigh` for long sessions, prefer plan mode for
  big tasks, abort on repeated no-tool turns. Circuit-breaker PR #13042 was
  pending at time of writing.
- **DeepSeek 128K compact** (`cline/cline#10980`): Cline auto-compacts DeepSeek
  V4.1 context at 128K regardless of the model's 1M marketing window; `settings`
  400000 cannot raise it. Verify effective context per-model before relying on
  1M for long inputs.

## Known Architecture Traps

### 1. Claude Tool Schema Validation Bug (#197)
Google's Antigravity endpoint applies strict OpenAPI schema validation for Claude models. 
**The Bug:** OpenCode's native tools (like `todowrite` and `skill`) have loose JSON schemas. If Claude attempts to invoke them, the API throws: `APIError 400 (Invalid Argument)`.
**The Workaround:** When using `antigravity-claude-*` models, you may need to disable native tools in the agent profile, or expect failure states if the agent attempts to use complex OpenCode built-in tools. Gemini models do not enforce this strict validation and work seamlessly.

### 2. Rate Limit Failsafe
If all accounts exhaust their Antigravity quota, the plugin automatically attempts to fall back to the "Gemini CLI" quota pool on the same accounts, effectively doubling your daily limits.

---
*Generated by Antigravity Agent Operations.*