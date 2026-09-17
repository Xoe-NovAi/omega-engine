---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: nvidia/nemotron-3-nano-30b-a3b:free
display_name: Nemotron 3 Nano 30B A3B (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 256000
max_output_tokens: 256000
capabilities:
  reasoning: 0.82
  code_generation: 0.8
  knowledge: 0.85
  creative: 0.78
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
latency_p99_ms: 2800
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.3/5.0
community_notes:
- "NVIDIA's Nemotron 3 Nano \u2014 30B A3B MoE"
- 256K context window
- Efficient MoE architecture
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
- moe
- efficient
- free_tier
- openrouter
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
  total: 30B
  active: 3B
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

# Nemotron 3 Nano 30B A3B (Free) — Model Card

## Overview
NVIDIA's Nemotron 3 Nano. 30B A3B MoE. 256K context. Efficient MoE architecture. Free on OpenRouter.

## Intended Use
- **Primary**: Efficient reasoning, balanced workloads
- **Secondary**: Code generation, tool use
- **Avoid**: Maximum-depth reasoning (use Super 120B)

## Cognitive Mode: Efficient Iterative Reasoning
MoE architecture gives good capability per parameter. 256K context for large evidence sets.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 256,000 |
| Latency (P99) | 2,800ms |
| Uptime | 99.0% |
| Community Rating | 4.3/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **MoE Routing**: Can have routing instability.
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
