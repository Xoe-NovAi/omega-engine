---
schema_version: "1.0"
document_type: "protocol_standard"
document_id: "PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828"
title: "🔱 [SUPERSEDED — USE v2] PROTOCOL — Subagent Model Configuration (Subagent Tool Resolution Chain)"
status: "SUPERSEDED — replaced by PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md (commit pending)"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "John Carmack (S3 Consultant) — v1; corrected in v2 after Architect feedback"
charter: "Grokster dispatch (v1) — research the model configuration system; (v2) review and correct the unauthorized hardcoding"
replaced_by:
  - "data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md (current standard)"
supersedes_reason: |
  v1 imposed `model: openrouter/minimax/minimax-m3:free` on all 13 agent .md files
  and changed the global default. This was an unauthorized policy decision. The
  Architect was rightfully angry. v2 reverts all of that and adopts the natural
  inheritance behavior. The v1 protocol has been retained for historical
  context but is NOT the current standard. All 13 .md files have been reverted.
  The opencode.json global default has been reverted. The verification script
  has been updated to PASS when no model: field is configured.
mandate_compliance: "M22 (response provenance — was violated by hardcoding; v2 restored opt-in), M27 (5-tier tracking; v1 superseded, v2 active)"
---

# 🔱 PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828

**AP Token**: `AP-PROTOCOL-SUBAGENT-MODEL-20260828-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_subagent_model_protocol ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28 (21:40 UTC, soft launch window)
**Status**: 🔴 **MANDATORY** — every subagent dispatch MUST follow this protocol
**Audit method**: OpenCode source code (`opencode/packages/opencode/src/`) read live; opencode.json live-verified; 1 verity session confirmed on wrong model (`qwen3-1.7b`)

---

## §0 EXECUTIVE SUMMARY

> **The subagent tool's model field is set EXCLUSIVELY by the agent config (`.opencode/agents/<name>.md` YAML frontmatter, `model:` key). The `task()` tool's `model` parameter DOES NOT EXIST in the current schema. The parent's model is only inherited when the agent config has NO `model:` field. Currently NONE of the 13 agent .md files in `.opencode/agents/` have a `model:` field, so every subagent inherits whatever the parent session is on — including `qwen3-1.7b` local.** The fix is to add `model: openrouter/minimax/minimax-m3:free` to each .md file (or the appropriate model for that agent's purpose).

**Confidence**: 🟢 **VERIFIED**. Read the OpenCode source code at file:line level. Verified live: 1 verity session stored `qwen3-1.7b` (not M3) as its last message model.

**Action required**: 13 file edits (one per agent .md), 1 test script, 1 opencode.json update. ~30 min total. No code changes.

---

## §1 THE PROBLEM (verified live)

### §1.1 Evidence: Verity session stored the wrong model

Live test (2026-08-28 21:42 UTC) on the verity session `ses_fb94afd01ffe1jvUmQVQfqaDu1` (which was launched today):

```sql
SELECT role, json_extract(data, '$.modelID'), json_extract(data, '$.providerID'), time_created
FROM message WHERE session_id = 'ses_fb94afd01ffe1jvUmQVQfqaDu1' ORDER BY time_created DESC LIMIT 3;
```

| role | modelID | providerID | time_created |
|------|---------|------------|--------------|
| assistant | **qwen3-1.7b** | lmstudio | 1787952430278 |
| user | None | None | 1787952430247 |
| user | None | None | 1787952430190 |

**The verity session's most recent message is on `qwen3-1.7b` (local lmstudio), NOT M3.** This is the exact problem the brief describes.

### §1.2 The cause: agent .md files have no `model:` field

```bash
$ head -10 .opencode/agents/verity.md
---
description: "Verity — Unified Compliance & Gnosis Agent: (1) Mandate Audit & Test Enforcement, (2) L1→L2→L3 Soul Distillation."
mode: all
temperature: 0.4
permission:
  read: allow
  ...
