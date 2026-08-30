---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: claude-haiku-4.5-extended
display_name: Claude Haiku 4.5 (Extended)
version: '2026-06-15'
provider: anthropic
platform: cloud
tier: T2
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.65
  code_generation: 0.75
  knowledge: 0.7
  creative: 0.8
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.002
  output_per_mtok: 0.01
  cached_input_per_mtok: 0.00019999999999999998
  batch_discount: 0.5
  cost_per_1k_tokens_usd: 0.0015
free_tier: true
latency_p99_ms: 2500
uptime_percent: 99.8
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.3/5.0
community_notes:
- "High-throughput generation mode \u2014 3-5x output tokens vs Sonnet"
- Hits free tier limit fast in Extended mode (3.7x output multiplier)
- Shallow reasoning; misses deep bugs Sonnet catches
- Best for documentation factories, test scaffolding, boilerplate
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: fast
  tool_fidelity: low
  failure_signature: shallow
  shadow_focus: force_deepening
  guardrails:
  - Do NOT use for diagnostic/audit tasks
  - 'Use for generation only: docs, tests, boilerplate'
  - "Monitor free tier usage \u2014 Extended mode exhausts fast"
empirical_evidence:
  test_runs:
  - test_id: context-packer-split-test-2026-07-18
    role: documentation_factory
    output_files: 3
    total_lines: 3176
    p0_bugs_found: 0
    p1_bugs_found: 0
    p2_bugs_found: 0
    memory_contamination: false
    contamination_details: ''
    hit_usage_limit: true
    cognitive_mode: high_throughput_generation
    quality_score: N/A (generation only)
  synergies:
  - pattern: Diagnostic + Documentation Factory
    partners:
    - claude-sonnet-5-high-thinking
    confidence: 0.95
    use_case: "Bug audit \u2192 remediation docs \u2192 test suites"
  - pattern: Consolidator + Diagnostic + Factory Triad
    partners:
    - john-carmack-opencode
    confidence: 0.92
    use_case: "Full sprint: roadmap \u2192 audit \u2192 artifacts"
provider_fabric:
  available_via:
  - provider: opencode-zen
    priority: 5
  - provider: cline
    priority: 6
  local_first_priority: null
tags:
- generation
- high_throughput
- extended
- web
- anthropic
- haiku_4_5
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

# Claude Haiku 4.5 (Extended) — Model Card

## Overview
Anthropic's Haiku 4.5 with Extended output mode. Released June 2026. High-throughput generation specialist. 200K context, 500K output tokens in Extended mode. $0.25/$1.25 per 1M tokens.

## Intended Use
- **Primary**: Documentation generation, test scaffolding, boilerplate, quick references
- **Secondary**: High-volume code generation, API client generation
- **Avoid**: Diagnostic tasks, root cause analysis, architectural reasoning, deep audits

## Cognitive Mode: High-Throughput Generation
Produces 3-5x more output tokens than Sonnet. Creates complete documentation suites, test suites, boilerplate. Not a diagnostician — misses deep bugs. In Context Packer test: 3176 lines across 3 files, 0 bugs found, hit free tier limit.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 200,000 |
| Max Output (Extended) | 500,000 |
| Latency (P99) | 2,500ms |
| Uptime | 99.8% |
| Community Rating | 4.3/5.0 |
| Cost | $0.25/$1.25 per 1M tokens |
| Free Tier | Yes (but low allocation) |

## Known Issues
1. **Free Tier Exhaustion**: Extended mode's 3.7x output multiplier exhausts Haiku's low free tier allocation rapidly. In split test, hit limit after 3 docs.
2. **Shallow Reasoning**: Cannot do deep diagnostic reasoning. Misses P0 bugs Sonnet catches.
3. **Per-Model Limits**: Free tier limits are per-model, per-account. Using Haiku doesn't deplete Sonnet's allocation.

## Research Profile
```yaml
reasoning_depth: fast
tool_fidelity: low
failure_signature: shallow
shadow_focus: force_deepening
guardrails:
  - "Do NOT use for diagnostic/audit tasks"
  - "Use for generation only: docs, tests, boilerplate"
  - "Monitor free tier usage — Extended mode exhausts fast"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Diagnostic + Documentation Factory | Sonnet 5 High Thinking | 95% | Bug audit → remediation docs |
| Consolidator + Diagnostic + Factory Triad | Carmack + Sonnet | 92% | Full sprint orchestration |

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6). Engine-routable.
