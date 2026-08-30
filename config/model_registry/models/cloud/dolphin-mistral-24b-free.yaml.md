---
model_id: cognitivecomputations/dolphin-mistral-24b-venice-edition:free
display_name: Dolphin Mistral 24B Venice Edition (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 32768
max_output_tokens: 32768
capabilities:
  reasoning: 0.78
  code_generation: 0.75
  knowledge: 0.8
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
latency_p99_ms: 2500
uptime_percent: 98.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.2/5.0
community_notes:
- "Cognitive Computations' Dolphin \u2014 uncensored"
- "Venice edition \u2014 24B Mistral base"
- 32K context window
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-05-17'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: medium
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - "Uncensored \u2014 verify safety-critical outputs"
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
- uncensored
- dolphin
- mistral
- free_tier
- openrouter
- cognitive_computations
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
  total: 24B
  active: 24B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: FP16
  training_tokens: Unknown
  source: community
  verified: false
---

# Dolphin Mistral 24B Venice Edition (Free) — Model Card

## Overview
Cognitive Computations' Dolphin fine-tune of Mistral 24B. Uncensored. Venice edition. 32K context. Free on OpenRouter.

## Intended Use
- **Primary**: Uncensored reasoning, creative tasks
- **Secondary**: Code generation, tool use
- **Avoid**: Safety-critical applications (uncensored)

## Cognitive Mode: Uncensored Iterative
No safety filters. Good for creative and reasoning tasks where censorship interferes.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 32,768 |
| Latency (P99) | 2,500ms |
| Uptime | 98.5% |
| Community Rating | 4.2/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Uncensored**: No safety filters — verify safety-critical outputs.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Uncensored — verify safety-critical outputs"
  - "Use structured output for tool calls"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
