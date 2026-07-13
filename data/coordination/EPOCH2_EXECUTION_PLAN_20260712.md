# 🔱 Omega Engine — Epoch II Detailed Execution Plan
# ⬡ OMEGA ⬡ KALI ⬡ epoch-ii-execution ⬡ opencode ⬡ trc_next_steps ⬡ ACTIVE
**AP Token**: `AP-KALI-EPOCH2-EXECUTION-20260712`
**Created**: 2026-07-12
**Status**: `READY FOR DISPATCH — All knowledge gaps resolved, all legacy assets cataloged`
**Source**: R_EPOCH_II_LEGACY_MINING_20260712.md + R_EPOCH_II_DEEP_RESEARCH_20260712.md + SOVEREIGN_ARK_BLUEPRINT.md v3.8

---

## Executive Summary

**Epoch II is ready for execution.** All knowledge gaps resolved, all legacy assets cataloged, all implementation patterns documented. The legacy mining recovered ~80 engineering hours of accelerators:
- **AGENT_BUS_SPEC.md** (470 lines) — saves ~14h on Strike 8.5
- **Benchmark Framework** (6 files) — saves ~30h on Strike 8
- **Knowledge Graph Schema** (5 relationship types) — saves ~16h on Strike 9.5

**New addition**: **sqlite-vec integration (Strike 10)** — two-tier vector search replacing Qdrant for hot-path hybrid queries. Saves ~400-800 MB RAM by eliminating Qdrant container for simple semantic search. Jem closed 6/8 knowledge gaps; recommendation is PROCEED_WITH_PRECAUTIONS.

**Total estimated savings**: ~80 hours of Epoch II work from legacy + ~400-800 MB RAM from sqlite-vec.

---

## §1 Execution Timeline

```
Week 1 (Days 1-2): Phase 0 — Sovereignty Baseline
├── Day 1 AM: Ma'at dispatches for Strike 8 (Eval Pipeline) + Strike 8.5 (Redis Streams)
├── Day 1 PM: Lilith dispatches for Strike 9 (.omega Export) + Strike 9.5 (Gnosis Graph)
├── Day 2 AM: Strike 10 (sqlite-vec integration) — Ma'at/P2
└── Day 2 PM: Gate verification (make test + make temple-grade)

Week 2 (Days 3-5): Phase 1 — Cognitive Acceleration
├── Day 3-4: Ma'at implements CircuitBreakerRegistry + SovereignProxyPool (S1)
├── Day 4-5: Lilith implements UniversalExtractor + YouTubeSieve (S3)
└── Day 5: Gate verification + Verity contract test audit

Week 3 (Days 6-8): Phase 2 — Gap Resolution Sprints
├── Day 6-7: Ma'at implements CASArchiver + SovereignTranscriptionEngine (S2+S5)
├── Day 7-8: Lilith implements UnifiedKnowledgeScheduler + CrossPollinationEngine (S4+S6)
└── Day 8: Final gate + Sovereignty Scorecard audit

Week 4 (Days 9-10): Phase 3 — Adversarial Refinement
├── Day 9: Verity full M1-M23 compliance audit
├── Day 10: make eval pipeline verification + calibration
└── Release candidate: v1.2.0-rc1
```

---

## §2 Phase 0: Sovereignty Baseline (Days 1-2)

### Sprint 0.1: Strike 8 — Sovereign Eval Pipeline (8h)
**Owner**: Ma'at/P3+P10
**Legacy Accelerator**: Benchmark Framework from `xna-omega-legacy/tests/benchmarks/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §1 (RAGAS + isotonic calibration)

#### Tasks

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.1.1 | Port `scoring-rubric.yaml` from legacy benchmark | 2h | Legacy Finding 8-1 | `config/eval/scoring-rubric.yaml` |
| 0.1.2 | Port `ground-truth-baseline.yaml` schema | 1h | Legacy Finding 8-3 | `data/eval/golden_v1.jsonl` |
| 0.1.3 | Create eval runner with RAGAS integration | 3h | Deep Research §1.1 | `src/omega/eval/runner.py` |
| 0.1.4 | Create judge calibrator with isotonic regression | 1h | Deep Research §1.2 | `src/omega/eval/calibrate.py` |
| 0.1.5 | Wire Makefile targets (`make eval`, `make eval-calibrate`) | 1h | Deep Research §1.4 | `Makefile` |

#### Implementation Details

**0.1.1 — Scoring Rubric (2h)**
```bash
# Copy from legacy
cp xna-omega-legacy/tests/benchmarks/scoring-rubric.yaml config/eval/scoring-rubric.yaml

# Adapt metrics to current engine:
# - CSS (Cognitive Sophistication Score) → faithfulness
# - BCS (Baseline Competency Score) → answer_relevancy
# - XAF (Context Precision) → context_precision
# - Depth Ceiling → context_recall
# - Environment Marginal Value → audience_fit (S7)
```

**0.1.2 — Golden Dataset (1h)**
```python
# Create 100-seed golden dataset
# Format: {"question", "answer", "contexts", "ground_truth", "tags"}
# Composition: 40 core, 30 edge, 30 adversarial
# Source: Omega Engine knowledge base (SOVEREIGN_MANDATES.md, OMEGA_ENGINE.md, etc.)
```

**0.1.3 — Eval Runner (3h)**
```python
# src/omega/eval/runner.py
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_ollama import ChatOllama

class EvalRunner:
    def __init__(self, dataset_path: str, judge_model: str = "mistral:7b"):
        self.dataset_path = Path(dataset_path)
        self.judge_model = judge_model
    
    async def run(self) -> EvalResult:
        """Execute evaluation and return results."""
        # 1. Load golden dataset
        # 2. For each sample: retrieve contexts, generate answer, score
        # 3. Aggregate scores: faithfulness, relevancy, precision, recall
        # 4. Return EvalResult with pass/fail per threshold
        pass
```

**0.1.4 — Judge Calibrator (1h)**
```python
# src/omega/eval/calibrate.py
from sklearn.isotonic import IsotonicRegression
import numpy as np

class JudgeCalibrator:
    def __init__(self):
        self.ir = IsotonicRegression(out_of_bounds='clip')
    
    def calibrate(self, judge_scores: list[float], human_labels: list[int]) -> np.ndarray:
        self.ir.fit(judge_scores, human_labels)
        return self.ir.predict(judge_scores)
