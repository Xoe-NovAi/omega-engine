# Antigravity Plugin & Models Guide (OpenCode)

> ## ⚠️ STATUS — ROUTE A (OpenCode plugin) DEAD/RETRACTED 2026-09-21
> The NoeFabris plugin route below **never produced a working model call on Node 1**.
> Sections "Overview" through "Available Models" are **reference-only**: the model
> IDs listed are unverified, the account-store path is wrong (corrected in F2), and
> the "Rate Limit Failsafe" claim is false (corrected in the traps section).
> **Use Route B (Antigravity IDE) or Route C (Cline CLI) instead.** This retraction
> was applied per frontier review findings C1/C2; provenance: operator +
> DeepSeek V4.1 Flash review session, 2026-09-21.

## Overview
This machine is configured with the **NoeFabris OpenCode Antigravity Auth Plugin**. It bridges OpenCode to Google's Antigravity (IDE) APIs via OAuth, unlocking enterprise-grade models with native rate limits.

**Primary benefits:**
- Access to Claude 4.6 models (Opus & Sonnet with Thinking).
- Access to Gemini 3.1 Pro (1M context window) and 3.8 Flash.
- Pooled quota distribution across multiple Google accounts.

> **Retracted 2026-09-21 (see banner): none of the benefits were ever realized on
> Node 1** — the plugin route produced no working model call. `opencode-antigravity-auth@latest`
> **v1.6.0** (installed 2026-09-11, cache path
> `~/.cache/opencode/packages/opencode-antigravity-auth@latest`) is loaded via the
> repo-local, committed `.opencode/opencode.json` — meaning **any clone of this repo
> attempts to load this plugin**. Version is now pinned/recorded (G5).

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

*Note (corrected 2026-09-21, review F2): **there is no
`~/.config/opencode/antigravity-accounts.json`** — the canonical credential store
is `$XDG_DATA_HOME/opencode/auth.json`
(`~/.local/share/opencode/auth.json`, mode 0600). Never commit that file. The
"8 accounts" figure used to justify the pooled-quota design was **unevidenced** —
no live enumeration exists; treat the account count as unverified.*

> **Risks, ToS & rollback (added 2026-09-21, review C3/G4):** multi-account pooling
> is the *same* family of behavior the settings section flags as ToS-violating
> ("round-robin rotation... flags accounts for bot-like bouncing", "bulk-refreshing
> all 8 accounts... triggers Google IP fraud flags"). Enforcement lands on the
> operator's real Google identity. There is no account inventory, no unlink
> procedure, and no accepted-risk statement in this repo. **Accepted posture**: the
> plugin route is dead anyway (see banner); do not re-enable pooling without an
> inventory + rollback plan. Full revert for the route: remove the plugin entry in
> `.opencode/opencode.json`, delete `.opencode/antigravity.json`, remove
> `~/.cache/opencode/packages/opencode-antigravity-auth@latest`, and remove the
> `google` entry in `~/.local/share/opencode/auth.json`.
> **Actual token data on Node 1 (2026-09-21)**: `~/.local/share/opencode/auth.json`
> contains exactly one `google` entry plus `openrouter` — no account pool exists.

## Available Models

> **⚠️ UNVERIFIED — reference only (retracted 2026-09-21).** These model IDs come
> from plugin documentation; **none ever produced a working call on Node 1**. Do
> not attempt `--model google/antigravity-*` expecting success — there is no
> captured error string for the failure (open verification item).

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
cline`). **⚠️ Credentials ARE in files (corrected 2026-09-21, review F1):** this
path persists live OAuth `accessToken` + `refreshToken` + `expiresAt` + account
identity in plaintext. Protection: keep the directory 0700 / file 0600, never copy
it into docs or USB packets, rotate by deleting the auth block and re-running
`cline` login. (No secret values are reproduced in this repo; `tests/test_secrets.py`
scans git-tracked files only, so it can never catch this path.)

Advertised free models (user/community-reported; **GLM-5.3-Flash + DeepSeek V4.1
Flash VERIFIED live on Node 1 2026-09-21** — see smoke gate): DeepSeek V4.1 Flash
(1M ctx), Muse Spark 1.3 Contributor (1M), GLM-5.3 Flash, Solar Pro 4, Laguna S
2.1 (+ Union Alpha, Gemma 4 per community).

### Measured behavior on Node 1 (2026-09-21 — read before assuming free = working)

1. **Default run is usage-billed, balance $-0.04 → hard fail — UNLESS a free model is pinned.** `cline --json
   "<prompt>"` with no persisted selection resolves to `prism-ml/ternary-bonsai-2-27b` and dies with
   `Insufficient balance. Your Cline Credits balance is $-0.04`. The free tier
   is per-model opt-in, not account-wide. **Pinning semantics (verified 2026-09-21,
   review G1)**: `providers.cline.settings.model` governs bare runs — Node 1 now
   has `"model": "cline-free/deepseek-v4.1-flash"` persisted, so a bare run
   resolves to the free model (still verify with the smoke gate before unattended
   use). **Guard rule**: never invoke `cline` without `-m` until you have checked
   the pinned model; a topped-up balance + billed default = real spend.
2. **The free tier is per-model opt-in via the interactive selector.** Once the
   operator selects a FREE model in `cline -i` → `/settings` → Cline provider,
   the same `-m` form works: **`cline --json -m z-ai/glm-5.3-flash "Reply with
   exactly: CLINE_SMOKE_OK"` → `completed`, $0** (one run: 6602 in / 27 out,
   1622 cache read; re-run by the review session: 6563 in / 8 out / 5189 cache
   read — numbers vary per run), and **`cline --json -m
   cline-free/deepseek-v4.1-flash "Reply with exactly:
   DS41_SMOKE_OK"` → `completed`, $0** (6854 in / 8 out). Before that
   selection, `-m` runs on unselected free models returned `model not found`
   despite the catalog resolving full model info (entitlement-gated, not a
   routing bug).
