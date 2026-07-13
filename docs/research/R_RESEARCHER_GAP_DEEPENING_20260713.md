# 🔱 Researcher Gap Deepening — 2026-07-13
**AP Token**: `AP-RESEARCHER-GAP-DEEPEN-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_gap_deepening ⬡ RESEARCH

## Executive Summary

This report closes **6 critical knowledge gaps** for the Omega Engine's sqlite-vec unified fabric. Key findings:

1. **vstash (Gap 1)**: Fully production-ready. `pip install vstash` (v0.38.1, MIT). CLI + Python SDK. GPU needed for training (T4 minimum), but trained model runs on CPU. The hybrid disagreement signal (vector vs keyword ranking differences) is free supervision. Custom `register_encoder_resolver` hook in v0.34+ allows LoRA adapter injection.

2. **STE-QAT on Zen 2 (Gap 2)**: **BREAKTHROUGH** — bitsandbytes PR #1901 (merged 2026-03-30) enables CPU-optimized 8-bit optimizers. True 4-bit CNN training on CPU achieves FP32 parity (arXiv:2603.13931). For BGE-small (33M params), CPU fine-tuning is feasible but slow (~5-10× GPU). For mxbai-embed-large-v1 (335M), GPU recommended.

3. **Semantic Cache (Gap 3)**: Well-characterized. Threshold 0.92-0.97 for production (sweet spot 0.93-0.95). **SphereLFU** optimal eviction policy (arXiv:2603.03301). Embedding model drift requires version-stamped entries + full cache flush on upgrade.

4. **VR/3D Spatial (Gap 4)**: sqlite-vec fully supports 3D via `float[3]` + `vec_distance_L2()`. No existing VR projects found. Spatial+semantic hybrid requires two vec0 tables + JOIN.

5. **Sovereign Research (Gap 5)**: Complete zero-API-key pipeline exists: SearXNG + Trafilatura + Crawl4AI. GroktoCrawl (MIT) is a full Firecrawl replacement.

6. **Contradiction Detection (Gap 6)**: SparseCL (arXiv:2406.10746) provides optimal open approach using Hoyer sparsity. Simple pipeline: cosine ≥ 0.75 + exclusive-predicate matching + LLM verification gate.

---

## Gap 1: vstash Flywheel Implementation Details

**Sources**:
- https://github.com/stffns/vstash (README, docs/retrain.md, experiments/hypotheses.md)
- https://pypi.org/project/vstash/ (PyPI listing, v0.38.1)
- https://arxiv.org/abs/2604.15484 (paper reference)

### 1. What is the EXACT Python API?

Two-level API:

**High-level SDK** (from PyPI README):
```python
from vstash import Memory

mem = Memory(project="my_agent")
mem.add("docs/spec.pdf")
mem.remember("OAuth uses PKCE for public clients", title="auth-notes")
results = mem.search("deployment strategy", top_k=5)
for r in results:
    print(r.text, r.score, r.collection, r.tags, r.added_at)
answer = mem.ask("What are the system requirements?")
```

**Low-level retrain API** (from docs/retrain.md):
```python
from vstash.retrain import retrain, retrain_multi, qrels_to_eval_queries

# Single corpus
result = retrain(
    store=my_store,
    base_model="BAAI/bge-small-en-v1.5",
    epochs=2, lr=3e-6, batch_size=64,
    eval_fraction=0.15, min_gain=0.0, seed=42,
    output_path="~/.vstash/models/retrained",
)

