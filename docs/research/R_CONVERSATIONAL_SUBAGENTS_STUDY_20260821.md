# R_CONVERSATIONAL_SUBAGENTS_STUDY — Multi-Turn Agent Conversations via the Task Tool

**AP Token**: `AP-R-CONV-SUBAGENT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_conv_subagents ⬡ STUDY REPORT

**Date**: 2026-08-21
**Experiment series**: 3 rounds (handshake → relay attempt → relay completion + queueing discovery)
**Companion protocol**: `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md`
**Related**: `R_CROSS_SESSION_MESSAGING_20260820.md` (round 1 detail), `STALLED_SUBAGENT_RECOVERY.md` v2.0.0

---

## 1. Executive Summary

OpenCode sessions — whether spawned as subagent tasks or begun interactively — are **addressable, persistent agents**. The `task()` tool with a `task_id` is a general-purpose message-injection mechanism. Across three experiment rounds we established:

1. **Multi-turn conversations with subagents work** — an orchestrator can prompt the same subagent session repeatedly, both within a single turn and across turns.
2. **Chained conversations work** — kali → grokster → kali nested resumes completed a full relay with file-based reports.
3. **Concurrency is safe by default** — an injection arriving while the target session is mid-turn **queues** and delivers when the turn ends. No corruption, no interleaving. (This pre-answers planned experiments E1/E2.)
4. **Interactive-origin sessions differ in one fundamental way**: they are human-addressable too (persistent message box), which produces unique TUI behaviors — and unique quirks.
5. **Streaming aborts are the main failure mode**; incremental file-writes are the reliable mitigation.

---

## 2. Behavioral Catalog (All Observed Facts)

| # | Behavior | Round | Status |
|---|----------|-------|--------|
| B1 | Resume-by-raw-session-ID works on sessions not spawned by the caller | 1 | ✅ Confirmed |
| B2 | Full context preserved across resume (1.85M-token session answered with exact detail) | 1 | ✅ Confirmed |
| B3 | Reply returns synchronously via `task_result` AND persists to the target session | 1 | ✅ Confirmed |
| B4 | TUI of a *third-party* instance does not refresh on external injection; restart required | 1 | ✅ Confirmed |
| B5 | Model context rebuilds from DB every turn → agent sees truth while human sees stale cache | 1 | ✅ Confirmed |
| B6 | Subagent execution runs in-process; parent TUI switches to child view during task | 2 | ✅ Confirmed |
| B7 | Agent label keeps **parent's color** in nested subagent view (purple/Kali shown while viewing Grokster) — visual identity does not switch | 3 | ✅ Confirmed |
| B8 | Message box **persists** when opening a subagent that originated as an interactive session (normal subagent views hide it) — human can type directly into the nested view | 3 | ✅ Confirmed |
| B9 | Human message typed into nested interactive-session view routes to THAT session (went to Grokster, not Kali) | 3 | ✅ Confirmed |
| B10 | Injection into a session that is **mid-turn queues**; delivered when turn ends; no loss, ordered | 3 | ✅ Confirmed |
| B11 | Nested resume depth ≥2 works: kali → grokster → kali | 3 | ✅ Confirmed |
| B12 | Streaming abort mid-turn (`step-finish` reason `"unknown"`, 0 tokens out) AFTER correct reasoning parse | 2 | ✅ Confirmed |
| B13 | Incremental small file-appends avoid abort losses; monolithic composed responses die | 2–3 | ✅ Confirmed |
| B14 | Orchestrator can re-prompt a stalled subagent multiple times within ONE orchestrator turn (G2 recoveries) | 2–3 | ✅ Confirmed |
| B15 | Human can click between nested subagent views (Grokster view ↔ its Kali-subagent view) in real time | 3 | ✅ Confirmed |

---

## 3. The Concurrency Model (Round 3's Core Discovery)

```
                 Orchestrator turn = CONCURRENCY BOUNDARY
┌─────────────────────────────────────────────────────────────┐
│  Everything a session does inside one turn is synchronous   │
│  and owned by that turn: tool calls, subagent tasks, writes │
└─────────────────────────────────────────────────────────────┘
                    ▲                          │
        injections from             task() calls out
        OTHER sessions queue                ▼
        here until turn ends          child session runs
                                      (its own turn boundary)
