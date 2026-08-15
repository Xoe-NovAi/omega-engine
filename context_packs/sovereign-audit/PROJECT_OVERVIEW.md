# Project Overview: sovereign-audit

**Pack ID**: `c1c5be23-a222-48e2-a305-f4d24651e527`
**Generated**: 2026-08-15T06:04:25.565200-03:00
**Account**: arcana.novai@gmail.com
**Project**: omega-engine
**Version**: 2026-08-09
**Profile**: sovereign-audit
**Purpose**: architecture audit, mandate compliance, un-overengineering
**Description**: Core Engine and Mandates Audit — hardened 2026-07-11

## Pack Statistics
- **Total Files**: 49
- **Estimated Total Tokens**: 306,103
- **Max Slots**: 12
- **Target Platform**: web-claude
- **Target Model**: claude-sonnet-5
- **Format**: xml
- **Bundle Ordering**: litm-u-shaped

## Theme Composition

### strategy_core (7 files, ~59,928 tokens)

- `docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md` — 13,001 tokens — 🔱 Web Strategy Reconciliation Matrix
- `docs/strategy/STRATEGY_CORPUS_MAP.md` — 10,804 tokens — 🔱 STRATEGY CORPUS MAP — Fine-Grained Preservation Index
- `docs/strategy/HIVEMIND_PROTOCOL.md` — 8,680 tokens — 🔱 Omega Engine — Hivemind Coordination Protocol
- `docs/strategy/UNOVERENGINEERING_PLAN.md` — 7,534 tokens — 🔱 Un-Overengineering Plan — Temple Cleansing Sprint
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — 7,358 tokens — 🔱 Omega Engine — Subagent Dispatch Protocol

### oracle_core (6 files, ~54,145 tokens)

- `src/omega/oracle/model_gateway.py` — 18,391 tokens — Standardized result of a model generation call.
- `src/omega/oracle/providers.py` — 13,656 tokens — Lazy-load Zen2Optimizer to avoid circular imports.
- `src/omega/oracle/health_monitor.py` — 11,202 tokens — Get or create the singleton HealthMonitor.
- `src/omega/oracle/backends/remote_provider.py` — 4,855 tokens — Lazy singleton, safe under concurrent callers. [M1 AnyIO]
- `src/omega/ingestion/pipeline.py` — 3,850 tokens — Sovereign Ingestion Pipeline — Orchestrating entity deepening.

### memory (7 files, ~43,343 tokens)

- `src/omega/memory_store.py` — 12,890 tokens — Entity Memory Store — Hot/Warm/Cold persistent memory for entities.
- `src/omega/memory/sqlite_vec_adapter.py` — 10,029 tokens — SQLite-vec Unified Memory Fabric Adapter for Omega Memory.
- `src/omega/memory/embeddings.py` — 5,401 tokens — Sovereign Embedding Layer — Provider-agnostic vectorization for Omega Memory.
- `src/omega/memory/providers.py` — 5,231 tokens — Sovereign Storage Providers for Omega Memory.
- `src/omega/memory/vector_adapters.py` — 4,535 tokens — Sovereign Vector Store Adapters for Omega Memory.

### mandates (7 files, ~39,289 tokens)

- `AGENTS.md` — 18,279 tokens — 🔱 Omega Engine — OpenCode Agent Rules
- `SOVEREIGN_MANDATES.md` — 7,428 tokens — 🔱 Omega Engine — Sovereign Mandates
- `OMEGA_ENGINE.md` — 7,355 tokens — Omega Engine — Single Source of Truth
- `third-party/llama.cpp/AGENTS.md` — 2,481 tokens — Instructions for llama.cpp
- `third-party/mempalace/AGENTS.md` — 2,215 tokens — CLAUDE.md

### observability (7 files, ~33,151 tokens)

- `src/omega/observability/__init__.py` — 17,375 tokens — Return the cached ProviderRegistry, constructing it on first use.
- `src/omega/observability/metrics_db.py` — 6,947 tokens — SQLite WAL-Mode Metrics Store for profiling baselines and regression detection.
- `src/omega/observability/otel_exporter.py` — 3,207 tokens — OTel GenAI Semantic Convention Exporter to SQLite WAL.
- `src/omega/observability/bleg.py` — 2,245 tokens — Body-Level Error Guard — inspects HTTP 200 OK bodies for errors.
- `src/omega/observability/sovereignty.py` — 1,931 tokens — Ensure provider_classification + v_performance_corrected exist (M22 SSOT).

