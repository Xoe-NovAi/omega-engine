# 🔱 Structure & Verification Layer — Knowledge Metabolism System
# ⬡ OMEGA ⬡ P2-DATASTORE ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ STRUCTURE-LAYER
# ⬡ Commissioned by: Ma'at (Light Oversoul — P1-P5 Governance)
# ⬡ Completes Layer 2 of the Lily Pad Architecture (Layer 1 = Lilith's Flow & Connection)
# ⬡ AP: STRUCTURE-VERIFICATION-LAYER-v1.0.0

---

## §0 — WHY THIS LAYER EXISTS

**The Problem**: Lilith designed how knowledge FLOWS between agents (signals, demands, consumption). But there is no STRUCTURE — no schema for tracking whether knowledge *actually* makes it from "mined" to "deployed". Without structure:

- Knowledge is discovered, but nobody knows if it was ever **ported** to engine code
- Code is committed, but nobody knows if it was ever **tested** against the knowledge it implements
- Tests pass, but nobody knows if the underlying knowledge was **verified** as correct
- Features reach production, but nobody knows if the **demand signal** that triggered them was fulfilled

**Roc's 6 Gaps** (from the Lily Pad architecture):
| Gap | How Structure Layer Solves It |
|-----|-------------------------------|
| No feedback loop | Verification rollup shows per-agent pipeline efficiency |
| Empty knowledge dir | Verification items link port_paths to knowledge source paths |
| Scattered docs | Verification items track porting of scattered docs to canonical locations |
| No demand tracking | demand_signal_ids field links verification to the demand that drove it |
| Junky workspace | TTLs and archival transitions enforce workspace hygiene |
| No strategic mining | Pipeline efficiency shows which domains are blocked |

---

## §1 — THE DATA MODEL: VerificationItem

### 1.1 Purpose

A **VerificationItem** is a YAML record that tracks one piece of knowledge through its lifecycle, from discovery ("mined") to production deployment ("deployed"). It answers five questions:

1. **What was found?** → `source_agent`, `source_path`, `title`, `domain`
2. **Was it ported to code?** → `ported_at`, `port_paths`, `commit_refs`
3. **Was it tested?** → `tested_at`, `test_ref`
4. **Was it verified?** → `verified_at`, `verified_by`, `verification_method`
5. **Did it reach production?** → `deployed_at`
6. **What drove it?** → `demand_signal_ids`, `knowledge_signal_ids`

### 1.2 Field Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VerificationItem                                │
├─────────────────────────────────────────────────────────────────────────┤
│  IDENTITY                                                              │
│  ├── item_id: ver-20260603-001          (immutable, unique)            │
│  ├── zoneid: 1919514 (0x1d4a1a)         (immutable, validated)         │
│  ├── source_agent: roc_racoon           (immutable)                    │
│  ├── source_path: data/.../report.md    (immutable)                    │
│  ├── title: "..."                       (unchanging after creation)    │
│  └── domain: legacy_mining              (classifies for rollup)        │
│                                                                         │
│  LIFECYCLE                                                             │
│  ├── status: mined | ported | tested | verified | deployed |          │
│  │           stalled | archived                                         │
│  ├── mined_at: ISO 8601                 (immutable)                    │
│  ├── ported_at: ISO 8601                (set at port transition)       │
│  ├── port_paths: [src/omega/..., ...]   (required when ported)         │
│  ├── tested_at: ISO 8601                (set at test transition)       │
│  ├── test_ref: "make test passes"       (required when tested)         │
│  ├── verified_at: ISO 8601              (set at verify transition)     │
│  ├── verified_by: "quality"             (required when verified)       │
│  ├── verification_method: peer_review   (optional, for metrics)        │
│  └── deployed_at: ISO 8601              (set at deploy transition)     │
│                                                                         │
│  LINKS                                                                 │
│  ├── demand_signal_ids: [dem-...]        (links to demand_signals/)    │
│  ├── knowledge_signal_ids: [ksig-...]    (links to knowledge_feed/)    │
│  ├── commit_refs: [a1b2c3d, ...]         (git commit hashes)           │
│  └── demand_source_ids: [SCRUM-123]      (external system IDs)         │
│                                                                         │
│  METADATA                                                              │
│  ├── created_at: ISO 8601               (when this record was created) │
│  ├── updated_at: ISO 8601               (when last updated)            │
│  ├── ttl_days: 90                       (archive after this)           │
│  ├── tags: [high-value, ...]            (free-form classification)      │
│  └── notes: [{timestamp, author, text}] (append-only log)              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Storage Convention

