---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_report"
document_id: "R_COPILOT_ALL_COMPACTION_PATHS_20260828"
title: "Complete Map of OpenCode CLI Compaction Architecture"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
status: "FINAL"
sources:
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/compaction.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/overflow.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/processor.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/prompt.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/run-state.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/retry.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/summary.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/message-v2.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/tool/truncate.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/provider/transform.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/agent/agent.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/agent/prompt/compaction.txt
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/server/routes/instance/httpapi/handlers/session.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/server/routes/instance/httpapi/server.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/config/config.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/server/routes/instance/httpapi/groups/session.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/effect/app-runtime.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/plugin/github-copilot/copilot.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/effect/runner.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/compaction.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/runner/llm.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/runner/to-llm-message.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/history.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/execution.ts
  - /home/arcana-novai/Doorkeeper/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/execution/local.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/config/compaction.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/config.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/v1/config/config.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/v1/config/migrate.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/core/src/session/runner/index.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/llm/src/provider-error.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/plugin/src/index.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/test/session/compaction.test.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/tui/src/routes/session/index.tsx
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/packages/opencode/src/session/revert.ts
  - /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/opencode/packages/opencode/src/session/session.ts
confidence: "HIGH"
findings: 36
---

# Complete Map of OpenCode CLI Compaction Architecture

> **TL;DR**: This Omega Engine fork ships **two parallel compaction systems** — V1 (active, in `packages/opencode/src/session/`) and V2 (newer Effect-native, in `packages/core/src/session/`). V1 is what TUI/HTTP actually executes today; V2 is wired into the server's Effect layer but the V1 path is still on the request hot path. There are **6 trigger conditions** (2 in V1 preflight/post-turn, 1 manual `/compact`, 1 overflow recovery, 1 prune, 1 hidden retry), **3 compaction strategies** in V1 (summary, prune, replay), **2 in V2** (summary only, no prune), and **2 plugin hooks** (`experimental.session.compacting`, `experimental.compaction.autocontinue`).

---

## 0. The Two-System Reality (Read First)

This is the most important finding. The codebase contains **two compaction systems** that are both wired and compete for control:

| System | Location | Wiring | Currently executes? |
|--------|----------|--------|----------------------|
| **V1** (active legacy) | `packages/opencode/src/session/` | `app-runtime.ts:85` provides `SessionRunState.node`; `run-state.ts` runs `runLoop` in `prompt.ts:1081` | **YES** — invoked by TUI `session.summarize` (`tui/src/routes/session/index.tsx:580`), HTTP `POST /session/:id/summarize` (`server/.../handlers/session.ts:273`), and every prompt run. |
| **V2** (Effect-native future) | `packages/core/src/session/` | `server.ts:301` provides `SessionExecution.node` + `SessionExecutionLocal.node`; `runner/llm.ts:109` instantiates `SessionCompaction.make({...})` | **YES but secondary** — `SessionExecutionLocal.drain` (`execution/local.ts:20`) calls `SessionRunner.run(...)` which owns `runTurnAttempt` that calls `compaction.compactIfNeeded` and `compactAfterOverflow` (`runner/llm.ts:222`, `runner/llm.ts:293`). |

Both layers are composed in the live server (`httpapi/server.ts:295-303`). V1 is the legacy active path used by TUI/HTTP today; V2 sits alongside it. The V1 system is therefore the one whose behavior the user will see when they press `/compact` or hit a context overflow during normal operation, but V2 is the one referenced by `specs/v2/session.md` and the `specs/v2` directory's stated future direction.

### Active hot path (V1)

```
TUI "/compact"  ──► sdk.client.session.summarize()
HTTP POST /session/:id/summarize
                 ▼
   handlers/session.ts:273 (SessionHttpApi.summarize)
                 ▼
   compaction.create()  (opencode/src/session/compaction.ts:559) — inserts User message + Compaction part
                 ▼
   promptSvc.loop()     (handlers/session.ts:291)
                 ▼
   runLoop()  (opencode/src/session/prompt.ts:1081)
                 ▼
   task = tasks.pop()  (prompt.ts:1142) — picks up CompactionPart
                 ▼
   compaction.process() (opencode/src/session/compaction.ts:319)
                 ▼
   processors.create() → processor.process()  (compaction.ts:420-448)
                 ▼
   Events.publish(Compaction.Compacted)        (compaction.ts:554)
                 ▼
   optional synthetic "Continue if you have next steps" user message
                  (compaction.ts:519-547, metadata: { compaction_continue: true })
```

### Active hot path (V2)

```
SessionExecution.resume(sessionID)
   ▼
SessionExecutionLocal.drain
   ▼
SessionRunner.run
   ▼
runTurn → runTurnAttempt  (core/src/session/runner/llm.ts:173)
   ▼
compaction.compactIfNeeded    (runner/llm.ts:222) — preflight
   ▼
llm.stream(request) → provider-error event
   ▼
compaction.compactAfterOverflow  (runner/llm.ts:293) — recovery
   ▼
continueAfterCompaction / continueAfterOverflowCompaction  (runner/llm.ts:223, 295)
```

---

## 1. Complete Trigger Map

There are **six distinct trigger conditions** for compaction in the active V1 system, plus the **V2 runner's two** (one in V2 that mirrors V1's preflight + overflow recovery).

### 1.1 V1 Trigger 1: Preflight overflow check (auto, at loop top)

**File**: `packages/opencode/src/session/prompt.ts:1161-1168`

```typescript
if (
  lastFinished &&
  lastFinished.summary !== true &&
  (yield* compaction.isOverflow({ tokens: lastFinished.tokens, model }))
) {
  yield* compaction.create({ sessionID, agent: lastUser.agent, model: lastUser.model, auto: true })
  continue
}
```

**When**: every iteration of `runLoop` (line 1081) BEFORE the next assistant turn starts, when the **last finished** assistant message's `tokens` exceed the model's usable context. The check is gated by `lastFinished.summary !== true` (so the compaction-agent's own messages don't trigger re-compaction) and by `compaction.isOverflow`.

**`isOverflow` definition** (`session/overflow.ts:22-34`):

```typescript
export function isOverflow(input: {
  cfg: ConfigV1.Info
  tokens: SessionV1.Assistant["tokens"]
  model: Provider.Model
  outputTokenMax?: number
}) {
  if (input.cfg.compaction?.auto === false) return false
  if (input.model.limit.context === 0) return false
  const count =
    input.tokens.total || input.tokens.input + input.tokens.output + input.tokens.cache.read + input.tokens.cache.write
  return count >= usable(input)
}
```

The token count prefers `tokens.total` if present, otherwise sums `input + output + cache.read + cache.write` (cache is treated as input cost). It returns `true` when the count ≥ `usable(...)`.

**`usable(...)`** (`overflow.ts:10-20`):

```typescript
export function usable(input: { cfg: ConfigV1.Info; model: Provider.Model; outputTokenMax?: number }) {
  const context = input.model.limit.context
  if (context === 0) return 0
  const reserved =
    input.cfg.compaction?.reserved ??
    Math.min(COMPACTION_BUFFER, ProviderTransform.maxOutputTokens(input.model, input.outputTokenMax))
  return input.model.limit.input
    ? Math.max(0, input.model.limit.input - reserved)
    : Math.max(0, context - ProviderTransform.maxOutputTokens(input.model, input.outputTokenMax))
}
```

`COMPACTION_BUFFER` = 20,000 (`overflow.ts:8`); `maxOutputTokens` is `min(model.limit.output, OUTPUT_TOKEN_MAX=32_000)` (`provider/transform.ts:1418-1420`).

**Effect**: when this fires, `compaction.create(...)` writes a new User message with a `CompactionPart` (`{ type: "compaction", auto: true, overflow: false }`), then the loop continues to the next iteration, where `tasks.pop()` returns the compaction task and `compaction.process(...)` is called.

### 1.2 V1 Trigger 2: Post-turn overflow check (auto, on step-finish)

**File**: `packages/opencode/src/session/processor.ts:477-482`

```typescript
if (
  !ctx.assistantMessage.summary &&
  isOverflow({ cfg: yield* config.get(), tokens: usage.tokens, model: ctx.model })
) {
  ctx.needsCompaction = true
}
```

**When**: inside `handleEvent` for `step-finish` (line 435), the same `isOverflow` check runs against the just-finished step's `usage.tokens`. If true, it sets `ctx.needsCompaction = true`.

**Then** (`processor.ts:642-646`):

```typescript
yield* stream.pipe(
  Stream.tap((event) => handleEvent(event)),
  Stream.takeUntil(() => ctx.needsCompaction),
  Stream.runDrain,
)
```

The stream is **aborted as soon as `needsCompaction` becomes true**. After the stream exits, `process` returns `"compact"` (`processor.ts:679`). Back in `runLoop` (`prompt.ts:1319-1328`):

