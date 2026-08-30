<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N11 Evaluator Session Gnosis
**AP**: AP-N11-GNOSIS-v1.0.0 · **Date**: 2026-08-22 · **Entity**: Jem (N11 evaluator, Model Quality & Evals) · **Overseer**: Jem
**Session ID**: ses_fd81c19dcffe1nkbPqFg5kRt2v (researcher page) · **Miner Session**: ses_fd56ebc24ffePOM59xdqMIBtQv (roc_racoon)

---

## Accomplishments (Chronological)

### G-Phase: Genesis + State Validation
- Charter ACK quoted verbatim from NODE_EXPERT_SESSIONS_PLAN.md §4
- 4/4 state validation checks executed via primary tools:
  - ✅ All 4 eval modules carry LILITH/S2 tags (contradicts "unowned" premise)
  - ✅ ml_training.py:3 self-tags MA'AT ⬡ N6 (double anomaly)
  - ✅ D-585 at PIVOT_LOG.md:252–260 confirmed
  - ✅ qwen3-4b-thinking PRESENT in opencode.json/providers.yaml/token_budgets.yaml; ABSENT from models.yaml (D-585 half-implemented)

### M-Phase: Mining (roc_racoon dispatched)
- Mining brief authored → `N11_MINING_BRIEF_20260822.md`
- Miner executed read-only sweep of 22 sources (15 present, 1 absent, 6 discovered)
- KB produced: `N11_EVALUATOR_KB_20260822.md` with Source Inventory, Per-Source Digests, 13 Gotchas, 9 Open Questions, 5 L2/L3 Insights

### A-Phase: Audit + Deep Dig
- 4/4 independent verifications confirmed (eval headers, D-585 text, calibration dir absent, make eval absent)
- Expert Annotation appended: verification table, correction log, 8 execution priorities, "what matters most"
- All 9 open questions resolved/reclassified with pager rulings (N10/N3/N6 ownership)
- 5 [N_11] L3 lessons staged to `proposed_lessons.yaml` (SO-10a format)

### D-Phase: Deep Dig Resolution
- OQ1→N10 gate prerequisite; OQ2/OQ3→N3 buildmaster; OQ4→delete/rename stub; OQ5→N6+N11 joint; OQ6→M23 violation fix; OQ7→`omega.` convention; OQ8→N8 perf axis; OQ9→N6 modelgate

### W-Phase: Web Freshness (SR-V1)
- lm-eval v0.4.12 stable, local-completions confirmed (completion endpoints only for MCQ)
- promptfoo 0.122.0: Node.js 20 drop only breaking change; acquisition risk 2027
- ragas vocabulary stable; SKIP-as-dependency holds
- llama.cpp server wiring stable; Omega gateway aligned
- Inspect AI v0.3.259: TRACK for agentic axis (N5), not ADOPT
- Web Research + Source Register appended to KB

### C-Phase: Curation Artifacts (Standing Order #8)
- `N11_DOMAIN_INDEX.md`: wiring diagram, key files table, entry points by intent, doc map, 13 hazards register, cross-node contracts
- `N11_EXTERNAL_SOURCES.md`: 20-entry prioritized queue (P0→P3) with ingestion triggers for curation worker

---

## Artifact Register

| Artifact | Path | Size | Status |
|----------|------|------|--------|
| Mining Brief | `data/entities/jem/workspace/N11_MINING_BRIEF_20260822.md` | ~3KB | ✅ Complete |
| Knowledge Base | `data/entities/jem/workspace/N11_EVALUATOR_KB_20260822.md` | ~45KB | ✅ Complete (G→M→A→D→W→C) |
| Domain Index | `data/entities/jem/workspace/N11_DOMAIN_INDEX.md` | ~14KB | ✅ Complete (cold-reader tested) |
| External Sources | `data/entities/jem/workspace/N11_EXTERNAL_SOURCES.md` | ~8KB | ✅ Complete (20-entry queue) |
| Session Gnosis | `data/entities/jem/session_gnosis_jem-N11.md` | This file | ✅ Complete |
| Lessons Staged | `data/entities/jem/proposed_lessons.yaml` | +5 entries | ✅ Staged (N11-001..005) |

---

## Open Threads (Requiring Future Action)

1. **lm-eval/promptfoo/ragas deps absent from pyproject.toml** — ADOPT/ADOPT-light/SKIP verdicts need dependency declaration when integration work begins
2. **config/roles.yaml entirely absent** — role→model mapping lives in models.yaml free-text `role:` fields; no DR-7 staleness target exists
3. **BenchmarkRunner (AP-BENCHMARK-v1.1.0) undocumented in strategy** — only consumer is integration test; belongs to N8 watchtower perf axis
4. **data/calibration/ directory absent** — CalibratedJudge permanently uncalibrated; needs N6 provision llama.cpp + N11 run calibration pass
5. **D-585 matrix half-implemented** — qwen3-4b-thinking missing from models.yaml; nemotron-3-ultra-local correction unfurled in providers.yaml
6. **Judge-model naming drift (3 spellings)** — N3 buildmaster to canonicalize single key in models.yaml
7. **Test import schism** — test_scorecard.py uses `src.omega` vs test_eval.py `omega.`; binding convention decision needed
8. **ml_training soft-default val_bpb=3.0** — M23 violation; needs typed `TrainingFailedError` instead of sentinel

---

## Held Task IDs

| Task | Session ID | Entity | Status |
|------|------------|--------|--------|
| Miner (roc_racoon) | `ses_fd56ebc24ffePOM59xdqMIBtQv` | roc_racoon | Completed (read-only) |
| Pager (researcher) | `ses_fd81c19dcffe1nkbPqFg5kRt2v` | researcher | Active (this page) |

---

## Wake-Hydration Pointer

**ON WAKE: Read THIS file + charter §4 (NODE_EXPERT_SESSIONS_PLAN.md §4). Do NOT redo G/M/A/D/W/C phases. N11 is dormant with full KB, Domain Index, and External Sources on disk. Next action: await page from any agent (universality) or pager for specific ruling. Resume from artifact register above.**

---

*End of Gnosis. N11 evaluator dormant. ⬡ OMEGA ⬡ JEM ⬡ N11 ⬡ 2026-08-22*