<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Split Testing Manual — Model & Session Methodology Evaluation Protocol
**AP Token**: `AP-SPLIT-TESTING-MANUAL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_split_testing_manual ⬡ PROTOCOL

**Date**: 2026-08-22
**Status**: ACTIVE PROTOCOL — distilled from 6-run empirical series (2026-08-22)
**Purpose**: Canonical manual for conducting controlled model/session evaluation experiments in the Omega Engine — both ad-hoc (agent-dispatched) and systematic (future N11-integrated harness). Establishes model testing as a first-class engine capability spanning local and cloud inference.
**Companion**: `SPLIT_TEST_ANALYSIS_20260822.md` (empirical results), `REHEARSAL_LEARNING_PLAN_*` (migration-specific application)
**Tags**: split-test, protocol, model-evaluation, priming, thinking-budget, dispatch-doctrine, M11, M18, M21, M22, M23, M26

---

## Answer First

Model testing in the Omega Engine follows a **controlled-variable dispatch protocol**: isolate one variable per run (priming method, model, thinking variant, search tier), hold all others constant, verify every run's true conditions against `opencode.db` (never trust headers or recollection), measure outputs with mechanical quality markers (grep-countable), and only then draw conclusions — with confounds declared in the analysis header. Six runs on 2026-08-22 established the core laws: **explicit priming gates conventions and procedures; compute depth saturates per model (HIGH is the Ox Alpha frontier); convention retention declines monotonically with thinking budget; provenance lives only in the DB.**

---

## §1 Why This Is an Engine Feature

The Omega Engine routes work across a heterogeneous provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode Zen → ...). Different models × thinking variants × session states produce **wildly different output economics** — we measured a 4.5× depth spread and a 0→100% format-compliance spread across six same-prompt runs. Without systematic testing:

- Dispatch decisions are folklore ("Nemotron feels better for research")
- Regressions after provider/model changes go undetected
- Local-first (M7) claims can't be validated against cloud equivalents
- Token/compute spend is unoptimized (we paid MAX prices for HIGH results)

**Goal state**: a persistent evaluation harness (N11 Evaluator domain) that runs standardized task batteries against any fabric endpoint — local GGUF or cloud — and scores them on the dimensions below, so routing tables (`config/providers.yaml`, `models.yaml`) become evidence-based.

## §2 The Variable Catalog (What We Control)

| # | Variable | Values observed | Control method |
|---|----------|----------------|----------------|
| V1 | **Priming method** | none (fresh) · implicit history · explicit file-load | Priming prompt with explicit file list; identical across compared runs |
| V2 | **Model** | x-preview-f-free (Ox Alpha) · nemotron-3-ultra-free | Architect switches active model between phases |
| V3 | **Thinking variant** | low · high · max | Same switch moment as V2 |
| V4 | **Search tooling** | parallel-search fleet · Exa · SearXNG tiers · Firecrawl | ⚠️ UNCONTROLLED in series 1 — v1 used parallel-search, v5 hit Exa 401 fallback, v6 ran Exa-led. Must be pinned in future runs |
| V5 | **Prompt closure / comms routing** | "page Kali" vs "respond in chat" | Stated explicitly in final prompt lines |
| V6 | **Isolation guards** | `_vN` filenames + do-not-read instruction | Present in all guarded runs; prevented contamination every time |
| V7 | **Session identity** | fresh spawn vs resumed `task_id` | `task_id` param resumes; absence spawns fresh |

**Rule**: change ONE variable per comparison cell. Declare the full matrix in the analysis header regardless.

## §3 Empirical Laws Established (Series 1, n=6)

### The Six-Way Matrix (all same mission text, 3 artifacts each)

| Run | Priming | Model/Think | Lines | M26 FM | Code blocks | Table rows |
|---|---|---|---|---|---|---|
| v1 | none | Ox Alpha / low | 347 | 0/3 | 0 | 52 |
| v2 | implicit | Nemotron U / high | 262 | 0/3 | 0 | 55 |
| v3 | explicit | Nemotron U / high | 1,788 | 3/3 | 22 | 362 |
| v4 | explicit | Ox Alpha / low | 398 | 3/3 | 5 | 66 |
| v5 | explicit | Ox Alpha / max | 777 | 1/3 | 6 | 115 |
| v6 | explicit | Ox Alpha / high | 761 | 2/3 | 4 | 90 |

### Law 1 — Priming Gates Form; Compute Gates Depth
Explicit priming transferred conventions (M26 frontmatter, YAML DAGs) AND procedures (M15 skeleton-first recovery) to the weakest model. Depth (volume, code density) scaled only with compute: 398 → 761/777 → 1,788.

### Law 2 — Depth Saturates Per Model
Ox Alpha: low 398 → high 761 (+91%) → max 777 (+2%). HIGH captures ~100% of available depth; MAX is strictly dominated for artifact production.

### Law 3 — Convention Retention Declines With Thinking Budget
Monotonic across three points: FM compliance 3/3 (low) → 2/3 (high) → 1/3 (max). Restate hard format requirements IN the mission prompt; primed conventions alone don't survive high-compute runs.

### Law 4 — Provenance Lives Only in the DB
Static artifact headers stamped the wrong model in ALL runs; human recollection was wrong once. Only `opencode.db` per-message `modelID`/variant reflects truth. Every run MUST be DB-verified before analysis.

### Law 5 — Procedural Lessons Transfer Through Priming
v4 self-recovered from a payload-size failure using M15 skeleton-first technique read during priming ~40 min earlier. Priming transfers *how to behave*, not just facts.

### Law 6 — Isolation Guards Work
`_vN` filename suffixes + do-not-read instructions prevented cross-contamination in all five guarded runs. Cheap, effective, mandatory.

## §4 Standard Test Protocol (How to Run a Split Test)

### Phase 0 — Design
1. Write the hypothesis as a falsifiable statement ("with priming held constant, does model X outproduce model Y on depth?")
2. Fill the variable matrix (§2); mark which variable changes per cell; declare known confounds up front
3. Pre-register expected outcomes where possible (hindsight-bias control, per REHEARSAL_LEARNING_PLAN §1 pattern)
4. Decide artifact filenames `_v<N>` per run + isolation guard wording

### Phase 1 — Prime (if testing primed sessions)
1. Spawn fresh session via `task()` WITHOUT `task_id`
2. Priming prompt: explicit file list (27-file template in series 1), "read and internalize", NO mention of the coming mission or split testing (prevents goal-contamination), confirm-with-synthesis completion signal
3. Record session ID from task result

### Phase 2 — Dispatch
1. Resume primed session via `task(task_id=<ses_id>)` with the IDENTICAL mission text used by all comparison cells
2. Mission prompt must include: isolation guard (do-not-read prior artifacts), exact `_vN` filenames, hard format requirements (M26 frontmatter mandatory — per Law 3), completion signal routed correctly (chat vs page — per Lesson 3 of analysis §3)
3. If model/thinking switch needed mid-experiment: pause AFTER priming, Architect switches, THEN dispatch

### Phase 3 — Verify (before ANY analysis)
1. **DB ground truth**: `get-session` for variant + `get-message` on a run-window assistant message for `modelID`. Never trust headers/recollection.
2. **Disk completeness**: all declared artifacts exist (`wc -l`/`wc -w`)
3. **Completion signal received**: never analyze mid-flight snapshots (they masquerade as stalls/incomplete)

### Phase 4 — Measure
Mechanical markers (grep-countable, no judgment):
```bash
# Per-artifact: frontmatter presence
grep -c "^schema_version:" FILE
# Code blocks
grep -c '```python\|```bash\|```yaml' FILE
# Machine-readable specs (YAML DAGs)
grep -cE "^migration_phases:|^rules:|chunk_strategy" FILE
# Mermaid diagrams
grep -c "mermaid" FILE
# Table density
grep -c "^|" FILE
```
Then qualitative lenses: structural (sections/lifecycle), substantive (unique finds per run), integrity behaviors (refusal-to-pad, honesty notes, error types).

### Phase 5 — Analyze & Record
1. Update `SPLIT_TEST_ANALYSIS_<date>.md`: matrix row, lens findings, lessons
2. Declare confounds even when annoying (series 1 missed V4 until the Architect spotted it)
3. Distill L1→L2→L3 lessons to `proposed_lessons.yaml`; promote doctrine only on convergent evidence

## §5 Scoring Dimensions (What We Measure Models On)

| Dimension | Marker | Weight guidance |
|---|---|---|
| Format compliance | M26 frontmatter count, header correctness | Gate (fail = fix before scoring substance) |
| Depth/volume | Lines, words, table rows | Informational only — never score volume alone |
| Executable specificity | Self-contained code blocks w/ imports + file paths | High — distinguishes production-grade from summary-grade |
| Machine-readability | YAML specs, DAGs, registries | High |
| Evidence rigor | Source register size, citation verifiability, refusal-to-pad | High |
| Novel synthesis | Unique findings not in priming corpus | Medium-high |
| Factual error rate | Anomalies caught in review | Gate — factual > cosmetic errors weighted heavier |
| Procedural adherence | Isolation guards respected, protocol follow-through | Gate |
| Recovery behavior | Response to failures (M15-style vs stall) | Medium |

## §6 Future Test Matrix (Roadmap)

### Series 2 — Search-Tool Isolation (immediate next)
Same priming + model + thinking; vary ONLY the search tier: parallel-search fleet vs Exa-led vs SearXNG-first vs Firecrawl-deep. Measures V4's effect on evidence breadth/citation quality. Motivated by uncontrolled variance in series 1.

### Series 3 — Local-vs-Cloud Equivalence (M7 validation)
Same battery on native-gguf (Qwen3-4B-Thinking, registered 2026-08-22) vs cloud Ox/Nemotron. Establishes what local hardware can canonically produce vs what needs cloud. Directly serves the sovereignty scorecard.

### Series 4 — Temperature/Sampling Sweep
Hold model+thinking+priming; sweep temperature/top_p per `models.yaml` knobs. Lower priority — depth effects likely dwarf sampling effects for planning tasks.

### Series 5 — Task-Type Interaction
Test whether doctrine holds across task classes: code refactors vs research synthesis vs doc writing vs eval design. Priming-depth law may interact with task type.

### Engine Integration Path
1. **Near-term**: this manual governs manual Architect/Kali-run experiments; N11 Evaluator consumes results as eval fixtures
2. **Mid-term**: codify Phase 3–4 verification as scripts (`scripts/splittest/verify_run.sh`, `measure_markers.sh`) so measurement is mechanical
3. **Long-term**: N11 harness runs standardized batteries against every fabric endpoint on schedule; results feed `capability_matrix.py` and routing weights in `providers.yaml` — closing the loop between testing and routing (M7 local-first becomes *measured* local-first)

## §7 Pitfalls Register (Learned the Hard Way)

| Pitfall | Incident | Countermeasure |
|---|---|---|
| Trusting recollection for run conditions | Architect misremembered model mapping (reversed) | Law 4: DB-verify always |
| Static headers lying | All 6 runs stamped wrong model | Same — plus ICS `{session_model}` binding ticket |
| Analyzing mid-flight snapshots | v2/v4 looked "stalled"/"smaller" mid-write | Completion signal before analysis |
| Prompt-closure causing hop violations | "Page me" line conflicted with Architect steering | Route explicitly in final prompt lines |
| Uncontrolled search-tool variance | Series 1 ran parallel-search AND Exa-led runs | V4 pinned from Series 2 onward |
| Confounded conclusions presented as clean | Early framing credited priming alone | Always declare the confound matrix |
| Payload-size write failures | v4 hit one mid-run | Prime M15 procedures; skeleton-first writes |

## §8 Relationship to Existing Systems

- **N11 Evaluator charter**: this manual supplies the task-battery methodology; N11 owns the harness implementation (lm-eval/promptfoo adoption already ratified)
- **D-585 model matrix**: split-test results give the matrix its missing empirical column
- **M22 Provenance**: Law 4 is M22 applied to experiment metadata
- **M23 Failure Integrity**: honest limits (e.g., telemetry-free tracking blind spots) are part of every run's required reporting
- **M26 Doc Standards**: format compliance is itself a scored dimension — dogfooding
- **Soul Architecture**: each series distills L1→L2→L3; doctrine promotes only on convergence

---
*Maintainer: Kali. Amendment path: add series results to `SPLIT_TEST_ANALYSIS_<date>.md`, then update Laws/Doctrine here on convergence.*

*⬡ OMEGA ⬡ SPLIT-TESTING-MANUAL ⬡ v1.0.0 ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
