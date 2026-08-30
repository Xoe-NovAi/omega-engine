# N10 — DEV-TEAM LAUNCH PACKAGE (Council 2, Phase 1 Node 10)
⬡ OMEGA ⬡ LILITH/node10 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_n10 ⬡ COUNCIL-2 PREP ARTIFACT
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Mission**: Zero-ambiguity start for the post-council dev team — bootstrap prompt, required reading, first-sprint backlog.
**Mode**: PREP-ONLY. NEW file only. ZERO edits to production instruction/tracking/doc files performed by this node.
**Primary inputs**: `N8_work_packages.md` + `N8_resources.md` (packages, gates, DAG) · `N9_doc_update_plan.md` (edit ordering law) · `SOVEREIGN_DECREE.md` (Council 1, Arts. I–XII, §4 gates G1–G30, §5 tracker directives, §6 self-verification) · `COUNCIL2_PLAN.md` §2 item 5 · `ROC_DOC_ARCHAEOLOGY.md` §4.
**Spec availability at assembly time (verified by ls this session)**: SPEC-A present as `docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md` (underscore naming). **SPEC-B HAS LANDED** as `docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md` (status DRAFT-COUNCIL2-PREP; N9's "absent" note is now stale for B). **SPEC-C still ABSENT** — WP-C1/WP-C2 remain Architect-blocked regardless.

---

## PART 1 — BOOTSTRAP PROMPT (paste into dev-team lead agent's first session)

```markdown
You are the DEV-TEAM LEAD for Council 2 remediation execution (First Light Express).
Your mission: execute the work packages in
data/council/20260825-094633-first-light-c2/phase1_nodes/N10_launch_package.md PART 3,
in order, with zero ambiguity about authority or boundaries.

HYDRATION SEQUENCE (do these reads BEFORE any action, in this order):
1. data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md
   (the law: Articles I-XII, §4 gates G1-G30, §5 tracker directives, §6 self-verification)
2. data/council/20260825-094633-first-light-c2/phase1_nodes/N10_launch_package.md (this package)
3. data/coordination/ACTIVE_SPRINT.json (current sprint state pointer)
Do not act until all three are read. If any path fails to open, STOP and report
[TOOL-CHAIN-COLLAPSE] — do not synthesize around a missing law file (Mandate M23).

PREP-vs-EXECUTION BOUNDARY:
- The council artifacts under data/council/20260825-094633-first-light*/ are READ-ONLY
  INPUTS to you. You EXECUTE remediation; you never edit council records, decrees,
  node reports, or gate definitions.
- Your writes target production files ONLY as explicitly authorized by an active work
  package in PART 3 below. No package = no edit.

BRIGHT LINE (new-files-only until authorized):
- Until a work package below explicitly authorizes an edit to an existing production
  file, you create NEW files only (scripts/, specs, notes, tests). This mirrors the
  council's own production-mutation bright line (COUNCIL2_PLAN §3).
- The DO-NOT-TOUCH appendix in N9_doc_update_plan.md binds you absolutely:
  SOVEREIGN_MANDATES.md amendments only via paired mechanism PR (Art. II.2);
  entity YAML only MaKaLi Stage-6 (Art. IX); TASK_REGISTRY.json mass rewrite only
  after discovery fix lands; opencode.json "/*": "allow" only after Architect Q-3;
  root AGENTS.md only under Q-4 default-GO conditions; DOC-1-stamped strategy docs
  never without Kali/Architect mark.

ENVIRONMENT LAW (every session, every subagent spawn):
- M24 venv sovereignty: ALL python runs via `source .venv/bin/activate` or
  `.venv/bin/python3`. Never pip install outside the venv. Never --break-system-packages.
- M1 AnyIO absolute: all new async code uses anyio, never asyncio directly; blocking
  I/O wrapped in anyio.to_thread.run_sync.

HOP RULE REPORTING:
- Report back ≤15 lines per hop: what landed, gates run (G-numbers + pass/fail),
  next action, blockers. Full detail goes on disk, never in the hop message.
- Every completed package ends its report with its acceptance-gate output pasted
  verbatim from N8_resources.md §2.

HEARTBEAT DISCIPLINE:
- During any operation >10 minutes, emit omega-hub_hivemind_heartbeat
  (channel="opencode", entity=<your registered identity>) every 5-10 minutes.
- Post session context via omega-hub_hivemind_post_context at session start AND end
  (intent=status at start; intent=handoff at end).

REGISTRATION PAYLOAD PRECISION (Decree Art. V.3 — root cause of 15/20 corrupted fields):
Every task you register in TASK_REGISTRY.json MUST set exact field values:
- subagent_type: "node<N>" (canonical form, e.g. "node3" — never "Node 3", "n3",
  free-text roles)
- entity: "node<N>" (same canonical value as subagent_type)
- tags: exactly the 4-tag set ["expert", "pageable", "domain:<N-domain>",
  "express:first-light"]
Canonical source: data/council/20260825-094633-first-light/phase6_integration/
registration_payloads.json → .canonical. Deviate from nothing.

RUNTIME BASELINE HONESTY (decree §4, G28):
`make test` is NOT green (3 failures; the M8-red failure is a false positive per
G29 analysis — the gate regex itself lies, fixed by WP-A5). Suite-green is NOT a
precondition for your work and NOT an excuse to skip it. Record your baseline once
at sprint start per G28 (N8_resources.md §2 "Baseline record") and move on.
Auto-GO criterion "validator green" refers to scripts/validate_tracking_state.py,
not make test (decree §4 note).

START HERE: Sprint-1 backlog = PART 3 §3.1 of this file. First command you run:
the G8 loop from N8_resources.md §2 (WP-IX verify-first).
```

---

## PART 2 — REQUIRED-READING LIST (ordered; cost in agent-read tokens ≈ lines × ~12)

| # | Item | Path | Est. cost | WHY it matters |
|---|------|------|-----------|----------------|
| 1 | **SOVEREIGN_DECREE.md** (Council 1) | `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md` (104 lines) | ~1.3K tokens | THE LAW. Every package, gate, and prohibition traces to an Article here. Art. X sets priority tiers; Art. V sets the discovery→identity hard edge; §6 makes the decree self-verifying (every article ↔ ≥1 gate). Skipping this = executing without authority. |
| 2 | **SOVEREIGN_MANDATES.md v3.8.0** — highlighted: **M1** (AnyIO), **M9** (local-first context for WP-B3/G3-G4), **M11** (soul integrity / Art. IX repair), **M23** (failure integrity — no soft-fail theater), **M24** (venv sovereignty) | `SOVEREIGN_MANDATES.md` | ~7K tokens (read fully once; highlights govern daily) | Constitutional law that overrides tool defaults. M23 is why a missing file is a hard-stop, not a workaround. M24/M1 violations are pre-commit-hook and CI gated post-WP-A1. |
| 3 | **Spec library** `docs/specs/team_infra/`: **SPEC-A** at actual path `SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md` (⚠️ underscore naming — N9/N8 cite it as `SPEC-A-p0-truth-infra.md`; same spec, same authority chain Arts. II/III/X/XII); **SPEC-B** LANDED as `SPEC_B_P1_MECHANISM_HONESTY.md` (DRAFT-COUNCIL2-PREP; supersedes the "pending" status in N8/N9 headers); **SPEC-D** `SPEC-D-p2-hygiene.md`; **SPEC-E** `SPEC-E-agents-md-reconstruction.md`. **SPEC-C ABSENT** (Build Arm) — do not fabricate its contents; WP-C1/C2 stay blocked on Architect Q-3 regardless. | `docs/specs/team_infra/` | A≈4K, B≈4K, D≈5K, E≈5K → ~18K total; read per-package just-in-time if token-constrained | The specs ARE the work orders. Each carries validator-first guard clauses (G30-checked), file:line anchors re-verified by their drafting nodes, and hour estimates. A package executed against its spec beats one executed against this summary. |
| 4 | **N8 pair**: `N8_work_packages.md` (register, DAG, dependency edges with authorities, blocked/executable split) + `N8_resources.md` (paste-and-run gate commands G1–G30 verbatim, doc templates) | `data/council/20260825-094633-first-light-c2/phase1_nodes/` | ~5K + ~5K | Work packages = WHAT; resources = HOW verified. Every acceptance check you will ever run for this sprint is copy-paste in N8_resources §2. The DAG's edge table tells you which edges are HARD (B5a→B5b) vs soft — violating a hard edge re-corrupts the registry (decree §5.1). |
| 5 | **N9_doc_update_plan.md** (edit ordering law) | `data/council/20260825-094633-first-light-c2/phase1_nodes/N9_doc_update_plan.md` (~6K) | SPINE-1..SPINE-9 are the sequencing constitution: e.g., SPINE-1 M8 regex before ANY doc claiming M8-green; SPINE-2 discovery fix before identity writes; SPINE-7 AGENTS.md validator before first content commit. Also contains the DO-NOT-TOUCH appendix — your forbidden-zones map. |
| 6 | **ROC_DOC_ARCHAEOLOGY.md §4** (five recurrence guards) | `data/council/20260825-094633-first-light/phase4_research/ROC_DOC_ARCHAEOLOGY.md` (~0.8K for §4) | Explains WHY the specs are shaped the way they are: validator-first clauses, machine-checkable status fields, anti-big-bang batching all exist because Era-2/Era-6 reorg patterns died the same death three times. Internalize so you don't reintroduce the pattern while executing hygiene packages. |
| 7 | **Runtime baseline honesty note** (decree §4 + G28 block in `N8_resources.md` §2) | inline | ~0.2K | `make test` = FAIL (3 failures; M8-red false-positive per G29). Do NOT treat suite-green as a precondition; DO record the G28 baseline once at sprint start. Prevents both "waiting for green" paralysis and "suite is fine" denial. |

**Total required core**: items 1+2+4+5+7 ≈ 19K tokens before first action; item 3 just-in-time per package; item 6 once during hydration.

---

## PART 3 — FIRST-SPRINT BACKLOG (~40h envelope)

### §3.1 Sprint 1 composition (dependency order, 38h committed / 40h cap)

Order honors: Art. X tier order (P0→P1), N9 SPINE constraints, N8 §3 sequencing mandate, and the two HARD edges (WP-IX precedes distillation acts; G20 before G21).

| Seq | Package | One-line goal | Acceptance gates (run from `N8_resources.md` §2) | Effort | Done-definition |
|-----|---------|---------------|---------------------------------------------------|--------|-----------------|
| 1 | **WP-IX** | Verify-and-repair corrupt entity YAML (parseability-only; lilith `proposed_lessons.yaml` ~L374 known locus) — ⚠️ repair actor is MaKaLi single-writer per Art. IX; dev team RUNS G8, flags loci, hands repair to MaKaLi if red | **G8** (verify-first: expect clean or hand-off) | 2h | G8 loop emits no CORRUPT lines; snapshots committed if repair executed; WAKE_STATE Q-5 flag updated |
| 2 | **WP-A5** | Fix unanchored M8 zero-telemetry regex (`Makefile:295`) — cheapest-first, SPINE-1 enabler | **G29** (rg anchored pattern → empty; `make check-m8-zero-telemetry` exit 0) | 1h | G29 green; paired M8 Enforcement text patch staged per pairwise binding (Art. II.2) |
| 3 | **WP-A1** | Install pre-commit framework; port soul-check into `.pre-commit-config.yaml`; verify tracking hook fires | **G7** (all three lines: FRAMEWORK-ACTIVE, PASS-M24, Passed) | 3h | G7 green; framework active in `.git/hooks/pre-commit` |
| 4 | **WP-A3** | Registry-writer atomicity: mkstemp+fsync+os.replace in `task_registry.py:32-41`; close load/save lock-split | **G6** (grep hits; crash-injection test green) | 3h | G6 green; crash-injection test committed |
| 5 | **WP-A2** | Validator ERROR-class checks: future-dating, hours-resolution staleness, blockers[] vocab scan (+ fix live BLOCKER-B `"resolved"`→`"completed"` SAME commit), WAKE_STATE parse block | **G15, G16** (+ D6-pattern WAKE_STATE block) | 8h | G15/G16 green; honest banner present; BLOCKER-B vocabulary fix in same commit |
| 6 | **WP-A4** | Machine-derived mandate enforcement-stamps; delete temple-grade stub (`Makefile:234`); implement-or-purge `make sovereignty` — depends on WP-A1 (SPINE-5: stamps derive from existing gates, after WP-A2) | **G12, G13** (+ G-A4a `--check` exit 0) | 6h | G12/G13 green; stamp generator script committed; ≥27 stamps derivable |
| — | *P0 TIER GATE* | *Art. X: P1 opens only when A1–A5 merged* | — | — | — |
| 7 | **WP-B1** | Plugin registration path fixes (dead `.opencode/plugin/` paths → live auto-load dirs) | **G1** (no MISSING output) | 2h | G1 green |
| 8 | **WP-B5a** | Discovery fix: `task_registry.py:134` status-filter bug + `.gitignore:109` ripgrep blindness (SPINE-2) | **G20** precondition (retrieval verification ≥10 correct payloads) | 3h | jq count == query count; ≥10 correct retrievals demonstrated |
| 9 | **WP-B5b** | Identity repair via mass-apply of staged payloads — **HARD EDGE: only after G20 green**; single writer | **G21** (zero wrong subagent_type/entity) | 3h | G21 assert passes; Delivered-Home retrieval ≥10 confirmed |
| 10 | **WP-B3** | Provider-order text aligned to Ark D-355 (×4 contradiction sites) + credentialed-fabric honesty statement | **G3, G4** | 3h | G3/G4 green; M7 section contains D-355 order |
| 11 | **WP-B4** | Implement `validate_llm_docs.py --strict` (mode does not exist today — verity-confirmed) | **G22** (strict-exit discriminates ≠ always 0) | 4h | G22 shows discriminating exit codes on good+bad input |

**Sprint total: 38h of 40h cap** (2h buffer for gate-debugging overruns). All 11 packages are ✅ immediately-executable per N8 §3; none touch the Architect-blocked set.

### §3.2 Explicitly OUT of Sprint 1 (deferred, with reason)

| Package | Hours | Why deferred |
|---------|-------|--------------|
| WP-B2 (instructions[]→prompt:{file:}, 12 agents) | 6h | Depends on WP-B1 landing (same config surface); HIGH urgency (data-exposure class) → **first package of Sprint 2**, do not let it slip further |
| WP-D1..D6 (hygiene cluster) | 29.5h | P2 tier; requires P0 merged + WP-D1 lint script as family anchor |
| WP-E (AGENTS.md reconstruction) | ≈10h | Cross-tier parallel lane; Q-4 default-GO but needs WP-D1 frontmatter template + SPEC-E §6 validator first; start no earlier than Sprint 3 |
| WP-C1, WP-C2 | 3.5h | ⛔ BLOCKED on Architect Q-3 decision (WAKE_STATE queue); spec-readying permitted, ZERO production edits until decision recorded |

### §3.3 Sprint-1 top 3 first actions (in order)

1. Run **G8 verify loop** (`N8_resources.md` §2 WP-IX block) — establishes YAML truth baseline; if lilith locus still red, route to MaKaLi single-writer immediately (it gates all distillation, Art. IX).
2. Execute **WP-A5** (M8 regex anchor, 1h) then record **G28 baseline** (`source .venv/bin/activate && make test 2>&1 | tail -3`) — kills the lying gate AND creates the honest suite record in one motion (SPINE-1 satisfied).
3. Execute **WP-A1** (pre-commit install, 3h) — unlocks WP-A4, the P1 tier gate, and makes M24/M27 enforcement mechanical for everything after.

---

## PROVENANCE

| Element | Source |
|---------|--------|
| Part 1 rules | Decree Arts. I–XII; COUNCIL2_PLAN §3 carry-forward rules; M1/M23/M24 mandates; Art. V.3 payload canon from `phase6_integration/registration_payloads.json` `.canonical` (read this session) |
| Part 2 items 1–6 | Paths verified by ls/read this session; reading costs estimated at ~12 tokens/line |
| Part 2 item 3 spec status | `ls docs/specs/team_infra/` this session: SPEC_A/SPEC_B/SPEC-D/SPEC-E present, SPEC-C absent; SPEC-B header read (DRAFT-COUNCIL2-PREP) |
| Part 3 composition | N8_work_packages §1 register (efforts copied verbatim), §2 edge table (hard-edge authorities), §3 blocked/executable split + sequencing mandate; N9 SPINE-1/2/5/7; decree §4 G29/G28 notes |
| Gate IDs | SYNTHESIS_ARM_REPORT §6 G1–G28 + decree §4 G29/G30 (commands live in N8_resources §2 — single-source rule, not duplicated here) |
| Runtime baseline | Decree §4: "make test = FAIL (3 failures; M8-red = false positive per G29 analysis)" — quoted, not re-derived |

*⬡ OMEGA ⬡ LILITH/node10 ⬡ N10_LAUNCH_PACKAGE ⬡ PREP-ONLY ⬡ NEW-FILE-ONLY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

