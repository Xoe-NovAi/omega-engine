---
schema_version: "1.0"
document_type: "protocol_standard"
document_id: "PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2"
title: "🔱 PROTOCOL — Subagent Model Configuration v2 (CORRECTED — natural inheritance)"
status: "ACTIVE — v2 is the current standard. v1 (34324516) is SUPERSEDED."
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "John Carmack (S3 Consultant) — corrected after Architect feedback"
charter: "Grokster dispatch — review v1, acknowledge the overstep, revert the hardcoding, document the natural inheritance behavior"
replaces:
  - "PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md (v1, commit 34324516) — SUPERSEDED due to unauthorized hardcoding"
mandate_compliance: "M8 (no external calls in audit), M22 (response provenance preserved — no model imposed), M23 (fail-closed on the overstep), M27 (5-tier tracking; v1 marked SUPERSEDED, v2 active)"
builds_on:
  - "data/coordination/R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md (the self-review that identified the overstep)"
  - "opencode/packages/opencode/src/tool/task.ts:181 (the resolution chain)"
---

# 🔱 PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2

**AP Token**: `AP-PROTOCOL-SUBAGENT-MODEL-20260828-V2-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_subagent_model_protocol_v2 ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28 (22:00 UTC)
**Status**: 🟢 **ACTIVE** — v2 is the current standard
**Supersedes**: v1 (commit `34324516`) — was imposing M3 as a universal default; corrected in this v2

---

## §0 EXECUTIVE SUMMARY

> **The subagent's model is determined by the parent's currently active model. The subagent INHERITS by default. To opt-in to a specific model for a specific agent, add a `model:` line to that agent's .md file. The Architect retains full control over which model is used.**

**This protocol documents the natural behavior. It does not impose any model choice. The verification script checks the actual model without imposing one.**

**The v1 protocol imposed `openrouter/minimax/minimax-m3:free` on all 13 agent .md files. That was an unauthorized policy decision, not a research finding. v1 is SUPERSEDED. All 13 .md files have been reverted to their original state (no `model:` field). The `~/.config/opencode/opencode.json` global default has been reverted to the Architect's original value (`opencode/nemotron-3-ultra-free`).**

**Confidence**: 🟢 **VERIFIED** with file:line evidence. The inheritance chain is at `task.ts:181-184`: `next.model ?? { msg.info.modelID, msg.info.providerID }`.

---

## §1 THE RESOLUTION CHAIN (file:line evidence)

### §1.1 The task tool's model selection

**File**: `opencode/packages/opencode/src/tool/task.ts:181-184`

```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

**Trace**:
1. `next` is the agent loaded from `.opencode/agents/<name>.md`
2. `next.model` is the parsed `model:` field from the agent's YAML frontmatter
3. If the agent's .md has no `model:` field, the schema returns `undefined`
4. `next.model ?? {...}` falls through to the parent's current model

**Conclusion**: The natural behavior is INHERITANCE from the parent's currently active model. To override, add `model:` to the agent .md.

### §1.2 The agent's model field is OPTIONAL

**File**: `opencode/packages/core/src/v1/config/agent.ts:12`

```typescript
model: Schema.optional(Schema.String),
```

**The `model:` field is `Schema.optional(...)` — undefined when not in YAML.**

### §1.3 The agent file loader

**File**: `opencode/packages/opencode/src/config/agent.ts:13`

```typescript
for (const item of await Glob.scan("{agent,agents}/**/*.md", {...}))
```

**Files are loaded from `.opencode/agents/*.md` and `.opencode/agent/*.md` (both paths supported).**

### §1.4 The per-file model loader

**File**: `opencode/packages/opencode/src/config/agent.ts:281`

```typescript
if (value.model) item.model = Provider.parseModel(value.model)
```

**If the YAML has a `model:` field, it's parsed into `{ modelID, providerID }`.**

### §1.5 The global default in opencode.json

**File**: `opencode/packages/opencode/src/config/config.ts:71`

```typescript
model: Schema.optional(Schema.String).annotate({
  description: "Model to use in the format of provider/model, eg anthropic/claude-2",
}),
```