```typescript
if (result === "stop") return "break" as const
if (result === "compact") {
  yield* compaction.create({
    sessionID,
    agent: lastUser.agent,
    model: lastUser.model,
    auto: true,
    overflow: !handle.message.finish,  // overflow=true if stream never finished
  })
}
```

The `overflow` flag is set when the assistant turn didn't `finish` at all (i.e. the stream was cut off mid-flight because `needsCompaction` fired) — this matters because the post-compaction flow uses it to **replay** the user message without media attachments (`compaction.ts:340-356`).

### 1.3 V1 Trigger 3: ContextOverflowError recovery (error path)

**File**: `packages/opencode/src/session/processor.ts:599-625`

```typescript
const halt = Effect.fn("SessionProcessor.halt")(function* (e: unknown) {
  ...
  const error = parse(e)
  if (SessionV1.ContextOverflowError.isInstance(error)) {
    if ((yield* config.get()).compaction?.auto === false && !ctx.assistantMessage.summary) {
      ctx.assistantMessage.error = error
      ctx.assistantMessage.finish = "error"
      yield* events.publish(Session.Event.Error, { sessionID: ctx.sessionID, error })
      yield* status.set(ctx.sessionID, { type: "idle" })
      return
    }
    ctx.needsCompaction = true
    yield* events.publish(Session.Event.Error, { sessionID: ctx.sessionID, error })
    return
  }
  ...
})
```

**When**: when a stream raises a `ContextOverflowError` (parsed by `MessageV2.fromError`, see `error.ts` and the V1 schema at `core/src/v1/session.ts:64`). The error pattern matcher is **`packages/llm/src/provider-error.ts:4-32`** — a 28-pattern regex set covering the common provider phrasings (`"prompt is too long"`, `"request_too_large"`, `"context_length_exceeded"`, `"too many tokens"`, etc.) with explicit exclusion of throttling/rate-limit messages (line 34).

**Path**: `halt` is called via `Effect.catch(halt)` in `processor.ts:675`. After `halt` returns, `process` resumes, sees `ctx.needsCompaction === true`, and returns `"compact"` (line 679) — same downstream as Trigger 2.

**Auto-disabled branch**: when `compaction.auto === false` AND the message is not itself a compaction summary, the error is surfaced to the user via `Session.Event.Error` and the session goes idle — the user must invoke `/compact` themselves or send a new prompt. The non-compaction `summary` assistant messages are excluded from auto-disable because the compaction subagent's own output is the one that just produced a `ContextOverflowError`.

**Disambiguation**: `SessionRetry.retryable` (`session/retry.ts:85-87`) explicitly returns `undefined` for `ContextOverflowError` so it is **not** retried — it always falls into `halt` → compaction.

### 1.4 V1 Trigger 4: Manual `/compact` slash command (user-initiated)

**TUI entry**: `packages/tui/src/routes/session/index.tsx:562-587`

```typescript
{
  title: "Compact session",
  value: "session.compact",
  category: "Session",
  slash: {
    name: "compact",
    aliases: ["summarize"],
  },
  run: () => {
    const selectedModel = local.model.current()
    if (!selectedModel) { ...return; }
    void sdk.client.session.summarize({
      sessionID: route.sessionID,
      modelID: selectedModel.modelID,
      providerID: selectedModel.providerID,
    })
    dialog.clear()
  },
},
```

**API entry**: `packages/opencode/src/server/routes/instance/httpapi/handlers/session.ts:273-293`

```typescript
const summarize = Effect.fn("SessionHttpApi.summarize")(function* (ctx: {
  params: { sessionID: SessionID }
  payload: typeof SummarizePayload.Type
}) {
  yield* revertSvc.cleanup(yield* requireSession(ctx.params.sessionID))
  const messages = yield* SessionError.mapStorageNotFound(session.messages({ sessionID: ctx.params.sessionID }))
  const defaultAgent = yield* agentSvc.defaultAgent()
  const currentAgent = messages.findLast((message) => message.info.role === "user")?.info.agent ?? defaultAgent

  yield* compactSvc.create({
    sessionID: ctx.params.sessionID,
    agent: currentAgent,
    model: { providerID: ctx.payload.providerID, modelID: ctx.payload.modelID },
    auto: ctx.payload.auto ?? false,
  })
  yield* promptSvc.loop({ sessionID: ctx.params.sessionID })
  return true
})
```

**Effect**: a CompactionPart is created with `auto: false` (when payload.auto is unset), then `promptSvc.loop` is invoked. The next `runLoop` iteration picks the compaction task off the `tasks` stack (`prompt.ts:1142-1158`) and runs `compaction.process(...)` — the **same** `compaction.process` path as auto-compaction, just with `auto: false` so the **synthetic "Continue" prompt is not generated** (`compaction.ts:468-549` checks `if (result === "continue" && input.auto)`).

**Also wired** from `app/src/utils/server-compat.ts:277` for the desktop app's compat layer.

### 1.5 V1 Trigger 5: Background prune (post-loop, async)

**File**: `packages/opencode/src/session/prompt.ts:1338`

```typescript
yield* compaction.prune({ sessionID }).pipe(Effect.ignore, Effect.forkIn(scope))
```

**When**: at the end of every successful `runLoop` (after the loop exits normally), prune is **forked into the scope** and runs asynchronously. It is therefore a "best-effort, post-session" trigger.

**Prune definition** (`session/compaction.ts:273-317`):

```typescript
const prune = Effect.fn("SessionCompaction.prune")(function* (input: { sessionID: SessionID }) {
  const cfg = yield* config.get()
  if (!cfg.compaction?.prune) return
  yield* Effect.logInfo("pruning")
  ...
})
```

It is **opt-in** via `compaction.prune = true` (default `false`, see V1 schema at `core/src/v1/config/config.ts:154-156`). The implementation walks backward through messages, skipping the first user turn, breaks on the first prior compaction boundary, and marks `part.state.time.compacted = Date.now()` on tool outputs whose bytes would push total over `PRUNE_PROTECT` (40,000 tokens). Only fires when `pruned > PRUNE_MINIMUM` (20,000 tokens). Protected tool names: `["skill"]` (`compaction.ts:31`).

### 1.6 V1 Trigger 6: Compaction overflow replay (sub-trigger of T2/T3)

**File**: `packages/opencode/src/session/compaction.ts:340-356`

```typescript
if (input.overflow) {
  const idx = input.messages.findIndex((m) => m.info.id === input.parentID)
  for (let i = idx - 1; i >= 0; i--) {
    const msg = input.messages[i]
    if (msg.info.role === "user" && !msg.parts.some((p) => p.type === "compaction")) {
      replay = { info: msg.info, parts: msg.parts }
      messages = input.messages.slice(0, i)
      break
    }
  }
  const hasContent =
    replay && messages.some((m) => m.info.role === "user" && !m.parts.some((p) => p.type === "compaction"))
  if (!hasContent) {
    replay = undefined
    messages = input.messages
  }
}
```

**When**: `compaction.process` is called with `overflow: true` (set by `prompt.ts:1326` when `result === "compact" && !handle.message.finish`). The previous user message becomes the `replay` object and all messages before it are used as the head — and **media attachments are stripped** from the replayed user message (`compaction.ts:485-486`):

```typescript
const replayPart =
  part.type === "file" && MessageV2.isMedia(part.mime)
    ? { type: "text" as const, text: `[Attached ${part.mime}: ${part.filename ?? "file"}]` }
    : part
```

This is the only path that produces a media-stripped "replay" user message in the new conversation.

### 1.7 V2 Trigger A: `compactIfNeeded` (preflight, request-construction-time)

**File**: `packages/core/src/session/runner/llm.ts:222-223`

```typescript
if (yield* compaction.compactIfNeeded({ sessionID: session.id, entries, model, request }))
  return yield* Effect.die(continueAfterCompaction(currentStep))
```

**When**: every provider turn starts. The V2 check (`core/src/session/compaction.ts:232-243`):

```typescript
const compactIfNeeded = Effect.fn("SessionCompaction.compactIfNeeded")(function* (input: Input) {
  if (!config.auto) return false
  const context = input.model.route.defaults.limits?.context
  if (context === undefined || context <= 0) return false
  const output = input.request.generation?.maxTokens ?? input.model.route.defaults.limits?.output ?? 0
  if (
    estimate({ system: input.request.system, messages: input.request.messages, tools: input.request.tools }) <=
    context - Math.max(output, config.buffer)
  )
    return false
  return yield* compactAfterOverflow(input)
})
```

The estimate is a `Token.estimate(JSON.stringify(...))` on the **assembled request** (system + messages + tools), not on a `tokens` counter. Threshold is `context - max(output, config.buffer)` where `config.buffer` defaults to 20,000 (`compaction.ts:12`). `config.auto` defaults to `true` (`compaction.ts:133`).

