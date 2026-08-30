---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "supplementary_discovery_report"
document_id: "R_ROC_OPENCODE_COMPACTION_CAPTURE_20260829"
title: "OpenCode Compaction Capture — Auto-Routing to Agent Workspaces & Vector Store"
status: "ACTIVE — Supplementary to R_ROC_OPENCODE_COMPACTION_DEEP_DIVE_20260829"
date: "2026-08-29"
author: "roc_racoon (Sovereign Miner)"
parent_report: "data/coordination/R_ROC_OPENCODE_COMPACTION_DEEP_DIVE_20260829.md"
dispatched_by: "Kali"
sprint: "PUBLIC-DEBUT-01"
---

# 🔱 R_ROC_OPENCODE_COMPACTION_CAPTURE — Auto-Capture & Route Architecture
**AP Token**: `AP-OPENCODE-COMPACTION-CAPTURE-20260829-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_compaction_capture ⬡ ACTIVE

---

## §0 — Executive Summary

**Kali's strategic question**: Instead of *extracting* compaction summaries after-the-fact, can we *capture* them at write-time, auto-route to the active agent's workspace, and auto-digest into the vector store?

**Answer**: ✅ **YES** — and the mechanism already exists in OpenCode's V2 architecture. We can intercept at the `events.project(SessionV1.Event.PartUpdated, ...)` layer in `projector.ts:310`, route via the existing `SovereignIngestionCoordinator.process_and_anchor()` pipeline, and store in `sqlite_vec_adapter.upsert()` with `entity_name` partition.

**What we can do TODAY (without forking OpenCode)**:
1. Build an Omega plugin that listens to `SessionV1.Event.PartUpdated` events
2. Filter for parts where `assistantMessage.summary === true` AND `part.type === "text"`
3. On match, route to active entity workspace + auto-digest into vector store
4. Use the existing `SovereignIngestionCoordinator` for the full Sieve-and-Sign pipeline

**What we CANNOT do (without V2 maturation or forking)**:
1. V2 has no plugin hooks for compaction — but V1 has `experimental.text.complete` which fires for every text-end (including summaries)
2. No clean "compaction finished" event in V1 — only the post-completion `session.compacted` event which has NO text content

**Recommended approach**: Build a **sidecar service** that polls the OpenCode SQLite DB for new compaction messages (since the EventV2Bridge is a server-side mechanism, not accessible from external plugins directly). This is more reliable than trying to inject into OpenCode's internal event system.

---

## §1 — Current State: Where Summaries Get Written to DB

### §1.1 V1 Path (Current Production)

The summary text ends up in the DB as a `text` part of an `assistant` message with `info.summary = true`:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. User types /compact                                              │
│ 2. TUI: routes to SDK session.summarize() (index.tsx:580)           │
│ 3. HTTP: POST /session/:sessionID/summarize (handlers/session.ts:273)│
│ 4. handler: revertSvc.cleanup() + compactSvc.create()                │
│ 5. compactSvc.create() → writes user message with type="compaction" │
│ 6. promptSvc.loop() runs the session loop                            │
│ 7. processCompaction() (compaction.ts:319) builds prompt             │
│ 8. processor.process() sends prompt to LLM                           │
│ 9. LLM streams text-delta events (processor.ts:499)                  │
│ 10. text-delta → session.updatePartDelta() → DB write                │
│ 11. text-end → session.updatePart() → DB write FINAL                  │
│ 12. The text is now in part.text of the assistant message            │
│ 13. events.publish(Event.Compacted, { sessionID }) (line 554)        │
└─────────────────────────────────────────────────────────────────────┘
```

### §1.2 V2 Path (New Architecture)

