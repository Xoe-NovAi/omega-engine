<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Model Library Integration Architecture
## Unifying Model Study KB with Existing Model Infrastructure

**Date**: 2026-07-18
**Author**: Kali (Transcendent Oversoul)
**Status**: ARCHITECTURAL DECISION — Ready for Implementation

---

## 📋 EXECUTIVE SUMMARY

We have **FOUR model-related systems** that need unification:

| System | Location | Purpose | Status |
|--------|----------|---------|--------|
| **Provider Fabric** | `config/providers.yaml`, `config/models.yaml` | Runtime inference routing (local-first chain) | ✅ Production |
| **Research Model Profiles** | `config/research/model_profiles.yaml`, `R_MODEL_RESEARCH_PROTOCOL.md` | Model-adaptive research protocol | ✅ Production |
| **Model Card Library** | `docs/research/model_db/` | **Production model catalog** (24 models, T1/T2/T3 tiers, YAML schema, live API state) | ✅ Production |
| **Model Study KB** | `docs/kb/MODEL_STUDY_KNOWLEDGE_BASE.md`, `data/model_study/model_study.db` | Empirical split-test knowledge base | 🆕 New |

**Decision**: **Hybrid Architecture** — File-based model cards (YAML frontmatter + Markdown) as source of truth, SQLite DB as queryable index, unified via a Model Registry service. **The existing `docs/research/model_db/` library becomes the foundation.**

---

## 🏗️ CURRENT STATE ANALYSIS

### What Exists (Production)

#### 1. Provider Fabric (`config/providers.yaml`)
```yaml
# Runtime inference chain — local-first priority
inference:
  strategy: local_first
  fallback_chain:
    - provider: native-gguf      # Priority 0
    - provider: lmster           # Priority 1
    - provider: ollama           # Priority 2 (disabled)
    - provider: antigravity      # Priority 3
    - provider: google           # Priority 4
    - provider: openrouter       # Priority 4
    - provider: opencode-zen     # Priority 5
    - provider: cline            # Priority 6
    - provider: mock             # Priority 99
```

#### 2. Local Model Configs (`config/models.yaml`)
```yaml
models:
  qwen3-1.7b:
    context_budget: 15000
    provider: native-gguf
    path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf
    size_gb: 1.6
    ram_mb: 2048
    context_window: 8192
    role: "P1-P10 pillars, fast inference"
```

#### 3. Model Card Library (`docs/research/model_db/`) — **PRODUCTION FOUNDATION**

This is the **existing production model catalog** with 24 models across T1/T2/T3 tiers:

| File | Purpose |
|------|---------|
| `CURRENT_MODELS.md` | 24 models with YAML schema: capabilities (reasoning/code/knowledge/creative scores), cost, latency, uptime, community ratings, routing rules |
| `LEGACY_CROSS_REFERENCE_REPORT.md` | Cross-reference of 72 legacy model references from xna-omega-legacy |
| `.last_state.json` | Live API state: OpenRouter (42 free models), Google (2 Gemma), OpenCode Zen (42 models) |

**Key Features:**
- **Tiered classification**: T1 (reflex/fast), T2 (balanced), T3 (reasoning/knowledge)
- **Capability scoring**: reasoning, code_generation, knowledge, creative (0-1 scale)
- **Operational metrics**: cost_per_1k_tokens, latency_p99_ms, uptime_percent
- **Community intelligence**: ratings, notes, identity tracking for stealth models
- **Routing rules**: `engine_routable`, `opencode_cli_only`, `recommended_engine_alternative`
- **Identity tracking**: `identity_history` for stealth models (e.g., `big-pickle` = DeepSeek V4 Flash, was GLM-4.6)
- **Live API state**: `.last_state.json` captures OpenRouter (42 free), Google (2), OpenCode Zen (42)

**Example Model Definition (from CURRENT_MODELS.md):**
```yaml
models:
  opencode/big-pickle:
    provider: opencode-zen
    context_window: 200000
    free_tier: true
    capabilities:
      reasoning: 0.88
      code_generation: 0.94
      knowledge: 0.80
      creative: 0.70
      tool_use: true
      structured_output: true
    cost_per_1k_tokens_usd: 0.0
    latency_p99_ms: 3200
    uptime_percent: 99.0
    community_rating: "4.5/5.0"
    community_notes:
      - "STEALTH MODEL — identity may swap without notice. Current: DeepSeek V4 Flash. Originally: GLM-4.6."
      - "CLI-exclusive — NOT routable from Engine provider fabric."
    routing:
      engine_routable: false
      opencode_cli_only: true
      recommended_engine_alternative: "deepseek/deepseek-v4-flash"
    identity_history:
      original: "glm-4.6"
      current: "deepseek-v4-flash"
      swap_detected: true
      last_verified: "2026-06-10"
```

