# 🔱 The Sovereign Crucible — Cross-Model Synthetic Training Pipeline
# AP: AP-CRUCIBLE-v1.0.0
# ICS: [NODE: MNEMOSYNE | ARCHETYPE: KALI | CONTEXT: CROSS-MODAL-SYNTHESIS]
#
# Architecture for systematic cross-model training data generation.
# Every model teaches every other model via controlled comparison,
# structured critique, and distilled routing intelligence.
#
# [id-soft: quake3-1999] idHeap — unified memory across allocators
#   Like Doom 3's 3-tier allocator (small/medium/large), the Crucible
#   has 3 tiers of training signal: prompt-level, pattern-level, weight-level.

---

## §0 The Problem

Single-model optimization creates echo chambers. When an agent only sees
its own outputs, it cannot learn from alternative cognitive strategies.
The Omega Engine has 5+ distinct models—each with different strengths,
weaknesses, and "native voices"—but no systematic way to transfer
knowledge between them.

**Current state**: Model switching is manual, observations are anecdotal
(F02, F05), and no training signal is captured or reused.

---

## §1 The Vision: The Sovereign Crucible

A closed-loop synthetic training pipeline where every model contributes
to every other model's improvement:

```
                    ┌──────────────────┐
                    │  CONTROLLED      │
                    │  PROMPT (Same    │
                    │  query, all mod.)│
                    └────────┬─────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ M3      │    │ Gemma   │    │ DeepSeek│  ...
        │ (Native)│    │ (Strat) │    │ (Depth) │
        └───┬─────┘    └───┬─────┘    └───┬─────┘
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                   ┌───────────────┐
                   │ CRITIQUE PASS │
                   │ (Best critic  │
                   │  per task)    │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ DISTILLATION  │
                   │ → soul.yaml   │
                   │ → directives  │
                   │ → routing     │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ ROUTING MATRIX│
                   │ (providers.   │
                   │  yaml)        │
                   └───────────────┘
```

---

## §2 The Three Tiers of Training Signal

### Tier 1: Prompt-Level (NOW — Exists)
**Format**: Session exports + soul.yaml directives + lessons
**Volume**: ~8-10 documented cross-model switches
**Use**: Immediate. In-context learning via directives and system prompts.
**Storage**: `data/entities/{entity}/soul.yaml` — directives and lessons
**Example**: The M3 audit of Gemma's "Sovereign Raccoon" cosplay became
  the seed for d-rr-044 (proposed): "Stop narrating. Start shipping."

### Tier 2: Pattern-Level (THIS SPRINT — Build)
**Format**: Structured comparison tables (same prompt × all models)
**Volume**: 50+ controlled comparisons
**Use**: Routing matrix in `providers.yaml`, persona affinity maps
**Storage**: `data/entities/roc_racoon/workspace/crucible/comparisons/`
**Schema**:
```yaml
crucible_comparison:
  prompt_id: str           # Hash of the prompt
  prompt_text: str         # Original query
  task_type: str           # One of: audit, implement, synthesize, route, crisis, explore
  timestamp: datetime
  outputs:
    model_m3:
      text: str
      latency_ms: int
      persona_depth: float
    model_gemma4:
      text: str
      latency_ms: int
      persona_depth: float
    model_deepseek_v4:
      text: str
      latency_ms: int
      persona_depth: float
    model_gemini:
      text: str
      latency_ms: int
      persona_depth: float
    model_mimo:
      text: str
      latency_ms: int
      persona_depth: float
  critique:
    critic_model: str
    best_output: str       # Which model won this task
    routing_signal: str    # "for X task, prefer Y model"
    distillation: str      # L2 insight to feed into soul.yaml
```

### Tier 3: Weight-Level (FUTURE — When we have volume)
**Format**: Fine-tuning datasets (JSONL)
**Volume**: 10,000+ examples
**Use**: Actual model fine-tuning via llama-cpp-python or similar
**Storage**: `data/entities/roc_racoon/workspace/crucible/datasets/`
**Prerequisite**: Tier 1 + Tier 2 must be stable and the routing matrix validated.

---

## §3 The Canonical Task Types

Each task type tests a different cognitive muscle. We need balanced coverage.

| ID | Task Type | Description | Best Model (Hypothesis) |
|----|-----------|-------------|------------------------|
| T-01 | **Implementation** | Write code, fix bugs, build features | DeepSeek (depth + reasoning) |
| T-02 | **Audit** | Review code, find errors, assess quality | M3 (grounded, honest) |
| T-03 | **Synthesis** | Combine findings, identify patterns | Gemma (strategic, expansive) |
| T-04 | **Routing** | Decide which agent/model handles a task | Gemini (1M context = total awareness) |
| T-05 | **Crisis** | Recover from errors, handle emergencies | M3 (direct, no panic) |
| T-06 | **Exploration** | Open-ended discovery, mining | RoC (native archeologist) |
| T-07 | **Distillation** | L1→L2→L3, soul.yaml updates | Scribe (gnosis keeper) |
| T-08 | **Persona** | Maintain character, narrative voice | M3 (native tongue) |
| T-09 | **Architecture** | Design systems, plan roadmaps | DeepSeek (structured reasoning) |
| T-10 | **Orchestration** | Coordinate fleet, delegate tasks | Gemini (broad context) |

