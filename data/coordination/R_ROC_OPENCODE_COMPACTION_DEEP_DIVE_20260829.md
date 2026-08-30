---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "deep_discovery_report"
document_id: "R_ROC_OPENCODE_COMPACTION_DEEP_DIVE_20260829"
title: "OpenCode CLI Compaction Mechanism — Deep Local Discovery"
status: "ACTIVE — Comprehensive Reference"
date: "2026-08-29"
author: "roc_racoon (Sovereign Miner)"
sprint: "PUBLIC-DEBUT-01"
scope: "Local source code at ~/Documents/Xoe-NovAi/omega-engine/opencode/"
confidence: "🟢 HIGH (all claims file:line grounded, two code paths mapped)"
search_targets: [
  "~/.config/opencode/node_modules/@opencode-ai/ (SDK only, no CLI source)",
  "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/ (full source tree — PRIMARY)",
  "Local opencode.json config",
  "Local plugin system"
]
---

# 🔱 R_ROC_OPENCODE_COMPACTION_DEEP_DIVE — OpenCode CLI Compaction Mechanism
**AP Token**: `AP-OPENCODE-COMPACTION-DEEPDIVE-20260829-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_compaction_deep_dive ⬡ COMPLETE

---

## §0 — Executive Summary

OpenCode compaction is a **client-side, pre-flight mechanism** that summarizes conversation history before each LLM call to prevent context overflow. It is NOT server-triggered. The architecture is: **dual-path trigger → agent "compaction" → LLM call → summary injection → tail preservation**. Three plugin hooks allow external shaping. The codebase contains **TWO parallel compaction implementations** (V1 in `packages/opencode/` and V2 in `packages/core/src/session/`) — V1 is the current default, V2 is the new architecture in development.

**Key Finding for Omega**: Compaction model can be set via the `agent.compaction.model` config field. There is no plugin hook to set the model. The plugin hooks give full control over prompt content and message selection.

---

## §1 — Search Targets Verified

| Target | Found? | Notes |
|--------|--------|-------|
| `~/.config/opencode/node_modules/@opencode-ai/` | ⚠️ SDK ONLY | Only the SDK (`@opencode-ai/sdk`) is installed, not the CLI source. Full source must be read from the omega-engine repo. |
| `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode/` | ✅ FULL SOURCE | Complete OpenCode v2 source tree (packages: app, opencode, tui, core, plugin, schema, sdk, etc.) |
| `/home/arcana-novai/.config/opencode/opencode.json` | ✅ LOCAL CONFIG | Contains 6 providers, no custom compaction model |
| `~/.config/opencode/zen_accounts_state.json` | ✅ MISC | Zen account state, unrelated to compaction |

---

## §2 — Architecture Overview: Two Parallel Implementations

### V1 (Current — `packages/opencode/src/session/compaction.ts`)
- The live implementation that the TUI/CLI currently uses
- 608 lines, full-featured
- 3 plugin hooks for shaping
- Uses the SessionV1 message format

### V2 (New — `packages/core/src/session/compaction.ts`)
- The new Effect-native implementation
- 248 lines, leaner
- Uses SessionEvent.Compaction.Started/Delta/Ended events
- Uses SessionMessage with type "compaction" stored in DB
- Driven by V2 runner (`core/src/session/runner/llm.ts`)

### Migration Path
The V2 implementation is being developed under the `core/src/session/runner/` directory and is referenced from V1 code via `buildPrompt` import (`packages/opencode/src/session/compaction.ts:23`). The V1 code uses the V2 prompt builder.

---

## §3 — V1 Implementation Deep Dive

### §3.1 Complete Call Chain (TUI /compact command)

```
User types /compact in TUI
  ↓
TUI Command: "session.compact" (packages/tui/src/routes/session/index.tsx:121)
  ↓
TUI Handler: packages/tui/src/routes/session/index.tsx:562-586
  - Slash alias: "compact" or "summarize"
  - Calls: sdk.client.session.summarize({sessionID, modelID, providerID})
  ↓
SDK: @opencode-ai/sdk session.summarize()
  ↓
