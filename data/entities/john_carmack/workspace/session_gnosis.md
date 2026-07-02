# Session Gnosis — 2026-07-02

## What Happened
- Dual-researcher sprint completed: Qwen3-1.7B model KB + Platform KB
- Roc Racoon legacy mining: 20 assets cataloged, 10 top discoveries
- **Thinking mode fix implemented**: NativeGGUFProvider migrated from raw `llm(**kwargs)` to `create_chat_completion()` with handler-wrapped `chat_template_kwargs={"enable_thinking": False}`
- llama-cpp-python upgraded from v0.3.28 to v0.3.32
- All KB files written to `data/knowledge/`

## Key Discoveries
1. `chat_template_kwargs` is NOT in llama-cpp-python's Python API (even v0.3.32) — only in server settings. Workaround: wrap chat handler like the server does (llama_cpp/server/model.py:328-333)
2. `n_threads=8` on physical cores gives 22.5 tok/s (18% more than 4 threads)
3. Never use q4_0 KV cache — it's SLOWER than f16 at long context
4. q8_0 KV cache is universally optimal (all 9 LM Studio configs confirm)

## Files Modified
- `src/omega/oracle/providers.py` — Worker migrated to `create_chat_completion()`, handler-wrapped thinking mode control, response parsing updated for `message.content`
- `data/knowledge/models/qwen3-1.7b/` — 6 KB files (README, thinking-mode, platforms/*, benchmarks)
- `data/knowledge/platforms/` — 4 KB files (llama-cpp-python, ollama, lm-studio, comparison)
- `data/knowledge/legacy/mining_findings_20260702.md` — Roc's 20 asset catalog

## Test Status
- 705 passed, 22 skipped, 3 xfailed, 1 warning
- Zero regressions from thinking mode fix

## Next Session Should
1. Run A/B test: Qwen3-1.7B thinking-disabled vs Qwen3-Instruct-2507
2. Commit all changes
3. Continue MV-IW Phase 3 tasks