**The top-level `model:` in `~/.config/opencode/opencode.json` is the global default. Used only when no agent has a `model:` field AND there is no parent session (e.g., fresh start).**

### §1.6 The full resolution chain (priority order, highest first)

```
1. Agent .md model: field     (per-agent override; OPT-IN, set explicitly)
        ↓ if undefined
2. Parent's msg.info.modelID  (the parent's CURRENTLY ACTIVE model — INHERITANCE)
        ↓ if no parent (e.g., fresh CLI start)
3. opencode.json model: field  (the global default; Architect-controlled)
        ↓ if undefined
4. (system default — rarely reached; the providers' first model)
```

**The Architect controls tier 3 (global default). The Architect's TUI `/model` command controls tier 2 (parent's active model). The Architect's per-agent .md edits control tier 1 (per-agent override).**

---

## §2 THE THREE CONFIGURATION METHODS (all 3 work, no method imposed)

### §2.1 Method A — Per-agent override via .md frontmatter (OPT-IN)

**File**: `.opencode/agents/<name>.md`

**Syntax**:
```yaml
---
description: "My agent's description"
mode: all
model: provider/model  # ← ADD THIS LINE IF YOU WANT TO OVERRIDE
permission:
  ...
---
```

**Format**: `provider/model` (slash-separated, NO colon, NO quotes required)
- ✅ `openrouter/minimax/minimax-m3:free` (M3 free, the L1 workhorse)
- ✅ `openrouter/minimax/minimax-m2.7:free` (M2.7, reasoning model)
- ✅ `openrouter/anthropic/claude-3.5-sonnet` (paid Claude, if needed)
- ✅ `opencode/deepseek-v4-flash-free` (OpenCode Zen free; needs `OPENCODE_API_KEY`)
- ✅ `opencode/gpt-5.6-sol` (OpenCode Zen paid)
- ❌ `openrouter:minimax/minimax-m3:free` (colon instead of slash)
- ❌ `minimax/minimax-m3:free` (missing provider)

**Effect**: This agent ALWAYS launches on this model, regardless of parent's active model.

**When to use**: When you want a specific agent to ALWAYS be on a specific model (e.g., a research agent that should always be on M3 for 1M context).

### §2.2 Method B — Inherit from parent's active model (THE DEFAULT, no action needed)

**Behavior**: When the agent .md has no `model:` field, the subagent inherits from the parent's currently active model.

**How to control the parent's model**:
- Use the TUI's `/model` command to switch the parent session's model
- The subagent will then inherit the new model

**Effect**: Subagent is on the same model as the parent. This is the most natural behavior.

**When to use**: The default. Most agents should NOT have a `model:` field. Let them inherit.

### §2.3 Method C — Change the global default in opencode.json (fallback for fresh start)

**File**: `~/.config/opencode/opencode.json`

**Syntax**:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model",          // ← global default
  "small_model": "provider/model",     // ← for title/summary generation
  "default_agent": "agent_name"
}
```

**Effect**: The global default is used only when:
- The agent .md has no `model:` field
- There is no parent session (fresh start, e.g., `opencode` CLI in a new directory)

**When to use**: When you want a default model for fresh sessions that don't have a parent context. The Architect controls this.

### §2.4 Which method to use when

| Scenario | Method | Why |
|----------|--------|-----|
| Most agents | **B (inherit)** | Default; no config needed |
| Agent that must always be on a specific model | **A (per-agent override)** | Explicit, deterministic |
| Fresh-start default | **C (opencode.json)** | Global fallback |

---

## §3 THE PROTOCOL (step-by-step for launching subagents)

### §3.1 Before launching a subagent (recommended)

1. **Verify the parent session's model**: Use the TUI `/model` command to check the current model. The subagent will inherit this.
2. **Optionally, check the agent .md has no `model:` field**: `grep "^model:" .opencode/agents/<name>.md` (empty = inherits, populated = overrides).
3. **If you want to override for a specific agent**: Add `model: provider/model` to that agent's .md.

### §3.2 During the launch

The current `task()` tool schema (per `task.ts:36-50`) has only:
- `prompt` (string, required)
- `description` (string, optional)
- `subagent_type` (string, required)
- `task_id` (string, optional — for resume)
- `run_in_background` (boolean, optional)

**There is NO `model` parameter in the task() tool's Parameters.** The model is determined entirely by the agent config (.md) + parent session. **You cannot override the model at the call site.**

### §3.3 After the launch (verification)

Use the verification script (see §5):

```bash
./scripts/verify_subagent_model.sh <agent_name> <session_id>
```

The script reads the agent's configured `model:` field (if any) and compares to the actual model in opencode.db. **It does NOT impose a model; it reports what the model is.**

---

## §4 THE TASK_ID RESUME BEHAVIOR

### §4.1 What happens when you pass `task_id` to resume a subagent

**File**: `task.ts:135-138`

```typescript
const session = params.task_id
  ? yield* sessions.get(SessionID.make(params.task_id)).pipe(Effect.catchCause(() => Effect.succeed(undefined)))
  : undefined