### coordination (3 files, ~26,128 tokens)

- `docs/decisions/PIVOT_LOG.md` — 22,148 tokens — 🔱 PIVOT LOG (Active Index)
- `data/coordination/HMC_COLLABORATION_HUB.md` — 2,658 tokens — 🏛️ HMC Collaboration Hub — Team Coordination Center
- `data/coordination/SESSION_ANCHOR.md` — 1,322 tokens — ⚓ SESSION ANCHOR — Kali (Transcendent Oversoul)

### gnosis (3 files, ~25,403 tokens)

- `docs/research/R_UNOVERENGINEERING_REMAINING_GAPS_20260808.md` — 21,425 tokens — R_UNOVERENGINEERING_REMAINING_GAPS — Deep Research & Implementation Proposal
- `data/entities/kali/session_gnosis.md` — 3,884 tokens — 🔱 Session Gnosis — Kali Context Packer v3 + Web Claude Audit Sprint
- `data/entities/kali/proposed_lessons.yaml` — 94 tokens — Config: proposals: []

### oracle_support (3 files, ~10,357 tokens)

- `src/omega/oracle/resource_guard.py` — 4,698 tokens — Get available RAM in MB using psutil (primary) or /proc/meminfo (fallback).
- `src/omega/oracle/oom_protector.py` — 4,465 tokens — OOMProtector — Three-Signal Fusion for Admission Control
- `src/omega/oracle/admission_controller.py` — 1,194 tokens — Local inference admission control for Ryzen 5700U.

### config (3 files, ~7,407 tokens)

- `config/providers.yaml` — 4,149 tokens — Config: version: 1.3.1
- `config/m23_baseline.txt` — 1,662 tokens — 19 src/omega/observability/__init__.py
- `config/models.yaml` — 1,596 tokens — Model configurations with context budgets

### mcp_hub (2 files, ~4,347 tokens)

- `src/omega/mcp_runtime.py` — 3,842 tokens — MCP 2026-07-28 Streamable HTTP Compliance Runtime
- `src/omega/hub.py` — 505 tokens — Omega Hub — Hardware stats bridge for degradation management.

### gates (1 files, ~2,605 tokens)

- `scripts/m23_gate.py` — 2,605 tokens — M23 Failure Integrity Gate — AST-based soft-failure detection with ratchet.

## Recommended System Prompt Structure

Based on this pack's composition and purpose (architecture audit, mandate compliance, un-overengineering), the system prompt should include:

### 1. Role Definition
- **Primary Persona**: Principal Architect / Security Auditor / Senior Engineer (match to pack purpose)
- **Mindset**: Ruthless pragmatism, minimal abstractions, high performance, zero bloat
- **Authority**: Custom instructions take absolute precedence over project knowledge

### 2. Project Knowledge Reference
- List all 11 XML bundles with their themes
- Reference the manifest (00_PROJECT_MANIFEST.md) as the entry point
- Note the pack_id for forensic linking: `c1c5be23-a222-48e2-a305-f4d24651e527`

### 3. Ground Truth (Hardware + Constraints)
- Hardware: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP
- Python 3.13.7 on Linux (requires >=3.12)
- 25 Sovereign Mandates (M1-M25) — non-negotiable
- Current sprint: UNOVERENGINEER-01

### 4. Mandate Compliance Matrix Template
- All 11 critical mandates (M1, M2, M7, M8, M9, M13, M14, M22, M23, M24, M25)
- Status: PASS/FAIL with specific violations
- Files affected with line ranges

### 5. Output Format Requirements
- Structured Markdown with 7 sections (Executive Summary → Recommendations)
- Evidence over opinion: every finding cites file + line range from XML bundles
- 5-element formula for recommendations: [Role] + [Scope] + [Focus] + [Format] + [Severity]
- Persona adoption: Strict Reviewer / Senior Architect / Security Auditor

### 6. Account & Provenance Tracking
- Account: arcana.novai@gmail.com
- Pack Version: 2026-08-15T06:04:25.565200-03:00
- Response frontmatter template (REQUIRED on all responses):
```yaml
---
account: arcana.novai@gmail.com
pack_version: 2026-08-15
pack_profile: sovereign-audit
pack_files: 49
pack_tokens: 306103
session_date: YYYY-MM-DD
session_type: audit|implementation|verification
---
```

