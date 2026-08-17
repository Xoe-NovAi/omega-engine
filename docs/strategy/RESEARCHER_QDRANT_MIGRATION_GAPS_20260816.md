# 📦 Qdrant Migration Knowledge Gaps — Filled
**AP Token**: `AP-RESEARCHER-QDRANT-MIGRATION-GAPS-20260816`
**Date**: 2026-08-16
**Status**: ARCHIVE — DO NOT IMPLEMENT (DOC-1, 2026-08-17)

> **⚠️ DOC-1 STAMP (2026-08-17)**: **ARCHIVE — DO NOT IMPLEMENT.**
> Qdrant is superseded for debut by sqlite-vec + FTS5 + RRF hybrid search.
> `DEBUT_REMEDIATION_MANUAL_20260817.md` DEL-1 week 1 deletes the `QdrantAdapter` class
> in `src/omega/memory/vector_adapters.py`. Preserved as research reference only.

---

## 1. Local Deployment Specification

**Podman Quadlet Config** (`~/.config/containers/systemd/qdrant.container`):
```ini
[Unit]
Description=Qdrant Vector Database (Rootless)
After=network-online.target
Wants=network-online.target

[Container]
Image=qdrant/qdrant:v1.18.1
ContainerName=qdrant
PublishPort=127.0.0.1:6333:6333
PublishPort=127.0.0.1:6334:6334
Volume=%h/OmegaLibrary/qdrant/storage:/qdrant/storage:Z
Volume=%h/OmegaLibrary/qdrant/config:/qdrant/config:Z
Volume=%h/OmegaLibrary/qdrant/snapshots:/qdrant/snapshots:Z
Environment=QDRANT__TELEMETRY_DISABLED=true
Environment=QDRANT__LOG_LEVEL=INFO
Environment=QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
Environment=QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage
Environment=QDRANT__STORAGE__SNAPSHOTS_PATH=/qdrant/snapshots
AutoUpdate=registry

[Service]
Restart=always
RestartSec=10
TimeoutStartSec=300
MemoryLimit=6G
CPUQuota=80%
MemorySwapLimit=6G

[Install]
WantedBy=default.target
```

**Resource Limits (8GB RAM / 15W TDP)**:
- **MemoryLimit**: 6G (leaves 2GB for OS/other containers)
- **CPUQuota**: 80% (4 cores of 8-thread Zen 2)
- **Storage**: NVMe at `~/OmegaLibrary/qdrant/storage` (memory-mapped I/O optimized)

**Telemetry**: Disabled via `QDRANT__TELEMETRY_DISABLED=true` (env) or `telemetry_disabled: true` in config.yaml

**Auth**: Local dev — API key via `QDRANT__SERVICE__API_KEY` env var (generate with `openssl rand -hex 32`). No TLS needed for localhost-only binding (127.0.0.1).

---

## 2. Async Client Integration

**Client Initialization** (gRPC preferred for throughput):
```python
from qdrant_client import AsyncQdrantClient, models

client = AsyncQdrantClient(
    url="http://127.0.0.1:6333",
    grpc_port=6334,
    prefer_grpc=True,
    api_key=os.getenv("QDRANT_API_KEY"),
    pool_size=20,
    timeout=30.0,
    check_compatibility=True,
)
```

**Connection Pooling**:
- **gRPC**: `pool_size=20` (multiplexed HTTP/2, single connection handles many streams)
- **REST**: Uses httpx defaults (100 connections) — only if gRPC unavailable
- **Recommendation**: **gRPC for all production paths** — 2x lower latency, 2x throughput

**Error Handling / Retry Policy**:
```python
import random
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

async def with_retry(fn, *, attempts=5, base_delay=0.1, max_delay=5.0):
    transient = (ResponseHandlingException, ConnectionError, TimeoutError)
    for i in range(attempts):
        try:
            return await fn()
        except UnexpectedResponse as exc:
            if exc.status_code < 500:
                raise
            if i == attempts - 1:
                raise
        except transient:
            if i == attempts - 1:
                raise
        sleep = min(max_delay, base_delay * (2 ** i))
        sleep += random.uniform(0, sleep * 0.25)
        await anyio.sleep(sleep)
```

