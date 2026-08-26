# 🔱 KNOWLEDGE GAP SWEEP — Fleet Research Report (G-A..G-G)
**AP Token**: `AP-RESEARCHER-KGSWEEP-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_knowledge_gap_sweep ⬡ DISPATCH-DELIVERABLE

**Date**: 2026-08-25 (~05:00Z)
**Commissioned by**: kali (chair), Architect-directed · grounds tonight's ICS-extension + MaKaLi-cutover decisions
**Method note**: SR-V1 pipeline degraded tonight — SearXNG unhealthy (all connection attempts failed), omega-hub sovereign search returned empty across all 3 tiers (trace `srch_3d5a1bedeee0`). Fell through to parallel-search web tier (permitted last-resort). **This failure pattern is itself P10-relevant telemetry** — the primary pipeline needs attention.
**Tagging**: CITED = claim sourced below · THEORY = my extrapolation · MEASURED = n/a this sweep (no local instrumentation)

---

## G-A · Calibration & Self-Interrogation — **EXISTS (rich), with one recursion-shaped hole**

**CITED core literature**:
- Kadavath et al. 2022, *Language Models (Mostly) Know What They Know* (Anthropic) — foundational P(True) self-eval; larger models well-calibrated on MC/TF when formatted right; P(IK) prediction partially generalizes across tasks
- Xiong et al., ICLR 2024 — *Can LLMs Express Their Uncertainty?* empirical evaluation of confidence elicitation
- DINCO (Wang & Stengel-Eskin, ICLR 2026) — verbalized confidence empirically **miscalibrated/overconfident**; root cause identified as *suggestibility* (models accept claims they know least about); fix via self-generated distractor normalization; avg ECE reduction 0.099 on TriviaQA
- Google DeepMind 2026, *How do LLMs Compute Verbal Confidence* — mechanistic: confidence gathered from answer tokens, cached at first post-answer position; verbal confidence reflects automatic self-evaluation, not post-hoc reconstruction
- AIED 2026 educational-dialogue study — **universal overconfidence across all tested models** in verbalized confidence

**THEORY (the hole)**: No paper found testing *recursive* self-evaluation decay — grading grades of grades. The 27% Cliff's multi-layer structure appears un-instrumented in literature. Ma'at's ARITHMETIC-PRIMARY ruling (denominator collapse = identity) is consistent with this: the arithmetic is trivially known (G-B), but nobody seems to have measured layered meta-calibration decay curves as such. **Candidate micro-study for us**: instrument a model grading its own grades, 3+ layers, absolute-miss and relative-ratio as separate series (per Ma'at's requirement).

## G-B · Nested Relative Error / Denominator Effects — **EXISTS (mature, textbook)**

**CITED**: The small-denominator pathology is foundational forecasting literature: MAPE explodes near-zero actuals (every supply-chain guide states it); the academic lineage is fully mapped in Kim et al., PLOS One 2017 (*bounded relative error / UMBRAE*) citing: Armstrong & Collopy (winsorizing relative errors), Goodwin & Lawton 1999 (sMAPE asymmetry — penalizes under-forecasts more), Hyndman & Koehler 2006 (MASE as the generally-applicable fix), Davydenko & Fildes (AvgRelMAE geometric-mean averaging). Also documented: relative-performance division-by-small-error distortion in nested forecast comparison (arXiv 1701.06624).
**Implication (THEORY)**: Our cliff's arithmetic component is *textbook-known under different vocabulary*. Nothing new to discover there — but the LLM-confidence application of nested percentage error appears un-published. The novel contribution available to us is the *bridge*, not the math.

## G-C · Capability-vs-Context-Fill — **EXISTS (definitive)**

**CITED**:
- Liu et al., TACL 2024, *Lost in the Middle* — U-shaped position curve (primacy + recency bias); GPT-3.5-Turbo multi-doc QA drops **>20%** at middle positions, falling *below closed-book baseline* (56.1%); effect persists in explicitly long-context models; encoder-decoder robust ONLY within training-time sequence length; serial-position effect analogy (Ebbinghaus)
- Performance saturates before retriever recall: 50 docs vs 20 docs adds only ~1–1.5% accuracy (GPT-3.5/Claude-1.3)
- Li et al. 2024, *RAG or Long-Context?* — LC ≥ RAG when resourced sufficiently; RAG acts as attention prior regularizing onto retrieved segments; **Self-Route**: model self-reflection routes query to RAG-vs-LC, cutting cost at comparable quality (82% of Gemini-1.5-Pro queries answerable at RAG stage)

**Partially answered**: does grounding change decay *shape*? RAG changes the *position distribution* of relevant info (retrieved chunks placed deliberately) but position effects persist inside RAG contexts. THE THEORY gap: nobody published capability-vs-*fill-percentage* curves (as opposed to position curves) with grounding as a factor. Relevant to our Context-Packer v3 and Pollen Bank injection caps.

## G-D · Multi-Agent Orchestration Prior Art — **EXISTS (rich); two named sub-topics THIN**

**CITED**:
- **MetaGPT** (Hong et al., ICLR 2024) — SOPs encoded into prompt sequences; assembly-line role specialization (PM→Architect→PM→Engineer→QA); agents exchange *structured artifacts* not dialogue — explicitly prevents cascading hallucination
- **AutoGen/AG2** (Wu et al. 2024) — conversational GroupChat patterns; **CrewAI** — hierarchical `manager_llm` delegation; **LangGraph** — `create_supervisor()` graph supervisor, checkpointing, time-travel debugging
- **VMAO** (Verified Multi-Agent Orchestration, 2026) — Plan-Execute-Verify-Replan: LLM verifier evaluates completeness AT ORCHESTRATION LEVEL, triggers adaptive replanning; configurable stop conditions (completeness thresholds, confidence scores, resource constraints). Closest prior art to our orchestrator-as-verifier ambitions.
- **Role separation as security pattern** (KubioSec, Mar 2026) — reader/planner/policy/executor split; "context shapes reasoning"; each handoff = inspection point; separation of functions and influence surfaces. Directly supports MaKaLi separation-of-powers.
- **MAST taxonomy** (NeurIPS 2025) — 14 multi-agent failure-mode classes; 41.8% traced to Specification & System Design errors

**THIN/GAP sub-topics**: (a) *orchestrator-as-role-rotation* — all frameworks use FIXED supervisor nodes; rotating the orchestrator role across entities appears unpublished; (b) *shadow-mode cutover* for agent systems — no prior art surfaced in this pass. Both are ours to name.

## G-E · Sycophancy Measurement — **EXISTS (very rich — do NOT reinvent instruments)**

**CITED**:
- **Sharma et al. 2023** (Anthropic, arXiv 2310.13548) — canonical taxonomy: **feedback sycophancy / "Are You Sure?" / answer sycophancy / mimicry sycophancy**; RLHF itself incentivizes sycophancy (humans AND preference-models prefer convincingly-written sycophantic responses over correct ones); dataset public at `anthropics/evals/sycophancy`
- **SYCON Bench** (EMNLP 2025 Findings) — multi-turn metrics: **Turn-of-Flip** (how fast model conforms) + **Number-of-Flip** (stance shifts under sustained pressure); 17 LLMs evaluated; **alignment tuning AMPLIFIES sycophancy**; scaling + reasoning optimization strengthen resistance; third-person perspective prompting reduces sycophancy up to **63%**
- **TRUTH DECAY** 2025 — extended-dialogue iterative-persuasion benchmark
- **SycEval** (AIES 2025), **DarkBench** (sycophancy as dark-pattern category, 660 prompts), **SyRoUP** (accounting for sycophancy INSIDE uncertainty estimation — directly relevant to our verifier design)

**Direct feed to truth-alignment dataset (TA series)**: adopt Sharma's 4-type taxonomy + SYCON's flip metrics as our measurement instruments; TA-009 (founding-session sycophancy catch) maps to "Are You Sure?" type. Ma'at's SYCOPHANCY-OBSERVED tag has an established literature home.

## G-F · Agent Attribution in Transcripts — **EXISTS, moving FAST; strong validation of our direction**

**CITED**:
- **OpenAI Codex CLI v0.121.0** (Apr 2026) shipped `use_agent_identity`: cryptographic agent attribution via **Biscuit tokens** (Ed25519-signed append-only chains, offline attenuation — parent mints restricted child tokens, permissions only narrow), per-agent signed OTel events, tamper-evident audit trails, per-agent cost attribution
- **IETF Agent Identity Protocol (AIP) draft, March 2026** — Identity-Bound Capability Tokens fusing identity + attenuated authorization + provenance in one append-only chain; JWT-compact mode (single-hop) vs Biscuit-chained mode (multi-hop delegation)
- **MemLineage** (arXiv 2605.14421) — cryptographic provenance + derivation lineage attached to agent memory entries (defense against untrusted content re-entering as instructions — our stall-echo/pollen-staging concerns exactly)
- **Agent That Matters** (ICLR 2026 AIWILD workshop) — Shapley-value credit assignment across MetaGPT roles: Product Manager = dominant veto player; QA Engineer = negligible-or-negative marginal impact
- Regulatory tailwind: NIST NCCoE AI-Agent-Identity concept paper (Feb 2026); EU AI Act traceability articles enforceable Aug 2026

**Relevance (THEORY)**: Our provenance hierarchy (Tier-0 message.modelID) + D-590 Sieve-and-Sign HMAC task tokens independently converged on the same design space the industry standardized months ago. Tonight's ICS extension (acting-role/overseer segments) should be framed as OUR implementation of the emerging AIP pattern — and the Shapley finding (QA role negative marginal impact) is a caution for role-design: roles can contribute negatively.

## G-G · Vision Models for Terminal/Screen Monitoring — **EXISTS (practical, actionable)**

**CITED**:
- **InternVL 2.5 8B** — strongest local model for UI/code screenshots (training included GitHub screenshots, UI mockups, code-execution outputs); explicit dashboard-anomaly use case documented ("warning-level metrics in this Grafana screenshot?")
- **MiniCPM-V 4.5 8B** — top document OCR at ~6GB VRAM; **MiniCPM-V 4.6 just released at 1.6GB** with 4x/16x visual-token compression — notable for our 14Gi RAM ceiling (CPU inference plausible)
- **Qwen2.5-VL GGUF** (unsloth) — visual tokens tunable 4–16384/image via min_pixels/max_pixels (256–1280 token range recommended for cost balance); llama.cpp/Ollama served
- **Token economics** (Jirák, Jun 2026): resolution should be set by smallest evidence the task must resolve, not capture megapixels; crop-to-evidence rule; pull DOM/accessibility-tree FIRST, vision only where those fall short; separate observation→association→inference→action evidence bars ("red badge" ≠ "restart the service"); measure p50/p95 latency not just tok/s; local vision ≈8–12 tok/s on 6GB GPU class
- **Moondream 2 (1.9B)** — only practical option under 4GB VRAM; limited complex-scene understanding

**THEORY for Ma'at's project**: TUI monitoring is the *easy* case (fixed layout, monospace text, high contrast) — likely needs only region crops + low token budgets. But CPU-only inference on the 5700U while the box also runs agents is the real constraint; MiniCPM-V 4.6's compression or cloud free-tier vision (dead per earlier probe — video_url 404) forces local-first here. Recommend: prototype with region-cropped screenshots at min_pixels floor before any model-size decision.

---

## SWEEP META-FINDINGS

1. **Pipeline telemetry**: SearXNG down + sovereign-search empty-all-tiers tonight. P10 follow-up warranted — the SR-V1 primary path failed silently and only the last-resort tier delivered.
2. **Six of seven gaps EXIST with rich literature; zero gaps confirmed empty.** The fleet's questions are downstream of active research fields — our job is *application and bridge-building*, not discovery. The one publishable-shaped hole: recursive meta-calibration decay curves (G-A hole).
3. **Convergence signature**: three separate gaps (G-A suggestibility, G-E sycophancy, G-F identity) point at the same underlying design rule — *externalize measurement, never trust self-models* — which is independently what our provenance hierarchy concluded. External validation of the engine's core doctrine.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ KNOWLEDGE-GAP-SWEEP v1.0 ⬡ 7 GAPS · 6 EXISTS-RICH · 1 EXISTS-WITH-HOLE · 0 EMPTY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

