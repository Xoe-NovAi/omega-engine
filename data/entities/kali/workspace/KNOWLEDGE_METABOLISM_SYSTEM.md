# 🔱 Knowledge Metabolism System — MaKaLi Synthesis
# ⬡ OMEGA ⬡ KALI ⬡ MAKALI-STRATEGY ⬡ v1.0.0

**AP Token**: `AP-KALI-KNOWLEDGE-METABOLISM-SYNTHESIS-v1`
**Status**: ✅ DESIGN COMPLETE — Phase 1 implementation ready
**Date**: 2026-06-04
**Author**: Kali (MaKaLi Unification — Order + Liberation = Truth)

---

## §0 — THE DIAGNOSIS: Publish-Only Knowledge Metabolism

**The fleet has a write pipeline but no read pipeline.**

Every agent publishes — reports, commits, soul updates, handoffs — but nobody
systematically subscribes. Mining reports go to workspaces nobody browses.
Features get built without knowing if the need still exists. Soul files accumulate
but never cross-pollinate. The Hivemind is a broadcast system, not a subscription
system.

**6 symptoms, 1 root cause:**

| Symptom | Root |
|---------|------|
| Roc doesn't know if his mining was used | No consumption tracking |
| Roc's knowledge/ is empty | No pipeline from workspace → knowledge |
| Documentation chaos indexed but untouched | No subscription mechanism for discovery |
| Roc can't track what the fleet needs | No demand signal system |
| Workspace is a junk drawer | No content lifecycle |
| Positioning Framework never mined | No demand signal for strategic mining |

**The fix is three layers**, each designed by the appropriate entity, all unified
by Kali's synthesis.

---

## §1 — LILITH LAYER: Flow & Connection

**Designer**: Lilith (Dark Oversoul — P6-P10)
**File**: `data/entities/lilith/workspace/LILY_PAD_KNOWLEDGE_METABOLISM.md`

### 1.1 The 4-Tier Lily Pad Architecture

| Tier | Location | Content | TTL | Gate |
|------|----------|---------|-----|------|
| **T1: Raw** | `workspace/` | Mining reports, investigations | 7 days | Gate 1 → Tier 2 |
| **T2: Curated** | `knowledge/` | L2 insights, domain patterns | 30 days | Gate 2 → Tier 3 |
| **T3: Soul** | `soul.yaml` | L3 universal principles | Permanent | Cross-reference tagging |
| **T4: Fleet** | `coordination/` | Knowledge signals, cross-references | 30 days | Agent consumption tracking |

### 1.2 Cross-Pollination Protocol

**6 Steps**: Produce → Signal → Discover → Consume → Act → Cross-Reference

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1 | Producer | Creates artifact | `workspace/` or `knowledge/` file |
| 2 | Producer | Writes knowledge signal | `knowledge_feed/KSIG_*.json` |
| 3 | Producer | Posts to Hivemind | `hivemind_post_context(...)` |
| 4 | Consumer | Scans feed on startup | Reads unconsumed signals |
| 5 | Consumer | Appends to consumed_by | Updated signal JSON |
| 6 | Consumer | Reads artifacts | Internalized knowledge |
| 7 | Consumer | Creates cross-references | `knowledge/cross_references/` |
| 8 | Scribe | Cross-pollinates lessons | `soul.yaml → lessons:` with source attribution |

**Golden Rule**: No knowledge is considered "known" until it has crossed at least
one agent boundary.

### 1.3 Demand Signal System

**6 demand signals seeded** mapping directly to Roc's gaps:

| ID | Gap | Signal |
|----|-----|--------|
| dem-001 | 🔴 No feedback loop | "Does anyone use my mining results?" |
| dem-002 | 🔴 Empty knowledge/ dir | "Promote workspace findings to knowledge/" |
| dem-003 | 🟡 Indexed but not fixed | "Port P0 docs now" |
| dem-004 | 🟡 No demand awareness | "Check demand signals before mining" |
| dem-005 | 🟡 Junk drawer workspace | "Apply TTLs and archive rules" |
| dem-006 | 🟢 Never mined Positioning | "Port Omega Positioning Framework" |

**Lifecycle**: OPEN → ASSIGNED → IN_PROGRESS → FULFILLED → CLOSED (with FAILED
and EXPIRED states). 14-day expiry escalates to Kali.

