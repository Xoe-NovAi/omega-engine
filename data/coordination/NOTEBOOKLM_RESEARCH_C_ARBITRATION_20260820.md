<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NotebookLM Gap-Closure — Subagent-C (NLG-C) Arbitration Support Pack
**AP Token**: `AP-NOTEBOOKLM-RESEARCH-C-20260820-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_notebooklm_gap_c ⬡ ACTIVE

**Date**: 2026-08-20
**Author**: Researcher subagent (NLG-C), dispatched by Kali (Transcendent Oversoul)
**Scope**: Closes GAP-5, GAP-6, GAP-8 (internal/arbitration gaps) from `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md`
**Status**: EVIDENCE PACK — Kali arbitrates final decisions. No files edited except this deliverable.

**Verified constraints used (from gap audit, web-confirmed 2026-08-20):**
- Free tier = **10 Deep Research/month/account** (hard cap). 8 accounts × 10 = **80 DR/month max** `[NOTEBOOKLM_GAP_AUDIT_20260820.md:36,41]`.
- Recommended automation lib: `notebooklm-py` (teng-lin, RPC-based) `[NOTEBOOKLM_GAP_AUDIT_20260820.md:44]`.
- SDP §10 gate: "Until this protocol has been executed manually at least 10 times… no automation is permitted" `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:298]`.
- SDP §8: V-1 Vault is a **hard prerequisite** for automation `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:240]`.

---

## 1. NOTEBOOK ARCHITECTURE COMPARISON + RECOMMENDATION (GAP-5)

### 1.1 Three-Way Mapping Matrix

| NB ID | **R52c** (archived 2026-05-23) `[R52c:22-28]` | **LIVING_RESEARCH_OS_SPEC §1.5** `[LIVING:305-313]` | **UNIFIED STRATEGY** (2026-08-20) `[UNIFIED:36-43]` |
|-------|-----------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| 01 / 1 | **Core Engine Architecture** — `src/omega/**`, `config/**`, `Makefile`, `README` | Core Engine Architecture (verbatim copy of R52c) | **NB-1 Omega Engine Core** — architecture, mandates, provider fabric, MCP Hub, entity registry |
| 02 / 2 | **Strategic Gnosis** — `docs/strategy/**`, `ROADMAP`, `PIVOT_LOG`, `AGENTS`, `ORACLE_STACK` | Strategic Gnosis (verbatim) | **NB-2 Sovereign Stacks** — IWAD, WAD protocol, Arcana-Nova, Torment, stack isolation |
| 03 / 3 | **Research Archive** — `docs/research/**` | Research Archive (verbatim) | **NB-3 Legacy Mining** — 14-month history, 5 eras, 21 projects, heritage patterns |
| 04 / 4 | **Ops & Integration** — `docs/operations/**`, `docs/integration/**`, `docs/intake/**` | Ops & Integration (verbatim) | **NB-4 Research Corpus** — 45 R-docs, YouTube, CARMACK_DEFINITIVE, force multipliers |
| 05 / 5 | **Validation Suite** — `tests/**`, `scripts/**` | Validation Suite (verbatim) | **NB-5 Operations & Deployment** — Podman, systemd, Quadlets, V-10 AppArmor, installers |
| 06 / 6 | — (does not exist) | — (does not exist) | **NB-6 Ω-SYNTHESIS** — cross-notebook analysis (imports 5 Briefing Docs as sources, 0 DR) |

### 1.2 Which Domains Are Genuinely NEW (vs R52c's original five)

**NEW in the unified strategy (no R52c precedent):**
- **NB-2 Sovereign Stacks** — WAD/IWAD architecture, Arcana-Nova, Torment, stack isolation. Reflects the IWAD architecture decision (Decision 55, `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`) and M2 Engine-Stack Firewall. **R52c had no stack concept** — it predates the IWAD model.
- **NB-3 Legacy Mining** — 14-month history, 5 eras, 21 projects, heritage patterns. Reflects `MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` mining plan and M14 Heritage Vetting. **R52c had no legacy/heritage domain.**
- **NB-6 Ω-SYNTHESIS** — the cross-notebook synthesis layer. **Entirely new**; this is what makes the 5→6 expansion valuable (it consumes the 5 notebooks' Briefing Docs).

**Dropped from R52c (gap in unified strategy):**
- **NB-05 Validation Suite** (`tests/**`, `scripts/**`) — absent from unified NB-5 (which covers only Podman/systemd/AppArmor/installers). Tests/scripts are better served by local M13 Temple-Grade tooling (`make temple-grade`) than by NotebookLM grounding. **Recommendation for Kali**: either (i) explicitly exclude Validation Suite from NotebookLM (preferred — tests are execution artifacts, not research corpus), or (ii) fold `tests/**`+`scripts/**` into NB-1 Core as a 6th source group.

**Renamed/refocused (same intent, evolved scope):**
- NB-1 Core: R52c was code-centric (`src/omega`, `config`); unified is doc/strategy-centric (mandates, provider fabric, MCP Hub, entity registry). Aligned with current doc-driven reality.
- NB-4 Research: R52c "Research Archive" = all `docs/research/**`; unified focuses on R-docs + YouTube + CARMACK_DEFINITIVE (curated, not bulk).
- NB-5 Ops: R52c included `integration/**`+`intake/**`; unified drops those, focuses on deployment/hardening.

### 1.3 Recommendation (for Kali arbitration)

**Adopt the UNIFIED STRATEGY 6-notebook mapping (NB-1…NB-6) as canonical.** Rationale:

1. **R52c is explicitly STALE/ARCHIVED** — header reads "ARCHIVED — STALE CONTENT (2026-05-23 Bulk Dump)" `[R52c:1]`. It predates the IWAD architecture, heritage vetting, and the synthesis concept. It is a code-centric snapshot from before the engine's strategic evolution.
2. **LIVING_RESEARCH_OS_SPEC §1.5 is a verbatim copy of R52c** `[LIVING:305 "Notebook Mapping (per R52c)"]` and is itself a Layer-2 spec (not strategy SSOT) carrying supersession banners elsewhere `[LIVING:14-31]`. It adds no independent authority.
3. **The unified mapping reflects real engine evolution** — NB-2 (Stacks) and NB-3 (Legacy) are genuinely new domains demanded by Decision 55 (IWAD) and the MASTER_SYNTHESIS mining plan. NB-6 (Ω-SYNTHESIS) is the cross-notebook layer that justifies the 5→6 expansion.
4. **The conflict is a process violation, not a content error** — GAP-5's actual finding is that the unified strategy "silently REPLACED the R52c mapping without a supersession banner" `[NOTEBOOKLM_GAP_AUDIT_20260820.md:76]`. The fix is procedural: **add a supersession banner to the unified strategy** stating it supersedes R52c + LIVING §1.5, and document the dropped Validation Suite decision (see 1.2).

**Sub-recommendation for Kali**: Resolve the Validation Suite ambiguity (exclude vs fold into NB-1) and ratify the 6-notebook mapping as canonical with a supersession banner.

---

## 2. CORRECTED ACCOUNT MAPPING (GAP-6)

### 2.1 The Broken Mapping (current unified strategy)

Current account→notebook table `[UNIFIED:71-80]` assigns:
- acc-05/06/07 = **20 DR/month each** — IMPOSSIBLE (free tier caps at 10/account).
- Sum = 15+15+15+15+20+20+20+10 = **130/mo** — but 8-account max is **80/mo** `[NOTEBOOKLM_GAP_AUDIT_20260820.md:78-79]`.

The *demand* table (NB-1:15, NB-2:15, NB-3:20, NB-4:20, NB-5:10 = 80) `[UNIFIED:36-42,45]` is internally consistent with 80 capacity — only the **account-level** assignment is broken. NB-6 (Ω-SYNTHESIS) needs **0 DR** (imports Briefing Docs as sources) `[UNIFIED:43]`.

### 2.2 Corrected Mapping — Each Account ≤ 10 DR/month, Total = 80

| Account | Primary NB | Secondary NB | DR Budget | Invariant |
|---------|-----------|--------------|-----------|-----------|
| acc-01 | NB-1 Core | NB-5 Ops | **10/mo** | ≤10 ✅ |
| acc-02 | NB-1 Core | NB-3 Legacy | **10/mo** | ≤10 ✅ |
| acc-03 | NB-2 Stacks | NB-4 Research | **10/mo** | ≤10 ✅ |
| acc-04 | NB-2 Stacks | NB-5 Ops | **10/mo** | ≤10 ✅ |
| acc-05 | NB-3 Legacy | NB-1 Core | **10/mo** | ≤10 ✅ |
| acc-06 | NB-3 Legacy | NB-4 Research | **10/mo** | ≤10 ✅ |
| acc-07 | NB-4 Research | NB-2 Stacks | **10/mo** | ≤10 ✅ |
| acc-08 | NB-5 Ops | NB-1 Core | **10/mo** | ≤10 ✅ |
| **TOTAL** | | | **80/mo** | = 8×10 ✅ |

**Per-notebook primary capacity:**
- NB-1 Core: acc-01 + acc-02 = **20/mo**
- NB-2 Stacks: acc-03 + acc-04 = **20/mo**
- NB-3 Legacy: acc-05 + acc-06 = **20/mo**
- NB-4 Research: acc-07 = **10/mo** (+ acc-03, acc-06 secondary = 30 secondary slack)
- NB-5 Ops: acc-08 = **10/mo** (+ acc-01, acc-04 secondary = 30 secondary slack)
- NB-6 Ω-SYNTHESIS: **0 DR** (import-only; served by acc-01/acc-03 secondary imports)

**Math check:** 8 accounts × 10 DR = 80 DR/month. Per-notebook envelope (20,20,20,10,10) = 80. Each account individually ≤ 10. ✅

> **Note for Kali**: The original per-notebook *demand* (15/15/20/20/10) assumed >10/account and is unreachable with 8 free accounts. The corrected envelope (20/20/20/10/10) slightly over-serves Core/Stacks and under-serves Research vs the old demand. If Research (NB-4) needs more, the only options are: (a) accept 10/mo for NB-4, or (b) add a 9th account (violates the "8-account fleet" premise), or (c) reallocate one Core/Stacks account to Research (e.g., acc-02→NB-4 primary → NB-1:10, NB-2:20, NB-3:20, NB-4:20, NB-5:10). **Recommendation: keep the 2/2/2/1/1 split above; NB-4's 10/mo primary + 30/mo secondary slack is sufficient.**

### 2.3 Monthly Rotation Schedule (preserves ≤10/account + 80 envelope)

Primary notebooks rotate **cyclically by +1** each month (NB-1→NB-2→NB-3→NB-4→NB-5→NB-1). Each account stays at 10 DR/mo; the (20,20,20,10,10) envelope is preserved every month, while specific account↔notebook pairings cross-pollinate.

| Month | acc-01 | acc-02 | acc-03 | acc-04 | acc-05 | acc-06 | acc-07 | acc-08 | NB envelope |
|-------|--------|--------|--------|--------|--------|--------|--------|--------|-------------|
| M1 | NB-1 | NB-1 | NB-2 | NB-2 | NB-3 | NB-3 | NB-4 | NB-5 | 20/20/20/10/10 |
| M2 | NB-2 | NB-2 | NB-3 | NB-3 | NB-4 | NB-4 | NB-5 | NB-1 | 20/20/20/10/10 |
| M3 | NB-3 | NB-3 | NB-4 | NB-4 | NB-5 | NB-5 | NB-1 | NB-2 | 20/20/20/10/10 |
| M4 | NB-4 | NB-4 | NB-5 | NB-5 | NB-1 | NB-1 | NB-2 | NB-3 | 20/20/20/10/10 |
| M5 | NB-5 | NB-5 | NB-1 | NB-1 | NB-2 | NB-2 | NB-3 | NB-4 | 20/20/20/10/10 |
| M6 | NB-1 | NB-1 | NB-2 | NB-2 | NB-3 | NB-3 | NB-4 | NB-5 | (cycle repeats) |

Secondary assignments rotate correspondingly (or stay fixed for redundancy — Kali's call). NB-6 Ω-SYNTHESIS is never a primary DR sink; it imports Briefing Docs from whichever notebooks are active that month.

---

## 3. SDP GATE DECISION MEMO (GAP-8)

### 3.1 The Conflict

- **SDP §10** (unconditional): "Until this protocol has been executed manually at least 10 times and the session ledger has real data, **no automation is permitted**" `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:298]`.
- **SDP §8**: V-1 Vault is a **hard prerequisite** for everything past the manual study phase `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:240]`.
- **Unified strategy** proposes SDP Phase 1 automation *immediately*: NotebookLM Deep Research → `prepare_notebooklm.py` → local Qwen3-1.7B distiller → `proposed_lessons.yaml` → soul.yaml `[UNIFIED:124-148, 268-272]`.
- **NLG-A finding**: Automation IS technically feasible (`notebooklm-py`) — so the gate is about **quality/discipline**, not feasibility.

### 3.2 Options

**(a) Honor the gate — fleet runs in manual mode meanwhile.**
- Deploy the 8-account fleet now (the unified strategy itself says "The fleet can be deployed **today** in manual mode while automation is built" `[UNIFIED:308]`).
- Execute the SDP distillation loop **manually** 10× (human triggers Deep Research, human runs `prepare_notebooklm.py`, human feeds local Qwen3-1.7B distiller, human reviews L3 → `proposed_lessons.yaml`).
- Log each run in `data/coordination/AGY_SESSION_LEDGER.md` `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:191-205]` (or a NotebookLM-specific ledger).
- Only after (1) 10 manual executions + ledger data AND (2) V-1 Vault completion `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:240]` → enable automation.

**(b) Amend the protocol with a documented exception.**
- Carve out the NotebookLM→local-distiller pipeline as a "supervised automation pilot" exempt from the §10 gate.
- Argument: §10 was written for **AGY frontier-model** usage (expensive weekly pools) `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:16-18, 114-126]`. This pipeline uses a **cheap local Qwen3-1.7B distiller** (not AGY frontier), so the *spirit* of the gate (don't waste expensive frontier tokens on unvalidated automation) may not apply as strictly.
- Requires Kali to formally amend §10 (scope it to AGY-pool automation). Even then, **V-1 remains a hard blocker** `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:240]` — automated credential management for 8 accounts is impossible without it.

### 3.3 Recommendation (for Kali arbitration)

**Recommend OPTION (a) — Honor the gate.** Rationale:

1. **The protocol is explicit and unconditional** `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:298]`. Amending it is Kali's prerogative, but the conservative, sovereignty-preserving default is to honor it. Option (a) costs nothing — manual mode is already prescribed by the unified strategy itself `[UNIFIED:308]`.
2. **V-1 Vault is the actual hard blocker regardless of §10.** The unified strategy lists V-1 as GAP-08 `[UNIFIED:284]` and the SDP protocol makes it a hard prerequisite `[COGNITIVE_SCAFFOLDING_PROTOCOL.md:240]`. Until V-1 exists, 8-account credential automation is impossible *even if §10 were waived*. So honoring §10 adds no deployment delay beyond what V-1 already imposes.
3. **Quality/discipline protection (M11 Soul Integrity, M5 Gnosis Preservation).** The gate exists because unvalidated automation can pollute `soul.yaml` with low-quality L3 principles. 10 manual runs build the quality baseline + tune distiller prompts before any auto-write. NLG-A's feasibility finding addresses *technical* feasibility only — not output quality.
4. **Sovereignty + reliability.** Manual-first protects the canonical soul from automated noise; V-1 is the genuine credential-automation blocker. Honoring the gate is the lowest-risk path that satisfies M23 (no soft-failures / no theater).

**Conditional path to (b) if Kali wants faster automation:** The cleanest amendment is to **scope §10 to AGY-frontier-pool automation** (since this pipeline uses local Qwen3-1.7B, not AGY frontier), carving out NotebookLM→local-distiller as a "supervised pilot." But this still requires V-1 completion before credential automation, and Kali must make the amendment formally. **Researcher's standing recommendation remains (a).**

---

## 4. SUMMARY FOR KALI

| Gap | Researcher Recommendation | Key Evidence |
|-----|--------------------------|--------------|
| **GAP-5** | Adopt **unified 6-notebook mapping (NB-1…NB-6)** as canonical; add supersession banner over R52c + LIVING §1.5; resolve Validation Suite (exclude or fold into NB-1). | R52c is archived/stale `[R52c:1]`; NB-2/NB-3/NB-6 are genuinely new domains reflecting IWAD + heritage + synthesis. |
| **GAP-6** | Corrected mapping: 8 accounts × 10 DR = **80 DR/month**; per-notebook envelope (20,20,20,10,10); monthly cyclic rotation preserves ≤10/account. | Free tier = 10/account `[GAP_AUDIT:36]`; current mapping sums to 130 (broken) `[UNIFIED:71-80]`. |
| **GAP-8** | **Honor the SDP §10 gate (option a)** — deploy fleet in manual mode now, automate only after 10 manual executions + V-1 Vault. V-1 is the real blocker regardless. | SDP §10 `[SDP:298]`, §8 `[SDP:240]`; unified acknowledges manual-mode viability `[UNIFIED:308]`. |

**Deliverable path**: `data/coordination/NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md`

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_notebooklm_gap_c ⬡ 2026-08-20*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: hy3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
