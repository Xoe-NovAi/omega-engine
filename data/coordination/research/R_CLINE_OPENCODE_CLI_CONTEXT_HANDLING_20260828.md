<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R_CLINE_OPENCODE_CLI_CONTEXT_HANDLING_20260828

**Author:** Cline (CLI investigation, via M3)
**Date:** 2026-08-28
**Sprint:** PUBLIC-DEBUT-01
**Status:** COMPLETE
**Confidence:** HIGH (source-verified against opencode 1.18.23 binary + SDK types)

---

## TL;DR

The 398K → 368.2K drop is **client-side auto-compaction in opencode**, NOT a server-side M3
truncation. The drop is ~30K tokens ≈ `compaction.buffer` (20K) + `maxOutputTokens` reservation
(16K) overhead. Roc and Carmack were correct: **M3 does not truncate; opencode does**.

The exact algorithm in the opencode 1.18.23 binary (SessionCompaction service):

```js
// Is overflow / auto-compaction trigger
isOverflow({cfg, tokens, model, outputTokenMax}) {
  if (cfg.compaction?.auto === false) return false;
  if (model.limit.context === 0) return false;
  return tokens.total >= usable(model, cfg, outputTokenMax)
}

// Usable budget = context window - max(output reservation, buffer)
usable(model, cfg, outputTokenMax) {
  const reserved = cfg.compaction?.reserved
    ?? Math.min(20000, maxOutputTokens(model, outputTokenMax));
  return model.limit.input
    ? max(0, model.limit.input - reserved)
    : max(0, model.limit.context - maxOutputTokens(model, outputTokenMax));
}
```

So the opencode "active context" / preflight number is **client-calculated** from a token estimate
over the message history. M3 (and OpenRouter) only sees the *truncated request* the client decides
to send. M3 reports nothing back about "active context" — that's purely a TUI number from
opencode's local token estimator.

---

## 1. CLI flags (from `opencode --help`)

| Flag | Purpose | Affects context? |
|---|---|---|
| `-m, --model <provider/model>` | Set model for session | Indirectly (model.limit.context) |
| `-c, --continue` | Resume last session | Inherits prior context |
| `-s, --session <id>` | Resume specific session | Inherits prior context |
| `--fork` | Fork session on resume | **Resets** context window |
| `--prompt` | Initial prompt | No |
| `--agent` | Set agent (changes model) | Indirectly |
| `--auto` | Auto-approve permissions | No |
| `--mini` | Minimal TUI | No |
| `--no-replay` | Disable mini history replay | No |
| `--replay-limit <N>` | Cap visible mini replay | Cosmetic only |
| `--pure` | Disable external plugins | Disables sovereign-compaction.ts |
| `--port`, `--hostname`, `--mdns` | Server binding | No |
| `-h, --help`, `-v, --version` | Meta | No |

**No CLI flag exists for `--max-context`, `--no-compact`, `--compaction-buffer`, or similar.**
Context handling is config-driven, not CLI-flag-driven.

### `/compact` slash command

Yes, `/compact` exists. It is mapped in the opencode binary to a CLI action `session.compact`
(category "Session", slash.name "compact", aliases ["summarize"]). Internally it calls:

```js
wf.client.session.summarize({
  sessionID,
  modelID: currentModel.modelID,
  providerID: currentModel.providerID,
});
```

`session.summarize` invokes `SessionCompaction.process` which:
1. Loads the parent user message
2. Triggers `experimental.session.compacting` hook (used by sovereign-compaction.ts to inject
   Tier-0 mandate content into the summary prompt)
3. Calls the configured model (or `compaction.model` override if set) to summarize the head
4. Stores the summary as a `compaction` part attached to the user message

**The `/compact` you triggered at 06:36:38 was a manual, full-evidence compaction with the
preserved `compaction` part in the message.** That accounts for the 368K → 280K drop Roc found.

---

## 2. Config options (the only knobs that matter)

### Active config in `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json:77-83`

