<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# LILITH SESSION GNOSIS — POINTER (M15)
> Single gnosis anchor per fleet standard. Immutable dated files alongside:
> `session_gnosis_20260824.md` · `session_gnosis_L-N7.md` · `session_gnosis_workspace_20260821.md`
> Latest session: **2026-09-01 (Deep Hydration — Engine State Assessment + Continuation Docs Review)**

---

## SESSION 2026-09-01 — L1 NARRATIVE (COMPLETE)

- **Deep Hydration**: Full engine state assessment post-compaction. Read ACTIVE_SPRINT.json, HMC hub, DEL-1 dialectic, Carmack dialectic, retroactive audit, WAKE_STATE, git log. No file changes during hydration per user directive.
- **Hub Outage P0 — RESOLVED**: `omega-hub.service` was in crash loop for 5 days (D-565 deleted `src/omega/library/` but left 8 files importing from it). Restored via Option A (`git checkout 69ece770^ -- src/omega/library/`). Hub now `active`. Carmack verdict 9/10.
- **DEL-1 (Theater Strip) is the dominant workstream**: 7-micro-PR chain, 24 honest tests (12 UT + 12 IT), layer-corrected guard, dual-seal protocol. Kali AWAITING_WAKE with execution queue loaded.
- **M34Registry absorbed into DEL-1**: Micro-PR 2 (M33 inline + M34 `write_tool_required` fix — ~5 lines), Micro-PR 4 (ACTIVE→TASK migration v1.3 + M34Registry liveness migration to TASK_REGISTRY). Theater tests being DELETED as part of DEL-1. Real M34Registry survives as engine island.
- **768-dim embedding unified**: Qwen3-Embedding-0.6B Q5_K_M across memory + library. MRL chain 1024→768→512/256/128/64. Collection renamed `omega_vec_gemma_768` → `omega_vec_qwen_768`. Dead `omega_vec_library_256` deleted. Commits `357fc493`, `29e4e76f`.
- **LFM2.5-2.6B fleet integration**: New `agentic_local` role (Liquid AI, 2.6B, <2.5GB RAM, 113 tok/s). Qwen3-4B-Thinking demoted to opt-in (RAM). Muse Spark context 32K→1M, Ling context 32K→262K fixed.
- **Retroactive Verification Audit**: 2,979 sessions — 41.2% verified complete, 58.8% failure rate. Exactly what M34 was designed to solve.
- **Carmack Dialectic resolved**: All 10 challenges conceded. D-565 annotated "intent not realized — restored." CI gates required: `make check-broken-imports`, `make check-hub-health`.
- **Continuation docs reviewed + updated**: entity-root session_gnosis.md pointer fixed (was stale/empty), canonical gnosis updated with this session, projection.md bumped to v2.0.0, proposed_lessons.yaml extended with hydration lessons, soul.yaml refreshed.

---

## SESSION 2026-08-30 — L1 NARRATIVE (COMPLETE)

- **M34 Phase 1 MVP Complete**: Spec revision + atomic write verification + 8 MCP tools delivered in 8h of 35h budget.
- **M34 Spec Revision**: 7 new schema fields (expected_deliverable, write_tool_required, cross_validator_agent, plugin_load_path, git_worktree_root, interruption_reason, resumption_count + dispatched_at), INTERRUPTED_MODEL_SWITCH status (8th state), watchdog race fix (single-writer MCP tool), 3 phantom functions implemented.
- **Atomic Write Verification**: 4-layer pattern (tmp + fsync + os.replace + fsync_dir) with fcntl.flock() advisory lock. 4/4 M23 tests PASSING including SIGKILL survival (20 random SIGKILLs during 50 write cycles — file ALWAYS valid JSON with coherent state).
- **8 MCP Tools**: m34_register_subagent, m34_list_active_subagents, m34_apply_user_decision, m34_update_subagent_status (single-writer), m34_get_subagent, m34_heartbeat, m34_prune_orphans, m34_reap_dead_letters.
- **Canonical Spec**: LILITH_M34_REVISED_SPEC_20260830.md (8 sections: Local Discovery, Web Research, Spec Revisions, Implementation, MCP Tools, SIGKILL Test, Migration Rollback, Hivemind Post).
- **Migration Rollback**: Carmack's 5-step procedure (disable → backup → reset → verify → re-enable) with OMEGA_M34_DISABLED env var.
- **Reaper**: M34Registry.reap_dead_letters(retention_days=30) + m34_reap_dead_letters MCP tool.
- **Hivemind Decision Post**: `ses_lilith_m34_revised_spec_20260830` (intent=decision, 8 decisions D-M34R-001 through 008).