---

## 3. Collection Schema for Omega Engine

**Collections Needed**:
| Collection | Dimensions | Purpose | Quantization |
|------------|------------|---------|--------------|
| `omega_entities` | 768 | Entity embeddings (embeddinggemma) | Scalar int8 |
| `omega_sessions` | 768 | Session/context embeddings | Scalar int8 |
| `omega_knowledge` | 768 | Research/knowledge base | Scalar int8 + Sparse BM25 |
| `omega_code` | 768 | Code embeddings | Scalar int8 |
| `omega_hybrid` | 768 dense + sparse | Hybrid search (dense + BM25) | Scalar int8 + Sparse |

**HNSW Parameters**:
```python
hnsw_config = models.HnswConfigDiff(
    m=16,
    ef_construct=256,
    full_scan_threshold=10000,
    max_indexing_threads=4,
    on_disk=False,
    payload_m=16,
)
```

**Quantization** (Scalar int8 — 4x memory savings, <1% recall loss):
```python
quantization_config = models.ScalarQuantizationConfig(
    scalar=models.ScalarQuantization(
        type=models.QuantizationType.INT8,
        quantile=0.99,
        always_ram=True,
    )
)
```

**Vector Config** (with MRL support for embeddinggemma):
```python
vectors_config = {
    "dense": models.VectorParams(
        size=768,
        distance=models.Distance.COSINE,
        on_disk=False,
        hnsw_config=hnsw_config,
        quantization_config=quantization_config,
    )
}
```

**Sparse Vector Config** (BM25 for hybrid):
```python
sparse_vectors_config = {
    "bm25": models.SparseVectorParams(
        modifier=models.Modifier.IDF,
        index=models.SparseIndexParams(on_disk=False),
    )
}
```

**Payload Indexes** (required per entity):
```python
payload_indexes = [
    ("entity_name", models.PayloadSchemaType.KEYWORD),
    ("session_id", models.PayloadSchemaType.KEYWORD),
    ("type", models.PayloadSchemaType.KEYWORD),
    ("timestamp", models.PayloadSchemaType.DATETIME),
    ("tags", models.PayloadSchemaType.KEYWORD),
    ("source", models.PayloadSchemaType.KEYWORD),
]
for field, schema in payload_indexes:
    await client.create_payload_index(
        collection_name="omega_knowledge",
        field_name=field,
        field_schema=schema,
    )
```

---

## 4. Multi-Entity Isolation

**Strategy: Single Collection + Payload Partitioning** (not per-entity collections)

**Rationale**:
- Qdrant's payload filtering integrates with HNSW traversal (pre-filtering)
- Per-tenant collections create overhead for many small tenants
- Qdrant v1.19+ supports per-tenant IDF statistics for BM25

**Payload Filter Pattern**:
```python
from qdrant_client import models

query_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="entity_name",
            match=models.MatchValue(value="researcher"),
        ),
        models.FieldCondition(
            key="type",
            match=models.MatchValue(value="knowledge"),
        ),
    ]
)

results = await client.query_points(
    collection_name="omega_knowledge",
    query=query_vector,
    query_filter=query_filter,
    limit=10,
    search_params=models.SearchParams(hnsw_ef=128),
)
```

**Filter Performance**: Pre-filtering via payload indexes adds ~1-2ms overhead. With proper indexes, filtering is integrated into HNSW traversal — no post-filter recall loss.

---

## 5. Hybrid Search Configuration

**Sparse Vector Model**: `Qdrant/bm25` (FastEmbed, local, no API calls)

**Collection Creation**:
```python
await client.create_collection(
    collection_name="omega_hybrid",
    vectors_config={
        "dense": models.VectorParams(size=768, distance=models.Distance.COSINE),
    },
    sparse_vectors_config={
        "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF),
    },
)
```

**Fusion Method**: **RRF (Reciprocal Rank Fusion)** — Qdrant default, handles score normalization automatically

