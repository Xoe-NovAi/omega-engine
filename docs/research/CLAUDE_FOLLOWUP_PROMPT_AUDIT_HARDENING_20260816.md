# STRATEGIC FOLLOW-UP PROMPT FOR CLAUDE.AI
## Hardened Hybrid Benchmark Audit — Research-Enhanced Deep Dive

**Pack ID**: `eaa4d2b1-f20c-47aa-ab81-6787243507f5`
**Account**: arcana.novai@gmail.com
**Version**: 2026-08-16 (Research-Enhanced)
**Session Type**: audit|implementation|verification

---

## UPDATED GROUND TRUTH (Research-Enhanced 2026-08-16)

### Hardware & Runtime (Unchanged)
- **Hardware**: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP
- **Python**: 3.13.7 on Linux (requires >=3.12)
- **AnyIO**: 4.13.0 (released Mar 24, 2026) — backend-agnostic on asyncio/Trio
- **SQLite-vec**: vec0 virtual tables with metadata/partition/auxiliary columns

### Research-Backed Pattern Updates

| Area | Previous Assumption | Research Finding (2026) | Implication |
|------|---------------------|-------------------------|-------------|
| **AnyIO Migration** | Manual `asyncio.sleep` → `anyio.sleep` | AnyIO 4.x: drop `asyncio` import entirely; use `anyio.sleep`, `anyio.create_task_group`, `anyio.fail_after` for timeouts | Fix is trivial but must be complete — no mixed asyncio/anyio |
| **SQLite-vec Delete** | Hardcoded `omega_memory_vec` table | vec0 tables support **metadata columns** for collection filtering; partition keys shard by collection; delete via `WHERE collection = ?` on metadata column | Fix: add `collection` metadata column to vec0 tables, delete by collection |
| **OOM Admission** | PSI pressure monitoring | **ConsRoute (2026)**: consistency-driven capability matching — local model attempts first, reranker evaluates semantic consistency, route to cloud only if below threshold | Upgrade: add lightweight reranker for local quality gate before admission |
| **Hybrid Benchmarking** | Static routing table | **ConsRoute 3-tier**: Device → Edge → Cloud with dynamic consistency scoring; **PRISM (AAAI 2026)**: entity-level sensitivity detection for privacy routing | Enhance: add capability matching + sensitivity detection to routing table |
| **SSOT Integrity** | Manual reconciliation | **ADR (Architecture Decision Records)**: standardized format (MADR, Nygard templates); anti-drift architecture stores minimal facts to prevent next bad decision | Implement: ADR format for PIVOT_LOG, automated consistency checks |
| **Query-Aware RAG** | Entity-name-based retrieval | **SaR-RAG (2026-07)**: "on-demand retrieval, refined reranking, selective aggregation" — query rewriting/decomposition for multi-hop, selective context aggregation | Fix: implement query decomposition + selective aggregation in SelectiveHydration |
| **Dead Code Detection** | Vulture only | **CleanAI (2026)**: multi-language IDE-integrated; **Knip** for JS/TS; **evidence-calibrated detection** (ResearchSquare 2026) treats unused code as classification problem with abstention for uncertain | Add: Vulture + pytest-vulture in CI, evidence-calibrated reporting |
| **Model Path Portability** | Hardcoded `/media/...` | **HF_HOME/HF_HUB_CACHE/HF_DATASETS_CACHE** env vars control all Hugging Face caches; `cache_dir` parameter in `load_dataset`/`from_pretrained` | Fix: use `env:HF_HOME` in configs, `cache_dir` in code |
| **Circuit Breaker** | 8 custom classes | **PyBreaker 2026**: async support, adaptive thresholds via ML; **opossum** (Node), **Resilience4j** (Java); **knowledgelib.io**: one breaker per service, percentage thresholds need `minimumNumberOfCalls` | Consolidate: adopt PyBreaker, factory pattern via HealthMonitor |
| **Secrets/Vault** | VaultCore custom (~2000 lines) | **Peta (2025-12)**: agent-native vault + MCP gateway — agents never see raw secrets, ephemeral contextual credentials, scoped least-privilege access | Replace: adopt Peta MCP gateway, eliminate VaultCore custom code |

---

## ENHANCED TASK: DEEP AUDIT + IMPLEMENTATION PLAN

### Role
You are a **Principal Architect** auditing the Omega Engine — a sovereign, local-first AI runtime. Your mindset is **Carmack**: ruthless pragmatism, minimal abstractions, high performance, zero bloat. You now have **research-backed ground truth** for every gap.

### Audit Scope (11 XML Bundles — 44 files, 247,762 tokens)
Same as initial audit, but now with research-enhanced criteria.

