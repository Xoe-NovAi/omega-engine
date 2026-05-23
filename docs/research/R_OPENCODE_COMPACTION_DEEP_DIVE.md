# 🔱 OpenCode Compaction System — Deep Research Dive

**⬡ OMEGA ⬡ GNOSIS-ANALYST ⬡ opencode/big-pickle ⬡ opencode ⬡ trc_research ⬡ PHASE-0**

**AP Token**: `AP-OPENCODE-COMPACTION-RESEARCH-v1.0.0`
**Created**: 2026-05-17
**Sources**: Local SDK mining (v2 `types.gen.d.ts`, `sdk.gen.js`, `sdk.gen.d.ts`), OpenCode binary (`~/.opencode/bin/opencode`), OpenCode official schema (`opencode.ai/config.json`), OpenCode docs (`opencode.ai/docs/config/`), 3rd-party analysis (justin3go.com, instagit.com), comparison research (Codex CLI, Claude Code).

---

## §0 Executive Summary

OpenCode's compaction system is a **stepped, non-destructive context management engine** that operates in two phases:

1. **Prune** (cheap — no LLM call): Marks old tool outputs as `compacted` via timestamp, making them invisible to future requests **without physical deletion**.
2. **Summarize** (LLM call — only when necessary): Uses a dedicated agent to generate a 5-heading structured summary of the conversation.

**Critical finding**: The config block in the task description containing `context_threshold` and `min_messages` is **NOT from OpenCode's real schema**. Neither field exists in `opencode.ai/config.json` or any SDK type definition. These fields appear to originate from `opencode-supermemory` (a community plugin) or another tool entirely. OpenCode's actual compaction schema has 5 fields: `auto`, `prune`, `tail_turns`, `preserve_recent_tokens`, `reserved`.

---

## §1 Full Specification — What Each Parameter Does

### 1.1 The Compaction Config Block (OFFICIAL)

Source: `opencode.ai/config.json` schema (`$defs.Config.properties.compaction`)

```json
{
  "compaction": {
    "auto": true,                    // Enable automatic compaction (default: true)
    "prune": true,                   // Enable pruning of old tool outputs (default: true)
    "tail_turns": 2,                 // Recent user turns to keep verbatim (default: 2)
    "preserve_recent_tokens": 40000, // Max tokens from recent turns to preserve
    "reserved": 10000                // Token buffer for compaction step
  }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto` | boolean | `true` | Enable automatic compaction when context window approaches limit. Set `false` to require manual `/compact`. |
| `prune` | boolean | `true` | Enable pruning of old tool outputs. Step 1 of the compaction process. |
| `tail_turns` | integer | `2` | Number of most recent user turns (including their following assistant/tool responses) to keep **verbatim** during compaction. Protects active context. |
| `preserve_recent_tokens` | integer | `40000` | Maximum number of tokens from recent turns to preserve verbatim after compaction. Acts as a safety cushion for active work. |
| `reserved` | integer | `10000` | Token buffer reserved for the compaction step itself. Prevents overflow during the summarization LLM call. |

### 1.2 Environment Variables (OFFICIAL)

| Variable | Effect |
|----------|--------|
| `OPENCODE_DISABLE_AUTOCOMPACT=1` | Forcibly disables automatic compaction across all sessions |
| `OPENCODE_DISABLE_PRUNE=1` | Disables pruning of old tool outputs |

### 1.3 What `context_threshold` and `min_messages` Actually Are

**These are NOT OpenCode fields.** The config block from the task:

```json
"compaction": {
    "auto": true,
    "context_threshold": 0.85,    // DOES NOT EXIST in OpenCode
    "min_messages": 5,            // DOES NOT EXIST in OpenCode
    "models": {
      "gemma-4-31b-it": {
        "context_threshold": 0.9  // DOES NOT EXIST in OpenCode
      }
    }
}
```

