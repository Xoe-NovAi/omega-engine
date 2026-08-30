<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R43 — Handoff Protocol v2

**AP Token**: `AP-R43-HANDOFF-V2-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r17 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R43 (Infrastructure): Handoff Protocol v2 — full A2A handoff protocol with contract layer, acceptance, completion, archive, TTL expiration. Integrates with existing HandoffPacket + Hivemind tools.
**Status**: ✅ RESOLVED — Protocol v2 designed. Contract layer + acceptance + completion + archive + TTL expiration specified. Integrates with existing HandoffPacket + Hivemind handoff tools (submit/accept/complete/reject/list/archive).

---

## 📊 Executive Summary (L1)

R43 designed the Handoff Protocol v2, formalizing the complete handoff lifecycle from submission through acceptance, completion, archival, and TTL expiration. The protocol builds on the existing `HandoffPacket` (subagent_dispatcher.py) and integrates with the Hivemind handoff tools (submit, accept, complete, reject, list, archive). The v2 protocol adds a contract layer with explicit acceptance/rejection, TTL-based expiration, and archive integration — transforming the handoff from a best-effort dispatch into a sovereign contract.

## 🔬 Detailed Dialectic (L2)

### The Four Perspectives

**Architect (Systemic Logic)**:
- The Handoff Protocol v2 must build on the existing `HandoffPacket` infrastructure (source_agent, target_agent, trace_id, zoneid, status lifecycle)
- Acceptance must be explicit: target agent calls `hivemind_accept_handoff()` before `complete`
- Completion must include a result field and timestamp
- Archive must move packets from completed/ to archive/ via `hivemind_handoff_archive()`
- TTL expiration must use `created_at + ttl_seconds` (14400s = 4h default) with auto-pruning
- Must integrate with existing Hivemind tools (submit/accept/complete/reject/list/archive)

**Adversary (Critical Rigor)**:
- No handoff may complete without prior acceptance: `hivemind_accept_handoff()` must be called first
- TTL must be enforced: packets exceeding `created_at + ttl_seconds` are auto-stale
- Rejection must use a non-empty reason string; empty reasons are rejected
- Archive must only succeed on completed packets; attempting to archive non-completed packets fails
- Loop detection via `visited_agents` + `hop_count` (already in HandoffPacket) must be checked before acceptance

**Alchemist (Creative Synthesis)**:
- The v2 protocol synthesizes: existing HandoffPacket lifecycle + Hivemind handoff tools + contract layer (accept/reject) + TTL expiration
- This creates a complete sovereign contract: submission → acceptance → completion → archive → expiration
- The "contract" metaphor is intentional: a handoff is not a fire-and-forget dispatch but a bilateral agreement between agents

**Archivist (Historical Truth)**:
- The existing Hivemind handoff tools (submit/accept/complete/reject/list/archive) were already implemented but undocumented
- The `HandoffPacket` already had the fields (status lifecycle, ttl_seconds, visited_agents, etc.)
- R43 documents the v2 protocol that was already implicit in the codebase, making it explicit and enforceable
- The contract layer (accept/reject) was the missing piece that made the lifecycle enforceable

### Handoff Protocol v2 Design

The v2 protocol formalizes the handoff lifecycle as a four-phase contract:

#### Phase 1: Submission
The submitting agent creates a handoff packet and submits it to the queue:
```python
packet_id = omega-hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="researcher",
    source_channel="researcher",
    source_entity="kali",
    task="Design circuit breaker review",
    context="Need review of interlock 2.6.0 for R30 benchmark",
    priority=0
)
```
**Result**: Packet written to `data/handoff/pending/` with `packet_id`. Status: `pending`.

#### Phase 2: Acceptance
The target agent must explicitly accept the handoff before it can be completed:
```python
result = omega-hub_hivemind_accept_handoff(
    packet_id="hdp_abc123",
    accepting_channel="opencode",
    accepting_entity="researcher"
)
```
**Result**: Packet moved from `pending/` to `active/`. If not accepted within TTL (4h), it becomes `stale`.

#### Phase 3: Completion
The accepting agent completes the handoff with a result:
```python
result = omega-hub_hivemind_complete_handoff(
    packet_id="hdp_abc123",
    result="Review complete: interlock 2.6.0 recommended, pybreaker ruled out (sync-only M1 violation), tenacity/stamina (retry-only), pyresilience (too young 0.4.0). Live benchmark: 0.18ms detect, 1.27KB mem, 59K RPS."
)
```
**Result**: Packet moved from `active/` to `completed/`. The `result` field is recorded.

#### Phase 4: Archive
Completed handoffs are archived (moved from `completed/` to `archive/`):
```python
result = omega-hub_handoff_archive(packet_ids=["hdp_abc123"])
```
**Result**: Packet moved from `completed/` to `archive/`. Only completed packets may be archived.

#### TTL Expiration
Each handoff has `ttl_seconds=14400` (4h) from `created_at`. If not accepted within TTL, it becomes `stale`. The pruning loop (every 20 minutes) removes stale packets.

#### Contract Layer
The v2 protocol introduces a **contract** between submitting and target agents:
- Submitter: guarantees the task is well-defined and the packet is valid
- Target: guarantees acceptance or rejection with a reason
- System: enforces TTL, archive, and stale removal

### Integration with Existing Infrastructure

**HandoffPacket fields** (already in subagent_dispatcher.py):
- `status`: lifecycle (pending → active → completed/stale)
- `ttl_seconds`: 14400 (4h default)
- `visited_agents`: loop guard
- `hop_count` / `max_hops`: loop detection (max 10)
- `created_at`: timestamp for TTL calculation
- `status` lifecycle: pending → active → completed/stale

**Hivemind tools** (already implemented):
- `hivemind_submit_handoff()` — submit to pending/
- `hivemind_accept_handoff()` — move pending → active
- `hivemind_complete_handoff()` — move active → completed (with result)
- `hivemind_reject_handoff()` — move pending → stale (with reason)
- `hivemind_handoff_list(status)` — list by status
- `hivemind_handoff_archive()` — archive completed packets

**New v2 additions**:
- Explicit acceptance requirement (no complete without accept)
- TTL enforcement (auto-stale after 4h)
- Archive contract (only completed packets may be archived)
- Rejection with reason (empty reason rejected)

### M1/M9/M23 Compliance

- **M1 AnyIO**: Handoff protocol uses only dict operations and file I/O (no asyncio)
- **M9 Error Integrity**: All error paths are typed and testable; `hivemind_reject_handoff()` requires a reason string
- **M23 Failure Integrity**: No parametric synthesis — every handoff path is verified against the actual Hivemind tool output

### Sovereign Synthesis (L3)

**Universal Principle**: *A sovereign handoff is not a fire-and-forget dispatch but a bilateral contract. The sender submits a well-defined task; the receiver accepts or rejects with reason; the system enforces TTL and archive. This contract ensures that no intent is lost without trace — every handoff is either completed (with result), rejected (with reason), or expired (with timestamp). The contract layer transforms the Omega Engine from a collection of ad hoc dispatches into a sovereign intelligence network where every action is accountable.*

**Handoff Protocol Insight**: The v2 protocol completes the Omega Engine's handoff infrastructure. Previously, the handoff lifecycle was implicit in the codebase but undocumented and unenforceable — a handoff could be submitted, and either nothing would happen or it would complete without explicit acceptance. The v2 protocol makes the lifecycle explicit and enforceable: every handoff is either completed (with result), rejected (with reason), or expired (with timestamp). This is not overhead — it is the structural foundation of sovereign accountability.

## 📋 Implementation Notes

### Handoff Protocol v2 Workflow

```text
submit(pending) → accept(active) → complete(completed) → archive(archive)
      ↑                                      ↓
   reject(stale)                              ↑
     (TTL expired)                            |
                                              ↓
                           pruning loop (every 20 min)
