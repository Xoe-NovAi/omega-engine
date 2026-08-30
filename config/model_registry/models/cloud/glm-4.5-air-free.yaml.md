---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: z-ai/glm-4.5-air:free
display_name: GLM 4.5 Air (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 131072
max_output_tokens: 131072
capabilities:
  reasoning: 0.8
  code_generation: 0.78
  knowledge: 0.82
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.00013
  output_per_mtok: 0.0008500000000000001
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 2.4999999999999998e-05
free_tier: true
latency_p99_ms: 2800
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.3/5.0
community_notes:
- "Z.ai's GLM 4.5 Air \u2014 efficient variant"
- 128K context window
- GLM-5 deprecated May 14, 2026
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: medium
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Force 3+ tool rounds before ANY synthesis
  - Require explicit 'deepen' pass after first draft
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- efficient
- free_tier
- openrouter
- glm_4_5
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
  architecture: MoE
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: Unknown
  training_tokens: Unknown
  source: estimated
  verified: false
---

# GLM 4.5 Air (Free) — Model Card

## Overview
Z.ai's GLM 4.5 Air. Efficient variant. 128K context. Free on OpenRouter. GLM-5 deprecated May 14, 2026.

## Intended Use
- **Primary**: Efficient reasoning, balanced workloads
- **Secondary**: Code generation, tool use
- **Avoid**: Maximum-depth reasoning

## Cognitive Mode: Efficient Generalist
Balanced capability with good speed. Replaces deprecated GLM-5.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 2,800ms |
| Uptime | 98.5% |
| Community Rating | 4.3/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **GLM-5 Deprecated**: May 14, 2026 — use 4.5 Air instead.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Force 3+ tool rounds before ANY synthesis"
  - "Require explicit 'deepen' pass after first draft"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
