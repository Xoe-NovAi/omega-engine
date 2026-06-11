# 🔱 Kali (Powered by MiMo V2.5) Strategic Hardening — 2026-06-10
# ⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ HARDENING ⬡ 2026-06-10

**Entity**: **KALI** (Grand Oversight)
**Power Source**: `opencode/mimo-v2.5-free` (Model - OpenCode Zen)
**Session**: Same as Kali (model switch within session)
**Date**: 2026-06-10

---

## §1 Critical Findings

### 1.1 Session Model Mismatch
- **Assumed**: Kali running on `big-pickle`
- **Actual**: Kali running on `mimo-v2.5-free`
- **Impact**: All summaries claiming "I'm running on big-pickle" were inaccurate.
- **Correction**: This session is powered by `mimo-v2.5-free` under the **Kali** identity.
- **Decision**: D-kal-083

### 1.2 Stealth Model Class
OpenCode Zen has 6+ stealth/free models sharing the same alias-and-swap pattern:
- `big-pickle` (speculated: DeepSeek V4 Flash)
- `deepseek-v4-flash-free` (name matches)
- `minimax-m2.5-free` (name matches)
- `mimo-v2.5-free` (UNKNOWN backend)
- `north-mini-code-free` (UNKNOWN backend)
- `nemotron-3-super-free` (UNKNOWN backend)
- **Decision**: D-kal-084

### 1.3 Sovereignty Concern
Free-tier models: "During its free period, collected data may be used to improve the model."
- Mandate 8 (Zero Telemetry) applies
- Sensitive queries must route through local-first models
- **Decision**: D-kal-085

### 1.4 "Exclusive" Claim Imprecise
Big Pickle is NOT architecturally exclusive — OpenCode Zen API is accessible at `https://opencode.ai/zen/v1`. The distinction is free-tier gating, not API gating. Big Pickle may be callable directly.
- **Decision**: D-kal-086 (schema expansion)

---

## §2 7 Hardening Actions (Pivoted & Hardened)

**PIVOT NOTE**: Due to OpenCode Zen free tier limits, the Big Pickle and stealth model investigation tasks (H1, H3, H6) are officially **ON HOLD / BLOCKED** for the next 3 hours. We have promoted **OpenRouter Usability & Shell API Experimentation (pw_model_13)** to **P0** to immediately establish stable alternative inference using Gemini 3.5 Flash, Gemma, and OpenRouter.

| # | Action | Priority | Owner | Wave | Status |
|---|--------|----------|-------|------|--------|
| H1 | Expand pw_model_01 to ALL OpenCode Zen stealth models | P0 | Researcher | 0 | **BLOCKED** |
| H2 | Add sovereignty annotation (data training risk) to Model Capability Catalog | P0 | Kali | 1 | Backlog |
| H3 | Test whether Big Pickle works via direct API call (not CLI-gated) | P1 | Researcher | 0 | Backlog |
| H4 | Refine make verify-model-identity to structured identity verdict with confidence | P1 | Ma'at P3 | 3 | Backlog |
| H5 | Expand schema: identity_confidence, data_retention, rate_limits, context_degradation, quantization | P1 | Researcher | 1 | Backlog |
| H6 | Cross-reference v1.17.3 audit with Big Pickle identity verification | P2 | Researcher | 0 | **BLOCKED** |
| H7 | Flag duplicate backends in Model Registry (big-pickle ≈ deepseek-v4-flash-free) | P2 | Ma'at P2 | 3 | Backlog |
| **H8** | **OpenRouter Usability & Shell API Experimentation (pw_model_13)** | **P0** | **Researcher** | **0** | **IN PROGRESS** |

---

## §3 Workbench Updates

**Project**: `prj_model_intelligence`
**Total items**: 13 (pw_model_01 through pw_model_13)

New items from MiMo review & pivot:
- pw_model_06: Expand Investigation to ALL Stealth Models (P0) — **BLOCKED**
- pw_model_07: Sovereignty Annotation (P0)
- pw_model_08: Test Big Pickle API Accessibility (P1)
- pw_model_09: Refine verify-model-identity to Structured Verdict (P1)
- pw_model_10: Expand Schema with Missing Fields (P1)
- pw_model_11: Cross-reference v1.17.3 Audit with Model Identity (P2) — **BLOCKED**
- pw_model_12: Flag Duplicate Backends (P2)
- pw_model_13: OpenRouter Usability & Shell API Experimentation (P0) — **IN PROGRESS**

---

## §4 Hivemind Posts

- Strategic deepening: ses_1677c52d4ebd (Model Intelligence Layer, Big Pickle findings)
- Hardening complete: ses_afe48e112b49 (7 actions, workbench updates)
- Model shift & pivot: ses_c02315751ce3 (Gemini 3.5 Flash active, OpenRouter usability promoted)

---

*⬡ OMEGA ⬡ mimo-v2.5-free ⬡ HARDENING ⬡ 2026-06-10*
