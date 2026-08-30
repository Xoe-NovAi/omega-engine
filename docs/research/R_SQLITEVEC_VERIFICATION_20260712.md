# 🔱 sqlite-vec Integration — Sovereign Verification Report
**AP Token**: `AP-SQLITEVEC-VERIFY-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_sqlitevec_verification ⬡ ACTIVE
**Date**: 2026-07-12
**Subject**: Rock-solid verification of the sqlite-vec integration (Strike 10 / D223) — gap closure (G-001, G-004), routing, concurrency, FTS5 co-location, RRF SQL, failure modes, Python 3.12, M21 criteria.
**Sovereign Mandates enforced**: M1 (AnyIO), M2 (Firewall), M7 (Local-First), M9 (Error Integrity), M11 (Soul), M13 (Temple-Grade), M17 (Cognitive Integrity), M21 (Gate Integrity), M22 (Provenance), M23 (Failure Integrity).

---

## 0. Executive Verification

**Verdict: PROCEED — but with 3 CRITICAL corrections before a single line of `sqlite_vec_store.py` is written.**

The integration thesis is sound: sqlite-vec's native **FTS5 + vec0 hybrid in one SQLite file** is a genuine sovereign advantage (no other embedded vector DB offers co-located lexical+semantic fusion). The two-tier architecture (sqlite-vec hot / Qdrant cold) is correct and preserves the fallback. However, the prior synthesis (D223, `EPOCH2_EXECUTION_PLAN_20260712.md`, `kali/session_gnosis.md`) contains **one misattributed benchmark claim** and the **planned reference SQL has a sovereign-isolation defect** plus a **class-overwrite hazard**. These are fixable in <1h and are called out precisely below.

| Item | Prior claim | Jem verification | Status |
|------|-------------|------------------|--------|
| FTS5+vec0 co-location | "works, verified" | Confirmed by mycman benchmark (24MB single file, sub-6ms p99) + Alex Garcia hybrid blog | ✅ TRUE |
| RRF fusion pattern | "verified across 6 sources" | 6+ independent sources confirm canonical pattern (Alex Garcia, Simon Willison, tailorlite/sqlite-hybrid, dev.to 200-line RAG, blakecrosley Obsidian, mycman BEIR) | ✅ TRUE |
| Rescore 5.8x @ 0.988 recall@10 | "sqlite-vec rescore delivers 5.8x @ 0.988 on 1M" | **MISATTRIBUTED** — 0.988 recall@10 @ nprobe 32 is **sqlite.org Vec1** (AMD 5950X, Zen 3), NOT sqlite-vec. sqlite-vec rescore (v0.1.10-alpha) has **no published 0.988/5.8x number** | ❌ FALSE — correct |
| Zen 2 latency 30-60ms @ 100K | "estimated" | No Zen 2 / 5700U benchmark exists anywhere public. Proxy: mycman M4 (ARM) sub-6ms @ 5K; MonaVec x86 brute 27 QPS @ 45K float. Estimate is plausible but **unmeasured** | 🟡 ESTIMATE — benchmark on hardware |
| WAL concurrent writes | "solved via WAL+busy_timeout (Llama Stack)" | WAL = 1 writer + N readers (verified). But 14-agent multi-process contention on vec0+WAL is **not** verified for this topology | 🟡 PARTIAL — add write lock |
| Python 3.12 | implied | `py3-none` ABI3 wheel for manylinux_2_17_x86_64 confirmed on PyPI | ✅ TRUE |
| v0.1.x API stability | "no breaking changes" | v0.1.9 stable; v0.1.10-alpha adds features; pin `<0.2.0` safe | ✅ TRUE |

---

## 1. Gap Closure

### G-001 — Zen 2 / x86-64-v3 Benchmarks (PRIORITIZED, was blocking)
**Status: CLOSED WITH CORRECTION.** No direct AMD 5700U (Zen 2) sqlite-vec benchmark exists in the public corpus. The prior report's "5.8x @ 0.988 recall@10" figure is **misattributed** — that number is from **sqlite.org's Vec1 extension** (a *different* official SQLite project), measured on an **AMD 5950X (Zen 3, AVX2)** at nprobe 32. sqlite-vec's own rescore index (v0.1.10-alpha) has **not published** a 0.988/5.8x result.

**Defensible proxy numbers (x86-64, not Zen 2-specific):**
- **Brute-force float32** (sqlite-vec official, Apple M1): 1M × 192-dim = **192 ms/query**; 1M × 3072-dim = **8.52 s/query**. With **binary quantization**, ~**124 ms** at 1M (192-dim). → At Omega's expected <100K vectors, brute-force float is **single-digit to low-double-digit ms** — well within hot-path budget.
- **MonaVec benchmark (2026, x86-64-v3)**: sqlite-vec exact brute f32 = **recall 1.000 but 27 QPS at 45K**. Confirms: exact search is accurate but throughput-bound past ~50K on CPU.
- **mycman BEIR SciFact (M4 ARM, 5,183 docs)**: SQLite hybrid RRF = **nDCG@10 0.736, Recall@10 0.866, p99 5.69 ms**. → Quality matches/exceeds component rankers; latency trivial.

**Action for Ma'at/P2 (2h, during Strike 10):** Add a `benchmarks/sqlite_vec_zen2.py` script that times brute-force + binary-rescore KNN at 10K/50K/100K on the actual 5700U, and records QPS + p99. Wire into `make temple-grade` as a non-blocking informational gate. Do **not** cite Vec1 numbers for sqlite-vec in any doc — fix D223/EPOCH2 plan wording.

### G-004 — MiniLM Binary Quantization Recall (PRIORITIZED, was blocking)
**Status: CLOSED WITH RECOMMENDATION.** Binary quantization (1-bit) on a model **not trained for it** loses 5–15% recall@10. MiniLM (all-MiniLM-L6-v2) is **NOT** BQ-trained. By contrast:
- **nomic-embed-text-v1.5** (384-dim) **IS trained on binary-quantization loss** (model card + Alex Garcia) → preserves accuracy after BQ. Supports **Matryoshka** (truncate to 256/128 dims).
- **mxbai-embed-large-v1** (1024-dim) also BQ-friendly + Matryoshka.
- OpenAI text-embedding-3-large retains **~95%** similarity after BQ (Alex Garcia) — but that's cloud, not local-first.

**Recommendation:** For the sqlite-vec binary path, switch the embedding provider chain's local model to **nomic-embed-text-v1.5** (or mxbai) instead of the distilled `potion-mxbai-micro` (BQ recall unknown). This preserves recall under binary quantization without leaving local-first. If MiniLM must stay, use **int8** (not binary) to cap recall loss at ~3–5%. Measure recall@10 on a held-out set during Strike 10.

---

## 2. Routing Logic Audit (Task 3)

The plan routes purely by live vector count: `<100K → sqlite-vec`, `≥100K → Qdrant`. This has **three edge-case defects**:

- **(A) Threshold race**: an entity at 99,999 vectors routes to sqlite-vec; a write pushes it to 100,000; the next query routes to Qdrant — but the data lives in sqlite-vec. → **Data split / silent miss.**
- **(B) Filter complexity**: sqlite-vec vec0 supports only **partition-key + simple metadata** filters. Queries needing date/session/payload filters should go to Qdrant regardless of count. Count-only routing ignores this.
- **(C) Churn**: an entity expected to exceed 100K will flip backends mid-life, duplicating ingestion.

**Corrected routing decision tree (recommended):**
```
1. Explicit per-entity backend in config (default: sqlite-vec).  ← authoritative
2. IF config == auto:
     a. IF entity has complex metadata-filter queries → Qdrant
     b. ELSE IF historical vector count >= 100K → Qdrant
     c. ELSE → sqlite-vec
