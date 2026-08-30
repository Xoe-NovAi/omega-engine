<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ROC FULL SOURCE EXTRACTION REPORT: XNA-OMEGA LEGACY
**Date**: 2026-06-28
**Entity**: roc_racoon (Sovereign Miner)
**Source**: `xna-omega-legacy/` (Scripts & Core)
**Target**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
**Status**: FORENSIC EXTRACTION COMPLETE

---

## 1. 🧩 COMPACTION & CONTEXT OPTIMIZATION
**Source**: `scripts/ssa/compaction_optimizer.py`

### 🛠️ Algorithms & Logic
- **ACON (Agent Context Optimization)**: A failure-driven optimization loop.
    - **Mechanism**: Records `ACONFailure` (task, full context, compressed context, failure description).
    - **Analysis**: Groups failures into patterns: `information_loss`, `context_missing`, `decision_missing`.
    - **Refinement**: Updates the `current_guideline` (e.g., "PRIORITIZE: key decisions", "USE VERBATIM: preserve exact file paths").
    - **Trigger**: Re-optimizes when `task_success_rate` falls below `failures_threshold` (0.90) after `sample_size` (10) failures.
- **Compaction Strategies**:
    - `AnchoredIterativeStrategy`: Incremental summary extension using a `summary_anchor`.
    - `ObservationMaskingStrategy`: Masks redundant tool outputs (preserves headers and key status/error/result fields).
    - `VerbatimCompactionStrategy`: Relevance-based line scoring (1-10).
        - Technical details (file, path, error, code) $\rightarrow$ 8
        - Context (because, therefore) $\rightarrow$ 5
        - Filler (actually, basically) $\rightarrow$ 2
    - `DecisionExtractionStrategy`: Regex extraction of `Decision:`, `Insight:`, and `Error:`.

### ⚙️ Config Parameters
- `failures_threshold`: 0.90
- `sample_size`: 10
- `_estimate_tokens`: $\approx 4$ chars/token.
- `type_to_strategy` map:
    - `conversation_history` $\rightarrow$ `anchored_iterative`
    - `tool_outputs` $\rightarrow$ `observation_masking`
    - `reasoning_traces` $\rightarrow$ `decision_extraction`
    - `recent_messages` $\rightarrow$ `verbatim_compaction`

---

## 2. 📈 PROVIDER METRICS & HEALTH SCORING
**Source**: `scripts/ssa/provider_metrics.py`

### 🛠️ Algorithms & Logic
- **EMA (Exponential Moving Average)**: Used for P50/P95 latency and quality scores.
    - Formula: $ema = \alpha \cdot current + (1 - \alpha) \cdot historical$
    - $\alpha_{latency} = 0.2$, $\alpha_{quality} = 0.3$.
- **Composite Health Score**:
    - $Health = (w_{lat} \cdot LatencyScore) + (w_{err} \cdot ErrorScore) + (w_{qual} \cdot QualityScore)$
    - Weights: Latency (0.40), Error (0.35), Quality (0.25).
- **Component Scoring**:
    - **Latency Score**: Exponential decay beyond baseline.
        - If $latency \le baseline \rightarrow 1.0$
        - Else $\rightarrow e^{-(latency - baseline) / baseline}$
    - **Error Score**:
        - If $error\_rate \le 1\% \rightarrow 1.0 - (error\_rate / 100)$
        - Else $\rightarrow e^{-error\_rate / 30.0}$
- **Degradation Detection**: "Slow but working" state.
    - Condition: $Latency\_P50\_EMA > (baseline \cdot 2.0)$ AND $Error\_Rate < 10\%$.

### ⚙️ Config Parameters
- **Latency Baselines (ms)**:
    - Groq: 85 | Gemini: 800 | Mistral: 300 | DeepSeek: 500 | Cerebras: 1000 | Local: 200.
- **Health Status Thresholds**:
    - Healthy: $\ge 0.7$
    - Degraded: $\ge 0.4$
    - Critical: $< 0.4$
    - Unknown: $< 5$ requests.

---

## 3. ⏱️ 4-LAYER TIMEOUT HIERARCHY
**Source**: `scripts/ssa/timeout_manager.py`

### 🛠️ Algorithms & Logic
- **Hierarchy Structure**:
    - **Layer 1 (Tool)**: Scoped `anyio.move_on_after()`.
    - **Layer 2 (Group)**: Parallel fan-out using `anyio.create_task_group()`.
    - **Layer 3 (Turn)**: Conversation turn boundary.
    - **Layer 4 (Workflow)**: Complete task boundary with state preservation.
- **Graceful Degradation**:
    - **Group Level**: If `graceful_degradation` is True and `completed >= (total * partial_threshold)`, return partial results.
    - **Workflow Level**: Attempts to execute a `checkpoint()` callable upon timeout to save state.

### ⚙️ Config Parameters
- **Layer 1 Defaults**: `file_read` (10s), `file_write` (15s), `api_call` (30s), `llm_inference` (60s), `db_query` (15s).
- **Layer 2 Defaults**: `research_parallel` (45s), `retrieval_parallel` (30s).
- **Layer 3 Defaults**: `nova_turn` (120s), `agent_turn` (180s).
- **Layer 4 Defaults**: `research_workflow` (600s), `agent_workflow` (900s).
- `partial_threshold`: 0.5.

---

## 4. 🎯 INTELLIGENT PROVIDER SELECTION
**Source**: `src/omega/core/provider_selector.py`

