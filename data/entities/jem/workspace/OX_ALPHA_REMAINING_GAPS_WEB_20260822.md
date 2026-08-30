<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# OX ALPHA REMAINING GAPS — WEB RESEARCH CLOSURE
**AP Token**: `AP-JEM-OXALPHA-GAPS-WEB-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_oxalpha_gaps_web ⬡ SOVEREIGN

**Date**: 2026-08-23
**Method**: M23 active-tool web research (websearch × 6 gap queries). All claims traced to fetched sources below. No parametric synthesis.
**Prior context**: `OX_ALPHA_GAP_INTEGRATION_20260822.md` (this workspace)

---

## GAP 1: Z.AI Direct Access Path — **CLOSED**

**Findings**:

| Item | Finding | Source |
|---|---|---|
| **GLM-5.3 on Z.AI direct?** | **YES** — GLM-5.3 is Z.ai's flagship on the international platform (`api.z.ai`), launched **Aug 14, 2026**, 1M ctx / 128K out, reasoning always-on (low/high/max effort), prompt caching, tools, web search. OpenAI **and** Anthropic protocols supported. | [z.ai/model-api](https://z.ai/model-api); [docs.z.ai/guides/llm/glm-5.3](https://docs.z.ai/guides/overview/quick-start); [ofox.ai/models/z-ai/glm-5.3](https://ofox.ai/models/z-ai/glm-5.3) |
| **Signup process** | Register at Z.AI Open Platform (z.ai/model-api) → top up at Billing Page (z.ai/manage-apikey/billing) → create key at API Keys page. Standard email registration documented; **no KYC requirement surfaced** in docs for API access. Usage bundles purchasable with instant activation. | [docs.z.ai/guides/overview/quick-start](https://docs.z.ai/guides/overview/quick-start) |
| **Per-token pricing** | **GLM-5.3 per-token rate NOT YET PUBLISHED** — official pricing table ends at GLM-5.2 ($1.40/M in, $0.26/M cached, $4.40/M out). Access rolling out behind safety review. Third-party aggregator OfoxAI lists `z-ai/glm-5.3` at **$1.40/M in / $4.40/M out** (via Zhipu/Volcengine providers) — treat as indicative, not official. | [emergent.sh/learn/glm-5-3-pricing](https://emergent.sh/learn/glm-5-3-pricing) (Aug 14); [developer.puter.com Z.AI pricing](https://developer.puter.com/tutorials/zai-glm-api-pricing/) (Aug 11); ofox.ai |
| **Coding Plan alternative** | GLM Coding Plan from **$18/mo Lite** ($80 Pro, $168 Max; yearly −30%). Credit multipliers for 5.3: input 6.9, cached 1.7, output 24 (per 10K units). Off-peak = 50% rate outside Mon–Fri 14:00–18:00 Singapore time. Works only inside supported coding tools (Claude Code, Cline, OpenCode, ZCode) — **not SDK/custom integrations**. | emergent.sh; [docs.z.ai/devpack](https://docs.z.ai/guides/overview/pricing) |
| **Open weights** | Promised **~2 weeks after Aug 14 launch ≈ Aug 28**, gated by safety review (cybersecurity focus cited). No checkpoint/license published yet. | emergent.sh |

**Sprint implication**: Post-free-tier continuity path exists: Ox Alpha (free, ends ~Aug 26-27) → Z.AI direct GLM-5.3 (per-token price TBD, or Coding Plan $18/mo inside OpenCode) → open weights ~Aug 28 for local GGUF quantization. This forms a **continuity ladder** rather than a cliff.

---

## GAP 2: GLM-5.3 Local Quantization Status — **PARTIAL**

**Findings**:

- **unsloth**: Has `unsloth/GLM-5-GGUF` (744B-A40B, MIT, UD-Q2_K_XL = 241GB, UD-IQ2_XXS fits 256GB Mac / 1×24GB GPU + 256GB RAM MoE-offload) — but this is **GLM-5, NOT GLM-5.3**. No unsloth GLM-5.3 GGUF found as of search date. ([huggingface.co/unsloth/GLM-5-GGUF](https://huggingface.co/unsloth/GLM-5-GGUF); [unsloth.ai/docs/models/tutorials/glm-5](https://unsloth.ai/docs/models/tutorials/glm-5))
- **bartowski**: Only legacy GLM-4-9B GGUF surfaced; no GLM-5.3 release found. ([mygguf.com](https://www.mygguf.com/models/bartowski_glm-4-9b-chat-GGUF))
- **MaliAir/GLM-5.3-MXFP4-MOE-Q8_0-GGUF & manakanemu/glm5.3**: No download-count updates surfaced; prior 0-download status unchallenged by any evidence found. Treat as **placeholder/unverified**.
- **Minimum viable VRAM**: For GLM-5 (744B): 2-bit dynamic = 241GB disk, runs on 1×24GB card + 256GB RAM via MoE offloading. GLM-5.3 size unknown until weights drop (~Aug 28); if it follows GLM-5 scale, **no viable quant fits Omega's Tier 0/1 hardware budget**. If GLM-5.3 is a smaller Air/Turbo variant (GLM-4.5-Air precedent: $0.20/M tier), a sub-100GB quant may be feasible — **unconfirmable until weights publish**.
- **Key timeline fact**: Z.ai explicitly gated open weights behind safety review, promising them ~2 weeks post-launch (**≈ Aug 28**) — i.e., **right after the Ox Alpha free tier ends**. Unsloth received day-zero access for GLM-5 and will likely repeat for 5.3.

**Verdict**: PARTIAL — no working GLM-5.3 GGUF today; credible path opens ~Aug 28 when official weights land. Sprint plan should schedule a **weights-drop watch for Aug 28** rather than assuming availability now.

---

## GAP 3: OpenRouter Batch API for stealth/ox-alpha — **PARTIAL**

**Findings** (from official Batch API Quickstart):

| Item | Finding |
|---|---|
| Endpoint | `POST https://openrouter.ai/api/beta/batches`; poll via `GET /api/beta/batches/:id` |
| Schema | Inline JSON `requests` array of `{custom_id, body}` — no JSONL upload. **Must serialize `endpoint` and `model` before `requests`** (stream-parsed; 400 if reversed) |
| Shapes | `/v1/chat/completions`, `/v1/responses`, `/v1/messages`, `/v1/embeddings` |
| Window | **24h only** (`completion_window: "24h"`) |
| Discount | "Typically billed at **50%** of standard per-token pricing" — mirrors OpenAI/Anthropic batch discounts |
| Constraints | **Text-only** — validation rejects image/audio/video/file content parts; rejects non-text output modalities |
| stealth/ox-alpha eligibility | **NOT CONFIRMED** — docs describe no per-model eligibility list. Single-provider stealth models may or may not support batch routing to the Stealth endpoint. Requires empirical probe (submit 1-request test batch) |

