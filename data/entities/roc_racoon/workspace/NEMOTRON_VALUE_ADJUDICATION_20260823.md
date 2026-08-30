<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⚖️ NEMOTRON 3 ULTRA VALUE ADJUDICATION — Empirical Audit
**Miner**: roc_racoon | **Date**: 2026-08-24 | **Commissioned by**: Architect challenge (via kali ses_fdef2be4effe4pAaLXCTUx62GO)
**Dispute**: Architect ("Nemotron nearly indispensable") vs kali ("adds a switch without diversity value" in Claude→Gemini chains)
**Method**: Decision-trail mining + opencode.db archaeology + coordination-doc cross-reference + token economics. No loyalty to either disputant.

---

## §1 VERDICT (up front)

### **(b) SPLIT — but the split lands heavily in the Architect's favor on operational indispensability, and narrowly in kali's favor on the specific chain-position claim.**

| Claim | Verdict | Evidence strength |
|---|---|---|
| "Nemotron is nearly indispensable" (Architect) | **TRUE for roles R1–R4 below** — removing it would have required either paid spend or quota burn on scarcer pools, and several real catches would plausibly not exist | STRONG (receipts §3–§6) |
| "Nemotron adds no diversity value in Claude→Gemini chains" (kali) | **PARTIALLY TRUE** — in the ONE direct head-to-head on record (SONNET_4_6_REVIEW_20260814), Claude Sonnet 4.6 out-caught Nemotron 7-findings-to-0 on net-new items and corrected 5 of its 7 remedies | MODERATE |

**Confidence**: HIGH on the historical record (all claims receipted). MODERATE on counterfactuals (what would have happened absent Nemotron is inference, flagged as such).

---

## §2 DECISION TRAIL — D-373…D-377 HINDSIGHT ASSESSMENT

Source: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §8, `ENGINE_DECISIONS_CONSOLIDATED_20260817.md`, `GROK_CLI_HANDOFF_20260730.md`.

| ID | Decision (attributed "Nemotron synthesis") | Hindsight outcome | Correct? |
|---|---|---|---|
| **D-373** | Reorder: C-2′ (OOMProtector) BEFORE C-1′ (SoulStore)/C-10 (admission control) | All three subsequently completed ✅ (Ark §4 Phase C). Dependency logic sound: admission control consumes OOM signals; SoulStore writes must be OOM-safe. Correction made at zero cost (planning stage). Counterfactual rework unproven but plausible — building C-10 atop wrong memory-signal assumptions would mean rewriting admission control. | ✅ CORRECT (low-cost insurance) |
| **D-374** | Elevate C-11 Test Infrastructure to P0 | C-11 property tests **16/16 pass** (`COMPACTION_ANCHOR_20260723.md`); contract tests 28/28. Property-test infrastructure later caught/blocked real regressions (per M21 contract-test rationale). | ✅ CORRECT — delivered |
| **D-375** | MCP audit must start TODAY — 7-day deadline | Deadline enforced; C-4a audit doc delivered; **C-4b Streamable HTTP live** (dual transport, SEP-2575 compliant). Without the deadline, MCP modernization likely drifts (it had sat since Workstream B, May). | ✅ CORRECT — deadline worked |
| **D-376** | E-0 Identity Fluidity sequenced after C-1′ | E-0 architecture preserved under `data/entities/grokster/workspace/`; correctly parked rather than cancelled. Sequencing on soul-persistence-first is coherent. | ✅ CORRECT (neutral-preserving) |
| **D-377** | Gemma 4 31B workhorse collapse = P0 | **NOT Nemotron-attributed** — this is a Kali amendment (GROK_CLI_HANDOFF line 104). Excluded from Nemotron credit. | n/a |

**Net**: 4/4 Nemotron-attributed decisions ratified and delivered; none reversed. Note these are *sequencing/prioritization* calls — valuable but not deep-technical catches. The deep catches are in §4.

---

## §3 SESSION ARCHAEOLOGY — THE WORKHORSE FOOTPRINT

