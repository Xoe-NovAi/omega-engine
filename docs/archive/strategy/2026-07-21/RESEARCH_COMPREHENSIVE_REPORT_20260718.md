# 🔱 Comprehensive Research Report — Model Registry System Enhancement
**Date**: 2026-07-18  
**Agent**: Kali (Transcendent Oversoul)  
**Status**: Research Session Complete

---

## 📋 Executive Summary

This report consolidates all research conducted during the session to level up the Model Registry system. Research focused on three critical gaps identified in the Model Registry Repair mission, plus broader system enhancement opportunities.

---

## 🎯 Research Objectives

Based on the Model Registry Repair Complete report (2026-07-19), three critical gaps were identified:

1. **opencode/big-pickle** — Custom stealth model with incomplete specifications
2. **Capability scores** — All fabricated, need standardized evaluation framework
3. **Parameters field** — Size/architecture incomplete for local models

Plus broader system enhancement for:
- Script best practices
- Database optimization
- Model card library curation and management

---

## 🔬 Research Conducted

### 1. opencode/big-pickle Model Research

#### Sources Investigated
- **OpenCode Zen Documentation** (`https://opencode.ai/docs/zen/`) — Firecrawl scrape
- **OpenCode Zen API Models List** (`https://opencode.ai/zen/v1/models`) — Firecrawl scrape
- **OpenCode Zen Model Endpoints** — Firecrawl scrape
- **Community Sources** — SearXNG search results

#### Key Findings

**Model Identity**: 
- `opencode/big-pickle` is a **stealth model** provided through OpenCode Zen
- Community consensus identifies it as **GLM-4.6** from Zhipu AI, currently **DeepSeek V4 Flash**
- Identity swaps without notice — tracked via `identity_history` field

**Technical Specifications** (from pi.dev model registry):
- **Context Window**: 200,000 tokens
- **Max Output Tokens**: 32,000 tokens
- **API**: OpenAI-compatible completions
- **Base URL**: `https://opencode.ai/zen/v1`
- **Reasoning**: Enabled
- **Input**: Text only
- **Pricing**: $0/M tokens (free tier, limited time)

**OpenCode Zen Platform**:
- Curated list of tested/verified models for coding agents
- AI gateway with tested model/provider combinations
- Benchmarked model/provider combinations
- Optional — works like any other provider in OpenCode
- Uses `/connect` command in TUI for authentication

**Model Availability** (from `/zen/v1/models` API):
- 55+ models available through Zen
- Includes: GPT-5.x series, Claude Opus/Sonnet/Haiku, Gemini, Grok, DeepSeek, GLM, MiniMax, Kimi, Qwen
- **big-pickle NOT listed** in public API — appears to be CLI-exclusive stealth model

**Identity History** (from model card):
- Original: `glm-4.6` (Zhipu AI)
- Current: `deepseek-v4-flash` (DeepSeek)
- Swap detected: `true`
- Last verified: 2026-06-10