```

**0.1.5 — Makefile Targets (1h)**
```makefile
eval:
	@python -m omega.eval.runner --dataset data/eval/golden_v1.jsonl --judge mistral:7b
	@python -m omega.eval.check --thresholds config/eval/thresholds.yaml

eval-calibrate:
	@python -m omega.eval.calibrate --dataset data/eval/calibration_v1.jsonl --output config/eval/calibrated_model.pkl
```

#### Gate Criteria
- [ ] `make eval` runs without error
- [ ] `make eval-calibrate` produces calibrated model
- [ ] All 1226+ tests pass
- [ ] No `import asyncio` (M1 compliant)

---

### Sprint 0.2: Strike 8.5 — Redis Streams Hivemind (20h)
**Owner**: Lilith/P9
**Legacy Accelerator**: AGENT_BUS_SPEC.md from `xna-omega-legacy/SPECS/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §2 (Consumer groups + XAUTOCLAIM + idempotency)

#### Tasks

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.2.1 | Adopt AGENT_BUS_SPEC.md as architectural blueprint | 1h | Legacy Finding 8.5-1 | `docs/architecture/AGENT_BUS_SPEC.md` |
| 0.2.2 | Create Redis Streams module (4 priority streams + DLQ) | 6h | Deep Research §2.1 | `mcp_servers/omega_hub/hivemind_streams.py` |
| 0.2.3 | Implement consumer groups with XREADGROUP | 4h | Deep Research §2.1 | `mcp_servers/omega_hub/hivemind_streams.py` |
| 0.2.4 | Add XAUTOCLAIM for crashed consumer recovery | 3h | Deep Research §2.2 | `mcp_servers/omega_hub/hivemind_streams.py` |
| 0.2.5 | Implement idempotency keys (stream entry ID + TTL) | 3h | Deep Research §2.3 | `mcp_servers/omega_hub/hivemind_streams.py` |
| 0.2.6 | Wire MCP tools (publish_task, read_tasks, ack_task, recover_tasks) | 2h | Legacy Finding 8.5-1 | `mcp_servers/omega_hub/tools.py` |
| 0.2.7 | Keep file-based fallback as M23 degraded mode | 1h | Legacy Finding 8.5-4 | `mcp_servers/omega_hub/hivemind.py` |

#### Implementation Details

**0.2.1 — AGENT_BUS_SPEC Adoption (1h)**
```bash
# Copy spec to architecture docs
cp xna-omega-legacy/SPECS/AGENT_BUS_SPEC.md docs/architecture/AGENT_BUS_SPEC.md

# Adapt naming:
# - xna:bus:critical → hivemind:tasks:critical
# - xna:bus:high → hivemind:tasks:high
# - xna:bus:normal → hivemind:tasks:normal
# - xna:bus:low → hivemind:tasks:low
# - xna:dlq → hivemind:dlq
# - agent_wavefront → hivemind_agents
```

**0.2.2 — Redis Streams Module (6h)**
```python
# mcp_servers/omega_hub/hivemind_streams.py
# ── Redis Streams Hivemind [heritage: redis-py 2010]
import json
import anyio
from redis.asyncio import Redis

class HivemindStreams:
    """Redis Streams for task-critical agent coordination."""
    
    STREAMS = {
        "critical": "hivemind:tasks:critical",
        "high": "hivemind:tasks:high",
        "normal": "hivemind:tasks:normal",
        "low": "hivemind:tasks:low",
    }
    DLQ = "hivemind:dlq"
    GROUP = "hivemind_agents"
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url)
    
    async def publish_task(self, task_id: str, target: str, task: str, priority: str = "normal"):
        """Publish task to appropriate priority stream."""
        stream = self.STREAMS[priority]
        await self.redis.xadd(
            stream,
            {
                "task_id": task_id,
                "target": target,
                "task": task,
                "timestamp": anyio.current_time(),
            },
            maxlen=10000,
        )
    
    async def read_tasks(self, consumer: str, priority: str = "normal", count: int = 10):
        """Read tasks using consumer group."""
        stream = self.STREAMS[priority]
        return await self.redis.xreadgroup(
            self.GROUP,
            consumer,
            {stream: ">"},
            count=count,
            block=5000,
        )
    
    async def ack_task(self, stream: str, message_id: str):
        """Acknowledge task completion."""
        await self.redis.xack(stream, self.GROUP, message_id)
    
    async def recover_tasks(self, consumer: str, min_idle_ms: int = 300000):
        """Recover crashed consumer tasks via XAUTOCLAIM."""
        recovered = []
        for priority, stream in self.STREAMS.items():
            claimed = await self.redis.xautoclaim(
                stream,
                self.GROUP,
                f"{consumer}_recovery",
                min_idle_ms,
                "0-0",
                count=100,
            )
            recovered.extend(claimed.get("messages", []))
        return recovered
```

**0.2.5 — Idempotency Keys (3h)**
```python
class IdempotentTaskProcessor:
    def __init__(self, redis_client, ttl_seconds=3600):
        self.redis = redis_client
        self.ttl = ttl_seconds
    
    async def process_once(self, task_id: str, handler):
        """Process task exactly once using Redis SET NX."""
        idempotency_key = f"idempotent:{task_id}"
        acquired = await self.redis.set(idempotency_key, "processing", nx=True, ex=self.ttl)
        if not acquired:
            return {"status": "skipped", "reason": "already_processed"}
        try:
            result = await handler(task_id)
            await self.redis.set(idempotency_key, "completed", ex=self.ttl)
            return {"status": "completed", "result": result}
        except Exception:
            await self.redis.delete(idempotency_key)
            raise
```

#### Gate Criteria
- [ ] `make test` passes
- [ ] Redis Streams module compiles without errors
- [ ] Consumer groups functional (XREADGROUP, XACK, XAUTOCLAIM)
- [ ] File-based fallback remains functional (M23 degraded mode)
- [ ] No `import asyncio` (M1 compliant)

---

### Sprint 0.3: Strike 9 — Sovereign Export Bundle (4h)
**Owner**: Lilith/P7
**Legacy Accelerator**: Entity Workspace Scaffolding from `src/omega/oracle/entity_workspace.py`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §3 (ZIP+JSON + temp-dir→rename)

