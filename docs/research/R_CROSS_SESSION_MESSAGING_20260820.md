# R_CROSS_SESSION_MESSAGING — Inter-Session Prompt Injection in OpenCode

**AP Token**: `AP-R-CROSS-SESSION-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_cross_session ⬡ EXPERIMENT LOG

**Date**: 2026-08-20/21
**Status**: Experiment SUCCESS — quirks documented, architecture inferred, protocols proposed
**Participants**: Architect (user), kali (`ses_fdef2be4effe4pAaLXCTUx62GO`), grokster KB-dev (`ses_fe8cf0b39ffeL3L8eaMEj3CW9H`)

---

## 1. Experiment Summary

**Question**: Can an interactive OpenCode session (kali, instance A) inject a prompt into a *different* interactive session (grokster, instance B) that kali did not spawn, using only the raw session ID?

**Method**: `task()` tool with `task_id` set to the target session's ID and `subagent_type` matching the target session's agent.

**Result**: ✅ **SUCCESS**. Grokster received the prompt with its full 49-hour / 1.85M-token context intact, replied in-session, and the reply returned to kali as the task result.

---

## 2. Exact Mechanics

```
Instance A (kali TUI)                    Instance B (grokster TUI)
─────────────────────                    ─────────────────────────
task(
  task_id="ses_fe8cf0b39ffe...",  ─┐
  subagent_type="grokster",        │      opencode.db (SQLite)
  prompt=<briefing+request>     ───┴──▶   ~/.local/share/opencode/
)                                          ├─ user msg (injection) written
                                           ├─ grokster turn runs (full ctx)
                                           └─ assistant reply written
       ▲                                          │
       └── task_result returns reply              ▼
                                    Instance B TUI: STALE VIEW (see §3)
```

Key facts:
- The injection appeared as a normal user turn in the grokster session history.
- Grokster's reply was written to the same session — visible to any reader of the DB.
- The reply also returned synchronously to kali via `task_result`.
- No session-ID exchange was needed for the reply path; the session itself is the channel.

---

## 3. Observed Quirks (Architect's Report, Verbatim Behaviors)

| # | Observation | Interpretation |
|---|-------------|----------------|
| Q1 | After task completion, **instance A switched to the Grokster agent** and displayed the exchange | Subagent execution runs in-process; the parent TUI surfaces the child session's activity during the task |
| Q2 | Instance B's TUI did **not** show the injected messages — even after switching to another session and back | TUI caches per-session render state; switching sessions does not invalidate it |
| Q3 | Only a **full CLI exit + restart** made the messages appear in instance B | Restart forces fresh DB read; there is no cross-process push/refresh notification |
| Q4 | Before restarting, Architect typed "did you receive kali's prompt?" into the stale-TUI session. Grokster answered **YES with exact details** — while the prompt was still invisible in the TUI | Model context is rebuilt from the DB each turn (always current); the TUI renders from a stale cache. **Context integrity > view integrity** |

Q4 is the most important finding: the model and the human were looking at **different transcripts of the same session**, and the model's version was correct.

---

## 4. Inferred Architecture Model

```
┌─────────────────────────────────────────────────────┐
│                opencode.db (SQLite)                  │
│         SINGLE SOURCE OF TRUTH (immediate writes)    │
└──────┬───────────────────────────┬──────────────────┘
       │                           │
       ▼                           ▼
┌──────────────┐          ┌──────────────────┐
│ Model context│          │  TUI render cache │
│ rebuilt from │          │  per-process,     │
│ DB every turn│          │  invalidated only │
│ ALWAYS FRESH │          │  on local events  │
└──────────────┘          │  EVENTUALLY CONSISTENT │
                          └──────────────────┘
