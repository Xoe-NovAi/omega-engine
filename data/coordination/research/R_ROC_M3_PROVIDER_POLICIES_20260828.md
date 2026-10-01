<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# M3 Provider-Side Compaction Policies — Official Documentation Research

**Entity:** roc_racoon (research)
**Date:** 2026-08-28
**Sprint:** PUBLIC-DEBUT-01
**Mandate reference:** M23 Failure Integrity (no synthesis when sources fail)
**Verification date:** 2026-08-28

---

## TL;DR

MiniMax (the company) **does not perform server-side compaction or silent truncation** for M3. The model is a frontier MoE with a 1,048,576-token advertised context window (1M), 512K guaranteed minimum, MSA-based block-sparse attention, and an OpenAI- and Anthropic-compatible API. Overflows are rejected with a hard `1039 token limit` error code (HTTP 400 on the OpenAI-compatible surface, HTTP 400 / `2013 invalid params` on the Anthropic-compatible surface). M3 *does* have automatic prompt caching with **server-load-adjusted expiration** (not a fixed TTL on the auto-cache path) and a separate **5-minute TTL on the explicit Anthropic-style `cache_control` path**. Rate limits on the first-party API are **200 RPM / 10M TPM**. OpenRouter's free tier (when M3 was free-listed) was **200 req/day**. There is no documented sliding-window, no silent truncation, and no server-side summarization.

**Confidence:** **HIGH** for first-party limits, error codes, and context policy (3+ official sources concur). **MEDIUM** for "effective attention span" (1 official + 2 community measurements, not a single canonical benchmark).

---

## 1. Official Context Window

