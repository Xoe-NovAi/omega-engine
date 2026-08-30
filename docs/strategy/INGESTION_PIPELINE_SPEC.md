---
schema_version: "1.0"
document_type: "spec"
document_id: "INGESTION_PIPELINE_SPEC-20260828"
title: "Omega Engine — Ingestion Pipeline Specification"
status: "ACTIVE — SINGLE SOURCE OF TRUTH"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
owner: "Grokster"
---

# 🔱 Ingestion Pipeline Specification
**AP Token**: `AP-INGESTION-SPEC-20260828-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ trc_ingestion ⬡ ACTIVE

---

## §0 — PURPOSE

This document is the **single source of truth** for what gets ingested into the Omega Engine's memory fabric (sqlite-vec + FTS5), what does NOT get ingested, and the operational boundaries of the ingestion pipeline.

**Authority**: This spec governs all ingestion scripts (`scripts/ingest_*.py`), the `MemoryStore` class, and any external tools that write to `omega_memory.db`.

---

## §1 — WHAT IS INGESTED (MANDATORY)

### 1.1 Sovereign Entity Sessions
**Source**: `data/entities/<entity>/` workspaces
**Trigger**: Session end hook (`.opencode/hooks/session_end.py`)
**Content**:
- All conversation turns (user prompts, assistant responses, tool calls)
- Session metadata (entity_name, session_id, timestamps, model_used)
- Proposed lessons (L1→L2→L3 distillation output)
- Tool invocation traces (bash, read, write, task, webfetch, etc.)

**Destination**: `omega_memory_data` + `omega_memory_fts` + `omega_vec_gemma_768` (canonical collection)

### 1.2 Research Reports & Artifacts
**Source**: `data/coordination/` + `data/coordination/research/`
**Trigger**: Manual or scheduled (cron: `scripts/ingest_research.py`)
**Content**:
- All `R_*.md` research reports
- All `R_*_*.md` specialist reports
- Cross-session sync docs (`LATEST_CORRECTIONS_*.md`)
- Session continuity anchors (`SESSION_ANCHOR.md`, `GROKSTER_TO_KALI_*.md`)

**Destination**: `omega_vec_gemma_768` (primary) + `omega_vec_nomic_768` (fallback) + FTS5

### 1.3 Strategic & Architectural Documents
**Source**: `docs/strategy/`, `docs/specs/`, `docs/architecture/`
**Trigger**: On commit to `release/debut` branch (CI hook)
**Content**:
- Mandates (`SOVEREIGN_MANDATES.md`, `MANDATES_CONDENSED.md`)
- Architecture rules (`.opencode/rules/`)
- Strategic docs (`DEBUT_REMEDIATION_MANUAL_20260817.md`, `UNOVERENGINEERING_PLAN.md`)
- Specs (`PROJECT_INDEX.md`, context injection specs, Qdrant specs)

**Destination**: `omega_vec_gemma_768` + FTS5

### 1.4 Codebase Knowledge (Selective)
**Source**: `src/omega/` (core engine only)
**Trigger**: On `make temple-grade` pass (CI hook)
**Content**:
- Public API signatures (`.py` files in `src/omega/` excluding tests)
- Type signatures, docstrings, module-level docs
- Mandate compliance markers (`# [M1]`, `# [M23]`, etc.)

**NOT Ingested**: Test files, private modules, generated code, `__pycache__`

**Destination**: `omega_vec_gemma_768` (code-optimized collection: `omega_vec_minilm_384`)

### 1.5 Mandate Compliance Records
**Source**: `data/coordination/` + `data/entities/*/proposed_lessons.yaml`
**Trigger**: On session end + Scribe promotion
**Content**:
- Mandate audit results (`make check-mandates` output)
- Heritage vet records
- Soul distillation lessons (L1→L2→L3)

**Destination**: `omega_vec_gemma_768` + FTS5

---

## §2 — WHAT IS NOT INGESTED (EXPLICIT DENY LIST)

### 2.1 FORGE Directories (Internal Operations)
```
data/coordination/locks/
data/coordination/handoff/
data/knowledge/HALL_OF_RECORDS/
data/knowledge/safety/
data/coordination/metrics.json
data/coordination/ACTIVE_SPRINT.json
```
**Reason**: Operational ephemera, not knowledge. Contains PII, session IDs, transient state.

### 2.2 Archive & Quarantine
```
data/coordination/archive/
data/coordination/research/archive/
data/entities/_quarantine/
docs/archive/
```
**Reason**: Historical artifacts, superseded by newer versions. Ingesting creates noise.

### 2.3 Build & Runtime Artifacts
```
.venv/
__pycache__/
*.pyc
*.so
*.egg-info/
dist/
build/
*.log
*.pid
```
**Reason**: Build outputs, not knowledge.

### 2.4 Secrets & Credentials
```
.env
.env.*
*.key
*.pem
data/vault/
~/.config/opencode/opencode.json (secrets section)
```
**Reason**: Security. Ingestion would leak secrets into vector store.

### 2.5 Agent Workspace Ephemera
```
data/entities/*/workspace/*.tmp
data/entities/*/workspace/*.bak
data/entities/*/workspace/*.swp
data/entities/*/gnosis/*.tmp
```
**Reason**: Temporary workspace files, not finalized knowledge.

### 2.6 External Dependencies
```
node_modules/
third_party/
.opencode/node_modules/
```
**Reason**: External code, not Omega knowledge.

