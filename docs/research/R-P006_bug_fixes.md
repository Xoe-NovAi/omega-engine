# 🔱 Omega Engine — Bug Fix Registry (R-P006)
**AP Token**: `AP-BUGFIX-REGISTRY-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_builder ⬡ PHASE-0

This document tracks the resolution of critical bugs identified in the R44 Comprehensive Systems Review.

## 🛠️ Fix Log

| Bug ID | Description | Fix Applied | Verification | Status | Date |
|--------|-------------|-------------|-------------|--------|------|
| C-1 | Broken Import in `gnosis_proxy.py` | Changed `from src.omega.oracle.entity_registry` to `from .entity_registry` | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-5 | MCP Hub async calls without await | Added `await` to `library.domains()` and `library.stats()`; made `library_domains` async | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-6 | MCP Hub undefined `get_engine()` | Added `get_engine` to `omega.observability` import | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-8 | Exposed API Keys in version control | Removed keys from `generate_systemd_units.sh`, `opencode.json`, `mcp_servers.json`; replaced with placeholders | Manual inspection | ✅ FIXED | 2026-05-15 |
| C-9 | `.env` tracked in git | Removed `deploy/infra/.env` from git tracking; created `.env.example` | `git ls-files` | ✅ FIXED | 2026-05-15 |
| C-2 | `oracle.py` — Soul Evolution Race Condition | Implemented `anyio.Lock` and atomic write using `tempfile` + `os.replace` | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-3 | Blocking `subprocess.run()` in `orchestrator.py` | Replaced `subprocess.run` with `await anyio.run_process` | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-4 | `model_gateway.py` — `NativeGGUFProvider` ResourceGuard | Added `NativeGGUFProvider` to the ResourceGuard `isinstance` check | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-7 | Non-existent `anyio.Deque()` in `curation_pipeline.py` | Deleted redundant `curation_pipeline.py` (superseded by `curator.py`) | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-10 | Wrong install extra `iris` in `setup.sh` | Changed `.[cli,iris,all,dev]` to `.[all,dev]` | Manual inspection | ✅ FIXED | 2026-05-15 |
| C-11 | `omega-belial.container` — Missing Dependencies | Created `Dockerfile.belial` and updated `.container` to use `omega-belial:latest` | Manual inspection | ✅ FIXED | 2026-05-15 |
| C-12 | `providers.yaml` Native-GGUF Model Path | Added `phi-4-mini` spec to `models.yaml` to match `providers.yaml` | Manual inspection | ✅ FIXED | 2026-05-15 |
| C-13 | `asyncio.create_task()` in AnyIO loop | Replaced `asyncio.create_task` with `anyio.to_thread.run_sync` + `anyio.run` | `make test` (41/41 passed) | ✅ FIXED | 2026-05-15 |
| C-14 | `entity_belial.py` — Relative Paths | Replaced relative `data/` paths with `DATA_DIR` constant | Manual inspection | ✅ FIXED | 2026-05-15 |
| C-15 | `omega-belial.container` — Duplicate Keys | Combined duplicate `PodmanArgs` into a single line | Manual inspection | ✅ FIXED | 2026-05-15 |

## 📋 Pending Criticals
- [ ] C-16: Image tag mismatch in `setup.sh`
- [ ] C-17: `BASE_DIR` resolution off-by-one in `entity_workspace.py`
