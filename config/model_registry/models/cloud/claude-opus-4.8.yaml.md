---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: anthropic/claude-opus-4.8
display_name: Claude Opus 4.8
version: '2026-06-15'
provider: anthropic
platform: cloud
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 1.0
  code_generation: 0.95
  knowledge: 0.98
  creative: 0.92
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.005
  output_per_mtok: 0.025
  cached_input_per_mtok: 0.0005
  batch_discount: 0.5
  cost_per_1k_tokens_usd: 0.03
free_tier: false
latency_p99_ms: 12000
uptime_percent: 99.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.9/5.0
community_notes:
- "Maximum reasoning depth \u2014 complex synthesis, novel problem solving"
- "Very expensive \u2014 reserve for architecture design only"
- Overkill for most tasks; Sonnet 5 High Thinking sufficient for diagnostics
- Free tier allocation very low
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: null
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: medium
  failure_signature: over_analysis
  shadow_focus: force_persistence
  guardrails:
  - Reserve for architecture design, novel problems only
  - Do NOT use for routine review or generation
  - "Monitor cost \u2014 $5/$25 per MTok"
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
- architecture
- maximum_reasoning
- web
- anthropic
- opus_4_8
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
  total: 284B
  active: 284B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: BF16
  training_tokens: Unknown
  source: estimated
  verified: false
---

# Claude Opus 4.8 — Model Card

## Overview
Anthropic's Opus 4.8. Maximum reasoning depth. 1M context, 200K output. $5/$25 per 1M tokens. Reserve for architecture design and novel problem solving only.

## Intended Use
- **Primary**: Architecture design, novel problem solving, complex synthesis
- **Secondary**: Extremely complex multi-system reasoning
- **Avoid**: Routine review, generation, diagnostics (use Sonnet 5 High Thinking)

## Cognitive Mode: Maximum Reasoning Depth
Deepest internal reasoning. Complex synthesis across massive contexts. Not cost-effective for routine work.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000 |
| Max Output | 200,000 |
| Latency (P99) | 12,000ms |
| Uptime | 99.5% |
| Community Rating | 4.9/5.0 |
| Cost | $5.00/$25.00 per 1M tokens |
| Free Tier | Very low allocation |

## Known Issues
1. **Cost**: 1.67x Sonnet 5 input, 1.67x output. Use sparingly.
2. **Overkill**: Sonnet 5 High Thinking handles 95% of diagnostic tasks.
3. **Free Tier**: Minimal allocation.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: medium
failure_signature: over_analysis
shadow_focus: force_persistence
guardrails:
  - "Reserve for architecture design, novel problems only"
  - "Do NOT use for routine review or generation"
  - "Monitor cost — $5/$25 per MTok"
```

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6). Engine-routable.
