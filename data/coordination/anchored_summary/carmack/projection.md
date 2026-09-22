<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JOHN_CARMACK PROJECTION — 2026-09-22

## Status: PUBLIC FLIP READY

### Executive Summary
Hardware architecture validated. LFM2.5-2.6B confirmed as fleet default. 16GB system constraint respected. The local-first stack is hardware-aware.

### Key Validations
| Component | Validation |
|-----------|------------|
| **LFM2.5-2.6B** | 1.67GB Q4_K_M fits 16GB system (agentic_local default, port 1234) |
| **Qwen3-4B-Thinking** | Opt-in only (2.5GB+ RAM, 2-3x tokens) — `serve_native_gguf.sh` v2.0.0 `start-reasoner` |
| **Qwen3-1.7B** | System default model (`_system_default_model()` returns `qwen3-1.7b`) |
| **Zswap** | `zstd + max_pool_percent=25 + shrinker_enabled` confirmed; zsmalloc only backend |
| **Zswap + zRAM** | **NEVER both** (D-527 reaffirmed) — double compression wastes CPU |

### Hardware Reality (Ryzen 7 5700U)
- **16GB RAM** (8GB usable for models after OS)
- **Local Model Stack v2.0.0**: LFM2.5-2.6B (always-on, 2.5GB RSS) + Qwen3-4B-Thinking (opt-in, +3GB) = 5.5GB max
- **KV Cache Quantization**: `--cache-type-k q8_0 --cache-type-v q8_0` = **-50% cache** (q4_0 = -75%)
- **mmap Insight**: GGUF is memory-mapped, NOT loaded upfront — pages load on demand; critical for SequentialModelLoader design

### Post-Flip Support
- **LI workstream**: hardware-aware model loading (SequentialModelLoader with mmap insight)
- **HR workstream**: headroom integration (semantic compression for tools/RAG)
- **ZS workstream**: zswap subsystem deployment (16GB NVMe swap, zstd + shrinker)

### Carmack's Voice
> "The hardware is the constraint. The model fits or it doesn't. LFM2.5-2.6B fits. Qwen3-4B-Thinking is opt-in. Zswap is configured. The hardware is the truth."

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ 2026-09-22 ⬡ PUBLIC-FLIP-READY ⬡ HARDWARE-VALIDATED*