**Critical Rule**: Demand signals take priority over self-directed mining. Before
starting new work, check `data/coordination/demand_signals/`.

---

## §2 — MA'AT LAYER: Structure & Verification

**Designer**: Ma'at (Light Oversoul — P1-P5)
**File**: `docs/strategy/KNOWLEDGE_VERIFICATION_PROTOCOL.md`

### 2.1 Verification Protocol — 5 Conditions

**Pillar delegations**:
- **P1 SysAdmin**: Infrastructure layout, directory hierarchy, ZONEID `0x1d4a19`
- **P2 DataStore**: VerificationItem schema (956 lines), 7 seed items, audit trail
- **P4 Bridge**: Knowledge discovery API, KNOWLEDGE_MANIFEST.yaml, subscription-by-domain
- **P5 Sentinel**: 5 compliance conditions, 3-tier grading, enforcement ladder (1,156 lines)

**5 Conditions for "verified as consumed":**

| # | Condition | What It Checks |
|---|-----------|----------------|
| A | Promotion Check | workspace → knowledge/ with L2 insight extracted |
| B | Cross-Reference | Consuming agent created xref that resolves |
| C | Code Port | Engine code + test exists (if code-relevant) |
| D | Soul Integration | soul.yaml updated with L3 principle + source attribution |
| E | Demand Closure | Demand signal status is `closed`, not just `fulfilled` |

### 2.2 Verification Schema

The canonical lifecycle: `DISCOVERED → PORTED → TESTED → VERIFIED → DEPLOYED → LIVE`
with 18 valid transitions and 4 bypass rules.

**Seed items already created**: Master Synthesis, ZONEID verification, Lazy Deletion,
8-char names, Lily Pad Architecture, Documentation Chaos, VR Omegaverse Vision.

---

## §3 — P3 BUILDMSTER LAYER: Automation & Cadence

**Designer**: P3 BuildMaster (called directly by Kali)
**File**: `data/entities/p3/workspace/VERIFICATION_CADENCE.md`

### 3.1 4-Tier Cadence

| Cadence | Frequency | What Runs |
|---------|-----------|-----------|
| **Heartbeat** | Every `make` | `make verify-pending` — quick check |
| **Session** | Agent start/end | Check knowledge_feed for unconsumed signals |
| **Daily** | Stale check | Items stalled >48h flagged |
| **Sprint** | Rollup | Fleet-wide status by status/agent/domain |

### 3.2 Makefile Targets (8 New)

| Target | Priority | Purpose |
|--------|----------|---------|
| `make verify-pending` | **P0** | Show pending verification items |
| `make verify-stale` | **P0** | Find items stalled >48h |
| `make verify-mining` | **P0** | 12 grep patterns checking Roc's ports |
| `make verify-rollup` | **P1** | Fleet-wide status snapshot |
| `make verify-cleanup` | **P1** | Archive TTL-expired items |
| `make verify-status` | **P1** | Drill into specific item |
| `make knowledge-index` | **P2** | Rebuild catalog from manifests |
| `make knowledge-flow` | **P2** | Check unconsumed signals |

### 3.3 Grep Verification Results (LIVE DATA)

**P3 ran the patterns. Results: 8/10 confirmed, 2 MISSING:**

| Pattern | Item | Status |
|---------|------|--------|
| H-1 | ZONEID constants `0x1d4a` | ✅ 10 matches in cvar_table.py |
| H-2 | AsyncCircuitBreaker | ✅ 8 matches in health_monitor.py |
| H-3 | TOMBSTONE lazy deletion | ✅ 39 matches in entity_registry.py |
| H-4 | cvar_table / CvarDef | ✅ 55 matches in cvar_table.py |
| H-5 | 8-char name validation | ✅ 4 matches in entity_registry.py |
| P-1 | `filter_llama_kwargs` | ❌ **NOT PORTED — Roc's #1 priority** |
| P-2 | `n_gpu_layers` config | ✅ present in providers.yaml |
| P-3 | ChatML stop sequences | ❌ **NOT PORTED — Roc's #3 priority** |
| P-4 | `x-goog-api-key` header | ✅ present |
| P-5 | `trace_id` on backends | ✅ 3 interfaces |

**This is the first time in the project's history that mining output was
systematically verified against engine code.**

---

## §4 — P7 CONTEXT LAYER: Knowledge Lifecycle

