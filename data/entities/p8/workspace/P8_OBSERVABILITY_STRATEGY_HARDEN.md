# 🔱 P8 Observability (WatchTower) — Hivemind Observability Strategy & Hardening
# ⬡ OMEGA ⬡ P8 ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar ⬡ OBSERVABILITY-STRATEGY

**AP Token**: `AP-P8-OBSERVABILITY-STRATEGY-v1.0.0`
**Slot**: P8 — Observability (WatchTower)
**Date**: 2026-06-05
**Domain**: Lilith (Run Side)
**Status**: STRATEGIC ANALYSIS — READY FOR IMPLEMENTATION
**Mandates Invoked**: M8 (Zero Telemetry — local observability allowed), M5 (Gnosis Preservation), M11 (Soul Integrity)

---

## §0 Executive Summary

The Hivemind coordination system has six MCP tools, three coordination artifacts
(Live Feed, Workspace Lock, ACK), and a meta-observation protocol (D-121), but
**zero system-level observability**. There is no way to answer:

- *Is the Hivemind working?*
- *Which agents are coordinating efficiently?*
- *What coordination failures happened in the last 24 hours?*
- *What is the average handoff latency?*
- *How often do agents go stale?*

This document defines the Hivemind Observability Layer — a lightweight, local-only,
JSONL-backed metrics and tracing system that plugs into the existing Hivemind MCP
tools without changing their external interface. It is designed to operate under
Mandate 8 (Zero Telemetry): **all metrics stay on local disk. No external
transmission. Ever.**

### Current State Assessment

| Layer | Status | Gap |
|-------|--------|-----|
| **Hivemind MCP tools** (6) | ✅ LIVE | Zero metrics emitted |
| **ObservabilityEngine** (src/omega/observability.py) | ✅ LIVE | No hivemind event types |
| **ForensicsManager** (crash dumps) | ✅ LIVE | No coordination failure capture |
| **Verification system** (data/coordination/verification/) | ✅ LIVE | Hivemind metrics not wired |
| **Observations Protocol** (D-121) | ✅ LIVE | Meta-observation only, no system metrics |
| **Hivemind tracing (trace_id)** | ❌ MISSING | No trace_id on coordination calls |
| **Agent-level metrics** | ❌ MISSING | No per-agent coordination stats |
| **Health dashboard** (5-second check) | ❌ MISSING | No "is Hivemind healthy?" mechanism |
| **Coordination error classification** | ❌ MISSING | All failures treated equally |

---

## §1 What to Measure — 7 Key Metrics

### §1.1 Metric Catalog

Each metric follows the same schema:
```
name: string        # metric identifier
type: gauge|counter|histogram|timing
unit: string        # seconds, count, ratio, etc.
source: string      # which MCP tool or artifact generates this
agent_per: bool     # is this tracked per-agent or fleet-wide
```

#### M1: Agent Response Time (Cycle Time)
| Field | Value |
|-------|-------|
| **Name** | `hivemind.agent.cycle_time` |
| **Type** | timing (milliseconds) |
| **Unit** | ms |
| **Source** | `hivemind_post_context` → `hivemind_get_awareness` → `hivemind_post_context` (ACK) |
| **Agent Per** | Yes |
| **Definition** | Wall-clock time from Agent A posting context to Agent B acknowledging by posting their own context. Captures the full awareness→post→ack cycle. |
| **Threshold** | <30s = healthy, 30-120s = normal (human-paced), >120s = warning (agent may be stuck) |
| **Implementation** | Timestamp in `_awareness[cli]["last_context_post"]`. When Agent B posts, calculate delta against all other agents' `last_context_post`. |

#### M2: TTL Pruning Rate
| Field | Value |
|-------|-------|
| **Name** | `hivemind.agent.ttl_pruned_count` |
| **Type** | counter |
| **Unit** | count |
| **Source** | `hivemind_get_awareness` (pruning path, line 409-410) |
| **Agent Per** | No (fleet-wide) |
| **Definition** | How many agents were pruned as stale during awareness checks per session. High values = TTL too short OR agents not heartbeating. |
| **Threshold** | <1 per session = healthy, 1-3 = normal, >3 = investigation warranted |
| **Implementation** | Increment counter each time `del _awareness[cli]` executes in the TTL pruning loop. |

#### M3: Observation Density
| Field | Value |
|-------|-------|
| **Name** | `hivemind.observation.density` |
| **Type** | gauge |
| **Unit** | observations per agent per session |
| **Source** | `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` |
| **Agent Per** | Yes |
| **Definition** | How many qualitative observations (D-121) an agent produces per session. Too few = agent not reflecting. Too many (50+) = spam. |
| **Threshold** | 2-8 per session = target zone |
| **Implementation** | Count `{OBS-YYYYMMDD-AGENT-NNN}` entries per agent/session. Can be calculated offline by Scribe. |