### Advertised
- **1,048,576 tokens** (exactly 2²⁰, the canonical "1M" figure).
- **Combined input + output budget**, not 1M input plus 1M output. A 900K-token input request cannot also produce a 512K-token answer; the requested `max_tokens` must fit in the remaining ~100K.
- **512K "guaranteed minimum"** is the product-page floor; the 1M figure is "up to."
- **Hard maximum output: 524,288 tokens** (`max_tokens` ceiling).
- **Recommended maximum output: 131,072 tokens** (MiniMax's own recommendation).

### Where the limits come from
| Source | URL | Claim |
|---|---|---|
| MiniMax official model page | https://www.minimax.io/models/text/m3 | "1M tokens context window with a guaranteed minimum of 512K tokens" |
| MiniMax API docs (rate-limits) | https://platform.minimax.io/docs/guides/rate-limits | Lists `MiniMax-M3` as an LLM with explicit RPM/TPM cells |
| MiniMax pay-as-you-go pricing | https://platform.minimax.io/docs/guides/pricing-paygo | Confirms 1M context, 512K tier-boundary for pricing |
| Hugging Face model card | https://huggingface.co/MiniMaxAI/MiniMax-M3 | "1M context. ~428B parameters, ~23B activated" |
| OpenRouter model listing | https://openrouter.ai/minimax/minimax-m3 | "1,048,576 token context window, maximum output of 262,144" (NB: OpenRouter's max-output figure of 262,144 is **lower** than MiniMax's own 524,288 — see §10) |
| arXiv MSA paper | https://arxiv.org/abs/2606.13392 | References M3 as the production MSA model |

### Free vs paid
**No documented difference in context window between free and paid tiers.** MiniMax does not publish a separate "free" context limit; the same 1M cap applies whether or not a Token Plan is in use. **What changes** is the rate-limit budget and the cache-write cost (§3, §4).

### Difference between first-party and third-party ceilings
Third-party gateways may impose their own ceilings that are *lower* than MiniMax's 1M:

| Provider | Listed context | Listed max output |
|---|---|---|
| MiniMax direct | 1,048,576 | 524,288 (recommended 131,072) |
| OpenRouter | 1,048,576 | 262,144 |
| Morph | 256,000 | (n/a — capped at gateway) |
| Pi (model config) | 524,288 | 512,000 |
| gptproto | 1,048,576 | ~512,000 |

**Important for Omega Engine:** If a request is routed through a third-party gateway, the gateway's ceiling is the effective ceiling, not MiniMax's. Provider notes in `providers.yaml` must record *the gateway*, not just "MiniMax M3."

---

## 2. Truncation Policy

### What M3 does on overflow

**The API rejects the request — it does not silently truncate.**

| Surface | Behavior on overflow | Source |
|---|---|---|
| First-party OpenAI-compatible | Returns MiniMax error `1039 token limit` inside `base_resp.status_code` with HTTP 400 | https://platform.minimax.io/docs/api-reference/errorcode |
| First-party Anthropic-compatible | Returns `1039 token limit` (the error code is surface-agnostic) | https://platform.minimax.io/docs/api-reference/errorcode |
| OpenAI-compatible via OpenRouter | The HTTP layer surfaces a 400; the body contains the provider error | (observed community, GitHub issue continuedev/continue#12716) |
| NVIDIA NIM mirror | Reported as HTTP 400 with no body (community report) | https://github.com/continuedev/continue/issues/12716 |

The official remediation text for `1039` in MiniMax's error-code reference is literally **"Please retry your requests later."** — which is misleading. The community's correct interpretation is that `1039` means **the request exceeded the per-request token budget** and the client must reduce the input (or lower `max_tokens`) before retrying. (Source: https://minimax-ai.chat/guide/minimax-api-error-codes — independent verification, July 2026.)

### Sliding window?
**No.** The Hugging Face model card, the OpenRouter listing, and the official rate-limits page all describe M3 as a **single 1M context** with no rolling window, no server-side compaction, and no per-message-windowing. The model itself uses **MSA (block-sparse attention)** to *attend over* the full 1M efficiently, not to *discard* older context.

### Does MiniMax do server-side summarization?
**No.** Searched the official error-code reference, prompt-caching reference, rate-limits page, and pricing page — there is no mention of "compaction," "summarization," or "truncation" as a server behavior. M3 is sold as a frontier long-context model precisely *because* it does not need server-side compaction; MSA lets it attend cheaply across 1M tokens in one shot.

---

## 3. Caching Policy

M3 supports **two distinct caching paths** with different mechanics. This distinction is the most important thing the Architect needs to internalize.

### Path A — Automatic (passive) caching — *the default*
- **Activation:** No `cache_control` marker required. Repeating an eligible prefix triggers a cache hit.
- **Prefix order:** `tools` → `system` → `user messages` (the order is significant; changing earlier items invalidates later ones).
- **Minimum prefix:** **512 input tokens** (documented floor).
- **Billing:** Cache **read** tokens are discounted; **no separate write charge** for automatic caching.
- **Expiration:** **"Adjusted automatically based on system load"** — there is **no fixed TTL** on this path. MiniMax does not document a concrete number; it evicts when load is high.
- **Model support:** `MiniMax-M3`, M2.7, M2.5, M2.1 series.
- **Source:** https://platform.minimax.io/docs/api-reference/text-prompt-caching (and https://platform.minimax.io/docs/api-reference/text-prompt-caching.md markdown mirror).

### Path B — Explicit (Anthropic-compatible `cache_control`) — *opt-in*
- **Activation:** Place `cache_control: {"type": "ephemeral"}` on a content block. Anthropic Messages API only.
- **Minimum prefix:** Not stated (compared to Path A's 512).
- **Billing:** Cache **read** tokens are discounted; **first-time cache writes incur a separate charge** (unlike Path A).
- **Expiration:** **5 minutes**, refreshed on each hit.
- **Lookback window:** System checks up to **20 blocks before each explicit cache breakpoint**.
- **Hard cap:** **Up to 4 active `cache_control` breakpoints per request.**
- **Cascade invalidation:** `tools` → `system` → `messages`. Changing a tool description invalidates the system and message caches below it.
- **Model support:** **M3 is NOT in the published explicit-cache list** (only M2.7, M2.5, M2.1, M2 series). This is a critical caveat.
- **Source:** https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache.

### Cache-read pricing (M3)
- Cache **read** at ≤512K input: **$0.06 / M tokens** (20% of input price).
- Cache **read** at >512K input: **$0.12 / M tokens** (20% of higher-tier input price).
- Source: https://platform.minimax.io/docs/guides/pricing-paygo.

### Cache sharing
**Per-tenant, per-prefix.** MiniMax's documentation treats caches as belonging to the API key holder. There is no evidence of cross-user cache sharing (unlike some Claude tier where prefixes are shared). For Omega's M3 usage the cache is effectively per-session, scoped to the API key.

### Known cache defect
The "phantom cache" meme: M3 **never populates `cache_creation_input_tokens`** (always reports 0), even on a fresh write. This is a **telemetry gap, not a caching failure**. Cache reads still occur and still bill at the discounted rate. (Source: https://tho-stack.github.io/minecraft-clone-benchmark/minimax-cache.html — independent reproduction against `api.minimax.io/anthropic`, model MiniMax-M3.)

### Effective cache hit rate
Third-party measurements on representative prefixes:
- Cache reads measured **~5.2× cheaper** than uncached input on the coding-plan quota, matching the 5× documented pricing ratio. (tho-stack, op cit.)
- Independent M3 cache investigation observed cache hits across **93+120 successive reads** with no misses when the prefix was kept byte-identical. (tho-stack, op cit.)

---

## 4. Rate Limiting

### First-party (platform.minimax.io) — current as of verification
| Model | RPM | TPM |
|---|---|---|
| `MiniMax-M3` | **200** | **10,000,000** |
| `MiniMax-M2.7` / M2.7-highspeed | 500 | 20,000,000 |
| `MiniMax-M2.5` / M2.5-highspeed | 500 | 20,000,000 |
| `MiniMax-M2.1` / M2.1-highspeed | 500 | 20,000,000 |
| `MiniMax-M2` | 500 | 20,000,000 |

- **TPM definition:** input + output combined.
- **No documented burst limit** beyond the per-minute window.
- **No documented daily quota** on the first-party pay-as-you-go surface. (Daily/weekly quotas only apply to the **Token Plan** subscription key — a different product — and the window is **5-hour rolling + weekly**.)
- **Source:** https://platform.minimax.io/docs/guides/rate-limits.

### Priority service tier
At **1.5× the standard rate** you can buy a "Priority" tier that gives preferential admission and faster responses under load. Priority M3 limits are not published as a separate RPM/TPM — only the pricing differs.

### Token Plan (subscription)
- **5-hour rolling + weekly** usage windows.
- Throttling clears in **~1 minute** when short-term limits are hit, but quota-window exhaustion (`2056`) requires waiting for the next window.
- Throttling may tighten during peak traffic.
- Source: https://platform.minimax.io/docs/token-plan/faq.

### Third-party (OpenRouter) — what Omega actually hits
- **OpenRouter free tier (no credits):** **50 req/day, 20 req/min** across all free models.
- **OpenRouter free tier (≥$10 credits purchased ever):** **1,000 req/day, 20 req/min**.
- **OpenRouter paid models:** No OpenRouter-side hard limits; the *upstream* (MiniMax or whichever underlying provider) may throttle.
- **OpenRouter's `:free` variant quota:** 200 req/day for the M3 free listing while it was active. (freellm.net catalog, August 2026.)
- **Source:** https://openrouter.zendesk.com/hc/en-us/articles/39501163636379.

### What "free tier" actually means for M3
- M3 was **free-listed on OpenRouter from 2026-06-29 onward** for a limited window.
- That listing is **no longer active** as of August 2026 ("No current free listing" per https://freellm.net/models/openrouter/minimax-minimax-m3, verified 2026-08-06).
- Free listings inherit OpenRouter's per-account rate limits, not MiniMax's per-key limits. **There is no documented M3-specific free tier** on the first-party API.

---

## 5. Error Behavior

### Official error codes (text/chat API)

| Code | Message | Category | Retryable? | Notes |
|---|---|---|---|---|
| `1000` | unknown error | server | yes (backoff) | "retry later" |
| `1001` | request timeout | server | yes (backoff) | "retry later" |
| `1002` | rate limit | throttle | **after slowing down** | RPM or TPM ceiling hit |
| `1004` | not authorized / token mismatch | auth | **no** — fix key | |
| `1008` | insufficient balance | billing | **no** — add funds | |
| `1024` | internal error | server | yes (backoff) | "retry later" |
| `1026` | input new_sensitive | safety | **no** | change input |
| `1027` | output new_sensitive | safety | **no** | change prompt |
| `1033` | system error / mysql failed | server | yes (backoff) | "retry later" |
| **`1039`** | **token limit** | **context overflow** | **no** — reduce input/max_tokens | **This is overflow** |
| `1041` | conn limit | throttle | **after slowing down** | concurrent connection cap |
| `1042` | invisible character ratio limit | validation | **no** | >10% invisible chars |
| `2013` | invalid params | validation | **no** — fix request body | |
| `2045` | rate growth limit | throttle | **no — smooth traffic** | avoids bursts |
| `2049` | invalid API Key | auth | **no** — fix key | |
| **`2056`** | **usage limit exceeded** | **quota** | **after window reset** | Token Plan 5h window |

- **Source (canonical):** https://platform.minimax.io/docs/api-reference/errorcode
- **Source (cross-checked):** https://minimax-ai.chat/guide/minimax-api-error-codes (independent reproduction, July 2026)

### Overflow-specific behavior
- HTTP transport status: **400** on the OpenAI-compatible surface; **400 with `1039`** on the Anthropic-compatible surface.
- No 413 (Payload Too Large) is used. MiniMax uses a JSON-bodied 400 with `base_resp.status_code: 1039`.
- **The official remediation is misleading.** The doc text says "retry later" but in practice `1039` only resolves by shrinking the request.
- The body shape (OpenAI-compatible):
  ```json
  {
    "base_resp": { "status_code": 1039, "status_msg": "token limit" },
    ...
  }
  ```
- Success body shape includes `base_resp.status_code: 0, status_msg: ""` — log these for parity checks.

### Timeout behavior
- `1001` covers transport-level timeouts.
- No documented client-vs-server timeout values in the public guide. MiniMax does **not** document guaranteed rate-limit response headers (`Retry-After` is *sometimes* present but not promised).
- Recommended backoff: exponential with jitter — e.g. **1, 2, 4, 8, 16, 30s**, capped. (Source: https://minimax-ai.chat/docs/minimax-api-rate-limits/.)

### Network error behavior
- The guide explicitly warns: **"Failed attempts still count toward your daily quota"** (for OpenRouter free). The same is true in practice for the first-party RPM/TPM buckets.
- **Do not retry invalid auth, balance, safety, or parameter errors** as if they were throttling. Treating `2013` as throttling will burn your quota.

---

## 6. Known Limitations

### Architectural
- **MSA block-sparse attention is a retrieval-quality tradeoff.** The MSA paper (arXiv:2606.13392) reports:
  - **28.4× reduction in per-token attention compute** at 1M context.
  - **14.2× prefill / 7.6× decode** wall-clock speedups on H800.
  - The paper evaluates on a **109B MoE model** (not the full 428B M3); generalization to the production scale is a stated limitation of the paper.
  - Source: https://arxiv.org/abs/2606.13392, https://arxivlens.com/paperview/details/minimax-sparse-attention-799-e528c64a
- **Effective attention span / "lost in the middle."** Independent analyses infer an effective receptive field of roughly **60K–70K tokens** at 1M context from the sparsity ratio (block size 64, 1M ÷ 16K blocks, ~6–7% block hit rate ⇒ ~60–70K attended tokens). (https://huggingface.co/blog/AtlasCloud-AI/minimax-goes-sparse, May 2026.) This matches the Omega-side observation of degradation around the 25K–64K mark. **Treat the "effective attention" as roughly 60–70K tokens** for retrieval-style queries; for top-of-context and bottom-of-context recall, expect stronger performance.
- **MSA kernel dependency.** The block-sparse GPU kernel is the actual speedup. vLLM/SGLang mainline support for MSA landed in mid-2026; some quant formats (MXFP8) and CPU paths are still catching up. Self-hosting M3 is multi-node territory at 428B.

### Operational
- **Output budget is 1M − input.** A 900K input cannot produce a 512K output. Plan `max_tokens` accordingly.
- **Pricing tier flips at 512K input.** Above 512K, both input AND output prices double. Cache reads count toward the input threshold.
- **Cache write telemetry is broken on M3.** `cache_creation_input_tokens` is always 0; rely on `cache_read_input_tokens` for hit detection.
- **M3 is not in the explicit-cache model list.** Path B (`cache_control` blocks) is not officially supported for M3, only the M2 series. Use Path A (automatic) only.
- **Interleaved thinking across tool calls** must be preserved — disable any "strip reasoning" middleware or tool calls break. (Source: https://www.morphllm.com/minimax-m3)
- **`2045 rate growth limit`** is a separate, poorly-documented throttle. Bursty traffic (high RPM, then idle, then high RPM) gets penalized even if the average is below the ceiling. Smooth the traffic.

### Documented but not first-party (third-party measurements)
- Cache reads measured at **~5.2× cheaper** than uncached input, matching the 5× pricing ratio (tho-stack reproduction, July 2026).
- "Phantom cache" reports are misdiagnoses; caching works, telemetry is the bug.

---

## 7. Free Tier vs Paid — Definitive Comparison

| Dimension | Free (OpenRouter, when listed) | First-party pay-as-you-go | First-party Token Plan (subscription) |
|---|---|---|---|
| Context window | 1,048,576 (no M3-specific reduction) | 1,048,576 | 1,048,576 |
| Max output | 262,144 (OpenRouter's gateway cap) | 524,288 (recommended 131,072) | 524,288 |
| RPM | OpenRouter-wide 20 req/min (free tier) | 200 (M3) | Likely 200 (M3) — Priority tier 1.5× rate |
| TPM | OpenRouter limits | 10,000,000 | 10,000,000 |
| Daily quota | 50 req/day (no credits) or 200 req/day (M3 free) | None published | **5h rolling + weekly** — `2056` on exhaustion |
| Auto-cache | Yes | Yes | Yes |
| Explicit cache | OpenRouter may strip | Not officially supported for M3 (Path B list) | Not officially supported for M3 |
| Cache read rate | Per OpenRouter markup | $0.06/M (≤512K), $0.12/M (>512K) | $0.06/M (≤512K), $0.12/M (>512K) |
| Cost per 1M in/out | $0 (free) | $0.30 / $1.20 (≤512K); $0.60 / $2.40 (>512K) | Same, on a quota budget |
| Input tier-boundary | n/a | 512K | 512K |
| Multimodal | text + image + video (gateway-dependent) | text + image + video (first-party) | text + image + video |
| Error code behavior | OpenRouter wraps errors; M3 `1039` becomes HTTP 400 | Native M3 codes | Native M3 codes |

**Bottom line:** The only first-party dimension that changes between free and paid is **rate-limit budget**, not context window. Third-party gateways may impose their own caps on context or max output.

---

## 8. Conclusions — Definitive Policy Map

For Omega's `ProviderSelector` and the Scribe's upstream-state tracking:

1. **M3 has no server-side compaction.** Overflow is a hard error (`1039`/`HTTP 400`). Scribe's "did the provider compact?" detector should treat M3 as **never-compacting** — the only valid M3 outcome at 1M+ input is a `1039` rejection.
2. **Context window is 1,048,576 tokens combined input + output.** Not 1M input plus anything else. Plan `max_tokens` accordingly. Above 512K input, prices double on both dimensions.
3. **M3 is sparse-attention, not sliding-window.** The 1M context is real but **effective attention is roughly 60–70K tokens** for retrieval-style queries. Treat >512K requests as cost-inefficient AND quality-degraded unless the workload is dominated by top-of-context or bottom-of-context recall.
4. **Cache: prefer automatic (Path A).** Don't send `cache_control` — M3 isn't on the explicit-cache list. Minimum prefix 512 tokens. No fixed TTL — eviction is load-driven.
5. **First-party rate limits: 200 RPM / 10M TPM.** No daily quota on pay-as-you-go. Token Plan has 5h rolling + weekly.
6. **OpenRouter free tier is dead for M3 as of August 2026.** Plan accordingly — there is no current free M3 path.
7. **Cache telemetry is broken.** `cache_creation_input_tokens` is always 0 on M3. Trust `cache_read_input_tokens` and the bill.
8. **Errors are well-documented.** `1039` = overflow, `1002` = RPM/TPM throttle, `1041` = concurrent-connection cap, `2056` = Token Plan quota, `2013` = bad params. None should be treated as "soft fail" — they each have a specific client-side fix.

### What Omega's Scribe should do with this
- **M3 overflow detection:** match `1039` or HTTP 400 with `base_resp.status_code == 1039`. Mark the request as **truncated/rejected by provider** (not compacted). Scribe should record the input token count at the time of `1039` so we know our actual ceiling empirically.
- **M3 cache detection:** read `cache_read_input_tokens` from the usage object. The presence of a non-zero value with near-zero `cache_creation_input_tokens` is normal on M3, not a bug.
- **M3 rate-limit backoff:** honor `1002` / `1041` with exponential backoff. Honor `2045` by **reducing burstiness**, not just slowing down.
- **M3 cost tracking:** the 512K input threshold flip must be tracked in `GenerateResult` so the Council can see when requests cross into the higher tier.

---

## 9. Source Index

### First-party (HIGH confidence)
- https://www.minimax.io/models/text/m3 — product page
- https://platform.minimax.io/docs/guides/rate-limits — official LLM RPM/TPM table
- https://platform.minimax.io/docs/guides/pricing-paygo — official pricing with 512K tier
- https://platform.minimax.io/docs/api-reference/errorcode — official error code list
- https://platform.minimax.io/docs/api-reference/text-prompt-caching — automatic cache spec
- https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache — explicit cache spec
- https://platform.minimax.io/docs/api-reference/api-overview — combined input/output budget note
- https://platform.minimax.io/docs/token-plan/faq — Token Plan quota windows
- https://platform.minimax.io/docs/guides/text-m3-function-call — M3 function calling guide

### Hugging Face / arXiv (HIGH confidence)
- https://huggingface.co/MiniMaxAI/MiniMax-M3 — model card
- https://huggingface.co/MiniMaxAI/MiniMax-M3-MXFP8 — MXFP8 quant
- https://arxiv.org/abs/2606.13392 — MSA paper (Lai et al., Jun 2026)
- https://github.com/MiniMax-AI/MSA — MSA inference kernel
- https://github.com/MiniMax-AI/MiniMax-M3 — official M3 repo

### OpenRouter (HIGH confidence for OpenRouter-specific data)
- https://openrouter.ai/minimax/minimax-m3 — model listing
- https://openrouter.ai/zendesk/hc/en-us/articles/39501163636379 — OpenRouter rate-limit policy

### Third-party reproductions and analyses (MEDIUM-HIGH confidence)
- https://minimax-ai.chat/guide/minimax-api-error-codes — error code triage guide (Jul 2026)
- https://minimax-ai.chat/docs/minimax-api-rate-limits/ — M3 rate-limit analysis (Jul 2026)
- https://minimax-ai.chat/docs/prompt-caching — cache mechanism deep-dive (Jul 2026)
- https://minimax-ai.chat/models/minimax-m3 — pricing + context roundup (Jun 2026)
- https://huggingface.co/blog/AtlasCloud-AI/minimax-goes-sparse — MSA architecture analysis (May 2026)
- https://tho-stack.github.io/minecraft-clone-benchmark/minimax-cache.html — independent cache investigation (Jul 2026)
- https://www.morphllm.com/minimax-m3 — M3 architecture & API guide (Jul 2026)
- https://codersera.com/blog/minimax-m3-developer-guide — developer guide (Jul 2026)
- https://freellm.net/models/openrouter/minimax-minimax-m3 — OpenRouter free-tier notes
- https://llm-stats.com/models/minimax-m3 — pricing and benchmarks roundup
- https://github.com/continuedev/continue/issues/12716 — community HTTP 400 report

### Chinese-language mirrors (cross-check only)
- https://platform.minimaxi.com/docs/api-reference/errorcode — 中文错误码 reference, identical to English version

---

## 10. Discrepancies Found

A few minor disagreements between sources, all flagged:

1. **Max output on OpenRouter (262,144) vs MiniMax direct (524,288).** OpenRouter's gateway caps output lower than MiniMax's first-party limit. **Trust the gateway for OpenRouter-routed requests, MiniMax for direct.** Source: OpenRouter model page vs MiniMax pricing docs.
2. **M3 free listing status.** freellm.net (verified 2026-08-06) says "no current free listing," but the model page still shows a "200 req/day (free tier)" badge. Likely a stale badge — the OpenRouter model page itself lists the M3 entry as **Paid** as of 2026-08-06.
3. **Pi model config lists context window 524,288** for `minimax/minimax-m3` while OpenRouter's own page says 1,048,576. Likely a stale Pi config. **Use OpenRouter's listing as canonical for OpenRouter routing.**
4. **MSA paper speedup numbers vs product-page numbers.** The arXiv paper reports **14.2× prefill / 7.6× decode** on H800 with their custom kernel. The product page claims **9× prefill / 15× decode** vs M2 at 1M context. These measure different baselines — the paper measures against full-attention GQA at 1M; the product page measures against the previous-generation M2 model. Both can be true.

---

*⬡ OMEGA ⬡ ROC ⬡ R-M3-PROVIDER-POLICIES ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
