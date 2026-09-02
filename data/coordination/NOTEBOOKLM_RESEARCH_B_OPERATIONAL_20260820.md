<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# NOTEBOOKLM RESEARCH — SUBAGENT B (NLG-B) · OPERATIONAL GAPS
**Closing**: GAP-10 (session persistence), GAP-7 (token density), GAP-9 (Pro vs free cost-benefit)
**Date**: 2026-08-20
**Agent**: researcher (subagent of Kali / Transcendent Oversoul)
**Workspace lock**: `notebooklm-research` (held by Kali)
**Product name note**: NotebookLM was renamed **Gemini Notebook** in July 2026 — same product, same limits [blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook). "NotebookLM" used throughout for search-artifact continuity.

---

## 1. SESSION PERSISTENCE DESIGN (GAP-10)

### 1.1 Cookie taxonomy & lifetimes
NotebookLM has **no public OAuth surface** — all libraries authenticate by carrying Google session cookies extracted from a real browser sign-in [github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md). Two clocks govern validity:

| Cookie class | Role | Server-side lifetime | Notes |
|---|---|---|---|
| `*SID` / `__Secure-1PSID` | Long-lived identity | Months → ~1 year (effectively never expires for active accounts) | The on-disk `Expires` stamp is irrelevant to server-side validity |
| `*SIDTS` (`__Secure-1PSIDTS`) | Rotating "freshness" partner | **Recommended rotation cadence ~600 s** (Google self-reports `["identity.hfcr",600]` on `RotateCookies`); **not a hard TTL** | A *superseded* value is rejected within ~30 min; an *un-superseded* stale value works for hours-to-days on a stable IP |
| `SIDCC` / `*SIDCC` | Per-request session continuity | ~5 min sliding window | Ephemeral; not load-bearing for auth |
| `OSID` / `__Secure-OSID` | Per-product (notebooklm.google.com) | Re-issued each sign-in | — |

Key finding: **cookie-set completeness matters more than freshness.** Google rejects a cookie set missing `__Secure-1PSIDTS` together with any other cookie, even though removing `__Secure-1PSIDTS` alone is recoverable [github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md).