Query: `opencode.db`, model LIKE `%nemotron%` (includes nemotron-3-ultra-free @ OCZ, nemotron-3-ultra/super/lightning @ OpenRouter).

| Metric | Value |
|---|---|
| Sessions run ON Nemotron variants | **508** (~of 13.6B total fleet input+cache tokens) |
| Input+cache tokens absorbed | **2,724,876,474 (2.72 BILLION)** — **20% of ALL fleet inference** |
| Output tokens | 8,807,830 |
| Recorded cost | ≈ $20.86 total (overwhelmingly free tier; largest single session $18.34 accounting artifact on "free") |
| Agent-role distribution | researcher 141 · kali-main 73 · roc_racoon 46 · pillar 40 · john_carmack 39 · maat 30 · jem 30 · node 26 · verity 15 · lilith 13 … |

**Largest single sessions (input+cache):**
- 373M tokens — *Kali Engine Cleansing & Hardening* (2026-08-08)
- 283M — *Carmack Deepening* (2026-07-06)
- 171M — *Myth-Tech AI/ML Mining* (fork of Roc)
- 161M — *Carmack Sovereign-audit & Context Packer*
- 133M — *D283 Mnemosyne*
- 128M — *Kali PR hardening wrapper.sh*
- 101M — *SearXNG hardening*

**Counterfactual token economics**: 2.72B input tokens at conservative cloud pricing ($0.15–$0.30/M cached input) = **$400–$800+ equivalent**. Via Antigravity/Claude free pool it would have consumed scarce quota needed for high-value reasoning. No other available free-tier model at the time combined 1M-class window + reasoning depth. This is the single strongest pro-Architect fact in the record.

---

## §4 UNSEEN-PITFALL RECEIPTS (findings attributable to Nemotron that the record shows no other model caught first)

