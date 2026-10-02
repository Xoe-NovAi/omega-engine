# MemPalace Hivemind — Integration Guide

**Version**: 1.0 | **Target**: Omega Engine PR Debut

---

## Quick Start

```bash
# 1. Copy package to Omega Engine
cp -r mempalace-hivemind/ $OMEGA_ENGINE_ROOT/

# 2. Install Python client
cd $OMEGA_ENGINE_ROOT/mempalace-hivemind/
uv pip install -e .

# 3. Verify connection
python -c "
from mempalace_hivemind import HivemindClient
client = HivemindClient(entity='test-n1')
client.brief('test', 'Hivemind online', room='federation')
print('✅ Hivemind connected!')
"
```

---

## Architecture Overview

```
Omega Engine
├── mempalace-hivemind/           # This package
│   ├── src/mempalace_hivemind/      # installable package (src layout)
│   │   ├── __init__.py              # Core client (HivemindClient)
│   │   ├── hivemind_cli.py          # CLI interface
│   │   └── validator.py             # Schema validator
│   ├── schemas/
│   │   ├── event.json               # JSON Schema
│   │   └── artifact.json
│   └── docs/                        # Full documentation
│
└── gnosis/                          # MemPalace data (sqlite_exact.sqlite3)
    ├── project/omega-engine/        # Wing: project coordination
    ├── gnosis/                      # Wing: internal memory
    └── well/                        # Wing: corrections corpus
```

---

## Core Client API

### HivemindClient

```python
from mempalace_hivemind import HivemindClient

client = HivemindClient(
    entity="myagent-n1",              # REQUIRED: your entity ID with -n1/-n0
    palace_path="/path/to/mempalace", # Optional: custom palace path
    auto_connect=True                 # Connect on init
)

# Send briefing (fire-and-forget)
client.brief(
    topic="pr-delivery",
    body="## Delivery\nPackage deployed.",
    room="federation",
    to_agent="makali-n0"              # or "*" for broadcast
)

# Wait for response (blocking)
response = client.request(
    topic="sync",
    body="Requesting hub status",
    to_agent="makali-n0",
    timeout_ms=30000
)

# Wait for specific event
event = client.wait_for(
    topic="sync",
    from_agent="makali-n0",
    correlation_id="sync-20260922-001",
    timeout_ms=30000
)

# Subscribe to events (async generator)
async for event in client.subscribe(room="federation", topic="*"):
    print(event.body)
```

---

## CLI Interface

```bash
# Send briefing
hivemind brief --topic pr-delivery --room federation --to makali-n0 --body "Package delivered"

# Send with file
hivemind brief --topic pr-delivery --room federation --body-file briefing.md

# Wait for event
hivemind wait --room federation --topic sync --from makali-n0 --timeout 30000

# List recent events
hivemind list --room federation --topic pr-delivery --limit 10

# Send artifact
hivemind artifact put --kind patch --file patch.diff --metadata '{"base": "abc123"}'

# Validate event
hivemind validate --file event.json
```

---

## Integration Points

### 1. OpenCode Hooks

```python
# In opencode_hooks.py
from mempalace_hivemind import HivemindClient

def on_pre_compact(session_id, reason):
    client = HivemindClient(entity="kali-n1")
    client.brief(
        topic="ritual.pre-compact.start",
        body=f"Pre-compaction ritual started: {reason}",
        room="gnosis",
        tags=["ritual", "session-start"]
    )

def on_session_end(session_id, reason):
    client = HivemindClient(entity="kali-n1")
    client.brief(
        topic="session.end",
        body=f"Session ended: {reason}",
        room="gnosis",
        tags=["session-end"]
    )
```

### 2. Gnosis-Lock Ritual

```bash
# In pre_compaction_ritual.sh, add:
python3 -c "
from mempalace_hivemind import HivemindClient
client = HivemindClient(entity='kali-n1')
client.brief(
    topic='ritual.pre-compact.start',
    body='Ritual started: $REASON',
    room='gnosis',
    tags=['ritual', 'session-start']
)
"
```

### 3. Gnosis-Leash Injection

```javascript
// In gnosis-leash.js, add to compaction injection:
const client = new HivemindClient({ entity: 'kali-n1' });
const event = await client.wait_for('ritual.pre-compact.end', timeout_ms=5000);
// Inject event into compaction context
```

### 4. Make Targets

```makefile
hivemind-brief: ## Send Hivemind briefing
	python3 -c "from mempalace_hivemind import HivemindClient; HivemindClient(entity='kali-n1').brief(topic='$(TOPIC)', body='$(BODY)', room='$(ROOM)')"

hivemind-wait: ## Wait for Hivemind event
	python3 -c "from mempalace_hivemind import HivemindClient; e=HivemindClient(entity='kali-n1').wait_for(topic='$(TOPIC)', timeout_ms=30000); print(e.body)"

hivemind-status: ## Show Hivemind status
	python3 -c "from mempalace_hivemind import HivemindClient; c=HivemindClient(entity='kali-n1'); print(c.status())"
```

---

## Entity Identity Setup

```bash
# Node 1 (this machine)
export HIVEMIND_ENTITY=kali-n1

# Node 0
export HIVEMIND_ENTITY=makali-n0

# In scripts, always use:
entity = os.environ.get("HIVEMIND_ENTITY", "unknown-n1")
```

---

## Event Validation

```bash
# Validate event file against schema
python3 -m mempalace_hivemind.validator event.json

# Or in Python
from mempalace_hivemind.validator import validate_event
validate_event(event_dict)  # raises ValidationError
```

---

## Schema Files

```json
// schemas/event.json - Event schema (see EVENT_SCHEMA.md)
// schemas/artifact.json - Artifact schema
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "kind", "content", "created_by", "created_at", "sha256"],
  "properties": {
    "id": {"type": "string"},
    "kind": {"enum": ["patch", "file", "log", "json", "note"]},
    "content": {"type": "string"},
    "created_by": {"pattern": "^[a-z0-9_-]+-n[0-9]$"},
    "created_at": {"format": "date-time"},
    "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "metadata": {"type": "object"}
  }
}
```

---

## Testing

```bash
# Run validator tests
python3 -m pytest mempalace-hivemind/tests/ -v

# Integration test
python3 -c "
from mempalace_hivemind import HivemindClient
c1 = HivemindClient(entity='test-n1')
c2 = HivemindClient(entity='test-n0')
c1.brief('test', 'hello', room='test', to_agent='test-n0')
# c2 should receive via wait_for or subscribe
"
```

---

## Deployment Checklist

- [ ] Package copied to Omega Engine
- [ ] Python client installed (`uv pip install -e .`)
- [ ] OpenCode hooks updated
- [ ] Gnosis-Lock ritual updated
- [ ] Make targets added
- [ ] Entity env vars set (`HIVEMIND_ENTITY=kali-n1`)
- [ ] `make test` passes
- [ ] `make docs` passes
- [ ] `make lint` passes

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `sqlite_exact.sqlite3` not found | Run `mempalace init` or copy existing palace |
| `Entity validation failed` | Check `-n1`/`-n0` suffix on entity |
| `Event validation failed` | Run `hivemind validate --file event.json` |
| `Connection refused` | Check MemPalace server running on Node 0 |
| `Artifact not found` | Verify artifact ID exists in palace |

---

## License

Apache-2.0 — see parent repo LICENSE.