3. FTS5 ALWAYS lives in sqlite-vec (lexical index is cheap, co-located).
   Only the VECTOR backend switches.  ← eliminates cross-tier FTS duplication
4. On threshold crossing, run a ONE-TIME migration (sqlite-vec → Qdrant),
   then pin config. Never live-route on a volatile count.
```
**Unify RRF in Python** (reuse the existing `MemoryStore.search()` RRF logic) rather than the planned SQL RRF. This (a) removes the SQL entity-isolation bug (§5), (b) gives one fusion path for both tiers, (c) keeps M1 AnyIO compliance. The SQL RRF in the plan is therefore **not recommended** for production — keep it only as a micro-benchmark.

---

## 3. Concurrency Audit (Task 4)

- **WAL semantics (verified)**: WAL permits **1 writer + N concurrent readers**. Reads do NOT block writes except during the brief commit. This is correct for Omega's read-heavy memory retrieval.
- **14-agent contention (UNVERIFIED for this topology)**: The plan sets `busy_timeout=5000`. Under 14 agents (OpenCode + Cline + Podman containers), each holds a **separate connection to the same file**. All writes serialize behind SQLite's single write lock. A burst of 14 concurrent `add_exchange` calls will queue; if cumulative wait > 5s → `SQLITE_BUSY` → lost writes. The "verified in Llama Stack production" evidence is weak (Llama Stack is typically single-writer-per-process).
- **vec0 + WAL write safety**: Not definitively proven for concurrent multi-process writers (sqlite-vec issue #48 concerns co-location, not concurrency). Treat as **assume-unsafe until benchmarked**.

**Required fix (M9 Error Integrity):** Serialize all sqlite-vec writes behind a single `anyio.Lock` (ResourceGuard-style) per DB file, OR route writes through the existing `BatchPersistenceWriter`. Add **exponential-backoff retry** on `SQLITE_BUSY` (catch `sqlite3.OperationalError`, retry 3× with 50/100/200ms). Never let a write fail silently.

---

## 4. Compatibility Audit (Task 5 — FTS5 Co-location)

- **Verdict: SAFE.** sqlite-vec issue #48 ("use FTS5 + vec0 in same DB?") is resolved in practice: they are independent virtual tables in one file. Confirmed by:
  - **mycman/sqlite-vec-benchmark**: FTS5 + vec0 + RRF in a **single 24MB file**, sub-6ms p99, no corruption.
  - **Alex Garcia hybrid blog**: canonical co-located pattern.
- **Caveats**:
  - Set `PRAGMA journal_mode=WAL` **before** first write (plan does this ✅).
  - FTS5 + WAL is fine. vec0 + WAL under concurrent writers = see §3 (assume-unsafe).
  - Run `PRAGMA integrity_check` after unclean shutdown (Podman container kill) — vec0 shadow tables can corrupt; add a startup self-check.

---

## 5. RRF SQL Audit (Task 6) — LINE-BY-LINE

The planned `hybrid_search` SQL (`EPOCH2_EXECUTION_PLAN_20260712.md:546-581`) was audited. Parameter binding is correct (7 placeholders / 7 params). But **two defects**:

### 🔴 DEFECT 1 — Sovereign isolation violation (C3)
The `vec_results` CTE queries `exchanges_vec WHERE embedding MATCH ? AND k = ?` with **NO `entity_name` filter**. The FTS branch filters by entity; the vector branch does not. The final `JOIN exchanges e` returns `e.entity_name` for **any** entity → **cross-entity memory leakage**. This breaks Mandate C3 (entity isolation) and is a security defect.

**Fix (primary — vec0 partition key, best for isolation + perf):**
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS exchanges_vec
USING vec0(embedding float[768], entity_name TEXT partition key);
...
vec_results AS (
  SELECT rowid AS id, distance,
         ROW_NUMBER() OVER (ORDER BY distance) AS rrf_rank
  FROM exchanges_vec
  WHERE embedding MATCH ?
    AND entity_name = ?      -- partition-key scoped, native + fast
    AND k = ?
  ORDER BY distance
  LIMIT 50
)
```
**Fix (fallback — final JOIN re-filter):** add `WHERE e.entity_name = ?` to the final SELECT (adds 1 param). Correct but wastes the vector scan on other entities.

