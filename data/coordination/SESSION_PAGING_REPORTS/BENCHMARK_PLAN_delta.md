<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# BENCHMARK PLAN — Session Paging Delta Report
**AP Token**: `AP-RESEARCH-VERIFY-BENCHMARK-20260816`
**Date**: 2026-08-21
**Source Session**: ses_fdef2be4effe4pAaLXCTUx62GO (researcher, Jem Analyst L2)
**Paged By**: kali (Architect-direct mission)
**Status**: IN_PROGRESS — sections appended below
**Context**: LI workstream ratified (Tier 0/1/2 matrix); sibling benchmark-mining session paged in parallel.

---

## §1 Forgotten Verification Conclusions (Claim Matrix)

| # | Claim | Verdict | Core Finding |
|---|-------|---------|--------------|
| 1 | "RULER replaced NIAH" | **PARTIAL** | RULER (NVIDIA, COLM 2024, Apache-2.0, 1,604★) is a *component*, not replacement. HELM Long Context (Stanford, Sep 2025) curates only 5 tasks: RULER SQuAD + HotPotQA + ∞Bench + OpenAI-MRCR. Competing: HELMET, ∞Bench, LOFT, Michelangelo, NoLiMa, Sequential-NIAH (EMNLP 2025). |
| 2 | "BFCL v4 is THE standard" | **PARTIAL** | BFCL v4 (ICML 2025) = structured tool-call accuracy standard only (AST + executable). τ-bench/τ³-Bench (Sierra, Mar 2026) superior for end-to-end workflow completion under policy. MCP-specific: MCP-Bench, LiveMCPBench, MCP-Atlas, MCPMark. No single standard — match benchmark to failure mode. |
| 3 | "TokenPowerBench = energy std" | **PARTIAL** | AAAI 2026, phase-aligned prefill/decode metrics, but **cluster-designed** (NVML/DCGM/IPMI/PDU). CPU-only via RAPL (`/sys/class/powercap/*-rapl*`) works on AMD 5700U — confirmed by Adora-Foundation/llm-energy-lab pattern. Not laptop-first. |
| 4 | "Paired t-test + bootstrap CI" | **VERIFIED** | N=300 golden set detects 0.02 effect @ 80% power. Wilcoxon signed-rank for bounded/skewed metrics. FWER correction needed for multi-comparison. evalstats (114★, 2026) implements PPI-corrected Wilcoxon for LLM-judge bias. |
| 5 | "HAQA/HALO/LLM Checker usable" | **MIXED** | HAQA (ICLR 2026): paper only, code "will be released" — NOT available. HALO (AAAI 2026): circuit-level timing-aware quant, no public library. **LLM Checker (signerless, MIT, 2,892★) = ONLY production-ready recommender** (200+ catalog, 33k registry, 4D scoring, calibration routing). |
| 6 | "CARS metric right choice" | **REFUTED** | soul-bench CARS: 1★, 0 forks — abandoned personal project. Use instead: Joules/token, tokens/Joule, Energy-Delay Product (EDP = E × latency). |
| 7 | "No sovereign bench framework" | **VERIFIED** | SovAIHub/PrivateAIEdgeGallery/TrueFoundry are *deployment* frameworks, not benchmarking. True white space: air-gapped suite w/ local judges + bundled data + zero network calls. |

**Landscape verdict**: FRAGMENTING monthly, not consolidating. MMLU dead (88–94% saturation).

---

## §2 Best-Practice Findings for Future Engine Benchmark Suite