If it fires, it returns `true` and the runner `Effect.die`s with a `TurnTransitionError` of `_tag: "ContinueAfterCompaction"`. The outer `runTurn` catches the defect and re-enters `runTurnAttempt` with `step = defect.transition.step` (`runner/llm.ts:382-386`).

### 1.8 V2 Trigger B: `compactAfterOverflow` (provider-error recovery)

**File**: `packages/core/src/session/runner/llm.ts:289-295`

```typescript
if (
  recoverOverflow &&
  !publisher.hasAssistantStarted() &&
  isContextOverflowFailure(overflowFailure ?? failure) &&
  (yield* restore(recoverOverflow({ sessionID: session.id, entries, model, request })))
)
  return yield* Effect.die(continueAfterOverflowCompaction(currentStep))
```

**When**: after the `llm.stream` exits with a `ProviderErrorEvent` classified as `"context-overflow"` (regex-based, see `packages/llm/src/provider-error.ts:40-42`), **and** the assistant message has not yet started publishing. The check uses the shared `isContextOverflowFailure` helper from `@opencode-ai/llm`. If compaction succeeds, the runner `Effect.die`s with `_tag: "ContinueAfterOverflowCompaction"` and the outer `runAfterOverflowCompaction` retries **once** with `recoverOverflow` removed (line 362-374) — a post-compaction attempt cannot itself trigger another overflow recovery.

### Trigger Matrix

| # | Trigger | File:Line | Auto/Manual | Strategy | Guards |
|---|---------|-----------|-------------|----------|--------|
| T1 | V1 preflight | `prompt.ts:1161-1168` | Auto | Create + process | `compaction.auto !== false`, `model.limit.context !== 0`, `lastFinished.summary !== true` |
| T2 | V1 post-turn | `processor.ts:477-482` | Auto | Create + process (overflow=true) | same as T1 + `!ctx.assistantMessage.summary` |
| T3 | V1 ContextOverflowError | `processor.ts:607-617` | Auto/Manual (config-dependent) | Create + process (overflow=true) | `compaction.auto !== false` OR `ctx.assistantMessage.summary` |
| T4 | Manual `/compact` | `tui/.../session/index.tsx:580` + `handlers/session.ts:273-293` | Manual | Create + process (auto=false) | none |
| T5 | Prune | `prompt.ts:1338` | Auto (background) | Prune (no summary) | `cfg.compaction?.prune === true` |
| T6 | Overflow replay | `compaction.ts:340-356` | Sub-trigger | Strip media + re-replay | `input.overflow === true` |
| T7 | V2 preflight | `runner/llm.ts:222` | Auto | Compact + retry turn | `config.auto`, `context > 0`, estimated > threshold |
| T8 | V2 overflow recovery | `runner/llm.ts:289-295` | Auto | Compact + retry turn (once) | `!hasAssistantStarted()`, `isContextOverflowFailure(...)` |

---

## 2. Complete Strategy Map

V1 has **three** strategies: **Summarize** (the default), **Prune** (opt-in), and **Replay** (sub-trigger of overflow). V2 has **one**: **Summarize**.

### 2.1 Strategy: Summarize (V1, default)

**File**: `packages/opencode/src/session/compaction.ts:319-557` (`processCompaction`)

**Algorithm**:
1. **Find parent user message** (must exist; throws otherwise, line 327-329).
2. **If overflow**, locate the **replay** user message (the one before the compaction parent that is itself not a compaction) and use it as the replay target; strip media (`compaction.ts:485-486`).
3. **Resolve the compaction subagent** (`agents.get("compaction")`, line 358). Defined in `agent/agent.ts:219-233`:
   ```typescript
   compaction: {
     name: "compaction",
     mode: "primary",
     native: true,
     hidden: true,
     prompt: PROMPT_COMPACTION,
     permission: Permission.merge(
       defaults,
       Permission.fromConfig({ "*": "deny" }),
       user,
     ),
     options: {},
   }
   ```
   It has `mode: "primary"`, `hidden: true` (not shown to user), and `permission: { "*": "deny" }` (no tools allowed during summary generation).
4. **Select tail via `SessionCompaction.select(...)`** (`compaction.ts:223-269`):
   - If `cfg.compaction?.tail_turns <= 0` returns the full message list with `tail_start_id: undefined` (no retention).
   - Otherwise computes a `budget = preserveRecentBudget({ cfg, model })` (`compaction.ts:115-120`):
     ```typescript
     function preserveRecentBudget(input: { cfg: ConfigV1.Info; model: Provider.Model }) {
       return (
         input.cfg.compaction?.preserve_recent_tokens ??
         Math.min(MAX_PRESERVE_RECENT_TOKENS, Math.max(MIN_PRESERVE_RECENT_TOKENS, Math.floor(usable(input) * 0.25)))
       )
     }
     ```
     `MIN_PRESERVE_RECENT_TOKENS = 2_000`, `MAX_PRESERVE_RECENT_TOKENS = 15_000`. Default = `clamp(usable * 0.25, 2k, 15k)`.
   - Walks recent user-turns backward, accumulating estimated tokens (via `Token.estimate(JSON.stringify(MessageV2.toModelMessagesEffect(...)))`); stops when the budget is full.
   - If a turn doesn't fit, attempts to split it (`splitTurn`, line 140-163) by walking forward through the turn's messages, finding the first slice whose JSON-stringified size fits in the remaining budget. Falls back to dropping the turn if no slice fits (logged `"tail fallback"`).
   - Returns `{ head: messages[0..keep.start], tail_start_id: keep.id }`.
5. **Filter out prior completed compactions** via `completedCompactions(history)` (`compaction.ts:97-113`) so we don't re-summarize what's already summarized. The previous summary is captured as `previousSummary` (line 366) and prepended to the new prompt.
6. **Plugin hook** — `experimental.session.compacting` (line 373-377):
   ```typescript
   const compacting = yield* plugin.trigger(
     "experimental.session.compacting",
     { sessionID: input.sessionID },
     { context: [], prompt: undefined },
   )
   ```
   The plugin may return `{ context: [...strings], prompt: undefined|"<full-prompt>" }`. If `prompt` is set, the default build is **replaced entirely**. Otherwise `context` strings are appended after the default build.
7. **Default prompt builder** — `buildPrompt` from `core/src/session/compaction.ts:160-174` (imported as `buildPrompt` at `compaction.ts:23`). On first compaction it returns `[conversation, "Create a new anchored summary...", SUMMARY_TEMPLATE]`. On subsequent ones it returns `[conversation, <prior-summary>, SUMMARY_UPDATE_INSTRUCTIONS, SUMMARY_TEMPLATE]`. The template is a 7-section Markdown skeleton (Objective, Important Details, Work State, Active/Blocked, Next Move, Relevant Files).
8. **Chat transform** — `plugin.trigger("experimental.chat.messages.transform", ...)` runs on the cloned head (line 379) so plugins can also rewrite the to-be-summarized messages.
9. **Serialize** — `serialize(message)` (`compaction.ts:54-85`) flattens the head to a single string per message: user → `[User]: <text>` + `[Attached <mime>: <name>]`; assistant → `[Assistant]: <text>` + `[Assistant reasoning]: <text>` + `[Assistant tool call]: <name>(input)` + `[Tool result]: <output truncated to 2000 chars or "[Old tool result content cleared]">` (line 30 = `TOOL_OUTPUT_MAX_CHARS`); errors → `[Tool error]: <error>`.
10. **Create the assistant message** with `mode: "compaction"`, `agent: "compaction"`, `summary: true` (`compaction.ts:393-419`) and the compaction subagent's model (or fallback to the user message's model, line 359-361).
11. **Run the compaction agent's stream** via `processor.process(...)` (line 425-448) with the built `nextPrompt` and the serialized conversation appended. The result is `"compact" | "stop" | "continue"`.
12. **If `"compact"`** (the compaction itself overflowed), set `processor.message.error = ContextOverflowError` and **stop** (line 450-458). The user sees `"Conversation history too large to compact - exceeds model context limit"`.
13. **Otherwise** update the `CompactionPart.tail_start_id` to the new `selected.tail_start_id` (line 461-466), then if `input.auto`, optionally emit a **synthetic "Continue if you have next steps"** user message (line 468-549). For overflow triggers, a different preamble is used (line 528-530) that explicitly tells the model media was removed.
14. **Plugin hook** — `experimental.compaction.autocontinue` (line 499-518): runs only when `replay === undefined` (i.e. not an overflow), receives `{ sessionID, agent, model, provider, message, overflow }`, and can return `{ enabled: false }` to skip the synthetic continue.
15. **Publish event** `Event.Compacted` (line 554) for downstream subscribers.

### 2.2 Strategy: Prune (V1, opt-in)

**File**: `packages/opencode/src/session/compaction.ts:273-317`