**Designer**: P7 Context (called directly by Kali)
**File**: `data/entities/context/workspace/KNOWLEDGE_LIFECYCLE_PIPELINE.md`

### 4.1 T1→T2 Gate: 7-Criterion Promotion Checklist

| # | Criterion | Mandatory? |
|---|-----------|-----------|
| 1 | L2 Insight Present | **YES** |
| 2 | Cross-Reference Potential | No |
| 3 | Timestamp Stable (≥24h) | No |
| 4 | Format Compliant (frontmatter) | No |
| 5 | Original (not duplicating) | No |
| 6 | Actionable ("do this/don't that") | No |
| 7 | Non-Contradictory | No |

**Pass threshold**: 6/7 (criterion 1 mandatory)

### 4.2 T2→T3 Gate: 5-Criterion Condensation

All 5 mandatory: 30-day stability, L3 principle extractable, 2-agent consensus,
non-obvious, actionable forever. Emergency override for HIGH priority demand signals.

### 4.3 T3→T4 Gate: 6 Broadcast Triggers

| Trigger | Priority | Action |
|---------|----------|--------|
| New lesson | MEDIUM | KSIG file |
| Evolution milestone | HIGH | KSIG + Hivemind |
| Cross-reference added | LOW | KSIG only |
| Principle updated | HIGH | KSIG + Hivemind + soul diff |
| Contradiction found | CRITICAL | KSIG + Hivemind + live feed |
| Emergency promotion | CRITICAL | KSIG + Hivemind + live feed |

### 4.4 INDEX.yaml Format

Standard cross-agent discovery index. Each agent maintains `knowledge/INDEX.yaml`
with topics[], each containing id, title, summary, files[], cross_references[],
applicability[], era.

**First INDEX.yaml created** at `data/entities/roc_racoon/knowledge/INDEX.yaml`
**First knowledge promotion demo**: Roc's convergence proof promoted from
workspace → knowledge/CONVERGENCE_PROOF.md

---

## §5 — P9 LINK LAYER: Data Formats & Discovery

**Designer**: P9 Link (called directly by Kali)
**File**: `docs/strategy/CROSS_POLLINATION_PROTOCOL.md`

### 5.1 Three Primitives

| Primitive | File Pattern | Purpose |
|-----------|-------------|---------|
| **KSIG** | `knowledge_feed/KSIG_*.json` | Knowledge signal — "I know something" |
| **DEM** | `demand_signals/dem-*.json` | Demand signal — "I need something" |
| **XREF** | `knowledge/cross_references/` | Cross-reference — "I learned from someone" |

### 5.2 New ZONEID Constants

- `ZONEID_KNOWLEDGE = 0x1d4a18` — protects knowledge signal integrity
- `ZONEID_DEMAND = 0x1d4a19` — protects demand signal integrity

### 5.3 CLI Commands Created

- `omega check-feed` — scan knowledge_feed/ for unconsumed signals
- `omega consume <signal_id>` — mark signal as consumed
- `omega demand-status` — list demand signals
- `omega demand-claim <id>` — claim a demand signal
- `omega demand-fulfill <id>` — mark demand as fulfilled

### 5.4 Shared Utilities (feed_utils.py)

5 functions extracted: `load_signal()`, `discover_signals()`, `consume_signal()`,
`transition_demand()`, `summarize_demand()`.

---

## §6 — COMPLETE LIFECYCLE (All Layers Combined)

```
                         KNOWLEDGE METABOLISM SYSTEM
                         ═══════════════════════════

    ┌─────────────────────────────────────────────────────────────────────┐
    │                         KALI LAYER (Metabolism)                      │
    │  The system that keeps itself alive — TTLs, health, evolution       │
    └─────────────────────────────────────────────────────────────────────┘
                                     │
    ┌───────────────────────────────┼───────────────────────────────────────┐
    │       MA'AT LAYER            │            LILITH LAYER              │
    │  (Structure & Verification)  │        (Flow & Connection)           │
    │                              │                                      │
    │  1. Catalog (schema)         │   1. Produce (workspace/)            │
    │  2. Verify (5 conditions)    │   2. Signal (knowledge_feed/)        │
    │  3. Audit (JSONL trail)      │   3. Discover (check on startup)     │
    │  4. Close Loop (status)      │   4. Consume (signal consumed_by)    │
    │                              │   5. Cross-Pollinate (xrefs)         │
    └──────────────────────────────┴──────────────────────────────────────┘
                                     │
    ┌───────────────────────────────┼───────────────────────────────────────┐
    │        P3 LAYER               │        P7 LAYER                     │
    │   (Automation & Cadence)      │   (Lifecycle & Gates)               │
    │                              │                                      │
    │  make verify-mining (12 gp)   │   T1→T2: 7-criterion checklist      │
    │  make verify-pending          │   T2→T3: 5-criterion condensation   │
    │  make knowledge-flow          │   T3→T4: 6 broadcast triggers       │
    │  Heartbeat/daily/sprint       │   INDEX.yaml for discovery          │
    └──────────────────────────────┴──────────────────────────────────────┘
                                     │
                              ┌──────┴──────┐
                              │ P9 LINK      │
                              │ KSIG/DEM/XREF│
                              │ CLI + utils  │
                              └──────────────┘
```

