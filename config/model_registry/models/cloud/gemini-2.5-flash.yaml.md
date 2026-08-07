---
model_id: gemini-2.5-flash
display_name: Gemini 2.5 Flash
version: '2026-06-15'
provider: google
platform: cloud
tier: T2
status: active
context_window: 1048576
max_output_tokens: 1048576
capabilities:
  reasoning: 0.85
  code_generation: 0.82
  knowledge: 0.9
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: true
  parallel_search: true
  workspace_integration: true
pricing:
  input_per_mtok: 9.999999999999999e-05
  output_per_mtok: 0.00039999999999999996
  cached_input_per_mtok: 1.0e-05
  batch_discount: null
  cost_per_1k_tokens_usd: 0.000375
free_tier: true
latency_p99_ms: 2500
uptime_percent: 99.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- Fast, cost-effective Gemini variant
- 1M context window
- Parallel web search + code execution
- Good for high-volume tasks
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: iterative
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - "Every claim must cite source: [bundle.xml \xA7X.Y]"
  - Use code execution to verify API surfaces
  - Parallel search for independent verification
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
  - provider: google
    priority: 4
  - provider: opencode-zen
    priority: 5
  local_first_priority: null
tags:
- fast
- cost_effective
- parallel_search
- code_execution
- web
- google
- gemini_2_5
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

# Gemini 2.5 Flash — Model Card

## Overview
Google's Gemini 2.5 Flash. 1M context, parallel web search, code execution. Fast and cost-effective. $0.075/$0.30 per 1M tokens.

## Intended Use
- **Primary**: High-volume source-grounded tasks, parallel verification
- **Secondary**: Cost-sensitive massive context synthesis
- **Avoid**: Maximum-depth reasoning (use 2.5 Pro)

## Cognitive Mode: Fast Source-Grounded Verification
Same capabilities as Pro but faster and cheaper. Good for high-volume verification tasks.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000 |
| Max Output | 200,000 |
| Latency (P99) | 2,500ms |
| Uptime | 99.5% |
| Community Rating | 4.6/5.0 |
| Cost | $0.075/$0.30 per 1M tokens |
| Free Tier | Yes |

## Known Issues
1. **Less Reasoning Depth**: Not for architectural/deep diagnostic tasks.
2. **Format Preference**: Markdown + frontmatter, not XML-native.

## Research Profile
```yaml
reasoning_depth: iterative
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Every claim must cite source: [bundle.xml §X.Y]"
  - "Use code execution to verify API surfaces"
  - "Parallel search for independent verification"
```

## Provider Access
Available via Google AI Studio (priority 4) and OpenCode Zen (priority 5). Engine-routable.
