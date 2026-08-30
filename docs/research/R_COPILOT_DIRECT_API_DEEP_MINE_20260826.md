# R_COPILOT_DIRECT_API_DEEP_MINE_20260826

**AP Token**: `AP-JEM-COPILOT-SPECIALIST-v1`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_copilot_deep_mine ⬡ COPILOT-SPECIALIST-01

**Date**: 2026-08-26
**Researcher**: jem (Copilot platform specialist session, established for grokster)
**Method**: Web-primary-sources only (docs.github.com, github.blog changelog, github/copilot-cli issues, OpenCode repo issues/PRs, community proxy repos). Local probes deferred to L4/L5 (§I).
**M23 honesty**: Every claim carries a confidence tag. Unverified items are marked **[UNVERIFIED]** or **[PROBE REQUIRED]**.

---

## SESSION CHARTER — Standing Copilot Specialist

**What future pages should know about this session:**

- This session is grokster's dedicated **Copilot researcher/strategist**. Inline house knowledge
  (OpenCode builtin `github-copilot` provider, auth.json credential present, 2-slot isolation limit,
  AI-Credits economics, Auto-only-plan dead-end #34644) is treated as **verified ground truth** —
  build on it, never re-litigate it.
- Primary research axes: (1) Copilot CLI as harness, (2) direct-API usage outside official surfaces,
  (3) AI-Credit burn economics, (4) multi-account strategy under the 2-slot constraint.
- Key client IDs (memorize — they recur everywhere):
  - `Iv1.b507a08c87ecfe98` — VS Code Copilot **GitHub App** (produces `ghu_` tokens; accepted by `/copilot_internal/v2/token`; broadest model allowlist)
  - `Ov23li8tweQw6odWQebz` — **OpenCode's own OAuth App** (produces `gho_`; NOT accepted by token-exchange endpoint on some paths; narrower server-side model allowlist)
  - `Ov23ctDVkRmgkPke0Mmm` — **Copilot CLI OAuth App** (works on ghe.com device flow)
  - `01ab8ac9400c4e429b23` — VS Code **OAuth App** (used by community plugins; "not allowed" per OpenCode maintainer sentiment)
- Endpoint map: `api.github.com/copilot_internal/v2/token` (exchange) → token contains `proxy-ep=proxy.<plan>.githubcopilot.com` → derive `api.<plan>.githubcopilot.com` (`individual` | `business`) or `copilot-api.<ghe-domain>` for GHE.
- House posture baseline entering this mine: P1a remediation = NO-OP (builtin provider works); multi-account = 2 slots only; burn-rate unknown pending L5 instrumented session.

---

## §A — Copilot CLI Reference

**What it is**: A standalone terminal-native agentic coding agent (`copilot` binary), distinct from the older `gh copilot` gh-extension (`suggest`/`explain`). Both can coexist on one machine ([gist mheadd](https://gist.github.com/mheadd/fee58ef0e74fa8fa11218440d7615d67)).

**Status**: GA February 2026 ([devleader.ca](https://www.devleader.ca/2026/07/27/running-github-copilot-cli-in-scripts-and-cicd-pipelines-headless-mode)). Version lineage observed in the wild: v0.0.369 (install-script examples) → 1.0.x series through 2026; **1.0.66+ required for AI-credit session limits** (July 1, 2026 changelog); issue reports show **1.0.75** active Aug 2026. Current exact latest: **[PROBE REQUIRED — run `copilot --version` locally]**.

**Install** ([docs.github.com](https://docs.github.com/copilot/github-copilot-in-the-cli/setting-up-github-copilot-in-the-cli)):
```shell
npm install -g @github/copilot          # Node 22+
brew install --cask copilot-cli         # macOS/Linux
curl -fsSL https://gh.io/copilot-install | bash
winget install GitHub.Copilot           # Windows
```

**Command surface** (agent-relevant):
| Feature | Detail |
|---|---|
| Headless | `copilot -p "<prompt>" [-s]` — runs prompt, exits. Pipe-to-stdin also supported |
| Permissions | `--allow-tool`, `--deny-tool`, `--allow-all-tools`, `--allow-all`/`--yolo` (all tools+paths+URLs) |
| Named agents | `--agent code-review` etc.; AGENTS.md + Agent Skills define behavior |
| Modes | Interactive / Plan (`Shift+Tab`) / **Autopilot** (continue-until-done; history of runaway-loop bugs, §G) |
| MCP | Ships GitHub's MCP server **by default**; custom MCP servers supported |
| LSP | Optional, configured at `~/.copilot/lsp-config.json` or `.github/lsp.json` |
| Session limits | `/limits` interactive; `--max-ai-credits=N` headless (soft cap, ≥30 recommended, CLI ≥1.0.66) |
| CI auth | `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN` env precedence; secrets redaction via `--secret-env-vars` |
| Sandbox | `copilot --cloud` (public preview — not yet a compliance boundary) |

**vs OpenCode as harness**: Copilot CLI is a competent agent harness (tools, MCP, subagents via `/fleet`, autopilot, headless mode) but is **single-provider by design** — locked to Copilot fabric and its metering. OpenCode is multi-provider, local-first, and (critically for house) does NOT inject Copilot's harness overhead into every turn. Copilot CLI's documented failure modes (autopilot loops, per-tool-call billing surprises, §G) are harness-level costs OpenCode avoids. **Verdict: Copilot CLI is worth probing for parity testing and as an official reference implementation of the auth chain, not as a house replacement for OpenCode.**

---

## §B — Direct API Anatomy & Auth Chain

**CONFIDENCE: HIGH** — reconstructed from four independent implementations (pi/earendil-works TS, LobsterAI TS, oxo-call Rust, agent-zero Python) plus OpenCode's own plugin code.

### The canonical chain

```
1. OAuth Device Flow (RFC 8628)
   POST https://github.com/login/device/code        client_id=<see charter>, scope=read:user
   POST https://github.com/login/oauth/access_token  (poll; authorization_pending / slow_down)
   → GitHub user token: gho_ (OAuth App) or ghu_ (GitHub App)

2. Token Exchange  ← THE CRITICAL GATE
   GET https://api.github.com/copilot_internal/v2/token
   Authorization: token <ghu_/gho_>
   Headers: Editor-Version: vscode/1.96.2, Editor-Plugin-Version: copilot-chat/0.26.7,
            User-Agent: GitHubCopilotChat/<ver>, Accept: application/json
   → { token: "tid=...;exp=...;sku=...;proxy-ep=proxy.individual.githubcopilot.com;...",
       expires_at: <unix>, refresh_in: <seconds>, endpoints: { api: "..." } }
   NOTE: endpoint accepts GitHub App user tokens (ghu_) reliably; gho_ acceptance varies
   by issuing OAuth App (OpenCode's app gets 404 on some paths per opencode#20759).

3. Model API calls
   Base URL derived from token: proxy-ep=proxy.X → https://api.X
     individual plans → https://api.individual.githubcopilot.com
     business         → https://api.business.githubcopilot.com   (also in endpoints.api)
     GHE (ghe.com)    → https://copilot-api.<slug>.ghe.com
   Endpoints observed:
     GET  /models                          (model catalog; policy-picker flags; 429 w/ Retry-After possible)
     POST /chat/completions                (OpenAI-compatible)
     POST /responses                       (OpenAI Responses API)
     POST /v1/messages                     (NATIVE Anthropic Messages for Claude SKUs!)
     POST /v1/messages/count_tokens
     POST /embeddings
   Auth: Authorization: Bearer <short-lived copilot token> (~30 min TTL, refresh at T-5min/T-2min)
   Required headers for ghu_ flows: Editor-Version, Editor-Plugin-Version,
     Copilot-Integration-Id: vscode-chat, matching User-Agent
   X-GitHub-Api-Version header on /models
```

### Critical facts that gate everything

1. **Server-side model allowlist is keyed to CLIENT ID** (opencode#20759): VS Code's GitHub App client ID has a different (wider) model set than OpenCode's OAuth App. This is why third-party tools (copilot.vim, avante.nvim, LiteLLM, every proxy project) impersonate VS Code identity headers.
2. **Raw `ghu_`/`gho_` tokens are NOT accepted as Bearer on model APIs** — must exchange for the short-lived HMAC bearer first.
3. **The token is self-describing**: `sku=`, `proxy-ep=`, `exp=` fields let a client route itself without config. This is the mechanism behind plan-type health checking (§E).
4. **Claude models have a native `/v1/messages` passthrough** — no translation needed for Anthropic-format clients. Major simplification for any house proxy work.
5. **GitHub OFFICIALLY supports OpenCode** (changelog 2026-01-16): paid Copilot subs can authenticate into OpenCode via `/connect` device flow — "no additional AI license needed." This makes OpenCode a **sanctioned surface**, materially de-risking the builtin-provider path (but NOT raw-API proxying, see §F).

---

## §C — Model Catalog & Credit Pricing

**Source**: [docs.github.com/copilot/reference/copilot-billing/models-and-pricing](https://docs.github.com/copilot/reference/copilot-billing/models-and-pricing) + [TokenMix compilation 2026-06-04](https://tokenmix.ai/blog/github-copilot-ai-credits-billing-2026). All prices per 1M tokens, USD. CONFIDENCE: HIGH (official docs); catalog drifts fast — re-verify before cost decisions.

### Individual-plan credit allowances (monthly, reset 00:00 UTC on the 1st, no carryover)

| Plan | Price | Base credits | Flex allotment | Total ($ value) |
|---|---|---|---|---|
| Free | $0 | — | — | small allowance, **auto model selection ONLY** (confirms house #34644 dead-end) |
| Pro | $10 | 1,000 | 500 | 1,500 ($15) |
| Pro+ | $39 | 3,900 | 3,100 | 7,000 ($70) |
| Max | $100 | 10,000 | 10,000 | 20,000 ($200) |
| Business | $19/user | — | — | 1,900/user **pooled org-wide** (promo 3,000 thru Sep 1 2026) |
| Enterprise | $39/user | — | — | 3,900/user pooled (promo 7,000 thru Sep 1 2026) |

Flex allotment is explicitly **variable** — GitHub reserves the right to shrink it as "AI economics evolve." Do not model it as permanent.

### Per-model pricing (as of Aug 2026)

| Provider | Model | Input /1M | Cached-in /1M | Output /1M |
|---|---|---|---|---|
| OpenAI | GPT-5.4 nano | $0.20 | $0.02 | $1.25 |
| OpenAI | GPT-5 mini | $0.25 | $0.025 | $2.00 |
| OpenAI | GPT-5.4 mini | $0.75 | $0.075 | $4.50 |
| Microsoft | MAI-Code-1-Flash | $0.75 | $0.075 | $4.50 |
| Anthropic | Claude Haiku 4.5 | $1.00 | $0.10 | $5.00 |
| Google | Gemini 3.5 Flash | $1.50 | $0.15 | $9.00 |
| Google | Gemini 3.1 Pro | $2.00 | $0.20 | $12.00 |
| OpenAI | GPT-5.4 | $2.50 | $0.25 | $15.00 |
| Anthropic | Claude Sonnet 4.6 | $3.00 | $0.30 | $15.00 |
| OpenAI | **GPT-5.6 Sol** (promo −50% thru Sep 3 2026) | $2.00 (long-ctx $4.00) | $0.20 | $10.00 (long-ctx $15) |
| OpenAI | GPT-5.5 | $5.00 | $0.50 | $30.00 |
| Anthropic | Claude Opus 4.8 | $5.00 | $0.50 | $25.00 |
| Google | Gemini 3.6/3.7 Flash (promo thru Dec 31 2026) | $0.75 | $0.075 | $3.75 |

Notes: code completions & next-edit suggestions are FREE (unmetered) on all paid plans — only chat/agent/CLI/cloud-agent/review consume credits. Copilot code review ALSO burns Actions minutes. Cached input ≈ 10× cheaper than fresh input → **prompt-cache discipline is the single biggest lever** (Microsoft reports >93% context reuse achievable).

**Model id naming**: ids are plain strings (`claude-sonnet-4.6`, `gpt-5.5`, `gemini-3-1-pro` style); discoverable at runtime via authenticated `GET /models`. Some SKUs gated by picker-policy flags that may return false even when enabled on individual accounts (pi source comment) — treat `/models` output as advisory, probe actual calls at L4.

---

## §D — AI-Credits Metering Mechanics

**CONFIDENCE: HIGH** (official changelog + docs).

1. **Unit**: 1 AI credit = $0.01. Usage = Σ(input × rate_in + cached × rate_cached + output × rate_out) ÷ $0.01, per model rates above.
2. **Metered surfaces**: chat, agent mode, Copilot CLI, cloud agent, Spaces, Spark, code review, third-party agents (Claude Code, Codex) riding Copilot auth.
3. **Order of draw**: base credits → flex allotment → additional-usage budget (optional, dollar-denominated; drawdown at $0.01/credit; **may be capped for individuals** based on usage patterns/billing history/verification status).
4. **Reset**: fixed calendar-month, 00:00:00 UTC day 1. No carryover. Not tied to subscription billing date.
5. **Business/Enterprise**: credits pooled at billing-entity level; user-level budgets ALWAYS hard-stop (a $0 ULB blocks instantly); cost-center/enterprise budgets only cap *metered* spend and their stop-at-limit switch is **OFF by default**.
6. **Session limits** (CLI ≥1.0.66, SDK ≥1.0.5, July 1 2026, public preview): `--max-ai-credits=N` / `/limits`. Counts model calls + subagents + background compaction. **SOFT CAP** — in-flight response finishes before enforcement; GitHub guidance: set ≥30 because most single model calls cost >20 credits. Limit does NOT persist across session resume — must re-set.
7. **Legacy annual Pro/Pro+ subscribers**: still on premium-request multipliers until plan expiry (raised June 1). Different pricing table applies.
8. **No mobile-subscription additional credits**: plans bought via GitHub Mobile iOS/Android cannot purchase additional AI credits.

**House implication**: the old premium-request mental model (1 request = 1 unit regardless of size) is DEAD. Every turn is now a micro-metered token transaction. Harness behavior (context re-sending, tool definitions, reasoning depth) directly drives cost — which is why harness choice matters more than model choice for burn control (§G).

---

## §E — Multi-Account Strategy & ToS

**ToS text (GitHub Terms of Service)**: 
- *"you may not have more than one free Account"* — free accounts capped at one (+ one free machine account).
- Paid accounts: **no explicit numeric cap in ToS**. Multiple paid personal accounts are not prohibited by the letter of the terms.
- *"Your login may only be used by one person — i.e., a single login may not be shared by multiple people."* — sharing one account across people is prohibited; one human using multiple own accounts is not addressed.
- Machine accounts: permitted for automated tasks, owner responsible.
- Copilot-specific terms moved to **GitHub Generative AI Services Terms** (March 5, 2026) for new/renewing business subs; individuals remain under ToS Section J + Additional Products Terms.

**CONFIDENCE: MEDIUM-HIGH on text; LOW on enforcement reality.** No found documentation of GitHub banning multi-account Copilot usage for one human. Risk concentrates in: payment-verification evasion, promo abuse, and ToS-violating automation patterns rather than account count per se.

**Practical isolation given OpenCode's 2 builtin slots** (`github-copilot` + `github-copilot-enterprise`):
1. **Slot 1 = `github-copilot`**: standard individual account via official `/connect` flow (sanctioned).
2. **Slot 2 = `github-copilot-enterprise`**: **[PROBE L4]** — pi's implementation proves the enterprise provider falls back to `https://api.individual.githubcopilot.com` when no enterprise domain is set, i.e., **the slot plausibly accepts a plain github.com account**. If confirmed, house gets TWO independent individual-account credentials in stock OpenCode with zero plugins. This is the highest-value cheap probe available.
3. **Beyond 2 slots**: external proxy pattern (§F) — each proxy instance holds its own account credential and exposes a distinct localhost port; OpenCode then sees N custom OpenAI-compatible providers. This bypasses the 2-slot limit entirely and moves ban-risk surface to the proxy pattern (accepted trade-off decision needed).
4. **Plan health-check**: decode the copilot token's `sku=` field after exchange — gives plan type programmatically without UI scraping. `GET /models` response shape also differs by entitlement.

---

## §F — Outside-Harness Patterns (community proxies)

**CONFIDENCE: HIGH on existence/mechanics; MEDIUM on stability; risk flags explicit.**

Active projects (all implement the §B chain):

| Project | Lang | Surfaces exposed | Notes |
|---|---|---|---|
| [messense/copilot-api-proxy](https://github.com/messense/copilot-api-proxy) | Rust | OpenAI `/v1/*`, Anthropic `/v1/messages` (native Claude passthrough), count_tokens | Background token refresh; systemd user-service install; sticky `X-Initiator` |
| [IT-BAER/copilot-api-proxy](https://github.com/IT-BAER/copilot-api-proxy) | ? | OpenAI chat/completions + responses, Anthropic messages, embeddings, dashboard, `/usage` quota | **Carries explicit ToS warning**: "may violate GitHub's Terms of Service… rate limits, API suspension, account review, or account termination" |
| [whtsky/copilot2api](https://github.com/whtsky/copilot2api) | Go | OpenAI + Anthropic + **Gemini-native** + AmpCode routes | Model-capability routing (native messages → responses → chat fallback); 5-min model cache |

**Pattern consensus across all three**: device-flow login → store long-lived GitHub token (0600) → background-refresh short-lived copilot bearer → translate/forward to derived `api.*` base URL → inject VS Code identity headers.

**Ban-risk assessment**: 
- The internal API (`/copilot_internal/v2/token`) is undocumented and explicitly flagged as ToS-gray by the proxy projects themselves. **No confirmed mass-ban incidents found in this pass** — risk is theoretical/dormant, not observed. **[UNVERIFIED absence-of-enforcement — absence of evidence ≠ evidence of absence]**
- Mitigating factor: GitHub formalized OpenCode support (Jan 2026) and ships a public **Copilot SDK** with GitHub-OAuth support designed exactly for building agents outside first-party surfaces ([github/docs SDK oauth page](https://github.com/github/docs/blob/main/content/copilot/how-tos/copilot-sdk/set-up-copilot-sdk/github-oauth.md)) — token types `gho_`, `ghu_`, `github_pat_` all documented-supported for SDK use. **The SDK path is the sanctioned escape hatch**: a house integration should prefer Copilot SDK semantics over raw internal-API impersonation wherever possible.
- Identity-header impersonation (claiming to be VS Code) is the sketchiest element — it exists to satisfy the per-client-ID model allowlist, but it is misrepresentation of client origin. Keep volume low, avoid parallel-fanout patterns that look abusive.

**House verdict inputs**: for ONE account, builtin provider (sanctioned) suffices. For N>2 accounts or non-OpenCode harness attachment, proxy-per-account on distinct ports is the working pattern, with SDK-based integration as the lower-risk alternative worth a spike.

---

## §G — Burn-Rate Intelligence (agentic loops)

**CONFIDENCE: HIGH on documented incidents; MEDIUM on generalizable numbers (self-reported).**

### Documented failure/incident classes

1. **Autopilot infinite loops** (copilot-cli #1523, #1540, #2881, #2969): agent unable to call `task_complete` → system re-prompts every ~3–30s → each iteration consumes a full request/credit-draw until quota hits 402. Damage reports: 17 requests in 2.5 min; 43, 169, 392 requests burned; weekly quotas wiped overnight. Partially fixed v1.0.4 (stop-on-error), regressions reported through v1.0.36+.
2. **Per-tool-call billing** (#2591): single user prompt → 80–100 billed requests because every tool invocation/thinking step is a separate model call. April 7–11 2026: confirmed **overbilling bug** on GPT-5-class models in CLI (experimental feature), refunds issued; quota-tracker corruption complaints persisted weeks after.
3. **Background consumption after task completion** (#4308, Aug 2026, v1.0.75): session climbed 97.8%→100% credits with zero user interaction — attributed to subagent completion/compaction accounting.
4. **General "too expensive" wave** (Visual Studio Magazine 2026-08-07): dev burned ~⅔ of monthly credits in ONE day of light GPT-5.6-Luna work; Max user: 60% of budget in 2 days of Auto mode; VSM's own test: 32-turn session → projected **$180/month**; community thread since June 4 full of cancellations, users moving agentic work to Codex/Claude/Zed/**OpenCode** and keeping Copilot for autocomplete only.

### Realistic cost model (synthesis)

Agentic loop cost ≈ turns × (context_tokens × rate_in_effective + output × rate_out), where context grows every turn unless cached. With Sonnet-4.6-class pricing ($3/$15):
- A 30-turn agent session averaging 50K context tokens/turn (~half cache-hit) ≈ 30 × (25K×$3 + 25K×$0.3 + 2K×$15)/1M ≈ 30 × $0.11 ≈ **$3.30 ≈ 330 credits** — roughly a **full Pro month (1,500 credits) in ~4–5 such sessions**.
- Cheap-model discipline (Gemini Flash promo $0.75/$3.75) cuts that ~4×; caching discipline another ~2–3×.
- **Key insight**: harness overhead dominates. Copilot CLI/VS Code harness re-sends growing context + tool defs every turn (mitigated ~20% by their lazy tool-loading). OpenCode's transform.ts context handling + local-first routing means house agentic loops on Copilot should be run through OpenCode, not Copilot CLI, purely for burn control.

### Controls matrix (use ALL of them)

| Control | Scope | Hard? |
|---|---|---|
| `--max-ai-credits` / `/limits` | one session | Soft (in-flight finishes) |
| User-level budget | billing cycle | **Hard always** |
| Additional-usage budget ($) | overage | Cap may apply (individuals) |
| Model choice | per-call | n/a — biggest lever |
| Prompt caching | per-call | ~10× cheaper input |

**L5 instrumented-session design hint**: run identical task through (a) OpenCode+github-copilot and (b) Copilot CLI, same model, log `session.usage_checkpoint` equivalents + billing-page deltas; measure credits/turn and cache-hit ratio. Hypothesis: OpenCode ≤ CLI burn due to context handling.

---

## §H — Enterprise Slot Behavior

**Question**: does `github-copilot-enterprise` accept regular github.com accounts?

**Evidence**:
1. **Architecturally yes** — pi/earendil-works and rab-agent implementations: `getGitHubCopilotBaseUrl(token, enterpriseDomain)` returns `https://api.individual.githubcopilot.com` when no enterprise domain present. The provider is domain-parameterized, not plan-locked. **[STRONG but secondhand — PROBE L4]**
2. **OpenCode's own enterprise flow is GHE-oriented**: `opencode auth login` → Copilot → Enterprise expects a `*.ghe.com` domain; device flow against ghe.com initially failed with OpenCode's client ID (404) because the OpenCode OAuth App isn't installed on GHE instances; workaround = Copilot CLI's OAuth App (`Ov23ctDVkRmgkPke0Mmm`) or VS Code's GitHub App (`Iv1.b507a08c87ecfe98`) both work on ghe.com device flow (issue #3936). Later EU-region reports: OpenCode's own app began working on ghe.com; `/connect` gained deployment-type selection.
3. **PR #20758** (merged direction): Business/Enterprise support via bearer exchange + dynamic endpoint from `endpoints.api` + VS Code identity headers on `ghu_` tokens. Related #23540: Business models failing with "model not supported" when token exchange skipped and requests hit individual endpoint.
4. **Plan differences that matter**: Business/Enterprise tokens route to `api.business.githubcopilot.com` / `copilot-api.<ghe>`; pooled credits; admin policies can block models/MCP; EMU users authenticate identically. A github.com personal account in the enterprise SLOT would behave as individual — the slot name is misleading; it's really the "second credential" slot.

**Answer**: The slot accepts whatever token you put in auth.json; with a github.com individual token it will function as a second individual provider **if** OpenCode's enterprise loader doesn't force a domain prompt. **PROBE L4 (cheap, high value): write a github.com credential into the enterprise slot, run `opencode run --model github-copilot-enterprise/<model> "Say SUCCESS"`.**

---

## §I — Research Targets Remaining (Local Probes)

| Probe | Target | Method | Value |
|---|---|---|---|
| **L4-a** | Enterprise slot ← github.com account | Write cred to auth.json enterprise slot; smoke `opencode run` | Confirms 2-individual-slot house capability; zero-cost |
| **L4-b** | Live `/models` dump | curl with exchanged bearer; record SKU list + policy flags | Ground-truth model catalog vs docs |
| **L4-c** | Token anatomy | Decode real copilot token fields (`sku`, `proxy-ep`, `exp`, `st`, `chat_mode`?) | Plan health-check implementation |
| **L4-d** | Copilot CLI current version + `--help` full flag dump | install + `copilot --version`, `copilot -p "hi" --max-ai-credits=5` | §A freshness; verify session-limit flag live |
| **L4-e** | Native `/v1/messages` Claude passthrough | Direct curl, tiny prompt | Validates cheapest Claude integration path for house proxy |
| **L5-a** | Instrumented burn-rate A/B | Identical task: OpenCode+copilot vs Copilot CLI, same model; log checkpoints + billing deltas | Answers outstanding house question (§G hypothesis test) |
| **L5-b** | Cache-hit ratio measurement | Repeat-context workload; compare cached-input share | Quantifies biggest burn lever |
| **L5-c** | Proxy stability soak | messense/copilot-api-proxy 1 week light load | Ban-risk empirics (§F) |
| **DOC** | Watch Sep 1 2026 | Biz/Ent promo credits expire; GPT-5.6 Sol promo expires Sep 3 | Cost-model refresh trigger |

---

## Source Index

**Official (HIGH confidence)**
1. https://docs.github.com/copilot/github-copilot-in-the-cli/setting-up-github-copilot-in-the-cli — CLI install
2. https://github.com/github/copilot-cli — README: features, modes, LSP, quota note
3. https://github.com/features/copilot/cli/ — marketing: /fleet, /plan, autopilot, plan inclusion
4. https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/quickstart — programmatic use
5. https://www.devleader.ca/2026/07/27/running-github-copilot-cli-in-scripts-and-cicd-pipelines-headless-mode — headless flags, CI auth, GA date (secondary but detailed)
6. https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/ — AI-Credits go-live
7. https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/ — transition announcement (Apr 27 2026)
8. https://docs.github.com/copilot/reference/copilot-billing/models-and-pricing — per-token pricing
9. https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals — base/flex allowances
10. https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises — pooling, budgets
11. https://github.blog/changelog/2026-07-01-set-ai-credit-session-limits-in-copilot-cli-and-sdk/ — session limits
12. https://github.blog/changelog/2026-01-16-github-copilot-now-supports-opencode/ — **official OpenCode support**
13. https://docs.github.com/en/site-policy/github-terms/github-terms-of-service — account rules
14. https://github.com/github/docs/blob/main/content/copilot/how-tos/copilot-sdk/set-up-copilot-sdk/github-oauth.md — SDK OAuth, supported token types

**Implementation ground truth (HIGH confidence on mechanics)**
15. https://github.com/earendil-works/pi/blob/209bc7b9/packages/ai/src/auth/oauth/github-copilot.ts — full auth chain + proxy-ep derivation + /models policy fallback
16. https://github.com/netease-youdao/LobsterAI/blob/main/src/main/libs/githubCopilotAuth.ts — device flow + headers + base URL
17. https://docs.rs/oxo-call/latest/src/oxo_call/copilot_auth.rs.html — ghu_-only token exchange insight
18. https://github.com/agent0ai/agent-zero/blob/main/plugins/_oauth/helpers/providers/github_copilot.py — GHE URL variants, host validation

**Burn-rate incidents (HIGH confidence events, MEDIUM generalization)**
19. https://github.com/github/copilot-cli/issues/1523 — task_complete loop
20. https://github.com/github/copilot-cli/issues/1540 — overnight quota wipe
21. https://github.com/github/copilot-cli/issues/2881 — autopilot loop, 17 reqs/2.5min
22. https://github.com/github/copilot-cli/issues/2969 — blocked-task loop, 50 iterations
23. https://github.com/github/copilot-cli/issues/2591 — per-tool-call billing + Apr 2026 overbilling incident/refunds
24. https://github.com/github/copilot-cli/issues/4308 — post-task background consumption (v1.0.75)
25. https://visualstudiomagazine.com/articles/2026/08/07/copilot-credit-complaints-keep-coming-too-expensive-to-use.aspx — burn-rate wave, $180 projection, migration-to-OpenCode reports
26. https://startdebugging.net/2026/07/set-ai-credit-session-limits-in-github-copilot-cli-and-sdk/ — soft-cap mechanics, >30 guidance
27. https://dvnc.dev/blog/copilot-cli-ai-credit-session-limits — controls matrix
28. https://tokenmix.ai/blog/github-copilot-ai-credits-billing-2026 — pricing table compilation
29. https://thenewstack.io/github-copilot-token-billing/ — transition analysis

**Multi-account / enterprise / proxies**
30. https://github.com/anomalyco/opencode/issues/20759 + PR #20758 — client-ID allowlist, bearer exchange, dynamic endpoints
31. https://github.com/anomalyco/opencode/issues/3936 — GHE device-flow client-ID saga, CLI-app workaround
32. https://github.com/anomalyco/opencode/issues/11554 — enterprise login client-ID bug
33. https://gist.github.com/JosXa/ab2224a6134917e0dbf31bd08ce92104 — OpenCode GHE plugin (VS Code OAuth client, JWT cron injection)
34. https://github.com/messense/copilot-api-proxy — Rust proxy
35. https://github.com/IT-BAER/copilot-api-proxy — proxy w/ explicit ToS warning
36. https://github.com/whtsky/copilot2api — Go proxy (Gemini/AmpCode surfaces)
37. https://gist.github.com/mheadd/fee58ef0e74fa8fa11218440d7615d67 — gh copilot vs copilot disambiguation
38. https://docs.github.com/en/copilot/how-tos/configure-personal-settings/authenticate-to-ghecom — GHE auth per surface incl. `copilot login --host`

---
*End of R_COPILOT_DIRECT_API_DEEP_MINE_20260826. Specialist session standing by for follow-on pages.*
<!-- PROVENANCE-CORRECTED 2026-08-27T03:02:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

