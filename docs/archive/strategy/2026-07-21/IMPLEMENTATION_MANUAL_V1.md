# 🔱 Sovereign Refactoring & Implementation Manual (v1.0)
**Date**: 2026-07-10
**Status**: ACTIVE ROADMAP
**Context**: Synthesized from deep legacy mining (@roc_racoon) and systems synthesis (@jem). All ignorance gaps closed; all implementations verified as technically viable.

## Phase 1: Governance & Documentation Hygiene (Immediate)
**Objective**: Eradicate stale documentation and restore the immutable audit trail.
**Viability**: 100%. Pure text manipulation and alignment with existing D209 (7-agent fleet) reality.

1.  **Resolve PIVOT_LOG Monotonicity (G6)**
    *   *Implementation*: Renumber colliding decisions in `docs/decisions/PIVOT_LOG.md`.
    *   *Mapping*: D189 (Multi-Model Council) → D207; D189 (SEHP) → D208; D190 (Qdrant L3) → D209.
2.  **Synchronize Fleet Protocols**
    *   *Implementation*: Update `HIVEMIND_PROTOCOL.md` and `SUBAGENT_DISPATCH_PROTOCOL.md`.
    *   *Mapping*: Change "14 agents" to "7 agents". Replace "Kali dispatch authority" with decentralized slot-based delegation (Pillar architecture).

## Phase 2: Core Engine Hardening (Short-Term)
**Objective**: Eliminate code smells and enforce mandates via CI automation.
**Viability**: 100%. Relies on standard Python dataclass semantics, bash grep, and SQLite queries.

1.  **Cleanse `OracleResponse` Dataclass (G7)**
    *   *Implementation*: Remove redundant `session_id`, `escalated`, and `cost_warning` fields in `src/omega/oracle/oracle.py` (lines 93-95).
2.  **Enforce D206 via CI Gate (G2)**
    *   *Implementation*: Add `grep -rn "google_search" src/omega/ .opencode/agents/ config/` to the `temple-grade` target in `Makefile`. If exit code is 0 (found), fail the build.
3.  **Automate Sovereignty Ratio (G1 / M7)**
    *   *Implementation*: Create `scripts/calculate_sovereignty.py`.
    *   *Logic*: Connect to `data/observability/metrics.db`. Query: `SELECT provider, COUNT(*) FROM inference_events WHERE timestamp > datetime('now', '-30 days') GROUP BY provider`.
    *   *Calculation*: `(local_count / total_count) * 100`. Wire to `make sovereignty`.

## Phase 3: Reliability & Integrity (Medium-Term)
**Objective**: Close gaps in the provider fabric and error handling.
**Viability**: 100%. Uses existing AnyIO/httpx patterns and the already-implemented `FailureModeRegistry`.

1.  **Wire the `FailureModeRegistry` (G4 / M17)**
    *   *Implementation*: Inject `src/omega/observability/failure_registry.py` into `Oracle.__init__`.
    *   *Logic*: In `talk()` and `summon()`, catch `OmegaError`, call `await self.failure_registry.record_failure(e)`, then raise or fallback.
2.  **D205 Key Sharding Test Coverage (G3)**
    *   *Implementation*: Add `test_openrouter_sticky_sharding_failover()` to `tests/test_providers.py`.
    *   *Logic*: Mock `httpx.AsyncClient.post` with a side_effect: first call returns 429, second call returns 200. Assert that `provider.active_key_index` increments.
3.  **SearXNG Health Probes (G5)**
    *   *Implementation*: Add `async def is_healthy()` to `SearXNGProvider`.
    *   *Logic*: `await client.get("http://127.0.0.1:8017/healthz", timeout=2.0)`. If it fails, `SearchRouter` skips T1 and proceeds to T2 (Exa).

## Phase 4: Sovereign Mail Integration (Strategic)
**Objective**: Replace cloud email with a self-hosted, privacy-first stack.
**Viability**: 100%. Stalwart Mail is written in Rust, consumes ~150MB RAM, and fits easily within the 14GB hardware constraint alongside local AI models.

1.  **Infrastructure Deployment**
    *   *Implementation*: Author `config/wads/_omega_default/infra/sovereign-mail.container`.
    *   *Logic*: Use `UserNS=keep-id` and `User=1000` (M6 compliance). Mount local volumes for JMAP/IMAP storage.
2.  **MCP Bridge Implementation**
    *   *Implementation*: Add `omega-hub_mail_send` and `omega-hub_mail_read` to `mcp_servers/omega_hub/tools.py`.
    *   *Logic*: Use standard Python `imaplib` and `smtplib` connecting to `localhost` ports exposed by the Stalwart container.