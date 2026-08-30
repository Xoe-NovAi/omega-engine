---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: openrouter/free
display_name: OpenRouter Free Models Router
version: '2026-06-15'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 2000000
max_output_tokens: 2000000
capabilities:
  reasoning: 0.75
  code_generation: 0.7
  knowledge: 0.8
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: -1000.0
  output_per_mtok: -1000.0
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 0.0
free_tier: true
latency_p99_ms: 3000
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.3/5.0
community_notes:
- Dynamic router across all free models on OpenRouter
- Automatic failover and load balancing
- Best for high availability free tier
- Model varies per request
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-06-15'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: medium
  failure_signature: inconsistent
  shadow_focus: verify_consistency
  guardrails:
  - Expect model variation across requests
  - Verify critical outputs independently
  - Not suitable for reproducible benchmarks
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- router
- high_availability
- free_tier
- openrouter
- dynamic
created_at: '2026-06-15'
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
  total: Variable
  active: Variable
  architecture: router
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: Variable
  training_tokens: Variable
  source: router
  verified: false
---

# OpenRouter Free Models Router — Model Card

## Overview
OpenRouter's dynamic router across all free models. Automatic failover and load balancing. Model varies per request. Best for high availability free tier usage.

## Intended Use
- **Primary**: High availability free tier, automatic failover
- **Secondary**: Load balancing across free models
- **Avoid**: Reproducible benchmarks, tasks requiring consistent model behavior

## Cognitive Mode: Dynamic Routing
Routes to best available free model per request. Inconsistent by design — different models for different requests.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 200,000 (varies) |
| Latency (P99) | 3,000ms |
| Uptime | 99.0% |
| Community Rating | 4.3/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Inconsistency**: Different model per request.
2. **Non-Reproducible**: Cannot reproduce exact results.
3. **Variable Capabilities**: Depends on routed model.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: inconsistent
shadow_focus: verify_consistency
guardrails:
  - "Expect model variation across requests"
  - "Verify critical outputs independently"
  - "Not suitable for reproducible benchmarks"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