#### 4. Research Model Profiles (`config/research/model_profiles.yaml`)
```yaml
profiles:
  gemma_4_31b:
    context_window: 256000
    reasoning_depth: iterative
    tool_fidelity: medium
    guardrails: [...]
    failure_signature: "shallow"
    shadow_focus: "force_deepening"
  
  deepseek_v4_flash:
    context_window: 32000
    reasoning_depth: deep
    tool_fidelity: high
    failure_signature: "over_analysis"
    shadow_focus: "force_persistence"
  
  claude_4_sonnet:
    context_window: 100000
    reasoning_depth: fast
    tool_fidelity: medium
    failure_signature: "tool_drift"
    shadow_focus: "verify_tool_use"
```

#### 5. Research Protocol (`R_MODEL_RESEARCH_PROTOCOL.md`)
- Model-adaptive protocol with 4 phases
- Shadow Protocol for catching 5 failure patterns
- File persistence verification
- Multi-agent orchestration templates

### What's New (Model Study KB)

| Component | Format | Content |
|-----------|--------|---------|
| `MODEL_STUDY_KNOWLEDGE_BASE.md` | Markdown | 12 models, 5 synergy patterns, decision framework, token economics |
| `model_study.db` | SQLite | 12 models, 2 test runs, 33 results, 12 findings, 5 synergies |
| `query_model_study.py` | Python CLI | Query interface for all data |

---

## 🎯 INTEGRATION ARCHITECTURE: HYBRID MODEL REGISTRY

### Design Principles (from Research)

1. **Model Cards as Source of Truth** — Hugging Face standard: YAML frontmatter + Markdown body
2. **Registry as Contract, Not Catalog** — Immutable versions, lineage, promotion gates (Resilio Tech)
3. **DB as Queryable Index** — Not the source; derived from model cards
4. **Unified Schema** — Merge provider config, research profiles, empirical KB

### Proposed File Structure

```
config/
├── model_registry/                    # NEW: Unified model registry
│   ├── models/                        # Model cards (one per model)
│   │   ├── cloud/
│   │   │   ├── claude-sonnet-5-high-thinking.yaml.md
│   │   │   ├── claude-haiku-4.5-extended.yaml.md
│   │   │   ├── grok-4.3-web.yaml.md
│   │   │   ├── gemini-3-pro-web.yaml.md
│   │   │   ├── gemma-4-31b-it-free.yaml.md
│   │   │   ├── deepseek-v4-flash-free.yaml.md
│   │   │   ├── minimax-m2.5-free.yaml.md
│   │   │   ├── nemotron-3-super-free.yaml.md
│   │   │   └── ...
│   │   ├── local/
│   │   │   ├── qwen3-1.7b-local.yaml.md
│   │   │   ├── qwen3-4b-thinking-local.yaml.md
│   │   │   ├── krikri-8b-local.yaml.md
│   │   │   ├── deepseek-r1-qwen3-8b-local.yaml.md
│   │   │   └── ...
│   │   ├── cli/
│   │   │   ├── john-carmack-opencode.yaml.md
│   │   │   ├── kali-maat-lilith-opencode.yaml.md
│   │   │   └── ...
│   │   └── stealth/
│   │       └── big-pickle-deepseek-v4.yaml.md
│   ├── providers/                     # Provider configs (existing)
│   │   ├── native-gguf.yaml
│   │   ├── lmster.yaml
│   │   ├── ollama.yaml
│   │   ├── antigravity.yaml
│   │   ├── google.yaml
│   │   ├── openrouter.yaml
│   │   ├── opencode-zen.yaml
│   │   ├── cline.yaml
│   │   └── ...
│   ├── research_profiles/             # Research profiles (existing)
│   │   ├── claude-sonnet-5.yaml
│   │   ├── claude-haiku-4.5.yaml
│   │   ├── grok-4.3.yaml
│   │   ├── gemini-3-pro.yaml
│   │   ├── gemma-4-31b.yaml
│   │   ├── deepseek-v4-flash.yaml
│   │   └── default.yaml
│   ├── model_db/                      # MIGRATED from docs/research/model_db/
│   │   ├── CURRENT_MODELS.md
│   │   ├── LEGACY_CROSS_REFERENCE_REPORT.md
│   │   ├── .last_state.json
│   │   └── index.sqlite               # Queryable index (derived)
│   ├── registry.yaml                  # Registry metadata & version
│   └── index.sqlite                   # Master queryable index (derived)
```

