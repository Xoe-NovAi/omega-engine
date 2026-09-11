# JC-EIS LFM vs Qwen Benchmark Status

## Current State (2026-09-11)
- **Briefing**: `data/coordination/GROKSTER_JC_EIS_BRIEFING_LFM_FLEET_20260901.md` ✅
- **Test Script**: `scripts/test_lfm_vs_qwen.py` ✅ (15.9KB, syntax validated)
- **LFM Model**: `/media/arcana-novai/omega_library/models/gguf/LFM2.5-2.6B-Q4_K_M.gguf` (1.67GB) ✅
- **Qwen Model**: `/media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf` (1.67GB) ✅
- **Current RAM**: 14GB total, 8.2GB available
- **Status**: **SCHEDULED** — awaiting RAM availability (Architect running heavy)

## Benchmark Protocol (from JC-EIS Briefing)
```bash
# Step 1: Start LFM only (default)
scripts/serve_native_gguf.sh start
# Should load LFM2.5-2.6B on port 1234

# Step 2: Run LFM test
.venv/bin/python scripts/test_lfm_vs_qwen.py --model lfm

# Step 3: Stop LFM
scripts/serve_native_gguf.sh stop

# Step 4: Override env var to use Qwen, restart
export OMEGA_NATIVE_GGUF_MODEL=Qwen3-1.7B-Q6_K.gguf
scripts/serve_native_gguf.sh start

# Step 5: Run Qwen test
.venv/bin/python scripts/test_lfm_vs_qwen.py --model qwen --port 1234
```

## Expected Results (Hypothesis)
| Metric | LFM2.5-2.6B | Qwen3-1.7B |
|--------|-------------|------------|
| Success Rate | 8/8 | 6-7/8 |
| Tokens/sec | ~35 | ~30 |
| RSS | ~2.5GB | ~2GB |
| Tool Call JSON | Clean | May need explicit examples |
| Instruction Following | Strong | Moderate |

## Trigger Condition
Run when Architect's RAM frees up (ASUS 16GB/32GB available) or HP RAM drops below 50% usage.

## Owner
**JC-EIS (John Carmack)** — per briefing handoff

## Related
- `data/coordination/GROKSTER_JC_EIS_BRIEFING_LFM_FLEET_20260901.md`
- `scripts/test_lfm_vs_qwen.py`
- `scripts/serve_native_gguf.sh` v2.0.0
- `config/model_fleet_operational.yaml` v2.0.0 (LFM as `agentic_local`)

---
*Generated: 2026-09-11 by Grokster CSS Turn 5*
