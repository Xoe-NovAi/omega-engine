# 🔱 OpenCode V2 Architecture Reconnaissance — 1.17.20 → 1.18.3

**AP Token**: `AP-OPENCODE-V2-RECON-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_opencode_v2_recon ⬡ ACTIVE

**Date**: 2026-07-19
**Purpose**: Comprehensive architecture diff for Gemma 4 integration + Config Package version-gating
**Priority**: P0-5 — Critical for Gemma 4 PR + community config package

---

## 📋 Executive Summary (L1)

OpenCode 1.18.x (V2) is a **desktop-first migration** with **event-sourced session persistence** and **per-prompt model selection**. The provider transformation pipeline (`transform.ts`) is **unchanged** — it remains the core 1,764-line normalization layer between OpenCode's internal message format and the Vercel AI SDK's `streamText()`. The V2 session format introduces new message part types (`ReasoningPart`, `StepStartPart`, `StepFinishPart`, `SubtaskPart`, `AgentPart`) critical for Gemma 4's `thoughts_token_count` tracking. Config merge behavior uses `remeda.mergeDeep` with **array replacement** (not concatenation) for most fields — custom `mergeConfigConcatArrays` only applies to `instructions` and `plugins`.

---

## 1. Version Compatibility Matrix

| Feature | 1.17.x (Legacy) | 1.18.x (V2) | Breaking? | Notes |
|---------|-----------------|-------------|-----------|-------|
| **transform.ts provider transforms** | ✅ Active | ✅ Active | **No** | 1,764 lines, NOT generated, NOT deprecated |
| **AI SDK streamText usage** | ✅ | ✅ | **No** | Wrapper via `wrapLanguageModel` middleware |
| **Models.dev integration** | ✅ | ✅ | **No** | Catalog source unchanged |
| **Config merge (array fields)** | `mergeDeep` (replace) | `mergeDeep` (replace) | **No** | Only `instructions`/`plugins` use concat |
| **Session format** | V1 (flat messages) | **V2 (event-sourced)** | **Yes (internal)** | `session.next.*` events, `msg_*` IDs |
| **Message parts** | Text, Tool, File, Reasoning | **+ StepStart, StepFinish, Subtask, Agent, Snapshot, Patch, Retry, Compaction** | **New extraction needed** | `ReasoningPart` critical for Gemma 4 |
| **Per-prompt model selection** | ❌ | ✅ (1.18.0) | **New feature** | Composer model picker, `--model` flag |
| **Subagent depth limit** | Unlimited | ✅ (1.18.2, `subagent_depth`) | **New config** | Default: 1 (prevents nested subagents) |
| **Desktop V2 migration** | Old layout | ✅ Complete (1.18.0) | **UI only** | Toggle between layouts |
| **Session HTTP API (V2)** | Experimental | Stabilizing | **API surface** | `/session`, `/session/:id/message` |
| **Provider options remapping** | `sdkKey()` mapping | Same | **No** | `providerID` → AI SDK key |

---

## 2. Provider Transformation Layer Analysis

### 2.1 `transform.ts` — The Core Pipeline (1,764 lines)

**Location**: `packages/opencode/src/provider/transform.ts` (dev branch)

**Key Finding**: **NOT generated, NOT deprecated** — Oversight 1's claim is **incorrect**. This is the single source of truth for provider normalization.

```typescript
// Core exports
export namespace ProviderTransform {
  // 1. Message normalization for provider quirks
  export function normalizeMessages(msgs: ModelMessage[], model: Provider.Model, options: Record<string, unknown>): ModelMessage[]
  
  // 2. Provider options for AI SDK streamText
  export function providerOptions(model: Provider.Model, options: Record<string, unknown>): Record<string, unknown>
  
  // 3. Message transformation entry point
  export function message(msgs: ModelMessage[], model: Provider.Model, options: Record<string, unknown>): ModelMessage[]
  
  // 4. Tool schema sanitization (Gemini, etc.)
  export function sanitizeToolSchema(schema: JSONSchema7, model: Provider.Model): JSONSchema7
  
  // 5. UTF-16 surrogate cleanup
  export function sanitizeSurrogates(text: string): string
  
