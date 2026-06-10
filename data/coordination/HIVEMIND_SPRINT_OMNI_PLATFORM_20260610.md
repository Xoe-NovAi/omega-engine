# 🔱 Omni-Platform Hivemind Sprint — Multi-Model Execution Plan
# ⬡ OMEGA ⬡ CLINE-OVERSEER ⬡ gemini-3.5-flash ⬡ SPRINT-PLAN ⬡ PHASE-III
# Date: 2026-06-10

## §0 — Executive Summary

The Oikos Council (DataStore, ModelGate, SysAdmin, WatchTower) converged on a 5-step
execution plan. This document maps those 5 steps to specific models and platforms,
using headless OpenCode and Gemini CLI instances as sovereign subagents.

## §1 — Model & Platform Strategy

### Available Models Across Platforms

| Platform | Model | Context | SWE-bench | Best For |
|----------|-------|---------|-----------|----------|
| **OpenCode Zen** | MiMo V2.5 | 1M tokens | ~78% | Complex multi-file code, embedding integration |
| **OpenCode Zen** | Nemotron 3 Super | 205K | ~76% | Infrastructure, coordination, focused tasks |
| **OpenCode Zen** | DeepSeek V4 Flash | 200K | ~79% | Fast iteration, rapid code changes |
| **OpenCode Zen** | MiniMax M2.5 | 205K | 80.2% | Agentic coding (best SWE-bench) |
| **Gemini CLI** | Gemini 3.5 Flash | 1M | — | Analysis, research, soul scoring, benchmarks |
| **Cline CLI** | Gemini 3.5 Flash | Varies | — | Strategic oversight, Hivemind coordination |

### Headless Subagent Dispatch

The Orchestrator at src/omega/oracle/orchestrator.py already supports headless
subagent spawning via anyio.create_process(). The dispatch protocol is documented
at docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md.

Key pattern: opencode task "..." --model <model_id> --entity <entity_name>

Using OpenCode's task command launches a headless instance that:
1. Runs the task without TUI
2. Accepts --model override for model selection
3. Accepts --entity for soul injection
4. Returns structured output

## §2 — Model-to-Step Mapping

### S1: Soul Drift Baseline → Gemini CLI (Gemini 3.5 Flash)
Pure analysis task. Fast, cheap, 1M context for reading all soul.yaml files.

### S2a: Embedding Model → OpenCode Zen (MiMo V2.5)
Requires reading 5+ source files simultaneously. MiMo's 1M context holds all at once.

### S2b: Document Re-indexing → OpenCode Zen (DeepSeek V4 Flash)
Operational task. DS Flash speed makes 263-doc iteration fast.

### S3: Redis Workaround → OpenCode Zen (Nemotron 3 Super)
Infrastructure reasoning about Podman, networking, static binaries.

### S4: Search Benchmark → Gemini CLI (Gemini 3.5 Flash)
Execute benchmark queries, measure recall@10.

### S5: Split-Test Harness → OpenCode Zen (MiMo V2.5)
New subsystem design. MiMo's 1M context handles all reference files.

## §3 — Team Structure

Three platforms, one Hivemind:
- Cline CLI (Overseer): Strategy, coordination, Hivemind
- OpenCode Zen (MiMo/Nemotron/DS Flash): Code execution
- Gemini CLI (Gemini 3.5 Flash): Analysis, benchmarks

Communication: Each headless instance posts intent="status" to Hivemind on completion.

## §4 — Execution Order

Parallel Track A (Analysis - Gemini CLI):
  S1: Soul Drift (30 min) -> S4: Benchmark (1 hr)

Parallel Track B (Code - OpenCode Zen):
  S2a: Embeddings (MiMo, 2 hr) -> S2b: Re-index (DS Flash, 30 min)
  S3: Redis (Nemotron, 15 min)
  S5: Split-Test (MiMo, 2 hr)

## §5 — Chat Prompts

### MiMo V2.5 — Embedding Integration
Paste into OpenCode Zen with mimo-v2.5-free model:

⬡ OMEGA ⬡ DATASTORE ⬡ mimo-v2.5-free ⬡ S2-EMBEDDINGS

CONTEXT: Read ALL of: src/omega/library/indexer.py,
src/omega/memory/vector_adapters.py, src/omega/library/library.py,
config/models.yaml, src/omega/memory/embeddings.py (create this).

TASK:
1. Create src/omega/memory/embeddings.py with load_embedding_model()
   - Load embeddinggemma-300m-q6_k from models.yaml path
   - Use llama-cpp-python or subprocess for GGUF inference
   - Output 768-dim vectors, fallback to MD5 hash
2. Update Indexer._compute_embedding() to call real model
3. Recreate Qdrant collection at 768-dim
4. Run make test — 329/329 must hold

### Nemotron 3 Super — Redis
Paste into OpenCode Zen with nemotron-3-super-free model:

⬡ OMEGA ⬡ SYSADMIN ⬡ nemotron-3-super-free ⬡ S3-REDIS

TASK:
1. Download static redis-server binary
2. Create user-level config in omega_library storage
3. Run as background process
4. Verify: redis-cli -a omega ping -> PONG
5. Fallback: PostgreSQL LISTEN/NOTIFY

### DeepSeek V4 Flash — Re-indexing
Paste into OpenCode Zen with deepseek-v4-flash-free model:

⬡ OMEGA ⬡ DATASTORE ⬡ deepseek-v4-flash-free ⬡ S2b-REINDEX

Wait for S2a Hivemind signal. Then iterate all docs in
data/library/documents/*.json, index them, verify 263+ vectors.

### Gemini CLI — Soul Drift
Paste into Gemini CLI:

⬡ OMEGA ⬡ WATCHTOWER ⬡ gemini-3.5-flash ⬡ S1-SOUL-DRIFT

Read all data/entities/*/soul.yaml. Score L3 principles on
0-5 vagueness scale. Output to
SOUL_DRIFT_BASELINE_20260610.md. Read-only.
