---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: nemotron-3-ultra-local
display_name: Nemotron 3 Ultra (Local)
version: '2026-06-10'
provider: native-gguf
platform: local
tier: T3
status: active
context_window: 1000000
max_output_tokens: 1000000
capabilities:
  reasoning: 0.87
  code_generation: 0.88
  knowledge: 0.9
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0006
  output_per_mtok: 0.0036
  cached_input_per_mtok: 0.00019999999999999998
  batch_discount: null
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 5000
uptime_percent: 100.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.4/5.0
community_notes:
- Current OpenCode session model
- Good instruction following
- Requires 24GB+ RAM
- Sovereign orchestration backbone
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: deep
  tool_fidelity: high
  failure_signature: tool_drift
  shadow_focus: verify_tool_use
  guardrails:
  - Use structured output templates
  - Verify tool output within 1 step
  - Split long chains into 5-step batches
empirical_evidence:
  test_runs: []
  synergies:
  - pattern: Sovereign Fleet
    partners:
    - kali-maat-lilith-opencode
    confidence: 1.0
    use_case: OpenCode session model for sovereign fleet
provider_fabric:
  available_via:
  - provider: native-gguf
    priority: 0
  - provider: lmster
    priority: 1
  - provider: ollama
    priority: 2
  local_first_priority: 0
tags:
- session_model
- instruction_following
- local
- sovereign
- native_gguf
- nemotron
created_at: '2026-06-10'
updated_at: '2026-07-18'
schema_version: 1.2.0
parameters:
  temperature: 0.5
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.0
  max_tokens: 8192
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
  total: 253B
  active: 253B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: INT4
  training_tokens: 9T
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# Nemotron 3 Ultra (Local) — Model Card

## Overview
NVIDIA's Nemotron 3 Ultra. 128K context. Current OpenCode session model. Good instruction following. Requires 24GB+ RAM. Sovereign orchestration backbone.

## Intended Use
- **Primary**: OpenCode session model (Kali, Ma'at, Lilith, nodes)
- **Secondary**: Sovereign orchestration, mandate enforcement
- **Avoid**: High-volume generation, multimodal tasks

## Cognitive Mode: Sovereign Orchestration Backbone
Session-bound model for OpenCode agents. Mandate-fluent, good instruction following, Hivemind coordination.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 128,000 |
| Max Output | 32,000 |
| Latency (P99) | 5,000ms |
| Uptime | 100% (local) |
| Community Rating | 4.4/5.0 |
| Cost | $0/token |
| Hardware | 24GB+ RAM |

## Known Issues
1. **Session-Bound**: Single model per OpenCode session.
2. **Hardware**: 24GB+ RAM required.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: tool_drift
shadow_focus: verify_tool_use
guardrails:
  - "Use structured output templates"
  - "Verify tool output within 1 step"
  - "Split long chains into 5-step batches"
```

## Synergies
| Pattern | Partners | Confidence | Use Case |
|---------|----------|------------|----------|
| Sovereign Fleet | Kali/Ma'at/Lilith | 100% | OpenCode session model |

## Provider Access
Local-first via native-gguf (priority 0), LM Studio (priority 1), Ollama (priority 2). Engine-routable.