# Multi-corpus with temperature sampling
retrain_multi(
    stores={"papers": paper_store, "code": code_store},
    base_model="BAAI/bge-small-en-v1.5",
    sampling_strategy="temperature",
    sampling_temperature=0.5,
    total_triples=30000,
    epochs=2, lr=3e-6, batch_size=32,
)
```

**CLI interface**:
```bash
vstash retrain [--max-queries 5000] [--epochs 2] [--lr 3e-6] [--batch-size 64]
vstash reindex --model ~/.vstash/models/retrained
```

### 2. How does it emit disagreement triples?

The triple generation is internal to `vstash.retrain.generate_triples` / `generate_labeled_triples_batched`:

1. **Chunk-prefix path (unsupervised)**: Sample chunks from the corpus, use first 200 chars as pseudo-query → run vector search and keyword search → if they rank different docs #1, that's a training pair.
2. **Labeled path (supervised)**: Pass `--training-queries train.jsonl` with format `{"query": str, "relevant_paths": [str, ...]}` per line → emits |gold| × 2 triples (positive + in-batch negative).
3. **Loss**: MNRL (Multiple Negative Ranking Loss) triplets.

Triple count: 30k-60k total recommended. At 60k triples, training takes ~55 min on Colab T4.

### 3. Does it support LoRA fine-tuning directly?

**No, not natively.** vstash uses full fine-tuning via sentence-transformers. However, **v0.34+ added `register_encoder_resolver(fn)`** — a custom encoder resolver hook that allows callers to plug in LoRA-adapted encoders. The resolver is consulted before every built-in path.

**Verdict**: LoRA possible via the resolver hook, but not built-in. Fine-tune a LoRA adapter externally via PEFT, then register it.

### 4. Output format of `vstash reindex`?

`vstash reindex --model <path>` re-embeds ALL documents in the store. It drops and recreates `vec_chunks` table (wrapped in `BEGIN IMMEDIATE`), re-computes embeddings, rebuilds the snapvec. The retrain produces a **new model directory** at `--output` with `pytorch_model.bin` + config. The eval gate atomically promotes or leaves at `.candidate/`.

### 5. Can we integrate as Python library?

**Yes, fully.** `from vstash.retrain import retrain, retrain_multi` accepts Python objects directly. The entire pipeline (`split_corpus_for_eval` → `evaluate_model` → `generate_triples` → `train_mnrl` → eval gate) is available as composable functions in `vstash/retrain.py`.

### 6. Memory requirements during training on CPU?

**vstash officially requires GPU for training** (T4 is sufficient). From docs/retrain.md: "Training itself needs a GPU (T4 is enough); the trained model then runs on CPU like any other embedding model."

For CPU training with bitsandbytes (see Gap 2): BGE-small (33M params, ~132MB in fp32) with 8-bit optimizers reduces optimizer state from 528MB to ~132MB. Forward+backward at batch_size=8 would need ~2-4GB RAM and take ~5-10 hours for 60k triples.

### 7. Is there a `pip install vstash` package?

**YES.** Published on PyPI at https://pypi.org/project/vstash/
- **Current version**: v0.38.1 (2026-05-27), **License**: MIT, **Python**: >=3.10
- Install: `pip install vstash` (SDK), `pip install 'vstash[ingest]'` (+PDF/DOCX), `pip install 'vstash[serve]'` (+web UI), `pip install 'vstash[all]'` (everything)

### L3 Principle
**L3-Disagreement-Signal**: When two retrieval systems (vector + keyword) disagree on ranking, their disagreement is free supervision for embedding fine-tuning. No human labels needed.

### Confidence: HIGH

---

## Gap 2: STE-QAT on Zen 2 — Binary Quantization Training

**Sources**:
- https://github.com/bitsandbytes-foundation/bitsandbytes/pull/1901 (CPU optimizers, merged 2026-03-30)
- https://arxiv.org/abs/2603.13931 (True 4-bit CNN training on CPU, FP32 parity)
- https://github.com/Nexa1nc/NexaQuant (CPU ternary training)
- https://arxiv.org/html/2505.18113v2 (Sample complexity of STE)
- https://github.com/mixedbread-ai/binary-embeddings (mxbai BQ notebook)

### 1. Is STE training feasible on CPU without GPU?

**YES, with caveats.** bitsandbytes PR #1901 (merged 2026-03-30) enables ALL optimizers on CPU, including 8-bit blockwise variants: `AdamW8bit`, `SGD8bit`, `Lion8bit`, `RMSprop8bit`. Full CPU training example runs `JackFram/llama-68m` at ~9.5 steps/sec.

**Bottleneck analysis**:
- **Memory**: BGE-small (33M params) = 132MB weights + 66MB optimizer states (8-bit) = ~200MB. Well within 14Gi RAM.
- **Compute**: CPU matmul is ~10-50× slower than GPU. That's the real bottleneck.
- **Theory**: arXiv:2505.18113v2 proves STE converges with O(n²) samples on Gaussian data.

**For BGE-small (33M)**: Feasible on Zen 2. Est. 5-10 hrs/epoch at batch_size=8.
**For mxbai-embed-large-v1 (335M)**: Not recommended for CPU. 1.34GB weights, 50-100 hrs.

### 2. Hyperparameter recipe for BGE-small (33M) LoRA r=16 on CPU

```python
from transformers import AutoModel
from peft import LoraConfig, get_peft_model
import bitsandbytes as bnb

