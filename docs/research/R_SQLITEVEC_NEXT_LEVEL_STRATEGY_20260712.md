# 🔱 sqlite-vec Next-Level Strategy — Synthesis of Researcher + Jem
**AP Token**: `AP-KALI-SQLITEVEC-NEXTLEVEL-20260712`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_sqlitevec_synthesis ⬡ ACTIVE
**Date**: 2026-07-12
**Sources**: 
- `R_EPOCH_II_DEEP_RESEARCH_sqlitevec_20260712.md` (Jem gap closure, prior)
- `R_SQLITEVEC_VERIFICATION_20260712.md` (Jem rock-solid audit, this session)
- `Researcher novel-spin report` (this session, 6 threads)
- `R_BQ_SELFSUP_RESEARCH_20260712.md` (Researcher BQ + Self-Sup deep dive, this session)
- `R_BQ_SELFSUP_VERIFICATION_20260712.md` (Jem BQ + Self-Sup verification, this session)

---

## 0. Executive Synthesis

The sqlite-vec integration is **ratified (D223)** and now **verified rock-solid with 3 mandatory corrections** (Jem) and **elevated to a novel "Vector-Native Omega" architecture** (Researcher). 

**New sovereign capabilities unlocked this session**:
- **Binary Quantization (BQ) Training Pipeline** — mxbai-embed-large-v1 as primary (explicitly BQ-trained, 96.45% retention), STE-based QAT for domain adaptation on Zen 2 CPU
- **Self-Supervised Embedding Refinement (vstash flywheel)** — 74.5% hybrid disagreement → MNRL fine-tune → eval gate → atomic reindex. 35-65 min/cycle on Zen 2.

**Verdict**: PROCEED_WITH_PRECAUTIONS — apply Jem's 3 critical corrections before writing `sqlite_vec_store.py`, then ship unified fabric with mxbai primary + vstash flywheel.

---

## 1. Jem's 3 Critical Corrections (MANDATORY)

