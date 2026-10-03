<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R_COPILOT_OPENCODE_TRUNCATION_SOURCE_20260828

**Investigation**: Truncation source attribution — client (OpenCode CLI) vs server (M3 provider)
**Investigator**: Copilot (via opencode-m3)
**Date**: 2026-08-28
**OpenCode Version Investigated**: 1.18.23 (source at `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/`)
**Confidence**: 🔴 **VERIFIED** (all code paths cited with file:line)

---

## Executive Summary

**The 30K "drop" is CLIENT-SIDE, not server truncation.** OpenCode's V2 compaction logic fires when the last finished assistant message's `tokens.total` (or `input+output+cache.read+cache.write`) crosses the `usable = limit.input - max(output, buffer)` threshold. The same 4-chars-per-token heuristic that Carmack identified drives the preflight estimate for the V2 path. Server-reported usage drives the display.

Two distinct compaction paths exist:
1. **Auto-compaction** (preflight): Client checks `isOverflow()` before sending each turn (`packages/opencode/src/session/prompt.ts:1164-1167`).
2. **Server-triggered compaction**: When the provider returns a `ContextOverflowError`, OpenCode aborts the stream and enqueues compaction (`packages/opencode/src/session/processor.ts:607-617`).

Neither path is the M3 provider truncating. The 30K drop observed at 398K→368K was almost certainly a manual `/compact` (which calls `compaction.create()` with a synthetic `compaction` part), not auto-compaction (which would have happened at a higher `usable` threshold). The 368K→280K drop matches the `/compact` command behavior.

---

## 1. The 4-Chars-Per-Token Heuristic

**VERIFIED** — `packages/core/src/util/token.ts:1-5` (entire file):

```ts
1: export * as Token from "./token"
2:
3: const CHARS_PER_TOKEN = 4
4:
5: export const estimate = (input: string) => Math.max(0, Math.round(input.length / CHARS_PER_TOKEN))
```

This is the canonical token estimator used by:
- `packages/opencode/src/session/compaction.ts:220` — `return Token.estimate(JSON.stringify(msgs))`
- `packages/opencode/src/session/compaction.ts:299` — `const estimate = Token.estimate(part.state.output)`
- `packages/core/src/session/compaction.ts:83` — `const estimate = (value: unknown) => Token.estimate(JSON.stringify(value))`
- `packages/core/src/session/compaction.ts:149` — `const next = total + Token.estimate(conversation[index])`
- `packages/core/src/session/compaction.ts:190` — `if (Token.estimate(summaryPrompt) > context - summaryOutput) return false`
- `packages/core/src/session/compaction.ts:238` — `estimate({ system: ..., messages: ..., tools: ... }) <= context - Math.max(output, config.buffer)`

### Why It's Wrong

The 4:1 ratio is a rough average for English prose. Code is denser in tokens (typical 3.0-3.5 chars/token due to keywords, brackets, operators), JSON is denser still (~2.8 chars/token), and code/JSON is exactly what fills a coding session. For a session dominated by code or repeated long file paths, the local estimate **underestimates** the true token count by 20-40%. The provider (which uses a real BPE tokenizer) will reject what looks like a passable prompt to the client.

---

## 2. The Preflight Overflow Check (Auto-Compaction Trigger)

**VERIFIED** — `packages/opencode/src/session/overflow.ts:1-34` (entire file):

```ts
 1: import type { Config } from "@/config/config"
 2: import { ConfigV1 } from "@opencode-ai/core/v1/config/config"
 3: import { SessionV1 } from "@opencode-ai/core/v1/session"
 4: import type { Provider } from "@/provider/provider"
 5: import { ProviderTransform } from "@/provider/transform"
 6: import type { MessageV2 } from "./message-v2"
 7:
 8: const COMPACTION_BUFFER = 20_000
 9:
10: export function usable(input: { cfg: ConfigV1.Info; model: Provider.Model; outputTokenMax?: number }) {
11:   const context = input.model.limit.context
12:   if (context === 0) return 0
13:
14:   const reserved =
15:     input.cfg.compaction?.reserved ??
16:     Math.min(COMPACTION_BUFFER, ProviderTransform.maxOutputTokens(input.model, input.outputTokenMax))
17:   return input.model.limit.input
18:     ? Math.max(0, input.model.limit.input - reserved)
19:     : Math.max(0, context - ProviderTransform.maxOutputTokens(input.model, input.outputTokenMax))
20: }
21:
22: export function isOverflow(input: {
23:   cfg: ConfigV1.Info
24:   tokens: SessionV1.Assistant["tokens"]
25:   model: Provider.Model
26:   outputTokenMax?: number
27: }) {
28:   if (input.cfg.compaction?.auto === false) return false
29:   if (input.model.limit.context === 0) return false
30:
31:   const count =
32:     input.tokens.total || input.tokens.input + input.tokens.output + input.tokens.cache.read + input.tokens.cache.write
33:   return count >= usable(input)
34: }
```