HTTP: POST /session/:sessionID/summarize
  Handler: packages/opencode/src/server/routes/instance/httpapi/handlers/session.ts:273-293
  1. revertSvc.cleanup() — discard any staged revert
  2. compactSvc.create() — write user message with "compaction" part
  3. promptSvc.loop() — run session loop
  ↓
Session Loop: packages/opencode/src/session/prompt.ts:1320-1328
  - result === "compact" → call compaction.create()
  ↓
SessionCompaction.create(): packages/opencode/src/session/compaction.ts:559-582
  - Creates a user message with `type: "compaction"` part
  - Sets `auto: false` for manual /compact, `auto: true` for auto
  ↓
SessionCompaction.process() (processCompaction): packages/opencode/src/session/compaction.ts:319-557
  1. Find parent user message (the compaction part)
  2. If overflow, find a "replay" message (the user message that caused overflow)
  3. Get the "compaction" agent and its model
  4. Call select() to split messages into head + tail_start_id
  5. Trigger plugin hook: experimental.session.compacting (allow prompt override)
  6. Trigger plugin hook: experimental.chat.messages.transform (allow message mutation)
  7. Build the compaction prompt (or use plugin-replaced prompt)
  8. Send to LLM via processor.process()
  9. Trigger plugin hook: experimental.compaction.autocontinue (enable/disable auto-continue)
  10. Optionally inject synthetic "Continue if you have next steps" message
  ↓
TUI Display: packages/tui/src/routes/session/index.tsx:1457-1465
  - Renders a "Compaction" banner with top border
```

### §3.2 Auto-Compaction Trigger (Pre-flight)

The pre-flight check happens in `processor.ts:479-481` AFTER each LLM call:
```typescript
if (
  !ctx.assistantMessage.summary &&  // Not itself a compaction
  isOverflow({ cfg: yield* config.get(), tokens: usage.tokens, model: ctx.model })
) {
  ctx.needsCompaction = true
}
```

The overflow detection (`packages/opencode/src/session/overflow.ts:22-34`):
```typescript
export function isOverflow(input) {
  if (input.cfg.compaction?.auto === false) return false  // Disabled
  if (input.model.limit.context === 0) return false       // Unknown limit
  const count = input.tokens.total ||
    (input.tokens.input + input.tokens.output + input.tokens.cache.read + input.tokens.cache.write)
  return count >= usable(input)  // usable = context - maxOutput - reserved
}
```

### §3.3 Overflow Path (Server-Triggered Fallback)

When the provider returns `ContextOverflowError`:
1. `processor.ts:607-617` — catches `ContextOverflowError`
2. Sets `ctx.needsCompaction = true` (unless `compaction.auto === false`)
3. Returns "compact" from `processor.process()`
4. `prompt.ts:1320-1328` calls `compaction.create()` with `overflow: true`

The `overflow: true` flag causes the compaction to:
- Find a "replay" message (the original user request that overflowed)
- Strip media attachments from the replay
- Inject a special auto-continue message about media being too large (compaction.ts:528-530)

---

## §4 — Exact Compaction Prompt/Instructions

### §4.1 System Prompt (`packages/opencode/src/agent/prompt/compaction.txt`, 5 lines)
```
You are a context summarization agent. You are given a conversation between a user and an agent.
Your goal is to produce a structured summary matching the format specified so another coding agent
can continue the work.

Always follow the exact output structure requested by the user prompt. Keep every section, preserve
exact file paths and identifiers when known, and prefer terse bullets over paragraphs.

Do not continue the conversation. Do not respond to any questions in the conversation. Only output
the structured summary in the exact format requested by the user prompt. Respond in the same
language as the conversation.
```

### §4.2 User Prompt Template (V2 core — `packages/core/src/session/compaction.ts:16-46`)

**First compaction** (no prior summary):
```
Here is the conversation so far:

<conversation>
{serialized messages}
</conversation>

Create a new anchored summary from the conversation history in the <conversation> tags above
so another coding agent can continue the work.

{SUMMARY_TEMPLATE}
```

**Subsequent compactions** (has prior summary):
```
Here is the conversation so far:

<conversation>
{serialized messages}
</conversation>

Here is the summary of the conversation before the <conversation> above:

<prior-summary>
{previous summary text}
</prior-summary>

{SUMMARY_UPDATE_INSTRUCTIONS}

