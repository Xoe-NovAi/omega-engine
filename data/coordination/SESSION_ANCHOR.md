# 🔱 SESSION ANCHOR & GNOSIS — PRE-COMPACTION #3
**Date**: 2026-08-07 (evening)
**Entity**: Kali
**Status**: PRE-COMPACTION HANDOFF — B2+B3+B4 COMPLETE & COMMITTED; A5 INVESTIGATED, FIX NOT YET IMPLEMENTED

## 📋 What Was Done (session #2 post-compaction, in order)

### 1. Committed B2+B3 batch — `4b0eab6`
- 50 files: kv_types.py (new canonical map), providers.py + model_gateway.py wired to it, registry.py + models.py fixes, 38 model cards (gitignore negation), test_model_registry.py (27/27), matrix docs-sync
- Pre-commit checks passed

### 2. B4 — q8_0 KV-cache crash conditions — COMPLETE ✅ (committed `64d1052`)
Reconstructed from refactor-manual verified fragments + actual code (the `[GAP]` was never externally researchable). Two coupled defects:
- **Crash condition**: `NativeGGUFProvider._worker` forced `flash_attn=True` for ANY quantized KV cache (`type_k != 1 or type_v != 1`). System is CPU-only (`llama_supports_gpu_offload()` = **False** on this build; n_gpu_layers=0). Forcing `LLAMA_FLASH_ATTN_TYPE_ENABLED` on non-GPU llama_context crashes. **Fix**: gate flash_attn on `n_gpu_layers > 0 AND llama_supports_gpu_offload()` — verified False on this build, would be True on GPU builds.
- **RAM math mismatch**: `cpu_optimizer.estimate_model_ram()` defaulted `kv_quant="q8_0"` (scale 1.0); runtime NativeGGUFProvider defaults **f16** (scale 2.0). Real KV footprint ~2x admission math → admission could approve OOM loads. **Fix**: default `kv_quant="f16"` to match runtime. Verified `recommend_kv_cache()` + `get_ram_pressure()` already prefer f16 at low pressure (consistent).
- Test status: test_providers 24 pass / 5 pre-existing GoogleAI + 1 pre-existing stale (`test_init_default_kv_cache` asserts `None` vs code `1` — both f16; confirmed pre-existing on clean baseline via git stash)

### 3. A5 — StreamHandler unwired — INVESTIGATED, NOT YET FIXED
- `model_gateway.py:89` imports `StreamHandler, get_stream_handler` from `.stream_handler`
- `stream_handler.py` = 456 lines, class at line 51, module singleton `_stream_handler` at 449, `get_stream_handler()` at 452
- **NEXT SESSION**: read `model_gateway.py` `generate()` (the `_stream_generate`/SSE path) + `stream_handler.py` fully; decide WIRE (call handler in generate() to emit SSE chunks) vs DELETE (remove import + module if truly dead). Per matrix: "Wire to SSE router or delete"

## ✅ Committed this session
- `4b0eab6` fix(provider-fabric): B2 model registry + B3 KV cache types
- `64d1052` fix(provider-fabric): B4 q8_0 KV-cache crash conditions
- (earlier, still unpushed): `ea60fd2`, `54ea23a`, `9e2af3a`, `197c02f`

## ⚠️ Blocked (Requires Network / Sudo)
- Push 6 local commits — network unreachable
- G-1 Gemma free-tier workhorse — billing/OAuth/network
- W-1 WARP pool bring-up — network + sudo (script confirmed fixed)

## 🎯 Next Actions (post-compaction)
1. **A5**: StreamHandler wire-or-delete in `model_gateway.generate()`. Read `stream_handler.py` (456 lines) + the `generate()`/SSE path first. If wire: call handler with streamed chunks from `_stream_generate`; add test. If delete: remove import (model_gateway.py:89) + mark module deprecated or delete. Update matrix §6 A5 row. Commit + docs-sync.
2. **B7**: `RAM_TOTAL_MB` hardcoded 14GB → dynamic detection (cpu_optimizer.py; compendium §4.1 `detect_hardware_profile.py` pattern)
3. **B8**: batch-size recommendations (`get_recommended_batch_sizes()`) never applied — wire or delete
4. **B6**: CPU topology inconsistent (4+ core lists; 5700U single-CCX) → `detect_hardware_profile.py`
5. **B5**: speculative decoding scaffolded, never reaches `Llama()` — wire or delete
6. **B9**: Vulkan/iGPU offload path — implement or document-defer
7. **Generator safety**: rewrite `scripts/generate_providers_yaml.py` to merge (preserve maakali_routing/fallback_resolver/streaming) or mark deprecated — DO NOT run destructively
8. When network returns: push 6 commits, G-1, W-1

## 📁 Relevant Files
- `src/omega/oracle/stream_handler.py` — 456 lines; A5 target
- `src/omega/oracle/model_gateway.py` — imports StreamHandler at :89; A5 target
- `src/omega/oracle/providers.py` — B4 flash_attn gating (committed)
- `src/omega/oracle/cpu_optimizer.py` — B4 RAM default f16 (committed); B7/B8 targets
- `src/omega/oracle/kv_types.py` — canonical KV map (B3, committed)
- `docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md` — defect SSOT; A1/A2/A4/A6/B1/B2/B3/B4 FIXED; A5/B5/B6/B7/B8/B9 remaining
- `context_packs/provider-fabric-review/claude-response/OMEGA_PROVIDER_FABRIC_REFACTOR_MANUAL_v3-nova.ai.md` — B4 reconstruction source
- `tests/test_providers.py` — 24 pass, 6 pre-existing fail (5 GoogleAI + 1 stale kv default)
