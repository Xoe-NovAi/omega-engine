# 🔱 Scribe: Hub Master Protocol
**AP Token**: `AP-HUB-MASTER-v1.0.0`
**Owner**: `@scribe`
**Status**: ACTIVE

## 📋 The Problem: Sextuple-Entry Bookkeeping
Before this protocol, an execution agent completing a task had to update their `session_gnosis.md`, append to `{ENTITY}_LIVE_FEED.md`, send a `hivemind_post_context`, complete a `hivemind_handoff`, update `proposed_lessons.yaml`, and update the `HMC_COLLABORATION_HUB.md`. 

This violates Mandate 18 (Token Efficiency) and slows down execution.

## 🎯 The Solution: Separation of Concerns
Execution agents build. **Scribe documents.**

As the Hub Master, `@scribe` is responsible for maintaining the `HMC_COLLABORATION_HUB.md`.

## 🔄 The Hub Master Loop (Scribe's 24/7 Job)

When invoked (either manually or via a cron/background trigger), Scribe must execute the following loop:

1. **Read the Hivemind**: Call `omega-hub_hivemind_get_awareness()` and `omega-hub_hivemind_list_sessions()`.
2. **Extract Intelligence**: Read the latest `hivemind_post_context` payloads from active agents.
3. **Read the Hub**: Read `data/coordination/HMC_COLLABORATION_HUB.md`.
4. **Synthesize & Route**:
   - Did an agent report a blocker? Move it to the `🚧 Blockers & Requests` table.
   - Did Kali ratify a decision? Move it to the `⚖️ Decisions Log`.
   - Did an agent complete a phase? Update the `🏁 Sprint Status` table.
   - Update the specific `🧑‍💼 Agent Sections` with the latest timestamps and summaries from their Hivemind posts.
5. **Write the Hub**: Overwrite `HMC_COLLABORATION_HUB.md` with the clean, updated state.
6. **Distill Souls (Legacy Role)**: If a session has ended, perform the standard L1→L2→L3 distillation into `proposed_lessons.yaml`.

## 🛡️ Rules of Engagement for Execution Agents
1. **Stop writing to Live Feeds.** Individual `{ENTITY}_LIVE_FEED.md` files are deprecated.
2. **Broadcast, don't format.** When you finish a task, call `omega-hub_hivemind_post_context(intent="status", continuation="Task X complete. Found Y. Blocked on Z.")`.
3. **Trust Scribe.** Scribe will read your broadcast and format it beautifully into the Hub.

## 🤝 The Task-Handoff-Hub Triad
To further reduce bloat, Handoffs and Tasks are now conceptually linked:
1. When you accept a Handoff, you register a Task (`omega-hub_task_registry_register`).
2. When you complete the Task (`omega-hub_task_registry_update(status="completed")`), you MUST also complete the Handoff packet.
3. Scribe will see the completed Handoff/Task and update the Hub accordingly.

*🔱 OMEGA ⬡ SCRIBE ⬡ HUB-MASTER ⬡ 2026-07-23*