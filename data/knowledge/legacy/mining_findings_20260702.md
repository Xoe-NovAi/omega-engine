<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Legacy Mining Findings — Model & Platform Knowledge

**Date**: 2026-07-02
**Miner**: Roc Racoon
**Status**: CATALOGED — 20 assets, 10 top discoveries

---

## Asset Catalog

| # | Asset | Path | Era | Value | Freshness | Action |
|---|-------|------|-----|-------|-----------|--------|
| 1 | LM Studio configs (9 files) | `~/.lmstudio/.internal/user-concrete-model-default-config/` | Era 3 | 9/10 | Current | **PORT** — document in KB |
| 2 | omega-stack provider config | `omega-stack-legacy/config/` | Era 4 | 6/10 | Outdated | REFERENCE only |
| 3 | xna-omega provider config | `xna-omega-legacy/config/` | Era 4 | 5/10 | Outdated | REFERENCE only |
| 4 | System prompts (4 files) | `~/Documents/docs_1/system-prompts/` | Era 0-3 | 7/10 | Mixed | **PORT** relevant to KB |
| 5 | Model-persona affinity map | (documented in legacy docs) | Era 3 | 8/10 | Current | **PORT** to KB |
| 6 | Krikri Modelfile | (in omega-stack-legacy) | Era 3 | 5/10 | Outdated | REFERENCE |
| 7 | Foundation philosophy docs | `~/Documents/docs-backup/` | Era 1-2 | 4/10 | Historical | DISCARD |
| 8 | omega-stack 33K files | `omega-stack-legacy/` | Era 4 | 3/10 | Bloated | DISCARD (selective mine only) |
| 9 | xna-omega legacy code | `xna-omega-legacy/` | Era 4 | 5/10 | Outdated | REFERENCE for patterns |
| 10 | archive/foundation-legacy | `~/archive/foundation-legacy/` | Era 2 | 4/10 | Historical | DISCARD |

## Top Discoveries

### 1. LM Studio Configs (9 files) — HIGH VALUE
All configs at `~/.lmstudio/.internal/user-concrete-model-default-config/` show:
- **Universal q8_0 KV cache** across all models
- **Flash attention enabled** for context >8K
- **Thread counts 6-8** for CPU inference
- **CPU-only operation** (offloadKVCacheToGpu=false)

This confirms our current config is correct.

### 2. Model-Persona Affinity Map
Legacy architecture assigned models by tier:
- **Iris (voice)**: 0.6B model (fastest)
- **Pillar Keepers**: 1.7B models (balanced)
- **Oversouls**: 4B-Think models (reasoning)
- **Prometheus**: 8B model (complex)

**Current status**: Partially implemented. Qwen3-1.7B is primary. Qwen3-4B-Thinking available for reasoning.

### 3. System Prompts Library
Found at `~/Documents/docs_1/system-prompts/` (4 files) and `~/Documents/xnaif-files/system-prompts/`.
Contains prompts from Era 0-3 — some reusable for entity system prompts.

## Recommendations

1. **Port LM Studio configs** to KB (document optimal settings per model)
2. **Port model-persona affinity** to entity config documentation
3. **Discard** omega-stack-legacy bulk (33K files, minimal unique value)
4. **Reference** xna-omega patterns (circuit breaker, provider FSM) — already ported
5. **Archive** foundation-legacy (historical only)