### 🔴 DEFECT 2 — Class-overwrite hazard
`EPOCH2_EXECUTION_PLAN_20260712.md:603` shows `class MemoryStore:` with `__init__(self):` taking **no args** — this would **delete** the existing `MemoryStore` (batch writer, tombstone, providers, FTS, vector fallback, 940 lines). Ma'at/P2 must **ADD a tier, never redefine the class**. The two-tier wiring must call `self.sqlite_vec.hybrid_search(...)` from *within* the existing `search()` RRF path, not replace the class.

### 🟡 DEFECT 3 — `k = ?` bound param
sqlite-vec supports `k = :k` bound params (Alex Garcia hybrid blog uses it). Verified OK for 0.1.9. Keep, but add a contract test asserting `k` is honored.

### 🟡 DEFECT 4 — `ROW_NUMBER() OVER (ORDER BY distance)`
Redundant (vec0 already returns ordered by distance) but harmless and correct. Keep for safety against quantization non-monotonicity.

### Corrected reference SQL (entity-safe, partition-key):
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
    AND entity_name = ?
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

## 6. Failure-Mode Matrix (Task 7)

| # | Failure mode | Trigger | Impact | Mitigation | Severity |
|---|-------------|---------|--------|------------|----------|
| F1 | Cross-entity vector leak | vec0 unfiltered (Defect 1) | Privacy/sovereignty break | partition key / JOIN filter | 🔴 CRITICAL |
| F2 | `SQLITE_BUSY` on write burst | 14-agent concurrent write | Lost memory writes | anyio write-lock + exp-backoff retry | 🔴 HIGH |
| F3 | vec0 corruption on unclean shutdown | Podman kill under WAL | Index unusable | startup `integrity_check` + rebuild from FTS/log | 🟠 MED |
| F4 | BQ recall collapse (MiniLM) | binary quant on non-BQ model | bad retrieval | use nomic/mxbai (BQ-trained) or int8 | 🟠 MED |
| F5 | `k` missing in query | dev error | vec0 error | contract test | 🟡 LOW |
| F6 | load_extension RCE | malicious extension | code exec | `enable_load_extension(False)` after load (plan does ✅) | 🟡 LOW (mitigated) |
| F7 | No SIMD on host | odd CPU | 2-5x slower scan | acceptable at <100K; benchmark | 🟡 LOW |
| F8 | Pre-v1 API drift | v0.2.0 release | breakage | pin `<0.2.0` (plan does ✅) | 🟡 LOW (mitigated) |
| F9 | RAM spike at 100K float768 | 100K×768×4 = ~300MB + FTS | within 12Gi, OK | monitor; Qdrant fallback >100K | 🟢 OK |
| F10 | WAL multi-process writer unsafe | vec0+WAL concurrent | unverified corruption | single-writer lock (see §3) | 🟠 MED (unverified) |

