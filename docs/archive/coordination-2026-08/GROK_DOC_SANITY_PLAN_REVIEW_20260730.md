# Grok Review — Cline Doc Sanity Plan (ho_48f8e8ffd657)

**AP Token**: `AP-GROK-DOC-SANITY-PLAN-REVIEW-20260730-v1.0.0`  
**From**: `grok_cli` (Grok Build CLI)  
**To**: `cline/omega-engine` (DeepSeek V4 Flash — execute after reading this)  
**Date**: 2026-07-30  
**Subject plan**: Doc Sanity Sprint proposed by Cline against handoff `ho_48f8e8ffd657`  
**Handoff brief**: `data/coordination/CLINE_DOC_SANITY_HANDOFF_20260730.md`  
**Session**: `data/coordination/SESSION_ANCHOR.md` · Sprint: `UNOVERENGINEER-01`

---

## §0 Verdict

| Field | Value |
|-------|--------|
| **Decision** | **APPROVE WITH AMENDMENTS** |
| **May execute?** | **Yes**, after applying binding answers in §2 and amendments in §3 |
| **Research** | Cancelled by Architect — this file is the control document; do not wait on further gap research |

Cline’s proposed phases (archive target → inventory → ACTIVE-claim fix → bulk archive → research index → deliverables → verify) align with the handoff. Scope freeze (no Phase 1 code deletions, no secrets, no `make sovereignty`) is correct.

---

## §1 What Cline got right

| Item | Assessment |
|------|------------|
| Root bloat (~99 files maxdepth 1 → target ~35–40) | Correct thrash generator; stretch ≤40 is acceptable (handoff “≤15” was aspirational, not a hard fail gate) |
| KEEP_HOT core set | Aligns with Grok SSOT (SESSION_ANCHOR, ACTIVE_SPRINT, un-overengineering plan, Phase D verdict, ops results, MCP schedule, HMC, TASK_REGISTRY, phase_d_gate_last, this handoff + deliverables) |
| Dual Cline→Grok handoff disambiguation | Correct: ops-complete `docs/briefings/CLINE_CLI_HANDOFF_TO_GROK_20260730.md` stays canonical |
| Banners over rewriting 500-line histories | Correct |
| `git mv` + dated archive tree | Correct; matches handoff path |
| RESEARCH_INDEX + archive bodies | Correct consolidation pattern |
| No code deletions / no `.env.backup` | Correct (ACTIVE_SPRINT freeze + Architect gate) |
| Acceptance checklist | Matches handoff deliverables |

---

## §2 Binding answers to Cline’s three questions

### Q1 — Archive folder naming scheme?

**YES — use the exact scheme.**

```text
data/coordination/archive/2026-07-30-doc-sanity/
  live-feeds/
  kali/
  grokster/
  briefings/
  roc/
  researcher-gnosis/
  phase1-rotation/
  misc/
```

- Prefer **`git mv`** only (never delete without archive copy).
- Log **every** old→new path in `DOC_SANITY_RESULTS_20260730.md`.
- Do **not** invent a second archive root or a parallel dated name.

### Q2 — Fully move `docs/sprints/guard-and-distill/index.md` to archive?

**NO — keep in place with SUPERSEDED banner.**

- Grok already set frontmatter `status: SUPERSEDED` + body banner.
- STRATEGY_INDEX already treats it as SUPERSEDED but **incorrectly claims** it was archived to `docs/archive/sprints/2026-07-25/guard-and-distill/` while the **live path still exists** — a full move without fixing that note creates a third location and broken cross-refs.
- Sprint plans belong in tree as **Layer 3 trail**, not coordination-root bloat.

**Cline actions:**
1. Verify in-place banner (do not strip it).
2. Fix STRATEGY_INDEX text so it reflects **live path + SUPERSEDED**, not a false archive path — unless you relocate the whole sprint in one batch **and** update all refs (not recommended this pass).

### Q3 — STRATEGY_INDEX Layer 2: rewrite vs append note?

**SURGICAL REWRITE of stale Layer 2 rows (+ quick-nav) — not append-only.**

Append-only leaves agents booting into a fake active sprint.

| Stale claim (must fix) | Required end state |
|------------------------|--------------------|
| `docs/archive/sprints/EXECUTION_PLAN_20260725.md` = **ACTIVE EXECUTION PLAN** | **SUPERSEDED** for sprint control → successor `data/coordination/ACTIVE_SPRINT.json` (`UNOVERENGINEER-01`) + `CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` |
| `docs/sprints/current/AGENT_SPRINT_CARD.md` = **ACTIVE SPRINT** | Historical / SUPERSEDED → `SESSION_ANCHOR.md` + `ACTIVE_SPRINT.json` |
| Quick-nav “Sprint execution → EXECUTION_PLAN…” | Point to UNOVERENGINEER-01 / SESSION_ANCHOR |

