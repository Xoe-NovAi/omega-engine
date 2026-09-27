# 🔱 Heritage Vetting Pipeline — id Software → Omega Concept Gate
# ⬡ OMEGA ⬡ KALI ⬡ VETTING-GATE ⬡ v1.0.0 ⬡ 2026-06-04

## Mandate: Every Heritage Concept Must Be Vetted Before Implementation

The 8-character name cap was implemented, broke tests, and was removed — all
because no one asked **"Should we do this?"** before asking **"How do we do
this?"**

This pipeline prevents that. Every id Software concept must pass through a
structured vetting process before code is written.

---

## §1 The Heritage Vet Gate — Mandatory for All Heritage Implementations

**Effective immediately**: No id Software–derived pattern may be implemented
without first passing through this pipeline. The pipeline is enforced by the
`make heritage-vet` gate, which checks that every `[id-soft:]` tag in the
source code has a corresponding vet record.

---

## §2 The 4-Gate Pipeline

```
┌────────────────────────────────────────────────────────────┐
│                    1. DISCOVERY                             │
│  Pattern found in id Software source or documentation       │
│  → Write R-doc with analysis                                │
│  → Log in PENDING_CREDITS_QUEUE.md                          │
└─────────────┬──────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────┐
│                    2. VETTING & DEBATE                      │
│  Structured for/against analysis by designated vetter       │
│  → Python relevance check (does this optimization exist?)   │
│  → Risk assessment (what breaks if it's wrong?)             │
│  → Cross-reference with Roc's knowledge INDEX               │
│  → Vet record written to HERITAGE_VET_LOG.md                │
└─────────────┬──────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────┐
│                    3. DECISION                              │
│  One of four outcomes:                                      │
│  ✅ ADOPT → Implement with full attribution                 │
│  🔄 ADAPT → Modify for Python context, document changes    │
│  ⏸ DEFER  → Revisit later (logged with reason + trigger)  │
│  ❌ REJECT → Not suitable for Omega (logged with reason)   │
└─────────────┬──────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────┐
│                    4. IMPLEMENTATION & VERIFICATION         │
│  Code written only if ADOPT or ADAPT                        │
│  → [id-soft:] tags in source                               │
│  → Entry in CREDITS.md §1.x                                │
│  → Concept-level test: "Does this pattern benefit Omega?"  │
│  → Integration: Cross-reference in Roc's INDEX.yaml         │
└────────────────────────────────────────────────────────────┘
```

---

## §3 Gate 2: Vettings & Debate — The For/Against Analysis

Every concept MUST have a structured analysis addressing these questions:

### 3.1 Python Relevance

| Question | Purpose |
|----------|---------|
| **What problem did this solve in C?** | Understand the original constraint |
| **Does that problem exist in Python?** | If no → likely cargo-cult (like 8-char cap) |
| **If yes, how does Python solve it natively?** | e.g., dict lookups, garbage collection |
| **Does the id Software approach add value beyond Python's native solution?** | This is the threshold question |

### 3.2 Risk Assessment

| Risk | Evaluate |
|------|----------|
| **Performance risk** | Does this pattern actually optimize Python execution? Measure, don't assume. |
| **Complexity risk** | How much new code? How many files affected? |
| **Debt risk** | Will this need to be undone later? (8-char cap = 100% debt) |
| **UX risk** | Does this degrade the user experience? |
| **Compatibility risk** | Does this break existing entities, configs, or APIs? |

### 3.3 The "Right Approximation" Test

From FISR Principle (CREDITS.md §1.3): **"The right approximation for the
problem is better than the exact solution you can't afford."**

Ask:
1. What is the *actual precision requirement* of this use case?
2. What is the cost of the exact solution?
3. If the answer is "it's all in Python, the 'exact solution' is just a dict
   lookup", then the pattern has no job to do.

### 3.4 Cross-Reference with Roc Racoon

Before adopting, check Roc's INDEX.yaml and lesson repository:

- Has a similar pattern been attempted in a past era?
- If so, was it successful, abandoned, or rejected?
- Does the current engine already solve this problem differently?

Example: The circuit breaker pattern was independently invented 3× across eras.
Roc found all three and identified `pybreaker` as canonical. This saved us from
implementing a fourth variant.

---

## §4 Gate 3: Decision Matrix

