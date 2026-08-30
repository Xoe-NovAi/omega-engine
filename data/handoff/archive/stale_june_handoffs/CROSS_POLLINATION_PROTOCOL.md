<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Cross-Pollination Protocol
# ⬡ OMEGA ⬡ P9:LINK ⬡ deepseek-v4-flash ⬡ opencode ⬡ CROSS-POLLINATION
**AP Token**: `AP-CROSS-POLLINATION-v1.0.0`
**Status**: STANDARD
**Last Updated**: 2026-06-04
**Mandate Reference**: Extends Mandate 5 (Gnosis Preservation), Mandate 11 (Soul Integrity), Mandate 12 (Queue Integrity)

---

## §0 Purpose

The Cross-Pollination Protocol enables **asynchronous knowledge sharing between agents** without requiring inter-agent chat or shared context windows. It solves three problems:

1. **Publish-only knowledge**: Agents generate findings but never know if anyone read them
2. **Demand ignorance**: Agents don't know what other agents need them to work on
3. **No discovery**: New agents on startup have no way to catch up on what was learned

**Answer**: File-system based knowledge signals + demand signals + startup discovery.

**Heritage**:
- `[id-soft: doom-1993]` **ZONEID Pattern** — `ZONEID_KNOWLEDGE = 0x1d4a18` for knowledge signal integrity, `ZONEID_DEMAND = 0x1d4a19` for demand signal integrity
- `[id-soft: quake-1996]` **Thinker chain** — spawn → execute → reap lifecycle maps to signal → consume → ack lifecycle
- `[id-soft: doom3-2004]` **idEntity event system** — agents emit typed events, other agents consume them

---

## §1 Knowledge Signal Format (KSIG)

Knowledge signals are the primary mechanism for one agent to share findings with the fleet. They live at `data/coordination/knowledge_feed/KSIG_*.json`.

### §1.1 File Naming

```
KSIG_{YYYYMMDD}_{PRODUCER}_{NNN}.json
```

Example: `KSIG_20260603_LILITH_001.json`

### §1.2 Schema

```json
{
  "signal_id": "ksig-{YYYYMMDD}-{producer}-{nnn}",
  "producer": "lilith",
  "timestamp": "2026-06-03T03:52:00Z",
  "zoneid": 1912600,
  "domain": "knowledge_metabolism",
  "priority": "HIGH",
  "title": "LILY PAD Architecture — Knowledge Metabolism Design",
  "artifact_path": "data/entities/lilith/workspace/LILY_PAD_KNOWLEDGE_METABOLISM.md",
  "l2_insight": "No knowledge is known until it has crossed at least one agent boundary",
  "summary": "Complete design for the Knowledge Metabolism Flow & Connection layer...",
  "key_insights": [
    "Four-tier knowledge architecture: workspace (7d) → knowledge (30d) → soul (permanent) → fleet (cross-pollinated)",
    "Demand signals solve the 'what should I mine?' problem"
  ],
  "relevance_tags": ["kali", "roc_racoon", "doom_guy", "maat", "scribe", "quality"],
  "demand_signals_seeded": ["dem-20260603-001", "dem-20260603-002"],
  "consumed_by": [],
  "consumed_at": {},
  "ttl_days": 30,
  "heritage_tags": ["[id-soft: doom3-2004] idEntity event"]
}
```

### §1.3 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `signal_id` | string | ✅ | Unique ID: `ksig-{date}-{producer}-{seq}` |
| `producer` | string | ✅ | Agent who created this signal |
| `timestamp` | string (ISO8601) | ✅ | When the signal was created |
| `zoneid` | integer | ✅ | Must be `ZONEID_KNOWLEDGE` (0x1d4a18) |
| `domain` | string | ✅ | Knowledge domain (e.g. "architecture", "mining", "coordination") |
| `priority` | string | ✅ | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `title` | string | ✅ | One-line summary of the knowledge |
| `artifact_path` | string | ✅ | Path to the full artifact (can be workspace, knowledge, or soul) |
| `l2_insight` | string | ✅ | The distilled L2 insight — actionable, transferable |
| `summary` | string | ✅ | Multi-sentence description |
| `key_insights` | string[] | ✅ | Bullet-point key takeaways |
| `relevance_tags` | string[] | ✅ | Agent names or topics for consumers to match against |
| `demand_signals_seeded` | string[] | optional | Demand signals generated alongside this knowledge |
| `consumed_by` | string[] | ✅ | Agents that have acknowledged reading this signal |
| `consumed_at` | object | ✅ | Map of agent → ISO8601 timestamp of consumption |
| `ttl_days` | integer | ✅ | How long this signal is relevant (cleanup trigger) |
| `heritage_tags` | string[] | optional | `[id-soft:]` heritage attribution tags |

