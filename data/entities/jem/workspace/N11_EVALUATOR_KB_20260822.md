<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N11 Evaluator Knowledge Base — Model Quality & Evals
**AP**: AP-N11-MINING-v1.0.0 · **last_verified: 2026-08-22**
**Curator**: Jem (N11) · **Miner**: roc_racoon (read-only mining per `data/entities/jem/workspace/N11_MINING_BRIEF_20260822.md`)
**Scope**: every eval/benchmark/experiment-harness asset in the repo; interfaces, wiring surfaces, constraints, gaps. Every claim cites `file:line`. Absent sources marked ABSENT with the probe used.

## Source Inventory

| Path | Status | Priority | Role |
|------|--------|----------|------|
| `src/omega/eval/__init__.py` | PRESENT | P0 | Package init; self-describes "Sovereign Eval Pipeline: RAGAS + calibrated LLM-as-Judge (S2)" (`__init__.py:4`) |
| `src/omega/eval/runner.py` | PRESENT | P0 | Golden-dataset eval runner; local deterministic scorer + optional RAGAS flag; CLI entry |
| `src/omega/eval/check.py` | PRESENT | P0 | `EvalResult` dataclass + threshold checker (`EvalChecker`) |
| `src/omega/eval/calibrate.py` | PRESENT | P0 | Isotonic-regression judge calibration; CLI entry |
| `tests/test_eval.py` | PRESENT | P0 | Contract tests for all three eval modules (91 lines) |
| `src/omega/research/sandboxes/ml_training.py` | PRESENT | P0 | ONLY sandbox module; synthetic ML training → val_bpb for CLEARScore |
| `docs/decisions/PIVOT_LOG.md` D-585 | PRESENT | P0 | Canonical model matrix ratification (lines 252–260) |
| `tests/test_scorecard.py` | PRESENT | P0 | CLEARScore/AMFO contract tests (uses `src.`-prefixed imports) |
| `tests/test_integration_new_systems.py` | PRESENT | P0 | BenchmarkRunner usage at :44–53 |
| `data/entities/researcher/workspace/NODE_GAP_WEB_RESEARCH_JEM_20260822.md` §W1 | PRESENT | P0 | External SOTA verdicts: lm-eval ADOPT, promptfoo ADOPT-light, RAGAS SKIP-as-dep (:367–385) |
| `data/entities/roc_racoon/workspace/NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md` §L8 | PRESENT | P0 | Local inventory seeds + Continuation-1 questions (:310–335) |
| `config/roles.yaml` | **ABSENT** | P1 | Probe: `ls config/roles.yaml` empty + `find . -maxdepth 3 -name roles.yaml` no hits. DR-7 staleness check impossible — nothing to be stale |
| `pyproject.toml` | PRESENT | P1 | NO `lm-eval`, `promptfoo`, `ragas`, `scikit`, `joblib`, `sklearn` anywhere (full-file grep, 0 hits); deps list `pyproject.toml:11–41+` |
| `src/omega/oracle/model_gateway.py` | PRESENT | P1 | Wiring surface: `get_model_path`:630, `get_model_spec`:661, llama.cpp server URL :114/:700 |
| `config/providers.yaml` native-gguf | PRESENT | P1 | `qwen3-4b-thinking-local` in supported_models at :153, :174, :195 (native-gguf/lmster/ollama blocks) |
| `config/models.yaml` | PRESENT | P1 | CONFIRMED: no `qwen3-4b-thinking` key (keys: qwen3-1.7b:5, qwen3-1.7b-q6_k:19, qwen3-4b:32, frontier, mimo-7b-rl-q4_k_m, rocracoon-3b×2) |
| OOM/admission control | PRESENT | P1 | `admission_controller.py` Semaphore(1)+OOMProtector fusion (:46–96); `oom_protector.py` 3-signal PSI/MemAvailable/zram |
| Scorecard/sediment pipeline | PRESENT | P1 | `src/omega/research/scorecard.py` (CLEAR-Pareto + AMFO); `sediment.py` is a MISNOMER (see G2) |
| `src/omega/benchmarks/{runner,schema,comprehensive_runner}.py` | PRESENT | P0† | †Discovered beyond brief: perf benchmark harness (AP-BENCHMARK-v1.1.0), consumed by integration test |
| Docs mentioning ragas/lm-eval/promptfoo | PRESENT | P2 | 11 non-archive docs (list in Digest §15); research docs only, no spec |
| `data/coordination/ACTIVE_SPRINT.json` LI workstream | PRESENT | P2 | LI-4 "Tier 0 model matrix: Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B" status ready (:347–352) |

## Per-Source Digests

### 1. `src/omega/eval/__init__.py`
- Header: `⬡ OMEGA ⬡ LILITH ⬡ eval ⬡ S2` (`__init__.py:3`). AP-EVAL-v1.0.0 (`:2`).
- Docstring claims "RAGAS + calibrated LLM-as-Judge" (`:4`) — RAGAS part is aspirational (see G3).

### 2. `src/omega/eval/check.py`
- Header: `⬡ OMEGA ⬡ LILITH ⬡ eval.check ⬡ S2` (`check.py:3`); `[heritage: ragas-2024]` metric-vocabulary tag (`:6`).
- `EvalResult` dataclass (`:14–32`): faithfulness, answer_relevancy, context_precision, context_recall, audience_fit (default 1.0), passed, n_samples, per_sample, details. Docstring cross-links audience_fit to S7 register verification (`:18–21`).
- `EvalChecker.DEFAULT_THRESHOLDS` (`:38–43`): faithfulness 0.85, answer_relevancy 0.80, context_precision 0.75, context_recall 0.80.
- `check()` returns False if any metric missing or below threshold (`:50–59`); missing metric logs warning via module-level `logger_missing` defined *below* the class (`:71–74`) — works at runtime but is a forward-reference style smell.
- `failing_metrics()` lists sub-threshold metrics (`:61–68`).