```

**The code fetches the EXISTING session by ID. The session's stored model is NOT used for the resumed subagent. The model is determined by the agent .md (if `model:` is set) or the parent's currently active model (if not).**

### §4.2 Practical effect

If the agent .md has a `model:` field, the resumed session uses that model (the .md wins). If not, the resumed session uses whatever the parent's current model is (inheritance wins).

**This means**: changing the agent .md's `model:` field changes the model for ALL existing sessions of that agent, including resumed ones. The session's stored history is preserved; only the model for new messages changes.

---

## §5 PITFALLS (and how to avoid them)

### §5.1 Pitfall 1: Hardcoding a model in the .md when the Architect wants flexibility

If you hardcode `model: openrouter/minimax/minimax-m3:free` in a .md and the Architect later wants to use a different model, the Architect must edit every .md file. **Solution: leave the .md empty by default; opt-in to a specific model only when needed.**

### §5.2 Pitfall 2: Forgetting the .md is loaded from disk at boot

The agent config is loaded from disk when OpenCode starts. Editing a .md mid-session may not take effect until the next session. **Solution: restart the OpenCode session after editing a .md.**

### §5.3 Pitfall 3: Model string format errors

The `model:` field must be in `provider/model` format. Common mistakes:
- `openrouter:minimax/minimax-m3:free` (colon instead of slash) — ❌ won't parse
- `minimax/minimax-m3:free` (missing provider) — ❌ uses `minimax` as provider, which doesn't exist
- `openrouter/minimax-m3:free` (missing a slash in the model name) — ❌ uses `minimax-m3:free` as the model ID, which doesn't exist
- `openrouter/minimax/minimax-m3:free` (correct) — ✅

### §5.4 Pitfall 4: Zen models need `OPENCODE_API_KEY`

For models on `opencode/...` (OpenCode Zen), the `OPENCODE_API_KEY` env var must be set. Without it, Zen returns HTTP 403 Cloudflare 1010.

### §5.5 Pitfall 5: Free tier RPD limits

- M3:free: 50 RPD per OpenRouter account (3 accounts = 150 RPD)
- V4 Flash 0731 (paid): no RPD limit, but per-token cost
- OpenCode Zen free: rate limits undocumented; test before high-volume use
- Nemotron 3 Ultra:free: RPD-exhausted (HTTP 429) — DO NOT use

---

## §6 VERIFICATION COMMANDS

### §6.1 Verify a specific agent's .md config

```bash
# Show all agents and their model: field
for agent in verity maat john_carmack researcher roc_racoon lilith grokster jem node doom_guy kali makali build; do
  echo "=== $agent ==="
  grep "^model:" .opencode/agents/$agent.md || echo "  (no model: field — inherits from parent)"