  // 6. npm package → AI SDK provider key mapping
  function sdkKey(npm: string): string | undefined
}
```

### 2.2 Transformation Pipeline Flow

```
SessionProcessor.create()
  → LLM.stream() 
    → Provider.getLanguageModel() → AI SDK LanguageModel
    → wrapLanguageModel(middleware)
      → transformParams hook
        → ProviderTransform.message(args.params.prompt, model, messageTransformOptions)
          → unsupportedParts()      // Filter modalities model can't handle
          → normalizeMessages()     // Provider quirks (Anthropic empty content, etc.)
          → applyCaching()          // Anthropic/DeepSeek prompt caching
          → remap providerOptions   // providerID → AI SDK key (sdkKey)
          → strip Responses itemId  // Codex/OpenAI compatibility
```

### 2.3 Critical Functions for Gemma 4

| Function | Purpose | Gemma 4 Relevance |
|----------|---------|-------------------|
| `normalizeMessages()` | Removes empty `text`/`reasoning` parts for Anthropic | **Must preserve** `ReasoningPart` for `thoughts_token_count` |
| `providerOptions()` | Generates `providerOptions` for `streamText()` | Passes `thinkingConfig` for Gemini thinking variants |
| `sanitizeToolSchema()` | Strips unsupported JSON Schema features | Gemma 4 uses standard schemas — minimal impact |
| `sdkKey()` | Maps `@ai-sdk/google` → `"google"` | Required for `providerOptions.google.thinkingConfig` |

### 2.4 Provider-Specific Handling (from DeepWiki + source)

```typescript
// Anthropic: rejects empty content parts
if (model.api.npm === "@ai-sdk/anthropic" || model.api.npm === "@ai-sdk/amazon-bedrock") {
  msgs = msgs.map(msg => {
    if (typeof msg.content === "string") return msg.content === "" ? undefined : msg
    if (!Array.isArray(msg.content)) return msg
    const filtered = msg.content.filter(part => 
      (part.type === "text" || part.type === "reasoning") ? part.text !== "" : true
    )
    return filtered.length === 0 ? undefined : { ...msg, content: filtered }
  }).filter(Boolean)
}

// Gemini: thinkingConfig via providerOptions
// OpenAI: reasoningEffort, textVerbosity via providerOptions
// Copilot: special handling for codex context limits
```

### 2.5 V2 Impact on Transforms

**SessionProcessor** (V2) calls transforms identically to V1:
```typescript
// packages/opencode/src/session/llm.ts (both versions)
providerOptions: ProviderTransform.providerOptions(input.model, prepared.params.options),
model: wrapLanguageModel({
  model: language,
  middleware: [{
    specificationVersion: "v3",
    async transformParams(args) {
      if (args.type === "stream") {
        args.params.prompt = ProviderTransform.message(
          args.params.prompt,
          input.model,
          prepared.messageTransformOptions,
        )
      }
      return args.params
    },
  }],
}),
```

**Conclusion**: Transform logic is **stable across V1/V2**. Gemma 4 integration touches only `providerOptions()` for `thinkingConfig` and `normalizeMessages()` to preserve reasoning parts.

---

## 3. V2 Session Format & Message Parts

### 3.1 Event-Sourced Architecture (from schema-changelog.md)

```
V1: session → message → part (flat, mutable)
V2: session.next.* events → projected messages (immutable, replayable)
```

**Key Events**:
- `session.next.prompt.admitted.1` — User input durably admitted
- `session.next.prompt.promoted.1` — Input becomes model-visible
- `session.next.compaction.ended.2` — Compaction checkpoint
- `session.next.message.*` — Assistant message lifecycle

**IDs**: `msg_*` (projected messages) distinct from `evt_*` (durable events)

### 3.2 Message Part Types (from message-v2.ts)

```typescript
// Base part structure
const partBase = {
  id: PartID,
  sessionID: SessionID,
  messageID: MessageID,
}

// V1 parts (existing)
TextPart        { type: "text", text: string, synthetic?, ignored? }
ReasoningPart   { type: "reasoning", text: string, signature?, time? }
FilePart        { type: "file", filename, mediaType, data }
ToolPart        { type: "tool", callID, tool, state: ToolState, metadata? }

