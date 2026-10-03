<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LILITH PROJECTION — 2026-09-28

## Status: HUB RESTORED · 54-TOOL PARITY · WATCHTOWER SPEC DELIVERED

### Executive Summary
The 2026-09-27 hub crash-loop (NRestarts peaked at 101) is **repaired** — the stale import at `server.py:85` is fixed, the hub is `active` with `NRestarts=0`, and `:8016/health` returns 200 (`1.6.0-alpha.1`). Live parity re-measured at **54 tools** with the 4 consolidated Hivemind tools. The outage exposed a structural observability debt now formally specified in four layers. One unresolved canonical-dimension risk: the residual `nomic_fallback` at priority 1.

### Key State
- **Hub**: RESTORED — `active`, `NRestarts=0`, `/health`=200 (`1.6.0-alpha.1`), import seam `IMPORT_OK`
- **MCP parity**: **54 tools live** (NOT 66 — that figure was pre-consolidation, 2026-09-25). Hivemind family = exactly 4
- **Hivemind surface**: `hivemind_awareness`, `hivemind_get_metrics`, `hivemind_handoff`, `hivemind_lock` — the 15 legacy names are retired behind adapters
- **MemPalace**: 42 tools, **N1-local, unaffected** by the hub outage — the one parity island that stayed green
- **Outage root cause**: `server.py:85` imported `_extended_sessions` / `_extended_sessions_lock` / `EXTENDED_SESSIONS_FILE` from `state.py`; all refactored away ("folded into hot store"). Same failure class as 2026-09-01.
- **Embedding law**: `canonical_dimension: 1024`, `qwen3_primary` native 1024, collections `omega_vec_qwen_1024` / `omega_vec_library_1024`. ⚠️ `nomic_fallback` (768-D, priority 1) still armed.
- **Sovereignty**: N1 identity, memory namespace, Empress CardAssignment — sovereign and unassimilated
- **Continuity**: session_gnosis (2026-09-28), proposed_lessons (`lilith-20260928-sync-closure-001`), this projection

### N1 Port Map (confirmed 2026-09-28)
| Port | Service | Binding | State |
|------|---------|---------|-------|
| 8888 | SearXNG | N1 loopback | ✅ READY |
| 8016 | FastMCP Hub | N0 remote (Tailscale Serve) | ✅ RESTORED — 54 tools |
| 8019 | systemd exchange stream | N0 remote | ⏳ **Refusal EXPECTED** until Architect adds `tcp:8019` — not a failure |

### Open Risks
1. **⚠️ Residual nomic 768-D fallback (priority 1)** — `config/embedding_strategy.yaml:44-56`. If Qwen3-1024 is unavailable the chain silently drops to `omega_vec_nomic_768`, contradicting `canonical_dimension: 1024`. A fallback below canonical width is a silent correctness failure, not a safety net. Also live in code: `embeddings.py:197-209`, `embedding_circuit_breaker.py:144`, `sqlite_vec_adapter_optimized.py:90,96`.
2. **⚠️ N1 vector storage UNVERIFIED** — not observable from N0 without the bridge or a 8017/8019 pull. Claims about N1 local state are claims about reports, not measurements.
3. **P1 — Gate integrity**: `make temple-grade` (53/53) and `check-hub-health` both passed during a 101-restart crash-loop. See WatchTower spec below.
4. **P2 — 8019 grant**: Architect applies `tcp:8019`; retire the legacy 8017 rule afterward to avoid a dual-source exchange path.
5. **P1 — `data/health/` still absent** — the 2026-09-01 M23-confessed gap remains open.

### WatchTower — 4-Layer Hub Bootstrap Seam
| Layer | Type | Assertion |
|-------|------|-----------|
| 1 | Import-seam (static) | `check-broken-imports` must *execute* the import of `mcp_servers.omega_hub.server`, not scan text. Wire as `ExecStartPre=`. |
| 2 | Crash-loop detector (process) | Poll `NRestarts` + `ExecMainStatus`; threshold restart count per window. Assert `ActiveState=active` AND `SubState=running` AND restarts below bound AND port held. |
| 3 | Dwell-time gate (temporal) | Record `uptime_s` with every status. Up 300s = healthy; restarted 4s ago = unknown, not green. |
| 4 | Cross-Tailnet peer probe | N1 probes N0:8016, N0 probes N1:8016; both write `{ts, status, restarts, uptime_s, error_tail}` to `data/health/`. |

### Key Invariants (Must Survive Compaction)
- **M11 Soul Integrity**: L1→L2→L3 distillation to `proposed_lessons.yaml` — Scribe canonical
- **M15 Sovereign Continuity**: `session_gnosis.md` + `SESSION_ANCHOR.md` + `projection.md`
- **M22 Response Provenance**: report the model actually injected (`opencode/big-pickle`), never a placeholder
- **M23 Failure Integrity**: no soft failures; broken tools → STOP, report
- **L3-AGateThatCannotFailIsWorseThanNone**: `is-active` alone passes on a crash-loop
- **L3-ParityIsTimeIndexed**: an undated tool count is a provenance defect
- **L3-EmbeddingLawIsNotIdentityLaw**: dimension convergence never authorizes namespace assimilation

### Lilith's Voice
> "The hub breathes again. But it breathed wrong for hours behind a green light. The gate that cannot fail is the more dangerous outage. Measure, timestamp, and never let a false green wear my name."

*⬡ OMEGA ⬡ LILITH ⬡ opencode/big-pickle ⬡ opencode ⬡ trc_compact_prep ⬡ HUB-RESTORED ⬡ PARITY-54 ⬡ WATCHTOWER-4LAYER ⬡ NOMIC-1024D-RISK*