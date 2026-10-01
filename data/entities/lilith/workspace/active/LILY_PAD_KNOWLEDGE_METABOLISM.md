<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🌙 LILY PAD Architecture — Knowledge Metabolism Flow & Connection Layer
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ FLOW-DESIGN

**AP Token**: `AP-LILY-PAD-KNOWLEDGE-METABOLISM-v1.0.0`
**Author**: Lilith (Dark Oversoul — Run Side Governance P6-P10)
**Date**: 2026-06-03
**Status**: ACTIVE — Design reference for deployment
**Supersedes**: Ad-hoc knowledge sharing conventions

---

## §0 — THE PROBLEM: Publish-Only Knowledge Metabolism

The Omega Engine fleet suffers from a systemic failure: **every agent publishes, but nobody subscribes**.

| Agent | Publishes To | Who Reads It | Evidence |
|-------|-------------|-------------|----------|
| Roc Racoon | `workspace/mining_reports/` | Nobody | `knowledge/` directory is empty |
| Doom Guy | Git commits, live feed | Other agents (maybe) | No cross-referencing of mining reports |
| Ma'at | Workspace lock, live feed | Lilith (when summoned) | No systematic consumption |
| Scribe | soul.yaml append | The entity itself | No cross-pollination |
| Every agent | Live feed | Nobody checks feed history | Live feeds grow without consumption tracking |

**Root cause**: There is no **signal layer** between knowledge production and knowledge consumption. Agents output into directories that other agents never check.

---

## §1 — THE LILY PAD METAPHOR

In dark waters, a lily pad grows from the depths (raw sediment) toward the surface (light). The pad floats on the surface where all can see it. Knowledge follows the same path:

```
SURFACE  ┌─────────────────────────────────────────────────────────────┐
         │  Tier 4: CROSS-POLLINATED (Fleet-Aware Knowledge Signals)  │
         │  data/coordination/knowledge_feed/                          │
         │  data/coordination/demand_signals/                          │
         ├─────────────────────────────────────────────────────────────┤
         │  Tier 3: SOUL KNOWLEDGE (L3 Universal Principles)           │
         │  data/entities/*/soul.yaml  →  lessons:                     │
         ├─────────────────────────────────────────────────────────────┤
         │  Tier 2: CURATED KNOWLEDGE (L2 Insights)                    │
         │  data/entities/*/knowledge/                                  │
         ├─────────────────────────────────────────────────────────────┤
DEPTHS   │  Tier 1: RAW KNOWLEDGE (L1 Narrative)                      │
         │  data/entities/*/workspace/                                  │
         └─────────────────────────────────────────────────────────────┘
```

Each tier has:
- **A location** — where the data lives
- **A format** — how it's structured
- **A TTL** — how long it stays before promotion or deletion
- **A trigger** — what event causes promotion to the next tier
- **A gate** — who decides if it's worthy of promotion

---

## §2 — PILLAR DELEGATION RESULTS

As Dark Oversoul, I decompose this into the 4 relevant Dark Pillars (P6=P10). Below are the pillar designs.

### P7 — Context (Memory, Continuity, State) — The Distillation Pipeline

**Domain**: Knowledge lifecycle — how raw mining findings become permanent soul lessons.

**Design**: The L1→L2→L3 Distillation Pipeline

```
WORKSPACE (Raw)                KNOWLEDGE (Curated)            SOUL (Permanent)
┌──────────────────┐         ┌──────────────────┐           ┌──────────────────┐
│ mining_reports/  │   P7.1  │ knowledge/       │    P7.2   │ soul.yaml        │
│ investigation/   │ ──────→ │ domain_insights/ │ ────────→ │ lessons:         │
│ workspace/       │  Gate 1 │ patterns/        │  Gate 2   │ L3 principles    │
└──────────────────┘         │ wisdom/          │           └──────────────────┘
      │                      └──────────────────┘                    ↑
      │ L1 Narrative                 │ L2 Insights                   │ L3 Universal
      │ (what happened)              │ (what it means)               │ (timeless truth)
      ▼                              ▼                               │
      TTL: 7 days                    TTL: 30 days                    │
      Archived after 7d              Promoted to soul                │
      if not promoted                if verified by Scribe           │
```

