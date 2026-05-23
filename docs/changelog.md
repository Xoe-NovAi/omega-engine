# Omega Engine – Changelog (MVE Phase)

## 2026‑05‑14
### Dependency Updates
- `qdrant-client` pinned to **1.17.1** (client‑server parity).
- Updated `pydantic` to **2.13.4**, `httpx` to **0.28.1**, and other core libs.

### Infrastructure
- Implemented systemd socket activation for Hub, Research, Stats services.
- Migrated to Podman Quadlets (`omega-infra-pod.service`) with CPU‑set pinning.
- Upgraded containers:
  - Qdrant **v1.17.1** (gridstore enabled)
  - Redis **8.6.3**
  - PostgreSQL **18.4**
  - Caddy **2.11.3**

### Core Engine
- `EntityRegistry` now auto‑creates entity workspaces (`data/entities/<name>/`).
- Added `Orchestrator.dispatch_agent` and `ResourceGuard` (anyio semaphore).
- Introduced `OfflineMockBackend` for deterministic test runs.
- Updated `ContextBuilder` to inject recent memory snippets.

### New Modules
- `src/omega/bridge/elevenlabs.py` – ElevenLabs voice bridge (service deployed).
- `src/omega/oracle/gnosis_proxy.py` – Gnosis Proxy with Tool‑RAG scaffolding.

### UI / UX
- Chainlit removed from active codebase; UI now via Omega CLI and Iris voice assistant.
- Session header configurability added (`config/omega.yaml`).

### Research & Documentation
- Completed critical research items R‑00 → R‑41 (provider fabric, circuit‑breaker, native inference, hardware steering, etc.).
- Added OpenCode skills: `pr-readiness-checker`, `legacy-pattern-miner`, `omega-doc-architect`.
- Updated `researcher.md` to v3.0.0 with sovereign directives.
- Populated `docs/research/` with markdown deliverables and updated `INDEX.md`.

### Testing & CI
- All **40 tests** now pass (`make test`), both in mock and live modes.
- Linting (`flake8`) clean.
- `make demo` runs successfully with mock backend.

### Miscellaneous
- Added `.env.example`, updated `Makefile` targets.
- Refactored `make lint` to use `flake8`.
- Added `docs/changelog.md` (this file).
