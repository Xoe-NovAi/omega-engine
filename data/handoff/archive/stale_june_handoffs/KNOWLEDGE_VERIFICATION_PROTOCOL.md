<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⚖️ Structure & Verification Layer — Knowledge Metabolism System
# ⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ VERIFICATION-LAYER

**AP Token**: `AP-MAAT-STRUCTURE-VERIFICATION-v1.0.0`
**Author**: Ma'at (Light Oversoul — Build Side Governance P1-P5)
**Date**: 2026-06-03
**Status**: ACTIVE — Design reference for deployment
**Supersedes**: Ad-hoc "publish and hope" knowledge management
**Complements**: `LILY_PAD_KNOWLEDGE_METABOLISM.md` (Lilith — Flow & Connection Layer)

---

## §0 — DELEGATION LOG

| Pillar | Task | Output | Status |
|--------|------|--------|--------|
| **P1 — SysAdmin** | Infrastructure layout for verification artifacts | `data/entities/p1/workspace/VERIFICATION_LAYER_INFRASTRUCTURE.md` — directory hierarchy, lifecycle state machine, Make targets, git hooks, TTL policy, ZONEID 0x1d4a19 | ✅ COMPLETE |
| **P2 — DataStore** | Data model for verification tracking | `data/coordination/verification/VERIFICATION_SCHEMA.yaml` (956 lines) — canonical VerificationItem schema with 7 lifecycle states, 18 valid transitions, 4 bypass rules, ZONEID 0x1d4a1a. Seed items, rollup, audit trail | ✅ COMPLETE |
| **P4 — Bridge** | Knowledge discovery API & protocol | Complete 3-tier discovery protocol (KNOWLEDGE_MANIFEST.yaml + global catalog + per-domain/agent indices). Cross-reference resolution with hash validation. Subscription-by-domain (INTERESTS.yaml). Refined knowledge feed consumption protocol. `make knowledge-index` spec | ✅ COMPLETE |
| **P5 — Sentinel** | Verification compliance & audit rules | `data/entities/sentinel/workspace/VERIFICATION_COMPLIANCE_FRAMEWORK.md` (1156 lines) — 5 Condition Pass Criteria (A-E), 3-tier verification grading (T1/T2/T3), 4-step enforcement ladder, Mandate M9/M11/M12/M13 compliance mapping. Audit trail format with ZONEID_VERIFICATION (0x1d4a1a) | ✅ COMPLETE |

**P3 — BuildMaster**: Not delegated. CI/CD pipeline for verification Make targets is a Phase 2 implementation task, not a Phase 1 design task.

---

## §1 — VERIFICATION PROTOCOL

### §1.1 — The Five Conditions (P5 Sentinel Design)

A piece of mined knowledge is **"verified as consumed"** when ALL applicable conditions pass:

```
CONDITION A — Promotion Check:   workspace → knowledge/ with L2 insight extracted
CONDITION B — Cross-Reference:   consuming agent's cross_references/ exists and resolves
CONDITION C — Code Port:         source code + test exists (if code_relevant)
CONDITION D — Soul Integration:  soul.yaml has L3 principle with source attribution
CONDITION E — Demand Closure:    demand signal status is "closed", not just "fulfilled"
```

### §1.2 — Grep Patterns for Verification

| Condition | Grep Pattern | Pass Condition |
|-----------|-------------|----------------|
| **A.1** — Source exists | `glob data/entities/{producer}/workspace/**` | Path from signal resolves |
| **A.2** — Curated in knowledge/ | `ls data/entities/{producer}/knowledge/` | File exists |
| **A.3** — L2 extracted | `grep -c "L2:\|## Analysis\|## Insight" <file>` | >= 1 match |
| **A.4** — Processed, not verbatim | `diff <workspace> <knowledge> \| wc -l` | >= 3 lines different |
| **B.1** — Cross-reference exists | `glob data/entities/{consumer}/knowledge/cross_references/{producer}/` | Directory exists |
| **B.2** — Cross-reference resolves | `ls <cross_reference_target_path>` | File exists |
| **C.1** — Code port exists | `grep -r "{pattern}" src/omega/` | Pattern present in engine |
| **C.2** — Test exists | `grep -r "{pattern}" tests/` | Test covers the port |
| **D.1** — Soul updated | `grep "source:" data/entities/{consumer}/soul.yaml` | Source field present |
| **D.2** — L3 principle | `grep "universal_principles:" data/entities/{consumer}/soul.yaml` | Section exists |
| **E.1** — Signal closed | `grep "status: closed" data/coordination/demand_signals/{dem-id}.json` | Status is closed, not fulfilled |