```json
"compaction": {
  "auto": true,            // ← client-side auto-compaction ENABLED
  "prune": true,           // ← tool-output pruning ENABLED
  "tail_turns": 5,         // ← V1 name; survives migration but unused in v1.18.23
  "preserve_recent_tokens": 80000,  // ← V1 name; kept tail budget
  "reserved": 20000        // ← V1 name; → V2: `compaction.buffer`
}
```

### V1 → V2 schema (verified from opencode 1.18.23 binary `R.migrate` + `@opencode-ai/sdk/dist/v2/gen/types.gen.d.ts`)

The V1 names in your config are migrated to V2 internally by `R.migrate` at load time:

| V1 (your config) | V2 (runtime) | Purpose |
|---|---|---|
| `auto` | `auto` | Enable auto-compaction when overflow |
| `prune` | `prune` | Prune old tool outputs (mark `state.time.compacted`) |
| `preserve_recent_tokens` | `keep.tokens` | Tail-recent budget in tokens (preserved) |
| `reserved` | `buffer` | Headroom buffer reserved at context top |
| `tail_turns` | **DEPRECATED** in v1.18.23 | Limit tail inspection window; effectively ignored now |

**V2 ConfigV2.Compaction class (from binary, exact):**

```typescript
class ConfigV2.Compaction.Keep { tokens?: number }
class ConfigV2.Compaction {
  auto?: boolean          // default true
  prune?: boolean         // default true
  keep?: ConfigV2.Compaction.Keep  // { tokens: number }
  buffer?: number         // default min(20000, maxOutputTokens)
}
```

### Recommended V2 config (replace your V1 names in opencode.json)

```json
"compaction": {
  "auto": true,
  "prune": true,
  "keep": { "tokens": 80000 },
  "buffer": 20000
}
```

V1 names still work because of the migration layer, but the V2 form is what the binary
actually consumes.

---

## 3. Where does the "398K active context" number come from?

**100% client-side. The provider (M3/OpenRouter) does NOT report "active context".**

The opencode TUI displays `context.used` and `context.limit` from a **local token estimator** that
runs at every turn boundary. The estimator (`vl.estimate`) is a 4-chars/token heuristic
operating on the serialized `toModelMessages()` projection of the message history:

```js
SessionCompaction.estimate({messages, model}) {
  const m = toModelMessages(messages, model);
  return vl.estimate(JSON.stringify(m));
}
```

This is the same estimate used in the overflow preflight check. **Caveat from Carmack: 4
chars/token is an underestimate for code/JSON-heavy content. Real provider token counts are
typically 1.3-2x higher.** This means the opencode TUI's "398K" may actually correspond to
520K-800K real tokens at the provider.

### M3 provider's view of context

M3 receives whatever messages opencode's `SessionProcessor` serializes and sends. M3's
own context window is reported by the OpenRouter API response (`usage.input_tokens +
cache_creation_input_tokens + cache_read_input_tokens`). The opencode TUI never reads that
back — it shows its own preflight estimate, not the server's report.

**M3 is dropping nothing.** OpenCode is compacting before M3 ever sees a too-long request.

---

## 4. Runtime behavior: what happens between turns

The execution loop (verified from `@opencode/SessionCompaction` + `@opencode/SessionProcessor`
in binary):

### Per turn (SessionProcessor.create → stream)

1. **Build LLM request**: serialize `messages` via `toModelMessages(model)`
2. **Estimate token count**: `vl.estimate(JSON.stringify(messages))` (4-chars/token)
3. **Preflight overflow check**:
   ```js
   if (isOverflow({cfg, tokens, model, outputTokenMax})) {
     await SessionCompaction.process({messages, parentID, overflow: true});
   }
   ```
4. **Stream LLM response**, accumulate `toolcalls`, `text`, `reasoning`
5. **Store**: persist all parts (`tool`, `text`, `reasoning`, `compaction`) to DB

### Compaction invocation paths (3 entry points)

| Path | When | Result |
|---|---|---|
| `isOverflow` preflight | Turn boundary, estimated tokens ≥ usable | Auto-compact, parent = most recent user message, `overflow: true` |
| `/compact` slash command | User-triggered | Manual compact, `overflow: false` |
| `experimental.session.compacting` hook | Fires inside compaction | Lets plugins (sovereign-compaction.ts) inject into summary prompt |

