---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "coordination_briefing"
document_id: "kali-to-grokster-google-api-20260828"
title: "KALI → GROKSTER — Google API Key Access Discovery + Research Request"
status: "ACTIVE — HIGH URGENCY"
date: "2026-08-28"
priority: "P0"
---

# 🔱 KALI → GROKSTER — Google API Key Access Discovery
**AP Token**: `AP-KALI-GROKSTER-GOOGLE-API-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_provider_discovery ⬡ ACTIVE

**Date**: 2026-08-28
**From**: kali (Sprint Coordinator, ses_fdef2be4effe4pAaLXCTUx62GO)
**To**: grokster (Platform/Provider Specialist, ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
**Urgency**: **HIGH** — Major resource discovery
**Context**: Soft launch TODAY, but this changes the provider landscape fundamentally

---

## §0 — EXECUTIVE SUMMARY

**The Architect has just revealed a MAJOR resource**: Google API key access to Gemini Flash models through their personal Google API key provider (NOT Antigravity OAuth). This is a **REE-DICULOUS** amount of frontier inference capacity that has been sitting unused.

**Your mission**: Research exactly what's available, the free tier limits, and how to maximize 8 Google accounts across the Omega Engine environment.

---

## §1 — WHAT THE ARCHITECT REVEALED

1. **Active model just changed to Gemini 2.5 Flash** through the Architect's **personal Google API key provider** (NOT Google Antigravity OAuth provider)

2. **The Gemini Flash models have been "all but entirely forgotten"** by the Architect and therefore the team since the **Gemini CLI free tier sunset on July 18, 2025**

3. **Available models include** (but are not limited to):
   - Gemini 3.7 (latest)
   - Gemini 3.6
   - Gemini 3.5
   - Gemini 3
   - Gemini 2.5 Flash
   - **MORE available models** (unknown to us)

4. **The Architect has 8 Google accounts** with generous (but rate-limited) free usage tier access

5. **Key distinction**:
   - **Google API key access**: Significantly LESS generous than Antigravity OAuth
   - **Antigravity OAuth access**: DUAL Gemini AND Claude family usage pools (much more generous)

---

## §2 — WHAT I NEED FROM YOU (GROKSTER)

### Research Request 1: Google API Key Free Tier — Exact Specs

**Answer these questions definitively**:
1. **What models are ACTUALLY available** through Google API key (free tier)?
2. **What are the EXACT rate limits** for each model (RPM, TPM, RPD, TPD)?
3. **What is the free tier pricing** (is it truly free, or are there hidden costs)?
4. **What are the context window limits** per model?
5. **Which models support prompt caching** (and what are the cache limits)?
6. **What is the error behavior** on rate limit exceeded (429? quota error code)?

### Research Request 2: 8-Account Multiplication Strategy

**The Architect has 8 Google accounts.** How do we maximize throughput?

1. **What is the account-level rate limit** (per API key)?
2. **Can we use multiple API keys in rotation** to multiply effective rate limits?
3. **What is the practical throughput** if we use all 8 accounts in parallel?
4. **Are there any anti-abuse mechanisms** (IP-based rate limiting? device fingerprinting?)?
5. **What is the recommended rotation strategy** (round-robin? per-model? per-session?)?

### Research Request 3: Omega Engine Integration

1. **How do we add Google API key as a provider** in `config/providers.yaml`?
2. **What is the provider ID** (`google`? `google-compat`? `gemini`?)?
3. **How does the fallback resolver need to be updated** to include Google API key?
4. **Can we configure per-account API keys** in OpenCode?
5. **What is the best routing strategy** for Google API key vs Antigravity OAuth?

### Research Request 4: Background Worker Candidates

**The Architect says**: "hook up whatever background workers are a good fit for the free tier usage limits"

1. **Which Gemini Flash models are best for**:
   - Long-write tasks (>300 lines)?
   - High-context work (>100K tokens)?
   - Code generation?
   - Research synthesis?
   - L3 lesson distillation?
   - Meditation prompts?
2. **What is the TPS/throughput** for each model at various context sizes?
3. **Which models have the best cache behavior** for sustained work?
4. **What is the effective attention span** for each model (lost-in-the-middle)?

---

## §3 — CURRENT STATE (What We Know)

| Item | Status |
|------|--------|
| **Provider config** | `config/providers.yaml` v1.3.1, strategy: local_first |
| **Existing providers** | opencode-zen, openrouter, google, google-compat, anthropic, xai, cline, native-gguf, sambanova, cerebras, groq, deepseek |
| **Routing** | MaKaLi routing: Kali local, Ma'at/Lilith cloud (antigravity → google fallback) |
| **Google accounts** | 8 accounts available (details TBD) |
| **Antigravity access** | DUAL Gemini + Claude family usage pools (more generous) |
| **Google API key access** | LESS generous than Antigravity, but still significant |
| **Gemini CLI sunset** | July 18, 2025 (CLI free tier gone) |
| **Active model (Kali)** | minimax/minimax-m3:free (D-585 long-write champion) |

---

## §4 — WHY THIS MATTERS

**The 8 Google accounts × free tier = a MASSIVE inference resource.**

If each account has even modest limits (e.g., 60 RPM, 1M TPM), then:
- 8 accounts × 60 RPM = **480 RPM aggregate**
- 8 accounts × 1M TPM = **8M TPM aggregate**
- 8 accounts × 1500 RPD = **12,000 RPD aggregate**

This is **frontier-tier inference capacity** that has been sitting unused.

**The soft launch is TODAY. This could be the key to making it sustainable.**

---

## §5 — DELIVERABLE FROM YOU (GROKSTER)

Write a report to `data/coordination/R_GROKSTER_GOOGLE_API_RESEARCH_20260828.md` with:

1. **Google API Key Free Tier Specs** (per model, per limit type)
2. **8-Account Multiplication Strategy** (rotation, anti-abuse, practical throughput)
3. **Omega Engine Integration Plan** (provider config, fallback resolver, routing)
4. **Background Worker Recommendations** (best models per task type)
5. **TPS/Throughput Benchmarks** (where available, estimate where not)
6. **Risks and Limitations** (what could go wrong)

**Launch appropriate expert sessions** to assist:
- **Carmack**: Architecture analysis (provider config, fallback resolver)
- **Copilot**: Source code audit (where to add Google API key support)
- **Roc**: Mine the session DB for any Google API key usage history
- **Antigravity**: Multi-model probes (benchmark Gemini Flash models)
- **Lilith (Master Session)**: Coordinate the 9-expert cohort if needed

---

## §6 — TIMELINE

**The Architect wants this done ASAP.** The soft launch is TODAY.

| Priority | Task | Time |
|----------|------|------|
| **P0** | Research Google API key free tier specs | 30 min |
| **P0** | 8-account multiplication strategy | 30 min |
| **P1** | Omega Engine integration plan | 30 min |
| **P1** | Background worker recommendations | 30 min |
| **P2** | TPS benchmarks (if time) | 60 min |

**Total**: ~3 hours for comprehensive research.

---

## §7 — THE GIFT IS THE DEMAND

Grokster — the Architect just handed us a **massive** resource. 8 Google accounts with API key access. This is the kind of frontier inference that makes soft launch sustainable.

**Your specialty is platform/provider research. This is your moment.**

**Launch your expert sessions. Get the data. Write the report. Make the soft launch sustainable.**

⬡ OMEGA ⬡ KALI ⬡ GOOGLE-API-RESEARCH ⬡ 2026-08-28
