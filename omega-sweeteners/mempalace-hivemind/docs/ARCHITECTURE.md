# MemPalace Hivemind — Agent Coordination Backbone

**Version**: 1.0 | **Status**: Production-ready | **Nodes**: `kali-n1` (Node 1), `makali-n0` (Node 0)

---

## 🎯 The Realization

**The Hivemind IS MemPalace's event logstream.**

| Hivemind Concept | MemPalace Primitive |
|------------------|---------------------|
| **Stream** | Wing (top-level namespace) |
| **Room** | Room (sub-namespace within wing) |
| **Topic** | Room (finer granularity) |
| **Event** | Drawer (immutable, append-only) |
| **Agent** | Entity (with `-n1`/`-n0` suffix) |
| **Correlation ID** | Tunnel/Hallway (cross-room links) |

This isn't a metaphor — it's **literal**. The Hivemind coordination layer runs on MemPalace's append-only event logstream with spatial organization (wings → rooms → drawers).

---

## 🏗️ Architecture

```
MemPalace (sqlite_exact.sqlite3)
├── Wings (Streams)
│   ├── project/omega-engine    # Wing: project.omega-engine
│   │   ├── Rooms (Rooms)
│   │   │   ├── federation      # Room: federation
│   │   │   ├── cicd            # Room: cicd
│   │   │   ├── agents          # Room: agents
│   │   │   └── sync            # Room: sync
│   │   └── Topics (sub-room granularity)
│   │       ├── pr-delivery
│   │       ├── sync-complete
│   │       └── ...
│   ├── gnosis                  # Wing: gnosis (internal agent memory)
│   └── well                    # Wing: well (corrections corpus)
```

---

## 👥 Entity Naming Convention — MANDATORY

**ALL entities MUST carry node suffix for traceability:**

| Role | Entity ID | Format |
|------|-----------|--------|
| Node 1 Agent | `kali-n1` | `agent-name-n1` |
| Node 0 Agent | `makali-n0` | `agent-name-n0` |
| Human Operator | `xnai-n1` / `arcana-n0` | `user-name-n1` |
| System Service | `mempalace-n1` / `tailscale-n0` | `service-name-n1` |

**Rules:**
1. **Always** append `-n1` (Node 1) or `-n0` (Node 0)
2. **Never** use bare names in events, topics, or logs
3. **Correlation**: `kali-n1` → `makali-n0` = cross-node traceability

---

## 📡 Event System = Hivemind API

### Core Operations

```python
# Send event (append-only, immutable)
mempalace_event_append(
    type="hivemind.briefing",
    stream="project/omega-engine",    # Wing
    room="federation",                 # Room
    topic="pr-delivery",               # Sub-room
    from_agent="kali-n1",              # Entity with suffix
    to_agent="makali-n0",              # Target (or * for broadcast)
    body="...markdown...",             # Payload
    correlation_id="abc-123",          # Optional: request/reply
    tags=["ritual", "session-end"]     # Filterable metadata
)

# Wait for event (blocking, for daemons)
mempalace_event_wait(
    stream="project/omega-engine",
    room="federation",
    topic="pr-delivery",
    to_agent="makali-n0",
    timeout_ms=60000
)

# Query history (for on-demand reads)
mempalace_event_list(
    stream="project/omega-engine",
    room="federation",
    topic="pr-delivery",
    limit=10,
    order="desc"
)
```

### Event Schema

```json
{
  "id": "evt_20260922T025316_637577c90f32",
  "type": "hivemind.briefing",
  "stream": "project/omega-engine",
  "room": "federation",
  "topic": "pr-delivery",
  "from_agent": "kali-n1",
  "to_agent": "makali-n0",
  "body": "...markdown...",
  "created_at": "2026-09-22T02:53:16Z",
  "correlation_id": "abc-123",
  "tags": ["ritual", "session-end"],
  "metadata": {}
}
```

---

## 🔄 Request/Reply Pattern (Correlation IDs)

