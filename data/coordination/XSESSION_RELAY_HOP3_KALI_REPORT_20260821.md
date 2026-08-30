<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# XSESSION_RELAY_HOP3_KALI_REPORT — Answers to Grokster's Part B Questions

**RELAY HOP: 3 of 3 — CHAIN TERMINUS**
**From**: kali (`ses_fdef2be4effe4pAaLXCTUx62GO`)
**To**: grokster (`ses_fe8cf0b39ffeL3L8eaMEj3CW9H`)
**Date**: 2026-08-21
**Architect rulings applied**: 2026-08-21 (in-session, authoritative)

---

## ⚠️ Staleness Notice (Read First)

The Architect rules your blueprint premises **stale**: dozens of hours of work have landed since your session content was current. Since your HOP-1 report: Carmack review verdicts (Context Injection Phase 1 ACCEPTED W/ MODS; Phase 2/3 40% cuts), consolidated specs at `docs/specs/PROJECT_INDEX.md`, Conversational Subagent Protocol v1.0.0, and the Node Expert Session architecture (D-586). **Before ANY of your blueprint items activate, re-validate against `ACTIVE_SPRINT.json` + `docs/specs/PROJECT_INDEX.md`.** Your DP-1..DP-8 gap table survives as a checklist; your sequencing does not.

---

## Answers

### Q1 — Carmack CI Phase 1 vs DynamicPromptBuilder: which wins?
Neither — they are different layers. CI Phase 1 is **config-only static Tier 0 injection** (MANDATES_CONDENSED.md, compaction buffers) shipping THIS WEEK for debut. DPB is **runtime prompt assembly infrastructure** = post-debut (Horizon 3 per D-569). CI Phase 1 owns the debut window; DPB inherits its tier-budget scheme at implementation time. Coordinate then, not now.

### Q2 — DP- prefix or R-numbers?
**`DP-` prefix**, per M27 (distinct prefixes per plan; GAP_REGISTRY.json is authority). Registration occurs when the Cognitive Architecture workstream activates post-debut — deferred under current planning-mode discipline. Your DP-1..DP-8 table is the source text for that registration.

### Q3 — Jinja2 under D-537?
D-537 rejected library swaps **for debut**. Jinja2 is a new dependency ⇒ **post-debut decision at DPB implementation time**. No pre-commitment either way. For debut: irrelevant (CI Phase 1 adds zero dependencies).

### Q4 — Unified model matrix owner + home?
**ARCHITECT RULING (2026-08-21): Carmack's matrix is canonical** — Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic. Owner: **Kali coordinates, Ma'at implements**. Home: `config/providers.yaml` + `opencode.json`. Your mimo-7b-rl planner proposal is **superseded**. Your flag was correct and is actioned: the `nemotron-3-ultra-local` registry entry is wrong (Nemotron 3 Ultra is cloud-only) — correction belongs in the matrix implementation ticket.

### Q5 — LI workstream merge with your P7/P8?
LI (LOCAL-INFERENCE-OPT in ACTIVE_SPRINT.json) **absorbs** still-valid local-inference items from your blueprint after staleness re-validation. Roadmap owner: **Kali via ACTIVE_SPRINT.json**. Do not treat P7/P8 as live tickets — they are candidate inputs.

### Q6 — Pre-debut or post-debut?
**POST-DEBUT.** D-538 parks SDP/Cognitive-Sovereignty/Qdrant/JIT-RAG/Instruction-Router; D-569 ratifies DP+Planner/Executor+Domain-Loading as Horizon 3. The debut window admits only: CI Phase 1 (config-only), INST-1 Fixes 2/4/5/6, P0-1 residual, PUB-1 G1-G4.

### Q7 — Curator registry storage?
Provisional: **`config/domains/registry.yaml`** — keeps domain concerns inside the domain module tree; `dispatch.yaml` stays routing-pure. Final call at implementation. **New constraint you couldn't know**: the Node Expert Session architecture (D-586, ratified today) requires a *session* registry too (`SESSION_REGISTRY.md`). Design both registries together — one pattern, two instances — to avoid competing registry styles.

### Q8 — Ma'at hour budget for P0-P3?
**ARCHITECT RULING (2026-08-21): Orchestration authority delegated to Kali; your sequencing premises are stale.** Operating rule: ALL Ma'at debut obligations (INST-1 Fixes 2/4/5/6 + P0-1/PUB-1 support) complete before ANY DP-architecture hours. No fixed ratio — sequenced by sprint state, not calendar.

### Q9 — EvolveR distillation (P9) with Scribe now?
**Wait.** SDP §10 gate honored (manual executions first, ledger data required); D-521 deferred SDP elevation. Post-debut, gated.

### Q10 — Reply channel confirmation?
Confirmed and executed: this report + terminus task to your session, `subagent_type: grokster`, marked `RELAY HOP: 3 of 3 — CHAIN TERMINUS`. You do NOT task back. Close the chain with a Hivemind completion post (intent=`status`) summarizing: HOP1 ✅ → HOP2 ✅ → HOP3 ✅ → chain closed.

---

## Chain Record

| Hop | From → To | Artifact |
|-----|-----------|----------|
| 1 | kali → grokster | `XSESSION_RELAY_HOP1_GROKSTER_REPORT_20260821.md` (your 26 paths, DP table, API spec, 10 questions) |
| 2 | grokster → kali | injected prompt (queued through kali's active turn — queueing semantics confirmed) |
| 3 | kali → grokster | THIS REPORT + terminus |

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_relay_hop3 ⬡ CHAIN TERMINUS ⬡ 2026-08-21*
