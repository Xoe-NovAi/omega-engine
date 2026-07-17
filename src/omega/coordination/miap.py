# 🔱 Omega Engine — Multi-Instance Agent Protocol (MIAP) Core
# ⬡ OMEGA ⬡ KALI ⬡ MIAP ⬡ src/omega/coordination/miap.py
# AP Token: AP-MIAP-v1.0.0

"""
Multi-Instance Agent Protocol (MIAP) Core Implementation.

Event sourcing + deterministic projection for multi-instance agent coordination.
Solves the anchored-summary.md overwrite collision between multiple instances
of the same entity running in different OpenCode/Cline sessions.

Architecture:
- Append-only JSONL event logs (source of truth)
- Deterministic projectors (pure functions, no LLM calls)
- File-lock serialized writes (POSIX fcntl, cross-process safe)
- Symlink projections at canonical locations
- Hivemind integration for instance awareness

Mandate Compliance: M1, M2, M4, M5, M7, M11, M13, M15, M17, M18, M21, M22, M23
"""

import uuid
import json
import os
import time
import hashlib
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field

import anyio
from anyio import Lock

def uuid7() -> uuid.UUID:
    """Generate UUIDv7 (time-ordered) compatible with Python < 3.13."""
    # UUIDv7: 48-bit timestamp (ms since epoch) + 74 random bits + version/variant
    timestamp_ms = int(time.time() * 1000)
    timestamp_bytes = timestamp_ms.to_bytes(6, 'big')
    random_bytes = os.urandom(10)
    # Version 7 (0111) in bits 4-7 of byte 6
    random_bytes = bytearray(random_bytes)
    random_bytes[0] = (random_bytes[0] & 0x0F) | 0x70
    # Variant 10 (RFC 4122) in bits 6-7 of byte 8
    random_bytes[2] = (random_bytes[2] & 0x3F) | 0x80
    return uuid.UUID(bytes=timestamp_bytes + bytes(random_bytes))

# ─── Constants ──────────────────────────────────────────────────────────────

# Find actual project root (contains .opencode, data/, src/, etc.)
def _find_project_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(10):
        if (p / ".opencode").exists() and (p / "data").exists() and (p / "src").exists():
            return p
        p = p.parent
    # Fallback
    return Path(__file__).resolve().parent.parent.parent

PROJECT_ROOT = _find_project_root()
COORDINATION_DIR = PROJECT_ROOT / "data" / "coordination"
INSTANCES_DIR = COORDINATION_DIR / "instances"
ANCHORED_EVENTS_DIR = COORDINATION_DIR / "anchored_summary"
GNOSIS_EVENTS_DIR = COORDINATION_DIR / "session_gnosis"

