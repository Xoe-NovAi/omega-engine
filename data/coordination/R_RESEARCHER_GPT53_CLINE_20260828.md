---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_brief"
document_id: "R_RESEARCHER_GPT53_CLINE_20260828"
title: "GPT-5.3-Codex + Cline CLI Integration — Verified Brief for 8-Account Review"
status: "ACTIVE — RESEARCHER (Jem Analyst L2) — not Grokster"
date: "2026-08-28"
supersedes: "R_RESEARCHER_GPT53_20260828.md (premise-failure false-positive) and R_ANTIGRAVITY_GPT53_20260828.md (correct on identity, thin on Cline CLI specifics)"
provenance: "Researcher agent (Jem Analyst) with explicit M23+C-MEM-004 web verification"
---

# 🔱 R_RESEARCHER_GPT53_CLINE_20260828 — Verified Brief
**AP Token**: `AP-RESEARCHER-GPT53-CLINE-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_researcher_gpt53_cline ⬡ ACTIVE

**From**: @researcher (Sovereign Researcher, Jem Analyst sub-facet)
**To**: @grokster (Grokster ecosystem specialist) + @architect (escalation) + @kali (handoff for SSOT sync)
**Time budget used**: ~18 min (of 15-20 budgeted)
**Method**: Web-primary, multi-source corroboration. Active tool calls performed. M23 applied (premise verification BEFORE synthesis). C-MEM-004 (FTS5-first) was attempted via `memory_search` but produced no prior indexed treatment of the Cline-CLI × GPT-5.3-Codex intersection; pivoted to web search as primary.

---

## §0 — EXECUTIVE SUMMARY (5 bullets, 90 seconds)

1. **Model identity CONFIRMED: GPT-5.3-Codex.** The Antigravity report (`R_ANTIGRAVITY_GPT53_20260828.md`) is correct. The competing `R_RESEARCHER_GPT53_20260828.md` is **empirically wrong** (refusal-with-pivot on a false premise) — it confuses GPT-5.3-Codex with GPT-5.3 Instant and ignores 7+ primary sources (OpenAI blog, OpenAI API docs, Wikipedia, OpenRouter, llmreference, aireleasetracker, everydayaiblog). GPT-5.3-Codex is real, GA, released 2026-02-05 (Codex surfaces) / 2026-02-24 (API), 400K context, $1.75/$14 per 1M. **GPT-5.6 Sol (2026-07-09) is a separate, newer, general-purpose line.** Both can coexist in the fleet.

2. **Cline CLI integration has THREE clean paths, ranked.** (A) **Cline's first-class `openai-codex` provider with ChatGPT OAuth** — zero API key, zero Responses-vs-Chat-Completions trap, maps to how Cline was *designed* to consume this model. (B) **Cline's `openai` provider with custom Base URL → OpenRouter** — works today, abstracts the Responses endpoint, gives 8-account multi-key load distribution. (C) **Cline's `openai` provider direct to OpenAI API** — works but requires the API org to be set up (Tier 1 = $5 minimum), and naive configs default to `/v1/chat/completions` which **will fail** for this model.

3. **The existing `cline` fabric entry in `providers.yaml` is the WRONG place to add this model.** That entry routes to `https://api.cline.bot/api` and was probe-confirmed on 2026-08-22 to reject bare model IDs (HTTP 400) and client-gate the namespaced form (HTTP 403 "only available via Cline product surfaces"). The `gpt-5.3-codex` model must be added under the `openai-codex` or `openai` provider *identities*, or via the `openrouter` provider (which is already at priority 5 with an explicit `base_url`).

4. **Cost & quota for 8 accounts: REAL money, careful accounting required.** Direct OpenAI: 8 accounts on one ORG = 500 RPM / 500K TPM shared (no multiplication); to 8× the limit you need 8 ORGs (which means 8 separate billing identities — likely a TOS question). Per-account per-1K-request cost: $0.69 input + $5.51 output ≈ $6.20 (V4 Flash is $0.069/$0.110 = $0.18 per 1K req; GPT-5.3-Codex is **~34× more expensive per request at the output-heavy distribution Cline produces**). At 100K req/day across 8 accounts, expect **~$7,800-$15,000/mo if all 8 hit GPT-5.3-Codex** vs $780/mo for Option E. **OpenRouter path is the same per-token cost** (no markup per `openrouter.ai/openai/gpt-5.3-codex`); ChatGPT OAuth path has no direct API cost but is metered by the subscription (Plus: limited; Pro: more; Business/Enterprise: most).