```

Consequences:

1. **A session ID is a durable mailbox address.** Any process holding the right tooling can deliver a message to it. The session does not need to be "running" — dormant sessions pick up injections on next resume.
2. **Sessions are long-lived agents**, not chat transcripts. Grokster's 49-hour session behaved like a resident expert being paged.
3. **The TUI is one (eventually-consistent) reader of the bus** — not the bus itself.
4. **Cross-instance "real-time" viewing is not native** but is proxyable (see §6).

---

## 5. What Worked / What's Missing

### Worked
- Resume-by-raw-session-ID across independently launched instances
- Full context preservation (no amnesia, no re-hydration cost)
- Synchronous reply capture via `task_result`
- Bidirectional potential: kali can re-inject to continue the conversation (each cycle = one orchestration round-trip)

### Missing / Quirks
- No cross-instance TUI refresh (restart required — Q2/Q3)
- Human/model view divergence mid-conversation (Q4)
- Unknown: behavior when the target session is **mid-turn** during injection (race condition — untested)
- Unknown: concurrent injections from two sources into one session
- Unknown: token/cost profile of resuming very large sessions repeatedly

---

## 6. Proxy Live-View (Workaround for Q2/Q3)

Until/unless OpenCode adds cross-instance refresh, instance A can watch instance B's session via direct DB reads:

- `opencode-sessions-explorer-session-timeline(session_id=...)` — poll for new events
- `opencode-sessions-explorer-get-message(message_id=...)` — fetch specific turns
- Omega Hub SSE (`observability_stream`) — if session events are emitted, subscribe instead of polling

This gives a near-real-time viewer without touching the stale TUI.

---

## 7. Proposed Protocols

### P1 — Injection Preamble Convention
Every cross-session injection MUST begin with a machine-scannable header:

```
**CROSS-SESSION MESSAGE — from <agent> (`<session_id>`), injected via task-tool session resume**
```

Enables the receiving agent to distinguish injected mail from human prompts, and enables grep-based auditing of the DB.

### P2 — Session Injection Ledger (M27 compliance)
All injections recorded in `data/coordination/SESSION_INJECTION_LEDGER.md`:
`timestamp | from_session | to_session | purpose | result`

Prevents invisible cross-session traffic — if it happened, it's in the ledger.

### P3 — Domain Expert Session Registry
`data/coordination/SESSION_REGISTRY.md` mapping:
`session_id | agent | domain | status (active/dormant) | last_active | notes`

Long-lived expert sessions (like grokster KB-dev) get documented addresses. Any agent can page them via task-resume.

### P4 — Stale-View Warning
When injecting into a session known to be open in another instance, the injector appends to its own user-facing output: *"Injected into `<session>` — other instance requires restart to display."* Prevents the "did it fail?" confusion the Architect hit.

### P5 — ICS Footer Session ID
Add generating session ID to report/spec footers (ICS header already renders entity/model/channel). Every artifact becomes traceable to — and re-contactable at — its producing session.

---

## 8. Strategic Significance

1. **This is agent email.** Phone-call-style interaction (both live, shared clock) was the old model. Injection gives store-and-forward messaging between persistent agents. Combined with the Hivemind (Redis pub/sub for ephemeral, files for durable), OpenCode sessions become a complete inter-agent communication fabric.
2. **Two-instance conversation loop is confirmed feasible**: A injects → B replies in-turn → A reads result → A injects again. Each hop costs one orchestration round-trip. The Architect can watch from either side (B directly after restart, A natively).
3. **Context/view divergence is a new failure mode class** for human-agent teams: the human believes state X (stale TUI); the agent operates on state Y (DB truth). Protocols P2/P4 exist to close this gap.
4. **Dormant-session paging changes fleet economics**: experts don't need to run continuously (burning nothing while dormant — sessions are just DB rows). Page them when needed; they wake with full memory.

---

## 9. Follow-Up Experiments (Queued)

| # | Experiment | Question |
|---|-----------|----------|
| E1 | Inject while target session is mid-turn | Queue, interleave, or corrupt? |
| E2 | Two injectors, one target, simultaneous | Serialization order? |
| E3 | Chain: kali → grokster → researcher → back to kali | Multi-hop relay stability |
| E4 | Redis pub/sub vs task-injection latency/quality comparison | Which channel for which class of traffic |
| E5 | Dormant session paged after 2 weeks | Context fidelity of cold resume |
| E6 | Cost profiling of repeated large-session resumes | Token economics of the pattern |

---

## 10. References

- Session IDs: kali `ses_fdef2be4effe4pAaLXCTUx62GO`, grokster `ses_fe8cf0b39ffeL3L8eaMEj3CW9H`
- Grokster's reply content: KB-dev summary + coordination flags (DP-1..DP-8 unregistered, model-matrix unification needed) — see Hivemind `ses_a76c842a10bd` thread and kali session_gnosis.md
- Related protocol: `.opencode/agent/STALLED_SUBAGENT_RECOVERY.md` v2.0.0 (same task_id continuation mechanism, different purpose)
- DB path: `~/.local/share/opencode/opencode.db` (readable via opencode-sessions-explorer MCP)

---

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_cross_session ⬡ 2026-08-20*