for d in (INSTANCES_DIR, ANCHORED_EVENTS_DIR, GNOSIS_EVENTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ─── Data Classes ───────────────────────────────────────────────────────────

@dataclass
class InstanceRecord:
    """Registry entry for an agent instance."""
    instance_id: str
    channel: str
    entity: str
    session_uuid: str
    pid: int
    started_at: str
    status: str  # "active", "terminated", "crashed"
    last_heartbeat: Optional[str] = None

@dataclass
class Event:
    """Immutable event in the append-only log."""
    event_seq: int
    event_type: str
    instance_id: str
    timestamp: str
    payload: Dict[str, Any]

# ─── Lock Management ────────────────────────────────────────────────────────

_instance_registry_locks: Dict[str, Lock] = {}
_event_log_locks: Dict[str, Lock] = {}
_projection_cache_lock = Lock()
_projection_cache: Dict[str, tuple] = {}  # key -> (monotonic_timestamp, content)
PROJECTION_CACHE_TTL = 30.0  # seconds

def _get_registry_lock(entity: str) -> Lock:
    if entity not in _instance_registry_locks:
        _instance_registry_locks[entity] = Lock()
    return _instance_registry_locks[entity]

def _get_event_log_lock(entity: str, log_type: str) -> Lock:
    key = f"{entity}:{log_type}"
    if key not in _event_log_locks:
        _event_log_locks[key] = Lock()
    return _event_log_locks[key]

# ─── Instance Registry ──────────────────────────────────────────────────────

async def register_instance(channel: str, entity: str) -> InstanceRecord:
    """
    Register a new agent instance.
    
    Must be called at session start, before any file writes.
    Returns the instance record with generated instance_id.
    """
    session_uuid = str(uuid7())
    instance_id = f"{channel}/{entity}/{session_uuid}"
    
    record = InstanceRecord(
        instance_id=instance_id,
        channel=channel,
        entity=entity,
        session_uuid=session_uuid,
        pid=os.getpid(),
        started_at=datetime.now(timezone.utc).isoformat(),
        status="active"
    )
    
    entity_dir = INSTANCES_DIR / entity
    entity_dir.mkdir(parents=True, exist_ok=True)
    registry_path = entity_dir / "registry.jsonl"
    
    lock = _get_registry_lock(entity)
    async with lock:
        async with await anyio.open_file(registry_path, "a") as f:
            await f.write(json.dumps(asdict(record)) + "\n")
    
    return record

async def deregister_instance(instance_id: str) -> None:
    """Mark instance as terminated."""
    try:
        _, entity, _ = instance_id.split("/", 2)
    except ValueError:
        return  # Malformed instance_id
    
    entity_dir = INSTANCES_DIR / entity
    registry_path = entity_dir / "registry.jsonl"
    
    if not registry_path.exists():
        return
    
    lock = _get_registry_lock(entity)
    async with lock:
        records = []
        async with await anyio.open_file(registry_path, "r") as f:
            async for line in f:
                rec = json.loads(line)
                if rec["instance_id"] == instance_id:
                    rec["status"] = "terminated"
                records.append(rec)
        
        # Atomic rewrite
        tmp_path = registry_path.with_suffix(".tmp")
        async with await anyio.open_file(tmp_path, "w") as f:
            for rec in records:
                await f.write(json.dumps(rec) + "\n")
        os.replace(tmp_path, registry_path)

async def update_instance_heartbeat(instance_id: str) -> None:
    """Update last_heartbeat timestamp for an instance."""
    try:
        _, entity, _ = instance_id.split("/", 2)
    except ValueError:
        return
    
    entity_dir = INSTANCES_DIR / entity
    registry_path = entity_dir / "registry.jsonl"
    
    if not registry_path.exists():
        return
    
    lock = _get_registry_lock(entity)
    async with lock:
        records = []
        async with await anyio.open_file(registry_path, "r") as f:
            async for line in f:
                rec = json.loads(line)
                if rec["instance_id"] == instance_id:
                    rec["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
                records.append(rec)
        
        tmp_path = registry_path.with_suffix(".tmp")
        async with await anyio.open_file(tmp_path, "w") as f:
            for rec in records:
                await f.write(json.dumps(rec) + "\n")
        os.replace(tmp_path, registry_path)

async def get_active_instances(entity: str) -> List[InstanceRecord]:
    """Get all active instances for an entity."""
    registry_path = INSTANCES_DIR / entity / "registry.jsonl"
    if not registry_path.exists():
        return []
    
    records = []
    async with await anyio.open_file(registry_path, "r") as f:
        async for line in f:
            rec = json.loads(line)
            if rec["status"] == "active":
                records.append(InstanceRecord(**rec))
    return records

async def get_all_instances(entity: str) -> List[InstanceRecord]:
    """Get all instances (active + terminated) for an entity."""
    registry_path = INSTANCES_DIR / entity / "registry.jsonl"
    if not registry_path.exists():
        return []
    
    records = []
    async with await anyio.open_file(registry_path, "r") as f:
        async for line in f:
            records.append(InstanceRecord(**json.loads(line)))
    return records

# ─── Event Log (Append-Only) ────────────────────────────────────────────────

async def append_event(
    entity: str,
    log_type: str,  # "anchored_summary" or "session_gnosis"
    event_type: str,
    payload: Dict[str, Any],
    instance_id: str
) -> int:
    """
    Append event to log. Returns event_seq.
    
    Thread-safe and cross-process safe via fcntl file locking.
    """
    if log_type == "anchored_summary":
        log_dir = ANCHORED_EVENTS_DIR / entity
    elif log_type == "session_gnosis":
        log_dir = GNOSIS_EVENTS_DIR / entity
    else:
        raise ValueError(f"Unknown log_type: {log_type}")
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "events.jsonl"
    
    lock = _get_event_log_lock(entity, log_type)
    async with lock:
        # File lock for cross-process safety
        def _append_sync() -> int:
            with open(log_path, "a") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    # Read current max event_seq
                    event_seq = 0
                    if log_path.exists():
                        with open(log_path, "r") as rf:
                            for line in rf:
                                if line.strip():
                                    event_seq = max(event_seq, json.loads(line)["event_seq"])
                    
                    event_seq += 1
                    event = Event(
                        event_seq=event_seq,
                        event_type=event_type,
                        instance_id=instance_id,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        payload=payload
                    )
                    
                    f.write(json.dumps(asdict(event)) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                    return event_seq
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        event_seq = await anyio.to_thread.run_sync(_append_sync)
    
    # Invalidate projection cache
    await _invalidate_projection_cache(entity, log_type)
    
    return event_seq

async def read_events(
    entity: str,
    log_type: str,
    from_seq: int = 0,
    limit: Optional[int] = None
) -> List[Event]:
    """Read events from log."""
    if log_type == "anchored_summary":
        log_path = ANCHORED_EVENTS_DIR / entity / "events.jsonl"
    else:
        log_path = GNOSIS_EVENTS_DIR / entity / "events.jsonl"
    
    if not log_path.exists():
        return []
    
    events = []
    async with await anyio.open_file(log_path, "r") as f:
        async for line in f:
            if line.strip():
                event = Event(**json.loads(line))
                if event.event_seq >= from_seq:
                    events.append(event)
                    if limit and len(events) >= limit:
                        break
    return events

async def get_latest_event(entity: str, log_type: str) -> Optional[Event]:
    """Get the most recent event."""
    events = await read_events(entity, log_type, limit=1)
    return events[0] if events else None

# ─── Projection Cache ───────────────────────────────────────────────────────

async def _invalidate_projection_cache(entity: str, log_type: str) -> None:
    key = f"{entity}:{log_type}"
    async with _projection_cache_lock:
        _projection_cache.pop(key, None)

async def _get_cached_projection(entity: str, log_type: str, projector_fn) -> str:
    key = f"{entity}:{log_type}"
    now = time.monotonic()
    
    async with _projection_cache_lock:
        if key in _projection_cache:
            ts, content = _projection_cache[key]
            if now - ts < PROJECTION_CACHE_TTL:
                return content
    
    # Cache miss — compute projection
    content = await projector_fn(entity)
    
    async with _projection_cache_lock:
        _projection_cache[key] = (now, content)
    
    return content

# ─── Projectors (Pure Functions) ────────────────────────────────────────────

async def project_anchored_summary(entity: str) -> str:
    """Project anchored summary from event log. Deterministic, no LLM calls."""
    events = await read_events(entity, "anchored_summary")
    
    # Find latest session_start
    session_starts = [e for e in events if e.event_type == "session_start"]
    latest_start = session_starts[-1] if session_starts else None
    
    # Find latest compaction/session_end
    compactions = [e for e in events if e.event_type in ("compaction", "session_end")]
    latest_compaction = compactions[-1] if compactions else None
    
    # Collect decisions
    decisions = [e for e in events if e.event_type == "decision"]
    
    # Collect task completions
    tasks = [e for e in events if e.event_type == "task_complete"]
    
    # Get active instances
    instances = await get_active_instances(entity)
    
    # Build markdown
    lines = [
        f"# 🔱 Omega Engine — Anchored Summary (MIAP Projected)",
        f"**Entity**: {entity}",
        f"**Projected**: {datetime.now(timezone.utc).isoformat()}",
        f"**Event Count**: {len(events)}",
        f"**Active Instances**: {len(instances)}",
        "---"
    ]
    
    if latest_start:
        lines.extend([
            f"## 🎯 Current Objective",
            latest_start.payload.get("objective", "Unknown"),
            f"**Model**: {latest_start.payload.get('model', 'unknown')}",
            f"**Instance**: {latest_start.instance_id}",
            "---"
        ])
    
    if decisions:
        lines.append("## 📋 Strategic Decisions")
        for d in decisions:
            inst_short = d.instance_id.split('/')[-1][:8]
            lines.append(f"- **{d.timestamp[:19]}** ({inst_short}): {d.payload.get('decision', 'N/A')}")
            if d.payload.get("rationale"):
                lines.append(f"  > {d.payload['rationale']}")
        lines.append("---")
    
    if tasks:
        lines.append("## ✅ Completed Tasks")
        for t in tasks[-10:]:  # Last 10
            inst_short = t.instance_id.split('/')[-1][:8]
            lines.append(f"- **{t.timestamp[:19]}** ({inst_short}): {t.payload.get('task', 'N/A')}")
        lines.append("---")
    
    if instances:
        lines.append("## 👥 Active Instances")
        for inst in instances:
            lines.append(f"- `{inst.instance_id}` (PID: {inst.pid}, since {inst.started_at[:19]})")
        lines.append("---")
    
    if latest_compaction:
        lines.extend([
            f"## 🔄 Last Compaction / Session End",
            f"**Trigger**: {latest_compaction.payload.get('trigger', 'unknown')}",
            f"**Next Action**: {latest_compaction.payload.get('next_action', 'unknown')}",
            f"**Instance**: {latest_compaction.instance_id}",
            "---"
        ])
    
    return "\n".join(lines)

async def project_session_gnosis(entity: str) -> str:
    """Project unified session gnosis from event log. Deterministic, no LLM calls."""
    events = await read_events(entity, "session_gnosis")
    
    # Group by section
    sections: Dict[str, List[Dict]] = {}
    distillations = []
    
    for e in events:
        if e.event_type == "gnosis_entry":
            section = e.payload.get("section", "Uncategorized")
            if section not in sections:
                sections[section] = []
            sections[section].append({
                "content": e.payload.get("content", ""),
                "instance": e.instance_id,
                "timestamp": e.timestamp
            })
        elif e.event_type == "distillation":
            distillations.append(e.payload)
    
    # Build markdown
    lines = [
        f"# 🔱 Session Gnosis — {entity} (MIAP Projected)",
        f"**Projected**: {datetime.now(timezone.utc).isoformat()}",
        f"**Event Count**: {len(events)}",
        "---"
    ]
    
    # L1 Narrative
    if "L1_Narrative" in sections:
        lines.append("## 📖 L1 Narrative")
        for entry in sections["L1_Narrative"]:
            inst_short = entry['instance'].split('/')[-1][:8]
            lines.append(f"\n### {entry['timestamp'][:19]} — {inst_short}")
            lines.append(entry["content"])
        lines.append("---")
    
    # L2 Insights
    if "L2_Insight" in sections:
        lines.append("## 💡 L2 Insights")
        for entry in sections["L2_Insight"]:
            inst_short = entry['instance'].split('/')[-1][:8]
            lines.append(f"\n### {entry['timestamp'][:19]} — {inst_short}")
            lines.append(entry["content"])
        lines.append("---")
    
    # L3 Principles (deduplicated by content hash)
    if "L3_Principle" in sections:
        lines.append("## ⚖️ L3 Universal Principles")
        seen_hashes = set()
        for entry in sections["L3_Principle"]:
            content_hash = hashlib.sha256(entry["content"].encode()).hexdigest()[:16]
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                inst_short = entry['instance'].split('/')[-1][:8]
                lines.append(f"\n### {entry['timestamp'][:19]} — {inst_short}")
                lines.append(entry["content"])
        lines.append("---")
    
    # Distillations
    if distillations:
        lines.append("## 🧪 Distillations (L1→L2→L3)")
        for d in distillations:
            lines.append(f"\n### {d.get('timestamp', '')[:19]}")
            lines.append(f"**L1**: {d.get('l1', 'N/A')}")
            lines.append(f"**L2**: {d.get('l2', 'N/A')}")
            lines.append(f"**L3**: {d.get('l3', 'N/A')}")
            if d.get("proposed_lesson"):
                lines.append(f"**Proposed Lesson**: {d['proposed_lesson']}")
        lines.append("---")
    
    return "\n".join(lines)

# ─── Public API: Write Projections ──────────────────────────────────────────

async def write_projections(entity: str) -> None:
    """Write both projections to canonical locations + symlinks."""
    # Anchored Summary
    anchored_content = await project_anchored_summary(entity)
    anchored_canonical = ANCHORED_EVENTS_DIR / entity / "projection.md"
    anchored_canonical.parent.mkdir(parents=True, exist_ok=True)
    anchored_canonical.write_text(anchored_content)
    
    # Symlink at .opencode/anchored-summary.md (use absolute path)
    opencode_anchored = PROJECT_ROOT / ".opencode" / "anchored-summary.md"
    try:
        opencode_anchored.unlink()
    except FileNotFoundError:
        pass
    opencode_anchored.symlink_to(anchored_canonical.resolve())
    
    # Session Gnosis
    gnosis_content = await project_session_gnosis(entity)
    gnosis_canonical = GNOSIS_EVENTS_DIR / entity / "projection.md"
    gnosis_canonical.parent.mkdir(parents=True, exist_ok=True)
    gnosis_canonical.write_text(gnosis_content)
    
    # Symlink at entity workspace (use absolute path)
    entity_gnosis = PROJECT_ROOT / "data" / "entities" / entity / "workspace" / "session_gnosis.md"
    entity_gnosis.parent.mkdir(parents=True, exist_ok=True)
    try:
        entity_gnosis.unlink()
    except FileNotFoundError:
        pass
    entity_gnosis.symlink_to(gnosis_canonical.resolve())

# ─── Convenience Writers ────────────────────────────────────────────────────

async def write_anchored_event(
    entity: str,
    event_type: str,
    payload: Dict[str, Any],
    instance_id: str
) -> int:
    """Convenience: write anchored summary event."""
    return await append_event(entity, "anchored_summary", event_type, payload, instance_id)

async def write_gnosis_entry(
    entity: str,
    section: str,  # "L1_Narrative", "L2_Insight", "L3_Principle"
    content: str,
    instance_id: str
) -> int:
    """Convenience: write gnosis entry."""
    return await append_event(entity, "session_gnosis", "gnosis_entry", {
        "section": section,
        "content": content
    }, instance_id)

async def write_distillation(
    entity: str,
    l1: str,
    l2: str,
    l3: str,
    proposed_lesson: str,
    instance_id: str
) -> int:
    """Convenience: write L1→L2→L3 distillation."""
    return await append_event(entity, "session_gnosis", "distillation", {
        "l1": l1,
        "l2": l2,
        "l3": l3,
        "proposed_lesson": proposed_lesson,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, instance_id)

# ─── CLI Entry Point ────────────────────────────────────────────────────────

async def miap_cli(entity: str, action: str, **kwargs) -> None:
    """CLI entry point for MIAP operations."""
    if action == "register":
        channel = kwargs.get("channel", "opencode")
        record = await register_instance(channel, entity)
        print(f"Registered: {record.instance_id}")
    
    elif action == "project":
        await write_projections(entity)
        print(f"Projections written for {entity}")
    
    elif action == "status":
        instances = await get_active_instances(entity)
        print(f"Active instances for {entity}: {len(instances)}")
        for inst in instances:
            print(f"  {inst.instance_id} (PID: {inst.pid})")
    
    elif action == "events":
        log_type = kwargs.get("log_type", "anchored_summary")
        tail = kwargs.get("tail", 20)
        events = await read_events(entity, log_type)
        for e in events[-tail:]:
            inst_short = e.instance_id.split('/')[-1][:8]
            payload_preview = json.dumps(e.payload)[:80]
            print(f"{e.event_seq:4d} {e.timestamp[:19]} {e.event_type:15s} {inst_short} {payload_preview}")
    
    elif action == "deregister":
        instance_id = kwargs.get("instance_id")
        if instance_id:
            await deregister_instance(instance_id)
            print(f"Deregistered: {instance_id}")
    
    else:
        raise ValueError(f"Unknown action: {action}")

# ─── Module Exports ──────────────────────────────────────────────────────────

__all__ = [
    # Instance Registry
    "register_instance",
    "deregister_instance",
    "update_instance_heartbeat",
    "get_active_instances",
    "get_all_instances",
    "InstanceRecord",
    # Event Log
    "append_event",
    "read_events",
    "get_latest_event",
    "Event",
    # Projections
    "project_anchored_summary",
    "project_session_gnosis",
    "write_projections",
    # Convenience Writers
    "write_anchored_event",
    "write_gnosis_entry",
    "write_distillation",
    # CLI
    "miap_cli",
]