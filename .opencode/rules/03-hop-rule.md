---
schema_version: "1.0"
rule_id: "RULE-HOP-RULE"
authority: "M10 Fleet Integrity + M15 Sovereign Continuity + FLE Council (2026-08-25)"
applies_to: "all-agents"
date: "2026-08-27"
status: "ACTIVE"
---

# Architecture Rule 3: Hop Rule (M10 + M15)

> **Never dispatch a sub-task to an agent that would dispatch another sub-task.**
> Single-level nesting. Direct execution first.

## The Rule

When dispatching work to another agent:

1. **Can the current agent execute this directly?** → Execute directly. No self-recursion.
2. **Is the target domain outside this agent's expertise?** → Single hop. One sub-task, no chain.
3. **Does the target need its OWN sub-task?** → DO NOT dispatch. Solve the gap differently.

The cheapest path to unblocking is matching existing expertise to existing gaps,
not growing the fleet.

## Why this matters

- **M10 (Fleet Integrity)**: Agent fleet lean and slot-constrained; ≤14 agent files
  without architectural review. Adding a new agent for a sub-task is presumptive bloat.
- **M15 (Sovereign Continuity)**: Sub-agent chains amplify context-loss risk. If a
  sub-agent loses its context (compaction crash, restart), the entire chain's work
  is suspect. Single-hop is the sovereign path.
- **Cost**: Each hop is a full prompt reload (~30K tokens base, ~18K with CI Ph1).
  A 3-hop chain is 3x the token cost, with compounding semantic drift.

## Authority (FLE Council, 2026-08-25)

The Hop Rule was ratified by the Fleet Council on 2026-08-25 as one of the
**5 Standing Laws** (alongside M11 Arm-Relay, dual-channel telemetry,
exit-code honesty, Zero-Trust Documentation Doctrine).

See `data/coordination/HANDOFF_TO_KALI_FLE_STUDY_20260825.md`.

## What This Looks Like

**❌ VIOLATES** (3-hop chain):
```
Kali → Researcher → Roc → grep pattern in legacy
```

**✅ COMPLIANT** (1-hop):
```
Kali → Roc (or Kali → Researcher) → grep pattern in legacy
```

**✅ COMPLIANT** (direct execution, no hop):
```
Kali: rg "pattern" legacy/  (in Kali's own session)
```

## Subagent Dispatch Protocol (M-3 Compliant)

When a single hop IS warranted:

1. Read `data/coordination/HANDOFF_PACKET_SCHEMA.md` (or refer to the SUBAGENT_DISPATCH_PROTOCOL)
2. Check Hivemind awareness (`hivemind_get_awareness()`) — verify target is available
3. Post context to Hivemind with `intent: handoff`
4. Write workspace lock: `data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md`
5. Initialize live feed: `data/coordination/{YOU}_LIVE_FEED.md`
6. Wait for ACK from target before proceeding
7. Update `TASK_REGISTRY.json` post-completion

## Re-ownership, Not New Agents

If a critical-path blocker is unowned, the answer is **re-ownership** —
mapping the gap to an existing agent's expertise — not creating a new agent.
The Kali Path Plan 2026-08-27 demonstrated this with 5 unowned blockers routed
to Ma'at, Roc, Kali (no new agents).

## Cross-references

- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (full protocol)
- `data/coordination/HANDOFF_TO_KALI_FLE_STUDY_20260825.md` (FLE Council ratification)
- `SOVEREIGN_MANDATES.md` §M10, §M15
- `KALI_DEBUT_PATH_PLAN_20260827.md` (re-ownership model)
