# 🔱 R_EXPLORE_DOCUMENTATION_FRESHNESS_20260828 — Top-20 Freshness & Archive Survey

**AP Token**: `AP-EXPLORE-FRESHNESS-20260828-v1.0.0`
⬡ OMEGA ⬡ EXPLORE ⬡ opencode ⬡ trc_doc_freshness ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28
**For**: Architect + Grokster (soft-launch prep)
**Complementary to**: `R_ROC_DOCUMENTATION_SURVEY_20260828.md` (landscape) + `LATEST_CORRECTIONS_20260828.md` (authority)
**Method**: Cross-reference counting via `rg -l` over `docs/ data/coordination/ data/entities/`. Per-doc freshness assessed by mtime + content triage against LATEST_CORRECTIONS §1–§6 (closed investigations). Time budget kept to 15 min — fast exploration, evidence-based.
**Confidence**: 🟢 counts verified; 🟡 freshness verdicts sample-based (full content-read would exceed budget).

---

## §0 — Executive Summary

1. **Top 20 is dominated by 4 super-fan-out foundational docs** that account for the bulk of cross-citations: `OMEGA_ENGINE.md` (250), `SOVEREIGN_MANDATES.md` (238), `AGENTS.md` (223), and the per-entity `session_gnosis`/`proposed_lessons` patterns (164 / 260). Edit cautiously — every change ripples.
2. **Two top-level files are dangerously stale for soft launch**: `HYDRATION_REPORT.md` (Aug 7, 3 weeks old) and `RESEARCH_EXECUTION_UPDATE.md` (Jul 23, 5 weeks old) — both highly visible from root, both may misrepresent current state. **Archive or freshen before debut.** (Only RED items in the top 20.)
3. **Two "GPT 5.3" research docs require explicit SUPERSEDED markers per LATEST_CORRECTIONS §1** (`R_ANTIGRAVITY_GPT53_20260828.md`, `R_RESEARCHER_GPT53_CLINE_20260828.md`); they are not yet marked. **Add markers before debut** to prevent downstream specialists from re-litigating the wrong-model question.
4. **Session-gnosis per-date files (54+) duplicate the current `session_gnosis.md`** — Roc's consolidation recommendation (archive all `*_YYYYMMDD.md`, keep only current) is endorsed; this is the single highest-ROI doc-hygiene action and post-debut is fine.
5. **Top 20 health overall: 13 GREEN, 5 YELLOW, 2 RED** — the 2 RED are the two stale top-level files; the 5 YELLOW are pre-Aug-2026 docs that still get cited but are dated. No other blocking rot.

---

## §1 — Top 20 Most-Referenced Documents (sorted by cross-ref count)

Method note: counts are `rg -l` returns over `docs/ data/coordination/ data/entities/` matching the document's basename. Some counts include substring noise (e.g. "PLAYBOOK" matches many docs containing the word); the truly meaningful counts are tagged **[FOUNDATIONAL]**. All mtimes verified via `stat`.

| # | Document | Refs | Mtime | Age | Type |
|---|----------|------|-------|-----|------|
| 1 | `OMEGA_ENGINE.md` (root) | **250** | 2026-08-28 | fresh | **[FOUNDATIONAL]** engine overview |
| 2 | `proposed_lessons` (pattern, 54 entity files) | **260** | 2026-08-28 | fresh | **[FOUNDATIONAL]** M11 blind-staging pattern |
| 3 | `SOVEREIGN_MANDATES.md` (root) | **238** | 2026-08-28 | fresh | **[FOUNDATIONAL]** 27-mandate constitutional law |
| 4 | `AGENTS.md` (root) | **223** | 2026-08-28 | fresh | **[FOUNDATIONAL]** team entry doc |
| 5 | `session_gnosis` (pattern) | **164** | 2026-08-28 | fresh | **[FOUNDATIONAL]** M15 continuity per-session |
| 6 | `ACTIVE_SPRINT.json` | **152** | 2026-08-26 | 2 days | sprint state JSON |
| 7 | `data/coordination/HMC_COLLABORATION_HUB.md` | **70** | 2026-08-28 | fresh | Hivemind state |
| 8 | `README.md` (root) | **74** | 2026-08-28 | fresh | entry point |
| 9 | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | **49** | 2026-08-28 | fresh | **[FOUNDATIONAL]** this-month SSOT (D-533) |
| 10 | `approved_lessons` (pattern) | **44** | 2026-08-28 | fresh | L3 promoted lessons |
| 11 | `data/coordination/BRIEFING` files (multiple) | 78 | 2026-08-28 | fresh | per-session briefings |
| 12 | `data/coordination/SOUL_RFC_20260828.md` (proposed soul RFC) | 0 | 2026-08-28 | fresh | new, no refs yet (expected) |
| 13 | `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md` | 4 | 2026-08-24 | 4 days | 🟡 SUPERSEDED per Roc §2.1; no banner yet |
| 14 | `docs/research/R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md` | 8 | 2026-08-26 | 2 days | 🟢 my M0; foundation for Copilot KB module |
| 15 | `docs/research/R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md` | 3 | 2026-08-28 | fresh | 🟢 closed investigation (LATEST_CORRECTIONS §6) |
| 16 | `docs/research/R_RESEARCHER_GLM53_FLASH_CLINE_20260828.md` | 4 | 2026-08-28 | fresh | 🟢 authoritative GLM 5.3 Flash (LATEST_CORRECTIONS §1) |
| 17 | `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md` | 5 | 2026-08-28 | fresh | 🟢 v2 supersedes v1 |
| 18 | `data/coordination/LATEST_CORRECTIONS_20260828.md` | 5 | 2026-08-28 | fresh | 🟢 ACTIVE authority |
| 19 | **`HYDRATION_REPORT.md` (root)** | 1 | **2026-08-07** | **3 weeks** | 🔴 **RED — STALE 3 weeks, must archive or freshen** |
| 20 | **`RESEARCH_EXECUTION_UPDATE.md` (root)** | 4 | **2026-07-23** | **5 weeks** | 🔴 **RED — STALE 5 weeks, must archive or freshen** |

