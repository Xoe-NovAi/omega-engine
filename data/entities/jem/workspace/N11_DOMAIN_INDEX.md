<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N11 Domain Index — Model Quality & Evals
**AP**: AP-N11-DOMAIN-INDEX-v1.0.0 · **last_verified: 2026-08-22** · **Curator**: Jem (N11 evaluator)
**Purpose**: Cold-reader onboarding — wiring diagram, key files, entry points by intent, doc map, known hazards. Passes "5-minute comprehension" test.

---

## Wiring Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        N11 EVAL HARNESS (Quality Axis)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │ Golden Dataset│───▶│ EvalRunner   │───▶│ Local Scorer │───▶│EvalResult│  │
│  │ (111 cases)   │    │ (runner.py)  │    │ (tag-aware)  │    │(check.py)│  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘    └────┬─────┘  │
│                             │                                       │        │
│                    ┌────────▼────────┐                      ┌────────▼────┐  │
│                    │ _score_ragas()  │                      │ EvalChecker │  │
│                    │ [STUB → local]  │                      │ (thresholds)│  │
│                    └─────────────────┘                      └──────┬──────┘  │
│                                                                     │        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │        │
│  │ Calibration   │───▶│ JudgeCalib.  │───▶│ Isotonic Reg.│─────────┘        │
│  │ (golden adv.) │    │ (calibrate.py)│   │ (sklearn)    │   (data/calib/)  │
│  └──────────────┘    └──────────────┘    └──────────────┘   [ABSENT]       │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ Scorecard     │───▶│ AMFOEvaluator│───▶│ Calibrated   │                  │
│  │ (CLEARScore)  │    │ (tiers)      │    │ Judge        │                  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘                  │
│                             │                   │                          │
│                    ┌────────▼────────┐    ┌─────▼─────┐                    │
│                    │ oracle_summon() │    │ llama.cpp │                    │
│                    │ (hardcoded      │    │ server    │                    │
│                    │  entity=lilith) │    │ :8080     │                    │
│                    └─────────────────┘    └───────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      N6 MODELGATE (Inference Serving)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ ModelGateway │  │ Admission    │  │ OOMProtector │  │ Provider     │   │
│  │ (paths/specs)│  │ Controller   │  │ (3-signal)   │  │ Fabric       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       N10 VERIFIER (Gate Integration)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ CI Gate      │  │ Contract     │  │ Test Honesty │                      │
│  │ (pytest hook)│  │ Tests (M21)  │  │ (C-0)        │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘

PARALLEL PERF AXIS (N8 Watchtower):
┌─────────────────────────────────────────────────────────────────────────────┐
│  BenchmarkRunner (src/omega/benchmarks/runner.py)                           │
│  → ttft_ms, tokens_per_sec, peak_ram_mb, quality scores (fail/pass/excellent)│
│  → Consumed by: tests/test_integration_new_systems.py ONLY                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Files Table

| File | Role | Entry Points | Status | Hazards |
|------|------|--------------|--------|---------|
| `src/omega/eval/__init__.py` | Package root | `AP-EVAL-v1.0.0` | LILITH/S2 tagged | RAGAS claim aspirational |
| `src/omega/eval/runner.py` | Golden-dataset runner | `EvalRunner.run()`, `main()` CLI | LILITH/S2 tagged | `make eval` docstring lie; `_score_ragas` stub |
| `src/omega/eval/check.py` | Threshold checker | `EvalResult`, `EvalChecker.check()` | LILITH/S2 tagged | Forward-ref logger; RAGAS heritage tag only |
| `src/omega/eval/calibrate.py` | Isotonic calibration | `JudgeCalibrator.calibrate()`, `main()` CLI | LILITH/S2 tagged | Synthetic labels degenerate; `data/calibration/` absent |
| `src/omega/research/scorecard.py` | CLEARScore/AMFO | `AMFOEvaluator`, `CalibratedJudge` | LILITH/N6-N10 tagged | Hardcoded `entity=lilith`; calibration dir absent |
| `src/omega/research/sediment.py` | SEDA ring-bus (NOT sediment) | `SEDATopic`, `SEDAEvent` | Misnamed file | Filename trap; consumers: hybrid_orchestrator, fleet_status_tui |
| `src/omega/benchmarks/runner.py` | Perf benchmark harness | `BenchmarkRunner.run()` | AP-BENCHMARK-v1.1.0 | Undocumented in strategy; only integration test consumer |
| `src/omega/research/sandboxes/ml_training.py` | Synthetic ML training | `MLTrainingSandbox` | MA'AT/N6 tagged | Soft-default `val_bpb=3.0` masks failure (M23 violation) |
| `tests/test_eval.py` | Contract tests (91 lines) | `pytest` | LILITH/S2 tagged | ONLY consumer of omega.eval |
| `tests/test_scorecard.py` | CLEARScore/AMFO tests | `pytest` | VERITY tagged | `src.omega` imports (breaks wheel installs) |
| `config/eval/thresholds.yaml` | Threshold config | Mirrors check.py defaults | LILITH/S2 tagged | `audience_fit` explicitly non-gated |
| `data/eval/golden_v1.jsonl` | Golden dataset | 111 samples (core/edge/adversarial) | Active | Schema: question/answer/contexts/ground_truth/tags |
| `config/models.yaml` | Model registry | `get_model_path/spec/weight` | **MISSING qwen3-4b-thinking** | D-585 half-implemented |
| `config/providers.yaml` | Provider allowlists | `qwen3-4b-thinking-local` listed | Partial | nemotron-3-ultra-local still listed (D-585 correction unfurled) |
| `opencode.json` | Agent model config | `qwen3-4b-thinking` id present | Partial | ctx 8192 vs models.yaml absent |