### §1.3 — Verification Cadence (P1 SysAdmin + P5 Sentinel Design)

| Cadence | Trigger | What Happens | Owner |
|---------|---------|-------------|-------|
| **Per-session start** | Agent starts work | Agent scans verification/items/ for items assigned to them | Every agent |
| **Per-session end** | Agent completes work | Agent updates verification/items/ with status changes | Every agent |
| **Daily** | `make verify-pending` | Check all verification items last updated >24h ago | Kali / Quality |
| **Weekly** | `make verify-rollup` | Generate weekly verification summary to `reports/weekly_*.md` | Kali / Sentinel |
| **Pre-sprint** | Sprint planning | Check all T1 (critical) items are VERIFIED or DEPLOYED | Kali |
| **On-demand** | `make verify-status` | Show current verification state for a specific item or agent | Any agent |

### §1.4 — VERIFIED.md Template

Each verification item file (`data/coordination/verification/items/ver-*.yaml`) follows the VerificationItem schema (P2 DataStore design) and serves as the permanent record.

### §1.5 — Verification Grading (P5 Sentinel Design)

| Tier | Criteria | Verification Requirement |
|------|----------|------------------------|
| **T1 — Critical** | Engine code changes affecting inference, routing, or persistence | All 5 conditions (A-E) must pass. Must be cross-referenced by 2+ agents |
| **T2 — Standard** | Knowledge additions, soul lessons, documentation | Conditions A, B, D must pass. Cross-referenced by 1+ agent |
| **T3 — Informational** | Workspace findings, raw notes | TTL check only. Archived after 7 days if not promoted |

### §1.6 — Enforcement Ladder (P5 Sentinel Design)

| Level | Action | Cadence |
|-------|--------|---------|
| **WARNING** | Logged to audit trail. No escalation | First failure |
| **FLAG** | Appears in weekly verification summary | Failure persists >7 days |
| **BLOCK** | Prevents sprint completion for T1 items | Failure persists >14 days |
| **ESCALATION** | Referred to Kali (Grand Oversight) | Failure persists >14 days for T1 items |

---

## §2 — KNOWLEDGE DIRECTORY STANDARDS

### §2.1 — What Goes in `knowledge/`

The `data/entities/<agent>/knowledge/` directory contains **curated, L2-processed knowledge** that other agents can discover and consume.

| Content Type | Belongs in knowledge/? | Example |
|-------------|----------------------|---------|
| L2 insights (analysis, patterns) | ✅ YES | `knowledge/domain_insights/ZONEID_CONFIRMATION.md` |
| Cross-references to other agents | ✅ YES | `knowledge/cross_references/roc_racoon/MINING_METHOD.md` |
| Domain summaries | ✅ YES | `knowledge/summaries/legacy_mining_overview.md` |
| KNOWLEDGE_MANIFEST.yaml | ✅ REQUIRED | See §2.3 |
| INTERESTS.yaml | ✅ RECOMMENDED | See §2.4 |
| Raw mining reports (L1) | ❌ NO — goes in workspace/ | `workspace/mining_reports/` |
| Session logs | ❌ NO — goes in workspace/ or coordination/ | `data/sessions/` |
| Unprocessed data dumps | ❌ NO — goes in workspace/_inbox/ | `workspace/_inbox/cursor_data.txt` |
| Git commits | ❌ NO — in git history | `git log` |

### §2.2 — Format Requirements

