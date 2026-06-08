# 🔱 Omega Engine — Changelog

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
