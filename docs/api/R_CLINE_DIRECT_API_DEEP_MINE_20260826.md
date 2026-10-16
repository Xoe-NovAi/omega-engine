<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R_CLINE_DIRECT_API_DEEP_MINE_20260826
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_cline_deep_mine ⬡ CLINE-SPECIALIST-ESTABLISH

**Date**: 2026-08-26
**Mission**: Deep-mine `api.cline.bot` direct-API access from NON-Cline surfaces (OpenCode via
`@ai-sdk/openai-compatible`). Both Cline surfaces covered for completeness: **Cline CLI** (primary)
and **Cline VS Code extension**.
**Session role**: This document establishes jem as grokster's standing **CLINE SPECIALIST** session
(recorded in grokster's EXPERT_SESSIONS.md). Future pages should build on this charter, not re-run it.
**Confidence tags**: 🟢 HIGH (verified source/live) · 🟡 MEDIUM (single credible source/inference) · 🔴 LOW/UNVERIFIED (M23-flagged)
**House context (do not re-litigate)**: D-557 (Cline+DeepSeek V4 Flash 1M = primary surgical tool),
D-563 (1 active Cline instance; 8-account pool = resilience not parallelism), Aug-22 live probe
(`data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` — free models 403-gated from raw API),
`R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md` (same-day companion doc).

---

## SESSION CHARTER — Standing Cline Specialist

**What future sessions should know about this session's remit:**

| Field | Value |
|---|---|
| Specialist domain | Cline platform: CLI (primary), VS Code extension, api.cline.bot gateway |
| Core question owned | "Can house tooling consume api.cline.bot OUTSIDE the Cline harness?" |
| House rulings inherited | D-557, D-563 (see above) |
| Key local artifacts | `~/.cline/data/secrets.json` (`clineApiKey`, static sk_ key) · `~/.cline/data/settings/providers.json` (WorkOS OAuth state) · `~/.cline/data/logs/cline.log` |
| Established facts | Gateway is OpenAI-compatible at `https://api.cline.bot/api/v1`; model namespace `modelType/model`; bare model ids → HTTP 400; free models → HTTP 403 from non-Cline clients (Aug-22); anthropic/claude-* NOT actually available despite Cline docs listing them; paid tier uses `cline-pass/` id namespace (hyphenated — corrected from earlier house record `clinepass/` per official ClinePass docs, §D.3; live confirm = probe P7); reasoning_effort handling UNDOCUMENTED |
| Escalation path | grokster → Architect for any ToS-sensitive action (header spoofing permanently rejected per audit B2/M23/M8) |

**Standing re-probe protocol** (30-second gate check, run before any posture change):
```bash
curl -s -X POST https://api.cline.bot/api/v1/chat/completions \
  -H "Authorization: Bearer $CLINE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek/deepseek-v4-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```
HTTP 200 = gate lifted → escalate to kali immediately. HTTP 403 = gate stands. HTTP 401 = rotate key first.

---

## §A DIRECT-API VIABILITY VERDICT

*(filled at §A below — see "VERDICT: VIABLE FOR PAID TIERS" section near end of document)*

---

## §B AUTH & KEY ACQUISITION

### B.1 Two auth methods 🟢 HIGH (official docs)

| Method | Use case | Acquisition |
|---|---|---|
| **API key** (static Bearer) | Direct API calls, scripts, CI/CD | [app.cline.bot](https://app.cline.bot) → Settings → API Keys → Create |
| **Account auth token** | Cline extension (VS Code/JetBrains) + CLI | Auto-generated on sign-in; managed by client |

Both use identical header: `Authorization: Bearer YOUR_TOKEN`.

**Free-tier key path**: YES — key creation requires only a Cline account at app.cline.bot;
no paid tier mentioned anywhere in the key-creation flow. The Getting Started guide even
demonstrates using a fresh key against a FREE model (`minimax/minimax-m2.5`) via raw curl
— i.e., **the documented happy path IS direct-API free-model access**. This directly
tensions with our Aug-22 403 on `deepseek/deepseek-v4-flash`. See §C/§D for resolution.

### B.2 Key management surface 🟢 HIGH

- Revoke anytime from same page; deletion is immediate.
- **Programmatic management exists** (Enterprise API):
  - `GET https://api.cline.bot/api/v1/api-keys` (list)
  - `DELETE https://api.cline.bot/api/v1/api-keys/KEY_ID`
  - Whether plain-account tokens can call these (vs enterprise-admin tokens) UNVERIFIED 🔴.

### B.3 Optional identification headers 🟢 HIGH

| Header | Purpose |
|---|---|
| `HTTP-Referer` | Your app URL; usage tracking |
| `X-Title` | App name; appears in usage logs |
| `X-Task-ID` | Unique task id; used internally by the Cline extension |

⚠️ Gate-relevant hypothesis (🔴 UNVERIFIED): `X-Task-ID` is described as extension-internal —
it is plausible the free-model gate keys off this header or its absence. A local probe matrix
(± X-Task-ID / ± HTTP-Referer / ± User-Agent) is listed in §J.

### B.4 Local credential stores (this machine) 🟢 HIGH (house audit, Aug-22)

| Store | Contents |
|---|---|
| `~/.cline/data/secrets.json` | `clineApiKey` (static `sk_…`, 67 chars) + third-party keys; plaintext JSON |
| `~/.cline/data/settings/providers.json` | WorkOS OAuth state for provider `cline`: accessToken/refreshToken/expiresAt/accountId |

HG-003's documented paths (`libsecret`, `~/.local/share/cline/credentials.json`) are STALE
for CLI ≥3.0.56 — actual stores are the two above. House policy: extract static key to `.env`,
never point tools at the plaintext store directly.

### B.5 CLI auth commands 🟢 HIGH

```bash
cline auth                                  # interactive TUI (Sign in with Cline / ChatGPT Sub / OCA / own key)
cline auth cline                            # OAuth sign-in specifically
cline auth -p cline -k "$CLINE_API_KEY" -m anthropic/claude-sonnet-4-6   # quick setup w/ API key
```

Sources: docs.cline.bot/api/authentication · docs.cline.bot/api/getting-started ·
github.com/cline/cline/blob/main/docs/api/authentication.mdx · house audit 20260822 §2.

---

## §C MODEL CATALOG TRUTH

### C.1 THE GATE IS NOW OFFICIAL POLICY 🟢 HIGH — headline finding

`docs.cline.bot/getting-started/free-models.md` states verbatim:

> "**Free model usage is not supported through the Cline API.** Free models are only
> available in the Cline IDE Extension and CLI."

This retroactively explains our Aug-22 live 403 (`deepseek/deepseek-v4-flash is only
available via Cline product surfaces`) as **deliberate, documented product policy** — not a
transient misconfiguration. House implication: waiting for the gate to "lift" is NOT a
strategy; the gate is a business rule (free promos are client-acquisition funnels).

Additional policy notes from same page:
- Free models are **limited-time rotating promotions**, available to any Cline account holder.
- 🔴 **Data-training caveat**: "Free model usage may be used to help improve model performance
  and quality." — relevant to M8/zero-telemetry posture even inside sanctioned clients.
- After quota: paths are ClinePass ($9.99/mo), usage-billing credits, or BYO API key.

**Doc contradiction flagged (M17)**: `api/getting-started.md` still shows "Try a Free Model"
via raw curl with `minimax/minimax-m2.5` ("test without spending credits") — this CONTRADICTS
the free-models page. Treat free-models.md as authoritative (it's specific and matches our
empirical 403); getting-started example likely stale or aspirational. A single curl re-probe
of `minimax/minimax-m2.5` would settle whether ANY free model passes from raw API (§J).

### C.2 Model ID namespace 🟢 HIGH

- Format: `provider/model-name`, OpenRouter convention (e.g. `anthropic/claude-sonnet-4-6`,
  `openai/gpt-4o`, `google/gemini-2.5-pro`). Bare ids rejected HTTP 400 (house probe #1 ✓).
- Paid namespace: **`cline-pass/…`** (hyphenated) ids distinct from free-tier ids — CORRECTED here from the earlier house observation `clinepass/`; official ClinePass docs are authoritative (see §D.3). Live confirmation queued as probe P7.
- Docs still use `anthropic/claude-sonnet-4-6` as canonical curl examples — but house
  third-party validation found anthropic/* NOT actually served despite docs listing them.
  Docs lag reality; always validate against `/api/v1/models` live listing (§J U2).
- Catalog capability flags referenced by docs: `supportsReasoning`, `supportsImages`
  (implying the /models endpoint returns a capability-rich catalog object).

### C.3 Choosing-model table (docs' own guidance) 🟢 HIGH

| Need | Docs recommend |
|---|---|
| Best coding | `anthropic/claude-sonnet-4-6` |
| Long docs | `google/gemini-2.5-pro` (1M ctx) |
| Fast/cheap | `deepseek/deepseek-chat` |
| Free experimentation | `minimax/minimax-m2.5` |

Note: `deepseek/deepseek-chat` (not v4-flash) is the docs' cheap-workhorse recommendation —
the D-557 workhorse model is NOT in the API-docs guidance set at all.

---

## §D RATE LIMITS & QUOTAS

### D.1 Tier structure 🟢 HIGH

| Tier | Cost | External-API access | Limits |
|---|---|---|---|
| Free promos | $0 | ❌ **EXPLICITLY BLOCKED** ("not supported through the Cline API") | Quota-capped, rotating models |
| **ClinePass** | $9.99/mo flat | ✅ **EXPLICITLY SANCTIONED** — docs show raw-curl examples from "your own scripts, apps, or automation" | 3-window quota (below) |
| Usage-billing (Cline credits) | Pay-as-you-go | ✅ (implied by API-first design; 402 on empty credits) | Credit balance |

### D.2 ClinePass quota mechanics 🟢 HIGH

Usage measured against **three simultaneous windows**: 5-hour rolling · calendar week ·
calendar month. Dashboard: app.cline.bot/dashboard/subscription. Concrete token allowances
NOT published (deliberately undisclosed, OpenRouter-style).

**2-5x multiplier semantics**: ClinePass quota is denominated in what the underlying model
would cost at standard API rate — i.e., subscription buys 2-5x the usage an equivalent
credit spend would. Reference per-1M prices published per model.

### D.3 ClinePass model catalog (official) 🟢 HIGH — D-557 CORRECTION

Namespace is **`cline-pass/`** (hyphenated) — house records said `clinepass/`; the official
docs say `cline-pass/`. Verify live before wiring.

| Model | ID | In $/1M | Out $/1M |
|---|---|---|---|
| GLM-5.3 / 5.2 | `cline-pass/glm-5.3` / `-5.2` | 1.40 | 4.40 |
| Kimi K3 | `cline-pass/kimi-k3` | 3.00 | 15.00 |
| Kimi K2.7 Code | `cline-pass/kimi-k2.7-code` | 0.95 | 4.00 |
| Kimi K2.6 | `cline-pass/kimi-k2.6` | 0.95 | 4.00 |
| DeepSeek V4 Pro | `cline-pass/deepseek-v4-pro` | 1.32 (0.66 off-peak) | 3.96 (1.98) |
| **DeepSeek V4 Flash** | **`cline-pass/deepseek-v4-flash`** | **0.44 (0.22 off-peak)** | **1.32 (0.66)** |
| MiMo-V2.5 | `cline-pass/mimo-v2.5` | 0.14 | 0.28 |
| MiMo-V2.5-Pro | `cline-pass/mimo-v2.5-pro` | 1.74 | 3.48 |
| MiniMax M3 | `cline-pass/minimax-m3` | 0.30 | 1.20 |
| Qwen3.8 Max | `cline-pass/qwen3.8-max` | 2.00 | 6.00 |
| Qwen3.7 Max | `cline-pass/qwen3.7-max` | 2.50 | 7.50 |
| Qwen3.7 Plus | `cline-pass/qwen3.7-plus` | 0.40 ≤256K / 1.20 >256K | 1.60 / 4.80 |

**STRATEGIC**: `cline-pass/deepseek-v4-flash` exists → **D-557's workhorse is reachable via
direct API on ClinePass at $9.99/mo**, bypassing the free-gate entirely. The Aug-22 verdict
("config-only wiring works ONLY for API-permitted models") now has a CONCRETE permitted-model
list. Off-peak DeepSeek pricing ($0.22/$0.66) makes agentic loops extremely cheap even
post-quota. Whether the 1M-context config carries to the cline-pass variant is UNVERIFIED 🔴 (§J).

### D.4 Error surface & retry taxonomy 🟢 HIGH

- Standard codes: 400 malformed · 401 bad key · **402 insufficient credits** · **403 key lacks
  resource access (the free-gate code)** · 404 bad endpoint/model-id · 429 rate limit · 5xx upstream.
- **Mid-stream errors arrive inside a 200-OK stream** as `finish_reason:"error"` chunks with
  codes: `context_length_exceeded`, `content_filter`, `rate_limit`, `server_error`. Any M25-style
  streaming handler MUST check finish_reason, not just HTTP status.
- Debug header: `x-request-id` response header.
- No published numeric rate limits; guidance is backoff (429/5xx retryable).

---

## §E CLI SURFACE REFERENCE

### E.1 Headless invocation patterns 🟢 HIGH (official cli-reference)

```bash
cline "prompt"                        # one-shot, act mode, auto-approve ON by default
echo "prompt" | cline                 # piped stdin
cline --json "prompt"                 # NDJSON structured output (non-interactive)
cline -i                              # interactive TUI
cline --id <session-id> "continue"    # RESUME session by id
cline --acp                           # Agent Client Protocol mode (Zed/JetBrains/Neovim/Emacs)
cline -z "task"                       # dispatch to background hub, exit immediately
```

Key flags: `-P provider` · `-m model-id` · `-k api-key` (overrides env) · `-s system-prompt`
· `-p plan` · `-t timeout` · `-c cwd` · `--auto-approve <bool>` (default TRUE headless!) ·
`--retries <n>` · `--data-dir <path>` (isolated state) · `--config <path>`.

### E.2 ⚡ `--thinking` flag — partial answer to the reasoning_effort unknown 🟢 HIGH

```
--thinking <level>   Set reasoning effort level between none|low|medium|high|xhigh (default: medium)
```

The CLI exposes a FIVE-level effort ladder (note: `xhigh`, not OpenAI's `max`). This confirms
effort control exists end-to-end in sanctioned clients; what wire parameter the CLI sends to
api.cline.bot for non-OpenAI models remains UNVERIFIED 🔴 — but a local probe can capture it
from `~/.cline/data/logs/cline.log` (§J).

### E.3 Programmatic integration surfaces 🟢 HIGH

| Surface | Detail |
|---|---|
| **ACP mode** (`--acp`) | First-class Agent Client Protocol — usable from Zed/JetBrains/Neovim/Emacs. Auto-approve defaults FALSE in ACP. Relevant to any future house ACP fabric work |
| **NDJSON output** | `{"type":"say"/"ask","text","ts","say"/"ask" subtype,"reasoning","partial"}` — parseable agent-loop stream incl. reasoning field |
| **Hub daemon** | Local background coordinator at `127.0.0.1:25463` (`CLINE_HUB_ADDRESS`); `-z` dispatches tasks; `cline hub` manages |
| **Schedules** | `cline schedule create --cron … --workspace … --timeout …`; delivery adapters to chat surfaces |
| **Desktop approval** | `CLINE_TOOL_APPROVAL_MODE=desktop` + `CLINE_TOOL_APPROVAL_DIR` — file-based request/decision protocol |

### E.4 Safety-relevant env vars 🟢 HIGH

- `CLINE_COMMAND_PERMISSIONS='{"allow":["npm *","git *"],"deny":["rm -rf *","sudo *"],"allowRedirects":false}'`
  — glob-based shell policy; deny always wins; redirects denied by default.
- `CLINE_SANDBOX` / `CLINE_SANDBOX_DATA_DIR` — sandbox mode.
- `CLINE_DATA_DIR` — relocate all state.
- CA bundle auto-harvest: `~/.cline/cli-node-extra-ca-certs.pem` (regenerated; safe to delete).

### E.5 On-disk layout (current) 🟢 HIGH

```
~/.cline/
  data/settings/providers.json      # API keys + provider config (plaintext; matches house audit)
  data/settings/rules/              # global rules
  data/settings/skills/             # global skills
  data/sessions/                    # session database (SQLite)
  data/logs/hub-daemon.log
  plugins/_installed/
<project>/.cline/
  rules/ skills/ hooks/ plugins/
  mcp.json                          # ← MCP config (NOT cline_mcp_settings.json anymore)
  agents.yaml                       # agent definitions
```

⚠️ House repo references `cline_mcp_settings.json` (legacy VS Code-extension-era name).
Current CLI/extension uses `<project>/.cline/mcp.json`. Migration note for house configs.

---

## §F VS CODE EXTENSION SURFACE

### F.1 Provider configuration model 🟢 HIGH

The extension exposes an **API Provider** dropdown in settings (⚙️ icon) with entries
including: `Cline` (usage-billing), `ClinePass`, `OpenAI Compatible`, `Anthropic`,
`OpenRouter`, `Bedrock` (API-key/IAM/SSO profiles), `Gemini`, `OpenAI (Codex OAuth)`,
`Qwen`, `MiniMax`, `Z AI`, `Poolside`, and 30+ more. For generic endpoints:
Base URL + API Key + Model ID + optional advanced params (max output tokens, context window,
image support, computer-use flag, per-token prices).

### F.2 Auth difference: extension vs direct API 🟢 HIGH

| Surface | Credential |
|---|---|
| VS Code/JetBrains extension signed into "Cline" provider | **Account auth token** — WorkOS-based OAuth pair, auto-generated and auto-refreshed at sign-in; never handled manually |
| Direct API / scripts / CI | **Static API key** from app.cline.bot Settings → API Keys |
| CLI | Either (`cline auth` OAuth flow, or `-k`/env static key) |

Both token types hit the same gateway with the same Bearer header. House machine holds both:
WorkOS OAuth state in `~/.cline/data/settings/providers.json`, static key in
`~/.cline/data/secrets.json`. Whether the ACCOUNT TOKEN passes the free-model gate while the
static key does not is an open empirical question (§J P4) — docs say free models are
"only available in the Cline IDE Extension and CLI", suggesting client identity matters more
than token type, but token-type gating is not excluded.

### F.3 Extension-specific notes 🟢 HIGH

- Free-model selector: FREE-tagged models visible under both Cline and ClinePass providers.
- Telemetry: ON by default, disable in extension settings (ToS §3.6).
- System prompt is hardcoded/not user-editable; `.clinerules` adds context but cannot change
  wire format (GitHub issue #4301 confirms role:"system" message format sent as OpenAI-style).
- Multi-profile support confirmed by third-party setup guides (e.g., RunPod gist).

---

## §G .CLINERULES SPEC

### G.1 Format evolution — house copy is legacy-shape 🟢 HIGH

Current spec (official docs): `.clinerules/` is a **DIRECTORY** of `.md`/`.txt` files,
combined into one rule set. Numeric prefixes optional. House repo's single-file
`.clinerules` v7.2.0 predates this layout — likely still read (docs don't explicitly
deprecate the flat file), but the documented surface is the directory.

### G.2 Full key surface 🟢 HIGH

| Aspect | Spec |
|---|---|
| Locations | Workspace `.clinerules/` + global `~/Documents/Cline/Rules` (Linux/WSL alt: `~/Cline/Rules`) + global `~/.agents/AGENTS.md` |
| File types | `.md` and `.txt` inside `.clinerules/` |
| Frontmatter | YAML between `---` markers; currently ONE key: `paths:` (array of globs) |
| Conditional activation | Rule activates when current context (message paths, open tabs, visible files, edited files, pending ops) matches ANY glob |
| `paths: []` | Rule never activates (soft-disable) |
| No frontmatter | Always active |
| Invalid YAML | **Fail-open**: rule activates with raw frontmatter visible |
| Precedence | Workspace > global on conflict; otherwise combined |
| Toggles | Per-rule UI toggle; toggling off beats conditional matching |
| Cross-tool detection | `.cursorrules`, `.windsurfrules`, `AGENTS.md` auto-detected, individually toggleable |

### G.3 Glob syntax 🟢 HIGH

`*` (no `/`) · `**` (recursive) · `?` single char · `[abc]` · `{a,b}`. Examples:
`src/**/*.ts`, `packages/{web,api}/**`, `**/*.test.ts`.

### G.4 Versioning 🟡 MEDIUM

No formal version field exists in the current spec — house's "v7.2.0" header is a house-side
convention, not a Cline-readable key. Rules are plain markdown; versioning is git's job.

### G.5 Context-cost guidance (docs' own warning) 🟢 HIGH

"Rules consume context tokens… keep concise, link out." Conditional rules exist precisely to
cut token waste — directly relevant to M18 Token Efficiency if house ever adopts Cline rules.

Sources: docs.cline.bot/customization/cline-rules · docs.cline.bot/cli/cli-reference.

---

## §H ToS & CONSTRAINTS

Source: cline.bot/tos (Last Modified Sep 25, 2025). Clauses ranked by house relevance:

### H.1 Directly gate-relevant 🟢 HIGH

| Clause | Text (condensed) | House implication |
|---|---|---|
| §2.2(10) | No accessing content "through any technology or means other than those provided by the Service **or authorized by us**" | The documented API **IS** the authorized means — ClinePass external use is expressly authorized. Header-spoofing to reach free models is NOT |
| §2.2(11) | No bypassing "measures we may use to prevent or restrict access" | The free-model 403 gate is such a measure. **Circumvention = ToS breach.** Audit Path B2 stays permanently rejected — now with ToS citation |
| §2.2(4) | No buying/selling/transferring API keys without written consent | Constrains any future multi-account key pool: keys must each be tied to legitimately-held accounts; trading/sharing keys across users is forbidden. D-563's resilience-pool posture needs account-ownership legitimacy per key |

### H.2 Data & training posture 🟢 HIGH — M8/zero-telemetry relevant

- **§3.2(2)**: Cline grants itself license to use User Content "to improve and develop the
  Service… including creating and using de-identified or aggregated data… **provided that when
  you purchase a per-seat Subscription… this subsection 2 will not apply during such
  Subscription**." → **Paid subscription = contractual carve-out from improvement/training use.**
  Free tier = your content may feed product improvement (matches free-models.md's training caveat).
- **§3.5**: With Cline-provided keys, prompts/code are transmitted to third-party AI Model
  Providers, which "may use User Content for training unless you have explicitly opted out."
  You have NO direct contract with those providers.
- **§3.1**: BYOK + self-controlled infrastructure → "Cline does not receive or store your input
  tokens, output tokens, underlying code."
- **§3.6**: Telemetry on by default; disable in settings.

**Sovereignty reading**: the ONLY privacy-clean configurations are (a) BYOK/local models, or
(b) paid Subscription + telemetry off. Free-tier gateway usage is the worst case: gated AND
training-exposed.

### H.3 Other constraints 🟢 HIGH

- §2.2(2): no automated access exceeding human-browser rates (scraping clause; API usage under
  documented API is the sanctioned automation channel).
- §2.2(9): no benchmarking/competitive analysis "to our detriment" — flag for any house
  published comparisons of ClinePass vs alternatives.
- §1.3 / §2.1: service and license revocable at any time, with or without cause — **no
  entitlement durability**; treat api.cline.bot as an opportunistic provider, never a fabric
  dependency above deep-fallback priority.

---

## §I COMMUNITY INTELLIGENCE

### I.1 Absence finding: nobody bridges api.cline.bot INTO other harnesses 🟢 HIGH (absence, searched)

Searches across GitHub, dev.to, gists, npm found **zero projects attaching api.cline.bot as a
provider inside OpenCode/Aider/other harnesses**. The community pattern runs the OPPOSITE
direction — Cline as a CLIENT consuming other backends:

| Project | Pattern |
|---|---|
| OCP (Open Claude Proxy) | localhost OpenAI-compat proxy ← Cline/OpenCode/Aider all consume Claude Pro sub |
| aigate | Kiro/Copilot free tiers → local OpenAI+Anthropic endpoint; README shows OpenCode config consuming it |
| RunPod gist | RunPod endpoints wired into Cursor/Cline/OpenCode side-by-side |

Interpretation: the free-model client-gate makes outbound bridging pointless (the only models
worth bridging are gated), and ClinePass is too niche to have spawned bridge tooling yet. We
would be early if we wired `cline-pass/*` into OpenCode — no community precedent to copy, but
also no known breakage reports.

### I.2 Gate corroboration 🟡 MEDIUM

No public GitHub issue documents the 403 free-model gate directly (searched cline/cline issues).
The docs' own free-models page is the strongest public statement. Third-party model-catalog
validation (house inline context: anthropic/* listed but not actually served) remains the best
evidence that docs lag gateway reality.

### I.3 Ecosystem signals 🟢 HIGH

- Cline SDK (`@cline/sdk`, `@cline/core`, `@cline/agents`, `@cline/llms`) now positions Cline as
  an embeddable agent runtime — hub-spoke daemon architecture, plugins, hooks, scheduled agents.
  This is a THIRD integration path besides raw-API and CLI-wrapper: embed the harness itself.
- ACP mode means Cline can serve ANY ACP-capable editor — a sanctioned way to consume Cline's
  agent loop without raw-API gating concerns (gate applies to model access, not agent access;
  🔴 inference, untested).

---

## §A DIRECT-API VIABILITY VERDICT

**VERDICT: VIABLE FOR PAID TIERS, BLOCKED FOR FREE TIER — and the block is now official,
documented policy rather than a transient anomaly.** Raw OpenAI-compatible calls to
`api.cline.bot/api/v1` work with a static key created free at app.cline.bot, and ClinePass
($9.99/mo) is EXPLICITLY sanctioned for external automation use ("from your own scripts, apps,
or automation") with a full official curl example — including `cline-pass/deepseek-v4-flash`,
which restores D-557's workhorse through a legitimate paid channel at $0.22–0.44/1M input
(off-peak/peak). Free promotional models are hard-gated to Cline product surfaces by ToS
§2.2(10)/(11)-backed policy; circumvention (header spoofing) is both fragile and a ToS breach —
permanently rejected.

**House posture change**: the Aug-22 framing "config-only wiring works ONLY for API-permitted
models" upgrades to a CONCRETE decision: either (a) $9.99/mo ClinePass unlocks D-557 via direct
API in OpenCode's picker (~7 LOC config delta, zero Python), or (b) stay on the CLI-wrapper
deep-fallback path for $0. There is no longer a free direct-API path worth pursuing.

---

## §J RESEARCH TARGETS REMAINING (LOCAL PROBES NEEDED)

All probes are read-only or zero/low-cost; none require new code modules.

| # | Probe | Method | Resolves |
|---|---|---|---|
| P1 | Gate re-check on free model (30s standing protocol, Charter above) | curl POST chat/completions, `deepseek/deepseek-v4-flash` | Whether Aug-22 gate still stands |
| P2 | Does ANY free model pass raw API? (docs contradiction) | Same, model `minimax/minimax-m2.5` | getting-started vs free-models doc conflict |
| P3 | Live `/api/v1/models` listing | `curl https://api.cline.bot/api/v1/models -H "Authorization: Bearer $CLINE_API_KEY"` | Real catalog, capability flags, enforced context/output caps (resolves U2: deepseek-v4-flash output cap guess of 131072), whether anthropic/* actually served |
| P4 | Token-type gate test | Repeat P1 using WorkOS accessToken from providers.json instead of static key | Whether gate keys on token type vs client identity |
| P5 | Header matrix on free model | P1 ± `X-Task-ID` / ± `HTTP-Referer` / ± `User-Agent: cline-cli/x.y.z` | What the gate inspects (NOT spoofing to bypass — diagnostic only; any success would still be ToS-§2.2(11)-fraught and must not be used) |
| P6 | reasoning_effort wire capture | Run `cline --thinking xhigh "ping"` with CLINE_DEBUG=1; grep `~/.cline/data/logs/cline.log` for request body | What param the sanctioned client sends (resolves U3); informs whether OpenCode variants should ship |
| P7 | cline-pass namespace verification | P3 listing grep for `cline-pass/` vs `clinepass/` | Corrects house records before any config write |
| P8 | 1M-context survival on cline-pass/deepseek-v4-flash | Post-P3: large-context smoke call (or read caps from catalog) | Whether D-557's 1M figure carries to paid variant |
| P9 | CLI version stamp | `cline version` | Refresh house's 3.0.52/3.0.56-era references |
| P10 | ClinePass quota visibility | Check app.cline.bot dashboard subscription tab (manual) | Concrete allowance magnitudes (undisclosed in docs) |

Escalation rule: P1/P2 results go to kali BEFORE any opencode.json change; P7 result corrects
this document and the Aug-26 companion doc.

---

## SOURCE INDEX

### Official (docs.cline.bot unless noted)
1. https://docs.cline.bot/llms.txt — full documentation index
2. https://docs.cline.bot/api/overview — gateway overview, OpenAI-compatible positioning
3. https://docs.cline.bot/api/authentication — API keys vs account tokens, custom headers, Enterprise key management
4. https://docs.cline.bot/api/getting-started — key creation flow, first request, streaming intro, free-model curl example (contradicted by #6)
5. https://docs.cline.bot/api/models — model ID format, capability flags, choosing-guidance
6. https://docs.cline.bot/getting-started/free-models.md — **THE GATE**: "Free model usage is not supported through the Cline API"
7. https://docs.cline.bot/getting-started/clinepass.md — $9.99/mo, `cline-pass/` catalog + pricing, 3-window quotas, **external-use sanction + curl example**
8. https://docs.cline.bot/getting-started/cline-provider.md — usage-billing credits flow
9. https://docs.cline.bot/api/chat-completions.md — endpoint reference, SSE streaming, delta.reasoning, mid-stream errors, tool calling
10. https://docs.cline.bot/api/errors.md — error codes incl. 403 semantics, finish_reason:"error", retry taxonomy, x-request-id
11. https://docs.cline.bot/cli/cli-reference.md — full flags incl. --thinking/--acp/--id/-z, env vars, config layout
12. https://docs.cline.bot/customization/cline-rules — .clinerules directory spec, paths frontmatter, cross-tool detection
13. https://github.com/cline/cline/blob/main/docs/api/authentication.mdx — source mirror of #3
14. https://github.com/cline/cline/blob/main/apps/cli/README.md — CLI README (connectors, schedules, approval modes)
15. https://cline.bot/tos — Terms (Sep 25 2025): §2.2 restrictions, §3.2 training-license + subscription carve-out, §3.5 provider transmission, §3.6 telemetry
16. https://cline.bot/faq — "Cline is free; you pay for token access"

### Community / third-party
17. https://github.com/cline/cline/issues/4301 — hardcoded system prompt, role:"system" wire format
18. https://dev.to/dtzp555max/use-your-claude-promax-subscription-to-power-openclaw-opencode-cline-and-any-openai-compatible-na0 — OCP proxy (community direction: INTO Cline, not out)
19. https://github.com/hoazgazh/aigate — same-direction proxy ecosystem evidence
20. https://gist.github.com/zackmckennarunpod/e0d87bff8a4676dce24d6d736a1cc9cd — multi-tool provider setup patterns incl. Cline extension profiles
21. https://docs.cline.bot/sdk/overview (+ llms.txt SDK section) — embeddable runtime, hub-spoke architecture

### House (local)
22. data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md — live 403 probe, credential stores, M22 base_url repair
23. docs/research/R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md — same-day companion; OpenCode config math
24. Inline context: D-557, D-563, third-party model-catalog validation (anthropic/* absent), `clinepass/` namespace observation (corrected to `cline-pass/` by this research, pending P7)

---
*⬡ OMEGA ⬡ JEM ⬡ CLINE-DEEP-MINE ⬡ PAID-TIER-VIABLE / FREE-GATED-BY-POLICY ⬡ 2026-08-26*
<!-- PROVENANCE-CORRECTED 2026-08-27T03:02:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