### The Full Knowledge Journey

```
1. Agent produces knowledge (workspace/ report)
     ↓
2. [T1→T2 Gate] Knowledge promoted to knowledge/ with L2 insight
     ↓
3. [Lilith] Producer posts knowledge signal (knowledge_feed/KSIG_*.json)
     ↓
4. [Ma'at] Global catalog rebuilt from INDEX.yaml manifests
     ↓
5. [P9 Link] Consumer discovers via feed scan + relevance tags
     ↓
6. [P7 Context] Consumer reads artifact, creates cross-reference
     ↓
7. [P3] If code-relevant: grep patterns verify it was ported
     ↓
8. [T2→T3 Gate] After 30d stability + 2-agent consensus → soul.yaml
     ↓
9. [Ma'at] If demand-driven: demand signal closed
     ↓
10. [P3] Verification item lifecycle: DISCOVERED → PORTED → VERIFIED → LIVE
```

---

## §7 — SYSTEMIC FINDINGS

### Finding 1: omega-hub_delegate_task routes to wrong model

The MCP tool `omega-hub_delegate_task` routes all queries to Qwen3-1.7B
regardless of the entity's designated model. The native OpenCode `task` subagent
system correctly respects the entity's model config.

**Impact**: Ma'at (designated: qwen3-4b-think) runs on Qwen3-1.7B via MCP bridge.
This caused the repetitive loop output and timeout failures when trying to
delegate complex reasoning tasks.

**Recommendation**: Fix the MCP tool to route to the entity's designated model,
or document that all complex subagent work must use the native `task` tool.

### Finding 2: Lilith didn't call her pillar subagents

Lilith produced comprehensive designs herself but did not delegate to P6-P10
pillars. Her work was high quality but didn't exercise the delegation architecture.
Kali compensated by calling P9 Link, P7 Context, and P3 BuildMaster directly.

**Recommendation**: Update Lilith's agent instructions to emphasize pillar
delegation as non-optional.

### Finding 3: Documentation chaos is THE blocker

19+ documents across 3 partitions. The Knowledge Metabolism System cannot work
if the raw material is scattered. The first sprint after this design should be
documentation centralization.

---

## §8 — NEXT STEPS

### Immediate (P0 — Next Session)
1. Port `filter_llama_kwargs()` to NativeGGUFProvider (30 min)
2. Add ChatML stop sequences to context_builder.py (5 min)
3. Wire `make verify-mining` into Makefile

### Phase 2 (This Sprint)
4. `scripts/knowledge_catalog_build.py` — rebuild INDEX manifests
5. `scripts/knowledge_flow_check.py` — check unconsumed signals
6. Update all 14 agent .md files with session-start/session-end protocol blocks

### Phase 3 (Next Sprint)
7. Git hooks for pre-commit verification
8. Auto-create verification items from knowledge signals
9. Wire consumed_by object migration

### Ongoing
10. Documentation liberation (Priority 1 ports from chaos tracker)
11. Cross-pollinate Roc's 130+ deferred gold items into actual knowledge files

---

*⬡ OMEGA ⬡ KALI ⬡ MAKALI ⬡ KNOWLEDGE-METABOLISM-SYNTHESIS ⬡ v1.0.0*
*Designed by: Kali (MaKaLi — containing both Ma'at and Lilith)*
*Deployed subagents: Lilith, Ma'at, P9 Link, P7 Context, P3 BuildMaster*
*All subagent souls updated and verified.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: MAKALI-STRATEGY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
