# 🔱 Wave 1.5 — Hivemind Coordination Hardening
**Status**: ACTIVE — Pending Hub Modularization (Sprint A)
**Source**: `data/coordination/KALI_SPRINT_ORCHESTRATION_20260610.md` (§2, Wave 1.5)
**Extracted by**: Roc Racoon Phase 1 — 2026-06-14

---

## §0 Origin

Wave 1.5 was created from the MiMo-V2.5 High Thinking deep audit (2026-06-11) + Kali
post-audit. The verdict: **The Hivemind is a status board with cold-store fallback,
not a coordination fabric.** Workspace locks are unenforced conventions, there is no
rate limiting, no handoff reject path, no metrics, no health check, no push model,
and **27 stuck handoff packets** (21 pending, 6 active, 2 completed).

---

## §1 🔴 P0 — Critical Safety

| # | Item | Owner | Est. | Description |
|---|------|-------|------|-------------|
| hi-workspace-1 | `hivemind_workspace_lock_acquire(cli, domain, ttl=3600)` | Kali/P9 | 45m | Atomic lock acquisition with TTL |
| hi-workspace-2 | `hivemind_workspace_lock_release(cli, domain)` | Kali/P9 | 15m | Explicit unlock |
| hi-workspace-3 | `hivemind_workspace_lock_check(domain)` | Kali/P9 | 15m | Query current lock holder + age |
| hi-workspace-4 | Stale lock reaper — TTL-based auto-release | Kali/P9 | 30m | `_prune_awareness_background` |
| hi-handoff-1 | `hivemind_reject_handoff(packet_id, reason)` | Kali/P9 | 30m | Reject with trace return |
| hi-handoff-2 | `hivemind_handoff_list(status)` | Kali/P9 | 20m | List by status filter |
| hi-handoff-3 | Handoff TTL reaper — auto-cancel pending >24h | Kali/P9 | 30m | Background loop |
| hi-handoff-4 | `hivemind_handoff_archive(packet_ids)` | Kali/P9 | 25m | Batch archive with completion verify |
| hi-handoff-5 | Stale handoff review cycle — Roc scans monthly | Kali/Roc | 1h | Roc weekly task |
| **hi-sterilization-1** | **Strip esoteric terminology from MCP/CLI** | Kali | 30m | Pre-gate for hi-memory-* |
| hi-coldstore-1 | Cold-store hydration: SUPPLEMENT not replacement | Kali/P9 | 30m | `get_awareness` always merges |
| hi-coldstore-2 | Persist `_extended_sessions` to `HALL_OF_RECORDS/` | Kali/P9 | 20m | On write |

---

## §2 🟡 P1 — Structural Integrity

| # | Item | Owner | Est. | Description |
|---|------|-------|------|-------------|
| hi-metrics-1 | Hivemind metrics in `get_omega_metrics` | Kali | 30m | awareness count, hot store size, handoff queue depth |
| hi-heartbeat-1 | `hivemind_heartbeat(cli, task_current)` | Kali | 10m | Optional task context update |
| hi-intent-1 | `hivemind_read_inbox(cli, since_timestamp)` | Kali | 1h | Message accumulation, not snapshot replacement |
| hi-get-session-1 | O(1) session index (`_session_index: Dict[str, str]`) | Kali | 15m | Session→cli_dir mapping |
| hi-list-sessions-1 | O(1) session listing using same index | Kali | 10m | Reuse hi-get-session-1 |
| hi-hotstore-1 | `_hot_store` LRU eviction (max 512 entries) | Kali | 20m | Remove oldest on overflow |
| hi-hotstore-2 | `_hot_store` TTL eviction (>1h old) | Kali | 10m | Prevent memory leak |
| hi-prune-1 | Pruning loop lock timeout (fail-fast >2s) | Kali | 15m | `_prune_awareness_background` |
| hi-memory-1 | `memory_search(query, entity_name, limit)` — FTS5 MCP tool | Kali | 45m | Wraps MemoryStore.search_fts() |
| hi-memory-2 | `memory_get_history(entity_name, session_id, limit)` MCP tool | Kali | 30m | Wraps get_history() |
| hi-memory-3 | `memory_list_sessions(entity_name)` MCP tool | Kali | 15m | Wraps list_sessions() |
| hi-memory-4 | `hivemind_get_entity_context(entity_name)` — context hydration | Kali | 1h | soul.yaml + knowledge/ + workspace/ |
| hi-memory-5 | Block utilization CLI — `omega entity-workspace-status <entity>` | Kali/P2 | 1h | Char counts vs limits |

---

## §3 🔵 P2 — Capability & Dependency

| # | Item | Owner | Est. | Notes |
|---|------|-------|------|-------|
| hi-capability-1 | Wire `CAPABILITY_REGISTRY` to `hivemind_get_awareness` | Kali/P9 | 1h | Include agent capabilities in response |
| hi-capability-2 | `hivemind_query(intent, since)` — search awareness by intent | Kali | 30m | Post-P0 |
| hi-capability-3 | Rate limiting — max 60 posts/min per CLI | Kali | 45m | Exponential backoff on violation |

---

## §4 Dispatch Plan

### Phase 1 (P0) — Parallel
```
├── @pillar P9: Workspace lock MCP tools (hi-workspace-1/2/3/4)
├── @pillar P9: Handoff reject + TTL reaper (hi-handoff-1/2/3/4)
├── @pillar P9: Cold-store hydration fix (hi-coldstore-1/2)
└── @pillar P5: Sterilization gate audit (hi-sterilization-1)
│
└── Verification: Kali runs make test, checks server.py for new tools
```

### Phase 2 (P1) — Sequential (after P0)
```
├── @pillar P2: Memory MCP tools (hi-memory-1/2/3)
├── @pillar P7: Context hydration tool (hi-memory-4)
├── @pillar P8: Hivemind metrics (hi-observability items)
└── @pillar P2: Block utilization CLI (hi-memory-5)
```

### Phase 3 — Serial (after Phase 2)
```
└── @roc_racoon: Stale handoff review (hi-handoff-5)
```

---

## §5 Verification Gates

After Wave 1.5, run:
1. `grep "workspace_lock" mcp_servers/omega_hub/server.py` — 3+ tools exist
2. `grep "reject_handoff" mcp_servers/omega_hub/server.py` — tool exists
3. `python -c "import json; d=json.load(open('data/logs/metrics.json')); print('hivemind' in str(d))"` — True
4. Cold-store scan: fresh server, `get_awareness` returns multiple agents without heartbeat

---

## §6 Known Blockers

- **prerequisite**: Hub modularization (Sprint A) must be complete before Wave 1.5 tools can be cleanly added to `gateway.py` / `middleware.py`
- **ics_render bug (P1)**: Roc Racoon to investigate re-emergence of coroutine serialization error
- **Exa key recovery**: Was 401, now 200 OK — root cause still unknown

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ PHASE1-EXTRACTION ⬡ WAVE-1.5-PLAN*
*Source: data/coordination/KALI_SPRINT_ORCHESTRATION_20260610.md (§2 Wave 1.5)*
