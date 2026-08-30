---
model_id: gemini-2.5-pro
display_name: Gemini 2.5 Pro
version: '2026-06-15'
provider: google
platform: cloud
tier: T3
status: active
context_window: 1048576
max_output_tokens: 1048576
capabilities:
  reasoning: 0.95
  code_generation: 0.9
  knowledge: 0.98
  creative: 0.92
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: true
  parallel_search: true
  workspace_integration: true
pricing:
  input_per_mtok: 0.00125
  output_per_mtok: 0.01
  cached_input_per_mtok: 0.000125
  batch_discount: null
  cost_per_1k_tokens_usd: 0.00625
free_tier: true
latency_p99_ms: 5000
uptime_percent: 99.5
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.8/5.0
community_notes:
- "Parallel web search \u2014 independent verification"
- Built-in Python sandbox for code execution
- "Source grounding required: every claim cites [bundle.xml \xA73.2]"
- 'Workspace export: format findings as MD tables for Sheets/Docs'
- Markdown + structured frontmatter preferred format
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: hallucination
  shadow_focus: verify_facts
  guardrails:
  - "Every claim must cite source: [bundle.xml \xA7X.Y]"
  - Use code execution to verify API surfaces
  - Parallel search for independent verification
empirical_evidence:
  test_runs: []
  synergies:
  - pattern: Source-Grounded Review
    partners:
    - claude-sonnet-5-high-thinking
    confidence: 0.9
    use_case: Parallel verification of claims
provider_fabric:
  available_via:
  - provider: google
    priority: 4
  - provider: opencode-zen
    priority: 5
  local_first_priority: null
tags:
- reasoning
- parallel_search
- code_execution
- source_grounding
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

# Gemini 2.5 Pro — Model Card

## Overview
Google's Gemini 2.5 Pro. 1M context, parallel web search, code execution, Workspace integration. Markdown + structured frontmatter preferred.

## Intended Use
- **Primary**: Source-grounded review, parallel verification, executable validation
- **Secondary**: Massive context synthesis, video understanding, Workspace collaboration
- **Avoid**: XML-native tasks, real-time social search (no X access)

## Cognitive Mode: Source-Grounded Verification
Every claim must cite sources. Parallel search enables independent verification. Built-in Python sandbox for executable validation. NotebookLM-style citation format.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000+ |
| Max Output | 200,000 |
| Latency (P99) | 5,000ms |
| Uptime | 99.5% |
| Community Rating | 4.8/5.0 |
| Cost | $1.25/$5.00 per 1M tokens (<200K) / $2.50/$10.00 (>200K) |
| Free Tier | Yes |

## Known Issues
1. **Hallucination Risk**: Without source grounding, can hallucinate. Guardrail: mandatory citations.
2. **Format Preference**: Markdown + frontmatter, not XML-native.
3. **Server-Managed Caching**: No explicit cache_control like Anthropic.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Every claim must cite source: [bundle.xml §X.Y]"
  - "Use code execution to verify API surfaces"
  - "Parallel search for independent verification"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Source-Grounded Review | Sonnet 5 High Thinking | 90% | Parallel verification |

## Provider Access
Available via Google AI Studio (priority 4) and OpenCode Zen (priority 5). Engine-routable.