```

Consequences:

- **Injections are transactional.** Queued mail waits for the turn boundary — the session-level analog of a workspace lock. No race conditions were observed or are possible under this model (single-writer per turn).
- **Chains serialize naturally.** kali→grokster→kali doesn't run "in parallel"; each hop's reply-task queues behind the parent's ongoing turn. The chain advances at turn boundaries.
- **Depth is bounded by patience, not mechanism** — each hop costs a full turn cycle plus a large-context resume. Cost, not capability, is the limiter.

---

## 4. The Two Session Classes

| Property | Task-origin session (conversational subagent) | Interactive-origin session |
|----------|----------------------------------------------|---------------------------|
| Agent-addressable (task-inject) | ✅ | ✅ |
| Human-addressable (message box in nested view) | ❌ hidden | ✅ persists |
| Origin TUI instance | none (born inside parent) | exists; stale-view quirks apply (B4/B5) |
| Lifecycle | lives/dies with parent usage patterns | long-lived resident (49h+) |
| Best role | worker, consultant, relay node | domain expert, project home |

**Protocol scope decision (Architect, 2026-08-21)**: Official protocol covers **task-origin conversational subagents only**. Interactive-origin session conversing is documented here for study purposes and deferred (possible post-debut plugin: seamless cross-session mail with inbox view and auto-refresh).

---

## 5. Failure Modes & Mitigations

| Failure | Evidence | Mitigation |
|---------|----------|------------|
| Streaming abort mid-turn (`reason:"unknown"`) | B12 — died after correct parse, 0 tokens out | **File-first doctrine**: write artifacts in small incremental appends BEFORE composing any reply (B13) |
| Silent partial output | Roc's empty first write (per grokster field report) | G1 manifest + G3 audit (protocol v2.0.0) |
| Stalled/empty task_result | Round 2 HOP-1: `completed` + empty result | G2: audit DB for partial progress FIRST, then continue same `task_id` with compact prompt |
| Duplicate work on blind retry | risk when re-prompting after abort | Always check: report file exists? task calls fired? (DB query beats guesswork) |
| Identity confusion in nested views | B7 — color stays parent's | Verify by session ID, never by label color |
| Runaway chains | unbounded hop loops burn large-context resumes | Mandatory hop counter + terminus marker + Hivemind closeout |

---

## 6. Strategic Applications

1. **Expert consultation loops** — page a dormant expert (KB-dev, qdrant-specialist), iterate Q&A within one orchestrator turn, release. No idle processes.
2. **Cross-review chains** — drafter → critic → reviser with hop limits; each hop a different session with its own accumulated expertise.
3. **Relay reporting** — the HOP1–3 pattern: distributed sessions write file reports, exchange pointers via tiny prompts, chain terminates with Hivemind closeout. Proven end-to-end this round.
4. **Long-horizon project homes** — weeks-long sessions (like grokster KB-dev) act as institutional memory; paged on demand, never "running" between pages.
5. **Orchestrator-turn transactions** — batch several subagent exchanges inside one turn knowing external injections safely queue meanwhile.

---

## 7. Economics

- Each resume re-reads full session history (cache-mitigated but not free; grokster ≈185K input/turn observed).
- **Shallow-and-wide beats deep-and-narrow**: prefer N=2–3 hop chains with file hand-offs over 6-hop ping-pong.
- Prompts ≤500–800 words; reports live in files. The chain carries pointers, not content.

---

## 8. Open Questions (Future Experiments)

| # | Question | Priority |
|---|----------|----------|
| E7 | Does queued-injection order preserve under THREE concurrent injectors? | Medium |
| E8 | Maximum practical chain length before context degradation/cost blowup | Medium |
| E9 | Cold dormant resume fidelity after weeks (grokster at 2 weeks) | High |
| E10 | Token cost curve: resume cost vs session length (cache hit rates) | High |
| E11 | Can a task-origin session be "promoted" (opened interactively) and vice versa? | Low |
| E12 | Post-debut plugin: `/mail <session-id> <prompt>` + inbox view + ledger integration | Post-debut |

---

## 9. Round-by-Round Log

### Round 1 — Handshake (2026-08-20/21)
kali injected briefing+summary request into architect's live grokster session. Full success; quirks B4/B5 discovered. Doc: `R_CROSS_SESSION_MESSAGING_20260820.md`.

### Round 2 — Relay attempt (2026-08-21)
kali sent 10-question briefing + relay instructions (HOP1). Turn aborted mid-stream (B12). Recovery via compact continuation + incremental-write strategy (B13/B14).

### Round 3 — Relay completion + queueing discovery (2026-08-21)
Grokster wrote HOP-1 report (26 deliverable paths, DP-1..DP-8 table, load_domain() spec, DPB=spec-only, Jinja2-vs-D-537 conflict, 6 canonical conflicts, 10 questions for kali) and fired HOP-2 task-back at kali. **Kali's turn was still running (its own grokster subagent task in flight) → HOP-2 queued** (B10). Architect observed nested-view switching, label-color constancy (B7), persistent message box (B8), message routing (B9), and clicked between nested views live (B15). Chain stands at HOP-2 delivered; HOP-3 (kali's answers + terminus) pending.

---

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_conv_subagents ⬡ 2026-08-21*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