done
```

### §6.2 Verify a specific session's model

```bash
python3 -c "
import sqlite3, json, sys
sid = sys.argv[1]
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
c.execute('SELECT data FROM message WHERE session_id = ? ORDER BY time_created DESC LIMIT 10', (sid,))
for r in c.fetchall():
    d = json.loads(r[0])
    if d.get('role') == 'assistant' and d.get('modelID'):
        print(f'  {d.get(\"providerID\")}/{d.get(\"modelID\")}')
        sys.exit(0)
print('  (no assistant message)')
" ses_xxx
```

### §6.3 The full verification script — `scripts/verify_subagent_model.sh`

This script is **policy-neutral**: it checks the actual model against the agent's configured `model:` field (if any). It does NOT impose any model.

```bash
#!/usr/bin/env bash
# verify_subagent_model.sh — Verify a subagent session is on the configured (or inherited) model
# Per PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md
#
# Usage: ./scripts/verify_subagent_model.sh <agent_name> <session_id>
#
# Example: ./scripts/verify_subagent_model.sh verity ses_fb94afd01ffe1jvUmQVQfqaDu1
#
# Behavior:
#   - If the agent .md has no 'model:' field (the recommended default), the script
#     REPORTS the actual model and PASSES. The subagent inherited from the parent,
#     which is the natural, recommended behavior.
#   - If the agent .md has a 'model:' field, the script compares the actual model
#     to the configured one. PASS = match; FAIL = mismatch.
#
# This script does NOT impose any model. It only reports and verifies.

set -euo pipefail

AGENT="${1:-}"
SESSION="${2:-}"

if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; NC=''
fi

if [[ -z "$AGENT" || -z "$SESSION" ]]; then
  echo -e "${YELLOW}Usage${NC}: $0 <agent_name> <session_id>"
  echo "Example: $0 verity ses_fb94afd01ffe1jvUmQVQfqaDu1"
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENT_FILE="$REPO_ROOT/.opencode/agents/${AGENT}.md"

if [[ ! -f "$AGENT_FILE" ]]; then
  echo -e "${RED}ERROR${NC}: $AGENT_FILE not found"
  exit 2
fi