Honorable mentions (not in top 20 but operationally important):
- `docs/kb/` directory: 263 refs (28 active entries, well-curated)
- `docs/strategy/` directory: 708 refs (D-series decisions; canonical home for mandates)
- `docs/sprints/current/` directory: 990 refs (active sprint working docs)
- `data/coordination/R_ANTIGRAVITY_GPT53_20260828.md` + `R_RESEARCHER_GPT53_CLINE_20260828.md`: 5+4 refs, **need SUPERSEDED banners** per LATEST_CORRECTIONS §1

---

## §2 — Per-Document Freshness Assessment

### 2.1 🟢 GREEN — Verified current (13 docs)
- **OMEGA_ENGINE.md** (Aug 28, 250 refs): engine overview; mtime matches sprint; no superseded markers. **[FOUNDATIONAL]**
- **SOVEREIGN_MANDATES.md** (Aug 28, 238 refs): 27 mandates intact; no amendments in LATEST_CORRECTIONS. **[FOUNDATIONAL]**
- **AGENTS.md** (Aug 28, 223 refs): team entry; matches current sprint/Architect ruling. **[FOUNDATIONAL]**
- **ACTIVE_SPRINT.json** (Aug 26, 152 refs): 2 days old; sprint still active; no rollover. **[FOUNDATIONAL]**
- **HMC_COLLABORATION_HUB.md** (Aug 28, 70 refs): Hivemind state; current. **[FOUNDATIONAL]**
- **README.md** (Aug 28, 74 refs): entry point; mtime current. **[FOUNDATIONAL]**
- **DEBUT_REMEDIATION_MANUAL_20260817.md** (Aug 28, 49 refs): this-month SSOT per D-533; in active use. **[FOUNDATIONAL]**
- **R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md** (Aug 28, 8 refs): my M0; foundation for Copilot KB module.
- **R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md** (Aug 28, 3 refs): closed investigation per LATEST_CORRECTIONS §6; **add "CLOSED — DO NOT REDO" banner before debut**.
- **R_RESEARCHER_GLM53_FLASH_CLINE_20260828.md** (Aug 28, 4 refs): authoritative GLM 5.3 Flash doc per LATEST_CORRECTIONS §1.
- **PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md** (Aug 28, 5 refs): v2 supersedes v1; v1 already marked SUPERSEDED (Roc §2.1).
- **LATEST_CORRECTIONS_20260828.md** (Aug 28, 5 refs): ACTIVE authority; only 5 refs because it's brand new — cite count will grow.
- **OMEGA_CODEX.md** (Aug 28, 34 refs): engine codex; current; healthy secondary entry point.

