# Knowledge Freshness Systems — Working Implementations (2025‑2026)

**AP Token**: `AP-KF-SYSTEMS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kf_systems ⬡ ACTIVE

**Date**: 2026-08-18
**Purpose**: Catalog of production‑grade knowledge‑freshness systems — automated re‑verification, doc‑rot detection, freshness SLAs, and concrete tools/frameworks.

---

## Executive Summary

**The #1 failure mode**: Knowledge rot — the silent divergence between an AI system’s retrieval index and current organizational reality. **The solution that works**: *Automated freshness‑weighted retrieval + source‑system webhooks + assigned document owners*. Manual audits fail; continuous monitoring succeeds.

---

## 1. Scabera Continuous Monitoring Model (Most Cited)

### Architecture
```
Source Systems (Git, Confluence, Notion, APIs)
        │
        ▼
┌───────────────────┐
│  CHANGE DETECTOR  │  ← Webhooks / polling / CDC
│  (per doc type)   │
└─────────┬─────────┘
          │ emits ChangeEvent
          ▼
┌───────────────────┐
│  FRESHNESS ENGINE │  ← Computes freshness score per chunk
│  • age_score      │     age_score = 1 - min(1, days_since_update / TTL)
│  • embed_lag      │     embed_lag = 1 - min(1, reindex_delay_hours / 24)
│  • owner_alert    │     owner_alert = 1 if owner_acknowledged else 0
│  • composite      │     freshness = 0.5*age + 0.3*embed_lag + 0.2*owner
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  RETRIEVAL WEIGHT │  ← Freshness score weights BM25/vector scores
│  (at query time)  │     final_score = base_score * freshness^α
└───────────────────┘
```

### Key Sources
| Source | URL | Verified |
|--------|-----|----------|
| Scabera: Preventing Knowledge Rot | <https://scabera.com/blog/knowledge-rot-prevention-enterprise> | ✅ |
| Scabera: Knowledge Rot Hidden Cost | <https://scabera.com/blog/knowledge-rot-enterprise-ai-hidden-cost> | ✅ |

### What Works
- **Continuous, not periodic**: Webhooks from source systems (Git push, Confluence update) trigger immediate re‑indexing of affected chunks.
- **Freshness‑weighted retrieval**: At query time, chunks with low freshness scores are down‑weighted (α=0.5‑1.0). Prevents confident wrong answers from stale docs.
- **Document ownership**: Every doc type has an owner (team/individual). Owner must acknowledge changes within SLA (24h for product, 72h for policy). Unacknowledged → freshness penalty.
- **Metrics dashboard**: Tracks “stale retrieval rate”, “re‑index lag”, “owner acknowledgment rate”.

### What Doesn’t
- **Requires source‑system integration**: Not all tools expose webhooks (legacy wikis, PDFs). Fallback: scheduled polling (hourly) with content hash diff.
- **Owner assignment is organizational, not technical**: Needs buy‑in; teams that skipped it saw freshness scores decay to 0.3 within 2 weeks.
- **Composite score tuning**: Weights (0.5/0.3/0.2) are heuristic; requires A/B testing per domain.

---

## 2. AgentForgeHub Playbook — Source SLAs & Expiration Rules

### Core Rules
| Document Type | Review Cadence | Expiration (auto‑archive) | Re‑index Trigger |
|---------------|----------------|---------------------------|------------------|
| Product specs | Monthly | 90 days | Git push to `docs/` |
| API references | Weekly | 60 days | OpenAPI spec change |
| Policies/Compliance | Quarterly | 180 days | Confluence `last_modified` |
| Runbooks/Incidents | After each incident | 30 days | Incident closure webhook |
| Reference/Archival | Annually | 365 days | Manual only |

### Key Source
| Source | URL | Verified |
|--------|-----|----------|
| AgentForgeHub: Knowledge Freshness for AI Agents | <https://www.agentforgehub.com/posts/knowledge-freshness-for-ai-agents> | ✅ |

### What Works
- **Explicit SLAs per doc type**: Removes ambiguity; owners know exactly when to review.
- **Automated expiration**: Chunks past expiration are moved to `archival` namespace (still searchable but heavily down‑weighted).
- **Retrieval pipelines that age gracefully**: Query router checks freshness namespace first; falls back to archival only if no fresh results.

### What Doesn’t
- **Manual review cadence still human‑dependent**: Automated reminders help but don’t guarantee quality of review.
- **Cross‑doc dependencies ignored**: Updating a product spec may invalidate a runbook; no automatic dependency tracking.

---

## 3. Fast.io 2026 Guide — Automated Change Detection + Weekly Audit

### Pipeline
```mermaid
graph LR
    A[Source System] -->|Webhook / Poll| B(Change Detector)
    B --> C{Content Hash Changed?}
    C -->|Yes| D[Re‑index Affected Chunks]
    C -->|No| E[Update Last‑Checked Timestamp]
    D --> F[Update Freshness Metadata]
    F --> G[Notify Owner (Slack/Email)]
    G --> H[Owner Acknowledges in Portal]
    H --> I[Freshness Score = 1.0]
    E --> J[Weekly Audit Job]
    J --> K[Flag Docs > SLA Without Ack]
    K --> L[Escalate to Doc Owner Manager]