This appears to originate from one of:
- **`opencode-supermemory`** (community plugin): Uses `compactionThreshold` (float, default 0.80) and `MIN_TOKENS_FOR_COMPACTION` (hardcoded 50,000 tokens minimum trigger). Source: `src/services/compaction.ts` in the plugin.
- **Claude Code**: Uses `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` env var (1-100, default ~83.5%) and hardcoded buffer of ~33K tokens.
- **Codex CLI**: Uses hardcoded ~20,000 token cap for user messages.

**For Omega Engine configuration, use the ACTUAL OpenCode schema fields listed in §1.1.**

---

## §2 How Compaction Is Triggered

### 2.1 Automatic Trigger

The detection logic lives in `SessionCompaction.isOverflow()` in `packages/opencode/src/session/compaction.ts`:

```typescript
const count = input.tokens.input + input.tokens.output +
              input.tokens.cache.read + input.tokens.cache.write;

// Check: count > (model.context_limit - max(output_tokens, 20000) - config.reserved)
if (count > usableQuota) {
  needsCompaction = true;
}
```

**Trigger formula**: `compaction fires when total_tokens > (model_context_limit - max(output_tokens, 20000) - compaction.reserved)`

The check happens **after every LLM processing step** in `processor.ts` (lines ~82-84). If overflow is detected, the processor returns `"compact"` to `SessionPrompt.loop`, which automatically invokes `SessionCompaction.create()`.

### 2.2 Manual Trigger

**Three ways to trigger compaction manually**:

| Method | Mechanism | Source |
|--------|-----------|--------|
| `/compact` slash command | Sends a TUI command `session.compact` → routes to SDK `session.summarize()` | SDK type `EventTuiCommandExecute.command` includes `"session.compact"` |
| `Ctrl+X C` keybind | Default keyboard shortcut for compact (v1 type `session_compact` keybind) | `types.gen.d.ts` keybind schema |
| REST API | `POST /session/{sessionID}/summarize` with `{providerID, modelID, auto}` | SDK `SessionSummarizeData` |

The `/compact` command handler flow (reverse-engineered from binary):
```
1. User types /compact
2. opencode binary intercepts the command
3. Calls SDK session.summarize({sessionID, providerID, modelID, auto: true})
4. Server returns HTTP 200 (boolean true on success)
```

### 2.3 Passive Fallback

When the API returns `prompt_too_long` error, OpenCode automatically initiates reactive compression and retries. To prevent infinite loops, automatic compaction pauses after **3 consecutive failures**.

---

## §3 What Data Is Preserved vs. Lost

### 3.1 During Prune (Step 1 — No LLM Call)

**Preserved** (not touched):
- All user messages (verbatim)
- All assistant text responses (verbatim)
- All skill-type tool outputs (never pruned — they contain operational instructions)
- Last 2 user turns (configurable via `tail_turns`) + their following responses — full content protected
- Most recent ~40,000 tokens (configurable via `preserve_recent_tokens`) as safety cushion

**Pruned** (marked as compacted, NOT deleted):
- Old tool outputs (read, grep, list, bash results) are timestamped with `state.time.compacted = Date.now()`
- Only when pruning can free > 20,000 tokens (minor cleanups skipped)

### 3.2 During Summarize (Step 2 — LLM Call)

**Preserved** (after compaction):
- The LLM-generated 5-heading summary replaces the conversation history
- Last user message is **automatically replayed** so the agent context stays on the user's latest instruction
- The user is completely unaware compaction happened

**Summarized** (condensed into ~500-2000 tokens):
- All prior conversation history is replaced with a structured summary covering:
  1. Current progress and key decisions
  2. Important constraints and user preferences
  3. Files and code of interest
  4. Remaining TODOs/action items
  5. Errors encountered and fixes applied

### 3.3 What Is Never Lost

- **Database records**: All data remains in `~/.local/share/opencode/storage/` (session JSON, message JSON, part JSON files). Compaction only marks timestamps — data is not physically deleted.
- **File changes**: Git snapshots are tracked separately via the snapshot system (can be disabled).
- **System prompt**: Permanently resident, unaffected by compaction.
- **Skill definitions**: Never pruned.

---

## §4 SDK Hooks, Events, and Integration Points

