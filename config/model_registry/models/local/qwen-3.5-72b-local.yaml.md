---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: qwen-3.5-72b-local
display_name: Qwen 3.5 72B (Local)
version: '2026-06-15'
provider: native-gguf
platform: local
tier: T3
status: active
context_window: 128000
max_output_tokens: 32000
capabilities:
  reasoning: 0.85
  code_generation: 0.92
  knowledge: 0.88
  creative: 0.82
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cached_input_per_mtok: 0.0
  batch_discount: null
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 6000
uptime_percent: 100.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- Strong coding, multilingual
- Requires 24GB+ RAM
- Good local development model
- Better coding than Llama 4 Scout
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - Verify code against actual execution
  - Use RAG for API documentation
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: native-gguf
    priority: 0
  - provider: ollama
    priority: 1
  - provider: ollama
    priority: 2
  local_first_priority: 0
tags:
- coding
- multilingual
- local
- development
- native_gguf
- qwen
created_at: '2026-06-15'
updated_at: '2026-07-18'
schema_version: 1.2.0
parameters:
  temperature: 0.5
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.0
  max_tokens: 8192
  stop_sequences: []
  presence_penalty: 0.0
  frequency_penalty: 0.0
benchmark_sources:
  reasoning: ''
  code_generation: ''
  knowledge: ''
  creative: ''
  tool_use: ''
  structured_output: ''
  multimodal: ''
  overall: ''
architecture:
  total: 72B
  active: 72B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: INT4
  training_tokens: Unknown
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Qwen 3.5 72B (Local) — Model Card

## Overview
Alibaba's Qwen 3.5 72B. 128K context. Strong coding, multilingual. Requires 24GB+ RAM. Excellent for local development.

## Intended Use
- **Primary**: Local development, coding tasks, multilingual work
- **Secondary**: Sovereign deployment for coding-heavy workloads
- **Avoid**: Massive context synthesis (use Llama 4 Scout)

## Cognitive Mode: Local Development Specialist
Optimized for coding and multilingual tasks. Strong tool use for development workflows.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 128,000 |
| Max Output | 32,000 |
| Latency (P99) | 6,000ms |
| Uptime | 100% (local) |
| Community Rating | 4.6/5.0 |
| Cost | $0/token |
| Hardware | 24GB+ RAM |

## Known Issues
1. **Hardware**: 24GB+ RAM required.
2. **Context**: 128K vs Llama 4 Scout's 10M.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify code against actual execution"
  - "Use RAG for API documentation"
```

## Provider Access
Local-first via native-gguf (priority 0), LM Studio (priority 1), Ollama (priority 2). Engine-routable.