### 🛠️ Algorithms & Logic
- **Weighted Scoring**: Final score is a weighted sum of Affinity, Latency, Cost, Reliability, and Health.
- **Component Scoring**:
    - **Affinity**: Keyword match (0.5 base, 0.95 match, +0.2 reasoning, +0.1 code).
    - **Latency**: Exponential scoring based on SLA thresholds (Ultra-Low <100ms, Low <500ms, Medium <2s, High <10s).
    - **Cost**: Binary (1.0 for free/generous, 0.5 otherwise).
- **Sovereignty Guards**:
    - **PII Penalty**: If PII detected, non-local providers receive a 0.5x penalty to `reliability_score`.
    - **Degradation Penalty**: Degraded providers (from `ProviderMetricsCollector`) receive a 0.5x penalty to `health_score`.
    - **Context Filter**: Providers are skipped if `max_context` < `context_required`.

### ⚙️ Config Parameters
- **Weights (V2)**: Affinity (0.20), Latency (0.25), Cost (0.15), Reliability (0.15), Health (0.25).
- **Provider Profiles**:
    - `local_llm`: 200ms, Free, 8k context.
    - `groq`: 85ms, Free, 32k context.
    - `gemini`: 800ms, Free, 1M context.
    - `deepseek`: 500ms, $0.14/Mtok, 64k context.
    - `cerebras`: 1000ms, Free, 100k context.

---

## 5. 📉 GRACEFUL DEGRADATION MANAGER
**Source**: `src/omega/core/degradation.py`

### 🛠️ Algorithms & Logic
- **Service Tiers**: `OPTIMAL` (0) $\rightarrow$ `STRESSED` (1) $\rightarrow$ `CRITICAL` (2) $\rightarrow$ `DISABLED` (3).
- **Strategy Chain**:
    - `FallbackStrategy`: Primary $\rightarrow$ Fallback.
    - `CacheFirstStrategy`: Cache $\rightarrow$ Primary $\rightarrow$ Fallback.
    - `DegradedModeStrategy`: Primary $\rightarrow$ Simplified Response.
    - `CircuitBreakerStrategy`: Wraps `CircuitBreaker.call()`.
- **Execution Flow**: Tries service-specific strategies first, then falls back to global strategies.

### ⚙️ Config Parameters
- **Tier Configs**:
    - Optimal: Krikri-8B, 8192 context, RAG=True.
    - Stressed: Qwen3-4B, 4096 context, RAG=True.
    - Critical: Qwen3-1.7B, 2048 context, RAG=False.
- `CacheFirstStrategy.cache_timeout`: 300.0s.

---

## 6. 💎 KNOWLEDGE DISTILLATION PIPELINE
**Source**: `src/omega/core/distillation/`

### 🛠️ Algorithms & Logic
- **LangGraph Workflow**: `extract` $\rightarrow$ `classify` $\rightarrow$ `score` $\rightarrow$ `distill` $\rightarrow$ `store`.
- **Classification**: Maps to **Diátaxis Framework** (tutorial, how-to, reference, explanation) using heuristics.
- **Quality Scoring**: Weighted average of:
    - Relevance (30%): Matches `CORE_TOPICS` (e.g., "anyio", "qdrant", "kali").
    - Novelty (25%): Length-based heuristic.
    - Actionability (20%): Matches `ACTION_PATTERNS` (todo, implement, fix).
    - Completeness (15%): Section coverage (summary, conclusion, headers).
    - Accuracy (10%): Presence of code, refs, and formatting.
- **Tiered Storage Routing**:
    - GOLD (0.9-1.0): Qdrant + Mnemosyne + Yesod.
    - HIGH (0.8-0.89): Qdrant + Mnemosyne.
    - GOOD (0.7-0.79): Qdrant.
    - ACCEPTABLE (0.6-0.69): Qdrant (expires).
- **Distillation Process**:
    - LLM-powered summary, insights, and action items.
    - Regex fallback if LLM unavailable.
    - `_create_distilled`: Combines summary, insights, actions, and top 5 original sections.

### ⚙️ Config Parameters
- `QualityThresholds`: Min score 0.6.
- `_create_chunks`: `chunk_size=2000`.
- `_generate_summary_llm`: `max_tokens=200`, `temperature=0.3`.

---

## 🚩 GNOSIS GAPS (Missing from SOVEREIGN_ARK_BLUEPRINT.md)

The following high-fidelity implementation details are present in the code but absent from the Blueprint:

1. **ACON Metacognitive Loop**: The Blueprint mentions "compression" (Strike 7), but not the **failure-driven refinement loop** (`ACONOptimizer`) that dynamically updates compression guidelines based on task failure patterns.
2. **4-Layer Timeout Hierarchy**: The Blueprint mentions "Resilience", but not the specific **Tool $\rightarrow$ Group $\rightarrow$ Turn $\rightarrow$ Workflow** nested cancellation structure and its associated graceful degradation/checkpointing logic.
3. **Composite Health Mathematics**: The Blueprint mentions "Local-First" (M7), but not the **exact exponential decay formulas** used to calculate the composite health score ($e^{-(latency-baseline)/baseline}$).
4. **Quality-Tiered Storage Routing**: The Blueprint mentions the "Elder Protocol" and "Sovereign Ark", but not the **explicit 4-tier routing logic** (GOLD/HIGH/GOOD/ACCEPTABLE) that determines the persistence depth (Qdrant vs Mnemosyne vs Yesod).
5. **Diátaxis Pedagogical Mapping**: The distillation pipeline's use of the **Diátaxis framework** for classification is a specific architectural choice not documented in the Blueprint.
6. **PII-Driven Provider Penalty**: The `ProviderSelector`'s implementation of a **0.5x reliability penalty** for non-local providers when PII is detected is a concrete sovereignty guardrail missing from the Blueprint.