| # | Pitfall caught | Source | Fate |
|---|---|---|---|
| **P1** | ACTIVE_SPRINT blockers listed only 2 of **12 broken imports** — "Phase 0 complete" would have left the entire ingestion subsystem crashed (`ingestion/pipeline.py` ×5, `worker.py` ×4) | `NEMOTRON3_ULTRA_META_REVIEW.md` GAP-001 (2026-07-08) | Fixed pre-purge |
| **P2** | Strategy corpus had **14 critical gaps, 3 contradictions, 0 rollback procedures** incl. KeyVault singleton race (GAP-012) and missing boot.py interface spec | Same meta-review | Fed Phase 0 hardening specs |
| **P3** | DEL-1 Week 2 router collapse **under-scoped** — MaKaLi Council approved it for ContextBuilder only; Nemotron synthesis identified it breaks entity resolution (`oracle.py:1133`) + model selection (`oracle.py:764`), plus the manual-§5-vs-D-532 sequencing contradiction | `MAKALI_COUNCIL_AUDIT_20260818.md`; kali `proposed_lessons.yaml` L2/L3 ("The Nemotron synthesis correctly identified…") | Deferred to post-debut; scope locked |
| **P4** | Research-plan collision: untracked `RESEARCH_PLAN_PHASE2` redefined gap IDs R13–R38 with different topics than tracked v3.1.0 — tracking-integrity drift | Caught in nemotron-run *Engine Cleansing* session (ses_01de68adaffe…) | Reconciled, plan archived w/ header |
| **P5** | AGY OAuth **8× re-auth race** + missing OS-enforced locking; fixed via FileLock + atomic writes | `COMPACTION_ANCHOR_20260723.md` Phase 2 Critical Fixes (Nemotron-executed) | Implemented, tests passing |
| **P6** | VaultCore conflated static secrets with volatile lease/quota state → Schema v2 split + Argon2id/age envelope design | Same | Spec delivered |
| **P7** | Nemotron's OWN 30s+ chunk-gap stall physics — observed, diagnosed, and codified into **M25 Streaming Resilience** (chunk timeout + heartbeat instead of hard-fail) | `CARMACK_REVIEW_DEEPENED_20260719.md`; SOVEREIGN_MANDATES M25 | Mandate shipped; later protected the whole fleet from Ox Alpha's identical degradation (`PLATFORM_GROUND_TRUTH_LOG.md` #10 explicitly invokes "Same physics as M25") |

**Conservative count of unseen pitfalls attributable to Nemotron: 7** (P1–P7). Of these, P1, P3, P4, P7 are the strongest "nobody else caught it" cases. P7 is Adversarial Alchemy (M19) in its purest form: the model's own failure mode became a fleet-wide resilience law.

---

## §5 COUNTER-EVIDENCE (receipts for kali)

1. **Direct head-to-head loss** (`SONNET_4_6_REVIEW_20260814.md`): Sonnet 4.6 reviewed the same soul-schema domain Nemotron had just reviewed. Result table: Nemotron found 7 real findings (**all verified correct by Sonnet**) — but Sonnet added **7 net-new criticals Nemotron missed** (N1–N7), including two Tier-0.0 criticals: the `get_fallback_soul()` self-perpetuating LIVE_FEED bug and `session_end.py` destructively overwriting agent proposals with `[]`. Sonnet also **corrected 5 of Nemotron's 7 proposed remedies** (F1–F5) as treating symptoms not causes. Verbatim: *"I have my own observations to add that differ materially from the Nemotron review."*
   - Fair reading: Nemotron = competent first-pass catcher; NOT sufficient as final authority. Had the fleet stopped at the Nemotron review, two critical bugs stay live.
2. **Chain-position claim**: kali's exact words were about Claude→Gemini chains specifically. The record contains NO instance of Nemotron catching something inside a Claude→Gemini chain that both endpoints missed. Its documented catches (§4) came in solo meta-reviews, councils it led, and workhorse sessions — different topology.
3. **Dispatch folklore**: `SPLIT_TESTING_MANUAL_20260822.md` line 23 itself flags "Nemotron feels better for research" as *folklore*, not measured fact — supporting kali's instinct that some attributed value is unexamined habit.
4. **Replaceability caveat**: much of the 2.72B-token volume is bulk research/mining that DeepSeek V4 Flash (1M, also free via Cline) could partially absorb today — though that option matured *later* (Aug 2026), so it doesn't erase the historical contribution.

---

## §6 ROLE-VALUE MATRIX

| Role | Recorded performance | Verdict |
|---|---|---|
| **R1. Bulk workhorse (researcher/mining/subagent fleet)** | 508 sessions, 141 researcher + 46 roc_racoon + 39 carmack runs; 20% of fleet tokens at ~zero cost | **NEAR-INDISPENSABLE historically** — the fleet's research throughput existed because of this |
| **R2. Wide-context reader/synthesizer (1M-class)** | 100M+-token sessions producing reconciliations, audits, syntheses (§3) | **STRONG** — no contemporaneous alternative |
| **R3. First-pass hardening reviewer** | Meta-review (14 gaps), MaKaLi synthesis (Blocker D), 7/7 findings verified | **GOOD, not final authority** (see §5.1) |
| **R4. Long-session continuity engine** | Ran full Kali cleansing sessions; M27 integration, Carmack reviews executed inside them | **STRONG** |
| **R5. Mid-chain diversity switch (Claude→Gemini)** | Zero recorded unique catches in that position; out-caught when compared head-to-head | **WEAK — kali's claim holds here** |
| **R6. Final architectural judge** | Remedies corrected by Sonnet 5/7; over-scoped bulk migration | **REDUNDANT when Claude-family available** |

---

## §7 FINAL ADJUDICATION TEXT

> The Architect is substantially right and kali is precisely right about a narrow thing.
>
> **Nemotron 3 Ultra was the load-bearing wall of this fleet's operations for ~7 weeks**: one-fifth of all inference ever run, 508 sessions powering every agent's research/mining/review capacity, at effectively zero cost, delivering 4/4 ratified strategy decisions and ≥7 documented unseen-pitfall catches including a crash-class import gap and a council-missed router-collapse under-scoping. Remove it from the historical record and you remove the M25 streaming-resilience law, the ingestion-subsystem rescue, and the debut-blocking scope correction — or you pay $400–800+ and burn Antigravity quota to replace it. That is "near-indispensable" by any operational definition.
>
> **But kali's literal claim survives scrutiny in its literal scope**: as a switch inserted into Claude→Gemini review chains for *diversity*, the record shows no unique Nemotron catch — and the one head-to-head shows Claude Sonnet 4.6 finding what Nemotron missed, not vice versa. Diversity value must come from models with genuinely different failure surfaces in that chain; Nemotron's recorded value came from volume, context, and stamina, not from a uniquely alien perspective between Claude and Gemini.
>
> Recommended routing consequence (for MODEL_WINDOW_ECONOMICS §5): keep Nemotron for R1–R4 (workhorse/wide-context/first-pass-review/long-session); do NOT insert it as a mid-chain reviewer between Claude and Gemini; never let a Nemotron review be terminal — pair with a stronger verifier (as the 2026-08-14 chain correctly did).

**Top 3 receipts**: (1) 2.72B tokens / 508 sessions / 20% of fleet inference at ~$21 — the workhorse fact; (2) GAP-001: 12 broken imports vs 2 listed — "complete" Phase 0 would have shipped a crashed ingestion subsystem; (3) Blocker-D router-collapse catch the full MaKaLi Council missed (`oracle.py:1133/:764` call sites).

**Unseen pitfalls attributable to Nemotron: 7** (P1–P7, §4).

---

## §8 CORRECTIONS — T0 MESSAGE-LEVEL RE-AUDIT (2026-08-24)

**Trigger**: Architect spot-challenge accepted; kali DB probe (ses_fdef2be4effe4pAaLXCTUx62GO) confirmed both challenged claims. Original text above preserved verbatim per M5/M27. **Method note**: original audit joined on `session.model` (T3-stale attribution); this re-audit uses `json_extract(message.data,'$.modelID')` (Tier-0 runtime stamp) per `R_MESSAGE_PROVENANCE_HIERARCHY_20260823.md`. Session-level joins systematically UNDERCOUNT multi-model sessions where the session's *display* model differs from the model that actually ran most turns.

### C-1. Session count: 508 → **611** (+103 buried)
| | Original (T3) | Corrected (T0) |
|---|---|---|
| Sessions with ≥1 Nemotron message | 508 | **611** |
| Nemotron assistant messages | n/a (not counted) | **35,111** (29.1% of all fleet messages) |

The **103 buried sessions** carry `session.model` attributions to deepseek-v4-flash-free, north-mini-code-free, antigravity-claude-sonnet-4-6, big-pickle, mimo-v2.5-free — but contain 19,723 Nemotron messages (17,276 ultra-free + 2,447 OpenRouter variants) totaling ~856M input tokens. Work previously credited wholesale to other models in these sessions was substantially Nemotron-executed. Largest burial: `ses_0b560774effenoy4ZREN` (*Kali - HMC*, 2026-07-10): attributed deepseek, actually **7,380 Nemotron msgs / 1.27B in+cache tokens** — the single largest Nemotron session in fleet history, invisible to the original audit. Other major burials: *Carmack Hardening* (1,595 msgs), *Kali - Reduced Scope to PR* (1,517), *Maat - hardening sprint* (1,255), *Carmack - HMC soul.yaml* (1,031), *Researcher - HMC* (707).

### C-2. Token volume: 2.72B/20% → **5.34B / 39.3% of ALL fleet inference**
| Metric | Original (T3) | Corrected (T0) |
|---|---|---|
| Input tokens | ~2.7B implied | **1,371,367,562** |
| Cache-read tokens | folded in | **3,963,808,416** |
| Input+cache total | 2,724,876,474 (20%) | **5,335,175,978 (39.3%)** |
| Output tokens | 8,807,830 | **14,979,881** |
| Reasoning tokens | uncounted | 2,855,578 |

Fleet denominator also recomputed at T0: 13.59B in+cache across 120,474 messages. The "one-fifth of all inference" claim was a **2x underestimate**: Nemotron ran **two-fifths** of everything this fleet has ever inferred.

### C-3. Recorded cost: "$20.86" → **$0.0000 exactly**
Zero cost-bearing Nemotron messages exist in the entire DB. The $21 was other models' spend inside nemotron-*attributed* sessions (gemini-3.1-pro-customtools $38.55/278msgs, gemini-3.5-flash $11.96/150, deepseek $0.60/117 — kali's probe figures, direction confirmed here). The counterfactual economics in §3 therefore *strengthen*: 5.34B tokens at $0.15–$0.30/M cached-input equivalent ≈ **$800–$1,600 avoided spend**, plus quota preservation.