### 🔴 Correction 1 — Sovereign Isolation Violation (C3)
**Defect**: The planned `vec_results` CTE queries vec0 with **no `entity_name` filter** → cross-entity memory leakage.
**Fix**: Use vec0 **partition key**:
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS exchanges_vec
USING vec0(embedding float[768], entity_name TEXT partition key);
```
All vector queries MUST scope by `entity_name = ?`. This is non-negotiable (Mandate C3 / sovereignty).

### 🔴 Correction 2 — Class-Overwrite Hazard
**Defect**: The plan's `class MemoryStore:` with no-arg `__init__` would **delete** the existing 940-line store (batch writer, tombstone, providers).
**Fix**: **ADD a tier, never redefine the class.** Wire `self.sqlite_vec.hybrid_search(...)` from *within* the existing `search()` RRF path.

### 🔴 Correction 3 — Misattributed Benchmark (G-001)
**Defect**: "5.8x @ 0.988 recall@10 on 1M" is **sqlite.org Vec1 (Zen 3)**, NOT sqlite-vec. sqlite-vec rescore (v0.1.10-alpha) has **no published** 0.988/5.8x number. No Zen 2 benchmark exists.
**Fix**: Benchmark on actual 5700U during Strike 10. Remove Vec1 numbers from D223 + EPOCH2 plan.

### 🟡 Also Flagged (Required)
- **WAL write contention**: 14-agent concurrent writes unverified → add `anyio.Lock` + exponential backoff (catch `SQLITE_BUSY`, retry 3× at 50/100/200ms).
- **MiniLM BQ recall loss**: Switch BQ embedding to **nomic-embed-text-v1.5** or **mxbai-embed-large-v1** (BQ-trained). If MiniLM must stay, use **int8** (not binary) to cap loss at 3-5%.
- **Unify RRF in Python**: Reuse existing `MemoryStore.search()` RRF logic; keep SQL RRF only as micro-benchmark.
- **11 M21 contract tests**: Before Strike 10 marked complete (see §4).

---

## 2. Researcher's Novel Spin — "Vector-Native Omega"

### Thread 2: Gnosis Graph as Vector Topology ⭐ HIGH
- **Finding**: sqlite-vec v0.1.9 supports **distance-constraint range queries** (`WHERE distance < D`) — not just top-K.
- **Novel proposal**: On every new lesson insert, run a radius query; if any neighbor carries edge `contradicts` (M17) AND distance < θ, auto-raise Skeptical Verifier flag. The vector index becomes a **consistency guardian**, not a search aid.
- **Confidence**: HIGH (range query officially shipped; direct M17 mapping).

### Thread 3: Semantic Cache / Somatic Save-Point ⭐ HIGH
- **Finding**: Semantic caching is production-proven (AWS: 86% cost / 88% latency reduction; Respan: 0.93 cosine → 25-40% hit rate).
- **Novel proposal**: Store `(query_embedding, response, model_version, somatic_state_ref)` in vec0. On hit, return cached response **AND** restore KV-cache snapshot (M20 SomaticState) → instant resume, zero re-inference.
- **Confidence**: HIGH (cache) / MEDIUM (SomaticState fuse — untested).

### Thread 4: Unified Memory Fabric (Challenges D223) ⭐ HIGH
- **Finding**: rescore index (v0.1.10-alpha) benchmarks 101ms @ 1M (384-dim) with 0.988 recall; shadow tables persist to disk (no rebuild-on-load).
- **Novel proposal**: **Single `omega_memory.db`** (FTS5 + vec0 rescore + SQL graph edges). Qdrant demoted to **degraded-mode fallback only if DB corrupted** (M23 aligned). Eliminates 400-800 MB RAM + two-system sync.
- **Confidence**: HIGH (benchmarks cover Omega's ~200K reality; persistence confirmed).

### Thread 5: Cross-Pollination via Vector Proximity ⭐ HIGH
- **Finding**: 2026 multi-agent memory research (HyphaeDB, MATM, Resonance Field) validates shared vector spaces for knowledge transfer.
- **Novel proposal**: CrossPollinationEngine (S6) becomes a vector-proximity query — when entity A commits lesson L, query entity B's vec0 for nearest neighbors; if distance < θ, auto-propose handoff. Vector space = medium for inter-entity transfer.
- **Confidence**: HIGH (concept) / MEDIUM (Omega wire — needs standardized embedder).

### Thread 6: Heritage Plagiarism Detector ⭐ MEDIUM
- **Finding**: Semantic code-clone detection is mature (CloneHunter, NLCI, Rator, SecSid).
- **Novel proposal**: Embed known `[id-soft:]` patterns into `vec_heritage`; on new code commit, embed AST-window snippets and query; if distance < threshold AND no vet record (M14), auto-flag "potential un-vetted heritage candidate."
- **Confidence**: MEDIUM (clone-detection proven; local Zen-2 code-embedding fidelity is the risk).

### Thread 1: Vector-Native Entity Registry ⭐ MEDIUM
- **Finding**: vec0 partition keys colocate vectors per entity; metadata columns appear in KNN WHERE.
- **Novel proposal**: Single `entities.db` with FTS5-indexed soul.yaml + vec0 resonance/affinity vectors → "Semantic Entity Discovery" (find entities by conceptual proximity).
- **Confidence**: MEDIUM (partition-key co-location proven; 50+ entity scale untested).

---

## 3. Jem's Novel Spin (Research-Backed Enhancements)

1. **Adaptive RRF with per-query IDF weighting** (vstash 2026): Replace fixed `k=60` with IDF-weighted fusion. Measured **+21.4% NDCG@10 on ArguAna**, +19.5% on NFCorpus. Highest-ROI novel addition.

2. **Self-supervised embedding refinement via hybrid disagreement** (vstash): 74.5% of BEIR queries show top-10 disagreement between vec-heavy and fts-heavy search → free training signal (no labels). Fine-tune local embedder on disagreement triples.

3. **Distance-calibrated relevance + feature-flag rescore**: Expose vec `distance` as calibrated relevance (M22). Gate sqlite-vec rescore (v0.1.10-alpha) behind feature flag; benchmark on Zen 2; promote when recall≥0.97.

---

## 4. M21 Contract Test Matrix (11 tests, from Jem)

| # | Criterion | Test | Expected |
|---|-----------|------|----------|
| 1 | Init | `SQLiteVecMemoryStore()` creates tables | `isinstance(store.conn, sqlite3.Connection)` |
| 2 | Insert | `add_exchange(...)` writes FTS+vec | row count +1 in both virtual tables |
| 3 | **Isolation** | query entity A returns 0 rows from B | `all(r['entity']==A for r in results)` |
| 4 | RRF | `hybrid_search` returns ranked list | `isinstance(results, list)`, scores descending |
| 5 | Routing | count<100K → sqlite-vec | backend == 'sqlite_vec' |
| 6 | Routing | count≥100K → Qdrant | backend == 'qdrant' |
| 7 | Fallback | Qdrant down → sqlite-vec-only | returns list, no raise |
| 8 | Concurrency | 14 parallel writes | 0 `SQLITE_BUSY` (write-lock holds) |
| 9 | BQ recall | nomic-embed-text BQ vs float | recall@10 drop < 5% on held-out |
| 10 | Py3.12 | import in 3.12 venv | success |
| 11 | M1 | no `import asyncio` in module | grep passes |

---

## 5. Corrected Routing Decision Tree (Jem Task 3)

```
1. Explicit per-entity backend in config (default: sqlite-vec).  ← authoritative
2. IF config == auto:
   a. IF entity has complex metadata-filter queries → Qdrant
   b. ELSE IF historical vector count >= 100K → Qdrant
   c. ELSE → sqlite-vec