### Enhanced Constraints (Non-Negotiable + Research-Backed)

| Mandate | Research-Backed Enforcement |
|---------|----------------------------|
| M1 AnyIO | AnyIO 4.x patterns only — `anyio.sleep`, `anyio.create_task_group`, `anyio.fail_after`; zero `asyncio` imports |
| M2 Firewall | ADR format for all architectural decisions; maakali_routing must have ADR or be removed |
| M7 Local-First | ConsRoute capability matching: local model attempts first, reranker evaluates, cloud only on failure |
| M8 Zero Telemetry | Qdrant telemetry disabled; Prometheus local-only; Peta MCP for agent secrets (no raw secrets in agent memory) |
| M9 Error Integrity | Evidence-calibrated error handling: classify, log with trace_id, abstain on uncertain |
| M13 Temple-Grade | ADR-verified decisions; pytest-testmon incremental runs; `make test` <10s |
| M14 Heritage | Vet records in ADR format; scope declarations mandatory |
| M22 Provenance | GenerateResult.provider_name at receipt; Peta MCP enforces agent never sees raw secrets |
| M23 Failure Integrity | Ruff AST ratchet + pytest-randomly for flake exposure; no `--reruns` masking |
| M24 Venv Sovereignty | `.venv`-only; `--break-system-packages` forbidden; HF_HOME for model cache |
| M25 Streaming Resilience | AnyIO `fail_after` for chunk/timeouts; Peta MCP gateway for agent streaming |

---

## RESEARCH-BACKED FIX PATTERNS FOR EACH P0/P1

### P0-1: M1 Violation — `asyncio.sleep` in `benchmark_hybrid.py`
**Research Pattern**: AnyIO 4.x structured concurrency
```python
# BEFORE (violates M1)
import asyncio
await asyncio.sleep(thermal["cooldown_s"])

# AFTER (AnyIO-native)
import anyio
await anyio.sleep(thermal["cooldown_s"])

# For rate limiting: use anyio.create_task_group with capacity limiter
async def rate_limited_calls(calls, rps):
    async with anyio.create_task_group() as tg:
        limiter = anyio.CapacityLimiter(rps)
        async def limited_call(call):
            async with limiter:
                return await call()
        for call in calls:
            tg.start_soon(limited_call, call)
```

### P0-2: SQLiteVecAdapter.delete() — Stale Table Reference
**Research Pattern**: vec0 metadata columns for collection filtering
```sql
-- Add collection metadata column to vec0 tables
CREATE VIRTUAL TABLE omega_vec_gemma_768 USING vec0(
    embedding float[768],
    collection TEXT,  -- metadata column for filtering
    + content TEXT    -- auxiliary column for payload
);

-- Delete by collection (not hardcoded table)
DELETE FROM omega_vec_gemma_768 WHERE collection = ? AND rowid = ?;
```
**Fix**: Iterate `self._vec_tables_created`, delete from each collection with `WHERE collection = ?`

### P1-1: OOM Protector Silent Swallow
**Research Pattern**: ConsRoute consistency-driven capability matching + evidence-calibrated errors
```python
# BEFORE (violates M9)
try:
    psi_some = anyio.run(psi.get_pressure("some", "avg60"))
except Exception:
    pass  # Silent fail → assumes 0% pressure (opposite of fail-safe)

# AFTER (evidence-calibrated, fail-safe)
import logging
logger = logging.getLogger(__name__)

try:
    psi_some = await anyio.to_thread.run_sync(psi.get_pressure, "some", "avg60")
    psi_full = await anyio.to_thread.run_sync(psi.get_pressure, "full", "avg10")
except Exception as e:
    logger.warning("PSI pressure read failed, treating as THROTTLE (fail-safe)", 
                   extra={"trace_id": trace_id, "error": str(e)})
    return AdmissionDecision.THROTTLE  # Fail-safe: assume pressure, not zero
```

### P1-2: OMEGA_ENGINE.md Self-Contradiction (92% vs 84%)
**Research Pattern**: ADR (Architecture Decision Records) for SSOT integrity
```markdown
# ADR Template (MADR format) for compliance tracking
## Title: Mandate Compliance Status
## Status: Accepted
## Context: Single source of truth must not contradict itself
## Decision: 
- Single compliance % in OMEGA_ENGINE.md §2 table
- Breaker count sourced from single `rg` query in UNOVERENGINEERING_PLAN.md
- Automated CI check: `scripts/verify_ssot_consistency.py`
## Consequences: Any drift fails CI
```

