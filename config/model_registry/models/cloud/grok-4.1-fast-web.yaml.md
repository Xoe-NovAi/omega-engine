---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: xai/grok-4.1-fast-web
display_name: Grok 4.1 Fast (Web)
version: '2026-06-20'
provider: xai
platform: cloud
tier: T2
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.75
  code_generation: 0.7
  knowledge: 0.8
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: true
  realtime_search: true
  code_execution: false
  parallel_search: true
  workspace_integration: false
pricing:
  input_per_mtok: 0.00125
  output_per_mtok: 0.0025
  cached_input_per_mtok: 0.00019999999999999998
  batch_discount: null
  cost_per_1k_tokens_usd: 0.000375
free_tier: true
latency_p99_ms: 2000
uptime_percent: 99.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.2/5.0
community_notes:
- 10x cheaper than Grok 4.3
- 2M context window
- "Lower reasoning quality \u2014 bulk processing, high-throughput review"
- Real-time X search available
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: fast
  tool_fidelity: medium
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Use for bulk processing, not deep reasoning
  - Verify critical claims with Grok 4.3 or Sonnet
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: opencode-zen
    priority: 5
  - provider: cline
    priority: 6
  local_first_priority: null
tags:
- high_throughput
- bulk_processing
- realtime_search
- web
- xai
- grok_4_1
created_at: '2026-06-20'
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

# Grok 4.1 Fast (Web) — Model Card

## Overview
xAI's Grok 4.1 Fast web interface. 2M context, 10x cheaper than Grok 4.3. High-volume, latency-sensitive. Lower reasoning quality.

## Intended Use
- **Primary**: Bulk processing, high-throughput review, large-context synthesis
- **Secondary**: Cost-sensitive real-time search
- **Avoid**: Deep diagnostic reasoning, architectural review

## Cognitive Mode: High-Volume Fast Processing
Lower reasoning quality but massive context and low cost. Good for bulk tasks where depth isn't critical.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 2,000,000 |
| Max Output | 200,000 |
| Latency (P99) | 2,000ms |
| Uptime | 99.5% |
| Community Rating | 4.2/5.0 |
| Cost | $0.125/$0.25 per 1M tokens |
| Free Tier | Yes |

## Known Issues
1. **Lower Reasoning**: Not for diagnostic or architectural tasks.
2. **Format**: XML+MD hybrid like 4.3.

## Research Profile
```yaml
reasoning_depth: fast
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Use for bulk processing, not deep reasoning"
  - "Verify critical claims with Grok 4.3 or Sonnet"
```

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6). Engine-routable.
