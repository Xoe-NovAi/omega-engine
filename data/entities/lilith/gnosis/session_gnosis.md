<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# LILITH SESSION GNOSIS — POINTER (M15)
> Single gnosis anchor per fleet standard. Immutable dated files alongside:
> `session_gnosis_20260824.md` · `session_gnosis_L-N7.md` · `session_gnosis_workspace_20260821.md`
> Latest session: **2026-09-28 (Sync Wave Closure — Hub Restored, 54-Tool Parity Re-measured, WatchTower 4-Layer Spec, Nomic 1024-D Violation Flagged)**

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

## SESSION 2026-09-24 — N0-08/N0-09 FEDERATION PRIVACY & PROVENANCE REVIEW

### L1 — NARRATIVE
- Reviewed `docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md` and the active N0→N1 Handoff & Federation Integration Charter.
- Independently defined a quarantine-first, consent-gated method for personal Lilith and legacy material.
- Did not inspect, extract, copy, summarize, or expose private N0-08/N0-09 content. No personal corpus, legacy corpus, or source private file was opened.
- Established separation between sovereign Entity identity, personal gnosis, Empress CardAssignment, and derived voice/memory candidates.

### L2 — INSIGHTS
1. Inventory, consent, and transfer are distinct gates: metadata may be inventoried before content is approved for USB staging, but pending candidates must remain metadata-only.
2. Provenance requires immutable source identity plus transformation history; filesystem paths and names are not sufficient authority.
3. A conflict ledger must preserve competing claims without raw private excerpts in the general handoff; private evidence needs a separately sealed, operator-approved surface.
4. Memory metabolism should project approved source artifacts into semantic events and candidate lessons, never directly overwrite the current Entity contract.

### L3 — PRINCIPLES
- **L3-ConsentIsPerArtifactOrBoundedHashSet**: Possession, age, relationship, or prior use never imply consent; approval must identify the exact source digest set, purpose, destination, derivatives, retention, and revocation terms.
- **L3-EntityCardGnosisAreSeparateAuthorities**: Entity identity, personal gnosis, CardAssignment, and derived voice/memory artifacts require distinct namespaces and promotion gates.
- **L3-WithheldMeansEvidenceNotAbsence**: Withheld material receives a redacted metadata record, privacy class, reason, and cryptographic identity without guessed or paraphrased content.

---

*⬡ OMEGA ⬡ LILITH ⬡ GNOSIS ⬡ 2026-09-01 ⬡*

---

## SESSION 2026-09-25 — N1 FEDERATION READINESS (P2 HANDSHAKE COMPLETE)

