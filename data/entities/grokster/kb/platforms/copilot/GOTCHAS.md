<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# GitHub Copilot — Gotchas (Trap → Evidence → Defense)

**KB Entry**: grokster/platforms/copilot/GOTCHAS
**last_verified**: 2026-08-26 · **rot_class**: medium (add on every incident; re-check promo dates monthly)
**Scope**: Known traps operating Copilot as a house provider. Format: TRAP → EVIDENCE → DEFENSE. Confidence tagged.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md §D/§F/§G; github/copilot-cli issues #1523/#1540/#2591/#2881/#2969/#4308; opencode issues #20759/#34644; docs.github.com billing pages.

---

## G-COP-01 · Auto-only plans are dead ends
**TRAP**: Provisioning a Free/Student account expecting explicit model selection via API.
**EVIDENCE**: anomalyco/opencode #34644 (house-verified); docs: Free/Student = auto model selection only.
**DEFENSE**: Paid plan (Pro minimum) required for any house account. [HIGH]

## G-COP-02 · Per-tool-call billing surprise (the 87-for-6 incident)
**TRAP**: Assuming 1 user prompt = 1 billed unit. Agentic harnesses bill EVERY internal model call — tool invocations, thinking steps, subagent turns, background compaction.
**EVIDENCE**: copilot-cli #2591 — single prompt → 80–100 billed requests; confirmed overbilling bug Apr 7–11 2026 (experimental feature, refunds issued); quota-tracker corruption reports persisted weeks after.
**DEFENSE**: Never run agentic loops through Copilot CLI (PLAYBOOK §3). Through OpenCode, budget by tokens not turns; check billing dashboard deltas after first runs of any new workload. [HIGH]

## G-COP-03 · Autopilot/runaway loops wipe quotas
**TRAP**: Unattended agent hits an unresolvable state → system re-prompts every few seconds → each iteration bills until 402 "no quota".
**EVIDENCE**: #1523 (~500 wasted turns/15 min), #1540 (overnight full-quota wipe), #2881 (17 reqs/2.5 min), #2969 (~50 iterations through compaction). Partial fix v1.0.4; regressions through v1.0.36+.
**DEFENSE**: Headless only with `--max-ai-credits` + wall-clock timeout + acceptance gate; never auto-raise limits; treat exhaustion as human-review signal. [HIGH]

## G-COP-04 · Post-task background consumption
**TRAP**: Session keeps burning credits after visible work completes (subagent finalization, compaction accounting).
**EVIDENCE**: #4308 (v1.0.75, Aug 2026): 97.8%→100% with zero user interaction.
**DEFENSE**: Close/idle-timeout sessions promptly; don't leave metered sessions open overnight. [MEDIUM — single report]

## G-COP-05 · gho_ vs ghu_ exchange failure
**TRAP**: Feeding OpenCode's OAuth App token (`gho_`, client `Ov23li8tweQw6odWQebz`) to `/copilot_internal/v2/token` → 404; or valid `ghu_` without matching identity headers → 400 "model not supported".
**EVIDENCE**: opencode #20759/#20758; per-client-ID server-side model allowlists.
**DEFENSE**: Use the builtin provider's own flow (sanctioned). For custom integrations use `Iv1.b507a08c87ecfe98` + VS Code headers (ARCHITECTURE §5). [HIGH]

## G-COP-06 · Hardcoding proxy-ep base URLs
**TRAP**: Hardcoding `api.githubcopilot.com` (legacy host) breaks Business routing (`api.business.githubcopilot.com`) and future endpoint migrations.
**EVIDENCE**: opencode `base()` hardcode bug (#20758); token carries authoritative `proxy-ep=` and `endpoints.api`.
**DEFENSE**: Always derive base URL from exchanged token fields. [HIGH]

## G-COP-07 · Promo-expiry cost cliffs
**TRAP**: Cost models built on promotional pricing silently break.
**EVIDENCE**: GPT-5.6 Sol −50% expires **2026-09-03**; Gemini 3.6/3.7 Flash promo expires **2026-12-31**; Business/Enterprise boosted pools (3,000/7,000) expire **2026-09-01**.
**DEFENSE**: Re-verify pricing table monthly (RESEARCH_TARGETS cadence); never bake promo rates into standing budgets. [HIGH]

## G-COP-08 · Enterprise-slot assumption unverified
**TRAP**: Building two-individual-account workflows on slot 2 before proof.
**EVIDENCE**: Fallback-to-individual-endpoint pattern exists in pi/rab-agent implementations, but OpenCode's enterprise loader behavior untested in-house.
**DEFENSE**: Gate on probe L4-a; until then treat slot 2 as GHE-only. [UNVERIFIED]

## G-COP-09 · Session-limit false security
**TRAP**: Treating `--max-ai-credits` as a hard ceiling.
**EVIDENCE**: Official docs: soft cap — in-flight response finishes before enforcement; GitHub guidance ≥30 because most calls cost >20 credits; limit does NOT persist across resume (null = no limit).
**DEFENSE**: Pair with user-level budget (the only always-hard control); re-set limit on every resume; set below true ceiling with overshoot headroom. [HIGH]

## G-COP-10 · Flex-allotment permanence assumption
**TRAP**: Modeling Pro=$15 / Pro+=$70 / Max=$200 credit value as fixed income.
**EVIDENCE**: docs.github.com: flex allotment is explicitly variable ("adapts as the economics of AI evolve").
**DEFENSE**: Budget against BASE credits only; treat flex as bonus. [HIGH]

## G-COP-11 · Annual-plan legacy pricing
**TRAP**: Applying AI-Credit math to annual Pro/Pro+ subscribers — they remain on premium-request multipliers (raised Jun 1) until expiry.
**EVIDENCE**: docs.github.com models-and-pricing legacy section; thenewstack.io analysis.
**DEFENSE**: Check subscription type before cost modeling. [HIGH]

## G-COP-12 · Mobile-purchased plans can't buy overage
**TRAP**: Subscriptions bought via GitHub Mobile iOS/Android cannot purchase additional AI credits — hard stop at allowance.
**EVIDENCE**: docs.github.com usage-based-billing note.
**DEFENSE**: Avoid Mobile-channel subscriptions for house accounts. [HIGH]

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
