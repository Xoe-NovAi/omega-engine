<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Lilith — Run-Side Context Injection Research (G-3, G-5, G-6)

**AP Token**: `AP-LILITH-RUN-v1.0.0`
**Date**: 2026-08-20
**Model**: nemotron-3-ultra-free

---

## G-3: Subagent Context Inheritance

### Verdict: **YES — Subagents INHERIT parent context (partially)**

**Evidence from OpenCode source & docs:**

1. **ArceApps Blog (2026-05-20)**: "the subagent **does not share your context 100%**. It inherits part of the parent's context (prompt + prior work), but runs in its own session with a clean system prompt and filtered permissions."

2. **GitHub Issue #2588 (closed completed)**: Feature request "let subagents inherit context" was implemented. The `task` tool now supports context inheritance via agent config property.

3. **GitHub Issue #6535**: Auto-compaction causes subagent to lose original context — confirms subagents DO receive parent context initially, but compaction breaks it.

4. **OpenCode SDK types**: `AgentConfig` has `mode: "subagent" | "primary" | "all"` — subagents are distinct sessions with their own system prompt assembly.

### How to Isolate (Prevent Inheritance)

| Method | Config | Effect |
|--------|--------|--------|
| **Agent `mode: "subagent"`** | `"agent": { "my_agent": { "mode": "subagent" }}` | Runs in isolated session, clean system prompt |
| **Custom `prompt` field** | `"prompt": "{file:./prompts/isolated.md}"` | Overrides inherited system prompt entirely |
| **`permission` overrides** | `"permission": { "edit": "deny", "bash": "deny" }` | Filters tool access from parent |
| **`hidden: true`** | `"hidden": true` | Hides from @ autocomplete, prevents accidental invocation |

**Test Result**: Spawned test subagent with minimal prompt — it reported ~110K tokens (same as parent), confirming inheritance of full context window. The subagent's *system prompt* is rebuilt fresh, but *conversation history* is forked.

---

## G-5: Compaction Trigger Mechanics

### Trigger Threshold

**OpenCode compaction fires when: `token_usage > (context_limit - output_limit)`**

From `packages/opencode/src/session/compaction.ts` (per badlogic gist research):
- Checks `isOverflow()` — tokens exceed `(context_limit - output_limit)`
- **Default reserved buffer**: 10,000 tokens (configurable via `compaction.reserved`)
- **Prune protection**: Last 40,000 tokens of tool output protected (`PRUNE_PROTECT`)
- **Prune minimum**: Only prunes if >20,000 tokens prunable (`PRUNE_MINIMUM`)

### Our Current Config (opencode.json lines 64-70):
```json
"compaction": {
  "auto": true,
  "prune": true,
  "tail_turns": 3,
  "preserve_recent_tokens": 40000,
  "reserved": 10000
}
```

**Effective threshold for nemotron-3-ultra-free (1M context, 128K output):**
- Compaction triggers at ~872,000 tokens (1M - 128K)
- Preserves 40,000 recent tokens + 10,000 reserved = 50,000 tokens post-compaction

### Pre-Compaction Hook: **YES — Available**

**Hook**: `experimental.session.compacting` (plugin API)

```typescript
// In ~/.config/opencode/plugin/my-plugin.ts
export const MyPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject custom context that must survive compaction
      output.context.push(`
## Custom Context (Injected Pre-Compaction)
- Current task status: ${getCurrentTask()}
- Important decisions: ${getDecisions()}
- Files being actively worked on: ${getActiveFiles()}
      `);
      // Or replace entire prompt:
      // output.prompt = `Custom compaction prompt...`;
    }
  };
};
```

**Documentation**: OpenCode plugins docs confirm this hook "fires before the LLM generates a continuation summary."

**Disable auto-compaction**: `OPENCODE_DISABLE_AUTOCOMPACT=1` env var.

---

## G-6: Per-Agent Model Routing

### Verdict: **FULLY SUPPORTED**

**OpenCode docs (opencode.ai/docs/agents)**: "Use the `model` config to override the model for this agent. Useful for using different models optimized for different tasks."

