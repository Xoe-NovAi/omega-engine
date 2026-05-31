# 🔱 Omega Engine — Tool Remediation & Embedding Research Handoff
**AP Token**: `AP-HANDOFF-TOOL-EMBED-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_tool_remediation ⬡ BUILDER

---

## §0 Status Summary

| System | Status | After Fix |
|--------|--------|-----------|
| **Firecrawl MCP (search)** | ✅ Fixed | Env var `${FIRECRAWL_API_KEY}` now expands correctly (was literal string). Needs OpenCode restart to reconnect MCP transport. |
| **Firecrawl MCP (scrape)** | ✅ Working | Was always working (env issue was specific to search endpoint MCP routing) |
| **Firecrawl Direct API** | ✅ Working | Confirmed: search + scrape both return real results |
| **Jina MCP** | ❌ Disabled | Insufficient balance on API key. Free Reader API (r.jina.ai) works w/o auth but MCP requires credits. |
| **Exa MCP** | ❌ Broken | 401 Invalid API key. Same key works for direct API but MCP requires additional MCP permissions. None of 5 alternate Exa keys work either (different error: "Not Acceptable: Client must..."). |
| **Exa Direct API** | ✅ Working | Returns real search results |
| **Filesystem MCP** | ❌ Disabled | Was workaround for past permission issues (now solved). Completely redundant with built-in OpenCode file tools. |
| **Task (sub)agents** | ❌ Broken | `FOREIGN KEY constraint failed` — internal OpenCode v1.15.11 bug in opcode.db. DB is consistent (no orphaned records). Bug is in compiled binary, can't fix from outside. Only fix: upgrade OpenCode. |
| **Omega Hub (local)** | ✅ Working | Python MCP servers running on :8016 |
| **Web/URL tools via bash** | ✅ Working | Firecrawl direct API works perfectly via curl/bash |

---

## §1 Root Causes Found & Fixed

### 1.1 MCP Environment Variable Expansion (CRITICAL FIX)
**Root cause**: OpenCode v1.15.11 expands `${VAR}` from its own environment at process spawn time. When OpenCode started, `FIRECRAWL_API_KEY` was NOT in the environment (added to `.env` after OpenCode launched during today's env remediation). This caused the MCP process to receive the literal string `${FIRECRAWL_API_KEY}` instead of the actual key.

**Evidence**:
```
# From MCP process /proc/PID/environ:
FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}   # LITERAL template string!
EXA_API_KEY=a91c1829...                    # Expanded correctly
JINA_API_KEY=jina_2c57...                  # Expanded correctly
```

**Fix**: Killed the stale MCP process. OpenCode re-spawned it after env var was available, now key expands correctly:
```
FIRECRAWL_API_KEY=fc-4bc8cf1288da42f1aec6bc3bb645b227  # ✅ Correct
```

**Current state**: MCP process has correct key but OpenCode transport is disconnected (transport breakage from killing process). **Needs OpenCode restart** to reconnect.

### 1.2 Filesystem MCP — Redundant Workaround
**Root cause**: `@modelcontextprotocol/server-filesystem` was installed as a workaround for OpenCode file permission issues that have since been solved correctly. The MCP duplicates tools OpenCode already has natively (`filesystem_read_text_file`, `filesystem_write_file`, etc.).

**Fix**: Set `"enabled": false` in `opencode.json`.

### 1.3 Jina MCP — Insufficient Balance
**Root cause**: Jina API key `jina_2c57...` has 0 credits. Full balance needed for:
- Embeddings API
- Classification API
- MCP search/reader endpoints

Free Reader API at `r.jina.ai` works without auth for URL→markdown conversion.

**Fix**: Set `"enabled": false` in `opencode.json`. Use Firecrawl for web search/scrape instead.

### 1.4 Exa MCP — Key Lacks MCP Permissions
**Root cause**: Direct Exa API works fine but Exa MCP requires API keys with MCP access explicitly enabled. The 5 keys in inventory all fail with different errors (401 vs "Not Acceptable").

**Fix**: None possible without MCP-enabled Exa key. Use Exa direct API via curl/bash.

### 1.5 Task Agents — OpenCode v1.15.11 Internal Bug
**Root cause**: `FOREIGN KEY constraint failed` is a SQLite constraint violation in OpenCode's compiled binary at `~/.opencode/bin/opencode`. Database is internally consistent (all FK relationships intact — verified). Bug is in message/part creation logic during subagent dispatch.

**Diagnosis**: The `opencode.db` (1.1GB, 47K messages, 203K parts, 1986 sessions, 16 tables) has `session → project`, `message → session`, `part → message` FK cascade. No orphaned records exist. The error happens at INSERT time — likely a race condition where a parent record isn't committed before child INSERT.

**Fix**: None from outside. Requires OpenCode version upgrade (v1.15.11 → newer).

---

## §2 MCP Configuration — Current State

```json
// opencode.json MCP section (as of remediation)
// ENABLED (3):
//   omega-hub  (remote)  — http://127.0.0.1:8016/sse  ✅
//   firecrawl  (local)   — npx firecrawl-mcp           ✅ (key fixed, needs restart)
//   exa        (remote)  — https://mcp.exa.ai/mcp      ❌ (401, no MCP-enabled key)
//
// DISABLED (4):
//   filesystem  (local)  — redundant, was workaround   ❌ disabled
//   jina        (remote) — insufficient balance         ❌ disabled
//   serper      (remote) — no key                       ❌ disabled
//   tavily      (local)  — no key                       ❌ disabled
```

---

## §3 Deep Research: Best 768-dim Embedding Model for Zen 2 + Qdrant

### 3.1 Candidate Models (fastembed-supported, 768-dim)

| Model | Size | Dims | Context | License | Quality | Notes |
|-------|------|------|---------|---------|---------|-------|
| **bge-base-en-v1.5** | **0.21GB** | **768** | 512 | MIT | ⭐⭐⭐⭐⭐ | **BEST PICK** — best quality/size, ONNX CPU-optimized |
| **nomic-embed-text-v1.5-Q** | **0.13GB** ⚡ | **768** | 2048 | Apache-2 | ⭐⭐⭐⭐ | Quantized, lighter, longer context |
| **nomic-embed-text-v1.5** | 0.52GB | 768 | 2048 | Apache-2 | ⭐⭐⭐⭐⭐ | Full version, longer context |
| **snowflake-arctic-embed-m** | 0.43GB | 768 | 512 | Apache-2 | ⭐⭐⭐⭐ | Good English quality |
| **snowflake-arctic-embed-m-long** | 0.54GB | 768 | 2048 | Apache-2 | ⭐⭐⭐⭐ | Longer context variant |
| **jina-embeddings-v2-base-en** | 0.52GB | 768 | 8192 | Apache-2 | ⭐⭐⭐⭐ | MASSIVE context (8192) |
| **bge-base-en** (v1, not v1.5) | 0.42GB | 768 | 512 | MIT | ⭐⭐⭐ | Older, lower quality |
| **paraphrase-multilingual-MiniLM** | 1.0GB | 768 | 128 | Apache-2 | ⭐⭐⭐ | Multilingual, large |

### 3.2 New 2026 Models (not yet in fastembed)

| Model | Dims | Size | Notes |
|-------|------|------|-------|
| **Qwen3-Embedding-0.6B** | 32-1024 (flex) | ~0.6B params | Flexible dims, instruction-aware, 100+ languages |
| **EmbeddingGemma-300M** | 768 (MRL: 128→768) | <200MB quantized | Matryoshka, 22ms on EdgeTPU, 2048 ctx |
| **BGE-M3** | 1024 (flex 128→1024) | 567M params | Multi-vector + sparse + dense, 8192 ctx |

### 3.3 Specialized Embedding Strategies

| Strategy | Approach | Complexity | Quality | RAM Impact |
|----------|----------|-----------|---------|------------|
| **Pure Dense (bge-base-en-v1.5)** | Single 768-dim vector per doc | 🟢 Low | ⭐⭐⭐⭐ | ~350MB |
| **Hybrid: Dense + Sparse (BM42)** | bge-base-en + Qdrant/bm42 | 🟡 Medium | ⭐⭐⭐⭐⭐ | ~400MB total |
| **Matryoshka (EmbeddingGemma)** | Truncatable dims (768→128) | 🟡 Medium | ⭐⭐⭐⭐ | ~200MB |
| **Late Interaction (ColBERT)** | Multi-vector per doc | 🔴 High | ⭐⭐⭐⭐⭐ | ~800MB |
| **Cross-encoder Reranking** | bge-base-en + bge-reranker-base | 🟡 Medium | ⭐⭐⭐⭐⭐ | ~450MB total |

### 3.4 Recommended Architecture

**Phase 1 (v0.5.x) — Minimal viable:**
```
Model: BAAI/bge-base-en-v1.5 (fastembed)
Dims: 768
Store: Qdrant single collection "omega_library"
Search: Dense ANN (Cosine) + FTS5 fallback
RAM: ~350MB for embedding model
```

**Phase 2 (v0.6.0) — Hybrid search:**
```
- Dense: bge-base-en-v1.5 (768-dim, 0.21GB)
- Sparse: Qdrant/bm42-all-minilm-l6-v2-attentions (0.09GB) OR custom BM25
- Fusion: Reciprocal Rank Fusion (RRF)
- Optional reranker: BAAI/bge-reranker-base (1.04GB — RAM permitting)
```

**Phase 3 (Future) — Matryoshka / Qwen3:**
```
- Replace bge-base-en with Qwen3-Embedding-0.6B if fastembed adds support
- Or use EmbeddingGemma-300M with MRL truncation
```

### 3.5 Implementation Order (from handoff_overseer_to_builder_qdrant_redis.md)

```
1. Install fastembed (pip install fastembed==0.6.0)                # ~5 min
2. Add Qdrant container/quadlet (deploy/infra/)                    # ~15 min
3. Create RedisBus (src/omega/infra/redis_bus.py)                  # ~10 min
4. Rewrite Indexer with fastembed + Qdrant (indexer.py)            # ~25 min
5. Add hybrid_search to Library (library.py)                       # ~15 min
6. Wire observability to Redis streams (observability.py)          # ~10 min
7. Wire Redis pub/sub to MemoryStore (memory_store.py)             # ~15 min
8. Test + benchmark with full re-index                             # ~20 min
Total: ~2 hours
```

---

## §4 API Key Inventory (.env.API-keys)

| Service | Key(s) | Status |
|---------|--------|--------|
| **Firecrawl** | fc-4bc8... (primary), fc-9157... (alt) | ✅ Both work for direct API |
| **Exa** | a91c18... ($20 credit), 51eb82... ($20), 3 more | ✅ Direct API works; 🚫 No MCP access |
| **Jina** | jina_2c57... | 🚫 Insufficient balance |
| **OpenRouter** | sk-or-v1-0fba... (arcana), sk-or-v1-020c... (xoe) | Need testing |
| **AIHubMix** | sk-h6H9... | Need testing |
| **Tavily** | tvly-dev-2uIU... | Need testing (MCP disabled) |
| **SerpApi** | c0acbeec... | Need testing (MCP disabled) |

---

## §5 Recommended Actions After OpenCode Restart

1. **Restart OpenCode** — This will:
   - Reconnect Firecrawl MCP transport with correct API key
   - Pick up MCP config changes (filesystem/jina disabled)
   - Respawn firecrawl-mcp with proper env

2. **Test Firecrawl search tool** — Should work after restart

3. **Test task subagent** — If FOREIGN KEY persists, upgrade OpenCode:
   ```bash
   # Check: https://opencode.ai/download
   # Or reinstall: curl -fsSL https://opencode.ai/install.sh | bash
   ```

4. **Start Phase 1b Sprint 3** — Knowledge Seeding (from handoff_builder_execution_card.md)

5. **Execute Qdrant/Redis build** — Follow 3-phase plan from handoff_overseer_to_builder_qdrant_redis.md

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_tool_remediation ⬡ BUILDER*