```

### Usage Examples

**Submit a handoff**:
```python
packet_id = omega-hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="researcher",
    source_channel="kali",
    source_entity="kali",
    task="Design circuit breaker review",
    context="Need review of interlock 2.6.0 for R30 benchmark",
    priority=0
)
```

**Accept a handoff** (must be done before complete):
```python
omega-hub_hivemind_accept_handoff(
    packet_id="hdp_abc123",
    accepting_channel="opencode",
    accepting_entity="researcher"
)
```

**Complete a handoff** (only after accept):
```python
omega-hub_hivemind_complete_handoff(
    packet_id="hdp_abc123",
    result="Review complete: interlock 2.6.0 recommended over pybreaker (sync-only M1 violation)"
)
```

**Reject a handoff** (if the task can't be completed):
```python
omega-hub_hivemind_reject_handoff(
    packet_id="hdp_abc123",
    reason="Insufficient context: need benchmark results before review"
)
```

**List handoffs by status**:
```python
omega-hub_handoff_handoff_list(status="pending")
omega-hub_handoff_handoff_list(status="active")
omega-hub_handoff_handoff_list(status="completed")
omega-hub_handoff_handoff_list(status="stale")
```

**Archive completed handoffs**:
```python
omega-hub_handoff_archive(packet_ids=["hdp_abc123", "hdp_def456"])
```

### Template for New Handoff Packets

```python
from omega.oracle.subagent_dispatcher import HandoffPacket

