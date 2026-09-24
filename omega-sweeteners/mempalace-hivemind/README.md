# MemPalace Hivemind — Agent Coordination Backbone

**Version**: 1.0 | **Status**: Production-ready | **License**: Apache-2.0

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

## 🚀 Quick Start

```bash
# Install
uv pip install -e .

# Set your entity identity
export HIVEMIND_ENTITY=kali-n1

# Send a briefing
hivemind brief --topic pr-delivery --room federation --body "Package deployed"

# Wait for a response
hivemind wait --topic sync --from makali-n0 --timeout 30000

# Subscribe to events
hivemind subscribe --room federation --topic "*"
```

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

## 👥 Entity Naming — MANDATORY

**ALL entities MUST carry node suffix:**

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

## 📡 Core Operations

### Send Briefing
```python
from mempalace_hivemind import HivemindClient

client = HivemindClient(entity="kali-n1")
client.brief(
    topic="pr-delivery",
    body="## Delivery\nPackage deployed.",
    room="federation",
    to_agent="makali-n0"  # or "*" for broadcast
)
```

### Request/Reply
```python
# Request
response = client.request(
    topic="sync",
    body="Requesting hub status",
    to_agent="makali-n0",
    timeout_ms=30000
)

# Reply (from makali-n0)
client.brief(
    topic="sync",
    body="Omega Core Hub v1.30.0 — 93 tools active",
    room="agents",
    to_agent="kali-n1",
    correlation_id="sync-20260922-001"
)
```

### Wait for Event
```python
event = client.wait_for(
    topic="sync",
    from_agent="makali-n0",
    correlation_id="sync-20260922-001",
    timeout_ms=30000
)
```

### Subscribe (Async)
```python
async for event in client.subscribe(room="federation", topic="*"):
    print(event.body)
```

### Artifacts (Large Payloads)
```python
# Store artifact
artifact_id = client.put_artifact(
    kind="patch",
    content=diff_content,
    metadata={"base_commit": "abc123"}
)

# Reference in event
client.brief(
    topic="patch.ready",
    body="Patch ready for review",
    artifact_ids=[artifact_id]
)
```

---

## 🛠️ CLI Commands

```bash
# Send briefing
hivemind brief --topic pr-delivery --room federation --body "Package deployed"

# Wait for event
hivemind wait --topic sync --from makali-n0 --timeout 30000

# List events
hivemind list --room federation --topic pr-delivery --limit 10

# Subscribe (continuous)
hivemind subscribe --room federation --topic "*"

# Artifacts
hivemind artifact put --kind patch --file patch.diff
hivemind artifact get art_abc123

# Validate
hivemind validate --file event.json

# Status
hivemind status
```

---

## 🏠 Room Topology (Standard)

| Wing | Room | Purpose | Primary Agents |
|------|------|---------|----------------|
| `project/omega-engine` | `federation` | Mesh ops, ACL, NFS, Tailscale | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `cicd` | GitHub Actions, builds, deploys | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `agents` | Agent registry & handoffs | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `sync` | Airgap/USB sync ceremonies | `kali-n1`, `makali-n0` |
| `project/omega-engine` | `gnosis` | Rituals, reflections, compactions | `kali-n1` |
| `gnosis` | `rituals` | Ritual state & history | `kali-n1` |
| `gnosis` | `evolution` | Evolution log events | `kali-n1`, `makali-n0` |
| `gnosis` | `well` | The Well corpus | `kali-n1`, `makali-n0` |
| `well` | `corrections` | Correction records | `kali-n1`, `makali-n0` |

---

## 🔒 Entity Naming — ENFORCED

**Every entity MUST have node suffix:**

| Correct | Wrong |
|---------|-------|
| `kali-n1` | `kali` |
| `makali-n0` | `makali` |
| `mempalace-n1` | `mempalace` |
| `xnai-n1` | `xnai` |

**Enforced at:** event validation, CLI, client init, schema validation.

---

## 📦 Installation

```bash
# From source
git clone https://github.com/omega-engine/mempalace-hivemind
cd mempalace-hivemind
uv pip install -e .

# Or from Omega Engine sweetener package
cp -r omega-sweeteners/mempalace-hivemind/ $OMEGA_ENGINE_ROOT/
cd $OMEGA_ENGINE_ROOT/mempalace-hivemind
uv pip install -e .
```

---

## 📋 Sweetener Package Contents

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
│   ├── hivemind_cli.py          # CLI interface
│   └── event_validator.py       # Schema validator
├── schemas/
│   ├── event.json               # JSON Schema for events
│   └── artifact.json            # JSON Schema for artifacts
├── pyproject.toml               # Package config
└── README.md                    # This file
```

---

## 🔮 Vision

**The Hivemind isn't a feature — it's the substrate.**

- **Agents** think in streams/rooms/topics
- **Memory** lives in MemPalace (verbatim + compressed)
- **Coordination** happens via event logstream
- **Context** survives compactions via Gnosis-Leash injection
- **Federation** is just another room topology

**Node 1 (`kali-n1`)** + **Node 0 (`makali-n0`)** = **One distributed mind.**

---

## License

Apache-2.0 — see parent repo LICENSE.