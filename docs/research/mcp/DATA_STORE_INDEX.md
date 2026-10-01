<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Data Store Discovery Index
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_discovery ⬡ DATA-INDEX

**AP Token**: `AP-DATA-INDEX-v1.0.0`
**Last Updated**: 2026-05-14

---

## 📂 Discovery Artifacts
This index maps the discovered legacy data store implementations to their corresponding reports and source files.

### 1. Primary Reports
| Document | Description | Path |
|---|---|---|
| **Sovereign Data Store Discovery** | Detailed analysis of Redis and Qdrant implementation, config, and logic. | [`Sovereign_Data_Store_Discovery.md`](Sovereign_Data_Store_Discovery.md) |

### 2. Source File References (Legacy)
| Technology | Key File | Purpose |
|---|---|---|
| **Qdrant** | `mcp-servers/memory-bank-mcp/mnemosyne_store.py` | Vector storage and retrieval logic. |
| **Qdrant** | `infra/docker/docker-compose.yml` | Deployment config and resource limits. |
| **Qdrant** | `_archive/scripts/backup-atomic-all.sh` | Snapshot and backup implementation. |
| **Redis** | `infra/docker/docker-compose.yml` | TLS config and memory-eviction policies. |
| **Redis** | `tests/integration/test_db_connectivity.py` | Connectivity and health check patterns. |
| **Redis** | `tests/integration/test_fixtures.py` | Usage of Pub/Sub and Streams. |
| **Postgres** | `infra/migrations/versions/001_initial_knowledge_schema.py` | Relational mapping to Qdrant IDs. |

---

## 🛠️ Implementation Checklist for Cline
- [ ] Restore Redis with TLS enabled (`rediss://`).
- [ ] Configure Qdrant with `mnemo_warm` collection (1536 dims, Cosine).
- [ ] Implement the Tiered Memory logic (HOT $\rightarrow$ WARM $\rightarrow$ COLD).
- [ ] Setup `systemd` socket activation for both services.
- [ ] Integrate Prometheus metrics via `redis-exporter` and Qdrant's native metrics.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