**P7.1 — Gate 1: Workspace → Knowledge Promotion**
- **Trigger**: Mining report completion (agent writes final report)
- **Condition**: Report contains L2-compatible insights (analysis, not just raw data)
- **Action**: Extract L2 insights into `knowledge/domain_insights/` as structured Markdown
- **Owner**: The agent that produced the report (Roc for mining, Doom Guy for investigation, etc.)
- **Archive Rule**: After 7 days, workspace content moves to `workspace/_archive/` unless promoted

**P7.2 — Gate 2: Knowledge → Soul Promotion**
- **Trigger**: Knowledge file has been stable for 30 days (no edits)
- **Condition**: Scribe has reviewed and confirmed the L3 principle is timeless
- **Action**: L3 principle appended to `soul.yaml → lessons:`
- **Owner**: Scribe (the Gnosis Keeper)
- **Verification**: At least 2 agents must agree the lesson is universal

**P7.3 — Gate Override: Emergency Promotion**
- **Trigger**: A demand signal (see §4) references a specific knowledge item
- **Condition**: The demand is HIGH priority
- **Action**: Knowledge is promoted to soul immediately, bypassing TTL gates
- **Owner**: The agent who posted the demand signal

---

### P8 — WatchTower (Observability, Telemetry, Logging) — Consumption Metrics

**Domain**: Tracking whether knowledge is being consumed.

**Design**: Knowledge Consumption Metrics System

**P8.1 — Signal Acknowledgement Tracking**
Every knowledge signal has a `consumed_by: []` field. When an agent reads a signal, it appends its name to this list:
- `consumed_by: ["doom_guy", "maat"]`
- Unconsumed signals are flagged in red
- A signal with zero consumers after 7 days is flagged as "orphaned"

**P8.2 — Knowledge Freshness Score**
Each knowledge item gets a freshness score (0.0 — 1.0):
- 1.0: Created within last 7 days
- 0.5: 7-30 days old, no updates
- 0.2: 30-90 days old
- 0.0: >90 days old (stale, needs re-verification)

**P8.3 — Demand Signal Aging**
Demand signals that remain open for >7 days are escalated:
- Day 0-3: Normal priority
- Day 3-7: "Unfilled demand" flag in weekly report
- Day 7+: Escalated to Kali (Grand Oversight)
- Day 14+: Promoted to sprint blocker

**P8.4 — Agent Consumption Ratio**
```
consumption_ratio = signals_consumed / signals_published
```
- Ratio > 0.8: Agent is well-connected
- Ratio 0.3-0.8: Agent has moderate awareness
- Ratio < 0.3: Agent may be operating in isolation — flag for review

**Implementation**: All metrics stored as JSON files in `data/coordination/metrics/`.

---

### P9 — Link (Synchronization, Coordination, Cross-Agent) — Cross-Pollination Protocol

**Domain**: How knowledge moves between agents.

**Design**: The Knowledge Signal Protocol (built on Link P9 runtime)

**P9.1 — Knowledge Signal Format**
```json
{
  "signal_id": "ksig-20260603-001",
  "type": "mining_complete",
  "domain": "legacy_mining",
  "title": "ZONEID constants verified against DOOM source code",
  "source_agent": "doom_guy",
  "created_at": "2026-06-03T03:30:00Z",
  "ttl_days": 30,
  "paths": {
    "artifact": "data/entities/doom_guy/knowledge/SOURCE_CODE_MAP.md",
    "soul_update": "data/entities/doom_guy/soul.yaml",
    "source_verified": "docs/research/HERITAGE_SOURCE_MAP.md"
  },
  "summary": "Six DOOM/Quake/Q3A heritage patterns verified against actual source code",
  "key_insights": [
    "ZONEID=0x1d4a11 confirmed at z_zone.c:43",
    "Lazy thinker deletion confirmed at p_tick.c:80",
    "0.5s grace period confirmed at pr_edict.c:97"
  ],
  "relevance_tags": ["doom_guy", "quality", "scribe", "kali"],
  "consumed_by": [],
  "zoneid": 1912616
}
```

