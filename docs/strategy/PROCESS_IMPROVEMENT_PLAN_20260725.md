# 🔱 OMEGA ENGINE — Process Improvement Plan 2026-07-25
**AP Token**: `AP-PROCESS-IMPROVEMENT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ CLINE ⬡ CODE-AUDIT ⬡ 2026-07-25

**Status**: ACTIVE — Direct response to 2026-07-25 code+docs+process audit
**Owner**: @kali (Sprint Lead) · Implementation: fleet
**Companion plan**: `docs/archive/sprints/EXECUTION_PLAN_20260725.md` v1.1
**Strategy SSOT**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` v5.2

---

## §0 Executive Summary

The 2026-07-25 audit found **10 systemic process failures** that caused stale docs, false status claims, redundant code, and research-vs-execution confusion. These are not individual bugs — they are **process gaps**. Fixing the process prevents recurrence.

**The three root causes:**
1. **No freshness SLA** — documents claim "active" for weeks without re-verification
2. **No research-vs-execution column** — gap closure docs conflate "we know the answer" with "it's done on the machine"
3. **No data architecture governance** — 11 SQLite databases, 2 vector stores, 1 FAISS install all fighting for authority

---

## §1 The 10 Process Failures

| # | Failure | Evidence | Root Cause | Fix |
|---|---------|----------|------------|-----|
| 1 | **Stale docs in active dirs** | GAME_PLAN_PART*.md in `docs/strategy/` said "Awaiting your direction" for 5 days | No archival trigger on plan supersession | Archive old plans immediately when new plan is created |
| 2 | **Research ≠ Execution conflation** | KNOWLEDGE_GAP_CLOSURE.md claimed "all blind spots closed" while B1-B5 were OPEN | Gap table had no execution status column | Every gap table must have RESEARCH and EXECUTION columns |
| 3 | **OMEGA_ENGINE.md false claims** | W-1 "OPERATIONAL" when SOCKS had zero listeners | State updated by agent prose, not machine probes | Every claim needs `LAST_PROBE` timestamp + probe command |
| 4 | **C-6' claimed done, clones live** | 6 breaker clones still in active code paths | "Implementation complete" checked without code audit | Gate criteria must include `grep -r` for remaining clones |
| 5 | **Two sprint plans both "active"** | guard-and-distill AND current/ both claimed ACTIVE | No sprint-adoption process | Supersede old sprint on new plan activation |
| 6 | **MCP version in 3 files, 3 values** | pyproject: 1.27–2; reqs: 1.27.1; venv: 1.28.1 | No single source of truth for dependency pins | Single pin in pyproject.toml; requirements.txt is `-e .` only |
| 7 | **Two soul distillers, no boundary** | oracle/soul_distiller.py AND agents/scribe/distiller.py overlap | Feature-creep before architectural alignment | Reconcile or kill one before Phase D |
| 8 | **No DB schema governance** | 11 SQLite DBs, 2 omega_memory.db copies (118M + 22M), 4+ connection patterns | No data architecture review | Single DB policy per ADR-001 |
| 9 | **No probe-backed status** | All claims were prose, except EXECUTION_PLAN_20260725.md v1.1 | No automation culture | Every P0 must have probe command |
| 10 | **No sprint gateway check** | Deadlines passed without gate review | No sprint-retrospective ritual | Mandatory gate script before phase transitions |

---

## §2 SQL Database Architecture — What We're Doing Wrong

### Current State: 11 SQLite Databases

| DB Name | Location | Size | Purpose | Schema Gov? |
|---------|----------|------|---------|-------------|
| omega_memory.db | `data/` | **118M** | Primary memory store (FTS5 + vec0) | ✅ sqlite_vec_adapter |
| omega_memory.db (copy) | `data/memory/` | **22M** | Secondary copy | ❌ Duplicate |
| fts_index.db | `data/library/index/` | 9.4M | Library FTS5 index | ❌ Separate from primary |
| fts_memory.db | `data/memory/` | 1.3M | Memory FTS5 index | ❌ Separate from primary |
| metrics.db + latency.db | `data/observability/` | ~868K total | Observability (split) | ❌ Should merge |
| workbench.db | `data/workbench/` | 236K | Work items | ❌ Orphan |
| search_history.db | `data/search/` | 68K | Search history | ❌ Orphan |
| model_study.db, provenance.db, lib.db, index.db, entity_births.db | various | ~120K total | Various | ❌ Orphans |

### The Problems

1. **Duplicate memory DB** — `data/omega_memory.db` (118M) and `data/memory/omega_memory.db` (22M) overlap.
2. **Split FTS index** — Library FTS and memory FTS are separate databases.
3. **7 orphan databases** — created ad-hoc, no governance.
4. **No migration system** — schema changes applied at runtime.