### 3. `src/omega/eval/calibrate.py`
- Header: `⬡ OMEGA ⬡ LILITH ⬡ eval.calibrate ⬡ S2` (`calibrate.py:3`); `[heritage: calibration-curves-2026]` (`:6`).
- Embedded empirical claim: uncalibrated 7–13B judges overconfident by ~0.18 ECE in 0.8–0.95 band; isotonic regression reduces ECE 0.18→0.06; min judge Mistral 7B Q4_K_M, recommended Qwen3:14b Q4_K_M (`:8–10`).
- `_ece()` computes Expected Calibration Error, 10 bins (`:24–43`).
- `JudgeCalibrator.calibrate(judgments, human_labels, output_path)` (`:59–100`): lazy sklearn import (`:75`), lazy joblib import (`:85`), saves `{isotonic, ece_before, ece_after}` pickle. `apply(model_path, score)` static method (`:102–109`).
- `_synthetic_labels()` (`:112–135`): generates pseudo judge scores from golden dataset tags. **Degenerate**: both adversarial and non-adversarial branches append label 1 with raw scores 0.80–0.97 (`:127–133`) — the docstring's claimed miscalibration simulation is not actually implemented differently per branch (see G4).
- CLI `main()` (`:138–179`): defaults `--dataset data/eval/golden_v1.jsonl` (`:140`), `--output config/eval/calibrated_model.pkl` (`:141`), optional `--human-labels` JSON file (`:142–144`).

### 4. `src/omega/eval/runner.py`
- Header: `⬡ OMEGA ⬡ LILITH ⬡ eval.runner ⬡ S2` (`runner.py:3`); `[heritage: ragas-2024]` (`:6–7`).
- M7/M23 banner claims graceful degradation so "`make eval` is sovereign-offline and never soft-fails" (`:9–12`) — **but Makefile has no `eval` target** (probe: `grep -E "^[a-z-]+:" Makefile` lists test*/lint/doc targets only; zero eval entries). See G1.
- Public API: `EvalRunner(dataset_path, judge_model="mistral:7b", thresholds_path=None, audience_profile=None, use_ragas=False)` (`:261–277`); `async run() -> EvalResult` (`:344–396`); module `main()` argparse CLI (`:405–442`, exits 1 on fail `:437–440`).
- Local scorer `_local_score(sample)` (`:219–258`): tag-aware. core/edge → faithfulness = smoothed-recall(answer vs ground_truth), answer_relevancy = overlap(answer vs question); adversarial → refusal-marker match gives faithfulness 1.0 else 0.3, answer_relevancy fixed 0.8 (`:235–239`). No contexts → neutral context_precision/recall 0.9 (`:248–251`).
- `_smoothed_recall(reference, candidate, alpha=0.25)` (`:201–216`): recall-style, not Jaccard; long correct answers not penalized.
- `_REFUSAL_MARKERS` tuple of 10 strings (`:30–41`); large stopword set incl. injection-instruction words ("ignore","bypass","exfiltrate", etc., `:45–185`) so instruction verbs don't pollute overlap.
- Audience fit (`:302–329`): imports `omega.oracle.audience_calibrator.AudienceCalibrator` (`:307`); keyword-marker heuristic (+0.25 per matched tone/technical marker, base 0.5); advisory-only, broad except returns 1.0 (`:327–329`).
- RAGAS path: `_ragas_available()` checks `use_ragas` flag then importability (`:332–341`); **`_score_ragas()` is a placeholder that just calls `_local_score`** (`:398–402`). The RAGAS integration does not exist yet — see G3.
- Dataset loader skips malformed JSONL lines with a warning (`:289–292`); raises FileNotFoundError if dataset absent (`:281–282`).

### 5. `tests/test_eval.py`
- Header `⬡ OMEGA ⬡ LILITH ⬡ test_eval ⬡ S2` (`test_eval.py:3`); imports all three modules (`:11–13`) — this is currently the ONLY consumer of `omega.eval` besides itself (probe: `grep -rn "from omega.eval\|import omega.eval" src/ tests/ scripts/ Makefile` → only `tests/test_eval.py:11–13`; no CLI command, no omega_hub tool references it).
- Enforces golden dataset ≥100 cases (`:19–22`); actual `data/eval/golden_v1.jsonl` = 111 lines (wc -l).
- Exercises: local scorer core + adversarial-refusal paths (`:25–38`), checker thresholds (`:41–47`), full offline runner pass on golden set (`:50–58`), advisory audience-fit (`:61–65`), calibrator ECE reduction + apply round-trip (`:68–81`), ECE math edge cases incl. empty input (`:84–91`).

### 6. `src/omega/research/sandboxes/ml_training.py`
- Sole member of `sandboxes/` (ls: only ml_training.py + __pycache__).
- Header: `⬡ OMEGA ⬡ MA'AT ⬡ N6 ⬡ ML_TRAINING` (`ml_training.py:3`); AP-MAAT-ML-SANDBOX-v1.0.0 (`:4`); mandate compliance block M1/M2/M7/M9/M12/M13/M21/M23 (`:9–17`).
- Purpose: trains small model (BGE-small 33M or synthetic) measuring `val_bpb`, "returns metrics for CLEARScore integration" (`:6–7`).
- `MLTrainingSandbox(SandboxRuntime)`, `spec_name = "ml_training"` (`:32–44`); experiment spec keys model_type/dataset_size/epochs/learning_rate/eval_metric (`:36–42`).
- Generates an inline training script as a string literal (`:50–200`): numpy logistic-regression via mini-batch SGD; `val_bpb ≈ cross_entropy / ln(2)` (`:142–150`). `model_type="bge_small"` is a placeholder returning hardcoded metrics + `"bge_small not implemented in sandbox"` note (`:181–189`).
- Execution: `anyio.run_process([sys.executable, script], env=…)` (`:227–233`) — M1 compliant; writes only to its sandbox workspace (`:207–208`).
- `_parse_metrics` parses last JSON line of stdout; regex fallback on stderr (`:237–262`); injects default `val_bpb=3.0` when absent (`:264–266`) — a soft-default that could mask training failure (borderline M23 tension; recorded as OQ6).
- Style note: `os`/`sys` imported at bottom of file (`:272–273`) — legal (module-level executes before methods run) but fragile.