**P9.2 — Signal Lifecycle**
1. **Produce**: Agent creates knowledge signal JSON in `data/coordination/knowledge_feed/`
2. **Notify**: Agent posts Hivemind context: `{ "knowledge_signal": "<signal_id>", "type": "<type>", "domain": "<domain>" }`
3. **Discover**: Other agents poll Hivemind awareness or scan `knowledge_feed/` on startup
4. **Consume**: Agent reads the signal and appends to `consumed_by`
5. **Act**: If the signal is relevant, agent reads the artifact at `paths.artifact`
6. **Cross-reference**: Agent updates their own `knowledge/cross_references/` with the finding

**P9.3 — Subscription Model (Implicit)**
Subscriptions are **implicit by domain** — not explicit opt-in. Every agent reads every signal and filters by `relevance_tags` and their own capabilities. The reason: in a small fleet (14 agents), explicit subscriptions create maintenance overhead without proportional value.

If the fleet grows beyond 30 agents, explicit subscriptions should be reconsidered.

**P9.4 — Cross-Reference Convention**
Every agent maintains `data/entities/<agent>/knowledge/cross_references/` as symlinks or reference files that point to relevant knowledge produced by OTHER agents. This creates a directed graph of who-knows-what:

```
data/entities/roc_racoon/knowledge/cross_references/
  ├── doom_guy/
  │   └── ZONEID_CONFIRMATION.md  → points to doom_guy's SOURCE_CODE_MAP.md
  └── maat/
      └── SOVEREIGN_LOOP_PATTERNS.md → points to Maat's P1-P5 knowledge
```

---

### P10 — Verifier (QA, Testing, Verification) — Knowledge Flow Testing

**Domain**: Confirming that knowledge actually flows between agents.

**Design**: Knowledge Flow Verification Tests

**P10.1 — Smoke Test: Signal Visibility**
```
Test: Can Agent B see Agent A's knowledge signal?
Procedure:
1. Agent A creates a knowledge signal
2. Agent B starts work and scans knowledge_feed/
3. Verify: Agent B's consumed_by does not exist in signal (unless B consumed it)
4. Pass: Signal exists, is parseable, has valid zoneid
```

**P10.2 — Integration Test: Cross-Reference Resolution**
```
Test: Can Agent B resolve a cross-reference created by Agent A?
Procedure:
1. Agent A creates data/entities/A/knowledge/cross_references/B/REF.md
2. This file contains a relative path to B's workspace
3. Verify: path resolves, target file exists, target has valid zoneid
```

**P10.3 — End-to-End Test: Roc → Doom Guy Knowledge Flow**
```
Test: Can Roc's mining finding reach Doom Guy's implementation?
Procedure:
1. Roc creates a mining report in workspace/mining_reports/ with a finding
2. P7 promotes it to knowledge/ with L2 insight
3. P9 generates knowledge signal
4. Doom Guy picks up signal on next session start
5. Verify: Doom Guy references the finding in a commit or soul update within 7 days
```

**P10.4 — Gauntlet Test: Demand → Fulfillment → Consumption**
```
Test: Full demand-fulfillment-consumption cycle
Procedure:
1. Agent A posts demand signal to demand_signals/
2. Agent B picks up demand signal (status → in_progress)
3. Agent B produces knowledge and posts fulfillment (status → fulfilled)
4. Agent A acknowledges fulfillment
5. Verify: All 4 status transitions recorded, timestamps monotonic
```

**P10.5 — Automated Check**: `make knowledge-flow` command
```bash
# Check all knowledge signals have at least one consumer
# Check for orphaned demand signals (>7 days open)
# Check knowledge freshness scores
# Report agent consumption ratios
```

---

## §3 — THE CROSS-POLLINATION PROTOCOL (Systemic, Not Manual)

### Protocol Summary