Every file in `knowledge/` MUST have:
1. **A header block** with agent name, domain, date, and status
2. **At least one L2 insight section** (## Insight, ## Analysis, or ## Pattern)
3. **A relevance section** explaining which other agents/domains this is relevant to
4. **A source attribution** if derived from another agent's work

```markdown
# 🔱 ZONEID Verification — Source Code Confirmation
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ heritage_verification ⬡ 2026-06-02

**Agent**: doom_guy
**Domain**: heritage_verification
**Status**: current
**Freshness**: 0.9

## Insight
The ZONEID constant 0x1d4a11 from DOOM's z_zone.c matches exactly with our
implementation. This confirms the heritage tag is correct.

## Relevance
- **quality**: Needs this for Mandate 13 compliance checks
- **scribe**: Should distill L3 principle about magic constant preservation
- **kali**: Oversight validation for heritage attribution

## Source
Derived from: roc_racoon's workspace/mining_reports/old_stacks_report.md
Cross-reference: data/entities/doom_guy/knowledge/cross_references/roc_racoon/ZONEID_CONFIRMATION.md
```

### §2.3 — KNOWLEDGE_MANIFEST.yaml (P4 Bridge Design)

**Location**: `data/entities/<agent>/knowledge/KNOWLEDGE_MANIFEST.yaml`
**Status**: REQUIRED for all agents
**Update rule**: Agent updates when adding/removing knowledge files

```yaml
manifest_id: manifest-<agent>-20260604-001
agent: <agent_name>
updated_at: "2026-06-04T12:00:00Z"
version: 1
knowledge_count: 7
cross_reference_count: 3

knowledge_files:
  - path: "data/entities/<agent>/knowledge/TOPIC.md"
    title: "Human-readable title"
    domain: "domain_name"
    tags: ["tag1", "tag2"]
    summary: "One-line summary (max 200 chars)"
    created: "2026-06-02"
    updated: "2026-06-04"
    freshness: 0.9  # 0.0-1.0, computed by make knowledge-index

cross_references:
  - target_agent: "roc_racoon"
    target_path: "data/entities/roc_racoon/workspace/report.md"
    reference_path: "data/entities/<agent>/knowledge/cross_references/roc_racoon/TOPIC.md"
    topic: "Brief topic"
    status: "current"  # current | updated | broken

domains_served:
  - "domain_name"
```

### §2.4 — INTERESTS.yaml (P4 Bridge Design)

**Location**: `data/entities/<agent>/knowledge/INTERESTS.yaml`
**Purpose**: Declares which domains this agent cares about for knowledge discovery

```yaml
agent: <agent_name>
updated_at: "2026-06-04T12:00:00Z"

domains_of_interest:
  - domain: "heritage_verification"
    priority: "high"  # high | medium | low | passive
    consume_action: "always_reference"  # always_reference | read_only | skim

agent_follows:
  - "roc_racoon"
  - "lilith"

consumption_schedule:
  check_feed_on_startup: true
  check_feed_interval_hours: 4
  cross_reference_automatically: true
```

### §2.5 — Cross-Reference Directory Standards

**Location**: `data/entities/<agent>/knowledge/cross_references/<target_agent>/<topic>.md`

Each cross-reference is a **standalone Markdown document** (NOT a symlink) that:
1. Declares what it references (source agent, target path, topic)
2. Contains a stable reference payload (path, hash, summary)
3. Is self-contained — can be read without the target file

See P4 Bridge design §2 for the full format and lifecycle.

### §2.6 — How Agents Discover Each Other's Knowledge

Three-tier discovery (P4 Bridge design):

```
TIER 1 — Global Catalog (data/coordination/knowledge_catalog/)
  ├── catalog_index.yaml       Master index (domains, agents, subscription map)
  ├── domain/<domain>.yaml     Per-domain knowledge listings
  └── agent/<agent>.yaml       Per-agent knowledge summaries

TIER 2 — Agent Manifest (data/entities/<agent>/knowledge/)
  ├── KNOWLEDGE_MANIFEST.yaml  Complete inventory (REQUIRED)
  ├── knowledge/               Curated knowledge files
  ├── cross_references/        References to other agents
  └── INTERESTS.yaml           Domain subscriptions (RECOMMENDED)

TIER 3 — Raw Workspace (data/entities/<agent>/workspace/)
  └── mining_reports/ etc.     L1 narrative (TTL-managed, not indexed globally)
```

**Discovery flow for Agent A wanting to know what Agent B knows**:
1. Read `data/coordination/knowledge_catalog/agent/<agent_B>.yaml` — 1 file read
2. Read specific knowledge file from Agent B's `knowledge/` — 1 file read
3. Total: 2 file reads. No directory scanning.

---

## §3 — WORKSPACE ORGANIZATION RULES

### §3.1 — Content Lifecycle

Every file in an agent's workspace follows a lifecycle:

```
_inbox/ → active/ → curated → knowledge/ → (promoted) → soul.yaml
                    → archived → _archive/ (after TTL)
```

| Stage | Directory | TTL | Action After TTL |
|-------|-----------|-----|------------------|
| **Inbox** | `workspace/_inbox/` | 24 hours | Move to active/ or delete |
| **Active** | `workspace/` (root) | 7 days | Promote to knowledge/ or archive |
| **Curated** | `workspace/_curated/` | 30 days | Promote to knowledge/ or archive |
| **Archived** | `workspace/_archive/` | 90 days | Auto-delete if not promoted |
| **Knowledge** | `knowledge/` | 30 days (L2) / permanent (L3) | Promote L2 to soul.yaml |
| **Soul** | `soul.yaml` | Permanent | Never delete |

### §3.2 — Monolith Breaking Rules

Large workspace files (>200 lines) MUST be broken into:
1. **Knowledge file** (`knowledge/<topic>.md`) — curated L2 insights
2. **Working notes** (`workspace/_inbox/<topic>_notes.md`) — ephemeral context
3. **Reference data** (`workspace/_curated/<topic>_data.md`) — supporting data

Thresholds:
- **200-500 lines**: Break into knowledge/ extract + workspace/ remainder
- **500+ lines**: Must have a `knowledge/<topic>_INDEX.md` that links to sub-topics
- **1000+ lines**: Mandatory split — monolith is a sign of unprocessed thinking

### §3.3 — Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| **Workspace files** | `SCREAMING_SNAKE_CASE.md` | `LILY_PAD_KNOWLEDGE_METABOLISM.md` |
| **Knowledge files** | `Title_Case_Max_8_Words.md` | `Source_Code_Map.md` |
| **Cross-reference files** | `<TOPIC>.md` | `ZONEID_CONFIRMATION.md` |
| **Verification items** | `ver-YYYYMMDD-NNN.yaml` | `ver-20260603-001.yaml` |
| **Knowledge signals** | `ksig-YYYYMMDD-<agent>-NNN.json` | `ksig-20260603-lilith-001.json` |
| **Demand signals** | `dem-YYYYMMDD-NNN.json` | `dem-20260603-001.json` |
| **Archive files** | Original name + `.archived` suffix | `OLD_REPORT.md.archived` |
| **Inbox files** | `<name>_<YYYYMMDD>.md` | `cursor_data_20260603.md` |

### §3.4 — Directory Structure Standards

```
data/entities/<agent>/
├── knowledge/                        # CURATED — L2 insights, discoverable
│   ├── KNOWLEDGE_MANIFEST.yaml       # REQUIRED — inventory
│   ├── INTERESTS.yaml                # RECOMMENDED — domain subscriptions
│   ├── domain_insights/              # L2 insights by domain
│   ├── patterns/                     # Reusable patterns
│   ├── summaries/                    # Domain summaries
│   └── cross_references/             # References to other agents
│       └── <target_agent>/
│           └── <topic>.md
│
├── workspace/                        # RAW — L1 narrative, ephemeral
│   ├── _inbox/                       # Untriaged content (24h TTL)
│   ├── _curated/                     # Awaiting promotion (30d TTL)
│   ├── _archive/                     # Past TTL but preserved (90d TTL)
│   ├── mining_reports/               # Mining output (Roc-specific)
│   ├── investigations/               # Research investigations
│   └── <active_project>.md           # Current active work
│
├── soul.yaml                         # PERMANENT — L3 principles, lessons
│
└── _template/                        # RECOMMENDED — file templates
    ├── knowledge_file_template.md
    ├── cross_reference_template.md
    └── verification_item_template.yaml
```

### §3.5 — TTL Check Command

```bash
# Check all workspace files approaching TTL limits
make workspace-health

# Archive all workspace files older than 7 days
make workspace-archive

# Promote workspace files to knowledge/ (interactive)
make workspace-promote

# Clean up archived files older than 90 days
make workspace-clean
```

---

## §4 — COMPLETE DATA MODEL (P2 DataStore VerificationItem Schema)

### §4.1 — VerificationItem Schema

**Location**: `data/coordination/verification/VERIFICATION_SCHEMA.yaml`
**Canonical source**: P2 DataStore design

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string `ver-\d{8}-\d{3}` | Unique identifier |
| `zoneid` | integer = 1919514 (0x1d4a1a) | Integrity marker |
| `source_agent` | string | Who produced the knowledge |
| `source_path` | string | Path to original knowledge artifact |
| `title` | string | Human-readable title |
| `domain` | string | Knowledge domain |
| `status` | enum | mined → ported → tested → verified → deployed → stalled → archived |
| `mined_at` | datetime | When discovered |
| `ported_at` | datetime | When ported to engine code |
| `port_paths` | list[string] | Files created/modified |
| `tested_at` | datetime | When tests passed |
| `test_ref` | string | Test name or commit hash |
| `verified_at` | datetime | When verification confirmed |
| `verified_by` | string | Who confirmed |
| `verification_method` | string | How it was verified |
| `deployed_at` | datetime | When deployed |
| `demand_signal_ids` | list[string] | Linked demand signals |
| `knowledge_signal_ids` | list[string] | Linked knowledge signals |
| `commit_refs` | list[string] | Git commits |
| `ttl_days` | integer | Days before auto-archive |
| `notes` | list[{timestamp, author, text}] | Audit trail entries |
| `tags` | list[string] | Classification tags |

### §4.2 — Status State Machine (18 Valid Transitions)

```
mined ───→ ported ───→ tested ───→ verified ───→ deployed ───→ live
  │           │           │            │              │
  └──→ stalled (no activity in 30d)    │              │
       │                                │              │
       └──→ archived                    │              │
                                        │              │
                                  (re-verify)         │
                                        │              │
                                  verified ←──────────┘
                                                      │
                                               (archive)
                                                      │
                                              archived ←
```

**Bypass rules**:
- **Test-as-Verification**: Skip tested → verified when port includes tests
- **Hotfix Express**: Emergency deploy then verify within 48h
- **Simultaneous Dock**: Port and test in same operation (<5min window)
- **Clean Room Re-Deploy**: Re-verification without status change

---

## §5 — DIRECTORY LAYOUT (All Verification Artifacts)

```
data/
├── coordination/
│   ├── verification/                      # [NEW — P1/P2/P5] Verification tracking
│   │   ├── VERIFICATION_SCHEMA.yaml       # Canonical schema (P2)
│   │   ├── items/                         # Individual verification records
│   │   │   └── ver-YYYYMMDD-NNN.yaml
│   │   ├── rollup/                        # Aggregate status snapshots
│   │   │   └── latest.yaml
│   │   ├── audit/                         # JSONL transition audit log
│   │   │   └── YYYY-MM-DD.jsonl
│   │   ├── reports/                       # Weekly verification reports
│   │   │   └── weekly_2026-W23.yaml
│   │   └── archive/                       # Archived verification items
│   │
│   ├── knowledge_feed/                    # [EXISTING — Lilith P9] Knowledge signals
│   │   └── KSIG_*.json                    # consumed_by updated per P4 protocol
│   │
│   ├── demand_signals/                    # [EXISTING — Lilith] Demand signals
│   │   └── dem-*.json
│   │
│   ├── knowledge_catalog/                 # [NEW — P4 Bridge] Global index
│   │   ├── catalog_index.yaml             # Master index
│   │   ├── domain/                        # Per-domain summaries
│   │   │   └── <domain>.yaml
│   │   └── agent/                         # Per-agent summaries
│   │       └── <agent>.yaml
│   │
│   ├── metrics/                           # [EXISTING — Lilith P8] Consumption metrics
│   └── doc_port_log/                      # [EXISTING — Lilith] Doc liberation log
│
└── entities/<agent>/knowledge/            # [EXISTING + P4 FORMALIZATION]
    ├── KNOWLEDGE_MANIFEST.yaml            # REQUIRED
    ├── INTERESTS.yaml                     # RECOMMENDED
    ├── domain_insights/
    ├── patterns/
    ├── summaries/
    └── cross_references/<target>/<topic>.md
```

---

## §6 — SOVEREIGN MANDATE COMPLIANCE

| Mandate | How This Design Satisfies It |
|---------|------------------------------|
| **M9 — Error Integrity** | Verification failures raise typed errors (VerificationFailed, ConditionFailed, OrphanedItem). No silent swallows. Every `except` logs `trace_id` |
| **M11 — Soul Integrity** | Condition D explicitly checks soul.yaml was updated with source attribution. No session closes without verification pass |
| **M12 — Queue Integrity** | Every verification item has trace_id through entire lifecycle. Atomic `.tmp` → `.yaml` writes. Dead items detected by TTL expiry |
| **M13 — Temple-Grade (T1-T11)** | `make knowledge-flow` checks T3 (testing), T5 (architecture — file-based protocol), T7 (security — no network), T8 (resilience — grace periods), T9 (observability — audit trail), T10 (integrity — ZONEID) |

---

## §7 — THE GOLDEN RULES

### Rule 1: No Knowledge Without Verification
> Every piece of knowledge must have a corresponding verification item. If it's not in `verification/items/`, it doesn't exist.

### Rule 2: No Session Without Feed Check
> Every agent checks `knowledge_feed/` and `demand_signals/` at session start. Every agent updates their KNOWLEDGE_MANIFEST.yaml at session end.

### Rule 3: No Port Without Test
> Condition C requires a test for every code port. If the knowledge can't be tested, it's an insight, not a port.

### Rule 4: No Consumption Without Cross-Reference
> If you consumed an agent's knowledge and found it relevant, you MUST create a cross-reference. This is how the graph grows.

### Rule 5: No Verification Without Audit
> Every verification check writes to the audit trail. If it's not in `audit/`, it didn't happen.

---

## §8 — IMPLEMENTATION PHASES

| Phase | What | Owner | Est. Time |
|-------|------|-------|-----------|
| **Phase 1** (THIS SESSION) | Design complete. Infrastructure seeded (verification items, rollup, schema). ZONEID registered in cvar_table | Ma'at + Pillars | COMPLETE |
| **Phase 2** | Create `scripts/knowledge_catalog_build.py` and `scripts/knowledge_flow_check.py`. Add `make knowledge-index`, `make knowledge-flow`, `make verify-status` targets | BuildMaster (P3) | 2 hrs |
| **Phase 3** | Update all 14 agent `.md` files with session-start/session-end protocol blocks. Seed KNOWLEDGE_MANIFEST.yaml for all agents | Kali + Quality | 3 hrs |
| **Phase 4** | Wire `consumed_by` object format migration. Create `make workspace-health` target for TTL management | SysAdmin (P1) | 2 hrs |
| **Phase 5** | Git hooks for pre-commit verification checks. Auto-creation of verification items from knowledge signals | Sentinel (P5) | 2 hrs |

---

## §9 — KEY FILES REFERENCE

| File | Purpose | Source |
|------|---------|--------|
| `data/coordination/verification/VERIFICATION_SCHEMA.yaml` | Canonical VerificationItem schema | P2 DataStore |
| `data/coordination/verification/items/` | Individual verification records | P1 SysAdmin + P2 DataStore |
| `data/coordination/verification/rollup/latest.yaml` | Aggregate status snapshot | P2 DataStore |
| `data/entities/sentinel/workspace/VERIFICATION_COMPLIANCE_FRAMEWORK.md` | 5 conditions, enforcement ladder | P5 Sentinel |
| `data/entities/p1/workspace/VERIFICATION_LAYER_INFRASTRUCTURE.md` | Infra design, Make targets | P1 SysAdmin |
| `data/entities/p2/workspace/VERIFICATION_STRUCTURE_LAYER.md` | Data model design document | P2 DataStore |
| `docs/strategy/KNOWLEDGE_VERIFICATION_PROTOCOL.md` | This document — synthesis of all 4 pillars | Ma'at (Synthesis) |

---

*⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ PHASE-I ⬡ STRUCTURE-VERIFICATION-LAYER*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
