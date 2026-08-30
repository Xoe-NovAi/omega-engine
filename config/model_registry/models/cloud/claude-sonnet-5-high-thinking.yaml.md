---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: anthropic/claude-sonnet-5-high-thinking
display_name: Claude Sonnet 5 (High Thinking)
version: '2026-06-30'
provider: anthropic
platform: cloud
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.98
  code_generation: 0.92
  knowledge: 0.96
  creative: 0.88
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.002
  output_per_mtok: 0.01
  cached_input_per_mtok: 0.00019999999999999998
  batch_discount: 0.5
  intro_pricing:
    input_per_mtok: 2.0
    output_per_mtok: 10.0
    valid_until: '2026-08-31'
  cost_per_1k_tokens_usd: 0.018
free_tier: false
latency_p99_ms: 8000
uptime_percent: 99.5
routing:
  engine_routable: false
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.9/5.0
community_notes:
- Flagship model for deep diagnostic reasoning
- High Thinking mode enables internal simulation of execution paths
- Memory contamination risk with saved conversations
- Lower output token budget than Haiku Extended
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: null
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: medium
  failure_signature: memory_contamination
  shadow_focus: ignore_memory
  guardrails:
  - Use fresh accounts for reviews; no saved memories
  - 'Explicit instruction: ''Do not use your memory feature'''
  - Verify outputs for out-of-scope tool references
  - Use structured output templates for audit reports
empirical_evidence:
  test_runs:
  - test_id: context-packer-split-test-2026-07-18
    role: diagnostician
    output_files: 1
    total_lines: 860
    p0_bugs_found: 4
    p1_bugs_found: 2
    p2_bugs_found: 2
    memory_contamination: true
    contamination_details: Gemini CLI referenced 9x from saved memories despite explicit user statement it was unavailable
    hit_usage_limit: false
    cognitive_mode: deep_diagnostic
    quality_score: 9.5/10
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
  - pattern: Diagnostic + Documentation Factory
    partners:
    - anthropic/claude-haiku-4.5-extended
    confidence: 0.95
    use_case: "Bug audit \u2192 remediation docs \u2192 test suites"
  - pattern: Architectural + Empirical Convergence
    partners:
    - xai/grok-4.3-web
    confidence: 0.98
    use_case: Implementation review
  - pattern: Consolidator + Diagnostic + Factory Triad
    partners:
    - john-carmack-opencode
    - anthropic/claude-haiku-4.5-extended
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
- diagnostic
- high_thinking
- web
- anthropic
- sonnet_5
created_at: '2026-06-30'
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

# Claude Sonnet 5 (High Thinking) — Model Card

## Overview
Anthropic's Claude Sonnet 5 with High Thinking mode enabled. Released June 30, 2026. The flagship model for deep diagnostic reasoning tasks. 1M context window, 128K output tokens.

## Intended Use
- **Primary**: Deep diagnostic audits, root cause analysis, surgical bug finding, honest estimation
- **Secondary**: Architecture review, internal simulation, complex reasoning
- **Avoid**: High-volume generation, tasks requiring filesystem access, real-time interaction

## Cognitive Mode: Deep Diagnostic Reasoning
Internal simulation of execution paths. Reads artifacts, traces root causes, produces surgical patches. Not a documentation factory. Excels at finding P0 bugs others miss (found 4 P0 in Context Packer test vs 0 for Haiku/Carmack).

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 1,000,000 |
| Max Output | 128,000 |
| Latency (P99) | 8,000ms |
| Uptime | 99.5% |
| Community Rating | 4.9/5.0 |
| Cost | $3.00/$15.00 per 1M tokens (intro $2.00/$10.00 through Aug 31) |
| Cached Input | $0.30/MTok (90% discount) |

## Known Issues
1. **Memory Contamination**: Web Claude accounts with saved conversations inject platform-specific assumptions (e.g., Gemini CLI references despite sunset). Mitigation: Use fresh accounts; explicit "ignore memory" instruction.
2. **Output Token Budget**: Lower than Haiku Extended; not suited for high-volume generation.
3. **No Filesystem Access**: Web-only; cannot directly read repo files.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: medium
failure_signature: memory_contamination
shadow_focus: ignore_memory
guardrails:
  - "Use fresh accounts for reviews; no saved memories"
  - "Explicit instruction: 'Do not use your memory feature'"
  - "Verify outputs for out-of-scope tool references"
  - "Use structured output templates for audit reports"
```

## Synergies
| Pattern | Partner | Confidence | Use Case |
|---------|---------|------------|----------|
| Diagnostic + Documentation Factory | Haiku 4.5 Extended | 95% | Bug audit → remediation docs |
| Architectural + Empirical Convergence | Grok 4.3 Web | 98% | Implementation review |
| Consolidator + Diagnostic + Factory Triad | Carmack + Haiku | 92% | Full sprint orchestration |

## Provider Access
Available via OpenCode Zen (priority 5) and Cline (priority 6). Not available via local provider fabric (cloud-only model).