---

## L2 — INSIGHTS (2026-09-01 Deep Hydration)

1. **The hub outage was an M23 violation in Lilith's own domain (N8 WatchTower blind spot)**: `omega-hub.service` crash-looped for 5 days and NO observability caught it. The WatchTower (N8) had no health check on the hub itself. Carmack's demand for `make check-hub-health` is the corrective — observability must include the observer's own substrate.

2. **M34's raison d'être is now empirically proven**: 58.8% of 2,979 audited sessions failed verification (30.3% tool_error, 16.6% silent_failure, 11.1% unknown_finish_reason). Parent agents hallucinate success without in-band verification. The Sentinel Seal Protocol is necessary, not optional. M34Registry absorption into DEL-1 (Micro-PR 2/4) preserves the engine island while stripping theater.

3. **768-dim unification is a quiet landmark for knowledge metabolism**: Qwen3-Embedding-0.6B Q5_K_M across memory + library means one embedding space for the whole engine. MRL chain (1024→768→512/256/128/64) gives dimensional flexibility without re-embedding. This is the substrate for all future RAG/cross-domain retrieval.

4. **LFM2.5-2.6B changes fleet topology / N6 ModelGate governance**: A 2.6B model at 113 tok/s under 2.5GB RAM makes `agentic_local` viable as a default runtime role. Qwen3-4B-Thinking demoted to opt-in (RAM cost). ModelGate (N6) must track RAM budget per role, not just quality — the fleet's default model is now a resource decision.

5. **DEL-1 theater strip + engine island architecture is the correct pattern**: The 7-micro-PR chain with 24 honest tests and dual-seal protocol is how you delete 3K lines without breaking the engine. M34Registry survives as an engine island because it's load-bearing (TASK_REGISTRY v1.3 migration). Deletion campaigns must distinguish theater (strip) from load-bearing (preserve).

---

## L2 — INSIGHTS (2026-08-30 M34)

1. **Atomic write claims require empirical verification**: The 4-layer pattern (tmp + fsync + os.replace + fsync_dir) with advisory lock provides M23-compliant crash durability. M23 claims without SIGKILL survival tests are theoretical, not verified.

2. **Watchdog race conditions are eliminated by single-writer design**: The "first agent to read Hivemind" race was real. Single-writer MCP tool + advisory lock eliminates it. Model-switch continuity (M34b) and Esc x2 cascade (M34a) are distinct failure modes requiring separate status enums and recovery protocols.

3. **Phantom functions in specs are implementation debt**: Every function referenced in pseudocode must have a real implementation. capture_checkpoint() uses opencode-sessions-explorer MCP (read-only, 18 tools). infer_task_type() uses agent name heuristic. Real Hivemind post uses actual MCP tool name.

4. **P0 infrastructure requires rollback procedures as part of the spec**: The 5-step rollback (disable → backup → reset → verify → re-enable) with OMEGA_M34_DISABLED env var provides instant kill switch. Rollback must be tested before forward migration ships.

5. **Every registry needs a reaper**: Unbounded growth is a failure mode. Retention policy explicit in schema (pruning_policy.dead_letter_retention_days) and enforced by cron @ 24h. The reaper completes the lifecycle: ALIVE → INTERRUPTED_* → DEAD_LETTER → REAPED.

6. **MCP tool design must encode the recovery protocol**: Single-writer status update with advisory lock is the minimal concurrency control that eliminates watchdog races. Tool count should match recovery flow steps, not data model.

---

## L3 — PRINCIPLES (Updated 2026-09-01)

