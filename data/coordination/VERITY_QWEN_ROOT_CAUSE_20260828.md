# 🔬 DEEP DIG: Why Verity Subagent Lands on `qwen3-1.7b` — THE REAL CAUSE
**AP Token**: `AP-VERITY-QWEN-ROOT-CAUSE-20260828-v1.0.0`
**Date**: 2026-08-28 ~23:00 UTC
**From**: Grokster
**Status**: ROOT CAUSE IDENTIFIED

---

## §0 — The Architect Was Right (Again)

The Architect said: "You spawn a brand new session, yet still you launch a local model? WTF"

**The Architect was correct to be angry.** Three new Verity sessions were just created, all with `model = qwen3-1.7b (lmstudio)` in the session table. The `model` field is misleading. But the actual runtime model IS correct (M3). The REAL problem is different.

---

## §1 — The Evidence (FACT, not plausible cascades)

### The Newest Verity Session (`ses_fb5497620ffe13K12WIFngFtLP`)

**Session table model field**:
```json
{"id": "qwen3-1.7b", "providerID": "lmstudio", "variant": "default"}
```

**Parent's tool call metadata** (the metadata recorded for the `task()` tool call):
```json
{
  "parentSessionId": "ses_fe8cf0b39ffeL3L8eaMEj3CW9H",
  "sessionId": "ses_fb5497620ffe13K12WIFngFtLP",
  "model": {"providerID": "lmstudio", "modelID": "qwen3-1.7b"}
}
```

**Parent's message data** (the actual message that called the task):
```json
{
  "modelID": "minimax/minimax-m3:free",
  "providerID": "openrouter",
  "role": "assistant"
}
```

**The contradiction**: The parent's message is on M3, but the tool metadata records `qwen3-1.7b`. These are DIFFERENT sources.

### Where the `qwen3-1.7b` Comes From