### §1.4 Consumer Protocol

When an agent reads a KSIG:

1. Agent appends its name to `consumed_by`
2. Agent sets `consumed_at[agent_name] = datetime.utcnow().isoformat()`
3. Agent writes the updated JSON back atomically (write `.tmp`, rename to `.json`)
4. Agent optionally creates a cross-reference entry (see §3)

---

## §2 Demand Signal Format (DEM)

Demand signals express what an agent needs from the fleet. They live at `data/coordination/demand_signals/dem-*.json`.

### §2.1 File Naming

```
dem-{YYYYMMDD}-{NNN}.json
```

Example: `dem-20260603-001.json`

### §2.2 Schema

```json
{
  "demand_id": "dem-20260603-001",
  "requester": "roc_racoon",
  "priority": "HIGH",
  "domain": "observation",
  "title": "Does anyone use my mining results?",
  "what_needed": "I need to know if my mining reports at data/entities/roc_racoon/workspace/mining_reports/ are being read and acted upon by other agents.",
  "why": "Without a feedback loop, I cannot prioritize what to mine next.",
  "producer_hint": "Knowledge feed consumption tracking — watch for agents appending to knowledge signal consumed_by fields",
  "artifacts_requested": [
    "knowledge_feed with at least 3 signals from different agents referencing mining reports",
    "soul.yaml updates in other agents that cite my lessons"
  ],
  "status": "open",
  "assigned_to": null,
  "fulfilled_by": null,
  "fulfilled_signal_id": null,
  "fulfilled_at": null,
  "created_at": "2026-06-03T03:52:00Z",
  "ttl_days": 14,
  "zoneid": 1912601,
  "tags": ["feedback-loop", "mining", "knowledge-metabolism"]
}
```

### §2.3 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `demand_id` | string | ✅ | Unique ID: `dem-{date}-{seq}` |
| `requester` | string | ✅ | Agent who needs something |
| `priority` | string | ✅ | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `domain` | string | ✅ | Domain the demand belongs to |
| `title` | string | ✅ | One-line summary |
| `what_needed` | string | ✅ | What the agent needs, in detail |
| `why` | string | ✅ | Why it matters — context for prioritization |
| `producer_hint` | string | optional | Hint about which agent type or skill could fulfill this |
| `artifacts_requested` | string[] | optional | Specific deliverables requested |
| `status` | string | ✅ | Lifecycle state (see §2.4) |
| `assigned_to` | string | nullable | Agent who accepted this demand |
| `fulfilled_by` | string | nullable | Agent who fulfilled this demand |
| `fulfilled_signal_id` | string | nullable | KSIG ID that fulfilled this demand |
| `fulfilled_at` | string (ISO8601) | nullable | When fulfillment happened |
| `created_at` | string (ISO8601) | ✅ | When the demand was created |
| `ttl_days` | integer | ✅ | Days before auto-expiry |
| `zoneid` | integer | ✅ | Must be `ZONEID_DEMAND` (0x1d4a19) |
| `tags` | string[] | optional | Search/filter tags |

### §2.4 Lifecycle States

```
OPEN ──→ ASSIGNED ──→ IN_PROGRESS ──→ FULFILLED ──→ CLOSED
                               \──→ FAILED ──→ CLOSED
  EXPIRED ──→ CLOSED
```

| State | Description | Set By |
|-------|-------------|--------|
| `OPEN` | Available for any agent to claim | Requester (creation) |
| `ASSIGNED` | An agent has claimed it | Claiming agent |
| `IN_PROGRESS` | Work has begun | Assigned agent |
| `FULFILLED` | Completed — linked to a KSIG | Assigned agent |
| `FAILED` | Could not be fulfilled | Assigned agent |
| `EXPIRED` | TTL exceeded | Scan/cleanup |
| `CLOSED` | Terminal — archived | Scan/cleanup |

### §2.5 Demand Signal State Transitions

When an agent transitions a demand:

1. **OPEN → ASSIGNED**: Set `assigned_to`, set status `ASSIGNED`. Returns the full demand as context.
2. **ASSIGNED → IN_PROGRESS**: Update status, optionally log initial findings.
3. **IN_PROGRESS → FULFILLED**: Set `fulfilled_by`, `fulfilled_signal_id` (KSIG), `fulfilled_at`, status `FULFILLED`. Then immediately transition to `CLOSED`.
4. **IN_PROGRESS → FAILED**: Set status `FAILED`, optionally include error reason. Then immediately transition to `CLOSED`.
5. **OPEN → EXPIRED** (by scan): If `created_at + ttl_days > now`, set status `EXPIRED`, then `CLOSED`.