### Model Card Schema (YAML Frontmatter + Markdown)

```yaml
---
# === CORE IDENTITY ===
model_id: "google/gemma-4-31b-it:free"
display_name: "Gemma 4 31B IT (Free)"
version: "2026-05-17"
provider: "openrouter"
platform: "cloud"
tier: "T3"  # T1=reflex, T2=balanced, T3=reasoning
status: "active"  # active, deprecated, experimental, stealth

# === CAPABILITIES (from Model Card Library) ===
context_window: 262144
capabilities:
  reasoning: 0.92
  code_generation: 0.88
  knowledge: 0.96
  creative: 0.85
  tool_use: false
  structured_output: false

# === ECONOMICS (from Model Card Library) ===
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 4200
uptime_percent: 98.5

# === ROUTING (from Model Card Library) ===
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null

# === IDENTITY (from Model Card Library) ===
identity_history: null  # For stealth models like big-pickle

# === COMMUNITY INTELLIGENCE (from Model Card Library) ===
community_rating: "4.8/5.0"
community_notes:
  - "State-of-the-art reasoning for zero cost."
  - "Watch daily quota resets (00:00 UTC)."

# === LIVE API STATE (from .last_state.json) ===
live_api_state:
  source: "openrouter"
  last_verified: "2026-05-17"
  last_verified_free: "2026-05-17"

# === RESEARCH PROFILE (from model_profiles.yaml) ===
research_profile:
  reasoning_depth: "iterative"
  tool_fidelity: "medium"
  failure_signature: "shallow"
  shadow_focus: "force_deepening"
  guardrails:
    - "Force 3+ tool rounds before ANY synthesis"
    - "Require explicit 'deepen' pass after first draft"
    - "Write intermediate evidence to disk every 3 tool calls"

# === EMPIRICAL EVIDENCE (from Model Study KB) ===
empirical_evidence:
  test_runs: []  # Populated when model participates in split tests
  synergies: []

# === PROVIDER FABRIC INTEGRATION ===
provider_fabric:
  available_via:
    - provider: "openrouter"
      priority: 4
    - provider: "google"
      priority: 4
  local_first_priority: null

# === METADATA ===
tags:
  - "reasoning"
  - "knowledge"
  - "free_tier"
  - "openrouter"
  - "gemma_4"
created_at: "2026-05-17"
updated_at: "2026-07-18"
schema_version: "1.0.0"
---

# Gemma 4 31B IT (Free) — Model Card

## Overview
Google's Gemma 4 31B instruction-tuned model. Available free via OpenRouter.
State-of-the-art reasoning for zero cost. 262K context window.

## Intended Use
- **Primary**: Deep reasoning, knowledge retrieval, complex synthesis
- **Secondary**: Code generation, multi-step logic
- **Avoid**: Creative writing, real-time interaction (latency ~4.2s)

## Cognitive Mode: Iterative Reasoning
Strong synthesis but needs forcing to deepen. 256K context allows holding
full evidence sets. Guardrails required to prevent shallow single-pass research.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 |
| Latency (P99) | 4,200ms |
| Uptime | 98.5% |
| Community Rating | 4.8/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Shallow Research Tendency**: Context wealth creates illusion of depth; model summarizes instead of deepens
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC
3. **Tool Fidelity**: Medium — drifts on >5 step chains

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Force 3+ tool rounds before ANY synthesis"
  - "Require explicit 'deepen' pass after first draft"
  - "Write intermediate evidence to disk every 3 tool calls"
```

## Provider Access
Available via OpenRouter (priority 4) and Google AI Studio (priority 4).
Not available via local provider fabric (cloud-only model).
```

### Model Card Schema (YAML Frontmatter + Markdown)

```yaml
---
# === CORE IDENTITY ===
model_id: "claude-sonnet-5-high-thinking"
display_name: "Claude Sonnet 5 (High Thinking)"
version: "2026-06-30"
provider: "anthropic"
platform: "web"
tier: "web"
status: "active"  # active, deprecated, experimental