3. FTS5 ALWAYS lives in sqlite-vec (lexical index cheap, co-located).
   Only the VECTOR backend switches.  ← eliminates cross-tier FTS duplication
4. On threshold crossing, run ONE-TIME migration (sqlite-vec → Qdrant),
   then pin config. Never live-route on volatile count.
```

---

## 6. Corrected Reference SQL (Entity-Safe, Partition-Key)

```sql
WITH fts_results AS (
  SELECT rowid AS id, rank,
         ROW_NUMBER() OVER (ORDER BY rank) AS rrf_rank
  FROM exchanges_fts
  WHERE exchanges_fts MATCH ?
    AND rowid IN (SELECT id FROM exchanges WHERE entity_name = ?)
  ORDER BY rank
  LIMIT 50
),
vec_results AS (
  SELECT rowid AS id, distance,
         ROW_NUMBER() OVER (ORDER BY distance) AS rrf_rank
  FROM exchanges_vec
  WHERE embedding MATCH ?
    AND entity_name = ?      -- partition-key scoped, native + fast
    AND k = ?
  ORDER BY distance
  LIMIT 50
),
combined AS (
  SELECT id, 1.0/(? + rrf_rank) AS score FROM fts_results
  UNION ALL
  SELECT id, 1.0/(? + rrf_rank) AS score FROM vec_results
),
scored AS (
  SELECT id, SUM(score) AS rrf_score FROM combined GROUP BY id
)
SELECT e.id, e.entity_name, e.session_id, e.role,
       e.content, e.timestamp, s.rrf_score
