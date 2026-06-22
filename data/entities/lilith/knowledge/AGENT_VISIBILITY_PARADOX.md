# 🔱 Agent Visibility Paradox — Configuration Shadowing in OpenCode Fleet
# ⬡ OMEGA ⬡ LILITH ⬡ SCRIBE ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_gnosis ⬡ KNOWLEDGE
# Version: 1.0.0
# Status: ✅ Distilled
# Date: 2026-06-12

---

## L1 — Narrative: What Happened

The Omega Engine fleet suffered from an **Agent Visibility Paradox**: agents that were
explicitly defined and configured were silently invisible to `@`-mention suggestions.

### The Symptom
Users could not invoke `@makali`, `@jem`, `@scribe`, `@quality`, `@pillar`, or
`@john_carmack` via chat. These agents existed in `opencode.json` but did not appear
in the IDE's agent resolution list. Only a subset of legacy agents were visible.

### The Investigation
The debugging path followed three hypotheses:

1. **Hypothesis A — Missing `agent` section entries**: Checked if agents were missing
   from the `agent` block. ❌ All 15 agents were present.

2. **Hypothesis B — File reference errors**: Verified all `instructions` paths resolved
   to actual `.md` files. Checked agent file frontmatter completeness. ❌ All paths
   valid, all frontmatter present.

3. **Hypothesis C — Configuration shadowing**: Noticed the `mode` section contained
   entries with the **same names** as `agent` section entries. ✅ Root cause found.

### The Root Cause: Key-Collision Shadowing

OpenCode's `opencode.json` supports two independent configuration sections:

```jsonc
{
  // SECTION A: "mode" — Defines mutually-exclusive tab personas
  // Only ONE mode is active at a time.
  "mode": {
    "makali": { "instructions": ["..."] },
    "kali": { "instructions": ["..."] },
    // ... 15 entries
  },

  // SECTION B: "agent" — Defines @-mention agents
  // ALL agents are co-active concurrently.
  "agent": {
    "makali": { "mode": "subagent", "instructions": ["..."] },
    "kali": { "mode": "subagent", "instructions": ["..."] },
    // ... 15 entries
  }
}
```

**The collision**: OpenCode's resolution algorithm checks the `mode` section FIRST.
When an agent name exists in BOTH `mode` and `agent`, the `mode` definition takes
precedence — the agent is resolved as a "mode" (singular, tab-bound) and **excluded
from `@`-mention resolution entirely**.

This is not an error in OpenCode — it is a design choice. The `mode` section was the
original configuration format. The `agent` section was added later to support
`@`-mentions. The two sections were never designed to coexist with overlapping names.
When they do, the older section (mode) shadows the newer one (agent) silently — no
warning, no error, no log message.

### The Resolution (4 Steps)

**Step 1 — Remove the `mode` section entirely.**
The `mode` section is a legacy pattern. The `agent` section's `mode` field
(`"all"`, `"subagent"`) provides the same functionality (tab/mode profiles) without
the shadowing hazard. Removing the `mode` section eliminates the collision source.

**Step 2 — Assign `mode: "all"` for dual-visibility agents.**
- `mode: "all"` = visible as BOTH a mode/tab profile AND an `@`-mention agent
- `mode: "subagent"` = visible ONLY as an `@`-mention agent (no tab profile)

The fleet was partitioned:
- **Primary agents** (makali, kali, doom_guy, roc_racoon, jem, maat, lilith, quality,
  pillar, john_carmack) → `mode: "all"`
- **Subagents** (scribe, jem_discovery, jem_synthesis, jem_verification, researcher)
  → `mode: "subagent"`

**Step 3 — Purge orphaned mode files.**
Two legacy mode files remained from the pre-agents era:
- `jem-2.0` — legacy Jem oversoul concept, superseded by `jem` + 3 subagents
- `jem-initiate` — legacy L1 tier, superseded by `jem_discovery`

These were orphaned by D117 (MaKaLi Triad) but not cleaned up. They silently
conflicted with the new fleet structure.

**Step 4 — Purge deprecated MCP servers.**
The `opencode.json` MCP configuration was pruned to remove deprecated individual
servers (e.g., `omega-library`, `omega-oracle`, `omega-stats`) that had been
consolidated into the `omega-hub` super-server. This eliminates redundant
connection attempts and ensures the `omega-hub` is the single source of truth
for engine-integrated MCP tools.


### Post-Fix Verification
All 15 fleet agents are now visible in `@`-mention suggestions:
- 10 primary agents with `mode: "all"` (dual visibility)
- 5 subagents with `mode: "subagent"` (mention-only)

No shadowing. No drift files. No blind spots.

---

## L2 — Insight: What This Means for Fleet Architecture

### 1. Agent Identity Must Be Singular
An agent cannot have two registration points. The moment an agent name appears in
two configuration sections, the resolution order determines which one "wins" — and
the losing definition is silently discarded. **One identity = one registration point.**