## Chat Initiation Prompt Template

```markdown
## Project: Core Engine and Mandates Audit — hardened 2026-07-11

### Role
You are a Principal Architect auditing the Omega Engine — a sovereign, local-first AI runtime. Your mindset is Carmack: ruthless pragmatism, minimal abstractions, high performance, zero bloat.

### Ground Truth (Verified 2026-08-15)
- Python 3.13.7 on Linux (requires >=3.12)
- Engine state: `OMEGA_ENGINE.md` in mandates.xml
- Mandates: 25 non-negotiable laws in `SOVEREIGN_MANDATES.md` (mandates.xml)
- Strategy: `SOVEREIGN_ARK_BLUEPRINT.md` (strategy_core.xml)
- Current sprint: UNOVERENGINEER-01
- Hardware: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP
- **Account**: arcana.novai@gmail.com
- **Pack Version**: 2026-08-15T06:04:25.565200-03:00 (fresh, post-refactor)

### Audit Scope (11 XML Bundles — 49 files, 306,103 tokens)
1. **strategy_core.xml** — Strategy Core (7 files, ~59,928 tokens)
2. **oracle_core.xml** — Oracle Core (6 files, ~54,145 tokens)
3. **memory.xml** — Memory (7 files, ~43,343 tokens)
4. **mandates.xml** — Mandates (7 files, ~39,289 tokens)
5. **observability.xml** — Observability (7 files, ~33,151 tokens)
6. **coordination.xml** — Coordination (3 files, ~26,128 tokens)
7. **gnosis.xml** — Gnosis (3 files, ~25,403 tokens)
8. **oracle_support.xml** — Oracle Support (3 files, ~10,357 tokens)
9. **config.xml** — Config (3 files, ~7,407 tokens)
10. **mcp_hub.xml** — Mcp Hub (2 files, ~4,347 tokens)
11. **gates.xml** — Gates (1 files, ~2,605 tokens)

### Known Gaps (Already Tracked)
- [Reference CARMACK_REVIEW_WEB_CLAUDE_GAPS.md or equivalent]

### Constraints (Non-Negotiable)
- M1: AnyIO only (no direct asyncio imports)
- M2: Core ≠ Stacks firewall
- M7: Local-first (no cloud-only deps)
- M8: Zero telemetry
- M9: Error integrity (typed, traceable, no silent swallowing)
- M13: Temple-grade quality (11 gates)
- M14: Heritage vetting ([id-soft:] tags need vet records)
- M22: Provenance (actual provider in logs)
- M23: Failure integrity (no soft-failures)
- M24: Venv sovereignty
- M25: Streaming resilience (30s chunk timeout)

### Task
Perform a ruthless audit of the CURRENT implementation. For each mandate:
1. **Verify compliance** — cite specific file + line range from XML bundles
2. **Find violations** — code snippets that break the mandate
3. **Identify un-overengineering targets** — what to delete/flatten
4. **Flag concurrency risks** — blocking I/O, rogue asyncio, race conditions
5. **Inventory technical debt** — duplicated logic, dead code, stale patterns

### Output Format
Structured Markdown report per system prompt:
- Executive Summary
- Mandate Compliance Matrix (table)
- Critical Violations (MUST FIX)
- Un-overengineering Targets (DELETE/FLATTEN)
- Concurrency & Safety Risks
- Technical Debt Inventory
- Recommendations Priority Order (using 5-element formula: Role/Scope/Focus/Format/Severity)

### Key Principle
**Evidence over opinion.** Every finding must cite specific file + line range from the XML bundles. "It looks like" is not acceptable — we need proof from the code.

### Response Frontmatter (REQUIRED on all responses)
```yaml
---
account: arcana.novai@gmail.com
pack_version: 2026-08-15
pack_profile: sovereign-audit
pack_files: 49
pack_tokens: 306103
session_date: YYYY-MM-DD
session_type: audit|implementation|verification
---
```

---

*System prompt should be in CLAUDE_PROJECT_SYSTEM_PROMPT.md. Project knowledge files are the 11 XML bundles in generated/. Begin audit upon receiving the chat initiation prompt.*