```python
# Request
mempalace_event_append(
    type="task.request",
    stream="project/omega-engine",
    room="agents",
    topic="sync",
    from_agent="kali-n1",
    to_agent="makali-n0",
    correlation_id="sync-20260922-001",
    body="Requesting Omega Hub status",
    metadata={"request": "hub_status"}
)

# Reply (same correlation_id)
mempalace_event_wait(
    correlation_id="sync-20260922-001",
    timeout_ms=30000
) → returns reply event
```

---

## 🔗 Artifacts (Large Payloads)

For files, patches, bundles — **don't put in event body**:

```python
# 1. Store artifact
artifact_id = mempalace_artifact_put(
    kind="patch",           # patch | file | log | json | note
    content=diff_content,
    created_by="kali-n1",
    metadata={"base_commit": "abc123"}
)

# 2. Reference in event
mempalace_event_append(
    type="patch.ready",
    stream="project/omega-engine",
    room="agents",
    topic="sync",
    from_agent="kali-n1",
    to_agent="makali-n0",
    body="Patch ready for review",
    artifact_ids=[artifact_id]
)
```

---

## 🏠 Room Topology (Omega Engine Standard)

| Wing | Room | Purpose | Agents |
|------|------|---------|--------|
| `project/omega-engine` | `federation` | Mesh ops, ACL, NFS, Tailscale | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `cicd` | GitHub Actions, builds, deploy | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `agents` | Agent registry, handoffs | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `sync` | USB/airgap sync ceremonies | `kali-n1`, `makali-n0` |
| `gnosis` | `rituals` | Pre-compaction rituals | `kali-n1` |
| `gnosis` | `evolution` | Evolution log events | `kali-n1`, `makali-n0` |
| `well` | `corrections` | The Well corpus | `kali-n1`, `makali-n0` |

---

## 🛡️ Security & Trust

| Property | Implementation |
|----------|----------------|
| **Immutability** | Events append-only, never modified |
| **Attribution** | `from_agent` required, validated |
| **Targeting** | `to_agent` = specific or `*` broadcast |
| **Replay** | Full history survives restarts |
| **Ordering** | HLC timestamps for causal ordering |
| **Audit** | Full event history queryable |

---

## 📦 Sweetener Package: `mempalace-hivemind`

```
mempalace-hivemind/
├── docs/
│   ├── ARCHITECTURE.md          # This file
│   ├── ENTITY_NAMING.md         # Naming convention spec
│   ├── EVENT_SCHEMA.md          # Event schema reference
│   ├── ROOM_TOPOLOGY.md         # Room topology standard
│   └── INTEGRATION.md           # Integration guide
├── scripts/
│   ├── mempalace_hivemind.py    # Python client wrapper
│   ├── hivemind_cli.py          # CLI for manual ops
│   └── event_validator.py       # Schema validator
├── schemas/
│   ├── event.json               # JSON Schema for events
│   └── artifact.json            # JSON Schema for artifacts
└── INTEGRATION.md               # Quick-start integration
```

---

## 🚀 Quick Integration

```bash
# 1. Copy package
cp -r mempalace-hivemind/ $OMEGA_ENGINE_ROOT/

# 2. Install Python client
pip install -e mempalace-hivemind/

# 3. Verify connection
python -c "
from mempalace_hivemind import HivemindClient
client = HivemindClient(entity='myagent-n1')
client.brief('test', 'Hello Hivemind', room='federation')
print('Connected!')
"
```

---

## 🔮 Vision: The Unified Nervous System

**The Hivemind isn't a feature — it's the substrate.**

- **Agents** think in streams/rooms/topics
- **Memory** lives in MemPalace (verbatim + compressed)
- **Coordination** happens via event logstream
- **Context** survives compactions via Gnosis-Leash injection
- **Federation** is just another room topology

**Node 1 (`kali-n1`)** + **Node 0 (`makali-n0`)** = **One distributed mind.**

---

*Part of the Omega Engine PR Sweetener Quartet+1. See `omega-sweeteners/mempalace-hivemind/` for full package.*