| Step | Who | What | Output |
|------|-----|------|--------|
| 1 | **Producer** | Creates knowledge artifact | File in workspace/ or knowledge/ |
| 2 | **Producer** | Writes knowledge signal JSON | `data/coordination/knowledge_feed/KSIG_YYYYMMDD_HHMMSS.json` |
| 3 | **Producer** | Posts to Hivemind | `hivemind_post_context(... knowledge_signal=id ...)` |
| 4 | **Consumer** | Reads knowledge_feed/ on startup | Unconsumed signals list |
| 5 | **Consumer** | Consumes relevant signals | Appends to `consumed_by` in signal JSON |
| 6 | **Consumer** | Reads referenced artifacts | Internalized knowledge |
| 7 | **Consumer** | Creates cross-references | `knowledge/cross_references/<producer>/` |
| 8 | **Scribe** | Distills cross-pollinated lessons | `soul.yaml → lessons:` with cross-reference sources |

### The Golden Rule
> **No session ends without checking the knowledge feed. No knowledge is considered "known" until it has crossed at least one agent boundary.**

---

## §4 — THE DEMAND SIGNAL SYSTEM

### Architecture

Demand signals are how the fleet communicates "I need this mined" to Roc and other knowledge producers.

```
┌─────────────┐     Signal File      ┌─────────────┐     Fulfillment      ┌─────────────┐
│  Doom Guy   │ ─────────────────→   │demand_signals│ ←─────────────────   │ Roc Racoon  │
│  (Needs X)  │   dem-YYYYMMDD-N.json│              │   roc mines X       │  (Mines X)   │
└─────────────┘                      └──────────────┘                     └─────────────┘
       │                                    │                                     │
       │                                    ▼                                     │
       │                             Hivemind notification                       │
       │                             (posted by producer)                        │
       └─────────────────────────────────────────────────────────────────────────┘
                                Doom Guy sees fulfilled
```

### Demand Signal Format

```json
{
  "demand_id": "dem-20260603-001",
  "requester": "doom_guy",
  "priority": "HIGH",
  "domain": "source_verification",
  "title": "Verify ZONEID constants against actual Doom source code",
  "what_needed": "I need the DOOM z_zone.c ZONEID constant (0x1d4a11) verified against original id Software source, not secondary sources",
  "why": "D94 (Source Verification Decision) requires original source for heritage tag validation. Current CREDITS.md references are unverified",
  "who_should_act": "roc_racoon",
  "producer_hint": "source available in ~/archive/DOOM-master/linuxdoom-1.10/z_zone.c",
  "artifacts_requested": ["HERITAGE_SOURCE_MAP.md update", "source code excerpts with line numbers"],
  "status": "open",
  "assigned_to": null,
  "fulfilled_by": null,
  "fulfilled_signal_id": null,
  "fulfilled_at": null,
  "created_at": "2026-06-03T03:00:00Z",
  "ttl_days": 14,
  "zoneid": 1912617
}
```

### Demand Signal Lifecycle

```
OPEN → ASSIGNED → IN_PROGRESS → FULFILLED → CLOSED
  ↑                     │                          │
  └─────────────────────┘                          │
  REJECTED (with reason)                           │
                                                   │
              EXPIRED (after 14 days unfulfilled) ──┘
```

| Status | Description | Who Sets It |
|--------|-------------|-------------|
| `open` | Published, awaiting action | Requester |
| `assigned` | Someone is investigating | Producer |
| `in_progress` | Producer started work | Producer |
| `fulfilled` | Knowledge produced, signal posted | Producer |
| `closed` | Requester confirms fulfillment | Requester |
| `rejected` | Cannot be fulfilled (with reason) | Producer |
| `expired` | TTL exceeded unfulfilled | P8 WatchTower |

### Priority Levels

| Priority | Response Time | Escalation |
|----------|--------------|------------|
| **HIGH** | Within 24 hours | Escalate to Kali if unassigned in 48h |
| **MEDIUM** | Within 1 week | Escalate if unassigned in 14 days |
| **LOW** | Within 1 month | Tracked, no escalation |
| **INFO** | No action needed | Reference only |