### P1-3: SelectiveHydration.hydrate() — Entity Name Instead of Query
**Research Pattern**: SaR-RAG (2026) — query rewriting/decomposition + selective aggregation
```python
# BEFORE (broken)
def hydrate(self, entity_name: str, ...):
    # Retrieves same L3 principles regardless of query
    principles = self.store.query(entity_name)  # WRONG: entity_name ≠ query

# AFTER (query-aware)
async def hydrate(self, query: str, entity_name: str, ...):
    # 1. Query decomposition for multi-hop
    subqueries = await self.decompose_query(query)
    
    # 2. Selective retrieval per subquery
    all_principles = []
    for sq in subqueries:
        principles = await self.store.query(sq, entity_name=entity_name)
        all_principles.extend(principles)
    
    # 3. Refined reranking (cross-encoder)
    reranked = await self.reranker.rerank(query, all_principles, top_k=15)
    
    # 4. Selective aggregation (knapsack budgeting)
    return self.aggregate_selective(reranked, token_budget=8000)
```

### P2-1: Dead Code (recall.py, miap.py, hivemind_redis.py)
**Research Pattern**: Evidence-calibrated detection (ResearchSquare 2026) + Vulture + pytest-vulture
```bash
# CI Integration
vulture src/ --min-confidence 80 --json > vulture-report.json
pytest --vulture --min-confidence 80 tests/

# Evidence-calibrated: classify as SAFE_TO_REMOVE / POTENTIALLY_DYNAMIC / PUBLIC_API_KEEP
# Abstain on uncertain — don't auto-delete
```

### P2-2: Hardcoded Paths
**Research Pattern**: HF_HOME/HF_HUB_CACHE env vars + cache_dir parameter
```yaml
# config/routing_table.yaml
local_models:
  qwen3-1.7b:
    path: "env:HF_HOME/hub/models--Qwen--Qwen3-1.7B-GGUF/snapshots/<hash>/qwen3-1.7b.gguf"
    # OR use cache_dir in code:
    # model = Llama(model_path=cache_dir / "qwen3-1.7b.gguf", ...)
```

```python
# scripts/benchmark_hybrid.py
from huggingface_hub import hf_hub_download
import os

HF_HOME = Path(os.environ.get("HF_HOME", "~/.cache/huggingface")).expanduser()
MODELS_DIR = HF_HOME / "hub"
```

### P3-1: M2 Firewall — maakali_routing Hardcoded Entities
**Research Pattern**: ADR for architectural exceptions or removal
```markdown
# ADR: MaKaLi Routing in Core Config
## Status: Accepted (or Superseded)
## Context: config/providers.yaml is Core, maakali_routing references WAD entities
## Decision: 
- Option A: Move to WAD config (config/wads/arcana-nova/providers.yaml)
- Option B: Abstract to generic "routing_policy" with entity-agnostic rules
- Option C: Document as accepted exception with ADR
## Consequences: If Option A/B, update ModelGateway to load from WAD
```

---

## NEW AUDIT AREAS TO PROBE (Research-Revealed)

### 1. **Capability Matching Gap**
- Does local model attempt first with reranker evaluation? (ConsRoute pattern)
- Is there a consistency threshold before cloud routing?
- **Probe**: `src/omega/oracle/provider_selector.py` — check for local-first attempt + quality gate

### 2. **Sensitivity Detection Gap**
- Is PII/entity detection implemented for privacy routing? (PRISM pattern)
- Do sensitive requests fail closed (never fall back to cloud)?
- **Probe**: `src/omega/oracle/cascade_router.py` — check for fail-closed on sensitive data

### 3. **Agent Secret Exposure Gap**
- Do agents ever receive raw secrets? (Peta pattern: agents never see raw secrets)
- Is there an MCP gateway mediating secret access?
- **Probe**: `src/omega/oracle/providers.py` — check for raw API keys in agent context

### 4. **Flake Masking Gap**
- Does CI use `--reruns` to mask flakes? (Reject per research)
- Is `pytest-randomly` used to expose state leakage?
- **Probe**: `.github/workflows/` + `Makefile` — check for `--reruns` vs `--randomly-seed`

### 5. **Model Cache Portability Gap**
- Are all model paths using `HF_HOME`/`cache_dir`?
- Does benchmark work on fresh machine without `/media/arcana-novai/...`?
- **Probe**: `config/routing_table.yaml`, `scripts/benchmark_hybrid.py`, `config/models.yaml`

### 6. **Circuit Breaker Factory Gap**
- Is there a single `HealthMonitor.get_breaker()` factory?
- Are all 8 breaker classes consolidated?
- **Probe**: `src/omega/oracle/health_monitor.py` — check for factory pattern

### 7. **VaultCore Bloat Gap**
- Can Peta MCP gateway replace ~2000 lines of custom vault code?
- Do agents use MCP for secret access?
- **Probe**: `src/omega/vault_core.py`, `blindvault_resolver.py`, `enforce_vaultcore.py`