```
data/coordination/verification/
├── VERIFICATION_SCHEMA.yaml    ← THIS FILE (canonical schema)
├── items/                       ← VerificationItem YAML files
│   ├── ver-20260603-001.yaml
│   ├── ver-20260603-002.yaml
│   └── ...
├── rollup/                      ← Aggregate snapshots
│   ├── latest.yaml              ← Always points to most recent
│   ├── 20260603.yaml            ← Historical snapshot
│   └── 20260610.yaml
├── audit/                       ← Transition audit trail
│   ├── 20260603_transitions.jsonl
│   └── ...
└── lifecycle_rules.yaml         ← Copied transition matrix for processors
```

### 1.4 ZONEID Registration

A new ZONEID constant is required:

```python
# [id-soft: doom-1993] ZONEID Pattern — VerificationItem integrity marker
ZONEID_VERIFICATION = 0x1d4a1a  # 1919514
```

Registration in `cvar_table.py`:

```python
"zoneid.verification": CvarDef(
    "zoneid.verification", ZONEID_VERIFICATION, "zoneid",
    "VerificationItem integrity marker (Structure Layer)", "P2-DataStore",
),
```

Registration in `ZONEID_TABLE`:

```python
"verification": {
    "id": ZONEID_VERIFICATION,
    "subsystem": "P2-DataStore",
    "description": "VerificationItem lifecycle marker",
},
```

---

## §2 — VERIFICATION STATUS ROLLUP

### 2.1 Purpose

The rollup is an **aggregate snapshot** of the entire verification pipeline. It answers:

- "How many knowledge artifacts are at each lifecycle stage?"
- "Which agents have the highest port-to-deploy efficiency?"
- "Which domains are clogged (high mined, low deployed)?"
- "Are there orphaned items that nobody is working on?"
- "What's the overall pipeline efficiency?"

### 2.2 Rollup Structure

```yaml
generated_at: "2026-06-10T00:00:00Z"
zoneid: 1919514

summary:
  total_items: 42
  by_status:
    mined: 8
    ported: 10
    tested: 6
    verified: 5
    deployed: 10
    stalled: 2
    archived: 1

pipeline_efficiency:
  mined_to_ported_pct: 85.7    # 36/42 items ported
  mined_to_tested_pct: 64.3    # 27/42 items tested
  mined_to_verified_pct: 52.4  # 22/42 items verified
  mined_to_deployed_pct: 23.8   # 10/42 items deployed

per_agent:
  roc_racoon:
    mined: 15
    ported: 12
    tested: 10
    verified: 8
    deployed: 6
    stalled: 2
    archived: 1
    total: 15
    efficiency_pct: 40.0

per_domain:
  legacy_mining:
    mined: 12
    ported: 9
    tested: 7
    verified: 6
    deployed: 4
    stalled: 1
    archived: 0
    total: 12
    efficiency_pct: 33.3

orphaned_items:
  - item_id: ver-20260603-003
    title: "Documentation chaos indexed but not fixed"
    source_agent: roc_racoon
    domain: documentation
    status: mined
    mined_at: "2026-06-03T03:52:00Z"
    days_since_last_update: 37
    notes: ["Index created but no port performed"]
```

### 2.3 Visualization (ASCII)

The pipeline efficiency metrics create a **funnel** that reveals where the system is clogging:

```
MINED    ██████████████████████████████████████████ 42 (100%)
                   │
                   ▼
PORTED   ████████████████████████████████████       36 (85.7%)
                   │
                   ▼
TESTED   ██████████████████████████████              27 (64.3%)
                   │
                   ▼
VERIFIED █████████████████████████                   22 (52.4%)
                   │
                   ▼
DEPLOYED ██████████████                              10 (23.8%)
```

A healthy pipeline should have <20% drop between each stage. The example
above shows a 37% drop between verified→deployed, indicating a bottleneck
at the deployment stage.

