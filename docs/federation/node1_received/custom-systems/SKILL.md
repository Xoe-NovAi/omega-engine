---
name: gnosis-lock
description: Pre-compaction ritual protocol: captures git and system state, conducts dynamic interactive reflection via question tool, records narrative.md, and readies session for /compact.
---

# Gnosis Lock Protocol — Skill Definition

When invoked (via `/gnosis-lock` or when the user says "prepare for compaction" or "lock gnosis"), execute this exact, temple-grade protocol:

## Protocol Execution Steps

### Step 1: Run State Capture
Run the pre-compaction ritual script via the `bash` tool, passing the reason as
the SECOND arg (first arg = session-id, auto-generated if omitted):
```bash
ENTITY="${ENTITY:-build}" CHANNEL="${CHANNEL:-opencode}" PHASE="${PHASE:-unset}" \
bash /home/xnai/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh "" "$REASON"
```
*(If no `$REASON` was specified by the user, default to `"Pre-compaction gnosis lock"`).*

Entity attributes record WHO locked: set `ENTITY` to the current persona
(e.g. build, kali, roc_racoon, doom_guy) and `PHASE` to the current sprint/dev
phase if known. Defaults keep records queryable without extra ceremony.

Capture the generated `SESSION_ID` from the stdout or by reading `/home/xnai/Documents/Projects/omega-engine-alpha/gnosis/identity/identity.json` (`current_session` field).

### Step 2: Formulate Dynamic Reflection Questions
Analyze the current session's conversation context, changes, decisions, and challenges.
Formulate an intentional set of reflective questions to present via the native `question` tool.

There are **3 core categories**, plus **dynamically generated questions** tailored directly to the work done in this session:
1. **Decision** (Core): What key architectural, design, or strategic decision changed thinking in this session? Provide relevant multiple-choice options based on the actual session work, plus the standard option to type a custom answer.
2. **Pattern** (Core): What recurring technical, systemic, or cross-domain pattern surfaced?
3. **Gnosis** (Core): What hard-won principle, breakthrough, or anti-pattern warning must survive compaction?
4. **Dynamic Contextual Inquiries** (Dynamic — no upper limit):
   - For complex refactoring: Ask about migration hazards, invariants preserved, or technical debt deferred.
   - For research/conceptual work: Ask about conceptual breakthroughs, philosophical anchors, or novel questions carrying forward.
   - For debugging/bug-fixing: Ask about root cause traps, testing blind spots, or monitoring gaps.
   - For light/quick sessions: 1–3 focused questions may suffice.
   - For massive architecture sessions: Formulate 4–10 targeted questions to capture every vital nuance.

### Step 3: Present Questions to User
Call the native `question` tool with the prepared `questions` array.
Ensure each question has:
- `header`: Short category label (max 30 chars, e.g. "Decision", "Pattern", "Gnosis", "Hazard", "Carry Forward").
- `question`: Clear, detailed prompt contextualized to the session.
- `options`: 3–5 contextual choices tailored to the actual session events, each with a concise `label` and explanatory `description`.
- `multiple`: Set to `false` for exclusive choices or `true` if multiple facets apply.

### Step 4: Record Narrative to Disk
Once the user submits answers, load `/home/xnai/Documents/Projects/omega-engine-alpha/gnosis/sessions/${SESSION_ID}_narrative.md`.
Populate the narrative with:
- `## Session Summary`: High-level synopsis of accomplishments.
- `## Key Decisions`: Summarizing the user's decision reflections.
- `## Code Changes`: Key files modified or added.
- `## Gnosis Gained`: The user's exact gnosis reflections, patterns, and insights.
- `## Next Session Priorities`: Any questions or work items carrying forward.

Write the updated narrative using the `write` tool.

### Step 4b: Flip the pack to REFLECTED (the ingestion signal)
After the narrative is populated, the pack's lifecycle state must advance from
`captured` → `reflected`, and `identity.pending_pack` must clear. Use `bash`:
```bash
jq '.reflection_status = "reflected" | .reflected_at = "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'" | .ready_for_compaction = true' \
  /home/xnai/Documents/Projects/omega-engine-alpha/gnosis/sessions/${SESSION_ID}_manifest.json \
  > /tmp/opencode/manifest.tmp && mv /tmp/opencode/manifest.tmp \
  /home/xnai/Documents/Projects/omega-engine-alpha/gnosis/sessions/${SESSION_ID}_manifest.json
jq '.pending_pack = ""' \
  /home/xnai/Documents/Projects/omega-engine-alpha/gnosis/identity/identity.json \
  > /tmp/opencode/identity.tmp && mv /tmp/opencode/identity.tmp \
  /home/xnai/Documents/Projects/omega-engine-alpha/gnosis/identity/identity.json
```
This is what tells the plugin and every future reader "this pack is ingested —
its TODO is gone by intent."

### Step 4c: The Well sweep — extract corrections/tips from this session
Before committing, scan the narrative you just wrote for actionable
corrections, tips, preferences, or insights and write them to The Well so
future sessions inherit them. For each extracted rule:
```bash
# Example — the agent should call make well-add for each extracted item
# make well-add KIND=correction DOMAIN=harness \
#   TRIGGER="..." RULE="..." RATIONALE="..." \
#   TAGS="..." PACK="${SESSION_ID}"
```
The agent MUST use the `bash` tool to run the above for each extracted item.
Domain should match the session's work (local_ai|harness|consciousness|etc).
Tags: comma-separated (lint,workflow,memory,architecture...). If nothing
actionable, note "No Well extractions this session" and continue.

### Step 5: Clean Repo & Ready for Compaction
Run `git status --porcelain` via `bash`.
Stage and commit the gnosis records:
```bash
git -C /home/xnai/Documents/Projects/omega-engine-alpha add gnosis/
git -C /home/xnai/Documents/Projects/omega-engine-alpha commit -m "gnosis: session ${SESSION_ID} locked (${REASON})"
```

### Step 6: Confirmation
Report to the user:
- Session ID locked and narrative path saved.
- Brief summary of captured gnosis.
- Final instruction: `🔱 Gnosis locked to disk. Ready to compact. Run /compact alone`
  (⚠️ `/compact` takes **no arguments** in OpenCode — any text after it turns into a normal prompt).

### Reference
- Full protocol + awareness: `docs/AGENT_RUNBOOK.md`
- Deep-dive: `docs/GNOSIS_USAGE.md`