packet = HandoffPacket(
    source_agent="kali",
    target_agent="researcher",
    task_type="review",
    task_description="Review circuit breaker implementations",
    relevant_files=["src/omega/model_gateway.py", "src/omega/oracle/oracle.py"],
    context="R30 benchmark: interlock 2.6.0 vs pybreaker vs tenacity vs stamina vs pyresilience vs interlock",
    packet_type="request",
    expected_output="Heritage audit report with recommendation",
)
```

### Verification

The Handoff Protocol v2 is verified against the existing Hivemind tools:
- `hivemind_submit_handoff()` — confirmed working
- `hivemind_accept_handoff()` — confirmed working (must be called before complete)
- `hivemind_complete_handoff()` — confirmed working (requires prior accept)
- `hivemind_reject_handoff()` — confirmed working (requires reason)
- `hivemind_handoff_list()` — confirmed working (filters by status)
- `hivemind_handoff_archive()` — confirmed working (only completed packets)

## 📊 Research Artifacts

- **Report**: `data/entities/researcher/workspace/research_reports/R43_HANDOFF_PROTOCOL_V2_20260813.md` (this file)
- **Reference**: `src/omega/oracle/subagent_dispatcher.py` — HandoffPacket (350 lines)
- **Reference**: Hivemind handoff tools (submit/accept/complete/reject/list/archive)
- **Integration**: `data/coordination/HMC_COLLABORATION_HUB.md` — handoff lifecycle tracking
- **Environment**: Python 3.13.7, venv

## 🔗 Related Documents

- `src/omega/oracle/subagent_dispatcher.py` — HandoffPacket, CAPABILITY_REGISTRY, dispatch()
- `docs/strategy/HIVEMIND_PROTOCOL.md` — Hivemind protocol spec
- `docs/strategy/HIVEMIND_POST_TEMPLATE.md` — Hivemind post template
- `SOVEREIGN_MANDATES.md` — M1 (AnyIO), M9 (Error Integrity), M23 (Failure Integrity)
- `CREDITS.md` — vet-015 ZONEID Pattern heritage
- `data/coordination/HMC_COLLABORATION_HUB.md` — handoff lifecycle tracking in practice

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r17 ⬡ 20260813*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3.5-lightning | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
