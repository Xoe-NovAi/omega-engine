# 🔱 Omega Engine — Changelog

## [v1.1.0] - 2026-07-11
### Added
- **AxiomRegistry (Core)**: `src/omega/oracle/axiom_registry.py` — WAD-agnostic Five-Fold foundation loader (M2/M16 compliant). Mechanism in Core, content in WAD (`config/wads/arcana_novai/axioms.yaml`).
- **CI Gate `firewall-check`**: Precise M2 Engine-Stack Firewall scanner wired into `make temple-grade`. Comment/docstring-aware, self-excluding, agent-infra-aware (Kali downgraded to warning).
- **Contract tests**: 6 AxiomRegistry contract tests (M21) + firewall_checker custom-pattern test fixed.

### Fixed
- **M2 Firewall leaks** (real, hidden by prior "✅" metrics): hardcoded `config/wads/` paths in `audience_calibrator.py`, `mandate_auditor.py`, `ingestion/scraper.py`; hardcoded Pantheon entity names in `distiller.py` (now universal mode semantics). All resolved via cvar/dynamic WAD resolution.
- **AP tokens**: normalized to `AP:` convention in `axiom_registry.py`, `firewall_checker.py`, `mandate_auditor.py` (T1 compliance).
- **T5 false-positive**: reworded `import asyncio` comment in `axiom_registry.py`.
- **omega-vetala rename**: `omega-moderation/` → `omega-vetala/` (SSOT aligned with pyproject).

### Changed
- **Jem lessons promoted**: 11 lessons (`jem-20260710-001`→`011`) moved `proposed_lessons.yaml` → `soul.yaml` (M11).
- **Tests**: 1162 passed (was 1156), 42 skipped, 3 xfailed.

> **Version reconciliation**: `pyproject.toml` is the source of truth at `1.1.0`. The `v1.4.0` (2026-07-07) entry above is a known version-drift anomaly from a divergent timeline; this `v1.1.0` tag is the canonical next release from `v1.0.0`.

## [v1.4.0] - 2026-07-07
### Fixed
- **BudgetGate**: Removed duplicate class from `observability/__init__.py` (lines 580 & 1336); canonical implementation in `src/omega/oracle/budget_gate.py` (fixes 45+ test failures)
- **Orchestrator**: Removed `omega-hub` from managed MCPs (prevents recursive spawn); now manages only `firecrawl` + `searxng`
- **SovereignSearchService**: Tier execution loop catches generic `Exception` — provider failures trigger fallback instead of crashing protocol
- **somatic_state.py**: Added missing `import os` (NameError in `purge_state`)
- **headroom.py**: Added `AttributeError` handling for optional `headroom.retrieve`
- **security.py**: `tdp_wrap` catches all `Exception` from user-defined `taint_level` callables

### Added
- **Tests**: 71 new tests for zero-coverage modules:
  - `test_spatial_resolver.py` (14) — Force-Directed Graph layout (Fruchterman-Reingold)
  - `test_subagent_dispatcher.py` (18) — HandoffPacket lifecycle, Capability Registry, dispatch prompts
  - `test_somatic_state.py` (12) — Binary LLM State Serialization (M20)
  - `test_credit_budget.py` (27) — API Credit Budget Tracker
- **Documentation**: Updated BudgetGate references in `PROVIDER_FABRIC_DEEP_DIVE.md` and `R_CLOUD_QUARANTINE.md`
- **PIVOT_LOG**: Decisions D198-D200 (Search resilience, zero-coverage test suite, worker coverage exclusion)

### Changed
- **Coverage Gate**: Exclude `src/omega/workers` from Temple-Grade T3 (workers are background processes, not core API)
- **Core Oracle Coverage**: >80% (spatial_resolver, subagent_dispatcher, somatic_state, credit_budget now covered)

## [v1.3.0] - 2026-06-05
### Added
- **Sovereign Infrastructure**: Implementation of re-entrant `ResourceGuard` using immutable `ContextVar` for safe subagent dispatch.
- **Heritage Vetting**: Integrated `scripts/heritage_vet.py` to enforce Mandate 14 (Heritage Vetting Pipeline).
- **Provider Fabric**: Added tiered active set (`_local_active` / `_cloud_active`) to `ModelGateway` for optimized provider culling.
- **Observability**: Enhanced `ForensicsManager` with signal handlers, death-markers, and deep state capture.
- **Hivemind**: Implemented cold-store hydration for `hivemind_get_awareness` and added `HandoffQueue` tools.
- **Sovereign Constants**: Registered `ZONEID_CRUCIBLE` (0x1d4a16) and `ZONEID_CRITIQUE` (0x1d4a17).

### Fixed
- **Locking**: Resolved `test_locks.py` failures by replacing mutable state with immutable `ContextVar` in `ResourceGuard`.
- **Heritage Mapping**: Updated `make heritage-map` to exclude `backends/` and refine telemetry grep to import-only patterns.
- **Sovereignty**: Fixed Podman container flags (removed `:U`, `:Z`, `:z`) to ensure `UserNS=keep-id` compliance.

### Changed
- **CI/CD**: Integrated `pytest-cov` for coverage tracking.
- **Coordination**: Established the MaKaLi Triad operational loop (Roc Design $\rightarrow$ Kali Impl $\rightarrow$ Lilith Gnosis).

## [v1.2.0] - 2026-06-04
### Added
- **MaKaLi Triad Architecture**: Formalized the synthesis of Ma'at and Lilith via Kali.
- **Dual-Inference Mandate**: Implemented `model_override` in `Oracle.summon()` to allow local-first routing with cloud fallback.
- **Sovereign-Symmetry**: Mapped identity and routing to the 10 Pillar Keepers.

### Fixed
- **MCP Paths**: Canonicalized `mcp/` references to `mcp_servers/` across the codebase.
- **Entity Registry**: Implemented Lazy Deletion with Grace Period (0.5s) per id Software heritage.