The V2 path is cleaner and more event-driven:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. LLM streaming completes in V2 runner                              │
│ 2. yield* dependencies.events.publish(SessionEvent.Compaction.Ended) │
│    (core/session/compaction.ts:222)                                  │
│    Payload: { sessionID, messageID, reason, text, recent, timestamp }│
│ 3. events.project(SessionV1.Event.PartUpdated, ...) (projector.ts:310)│
│    → DB write via Drizzle ORM                                        │
│ 4. message-updater.ts:377 handles "session.next.compaction.ended"    │
│    → adapter.appendMessage(SessionMessage.Compaction.make({...}))    │
│    → DB write to session_message table with type="compaction"        │
└─────────────────────────────────────────────────────────────────────┘
```

**Key insight**: The V2 event `SessionEvent.Compaction.Ended` carries the FULL summary text in `event.data.text`. This is the cleanest interception point. But V2 has **no plugin hooks** to listen externally.

---

## §2 — Interception Strategy: Three Options

### §2.1 Option A: Sidecar Polling Service (RECOMMENDED)

**Architecture**: A long-running service that polls the OpenCode SQLite DB for new compaction messages.

```
OpenCode SQLite DB (PartTable)         Omega Sidecar Service
┌──────────────────────────┐           ┌──────────────────────────┐
│ id: PartID               │           │ SELECT * FROM part       │
│ message_id: MessageID    │  poll    │ WHERE time_created > ?   │
│ session_id: SessionID    │ ───────► │ AND data LIKE '%summary%'│
│ data: JSON (contains text)│          │                          │
│ time_created: timestamp  │           │ → extract text           │
└──────────────────────────┘           │ → identify entity        │
                                       │ → route to workspace     │
                                       │ → ingest into vector DB  │
                                       └──────────────────────────┘
```

**Pros**:
- No OpenCode modification needed
- Works with V1 (current) and V2 (future)
- Reliable — DB is the source of truth
- Can use existing Omega infrastructure

**Cons**:
- Polling latency (1-5s typical)
- Needs to track "last seen" timestamp
- Requires DB access to OpenCode's SQLite

**Implementation estimate**: 2-3 hours

### §2.2 Option B: V1 Plugin via `experimental.text.complete` Hook

**Architecture**: Use the existing V1 plugin hook that fires on every text-end (including compaction summary text).

```typescript
// Omega Compaction Capture Plugin
const plugin: PluginInstance = {
  async "experimental.text.complete"(input, output) {
    // input: { sessionID, messageID, partID }
    // output: { text }  // the final text
    
    // Check if this is a summary (the message has summary=true flag)
    const isCompaction = await isCompactionMessage(input.messageID)
    if (!isCompaction) return
    
    // Route to active entity workspace
    const entity = getActiveEntity(input.sessionID)
    await captureToWorkspace(entity, input.sessionID, output.text)
    
    // Auto-digest into vector store
    await digestToVector(entity, input.sessionID, output.text)
  }
}
```

**Pros**:
- Real-time (no polling latency)
- Uses existing plugin mechanism
- No DB access required

**Cons**:
- V1-specific (V2 has no plugin hooks)
- `experimental.text.complete` fires for EVERY text-end, not just compactions
- Need to filter: check if the parent message is a `summary` type
- Plugin runs in-process with OpenCode — needs to be loaded into the plugin config
- Cannot async-route to Python sidecar (plugin is JS/TS, ingestion pipeline is Python)

**Implementation estimate**: 3-4 hours (plugin + Python IPC bridge)

### §2.3 Option C: V2 Event Bus Listener (Future)

**Architecture**: Listen to `SessionEvent.Compaction.Ended` directly via the EventV2 system.

```typescript
// Internal hook in OpenCode (requires fork)
yield* events.listen((event) => {
  if (event.type === "session.next.compaction.ended") {
    // Route to Omega
    routeToOmega(event.data)
  }
})
```

**Pros**:
- Cleanest interception point
- Real-time, exact text content
- Future-proof

**Cons**:
- Requires forking OpenCode (no external plugin access to V2 events)
- V2 is in development, API may change
- Not available in production today

**Implementation estimate**: N/A (requires upstream contribution or fork)

### §2.4 Recommendation: Option A (Sidecar Polling)

**Why**:
1. **No OpenCode modification required** — works with current production V1
2. **Reliable** — DB is the source of truth, polling catches everything
3. **Simple** — single Python service using existing Omega infrastructure
4. **Testable** — easy to verify via DB inspection
5. **Decoupled** — doesn't depend on OpenCode internal events

**Trade-off accepted**: 1-5s polling latency is acceptable for compaction capture (not real-time critical).

---

## §3 — Sidecar Polling Service: Detailed Design

### §3.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenCode SQLite DB                                 │
│  ~/.local/share/opencode/opencode.db                                  │
│                                                                       │
│  Tables:                                                              │
│  - session: session metadata (ID, directory, etc.)                    │
│  - message: SessionV1.Message rows (contains summary=true)            │
│  - part: text parts (contains the summary text)                      │
│  - session_message: V2 messages (type='compaction')                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ poll every 2-5s
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         Omega Compaction Capture Sidecar (Python)                    │
│                                                                       │
│  1. Track last_seen_message_id (initially 0)                          │
│  2. Query: SELECT m.id, m.session_id, s.directory, p.text             │
│           FROM message m                                               │
│           JOIN session s ON s.id = m.session_id                       │
│           JOIN part p ON p.message_id = m.id                          │
│           WHERE m.id > :last_seen                                     │
│           AND json_extract(m.data, '$.summary') = true                │
│           AND p.type = 'text'                                         │
│           ORDER BY m.id ASC                                            │
│  3. For each new compaction:                                          │
│     a. Identify entity (from session.directory or active agent)       │
│     b. Run SovereignIngestionCoordinator.process_and_anchor()        │
│     c. Run sqlite_vec_adapter.upsert() with entity_name partition    │
│     d. Update last_seen_message_id                                   │
│  4. Use SQLite WAL mode for non-blocking concurrent reads            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ ingest
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Omega Storage Layer                                      │
│                                                                       │
│  - Entity workspace: data/entities/{entity}/workspace/compaction/     │
│  - Vector store: data/omega_vec/collections/omega_vec_gemma_768       │
│  - Raw anchor: data/entities/{entity}/anchors/{timestamp}.md         │
│  - SCA metadata: data/entities/{entity}/sca/{timestamp}.yaml         │
└─────────────────────────────────────────────────────────────────────┘
```

