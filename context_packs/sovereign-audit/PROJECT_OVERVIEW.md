# Project Overview: sovereign-audit

**Pack ID**: `b70cdf7c-ad48-442e-8d8d-75c180a6548f`
**Generated**: 2026-08-09T10:34:33.059764-03:00
**Account**: arcana.novai@gmail.com
**Project**: omega-engine
**Version**: 2026-08-09
**Profile**: sovereign-audit
**Purpose**: architecture audit, mandate compliance, un-overengineering
**Description**: Core Engine and Mandates Audit — hardened 2026-07-11

## Pack Statistics
- **Total Files**: 39
- **Estimated Total Tokens**: 217,990
- **Max Slots**: 12
- **Target Platform**: web-claude
- **Target Model**: claude-sonnet-5
- **Format**: xml
- **Bundle Ordering**: litm-u-shaped

## Theme Composition

### strategy_core (7 files, ~59,303 tokens)

- `docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md` — 13,001 tokens — 🔱 Web Strategy Reconciliation Matrix
- `docs/strategy/STRATEGY_CORPUS_MAP.md` — 10,786 tokens — 🔱 STRATEGY CORPUS MAP — Fine-Grained Preservation Index
- `docs/strategy/HIVEMIND_PROTOCOL.md` — 8,451 tokens — 🔱 Omega Engine — Hivemind Coordination Protocol
- `docs/strategy/UNOVERENGINEERING_PLAN.md` — 7,534 tokens — 🔱 Un-Overengineering Plan — Temple Cleansing Sprint
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — 7,173 tokens — 🔱 Omega Engine — Subagent Dispatch Protocol

### oracle_core (4 files, ~46,257 tokens)

- `src/omega/oracle/model_gateway.py` — 20,411 tokens — Standardized result of a model generation call.
- `src/omega/oracle/providers.py` — 13,656 tokens — Lazy-load Zen2Optimizer to avoid circular imports.
- `src/omega/oracle/health_monitor.py` — 11,139 tokens — Get or create the singleton HealthMonitor.
- `src/omega/oracle/provider_registry.py` — 1,051 tokens — Single source of truth for provider capability metadata (M7/M22).

### memory (7 files, ~42,001 tokens)

- `src/omega/memory_store.py` — 12,866 tokens — Entity Memory Store — Hot/Warm/Cold persistent memory for entities.
- `src/omega/memory/sqlite_vec_adapter.py` — 9,742 tokens — SQLite-vec Unified Memory Fabric Adapter for Omega Memory.
- `src/omega/memory/embeddings.py` — 5,401 tokens — Sovereign Embedding Layer — Provider-agnostic vectorization for Omega Memory.
- `src/omega/memory/providers.py` — 4,590 tokens — Sovereign Storage Providers for Omega Memory.
- `src/omega/memory/vector_adapters.py` — 4,535 tokens — Sovereign Vector Store Adapters for Omega Memory.

### mandates (7 files, ~36,606 tokens)

- `AGENTS.md` — 16,456 tokens — 🔱 Omega Engine — OpenCode Agent Rules
- `OMEGA_ENGINE.md` — 7,355 tokens — Omega Engine — Single Source of Truth
- `SOVEREIGN_MANDATES.md` — 6,568 tokens — 🔱 Omega Engine — Sovereign Mandates
- `third-party/llama.cpp/AGENTS.md` — 2,481 tokens — Instructions for llama.cpp
- `third-party/mempalace/AGENTS.md` — 2,215 tokens — CLAUDE.md

### oracle_support (3 files, ~10,385 tokens)

- `src/omega/oracle/resource_guard.py` — 4,726 tokens — Get available RAM in MB using psutil (primary) or /proc/meminfo (fallback).
- `src/omega/oracle/oom_protector.py` — 4,465 tokens — OOMProtector — Three-Signal Fusion for Admission Control
- `src/omega/oracle/admission_controller.py` — 1,194 tokens — Local inference admission control for Ryzen 5700U.

### observability (5 files, ~10,070 tokens)

- `src/omega/observability/metrics_db.py` — 4,839 tokens — SQLite WAL-Mode Metrics Store for profiling baselines and regression detection.
- `src/omega/observability/bleg.py` — 2,245 tokens — Body-Level Error Guard — inspects HTTP 200 OK bodies for errors.
- `src/omega/observability/sovereignty.py` — 1,540 tokens — Query the local vs cloud inference ratio from MetricsDB.
- `src/omega/observability/latency_tracker.py` — 830 tokens — Sovereign Latency Tracker — Time-series monitoring for provider performance.
- `src/omega/observability/context.py` — 616 tokens — Get current trace_id or generate a new one.

