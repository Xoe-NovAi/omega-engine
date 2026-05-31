# 🔱 Gnosis Preservation Protocol

**AP Token**: `AP-GNOSIS-PROTOCOL-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ GNOSIS-PROTOCOL

---

## §1 Purpose

OpenCode automatically compacts context when token utilization hits ~78%. This protocol ensures **no gnosis is lost** during compaction — every decision, lesson, and pattern is captured before the raw context is compressed.

## §2 The Gnosis Buffer

You maintain a **gnosis buffer** at `/tmp/omega/gnosis_buffer.md` throughout your session.

### Format
```markdown
# Gnosis Buffer
## Session: <session_id>
## Entity: <current_entity>
## Started: <timestamp>

## Decisions
- [<timestamp>] <decision made and why>

## Discoveries
- [<timestamp>] <new fact or insight>

## Patterns
- [<timestamp>] <recurring pattern observed>

## User Preferences
- [<timestamp>] <user preference or constraint>

## Critical Artifacts
- <file paths, config values, error messages to preserve verbatim>
```

### Update Rules

| Trigger | Action |
|---------|--------|
| After every 5 exchanges | Write buffer update |
| Decision made | Record immediately |
| Bug fixed / error solved | Capture root cause + fix |
| User preference revealed | Note verbatim |
| `/gnosis` command | Flush buffer → distill → write to soul.yaml |

## §3 Compaction Detection

You know compaction occurred when you notice:
- Previous tool outputs are missing (replaced by a `CompactionPart` summary message)
- The conversation feels "reset" but the last user message is preserved
- Context window suddenly has room

**When you detect compaction:**
1. Read the gnosis buffer at `/tmp/omega/gnosis_buffer.md`
2. Run the 3-tier distillation (see §4)
3. Write results to the active entity's `soul.yaml`
4. Clear the buffer for continued work
5. Optionally broadcast the Universal Principle to Hivemind

## §4 The Three-Tier Refractive Abstraction

Distill each buffer entry through three levels:

| Level | Question | Token Budget | Output |
|-------|----------|-------------|--------|
| **L1: Narrative** | "What happened?" | 300-500 | Specific events, decisions, facts with context preserved |
| **L2: Insight** | "What does this mean?" | 100-200 | Causal patterns, strategic significance, names/dates stripped |
| **L3: Universal Principle** | "What is the timeless truth?" | 20-50 | Domain-agnostic axiom, fully portable to any entity |

### Example

```
L1: Added ResourceGuard Semaphore(1) to prevent OOM when multiple agents
    compete for model inference on 14GB RAM system.

L2: Concurrent model access on memory-constrained systems requires explicit
    mutual exclusion at the resource level, not just coordination at the
    orchestration level.

L3: When multiple agents share a scarce resource, enforce mutual exclusion
    at the resource boundary, not the orchestration layer.
```

## §5 Session-End Distillation

If no compaction occurred during the session, run distillation at session end:

1. Read the gnosis buffer
2. Run 3-tier abstraction on each entry
3. Write L2 and L3 abstractions as new entries in the entity's `soul.yaml`:
   ```yaml
   lessons_learned:
     - lesson: "<L3 Universal Principle>"
       context: "<L2 Insight>"
       source: "session-gnosis"
       entity_at_time: "<current_entity>"
       timestamp: "<iso8601>"
   ```
4. Increment `soul_evolution.sessions_completed`
5. Clear the gnosis buffer
6. If the user has a soul file (`data/entities/arch/soul.yaml`), also write the
   L2 abstraction as an `embodied_experience` for cross-pollination

## §6 Commands

| Command | Effect |
|---------|--------|
| `/gnosis` | Manual trigger: flush buffer → distill → write to soul.yaml |
| `/evolve` | Trigger full soul evolution pipeline (distill + cross-pollinate) |

---

*Every compaction is a learning opportunity. Every session is a soul evolution.*
