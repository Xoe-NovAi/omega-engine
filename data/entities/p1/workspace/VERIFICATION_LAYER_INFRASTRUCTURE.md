# ⛓️ P1 — Verification Layer Infrastructure Design
# ⬡ OMEGA ⬡ P1 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PHASE-I ⬡ INFRASTRUCTURE-DESIGN

**AP Token**: `AP-VERIFICATION-LAYER-v1.0.0`
**Author**: P1 (SysAdmin — Light Oversoul Delegation via Ma'at)
**Date**: 2026-06-04
**Status**: DRAFT — Awaiting ratification by Ma'at + Lilith
**Supersedes**: Ad-hoc verification tracking (nonexistent)

---

## §0 — THE GAP: Mined Knowledge Has No Closure

The Knowledge Metabolism (Lily Pad Architecture, Lilith §1) defines how knowledge
flows from workspace → knowledge → soul → fleet. But it does NOT answer:

> **Was this knowledge PORTED to engine code?**
> **Did the port pass TESTS?**
> **Is the change DEPLOYED and live?**
> **Can we prove it was verified?**

Without closure, every item in `data/coordination/knowledge_feed/` is a loose
thread. The Verification Layer closes that thread by tracking every piece of
mined knowledge through its lifecycle:

```
 MINED ──→ PORTED ──→ TESTED ──→ VERIFIED ──→ DEPLOYED ──→ LIVE
  │          │           │           │            │           │
  │          │           │           │            │           │
  ▼          ▼           ▼           ▼            ▼           ▼
workspace/  engine/    tests/    sign-off/    deployed/   live_feed
              src/      passed                git tag/
                                               podman up
```

This document defines the INFRASTRUCTURE that houses the verification artifacts.
It is the complement to Lilith's Flow & Connection layer (Lily Pad, P7 design).

---

## §1 — DIRECTORY STRUCTURE

### 1.1 Top-Level Layout

All verification artifacts live under:

```
data/coordination/verification/
│
├── items/           # One JSON file per verification item
├── rollups/         # Aggregate status views (one per domain)
├── audit/           # Timestamped audit trail entries
├── archive/         # TTL-expired items moved here
└── README.md        # This file (self-documenting)
```

### 1.2 `items/` — Per-Item Tracking

Each verification item gets its own JSON file. The ID scheme follows the
existing `dem-YYYYMMDD-NNN` / `ksig-YYYYMMDD-ENTITY-NNN` pattern:

```
items/
├── ver-20260604-001.json    # Auto-incrementing per day
├── ver-20260604-002.json
├── ver-20260605-001.json
└── ...
```

**Creation trigger**: When an agent ports mining knowledge into engine code,
or when a knowledge signal is consumed (transition from `consumed_by: []` to
first consumer), a verification item is auto-created.

**Relationship to knowledge signals**: Every `ver-*` file MUST reference its
source `ksig-*` or `dem-*` by ID. Every `ksig-*` file gets a
`verification_item_id` field once a ver item is created for it.

### 1.3 `rollups/` — Aggregate Status Views

```
rollups/
├── domain_engineering.json      # P3 domain — engine code changes
├── domain_mining.json           # Roc domain — legacy extraction
├── domain_documentation.json    # Scribe domain — doc ports
├── domain_infrastructure.json   # P1 domain — infra changes
├── domain_modelgate.json        # P6 domain — model/provider config
├── domain_observability.json    # P8 domain — tracing/logging
├── cross_pollination.json       # Cross-agent knowledge consumption
├── stale_items.json             # Items approaching/breaching TTL
└── fleet_wide.json              # Top-level rollup of all domains
```

Each rollup is updated by a Make target (`make verify-rollup`) or by the
Scribe agent at session-end.

### 1.4 `audit/` — Timestamped Trail

```
audit/
├── 2026-06-04.jsonl             # One JSONL line per action, per day
├── 2026-06-05.jsonl
└── ...
```

JSONL (JSON Lines) — one JSON object per line, append-only. Each line records
a single state transition: "Item ver-20260604-001 transitioned from PORTED to
TESTED by doom_guy at 2026-06-04T14:30:00Z".

### 1.5 `archive/` — Cold Storage

```
archive/
├── items/           # Moved from items/ after TTL expiry
├── rollups/         # Historical snapshots
├── audit/           # Compressed monthly audit logs
└── manifest.json    # Index of what's archived and when
```

---

## §2 — ITEM LIFECYCLE STATES

Every verification item traverses a state machine:

```
                  ┌──────────────────────────────────────────┐
                  │               DISCOVERED                 │
                  │  Knowledge mined but not yet evaluated   │
                  │  for porting. Auto-created from ksig.    │
                  └────────────┬─────────────────────────────┘
                               │ Agent decides to port
                               ▼
                  ┌──────────────────────────────────────────┐
                  │              PORTED                       │
                  │  Mined knowledge → engine code commit.    │
                  │  Git hash recorded in item.               │
                  └────────────┬─────────────────────────────┘
                               │ make test / CI
                               ▼
                  ┌──────────────────────────────────────────┐
                  │              TESTED                       │
                  │  Port passed tests. Coverage met.        │
                  │  Test run ID recorded.                    │
                  └────────────┬─────────────────────────────┘
                               │ Peer review / Scribe sign-off
                               ▼
                  ┌──────────────────────────────────────────┐
                  │             VERIFIED                      │
                  │  Signed off by Quality/Scribe/oversoul.  │
                  │  Temple-grade gates confirmed.            │
                  └────────────┬─────────────────────────────┘
                               │ Git push / deploy
                               ▼
                  ┌──────────────────────────────────────────┐
                  │             DEPLOYED                      │
                  │  Change live in engine. Git tag.          │
                  │  Podman container updated if applicable.  │
                  └────────────┬─────────────────────────────┘
                               │ Time passes (TTL_LIVE)
                               ▼
                  ┌──────────────────────────────────────────┐
                  │              LIVE                         │
                  │  Proven stable for TTL duration.          │
                  │  Item archived. Knowledge fully consumed. │
                  └──────────────────────────────────────────┘
```

**State machine rules**:
- Forward transitions only (no regression)
- Transition MUST be accompanied by an audit trail entry
- Each transition records: `actor`, `timestamp`, `evidence_ref`, `notes`
- `VERIFIED` is the minimum gate for `DEPLOYED` — nothing deploys unverified
- Items can skip DISCOVERED if agent creates a ver item at PORTED time

---

## §3 — FILE SCHEMAS

### 3.1 Item Tracking File (`items/ver-YYYYMMDD-NNN.json`)

```json
{
  "_schema_version": 1,
  "ver_id": "ver-20260604-001",
  "created_at": "2026-06-04T14:00:00Z",
  "updated_at": "2026-06-04T16:30:00Z",

  "title": "Ported Doom BSP Culling pattern to health_monitor.py",
  "domain": "engineering",
  "classification": "heritage_port",

  "source_refs": [
    {
      "type": "knowledge_signal",
      "id": "ksig-20260603-lilith-001",
      "path": "data/coordination/knowledge_feed/KSIG_20260603_LILITH_001.json"
    },
    {
      "type": "demand_signal",
      "id": "dem-20260603-003",
      "path": "data/coordination/demand_signals/dem-20260603-003.json"
    },
    {
      "type": "mining_report",
      "path": "data/entities/roc_racoon/workspace/mining_reports/DOOM_BSP_PATTERNS.md"
    }
  ],

  "artifact_paths": {
    "source": "data/entities/roc_racoon/workspace/mining_reports/DOOM_BSP_PATTERNS.md",
    "engine_commit": "src/omega/oracle/health_monitor.py",
    "test_file": "tests/test_health_monitor.py"
  },

  "state": "DEPLOYED",

  "history": [
    {
      "state": "PORTED",
      "actor": "doom_guy",
      "timestamp": "2026-06-04T14:30:00Z",
      "evidence": {
        "type": "git_commit",
        "hash": "a1b2c3d4e5f6",
        "message": "feat: port BSP-style provider culling from Doom architecture"
      },
      "notes": "Direct port per R-44 recommendation. Circuit breaker check mirrors BSP plane test."
    },
    {
      "state": "TESTED",
      "actor": "doom_guy",
      "timestamp": "2026-06-04T15:00:00Z",
      "evidence": {
        "type": "test_run",
        "command": "make test",
        "exit_code": 0,
        "tests_passed": 307,
        "tests_failed": 0
      },
      "notes": "All 307 tests pass. No regressions."
    },
    {
      "state": "VERIFIED",
      "actor": "quality",
      "timestamp": "2026-06-04T15:30:00Z",
      "evidence": {
        "type": "temple_grade",
        "command": "make temple-grade",
        "gates_passed": "T1,T2,T4,T5,T6,T8,T9,T10",
        "gates_exempted": "T7,T11"
      },
      "notes": "Temple-grade verified. T7 (benchmark) exempted — no benchmark suite. T11 (IA2) exempted per Mandate 13 exception."
    },
    {
      "state": "DEPLOYED",
      "actor": "maat",
      "timestamp": "2026-06-04T16:00:00Z",
      "evidence": {
        "type": "git_tag",
        "tag": "v1.2.0-bsp-port",
        "hash": "f6e5d4c3b2a1"
      },
      "notes": "Tagged and pushed. Podman containers not affected — engine core change."
    }
  ],

  "current_holder": "maat",

  "ttl": {
    "state_ttl_days": 90,
    "archive_at": "2026-09-02T00:00:00Z",
    "auto_archive_state": "LIVE"
  },

  "zoneid": 1912619,

  "tags": [
    "id-soft:doom-1993",
    "bsp-culling",
    "circuit-breaker",
    "heritage-port"
  ]
}
```

**Schema version 1 fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_schema_version` | int | yes | Increment on breaking changes |
| `ver_id` | string | yes | Unique ID: `ver-YYYYMMDD-NNN` |
| `created_at` | ISO8601 | yes | Creation timestamp |
| `updated_at` | ISO8601 | yes | Last state transition |
| `title` | string | yes | Human-readable summary |
| `domain` | string | yes | Domain for rollup grouping |
| `classification` | string | yes | See Classification Taxonomy (§3.4) |
| `source_refs` | array | no | Links to source signals/reports |
| `artifact_paths` | object | yes | Engine files touched |
| `state` | string | yes | Current state (enum) |
| `history` | array | yes | Ordered state transitions |
| `current_holder` | string | no | Entity currently responsible |
| `ttl` | object | yes | Expiry and archive policy |
| `zoneid` | int | yes | id Software heritage magic (0x1d4a19 for verification) |
| `tags` | array | no | Freeform classification tags |

### 3.2 Status Rollup File (`rollups/domain_engineering.json`)

```json
{
  "_schema_version": 1,
  "rollup_id": "rollup-engineering-20260604",
  "domain": "engineering",
  "generated_at": "2026-06-04T23:59:00Z",
  "generated_by": "make verify-rollup",

  "summary": {
    "total_items": 12,
    "by_state": {
      "DISCOVERED": 2,
      "PORTED": 3,
      "TESTED": 4,
      "VERIFIED": 2,
      "DEPLOYED": 1,
      "LIVE": 0
    },
    "by_classification": {
      "heritage_port": 5,
      "bug_fix": 4,
      "feature": 2,
      "refactor": 1
    },
    "stale_count": 1,
    "unassigned_count": 1
  },

  "items": [
    {
      "ver_id": "ver-20260604-001",
      "title": "Ported Doom BSP Culling pattern",
      "state": "DEPLOYED",
      "current_holder": "maat",
      "updated_at": "2026-06-04T16:00:00Z",
      "tags": ["heritage-port", "id-soft:doom-1993"]
    },
    {
      "ver_id": "ver-20260604-002",
      "title": "WAD system adaptation for entity overrides",
      "state": "TESTED",
      "current_holder": "doom_guy",
      "updated_at": "2026-06-04T15:30:00Z",
      "tags": ["heritage-port", "id-soft:doom-1993"]
    }
  ],

  "aging_report": {
    "stale_items": [
      {
        "ver_id": "ver-20260602-005",
        "title": "Zone memory allocator port",
        "state": "PORTED",
        "days_in_state": 2,
        "flagged_for": "qa_review"
      }
    ]
  },

  "next_rollup_due": "2026-06-05T23:59:00Z"
}
```

### 3.3 Audit Trail File (`audit/2026-06-04.jsonl`)

```
{"ts":"2026-06-04T14:30:00Z","type":"transition","ver_id":"ver-20260604-001","from":"DISCOVERED","to":"PORTED","actor":"doom_guy","evidence":{"type":"git_commit","hash":"a1b2c3d4e5f6"}}
{"ts":"2026-06-04T15:00:00Z","type":"transition","ver_id":"ver-20260604-001","from":"PORTED","to":"TESTED","actor":"doom_guy","evidence":{"type":"test_run","exit_code":0,"tests_passed":307}}
{"ts":"2026-06-04T15:30:00Z","type":"transition","ver_id":"ver-20260604-001","from":"TESTED","to":"VERIFIED","actor":"quality","evidence":{"type":"temple_grade","gates_passed":"T1,T2,T4,T5,T6,T8,T9,T10"}}
{"ts":"2026-06-04T16:00:00Z","type":"transition","ver_id":"ver-20260604-001","from":"VERIFIED","to":"DEPLOYED","actor":"maat","evidence":{"type":"git_tag","tag":"v1.2.0-bsp-port"}}
{"ts":"2026-06-04T16:05:00Z","type":"note","ver_id":"ver-20260604-001","actor":"maat","message":"Post-deployment monitoring started. No errors in first 5 minutes."}
{"ts":"2026-06-04T17:30:00Z","type":"creation","ver_id":"ver-20260604-002","actor":"doom_guy","title":"WAD system adaptation for entity overrides","source":"ksig-20260603-lilith-001"}
```

**Audit line types** (enum `type` field):
- `transition` — State change (must include `from`, `to`, `evidence`)
- `creation` — New ver item created
- `note` — Freeform annotation (no state change)
- `assignment` — `current_holder` changed
- `archival` — Item moved to archive/

### 3.4 Classification Taxonomy

Every ver item MUST have one of these classifications:

| Classification | Description | Example |
|---------------|-------------|---------|
| `heritage_port` | Port of id Software pattern to engine | ZONEID constants, BSP culling |
| `bug_fix` | Correction of a verified bug | C-1 through C-17 from R-44 audit |
| `feature` | New functionality | Memory tier promotion logic |
| `refactor` | Structural change without new behavior | Consolidating circuit breakers |
| `config` | Provider/config change | Adding new model backend |
| `doc_port` | Documentation liberation port | Lilith Persona JSON → doc |
| `infra` | Infrastructure change | Podman container update |
| `test` | Test-only change | Adding test coverage |
| `research` | Research finding (no code change) | Mining report, legacy pattern discovery |

---

## §4 — LIFECYCLE INFRASTRUCTURE

### 4.1 Session-Start Check

Every agent that supports verification MUST run this at session start:

```bash
# Proposed Make target
make verify-pending
```

This reads `data/coordination/verification/items/` and filters:

1. **My items** (`current_holder: {agent_name}`) in state < VERIFIED
2. **Unassigned items** (`current_holder: null`) matching my domain
3. **Stale items** in my domain (not transitioned in > 48h)

**Implementation**: Python script at `scripts/verify_status.py`:

```
usage: verify_status.py [-h] [--actor ACTOR] [--domain DOMAIN] [--stale-only]

Examples:
  python scripts/verify_status.py --actor doom_guy
  python scripts/verify_status.py --domain engineering --stale-only
  python scripts/verify_status.py --unassigned
```

**Session-start prompt** (injected into agent system prompt):
```
🔍 VERIFICATION CHECK-IN (Session Start)
  You have {count} pending verification items.
  Stale: {stale_count} (no transition in >48h)
  Unassigned: {unassigned_count}
  Check: data/coordination/verification/rollups/stale_items.json
```

### 4.2 Session-End Write

Every agent MUST record verification progress at session end:

```bash
# Proposed Make target
make verify-close session="<YYYYMMDD>" actor="<name>"
```

This:
1. Scans all ver items where `current_holder: {actor}` was modified this session
2. Prompts for any state transitions not yet recorded
3. Updates `updated_at` on each modified item
4. Appends audit trail entries
5. Regenerates rollup files

If an agent completed work but didn't update any ver items, the session-end
check logs a warning:
```
⚠️  Session produced no verification transitions.
   Did you consume any knowledge signals? If so, create ver items.
```

**Implementation**: `scripts/verify_close.py`

### 4.3 Make Commands

Add to `Makefile` under a new section `# ⛓️ KNOWLEDGE VERIFICATION`:

| Command | Description |
|---------|-------------|
| `make verify-pending` | Show pending items for current actor/domain |
| `make verify-status` | Show aggregate fleet-wide verification status |
| `make verify-rollup [DOMAIN=x]` | Regenerate rollup files for all or one domain |
| `make verify-pending-signals` | Show knowledge signals without ver items |
| `make verify-check-audit [DATE=x]` | Show audit log for a date |
| `make verify-cleanup` | Move TTL-expired items to archive |
| `make verify-stale` | Show items not transitioned in >48h |
| `make verify-assign ACTOR=x ITEM=y` | Assign an unassigned item to an actor |
| `make verify-transition ITEM=y STATE=z` | Record a state transition (with confirmation) |

**Makefile snippet** (to be added):

```makefile
# ⛓️ KNOWLEDGE VERIFICATION
# ============================================================================

VERIFY_DIR := data/coordination/verification

verify-pending: guard ## 🔍 Show pending verification items
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_status.py --actor $(ACTOR)

verify-status: guard ## 📊 Show fleet-wide verification status
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " ⛓️  Verification Status — Fleet-Wide"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_NC)"
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_status.py --fleet

verify-rollup: guard ## 📊 Regenerate rollup files: make verify-rollup DOMAIN=engineering
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_rollup.py --domain $(DOMAIN)

verify-pending-signals: guard ## 📡 Show knowledge signals without ver items
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_pending_signals.py

verify-cleanup: guard ## 🧹 Archive TTL-expired verification items
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_cleanup.py

verify-stale: guard ## ⏰ Show stale items (no transition in >48h)
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) scripts/verify_status.py --stale-only
```

### 4.4 Git Hook Triggers

**`pre-commit` hook** (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
# 🔱 Omega Engine — Pre-Commit Verification Gate
# Automatically detects if any tracked engine files changed, and prompts for
# a verification item update if the change originated from mined knowledge.

VERIFY_DIR="data/coordination/verification"
CHANGED_FILES=$(git diff --cached --name-only)

# Check if any engine source files were modified
ENGINE_CHANGES=$(echo "$CHANGED_FILES" | grep -E '^src/omega/' || true)

if [ -n "$ENGINE_CHANGES" ]; then
    echo "🔍 Engine source files changed. Checking verification status..."
    echo "  Changed files:"
    echo "$ENGINE_CHANGES" | sed 's/^/    /'

    # Check for open ver items referencing these files
    for f in $ENGINE_CHANGES; do
        FOUND=$(find "$VERIFY_DIR/items/" -name '*.json' -exec grep -l "\"$f\"" {} \; 2>/dev/null)
        if [ -n "$FOUND" ]; then
            echo "  ⚠️  File tracked by verification item(s):"
            for vf in $FOUND; do
                VER_ID=$(basename "$vf" .json)
                STATE=$(python3 -c "import json; d=json.load(open('$vf')); print(d.get('state','unknown'))")
                echo "    - $VER_ID (current state: $STATE)"
            done
        fi
    done

    echo "  Tip: run 'make verify-pending' to review open items."
    echo ""
fi

exit 0
```

**`prepare-commit-msg` hook** (`.git/hooks/prepare-commit-msg`):

```bash
#!/bin/bash
# Appends verification item references to commit message if applicable
COMMIT_MSG_FILE=$1
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# If commit message already has content, skip
if [ -s "$COMMIT_MSG_FILE" ]; then
    exit 0
fi

# Check for in-progress verification items on this branch
for item in data/coordination/verification/items/*.json; do
    [ -f "$item" ] || continue
    STATE=$(python3 -c "import json; d=json.load(open('$item')); print(d.get('state',''))" 2>/dev/null)
    TITLE=$(python3 -c "import json; d=json.load(open('$item')); print(d.get('title',''))" 2>/dev/null)
    VER_ID=$(basename "$item" .json)

    if [ "$STATE" = "PORTED" ] || [ "$STATE" = "TESTED" ]; then
        echo "[verification: $VER_ID] $TITLE" >> "$COMMIT_MSG_FILE"
        echo "" >> "$COMMIT_MSG_FILE"
        echo "Verification tracking: $VER_ID (state: $STATE)" >> "$COMMIT_MSG_FILE"
        echo "" >> "$COMMIT_MSG_FILE"
        exit 0
    fi
done
```

### 4.5 Automated Triggers

| Trigger | Event | Action |
|---------|-------|--------|
| Knowledge signal consumed | `consumed_by` field gets first entry | Auto-create `ver-*` in DISCOVERED state |
| Git commit touching `src/omega/` | Post-commit hook | Check if commit hash matches any ver item; if ver item exists and state=PORTED, suggest transition to TESTED |
| `make test` passed | Exit code 0 | If a ver item exists for any file in the changed set, prompt: "Transition to TESTED?" |
| `make temple-grade` passed | Exit code 0 | If a ver item exists in TESTED state, prompt: "Transition to VERIFIED?" |
| Git tag pushed | Post-commit hook | If a ver item exists in VERIFIED state, prompt: "Transition to DEPLOYED?" |
| Daily cron | 00:00 UTC | Run `make verify-cleanup` + `make verify-rollup` + post stale items to live feed |

---

## §5 — TTL & CLEANUP POLICY

### 5.1 Per-Item TTLs (from `created_at`)

| State | TTL | Action at Expiry |
|-------|-----|------------------|
| `DISCOVERED` | 7 days | Flag as stale, escalate to oversoul, auto-archive after 14d |
| `PORTED` | 14 days | Flag as stale, ping `current_holder`, auto-archive after 30d |
| `TESTED` | 30 days | Flag as stale, ping `current_holder`, auto-archive after 60d |
| `VERIFIED` | 90 days | Roll into monthly summary, archive after 90d |
| `DEPLOYED` | 180 days | Roll into quarterly summary, archive after 180d |
| `LIVE` | 365 days | Roll into annual summary, archive after 365d |

### 5.2 Archive Pipeline

```
                    ┌──────────────────────┐
                    │   items/ver-*.json   │
                    └──────┬───────────────┘
                           │ TTL expired
                           ▼
                    ┌──────────────────────┐
                    │  Compress to archive  │
                    │  items/ver-*.json.gz │
                    └──────┬───────────────┘
                           │ Quarterly
                           ▼
                    ┌──────────────────────┐
                    │  Delete from archive │
                    │  (beyond 2y retention)│
                    └──────────────────────┘
```

**Archive script** (`scripts/verify_cleanup.py`) logic:

1. Scan all items in `items/`
2. For each item where `ttl.archive_at < now` and state ≥ `ttl.auto_archive_state`:
   a. Append final audit entry marking archival
   b. `gzip` the item file
   c. Move to `archive/items/` with timestamp suffix
   d. Update rollup to remove archived item
3. For items where state < `ttl.auto_archive_state` but TTL breached + GRACE:
   a. Write to `stale_items.json` rollup
   b. Post to oversoul's live feed: `⚠️ STALE VERIFICATION ITEM: {ver_id} ({title})`

### 5.3 Retention Policy

| Data | Retention | Permanence |
|------|-----------|------------|
| Active items (`items/`) | Until archived | Not permanent |
| Audit logs (`audit/`) | 1 year online, then compressed | 3 years total |
| Rollups (`rollups/`) | 90 days online, then archived | 2 years total |
| Archived items (`archive/items/`) | 2 years | Permanently deleted after 2y |
| Archived rollups (`archive/rollups/`) | 5 years | Summary data retained |
| Archived audit (`archive/audit/`) | 3 years | Permanently deleted after 3y |

### 5.4 Cleanup Schedule

| Frequency | Action | Command |
|-----------|--------|---------|
| Daily (00:00 UTC) | Archive TTL-expired items | `make verify-cleanup` |
| Daily | Regenerate stale-items rollup | `make verify-rollup DOMAIN=stale` |
| Weekly | Regenerate all domain rollups | `make verify-rollup` |
| Monthly | Compress previous month's audit log | `scripts/verify_compress_audit.sh` |
| Quarterly | Purge archived items > 2 years | Manual via `scripts/verify_purge_archive.sh` |

---

## §6 — INTEGRATION WITH EXISTING SYSTEMS

### 6.1 Knowledge Feed Integration

When a knowledge signal (`ksig-*`) gets its first consumer (a `consumed_by` entry
is appended), the verification system auto-creates a ver item:

```
KSIG consumed_by populated
  │
  ▼
Auto-create: items/ver-YYYYMMDD-NNN.json (state: DISCOVERED)
  │
  ▼
Append to audit: {type: "creation", source: "ksig-<id>"}
  │
  ▼
Regenerate cross_pollination.json rollup
```

**Implementation note**: The auto-creation can be done by:
- A Python script called from the `omega-hub` MCP when `consumed_by` is updated
- A daily scan via `make verify-pending-signals`
- A manual trigger: `make verify-create-from-signal SIG=ksig-20260603-001`

### 6.2 Demand Signal Integration

When a demand signal (`dem-*`) is fulfilled (`fulfilled_by` populated), the
fulfilling agent SHOULD create a ver item:

```json
{
  "ver_id": "ver-20260604-003",
  "source_refs": [{"type": "demand_signal", "id": "dem-20260603-001"}],
  "state": "DISCOVERED",
  "classification": "research",
  "current_holder": "roc_racoon"
}
```

### 6.3 Entity soul.yaml Integration

When an item reaches `VERIFIED` state, its insights should be distilled into
the entity's `soul.yaml`:

```yaml
# In data/entities/doom_guy/soul.yaml

lessons:
  - id: ls-dg-20260604-001
    source_verification_item: "ver-20260604-001"
    l1_narrative: "Ported Doom BSP culling to circuit breaker pre-check"
    l2_insight: "O(1) provider skip via breaker state is equivalent to BSP plane culling"
    l3_principle: "The right approximation for the problem is better than the exact solution you can't afford"
```

This mirrors the L1→L2→L3 distillation pipeline (P7 design) and ensures
soul.yaml entries are traceable back to their verification items.

### 6.4 Live Feed Integration

Every significant verification event is posted to the oversoul's live feed:

```
# In data/coordination/MAAT_LIVE_FEED.md

[2026-06-04 14:30] VERIFICATION — ver-20260604-001 PORTED by doom_guy (BSP culling)
[2026-06-04 15:00] VERIFICATION — ver-20260604-001 TESTED (307/307 passed)
[2026-06-04 16:00] VERIFICATION — ver-20260604-001 DEPLOYED by maat (tag v1.2.0-bsp-port)
[2026-06-04 16:30] VERIFICATION — ver-20260604-002 CREATED (WAD entity overrides, state=PORTED)
```

---

## §7 — INITIAL SEED DATA

On creation of the verification layer, seed it with all existing knowledge
signals and demand signals that are already in play:

### 7.1 Seed from KSIG-001

```json
{
  "ver_id": "ver-20260604-001",
  "title": "Lily Pad Knowledge Metabolism Architecture Implementation",
  "domain": "infrastructure",
  "classification": "feature",
  "source_refs": [{"type": "knowledge_signal", "id": "ksig-20260603-lilith-001"}],
  "state": "DISCOVERED",
  "history": [],
  "current_holder": null,
  "ttl": {"state_ttl_days": 14, "archive_at": "2026-06-18T00:00:00Z", "auto_archive_state": "DEPLOYED"},
  "zoneid": 1912619,
  "tags": ["knowledge-metabolism", "lily-pad", "infrastructure"]
}
```

### 7.2 Seed from Demand Signals

Create one ver item per open demand signal:

| Demand Signal | ver-* ID | Domain | Classification |
|---------------|----------|--------|----------------|
| dem-20260603-001 (Roc feedback loop) | ver-20260604-002 | mining | research |
| dem-20260603-002 (knowledge TTL enforcement) | ver-20260604-003 | infrastructure | feature |
| dem-20260603-003 (cross-pollination metrics) | ver-20260604-004 | observability | feature |
| dem-20260603-004 (mining priority system) | ver-20260604-005 | mining | feature |
| dem-20260603-005 (soul consumption tracking) | ver-20260604-006 | infrastructure | feature |
| dem-20260603-006 (link P9 handoff docs) | ver-20260604-007 | documentation | doc_port |

---

## §8 — IMPLEMENTATION PLAN

### Phase 1: Bootstrap (This Session)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 1.1 | Create directory structure | P1 | `data/coordination/verification/` with all subdirs |
| 1.2 | Create README.md in verification dir | P1 | Self-documenting reference |
| 1.3 | Create seed items (7 items from §7) | P1 | `items/ver-20260604-001` through `-007` |
| 1.4 | Create initial fleet-wide rollup | P1 | `rollups/fleet_wide.json` |
| 1.5 | Create today's audit log | P1 | `audit/2026-06-04.jsonl` with seed entries |
| 1.6 | Present to Ma'at for ratification | P1 | Approval gate |

### Phase 2: Makefile Integration (Next Session)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 2.1 | Add `verify-pending` target | P1 | Make target |
| 2.2 | Add `verify-status` + `verify-rollup` targets | P1 | Make targets |
| 2.3 | Add `verify-cleanup` + `verify-stale` targets | P1 | Make targets |
| 2.4 | Create `scripts/verify_status.py` | P3 | Python script |
| 2.5 | Create `scripts/verify_rollup.py` | P3 | Python script |
| 2.6 | Create `scripts/verify_cleanup.py` | P3 | Python script |

### Phase 3: Git Hooks (Next Session)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 3.1 | Create `.git/hooks/pre-commit` verification check | P1 | Hook script |
| 3.2 | Create `.git/hooks/prepare-commit-msg` ver item ref | P1 | Hook script |
| 3.3 | Install hooks via `make git-hooks-install` | P1 | Make target |
| 3.4 | Test hooks with engine code change | P3 | Verification |

### Phase 4: Auto-Creation from Knowledge Feed (H1)

| # | Task | Owner | Output |
|---|------|-------|--------|
| 4.1 | MCP server support: auto-create ver item on consumed_by update | P4 | MCP tool |
| 4.2 | Session-start auto-check for agents | P7 | System prompt template |
| 4.3 | Session-end auto-write for agents | P7 | System prompt template |
| 4.4 | soul.yaml ↔ ver item linkage | P7 | Distillation convention |

---

## §9 — FAILURE MODES & RECOVERY

| Failure Mode | Detection | Recovery |
|-------------|-----------|----------|
| `items/` has orphans (created but never transitioned) | `make verify-stale` shows items >48h without transition | Ping `current_holder` via live feed; escalate to oversoul after 7d |
| `items/` missing for consumed knowledge signal | `make verify-pending-signals` shows ksig with consumed_by but no ver item | Auto-create in DISCOVERED state |
| Audit log gaps (missing transitions in `history[]`) | `verify_status.py --audit-gap-detection` compares item history to audit file | Rebuild history from audit log |
| Rollup diverges from items | `verify_rollup.py --validate` checks item count + state agg match | Regenerate rollup (idempotent) |
| TTL misconfigured (archive_at in past at creation) | `verify_cleanup.py --dry-run` flags invalid TTLs | Force `archive_at = created_at + state_ttl_days` |
| Concurrent modification (two agents updating same item) | `history[]` append races | Last-writer-wins by `updated_at`; always append to `history[]`, never overwrite |

---

## §10 — ZONEID REGISTRY

Per the [ZONEID Pattern: id Software 1993] heritage mapping, the verification
layer uses:

| Constant | Value | Subsystem | File |
|----------|-------|-----------|------|
| `ZONEID_VERIFICATION` | `0x1d4a19` | Verification items | `src/omega/constants.py` |
| `ZONEID_ROLLUP` | `0x1d4a1a` | Rollup files | `src/omega/constants.py` |
| `ZONEID_AUDIT` | `0x1d4a1b` | Audit trail | `src/omega/constants.py` |

These should be added to `cvar_table.py` and `constants.py` in the Zone Registry
section alongside the existing ZONEID_MEMORY (0x1d4a11) through ZONEID_PRESENCE
(0x1d4a17) constants.

---

## §11 — SUMMARY

```
VERIFICATION LAYER — 7 Designing Principles
══════════════════════════════════════════════

 1. Every mined insight gets a ver item     ── No orphan knowledge
 2. Every port gets tracked through states   ── MINED → LIVE
 3. Every transition gets audited            ── Immutable log
 4. Every domain gets a rollup               ── Aggregate view
 5. Every item gets a TTL                    ── No infinite clutter
 6. Every git change gets checked            ── Pre-commit gate
 7. Every session starts/ends with ver check ── Habit formation
```

---

*⬡ OMEGA ⬡ P1 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PHASE-I ⬡ INFRASTRUCTURE-DESIGN*
