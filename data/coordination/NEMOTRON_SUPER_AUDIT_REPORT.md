# 🔱 Nemotron-3-Super Audit Report
**Recovered**: 2026-07-07 from `git log 9d439bd`
**Original Author**: OpenCode agent session (Nemotron 3 Ultra)
**Source**: Commit `9d439bd` — "fix: full fact-check with Nemotron 3 Ultra + OpenCode Zen catalog verified"

---

## Recovered Commit Body

You were right to call me out. I missed Nemotron 3 Ultra entirely, and
I made multiple errors about the user's actual environment.

### VERIFIED FACTS (2026-06-05, OpenCode Zen docs scraped directly)

### FREE TIER (4 models, all available now):
- opencode/deepseek-v4-flash-free
- opencode/mimo-v2.5-free
- opencode/nemotron-3-ultra-free
- opencode/big-pickle (stealth)

### PAID TIER (relevant subset):
- opencode/deepseek-v4-flash ($0.14 input / $0.28 output)
- opencode/minimax-m2.7 and m2.5 (NO M3!)
- opencode/gpt-5.x, claude-opus-4.x, claude-sonnet-4.x
- opencode/gemini-3.x, qwen3.7, glm-5.x, kimi-k2.5/k2.6

### NOT ON ZEN:
- Google Gemma (via Google AI Studio)
- Google Gemini (via Google AI Studio — but also on Zen)
- Anthropic Claude direct (but on Zen too)

### PREVIOUS ERRORS (now retracted):
- ❌ "MiniMax M3" — there is NO M3 on Zen. Only M2.7/M2.5.
- ❌ "deepseek-v4-flash pricing $0.28/M output" — correct but incomplete.
- ❌ Cost estimate "$2-4 for full refactor" — completely wrong.

### NEMOTRON 3 ULTRA VERIFIED SPECS (NVIDIA blog + HuggingFace):
- 550B total / 55B active (MoE)
- Hybrid Mamba-Transformer + LatentMoE
- NVFP4 quantization (5x throughput on Blackwell)
- 1M context (Ruler @1M = 95%)
- Agentic-tuned via Multi-Teacher On-Policy Distillation (10+ teachers)
- OpenMDW-1.1 license (Linux Foundation permissive)
- 4 variants: BF16, NVFP4, Base BF16, GenRM
- Benchmark: Terminal-Bench 2.0 = 54%, IFBench = 82%, PinchBench = 91%

### WHY DEEPSEEK V4 FLASH FREE REMAINED THE RECOMMENDATION:
- Only candidate with verified code benchmark (LiveCodeBench 91.6 Max)
- Nemotron's strengths (agentic, 1M context with 95% Ruler) were
  misaligned with the mechanical refactoring task profile

### WHEN TO USE NEMOTRON INSTEAD:
- Phase 2 deep review (heritage, multi-file analysis, long context)
- Any agentic multi-turn task
- When you need 1M context with verified 95% Ruler score

---

*Recovered from `git commit 9d439bd` — originally authored by Nemotron 3 Ultra via OpenCode.*