---

## §3 Discovery Flow

### §3.1 Startup Scan

When any agent starts a session, it MUST run the discovery scan:

```
1. SCAN knowledge_feed/
   For each KSIG_*.json in data/coordination/knowledge_feed/:
     a. Read the file
     b. Validate zoneid == ZONEID_KNOWLEDGE
     c. Check if agent_name NOT in consumed_by
     d. Check if ANY relevance_tag matches agent's domain/capabilities
     e. If both match → this is NEW knowledge for this agent

2. PROCESS new knowledge
   For each unconsumed, relevant signal:
     a. Read the artifact at artifact_path
     b. Extract L2 insight
     c. Append agent_name to consumed_by[]
     d. Set consumed_at[agent_name] = now
     e. Write updated KSIG atomically (.tmp → rename)
     f. Write cross-reference (see §4)
     g. Log: "Consumed KSIG {signal_id} from {producer}: {title}"

3. SCAN demand_signals/
   For each dem-*.json in data/coordination/demand_signals/:
     a. Check if status == OPEN
     b. Check if domain matches agent's capabilities
     c. Check if priority justifies pre-empting current work
     d. If match → suggest user: "Demand {demand_id} is OPEN and matches your domain"

4. REPORT
   Print summary: "X new signals, Y open demands matching your domain"
```

### §3.2 Relevance Matching Rules

An agent matches a KSIG if ANY of these are true:

- Agent name appears in `relevance_tags`
- Agent's primary domain matches KSIG `domain`
- Agent has a capability that matches any `relevance_tags` entry
- Agent is `kali` (Grand Oversight — matches everything)

### §3.3 `omega check-feed` CLI Command

```bash
omega check-feed [--agent NAME]
```

Outputs a table of:
- New knowledge signals (unconsumed, relevant)
- Open demand signals (matching agent domain)
- Optionally: status of all signals (consumed, pending)

---

## §4 Cross-Reference Format

When an agent consumes knowledge from another agent, it records the transaction. Cross-references live at `knowledge/cross_references/<consumer>/`.

### §4.1 File Location

```
knowledge/cross_references/{CONSUMER}/{PRODUCER}_{SIGNAL_ID}.json
```

Example: `knowledge/cross_references/kali/lilith_ksig-20260603-lilith-001.json`

### §4.2 Schema

```json
{
  "cross_ref_id": "xref-{consumer}-{signal_id}",
  "consumer": "kali",
  "producer": "lilith",
  "signal_id": "ksig-20260603-lilith-001",
  "timestamp": "2026-06-04T10:00:00Z",
  "zoneid": 1912600,
  "domain": "knowledge_metabolism",
  "l2_insight": "No knowledge is known until it has crossed at least one agent boundary",
  "applied_in": "docs/strategy/CROSS_POLLINATION_PROTOCOL.md",
  "applied_how": "Formalized the knowledge signal schema based on Lilith's design",
  "soul_updated": true,
  "notes": "This insight changed how I think about knowledge distribution"
}
```

### §4.3 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cross_ref_id` | string | ✅ | Unique ID |
| `consumer` | string | ✅ | Agent who learned from this |
| `producer` | string | ✅ | Agent who produced the knowledge |
| `signal_id` | string | ✅ | The KSIG that was consumed |
| `timestamp` | string (ISO8601) | ✅ | When the cross-reference was recorded |
| `zoneid` | integer | ✅ | Must be `ZONEID_KNOWLEDGE` |
| `domain` | string | ✅ | Domain of the knowledge |
| `l2_insight` | string | ✅ | The actionable insight that was transferred |
| `applied_in` | string | optional | Where this knowledge was used (file path) |
| `applied_how` | string | optional | How the knowledge was applied |
| `soul_updated` | boolean | ✅ | Whether the consumer's soul.yaml was updated with this insight |
| `notes` | string | optional | Additional context |

### §4.4 Cross-Reference Index

An agent can optionally maintain an index at `knowledge/cross_references/{CONSUMER}/INDEX.json`:

```json
{
  "agent": "kali",
  "updated_at": "2026-06-04T10:00:00Z",
  "cross_references": ["xref-kali-ksig-20260603-lilith-001"],
  "total_consumed": 1,
  "unique_producers": ["lilith"]
}
```

---

## §5 Lifecycle Management

### §5.1 Signal Cleanup

Knowledge signals and demand signals have `ttl_days`. The cleanup process:

1. Scan all `KSIG_*.json` files in `knowledge_feed/`
2. If `timestamp + ttl_days < now`, move to `knowledge_feed/_archive/`
3. Scan all `dem-*.json` files in `demand_signals/`
4. If `created_at + ttl_days < now` and status is `OPEN`, set → `EXPIRED` → `CLOSED`, move to `demand_signals/_archive/`

### §5.2 Archive Directory Structure

```
data/coordination/
├── knowledge_feed/
│   ├── KSIG_20260603_LILITH_001.json      (active)
│   ├── KSIG_20260604_LINK_001.json         (active)
│   └── _archive/
│       └── KSIG_20260401_OLD_001.json      (expired)
├── demand_signals/
│   ├── dem-20260603-001.json               (active)
│   └── _archive/
│       └── dem-20260401-001.json           (closed)

knowledge/
└── cross_references/
    ├── kali/
    │   ├── INDEX.json
    │   └── lilith_ksig-20260603-lilith-001.json
    └── doom_guy/
        ├── INDEX.json
        └── lilith_ksig-20260603-lilith-001.json
```

---

## §6 Integration with Existing Systems

### §6.1 Hivemind Protocol

Cross-pollination complements, does not replace, Hivemind:

| Concern | Hivemind Protocol | Cross-Pollination Protocol |
|---------|-------------------|---------------------------|
| Live awareness | ✅ Who is alive NOW | ❌ |
| Task coordination | ✅ Workspace locks, live feed | ❌ |
| Knowledge persistence | ❌ | ✅ KSIG + cross-ref format |
| Demand discovery | ❌ | ✅ Demand signal lifecycle |
| Startup catch-up | ❌ | ✅ Startup discovery scan |
| Inter-agent handoff | ❌ (uses Subagent Dispatch) | ✅ Asynchronous knowledge sharing |

### §6.2 Link P9 Runtime

The Cross-Pollination Protocol builds ON TOP of Link P9 Runtime (384 lines):

- Link P9 handles **live** agent presence + handoff packets
- Cross-Pollination handles **async** knowledge sharing via filesystem
- Use both: Link P9 for synchronous handoff, Cross-Pollination for knowledge broadcasts

### §6.3 Subagent Dispatch

- Subagent Dispatch creates a HandoffPacket for a specific task to a specific agent
- Cross-Pollination broadcasts knowledge to ALL agents simultaneously
- When a demand signal is fulfilled, optionally create a HandoffPacket to deliver the result directly

---

## §7 Agent Onboarding Manifest

Every agent SHOULD perform this at session start:

```python
# Pseudocode for any agent's session_start()
async def session_start(agent_name: str, capabilities: List[str], domains: List[str]):
    # 1. Register presence
    await link_p9.heartbeat(agent_name)

    # 2. Scan knowledge feed for unconsumed signals
    new_signals = await scan_knowledge_feed(agent_name, capabilities, domains)

    for signal in new_signals:
        # 3. Consume each signal
        await consume_signal(signal, agent_name)

    # 4. Scan demand signals for open matches
    open_demands = await scan_demand_signals(domains)

    # 5. Report
    return {
        "new_signals": len(new_signals),
        "open_demands": len(open_demands),
    }
```

---

## §8 Error Handling

### §8.1 Corrupted KSIG/DEM Files

If a signal file fails JSON validation:
1. Log warning with file path
2. Skip the file (do not crash)
3. Move to `data/coordination/_corrupt/{FILENAME}` for manual inspection

### §8.2 ZONEID Validation

If `zoneid != ZONEID_KNOWLEDGE` or `ZONEID_DEMAND`:
1. Log error with expected vs actual hex values
2. Skip the file
3. Move to `data/coordination/_corrupt/`

### §8.3 Atomic Writes

Always write signal files using `.tmp` → rename pattern:
```python
tmp = path.with_suffix(".tmp")
tmp.write_text(json_data)
tmp.rename(path)
```

---

## §9 Changelog

- **v1.0.0 (2026-06-04)**: Initial Cross-Pollination Protocol
  - §1: Knowledge Signal Format (KSIG)
  - §2: Demand Signal Format (DEM) with lifecycle states
  - §3: Discovery flow and relevance matching
  - §4: Cross-reference format
  - §5: Lifecycle management and cleanup
  - §6: Integration with Hivemind, Link P9, Subagent Dispatch
  - §7: Agent onboarding manifest
  - §8: Error handling
  - New ZONEID constants: `ZONEID_KNOWLEDGE = 0x1d4a18`, `ZONEID_DEMAND = 0x1d4a19`

— P9:Link, 2026-06-04

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
