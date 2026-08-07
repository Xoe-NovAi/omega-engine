---
model_id: nousresearch/hermes-3-llama-3.1-405b:free
display_name: Hermes 3 Llama 3.1 405B (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T3
status: active
context_window: 131072
max_output_tokens: 131072
capabilities:
  reasoning: 0.9
  code_generation: 0.88
  knowledge: 0.92
  creative: 0.88
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
latency_p99_ms: 5000
uptime_percent: 98.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- "Nous Research's Hermes 3 \u2014 405B parameters"
- 128K context window
- Strong instruction following
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
  - Verify claims against source documents
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
- instruction_following
- free_tier
- openrouter
- hermes_3
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
  total: 405B
  active: 405B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: 15T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Hermes 3 Llama 3.1 405B (Free) — Model Card

## Overview
Nous Research's Hermes 3. 405B parameters. 128K context. Strong instruction following. Free on OpenRouter.

## Intended Use
- **Primary**: Instruction following, reasoning, tool use
- **Secondary**: Complex synthesis, code generation
- **Avoid**: Real-time tasks (latency)

## Cognitive Mode: Instruction-Following Reasoning
Hermes series optimized for instruction following and tool use. Strong at agentic workflows.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 5,000ms |
| Uptime | 98.0% |
| Community Rating | 4.6/5.0 |
| Cost | $0.00 (free tier) |

## Known Issues
1. **Latency**: 405B model — slower than smaller models.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Use structured output for tool calls"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
