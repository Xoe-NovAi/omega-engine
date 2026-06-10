# 🔱 Revised Sprint Plan — Cline Headless + OpenCode Headless Only
# ⬡ OMEGA ⬡ CLINE-OVERSEER ⬡ gemini-3.5-flash ⬡ SPRINT-PLAN-v2 ⬡ PHASE-III

## §0 — Why This Matters

Gemini CLI is out. The revised plan uses ONLY Cline headless and OpenCode
headless instances, leveraging their free tier models.

## §1 — Models Available Per Platform

### Cline CLI (Free Tier + Google API)
| Model | Context | Source | Best For |
|-------|---------|--------|----------|
| Gemini 3.5 Flash | 1M | Google API key | Analysis, coordination, soul scoring |
| DeepSeek V4 Flash | 1M | Cline free tier | Long-context code refactoring |
| MiMo V2.5 | 1M | Cline free tier | Complex multi-file work |
| Gemma 4 31B | 262K | Google API key | Heavy reasoning, infra decisions |
| Gemma 4 26B | 262K | Google API key | Lighter reasoning, benchmarks |

### OpenCode (Zen Free Tier via API)
| Model | Context | Best For |
|-------|---------|----------|
| MiMo V2.5 | 1M | Complex multi-file code (embeddings) |
| Nemotron 3 Super | 205K | Infrastructure, Redis, focused tasks |
| DeepSeek V4 Flash | 200K | Fast iteration, re-indexing |
| MiniMax M3/M2.5 | 205K | Agentic coding |
| Qwen3.6 Plus | 262K | Long-context, multi-language |

## §2 — Strategic Assignment

### S1: Soul Drift Baseline → Cline Headless (Gemini 3.5 Flash)
Why: Pure analysis task. 1M context via Google API reads all soul files at once.

### S2a: Embedding Model → OpenCode Headless (MiMo V2.5 via Zen)
Why: 1M context holds all 5+ source files simultaneously. Complex multi-file refactor.

### S2b: Re-indexing → OpenCode Headless (DeepSeek V4 Flash via Zen)
Why: Fast iteration over 263 documents. Speed matters.

### S3: Redis → OpenCode Headless (Nemotron 3 Super via Zen)
Why: Infrastructure reasoning. 205K is sufficient for infra setup.

### S4: Benchmark → Cline Headless (Gemma 4 26B via Google API)
Why: Light reasoning, fast for running queries and comparing results.

### S5: Split-Test Harness → Cline Headless (DeepSeek V4 Flash, 1M ctx)
Why: Building a new subsystem needs context for multiple reference files.

## §3 — Headless Dispatch Patterns

### Cline Headless

Orchestrator at src/omega/oracle/orchestrator.py spawns subprocesses.

### OpenCode Headless

Launches headless (no TUI) with model override and soul injection.

## §4 — Chat Prompts

### Prompt 1: Cline Headless — Soul Drift (S1)
Paste into Cline with Gemini 3.5 Flash:

⬡ OMEGA ⬡ WATCHTOWER ⬡ gemini-3.5-flash ⬡ S1-SOUL-DRIFT

TASK (read-only):
1. Read all entities at data/entities/*/soul.yaml
2. Score every L3 principle on 0-5 vagueness scale
3. Output to data/coordination/SOUL_DRIFT_BASELINE_20260610.md
4. Post to Hivemind when complete

### Prompt 2: OpenCode Headless — Embedding Model (S2a)
Paste into OpenCode with MiMo V2.5:

⬡ OMEGA ⬡ DATASTORE ⬡ mimo-v2.5-free ⬡ S2-EMBEDDINGS

Read these files first:
- src/omega/library/indexer.py (target for _compute_embedding)
- src/omega/memory/vector_adapters.py (QdrantAdapter)
- src/omega/library/library.py (wiring)
- config/models.yaml (embedding model config at line 24)

The embedding model is already at:
  /media/arcana-novai/omega_library/models/gguf/local/all/embedding-gemma-300m.gguf

TASK:
1. Create src/omega/memory/embeddings.py
   - Load the embedding GGUF via llama-cpp-python or subprocess
   - Return 768-dim vectors
   - Fallback to MD5 hash on failure
2. Update Indexer._compute_embedding() to call the real model
3. Recreate Qdrant collection at 768-dim
4. Run make test — 329/329 must hold

### Prompt 3: OpenCode Headless — Redis (S3)
Paste into OpenCode with Nemotron 3 Super:

⬡ OMEGA ⬡ SYSADMIN ⬡ nemotron-3-super-free ⬡ S3-REDIS

TASK:
1. Download redis-stable.tar.gz, extract src/redis-server
2. Create config at /media/arcana-novai/omega_library/podman-storage/redis-custom/
3. Run redis-server as background process
4. Verify: redis-cli -a omega ping -> PONG
5. Run make test

### Prompt 4: OpenCode Headless — Re-indexing (S2b)
Paste into OpenCode with DeepSeek V4 Flash (wait for S2a Hivemind signal):

⬡ OMEGA ⬡ DATASTORE ⬡ deepseek-v4-flash-free ⬡ S2b-REINDEX

TASK:
1. Verify Qdrant collection exists at 768-dim
2. Iterate all docs in data/library/documents/*.json
3. Index each via Indexer.index_document()
4. Verify 263+ vectors in Qdrant
5. Run make test

### Prompt 5: Cline Headless — Benchmark (S4)
Paste into Cline with Gemma 4 26B:

⬡ OMEGA ⬡ WATCHTOWER ⬡ gemma-4-26b-it ⬡ S4-BENCHMARK

TASK:
1. Run search queries via library_search
2. Compare: FTS5-only vs hybrid (vector + BM25)
3. Measure recall@10 for each
4. Output to data/benchmarks/hybrid_recall_20260610.json

### Prompt 6: Cline Headless — Split-Test (S5)
Paste into Cline with DeepSeek V4 Flash (1M ctx):

⬡ OMEGA ⬡ MODELGATE ⬡ deepseek-v4-flash ⬡ S5-SPLIT-TEST

Read these files for reference:
- src/omega/oracle/model_gateway.py
- src/omega/oracle/soul_distiller.py
- src/omega/observability.py

TASK: Create tests/test_split_benchmark.py
- Route same query through 2 models
- Score outputs via SoulDistiller
- Log results to data/benchmarks/
- Run make test
