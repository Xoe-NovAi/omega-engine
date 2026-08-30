---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: openai/gpt-oss-20b:free
display_name: GPT-OSS-20B (Free)
version: '2026-05-17'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 131072
max_output_tokens: 131072
capabilities:
  reasoning: 0.78
  code_generation: 0.8
  knowledge: 0.85
  creative: 0.8
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
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.2/5.0
community_notes:
- "OpenAI's GPT-OSS-20B \u2014 open weights (Apache 2.0)"
- 128K context window
- Smaller but capable
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
  - Verify claims against source documents
  - Use RAG for factual grounding
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: openrouter
    priority: 4
  local_first_priority: null
tags:
- open_weights
- reasoning
- free_tier
- openrouter
- gpt_oss
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
  total: 20B
  active: 20B
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

# GPT-OSS-20B (Free) — Model Card

## Overview
OpenAI's GPT-OSS-20B. Open weights (Apache 2.0). 128K context. Smaller but capable. Free on OpenRouter.

## Intended Use
- **Primary**: Reasoning without cloud, open weights
- **Secondary**: Local development alternative
- **Avoid**: Multimodal tasks, maximum-depth reasoning

## Cognitive Mode: Open Weights Reasoning
Apache 2.0 license enables commercial use. Good reasoning for size.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 131,072 |
| Latency (P99) | 2,500ms |
| Uptime | 99.0% |
| Community Rating | 4.2/5.0 |
| Cost | $0.00 (free tier) |
| License | Apache 2.0 |

## Known Issues
1. **Open Weights ≠ Open Source**: License restrictions apply.
2. **Daily Quota**: OpenRouter free tier resets at 00:00 UTC.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: medium
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Use RAG for factual grounding"
```

## Provider Access
Available via OpenRouter (priority 4). Engine-routable.