**Algorithm**:
- Constants (`compaction.ts:28-31`): `PRUNE_MINIMUM = 20_000`, `PRUNE_PROTECT = 40_000`, `TOOL_OUTPUT_MAX_CHARS = 2_000`, `PRUNE_PROTECTED_TOOLS = ["skill"]`.
- Walks messages backward (`msgs.length - 1 → 0`).
- Counts `turns++` for each user message; **skips the first 1 turn** (`if (turns < 2) continue`, line 291).
- Stops if it hits an assistant message with `summary: true` (a previous compaction boundary) — `break loop` (line 292).
- For each `tool` part in reverse:
  - Skip if `status !== "completed"` (line 296).
  - Skip if `PRUNE_PROTECTED_TOOLS.includes(part.tool)` (line 297) — i.e. the `skill` tool is never pruned.
  - Stop if `part.state.time.compacted` is already set (line 298) — the part was already pruned.
  - Add `Token.estimate(part.state.output)` to `total`; continue while `total <= PRUNE_PROTECT` (40k) (line 301).
  - Once `total > PRUNE_PROTECT`, push the part onto `toPrune` and add the estimate to `pruned`.
- **Only commit** if `pruned > PRUNE_MINIMUM` (20k) (line 308). For each part in `toPrune`: set `part.state.time.compacted = Date.now()` and `session.updatePart(part)`.
- **Net effect**: tool outputs older than the last 40k tokens (and not in the most recent turn) get their `time.compacted` flag set, and `serialize(...)` checks this flag (`compaction.ts:76-78`) to render them as `"[Old tool result content cleared]"` in the next compaction summary. The underlying output is **not deleted** — only its display is replaced.

**Note**: prune is **never invoked in the V2 core path**. The `core/src/session/compaction.ts` has no `prune` strategy.

### 2.3 Strategy: Replay (V1, sub-trigger of overflow)

**File**: `packages/opencode/src/session/compaction.ts:340-356, 468-495`

When `input.overflow === true`, the previous non-compaction user message is **re-emitted** as a fresh user message (with new IDs) and **media file parts are converted to placeholder text**:

```typescript
const replayPart =
  part.type === "file" && MessageV2.isMedia(part.mime)
    ? { type: "text" as const, text: `[Attached ${part.mime}: ${part.filename ?? "file"}]` }
    : part
```

The synthetic "Continue" prompt's text changes too (`compaction.ts:528-530`):

```typescript
input.overflow
  ? "The previous request exceeded the provider's size limit due to large media attachments. The conversation was compacted and media files were removed from context. If the user was asking about attached images or files, explain that the attachments were too large to process and suggest they try again with smaller or fewer files.\n\n"
  : ""
```

This is the only path that produces a media-stripped replay.

### 2.4 Strategy: V2 Summarize (V2 core)

**File**: `packages/core/src/session/compaction.ts:176-247`

**Algorithm**:
1. **`compactIfNeeded(...)`**: preflight estimate; if `estimate(system+messages+tools) > context - max(output, config.buffer)`, call `compactAfterOverflow(...)`. Skipped if `config.auto === false` or `context <= 0`.
2. **`compactAfterOverflow(...)`**:
   - **Re-check feasibility** (line 179-184): if `context <= 0` or the selected head is empty AND no prior compaction, abort.
   - **Select head + recent** via `select(entries, config.tokens)` (line 137-158): walks messages backward from the end, accumulating `Token.estimate(message)` until exceeding `config.tokens` (default 8,000, see `DEFAULT_KEEP_TOKENS` at `compaction.ts:13`). Returns `{ head: pre-split joined, recent: post-split joined }`.
   - **Build the prompt** via `buildPrompt` (line 160-174) with `previousSummary` (from prior compaction) + `[selected.head, prior recent]`.
   - **Re-check prompt size** (line 190): `Token.estimate(summaryPrompt) > context - summaryOutput` → abort. `summaryOutput = min(output || 4096, 4096)` (`SUMMARY_OUTPUT_TOKENS = 4_096`).
   - **Stream a `llm.stream(...)` call** with `tools: []` and `maxTokens: summaryOutput`. Collect `text-delta` events; abort on `provider-error` (line 213).
   - **On failure** (line 218-221): `Effect.catchTag("LLM.Error", () => Effect.succeed(false))` — if the compaction subagent's own LLM call fails, return `false` (no compaction, runner will likely fail again).
   - **Publish** `SessionEvent.Compaction.Started` then `Ended` (line 192, 222) with the `text: summary, recent: selected.recent` payload.
3. **After compaction succeeds**, the V2 runner `Effect.die`s with `TurnTransitionError{ _tag: "ContinueAfterCompaction" }` and the outer loop restarts `runTurnAttempt` with `step = defect.transition.step`. History is reloaded via `SessionHistory.entriesForRunner(db, session.id, system.baselineSeq)` (`history.ts:90-99`) which uses `latestCompaction` (`history.ts:13-22`) to find the compaction row and only return rows with `seq >= compaction.seq` (so the head is dropped, the recent is kept).

**Critical difference from V1**: V2's **"recent" is computed and stored on the compaction row** as a single string (`SessionMessage.Compaction.recent`, see `core/src/session/compaction.ts:228`). The V2 `to-llm-message.ts:153-167` renders a `<recent-context>` block with this stored recent plus a system-update block with the summary text. V1, by contrast, **mutates the CompactionPart in place** (`compaction.ts:461-466`) and relies on `filterCompacted` (`message-v2.ts:521-572`) to **reorder** `[compaction-user, summary, ...tail..., continue-user]` for model consumption.

### 2.5 No other strategies

There is **no truncation strategy in either system**. The `tool/truncate.ts` module (line 1-156) handles **tool output truncation to disk** — a separate, unrelated mechanism that runs when a tool's output exceeds `MAX_LINES=2000` or `MAX_BYTES=50*1024` (lines 14-15, defaults overridable via `tool_output` config). When triggered, the full output is written to `~/.local/share/opencode/tool-output/tool_<id>` and the model receives a preview. The retained preview is `<= 2000` chars of head by default. This is **not** a compaction strategy — it is per-tool output management and never mutates the conversation.

---

## 3. V1 vs V2 Comparison (Side-by-Side)

### 3.1 Schema

| Field | V1 (`core/src/v1/config/config.ts:149-168`) | V2 (`core/src/config/compaction.ts:6-15`) |
|-------|--------------------------------------------|------------------------------------------|
| `auto` | optional bool (default `true`) | optional bool (default `true` via `settings()` reduce) |
| `prune` | optional bool (default `false`) | **absent** |
| `tail_turns` | optional `NonNegativeInt` (cap on user turns to keep verbatim) | **absent** (V2 uses token budget only) |
| `preserve_recent_tokens` | optional `NonNegativeInt` (explicit cap on tokens kept) | **renamed to `keep.tokens`** |
| `reserved` | optional `NonNegativeInt` (buffer; falls back to `min(20_000, maxOutput)`) | **renamed to `buffer`** (default 20_000) |
| | | `Keep` class: `{ tokens?: number }` |

### 3.2 Migration (V1 → V2)

**File**: `packages/core/src/v1/config/migrate.ts:54-61`

```typescript
compaction: info.compaction && {
  auto: info.compaction.auto,
  prune: info.compaction.prune,
  keep: {
    tokens: info.compaction.preserve_recent_tokens,
  },
  buffer: info.compaction.reserved,
},
```

The V1 `tail_turns` is **dropped** in the migration. The V2 system has no equivalent concept — it always uses the token budget alone.

### 3.3 Detection

**File**: `packages/core/src/v1/config/migrate.ts:30-33`

```typescript
export function isV1(input: unknown) {
  if (typeof input !== "object" || input === null || Array.isArray(input)) return false
  return Object.keys(input).some((key) => keys.has(key))
}
```

A config is V1 if any of the listed keys (`logLevel`, `server`, `command`, `reference`, `snapshot`, `plugin`, `autoshare`, `disabled_providers`, `enabled_providers`, `small_model`, `mode`, `agent`, `provider`, `permission`, `tools`, `attachment`, `layout`) appear. V1 configs are auto-migrated at `packages/core/src/config.ts:155-159`.

### 3.4 Algorithm differences