**Statistics (highest-confidence findings):**
1. **Pair everything.** Per-scenario deltas cancel difficulty variance — "cheapest statistical upgrade" (Basedash postmortem: their eval couldn't detect a 7-pt regression; MDE was ~10 pts while they made 2-pt decisions).
2. **Compute Minimum Detectable Effect BEFORE trusting any comparison.** Half the effect size = 4× the samples (quadratic).
3. **Wilcoxon signed-rank > paired t-test for bounded metrics** (accuracy 0–1, skewed distributions). t-test OK when N>30 via CLT on averaged binary scores.
4. **PPI-corrected inference** (evalstats) calibrates p-values against LLM-judge bias using small human-label sets — only known implementation of PPI-corrected rank tests.
5. **Model correlation structure**: scenarios sharing fixtures fail together; independent resampling gives flat-out-wrong CIs.
6. **Grader noise compounds** — budget for it.

**Architecture:**
7. **Tiered profiles mandatory on 5700U-class hardware**: smoke (~15 min) / standard (~2 hr) / comprehensive (~24 hr). Full suite ≈ 1,500–3,000 CPU-hours = infeasible.
8. **Wrap, don't adopt**: lm-eval (MIT, 13k★) as runner core; BFCL/RULER as task sources; independent verification layer on top ("Benchmarking the Benchmarks", Jul 2026, proves evaluators disagree with expert trace-level judgment).
9. **Pin benchmark versions in WADs**, update quarterly. lm-eval monthly cadence + benchmark fragmentation = maintenance hell otherwise.
10. **True air-gap requires bundled datasets**: lm-eval downloads from HF at runtime by default. Zero-telemetry ≠ sovereign unless data+judges+models all local.

**Energy (relevant to ratified LI workstream Tier 0/1/2 matrix):**
11. RAPL-only phase-aligned metrics are viable on CPU: split prefill (first-token boundary) vs decode via cumulative µJ counters; Scaphandre optional for per-process attribution.
12. Report Joules/token + EDP alongside tokens/s — wall-power measurement (~5% accuracy w/ Kill-A-Watt class meters) beats vendor telemetry assumptions.

---

## §3 Flagged Important — Never Executed (Build Backlog)

**P0 (was Weeks 1–4, ~200 hrs total) — NOT STARTED:**
- **Omega Benchmark Harness Core** (~120 hrs): thin wrapper over lm-eval + BFCL + RULER; entity-specific profiles (run-as-Jem vs run-as-Roc weightings); WAD packaging (`config/wads/benchmark/<suite>.xoe`); local judge integration via evalstats PPI-corrected tests.
- **Tiered Benchmark Profiles** (~80 hrs): smoke/standard/comprehensive with CPU/GPU auto-detection. Prereq for anything else on 5700U.

**P1 (was Weeks 4–10, ~350 hrs) — NOT STARTED:**
- **Sovereign Benchmark Suite** (~200 hrs): curated local datasets (no HF runtime download), bundled judges, air-gapped execution, RAPL energy tracking. Fills verified Claim-7 white space.
- **Quantization Recommender** (~150 hrs): integrate LLM Checker (only usable lib) + HALO paper logic + TokenPowerBench energy models → single CLI. NOTE: overlaps ratified LI workstream Tier 0/1/2 matrix — coordinate with sibling session to avoid double-build.

**P2 (Weeks 10+, ~300 hrs) — NOT STARTED:**
- **DPO-Driven Selection**: benchmark→deployment→soul-distillation feedback loop. Identified as THE Omega moat ("no one has built a benchmark suite that learns from your deployments").

**KILL LIST (ratified by verification, never formally closed):**
- CARS metric — refuted, abandoned upstream. Delete from any plan docs.
- "Single standard" assumptions for long-context (RULER-only) and function-calling (BFCL-only).
- Full-suite-on-CPU ambition.
- Direct HAQA/HALO library integration (papers only — monitor for code release).

**Coordination flag for kali**: sibling benchmark-mining session should own §2 best-practice incorporation into LI matrix; this delta is the evidence base. Licensing all-clear stands: lm-eval MIT, BFCL/RULER/TokenPowerBench Apache-2.0, LLM Checker MIT — all bundle-compatible.

---
**FILE COMPLETE** — 3 sections + header. Evidence base: 28+ sources (arXiv, GitHub, HELM/BFCL leaderboards, enterprise reports), gathered via live search 2026-08-16 session. No parametric synthesis.
