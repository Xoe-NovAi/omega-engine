# R_RESEARCHER — OpenCode `task` Tool Model Resolution & Inheritance

**Author:** @researcher (Sovereign Researcher, Jem Analyst — Polymathic Council mode)
**Date:** 2026-08-28
**Sprint:** PUBLIC-DEBUT-01
**Source query:** GROKSTER handoff `ses_fe8cf0b39ffeL3L8eaMEj3CW9H`
**Mode:** Research only — NO code changes. Per Architect mandate: *"Stop fuckin changing code."*

---

## 1. Executive Summary

1. **The smoking gun is `opencode/packages/opencode/src/tool/task.ts:181-184`**. If a subagent's agent config (`.md` or `opencode.json`) has no `model:` field, the subagent inherits the **parent's CURRENT assistant message's model** — not a default and not the parent's primary agent model. Line 181: `const model = next.model ?? { modelID: msg.info.modelID, providerID: msg.info.providerID }`.

2. **`msg.info.modelID` is the model the parent is *currently using* for the turn that invoked the `task` tool** (verified via `task.ts:174-179` + `schema/src/v1/session.ts:462-463`). It is whatever model produced the most recent assistant message in the parent's session, which is whatever the user selected via `/model` in the TUI (or whatever the server resolved on the most recent prompt — see Section 4).

3. **The TUI `/model` command updates `state.model` in `cli/cmd/run/runtime.ts:289`**, which is then sent on every subsequent prompt via `stream.transport.ts:1286` as `"providerID/modelID"`. The server stores it on the new `Assistant` row (`session-v1.ts:462-463`). On the next `task()` call, `task.ts:182` reads that row back. Inheritance is **reactive to the parent's most recent turn**, not the original TUI selection.

4. **The `qwen3-1.7b` bug root cause**: when a parent session has *no* `model:` on the calling agent AND the parent's last assistant message is a local fallback (e.g. the parent itself was launched by a subagent that fell back to `provider.defaultModel()`), the chain cascades. `Provider.defaultModel()` (`provider.ts:2003-2034`) ultimately picks the first configured provider's first model via `sort()` with priority list `["gpt-5", "claude-sonnet-4", "big-pickle", "gemini-3-pro"]` (line 2042) — if `qwen3` is the only configured provider and `qwen3-1.7b` is its only model, that's the default.

5. **The three config files have a clear precedence** — global (`~/.config/opencode/opencode.json[ c]`) → per-project walk-up (`ConfigPaths.files`, `paths.ts:10-21`) → per-directory `.opencode/opencode.json[ c]` and `.opencode/agent/*.md`. All are deep-merged with `remeda.mergeDeep` (`config.ts:42, 460`). Agent `.md` frontmatter applies *only to that agent*; removing `model:` from a custom agent .md forces inheritance from the parent turn.

---

## 2. Full Model Resolution Chain (file:line evidence)

### Step 1: User issues a prompt (or subagent `task()` runs)

The prompt arrives at the server. The server reads `PromptInput.model` if provided, else falls back through three levels in `opencode/packages/opencode/src/session/prompt.ts:646`:

```ts
const model = input.model ?? ag.model ?? (yield* currentModel(input.sessionID))
```