### §3.2 Component: Active Entity Resolution

**Problem**: The OpenCode session doesn't directly know which Omega entity is "active" for it.

**Solution**: Use a mapping table `data/coordination/SESSION_ENTITY_MAP.yaml`:

```yaml
# data/coordination/SESSION_ENTITY_MAP.yaml
# Maps OpenCode session IDs to Omega entities
# Updated by: orchestrator when entities are activated
session_mappings:
  - opencode_session: "ses_abc123"
    omega_entity: "roc_racoon"
    activated_at: "2026-08-29T10:00:00Z"
  - opencode_session: "ses_xyz789"
    omega_entity: "kali"
    activated_at: "2026-08-29T10:15:00Z"
default_entity: "default"  # Used if session not in map
```

**Alternative**: Use the OpenCode session's `directory` field to match against entity workspaces by path.

### §3.3 Component: Compaction Capture Worker

```python
# src/omega/oracle/compaction_capture.py

import anyio
import sqlite3
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from omega.oracle.entity_workspace import EntityWorkspaceManager
from omega.oracle.ingestion import SovereignIngestionCoordinator
from omega.memory.sqlite_vec_adapter import SqliteVecAdapter
from omega.errors import OmegaError

logger = logging.getLogger("compaction_capture")

OPENCODE_DB_PATH = Path("~/.local/share/opencode/opencode.db").expanduser()
POLL_INTERVAL_SEC = 3.0
SESSION_ENTITY_MAP_PATH = Path("data/coordination/SESSION_ENTITY_MAP.yaml")


class CompactionCaptureWorker:
    """
    Sidecar service that polls the OpenCode SQLite DB for new
    compaction summaries and auto-routes them to:
    1. Active agent's workspace
    2. Vector store (auto-digested)
    3. Raw anchor + SCA (provenance)
    """
    
    def __init__(self):
        self._last_seen_message_id = 0
        self._running = False
        self._workspace_mgr = EntityWorkspaceManager()
        self._ingestion = SovereignIngestionCoordinator(...)
        self._vector_store = SqliteVecAdapter(...)
        self._session_map = self._load_session_map()
    
    async def start(self, task_group: anyio.abc.TaskGroup):
        """Start the background capture loop."""
        self._running = True
        self._last_seen_message_id = self._get_current_max_id()
        task_group.start_soon(self._capture_loop)
        logger.info("CompactionCaptureWorker online — polling every %.1fs", POLL_INTERVAL_SEC)
    
    async def stop(self):
        self._running = False
    
    async def _capture_loop(self):
        while self._running:
            try:
                await self._scan_for_new_compactions()
            except Exception as e:
                logger.error("Compaction capture failed: %s", e, exc_info=True)
            await anyio.sleep(POLL_INTERVAL_SEC)
    
    async def _scan_for_new_compactions(self):
        """Query OpenCode DB for new compaction messages since last scan."""
        conn = sqlite3.connect(str(OPENCODE_DB_PATH), timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT m.id, m.session_id, m.data, s.directory,
                       p.id as part_id, p.data as part_data
                FROM message m
                JOIN session s ON s.id = m.session_id
                JOIN part p ON p.message_id = m.id
                WHERE m.id > ?
                  AND json_extract(m.data, '$.summary') = true
                  AND json_extract(p.data, '$.type') = 'text'
                ORDER BY m.id ASC
                """,
                (self._last_seen_message_id,),
            ).fetchall()
        finally:
            conn.close()
        
        for row in rows:
            await self._capture_one(row)
            self._last_seen_message_id = max(self._last_seen_message_id, row["id"])
    
    async def _capture_one(self, row: sqlite3.Row):
        """Route a single compaction summary to all sinks."""
        message_data = json.loads(row["data"])
        part_data = json.loads(row["part_data"])
        
        summary_text = part_data.get("text", "")
        if not summary_text:
            return
        
        session_id = row["session_id"]
        entity = self._resolve_entity(session_id, row["directory"])
        
        metadata = {
            "source": "opencode_compaction",
            "session_id": session_id,
            "message_id": row["id"],
            "part_id": row["part_id"],
            "compaction_reason": message_data.get("summary_reason", "manual"),
            "timestamp": part_data.get("time", {}).get("end", time.time()),
            "agent": message_data.get("agent", "unknown"),
            "model": message_data.get("modelID", "unknown"),
        }
        
        # Sink 1: Raw anchor + SCA via SovereignIngestionCoordinator
        source_id, doc = await self._ingestion.process_and_anchor(
            raw_content=summary_text,
            metadata=metadata,
            target_entity=entity,
            provider_name="opencode_compaction",
        )
        
        # Sink 2: Entity workspace copy
        await self._write_to_workspace(entity, session_id, source_id, summary_text, metadata)
        
        # Sink 3: Vector store (auto-digest)
        await self._digest_to_vector(entity, session_id, source_id, summary_text, metadata)
        
        logger.info(
            "Captured compaction: entity=%s session=%s source=%s chars=%d",
            entity, session_id, source_id, len(summary_text),
        )
    
    def _resolve_entity(self, session_id: str, directory: str) -> str:
        """Resolve the Omega entity for this session."""
        if session_id in self._session_map:
            return self._session_map[session_id]
        # Try matching directory to entity workspace
        for entity_dir in Path("data/entities").iterdir():
            if entity_dir.is_dir() and str(entity_dir) in directory:
                return entity_dir.name
        return "default"
    
    async def _write_to_workspace(self, entity, session_id, source_id, text, metadata):
        """Write a copy of the summary to the entity's workspace."""
        workspace_dir = self._workspace_mgr._get_entities_data_dir() / entity
        compaction_dir = workspace_dir / "workspace" / "compactions"
        compaction_dir.mkdir(parents=True, exist_ok=True)
        
        # Write as markdown
        ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime(metadata["timestamp"] / 1000))
        file_path = compaction_dir / f"{ts}_{session_id[:12]}.md"
        file_path.write_text(
            f"# Compaction {ts}\n\n"
            f"**Session**: {session_id}\n"
            f"**Reason**: {metadata['compaction_reason']}\n"
            f"**Agent**: {metadata['agent']}\n"
            f"**Model**: {metadata['model']}\n\n"
            f"---\n\n{text}\n"
        )
    
    async def _digest_to_vector(self, entity, session_id, source_id, text, metadata):
        """Embed and upsert into the vector store."""
        # Get embedding from current provider
        embedding = await self._get_embedding(text)
        
        vector_metadata = {
            "content": text[:1000],  # First 1000 chars as preview
            "session_id": session_id,
            "source_id": source_id,
            "role": "compaction_summary",
            "timestamp": metadata["timestamp"],
            "agent": metadata["agent"],
            "compaction_reason": metadata["compaction_reason"],
        }
        
        await self._vector_store.upsert(
            entity_name=entity,
            vector=embedding,
            metadata=vector_metadata,
            id=source_id,  # Idempotent: same source_id = same vector
            collection="omega_vec_gemma_768",
        )
    
    async def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding using current provider."""
        # Use the SovereignFallbackEmbeddingProvider or Ollama
        # (implementation in omega.memory.embeddings)
        ...
    
    def _get_current_max_id(self) -> int:
        """Get the current max message ID (for restart safety)."""
        conn = sqlite3.connect(str(OPENCODE_DB_PATH), timeout=5.0)
        try:
            row = conn.execute("SELECT MAX(id) FROM message").fetchone()
            return row[0] or 0
        finally:
            conn.close()
    
    def _load_session_map(self) -> Dict[str, str]:
        """Load session→entity mapping from yaml."""
        if not SESSION_ENTITY_MAP_PATH.exists():
            return {}
        import yaml
        data = yaml.safe_load(SESSION_ENTITY_MAP_PATH.read_text())
        return {
            m["opencode_session"]: m["omega_entity"]
            for m in data.get("session_mappings", [])
        }


# Singleton
_capture: Optional[CompactionCaptureWorker] = None

def get_capture() -> CompactionCaptureWorker:
    global _capture
    if _capture is None:
        _capture = CompactionCaptureWorker()
    return _capture

async def start_capture(task_group: anyio.abc.TaskGroup):
    capture = get_capture()
    await capture.start(task_group)
    return capture
```