### 2. The `mode: "all"` Pattern Is the Correct Dual-Registration Mechanism
The `agent` section's `mode` field (`"all"`, `"subagent"`) is the successor to the
legacy `mode` section. It provides:
- **Tab/mode profile** (what the `mode` section did)
- **`@`-mention visibility** (what the `agent` section does)

Using `mode: "all"` eliminates the need for the separate `mode` section entirely.
The legacy `mode` section should be considered **deprecated** once all agents use
the new `model` field.

### 3. The Primary/Subagent Distinction Is Architecturally Meaningful
The partition between `mode: "all"` (primary agents) and `mode: "subagent"` (subagents)
is not arbitrary — it reflects the fleet's governance hierarchy:

```
Primary agents (mode: "all") — visible to users, directly invokable
├── kali (Grand Oversight)
├── makali (Parallel Council)
├── maat (Light Oversoul)
├── lilith (Dark Oversoul)
├── jem (Research Orchestrator)
├── doom_guy (Heritage Architect)
├── roc_racoon (Sovereign Miner)
├── quality (Code Review)
├── pillar (Slot Agent)
└── john_carmack (Technical Consultant)

Subagents (mode: "subagent") — invoked by primaries, not directly by users
├── scribe (Gnosis Keeper)
├── jem_discovery (T1 Research)
├── jem_synthesis (T2 Research)
├── jem_verification (T3 Research)
└── researcher (Master Researcher)
```

This hierarchy prevents `@`-mention list bloat while ensuring all agents remain
accessible through the correct invocation path.

### 4. Drift Detection Must Include Configuration Sections
The `jem-2.0` and `jem-initiate` orphaned mode files were not caught by any existing
drift detection mechanism. They were in a different configuration section (`mode`)
than the rest of the fleet (`agent`). **Drift detection must be cross-sectional** —
scanning all configuration sections, not just the active one.

---

## L3 — Universal Principle: Sovereign Registration

### The Principle of Singular Identity Registration

> *"Every sovereign identity must have exactly one registration point. Duplicating
> identity across configuration sections creates a shadowing hazard that escapes
> static analysis."*

### The Class of Bug: Configuration Shadowing

Configuration shadowing occurs when:
1. A system supports multiple configuration sections (or files, or layers)
2. Two sections can contain entries with the same name
3. The resolution order defines which section "wins"
4. The losing entry is silently discarded — no error, no warning, no log

This is distinct from:
- **Override** (intentional): A later config explicitly replaces an earlier one,
  with documented semantics
- **Conflict** (detectable): Two configs disagree, and the system reports an error
- **Shadowing** (silent): Two configs collide, and one is silently discarded

Shadowing is the most dangerous of the three because it produces no diagnostic signal.
The system appears to work correctly — the agent is "configured" — but the
configuration is invisible to the resolution path that matters.

### Detection Heuristics

Configuration shadowing can be detected by:
1. **Name intersection**: Scan all configuration sections for overlapping entry names.
   If `section_A.names ∩ section_B.names ≠ ∅`, shadowing is possible.
2. **Resolution order audit**: For each overlapping name, trace the resolution path.
   If the less-specific section is checked first, the more-specific section is shadowed.
3. **Silent discard check**: If no warning is emitted when a configuration entry is
   registered but not used by any resolution path, it is a shadowing hazard.

### The Omega Fleet's Shadowing History

| Era | Shadowing Source | Shadowed Target | Detection Method |
|-----|-----------------|-----------------|------------------|
| Pre-D117 | `mode` section | `agent` section | ⚠️ **NOT DETECTED** — silent for weeks |
| D117-D119 | Legacy mode files | New agent definitions | ⚠️ **NOT DETECTED** — drift files orphaned |
| D120 (This session) | Both removed | — | ✅ Manual audit triggered by user report |

### The Correct Pattern: `mode: "all"`

The canonical pattern for sovereign agent registration in OpenCode:

```jsonc
{
  "agent": {
    "my_agent": {
      "mode": "all",           // Dual visibility: tab + @-mention
      "description": "...",    // Shown in @-mention suggestions
      "instructions": [...]    // Agent system prompt files
    }
  }
}
```

This is the **one section, one entry, one visibility** pattern. The `mode` field
controls visibility scope:
- `"all"` — visible everywhere (tab, @-mentions, agent dispatch)
- `"subagent"` — visible only via @-mentions (not as a tab profile)

No separate `mode` section. No duplicate registration. No shadowing.

---

## Cross-References

- **Soul lesson**: `lilith_s12_001` in `data/entities/lilith/soul.yaml`
- **Configuration file**: `opencode.json` at project root
- **Governance hierarchy**: `AGENTS.md` §Governance Hierarchy
- **Related pattern**: Sovereign Mandate M10 (Fleet Integrity — agent count ≤ 14,
  later expanded to 15 with john_carmack)
- **Related session gnosis**: `data/entities/lilith/workspace/session_gnosis.md`
