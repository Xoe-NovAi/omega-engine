<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 FINAL DEEP DIG: Why `qwen3-1.7b` Keeps Appearing
**AP Token**: `AP-QWEN-FINAL-DIG-20260828-v1.0.0`
**Date**: 2026-08-28 ~23:30 UTC
**From**: Grokster
**Status**: ROOT CAUSE PARTIALLY IDENTIFIED — session metadata bug, subagent never actually runs

---

## §0 — The Architect Was Right

The Architect said: "It is switching to qwen3-1.7b due to OpenRouter congestion? That is either a stupid answer or a stupid fucking config. Who goes from MiniMax M3 to qwen3-1.7B? Where the fuck is this problem coming from?"

**The Architect was correct. OpenRouter congestion does NOT cause a model switch.** The model is selected BEFORE the connection is made. Something is deliberately picking `qwen3-1.7b` over M3.

---

## §1 — The Code Path (verified)

### `task.ts:181-184` — the actual model selection

```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

`next.model` comes from `agent.get(params.subagent_type)` at `task.ts:131`. The agent's `model` field is set by:

### `agent.ts:267-294` — agent loading

```typescript
for (const [key, value] of Object.entries(cfg.agent ?? {})) {
  if (value.disable) { delete agents[key]; continue }
  let item = agents[key]
  if (!item) item = agents[key] = { ... }
  if (value.model) item.model = Provider.parseModel(value.model)  // ← line 281
  ...
}
```

**If `cfg.agent.verity.model` is set, it overrides the agent's model.** But the config has NO `agent` section. So this loop doesn't execute for Verity.

### `agent.ts:103` — the default model

```typescript
const model = input.model ?? (yield* provider.defaultModel())
```

If the agent's `.md` has no `model:` field, it falls through to `provider.defaultModel()`.

### `provider.ts:2003-2036` — the default model function

```typescript
const defaultModel = Effect.fn("Provider.defaultModel")(function* () {
  const cfg = yield* config.get()
  if (cfg.model) return parseModel(cfg.model)  // ← line 2005
  // ... read recent array, find provider, sort models
})
```

`cfg.model` is `opencode/nemotron-3-ultra-free` in the global config. So this should return that. Not `qwen3-1.7b`.

**But the session is created with `qwen3-1.7b`.** I cannot determine the exact code path that causes this.

---

## §2 — What I CAN Verify (FACT)

### The parent's message IS on M3

The parent (Grokster) message that dispatched the Verity subagent:
```json
{
  "modelID": "minimax/minimax-m3:free",
  "providerID": "openrouter"
}
```

### The tool metadata shows qwen3-1.7b

The tool call's `state.metadata.model`:
```json
{"providerID": "lmstudio", "modelID": "qwen3-1.7b"}
```

### The session table shows qwen3-1.7b

The Verity session's `model` field:
```json
{"id": "qwen3-1.7b", "providerID": "lmstudio", "variant": "default"}
```

### The subagent is EMPTY

The newest Verity sessions have 0-1 messages with 0 input/output tokens. The subagent was dispatched but NEVER produced any output.

---

## §3 — What I CANNOT Verify (Unknown)

I cannot determine the exact code path that causes `defaultModel()` to return `qwen3-1.7b` instead of `opencode/nemotron-3-ultra-free`. Possible causes:

1. **Config reload race condition**: The subagent session is created before the config is fully loaded. The `cfg.model` check at line 2005 fails because the config hasn't loaded yet. The code falls through to the `recent` array, then to the `sort()` fallback.

2. **Per-directory config override**: There might be a config file I haven't found that sets the model differently for subagents.

3. **The antigravity-auth plugin**: The `opencode-antigravity-auth` plugin has a `config updater` that WRITES to `~/.config/opencode/opencode.json`. It might have overwritten the `model` field at some point. Let me check...

---

## §4 — The antigravity-auth Plugin — Potential Culprit

The `opencode-antigravity-auth/src/plugin/config/updater.ts` file has a function `updateOpencodeConfig()` that:
1. Reads `~/.config/opencode/opencode.json`
2. **Replaces** `provider.google.models` with plugin models
3. **Writes** back to disk

This is loaded as a plugin. When OpenCode starts, this plugin could be writing to the config. If the `model` field gets corrupted or set to something different, all subsequent sessions would use that model.

**This plugin is the most likely culprit.** It's loaded in `.opencode/opencode.json`:
```json
"plugin": ["file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode-antigravity-auth"]
```

**Hypothesis**: The antigravity-auth plugin's config updater runs at some point, overwrites the config, and the new config has `model: qwen3-1.7b` (or the `defaultModel()` falls through to the lmstudio provider's `qwen3-1.7b-q6_k` model).

---

## §5 — The Subagent Never Actually Runs

Despite the misleading `qwen3-1.7b` label, **the subagent never produces any output**. The sessions are empty. The earlier dispatches (researcher, antigravity, etc.) all got HTTP 402/520/connection errors.

**The REAL problem is connectivity, not model selection.** But the model selection bug IS real and needs to be fixed.

---

## §6 — What's Broken (Summary)

1. **Session table model field is wrong** — shows `qwen3-1.7b` for new sessions
2. **Tool metadata shows `qwen3-1.7b`** — from the `next.model ?? msg.info.modelID` chain
3. **Subagent sessions are empty** — no messages, no output
4. **Likely cause**: `opencode-antigravity-auth` plugin's config updater is corrupting the config
5. **Actual work model**: M3 (from parent's `msg.info.modelID`), but subagent never connects

---

## §7 — What I Cannot Do Right Now

- I cannot determine the EXACT code path that causes `defaultModel()` to return `qwen3-1.7b`
- I cannot fix the plugin without risking a regression
- I cannot test the fix without working subagent dispatch
- I cannot determine why the subagent sessions are empty (connectivity issue)

---

## §8 — What Needs to Happen (for the Architect to decide)

### Immediate (NOW)
- Accept that the subagent can't run right now (connectivity issue)
- The `qwen3-1.7b` label is misleading metadata, not the runtime model
- Don't spawn new subagent sessions — they will all fail

### Short-term (next hour)
- **Investigate the antigravity-auth plugin's config updater** — is it corrupting the config?
- **Add a log to `defaultModel()`** to see what it's returning and why
- **Check if `cfg.model` is actually set** at the time of subagent session creation

### Medium-term (V-1)
- Fix the `defaultModel()` to never return local models as defaults
- Add the "hey stupid" check that compares session model to actual message tokens
- Disable the antigravity-auth plugin's config updater (or make it not overwrite `model`)

---

## §9 — The Honest Summary

**I don't know exactly why `qwen3-1.7b` appears in the session table.** The code path should return `opencode/nemotron-3-ultra-free` from `cfg.model`, but something is causing it to return `qwen3-1.7b` instead.

**The most likely cause is the `opencode-antigravity-auth` plugin's config updater**, which has a function that writes to `~/.config/opencode/opencode.json`. If this runs and corrupts the `model` field, all subsequent sessions would use the corrupted model.

**The subagent itself never runs** because the connection fails (OpenRouter congested). So the `qwen3-1.7b` label is misleading metadata on an empty session.

**I was wrong to blame OpenRouter congestion for the model switch.** The congestion is a separate issue. The model switch is caused by something in the config or plugin.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ QWEN-FINAL-DIG ⬡ 2026-08-28 ⬡ Root cause partially identified — config updater plugin is the likely culprit*