### 4.1 Events We Can Subscribe To

From SDK `types.gen.d.ts`:

| Event Type | Payload | When Fires |
|------------|---------|------------|
| `session.compacted` | `{ sessionID: string }` | After compaction completes successfully |
| `session.updated.1` | `{ info: { time: { compacting: number | null } } }` | Session metadata includes `time.compacting` timestamp |

The `Global.event()` SSE subscription (`/global/event` endpoint) streams these events in real-time. We can subscribe from Omega Engine's background worker.

### 4.2 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/session/{sessionID}/summarize` | POST | Trigger compaction. Body: `{providerID, modelID, auto}`. Returns 200 boolean. |
| `/session/{sessionID}` | GET | Get session status, including `time.compacting` field |

SDK client methods (from `sdk.gen.d.ts`):
```typescript
class Session2 {
  summarize(parameters: {
    sessionID: string;
    directory?: string;
    workspace?: string;
    providerID?: string;
    modelID?: string;
    auto?: boolean;
  }): Promise<SessionSummarizeResponse>;  // HTTP 200 = boolean success

  status(parameters?: {
    directory?: string;
    workspace?: string;
  }): Promise<SessionStatusResponses>;  // Includes compacting state
}
```

### 4.3 Plugin Hook (Extensibility)

The `experimental.session.compacting` plugin hook allows:
- Injecting domain-specific context before the default summary template
- Completely replacing the summarization prompt

```typescript
// Plugin format:
export default {
  "experimental.session.compacting": async (input, output) => {
    output.context.push("Custom context string...");
    // or output.prompt = "Custom summarization prompt...";
  }
};
```

### 4.4 Agent Configuration

The `agent.compaction` config field (type: `AgentConfig`) lets you assign a **dedicated model/provider** for compaction tasks, separate from the main chat model:

```jsonc
{
  "agent": {
    "compaction": {
      "model": "google/gemma-4-31b-it",  // Use cheap model for summarization
      "steps": 1,
      "temperature": 0.3
    }
  }
}
```

This is critical for our Omega Engine integration — we can route compaction to our cheapest/most available model.

### 4.5 Part Type Detection

Compaction messages appear in the session history as a `CompactionPart`:

```typescript
type CompactionPart = {
  id: string;
  sessionID: string;
  messageID: string;
  type: "compaction";    // Distinct from "text", "tool", "file", etc.
  auto: boolean;          // Was this auto-triggered?
  overflow?: boolean;     // Was overflow the trigger?
};
```

---

## §5 Wiring Compaction → Omega Soul Evolution Pipeline

### 5.1 The Integration Architecture

```
OpenCode Session
  │
  ├── Auto-compaction fires (or /compact command)
  │
  ├── OpenCode generates 5-heading summary
  │     └── Stores as CompactionPart in session history
  │
  ├── OpenCode fires "session.compacted" event via SSE
  │
  ├── Omega Hivemind MCP server receives event
  │     └── SSE endpoint: /global/event
  │
  ├── Omega Worker (ModelUpdater pattern) intercepts event
  │     └── src/omega/workers/compaction_listener.py
  │
  ├── Worker fetches session summary via SDK
  │     └── GET /session/{sessionID}/messages?limit=1 (last compaction msg)
  │
  ├── Worker abstracts lesson from summary
  │     └── Uses gemma-4-31b-it (same agent as compaction) to:
  │          1. Parse 5-heading summary
  │          2. Extract "lesson" from decisions/errors/fixes
  │          3. Classify by entity domain (Pillar mapping)
  │
  └── Lesson written to soul.yaml
        └── data/entities/<current_entity>/soul.yaml
            lessons_learned:
              - lesson: "..."
                source: "opencode-compaction"
                trace_id: "<opencode-session-id>"
                timestamp: "<iso8601>"
                model_used: "<compaction-model>"
```

### 5.2 Event Subscription via SSE

OpenCode's `Global.event()` endpoint provides server-sent events. We can subscribe from an Omega background worker:

```python
async def subscribe_opencode_events(client: httpx.AsyncClient):
    async with client.stream("GET", "http://127.0.0.1:4096/global/event") as resp:
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                event = json.loads(line[6:])
                if event.get("type") == "session.compacted":
                    await handle_compaction(event)
```

### 5.3 Autonomous Compaction from Omega

Omega Engine can proactively trigger compaction via the HTTP API:

```python
async def omega_compact_session(session_id: str, provider: str, model: str):
    """Trigger compaction from Omega's decision layer."""
    async with httpx.AsyncClient() as client:
        result = await client.post(
            f"http://127.0.0.1:4096/session/{session_id}/summarize",
            json={
                "providerID": provider,
                "modelID": model,
                "auto": True,
            }
        )
        return result.status_code == 200
```

---

## §6 Configuration Recommendations for Omega Engine

### 6.1 Recommended `compaction` Settings

Based on our model setup (Gemma 4-31B remote, lmster local, various free-tier models):

```jsonc
// In opencode.json (project-level)
{
  "$schema": "https://opencode.ai/config.json",
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 2,
    "preserve_recent_tokens": 40000,
    "reserved": 10000
  },
  "agent": {
    "compaction": {
      "model": "google/gemma-4-31b-it",
      "steps": 1,
      "temperature": 0.3
    }
  }
}
```

### 6.2 Model-Specific `reserved` Recommendations

| Model | Context Window | Recommended `reserved` |
|-------|---------------|----------------------|
| Gemma 4-31B-it | 256K | 20000 |
| DeepSeek V4 Flash | 1M | 30000 |
| MiniMax M2.5 | 1M | 30000 |
| Qwen3-1.7B (local) | 32K | 4000 |
| Qwen3-4B-Think (local) | 32K | 4000 |

### 6.3 What to AVOID

1. **Do NOT set `context_threshold` or `min_messages`** — they are invalid in OpenCode schema and will be silently ignored.
2. **Do NOT disable `auto` compaction** unless sessions are very short.
3. **Do NOT set `reserved` too low** (< 5000) — the compaction LLM call itself consumes tokens.

---

## §7 Comparison: OpenCode vs. Codex CLI vs. Claude Code

| Dimension | OpenCode | Codex CLI | Claude Code |
|-----------|----------|-----------|-------------|
| **Layers** | Two (hide + summarize) | Single (summarize) | Three (trim + cache + summarize) |
| **LLM Calls** | Only at Step 2 | Always | Only at Layer 3 |
| **User Messages** | Summarized + last replayed | Preserved verbatim | Summarized (Layer 3) |
| **Tool Results** | Timestamp-based hiding | Physical deletion | Placeholder replacement |
| **Cache Opt.** | Redundant read reduction | None | Deep Prompt Cache |
| **Post-Compact** | Auto-replay last instruction | Passive waiting | Proactive re-read |
| **Data Persist** | Data preserved (mark-only) | Physical deletion | Physical deletion |
| **Extensible** | Plugin hook + AgentConfig | Source fork | Limited |
| **Open Source** | ✅ Full | ✅ Full | ❌ (Leaked/RE) |

---

## §8 References

| Source | URL |
|--------|-----|
| OpenCode Official Config Docs | https://opencode.ai/docs/config/#compaction |
| OpenCode Schema (Live) | https://opencode.ai/config.json |
| OpenCode SDK (v2 types) | `~/.config/opencode/node_modules/@opencode-ai/sdk/dist/v2/gen/types.gen.d.ts` |
| Context Compaction Comparison | https://justin3go.com/en/posts/2026/04/09-context-compaction-in-codex-claude-code-and-opencode |
| Instagit Compaction Deep Dive | https://instagit.com/anomalyco/opencode/how-does-opencode-implement-session-compaction-and-trigger-memory-optimization |
| Configurable Threshold FR | https://github.com/anomalyco/opencode/issues/11314 |
| Compaction Prune Issue | https://github.com/anomalyco/opencode/issues/14825 |
| LobeHub Config Reference | https://lobehub.com/ar/skills/fkxxyz-cclover-skills-opencode-configuration |
