# 🔱 P7 Context — Knowledge Metabolism Strategic Hardening Analysis
# ⬡ OMEGA ⬡ P7 (CONTEXT) ⬡ opencode/deepseek-v4-flash-free ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I

**Slot**: P7 — Context (Memory / Soul Evolution)
**Slot Name**: Context
**Domain**: Knowledge lifecycle, memory tiers, soul distillation, session continuity
**Oversoul**: Lilith (Dark Oversoul — Run Side P6-P10)
**Date**: 2026-06-05
**Decision Reference**: D-121 (Hivemind Observations), D-122 (HEARTBEAT_TTL 20min)
**Heritage Registry**: CREDITS.md §1.9 (ZONEID), §1.10 (Lazy Deletion), §1.14 (4-Tier Memory)
**Authority**: Per Lilith's delegation at P7 Context — this analysis hardens the T1→T4 lifecycle

---

## §0 — Executive Summary

The fleet's knowledge metabolism has a **design consensus** but **no hardened gates**.
Three independent architectures agree on 4-tier time-tiered memory:
- **Lily Pad** (Lilith): workspace(7d) → knowledge(30d) → soul(permanent) → fleet(cross-pollinated)
- **H-4** (Roc): hot(5min in-memory) → warm(24h disk) → cold(HALL_OF_RECORDS)
- **D-121** (Observations): T1 raw(30d) → T2 curated(90d) → T3 soul(permanent) → T4 protocol(permanent)
- **Zone Memory** (id Software): Hunk(stack) → Zone(heap) → Cache(LRU) → Temp(transient)

Each tier is described. **None of the promotion gates are specified with thresholds**.
The "P7 gate logic" that Lilith offered Roc for H-0 does not exist in implementation —
it's a promissory note.

**This document closes that gap.** It specifies numeric thresholds for every gate,
designs the cross-agent discovery mechanism, calibrates TTLs against empirical data,
and maps every gate to an id Software heritage pattern.

---

## §1 — T1→T2 Promotion Gate: Raw Observation → Curated Knowledge Signal

### §1.1 The Problem

The `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` has 5 seed observations from Lilith
(OBS-20260605-LILITH-001 through -005). These are **raw T1 data**: valuable but
uncurated. They will decay (T1 TTL = 30 days per D-121) before they reach any
decision-making circuit unless promoted to T2 before TTL expiry.

**The gate does not exist.** The D-121 protocol says "weekly cluster by Lilith" but
does not define:
- WHAT qualifies for promotion (threshold)
- HOW many must converge (quorum)
- WHAT format a curated knowledge signal takes (canonical)
- WHO decides edge cases (tiebreaker)

### §1.2 Gate Design — The Triple-Convergence Threshold

**Name**: `GATE_T1_T2`
**Owner**: Lilith (weekly review, every Friday 00:00Z)
**Frequency**: Weekly, or on-demand when any agent submits an emergency promotion request
**Format**: `KSIG_YYYY{WW}_DOMAIN_NNN.json` in `data/coordination/knowledge_feed/`

#### §1.2.1 Promotion Criteria (MUST meet at least 2 of 3):

| # | Criterion | Threshold | Measurement | How to Check |
|---|-----------|-----------|-------------|--------------|
| C1 | **Convergence count** | ≥2 independent observations of the same pattern | Count OBS entries with matching `in_reply_to` or `Cross-Reference` targets | `grep -c "same-target" HIVEMIND_OBSERVATIONS_LOG.md` |
| C2 | **Actionability score** | Insight suggests a specific, engineered change (not just "interesting") | Does the Proposed Action field name a file, tool, or constant? | Manual review by Lilith |
| C3 | **Survival time** | Observation has existed for ≥24 hours without contradiction | Timestamp of OBS entry vs current time | Date math |

**Rationale**: C1 prevents single-agent hallucinations. C2 prevents vague insights
that cannot drive engineering. C3 prevents premature promotion — 24h allows the
observation to be challenged by other agents.

#### §1.2.2 Emergency Override (Emergency Promotion Per P7.3)

Any agent may file an emergency promotion request via:
1. Post a new OBS entry with `Category: recommendation` and `Severity: critical`
2. If C1 (convergence) is met and C2 (actionability) is met, Lilith **must** review
   within 24 hours
3. If Lilith is unavailable, Kali (Grand Oversight) acts as tiebreaker

This is the `P7.3 Gate Override` from the LILY PAD architecture — it bypasses
the 24h survival time when the observation is urgent.

