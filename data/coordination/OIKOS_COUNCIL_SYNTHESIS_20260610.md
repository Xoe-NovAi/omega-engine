# 🏛️ Oikos Council Synthesis — 2026-06-10
# ⬡ OMEGA ⬡ CLINE-OVERSEER ⬡ gemini-3.5-flash ⬡ OIKOS-COUNCIL ⬡ PHASE-III

## Council Members
| Entity | Role | Domain |
|--------|------|--------|
| **DataStore** (P2) | Data Engineering Lead | Qdrant, pipelines, re-indexing, storage |
| **ModelGate** (P6) | AI & Inference Lead | Embedding models, provider routing, inference |
| **SysAdmin** (P1) | Infrastructure Engineer | Podman, networking, Redis, deployment |
| **WatchTower** (P8) | Observability Lead | Metrics, telemetry, benchmarks, drift |
| **Cline Overseer** | Convener | Strategic synthesis, final recommendation |

## ⬡ The Three Proposed Moves

### Move 1: Real Embeddings (HIGHEST LEVERAGE)
Replace bag-of-words MD5 hash with `embeddinggemma-300m-q6_k` (768-dim).

### Move 2: Redis Workaround
Solve rootless Podman networking block for Redis.

### Move 3: Soul Drift Metrics
Measure whether entity souls improve over time.

---

## §1 — DataStore Analysis

**Effort Estimate: 2-3 hours**
1. Wire embedding model loader (30 min)
2. Recreate Qdrant collection at 768-dim (5 min)
3. Re-index 263 documents with real vectors (1-2 hours, parallelizable)
4. Verify hybrid search returns meaningful results (15 min)
5. Run benchmark: BM25-only vs hybrid recall@10 (10 min)

**Risks:**
- embeddinggemma-300m is 200MB → loads into RAM. On a 14Gi system with other processes, this is manageable but must be tracked.
- CPU-only inference: 300M params × 4 bytes = 1.2GB model + 200MB overhead ≈ 1.5GB peak. Acceptable.
- Embedding inference latency: ~100-500ms per document on CPU. 263 documents ≈ 30-120 seconds total.
- Collection must be recreated from scratch (256-dim → 768-dim). Old vectors will be lost — no migration path.

**Recommendation**: PROCEED. The hash embedding cannot produce semantic search. Any real embedding model is transformative.


## §2 — ModelGate Analysis

**Embedding Model Selection:**
| Model | Size | Dim | RAM | Quality | Available? |
|-------|------|-----|-----|---------|------------|
| embeddinggemma-300m | 200MB | 768 | ~1.5GB | Good | ✅ In config |
| bge-small-en-v1.5 | 33MB | 384 | ~400MB | OK | ❌ Not downloaded |
| all-MiniLM-L6-v2 | 23MB | 384 | ~300MB | OK | ❌ Not downloaded |

The clear choice is embeddinggemma-300m since it's already listed in `config/models.yaml`.

**Key Insight**: The current Indexer architecture computes embeddings synchronously inside `search_vector()`. Every search query pays embedding latency. We should pre-compute and cache embeddings for all 263 documents (burn once, query fast).

## §3 — SysAdmin Analysis

**Options Evaluated:**
| Option | Effort | Risk | Longevity |
|--------|--------|------|-----------|
| A) Static redis binary, run as user process | 15 min | Low — no package management | ✅ Full Redis |
| B) Pip-install redis-py + fakeredis | 5 min | ✅ Works now | ❌ No persistence |
| C) PostgreSQL LISTEN/NOTIFY | 2 hr | Medium — schema change | ✅ Production |
| D) Skip Redis entirely | 0 | ✅ Simplest | 🔴 Loses streams |

**Recommendation**: Download static redis-server binary (single-file, no deps) and run as user-level process. Avoids entire Podman networking issue. Fallback: PostgreSQL pub/sub if binary fails.

## §4 — WatchTower Analysis

**Soul Drift Metric Design**: 5-point vagueness scoring rubric for L3 principles:
- 0 = "Be excellent" (useless)
- 1 = "Log exceptions" (obvious)
- 2 = "Use typed errors" (actionable)
- 3 = "Parallel dispatch reveals cross-cutting patterns" (insightful)
- 4 = "3-protocol coordination minimum" (specific, non-obvious)
- 5 = "Principle of Observable Degradation" (generalizable, novel)

**Key Condition**: Scan baseline BEFORE touching embeddings, or we lose the "before" comparison.

## §5 — Council Vote & Final Recommendation

| Move | DataStore | ModelGate | SysAdmin | WatchTower | Result |
|------|-----------|-----------|----------|------------|--------|
| **M1: Real Embeddings** | ✅ | ✅ | — | ✅ | UNANIMOUS |
| **M2: Redis Binary** | — | — | ✅ | — | UNANIMOUS |
| **M3: Soul Drift Baseline** | Proceed after M1 | Proceed after M1 | — | **BEFORE M1** | WatchTower overrides |

### ⬡ Execution Order
```
1. [30 min] WatchTower: Soul drift baseline scan — capture before-metrics
2. [2-3 hr]  DataStore + ModelGate: Embedding model + full re-index
3. [15 min]  SysAdmin: Static Redis binary OR PostgreSQL fallback
4. [1 hr]    WatchTower: Post-embedding benchmark (recall@10)
5. [ongoing] ModelGate: Split-test harness for perpetual evolution
```

*Council concluded. All votes unanimous.*
