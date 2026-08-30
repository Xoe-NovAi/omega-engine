---
model_id: liquid/lfm-2.5-1.2b-instruct:free
display_name: LFM 2.5 1.2B Instruct (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T1
status: active
context_window: 32768
max_output_tokens: 8192
capabilities:
  reasoning: 0.6
  code_generation: 0.55
  knowledge: 0.65
  creative: 0.6
  tool_use: false
  structured_output: false
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 500
uptime_percent: 99.8
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 3.8/5.0
community_notes:
- "Liquid AI's LFM 2.5 \u2014 1.2B"
- 32K context window
- Ultra-fast reflex
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: reflex
  tool_fidelity: low
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Do NOT use for reasoning
  - Use for ultra-fast classification only
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- ultra_fast
- reflex
- free_tier
- openrouter
- liquid_ai
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
  total: 1.2B
  active: 1.2B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: Unknown
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# LFM 2.5 1.2B Instruct (Free) — Model Card

## Overview
Liquid AI's LFM 2.5 1.2B. 32K context. Ultra-fast reflex. Free on OpenRouter.

## Intended Use
- **Primary**: Ultra-fast classification, extraction, simple QA
- **Secondary**: Highest-volume lowest-latency
- **Avoid**: Any reasoning, code generation

## Cognitive Mode: Ultra-Fast Reflex
Sub-500ms latency. Pure reflex. No reasoning capability.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 32,768 |
| Latency (P99) | 500ms |
| Uptime | 99.8% |
| Community Rating | 3.8/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **No Reasoning**: Will fail on any reasoning task.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: reflex
tool_fidelity: low
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Do NOT use for reasoning"
  - "Use for ultra-fast classification only"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
