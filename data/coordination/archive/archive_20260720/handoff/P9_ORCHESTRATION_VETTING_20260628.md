<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P9 Orchestration Vetting Report — Handoff State Machine

**Vetter**: @pillar P9 (Orchestration — Link, Agent Handoff & Delegation)
**Date**: 2026-06-28
**Target**: `RUN_SIDE_HARDENING_REPORT_ENHANCED_20260628.md` §3 (Handoff State Machine)
**Scope**: Handoff State Machine + Loop Guard + Stale→Archive Lifecycle
**Verdict**: **MODIFY** (with conditions)

---

## §1 Executive Summary

The hardening report's §3 proposes a 7-state handoff machine, a `HandoffGuard` class, and a stale packet lifecycle. The design is **structurally sound** and aligns with production multi-agent patterns (Geodocs spec, Agent Handoff Protocol library, Microsoft Agent Framework, Tangle). However, **three critical gaps** and **two moderate issues** require resolution before implementation. The existing Hivemind infrastructure (`background.py:_reap_stale_handoffs`) already implements a subset of the proposed lifecycle — the new design must reconcile with it, not replace it.

**Key finding**: The report correctly identifies that 57% of multi-agent failures originate in orchestration (Anthropic), and that visited-set loop detection + max depth are the canonical defenses. The proposed `HandoffGuard` class is well-structured. But the state machine's state names conflict with the existing Hivemind directory structure, and the loop guard has no integration path to the existing `hivemind_submit_handoff()` / `hivemind_accept_handoff()` MCP tools.

---

## §2 Detailed Vetting by Subsection

### 2.1 Handoff State Machine (§3.3.1)

#### What the Report Proposes

A 7-state machine: `PENDING → QUEUED → STALE → ARCHIVED` (auto-transitions) and `PENDING → ACTIVE → COMPLETED/REJECTED` (manual transitions). ASCII diagram included.

#### What Exists Today

The current Hivemind (`background.py:110-150`) uses a **4-directory lifecycle**:
```
pending/ → stale/ (24h timeout)
active/  → stale/ (48h timeout)
completed/ → archive/ (7d timeout)
stale/   → (terminal, manually cleaned)
```

This maps to states: `pending`, `active`, `completed`, `stale`, `archived`.

#### Gap 1: QUEUED State Is Undefined

The report introduces `QUEUED` between `PENDING` and `STALE`, but:
- No code defines when a packet enters `QUEUED`
- No MCP tool transitions a packet to `QUEUED`
- The existing `hivemind_submit_handoff()` writes directly to `pending/` — there is no intermediate queue

**Verdict**: The `QUEUED` state is aspirational (it would represent "accepted by the broker but not yet picked up by a consumer"). In the current file-based architecture, `pending/` IS the queue. **Recommendation**: Remove `QUEUED` from the state machine. The 6-state model (`pending → active → completed/rejected → stale → archived`) matches the existing directory structure and should be the canonical design.

#### Gap 2: State Names vs Directory Names

The report's state names (`PENDING`, `QUEUED`, `STALE`, `ARCHIVED`, `ACTIVE`, `COMPLETED`, `REJECTED`) use SCREAMING_CASE, while the existing directories use lowercase (`pending/`, `active/`, `completed/`, `stale/`, `archive/`). The report says `ARCHIVED` but the directory is `archive/`.

**Verdict**: Minor but important for implementation. Use the directory names as canonical state identifiers: `pending`, `active`, `completed`, `stale`, `archived`.

#### Gap 3: Missing Transition — `active → stale`

The report shows `QUEUED → STALE` on TTL expiry but does not show `ACTIVE → STALE`. The existing `background.py:145` already handles this (`active/ older than 48h → stale/`). The report should explicitly document this transition.

**Recommendation**: Add `ACTIVE → STALE` with 48h TTL to the state machine diagram.