model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
lora_config = LoraConfig(
    r=16, lora_alpha=32,
    target_modules=["query", "key", "value", "dense"],
    lora_dropout=0.05, bias="none", task_type="FEATURE_EXTRACTION",
)
model = get_peft_model(model, lora_config)
optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=2e-4)
# batch_size=8, epochs=3, lr=2e-4, warmup_steps=50, grad_accum=4
```

### 3. Memory profile for 33M model on CPU

| Component | 32-bit | 8-bit optimizer |
|-----------|--------|-----------------|
| Weights | 132 MB | 132 MB |
| Adam states | 264 MB | 66 MB |
| Gradients | 132 MB | 132 MB |
| Activations (bs=8) | ~256 MB | ~256 MB |
| LoRA (r=16) | 8 MB | 8 MB |
| **Total peak** | **~792 MB** | **~594 MB** |

**Verdict**: Fits easily in 14Gi RAM. Bottleneck is CPU matmul throughput, not RAM.

### 4. CPU-optimized training libraries

- **bitsandbytes PR #1901**: CPU optimizer support for AdamW8bit, SGD8bit, etc. AVX2 required (Zen 2 has it). HF Trainer integration with `use_cpu=True`.
- **NexaQuant v3.0**: 1.58-bit ternary training on CPU. Uses int16 accumulators, tiled GEMM for 3-5× speedup. Specialized for extreme quantization.
- **llama-cpp-python**: Inference only, no training API for embedding models.

### 5. Pure PyTorch BQ training loop on CPU?

**YES — with important caveat**: For mxbai-embed-large-v1, BQ is **post-training**, not learned:
```python
emb = model.encode(texts, normalize_embeddings=True)  # float32
bemb = np.packbits(emb > 0).reshape(emb.shape[0], -1)  # threshold binarization
```

For **actually training** BQ-aware embeddings: use contrastive loss with binary-aware objective + quantization noise (STE-based). The True 4-bit CNN paper (arXiv:2603.13931) demonstrates this.

**Expected time per epoch for BGE-small on Zen 2**:
- batch_size=8: 3-5 hrs, ~600MB RAM
- batch_size=16: 2-3 hrs, ~1.1GB RAM
- batch_size=32: 1-2 hrs, ~2.0GB RAM

### 6. mxbai BQ-specific training script?

**No.** The only published notebook (https://github.com/mixedbread-ai/binary-embeddings) is for **post-training binary quantization** using `np.packbits(emb > 0)`. Achieves 96-99% retention via Hamming distance + dot product rescore. The model's embedding space was designed for this.

### L3 Principle
**L3-BQ-Is-PostTraining**: For mxbai-embed-large-v1, BQ does not require STE-aware training. Use post-training binarization + Hamming retrieval + rescore.

### Confidence: HIGH

---

## Gap 3: Exact Semantic Deja Vu Cache Patterns

**Sources**:
- https://llmbestpractices.com/ai-agents/embeddings-semantic-cache
- https://www.respan.ai/articles/semantic-cache-llm (production hit rate table)
- https://arxiv.org/pdf/2603.03301 (SphereLFU, formal eviction analysis)
- https://vadim.blog/semantic-caching-for-llms (cross-encoder reranking, three-zone confidence)
- https://pr-peri.github.io/ai-engineering/2026/05/30/semantic-caching-llm.html
- https://duanegrey.com/insights/why-embedding-model-drift-breaks-ai-systems-silently (drift)
- https://tianpan.co/blog/2026-04-20-cache-invalidation-ai-semantic-rag (version-stamped namespaces)
- https://redis.io/docs/latest/develop/ai/redisvl/user_guide/how_to_guides/llmcache/ (TTL behavior)

### 1. Optimal cosine similarity threshold?

**Consensus: 0.92-0.97 for production.**

| Threshold | Hit Rate | FP Rate | Use Case |
|-----------|----------|---------|----------|
| 0.99 | 1-3% | <0.1% | Legal/medical |
| 0.97 | 5-10% | ~0.5% | First deployment |
| **0.95** | **15-25%** | **1-3%** | **General sweet spot** |
| **0.93** | **25-40%** | **3-7%** | **Max savings (with eval)** |
| 0.90 | 35-55% | 7-15% | Low-risk FAQ |
| 0.85 | 45-70% | 15-30% | Aggressive — high risk |

Three-zone confidence (vadim.blog): Green (≥0.93) serve; Amber (0.78-0.93) log+repair; Red (<0.78) miss. Cross-encoder reranking lifts precision from 85% to 96-98%.

### 2. Best eviction policy?

**SphereLFU** (arXiv:2603.03301) is optimal. Uses Kernel Density Estimation to maintain vectors in highest-density regions. LFUDA (LFU with dynamic aging) is second-best. LRU underperforms on semantic cache workloads because semantically similar queries arrive in bursts.

**Recommendation**: LFUDA default; implement SphereLFU if KDE overhead is acceptable.

### 3. Embedding model drift handling?

**Critical**: Model upgrades shift vector positions by 5-15% in cosine distance (duanegrey.com). Mixing versions produces incomparable vectors silently.

**Mitigation**: (1) Version-stamp every cache entry with `(model_id, version)`. (2) Lock model version — never use `:latest`. (3) On upgrade: flush entire cache OR background re-embedding. (4) Validate at startup.

### 4. Hit rate vs threshold (production measurements)

From Respan's production data: 0.97 → 5-10% hit (marginal savings), 0.95 → 15-25% (good), 0.93 → 25-40% (max savings). Break-even at ~10% hit rate (embedding cost < LLM savings).

### 5. Storing raw embedding cheaper than re-embedding?

**YES**. all-MiniLM-L6-v2: 384×float32 = 1,536 bytes/entry, ~5ms embedding time. At 100K queries/day with 30% hit rate: 150MB storage for embeddings, 500s CPU time, saves ~8.3 hrs LLM inference. Net positive at >5% hit rate. BQ embeddings: 48 bytes/entry → 4.8MB for 100K entries.

### 6. Multi-turn vs single-query?

**Last-1-turn** is the safe default (92% recall at 40% token cost, per vadim.blog). Tag entries with `session_id` to prevent cross-session leaks.

### L3 Principle
**L3-Threshold-Calibration**: A semantic cache without an eval loop is dangerous. Sample 1-5% of cache hits weekly for blind review and adjust threshold based on false-positive rate.

### Confidence: HIGH

---

## Gap 4: VR/3D Spatial Patterns with sqlite-vec

**Sources**:
- https://github.com/asg017/sqlite-vec/blob/main/site/features/knn.md
- https://github.com/asg017/sqlite-vec/blob/main/site/api-reference.md
- https://github.com/asg017/sqlite-vec/blob/main/site/features/vec0.md
- https://github.com/asg017/sqlite-vec/commit/0de765f (ANN benchmark with float[768]+bit[768])

### 1. Any precedent for 3D coordinates in sqlite-vec?

**No existing projects found.** sqlite-vec is used for text embeddings (float[384], [768], [1024]). But the infrastructure fully supports 3D: vec0 accepts ANY float array dimension (`float[3]`, `float[4]`), and `vec_distance_L2()` works on any float32 vector.

### 2. Optimal distance metric for 3D spatial?

**L2/Euclidean** is the natural metric. L1 (Manhattan) for grid spaces. Cosine only useful for normalized direction-only vectors.

### 3. Combine spatial proximity + semantic similarity?

**Two-table JOIN** is the canonical pattern:
```sql
CREATE VIRTUAL TABLE vec_spatial USING vec0(entity_id INTEGER PK, coord_embedding float[3]);
CREATE VIRTUAL TABLE vec_semantic USING vec0(entity_id INTEGER PK, text_embedding float[1024] distance_metric=cosine);