| Order | Source | File:line | When it wins |
|-------|--------|-----------|--------------|
| 1 | `input.model` (explicit on the prompt call) | `prompt.ts:646` | TUI sent `state.model` (`runtime.ts:652` → `stream.transport.ts:1286`) |
| 2 | `ag.model` (agent's own configured `model:` field) | `prompt.ts:646` | Agent .md or `cfg.agent[name].model` set this |
| 3 | `currentModel(sessionID)` | `prompt.ts:600-633` | Fallback — see below |

`currentModel()` resolution (`prompt.ts:615-632`):

```ts
const current = yield* db.select({ model: SessionTable.model })
  .from(SessionTable).where(eq(SessionTable.id, sessionID)).get()
if (current?.model) { return { providerID, modelID, variant } }
const match = yield* sessions.findMessage(sessionID, 
  (m) => m.info.role === "user" && !!m.info.model)
if (Option.isSome(match) && match.value.info.role === "user") 
  return match.value.info.model
return yield* provider.defaultModel().pipe(Effect.orDie)  // ← line 632
```

| Sub-step | Source | File:line |
|----------|--------|-----------|
| 3a | `SessionTable.model` (last user msg's resolved model) | `prompt.ts:621-627` |
| 3b | Walk history for the last user message with a `model` field | `prompt.ts:628-631` |
| 3c | `provider.defaultModel()` | `prompt.ts:632` → `provider.ts:2003-2034` |

### Step 2: `provider.defaultModel()` chain (`provider.ts:2003-2034`)

```ts
const defaultModel = Effect.fn("Provider.defaultModel")(function* () {
  const cfg = yield* config.get()
  if (cfg.model) return parseModel(cfg.model)                            // line 2005

  const s = yield* InstanceState.get(state)
  const recent = yield* fs.readJson(path.join(Global.Path.state, "model.json"))  // line 2008
    .pipe(Effect.map(...), Effect.catch(...))
  for (const entry of recent) {                                         // line 2020
    const provider = s.providers[entry.providerID]
    if (!provider) continue
    if (!provider.models[entry.modelID]) continue
    return { providerID: entry.providerID, modelID: entry.modelID }
  }

  const configured = Object.keys(cfg.provider ?? {})                    // line 2027
  const provider = Object.values(s.providers).find(
    (p) => configured.length === 0 || configured.includes(p.id))
  if (!provider) return yield* new NoProvidersError()
  const [model] = sort(Object.values(provider.models))                  // line 2030
  if (!model) return yield* new NoModelsError({ providerID: provider.id })
  return { providerID: provider.id, modelID: model.id }
})
```

| Tier | Source | File:line | Note |
|------|--------|-----------|------|
| a | `cfg.model` (top-level `model: "provider/id"` in any config) | `provider.ts:2005` | Strongest — set via `opencode.json` or CLI flag |
| b | `~/.local/state/opencode/model.json#recent[0]` | `provider.ts:2008-2025` | **DEAD — `recent` is never written in this codebase** (only read; see §7 Knowledge Gaps) |
| c | First configured provider's first model via `sort()` | `provider.ts:2027-2034` | Uses priority list at `provider.ts:2042`: `["gpt-5", "claude-sonnet-4", "big-pickle", "gemini-3-pro"]` then `latest` preference, then alphabetical `desc` |

### Step 3: `parseModel(string)` for the `model:` agent field

```ts
// provider.ts:2053-2059
export function parseModel(model: string) {
  const [providerID, ...rest] = model.split("/")
  return {
    providerID: ProviderV2.ID.make(providerID),
    modelID: ModelV2.ID.make(rest.join("/")),
  }
}
```

The string `"anthropic/claude-sonnet-4-5"` becomes `{ providerID: "anthropic", modelID: "claude-sonnet-4-5" }`. Same logic applies in `cli/cmd/run.ts:31-38` (`pick(value)`) for the CLI `--model` flag.

### Step 4: Where the agent's `model` field is set (`agent.ts:267-294`)

The agent config map is built by `Agent.Service` layer in `opencode/packages/opencode/src/agent/agent.ts`. The `agent.ts:281` line is the *only* place user-supplied model strings are turned into typed `{ providerID, modelID }` for the agent registry:

```ts
for (const [key, value] of Object.entries(cfg.agent ?? {})) {
  // ...
  if (value.model) item.model = Provider.parseModel(value.model)  // line 281
  // ...
}
```

If `value.model` is falsy (no `model:` in the agent .md or opencode.json entry), `item.model` stays `undefined`. The `Info` schema makes `model` optional:

```ts
// agent.ts:35-55
export const Info = Schema.Struct({
  // ...
  model: Schema.optional(
    Schema.Struct({
      modelID: ModelV2.ID,
      providerID: ProviderV2.ID,
    }),
  ),
  // ...
})
```

This `undefined` is the **required precondition** for the inheritance in `task.ts:181`.

### Step 5: The `task` tool inherits from the parent's CURRENT turn

```ts
// task.ts:174-184
const msg = yield* MessageV2.get({ sessionID: ctx.sessionID, messageID: ctx.messageID })
if (msg.info.role !== "assistant") return yield* Effect.fail(new Error("Not an assistant message"))
const variant = msg.info.variant

const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

- `ctx.sessionID` = the **parent session ID** (passed to the tool via the parent prompt's context).
- `ctx.messageID` = the **parent's currently-executing assistant message** (the one invoking `task`).
- `msg.info.modelID` / `msg.info.providerID` = the model stored on that assistant row when the parent generated its turn.
- `next.model` = the subagent's own configured model from `cfg.agent[next.name].model`, resolved by `agent.ts:281`.

**Inheritance rule:** `next.model ?? { msg.info.modelID, msg.info.providerID }`. If the subagent .md *omits* `model:`, it gets the parent's CURRENT model — not a global default, not the parent's primary agent's configured model.

The same model is then passed to the subagent's prompt call at `task.ts:202-212`:

```ts
const result = yield* ops.prompt({
  messageID: MessageID.ascending(),
  sessionID: nextSession.id,
  model: { modelID: model.modelID, providerID: model.providerID },
  variant: next.model ? undefined : variant,   // ← line 209
  agent: next.name,
  parts,
})
```

`variant` is similarly inherited from the parent unless the subagent explicitly configured a `model:` (line 209).

---

## 3. Inheritance from Parent's Active Model — VERIFIED

**Claim:** If the Architect removes `model:` from an agent .md and launches that subagent, the subagent gets the Architect's **current turn's model** — which is the most recent assistant message in the parent session.

**Evidence chain (5-step proof):**

1. `task.ts:181-184` — `next.model ?? { modelID: msg.info.modelID, providerID: msg.info.providerID }`. This is the only place subagent model is resolved.
2. `task.ts:174-177` — `msg` is fetched via `MessageV2.get({ sessionID: ctx.sessionID, messageID: ctx.messageID })`. `ctx.sessionID` is the parent's session; `ctx.messageID` is the assistant message that's calling `task` (provided by the tool registry, not user input).
3. `task.ts:178` — `if (msg.info.role !== "assistant") return yield* Effect.fail(new Error("Not an assistant message"))` — explicitly requires this to be the parent's current assistant turn.
4. `schema/src/v1/session.ts:462-463` — the `Assistant` schema has `modelID: Model.ID, providerID: Provider.ID` as *required* fields. Every assistant message has these baked in at write time, immutable thereafter.
5. `cli/cmd/run/runtime.ts:289` — `state.model = model` is the only place the TUI's `/model` selection mutates the active model. The next `runPromptTurn` (`runtime.ts:652`) sends `state.model` to the server; the server stores it on the new assistant message; on the very next `task()` invocation, `task.ts:182` reads it back.

**Conclusion:** Inheritance is **reactive, not static**. If the Architect is on Nemotron 3 Ultra and types `/model anthropic/claude-sonnet-4-5` then runs the subagent, the subagent gets `claude-sonnet-4-5`. If they switch back to Nemotron 3 Ultra and run another subagent, that one gets Nemotron 3 Ultra. The "parent's active model" is whatever the parent last produced.

**Edge case:** If the parent is a fresh session with no prior assistant messages when the first `task()` runs (i.e. the user message itself invokes `task`), `msg.info` is still well-formed — the model on the assistant row is whatever the user prompted with, even for the first turn (the model is resolved at prompt-admit time per `prompt.ts:646` and stored on the new assistant row as it streams).

**No self-reference**: `task.ts:181` uses `next.model`, not `ag.model`. The `ag` (parent's primary agent) is *not* consulted. The Architect could be on `build` agent with no `model:` field, but the parent is currently using `claude-sonnet-4-5` (because the TUI set `state.model` on the prior turn), and the subagent will get `claude-sonnet-4-5`, not `build`'s `provider.defaultModel()` fallback.

---

## 4. The TUI `/model` Command — How Model Selection Works

### 4.1 The user-facing flow

1. The user types `/model` (or hits the model keybind). This opens the model picker UI.
2. The picker lists providers/models from `providers()` SDK call (`runtime.boot.ts:98-111`).
3. On selection, the picker invokes `footer.handleModelSelect(model)` (`footer.ts:819-864`).
4. `handleModelSelect` updates local footer state via `setCurrentModel(model)` (line 825) and calls `options.onModelSelect(model)` (line 830).
5. The `onModelSelect` callback lives in `runtime.ts:284-310`:

```ts
onModelSelect: async (model) => {
  if (state.model?.providerID === model.providerID 
      && state.model.modelID === model.modelID) {
    return
  }
  state.model = model                                  // ← line 289
  state.activeVariant = undefined
  state.variants = variantsFor(state.providers, model)
  const switching = resolveSavedVariant(model).then((saved) => {
    // ... resolves the saved variant for this provider/model pair from model.json
    state.activeVariant = resolveVariant(ctx.variant, undefined, saved, state.variants)
  })
  state.switching = switching
  await switching
  // ...
}
```

This is the **single point of mutation** for the user's current model.

### 4.2 How the model reaches the server

On every prompt turn (`runtime.ts:640-661`):

```ts
run: async (prompt, signal) => {
  // ...
  const next = await ensureStream()
  await next.handle.runPromptTurn({
    agent: state.agent,
    model: state.model,           // ← line 652, passed to stream transport
    variant: state.activeVariant,
    prompt,
    files: input.files,
    // ...
  })
  // ...
}
```

`stream.transport.ts:1286` then formats it as a string and sends to the SDK:

```ts
input.sdk.session.command({
  sessionID: input.sessionID,
  // ...
  model: next.model ? `${next.model.providerID}/${next.model.modelID}` : undefined,
  // ...
})
```

(Same code path for `session.prompt` — line 1224/1250 of `stream.transport.ts`.)

### 4.3 How the server stores it

The server's `SessionPrompt.prompt` (via `prompt.ts:646`) resolves the model and writes the new `Assistant` row with `modelID`/`providerID` set (`session-v1.ts:453-485`).

### 4.4 How it propagates to subagents

The next `task()` call reads `msg.info.modelID` from the most recent assistant row (`task.ts:181-184`). The cycle is closed.

### 4.5 The variant sub-system (related)

Variants are persisted in `~/.local/state/opencode/model.json#variant` (`variant.shared.ts:19, 158-188`). The `recent` array (line 2008-2025) is **read but never written** in this codebase (see §7). Variant is selected per provider/model key.

---

## 5. Why `qwen3-1.7b` — Root Cause Analysis

### 5.1 The visible symptom

Verity (or another subagent) was launched via `task(subagent_type="verity")` from a parent session. Verity's `.md` had no `model:` field. Verity landed on `qwen3-1.7b` (local).

### 5.2 The cascade (most likely path)

1. The Architect (parent) had a previous turn where its assistant row's `modelID` was `qwen3-1.7b` (or the Architect never explicitly picked a model and `provider.defaultModel()` had cascaded to `qwen3-1.7b` as the only available provider).
2. The Architect issued a prompt that invoked `task(subagent_type="verity")`.
3. `task.ts:174-184` ran. `next.model` was `undefined` (Verity .md had no `model:`). The fallback used `msg.info.modelID = "qwen3-1.7b"`.
4. Verity ran on `qwen3-1.7b` even though the user intended (say) `claude-sonnet-4-5`.

### 5.3 Why `qwen3-1.7b` specifically (not anything else)

`Provider.defaultModel()` (`provider.ts:2003-2034`) tiers:
- `cfg.model` (set? unlikely in our project)
- `recent[0]` (always empty — see §7)
- First provider's first model via `sort()`

`sort()` (`provider.ts:2042-2051`) uses the priority list:

```ts
const priority = ["gpt-5", "claude-sonnet-4", "big-pickle", "gemini-3-pro"]
```

If none of the provider's model IDs match the priority substrings, the result is `[model.id, "asc"]` alphabetical sort *descending* applied via `sortBy(..., "desc")`. So among remaining models, the alphabetically last wins.

For a local `qwen3` provider offering `qwen3-1.7b`, `qwen3-4b`, `qwen3-32b`, etc., the alphabetical-desc winner is `qwen3-4b` — but if only `qwen3-1.7b` is configured/visible, that's the one.

### 5.4 Verification of the cascade

To verify whether the parent was on `qwen3-1.7b` at the time of the `task()` invocation, the Architect should inspect the most recent assistant message in the parent session row in `~/.local/share/opencode/opencode.db` (or via `opencode-sessions-explorer-get-message`). The `modelID` field is canonical.

### 5.5 Other plausible root causes (not yet ruled out)

- **The parent itself was a subagent that inherited `qwen3-1.7b` from a grandparent** — recursive fallback. The same `task.ts:181` logic applies at every level.
- **A `default_agent` config**: `agent.ts:328-340` resolves `defaultInfo()` from `cfg.default_agent`. If `default_agent: "qwen3-1.7b-default"` is set and the user's first prompt went through the default-agent path, it could land on a qwen3 model. But the question is `modelID`, not `agent`, so this would have to be a `model:` set on that default agent.
- **Session restoration**: `SessionTable.model` (`prompt.ts:621-627`) is read first in `currentModel()`. If a session was forked/resumed and the stored `SessionTable.model` is a qwen3 model, that wins over the user's `/model` selection for the first turn. After the first new assistant message writes a new model, the cascade settles.

---

## 6. The Three Config Files — Priority and Merging

### 6.1 The three layers

| Layer | Path | Loaded by | File:line |
|-------|------|-----------|-----------|
| **Global** | `~/.config/opencode/opencode.json` (or `.jsonc`, or legacy `config.json`) | `config.ts:139-147, 246-279` | `loadGlobal()` merges in order: `config.json` → `opencode.json` → `opencode.jsonc`; later wins via `mergeDeep` (line 258-260) |
| **Per-project walk-up** | Walked from `cwd` upward to `worktree` looking for `opencode.json` / `opencode.jsonc` | `ConfigPaths.files` → `paths.ts:10-21` | `afs.up({ targets: [...], start: directory, stop: worktree }).toReversed()` — closest to `worktree` last, so it wins |
| **Per-directory `.opencode/`** | `.opencode/opencode.json[ c]`, `.opencode/agent/*.md`, `.opencode/agents/*.md`, `.opencode/mode/*.md`, `.opencode/modes/*.md`, `.opencode/command/*.md`, `.opencode/commands/*.md`, plugins under `.opencode/plugin(s)/` | `config.ts:407-466`, `config/agent.ts:11-32`, `config/command.ts`, `config/plugin.ts` | `ConfigPaths.directories` walks up from `directory` AND from `home`, unioned + unique (`paths.ts:23-41`); for each dir, if it's `.opencode` then load `opencode.json[ c]` (line 425-433) plus `ConfigAgent.load` for `agent/**/*.md` (line 460) |

### 6.2 The merge function

```ts
// config.ts:41-43
function mergeConfig(target: Info, source: Info): Info {
  return mergeDeep(target, source) as Info
}
```

All layers are deep-merged. **No array concatenation by default** — except `instructions` arrays via `mergeConfigConcatArrays` (line 45-51), and `plugin` lists which are deduplicated by `ConfigPlugin.deduplicatePluginOrigins` (line 343-349).

### 6.3 The agent.md model field

```ts
// config/agent.ts:11-32 — loads .opencode/agent/**/*.md
for (const item of await Glob.scan("{agent,agents}/**/*.md", { cwd: dir, ... })) {
  const md = await ConfigMarkdown.parse(item).catch(() => undefined)
  if (!md) continue
  const name = configEntryNameFromPath(path.relative(dir, item), ["agent/", "agents/"])
  const config = { name, ...md.data, prompt: md.content.trim() }
  result[config.name] = ConfigParse.schema(ConfigAgentV1.Info, config, item)
}
```

YAML frontmatter in the .md is parsed by `ConfigMarkdown.parse`. The schema (`core/src/v1/config/agent.ts:12-41`) has `model: Schema.optional(Schema.String)`. The string is later parsed at `agent.ts:281`:

```ts
if (value.model) item.model = Provider.parseModel(value.model)
```

**No `model:` field in the .md → `item.model` stays `undefined` → subagent inherits parent's current model at `task.ts:181-184`.**

### 6.4 The order in `loadInstanceState` (where the merging actually happens)

`config.ts:314-598` is the per-instance orchestrator. Key merge sequence:

1. **Well-known remote configs** (per auth provider, line 356-396)
2. **Global config** (`loadGlobal`, line 398-399)
3. **`OPENCODE_CONFIG` env-var file** (line 401-404)
4. **Per-project walk-up** (`ConfigPaths.files`, line 406-410) — closest to worktree wins
5. **Per-directory `.opencode/`** (line 424-466) — both `opencode.json[ c]` and agent/command .md files
6. **`OPENCODE_CONFIG_CONTENT` env-var JSON** (line 468-476)
7. **Active account's remote config** (line 478-514)
8. **Managed config dir** (line 516-522)
9. **macOS managed preferences** (line 524-534)
10. **Mode markdown files** (line 536-543) — applied as `{ [name]: { ...mode, mode: "primary" } }` overlay

**Effective precedence (last wins):** macOS managed > account remote > env content > per-dir `.opencode/agent/*.md` > per-project walk-up `opencode.json[ c]` > per-dir `.opencode/opencode.json[ c]` > global `opencode.json[ c]` > well-known remote.

In practice the per-project walk-up and the per-directory `.opencode/` files are the dominant sources for agent-specific model overrides.

---

## 7. Knowledge Gaps — What We Still Don't Know

1. **`recent` array in `~/.local/state/opencode/model.json` is never written in this repo.** Only `provider.ts:2008-2025` reads it. I searched for `writeJson.*model.json` and `recent:` and found only the read site. Either: (a) it's written by an external script not in this monorepo, (b) it's a legacy field reserved for future use, (c) it was a feature that was removed. **Architect should check `model.json` on disk** to see if `recent` is populated for their install.

2. **First assistant message model vs `cfg.model`**: If the user starts a fresh session and types nothing, then runs `task()`, the parent has no prior assistant messages. Where does `msg.info.modelID` come from? My reading: the very first user prompt that triggers a `task()` is itself the assistant row that calls `task`, so the assistant row's model is whatever `prompt.ts:646` resolved at admit time. But I haven't traced the case where the user issues a single message that *immediately* invokes `task()` before any other assistant output streams. **Worth a single targeted test.**

3. **How `SessionTable.model` is written vs `Assistant.modelID`**: `prompt.ts:621` reads `SessionTable.model` first. Where is that written? I didn't trace it. If it's set at session-create time and not updated on `/model` change, the session-resume path may use a stale model. **Architect should verify by reading the session create path.**

4. **Background subagent inheritance** (`task.ts:98` — `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`): the inheritance logic at line 181 is the same for background tasks, but the parent's `ctx.messageID` is different — it's the message that scheduled the background task, not the message currently streaming. The `currentModel` the subagent gets is "the model the parent was on when the background was scheduled" — which may be a turn or two behind. **Edge case to test.**

5. **`mode/*.md` files** (`config/agent.ts:34-58`) are loaded with `mode: "primary"` overlay (line 51-55). If a mode .md sets `model:`, does it apply to *all* agents in that mode, or only to the mode-as-an-agent? I didn't trace downstream effects. `config.ts:536-543` applies them as `result.agent[name]` entries. Worth a closer look.

6. **The `subagent-permissions.ts` interaction** with `task.ts:139-155` — the `childPermission` derivation. Doesn't affect model resolution, but is part of the full subagent launch sequence.

7. **No `task.ts` test for inheritance.** A unit test would be straightforward: stub the parent's assistant message to a known `modelID`, launch a subagent with no `model:`, assert the subagent runs on that model. We don't have one.

---

## 8. Recommendations (Options for the Architect — NO Code Changes)

These are decision-shaping options, not implementation proposals. The Architect picks.

### Option A — Explicit `model:` on every agent .md

Add `model: provider/modelID` to each subagent .md (`verity.md`, `roc_racoon.md`, `sophia.md`, `kali.md`, etc.) at `omega-engine/.opencode/agents/`. This breaks the inheritance chain for those agents, so each one is guaranteed to run on the named model regardless of the parent's current selection.

**Pros:** Deterministic, no inheritance surprises, model chosen at deploy time, no runtime surprise.
**Cons:** Bypasses the user's `/model` choice — if Architect is on `qwen3-1.7b` and wants the subagent to use the same, they'd have to set it. Slight cost in flexibility.

### Option B — Explicit `model:` only on the agents that MUST use a specific model

Add `model:` to `verity.md` (compliance work), `compaction.md`, `title.md`, `summary.md` (these already are `hidden: true` and have no inheritance intent). Leave `sophia.md`, `researcher.md`, `roc_racoon.md` to inherit.

**Pros:** Most agents keep the dynamic "follow my model" behavior. Only the agents that have a hard requirement get pinned.
**Cons:** Still inherits surprise on the unpinned agents. Slightly higher cognitive load.

### Option C — Document the inheritance in agent .md comments

Add a header comment to each subagent .md: `<!-- INHERITS MODEL FROM PARENT'S CURRENT TURN. Add "model:" to override. -->`. Zero code change. Trains the user.

**Pros:** Zero risk. Educates.
**Cons:** Doesn't fix the surprise — only documents it. Relies on the user reading.

### Option D — Pre-flight check in the prompt

Before calling `task()`, the Architect (or the parent agent's prompt) checks: *"What model am I on right now?"* (read the latest assistant row, or trust the TUI's footer model label) and explicitly states the intent: *"Launch a subagent on `claude-sonnet-4-5` to do X"*. Use `subagent_type: "general"` only with intent. Avoid paging subagents that lack a model pin unless the parent model is correct.

**Pros:** Human-driven, situational.
**Cons:** Relies on the user always being aware. Easy to forget.

### Option E — Server-side change to `task.ts:181-184` to add a fallback

Add a config option `subagent_model_inheritance: "parent" | "default" | "agent"` where:
- `parent` (current): inherit from parent's `msg.info.modelID` (line 182)
- `agent`: use the subagent's `next.model` only; if `undefined`, error or fall back to `provider.defaultModel()`
- `default`: always use `provider.defaultModel()` regardless of parent

This is a **code change** — would require filing a PR upstream to `sst/opencode`. The Architect would need to weigh whether to fork.

**Pros:** Most control, no .md changes needed for the "follow parent" case.
**Cons:** Code change, M23 implications, upstream PR churn. Architect explicitly said no code changes today.

### Recommendation

**Option A** for agents that need deterministic model selection (compliance, compaction, summary). **Option C** for the rest. Hold **Option E** as a long-term upstream proposal. This is decision-shaping — Architect decides.

---

## 9. File:Line Citations Index

| Claim | File:line |
|-------|-----------|
| Task tool reads parent's `msg.info.modelID` if no agent `model:` | `opencode/packages/opencode/src/tool/task.ts:181-184` |
| Parent's assistant row required | `opencode/packages/opencode/src/tool/task.ts:174-179` |
| Subagent prompt receives inherited model | `opencode/packages/opencode/src/tool/task.ts:202-212` |
| Variant inherited only when subagent has no `model:` | `opencode/packages/opencode/src/tool/task.ts:209` |
| `Assistant` schema has `modelID`/`providerID` required | `opencode/packages/schema/src/v1/session.ts:462-463` |
| Agent `Info` schema with optional `model` | `opencode/packages/opencode/src/agent/agent.ts:35-55` |
| Agent config string parsed at runtime | `opencode/packages/opencode/src/agent/agent.ts:281` |
| Native agents (build, plan, general, explore, compaction, title, summary) defined | `opencode/packages/opencode/src/agent/agent.ts:140-265` |
| `Provider.parseModel` | `opencode/packages/opencode/src/provider/provider.ts:2053-2059` |
| `Provider.defaultModel` 3-tier resolution | `opencode/packages/opencode/src/provider/provider.ts:2003-2034` |
| `Provider.sort` priority list | `opencode/packages/opencode/src/provider/provider.ts:2042-2051` |
| Prompt model resolution: `input.model ?? ag.model ?? currentModel(sessionID)` | `opencode/packages/opencode/src/session/prompt.ts:646` |
| `currentModel` tiers: SessionTable → last user msg → `provider.defaultModel` | `opencode/packages/opencode/src/session/prompt.ts:615-632` |
| Global config file candidates | `opencode/packages/opencode/src/config/config.ts:139-147` |
| Global config loaded: `config.json` → `opencode.json` → `opencode.jsonc` | `opencode/packages/opencode/src/config/config.ts:258-260` |
| Per-project config walk-up | `opencode/packages/opencode/src/config/paths.ts:10-21` |
| Per-directory `.opencode/` walk | `opencode/packages/opencode/src/config/paths.ts:23-41` |
| `.opencode/opencode.json[ c]` loaded per dir | `opencode/packages/opencode/src/config/config.ts:424-433` |
| `ConfigAgent.load` for `.opencode/agent/**/*.md` | `opencode/packages/opencode/src/config/agent.ts:11-32` |
| `mergeDeep` for config layers | `opencode/packages/opencode/src/config/config.ts:42-43` |
| Agent config schema (yaml frontmatter validated) | `opencode/packages/core/src/v1/config/agent.ts:12-41` |
| TUI `onModelSelect` mutates `state.model` | `opencode/packages/opencode/src/cli/cmd/run/runtime.ts:284-310` (line 289) |
| TUI prompt run sends `state.model` | `opencode/packages/opencode/src/cli/cmd/run/runtime.ts:652` |
| Stream transport sends model to server | `opencode/packages/opencode/src/cli/cmd/run/stream.transport.ts:1224, 1250, 1286` |
| `pick(args.model)` parses CLI flag | `opencode/packages/opencode/src/cli/cmd/run.ts:31-38, 863, 880, 908` |
| Footer `handleModelSelect` | `opencode/packages/opencode/src/cli/cmd/run/footer.ts:819-864` |
| Variant persistence in `model.json` | `opencode/packages/opencode/src/cli/cmd/run/variant.shared.ts:19, 158-188` |
| `recent` array READ (never written in this repo) | `opencode/packages/opencode/src/provider/provider.ts:2008-2025` |

---

## 10. Researcher's Honest Limitations

- I read the four primary files end-to-end. I did not run the TUI.
- I did not test inheritance with a live `bun dev` session; the TUI's behavior is inferred from `runtime.ts:284-310` and the call chain.
- The "recent array never written" finding is based on grep across `packages/opencode/src/`. If the writes are in a package I didn't search (e.g. a separate `cli-only` package or a script), I missed them. Architect should verify by `ls -la ~/.local/state/opencode/model.json` and inspect.
- I did not check upstream `sst/opencode` issues for related discussions. The Architect may want to search GitHub for "subagent model inheritance" or "task tool model" before deciding on a code change (Option E).

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ researcher ⬡ opencode ⬡ trc_research ⬡ ACTIVE*
*2026-08-28 · Sprint: PUBLIC-DEBUT-01 · No code changes per Architect mandate*