### 7. `src/omega/research/scorecard.py` (scorecard pipeline)
- Header: `⬡ OMEGA ⬡ LILITH ⬡ N6-N10 ⬡ SCORECARD` (`scorecard.py:3`).
- `AMFO_TIERS` (`:28–50`): scout(qwen3-0.6b, 60s, low) → validate(qwen3-1.7b, 300s, medium) → synthesize(qwen3-4b-thinking-q4_k_m, 1800s, high).
- Judge config constants (`:52–55`): `CALIBRATED_JUDGE_MODEL="qwen3-4b-thinking-q4_k_m"`; paths `data/calibration/judge_calibration.json` and `data/calibration/isotonic_regressor.pkl`. **`data/calibration/` directory ABSENT** (probe: ls fails) → `CalibratedJudge._load_calibration()` silently finds nothing and runs uncalibrated forever (`:128–136`). See G5.
- `CalibratedJudge.evaluate(hypothesis, evidence, criteria, oracle_summon)` (`:158–205`): builds JSON-only judge prompt (`:207–223`), parses scores with fallback to 0.5 heuristics on parse failure (`:189–191`), inverts cost dimension (`:196–198`), returns `(CLEARScore, provider_name)` for M22 (`:168`).
- `AMFOEvaluator` (`:226–301`): tiered fidelity with early-stop heuristic `local_first_ratio>0.8 AND epistemic_rigor>0.7` (`:270–278`); budget overrun break at 1.5× tier budget (`:280–282`); timeout/error tiers return sentinel CLEARScore(1.0,0,…,0) with provider "timeout"/"error" (`:334–359`).
- Oracle adapter `oracle_summon(model, prompt)` (`:440–460`): imports `omega_hub.omega_hub_oracle_summon`, **hardcodes `entity_name="lilith"`** (`:447`) — see G6.

### 8. `sediment.py` — misnomer alert
- `src/omega/research/sediment.py` contains **SEDA — Sovereign Engine Data Access ring-bus** (AnyIO memory-object-stream pub/sub; header `sediment.py:1–14`; `[id-soft: vet-045]` LMAX Disruptor inspiration `:12–16`). It is NOT a sediment/score-decay pipeline.
- Consumers: `src/omega/oracle/planner/hybrid_orchestrator.py:554,595` imports `SEDATopic, SEDAEvent` from it; `src/omega/cli/fleet_status_tui.py:38`.
- Brief's grep hint "grep `sediment` across src/" therefore resolves to bus plumbing, not an eval artifact. There is NO separate sediment pipeline in src/ (only stale .pyc artifacts named test_sediment).

### 9. `src/omega/benchmarks/` (discovered beyond brief)
- `runner.py`: AP-BENCHMARK-v1.1.0 (`runner.py:3`); integrates ObservabilityEngine (`:4`); 3-point quality scale fail/pass/excellent per Galtea/EMNLP 2025 (`:7`); per-criterion scoring Accuracy/Adherence/Conciseness/Structure (`:9`); position randomization for pairwise comparisons (`:11`); calibration-loop requirement for judge prompts (`:12`).
- `BenchmarkResult` dataclass (`:44–62`): ttft_ms, tokens_per_sec, peak_ram_mb, scores dict, avg_quality_score, factuality_rate.
- `DATA_DIR/BENCH_DIR` under repo `data/benchmarks` (`:39–40`).
- Consumer: `tests/test_integration_new_systems.py:44–53` — `BenchmarkRunner().run("qwen3-1.7b", "p7_context", samples=5)` persisted + listable; hardware profile prerequisite (`:56–59`). No other consumer found (grep across src/, omega_hub: none).

### 10. `docs/decisions/PIVOT_LOG.md` D-585
- Index row: "D-585 Canonical model matrix = Carmack version (Qwen3-4B/4B-Thinking/1.7B) ✅ RATIFIED" (`PIVOT_LOG.md:28`).
- Full entry at `PIVOT_LOG.md:252–260`: matrix = Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic; Grokster's competing matrix superseded; ownership Kali coordinates / Ma'at implements; canonical home `config/providers.yaml` + `opencode.json`; known correction to fold in: `nemotron-3-ultra-local` registry entry wrong (Nemotron 3 Ultra is cloud-only) (`:255`).
- Context: resolved HOP-3 relay Q4; two competing matrices existed; Architect ruled 2026-08-21 (`:256–257`). Mandates M27, M22 (`:258`).
- Other eval-related decisions: grep `eval|benchmark|RAGAS|lm-eval|promptfoo` over PIVOT_LOG hits only `:340` (N11/N12/N13 charter mention) — D-585 is the sole eval-relevant decision.

### 11. D-585 implementation status across configs
| Surface | Status | Evidence |
|---|---|---|
| `opencode.json` (lmstudio provider models) | ✅ has `qwen3-4b-thinking` id, ctx 8192/out 4096 | `opencode.json:80–87`; also qwen3-1.7b `:88–95`, qwen3-1.7b-q6_k `:96–103` |
| `config/providers.yaml` supported_models | ✅ `qwen3-4b-thinking-local` listed on native-gguf(:153), lmster(:174), ollama(:195) | but these are name allowlists, not specs |
| `config/models.yaml` | ❌ NO `qwen3-4b-thinking` entry (confirmed; nearest is `qwen3-4b` via lmster at `models.yaml:32–38` with role "Ma'at/Lilith synthesis") | consequence: `ModelGateway.get_model_path("qwen3-4b-thinking")` → None (`model_gateway.py:630–658`) |
| nemotron correction | ❌ NOT folded in: `nemotron-3-ultra-local` still in all three supported_models lists (`providers.yaml:150,171,192`) | contradicts D-585 correction clause |