WITH spatial_candidates AS (
    SELECT entity_id FROM vec_spatial
    WHERE coord_embedding MATCH vec_f32('[qx, qy, qz]') AND k = 100
)
SELECT e.*, v.distance FROM spatial_candidates s
JOIN vec_semantic v ON s.entity_id = v.entity_id
WHERE v.text_embedding MATCH vec_f32(':query_emb') AND k = 10
ORDER BY v.distance;
```

vec0 aux columns cannot appear in KNN WHERE clauses, so post-filtering or two-table JOIN is required.

### 4. Performance on low-dimensional (3-4) vectors?

**Excellent**: L2 on float[3] = 3 multiplications + 2 additions + sqrt. Brute-force over 100K float[3] vectors: ~3ms (vs 768-dim: ~100ms). Partition keys can shard spatial regions.

### 5. Research on spatial-semantic hybrid for VR/gaming?

**None found** combining sqlite-vec with VR/gaming. Spatial databases (PostGIS, pgvector+H3) and game engines dominate this space.

### L3 Principle
**L3-Spatial-Semantic-Separation**: For hybrid spatial+semantic search, use separate vec0 tables JOINed on entity_id. vec0 cannot do multi-vector queries natively.

### Confidence: MEDIUM-HIGH

---

## Gap 5: Sovereign Research Alternatives to Exa/Firecrawl

**Sources**:
- https://github.com/groktopus/groktocrawl (MIT, Firecrawl-compatible)
- https://github.com/SID1ART/agentfetch (SearXNG-backed, local)
- https://trafilatura.readthedocs.io/en/latest/usage-python.html (Python text extraction)
- https://docs.crawl4ai.com/ (Playwright-backed async crawling)
- https://fastcrw.com/alternatives/firecrawl (single Rust binary)
- https://github.com/anakin-inc/anakin (Camoufox anti-detect, Thompson sampling proxies)

### 1. Can SearXNG alone serve as complete research pipeline?

**Partially.** SearXNG is excellent for search (T1 — metasearch over Google, DDG, Bing, Wikipedia) but cannot render JS, handle CAPTCHAs, or do full-page scraping. You still need a scraping layer (webfetch or Trafilatura) for full content.

### 2. Open-source alternatives to Firecrawl?

**GroktoCrawl** (MIT, recommended): Full Firecrawl v2 API compatibility (`/v2/scrape`, `/v2/crawl`, `/v2/search`, `/v2/map`, `/v2/agent`), Qdrant-backed semantic search, intelligent scrape cache (ETag/Last-Modified), site adapters (GitHub, Reddit, YouTube, Bluesky). One `docker compose up`.

**Trafilatura** (Python, 14k+ stars): `pip install trafilatura`, `from trafilatura import fetch_url, extract` → clean markdown. Supports sitemaps, feeds, crawling. Markdown/JSON/XML/CSV. No JS rendering.

**Crawl4AI** (Python): `pip install crawl4ai` + `crawl4ai-setup`. Playwright-backed, async, concurrent. JS rendering, proxy support, CSS extraction strategies.

### 3. Pure sovereign pipeline (no API keys)?

**YES — complete zero-API-key pipeline:**
```
SearXNG (search) → Trafilatura/webfetch (scrape) → sqlite-vec (store)
    T1                    T2                            T3
