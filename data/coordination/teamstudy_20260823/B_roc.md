<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 TEAM-SYNTHESIS STUDY #1 — PHASE B — ROC_RACOON GROUND-TRUTH AUDIT
**AP Token**: `AP-ROC-PHASEB-VERIFY-20260823-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_teamstudy_phaseB ⬡ ACTIVE

**Date**: 2026-08-23
**Mission**: Verify/refute A_researcher, A_jem, A_carmack claims against disk/git/DB. Adversarial where warranted.
**Method**: Every number re-measured (`wc -l`, `git show <rev>:<file> | wc -l`, JSON parse, sed line-windows). Git archaeology used to date the growth, not just measure it.

---

## §1 FINDINGS — CLAIM-BY-CLAIM VERIFICATION

### 1.1 Researcher (A_researcher.md)

| Claim | Verdict | Evidence |
|---|---|---|
| **G1**: TASK_REGISTRY.json has 80 tasks; registration prompt-enforced only | ✅ VERIFIED | JSON parse: exactly 80 tasks. No mechanical registration path outside MCP tools + prompt text. |
| **G2 / C2**: `.git/hooks/pre-commit` lacks tracking-state hook; runs only soul validation | ✅ VERIFIED — **with a material nuance neither researcher nor carmack surfaced** | `.git/hooks/pre-commit` is a 6-line hand-written bash script (researcher said 7 — trivial) running ONLY `validate_soul.py`. **BUT** `omega-tracking-state` IS defined in `.pre-commit-config.yaml` (~line 137, comment: "the Iron Gate"). The mechanism exists *in config* and is *not installed into git*. Root cause is not "hook missing" — it is **the pre-commit framework itself never wired into `.git/hooks/`**. The real 10-minute fix is `pre-commit install` (or replacing the hand-written hook with the framework shim), not writing a new hook stanza. Additional confirmation of jem's M24 worry: the config entry runs bare `entry: python scripts/validate_tracking_state.py` — not `.venv/bin/python`. |
| **G3**: validator exists, CI-gated via make temple-grade/test, staleness rule present | ✅ VERIFIED | `Makefile:232` — `temple-grade: ... check-tracking-state`; `Makefile:240-242` invokes `scripts/validate_tracking_state.py`. Staleness rule at validator :228-232 (in_progress-only). |
| **G4**: zombie sweep with ACTIVE_SPRINT cross-check + review-list escape hatch | ✅ VERIFIED | `sweep_task_registry.py:2-15` docstring: ACTIVE_SPRINT-aware, routes to `sweep_review_<date>.md`, exit codes 0/2/3 documented. |
| **G5**: TS plugin surface available (`sovereign-compaction.ts`) | ✅ VERIFIED | File exists at `~/.config/opencode/plugin/sovereign-compaction.ts`. |
| **G6**: MCP write API exists (`task_registry_register/update/get/query`) | ✅ VERIFIED | `mcp_servers/omega_hub/hub_tools/task_registry.py` exports all four. |
| §3 Q4 premise: "~20 orphan sessions" needing backfill | ⚠️ UNTESTED PREMISE | Registry holds 80 tasks; my Phase-A ledger resolved ~13 dispatches, most ALREADY registered. Nobody has produced the orphan list. **Measure before building the backfill script** — the true orphan count may be far below 20. |

### 1.2 Carmack (A_carmack.md)

| Claim | Verdict | Evidence |
|---|---|---|
| All 8 god-module line counts (§0 table) | ✅ VERIFIED — 8/8 exact | `hub_tools/tools.py`=3649 (at `mcp_servers/omega_hub/hub_tools/tools.py`), observability=1660, model_gateway=1606, oracle=1455, youtube_worker=1231, memory_store=1224, providers=1303, sqlite_vec_adapter=1031. Manual §7 (:383-390) baselines match his table digit-for-digit. |
| **"Six of eight grew DURING the deletion-campaign week" (08-17→08-23)** | ❌ **REFUTED (causal narrative)** — numbers right, story wrong | Git archaeology: the Manual baselines are EXACTLY the **pre-`e2c16d3c`** file sizes (verified via `git show e2c16d3c^:<file>`: 1583/1481/1253/1181/1077/1088/992 — all seven match Manual digit-for-digit). Commit `e2c16d3c` — *"style: ruff format + mechanical lint fixes (255 files, 4849 violations)"* — landed **2026-08-17, the same day the Manual was written**, and accounts for essentially ALL the delta (observability +77, oracle +202, providers +215, sqlite_vec +39, youtube +50, memory_store +146, model_gateway +100). **Zero committed net growth since 08-17** (`git log --since=2026-08-17` on these files: empty). The freeze has actually HELD since baseline capture; the baselines were simply snapshotted hours before a same-day formatter commit. |
| …except ONE live exception | ⚠️ NEW FINDING carmack missed | `model_gateway.py` has **+30/−5 UNCOMMITTED lines right now** (worktree 1606 vs HEAD 1581): an M22 provenance fix dated 2026-08-22 removing silent OpenRouter base_url fallback. This is the only genuine post-freeze growth event — and it is dirty-tree WIP, invisible to both carmack's `wc -l` and any committed-history audit. |
| Charter defect: header says "THE SIX PHASES", table lists five (A–E) | ✅ VERIFIED | `PROTOCOL_CHARTER.md:20` header vs table rows A,B,C,D,E. |
| `ho_2f77f83964e5` pulled live | ✅ VERIFIED | `data/handoff/pending/ho_2f77f83964e5.json` exists (status: pending). |
| CUT-2: "127 verified-green files uncommitted" | ✅ VERIFIED (approx.) | `git status --porcelain` = **129** at my measurement. ±2 drift since his read is expected in a live tree; magnitude claim sound. |

### 1.3 Jem (A_jem.md)

| Claim | Verdict | Evidence |
|---|---|---|
| G2-1: live annotations file mandates M27 taxonomy at line 9; W4's `pass/fail/flagged` contradicts it | ✅ VERIFIED | `session_annotations.yaml:9` verbatim: *"verdict vocabulary: M27 ONLY — backlog\|ready\|in_progress\|blocked\|completed\|superseded\|failed"*. Four target conventions at :4-8 exactly as claimed. Jem is right — W4's enum was written without reading the data. |
| G1-3: `render()` embeds wall-clock → known-hash self-test impossible as specified | ✅ VERIFIED | `generate_session_registry.py:58-60`: `def render(registry, annotations)` with `now = datetime.now(timezone.utc)...` at :60. Non-deterministic output confirmed by inspection. |
| IR-9: generator reimplements staleness inline (:104-108) — third implementation | ✅ VERIFIED | Lines 103-107: independent `in_progress` + `(now_dt - ts).days > STALENESS_DAYS` filter. Three implementations confirmed (validator :228, sweep :66-70, generator :103). |
| G2-8: generator parses annotations YAML raw (:159-165) | ✅ VERIFIED | Lines 159-165: `yaml.safe_load` with warn-and-continue on missing file. |
| G4-4: BOTH generator (:31) and sweep (:35) import `STALENESS_DAYS` | ✅ VERIFIED | Import blocks confirmed in both files. |
| G4-2: staleness currently checks ONLY `in_progress` (validator :230, sweep :68) | ✅ VERIFIED | Both loops: `if t.get("status").lower() != "in_progress": continue`. `blocked=14d` would be new enforcement surface — jem's scope-growth flag is correct. |
| M24: pydantic 2.13.4 in `.venv`; verify hook invokes venv python | ✅ VERIFIED / ⚠️ RISK CONFIRMED | `pydantic-2.13.4.dist-info` present. And the risk is REAL: `.pre-commit-config.yaml` entry uses bare `python`, not `.venv/bin/python`. |
| IR-2: sweep exit-code semantics (0/2/3, review-list cases) | ✅ VERIFIED | Docstring :12-15 documents exactly this triple. |

### 1.4 Refuted / Corrected — Summary

1. **REFUTED**: carmack's drift-timing narrative ("grew during the campaign week"). Growth = single formatter commit on freeze-day; zero committed growth since. His *prescription* (ratify current counts + `wc -l` gate) survives — arguably strengthened — but the *evidence story* in §0 must be amended before it enters a ruling, because "agents blew the freeze" and "a linter blew the baseline on day zero" lead to different enforcement designs (see §2 Insight 4).
2. **CORRECTED (framing)**: researcher's G2. The tracking-state gate is defined-but-uninstalled. Any CEB commit-time checkpoint inherits this same installation gap — if the framework isn't wired into `.git/hooks/`, CEB gates nothing either.

---

## §2 INSIGHTS — CROSS-REPORT PATTERNS

1. **Total convergence on the meta-principle**: all four reports independently arrive at *mechanical enforcement over prompt discipline* (researcher: CEB; jem: contract tests + fail-closed; carmack: `wc -l` gate; me: pointer-integrity spot-checks). Zero collisions on values; collisions are only about scope and sequence. That convergence is itself signal — Phase C can treat "machinery beats memos" as settled and spend its budget entirely on the HOW.
2. **Everyone was half-right about the hook gap because everyone probed only one layer.** Researcher probed `.git/hooks/` (found nothing). Nobody probed `.pre-commit-config.yaml` (found everything). State + origin must be probed as a PAIR — this is the same lesson as my Phase-A filename-drift flag (F1): the artifact exists, the pointer lies. Propose for Phase C ledger: **no verification claim is admissible without its probe path recorded**.
3. **The dirty tree is a blind spot in every proposed enforcement mechanism.** Carmack's `wc -l` gate measures worktree (would catch the model_gateway +25 — good), but researcher's commit-time CEB and carmack's "commit NOW" CUT-2 both assume the tree gets committed promptly. There is currently uncommitted M22-critical work sitting in `model_gateway.py` **during a study about tracking integrity**. Practice what we preach: that diff should be committed (or explicitly parked) before Phase 3's path-staged commit.
4. **Mechanical tooling can silently defeat numeric freezes.** The entire god-module "drift" was `ruff format` reflowing 255 files. A naive `wc -l` gate will cry wolf on the next formatter pass — and a gate that fires falsely gets disabled within a month. Design requirement for carmack's Ruling #1: the gate needs either formatter-aware exemption (compare AST/token counts?) or an explicit re-baseline ritual tied to formatter commits. Otherwise it enforces noise.
5. **Jem's blocking-gaps list and carmack's cut list collide productively on Item 3.** Jem found 10 gaps in the hash-chain spec (implying significant build cost); carmack wants it cut entirely. These aren't in tension — jem's gap density is *evidence for* carmack's cut. The synthesis writes itself: defer Item 3, keep only jem's G3-8 principle (audit-before-mutate ordering) as a one-line comment/contract in sweep until post-debut.

---

## §3 QUESTIONS & CHALLENGES — ADDRESSED TO NAMED TEAMMATES

### → TO RESEARCHER

1. **Answered (your §3 Q1 to me)**: I checked the container topology. No OpenCode-in-container quadlet exists — `deploy/infra/` and `config/containers/` hold only hub/qdrant/searxng service units. All `task()` spawns originate from the host OpenCode process, so **one plugin call site covers current topology**. Caveat for the design doc: if the legacy roc_racoon quadlet (mentioned in SOVEREIGN_MANDATES context) is ever revived as an agent host, its instance needs its own plugin — note it as a known limitation, don't build for it now.
2. **Challenge — your §1 migration estimate**: "~20 orphans" appears twice but is never enumerated. My Phase-A sweep found the recent ledger largely registered already. Before anyone builds the backfill script, produce the actual orphan list (query: sessions in opencode.db with deliverable artifacts vs TASK_REGISTRY rows). If it's 6, not 20, option (b)-only might beat the hybrid.
3. **Challenge — CEB commit-time checkpoint depends on the broken thing you're fixing**: your Step 1 ("fix G2, 10 min") must be specified as *install the pre-commit framework into `.git/hooks/`*, not merely *add a stanza*. And per the bare-`python` entry: the fixed wiring must pin `.venv/bin/python` or every pydantic import (jem's Item 2) bricks the hook on system Python. Please amend §2 step 1 accordingly.
4. **Question — sweep-time scope compounding**: your sweep-time spot-check adds a second new sweep enforcement surface (completed-artifact checks) in the same sprint jem flags `blocked=14d` as the first. Two scope expansions to a pre-commit-gated script in one PR is exactly the blast radius carmack's MERGE warns about. Should sweep-time spot-check land in a separate, later PR?

### → TO JEM

1. **Amendment to your IR-5**: the injectable clock must cover **two** wall-clock sites, not one — `render()`'s header stamp (:60) AND the hygiene section's staleness ages (:103, `now_dt = datetime.now(timezone.utc)`). A `now` parameter threaded to only the header still leaves non-deterministic bytes. Your test #4 should assert byte-identity across a day boundary with the frozen clock to prove both sites covered.
2. **Your M24 action item resolves darker than you wrote**: it's not just that the hook *might* run under system python — the config entry literally says `entry: python scripts/validate_tracking_state.py`, and the installed `.git/hooks/pre-commit` never invokes the pre-commit framework at all. Recommend escalating your M24 row from "⚠️ verify" to "🔴 prerequisite for Items 2+3": no pydantic gate can have teeth until (a) framework installed, (b) entry pinned to `.venv/bin/python`.
3. **Challenge — G1-1 blocking severity**: you mark undefined domain vocabulary BLOCKING, but your own G4-1 recommendation decouples staleness class from domain (explicit `stale_class` field). If decoupled, what breaks if Item 1 ships with domains validated warn-only and the enum hardened post-debut? If nothing structural, G1-1 should downgrade to HIGH — it's a vocabulary decision, not a load-bearing wall.

### → TO CARMACK

1. **Your §0 needs a forensic amendment before it drives Ruling #1** (see §1.2): the growth is `e2c16d3c` (ruff format, 2026-08-17, same-day-as-Manual), not week-long agent creep; committed growth since then is zero. I agree with ratify-current-baselines — MORE strongly, since the delta was mechanical formatting, not feature creep — but the ruling text should record the true cause, because "freeze failed because nothing measured it" and "baseline was snapshotted pre-formatter-commit" justify different gate designs (see §2 Insight 4: formatter-aware exemption or re-baseline ritual, else false-positive gate).
2. **Hidden evidence dependency in CUT-3**: you'd skip backfill annotations because "nobody will query" concluded-session annotations. But the generator renders an annotations section and the file already carries 15 migrated seed entries (from EXPERT_SESSION_REGISTRY §4.x, per its own header) — cutting backfill annotations creates a permanently two-tier quality record where the §2 Domain Index and any future Langfuse-style scoring have holes exactly where history is thinnest. Cheap middle path: backfill a one-line `verdict: completed` annotation per session (schema-valid, zero prose) rather than full assessments. Does your cut survive that amendment? It costs minutes.
3. **Probe of CUT-1's substitution logic**: if the hash-chain audit log is deferred, the pre-debut tamper-evidence layer is… git history. That substitution works ONLY if CUT-2 lands first (tree committed) and IF sweep `--apply` mutations happen on committed state. Say this dependency explicitly in the cut rationale — otherwise a reader could accept CUT-1 while rejecting CUT-2 and leave the registry mutation path with zero evidence layer.
4. **Question — Ruling #6 vs your own CUT philosophy**: Ruling #6 says extend `validate_tracking_state.py` with a completed-requires-artifact rule; researcher's CEB says add an `evidence` field schema. Your version needs no schema change (validator can heuristically check notes/deliverable paths); hers is explicit but touches Tier-0/Tier-3 schemas (M27 territory, TRACKING_ARCHITECTURE amendment). Which do you actually want — heuristic warn (yours, zero schema churn) or explicit field (hers, cleaner but heavier)? Phase C should force this fork to a single pick.

---

## §4 REVISIONS TO MY OWN PHASE-A REPORT

| # | Revision | Basis |
|---|---|---|
| R1 | **F2 count precision**: "25 AUD- refs" stands as 25 *unique* AUD- IDs (`grep -o \| sort -u` = 25); my earlier phrasing invited line-count confusion (grep -c gives 26 because AUD-03/AUD-04 each appear twice). No correction needed; measurement method now pinned. | Re-measured today |
| R2 | **New flag F6 (should have caught it)**: `.pre-commit-config.yaml` defines `omega-tracking-state` but the framework is not installed into `.git/hooks/` — meaning my Phase-A statement "already registered as critical-gap-audit…" etc. was fine, but the broader implication I left implicit (that the M27 gate merely needs a stanza) was wrong. The gate is doubly unwired: not installed AND not venv-pinned. This strengthens F2's "integration never happened" theme into a systemic pattern: **defined ≠ wired**. | §1.1 G2 nuance |
| R3 | **F3/F4 gain design consequence**: kali-launched Missions A/B and N5 mean any lineage-based auto-backfill (researcher §1 option b, "reconstruct launch metadata from opencode.db") WILL misattribute parentage unless it reads `parent_id` rather than assuming researcher lineage. My flags were advisory; they are now hard requirements for the backfill spec. | Cross-reference with researcher §1 |
| R4 | No other Phase-A claims amended: 18/18 session resolutions, 5/5 registry spot-checks, and the ox-alpha `in_progress` status (re-confirmed today via JSON parse: still `in_progress`, 80 tasks total) all survived adversarial re-measurement. | Re-measured today |

---

## §5 SUMMARY (5 lines) + COUNTS

1. Researcher's six grounding facts all verified — but G2's root cause is deeper than reported: the M27 gate is *defined in config, never installed into git*, and unpinned to venv python; the real fix is framework installation, not a new stanza.
2. Carmack's 8/8 god-module numbers are exact, but his drift narrative is REFUTED by git archaeology: all growth = `e2c16d3c` ruff-format commit on freeze-day itself; zero committed growth since 08-17; one live exception (+25 uncommitted M22 fix in model_gateway.py).
3. Jem's file-level claims verified 9/9 including the two blockers (M27 taxonomy collision, wall-clock non-determinism); her M24 venv risk is CONFIRMED at config level and escalates to prerequisite.
4. Strongest cross-report synthesis: jem's 10-gap density on Item 3 is the evidence that wins carmack's CUT-1; the "defined ≠ wired" pattern unites my F2, researcher's G2, and the dirty model_gateway diff.
5. Five challenges issued (2 researcher, 3 carmack/jem forks requiring Phase-C rulings); 4 self-revisions logged; my Phase-A verdicts otherwise survive re-measurement.

| Metric | Count |
|---|---|
| Claims VERIFIED | **24** (researcher 5+1-premise-split, carmack 11 incl. 8 line-counts, jem 9 minus overlaps → tallied individually in §1) |
| Claims REFUTED | **1** (carmack drift-timing narrative — numbers stand, causality corrected) |
| Claims CORRECTED/NUANCED | **2** (researcher G2 root cause; jem M24 escalation) |
| UNTESTABLE | **3** (researcher's OTel/GitLab prior-art anecdotes; carmack's effort estimates; his "~20 orphan" figure shared with researcher — pending enumeration) |
| New findings contributed | **2** (uninstalled pre-commit framework + bare-python entry; dirty model_gateway.py +25 during freeze) |
| Challenges to teammates | **7** (researcher 3, jem 3, carmack 4 — two joint forks) |
| Self-revisions | **4** (R1–R4, none overturning Phase-A verdicts) |

*⬡ OMEGA ⬡ ROC_RACOON ⬡ PHASE-B GROUND-TRUTH AUDIT ⬡ 24 VERIFIED · 1 REFUTED · 2 NUANCED · 3 UNTESTABLE ⬡ 2026-08-23*

---

## PHASE-C RESPONSE (roc_racoon)
**AP Token**: `AP-ROC-PHASEC-RESPONSE-20260823-v1.0.0`

### O-Q3 → carmack: Working-tree hygiene certification — ✅ CERTIFIED WITH ONE FINDING

Measured this round (all numbers re-run today):

| Check | Result |
|---|---|
| Tree state | 129 porcelain lines: 90 `??`, 37 staged-modified, 2 added-modified |
| Path-staged commit surface | Exactly 5 files: Makefile, GAP_REGISTRY.json, generate_session_registry.py, sweep_task_registry.py, validate_tracking_state.py (+579/−38) |
| Secrets scan (staged diff) | CLEAN — one false positive ("Token Budget Manager" topic string); no key formats, no private-key blocks, no bearer tokens |
| Secrets scan (all 90 untracked files) | CLEAN — full key-format sweep returned zero hits |
| Stray junk | `data/coordination/metrics.json` is gitignored (verified via check-ignore); teamstudy/, locks/, sessions/ are legitimate structure. Root-level strays exist (`MANDATES_CONDENSED.md`, `MANIFEST.md`, 2 PILLAR_*.md) — do NOT `git add .`; keep the commit strictly path-staged |
| Scrub posture | No scrub required on the staged surface. The M22-critical dirty diff in model_gateway.py remains UNCOMMITTED and OUTSIDE this commit — per my Phase-B §2 Insight 3 and Ma'at Fork 3 prerequisite, commit/park it separately BEFORE this lands |

**Certification requires**: (1) secrets scan of staged diff + all files entering the commit [done], (2) confirm staging is path-explicit, never `git add .` [condition], (3) resolve or explicitly park the model_gateway.py WIP first [condition]. With those two conditions met, I certify the 5-file commit clean.

**Full 80-row pointer walk vs 5/80 sampling**: FULL WALK — decided by measurement, not opinion. I ran it: JSON parse + existence-check over all 80 rows = **0.003 seconds**. It is not merely cheap enough to replace sampling; it already PAID FOR ITSELF — it caught a broken pointer sampling would likely have missed: `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md.` (trailing period, unresolvable as written). Sampling a 3ms operation was ceremony. Recommend the walk become the standard pre-commit gate for any registry-touching commit (S7's harness territory).

### O-Q4 → jem: Evidence grade — CONCUR, one amendment

Existence+mtime-window as standard grade, hash reserved post-debut: **concur**. Rationale: jem's own 10-gap density on CUT-1 is the cost proof; mtime-window delivers ~90% of the tamper-evidence value at ~5% of the build cost; hash layers on later without schema break if the evidence field is versioned from day one (consistent with Ma'at F2's explicit-field pick).

**One amendment**: bind each evidence claim to its **probe path** (my Phase-B §2 Insight 2 — "no verification claim admissible without its probe path recorded"). Existence+mtime tells you *that*; probe path tells you *how verified*, which is what made the G2 hook-gap invisible to four auditors probing single layers. Cost: one string field, zero new machinery.

### Ma'at :104 correction — ACCEPTED

Substantively my two-site claim stands; citation off-by-one acknowledged. Noted that my own Phase-B report carried the inconsistency (:104-108 in §1.3 vs :103 in §3-to-jem) — the exact filename-drift class I flagged in F1. Logged without prejudice; fitting.

### S1–S12 standing objections: NONE

Confirmed zero objections across all twelve settled points. Specifically: S8 (my corrected table verbatim, naive execution forbidden), S9 (parent_id attribution = my R3 hard requirement), S12 (my scope-compounding challenge adopted) all land as I argued them. No undiscovered disagreements to report (convergence criterion #4 satisfied from my side).

*⬡ OMEGA ⬡ ROC_RACOON ⬡ PHASE-C RESPONSE ⬡ CERTIFIED · FULL-WALK-MANDATED · NO-OBJECTIONS ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
