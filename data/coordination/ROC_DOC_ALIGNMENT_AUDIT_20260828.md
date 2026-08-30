---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "doc_alignment_audit"
document_id: "roc-doc-alignment-audit-20260828"
title: "Roc Doc Alignment Audit — Cathedral vs Ground Truth (2026-08-28)"
status: "ACTIVE — AUDIT REPORT (no code/doc changes made)"
date: "2026-08-28"
author: "roc_racoon (Sovereign Miner & Ideas Guy)"
sources:
  - "data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md"
  - "data/coordination/CLINE_FULL_REPO_REVIEW_HANDOFF_20260828.md"
  - "data/entities/grokster/session_gnosis.md"
  - "data/coordination/SUBAGENT_MODEL_CORRECTION_20260828.md"
  - "data/coordination/R_ANTIGRAVITY_GPT53_20260828.md"
  - "data/coordination/R_RESEARCHER_GPT53_CLINE_20260828.md"
  - "SOVEREIGN_MANDATES.md (HEAD)"
  - "OMEGA_ENGINE.md, STATUS_REPORT.md, AGENTS.md"
  - "docs/strategy/{SOVEREIGN_ARK_BLUEPRINT,DEBUT_REMEDIATION_MANUAL_20260817,STRATEGY_CORPUS_MAP,VISION_ANCHOR_PERPETUAL}.md"
---