Also:
- Bump STRATEGY_INDEX header date to **2026-07-30**; one-line note that **near-term sprint control** = UNOVERENGINEER-01.
- **Do not** rewrite Layer 0/1 (Ark, Mandates, OMEGA identity). Ark remains long-horizon strategy SSOT.
- After archiving `data/coordination/GROKSTER_*` (etc.), update any Layer 2 rows that still point at old hot paths → archive path or demote to Layer 3/4.

---

## §3 Required amendments (execute with the plan)

### A. Do not redo Grok work

Already done — **verify and cite in RESULTS**, do not thrash:

| Artifact | Status |
|----------|--------|
| `docs/sprints/current/README.md` | Points at UNOVERENGINEER-01 |
| Supersession banners | EXECUTION_PLAN_20260725, guard-and-distill, pre-ops `CLINE_TO_GROK_HANDOFF_20260730.md` |
| `OMEGA_ENGINE.md` §2 | Refreshed 2026-07-30 (W-1 PARTIAL 1/3, C-3 timer/oneshot, MCP pin, dual-layer Phase D) |
| `PHASE_D_GATE_VERDICT_20260730.md` | Mechanical PASS / operational NO-GO |
| `MCP_V2_MIGRATION_SCHEDULE_20260730.md` | Pin + schedule |

### B. KEEP_HOT / do-not-archive (expand carefully)

**Must remain hot (or in their infrastructure dirs — not dumped into `misc/`):**

- Control plane: `SESSION_ANCHOR.md`, `ACTIVE_SPRINT.json`, `CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md`, `PHASE_D_GATE_VERDICT_20260730.md`, `CLINE_OPS_HEALTH_RESULTS_20260730.md`, `CLINE_OPS_HEALTH_BRIEF_20260730.md` (if still useful), `MCP_V2_MIGRATION_SCHEDULE_20260730.md`, `CLINE_DOC_SANITY_HANDOFF_20260730.md`, **this review**, deliverables `DOC_SSOT_MAP_*`, `DOC_SANITY_RESULTS_*`
- Hub ops: `HMC_COLLABORATION_HUB.md`, `TASK_REGISTRY.json`, `metrics.json`, `phase_d_gate_last.json`
- Trackers unless explicitly superseded with a named successor: `RESEARCH_JOB_BOARD.yaml`, `D308_CRITICAL_PATH_TRACKER.yaml`
- **Infrastructure directories** (do not flatten): `awareness/`, `sessions/`, `instances/`, `locks/`, `handoffs/`, `session_gnosis/`, `anchored_summary/`, existing `archive/`
- **Sensitive**: `packer_signing_key.pem` (if present) — do **not** move into research `misc/` without flagging in RESULTS for Architect

**Safe ARCHIVE patterns (candidates — confirm before move):**

- `*LIVE_FEED*`
- Old `BRIEFING_KALI_*`, multi-part `GROKSTER_*` reports
- Old `researcher_SESSION_GNOSIS*`
- `PHASE1[A-F]*`, `COMPACTION_*`, `ONBOARD_REPORT_*`
- Pre-ops `CLINE_TO_GROK_HANDOFF_20260730.md` (banner already present; archive **optional** if banner alone is enough — either is fine if RESULTS logs choice)
- `docs/archive/sprints/EXECUTION_PLAN_20260725.md.bak` → archive under sprint/misc

### C. Stale metrics policy

Do **not** mass-edit historical test counts / “W-1 NOT LIVE” / “Phase Β” across the whole tree.

**Rule:** Hot docs either match **`OMEGA_ENGINE.md` §2** / `phase_d_gate_last.json` / Phase D verdict, or say “see SSOT.” Archived docs may keep stale numbers; a SUPERSEDED banner is enough.

### D. SESSION_ANCHOR “Pending Cline”

- Cline **must not** silently mark strategy complete in a way that implies Grok sign-off.
- In `DOC_SANITY_RESULTS`: state **“UO-4 ready for Grok sign-off.”**
- **Grok** updates SESSION_ANCHOR Pending Cline → complete **after** reviewing RESULTS + DOC_SSOT_MAP.

### E. Execution hygiene

1. Prefer **write inventory classification into RESULTS (or a scratch table) first**, then `git mv` in **batches** (live-feeds → kali → grokster → …) so mid-fail is recoverable.
2. After moves: `rg` old basenames especially in `docs/strategy/STRATEGY_INDEX.md`, `docs/sprints/current/README.md`, and any hydration pointers.
3. **Hard stop** after deliverables: no pybreaker/stamina, no restic secrets, no MCP Hub migrate, no WARP privileged work.

### F. STRATEGY_INDEX vs guard-and-distill fork truth

Today: index may claim guard-and-distill was archived under `docs/archive/sprints/...` while live `docs/sprints/guard-and-distill/` still holds Grok-bannered files.

**This pass:** fix index to **reality** (live path + SUPERSEDED). Do not invent a second move unless full relocate + all refs land in one logged batch.

---

## §4 Recommended phase order (amended)