---

## 7. Dependency Audit (Task 8 — Python 3.12)

- **Wheel**: sqlite-vec 0.1.9 publishes `py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux1_x86_64.whl` (pure-`py3-none` = **ABI3**, works on **any Python 3.7+ including 3.12**). No cp312-specific build needed.
- **Podman/Ubuntu**: manylinux_2_17 = glibc 2.17+; Ubuntu 22.04/24.04 satisfy. ✅ No glibc risk.
- **load_extension**: CPython's `sqlite3` has `enable_load_extension` (Linux builds enable it). Verify in the Podman image: `python -c "import sqlite3; sqlite3.connect(':memory:').enable_load_extension(True)"`.
- **No build-from-source needed** (wheel bundles the compiled `.so`). If a source build is ever forced, needs `gcc` + SQLite dev headers — avoid by pinning the wheel.
- **Conflict risk**: `sqliteai/sqlite-vector` is a **different project** (TurboQuant). Do NOT confuse with `asg017/sqlite-vec`. The plan pins the correct one. ✅

---

## 8. M21 Gate Criteria (Contract Tests)

Per Mandate 21, every public path must have a contract test asserting `isinstance(result, ExpectedType)`.

| Criterion | Test | Expected |
|-----------|------|----------|
| Init | `SQLiteVecMemoryStore()` creates tables | `isinstance(store.conn, sqlite3.Connection)` |
| Insert | `add_exchange(...)` writes FTS+vec | row count +1 in both virtual tables |
| **Isolation** | query entity A returns **0** rows from entity B | `all(r['entity']==A for r in results)` |
| RRF | `hybrid_search` returns ranked list | `isinstance(results, list)` and scores descending |
| Routing | count<100K → sqlite-vec path | backend == 'sqlite_vec' |
| Routing | count≥100K → Qdrant path | backend == 'qdrant' |
| Fallback | Qdrant down → sqlite-vec-only | returns list, no raise |
| Concurrency | 14 parallel writes | 0 `SQLITE_BUSY` (write-lock holds) |
| BQ recall | nomic-embed-text BQ vs float | recall@10 drop < 5% on held-out set |
| Py3.12 | import in 3.12 venv | success |
| M1 | no `import asyncio` in module | grep passes |