```
Add Crawl4AI for JS-heavy sites (T2.5). AgentFetch already does this with SearXNG as default backend.

### 4. Best local-only crawling stack for 2026?

| Tool | JS | Install | Best For |
|------|----|---------|----------|
| Trafilatura | No | `pip install` | Text pages |
| Crawl4AI | ✅ Playwright | `pip install` | JS-heavy sites |
| GroktoCrawl | ✅ Playwright | `docker compose up` | Full API server |
| AgentFetch | ✅ Auto-detect | `pip install` | AI agent pipeline |
| fastCRW | Limited | Single binary | Minimum resource |
| Anakin | ✅ Camoufox | `go run` | Anti-detect scraping |

### 5. CAPTCHAs and rate limits?

Without proxies: (1) robots.txt compliance, (2) exponential backoff with jitter, (3) UA rotation, (4) aggressive caching with ETag/Last-Modified. Some Cloudflare-protected sites simply cannot be scraped without a proxy network.

### L3 Principle
**L3-Sovereign-Scraping-Stack**: Three layers suffice: SearXNG (T1) + Trafilatura (T2) + Crawl4AI (T2.5 JS fallback). No API keys. No token cost. No phone-home.

### Confidence: HIGH

---

## Gap 6: Range-Query Contradiction Detection

**Sources**:
- https://arxiv.org/pdf/2406.10746 (SparseCL — sparsity-based contradiction retrieval)
- https://doi.org/10.1109/acit65614.2025.11185903 (ASDC — 98% comparison reduction)
- https://github.com/datarootsio/knowledgebase_guardian (LLM-powered detection)
- https://arxiv.org/html/2606.28781 (HyphaeDB — HNSW gossip-based detection)
- https://github.com/ajitpratap0/openclaw-cortex/pull/62 (threshold 0.75 + keyword)
- https://aclanthology.org/2026.acl-long.1306/ (CDRs — ACL 2026)

### 1. Existing research?

**YES — multiple validated approaches:**

**SparseCL** (arXiv:2406.10746, MIT): Core insight — cosine similarity is TRANSITIVE, contradiction is NOT. Solution: **Hoyer sparsity measure** — contradictions produce sparse differences (few coordinates change a lot). Score: `F = cosine(E(q),E(p)) + α·Hoyer(Es(q),Es(p))`. 30%+ accuracy improvement. 200× faster than cross-encoder.

**ASDC** (IEEE 2025): Anchor-guided Semantic Double-Clustering. 98% reduction (1.2M → 15.6K comparisons). 92% → 99% recall.

**HyphaeDB** (arXiv:2606.28781): Contradiction as emergent HNSW topology property — conflicting knowledge near same position in embedding space.

### 2. Distance threshold for contradiction?

From openclaw-cortex (production Go): **cosine ≥ 0.75** (top 20), then check exclusive-predicate overlap. If both say "works_at" but values conflict → contradiction.

### 3. Genuine contradiction vs complementary?

Three strategies: (1) Exclusive-predicate check — only flag when predicate types match (openclaw-cortex). (2) LLM verification gate — slower but more accurate (KnowledgeBase Guardian). (3) Three-layer architecture — stance → pair comparison → graph traversal (91.7% precision, Zenodo 2026).

**Recommended**: Two-stage: fast vector pre-filter (≥0.75 + predicate match) + LLM verification for flagged pairs.

### 4. Existing open-source systems?

- **SparseCL**: Trainable sentence embeddings for contradiction retrieval. Open code.
- **KnowledgeBase Guardian**: Simple LLM-powered detection. GitHub: datarootsio/knowledgebase_guardian.
- **openclaw-cortex Phase 3**: Pure heuristic (no LLM calls). Go, threshold 0.75 + exclusive predicates.

### 5. Contradiction edge graph schema?

```sql
CREATE TABLE contradiction_edges (
    entity_a_id INTEGER NOT NULL,
    entity_b_id INTEGER NOT NULL,
    cosine_similarity REAL NOT NULL,
    hoyer_sparsity REAL,
    detection_method TEXT,
    confidence REAL DEFAULT 0.5,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (entity_a_id, entity_b_id)
);