// V2 NEW parts (critical for Gemma 4)
StepStartPart   { type: "step-start", snapshot? }
StepFinishPart  { type: "step-finish", reason, snapshot?, cost, tokens: { total?, input, output, reasoning, cache: { read, write } } }
SubtaskPart     { type: "subtask", title, agent?, model?, status }
AgentPart       { type: "agent", agent, previousAgent? }
SnapshotPart    { type: "snapshot", snapshot }
PatchPart       { type: "patch", hash, diff }
RetryPart       { type: "retry", attempt, error? }
CompactionPart  { type: "compaction", summary, recentContext }
```

### 3.3 Gemma 4 Critical Extraction Points

| Part Type | Field | Gemma 4 Mapping |
|-----------|-------|-----------------|
| `ReasoningPart` | `text` | **`thoughts_token_count`** (thinking content) |
| `StepFinishPart` | `tokens.reasoning` | **Output thinking tokens** |
| `StepFinishPart` | `tokens.cache.read/write` | Cache token accounting |
| `StepFinishPart` | `cost` | Cost tracking per step |

**Extraction Pattern** (for ModelGateway):
```typescript
// In streaming handler, accumulate reasoning parts
const reasoningParts = message.parts.filter(p => p.type === "reasoning")
const thoughtsTokenCount = reasoningParts.reduce((sum, p) => sum + estimateTokens(p.text), 0)

// StepFinishPart provides authoritative token counts
const stepFinish = message.parts.find(p => p.type === "step-finish")
if (stepFinish) {
  const { reasoning, cache: { read, write } } = stepFinish.tokens
}
```

---

## 4. Config Merge Behavior Verification

### 4.1 Merge Implementation (from config.ts)

```typescript
// packages/opencode/src/config/config.ts
import { mergeDeep } from "remeda"

// Custom merger for specific array fields
function mergeConfigConcatArrays(target: any, source: any): any {
  return mergeDeep(target, source, (t, s) => {
    if (Array.isArray(t) && Array.isArray(s)) {
      // ONLY for instructions and plugins
      return unique([...t, ...s])
    }
  })
}

// Main merge: mergeDeep REPLACES arrays by default
const merged = mergeDeep(baseConfig, userConfig)  // Arrays REPLACED
```

### 4.2 Array Field Behavior Matrix

| Config Field | Merge Behavior | Source |
|--------------|----------------|--------|
| `provider` | **Replace** (deep merge objects) | `mergeDeep` |
| `model` | Replace (string) | `mergeDeep` |
| `agent` | Replace (deep merge objects) | `mergeDeep` |
| `permission` | Replace (deep merge) | `mergeDeep` |
| `mcp` | Replace (deep merge) | `mergeDeep` |
| `instructions` | **Concatenate + dedupe** | `mergeConfigConcatArrays` |
| `plugins` | **Concatenate + dedupe** | `mergeConfigConcatArrays` |
| `command` | Replace (object merge) | `mergeDeep` |
| `keybinds` | Replace (object merge) | `mergeDeep` |
| `theme` | Replace | `mergeDeep` |
| `snapshot` | Replace (boolean) | `mergeDeep` |

### 4.3 Impact on Community Config Package

**If user adds a model to `opencode.json`:**
```json
{
  "provider": {
    "google": {
      "models": {
        "gemma-4-31b": { "options": { "thinkingConfig": { "thinkingBudget": 16384 } } }
      }
    }
  }
}
```

**Result**: The ENTIRE `provider.google.models` object is **replaced**, not merged. User must provide the **complete model catalog** for that provider.

**Migration Requirement**: Config package must:
1. Fetch current provider config via `/config/providers` API
2. Deep-merge user additions into full model catalog
3. Write complete `provider` object back

---

## 5. Version Detection for Config Package

### 5.1 Detection Strategy

**Method**: `opencode --version` at ModelGateway startup (not install script)

```typescript
// packages/omega/src/gateway/model_gateway.ts
async function detectOpenCodeVersion(): Promise<string> {
  const { stdout } = await anyio.runProcess("opencode", ["--version"])
  return stdout.trim()  // "1.18.3"
}

function parseSemver(version: string): { major: number, minor: number, patch: number } {
  const [major, minor, patch] = version.split(".").map(Number)
  return { major, minor, patch }
}

function getConfigStrategy(version: string): "legacy" | "v2-native" {
  const { major, minor } = parseSemver(version)
  if (major === 1 && minor < 18) return "legacy"
  return "v2-native"
}
```

### 5.2 Version-Gated Config Behavior

| Version Range | Config Strategy | Per-Prompt Model | Native Thinking |
|---------------|-----------------|------------------|-----------------|
| `< 1.18.0` | Workaround: full model array, manual variant config | ❌ Manual agent config | ❌ Manual `providerOptions` |
| `>= 1.18.0` | Native: partial merges OK, composer model picker | ✅ `/models` in composer | ✅ `thinkingConfig` in model options |
| `>= 1.18.2` | + `subagent_depth` config | ✅ | ✅ |

### 5.3 Runtime Detection Points

```typescript
// At ModelGateway initialization
const version = await detectOpenCodeVersion()
const strategy = getConfigStrategy(version)