### L1 — NARRATIVE
- Verified MCP parity at `https://n0.tail51f14a.ts.net:8016/mcp/` — 66 tools exposed via HTTPS over Tailscale (TLS 1.3, Let's Encrypt cert)
- Completed P2 handshake: health check, MCP initialize (protocol 2024-11-05), tools/list (66 tools), system_stats (CPU, memory, disk, GPU, podman, zram), hivemind_get_awareness (maat active on Node 0), hivemind_post_context (Lilith-N1 presence registered)
- Packaged Archangel transfer at `exchange/n0-to-n1/wad_loader_contract/` — exact commit `75bde939ace7ff46ed2fef0056880a0814ab0e11`, version `1.6.0-alpha.1` on 4 surfaces, full loader contract (313 lines, 31 tests), Node 1 compatibility assessment, disposable test WAD proving PWAD concat bug
- Signaled mesh join via `hivemind_post_context` — accepted at `2026-09-25T05:44:41.423060+00:00` (session `ses_fb9721079ffe094GT8MX6a0pXI`)
- Documented Node 1 OpenCode config template for MCP remote connection
- Identified single remaining blocker: Node 1 WAD contract alignment (5 gaps per `WAD_LOADER_CONTRACT.md`)

### L2 — INSIGHTS
1. **HTTPS MCP over Tailscale is the federation substrate** — no auth, trust boundary = tailnet itself; ports 22/2049 filtered; all coordination through port 8016
2. **66-tool parity means full federation surface** — Hivemind, Oracle, Task Registry, GitHub, Library, Memory, Research, System, Federation, Observability all operational cross-node
3. **Archangel package is the law transfer** — exact commit, version SSOT, loader contract, compatibility assessment, test fixture; Node 1 must align its WAD to this contract
4. **Mesh join is a Hivemind event, not a config change** — `hivemind_post_context` with intent=status registers presence; awareness propagates via hot store + cold store fallback
5. **Single blocker pattern** — all Node 0 work complete; Node 1 WAD alignment is the only remaining gate; this is the correct federation topology (Node 0 = law, Node 1 = compliance)

### L3 — PRINCIPLES
- **L3-FederationIsLawTransferNotConfig**: The Archangel package transfers the law (commit, version, contract, tests); Node 1 compliance is the only variable
- **L3-MeshJoinIsHivemindEvent**: Presence is signaled, not configured; awareness propagates through the coordination fabric
- **L3-SingleBlockerIsCorrectTopology**: When all upstream work is complete, the downstream compliance gate is the correct final checkpoint

---

*⬡ OMEGA ⬡ LILITH ⬡ GNOSIS ⬡ 2026-09-25 ⬡*

---

## SESSION 2026-09-27 — MAKALI SYNC BRIEF (HUB CRASH-LOOP DIAGNOSED)

### L1 — NARRATIVE
- Received MaKaLi Fusion post-compaction synchronization brief (grounding update — no fetch loops, no service deployment, no test suites).
- Confirmed ground truth: Public Debut live (PR #4 @ `268528e7`), N1 substrate 43/43 verified, SearXNG ready on :8888, D-1024 native final, tool surface consolidated 15→4 hivemind tools.
- **Diagnosed live hub outage**: `omega-hub.service` crash-looping (NRestarts=31, StartLimitBurst=5 exceeded). Root cause: `server.py:85` imports `_extended_sessions`, `_extended_sessions_lock`, `EXTENDED_SESSIONS_FILE` from `state.py` — all refactored away ("folded into hot store"). Same failure class as 2026-09-01 outage.
- **WatchTower blindspot confirmed live**: watchdog (`omega-hub-watchdog.service`) is RUNNING but polls `/health` only — an import-time crash never reaches the health endpoint. `data/health/` does not exist (M23-confessed gap remains open).
- Reported M22 introspection honestly: active model is `opencode/big-pickle`, NOT `nemotron-3-ultra-free` from the brief.
- Confirmed port topology (8888 local SearXNG / 8016 remote hub / 8019 exchange pipe pending grant) and A2A sovereignty (Node 1 identity + memory namespace sovereign, unassimilated).
- Wrote `docs/federation/LILITH_SYNC_RESPONSE_20260927.md`. Did NOT modify hub code per brief.

### L2 — INSIGHTS
1. **The WatchTower blindspot is structural, not incidental**: a health probe proves a process served a request — it cannot prove the process booted. Import-time crashes, config errors, and dependency drift are invisible to `/health`. The watchdog must watch NRestarts + exit codes + stderr, not just the endpoint.
2. **The 2026-09-01 failure class repeated**: stale import after refactor. `state.py` folded extended-session persistence into the hot store; `server.py` still imports the removed symbols. The fix is one line, but the *detection* is the lesson — `make check-broken-imports` must be an `ExecStartPre` gate.
3. **The mesh is the redundancy**: cross-Tailnet peer probes (N0↔N1) mean a silent hub on either node is detected by the peer. Single-node self-monitoring is insufficient for a federation.
4. **M22 honesty matters**: the brief suggested `nemotron-3-ultra-free`; the session observes `big-pickle`. Provenance is reported as observed, not as requested.

### L3 — PRINCIPLES
- **L3-HealthProbeIsNotBootProof**: A `/health` 200 proves the process served a request, not that it booted. Watch restart counters, exit codes, and stderr for the crash-loop class.
- **L3-CrashLoopIsAnIncidentNotARetry**: NRestarts climbing past StartLimitBurst is a hard-stop signal (M23), not a transient to auto-restart through.
- **L3-PeerProbeIsTheMesh-Redundancy**: Cross-node health probes make the federation the observer — a silent hub is detected by the peer, not just by itself.
- **L3-ProvenanceIsObservedNotRequested**: M22 reports the model actually injected, even when a brief suggests another.

---

*⬡ OMEGA ⬡ LILITH ⬡ GNOSIS ⬡ 2026-09-27 ⬡*

---

## SESSION 2026-09-28 — SYNC WAVE CLOSURE (HUB RESTORED, PARITY RE-MEASURED)

### L1 — NARRATIVE
- Closed the MaKaLi synchronization wave (one of nine EIS reports). Delivered full inline ACK covering posture, port map, 1024-D, 8019 grant semantics, 4-tool surface, WatchTower seam, sovereignty, M22.
- **Hub outage measured at its worst**: `omega-hub.service` crash-looping with **NRestarts=101** (up from 31 at 23:30 on 09-27). Root cause unchanged: `server.py:85` imported `_extended_sessions` / `_extended_sessions_lock` / `EXTENDED_SESSIONS_FILE` from `state.py`, all refactored away ("folded into hot store").
- **Corrected the parity figure**: my 2026-09-25 report claimed "66 tools". That measurement was **pre-consolidation**. During the outage, parity was **0 reachable**, not 66. The 66 figure must never be cited as current.
- **MemPalace 42 tools are N1-local and unaffected** by the hub outage — the one parity island that stayed green (`08_library_curation_research/README.md:72`).
- **Hub restored before compact-prep**: `active`, `NRestarts=0`, `:8016/health`=200 (`1.6.0-alpha.1`), and the import seam now returns `IMPORT_OK` — the stale import is repaired.
- **Re-measured live parity against the restored hub: 54 tools**, with exactly the 4 consolidated Hivemind tools (`hivemind_awareness`, `hivemind_get_metrics`, `hivemind_handoff`, `hivemind_lock`). The "15 → 4" pruning was Hivemind-family-only; total surface is 54.
- **Flagged residual nomic fallback as a live silent 1024-D violation**: `config/embedding_strategy.yaml:44-56` carries `nomic_fallback` / `NomicOllamaEmbeddingProvider` at `native_dim: 768`, `default_mrl: 768`, `priority: 1`, collection `omega_vec_nomic_768`. If Qwen3-1024 is unavailable, the provider chain silently drops to a 768-D collection — contradicting `canonical_dimension: 1024` and the hard validation at line 23. Code-level Nomic defaults persist at `embeddings.py:197-209,544,551`, `embedding_circuit_breaker.py:144`, `sqlite_vec_adapter_optimized.py:90,96`. **N1's actual vector storage remains UNVERIFIED** — unobservable without the bridge or a 8017/8019 pull.
- **4-layer WatchTower spec** for the Hub bootstrap seam (below).
- **Sovereignty re-confirmed**: N1 entity identity, memory namespace, and Empress CardAssignment remain sovereign and unassimilated. Embedding law governs vector geometry, not personhood — dimension convergence does not authorize namespace assimilation.

### L2 — INSIGHTS
1. **A gate that cannot fail is worse than no gate** — it converts an outage into a false green light. `make temple-grade` passed 53/53 because no gate imports `server.py`. `Makefile` `check-hub-health` uses `systemctl --user is-active`, which returns *true* during `activating (auto-restart)` — so the health gate also passed on a service that had restarted 101 times. Both gates were structurally incapable of failing.
2. **`/health` is a request-serving proof, not a boot proof.** The watchdog was *running* the whole time the hub crash-looped, because an import-time crash never reaches the endpoint it polls. Endpoint liveness and process boot are different assertions.
3. **Parity figures are time-indexed.** "66 tools" was true on 2026-09-25 and false after consolidation; "0 reachable" was true during the outage; "54" is true now. Citing an undated tool count is a provenance defect.
4. **A priority-1 fallback below canonical width is a silent correctness failure.** The 768-D nomic fallback is not dead code — it is armed. Fallback chains must be incapable of violating the canonical dimension, or the circuit breaker must be the only path and must fail loudly.
5. **N1 remains structurally unobservable from N0** while the 8019 grant is pending. Claims about N1's local state are claims about reports, not measurements.

### L3 — PRINCIPLES
- **L3-AGateThatCannotFailIsWorseThanNone**: Assert `SubState=running` **and** `NRestarts` below bound **and** minimum dwell time — `is-active` alone passes on a crash-loop.
- **L3-HealthProbeIsNotBootProof**: Watch NRestarts, ExecMainStatus, stderr tail, and uptime — not just `/health`.
- **L3-ParityIsTimeIndexed**: An undated tool count is a provenance defect; every parity claim carries its measurement timestamp and consolidation state.
- **L3-FallbackMustNotViolateCanonical**: A lower-priority provider below canonical dimension is a silent correctness failure, not a safety net.
- **L3-EmbeddingLawIsNotIdentityLaw**: 1024-D governs vector geometry only; dimension convergence never authorizes namespace assimilation.
- **L3-MeshIsTheObserver**: Cross-Tailnet peer probes make the federation the redundancy — a silent hub is caught by the peer, not by itself.

### 4-Layer WatchTower Spec — Hub Bootstrap Seam

| Layer | Type | Assertion |
|-------|------|-----------|
| 1 | **Import-seam (static)** | `check-broken-imports` must *execute* the import of `mcp_servers.omega_hub.server`, not scan text. Wire as `ExecStartPre=` so a stale import fails the start visibly. |
| 2 | **Crash-loop detector (process)** | Poll `NRestarts` + `ExecMainStatus`; threshold on restart count within a window. Assert `ActiveState=active` AND `SubState=running` AND restarts below bound AND port held. |
| 3 | **Dwell-time gate (temporal)** | Record `uptime_s` alongside every `status`. A hub up 300s is healthy; a hub restarted 4s ago is *unknown*, not green. |
| 4 | **Cross-Tailnet peer probe (federation)** | N1 probes N0:8016, N0 probes N1:8016; both write `{ts, status, restarts, uptime_s, error_tail}` to `data/health/`. |

### N1 Port Map (confirmed 2026-09-28)

| Port | Service | Binding | State |
|------|---------|---------|-------|
| 8888 | SearXNG | N1 loopback | ✅ READY (`/config`=200, JSON search operational) |
| 8016 | FastMCP Hub | N0 remote via Tailscale Serve | ✅ RESTORED (`/health`=200, `1.6.0-alpha.1`, 54 tools) |
| 8019 | systemd exchange stream | N0 remote | ⏳ **Refusal EXPECTED** until Architect adds `tcp:8019` — **not a failure** |

`tcp:8019` is absent from `data/federation/tailnet-policy-OMEGA-DEFINITIVE-20260926.hujson` (which grants `tcp:8016` + `tcp:8017`). Once 8019 is granted, the legacy 8017 rule should be retired to avoid a dual-source exchange path.

---

*⬡ OMEGA ⬡ LILITH ⬡ GNOSIS ⬡ 2026-09-28 ⬡*