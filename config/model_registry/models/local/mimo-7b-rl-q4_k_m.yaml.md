---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

model_id: "mimo-7b-rl-q4_k_m"
display_name: "MiMo-7B-RL-Q4_K_M"
version: "2026-07-18"
provider: "native-gguf"
platform: "LOCAL"
tier: "T2"
status: "ACTIVE"
context_window: 32768
max_output_tokens: 8192
capabilities:
  reasoning: 0.85
  code_generation: 0.88
  knowledge: 0.82
  creative: 0.75
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cached_input_per_mtok: 0.0
  batch_discount: 0.0
  intro_pricing: null
  free_tier: true
  cost_per_1k_tokens_usd: 0.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history:
  original: "MiMo-7B-RL"
  current: "MiMo-7B-RL-Q4_K_M"
  swap_detected: false
  last_verified: "2026-07-18"
community_intelligence:
  rating: "community_verified"
  notes:
    - "Xiaomi MiMo 7B RL model, Q4_K_M quantization"
    - "Strong reasoning and coding capabilities"
    - "32K context window"
    - "Local-first sovereign inference"
live_api_state:
  source: "native-gguf"
  last_verified: "2026-07-18"
  last_verified_free: "2026-07-18"
research_profile:
  reasoning_depth: "iterative"
  tool_fidelity: "high"
  failure_signature: "repetition_loops"
  shadow_focus: "force_deepening"
  guardrails:
    - "repetition_penalty_1.15"
    - "temperature_0.7_max"
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via: ["native-gguf"]
  local_first_priority: 0
parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.15
  max_tokens: 8192
  stop_sequences: ["</s>", "<|im_end|>", "<|endoftext|>"]
  presence_penalty: 0.0
  frequency_penalty: 0.0
  logit_bias: null
  seed: null
  model_specific_overrides:
    n_ctx: 32768
    n_threads: 6
    n_gpu_layers: 0
    kv_cache_type: "q8_0"
    n_batch: 512
    n_ubatch: 32
benchmark_sources:
  reasoning: "internal_benchmark_2026-07"
  code_generation: "internal_benchmark_2026-07"
  knowledge: "internal_benchmark_2026-07"
  creative: "internal_benchmark_2026-07"
  tool_use: "internal_benchmark_2026-07"
  structured_output: "internal_benchmark_2026-07"
  multimodal: ""
  overall: "internal_benchmark_2026-07"
tags:
  - "local"
  - "sovereign"
  - "mimo"
  - "xiaomi"
  - "7b"
  - "rl"
  - "q4_k_m"
  - "32k_context"
created_at: "2026-07-18"
updated_at: "2026-07-18"
schema_version: "1.2.0"
---