<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Conversational Subagent Protocol — Multi-Turn Agent Conversations via the Task Tool

**AP Token**: `AP-CONV-SUBAGENT-PROTOCOL-v1.0.0`
**Status**: ACTIVE — Ratified 2026-08-21 (Architect + Kali)
**Scope**: Task-origin subagent sessions engaged over multiple `task()` calls
**Companion docs**: `STALLED_SUBAGENT_RECOVERY.md` v2.0.0 (G1–G3 guardrails) · `R_CONVERSATIONAL_SUBAGENTS_STUDY_20260821.md` (evidence base)

---

## 1. Definition

A **conversational subagent** is a subagent session treated as a persistent counterpart rather than a one-shot function call:

- Spawned once via `task()` → receives a `task_id`
- Engaged repeatedly by prompt continuation on that SAME `task_id`
- Exchanges may occur **within one orchestrator turn** (tight loop) or **across turns** (async mail — injections into a busy session queue safely)

Evidence: behaviors B1–B15 in the study report; relay chain kali→grokster→kali completed 2026-08-21.

---

## 2. The Core Loop

```
LAUNCH     task(subagent_type, prompt-with-manifest)      → task_id
   ↓
AUDIT      files written? task calls fired? (DB > guess)  ← G3
   ↓ ┌─ gaps? → CONTINUE same task_id, compact prompt ←── G2
   ↓ └─ clean? → accept deliverable
ENGAGE     further prompts as needed (same task_id)
   ↓
RELEASE    final summary to Hivemind; session stays dormant
```

---

## 3. Binding Rules

### R1 — One session per counterpart
Never spawn a fresh `task()` for work a live `task_id` already owns. All continuation goes through the original `task_id`. (Preserves context, avoids duplicate-cost resumes.)

### R2 — Tight-loop engagement is legal
An orchestrator MAY issue multiple sequential prompts to the same subagent within ONE turn — stall recovery, section-by-section writing, follow-up questions. Proven repeatedly (B14).

### R3 — Queueing is safe; rely on it
Injections into a mid-turn session queue and deliver at the turn boundary, ordered, without loss (B10). Do NOT poll or re-send because a reply seems slow — check the DB instead.

### R4 — File-first doctrine
Durable artifacts are written to disk in small incremental appends BEFORE any reply or relay-task is composed. Monolithic streamed responses die mid-flight (B12/B13). Prompts carry pointers (≤500–800 words); files carry content.

### R5 — Chains require a declared terminus (amended 2026-08-21: hop budgets REMOVED)
~~Numeric hop budgets~~ **REMOVED per Architect ruling** — task-origin chains (sessions created as subagents from the start) exhibit none of the interactive-session failure modes that motivated hop caps. What remains binding: every chain declares its **terminus condition up front** (what event ends it: question answered, artifact complete, explicit close) and every participant honors R10 closeout. Runaway protection lives in this terminus requirement plus the Anti-Patterns list ("unbounded reply-loops").

### R6 — Preamble convention
Every injected prompt begins:
```
**CROSS-SESSION MESSAGE — from <agent> (`<session_id>`), injected via task-tool session resume**
**RELAY HOP: N of MAX** (if chaining)
```

### R7 — Audit before retry
On empty/aborted results, query the DB (or filesystem) for partial progress BEFORE re-prompting: report file exists? `task` calls fired from the target session? Then continue with ONLY the remaining work. Blind retries duplicate work and burn large-context resumes.

### R8 — Ledger every cross-session injection
Record in `data/coordination/SESSION_INJECTION_LEDGER.md`:
`timestamp | from_session | to_session | hop | purpose | outcome`

If it happened, it's in the ledger (M27 spirit).

### R9 — Identity by session ID, never by color
Nested subagent views keep the parent's label color (B7). Verify counterparts by session ID.

### R10 — Termination hygiene
Every chain ends with: final artifact on disk + Hivemind closeout post (intent=`status`) + ledger row. A chain that "just stops" is a violation.

### R11 — Max-steps completion is not done
If a subagent returns `completed` but the manifest is incomplete (step limit reached, no error shown), treat as stalled: audit the DB for actual progress (R13), then page a continuation prompt scoped to REMAINING work only. Proven pattern: N7↔Roc mining continuation (2026-08-21).

### R12 — Summaries must carry questions back
Every subagent final summary MUST close with a `## Questions for Pager` section (≥1 question expected on non-trivial tasks). This enables drill-down: the pager answers in the next page prompt, converging on exactly what the work needs instead of guessing. Nodes use this to iterate with Roc/Researcher/Kali sessions.

### R13 — Empty result ⇒ mandatory DB audit before continuation
On an empty or truncated `task_result`, the orchestrator MUST inspect the session's actual last outputs in `opencode.db` (direct sqlite or opencode-sessions-explorer tools) BEFORE composing the continuation prompt. Never re-prompt blind: work may be complete (false negative), partial (scope the continuation), or absent (full re-dispatch). Verified twice on 2026-08-21: N7 mining (work complete, reply lost) and relay HOP-1 (abort mid-turn, 0 tokens).

---

## 4. Anti-Patterns

- ❌ Fresh `task()` spawn to redo work an existing `task_id` owns
- ❌ Re-sending an injection because no reply arrived quickly (it's queued — B10)
- ❌ Composing whole reports inside chat responses instead of incremental file writes
- ❌ Unbounded hop chains ("reply back and we'll keep going")
- ❌ Trusting agent-label color in nested views
- ❌ Accepting `state:"completed"` + empty result as done (audit first — G3)
- ❌ Interactive-origin sessions in production chains (study-only until post-debut tooling exists)

---

## 5. Relationship to Existing Protocols

| Doc | Role |
|-----|------|
| `STALLED_SUBAGENT_RECOVERY.md` v2.0.0 | G1 manifest / G2 recovery / G3 audit — the per-engagement guardrails this protocol builds on |
| This protocol | The multi-turn, multi-session layer: engagement loops, chains, queueing semantics, ledgers |
| `TRACKING_ARCHITECTURE.md` | Ledger entries feed Tier-3 execution records |

---

## 6. Ratified Scope Boundary (Architect, 2026-08-21)

Conversational **task-origin** subagents = OFFICIAL protocol, effective now.
Conversing with **interactive-origin** sessions (human-addressable message box, cross-instance TUI quirks) = documented in the study report only; revisit post-debut, possibly as a mail plugin (E12).