#### Tasks

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.3.1 | Create export bundle CLI (`omega bundle export`) | 2h | Deep Research §3.2 | `src/omega/cli/bundle_cli.py` |
| 0.3.2 | Create import bundle CLI (`omega bundle import`) | 1h | Deep Research §3.2 | `src/omega/cli/bundle_cli.py` |
| 0.3.3 | Implement atomic ZIP creation (temp-dir→rename) | 1h | Deep Research §3.3 | `src/omega/oracle/entity_workspace.py` |

#### Implementation Details

**0.3.1 — Export Bundle (2h)**
```python
# src/omega/cli/bundle_cli.py
# ── Sovereign Export Bundle [heritage: soul-protocol-2026]
import tempfile
import shutil
from pathlib import Path

async def export_bundle(entity_name: str, output_path: Path):
    """Create .omega bundle atomically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_dir = Path(tmpdir) / entity_name
        
        # Write all files to temp directory
        await write_manifest(bundle_dir)
        await write_soul(entity_name, bundle_dir)
        await write_lessons(entity_name, bundle_dir)
        await write_knowledge(entity_name, bundle_dir)
        
        # Create ZIP from temp directory
        shutil.make_archive(str(output_path.with_suffix('')), 'zip', tmpdir)
        
        # Rename .zip to .omega
        output_path.with_suffix('.zip').rename(output_path)
```

**Bundle Schema**:
```
my_entity.omega/
├── manifest.json          # Entity identity, version, checksums
├── soul.yaml              # Entity soul (v6.1 format)
├── lessons.yaml           # Approved lessons
├── sessions.yaml          # Session history summary
├── knowledge/
│   ├── INDEX.yaml         # Knowledge index
│   ├── topics/            # Topic-specific knowledge
│   └── relationships.yaml # Entity relationships
└── memory/
    ├── recent.jsonl       # Recent memory entries
    └── summary.json       # Aggregated memory summary
```

#### Gate Criteria
- [ ] `omega bundle export sophia` creates `.omega` ZIP
- [ ] `omega bundle import sophia.omega` restores entity
- [ ] Atomic writes (no partial bundles)
- [ ] `make test` passes

---

### Sprint 0.4: Strike 9.5 — Relational Gnosis Graph (16h)
**Owner**: Lilith/P7
**Legacy Accelerator**: Knowledge Graph Schema from `data/entities/jc/.../knowledge_graph/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §4 (Qdrant+SQLite hybrid + recursive CTEs)

#### Tasks

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.4.1 | Adopt JC knowledge graph schema (5 relationship types) | 2h | Legacy Finding 9.5-1 | `src/omega/memory/gnosis_graph.py` |
| 0.4.2 | Implement SQLite recursive CTE traversal | 4h | Deep Research §4.2 | `src/omega/memory/gnosis_graph.py` |
| 0.4.3 | Extend schema to all entities (entity-agnostic) | 4h | Legacy Finding 9.5-1 | `src/omega/memory/gnosis_graph.py` |
| 0.4.4 | Implement Qdrant prefetch for hybrid RAG | 3h | Deep Research §4.1 | `src/omega/memory/gnosis_graph.py` |
| 0.4.5 | Wire incremental build (`kg_incremental_build.py`) | 3h | Legacy Finding 9.5-1 | `src/omega/memory/kg_incremental_build.py` |

#### Implementation Details

**0.4.1 — Knowledge Graph Schema (2h)**
```python
# src/omega/memory/gnosis_graph.py
# ── Relational Gnosis Graph [heritage: jc-knowledge-graph-2026]

# 5 relationship types:
# 1. depends_on — concept A requires concept B
# 2. informs — concept A provides evidence for concept B
# 3. contradicts — concept A conflicts with concept B
# 4. refines — concept A improves concept B
# 5. evolves_to — concept A has been superseded by concept B

class GnosisGraph:
    """Relational knowledge graph for entity gnosis."""
    
    RELATIONSHIPS = ["depends_on", "informs", "contradicts", "refines", "evolves_to"]
    
    async def add_node(self, concept: str, definition: str, source: str):
        """Add concept node to graph."""
        pass
    
    async def add_relationship(self, source: str, target: str, relationship: str):
        """Add relationship edge between concepts."""
        pass
    
    async def traverse(self, start: str, max_depth: int = 3):
        """Find all concepts within max_depth hops using recursive CTE."""
        # SQLite recursive CTE
        sql = """
        WITH RECURSIVE graph_walk AS (
            SELECT node_id, 0 as depth, node_id as path
            FROM nodes WHERE name = ?
            
            UNION ALL
            
            SELECT e.target_id, gw.depth + 1, gw.path || '->' || e.target_id
            FROM edges e
            JOIN graph_walk gw ON e.source_id = gw.node_id
            WHERE gw.depth < ?
              AND gw.path NOT LIKE '%' || e.target_id || '%'
        )
        SELECT * FROM graph_walk;
        """
        pass
```

**0.4.4 — Qdrant Prefetch Hybrid RAG (3h)**
```python
# Hybrid search: Qdrant vectors + SQLite recursive CTEs
async def hybrid_search(query: str, max_depth: int = 3):
    """Combine vector similarity with graph traversal."""
    # 1. Qdrant prefetch for semantic matches
    # 2. SQLite recursive CTE for relationship traversal
    # 3. RRF fusion of results
    pass