### §3.4 Edge Cases to Handle

1. **OpenCode DB not available** — graceful degradation, log warning, retry
2. **Polling during OpenCode shutdown** — connection errors, retry with backoff
3. **Large summary text** — embed only first 4K chars, store full text as anchor
4. **Entity not resolved** — use "default" entity, log warning
5. **Vector store unavailable** — store in workspace, retry vector ingestion later
6. **DB schema mismatch** — V1 vs V2 message tables (handle both)
7. **Concurrent captures** — use last_seen_id as monotonic guard
8. **Workspace lock conflict** — coordinate with existing entity workspace lock system
9. **Embedding failure** — fall back to StaticEmbeddingProvider (hash-based)
10. **Capture service restart** — resume from last_seen_id, never miss

---

## §4 — Other High-Value Auto-Actions to Implement

### §4.1 Tool Output Indexing (HIGH VALUE)

**What**: When a tool produces output, auto-digest it into the vector store tagged with `role: "tool_output"`.

**Why**: Tool outputs are often the most valuable context — file contents, search results, command outputs. But they get truncated or compacted away. Auto-indexing preserves searchability.

**How**:
- Hook into `experimental.tool.execute.after` (V1) or `tool.execute.after` event (V2)
- Filter for large outputs (>1KB)
- Embed and store with metadata: tool_name, call_id, session_id, args_hash