**Query API** (prefetch pattern):
```python
from qdrant_client import models

results = await client.query_points(
    collection_name="omega_hybrid",
    prefetch=[
        models.Prefetch(
            query=models.Document(text=query_text, model="Qdrant/bm25"),
            using="bm25",
            limit=50,
        ),
        models.Prefetch(
            query=dense_vector,
            using="dense",
            limit=50,
        ),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),
    limit=10,
    query_filter=entity_filter,
)
```

**Reranker**: Cross-encoder (e.g., `BAAI/bge-reranker-v2-m3`) applied client-side on top-50 fused results.

---

## 6. Migration Procedure

**Export from sqlite-vec**:
```python
import sqlite3
import sqlite_vec
import numpy as np
from qdrant_client import AsyncQdrantClient, models

conn = sqlite3.connect("data/knowledge/vec.db")
conn.enable_load_extension(True)
sqlite_vec.load(conn)
cursor = conn.cursor()

BATCH_SIZE = 1000
offset = 0
while True:
    rows = cursor.execute(
        "SELECT id, vector, payload FROM embeddings LIMIT ? OFFSET ?",
        (BATCH_SIZE, offset)
    ).fetchall()
    if not rows:
        break
    
    points = []
    for row in rows:
        point_id, vector_blob, payload_json = row
        vector = np.frombuffer(vector_blob, dtype=np.float32)
        payload = json.loads(payload_json)
        points.append(models.PointStruct(
            id=point_id,
            vector={"dense": vector.tolist()},
            payload=payload,
        ))
    
    await client.upsert(
        collection_name="omega_knowledge",
        points=points,
        wait=True,
    )
    offset += BATCH_SIZE
```

**Bulk Import Optimization**:
- **Batch size**: 1000 points
- **Parallelism**: 4 concurrent upsert tasks
- **gRPC**: Required for bulk throughput
- **Shard number**: 2 for collections >1M vectors

**Verification** (Recall Parity Test):
```python
test_queries = load_test_queries(100)
for q in test_queries:
    sqlite_results = search_sqlite_vec(q, k=10)
    qdrant_results = await search_qdrant(q, k=10)
    recall = compute_recall(sqlite_results, qdrant_results)
    assert recall >= 0.95, f"Recall {recall} below threshold"
```

**Rollback Plan**:
1. Keep sqlite-vec DB read-only during migration
2. Qdrant snapshots created after successful migration
3. If issues: stop Qdrant, restart sqlite-vec service, DNS switch back

---

## 7. Config Files to Create

**`config/qdrant.yaml`** (mounted at `/qdrant/config/production.yaml`):
```yaml
storage:
  storage_path: /qdrant/storage
  snapshots_path: /qdrant/snapshots
  on_disk_payload: true
  
wal:
  wal_capacity_mb: 1024

optimizers:
  deleted_threshold: 0.2
  vacuum_min_vector_number: 1000
  default_segment_number: 2
  max_segment_size_kb: null
  indexing_threshold_kb: 10000
  flush_interval_sec: 5
  max_optimization_threads: 4

hnsw_index:
  m: 16
  ef_construct: 256
  full_scan_threshold: 10000
  max_indexing_threads: 4

quantization:
  scalar:
    type: int8
    quantile: 0.99
    always_ram: true

performance:
  max_search_threads: 4

service:
  api_key: ""
  http_port: 6333
  grpc_port: 6334
  enable_cors: false

telemetry_disabled: true
log_level: INFO
```