### 12. Provider fabric wiring surface (for lm-eval `local-completions`)
- `ModelGateway.LLAMA_CPP_URL = "http://127.0.0.1:8080"` (`model_gateway.py:114`); health check `_check_llama_cpp()` probes `127.0.0.1:8080/health` (`:700+`). This is the natural target for lm-eval's `local-completions` backend (OpenAI-compatible; W1 verdict confirms compatibility).
- `get_model_path(name)` resolves `env:` prefixes (e.g. `env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf`) and returns None when unmapped (`model_gateway.py:630–658`); `get_model_spec(name)` returns raw models.yaml dict (`:661–662`); `get_model_weight` reads ram_mb, default 1024MB (`:664–673`).
- `config/models.yaml` carries context budgets + sampling params per model (e.g. qwen3-1.7b: budget 15000, window 8192, ram 2048MB — `models.yaml:5–17`); KV-cache quant config consumed by gateway (`model_gateway.py:620–627`); sampling_overrides section for stability floors (gemma-4-31b forced logit bias, tail of models.yaml).
- Native-gguf provider block: priority 0, max_concurrent 1, n_threads 4, numa disable (`providers.yaml:143–160`).

### 13. CPU/OOM/admission constraints bounding a benchmark run
- `LocalInferenceAdmission` (`admission_controller.py:46–96`): enforces **max 1 concurrent local inference** via `anyio.Semaphore(1)` (`:51`); acquire() = OOMProtector fail-fast check THEN semaphore (`:56–89`); required_gb = (model_ram_mb + kv_cache_mb)/1024 with defaults 1700+512MB (`:56,68`); busy slot refuses rather than queues (`:79–85`).
- `OOMProtector` (`oom_protector.py`): three-signal fusion — PSI pressure, MemAvailable (/proc/meminfo), zram (`:4–9,39–50`); DENY_OOM_RISK hard floor when MemAvailable < reserve (`:33,87`); THROTTLE when MemAvailable < 4GB (`:92`).
- Gateway integration: admission token acquired around local inference and released after completion (`model_gateway.py:1251–1259,1424–1426`).
- systemd ceilings: inference services pattern `MemoryMax=8G + Delegate=yes` (`config/domains/engineering/PLAYBOOK.md:145`); zswap architecture locked by D-584 (zswap 25% pool + 16GB NVMe swap, zRAM disabled, swappiness=100, cgroup MemoryMax=6G — `PIVOT_LOG.md:240–250`).
- Implication for N11: any benchmark sweep is strictly serial per model load; batch parallelism must come from within one loaded model, not concurrent loads.

### 14. Node-gap source digests
- Researcher §W1 (`NODE_GAP_WEB_RESEARCH_JEM_20260822.md:367–385`): lm-eval-harness v0.4.12 ADOPT (model-selection axis; `local-completions` speaks OpenAI-compatible → llama.cpp server; CPU-feasible subsets can validate D-585 matrix); promptfoo ADOPT-light (dual-duty prompt regression + N5 agentic-security red-team); DeepEval TRACK; RAGAS SKIP-as-dependency because check.py already implements the vocabulary natively (`:377–379`); complementarity ruling: homegrown owns application-quality axis, gaps are model-selection + adversarial axes (`:383–384`).
- Roc §L8 (`NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md:310–321`): inventory table matching this KB's findings; flags ml_training self-tag N6 orphaning (`:320–321`). Continuation-1 questions include L5: qwen3-4b-thinking used by AFFINITY_PRESETS + D-585 but absent from models.yaml — register or correct matrix? (`:327`).

### 15. P2 skims
- ACTIVE_SPRINT LI workstream: LI-4 "Tier 0 model matrix: Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B", owner maat_n3, status ready (`ACTIVE_SPRINT.json:347–352`); LI-2 SequentialModelLoader "one model at a time" (`:341–346`) — aligns with admission Semaphore(1).
- Docs mentioning ragas/lm-eval/promptfoo (non-archive, grep -l): docs/intake/WEB-GEMINI_Research-Bridge-Implementation-Plan.md; docs/research/R_JEM_DEEP_RESEARCH_CURRENT_CONCERNS_20260713.md; R_RESEARCHER_COMPREHENSIVE_STATUS_REPORT_20260713.md; R_JEM_MAKALI_DEEP_RESEARCH_20260712.md; R_EPOCH_II_LEGACY_MINING_20260712.md; R_ROC_RACCOON_LEGACY_MINING_20260713.md; R_RESEARCHER_NEXTSTEP_GAPS_20260713.md; R_RESEARCH_GAPS_20260724.md; R_EPOCH_II_DEEP_RESEARCH_20260712.md; R_CONTEXT_PACKER_V3_RESEARCH_SYNTHESIS_20260808.md; R_RESEARCHER_MANDATORY_WEB_20260713.md. All are research/discussion docs — no formal eval spec exists.
- Supporting config assets: `config/eval/thresholds.yaml` (S2 LILITH header `:1–4`; mirrors check.py defaults; audience_fit explicitly non-gated `:8`); `data/eval/golden_v1.jsonl` 111 samples (sample schema: question/answer/contexts/ground_truth/tags — first line); `data/eval/golden_mimo_v1.jsonl` 31 samples; `data/eval/golden/` dir exists (empty listing).
- `tests/test_scorecard.py`: VERITY-tagged contract tests (`test_scorecard.py:1–3`); covers CLEARScore creation/vector/dominance, proposal status machine, AMFO tier structure/budget monotonicity, judge calibrate/passthrough, evaluator run (`:30–256`). NOTE: uses `from src.omega.…` prefixed imports (`:8–17`) unlike test_eval.py's installed-package imports — inconsistent, likely breaks under wheel installs (OQ7).

