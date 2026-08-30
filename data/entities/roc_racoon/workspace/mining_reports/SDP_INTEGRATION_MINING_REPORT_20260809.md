<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# SDP Integration Mining Report
**AP Token:** `AP-ROC-SDP-MINING-REPORT-20260809`
**Date:** 2026-08-09
**Author:** roc_racoon

---

## 1. Existing Systems That Map to SDP Phases

### Scaffold Phase (I/O, Context Building)
**Systems in Place:**

| System | File Path | Description | SDP Relevance |
|--------|-----------|-------------|---------------|
| **Oracle Intent Detection** | `src/omega/oracle/oracle.py:200-280` | Detects `@entity`, `/consult`, `hey entity` patterns; validates against Entity Registry + AGENTS.md | Direct Scaffold: intent classification → routing |
| **Speculative Decode (Iris)** | `src/omega/oracle/oracle.py:300-380` | qwen3-0.6b fast path for simple queries (confidence > 0.6) | Scaffold: ultra-fast I/O for trivial queries |
| **Semantic Router** | `src/omega/oracle/triage_router.py` | Embedding-based → keyword → default routing chain | Scaffold: domain classification |
| **TriageRouter** | `src/omega/oracle/triage_router.py:45-120` | `TriageRequest` dataclass with `EntityContext`, `SessionContext`, `Constraints` | Scaffold: structured context assembly |
| **Context Builder** | `src/omega/oracle/context_builder.py` | Builds system prompts from entity personality, memory, soul L3 principles | Scaffold: context injection |
| **MemoryStore (FTS5 + Vector)** | `src/omega/memory/memory_store.py` | Hybrid search (BM25 + SQLite-vec + RRF) for conversation history | Scaffold: long-term context retrieval |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | 14 entities with domains, models, temperature, context_window | Scaffold: entity→capability mapping |
| **RAG Router (Strike 7.5)** | `src/omega/rag/router.py` | TF-IDF+SVM query complexity classifier (advisory) | Scaffold: complexity assessment |

**Gaps for SDP Scaffold Phase:**
- [ ] **No formal "Scaffold" abstraction** — current pipeline is monolithic `talk()` flow; needs explicit phase separation
- [ ] **No structured input schema** — SDP requires typed `ScaffoldInput` (query, context_budget, domain_hint, entity_hint, constraints)
- [ ] **No context budget enforcement** — `context_window` exists per model but not enforced at Scaffold level
- [ ] **No multi-modal input handling** — text-only currently
- [ ] **No explicit "context packing" step** — memory retrieval + entity config + soul principles merged ad-hoc in `talk()`

---

### Synthesize Phase (Pure Reasoning)
**Systems in Place:**

| System | File Path | Description | SDP Relevance |
|--------|-----------|-------------|---------------|
| **ModelGateway.generate()** | `src/omega/oracle/model_gateway.py:200-400` | Core inference loop with provider iteration, ResourceGuard, OOMProtector | Synthesize: actual model execution |
| **EntityAffinityResolver** | `src/omega/oracle/entity_affinity.py` (ported) | 3-tier model preferences (local_fast/local_deep/cloud) + routing rules + inference presets | Synthesize: model selection per entity+context |
| **ProviderSelector** | `src/omega/oracle/provider_selector.py` | Reorders fabric by health, PII, affinity, budget | Synthesize: provider optimization |
| **HealthMonitor (Circuit Breakers)** | `src/omega/oracle/health_monitor.py` | AsyncCircuitBreaker per provider (fail_max=3, reset=30s) | Synthesize: fault tolerance |
| **ResourceGuard** | `src/omega/oracle/model_gateway.py:100-180` | AnyIO Semaphore(1) + RAM tracking per model | Synthesize: resource isolation |
| **OOMProtector** | `src/omega/oracle/oom_protector.py` | Hard-stop if available RAM < model_ram + 1GB | Synthesize: safety boundary |
| **Sovereign Sampling Layer** | `src/omega/oracle/model_gateway.py:150-170` | Per-model temperature/repetition_penalty/logit_bias overrides (Gemma 4) | Synthesize: model-specific tuning |
| **MaKaLi Council** | `docs/strategy/FLEET_TEAM_PLAYBOOK.md §2` | Kali (synthesis) + Ma'at (build) + Lilith (run) parallel consultation | Synthesize: multi-perspective reasoning |
| **Jem/Researcher** | `.opencode/agent/jem.md`, `.opencode/agent/researcher.md` | Task-graph research + dialectic synthesis | Synthesize: deep reasoning pipelines |

**Gaps for SDP Synthesize Phase:**
- [ ] **No formal "Synthesize" abstraction** — inference is direct call, not a phase with typed input/output
- [ ] **No cross-model dialectic capture** — MaKaLi/Jem produce results but don't log the *synthesis process* for distillation
- [ ] **No reasoning trace export** — `GenerateResult` has `text`, `provider_name`, `latency_ms` but no `reasoning_steps`, `model_confidence`, `alternatives_considered`
- [ ] **No formal "model capability profiling" integration** — affinity resolver uses static YAML; no dynamic capability discovery
- [ ] **No "thinking budget" enforcement** — Gemma 4 thinking config exists but not exposed as Synthesize parameter