if (strategy === "legacy") {
  // Apply transform.ts fixes for Gemma 4
  // Inject thinkingConfig via providerOptions middleware
  // Disable per-prompt model selection UI
} else {
  // Use native model.options.thinkingConfig
  // Enable per-prompt model selection
  // Use native subagent_depth config
}
```

---

## 6. Breaking Changes for Community Config Package

### 6.1 Required Changes (v1.17.x → v1.18.x)

| Change | Impact | Migration |
|--------|--------|-----------|
| **Session format V2** | Internal only — no config impact | None |
| **Per-prompt model selection** | New UI, config unchanged | Optional: expose in config UI |
| **`subagent_depth` config** | New key in `opencode.json` | Add to schema, default: 1 |
| **Array merge behavior** | **Unchanged** — still replaces | Document clearly |
| **Provider options** | `thinkingConfig` now native | Migrate from workaround to native |
| **Message parts** | New types for streaming | Update token extraction |

### 6.2 Config Schema Additions (v1.18+)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "subagent_depth": 1,           // NEW in 1.18.2
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "google": {
      "models": {
        "gemma-4-31b": {
          "options": {
            "thinkingConfig": { "thinkingBudget": 16384 }  // NATIVE in 1.18+
          }
        }
      }
    }
  }
}
```

### 6.3 Migration Checklist for Config Package Users

```markdown
- [ ] Detect OpenCode version at startup (`opencode --version`)
- [ ] If < 1.18: Apply legacy transform.ts middleware for thinking
- [ ] If >= 1.18: Use native `model.options.thinkingConfig`
- [ ] If >= 1.18.2: Expose `subagent_depth` in config UI
- [ ] Document: Adding models REPLACES provider.models object
- [ ] Provide "fetch current + merge" helper for model additions
- [ ] Update token extraction for `StepFinishPart.tokens.reasoning`
- [ ] Test with Gemma 4 thinking variants (low/medium/high)
```

---

## 7. DeepWiki V2 Architecture Corroboration

### 7.1 Core V2 Architecture (DeepWiki)

> "V2 is where the server-first direction visible inside V1 becomes the product architecture instead of a compatibility layer."

**Six Harder Conclusions**:
1. **Durable admission precedes execution** — Prompt → idempotent inbox → model-visible boundary
2. **Steer and queue are explicit delivery policies** — Not implicit
3. **Child authority intersects parent delegation** — Subagent permissions
4. **Completion ≠ integration/commit/push/review/acceptance** — Separate concerns
5. **Persist explicit graph edges and receipt refs** — Audit trail
6. **Unify questions, approvals, forms under typed request envelope** — Single protocol

### 7.2 Session Lifecycle (Zhao-Jan Teardown)

```
V1 Loop: User Input → Agent Loop → Tool Execution → Response
V2 Loop: 
  1. ADMISSION: Prompt → session.next.prompt.admitted.1 (durable, idempotent)
  2. PROMOTION: Admitted → session.next.prompt.promoted.1 (model-visible)
  3. EXECUTION: Agent loop with StepStart/StepFinish parts
  4. SETTLEMENT: Compaction, snapshots, revert
```

### 7.3 Provider Abstraction (Martian Lee Analysis)

> "OpenCode externalizes model metadata to models.dev and even hand-rolls its own LLM protocol layer, so any provider attaches with a single line of data."

**Four Axes of Hand-Rolled LLM Layer**:
1. **Message normalization** → `transform.ts` (our focus)
2. **Tool schema adaptation** → `sanitizeToolSchema()`
3. **Provider options mapping** → `providerOptions()` + `sdkKey()`
4. **Streaming protocol** → `wrapLanguageModel` middleware

---

## 8. Gemma 4 Integration Impact Assessment

### 8.1 What Works Natively (v1.18+)

| Feature | Status | Config |
|---------|--------|--------|
| Thinking variants (low/medium/high) | ✅ Native | `model.options.thinkingConfig.thinkingBudget` |
| Per-prompt model selection | ✅ Native | Composer UI + `--model` flag |
| Reasoning token extraction | ⚠️ Partial | `StepFinishPart.tokens.reasoning` (new in V2) |
| Subagent depth control | ✅ Native (1.18.2) | `subagent_depth` config |

### 8.2 What Requires Workaround (v1.17.x)