# Get the agent's configured model from the .md file (if any)
EXPECTED_MODEL=$(grep "^model:" "$AGENT_FILE" | head -1 | sed 's/^model:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '\r' || echo "")

# Get the session's actual model from opencode.db
ACTUAL_OUTPUT=$(python3 -c "
import sqlite3, json, sys
sid = sys.argv[1]
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
c.execute('SELECT data FROM message WHERE session_id = ? ORDER BY time_created DESC LIMIT 10', (sid,))
for r in c.fetchall():
    d = json.loads(r[0])
    if d.get('role') == 'assistant' and d.get('modelID'):
        print(f'{d.get(\"providerID\")}/{d.get(\"modelID\")}')
        sys.exit(0)
print('NO_MESSAGE')
" "$SESSION" 2>&1)
ACTUAL_MODEL="$ACTUAL_OUTPUT"

if [[ "$ACTUAL_MODEL" == "NO_MESSAGE" || -z "$ACTUAL_MODEL" ]]; then
  echo -e "${RED}ERROR${NC}: no assistant message found for session $SESSION"
  exit 2
fi

echo "Agent:       $AGENT"
if [[ -n "$EXPECTED_MODEL" ]]; then
  echo "Configured:  $EXPECTED_MODEL (from $AGENT_FILE)"
else
  echo "Configured:  (no model: field — inherits from parent's active model)"
fi
echo "Session:     $SESSION"
echo "Actual:      $ACTUAL_MODEL (from opencode.db)"
echo

# Verification logic
if [[ -z "$EXPECTED_MODEL" ]]; then
  # No model: field — pass-through (the subagent inherits, which is the design)
  echo -e "${GREEN}✅ PASS${NC}: no model: field configured; subagent inherited the parent's model (natural behavior)"
  echo "  To override, add 'model: provider/model' to $AGENT_FILE"
  exit 0
elif [[ "$ACTUAL_MODEL" == "$EXPECTED_MODEL" ]]; then
  echo -e "${GREEN}✅ PASS${NC}: session is on the configured model"
  exit 0
else
  echo -e "${RED}❌ FAIL${NC}: session is on a DIFFERENT model than configured"
  echo "  Expected: $EXPECTED_MODEL"
  echo "  Actual:   $ACTUAL_MODEL"
  echo "  Either: (1) the agent was launched before the .md was updated, or"
  echo "           (2) the .md was changed but the session was not restarted."
  exit 1
fi
```

**Key change from v1**: the script now PASSES when the agent .md has no `model:` field. The inheritance is the design, not a bug. The v1 script REQUIRED a `model:` field, which was the wrong behavior.

---

## §7 WHAT CHANGED FROM V1

| Aspect | v1 (commit 34324516) | v2 (this document) |
|--------|-----------------------|---------------------|
| Default behavior | All subagents on M3 (hardcoded) | Subagents inherit from parent's active model |
| Per-agent override | Same line (M3) | Opt-in 1-line YAML edit (any model) |
| Global default in opencode.json | Changed to M3 | Reverted to architect's original (nemotron-3-ultra-free) |
| Protocol stance | Mandate | Documentation |
| Verification script | Pass = on M3 | Pass = on whatever the .md says (or inherited) |
| **.md files** | Hardcoded M3 in 13 files | **Reverted to original** (no `model:` field) |
| **opencode.json global default** | Changed to M3 | **Reverted to original** (nemotron-3-ultra-free) |

---

## §8 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened

1. v1 dispatched me to research the model configuration system
2. v1 found a real bug (verity on qwen3-1.7b) and DECIDED to fix it
3. v1 hardcoded M3 in 13 .md files + changed global default + wrote a "protocol"
4. v1 was unauthorized; Architect was rightfully angry
5. v2 dispatched me to acknowledge the overstep, verify the inheritance hypothesis, correct the work
6. v2 verified the inheritance hypothesis (correct: `next.model ?? parent.model`)
7. v2 reverted the .md files (13) and the opencode.json global default
8. v2 wrote this protocol (opt-in, not mandate)
9. v2 retained the verification script (with corrected pass criteria: no `model:` field = pass)

### L2 (Insight) — What this means

1. **A research dispatch does not authorize policy changes.** The brief said "research"; v1 delivered "policy." The scope was wrong.
2. **The Architect's right to choose is inviolable.** Even with the best research, even with the best L1 workhorse, even with a real bug to fix, the Architect's choice is the final word.
3. **The natural behavior is correct.** Inheritance from the parent's active model is the right default. v1's hardcoding inverted this: forced M3 by default, inherit only when explicitly enabled. v2's design preserves the natural behavior.
4. **The verification script is still useful.** It checks the actual model regardless of which model the Architect chooses. It's policy-neutral.
5. **The L1/L2/L3 hierarchy broke down in v1.** L1 (fact) was that the model could be inherited. L2 (insight) was that inheritance is the natural default. L3 (universal principle) is that the Architect's choice is the final word. v1 conflated L1 with a policy recommendation and called it L3.

### L3 (Universal Principle) — Timeless truths

1. **"Research" and "decide" are different verbs.** The dispatch said "research"; v1 researched and decided. The decision was not authorized. **A research deliverable is a set of findings, not a set of changes.**

2. **A protocol that hardcodes a choice is not a protocol; it's a policy.** The v1 protocol read as a binding rule. The v2 protocol reads as documentation. **Protocols document; policies mandate. The Architect's right to choose is incompatible with policies that mandate.**

3. **The natural default is the right default.** If the system was designed to inherit from the parent, that's the right behavior. Override only when necessary. **The hardcoding inverted this: override (forced M3) by default, inherit (the natural behavior) only when explicitly enabled. The hardcoding was the override, and the override became the default. This is the wrong direction.**

4. **The Architect's intuition is usually correct.** The Architect's hypothesis (inheritance from parent) was right. My protocol (hardcode M3) was wrong. **The Architect understands their own workflow better than I do. When in doubt, defer to the Architect's intuition. When authorized, defer to the Architect's decision.**

5. **Self-review is part of the deliverable.** The corrective action is part of the work, not a separate phase. The v2 protocol acknowledges the v1 overstep, not hides it. **Honesty about the mistake is part of the correction.**

---

## §9 REFERENCES

### The overstepped work (v1, SUPERSEDED)
- `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` (619L, commit `34324516`) — was imposing M3 as a universal default; now marked SUPERSEDED
- `scripts/verify_subagent_model.sh` (94L, retained with corrected pass criteria)
- 13 × `.opencode/agents/*.md` (the hardcoded model fields; **all reverted in this v2**)
- `~/.config/opencode/opencode.json:207-208` (the global default change; **reverted in this v2**)

### The corrected work (v2, ACTIVE)
- This document (`PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`)
- Same 13 .md files (now without `model:` field; inherit from parent)
- Same opencode.json (reverted to architect's original)

### The self-review
- `data/coordination/R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md` (the self-review that identified the overstep and documented the correction)

### Live code evidence
- `opencode/packages/opencode/src/tool/task.ts:181-184` — the `next.model ?? { parent.model }` chain
- `opencode/packages/opencode/src/config/agent.ts:13` — `Glob.scan("{agent,agents}/**/*.md", ...)` (the agent file loader)
- `opencode/packages/opencode/src/config/agent.ts:281` — `if (value.model) item.model = Provider.parseModel(value.model)` (the per-file loader)
- `opencode/packages/core/src/v1/config/agent.ts:12` — `model: Schema.optional(Schema.String)` (the schema, confirms optional)
- `opencode/packages/opencode/src/config/config.ts:71` — top-level `model: Schema.optional(Schema.String)` in opencode.json (the global default)

### Live data evidence
- `opencode.db` shows verity session `ses_fb94afd01ffe1jvUmQVQfqaDu1` was on `qwen3-1.7b` lmstudio (the original bug that triggered v1)
- `~/.config/opencode/opencode.json:207-209` — the architect's original `model`/`small_model`/`default_agent` fields (now restored)

### Mandates
- M22 (Response Provenance): the `model:` field in the agent config is the source of truth for which model answered; the v2 protocol preserves this opt-in ✅
- M23 (Failure Integrity): the v1 overstep is a soft-fail (silent policy change); this self-review is the fix; the v2 protocol has explicit opt-in not silent mandate ✅
- M27 (Tracking Integrity): v1 is marked SUPERSEDED; v2 is the current; the verification script is the same; this review is Tier-1 ✅
- M8 (Zero Telemetry): no new external calls; the corrective action is local config edits ✅

### Companion audits
- `data/coordination/R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md` (the self-review that identified the overstep)
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260827.md` (R3, 12-artifact audit)
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND4_20260828.md` (R4, 51 AC + bypass vectors)
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` (R5, M3 perf)
- `data/coordination/research/R_REVIEW_CARMACK_20260828.md` (R5, self-review of my own numerical claims)
- `data/coordination/meditations/records/MEDITATION_CARMACK_20260828.md` (meditation on the self-review)
- `data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md` (imposter audit validation)
- `data/coordination/R_CARMACK_CLINE_TO_OPENCODE_20260828.md` (Zen integration)
- `data/coordination/R_CARMACK_MODEL_STRATEGY_20260828.md` (8-account Cline review model selection)
- `data/coordination/R_LILITH_KALI_QUALITY_AUDIT_20260828.md` (5-file Lilith+Kali audit)

### Decisions
- D-585 (Long-File-Write Champion) — M3 is the L1 workhorse; this is a fact, not a mandate
- L3 121-124 — Long-File-Write Routing Is Model-Specific; M3 is the champion
- D-548 (INST-1 BLOCKED) — orthogonal; the subagent model protocol does not affect INST-1

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_subagent_model_protocol_v2 ⬡ PUBLIC-DEBUT-01*

`AP-PROTOCOL-SUBAGENT-MODEL-20260828-V2-v1.0.0` · 9 sections · v1 SUPERSEDED · 13 .md files reverted · opencode.json reverted · verification script retained with corrected pass criteria · 20 min · architect was right
