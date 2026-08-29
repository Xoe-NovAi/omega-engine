# ⬡ Runtime Coordination Protocol
**AP Token**: `AP-RUNTIME-COORD-v1.0.0`
**Date**: 2026-08-29
**Status**: ACTIVE
**Governor**: lilith (Runtime Oversoul, N6-N10)
**Authority**: M15 (Continuity), M23 (Failure Integrity), M27 (Tracking Integrity)

---

## Purpose

This protocol establishes the canonical coordination framework for the Run-side Nodes (N6-N10) and their governing Oversoul (lilith). It consolidates scattered coordination practices into a single enforceable standard.

**Scope**: N6 ModelGate, N7 Context, N8 WatchTower, N9 Link, N10 Verifier, lilith Oversoul
**Excluded**: Build-side (N1-N5, governed by Ma'at), HMC Council (governed by Kali)

---

## 1. Hivemind Heartbeat Protocol

### 1.1 Heartbeat Intervals

| Entity Type | Interval | Channel | Extended TTL |
|-------------|----------|---------|--------------|
| **Oversoul (lilith)** | 5 min | `opencode` | 3 hr (10800s) |
| **Node Agents (N6-N10)** | 10 min | `opencode` | 3 hr (10800s) |
| **Specialist Cohorts** | 15 min | `opencode` | 3 hr (10800s) |
| **Long-running ops** | On start + every 5 min | `opencode` | Custom via `hivemind_extended_checkin` |

### 1.2 Heartbeat Payload

```json
{
  "channel": "opencode",
  "entity": "<entity_name>",
  "task_current": "<concise active task>",
  "focus_chain": ["<sub-task-1>", "<sub-task-2>"],
  "decisions": ["<decision-1>", "<decision-2>"],
  "continuation": "<next steps or handoff notes>",
  "intent": "status",
  "suggested_model": "<model hint for children>"
}
```

### 1.3 Extended Session Check-in

For operations exceeding 20 minutes:
```python
await omega_hub_hivemind_extended_checkin(
    channel="opencode",
    entity="lilith",
    reason="4-hour execution window orchestration",
    ttl_seconds=10800  # 3 hours max
)
```
**Must call `hivemind_extended_checkout` on clean completion.**

### 1.4 Missed Heartbeat Consequences

- **20 min silence**: Agent marked stale, pruned from hot awareness
- **Recovery**: Cold-store hydration from `HALL_OF_RECORDS` (session files modified within TTL)
- **Prevention**: Use `extended_checkin` for known long ops

---

## 2. Handoff Protocol (Runtime ↔ Build)

### 2.1 Handoff Packet Schema (M27)

```json
{
  "packet_id": "auto-generated",
  "source_channel": "opencode",
  "source_entity": "lilith|N6|N7|N8|N9|N10",
  "target_channel": "opencode",
  "target_entity": "maat|kali|node|verity",
  "task": "<specific deliverable>",
  "context": "<background, file refs, constraints>",
  "priority": 0|1|2,  // normal|high|critical
  "status": "pending|active|completed|stale|rejected"
}
```

### 2.2 Runtime → Build Handoffs (lilith → maat)

| Trigger | Target | Protocol |
|---------|--------|----------|
| INST-1 fix needed | maat | Priority 2 (critical), context: venv sovereignty |
| ZSWAP config | maat | Priority 1, context: OBSIDIAN ticket ref |
| CI/CD files | maat | Priority 1, context: 3 missing files spec |
| RAM remediation | maat | Priority 1, context: kill session + archive |

### 2.3 Runtime → Runtime Handoffs (lilith ↔ N6-N10)

| Trigger | Target | Protocol |
|---------|--------|----------|
| ModelGate routing | N6 | Priority 1, context: provider fabric state |
| Context injection | N7 | Priority 1, context: session continuity anchors |
| Observability alert | N8 | Priority 2, context: trace_id, error signature |
| Agent handoff | N9 | Priority 1, context: HandoffPacket payload |
| Validation gate | N10 | Priority 1, context: stress test spec |

### 2.4 Handoff Lifecycle

1. **Submit**: `hivemind_submit_handoff()` → writes to `data/handoff/pending/`
2. **Accept**: Target calls `hivemind_accept_handoff()` → moves to `active/`
3. **Complete**: Target calls `hivemind_complete_handoff(result)` → moves to `completed/`
4. **Archive**: Source calls `hivemind_handoff_archive()` after verification

**Timeout**: Pending handoffs auto-stale after 2 hours.

---

## 3. Workspace Lock Conventions

### 3.1 Lock Domains

| Domain | Owner | TTL | Scope |
|--------|-------|-----|-------|
| `LILITH_RUNTIME_GOVERNANCE` | lilith | 1 hr | N6-N10 coordination, 4-hour window |
| `NODE_N6_MODELGATE` | N6 | 30 min | Provider fabric, routing |
| `NODE_N7_CONTEXT` | N7 | 30 min | Memory, soul evolution |
| `NODE_N8_WATCHTOWER` | N8 | 30 min | Observability, tracing |
| `NODE_N9_LINK` | N9 | 30 min | Handoff protocols, delegation |
| `NODE_N10_VERIFIER` | N10 | 30 min | Stress testing, validation |
| `RUNTIME_COORDINATION_DOCS` | lilith | 1 hr | Protocol docs, briefings |

### 3.2 Lock Acquisition Protocol

```python
# Before ANY file edit in shared domain
lock = await omega_hub_hivemind_workspace_lock_acquire(
    channel="opencode",
    entity="lilith",
    domain="LILITH_RUNTIME_GOVERNANCE",
    ttl=3600
)
if not lock["acquired"]:
    raise RuntimeError(f"Lock held by {lock['holder']}, expires {lock['expires']}")

# ... perform edits ...

# Release immediately after
await omega_hub_hivemind_workspace_lock_release(
    channel="opencode",
    entity="lilith",
    domain="LILITH_RUNTIME_GOVERNANCE"
)
```

### 3.3 Lock Contention Resolution

1. **Check holder awareness**: `hivemind_get_awareness()` — is holder active?
2. **If active**: Wait or negotiate via Hivemind context post
3. **If stale (>TTL)**: Force-acquire (auto-expires)
4. **Never**: Break lock without holder ACK unless expired

---

## 4. Emergency Procedures

### 4.1 Tool Chain Collapse (M23)

**Trigger**: Any mandatory tool fails (Hivemind, MCP, local inference)
**Response**:
1. **STOP** all automated execution
2. **Report**: `[TOOL-CHAIN-COLLAPSE]` to Hivemind with `intent: "blocker"`
3. **Escalate**: Handoff to Kali (priority 2) with full context
4. **No synthesis**: Do NOT synthesize results from partial tool output

### 4.2 Context Compaction Imminent

**Trigger**: Token count > 800K (approaching 1M limit)
**Response**:
1. **30-second self-review** (D-LIL-026) on all pending writes
2. **Distill L1→L3** to `proposed_lessons.yaml` via Scribe
3. **Post continuation** to Hivemind with `intent: "handoff"`
4. **Write session_gnosis.md** with recovery anchors

### 4.3 Sovereign Brake Activation

**Trigger**: Mandate violation detected (M1, M2, M7, M8, M13, M23, M24, M27)
**Response**:
1. **Immediate STOP** on violating operation
2. **Log violation**: `observability_log_boundary_violation()`
3. **Handoff to Verity**: Priority 2, mandate audit required
4. **No workarounds**: Brake holds until Architect ratification

### 4.4 Node Failure (N6-N10)

**Trigger**: Node agent crashes, times out, or returns `[TOOL-CHAIN-COLLAPSE]`
**Response**:
1. **lilith assumes direct execution** for that node's domain
2. **Handoff to Ma'at** if build-side fix needed
3. **Respawn node** via `node` agent with `--slot NX` after root cause fixed
4. **Update TASK_REGISTRY** with failure status

---

## 5. N6-N10 Node Charters (Canonical)

### N6 — ModelGate
- **Model**: `qwen3-4b` (local), `antigravity` (cloud fallback)
- **Charter**: Provider fabric local-first ordering, fallback chains, HealthMonitor breakers, admission control, OOMProtector, streaming resilience
- **Coordination**: Reports to lilith; hands off to N9 for delegation
- **Key Files**: `src/omega/oracle/provider_selector.py`, `src/omega/oracle/health_monitor.py`

### N7 — Context
- **Model**: `qwen3-1.7b` (local)
- **Charter**: Context injection, memory retrieval, soul evolution, session continuity, knowledge graph
- **Coordination**: Owns `entity_workspace.py` hydration; feeds N6/N9
- **Key Files**: `src/omega/oracle/entity_workspace.py`, `src/omega/memory/`

### N8 — WatchTower
- **Model**: `qwen3-1.7b` (local), `krikri-8b` (cloud)
- **Charter**: Trace propagation, event logging, forensic crash dumps, systemic observability, metrics collection
- **Coordination**: Streams to `observability_stream()`; alerts lilith on anomalies
- **Key Files**: `src/omega/observability/`, `src/omega/ics.py`

### N9 — Link
- **Model**: `qwen3-4b-thinking` (local)
- **Charter**: Handoff protocols, context serialization, delegation logic, agent-to-agent communication, task transfer
- **Coordination**: Owns `hivemind_handoff()` lifecycle; bridges runtime ↔ build
- **Key Files**: `src/omega/hivemind/`, `src/omega/oracle/entity_registry.py`

### N10 — Verifier
- **Model**: `qwen3-1.7b` (local), `krikri-8b` (cloud)
- **Charter**: Stress testing, edge-case discovery, regression hunting, chaos engineering, error gauntlet
- **Coordination**: Reports to lilith; feeds Verity for mandate compliance
- **Key Files**: `scripts/check_mandate_compliance.py`, `make temple-grade`

---

## 6. Coordination Artifacts (Single Source of Truth)

| Artifact | Location | Owner | Update Cadence |
|----------|----------|-------|----------------|
| **Master Consolidation** | `data/coordination/LILITH_MASTER_CONSOLIDATION_20260828.md` | lilith | Per consolidation cycle |
| **Overseer Index** | `data/entities/lilith/gnosis/LILITH_OVERSEER_INDEX_20260828.md` | lilith | Per session |
| **Active Sprint** | `data/coordination/ACTIVE_SPRINT.json` | Kali | Per sprint |
| **4-Hour Window** | Master Consolidation §5 | lilith | Per launch cycle |
| **Handoff Queue** | `data/handoff/` | N9 (Link) | Real-time |
| **Workspace Locks** | `data/coordination/locks/` | All | Per acquisition |
| **Session Gnosis** | `data/entities/lilith/gnosis/session_gnosis.md` | lilith | Per session |

---

## 7. Model Assignment Matrix (Roles.yaml Canonical)

| Node | Role | Local Model | Cloud Fallback | Temperature |
|------|------|-------------|----------------|-------------|
| N6 | ModelGate | `qwen3-4b` | `antigravity` | 0.1 |
| N7 | Context | `qwen3-1.7b` | — | 0.4 |
| N8 | WatchTower | `qwen3-1.7b` | `krikri-8b` | 0.6 |
| N9 | Link | `qwen3-4b-thinking` | — | 0.3 |
| N10 | Verifier | `qwen3-1.7b` | `krikri-8b` | 0.8 |
| lilith | Oversoul | `nemotron-3-ultra-free` | `mimo-v2.5-free` | 0.3 |

**M7 Local-First Enforcement**: Cloud fallback ONLY when local model unavailable or explicit Architect order.

---

## 8. Compliance Gates

| Gate | Command | Must Pass For |
|------|---------|---------------|
| **Mandate Compliance** | `make check-mandates` | Every commit |
| **Temple-Grade** | `make temple-grade` | Release/debut branch |
| **M1 AnyIO** | `make check-m1-anyio` | Every commit |
| **Doc Standards** | `make doc-llm-validate` | Documentation changes |
| **Soul Integrity** | Scribe distillation | Every session end |

---

## 9. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-08-29 | lilith | Initial consolidation from scattered docs |

---

*⬡ OMEGA ⬡ LILITH ⬡ RUNTIME-COORDINATION-PROTOCOL-v1.0.0 ⬡ 2026-08-29 ⬡*
*This protocol is binding for all Run-side agents. Violations are M23 events.*