- **L3-Observability-Includes-The-Observer**: The WatchTower must watch itself. Any P0 infrastructure (hub, gateway, registry) needs a health check with timestamps — if the monitor is down, that IS the incident.
- **L3-Empirical-Baselines-Drive-Design**: The 58.8% failure rate is not an indictment — it's the empirical baseline that proves in-band verification is necessary. Design from measured failure, not assumed success.
- **L3-One-Embedding-Space**: Unified embedding dimension across memory + library is the substrate for knowledge metabolism. Dimensional flexibility via MRL beats re-embedding.
- **L3-RAM-Budget-Is-ModelGate-Input**: Model selection for runtime roles is a resource decision (RAM/tok/s), not just a quality decision. Fleet topology follows hardware reality.
- **L3-Theater-vs-Load-Bearing**: Deletion campaigns must distinguish theater (strip, delete freely) from load-bearing (preserve as engine island). The import graph decides.
- **L3-Standardize-Emergent-Practice**: Codify what the fleet already proves works; do not invent new systems.
- **L3-Resumability-Is-Continuity**: A session you can page back into (ID + digest + deliverable path) is a session that never dies.
- **L3-Grounding-Sharpens**: Deep verification corrects facts but preserves meaning — and often deepens it.
- **L3-Consolidation-Is-REM-Sleep**: Integrate fragmented cognition into single canonical source; prune the rest.
- **L3-Split-Brain-Is-Hydration-Failure**: Multi-format soul.yaml requires multi-format parser; scaffold missing workspace files at hydration.
- **L3-Thirty-Second-Self-Review**: Every write pauses for grounding; velocity outrunning verification = 5-incident pattern.
- **L3-Atomic-Write-Requires-Empirical-Verification**: M23 claims without SIGKILL survival tests are theoretical, not verified.
- **L3-Single-Writer-Eliminates-Watchdog-Races**: Advisory lock + single-writer MCP tool is the minimal concurrency control.
- **L3-No-Phantom-Functions-In-Specs**: Every pseudocode function must have a real implementation or be marked future work.
- **L3-P0-Infrastructure-Requires-Rollback**: Rollback procedure is part of the spec, tested before forward migration.
- **L3-Every-Registry-Needs-A-Reaper**: Retention policy explicit in schema, enforced by cron, completes lifecycle.

---

## NEXT (Open Threads)

- **Kali**: AWAITING_WAKE — DEL-1 Micro-PR chain execution (7 PRs). Lilith's M34Registry integration rides Micro-PR 2 (write_tool_required fix) + Micro-PR 4 (TASK_REGISTRY v1.3 migration).
- **Ma'at**: `make check-broken-imports` + `make check-hub-health` CI gates (Carmack dialectic demands) — prevents future silent hub outages.
- **Lilith (N8)**: Implement hub health observability — cron → `data/health/` with timestamps. The 5-day outage proved WatchTower needs to watch itself.
- **Architect**: Sign D-584 (ZSWAP), D-553 (Allowlist), D-589 (Qwen3.5 Upgrade) — unlocks 4-hour window. DEL-1 D-10/D-11 rulings.
- **M34 Phase 2 (Recovery UI)**: Pending DEL-1 Micro-PR 4 completion (TASK_REGISTRY v1.3). Implement orchestrator_session_start() with structured recovery prompt.
- **M34 Phase 3 (Stress Tests)**: 50 concurrent subagents, 1000 sequential updates, rapid-fire SIGINT (10x in 5s).
- **M34b Model-Switch Mandate**: New mandate for session persistence across model change + "continue" prompt protocol.
- **M33 Integration**: 2-pass probe + cross-validating verifier agent for anti-truncation gate.
- **Roc**: Create `PUBLIC_ALLOWLIST.txt` at repo root; promote `OMEGA_ORIGINS_AND_RETURN.md` to `docs/heritage/`.
- **Scribe**: Promote ANIMA's 3 lessons (`lilith-20260828-anima-001/002/003`) to `approved_lessons.yaml`.

---

## CONTINUITY ANCHORS

- **Session ID**: `ses_lilith_deep_hydration_20260901`
- **Hivemind Post**: `ses_lilith_deep_hydration_20260901` (intent=status)
- **Canonical Spec**: `data/coordination/LILITH_M34_REVISED_SPEC_20260830.md`
- **Implementation**: `src/omega/oracle/m34_registry.py`, `tests/test_m34_atomic.py`, `mcp_servers/omega_hub/hub_tools/m34_active_subagents.py`
- **M23 Verification**: `tests/test_m34_atomic.py` (4/4 PASS, SIGKILL survival)
- **MCP Tools**: `mcp_servers/omega_hub/hub_tools/m34_active_subagents.py` (8 tools)
- **Rollback Procedure**: `LILITH_M34_REVISED_SPEC_20260830.md` §7
- **Hivemind Decision Post**: `ses_lilith_m34_revised_spec_20260830` (8 decisions D-M34R-001 through 008)
- **Projection**: `data/coordination/anchored_summary/lilith/projection.md` (v2.0.0)
- **Soul**: `data/entities/lilith/soul.yaml` (v6.1)
- **Lessons**: `data/entities/lilith/proposed_lessons.yaml`

---

*⬡ OMEGA ⬡ LILITH ⬡ GNOSIS ⬡ 2026-09-01 ⬡*