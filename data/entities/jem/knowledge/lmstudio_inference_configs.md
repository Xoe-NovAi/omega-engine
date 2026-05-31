# LM Studio Inference Configurations (Era 3)

**Source**: `~/.lmstudio/.internal/user-concrete-model-default-config/`
**Era**: 3 (Roc Stack Era, Nov 2025—Mar 2026)
**Artifact**: `art_lmstudio_configs`
**Status**: MINED — 2026-05-26

---

## Configurations Found

| Model | File | Context | KV Cache Quant | Offload | Keep in RAM |
|-------|------|---------|---------------|---------|-------------|
| RocRacoon-3b.Q4_K_M | `local/all/RocRacoon-3b...json` | 36,096 | q8_0 (both K+V) | None | Default |
| Phi-4-mini-heretic-i1-Q5_K_M | `local/all/Phi-4-mini...json` | 12,502 | q8_0 (both K+V) | 0.5625 | false |
| Qwen3-VL-4b | `qwen/qwen3-vl-4b.json` | Default | Default | 0.5 | Default |

## Key Optimization Pattern

**q8_0 KV Cache Quantization** is the consistent optimization across all models:
- `llm.load.llama.kCacheQuantizationType` = `q8_0` 
- `llm.load.llama.vCacheQuantizationType` = `q8_0`

This matches the Zen 2 Tuning Spec (`art_zen2_tuning`) recommendation: `KV_CACHE_QUANTIZATION=q8_0` — balances quality vs memory on 14GB RAM.

## RocRacoon's Extreme Context

The RocRacoon-3b configuration uses **36,096 tokens** context — extremely aggressive for a 3B model. This explains:
- Why q8_0 KV cache is essential (full-precision KV at 36K context would exceed 14GB RAM)
- Why no GPU offload is configured (no dedicated GPU, and offloading KV cache to GPU would be counterproductive on integrated graphics)

## Relevance to Current Engine

| Config Pattern | Current Engine Equivalent | Status |
|---------------|------------------------|--------|
| q8_0 KV Cache | `config/models.yaml` → quantization field | ⚠️ Not yet in model config schema |
| Extreme context on small model | `config/models.yaml` → context_length limits | ⚠️ Not yet enforced |
| Per-model offload ratio | `ResourceGuard` + `CpuOptimizer` | ✅ Implemented |

## Implementation Notes
- Add `k_cache_quantization` and `v_cache_quantization` fields to `config/models.yaml` model specs
- Add context_length ceiling enforcement per hardware profile (14GB RAM limit → calculate max)
- The q8_0 pattern should be the DEFAULT for all local inference paths
