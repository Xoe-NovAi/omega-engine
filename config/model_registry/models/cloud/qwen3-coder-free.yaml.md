---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: qwen/qwen3-coder:free
display_name: Qwen3 Coder (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 1048576
max_output_tokens: 1048576
capabilities:
  reasoning: 0.88
  code_generation: 0.95
  knowledge: 0.85
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 0.0
free_tier: true
latency_p99_ms: 4000
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- "Specialized for coding \u2014 480B A35B"
- 256K native context, extendable to 1M via YaRN
- 'OpenRouter free tier: 262K context'
- Strong tool use for development
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: over_analysis
  shadow_focus: force_persistence
  guardrails:
  - Verify code against actual execution
  - Use RAG for API documentation
  - Time-box reviews to prevent over-analysis
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- coding
- specialized
- free_tier
- openrouter
- qwen3_coder
created_at: '2026-05-17'
updated_at: '2026-07-18'
schema_version: 1.2.0
parameters:
  temperature: 0.5
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.0
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
  total: Unknown
  active: Unknown
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: Unknown
  training_tokens: Unknown
  source: estimated
  verified: false
---

# Qwen3 Coder (Free) — Model Card

## Overview
Alibaba's Qwen3 Coder. 480B A35B MoE specialized for coding. 256K native context (1M with YaRN). OpenRouter free tier: 262K. Strong tool use for development.

## Intended Use
- **Primary**: Code generation, refactoring, debugging, tool use
- **Secondary**: Technical reasoning, API integration
- **Avoid**: Creative writing, general knowledge

## Cognitive Mode: Code-Specialized Reasoning
Optimized for code generation and technical tasks. Strong tool use for development workflows.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 (OpenRouter) / 256K native (1M with YaRN) |
| Latency (P99) | 4,000ms |
| Uptime | 98.5% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Context Discrepancy**: Native 256K, 1M with YaRN, 262K on OpenRouter free.
2. **Specialized**: Not a generalist.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: over_analysis
shadow_focus: force_persistence
guardrails:
  - "Verify code against actual execution"
  - "Use RAG for API documentation"
  - "Time-box reviews to prevent over-analysis"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
