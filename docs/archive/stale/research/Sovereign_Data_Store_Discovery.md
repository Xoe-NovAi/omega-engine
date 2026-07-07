# 🔱 Omega Engine — Sovereign Data Store Discovery
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_discovery ⬡ DATA-DISCOVERY

**AP Token**: `AP-DATA-DISCOVERY-v1.0.0`
**Status**: ✅ COMPLETE
**Target**: Cline VSCodium Extension (Implementation Reference)
**Date**: 2026-05-14

---

## 📌 Executive Summary
This report details the implementation and architectural patterns of the **Sovereign Data Store** (Redis and Qdrant) as discovered in the legacy stacks (`omega-stack-legacy`). These findings serve as the technical baseline for the new **Omega Control Plane** memory fabric.

The legacy system utilized a **Tiered Memory Architecture**:
- **HOT Tier (Redis)**: Ephemeral, low-latency session and context storage.
- **WARM Tier (Qdrant)**: Vector-based semantic memory for fast retrieval.
- **COLD Tier (PostgreSQL)**: Permanent, relational storage for all memories.

---

## 🔴 Redis Implementation (The HOT Tier)

### 1. Infrastructure & Hardening
- **Image**: `redis:7.4.1`
- **Connectivity**: Deployed with **Full TLS/SSL** (`rediss://` protocol) using custom CA, certs, and keys.
- **Resource Gating**: 
  - `maxmemory 512mb`
  - `maxmemory-policy allkeys-lru` (Least Recently Used eviction).
- **Port**: 6379 (TLS).

### 2. Usage Patterns
- **Mnemosyne Memory**: Used for the "HOT" tier.
  - **Key Format**: `mnemo:hot:{entity_id}:{context_type}`
  - **TTL**: Default 3600 seconds (1 hour).
  - **Format**: JSON-serialized strings.
- **Coordination & Messaging**:
  - **Streams**: Used for critical system events (e.g., the "Red Phone Kill Switch" via `xrevrange`).
  - **Pub/Sub**: Used for inter-service event broadcasting.
  - **Queues**: Served as the backend for the `library_curator` and crawler workers.
- **State Management**: Used as a lightweight state machine to track migration progress (e.g., `MigrationState` for FAISS $\rightarrow$ Qdrant).

### 3. Monitoring & Health
- **Exporter**: `oliver006/redis_exporter`.
- **Critical Alerts**:
  - Memory usage > 85%.
  - Hit rate < 70% (indicates cache inefficiency).
  - Blocked clients > 0.

---

## 🔵 Qdrant Implementation (The WARM Tier)

### 1. Infrastructure & Configuration
- **Image**: `qdrant/qdrant:v1.13.1`
- **Port**: 6333 (HTTP), 6334 (gRPC).
- **Volumes**: `./data/qdrant` $\rightarrow$ `/qdrant/storage`.
- **Config**: `config/qdrant_config.yaml`.

### 2. Vector Schema (`mnemo_warm` collection)
- **Vector Dimensions**: 1536 (Optimized for OpenAI/Gemini embeddings).
- **Distance Metric**: Cosine Similarity.
- **Payload Structure**:
  - `entity_id`: (String) To filter by entity.
  - `context_type`: (String) To filter by memory type.
  - `data`: (JSON) The actual memory content.
- **Point ID**: Calculated as `hash(entity_id:context_type) % 100000`.

### 3. Core Logic (`mnemosyne_store.py`)
- **Initialization**: Auto-creates the `mnemo_warm` collection if missing.
- **Storage**: Performs an `upsert` of the vector and payload.
- **Retrieval**: Uses a **Filter-based search** on `entity_id` to retrieve the most relevant memory point.

### 4. Backup & Recovery
- **Snapshotting**: Uses the Qdrant REST API (`/collections/{name}/snapshots`) to create atomic backups.
- **Restore**: Dedicated scripts (`restore-qdrant.sh`) for full collection recovery.

### 5. Monitoring & Health
- **Prometheus Metrics**: Monitors search duration (95th percentile), point insertion rates, and index size.
- **Alerts**: Triggered if index size > 100GB or if replication lag > 60s.

---

## ⚖️ Cross-Store Correlation (PostgreSQL Link)
The legacy system used PostgreSQL as the final source of truth. The `embeddings` table in Postgres acted as a relational index for Qdrant:
- **Table**: `embeddings`
- **Link**: `qdrant_id` (BigInteger) maps directly to the Qdrant Point ID.
- **Scores**: `qdrant_score` (Numeric) stores the similarity score for auditing.

---

## 🚀 Implementation Guidance for Cline
When rebuilding the data store for the Omega Control Plane:
1. **Maintain TLS**: Use `rediss://` for all Redis connections to ensure sovereign security.
2. **Preserve Tiers**: Keep the HOT (Redis) $\rightarrow$ WARM (Qdrant) $\rightarrow$ COLD (Postgres) flow; it is proven for the Ryzen 5700U's RAM limits.
3. **Standardize Ports**: Use 6379 (Redis) and 6333 (Qdrant).
4. **Use Socket Activation**: Move these from `docker-compose` to `systemd` user units as per `R-MCP_SOVEREIGN_BLUEPRINT.md`.