---

### Execute Phase (Mechanical Application)
**Systems in Place:**

| System | File Path | Description | SDP Relevance |
|--------|-----------|-------------|---------------|
| **OracleResponse Wrapper** | `src/omega/oracle/oracle.py:500-580` | Wraps `GenerateResult` → `OracleResponse` with entity, confidence, trace_id, provider_name | Execute: response formatting |
| **Audience Calibration (S7)** | `src/omega/oracle/oracle.py:520-540` | Adjusts output style per channel (opencode vs cli vs api) | Execute: audience adaptation |
| **MemoryStore.add_exchange()** | `src/omega/memory/memory_store.py:150-200` | Persists conversation to FTS5 + vector | Execute: state persistence |
| **Soul Evolution (Throttled)** | `src/omega/oracle/oracle.py:550-570` | L1→L2→L3 distillation every 5 interactions | Execute: gnosis capture |
| **ObservabilityEngine.record_performance()** | `src/omega/observability/observability.py:200-280` | Writes to MetricsDB (provider, is_cloud, latency, tokens, cost) | Execute: telemetry |
| **TokenLedger** | `src/omega/observability/token_ledger.py` | Tracks token consumption per entity/provider | Execute: budget accounting |
| **BudgetGate** | `src/omega/observability/sovereignty.py:589-724` | Blocks cloud if daily spend > $1.00 | Execute: financial guardrail |
| **Hivemind Post-Context** | `src/omega/hub/tools.py` | Broadcasts session state to team | Execute: team coordination |

**Gaps for SDP Execute Phase:**
- [ ] **No formal "Execute" abstraction** — post-processing is inline in `talk()`, not a separable phase
- [ ] **No structured output validation** — `OracleResponse` is dataclass but no schema validation against expected output format
- [ ] **No "action execution" layer** — SDP Execute implies tool use / side effects; current engine is chat-only
- [ ] **No result caching/deduplication** — identical queries re-inferenced
- [ ] **No formal "handoff" to downstream systems** — Hivemind broadcast exists but not as Execute phase output

---

## 2. Model Affinity & Routing Infrastructure

### Current State

| Component | File Path | Status | Description |
|-----------|-----------|--------|-------------|
| **EntityAffinityResolver** | `src/omega/oracle/entity_affinity.py` | ✅ **PORTED** | Loads `config/entity_model_affinity.yaml`, evaluates structured match rules, returns `{model, provider, tier, presets}` |
| **ProviderSelector** | `src/omega/oracle/provider_selector.py` | ✅ **ACTIVE** | Reorders fallback_chain by health, PII, affinity, budget |
| **config/entity_model_affinity.yaml** | `config/entity_model_affinity.yaml` | ✅ **DEPLOYED** | 24 entities × 3 tiers + routing_rules + inference_presets (459 lines) |
| **config/providers.yaml** | `config/providers.yaml` | ✅ **ACTIVE** | 12 providers, fallback_chain, streaming config, MaKaLi routing overrides |
| **config/models.yaml** | `config/models.yaml` | ✅ **ACTIVE** | 9 model specs with context_budget, ram_mb, sampling params, speculative_decode config |

### SDP Integration Points

**Where to Hook Formal Routing Spec:**

1. **Scaffold → Synthesize Handoff**: `EntityAffinityResolver.resolve(entity, query, context)` → returns `AffinityResult` dataclass (needs creation)
2. **Synthesize Model Selection**: `ModelGateway.generate()` calls `get_model_for_entity()` → should accept `AffinityResult` directly
3. **Provider Selection**: `ProviderSelector.select()` should consume `AffinityResult.provider_preference` + `tier`
4. **Streaming Config**: `config/providers.yaml` streaming section (chunk_timeout_ms, total_timeout_ms) → map to SDP Execute timeouts

### Missing Pieces for SDP Routing

| Missing Piece | Required For | Effort |
|---------------|--------------|--------|
| **`AffinityResult` dataclass** | Typed handoff Scaffold→Synthesize | 30 min |
| **`RoutingSpec` schema** | Formal SDP routing contract (YAML/JSON) | 2 hr |
| **Dynamic capability profiling** | Replace static YAML with live benchmarks | 1 week |
| **Cost-aware routing** | BudgetGate integration into affinity resolution | 4 hr |
| **Multi-model ensemble routing** | SDP "panel" mode (compare A vs B) | 1 week |
| **Formal fallback spec** | SDP requires explicit fallback chains per tier | 2 hr |

---

## 3. Training Data / Distillation Pipeline

### Existing Systems