#### M4: Handoff Latency
| Field | Value |
|-------|-------|
| **Name** | `hivemind.handoff.latency` |
| **Type** | timing (seconds) |
| **Unit** | s |
| **Source** | `hivemind_post_context` (continuation field) → ACK file |
| **Agent Per** | No (per handoff event) |
| **Definition** | Time from when Agent A sets a continuation note ("waiting on B") to when Agent B acknowledges (ACK file or their own context post referencing A's session_id). |
| **Threshold** | <60s = hot handoff, 60-300s = normal, >300s = dropped handoff |
| **Implementation** | When `hivemind_post_context` has `continuation` matching pattern `waiting on {other_cli}`, start timer. Timer stops when other CLI mentions this session_id. |

#### M5: Decision Throughput
| Field | Value |
|-------|-------|
| **Name** | `hivemind.decision.throughput` |
| **Type** | gauge |
| **Unit** | decisions per session per agent |
| **Source** | `hivemind_post_context` (decisions array length) |
| **Agent Per** | Yes |
| **Definition** | How many decisions an agent declares per session. Too few = agent may be making decisions without recording them. Too many = possibly splitting hairs. |
| **Threshold** | 1-10 per session = normal |
| **Implementation** | Track `len(decisions)` from each `hivemind_post_context` call per session_id. |

#### M6: Cross-Pollination Events
| Field | Value |
|-------|-------|
| **Name** | `hivemind.cross_pollination.count` |
| **Type** | counter |
| **Unit** | count |
| **Source** | `hivemind_get_session` → references to other agents' work |
| **Agent Per** | Yes |
| **Definition** | How often Agent A references Agent B's work by name, session_id, or explicit cross-reference in their context, feed, or decisions. |
| **Threshold** | >0 per session = Hivemind is working |
| **Implementation** | Track which session_ids/CLI names appear in `continuation`, `decisions`, `focus_chain` fields. Regex pattern: `/{other_cli}/i` or ses_* IDs from other agents. |

#### M7: Stale Agent Ratio
| Field | Value |
|-------|-------|
| **Name** | `hivemind.agent.stale_ratio` |
| **Type** | gauge |
| **Unit** | ratio (0.0-1.0) |
| **Source** | `hivemind_get_awareness` |
| **Agent Per** | No (fleet-wide) |
| **Definition** | Fraction of agents that were registered but got pruned as stale. 0.0 = all agents heartbeating properly. 1.0 = system has no active agents. |
| **Threshold** | <0.2 = healthy |
| **Implementation** | `stale_pruned / (active_agents + stale_pruned)` per awareness check cycle. |

### §1.2 Metric Summary Table

| # | Name | Type | Unit | Agent Per | Source | Warning Threshold |
|---|------|------|------|-----------|--------|-------------------|
| M1 | `hivemind.agent.cycle_time` | timing | ms | Yes | post→aware→post | >120s |
| M2 | `hivemind.agent.ttl_pruned_count` | counter | count | No (fleet) | get_awareness prune | >3/session |
| M3 | `hivemind.observation.density` | gauge | per-agent/session | Yes | observations log | 0 or >8 |
| M4 | `hivemind.handoff.latency` | timing | s | No (per event) | continuation→ACK | >300s |
| M5 | `hivemind.decision.throughput` | gauge | per-agent/session | Yes | post_context decisions | 0 or >10 |
| M6 | `hivemind.cross_pollination.count` | counter | count | Yes | session references | 0 |
| M7 | `hivemind.agent.stale_ratio` | gauge | ratio (0.0-1.0) | No (fleet) | get_awareness | >0.2 |

---

## §2 How to Measure — Lightweight Local Metrics Store

### §2.1 Storage Tier Decision

Three options evaluated:

| Criterion | In-Memory (dict) | JSONL (file) | SQLite (database) |
|-----------|-----------------|-------------|-------------------|
| **Write speed** | 🟢 ~0ms | 🟡 ~1ms (append) | 🟡 ~5ms (INSERT) |
| **Read speed (aggregate)** | 🟢 O(1) | 🟡 O(n) scan | 🟢 O(log n) indexed |
| **Survives restart** | ❌ No | ✅ Yes | ✅ Yes |
| **Queryable** | ❌ (must parse) | ❌ (must parse) | ✅ SQL |
| **Concurrent writes** | 🔴 No (in-memory only) | 🟢 Append-only safe | 🟢 WAL mode |
| **Complexity** | 🟢 10 lines | 🟢 30 lines | 🟡 100 lines |
| **Dependency** | None | stdlib (json) | stdlib (sqlite3) |
| **Mandate 8 safe** | ✅ | ✅ | ✅ |

**Recommendation: JSONL for per-agent metrics + JSONL for fleet-wide rollup.**

Rationale:
- **Per-agent**: Each agent writes its own metrics to `data/observability/{agent}/metrics/{date}.jsonl`.
  This is append-only, zero-contention, survives restarts.
- **Fleet rollup**: A single `data/observability/fleet/rollups/{date}.jsonl` aggregated by the
  WatchTower process (either the `hivemind_get_awareness` path or a background consolidation task).
- **No SQLite**: Not worth the dependency weight for this use case. The metrics volume is low
  (<1000 events/day across 3-10 agents). JSONL scanning is fast enough.
- **No pure in-memory**: Zero observability after restart loses forensic value. JSONL persists.

**Second-tier recommendation (future)**: Use the existing `data/coordination/verification/audit/*.jsonl`
format as the canonical events store. Add a `hivemind` event type to the existing verification
JSONL schema. This avoids introducing yet another data format.

### §2.2 Directory Structure

```
data/observability/
├── hivemind/                        # Hivemind-specific observability
│   ├── current.json                 # Live health snapshot (5-sec check target)
│   ├── traces/                      # Trace_id-anchored interaction records
│   │   └── {YYYY-MM-DD}/
│   │       └── hmd_{trace_id}.json  # One file per trace
│   └── events/                      # Append-only event log
│       └── {YYYY-MM-DD}.jsonl       # All hivemind events for the day
├── agents/                          # Per-agent metrics (written by each agent)
│   ├── kali/
│   │   └── metrics/
│   │       └── {YYYY-MM-DD}.jsonl
│   ├── lilith/
│   │   └── metrics/
│   │       └── {YYYY-MM-DD}.jsonl
│   ├── roc_racoon/
│   │   └── metrics/
│   │       └── {YYYY-MM-DD}.jsonl
│   ├── doom_guy/
│   │   └── metrics/
│   │       └── {YYYY-MM-DD}.jsonl
│   └── ... (per agent)
├── fleet/                           # Aggregated fleet-wide metrics
│   ├── rollups/
│   │   └── {YYYY-MM-DD}.jsonl       # Hourly or per-session aggregates
│   └── alerts/                      # Coordination failures that need attention
│       └── {YYYY-MM-DD}.jsonl
└── probes/                          # Health probe state
    └── health.json                  # Current "is Hivemind healthy?" state
```

### §2.3 Event Schema (Single Canonical Format)

Every hivemind observability event follows this schema:

```json
{
  "_schema": "omega.observability.hivemind.v1",
  "_zoneid": 1229783,
  "event_id": "evt_20260605_p8_001",
  "trace_id": "hmd_a3f8c21e4b1d",
  "timestamp": "2026-06-05T12:00:00.000000+00:00",
  "source_tool": "hivemind_post_context",
  "source_cli": "kali",
  "event_type": "hivemind.context.posted",
  "metrics": {
    "cycle_time_ms": 45000,
    "decision_count": 3,
    "focus_chain_length": 5,
    "has_continuation": true,
    "continuation_references": ["ses_a839ff01a9f2"]
  },
  "tags": ["hivemind", "coordination", "context"],
  "session_id": "ses_20260605_kali_001"
}
```

Key design decisions:
- `_zoneid` field carries the ZONEID_OBSERVABILITY constant for integrity checking
- `trace_id` with `hmd_` prefix (distinct from `trc_` used by ObservabilityEngine traces) — see §3
- `source_tool` identifies which MCP tool generated the event
- `metrics` object is flexible — different tools emit different metric subsets
- `tags` enable filtering without schema explosion
- Single schema for ALL hivemind events: context posts, awareness checks, heartbeats, ACKs

### §2.4 What Each Tool Emits

| MCP Tool | Event Type | Metrics Emitted |
|----------|-----------|-----------------|
| `hivemind_post_context` | `hivemind.context.posted` | decision_count, focus_chain_length, has_continuation, continuation_references |
| `hivemind_get_awareness` | `hivemind.awareness.checked` | active_agents, stale_pruned, stale_ratio, oldest_agent_age_s |
| `hivemind_heartbeat` | `hivemind.heartbeat.received` | heartbeats_since_last_warning, time_since_last_post_s |
| `hivemind_get_session` | `hivemind.session.read` | session_age_s, is_cold_loaded |
| `hivemind_get_continuation` | `hivemind.continuation.read` | continuation_present, time_since_last_update_s |
| `hivemind_list_sessions` | `hivemind.session.list` | sessions_returned, oldest_session_age_s |

### §2.5 Agent Self-Metrics

Every agent that uses the Hivemind can optionally self-report by writing to
`data/observability/agents/{agent}/metrics/{date}.jsonl`. This is the per-agent
metrics stream for M1-M7. The format mirrors the canonical event schema.

**Agent metric generation** is NOT mandatory for Hivemind usage — it's a cooperative
pattern. The core system metrics (M2, M7) are generated server-side by the MCP
`hivemind_get_awareness` tool. Per-agent metrics (M1, M3, M4, M5, M6) are best-effort
from agents that choose to self-report.

---

## §3 Tracing — trace_id for Every Hivemind Interaction

### §3.1 Current State

Currently, `hivemind_post_context` returns:
```json
{"status": "accepted", "session_id": "ses_abc123", "timestamp": "..."}
```

No `trace_id`. There is no way to follow a coordination thread across agents.

### §3.2 Proposed Schema

Every Hivemind MCP tool SHOULD generate and return a `trace_id`:

```json
{
  "status": "accepted",
  "session_id": "ses_abc123",
  "trace_id": "hmd_f8a3c21e4b1d",
  "timestamp": "2026-06-05T12:00:00Z"
}
```

**Prefix convention**:
- `hmd_` prefix for Hivemind coordination traces (new)
- `trc_` prefix for existing ObservabilityEngine traces (unchanged)

This keeps the trace namespaces distinct and searchable: `grep -r "hmd_" data/observability/`.

### §3.3 Trace_id Propagation Pattern

```
Agent A: hivemind_post_context()  → returns trace_id "hmd_a1"
Agent B: hivemind_get_awareness()  → sees Agent A's session_id, returns trace_id "hmd_b1"
Agent B: hivemind_post_context(continuation="Ack for ses_abc123") → returns trace_id "hmd_b2"
         (references hmd_a1 in its metrics: continuation_references: ["hmd_a1"])
```

The trace_id propagates by **reference**, not by header. Agent B includes Agent A's
trace_id in its `continuation_references` metric. This is a lightweight, human-readable
alternative to distributed tracing headers — and it's more aligned with how agents
work (they read each other's context, they don't pass HTTP headers).

### §3.4 Trace File

When a trace generates multiple events, they are persisted to:
```
data/observability/hivemind/traces/{YYYY-MM-DD}/hmd_{trace_id}.json
```

This is a single JSON document aggregating all events in that trace:
```json
{
  "trace_id": "hmd_a3f8c21e4b1d",
  "start_time": "2026-06-05T12:00:00Z",
  "end_time": "2026-06-05T12:01:30Z",
  "duration_ms": 90000,
  "agent_chain": ["kali", "roc_racoon"],
  "events": [
    {"event_type": "hivemind.context.posted", "source_cli": "kali", "timestamp": "..."},
    {"event_type": "hivemind.context.posted", "source_cli": "roc_racoon", "timestamp": "..."},
    {"event_type": "hivemind.heartbeat.received", "source_cli": "kali", "timestamp": "..."}
  ],
  "metrics_aggregated": {
    "cycle_time_ms": 90000,
    "decisions_total": 5,
    "cross_references": ["ses_002", "ses_007"]
  }
}
```

### §3.5 Trace Flush Policy

- A trace is **open** for 5 minutes after the last event
- After 5 minutes, it is **flushed** from memory to disk
- An agent can explicitly **close** a trace by calling `hivemind_post_context` with
  `continuation: "TRACE_COMPLETE: hmd_xxx"` — which triggers immediate flush

### §3.6 Existing Observability Integration

The existing `ObservabilityEngine` in `src/omega/observability.py` already has:
- `TraceSession` context manager
- `new_trace_id()` function
- `_persist_event()` writing to `data/logs/events/{date}.jsonl`

The Hivemind tracing runs **alongside** the existing engine tracing. Two independent
trace streams:
- `trc_*` = engine inference traces (Oracle → Entity → ModelGateway)
- `hmd_*` = Hivemind coordination traces (awareness → post → ack)

They intersect when an agent dispatches a coordination task that triggers inference,
but that's a future integration (see §6).

---

## §4 Dashboard — The 5-Second "Is the Hivemind Healthy?" Check

### §4.1 Target Design

A single command or file that answers three questions:

1. **Are agents alive?** — Which agents have heartbeaten in the last 20 minutes?
2. **Are agents coordinating?** — Have they posted context and read each other's work?
3. **Any failures?** — Stale prune count, handoff latency violations, unresolved conflicts?

### §4.2 Option A: `data/observability/hivemind/current.json` (RECOMMENDED)

A lightweight JSON snapshot file, regenerated on every `hivemind_get_awareness` call:

```json
{
  "_schema": "omega.observability.hivemind.health.v1",
  "_zoneid": 1229783,
  "generated_at": "2026-06-05T12:00:00Z",
  "status": "healthy",
  "summary": {
    "agents_alive": 3,
    "agents_stale_last_hour": 0,
    "coordinating_agents": 2,
    "current_sessions": ["ses_kali_001", "ses_roc_002", "ses_lilith_003"]
  },
  "metrics": {
    "agent_cycle_time_p50_ms": 28000,
    "agent_cycle_time_p95_ms": 120000,
    "ttl_pruned_last_session": 0,
    "handoff_latency_p50_s": 45,
    "handoff_latency_p95_s": 240,
    "decisions_total_today": 12,
    "cross_pollination_events_today": 3,
    "stale_ratio": 0.0
  },
  "warnings": [],
  "errors": [],
  "agents": [
    {
      "cli": "kali",
      "status": "active",
      "last_seen": "2026-06-05T11:55:00Z",
      "last_context_post": "2026-06-05T11:50:00Z",
      "metrics": {
        "cycle_time_ms": 25000,
        "decision_count": 5,
        "observation_count": 3
      }
    },
    {
      "cli": "roc_racoon",
      "status": "stale",
      "last_seen": "2026-06-05T10:00:00Z",
      "last_context_post": "2026-06-05T10:00:00Z",
      "metrics": null
    }
  ],
  "failures_last_hour": [],
  "recommendation": "roc_racoon went stale 2 hours ago. Start a new session or clean up."
}
```

**Update trigger**: Regenerated on every `hivemind_get_awareness()` or `hivemind_post_context()` call.
This is a fire-and-forget write that doesn't block the calling agent.

### §4.3 Option B: `make hivemind-health` Makefile Target

A `Makefile` target that reads `data/observability/hivemind/current.json` and prints
a human-readable summary:

```bash
$ make hivemind-health

  ⬡ HIVEMIND HEALTH — 2026-06-05 12:00:00 UTC ⬡
  ──────────────────────────────────────────
  Status: 🟢 HEALTHY
  Agents: 3 alive, 0 stale (0.0%)
  ──────────────────────────────────────────
  Kali     🟢 active     last seen 5m ago  5 decisions today
  Roc      🟢 active     last seen 12m ago 3 decisions today
  Lilith   🟢 active     last seen 8m ago  4 decisions today
  ──────────────────────────────────────────
  Coordination: 2 agents in active session
  Handoffs:     p50=45s p95=240s
  Cross-Poll:   3 events today
  ──────────────────────────────────────────
  No warnings. No errors.
```

### §4.4 Option C: `hivemind_health()` MCP Tool

An additional MCP tool that any agent can call:

```python
@mcp.tool()
async def hivemind_health() -> str:
    """Get a 5-second health snapshot of the Hivemind coordination system."""
    # Read current.json
    # Read awareness
    # Aggregate metrics
    return json.dumps(health_snapshot, indent=2)
```

**Recommendation**: Implement Option A (current.json) first. It's the simplest and
can be read by both humans (`cat data/observability/hivemind/current.json`) and tools
(`omega-hub_hivemind_health()` MCP call). Option B and C are wrappers around Option A.

---

## §5 Error Classification — Coordination Failure Modes

### §5.1 Failure Mode Catalog

Each failure mode is classified with:
- **Severity**: info | warning | critical (per D-121 severity scale)
- **Detection**: How the failure is observed
- **Recovery**: What should happen when the failure is detected
- **Metric**: Which metric this failure mode feeds (M1-M7)

#### F1: Missed Message (Critical)
| Field | Value |
|-------|-------|
| **Severity** | 🔴 **critical** |
| **Description** | Agent A posts context with a continuation asking for Agent B's input. Agent B never responds. The continuation goes unacknowledged for >10 minutes. |
| **Detection** | `hivemind_post_context` with continuation → no matching ACK or `continuation_references` from target agent within threshold. |
| **Recovery** | Escalate to Kali or Lilith oversight. Post a `data/coordination/{A}_BLOCKER_{DATE}.md`. |
| **Metric** | M4 (handoff latency) exceeds 600s. |
| **Heritage** | `[id-soft: quake3-1999]` netchan — lost packet detection via sequence number gap. In Hivemind terms: `trace_id` continuity check. |

#### F2: Stale Agent (Warning)
| Field | Value |
|-------|-------|
| **Severity** | 🟡 **warning** |
| **Description** | An agent registered via `hivemind_post_context` but didn't heartbeat within HEARTBEAT_TTL (1200s). Pruned from awareness on next `hivemind_get_awareness` call. |
| **Detection** | `hivemind_get_awareness` pruning path. Counter `hivemind.agent.ttl_pruned_count` incremented. |
| **Recovery** | Agent should be restarted or re-register. If stale_ratio >0.3, consider extending TTL. |
| **Metric** | M2 (ttl_pruned_count), M7 (stale_ratio). |
| **Heritage** | `[id-soft: doom-1993]` Lazy Deletion — mark as tombstoned (stale), reap on next iteration. |

#### F3: Conflicting Locks (Critical)
| Field | Value |
|-------|-------|
| **Severity** | 🔴 **critical** |
| **Description** | Two agents claim ownership of the same file in their workspace locks. Risk of merge conflict / data loss. |
| **Detection** | `grep` across `data/coordination/*_WORKSPACE_LOCK_*.md` for overlapping file paths. |
| **Recovery** | Both agents must renegotiate. One agent must yield or they must split work. Escalate to Kali. |
| **Metric** | N/A (discrete event, not aggregate). Track as `coord.conflict` in alerts. |
| **Heritage** | `[id-soft: quake-1996]` Zone Memory — tag-based ownership. Conflict is two tags claiming the same block. |

#### F4: Orphaned Context (Warning)
| Field | Value |
|-------|-------|
| **Severity** | 🟡 **warning** |
| **Description** | A context snapshot exists in `_hot_store` but the agent that created it is no longer alive (no heartbeat, no session cleanup). The context is consuming memory for no reason. |
| **Detection** | `hivemind_get_awareness` returns N agents but `_hot_store` has >N sessions. |
| **Recovery** | TTL sweep on `_hot_store` — prune sessions whose `cli` has been stale for >2× HEARTBEAT_TTL. |
| **Metric** | N/A. Track as `coord.orphaned_contexts` gauge. |
| **Heritage** | `[id-soft: quake-1996]` Surface Cache / PVS — "only observe what's active." An orphaned context is a cached surface whose sector was unloaded. |

#### F5: Dropped Heartbeat (Info)
| Field | Value |
|-------|-------|
| **Severity** | 🟢 **info** |
| **Description** | An agent misses one heartbeat cycle but recovers on the next. Normal for long-running operations. |
| **Detection** | `hivemind_heartbeat` not called within HEARTBEAT_TTL, but agent still alive on next check. |
| **Recovery** | No action needed. Track rate for TTL tuning. |
| **Metric** | M2 (ttl_pruned_count — but with "recovered" sub-counter). |
| **Heritage** | `[id-soft: quake3-1999]` netchan — packet loss on unreliable channel. Single dropped packet is normal. Sustained loss = problem. |

#### F6: Silent Agent (Warning)
| Field | Value |
|-------|-------|
| **Severity** | 🟡 **warning** |
| **Description** | Agent is alive (heartbeating) but never posts context or reads other agents' context. It's present but not coordinating. |
| **Detection** | `hivemind_get_awareness` shows agent, but `hivemind_get_session` shows no `hivemind_post_context` in last HEARTBEAT_TTL. |
| **Recovery** | Agent should be reminded to post context. If intentional (headless worker), tag as `[SILENT]` in task_current. |
| **Metric** | M1 (cycle_time = infinity for that agent). |
| **Heritage** | `[id-soft: doom-1993]` Multi-Index Entity — an entity in the blockmap but not in the sector list. Visible but not rendering. |

#### F7: Cascade Stale (Critical)
| Field | Value |
|-------|-------|
| **Severity** | 🔴 **critical** |
| **Description** | Multiple agents go stale simultaneously. The Hivemind becomes empty. This indicates a systemic failure (MCP server restart, power loss, coordination breakdown). |
| **Detection** | `hivemind_get_awareness` returns 0 agents when 3+ were active in the last hour. |
| **Recovery** | Emergency restart protocol. All agents must re-register. Check `data/observability/hivemind/traces/` for the last trace before the cascade. |
| **Metric** | M7 (stale_ratio jumps to 1.0). |
| **Heritage** | `[id-soft: quake3-1999]` netchan — total channel loss. All qports silent. |

### §5.2 Severity Matrix

| Failure Mode | Severity | Detection Latency | Auto-Recovery | Escalation |
|-------------|----------|-------------------|---------------|------------|
| F1: Missed Message | 🔴 critical | TTL+10min | ❌ No | Kali |
| F2: Stale Agent | 🟡 warning | TTL (20 min) | ✅ Re-register | None |
| F3: Conflicting Locks | 🔴 critical | Session start | ❌ No | Kali |
| F4: Orphaned Context | 🟡 warning | 2× TTL (40 min) | ✅ Auto-prune | None |
| F5: Dropped Heartbeat | 🟢 info | TTL (20 min) | ✅ Self-healing | None |
| F6: Silent Agent | 🟡 warning | TTL (20 min) | ❌ No (intentional) | Lilith |
| F7: Cascade Stale | 🔴 critical | 1 hour | ❌ No | User/Kali |

### §5.3 Alert File Format

When a critical failure is detected, an alert file is written to `data/observability/fleet/alerts/`:

```json
{
  "_schema": "omega.observability.hivemind.alert.v1",
  "_zoneid": 1229783,
  "alert_id": "alert_20260605_001",
  "timestamp": "2026-06-05T12:00:00Z",
  "failure_mode": "F1",
  "severity": "critical",
  "summary": "Handoff from kali to roc_racoon unacknowledged for 15 minutes",
  "trace_id": "hmd_f8a3c21e4b1d",
  "agents_involved": ["kali", "roc_racoon"],
  "session_ids": ["ses_kali_001", "ses_roc_002"],
  "detail": "Kali posted context with continuation 'waiting on roc for mining results' at 11:45. Roc last posted context at 11:30. No ACK file found.",
  "recommended_action": "Check if Roc is still running. Restart Roc session if needed. Escalate to Kali if unresolved.",
  "resolved_at": null
}
```

---

## §6 Heritage Cross-Reference

### §6.1 Surface Cache / PVS — "Only Observe What's Active" [id-soft: quake-1996]

| Aspect | id Software Original | Hivemind Observability Adaptation |
|--------|--------------------|-----------------------------------|
| **Core idea** | Precompute Potentially Visible Set. Only render surfaces in the PVS. | Only collect metrics for agents that are currently alive. Pruned agents have their metrics finalized and archived. |
| **Mechanism** | PVS bitfield per sector (precomputed, O(1) lookup) | `_awareness` dict is the PVS. If an agent is not in awareness, we don't poll it for metrics. |
| **Application to M2** | A sector outside the PVS generates no rendering cost | A stale agent generates no metrics collection cost. Its metrics are finalized at prune time. |
| **Application to F4** | Cache is purged when sector is unloaded | Orphaned context is purged when agent is pruned. Context → sector, agent → camera. |
| **Omega evolution** | Static PVS → dynamic awareness set | The "visible set" changes as agents start/stop. Metrics are transitioned, not recalculated. |

### §6.2 Fixed-Size Active Set — Bounded Observation Window [id-soft: doom-1993]

| Aspect | id Software Original | Hivemind Observability Adaptation |
|--------|--------------------|-----------------------------------|
| **Core idea** | MAXVISPLANES = 32. BSP drawer clips to 32 active visplanes. Bounded iteration cost. | Bounded observation window: collect metrics for at most N agents (default 32). Linear scan cost capped. |
| **Mechanism** | 32-entry array of visplane_t, fits in L1 cache (256 bytes) | Metric array of agent_metric_t, 32 entries, fits in CPU cache (~2KB). |
| **Application to all metrics** | BSP renderer processes at most 32 visplanes per frame | WatchTower processes at most 32 agents per health check. Beyond 32, aggregate as "other". |
| **Omega evolution** | 256 bytes → ~2KB | Python object overhead is significant. But the bounded iteration principle is the same. The cap prevents the metrics system from becoming the bottleneck. |

### §6.3 netchan — Tracing Across Agent Boundaries [id-soft: quake3-1999]

| Aspect | id Software Original | Hivemind Observability Adaptation |
|--------|--------------------|-----------------------------------|
| **Core idea** | OOB messages carry sequence numbers. Fragments carry reassembly info. Messages cross network channel boundaries. | trace_id carries continuity across agent boundaries. Events carry cross-references to other traces. |
| **Mechanism** | `netchan_t.incoming_sequence`, `outgoing_sequence`. Packet header includes sequence number. | `hmd_` trace_id in every event. `continuation_references` array links agent A's trace to agent B's. |
| **Application to F1** | Lost packet detected via sequence number gap | Missed message detected via missing `continuation_references` within timeout. |
| **Application to M1** | Round-trip time = ack_time - send_time | Cycle time = agent B's post time - agent A's post time (with session reference matching). |
| **Omega evolution** | Binary packet header → JSON event field | Fields are human-readable and searchable. The tracing principle is the same: continuity markers across boundaries. |

### §6.4 cvar Table — Tunable Thresholds [id-soft: quake-1996/1999]

| Aspect | id Software Original | Hivemind Observability Adaptation |
|--------|--------------------|-----------------------------------|
| **Core idea** | Named console variables with flags (ARCHIVE, READONLY, LATCH). Tunable at runtime. | Named metric thresholds in the cvar table. Tunable without code changes. |
| **Proposed cvars** | `sv_timeout`, `cl_timeout`, `rate` | `hivemind.alert.missed_message_timeout`, `hivemind.ttl.warning_ratio`, `hivemind.cycle_time.warning_ms` |
| **Mechanism** | `Cvar_Get("sv_timeout")` → returns current value | `cvar_get("hivemind.alert.missed_message_timeout")` → returns 600 (seconds) |
| **Omega evolution** | Embedded in game engine → embedded in observability layer | Thresholds are hot-reloadable. Change a warning level without restarting the MCP server. |

### §6.5 ZONEID Pattern — Integrity on Every Event [id-soft: doom-1993]

Every observability event carries `_zoneid` for integrity checking. A new ZONEID
constant should be registered:

| Constant | Value | Purpose |
|----------|-------|---------|
| `ZONEID_OBSERVABILITY` | `0x1d4a1c` | Hivemind observability event integrity (previously unassigned — slot 0x1c after ZONEID_ATOMIC at 0x1d4a1b) |

The existing `validate_zoneid()` function in `omega.cvar_table` can be used to
validate observability events on read.

---

## §7 Implementation Roadmap

### §7.1 Phase 1: Foundation (Day 1-2) — Server-Side Only

**Goal**: Metrics collection without any agent code changes.

| # | Task | File | Effort |
|---|------|------|--------|
| 1.1 | Add `ZONEID_OBSERVABILITY = 0x1d4a1c` to `omega.cvar_table.py` | `src/omega/cvar_table.py` | 5 min |
| 1.2 | Add hivemind-specific event types to `EventType` class | `src/omega/observability.py` | 5 min |
| 1.3 | Add metrics emission to `hivemind_get_awareness` (stale count, ratio) | `mcp_servers/omega_hub/server.py` | 30 min |
| 1.4 | Add metrics emission to `hivemind_post_context` (decision_count, focus_length) | `mcp_servers/omega_hub/server.py` | 30 min |
| 1.5 | Add metrics emission to `hivemind_heartbeat` (timestamp tracking) | `mcp_servers/omega_hub/server.py` | 15 min |
| 1.6 | Write `current.json` health snapshot after `hivemind_get_awareness` | `mcp_servers/omega_hub/server.py` | 45 min |
| 1.7 | Create `data/observability/hivemind/` directory structure | Init on server start | 5 min |

### §7.2 Phase 2: Tracing (Day 3-4) — trace_id + Per-Agent Metrics

| # | Task | File | Effort |
|---|------|------|--------|
| 2.1 | Generate `hmd_` trace_id on every `hivemind_post_context` call | `mcp_servers/omega_hub/server.py` | 20 min |
| 2.2 | Return `trace_id` in `hivemind_post_context` response | `mcp_servers/omega_hub/server.py` | 5 min |
| 2.3 | Add `continuation_references` extraction (regex for ses_* IDs in continuation) | `mcp_servers/omega_hub/server.py` | 20 min |
| 2.4 | Implement trace_id continuity: propagate trace_id across agents via continuation_references | `mcp_servers/omega_hub/server.py` | 30 min |
| 2.5 | Write trace aggregate file on flush (5-min timeout) | `mcp_servers/omega_hub/server.py` | 30 min |
| 2.6 | Add cross_pollination detection (session_id references across agents) | `mcp_servers/omega_hub/server.py` | 20 min |

### §7.3 Phase 3: Dashboard & Alerts (Day 5-7)

| # | Task | File | Effort |
|---|------|------|--------|
| 3.1 | Implement `hivemind_health()` MCP tool | `mcp_servers/omega_hub/server.py` | 30 min |
| 3.2 | Add `make hivemind-health` target | `Makefile` | 10 min |
| 3.3 | Implement alert generation for F1-F7 failure modes | `mcp_servers/omega_hub/server.py` | 1 hr |
| 3.4 | Wire alert file writes to `data/observability/fleet/alerts/` | `mcp_servers/omega_hub/server.py` | 20 min |
| 3.5 | Add daily rollup generation (aggregate all metrics into fleet rollup) | Background task | 45 min |
| 3.6 | Add metric thresholds to `omega.cvar_table.py` as cvars | `src/omega/cvar_table.py` | 30 min |

### §7.4 Phase 4: Agent Self-Metrics (Cooperative, Ongoing)

| # | Task | File | Effort |
|---|------|------|--------|
| 4.1 | Document per-agent metric format in HIVEMIND_PROTOCOL.md | `docs/strategy/HIVEMIND_PROTOCOL.md` | 20 min |
| 4.2 | Add optional `--self-metrics` flag to Pillar agents | `.opencode/agents/pillar.md` | 15 min |
| 4.3 | Add observation density tracking (count OBS- entries per agent/session) | Background script | 20 min |

---

## §8 Metric Federation with Existing Systems

### §8.1 Verification System Integration

The existing `data/coordination/verification/` system has:
- Items with states: DISCOVERED → PORTED → TESTED → VERIFIED → DEPLOYED → LIVE
- JSONL audit logs
- Rollups (fleet-wide, cross-pollination, stale_items)

**Integration point**: The verification system's `audit/` JSONL logs can also store
Hivemind observability events. The schema is compatible:

```json
{
  "ts": "2026-06-05T12:00:00Z",
  "type": "hivemind_metric",
  "metric_name": "hivemind.agent.cycle_time",
  "value": 45000,
  "unit": "ms",
  "source_cli": "kali"
}
```

**Recommendation**: Keep them separate for now. The verification system tracks
*verification items* (cross-pollination verification, stale item verification).
The observability system tracks *operational metrics*. They are sibling directories
under `data/coordination/`:
- `data/coordination/verification/` → correctness verification
- `data/observability/` → operational health

Merge them when both have stabilized.

### §8.2 Observations Protocol (D-121) Integration

The D-121 Observations Protocol captures **qualitative** meta-observation. The
observability system captures **quantitative** metrics.

| Dimension | Observations (D-121) | Observability (This Doc) |
|-----------|---------------------|-------------------------|
| **Data type** | Qualitative narrative | Quantitative numbers |
| **Format** | Markdown in `HIVEMIND_OBSERVATIONS_LOG.md` | JSONL events |
| **Frequency** | Per notable event (1-5 per session) | Per every tool call (10-100 per session) |
| **Consumer** | Lilith (weekly cluster) | WatchTower (real-time health) |
| **TTL** | 30 days (T1) → permanent (T3/T4) | 30 days (events), permanent (traces) |

**Federation**: Observations that identify systemic issues (e.g., "TTL pruning is
too aggressive") should trigger an observability metric adjustment (e.g., change
the TTL pruning threshold). The bridge is the `data/observability/fleet/alerts/`
directory — an observation that identifies a concrete failure mode can be promoted
to an alert.

### §8.3 Existing ObservabilityEngine Integration

The `ObservabilityEngine` at `src/omega/observability.py` has:
- TraceSession (context manager)
- Event logging to `data/logs/events/{date}.jsonl`
- ForensicsManager (crash dumps)

The Hivemind observability events should use a separate log directory
(`data/observability/hivemind/events/` rather than `data/logs/events/`)
because:
1. Hivemind events have a different schema (agent-centric vs engine-centric)
2. Hivemind events should be disposable independently of engine logs
3. The Hivemind MCP server may run separately from the Oracle engine

However, the **same code patterns** should be used (JSONL append, atomic writes,
trace_id propagation). The Hivemind observability code can import
`ObservabilityEngine.log_event()` and `ForensicsManager.snapshot()` if the MCP
server has access to the engine module. If not, a standalone
`HivemindObservability` class can mirror the patterns without importing the engine.

---

## §9 Anti-Patterns

### §9.1 Don't: Metric Spam
❌ **WRONG**: Every `hivemind_heartbeat` writes 200 bytes of JSON. With 10 agents
heartbeating every 5 minutes, that's 576KB/day — acceptable. But every
`hivemind_get_session` read? That's overkill.

✅ **RIGHT**: Only emit metrics on **mutation** operations (post, heartbeat, awareness
check). Read operations (get_session, get_continuation) are low-signal unless they
detect a cross-reference.

### §9.2 Don't: Blocking on Metrics
❌ **WRONG**: `hivemind_post_context` waits for the JSONL write to complete before
returning. Agents are delayed by observability.

✅ **RIGHT**: Fire-and-forget `anyio.to_thread.run_sync(jsonl_append)` — never block
the agent on the metrics store. The agent gets their response, the metrics write
happens in the background.

### §9.3 Don't: Over-Indexing
❌ **WRONG**: Add Elasticsearch, Grafana, Prometheus, or any external metrics system.
Mandate 8 forbids external telemetry.

✅ **RIGHT**: JSONL files + `grep` + `jq` are the query toolchain. If querying
becomes painful, add a light Python CLI wrapper — never a remote service.

### §9.4 Don't: Metric-Drive Without Context
❌ **WRONG**: "TTL prune rate is 5/hr — that's bad!" Without knowing *why* agents
are going stale (session ended? server restarted? heartbeat bug?), the metric is
noise.

✅ **RIGHT**: Always pair metrics with the qualitative observations log (D-121).
Metrics tell you *what* is happening. Observations tell you *why*.
Both must be read together.

### §9.5 Don't: Per-Agent Metrics That Compete
❌ **WRONG**: Two agents both write to `data/observability/agents/kali/metrics/{date}.jsonl`.
Race condition on append (rare with append-only, but possible if runtimes overlap).

✅ **RIGHT**: Each agent writes to its own file. Agent identity is the split key.
The MCP server should NOT write per-agent metrics — each agent is responsible
for its own `data/observability/agents/{cli}/metrics/{date}.jsonl`.

---

## §10 Cross-References

| Document | Relevance |
|----------|-----------|
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Hivemind MCP tools definition — metrics hooks go here |
| `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` | D-121 meta-observation — qualitative sibling to this quantitative system |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Link P9 handoff — M4 handoff latency measures this |
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | Phase H2-E / H3-A — this analysis feeds those tracks |
| `src/omega/observability.py` | Existing ObservabilityEngine — patterns to mirror |
| `src/omega/oracle/health_monitor.py` | Circuit breaker health — existing metric infrastructure to align with |
| `src/omega/cvar_table.py` | ZONEID constants + cvar thresholds — ZONEID_OBSERVABILITY goes here |
| `mcp_servers/omega_hub/server.py` | All 6 Hivemind MCP tools — metrics and trace_id injection points |
| `data/coordination/verification/` | Verification system — parallel metrics track to align with |
| `SOVEREIGN_MANDATES.md` | M8 (Zero Telemetry) — this system is explicitly allowed by M8's local-observability exception |
| `CREDITS.md` §1.5/1.20/1.21 | Surface Cache, Fixed-Size Active Set, netchan — heritage foundations for this strategy |

---

## §11 Open Questions for Oversight

1. **Should `ZONEID_OBSERVABILITY` be `0x1d4a1c` (the next available, after ZONEID_ATOMIC at 0x1d4a1b)?**
   - Yes. The ZONEID constant table has slots 0x1d4a11 through 0x1d4a1b assigned.
     Slot 0x1d4a1c is the natural next assignment.

2. **Should the Hivemind observability live in `src/omega/` or in `mcp_servers/omega_hub/`?**
   - Prefer `mcp_servers/omega_hub/hivemind_observability.py` — the Hivemind MCP
     server is the natural owner. The engine's `src/omega/observability.py` is for
     Oracle/engine-level observability. They share patterns but are independent modules.

3. **Should metrics collection be opt-in or opt-out for agents?**
   - **Server-side metrics** (M2, M7): Always collected. No agent action needed.
   - **Per-agent metrics** (M1, M3, M4, M5, M6): Opt-in via `--self-metrics` flag
     or by writing `data/observability/agents/{cli}/metrics/`. If an agent doesn't
     self-report, the server side does its best with server-only data.

4. **Retention policy: how long to keep trace files and events?**
   - **Events** (`data/observability/hivemind/events/`): 30 days rolling, matching
     the D-121 Observations Protocol T1 TTL.
   - **Traces** (`data/observability/hivemind/traces/`): 90 days rolling.
     Critical traces (those involving F1/F3/F7 failures) archived to a `critical/`
     subdirectory for permanent retention.
   - **Alerts** (`data/observability/fleet/alerts/`): Permanent.
     Alerts are rare and high-signal.
   - **Health snapshots** (`current.json`): Only the current snapshot is kept.
     Previous snapshot is overwritten.

5. **When Redis Pub/Sub is added (Phase 5 of Kali's plan), does the observability layer change?**
   - The metrics store stays as JSONL (Redis is for coordination, not metrics).
   - Tracing becomes richer: Redis Streams message IDs can serve as additional
     trace continuity markers. A `redis_stream_id` field can be added to the
     event schema without breaking backward compatibility.

---

*⬡ OMEGA ⬡ P8 ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar ⬡ OBSERVABILITY-STRATEGY*

— P8 (WatchTower), 2026-06-05