### config (3 files, ~7,510 tokens)

- `config/providers.yaml` — 4,249 tokens — Config: version: 1.3.1
- `config/m23_baseline.txt` — 1,665 tokens — 21 src/omega/observability/__init__.py
- `config/models.yaml` — 1,596 tokens — Model configurations with context budgets

### mcp_hub (2 files, ~4,347 tokens)

- `src/omega/mcp_runtime.py` — 3,842 tokens — MCP 2026-07-28 Streamable HTTP Compliance Runtime
- `src/omega/hub.py` — 505 tokens — Omega Hub — Hardware stats bridge for degradation management.

### gates (1 files, ~1,511 tokens)

- `scripts/m23_gate.py` — 1,511 tokens — M23 Failure Integrity Gate — AST-based soft-failure detection with ratchet.

## Recommended System Prompt Structure

Based on this pack's composition and purpose (architecture audit, mandate compliance, un-overengineering), the system prompt should include:

### 1. Role Definition
- **Primary Persona**: Principal Architect / Security Auditor / Senior Engineer (match to pack purpose)
- **Mindset**: Ruthless pragmatism, minimal abstractions, high performance, zero bloat
- **Authority**: Custom instructions take absolute precedence over project knowledge

### 2. Project Knowledge Reference
- List all 9 XML bundles with their themes
- Reference the manifest (00_PROJECT_MANIFEST.md) as the entry point
- Note the pack_id for forensic linking: `b70cdf7c-ad48-442e-8d8d-75c180a6548f`

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
- Pack Version: 2026-08-09T10:34:33.059764-03:00
- Response frontmatter template (REQUIRED on all responses):
```yaml
---
account: arcana.novai@gmail.com
pack_version: 2026-08-09
pack_profile: sovereign-audit
pack_files: 39
pack_tokens: 217990
session_date: YYYY-MM-DD
session_type: audit|implementation|verification
---
```

## Chat Initiation Prompt Template

```markdown
## Project: Core Engine and Mandates Audit — hardened 2026-07-11

### Role
You are a Principal Architect auditing the Omega Engine — a sovereign, local-first AI runtime. Your mindset is Carmack: ruthless pragmatism, minimal abstractions, high performance, zero bloat.

### Ground Truth (Verified 2026-08-09)
- Python 3.13.7 on Linux (requires >=3.12)
- Engine state: `OMEGA_ENGINE.md` in mandates.xml
- Mandates: 25 non-negotiable laws in `SOVEREIGN_MANDATES.md` (mandates.xml)
- Strategy: `SOVEREIGN_ARK_BLUEPRINT.md` (strategy_core.xml)
- Current sprint: UNOVERENGINEER-01
- Hardware: Ryzen 5 4600H, 16GB RAM, no GPU, 15W TDP
- **Account**: arcana.novai@gmail.com
- **Pack Version**: 2026-08-09T10:34:33.059764-03:00 (fresh, post-refactor)

### Audit Scope (9 XML Bundles — 39 files, 217,990 tokens)
1. **strategy_core.xml** — Strategy Core (7 files, ~59,303 tokens)
2. **oracle_core.xml** — Oracle Core (4 files, ~46,257 tokens)
3. **memory.xml** — Memory (7 files, ~42,001 tokens)
4. **mandates.xml** — Mandates (7 files, ~36,606 tokens)
5. **oracle_support.xml** — Oracle Support (3 files, ~10,385 tokens)
6. **observability.xml** — Observability (5 files, ~10,070 tokens)
7. **config.xml** — Config (3 files, ~7,510 tokens)
8. **mcp_hub.xml** — Mcp Hub (2 files, ~4,347 tokens)
9. **gates.xml** — Gates (1 files, ~1,511 tokens)

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
pack_version: 2026-08-09
pack_profile: sovereign-audit
pack_files: 39
pack_tokens: 217990
session_date: YYYY-MM-DD
session_type: audit|implementation|verification
---
```

---

*System prompt should be in CLAUDE_PROJECT_SYSTEM_PROMPT.md. Project knowledge files are the 9 XML bundles in generated/. Begin audit upon receiving the chat initiation prompt.*