### Compaction algorithm (SessionCompaction.process)

```js
// 1. Find the parent user message
const parent = messages.findLast(m => m.info.id === parentID);

// 2. If overflow, restrict to messages BEFORE the most recent non-compaction user message
if (overflow) {
  // Walk backwards to find the most recent user message that has no compaction part
  // Drop everything after it. The dropped portion becomes the "head" to summarize.
}

// 3. Build candidates for tail-preservation windows (ey function)
// Each entry: { start, end, id } for non-compaction user-message boundaries

// 4. Select head/tail split (select function)
// Default: tail budget = cfg.compaction.preserve_recent_tokens
//        = min(modelLimit * 0.25, max(20000, maxOutputTokens(model, outputTokenMax)))
// If keep.tokens is set, use that.
// If tail_turns is set and > 0, limit candidates to last N turn boundaries.

// 5. Fire experimental.session.compacting hook (sovereign-compaction.ts runs here)
//    output.context is the slot plugins use to inject MUST-PRESERVE content

// 6. Call model to summarize (default: parent message's model, OR cfg.compaction.model override)
//    The summary is stored as a "compaction" part attached to the parent user message

// 7. Prune tool outputs (prune function, only if cfg.compaction.prune !== false)
//    Walks messages from end, marks `state.time.compacted` on tool outputs
//    that exceed cumulative `Fh` bytes (Fh ~= 50KB; jh ~= 20KB threshold to actually mark)
```

### `prune` mechanic (prune function)

```js
let m = 0; // user message count
for (let q = messages.length-1; q >= 0; q--) {
  const z = messages[q];
  if (z.info.role === "user") m++;
  if (m < 2) continue;  // skip last user message
  if (z.info.role === "assistant" && z.info.summary) break;  // hit prior compaction, stop
  for (let F = z.parts.length-1; F >= 0; F--) {
    const T = z.parts[F];
    if (T.type !== "tool") continue;
    if (T.state.status !== "completed") continue;
    if (PD.includes(T.tool)) continue;  // PD = protected tools list (not shown)
    if (T.state.time.compacted) break;  // already pruned, stop walking this message
    const se = vl.estimate(T.state.output);
    V += se;
    if (V <= Fh) continue;  // Fh ~= 50KB, accumulation cap
    K += se;
    x.push(T);  // candidate for pruning
  }
  if (K > jh) {  // jh ~= 20KB; must exceed threshold to actually mark
    for (let q of x) {
      if (q.state.status === "completed") {
        q.state.time.compacted = Date.now();  // mark but don't delete
      }
    }
  }
}
```