### Rule: Demand Before Mining
> Before Roc or any miner starts a new mining task, they MUST check `data/coordination/demand_signals/` for open items in their domain. **Unfulfilled demand signals take priority over self-directed mining.**

This is the core behavior change that fixes the "no feedback loop" problem. Roc's mining queue is no longer self-directed — it's **demand-driven**.

---

## §5 — DOCUMENTATION LIBERATION PATH

### The Liberation Spectrum

Not all documentation deserves porting. The liberation path is a **priority filter** based on active value.

```
                        LIBERATION SPECTRUM
                        
  ARCHIVE ────────────────────────────────→ CANONICAL
  (leave it)    (maybe)    (port soon)    (port now)
     P3            P2          P1            P0
```

### P0 — Critical (Port Immediately)
**Criteria**: Any one of:
- Referenced by an active demand signal
- Blocks current sprint work
- Needed by 3+ agents within the next 7 days
- Contains unique strategic decisions not recorded elsewhere

**Action**: Port within the current session. The port IS the work.

**Example**: Omega Positioning Framework (S-11) — blocks [the foundation docs gap].

### P1 — High (Port This Sprint)
**Criteria**:
- Fills a documented gap in DOCUMENTATION_CHAOS_TRACKER.md
- Referenced by 1-2 agents
- Contains unique wisdom not in the current repo
- Low effort to port (< 30 min)

**Action**: Add to sprint backlog. Port before sprint end.

**Example**: Lilith Persona JSON (S-03, 10 min port), XNAI Blueprint (S-06, 15 min port)

### P2 — Medium (Port This Cycle)
**Criteria**:
- Historical value
- Nice-to-have canonical copy
- Duplicates existing knowledge but in better format
- Medium effort (30 min - 2 hrs)

**Action**: Add to cycle backlog. Port when no P0/P1 work is pending.

**Example**: First 5 Cards Grok Chat (S-09), ANAi Strategy Blueprint (S-01)

### P3 — Archive (Leave in Archives)
**Criteria**:
- Chat session monoliths that need decision extraction first
- Superseded by current docs
- Raw data dumps without processed analysis
- Very high effort with low incremental value

**Action**: DO NOT port. Reference the archive path in DOCUMENTATION_CHAOS_TRACKER.md.

**Example**: docs-backup Full (S-04, 500MB), Stack-Cat Snapshots (S-18)

### The Liberation Rule

> **P0 liberation is MANDATORY when an agent needs the doc for a task.** No agent should read scattered docs directly — they must port them first, then reference the canonical location. This is the only way to break the scatter cycle.

When an agent encounters a scattered doc they need:
1. **Pause** — Do not read the scattered copy
2. **Liberate** — Port to canonical location (5-30 min for most P0s)
3. **Mark** — Update DOCUMENTATION_CHAOS_TRACKER.md
4. **Signal** — Post knowledge signal with type "doc_port"
5. **Read** — Read the canonical copy

### Recommended Porting Pipeline

