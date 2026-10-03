<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# BENCH_MINING_EARLY — Delta Report (Session Paging Batch 2)

**Entity**: roc_racoon | **Date**: 2026-08-21 | **Channel**: opencode
**Mission**: Legacy local-model benchmark mining, EARLY pass (V-1 Vault support)
**Sibling**: BENCH_MINING (later pass, paged in parallel) — this file covers ONLY early-pass-unique material.
**Status**: IN_PROGRESS

## 1. Unique Early-Pass Findings (unlikely in later pass)

**LM Studio per-model configs** (`~/.lmstudio/.internal/user-concrete-model-default-config/local/all/*.json`, 9 files, all read in full):
- Krikri-8B-Instruct.Q4_K_M: ctx=2856, offloadRatio=0.15625, cpuThreadPoolSize=8, keepModelInMemory=true
- Qwen3-4B-Thinking-2507-Q4_K_M: ctx=26674 (largest), cpuThreadPoolSize=6
- RocRacoon-3b.Q4_K_M: ctx=12464
- Phi-4-mini-reasoning-heretic-i1-Q5_K_M: ctx=12502, offloadRatio=0.5625, keepModelInMemory=false
- Phi-4-mini-instruct-Q5_K_M: ctx=6608 | Ministral-3-3B: ctx=6324 | Qwen3-1.7B-UD-Q4_K_XL: ctx=6153 | Qwen3-VL-4B: ctx=8369, offloadRatio≈0.361
- UNIVERSAL pattern: KV cache q8_0 (k+v) on ALL 9; flashAttention on 5; offloadKVCacheToGpu=false except 2. This is the de-facto tuned baseline matrix for the new benchmark infra.

**query_test.py** (Old-Stacks/Xoe-NovAi/scripts/, 538 lines, full read): complete RAG benchmark harness — DEFAULT_QUERIES[10], measure_query() w/ psutil memory delta, run_benchmark() stats (min/max/mean/median/p95), targets: token rate 15–25 tok/s, p95<1000ms, mem<6GB, cache hit>50%; JSON export + exit-code gating on targets; embedded pytest block + self-critique footer.

**ANai_v4.27.1_Claude snapshot found INSIDE Grok export** (non-obvious location): grok-accounts-exports/Antipode2727/ttl/30d/export_data/<uuid>/prod-mc-asset-server/1e7ab850…/content — Era-1 stack with FULL llama.cpp tuning: N_CTX=2048, N_BATCH=512, N_GPU_LAYERS=0, MALLOC_ARENA_MAX=4, ANAI_TEMPERATURE=0.7, TOP_P=0.95, TOP_K=50, REPEAT_PENALTY=1.1; model gemma-3-4b-it-UD-Q5_K_XL.gguf.

**config.toml v0.1.4-stable→v0.1.5** (Old-Stacks root): [performance] codified targets — token_rate_min/target/max=15/20/25, memory_limit_bytes=5GiB, latency_target_ms=1000, cpu_threads=6, f16_kv_enabled=true; llm=gemma-3-4b-it-UD-Q5_K_XL, embedding=all-MiniLM-L12-v2.Q8_0 (384-dim).

**Ollama history**: ~24 prompts, mostly persona/context probes of "Krikri"; only bench-relevant item = "How do I add a local gguf model to Ollama". No quantitative runs.

**RocRacoon Test v1**: qualitative role-fit test; subject model misidentified itself as "Microsoft Phi (formerly GPT-3)" and confused RAG with RAID — earliest recorded eval-failure datum.

## 2. Sources & Methods — Succeeded / Failed

**SUCCEEDED**:
- Direct read of all 9 LM Studio JSON configs — intact, parseable, highest signal-per-KB of any source.
- Stack-cat snapshots hidden inside Grok export asset-server `content` files (no extension). Heuristic: largest content files (92KB/178KB/224KB) = full stack concatenations. ANai_v4.27.1_Claude recovered this way.
- Old-Stacks scripts/query_test.py + config.toml full reads — the only true benchmark code found in Era 1–3.
- xnai_guide_updates_comprehensive.md §6.2/§10.4: Ryzen env block (N_THREADS=6, F16_KV, MLOCK, MMAP, OMP=1, OPENBLAS=1, CORETYPE=ZEN, MKL_DEBUG_CPU_TYPE=5) + perf-benchmark checklist (15–25 tok/s, <6GB, <1000ms p95, crawl 50–200 items/h).
- ingest_library.py (stack-cat-v0_1_2-full): chunk_size=2000/overlap=200, tenacity retry(3), Redis TTL 86400, LlamaCppEmbeddings n_threads=6.

**FAILED / FRICTION**:
- Paths with spaces ("from main partition", "Old XNAi guides") errored on first read attempts; required quoting.
- omega_vault XNAi-v0_1_2 absent under expected name — actual dirs are "(Copy)"/"(Copy 2)" variants.
- xnaif-files/system-prompts/experts near-empty; docs_1 assistants/cline empty. Prompt-library yield lower than inventory claimed.
- docs_1 owned by UID 101000 (:U chown damage signature — M6/D144 relevance, readable but flagged).
- prod-grok-backend.json (2.4MB/account × 8) sampled only, never parsed structurally.

## 3. Flagged Important — Never Executed

1. **PRIMARY GAP**: Mission output `data/coordination/ROC_LEGACY_BENCHMARK_MINING_20260816.md` was NEVER WRITTEN. Early pass ended at synthesis stage; all §1 findings exist only in session transcript. This delta file is their first durable record.
2. **Grok 8-account deep dive** (D-386: 274 convos / 6565 responses): untouched beyond 2 content-file samples. Model-evaluation conversations likely still buried there.
3. **foundation-legacy 861MB** (`~/archive/foundation-legacy/versions/Xoe-NovAi/`): listed, never traversed. Contains UPDATES_RUNNING.md (70KB) + versions/ tree unexamined.
4. **docs-backup TASK-5A-1…5** (ZRAM/NUMA/kernel baseline collection + stress test docs, 01-strategic-planning/): flagged as hardware-tuning-relevant during pass; never mined. Directly feeds benchmark infra's Ryzen section.
5. **wheelhouse.tgz (566MB)** in Xoe-NovAi old versions: noted, skipped.
6. **Quantization comparison**: NO Q4-vs-Q5-vs-Q8 throughput benchmarks found anywhere in early-pass sources — only config choices (Q5_K_XL LLM / Q8_0 embeddings / q8_0 KV). Gap confirmed, not filled.

## 4. Completion

File complete: 4 sections, written incrementally per paging discipline. No other files created.

<!-- END -->

