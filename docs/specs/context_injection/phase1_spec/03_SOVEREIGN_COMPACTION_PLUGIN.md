# Sovereign Compaction Plugin — Full TypeScript Implementation

**Target**: `~/.config/opencode/plugin/sovereign-compaction.ts`  
**Hook**: `experimental.session.compacting` (fires BEFORE summary generation)  
**Authority**: Phase 1 Plan + Carmack Review Q3.3 (plugin = defense-in-depth; checkpoint at 80% is primary)

---

## Complete Implementation

```typescript
// ~/.config/opencode/plugin/sovereign-compaction.ts
// Sovereign Compaction Plugin — Injects mandates/entity/phase/anchor pre-compaction
// Hook: experimental.session.compacting (fires during compaction, before summary)

import type { Plugin } from "@opencode-ai/plugin";

export const SovereignCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Read environment for active entity/phase (set by session startup)
      const entity = process.env.OMEGA_ENTITY || "unknown";
      const phase = process.env.OMEGA_PHASE || "unknown";
      
      // Session anchor path (hydration source)
      const anchorPath = "data/coordination/SESSION_ANCHOR.md";
      
      // Condensed mandates (Tier 0 - survives compaction)
      const mandates = `
## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Active Entity: ${entity}
- Active Phase: ${phase}
- Session Anchor: ${anchorPath}
      `.trim();

      // Inject at the TOP of context so it survives pruning
      output.context.unshift(mandates);
    }
  };
};
```

---

## Installation

```bash
mkdir -p ~/.config/opencode/plugin
cat > ~/.config/opencode/plugin/sovereign-compaction.ts << 'EOF'
import type { Plugin } from "@opencode-ai/plugin";

export const SovereignCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      const entity = process.env.OMEGA_ENTITY || "unknown";
      const phase = process.env.OMEGA_PHASE || "unknown";
      const anchorPath = "data/coordination/SESSION_ANCHOR.md";
      
      const mandates = `
## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Active Entity: ${entity}
- Active Phase: ${phase}
- Session Anchor: ${anchorPath}
      `.trim();
      
      output.context.unshift(mandates);
    }
  };
};
EOF
```

---

## Registration (in opencode.json)

> **⚠️ Remediated 2026-08-21 (D2/DEV-03)**: the two repo plugin entries are corrected
> singular→plural (`.opencode/plugins/`). The original spec propagated the dead paths.

```json
{
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugins/awareness.ts",
    "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
  ]
}
```

---

## How It Works

### Hook Payload (verified against core source — web Q-B4)

Core (`packages/opencode/src/session/compaction.ts`):

```ts
const compacting = yield* plugin.trigger(
  "experimental.session.compacting",
  { sessionID: input.sessionID },
  { context: [], prompt: undefined },
)
const nextPrompt = compacting.prompt ?? buildPrompt({ previousSummary, context: compacting.context })
```

- Input: `{ sessionID }`. Output: `{ context: string[]; prompt?: string }`.
- `context` strings are folded into the **compaction summary prompt**; if `prompt` is set it
  REPLACES the entire built prompt (anchor + template + context discarded).
- Fires once per compaction run (auto or manual `/compact`), before summary generation.
- Status: `experimental` prefix = explicitly unstable API.

### What Injection Actually Does (corrected mechanics — DEV-07)

The hook does NOT inject into the live conversation context. It shapes the **compaction
summary prompt** — i.e., it guarantees the post-compaction summary RETAINS the mandates,
entity, phase, and anchor path. The original claim ("survives prune/tail_turns") mischaracterized
this; the honest statement is: *content pushed via `output.context` is what the summarizer is
told to preserve.* `unshift()` keeps mandates at index 0 of the hook's context list for prompt
ordering; it is not a conversation-context operation.

### Environment Variables
| Variable | Source | Default |
|----------|--------|---------|
| `OMEGA_ENTITY` | Session startup / agent invocation | `"unknown"` |
| `OMEGA_PHASE` | Sprint/phase context | `"unknown"` |

Set in shell profile or session wrapper:
```bash
export OMEGA_ENTITY="kali"
export OMEGA_PHASE="PUBLIC-DEBUT-01"
```

---

## Defense-in-Depth Architecture (Carmack Q3.3)

| Layer | Mechanism | Timing | Survives Crash? |
|-------|-----------|--------|-----------------|
| **Primary** | Hydration Engine checkpoint | Background monitor at 80% usage | ✅ Independent process |
| **Secondary** | This plugin hook | During compaction | ❌ If compaction crashes |
| **Tertiary** | `SESSION_ANCHOR.md` | Session start/end | ✅ File-based |

**Carmack Verdict**: "Plugin hook = defense-in-depth (injects mandates/entity/anchor into compaction prompt), not primary. Checkpoint is primary; hook is secondary. Both needed."

---

## Verification

```bash
# Test 1: Plugin loads without error
opencode --log-level DEBUG 2>&1 | grep -i "sovereign-compaction"
# Expected: "Loading plugin: file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"

# Test 2: Hook fires during compaction (trigger manually)
opencode --log-level DEBUG run "Say hello" 2>&1 | grep -A5 "experimental.session.compacting"
# Expected: Hook invocation logged with injected mandates

# Test 3: Verify injection in context
opencode --log-level DEBUG run "What are the sovereign mandates?" 2>&1 | head -20
# Expected: Response includes M1, M7, M11, M15, M23 + entity + phase + anchor
```

---

## Rollback

```bash
# Remove plugin file
rm ~/.config/opencode/plugin/sovereign-compaction.ts

# Remove from opencode.json plugin array
# (edit opencode.json, remove the sovereign-compaction.ts line)
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20*