---

## Entry Points by Reader Intent

| Intent | Start Here | Then Read |
|--------|------------|-----------|
| "Run an eval" | `python -m omega.eval.runner --help` | `runner.py:405–442` CLI; `data/eval/golden_v1.jsonl` schema |
| "Add a metric" | `check.py:14–32` `EvalResult` dataclass | `runner.py:219–258` `_local_score`; `check.py:38–43` thresholds |
| "Calibrate a judge" | `calibrate.py:138–179` CLI | `calibrate.py:59–100` `JudgeCalibrator.calibrate`; need `data/calibration/` |
| "Wire into CI" | `tests/test_eval.py:50–58` full offline runner pass | N10 verifier charter (gate integration); `make test` |
| "Understand D-585 matrix" | `PIVOT_LOG.md:252–260` | `config/models.yaml` (missing entry), `opencode.json:80`, `providers.yaml:153` |
| "Run benchmarks" | `benchmarks/runner.py:3` AP-BENCHMARK-v1.1.0 | `tests/test_integration_new_systems.py:44–53` usage |
| "Fix model registry" | `model_gateway.py:630–658` `get_model_path` | `models.yaml` keys; N3 buildmaster charter |
| "Debug admission/OOM" | `admission_controller.py:46–96` | `oom_protector.py:4–9,39–50`; systemd `MemoryMax=6G` (D-584) |

---

## Doc Map

| Doc | Location | Relevance |
|-----|----------|-----------|
| N11 Charter | `NODE_EXPERT_SESSIONS_PLAN.md §4` | Constitutional scope |
| W1 Web Research | `NODE_GAP_WEB_RESEARCH_JEM_20260822.md §W1` | lm-eval/promptfoo/ragas verdicts |
| L8 Local Discovery | `NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md §L8` | Inventory + continuation questions |
| D-585 Decision | `PIVOT_LOG.md:252–260` | Canonical matrix ratification |
| C-0 Test Honesty | `PIVOT_LOG.md` (search C-0) | False-count ban, honest badge |
| C-10 Admission Control | `PIVOT_LOG.md` (search C-10) | Semaphore(1) + OOMProtector fusion |
| LI Workstream | `ACTIVE_SPRINT.json` LI-2/LI-4 | Sequential loader + Tier 0 matrix |
| RAGAS Metrics | `docs/research/` (grep ragas) | 11 research docs, no spec |

---

## Known Hazards Register (from 13 Gotchas)

| # | Hazard | File:Line | Severity | Mitigation |
|---|--------|-----------|----------|------------|
| G1 | `make eval` docstring lie | runner.py:9–12 | P1 | Correct docstring OR add `make test-eval` under N10 |
| G2 | `sediment.py` is SEDA bus | sediment.py:1–14 | P2 | Rename or add `# NOT sediment pipeline` banner |
| G3 | RAGAS path is vaporware | runner.py:398–402 | P1 | Rename `_score_ragas_stub` with TODO |
| G4 | Synthetic labels degenerate | calibrate.py:127–134 | P1 | Implement proper adversarial miscalibration simulation |
| G5 | CalibratedJudge never calibrated | scorecard.py:130–136 | P0 | Create `data/calibration/` + run human-label pass |
| G6 | Judge-model naming drift (3 spellings) | opencode.json:80, providers.yaml:153, scorecard.py:47 | P0 | N3 canonicalize; single key in models.yaml |
| G7 | D-585 half-implemented | models.yaml (missing), providers.yaml (nemotron) | P0 | N3 register executor; N6 fold nemotron correction |
| G8 | `config/roles.yaml` absent | — | P2 | Role→model mapping lives in models.yaml `role:` fields |
| G9 | Zero production consumers | grep src/omega_hub/, cli/, Makefile | P0 | N10 wire CI gate; N11 CLI subcommand |
| G10 | Adversarial scoring asymmetry | runner.py:239, 30–41 | P2 | Expand refusal markers; make answer_relevancy dynamic |
| G11 | ml_training soft-default | ml_training.py:264–266 | P1 (M23) | Raise `TrainingFailedError` instead of sentinel 3.0 |
| G12 | Test import schism | test_scorecard.py:8–17 vs test_eval.py:11–13 | P1 | Standardize on `omega.` convention |
| G13 | BenchmarkRunner undocumented | benchmarks/runner.py:3 | P2 | Document as N8 perf harness or fold into N11 |

---

## Cross-Node Contracts

| From N11 | To Node | Contract |
|----------|---------|----------|
| EvalRunner/EvalChecker outputs | N10 Verifier | CI gate consumes verdicts (pytest hook or `make test-eval`) |
| Model names (qwen3-4b-thinking*) | N3 Buildmaster | Single canonical key in models.yaml; aliases in opencode.json/providers.yaml |
| llama.cpp server provisioning | N6 Modelgate | N6 owns serving; N11 provides calibration workload |
| BenchmarkRunner perf data | N8 Watchtower | N8 consumes ttft/throughput/RAM metrics |
| CLEARScore/AMFO outputs | N12 Curator | Corpus quality signals for ingestion prioritization |

---

*End of Domain Index. Cold-reader test: can you explain the wiring diagram in 2 minutes? If yes, index passes.*