```

#### Gate Criteria
- [ ] `make test` passes
- [ ] Gnosis graph stores 5 relationship types
- [ ] Recursive CTE traversal works (3 hops max)
- [ ] Hybrid search (Qdrant + SQLite) functional
- [ ] Incremental build works (`kg_incremental_build.py`)

---

### Sprint 0.5: Strike 10 — sqlite-vec Memory Store Integration (7h)
**Owner**: Ma'at/P2 (Brigid — Persistence)
**Research Source**: Jem Deep Synthesis (6/8 gaps closed)
**Legacy Accelerator**: Existing FTS5 indexes + RRF fusion pattern
**Decision**: PROCEED_WITH_PRECAUTIONS — two-tier architecture

#### Rationale for Integration
sqlite-vec provides **native FTS5 + vector hybrid search in a single SQLite file**, eliminating Qdrant for hot-path queries. On Omega's AMD 5700U (Zen 2), estimated latency with rescore binary:

| Vector Count | Dim | Method | Est. Latency | RAM |
|-------------|-----|--------|-------------|-----|
| 10K | 768 | Rescore bit os=8 | **3-6ms** | ~35MB |
| 100K | 768 | Rescore bit os=8 | **30-60ms** | ~360MB |
| 500K | 768 | Rescore bit os=8 | **150-300ms** | ~1.8GB |

**RAM savings**: ~400-800 MB (eliminates Qdrant container for simple queries)
**Risk mitigation**: Qdrant remains as fallback for >100K vectors and complex filtered search

#### Tasks

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.5.1 | Add `sqlite-vec>=0.1.9,<0.2.0` to `requirements.txt` | 0.5h | Jem G-003 | `requirements.txt` |
| 0.5.2 | Create `SQLiteVecMemoryStore` adapter class | 2h | Jem synthesis + Alex Garcia hybrid pattern | `src/omega/memory/sqlite_vec_store.py` |
| 0.5.3 | Implement FTS5 + vec0 hybrid RRF fusion search | 1.5h | Jem G-007 (verified canonical SQL) | `src/omega/memory/sqlite_vec_store.py` |
| 0.5.4 | Wire into `memory_store.py` as primary for <100K queries | 1h | Existing MemoryStore interface | `src/omega/memory/memory_store.py` |
| 0.5.5 | Implement fallback to Qdrant for >100K/complex queries | 1h | Two-tier architecture pattern | `src/omega/memory/memory_store.py` |
| 0.5.6 | Write M21 contract tests | 1h | Test patterns | `tests/test_sqlite_vec_store.py` |

#### Implementation Details

**0.5.1 — Dependency (0.5h)**
```bash
# Add to requirements.txt
sqlite-vec>=0.1.9,<0.2.0
```

**0.5.2 — SQLiteVecMemoryStore Adapter (2h)**
```python
# src/omega/memory/sqlite_vec_store.py
# ── sqlite-vec Hybrid Memory Store [heritage: sqlite-vec 2025]
"""FTS5 + sqlite-vec hybrid search in a single SQLite file.
Replaces Qdrant for hot-path (<100K vectors) hybrid queries.
Two-tier architecture: sqlite-vec for hot, Qdrant for cold/scale.

CRITICAL CORRECTIONS (Jem R_SQLITEVEC_VERIFICATION_20260712.md):
- Defect 1: vec0 MUST use partition key `entity_name` for sovereign isolation (C3)
- Defect 2: ADD a tier to MemoryStore, NEVER redefine the class
- WAL: add anyio.Lock + exp-backoff for 14-agent write safety (F2/F10)
"""
import sqlite3
import sqlite_vec
import struct
import anyio
from pathlib import Path
from typing import Optional