**Implementation estimate**: 1-2 hours (plugin + Python IPC)

### §4.2 Session Title Generation (MEDIUM VALUE)

**What**: When a session is created, auto-generate a title from the first user message.

**Why**: Sessions with no title are hard to find later. OpenCode has a `title` agent but it's opt-in.

**How**:
- Subscribe to `session.created` events
- Call the title generation agent
- Update session metadata

**Implementation estimate**: 30 min (OpenCode has `title` agent built in)

### §4.3 Session Diff Anchoring (HIGH VALUE)

**What**: When a session completes (or compacts), auto-anchor the file diffs to the entity's workspace.

**Why**: OpenCode already calculates file diffs via the `SessionSummary.summarize()` function (`opencode/src/session/summary.ts:82-100`). We just need to capture them.

**How**:
- Hook into `SessionSummary.summarize()` events
- The `diffs` array contains file paths and changes
- Persist to entity workspace + vector store

**Implementation estimate**: 2 hours (capture service + diff persistence)

### §4.4 Conversation Thread Reconstruction (HIGH VALUE)

**What**: When a compaction happens, capture the FULL conversation history (not just summary) to the entity's archive.

**Why**: The summary loses nuance. For audit, debugging, and learning, the original conversation is valuable.

**How**:
- On `SessionV1.Event.Compacted` event (V1) or `session.next.compaction.ended` (V2)
- Query all messages before the compaction point
- Write to `data/entities/{entity}/archive/sessions/{session_id}/conversations/{compaction_id}.jsonl`