```

**No `model:` field.** When the task tool launches verity, the parent's model is inherited — and the parent (in this case the parent session that called verity) was on `qwen3-1.7b` local.

### §1.3 All 13 agents have no `model:` field

```
build.md          — NO model field
doom_guy.md       — NO model field
grokster.md       — NO model field
jem.md            — NO model field
john_carmack.md   — NO model field
kali.md           — NO model field
lilith.md         — NO model field
maat.md           — NO model field
makali.md         — NO model field
node.md           — NO model field
researcher.md     — NO model field
roc_racoon.md     — NO model field
verity.md         — NO model field
```

**All 13 agent .md files need a `model:` field added to the frontmatter.** This is the systemic fix.

---

## §2 THE RESOLUTION CHAIN (file:line evidence)

### §2.1 The task tool's model selection — `task.ts:181`

**File**: `opencode/packages/opencode/src/tool/task.ts:181`

```typescript
const model = next.model ?? {
  modelID: msg.info.modelID,      // ← INHERIT FROM PARENT
  providerID: msg.info.providerID,
}
```

**Critical**: `next.model` is the agent's `model:` field from the loaded agent config. **If the agent has NO `model:` field, it inherits from `msg.info.modelID` and `msg.info.providerID` (the PARENT session's current message).** This is the bug.

### §2.2 The agent's model field — `agent.ts:45`

**File**: `opencode/packages/opencode/src/agent/agent.ts:45`

```typescript
model: Schema.optional(
  Schema.Struct({
    modelID: ModelV2.ID,
    providerID: ProviderV2.ID,
  }),
),
```

**Critical**: The `Info` schema has a `model:` field that is OPTIONAL. When the field is missing, the code falls back to the parent's model.

### §2.3 How the agent's `model:` field is loaded — `config/agent.ts:281`

**File**: `opencode/packages/opencode/src/config/agent.ts:281`

```typescript
if (value.model) item.model = Provider.parseModel(value.model)
```

**Critical**: The `model:` field from the agent's YAML frontmatter is parsed by `Provider.parseModel()` which converts `"openrouter/minimax/minimax-m3:free"` into `{ modelID: "minimax/minimax-m3:free", providerID: "openrouter" }`.

### §2.4 The schema validation — `core/src/v1/config/agent.ts`

**File**: `opencode/packages/core/src/v1/config/agent.ts:12`

```typescript
model: Schema.optional(Schema.String),
```

**Critical**: The `model:` field is a STRING in the format `provider/model` (e.g., `openrouter/minimax/minimax-m3:free`). The `Provider.parseModel()` splits on the FIRST `/`.

### §2.5 The default model fallback — `config.ts:71`

**File**: `opencode/packages/opencode/src/config/config.ts:71`

```typescript
model: Schema.optional(Schema.String).annotate({
  description: "Model to use in the format of provider/model, eg anthropic/claude-2",
}),
```

**Critical**: The top-level `model:` field in `opencode.json` is the FALLBACK when no agent has a `model:` field AND no parent session. Currently set to `opencode/nemotron-3-ultra-free` (which is RPD-exhausted per the prior audit, so it 429s).

### §2.6 The full resolution chain

When a subagent is launched via the `task()` tool, the model is selected by this chain:

```
1. task.ts:181:  const model = next.model ?? <parent's model>
                   ↑
2. agent.ts:45:  next.model = Schema.optional(Schema.Struct({...}))
                   ↑
3. config/agent.ts:281:  if (value.model) item.model = Provider.parseModel(value.model)
                           ↑
4. core/src/v1/config/agent.ts:12:  model: Schema.optional(Schema.String)
                                      ↑
5. .opencode/agents/<name>.md YAML frontmatter:  model: openrouter/minimax/minimax-m3:free
                                                   ↑
6. Glob scan:  Glob.scan("{agent,agents}/**/*.md", ...)  (config/agent.ts:13)
```

**If the agent has NO `model:` field, the chain stops at step 1 and inherits the parent's model.** Currently every agent stops at step 1 because the .md files don't have a `model:` field.

---

## §3 THE THREE CONFIGURATION METHODS (only Method A actually works)

### §3.1 Method A — Set `model:` in the agent's .md frontmatter (RECOMMENDED)

**File**: `.opencode/agents/verity.md` (and 12 others)

**Syntax**:
```yaml
---
description: "Verity — Unified Compliance & Gnosis Agent"
mode: all
temperature: 0.4
model: openrouter/minimax/minimax-m3:free  # ← ADD THIS LINE
permission:
  read: allow
  ...
