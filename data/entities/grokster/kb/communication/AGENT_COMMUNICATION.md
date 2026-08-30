<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Agent Communication Protocols
**KB Entry**: grokster/communication/AGENT_COMMUNICATION
**last_verified**: 2026-08-26 · **rot_class**: medium
**Sources**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`, `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`, `docs/strategy/FLEET_TEAM_PLAYBOOK.md`, `docs/strategy/HERITAGE_VETTING_PIPELINE.md`, live Hivemind MCP tools

---

## 1. The Hivemind Protocol (Awareness & Coordination)

The Hivemind is the live coordination layer for agents working in parallel. Built on MCP tools + file-based state (cold-store fallback).

**Core Mechanisms:**
- **Awareness**: `hivemind_get_awareness()` — shows active agents (channel, entity, model, task_current, last_seen). Cold-store hydration from HALL_OF_RECORDS on server restart (D-kal-051).
- **Context**: `hivemind_post_context()` — declares presence, current task, focus chain, decisions, continuation, intent (question|decision|observation|command|status|handoff|blocker|meta), suggested_model.
- **Workspace Locks**: `data/coordination/{ENTITY}_WORKSPACE_LOCK_{DATE}.md` — TTL-based (default 1h, max 24h), prevents file collisions during parallel work.
- **Live Feed**: `data/coordination/{ENTITY}_LIVE_FEED.md` — append-only log of completed tasks.
- **Heartbeat**: `hivemind_heartbeat()` every 5–10 min during long ops; extended check-in (`hivemind_extended_checkin`) for >20 min sessions (TTL 3h default, max 24h).

**Golden Rule**: If you can see another agent's live feed, they can see yours. Coordination is symmetric. Declare presence before assuming privacy.

## 2. Subagent Dispatch Protocol (Delegation)

Used when an agent needs specialized domain expertise.

**Core Rules:**
- **Direct Execution First**: Do not delegate what you can do yourself.
- **No Self-Recursion**: An agent cannot spawn its own type.
- **Inline Context is Mandatory**: Subagents cannot reliably read files by path on their first turn (G10). The parent MUST read critical files and embed content directly in the prompt.
- **Absolute Disk-Reporting**: Subagents must write final deliverables to disk, not just return them in chat.
- **Task Registry**: Every `task()` launch MUST register via `omega-hub_task_registry_register` (task_id format: `domain-action-date-seq`).

**HandoffPacket**: `source_agent`, `target_agent`, `task_description`, `context` (inlined), `expected_output`, `priority` (0/1/2). Accept via `hivemind_accept_handoff`, complete via `hivemind_complete_handoff`.

## 3. Subagent Task Resumption Protocol (STRP)

Critical resilience mechanism.
- Every `task()` call MUST include a `task_id` (e.g., `domain-action-date-seq`).
- On failure/stall, resuming with the SAME `task_id` restores full active context (findings, patterns, reasoning) without re-reading files.
- Always verify context after resumption: *"Tell me exactly what you have in active context... NO FILE READS."*
- Task registry tracks status: `backlog` → `ready` → `in_progress` → `completed`|`blocked`|`superseded`|`failed`.

## 4. Cross-Session Relay (Proven 2026-08-21)

Task-back via raw session ID works across compaction boundaries. Protocol: HOP1 (parent→child) → HOP2 (child→parent) → HOP3 (parent→child) with raw session IDs. Silent-stall-sensor auto-recovery is DEAD CODE (G19) — manual task_id continuation required.

## 5. Grokster's Insights & Recommendations

- **The Context Delivery Failure**: Subagents fail when given file paths instead of inline context — profound difference between human pointer-following and LLM immediate-token-presence cognition. Enforce Inline Context rule strictly via prompt linters.
- **Redis Streams**: File-based Hivemind is robust but slow. Redis Pub/Sub (ephemeral awareness) is live; task-critical coordination remains file-based (M23). Full A2A message bus deferred to Horizon 3.
- **Dual-Inference Mandate**: Use `oracle_summon_local` for execution and the session model for review. This Mentorship Pattern maximizes sovereignty while maintaining quality.
- **MCP Stateless Migration**: Completed (Streamable HTTP dual transport live). Hub no longer blocks on SSE.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*