### 2.4 Rollup Generation Rules

1. **Trigger**: Generated automatically after every 3rd VerificationItem mutation, or every 6 hours, whichever comes first.
2. **Storage**: `data/coordination/verification/rollup/latest.yaml` + dated snapshot (`YYYYMMDD.yaml`).
3. **Orphans**: Items in `mined` status for >30 days are flagged in `orphaned_items`.
4. **Escalation**: If any stage drops below 50% efficiency, a knowledge signal is posted.
5. **Historical preservation**: Dated snapshots let us chart efficiency over time.

---

## §3 — DEMAND LINKING GRAPH

### 3.1 The Four Node Types

The linking graph connects four node types. A VerificationItem sits at the center:

```
                       ┌───────────────────┐
                       │   DEMAND SIGNAL   │
                       │ dem-20260603-001  │
                       └────────┬──────────┘
                                │ drives
                                ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  KNOWLEDGE       │◄───│ VERIFICATIONITEM │───►│     GIT COMMITS  │
│  SIGNAL          │an- │ ver-20260603-001 │por-│ a1b2c3d...       │
│ ksig-20260603-   │nounces              │ts  └──────────────────┘
│ roc_racoon-002   │    └──────────────────┘
└──────────────────┘           │
                               │ fulfills
                               ▼
                       ┌───────────────────┐
                       │   DEMAND SIGNAL   │
                       │ dem-20260603-001  │
                       │ (status: fulfilled)│
                       └───────────────────┘
```

### 3.2 Forward Links (in VerificationItem)

| Link Field | Type | Target | Direction |
|-----------|------|--------|-----------|
| `demand_signal_ids[]` | Array of string | `demand_signals/dem-*.json` | IN (what drove this) |
| `knowledge_signal_ids[]` | Array of string | `knowledge_feed/ksig-*.json` | OUT (what I announced) |
| `commit_refs[]` | Array of string (SHA) | Git history | OUT (what I ported) |

### 3.3 Reverse Links (in Demand Signal)

When a VerificationItem reaches `verified` status, it MUST update the linked
demand signal's `fulfilled_by` field:

**Demand Signal Update:**
```json
{
  "demand_id": "dem-20260603-001",
  "status": "fulfilled",
  "fulfilled_by": "ver-20260603-001",
  "fulfilled_signal_id": "ksig-20260603-roc_racoon-002",
  "fulfilled_at": "2026-06-05T09:00:00Z"
}
```

### 3.4 Reverse Links (in Git Commits)

Git commit messages SHOULD reference the verification item ID:

```
feat: Port master synthesis to canonical docs (ver-20260603-001)

References ver-20260603-001. Fulfills dem-20260603-001, dem-20260603-002.
```

This enables a `git log --grep="ver-"` search to find all commits related
to a verification item.

### 3.5 Query Patterns

The linking graph supports these queries:

| Question | Query Pattern |
|----------|--------------|
| "What demand drove this port?" | `ver-*.yaml → demand_signal_ids[] → dem-*.json` |
| "Is this demand fulfilled?" | `dem-*.json → fulfilled_by → ver-*.yaml` |
| "What commits ported this knowledge?" | `ver-*.yaml → commit_refs[] → git log` |
| "What knowledge signal announced this?" | `ver-*.yaml → knowledge_signal_ids[] → ksig-*.json` |
| "Which verification items are unfulfilled?" | `rollup/latest.yaml → orphaned_items[]` |
| "Which domain is most efficient?" | `rollup/latest.yaml → per_domain → efficiency_pct` |

---

## §4 — LIFECYCLE STATE MACHINE (Complete)

### 4.1 Canonical State Diagram