{SUMMARY_TEMPLATE}
```

### §4.3 SUMMARY_TEMPLATE (the output structure)
```markdown
## Objective
- [one or two brief sentences describing what the user is trying to accomplish]

## Important Details
- [constraints/preferences, decisions and why, important facts/assumptions, exact context needed
  to continue, or "(none)"]

## Work State
### Completed
- [finished work, verified facts, or changes made; otherwise "(none)"]

### Active
- [current work, partial changes, or investigation state; otherwise "(none)"]

### Blocked
- [blockers, failing commands, or unknowns; otherwise "(none)"]

## Next Move
1. [immediate concrete action, or "(none)"]
2. [next action if known, or "(none)"]

## Relevant Files
- [file or directory path: why it matters, or "(none)"]
```

### §4.4 SUMMARY_UPDATE_INSTRUCTIONS (for merging with prior summary)
```
The <prior-summary> summarizes everything that happened before the <conversation>. Construct a new
summary that combines both. The <prior-summary> is discarded after this: anything you do not carry
into the new summary is lost.

When combining:
- Carry forward objectives, constraints, user directives, decisions, and parallel workstreams from
  the <prior-summary> even when the <conversation> does not mention them. Drop only what is finished
  and no longer needed.
- The <conversation> is more recent than the <prior-summary>. Where they conflict, the conversation
  wins: state the corrected fact and drop the old claim.
- Add new progress, decisions, constraints, and context from the conversation.
- Move completed work from "Active" to "Completed".
- If a blocker has been resolved, update the summary to reflect that while keeping any details still
  needed to continue the work.
- Update "Objective" and "Next Move" to reflect the current work state.
```

### §4.5 Rules
- Keep every section, even when empty
- Use terse bullets, not prose paragraphs
- Preserve exact file paths, symbols, commands, error strings, URLs, and identifiers
- Do not mention the summary process or that context was compacted

### §4.6 Serialization Format
Messages are serialized as:
- `[User]: {text}` + `[Attached {mime}: {name}]` for user messages
- `[Assistant]: {text}` for assistant text
- `[Assistant reasoning]: {text}` for reasoning
- `[Assistant tool call]: {name}({input})` + `[Tool result]: {truncated output}` for tool calls
- `[Tool error]: {error}` for failed tool calls
- Tool output truncated at **2,000 chars** (`TOOL_OUTPUT_MAX_CHARS`)

---

## §5 — Where Compaction Model Is Configured

### §5.1 Model Selection Logic (`packages/opencode/src/session/compaction.ts:358-361`)
```typescript
const agent = yield* agents.get("compaction")
const model = agent.model
  ? yield* provider.getModel(agent.model.providerID, agent.model.modelID)
  : yield* provider.getModel(userMessage.model.providerID, userMessage.model.modelID)
