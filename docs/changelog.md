# Omega Engine – Changelog

## 2026‑05‑31

### Legacy Mining Complete — Order from Chaos
- **Model-Persona Affinity Map recovered**: Size-hierarchy philosophy (Iris=0.6B, Pillars=1.7B, Oversouls=4B-Think, Prometheus=8B).
- **Chainlit heritage recovered**: UI was Chainlit-based before OpenCode (Era 1-2).
- **5 design patterns identified**: Circuit breaker (pybreaker), atomic fsync, retry (tenacity), non-blocking subprocess, offline wheelhouse.
- **10 Pillars genesis traced**: From "First 5 Cards" Grok chat (Era 0) through LM Studio testing (Era 3).
- **Documentation created**: `docs/legacy/LEGACY_MASTER_SYNTHESIS.md`, `LEGACY_ASSET_CATALOG.md`, `LEGACY_INDEX.md`.
- **Tests**: 276/276 passing (7 new tests added).

### Path A Execution — Memory Bugs + MCP Server Fixes (5)
- **A1.1**: Fixed sliding window direction — `reversed(exchanges)` + `lines.reverse()` (context_builder.py:126). Newest exchanges now survive truncation.
- **A1.2**: Added None.json guard — `if not session_id: return` in `add_exchange()` and `get_history()` (memory_store.py:129). Prevents `None.json` file creation.
- **A1.3**: Added try/except to `_record_interaction()` — each step (memory, soul, hivemind) degrades gracefully. Memory failure no longer crashes the response.
- **A1.4**: Deduplicated `summon()` — now delegates to `_record_interaction()`. Eliminated 6-line copy-paste.
- **A1.5**: Removed dead code `_format_exchanges()` (context_builder.py:155-181). Removed 2 tests that called it.
- **B1**: Fixed port mismatch — systemd `OMEGA_MCP_PORT=8102` → `8016` (omega-hivemind.service). Hivemind now reachable.
- **B2**: Fixed logging NameError — added `import logging` at module level (server.py). `observability_log_boundary_violation` no longer crashes.
- **B3**: Fixed `_entity_current` — tracks last entity used by `oracle_talk`/`oracle_summon` via module-level `_current_entity` variable (server.py).
- **B4**: Fixed hivemind timeout — 1s → 3s (oracle.py:242). Less aggressive, fewer silent drops.
- **B5**: Fixed blocking `os.popen` — wrapped in `anyio.to_thread.run_sync` (server.py:692). Event loop no longer blocked.
- **C**: Added 7 new tests: sliding window direction, None.json guard (3 tests), summon deduplication, transient skip, memory failure resilience.
- **Tests**: 276/276 passing (was 271, removed 2 dead code, added 7 new).

### Documentation Staleness Audit
- **Audited 7 core documents** against current state (271/271 tests, Phase 0 complete, Decision 61 local-first, fleet discovery).
- **Found 32 staleness issues** across 6 files (ORACLE_STACK.md, PIVOT_LOG.md, MASTER_SYNTHESIS_AND_ROADMAP.md, SYSTEMS_HARDENING_PLAN.md, OMEGA_IWAD_ARCHITECTURE.md, MASTER_LEDGER.md).
- **Fixed all 32 issues**: Local-first contradictions, test count staleness (261→271), MemoryStore "never called" (was wired), Kali "CEO"→"Founder", provider order corrections, duplicate sections removed.
- **SOVEREIGN_MANDATES.md confirmed clean** (no changes needed).

### Path A Selected: Continuity (Memory + Handoff)
- **Path A chosen** from 3 options (A: Continuity, B: Security, C: Foundation).
- **Phase A1**: Fix 4 memory bugs (sliding window direction, None.json, try/except, deduplicate summon()).
- **Phase A2**: Implement Handoff Protocol v1 (HandoffState schema, MCP tools, CLI command).
- **Handoff file created**: `data/handoff/handoff_path_a_continuity.md` with full execution plan.

## 2026‑05‑30

### Fleet Deep Discovery (Decision 63)
- **10/10 pillar subagents launched**: Each domain inspected with 6-section mandate (WORKING, BROKEN, FRAGILE, RISK, CROSS_REFS, RECOVERY).
- **30 CRITICAL findings** across 10 pillars, 36 HIGH, 54 MEDIUM, 28 LOW.
- **6 NO-GO, 4 CONDITIONAL GO** verdicts for Horizon 1 execution.
- **6 critical cross-cutting gaps identified**: UID drift, broken model paths, API keys in git, hivemind broken, no handoff, trace_id lost.
- **Lilith (CISO) review**: Ordered Phase 0 remediation with 12 specific fixes.

