---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

model_id: gpt-oss-120b-local
display_name: GPT-OSS-120B (Local)
version: '2026-06-20'
provider: native-gguf
platform: local
tier: T3
status: active
context_window: 131072
max_output_tokens: 131072
capabilities:
  reasoning: 0.88
  code_generation: 0.9
  knowledge: 0.92
  creative: 0.85
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 3.7e-05
  output_per_mtok: 0.00016999999999999999
  cached_input_per_mtok: 0.0
  batch_discount: null
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 8000
uptime_percent: 100.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null
community_rating: 4.5/5.0
community_notes:
- Open weights (not open source)
- Strong reasoning, local inference
- Requires 48GB+ RAM
- Good alternative to cloud for complex reasoning
live_api_state:
  source: openrouter-api-2026-07-19
  last_verified: '2026-07-18'
  last_verified_free: '2026-07-18'
  confidence: high
research_profile:
  reasoning_depth: deep
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
  - provider: native-gguf
    priority: 0
  - provider: lmster
    priority: 1
  - provider: ollama
    priority: 2
  local_first_priority: 0
tags:
- reasoning
- open_weights
- local
- sovereign
- native_gguf
- gpt_oss
created_at: '2026-06-20'
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
  total: 120B
  active: 120B
  architecture: dense
  experts: 0
  active_experts: 0
  shared_experts: 0
  quantization: INT4
  training_tokens: Unknown
  source: official
  verified: true
  verified_date: '2026-07-18'
---

# GPT-OSS-120B (Local) — Model Card

## Overview
OpenAI's GPT-OSS-120B. Open weights (Apache 2.0). 128K context. Strong reasoning. Requires 48GB+ RAM. $0/token local inference.

## Intended Use
- **Primary**: Complex reasoning without cloud, sovereign deployment
- **Secondary**: Local development, offline work
- **Avoid**: Multimodal tasks, real-time interaction

## Cognitive Mode: Sovereign Complex Reasoning
Open weights enable full local control. Good reasoning for production use without cloud dependency.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 128,000 |
| Max Output | 32,000 |
| Latency (P99) | 8,000ms |
| Uptime | 100% (local) |
| Community Rating | 4.5/5.0 |
| Cost | $0/token |
| Hardware | 48GB+ RAM |

## Known Issues
1. **Hardware**: 48GB+ RAM required.
2. **Open Weights ≠ Open Source**: License restrictions apply.
3. **Latency**: Slower than smaller models.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: medium
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Use RAG for factual grounding"
```

## Provider Access
Local-first via native-gguf (priority 0), LM Studio (priority 1), Ollama (priority 2). Engine-routable.