**Caveats for sprint**: (a) eligibility unverified — needs a live smoke test before relying on it; (b) even if eligible, batch is text-only, so **multimodal distillation vectors cannot use Batch API**; (c) 50% of $0 is still $0 during preview — discount only matters post-preview.

Source: [openrouter.ai/docs/batch-quickstart](https://openrouter.ai/docs/batch-quickstart)

**Verdict**: PARTIAL — mechanism fully documented; ox-alpha eligibility requires live probe.

---

## GAP 4: Free Tier Expiry Precision — **PARTIAL**

**Findings**:

- **OpenCode** (X, Aug 20): "Ox Alpha (stealth model) is free for the next week" → ~**Aug 27**. ([x.com/opencode/status/2090544355824038300](https://x.com/opencode/status/2090544355824038300))
- **OpenCode Go** (X, Aug 21): "free for the next 6 days" → ~**Aug 27**. Consistent.
- **OpenRouter model page**: lists $0/$0 with **NO end date published**. ([openrouter.ai/stealth/ox-alpha](https://openrouter.ai/stealth/ox-alpha))
- **AI Catchup** (Aug 22): "Treat the window as roughly one week from August 20 and expect it to close without notice." ([aicatchup.com](https://aicatchup.com/news/ox-alpha-stealth-model-free-openrouter-opencode))
- **No extension or pricing-reveal announcement found** from OpenRouter, OpenCode, or Zhipu as of Aug 23 searches.

**Best estimate**: **~Aug 26–27, timezone unspecified** (likely UTC given OpenRouter conventions). No official timestamp exists. Keep auto-disable at `2026-08-26T23:59:59Z` (conservative) — current plan stands.

**Verdict**: PARTIAL — convergent community evidence for Aug 26-27; zero official precision; no extension signals.

---

## GAP 5: Stall-Echo Community Reports — **STILL OPEN**

**Findings**:

- **No direct reports found** of truncated-output re-injection as user turns specifically on OpenRouter/Z.AI/GLM endpoints matching Omega's PLATFORM_GROUND_TRUTH_LOG entry #10 pattern.
- **Adjacent confirmed failure modes** (different signature, same family):
  - GLM 4.6 via OpenRouter returning **empty responses** after long thinking (ChatterUI #467, Oct 2025, closed-unreproducible) — upstream stream failure → empty completion, the precursor condition for stall-echo.
  - Cline v3.68.0 **max_tokens regression** breaking `z-ai/glm-5` (400 context-length errors + "empty or unparsable response", fixed PR #9633 Mar 2026) — shows GLM-family large-output requests are fragile across clients.
  - OpenRouter **middle-out/context-compression transforms silently truncating** conversation middles without notification (Reddit r/SillyTavernAI TIL thread; Message Transforms docs confirm auto-compression on ≤8k-context models).
- No provider acknowledgment of re-injection behavior found. No workaround threads found.

**Assessment**: The stall-echo phenomenon appears **under-reported or client-specific**. Omega's existing mitigations (ORACLE_STACK.md stitching-artifact rules, M25 chunk-timeout heartbeats) remain the correct defense. Recommend adding a **synthetic user-turn detector** (hash incoming user turns against own recent truncated drafts) as a cheap guard — no external fix is coming.

Sources: [github.com/Vali-98/ChatterUI/issues/467](https://github.com/Vali-98/ChatterUI/issues/467); [github.com/cline/cline/issues/9592](https://github.com/cline/cline/issues/9592); [openrouter.ai/docs message-transforms](https://openrouter.ai/docs/guides/features/message-transforms)

**Verdict**: STILL OPEN — no independent confirmation, no vendor acknowledgment; internal mitigation stands.

---

## GAP 6: Vision API Format Verification — **CLOSED**

**Findings** (SMF Clearinghouse live probe, Aug 21, 157-test run + dedicated vision probes — highest-quality evidence available):

| Probe | Result |
|---|---|
| `image_url` data URL (64×64 PNG) | ✅ **WORKS** — shapes/colors/layout correctly described; image tokens counted in prompt |
| `image_url` fetchable HTTPS PNG | ✅ **WORKS** — text "OXALPHA" on blue correctly read |
| `image_url` Wikimedia JPEG URL | ❌ HTTP 400 at OpenRouter fetch layer ("Received 400 status code when fetching image") — **fetch limitation, not blindness**; use data URLs or reliable CDNs |
| `video_url` content part | ❌ **404 "No endpoints found that support video URLs"** |
| MP4 wrapped as `image_url` | ❌ 415 (PNG/JPEG/WebP/GIF only) |

**Ruling**: The model card (`text+image+video→text`) **oversells the live route**. On OpenRouter's single Stealth endpoint: **image_url works (data URLs preferred), video_url does NOT**. SMF's explicit guidance: "Do not plan video on stealth/ox-alpha until OpenRouter lists a video-capable endpoint."

**Sprint impact**: The **video_code_reasoning distillation vector (10K tasks) is DEAD on OpenRouter route**. Reallocate that vector to image-only (UI screenshots → code fixes) or drop it. Token budget unaffected materially (10M of ~860M plan).

Sources: [smfclearinghouse.com Ox Alpha probe](https://www.smfclearinghouse.com/blog/2026-08-21-ox-alpha-openrouter-official-a/); [openrouter.ai/docs videos](https://openrouter.ai/docs/guides/overview/multimodal/videos) (confirms provider-level video gating); raw probes: github.com/smfworks/NemoKnowledgebase/tree/main/benchmarks/ox-alpha-or

**Verdict**: CLOSED — image_url yes, video_url no, empirically verified.

---

## 🚨 SURPRISE FINDING: Data Policy Contradiction (Material Update)

Multiple independent sources quoting the **live OpenRouter model page banner** report:

> "Prompts and completions for this model are **retained by the provider** and are **not used for training**; all other use is governed by the Stealth Model Terms."

(SMF Clearinghouse live probe Aug 21; explainx.ai Aug 21; glm5.app Aug 22; AI Catchup Aug 22 — all four concur.)

This **contradicts the Researcher's Stealth EULA §4 reading** ("irrevocable perpetual training license"). Two possibilities:
1. The banner reflects a **narrower commitment than the underlying Stealth Terms** (§4 may still grant broad license for "other uses" — eval, abuse monitoring, legal holds — while excluding weight-training for *this* release), or
2. Terms were amended since the July 6 version the Researcher analyzed.

**Revised compliance posture**: Retention risk stands (anonymous provider keeps logs); **training-license risk is downgraded but not eliminated** — the catch-all "Stealth Model Terms" clause preserves ambiguity. Production secrets remain forbidden (AUD-17 unchanged), but sanitized-repo work can proceed with slightly higher confidence. Flag for Verity audit: reconcile banner vs §4 before Day 3 synthetic-data generation at scale.

---

## DELTA SECTION — What Changes for the Sprint Plan

| # | Change | Triggered By | Priority |
|---|---|---|---|
| **Δ-1** | Add **Z.AI direct GLM-5.3 continuity ladder** to expiry handling: Ox Alpha (free → ~Aug 26-27) → Z.AI Coding Plan $18/mo Lite inside OpenCode (immediate paid fallback) → Z.AI per-token API (price TBD) → **GLM-5.3 open weights watch on ~Aug 28** for local GGUF quantization. Replace flat "fallback to google" with this ladder. | GAP 1 + GAP 2 | HIGH |
| **Δ-2** | **Kill video_code_reasoning distillation vector** (10K tasks); reallocate to image-only UI-screenshot→code-fix tasks using `image_url` data URLs. Never send Wikimedia-style hotlink JPEGs (fetch 400s). | GAP 6 | HIGH |
| **Δ-3** | Schedule **Batch API eligibility probe** (single-request test batch to stealth/ox-alpha) before Day 2 bulk generation; if eligible, route all text-only synthetic generation through `/api/beta/batches` (24h window, inline JSON, endpoint+model field order mandatory). Multimodal stays sync-only regardless. | GAP 3 | MEDIUM |
| **Δ-4** | Keep auto-disable at **2026-08-26T23:59:59Z** (conservative); add a daily expiry check (model page price flip from $0) since no official end timestamp exists and closure comes "without notice." | GAP 4 | MEDIUM |
| **Δ-5** | Implement **synthetic user-turn detector** in streaming pipeline (hash-match incoming user turns against own truncated drafts) — stall-echo has no external fix coming; internal guard is permanent defense. Extends ORACLE_STACK.md artifact rule #10. | GAP 5 | MEDIUM |
| **Δ-6** | Escalate **banner-vs-§4 data-policy contradiction to Verity** before Day 3 large-scale synthetic generation; document both readings in AUD-17 amendment. Training-risk downgraded, retention-risk unchanged. | Surprise finding | HIGH |
| **Δ-7** | Note: coding quality caveat — SMF scored Ox Alpha **20/30 coding with Unicode-leak SyntaxErrors** (≈, ×, →, — leaking into code; milder than GLM-5.2's 16 errors). Distillation traces must pass a **Unicode-lint filter** before LoRA training, else local Qwen3-1.7B inherits the defect. | GAP 6 (SMF data) | HIGH |

---

## Per-Gap Verdict Summary

| Gap | Verdict | Confidence |
|---|---|---|
| 1. Z.AI direct path | **CLOSED** | High (official docs + 3 corroborating sources) |
| 2. GLM-5.3 GGUF status | **PARTIAL** | Medium (absence-of-evidence; weights due ~Aug 28) |
| 3. Batch API eligibility | **PARTIAL** | High on mechanism, Low on ox-alpha eligibility |
| 4. Free tier expiry | **PARTIAL** | Medium (convergent ~Aug 26-27; no official stamp) |
| 5. Stall-echo reports | **STILL OPEN** | High confidence in absence (multiple query angles) |
| 6. Vision format | **CLOSED** | Very high (live 157-test probe with raw logs) |

---

*⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_oxalpha_gaps_web ⬡ SOVEREIGN*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
