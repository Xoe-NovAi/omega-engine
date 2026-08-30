---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: arcee-ai/trinity-large-thinking:free
display_name: Trinity Large Thinking (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 262144
max_output_tokens: 262144
capabilities:
  reasoning: 0.92
  code_generation: 0.88
  knowledge: 0.94
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.00025
  output_per_mtok: 0.0007999999999999999
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 5.9999999999999995e-05
free_tier: true
latency_p99_ms: 4500
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.7/5.0
community_notes:
- "Arcee AI's Trinity Large \u2014 thinking mode"
- 262K context window
- Optimized for reasoning
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
  - Time-box reviews to prevent over-analysis
  - Verify claims against source documents
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- thinking
- reasoning
- free_tier
- openrouter
- arcee_ai
- trinity
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

# Trinity Large Thinking (Free) — Model Card

## Overview
Arcee AI's Trinity Large with thinking mode. 262K context. Optimized for reasoning. Free on OpenRouter.

## Intended Use
- **Primary**: Deep reasoning, complex synthesis
- **Secondary**: Code generation, tool use
- **Avoid**: Real-time tasks (latency)

## Cognitive Mode: Thinking Mode Reasoning
Explicit thinking process. 262K context for massive evidence sets.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 262,144 |
| Latency (P99) | 4,500ms |
| Uptime | 98.5% |
| Community Rating | 4.7/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Over-Analysis**: Thinking mode can over-analyze; needs time-boxing.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: over_analysis
shadow_focus: force_persistence
guardrails:
  - "Time-box reviews to prevent over-analysis"
  - "Verify claims against source documents"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