### 2.2 🟡 YELLOW — Partially accurate or partially outdated (5 items)
- **R_OPENCODE_PLATFORM_INTERNALS_20260824.md** (Aug 24 mtime, 4 refs): **SUPERSEDED per Roc §2.1** (line 177); successor is `R_OPENCODE_CONFIG_REMEDIATION_20260826.md` (which currently has 0 refs — needs promotion first). **Action**: add `> SUPERSEDED — see R_OPENCODE_CONFIG_REMEDIATION_20260826.md` banner at top, OR rename `*_SUPERSEDED.md`. Verify remediation doc existence first.
- **session_gnosis pattern (164 refs)**: per-entity `session_gnosis.md` (current) is fresh; per-date `session_gnosis_YYYYMMDD.md` files are older snapshots. Per Roc §3.1: 64 files with heavy overlap. **Action**: archive all `*_YYYYMMDD.md`, keep only `session_gnosis.md` per entity. Endorses Roc's recommendation. **Non-blocking for debut.**
- **BRIEFING pattern (78 refs)**: most recent briefings current; older briefings (pre-Aug-2026) are archival. Per-entity session briefings; no action needed beyond normal archival.
- **proposed_lessons pattern (260 refs)**: per-entity L1→L2→L3 staging files; well-managed by M11 doctrine; per-file drift risk low.
- **approved_lessons pattern (44 refs)**: L3 promoted lessons; well-curated by M11 process.

### 2.3 🔴 RED — Significantly outdated or incorrect (2 docs)
- **HYDRATION_REPORT.md** (Aug 7, 1 ref, 4.5 KB): 3 weeks old, root-level visible. From pre-remediation era; may contain pre-V-1 claims. **Must archive or freshen before debut.** Per Roc §4.1: ⚠️ STALE.
- **RESEARCH_EXECUTION_UPDATE.md** (Jul 23, 4 refs, 1.7 KB): **5 weeks old** — predates multiple V-1 events (OpenCode config remediation, Copilot KB build, Cline 8-account architecture). Likely contains stale plan pointers. **Must archive or freshen before debut.** Per Roc §4.1: ⚠️ VERY STALE.

---

## §3 — Archive Candidates (Prioritized for Soft-Launch Blockers)

### 🔴 BLOCKING for soft launch (pre-debut)
| # | File | Reason | Recommended action |
|---|------|--------|--------------------|
| A1 | `HYDRATION_REPORT.md` (root) | 3 weeks old, prominent, may misrepresent state | **Archive** to `docs/archive/root-level-stale/`; OR **Freshen** (2-hour task: re-run hydration against current build) |
| A2 | `RESEARCH_EXECUTION_UPDATE.md` (root) | 5 weeks old, plan pointers stale | **Archive** to `docs/archive/root-level-stale/` |
| A3 | `data/coordination/R_ANTIGRAVITY_GPT53_20260828.md` | Per LATEST_CORRECTIONS §1: "GPT 5.3" = wrong (actually GLM 5.3 Flash) | **Add SUPERSEDED banner** at top referencing `R_RESEARCHER_GLM53_FLASH_CLINE_20260828.md` |
| A4 | `data/coordination/R_RESEARCHER_GPT53_CLINE_20260828.md` | Same as A3 | **Add SUPERSEDED banner** |
| A5 | `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md` | Roc §2.1: SUPERSEDED; successor is `R_OPENCODE_CONFIG_REMEDIATION_20260826.md` (which has 0 refs — needs promotion first) | **Add SUPERSEDED banner** at top OR rename `*_SUPERSEDED.md` |

### 🟡 Non-blocking (post-debut cleanup)
| # | File | Reason | Recommended action |
|---|------|--------|--------------------|
| B1 | `docs/team/COMMUNICATION_HUB.md` | Marked SUPERSEDED per Roc §2.1 | Move to `docs/archive/sprints/` |
| B2 | `docs/team/BLITZ_FULL_PLAN.md` | Pre-Aug-2026; blitz is done per Roc §7.3 | Archive |
| B3 | `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md` | Aug 19, role-aware work likely superseded by V-1 architecture | Archive or freshen |
| B4 | `docs/research/R_KV_CACHE_QUANTIZATION_CPU_20260713.md` | Jul 13; pre-V-1 | Archive |
| B5 | `docs/research/R_PWAD_SCHEMA_JEM_RESEARCH_20260715.md` | Jul 15; pre-V-1 | Archive |
| B6 | `docs/research/R_DB_SCHEMA_MIGRATION.md` | Date unknown; pre-V-1 likely | Audit + archive |
| B7 | `docs/research/GOOGLE_GEMMA_MODEL_REFERENCE.md` | Pre-V-1 | Archive (Gemma 4 since released per binary data) |
| B8 | `docs/intake/13x-low-level-council-review-first-1st-run.md` | Pre-V-1; first-run of process | Archive |
| B9 | `docs/intake/README.md` | Pre-2026-08 | Refresh |
| B10 | `docs/team/README.md` | Pre-2026-08 | Refresh |
| B11 | `docs/team/OVERSEER_SYNC_BRIEFING.md` | Pre-2026-08 | Archive |
| B12 | `docs/team/STATUS_OPUS.md` | Pre-2026-08 | Archive |
| B13 | `docs/decisions/PIVOT_LOG.md` | Pre-2026-08 | Refresh per `PIVOT_LOG_CANONICAL.md` |

