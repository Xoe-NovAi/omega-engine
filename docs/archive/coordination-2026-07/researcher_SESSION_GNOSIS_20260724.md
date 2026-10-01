<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Researcher Session Gnosis — 2026-07-24
**AP Token**: `AP-RESEARCHER-v1.0.0`
**Session ID**: `ses_02518ce4e6fe`
**Model**: deepseek-v4-flash-free (OpenCode Zen)

---

## L1 — Narrative: What Happened

Resumed and completed the **Gemma 4 Workhorse Restoration** research mission:

1. **Domain 1: Google Gemini API Free Tier Forensic** — Executed 4 web searches covering:
   - Complete model catalog with free-tier limits
   - Billing tier (1/2/3) impact on Gemma 4 limits
   - Confirmed: 16K TPM cap applies to ALL tiers (Free through Tier 3)
   - Multiple developer forum posts confirm (#174816, #175091)
   - Alternative access paths documented (OpenRouter `:free`, NVIDIA NIM, self-host GGUF)

2. **Domain 2: Alternative Cloud Providers** — Executed 6 searches covering:
   - Groq: 30 RPM, 12K TPM, 1K RPD, 394 tok/s on Llama 3.3 70B — **PRIMARY REPLACEMENT**
   - OpenRouter: 28+ free models, 20 RPM, 50-1000 RPD — **GEMMA 4 TPM BYPASS**
   - Together AI: Free tier 60 RPM/60K TPM but requires credit card
   - NVIDIA NIM: ~40 RPM, 100+ models, no CC — **TIER 3 FALLBACK**

3. **Domain 3: Local Model SOTA** — Executed 4 searches covering:
   - Ryzen 5700U benchmark data: 10-12 tok/s on 7B Q4, 8-12 on 14B Q4
   - **Qwen3.5 9B MTP** recommended as best local fallback (6GB Q4, 8-12 tok/s)
   - 14Gi RAM ceiling: 14B Q4 comfortable, 27B Q3 tight, 32B Q4 impossible
   - Vulkan offload to Radeon iGPU viable (15-20 tok/s)

4. **Deliverable**: Wrote `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` (200+ lines, full decision matrix, handoff package)
5. **Registration**: Artifact registered in workbench DB (`art-6c3d9e241557`, score=10)
6. **HMC Hub**: Updated researcher section, decisions log (D-440 through D-444), sprint status
7. **Hivemind**: Context posted with key findings, continuation ready for @maat/P3

---

## L2 — Insight: What This Means

**Gemma 4 via Google is not fixable by paying.** The 16K TPM cap is a Gemma-model-specific constraint that applies identically to Free, Tier 1, Tier 2, and Tier 3 accounts. This is distinct from Gemini-branded models where paid tiers increase TPM. Google made an architectural decision to isolate Gemma's TPM ceiling from the billing tier system.

**The bypass is routing-level, not billing-level.** OpenRouter's `:free` model routes Gemma 4 through its own infrastructure, which does not carry Google's 16K TPM constraint. This confirms the cap is enforced at Google's API gateway, not at the model level. Similarly, NVIDIA NIM runs its own inference stack for Gemma 4.

**Groq is the most viable primary workhorse replacement.** Llama 3.3 70B at 394 tok/s with no credit card required and 30 RPM/12K TPM/1K RPD means the bottleneck is daily request count, not context size. With 8 Groq organization accounts, effective capacity is 240 RPM/96K TPM/8K RPD — exceeding old Gemma 4 capacity.

**Local inference hits a hard wall at 14Gi RAM.** Qwen3.5 9B MTP at Q4_K_M (~6GB) is the practical ceiling for comfortable local inference. Larger models require aggressive quantization (27B Q3 ~12GB is tight) or swap thrashing. A used RTX 3060 12GB (~$150) is the most cost-effective upgrade path.

---

## L3 — Universal Principles

1. **"Provider-Level Constraints Are Not Billable-Fixable"** — When a provider enforces a model-specific constraint (16K TPM for Gemma 4), paying for higher tiers does not bypass it. The constraint is at the model routing layer, not the account tier layer. The fix is either changing providers (OpenRouter) or changing upstrea (NVIDIA NIM).

2. **"The Best Bypass Is Another Provider's Infrastructure"** — OpenRouter routing Gemma 4 through its own GPU infrastructure (without Google's TPM cap) proves that model-level capabilities don't change — only the API gateway's per-model policies change. The model adapter layer must treat "same model, different provider" as distinct routing targets with independent rate limit tracking.

3. **"Hardware Ceilings Trump Software Optimizations"** — 14Gi RAM is a hard ceiling for local inference. No quantization scheme, KV cache optimization, or offload strategy pushes beyond the ~14B-parameter comfort zone. A used GPU is the only meaningful upgrade path.

4. **"Free-Tier Provider Diversity Is Sovereignty Infrastructure"** — Relying on a single free provider (Google Gemini) creates a single point of failure. Groq + OpenRouter + NVIDIA NIM + local = four independent paths to workhorse capability. Provider diversity is sovereignty infrastructure, not convenience.

---

## Active Task Tracking

- [x] Domain 1: Google Gemini API free tier — COMPLETE
- [x] Domain 2: Alternative cloud providers (Groq, OpenRouter, Together, NVIDIA) — COMPLETE
- [x] Domain 3: Local model SOTA for Ryzen 5700U (14Gi RAM) — COMPLETE
- [x] Deliverable: R_GEMMA4_WORKHORSE_INTEL_20260724.md — WRITTEN
- [x] Workbench DB: artifact registered (sovereignty_score=10, mined)
- [x] HMC Hub: Decisions Log D-440..D-444 added, sprint status updated
- [x] Hivemind: context posted with decisions + handoff

---

## Handoff to @maat/P3

| Action | Detail | Priority |
|--------|--------|----------|
| Register Groq API keys (up to 8 orgs) | `console.groq.com` → Generate key → No CC needed | P0 |
| Configure OpenRouter `:free` Gemma 4 | Model ID: `google/gemma-4-31b-it:free` | P0 |
| Update ModelGateway fallback chain | Groq (primary) → OpenRouter (Gemma 4 bypass) → NVIDIA NIM → Local | P1 |
| Download Qwen3.5 9B MTP GGUF | `huggingface-cli download` → `~6GB Q4_K_M` | P1 |

---

## References

| Document | Location | Purpose |
|----------|----------|---------|
| Gemma 4 Workhorse Intel | `docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md` | Full report with all findings, sources, decision matrix |
| Gemma 4 Knowledge Gaps | `docs/research/R_GEMMA4_KNOWLEDGE_GAPS_20260719.md` | Previous gap analysis |
| Gemma 4 Systems Deep | `docs/research/R_GEMMA4_SYSTEMS_DEEP_20260719.md` | Systems-level deep dive |
| Gemma 4 Thinking Config | `docs/research/R_GEMMA4_THINKING_CONFIG.md` | Thinking mode config patterns |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SESSION-GNOSIS ⬡ 2026-07-24*