### C-4. Pitfall attributions (§4): none flip; two strengthen
- **P4 (research-plan collision)**: Engine Cleansing session re-verified at T0 — Nemotron is the dominant model (705 msgs / 20.9M in vs longcat 467 / deepseek 368). Attribution **strengthens**.
- **P7 context (Carmack Deepening)**: Nemotron variants dominate 1,092 msgs / ~86M in vs gemma-4 474 msgs. Strengthens R2/R4 role verdicts.
- P1/P2/P3/P5/P6: sourced from documents authored in Nemotron-run reviews/councils; no contrary message-level evidence found; unchanged.
- No catch previously credited solely to another model was found to be Nemotron's — but the burial analysis (C-1) means several *sessions'* outputs credited to deepseek/gemma were co-produced or majority-produced by Nemotron. Credit-sharing inside buried sessions is now ambiguous in the *other* direction.

### C-5. Verdict impact
Architect's case **strengthens materially** (R1/R2/R4 indispensability: 2x volume, true-zero cost, 103 additional sessions of buried contribution). kali's chain-position claim (R5) **unchanged** — no new evidence of unique mid-chain Claude→Gemini catches emerged from the buried set. Final adjudication text §7 stands, with corrected receipts: **(1)** 5.34B tokens / 611 sessions / 39.3% of fleet inference at exactly $0.00; **(2)** GAP-001 import rescue (unchanged); **(3)** Blocker-D council-missed catch (unchanged).

