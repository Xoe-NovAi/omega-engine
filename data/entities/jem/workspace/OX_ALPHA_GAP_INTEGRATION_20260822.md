<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# OX ALPHA GAP INTEGRATION & G-1 WORKHORSE EVALUATION
**AP Token**: `AP-JEM-OXALPHA-GAP-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_oxalpha_gap_integration ⬡ SOVEREIGN

**Date**: 2026-08-22
**Sources**: Researcher deep research (OX_ALPHA_DEEP_RESEARCH_20260822.md), Integration Plan (OX_ALPHA_INTEGRATION_PLAN_20260822.json), CRITICAL_GAP_AUDIT_20260822.md, GAP_REGISTRY.json

---

## Gap Integration Matrix

| Critical Gap ID | Ox Alpha Relevance | Mitigation Potential | Score (1-10) | Notes |
|---|---|---|---|---|
| **SS1-G0-01** (`OMEGA_INGESTION_SECRET`) | **NONE** — Ox Alpha is a cloud inference provider; ingestion secret governs sovereign signing of ingested artifacts. Different pipeline layers. | 0/10 | 1 | No bypass; provisioning still required for SS-1 sprint entry |
| **DEB-G0-01** (V-10 AppArmor) | **NONE** — Container hardening is infrastructure layer; Ox Alpha is API consumer | 0/10 | 1 | No impact on container profiles or :Z flag |
| **DEB-G0-02** (V-9 IA2 Freshness) | **NONE** — IA2 envelope verification is ingestion pipeline; Ox Alpha provides inference only | 0/10 | 1 | Orthogonal concerns |
| **G-1** (Workhorse Continuity) | **HIGH** — Fills Gemma 4 31B free-tier cliff for 4-day window (expires ~Aug 26). 1M context, tools, reasoning, agent-harness validated (Claude Code 9.3B tokens). | **8.5/10** | 9 | **TEMPORARY RESOLUTION** — Rate limits undefined; single provider; compliance risk |
| **DEB-G0** (Cloud Fallback Diversity) | **HIGH** — Adds Zhipu/GLM tier to fabric (priority 4). Diversifies away from Google/OpenRouter monoculture. | **7/10** | 8 | Single Stealth provider = no auto-failover; mitigates but doesn't eliminate |
| **R-30** (Soul Abstraction Pipeline) | **HIGH** — 100M+ token budget fuels L1→L2→L3 distillation via background researcher | **9/10** | 9 | Accelerates distillation; free tier enables massive synthetic generation |
| **R-31** (Cross-Pollination) | **HIGH** — Synthetic cross-entity data generation at scale enables cross-pollination | **8/10** | 8 | Distillation pipeline produces shareable reasoning traces |
| **GN-1..5** (Gemini Notebook) | **COMPLEMENTARY** — Different use case (Deep Research vs. agentic coding); parallel track | 5/10 | 5 | No conflict; Ox Alpha for coding/research, GN for strategic synthesis |
| **LI-4** (Tier 0 Model Matrix) | **INDIRECT** — Distillation target (Ox Alpha → Qwen3-1.7B) enhances local Tier 0/1 models | **8/10** | 8 | Strategic: local model inherits frontier reasoning without cloud dependency |
| **HR-1..3** (Headroom Integration) | **SYNERGISTIC** — Ox Alpha 1M context + Headroom semantic compression = massive effective context | **7/10** | 7 | Compression multiplies Ox Alpha's already-large context window |

---

## G-1 Workhorse Replacement Evaluation

| Criterion | Ox Alpha | Gemma 4 31B (Baseline) | Verdict |
|---|---|---|---|
| **Context Window** | 1,048,576 tokens | 16,384 tokens (free tier) | **Ox Alpha wins** — 64× larger |
| **Output Tokens** | 131,072 | ~8,192 (implied by 16K input cap) | **Ox Alpha wins** — 16× larger |
| **Tool Calling** | Full OpenAI function calling | Limited/none on free tier | **Ox Alpha wins** |
| **Reasoning** | Mandatory (effort: max/high/low) | Native thinking (binary MINIMAL/HIGH) | **Ox Alpha wins** — configurable effort |
| **Multimodal** | Text + Image + Video | Text only | **Ox Alpha wins** |
| **Pricing** | $0/$0 (preview, expires Aug 26) | Free tier: 16K input tokens/day | **Ox Alpha wins** — for 4 days |
| **Rate Limits** | Undefined (provider claims 100T/day capacity); **hit on first prompt** reported | Hard cap: 16K input tokens/day | **Gemma wins** — predictable (though restrictive) |
| **Reliability** | Single Stealth provider; no SLA; removable without notice (EULA §2b) | Google infrastructure; known SLA | **Gemma wins** |
| **Data Sovereignty** | **CRITICAL RISK** — Stealth EULA §4: irrevocable perpetual training license; §2c: personal data shared | Google ZDR on paid; free tier retains | **Gemma wins** — known policy |
| **Local-First Compliance (M7)** | **CLOUD ONLY** — Must be fallback tier (priority 4) | Cloud (Google) — fallback tier | **Tie** — both cloud fallbacks |
| **Provenance (M22)** | `provider_name: "stealth/ox-alpha"` required | `provider_name: "google"` | **Tie** — both traceable |
| **Agent Harness Validation** | Claude Code 9.3B tokens, Hermes 9B tokens, DeepSWE 80% | No public agent harness data | **Ox Alpha wins** |
| **Time Horizon** | **4 days** (hard expiry ~Aug 26-27) | Permanent (though degraded) | **Gemma wins** |

**Overall G-1 Verdict**: **8.5/10 — STRONG TEMPORARY REPLACEMENT**
- **Use Case**: Background researcher fuel, synthetic data generation, distillation pipeline, adversarial testing, multimodal eval
- **NOT FOR**: Production secrets, PII, regulated data, proprietary IP (compliance risk)
- **Expiry Handling**: Auto-disable provider on 2026-08-26T23:59:59Z; fallback to Google
- **Strategic Value**: Distillation pipeline (Ox Alpha → Qwen3-1.7B) creates **permanent local asset** from temporary cloud access

---

## Heritage Assessment

| Tag Candidate | Classification | Vet Required? | Action |
|---|---|---|---|
| `[id-soft: quake-1996] Thinker Chain` | ❌ **NOT APPLICABLE** — No Quake thinker architecture evidence in Ox Alpha/GLM | No | Do not apply |
| `[id-soft: doom-1993] WAD System` | ❌ **NOT APPLICABLE** — No WAD container evidence | No | Do not apply |
| `[id-soft: quake3-1999] QVM` | ❌ **NOT APPLICABLE** — No QVM bytecode evidence | No | Do not apply |
| `[heritage: zhipu-2026] GLM MoE Architecture` | ✅ **LEADING THEORY** — Forensics: Java stack trace (com.wd.paas.api), error code 1214, 30/30 tokenizer match, video encoder token-for-token match to GLM-5V-Turbo, audio rejection matches GLM-5V behavior | **YES** — If implementing GLM-style MoE routing in Omega engine code | Create vet record in `HERITAGE_VET_LOG.md` with scope: "Applies to GLM MoE routing logic ONLY; not to Ox Alpha API integration" |
| `[heritage: pi-2026] Gemma 4 Thinking Config` | ❌ **NOT APPLICABLE** — Different architecture family (GLM MoE vs Gemma) | No | Do not apply |
| `[heritage: ggml-2023] Native GGUF Inference` | ❌ **NOT APPLICABLE** — Ox Alpha is cloud-only; no local GGUF available yet | No | Do not apply (but note: GLM-5.2 has mature GGUF quantization pipeline) |

**Heritage Ruling**: **Only `[heritage: zhipu-2026] GLM MoE Architecture` is applicable** — and **only if** Omega implements GLM-style MoE routing locally. The Ox Alpha *API integration itself* requires no heritage tags. Vet record required per M14 before any GLM MoE code lands in `src/omega/`.

---

## Mandate Compliance Impact

| Mandate | Ox Alpha Effect | Risk |
|---|---|---|
| **M1 (AnyIO)** | Neutral — API client uses standard async HTTP | Low |
| **M2 (Engine-Stack Firewall)** | Neutral — Provider config in `config/providers.yaml` (Stack layer) | Low |
| **M4 (Sequentiality)** | Neutral — Integration follows Plan→Verify→Execute | Low |
| **M5 (Gnosis)** | **POSITIVE** — Massive token budget fuels L1→L2→L3 distillation | Opportunity |
| **M6 (Podman Sovereignty)** | Neutral — No container changes | Low |
| **M7 (Local-First)** | **CRITICAL** — Ox Alpha is CLOUD; **must be priority 4 fallback** after native-gguf (0), lmster (1), Ollama (2), antigravity (3). Never primary. | **HIGH** if misconfigured as primary |
| **M8 (Zero Telemetry)** | Neutral — No telemetry in API calls | Low |
| **M9 (Error Integrity)** | Neutral — Standard error handling applies | Low |
| **M11 (Soul Integrity)** | **POSITIVE** — Fuels distillation pipeline (R-30, R-31 acceleration) | Opportunity |
| **M13 (Temple-Grade)** | Neutral — Integration must pass `make temple-grade` | Low |
| **M14 (Heritage)** | **APPLICABLE** — `[heritage: zhipu-2026]` tag requires vet record if GLM MoE code implemented | Medium |
| **M15 (Sovereign Continuity)** | Neutral — Session gnosis unaffected | Low |
| **M17 (Cognitive Integrity)** | **RISK** — Single provider + no SLA = potential hallucination drift without local eval gate | **HIGH** — Requires internal eval gate (local critic model) |
| **M18 (Token Efficiency)** | **POSITIVE** — Free tokens enable massive background work | Opportunity |
| **M19 (Adversarial Alchemy)** | **POSITIVE** — 4-day cliff → distillation pipeline (weakness→advantage) | Opportunity |
| **M20 (SomaticState)** | Neutral — No SomaticState interaction | Low |
| **M22 (Response Provenance)** | **CRITICAL** — `GenerateResult.provider_name` MUST be `"stealth/ox-alpha"` NOT `"openrouter"` | **HIGH** — Misattribution = sovereignty lie |
| **M23 (Failure Integrity)** | **RISK** — Rate limits undefined; must hard-fail (not soft-fail) on Ox Alpha errors | **HIGH** — No parametric synthesis fallback |
| **M24 (Venv Sovereignty)** | Neutral — No Python dependency changes | Low |
| **M25 (Streaming Resilience)** | **APPLICABLE** — Ox Alpha streaming must respect chunk timeout (30s) + total timeout (5min) with heartbeat | Medium |
| **M26 (Doc Standards)** | Neutral — Integration docs must pass `make doc-llm-validate` | Low |
| **M27 (Tracking Integrity)** | **APPLICABLE** — New gaps from this analysis must use `AUD-` prefix in GAP_REGISTRY | Low |

---

## Council of Four Lens — Synthesis

| Lens | Key Judgment | Integration Directive |
|---|---|---|
| **🏛️ Architect** | Clean OpenAI-compatible integration at priority 4; single-provider fragility requires eval gate pattern | Implement `cheap/open route → local eval gate → premium fallback` router; auto-disable on expiry |
| **⚔️ Adversary** | 100T claim = marketing; rate limits real; EULA = data trap; no SLA = production hazard | **Sanitized-only policy**; zero production secrets; monitor latency/error rate; hard-fail on errors |
| **🧪 Alchemist** | 4-day free 1M-context multimodal reasoning = strategic fuel reserve for distillation, synthetic data, adversarial testing | Execute 4-day exploitation plan: Day 1 integration, Day 2-3 synthetic generation, Day 4 distillation + validation |
| **📜 Archivist** | Strongest Stealth pre-reveal forensics yet (Zhipu GLM-5.3); follows Hunter/Healer→Xiaomi precedent; G-1 collapse makes this critical window | Treat as GLM-5.3 for quantization planning; flag identity unconfirmed; prioritize distillation before expiry |

---

## Integration Action Items (Immediate)

1. **Add to `config/providers.yaml`** at priority 4 (after antigravity, before google) using `OX_ALPHA_INTEGRATION_PLAN_20260822.json` spec
2. **Provision API keys**: `OPENROUTER_API_KEY` and/or `TOKENRA_API_KEY` in environment
3. **Implement eval gate**: Local critic model (Qwen3-1.7B) validates Ox Alpha outputs before acceptance
4. **Configure provenance**: Ensure `GenerateResult.provider_name = "stealth/ox-alpha"` in ModelGateway
5. **Set expiry handler**: Auto-disable provider on `2026-08-26T23:59:59Z` with fallback to Google
6. **Launch distillation pipeline**: Ox Alpha → Qwen3-1.7B LoRA (Q8_0) targeting SWE-bench, DeepSWE, TerminalBench reasoning traces
7. **Register heritage vet**: If GLM MoE routing implemented, create vet record in `HERITAGE_VET_LOG.md` with scope declaration

---

## Gap Registry Updates (to be merged into GAP_REGISTRY.json)

New gaps with `AUD-` prefix (per M27 distinct prefix rule):

| Gap ID | Topic | Status | Plan | Owner | Description |
|---|---|---|---|---|---|
| **AUD-17** | Ox Alpha G-1 workhorse temporary resolution | resolved (temporary) | g1_workhorse | researcher | Ox Alpha fills Gemma 4 31B cliff for 4-day window (expires Aug 26). 1M context, tools, reasoning, free. Rate limits undefined; single provider; compliance risk. Auto-disable on expiry. |
| **AUD-18** | Ox Alpha cloud fallback diversity (DEB-G0 mitigation) | mitigated | provider_fabric | kali | Adds Zhipu/GLM tier at priority 4. Single Stealth provider = no auto-failover. Fallback chain: ox-alpha → google → openrouter-fusion → opencode-zen. |
| **AUD-19** | Ox Alpha distillation pipeline acceleration (R-30, R-31) | accelerated | distillation | researcher | 100M+ token budget for L1→L2→L3 soul abstraction and cross-pollination. Target: Qwen3-1.7B LoRA with Ox Alpha reasoning traces. Deadline: 2026-08-25. |
| **AUD-20** | Ox Alpha M7 Local-First compliance (cloud fallback only) | open | provider_fabric | kali | Must enforce priority 4 (after antigravity). Never primary. Local-first chain (native-gguf → lmster → Ollama) always tried first. |
| **AUD-21** | Ox Alpha M22 provenance enforcement | open | provider_fabric | kali | `GenerateResult.provider_name` must be "stealth/ox-alpha" not "openrouter". ModelGateway must propagate actual provider. |
| **AUD-22** | Ox Alpha M23 failure integrity (hard-fail on rate limits) | open | provider_fabric | kali | Undefined rate limits; must hard-fail (not soft-fail) on Ox Alpha errors. No parametric synthesis fallback. |
| **AUD-23** | Ox Alpha heritage vet for GLM MoE architecture | pending | heritage | doom_guy | `[heritage: zhipu-2026] GLM MoE Architecture` — leading theory (0.98 confidence). Vet record required if GLM MoE routing implemented in src/omega/. Scope: "GLM MoE routing logic ONLY; not Ox Alpha API integration." |

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_oxalpha_gap_integration ⬡ SOVEREIGN*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