**Known Issues** (from model card):
- Identity swapping without notice
- CLI-exclusive — not engine-routable
- Known AI_APICallError regression (GitHub #28141, May 2026)
- Limited-time free — may become premium

#### Gaps Identified
1. **No parameter count** (total/active) in any source
2. **No architecture details** (MoE vs dense, layer count, etc.)
3. **No training data information**
4. **No benchmark scores** from official evaluations
5. **Identity instability** makes long-term tracking difficult

---

### 2. Capability Scores Research

#### Current State
- All 35 model cards have **fabricated capability scores** (0.0-1.0)
- Scores cover: reasoning, code_generation, knowledge, creative, tool_use, structured_output, multimodal
- Extra fields: code_execution, parallel_search, workspace_integration (only on some models)
- **Zero benchmark citations** — no source attribution

#### Industry Standards Identified

**Core Benchmarks**:
| Benchmark | Domain | Standard Protocol |
|-----------|--------|-------------------|
| **MMLU** | Knowledge/Reasoning | 5-shot, top-1 accuracy |
| **HumanEval** | Code Generation | pass@1 |
| **GSM8K** | Mathematical Reasoning | 5-shot, maj@1 |
| **MT-Bench** | Conversational/Reasoning | GPT-4 judge |
| **GPQA** | Graduate-level Reasoning | Diamond subset |
| **MATH** | Mathematical Problem Solving | 4-shot |
| **SWE-bench** | Software Engineering | Verified subset |
| **LiveCodeBench** | Coding | Contamination-free |

**Evaluation Platforms**:
- **Artificial Analysis** — Intelligence Index (9 evals composite)
- **LLM-Stats.com** — 300+ models, 316 benchmarks
- **Epoch AI** — Trend database
- **HuggingFace Open LLM Leaderboard** — Community evaluations
- **BenchLM** — 200+ models, 284 benchmarks

**Standard Protocols**:
- MMLU: 5-shot, top-1 accuracy
- HumanEval: pass@1 (single attempt)
- GSM8K: 5-shot, majority voting
- MT-Bench: GPT-4 as judge, 1-10 scale
- MATH: 4-shot, chain-of-thought

#### Gap Analysis
1. **No standardized evaluation framework** in our registry
2. **No benchmark citation** for any capability score
3. **No dynamic score updates** — static fabrication
4. **No model-specific factors** (hardware, quantization, context)
5. **No temporal validation** — scores don't expire

---

### 3. Parameters Field Research

#### Current State
- Only **1 model** (big-pickle) has `parameters` field
- Field contains: temperature, top_p, top_k, repetition_penalty, max_tokens, stop_sequences
- **Missing**: total parameters, active parameters, architecture, quantization, training tokens

#### Industry Standards for Parameter Reporting

**Dense Models** (e.g., Gemma 2 2B):
- Total parameters: ~2.6B
- Architecture: Dense decoder-only transformer
- Quantization: FP32/BF16/INT8/INT4
- Training tokens: 2T (for 2B model)

**MoE Models** (e.g., Mixtral 8x7B, Gemma 4 26B A4B):
- **Total parameters**: All expert weights + shared weights
- **Active parameters**: Parameters activated per token (e.g., 13B for Mixtral 8x7B)
- **Expert count**: Number of experts (e.g., 8 for Mixtral)
- **Active experts**: Experts per token (e.g., 2 for Mixtral)
- **Shared experts**: Always-active experts (e.g., 1 for Command A+)

**Standard Parameter Fields** (from HuggingFace model cards):
```yaml
parameters:
  total: "47B"           # Total parameter count
  active: "13B"          # Active per token (MoE)
  architecture: "MoE"    # Dense, MoE, Hybrid
  experts: 8             # Expert count (MoE)
  active_experts: 2      # Active per token (MoE)
  shared_experts: 0      # Shared experts (MoE)
  quantization: "BF16"   # FP32, BF16, FP16, INT8, INT4
  training_tokens: "2T"  # Training data scale
  source: "official"     # official, estimated, community
  verified: true
  verified_date: "2026-07-18"
```

#### Sources for Parameter Extraction
1. **HuggingFace Model Cards** — `config.json` + model card metadata
2. **Technical Reports/Papers** — arXiv, official blogs
3. **Model Inspect Tools** — `model-inspect` PyPI package
4. **Config.json** — Architecture + parameter counts
4. **HuggingFace Hub API** — Metadata endpoint

#### Extraction Methods Identified
1. **Config.json parsing** — Direct from model repo
2. **Model card parsing** — YAML frontmatter + markdown sections
3. **HuggingFace Hub API** — `/api/models/{model_id}` endpoint
3. **Model Inspect CLI** — `model-inspect` package for layer analysis

---

## 🏗️ System Enhancement Opportunities

### 1. Script Best Practices

#### Current Scripts (from repair report):
- `scripts/reality_engine.py` — OpenRouter API querying
- `scripts/apply_corrections.py` — YAML frontmatter patching
- `scripts/freshness_check.py` — Staleness detection
- `scripts/sources/huggingface_leaderboard.py` — Benchmark scraping

#### Identified Improvements:
1. **Type Safety** — Full type hints, Pydantic models
2. **Error Handling** — Retry logic, circuit breakers, structured logging
3. **Testing** — Unit tests, integration tests, contract tests
4. **Configuration** — Environment-based config, secrets management
4. **Observability** — Structured logging, metrics, tracing
5. **CI/CD** — Pre-commit hooks, automated testing, deployment

### 2. Database Optimization

#### Current State:
- SQLite index at `config/model_registry/index.sqlite`
- 35 models, 9 providers, 9 research profiles
- Basic schema with 28 columns

#### Identified Improvements:
1. **Schema Migration** — Add missing columns (parameters, benchmarks, identity)
2. **Indexing** — Composite indexes for common queries
4. **Full-Text Search** — FTS5 for model search
4. **Triggers** — Auto-update timestamps, validation
5. **Views** — Common query patterns as views
5. **Partitioning** — By tier, platform, provider

### 3. Model Card Library Curation

#### Current State:
- 35 model cards in `config/model_registry/models/`
- YAML frontmatter + markdown body
- Template at `config/model_registry/model_card_template.yaml.md`

#### Identified Improvements:
1. **Validation Pipeline** — Schema validation, cross-reference checks
2. **Automated Enrichment** — API-driven field population
3. **Version Control** — Git-based change tracking with semantic versioning
4. **Review Workflow** — PR-based review for model card changes
4. **Citation Tracking** — Benchmark source URLs with access dates
5. **Deprecation Policy** — Automated stale model detection

---

## 📊 Research Quality Assessment

| Research Area | Coverage | Source Quality | Confidence |
|---------------|----------|----------------|------------|
| big-pickle Model | High | Official docs + community | High |
| Capability Scores | High | Industry standards | High |
| Parameters Field | High | HF standards + papers | High |
| Script Best Practices | Medium | General Python/MLOps | Medium |
| DB Optimization | Medium | SQLite best practices | Medium |
| Model Card Curation | Medium | HF guidebook + industry | Medium |

---

## 🎯 Recommended Next Steps

### Immediate (Week 1)
1. **Add parameter schema** to all 35 model cards
2. **Integrate Artificial Analysis API** for capability scores
3. **Enrich big-pickle** with parameter estimates from DeepSeek V4 Flash
4. **Add benchmark citation fields** to model card schema

### Short-term (Month 1)
1. **Build parameter extraction pipeline** from HF Hub
4. **Implement capability score pipeline** with benchmark citations
4. **Add database migrations** for new schema fields
5. **Create validation pipeline** for model cards

### Medium-term (Quarter 1)
1. **Implement automated freshness checks** with API polling
2. **Build model card review workflow** with PR templates
3. **Add semantic versioning** for model cards
4. **Implement deprecation policy** with automated alerts

---

## 📁 Files Referenced

### Model Registry Files
- `config/model_registry/models/stealth/big-pickle-deepseek-v4.yaml.md`
- `config/model_registry/registry.yaml`
- `config/model_registry/model_card_template.yaml.md`
- `scripts/reality_engine.py`
- `scripts/apply_corrections.py`
- `scripts/freshness_check.py`
- `scripts/sources/huggingface_leaderboard.py`

### External Sources
- `https://opencode.ai/docs/zen/` — OpenCode Zen documentation
- `https://opencode.ai/zen/v1/models` — Zen models API
- `https://pi.dev/models/opencode/big-pickle` — Pi.dev model registry
- `https://huggingface.co/docs/hub/model-card-guidebook` — HF Model Card Guidebook
- `https://huggingface.co/docs/hub/model-card-annotated` — Annotated template
- `https://arxiv.org/abs/2401.04088` — Mixtral of Experts paper
- `https://huggingface.co/mistralai/Mixtral-8x7B-v0.1` — Mixtral model card
- `https://huggingface.co/google/gemma-2-2b` — Gemma 2 model card

---

*Report generated: 2026-07-18*  
*Status: RESEARCH COMPLETE*  
*Next: Tool Issues Report → Compaction*