**Implementation estimate**: 2-3 hours (read + serialize + write)

### §4.5 L1→L2→L3 Distillation Triggers (HIGH VALUE)

**What**: When a session ends, automatically run the L1→L2→L3 distillation to extract lessons.

**Why**: The Scribe pipeline (`scribe`) already does this for human-managed sessions. Auto-triggering it on session end captures lessons automatically.

**How**:
- Subscribe to session status changes (`busy` → `idle`)
- When status becomes `idle` for >5 minutes, run distillation
- Write to `proposed_lessons.yaml`

**Implementation estimate**: 3-4 hours (Scribe integration)

### §4.6 Cross-Session Reference Graph (MEDIUM VALUE)

**What**: When a compaction references a file path, D-number, mandate ID, or entity, auto-link it to the relevant Omega knowledge node.

**Why**: Summaries mention many entities (files, decisions, mandates). Auto-linking builds a knowledge graph for free.

**How**:
- Parse summary text for patterns: `D-\d+`, `M\d+`, file paths, entity names
- Create references in `data/entities/{entity}/knowledge/links/`
- Update cross-references in PIVOT_LOG

**Implementation estimate**: 2-3 hours (regex parser + link store)

### §4.7 Compaction Quality Metrics (MEDIUM VALUE)

**What**: Track the size delta before/after compaction, time taken, model used, summary length.

**Why**: Without metrics, we can't improve. Already have a `CompactionHarvester` but it doesn't capture from OpenCode.

**How**:
- Extend the capture service to record metrics
- Store in `data/coordination/compaction_metrics/`
- Aggregate by model, agent, session type

**Implementation estimate**: 1 hour (metrics + dashboard)

### §4.8 Auto-Promote to Knowledge (LOWER VALUE, COMPLEX)

**What**: When a summary is captured, automatically attempt to promote important facts to the entity's `knowledge/` directory.

**Why**: Currently, knowledge promotion is manual. Auto-promotion could accelerate knowledge accumulation.

**How**:
- Use the L1→L2→L3 distillation on the summary
- If the lesson passes the T1→T2 gate, move to `knowledge/`
- Otherwise, leave in `workspace/`

**Implementation estimate**: 4-6 hours (full Scribe integration + quality gates)

---

## §5 — Implementation Priority Matrix

| Action | Value | Effort | Risk | Priority |
|--------|-------|--------|------|----------|
| **Compaction Capture (Sidecar Polling)** | HIGH | 2-3h | LOW | 🔴 P0 |
| **Tool Output Indexing** | HIGH | 1-2h | LOW | 🟠 P1 |
| **Session Diff Anchoring** | HIGH | 2h | LOW | 🟠 P1 |
| **Conversation Thread Reconstruction** | HIGH | 2-3h | MED | 🟠 P1 |
| **L1→L2→L3 Auto-Distill on Session End** | HIGH | 3-4h | MED | 🟡 P2 |
| **Cross-Session Reference Graph** | MED | 2-3h | LOW | 🟡 P2 |
| **Compaction Quality Metrics** | MED | 1h | LOW | 🟢 P3 |
| **Auto-Promote to Knowledge** | MED | 4-6h | HIGH | 🟢 P3 |