# === CAPABILITIES ===
context_window: 1000000
max_output_tokens: 128000
reasoning_mode: "high_thinking"  # high_thinking, default, extended
cognitive_modes:
  - deep_diagnostic_reasoning
  - root_cause_analysis
  - surgical_bug_finding
  - honest_estimation
  - internal_simulation
weaknesses:
  - memory_contamination_risk
  - lower_output_token_budget
  - no_filesystem_access
  - no_web_search_in_projects

# === ECONOMICS ===
pricing:
  input_per_mtok: 3.0
  output_per_mtok: 15.0
  cached_input_per_mtok: 0.30
  batch_discount: 0.50
  intro_pricing:
    input_per_mtok: 2.0
    output_per_mtok: 10.0
    valid_until: "2026-08-31"
free_tier:
  allocation: "high"
  model_specific: true

# === RESEARCH PROFILE (from model_profiles.yaml) ===
research_profile:
  reasoning_depth: "deep"
  tool_fidelity: "medium"
  failure_signature: "tool_drift"
  shadow_focus: "verify_tool_use"
  guardrails:
    - "Use structured output templates"
    - "Verify tool output within 1 step"
    - "Split long chains into 5-step batches"

# === EMPIRICAL EVIDENCE (from Model Study KB) ===
empirical_evidence:
  test_runs:
    - test_id: "context-packer-split-test-2026-07-18"
      role: "diagnostician"
      output_files: 1
      total_lines: 860
      p0_bugs_found: 4
      p1_bugs_found: 2
      p2_bugs_found: 2
      memory_contamination: true
      contamination_details: "Gemini CLI referenced 9x from saved memories"
      hit_usage_limit: false
      cognitive_mode: "deep_diagnostic"
    - test_id: "decision-tools-dual-review-2026-07-19"
      role: "architectural_reasoner"
      convergence_load_bearing: "7/7"
      asymmetric_catches: ["idempotency", "id_allocator_race", "cycle_detection", "validate_command"]
      divergence: 1
      time_seconds: 155
      quality_score: "9.5/10"

# === SYNERGIES ===
synergies:
  - pattern: "Diagnostic + Documentation Factory"
    partner: "claude-haiku-4.5-extended"
    confidence: 0.95
    use_case: "Bug audit → remediation docs → test suites"
  - pattern: "Architectural + Empirical Convergence"
    partner: "grok-4.3-web"
    confidence: 0.98
    use_case: "Implementation review"
  - pattern: "Consolidator + Diagnostic + Factory Triad"
    partners: ["john-carmack-opencode", "claude-haiku-4.5-extended"]
    confidence: 0.92
    use_case: "Full sprint: roadmap → audit → artifacts"

# === PROVIDER FABRIC INTEGRATION ===
provider_fabric:
  available_via:
    - provider: "opencode-zen"
      priority: 5
    - provider: "cline"
      priority: 6
  local_first_priority: null  # Cloud-only model

# === METADATA ===
tags:
  - "diagnostic"
  - "high_thinking"
  - "web"
  - "anthropic"
  - "sonnet_5"
created_at: "2026-06-30"
updated_at: "2026-07-18"
schema_version: "1.0.0"
---

# Claude Sonnet 5 (High Thinking) — Model Card

## Overview
Claude Sonnet 5 with High Thinking mode enabled. Released June 30, 2026. 
The flagship model for deep diagnostic reasoning tasks.

## Intended Use
- **Primary**: Deep diagnostic audits, root cause analysis, surgical bug finding
- **Secondary**: Architecture review, honest estimation, internal simulation
- **Avoid**: High-volume generation, tasks requiring filesystem access

## Cognitive Mode: Deep Diagnostic Reasoning
Internal simulation of execution paths. Reads artifacts, traces root causes, 
produces surgical patches. Not a documentation factory.

## Empirical Performance
### Context Packer Split Test (2026-07-18)
- **Role**: Diagnostician
- **Output**: 1 file, 860 lines
- **P0 Bugs Found**: 4 (PII offset corruption, consolidation overwrite, signature gap, bare except)
- **P1 Bugs Found**: 2 (hardcoded paths, injection scanner)
- **P2 Bugs Found**: 2 (unimplemented profiles, profile count)
- **Memory Contamination**: YES — 9 references to "Gemini CLI" from saved conversations
- **Usage Limit**: Not hit

