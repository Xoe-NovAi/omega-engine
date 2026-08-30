---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: nvidia/nemotron-3-super-120b-a12b:free
display_name: Nemotron 3 Super 120B (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.9
  code_generation: 0.88
  knowledge: 0.92
  creative: 0.85
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
latency_p99_ms: 4500
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.5/5.0
community_notes:
- Massive parameter count for free
- 1M context on NVIDIA; 262K on OpenRouter free tier
- Generalist with tool support
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - Verify factual claims against sources
  - Use structured output for tool calls
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- reasoning
- generalist
- tools
- free_tier
- openrouter
- nvidia
- nemotron_3
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
  total: 120B
  active: 12B
  architecture: MoE
  experts: 10
  active_experts: 1
  shared_experts: 0
  quantization: BF16
  training_tokens: 9T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Nemotron 3 Super 120B (Free) — Model Card

## Overview
NVIDIA's Nemotron 3 Super. 120B parameters (12B active). 1M context on NVIDIA; 262K on OpenRouter free tier. Generalist with tool support. Free on OpenRouter.

## Intended Use
- **Primary**: General reasoning, tool use, knowledge tasks
- **Secondary**: Code generation, multi-step logic
- **Avoid**: Creative writing, specialized domains

## Cognitive Mode: Generalist with Tools
Balanced capabilities across reasoning, code, knowledge. Tool support enables agentic workflows.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000 (NVIDIA) / 262,144 (OpenRouter free) |
| Latency (P99) | 4,500ms |
| Uptime | 98.5% |
| Community Rating | 4.5/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Context Discrepancy**: 1M on NVIDIA, 262K on OpenRouter free.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify factual claims against sources"
  - "Use structured output for tool calls"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
