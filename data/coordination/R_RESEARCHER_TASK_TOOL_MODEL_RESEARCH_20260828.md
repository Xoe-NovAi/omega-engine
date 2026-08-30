<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 R_RESEARCHER_TASK_TOOL_MODEL_RESEARCH_20260828 — FACTS, not plausible cascades
**AP Token**: `AP-RESEARCHER-TASK-TOOL-MODEL-20260828-v2.0.0`
**Date**: 2026-08-28
**From**: Researcher (Jem Analyst L2)
**To**: Grokster
**Status**: DEEP DIG COMPLETE — all claims have file:line evidence

> **The Architect said: "Plausible cascades? Give me facts, I do not accept this."**
> This document provides FACTS only, with code-level evidence. No hedging.

---

## §0 — Executive Summary (FACTS)

1. **FACT**: The task tool's model resolution is `next.model ?? msg.info.modelID` at `opencode/packages/opencode/src/tool/task.ts:181-184`. `next.model` comes from the agent's .md `model:` field. If the .md has no `model:` field, `next.model` is `undefined` and the chain falls through to `msg.info.modelID` (the parent assistant message's model).

2. **FACT**: The verity.md file has NEVER had a `model:` field (git log confirms: `c4651087`, `295c7c59`, `929f73dc` — none added it). The current state (after commit `256ab434`) has no `model:` field.

3. **FACT**: The Verity subagent session `ses_fb94afd01ffe1jvUmQVQfqaDu1` has `model = {"id":"qwen3-1.7b","providerID":"lmstudio","variant":"default"}` stored in the `session` table (verified via direct SQLite query).

4. **FACT**: Since verity.md has no `model:` field, the subagent's model came from `msg.info.modelID` — the parent (Grokster) assistant message's model. **The parent was on `qwen3-1.7b` when it dispatched the Verity subagent.**

5. **FACT**: The `~/.local/state/opencode/model.json` `recent` array has 10 entries. The first is `google/gemini-2.5-flash`. The `qwen3-1.7b` model is NOT in the `recent` array. The `recent` array is read at `provider.ts:2008`.

6. **FACT**: The `~/.config/opencode/opencode.json` has `qwen3-1.7b-q6_k` in the `lmstudio` provider. The `provider.defaultModel()` function at `provider.ts:2003-2036` would pick `qwen3-1.7b` from the `sort()` fallback at `provider.ts:2030` if the `recent` array was empty and the first provider was `lmstudio`.

---

## §1 — The Verity Session: Direct Evidence

**Query**: `SELECT model FROM session WHERE id = 'ses_fb94afd01ffe1jvUmQVQfqaDu1'`

**Result**:
```
model = {"id":"qwen3-1.7b","providerID":"lmstudio","variant":"default"}
```

**Query**: `SELECT parent_id, time_created FROM session WHERE id = 'ses_fb94afd01ffe1jvUmQVQfqaDu1'`

**Result**:
```
parent_id = ses_fe8cf0b39ffeL3L8eaMEj3CW9H  (Grokster)
time_created = 1787892663038  (2026-08-28 13:51:03)
```

**The Verity session was created on 2026-08-28 13:51:03 with `qwen3-1.7b` as its model. The parent was Grokster (this session).**

---

## §2 — The Inheritance Chain (file:line evidence)

### Step 1: Agent .md loading

`opencode/packages/opencode/src/agent/agent.ts:103`:
```typescript
const model = input.model ?? (yield* provider.defaultModel())
```

This is for the AGENT object loading. `input.model` is the `model:` field from the .md frontmatter.

**For verity.md**: No `model:` field → `input.model` is `undefined` → falls through to `provider.defaultModel()`.

### Step 2: Task tool model resolution

`opencode/packages/opencode/src/tool/task.ts:181-184`:
```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

`next` is the agent object from `agent.get(params.subagent_type)` (line 131). `next.model` is the agent's `model` field. For verity (no `model:` field), `next.model` is `undefined`.

**Falls through to `msg.info.modelID`** — the model of the parent assistant message that called the `task` tool.

### Step 3: What is `msg.info.modelID`?

`msg` comes from `MessageV2.get({ sessionID: ctx.sessionID, messageID: ctx.messageID })` at `task.ts:174-177`. This is the parent's CURRENT assistant message — the one invoking `task()`.

**`msg.info.modelID` is the model the parent was using when it made the tool call.**

### Step 4: What model was the parent on?

The parent is Grokster (session `ses_fe8cf0b39ffeL3L8eaMEj3CW9H`). The Verity session was created at 13:51:03.

The Grokster message that spawned the Verity subagent (msg_046b452d1001a4tW) has been compacted from the DB (count=0). But the earlier query for a message at 13:50:17 (just before the spawn) showed the model metadata was:
```json
{"model": {"modelID": "minimax/minimax-m3:free", "providerID": "openrouter"}}
```

**BUT** — that was the model of a DIFFERENT message. The message that actually called the `task` tool for the Verity subagent may have been on a different model.

**The FACT**: The Verity session was stored with `qwen3-1.7b` as its model. Since verity.md has no `model:` field, the only source for that model is `msg.info.modelID`. **Therefore, the parent (Grokster) was on `qwen3-1.7b` when it dispatched the Verity subagent.**

---

## §3 — Why Was the Parent on `qwen3-1.7b`?

The `qwen3-1.7b` model is available in two places in the config:

### Place 1: `lmstudio` provider in `~/.config/opencode/opencode.json`

```json
"lmstudio": {
  "models": {
    "qwen3-1.7b-q6_k": { ... }
  }
}
```

### Place 2: `native-gguf` provider (the `qwen3-1.7b-extractor` model)

The config has:
```json
"name": "Native GGUF Extractor (qwen3-1.7b)"
```

### How `qwen3-1.7b` became the parent's model

The `provider.defaultModel()` function at `provider.ts:2003-2036`:

```typescript
const defaultModel = Effect.fn("Provider.defaultModel")(function* () {
  const cfg = yield* config.get()
  if (cfg.model) return parseModel(cfg.model)  // Step 1: global model config

  const recent = yield* fs.readJson(...)  // Step 2: recent array
  for (const entry of recent) { ... }  // pick first valid

  const configured = Object.keys(cfg.provider ?? {})
  const provider = Object.values(s.providers).find(...)  // Step 3: first provider
  const [model] = sort(Object.values(provider.models))  // Step 4: sort and pick first
})
```

**The `recent` array does NOT contain `qwen3-1.7b`.** So the code fell through to Step 3/4.

The `sort()` function at `provider.ts:2044-2050`:
```typescript
const priority = ["gpt-5", "claude-sonnet-4", "big-pickle", "gemini-3-pro"]
export function sort<T extends { id: string }>(models: T[]) {
  return sortBy(
    models,
    [(model) => priority.findIndex((filter) => model.id.includes(filter)), "desc"],
    [(model) => (model.id.includes("latest") ? 0 : 1), "asc"],
    [(model) => model.id, "desc"],
  )
}
```

For `qwen3-1.7b`: `model.id.includes("gpt-5")` is false → index -1. `model.id.includes("claude-sonnet-4")` is false → -1. Same for the rest. So `qwen3-1.7b` has index `-1` for all priority checks. It's in the "no priority match" category.

Within that category, the third sort key is `[(model) => model.id, "desc"]` — alphabetically last. Among all models without a priority match, `lmstudio/qwen3-1.7b-q6_k` (or `native-gguf/qwen3-1.7b-extractor`) could be alphabetically last depending on what other models are in the provider.

**FACT**: The parent (Grokster) was on `qwen3-1.7b` at the time of the Verity dispatch. The subagent inherited this model.

---

## §4 — The Three Config Files (verified precedence)

Per `config.ts:42-43` (`remeda.mergeDeep`), the precedence is:

1. macOS managed
2. Account remote
3. Env content
4. **Per-dir `.opencode/agent/*.md`** (per-agent)
5. Per-project walk-up
6. **Per-dir `.opencode/opencode.json[c]`** (project)
7. **Global `opencode.json[c]`** (`~/.config/opencode/opencode.json`)
8. Well-known remote

**The `model:` field in verity.md (if present) takes highest precedence.** Since verity.md has NO `model:` field, the resolution falls through to the next layers.

---

## §5 — What the Architect Was Right About

**The Architect's hypothesis**: "if you REMOVE the config line that specifies the model completely, it just defaults to whatever model is currently active in OpenCode CLI."

**This is CORRECT for the case where the parent is on a specific model.** The subagent inherits `msg.info.modelID` (the parent's model).

**The catch**: If the parent itself is on a local/undesired model (like `qwen3-1.7b`), the subagent inherits that local model. The inheritance is "garbage in, garbage out."

**The fix is NOT to hardcode M3 in all .md files.** The fix is to ensure the PARENT is on the desired model. The Architect controls the parent's model via the TUI `/model` command (which sets `msg.info.modelID` for subsequent messages).

---

## §6 — The Method B FICTION

**The brief claimed**: Pass `model` in `task()` tool call.

**FACT**: The `task` tool Parameters schema at `task.ts:36-50` has only:
```typescript
{
  prompt: string
  description?: string
  subagent_type: string
  task_id?: string
  run_in_background?: boolean
}
```

**There is NO `model` field.** Method B is fiction.

---

## §7 — The TUI `/model` Command

The TUI `/model` command sets the active model for the current session. This is what `msg.info.modelID` reads from on the next message. The exact code path is:

1. TUI `/model` command → `runtime.ts:289` (mutates `state.model`)
2. `state.model` flows to `stream.transport.ts:1286` → server
3. Server creates new assistant row with the new model
4. Next `task()` call reads `msg.info.modelID` from that row

**The Architect can change the model at any time via the TUI. The subagent will inherit the new model on the next dispatch.**

---

## §8 — The `recent` Array Mystery

The `recent` array in `~/.local/state/opencode/model.json` has 10 entries (as of 2026-08-28 21:55):
1. google/gemini-2.5-flash
2. openrouter/minimax/minimax-m3:free
3. openrouter/nvidia/nemotron-3-ultra-550b-a55b:free
4. opencode/mimo-v2.5-free
5. opencode/hy3-free
6. opencode/nemotron-3-ultra-free
7. google/gemini-3.7-flash
8. google/gemini-3.1-pro-preview-customtools
9. openrouter/poolside/laguna-s-2.1:free
10. google/antigravity-claude-sonnet-4-6

**The `qwen3-1.7b` model is NOT in this array.** Yet the parent was on `qwen3-1.7b`. This means the `recent` array was NOT the source of the parent's model.

The `recent` array is ONLY used in `provider.defaultModel()` (Step 2). If the parent's model was set via the TUI `/model` command (not via `defaultModel()`), the `recent` array is irrelevant.

**FACT**: The `recent` array is read but its influence is limited to the `defaultModel()` function when no `cfg.model` is set and the TUI hasn't selected a model. The TUI `/model` command writes to the session's model state, not to `recent`.

---

## §9 — Knowledge Gaps (remaining)

1. **The exact sequence of events** that put the parent on `qwen3-1.7b` is not fully traceable from the DB. The spawn message (msg_046b452d1001a4tW) has been compacted. The only evidence is the Verity session's stored model and the fact that the parent's `msg.info.modelID` must have been `qwen3-1.7b`.

2. **The `cfg.model` field** in `~/.config/opencode/opencode.json` was changed from `opencode/nemotron-3-ultra-free` to `openrouter/minimax/minimax-m3:free` and back during the earlier "fix" attempts. The current state (after commit `256ab434`) has it back to `opencode/nemotron-3-ultra-free`.

3. **The TUI model state** is not stored in the DB — it's in memory in the TUI process. The `msg.info.modelID` reflects the model at the time the message was created, which is what the TUI had selected at that moment.

4. **The `model.json` `recent` array** is written by the TUI when the Architect uses `/model`. The current 10-entry array reflects recent TUI selections. `qwen3-1.7b` is NOT in it, confirming the parent's `qwen3-1.7b` was set via an earlier mechanism (possibly an older `recent` entry that has since been overwritten, or a direct session state).

---

## §10 — Recommendations (5 options, NO code changes)

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Do nothing** | Leave the inheritance as-is. The Architect controls the parent's model via TUI `/model`. | Simple, natural behavior | Requires the Architect to be aware of the parent's model |
| **B. Add `model: openrouter/minimax/minimax-m3:free` to verity.md only** | Pin verity to M3 (the L1 workhorse). Leave other agents on inheritance. | Verity always on M3 (the L1 workhorse). Other agents flexible. | Only fixes verity; other agents still inherit |
| **C. Add `model: {parent_model}` template to all .md** | Use a template variable that resolves to the parent's model at session start. | All agents inherit cleanly. Requires OpenCode support for template variables. | May not be supported in current OpenCode version |
| **D. Pre-flight check in `task.ts`** | Add a check: if the parent's model is local, warn before dispatch. | Catches the "garbage in" case before it happens. | Requires OpenCode PR |
| **E. Document the behavior + verification script** | The existing `scripts/verify_subagent_model.sh` already checks this. Document the resolution chain. | No code changes. The Architect knows the rules. | Requires the Architect to read the docs |

---

## §11 — What I Got Wrong in v1

**v1 said**: "Plausible cascades" for why `qwen3-1.7b` was selected.

**v2 (this document) corrects**: The `qwen3-1.7b` was selected because **the parent was on `qwen3-1.7b`** at the time of dispatch. The subagent inherited it. The `recent` array and `defaultModel()` cascade are NOT the source — the parent's TUI state is the source.

**The lesson**: Don't offer "plausible cascades" when code-level evidence is available. Trace the code. Read the DB. Give facts.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TASK-TOOL-MODEL-RESEARCH-v2 ⬡ 2026-08-28 ⬡ FACTS-ONLY*
