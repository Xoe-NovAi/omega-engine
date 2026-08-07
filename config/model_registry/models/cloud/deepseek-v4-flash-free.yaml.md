---
model_id: deepseek/deepseek-v4-flash:free
display_name: DeepSeek V4 Flash (Free)
version: '2026-04-24'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 1048576
max_output_tokens: 1048576
capabilities:
  reasoning: 0.94
  code_generation: 0.92
  knowledge: 0.9
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 9.800000000000001e-05
  output_per_mtok: 0.00019600000000000002
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 1.96e-05
free_tier: true
latency_p99_ms: 3500
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.7/5.0
community_notes:
- 284B total / 13B active, 1M context, MIT license
- Released April 24, 2026
- Recommended engine alternative for Big Pickle
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-06-10'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: over_analysis
  shadow_focus: force_persistence
  guardrails:
  - Set explicit scope boundaries upfront
  - Require file references for all claims
  - Time-box reviews to prevent over-analysis
empirical_evidence:
  test_runs: []
  synergies:
  - pattern: Engine Alternative for Big Pickle
    partners:
    - opencode/big-pickle
    confidence: 1.0
    use_case: Engine routing when Big Pickle is CLI-only
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- reasoning
- code_generation
- free_tier
- openrouter
- deepseek_v4
- mit_license
created_at: '2026-04-24'
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
  total: 284B
  active: 13B
  architecture: MoE
  experts: 8
  active_experts: 2
  shared_experts: 0
  quantization: BF16
  training_tokens: 15T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# DeepSeek V4 Flash (Free) — Model Card

## Overview
DeepSeek V4 Flash. 284B total / 13B active parameters. 1M context window. MIT license. Released April 24, 2026. Free on OpenRouter. Recommended engine alternative for Big Pickle.

## Intended Use
- **Primary**: Deep reasoning, code generation, complex synthesis
- **Secondary**: Engine routing alternative for Big Pickle
- **Avoid**: Creative writing, real-time interaction

## Cognitive Mode: Deep Reasoning with Code Focus
Strong reasoning and code generation. 1M context allows massive evidence sets. MIT license enables commercial use.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,048,576 |
| Latency (P99) | 3,500ms |
| Uptime | 99.0% |
| Community Rating | 4.7/5.0 |
| Cost | $0.00 (free tier) |
| License | MIT |

## Known Issues
1. **Over-Analysis Tendency**: Can over-analyze; needs time-boxing.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: over_analysis
shadow_focus: force_persistence
guardrails:
  - "Set explicit scope boundaries upfront"
  - "Require file references for all claims"
  - "Time-box reviews to prevent over-analysis"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Engine Alternative for Big Pickle | Big Pickle | 100% | Engine routing when Big Pickle is CLI-only |

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
