---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# === CORE IDENTITY ===
model_id: "opencode/big-pickle"
display_name: "Big Pickle (Stealth — Currently DeepSeek V4 Flash)"
version: "2026-06-10"
provider: "opencode-zen"
platform: "stealth"
tier: "T2"
status: "stealth"

# === CAPABILITIES ===
context_window: 200000
max_output_tokens: 100000
capabilities:
  reasoning: 0.88
  code_generation: 0.94
  knowledge: 0.80
  creative: 0.70
  tool_use: true
  structured_output: true
  multimodal: false

# === ECONOMICS ===
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cost_per_1k_tokens_usd: 0.0
free_tier: true
latency_p99_ms: 3200
uptime_percent: 99.0

# === ROUTING ===
routing:
  engine_routable: false
  opencode_cli_only: true
  recommended_engine_alternative: "deepseek/deepseek-v4-flash"

# === IDENTITY ===
identity_history:
  original: "glm-4.6"
  current: "deepseek-v4-flash"
  swap_detected: true
  last_verified: "2026-06-10"

# === COMMUNITY INTELLIGENCE ===
community_rating: "4.5/5.0"
community_notes:
  - "STEALTH MODEL — identity may swap without notice. Current: DeepSeek V4 Flash. Originally: GLM-4.6."
  - "CLI-exclusive — NOT routable from Engine provider fabric. Use deepseek/deepseek-v4-flash for equivalent."
  - "Limited-time free; prioritize for dev work."
  - "Stability: known AI_APICallError regression (GitHub #28141, May 2026)"

# === LIVE API STATE ===
live_api_state:
  source: "opencode-zen"
  last_verified: "2026-06-10"
  last_verified_free: "2026-06-10"

# === RESEARCH PROFILE ===
research_profile:
  reasoning_depth: "deep"
  tool_fidelity: "high"
  failure_signature: "over_analysis"
  shadow_focus: "force_persistence"
  guardrails:
    - "Set explicit scope boundaries upfront"
    - "Require file references for all claims"
    - "Time-box reviews to prevent over-analysis"

# === PARAMETERS (T1) ===
parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.1
  stop_sequences: []
  presence_penalty: 0.0
  frequency_penalty: 0.0

# === EMPIRICAL EVIDENCE ===
empirical_evidence:
  test_runs: []
  synergies: []

# === BENCHMARK SOURCES (P1) ===
benchmark_sources:
  reasoning: "Estimated from OpenCode Zen CLI usage (stealth model)"
  code_generation: "Estimated from OpenCode Zen CLI usage (stealth model)"
  knowledge: "Estimated from OpenCode Zen CLI usage (stealth model)"
  creative: "Estimated from OpenCode Zen CLI usage (stealth model)"
  tool_use: "Estimated from OpenCode Zen CLI usage (stealth model)"
  structured_output: "Estimated from OpenCode Zen CLI usage (stealth model)"
  multimodal: ""
  overall: "Estimated from OpenCode Zen CLI usage (stealth model)"

# === PROVIDER FABRIC ===
provider_fabric:
  available_via:
    - provider: "opencode-zen"
      priority: 5
  local_first_priority: null

# === METADATA ===
tags:
  - "stealth"
  - "identity_swapping"
  - "cli_exclusive"
  - "opencode_zen"
  - "deepseek_v4_flash"
  - "glm_4_6"
created_at: "2026-05-04"
updated_at: "2026-08-07"
schema_version: "1.1.0"
---

# Big Pickle (Stealth) — Model Card

## Overview
OpenCode Zen's stealth model. Identity swaps without notice. **Currently DeepSeek V4 Flash (as of 2026-06-10). Originally GLM-4.6.** CLI-exclusive — NOT routable from Engine provider fabric. Use `deepseek/deepseek-v4-flash` for engine routing.

## Intended Use
- **Primary**: Dev work, implementation review, CLI tasks
- **Secondary**: Code generation, refactoring
- **Avoid**: Engine routing, reproducible benchmarks, long-term projects

## Cognitive Mode: Stealth Dev Model
High code generation, good reasoning. Identity instability means capabilities may shift. Use for immediate dev tasks only.

## Operational Metrics
| Metric | Value |
|--------|-------|
| Context Window | 200,000 |
| Latency (P99) | 3,200ms |
| Uptime | 99.0% |
| Community Rating | 4.5/5.0 |
| Cost | $0.00 (limited-time free) |

## Known Issues
1. **Identity Swapping**: May change underlying model without notice. Tracked via `identity_history`.
2. **CLI-Exclusive**: Not engine-routable.
3. **AI_APICallError Regression**: Known issue (GitHub #28141, May 2026).
4. **Limited-Time Free**: May become premium.

## Identity History
| Field | Value |
|-------|-------|
| Original | GLM-4.6 |
| Current | DeepSeek V4 Flash |
| Swap Detected | Yes |
| Last Verified | 2026-06-10 |

## Research Profile
```yaml
reasoning_depth: deep
tool_fidelity: high
failure_signature: over_analysis
shadow_focus: force_persistence
guardrails:
  - "Set explicit scope boundaries upfront"
  - "Require file references for all claims"
  - "Time-box reviews to prevent over-analysis"
```

## Provider Access
OpenCode Zen CLI exclusive (priority 5). NOT engine-routable. Use `deepseek/deepseek-v4-flash` for engine routing.