**`config/jit_rag.yaml`** (updated for Qdrant):
```yaml
vector_store:
  type: qdrant
  host: 127.0.0.1
  port: 6333
  grpc_port: 6334
  api_key_env: QDRANT_API_KEY
  prefer_grpc: true
  pool_size: 20
  timeout: 30.0

collections:
  entities: omega_entities
  sessions: omega_sessions
  knowledge: omega_knowledge
  code: omega_code
  hybrid: omega_hybrid

embedding:
  model: embeddinggemma:768m
  dimensions: 768
  mrl_dimensions: [768, 512, 256, 128]
  distance: cosine

hybrid_search:
  enabled: true
  sparse_model: "Qdrant/bm25"
  fusion: rrf
  prefetch_limit: 50
  final_limit: 10
  reranker: "BAAI/bge-reranker-v2-m3"

quantization:
  enabled: true
  type: int8
  quantile: 0.99
  always_ram: true

hnsw:
  m: 16
  ef_construct: 256
  ef_search: 128

payload_indexes:
  - entity_name
  - session_id
  - type
  - timestamp
  - tags
  - source
```

**Podman Quadlet** (`~/.config/containers/systemd/qdrant.container`):
```ini
[Unit]
Description=Qdrant Vector Database (Omega Engine)
After=network-online.target
Wants=network-online.target

[Container]
Image=qdrant/qdrant:v1.18.1
ContainerName=qdrant
PublishPort=127.0.0.1:6333:6333
PublishPort=127.0.0.1:6334:6334
Volume=%h/OmegaLibrary/qdrant/storage:/qdrant/storage:Z
Volume=%h/OmegaLibrary/qdrant/config:/qdrant/config:Z
Volume=%h/OmegaLibrary/qdrant/snapshots:/qdrant/snapshots:Z
Environment=QDRANT__TELEMETRY_DISABLED=true
Environment=QDRANT__LOG_LEVEL=INFO
Environment=QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
Environment=QDRANT__CONFIG_PATH=/qdrant/config/production.yaml
AutoUpdate=registry

[Service]
Restart=always
RestartSec=10
TimeoutStartSec=300
MemoryLimit=6G
CPUQuota=80%
MemorySwapLimit=6G

[Install]
WantedBy=default.target
```

---

## 8. Code Changes Required

**`src/omega/oracle/adapters/qdrant_adapter.py`** (Revival — implement `IVectorStoreAdapter`):
```python
class QdrantAdapter(IVectorStoreAdapter):
    """Qdrant implementation of IVectorStoreAdapter for JIT RAG."""
    
    def __init__(self, config: JitRagConfig):
        self.client = AsyncQdrantClient(
            url=f"http://{config.host}:{config.port}",
            grpc_port=config.grpc_port,
            prefer_grpc=True,
            api_key=config.api_key,
            pool_size=20,
            timeout=config.timeout,
        )
        self.collections = config.collections
    
    async def upsert(self, collection: str, points: list[PointStruct]) -> None:
        await self.client.upsert(collection_name=collection, points=points, wait=True)
    
    async def query(
        self,
        collection: str,
        vector: list[float],
        filter: Filter | None = None,
        limit: int = 10,
        ef_search: int = 128,
    ) -> list[ScoredPoint]:
        return await self.client.query_points(
            collection_name=collection,
            query=vector,
            query_filter=filter,
            limit=limit,
            search_params=models.SearchParams(hnsw_ef=ef_search),
        )
    
    async def hybrid_query(
        self,
        collection: str,
        dense_vector: list[float],
        sparse_text: str,
        filter: Filter | None = None,
        limit: int = 10,
    ) -> list[ScoredPoint]:
        return await self.client.query_points(
            collection_name=collection,
            prefetch=[
                models.Prefetch(query=dense_vector, using="dense", limit=50),
                models.Prefetch(
                    query=models.Document(text=sparse_text, model="Qdrant/bm25"),
                    using="bm25",
                    limit=50,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            query_filter=filter,
        )
    
    async def create_collection(self, name: str, config: CollectionConfig) -> None:
        await self.client.create_collection(...)
    
    async def create_payload_indexes(self, collection: str, fields: list[str]) -> None:
        for field in fields:
            await self.client.create_payload_index(
                collection_name=collection,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
```

**`src/omega/oracle/embedding_manager.py`** (Qdrant provider integration):
- Add `QdrantEmbeddingProvider` class
- Implement MRL truncation via `options={"mrl": dim}` for supported models
- Route embedding calls through Qdrant Cloud Inference or local FastEmbed