Independent corroboration: `jacob-bd/notebooklm-mcp` documents cookies as "typically lasting 2–4 weeks… not auto-refreshed, must be re-extracted when expired," with `is_expired()` defaulting to a 168-hour (1-week) threshold [deepwiki.com/jacob-bd/notebooklm-mcp/3.3-token-management](https://deepwiki.com/jacob-bd/notebooklm-mcp/3.3-token-management). For managed/Workspace accounts the default web session length is **14 days** [knowledge.workspace.google.com/admin/security/set-session-length-for-google-services](https://knowledge.workspace.google.com/admin/security/set-session-length-for-google-services).

### 1.2 Refresh cadence
- **Active rotation**: a direct `POST https://accounts.google.com/RotateCookies` is the durable primitive — Google's dedicated unsigned rotation endpoint, ~100% success in field captures, no DBSC challenge [github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md).
- **CSRF tokens** (valid for minutes) are auto-refreshed on every request failure; **session IDs** re-extracted at MCP startup [b-lab.team/en/content/b6ebeaa0-1f9c-4d96-8cd3-4811c217565c](https://b-lab.team/en/content/b6ebeaa0-1f9c-4d96-8cd3-4811c217565c).
- **Critical failure mode**: a cookie *snapshot* is **no longer a viable CI credential**. Any other active client (workstation, second CI job, keepalive) supersedes the value you shipped within ~10 min; the grace period then decides how long your copy limps on. The durable answer is a credential that does not rotate — ship `master_token.json` and mint a fresh session per run [github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md).

### 1.3 Bot-detection risk (Patchright vs Playwright)
- **Standard Playwright leaks** (`navigator.webdriver = true`, CDP runtime leaks, command-line-flag tells, Chromium TLS/JA3 mismatch) — trivially flagged by Cloudflare/DataDome [rtila.net/t/bypassing-strict-anti-bot-systems-in-2026-standard-playwright-vs-patchright/89](https://rtila.net/t/bypassing-strict-anti-bot-systems-in-2026-standard-playwright-vs-patchright/89).
- **Patchright** is a source-level patched Playwright fork that closes CDP leaks, neutralizes `navigator.webdriver`, and (with `channel='chrome'`) launches real Chrome for authentic TLS/JA3 alignment. "With the right setup, Patchright currently is considered undetectable" [github.com/Kaliiiiiiiiii-Vinyzu/patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright); [webscraping.app/tools/patchright](https://webscraping.app/tools/patchright).
- **Caveat — Tier 3 still bites**: Patchright passes Cloudflare BotFight and basic checks, but is *variable* against Cloudflare Enterprise/Turnstile and Akamai Bot Manager v4, and **fails behavioral/TLS-consistency analysis** [scrapewise.ai/blogs/playwright-stealth-2026](https://scrapewise.ai/blogs/playwright-stealth-2026); [blog.send.win/patchright-vs-playwright-stealth-complete-comparison-alternatives-2026/](https://blog.send.win/patchright-vs-playwright-stealth-complete-comparison-alternatives-2026/).
- **Relevance to NotebookLM**: NotebookLM is reached via *undocumented internal RPC/APIs*, not a public web scraper path, so the dominant risk is **Google's own account-abuse model** (bot-account detection, cross-account linkage), not a third-party anti-bot wall. See GAP-9 ToS evidence: a user's account was disabled with "created or used with multiple other accounts to violate Google's policies… created by a computer program or bot" after a single automated request [github.com/teng-lin/notebooklm-py/issues/228](https://github.com/teng-lin/notebooklm-py/issues/228).

### 1.4 V-1 Vault credential design — recommendation
1. **Do NOT store rotating cookie snapshots as the primary credential.** They die in minutes-to-hours and create a fragile refresh loop. Store instead a **`master_token.json`** (the durable, non-rotating credential) and mint a per-run session via `RotateCookies` + `notebooklm auth` [github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/auth-cookie-lifecycle.md).
2. **Vault schema**: per-account record = `{ account_id, master_token (encrypted at rest), last_rotate_ts, cookie_set_complete_flag, associated_profile }`. Encrypt with the Omega-Vault KMS; never plaintext on disk.
3. **Refresh cadence in Vault**: schedule an OS timer (systemd/cron) that calls `RotateCookies` every **≤600 s** while a session is active, and re-mints from `master_token` on any auth-401. Treat `__Secure-1PSIDTS` supersession as the trigger, not the `Expires` field.
4. **Completeness guard**: on every load, validate the full cookie set (presence of `__Secure-1PSIDTS` + ≥1 sibling). Reject partial sets before use.
5. **Bot-evasion**: if a browser is ever needed (initial `master_token` capture, headless re-auth), use **Patchright with `channel='chrome'`**, persistent `user_data_dir`, and a stable residential IP — never datacenter egress, which collapses the lifetime further [proxyhat.com/blog/patchright-deep-dive-undetected-playwright-1](https://proxyhat.com/blog/patchright-deep-dive-undetected-playwright-1).
6. **One account per Vault slot**; never share a cookie set across concurrent workers (supersession race).

---

## 2. TOKEN DENSITY VERDICT (GAP-7)

### 2.1 Verdict: PARTIALLY SOURCED — lower bands supported, upper bands are unsourced extrapolation
The strategy doc's table — **"5–15 Excellent, 15–30 Good, 30–50 Degrading, 50+ Poor"** — is **not fully sourced**. Evidence:

- **Lower bands (5–15 / 15–30) ARE supported.** Community consensus puts the retrieval sweet spot at **"around 5 to 25 sources per topic"**; quality degrades when "unrelated sources compete for context" [notebooklm-to-pdf.com/blog/notebooklm-source-limits](https://notebooklm-to-pdf.com/blog/notebooklm-source-limits). "More sources is always better" is explicitly **false** — "retrieval quality degrades as the source set gets noisier" [markdownconverters.com/learn/ai-file-uploads/notebooklm](https://markdownconverters.com/learn/ai-file-uploads/notebooklm). Batching by tight topic "improves answer quality because each source carries more signal" [posttosource.com/blog/notebooklm-source-limit](https://www.posttosource.com/blog/notebooklm-source-limit).
- **Upper bands (30–50 Degrading / 50+ Poor) are NOT directly sourced.** Observed behavior: response quality becomes "noticeably more generic as a notebook's source count climbs into the several-dozen range on complex, cross-cutting questions" — driven by a *broader source pool giving the model a wider space to draw a general answer from instead of a specific, well-cited one*, **not a hard count cliff** [sourclip.com/blog/notebooklm-source-limit](https://www.sourclip.com/blog/notebooklm-source-limit). Degradation is a **gradient tied to topic coherence and noise**, not a step function at 30 or 50.
- **Context-window context**: NotebookLM chat runs on Gemini's full **1-million-token** context across all plans (rolled out Jan 2026, +50% user-satisfaction on larger source sets) — so raw capacity is not the limiter; *relevance signal-to-noise* is [blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-custom-personas-engine-upgrade](https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-custom-personas-engine-upgrade).

### 2.2 Reconciliation with the doc's "40–50 recommendation"
The strategy doc's separate **"40–50 sources per notebook" recommendation contradicts its own quality table** (which rates 30–50 as "Degrading" and 50+ as "Poor"). Both cannot hold. Resolution:
- The 40–50 figure conflates *"max useful before the 50-source hard cap"* with *"optimal."* It is **wrong as an optimality claim.**
- **Corrected recommendation**: target **5–25 high-relevance, single-topic sources** per notebook (the sourced sweet spot). Use **source labels as a context filter** ("ground this answer ONLY in the [LABEL] subset") to narrow retrieval within larger notebooks and recover quality [notebooklm-guide.com/notebooklm-source-organization/](https://notebooklm-guide.com/notebooklm-source-organization/).
- Only approach 40–50 if sources are **extremely tightly related** AND you rely on label-scoped queries; otherwise split into topic notebooks (notebooks cannot query each other — attach several to one Gemini conversation for cross-notebook synthesis) [notebooklm-to-pdf.com/blog/notebooklm-source-limits](https://notebooklm-to-pdf.com/blog/notebooklm-source-limits).
- **Action for the strategy doc**: replace the unsourced "40–50" recommendation with "5–25 (sweet spot), up to 50 only when tightly topic-coherent + label-scoped." The 5–15/15–30 bands stay; re-label 30–50 as "Degrading (noise-driven, not a hard cliff)" and 50+ as "At hard cap — split recommended."

---

## 3. COST-BENEFIT TABLE (GAP-9)

### 3.1 Real pricing & Deep Research quotas (2026)
Sources: [felloai.com/notebooklm-pricing](https://felloai.com/notebooklm-pricing/), [felloai.com/is-notebooklm-free](https://felloai.com/is-notebooklm-free/), [gemini.google/us/subscriptions](https://gemini.google/us/subscriptions).

| Option | Cost/mo | Deep Research quota | Notebooks / Sources | Ban risk |
|---|---|---|---|---|
| **8 × Free (Standard)** | $0 | **10/mo each = 80/mo total** | 100 / 50 each | **HIGH** (see 3.3) |
| **1 × Plus** | $4.99 | 3/day ≈ 90/mo | 200 / 100 | Low (paid, legit) |
| **1 × Pro (Google AI Pro)** | $19.99 | **20/day ≈ 600/mo** | 500 / 300 | **Low** (paid, legit) |
| **2 × Pro** | $39.98 | 40/day ≈ 1,200/mo | 500 / 300 each | Low |
| **1 × Ultra 20TB** | $99.99 | 75/day ≈ 2,250/mo | 500 / 500 | Low |

### 3.2 Family-sharing multiplier (legitimate)
Google AI Pro supports **Google One Family Group sharing with up to 5 additional members (6 total)**; each member (18+) gets their **own independent quota** and own account — not a shared login [discuss.ai.google.dev/t/is-it-allowed-for-ai-pro-subscription-user-to-family-share-antigravity](https://discuss.ai.google.dev/t/is-it-allowed-for-ai-pro-subscription-user-to-family-share-antigravity-and-switch-between-family-account/130034); [one.google.com/intl/en_us/about/google-ai-plans](https://one.google.com/intl/en_us/about/google-ai-plans/); [dev.to/amals367/20-subscription-6-people-google-one-ai-family-sharing-explained-65a](https://dev.to/amals367/20-subscription-6-people-google-one-ai-family-sharing-explained-65a). Practical ceiling: **1 Pro sub → up to 6 × 20 DR/day = 120 DR/day (~3,600/mo)** if shared with a household. (Note: older Google One AI Premium family sharing was scheduled to end June 2025 for members, but the post-I/O-2026 "Google AI Pro" SKU explicitly restores family sharing [krater.ai/blog/ai-family-plan-share-subscription](https://krater.ai/blog/ai-family-plan-share-subscription).)

### 3.3 ToS / ban risk (the decisive factor)
- **Google ToS** permits suspension/termination if you "materially or repeatedly breach these terms," including "hiding or misrepresenting who you are" or using "automated means to access content… in violation of machine-readable instructions" [policies.google.com/terms](https://policies.google.com/terms).
- **Multiple free accounts to dodge limits = explicit ToS violation.** XDA explicitly warns: creating a second Google account "to double your free-tier limits" violates "Google's ToS [that] state you shouldn't create 'multiple accounts to misuse our services'" [xda-developers.com/dodge-notebooklm-source-limitations](https://www.xda-developers.com/dodge-notebooklm-source-limitations/).
- **Automation triggers account-disable.** A `notebooklm-py` user was disabled with "created or used with multiple other accounts to violate Google's policies… created by a computer program or bot" after one automated request [github.com/teng-lin/notebooklm-py/issues/228](https://github.com/teng-lin/notebooklm-py/issues/228).
- **8-free fleet compounds all three risks**: (a) ToS violation per account, (b) bot-detection from RPC automation, (c) cross-account linkage — Google links accounts created/used together. One ban can cascade.

### 3.4 Recommendation
**HYBRID: 1 × Google AI Pro ($19.99, ~600 DR/mo) as the primary Deep Research engine + free accounts only for non-quota-bound tasks (chats 50/day, audio 3/day, source ingestion).**

Rationale:
- **1 Pro alone delivers 7.5× the DR of the entire 8-free fleet (600 vs 80/mo) at $19.99**, with *lower* risk and *1 credential* instead of 8. The free fleet's only "advantage" ($0) is false economy once ban risk is priced in.
- Free tier's generous **50 chats/day, 3 audio/day, 10 reports/day** cover everything *except* Deep Research — so free accounts are still useful for ingestion/synthesis, just not for the 80-DR target.
- **Scale path**: if DR demand exceeds ~600/mo, add a **2nd Pro ($39.98, ~1,200/mo)** *before* ever considering a free-account fleet. Family-share the Pro (6 own-quota seats) only if a legitimate household exists.
- **Reject the 8-free fleet** for Deep Research — it is the highest-risk, lowest-yield option and contradicts NLG-A's HIGH-ban-risk finding.

---

*All factual claims cited inline. No parametric synthesis — every figure traced to a live web source. Deliverable complete; no other files modified.*