| Concern | V1 | V2 |
|---------|----|----|
| **Trigger count** | 6 paths (preflight, post-turn, error, manual, prune, replay) | 2 paths (preflight, overflow) |
| **Overflow detection** | counter on assistant `tokens` (`total \|\| input+output+cache.read+cache.write`) | estimate of assembled request (`Token.estimate(JSON.stringify({system, messages, tools}))`) |
| **Buffer logic** | `usable = limit.input - reserved`, where `reserved = min(20_000, maxOutput)` (or `cfg.compaction.reserved`) | `threshold = context - max(output, config.buffer)` (default buffer 20,000) |
| **Recent budget** | `clamp(usable * 0.25, 2_000, 15_000)` (or `cfg.compaction.preserve_recent_tokens`) | `config.tokens` (default 8,000) |
| **Turn cap** | `cfg.compaction.tail_turns` (number of recent user-turns to consider) | none — always token-budget-driven |
| **Split mid-turn** | yes (`splitTurn`, `compaction.ts:140-163`) walks messages inside a turn | yes, but only at message granularity (`select` line 137-158 splits before/after messages, not mid-message) |
| **Plugin hook before summary** | `experimental.session.compacting` (may replace prompt) | **none** (V2 has no plugin hook) |
| **Plugin hook after summary** | `experimental.compaction.autocontinue` (may skip synthetic continue) | **none** |
| **Plugin hook for messages** | `experimental.chat.messages.transform` (rewrites head) | **none** |
| **Subagent model resolution** | `agents.get("compaction")` → its model; fallback to user msg's model | **no named subagent**; uses the running session's model |
| **Subagent name** | `"compaction"`, `mode: "primary"`, `hidden: true` | n/a |
| **Subagent prompt** | `PROMPT_COMPACTION` (`agent/prompt/compaction.txt`): "You are a context summarization agent..." + injected `buildPrompt(...)` template | inline `buildPrompt(...)` from `core/src/session/compaction.ts:160-174` (no separate system prompt; template baked into the user prompt) |
| **Subagent tools** | `Permission.merge(defaults, { "*": "deny" }, user)` (all denied) | `tools: []` in the `llm.stream(...)` call |
| **Subagent max tokens** | inherits from the selected model | `maxTokens: summaryOutput = min(output \|\| 4096, 4096)` |
| **Output tokens** | full model output (no hard cap) | capped at 4,096 |
| **Retry on compaction failure** | on `ContextOverflowError` from the compaction subagent itself, **stop** with `error` and `"Conversation history too large to compact"` | on `LLM.Error` from `llm.stream`, return `false` (no retry; runner will likely fail again) |
| **Synthetic "continue" prompt** | yes, marked `synthetic: true, metadata: { compaction_continue: true }` (line 540) | **none** — V2's compaction just publishes the event and the runner loops back |
| **Overflow recovery** | re-emit user msg with media stripped + a different synthetic preamble | just retry the turn; recent is already retained |
| **Compaction row schema** | `CompactionPart { type: "compaction", auto, overflow, tail_start_id? }` (in-message) | `SessionMessage.Compaction { type: "compaction", summary, recent, ... }` (a separate `compaction` message type with its own seq) |
| **Storage filter for model** | `filterCompacted(...)` (`message-v2.ts:521-572`) reorders `[compaction-user, summary-assistant, ...tail, ...continue]` | `SessionHistory.entriesForRunner(...)` (`history.ts:90-99`) returns only rows with `seq >= latestCompaction.seq` |
| **Tool-output clearing (prune)** | yes — sets `part.state.time.compacted`, surfaced as `"[Old tool result content cleared]"` | **no** — V2 has no prune |
| **Multi-composition flow** | continues running (auto) or stops (manual) and emits `Event.Compacted` | `compactIfNeeded` + `compactAfterOverflow` both call `compactAfterOverflow`; result `true` causes runner to retry the turn |
| **Summary template** | same 7-section template (via `buildPrompt` from `core/src/session/compaction.ts`) | same 7-section template (via same `buildPrompt` from same file) |
| **Re-summarization on prior** | yes — `completedCompactions` + `previousSummary` + `SUMMARY_UPDATE_INSTRUCTIONS` | yes — same `buildPrompt` with `previousSummary` and `SUMMARY_UPDATE_INSTRUCTIONS` |
| **Estimated token count to trigger** | `tokens.total \|\| input+output+cache.read+cache.write >= usable` | `Token.estimate(JSON.stringify(request)) > context - max(output, buffer)` |
| **API to invoke** | `POST /session/:id/summarize` (handlers/session.ts:273) — writes a CompactionPart | n/a (internal-only) |
| **TUI slash command** | `/compact` (alias `/summarize`) | n/a |

### 3.5 Which is active

V1 is the **user-facing** path:
- TUI `/compact` → V1.
- HTTP `POST /session/:id/summarize` → V1.
- TUI's `session.compact` slash command is **only** the V1 endpoint.

V2 is the **internal** path:
- Triggered from `SessionExecutionLocal.drain` (when the server runs in V2 mode).
- The `core/src/session/runner/llm.ts:108` `db` is the V2 `Database` (Drizzle/SQLite via `core/src/database`), not the V1 message store.
- No TUI/HTTP entry point; only reached through V2's `sessions.prompt` API.

Both are wired in the live server (`httpapi/server.ts:295-303`). For a normal user interacting with TUI today, **V1 is what runs**.

---

## 4. Provider Behaviors

### 4.1 Token counting

**V1** uses the **`Assistant.tokens` counter** returned by the provider's `step-finish` event. The provider SDK writes into:

```typescript
ctx.assistantMessage.tokens = usage.tokens
```

(`processor.ts:445`). Then `isOverflow` reads `tokens.total` first, falling back to `input + output + cache.read + cache.write` (`overflow.ts:31-32`).

**V2** uses a **preflight `Token.estimate`** on the full assembled request (`core/src/session/compaction.ts:83, 238`):

```typescript
const estimate = (value: unknown) => Token.estimate(JSON.stringify(value))
```

V2 never reads a `tokens` counter — it estimates the would-be request.

### 4.2 `maxOutputTokens` (V1 only)

**File**: `packages/opencode/src/provider/transform.ts:18, 1418-1420`

```typescript
export const OUTPUT_TOKEN_MAX = 32_000
export function maxOutputTokens(model: Provider.Model, outputTokenMax = OUTPUT_TOKEN_MAX): number {
  return Math.min(model.limit.output, outputTokenMax) || outputTokenMax
}
```

Used in `overflow.ts:16, 19` to subtract from `context` when computing `usable`. Provider-specific `model.limit.output` is the per-model max (from the model catalog). 32k is a hard ceiling applied across all providers.

### 4.3 Per-provider flows

There is **no provider-specific compaction code path**. Compaction runs through the LLM SDK on the **same model** as the active session (V1: `agents.get("compaction").model` with fallback to user model; V2: same `model` as the running turn). The only provider-specific considerations are:

- **Model selection** — V1's compaction subagent respects a per-agent `model` override defined in `agent/agent.ts:219-233`. If unset, it falls back to the user message's model.
- **`promptCacheKey`** (V2 only) — `runner/llm.ts:204, 214`:
  ```typescript
  const promptCacheKey = /^ses_[0-9a-f]{64}$/.test(session.id) ? session.id.slice(4) : session.id
  ...
  providerOptions: { openai: { promptCacheKey } },
  ```
  V2 passes a deterministic `promptCacheKey` derived from the session ID to OpenAI-compatible providers so cache hits persist across turns.
- **`x-session-affinity` header** (V2 only) — `runner/llm.ts:206-213`:
  ```typescript
  http: {
    headers: {
      "x-session-affinity": session.id,
      "X-Session-Id": session.id,
      ...(session.parentID ? { "x-parent-session-id": session.parentID } : {}),
    },
  },
  ```
  V2 tags every request with the session/parent IDs so providers with session-aware routing can keep state.
- **GitHub Copilot handling of `compaction_continue`** — `packages/opencode/src/plugin/github-copilot/copilot.ts:391`:
  ```typescript
  (part.type === "text" && part.synthetic && part.metadata?.compaction_continue === true),
  ```
  The Copilot plugin checks for the V1 marker so it can distinguish auto-compaction continuations from user-authored post-compaction prompts. This is **not** a documented contract — the comment at `compaction.ts:537-539` explicitly says so: "Internal marker for auto-compaction followups so provider plugins can distinguish them from manual post-compaction user prompts. This is not a stable plugin contract and may change or disappear."

### 4.4 Cache behavior

- **V1** uses `cache.read` and `cache.write` in its token count (`overflow.ts:32`).
- **V2** does not use cache metrics in its estimate — it just estimates `Token.estimate(JSON.stringify(request))`.

### 4.5 The `compaction_continue` marker

V1 attaches `{ synthetic: true, metadata: { compaction_continue: true } }` to the synthetic "Continue" user message (`compaction.ts:540`). No other system uses this marker — only the GitHub Copilot plugin reads it. **Not** part of the stable plugin contract.

---

## 5. Plugin Hooks

### 5.1 `experimental.session.compacting`

**File**: `packages/plugin/src/index.ts:298-308`

```typescript
/**
 * Called before session compaction starts. Allows plugins to customize
 * the compaction prompt.
 *
 * - `context`: Additional context strings appended to the default prompt
 * - `prompt`: If set, replaces the default compaction prompt entirely
 */
"experimental.session.compacting"?: (
  input: { sessionID: string },
  output: { context: string[]; prompt?: string },
) => Promise<void>
```

**Trigger site**: `packages/opencode/src/session/compaction.ts:373-377`