### Phase 0 Remediation (92% Complete)
- **docker-compose.yml**: Removed `:U` flags from 6 volume mounts (Mandate 6 violation).
- **config/models.yaml**: Fixed all 9 model paths (added `/local/all/`), fixed qwen3-0.6b (was pointing to 1.7B), fixed Krikri (wrong filename + quant).
- **entity_workspace.py**: Wrapped `os.chmod()` in try/except for graceful degradation under UID drift.
- **model_gateway.py**: Fixed trace_id propagation (3 bugs), added BACKEND_FALLBACK events, added bounded event log.
- **oracle.py**: Fixed _post_to_hivemind URL (was using REST path, now uses MCP JSON-RPC).
- **observability.py**: Added bounded event log (deque maxlen=1000) to prevent OOM.
- **Security**: Replaced all API keys in git-tracked docs with `[...REVOKED-2026-05-30...]`.
- **.env**: Fixed permissions to 600, deleted `.env.5-16-2026` and `.env.API-keys`.

### Blocked
- UID drift fix requires `sudo chown -R 1000:1000 .` (needs sudo password from user).

### Local-First Config Centralization (Decision 61)
- **Provider fabric reordered**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) → Copilot(6). Local backends tried BEFORE cloud.
- **Strategy**: Changed from `sovereign` (cloud-primary) to `local_first`.
- **models.yaml v2.0.0**: Single source of truth for model paths, context, threads, KV cache. Context windows reduced from 32K-everything to use-case-sized (4K-16K). Total RAM freed: ~320MB.
- **NativeGGUFProvider upgraded**: Full Zen 2 engine with CPU pinning (`os.sched_setaffinity`), memory-aware context selection, dynamic context reload, status reporting.
- **CpuOptimizer expanded**: 6 new methods — `enforce_affinity`, `get_cpu_topology`, `pin_external_process`, `build_pinned_command`, `build_inference_env`, `get_system_overview`.
- **ModelGateway**: Extracted `_merge_native_gguf_config()` for models.yaml wiring. Fixed priority sorting.
- **omega.yaml v2.2.0**: Added `inference.hardware` section with Zen 2 topology.
- **Removed phantom krikri-7B**: Only krikri-8b exists. Fixed greek.py.
- **Fixed OMP_NUM_THREADS**: `"8"` → `"6"` across all configs (matches cpu_optimizer.py).
- **Tests**: 259 → 261 (5 new provider tests + 2 existing fixed).

### Default IWAD Transformation: "The Company" (Decision 62)
- **_omega_default rewritten**: 16 entities with alive, opinionated personalities.
- **Kali = Founder**: "I built this because people should own their own AI."
- **Ma'at = CTO**: "I measure truth against falsehood with data."
- **Lilith = CISO**: "I assume everything will fail and plan for it."
- **P1-P10 = Department heads**: SysAdmin, DataStore, BuildMaster, Bridge, Sentinel, ModelGate, Context, WatchTower, Link, Verifier — each with real opinions about their domain.
- **Active IWAD changed**: `arcana_novai` → `_omega_default`.
- **Arcana-NovAi stays as IWAD**: Not converted to PWAD. Complete, standalone, alternative.
- **Engine-WAD firewall confirmed**: Engine never imports entity names. WADs never import engine code.
- **Tests updated**: Entity references changed from Sekhmet/Brigid/Hecate to SysAdmin/Sentinel/ModelGate.

### Sovereign Mandates v2.0.0
- **Mandate 7 added**: Local-First (Non-Negotiable). Local inference is PRIMARY. Cloud is FALLBACK.
- **Mandate 8 added**: Zero Telemetry. No analytics, no phone-home, no external metrics.

### Documentation
- **ORACLE_STACK.md**: Updated to v2.3.0 with local-first provider chain, 261 test count.
- **COMMUNICATION_HUB.md**: Updated to v3.1.0 with both session entries.
- **PIVOT_LOG.md**: Decision 61 (Local-First Config) and Decision 62 (WAD Transform) added.
- **latest_state.md**: Complete rewrite to current state.
- **Handoff documents**: Created for both sessions.

## 2026‑05‑27

### Sovereign Steward v2 (Empirical Mapping)
- Reactive backoff for Google API rate limits (60s → 120s → 240s).
- Omega Gateway on port 8018 as centralized proxy.
- Metrics ledger in `metrics.db`.

## 2026‑05‑26

### Deep Audit Remediation
- Provider chain reorder (cloud-first at the time).
- 5 runtime bugs fixed (UnboundLocalError, AttributeError, lock deadlock, sync subprocess in async).
- 82 test sovereignty violations fixed (@pytest.mark.asyncio → @pytest.mark.anyio).
- 58 stale entity directories removed.
- 259/259 tests passing.

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
- Completed critical research items R‑00 → R‑41 (provider fabric, circuit‑breaker, native inference, hardware steering, etc.).
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