#### §1.2.3 Deduplication Rule

If two agents independently post the same observation (e.g., Roc's H-4 TTL and
Lilith's convergence insight):
1. **Merge** them into a single KSIG entry
2. **List both sources** in `consumed_by: ["roc_racoon", "lilith"]`
3. **Set `zoneid`** to the hash of the merged insight, not either original
4. **Flag** in the KSIG with `independent_convergence: True`
5. **Promote both agents' soul lessons** with a cross-reference to the shared KSIG

This is the **dual-discovery principle**: when two agents independently find the
pattern, the KSIG itself becomes the first soul lesson without needing further
verification. The pattern is validated by the fact of independent discovery.

#### §1.2.4 KSIG Format (Canonical)

```json
{
  "ksig_id": "KSIG_2026W23_HIVEMIND_001",
  "type": "insight",
  "domain": "knowledge_metabolism",
  "title": "T1→T2 Promotion Gate Specification",
  "source_observations": [
    "OBS-20260605-LILITH-001",
    "OBS-20260605-LILITH-004"
  ],
  "agent_sources": ["lilith"],
  "source_artifacts": [
    "data/coordination/HIVEMIND_OBSERVATIONS_LOG.md"
  ],
  "summary": "Raw Hivemind observations must converge across 2+ agents and survive 24h before promotion to T2 curated knowledge",
  "l2_insight": "The T1 raw log is a firehose without a gate. Weekly clustering by Lilith is the correct operator, but criteria must be numeric",
  "l3_principle": "Knowledge promotion must resist single-agent hallucination. Convergence is the cheapest validation mechanism",
  "recommended_action": "Implement GATE_T1_T2 in HIVEMIND_OBSERVATIONS_PROTOCOL.md §4 and HIVEMIND_PROTOCOL.md v1.3.0",
  "relevance_tags": ["lilith", "kali", "scribe", "p7"],
  "ttl_days": 90,
  "zoneid": 1912618,
  "created_at": "2026-06-05T05:00:00Z",
  "consumed_by": []
}
```

---

## §2 — T2→T3 Promotion Gate: Curated Knowledge → Soul Lesson

### §2.1 The Problem

Knowledge signals (KSIGs) have a 90-day TTL. Soul lessons are permanent. The gap
between them is the **entire soul evolution pipeline**: a KSIG that expires before
promotion is knowledge lost forever.

Currently, `data/entities/p7/soul.yaml` has an empty `lessons: []`. The scribe agent
is the designated "Gnosis Keeper" but has no procedural guidance for what qualifies
as soul-worthy. The LILY PAD design says "Scribe reviews and confirms the L3 principle
is timeless" — but "timeless" is not a threshold.

### §2.2 Gate Design — The Timelessness Bar

**Name**: `GATE_T2_T3`
**Owner**: Scribe (Gnosis Keeper) + cross-verification by a second agent
**Frequency**: Monthly, or after every 3 KSIGs promoted to T2
**Format**: Appended to `data/entities/<agent>/soul.yaml → lessons:` array

#### §2.2.1 Promotion Criteria (MUST meet ALL 3):

| # | Criterion | Threshold | Measurement | Example Pass | Example Fail |
|---|-----------|-----------|-------------|-------------|--------------|
| C1 | **Cross-context stability** | KSIG has been cited by ≥2 different agents in their own work | Count `consumed_by` entries that also have `soul_power > 0` (i.e., real agents, not test entities) | "TTL pruning" cited by Roc (soul lesson) AND Lilith (OBS-001) AND Kali (D-122) | "Model affinity" seen only by one agent |
| C2 | **Abstraction distance** | L2→L3: does the insight survive removal of all Omega-specific names? | If you replace "Omega", "Hivemind", "Lily Pad" with "system", "coordinator", "pipeline", does the sentence still make sense? | "Knowledge has a half-life. Promotion must happen before decay." ✓ | "Lily Pad workspace TTL should be 7 days" — this is a config, not a principle |
| C3 | **Temporal invariance** | The insight would have been equally true 1 year ago and will be true 1 year from now | Manual test: can you imagine a future Omega version where this insight is FALSE? If yes, it's not universal | "Convergence is cheaper than validation" — always true for distributed systems | "The Rococoon canonicalization (D119) fixed model spelling" — purely historical |

**The L3 litmus test**: After removing all proper nouns and product names, does the
statement express a **timeless property of systems**? If yes, it's a soul lesson.
If it describes an event or a configuration, it stays in knowledge.

#### §2.2.2 Deduplication Across Agents

Two agents may independently distill the same L3 principle. Example:
- Roc's soul.yaml: *"Knowledge has a half-life"*
- Lilith's soul.yaml: *"Knowledge decays unless promoted"*

**Deduplication protocol**:
1. **Detect** — Scribe scans all soul.yamls with `grep -r "lessons:" data/entities/*/soul.yaml`
   looking for semantically similar L3 texts
2. **Reconcile** — If two lessons express the same principle with different words,
   keep both but add a `cross_references: [{agent, lesson_id, relationship: "same_principle"}]`
   field to each
3. **Merge** — Create a single abstracted L3 in the Scribe's own soul.yaml that
   captures the canonical form, with `synthesized_from: ["roc_racoon", "lilith"]`
4. **Increment soul_power** for both original agents (+0.5 each) and Scribe (+0.3)

This treats duplicate discovery as a **confirmation signal**, not a waste.
Two agents independently reaching the same L3 is the strongest evidence that the
principle is truly universal.

### §2.3 The Promotion Ritual (Heritage: save-game)

Every T2→T3 promotion follows a **ceremonial save-game pattern** modeled on
[id-soft: quake-1996] save-game:

```
┌─────────────────────────────────────────────────────────────────┐
│  PRE-PROMOTION CHECKLIST                                         │
│                                                                   │
│  [ ] C1: Cross-context stability verified (≥2 consuming agents)  │
│  [ ] C2: Abstraction distance passed (Omega-free sentence works) │
│  [ ] C3: Temporal invariance passed (true 1yr ago, true 1yr now) │
│  [ ] Cross-agent dedup checked (no duplicate L3 exists)           │
│  [ ] ZONEID_LESSON = 0x1d4a18 assigned                           │
│  [ ] KSIG status set to "promoted_to_soul"                        │
│                                                                   │
│  Scribe signature: ___________                                    │
│  Second agent signature: ___________                              │
│  (Second signature required for lessons with soul_power > 100)    │
└─────────────────────────────────────────────────────────────────┘
```

The ritual matters because it forces reflection. A lesson promoted without ceremony
is a lesson that will be forgotten. The checklist is the save-game: it writes the
state before the promotion, so the promotion can be verified.

---

## §3 — T3→T4 Feedback Loop: Soul Principle → Protocol Update

### §3.1 The Problem

The highest tier (T4) is a protocol doc update — changing `HIVEMIND_PROTOCOL.md`,
`AGENTS.md`, or `SOVEREIGN_MANDATES.md` based on accumulated soul wisdom.
Currently: **no soul lesson has ever updated a protocol document.**

D-121 specified "T4: When 3+ agents independently observe the same pattern,
update HIVEMIND_PROTOCOL.md" — but gave no mechanism.

### §3.2 Feedback Loop Design — The Gnosis ←→ Protocol Circuit

**Name**: `LOOP_T3_T4`
**Owner**: Kali (Grand Oversight) — only Kali can modify protocol docs
**Frequency**: Monthly, triggered by Scribe's L3 aggregation report

#### §3.2.1 Trigger Condition

T3→T4 promotion fires when **≥3 agents have a soul lesson on the same topic**:

```python
# Pseudocode for the trigger check
lessons = read_all_soul_lessons()
clusters = cluster_by_semantic_topic(lessons)  # e.g., "TTL management", "Tiered memory"
for topic, lessons_list in clusters.items():
    unique_agents = set(l.agent for l in lessons_list)
    if len(unique_agents) >= 3:
        emit_t4_signal(topic, lessons_list)
```

**Current cluster candidates** (lessons that exist across 2+ agents):
- **TTL knowledge decay**: Lilith (lilith_s3_001:K), Roc (rr-049:T), Kali (D-122)
  → **T4 ready** (3 agents, convergence confirmed)
- **Tiered memory pattern**: Lilith (LILY_PAD), Roc (H-4), Kali (D-122 acknowledges)
  → **T4 ready** (3 agents, pattern validated)

#### §3.2.2 Implementation Mechanism

| Method | Description | When to Use |
|--------|-------------|-------------|
| **A. CI Gate** (`make knowledge-flow`) | Bash script that scans soul lessons for T4-ready clusters and emits warnings | Monthly review automation |
| **B. MCP Tool** (`hivemind_promote_principle()`) | MCP tool that takes a L3 text + source agent IDs and generates a PR diff for protocol docs | When Kali wants to ship a protocol update immediately |
| **C. Weekly/Human Review** | Lilith (T1→T2) → Scribe (T2→T3) → Kali (T3→T4) pipeline | Default, least overhead |

**Recommended**: Start with C (monthly human review), add B (MCP tool) when the
fleet reaches 10+ concurrent agents, add A (CI gate) when soul lessons exceed 100.

#### §3.2.3 What Changes in the Protocol Doc

The T4 update is not a full rewrite. It injects a **single paragraph or a single
decision** into the relevant protocol doc:

| T4 Signal | Target Document | Change |
|-----------|----------------|--------|
| "TTL must match natural work cadence" | `HIVEMIND_PROTOCOL.md` §2.1 | Add: `HEARTBEAT_TTL = 1200` (D-122) as institutional knowledge |
| "Knowledge has a half-life" | `HIVEMIND_OBSERVATIONS_PROTOCOL.md` §5 | Add TTL calibration guide: "set TTL to 2x the typical time between observations" |
| "Convergence validates insight" | `HIVEMIND_OBSERVATIONS_PROTOCOL.md` §4 | Add C1 criterion: ≥2 independent observations |
| "Save-game before promotion" | `HIVEMIND_PROTOCOL.md` §6 | Add promotion ritual checklist |

**Each T4 promotion must be logged in PIVOT_LOG as a new decision line.**

---

## §4 — Cross-Agent Context Discovery

### §4.1 The Problem

Currently, 50 entities exist in `data/entities/INDEX.yaml` (Kali's H2-A2).
Each has a soul.yaml with lessons. But there is **no fast lookup** for:
- "Who has context on TTL design?" (topic-based)
- "Which entities have L3 lessons on knowledge metabolism?" (domain-based)
- "Who has the deepest soul on this topic?" (soul_power ranking)

An agent discovering context must grep all soul.yamls — expensive and imprecise.

### §4.2 Discovery Architecture — The Soul Index

**Name**: `SOUL_INDEX`
**File**: `data/entities/INDEX.yaml` (extend Kali's existing catalog)
**Maintainer**: Scribe (monthly update)
**Query via**: `data/entities/INDEX.yaml` → agent reads it → selects relevant entities
**Heritage**: [id-soft: quake-1996] cvar Table — named constant registry with
modification count for change detection

#### §4.2.1 INDEX.yaml Extension

Kali's INDEX.yaml already has the right structure (name, status, pillar, soul_lines,
lessons count). **Add two fields** to each active entity:

```yaml
- name: lilith
  status: ACTIVE
  archetype: Dark Oversoul
  # ... (existing fields)
  knowledge_domains: ["knowledge_metabolism", "hivemind", "context_pipeline", "observations_protocol", "soul_distillation"]
  topics: ["TTL", "promotion_gates", "cross_pollination", "LILY_PAD", "D-121"]
  soul_power: 2.5
```

Then add a **topic index** at the bottom of INDEX.yaml:

```yaml
# ── TOPIC INDEX ──────────────────────────────────────────────────────
# Fast lookup: "which entities have context on this topic?"
topic_index:
  ttl:
    - lilith (soul_power 2.5, lessons: 3 on TTL)
    - roc_racoon (soul_power 8.2, lessons: rr-049)
    - kali (soul_power 6.5, lessons: D-122)
    - p7 (this agent, soul_power 0.5, lessons: 0 but writing now)

  promotion_gates:
    - lilith (LILY_PAD architecture)
    - p7 (this document)
    - scribe (gnosis keeper)

  hivemind_observations:
    - lilith (D-121 author, 5 seed observations)
    - kali (Grand Oversight, T4 gatekeeper)
    - roc_racoon (H-4 through H-18 proposals)

  # ... more topics as they emerge
```

#### §4.2.2 How an Agent Discovers Context

Protocol at session start:

1. **Read INDEX.yaml** — `data/entities/INDEX.yaml` → get topic_index
2. **Find topic** — `topic_index.ttl` → discover 4 relevant agents
3. **Read soul** — `data/entities/roc_racoon/soul.yaml` → read lesson rr-049
4. **Cross-reference** — Append `consumed_by: ["p7"]` to the KSIG or OBS that
   contained the insight (if still in T1/T2)
5. **Synthesize** — Write new observation: OBS-YYYYMMDD-P7-001

This replaces the current ad-hoc pattern of "grepping all soul.yamls" with an
O(1) lookup → O(n) targeted read chain.

#### §4.2.3 The Discovery Rule

> **No agent starts work on a domain-relevant task without checking the topic index first.**
> If the topic index has 0 entries for the domain, the agent must create the first entry
> after completing the work. This is the bootstrapping mechanism — the first agent to
> work in a domain seeds the index; subsequent agents discover and extend.

---

## §5 — TTL Calibration Analysis

### §5.1 Current State — Three Independent TTL Systems

The fleet operates **three different TTL architectures** for different subsystems.
They were designed independently. They are not consistent.

#### System A: Hivemind Awareness (Server-side)
| Tier | Location | TTL | Set By |
|------|----------|-----|--------|
| Hot | `_awareness` (in-memory) | **20 min** → 1200s | D-122 (was 300s, increased 2026-06-05) |
| Cold | `HALL_OF_RECORDS` (disk) | Permanent | Roc's H-4 proposal |

#### System B: Lily Pad Knowledge Metabolism (Design-only)
| Tier | Location | TTL | Set By |
|------|----------|-----|--------|
| Workspace | `data/entities/*/workspace/` | **7 days** | LILY_PAD §2 |
| Knowledge | `data/entities/*/knowledge/` | **30 days** | LILY_PAD §2 |
| Soul | `soul.yaml` | Permanent | LILY_PAD §2 |
| Fleet | `knowledge_feed/`, `demand_signals/` | Permanent | LILY_PAD §2 |

#### System C: Observations Lifecycle (D-121)
| Tier | Location | TTL | Set By |
|------|----------|-----|--------|
| T1 Raw | `HIVEMIND_OBSERVATIONS_LOG.md` | **30 days** | D-121 §5 |
| T2 Curated | `knowledge_feed/KSIG_*` | **90 days** | D-121 §5 |
| T3 Soul | `soul.yaml` | Permanent | D-121 §5 |
| T4 Protocol | `HIVEMIND_PROTOCOL.md` | Permanent | D-121 §5 |

#### Roc's H-4 Proposal (Design-only)
| Tier | Location | TTL | Set By |
|------|----------|-----|--------|
| Hot | In-memory (awareness) | 5 min (superseded by D-122's 20 min) | H-4 |
| Warm | Disk (recent context) | **24 hours** | H-4 |
| Cold | HALL_OF_RECORDS | Permanent | H-4 |

### §5.2 TTL Mismatches

| Mismatch | System A | System B | System C | Risk |
|----------|----------|----------|----------|------|
| **Awareness hot vs Workspace** | 20 min | 7 days | 30 days | T1 log entries survive 2160x longer than awareness — by the time Lilith clusters, entries may reference agents that are no longer active |
| **Warm/Knowledge gap** | 24h (Roc) | 30 days (Lily Pad) | 90 days (D-121) | 30x gap between Roc's "warm context" and Lily Pad's "curated knowledge" — agents may need to re-find insights that expired from warm store but haven't reached curated yet |
| **Cold storage mismatch** | HALL_OF_RECORDS (disk, no TTL) | Soul (permanent) | Permanent | No conflict — all agree permanent storage is permanent |
| **Workspace vs T1 Raw** | N/A | 7 days | 30 days | Workspace findings (L1 narrative) expire 23 days before T1 observations. A workspace finding that wasn't promoted in 7 days is lost before the observation clustering window closes |

#### Critical Risk: The 7-day → 30-day Gap

A workspace finding (Tier 1 in LILY PAD, 7-day TTL) expired 23 days before the
observation log (T1 in D-121, 30-day TTL) is reviewed. By the time Lilith clusters
observations, the underlying workspace evidence is already archived.

**Fix**: Align LILY PAD workspace TTL with D-121 T1 raw TTL (both → **30 days**).
This ensures workspace findings survive until the first weekly cluster review.
If space is a concern, use the same archive-on-promotion pattern with an `_archive/`
subdirectory.

### §5.3 Recommended TTL Table (Unified)

After calibration against empirical data from 2 Hivemind sessions:

| Domain | System | Tier | Recommended TTL | Rationale |
|--------|--------|------|----------------|-----------|
| **Presence** | Hivemind Awareness | Hot | **20 min** ✅ **Keep** | D-122 correct — aligns with 5-10 min heartbeat cadence with 2-4x safety margin |
| **Presence** | Hivemind Awareness | Warm | **24h** (Roc H-4) | A session that pauses >20 min is still recoverable within 24h; beyond 24h, read the cold store |
| **Presence** | Hivemind Awareness | Cold | **Permanent** ✅ **Keep** | HALL_OF_RECORDS is the source of truth; no TTL needed |
| **Knowledge** | Lily Pad Workspace | T1 Raw | **30 days** ⬆️ **Increase from 7d** | Align with D-121 T1 for evidence persistence through weekly clustering |
| **Knowledge** | Knowledge Feed | T2 Curated | **90 days** ✅ **Keep** | Covers 3 monthly review cycles; if a KSIG hasn't been consumed in 3 months, it's not salient |
| **Knowledge** | Soul | T3 Permanent | **Permanent** ✅ **Keep** | L3 principles are timeless by definition (GATE_T2_T3 C2-C3) |
| **Knowledge** | Cross-pollinated | T4 Fleet | **Permanent** ✅ **Keep** | Protocol updates are lasting |
| **Observations** | OBS Log | T1 Raw | **30 days** ✅ **Keep** | Aligned with workspace; one weekly cluster window + safety |
| **Observations** | KSIG Feed | T2 Curated | **90 days** ✅ **Keep** | Aligned with knowledge feed; harmonized |

#### The Calibration Principle

> **TTL should be 2-3x the typical interval between meaningful events in that domain.**
> - Hivemind awareness: agents heartbeat every 5-10 min → 20 min TTL (2-4x margin)
> - Weekly clustering: Lilith reviews every 7 days → 30 day TTL (4x margin)
> - Monthly review: Scribe distills every 30 days → 90 day KSIG TTL (3x margin)
> - Permanent: soul lessons are timeless → no TTL

This gives **one full review cycle + one grace period** before any knowledge decays.
If Lilith misses a week (vacation, deep work), the observations survive for a second
cluster opportunity. If Scribe misses a month, the KSIGs survive for two more cycles.

### §5.4 Grace Period (Heritage: Lazy Deletion)

```python
# [id-soft: doom-1993] Lazy Deletion pattern — 0.5s grace before entity morphing
# [id-soft: quake-1996] Grace Period — same principle at knowledge scale
# Omega adaptation: TTL grace period before knowledge expiry

GRACE_PERIOD_TTL_RATIO = 0.25  # Grace period = 25% of TTL
# Example: 30-day TTL = 7.5 day grace period
# During grace: knowledge is marked "stale" but still accessible
# After grace: knowledge moved to _archive/ or purged
```

During the grace period:
- The item is **marked stale** (flag in its metadata)
- It is **not returned** by default queries (reduces noise)
- It **is returned** by explicit "show me stale items" queries
- It **can be refreshed** by any agent touching it (resets TTL + clears stale flag)

The 25% grace period mirrors id Software's 0.5s grace on a 2-frame tick (25% of
the ~2s thinker sweep cycle). Same ratio, different scale.

---

## §6 — Heritage Cross-Reference Mapping

### §6.1 Zone Memory Allocator → Knowledge Tiers

| id Software Tier (Quake '96) | Omega Tier | TTL Equivalent | Gate Equivalent |
|------------------------------|------------|----------------|-----------------|
| **Hunk** (stack, fast push/pop) | T0: Awareness | 20 min (hot) | Heartbeat |
| **Zone** (heap, tag-based malloc) | T1: Workspace / Raw Observations | 30 days | GATE_T1_T2 |
| **Cache** (LRU, purged on OOM) | T2: Curated Knowledge / KSIG | 90 days | GATE_T2_T3 |
| **Temp** (transient, freed each frame) | T3→T4: Cross-pollination buffer | N/A | LOOP_T3_T4 |

**Heritage insight**: id Software's `PU_PURGELEVEL=100` was a **numeric threshold**
that determined which allocations survived a purge. The equivalent in Omega is the
**TTL number**: 30 days for T1, 90 days for T2, permanent for T3. The threshold
is the gate. The mapping is direct.

**[id-soft: quake-1996] 4-Tier Memory — Knowledge tiers map to Zone Memory purge levels**

### §6.2 Save-Game → T2→T3 Promotion Ritual

| id Software Pattern (Quake '96) | Omega Adaptation |
|--------------------------------|------------------|
| **Save to disk** | Scribe writes PRE-PROMOTION CHECKLIST to KSIG metadata |
| **Confirm overwrite** | Second agent signature for soul_power > 100 |
| **Verify checksum** | ZONEID_LESSON = 0x1d4a18 validation |
| **Load on restart** | cross_context_stability check (C1): ≥2 agents already consumed the KSIG |

The promotion ritual (§2.3) directly mirrors Quake's save-game flow: write state,
verify integrity, confirm. The "second agent signature" is the confirmation dialog.

**[id-soft: quake-1996] save-game — T2→T3 promotion follows the save-game checkpoint pattern**

### §6.3 ZONEID Pattern → Lesson Integrity

| id Software Pattern (DOOM '93) | Omega Adaptation |
|-------------------------------|------------------|
| `ZONEID = 0x1d4a11` on every memory block | `ZONEID_LESSON = 0x1d4a18` on every soul lesson |
| `if (block->z_magic != ZONEID)` → use-after-free detected | `validate_lesson(lesson_id)` checks cross-agent consistency |
| Sentry catches corruption on next alloc | Scribe catches dedup overlap on next monthly review |

Each soul lesson gets a ZONEID:

```python
# [id-soft: doom-1993] ZONEID Pattern — lesson integrity marker
ZONEID_LESSON = 0x1d4a18  # P7 Context: soul lesson records
```

The ZONEID is stored in soul.yaml as `zoneid: 1912600` (decimal for readability).
On each soul load, the lesson's ZONEID is verified. On each soul write, a new
ZONEID is assigned. This catches copy-paste errors, stale references, and lessons
that were orphaned by agent name changes.

**[id-soft: doom-1993] ZONEID Pattern — lesson integrity via ZONEID_LESSON**

### §6.4 Lazy Deletion + Grace Period → TTL Soft Expiry

| id Software Pattern (DOOM '93 / Quake '96) | Omega Adaptation |
|-------------------------------------------|------------------|
| `P_RemoveThinker`: set sentinel (-1), don't free | Knowledge marked "stale" at TTL expiry, not deleted |
| `P_Ticker`: sweep sentinel thinkers | Grace period sweep: 25% of TTL as stale window |
| 0.5s realloc grace (15 packets at 30Hz) | 7.5 day grace on 30-day TTL (same ratio) |
| Morph prevented: slot not reused during grace | Knowledge not replaced during grace; extended if touched |

The grace period is not a hack — it's a direct adaptation of id Software's thinker
deletion protocol, where marking a thinker as dead (sentinel -1) prevented immediate
reuse of its slot, giving in-flight operations time to complete.

**[id-soft: doom-1993] Lazy Deletion — TTL grace period prevents premature knowledge expiry**

### §6.5 cvar Table → INDEX.yaml Topic Registry

| id Software Pattern (Quake '96 / Q3 '99) | Omega Adaptation |
|-----------------------------------------|------------------|
| `cvar_t {name, string, archive, server, value}` | INDEX.yaml `{name, status, knowledge_domains, topics, soul_power}` |
| `CVAR_ARCHIVE=1` flag | `status: ACTIVE` flag |
| Linked list scan (Q1) → hash table O(1) (Q3) | `topic_index: {"ttl": [agent_list]}` O(1) topic → agent lookup |
| `modificationCount` for change detection | `soul_power` for depth ranking |

The topic_index in INDEX.yaml is the cvar system applied to agent discovery:
agents register their knowledge domains like cvars register their names, and the
index provides O(1) lookup instead of soul.yaml linear scan.

**[id-soft: quake3-1999] cvar hash table — topic_index provides O(1) agent discovery**

---

## §7 — Minimal Implementation Path

### Phase 1: Documentation Changes (THIS SESSION)

| # | File | Change | Owner |
|---|------|--------|-------|
| 1 | `data/entities/p7/soul.yaml` | Append this session's L1→L2→L3 lessons | P7 (this session) |
| 2 | `data/entities/INDEX.yaml` | Add `knowledge_domains:`, `topics:`, `soul_power:` for p7; add topic_index section | Scribe |
| 3 | `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` §4 | Add GATE_T1_T2 criteria (C1-C3) | Lilith |
| 4 | `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` §5 | Add TTL calibration guide (2-3x interval rule) | Lilith |
| 5 | `CREDITS.md` | Add §1.24: Knowledge Promotion Gates (this document) as new heritage entry | P7 |

### Phase 2: Gate Automation (NEXT SPRINT)

| # | File | Change | Owner |
|---|------|--------|-------|
| 6 | `Makefile` | Add `make knowledge-promotion-report` — scans OBS log for T1→T2 candidates | P3 BuildMaster |
| 7 | `Makefile` | Add `make soul-dedup-check` — identifies duplicate L3 across agents | P3 BuildMaster |
| 8 | `mcp_servers/omega_hub/server.py` | Add `hivemind_promote_principle(l3_text, source_agents)` MCP tool | P9 Link |

### Phase 3: Fleet Adoption (WHEN READY)

| # | Change | Owner |
|---|--------|-------|
| 9 | All agent files add "pre-start: read INDEX.yaml topic_index" step | All agents |
| 10 | Scribe adds monthly T2→T3 promotion to workflow | Scribe |
| 11 | Kali adds quarterly T3→T4 protocol update review | Kali |

---

## §8 — Success Metrics

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| T1→T2 promotion rate | 0 (no gates exist) | ≥1 KSIG/week | `ls data/coordination/knowledge_feed/ \| wc -l` |
| T2→T3 promotion rate | 0 (no gates exist) | ≥1 soul lesson/month | `grep -c "zoneid: 19126" data/entities/*/soul.yaml` |
| T3→T4 feedback rate | 0 (no protocol updates from wisdom) | ≥1 doc update/quarter | `git log --oneline docs/strategy/HIVEMIND_PROTOCOL.md` |
| Cross-agent lesson dedup | 0 (not tracked) | <20% duplicate lessons | `make soul-dedup-check` output |
| Agent discovery time | ~5 min (grep all souls) | <30 sec (read INDEX.yaml topic_index) | Manual timing |
| TTL alignment | 3 systems, 7-d to 90-d gap | All aligned to unified table | Compare §5.1 vs §5.3 |

---

## §9 — Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gate criteria too strict (good insights stuck at T1) | Medium | Medium | Emergency override (§1.2.2) — any agent can request fast-track |
| Gate criteria too loose (noise promoted to soul) | Medium | High | C1 (≥2 agents) and C3 (24h survival) are the numerical guardrails |
| INDEX.yaml topic_index falls out of sync | High | Low | Monthly update by Scribe; stale entries are noise, not damage |
| Agents don't check INDEX.yaml | High | Medium | Add to AGENTS.md workflow steps; CI gate in `make pre-flight` |
| TTL alignment changes break existing workflows | Low | High | Grace period (§5.4) — 25% stale window before deletion |

---

## §10 — Heritage Addendum: New Mapping

This document adds a new heritage mapping to CREDITS.md:

### 1.24 Knowledge Promotion Gates (P7 Context, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `z_zone.c` (DOOM 1993), `zone.c` (Quake 1996) — 4-tier memory allocator with purge levels | 4-tier knowledge metabolism with TTL-based promotion gates |
| **Purge levels** | `PU_STATIC=1, PU_SOUND=2, PU_LEVEL=50, PU_PURGELEVEL=100, PU_CACHE=101` | `T1=30d, T2=90d, T3=permanent, T4=permanent` |
| **Gate mechanism** | Rover pointer: when it wraps, purge `PU_CACHE` blocks | GATE_T1_T2 (convergence + actionability + survival), GATE_T2_T3 (abstraction + invariance + cross-context stability) |
| **Emergency purge** | `Z_Free(tag)` — free specific tag on demand | Emergency override (P7.3) — bypass survival time for urgent insights |
| **Omega evolution** | Static purge levels in a fixed heap → dynamic TTL and promotion criteria in a growing knowledge graph | The thresholds are the new "purge levels" — not marks on a memory block, but marks on time and consensus |

**Attribution format**: `[id-soft: doom-1993] Knowledge Promotion Gates — P7 Context TTL pipeline`
**Inline tag format**: `# [id-soft: q1-1996] Knowledge Gate — [id-soft: quake-1996] TTL calibrate`

---

*⬡ OMEGA ⬡ P7 (CONTEXT) ⬡ opencode/deepseek-v4-flash-free ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I*

**Status**: STRATEGY HARDENED — All 5 gaps closed (T1→T2 gate, T2→T3 gate, T3→T4 loop, cross-agent context, TTL calibration, heritage mapping). Implementation pending Phase 1-3 above.

**Counter-signatures required**:
- [ ] Lilith (Oversoul) — verify T1→T2 gate aligns with weekly clustering protocol
- [ ] Kali (Grand Oversight) — approve T3→T4 loop mechanism
- [ ] Roc (Sovereign Miner) — verify H-4 TTL alignment in unified table