```typescript
const compacting = yield* plugin.trigger(
  "experimental.session.compacting",
  { sessionID: input.sessionID },
  { context: [], prompt: undefined },
)
```

**Effect**:
- If `compacting.prompt` is set, it **replaces the default `buildPrompt(...)` output entirely**. The serialized `conversation` is then appended to the compaction message as `"The following is the conversation history:\n\n<conversation>"` (line 439).
- Otherwise, `compacting.context` is appended to the default prompt.
- Runs **before** the compaction subagent is invoked.

**Status**: V1 only. The V2 core path has no equivalent.

### 5.2 `experimental.compaction.autocontinue`

**File**: `packages/plugin/src/index.ts:309-326`

```typescript
/**
 * Called after compaction succeeds and before a synthetic user
 * auto-continue message is added.
 *
 * - `enabled`: Defaults to `true`. Set to `false` to skip the synthetic
 *   user "continue" turn.
 */
"experimental.compaction.autocontinue"?: (
  input: {
    sessionID: string
    agent: string
    model: Model
    provider: ProviderContext
    message: UserMessage
    overflow: boolean
  },
  output: { enabled: boolean },
) => Promise<void>
```

**Trigger site**: `packages/opencode/src/session/compaction.ts:499-518`

```typescript
yield* plugin.trigger(
  "experimental.compaction.autocontinue",
  {
    sessionID: input.sessionID,
    agent: userMessage.agent,
    model: yield* provider.getModel(...).pipe(Effect.orDie),
    provider: { source: info.source, info, options: info.options },
    message: userMessage,
    overflow: input.overflow === true,
  },
  { enabled: true },
)
```