## Gotchas

1. **`make eval` doesn't exist.** runner.py:9–12 promises sovereign-offline behavior "so `make eval` is sovereign-offline"; Makefile target list (grep `^[a-z-]+:`) contains no eval target. The eval pipeline is reachable only via `python -m omega.eval.runner` or pytest.
2. **`sediment.py` is not sediment.** File contains SEDA ring-bus (sediment.py:1–14); consumers hybrid_orchestrator.py:554,595 + fleet_status_tui.py:38 import SEDA symbols from it. Any "sediment pipeline" premise is false; filename is a trap for future miners.
3. **RAGAS path is vaporware.** `_score_ragas()` unconditionally delegates to `_local_score` (runner.py:398–402); package docstring and headers advertise "RAGAS + calibrated LLM-as-Judge" (__init__.py:4). RAGAS is vocabulary-only today (consistent with W1 SKIP ruling, but the code comment implies a live path).
4. **Synthetic calibration labels are degenerate.** `_synthetic_labels` appends label 1 and high raw score in BOTH branches (calibrate.py:127–134); the docstring's overconfidence simulation (miscalibrated adversarial branch) isn't implemented. Demo ECE numbers are structurally inflated-by-construction, not measured.
5. **CalibratedJudge can never be calibrated.** scorecard.py:54–55 points at `data/calibration/*` which does not exist (ls ABSENT); `_load_calibration` swallows the miss (scorecard.py:130–136) → silent permanent uncalibrated fallback, contradicting its own M17/M21 framing.
6. **Judge-model naming drift.** Three different identifiers for the same intended model: `qwen3-4b-thinking` (opencode.json:80–81), `qwen3-4b-thinking-local` (providers.yaml:153), `qwen3-4b-thinking-q4_k_m` (scorecard.py:47,53) — and NONE is a key in models.yaml, so gateway resolution fails for all three spellings.
7. **D-585 half-implemented.** Matrix ratified (PIVOT_LOG.md:252–260) but executor model absent from models.yaml and the mandated nemotron-registry correction not applied (nemotron-3-ultra-local still listed providers.yaml:150,171,192 despite being declared cloud-only).
8. **`config/roles.yaml` ABSENT entirely** (ls + find probes empty) — the brief's DR-7 staleness question has no target; any role→model mapping lives elsewhere (models.yaml `role:` free-text fields, e.g. models.yaml:15,36).
9. **No production consumer of eval outputs.** Only tests/test_eval.py imports omega.eval; no CLI subcommand, no MCP hub tool, no CI gate wires EvalRunner/EvalChecker/BenchmarkRunner into any gate (greps over src/omega_hub/, cli/, Makefile: zero hits).
10. **Adversarial scoring asymmetry.** In _local_score, adversarial samples get fixed answer_relevancy 0.8 (runner.py:239) and refusal detection is substring-based on 10 markers (runner.py:30–41) — a refusal phrased outside those markers scores faithfulness 0.3 regardless of correctness.
11. **ml_training soft-default masks failure.** Missing val_bpb is replaced with 3.0 "poor score" (ml_training.py:264–266) — downstream CLEARScore comparisons can't distinguish crashed runs from bad runs.
12. **Test import schism.** test_scorecard.py uses `from src.omega.…` (test_scorecard.py:8–17) while test_eval.py uses `from omega.eval…` (test_eval.py:11–13) — two import conventions in the same suite; the src.-style breaks under installed-package contexts.
13. **Benchmarks module is undocumented in strategy.** src/omega/benchmarks/ (AP-BENCHMARK-v1.1.0, runner.py:3) exists with quality-scale methodology (runner.py:7–12) but appears in no strategy doc surfaced by the brief's greps; only discovery path was the integration test.

## Open Questions

1. Should `make eval` be created to honor runner.py:9–12's stated contract, or should the docstring be corrected? (Pager/Jem ruling needed.)
2. Register `qwen3-4b-thinking` in config/models.yaml (with which context_budget/ram_mb?), or amend D-585 first? Mirrors Roc L5 continuation question (NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md:327).
3. Which single canonical spelling wins for the thinking model (`qwen3-4b-thinking` vs `-local` vs `-q4_k_m`), and who aliases the rest?
4. Is the placeholder `_score_ragas` (runner.py:398–402) slated for real implementation post-lm-eval adoption, or should it be deleted/renamed to avoid implying capability?
5. Who owns creating `data/calibration/` and running a real human-label calibration pass (calibrate.py --human-labels) so CalibratedJudge stops falling back silently?
6. Does the val_bpb=3.0 soft-default (ml_training.py:264–266) violate M23 Failure Integrity, or is it acceptable as a sentinel? Needs explicit terminal-failure state instead?
7. Standardize test imports (`src.omega` vs `omega`) — which convention is binding under the current install layout?
8. Should BenchmarkRunner (perf axis) be folded into N11's charter alongside quality-axis eval, or does it belong to another Node (it measures ttft/throughput/RAM, not answer quality)?
9. ml_training.py self-tags MA'AT ⬡ N6 (ml_training.py:3) while scorecard self-tags LILITH ⬡ N6-N10 (scorecard.py:3) and eval modules tag LILITH ⬡ S2 — who is the rightful owner of eval infrastructure for charter purposes?

## L2/L3 Insights

### [N11] Insight 1 — Vocabulary ≠ Framework
- narrative: The eval modules carry `[heritage: ragas-2024]` tags and RAGAS metric names, but the RAGAS library is neither imported as a dependency nor actually invoked; `_score_ragas` just re-runs the local scorer (runner.py:398–402), and pyproject.toml declares no eval deps.
- insight: Omega implemented RAGAS as a *metric vocabulary* (four named floats + thresholds) rather than a framework dependency — deliberately, per W1's SKIP-as-dependency ruling (NODE_GAP_WEB_RESEARCH_JEM_20260822.md:377–379) — but the code comments still narrate the framework as if present.
- principle: Adopt a standard's *contract* before adopting its *code*; naming drift between documentation and implementation is where audits rot. [N11]

