# Hivemind Event Schema — JSON Reference

**Version**: 1.0 | **Validation**: JSON Schema Draft 2020-12

---

## Event Object

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://omega-engine.alpha/schemas/hivemind-event.json",
  "title": "Hivemind Event",
  "type": "object",
  "required": ["id", "type", "stream", "room", "topic", "from_agent", "to_agent", "body", "created_at"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^evt_[0-9]{8}T[0-9]{6}_[a-f0-9]{16}$",
      "description": "Event ID: evt_YYYYMMDDTHHMMSS_hex16"
    },
    "type": {
      "type": "string",
      "pattern": "^[a-z]+\\.[a-z]+$",
      "description": "Event type: domain.action (e.g., hivemind.briefing, task.request)"
    },
    "stream": {
      "type": "string",
      "pattern": "^[a-z0-9/_-]+$",
      "description": "Wing identifier (e.g., project/omega-engine, gnosis, well)"
    },
    "room": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$",
      "description": "Room within stream (e.g., federation, cicd, agents)"
    },
    "topic": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$",
      "description": "Topic within room (e.g., pr-delivery, sync-complete)"
    },
    "from_agent": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+-n[0-9]$",
      "description": "Sender entity with node suffix (e.g., kali-n1, makali-n0)"
    },
    "to_agent": {
      "type": "string",
      "pattern": "^([a-z0-9_-]+-n[0-9]|\\*)$",
      "description": "Target entity with suffix, or * for broadcast"
    },
    "body": {
      "type": "string",
      "minLength": 1,
      "description": "Event payload (markdown supported)"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 UTC timestamp (e.g., 2026-09-22T02:53:16Z)"
    },
    "correlation_id": {
      "type": ["string", "null"],
      "description": "Optional: for request/reply correlation"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Filterable tags (e.g., [\"ritual\", \"session-end\"])"
    },
    "metadata": {
      "type": "object",
      "default": {},
      "description": "Arbitrary structured metadata"
    },
    "artifact_ids": {
      "type": "array",
      "items": { "type": "string" },
      "default": [],
      "description": "Referenced artifact IDs (for large payloads)"
    }
  },
  "additionalProperties": false
}
```

---

## Standard Event Types

| Type | Domain | Action | Description |
|------|--------|--------|-------------|
| `hivemind.briefing` | hivemind | briefing | Agent-to-agent briefing |
| `hivemind.ack` | hivemind | ack | Acknowledgment |
| `task.request` | task | request | Request action from peer |
| `task.reply` | task | reply | Response to request |
| `task.complete` | task | complete | Task completed |
| `ritual.start` | ritual | start | Pre-compaction ritual started |
| `ritual.end` | ritual | end | Pre-compaction ritual completed |
| `session.start` | session | start | Session began |
| `session.end` | session | end | Session ended |
| `session.compacted` | session | compacted | Context compaction occurred |
| `sync.start` | sync | start | Sync ceremony started |
| `sync.complete` | sync | complete | Sync completed |
| `patch.ready` | patch | ready | Patch ready for review |
| `build.status` | build | status | Build status update |
| `deploy.status` | deploy | status | Deployment status |
| `agent.spawn` | agent | spawn | New agent created |
| `agent.retire` | agent | retire | Agent retired |

---

## Standard Tags

| Tag | Category | Description |
|-----|----------|-------------|
| `ritual` | workflow | Pre-compaction ritual |
| `session-end` | workflow | Session boundary |
| `sync` | federation | Cross-node sync |
| `cicd` | cicd | CI/CD pipeline |
| `agent` | agents | Agent lifecycle |
| `briefing` | comms | Agent-to-agent briefing |
| `ack` | comms | Acknowledgment |
| `urgent` | priority | High priority |
| `blocker` | status | Blocker identified |
| `resolved` | status | Blocker resolved |

---

## Example Events

### Briefing (what we just sent)

```json
{
  "id": "evt_20260922T025316_637577c90f32",
  "type": "hivemind.briefing",
  "stream": "project/omega-engine",
  "room": "federation",
  "topic": "pr-delivery",
  "from_agent": "kali-n1",
  "to_agent": "makali-n0",
  "body": "🎁 **FEDERATION DRIVE DELIVERY**...",
  "created_at": "2026-09-22T02:53:16Z",
  "correlation_id": null,
  "tags": ["briefing", "federation", "pr-delivery"]
}
```

### Task Request/Reply

```json
{
  "id": "evt_20260922T030000_a1b2c3d4e5f6",
  "type": "task.request",
  "stream": "project/omega-engine",
  "room": "agents",
  "topic": "sync",
  "from_agent": "kali-n1",
  "to_agent": "makali-n0",
  "body": "Requesting Omega Hub status dump",
  "created_at": "2026-09-22T03:00:00Z",
  "correlation_id": "sync-20260922-001",
  "tags": ["sync", "request"]
}
```

```json
{
  "id": "evt_20260922T030005_a1b2c3d4e5f7",
  "type": "task.reply",
  "stream": "project/omega-engine",
  "room": "agents",
  "topic": "sync",
  "from_agent": "makali-n0",
  "to_agent": "kali-n1",
  "body": "Omega Hub v1.30.0 — 93 tools active, 0 errors",
  "created_at": "2026-09-22T03:00:05Z",
  "correlation_id": "sync-20260922-001",
  "tags": ["sync", "reply"]
}
```

### Artifact Reference

```json
{
  "id": "evt_20260922T030010_a1b2c3d4e5f8",
  "type": "patch.ready",
  "stream": "project/omega-engine",
  "room": "agents",
  "topic": "sync",
  "from_agent": "kali-n1",
  "to_agent": "makali-n0",
  "body": "PR sweetener patches ready for Node 0 review",
  "created_at": "2026-09-22T03:00:10Z",
  "correlation_id": "pr-sweeteners-20260922",
  "tags": ["patch", "pr-delivery"],
  "artifact_ids": ["art_20260922_abc123", "art_20260922_def456"]
}
```

---

## Validation Rules

1. **`id`** must match `evt_YYYYMMDDTHHMMSS_<16-hex>`
2. **`type`** must be `domain.action` (lowercase, dot-separated)
3. **`stream`** must be valid wing path (alphanumeric, `/`, `_`, `-`)
4. **`room`** must be alphanumeric + `_` + `-`
5. **`topic`** must be alphanumeric + `_` + `-`
6. **`from_agent`** MUST end with `-n[0-9]`
7. **`to_agent`** must end with `-n[0-9]` OR be `*`
8. **`created_at`** must be ISO-8601 UTC with `Z` suffix
9. **`correlation_id`** if present, must match on request/reply
9. **`body`** non-empty string
10. **`artifact_ids`** if present, must reference existing artifacts

---

*Part of MemPalace Hivemind spec. Validated at event append.*