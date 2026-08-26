# Cline — Architecture Reference

**KB Entry**: grokster/platforms/cline/ARCHITECTURE
**last_verified**: 2026-08-26 · **rot_class**: fast (gateway/tier details change; core anatomy stable)
**Sources**: docs.cline.bot (api/overview, api/authentication, getting-started/free-models, getting-started/clinepass, cli/cli-reference), cline.bot/tos, `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (live probe), `docs/research/R_CLINE_DIRECT_API_DEEP_MINE_20260826.md`

---

## §1 Gateway Anatomy

```
Cline product surfaces (extension / CLI) ─┐
                                          ├→ api.cline.bot/api/v1 → upstream providers
External scripts / OpenCode / CI ─────────┘   (OpenAI Chat Completions wire format)
```

- Wire endpoint: `POST https://api.cline.bot/api/v1/chat/completions`. VERIFIED (docs + house probe).
- Model id namespace: `provider/model-name` (OpenRouter convention). Bare ids → HTTP 400 "invalid model format". VERIFIED (house probe #1).
- Tier namespaces: free/promo ids (`deepseek/deepseek-v4-flash`, `minimax/minimax-m2.5`) vs paid **`cline-pass/*`** (hyphenated — CORRECTED 2026-08-26; old KB said `clinepass/`). Usage-billing ids use plain `provider/model`.
- Optional headers: `HTTP-Referer`, `X-Title`, `X-Task-ID` (extension-internal task id — possible gate input, UNVERIFIED).

## §2 Auth Chain

| Method | Who | Acquisition | Storage |
|---|---|---|---|
| Static API key | scripts, CI, direct API | app.cline.bot → Settings → API Keys | user-managed (env/.env) |
| Account auth token | extension + CLI | auto-generated at sign-in; WorkOS-based OAuth pair, auto-refreshed | see below |

Local credential stores on house machine (VERIFIED Aug-22 audit; HG-003's paths are STALE):

| Store | Contents |
|---|---|
| `~/.cline/data/secrets.json` | `clineApiKey` (static `sk_…`) + third-party keys; plaintext JSON |
| `~/.cline/data/settings/providers.json` | WorkOS OAuth state: accessToken/refreshToken/expiresAt/accountId |

House policy: extract static key to `.env` (`CLINE_API_KEY=…`); never point tools at the plaintext store directly.

## §3 Tier Structure & the Free Gate

| Tier | Cost | External API | Limits |
|---|---|---|---|
| Free promos | $0 | ❌ BLOCKED — documented policy ("not supported through the Cline API") | quota-capped, rotating models, training-exposed |
| ClinePass | $9.99/mo | ✅ explicitly sanctioned for external automation | 3 windows: 5h rolling + weekly + monthly; magnitudes undisclosed |
| Usage-billing | pay-as-you-go credits | ✅ implied by API-first design | credit balance; HTTP 402 when empty |

Gate enforcement observed: HTTP 403 `"deepseek/deepseek-v4-flash is only available via Cline product surfaces"` (house live probe 2026-08-22). Gate mechanism (token type vs client identity vs headers) UNRESOLVED — probes P4/P5.

## §4 Runtime Topology (CLI)

- **Hub daemon**: local background coordinator at `127.0.0.1:25463` (`CLINE_HUB_ADDRESS`); `-z/--zen` dispatches tasks to it; `cline hub` manages; logs at `~/.cline/data/logs/hub-daemon.log`. VERIFIED (cli-reference).
- **Sessions**: SQLite DB at `~/.cline/data/sessions/`; resume via `--id <session-id>`; `cline history` lists.
- **ACP mode**: `--acp` exposes the agent loop over Agent Client Protocol (Zed/JetBrains/Neovim/Emacs); auto-approve defaults FALSE in ACP.
- **Desktop approval mode**: `CLINE_TOOL_APPROVAL_MODE=desktop` + `CLINE_TOOL_APPROVAL_DIR` — file-based request/decision JSON protocol.

## §5 On-Disk Layout (current, VERIFIED vs cli-reference)

```
~/.cline/
  data/settings/providers.json      # provider config + OAuth state
  data/settings/rules/              # global rules
  data/settings/skills/
  data/sessions/                    # session SQLite DB
  data/logs/hub-daemon.log
  plugins/_installed/
<project>/.cline/
  rules/ skills/ hooks/ plugins/
  mcp.json                          # ← current MCP config location
  agents.yaml                       # agent definitions
```

Legacy names no longer current: `cline_mcp_settings.json` (old extension era), single-file `.clinerules`.

## §6 Error Surface (streaming-relevant)

- Standard codes: 400 malformed · 401 bad key · 402 insufficient credits · **403 resource-access/gate** · 404 bad model-id · 429 rate limit · 5xx upstream.
- **Mid-stream errors arrive inside a 200-OK stream** as `finish_reason:"error"` chunks (`context_length_exceeded`, `content_filter`, `rate_limit`, `server_error`). Any streaming handler MUST check finish_reason, not just HTTP status. VERIFIED (api/errors doc).
- Debug header: `x-request-id`.

## §7 Streaming Behavior

- SSE default (`stream: true`); `data:` lines terminated by `data: [DONE]`.
- Reasoning models emit `delta.reasoning` (+ optional encrypted `delta.reasoning_details` pass-back); reasoning tokens counted separately from output.
- Final chunk carries `usage` incl. `prompt_tokens_details.cached_tokens` and computed `cost` (USD).
- Documented request params: model/messages/stream/tools/temperature only — `max_tokens` and `reasoning_effort` are NOT documented at the gateway. VERIFIED absence in docs.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