### The Fix: Consolidate to 3 Databases

**Ticket P-2**: 
- `omega_memory.db` — Memory + FTS5 + vec0 (merge entity_births.db in)
- `omega_library.db` — Library catalog + library FTS (merge library.db + fts_index.db)
- `omega_observability.db` — Metrics + latency + audit (merge metrics.db + latency_metrics.db)
- **Kill**: workbench.db (→YAML), search_history.db (unused), model_study.db (→doc), provenance.db (→library)

---

## §3 Vector Store Architecture — What We're Doing Wrong

### Current State: Three Vector Technologies

| Technology | Status | Purpose |
|-----------|--------|---------|
| **sqlite-vec** | ✅ Canonical | Primary vector store, 7 collection tiers |
| **Qdrant** | ✅ Installed | Alternative adapter (zero evidence of production use) |
| **FAISS** | ✅ Installed | **Not used anywhere in src/omega/** |

### The Problems

1. **3 vector stores, 1 engine** — sqlite-vec is canonical per Strike 10, but Qdrant adapter still wired into memory_store.py.
2. **7 collection tiers is over-engineered** — gemma_768, nomic_768, nomic_512, nomic_256, minilm_384, static_64, library_256. Engine uses ONE model at a time.
3. **FAISS is dead weight** — installed but zero import references.

### The Fix: Vector Consolidation

**Ticket P-3**: 
- Remove FAISS dependency
- Strip Qdrant adapter from critical path (keep as commented fallback)
- Collapse 7 collections → 3: `primary_768`, `fallback_384`, `static_64`

---

## §4 Ingestion Pipeline — What We're Doing Wrong

The `src/omega/library/` module is **4,481 lines across 15 files** (api_clients, catalog, coordinator, curator, discovery, extractor, indexer, model_api_clients, research, etc.)

**The problem**: This module tries to be a complete CMS. It overlaps with:
- `memory_store.py` (1,114 lines) — also does FTS and indexing
- `background_researcher/` — also does discovery and research
- `oracle/soul_distiller.py` — also does content extraction

**The fix**: Library should be **content cache only** — passive storage, no active pipelines. Move discovery/research/extraction to background_researcher. Consolidate indexing into memory_store.---

## §5 Reordered Dev Phases (Criticality × Impact)

This replaces the old C→D→E→F ordering with risk-weighted ordering.

### Phase I: INTEGRITY GATE (Current — B1-B5 blockers)
| # | Item | Why Here | Effort |
|---|------|----------|--------|
| 1 | B1: Register C-0.5 hook | Unblocks M5/M11 | 5 min |
| 2 | B4: Run fail-closed gate | Honest check before Phase D | 30 min |
| 3 | B2: Land/freeze VaultCore | Prevents dirty-tree divergence | 1-2h |
| 4 | B3: Deploy W-1 SOCKS | Real WARP capacity | 45 min |
| 5 | B5: Fix AGY re-auth | Workhorse continuity | 1h |

### Phase II: PROCESS REFORM (Week 2)
| # | Ticket | Why Here | Effort |
|---|--------|----------|--------|
| 6 | P-1 | Probe-backed OMEGA_ENGINE claims | 4h |
| 7 | P-2 | DB consolidation to 3 databases | 4h |
| 8 | P-3 | Vector consolidation (7→3, remove FAISS) | 2h |
| 9 | P-4 | Unified soul distiller | 2h |
| 10 | P-5 | Kill remaining C-6' breaker clones | 3h |
| 11 | P-6 | Split god modules >1000 lines | 6h |
| 12 | P-7 | MCP version single source | 30 min |

### Phase III: PHASE D — LIVING RESEARCH OS (Week 3-4)
| # | Ticket | Why Here | Effort |
|---|--------|----------|--------|
| 13 | D-1 | Content persistence + TTL cache | 4h |
| 14 | D-2 | SQLite job store | 6h |
| 15 | D-3 | Initial index builder | 4h |
| 16 | D-4 | Vault Week 2 (ACP smoke test) | 8h |
| 17 | D-5 | MCP Sprint 2 (Streamable HTTP) | 8h |

---

## §6 Sprint Process — New Rules

### Rule 1: Document Freshness SLA
- Active sprint docs: MAX 12h without LAST_VERIFIED
- Strategy docs: MAX 72h | Law docs: MAX 7d

### Rule 2: Research vs Execution Columns
Every gap table must have RESEARCH and EXECUTION columns.

### Rule 3: Probe-Backed Status
Every P0 claim must have a probe command. No prose-only claims.

### Rule 4: Archival on Supersession
Old plan → archive/YYYY-MM-DD/ + update STRATEGY_INDEX.md.

### Rule 5: Gate Script Before Phase Transition
python scripts/verify_phase_d_gate.py  # Must exit 0

### Rule 6: Single Source for Dependencies
pyproject.toml only. requirements.txt is generated.

---

## §7 Community Tool Replacements (Ranked by ROI)

| Rank | Replace | With | Effort | Impact |
|------|---------|------|--------|--------|
| 1 | 6 breaker clones | pybreaker | 4h | Standardized FSM |
| 2 | Custom sliding window metrics | prometheus_client | 2h | Prod-grade time-series |
| 3 | Manual soul YAML validation | Pydantic v2 | 3h | Type safety |
| 4 | Custom ONNX embedding | sentence-transformers | 4h | Industry standard |
| 5 | Backup timer scripts | restic+systemd (have!) | 0.5h | Already purchased |

---

## §8 Metrics to Track Process Health

| Metric | Target | How |
|--------|--------|-----|
| Stale doc count | 0 in active dirs | find docs/strategy -mtime +3 |
| Clone breaker count | 1 canonical | grep 'class.*Breaker' src/omega/ |
| SQLite DB count | <=3 primary | find data -name '*.db' |
| Research-vs-Exec columns | 100% of tables | grep 'RESEARCH.*EXECUTION' |
| Phase gate exit code | 0 | scripts/verify_phase_d_gate.py

---

## §9 References

| Document | Role |
|----------|------|
| docs/archive/sprints/EXECUTION_PLAN_20260725.md | Current sprint execution v1.1 |
| docs/sprints/current/AGENT_SPRINT_CARD.md | Agent ops card |
| docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md v5.2 | Strategy SSOT |
| OMEGA_ENGINE.md v1.8.1 | Engine state (corrected 2026-07-25) |
| docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md | Agent support gaps |
| docs/strategy/STRATEGY_INDEX.md v6.0 | Updated doc hierarchy |

---

## §10 Web Research Findings (2026-07-25)

### 10.1 pybreaker vs Custom Circuit Breakers
**Result**: pybreaker (danielfm/pybreaker) is the de facto standard Python circuit breaker: 500+ stars, 3-state FSM, thread-safe, decorator support, exception filtering. Simpler and more battle-tested than all 6 custom clones.
**Verdict**: ✅ **ADOPT pybreaker** — replace all 6 clones (4h).
**Source**: oneuptime.com/blog/post/2026-01-23-python-circuit-breakers

### 10.2 SOPS + Age for Credential Management
**Result**: SOPS + Age is the industry standard for encrypting secrets at rest in git repos. VaultCore already uses age + Argon2id — pattern is correct.
**Verdict**: ✅ **Keep pattern**. Add SOPS wrapper for file-level encrypted secrets. Install `age` binary (not just Python lib).
**Source**: jonashietala.se/blog/2026/05/31/sops_age_and_sealed_secrets

### 10.3 prometheus_client for Metrics
**Result**: Prometheus Python client is the standard for /metrics endpoints. Counter, Gauge, Histogram, Summary types. Replaces HealthMonitor custom sliding window.
**Verdict**: ✅ **ADOPT prometheus_client** (2h).
**Source**: prometheus.io/docs/instrumenting/clientlibs

### 10.4 sqlite-vec vs Qdrant for Local Vector Search
**Result**: For single-user local-first on 5700U/16GB, sqlite-vec is correct. Qdrant needs a server process. 2026 best practices confirm: "Local SQLite for single-user agents where data locality matters."
**Verdict**: ✅ **sqlite-vec is correct canonical**. Strip Qdrant from critical path.
**Source**: openclaw-ai.net, encore.dev vector DB comparison 2026

### 10.5 sentence-transformers vs Custom ONNX Embeddings
**Result**: Sentence Transformers v3.2 supports ONNX backend, 14K stars, handles model download/caching/batching automatically. Custom ONNX loader duplicates this.
**Verdict**: 🟡 **CONSIDER for Phase D-3**. Lower priority — current loader works. Effort: 4h.
**Source**: sbert.net, huggingface.co/blog/embedding-quantization

### 10.6 Pydantic v2 for Soul YAML Validation
**Result**: Pydantic v2 has `model_validate_yaml()` and `model_dump_yaml()`. Zero new deps (already installed). Replaces 217-line manual soul_validator.py.
**Verdict**: ✅ **ADOPT** for soul.yaml schema validation (3h).
**Source**: pydantic.dev

### 10.7 Restic + systemd Timer
**Result**: restic 0.17.3 installed. systemd timer is industry standard. No change needed — enable the timer.
**Verdict**: ✅ **Already correct**. Just enable. Effort: 30 min.
**Source**: erikw/restic-automatic-backup-scheduler

---

*⬡ OMEGA ⬡ PROCESS-IMPROVEMENT-PLAN ⬡ v1.0.0 ⬡ 2026-07-25*