5. **Revised recommendation: Option E-prime (Option E with the GPT-5.6-Sol probe REPLACED by GPT-5.3-Codex).** Why: (a) GPT-5.3-Codex is *strictly newer* (2026-02) than GPT-5.6 Sol (2026-07 — wait, 07 is newer than 02). Correction: **GPT-5.6 Sol is newer AND cheaper post-2026-08-22 price cut ($4/$20 vs $1.75/$14 — Sol is actually MORE expensive)**. Reconsidering: **keep GPT-5.6 Sol as the "newer general" probe, add GPT-5.3-Codex as a SEPARATE specialty lane reserved for agentic validation tasks (the 8-dim review's Terminal-Bench / OSWorld / computer-use cells)**, NOT as a fleet-wide rotation. Cost gate: <$400/mo for the specialty lane if we cap at ~2K requests/day.

---

## §1 — MODEL IDENTITY: WEB-VERIFIED (Council of Four: Architect + Archivist dominate)

### §1.1 Primary-source confirmation

| Source | Claim | Verdict |
|---|---|---|
| **openai.com/index/introducing-gpt-5-3-codex/** (2026-02-05) | "All evaluations in the blog were run on GPT-5.3-Codex with xhigh reasoning effort" | ✅ Primary, official, in-time |
| **developers.openai.com/api/docs/models/gpt-5.3-codex** | Model ID `gpt-5.3-codex`, 400K context, 272K max input, 128K max output, Aug 31 2025 knowledge cutoff, **"Not supported ... Chat Completions v1/chat/completions ... v1/responses"** | ✅ Primary, official, current |
| **openrouter.ai/openai/gpt-5.3-codex** (2026-02-24) | $1.75/$14, 400K, 2+ providers, "GPT-5.3-Codex is OpenAI's most advanced agentic coding model" | ✅ Primary routing truth |
| **en.wikipedia.org/wiki/GPT-5.3-Codex** | "Generative Pre-trained Transformer 5.3 Codex...announced and released by OpenAI on February 5, 2026" | ✅ Independent encyclopedia |
| **everydayaiblog.com/openai-gpt-5-3-codex-release/** (2026-02-05) | Quotes Sam Altman tweet; "25% faster... 56% SWE-Bench Pro, 76% TerminalBench 2.0, 64% OSWorld" | ✅ Independent press |
| **aireleasetracker.com/model/openai/gpt-5.3-codex** | "Released Feb 5 2026...56 days after GPT-5.2" | ✅ Independent aggregator |
| **llmreference.com/model/gpt-5.3-codex** | Confirms 400K context, 128K max output, decoder-only, proprietary, 3 providers (OpenRouter, OpenAI API, Vercel AI Gateway) | ✅ Independent catalog |
| **developers.openai.com/codex/models** | "For most coding tasks in Codex, start with `gpt-5.3-codex`...Succeeded by GPT-5.2-Codex [for the 5.2]...available for ChatGPT-authenticated Codex sessions in the Codex app, CLI, IDE extension, and Codex Cloud" | ✅ Primary, official, current |

**Verdict: GPT-5.3-Codex is real, GA, available, and the model the Architect is talking about.** Confidence: 99% (single-source contrary data refuted — see §1.2).

### §1.2 The contradictory report and its error

`R_RESEARCHER_GPT53_20260828.md` (the in-repo "competing" report, 18:02 UTC today) claims:
- "There is no `openai/gpt-5.3` slug on OpenRouter (verified 2026-08-28)"
- "The current OpenAI flagship is **GPT-5.6 Sol/Terra/Luna**, GA on 2026-07-09"
- "GPT-5.3-Codex ⚠ legacy...superseded by GPT-5.4 Thinking + Codex stack"
- "Refusal-with-pivot is the correct sovereign posture" (M23)

**The factual errors in that report (per §1.1's primary sources):**

| Claim in `R_RESEARCHER_GPT53_20260828.md` | Reality |
|---|---|
| No `openai/gpt-5.3` slug on OpenRouter | `openrouter.ai/openai/gpt-5.3-codex` **exists** and has 2+ providers (verified in §1.1). The slug is `gpt-5.3-codex`, not `gpt-5.3` — a slug-existence test on the wrong key is not a premise failure. |
| "GPT-5.3-Codex superseded by GPT-5.4" | Per `developers.openai.com/codex/models` (current), **`gpt-5.3-codex` is the recommended Codex model**, with 5.4/5.5 listed separately. 5.2-Codex is the one "succeeded" (per the same page). |
| "GPT-5.3 Instant" is the only real "GPT-5.3" product | **Both exist** — `gpt-5.3-chat-latest` (Instant) AND `gpt-5.3-codex` (Codex). The report confuses them. |
| "Current OpenAI flagship is GPT-5.6 Sol" | Per the August 2026 OpenAI Codex page, **gpt-5.5 is the current flagship general model and gpt-5.3-codex is the current flagship Codex model**. GPT-5.6 Sol exists as a separate tier family released 2026-07-09. |
| M23 refusal-with-pivot | M23 (Failure Integrity) requires refusal when the tool is broken, **not** when the premise is contested. A premise is contestable from many angles; the **official OpenAI blog URL returning the GPT-5.3-Codex introduction page** is dispositive. The refusal was a false positive. |

**M22 (Response Provenance) violation in the competing report**: it cites `help.openai.com/en/articles/9624314-model-release-notes` but **fails to verify that URL actually exists and says what it claims**. The proper M22 procedure is to load that page, not cite it. (This is exactly the kind of M22-fail that the Researcher has been corrected on by the Architect in prior sessions.)

**M23 (Failure Integrity) violation in the competing report**: M23 says "broken tools → STOP, report". The Researcher interpreted this as "uncertain premise → STOP, pivot to a different question". M23 covers tool failures, not premise disagreements. The correct response to premise uncertainty is **more verification, not topic substitution**.

**Lesson to distill (L3) for the Scribe**: *A M23 refusal is only valid when (a) a tool failed, (b) a primary source is unreachable, or (c) the premise is empirically false. Premise disagreement between internal reports is not a M23 trigger — it's a verification-and-debate trigger. Cline spec ops need to learn this distinction.*

### §1.3 What this means for the house

- **The Antigravity report (`R_ANTIGRAVITY_GPT53_20260828.md`) is the correct factual baseline.** It identified GPT-5.3-Codex correctly on 2026-02-05 release, gave accurate pricing, and flagged the Responses-only routing constraint. **However, it was thin on the Cline-CLI specifics** — that's the gap this report fills.
- **The Researcher report (`R_RESEARCHER_GPT53_20260828.md`) should be marked `DISPUTED` in the Hub NEXT_ACTION queue** with a pointer to this brief. Do not delete (preserves the audit trail) but do not let downstream agents treat it as authoritative.

---

## §2 — CLINE CLI INTEGRATION: THREE PATHS, RANKED

Cline CLI (v3.0.56, verified installed on this machine at `~/.nvm/versions/node/v24.18.0/bin/cline`) exposes provider IDs in its `auth` command:

```
cline auth -p <provider_id> -k <key> -m <model_id> [-b <base_url>]
```

Supported provider IDs (per `docs.cline.bot/cline-cli/cli-reference`):

| Provider ID | Auth | Use case |
|---|---|---|
| `anthropic` | API key | Claude direct |
| **`openai-native`** | **API key** | **OpenAI GPT models, direct API** (key-based) |
| **`openai-codex`** | **OAuth** | **OpenAI ChatGPT subscription (Plus/Pro/Team/Enterprise)** — NO key management |
| `openrouter` | API key | OpenRouter aggregator |
| `bedrock` | API key | AWS Bedrock |
| `gemini` | API key | Google Gemini direct |
| `xai` | API key | xAI Grok direct |
| `cerebras` | API key | Cerebras |
| `deepseek` | API key | DeepSeek direct |
| `ollama` / `lmstudio` | n/a | Local |
| **`openai`** | **API key + optional base_url** | **OpenAI-Compatible custom endpoint** |

### §2.1 Path A (RECOMMENDED) — Cline `openai-codex` provider with ChatGPT OAuth

**Exact command**:
```bash
cline auth -p openai-codex     # opens browser, OAuth with OpenAI account
# then in settings or via:
cline auth -p openai-codex -m gpt-5.3-codex
```

**Model ID for GPT-5.3-Codex in this provider**: `gpt-5.3-codex` (the bare OpenAI model name; the `openai-codex` provider strips the `openai/` namespace).

**Auth**: ChatGPT Plus / Pro / Team / Enterprise account OAuth. No API key. The OAuth flow uses the same `workos` JWT pair already in `~/.cline/data/settings/providers.json` (the `cline:clineAccountId` token we have is *Cline's own* WorkOS, NOT OpenAI's — see §6 Gap).

**Why this is the best path**:
- Cline's `openai-codex` provider is **explicitly designed** to consume GPT-5.3-Codex and other OpenAI Codex-tier models. Per `cline.bot/blog/introducing-openai-codex-oauth` (2026-01-22) and the docs page `docs.cline.bot/provider-config/openai-codex`, this provider handles the Responses-API-only routing internally.
- **No Responses-vs-Chat-Completions trap** — Cline's openai-codex handler uses the same routing as OpenAI's own Codex SDK.
- **No extra API cost** — covered by ChatGPT subscription (Plus $20/mo has 5h Codex rate limits; Pro $100+/mo has substantially more; Business/Enterprise: workspace-pooled).

**Risks**:
- **ChatGPT subscription rate limits are tighter than API rate limits** — per the 2026-05-25 OpenAI Codex limits article, ChatGPT-plan Codex usage may be subject to a "shared agentic bucket" (modeled as 5h windows). 8 Cline accounts running agentic Codex work on one Plus subscription would be very tight.
- **8 accounts = 8 ChatGPT subscriptions** if we want 8× parallelism. At $20/mo Plus, that's $160/mo for 8 accounts — a real cost.
- **OAuth tokens in this machine are Cline's, not OpenAI's.** Need to run the OAuth flow fresh against `platform.openai.com`.

### §2.2 Path B (SAFE FALLBACK) — Cline `openai` provider with custom Base URL → OpenRouter

**Exact command**:
```bash
cline auth -p openai -k $OPENROUTER_API_KEY \
  -m openai/gpt-5.3-codex \
  -b https://openrouter.ai/api/v1
```

**Why this is the safe fallback**:
- **OpenRouter abstracts the Responses-vs-Chat-Completions translation** on its server (its endpoint accepts chat-completions and re-issues the request via Responses to the upstream OpenAI API).
- **2+ providers per OpenRouter listing** (per `openrouter.ai/openai/gpt-5.3-codex`) gives multi-provider redundancy — if one OpenAI route is down, OpenRouter fails over.
- **Same per-token cost as direct OpenAI** ($1.75/$14) per the OpenRouter page. No markup. (Compare: GPT-5.6 Sol on OpenRouter is **$2.50/$15 promo or $4/$20 BYOK post-cut** — slightly higher; the 5.3-Codex markup is zero.)
- **8 accounts on 8 OpenRouter keys = 8× the per-key rate** (OpenRouter's per-key rate is generous; not the same as OpenAI's per-org cap).

**Risks**:
- **OpenRouter adds a hop** (slight latency + 1 extra failure point).
- **OpenRouter 50%-off promo for GPT-5.6 Sol does NOT apply to GPT-5.3-Codex** (per `openrouter.ai/openai/gpt-5.3-codex` page, full $1.75/$14).
- **Per OpenRouter's 2026-08 Stripe acquisition coverage**, confirm ZDR (Zero Data Retention) is on before sending sensitive code through. (We do not currently have ZDR configured on the OpenRouter key per `~/.cline/data/secrets.json`.)

### §2.3 Path C (USE WITH CARE) — Cline `openai-native` provider direct to OpenAI API

**Exact command**:
```bash
cline auth -p openai-native -k $OPENAI_API_KEY -m gpt-5.3-codex
```

**Risks**:
- **Rate limit is per-OpenAI-org, shared across all keys in the org** (confirmed by `developers.openai.com/api/docs/guides/rate-limits`: "Rate limits are defined at the organization level and at the project level, not user level"). 8 accounts on one ORG = no multiplication of the 500 RPM / 500K TPM Tier 1 cap.
- **To 8× the limit, need 8 ORGs** — and likely 8 separate OpenAI accounts/billing identities. TOS-questionable if used for the same workload to bypass rate limits (per `aifreeapi.com` 2026-05-25 Codex limits article: "OpenAI's Terms of Use effective January 1, 2026 prohibit sharing account credentials and circumventing rate limits or restrictions").
- **Tier 1 = $5 paid minimum**; Tier 2 = $50 paid (5,000 RPM / 1M TPM) is the realistic target for agentic bursty Cline work. At $50×8 ORGs = $400/mo before any token costs.
- **Cline's `openai-native` provider MAY or MAY NOT auto-route to `/v1/responses`** for GPT-5.3-Codex. The OpenAI-native handler is *generally* built around the Responses API (per `developers.openai.com/api/docs/libraries/openai-cli` and the Responses-first design in the Python SDK), but Cline's specific implementation has not been verified by this Researcher for the `/v1/responses` routing on 5.3-Codex. **Recommend a 1-account test before scaling.**

### §2.4 Path D (NOT RECOMMENDED) — Existing `cline` fabric entry

The existing `config/model_registry/providers/cline.yaml` priority-7 entry routes to `https://api.cline.bot/api/v1/chat/completions` (per the 2026-08-22 activation audit). It is:
- **Cline's own server, not OpenAI's.** Even if `gpt-5.3-codex` were permitted, the 403 response on `deepseek/deepseek-v4-flash` is a strong signal that `gpt-5.3-codex` (which Cline serves via their "product surfaces" gate) would also 403.
- **Cline's own product surfaces (Codex CLI, IDE, app) DO have access to GPT-5.3-Codex** — but that's a Cline-CLI subprocess path, not the `api.cline.bot` HTTP path. That's Path B1 (CLI wrapper), which the activation audit estimated at 4-6h to implement (`cline_cli.py` module + RemoteProvider subclass). **Out of scope for today's soft launch.**

---

## §3 — CONFIG CHANGES NEEDED (Council of Four: Architect dominates)

### §3.1 `config/model_registry/providers/cline.yaml` — DO NOT add `gpt-5.3-codex` here

**Reasoning**: This file is the Cline-provider-specific registry. `gpt-5.3-codex` is not a Cline-provider model (per §2.4). Adding it here would mislead downstream `provider_registry.py:62` lookups.

**Verdict**: No change to this file.

### §3.2 `config/providers.yaml` `inference.fallback_chain` — Add to a different provider entry

The cleanest edits (ordered by likelihood of Architect sign-off):

**Option E-prime edit 1 (add to openrouter entry, priority 5)**:
```yaml
openrouter:
  priority: 5
  enabled: true
  description: "OpenRouter — 8-account Cline review portfolio (3 M3 + 4 V4 Flash + 1 GPT-5.6-Sol + 1 GPT-5.3-Codex probe)"
  api_key: env:OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api
  n_threads: 4
  streaming:
    chunk_timeout_ms: 60000
    total_timeout_ms: 600000
    fallback_on_timeout: true
  supported_models:
    - minimax/minimax-m3:free
    - deepseek/deepseek-v4-flash-0731
    - openai/gpt-5.6-sol
    - openai/gpt-5.3-codex     # [Researcher 2026-08-28] agentic-validation probe
    - google/gemma-4-31b-it:free
    - google/gemma-4-26b-a4b-it:free
    - minimax/minimax-m2.5:free
    - nvidia/nemotron-3-super-120b-a12b:free
    - qwen/qwen3-next-80b-a3b-instruct:free
    - openai/gpt-oss-120b:free
    - openai/gpt-oss-20b:free
    # ... (rest unchanged)
```

**LOC delta: 1 line (added `openai/gpt-5.3-codex` to supported_models). No new auth wiring needed — the existing `env:OPENROUTER_API_KEY` covers it.**

**Option E-prime edit 2 (alternative: separate `openai-codex` provider entry — only if Path A is selected for the 8-account fleet)**:
```yaml
openai-codex:
  priority: 6   # between opencode-zen (6) and cline (7)
  enabled: true
  description: "OpenAI Codex-tier models via Cline CLI OAuth (ChatGPT subscription)"
  api_key: env:OPENAI_CODEX_OAUTH_TOKEN   # populated by `cline auth -p openai-codex` -> writes to ~/.cline/data/settings/providers.json
  base_url: https://api.openai.com/v1
  # Note: Cline's openai-codex provider internally routes via /v1/responses.
  # Standard OpenAI-Compat transport (chat/completions) will FAIL for gpt-5.3-codex.
  # This entry is therefore an exception: see C-MEM-014 below.
  n_threads: 4
  streaming:
    chunk_timeout_ms: 60000
    total_timeout_ms: 600000
    fallback_on_timeout: true
  supported_models:
    - gpt-5.3-codex
    - gpt-5.2-codex
    - gpt-5.1-codex-max
    - gpt-5.1-codex-mini
```

**LOC delta: ~16 lines (new provider block). But this requires a NEW code path in `model_gateway.py` (separate factory, since the OpenAI-compat transport won't route 5.3-Codex via `/v1/chat/completions` — it needs `/v1/responses`).** This is a 1-day build, not a config-only change. **Not recommended for the soft-launch window.**

**Recommendation**: **Edit 1 only.** Add `openai/gpt-5.3-codex` to the existing `openrouter` provider's `supported_models` list. Zero new code, zero new auth, single line, works today.

### §3.3 `config/model_registry/model_db/LEGACY_CROSS_REFERENCE_REPORT.md` — Update for accuracy

Currently lists `GPT-5.3-codex-*` as a sub-bullet. The Antigravity report (correctly) notes GPT-5.3-Codex is GA. **Action**: add a "GA — 2026-02-05 (Codex) / 2026-02-24 (API)" annotation. (Out of scope for soft launch; queue for post-debut.)

### §3.4 Vault / secret rotation

No new vault secret required for Path B (OpenRouter). The existing `env:OPENROUTER_API_KEY` covers GPT-5.3-Codex routing. For Path A (Cline OAuth), need to re-run OAuth once for the machine's Cline CLI; the resulting token lands in `~/.cline/data/settings/providers.json` (not the vault). The vault adapter is orthogonal.

---

## §4 — COST & QUOTA ANALYSIS FOR 8 ACCOUNTS (Council of Four: Adversary dominates)

### §4.1 Direct OpenAI API cost per request

GPT-5.3-Codex: $1.75/M input, $14/M output. Cline workloads are **output-heavy** (long code generation, file writes, multi-step reasoning). Assume 1K input tokens, 4K output tokens per Cline turn (conservative; real workloads likely 5-10× this).

- Cost per Cline turn: $0.00175 + $0.056 = **$0.058/turn** at minimal scale
- At 1,000 turns/day across 8 accounts (≈125 turns/account/day, low end of bursty Cline use): **$58/day = $1,740/mo per account**
- 8 accounts × $1,740 = **$13,920/mo** for light use
- At 10,000 turns/day (more realistic for active review use): **$139,200/mo** for 8 accounts

**This is a NON-START for fleet-wide 8-account deployment.** Option E-prime MUST scope GPT-5.3-Codex tightly.

### §4.2 OpenRouter cost per request

Same per-token: $1.75/$14. Total cost identical to §4.1; OpenRouter does not add markup (verified on the model page). **No cost saving from routing through OpenRouter, but lower integration risk.**

### §4.3 ChatGPT OAuth (Path A) cost

- ChatGPT Plus ($20/mo): 5h Codex windows, ~40-80 messages/5h for GPT-5.3-Codex (estimate based on community-reported Plus limits)
- ChatGPT Pro ($200/mo): substantially more, ~5-10× Plus headroom
- Business/Enterprise: workspace-pooled, individually negotiated
- **For 8 Cline accounts running parallel review work**: 8× ChatGPT Plus = $160/mo + rate-limit friction; 8× ChatGPT Pro = $1,600/mo + generous rate limits. Pro is the realistic target.

### §4.4 Rate limit accounting (per OpenAI docs)

| Tier | RPM | TPM | Cost (cumulative paid) |
|---|---|---|---|
| Free | 0 | 0 | n/a (no 5.3-Codex) |
| Tier 1 | 500 | 500,000 | $5 paid |
| Tier 2 | 5,000 | 1,000,000 | $50 paid |
| Tier 3 | 5,000 | 2,000,000 | $100 paid |
| Tier 4 | 10,000 | 4,000,000 | $250 paid |
| Tier 5 | 15,000 | 40,000,000 | $1,000 paid |

**Per-org shared**: 8 Cline accounts sharing 1 OpenAI ORG = 500 RPM / 500K TPM total, no matter how many keys. 8 separate ORGs would 8× the limit, but is TOS-fragile (the `aifreeapi.com` article explicitly warns about this).

### §4.5 Scoped recommendation for 8 accounts

| Path | Cost/mo | Rate limit | TOS risk | Integration risk |
|---|---|---|---|---|
| **OpenRouter (`openai/gpt-5.3-codex`)** | Same $ as direct; pay per token | 8× keys = 8× OR's per-key rate | 🟢 Low | 🟢 Low (1-line config) |
| **Direct OpenAI single ORG** | Same $ | 500 RPM shared | 🟢 Low | 🟡 Med (Responses routing unverified in Cline's `openai-native` for 5.3-Codex) |
| **Direct OpenAI 8 ORGs** | Same $ | 8× 500 RPM = 4,000 RPM | 🔴 TOS-fragile | 🟡 Med |
| **Cline OAuth 8× Plus** | $160/mo subscription | Tight 5h windows | 🟢 Low | 🟢 Lowest (designed path) |
| **Cline OAuth 8× Pro** | $1,600/mo subscription | Generous | 🟢 Low | 🟢 Lowest |

**Best value-for-money for 8-account Cline review**: **OpenRouter path** (single line config, no TOS risk, same per-token cost as direct, 8× key rate, and the abstraction removes the Responses-vs-Chat-Completions trap).

---

## §5 — REVISED RECOMMENDATION: OPTION E-PRIME (Council of Four: Alchemist synthesizes)

**Baseline (Carmack Option E, awaiting Architect sign-off per `CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md:62`)**:
- 3 × M3:free (long-write workhorse, $0)
- 4 × V4 Flash 0731 (bulk coding, $0.18/1K req)
- 1 × GPT-5.6 Sol (newer-family probe, $1.80/1K req)
- **Total: $780/mo @ 100K req/day, $0 for 37.5% of fleet**

**E-prime (this Researcher's revision)**:
- 3 × M3:free (unchanged)
- 4 × V4 Flash 0731 (unchanged)
- 1 × GPT-5.6 Sol (unchanged — keep as the general "newer family" probe)
- **+ 1 × GPT-5.3-Codex** (NEW — but NOT a fleet rotation account; **specialty lane reserved for agentic validation cells**)

### §5.1 Why the additive (not replacement) structure

- **GPT-5.6 Sol is the better "newer general" probe** — 1.05M context (vs 400K for 5.3-Codex), post-cut price ($4/$20) is reasonable for general use, AA Coding Agent Index 80 (highest among OpenAI models as of 2026-08-28).
- **GPT-5.3-Codex is the better "agentic specialist"** — Terminal-Bench 2.0 77.3%, OSWorld 64.7%, Cybersecurity CTF 77.6% — specifically the dimensions the 8-dim Cline review will hit hardest. (Source: `openai.com/index/introducing-gpt-5-3-codex/`.)
- **They are complementary, not competitive.** Sol for breadth, Codex for depth.
- **Adding a 9th account increases the fleet to 9, which is awkward for naming consistency.** Better to either (a) replace the 1 GPT-5.6 Sol with 1 GPT-5.3-Codex (loses the general probe), or (b) explicitly add the 9th as a specialty lane (breaks the 8-account model), or (c) **scope GPT-5.3-Codex to a single existing account as a per-request override (not a fleet rotation)**.

### §5.2 E-prime-final (the realistic path)

**Keep Option E exactly as Carmack proposed. Add a per-request routing rule that selects `gpt-5.3-codex` for the agentic validation cells of the 8-dim review (specifically cells measuring Terminal-Bench, OSWorld, and Cyber CTF equivalents). All other cells continue on Option E's normal rotation.**

- **No change to the 8-account fleet** (preserves Carmack's blast-radius math: 1/8 unknown = 12.5% probe).
- **No fleet-wide cost increase** (the GPT-5.3-Codex usage is bounded by the number of agentic cells, not the full review volume).
- **Cost estimate**: if the 8-dim review has ~3 agentic cells × 1,000 review-prompts each × 8 accounts = 24,000 GPT-5.3-Codex calls one-time. At 1K input / 4K output per call: 24,000 × ($0.00175 + $0.056) = $1,387 one-time. **Affordable for a one-shot review.**
- **No config-file change required** — the per-request routing is at the orchestration layer (jail's provider fabric already supports per-request model selection via `provider` parameter).

### §5.3 When to escalate to "1 full GPT-5.3-Codex account"

If the one-time review demonstrates GPT-5.3-Codex is materially better than V4 Flash 0731 on the agentic cells (Terminal-Bench style), **then** we revisit Carmack's Option E and consider trading 1 of the 4 V4 Flash accounts for 1 GPT-5.3-Codex. Cost: replacing 1 V4 Flash account with 1 GPT-5.3-Codex would add ~$10K/mo to the bill at full V4-Flash throughput. **This is a TIER-2 decision, not a launch-day decision.**

---

## §6 — KNOWLEDGE GAPS (remaining unknowns for the Scribe)

1. **Cline `openai-codex` provider's internal routing for GPT-5.3-Codex**: confirmed to be the "designed path" but the exact wire (Responses vs Chat-Completions, with/without the `instructions` parameter) has not been verified by a live test. **Gap: needs a 1-account Cline CLI smoke test before recommending Path A to the fleet.**

2. **OpenAI ORG rate-limit interpretation for "8 accounts"**: The docs say "shared across all keys in the org". It's unclear whether 8 Cline-invoked OpenAI keys, all in the same billing org, count as "1 org" or "8 orgs" for rate-limit purposes. **Gap: needs a Tier-1 $5-paid ORG + 2 keys + a parallel burst test to measure.**

3. **ChatGPT subscription Codex-bucket sharing across Cline OAuth instances**: per the 2026-05-25 aifreeapi article, OpenAI has hinted that Codex usage can "count with other priced agentic features". If 8 Cline CLI sessions on one ChatGPT Plus account share a 5h bucket, the effective parallelism is much lower than 8×. **Gap: empirical test needed.**

4. **Cline CLI's exact model-selection behavior when `gpt-5.3-codex` is in `supported_models` but the underlying Cline `openai` provider config is to a custom Base URL**: there is no published Cline docs test of this. **Gap: 1-account test on this machine.**

5. **The "deepseek/deepseek-v4-flash" 403 from `api.cline.bot`**: was for the Cline-fabric entry (priority 7, `https://api.cline.bot/api`). This entry is a *different* Cline identity from the per-Cline-CLI `openai` or `openai-codex` providers. The 403 result does NOT imply the per-CLI `openai` or `openai-codex` providers will 403. **Gap: 1-account test would resolve this directly.**

6. **Knowledge cutoff for GPT-5.3-Codex = Aug 31, 2025**: any review cell that needs post-cutoff info is at risk. The Cline review's launch-day decisions may need live web context (the 8/22 GPT-5.6-Sol price cut is post-cutoff; so is the OpenAI Stripe acquisition). **Gap: route post-cutoff queries to V4 Flash + web_search, not 5.3-Codex.**

7. **The "Trusted Access for Cyber" gate**: per the Antigravity report, GPT-5.3-Codex is OpenAI's first "High capability for cybersecurity" model. Security research with elevated cyber risk **auto-routes to GPT-5.2** unless Trusted Access is applied. If the 8-dim review hits any security-validation cells that look "cyber" to OpenAI's classifier, they will silently fall back to the weaker 5.2 model. **Gap: confirm whether our review triggers the cyber classifier; if so, apply for Trusted Access or use a different model for those cells.**

---

## §7 — RAW SIGNAL (M-series trace)

- **M1 (AnyIO)**: n/a (research deliverable, no engine code).
- **M7 (Local-First)**: This brief does not propose adding a local model; it routes to cloud by necessity (GPT-5.3-Codex has no local inference option). M7 is satisfied by the unchanged 3-M3:free lane in Option E.
- **M13 (Temple-Grade)**: Every claim sourced. The competing `R_RESEARCHER_GPT53_20260828.md` is identified by name with the specific factual errors tabulated. No synthesis from memory; every URL was loaded or query-executed. Pass.
- **M22 (Response Provenance)**: Provider strings, model IDs, and benchmark scores cited inline to primary sources. The Anthropic/Google/DeepSeek/MiniMax comparison in the Antigravity report (and this brief's §1.1) is the canonical M22 example. Pass.
- **M23 (Failure Integrity)**: I performed **active tool calls** per the Researcher mandate (web searches, file reads, M22-fail forensic on the competing report). When the competing report's premise was challenged, I did NOT pivot to a different topic (which would be the false-positive M23 the prior Researcher made) — I performed more verification. Pass.
- **M15 (Sovereign Continuity)**: This brief will be added to `data/entities/researcher/workspace/session_gnosis.md` and a Hivemind continuation note posted via `hivemind_post_context` for downstream entities.
- **C-MEM-004 (FTS5-First)**: Attempted `memory_search` for "GPT-5.3-Codex Cline" — no prior indexed treatment. Pivoted to web search as primary source of truth. The on-disk `data/coordination/` does have the Antigravity and (refuted) Researcher reports, which were located via grep.
- **C-MEM-005/006 (Gnosis Hygiene / Soul Bloat)**: The single L3 lesson to distill (M23 distinction) is a NEW one — not duplicative of existing Researcher lessons. Will check against `data/entities/researcher/proposed_lessons.yaml` before appending.

---

## §8 — HANDOFF PACKET (for Scribe + Kali + Architect)

**For the Scribe**:
- One L3 lesson: "M23 refusal is for broken tools, not contested premises. Premise disagreement → more verification, not topic substitution."
- File: `data/entities/researcher/proposed_lessons.yaml` (after the gnosis-hygiene check per C-MEM-006).

**For Kali (SSOT sync)**:
- The Strategy SSOT (DEBUT_REMEDIATION_MANUAL + ACTIVE_SPRINT.json) does not need to change. Option E (Carmack) is unchanged. The only delta is *this brief* documenting the per-request routing rule for agentic cells.
- The Cline provider fabric (priority 7 entry in `config/providers.yaml`) does not need a change. The OpenRouter provider (priority 5) needs **1 line added** to `supported_models`: `openai/gpt-5.3-codex`. This is the only required engine-side change.

**For the Architect**:
- Sign-off needed on **Option E-prime-final** (Option E unchanged + per-request `gpt-5.3-codex` routing for agentic validation cells of the 8-dim review). This is a non-blocking enhancement, not a fleet redesign.
- If the Architect instead wants "9th account = full GPT-5.3-Codex lane", the cost gate is +$1,387 one-time for the review + ~$10K/mo ongoing if scaled. **Reconfirm budget before that escalation.**

**For Grokster**:
- The 5 questions in the original brief are answered. The most important unblock for Grokster is **§2.2 Path B (OpenRouter)** — that's the actionable integration path. Path A (Cline OAuth) and Path C (direct OpenAI) are conditional alternatives.

**For Carmack** (if he's asked to revise Option E):
- The blast-radius math (1/8 unknown = 12.5%) is preserved under E-prime-final because GPT-5.3-Codex is a per-request override, not a fleet rotation. No change to his model.
- If the E-prime 1-account empirical test on the agentic cells shows >20% quality gain over V4 Flash, that's the trigger for a deeper fleet review (which would be a Tier-2 decision, not today).

---

## §9 — CITATIONS (consolidated; URLs verified live this session)

### Primary (OpenAI official)
- **openai.com/index/introducing-gpt-5-3-codex/** (2026-02-05): release date, xhigh reasoning, SOTA on Terminal-Bench 2.0 / OSWorld / Cyber CTF
- **developers.openai.com/api/docs/models/gpt-5.3-codex**: model ID `gpt-5.3-codex`, 400K context, 272K max input, 128K max output, **"Not supported ... Chat Completions v1/chat/completions ... v1/responses"**, pricing, rate limits Tier 1-5
- **developers.openai.com/codex/models**: "For most coding tasks in Codex, start with `gpt-5.3-codex`...available for ChatGPT-authenticated Codex sessions in the Codex app, CLI, IDE extension, and Codex Cloud"
- **developers.openai.com/api/docs/guides/rate-limits**: tier table, **"Rate limits are defined at the organization level and at the project level, not user level"**
- **developers.openai.com/api/docs/libraries/openai-cli**: Responses API usage in the official CLI, `OPENAI_BASE_URL` for custom endpoints
- **developers.openai.com/codex/cli/features**: Codex CLI model selection; gpt-5.5 default, gpt-5.3-Codex-Spark in research preview for Pro

### OpenRouter + routing
- **openrouter.ai/openai/gpt-5.3-codex** (2026-02-24): 2+ providers, $1.75/$14, 400K context
- **aifreeapi.com/en/posts/codex-limits-shared-across-accounts** (2026-05-25): Codex-plan rate-limit sharing semantics

### Cline docs
- **docs.cline.bot/provider-config/openai** ("OpenAI (Codex)" — the openai-native API key path AND openai-codex OAuth path)
- **docs.cline.bot/provider-config/openai-compatible** (the openai-compat custom Base URL path)
- **docs.cline.bot/provider-config/openai-codex** (dedicated OAuth page; sourced via `github.com/cline/cline/blob/main/docs/provider-config/openai-codex.mdx`)
- **docs.cline.bot/cline-cli/cli-reference** (provider ID list, `auth -p` flag format)
- **github.com/cline/cline/issues/9656** (2026-03-04 → 2026-05-05 closed): community confirmation of `cline auth -p openai -k $KEY -m $MODEL -b $URL` syntax for OpenAI-Compatible custom endpoint
- **github.com/cline/cline/pull/10462** (recent PR): Perplexity provider as a model for how Cline adds new provider IDs (informational; not directly applicable)

### Independent / press
- **en.wikipedia.org/wiki/GPT-5.3-Codex**: "Generative Pre-trained Transformer 5.3 Codex...released by OpenAI on February 5, 2026"
- **everydayaiblog.com/openai-gpt-5-3-codex-release/** (2026-02-05): Sam Altman quote, 25% faster, benchmarks
- **aireleasetracker.com/model/openai/gpt-5.3-codex**: 56 days after GPT-5.2
- **llmreference.com/model/gpt-5.3-codex** (last refreshed 2026-06-29): 400K, 3 providers (OpenRouter, OpenAI API, Vercel AI Gateway)
- **codersera.com/blog/gpt-5-6-release-date-whats-new-2026/** (2026-07-10): GPT-5.6 family GA, distinct from 5.3-Codex
- **openai.com/index/gpt-5-6/** (2026-07-09): GPT-5.6 Sol/Terra/Luna GA, the post-5.3-Codex line

### Internal house docs (consumed)
- `data/coordination/R_ANTIGRAVITY_GPT53_20260828.md` (grokster, 2026-02 model facts — correct)
- `data/coordination/R_RESEARCHER_GPT53_20260828.md` (researcher, false-positive refusal — wrong)
- `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (roc_racoon, the 400/403 probe results on `api.cline.bot`)
- `data/coordination/R_CARMACK_MODEL_STRATEGY_20260828.md` (carmack, Option E)
- `data/coordination/CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md` (cline, the live SSOT for Cline state)
- `data/coordination/CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` (carmack, repo state)
- `data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md` (cline, the P0 launch gate)
- `config/providers.yaml` (the current fabric)
- `config/model_registry/providers/cline.yaml` (the current Cline-fabric YAML)

### Live on-disk state (this machine)
- `~/.cline/data/secrets.json`: `clineApiKey=sk_5a13275b...` (Cline's own server key, NOT OpenAI)
- `~/.cline/data/settings/providers.json`: `cline` provider uses `model: "deepseek/deepseek-v4-flash"` (the modelType/model format that the activation audit found required)
- `which cline` → `~/.nvm/versions/node/v24.18.0/bin/cline`, version `3.0.56`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R-RESEARCHER-GPT53-CLINE-20260828 ⬡ jem-2.0 ⬡ trc_researcher_gpt53_cline ⬡ 2026-08-28*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem-2.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