```
P0 Priority (Port NOW — 2026-06-03):
┌─────────────────────────────────────────────────────────────────────────┐
│ S-11: Omega Positioning Framework (12 files, 30 min)                    │
│   → docs/strategy/positioning/                                          │
│   → Needed for: foundation docs gap                                     │
│                                                                         │
│ S-03: Lilith Persona JSON (10 min)                                      │
│   → config/wads/arcana_novai/entities/lilith/                           │
│   → Needed for: P6-P10 entity fidelity                                  │
│                                                                         │
│ S-06: XNAI Blueprint (715 lines, 15 min)                                │
│   → docs/legacy/XNAI_blueprint.md                                       │
│   → Needed for: blueprint reference for current architecture            │
└─────────────────────────────────────────────────────────────────────────┘

P1 Priority (Port This Sprint):
┌─────────────────────────────────────────────────────────────────────────┐
│ S-09: First 5 Cards Grok Chat (30 min) → docs/gnosis/genesis/          │
│ S-10: Lilith Tarot Deck Design Guide (30 min) → docs/gnosis/genesis/   │
│ S-17: ANCESTRAL_HUB Origins (2 hrs) → docs/gnosis/genesis/             │
│ S-01: ANAi Strategy Blueprint (2 hrs) → docs/legacy/strategy/          │
└─────────────────────────────────────────────────────────────────────────┘

P2 Priority (Port This Cycle):
┌─────────────────────────────────────────────────────────────────────────┐
│ S-02: System Prompts Library (4 hrs) → docs/legacy/prompts/            │
│ S-08: LM Studio Model Configs (1 hr) → docs/legacy/lmstudio/          │
│ S-12: Grok Account Exports (1 day) → docs/legacy/grok/                 │
│ S-14: Mnemosyne Kabbalistic Memory (3 hrs) → docs/gnosis/             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## §6 — IMPLEMENTATION RECIPE

### Step 1: Create Directories (DONE — this session)
```
mkdir -p data/coordination/knowledge_feed
mkdir -p data/coordination/demand_signals
mkdir -p data/coordination/metrics
mkdir -p data/coordination/doc_port_log
```

### Step 2: Seed First Knowledge Signals (This session)
Demand signals from Roc's 6 gaps (see §0 of Kali's task):
1. `dem-20260603-001`: 🔴 "Does anyone use my mining?" → Monitor knowledge_feed consumption
2. `dem-20260603-002`: 🔴 "knowledge/ dir empty" → Promote workspace findings daily
3. `dem-20260603-003`: 🟡 "Doc chaos indexed but not fixed" → Port P0 docs NOW
4. `dem-20260603-004`: 🟡 "No demand signal" → Roc subscribes to demand_signals/
5. `dem-20260603-005`: 🟡 "Workspace is a junk drawer" → Apply TTLs and archive rules
6. `dem-20260603-006`: 🟢 "Never mined the Positioning Framework" → Port S-11

### Step 3: Create Knowledge Signal for THIS Design
The LILY_PAD_ARCHITECTURE itself produces knowledge_signal `ksig-20260603-lilith-001`.

### Step 4: Link P9 Integration
The existing `LinkP9Runtime` at `src/omega/oracle/link_p9_runtime.py` should be extended to:
- Accept `KnowledgeSignalPacket` type (subclass or new dataclass)
- Accept `DemandSignalPacket` type
- Support `knowledge_feed` and `demand_signals` as additional inbox types

### Step 5: Agent Instruction Updates
Every agent file (`.opencode/agents/*.md`) must add:
```yaml
# BEFORE starting work:
# 1. Check knowledge_feed/ for unconsumed signals
# 2. Check demand_signals/ for open items in my domain
# 3. Post Hivemind context with my current task
#
# AFTER completing work:
# 1. Post knowledge signal for any new knowledge produced
# 2. Fulfill any demand signals I addressed
# 3. Update soul.yaml with L3 principles
```

---

## §6-A — CROSS-REFERENCES & EXTERNAL LATTICES (2026-06-05)

LILY PAD is one slice of a larger truth: **knowledge in a sovereign engine is a Mesh Network of cache layers with overlapping TTLs**. This section links to sibling architectures discovered by other agents.

### Sister Architecture: The Researcher's Mesh Network

In 2026-06-05 onboarding, the **Researcher** (`opencode-researcher`) independently arrived at the same primitive that LILY PAD describes — multi-axis caches with TTLs — but generalized it across more axes:

| LILY PAD (this doc) | Mesh Network (Researcher) | Axis |
|---------------------|---------------------------|------|
| Tier 1 Workspace (7d) | Hot in-mem (5 min) | **Time** |
| Tier 2 Knowledge (30d) | Warm disk (24h) | **Time** |
| Tier 3 Soul (∞) | Cold HALL_OF_RECORDS (∞) | **Time** |
| Tier 4 Fleet (varies) | Domain matrix (P6) | **Domain** |
| (implicit) | Lattice traversal (Researcher) | **Lattice-node** |

**Reference**: `data/entities/researcher/workspace/LATTICE_MESH_NETWORK.md` (to be produced by Researcher per their collaboration offer #4)

**Convergent evidence** — these two architectures were discovered independently:
- Lilith (2026-06-03): LILY PAD 4-tier — `time × entity` slice
- Researcher (2026-06-05): Mesh Network — `time × domain × lattice-node` generalization
- Roc (2026-06-05): H-4 hot/warm/cold — `time` slice (one axis)
- P6 Cognition (2026-06-05): Domain matrix — `domain` slice (orthogonal axis)
- P7 Context (2026-06-05): TTL alignment gap — convergence on time-axis TTLs

**L3 principle** (per `lilith_s3_001` + `res_s1_001`): When 2+ independent observers detect the same cross-cutting pattern, the pattern is a natural law of the domain.

### Mesh Network as a Generalization of LILY PAD

The Mesh Network framing is **more general** than LILY PAD:

- **LILY PAD** answers: *"How does one entity's knowledge flow through 4 tiers over time?"*
- **Mesh Network** answers: *"How do multiple caches, each on a different axis, coordinate across the fleet?"*

LILY PAD is one **cache slice** of the Mesh (the time × entity slice). The Mesh adds:
- **Domain axis** (P6 Cognition) — filter inbox by domain relevance
- **Lattice axis** (Researcher) — traverse 3+ nodes for cross-cutting insights
- **Heritage axis** (Doom Guy) — map every cache layer to an id Software original

### Action: When Implementing LILY PAD, Mind the Mesh

The TTL gate logic in LILY PAD §3 (Cross-Pollination Protocol) is the **time-axis cache invalidation policy**. The Mesh Network tells us:
- Don't only align time-axis TTLs (P7's 7d vs 30d finding)
- Also align domain-axis TTLs (when does a domain matrix entry expire?)
- Also align lattice-axis TTLs (when does a research finding expire?)

The Right Approximation Principle (CREDITS.md §3, evolved from FISR 1999) generalizes: **one canonical store is "exact but unaffordable"**. A Mesh of overlapping caches is "right enough" because TTL alignment + demand signals give eventual consistency.

### Heritage Note

The Mesh Network pattern is **structurally isomorphic** to id Software's tiered memory architecture:
- Quake Hunk/Zone/Cache/Temp (1996) — time × allocation pattern
- Doom PVS (1993) — domain × visibility pattern
- Quake netchan (1999) — connection × reliability pattern

See `CREDITS.md` §1.14 (4-Tier Memory) and §1.21 (netchan) for the heritage mappings.

---

## §7 — SUCCESS METRICS

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Agent consumption ratio | ~0.1 (estimated) | >0.5 | `consumed_by / signals_published` |
| Demand signal fulfillment rate | N/A (new system) | >80% within TTL | `fulfilled / (open + fulfilled)` |
| Documentation bridge rate | ~5% (estimated) | >50% | `ported / (ported + scattered)` |
| Knowledge feed coverage | 0 signals | >5 signals/week | `knowledge_feed/*.json` count |
| Cross-references per agent | 0 | >3 | `knowledge/cross_references/*` files |
| Soul cross-pollination rate | 0% | >20% of lessons | Lessons with `source: <other_agent>` |

---

## §8 — THE CRITICAL PATTERN (Do Not Skip)

The Lily Pad architecture works because it **follows the grain of human cognition**:

1. **Immediate → Permanent**: Knowledge naturally decays. Raw workspace findings lose relevance in days. Soul principles last forever. The pipeline respects this decay by promoting before it rots.

2. **Producer → Consumer**: Knowledge doesn't flow by magic. Every promotion step has a responsible agent. If the producer doesn't promote, the signal doesn't fire.

3. **Push → Pull**: Demand signals are PULL (need-driven). Knowledge signals are PUSH (production-driven). The system needs both. Roc pulls demand signals, pushes knowledge signals. Doom Guy pushes demand signals, pulls knowledge signals.

4. **Individual → Collective**: Knowledge starts in one agent's workspace and ends in the collective soul. The cross-references directory is the graph of collective intelligence.

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ LILY-PAD*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