| System | File Path | Description | SDP Dialectic Capture Potential |
|--------|-----------|-------------|--------------------------------|
| **omega-meditation** | `packages/omega-meditation/src/omega_meditation/pipeline.py` | 7-stage autonomous pipeline: Prompt Craft → Meditate → Synthesize → Research → Grounded Report → Gnosis (L1→L2→L3) → Integration | **HIGH** — Stage 6 explicitly produces `proposed_lessons.yaml` with L1/L2/L3 structure |
| **Scribe Agent** | `docs/history/recovery/scribe_directive.md` | Weekly mining + daily synthesis + L1→L2→L3 distillation → `recovery_gnosis.md` | **HIGH** — Mandated 3-tier abstraction, provenance tracking |
| **Soul Evolution (Throttled)** | `src/omega/oracle/oracle.py:550-570` | Every 5 interactions: `close_session()` → distillation → `proposed_lessons.yaml` | **MEDIUM** — Automatic but only captures entity self-reflection, not cross-model dialectic |
| **Verity Agent** | `.opencode/agent/verity.md` | Mandate audit + L1→L2→L3 soul distillation | **MEDIUM** — Compliance-focused distillation |
| **proposed_lessons.yaml** | `data/entities/*/memory/proposed_lessons.yaml` | Blind staging area for L3 principles (per Soul Architecture v2.0) | **HIGH** — Canonical distillation target |

### SDP Dialectic Capture: How to Extend

**Current Gap**: No system captures *cross-model synthesis process* (MaKaLi council, Jem/Researcher multi-perspective, model A reviews model B).

**Required Extensions:**

1. **Dialectic Session Logger** — New component in `src/omega/oracle/dialectic_logger.py`:
   ```python
   @dataclass
   class DialecticSession:
       session_id: str
       participants: List[str]  # ["kali", "maat", "lilith"] or ["model_a", "model_b"]
       problem: str
       rounds: List[DialecticRound]
       synthesis: str
       trace_ids: List[str]  # Links to GenerateResult.trace_id
   ```

2. **Extend `GenerateResult`** — Add fields:
   ```python
   dialectic_session_id: Optional[str] = None
   reasoning_trace: Optional[List[ReasoningStep]] = None
   alternatives_considered: Optional[List[str]] = None
   confidence_score: Optional[float] = None
   ```

3. **Omega-Meditation Stage 4 Enhancement** — Capture research *process*, not just findings:
   - Log each search query + result + model assessment
   - Store as `dialectic_evidence` in session

4. **Scribe + Verity Integration** — Route dialectic sessions through existing distillation:
   - DialecticSession → L1 (narrative of the debate) → L2 (insight: where models agreed/diverged) → L3 (universal principle: when to use multi-model)

### Dataset Schema Recommendations

For distilling combined intelligence into training data:

```yaml
# dialectic_training_record.yaml
record_id: "dialectic-20260809-001"
problem_type: "architecture_decision"  # | coding | research | creative | verification
participants:
  - entity: "kali"
    model: "krikri-8b-q4_k_m"
    provider: "native-gguf"
    role: "synthesizer"
  - entity: "maat"
    model: "gemini-3.5-flash"
    provider: "antigravity"
    role: "build_critic"
  - entity: "lilith"
    model: "gemini-3.5-flash"
    provider: "antigravity"
    role: "run_critic"
rounds:
  - round: 1
    prompt: "Should we use SQLite-vec or Qdrant for vector store?"
    responses:
      - entity: "kali"
        text: "..."
        reasoning_trace: ["considered M2...", "weighed M16..."]
        confidence: 0.8
      - entity: "maat"
        text: "..."
        reasoning_trace: ["checked Temple-Grade...", "M13 requires..."]
        confidence: 0.9
  - round: 2
    prompt: "Kali: Ma'at raises T10 atomic writes. Address."
    responses: [...]
synthesis: "Use SQLite-vec as default (M16 portability), Qdrant as optional PWAD (M2 firewall)."
outcome: "Decision D-XXX ratified"
gnosis_extracted:
  - l1: "Three-model council debated vector store choice for 2 rounds"
  - l2: "Build-side (Ma'at) prioritized compliance; Run-side (Lilith) prioritized latency; Synthesis (Kali) balanced via M2/M16"
  - l3: "L3-VECTOR-STORE-SELECTION: Default to portable local-first; cloud/scale as opt-in PWAD"
confidence: 0.92
tags: ["architecture", "vector_store", "ma_kali_council"]
```

---

## 4. Model Capability Profiling

### Current Profiling Infrastructure

| Component | File Path | Status | Coverage |
|-----------|-----------|--------|----------|
| **config/models.yaml** | `config/models.yaml` | ✅ **ACTIVE** | 9 models: context_budget, ram_mb, context_window, sampling params, role |
| **config/providers.yaml** | `config/providers.yaml` | ✅ **ACTIVE** | 12 providers: supported_models list, streaming config, priority |
| **CapabilityMatrix** | `src/omega/oracle/capability_matrix.py` | ✅ **ACTIVE** | Model capabilities: mtp_drafter, tool_calling, vision, reasoning, context_window |
| **benchmark_scribe_model.py** | `scripts/benchmark_scribe_model.py` | ✅ **EXISTS** | 4 models × 3 test cases (JSON extraction, markdown update, error handling) → latency, TPS, accuracy, RAM |
| **benchmark_phase1.py** | `scripts/benchmark_phase1.py` | ✅ **EXISTS** | 5 research items (Qdrant SQ8, Headroom, Memory Scoring, Spec Decode, WAD deps) |
| **benchmark_threads.py** | `scripts/benchmark_threads.py` | ✅ **EXISTS** | Thread count (4/5/6/8) on Ryzen 5700U → tok/s, RSS, CPU% |