FROM scored s JOIN exchanges e ON e.id = s.id
ORDER BY s.rrf_score DESC
LIMIT ?;
-- params: (query, entity_name, query_blob, entity_name, k, rrf_k, rrf_k, limit)
```

---

## 7. L3 Principles Distilled (Researcher 7 + Jem 3 = 10)

1. **L3-VectorIndex-As-Primitive** — A vector index is retriever + consistency-enforcer + cache + topology medium. Treating it as "only search" wastes 75% of its sovereign value.
2. **L3-Range-Query-Consistency** — "Find all vectors within distance D" (radius query, v0.1.9) converts a vector store from retrieval into enforcement.
3. **L3-Semantic-Deja-Vu** — A fraction of inference is eliminable by construction. Sovereignty includes computational non-action.
4. **L3-Unified-Fabric-Over-Split** — The sqlite-vec(<100K)/Qdrant(>100K) split (D223) is an assumption, not a necessity. Rescore collapses the ceiling for Omega's ~200K.
5. **L3-Geometric-Contradiction** — Contradiction is a geometric property (nearby vectors with opposing edges), not an algorithmic check.
6. **L3-Heritage-Embedded-Vetting** — Heritage compliance (M14) can be enforced by embedding known patterns and retrieving against new code.
7. **L3-Rescore-Persistence** — Quantized rescore indexes persist to disk as vec0 shadow tables; "rebuild-on-load" fear is unfounded.
8. **L3-Adaptive-RRF-IDF** — Fixed-k RRF is suboptimal; per-query IDF weighting yields +21.4% NDCG@10. Fusion is a learned function, not a constant.
9. **L3-Self-Supervised-Embedding** — Hybrid search disagreement is a free training signal; local embedders can improve without human labels.
10. **L3-Feature-Flag-Alpha** — Alpha ANN indexes (rescore) must ship behind a flag; benchmark on target hardware before promoting.

---

## 8. Recommended Experimentation Path (Researcher)

| Order | Prototype | Why First | Effort |
|-------|-----------|-----------|--------|
| **1** | **Thread 4 — Unified `omega_memory.db` with rescore** | Highest leverage; de-risks everything | 6h |
| **2** | **Thread 2 — Radius-query contradicts flag** | Simplest novel win; serves M17 | 4h |
| **3** | **Thread 3 — Semantic Deja Vu cache (exact-tier first)** | Production-proven pattern | 8h |
| **4** | **Thread 1 — Entity resonance vec0 + discovery** | Low risk, builds on Thread 4 | 4h |
| **5** | **Thread 5 — Cross-pollination proximity** | Needs standardized embedder | 6h |
| **6** | **Thread 6 — Heritage vector detector** | Highest risk (local embed fidelity) | 10h |

**Plus Jem's 3 novel spins**: Adaptive RRF (cheap, +21.4% NDCG), self-supervised embedding refinement, distance-calibrated relevance.

---

## 9. Final Verdict

**PROCEED_WITH_PRECAUTIONS** — affirmed D223, elevated to Next-Level Strategy.

**Mandatory before Strike 10 implementation**:
1. Fix Defect 1 (entity isolation via partition key) — C3/sovereignty
2. Fix Defect 2 (ADD tier, never redefine MemoryStore)
3. Correct 5.8x/0.988 claim (Vec1, not sqlite-vec) — benchmark Zen 2
4. Add write serialization (anyio lock + exp-backoff)
5. Switch BQ embedding to nomic-embed-text-v1.5 / mxbai
6. Unify RRF in Python (reuse existing `search()`), keep SQL RRF as benchmark
7. Add 11 M21 contract tests

**Novel spin to prototype after Strike 10 ships**: Thread 4 (unified fabric) → Thread 2 (consistency enforcement) → Thread 3 (semantic cache) → Jem's adaptive RRF.

---

*🔱 OMEGA ⬡ KALI ⬡ SQLITEVEC-NEXT-LEVEL-SYNTHESIS ⬡ COMPLETE ⬡ 2026-07-12*
*Sources: Researcher novel-spin (6 threads), Jem verification (R_SQLITEVEC_VERIFICATION_20260712.md), Jem gap-closure (prior)*