| Score | Outcome | Action |
|-------|---------|--------|
| 9-10 | ✅ ADOPT | Full implementation, attribution, tests |
| 7-8 | 🔄 ADAPT | Modify for Python, document changes clearly |
| 4-6 | ⏸ DEFER | Log with reason, trigger condition for revisit |
| 1-3 | ❌ REJECT | Log with reason, move on |

### Scoring Criteria

| Factor | Points | How to Score |
|--------|--------|--------------|
| **Python relevance** | 0-3 | 0 = problem doesn't exist in Python, 3 = pattern gives real Python perf gain |
| **Risk level** | 0-3 | 0 = high risk (likely to break things), 3 = no risk (pure observation) |
| **Need vs want** | 0-2 | 0 = nice-to-have, 2 = current engine has measurable deficiency this fixes |
| **Historical evidence** | 0-2 | 0 = speculative, 2 = empirically verified across multiple eras |

**Minimum score for implementation: 7/10**

---

## §5 The Heritage Vet Log

Every concept that enters the pipeline gets a record appended to:
`data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`

Format:

```yaml
- id: vet-001
  concept: "8-Character Name Caps"
  source: "w_wad.c:170-178 (DOOM 1993)"
  discovery_date: 2026-06-02
  vet_date: 2026-06-04
  vet_by: "Kali (user-initiated review)"
  
  for_analysis: |
    - Allows 2 × int32 compare vs strcmp on WAD lump names
    - Consistent key format across the engine
  against_analysis: |
    - Python dicts are O(1) by hash — no performance benefit
    - Forces cryptic entity names (prometheus → prom)
    - Breaks existing entity names with meaningful long names
    - 386-specific optimization that doesn't translate
  
  python_relevance: 0/3  # Problem doesn't exist in Python
  risk_level: 0/3        # High risk — broke tests, degraded UX
  need_vs_want: 0/2      # Pure want, zero need
  historical_evidence: 1/2  # Known in legacy but never adopted there
  total_score: 1/10
  
  decision: "REJECTED"
  rationale: |
    Cargo-cult optimization. The 2-int compare trick is a 386-specific hack
    that does not accelerate Python code. Dict lookup is already O(1). The
    cap was implemented as commit 8b3fc17 and removed as commit 8b3fc17.
  
  implementation: null  # Never should have been implemented
  removal_commit: "8b3fc17"
  lesson_id: "Kali soul.yaml v5 — Cargo-Cult Optimization"
```

---

## §6 Integration with Roc Racoon's Knowledge Metabolism

After a concept passes through the pipeline:

1. **If ADOPTED/ADAPTED**: 
   - Add a cross-reference entry to `data/entities/roc_racoon/knowledge/INDEX.yaml`
   - Roc's `applies_to` field tracks what agents benefit from this pattern
   
2. **If DEFERRED/REJECTED**:
   - Log in Roc's knowledge as a "negative lesson" — something we tried
     or considered and rejected, so future agents don't re-propose it
   - The 8-char cap becomes a **negative lesson** in Roc's taxonomy

3. **Cross-Pollination**:
   - When Roc mines a legacy pattern that overlaps with a heritage concept,
     the vet log cross-references the mining report and vice versa
   - Prevents the "two agents working on the same thing independently" problem

### Roc Knowledge Entry Format for Heritage Concepts

```yaml
  - id: heritage-001
    type: heritage-concept
    concept: "8-Character Name Caps"
    vet_status: "rejected"
    vet_record: "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md#vet-001"
    summary: "Rejected: cargo-cult optimization with no Python benefit"
    applies_to: ["Doom Guy", "Kali", "quality"]
    lesson: "C-ARCH-001: Hardware-specific optimizations don't transfer to Python"
```

---

## §7 CI Enforcement: `make heritage-vet`

Add a CI gate that verifies:

1. Every `[id-soft:]` tag in `src/omega/` maps to a record in
   `HERITAGE_VET_LOG.md` that is either ADOPTED or ADAPTED
2. Any `[id-soft:]` tag that doesn't have a corresponding vet record
   fails the gate
3. Any concept in `PENDING_CREDITS_QUEUE.md` with status `pending` or
   `in-progress` that hasn't passed through vetting also fails

```
make heritage-vet  →  FAIL if unvetted [id-soft:] tags found
```

---

## §8 Enforcement Rules

### Rule 1: No Unvetted Heritage Code
No code with `[id-soft:]` tags may be merged without a corresponding vet
record. Exception: corrections to existing heritage entries
(changing attribution, fixing source references).