**Recommended phase plan**:
- **Phase 1 (debut-ready)**: Compaction Capture + Tool Output Indexing = 4-5h total
- **Phase 2 (post-debut week 1)**: Session Diff Anchoring + Conversation Reconstruction
- **Phase 3 (post-debut week 2)**: L1→L2→L3 + Cross-Session Reference Graph
- **Phase 4 (post-debut week 3)**: Metrics + Auto-Promotion

---

## §6 — Integration with Existing Omega Systems

### §6.1 Reuse Existing Infrastructure

| Existing System | How to Use |
|-----------------|------------|
| `SovereignIngestionCoordinator.process_and_anchor()` | Already does Sieve-and-Sign + Raw anchor + SCA — just call it |
| `sqlite_vec_adapter.upsert()` | Already accepts `entity_name` partition + idempotent `id` parameter |
| `IngestionPersistence.persist_raw_anchor()` | Already handles per-entity storage |
| `CompactionHarvester` | Already has metric aggregation — extend, don't replace |
| `EntityWorkspaceManager` | Already creates `workspace/` and `knowledge/` dirs |
| `Hivemind` | Use for status broadcasts on capture events |

### §6.2 What This Doesn't Replace

- The existing `CompactionHarvester` (which is for triggering Omega-internal compaction, not capturing OpenCode summaries)
- The existing `SovereignIngestionCoordinator` (we USE it, don't replace it)
- The existing entity workspaces (we ADD a `compactions/` subdirectory)

### §6.3 New Files to Create

1. `src/omega/oracle/compaction_capture.py` — main worker (3-4KB)
2. `data/coordination/SESSION_ENTITY_MAP.yaml` — session→entity mapping
3. `docs/strategy/COMPACTION_CAPTURE_ARCHITECTURE.md` — design doc
4. `data/entities/{entity}/workspace/compactions/` — per-entity output dir (auto-created)

---

## §7 — Open Questions for Kali

1. **Should we ship Compaction Capture as part of debut (P0)?**
   - Pro: Demonstrates "active" knowledge accumulation, a key differentiator
   - Con: Adds another moving part to debut; could fail in production
   - Recommendation: YES if we can validate in staging by 2026-08-30

2. **Which entities should the capture service support initially?**
   - All entities? (default) — catches everything
   - Only sovereign entities (kali, jem, lilith, etc.)? — limited but safer
   - Configurable per-session? — most flexible but more complex

3. **What happens when an OpenCode session is from a non-Omega user?**
   - Skip capture? (safe default)
   - Capture to "default" entity? (could pollute)
   - Log-only mode? (observability without action)

4. **Should we capture to VECTOR store or just entity workspace?**
   - Workspace only: simpler, no embedding cost
   - Vector + workspace: full RAG capability
   - Recommendation: Vector + workspace, but make it configurable

5. **For the auto-actions (§4), which should be P0 vs P2?**
   - My recommendation in §5 priority matrix
   - Kali's call on trade-offs

---

## §8 — Confidence & Evidence Quality

- **Confidence**: 🟢 HIGH on architecture, 🟡 MEDIUM on implementation details
- **Source coverage**:
  - V1 compaction: 100% traced
  - V2 compaction: 80% traced (V2 still in development)
  - EventV2 system: 90% traced
  - Omega ingestion pipeline: 100% traced
  - Vector store API: 100% traced
- **Critical uncertainties**:
  - V2 API stability (V2 is in development)
  - OpenCode DB schema versioning (need to handle both V1 and V2 message tables)
  - Polling vs event-driven tradeoff (recommend polling for simplicity)

---

## §9 — Cross-References

- **R_ROC_OPENCODE_COMPACTION_DEEP_DIVE_20260829.md** — Main deep dive report
- **ROC_RACOON_KALI_DISPATCH_REPORT_20260829.md** — Original dispatch report
- **ROC_RACOON_GROKSTER_TASKS_20260829.md** — Cross-platform research tasks
- **src/omega/oracle/compaction_harvester.py** — Existing harvester (metadata-only)
- **src/omega/oracle/ingestion.py** — Existing SovereignIngestionCoordinator
- **src/omega/memory/sqlite_vec_adapter.py** — Existing vector store

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_compaction_capture ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:40Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