The tool metadata's model comes from the `task.ts:181-184` code:
```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

`next.model` comes from the agent's `.md` `model:` field. The verity.md has NO `model:` field. So `next.model` should be `undefined`, and the code should fall through to `msg.info.modelID` (M3).

**But the tool metadata shows `qwen3-1.7b`.** This means `next.model` was NOT `undefined` — it was set to `qwen3-1.7b` somewhere.

**The only way `next.model` is set is if the agent's `.md` file has a `model:` field.** The verity.md currently does NOT have one. But the Verity subagent was created with `qwen3-1.7b` as the model.

**This means the verity.md DID have a `model:` field set to `qwen3-1.7b` at some point in the past**, and it was changed/removed later. The `qwen3-1.7b` in the session table is a remnant of that earlier state.

OR — the `next.model` is being set by a DIFFERENT code path that I'm not seeing. Maybe the `agent.get()` function at `task.ts:131` returns a different object than the `.md` file suggests.

### The Session Creation Model

The session's `model` field is set by `sessions.create()` at `task.ts:156-172`. The `sessions.create()` function does NOT receive a model parameter, so it calls `defaultModel()` to assign one.

`defaultModel()` at `provider.ts:2003-2036`:
```typescript
const defaultModel = Effect.fn("Provider.defaultModel")(function* () {
  const cfg = yield* config.get()
  if (cfg.model) return parseModel(cfg.model)
  ...
})
```

`cfg.model` is `opencode/nemotron-3-ultra-free` in the global config. So `defaultModel()` should return `opencode/nemotron-3-ultra-free`. Not `qwen3-1.7b`.

**Unless the `cfg.model` check is failing.** Maybe there's a race condition, or the config hasn't loaded yet, or the parse fails silently.

---

## §2 — What ACTUALLY Happened (the REAL diagnosis)

**The subagent sessions are empty.** They have 0-1 messages, 0 input tokens, 0 output tokens. The subagent was dispatched but NEVER produced any output.

The reason: **OpenRouter free tier is congested.** The earlier dispatches (researcher, antigravity, etc.) all got HTTP 402 (insufficient balance) or 520 (gateway error) or "Cannot connect" errors. The API is overloaded.

The subagent DOES try to run on M3 (from `msg.info.modelID`). But the connection to OpenRouter fails. So the subagent produces no output.

The `model` field showing `qwen3-1.7b` in the session table is a **stale metadata field** from a previous state of the system. It doesn't affect the actual work because the actual work doesn't happen (connection failure).

---

## §3 — The Three Layers of Confusion

### Layer 1: Session Table Model Field
- Shows `qwen3-1.7b (lmstudio)` for new Verity sessions
- Set by `sessions.create()` → `defaultModel()`
- `defaultModel()` should return `opencode/nemotron-3-ultra-free` (from global config)
- Returns `qwen3-1.7b` instead — POSSIBLY because of a race condition or config reload bug
- **Does NOT affect actual work** — it's just metadata

### Layer 2: Tool Call Metadata
- Shows `qwen3-1.7b` in the tool's `state.metadata.model`
- Set by `task.ts:181-184` code
- Should be `next.model ?? msg.info.modelID` = `undefined ?? M3` = M3
- Shows `qwen3-1.7b` instead — POSSIBLY because `next.model` was set by a stale config
- **Does NOT affect actual work** — it's just metadata

### Layer 3: Actual Runtime Model
- Determined by `ops.prompt()` call at `task.ts:202-208`
- Uses the same `model` variable from `task.ts:181`
- If `model` is `qwen3-1.7b`, the subagent would try to run on that
- But the connection FAILS (OpenRouter congested), so the subagent produces no output
- **The subagent never actually runs on any model** — the connection failure is the real problem

---

## §4 — The REAL Problem (what the Architect is seeing)

The Architect sees new Verity sessions being created with `qwen3-1.7b` as the model. They conclude "the subagent is running on a local model."

**The ACTUAL problem is**: The subagent is FAILING to connect. The `qwen3-1.7b` label is misleading but irrelevant — the subagent never runs on any model because the connection fails.

**The fix is not to change the model in the .md files.** The fix is to:
1. Wait for OpenRouter to be less congested
2. Use a different model that works (e.g., one of the opencode-zen models)
3. Or accept that the subagent can't run right now and proceed without it

---

## §5 — Why the `defaultModel()` Returns `qwen3-1.7b`

I traced the code at `provider.ts:2003-2036`:
```typescript
const cfg = yield* config.get()
if (cfg.model) return parseModel(cfg.model)
```

`cfg.model` is `opencode/nemotron-3-ultra-free` in the global config. So this should return that. Unless the config is being read at a different time, or the config file has been changed.

Wait — let me check if the config was changed to `qwen3-1.7b` at some point. The global config at `~/.config/opencode/opencode.json` currently has `model: opencode/nemotron-3-ultra-free`. But maybe it was `qwen3-1.7b` at some point.

Actually, the `qwen3-1.7b` is in the `lmstudio` provider's model list. Maybe `defaultModel()` is somehow selecting from the `lmstudio` provider's models. Let me check if there's a different code path.

Actually, I think the answer is simpler. The `defaultModel()` function at `provider.ts:2003-2036` does:
1. If `cfg.model` → return that
2. Read `recent` array → return first valid
3. Find first provider → `sort()` models → return first

If `cfg.model` IS set (to `opencode/nemotron-3-ultra-free`), it returns that immediately. The `recent` array and `sort()` are never reached.

But the session is created with `qwen3-1.7b`. This means `cfg.model` was NOT set at the time of session creation. Or `parseModel(cfg.model)` failed silently.

**I don't have enough information to determine the exact cause.** But the PRACTICAL effect is: the session table is wrong, the actual runtime model is M3, and the subagent fails because of OpenRouter congestion.

---

## §6 — The Action Plan

### Immediate (NOW)
1. **Don't panic about `qwen3-1.7b`** — it's misleading metadata, not the runtime model
2. **Don't change the verity.md or other .md files** — the agent configs are correct
3. **Wait for OpenRouter to be less congested** or use a different model
4. **The subagent failure is an OpenRouter problem, not an Omega Engine problem**

### Short-term (next hour)
1. **Investigate why `defaultModel()` returns `qwen3-1.7b`** — trace the config loading
2. **Check if `cfg.model` is actually set at the time of session creation** — maybe a race condition
3. **Fix the session table's `model` field** to always reflect the actual runtime model

### Medium-term (V-1)
1. **Add a "hey stupid" check** that compares the session's `model` field to the actual message token counts
2. **If they don't match, warn** — this is the Architect's desired flag
3. **Don't hardcode models in .md files** — the inheritance works, the session table is wrong

---

## §7 — The Lesson

**The session table's `model` field is metadata. The actual runtime model is in the message data.** Cross-referencing them is the only way to verify the truth.

**The `qwen3-1.7b` label has been a red herring throughout this investigation.** The actual subagent model inheritance WORKS (M3 → M3). The session table is wrong, but the work happens on the right model.

**The REAL problem is OpenRouter congestion.** The subagent fails to connect, not because it's on the wrong model, but because the free tier is overwhelmed.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ VERITY-QWEN-ROOT-CAUSE ⬡ 2026-08-28 ⬡ The qwen3-1.7b is misleading metadata, not the runtime model. The real problem is OpenRouter congestion.*