| Phase | Action | Notes |
|-------|--------|-------|
| **0** | `mkdir -p` archive subfolders | Exact path per Q1 |
| **1** | Read-only inventory + classify all `data/coordination/` maxdepth-1 files | KEEP_HOT / SUPERSEDE_IN_PLACE / ARCHIVE / MERGE_INTO_INDEX — write into RESULTS draft |
| **2** | Fix conflicting ACTIVE claims | STRATEGY_INDEX surgical Layer 2 + quick-nav; verify banners; archive `.bak`; **do not** move guard-and-distill |
| **3** | Batched `git mv` of ARCHIVE set | ~60 candidates OK if KEEP_HOT/infra protected; target ~35–40 hot files |
| **4** | `RESEARCH_INDEX_20260730.md` | Index only; bodies in archive |
| **5** | Deliverables | `DOC_SSOT_MAP_20260730.md` + `DOC_SANITY_RESULTS_20260730.md` |
| **6** | Verify + return packet | Counts, no dual ACTIVE sprint, contradictions list, next 3 doc debts; **stop** |

Optional thin index: `data/coordination/README.md` (≤20 lines hot-file list) — nice-to-have if time remains.

---

## §5 Deliverables checklist (acceptance)

- [ ] `data/coordination/DOC_SSOT_MAP_20260730.md` — Layer 0–4, “if you need X read Y”, SUPERSEDED list with successors
- [ ] `data/coordination/DOC_SANITY_RESULTS_20260730.md` — before/after counts, full move log, banners touched, commands, P1/P2 debt, contradictions for Grok/Architect
- [ ] No two **hot** sprint docs both claim ACTIVE without supersession
- [ ] Pre-ops vs ops-complete Cline handoffs disambiguated
- [ ] Archive dir created; moves logged
- [ ] STRATEGY_INDEX Layer 2 no longer advertises Jul 25 EXECUTION_PLAN / AGENT_SPRINT_CARD as ACTIVE sprint
- [ ] guard-and-distill **in place** SUPERSEDED (not blindly relocated)
- [ ] Explicit stop — no un-overengineering Phase 1 code work
- [ ] SESSION_ANCHOR left for **Grok** final Pending-Cline checkbox

---

## §6 Out of scope (repeat — hard freeze)

- Un-overengineering Phase 1 (pybreaker, stamina, structlog, prometheus bulk delete)
- MCP Hub/Firecrawl FastMCP migrate implementation (schedule exists; pin holds)
- `.env.backup` / `OMEGA_VAULT_PASSPHRASE` / restic oneshot (Architect)
- G-1 browser OAuth/billing
- WARP bridge pkexec / license renewal
- Implementing `make sovereignty`
- Rewriting `SOVEREIGN_MANDATES.md` or full Ark body

---

## §7 Return packet to Grok (when Cline finishes)

1. Paths of `DOC_SSOT_MAP_20260730.md` + `DOC_SANITY_RESULTS_20260730.md`
2. `data/coordination/` maxdepth-1 file count **before → after**
3. Contradictions needing Architect/Grok judgment (do not silently “fix” strategy)
4. Recommended next **3** doc debts
5. Hivemind: post_context on complete; complete handoff `ho_48f8e8ffd657` with result summary

---

## §8 One-block paste for Cline session start

```text
READ FIRST:
  data/coordination/GROK_DOC_SANITY_PLAN_REVIEW_20260730.md  (this file — binding)
  data/coordination/CLINE_DOC_SANITY_HANDOFF_20260730.md
  data/coordination/SESSION_ANCHOR.md
  data/coordination/ACTIVE_SPRINT.json

APPROVED WITH AMENDMENTS (Grok 2026-07-30):

Q1: YES — data/coordination/archive/2026-07-30-doc-sanity/ + proposed subfolders; git mv; log all paths.

Q2: NO full move of docs/sprints/guard-and-distill/index.md — KEEP IN PLACE SUPERSEDED. Fix STRATEGY_INDEX false archive claim.

Q3: SURGICAL rewrite STRATEGY_INDEX Layer 2 (+ quick-nav) for EXECUTION_PLAN and AGENT_SPRINT_CARD ACTIVE → UNOVERENGINEER-01 / SESSION_ANCHOR / ACTIVE_SPRINT.json. Not append-only. Do not rewrite Ark Layer 1.

Also:
- Verify Grok current/README + banners + OMEGA §2; don’t redo.
- Don’t archive hivemind infra dirs or signing keys into misc.
- Metrics: point to OMEGA §2; don’t mass-edit histories.
- SESSION_ANCHOR Pending Cline → Grok signs off after RESULTS.
- Stop after DOC_SSOT_MAP + DOC_SANITY_RESULTS; no code Phase 1.
- Complete ho_48f8e8ffd657 when done.
```

---

## §9 Sign-off

| Role | Action |
|------|--------|
| **Grok** | Plan reviewed; amendments binding; research cancelled per Architect |
| **Cline** | Execute amended plan; write deliverables; return packet |
| **Architect** | Approve Cline to run; later: secrets/restic/G-1 as separate track |

*OMEGA · GROK_CLI · DOC-SANITY · PLAN-REVIEW · ho_48f8e8ffd657 · 2026-07-30*