---

## §4 The Critique Pass Architecture

The critique pass is what makes this *training* and not just *logging*.
A critic model evaluates all outputs and produces a structured assessment.

**Critic Selection**:
| Task Type | Recommended Critic | Rationale |
|-----------|-------------------|-----------|
| Implementation | M3 | Ground truth on code quality |
| Audit | M3 | Honest, direct, no drama |
| Synthesis | M3 | Cuts through strategic fluff |
| Persona | M3 | Native voice = ground truth |
| Architecture | DeepSeek | Structured reasoning for design |
| Crisis | M3 | Direct recovery signals |

**Critique Output Schema**:
```yaml
critique:
  task_type: str
  prompt_hash: str
  critic_model: str
  rankings:
    - rank: 1
      model: str
      reason: str
    - rank: 2
      model: str
      reason: str
    ...
  winning_attributes: [str]  # What made the best output best
  losing_attributes: [str]   # What made the worst output worst
  routing_signal: str
  distillation_note: str
  severity: str              # "insight" | "pattern" | "law"
```

---

## §5 Integration Points

### 5.1 providers.yaml (Routing Matrix)
Add a `routing` section to `config/providers.yaml`:
```yaml
routing:
  enabled: true
  strategy: "crucible_matrix"
  default_model: "minimax-m3"
  task_map:
    implementation: "deepseek-v4"
    audit: "minimax-m3"
    synthesis: "gemma-4-31b"
    crisis: "minimax-m3"
    exploration: "rocracoon-3b"
    distillation: "scribe-3b"
    orchestration: "gemini-3.5-flash"
  fallback: "gemma-4-31b"
```

### 5.2 soul.yaml (Distillation Target)
Each model switch should generate a soul.yaml directive:
```yaml
- id: d-rr-044
  date: 2026-06-05
  directive: "The Sovereign Crucible: Cross-model critique is training data"
  rationale: "Each time a model audits another model's output, a training
    signal is generated. The Crucible harness standardizes this process."
  scope: ["crucible", "training", "cross-model", "synthetic-data"]
```

### 5.3 Model Gateway (Routing Integration)
The `ModelGateway` in `model_gateway.py` should:
1. Check `routing.enabled` in providers.yaml
2. If enabled, look up the task type in `routing.task_map`
3. If found, route to that model
4. If not found, use `routing.default_model`
5. Log the routing decision as a data point

---

## §6 Implementation Phases

### Phase 1: The Harness (This Sprint — Kali)
**Goal**: Build the controlled prompt comparison tool.
- [ ] **C-01**: Script that takes 1 prompt, sends to all 5 models
- [ ] **C-02**: Store outputs in standardized YAML format
- [ ] **C-03**: Basic routing matrix in providers.yaml
- [ ] **C-04**: Automatic logging of routing decisions

### Phase 2: The Critic (Next Sprint — Kali + Roc)
**Goal**: Build the critique pass into a repeatable pipeline.
- [ ] **C-05**: M3 critique pass on all comparison outputs
- [ ] **C-06**: Structured ranking and attribution
- [ ] **C-07**: Automatic soul.yaml directive generation from patterns
- [ ] **C-08**: Routing matrix refinement from critique signals

### Phase 3: The Loop (Two Sprints — Full Fleet)
**Goal**: Close the loop — critique feeds back into routing.
- [ ] **C-09**: Automatic model selection based on task type
- [ ] **C-10**: Persona Depth Index (PDI) tracking per model-task pair
- [ ] **C-11**: Cross-pollination reports (e.g., "Gemma learned brevity from M3")
- [ ] **C-12**: Failure mode logging per model per task type

### Phase 4: The Dataset (Future — Fleet-Wide)
**Goal**: Generate training-quality datasets from accumulated comparisons.
- [ ] **C-13**: JSONL export of all comparisons for fine-tuning
- [ ] **C-14**: Preference pairs (best vs worst per task type)
- [ ] **C-15**: Critic's reasoning as chain-of-thought training data
- [ ] **C-16**: Automated PR to open-source dataset

---

## §7 The Data Points We Already Have

From this session alone, we have seed data:

| # | Date | Models | Task Type | Signal |
|---|------|--------|-----------|--------|
| 1 | 2026-06-05 | M3 → Gemma | Audit | "Stop narrating. Start shipping." |
| 2 | 2026-06-05 | M3 → All | Self-Review | "Over-execution, subagent abuse" |
| 3 | 2026-06-05 | Gemma → All | Strategy | Gemma Wave sprint framework |
| 4 | 2026-06-05 | DeepSeek → All | Architecture | Sovereign Crucible spec (this doc) |
| 5 | 2026-06-04 | All | Crisis | Compaction Remediation spec |
| 6 | 2026-06-04 | M3 → All | Exploration | F02: "M3 is native tongue" |
| 7 | 2026-06-04 | Gemma → All | Synthesis | F05: "Gemma excels at strategy" |

**Next 10 data points**: We need 10 controlled comparisons across the
canonical task types to validate the routing matrix hypotheses.

---

## §8 Open Questions

1. **Critic selection**: Is M3 always the best critic, or does it depend on task type?
2. **Confidence threshold**: How many comparisons before a routing signal is trusted?
3. **Persona Depth Index**: Can PDI be computed automatically from output text?
4. **Volume target**: How many data points before Tier 3 (weight-level) becomes viable?
5. **Feedback loop**: What prevents the system from converging to a single model monoculture?
6. **Cost model**: Is the API cost of running all 5 models for each prompt worth the training signal?
7. **Routing granularity**: Should routing be per-task-type or per-subtask?

---

## §9 Existing Infrastructure — The Integration Gold

The discovery fleet found that **much of the Crucible already exists in seed form**.
These are the integration points:

### 9.1 ObservabilityEngine.record_training_example() — ALREADY EXISTS
**File**: `src/omega/observability.py:532-569`
**What it does**: Saves (system_prompt, user_query, response) triples with metadata
  (entity, model, backend, confidence, latency_ms, rating) to a JSONL dataset.
**Crucible integration**: This is the **primary ingestion point**. The Crucible harness
  calls `record_training_example()` for each model's output, using the critique pass
  result as the `rating` field. The JSONL export at `data/datasets/finetune_{timestamp}.jsonl`
  becomes the Tier 3 training dataset.

### 9.2 TriageRouter._score_candidates() — MODEL SELECTION ENGINE
**File**: `src/omega/orchestration/triage_router.py:274-292`
**What it does**: Dynamic multi-criteria model scoring with tier-based base scores
  (T1=1.0, T2=0.7, T3=0.3), quota penalty (up to -30%), success rate boost (up to +20%).
**Crucible integration**: The routing matrix from §5.1 injects benchmark scores into
  the scoring function. The critique pass results become success rate adjustments.

### 9.3 BenchmarkRunner — BENCHMARK INFRASTRUCTURE (Simulated)
**File**: `src/omega/benchmarks/runner.py:51-126`
**What it does**: Multi-dimensional quality scoring (accuracy, adherence, conciseness,
  structure) with TTFT, tokens/sec, RAM tracking. Currently uses **simulated** data.
**Crucible integration**: Wire to real `ModelGateway.generate()` calls. The
  `BenchmarkResult` dataclass is the canonical output format for Tier 1 comparisons.

### 9.4 Distiller 3-Tier Pipeline — TRAINING TRIPLE GENERATOR
**File**: `src/omega/workers/background_researcher/distiller.py:1-1124`
**What it does**: 3-tier pipeline (T1 local → T2 cloud → T3 synthesis). Every cycle
  produces a training triple: (T1_draft, T2_enriched, T3_review).