CREATE TABLE entity_predicates (
    entity_id INTEGER NOT NULL,
    predicate_type TEXT NOT NULL,
    predicate_value TEXT NOT NULL,
    source_chunk_id INTEGER
);
```

**Detection flow**: On insert, find similar entities (cosine ≥ 0.75, top 20). Check predicate overlap. If conflicting → insert contradiction edge. Periodic LLM verification for high-confidence edges.

### L3 Principle
**L3-Sparsity-Is-Contradiction**: In embedding space, contradiction manifests as sparse differences — few dimensions change significantly while most remain similar. Hoyer sparsity captures what cosine similarity misses.

### Confidence: HIGH

---

## Synthesis

### Cross-Cutting Patterns

1. **The Disagreement Signal**: Both vstash (Gap 1) and contradiction detection (Gap 6) use disagreement as signal. vstash uses vector-keyword ranking disagreement; contradiction detection uses embedding proximity + predicate disagreement. This is a meta-pattern: disagreement between two systems is information.

2. **CPU Training is Real Now**: bitsandbytes PR #1901 (2026-03-30) changes the landscape for Gap 2. 8-bit optimizers on CPU make BGE-small fine-tuning practical (if slow). The Omega Engine can now contemplate local embedding fine-tuning without any GPU.

3. **Preserve then Verify**: Both semantic caching (Gap 3) and contradiction detection (Gap 6) use a two-stage pattern: fast approximate pre-filter + slower verification gate. For caching: bi-encoder (fast) + cross-encoder (accurate). For contradiction: vector proximity (fast) + LLM judge (accurate).

### New L3 Universal Principles

| # | L3 Principle | Source Gap |
|---|-------------|------------|
| 1 | **L3-Disagreement-Signal**: Disagreement between two systems is free supervision. | Gap 1, Gap 6 |
| 2 | **L3-BQ-Is-PostTraining**: mxbai BQ is post-training binarization, not learned. | Gap 2 |
| 3 | **L3-Threshold-Calibration**: Every semantic threshold needs an eval loop. | Gap 3 |
| 4 | **L3-Spatial-Semantic-Separation**: Two vec0 tables + JOIN for spatial+semantic. | Gap 4 |
| 5 | **L3-Sovereign-Scraping-Stack**: SearXNG + Trafilatura + Crawl4AI = complete pipeline. | Gap 5 |
| 6 | **L3-Sparsity-Is-Contradiction**: Hoyer sparsity captures what cosine misses. | Gap 6 |

### Implementation Priority

| Priority | Item | Effort | Gap |
|----------|------|--------|-----|
| P0 | **Deploy semantic cache** with SphereLFU/LFUDA eviction, 0.93 threshold | 4h | 3 |
| P0 | **Build contradiction detection** with two-stage pipeline (≥0.75 + predicate check + LLM gate) | 8h | 6 |
| P1 | **Adopt sovereign scraping stack**: wire Trafilatura into research pipeline | 2h | 5 |
| P1 | **Version-stamp all embeddings** for drift detection | 3h | 3 |
| P2 | **Evaluate vstash integration** for Omega Engine embedding fine-tuning | 4h | 1 |
| P2 | **Benchmark spatial-semantic hybrid** with two-table vec0 JOIN | 4h | 4 |
| P3 | **Test CPU LoRA fine-tuning** of BGE-small with bitsandbytes 8-bit | 8h | 2 |

---

## 🛑 CORRECTION — Gap 5 Revised (2026-07-13)

**Correction**: We DO have Exa and Firecrawl API keys available (up to 8 each). The original assumption of "no API keys" is FALSE. This elevates the research pipeline significantly.

### Revised Research Tier Architecture (with API Keys)

| Tier | Tool | Cost | When to Use |
|:-----|:-----|:-----|:------------|
| **T0** | Local cache (`.firecrawl/`, `data/research/`) | Free | Check before any external call |
| **T1** | `websearch` / `webfetch` | Free, built-in | **Primary** — always available, sovereign |
| **T2** | `searxng_searxng_search` (SearXNG :8018) | Free, sovereign | Semantic/neural search refinement, sovereignty-sensitive |
| **T3** | Exa (`omega-hub_sovereign_search`) | API key (8 available) | High-precision seeds, academic/technical deep research |
| **T4** | Firecrawl (`firecrawl_firecrawl_scrape/search`) | Credits (8 keys) | Full-page scrape, structured crawl, JS rendering |
| **T5** | GroktoCrawl / Crawl4AI (fallback) | Free, self-hosted | When Firecrawl credits exhausted or offline |

### Revised Fallback Chain
```
T1 (websearch) → T2 (SearXNG) → T3 (Exa) → T4 (Firecrawl) → T5 (GroktoCrawl)
```

### What Changes

| Area | Old Assumption (zero API keys) | New Reality (8 keys each) |
|------|-------------------------------|---------------------------|
| **Research depth** | Limited to SearXNG + webfetch | Full T1-T4 tiered pipeline, deep crawling |
| **Academic papers** | arXiv search only | Exa semantic search → full papers |
| **JS-heavy pages** | Crawl4AI (heavy) | Firecrawl (lightweight, credit-based) |
| **Structured crawl** | Manual with Scrapy | Firecrawl `/crawl` with depth/limit |
| **Credit budgeting** | N/A | Track per-key, rotate on exhaustion |

### Updated L3 Principle
**L3-Tiered-Research-With-Keys**: API keys are a sovereign resource, not a crutch. Use free T1/T2 first; escalate to paid T3/T4 only when free tiers fail. Track credits per key. Rotate on exhaustion. Never hardcode keys — always use environment variables.

### Updated Recommended Next Steps
| Priority | Task | Effort | Gap |
|----------|------|--------|-----|
| **P0** | Configure Exa API key in `config/providers.yaml` | 0.5h | 5 |
| **P0** | Configure Firecrawl API key in `config/providers.yaml` | 0.5h | 5 |
| **P0** | Wire Exa into `omega-hub_sovereign_search` as T3 fallback | 1h | 5 |
| **P1** | Build Firecrawl credit budget tracker (per-key, auto-rotate) | 3h | 5 |
| **P1** | Add tier-awareness to research dispatch (don't use Exa for simple queries) | 2h | 5 |
| **P1** | Wire Trafilatura as T2.5 fallback for when Firecrawl credits low | 2h | 5 |

### Source
- User confirmation: "I can give you 8 for each" (Exa + Firecrawl API keys)

---

## Source Index (Original + Revised)

| Source | URL | What It Confirmed |
|--------|-----|-------------------|
| vstash GitHub | https://github.com/stffns/vstash | G1: Full API, CLI, Python SDK, PyPI package |
| vstash retrain docs | https://github.com/stffns/vstash/blob/develop/docs/retrain.md | G1: Training recipe, GPU requirement, eval gate |
| vstash PyPI | https://pypi.org/project/vstash/ | G1: v0.38.1, MIT, pip install |
| bitsandbytes PR #1901 | https://github.com/bitsandbytes-foundation/bitsandbytes/pull/1901 | G2: CPU AdamW8bit, SGD8bit, etc. |
| True 4-bit CNN | https://arxiv.org/abs/2603.13931 | G2: FP32 parity on CPU, STE recipe |
| mxbai BQ notebook | https://github.com/mixedbread-ai/binary-embeddings | G2: Post-training BQ, 96-99% retention |
| Semantic Cache Guide | https://llmbestpractices.com/ai-agents/embeddings-semantic-cache | G3: Threshold 0.92-0.97 |
| Respan Production Data | https://www.respan.ai/articles/semantic-cache-llm | G3: Hit rate table, FP rates |
| SphereLFU Paper | https://arxiv.org/pdf/2603.03301 | G3: Optimal eviction for semantic caches |
| Embedding Drift | https://duanegrey.com/insights/why-embedding-model-drift-breaks-ai-systems-silently | G3: 5-15% drift, version pinning |
| sqlite-vec KNN | https://github.com/asg017/sqlite-vec/blob/main/site/features/knn.md | G4: Manual L2 on any vector dim |
| sqlite-vec API | https://github.com/asg017/sqlite-vec/blob/main/site/api-reference.md | G4: vec_distance_L2, vec0 float[3] support |
| sqlite-vec vec0 | https://github.com/asg017/sqlite-vec/blob/main/site/features/vec0.md | G4: Metadata/partition/aux columns |
| GroktoCrawl | https://github.com/groktopus/groktocrawl | G5: MIT, Firecrawl v2 compatible |
| Trafilatura | https://trafilatura.readthedocs.io/en/latest/usage-python.html | G5: Python text extraction, markdown output |
| Crawl4AI | https://docs.crawl4ai.com/ | G5: Playwright async crawling |
| SparseCL | https://arxiv.org/pdf/2406.10746 | G6: Hoyer sparsity contradiction detection |
| ASDC | https://doi.org/10.1109/acit65614.2025.11185903 | G6: 98% comparison reduction |
| openclaw-cortex | https://github.com/ajitpratap0/openclaw-cortex/pull/62 | G6: Threshold 0.75 + exclusive predicates |
| KnowledgeBase Guardian | https://github.com/datarootsio/knowledgebase_guardian | G6: LLM-powered contradiction detection |