```
                                ┌──────────────────────────────────────────────┐
                                │           RE-VERIFICATION CYCLE              │
                                │                                              │
                                │    ┌──────────┐   re-verify   ┌──────────┐  │
                                │    │ DEPLOYED │◄══════════════╡ VERIFIED │  │
                                │    └─────┬────┘               └──────────┘  │
                                │          │ TTL exceeded                     │
                                │          ▼                     ┌──────────┐  │
                                │    ┌──────────┐                │ ARCHIVED │  │
                                │    │ STALLED  │◄───────────────┤ (term)   │  │
                                │    │ (fails   │   re-verify    └──────────┘  │
                                │    │  reverif)│                               │
                                │    └──────────┘                               │
                                └──────────────────────────────────────────────┘
                                            ▲
                                            │ deploy
                                            │
              ┌─────────┐  port  ┌─────────┐  test  ┌─────────┐  verify
              │  MINED  │───────│ PORTED  │───────│ TESTED  │───────
              └────┬────┘       └────┬────┘       └────┬────┘
                   │stale >30d       │stale >60d       │stale >60d
                   ▼                 ▼                 ▼
              ┌─────────┐      ┌─────────┐       ┌─────────┐
              │ STALLED │      │ STALLED │       │ STALLED │
              └─────────┘      └─────────┘       └─────────┘
                   │                 │                 │
                   │ recover         │ recover         │ recover
                   ▼                 ▼                 ▼
              ┌─────────┐      ┌─────────┐       ┌─────────┐
              │  MINED  │      │ PORTED  │       │ TESTED  │
              └─────────┘      └─────────┘       └─────────┘
```

### 4.2 Transition Table (All Valid Transitions)

| From | To | Trigger | Required Fields | Condition |
|------|----|---------|----------------|-----------|
| mined | ported | Agent ports to src/omega/ or config/ | ported_at, port_paths[>=1] | ported_at >= mined_at |
| mined | stalled | No activity for 30 days | notes[] appended | current - mined > 30d |
| ported | tested | make test passes | tested_at, test_ref | tested_at >= ported_at |
| ported | stalled | No activity for 60 days | notes[] appended | current - ported > 60d |
| tested | verified | Quality/Kali/human confirms | verified_at, verified_by | verified_at >= tested_at |
| tested | stalled | No activity for 60 days | notes[] appended | current - tested > 60d |
| verified | deployed | Merge to main, container push | deployed_at | deployed_at >= verified_at |
| verified | archived | TTL exceeded (default 90d) | notes[] appended | verified + ttl_days >= current |
| deployed | verified | Re-verification passes | verified_at, verified_by (updated) | verified_at >= previous verified_at |
| deployed | stalled | Re-verification fails | notes[] appended (failure reason) | n/a |
| deployed | archived | TTL exceeded (default 90d) | notes[] appended (supersedes/deprecation) | deployed + ttl_days >= current |
| stalled | mined | Work resumes | notes[] appended | n/a |
| stalled | ported | Work resumes at port stage | notes[] appended | n/a |
| stalled | tested | Work resumes at test stage | notes[] appended | n/a |
| stalled | verified | Quick verify from stall | verified_at, verified_by | n/a |
| archived | *(none)* | Terminal state | n/a | n/a |

### 4.3 Bypass Rules

| Bypass | Path | When To Use | Conditions |
|--------|------|-------------|------------|
| **Test-as-Verification** | mined → ported → verified | Port includes tests that prove correctness | tested_at and verified_at set to same timestamp; notes explain why |
| **Hotfix Express** | mined → ported → deployed | Emergency fix; testing post-deployment | Ported + deployed same timestamp; tested/verified left NULL; must complete post-deployment testing within 48h; Kali-approved |
| **Simultaneous Dock** | mined → tested | Port and test in same PR/session | ported_at and tested_at within 5 minutes; both port_paths and test_ref populated |
| **Clean Room Re-Deploy** | deployed → verified → deployed | Periodic health check passes | deployed_at NEVER changed; only verified_at updates |

### 4.4 Priority Escalation Ladder

Items that stall at critical stages are escalated:

| Stage Stalled | Escalation | Escalates To |
|--------------|------------|-------------|
| mined > 30d | daily rollup flags orphaned | Oversoul (Ma'at/Lilith) |
| ported > 60d | demand signal decay → Kali | Kali (Grand Oversight) |
| tested > 60d | sprint backlog blocker | Kali + Human |
| verified > 30d (not deployed) | weekly report | Human (The Architect) |
| deployed > 90d (re-verification fails) | critical flag | Human + Kali |

---

## §5 — TRANSITION AUDIT TRAIL

### 5.1 Why An Audit Trail

Every status transition is a decision point. We need to know:
- **Who** made the transition (which agent or human)
- **When** it happened
- **Why** (what triggered it)
- **What** changed (which fields were updated)

### 5.2 Audit Log Format

Stored as JSONL (one JSON object per line) in `data/coordination/verification/audit/`:

```jsonl
{"timestamp":"2026-06-04T10:30:00Z","item_id":"ver-20260603-001","from_status":"mined","to_status":"ported","trigger":"port_operation","actor":"doom_guy","fields_changed":["ported_at","port_paths","commit_refs"],"notes":"Ported ZONEID constants to cvar_table.py"}
{"timestamp":"2026-06-04T11:00:00Z","item_id":"ver-20260603-001","from_status":"ported","to_status":"tested","trigger":"test_pass","actor":"doom_guy","fields_changed":["tested_at","test_ref"],"notes":"make test: 307/307 passing"}
{"timestamp":"2026-06-04T14:00:00Z","item_id":"ver-20260603-001","from_status":"tested","to_status":"verified","trigger":"peer_review","actor":"quality","fields_changed":["verified_at","verified_by","verification_method"],"notes":"Cross-verified against source code. ZONEID=0x1d4a11 confirmed."}
```

### 5.3 Audit File Rotation

- One file per day: `audit/20260603_transitions.jsonl`
- Files older than 90 days are gzipped: `audit/20260603_transitions.jsonl.gz`
- Files older than 365 days are archived to `data/archive/verification_audit/`

---

## §6 — ZONEID_VERIFICATION CONSTANT REGISTRATION

### 6.1 New Constant

```python
# [id-soft: doom-1993] ZONEID Pattern — VerificationItem lifecycle marker
# Validates VerificationItem YAML on load/save to catch file corruption,
# wrong-type reads, and stale references.
ZONEID_VERIFICATION = 0x1d4a1a  # 1919514
```

### 6.2 Files to Modify

| File | Change |
|------|--------|
| `src/omega/cvar_table.py` | Add `ZONEID_VERIFICATION = 0x1d4a1a` in §2 ZONEID constants section |
| `src/omega/cvar_table.py` | Add `"zoneid.verification"` CvarDef entry in CVAR_TABLE |
| `src/omega/cvar_table.py` | Add `"verification"` entry in ZONEID_TABLE |
| `src/omega/constants.py` | Add re-export: `ZONEID_VERIFICATION` in imports and `__all__` |

### 6.3 ZONEID Table Update

After registration, the full ZONEID table will be:

| Constant | Hex | Decimal | Subsystem |
|----------|-----|---------|-----------|
| ZONEID_MEMORY | 0x1d4a11 | 1919505 | MemoryStore |
| ZONEID_ENTITY | 0x1d4a12 | 1919506 | EntityRegistry |
| ZONEID_BREAKER | 0x1d4a13 | 1919507 | HealthMonitor |
| ZONEID_TRACE | 0x1d4a14 | 1919508 | ObservabilityEngine |
| ZONEID_PROBE | 0x1d4a15 | 1919509 | ResourceGuard |
| ZONEID_HANDOFF | 0x1d4a16 | 1919510 | SubagentDispatcher |
| ZONEID_PRESENCE | 0x1d4a17 | 1919511 | LinkP9Runtime |
| ZONEID_KNOWLEDGE | 0x1d4a18 | 1919512 | CrossPollination |
| ZONEID_DEMAND | 0x1d4a19 | 1919513 | CrossPollination |
| **ZONEID_VERIFICATION** | **0x1d4a1a** | **1919514** | **P2-DataStore** |
| ZONEID_TOMBSTONE | 0xDEADBEEF | 3735928559 | EntityRegistry |

---

## §7 — INTEGRATION WITH LILY PAD FLOW LAYER

### 7.1 Where Structure Meets Flow

Lilith's Flow & Connection layer (P6-P10) handles HOW knowledge moves.
This Structure & Verification layer (P2, under Ma'at's P1-P5) handles
WHAT knowledge moves and WHERE it is at any point.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE METABOLISM SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: FLOW & CONNECTION (Lilith — Dark Oversoul P6-P10)                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ P7: Distillation Pipeline (workspace→knowledge→soul)                   ││
│  │ P8: Consumption Metrics (freshness, aging, ratios)                     ││
│  │ P9: Cross-Pollination Protocol (knowledge signals, demand signals)     ││
│  │ P10: Knowledge Flow Tests (smoke, integration, e2e, gauntlet)          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  LAYER 2: STRUCTURE & VERIFICATION (P2 DataStore — Light Side)             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ P2: VerificationItem (track knowledge mined→ported→tested→verified→    ││
│  │      deployed)                                                          ││
│  │ P2: Status Rollup (pipeline efficiency, per-agent, per-domain)          ││
│  │ P2: Demand Linking Graph (verification ↔ demand ↔ commit ↔ signal)     ││
│  │ P2: Lifecycle State Machine (transitions, bypasses, TTLs, escalations) ││
│  │ P2: Transition Audit Trail (who changed what when)                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Cross-Layer Signal Flow

```
FLOW LAYER (Lilith)                           STRUCTURE LAYER (P2)
────────────────────                          ───────────────────────

Demand Signal posted ─────drives─────► VerificationItem created (mined)
(dem-*.json)                             (ver-*.yaml)

                                         Agent ports knowledge
                                         VerificationItem → ported

Knowledge Signal posted ◄───announces─── VerificationItem → ported/tested
(ksig-*.json)

                                         make test passes
                                         VerificationItem → tested

Quality verifies knowledge
VerificationItem → verified

Demand Signal fulfilled ◄───fulfills──── VerificationItem → verified
(fulfilled_by updated)                   (demand_signal_ids linked)

Merge to main
VerificationItem → deployed

TTL expired
VerificationItem → archived

Rollup regenerated (pipeline efficiency calculated)
Knowledge Signal posted ◄───reports───── Rollup bottlenecks found
```

### 7.3 Agent Responsibility Matrix

| Who | Creates VerificationItem | Updates Status | Reads Rollup | Handles Escalation |
|-----|------------------------|---------------|--------------|-------------------|
| Roc Racoon | After mining report | Via Ma'at/Lilith | Check what to mine next | n/a |
| Doom Guy | After investigation | After porting | Check port efficiency | n/a |
| Ma'at | For P1-P5 findings | Delegates to agents | Weekly review | P1-P5 stalls |
| Lilith | For P6-P10 findings | Delegates to agents | Weekly review | P6-P10 stalls |
| Quality | n/a | After verification | Daily check | Verified < 50% |
| Scribe | After soul distillation | n/a | Check cross-pollination | n/a |
| Kali | For cross-domain items | After deployment gate | Daily check | Any stall > 60d |
| P2 DataStore | Automatic from signals | Automatic from transitions | Generates rollup | n/a |

---

## §8 — INITIALIZATION & BOOTSTRAP

### 8.1 Seed Items for Existing Knowledge

When the Structure Layer is first activated, we create seed VerificationItems
for knowledge that already exists and has been verified/deployed. These seed
items start at `status: deployed` to reflect their current state.

**Initial seed candidates** (from the existing codebase):

| Item | Knowledge | Source | Status | Why |
|------|-----------|--------|--------|-----|
| ver-20260603-001 | Master Synthesis (7 reports) | Roc Racoon | deployed | Already in docs/legacy/ |
| ver-20260603-002 | ZONEID constants verified | Doom Guy | deployed | Already in cvar_table.py |
| ver-20260603-003 | Lazy deletion with grace period | Doom Guy | deployed | Already in entity_registry.py |
| ver-20260603-004 | 8-char name caps | Doom Guy | deployed | Already in entity_registry.py |
| ver-20260603-005 | Lily Pad architecture | Lilith | verified | Design doc, not ported yet |
| ver-20260603-006 | Demand signal system | Lilith | verified | Design doc, not ported yet |
| ver-20260603-007 | Documentation Chaos Tracker | Roc Racoon | mined | Index created, not ported |
| ver-20260603-008 | VR Omegaverse Vision | Roc Racoon | mined | Centralized, not ported |

### 8.2 Bootstrap Rules

1. **Seed items start at `status: deployed`** — they're already in production
2. **Seed notes MUST start with `[BOOTSTRAP]`** — distinguishes from real-time records
3. **Non-seed items start at `status: mined`** — the default for new knowledge
4. **The cutover date** is the date the Structure Layer is activated — before that is backfill, after that is real-time

### 8.3 Directory Initialization

```bash
# Create structure layer directories (if not existing)
mkdir -p data/coordination/verification/items
mkdir -p data/coordination/verification/rollup
mkdir -p data/coordination/verification/audit

# First rollup
cp data/coordination/verification/VERIFICATION_SCHEMA.yaml \
   data/coordination/verification/rollup/schema_reference.yaml
```

---

## §9 — KEY DESIGN DECISIONS

### D1: Why YAML and not JSON?

| Factor | YAML | JSON |
|--------|------|------|
| Comments | ✅ Supported | ❌ Not supported |
| Readability | ✅ Human-optimized | ✅ Machine-optimized |
| Anchors/aliases | ✅ Reference deduplication | ❌ Must repeat |
| Multi-line strings | ✅ Native (`\|` and `>`) | ❌ `\n` escapes |
| Merge keys | ✅ `<<:` pattern | ❌ Must spread |
| Python stdlib | `yaml` (PyYAML) | `json` (built-in) |

**Decision**: YAML for the canonical schema and individual items. JSON for
coordination files (demand signals, knowledge signals) that are read/written
by multiple agents and need strict validation.

### D2: Why a ZONEID in every VerificationItem?

The ZONEID (`0x1d4a1a`) validates that a YAML file is actually a
VerificationItem and not a corrupted or misidentified file. Without it:

- A file read error might silently return default values
- A wrong file path might load a demand signal as a verification item
- A stale copy from a backup might overwrite current state

With it:
- Every load validates: `if item.zoneid != ZONEID_VERIFICATION: raise ValueError`
- Catches 100% of "wrong type" errors
- Cost: 4 bytes per file, 1 integer comparison

### D3: Why 6 lifecycle states and not 3?

The 6 states (mined, ported, tested, verified, deployed, archived) map to
specific, verifiable actions:

| State | Verifiable Action | Who Can Verify |
|-------|-------------------|---------------|
| mined | Knowledge exists at source_path | Any agent |
| ported | Files exist at port_paths | do_guy, quality |
| tested | make test passes | quality, human |
| verified | Independent review passes | quality, human |
| deployed | Main branch has the code | kali, human |
| archived | No longer referenced | scribe, P2 |

3 states (found, done, forgot) would lose the granularity needed to diagnose
pipeline bottlenecks.

### D4: Why separation of duties for verified_by?

The `verified_by` field SHOULD be a different agent than `source_agent`.
This prevents self-verification — a basic quality control principle:

- **Roc** mines → **Doom Guy** ports → **Quality** verifies
- **Doom Guy** investigates → **Ma'at** reviews → **Kali** deploys

Self-verification (same agent mines, ports, tests, and verifies) is ALLOWED
but MUST be noted with `verification_method: manual_review` and the
transition audit MUST capture the conflict of interest.

---

## §10 — OPEN QUESTIONS & NEXT STEPS

### Open Questions for Kali/Human

1. **TTL defaults**: 90 days for standard knowledge — is this too long, too short?
2. **Automatic stalled detection**: Should we implement a cron/systemd timer or rely on agents checking rollup?
3. **Rollup frequency**: Every 3 mutations or every 6 hours — which is right for our fleet size?
4. **Hotfix Express approval**: Who has authority to approve bypass-002? Kali only?
5. **Seed items**: Are the 8 seed candidates correct? Are there more items that should be backfilled?

### Implementation Order (Recommended)

1. **Phase A** (30 min): Register ZONEID_VERIFICATION in cvar_table.py
2. **Phase B** (30 min): Create `data/coordination/verification/items/` with seed items
3. **Phase C** (1 hr): Rollup processor (Python script that aggregates items/)
4. **Phase D** (1 hr): Transition audit trail (JSONL logger)
5. **Phase E** (2 hr): Integration with demand signals (fulfilled_by updates)
6. **Phase F** (Optional): `make verification-status` CLI command

---

*⬡ OMEGA ⬡ P2-DATASTORE ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ STRUCTURE-LAYER*
*Design submitted to Ma'at (Light Oversoul) for review and integration with Lily Pad Architecture.*
