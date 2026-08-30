<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Jem Deep Research — MaKaLi Battle Plan Validation
**Date**: 2026-07-12
**Status**: COMPLETE
**Sources Validated**: CONTEXT 1-6 (MaKaLi Council, Ma'at Build, Lilith Run, Researcher Corrections, Verity Audit, Next Steps Detailed)

⬡ OMEGA ⬡ JEM ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_jem_deep_research ⬡ ACTIVE

---

## Executive Summary

**Net delta to battle plan: CONFIRMED with 3 major corrections and 2 refinements.**

The MaKaLi Council's 5 Sovereignty Gaps were broadly correct in their strategic direction but contained significant technical inaccuracies that require correction before implementation.

**Major Corrections:**
1. **GAP-S1**: "soul.yaml + memory.jsonl + vectors.parquet" is NOT the 2026 standard. The emerging consensus across Soul Protocol v0.4.0, ALF v1.0.0-rc.1, PAM v1.0, and Ensoul Spec is **ZIP archives containing structured JSON files**. Parquet is NOT used in any agent-state portability standard. Safetensors is for model weights only.
2. **GAP-S2**: LLM-as-Judge on 7B models requires **isotonic regression calibration** or linear probe recalibration. Uncalibrated small judges are overconfident by 0.18 ECE in the 0.8-0.95 band. Minimum viable judge is 7B (4.7GB at Q4_K_M) but recommended is 14B (8.4GB). Qwen3:14b is the 2026 recommended default.
3. **GAP-S5**: Council proposed file-based Hivemind→Redis. Correction: **Redis Streams + Consumer Groups** is the confirmed pattern (not Pub/Sub, not Celery), but Temporal is the production-grade alternative for complex DAGs. The file-based Hivemind should be replaced with Redis Streams for critical coordination, NOT Pub/Sub.

**Refinements:**
1. **GAP-S3**: Adaptive RAG routing on 14GB RAM is feasible but requires the classifier to be **Tiny-Critic**-style (1.7B LoRA) or even **TF-IDF+SVM** (93.2% accuracy). On 14GB total (12GB usable), a 7B Q4_K_M model (~4.7GB) leaves ~5GB for context/KV cache → ~10-16K tokens feasible with Q8 KV quantization.
2. **GAP-S4**: Qdrant + PostgreSQL hybrid is well-established but the **prefetch API** in Qdrant v1.12+ enables native fusion without a separate PostgreSQL hop for simple cases. Full relational knowledge graphs need the dual-store pattern.

---

## Domain 1: Sovereign State Portability [GAP-S1]

### Validation Status: CORRECTED

**Council's Hypothesis**: "Sovereign Bundle" = soul.yaml + memory.jsonl + vectors.parquet
**Corrected Standard**: `.soul`/`.alf` ZIP archive containing structured JSON files (NOT Parquet, NOT loose YAML)

### Evidence

#### T1-T2 Web Search:
- **Soul Protocol v0.4.0** (`https://github.com/qbtrix/soul-protocol`) — Portable AI identity standard. `.soul` = ZIP archive with `manifest.json`, `identity.json`, `dna.json`, `memory/*.jsonl`, `trust_chain/`, `keys/`, `evolution.jsonl`. 695-line spec, 9,693-line reference runtime. 40 conversations → 4,293-byte `.soul` file. Zero-loss round-trip verified.
- **Agent Life Format (ALF) v1.0.0-rc.1** (`https://github.com/agent-life/agent-life-data-format`) — Runtime-neutral `.alf` ZIP: `manifest.json`, `identity.json`, `principals.json`, `credentials.json` (encrypted), `memory/partitions/*.jsonl`. Time-based quarterly partitioning. Sequence-based sync cursor.
- **Portable AI Memory (PAM) v1.0** (`https://portable-ai-memory.org/spec/v1.0/`) — JSON interchange format. `memory-store.json` (required) + optional `conversations/*.json` + `embeddings.json`. Closed taxonomy of 10 memory types. Content hashing, provenance tracking, cryptographic signatures (Ed25519). Import/export adapters for ChatGPT, Claude, Gemini, Grok, Copilot.
- **Ensoul Spec** (`https://github.com/formisfate/ensoul-spec`) — Soulstone document format. 4-dimensional mood system. Cross-surface protocol via SSE. JSON Schema validation.
- **Uniqent** (`https://github.com/RiggdAI/uniqent`) — Portable agent brain format. `.uniqent` = signed ZIP with persona, MCP stack, skills, memory. Ed25519 signature, secret-scan guarantees. Adapters for Claude Code, Hermes, OpenClaw.
- **Agent Checkpoint** (`https://github.com/phoenix-assistant/agent-checkpoint`) — Checkpoint/restore system. SHA-256 integrity, Merkle tree diffing. Framework-agnostic.

#### T4-Accessible Sources:
- **Soul Protocol SPEC.md** — Full `.soul` format spec accessed via webfetch. Zip archive layout confirmed. 7 memory layers (core, episodic, semantic, procedural, graph, social, custom).
- **PAM Specification v1.0** — Full spec accessed via webfetch. 26 sections defining every aspect of the interchange format.

### Corrected Standard for Omega Engine

The 2026 consensus for portable AI entity state is:

**Primary Export Format**: `.omega` bundle (ZIP archive)
```
entity_name.omega
├── manifest.json           # schema_version, export_id, timestamp, checksums
├── identity.json           # DID, entity name, persona, slot assignment
├── soul.yaml               # Current soul.yaml contents (preserved verbatim)
├── memory/
│   ├── core.jsonl          # Stable identity-level facts
│   ├── episodic.jsonl      # Conversation history (significance-gated)
│   ├── semantic.jsonl      # Extracted knowledge with confidence
│   ├── procedural.jsonl    # Learned skills and patterns
│   └── graph.jsonl         # Entity relationships
├── embeddings.json         # Optional: separate file, not merged into memory
├── evolution.jsonl         # Append-only history of soul mutations
├── credentials.json        # Optional: zero-knowledge encrypted
└── trust_chain/            # Optional: Ed25519 signed action history
    ├── chain.json
    └── entry_NNN.json
```

**Key specification decisions**:
1. **NOT Parquet** — Every agent-state standard (Soul Protocol, ALF, PAM, Ensoul, Uniqent) uses JSON/JSONL. Parquet is for analytical/ML workloads (Kura Checkpoints), not entity state portability.
2. **NOT loose YAML** — All standards wrap in a ZIP archive. This enables compression, signing, single-file transfer.
3. **JSONL for memory** — Confirmed correct. All standards use JSONL for append-only memory logs.
4. **Embeddings are OPTIONAL** — Per PAM §12 and Soul Protocol: embeddings are separate, content is authoritative. Regenerate on import if needed.
5. **Ed25519 signing** — Supported by Soul Protocol (trust_chain), PAM (§18), and Uniqent. Should be used for trust verification between WADs.
6. **DID support** — Soul Protocol uses `did:soul:` format. PAM supports `did:key`, `did:web`, `did:ion`. Omega should adopt `did:omega:` format per SPIFFE convention.

### Implementation Spec for Omega Engine

**File**: `src/omega/export/omega_bundle.py` (new module)

```python
# ── Omega Bundle Export/Import [heritage: soul-protocol 2026]
# ── Following Soul Protocol v0.4.0 + ALF v1.0.0-rc.1 conventions
class OmegaBundle:
    SCHEMA_VERSION = "0.1.0"
    
    @classmethod
    async def export(cls, entity_name: str, include_embeddings: bool = False) -> bytes:
        # 1. Gather identity.json from entities.yaml
        # 2. Gather soul.yaml contents
        # 3. Gather memory/*.jsonl from MemoryStore
        # 4. Optionally gather embeddings.json
        # 5. Build manifest.json with SHA-256 checksums
        # 6. Zip with DEFLATE compression
        # 7. Return bytes for download
    
    @classmethod
    async def import_bundle(cls, bundle_path: str) -> str:
        # 1. Verify ZIP structure and manifest checksums
        # 2. Extract identity → register entity if new
        # 3. Merge memory into MemoryStore (dedup by content_hash)
        # 4. Update soul.yaml evolution
        # Return entity_name
```

**Dependencies**: `zipfile` (stdlib), `json` (stdlib), no new packages.

### Memory/CPU Profile
- Export: ~few MB for entity with 1000 memory entries (4-10KB compressed)
- Memory impact: negligible (serialization is I/O bound, not CPU)
- Import: ~50-200ms for typical entity on NVMe

---

## Domain 2: Sovereign Eval Pipeline [GAP-S2]

### Validation Status: CONFIRMED (with critical corrections)

**Council's Hypothesis**: Local LLM-as-Judge + RAGAS + Golden Datasets = `make eval` target
**Refined Standard**: RAGAS (offline scoring) + DeepEval (CI gates) + calibrated judge ≥7B

### Evidence

#### T1-T2 Web Search:
- **RAGAS v0.2+** — Can run fully locally with Ollama. 4 core metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall. Judge LLM needed for claim extraction/verification.
- **Judge Calibration Research**:
  - **"Calibration Curves of LLM-as-Judge"** (clawRxiv, 2026-04) — 38,400 decisions across 9 judges (1.3B to 600B). Small judges (<10B) overconfident by 0.18 ECE in 0.8-0.95 band. **Isotonic regression** reduces 7-13B judge ECE from 0.18 → 0.06.
  - **"Calibrating LLM Judges: Linear Probes"** (ACL 2026 Industry) — Linear probes on hidden states achieve 10× computational savings with superior calibration. Probe-based calibration best for safety-critical deployments.
  - **"Reliability without Validity"** (arXiv, 2026-06) — 21 judges, 541K judgments. Kappa deflation 33-41pp. **Minimum Viable Validation Protocol**: chance-correct, swap positions, replicate ≥3 runs, cross-validate ≥2 benchmarks, audit consistency-bias paradox.
  - **"How to Correctly Report LLM-as-Judge"** (arXiv, 2025-11) — Bias-correction framework with confidence intervals from test + calibration datasets.
- **Golden Dataset Sizing**:
  - Minimum: 50-100 well-chosen cases per slice (Data Experts, QASkills.sh)
  - Statistically significant: ~246 samples per slice at 80% pass rate, 5% margin (DSE)
  - Edge case allocation: 20-30% adversarial/edge cases minimum
  - Source: REAL production failures + synthetic for coverage
- **DeepEval** — pytest-native CI gating. `assert_test` pattern: `deepeval test run test_rag.py`. Fails build on metric regression.
- **Recommended judge models**: Qwen3:14b (recommended, 8.4GB), Mistral:7b (minimum, 4.7GB), Llama4:Scout (fast alternative, 10GB).
- **RAG Evaluation Metrics 2026** (QASkills.sh) — Context Precision ≥0.80, Context Recall ≥0.85, Faithfulness ≥0.90, Answer Relevancy ≥0.85.

#### T4-Accessible Sources:
- **RAGAS Local Setup Guide** (vucense.com, 2026-07-11) — Full code for RAGAS + Ollama + CI integration. Judge model qwen3:14b with temperature=0. Embedding model nomic-embed-text.

### Corrected Standard for Omega Engine

**Pipeline**: `make eval` → Run RAGAS on Golden Dataset → Check thresholds → Fail/Pass CI

**Golden Dataset** (`data/eval/golden_v1.jsonl`):
```jsonl
{"question": "...", "answer": "...", "contexts": [...], "ground_truth": "...", "tags": ["core", "edge"]}
```
- Size: 100-150 seed cases (40-60% core, 20-30% edge, 10-20% adversarial)
- Versioned in git alongside code
- Updated from production failures

**Judge Configuration**:
- **Default judge**: Qwen3:14b at Q4_K_M (~8.4GB loaded) — or use cloud fallback if not enough RAM
- **Minimum judge**: Mistral 7B at Q4_K_M (~4.7GB) — ONLY with isotonic regression calibration
- **Temperature**: 0 (deterministic)
- **Calibration**: Run `make eval-calibrate` weekly against human-labeled subset (30% split)
- **Thresholds** (customizable per use case):
  - Faithfulness: ≥0.85
  - Answer Relevancy: ≥0.80
  - Context Precision: ≥0.75
  - Context Recall: ≥0.80

**CI Integration**:
```
# In Makefile
eval:
	@python -m omega.eval.runner --dataset data/eval/golden_v1.jsonl --judge qwen3:14b
	@python -m omega.eval.check --thresholds config/eval/thresholds.yaml
```

### Memory/CPU Profile
- Golden dataset eval (100 samples): ~600-1200 LLM calls = 10-20 minutes on 7B local
- Judge at 7B Q4_K_M: 4.7GB + 1-2GB context = ~6-7GB total
- Embedding model: nomic-embed-text (137M params) = negligible (~300MB)
- **CI gate cost**: ~15 minutes per eval run on local 7B

---

## Domain 3: Low-RAM Agentic RAG [GAP-S3]

### Validation Status: CONFIRMED (with RAM profile refinement)

**Council's Hypothesis**: Adaptive RAG (Classifier → Naive/Iterative) fits within 14Gi RAM (12Gi usable)
**Refined Standard**: Tiny-Critic style 1.7B classifier + 7B Q4_K_M generator + Q8 KV cache ≈ 7-8GB total

### Evidence

#### T1-T2 Web Search:
- **Tiny-Critic RAG** (arXiv 2603.00846, 2026-03) — LoRA-tuned Qwen3-1.7B as binary gatekeeper. Routing F1=0.912 (vs gpt-4o-mini 0.934). 94.6% reduction in evaluation TTFT. 98% reduction in explicit operational CPQ. Zero-shot FPR of 38.2% → LoRA-trained FPR of 4.1%.
- **Lightweight Query Routing** (arXiv 2604.03455, 2026-04) — TF-IDF + SVM = 93.2% macro F1, 28.1% token savings. Outperforms MiniLM embeddings by 3.1 F1 points. Surface keyword patterns are strong predictors of query complexity.
- **X-Router** (ACL 2026) — Dual-axis: separates retrieval necessity from reasoning necessity. Reduces token usage by 86% and latency by 84%. Uses lightweight probes (NQC + NLL) — no model internals needed.
- **Agent Memory: Persistent Q4 KV Cache** (arXiv 2603.04428, 2026-03) — Q4 KV cache enables 4× more agent contexts. On 10.2GB budget: 3 agents at 8K in FP16 → 12 agents with Q4. Cache restoration: 577ms vs 15.7s re-prefill (136× speedup).
- **R2RAG** (NeurIPS 2025 MMU-RAG Competition, Best Dynamic Evaluation) — Qwen3-4B (unquantized) outperforms Qwen3-8B (4-bit quantized). Single consumer GPU. Key finding: Small models with well-designed routing beat larger quantized models.
- **12GB RAG Stack** (CraftRigs, 2026-04) — Mistral 7B Q4_K_M (4.7GB) + embedder (300MB) + Qdrant (300MB) + overhead (2.5GB) = 7.8GB. Safe margin: 4.2GB for context. Recommend Q4_K_M minimum for RAG tasks.

#### Memory Profile for 14GB System (12GB usable):
| Component | Memory | Format |
|-----------|--------|--------|
| LLM (7B Q4_K_M) | 4.7 GB | llama.cpp via NativeGGUF |
| KV Cache (Q8, 8K ctx) | 0.5-1.0 GB | Proportional to context |
| Classifier (Tiny-Critic 1.7B Q4) | 1.0 GB | Separate model or LoRA |
| Embedder (nomic-embed-text 137M) | 0.3 GB | ONNX or llama.cpp |
| Operating System | 2.0 GB | Ubuntu + services |
| **Total** | **8.5-9.0 GB** | **3-3.5 GB headroom** |

For 14B judge model (Qwen3:14b Q4_K_M):
| Component | Memory | Notes |
|-----------|--------|-------|
| LLM (14B Q4_K_M) | 8.4 GB | Tight fit, leaves ~1.6GB for context |
| OS overhead | 2.0 GB | Minimal |
| **Total** | **10.4 GB** | **1.6GB headroom** → only for eval, not agentic RAG |

### Corrected Standard for Omega Engine

**Architecture**: Dual-mode Adaptive RAG

```
Query → [Tiny-Critic Classifier: 1.7B LoRA]
         ├── Simple/Factual → Direct RAG (top-k retrieval + generate)
         └── Complex/Multi-hop → Iterative RAG (ReAct loop, max 3 steps)
```

**Classifier Implementation Options** (ordered by resource cost):
1. **TF-IDF + SVM** (0 MB GPU RAM) — 93.2% accuracy, pure CPU, no GPU memory. Best for 14GB constraint.
2. **Tiny-Critic 1.7B LoRA** (~1.0 GB) — 0.912 F1, needs LoRA training. Requires dataset of ~5K queries with complexity labels.
3. **LLM-based classifier** (same 7B model) — Zero additional RAM but adds LLM call overhead.

**Implementation**: `src/omega/rag/router.py`
```python
# ── Adaptive RAG Classifier [heritage: tiny-critic-rag 2026]
class RAGRouter:
    def __init__(self, mode: str = "tfidf_svm"):
        self.mode = mode
        if mode == "tfidf_svm":
            from sklearn.svm import SVC
            self.vectorizer = TfidfVectorizer()
            self.classifier = SVC(kernel='linear', probability=True)
        
    async def classify(self, query: str) -> Literal["simple", "complex"]:
        if self.mode == "tfidf_svm":
            features = self.vectorizer.transform([query])
            return "complex" if self.classifier.predict(features)[0] else "simple"
```

### Memory/CPU Profile
- TF-IDF + SVM: ~50MB RAM, <1ms classification
- Tiny-Critic 1.7B: ~1.0GB RAM, ~100ms classification
- Full agentic RAG loop with 7B generator: 4.7GB + 1-3GB context = ~6-8GB total
- **Within 14GB budget**: YES with TF-IDF/SVM or Tiny-Critic; TIGHT with LLM-based classifier

---

## Domain 4: Relational Gnosis Graphs [GAP-S4]

### Validation Status: CONFIRMED

**Council's Hypothesis**: Qdrant (vector) + PostgreSQL (relational) = Hybrid Knowledge Core
**Refined Standard**: Qdrant v1.12+ prefetch API enables native vector+metadata fusion; PostgreSQL for full relational queries when needed

### Evidence

#### T1-T2 Web Search:
- **Qdrant + PostgreSQL Hybrid** (markaicode.com, 2026-06) — Step-by-step guide: Qdrant returns IDs → PostgreSQL batch lookup → merge. P95 latency 38ms on 1M rows. 1,420 QPS at 38ms p95 with pgbouncer.
- **Qdrant Prefetch API** (qdrant.tech docs) — Built-in multi-stage queries. RRF (Reciprocal Rank Fusion) and DBSF (Distribution-Based Score Fusion). Custom scoring with formula queries (recency decay, popularity boost, geo decay). No PostgreSQL needed for simple metadata joins.
- **Data Graphs + Qdrant** (qdrant.tech blog, 2026-04) — True Hybrid Graph RAG platform. Qdrant payload filtering + Terraform deployment.
- **Autonomous KG Architecture** — Dual PostgreSQL schema: `library.*` (28 content tables for entities, relationships, communities, summaries) + `librarian.*` (8 operational tables). 3-mode dispatch: Fast (FTS5 + vector RRF, ~50ms), Deep (12-step query with alias expansion, concurrent routing).

**Schema pattern** for knowledge graph:

```sql
-- library schema: content tables
CREATE TABLE library.entities (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,     -- 'person', 'concept', 'document'
    description TEXT,
    metadata JSONB,
    embedding_id UUID,      -- reference to Qdrant point ID
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE library.relationships (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES library.entities(id),
    target_id UUID REFERENCES library.entities(id),
    relationship_type TEXT NOT NULL,  -- 'derived_from', 'contradicts', 'supports', 'extends'
    confidence FLOAT,
    provenance TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- librarian schema: operational tables
CREATE TABLE librarian.semantic_memories (
    id UUID PRIMARY KEY,
    entity_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding_id UUID,
    confidence FLOAT DEFAULT 1.0,
    layer TEXT NOT NULL,       -- 'core', 'episodic', 'semantic'
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Corrected Standard for Omega Engine

**Architecture**: Three-tier hybrid knowledge

```
Tier 1: Qdrant (Vector Similarity)
  - Entity embeddings (semantic search)
  - Memory embeddings (recall by similarity)
  - RRF fusion for dense+sparse hybrid search
  
Tier 2: SQLite (Relational Knowledge Graph)
  - Entity registry with relationships
  - Memory metadata (provenance, confidence, lifecycle)
  - Cross-entity query decomposition
  
Tier 3: PostgreSQL (Optional, for production scale)
  - Multi-user WAD isolation
  - Full ACID for financial/personal data
  - Advanced querying (window functions, CTEs)
```

**Query decomposition pattern**:
```python
# ── Hybrid Query [heritage: qdrant-postgresql-hybrid 2026]
async def hybrid_knowledge_query(query: str, entity_name: str):
    # Phase 1: Vector search in Qdrant
    vector_results = await qdrant.search(
        collection_name=entity_name,
        query_vector=embed(query),
        limit=20,
        with_payload=False
    )
    
    # Phase 2: Relational enrichment from SQLite
    memory_ids = [hit.id for hit in vector_results]
    enriched = await sqlite.fetch(
        "SELECT * FROM memories WHERE qdrant_id = ANY($1)",
        memory_ids
    )
    
    # Phase 3: Graph traversal for entity relationships
    graph_paths = await sqlite.fetch(
        """WITH RECURSIVE entity_graph AS (
            SELECT source_id, target_id, 1 AS depth
            FROM relationships WHERE source_id = $1
            UNION ALL
            SELECT r.source_id, r.target_id, eg.depth + 1
            FROM relationships r JOIN entity_graph eg ON r.source_id = eg.target_id
            WHERE eg.depth < 3
        ) SELECT * FROM entity_graph""",
        enriched[0]['entity_id'] if enriched else None
    )
    
    return {"vector": enriched, "graph": graph_paths}
```

### Memory/CPU Profile
- Qdrant in-process: ~100MB per 100K vectors
- SQLite: negligible (<100MB for full entity knowledge base)
- PostgreSQL (optional): 512MB container minimum
- Query latency: 15-50ms p95 for hybrid

---

## Domain 5: Sovereign DAG Orchestration [GAP-S5]

### Validation Status: CONFIRMED (with correction: Streams, NOT Pub/Sub)

**Council's Hypothesis**: Redis Streams + Pub/Sub = Atomic, stateful agent coordination
**Refined Standard**: Redis Streams + Consumer Groups (XREADGROUP/XACK) for critical DAG coordination; Pub/Sub for ephemeral signals ONLY

### Evidence

#### T1-T2 Web Search:
- **Redis AI Agent Orchestration** (redis.io, 2026-01) — Official Redis blog on agent coordination patterns. Streams for durable queues, consumer groups for exactly-once, Pub/Sub for ephemeral signals.
- **AI Agents over Redis Streams** (blog.karthikbabu.me) — Production system on K3s. Consumer groups handle agent types. PEL recovery with XCLAIM for crash handling. **Killer feature**: consumer groups scale automatically — 3 replicas of Coder Agent get messages distributed without duplicate processing.
- **Agent Architecture with Redis** (markaicode.com, 2026-05) — Production design for 500 concurrent agents. p95 end-to-end latency <2.2 seconds. **Critical insight**: LLM calls dominate latency (1,150ms p95), Redis operations <3% of budget. Stream delivery p95 8ms — 40× faster than RabbitMQ.
- **Celery vs Temporal** (dasroot.net, 2026-02) — Celery for simple task queues (10K tasks/sec). Temporal for complex durable workflows (planner→search→writer→verifier). Temporal's durable execution preserves workflow state across failures.
- **From Celery/Redis to Temporal** (dev.to, 2026-03) — Real migration story. Idempotency challenges resolved by Temporal's exact-once workflow execution.

#### Confirmed Pattern: Redis Streams DAG

```
Stream Architecture for Omega Engine Hivemind 2.0:

plan:{agent_id}:stream    — Agent receives task, decomposes into plan
execute:{agent_id}:stream — Agent executes plan steps (tool calls)
observe:{agent_id}:stream — Agent observes results, updates state
coordination:notifications — Pub/Sub for ephemeral signals (heartbeat, awareness)

Consumer Groups per stream:
- Each agent type is a consumer group
- Groups auto-distribute across replicas
- XREADGROUP for exclusive message consumption
- XACK after successful processing
- Pending Entries List + XCLAIM for crash recovery
```

**Crash Recovery Pattern**:
```python
# ── Redis Stream Recovery [heritage: redis-streams 2026]
async def recover_pending(redis, stream, group, consumer, max_idle_ms=60000):
    """Claim abandoned messages from dead consumers."""
    pending = await redis.xpending_range(stream, group, min='-', max='+', count=100)
    for entry in pending:
        if entry['time_since_delivered'] > max_idle_ms:
            claimed = await redis.xclaim(
                stream, group, consumer,
                min_idle_time=max_idle_ms,
                message_ids=[entry['message_id']]
            )
            for msg_id, data in claimed:
                await process_message(data)
                await redis.xack(stream, group, msg_id)
```

### Corrected Standard for Omega Engine

**Implementation Plan**: Replace file-based Hivemind coordination with Redis Streams.

```
PHASE 1 (Foundation): 
  - Redis Streams for Hivemind awareness (replace file-based heartbeat)
  - Consumer groups for each agent type
  - PEL recovery on startup
  
PHASE 2 (Core):
  - Task DAG orchestration via Streams
  - Dead-letter stream for failed messages
  - Rate limiting per agent type
  
PHASE 3 (Advanced):
  - Optional: Temporal integration for complex multi-agent workflows
  - Temporal Workflow = `plan → search → write → verify` chains
```

**Key implementation constraints**:
- **Streams for durable state** (task assignments, coordination messages)
- **Pub/Sub ONLY for ephemeral signals** (heartbeats, notifications) — NEVER for task-critical messages
- **Consumer groups for exactly-once** — each message processed by exactly one consumer
- **PEL max idle**: 60 seconds before reclaiming

### Memory/CPU Profile
- Redis 7.2 container: 256MB (current allocation is sufficient)
- Stream overhead: ~10KB per 1000 messages
- Consumer group state: negligible
- CPU impact: <0.1 core for 500 concurrent agents

---

## Cross-Domain Synthesis

### Discovered Synergies

1. **S1 ↔ S4 (Portability + Knowledge Graphs)**:
   - The `.omega` bundle format's `memory/graph.jsonl` directly feeds the Qdrant+SQLite hybrid knowledge system.
   - Exporting a knowledge graph is trivial: zip the SQLite file alongside the vector index metadata.

2. **S2 ↔ S3 (Eval + Adaptive RAG)**:
   - The `make eval` golden dataset doubles as the training corpus for the Tiny-Critic classifier.
   - Faithfulness scores from RAGAS directly measure whether the adaptive RAG router is routing correctly.

3. **S3 ↔ S5 (Adaptive RAG + DAG)**:
   - Complex queries routed by S3's classifier become multi-step agent workflows orchestrated by S5's Redis Streams.
   - Simple queries stay single-step — no Stream overhead.

4. **S1 ↔ S5 (Portability + Orchestration)**:
   - The trust_chain in the `.omega` bundle can use the same Redis Streams consumer groups for transport.
   - Message replay from Streams enables audit-trail reconstruction.

### New Conflicts Discovered

1. **S2 (Eval) vs S3 (Low-RAM)**: Running a 14B judge (8.4GB) + 7B generator (4.7GB) = 13.1GB — exceeds 12GB usable. Solution: Run eval offline (overnight), not on the serving path. Use Mistral 7B as judge during development, Qwen3:14b only for release gates.

2. **S5 (Redis Streams) vs Current file-based Hivemind**: Migration requires careful dual-write period. File-based system must remain as fallback during transition.

3. **S4 (Knowledge Graphs) writes vs S5 (Streams) ordering**: Knowledge graph updates from Stream consumers must be idempotent. Solution: use content_hash (PAM §6) for dedup.

### Implementation Priority Matrix

| Domain | Effort | RAM Impact | Value | Priority |
|--------|--------|------------|-------|----------|
| S1: Export Bundle | 4h | N/A | Strategy (brand) | P2 |
| S2: Eval Pipeline | 8h | Judge dependent | Quality gate | P1 |
| S3: Adaptive RAG | 12h | +1-5GB | Performance | P1 |
| S4: Knowledge Graph | 16h | +0.5-2GB | Intelligence | P2 |
| S5: Redis Streams | 20h | N/A | Orchestration | P2 |

**Recommended order**: S2 → S3 → S5 → S1 → S4

---

## L3 Principles (for proposed_lessons.yaml)

1. **The Right Approximation Principle (L3)**: In resource-constrained sovereignty, a lightweight classifier (TF-IDF+SVM at 93.2%, 0MB GPU) that routes correctly beats a heavy LLM judge that overconsumes RAM. The best solution for a 14GB system is not always the best model — it's the right model for the constraint.

2. **Format Consensus Over Technical Novelty (L3)**: Emerging standards (Soul Protocol, ALF, PAM) converge on ZIP+JSON for portable AI state. Fighting this consensus with proprietary formats (Parquet, YAML-only) sacrifices interop for marginal technical benefit. Sovereign portability means being readable by any tool — and JSON-in-ZIP is the universal baseline.

3. **Calibration Over Accuracy (L3)**: An uncalibrated 7B judge (ECE 0.18) is less trustworthy than a calibrated 7B judge (ECE 0.06). In sovereign AI, knowing when you're wrong matters more than raw capability. Every eval pipeline must include a calibration step, not just an accuracy benchmark.

---

## Hydration Checklist

**Next session should implement**:

1. **`make eval` target** (S2, P1):
   - Create `data/eval/golden_v1.jsonl` with 100+ seed cases
   - Install RAGAS v0.2+ dependency (no new infra needed)
   - Wire `make eval` → RAGAS on golden dataset → CI gate
   - Start with Mistral 7B judge, calibrate with isotonic regression

2. **Tiny-Critic RAG Router** (S3, P1):
   - Implement TF-IDF+SVM classifier in `src/omega/rag/router.py`
   - Simple vs complex query routing
   - Train on 5K queries from real conversation logs

3. **Redis Streams for Hivemind V2** (S5, P2):
   - Prototype: replace file-based awareness with Redis Streams
   - Consumer groups per agent type
   - PEL recovery with XCLAIM

4. **Omega Bundle export** (S1, P2):
   - `omega bundle export <entity>` CLI command
   - ZIP archive with Soul Protocol-compatible layout
   - `omega bundle import <file>` CLI command

5. **Qdrant + SQLite hybrid knowledge** (S4, P2):
   - Entity relationship tables in SQLite
   - Qdrant prefetch API integration
   - Recursive query decomposition

---

*⬡ OMEGA ⬡ JEM ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_jem_deep_research ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