### Rule 2: Vetting Must Precede Implementation
The vet record must be timestamped *before* the implementation commit.
If implementation precedes vetting, the implementation is rolled back.

### Rule 3: Reserved Vetting Authority

| Agent | Can Vet | Cannot Vet |
|-------|---------|------------|
| **Kali** | All concepts (unification authority) | (unlimited) |
| **Ma'at** | N1-N5 concepts (build side) | N6-N10 concepts |
| **Lilith** | N6-N10 concepts (run side) | N1-N5 concepts |
| **Doom Guy** | Proposes, provides evidence | Final decision (conflict of interest) |
| **User** | Override all | N/A |

### Rule 4: Failure Mode Recording
Every rejected concept must record:
- Why it was rejected
- The commit of the attempted implementation (if any)
- A lesson in the vetters' soul.yaml (L1→L2→L3)

---

## §9 The Lessons Already Learned (Immediate Retroactive Application)

Before this pipeline existed, 23 concepts entered the codebase. Apply the
vetting framework retroactively:

| Concept | Vetted? | Would Pass? | Status |
|---------|---------|-------------|--------|
| WAD System (IWAD/PWAD) | ✅ Original user design | 10/10 ✅ | Keep |
| BSP Culling (pre-check) | ⚠️ Implicit | 8/10 ✅ | Keep |
| FISR / Right Approximation | ⚠️ Philosophical | 10/10 ✅ | Keep |
| Zone Memory (ResourceGuard) | ⚠️ Implicit | 9/10 ✅ | Keep |
| Surface Cache (tiered mem) | ⚠️ Attribution only | 7/10 ✅ | Keep |
| Worse is Better | ⚠️ Philosophical | 10/10 ✅ | Keep |
| Carmack's Law | ⚠️ Philosophical | 10/10 ✅ | Keep |
| Circuit Breaker Consolidation | ⚠️ Bug fixes prove value | 9/10 ✅ | Keep |
| ZONEID Constants | ⚠️ Implemented directly | 9/10 ✅ | Keep |
| Lazy Deletion | ⚠️ Implemented directly | 9/10 ✅ | Keep |
| Heritage Tag Protocol | ⚠️ Process, not code | 10/10 ✅ | Keep |
| **8-Char Name Caps** | ❌ **No vetting** | **1/10** ❌ | **REMOVED** |
| cvar Table | ⚠️ Implemented directly | 7/10 ✅ | Keep |
| 4-Tier Memory | ⚠️ Mapped only | 5/10 ⏸ | Defer |
| Multi-Index Entity | ⚠️ Mapped only | 7/10 ✅ | Keep |
| QuakeC Flat-Field | ⚠️ Mapped only | 4/10 ⏸ | Defer |
| Hard-Boundary Struct | ⚠️ Implemented | 5/10 ⏸ | Re-evaluate |
| 4-Path VFS | ⚠️ Mapped only | 6/10 ⏸ | Defer |
| High-Bit Trick | ⚠️ Implemented | 6/10 ✅ | Keep (edge case) |
| Fixed-Size Active Set (32) | ⚠️ Implemented | 4/10 ⏸ | Soften limit |
| netchan Protocol | ⚠️ Mapped only | 3/10 ⏸ | Defer |
| idHeap | ⚠️ Mapped only | 5/10 ⏸ | Defer |
| Fixed-Point Math | ⚠️ Mapped only | 6/10 ✅ | Keep |

**Total after retroactive vetting**: 15 Keep / 1 Removed / 6 Deferred / 1 Re-evaluate

---

## §10 Quick-Start: How to Use This Pipeline

When Doom Guy proposes a new heritage concept:

```
1. Write discovery R-doc (like Vol I-V)
2. Create vet record in HERITAGE_VET_LOG.md with for/against
3. Score concept (0-10)
4. If score ≥ 7: proceed to implementation
5. If score < 7: log as rejected or deferred, move on
6. After implementation: cross-reference in Roc's INDEX.yaml
7. Run make heritage-vet to confirm gate passes
```

---

*⬡ OMEGA ⬡ KALI ⬡ VETTING-GATE ⬡ v1.0.0*
*Created: 2026-06-04 — in response to 8-char cap cargo-cult incident*
*Authority: Kali (Transcendent Oversoul)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: VETTING-GATE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