#### Approved State Machine (Modified)

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ hivemind_submit_handoff()
                           ▼
                    ┌─────────────┐
                    │    STALE    │ ← TTL 24h (pending)
                    └──────┬──────┘
                           │ archive
                           ▼
                    ┌─────────────┐
                    │  ARCHIVED   │ ← TTL 7d (completed)
                    └─────────────┘

                    ┌─────────────┐
              ┌─────│   ACTIVE    │ ← TTL 48h → STALE
              │     └──────┬──────┘
              │            │
              │            ▼
              │     ┌─────────────┐
              │     │  COMPLETED  │
              │     └──────┬──────┘
              │            │ archive (7d)
              │            ▼
              │     ┌─────────────┐
              │     │  ARCHIVED   │
              │     └─────────────┘
              │
              │ hivemind_reject_handoff()
              ▼
       ┌─────────────┐
       │  REJECTED   │
       └─────────────┘
```

### 2.2 Loop Guard Implementation (§3.3.2)

#### What the Report Proposes

A `HandoffGuard` dataclass with:
- `max_handoff_depth: int = 10`
- `max_iterations: int = 20`
- `max_same_agent_visits: int = 3`
- `caution_threshold: int = 10`
- `warning_threshold: int = 3`
- `_visited: Set[str]` for circular detection
- `_visit_counts: dict` for same-agent tracking
- `pre_handoff()` validates before handoff
- `post_iteration()` injects budget pressure messages

#### Web Research Validation

| Source | Pattern | Alignment with Report |
|--------|---------|----------------------|
| **Geodocs Spec** | `loop_guard` is a **required field** in handoff contracts; must be "a reference to a counter or set of visited agents that MUST be updated" | ✅ Report's `_visited` set matches |
| **Agent Handoff Protocol (dakshjain)** | `HandoffBroker` with TTL + audit; `purge_expired()` for stale packets | ✅ Report's lifecycle matches |
| **CallSphere** | `HandoffTracker` with `record_handoff()` checking immediate bounce-back (A→B→A) + max_handoffs limit | ✅ Report's `_visited` + `max_handoff_depth` match |
| **AI Tools Guidebook** | DFS cycle detection on agent delegation graph at **startup** (static), plus runtime `call_path` threading | ⚠️ Report only does runtime — missing startup validation |
| **Tangle (Intuit)** | Incremental cycle detection on Wait-For Graph + `cancel_youngest` resolver | ⚠️ Report has no resolver strategy — just raises exception |
| **Microsoft Agent Framework** | Declarative topology (directed edges), terminal endpoints, graph terminates naturally | ⚠️ Report has no allowed-transitions topology |
| **Neural Base (Swarm)** | `transfer_depth` in context dict; session-level counter; 30s timeout for rapid transfers | ⚠️ Report's counter is per-guard, not per-session |
| **Ziro Agent SDK** | `maxHandoffDepth: 10` default, throws `HandoffLoopError`; deterministic router (rejects LLM-as-router) | ✅ Report's max depth + deterministic match |
| **Agentproof (arxiv)** | Static temporal verification via graph × DFA product construction; witness traces for debugging | ⚠️ Report has no witness/trace generation on loop detection |

#### Gap 4: No Resolver Strategy

The report's `HandoffGuard` raises exceptions on loop detection (`CircularHandoffDetected`, `MaxHandoffDepthExceeded`, `ExcessiveAgentVisits`). But it does not specify what happens next:
- Does the orchestrator catch the exception and force-terminate the handoff chain?
- Does it fall back to a supervisor agent?
- Does it return the best available result with a quality warning?

AWS Step Functions and Tangle both provide explicit resolver strategies:
- **Tangle**: `cancel_youngest` (cancel most recently registered agent), `cancel_all`, `tiebreaker`, `escalate`
- **Step Functions**: Error handling with catch configuration, fallback paths
- **Geodocs**: `on_reject`, `on_timeout`, `on_error` fields in the handoff contract

**Recommendation**: Add a `ResolverStrategy` enum to `HandoffGuard`:
```python
class ResolverStrategy(Enum):
    TERMINATE = "terminate"      # Raise, stop chain, return error
    ESCALATE = "escalate"        # Hand off to supervisor (Kali)
    FALLBACK = "fallback"        # Return best available result
    RETRY_DIFFERENTLY = "retry"  # Re-route to a different target
