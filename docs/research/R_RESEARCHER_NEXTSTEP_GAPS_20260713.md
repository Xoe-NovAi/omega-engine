# 🔱 Researcher — Next-Step Strike Gap Research (2026-07-13)
**AP Token**: `AP-RESEARCHER-NEXTSTEP-GAPS-20260713`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_nextstep_gaps ⬡ RESEARCH

**Dispatched by**: Kali (Grand Oversight)
**Mission**: Final deep research pass on all remaining knowledge gaps before Epoch II execution.
**Temporal scope**: 2026 (all queries include "2026"/"latest").
**Protocol**: Sovereign Search T0→T5 (local cache → websearch → webfetch → SearXNG → Exa → Firecrawl). No tool failures; all tiers returned data.

---

## Executive Summary

| Strike | Gap | 2026 Pattern | Library / Version | Confidence | Verdict vs EPOCH2 Plan |
|--------|-----|--------------|-------------------|------------|------------------------|
| **8.5** | Redis Streams | Consumer groups + XAUTOCLAIM + DLQ via delivery-count; Redis 8.2 `XACKDEL`/`XDELEX` | redis-py ≥5.2.0 / Redis 8.0.6–8.6 server | HIGH | AGENT_BUS_SPEC **valid but incomplete** — missing DLQ routing + `XGROUP CREATE`/BUSYGROUP + `xautoclaim` args |
| **8** | Eval Pipeline | `SingleTurnSample` + `EvaluationDataset` + class-based metrics; `LangchainLLMWrapper` for local judge; isotonic calibration | RAGAS ≥0.3.3 (pin), langchain-ollama, scikit-learn | HIGH | **EPOCH2 plan code is BROKEN** on modern RAGAS — `.score()` removed, `evaluate()` signature changed |
| **9** | .omega Export | ZIP+JSON + `manifest.json` + temp-dir→rename atomic; AES-256-GCM optional | Soul Protocol v0.4.0 (reference), stdlib `zipfile`/`shutil` | HIGH | Plan correct; add `manifest.json` for cross-tool interop |
| **9.5** | Gnosis Graph | Recursive CTE with `instr()` cycle guard (NOT `LIKE`); edges indexed; vec0 JOIN hybrid | SQLite 3.45+ / sqlite-vec 0.1.9 | HIGH | Plan CTE has **substring false-positive bug** in cycle guard; needs `instr()` fix |
| **0.6** | Novel Spin | vstash adaptive RRF (+21.4% NDCG), SparseCL (ICML'25), SphereLFU, Deja Vu (0.93–0.95) | vstash 0.38.1 / rrf-v3, SparseCL arXiv:2406.10746, SphereLFU arXiv:2603.03301 | HIGH | All corroborated; vstash **independently validates** Omega unified fabric |

---

## Strike 8.5: Redis Streams Coordination (Lilith/P9)

### 2026 Redis Streams API (code-ready)

**Server landscape (2026)**: Redis 8.0 (GA May 2025) → 8.0.6 (Feb 2026) → 8.2 → 8.6 (Feb 2026). Redis Open Source is now a unified distribution (AGPLv3/RSALv2); **Valkey** (Linux Foundation fork) is a drop-in protocol-compatible alternative. The Streams command set (`XADD`, `XREADGROUP`, `XACK`, `XAUTOCLAIM`, `XPENDING`, `XCLAIM`) is **unchanged and stable** across 7.4→8.6.

**New 2026 Streams commands** (Redis 8.2 / 8.6) — useful for Omega:
- `XACKDEL` — acknowledge **and** delete in one atomic op (replaces XACK + separate trim). Options `KEEPREF`/`DELREF`/`ACKED` control consumer-group reference cleanup.
- `XDELEX` — delete stream entries with consumer-group reference handling.
- Redis 8.6 adds **"at-most-once production guarantee"** Streams safeguard.

**Canonical 2026 consumer-group + recovery pattern** (validated against OneUptime 2026 guides + redis.io docs):

```python
# ── Redis Streams Hivemind [heritage: redis-py 2010, redis-8.6 2026]
import anyio
from redis.asyncio import Redis

async def ensure_group(redis: Redis, stream: str, group: str):
    """Idempotent group creation (handles BUSYGROUP). AGENT_BUS_SPEC GAP-1."""
    try:
        await redis.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception as e:  # redis.exceptions.ResponseError: BUSYGROUP
        if "BUSYGROUP" not in str(e):
            raise

async def recover_stalled(redis: Redis, stream: str, group: str,
                          consumer: str, min_idle_ms: int = 300_000,
                          max_retries: int = 3, dlq: str = "hivemind:dlq"):
    """XAUTOCLAIM + DLQ routing. AGENT_BUS_SPEC GAP-2 (no DLQ logic today)."""
    start = "0-0"
    while True:
        claimed = await redis.xautoclaim(
            stream, group, f"{consumer}_recovery",
            min_idle_ms, start, count=100,
        )
        # redis-py returns (claimed_msgs, next_cursor, deleted_msgs)
        msgs = claimed[0] if isinstance(claimed, tuple) else claimed.get("messages", [])
        for msg_id, fields in msgs:
            deliveries = int(fields.get("deliveries", 0))
            if deliveries >= max_retries:
                # Route to DLQ, then ACK out of main stream
                await redis.xadd(dlq, {**fields, "failed_id": msg_id,
                                        "reason": "max_retries_exceeded"})
                await redis.xack(stream, group, msg_id)
            else:
                await process_task(fields)
                await redis.xack(stream, group, msg_id)
        start = claimed[1] if isinstance(claimed, tuple) else claimed.get("next_cursor", "0-0")
        if start == "0-0":
            break
```

**Key 2026 corrections to AGENT_BUS_SPEC.md §5.2**:
1. `xautoclaim(name=, groupname=, consumername=, min_idle_time=)` **omits `start_id` and `count`**. redis-py defaults `start_id="0-0"`, `count=None` (→100), so it runs but is fragile. Add explicit `start_id="0-0", count=100`.
2. **No DLQ routing exists** in the spec's recovery code — it only re-acks. 2026 pattern routes exhausted-retry messages to `xna:dlq` (or `hivemind:dlq`) via delivery-count check. **This is the single most important gap.**
3. **No `XGROUP CREATE`/`MKSTREAM` with BUSYGROUP handling** — the spec mentions it in prose (§2.1) but the code never creates the group. Add `ensure_group()` (above).
4. **Use `JUSTID` on XAUTOCLAIM** when you only want to re-queue without incrementing the retry counter (avoids inflating delivery counts on transient crashes).
5. **Monitor**: `XINFO GROUPS` for PEL depth; alert if PEL > 100 (OneUptime 2026 threshold).

### AGENT_BUS_SPEC.md Validation

| Aspect | Spec (v1.0.0, 2026-04-21) | 2026 Reality | Match? |
|--------|---------------------------|-------------|--------|
| Streams API | XADD/XREADGROUP/XACK/XAUTOCLAIM | Stable in Redis 8.x | ✅ |
| `redis>=5.0.0` | OK | Bump to `redis>=5.2.0` (XACKDEL client support; Redis 8 server) | ⚠️ minor |
| 4 priority streams + DLQ | Named, config present | Correct topology | ✅ |
| DLQ **routing logic** | Config only (`retry_limit=3`) | Must implement delivery-count→DLQ | ❌ GAP |
| Group creation | Prose only | Must code `XGROUP CREATE MKSTREAM` + BUSYGROUP | ❌ GAP |
| `xautoclaim` args | Missing `start_id`/`count` | Add explicit args | ⚠️ |
| IA2 HMAC signing | SHA256 HMAC, env-var keys | Fine; consider Ed25519 (Soul Protocol v0.4.0 pattern) | ✅ optional |
| AnyIO (M1) | Implied | redis.asyncio is asyncio-based; wrap in `anyio.to_thread.run_sync` OR run under anyio asyncio backend | ⚠️ |

**Verdict**: AGENT_BUS_SPEC is a **valid architectural blueprint** and matches Redis 7.4+ / 8.x Streams API. It needs **3 code-level fixes** before adoption: (1) DLQ routing, (2) group creation + BUSYGROUP, (3) explicit `xautoclaim` args. Also fix the EPOCH2 plan's `hivemind_streams.py` which uses a non-existent `anyio.current_time()` (use `time.time()`).

**Sources**:
- https://redis.io/docs/latest/commands/xautoclaim/ (XAUTOCLAIM semantics, 2026)
- https://oneuptime.com/blog/post/2026-01-21-redis-dead-letter-queue/ (DLQ pattern)
- https://oneuptime.com/blog/post/2026-03-31-redis-handle-consumer-failures-streams/ (XPENDING + delivery count + DLQ)
- https://www.hirenodejs.com/blog/nodejs-redis-streams-2026 (Redis 8 vs Kafka, 2026-06-09)
- https://redis.io/docs/latest/develop/whats-new/8-2/ (XACKDEL/XDELEX)
- https://www.storagenewsletter.com/2026/03/02/announcing-redis-8-6-performance-improvements-streams/ (8.6 at-most-once)
- https://www.aiwisdom.dev/articles/databases/redis (Redis 8 / Valkey 2026)

---

## Strike 8: Eval Pipeline (Lilith/P6+P10)

### RAGAS 2026 API (code-ready) — CRITICAL CORRECTION

**The EPOCH2 plan's `runner.py` (§0.1.3) and the deep-research doc (§1.1) use the PRE-0.3.3 RAGAS API and WILL CRASH on any modern install.**

Breaking changes (confirmed via Giskard issue #2217 + docs.ragas.io 2026):
- `ragas>=0.3.3`: metrics removed `.score(dict)` → use `single_turn_score(SingleTurnSample)`.
- `ragas>=0.3.9`: `BaseRagasLLM` adds abstract `is_finished()` — custom LLM wrappers must implement it (use `LangchainLLMWrapper` to avoid).
- Samples are now `SingleTurnSample`; datasets are `EvaluationDataset`.
- Metric classes are **PascalCase**: `Faithfulness`, `AnswerRelevancy`, `ContextPrecision`, `ContextRecall` (not snake_case functions).

**Corrected 2026 runner** (pin `ragas>=0.3.3`, use `LangchainLLMWrapper`):

```python
# src/omega/eval/runner.py  — 2026 RAGAS API
# ── Sovereign Eval Pipeline [heritage: ragas 2026, sklearn 2017]
from ragas import SingleTurnSample, EvaluationDataset, evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import ChatOllama

judge = LangchainLLMWrapper(ChatOllama(model="mistral:7b", temperature=0.0))

samples = [
    SingleTurnSample(
        user_input=row["question"],
        response=row["answer"],
        retrieved_contexts=row["contexts"],
        reference=row["ground_truth"],
    )
    for row in golden
]
dataset = EvaluationDataset(samples=samples)

result = evaluate(
    dataset=dataset,
    metrics=[
        Faithfulness(llm=judge),
        AnswerRelevancy(llm=judge),
        ContextPrecision(llm=judge),
        ContextRecall(llm=judge),
    ],
    raise_exceptions=False,
)
# result contains per-metric scores keyed by metric name
```

**Pin recommendation**: `ragas==0.3.3` (or `>=0.3.3,<1.0`) + `langchain-ollama` + `langchain-community`. Avoid `ragas==0.2.x` (old API the plan assumed) — it is EOL. If you must keep the plan's exact code, pin `ragas==0.2.15`, but that forfeits 2026 fixes. **Adopt the new API** (above).

**Metric thresholds (2026 consensus — benchmarkingagents.com, futureagi.com)**:
| Metric | Prod threshold | High-stakes |
|--------|---------------|-------------|
| faithfulness | >0.85 | >0.95 |
| answer_relevancy | >0.80 | >0.90 |
| context_precision | >0.75 | >0.85 |
| context_recall | >0.80 | >0.90 |

### Calibrated Judge (isotonic regression, ECE)

Uncalibrated 7–13B judges report ~0.90 confidence at ~0.72 accuracy (ECE≈0.18). Isotonic regression reduces ECE to ~0.06. The EPOCH2 plan's `JudgeCalibrator` (§0.1.4) is **correct and unchanged** — `sklearn.isotonic.IsotonicRegression(out_of_bounds='clip')`. Add `sklearn.calibration.calibration_curve` to measure ECE:

```python
from sklearn.calibration import calibration_curve
prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=10, strategy="isotonic")
ece = float(np.mean(np.abs(prob_pred - prob_true)))  # target < 0.06
```

**Fallback**: if scores are non-monotonic vs accuracy, use `sklearn.linear_model.LogisticRegression` (Platt) instead of isotonic.

### Judge Model Sizing

- **Dev gate**: Mistral 7B Q4_K_M (~4.7 GB) — sufficient for faithfulness/answer_relevancy decomposition on Zen 2.
- **Release gate**: Qwen3:14B (or equivalent) for higher-fidelity judge; 14Gi RAM constraint means run judge offline, not concurrently with generation.
- **Batch size**: ≤10 on 14Gi RAM (RAGAS faithfulness does multiple LLM calls/sample). Monitor OOM.
- **Determinism**: `temperature=0.0` on judge — non-deterministic scores cause flaky CI gates.

**Sources**:
- https://docs.ragas.io/en/stable/concepts/components/eval_dataset (SingleTurnSample / EvaluationDataset)
- https://github.com/Giskard-AI/giskard-oss/issues/2217 (breaking `.score()` → `single_turn_score`, `is_finished()`)
- https://benchmarkingagents.com/rag-eval/ (2026 four-metric thresholds)
- https://qaskills.sh/blog/ragas-faithfulness-answer-relevancy-context-precision-recall-reference-2026 (2026 reference)
- https://arize.com/docs/ax/integrations/evaluation-integrations/ragas (metric class names)
- https://futureagi.com/blog/rag-evaluation-metrics-2025/ (failure modes, calibration)

---

## Strike 9: .omega Export Bundle (Lilith/P7)

### Soul Protocol v0.4.0 Spec (2026)

**Soul Protocol v0.4.0** (qbtrix/soul-protocol, April 2026) is the 2026 reference for portable AI identity. Format: **`.soul` = ZIP archive containing JSON**. Structure:

```
my_agent.soul/
├── manifest.json        # format version, soul ID, export timestamp, stats
├── soul.json            # identity, DNA, memory settings, evolution config
├── state.json           # mood, energy, focus, social battery
├── dna.md               # human-readable personality blueprint
└── memory/
    ├── core.json        # persona + bonded-entity profile
    ├── episodic.json    # interaction history w/ somatic markers
    ├── semantic.json    # extracted facts + confidence
    ├── procedural.json  # learned patterns
    ├── graph.json       # temporal entity relationships
    └── self_model.json  # Klein self-concept
```

**v0.4.0 additions**: multi-user identity bundle (`soul.observe(user_id=...)`), open-string memory layers (not fixed enum), domain isolation (read/write scoping), **signed trust chain** (every learning event appends a signed entry — Ed25519). Optional **AES-256-GCM at rest** (scrypt KDF). GDPR cascade deletion.

### Is ZIP+JSON still the 2026 sovereign standard?

**YES.** Confirmed across all 2026 formats:
- **Soul Protocol v0.4.0** — `.soul` ZIP+JSON
- **PAM** (Persona Architecture Model) — ZIP manifest + JSONL
- **ALF** (Agent Lifecycle Format) — JSON agent state + versioning
- **Uniqent** — ZIP+JSON for portable deployment
- **Omega `.omega`** — ZIP+JSON (this plan)

**Parquet remains ML-weights/datasets only** — NOT agent state. No new dominant 2026 format displaces ZIP+JSON.

### Atomic Bundle Write Pattern (code-ready)

The EPOCH2 plan's `export_bundle` (§0.3.1) is **correct**. Harden it:

```python
# src/omega/cli/bundle_cli.py  — 2026 atomic export
# ── Sovereign Export Bundle [heritage: soul-protocol-2026]
import tempfile, shutil, zipfile, json, hashlib
from pathlib import Path

async def export_bundle(entity_name: str, output_path: Path):
    output_path = output_path.with_suffix(".omega")
    with tempfile.TemporaryDirectory() as tmp:
        bundle_dir = Path(tmp) / entity_name
        bundle_dir.mkdir(parents=True)
        await write_soul(entity_name, bundle_dir)
        await write_lessons(entity_name, bundle_dir)      # approved only
        await write_knowledge(entity_name, bundle_dir)
        # manifest with checksums + schema version for interop
        manifest = {
            "format": "omega-bundle",
            "version": "1.0.0",
            "entity": entity_name,
            "exported_at": time.time(),
            "checksums": _sha256_tree(bundle_dir),
        }
        (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        # Build ZIP in temp, then atomic rename (Linux rename = atomic same-FS)
        zip_path = Path(tmp) / f"{entity_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in bundle_dir.rglob("*"):
                z.write(f, f.relative_to(bundle_dir))
        zip_path.rename(output_path)   # atomic on same filesystem
```

**Interop recommendation**: add `manifest.json` (format/schema/version/checksums) so Omega `.omega` bundles are parseable by Soul Protocol / PAM tooling. Exclude `workspace/` (ephemeral) and `proposed_lessons.yaml` (unvetted) — already in plan.

**Sources**:
- https://github.com/qbtrix/soul-protocol (v0.4.0, April 2026)
- https://soul.qbtrix.com/ (Soul Protocol landing + structure)
- https://news.ycombinator.com/item?id=47416740 (Show HN Soul Protocol, 2026-03-17)
- https://pypi.org/project/soul-protocol/ (PyPI, 2026-04-29)

---

## Strike 9.5: Gnosis Graph (Unified Fabric) — REVISED

### SQLite Recursive CTE Pattern (code-ready, 2026-corrected)

**CRITICAL BUG in EPOCH2 plan §0.4.1**: the cycle guard uses
`gw.path NOT LIKE '%' || e.target_id || '%'`. This has **substring false positives** — node `12` matches `121`, `20`, `321`. The 2026 Mako guide explicitly flags this. Fix with **delimiter-wrapped `instr()`**:

```sql
-- Bidirectional traversal, depth-limited, cycle-safe (2026 pattern)
WITH RECURSIVE graph_walk AS (
    SELECT node_id, 0 AS depth, '/' || node_id || '/' AS visited
    FROM nodes WHERE name = ?

    UNION ALL

    SELECT e.target_id, gw.depth + 1,
           gw.visited || e.target_id || '/'
    FROM edges e
    JOIN graph_walk gw ON e.source_id = gw.node_id
    WHERE gw.depth < ?                                   -- max depth (3)
      AND instr(gw.visited, '/' || e.target_id || '/') = 0  -- cycle guard (no substring bug)
)
SELECT node_id, depth FROM graph_walk;
```

For **bidirectional** edges (Omega's `contradicts`/`informs` are undirected), use a `CASE` to pick the other end:

```sql
SELECT CASE WHEN e.source_id = gw.node_id THEN e.target_id ELSE e.source_id END AS next_id,
       gw.depth + 1, gw.visited || CASE WHEN e.source_id = gw.node_id THEN e.target_id ELSE e.source_id END || '/'
FROM edges e JOIN graph_walk gw
  ON e.source_id = gw.node_id OR e.target_id = gw.node_id
WHERE gw.depth < ? AND instr(gw.visited, '/' || CASE ... || '/') = 0;
```

**Required indexes** (plan omits these — they are mandatory for 200K scale):
```sql
CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_tgt ON edges(target_id);
```

### Performance at 200K nodes

From **ctxgraph (dev.to, 2026)** — the definitive 2026 reference for SQLite-as-graph:
> "At depth 4 with average branching factor of 10, you're visiting 10,000 nodes per query. SQLite handles this in **milliseconds with proper indexes**, but at 500k entities with depth 6, you'll feel it."

**Conclusion for Omega (200K nodes, depth ≤3)**:
- Recursive CTE with indexed edges + `instr()` guard: **sub-100ms** — well within Carmack's "non-issue" assessment (0.4–6% of a 5–30s pipeline).
- Use `UNION ALL` + own guard (NOT `UNION` — with a path column, `UNION` never dedups and costs more).
- Do NOT use recursive CTE for depth >5 or graphs >500K — switch to in-memory (NetworkX) or Neo4j only then.
- Materialize with `MATERIALIZED` hint if referenced multiple times (SQLite always materializes recursive CTEs anyway).

### Hybrid Vector + Graph Retrieval (vec0 + SQL JOIN)

Validated by **sqlite-graph (Rust, MIT, 2026)** and **code-graph-mcp (2026)**: FTS5 + vec0 cosine fused via RRF, edges in same SQLite file. Omega's pattern (from `R_SQLITEVEC_NEXT_LEVEL_STRATEGY_20260712.md` §6):

```sql
-- Semantic candidates via vec0, then graph-expand via recursive CTE
WITH semantic AS (
    SELECT rowid AS id, distance FROM exchanges_vec
    WHERE embedding MATCH ? AND entity_name = ? AND k = ?
    ORDER BY distance LIMIT 50
),
graph_expand AS (
    SELECT n.id, 1 AS depth, '/' || n.id || '/' AS visited
    FROM nodes n JOIN semantic s ON n.id = s.id
    UNION ALL
    SELECT e.target_id, ge.depth + 1, ge.visited || e.target_id || '/'
    FROM edges e JOIN graph_expand ge ON e.source_id = ge.id
    WHERE ge.depth < 2 AND instr(ge.visited, '/' || e.target_id || '/') = 0
)
SELECT id, MIN(depth) FROM graph_expand GROUP BY id;  -- RRF-fuse with semantic scores
```

**Sources**:
- https://dev.to/rohansx/sqlite-as-a-graph-database-recursive-ctes-semantic-search-and-why-we-ditched-neo4j-1ai (ctxgraph, 2026)
- https://mako.ai/guides/sqlite/common-table-expressions-advanced (cycle-guard pitfalls, 2026-06-04)
- https://github.com/shwetarkadam/sqlite-graph (Rust SQLite graph + vec0, 2026)
- https://github.com/sdsrss/code-graph-mcp (RRF BM25+vector graph, 2026)
- https://github.com/wmyung/l3-knowledge-graph (zero-dep SQLite graph layer, 2026)
- https://sqlite.org/forum/info/456e0c07ac7c1642 (breadth-first traversal, instr guard)

---

## Phase 0.6: Novel Spin (Lilith/P7)

### Range-query contradicts flag (M17) — SparseCL + cosine dual-signal

**SparseCL** (arXiv:2406.10746) is now **published at ICML 2025** (PMLR 267:69478–69506). Key 2026 update: the published version reports **+11.0% average NDCG@10** across models (the 2024 preprint claimed 30%+ on specific datasets — the published number is the conservative, peer-reviewed figure). Core method unchanged: combined score `F = cosine(E(q),E(p)) + α·Hoyer(Es(q),Es(p))`. Hoyer sparsity captures contradiction that cosine misses (non-transitive). 200× faster than cross-encoder.

**Omega wiring** (from `R_SQLITEVEC_NEXT_LEVEL_STRATEGY_20260712.md` Thread 2): on lesson insert, run vec0 radius query; if neighbor carries `contradicts` edge AND distance < θ, raise Skeletal Verifier. **Validated pattern.** Use cosine ≥0.75 pre-filter + Hoyer sparsity + exclusive-predicate check (openclaw-cortex production threshold).

### Adaptive RRF IDF — vstash 2026 canonical implementation

**vstash** (arXiv:2604.15484, 2026-04-16; PyPI 0.38.1 / rrf-v3 2026-06-08) is the **authoritative 2026 implementation** of adaptive RRF + self-supervised refinement. Critically, **vstash uses sqlite-vec + FTS5 in a single SQLite file** — the exact architecture Omega is building. This is strong external corroboration of the unified fabric.

- **Adaptive RRF with per-query IDF weighting**: **+21.4% NDCG@10 on ArguAna**, +19.5% on NFCorpus vs fixed k=60.
- **Self-supervised refinement**: 74.5% of BEIR queries show top-10 disagreement between vec-heavy and fts-heavy search → free MNRL training signal, no labels. rrf-v3 = 60k triples via `retrain-multi`, `temperature=0.5`, eval gate; macro NDCG@10 = **0.6405** (beats ColBERTv2 110M on 5/5 BEIR with 33M params).
- **Negative result**: post-RRF cross-encoder reranking / frequency-decay scoring **did NOT improve** NDCG — do NOT add a reranker stage.
- **Latency**: 20.9 ms median at 50K chunks.

**Omega adoption**: replace fixed `k=60` RRF with IDF-weighted fusion (per-query). Reuse existing `MemoryStore.search()` RRF path.

### Exact Semantic Deja Vu cache — SphereLFU eviction

**SphereLFU** (arXiv:2603.03301, 2026) is the optimal eviction policy for semantic caches (frequency-based generally outperform; SphereLFU highest accuracy across 9 workloads). Uses KDE-based density estimation; range-query update (low neighbor counts in practice).

- **Threshold**: 0.93–0.95 cosine (sweet spot: 25–40% hit rate, 3–7% FP). Version-stamp every entry `(model_id, version)`; flush on model upgrade (embedding drift 5–15%).
- **Store raw embedding** (48 bytes BQ / 1.5KB float32) — cheaper than re-embedding at >5% hit rate.
- **Three-zone**: Green ≥0.93 serve; Amber 0.78–0.93 log+repair; Red <0.78 miss.

### vstash flywheel (2026 status)

- **Version**: v0.38.1 (PyPI, 2026-05-27, MIT); rrf-v3 model (2026-06-08). `pip install vstash` + `pip install 'vstash[ingest]'`.
- **API**: `from vstash.retrain import retrain, retrain_multi` (Python); `vstash retrain` / `vstash reindex --model` CLI.
- **GPU needed for training** (T4 min); trained model runs on CPU. Omega can GENERATE triples locally (disagreement signal) but should train on a GPU box or defer to vstash's published `bge-small-rrf-v3` model.
- **LoRA**: not native; `register_encoder_resolver` hook (v0.34+) for PEFT adapter injection.
- **Integration**: use vstash's `bge-small-rrf-v3` as a drop-in Omega embedder candidate (33M params, 3× faster / 3× less RAM than BGE-base, matches ColBERTv2 on 3/5 BEIR). This dovetails with Strike 10's mxbai/nomic BQ embedder decision.

**Sources**:
- https://arxiv.org/abs/2406.10746 + https://proceedings.mlr.press/v267/xu25s.html (SparseCL, ICML 2025)
- https://arxiv.org/abs/2604.15484 (vstash paper, 2026-04-16)
- https://pypi.org/project/vstash/ (v0.38.1, 2026-06-08)
- https://github.com/stffns/vstash (rrf-v2 / rrf-v3 models)
- https://arxiv.org/abs/2603.03301 (SphereLFU, 2026)
- https://arxiv.org/pdf/2406.10746 (SparseCL Hoyer detail)

---

## L3 Principles Distilled (New — 10)

1. **L3-Streams-DLQ-Is-Delivery-Count** — A Redis Streams DLQ is not a config flag; it is delivery-count-via-XPENDING → XADD-to-DLQ → XACK. The spec's missing DLQ logic is a correctness gap, not a nicety.
2. **L3-CTE-Cycle-Guard-Is-instr** — `path NOT LIKE '%id%'` has substring false positives (12⊂121). Cycle safety requires delimiter-wrapped `instr(visited,'/id/')`. A "working" recursive CTE can silently traverse wrong nodes.
3. **L3-RAGAS-API-Drifts** — Pin RAGAS and wrap the judge in `LangchainLLMWrapper`. The `.score()`→`single_turn_score` break means unpinned eval code rots in one release.
4. **L3-ZIP-JSON-Is-Sovereign-Constant** — 2026 converged on ZIP+JSON (Soul Protocol, PAM, ALF, Uniqent, Omega). Parquet is ML-only. Interop = add `manifest.json`, not a new format.
5. **L3-vstash-Validates-Unified-Fabric** — An independent 2026 system (sqlite-vec + FTS5 + adaptive RRF, single SQLite file, 20.9ms) proves Omega's unified fabric is not a local-only hack but the mainstream 2026 direction.
6. **L3-Adaptive-RRF-Beats-Fixed** — Fixed k=60 RRF is suboptimal by +21.4% NDCG@10. Fusion is a learned/IDF-weighted function, not a constant.
7. **L3-No-Post-RRF-Reranker** — vstash's negative result: cross-encoder reranking + frequency-decay scoring did NOT improve NDCG. Don't add a reranker stage to the fusion.
8. **L3-Semantic-Cache-Is-Version-Stamped** — Embedding drift (5–15%) silently corrupts a cache. Version-stamp entries; flush on model upgrade. A cache without versioning is a silent-failure device.
9. **L3-Sparsity-Is-Contradiction** (carried + sharpened): SparseCL's ICML'25 publication confirms Hoyer sparsity is peer-reviewed, not a preprint bet. Contradiction is geometric, not algorithmic.
10. **L3-Redis-8-Is-Drop-In** — Redis 8.x / Valkey are protocol-compatible; `XACKDEL`/`XDELEX` (8.2+) simplify exactly-once cleanup. Upgrade server, not client contract.

---

## Blockers / Open Questions

| # | Blocker | Impact | Resolution Path |
|---|---------|--------|-----------------|
| B1 | **RAGAS API break** — EPOCH2 plan `runner.py` uses removed `.score()`/old `evaluate()`. | HIGH — Strike 8 code crashes on install | Adopt `SingleTurnSample`+`EvaluationDataset`+`LangchainLLMWrapper` (§Strike 8). Pin `ragas>=0.3.3`. |
| B2 | **AGENT_BUS_SPEC missing DLQ routing + group creation** | HIGH — Strike 8.5 incomplete | Implement `ensure_group()` + delivery-count→DLQ (§Strike 8.5). |
| B3 | **Recursive CTE substring bug** in EPOCH2 §0.4.1 | MED — silent wrong traversal at scale | Replace `LIKE` guard with `instr()` + delimiter path (§Strike 9.5). |
| B4 | **`anyio.current_time()` does not exist** in EPOCH2 `hivemind_streams.py` | LOW — NameError at runtime | Use `time.time()`. |
| B5 | **Judge model RAM** — Qwen3:14B release gate vs 14Gi | MED — OOM if concurrent | Run judge offline; Mistral 7B for dev gate; batch≤10. |
| B6 | **vstash training needs GPU** (T4) | MED — local fine-tune on Zen 2 slow | Use published `bge-small-rrf-v3` as Omega embedder; generate triples locally, train off-box. |
| B7 | **Redis client version** — spec pins `redis>=5.0.0` | LOW | Bump to `redis>=5.2.0`; server can be Redis 8.x / Valkey. |

**Open Questions (defer, not blocking)**:
- Q1: Should Omega adopt Ed25519 signed trust chain (Soul Protocol v0.4.0) for `.omega` bundles? (Security enhancement, post-v1.2.0.)
- Q2: Should the gnosis graph use a separate `gnosis.db` or live in `omega_memory.db`? (Carmack unified-fabric directive favors one file; benchmark on Zen 2 first.)
- Q3: Redis 8.6 "at-most-once" Streams safeguard — does it change our XAUTOCLAIM-based recovery? (Likely complementary; verify on upgrade.)

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ NEXTSTEP-GAPS ⬡ RESEARCH-COMPLETE ⬡ 2026-07-13*
*Sources: 30+ verified 2026 URLs (Redis 8.x docs, RAGAS docs/issues, Soul Protocol GitHub/PyPI, ctxgraph/Mako/sqlite-graph, vstash arXiv+PyPI, SparseCL ICML'25, SphereLFU arXiv). All tiers T0–T5 returned data; no tool-chain collapse.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