---

## REVISED PRIORITY ORDER (Research-Justified)

| Priority | Task | Research Justification | Effort |
|----------|------|------------------------|--------|
| **P0-1** | Fix M1: `asyncio.sleep` → `anyio.sleep` (3 lines) | AnyIO 4.x structured concurrency mandate | 5 min |
| **P0-2** | Fix SQLiteVecAdapter.delete: multi-collection via metadata | vec0 metadata columns support collection filtering | 30 min |
| **P1-1** | Fix OOM protector: evidence-calibrated fail-safe | ConsRoute fail-safe + M9 error integrity | 20 min |
| **P1-2** | Fix SSOT: ADR format for compliance + automated check | ADR prevents drift; anti-drift architecture | 45 min |
| **P1-3** | Fix SelectiveHydration: query decomposition + SaR-RAG | SaR-RAG 2026: selective aggregation + reranking | 60 min |
| **P1-4** | Add capability matching: local attempt + reranker gate | ConsRoute 2026: consistency-driven routing | 90 min |
| **P1-5** | Add sensitivity detection: PRISM entity-level + fail-closed | PRISM AAAI 2026: privacy routing | 60 min |
| **P2-1** | Dead code: Vulture + evidence-calibrated CI | CleanAI 2026 + ResearchSquare evidence calibration | 45 min |
| **P2-2** | Path portability: HF_HOME + cache_dir everywhere | HF cache env vars standard 2026 | 30 min |
| **P2-3** | Flake exposure: pytest-randomly, remove --reruns | Research: --reruns masks flakes | 15 min |
| **P3-1** | Circuit breaker: PyBreaker factory via HealthMonitor | PyBreaker 2026 async + adaptive thresholds | 60 min |
| **P3-2** | VaultCore → Peta MCP gateway | Peta 2025: agent-native, zero raw secrets | 120 min |
| **P3-3** | M2 firewall: ADR for maakali_routing or move to WAD | ADR format for architectural decisions | 30 min |

---

## TOOLING RECOMMENDATIONS (Research-Backed)

| Need | Tool | Why |
|------|------|-----|
| Dead code detection | **Vulture + pytest-vulture** + evidence-calibrated reporting | Python standard, confidence scoring, CI integration |
| Model cache portability | **huggingface_hub** `hf_hub_download` + `HF_HOME` env | Standard 2026, works across machines |
| Circuit breaker | **PyBreaker 2026** (async, adaptive) | Lightweight, proven, factory pattern |
| Secrets/vault | **Peta MCP Gateway** (peta.io) | Agent-native, zero raw secrets, MCP standard |
| SSOT consistency | **ADR tools** (adr-tools, MADR templates) + custom CI check | Architecture decision records prevent drift |
| Flake detection | **pytest-randomly** + **pytest-instafail** + **pytest-tldr** | Exposes state leakage, instant failures, one-line summary |
| Query-aware RAG | **SaR-RAG pattern**: query decomposition + cross-encoder reranker + knapsack aggregation | 2026 SOTA for selective retrieval |

---

## OUTPUT FORMAT (Enhanced)

Structured Markdown report with **8 sections**:

1. **Executive Summary** — Research-enhanced verdict
2. **Mandate Compliance Matrix** — Updated with research-backed criteria
3. **Critical Violations (MUST FIX)** — P0/P1 with research-backed fix patterns
4. **New Audit Areas Probed** — 7 new gaps with evidence
5. **Un-overengineering Targets** — Consolidated with tooling recommendations
6. **Concurrency & Safety Risks** — Enhanced with research patterns
7. **Technical Debt Inventory** — Prioritized with research justification
8. **Recommendations Priority Order** — 13-item list with research citations

**Response Frontmatter (REQUIRED)**:
```yaml
---
account: arcana.novai@gmail.com
pack_version: 2026-08-16
pack_profile: hybrid-benchmark-strategy
pack_files: 44
pack_tokens: 247762
session_date: 2026-08-16
session_type: audit
research_enhanced: true
research_doc: docs/research/R_AUDIT_GAPS_DEEP_RESEARCH_20260816.md
---
```

---

## KEY PRINCIPLE (Reinforced)

**Evidence over opinion.** Every finding must cite:
1. Specific file + line range from XML bundles
2. Research source (URL + date) for the recommended pattern
3. Mandate reference (M1-M27)

"It looks like" is not acceptable. "Research shows [source] that [pattern] solves this" is required.

---

*Upload the 11 XML bundles from `generated/` to Claude.ai Projects. Paste `CLAUDE_PROJECT_SYSTEM_PROMPT.md` → Custom Instructions. Paste THIS prompt → First message in chat.*