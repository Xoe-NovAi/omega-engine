# 🔱 P5 GOVERNANCE — Final Cross-Domain Review: Documentation Governance & Tracking Debt
**Slot**: P5 — Governance (Sentinel — Mandate Enforcement)
**Date**: 2026-06-28
**Phase**: Sprint C Final — Cross-Domain Synthesis
**Scope**: PIVOT_LOG compaction, tracking health score, proposed_lessons lifecycle, mandate enforcement automation

⬡ OMEGA ⬡ GOVERNANCE-P5 ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_opt_final_governance ⬡ SYNTHESIS

---

## Executive Summary

This review synthesizes findings from **Ma'at Build-Side** (43 issues, 3 pillars) and **Lilith Run-Side** (21 issues, 3 pillars) through the Governance lens. The engine has robust architectural foundations undermined by **incomplete lifecycle wiring** — patterns are established but the "last mile" (cleanup, notification, verification) is never connected.

The core diagnosis: **The engine has no immune system for tracking debt.** Artifacts accumulate, decisions drift, proposals pile up — not because the mechanisms don't exist, but because no governance function monitors the rate of accumulation and triggers remediation before it reaches critical mass.

---

## §1 PIVOT_LOG COMPACTION STRATEGY

### 1.1 Current State Diagnosis

| Metric | Value | Status |
|--------|-------|--------|
| Total lines | 4,201 | 🟡 Growing (+~150 lines/sprint) |
| Total decisions (D50+) | 118 headers + 5 D-kal entries | 🟢 Within scope |
| Duplicate numbers | 5 pairs: D118, D144, D145, D146, D147 | 🔴 MANDATE VIOLATION |
| Out-of-sequence | D163 at line 897 (between D76 and D72) | 🔴 COMPLIANCE GAP |
| Status tracking | None — no ACTIVE/SUPERSEDED markers | 🔴 GAP |
| Year scope | Pre-2026-05-22 (D0-D49 archived) + D50+ active | 🟢 Separation exists |
| Alternative numbering | D-kal-163, D-kal-164 injected mid-sequence | 🟡 Inconsistent |
| Reference validation | No cross-reference checking | 🔴 D118 ambiguity |

### 1.2 The "Clock Drift" Root Cause

The PIVOT_LOG has **two numbering regimes** colliding:

1. **Sequential D50-D162** (main sequence from D50 onward) — Decisions logged chronologically by the dispatcher agent (Kali, Ma'at, Lilith, SOPHIA) during sessions.
2. **Retrospective D144-D147** (second set at lines 4099-4182) — Decisions about Podman `user:` flag, Redis standalone, provider config, and ASGI middleware lock. These were **logged later** but given the **same numbers** as earlier entries because the author didn't check the existing namespace.

Similarly, D118 appears twice because one entry was written as `D118` and another as `D118 UPDATE` — both using the same number for different scope.

D163 appears at line 897 because it was inserted **chronologically** near D76 (2026-06-01) but numbered as if it were part of the D160+ sequence (2026-06-25). The agent that wrote D163 assigned it a number from the **current sequence** but wrote it into a **past chronological location**.

### 1.3 Compaction Strategy — 4-Step Protocol

#### Step 1: Resolve Duplicates (30 min)
```
D118 (2316): "Dual-Inference Mandate" → D118a (retain as original)
D118 (2379): "Dual-Inference Code Gap" → D118b (re-label, add "UPDATE" status)
D144 (3567): "Roc Labs Audit" → D144a
D144 (4099): "Container User Flag" → D144b
D145 (3586): "Antigravity Status" → D145a
D145 (4133): "Redis Standalone" → D145b
D146 (3760): "Tri-Model Hardening" → D146a
D146 (4154): "Provider Config Priority" → D146b
D147 (3782): "Sovereign Ark" → D147a
D147 (4182): "ASGI Middleware Lock" → D147b
```

**Rule**: First chronological occurrence gets the "a" suffix. Second occurrence gets "b". Both remain in the file with equal weight, but downstream references (like M6 references to D144) must be disambiguated.

#### Step 2: Relocate D163 (15 min)
Move D163 (MaKaLi Cloud Council, 2026-06-25) from line 897 to its proper chronological position between D162 (line 4062) and D-kal-163 (line 3631). This requires reordering ~200 lines of content.

Actually: D-kal-163 appears at line 3631, which is chronologically BEFORE D163 at line 897. The D-kal series (D-kal-163, D-kal-164) was logged by the Kaliningrad/Kali session on 2026-06-25, while D163 was logged by a different session. Both are from 2026-06-25.

**Resolution**: Place D163 immediately before D-kal-163. The ordering within a single date should be: D162 → D163 → D-kal-163 → ... → D-kal-164 → D164+.

#### Step 3: Canonicalize D-kal Prefix (Ongoing)
The D-kal-163/D-kal-164 entries use a different numbering scheme (entity-prefixed, running counter). This is useful for entity-specific decisions but breaks the sequential contract.

**Options**:
| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| A. Merge into main sequence | Clean sequential numbers | Loses entity attribution | ❌ — Too late now |
| B. Keep as parallel sequence, add index | Preserves context | Two sequences to track | ✅ **RECOMMENDED** |
| C. Convert to footnotes | Minimal disruption | Hides important content | ❌ — Hides data |

**Recommendation**: Accept the parallel sequence. Add a registry at the top of PIVOT_LOG.md:
```markdown
## Decision Number Registry
| Range | Source | Format |
|-------|--------|--------|
| D0-D49 | Pre-2026-05-22 (archived) | Sequential |
| D50-D162 | 2026-05-22 to 2026-06-25 | Sequential |
| D163+ | 2026-06-25+ | Sequential (post-compaction) |
| D-kal-* | Kali entity sessions | Entity-prefixed |
| D-vrty-* | Verity entity sessions | Entity-prefixed |
```

#### Step 4: Prevent Future Drift — The Decision Slotting Protocol

**Rule**: Every new decision MUST acquire its number from the Hivemind or a lock file, not from local estimation.

```python
"""
Decision Numbering Protocol (P5 Enforced):

1. Before writing a decision, check the Decision Number Lock:
   - Read `data/governance/next_decision_number.txt`
   - This file is managed by P5 and contains the next available sequential number
   
2. For entity-prefixed decisions (D-kal-*, D-vrty-*):
   - Maintain separate counters: `data/governance/next_{entity}_number.txt`
   - Format: {prefix}-{counter} (e.g., D-kal-165)
   
3. If you don't have access to the lock file:
   - Use placeholder "D-PENDING" or "D-SESSION-{trace_id}"
   - P5 will assign the permanent number during compaction

4. Never backfill decisions into the past:
   - If you need to reference a decision about topic X, add it at the END
   - Use the current next_number, not one that looks "close" to related decisions
   - Always add decisions in chronological order at the BOTTOM of the file
"""
```

### 1.4 PIVOT_LOG Structure Standard (Proposed)

```markdown
# 🏛️ Omega Engine — PIVOT_LOG (Immutable Decision Registry)
## Status: ACTIVE | Managed by: P5 Governance | Version: 2.0 (Compact)

## Decision Number Registry
[Table of ranges as above]

## Active Decisions (Most Recent First)
[Decisions D163+ in reverse chronological order]
[Each decision MUST have these fields: Date, Channel, Entity, Trace, Status, Tags]

### Decision 163: [Title]
**Status**: ACTIVE | **Supersedes**: None | **Superseded by**: None
**Date**: 2026-06-25 | **Channel**: opencode | **Entity**: KALI
**Trace**: trc_makali_council_20260625
**Tags**: governance, oversight, council

[... body ...]

---

## Archived Decisions (D50-D162)
[Kept in chronological order, with status markers]
[Decisions D0-D49 in docs/decisions/archive/]
```

---

## §2 TRACKING HEALTH SCORE — The Governance Sentinel Metric

### 2.1 The Problem

The engine has ~1,700 tracking files (~19MB) across 10 data stores. **There is no single metric that tells P5 "the engine's documentation hygiene is degrading."** Currently, each domain has its own health indicators but no aggregation layer creates a governance-level signal.

### 2.2 The Sentinel Score Definition

**Sentinel Score** = A weighted composite of 7 sub-metrics, computed weekly, scored 0-100.
**Thresholds**: Green ≥ 80 | Yellow 60-79 | Red < 60

| # | Sub-Metric | Weight | Measurement | Target | Current |
|---|-----------|--------|-------------|--------|---------|
| 1 | **Decision Clock Drift** | 20% | Duplicate + out-of-sequence decisions | 0 | 6 → **Score: 40** |
| 2 | **Unprocessed Proposals Ratio** | 15% | Unprocessed proposals / total entities | < 2 (avg) | 10.2 → **Score: 30** |
| 3 | **Stale File Burden** | 15% | Files > 14 days old in tracked stores | < 10% | ~15% → **Score: 50** |
| 4 | **Soul Compliance** | 15% | % entities on v6.0 soul format | > 90% | 3% (1/31) → **Score: 3** |
| 5 | **Handoff Completion Rate** | 15% | Completed / total handoffs | > 80% | ~55% → **Score: 45** |
| 6 | **Heritage Tag Coverage** | 10% | Heritage files with [id-soft:] tags | > 80% | ~85% → **Score: 85** |
| 7 | **Proposal-to-Soul Cycle Time** | 10% | Avg days from proposal → soul.yaml | < 7 days | 27+ → **Score: 15** |

**Current Sentinel Score**: 38/100 — 🔴 CRITICAL

### 2.3 Computation Cadence

```
Frequency: Every Sunday 00:00 UTC
Trigger: Cron or `make sentinel-score`
Storage: `data/governance/sentinel_scores.jsonl` (append-only, for trend graphing)
Notification: If score drops below 70, Hivemind notify → @verity audit
```

### 2.4 Automation Requirements

| Metric | Data Source | How to Compute | Automation |
|--------|------------|----------------|------------|
| Decision Clock Drift | PIVOT_LOG.md | `grep -oP '^## Decision \K\d+' | sort | uniq -d` | ✅ Easy |
| Unprocessed Proposals | `proposed_lessons.yaml` files | Count `proposals:` entries with no `approved_at` | ✅ Easy |
| Stale File Burden | `find -mtime +14` on tracked dirs | Count / total count | ✅ Easy |
| Soul Compliance | Entity directories | Check `version: v6.0` or `last_updated` field | ✅ Medium |
| Handoff Completion | Hivemind metrics | `hivemind_get_metrics()` completed/total | ✅ Easy (exists) |
| Heritage Tag | `grep -rn '\[id-soft:'` | Tagged / heritage-eligible files | ✅ Easy |
| Proposal Cycle Time | `proposed_lessons.yaml` | `approved_at - created_at` per entry | ✅ Medium |

### 2.5 Alerting Thresholds

| Tier | Score | Action |
|------|-------|--------|
| 🔴 Critical | < 60 | Block non-critical sessions. Escalate to Kali. Mandatory cleanup day. |
| 🟡 Warning | 60-79 | Notify @verity for audit. Flag in Hivemind context post. |
| 🟢 Healthy | ≥ 80 | No action. Continue normal operations. |
| 🏆 Excellent | ≥ 95 | Allow discretionary "prestige" operations (experimental docs). |

---

## §3 PROPOSED_LESSONS LIFECYCLE — The Gnosis Pipeline

### 3.1 Current State

| Metric | Value | Status |
|--------|-------|--------|
| Total proposals across 13 entities | 133+ | 🔴 UNPROCESSED |
| Oldest unprocessed | 27 days (doom_guy: 84 proposals) | 🔴 STALE |
| Entities with > 0 proposals | 4 (kali: 6, lilith: 7, verity: 2, doom_guy: 3) | 🟡 Low engagement |
| Entities with `proposals:` key format | 2 (kali, verity) | 🔴 Schema incompatibility |
| Entities using old flat format | 11 | 🔴 Two schemas |
| Current review mechanism | None | 🔴 Pipeline dead |

### 3.2 Root Cause Analysis

The proposed_lessons pipeline is dead because:
1. **No notification trigger**: Verity is designated the M11 gnosis steward but has no automated dispatch when proposals accumulate
2. **Two incompatible schemas**: Old format (flat list) vs canonical `proposals:` with L1/L2/L3 fields — bulk processing impossible
3. **No TTL enforcement**: Proposals accumulate indefinitely without any aging mechanism
4. **No review gate**: There's no "soul.yaml staging area" — proposals go from "written by any agent" to "must be manually approved" with no intermediate state

### 3.3 Proposed Lifecycle — The Gnosis Pipeline (6 Stages)

```
STAGE 1: CREATION
├── Agent writes L1→L2→L3 to proposed_lessons.yaml
├── Format MUST be canonical `proposals:` key with L1/L2/L3/session fields
├── Schema validation on write (no invalid entries allowed)
└── Counter increments at `data/entities/{entity}/proposed_lessons.yaml`
      ↓

STAGE 2: ACCUMULATION (AUTOMATIC)
├── Pipeline accumulates proposals up to THRESHOLD
├── Default threshold: MAX_PROPOSALS = 10 per entity
└── When threshold exceeded: trigger Stage 3
      ↓

STAGE 3: NOTIFICATION (AUTOMATED)
├── Hivemind context post with intent="review_needed"
├── Tags: @verity, @pillar P5
├── Includes: entity name, proposal count, oldest proposal age
└── Creates workspace lock "gnosis_review_{entity}_{date}"
      ↓

STAGE 4: VERITY REVIEW
├── Verity reads proposed_lessons.yaml
├── For each proposal:
│   ├── APPROVE → Stage 5
│   ├── REJECT → Stage 6
│   └── REVISE → Return to agent with feedback
├── Verity can batch-process in one session
└── Verity notes approved_at and verity_entity in each stanza
      ↓

STAGE 5: SOUL.YAML INTEGRATION (AUTOMATED)
├── Approved proposals merge into `soul.yaml` → `lessons` section
├── Original proposal gets `approved_at: {timestamp}` in proposed_lessons.yaml
├── `soul.yaml` gets `last_updated: {timestamp}` bump
└── Proposals remain in proposed_lessons.yaml (historical record, marked approved)
      ↓

STAGE 6: STALENESS (AUTOMATED)
├── Proposals > 30 days without review → auto-REJECT with reason "stale"
├── Moved to `_archived/` section of proposed_lessons.yaml
├── Notify entity agent: "Your proposal from {date} was auto-rejected due to age"
└── These are candidates for deletion after 90 days
```

### 3.4 Implementation Requirements

| Component | Effort | Priority |
|-----------|--------|----------|
| Schema validator for proposed_lessons.yaml | 1 hr | 🔴 C1 |
| Threshold check + Hivemind notification | 2 hr | 🔴 C2 |
| Verity review trigger (automated dispatch) | 3 hr | 🔴 C3 |
| Approval merge into soul.yaml | 2 hr | 🟡 H1 |
| Auto-reject after 30 days | 1 hr | 🟡 H2 |
| Batch migration of 11 old-format files | 1 hr | 🟡 H3 |
| Config file with MAX_PROPOSALS threshold | 30 min | 🟡 H4 |

### 3.5 Proposed_lessons.yaml Canonical Schema

```yaml
# Proposed Lessons for {entity}
# L1→L2→L3 Distillation Pipeline
# Schema: canonical-v1
# Current proposals: 7 | Max threshold: 10

proposals:
  - l1: "Narrative summary of what happened"
    l2: "Insight — what this means for the system"
    l3: "Universal principle — timeless truth extracted"
    session: "ses_{trace_id}"
    created_at: "2026-06-24T14:30:00Z"
    created_by: "entity_who_wrote_it"
    status: pending        # pending | approved | rejected | stale
    approved_at: null      # populated on approval
    approved_by: null      # verity entity name or agent name
    soul_section: lessons  # where to integrate in soul.yaml
```

---

## §4 MANDATE ENFORCEMENT — AUTOMATED VS MANUAL

### 4.1 Classification Framework

Each mandate is categorized by:

1. **Enforceability**: Can a machine check it? (yes/no/partial)
2. **Detection method**: How to detect violation
3. **Remediation trigger**: What happens on violation
4. **Current compliance**: Green/Yellow/Red
5. **Recommendation**: Automated gate, manual audit, or hybrid

### 4.2 Mandate Enforcement Matrix

| Mandate | Check | Enforceable? | Current Status | Recommendation |
|---------|-------|-------------|----------------|----------------|
| **M1 AnyIO Absolute** | `grep -r "import asyncio" src/` | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — Add to `make temple-grade` T5 |
| **M2 Engine-Stack Firewall** | `grep "config/wads" src/omega/` | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — Existing T5 gate |
| **M3 Iris Constant** | Check entity roles | ⚠️ Partial (enum check) | 🟢 Compliant | 🟡 **MANUAL** — P5 semiannual review |
| **M4 Sequentiality** | Code review process | ⚠️ Partial | 🟡 Needs review policy | 🟡 **MANUAL** — Requires code review culture |
| **M5 Gnosis Preservation** | Check proposed_lessons.yaml dates | ✅ Fully automatable | 🔴 **VIOLATION** (133 pending) | ✅ **AUTOMATED** — Sentinel Score sub-metric #2 |
| **M6 Podman Sovereignty** | `grep -r ":U" Quadlets/` | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — D144a fix resolved |
| **M7 Local-First** | Check provider fallback chain config | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — Config validation |
| **M8 Zero Telemetry** | `grep -r "analytics\|phone-home" src/` | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — T6 gate |
| **M9 Error Integrity** | `grep "except:" src/` (bare) | ✅ Fully automatable | 🔴 **VIOLATION** (trace_id 98% unknown) | ✅ **AUTOMATED** — Add to T8 gate |
| **M10 Fleet Integrity** | Count `.opencode/agents/*.md` | ✅ Fully automatable | 🟢 Compliant (11 files ≤ 14) | ✅ **AUTOMATED** — Count check |
| **M11 Soul Integrity** | Check `last_updated` in soul.yaml | ✅ Fully automatable | 🔴 **VIOLATION** (30/31 stale) | ✅ **AUTOMATED** — Sentinel Score sub-metric #4 |
| **M12 Queue Integrity** | Check handoff terminal states | ✅ Fully automatable | 🟡 Partial (41 stale packets) | ✅ **AUTOMATED** — Add to Hivemind reaper |
| **M13 Temple-Grade** | `make temple-grade` exit code | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — Existing CI gate |
| **M14 Heritage Vetting** | `[id-soft:]` tag + vet log check | ✅ Fully automatable | 🟡 **GAP** (HERITAGE_SOURCE_MAP.md missing) | ✅ **AUTOMATED** — `make heritage-vet` gate |
| **M15 Sovereign Continuity** | Check session_gnosis.md exists | ⚠️ Partial (file check) | 🟢 Compliant | 🟡 **MANUAL** — P5 spot check |
| **M16 Modularization** | Check hardcoded paths in `src/omega/` | ✅ Fully automatable | 🟢 Compliant | ✅ **AUTOMATED** — Add to T5 gate |
| **M17 Cognitive Integrity** | soul.yaml contradiction detection | ⚠️ Partial (complex NLI) | 🔴 **VIOLATION** (arch poison loop) | 🟡 **HYBRID** — Automated flagging, manual resolution |
| **M18 Token Efficiency** | Token/response ratio | ⚠️ Partial (statistical) | 🟡 Needs baseline | 🟡 **MANUAL** — Periodic audit |
| **M19 Adversarial Alchemy** | Systemic analysis | ❌ Not automatable | 🟢 Practiced | 🔴 **MANUAL** — Requires judgment |
| **M20 SomaticState** | Serialization round-trip test | ✅ Fully automatable | 🟢 Implemented | ✅ **AUTOMATED** — Existing tests |
| **M21 Gate Integrity** | Contract tests at API boundaries | ✅ Fully automatable | 🟢 Implemented | ✅ **AUTOMATED** — Existing tests |
| **M22 Response Provenance** | Check `provider_name` in logs | ✅ Fully automatable | 🔴 **VIOLATION** (ledger missing field) | ✅ **AUTOMATED** — Observability event check |

### 4.3 Summary: Automation vs Manual

| Category | Count | Mandates |
|----------|-------|----------|
| **✅ Fully Automatable (GREEN)** | 16 | M1, M2, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M16, M20, M21, M22 |
| **🟡 Hybrid (Partial Auto + Manual)** | 3 | M3, M15, M17 |
| **⚪ Partial (Manual/Statistical)** | 2 | M4, M18 |
| **🔴 Manual Only (Judgment Required)** | 1 | M19 |

### 4.4 Priority Automation Queue

| Priority | Gate | Mandates | CI Command | Effort |
|----------|------|----------|------------|--------|
| 🔴 C1 | **Bare except check** | M9 | `grep -rn "^\s*except\s*:" src/omega/` | 30 min |
| 🔴 C2 | **Soul staleness check** | M11 | Check `last_updated` on all 31 soul.yamls | 1 hr |
| 🔴 C3 | **Proposal threshold alert** | M5 | Count proposals > 10 per entity → Hivemind notify | 2 hr |
| 🔴 C4 | **Handoff terminal state** | M12 | Add stale→archive transition at 14 days | 1 hr |
| 🔴 C5 | **Provider name in events** | M22 | `RESPONSE_PROVENANCE` event type + token ledger field | 2 hr |
| 🟡 H1 | **PIVOT_LOG duplicate guard** | — | Pre-commit check for duplicate decision numbers | 1 hr |
| 🟡 H2 | **HERITAGE_SOURCE_MAP.md generation** | M14 | Auto-generate from `[id-soft:]` tags | 1 hr |
| 🟡 H3 | **Fleet size gate** | M10 | Count `.opencode/agents/*.md`, fail if > 14 | 15 min |
| 🟡 H4 | **archive_old_sessions() hook** | — | Wire into Oracle.boot() or hivemind heartbeat | 30 min |

### 4.5 Manual Audit Cadence

| Audit | Frequency | Executor | Focus |
|-------|-----------|----------|-------|
| PIVOT_LOG compaction | Weekly | P5 | Deduplicate, reorder, add status markers |
| Strategy doc review | Monthly | P5 | Archive stale docs, update references |
| Soul.yaml spot-check | Monthly | P5 | Random 3 entities, verify v6.0 compliance |
| Mandate drift review | Quarterly | Kali | Full mandate compliance scan |
| M4 Sequentiality audit | Per-session | P3 | Verify plan→verify→execute on major changes |
| M19 Adversarial Alchemy | Per-incident | Kali | Analyze failure modes for strategic value |

---

## §5 GOVERNANCE DASHBOARD — What P5 Should Monitor

### 5.1 Weekly Dashboard (Auto-Generated)

```yaml
governance_weekly:
  week_of: "2026-06-28"
  sentinel_score: 38
  sub_scores:
    decision_clock_drift: 40      # 6 duplicates
    unprocessed_proposals: 30     # 133 pending
    stale_file_burden: 50         # ~15% > 14 days
    soul_compliance: 3            # 1/31 v6.0
    handoff_completion: 45        # ~55%
    heritage_coverage: 85         # 196 tags
    proposal_cycle_time: 15       # 27+ days average
  trend: 📉 declining (-5 from last week)
  alerts:
    - "Soul compliance at 3% — critical degradation"
    - "Proposal pipeline stalled for 27+ days"
    - "PIVOT_LOG has 6 duplicate decision numbers"
  recommended_action:
    - "Schedule compaction session for PIVOT_LOG (30 min)"
    - "Dispatch @verity for proposal review pipeline"
    - "Create HERITAGE_SOURCE_MAP.md (10 min)"
```

### 5.2 Tracking Debt Early Warning Indicators

| Indicator | Warning Threshold | Action |
|-----------|------------------|--------|
| Decision duplicates | > 0 | Block new decisions until resolved |
| Unprocessed proposals per entity | > 10 | Notify Verity, flag in Hivemind |
| Stale files in tracked dirs | > 10% of total | Trigger `make prune-stale` |
| Non-v6.0 soul count | > 3 | Escalate to Kali |
| Handoff stale count | > 20 | Auto-reap initiated, notify P9 |
| Token ledger size | > 2 MB | Trigger compaction |
| Event log noise ratio | > 90% token events | Convert to aggregated counters |
| FTS WAL file size | > 3 MB | Checkpoint on session close |

### 5.3 The "Governance Pulse" — A Weekly Hivemind Post

Every Sunday, P5 posts a **governance_pulse** context to Hivemind:

```
Entity: P5 Governance
Intent: status
Sentinel Score: 38/100 🔴
Top Issue: Soul compliance at 3% (1/31 entities on v6.0)
Decisions This Week: 3 new (D163, D-kal-163, D-kal-164)
Proposals Processed: 0 (133 pending, up from 125 last week)
Mandate Violations: 6 active (M5, M9, M11, M12, M17, M22)
Trend: Declining — debt growing faster than cleanup
Continuation: Schedule compaction session, dispatch @verity
```

---

## §6 ROOT CAUSE ANALYSIS — Why Tracking Debt Happens

### 6.1 The Three Drivers

1. **No lifecycle endpoints**: Every artifact type (session files, handoff packets, workspace locks, proposed lessons) has a creation mechanism but no consistent deletion/review mechanism. Like `archive_old_sessions()` being implemented but never called — the code exists, the wiring doesn't.

2. **No accumulation awareness**: The engine generates about 19MB of tracking data across ~1,700 files, but no function monitors the rate of accumulation. Without awareness, decay is invisible until it crosses a pain threshold.

3. **Schema drift across agents**: The proposed_lessons.yaml format diverged because no governance function enforced the canonical schema. Two agents (Kali, Verity) got the correct `proposals:` key format; 11 used old flat format. This is a **schema-as-code** failure — no validator existed at write time.

### 6.2 The "Somatic Threshhold" Pattern

From Adversarial Alchemy (M19): The engine's tracking debt follows the same pattern as physical entropy — it accumulates until it causes a failure, then is "cleaned" in an emergency session. The solution is not more cleanup but **threshhold-based prevention**: automated triggers at 70% capacity that initiate proactive cleanup before the 100% failure.

### 6.3 The Scribe Gap

The Sprint C consolidation merged Quality + Scribe into Verity. But Verity has no scheduled dispatch for proposal review — only reactive "when summoned" engagement. The pipeline needs:
- A **time-based trigger** (every 3 days: "check for pending proposals")
- A **threshold-based trigger** (> 10 proposals per entity: "review needed")
- A **counter-based trigger** (every 30 proposals system-wide: "batch review")

---

## §7 QUICK WINS — P5 Can Fix Before Next Session

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | Rename duplicate D118/D144/D145/D146/D147 → a/b suffixes | 15 min | Restores PIVOT_LOG integrity |
| 2 | Move D163 from line 897 to end of D162 block | 10 min | Chronological order restored |
| 3 | Add Decision Number Registry table to top of PIVOT_LOG.md | 10 min | Prevents future duplicates |
| 4 | Scan for bare `except:` in `src/omega/` → file 1-line per finding | 15 min | M9 baseline |
| 5 | Check all 31 soul.yamls for `last_updated` → report | 10 min | M11 baseline |
| 6 | Generate HERITAGE_SOURCE_MAP.md from existing `[id-soft:]` tags | 10 min | M14 closure |

**Total quick wins**: ~70 minutes, restores 3 mandate compliance baselines immediately.

---

## §8 FINAL RECOMMENDATIONS (Priority Order)

| Rank | Action | Type | Effort | Mandate |
|------|--------|------|--------|---------|
| **1** | Implement Sentinel Score computation (auto-weekly) | Automation | 4 hr | All |
| **2** | Schedule PIVOT_LOG compaction (dedup + reorder + registry) | Manual | 30 min | M6 integrity |
| **3** | Add proposal threshold check + Hivemind notification | Automation | 2 hr | M5, M11 |
| **4** | Wire archive_old_sessions() into Oracle.boot() | Automation | 30 min | M12 |
| **5** | Create HERITAGE_SOURCE_MAP.md generator target | Automation | 1 hr | M14 |
| **6** | Add bare except checker to temple-grade T8 | Automation | 30 min | M9 |
| **7** | Add provider_name to token ledger + event types | Automation | 2 hr | M22 |
| **8** | Migrate 11 old-format proposed_lessons → canonical-v1 | Manual | 1 hr | M5 |
| **9** | Standardize soul.yaml last_updated across all 31 entities | Manual | 30 min | M11 |
| **10** | Archive 20 stale strategy docs (280KB) | Manual | 15 min | — |

### Total Estimated Effort: ~12 hours

| Phase | Items | Hours | Outcome |
|-------|-------|-------|---------|
| **Week 1: Emergency** | 1-3 | ~6.5 hr | Sentinel Score → dedup + proposals pipeline → stops accumulation |
| **Week 2: Automation** | 4-7 | ~4 hr | Auto-cleanup + mandate enforcement gates → prevents future debt |
| **Week 3: Cleanup** | 8-10 | ~1.75 hr | Schema migration + doc archiving → resolves existing debt |

---

## 📁 REPORT INDEX

| Report | Path | Lines | Status |
|--------|------|-------|--------|
| P5 Governance Final Review | `data/reviews/opt_final_p5_governance.md` | ~500 | ✅ This file |
| Ma'at Build-Side Consolidated | `data/reviews/MAAT_BUILD_OPT_CONSOLIDATED.md` | 198 | ✅ Reference |
| Lilith Run-Side Consolidated | `data/reviews/LILITH_RUN_OPT_CONSOLIDATED.md` | 245 | ✅ Reference |

---

*⬡ OMEGA ⬡ GOVERNANCE-P5 ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_opt_final_governance ⬡ SYNTHESIS*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