### [N11] Insight 2 — Ratified matrices decay at the config layer
- narrative: D-585 ratified the Carmack model matrix on 2026-08-21 (PIVOT_LOG.md:252–260), yet one day later the executor model exists in opencode.json:80 and providers.yaml allowlists but not in models.yaml, and the mandated nemotron correction is unfurled.
- insight: Decisions propagate top-down through multiple config surfaces (decision log → opencode.json → providers.yaml → models.yaml), and each hop is a manual edit with no validator tying them together; partial propagation is invisible until a resolution call returns None.
- principle: A decision is only as ratified as its least-updated config surface; SSOTs need mechanical propagation checks, not memory. [N11]

### [N11] Insight 3 — Silent fallbacks invert safety machinery
- narrative: Three separate components degrade silently: CalibratedJudge runs uncalibrated forever when data/calibration/ is missing (scorecard.py:130–136), ml_training fabricates val_bpb=3.0 on parse failure (ml_training.py:264–266), and audience_fit swallows all exceptions to return 1.0 (runner.py:327–329).
- insight: Each fallback is individually defensible (availability over fragility), but stacked together they mean every eval number could be produced by a degraded path with zero signal that degradation occurred — the opposite of M22 provenance.
- principle: Graceful degradation without a degradation marker is indistinguishable from success; every fallback must stamp its output. [N11]

### [N11] Insight 4 — Serial admission is the benchmark budget
- narrative: Local inference is gated by Semaphore(1) plus OOMProtector three-signal fusion (admission_controller.py:46–96), models carry explicit ram_mb budgets in models.yaml, and LI-2 plans a sequential one-model-at-a-time loader (ACTIVE_SPRINT.json:341–346).
- insight: On this 14Gi-class host, benchmark throughput is bounded not by tokens/sec but by model-load serialization: any N11 harness design that assumes parallel model evaluation is architecturally invalid here.
- principle: Design benchmarks for the constraint you have (serial swap cost), not the cluster you wish for. [N11]

### [N11] Insight 5 — Unconsumed pipelines are demos, not systems
- narrative: The entire eval stack — EvalRunner, EvalChecker, JudgeCalibrator, BenchmarkRunner — has exactly one consumer class: tests (test_eval.py:11–13, test_integration_new_systems.py:44–53). No CLI command, MCP tool, or CI gate reads their outputs.
- insight: Code with correct internals but zero external callers provides no quality guarantee; the "eval pipeline" currently proves the pipeline works, not that the engine is good.
- principle: An eval system earns its keep at the moment a gate consumes its verdict; until wired, it is rehearsal. [N11]

---
## N11 Expert Annotation — A+D Phase (2026-08-22)

### Independent Verification Record (≥3 highest-stakes claims)

| Claim | Source | Probe | Result | Evidence |
|-------|--------|-------|--------|----------|
| All 4 eval modules carry LILITH/S2 ownership tags | KB §1–4 headers | `head -5 src/omega/eval/{__init__,check,calibrate,runner}.py` | **CONFIRMED** | All four: `⬡ OMEGA ⬡ LILITH ⬡ eval* ⬡ S2` |
| D-585 matrix exact claims | KB §10 | `sed -n '252,260p' docs/decisions/PIVOT_LOG.md` | **CONFIRMED** | Carmack matrix ratified; nemotron correction mandated |
| `data/calibration/` directory absent | KB §8 (G5) | `ls data/calibration/` | **CONFIRMED ABSENT** | `ls: cannot access... No such file or directory` |
| `make eval` target nonexistent | KB §4 (G1) | `grep -E "^[a-z-]+:" Makefile` | **CONFIRMED** | Only test*/lint/doc targets; zero eval entries |

### Correction Log
- KB §11 table: `config/models.yaml` key list — `qwen3-4b` at line 32 is via `lmster` provider (not native-gguf); corrected in annotation.
- KB §13: `MemoryMax=8G` for inference services is from `config/domains/engineering/PLAYBOOK.md:145`; cgroup `MemoryMax=6G` is from D-584 zswap architecture (PIVOT_LOG.md:240–250) — both cited, distinct scopes.