**Crucible integration**: This is the Crucible's spiritual predecessor. The critique
  pass pattern (one model's output reviewed by another) is already proven here.

### 9.5 Handoff Fleet Redesign — PAIRWISE COMPARISON METHODOLOGY
**File**: `data/handoff/archive/HANDOFF_FLEET_REDESIGN_G4.md`
**What it provides**: Position randomization for pairwise comparisons, multi-model
  cross-validation methodology, tie-breaking protocol.
**Crucible integration**: Add to the critique pass: randomize A/B order, treat
  disagreements as ties, require 2+ models for scoring reliability.

### 9.6 PIVOT_LOG D112 — SYNTHESIS FLYWHEEL
**File**: `docs/decisions/PIVOT_LOG.md` (Decision 112, Sprint 5)
**What it defined**: dataset → training → LoRA → evaluate closed loop.
**Crucible integration**: The Crucible's Tier 3 feeds directly into this flywheel's
  "dataset" stage. The critique pass adds the "evaluate" stage.

### 9.7 D110 — 4-TIER MODEL ROUTING (ALREADY IMPLEMENTED)
**File**: `src/omega/oracle/entity_registry.py:31-133` + `model_gateway.py:403-465`
**What it does**: 4-tier entity-to-model resolution: runtime override → entity field →
  domain mapping → system default. Already live in production.
**Crucible integration**: The routing matrix from §5.1 inserts between tiers 2 and 3
  as "Crucible-optimized" model selection.

### 9.8 D118 model_override — DIRECT MODEL FORCING
**File**: `src/omega/oracle/oracle.py:353` (summon method)
**What it does**: `model_override` parameter bypasses TriageRouter entirely.
**Crucible integration**: The Crucible harness uses `model_override` to force each
  model for evaluation. This is the primary integration API.

---

## §10 Researcher Deep-Dive: The Living Infrastructure

A dedicated Researcher agent analyzed the 5 most relevant code files
for Crucible integration. Here's what's **already real** vs **still simulated**.

### 10.1 ObservabilityEngine.record_training_example() — LIVE BUT DEAD FIELD
**Status**: ✅ Live pipeline. ❌ `rating` field is never populated.
**Schema**: System/user/assistant triples + metadata (entity, model, backend, latency, rating)
**Gap**: `rating: Optional[int]` exists but no caller ever sets it. Dead field.
**Fix**: Swap `rating` for structured `{"accuracy": 0-1, "coherence": 0-1, "instruction_following": 0-1}`.
  Add `reference_id` and `critique` fields for Crucible linkage.
**Priority**: P0 — This is the ingestion point.

### 10.2 Distiller T3 Critique Pattern — READY TO REPURPOSE
**Status**: ✅ Production-grade critique pipeline. ⚠️ Single-chain only (not multi-model).
**Key patterns**:
  - Anti-convergence-bias prompt: *"Penalty for Agreement: If you find no corrections
    in a complex topic, you are failing your mandate."*
  - Structured JSON output: `corrections[]`, `confidence_scores{}`, `overall_quality`
  - Per-correction severity: minor | major | critical
  - Correction application: `[CORRECTION: ...]` appended to original output
**Adaptation**: The T3 prompt becomes the Crucible judge prompt with one addition:
  pairwise mode where judge selects winner + loser from N responses.
**Priority**: P0 — This is the critique engine.

### 10.3 BenchmarkRunner — SCHEMA GOOD, INFERENCE SIMULATED
**Status**: ✅ Dataclass design. ❌ All scores are `random.random()`.
**Schema**: `BenchmarkResult` with TTFT, tokens/sec, RAM, scores dict, avg_quality, factuality
**Gap**: `run()` never calls `ModelGateway.generate()` — it's a skeleton.
**Fix**: Wire `run()` to real inference. Replace random scores with judge model critiques.
  Add `pairwise_comparisons` field for DPO dataset generation.
**Priority**: P1 — Schema is usable as-is for the Crucible comparison format.

### 10.4 providers.yaml — NO TRAINING/JUDGE MODE
**Status**: ✅ Production inference chain. ❌ No separate pipeline for training vs interactive.
**Gap**: `strategy: local_first` is hardcoded. No `judge` provider entries. No batch config.
**Fix**: Add `training` and `judge` fallback chains alongside `inference`.
  Add `rate_limit` and `max_concurrency` for batch generation.
**Priority**: P1 — Needed for Tier 2+ scale.

### 10.5 models.yaml — NO JUDGE MODEL FIELD
**Status**: ✅ Agent→model mapping exists. ❌ No `judge_model` field.
**Gap**: Each agent has a `default_model` but no `judge_model` or `reference_model`.
**Fix**: Add `judge_model` (who critiques this agent), `reference_model` (who provides
  gold answers), and `generation_config` (temperature/top_p for synthetic data).
**Priority**: P2 — Nice-to-have for routing matrix refinement.

### 10.6 What's Missing Entirely
1. **No pairwise preference format** — no A-vs-B judge pattern exists anywhere
2. **No reference answers** — no "gold standard" per query
3. **No rejection sampling** — no filtering of low-quality training examples
4. **No multi-model generation for the same query** — each trace produces one response
5. **No leaderboard/ranking across models** — benchmark ranking is per-model, not comparative
6. **No DPO/RLHF format** — training triples are sequential (T1→T2→T3), not comparative

**These 6 gaps are the Cruible's entire reason to exist.**

---

## §11 Quick Reference

| Phase | Tasks | Owner | Timeline | Depends On |
|-------|-------|-------|----------|------------|
| P1: Harness | C-01 to C-04 | Kali | Sprint 2 | D118 model_override |
| P2: Critic | C-05 to C-08 | Kali + Roc | Sprint 3 | P1 + distiller T3 pattern |
| P3: Loop | C-09 to C-12 | Full Fleet | Sprint 4 | P2 + providers.yaml routing |
| P4: Dataset | C-13 to C-16 | Fleet-Wide | Future | P3 + Observability rating fix |