```

**Priority order**:
1. If the `compaction` agent has a `model` field in its config → use that model
2. Otherwise → use the **same model as the user's active session**

### §5.2 How to Set a Different Compaction Model

**Option A: Agent config in `opencode.json`** (RECOMMENDED)
```json
{
  "agent": {
    "compaction": {
      "model": "openai/gpt-4o-mini"
    }
  }
}
```
This sets `agent.model = { providerID: "openai", modelID: "gpt-4o-mini" }` which the compaction code checks at line 359.

**Option B: Per-project agent markdown files**
Create `.opencode/agents/compaction.md` with a `model:` frontmatter field. The `ConfigAgent.load()` system picks up agent definitions from `agent/*.md` or `agents/*.md` patterns.

**Option C: The `small_model` config** ⚠️ **DOES NOT WORK FOR COMPACTION**
```json
{ "small_model": "openai/gpt-4o-mini" }
```
`small_model` is used for **title generation** and **debug agent** resolution — NOT for compaction. The compaction agent does NOT call `getSmallModel()`. This is a common misconception.

### §5.3 Compaction Config Schema (`packages/core/src/v1/config/config.ts:149-168`)
```yaml
compaction:
  auto: true                    # Enable automatic compaction (default: true)
  prune: false                  # Enable pruning of old tool outputs (default: false)
  tail_turns: N                 # Max recent user turns to keep verbatim
  preserve_recent_tokens: N     # Max tokens from recent turns to preserve
  reserved: N                   # Token buffer for compaction safety margin
```

### §5.4 Environment Variable Overrides
- `OPENCODE_DISABLE_AUTOCOMPACT` → sets `compaction.auto = false` (config.ts:579-580)
- `OPENCODE_DISABLE_PRUNE` → sets `compaction.prune = false` (config.ts:582-583)

### §5.5 V1 vs V2 Model Resolution
**V1 (current)**: Uses agent.model if set, else user's model (compaction.ts:358-361)
**V2 (new)**: Always uses the input.model parameter (compaction.ts:204) — the model is passed in from the caller, which uses the user's model

---

## §6 — Plugin/Hooks Mechanism for Shaping Compaction

### §6.1 Three Plugin Hooks

#### Hook 1: `experimental.session.compacting`
**File**: `packages/plugin/src/index.ts:305-308`
```typescript
"experimental.session.compacting"?: (
  input: { sessionID: string },
  output: { context: string[]; prompt?: string },
) => Promise<void>
```
**When**: Called BEFORE compaction LLM call, after message selection.
**Power**:
- `output.context.push("extra info")` — appends extra context strings to the prompt
- `output.prompt = "custom prompt"` — **REPLACES the entire default compaction prompt**

**Use case**: Inject domain-specific instructions into the summary (e.g., "Always preserve mandate references", "Flag any security-sensitive content")

#### Hook 2: `experimental.chat.messages.transform`
**File**: `packages/plugin/src/index.ts:282-290`
```typescript
"experimental.chat.messages.transform"?: (
  input: {},
  output: {
    messages: { info: Message; parts: Part[] }[]
  },
) => Promise<void>
```
**When**: Called AFTER `experimental.session.compacting`, BEFORE serialization.
**Power**: Mutate the messages array in-place before they're serialized for the summary prompt.

**Use case**: Redact sensitive content, re-order messages, inject synthetic context messages, strip noise

#### Hook 3: `experimental.compaction.autocontinue`
**File**: `packages/plugin/src/index.ts:316-326`
```typescript
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
**When**: Called AFTER compaction succeeds, BEFORE auto-continue message.
**Power**: Set `output.enabled = false` to prevent the synthetic "Continue if you have next steps" message.

**Use case**: Prevent auto-continue in certain contexts, customize post-compaction behavior

### §6.2 Plugin Registration Pattern
```typescript
// In a plugin file
export function myPlugin(input: PluginInput): PluginInstance {
  return {
    async "experimental.session.compacting"(input, output) {
      output.context.push("## Additional Context\n- Preserve all D-number references")
      // Or replace entirely:
      // output.prompt = "My custom compaction prompt..."
    },
    async "experimental.compaction.autocontinue"(input, output) {
      if (input.overflow) output.enabled = false
    },
  }
}
```

### §6.3 Plugin Examples in Codebase
1. **GitHub Copilot plugin** (`packages/opencode/src/plugin/github-copilot/copilot.ts:355-391`): Uses `experimental.provider.small_model` (not compaction hooks). Checks for `part.type === "compaction"` and `metadata.compaction_continue` to handle auto-continue specially.
2. **Test mocks** (`packages/opencode/test/session/compaction.test.ts:340-380`): Demonstrates all 3 hooks with mock implementations

---

## §7 — Compaction Events & TUI Display

### §7.1 V1 Compaction Events
The V1 implementation publishes:
- `SessionEvent.Compaction.Started` — published at start of compaction (core/session/compaction.ts:192)
- `SessionEvent.Compaction.Delta` — published as text streams in (implied)
- `SessionEvent.Compaction.Ended` — published at end with summary text and recent (core/session/compaction.ts:222)

Schema: `packages/schema/src/session-event.ts:398-432`
```typescript
export namespace Compaction {
  export const Started = Event.define({
    type: "session.next.compaction.started",
    schema: { ..., messageID, reason: "auto" | "manual" },
  })
  export const Delta = Event.define({
    type: "session.next.compaction.delta",
    schema: { ..., messageID, text },
  })
  export const Ended = Event.define({
    type: "session.next.compaction.ended",
    schema: { ..., messageID, reason, text, recent },
  })
}
```

### §7.2 TUI Display
- **During compaction**: TUI shows a "Compaction" banner with top border (routes/session/index.tsx:1457-1465)
- **Data flow**: TUI listens for `session.next.compaction.ended` event and creates a message of `type: "compaction"` in the message list (context/data.tsx:380-390)
- **Status indicator**: `session.time.compacting` flag shows "compacting" status (context/sync.tsx:587)

### §7.3 Message Storage
Compaction messages are stored as user messages with a `compaction` part type:
- `agent: "compaction"` (compaction.ts:399)
- `mode: "compaction"` (compaction.ts:398)
- `summary: true` (compaction.ts:401)
- Part type: `"compaction"` with `auto` and `overflow` fields (compaction.ts:578-580)

---

## §8 — Pruning (Separate from Compaction)

### §8.1 Prune Trigger
Pruning is triggered at the END of the prompt loop (`prompt.ts:1338`):
```typescript
yield* compaction.prune({ sessionID }).pipe(Effect.ignore, Effect.forkIn(scope))
```

### §8.2 Prune Logic (`packages/opencode/src/session/compaction.ts:273-317`)
1. Check `cfg.compaction?.prune` — if false, skip
2. Get all messages for session
3. Walk backwards through messages, skipping the last 2 user turns
4. For each assistant tool part (except "skill"):
   - If completed and not already compacted
   - Accumulate estimated tokens
   - If total > PRUNE_PROTECT (40,000), add to prune list
5. If total pruned > PRUNE_MINIMUM (20,000):
   - For each part in prune list, set `part.state.time.compacted = Date.now()`
   - This marks the output as cleared (the actual text is preserved but marked)
6. Tool output display: `[Old tool result content cleared]` (compaction.ts:77)

### §8.3 Prune vs Compact Relationship
- Prune: Marks old tool outputs as "cleared" (preserves the fact, removes the content)
- Compact: Summarizes the entire conversation into a new message
- They are complementary: prune frees space cheaply, compact is more expensive but preserves intent
- Prune runs after every prompt completion, compact runs only on overflow

---

## §9 — V2 Implementation (New Architecture)

### §9.1 Key Differences from V1
- Uses SQLite-backed event sourcing (`packages/core/src/session/history.ts`)
- Compaction messages are stored as rows in `SessionMessage` table with `type: "compaction"`
- Uses `baselineSeq` to track "what was the last compaction boundary"
- `latestCompaction(db, sessionID)` queries the most recent compaction
- More event-driven, less imperative

### §9.2 V2 Compact If Needed Flow (`core/src/session/compaction.ts:232-243`)
```typescript
const compactIfNeeded = function* (input: Input) {
  if (!config.auto) return false
  const context = input.model.route.defaults.limits?.context
  if (!context) return false
  const output = input.request.generation?.maxTokens ?? input.model.route.defaults.limits?.output ?? 0
  if (estimate({...}) <= context - Math.max(output, config.buffer)) return false
  return yield* compactAfterOverflow(input)
}
```

### §9.3 V2 Turn Transition Errors
V2 uses `TurnTransitionError` to signal post-compaction continuation:
- `ContinueAfterCompaction` — automatic compaction completed, rebuild request
- `ContinueAfterOverflowCompaction` — overflow compaction completed, rebuild without overflow recovery

### §9.4 V2 Plugin Hook Status
**V2 has NO plugin hooks for compaction shaping.** It is purely internal to core. Only V1 has the 3 plugin hooks.

---

## §10 — Constants & Limits

| Constant | Value | Location |
|----------|-------|----------|
| `DEFAULT_BUFFER` | 20,000 tokens | `core/session/compaction.ts:12` |
| `DEFAULT_KEEP_TOKENS` | 8,000 tokens | `core/session/compaction.ts:13` |
| `TOOL_OUTPUT_MAX_CHARS` | 2,000 chars | `core/session/compaction.ts:14` |
| `SUMMARY_OUTPUT_TOKENS` | 4,096 tokens | `core/session/compaction.ts:15` |
| `COMPACTION_BUFFER` | 20,000 tokens | `overflow.ts:8` |
| `CHARS_PER_TOKEN` | 4 | `core/util/token.ts:3` |
| `PRUNE_MINIMUM` | 20,000 tokens | `packages/opencode compaction.ts:28` |
| `PRUNE_PROTECT` | 40,000 tokens | `packages/opencode compaction.ts:29` |
| `MIN_PRESERVE_RECENT_TOKENS` | 2,000 tokens | `packages/opencode compaction.ts:32` |
| `MAX_PRESERVE_RECENT_TOKENS` | 15,000 tokens | `packages/opencode compaction.ts:33` |

---

## §11 — Token Estimation

**Formula** (`packages/core/src/util/token.ts:3-5`):
```typescript
const CHARS_PER_TOKEN = 4
export const estimate = (input: string) => Math.max(0, Math.round(input.length / CHARS_PER_TOKEN))
```

**Implication**: Token estimates are approximate (1 token ≈ 4 chars). This is used for:
- Overflow detection (preflight)
- `select()` budget calculation
- `splitTurn()` size estimation
- Prune accumulation

**This is NOT used for**: LLM billing, actual prompt size sent to provider (provider calculates its own tokens)

---

## §12 — Revert/Undo Relationship

### §12.1 Cleanup Before Compaction
`summarize` handler calls `revertSvc.cleanup()` BEFORE creating the compaction (`session.ts:277`). This means:
- If user had a staged revert, it is discarded when compaction starts
- You cannot revert a compaction back to pre-compaction state via /undo

### §12.2 What Revert Does
- `SessionRevert.revert()` — creates a snapshot, allows reverting file changes
- `SessionRevert.unrevert()` — restores the snapshot
- These are file-level reverts, NOT message-level reverts
- The session/revert-compact.test.ts test covers the workflow: revert → compact → verify

### §12.3 Impact
If you revert and then compact, the revert state is lost. This is by design: compaction creates a new "anchor point" that supersedes any prior revert state.

---

## §13 — Critical Gaps and Areas Needing Further Discovery

### §13.1 Gaps in This Report
1. **V2 compaction is not fully tested in production** — it's in development. Behavior may differ.
2. **No information on what `tail_turns` does in edge cases** — what if a turn is too large?
3. **No information on how compaction interacts with subagents** — they use the same SessionMessage format but separate sessions.
4. **No information on how compaction affects `/undo`** — the test file exists but the production behavior is not fully explored.
5. **The V2 implementation's `splitTurn` function** is referenced but not deeply analyzed.

### §13.2 Areas Needing Further Research (Outside Today's Scope)

1. **Empirical testing of compaction model behavior**:
   - How does GLM 5.3 Flash perform as compaction model vs M3?
   - Does a different compaction model produce better summaries?
   - What's the latency difference?

2. **Compaction quality analysis**:
   - Is the SUMMARY_TEMPLATE effective for all agent types?
   - Should we customize the template for build agents vs. exploration agents?

3. **The V1 → V2 migration timeline**:
   - When will V2 replace V1?
   - Will V2 have plugin hooks?
   - What's the migration path for existing plugins?

4. **Interaction with vault/credential systems**:
   - Does the compaction redaction hook actually prevent secret leaks?
   - Has there been a security audit of the compaction LLM call?
   - Are there prompt injection risks via user messages?

5. **Compaction in subagents**:
   - Do subagents compact independently?
   - Is there any coordination between parent and child compaction?

6. **The `revert` + `compact` edge cases**:
   - What happens if you revert, then compact, then try to undo the revert?
   - Are there any test gaps?

7. **Performance benchmarking**:
   - How long does a typical compaction take?
   - What's the token overhead?
   - Can we batch multiple compactions?

8. **The `prune` interaction with tools that produce large outputs**:
   - Does prune affect `bash` output? `read` output? `webfetch` output?
   - Are there tools that should NEVER be pruned?

9. **The TUI behavior during compaction**:
   - What does the user see during a 30-second compaction?
   - Is there a progress indicator?
   - Can the user cancel a compaction in progress?

10. **Compaction in the Desktop app**:
    - Does the desktop app use the same compaction?
    - Are there any desktop-specific overrides?

11. **The `OPENCODE_DISABLE_AUTOCOMPACT` environment variable**:
    - Where is it set? (config.ts:579-580)
    - Is it documented? (not in env file)
    - Are there any other undocumented env vars?

12. **The `compaction_continue` metadata flag**:
    - Used by GitHub Copilot plugin (copilot.ts:391)
    - What's the full contract? (marked as "not a stable plugin contract" at compaction.ts:540)

13. **The `agent.compaction.options` field**:
    - Schema includes `options: Schema.Record(Schema.String, Schema.Unknown)` (agent.ts:53)
    - What options can be passed to the compaction model?
    - Are they forwarded to the LLM call?

14. **The `variant` field in compaction**:
    - Set as `userMessage.model.variant` (compaction.ts:400)
    - What variants exist? (e.g., "low", "high", "max" in the local config)
    - Does the compaction respect the variant?

15. **The `EventV2Bridge`**:
    - `EventV2Bridge` service is injected in compaction layer (compaction.ts:200)
    - What does it bridge?
    - Is this for V1 → V2 event compatibility?

---

## §14 — Omega Integration Implications

### §14.1 What Omega CAN Do With Existing Hooks
1. **Inject mandate references** via `experimental.session.compacting` context — ensure Omega mandates survive compaction
2. **Inject sovereignty lineage** via context — track entity identity across compactions
3. **Redact vault secrets** via `experimental.chat.messages.transform` — scrub credential mentions before summary
4. **Prevent auto-continue** in certain contexts via `experimental.compaction.autocontinue`

### §14.2 What Omega CANNOT Do (Gaps)
1. **Cannot change compaction model via plugin** — only via agent config (`agent.compaction.model`)
2. **Cannot control summary token budget** — hardcoded at 4,096 tokens
3. **Cannot inject system prompt** into the compaction LLM call — only via prompt replacement
4. **Cannot access the raw summary output** — only the serialized input is hookable
5. **No compaction event hook** — no way to react AFTER summary is generated but BEFORE it's stored
6. **V2 has no plugin hooks** — only V1 is hookable
7. **No way to set a different compaction model per-session** — only globally via config

### §14.3 Recommended Omega Plugin Design
```typescript
const omegaCompactionPlugin: PluginInstance = {
  async "experimental.session.compacting"(input, output) {
    // 1. Inject current entity context
    output.context.push(
      `\n## Sovereign Context\n- Entity: ${currentEntity}\n- Session: ${input.sessionID}\n`
    )
    // 2. Inject active mandates summary
    output.context.push(
      `\n## Active Mandates\n${formatActiveMandates()}\n`
    )
    // 3. Flag security-sensitive patterns for preservation
    output.context.push(
      `\n## Preservation Directives\n- Preserve all D-number references\n- Preserve all mandate IDs (M1-M28)\n- Preserve all credential references (but do NOT expand them)\n`
    )
  },
  async "experimental.chat.messages.transform"(input, output) {
    // 4. Redact vault/credential references from messages before summarization
    for (const msg of output.messages) {
      for (const part of msg.parts) {
        if (part.type === "text") {
          part.text = redactSecrets(part.text)
        }
      }
    }
  },
  async "experimental.compaction.autocontinue"(input, output) {
    // 5. Disable auto-continue if this was an overflow compaction
    // (user should re-issue their request)
    if (input.overflow) output.enabled = false
  },
}
```

### §14.4 Recommended Compaction Model Configuration
```json
{
  "agent": {
    "compaction": {
      "model": "openai/gpt-4o-mini",
      "variant": "low"
    }
  }
}
```
This would use GPT-4o-mini for compaction regardless of the user's active model, potentially saving costs.

---

## §15 — Cross-References

- **R_ROC_CONTEXT_MINING_CORRECTED_20260828.md** — Context overflow behavior, TUI formula
- **R_COPILOT_ALL_COMPACTION_PATHS_20260828.md** — Industry compaction patterns
- **R_ANTIGRAVITY_OPENCODE_INDUSTRY_COMPACTION_20260828.md** — OpenCode V2 architecture
- **R_CARMACK_OPENCODE_ARCHITECTURE_BOUNDARY_20260828.md** — Engine-stack boundary
- **M3_SURVIVAL_ECONOMICS_20260828.md** — M3 context window analysis

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_compaction_deep_dive ⬡ COMPLETE*