```

### Key Source
| Source | URL | Verified |
|--------|-----|----------|
| Fast.io: AI Agent Knowledge Base Management 2026 | <https://fast.io/resources/ai-agent-knowledge-base-management/> | ✅ |

### What Works
- **Content‑hash diffing**: Avoids re‑indexing unchanged docs; scales to 100k+ docs.
- **Owner acknowledgment portal**: Simple internal tool (or Notion page) where owners click “Reviewed”. Low friction.
- **Weekly audit as safety net**: Catches docs that missed webhooks (e.g., manual PDF uploads).

### What Doesn’t
- **Weekly audit becomes noisy**: Without good filtering, owners get alert fatigue. Fast.io recommends “only alert on docs with >5 retrievals in last week”.

---

## 4. CobbAI — AI + Workflows for Freshness Automation

### Pattern
Use an **AI agent** to:
1. Fetch changed docs (via API)
2. Summarize changes
3. Identify impacted chunks in vector store
4. Draft update suggestions for owner
5. Owner approves → auto‑apply

### Key Source
| Source | URL | Verified |
|--------|-----|----------|
| CobbAI: Knowledge Freshness Automation | <https://cobbai.com/blog/knowledge-freshness-automation> | ✅ |

### What Works
- **Reduces owner burden**: Owner reviews AI‑drafted diff, not raw doc.
- **Consistent update style**: AI applies same formatting/terminology.

### What Doesn’t
- **AI can hallucinate changes**: Requires human‑in‑the‑loop approval; not fully autonomous.
- **Setup complexity**: Needs LLM + vector store + source APIs + approval workflow.

---

## 5. Tianpan / Atlan — RAG Freshness Index & Scoring Frameworks

### Tianpan: Index Rot Detection
- **Metric**: *Stale Retrieval Rate* = (retrievals from chunks > TTL) / (total retrievals)
- **Detection**: Nightly job samples 1% of queries, checks chunk freshness, alerts if SRR > 5%
- **Fix**: Auto‑re‑index flagged chunks; if source unchanged, extend TTL

### Atlan: Knowledge Base Freshness Scoring (4 Dimensions)
| Dimension | Metric | Target |
|-----------|--------|--------|
| Content Age | Days since source `last_modified` | < 30 days (product) |
| Embedding Lag | Hours between source update & vector update | < 4 hours |
| Stale Retrieval | % of queries returning >1 stale chunk in top‑5 | < 2% |
| Owner Coverage | % of docs with assigned active owner | 100% |

### Key Sources
| Source | URL | Verified |
|--------|-----|----------|
| Tianpan: RAG Knowledge Base Freshness | <https://tianpan.co/blog/2026-04-20-rag-knowledge-base-freshness-index-rot> | ✅ |
| Atlan: Context Freshness | <https://atlan.com/know/ai-agent/context-freshness/> | ✅ |
| Atlan: LLM Knowledge Base Freshness Scoring | <https://atlan.com/know/llm-knowledge-base-freshness-scoring/> | ✅ |

### What Works
- **Quantifiable SLAs**: Freshness becomes a measurable SLO, not a feeling.
- **Dashboardable**: All four dimensions are queryable from vector store metadata + source system APIs.

### What Doesn’t
- **Requires metadata discipline**: Every chunk must carry `source_id`, `source_updated_at`, `indexed_at`, `owner_id`. Retrofitting existing indexes is painful.

---

## 6. Tool / Framework Landscape (2026)

| Tool | Category | Freshness Features | Self‑Hosted | Notes |
|------|----------|-------------------|-------------|-------|
| **Aegis Memory** | Semantic memory layer | TTL per fact, confidence decay, owner alerts | ❌ SaaS | CrewAI‑native |
| **Mem0** | Vector memory | `memory.ttl`, `memory.metadata.freshness` | ✅ (Chroma/FAISS) | Generic |
| **Letta (MemGPT)** | Agent OS | Archival tier TTL, automatic decay policies | ✅ Docker | Best for agents |
| **Cognee** | Knowledge graph | Graph‑based freshness propagation | ✅ | Early stage |
| **Custom (Scabera pattern)** | DIY | Full control | ✅ | Most production teams build this |

---

## 7. Implementation Roadmap for Omega Engine

| Phase | Action | Owner | Evidence |
|-------|--------|-------|----------|
| 1 | Add `freshness_score` column to `MemoryStore` chunks (float 0‑1) | Ma'at | Scabera composite formula |
| 2 | Implement `SourceWatcher` — webhook receiver for Git/Confluence/Notion | Ma'at | Fast.io change detector |
| 3 | Build `FreshnessWeightedRetriever` — multiplies BM25/vector score by `freshness^α` | Ma'at | Scabera retrieval weight |
| 4 | Add `document_owner` metadata + acknowledgment API | Kali | AgentForgeHub SLAs |
| 5 | Weekly audit cron → `data/coordination/FRESHNESS_AUDIT.log` | Scribe | Fast.io weekly audit |
| 6 | Dashboard: stale retrieval rate, embed lag, owner coverage | Verity | Atlan 4‑dimension scoring |

---

## 8. Sources & Verification

| # | Source | Access | Verified |
|---|--------|--------|----------|
| 1 | Scabera Knowledge Rot Prevention | ✅ Public | ✅ |
| 2 | Scabera Knowledge Rot Hidden Cost | ✅ Public | ✅ |
| 3 | AgentForgeHub Freshness Playbook | ✅ Public | ✅ |
| 4 | Fast.io KB Management 2026 | ✅ Public | ✅ |
| 5 | CobbAI Freshness Automation | ✅ Public | ✅ |
| 6 | Tianpan RAG Freshness Index | ✅ Public | ✅ |
| 7 | Atlan Context Freshness | ✅ Public | ✅ |
| 8 | Atlan Freshness Scoring | ✅ Public | ✅ |

> **Directional only**: Scabera weight formula (0.5/0.3/0.2) and Atlan targets (<30 days, <4h) are published heuristics; validate with your data. CobbAI AI‑drafted updates not independently benchmarked.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kf_systems ⬡ DELIVERABLE-3*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