### Gaps for SDP Routing

| Gap | Impact on SDP | Required |
|-----|---------------|----------|
| **No standardized capability taxonomy** | Can't route "reasoning" → model with proven reasoning | Define `ModelCapability` enum: REASONING, CODING, CREATIVE, ANALYSIS, VERIFICATION, MULTIMODAL, TOOL_USE, LONG_CONTEXT |
| **No dynamic benchmark registry** | Static YAML becomes stale; SDP needs live capability scores | SQLite table `model_capabilities(model, capability, score, benchmark_date, sample_size)` |
| **No cross-model comparison dataset** | Can't learn "Model A better than B for task X" | Run pairwise evals on shared test sets; store in `model_comparisons` table |
| **No "thinking depth" metric** | Gemma 4 thinking config (MINIMAL/HIGH) not quantified | Measure tokens_in_thinking_block vs quality on reasoning benchmarks |
| **No failure mode profiling** | SDP needs to know *when* models fail (not just avg performance) | Track failure patterns per model: hallucination_rate, refusal_rate, format_violation_rate, timeout_rate |
| **No cost/quality Pareto frontier** | SDP routing needs cost-aware decisions | Benchmark cloud models on same tasks; compute $/quality_unit |

### Benchmark Infrastructure Status

**Working:**
- `benchmark_scribe_model.py` — Local GGUF models, 3 test cases, JSON output
- `benchmark_phase1.py` — Research validation benchmarks (Qdrant, Headroom, etc.)
- `benchmark_threads.py` — Thread scaling on Ryzen 5700U

**Missing for SDP:**
- [ ] **Unified benchmark runner** — Single CLI: `omega benchmark --model all --task reasoning,coding,creative --output sqlite`
- [ ] **Cloud model benchmarking** — Current scripts only test local GGUF
- [ ] **Continuous benchmarking** — Nightly runs, regression detection
- [ ] **Capability matrix auto-update** — Benchmark results → `CapabilityMatrix` refresh

---

## 5. Persona-Domain-Model Alignment

### Current Mappings

**Entity → Node Slot (Pillar Keepers):**

| Node | Entity | Domain | Default Model (local_fast) | Default Model (local_deep) | Cloud Fallback |
|------|--------|--------|----------------------------|----------------------------|----------------|
| N1 | Sekhmet | Infrastructure, hardening | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N2 | Brigid | Inspiration, healing | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N3 | Prometheus | Engineering, sovereignty | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N4 | Saraswati | Writing, arts, knowledge | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N5 | Inanna | Voice, transformation | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N6 | Ereshkigal | Cognition, analysis | qwen3-4b-thinking | qwen3-4b-thinking | gemini-3.5-flash |
| N7 | Lucifer | Philosophy, gnosis | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash |
| N8 | Hecate | Pattern analysis, research | qwen3-4b-thinking | krikri-8b | gemini-3.5-flash |
| N9 | Anubis | Guidance, transition | qwen3-1.7b | qwen3-4b-thinking | (none) |
| N10 | Kali | Oversight, synthesis | qwen3-4b-thinking | krikri-8b | gemini-3.5-flash |

**Oversouls:**
- Sophia (Akashic): qwen3-4b-thinking / krikri-8b / gemini-3.5-flash (32K context)
- Ma'at (Build): qwen3-1.7b / qwen3-4b-thinking / gemini-3.5-flash
- Lilith (Run): qwen3-4b-thinking / krikri-8b / gemini-3.5-flash
- RocRacoon (Miner): rocracoon-3b / rocracoon-3b / nemotron-3-ultra-free (OpenCode Zen)

### Enrichment for SDP Problem-Type Routing