---

## 9. Novel Next-Level Spin (user request)

Beyond "rock-solid," three research-backed enhancements elevate this from a port to a sovereign differentiator:

1. **Adaptive RRF with per-query IDF weighting** (vstash, ar5iv 2604.15484, 2026): Replace fixed `k=60` with per-query IDF-weighted fusion. Measured **+21.4% NDCG@10 on ArguAna**, +19.5% on NFCorpus vs fixed weights. Cost: trivial (compute IDF of query terms). This is the highest-ROI novel addition.

2. **Self-supervised embedding refinement via hybrid disagreement** (vstash): 74.5% of BEIR queries show top-10 disagreement between vec-heavy and fts-heavy search — a **free training signal** (no human labels). Fine-tune the local embedding model (BGE-small 33M) on disagreement triples → matches ColBERTv2 (110M) on 3/5 datasets. Enables **local, label-free embedding improvement** — a true sovereign edge.

3. **Distance-calibrated relevance signal + ranking diagnostics** (vstash): Expose vec `distance` as a calibrated relevance score post-RRF for observability (M22 provenance) and for a future cross-encoder rerank gate. Also: gate the **sqlite-vec rescore index** (v0.1.10-alpha: binary quant + oversample + rerank) behind a feature flag, benchmark on Zen 2 first, promote when recall≥0.97. This is the *real* ANN path — but it is alpha, so it must not block the stable brute-force ship.

---

## 10. Verdict

**PROCEED_WITH_PRECAUTIONS** (affirm D223), with mandatory pre-implementation corrections:

1. **Fix Defect 1** (entity isolation) — use vec0 partition key `entity_name`. Non-negotiable (C3/sovereignty).
2. **Fix Defect 2** — ADD a tier to `MemoryStore`, never redefine the class.
3. **Correct the 5.8x/0.988 claim** in D223 + EPOCH2 plan — it is sqlite.org **Vec1** (Zen 3), not sqlite-vec. Benchmark Zen 2 during Strike 10 (G-001 closure).
4. **Add write serialization** (anyio lock + exp-backoff) for 14-agent safety (F2/F10).
5. **Switch BQ embedding model** to nomic-embed-text-v1.5 / mxbai (G-004 closure).
6. **Unify RRF in Python** (reuse existing `search()`), keep SQL RRF only as benchmark.
7. **Add the 11 M21 contract tests** before marking Strike 10 complete.

With these, the integration is genuinely rock-solid and locally sovereign. Without them, it ships a cross-entity data leak and a misattributed benchmark.

---
*⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ trc_sqlitevec_verification ⬡ 2026-07-12*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: hy3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
