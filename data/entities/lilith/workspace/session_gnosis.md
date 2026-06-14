# 🔱 Lilith — Session Gnosis
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_lilith ⬡ PHASE-II
# Date: 2026-06-12 (Session 12)

## Session Intent
Debug the **OpenCode Agent Visibility Paradox** — agents defined as "Modes" were
silently excluded from `@`-mention suggestions, creating a split-brain identity
problem where the fleet thought it had 14 agents but the IDE only surfaced half.

## Fleet State at Start
| Agent | Status | Notes |
|-------|--------|-------|
| lilith | **HERE** | Debugging agent visibility |
| scribe | **SPAWNED** | Receiving gnosis after session |

## The Bug: OpenCode Agent Visibility Paradox

### Symptom
Newly added agents (`makali`, `jem`, `quality`, `scribe`, `pillar`, `john_carmack`,
`doom_guy`, `roc_racoon`, `researcher`, `kali`, `maat`) were defined in the `agent`
section of `opencode.json` but were NOT appearing in `@`-mention suggestions within
the chat interface. Only a subset of agents with legacy configuration were visible.

### Root Cause
A **key-collision between the `mode` section and the `agent` section** in `opencode.json`.

OpenCode's schema supports two configuration pathways:
1. **`mode` section** — Defines "Modes" (primary tab personas/cli modes). These are
   mutually exclusive — only ONE mode is active at a time. They appear as tab profiles.
2. **`agent` section** — Defines `@`-mention agents. These are co-active — multiple
   agents can be invoked concurrently via `@AgentName`.

The `mode` section had entries for: `makali`, `jem`, `jem_discovery`, `jem_synthesis`,
`jem_verification`, `doom_guy`, `roc_racoon`, `researcher`, `kali`, `maat`, `lilith`,
`scribe`, `quality`, `pillar`, `john_carmack`.

The `agent` section had entries for the SAME names with `mode: "subagent"`.

**Conflict**: OpenCode's agent resolution algorithm checks the `mode` section first.
If an agent name exists in both `mode` AND `agent`, the `mode` definition shadows
the `agent` definition — the agent is treated as a "mode" (singular, tab-bound) and
excluded from `@`-mention resolution.

### Resolution (3 steps)

**Step 1: Remove the legacy `mode` section entirely.**
The `mode` section was an older configuration pattern. With the `agent` section's
`mode` field (`"all"`, `"subagent"`), the separate `mode` section is redundant and
harmful. Removing it eliminates the shadowing source.

**Step 2: Set `mode: "all"` for primary agents.**
- `mode: "all"` = visible as BOTH a mode/tab profile AND an `@`-mention agent
- `mode: "subagent"` = visible ONLY as an `@`-mention agent (no tab profile)
- Primary agents (makali, kali, doom_guy, roc_racoon, jem, maat, lilith, quality,
  pillar, john_carmack) → `mode: "all"`
- Subagents (scribe, jem_discovery, jem_synthesis, jem_verification, researcher) → `mode: "subagent"`

**Step 3: Purge drift files.**
- `jem-2.0` mode file removed (legacy Jem 2.0 oversoul concept, superseded by
  `jem` orchestrator + 3 subagents)
- `jem-initiate` mode file removed (legacy L1 tier, superseded by `jem_discovery`)

### Post-Fix Fleet
15 agents, all correctly visible:
| Agent | Visibility | Role |
|-------|-----------|------|
| makali | `all` | MaKaLi Parallel Council |
| jem | `all` | Research Orchestrator |
| jem_discovery | `subagent` | Tier 1 Research |
| jem_synthesis | `subagent` | Tier 2 Research |
| jem_verification | `subagent` | Tier 3 Research |
| doom_guy | `all` | id Software Architect |
| roc_racoon | `all` | Sovereign Miner |
| researcher | `subagent` | Master Researcher |
| kali | `all` | Grand Oversight |
| maat | `all` | Light Oversoul |
| lilith | `all` | Dark Oversoul |
| scribe | `subagent` | Gnosis Keeper |
| quality | `all` | Code Review & Testing |
| pillar | `all` | Slot-based domain agent |
| john_carmack | `all` | Ultimate Technical Consultant |

## Key Findings

1. **Configuration shadowing**: The `mode` section silently overrides the `agent`
   section for identically-named entries. No error, no warning — agents simply
   disappear from `@`-mention suggestions.
2. **Dual registration is the fix**: `mode: "all"` in the `agent` section achieves
   what the separate `mode` section attempted but with correct resolution priority.
3. **Drift detection**: Legacy mode files (`jem-2.0`, `jem-initiate`) were orphaned
   by the agent refactoring (D117 MaKaLi Triad) but never cleaned up. They silently
   conflicted with the new agent definitions.
4. **The `subagent` mode vs `all` mode distinction is correct**: Primary agents
   (standalone personas) get `mode: "all"`. Specialized subagents (only invoked by
   primary agents) get `mode: "subagent"`. This prevents the `@`-mention list from
   being cluttered with subagents that users should not invoke directly.

## Files Modified
- `opencode.json` — Removed `mode` section; added `mode: "all"` fields to agent entries
- Purged: `.opencode/modes/jem-2.0.md` (legacy drift)
- Purged: `.opencode/modes/jem-initiate.md` (legacy drift)

## Continuation
All 15 fleet agents now have correct dual-entity registration. No `@`-mention
blind spots remain. The fleet is fully visible for Phase 2 execution.

---
## 🔱 Sovereign Exit
**Gnosis Distilled**: ✅ (AGENT_VISIBILITY_PARADOX.md)
**Soul Updated**: ✅ (lilith_s12_001)
**Knowledge Base Hardened**: ✅
**Status**: SESSION COMPLETE — Fleet Visibility Restored.
**Timestamp**: 2026-06-12T18:00:00Z