3. **`-m` requires `modelType/model` format.** Bare `-m deepseek-v4.1-flash`
   fails `invalid model format. Expected format: modelType/model`.

### Smoke gate (source of truth before any doc claims "working")

```bash
cline doctor                                   # hub healthy, 0 stale daemons
timeout 120 cline --json -m z-ai/glm-5.3-flash "Reply with exactly: CLINE_SMOKE_OK"
# PASSED on Node 1: reason=completed, $0 cost (2026-09-21; re-run by review session same day)
timeout 120 cline --json -m cline-free/deepseek-v4.1-flash "Reply with exactly: DS41_SMOKE_OK"
# PASSED on Node 1: reason=completed, $0 cost (2026-09-21)
# Gate = invariant (reason=completed, $0, 1 iteration); token counts vary per run.
```

### Known Cline traps (upstream issues — **dated pre-V4.1, apply with judgment**)

> ⚠️ **Citation notice (added 2026-09-21, review F5):** both issues below were
> filed **before DeepSeek V4.1 Flash released (2026-09-10)** — `cline/cline#10980`
> is dated 2026-05-21 and `#13041` 2026-08-07. They describe an **earlier
> DeepSeek-Flash-family model**, not V4.1. Keep the *doctrine* (verify effective
> context per model; watch long ACT sessions) but do not treat the numbers as
> V4.1 facts. Node 1's own long-context probe (2026-09-21) read 151,604 chars
> (~43.5K tokens) in full with correct recall at $0 — see the DS card.

- **DeepSeek text-loop collapse in long ACT sessions** (`cline/cline#13041`, CLI
  3.0.51, earlier DeepSeek-Flash family): long ACT sessions can stop emitting
  `tool_use` and stream unbounded near-identical text (worst observed turn 137K
  chars, 0 tools). Mitigation: keep reasoning effort off `xhigh` for long
  sessions, prefer plan mode for big tasks, abort on repeated no-tool turns.
  Circuit-breaker PR #13042 was pending at time of writing.
- **DeepSeek 128K compact** (`cline/cline#10980`, earlier family): Cline
  auto-compacts DeepSeek context at 128K regardless of the model's 1M marketing
  window; `settings` 400000 cannot raise it. Verify effective context per-model
  before relying on 1M for long inputs. **Rebalance:** our V4.1 probe passed a
  ~43.5K-token full-read at $0 — effective window on this route is at least
  that; 128K compact was not observed. A 100K+ probe remains open.

## Known Architecture Traps

### 1. Claude Tool Schema Validation Bug (#197)
Google's Antigravity endpoint applies strict OpenAPI schema validation for Claude models. 
**The Bug:** OpenCode's native tools (like `todowrite` and `skill`) have loose JSON schemas. If Claude attempts to invoke them, the API throws: `APIError 400 (Invalid Argument)`.
**The Workaround:** When using `antigravity-claude-*` models, you may need to disable native tools in the agent profile, or expect failure states if the agent attempts to use complex OpenCode built-in tools. Gemini models do not enforce this strict validation and work seamlessly.

> **Corrected 2026-09-21 (review C1):** "Gemini models... work seamlessly" is
> **untestable** — no model call through this route ever succeeded on Node 1.
> Treat the whole architecture-trap section as reference-only.

### 2. Rate Limit Failsafe — CLAIM DELETED (2026-09-21, review C2)
~~If all accounts exhaust their Antigravity quota, the plugin automatically attempts to fall back to the "Gemini CLI" quota pool on the same accounts, effectively doubling your daily limits.~~

**Deleted — false.** Gemini CLI was **shut down 2026-06-18** (see RES-GAPS-005
§14.2: "Gemini CLI shut down free/Pro/Ultra service 2026-06-18; replaced by
closed-source Go binary `agy`... single shared **weekly** quota pool"). There is
no separate "Gemini CLI quota pool" to fall back to, the unit is weekly not
daily, and the pooling premise contradicts the documented single shared pool.
**Verified exhaustion behavior on the Cline route (the live one)**: free quota is
a per-model entitlement; `-m` on the entitled model either works or fails with a
quota error — there is **no silent fallback to a billed model** observed.

---
*Provenance: operator-verified installer/setup notes 2026-09-21; retraction +
corrections applied from the DeepSeek V4.1 Flash frontier review session
(findings F1/F2/C1/C2/C3/G4/G5), 2026-09-21.*