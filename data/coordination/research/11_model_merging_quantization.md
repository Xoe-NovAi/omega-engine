<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Model Merging & Quantization — Deep Research
**AP Token**: `AP-MERGE-QUANT-20260726`
**Date**: 2026-07-26 | **Priority**: P1
**Researcher**: Sovereign Researcher

---

## Gap 1: Model Merging (R49)

### Executive Summary

Zero model merging infrastructure. `merge_gguf_models.py` is a file-migrator, not a model merger. No mergekit, no DARE-TIES, no LoRA adapter support. Qwen3-1.7B is the only viable merge candidate.

### Current State

| Component | Status |
|-----------|--------|
| mergekit | ❌ Not installed |
| DARE-TIES config | ❌ Does not exist |
| LoRA adapter support | ❌ Does not exist |
| Imatrix calibration | ❌ Does not exist |
| Merge candidates | Qwen3-1.7B (only viable base) |

### Models on Disk

| Model | Quant | Size | Merge Candidate? |
|-------|-------|------|------------------|
| Qwen3-1.7B | Q6_K | 1.6 GB | ✅ Base model |
| MiMo-7B-RL | Q4_K_M | 4.5 GB | ❌ Different architecture |
| Krikri-8B-Instruct | Q4_K_M | 4.7 GB | ❌ Different architecture |
| Qwen3-4B-Instruct | Q4_K_XL | 2.4 GB | ⚠️ Possible Qwen3 merge |

### Effort: ~12h

---

## Gap 2: Quantization (R47)

### Executive Summary

All models use standard quantization without importance matrix calibration. RAM estimation formula is approximate. No quality regression tracking.

### Current Quantization Levels

| Level | Models | Bits/Weight | Perplexity Loss |
|-------|--------|-------------|-----------------|
| Q6_K | Qwen3-1.7B, Qwen3-0.6B | ~6.6 | ~0.8% |
| Q5_K_M | Phi-4-mini, RocRacoon-3b | ~5.7 | ~1.2% |
| Q4_K_M | MiMo-7B, Krikri-8B, Qwen3-4B | ~4.8 | ~1.6% |
| Q3_K_L | DeepSeek-R1-Qwen3-8B | ~3.5 | ~3% |

### Issues

1. No imatrix quantization — losing ~0.3-1% quality
2. RAM formula is approximate (doesn't account for architecture)
3. No quality regression tracking
4. Q4_0 used for embeddings while K-quants are better

### Effort: ~17h

---

## Combined Summary

| Gap | Current Score | Effort |
|-----|--------------|--------|
| R49 Model Merging | 0/10 | ~12h |
| R47 Quantization | 4/10 | ~17h |