**`src/omega/oracle/selective_hydration.py`** (Qdrant query changes):
- Replace sqlite-vec FTS5 calls with Qdrant `query_points`
- Add payload filter for `entity_name`, `session_id`, `type`
- Implement hybrid search path for `omega_hybrid` collection

**Tests** (`tests/integration/test_qdrant_migration.py`):
- `test_collection_creation` — verify schema, quantization, HNSW params
- `test_upsert_batch` — 1000 points, verify count
- `test_query_recall` — parity test vs sqlite-vec (≥95%)
- `test_hybrid_search` — RRF fusion, BM25 + dense
- `test_payload_filtering` — entity isolation
- `test_migration_script` — end-to-end sqlite-vec → Qdrant
- `test_snapshot_backup_restore` — create/download/upload snapshot

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Qdrant OOM on 6GB limit** | Medium | High | Scalar int8 quantization (4x savings), `on_disk_payload=true`, `max_search_threads=4`, monitor via Prometheus |
| **gRPC connection exhaustion** | Medium | High | `pool_size=20`, connection reuse, monitor `qdrant_grpc_connections_active` |
| **Recall regression vs sqlite-vec** | Low | High | Parity test (100 queries, ≥95% recall), fallback to sqlite-vec if failed |
| **Payload filter performance** | Low | Medium | Create indexes BEFORE bulk insert, use KEYWORD type for exact match |
| **MRL truncation unsupported for embeddinggemma** | Medium | Medium | Verify model supports MRL; if not, use full 768-dim, plan fine-tune later |
| **Snapshot restore failure** | Low | High | Test restore in staging weekly, keep sqlite-vec as hot standby for 30 days |
| **Podman quadlet permission issues** | Medium | Medium | Use `:Z` for SELinux (Ubuntu AppArmor ignores), pre-create dirs with `chown 1000:1000` |
| **Telemetry leakage** | Low | Critical | `QDRANT__TELEMETRY_DISABLED=true` in quadlet + config.yaml double-disable |
| **API key rotation** | Low | Medium | Store in `.env` (gitignored), rotate via `systemctl reload qdrant` |

---

## 📋 Implementation Checklist

- [ ] Create `config/qdrant.yaml` and `config/jit_rag.yaml`
- [ ] Create Podman quadlet at `~/.config/containers/systemd/qdrant.container`
- [ ] Generate API key: `openssl rand -hex 32 > .qdrant_api_key`
- [ ] Deploy Qdrant: `systemctl --user daemon-reload && systemctl --user enable --now qdrant`
- [ ] Verify health: `curl http://127.0.0.1:6333/health`
- [ ] Implement `QdrantAdapter` in `src/omega/oracle/adapters/`
- [ ] Update `EmbeddingManager` with Qdrant provider
- [ ] Update `SelectiveHydration` for Qdrant queries
- [ ] Write migration script `scripts/migrate_sqlite_vec_to_qdrant.py`
- [ ] Run parity tests (100 queries, ≥95% recall)
- [ ] Create initial snapshot: `POST /collections/omega_knowledge/snapshots`
- [ ] Configure Prometheus scraping (port 6333/metrics)
- [ ] Import Grafana dashboard from `qdrant/prometheus-monitoring`
- [ ] Switch JIT RAG to Qdrant in `config/omega.yaml`
- [ ] Deprecate sqlite-vec code path (keep for 30-day rollback)

---

**Sources Cited**:
- Qdrant docs: configuration, quantization, hybrid search, multi-tenancy, snapshots, bulk upload, monitoring
- ComputingForGeeks: Podman Quadlet, Qdrant REST vs gRPC benchmark, Prometheus monitoring
- LlamaIndex: Qdrant hybrid search integration patterns
- Qdrant client GitHub: async client, connection pooling, error handling
- Stochastic Sandbox: HNSW + scalar quantization config
- Markaicode: Production Qdrant setup, HNSW tuning
- Qdrant blog: Matryoshka/MRL support, Gemini Embedding 2