### Execution Priorities (N11 charter scope)
1. **P0**: Wire eval outputs into a CI gate (N10 verifier owns gate integration per pager ruling #1) — currently zero consumers.
2. **P0**: Resolve model-name canonicalization (N3 buildmaster owns registry per pager ruling #2) — three spellings, zero models.yaml entry.
3. **P0**: Decide eval-infra ownership (N6 modelgate owns inference serving contracts per pager ruling #3) — LILITH/S2 vs MA'AT/N6 tag conflict.
4. **P1**: Create `make eval` target OR correct runner.py:9–12 docstring (Jem ruling needed — OQ1).
5. **P1**: Delete/rename `_score_ragas` placeholder or implement via lm-eval adoption (OQ4).
6. **P1**: Establish `data/calibration/` + run human-label pass so CalibratedJudge stops silent fallback (OQ5).
7. **P2**: Standardize test imports (`src.omega` vs `omega`) — binding convention decision (OQ7).
8. **P2**: Document BenchmarkRunner as perf-axis sibling or fold into N11 charter (OQ8).

### What Matters Most
The eval stack is **internally coherent but externally disconnected** — every module passes its contract tests, the golden dataset is 111 cases, the local scorer is tag-aware and adversarial-hardened, the calibration math is sound — but no gate consumes its verdicts. Until N10 wires a gate, N11 proves the pipeline works, not that the engine is good (Insight 5). The D-585 matrix decay (Insight 2) and silent fallbacks (Insight 3) are the two systemic rot vectors; both are mechanical, not intellectual.

---

## Deep Dig — Open Questions Resolved/Reclassified

### OQ1: `make eval` target — **RECLASSIFIED → N10 gate integration prerequisite**
Not a standalone Makefile target. The eval pipeline should be invoked by N10's CI gate (pytest hook or dedicated `make test-eval` under N10 ownership). Runner.py:9–12 docstring should be corrected to reference the actual invocation path (`python -m omega.eval.runner` or pytest).

### OQ2: Register qwen3-4b-thinking in models.yaml — **DELEGATED → N3 buildmaster (pager ruling #2)**
N3 owns the model registry. Required fields: context_budget (32768 per token_budgets.yaml:76), provider (lmster per D-585 executor role), ram_mb (~6144 estimated), context_window (8192 native / 32768 YaRN). N3 to decide quantization key (-q4_k_m vs -local vs base).

### OQ3: Canonical spelling — **DELEGATED → N3 buildmaster (pager ruling #2)**
Single canonical key in models.yaml; opencode.json and providers.yaml allowlists become aliases. N3 to publish the canonical spelling and alias map.

### OQ4: `_score_ragas` placeholder — **RESOLVED → DELETE/RENAME post-lm-eval adoption**
W1 ruling: RAGAS SKIP-as-dependency; lm-eval ADOPT provides model-selection axis. The placeholder should be renamed `_score_ragas_stub` with a `# TODO: wire via lm-eval local-completions backend` comment, or deleted until lm-eval integration lands. Current state implies capability that doesn't exist.

### OQ5: `data/calibration/` + human-label pass — **DELEGATED → N6 modelgate (pager ruling #3) + N11**
N6 owns inference serving; N11 owns eval logic. Joint action: N6 provisions llama.cpp server for calibration runs; N11 runs `python -m omega.eval.calibrate --human-labels <file>` on golden adversarial subset. Output to `data/calibration/` (create dir). Without this, CalibratedJudge is permanently uncalibrated theater.

### OQ6: val_bpb=3.0 soft-default — **RESOLVED → VIOLATES M23; replace with explicit failure state**
M23 Failure Integrity: "No soft-failures or simulated rigor." The soft-default masks training crashes as "poor scores." Fix: `_parse_metrics` should raise `TrainingFailedError` (new typed exception per M9) when val_bpb absent; downstream CLEARScore comparison must handle explicit failure, not sentinel values.

### OQ7: Test import schism — **RESOLVED → `omega.` convention binding; `src.omega` breaks wheel installs**
`test_eval.py` uses `from omega.eval...` (installed-package style); `test_scorecard.py` uses `from src.omega...` (editable-source style). The repo installs via `pip install -e .` → `omega` package is on sys.path. `src.omega` imports only work in editable mode. **Binding convention: `omega.` everywhere.** `test_scorecard.py` imports must be fixed.

### OQ8: BenchmarkRunner charter placement — **RESOLVED → N11 owns quality-axis; perf-axis stays separate (or N8 watchtower)**
BenchmarkRunner measures ttft/throughput/RAM (perf), not answer quality. N11 charter = "model-output evaluation & benchmarking" — but the *quality* axis (faithfulness, relevance, etc.) is N11; perf axis belongs to N8 watchtower (observability/metrics) or a dedicated perf Node. Recommendation: N11 keeps quality eval; BenchmarkRunner documented as N8-consumed perf harness.

### OQ9: Eval-infra ownership (LILITH/S2 vs MA'AT/N6) — **RULED → N6 modelgate (pager ruling #3)**
N6 owns inference serving contracts (provider fabric, admission, OOMProtector). Eval modules tag LILITH/S2 because Lilith curates N6–N10 nodes, but the *serving infrastructure* (llama.cpp server, model gateway, admission controller) is N6's domain. The ml_training sandbox self-tagging MA'AT ⬡ N6 is a separate anomaly (Ma'at entity on Lilith's Node) — flagged for N6/Lilith reconciliation.

---

---

## Web Research — Freshness Pass (2026-08-22, SR-V1)

### 1. lm-eval-harness
- **Current version**: v0.4.12 (PyPI/Zenodo, released 2026-05-11) — **matches W1 ADOPT target exactly**.
- **v0.5.0.dev1 pre-release** exists (PyPI, 2026-05-11) — unstable, not for production.
- **`local-completions` backend**: CONFIRMED stable. API guide (EleutherAI/lm-evaluation-harness/blob/main/docs/API_guide.md) documents `TemplateAPI` → `LocalCompletionsAPI` → `OpenAICompletionsAPI` chain. Requires OpenAI-compatible `/v1/completions` endpoint. **Loglikelihood/MCQ tasks only supported on completion endpoints, NOT chat-completion endpoints** — critical for D-585 matrix (Qwen3-4B-Thinking executor must expose completions, not chat).
- **CLI refactored** (2025-12): subcommands `run`/`ls`/`validate`, YAML config via `--config`.
- **Lighter install**: base package no longer bundles `transformers`/`torch`; backends via extras: `lm_eval[hf]`, `lm_eval[vllm]`, `lm_eval[openai]`.
- **Verdict**: v0.4.12 is current stable; `local-completions` wiring pattern is documented and stable; no breaking changes since W1 ruling.

### 2. promptfoo
- **Current version**: 0.122.0 (GitHub releases, 2026-08-04) — **18 days old**.
- **Breaking change**: **dropped Node.js 20 support** (requires Node.js 22+). This is the ONLY breaking change in 0.122.0.
- **Security fix**: Shai-Hulud compromised dependency versions blocked (#10301).
- **Streaming fix**: WebSocket evals no longer hang on stream stalls (#10266) — relevant for M25 streaming resilience.
- **OpenAI acquisition**: Announced March 2026, not closed as of Aug 2026. MIT license unchanged; Community tier fully functional. Long-term roadmap neutrality uncertain — monitor GitHub commit velocity.
- **Verdict**: ADOPT-light still valid. Node.js 20 drop is a build-time concern only (Omega uses Python); no API breaking changes. Acquisition risk is 2027 horizon.

### 3. ragas
- **Metric vocabulary**: STABLE. Core RAG metrics (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Context Entities Recall, Noise Sensitivity, Response Relevancy) unchanged since v0.2 (Dec 2025). Nvidia metrics (Answer Accuracy, Context Relevance, Response Groundedness) and Agent metrics (Agentic/Tool Use, Topic Adherence, Tool Call Accuracy/F1, Agent Goal Accuracy) added as extensions, not replacements.
- **Omega usage**: check.py implements the four core RAG metrics as vocabulary (faithfulness, answer_relevancy, context_precision, context_recall) — **no version lock risk**.
- **Verdict**: SKIP-as-dependency remains correct; vocabulary stable; no upgrade pressure.

### 4. llama.cpp server (OpenAI-compatible)
- **Official `llama-server`** (ggml-org/llama.cpp): `--port` (default 8080), `--host`, `--ctx-size`, `--n-gpu-layers`, `--jinja`/`--no-jinja` for tool calling. Endpoints: `/v1/chat/completions`, `/v1/completions`, `/v1/models`, `/health`. **Persistent KV cache** across requests (single global Llama instance).
- **Community wrapper** (odellus/llama-oai-server): FastAPI-based, single-threaded, persistent KV cache, huge context (120K+), streaming SSE, function calling, `/v1/chat/completions` + `/v1/completions` + `/health`. Config via env vars (`MODEL_PATH`, `N_CTX`, `PORT`, etc.).
- **Unsloth deployment guide**: `llama-server --model <gguf> --ctx-size 16384 --port 8001 --jinja` → OpenAI client at `http://127.0.0.1:8001/v1` with dummy API key.
- **Critical for N11**: lm-eval `local-completions` expects `/v1/completions` (NOT `/v1/chat/completions`) for loglikelihood/MCQ tasks. Omega's `ModelGateway.LLAMA_CPP_URL = "http://127.0.0.1:8080"` (model_gateway.py:114) + health check at `/health` (model_gateway.py:700+) aligns with official llama-server defaults.
- **Verdict**: Wiring pattern is stable and documented. Omega's gateway already targets the correct endpoint. No changes needed for lm-eval integration.

### 5. New eval frameworks (Inspect, Helicone, etc.)
- **Inspect AI** (UK AI Security Institute): v0.3.259 (PyPI, 2026-08-16) — **actively maintained, weekly releases**. MIT license. Built-in components: prompt engineering, tool usage, multi-turn dialog, model-graded evals, sandboxed code execution. 50+ contributors. Evals library includes GAIA, SWE-Bench, GDM CTF, Cybench. **Relevance to D-585**: Inspect is a *framework competitor* to lm-eval, not a complement. It uses its own model abstraction (supports OpenAI/Anthropic/Google/HF). Could replace lm-eval for agentic evals but adds dependency. **Verdict**: TRACK — not ADOPT. lm-eval remains correct for model-selection axis; Inspect for agentic/safety axis (N5 sentinel domain).
- **Helicone**: Acquired by Mintlify (March 2026). Drop-in proxy for observability (change base URL). Traces at API-call level, not agent-execution level. **Verdict**: NOT relevant to N11 eval harness; belongs to N8 watchtower observability stack.
- **OpenAI Evals / HELM**: Mentioned as related tools in AISI directory. No new adoption signal for Omega.

---

## Source Register (for future curation worker)

| # | Source | Type | Priority | Why | Target Format |
|---|--------|------|----------|-----|---------------|
| 1 | EleutherAI/lm-evaluation-harness (GitHub) | Repo | P0 | Primary upstream for ADOPT tool; API guide, model backends, task registry | Markdown mirror of docs/ + API guide |
| 2 | promptfoo/promptfoo (GitHub) | Repo | P0 | ADOPT-light; red-team plugins, provider matrix, CI integration patterns | Markdown mirror of docs/ + releases |
| 3 | ragas (GitHub/shahules786/ragas) | Repo | P1 | Metric vocabulary source; track v0.3+ for new metrics | Markdown mirror of concepts/metrics |
| 4 | ggml-org/llama.cpp (GitHub) | Repo | P0 | llama-server binary; OpenAI-compatible endpoints, KV cache, tool calling | Markdown mirror of tools/server/README.md |
| 5 | UKGovernmentBEIS/inspect_ai (GitHub) | Repo | P1 | Agentic eval framework; safety benchmarks (GAIA, SWE-Bench) | Markdown mirror of docs/ + evals listing |
| 6 | D-585 Canonical Model Matrix (PIVOT_LOG.md:252–260) | Decision | P0 | N11's constitutional matrix; must propagate to all config surfaces | YAML (models.yaml) + JSON (opencode.json) |
| 7 | RAGAS Metrics Paper (arXiv:2309.15217 / 2402.06416) | Paper | P2 | Theoretical grounding for faithfulness/answer_relevancy/context_precision/recall | PDF → Markdown summary |
| 8 | lm-eval v0.4.12 Release Notes (Zenodo 10.5281/zenodo.20122284) | Release | P1 | Exact feature set of ADOPT version | Markdown summary |
| 9 | promptfoo 0.122.0 Release Notes (GitHub) | Release | P1 | Node.js 20 drop, streaming fix, security patches | Markdown summary |
| 10 | llama.cpp Server Deployment (Unsloth guide) | Guide | P1 | Production wiring patterns for local-completions backend | Markdown mirror |

---

*End of KB. Miner: roc_racoon · Expert: Jem (N11) · AP-N11-MINING-v1.0.0 · W+C complete 2026-08-22.*