```

The default should be `ESCALATE` (hand off to Kali as the Transcendent Oversight agent).

#### Gap 5: No Startup Graph Validation

The AI Tools Guidebook and Agentproof both recommend validating the agent delegation graph for cycles **at startup** — before any handoffs occur. The report's guard only detects loops at runtime.

**Recommendation**: Add a `validate_delegation_graph()` function that:
1. Builds the directed graph from `ALLOWED_TRANSITIONS`
2. Runs DFS cycle detection
3. Rejects any configuration that creates a cycle at import time

This is a one-time cost that catches misconfigurations before they cause runtime loops.

### 2.3 Stale→Archive Lifecycle (§3.3.3)

#### What the Report Proposes

```python
LIFECYCLE = {
    "pending":   {"ttl_seconds": 3600, "auto_transition": "stale"},
    "stale":     {"ttl_seconds": 86400, "auto_transition": "archived"},
    "archived":  {"ttl_seconds": None, "auto_transition": None},
    "active":    {"ttl_seconds": None, "auto_transition": None},
    "completed": {"ttl_seconds": None, "auto_transition": None},
    "rejected":  {"ttl_seconds": None, "auto_transition": None},
}
```

#### What Exists Today

`background.py:110-150` already implements:
- `pending/` → `stale/` after **86400s (24h)**
- `active/` → `stale/` after **172800s (48h)**
- `completed/` → `archive/` after **604800s (7d)**

#### Gap 6: TTL Mismatch — Pending

The report proposes `pending → stale` after **3600s (1h)**. The existing implementation uses **86400s (24h)**.

The 1h TTL is aggressive. In production multi-agent systems, a pending handoff may need to wait for:
- Target agent cold-start (local model loading can take 30-60s on Ryzen 5700U)
- Target agent completing a long-running task
- Human-in-the-loop approval

**Recommendation**: Use **4h (14400s)** as a compromise. The 1h TTL will cause premature staleness for slow-starting local models. The 24h TTL is too lenient. 4h balances responsiveness with practical agent startup times.

#### Gap 7: No `active → stale` TTL in Report

The report's lifecycle dictionary sets `active.ttl_seconds = None`. But the existing `background.py:145` already reaps `active/` after 48h. The report should inherit this behavior.

**Recommendation**: Add `"active": {"ttl_seconds": 172800, "auto_transition": "stale"}` to the lifecycle dictionary.

#### Gap 8: No Stale→Archive Transition for Rejected

The report shows `REJECTED → ARCHIVED` in the ASCII diagram but the lifecycle dictionary does not include `rejected`. The existing `hivemind_reject_handoff()` moves packets to `stale/`, not directly to `archive/`. Rejected packets should follow the same stale→archive path.

**Recommendation**: Add `"rejected": {"ttl_seconds": 86400, "auto_transition": "archived"}` to the lifecycle dictionary.

#### Approved Lifecycle (Modified)

```python
LIFECYCLE = {
    "pending":   {"ttl_seconds": 14400, "auto_transition": "stale"},   # 4h (modified from 1h)
    "active":    {"ttl_seconds": 172800, "auto_transition": "stale"},  # 48h (added)
    "completed": {"ttl_seconds": 604800, "auto_transition": "archived"}, # 7d (added)
    "rejected":  {"ttl_seconds": 86400, "auto_transition": "archived"}, # 24h (added)
    "stale":     {"ttl_seconds": 86400, "auto_transition": "archived"}, # 24h (unchanged)
    "archived":  {"ttl_seconds": None, "auto_transition": None},        # Terminal
}
```

### 2.4 Verification Gates (§3.3.4)

The 7 proposed gates (T-HANDOFF-1 through T-HANDOFF-7) are well-designed. Additions:

| Gate | Name | Modification |
|------|------|-------------|
| T-HANDOFF-1 | Loop Detection | Add: verify exception carries `handoff_chain` list for trace |
| T-HANDOFF-3 | Budget Pressure | Add: verify CAUTION at iteration 10, WARNING at iteration 17, TERMINATE at 20 |
| T-HANDOFF-5 | State Machine | Add: verify invalid transition P6→P6 (self-loop) is also rejected |
| **T-HANDOFF-8** | **Startup Graph Validation** | **NEW**: Run `validate_delegation_graph()` on ALLOWED_TRANSITIONS — must pass with 0 cycles |
| **T-HANDOFF-9** | **Resolver Strategy** | **NEW**: Trigger loop detection → verify ESCALATE hands off to Kali |
| **T-HANDOFF-10** | **Stale Lifecycle Integration** | **NEW**: Create packet → wait 4h → verify file moves from `pending/` to `stale/` |

---

## §3 Cross-Cutting Findings

### 3.1 Integration with Existing Hivemind Infrastructure

The report proposes new classes (`HandoffGuard`, lifecycle dictionary) but does not specify how they integrate with the existing MCP tools:

- `hivemind_submit_handoff()` — writes to `pending/`
- `hivemind_accept_handoff()` — moves `pending/` → `active/`
- `hivemind_complete_handoff()` — moves `active/` → `completed/`
- `hivemind_reject_handoff()` — moves `active/` → `stale/`
- `hivemind_handoff_archive()` — moves `completed/` → `archive/`

**Recommendation**: The `HandoffGuard` must be instantiated per-handoff-chain and threaded through the MCP tool calls. The guard state should be stored in the packet JSON itself (not in-memory) to survive across MCP tool invocations:

```python
# In the packet JSON:
{
  "packet_id": "...",
  "guard": {
    "visited": ["P6", "P7"],
    "visit_counts": {"P6": 1, "P7": 1},
    "handoff_chain": ["P6", "P7"],
    "iteration": 2
  }
}
```

This ensures the guard survives across MCP tool boundaries (each tool call is a separate HTTP request).

### 3.2 M12 Queue Integrity Compliance

The stale→archive lifecycle directly supports M12 (Queue Integrity): "Every request operation must result in a terminal state." The lifecycle ensures no packet remains in a non-terminal state indefinitely. The background reaper loop (`_reaper_background`) runs every 300s and enforces the TTL transitions.

### 3.3 M9 Error Integrity Compliance

The report's exception types (`CircularHandoffDetected`, `MaxHandoffDepthExceeded`, `ExcessiveAgentVisits`) are properly typed and traceable. However, they must inherit from a common `HandoffError` base class (per M9's typed error hierarchy requirement).

---

## §4 Web Research Summary

### 4.1 Multi-Agent Handoff Protocols

| Source | Key Finding | Relevance |
|--------|-------------|-----------|
| **Geodocs.dev** (2026-04) | `loop_guard` is a required field; 6 required fields per handoff contract; `on_reject`/`on_timeout`/`on_error` recovery paths | Direct — validates report's guard design, exposes missing resolver |
| **Microsoft Agent Framework** (2026-05) | Declarative topology (directed edges), terminal endpoints, graph terminates naturally when agent finishes without handoff | Direct — validates report's state machine, exposes need for allowed-transitions |
| **Agent Patterns Catalog** (2026-05) | "Handoff loops (A→B→A→B) are a real failure"; loop detection refuses re-handoff back to source within same conversation | Direct — validates report's visited-set approach |
| **Agent Handoff Protocol (dakshjain)** (2026-04) | Pydantic HandoffPacket with `ttl_seconds`, `expires_at`; SQLite broker with TTL + audit; `purge_expired()` | Direct — validates report's lifecycle design |
| **Ziro Agent SDK RFC 007** (2026-04) | `maxHandoffDepth: 10` default; deterministic router (rejects LLM-as-router); `HandoffLoopError` | Direct — validates report's max depth + deterministic routing |
| **OpenAI Agents SDK** | `handoff()` as first-class primitive; `input_filter` for payload transformation | Indirect — confirms handoff-as-primitive pattern |

### 4.2 Loop Detection & Prevention

| Source | Key Finding | Relevance |
|--------|-------------|-----------|
| **AI Tools Guidebook** (2026-05) | DFS cycle detection on agent delegation graph at **startup**; `call_path` token threaded through invocations; call history injected into LLM routing prompts | Direct — exposes report's missing startup validation |
| **CallSphere** (2026-03) | `HandoffTracker` with immediate bounce-back detection (A→B→A); `LoopDetector` with ping-pong pattern matching (A→B→A→B repeated); hash-based tool argument dedup | Direct — validates report's visited-set, exposes ping-pong detection gap |
| **Tangle (Intuit)** (2026-03) | Wait-For Graph with incremental DFS; `cancel_youngest` resolver; deadlock (circular wait) vs livelock (repeated messages) distinction | Direct — exposes report's missing resolver strategy |
| **Neural Base** (2026-04) | `transfer_depth` in context dict (not in-process memory); session-level counter; 30s timeout for rapid transfers; Swarm has NO built-in loop detection | Direct — validates report's guard design, exposes need for cross-MCP persistence |
| **Agentproof (arxiv)** (2026-03) | Static temporal verification via graph × DFA product construction; witness traces for debugging | Indirect — advanced verification, not needed for MVP |
| **AWS Multi-Agent** | Orchestrator step counter per task; maximum delegation count; circuit breakers for failing agents | Direct — validates report's iteration budget |

### 4.3 Stale Task Lifecycle & Message Queue Patterns

| Source | Key Finding | Relevance |
|--------|-------------|-----------|
| **Forq** (SQLite MQ) | 7 states: Ready→Processing→Acknowledged→Stale→Failed→Expired→DLQ; 24h TTL default; 7d DLQ TTL | Direct — validates report's state model + TTL values |
| **pgqrs** | Pending→Locked→Archived lifecycle; `read_ct` for poison message detection; archive for audit trail | Direct — validates report's archive-for-audit approach |
| **RabbitMQ** | Message TTL + queue TTL + `x-expires` for unused queues; expired messages discarded at head of queue | Direct — validates report's TTL-based expiry |
| **Asynq** | Scheduled→Pending→Active→Retry→Archived→Completed; retention TTL for completed tasks | Direct — validates report's lifecycle design |
| **Tasker DLQ** | Staleness detection every 5min; `staleness_threshold_minutes` per state; DLQ for investigation tracking | Direct — validates report's background reap loop |
| **TrustHandoff** | Risk-based TTL (write=120s, read=900s); Ed25519 signing; replay protection; depth limit | Direct — validates report's max depth, exposes need for risk-based TTL |
| **Google ADK** (2026-05) | Durable state machines; checkpoint-and-resume; event-driven dormancy; `state_delta` atomic transitions | Direct — validates report's state machine approach |

---

## §5 Verdict

### **MODIFY** — 3 Critical + 2 Moderate Changes Required

#### Critical Changes (Must resolve before implementation)

| # | Issue | Resolution | Effort |
|---|-------|-----------|--------|
| **C1** | `QUEUED` state is undefined — no code or tool transitions to it | Remove `QUEUED`. Use 6-state model matching existing directories. | Low |
| **C2** | Loop guard has no resolver strategy — exceptions are raised but no recovery path defined | Add `ResolverStrategy` enum (TERMINATE/ESCALATE/FALLBACK/RETRY). Default: ESCALATE to Kali. | Low |
| **C3** | Guard state not persisted across MCP tool boundaries — each `hivemind_*` call is a separate HTTP request | Store `guard` dict in the packet JSON. Reconstruct on each tool call. | Medium |

#### Moderate Changes (Should resolve before implementation)

| # | Issue | Resolution | Effort |
|---|-------|-----------|--------|
| **M1** | Pending TTL too aggressive (1h) vs existing (24h) | Use 4h (14400s) as compromise for local model cold-start times | Low |
| **M2** | No startup graph validation for cycles | Add `validate_delegation_graph()` using DFS on `ALLOWED_TRANSITIONS` at import time | Low |

#### Recommended Enhancements (Optional, for future sprints)

| # | Enhancement | Rationale |
|---|-------------|-----------|
| **E1** | Add ping-pong detection (A→B→A→B repeated pattern) | CallSphere proves this catches loops the visited-set misses |
| **E2** | Add witness trace generation on loop detection | Agentproof shows this dramatically aids debugging |
| **E3** | Add risk-based TTL (write operations get shorter TTL) | TrustHandoff proves this reduces stale write exposure |
| **E4** | Add `active → stale` TTL (48h) to lifecycle dictionary | Already implemented in `background.py` but missing from report |

---

## §6 Temple-Grade Gate Compliance

| Gate | Status | Notes |
|------|--------|-------|
| T1 (Version Control) | ✅ | Report is versioned with date stamp |
| T2 (Documentation) | ✅ | 803-line report with source index |
| T3 (Testing) | ⚠️ | Verification gates defined but no test code yet |
| T4 (Code Quality) | ✅ | Python code samples are clean |
| T5 (Architecture) | ⚠️ | State machine needs reconciliation with existing Hivemind dirs |
| T6 (Security) | ✅ | No telemetry, no external calls |
| T7 (Performance) | ✅ | O(1) visited-set lookup, O(1) visit-count check |
| T8 (Resilience) | ⚠️ | Missing resolver strategy = no graceful degradation |
| T9 (Observability) | ✅ | Trace chain logging via `get_chain()` |
| T10 (Integrity) | ⚠️ | Guard state not persisted across MCP boundaries |
| T11 (Agent Security) | ✅ | No IA2 violations |

**Overall Temple-Grade**: 7/11 pass, 4 need attention from this vetting's recommended changes.

---

## §7 M12 Queue Integrity Verification

The stale→archive lifecycle directly supports M12:
- ✅ Every packet reaches a terminal state (`archived`, `completed`, `rejected`)
- ✅ Background reaper enforces TTL transitions every 300s
- ⚠️ Missing: packets in `stale/` without `auto_transition` in the report's dictionary would never reach `archived` — the existing `background.py` handles this but the report doesn't document it
- ⚠️ Missing: no dead-letter handling for packets that fail during handoff execution

---

## §8 Source Index (Vetting Research)

| # | Source | Key Contribution to Vetting |
|---|--------|-----------------------------|
| 1 | Geodocs.dev — Agent Handoff Protocol Spec | `loop_guard` as required field; `on_reject`/`on_timeout` recovery |
| 2 | Microsoft Agent Framework — Handoff Orchestration | Declarative topology; terminal endpoints; graph termination |
| 3 | Agent Patterns Catalog — Handoff | Loop detection prevents thrash; handoff-as-tool pattern |
| 4 | Agent Handoff Protocol (dakshjain) — GitHub | Pydantic HandoffPacket; SQLite broker; TTL + audit |
| 5 | Ziro Agent SDK — RFC 007 | `maxHandoffDepth: 10`; deterministic router; `HandoffLoopError` |
| 6 | AI Tools Guidebook — Cycle Detection | Startup DFS validation; `call_path` threading; witness traces |
| 7 | CallSphere — Debugging Agent Loops | Ping-pong detection; hash-based tool arg dedup; `HandoffTracker` |
| 8 | Tangle (Intuit) — Deadlock/Livelock | Wait-For Graph; `cancel_youngest` resolver; incremental DFS |
| 9 | Neural Base — Infinite Handoff Loops | `transfer_depth` in context; 30s timeout; Swarm has no built-in detection |
| 10 | Forq — Message Queue Spec | 7-state lifecycle; 24h TTL; 7d DLQ; poison message detection |
| 11 | pgqrs — Message Lifecycle | Pending→Locked→Archived; `read_ct`; archive-for-audit |
| 12 | RabbitMQ — TTL & Expiration | Message TTL; queue TTL; `x-expires` for unused queues |
| 13 | Asynq — Task Lifecycle | Scheduled→Pending→Active→Retry→Archived→Completed |
| 14 | TrustHandoff — TLS for Agents | Risk-based TTL; Ed25519 signing; replay protection |
| 15 | Google ADK — Long-running Agents | Durable state machines; checkpoint-and-resume; `state_delta` |
| 16 | AWS Multi-Agent Architectures | Orchestrator step counters; circuit breakers; Step Functions |

---

*Vetted by: @pillar P9 (Orchestration)*
*Date: 2026-06-28*
*Verdict: MODIFY — 3 critical + 2 moderate changes required*