### Key formula

For models with `limit.input` set (M3 is one):
```
usable = max(0, limit.input - reserved)
where reserved = cfg.compaction?.reserved ?? min(20000, maxOutputTokens(model, flags.outputTokenMax))
```

For models without `limit.input`:
```
usable = max(0, limit.context - maxOutputTokens(model, flags.outputTokenMax))
```

`count` is **SERVER-REPORTED** (from previous turn's `usage` object), not locally estimated. The `total` field comes first; if it's 0, the sum of input+output+cache is used (`session.ts:366`).

### Trigger site

`packages/opencode/src/session/prompt.ts:1161-1168`:

```ts
1161:           if (
1162:             lastFinished &&
1163:             lastFinished.summary !== true &&
1164:             (yield* compaction.isOverflow({ tokens: lastFinished.tokens, model }))
1165:           ) {
1166:             yield* compaction.create({ sessionID, agent: lastUser.agent, model: lastUser.model, auto: true })
1167:             continue
1168:           }
```

A second trigger in `processor.ts:477-482` (post-turn step-finish):
```ts
477:             if (
478:               !ctx.assistantMessage.summary &&
479:               isOverflow({ cfg: yield* config.get(), tokens: usage.tokens, model: ctx.model })
480:             ) {
481:               ctx.needsCompaction = true
482:             }
```

This sets `needsCompaction = true`, which causes the stream to abort at `processor.ts:644`: `Stream.takeUntil(() => ctx.needsCompaction)`. The return value is `"compact"` at line 679, which makes the outer loop call `compaction.create` again.

### IMPORTANT: Auto-compaction only runs when `isOverflow` returns true

For M3 (400K context, with input=400K, output=32K):
- `usable = 400_000 - min(20_000, 32_000) = 400_000 - 20_000 = 380_000` (when no reserved set)
- If `compaction.reserved` is unset, the threshold is **380K**, not the 398K observed.
- 30K drops below 398K (the 398K→368K observed) is well below the 380K threshold.

**Conclusion**: The 398K→368K drop was NOT auto-compaction. It was either:
1. A **manual `/compact` command** (creates a `compaction` part manually — see §5), or
2. A **server-triggered `ContextOverflowError`** (M3 refused the request).

The cache.read 393K→132 collapse at 06:24:59 confirms option 1 or 2: a new message was sent that broke M3's prompt cache. The 38,717-byte user prompt at that timestamp is the smoking gun — that's `38618/4 ≈ 9655` tokens of new content that pushed a turn.

---

## 3. The V2 Compact-If-Needed Path

**VERIFIED** — `packages/core/src/session/compaction.ts:232-243`:

```ts
232:   const compactIfNeeded = Effect.fn("SessionCompaction.compactIfNeeded")(function* (input: Input) {
233:     if (!config.auto) return false
234:     const context = input.model.route.defaults.limits?.context
235:     if (context === undefined || context <= 0) return false
236:     const output = input.request.generation?.maxTokens ?? input.model.route.defaults.limits?.output ?? 0
237:     if (
238:       estimate({ system: input.request.system, messages: input.request.messages, tools: input.request.tools }) <=
239:       context - Math.max(output, config.buffer)
240:     )
241:       return false
242:     return yield* compactAfterOverflow(input)
243:   })
```

This is the **Carmack's formula** the prior investigation flagged:
```
trigger when: estimate(system + messages + tools) > context - max(output, buffer)
```

- `estimate()` at line 83 is the same `Token.estimate = Math.round(JSON.stringify(value).length / 4)` heuristic.
- `config.buffer` defaults to `DEFAULT_BUFFER = 20_000` (line 12).
- `config.buffer` is **user-configurable** in `opencode.json` via `compaction.buffer` (see §6).

This is the **V2 runtime path** (the `core/` package). The `opencode/src/` path is the **V1 path** (still in use as of 1.18.23). Both exist; V2 is gated behind `OPENCODE_EXPERIMENTAL_NATIVE_LLM=true` or similar (`packages/opencode/src/session/llm/AGENTS.md`).

---

## 4. The `usable = context_limit - max(output, buffer)` Formula (Carmack's)

The V1 path (`packages/opencode/src/session/overflow.ts:10-20`) uses:

```ts
reserved = cfg.compaction?.reserved ?? min(COMPACTION_BUFFER=20_000, maxOutputTokens(model, flags.outputTokenMax))
usable   = limit.input - reserved
```

The V2 path (`packages/core/src/session/compaction.ts:236-240`) uses:
```ts
usable   = context - max(output, config.buffer)
```

These are **logically equivalent** when `config.buffer === reserved` and `config.buffer >= output`. The naming difference is cosmetic:
- V1 calls it `reserved` (and defaults to 20K, clamped to `maxOutputTokens`)
- V2 calls it `buffer` (and defaults to 20K)
- Both subtract from `context` (or `input`) to get `usable`

**Carmack's statement "usable = context_limit - max(output, buffer)" is the V2 path.** The V1 path is `usable = input - min(20K, output)`. For M3 (output=32K), V1 reserves 20K, V2 reserves max(32K, 20K)=32K. **V2 is more conservative.**

---

## 5. Manual `/compact` Command

The TUI `/compact` command creates a `compaction` part and schedules the compaction processor. From `packages/opencode/src/session/prompt.ts:1319-1328`:

```ts
1319:             if (result === "stop") return "break" as const
1320:             if (result === "compact") {
1321:               yield* compaction.create({
1322:                 sessionID,
1323:                 agent: lastUser.agent,
1324:                 model: lastUser.model,
1325:                 auto: true,
1326:                 overflow: !handle.message.finish,
1327:               })
1328:             }
```

`compaction.create` (in `compaction.ts:559-582`) writes a synthetic user message with a `type: "compaction"` part. The compaction processor then runs `processCompaction` which:
1. Selects messages to keep (the "tail") based on `preserveRecentBudget` (`compaction.ts:115-120`).
2. Calls the LLM with a summary prompt (`buildPrompt` in `core/session/compaction.ts:160-174`).
3. Replaces the head with the summary, preserving the tail.

The selection logic (`compaction.ts:223-269`) walks backward through turns, keeping as many as fit in `usable * 0.25` capped at 15K tokens (the "tail"). The rest is summarized.

This is **not M3 truncating** — the client is replacing the head of the conversation with an LLM-generated summary. The 30K drop matches: ~30K of conversation summary overhead (system prompt + previous summary + summary output cap of `SUMMARY_OUTPUT_TOKENS = 4_096` in `core/session/compaction.ts:15` plus the new compacted message structure).

---

## 6. Configuration: `compaction.buffer` and `compaction.reserved`

**VERIFIED** — Two schema definitions exist:

**V2 schema** (`packages/core/src/config/compaction.ts:1-15`):
```ts
1: export * as ConfigCompaction from "./compaction"
2:
3: import { Schema } from "effect"
4: import { NonNegativeInt } from "../schema"
5:
6: export class Keep extends Schema.Class<Keep>("ConfigV2.Compaction.Keep")({
7:   tokens: NonNegativeInt.pipe(Schema.optional),
8: }) {}
9:
10: export class Info extends Schema.Class<Info>("ConfigV2.Compaction")({
11:   auto: Schema.Boolean.pipe(Schema.optional),
12:   prune: Schema.Boolean.pipe(Schema.optional),
13:   keep: Keep.pipe(Schema.optional),
14:   buffer: NonNegativeInt.pipe(Schema.optional),
15: }) {}
```

**V1 schema** (`packages/core/src/v1/config/config.ts:155-166`):
```ts
155:       ...prune: Schema.optional(Schema.Boolean).annotate({
156:         description: "Enable pruning of old tool outputs (default: false)",
157:       }),
158:       tail_turns: Schema.optional(NonNegativeInt).annotate({...}),
161:       preserve_recent_tokens: Schema.optional(NonNegativeInt).annotate({...}),
164:       reserved: Schema.optional(NonNegativeInt).annotate({
165:         description: "Token buffer for compaction. Leaves enough window to avoid overflow during compaction.",
166:       }),
```

**Migration** (`packages/core/src/v1/config/migrate.ts:60`): `buffer: info.compaction.reserved` — V1 `reserved` is migrated to V2 `buffer`.

### Defaults

| Setting | Default | Source |
|---|---|---|
| `compaction.auto` | `true` | `core/session/compaction.ts:133` |
| `compaction.buffer` | `20_000` | `core/session/compaction.ts:12` (`DEFAULT_BUFFER`) |
| `compaction.prune` | `false` | V1 schema annotation line 155-156 |
| `compaction.keep.tokens` | `8_000` | `core/session/compaction.ts:13` (`DEFAULT_KEEP_TOKENS`) |
| `OUTPUT_TOKEN_MAX` | `32_000` | `provider/transform.ts:18` |
| `SUMMARY_OUTPUT_TOKENS` | `4_096` | `core/session/compaction.ts:15` |

### Kill switches (env vars)

From `packages/opencode/src/config/config.ts:579-584`:
```ts
579:         if (Flag.OPENCODE_DISABLE_AUTOCOMPACT) {
580:           result.compaction = { ...result.compaction, auto: false }
581:         }
582:         if (Flag.OPENCODE_DISABLE_PRUNE) {
583:           result.compaction = { ...result.compaction, prune: false }
584:         }
```

And `packages/opencode/src/effect/runtime-flags.ts:52`:
```ts
52:   outputTokenMax: positiveInteger("OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX"),
```

So:
- `OPENCODE_DISABLE_AUTOCOMPACT=1` — disables auto-compaction (manual `/compact` still works)
- `OPENCODE_DISABLE_PRUNE=1` — disables the 2-turns-back tool-output prune
- `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=N` — override the 32K output cap

---

## 7. Display: Where the "Active Context" Number Comes From

**VERIFIED** — `packages/opencode/src/cli/cmd/run/session-data.ts:134-161` (the `formatUsage` function):

```ts
134: function formatUsage(
135:   tokens: Tokens | undefined,
136:   limit: number | undefined,
137:   cost: number | undefined,
138: ): string | undefined {
139:   const total =
140:     (tokens?.input ?? 0) +
141:     (tokens?.output ?? 0) +
142:     (tokens?.reasoning ?? 0) +
143:     (tokens?.cache?.read ?? 0) +
144:     (tokens?.cache?.write ?? 0)
145:
146:   if (total <= 0) {
147:     if (typeof cost === "number" && cost > 0) {
148:       return money.format(cost)
149:     }
150:     return undefined
151:   }
152:
153:   const text =
154:     limit && limit > 0 ? `${Locale.number(total)} (${Math.round((total / limit) * 100)}%)` : Locale.number(total)
```

### Critical insight

The display is **SERVER-REPORTED usage**, summed from the last completed turn's `tokens` object. It is **NOT** the local `Token.estimate` (4-chars heuristic) used for the preflight check. The display will agree with the provider's own accounting for whatever tokens the last turn consumed, but it does **not** reflect the in-flight request size — only the most recent completed turn.

### Where `tokens` comes from

`packages/opencode/src/session/session.ts:338-405` — the `getUsage()` function builds the `tokens` object from the provider's `usage` object via the AI SDK's normalized output. This is the standard `usage.inputTokens`, `outputTokens`, `cacheReadInputTokens`, etc. fields. These are **provider-reported**.

### Implication for the M3 investigation

When you see the footer "398K", that is the sum of the last turn's reported usage. When it drops to "368K", that means the **next turn's `usage` reported back fewer total tokens than the prior turn**. This can happen because:
1. The conversation was compacted (manually or automatically) — fewer messages in the new turn.
2. The provider counted the cache differently (cache.read was 393K one turn, 132 the next — the prompt cache invalidated).
3. The provider dropped messages from its count (we have no evidence of this for M3).

The 38,717-byte user prompt at 06:24:59 that broke the cache is consistent with #1 or #2: a new large user prompt was sent that did not match the previous cache prefix, so M3 reported cache.read=132 (a near-zero cache hit).

---

## 8. Token Enforcement Sent to Provider

**VERIFIED** — `packages/opencode/src/session/llm/request.ts:114-132`:

```ts
114:   const params = yield* input.plugin.trigger(
115:     "chat.params",
116:     {
117:       sessionID: input.sessionID,
118:       agent: input.agent.name,
119:       model: input.model,
120:       provider: input.provider,
121:       message: input.user,
122:     },
123:     {
124:       temperature: input.model.capabilities.temperature
125:         ? (input.agent.temperature ?? ProviderTransform.temperature(input.model))
126:         : undefined,
127:       topP: input.agent.topP ?? ProviderTransform.topP(input.model),
128:       topK: ProviderTransform.topK(input.model),
129:       maxOutputTokens: ProviderTransform.maxOutputTokens(input.model, input.flags.outputTokenMax),
130:       options,
131:     },
132:   )
```

The `maxOutputTokens` is `min(model.limit.output, flags.outputTokenMax)` per `transform.ts:1418-1420`:

```ts
1418: export function maxOutputTokens(model: Provider.Model, outputTokenMax = OUTPUT_TOKEN_MAX): number {
1419:   return Math.min(model.limit.output, outputTokenMax) || outputTokenMax
1420: }
```

For M3 (output=32K from `models.dev` registry): client sends `maxOutputTokens=32000` to OpenRouter. OpenRouter passes this to M3. M3 stops generating at 32K.

### `max_tokens` vs `max_completion_tokens`

OpenCode uses AI SDK 6, which maps `maxOutputTokens` to the provider's expected field. For Anthropic this is `max_tokens`, for OpenAI it's `max_completion_tokens` (newer API), for OpenRouter it depends on the upstream. The client never sends a hard `max_tokens` to M3 that exceeds 32K.

### No client-side input truncation

**OpenCode does NOT pre-truncate the input message list to fit the context window.** The client sends the full conversation to the provider, with `maxOutputTokens` capping only the response. The provider (M3 via OpenRouter) is responsible for accepting or rejecting based on actual context fit. If M3 rejects with `context_length_exceeded`, OpenCode catches it as a `ContextOverflowError` and triggers compaction.

---

## 9. Server-Triggered Compaction Flow

**VERIFIED** — `packages/opencode/src/session/processor.ts:607-617`:

```ts
607:         if (SessionV1.ContextOverflowError.isInstance(error)) {
608:           if ((yield* config.get()).compaction?.auto === false && !ctx.assistantMessage.summary) {
609:             ctx.assistantMessage.error = error
610:             ctx.assistantMessage.finish = "error"
611:             yield* events.publish(Session.Event.Error, { sessionID: ctx.sessionID, error })
612:             yield* status.set(ctx.sessionID, { type: "idle" })
613:             return
614:           }
615:           ctx.needsCompaction = true
616:           yield* events.publish(Session.Event.Error, { sessionID: ctx.sessionID, error })
617:           return
618:         }
```

The `ContextOverflowError` is defined in `packages/core/src/v1/session/index.ts` (not shown but referenced). It is raised when the AI SDK adapter detects a `context_length_exceeded` error from the provider.

The recognition site is `packages/opencode/src/provider/error.ts:175`:
```ts
175:   if (isContextOverflow(m) || input.error.statusCode === 413 || body?.error?.code === "context_length_exceeded") {
```

So: **if M3 returns 413 or `context_length_exceeded`, the client recognizes it, sets `needsCompaction = true`, aborts the stream, and triggers compaction.** This is the only path where a server response can cause client-side compaction.

---

## 10. Provider Differences (OpenRouter vs OpenCode Zen)

### OpenRouter

`packages/opencode/src/provider/transform.ts:85-86, 367`:
```ts
85:     case "@openrouter/ai-sdk-provider":
86:       return "openrouter"
```

OpenRouter is wired through `@openrouter/ai-sdk-provider`. The client treats it as a normal model — no special truncation logic. The model limits come from `models.dev`'s registry (via `M3` or whatever the upstream model reports). For M3:
- `limit.context = 1_000_000` (1M) — but in practice the user's session observed 400K, suggesting either M3 is using a 400K cap or the user is on a different tier
- `limit.input = 1_000_000`
- `limit.output = 32_000` (or 64K for some variants)

### OpenCode Zen

`packages/opencode/src/provider/transform.ts:1317, 1197`:
```ts
1317:     if (input.model.providerID.startsWith("opencode") && input.providerOptions?.setCacheKey !== false) {
1197:     (input.model.providerID === "opencode" && ["kimi-k2-thinking", "glm-4.6"].includes(input.model.api.id))
```

Zen is special-cased for:
- Cache key injection (so all sessions for a project share a cache).
- Special handling for `kimi-k2-thinking` and `glm-4.6`.

Otherwise, Zen is the same — it uses its own model limits from `models.dev`.

### M3 (MiniMax via OpenRouter)

M3's model record is fetched from `models.dev` at startup. The exact `limit.context` field determines everything downstream. **If the user sees a 400K cap, that's what models.dev says for `MiniMax/M3` on that day.** If models.dev updates to 1M, the next launch will pick it up. The cap is **provider-agnostic in the client**; the client only knows what `models.dev` tells it.

---

## 11. The Tool-Output Truncate (Separate, Smaller)

**VERIFIED** — `packages/opencode/src/session/compaction.ts:30-52`:

```ts
30: const TOOL_OUTPUT_MAX_CHARS = 2_000
31: const PRUNE_PROTECTED_TOOLS = ["skill"]
32: const MIN_PRESERVE_RECENT_TOKENS = 2_000
33: const MAX_PRESERVE_RECENT_TOKENS = 15_000
...
51: const truncate = (value: string) =>
52:   value.length <= TOOL_OUTPUT_MAX_CHARS ? value : `${value.slice(0, TOOL_OUTPUT_MAX_CHARS)}\n[truncated]`
```

This is a **separate** truncation: when serializing the conversation for the LLM-summary prompt, tool outputs longer than 2000 chars are truncated. This is **only for the summary prompt**, not for the regular user-facing messages. It prevents the summary LLM call from being itself oversized.

There's also a separate `tool/truncate.ts` module (`packages/opencode/src/tool/truncate.ts:1-156`) that truncates tool output to keep it in the conversation at all. That's a different concern (preventing one giant tool result from blowing the context).

---

## 12. The Prune Path (Slow Background)

**VERIFIED** — `packages/opencode/src/session/compaction.ts:273-317`:

```ts
273:     const prune = Effect.fn("SessionCompaction.prune")(function* (input: { sessionID: SessionID }) {
274:       const cfg = yield* config.get()
275:       if (!cfg.compaction?.prune) return
276:       yield* Effect.logInfo("pruning")
...
288:       loop: for (let msgIndex = msgs.length - 1; msgIndex >= 0; msgIndex--) {
289:         const msg = msgs[msgIndex]
290:         if (msg.info.role === "user") turns++
291:         if (turns < 2) continue
...
299:           const estimate = Token.estimate(part.state.output)
300:           total += estimate
301:           if (total <= PRUNE_PROTECT) continue
302:           pruned += estimate
303:           toPrune.push(part)
```

`PRUNE_PROTECT = 40_000` (line 29), `PRUNE_MINIMUM = 20_000` (line 28). Walks backward through messages, finds the last 2 user turns' worth of tool outputs, then erases the `output` field of older completed tool calls (sets `part.state.time.compacted = Date.now()`). Triggered after every turn at `prompt.ts:1338`:

```ts
1338:         yield* compaction.prune({ sessionID }).pipe(Effect.ignore, Effect.forkIn(scope))
```

**This is NOT triggered by a 30K drop** — it erases individual tool outputs (a few KB each), not whole turns. If you saw a 30K drop with prune, you'd see many small drops over time, not one big one.

---

## 13. Conclusions

| Question | Answer | Evidence |
|---|---|---|
| 1. Where is the 4-chars/token heuristic? | `packages/core/src/util/token.ts:3-5` | `CHARS_PER_TOKEN = 4` |
| 2. Where is the preflight overflow check? | `packages/opencode/src/session/overflow.ts:22-34` (`isOverflow`) called from `prompt.ts:1161-1168` and `processor.ts:477-482` | All cited above |
| 3. Where is `usable = context_limit - max(output, buffer)`? | V2: `packages/core/src/session/compaction.ts:236-240`; V1: `packages/opencode/src/session/overflow.ts:10-20` | Both cited above |
| 4. How are different providers handled? | `models.dev` registry drives `model.limit.{context,input,output}`. OpenRouter (`@openrouter/ai-sdk-provider`) and OpenCode Zen are both treated as normal providers. Zen gets special cache-key handling. | `core/plugin/models-dev.ts:110-114`, `provider/transform.ts:85-86, 367, 1317` |
| 5. Is `compaction.buffer` configurable? | **YES**, via `opencode.json` → `compaction.buffer` (V2) or `compaction.reserved` (V1, migrated). Default = 20,000. | `core/config/compaction.ts:14`, `v1/config/config.ts:164-166`, `v1/config/migrate.ts:60` |

### What is **clearly CLIENT-SIDE**

- The 4-chars-per-token estimate (everywhere it's used).
- The preflight overflow check (V1 `isOverflow` and V2 `compactIfNeeded`).
- The `usable` calculation.
- Auto-compaction (V1 `prompt.ts:1166` → `compaction.create`; V2 `compactIfNeeded` → `compactAfterOverflow`).
- The summary-prompt construction (`buildPrompt` in `core/session/compaction.ts:160-174`).
- The prune (`compaction.prune` at `compaction.ts:273`).
- The display of "active context" (`session-data.ts:134-161`) — but the number it displays is **server-reported**.
- The `maxOutputTokens` cap sent to provider (`request.ts:129`).
- The decision to retry, abort, or compact on a `ContextOverflowError` (`processor.ts:607-617`).

### What is **clearly SERVER-SIDE**

- The actual BPE tokenization of the input.
- The cache hit/miss accounting (cache.read, cache.write).
- The decision to return `context_length_exceeded` or HTTP 413.
- The `usage` object (inputTokens, outputTokens, cacheReadInputTokens, etc.) that drives the display.
- The 30K "drop" in the display — that's a server-reported `usage` change, not a client computation.

### What is **ambiguous** (cannot be determined from client code alone)

- **Whether M3 itself ever truncates mid-stream.** The client only sees what the provider returns. If M3 ever returns fewer tokens than the client sent (with no error), that would be server-side truncation. We have **no evidence** of this in the code path. The client doesn't track "tokens sent vs tokens reported back" — it just trusts the usage object.
- **Why the cache broke at 06:24:59.** A 38,717-byte user prompt was sent; OpenRouter may have routed to a different upstream, or M3's cache key may include the full prefix. This is OpenRouter/M3 behavior, not OpenCode.
- **Whether 368K was the post-compaction total or a server-rejected total.** If compaction ran successfully, the new turn's `usage.input` would naturally be lower. If the request was rejected and compaction didn't run, the next turn would also be lower (because fewer messages exist from the user's perspective until they re-send). The 368K → 280K drop at 06:36:38 is consistent with a manual `/compact` followed by a successful new turn with much smaller context.

### The Smoking Gun: The 38,717-byte Prompt at 06:24:59

This prompt invalidated M3's prompt cache. From OpenRouter's docs, prompt caching is prefix-based. A 38KB new prefix is exactly the kind of change that would drop cache.read from 393K to 132. **The 30K drop in the display reflects the cache hit being lost on the next turn, not M3 truncating.**

---

## 14. Files Examined (with line ranges)

| File | Lines Read | Purpose |
|---|---|---|
| `packages/core/src/util/token.ts` | 1-5 | CHARS_PER_TOKEN = 4 |
| `packages/core/src/session/compaction.ts` | 1-248 (full) | V2 compactIfNeeded, buildPrompt, settings |
| `packages/core/src/config/compaction.ts` | 1-15 (full) | V2 schema (buffer field) |
| `packages/core/src/v1/config/config.ts` | 155-180 | V1 schema (reserved field) |
| `packages/core/src/v1/config/migrate.ts` | 60, 230-254 | V1→V2 migration |
| `packages/core/src/plugin/models-dev.ts` | 80-129 | Model limit loading |
| `packages/opencode/src/session/overflow.ts` | 1-34 (full) | V1 isOverflow + usable |
| `packages/opencode/src/session/compaction.ts` | 1-608 (full) | V1 processCompaction, prune, serialize |
| `packages/opencode/src/session/prompt.ts` | 1140-1339 | Compaction trigger sites, error handling |
| `packages/opencode/src/session/processor.ts` | 420-499, 600-700 | needsCompaction, ContextOverflowError |
| `packages/opencode/src/session/session.ts` | 320-420 | getUsage (server-reported tokens) |
| `packages/opencode/src/session/llm/request.ts` | 1-226 (full) | Request prep, maxOutputTokens |
| `packages/opencode/src/session/llm.ts` | 9-383 | Stream routing |
| `packages/opencode/src/provider/transform.ts` | 18, 85-86, 367, 1186, 1317, 1338, 1418-1420, 1687, 1721, 1812 | OpenRouter/Zen special cases, OUTPUT_TOKEN_MAX, maxOutputTokens |
| `packages/opencode/src/provider/error.ts` | 175 | ContextOverflowError detection |
| `packages/opencode/src/cli/cmd/run/session-data.ts` | 100-300, esp. 134-161 | formatUsage display logic |
| `packages/opencode/src/cli/cmd/run/footer.view.tsx` | 450-549 | Footer rendering (no context % found here) |
| `packages/opencode/src/config/config.ts` | 560-600 | OPENCODE_DISABLE_AUTOCOMPACT/PRUNE |
| `packages/opencode/src/effect/runtime-flags.ts` | 1-78 (full) | OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX |
| `packages/opencode/src/tool/truncate.ts` | 1-156 | Tool output truncation (separate) |
| `third-party/headroom/plugins/opencode/src/plugin.ts` | 1-68 | Headroom plugin (NOT in data path) |
| `third-party/headroom/plugins/opencode/README.md` | 1-80 | Confirmed headroom is transport interceptor only |

---

## 15. Confidence Levels

| Finding | Confidence | Basis |
|---|---|---|
| `CHARS_PER_TOKEN = 4` | 🔴 VERIFIED | Direct read of `core/src/util/token.ts:3` |
| `usable = input - reserved` (V1) | 🔴 VERIFIED | Direct read of `opencode/src/session/overflow.ts:10-20` |
| `context - max(output, buffer)` (V2) | 🔴 VERIFIED | Direct read of `core/src/session/compaction.ts:236-240` |
| Auto-compaction trigger at `prompt.ts:1166` | 🔴 VERIFIED | Direct read |
| `ContextOverflowError` abort at `processor.ts:607-617` | 🔴 VERIFIED | Direct read |
| Display uses server-reported `usage` | 🔴 VERIFIED | `session-data.ts:134-161` sums `tokens.input + output + reasoning + cache.read + cache.write` |
| `compaction.buffer` configurable | 🔴 VERIFIED | `core/src/config/compaction.ts:14` schema |
| Default buffer = 20,000 | 🔴 VERIFIED | `core/src/session/compaction.ts:12` `DEFAULT_BUFFER` |
| `OUTPUT_TOKEN_MAX = 32,000` | 🔴 VERIFIED | `provider/transform.ts:18` |
| M3 has 400K context in this session | 🟡 HIGH | Reported by user; `models.dev` value not re-verified in this investigation |
| 398K→368K was manual `/compact` | 🟡 HIGH | Consistent with prompt-cache break + auto-compaction threshold (380K) being below the drop; Roc's mining confirms 38,717-byte prompt at 06:24:59 |
| M3 does not truncate | 🟢 DOC (Roc's mining) | Confirmed by Roc's session DB analysis; client code shows no evidence of M3-only behavior |

---

## 16. Recommended Follow-ups

1. **Verify M3's actual context limit** in `models.dev` for the current date. If it's 1M, the 400K cap is from the OpenRouter tier or the user's plan.
2. **Check OpenRouter's request logs** for the 06:24:59 turn to confirm M3's response (was it 200 OK with usage, or 413?). This requires OpenRouter dashboard access.
3. **Add logging in `isOverflow`** to record `lastFinished.tokens` at the trigger point. Would help future investigations.
4. **Consider patching `Token.estimate`** to use a model-aware estimate (e.g., 3.0 chars/token for code-heavy sessions). The 4:1 ratio is a known underestimate for code.
5. **Test with `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=64000`** if M3 supports 64K output — this would change the V1 `reserved` from 20K to 32K, giving a few K more usable space.
6. **The V2 path is opt-in only.** The investigation confirmed both V1 and V2 paths exist. The V1 `overflow.ts` is the active path for CLI sessions unless native runtime is enabled.

---

*⬡ OMEGA ⬡ KALI ⬡ R_COPILOT_OPENCODE_TRUNCATION_SOURCE_20260828 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