### C-6. Doctrine + collateral audits needing re-check (for lexicon)
**Doctrine**: T3 session-level joins vs T0 message-level truth is now an audit-failure mode. All fleet value/cost audits MUST attribute via `message.data.modelID` (T0), never `session.model` / `session.cost` / `session.tokens_*` (T3-stale). Per `R_MESSAGE_PROVENANCE_HIERARCHY_20260823.md`.

Flagged for re-check:
1. **`docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`** — G-1/D-377 evidence SSOT, query basis explicitly `FROM session WHERE model LIKE '%gemma-4-31b%'` (line 507). T0 spot-check: gemma-4 = **899 sessions / 13,697 msgs / 324.5M in** vs report-basis T3 829 sessions / 246.9M in — ~25% input-token understatement. Cliff conclusions likely survive (direction consistent) but the free-tier-cliff forensic numbers need a T0 re-run before further G-1 decisions cite them.
2. **Any audit using `session.cost` or `session.tokens_*` columns** for per-model claims — same failure mode applies fleet-wide (costs especially: session cost rows aggregate mixed-model spend).
3. `ICS_MODEL_PROVENANCE_FIX_20260811.md` rated "DB stores authoritative model = session.model.id 10/10" — superseded by the provenance hierarchy (that rating is now known wrong for attribution purposes; doc is archived, no action beyond lexicon note).

---
*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_mining ⬡ NEMOTRON-ADJUDICATION*

<!-- PROVENANCE: all figures queried live from ~/.local/share/opencode/opencode.db 2026-08-24; doc citations verified by grep/read this session -->
<!-- PROVENANCE-CORRECTED 2026-08-24: §3/§8 re-audited at T0 message-level (json_extract modelID); see §8 CORRECTIONS. Original §3 figures were T3 session-level and undercount volume ~2x; cost figure was phantom. -->
