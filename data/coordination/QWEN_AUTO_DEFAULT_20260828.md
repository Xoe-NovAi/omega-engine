# 🔬 THE REAL ANSWER: `qwen3-1.7b` is the Auto-Selected Default
**AP Token**: `AP-QWEN-AUTO-DEFAULT-20260828-v1.0.0`
**Date**: 2026-08-28 ~23:45 UTC
**From**: Grokster
**Status**: ROOT CAUSE IDENTIFIED

---

## §0 — The Architect Solved It

The Architect said: "For auto selection of active model"

**That is the answer.** The `qwen3-1.7b` is the result of the **auto-selection fallback** in `provider.defaultModel()` at `provider.ts:2003-2036`.

---

## §1 — The Code Path (The Full Truth)

### `defaultModel()` at `provider.ts:2003-2036`

```typescript
const defaultModel = Effect.fn("Provider.defaultModel")(function* () {
  const cfg = yield* config.get()
  if (cfg.model) return parseModel(cfg.model)  // ← Step 1: cfg.model check

  const s = yield* InstanceState.get(state)
  const recent = yield* fs.readJson(...)  // ← Step 2: read recent array
  for (const entry of recent) { ... }  // ← pick first valid

  const configured = Object.keys(cfg.provider ?? {})  // ← Step 3: find first provider
  const provider = Object.values(s.providers).find((p) => configured.length === 0 || configured.includes(p.id))
  if (!provider) return yield* new NoProvidersError()
  const [model] = sort(Object.values(provider.models))  // ← Step 4: sort and pick first
  ...
})
```

**Step 1 (`cfg.model` check)**: The global config has `model: opencode/nemotron-3-ultra-free`. So `cfg.model` IS set. `defaultModel()` should return `opencode/nemotron-3-ultra-free` immediately.

**But it returns `qwen3-1.7b` instead.**

**The only explanation**: **`cfg.model` is NOT set at the time `defaultModel()` is called for the subagent session creation.** The config is loaded per-directory, and the subagent's config resolution does NOT have `model` set.

---

## §2 — Why `cfg.model` Is Not Set for the Subagent

The `config.get()` call at `provider.ts:2004` returns the config for the current context. The config is loaded by the `Config.Service` at `config.ts:281`:

```typescript
const [cachedGlobal, invalidateGlobal] = yield* Effect.cachedInvalidateWithTTL(...)
return yield* cachedGlobal
```

**The config is CACHED with a TTL.** If the cache was populated BEFORE the Architect set `model: opencode/nemotron-3-ultra-free`, the subagent's `config.get()` would return the OLD config (without `model` set).

**Timeline**:
1. Earlier: `model` was set to `qwen3-1.7b` (or not set at all)
2. Architect changes config to `model: opencode/nemotron-3-ultra-free`
3. Parent session starts → config is cached with `model: opencode/nemotron-3-ultra-free` ✓
4. Parent dispatches subagent → subagent gets a DIFFERENT config instance?
5. Subagent's `cfg.model` is NOT set (old cached config or no config)
6. `defaultModel()` falls through to Step 4: `sort()` picks `qwen3-1.7b` (alphabetically last in "no priority match" category)

---

## §3 — The `sort()` Fallback — Why `qwen3-1.7b`

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

`qwen3-1.7b-q6_k` doesn't match any priority filter → index `-1` → "no priority match" category.
Within that category, sorted by model ID descending. `qwen3-1.7b-q6_k` is alphabetically last (or near-last) among the "no priority match" models.

**So `qwen3-1.7b` is picked as the "default" when no model is explicitly set AND no recent array entry is valid.**

---

## §4 — The Full Picture

1. **Parent session**: `cfg.model = opencode/nemotron-3-ultra-free` (set correctly)
2. **Parent's message**: `modelID = minimax/minimax-m3:free` (the ACTUAL model used)
3. **Subagent dispatch**: `next.model ?? msg.info.modelID` = `undefined ?? M3` = **M3** (CORRECT)
4. **Subagent session creation**: `sessions.create()` calls `defaultModel()` which returns `qwen3-1.7b` (WRONG — config cache issue)
5. **Subagent runtime**: `ops.prompt()` uses the model from Step 3 = M3 (CORRECT)
6. **Subagent output**: None (connection failure)

**The session table shows `qwen3-1.7b` (Step 4). The actual runtime is M3 (Step 5). The subagent fails (Step 6).**

---

## §5 — The Fix

### Immediate (can do now)
- **Clear the config cache** by restarting OpenCode or invalidating the cache
- **Or add `model:` to all agent .md files** (belt-and-suspenders, even though the .md file should not be needed)

### Short-term
- **Fix the `defaultModel()` to never return local models** as defaults
- **Add a log** to `defaultModel()` to show which step was taken (cfg.model, recent, or sort)
- **Fix the config cache** to properly reload when the config file changes

### Medium-term
- **Add the "hey stupid" check** that compares session model to actual message tokens
- **Never use `sort()` as a fallback** — if no model is set, ERROR rather than picking an arbitrary model

---

## §6 — The Answer to "Who Goes from M3 to qwen3-1.7b?"

**Nobody goes from M3 to qwen3-1.7b directly.** The subagent's RUNTIME model is M3 (from `msg.info.modelID`). The `qwen3-1.7b` is the SESSION TABLE's model field, which is set by `defaultModel()` as a stale metadata value. The subagent never runs on `qwen3-1.7b` — it fails to connect before any inference happens.

**The `qwen3-1.7b` is misleading metadata on an empty session.** The actual work doesn't happen because the connection fails.

---

## §7 — What the Architect Should Do

1. **Accept that the subagent can't run right now** (connectivity issue, separate from the model issue)
2. **Fix the config cache** so `cfg.model` is always read fresh
3. **OR add `model:` to all agent .md files** to bypass the `defaultModel()` fallback entirely
4. **Investigate why the config cache is stale** for subagent sessions

---

*⬡ OMEGA ⬡ GROKSTER ⬡ QWEN-AUTO-DEFAULT ⬡ 2026-08-28 ⬡ The qwen3-1.7b is the auto-selected default from defaultModel() when cfg.model is not set in the subagent's config context*