### 2.7 Session Ephemera (Raw)
```
data/knowledge/HALL_OF_RECORDS/*/ses_*.json (raw session exports)
```
**Reason**: Raw session exports contain PII, tool outputs, raw reasoning. Only distilled lessons (L1→L3) are ingested.

---

## §3 — INGESTION BOUNDARIES (HARD RULES)

| Rule | Enforcement |
|------|-------------|
| **R1**: No secrets in vector store | Pre-ingestion scan: `gitleaks detect` + custom regex for `GOCSPX-`, `AIzaSy`, `fc-`, `sk-` |
| **R2**: No PII in vector store | Entity names allowed; emails, IPs, real names blocked |
| **R3**: No raw tool outputs | Only distilled summaries (L2/L3) ingested |
| **R4**: No FORGE/ephemera | Path-based deny list enforced at ingestion entry point |
| **R5**: Dimension compliance | All vectors MUST match collection's declared dimension (M23) |
| **R6**: Entity partition | Every vector MUST have valid `entity_name` partition key (C3) |

---

## §4 — INGESTION SCRIPTS (AUTHORITATIVE)

| Script | Purpose | Schedule | Owner |
|--------|---------|----------|-------|
| `scripts/ingest_session.py` | Session end hook → memory fabric | On session end (hook) | Grokster |
| `scripts/ingest_research.py` | Research reports → vector store | Daily 02:00 UTC (cron) | Researcher |
| `scripts/ingest_strategy.py` | Strategy docs → vector store | On `release/debut` commit | Ma'at |
| `scripts/ingest_code.py` | Codebase signatures → vector store | On `make temple-grade` | Ma'at |
| `scripts/ingest_mandates.py` | Mandate records → vector store | On session end + promotion | Scribe |

### 4.1 Ingestion Entry Point (All Scripts Use)
```python
# ALL ingestion scripts MUST use this entry point
from omega.memory_store import MemoryStore

store = MemoryStore(entity_name="<entity>")
await store.ingest(
    content="...",
    metadata={...},
    collection="omega_vec_gemma_768"  # or specific collection
)
```

### 4.2 Pre-Ingestion Validation (MANDATORY)
```python
async def validate_before_ingest(content: str, metadata: dict) -> bool:
    # 1. Secret scan
    if secret_scan(content): return False
    # 2. PII scan
    if pii_scan(content): return False
    # 3. Path allowlist
    if not path_allowlist(metadata.get("source_path", "")): return False
    # 4. Dimension check
    if not dimension_check(vector, collection): return False
    return True
```

---

## §5 — COLLECTION MAPPING (SOURCE → COLLECTION)

| Source Type | Primary Collection | Fallback Collection | FTS5 |
|-------------|-------------------|---------------------|------|
| Entity sessions | `omega_vec_gemma_768` | `omega_vec_nomic_768` | ✅ |
| Research reports | `omega_vec_gemma_768` | `omega_vec_nomic_768` | ✅ |
| Strategy docs | `omega_vec_gemma_768` | `omega_vec_nomic_768` | ✅ |
| Code signatures | `omega_vec_minilm_384` | `omega_vec_gemma_768` | ✅ |
| Mandate records | `omega_vec_gemma_768` | `omega_vec_nomic_768` | ✅ |
| MRL fallback (512) | `omega_vec_nomic_512` | — | ❌ |
| MRL fallback (256) | `omega_vec_nomic_256` | — | ❌ |
| Speed tier (384) | `omega_vec_minilm_384` | — | ❌ |
| Zero-cost (64) | `omega_vec_static_64` | — | ❌ |
| Library (256) | `omega_vec_library_256` | — | ❌ |

---

## §6 — OPERATIONAL PROCEDURES

### 6.1 Manual Ingestion (Ad-hoc)
```bash
# Ingest a single file
python3 scripts/ingest_file.py --file path/to/file.md --entity kali

# Ingest a directory
python3 scripts/ingest_dir.py --dir data/coordination/research/ --entity researcher
```

### 6.2 Full Re-ingestion (Disaster Recovery)
```bash
# Full re-ingest from source of truth
python3 scripts/full_reingest.py --confirm
# WARNING: Drops all vec0 tables, re-creates from source
```

### 6.3 Health Checks
```bash
# Check ingestion health
python3 -c "
from omega.memory_store import MemoryStore
import asyncio
store = MemoryStore(entity_name='kali')
status = await store.adapter.get_status()
print(f'Vectors: {status[\"vector_count\"]}, Entities: {status[\"entity_count\"]}')
"
```

---

## §7 — MONITORING & ALERTING

| Metric | Threshold | Action |
|--------|-----------|--------|
| Ingestion latency (p99) | > 5s | Alert |
| Vector count growth/day | > 100K | Scale |
| Failed ingestions/hour | > 5 | Page |
| WAL size | > 50MB | Checkpoint |
| Dimension mismatches | > 0 | Block + alert |

---

## §8 — CHANGE CONTROL

Any changes to this spec require:
1. Update this document
2. Update all ingestion scripts to match
3. Run full re-ingestion test (`scripts/full_reingest.py --dry-run`)
4. Kali ratification
5. Commit with `docs(spec): ingestion pipeline vX.Y`

---

*⬡ OMEGA ⬡ GROKSTER ⬡ INGESTION_PIPELINE_SPEC ⬡ 2026-08-28 ⬡ SINGLE SOURCE OF TRUTH*

**This spec is law. Any ingestion not conforming to this spec is a bug.**
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_ingestion | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