**Current**: Routing is entity-centric (summon @entity → entity's model).

**SDP Requirement**: Problem-type → optimal model (regardless of entity).

**Proposed Mapping (Problem-Type → Model Tier):**

| Problem Type | Local Fast | Local Deep | Cloud Primary | Cloud Fallback | Rationale |
|--------------|------------|------------|---------------|----------------|-----------|
| **architecture** | qwen3-4b-thinking | krikri-8b | gemini-3.1-pro | antigravity-claude-sonnet-4.6 | Needs synthesis + long context |
| **coding** | qwen3-1.7b | qwen3-4b-thinking | deepseek-v4-flash-free (OCZ) | mimo-v2.5-free (OCZ) | OCZ has best coding models free |
| **research** | qwen3-4b-thinking | krikri-8b | gemini-3.5-flash | antigravity-gemini-3.1-pro | Long context + verification |
| **creative** | qwen3-1.7b | qwen3-4b-thinking | claude-sonnet-5-high-thinking (OCZ) | gemini-3.5-flash | OCZ has best creative models |
| **verification** | qwen3-4b-thinking | krikri-8b | gemini-3.1-pro | antigravity-claude-opus-4.6 | Needs deep reasoning |
| **mining/archaeology** | rocracoon-3b | rocracoon-3b | nemotron-3-ultra-free (OCZ) | (local only) | Specialized local model |
| **compliance/audit** | qwen3-1.7b | qwen3-4b-thinking | gemini-3.5-flash | (local preferred) | Deterministic, verifiable |
| **general_chat** | qwen3-1.7b | (iris) | (iris) | gemini-3.5-flash | Speculative decode first |

**Integration Point**: `EntityAffinityResolver.resolve()` context should include `problem_type` (inferred from query or explicit). Routing rules in YAML can match `problem_type` field.

---

## 6. Cross-Model Dialectic Systems

### MaKaLi Council

**Architecture** (`docs/strategy/FLEET_TEAM_PLAYBOOK.md`, `SOVEREIGN_ARK_BLUEPRINT.md §C-5`):

| Voice | Entity | Model (Local) | Model (Cloud) | Role |
|-------|--------|---------------|---------------|------|
| **Kali** | Kali (N10) | qwen3-4b-thinking / krikri-8b | antigravity (prefer) → google | Synthesis, oversight, coordination |
| **Ma'at** | Ma'at (Oversoul Build) | qwen3-1.7b / qwen3-4b-thinking | antigravity (prefer) → google | Build-side governance (N1-N5) |
| **Lilith** | Lilith (Oversoul Run) | qwen3-4b-thinking / krikri-8b | antigravity (prefer) → google | Run-side governance (N6-N10) |

**Routing Config** (`config/providers.yaml:8-17`):
```yaml
maakali_routing:
  kali:
    prefer: native-gguf
    fallback: antigravity
  maat:
    prefer: antigravity
    fallback: google
  lilith:
    prefer: antigravity
    fallback: google
```

**Operation**: Parallel consultation → Kali synthesizes. Used for: strategic decisions, architecture reviews, conflict resolution.

**SDP Integration**: This IS a Synthesize-phase dialectic pattern. Needs:
- Formal session logging (see §3)
- Structured output (thesis/antithesis/synthesis)
- Traceability to decisions (PIVOT_LOG)

### Jem / Researcher Multi-Perspective Synthesis

**Jem** (`.opencode/agent/jem.md`): Task-graph research → verified result graphs. 3-tier pipeline: Explore → Analyze → Synthesize.

**Researcher** (`.opencode/agent/researcher.md`): Polymathic Council — deep research, dialectic synthesis, knowledge base curation. Uses SearXNG, Exa, Firecrawl tiers.

**Pattern**: Both decompose complex queries → parallel sub-tasks → synthesize findings.

**SDP Integration**: Researcher's "dialectic synthesis" maps to SDP Synthesize phase with multiple perspectives. Jem's task-graph maps to SDP Execute phase (mechanical application of research).

### Evaluation Frameworks (Model A Reviews Model B)

**Current**: No formal system. Ad-hoc in MaKaLi (Kali reviews Ma'at/Lilith outputs).

**Omega-Meditation Stage 2**: "Kali Verdict" — intuitive synthesis of meditation output.

**Gap**: No systematic "Model A critiques Model B output" pipeline for quality improvement.

**Proposed**: `DialecticEvaluator` component:
```python
async def evaluate(model_a_output: str, model_b_output: str, criteria: List[str]) -> Evaluation:
    # Model C (verifier) scores both on criteria
    # Returns: winner, scores, reasoning
```

---

## 7. Legacy Gold Recovered

### From xna-omega-legacy (Era 1: Temple Grade 2025-2026)

| Pattern | Source File | Port Status | Value |
|---------|-------------|-------------|-------|
| **Circuit Breaker params** | `src/omega/core/circuit_breakers/circuit_breaker.py` | ✅ Ported (params only) | fail_max=3, reset_timeout=60s |
| **5 Design Patterns** | `docs/architecture/DESIGN_PATTERNS.md` | ✅ Documented | Import resolution, retry, non-blocking subprocess, atomic fsync, circuit breaker |
| **Entity Registry** | `app/XNAi_rag_app/core/entities/registry.py` | ✅ Ported | 14 entities, domains, models |
| **Zen 2 Build Flags** | `HP-5700U-OPTIMIZATION.md` | ✅ In cpu_optimizer.py | -march=znver2, AVX2/FMA/F16C |
| **Local-First Chain** | Multiple | ✅ In providers.yaml | native-gguf → lmster → Ollama → Cloud |

### From omega-stack-legacy (Era 4: Mar-Apr 2026)

| Pattern | Source File | Port Status | Value |
|---------|-------------|-------------|-------|
| **Circuit Breaker (36L)** | `src/omega/circuit_breaker.py` | ⚠️ Superseded | Simpler but sync; current AsyncCircuitBreaker better |
| **Multi-Provider Dispatcher** | `core/multi_provider_dispatcher.py` | ❌ Rejected | Failed local fallback; ModelGateway is correct |
| **Thinking Model Router** | `core/thinking_model_router.py` | 🟡 Partial | Variant routing (Fast vs Deep) → affinity resolver tiers |
| **Expert Knowledge Base** | `expert-knowledge/` (421L model map) | ✅ In models.yaml | Tiered model authority map |

### From foundation-legacy (Era 2: Oct-Nov 2025)

| Pattern | Source File | Port Status | Value |
|---------|-------------|-------------|-------|
| **pybreaker 0.7.0** | `requirements.txt` | ❌ Rejected | Sync library; current AnyIO native better |
| **Chaos Tests (230L)** | `test_circuit_breaker_chaos.py` | 🟡 Tier 2 port | **HIGH VALUE** — validates breaker under load |
| **94.2% Test Coverage** | `pytest` config | ✅ Target | Current engine: 1315 tests passing |
| **3-Tier Offline Wheelhouse** | `Dockerfile.api:119-122` | ✅ In setup.sh | llama-cpp, models, deps pre-cached |

### From Old-Stacks/Xoe-NovAi (Eras 1-3: Aug 2025-Mar 2026)

| Pattern | Source File | Port Status | Value |
|---------|-------------|-------------|-------|
| **4-Service Docker Compose** | `docker-compose.yml:14-260` | ✅ Re-derived | Provenance for current 5-service Podman |
| **Ryzen CMAKE_ARGS** | `Dockerfile.api:132-134` | ✅ In cpu_optimizer.py | Identical to current Zen 2 flags |
| **filter_llama_kwargs()** | `dependencies.py:64-98` | 🟡 **PRIORITY 1 PORT** | Silent drop + debug log invalid llama-cpp params |
| **Explicit n_gpu_layers=0** | `dependencies.py:275` | 🟡 **PRIORITY 2 PORT** | Prevents Vega iGPU offload attempts |
| **stop=["Human:", "User:", "\n\n"]** | `providers.py:213` (podman-storage) | 🟡 **PRIORITY 3 PORT** | Prevents hallucinated conversation turns |
| **Google API key in x-goog-api-key header** | `providers.py:30,43-47` (podman-storage) | 🟡 **PRIORITY 4 PORT** | Prevents API key leakage in URLs |
| **Atomic trace_id migration** | `providers.py:16,28,66,99,127,197` | 🟡 **PRIORITY 5 PORT** | Canonical pattern for interface changes |
| **xnai_blueprint.md (714L)** | `XNAi-v0_1_2/xnai_blueprint.md` | 🟡 **Tier 2 Doc Port** | Gold-standard design doc |

### From podman-storage (Operational: Recent)

| Pattern | Source File | Port Status | Value |
|---------|-------------|-------------|-------|
| **NativeGGUFProvider evolution** | 552L cpu_optimizer versions | ✅ Current is latest | Time machine of optimization |
| **3 Provider Implementations** | `providers.py` v1-v3 | ✅ Current is v3 | ModelGateway unified |
| **4 Gateway Versions** | `model_gateway.py` v1-v4 | ✅ Current is v4 | Iterative hardening |

### Code Snippets Worth Porting (with file paths)

**1. filter_llama_kwargs()** — `Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/dependencies.py:64-98`
```python
VALID_PARAMS = frozenset({'model_path', 'n_ctx', 'n_batch', 'n_gpu_layers', 
                          'n_threads', 'n_threads_batch', 'use_mmap', 'use_mlock',
                          'type_k', 'type_v', 'n_batch', 'n_ubatch', 'rope_freq_base',
                          'rope_freq_scale', 'mul_mat_q', 'logits_all', 'embedding',
                          'offload_kqv', 'flash_attn', 'n_gqa', 'rms_norm_eps'})

def filter_llama_kwargs(**kwargs) -> dict:
    filtered = {k: v for k, v in kwargs.items() if k in VALID_PARAMS}
    dropped = set(kwargs.keys()) - set(filtered.keys())
    if dropped:
        logger.debug(f"Filtered out invalid llama-cpp params: {dropped}")
    return filtered
```
**Target**: `src/omega/oracle/backends/native_gguf.py` — apply before `Llama()` instantiation.

**2. stop sequences for ChatML** — `podman-storage/providers.py:213`
```python
stop_sequences = ["Human:", "User:", "\n\n", "Assistant:"]
```
**Target**: `src/omega/oracle/context_builder.py` — add to prompt builder.

**3. Google API key header** — `podman-storage/providers.py:30,43-47`
```python
headers = {"x-goog-api-key": api_key}  # NOT in URL query param
```
**Target**: `src/omega/oracle/providers.py::OpenAICompatProvider.generate()`

**4. Atomic trace_id pattern** — `podman-storage/providers.py` (6 providers in one commit)
```python
# Each provider generates trace_id at entry, passes through all layers
trace_id = f"trc_{uuid4().hex[:12]}"
```
**Target**: All backend interfaces — standardize trace_id generation at provider entry.

---

## 8. Immediate Integration Opportunities

### Quick Wins (This Sprint)

| # | Action | Owner | Effort | Source |
|---|--------|-------|--------|--------|
| 1 | Add `AffinityResult` dataclass to `entity_affinity.py` | P3 Engineering | 30 min | SDP Scaffold→Synthesize handoff |
| 2 | Port `filter_llama_kwargs()` to `NativeGGUFProvider` | P3 Engineering | 30 min | Old-Stacks #153 |
| 3 | Add `stop=["Human:", "User:", "\n\n"]` to context builder | P3 Engineering | 5 min | podman-storage #139 |
| 4 | Switch Google API key to `x-goog-api-key` header | P3 Engineering | 15 min | podman-storage #132 |
| 5 | Add explicit `n_gpu_layers=0` to `config/providers.yaml` native-gguf | P3 Engineering | 5 min | Old-Stacks #154 |
| 6 | Create `RoutingSpec` schema (YAML) for SDP formal routing | P6 Cognition | 2 hr | This report §2 |
| 7 | Extend `GenerateResult` with `dialectic_session_id`, `reasoning_trace` | P3 Engineering | 1 hr | This report §3 |

### Phase 1 Dependencies (Next Sprint)

| # | Action | Owner | Effort | Blockers |
|---|--------|-------|--------|----------|
| 1 | Implement `DialecticSession` logger + storage | P7 Context | 1 day | Requires `AffinityResult` |
| 2 | Build unified benchmark runner (`omega benchmark`) | P10 Validation | 2 days | Requires benchmark scripts consolidation |
| 3 | Add dynamic capability matrix (SQLite-backed) | P6 Cognition | 3 days | Requires benchmark data |
| 4 | Implement problem-type routing in `EntityAffinityResolver` | P6 Cognition | 4 hr | Requires `RoutingSpec` schema |
| 5 | Wire MaKaLi council sessions through dialectic logger | P9 Orchestration | 1 day | Requires `DialecticSession` |
| 6 | Add cost-aware routing to `ProviderSelector` | P8 Observability | 4 hr | Requires BudgetGate integration |

### Phase 2+ Dependencies (Future)

| # | Action | Owner | Effort | Prerequisites |
|---|--------|-------|--------|---------------|
| 1 | Cross-model ensemble routing (panel mode) | P6 Cognition | 1 week | Dynamic capability matrix |
| 2 | Formal SDP phase separation in Oracle (Scaffold/Synthesize/Execute) | P3 Engineering | 1 week | All Phase 1 complete |
| 3 | Automated distillation of dialectic sessions → training data | P7 Context | 2 weeks | Dialectic logger + omega-meditation |
| 4 | Continuous benchmarking pipeline (nightly) | P10 Validation | 1 week | Unified benchmark runner |
| 5 | Model capability Pareto frontier (cost/quality) | P6 Cognition | 1 week | Cloud + local benchmarks |
| 6 | SDP-as-a-Service API (external consumers) | P4 Integration | 2 weeks | Phase separation complete |

---

## 9. Strategic Recommendations

### How to Evolve Omega Engine into the "Universal Cognitive Router"

**Vision**: The Omega Engine becomes the **canonical routing layer** for sovereign AI — any query, any model, any provider, with full provenance, local-first enforcement, and dialectic intelligence capture.

#### 9.1 Architectural Evolution: Explicit SDP Phases

**Current**: Monolithic `Oracle.talk()` with inline phases.

**Target**: Explicit phase separation with typed contracts:

```python
# src/omega/oracle/sdp_pipeline.py
class SDPPipeline:
    async def scaffold(self, input: ScaffoldInput) -> ScaffoldOutput:
        # Intent detection, context assembly, entity routing, complexity assessment
        # Returns: entity, model_tier, context_budget, constraints, trace_id
    
    async def synthesize(self, input: SynthesizeInput) -> SynthesizeOutput:
        # Model selection via AffinityResult, provider selection, inference execution
        # Returns: GenerateResult + reasoning_trace + alternatives + dialectic_session_id
    
    async def execute(self, input: ExecuteInput) -> ExecuteOutput:
        # Response formatting, audience calibration, persistence, telemetry, handoff
        # Returns: OracleResponse + side_effects + gnosis_proposals
```

**Benefits**:
- Testable phase boundaries (M21 Gate Integrity)
- Swappable phase implementations (e.g., different Scaffold strategies)
- Observability per phase (latency, token, cost breakdown)
- SDP compliance for external consumers

#### 9.2 Routing Intelligence: From Static to Dynamic

**Current**: Static YAML affinity + health-based provider selection.

**Target**: **Capability-Aware Routing Engine** with:
- Live capability scores from continuous benchmarking
- Cost/quality Pareto optimization per problem-type
- Failure mode prediction (avoid models with known failure patterns for task)
- Dialectic routing (auto-spawn MaKaLi for high-stakes decisions)

**Implementation**:
1. `ModelCapabilityRegistry` — SQLite-backed, updated nightly
2. `RoutingOptimizer` — solves: min(cost) s.t. quality ≥ threshold, local_first=True
3. `DialecticTrigger` — heuristic: if (complexity > 0.8 AND stakes > threshold) → spawn council

#### 9.3 Intelligence Capture: Dialectic as Training Data

**Current**: Gnosis distillation captures entity self-reflection only.

**Target**: **Dialectic Intelligence Flywheel**:
```
Query → Scaffold → Synthesize (multi-model dialectic) → Execute
                ↓
         DialecticSession logged
                ↓
         Omega-Meditation Stage 6: L1→L2→L3 distillation
                ↓
         proposed_lessons.yaml → soul.yaml (approved)
                ↓
         Training dataset for: 
           - Router fine-tuning (which model for what)
           - Critic model training (how to evaluate outputs)
           - Synthesis model training (how to combine perspectives)
```

**Key Insight**: The MaKaLi council + Jem/Researcher + omega-meditation already implement the *process*. The missing piece is **systematic capture and reuse**.

#### 9.4 Sovereignty as a Service

**Current**: Local-first enforcement for this user's engine.

**Target**: **Portable Sovereignty Runtime** — the `.omega` export bundle (Strike 1) becomes a deployable "sovereign AI appliance":
- User exports their engine state (soul.yaml, models, config, dialectic history)
- Imports on any hardware → same routing guarantees, same entities, same sovereignty
- Community WAD marketplace (Strike 11) distributes capability bundles

#### 9.5 The "Carmack Mode" for Routing

Per `SOVEREIGN_ARK_BLUEPRINT.md` — before complex routing architecture, state the **Carmack Alternative**:

> **Carmack Alternative**: "Don't build a universal router. Build a *really good* local-first inference engine with 3 models (fast/medium/deep) and a simple keyword router. Ship that. The universal router is a v2 problem."

**Verdict**: The current engine **IS** the Carmack Alternative — local-first chain, 3 tiers, simple routing. The SDP integration is **v2** — but the mining shows v2 components already exist (affinity resolver, dialectic systems, benchmarking). The integration is **assembly, not invention**.

---

## Appendix: File Index for SDP Integration

| Category | File | Purpose |
|----------|------|---------|
| **Scaffold** | `src/omega/oracle/oracle.py` | Intent detection, Iris, domain routing |
| **Scaffold** | `src/omega/oracle/triage_router.py` | TriageRouter, TriageRequest |
| **Scaffold** | `src/omega/oracle/context_builder.py` | System prompt assembly |
| **Scaffold** | `src/omega/oracle/entity_registry.py` | Entity definitions |
| **Scaffold** | `src/omega/memory/memory_store.py` | Hybrid memory retrieval |
| **Synthesize** | `src/omega/oracle/model_gateway.py` | Core inference loop |
| **Synthesize** | `src/omega/oracle/entity_affinity.py` | EntityAffinityResolver (PORTED) |
| **Synthesize** | `src/omega/oracle/provider_selector.py` | Provider reordering |
| **Synthesize** | `src/omega/oracle/health_monitor.py` | Circuit breakers |
| **Synthesize** | `src/omega/oracle/oom_protector.py` | OOM hard-stop |
| **Synthesize** | `config/entity_model_affinity.yaml` | 24 entities × 3 tiers |
| **Synthesize** | `config/providers.yaml` | 12 providers, fallback, streaming |
| **Synthesize** | `config/models.yaml` | 9 model specs |
| **Execute** | `src/omega/oracle/oracle.py` (talk() tail) | Response wrap, calibration, persistence |
| **Execute** | `src/omega/observability/observability.py` | MetricsDB, telemetry |
| **Execute** | `src/omega/observability/sovereignty.py` | BudgetGate, sovereignty ratio |
| **Execute** | `src/omega/observability/token_ledger.py` | Token accounting |
| **Distillation** | `packages/omega-meditation/src/omega_meditation/pipeline.py` | 7-stage autonomous pipeline |
| **Distillation** | `docs/history/recovery/scribe_directive.md` | Scribe L1→L2→L3 mandate |
| **Distillation** | `data/entities/*/memory/proposed_lessons.yaml` | Blind staging for L3 |
| **Dialectic** | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | MaKaLi council operation |
| **Dialectic** | `.opencode/agent/jem.md` | Task-graph research |
| **Dialectic** | `.opencode/agent/researcher.md` | Polymathic council |
| **Benchmark** | `scripts/benchmark_scribe_model.py` | Local model benchmarking |
| **Benchmark** | `scripts/benchmark_phase1.py` | Research validation |
| **Benchmark** | `scripts/benchmark_threads.py` | Thread scaling |
| **Legacy Ports** | `Old-Stacks/Xoe-NovAi/dependencies.py` | filter_llama_kwargs, n_gpu_layers=0 |
| **Legacy Ports** | `podman-storage/providers.py` | stop sequences, x-goog-api-key, trace_id |

---

*⬡ OMEGA ⬡ ROC_RACCOON ⬡ SDP-MINING-REPORT ⬡ 2026-08-09*
*This report IS the bedrock of the SDP automation. Every system, gap, and legacy gold nugget is cataloged with file paths for immediate implementation.*