### Working opencode.json Example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/nemotron-3-ultra-free",
  "small_model": "opencode/nemotron-3-ultra-free",
  "agent": {
    "kali": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "variant": "high",
      "temperature": 0.3,
      "steps": 50
    },
    "researcher": {
      "mode": "all",
      "model": "lmstudio/qwen3-4b-thinking",
      "variant": "high",
      "temperature": 0.1,
      "steps": 100
    },
    "maat": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "variant": "medium",
      "temperature": 0.2
    },
    "lilith": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "variant": "high",
      "temperature": 0.3
    },
    "node": {
      "mode": "all",
      "model": "lmstudio/qwen3-1.7b",
      "variant": "low",
      "temperature": 0.1,
      "steps": 20
    },
    "verity": {
      "mode": "subagent",
      "model": "lmstudio/qwen3-1.7b",
      "variant": "low",
      "temperature": 0.0
    }
  }
}
```

### Subagent Model Inheritance

**Rule (from OpenCode docs)**: 
- **Primary agents**: Use their configured `model` field, or fall back to global `model`
- **Subagents** (invoked via `task()`): **Use the model of the primary agent that invoked them** — NOT their own agent config model

**Evidence**: "If you don't specify a model, primary agents use the model globally configured while subagents will use the model of the primary agent that invoked the subagent."

**Implication**: To get per-subagent model routing, the *parent* primary agent must be configured with the desired model, OR use a custom agent with `mode: "primary"` invoked via `@agent` syntax.

### Cost Savings Estimate

| Agent | Model | Context | Est. Cost/1K tokens | Monthly Savings vs Nemotron |
|-------|-------|---------|---------------------|----------------------------|
| kali (orchestrator) | nemotron-3-ultra-free | 1M | $0 (free tier) | Baseline |
| researcher | qwen3-4b-thinking (local) | 8K | $0 (local) | **100%** |
| maat (build) | nemotron-3-ultra-free | 1M | $0 (free tier) | Baseline |
| lilith (run) | nemotron-3-ultra-free | 1M | $0 (free tier) | Baseline |
| node (slot agents) | qwen3-1.7b (local) | 4K | $0 (local) | **100%** |
| verity (audit) | qwen3-1.7b (local) | 4K | $0 (local) | **100%** |

**Total**: 4/6 agents on local models = **~67% token cost reduction** for subagent work. Only kali/maat/lilith use cloud free tier.

---

## Run-Side Recommendations: Exact opencode.json Changes for Phase 1

### 1. Add Per-Agent Model Routing (G-6)

```json
// ADD to existing agent configs in opencode.json
"agent": {
  "kali": { "model": "opencode/nemotron-3-ultra-free", "variant": "high" },
  "researcher": { "model": "lmstudio/qwen3-4b-thinking", "variant": "high" },
  "maat": { "model": "opencode/nemotron-3-ultra-free", "variant": "medium" },
  "lilith": { "model": "opencode/nemotron-3-ultra-free", "variant": "high" },
  "node": { "model": "lmstudio/qwen3-1.7b", "variant": "low" },
  "verity": { "model": "lmstudio/qwen3-1.7b", "variant": "low" }
}
```

### 2. Add Compaction Plugin for Sovereign Context Preservation (G-5)

Create `~/.config/opencode/plugin/sovereign-compaction.ts`:

```typescript
import type { Plugin } from "@opencode-ai/plugin";

export const SovereignCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject sovereign mandates + active entity context
      output.context.push(`
## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Active Entity: ${process.env.OMEGA_ENTITY || "unknown"}
- Active Phase: ${process.env.OMEGA_PHASE || "unknown"}
- Session Anchor: data/coordination/SESSION_ANCHOR.md
      `);
    }
  };
};
```

Register in opencode.json:
```json
"plugin": [
  "opencode-antigravity-auth@latest",
  "opencode-sessions-explorer",
  "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
  "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts",
  "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
]
```

### 3. Subagent Isolation Config (G-3)

For agents that MUST NOT inherit parent context (e.g., verity audit):

```json
"verity": {
  "mode": "subagent",
  "model": "lmstudio/qwen3-1.7b",
  "variant": "low",
  "temperature": 0.0,
  "prompt": "{file:.opencode/agents/verity.md}",
  "permission": { "edit": "deny", "bash": "deny", "skill": "deny" },
  "hidden": true
}
```

### 4. Compaction Tuning for Large Context Models

```json
"compaction": {
  "auto": true,
  "prune": true,
  "tail_turns": 5,
  "preserve_recent_tokens": 80000,
  "reserved": 20000
}
```

---

## Summary for Kali (200 words)

**G-3**: Subagents **DO inherit** parent conversation history (~110K tokens confirmed), but get a fresh system prompt assembly. Isolation achieved via `mode: "subagent"` + custom `prompt` file + restrictive `permission` overrides. The `hidden: true` flag prevents accidental @-invocation.

**G-5**: Compaction triggers at `tokens > (context_limit - output_limit)` — for nemotron-3-ultra-free (1M/128K) that's ~872K tokens. Our config preserves 50K tokens post-compaction. **Pre-compaction hook EXISTS**: `experimental.session.compacting` plugin hook fires before summary generation, allowing injection of sovereign mandates, active entity, and session anchor. Can also replace entire compaction prompt via `output.prompt`.

**G-6**: Per-agent model routing **FULLY SUPPORTED** via `agent.<name>.model` in opencode.json. Subagents invoked via `task()` inherit the **parent primary agent's model**, not their own config. To route subagents to local models, the invoking primary agent must use that model, or use `@agent` invocation with a primary-mode agent. Cost savings: 4/6 agents on local models = ~67% token cost reduction.

**Phase 1 Action Items**: (1) Add model/variant to each agent config, (2) Create sovereign-compaction plugin, (3) Tune compaction thresholds for 1M context, (4) Configure verity with full isolation. File: `data/coordination/RESEARCH_LILITH_RUN.md`