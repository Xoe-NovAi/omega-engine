---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: llama-4-scout-local
display_name: Llama 4 Scout (Local)
version: '2026-06-15'
provider: native-gguf
platform: local
tier: T3
status: active
context_window: 10000000
max_output_tokens: 10000000
capabilities:
  reasoning: 0.85
  code_generation: 0.88
  knowledge: 0.82
  creative: 0.8
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 9.999999999999999e-05
  output_per_mtok: 0.0003
  cached_input_per_mtok: 0.0
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
community_rating: 4.7/5.0
community_notes:
- "10M context window \u2014 massive long-context synthesis"
- "$0/token \u2014 full sovereignty"
- Requires 24GB+ VRAM or 48GB+ RAM
- Production fleet candidate for sovereign deployment
- No cloud dependency
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
  - Verify claims against source documents
  - Use RAG for factual grounding
  - Monitor for context drift in 10M window
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
- sovereign
- massive_context
- local
- production_fleet
- native_gguf
- llama_4
created_at: '2026-06-15'
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
  total: 17B
  active: 17B
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

# Llama 4 Scout (Local) — Model Card

## Overview
Meta's Llama 4 Scout. 10M context window. $0/token. Full sovereignty. Requires 24GB+ VRAM or 48GB+ RAM. Production fleet candidate for sovereign deployment.

## Intended Use
- **Primary**: Production fleet, long-context synthesis, sovereign deployment
- **Secondary**: Complex reasoning without cloud, massive document processing
- **Avoid**: Real-time interaction (latency), tasks needing multimodal

## Cognitive Mode: Sovereign Production Reasoning
Massive context enables holding entire codebases + docs + history. Local inference = zero cloud dependency. Strong reasoning for production use.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 10,000,000 |
| Max Output | 500,000 |
| Latency (P99) | 5,000ms (depends on hardware) |
| Uptime | 100% (local) |
| Community Rating | 4.7/5.0 |
| Cost | $0/token |
| Hardware | 24GB+ VRAM / 48GB+ RAM |

## Known Issues
1. **Hardware Requirements**: High RAM/VRAM needed.
2. **Latency**: Slower than cloud for small tasks.
3. **No Multimodal**: Text only.
4. **Hallucination Risk**: Large context can drift; needs RAG grounding.

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: hallucination
shadow_focus: verify_facts
guardrails:
  - "Verify claims against source documents"
  - "Use RAG for factual grounding"
  - "Monitor for context drift in 10M window"
```

## Provider Access
Local-first via native-gguf (priority 0), LM Studio (priority 1), Ollama (priority 2). Engine-routable.
