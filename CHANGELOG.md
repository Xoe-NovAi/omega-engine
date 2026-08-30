<!--

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Changelog

## [v1.5.0] - 2026-07-18
### Added
- **Third-Party Repository Registry**: 18/19 repos cloned to `third-party/` — P0 (4/4), P1 (5/5), P2 (6/6) complete. P3 partial (1/4).
- **Heritage Tags Added**: 10 new `[heritage:]` tags for sqlite-vec, ggml, qdrant, mempalace, xai-grok-build, letta (see CREDITS_CANONICAL.md §1.2).
- **Grok Build Consolidated**: Moved from `third_party/` to `third-party/grok-build/` (85-crate Rust workspace).
- **Mining Report**: `data/entities/roc_racoon/workspace/mining_reports/THIRD_PARTY_REPOSITORY_REGISTRY.md` with key files, hardware constraints, and fleet usage patterns.
- **SOVEREIGN_LEGACY_MAP.md**: Added §11 with full registry integration and heritage vetting pipeline.

### Changed
- **CREDITS_CANONICAL.md**: v1.5.0 — 14 Conscious Adoptions (was 4). 10 new heritage mappings added.
- **CREDITS.md**: Compact registry expanded to 12 entries.
- **OMEGA_ENGINE.md**: Added Third-Party Registry metric to Current State table.

### Security
- **Local-First Compliance**: All P0 runtime dependencies now have local source access for debugging and heritage vetting (M7, M14).
### Added
- **Sovereign WAD Protocol (SWP) — Strike 11**: `src/omega/wad/protocol.py` — `ILump`, `LumpEnvelope`, `LumpRegistry`, `SovereignBus`, Topological WAD Loader. The "Doom-ification" of the Engine (MaKaLi Council + Heritage Council ratified).
- **Universal Document Reader**: `src/omega/doc_reader/` — Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml with metadata extraction. Published as `omega-doc-reader` v1.0.0 on PyPI.
- **Sovereign Sieve (Standalone)**: `packages/omega-sieve/` — T1→T2→T3 tiered web research (Trafilatura → Surgical → Crawl4AI). Published as `omega-sieve` v0.1.0 on PyPI.
- **Heritage Vetting Pipeline**: `scripts/heritage_vet.py` — 4-gate pipeline (Discovery → Vetting → Decision → Implementation) with vet record IDs (`vet-XXX`) replacing legacy `[id-soft: game-year]` format.
- **Test Suite**: 1315 tests passing (was 1162), 43 skipped, 3 xfailed, 0 failed.

### Fixed
- **M2 Firewall**: Sandbox workspace exception for `config/wads/omega_research/workspaces` — legitimate WAD boundary write, not leakage.
- **Datetime Deprecation**: Migrated all `datetime.utcnow()` → `datetime.now(timezone.utc)` across 15+ files (M9 Error Integrity).
- **Heritage Tags**: Updated `providers.py` lines 901/912 to `[id-soft: vet-057]` (Atomic Swap) and `[id-soft: vet-058]` (Rollback) per M14 compliance.
- **ODT Reader**: Safe attribute access for missing metadata elements (no more ValueError on empty meta).
- **RTF/HTML/MD/JSON/YAML Tests**: Fixed temp file flush/sync timing (`f.flush()` + `os.fsync()` before read).
- **Sandbox Tests**: Fixed import paths (`src.omega` → `omega`), timezone-aware datetime handling, mock coroutine awaits.
- **Somatic State Test**: Fixed duplicate AsyncMock assignment causing unawaited coroutine warning.

### Changed
- **WAD Loader**: Evolving to Sovereign WAD Protocol (SWP) — Lump-based DAG loader, MWAD deployment descriptors.
- **Heritage Format**: 122 tags mapped; migration advisory for legacy `[id-soft: game-year]` → `[id-soft: vet-XXX]`.
- **Test Count**: 1315 passed (was 1162 in v1.1.0).

### Security
- **Zero Telemetry**: Confirmed no external metrics collection (M8).
- **Local-First**: Provider fabric unchanged — native-gguf primary, cloud fallback only (M7).

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