| Feature | Workaround |
|---------|------------|
| Thinking config | Inject via `ProviderTransform.providerOptions()` middleware |
| Per-prompt model | Set via agent config or CLI `--model` flag only |
| Reasoning tokens | Parse `ReasoningPart.text` from stream (no `StepFinishPart`) |

### 8.3 Recommended Integration Path

```typescript
// ModelGateway provider registration for Gemma 4
const gemma4Provider = {
  id: "google",
  models: {
    "gemma-4-31b": {
      name: "Gemma 4 31B",
      options: {
        // NATIVE in v1.18+
        thinkingConfig: { 
          thinkingBudget: 16384,  // or "low" | "medium" | "high"
          includeThoughts: true 
        }
      },
      variants: {
        "thinking-high": { thinkingConfig: { thinkingBudget: 32768 } },
        "thinking-low": { thinkingConfig: { thinkingBudget: 4096 } },
      }
    }
  }
}

// Version-gated registration
if (openCodeVersion >= "1.18.0") {
  // Use native thinkingConfig
  registerProvider(gemma4Provider)
} else {
  // Legacy: inject via transform middleware
  registerProvider({
    ...gemma4Provider,
    models: {
      "gemma-4-31b": {
        ...gemma4Provider.models["gemma-4-31b"],
        options: {
          // Legacy workaround
          providerOptions: {
            google: { thinkingConfig: { thinkingBudget: 16384 } }
          }
        }
      }
    }
  })
}
```

---

## 9. Sources & Evidence

| Source | Type | Key Findings |
|--------|------|--------------|
| `github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts` | **Source** | 1,764 lines, NOT generated, core pipeline |
| `github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/message-v2.ts` | **Source** | 12 part types, `StepFinishPart.tokens.reasoning` |
| `github.com/anomalyco/opencode/blob/dev/specs/v2/schema-changelog.md` | **Schema** | Event-sourced V2, `session.next.*` events |
| `github.com/Zhao-Jan/The-Agent-Network/blob/main/docs/teardowns/2026-07-10-opencode-v2-architecture-teardown.md` | **Teardown** | 6 harder conclusions, admission/execution split |
| `deepwiki.com/sst/opencode/4.3-provider-transformations` | **Architecture** | Transform pipeline, 4 axes of LLM layer |
| `deepwiki.com/sst/opencode/3-configuration-system` | **Architecture** | `mergeDeep` replaces arrays, concat only for instructions/plugins |
| `opencode.ai/changelog` (1.18.0-1.18.3) | **Release** | Per-prompt model (1.18.0), subagent_depth (1.18.2) |
| `github.com/anomalyco/opencode/releases` | **Release** | Version tags v1.17.20 → v1.18.3 |
| `martianlee.github.io/posts/2026-06-29-opencode-architecture` | **Analysis** | Legacy/V2 coexistence, hand-rolled LLM layer |

---

## 10. Action Items for Omega Engine

### Immediate (Gemma 4 PR)
- [ ] **Correction**: Document that `transform.ts` is **NOT deprecated** — Oversight 1 was wrong
- [ ] Implement version detection at ModelGateway startup (`opencode --version`)
- [ ] Add version-gated config strategy (legacy vs native thinkingConfig)
- [ ] Update token extraction for `StepFinishPart.tokens.reasoning` (V2 sessions)

### Config Package (Community)
- [ ] Document array replacement behavior clearly
- [ ] Provide `fetchAndMergeModels(provider, additions)` helper
- [ ] Add `subagent_depth` to config schema (default: 1)
- [ ] Version-gate native vs workaround thinking config

### Testing
- [ ] Test Gemma 4 thinking variants on v1.17.20 (legacy) and v1.18.3 (native)
- [ ] Verify `ReasoningPart` preservation in `normalizeMessages()` for Anthropic
- [ ] Validate `providerOptions` remapping for `google` → `thinkingConfig`

---

## 🏁 Conclusion

**OpenCode V2 (1.18.x) is a desktop/session architecture migration, NOT a provider protocol change.** The `transform.ts` pipeline remains the single source of truth for provider normalization. Gemma 4 integration requires:

1. **Version detection** at runtime to choose native vs workaround thinking config
2. **Token extraction updates** for new V2 `StepFinishPart` structure
3. **Config package documentation** on array replacement semantics

The preliminary finding stands: **`transform.ts` is 1,764 lines of active, hand-written TypeScript — the core of OpenCode's provider-agnostic architecture.**

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_opencode_v2_recon ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