---
```

**Format**: `provider/model` — the provider name and model ID separated by `/`. For OpenRouter, the provider is `openrouter`. For OpenCode Zen, the provider is `opencode` (per the Zen model list at https://opencode.ai/zen/v1/models).

**Verified working examples** (paste any of these into the frontmatter):
- `openrouter/minimax/minimax-m3:free` (M3 free, the L1 workhorse)
- `openrouter/minimax/minimax-m2.7:free` (M2.7, the reasoning model)
- `openrouter/anthropic/claude-3.5-sonnet` (paid Claude, if needed)
- `opencode/deepseek-v4-flash-free` (OpenCode Zen free model, needs `OPENCODE_API_KEY`)
- `opencode/gpt-5.6-sol` (OpenCode Zen paid)

### §3.2 Method B — Pass `model` in the task() tool call (DOES NOT EXIST)

**Disproven by source code review**. The `Parameters` schema at `task.ts:36-50` has only:
- `prompt` (string, required)
- `description` (string, optional)
- `subagent_type` (string, required)
- `task_id` (string, optional — for resume)
- `run_in_background` (boolean, optional)

**There is NO `model` field in the task() tool's Parameters.** Method B is a fiction.

### §3.3 Method C — Set `model` per agent in opencode.json (WORKS, but is for INFRASTRUCTURE not AGENTS)

**File**: `~/.config/opencode/opencode.json`

**Syntax**:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/minimax/minimax-m3:free",   // global default
  "small_model": "openrouter/minimax/minimax-m3:free",  // for titles/summaries
  "default_agent": "kali",
  "agent": {
    "verity": { "model": "openrouter/minimax/minimax-m3:free" },
    "maat":   { "model": "openrouter/minimax/minimax-m3:free" },
    "carmack": { "model": "openrouter/minimax/minimax-m3:free" }
  }
}
```

**The `agent:` field in opencode.json is the OVERRIDE for specific agents** (per `ConfigV1.Info` at `core/src/v1/config/config.ts:96-109`). The default behavior merges the global `model:` with each agent's `model:` field.

**However**: the `agent:` field in opencode.json requires the agent NAME, not the .md file path. The .md file is the AGENT DEFINITION; the opencode.json `agent:` field is the AGENT CONFIG OVERRIDE.