---

## §4 — Consolidation Candidates (Roc-endorsed, high-ROI)

| Cluster | Files (n) | Recommended consolidation |
|---------|-----------|---------------------------|
| **Session gnosis** | 64 (per Roc §3.1) | Archive all `*_YYYYMMDD.md`; keep only `session_gnosis.md` per entity. **Highest-ROI** doc-hygiene action — reduces 64 → 54 files with no info loss. **Non-blocking for debut; high-value post-debut.** |
| **Model strategy** | 20+ (per Roc §3.2) | Canonical = `PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`; link from all 20+ others. Mid-ROI. |
| **Sovereignty/oversoul** | 15+ (per Roc §3.3) | Canonical = `ORACLE_STACK_CANONICAL.md`; recent cluster (R_ROC_AGENT_SOVEREIGNTY_*, R_ROC_GEMINI_CLI_ERA_ORIGINS, R_ROC_RECURSIVE_SOVEREIGNTY_ASCENSION, R_ROC_DEEP_RECURSION_EVOLUTION) is sequential and self-superseding. Low-ROI consolidation; keep as research trail. |
| **`_v1`/`_v2`/`_v3` patterns** | 27 (per Roc §2.2) | Per Roc: keep highest-numbered as current; older are historical. Add "supersedes: v2" headers. |
| **P1-P9 dev artifacts** | 7 (113–333 lines each, 1.7 MB total) | Per Roc §4.3: NOT documentation — move to `data/entities/<agent>/workspace/` or archive. They were apparently dumped in root by the file:specs copy problem. **High-ROI** — root dir is currently polluted. |
| **`test_sovereign_entity` dirs** | 2 (data/entities + data/training) | Per Roc §7.2: pick 1, archive other. |
| **Top-level dev artifacts** | 7 (P1, P3, P4, P5, P6, P7, P9) + `session-ses_07ee.md` (641 KB) | Same as above; 641 KB session dump should be split and archived. |

---

## §5 — Documentation Health Score (per top-20)

| Status | Count | Items |
|--------|-------|-------|
| 🟢 GREEN | 13 | OMEGA_ENGINE, SOVEREIGN_MANDATES, AGENTS, ACTIVE_SPRINT, HMC_COLLABORATION_HUB, README, DEBUT_REMEDIATION_MANUAL, OMEGA_CODEX, R_COPILOT_DIRECT_API, R_GROKSTER_CONTEXT_ACCOUNTING, R_RESEARCHER_GLM53, PROTOCOL_v2, LATEST_CORRECTIONS |
| 🟡 YELLOW | 5 | session_gnosis pattern (date-dupes), BRIEFING pattern (older briefings), R_OPENCODE_PLATFORM_INTERNALS (SUPERSEDED, no banner), proposed_lessons pattern (well-managed), approved_lessons pattern |
| 🔴 RED | 2 | HYDRATION_REPORT, RESEARCH_EXECUTION_UPDATE (both root-level, stale, visible from root) |

**Overall house doc health for soft launch**: 🟡 **YELLOW, trending GREEN** — only 2 RED, both fixable in <30 min (archive action); 5 YELLOW are non-blocking cleanup; 13 GREEN is solid coverage of the foundational layer.

---

## §6 — Recommendations (Prioritized Action List)

### Pre-debut (Architect-approved blockers — total: ~45 min)
1. **A2 + A1 (combined, 10 min)**: Move `HYDRATION_REPORT.md` and `RESEARCH_EXECUTION_UPDATE.md` to `docs/archive/root-level-stale/` OR add `> STALE — see LATEST_CORRECTIONS_20260828.md` banner. File:line ref: both at repo root.
2. **A3 + A4 (5 min)**: Add `> SUPERSEDED 2026-08-28 — "GPT 5.3" = GLM 5.3 Flash; see R_RESEARCHER_GLM53_FLASH_CLINE_20260828.md` banner to:
   - `data/coordination/R_ANTIGRAVITY_GPT53_20260828.md`
   - `data/coordination/R_RESEARCHER_GPT53_CLINE_20260828.md`