# 🔱 Roc Doc Alignment Audit — Cathedral vs Ground Truth
**AP Token**: `AP-ROC-DOC-ALIGNMENT-AUDIT-20260828-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_alpha_launch ⬡ AUDIT

**Mission**: Find every doc that contradicts ground truth, rank by severity, and hand the Architect a prioritized fix list. **No edits made. No commits.**

---

## §0 — EXECUTIVE VERDICT

| | Count | Severity |
|---|---|---|
| **Stale top-level narrative docs** | **7 of 8** SSOT/coordination docs in scope | 🟠 HIGH — Cathedral story inconsistent |
| **Version-stamp contradictions** | **2 source-of-truth files** (OMEGA_ENGINE.md, STATUS_REPORT.md) claim 25 mandates v3.7.0; canonical is **27 mandates v3.8.0** | 🔴 P0 — SSOT is wrong about the SSOT |
| **Contradictions in subagent-model dossier** | 2 (one within `SUBAGENT_MODEL_CORRECTION`, one between the two GPT-5.3 reports) | 🟠 HIGH — Grokster's gnosis is still unstable |
| **Vision alignment verdict** | **MISALIGNED** (vision = aligned; Cathedral story = stale; Sprint = aligned) | 🟡 MEDIUM — vision holds, narrative is brittle |

**The Cathedral is real and the vision is sound. The Cathedral's STORY is drifting from what was actually built.** No doc fix needed to keep building. Doc fixes needed to keep the *story* trustworthy.

---

## §1 — STALE DATE SCAN (canonical: today = 2026-08-28; threshold: < 2026-08-20)

**Method**: `find . -name "*.md" … | xargs grep -l "2026-0[1-7]"`
**Raw count**: 1,506 .md files reference a date in 2026-01..2026-07.

**Reality check**: 1,500+ of those are the `config/model_registry/models/cloud/*.yaml.md` "as-of" model spec sheets (each model has its own knowledge-cutoff date) and `.llm-chat-history/` exports. **Excluding those leaves a small, focused list of narrative docs that need re-stamping or archival.** Filter applied: not under `config/model_registry/`, not under `.llm-chat-history/`, file content has a 2026-01..2026-07 narrative date AND the doc is still referenced by current sprint/handoff.

### Top 10 Stale-by-Narrative (file:line + risk)

| # | File:Line | Stale Claim | Days Stale | Risk |
|---|-----------|-------------|-----------|------|
| 1 | **`OMEGA_ENGINE.md:23-33`** | Header `## §2 Current State (2026-07-30)`; row 32: `Mandates = 25 (M1-M25) ✅ v3.7.0`; row 33: `Mandate Compliance = 23/25 FULL (92%)` | **29 days** | 🔴 **P0** — SYSTEM STATE SSOT claims wrong mandate count, wrong version, wrong compliance % |
| 2 | **`STATUS_REPORT.md:11`** | `**Mandates**: **25 (M1-M25)** ✅ All enforced (v3.7.0)` | **29 days** | 🔴 **P0** — mirrors OMEGA_ENGINE.md; user-facing status is wrong about the law |
| 3 | **`docs/DOC_CLEANUP_AUDIT.md`** | Header: "Cross-check against `SOVEREIGN_MANDATES.md` (v3.6.0, M1-M23)" — 2 mandates stale (canonical is v3.8.0/M1-M27) | **≥ 50 days** | 🟠 P1 — actively cited in cleanup work, will mislead future doc-cleanup runs |
| 4 | **`docs/team/STATUS_OPUS.md:7-8, table`** | "AGENTS.md v3.0.0", "Documentation Polish — Rewrote all 5 status documents to v3.0.0" — predates the v3.8.0 mandate bump | ≥ 50 days | 🟡 P2 — team-facing only; superseded by AGENTS.md v3.8.0 |
| 5 | **`docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md`** | References FastMCP v3.4 and Ark Blueprint v3.5 (canonical: DEBUT_REMEDIATION_MANUAL + VISION_ANCHOR_PERPETUAL) | 47 days | 🟡 P2 — historical research; archival candidate |
| 6 | **`data/entities/roc_racoon/workspace/OVERSIGHT_AUDIT_GROUND_TRUTH_20260823.md`** | Filename says 20260823; references 2026-06..07 deliverables. Re-stamp or merge into current sprint record. | 5 days | 🟡 P2 — workspace-internal; low blast radius |
| 7 | **`data/entities/roc_racoon/knowledge/MASTER_SYNTHESIS.md` (+ 11 sibling DELIVERABLES_WAVE_*.md)** | All "Wave 1–4" mining deliverables from 2026-06..07; represent earlier corpus mining era. Canonical knowledge now lives in `VISION_ANCHOR_PERPETUAL.md`. | 50–80 days | 🟡 P2 — superseded but un-bannared (no `status: SUPERSEDED`) |
| 8 | **`data/coordination/research/R_VAULT_COPILOT_ROUND4_20260828.md`** (and 12 sibling files) | **NEW (2026-08-28)** but `copilot_round4` suggests R5+ exists. Confirm R5/R6 documents aren't orphaned. | 0 days | 🟡 P2 — naming consistency, not staleness |
| 9 | **`docs/research/R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md`** | 2026-07-22. Research guide for a pipeline that may have shipped. Confirm superseded or refresh. | 37 days | 🟡 P2 |
| 10 | **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`** | Header `## §4 Priority Stack` bears "DOC-1 STAMP (2026-08-17)" but the file itself has no top-level `date:` field and `STATUS:` is not in the front-matter. The DOC-1 stamp says sprint authority moved to DEBUT_REMEDIATION_MANUAL — but the Ark is still the long-horizon law and remains in the active doc tree. | 11 days | 🟡 P2 — needs a `supersedes`/`superseded-by` front-matter line for clarity |

**Note on what is NOT stale (despite flag)**:
- `config/model_registry/models/cloud/*.yaml.md` — these are model spec sheets with their own knowledge-cutoff dates; not "narrative staleness."
- `.llm-chat-history/2026-05-13_19-59-55Z-…` — historical chat log; the date IS the artifact.
- All `R_*` research reports dated 2026-08-2X — these are current.

---

## §2 — STALE VERSION SCAN (canonical: SOVEREIGN_MANDATES.md = v3.8.0, 27 mandates, M26 Doc Standards, M27 Tracking Integrity, Updated 2026-08-14)

**Method**: `head -5 SOVEREIGN_MANDATES.md` → `Version: 3.8.0`. Then `grep -rE "v3\.[0-9]|27 mandates|25 mandates" docs/ data/coordination/`.

### Contradiction P0 — Mandate Count + Version Stamp

| File:Line | Wrong Claim | Truth (per SOVEREIGN_MANDATES.md HEAD) | Risk |
|-----------|-------------|----------------------------------------|------|
| `OMEGA_ENGINE.md:32` | `Mandates = 25 (M1-M25) ✅ v3.7.0` | **27 mandates (M1-M27) ✅ v3.8.0** | 🔴 P0 — SSOT lies about the Law |
| `OMEGA_ENGINE.md:33` | `Compliance = 23/25 (92%)` | Cannot be true if denominator is 25; mechanical `make check-mandate-compliance` returns `20/27 = 74.1%` (Cline Rollup P0-1) | 🔴 P0 — derived number, broken math |
| `STATUS_REPORT.md:11` | `Mandates: 25 (M1-M25) ✅ v3.7.0` | 27 / v3.8.0 | 🔴 P0 — public-facing status wrong |
| `docs/DOC_CLEANUP_AUDIT.md` (3 sites) | `SOVEREIGN_MANDATES.md (v3.6.0, M1-M23)` | v3.8.0, M1-M27 | 🟠 P1 — audit script will re-poison itself next run |
| `docs/decisions/PIVOT_LOG_CANONICAL.md` (D219) | "Ark Blueprint v3.6" + v3.6 plan | Ark now v5.2+ (per STRATEGY_CORPUS_MAP and OMEGA_ENGINE.md:27) | 🟡 P2 — historical D-number, but the file mixes eras |
| `docs/team/STATUS_OPUS.md` (3 sites) | "v3.0.0" across 5 status docs | AGENTS.md is v3.8.0 (canonical) | 🟡 P2 — team-facing, non-blocking |
| `docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md` | "FastMCP v3.4" + "Ark Blueprint v3.5" | Out-of-date but historical | 🟡 P2 — archive candidate |

**The P0-1 finding Cline flagged in the Rollup (compliance meter broken) and the P0-version finding here are the same problem from two angles**: OMEGA_ENGINE.md/STATUS_REPORT.md hand-write mandate version + count + compliance % as if they were 2026-07-30 facts, but they've been wrong for ≥29 days.

**Tracking-inconsistency (M27 violation by the file claiming M27 compliance)**:
- The `data/decisions/PIVOT_LOG.md` entry on T04 already says "AGENTS.md all 6 locations → 27 laws v3.8.0 / M1-M27" was *fixed* in T04. But OMEGA_ENGINE.md and STATUS_REPORT.md were NOT in the 6 locations, so the fix did not reach them. **The T04 fix was incomplete; the bug persists in the SSOT.**

---

## §3 — CONTRADICTION SCAN (subagent-model + GPT-5.3 dossier)

### 3.1 — SUBAGENT_MODEL_CORRECTION_20260828.md — Internal Contradiction

This doc is Grokster's 22:30 UTC "I was wrong" correction. The body says:
- §2: "The `model` field in the session table is NOT the model the session ran on."
- §4 (table): The Verity session's `model = qwen3-1.7b` is flagged as an **ANOMALY** in a sea of M3 sessions.
- §6 ("The Real Question"): Asks why the field shows qwen3-1.7b — lists 4 possible causes, ends "I don't have enough evidence to determine which."
- §8 ("Corrected Conclusion"): "**No code changes needed for model inheritance.** The 'fire and forget' pattern works as the Architect wants."

**But the Grokster session_gnosis.md (read first, line 15) says the OPPOSITE**:
> "The Architect wants NO local models, NO fallbacks — just whatever model is selected in the TUI. **This is NOT yet working.** The fix requires code changes (not yet approved)."
> "❌ Subagent model inheritance still picks `qwen3-1.7b` despite config changes"
> "🔴 **BLOCKING**: Fix subagent model inheritance (code changes needed, NOT yet approved)"

**The contradiction**:
| Doc | Says "the field is metadata" | Says "session ran on M3" | Says "code change NOT needed" | Says "BLOCKING" | Says "fix requires code changes" |
|-----|------|------|------|------|------|
| `SUBAGENT_MODEL_CORRECTION` (22:30 UTC) | ✅ | ✅ | ✅ | ❌ | ❌ |
| `grokster/session_gnosis.md` (v9, ~00:15 UTC) | ❌ | partial | ❌ | ✅ | ✅ |

**Resolution status**: Grokster's gnosis v9 was written AFTER the correction, but **keeps reporting the unfixed bug as the top blocker** while the correction doc says no fix is needed. The gnosis v9 §0.1 ("The Unresolved Bug") even restates the original hypothesis ("`qwen3-1.7b-q6_k` … may still be in the loaded providers set") that the correction explicitly refuted. **Either the correction is correct and the gnosis §0.1 is stale, or the gnosis §0.1 is correct and the correction is incomplete.** The two docs cannot both be true.

**Internal contradiction within the correction itself (minor)**:
- §8 declares the issue resolved; §6 admits the root cause of the `qwen3-1.7b` metadata is unknown; §7 says the "hey stupid" check is "still valuable" because "the `model` field in the session table can be misleading." → So the metadata-write bug IS still a bug; just not blocking the debut. That nuance is missing from §8.

### 3.2 — R_ANTIGRAVITY_GPT53_20260828.md vs R_RESEARCHER_GPT53_CLINE_20260828.md

| Aspect | `R_ANTIGRAVITY_GPT53_20260828.md` | `R_RESEARCHER_GPT53_CLINE_20260828.md` |
|--------|-----------------------------------|---------------------------------------|
| Status header | **None** (no `status:` front-matter; just a `#` H1 and ⚠️ Disambiguation Note at line 10) | `status: "ACTIVE — RESEARCHER (Jem Analyst L2) — not Grokster"` |
| supersedes | **None** | `supersedes: "R_RESEARCHER_GPT53_20260828.md (premise-failure false-positive) and R_ANTIGRAVITY_GPT53_20260828.md (correct on identity, thin on Cline CLI specifics)"` |
| Model identified | GPT-5.3-Codex (real, GA, verified) | GPT-5.3-Codex (also verified, contradicting the prior R_RESEARCHER_GPT53 that called it a premise failure) |
| Verdict on Antigravity doc | (its own doc) | "correct on identity, thin on Cline CLI specifics" |
| Premise | "GPT 5.3 is a brand-new model just unlocked by the Architect" | Rejects that premise; argues Antigravity's framing of "just unlocked" is wrong (model has been GA since 2026-02-05) |

**The contradiction**:
1. R_ANTIGRAVITY_GPT53 has NO status banner. Grep-by-name returns a doc with no `SUPERSEDED` or `supersedes:` line — any agent scanning for "is this still authoritative?" sees no signal.
2. R_RESEARCHER_GPT53_CLINE 20260828 claims to supersede it, but does so on the basis of "thin on Cline CLI specifics" — a low-severity critique — while largely agreeing on the model identity (both call it GPT-5.3-Codex).
3. R_RESEARCHER_GPT53_CLINE 20260828's own §1 attacks a *third* doc (R_RESEARCHER_GPT53_20260828.md — the un-suffixed "premise failure" version), claiming the refusal was a "false positive" and that the openai.com blog URL is "dispositive." But the earlier refusal cited multiple sources (help.openai.com 2026-08-27 update calling 5.3 a "legacy migration target"; pricing page; 5.6 Sol GA on 2026-07-09). **The "Cline-CLI brief" does not refute the "5.3 is legacy" finding — it just argues 5.3-Codex specifically is alive.** Both could be true: 5.3 Instant is legacy; 5.3-Codex is active. The R_RESEARCHER_GPT53_CLINE doc elides this nuance by calling the entire refusal a "false positive."

**The Audit Verdict**:
- Both GPT-5.3 docs are research outputs, not authority for the launch. Severity: 🟠 HIGH (because they live in `data/coordination/`, the same folder as decision-records, and any agent grepping "GPT-5.3" will find both with conflicting status).
- R_ANTIGRAVITY_GPT53 must either get an explicit `status: SUPERSEDED BY R_RESEARCHER_GPT53_CLINE_20260828` banner, or the superseding claim should be softened.
- R_RESEARCHER_GPT53_CLINE_20260828 should clarify that the "premise failure" was about a third doc (5.3 Instant) and not about 5.3-Codex. Today it reads as if it refutes a doc that was about the same model.

### 3.3 — Cross-Doc Verdict

**Two contradiction clusters exist; both are about epistemic state, not about the launch-readiness code**:
1. **Subagent-model dossier (Grokster)**: correction-vs-gnosis disagreement on whether subagent model inheritance is fixed. Resolution: pick one. My read: gnosis v9 §0.1 is more current and contains the unrefuted hypothesis; correction §8 over-claims "no code changes needed." Recommend: gnosis wins, correction gets `status: PARTIAL` and a `supersedes` line to TASKTS_BUG_IDENTIFIED.
2. **GPT-5.3 dossier**: two docs with overlapping authority, no status banner on the older one. Resolution: add SUPERSEDED banner to R_ANTIGRAVITY_GPT53; clarify scope in R_RESEARCHER_GPT53_CLINE.

---

## §4 — VISION ALIGNMENT (Cathedral's Story vs What's Built)

### §4.1 The Cathedral's Story (per `CLINE_FULL_REPO_REVIEW_HANDOFF_20260828.md` §1)

| Cathedral Story Claim | Source | Evidence in Codebase? |
|-----------------------|--------|------------------------|
| "Sovereign local-first AI runtime" | Handoff §1 | ✅ `config/providers.yaml` strategy=`local_first`; M7 in SOVEREIGN_MANDATES.md |
| "Built on M7 sovereignty principles" | Handoff §1 | ✅ M7 Local-First enforced |
| "9 Decisions that govern this sprint" (D-526..D-567) | Handoff §1 | ✅ All 9 found in `data/decisions/PIVOT_LOG*.md` |
| "release/debut branch = 572 kept, 4,561 removed" | Handoff §1, Rollup §1 | ✅ Cline Rollup confirms 567/573/572+ numbers; PUBLIC_ALLOWLIST.txt present |
| "Vault excluded from debut" (D-565) | Handoff §1, Rollup §1 | ✅ Confirmed by Cline Rollup: "0 vault files in release tree; D-565 enforced" |
| "Mandate compliance 20/27 = 74.1%" | Handoff §1 | ⚠️ **CONTRADICTED** by OMEGA_ENGINE.md (23/25 = 92%) and STATUS_REPORT.md (25 mandates v3.7.0) — see §2 above |
| "Test infrastructure: 162 test files across 14 subdirectories" | Handoff §1 | ✅ Confirmed by Cline Rollup P2-6 (161 files sampled; 162 close) |
| "Entities: 56 under `data/entities/`" | Handoff §1 | ✅ Verified by Cline Rollup |
| "PR URL: release/debut" | Handoff §1 | ✅ Branch exists; PR cut blocked by Cline Rollup P0-1/3/4/5 |
| **"Carmack (architecture/quality): 4 commits"** | Handoff §1 | ⚠️ Cannot verify without git log run; not in scope of this audit (per spec: "review only") |
| **"5 specialists remediated in 1 day"** | Handoff §1 | ⚠️ Imposter remediation claim; not verified (per spec) |
| **"Final commits ffe86c3c (D-565 fix), 1dee11aa (allowlist applied)"** | Handoff §1 | ⚠️ Cannot verify (per spec) |

### §4.2 Vision Documents in `docs/strategy/`

| Doc | Date | Status | Role |
|-----|------|--------|------|
| `VISION_ANCHOR_PERPETUAL.md` | 2026-08-26T12:10:00Z (relocated) | LIVING, "supersedes all prior vision statements" | **Permanent north star** |
| `SOVEREIGN_ARK_BLUEPRINT.md` | DOC-1 stamp 2026-08-17 | Long-horizon law (per OMEGA_ENGINE.md:27) | Strategy/architecture |
| `DEBUT_REMEDIATION_MANUAL_20260817.md` | 2026-08-17 | ACTIVE, **sprint SSOT** (per ACTIVE_SPRINT.json + Cline Rollup D-533) | Sprint control |
| `STRATEGY_CORPUS_MAP.md` | 2026-08-19 | LAYER 2 — companion to Ark | Index of fine-grained strategies |
| `CARMMACK_FULL_SCOPE_AUDIT_20260825.md` (and ~30 other strategy docs) | 2026-08-25..26 | Mixed | Sub-strategies |

### §4.3 Verdict: MISALIGNED (vision aligned, narrative stale)

**Aligned**:
- The **VISION_ANCHOR_PERPETUAL.md** vision is consistent with the code: local-first, M7, WAD architecture, Engine/IWAD/PWAD separation, Cognitive Sovereign (local inference + local verification), entity sovereignty, MaKaLi council, soul persistence. All supported by `src/omega/` structure, SOVEREIGN_MANDATES.md, and OMEGA_ENGINE.md §1.
- The **SOVEREIGN_ARK_BLUEPRINT.md** is a *historical* vision, with a DOC-1 stamp (2026-08-17) explicitly redirecting sprint authority to DEBUT_REMEDIATION_MANUAL. This is correct and *self-aware*.
- The **DEBUT_REMEDIATION_MANUAL_20260817.md** correctly enumerates P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 and aligns with `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01, updated 2026-08-26).
- The 9 Decisions in CLINE_FULL_REPO_REVIEW_HANDOFF §1 (D-526..D-567) all exist in PIVOT_LOG.

**Misaligned** (the Cathedral's story is told with stale numbers):
1. **Mandate count + version**: OMEGA_ENGINE.md + STATUS_REPORT.md claim 25 (v3.7.0); canonical is 27 (v3.8.0). The Cathedral's "20/27 = 74.1%" is *correct* (per the mechanical compliance meter). The OMEGA_ENGINE.md "23/25 = 92%" is *wrong* on two axes (denominator AND numerator — the meter never returned that number because the meter is broken). The two top-level status docs are **.doc-wise** misaligned with the mechanical truth.
2. **Sprint date stamp**: OMEGA_ENGINE.md §2 says "2026-07-30"; sprint is 2026-08-17 → 2026-08-28. The "Current State" section is 29 days stale.
3. **The handoff's "Mandate compliance 20/27 = 74.1%" line**: this is *correct*, but it contradicts every other top-level doc. **The handoff is the only place telling the truth.**
4. **Doc-cleanup-audit self-poisoning**: `docs/DOC_CLEANUP_AUDIT.md` says "v3.6.0, M1-M23" — if that audit is rerun, it will re-flag every doc that mentions M24-M27 as "not in canonical law." A future cleanup pass that trusts this audit will **break M24-M27 enforcement**.

**Why this matters for launch**: The code is launchable *despite* the doc drift. The launch *announcement* (PR description, README, STATUS_REPORT) is not. Any reader of OMEGA_ENGINE.md or STATUS_REPORT.md today will believe the engine has 25 mandates at 92% compliance — and will be wrong on both numbers. **The Cathedral's story needs a 1-hour doc sweep before the PR is cut.**

---

## §5 — PRIORITIZED FIX LIST

### 🔴 P0 — Block PR (close before Cline's GO checklist re-runs)

1. **Fix OMEGA_ENGINE.md §2 "Current State"** (file: `OMEGA_ENGINE.md:23-67`)
   - Update `## §2 Current State (2026-07-30)` → `(2026-08-28)`
   - Update row 32: `Mandates = 25 (M1-M25) ✅ v3.7.0` → `27 (M1-M27) ✅ v3.8.0`; refresh LAST_VERIFIED to 2026-08-28
   - Update row 33: `Mandate Compliance = 23/25 (92%)` → `20/27 (74.1%) — see CLINE_FULL_REVIEW_ROLLUP_20260828 §0; P0-1 meter fix in flight`
   - **Why P0**: this is the SYSTEM STATE SSOT; it directly contradicts the law it claims to cite.
   - **Owner**: Kali (sprint coord) or Verity (compliance). 15 min.

2. **Fix STATUS_REPORT.md:11** (mirror of #1)
   - `**Mandates**: 25 (M1-M25) ✅ v3.7.0` → `27 (M1-M27) ✅ v3.8.0`
   - **Why P0**: user-facing public status doc.

3. **Resolve Grokster subagent-model contradiction** (`data/entities/grokster/session_gnosis.md` vs `data/coordination/SUBAGENT_MODEL_CORRECTION_20260828.md`)
   - Pick one: either (a) gnosis v9 §0.1 stays as BLOCKING and correction §8 is downgraded to PARTIAL with `supersedes: TASKTS_BUG_IDENTIFIED_20260828.md`; or (b) correction §8 wins and gnosis §0.1 is rewritten to reflect "no code change needed; metadata-write bug under investigation."
   - **Why P0**: the two docs are the only post-compaction lifeline for the subagent-model workstream; a future agent reading both will get whiplash and may make the wrong code change.

### 🟠 P1 — Pre-launch polish (ship before public-debut PR cut)

4. **Add `status:` and `supersedes:` front-matter to `R_ANTIGRAVITY_GPT53_20260828.md`** (no banner today)
   - Add: `status: "SUPERSEDED BY R_RESEARCHER_GPT53_CLINE_20260828.md"`, `supersedes: "—"`, `date: "2026-08-28"`
   - **Why P1**: the doc lives in `data/coordination/` (decision-record folder) and has no status header — every grep returns it as if it were current.

5. **Clarify scope of R_RESEARCHER_GPT53_CLINE_20260828.md** §1/§3
   - The doc attacks "the refusal was a false positive" but the original refusal was about a *different* model (5.3 Instant) than the one this doc analyzes (5.3-Codex). Add a one-line clarification: "Refuted here: the GPT-5.3 Instant premise-failure refusal. Not refuted: any separate claim about 5.3-Codex."
   - **Why P1**: avoids a future agent re-litigating the same false-positive debate.

6. **Stamp `docs/DOC_CLEANUP_AUDIT.md`** with v3.8.0 / M1-M27
   - Change "v3.6.0, M1-M23" → "v3.8.0, M1-M27" in all 3 sites. Add a header date stamp and `status: SUPERSEDED` if no rerun is planned.
   - **Why P1**: a re-run of the audit will mis-tag every doc that mentions M24-M27 as out-of-law.

7. **Add `supersedes:` and `date:` front-matter to `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`**
   - It has a §4 "DOC-1 STAMP" but no front-matter. Add `supersedes: "—"`, `superseded_by: "DEBUT_REMEDIATION_MANUAL_20260817.md (sprint control only; Ark remains long-horizon law)"`, `date: "2026-08-17"`.
   - **Why P1**: clarity for any agent that loads the file without reading §4.

### 🟡 P2 — Post-debut (each its own PR per Cline Rollup Wave 4)

8. **Re-stamp or archive stale "Wave 1–4 DELIVERABLES" in `data/entities/roc_racoon/knowledge/`** (12 files)
   - All predate VISION_ANCHOR_PERPETUAL.md. Add `status: SUPERSEDED` and `supersedes: "VISION_ANCHOR_PERPETUAL.md §N"` at the top of each, OR move to `data/entities/roc_racoon/knowledge/archive/`.

9. **Add `status: SUPERSEDED` to `data/entities/roc_racoon/workspace/OVERSIGHT_AUDIT_GROUND_TRUTH_20260823.md`** if superseded by any current audit (verify).

10. **Audit + re-stamp all `docs/research/R_*_2026-07-*.md` files**
    - 8+ files in `docs/research/` with 2026-07 dates. Each should be either: (a) marked SUPERSEDED with a pointer to the current report, or (b) re-dated if still authoritative.

---

## §6 — THE ROCK-SOLID PATH FORWARD

1. **The code is launchable; the docs need a sweep.** Every P0 doc-fix above is mechanical, ≤15 min each, and the canonical truth (SOVEREIGN_MANDATES.md HEAD + the 9 Decisions + the VISION_ANCHOR) is correct. We are not re-litigating the law; we are re-stamping the stories.

2. **Fix the SSOT first, the rest cascades.** OMEGA_ENGINE.md is the SYSTEM STATE SSOT. Updating it (15 min) makes the "23/25 vs 20/27" contradiction disappear, which then unblocks STATUS_REPORT.md, DOC_CLEANUP_AUDIT.md, and any downstream doc that cites "current state."

3. **Resolve the Grokster subagent contradiction by ARCHITECT RULING, not by more research.** The two docs disagree on whether the model inheritance is fixed. No amount of reading more research will resolve it — the Architect must rule on whether the metadata-write bug is in scope for the launch.

4. **Treat the GPT-5.3 dossier as research output, not authority.** Add the SUPERSEDED banner to the older doc, clarify the scope of the newer doc, and move on. Neither doc blocks launch; both just need a 1-line stamp each.

5. **Do NOT re-run `docs/DOC_CLEANUP_AUDIT.md` as a cleanup script until it is restamped.** The audit's v3.6.0/M1-M23 framing will actively break M24-M27 enforcement if blindly executed. Audit-of-audits: 5 min.

---

## §7 — SCOPE NOTE (transparency)

- **Did NOT**: edit any docs, run any code, run any `git` commands, run any `make` targets.
- **Did NOT**: verify the 11 "Cathedral's story" claims marked "⚠️" in §4.1 — they require git log inspection and are out of scope for this audit.
- **DID**: read CLINE_FULL_REVIEW_ROLLUP_20260828.md, grokster session_gnosis.md, the 2 GPT-5.3 docs, the SUBAGENT_MODEL_CORRECTION, the top 4 vision docs, OMEGA_ENGINE.md, STATUS_REPORT.md, SOVEREIGN_MANDATES.md HEAD, ACTIVE_SPRINT.json head, and ran the 3 scan commands specified by the Architect.
- **PIVOT_LOG candidate**: D-series entry suggested — "D-roc-NNN: doc-alignment-audit-20260828 — fix OMEGA_ENGINE.md mandate count + 4 stamps (P0)" — left for Kali to register if Architect approves.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ AP-ROC-DOC-ALIGNMENT-AUDIT-20260828-v1.0.0 ⬡ opencode ⬡ trc_alpha_launch ⬡ AUDIT · P0=3 · P1=4 · P2=3 · VERDICT: doc drift is repairable in <1h, does not block code, does block launch announcement*