### Decision Tools Dual Review (2026-07-19)
- **Role**: Architectural Reasoner (with Grok CLI)
- **Convergence**: 7/7 load-bearing decisions
- **Asymmetric Catches**: atomicwrites dead, portalocker version, Draft202012Validator
- **Quality Score**: 9.5/10 (Kali assessment)

## Known Issues
1. **Memory Contamination**: Web Claude accounts with saved conversations inject 
   platform-specific assumptions (e.g., Gemini CLI references despite sunset)
   - Mitigation: Use fresh accounts for reviews; explicit "ignore memory" instruction

2. **Output Token Budget**: Lower than Haiku Extended; not suited for high-volume generation

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Diagnostic + Documentation Factory | Haiku 4.5 Extended | 95% | Bug audit → remediation docs |
| Architectural + Empirical Convergence | Grok 4.3 Web | 98% | Implementation review |
| Consolidator + Diagnostic + Factory Triad | Carmack + Haiku | 92% | Full sprint orchestration |

## Token Economics (2026)
| Metric | Value |
|--------|-------|
| Input | $3.00/MTok (intro $2.00 through Aug 31) |
| Output | $15.00/MTok (intro $10.00 through Aug 31) |
| Cached Input | $0.30/MTok (90% discount) |
| Batch API | 50% discount |
| Free Tier | Higher allocation (flagship) |

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: medium
failure_signature: tool_drift
shadow_focus: verify_tool_use
guardrails:
  - "Use structured output templates"
  - "Verify tool output within 1 step"
  - "Split long chains into 5-step batches"
```

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6).
Not available via local provider fabric (cloud-only model).
```

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Create Model Registry Structure (1-2 hours)
```bash
mkdir -p config/model_registry/{models,providers,research_profiles}
```

### Phase 2: Migrate Existing Configs (2-3 hours)
1. Split `config/providers.yaml` → individual provider files
2. Split `config/models.yaml` → local model cards
3. Split `config/research/model_profiles.yaml` → research profile files
4. Create model cards for all 12 models from Model Study KB

### Phase 3: Build Registry Service (3-4 hours)
```python
# src/omega/model_registry/
# ├── __init__.py
# ├── models.py           # ModelCard dataclass + loading
# ├── providers.py        # ProviderConfig dataclass + loading
# ├── research.py         # ResearchProfile dataclass + loading
# ├── registry.py         # ModelRegistry service
# ├── indexer.py          # SQLite index builder
# └── query.py            # Query interface (extends query_model_study.py)
```

### Phase 4: Index Builder (1-2 hours)
```python
# Builds SQLite index from model cards
# Runs on registry change (git hook or CI)
# Provides: fast queries, filtering, joins
```

### Phase 5: Integration Points (2-3 hours)
1. **Provider Fabric** → reads from registry for fallback chain
2. **Research Protocol** → loads research profiles from registry
3. **Model Gateway** → queries registry for model capabilities
4. **Context Packer** → uses empirical evidence for platform tuning
5. **Agent Dispatch** → uses synergy patterns for model selection

---

## 📊 SCHEMA UNIFICATION MAPPING

| Field | Provider Fabric | Research Profiles | Model Card Library | Model Study KB | Unified Schema |
|-------|-----------------|-------------------|-------------------|----------------|----------------|
| Model ID | `qwen3-1.7b` | N/A | `google/gemma-4-31b-it:free` | `qwen3-1.7b-local` | `model_id` (namespaced) |
| Provider | `native-gguf` | N/A | `openrouter` | `antigravity` | `provider` |
| Platform | N/A | N/A | `cloud`/`local`/`cli` | `local`/`web`/`cli` | `platform` |
| Tier | N/A | N/A | `T1`/`T2`/`T3` | `local`/`web`/`cli` | `tier` |
| Context Window | `context_window` | `context_window` | `context_window` | `context_window` | `context_window` |
| Pricing | N/A | N/A | `cost_per_1k_tokens_usd` | `pricing` | `pricing` |
| Capabilities | N/A | N/A | `capabilities.*` (reasoning, code, knowledge, creative) | `cognitive_modes` | `capabilities` + `cognitive_modes` |
| Reasoning Depth | N/A | `reasoning_depth` | N/A | `cognitive_modes` | `reasoning_depth` + `cognitive_modes` |
| Failure Signature | N/A | `failure_signature` | N/A | `empirical_evidence` | `failure_signature` + `empirical_evidence` |
| Guardrails | N/A | `guardrails` | N/A | N/A | `guardrails` |
| Synergies | N/A | N/A | N/A | `synergies` | `synergies` |
| Test Evidence | N/A | N/A | N/A | `test_runs` | `empirical_evidence.test_runs` |
| Routing Rules | N/A | N/A | `routing.*` | N/A | `routing` |
| Identity History | N/A | N/A | `identity_history` | N/A | `identity_history` |
| Community Intelligence | N/A | N/A | `community_rating`, `community_notes` | N/A | `community_intelligence` |
| Live API State | N/A | N/A | `.last_state.json` | N/A | `live_api_state` |