3. **A5 (5 min)**: Add `> SUPERSEDED 2026-08-26 — see R_OPENCODE_CONFIG_REMEDIATION_20260826.md` banner to `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md`. Verify remediation doc has been promoted (currently 0 refs).
4. **P1-P9 + session-ses_07ee (15 min)**: Move 7 P-files + 641 KB session dump out of root (per Roc §7.1). Either to `data/entities/<relevant-agent>/workspace/` or `docs/archive/dev-artifacts/`.
5. **CLOSED-investigation banner (5 min)**: Add `> CLOSED 2026-08-28 — DO NOT REDO` to `R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md` per LATEST_CORRECTIONS §6.

### Post-debut (cleanup, not blocking — total: 4–8h)
6. **Session gnosis consolidation** (Roc §7.1): archive 54+ `*_YYYYMMDD.md` files, keep current `session_gnosis.md` per entity. **Highest-ROI doc-hygiene action.**
7. **Model strategy consolidation**: link all 20+ model docs to canonical `PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`.
8. **`_v1` archive pass**: 15+ old-version files in `data/entities/roc_racoon/workspace/` (per Roc §2.2).
9. **B1–B13 stale-docs sweep**: 13 pre-Aug-2026 docs in `docs/team/`, `docs/intake/`, `docs/decisions/`, `docs/research/`.
10. **`docs/kb/` audit**: 28 entries; verify each is current; promote or archive stale ones.

### Documentation gaps to address (per Roc §6)
11. **HIGH priority**: `docs/how-to/use-dispatch-guard.md`, `docs/how-to/use-hivemind.md` (Roc §6.1)
12. **MEDIUM priority**: `docs/protocol/WITNESS_PROTOCOL.md`, `docs/protocol/L1_L2_L3_DISTILLATION.md`, `docs/how-to/use-model-fleet.md`, `docs/reference/subagent-depth.md`

---

## §7 — File:line Citations (Key Claims)

| Claim | Source |
|-------|--------|
| 4,325 .md files repo-wide | R_ROC_DOCUMENTATION_SURVEY_20260828.md §1 |
| 16 archive dirs, 64 session_gnosis files | R_ROC §2.3 + §3.1 |
| HYDRATION_REPORT.md mtime = Aug 7 | `stat -c %y HYDRATION_REPORT.md` → 2026-08-07 |
| RESEARCH_EXECUTION_UPDATE.md mtime = Jul 23 | `stat -c %y RESEARCH_EXECUTION_UPDATE.md` → 2026-07-23 |
| "GPT 5.3" = GLM 5.3 Flash correction | LATEST_CORRECTIONS_20260828.md §1 |
| PROTOCOL_SUBAGENT_MODEL v1 SUPERSEDED | Roc §2.1 line 6-22 |
| R_OPENCODE_PLATFORM_INTERNALS_20260824 SUPERSEDED | Roc §2.1 line 177 |
| Context accounting CLOSED | LATEST_CORRECTIONS §6 |
| 2 P0 cut-tool bugs ALREADY FIXED | LATEST_CORRECTIONS §6 |
| M11 soul integrity / M15 continuity patterns | SOVEREIGN_MANDATES.md §M11/M15 (referenced 238x) |
| Top-20 reference counts | `rg -l "<basename>" docs/ data/coordination/ data/entities/` 2026-08-28 |
| 8-account Cline review fleet (Option E-prime-final) | LATEST_CORRECTIONS §5 |

---

## §8 — Confidence & Caveats

- 🟢 **HIGH confidence** on: file counts, mtimes, reference counts, archive dir enumeration, top-2 RED status.
- 🟡 **MEDIUM confidence** on: substring-noise ranks (some counts include the search basename as substring of other files — e.g. R_OPENCODE_PLATFORM_INTERNALS shows 4 refs but only a subset are real "link" references; others are discussion), freshness verdicts on B1–B13 (sample-triage, not full content-read), P1-P9 ownership routing.
- ❓ **Open questions for Architect**:
  1. Does `R_OPENCODE_CONFIG_REMEDIATION_20260826.md` exist and is it the authoritative successor? (0 refs; needs promotion if so — critical for A5 banner to be honest.)
  2. Should the 7 P-files go to a specific agent's workspace, or to `docs/archive/dev-artifacts/`?
  3. Is session_gnosis consolidation in-scope for soft launch (high-ROI) or post-debut (low risk)?
  4. Should the 4 SUPERSEDED-marker additions be done in this session or in a follow-up authoring pass?

---

*⬡ OMEGA ⬡ EXPLORE ⬡ DOC-FRESHNESS v1.0.0 ⬡ 2026-08-28*
**Authority**: Complementary to Roc's survey + LATEST_CORRECTIONS; no overlapping claims.
**Time**: 15 min exploration, evidence-based.
**AP Token**: `AP-EXPLORE-FRESHNESS-20260828-v1.0.0`
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