**Effect**:
- Only runs when `replay === undefined` (i.e. not the overflow replay path) and `result === "continue" && input.auto` (i.e. only on auto-compaction, not manual).
- If the plugin returns `{ enabled: false }`, the synthetic "Continue if you have next steps" message is **not** written.
- Plugins can mutate the `provider.options` in place (it's a mutable object passed by reference).
- Receives the **`overflow` flag** so plugins can distinguish overflow vs preflight compaction.

**Status**: V1 only.

### 5.3 `experimental.chat.messages.transform` (collateral)

**File**: `packages/plugin/src/index.ts:282-290`

```typescript
"experimental.chat.messages.transform"?: (
  input: {},
  output: {
    messages: {
      info: Message
      parts: Part[]
    }[]
  },
) => Promise<void>
```

**Trigger site** (compaction context): `packages/opencode/src/session/compaction.ts:379`

```typescript
const msgs = structuredClone(selected.head)
yield* plugin.trigger("experimental.chat.messages.transform", {}, { messages: msgs })
```

**Effect**: lets plugins rewrite the head of the conversation **before** it gets serialized into the compaction prompt. Also triggered from `prompt.ts:1255` for the regular LLM call. Same hook, two contexts.

**Status**: V1 only.

### 5.4 Plugin hooks V2 does **not** have

The V2 `core/src/session/compaction.ts` calls **no plugin hooks**. There is no `experimental.session.compacting` in V2, no `experimental.compaction.autocontinue` in V2, no `experimental.chat.messages.transform` in V2. The V2 compaction is a closed loop.

### 5.5 `experimental.text.complete`

**File**: `packages/opencode/src/session/processor.ts:516-524` — runs on every text-delta-end, not a compaction hook. Noted for completeness.

### 5.6 `tool/truncate.ts` — when called

**File**: `packages/opencode/src/tool/truncate.ts:1-156`

This is a **per-tool output management** module, not a compaction strategy. It's called by the tool dispatcher when a tool's output exceeds `MAX_LINES=2000` or `MAX_BYTES=50*1024` (lines 14-15, overridable via `tool_output.max_lines` / `tool_output.max_bytes` in config — see `core/src/v1/config/config.ts:140-144`).

When the threshold is exceeded:
- The full text is written to `~/.local/share/opencode/tool-output/tool_<ToolID>` (lines 68-72).
- The model receives a preview (head by default, `direction: "head"` is the default at line 89) plus a hint to inspect the saved file.
- Files older than 7 days (`RETENTION = Duration.days(7)`, line 12) are cleaned up by `cleanup()` (line 53-66).

**No relationship to compaction** — this is per-tool output truncation, not conversation truncation. `session/compaction.ts`'s `TOOL_OUTPUT_MAX_CHARS = 2_000` (line 30) is a separate constant for **summary serialization** only.

---

## 6. Error Recovery Paths

### 6.1 `ContextOverflowError` (V1)

**Definition**: `packages/core/src/v1/session.ts:64`

```typescript
export const ContextOverflowError = NamedError.create("ContextOverflowError", {
  message: Schema.String,
})
```

**Parsed from**: `MessageV2.fromError` (see `message-v2.ts:606+`) — the provider's `provider-error` event has its `reason` mapped to a `ContextOverflowError` when `isContextOverflow(message)` returns true.

**Detection regex**: `packages/llm/src/provider-error.ts:4-32` — 28 patterns:
- `"prompt is too long"`, `"request_too_large"`, `"input is too long for requested model"`
- `"exceeds the context window"`, `"exceeds (?:the )?(?:model'?s )?maximum context length(?: of [\\d,]+ tokens?|\\s*\\([\\d,]+\\))"`
- `"input token count.*exceeds the maximum"`, `"tokens in request more than max tokens allowed"`
- `"maximum prompt length is \\d+"`, `"reduce the length of the messages"`
- `"maximum context length is \\d+ tokens"`, `"exceeds (?:the )?maximum allowed input length of [\\d,]+ tokens?"`
- `"input (\\d+ tokens) is longer than the model'?s context length (\\d+ tokens)"`
- `"exceeds the limit of \\d+"`, `"exceeds the available context size"`
- `"greater than the context length"`, `"context window exceeds limit"`
- `"exceeded model token limit"`, `"context[_ ]length[_ ]exceeded"`
- `"request entity too large"`, `"context length is only \\d+ tokens"`
- `"input length.*exceeds.*context length"`, `"prompt too long; exceeded (?:max )?context length"`
- `"too large for model with \\d+ maximum context length"`
- `"prompt has [\\d,]+ tokens?, but the configured context size is [\\d,]+ tokens?"`
- `"model_context_window_exceeded"`, `"too many tokens"`, `"token limit exceeded"`
- `^4(00|13)\\s*(status code)?\\s*\\(no body\\)` (provider HTTP code 400/413 with no body)

**Exclusion** (`provider-error.ts:34`):
```typescript
const exclusions = [/^(throttling error|service unavailable):/i, /rate limit/i, /too many requests/i]
```
Rate-limit and overload messages are **not** treated as context overflow.

**Helper**: `isContextOverflow(message: string)` returns `true` for context-overflow messages; `isContextOverflowFailure(failure: unknown)` checks both `LLMError` (with `reason._tag === "InvalidRequest"` and `classification === "context-overflow"`) and `ProviderErrorEvent` (with `classification === "context-overflow"`).

**Recovery path** (V1): see Trigger T3 above. `halt` at `processor.ts:607-617` sets `ctx.needsCompaction = true` (when `compaction.auto !== false` or it's a compaction subagent message), then `process` returns `"compact"`, then `prompt.ts:1321-1327` creates a new compaction task with `overflow: true`.

**If `compaction.auto === false` AND the message is not a compaction summary**: the error is surfaced to the user via `Session.Event.Error` and the session goes idle. The user must invoke `/compact` themselves.

### 6.2 `APIError` (V1) — only when not ContextOverflow

**File**: `packages/opencode/src/session/retry.ts:85-155`

`SessionRetry.retryable` only triggers a retry for `APIError` (not `ContextOverflowError`). Patterns at lines 33-41:
- 429/500/502/503/504/524
- `"rate limit"`, `"too many requests"`, `"overloaded"`, `"service unavailable"`
- `"terminated"`, `"fetch failed"`, `"network error"`, `"connection refused"`, etc.
- `"resource exhausted"`, `"try again later"`, `"currently at capacity"`

These are **retried with backoff** (`delay(...)` at line 47, exponential `RETRY_INITIAL_DELAY=2000 * 2^(attempt-1)`, jitter `RETRY_JITTER_FACTOR=0.25`, cap `RETRY_MAX_DELAY_NO_HEADERS=30_000` or `retry-after-ms`/`retry-after` header), up to `RETRY_MAX_RETRIES=5` attempts.

After exhausting retries, the error is surfaced via `Session.Event.Error` and the session goes idle.

### 6.3 V2 — `LLMError`

**File**: `packages/core/src/session/runner/llm.ts:288-301`

V2's `isContextOverflowFailure` is the same regex-based detector. On detection:
- `compactAfterOverflow` is called (`runner/llm.ts:293`).
- If it returns `true`, the runner `Effect.die`s with `ContinueAfterOverflowCompaction`.
- `runAfterOverflowCompaction` then retries the turn with `recoverOverflow` removed (line 362-374), so a second overflow **fails the turn** (defect message at line 368: `"Post-compaction provider attempt cannot recover another overflow"`).

For **other LLMError** types (non-context-overflow):
- The runner calls `publisher.failUnsettledTools(...)` (line 299) and `publisher.failAssistant(llmFailure.reason.message)` (line 300) — both are projection events, not retries.
- The provider error is then surfaced through the event stream.

### 6.4 `OutputLengthError`, `AbortedError`, etc.

**File**: `packages/opencode/src/session/message-v2.ts:606+` — `fromError(...)` maps:
- `DOMException "AbortError"` → `AbortedError`
- `OutputLengthError` → `OutputLengthError`
- `ContextOverflowError` → `ContextOverflowError`

These are surfaced to the user as `Session.Event.Error` and not retried. They do **not** trigger compaction (except `ContextOverflowError`).

### 6.5 V2 `compactAfterOverflow` failure (sub-recovery)

**File**: `packages/core/src/session/compaction.ts:218`

```typescript
.catchTag("LLM.Error", () => Effect.succeed(false))
```

If the compaction subagent's own LLM call fails (e.g. rate-limited), V2 returns `false` from `compactAfterOverflow` — **no retry, no fallback**. The runner's outer recovery will then likely fail again with another overflow.

V1 by contrast will set `processor.message.error = ContextOverflowError` and return `"stop"` (`compaction.ts:450-458`) — visible to the user as `"Conversation history too large to compact - exceeds model context limit"`.

### 6.6 V1's "compaction itself overflowed" path

**File**: `packages/opencode/src/session/compaction.ts:450-458`

```typescript
if (result === "compact") {
  processor.message.error = new SessionV1.ContextOverflowError({
    message: replay
      ? "Conversation history too large to compact - exceeds model context limit"
      : "Session too large to compact - context exceeds model limit even after stripping media",
  }).toObject()
  processor.message.finish = "error"
  yield* session.updateMessage(processor.message)
  return "stop"
}
```

The error message differs based on `replay`:
- If `replay` is set (overflow path) → "Conversation history too large to compact - exceeds model context limit"
- If `replay` is undefined (manual/preflight without overflow) → "Session too large to compact - context exceeds model limit even after stripping media"

The session then surfaces the error and goes idle. **No further retry.**

---

## 7. Tail Mechanics

### 7.1 What is the "tail"?

The **tail** is the set of recent messages that V1 keeps verbatim after compaction — the `head` (everything before the tail) gets summarized, the `tail` is preserved. V2 calls this the **"recent"** (string) and stores it on the compaction row.

### 7.2 V1 selection algorithm

**File**: `packages/opencode/src/session/compaction.ts:122-163, 223-269`

1. **`turns(messages)`** (`compaction.ts:122-138`): walks the message list and creates one `Turn` per user message (skipping any user message that already has a `compaction` part). Each `Turn` has `{ start: <index in messages>, end: <exclusive end index>, id: <user msg ID> }`. End is set to the next turn's start.

2. **`select({ messages, cfg, model })`** (`compaction.ts:223-269`):
   - Reads `cfg.compaction?.tail_turns`:
     - If `<= 0` → return `{ head: messages, tail_start_id: undefined }` (no retention).
     - If `undefined` → consider **all** turns.
     - If a positive number → `recent = all.slice(-limit)`.
   - Computes the token budget: `budget = cfg.compaction?.preserve_recent_tokens ?? clamp(usable * 0.25, 2_000, 15_000)` (`compaction.ts:115-120`).
   - Walks `recent` **backward** (most-recent first), estimating each turn's JSON-stringified size via `MessageV2.toModelMessagesEffect(...)`:
     - If `total + size <= budget`, **keep the whole turn**, add `size` to `total`, continue.
     - Otherwise, try `splitTurn(turn, remaining, estimate)` to find a sub-turn slice that fits.
     - If no slice fits, **break** — keep what we have so far.
   - Returns `{ head: messages.slice(0, keep.start), tail_start_id: keep.id }`.

3. **`splitTurn({ messages, turn, model, budget, estimate })`** (`compaction.ts:140-163`): walks forward inside the turn from `turn.start + 1`, slicing `messages.slice(start, turn.end)` and estimating. The first slice that fits within the budget wins. The slice's start message ID becomes the `tail_start_id`.

4. **Boundary alignment**: the `tail_start_id` is set to a **user message ID**. So the kept tail always begins with a user turn, never mid-conversation.

5. **Persistence**: `compaction.process` updates the `CompactionPart.tail_start_id` if it changed (line 461-466):
   ```typescript
   if (compactionPart && selected.tail_start_id && compactionPart.tail_start_id !== selected.tail_start_id) {
     yield* session.updatePart({
       ...compactionPart,
       tail_start_id: selected.tail_start_id,
     })
   }
   ```

6. **Filter at model-consumption time** (`packages/opencode/src/session/message-v2.ts:521-572`):
   - `filterCompacted(msgs)` reorders `[compaction-user, summary-assistant, ...tail..., continue-user]` so the model sees the summary inline, then the recent tail, then the synthetic continue.
   - It is called from `prompt.ts:1092-1094` via `MessageV2.filterCompactedEffect(sessionID)`.
   - The `tail_start_id` determines where the tail begins; the **summary is repositioned to be first** so the model reads the compacted context before any retained turns.

### 7.3 V2 selection algorithm

**File**: `packages/core/src/session/compaction.ts:137-158`

```typescript
const select = (entries: readonly Entry[], tokens: number) => {
  const conversation = entries
    .filter((entry) => entry.message.type !== "compaction")
    .map((entry) => serialize(entry.message))
    .filter(Boolean)
  if (conversation.length === 0) return
  let total = 0
  let split = conversation.length
  for (let index = conversation.length - 1; index >= 0; index--) {
    const next = total + Token.estimate(conversation[index])
    if (next > tokens) break
    total = next
    split = index
  }
  return {
    head: conversation.slice(0, split).join("\n\n"),
    recent: conversation.slice(split).join("\n\n"),
  }
}
```

**Differences from V1**:
- Walks **message-by-message** (not turn-by-turn) backward.
- Does not align to user-turn boundaries.
- Returns **strings** (`head` and `recent`) — no per-message IDs.
- The "recent" is **stored on the compaction row** as a single string, and `to-llm-message.ts:153-167` renders it as `<recent-context>...</recent-context>` in the next turn.
- `config.tokens` (default 8,000) is the only knob. No `tail_turns`. No min/max bounds.

### 7.4 Differences between manual and auto

| Aspect | Manual (`/compact`) | Auto (T1/T2/T3) |
|--------|---------------------|-----------------|
| API | `POST /session/:id/summarize` with `auto: false` | Internal `compaction.create({ auto: true })` |
| Buffer logic | same | same |
| Selection | same | same |
| Plugin hook `experimental.session.compacting` | **runs** | **runs** |
| Plugin hook `experimental.compaction.autocontinue` | **skipped** (line 497: `if (!replay)`, and the surrounding `if (result === "continue" && input.auto)` excludes manual) | **runs** |
| Synthetic "Continue" prompt | **never** | **always** (unless plugin disables) |
| `Event.Compacted` publish | **yes** (line 554) | **yes** |
| `replay` (overflow recovery) | **never** (manual never sets `overflow: true`) | **yes for T2/T3** (post-turn + ContextOverflowError) |
| Tail re-selection | always runs (the `if (compactionPart && selected.tail_start_id ...)` block) | always runs |

The **tail itself is selected identically** for manual and auto — same algorithm, same budget, same plugin hook (`experimental.session.compacting`).

### 7.5 Where the tail is recorded

- **V1**: `CompactionPart.tail_start_id` (a `MessageID` referencing a user message in the retained tail).
- **V2**: `SessionMessage.Compaction.recent` (a precomputed `string` of the recent conversation).
- **V1 also stores** `assistantMessage.summary = true` on the compaction agent's response (line 401), which `completedCompactions` uses to find the prior summary (line 108-112).

---

## 8. Complete Pruning Constants

From `packages/opencode/src/session/compaction.ts:28-33`:

```typescript
export const PRUNE_MINIMUM = 20_000        // 20k tokens: must prune at least this much
export const PRUNE_PROTECT = 40_000        // 40k tokens: protect this much
const TOOL_OUTPUT_MAX_CHARS = 2_000        // chars per tool output in summary
const PRUNE_PROTECTED_TOOLS = ["skill"]    // never prune these
const MIN_PRESERVE_RECENT_TOKENS = 2_000   // min tail budget
const MAX_PRESERVE_RECENT_TOKENS = 15_000  // max tail budget
```

From `packages/opencode/src/session/overflow.ts:8`:

```typescript
const COMPACTION_BUFFER = 20_000           // default token buffer
```

From `packages/opencode/src/provider/transform.ts:18`:

```typescript
export const OUTPUT_TOKEN_MAX = 32_000     // hard ceiling for max output
```

From `packages/core/src/session/compaction.ts:12-15`:

```typescript
const DEFAULT_BUFFER = 20_000              // V2 buffer default
const DEFAULT_KEEP_TOKENS = 8_000          // V2 tail default
const TOOL_OUTPUT_MAX_CHARS = 2_000        // V2 summary tool output cap
const SUMMARY_OUTPUT_TOKENS = 4_096        // V2 summary max output
```

The 4-char / token heuristic in the prompt is **`Token.estimate`** (`packages/opencode/src/util/token.ts` + `packages/core/src/util/token.ts`); both are byte-length-based approximations (`/ 4` chars per token or similar). The V2 path always uses `Token.estimate(JSON.stringify(...))`.

---

## 9. Conclusions (Definitive Map)

### 9.1 Two systems coexist

V1 (`packages/opencode/src/session/`) and V2 (`packages/core/src/session/`) are **both wired into the live server** (`httpapi/server.ts:295-303`). V1 is the user-facing path (TUI `/compact`, HTTP `/session/:id/summarize`, in-loop preflight + post-turn + ContextOverflowError recovery). V2 is the internal Effect-native path used when callers go through the V2 `sessions.prompt` API. For TUI users today, **V1 is what runs**.

### 9.2 Eight distinct trigger conditions (counted across both systems)

| ID | File | When |
|----|------|------|
| V1-T1 | `prompt.ts:1161` | Loop preflight: `lastFinished.tokens >= usable` |
| V1-T2 | `processor.ts:477` | Post-turn (step-finish): same overflow check |
| V1-T3 | `processor.ts:607` | `ContextOverflowError` from provider |
| V1-T4 | `tui/.../session/index.tsx:580` + `handlers/session.ts:273` | Manual `/compact` |
| V1-T5 | `prompt.ts:1338` | Background prune (post-loop) |
| V1-T6 | `compaction.ts:340-356` | Overflow replay (sub-trigger of T2/T3) |
| V2-T7 | `runner/llm.ts:222` | Preflight: `estimate(request) > context - max(output, buffer)` |
| V2-T8 | `runner/llm.ts:289-295` | Provider context-overflow error before assistant starts |

### 9.3 Three V1 strategies, one V2 strategy

- **V1 Summarize** (default): head→summary, tail kept verbatim by token budget.
- **V1 Prune** (opt-in via `compaction.prune`): marks old tool outputs as compacted (display only).
- **V1 Replay** (sub-trigger of overflow): re-emit user msg with media stripped.
- **V2 Summarize** (the only one): same head→summary approach but with a stored `recent` string.

### 9.4 Two plugin hooks (V1 only)

- `experimental.session.compacting` — replaces or augments the compaction prompt.
- `experimental.compaction.autocontinue` — disables the synthetic "Continue" prompt.
- (Collateral: `experimental.chat.messages.transform` rewrites the head.)

### 9.5 Error recovery

- **V1**: `ContextOverflowError` → `compaction.create({ overflow: true })` → `process` (with media-stripped replay). Auto-compaction **disabled** by `compaction.auto = false` (then the error is surfaced to the user).
- **V1**: `ContextOverflowError` from the **compaction subagent itself** → `processor.message.error = ContextOverflowError`, `finish = "error"`, session goes idle. No retry.
- **V1**: Other `APIError` (5xx, 429, network) → `SessionRetry.retryable` → exponential backoff up to 5 retries, then surfaced.
- **V2**: Context overflow → `compactAfterOverflow` → turn retry; on second overflow, fail the turn.
- **V2**: Other `LLMError` → publish via `publisher.failUnsettledTools` + `publisher.failAssistant`, no retry.

### 9.6 Tail mechanics

- **V1 tail**: `tail_start_id` of a user message; `tail_turns` cap; `preserve_recent_tokens` budget defaulting to `clamp(usable*0.25, 2k, 15k)`. Stored on the `CompactionPart`.
- **V2 tail** (recent): a precomputed string on the `compaction` message; `tokens` budget defaulting to 8,000.
- **Tail alignment**: V1 aligns to user-turn boundaries; V2 splits at message granularity.
- **No difference** between manual and auto for the tail itself.

### 9.7 Provider-specific behaviors

- **No provider-specific compaction code**. All compaction runs through the LLM SDK.
- **V1** uses `assistant.tokens` counters from `step-finish`.
- **V2** uses a preflight `Token.estimate(JSON.stringify(request))` — no provider counters read.
- **V2 only**: `promptCacheKey` for OpenAI-compatible providers, `x-session-affinity` / `X-Session-Id` headers for session-aware routing.
- **V1 only**: the `compaction_continue` marker (synthetic + metadata) that the GitHub Copilot plugin reads; not a stable contract.

### 9.8 `tool/truncate.ts`

- **Not** a compaction strategy. It is a **per-tool output** truncator: when output > `MAX_LINES=2000` or `MAX_BYTES=50*1024`, the full output is written to `~/.local/share/opencode/tool-output/tool_<id>` (7-day retention) and the model receives a head preview (default `direction: "head"`).
- Wired via `SessionTools.resolve` in `prompt.ts:1239`; the truncate service is provided to the tool registry.
- Does not mutate the conversation.

### 9.9 The "hidden `agent='compaction'` subagent" the previous investigations mentioned

It exists. Definition at `agent/agent.ts:219-233`:
- `name: "compaction"`, `mode: "primary"`, `hidden: true` (not shown in `/agents` or `/switch`).
- `prompt: PROMPT_COMPACTION` (`agent/prompt/compaction.txt`) — 5 lines instructing the subagent to be a "context summarization agent" producing structured output.
- `permission: { "*": "deny" }` (no tools).
- The subagent's **model** comes from `agents.get("compaction").model`, with fallback to the user message's model (`compaction.ts:359-361`).
- The subagent is invoked via `processor.process(...)` with the built `nextPrompt` (line 425-448) and a single user message in the request.
- Its response is persisted as an assistant message with `mode: "compaction"`, `agent: "compaction"`, `summary: true` (line 393-419) — `summary: true` is the marker that `completedCompactions` and `filterCompacted` use to find prior summaries.

### 9.10 Config migration

V1 configs with `tail_turns` lose that field on migration (`migrate.ts:54-61`). V1 `reserved` → V2 `buffer`, V1 `preserve_recent_tokens` → V2 `keep.tokens`, V1 `prune` is preserved but V2 has no implementation for it. The V2 path is therefore **feature-incomplete** relative to V1 today.

---

## 10. Confidence Assessment

| Aspect | Confidence | Reasoning |
|--------|-----------|-----------|
| V1 trigger conditions (T1-T6) | **HIGH** | All 6 paths located by exact line numbers; `SessionCompaction.Service` is the only mutator of CompactionPart; the loop is the only entry to `compaction.process`. |
| V2 trigger conditions (T7-T8) | **HIGH** | Both paths in `runner/llm.ts` are exact and unique. |
| V1 strategy details | **HIGH** | The full `compaction.ts` (608 lines) was read end-to-end; the `select`/`prune`/`process` functions are small and self-contained. |
| V2 strategy details | **HIGH** | The full `core/src/session/compaction.ts` (248 lines) was read end-to-end. |
| Plugin hooks | **HIGH** | All 3 hooks enumerated at `plugin/src/index.ts:282-326`; the V1 trigger sites are exact. |
| Provider behaviors | **HIGH** | The V2 `promptCacheKey` and `x-session-affinity` headers are exact; V1's `compaction_continue` is exact. The absence of provider-specific compaction code was verified by grep across `packages/opencode/src/provider/`. |
| Error recovery paths | **HIGH** | All 28 overflow patterns enumerated at `llm/src/provider-error.ts:4-32`; retry logic at `retry.ts:33-41`; V1 halt logic at `processor.ts:599-625`. |
| Tail mechanics | **HIGH** | Both V1 and V2 `select` algorithms read end-to-end; the `tail_start_id` storage and `filterCompacted` reordering verified. |
| Manual vs auto differences | **HIGH** | The two flow paths are gated by `if (!replay)` and `if (result === "continue" && input.auto)` (lines 468, 497) — these are the only conditional differences. |
| `tool/truncate.ts` role | **HIGH** | Module is small (156 lines) and not on the compaction hot path; `SessionTools.resolve` is the only integration. |
| Which system is "active" | **MEDIUM** | Both are wired into the live server. TUI invokes V1 only. V2 is reachable through V2 APIs (e.g. `core/session` exports) but the TUI does not call them. **There may be additional V2 entry points not surfaced through TUI** (e.g. desktop app, web app). |

**Overall confidence: HIGH** for the architecture; **MEDIUM** for the live-traffic split because the desktop/web UIs were not exhaustively traced.

---

*⬡ OMEGA ⬡ KALI ⬡ R_COPILOT_ALL_COMPACTION_PATHS-v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
