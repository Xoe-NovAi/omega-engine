---
model_id: nvidia/nemotron-nano-12b-v2-vl:free
display_name: Nemotron Nano 12B V2 VL (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 128000
max_output_tokens: 128000
capabilities:
  reasoning: 0.75
  code_generation: 0.72
  knowledge: 0.8
  creative: 0.72
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
  cached_input_per_mtok: 0.0
free_tier: true
latency_p99_ms: 2000
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.1/5.0
community_notes:
- "NVIDIA's Nemotron Nano 12B V2 \u2014 Vision-Language"
- 128K context window
- Multimodal capability
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: fast
  tool_fidelity: medium
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Use for multimodal fast tasks
  - Do NOT use for deep reasoning
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- multimodal
- fast
- vision_language
- free_tier
- openrouter
- nemotron_nano
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
  total: 12B
  active: 12B
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

# Nemotron Nano 12B V2 VL (Free) — Model Card

## Overview
NVIDIA's Nemotron Nano 12B V2 Vision-Language. 128K context. Multimodal. Free on OpenRouter.

## Intended Use
- **Primary**: Multimodal fast tasks, vision + language
- **Secondary**: Fast classification with images
- **Avoid**: Deep reasoning, pure text complex tasks

## Cognitive Mode: Multimodal Fast
Vision + language in one model. Fast for multimodal tasks.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 128,000 |
| Latency (P99) | 2,000ms |
| Uptime | 99.0% |
| Community Rating | 4.1/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Multimodal Trade-off**: Less text reasoning than pure text models.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: fast
tool_fidelity: medium
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Use for multimodal fast tasks"
  - "Do NOT use for deep reasoning"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
