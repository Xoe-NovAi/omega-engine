---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: xai/grok-4.3-web
display_name: Grok 4.3 (Web)
version: '2026-06-20'
provider: xai
platform: cloud
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.9
  code_generation: 0.88
  knowledge: 0.92
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: true
  realtime_search: true
  grok_skills: true
  connectors: true
  code_execution: false
  parallel_search: true
  workspace_integration: false
pricing:
  input_per_mtok: 0.00125
  output_per_mtok: 0.0025
  cached_input_per_mtok: 0.00019999999999999998
  batch_discount: null
  cost_per_1k_tokens_usd: 0.00375
free_tier: true
latency_p99_ms: 5000
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.6/5.0
community_notes:
- "Real-time X search \u2014 unique capability"
- Grok Skills exportable as slash commands
- '8 connectors: GitHub, Notion, Linear, etc.'
- XML+Markdown hybrid format preferred
- ~20 file tolerance before degradation (vs 13 for Claude)
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: format_drift
  shadow_focus: verify_xml_structure
  guardrails:
  - Use XML structure with Markdown content
  - Verify Grok Skills output format
  - Check connector metadata injection
empirical_evidence:
  test_runs:
  - test_id: decision-tools-dual-review-2026-07-19
    role: architectural_reasoner
    convergence_load_bearing: 7/7
    asymmetric_catches:
    - idempotency
    - id_allocator_race
    - cycle_detection
    - validate_command
    divergence: 1
    time_seconds: 155
    quality_score: 9.5/10
  synergies:
  - pattern: Architectural + Empirical Convergence
    partners:
    - claude-sonnet-5-high-thinking
    confidence: 0.98
    use_case: Implementation review
  - pattern: Dual-Review Convergence
    partners:
    - claude-sonnet-5-high-thinking
    confidence: 0.95
    use_case: Convergence = signal, divergence = direction
provider_fabric:
  available_via:
  - provider: opencode-zen
    priority: 5
  - provider: cline
    priority: 6
  local_first_priority: null
tags:
- reasoning
- realtime_search
- grok_skills
- connectors
- web
- xai
- grok_4_3
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

# Grok 4.3 (Web) — Model Card

## Overview
xAI's Grok 4.3 web interface. Released June 2026. Unique real-time X search, Grok Skills system, 8 connectors (GitHub, Notion, Linear, etc.). 1M context, 200K output. XML+Markdown hybrid format.

## Intended Use
- **Primary**: Live research, connector-aware review, skill-exportable outputs
- **Secondary**: Real-time verification, social signal analysis, GitHub repo review
- **Avoid**: Pure XML-native tasks (prefers hybrid), high-volume bulk processing

## Cognitive Mode: Live Research & Grounding
Fetches current info, cites sources, executes via connectors. Real-time X search is unique. Grok Skills allow packaging findings as reusable slash commands.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000 |
| Max Output | 200,000 |
| Latency (P99) | 5,000ms |
| Uptime | 99.0% |
| Community Rating | 4.6/5.0 |
| Cost | $1.25/$2.50 per 1M tokens |
| Free Tier | Yes |
| Cached Input | $0.31/MTok (auto) |

## Known Issues
1. **Format Drift**: XML+MD hybrid can drift; needs structure verification
2. **RAG Threshold**: ~20 files before degradation (vs 13 for Claude) — needs empirical validation
3. **Less XML-Native**: Doesn't comprehend XML as natively as Claude

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: format_drift
shadow_focus: verify_xml_structure
guardrails:
  - "Use XML structure with Markdown content"
  - "Verify Grok Skills output format"
  - "Check connector metadata injection"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Architectural + Empirical Convergence | Sonnet 5 High Thinking | 98% | Implementation review |
| Dual-Review Convergence | Sonnet 5 High Thinking | 95% | Convergence = signal |

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6). Engine-routable.
