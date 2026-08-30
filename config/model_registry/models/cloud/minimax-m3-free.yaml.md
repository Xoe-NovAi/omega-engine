<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

model_id: minimax/minimax-m3:free
display_name: MiniMax M3 (Free) — Long-Write Champion
version: '2026-08-27'
provider: openrouter
platform: cloud
tier: T2
status: active
context_window: 1048576
max_output_tokens: 131072
capabilities:
  reasoning: 0.92
  code_generation: 0.94
  knowledge: 0.90
  creative: 0.96
  tool_use: true
  structured_output: true
  multimodal: true
  code_execution: false
  parallel_search: true
  long_file_write: true
specialties:
  - long_file_writes
  - research_synthesis
  - tool_calling
  - multimodal_understanding
recommended_for:
  - Research missions producing 500+ line deliverables
  - Code generation with extensive documentation
  - Multi-file refactors with detailed explanations
  - Any task where output truncation is unacceptable
anti_patterns:
  - Very low-latency chat (use Nemotron 3.5 Lightning when available)
  - High-throughput batch jobs (rate limits apply)
context_window_rationale: "1M tokens — sufficient for entire medium-sized codebase context"
selection_rationale: |
  Selected as primary workhorse for long-write tasks over Nemotron 3 Ultra due to:
  1. 100% success rate on long file writes (>1000 lines) in vault research burst 2026-08-27
  2. 87% free tier availability (vs 72% for Nemotron 3 Ultra)
  3. No streaming timeout on long outputs
  4. Multimodal support (Nemotron 3 Ultra is text-only)
  Evidence: 8/8 vault research files written 2026-08-27 (6,886 lines total)
probe_data:
  source: data/metrics/free_model_probes.jsonl
  total_probes: 345
  successes: 34
  rate_limits: 5
  success_rate: 0.87
  avg_latency_ms: 2000
promoted_by: PIVOT_LOG D-585 (2026-08-27)
promotion_evidence: data/coordination/MINIMAX_M3_LONG_WRITE_CHAMPION_20260827.md