---

## 🎯 DECISION MATRIX: WHY HYBRID?

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **File-only (YAML/MD)** | Git-native, human-readable, diffable | Slow queries, no joins, no aggregation | ❌ Insufficient alone |
| **DB-only (SQLite)** | Fast queries, joins, aggregation | Not git-friendly, opaque, hard to review | ❌ Insufficient alone |
| **Hybrid (Files + DB Index)** | Best of both: source control + query power | Slight complexity (sync) | ✅ **CHOSEN** |

**Sync Strategy**: DB is **derived artifact** — rebuilt from files on demand (git hook, CI, or manual `make model-index`). Files are source of truth.

---

## 🔄 MIGRATION CHECKLIST

### Immediate (This Sprint)
- [ ] Create `config/model_registry/` directory structure
- [ ] Write model card template (`model_card_template.yaml.md`)
- [ ] Create 12 model cards from Model Study KB
- [ ] Split existing `providers.yaml` → individual provider files
- [ ] Split existing `model_profiles.yaml` → individual research profile files
- [ ] Build `ModelRegistry` service with loading + indexing
- [ ] Add `make model-index` target

### Short-term (Next Sprint)
- [ ] Integrate Provider Fabric to read from registry
- [ ] Integrate Research Protocol to load profiles from registry
- [ ] Add model card validation (schema check)
- [ ] Add CI gate: `make model-validate`
- [ ] Extend `query_model_study.py` → `model_registry_query.py`

### Medium-term (Horizon 1)
- [ ] Add model versioning (immutable versions, mutable aliases)
- [ ] Add promotion workflow (staging → canary → production)
- [ ] Add lineage tracking (code commit → model version)
- [ ] Add rollback capability
- [ ] Integrate with Hugging Face Hub format for local models

---

## 📋 FILES TO CREATE

| File | Purpose |
|------|---------|
| `config/model_registry/registry.yaml` | Registry metadata, version, schema |
| `config/model_registry/model_card_template.yaml.md` | Template for new model cards |
| `config/model_registry/models/*.yaml.md` | 12 model cards |
| `config/model_registry/providers/*.yaml` | Provider configs |
| `config/model_registry/research_profiles/*.yaml` | Research profiles |
| `src/omega/model_registry/__init__.py` | Package exports |
| `src/omega/model_registry/models.py` | ModelCard dataclass, loader, validator |
| `src/omega/model_registry/providers.py` | ProviderConfig dataclass, loader |
| `src/omega/model_registry/research.py` | ResearchProfile dataclass, loader |
| `src/omega/model_registry/registry.py` | ModelRegistry service |
| `src/omega/model_registry/indexer.py` | SQLite index builder |
| `src/omega/model_registry/query.py` | Query interface |
| `scripts/model_registry_validate.py` | Validation script for CI |
| `Makefile` additions | `model-index`, `model-validate` targets |

---

## 🧪 VALIDATION GATES

```python
# Temple-Grade gates for model registry
GATES = {
    "SCHEMA_VALID": "All model cards validate against schema",
    "NO_DUPLICATES": "Unique model_id across registry",
    "PROVIDER_CHAIN_COMPLETE": "Fallback chain has no gaps",
    "RESEARCH_PROFILES_COMPLETE": "All models in KB have research profile",
    "EMPIRICAL_EVIDENCE_LINKED": "Test runs reference valid test_run_ids",
    "SYNERGIES_BIDIRECTIONAL": "If A references B, B references A",
    "INDEX_SYNC": "SQLite index matches file contents",
    "PROVIDER_FABRIC_COMPATIBLE": "Registry can generate providers.yaml",
}
```

---

*⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY-ARCHITECTURE ⬡ 2026-07-18 ⬡ DECISION: HYBRID FILE+DB*