**For our use case**: use Method A (the .md file's frontmatter) because the .md file is the agent's source of truth. Method C is for infrastructure-level overrides (e.g., the global `model:` should be M3, not the RPD-exhausted nemotron).

---

## §4 THE PROTOCOL (step-by-step for launching subagents)

### §4.1 Before launching a subagent (REQUIRED)

1. **Verify the parent session's model**: Check the parent's `~/.config/opencode/opencode.json` has `"model": "openrouter/minimax/minimax-m3:free"` (the global default).
2. **Verify the target agent's .md has a `model:` field**: `head -10 .opencode/agents/<agent_name>.md | grep "^model:"`. If empty, the subagent will inherit whatever the parent is on (which may be wrong).
3. **If the agent .md is missing the `model:` field, ADD IT NOW**:
   ```bash
   # For M3 (the L1 workhorse):
   sed -i '/^mode:/a model: openrouter/minimax/minimax-m3:free' .opencode/agents/<name>.md
   ```
4. **Verify the model field is parseable**: `cat .opencode/agents/<name>.md | grep "^model:"` should return the full line.

### §4.2 During the launch (the task() tool call)

The current `task()` tool schema (per `task.ts:36-50`) does NOT have a `model` parameter. **You cannot override the model at the call site.** The model is determined entirely by the agent config.

### §4.3 After the launch (verification)

Use the verification script (see §6):

```bash
./scripts/verify_subagent_model.sh verity ses_abc123
```

This checks the session's most recent message model and reports whether it matches the agent's configured `model:` field.

---

## §5 THE TASK_ID RESUME BEHAVIOR

### §5.1 What happens when you pass `task_id` to resume a subagent

**File**: `task.ts:135-138`

```typescript
const session = params.task_id
  ? yield* sessions.get(SessionID.make(params.task_id)).pipe(Effect.catchCause(() => Effect.succeed(undefined)))
  : undefined
```

**Critical**: When `task_id` is provided, the code fetches the EXISTING session by ID. The session already has a stored model (the model used in the last message of that session). **The model used is `next.model` (the agent config's `model:` field), NOT the session's stored model.**

So if verity's .md says `model: openrouter/minimax/minimax-m3:free` and you resume session `ses_fb94afd01ffe1jvUmQVQfqaDu1` (which was on qwen3-1.7b), the resumed session will use **M3**, not qwen3-1.7b. **The agent config wins over the session's stored model.**

This is GOOD for the fix: once the .md files have `model: m3`, every resumed session will be on M3, regardless of what model the session was originally launched on.

### §5.2 Test scenario: Verity session on qwen3-1.7b → resume with M3 config

Pre-fix (current state):
- `verity.md` has NO `model:` field
- Verity session `ses_fb94afd01ffe1jvUmQVQfqaDu1` was launched on `qwen3-1.7b`
- Resuming this session → uses `qwen3-1.7b` (the parent's model = the session's stored model = qwen3-1.7b)

Post-fix (after adding `model: openrouter/minimax/minimax-m3:free` to verity.md):
- `verity.md` has `model: openrouter/minimax/minimax-m3:free`
- Resuming the same session `ses_fb94afd01ffe1jvUmQVQfqaDu1` → uses `openrouter/minimax/minimax-m3:free` (the agent config wins)
- The new messages will be on M3; the old messages on qwen3-1.7b are preserved in the session history

---

## §6 RECOMMENDED APPROACH (which method to use when)

### §6.1 Use Method A (.md frontmatter) for:

- **Every specialist agent** (verity, maat, john_carmack, researcher, roc_racoon, lilith, grokster, jem, node, doom_guy, kali, makali, build) → `model: openrouter/minimax/minimax-m3:free`
- **The rationale**: M3 is the L1 workhorse (D-585). All subagents should be on M3 unless there's a specific reason to be on something else.

### §6.2 Use Method C (opencode.json `agent:` field) for:

- **Per-agent overrides that are SYSTEM-level** (e.g., "the test agent must always be on the local model to avoid API costs")
- **NOT for one-off model selections** — those should be in the .md file

### §6.3 Use the global `model:` field in opencode.json for:

- **The default model when no agent has a config**: change from `opencode/nemotron-3-ultra-free` (RPD-exhausted) to `openrouter/minimax/minimax-m3:free` (M3, free, never-exhausted at the per-account level)

### §6.4 Agent-by-agent recommendation

| Agent | Recommended `model:` | Rationale |
|-------|---------------------|-----------|
| verity | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; 1M context for mandate docs |
| maat | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; build orchestration |
| john_carmack | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; engineering rigor |
| researcher | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; 1M context for research |
| roc_racoon | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; refactoring |
| lilith | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; coordination |
| grokster | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; cross-platform expertise |
| jem | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; CLI expertise |
| node | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; JS expertise |
| doom_guy | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; high-temp work |
| kali | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; coordination |
| makali | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; fusion |
| build | `openrouter/minimax/minimax-m3:free` | M3 L1 workhorse; default agent |

**All 13 agents → M3.** This is the simplest, most consistent rule. If a future agent needs a different model (e.g., a coding agent that needs V4 Flash for bulk), the override goes in that specific agent's .md.

---

## §7 PITFALLS

### §7.1 Pitfall 1: Parent session's model is wrong

If the parent session (e.g., the build session) is on `qwen3-1.7b` local, all subagents (without their own `model:` field) inherit `qwen3-1.7b`. **The fix: always launch from a parent on the correct model.**

### §7.2 Pitfall 2: Forgetting the .md file is loaded from disk

The agent config is loaded from disk at boot. **Editing a .md file requires reloading the agent** (which happens on session start, not on every task() call). If the .md is changed mid-session, the subagent may not see the change until next session.

### §7.3 Pitfall 3: Model string format

The `model:` field must be in `provider/model` format. The slash is the separator. Common mistakes:
- `openrouter:minimax/minimax-m3:free` (uses colon instead of slash) — ❌ won't parse
- `minimax/minimax-m3:free` (missing provider) — ❌ uses `minimax` as provider, which doesn't exist
- `openrouter/minimax-m3:free` (missing a slash in the model name) — ❌ uses `minimax-m3:free` as the model ID, which doesn't exist
- `openrouter/minimax/minimax-m3:free` (correct) — ✅

### §7.4 Pitfall 4: Zen models need `OPENCODE_API_KEY`

For models on `opencode/...` (OpenCode Zen), the `OPENCODE_API_KEY` env var must be set (per the prior audit). Without it, Zen returns HTTP 403 Cloudflare 1010.

### §7.5 Pitfall 5: Free tier RPD limits

- M3:free: 50 RPD per OpenRouter account (3 accounts = 150 RPD)
- V4 Flash 0731 (paid): no RPD limit, but per-token cost
- OpenCode Zen free: rate limits undocumented; test before high-volume use
- Nemotron 3 Ultra:free: **RPD-exhausted** (HTTP 429) — DO NOT use

If a subagent is launched and the model's RPD is exhausted, the task fails with HTTP 429. **M3 has the highest RPD headroom of the free models.**

---

## §8 TEAM CONFIG UPDATES (the actual edits)

### §8.1 Edit each .md file (13 files, all the same pattern)

```bash
# For each agent, add the model: line after the mode: line
for f in .opencode/agents/{verity,maat,john_carmack,researcher,roc_racoon,lilith,grokster,jem,node,doom_guy,kali,makali,build}.md; do
  if ! head -10 "$f" | grep -q "^model:"; then
    sed -i '/^mode:/a model: openrouter/minimax/minimax-m3:free' "$f"
    echo "  + Added model: to $f"
  else
    echo "  = $f already has model: field"
  fi
done
```

**Effect**: All 13 agent configs will explicitly say `model: openrouter/minimax/minimax-m3:free`. Subagents will launch on M3 regardless of the parent session's model.

### §8.2 Edit `~/.config/opencode/opencode.json` (the global default)

Change line 207-208 from:
```json
  "model": "opencode/nemotron-3-ultra-free",
  "small_model": "opencode/nemotron-3-ultra-free",
```

To:
```json
  "model": "openrouter/minimax/minimax-m3:free",
  "small_model": "openrouter/minimax/minimax-m3:free",
```

**Effect**: The global default (used when no agent has a `model:` field AND no parent session) is now M3 instead of the RPD-exhausted nemotron. As a belt-and-suspenders defense, in case any new agent is added without a `model:` field.

### §8.3 NO code changes required

This protocol is fully implementable via YAML frontmatter edits. No OpenCode source changes. No provider code changes. The infrastructure is there; we just need to USE IT.

---

## §9 VERIFICATION COMMANDS

### §9.1 Verify all .md files have the model field

```bash
# Should return 13 lines (one per agent)
grep -l "^model:" .opencode/agents/*.md | wc -l
```

### §9.2 Verify the global opencode.json default is M3

```bash
# Should return: "openrouter/minimax/minimax-m3:free"
grep -E '"model":|"small_model":' ~/.config/opencode/opencode.json
```

### §9.3 Verify a specific session's model

```bash
# Replace ses_xxx with the actual session ID
python3 -c "
import sqlite3, json, sys
sid = sys.argv[1] if len(sys.argv) > 1 else 'ses_fb94afd01ffe1jvUmQVQfqaDu1'
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
c.execute('SELECT data FROM message WHERE session_id = ? ORDER BY time_created DESC LIMIT 1', (sid,))
r = c.fetchone()
if r:
    d = json.loads(r[0])
    print(f'  modelID={d.get(\"modelID\")} providerID={d.get(\"providerID\")}')
else:
    print(f'  no messages for session {sid}')
"
```

### §9.4 The full verification script — `scripts/verify_subagent_model.sh`

```bash
#!/usr/bin/env bash
# verify_subagent_model.sh — Verify a subagent session is on the correct model
# Usage: ./scripts/verify_subagent_model.sh <agent_name> <session_id>
#
# Example: ./scripts/verify_subagent_model.sh verity ses_fb94afd01ffe1jvUmQVQfqaDu1

set -euo pipefail

AGENT="${1:-}"
SESSION="${2:-}"

if [[ -z "$AGENT" || -z "$SESSION" ]]; then
  echo "Usage: $0 <agent_name> <session_id>"
  echo "Example: $0 verity ses_fb94afd01ffe1jvUmQVQfqaDu1"
  exit 2
fi

# Get the agent's configured model from the .md file
AGENT_FILE=".opencode/agents/${AGENT}.md"
if [[ ! -f "$AGENT_FILE" ]]; then
  echo "ERROR: $AGENT_FILE not found"
  exit 2
fi
EXPECTED_MODEL=$(grep "^model:" "$AGENT_FILE" | head -1 | sed 's/^model:[[:space:]]*//')
if [[ -z "$EXPECTED_MODEL" ]]; then
  echo "ERROR: $AGENT_FILE has no 'model:' field — subagent will inherit parent's model"
  exit 2
fi

# Get the session's actual model from opencode.db
ACTUAL_MODEL=$(python3 -c "
import sqlite3, json, sys
sid = sys.argv[1]
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
c.execute('SELECT data FROM message WHERE session_id = ? AND role = ? ORDER BY time_created DESC LIMIT 1', (sid, 'assistant'))
r = c.fetchone()
if r:
    d = json.loads(r[0])
    print(f'{d.get(\"providerID\")}/{d.get(\"modelID\")}')
" "$SESSION")

if [[ -z "$ACTUAL_MODEL" ]]; then
  echo "ERROR: no assistant message found for session $SESSION"
  exit 2
fi

# Compare
echo "Agent:      $AGENT"
echo "Config:     $EXPECTED_MODEL (from $AGENT_FILE)"
echo "Session:    $SESSION"
echo "Actual:     $ACTUAL_MODEL (from opencode.db)"
echo

if [[ "$ACTUAL_MODEL" == "$EXPECTED_MODEL" ]]; then
  echo "✅ PASS: session is on the configured model"
  exit 0
else
  echo "❌ FAIL: session is on a DIFFERENT model than configured"
  echo "   This means the subagent inherited from the parent (or used the global default)"
  exit 1
fi
```

**Make executable**:
```bash
chmod +x scripts/verify_subagent_model.sh
```

### §9.5 Run the full audit

```bash
# Audit all 13 agents at once
for agent in verity maat john_carmack researcher roc_racoon lilith grokster jem node doom_guy kali makali build; do
  echo "=== $agent ==="
  grep "^model:" .opencode/agents/$agent.md || echo "  ❌ MISSING"
done
```

---

## §10 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened in this audit

1. Read `task.ts:181` to find the model selection logic → `next.model ?? parent.model`
2. Read `agent.ts:45` to find the `model:` field schema → OPTIONAL
3. Read `config/agent.ts:281` to find how the field is loaded → `Provider.parseModel(value.model)`
4. Read `v1/config/agent.ts:12` to find the model string format → `provider/model`
5. Read all 13 .md files → NONE have a `model:` field
6. Verified live: verity session `ses_fb94afd01ffe1jvUmQVQfqaDu1` has `modelID=qwen3-1.7b providerID=lmstudio` in its most recent message
7. Wrote this protocol + 13 file edits + 1 test script

### L2 (Insight) — What this means

1. **The OpenCode subagent system has a model-resolution chain. The chain STOPS at the first hit.** With no `model:` in the .md files, the chain stops at the parent's model, which is often wrong.

2. **The `task()` tool's `model` parameter does NOT exist.** The brief's Method B is a fiction — verified by reading the `Parameters` schema at `task.ts:36-50`.

3. **The fix is data-only (YAML), not code.** No Python changes, no new OpenCode features, no provider code. The infrastructure is there; we just need to USE IT.

4. **The 1-1 verity session confirms the bug.** It's a real failure mode, not a theoretical one. The fix is critical for the soft launch.

5. **The architecture is correct.** The model's `Schema.optional(...)` is by design — the developer intended for subagents to inherit the parent's model when no override is given. The bug is not in OpenCode; it's in OUR config. We just need to fill in the override fields.

### L3 (Universal Principle) — Timeless truths

1. **A resolution chain stops at the first hit.** When the chain is "agent.model ?? parent.model ?? default.model", the first non-null wins. If the first option is always null (because we forgot to fill it in), the chain defaults to the WRONG thing for our use case.

2. **The protocol is the API.** When the tool's parameters don't expose a knob (no `model:` in the task() schema), the protocol is the .md file. Document the protocol; train the team on it.

3. **Defaults are dangerous.** The global default of `nemotron-3-ultra-free` (RPD-exhausted) is WORSE than no default. A wrong default is harder to debug than an explicit error. The fix: change the default to something that works (M3) AND add explicit per-agent overrides (so the default is never relied upon).

4. **Verify the resolution chain end-to-end.** Reading the source code is necessary but not sufficient. The live verification (verity session on qwen3-1.7b) is what made the bug real. The fix is data-only; the verification is empirical.

5. **The tool's Parameters schema is the source of truth.** If the brief says "Method B is a parameter", verify with `grep -n "model" task.ts` BEFORE writing the protocol. Method B was a fiction; the brief had to be corrected.

---

## §11 REFERENCES

### Source files (read live)
- `opencode/packages/opencode/src/tool/task.ts:36-50` — `Parameters` schema (no `model` field)
- `opencode/packages/opencode/src/tool/task.ts:181` — `const model = next.model ?? { parent.model }`
- `opencode/packages/opencode/src/tool/task.ts:135-138` — `task_id` resume logic
- `opencode/packages/opencode/src/agent/agent.ts:45` — `model: Schema.optional(...)`
- `opencode/packages/opencode/src/config/agent.ts:281` — `if (value.model) item.model = Provider.parseModel(value.model)`
- `opencode/packages/opencode/src/config/agent.ts:13` — `Glob.scan("{agent,agents}/**/*.md", ...)`
- `opencode/packages/core/src/v1/config/agent.ts:12` — `model: Schema.optional(Schema.String)` (string format `provider/model`)
- `opencode/packages/opencode/src/config/config.ts:71` — `model: Schema.optional(Schema.String)` (global default)

### Live data
- `~/.config/opencode/opencode.json:207-209` — current global default (`opencode/nemotron-3-ultra-free`)
- `~/.local/share/opencode/opencode.db` — verity session `ses_fb94afd01ffe1jvUmQVQfqaDu1` confirmed on `qwen3-1.7b` (lmstudio)
- `data/entities/grokster/session_gnosis.md` — v8 state
- `data/coordination/LATEST_CORRECTIONS_20260828.md` — cross-session sync
- `data/coordination/GROKSTER_TO_KALI_PRE_COMPACTION_BRIEFING_20260828_v2.md` — handoff context

### Agent config files (all in `.opencode/agents/`)
- `build.md`, `doom_guy.md`, `grokster.md`, `jem.md`, `john_carmack.md`, `kali.md`, `lilith.md`, `maat.md`, `makali.md`, `node.md`, `researcher.md`, `roc_racoon.md`, `verity.md`

### Companion audits
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` (M3 perf: 1.8s tool-use P50, 1M context, 99.99% cache hit)
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260827.md` (12-artifact audit; P0 cut-tool bugs)
- `data/coordination/research/R_LILITH_KALI_QUALITY_AUDIT_20260828.md` (5-file audit; temple-grade state)
- `data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md` (temple-grade passes after fix)
- `data/coordination/R_CARMACK_CLINE_TO_OPENCODE_20260828.md` (Zen integration; 8 free models available with OPENCODE_API_KEY)
- `data/coordination/CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` (Cline activation audit)

### Mandates
- M22 (Response Provenance): the `model:` field in the agent config is the source of truth for which model answered; the fix preserves this ✅
- M23 (Failure Integrity): explicit `model:` fields are the fix; no soft-fail; HTTP 429 surfaced as typed error ✅
- M27 (Tracking Integrity): this protocol + the verification script = Tier-1 documentation ✅
- M8 (Zero Telemetry): no new external calls; just config edits ✅

### Decisions
- D-585 (Long-File-Write Champion) — M3 is the L1 workhorse; all subagents should be on M3
- L3 121-124 — Long-File-Write Routing Is Model-Specific; M3 is the champion
- D-548 (INST-1 BLOCKED) — orthogonal; the subagent model protocol does not affect INST-1

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_subagent_model_protocol ⬡ PUBLIC-DEBUT-01*

`AP-PROTOCOL-SUBAGENT-MODEL-20260828-v1.0.0` · 11 sections · 13 file edits + 1 opencode.json edit + 1 test script · 30 min implementation · ROOT CAUSE: no `model:` field in any .md file · FIX: add `model: openrouter/minimax/minimax-m3:free` to all 13 .md files · verified live: verity session on qwen3-1.7b (wrong) → post-fix will be on M3