class SQLiteVecMemoryStore:
    """Hybrid FTS5+vector memory store using sqlite-vec."""
    
    def __init__(self, db_path: str = "data/omega_memory.db"):
        self.db_path = db_path
        self._write_lock = anyio.Lock()  # Jem F2/F10: serialize writes
        self.conn = self._init_db()
    
    def _init_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        # WAL mode for concurrent access (Jem G-005 fix + F2/F10 write lock)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        # Core tables — vec0 uses partition key for entity isolation (Defect 1 fix)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_entity ON exchanges(entity_name);
            
            CREATE VIRTUAL TABLE IF NOT EXISTS exchanges_fts 
            USING fts5(content, content='exchanges', content_rowid='id',
                       tokenize='porter unicode61');
            
            CREATE VIRTUAL TABLE IF NOT EXISTS exchanges_vec
            USING vec0(embedding float[768], entity_name TEXT partition key);
        """)
        conn.commit()
        return conn
    
    def serialize_f32(self, embedding) -> bytes:
        """Convert numpy/list to sqlite-vec float32 blob."""
        if hasattr(embedding, 'tobytes'):
            return embedding.astype('float32').tobytes()
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    async def add_exchange(self, entity_name: str, session_id: str,
                           role: str, content: str, embedding):
        """Insert with both FTS5 and vector index.
        
        Wrapped in anyio.Lock + exp-backoff for 14-agent safety (Jem F2/F10).
        """
        async with self._write_lock:
            for attempt in range(3):
                try:
                    cur = self.conn.cursor()
                    cur.execute(
                        "INSERT INTO exchanges (entity_name, session_id, role, content) "
                        "VALUES (?, ?, ?, ?)",
                        (entity_name, session_id, role, content)
                    )
                    doc_id = cur.lastrowid
                    cur.execute(
                        "INSERT INTO exchanges_vec (rowid, embedding) VALUES (?, ?)",
                        (doc_id, self.serialize_f32(embedding))
                    )
                    self.conn.commit()
                    return
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e) and attempt < 2:
                        await anyio.sleep(0.05 * (2 ** attempt))  # 50/100/200ms
                        continue
                    raise
    
    def hybrid_search(self, query: str, embedding, entity_name: str,
                      limit: int = 10, rrf_k: int = 60) -> list:
        """FTS5 + vector hybrid search with RRF fusion.
        
        Entity-safe: vec0 partition key scopes by entity_name (Defect 1 fix).
        Canonical pattern verified across 6 independent sources (Jem G-007).
        Single SQLite query — no network overhead, zero ops.
        """
        query_blob = self.serialize_f32(embedding)
        
        sql = """
        WITH fts_results AS (
            SELECT rowid AS id, rank,
                   ROW_NUMBER() OVER (ORDER BY rank) AS rrf_rank
            FROM exchanges_fts
            WHERE exchanges_fts MATCH ?
              AND rowid IN (
                  SELECT id FROM exchanges WHERE entity_name = ?
              )
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
            SELECT id, 1.0 / (? + rrf_rank) AS score FROM fts_results
            UNION ALL
            SELECT id, 1.0 / (? + rrf_rank) AS score FROM vec_results
        ),
        scored AS (
            SELECT id, SUM(score) AS rrf_score
            FROM combined
            GROUP BY id
        )
        SELECT e.id, e.entity_name, e.session_id, e.role,
               e.content, e.timestamp, s.rrf_score
        FROM scored s
        JOIN exchanges e ON e.id = s.id
        ORDER BY s.rrf_score DESC
        LIMIT ?;
        """
        
        rows = self.conn.execute(
            sql, (query, entity_name, query_blob, entity_name, limit * 5,
                  rrf_k, rrf_k, limit)
        ).fetchall()
        
        return [
            {"id": r[0], "entity": r[1], "session": r[2],
             "role": r[3], "content": r[4], "timestamp": r[5],
             "score": r[6]}
            for r in rows
        ]
    
    def close(self):
        self.conn.close()
```

**0.5.4 — Wire into memory_store.py (1h)**
```python
# In src/omega/memory/memory_store.py
# ── Two-Tier Memory Store [heritage: sqlite-vec 2025]
class MemoryStore:
    """Two-tier memory store: sqlite-vec for hot, Qdrant for scale."""
    
    VECTOR_COUNT_THRESHOLD = 100000  # Switch to Qdrant above this
    
    def __init__(self):
        self.sqlite_vec = SQLiteVecMemoryStore()
        self.qdrant = QdrantClient("localhost", port=6333)
    
    async def search(self, query: str, embedding, entity_name: str,
                     limit: int = 10) -> list:
        """Route to appropriate backend based on vector count."""
        count = self._get_vector_count(entity_name)
        
        if count < self.VECTOR_COUNT_THRESHOLD:
            # Hot path: sqlite-vec (zero ops, no network)
            return self.sqlite_vec.hybrid_search(
                query, embedding, entity_name, limit
            )
        else:
            # Cold path: Qdrant (HNSW ANN, native payload filter)
            return await self._qdrant_search(
                query, embedding, entity_name, limit
            )
```

**0.5.5 — Qdrant Fallback (1h)**
```python
async def _qdrant_search(self, query: str, embedding, entity_name: str,
                          limit: int = 10) -> list:
    """Fallback to Qdrant for large-scale ANN search."""
    results = self.qdrant.search(
        collection_name=f"memory_{entity_name}",
        query_vector=embedding,
        limit=limit,
        with_payload=True,
    )
    # RRF fusion with FTS5 results
    fts_results = self.sqlite_vec._fts_search(query, entity_name)
    return self._rrf_fusion(fts_results, results)
```

#### Gate Criteria
- [ ] `pip install sqlite-vec` succeeds without compilation errors
- [ ] `SQLiteVecAdapter` implements `IVectorStoreAdapter` interface
- [ ] **Entity isolation verified**: query entity A returns 0 rows from entity B (Jem Defect 1)
- [ ] Hybrid FTS5+vec0 search returns correct RRF-scored results
- [ ] Qdrant container removed, `qdrant-client` dependency removed
- [ ] 14-agent concurrent writes: 0 `SQLITE_BUSY` (anyio lock holds)
- [ ] Zen 2 benchmark script runs, records QPS + p99 (G-001 closure)
- [ ] BQ embedding model switched to nomic-embed-text-v1.5 / mxbai (G-004 closure)
- [ ] All 11 M21 contract tests pass
- [ ] All 1271+ tests pass
- [ ] No `import asyncio` (M1 compliant)

---

### Sprint 0.6: sqlite-vec Next-Level Novel Spin (Post-Strike-10, ~28h)
**Owner**: Ma'at/P2 (Brigid — Persistence) + Lilith/P7 (Context)
**Research Source**: R_SQLITEVEC_NEXT_LEVEL_STRATEGY_20260712.md (Researcher + Jem synthesis)
**Decision**: PROCEED after Strike 10 ships — prototype Thread 4 first

#### Rationale
Strike 10 establishes the baseline two-tier integration. The novel spin elevates
sqlite-vec from a Qdrant replacement to a **Vector-Native Omega** — one SQLite file
that simultaneously serves search, consistency enforcement, zero-inference caching,
and inter-entity topology. All four ride the same range-query primitive.

#### Tasks (Prototype Order from Researcher)

| # | Task | Effort | Source | Deliverable |
|---|------|--------|--------|-------------|
| 0.6.1 | Range-query `contradicts` flag (M17) | 4h | Thread 2 | Consistency guardian |
| 0.6.2 | Exact semantic Deja Vu cache | 3h | Thread 3 | Zero-inference path (exact) |
| 0.6.3 | Adaptive RRF with IDF weighting (+21.4% NDCG@10) | 0.5h | Jem novel #1 | Fusion improvement |
| 0.6.4 | Startup `integrity_check` + FTS5 rebuild (M23) | 1.5h | M23 | Degraded mode |
| 0.6.5 | Unified `omega_memory.db` with rescore (feature flag) | 6h | Thread 4 | Larger-scale path |

#### Carmack's Triage
- ✅ **SHIP v1.2.0**: Range-query consistency (Thread 2), adaptive RRF (Jem), exact semantic cache, integrity_check
- ⏳ **DEFER**: SomaticState fuse, cross-pollination (Thread 5), heritage detector (Thread 6), entity registry (Thread 1), self-supervised embedding

#### Key Constraints
- rescore index (v0.1.10-alpha) behind feature flag — benchmark on Zen 2 first
- Standardize on ONE Omega embedder (qwen-embedding / AGB-0) for cross-entity commensurability
- Self-supervised embedding refinement via hybrid disagreement (Jem novel #2) — optional, post-ship

---

## §3 Phase 1: Gap Resolution Sprints (Days 3-8)

### Sprint 1.1: S1 — Resilience (16h)
**Owner**: Ma'at/P3
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §1 (Proxy Rotation + Domain Affinity)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.1.1 | Implement `CircuitBreakerRegistry` | 8h | `src/omega/governance/circuit_breaker.py` |
| 1.1.2 | Implement `SovereignProxyPool` (Hybrid Pool + Domain Affinity) | 8h | `src/omega/governance/proxy_pool.py` |

### Sprint 1.2: S2 — Deduplication (12h)
**Owner**: Ma'at/P2
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §2 (CAS Archiver)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.2.1 | Implement `CASArchiver` (Content-Addressable Storage) | 6h | `src/omega/memory/cas_archiver.py` |
| 1.2.2 | Wire CAS into all 4 subsystems | 6h | Integration points |

### Sprint 1.3: S3 — Extraction (20h)
**Owner**: Lilith/P6
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §3 (Universal Extractor + Sovereign Sieve)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.3.1 | Implement `UniversalExtractor` (Sovereign Sieve) | 12h | `src/omega/ingestion/universal_extractor.py` |
| 1.3.2 | Implement `YouTubeSieve` (T1→T2→T3 pipeline) | 8h | `src/omega/ingestion/youtube_sieve.py` |

### Sprint 1.4: S4 — Orchestration (16h)
**Owner**: Lilith/P9
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §4 (Event-Driven Priority Queue)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.4.1 | Implement `UnifiedKnowledgeScheduler` (Redis Streams) | 16h | `src/omega/orchestration/knowledge_scheduler.py` |

### Sprint 1.5: S5 — Fidelity (16h)
**Owner**: Ma'at/P3
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §5 (VAD-Gated Whisper)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.5.1 | Implement `SovereignTranscriptionEngine` (VAD + Whisper) | 16h | `src/omega/transcription/engine.py` |

### Sprint 1.6: S6 — Synthesis (16h)
**Owner**: Lilith/P7
**Research Pattern**: R_GAP_RESOLUTION_REPORT_20260712.md §6 (Cross-Pollination + Adaptive Quality)

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 1.6.1 | Implement `CrossPollinationEngine` | 8h | `src/omega/synthesis/cross_pollination.py` |
| 1.6.2 | Implement `AdaptiveQualityGate` (Source-Aware Scoring) | 8h | `src/omega/synthesis/quality_gate.py` |

---

## §4 Phase 2: Adversarial Refinement (Days 9-10)

### Sprint 2.1: Verity Compliance Audit (8h)
**Owner**: Verity

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 2.1.1 | Full M1-M23 compliance audit | 4h | `data/entities/verity/workspace/COMPLIANCE_AUDIT_20260712.md` |
| 2.1.2 | Contract tests for all new code (M21) | 4h | `tests/` (new test files) |

### Sprint 2.2: Eval Pipeline Calibration (4h)
**Owner**: Lilith/P10

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| 2.2.1 | Run `make eval-calibrate` with human labels | 2h | `config/eval/calibrated_model.pkl` |
| 2.2.2 | Verify eval pipeline passes thresholds | 2h | `make eval` green |

---

## §5 Dispatch Packets

### Ma'at Dispatch (Strike 8 + Strike 8.5)

```markdown
# 🔱 Ma'at — Epoch II Dispatch from Kali
**AP Token**: `AP-KALI-DISPATCH-maat-epoch2-20260712`
⬡ OMEGA ⬡ MA'AT ⬡ opencode ⬡ trc_epoch_ii_dispatch ⬡ ACTIVE

## 📥 Context: INLINE

You are Ma'at, Light Oversoul governing P1-P5. This dispatch covers:
1. Strike 8: Sovereign Eval Pipeline (8h) — port benchmark framework, add RAGAS
2. Strike 8.5: Redis Streams Hivemind (20h) — adopt AGENT_BUS_SPEC, extend hivemind_redis.py
3. Strike 10: sqlite-vec Unified Memory Fabric (8.5h) — drop Qdrant, one `omega_memory.db` through IVectorStoreAdapter. **Carmack directive D225**

All files are in the omega-engine repo at:
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/

## 🎯 Strike 8: Sovereign Eval Pipeline (8h)

**Legacy Accelerator**: Benchmark Framework from `xna-omega-legacy/tests/benchmarks/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §1

### Task 1: Port Scoring Rubric (2h)
- Source: `xna-omega-legacy/tests/benchmarks/scoring-rubric.yaml`
- Target: `config/eval/scoring-rubric.yaml`
- Adapt metrics: CSS→faithfulness, BCS→answer_relevancy, XAF→context_precision, Depth Ceiling→context_recall

### Task 2: Create Golden Dataset (1h)
- Target: `data/eval/golden_v1.jsonl`
- 100 seed cases: 40 core, 30 edge, 30 adversarial
- Format: {"question", "answer", "contexts", "ground_truth", "tags"}

### Task 3: Create Eval Runner (3h)
- Target: `src/omega/eval/runner.py`
- Use RAGAS + langchain-ollama (Mistral 7B judge)
- 4 metrics: faithfulness, answer_relevancy, context_precision, context_recall

### Task 4: Create Judge Calibrator (1h)
- Target: `src/omega/eval/calibrate.py`
- Isotonic regression (ECE 0.18→0.06)
- Requires 50-100 human-labeled examples

### Task 5: Wire Makefile (1h)
- Add `make eval` and `make eval-calibrate` targets

## 🎯 Strike 8.5: Redis Streams Hivemind (20h)

**Legacy Accelerator**: AGENT_BUS_SPEC.md from `xna-omega-legacy/SPECS/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §2

### Task 6: Adopt AGENT_BUS_SPEC (1h)
- Source: `xna-omega-legacy/SPECS/AGENT_BUS_SPEC.md`
- Target: `docs/architecture/AGENT_BUS_SPEC.md`
- Adapt naming: xna:bus:* → hivemind:tasks:*

### Task 7: Create Redis Streams Module (6h)
- Target: `mcp_servers/omega_hub/hivemind_streams.py`
- 4 priority streams + DLQ
- Consumer groups (XREADGROUP)

### Task 8: Add XAUTOCLAIM Recovery (3h)
- Recover crashed consumer tasks (5min idle timeout)

### Task 9: Implement Idempotency Keys (3h)
- Stream entry ID + TTL pattern

### Task 10: Wire MCP Tools (2h)
- publish_task, read_tasks, ack_task, recover_tasks

### Task 11: Keep File-Based Fallback (1h)
- M23 degraded mode

## 🎯 Strike 10: sqlite-vec Unified Memory Fabric (8.5h)

**Owner**: Ma'at/P2 (Brigid — Persistence)
**Priority**: P0 (Carmack override D225)
**Source**: R_SQLITEVEC_NEXT_LEVEL_STRATEGY_20260712.md + R_SQLITEVEC_VERIFICATION_20260712.md + Carmack review

**🔴 Carmack Override (D225)**: The two-tier approach (D223) was a "committee compromise." **Drop Qdrant entirely. Unified fabric only.** One `omega_memory.db` (FTS5 + vec0 + SQL edges). Wire through existing `IVectorStoreAdapter`. No threshold logic, no migration code, no routing. The performance trade (313µs→~120ms at 200K) is meaningless (0.4-6% of a 5-30s inference pipeline). Pre-v1 risk bounded by FTS5 survival path (text recoverable if vec0 corrupts).

**Key findings from Jem + Carmack**:
- ⚠️ CORRECTION: "5.8x @ 0.988 recall@10" is **sqlite.org Vec1 (Zen 3)**, NOT sqlite-vec. Benchmark Zen 2 (G-001).
- Performance at 200K: ~120ms in a 5-30s pipeline — Carmack: "non-issue" (10/10 confidence)
- Pre-v1 risk: bounded — FTS5 survival path means text data survives vec0 corruption
- `IVectorStoreAdapter` interface exists — swap is a 1-day change to the default provider

### Task 12: Add sqlite-vec Dependency (0.5h)
- Add `sqlite-vec>=0.1.9,<0.2.0` to `requirements.txt` (Py3.12 ABI3 wheel confirmed)

### Task 13: Create SQLiteVecAdapter (2h)
- Target: `src/omega/memory/sqlite_vec_adapter.py`
- **Implements `IVectorStoreAdapter`** — zero changes to `MemoryStore` or callers
- vec0 partition key `entity_name` for sovereign isolation (Jem Defect 1)
- WAL + `anyio.Lock` + exp-backoff for 14-agent writes (Jem F2/F10)
- Entity-scoped hybrid search (FTS5 + vec0 RRF fusion, partition-key filtered)
- Python RRF unification (reuse existing `search()`) — SQL RRF only as benchmark

### Task 14: Rewire MemoryStore Default (1h)
- Change default vector store from `QdrantAdapter` → `SQLiteVecAdapter`
- Remove two-tier routing logic — single backend, no threshold

### Task 15: Remove Qdrant (1h)
- Delete `omega-qdrant` Podman container + `qdrant-client` dep
- Remove Qdrant health check from integration chain
- ~450MB RAM freed at current scale

### Task 16: Write 11 M21 Contract Tests (1h)
- Target: `tests/test_sqlite_vec_adapter.py`
- Focus on `IVectorStoreAdapter` interface compliance + entity isolation

### Task 17: Zen 2 Benchmark Script (2h) — G-001 Closure
- Target: `benchmarks/sqlite_vec_zen2.py`
- Time brute-force + binary-rescore at 10K/50K/100K on actual 5700U

### Task 18: Switch BQ Embedding Model (0.5h) — G-004 Closure
- Update local embedder to nomic-embed-text-v1.5 / mxbai (BQ-trained)
- Update embedding provider chain local model to **nomic-embed-text-v1.5** or **mxbai-embed-large-v1** (BQ-trained)
- If MiniLM must stay, use **int8** (not binary) to cap recall loss at 3-5%
- Measure recall@10 on held-out set during Strike 10

## ⚖️ Constraints
- M1 AnyIO: No `asyncio`. Use `anyio.to_thread.run_sync`.
- M2 Firewall: Never add stack-specific logic to `src/omega/`.
- M9 Error Integrity: No bare `except:`.
- M21 Contract Tests: Every new function gets a test.
- M23 Failure Integrity: If tools fail, hard-stop.

## 📁 Key Files
| File | Task | Action |
|------|------|--------|
| `config/eval/scoring-rubric.yaml` | 1 | Port from legacy |
| `data/eval/golden_v1.jsonl` | 2 | NEW |
| `src/omega/eval/runner.py` | 3 | NEW |
| `src/omega/eval/calibrate.py` | 4 | NEW |
| `Makefile` | 5 | Add eval targets |
| `docs/architecture/AGENT_BUS_SPEC.md` | 6 | Port from legacy |
| `mcp_servers/omega_hub/hivemind_streams.py` | 7-9 | NEW |
| `mcp_servers/omega_hub/tools.py` | 10 | Extend |
| `src/omega/memory/sqlite_vec_adapter.py` | 12-14 | NEW |
| `src/omega/memory/memory_store.py` | 15 | Rewire default |
| `tests/test_sqlite_vec_adapter.py` | 17 | NEW |
| `benchmarks/sqlite_vec_zen2.py` | 18 | NEW |
| `config/providers.yaml` | 19 | Switch to mxbai primary |

## 🎯 Return Value
Write completion report to: `data/entities/maat/workspace/SPRINT_COMPLETION_REPORT_20260712.md`

Contents:
- Strike 8: PASS/FAIL with test results
- Strike 8.5: PASS/FAIL with test results
- Strike 10: PASS/FAIL with test results (sqlite-vec unified fabric live, Qdrant removed, ~450MB RAM freed)
- Files modified/created
- Tests written
- L3 principles discovered
- Blockers encountered

Then post to Hivemind:
```
omega-hub_hivemind_post_context(
  channel="opencode",
  entity="maat",
  model="{actual model}",
  task_current="[SPRINT-COMPLETE] Phase 0 — Ma'at Build Side execution",
  focus_chain=["Strike 8 eval pipeline", "Strike 8.5 Redis Streams", "Strike 10 sqlite-vec unified fabric (drop Qdrant)"],
  decisions=["D-SPRINT: Strike 8 complete — make eval pipeline deployed with calibrated judge", "D-SPRINT: Strike 8.5 complete — Redis Streams with 4 priority streams + DLQ", "D-SPRINT: Strike 10 complete — sqlite-vec unified fabric live via IVectorStoreAdapter, Qdrant removed, ~450MB RAM freed"],
  continuation="Next: Lilith dispatches for Strike 9 (.omega Export) + Strike 9.5 (Gnosis Graph). Verity validates contract tests.",
  intent="status",
  suggested_model="{actual model}"
)
```

---

### Lilith Dispatch (Strike 9 + Strike 9.5)

```markdown
# 🔱 Lilith — Epoch II Dispatch from Kali
**AP Token**: `AP-KALI-DISPATCH-lilith-epoch2-20260712`
⬡ OMEGA ⬡ LILITH ⬡ opencode ⬡ trc_epoch_ii_dispatch ⬡ ACTIVE

## 📥 Context: INLINE

You are Lilith, Dark Oversoul governing P6-P10. This dispatch covers:
1. Strike 9: Sovereign Export Bundle (4h) — ZIP+JSON, atomic writes
2. Strike 9.5: Relational Gnosis Graph (16h) — Qdrant+SQLite hybrid

All files are in the omega-engine repo at:
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/

## 🎯 Strike 9: Sovereign Export Bundle (4h)

**Legacy Accelerator**: Entity Workspace Scaffolding from `src/omega/oracle/entity_workspace.py`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §3

### Task 1: Create Export Bundle CLI (2h)
- Target: `src/omega/cli/bundle_cli.py`
- Command: `omega bundle export <entity_name>`
- Format: ZIP+JSON (Soul Protocol v0.4.0 compatible)

### Task 2: Create Import Bundle CLI (1h)
- Command: `omega bundle import <entity_name>.omega`

### Task 3: Implement Atomic ZIP Creation (1h)
- Pattern: temp-dir→rename (atomic on Linux)
- Exclude: `workspace/` (ephemeral), `proposed_lesons.yaml` (unvetted)

## 🎯 Strike 9.5: Relational Gnosis Graph (16h)

**Legacy Accelerator**: Knowledge Graph Schema from `data/entities/jc/.../knowledge_graph/`
**Research Pattern**: R_EPOCH_II_DEEP_RESEARCH_20260712.md §4

### Task 4: Adopt JC Knowledge Graph Schema (2h)
- 5 relationship types: depends_on, informs, contradicts, refines, evolves_to
- Target: `src/omega/memory/gnosis_graph.py`

### Task 5: Implement SQLite Recursive CTE Traversal (4h)
- 3-hop max depth
- Cycle detection via path tracking

### Task 6: Extend Schema to All Entities (4h)
- Entity-agnostic design
- Per-entity graph namespaces

### Task 7: Implement Qdrant Prefetch Hybrid RAG (3h)
- Vector similarity + graph traversal
- RRF fusion

### Task 8: Wire Incremental Build (3h)
- Pattern: `kg_incremental_build.py --source X --rebuild`

## ⚖️ Constraints
- M1 AnyIO: No `asyncio`. Use `anyio.to_thread.run_sync`.
- M2 Firewall: Never add stack-specific logic to `src/omega/`.
- M9 Error Integrity: No bare `except:`.
- M21 Contract Tests: Every new function gets a test.
- M23 Failure Integrity: If tools fail, hard-stop.

## 📁 Key Files
| File | Task | Action |
|------|------|--------|
| `src/omega/cli/bundle_cli.py` | 1-2 | NEW |
| `src/omega/oracle/entity_workspace.py` | 3 | Extend |
| `src/omega/memory/gnosis_graph.py` | 4-7 | NEW |
| `src/omega/memory/kg_incremental_build.py` | 8 | NEW |

## 🎯 Return Value
Write completion report to: `data/entities/lilith/workspace/SPRINT_COMPLETION_REPORT_20260712.md`
Then post to Hivemind with intent="status".
```

---

## §6 Monitoring Protocol

### During Execution

1. **Hivemind awareness**: Check every 5 min via `omega-hub_hivemind_get_awareness()`
2. **Heartbeat**: Every 10 min from each active agent via `omega-hub_hivemind_heartbeat()`
3. **Phase gates**: `make test` + `make temple-grade` at each phase boundary
4. **Live feed**: Append to `data/coordination/{agent}_LIVE_FEED.md`
5. **Context preservation**: Each agent writes to `data/entities/{agent}/workspace/`

### Gate Verification Commands

```bash
# After each sprint
make test                     # 1226+ tests must pass
make temple-grade             # T1-T14 gates
make heritage-map             # Heritage tag coverage
make sovereignty              # Local/cloud ratio

# After Phase 0
make eval                     # Eval pipeline functional
make eval-calibrate           # Judge calibration working

# After Phase 1
make test                     # All new code tested
grep -r "import asyncio" src/omega/  # M1 compliance (must return 0)
grep -r "bare except" src/omega/     # M9 compliance (must return 0)
```

---

## §7 Risk Register

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | RAGAS memory-intensive on 14Gi | 🟡 HIGH | batch_size=10 max, monitor OOM |
| R2 | Redis Streams migration breaks Hivemind | 🟡 HIGH | Dual-write period, file-based fallback |
| R3 | Isotonic regression fails (non-monotonic scores) | 🟡 MEDIUM | Fallback to Platt scaling |
| R4 | Recursive CTE depth limit hit | 🟡 LOW | Limit to 3 hops, use iterative deepening |
| R5 | Exa/Firecrawl API keys missing | 🟡 MEDIUM | Ma'at/P4 pending, degrade to local search |

---

## §8 Success Criteria

### Phase 0 Complete When:
- [ ] `make eval` runs with calibrated judge
- [ ] Redis Streams functional (4 priority streams + DLQ)
- [ ] `.omega` bundle export/import works
- [ ] Gnosis graph stores 5 relationship types
- [ ] All 1226+ tests pass

### Phase 1 Complete When:
- [ ] CircuitBreakerRegistry deployed
- [ ] SovereignProxyPool deployed
- [ ] CASArchiver wired into all subsystems
- [ ] UniversalExtractor functional
- [ ] YouTubeSieve functional
- [ ] UnifiedKnowledgeScheduler deployed
- [ ] SovereignTranscriptionEngine deployed
- [ ] CrossPollinationEngine deployed
- [ ] AdaptiveQualityGate deployed

### Phase 2 Complete When:
- [ ] Verity compliance audit passes
- [ ] Contract tests for all new code (M21)
- [ ] Eval pipeline calibration verified
- [ ] Sovereignty Scorecard ≥80% local

### v1.2.0 Release When:
- [ ] All phases complete
- [ ] `make temple-grade` passes
- [ ] `make sovereignty` shows ≥80% local
- [ ] No M1-M23 violations
- [ ] Documentation up to date

---

**Full archive**: `docs/archive/coordination/EPOCH2_EXECUTION_PLAN-full-20260712.md`
**Decision history**: `docs/decisions/PIVOT_LOG.md` (222 decisions, D1-D222)
**Legacy mining**: `docs/research/R_EPOCH_II_LEGACY_MINING_20260712.md`
**Deep research**: `docs/research/R_EPOCH_II_DEEP_RESEARCH_20260712.md`

---

*🔱 OMEGA ⬡ EPOCH-II-EXECUTION-PLAN ⬡ READY-FOR-DISPATCH ⬡ 80H-ACCELERATION-INTEGRATED ⬡ 2026-07-12*