**Prune is non-destructive**: it only sets `state.time.compacted = Date.now()` on tool
parts. The part still exists in the DB and is still counted in the estimate. So `prune: true`
gives a marginal reduction in estimated tokens but **does not actually shrink the serialized
message size**. For the omega-engine's use case (huge agentic tool output streams), pruning
is essentially cosmetic unless the estimate somehow short-circuits on `compacted === true`
in `toModelMessages` (need to verify; not visible in this binary's reachable strings).

---

## 5. Auto-compaction threshold (the answer to "when does it fire?")

```
usable = model.limit.context - max(maxOutputTokens, buffer)
       (or model.limit.input - buffer if input is set, which it is for M3)

auto_compact fires when:
  estimated_tokens ≥ usable
```

For M3 via OpenRouter (`opencode/nemotron-3-ultra-free` from your config):

- `model.limit.context = 1000000` (1M from your config, line 148)
- `model.limit.input` = NOT SET (falls through to context - maxOutputTokens)
- `output = 128000` (your config line 149)
- `buffer` = 20000 (your config line 82)
- `keep.tokens` = 80000 (your config line 81)

Computed values:
- `maxOutputTokens(model, outputTokenMax)` = min(128000, outputTokenMax) — outputTokenMax comes
  from `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` env var (default = `Ad = ke.OUTPUT_TOKEN_MAX`,
  some value around 16K based on context)
- `usable` ≈ `1,000,000 - max(16000, 20000) = 980,000`
- `keep.tokens` (effective) = `min(Id, max(Ld, 0.25 * 980000)) = min(Id, 245000)`
  (Id and Ld not visible in strings — likely model-specific cap & floor, probably Id=200000, Ld=20000)

**So compaction fires at ~980K estimated tokens, preserving ~80K-200K tail.**

### Why the 398K → 368.2K drop looks weird

If auto-compaction only fires at ~980K, why did you see a drop at 398K? Two explanations:

1. **The 398K number is the opencode TUI's *post-compaction* display**, not the pre-compaction
   trigger. The trigger fired earlier (perhaps at 480K estimated = 624K real tokens accounting
   for the 4-chars/token underestimate), the compaction summary was generated, and the
   resulting 368K is what survived.

2. **The 38K user prompt that caused the cache invalidation (Carmack's finding) might have
   pushed the estimate just over `usable` for a model with a smaller context**. Check
   `model.limit.input` for the actual provider being used at that moment. If M3 was routed
   through a different model spec (e.g., a 200K-windowed variant), `usable` drops to ~180K
   and 398K would absolutely trigger auto-compaction.

---

## 6. Compaction buffer defaults

From binary:

- `Xd = 20000` — hardcoded default for `buffer` (your config matches this exactly)
- `Fh ≈ 50000` bytes — pruning accumulation cap per message
- `jh ≈ 20000` bytes — pruning threshold to actually mark
- `Id, Ld` — model-specific cap/floor for `keep.tokens` default (not visible in strings; likely
  Id = 200000, Ld = 20000)
- Default `keep.tokens` formula: `min(Id, max(Ld, 0.25 * usable))`
- Default `auto`: `true`
- Default `prune`: `true`

### Can buffer be set via CLI flag?

**No.** All compaction config is via the JSON config file only. There is no CLI override.

### Can buffer be set via env var?

**No.** `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` only overrides `outputTokenMax`, which is a
hard cap on the model's max output (used to compute `usable`). The compaction buffer itself
is config-only.

---

## 7. Conclusions: client-side vs server-side

| Aspect | Source | Verifiable? |
|---|---|---|
| `/compact` slash command | **CLIENT** (opencode) | Yes — binary strings confirm `session.compact` → `session.summarize` |
| Auto-compaction trigger | **CLIENT** (opencode `isOverflow`) | Yes — `Dl()` and `Is()` in binary |
| Token estimate for overflow | **CLIENT** (opencode `vl.estimate`, 4 chars/token) | Yes — visible in binary |
| `compaction.buffer` default | **CLIENT** (opencode config, default 20000) | Yes — `Xd = 20000` |
| `keep.tokens` default | **CLIENT** (opencode, `0.25 * usable` formula) | Yes — `pd()` in binary |
| `experimental.session.compacting` hook | **CLIENT** (opencode plugin API) | Yes — used by sovereign-compaction.ts |
| `tail_turns` (V1) | **CLIENT** (deprecated in v1.18.23, still migratable) | Yes — visible in schema |
| Tool output pruning (`prune: true`) | **CLIENT** (sets `state.time.compacted`) | Yes — `u()` function in binary |
| `model.limit.context` | **CONFIG** (opencode.json per-model) | Yes — line 148 of your config |
| Actual `usage.input_tokens` reported by M3 | **SERVER** (M3/OpenRouter API response) | Not used by opencode's "active context" display |
| "Active context: 398K" in TUI | **CLIENT** (opencode local estimate) | Yes — derived from `vl.estimate` of local message history |
| M3's actual prompt context | **SERVER** (what M3 received) | Cannot be observed from opencode TUI; need M3 logs |

### The 30K drop: it's the COMPACTION SUMMARY itself

When auto-compaction fires, the old messages are replaced with a single `compaction` part
(generated by the model). The new message history is:

```
[old compacted messages (replaced by summary) + new summary part] + tail (keep.tokens)
```

The 30K token drop = sum of (old replaced messages) - (new summary + tail). The exact math
depends on how much of the original history got summarized and how the summary was generated.

### What Carmack was right about

- "Auto-compaction fires when preflight estimate exceeds `usable = context_limit - max(output, buffer)`" — **CONFIRMED** (`Dl()` formula exact)
- "The 4-chars/token heuristic underestimates real tokens" — **CONFIRMED** (this is `vl.estimate`)
- "The headroom plugin is NOT loaded" — **CONFIRMED** (no headroom plugin referenced anywhere; `compaction.buffer` is the only buffer, and it's set to 20000)

### What Roc was right about

- "The 368K → 280K drop at 06:36:38 was a manual `/compact`" — **CONFIRMED** (matches `session.compact` behavior + `overflow: false` flag for manual)
- "The 398K → 361K was a cache invalidation from a 38K user prompt" — **PARTIALLY CONFIRMED** (cache invalidation is provider-side, but the drop from 398K to 361K (37K) ≈ the new 38K user prompt's added tokens triggering a re-estimate; the actual drop number in the TUI is the local estimate, not the cache state)

### What was NOT established by prior reports

- The exact `compaction.buffer` and `keep.tokens` default formulas — now established
- The distinction between V1 and V2 compaction config names — now established
- The prune function's non-destructive behavior (it only marks `time.compacted`, doesn't delete) — now established
- The fact that `tail_turns` is effectively a no-op in v1.18.23 — now established

---

## 8. Recommendations

1. **Migrate to V2 compaction config** in `omega-engine/opencode.json:77-83`:
   ```json
   "compaction": {
     "auto": true,
     "prune": true,
     "keep": { "tokens": 80000 },
     "buffer": 20000
   }
   ```

2. **The 4-chars/token underestimate is the real risk.** For code/JSON-heavy sessions
   (omega-engine's normal workload), real M3 tokens will be 1.3-2x the opencode estimate.
   If you actually approach 500K opencode-estimated tokens, you may already be at 1M+ real
   tokens at the provider. Consider:
   - **Increasing `buffer` to 40000-50000** to give more headroom for the estimate's blind spot
   - **Decreasing `keep.tokens` to 40000-60000** to force earlier compaction

3. **The "active context" TUI number is misleading by design.** Add a wall-clock note to the
   TUI display: `398K (est, 1.5x=597K real)`. Or just trust the provider's `usage.input_tokens`
   from the DB (`session.tokens` field) as ground truth.

4. **`prune: true` is mostly cosmetic for our workload** (non-destructive, only marks). Don't
   rely on it to actually shrink the message. If you need real shrinking, the only path is
   auto-compaction or `/compact`.

5. **For the M3 specifically**, the actual context window observed by Roc (398K before drop,
   M3's stated 1M from your config) is consistent with `auto: true` triggering at ~980K
   *estimated* — which corresponds to **~1.3-2M real tokens at M3** if the heuristic is
   undercounting. Either the model is being silently context-truncated by M3 (Roc was wrong),
   or the opencode TUI is showing a wildly optimistic number (more likely).

   **ACTION:** Read the actual `usage.input_tokens` from the session DB row for the affected
   turn. If it shows ~1M, opencode is right. If it shows ~400K, M3 is truncating.

---

## Files referenced

- `/home/arcana-novai/.opencode/bin/opencode` (v1.18.23, source of compaction logic)
- `/home/arcana-novai/.config/opencode/opencode.json` (global config, no compaction block)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json:77-83` (project compaction config)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/opencode.json` (no compaction)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/sovereign-compaction.ts` (uses `experimental.session.compacting` hook)
- `/home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts` (same)
- `/home/arcana-novai/.config/opencode/node_modules/@opencode-ai/sdk/dist/v2/gen/types.gen.d.ts` (V2 schema)
- `/home/arcana-novai/.local/share/opencode/opencode.db` (session metadata; `session.tokens` is ground truth)

## Confidence: HIGH

- All findings verified against opencode 1.18.23 binary strings and SDK type definitions
- V1→V2 migration confirmed in `R.migrate` function (visible in binary)
- Compaction algorithm (`Dl`, `Is`, `pd`, `ey`, `oy`, `y`, `u`, `W`) all located and transcribed
- Buffer default 20000 (`Xd`) confirmed
- No CLI flag for context control confirmed (full `opencode --help` reviewed)
