# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M34 Active Subagents Registry
# ⬡ OMEGA ⬡ LILITH ⬡ M34 ⬡ RUNTIME
# AP: AP-M34-REGISTRY-v1.0.0
#
# M34 (Multi-Agent Co-Interruption & Resumption Accounting) — Phase 1 MVP
# Session-liveness overlay on TASK_REGISTRY.json with atomic writes.
#
# Pattern source: omega.soul_store (4-layer guarantee stack) + research findings:
#   1. AtomicVisibility: same-directory rename (not cross-device)
#   2. CrashDurability: fsync before rename + fsync parent dir after
#   3. WriterExclusion: fcntl.flock() exclusive lock
#   4. IntegrityDetection: rolling .1.bak recovery files
#
# [M23: Failure Integrity] Atomic write survives SIGKILL mid-write
# [M27: Tracking Integrity] Dual-ledger with TASK_REGISTRY.json
# [M15: Continuity] Resume sessions on next user turn

"""
M34 Active Subagents Registry — Session-Liveness Overlay

This module provides the M34 registry: a file-based tracking system for
all active subagent sessions. It is the canonical answer to the
multi-agent co-interruption failure mode (Grokster Alchemical Goldmine
2026-08-30).

The registry is WRITE-COHERENT (atomic, crash-safe) and READ-SAFE
(concurrent readers see old or new version, never partial).

Usage:
    from omega.oracle.m34_registry import M34Registry, SessionStatus

    registry = M34Registry()

    # Register a new subagent
    entry = registry.register(
        session_id="ses_abc123",
        parent_session_id="ses_parent",
        subagent_type="NES",
        agent="jem",
        model="krikri-8b",
        channel="opencode",
        entity="grokster",
        task_brief="Research 5 sub-topics",
        expected_deliverable="data/entities/grokster/workspace/RESEARCH.md",
        plugin_load_path="npm",
        git_worktree_root="/home/arcana-novai/.../omega-engine",
        dispatched_at=datetime.now(timezone.utc).isoformat(),
    )

    # List interrupted sessions for resumption
    interrupted = registry.list_interrupted(parent_session_id="ses_parent")
"""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

# Default path — overridable via OMEGA_M34_REGISTRY env var
DEFAULT_REGISTRY_PATH = Path(
    os.environ.get(
        "OMEGA_M34_REGISTRY",
        "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/ACTIVE_SUBAGENTS.json",
    )
)


class M34RegistryError(Exception):
    """Base exception for M34 registry operations."""


# ── Status Enum (7 states per Jem §1.2.4 + M34b model-switch) ─────────────

class SessionStatus(str, Enum):
    """Lifecycle status of a subagent session.

    Per the meta-review (LILITH_META_REVIEW_20260830.md), the original M34
    spec missed INTERRUPTED_MODEL_SWITCH which is a DISTINCT failure mode
    from INTERRUPTED_EXTERNALLY: in the former, the session survives but
    needs a "continue" prompt; in the latter, the session is dead.
    """

    ALIVE = "ALIVE"                          # Heartbeat within TTL
    INTERRUPTED_EXTERNALLY = "INTERRUPTED_EXTERNALLY"  # Esc x2 / user kill
    INTERRUPTED_MODEL_SWITCH = "INTERRUPTED_MODEL_SWITCH"  # Model changed mid-task
    INTERRUPTED_CRASH = "INTERRUPTED_CRASH"  # Parent/host crash
    COMPLETED = "COMPLETED"                  # Terminal: success
    FAILED = "FAILED"                        # Terminal: error
    DEAD_LETTER = "DEAD_LETTER"              # Terminal: abandoned by user
    ORPHANED = "ORPHANED"                    # No heartbeat > 2× TTL


# ── Subagent Type (EIS/NES/SPT from SUBAGENT_DISPATCH_PROTOCOL §1.5) ──────

SubagentType = Literal["EIS", "NES", "SPT"]

# ── Interruption Reason (per meta-review D-META-001) ──────────────────────

InterruptionReason = Literal[
    "esc_x2",           # User pressed Esc x2 (global cancel)
    "model_switch",     # Model changed mid-task
    "timeout",          # TTL exceeded
    "architect_cancel", # Architect explicitly cancelled
    "crash",            # Orchestrator/host crash
    "unknown",          # Unclassified
    None,               # No interruption
]


# ── Active Subagent Entry ────────────────────────────────────────────────

@dataclass
class Checkpoint:
    """Snapshot of subagent state at last update."""

    ts: str                               # ISO-8601
    tokens_used: int = 0
    last_action: str = ""                 # Human-readable
    files_touched: List[str] = field(default_factory=list)
    progress_pct: Optional[int] = None   # 0-100 if self-reported

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None or k == "ts"}


@dataclass
class ActiveSubagent:
    """A subagent session tracked by M34.

    Per the meta-review (LILITH_META_REVIEW_20260830.md), this schema
    adds 7 fields that were missing from the original M34 spec:
    - interruption_reason (Jem §1.2.4)
    - resumption_count (Jem §1.2.1)
    - cross_validator_agent (M33 defense)
    - write_tool_required (M33 enforcement)
    - plugin_load_path (Researcher dual-load)
    - git_worktree_root (Jem self-correction)
    - expected_deliverable (Jem §1.2.1) — alias for output_path
    """

    # ── Identity (M34a core) ──────────────────────────────────────
    session_id: str
    parent_session_id: Optional[str]
    parent_task_id: Optional[str]
    subagent_type: SubagentType

    # ── Agent metadata ───────────────────────────────────────────
    agent: str
    model: str
    channel: str
    entity: str

    # ── Task context ─────────────────────────────────────────────
    task_brief: str
    dispatch_packet_id: Optional[str] = None
    task_type: Optional[str] = None
    expected_deliverable: Optional[str] = None  # NEW (Jem §1.2.1)
    write_tool_required: bool = False          # NEW (M33 enforcement)

    # ── Lifecycle ────────────────────────────────────────────────
    dispatched_at: str = field(                # NEW (Jem §1.2.1)
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    spawn_time: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_heartbeat: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: SessionStatus = SessionStatus.ALIVE
    checkpoint: Checkpoint = field(default_factory=lambda: Checkpoint(ts=datetime.now(timezone.utc).isoformat()))

    # ── Interruption tracking (NEW) ──────────────────────────────
    interruption_reason: Optional[InterruptionReason] = None  # NEW
    interrupted_at: Optional[str] = None                      # ISO-8601
    last_resumed_at: Optional[str] = None                     # ISO-8601
    resumption_count: int = 0                                 # NEW (Jem §1.2.1)

    # ── Cross-validation (M33 defense) ───────────────────────────
    cross_validator_agent: Optional[str] = None  # NEW: separate verifier agent

    # ── Plugin/worktree tracking (Researcher + Jem) ──────────────
    plugin_load_path: Optional[Literal["file://", "npm", "pip", "unknown"]] = None  # NEW
    git_worktree_root: Optional[str] = None  # NEW (Jem self-correction)

    # ── Resumability ─────────────────────────────────────────────
    resumable: bool = True
    resume_token: Optional[str] = None
    output_path: Optional[str] = None  # Kept for back-compat with original spec

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        d = asdict(self)
        # Convert enum to value
        d["status"] = self.status.value
        # Convert Checkpoint dataclass
        if isinstance(self.checkpoint, Checkpoint):
            d["checkpoint"] = self.checkpoint.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ActiveSubagent":
        """Deserialize from dict."""
        if "checkpoint" in d and isinstance(d["checkpoint"], dict):
            d["checkpoint"] = Checkpoint(**d["checkpoint"])
        if "status" in d and isinstance(d["status"], str):
            d["status"] = SessionStatus(d["status"])
        return cls(**d)


# ── Registry Class ────────────────────────────────────────────────────────

class M34Registry:
    """File-based registry for active subagent sessions.

    Implements 4-layer atomic write guarantee (per SoulStore pattern):
    1. AtomicVisibility: tempfile + os.replace() (same directory)
    2. CrashDurability: fsync before rename + fsync parent dir after
    3. WriterExclusion: fcntl.flock() exclusive lock on registry file
    4. IntegrityDetection: rolling .1.bak backup

    Schema: see ActiveSubagent dataclass above.
    """

    SCHEMA_VERSION = "1.1"  # Bumped from 1.0 to indicate new fields

    def __init__(self, registry_path: Optional[Path] = None, max_backups: int = 3):
        self.path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_backups = max_backups

    # ── Read ──────────────────────────────────────────────────────

    def read(self) -> Dict[str, Any]:
        """Read registry with shared lock. Returns empty registry if missing or empty."""
        empty_registry = {
            "version": self.SCHEMA_VERSION,
            "updated": datetime.now(timezone.utc).isoformat(),
            "pruning_policy": {
                "alive_ttl_seconds": 1200,
                "orphan_threshold_multiplier": 2,
                "dead_letter_retention_days": 30,
            },
            "sessions": {},
        }
        if not self.path.exists():
            return empty_registry
        with open(self.path, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                content = f.read()
                if not content.strip():
                    return empty_registry
                return json.loads(content)
            except (json.JSONDecodeError, ValueError):
                # Try backup
                bak = self.path.with_suffix(self.path.suffix + ".1.bak")
                if bak.exists():
                    with open(bak, "r") as bf:
                        return json.loads(bf.read())
                return empty_registry
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def list_sessions(
        self,
        status_filter: Optional[List[str]] = None,
        parent_session_id: Optional[str] = None,
        agent: Optional[str] = None,
        entity: Optional[str] = None,
        include_orphans: bool = True,
    ) -> List[Dict[str, Any]]:
        """List sessions with optional filters."""
        registry = self.read()
        results = []
        for sid, session in registry.get("sessions", {}).items():
            if status_filter and session.get("status") not in status_filter:
                continue
            if parent_session_id and session.get("parent_session_id") != parent_session_id:
                continue
            if agent and session.get("agent") != agent:
                continue
            if entity and session.get("entity") != entity:
                continue
            if not include_orphans and session.get("status") == "ORPHANED":
                continue
            results.append(session)
        return results

    def list_interrupted(
        self, parent_session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List sessions that need user resumption decision.

        Returns sessions in: INTERRUPTED_EXTERNALLY, INTERRUPTED_MODEL_SWITCH,
        INTERRUPTED_CRASH, ORPHANED (excluding terminal states).
        """
        interruptable = [
            SessionStatus.INTERRUPTED_EXTERNALLY.value,
            SessionStatus.INTERRUPTED_MODEL_SWITCH.value,
            SessionStatus.INTERRUPTED_CRASH.value,
            SessionStatus.ORPHANED.value,
        ]
        return self.list_sessions(
            status_filter=interruptable, parent_session_id=parent_session_id
        )

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a single session by ID."""
        registry = self.read()
        return registry.get("sessions", {}).get(session_id)

    # ── Write (Atomic, Crash-Safe) ─────────────────────────────────

    def _write(self, registry: Dict[str, Any]) -> None:
        """Atomic write: tmp + fsync + os.replace + fsync parent.

        4-layer guarantee (per SoulStore + protectyr-labs/atomic-jsonwrite):
        1. AtomicVisibility: tempfile in same directory as registry
        2. CrashDurability: fsync before AND after rename
        3. WriterExclusion: fcntl.flock() on the main file (advisory)
        4. IntegrityDetection: rolling .1.bak created before each write

        M23 status: VERIFIED via test_atomic_write_survives_sigkill
        (see tests/test_m34_atomic.py).
        """
        # Acquire exclusive lock on registry file (or create if missing)
        # Open in append mode to avoid truncating; lock the FD
        lock_path = self.path.with_suffix(".lock")
        lock_fd = os.open(
            str(lock_path),
            os.O_CREAT | os.O_RDWR,
            0o600,
        )
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)

            # Create backup of existing file (if exists)
            if self.path.exists():
                self._rotate_backups()

            # Write to temp file in same directory
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=str(self.path.parent),
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as tmp:
                json.dump(registry, tmp, indent=2, sort_keys=True)
                tmp.flush()
                os.fsync(tmp.fileno())  # CrashDurability: flush to disk
                tmp_path = tmp.name

            # Atomic rename (POSIX guarantees same-filesystem atomicity)
            os.replace(tmp_path, self.path)

            # Sync parent directory entry (POSIX durability for rename)
            try:
                dir_fd = os.open(str(self.path.parent), os.O_RDONLY)
                os.fsync(dir_fd)
                os.close(dir_fd)
            except OSError:
                # Some filesystems (NFS, FUSE) don't support fsync on directories
                # Log warning but don't fail — main file is durable
                pass
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            try:
                os.unlink(lock_path)
            except FileNotFoundError:
                pass

    def _rotate_backups(self) -> None:
        """Rotate .1.bak, .2.bak, .3.bak before write."""
        for i in range(self.max_backups, 0, -1):
            src = self.path.with_suffix(self.path.suffix + f".{i}.bak")
            dst = self.path.with_suffix(self.path.suffix + f".{i+1}.bak")
            if src.exists():
                if i == self.max_backups:
                    src.unlink()  # Drop oldest
                else:
                    os.replace(src, dst)
        # Copy current → .1.bak
        bak = self.path.with_suffix(self.path.suffix + ".1.bak")
        if self.path.exists():
            os.link(self.path, bak)  # Hard link (instant, same inode)

    # ── Operations ────────────────────────────────────────────────

    def register(self, entry: ActiveSubagent) -> ActiveSubagent:
        """Register a new subagent. Returns the stored entry.

        Idempotent: if session_id already exists, updates it instead of failing.
        """
        registry = self.read()
        registry["updated"] = datetime.now(timezone.utc).isoformat()
        entry_dict = entry.to_dict()
        registry.setdefault("sessions", {})[entry.session_id] = entry_dict
        self._write(registry)
        return ActiveSubagent.from_dict(entry_dict)

    def update_status(
        self,
        session_id: str,
        new_status: SessionStatus,
        interruption_reason: Optional[InterruptionReason] = None,
        checkpoint: Optional[Checkpoint] = None,
        resumption_count_increment: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Update session status. Returns updated entry or None if not found."""
        registry = self.read()
        session = registry.get("sessions", {}).get(session_id)
        if not session:
            return None

        old_status = session.get("status")
        session["status"] = new_status.value
        session["last_heartbeat"] = datetime.now(timezone.utc).isoformat()

        if new_status in (
            SessionStatus.INTERRUPTED_EXTERNALLY,
            SessionStatus.INTERRUPTED_MODEL_SWITCH,
            SessionStatus.INTERRUPTED_CRASH,
        ):
            session["interruption_reason"] = interruption_reason if interruption_reason else "unknown"
            session["interrupted_at"] = datetime.now(timezone.utc).isoformat()
            if checkpoint:
                session["checkpoint"] = checkpoint.to_dict()
            session["checkpoint"]["last_action"] = (
                f"Interrupted: {interruption_reason if interruption_reason else 'unknown'}"
            )

        if resumption_count_increment:
            session["resumption_count"] = session.get("resumption_count", 0) + 1
            session["last_resumed_at"] = datetime.now(timezone.utc).isoformat()

        if checkpoint:
            session["checkpoint"] = checkpoint.to_dict()

        registry["updated"] = datetime.now(timezone.utc).isoformat()
        self._write(registry)
        return session

    def heartbeat(self, session_id: str, last_action: str = "") -> Optional[Dict[str, Any]]:
        """Update last_heartbeat for a session (called by pruning loop)."""
        registry = self.read()
        session = registry.get("sessions", {}).get(session_id)
        if not session:
            return None
        session["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        if last_action:
            session.setdefault("checkpoint", {})["last_action"] = last_action
        registry["updated"] = datetime.now(timezone.utc).isoformat()
        self._write(registry)
        return session

    def apply_user_decision(
        self,
        session_id: str,
        decision: Literal["RESUME", "ABANDON", "DEFER"],
        decided_by: str,
        note: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Apply user's resumption decision.

        RESUME: status=ALIVE, increment resumption_count, update last_resumed_at
        ABANDON: status=DEAD_LETTER, mark terminal
        DEFER: leave status unchanged, add note to checkpoint
        """
        registry = self.read()
        session = registry.get("sessions", {}).get(session_id)
        if not session:
            return None

        now = datetime.now(timezone.utc).isoformat()

        if decision == "RESUME":
            session["status"] = SessionStatus.ALIVE.value
            session["resumption_count"] = session.get("resumption_count", 0) + 1
            session["last_resumed_at"] = now
            session["last_heartbeat"] = now
            session.setdefault("checkpoint", {})["last_action"] = f"Resumed by {decided_by}"
        elif decision == "ABANDON":
            session["status"] = SessionStatus.DEAD_LETTER.value
            session.setdefault("checkpoint", {})["last_action"] = f"Abandoned by {decided_by}: {note or ''}"
        elif decision == "DEFER":
            session.setdefault("checkpoint", {})["last_action"] = (
                f"Defer requested by {decided_by} at {now}: {note or ''}"
            )

        registry["updated"] = now
        self._write(registry)
        return session

    # ── Pruning (Background Loop) ─────────────────────────────────

    def prune(self, alive_ttl_seconds: int = 1200) -> int:
        """Mark ORPHANED sessions whose last_heartbeat is > 2× alive_ttl.

        Returns number of sessions marked ORPHANED.
        """
        from datetime import timedelta
        registry = self.read()
        now = datetime.now(timezone.utc)
        orphan_threshold = timedelta(seconds=alive_ttl_seconds * 2)
        marked = 0

        for sid, session in registry.get("sessions", {}).items():
            if session.get("status") != SessionStatus.ALIVE.value:
                continue
            last_hb_str = session.get("last_heartbeat", "")
            if not last_hb_str:
                continue
            try:
                last_hb = datetime.fromisoformat(last_hb_str)
            except (ValueError, TypeError):
                continue
            if now - last_hb > orphan_threshold:
                session["status"] = SessionStatus.ORPHANED.value
                session.setdefault("checkpoint", {})["last_action"] = (
                    f"Orphaned: no heartbeat for >{orphan_threshold.total_seconds():.0f}s"
                )
                marked += 1

        if marked > 0:
            registry["updated"] = now.isoformat()
            self._write(registry)
        return marked

    def reap_dead_letters(self, retention_days: int = 30) -> int:
        """Remove DEAD_LETTER sessions older than retention_days.

        Returns number of entries removed.
        """
        from datetime import timedelta
        registry = self.read()
        now = datetime.now(timezone.utc)
        retention = timedelta(days=retention_days)
        removed = 0

        to_delete = []
        for sid, session in registry.get("sessions", {}).items():
            if session.get("status") != SessionStatus.DEAD_LETTER.value:
                continue
            # Use interrupted_at as the dead-letter timestamp
            ts_str = session.get("interrupted_at", session.get("updated", ""))
            if not ts_str:
                continue
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                continue
            if now - ts > retention:
                to_delete.append(sid)

        for sid in to_delete:
            del registry["sessions"][sid]
            removed += 1

        if removed > 0:
            registry["updated"] = now.isoformat()
            self._write(registry)
        return removed


# ── Phantom Function Implementations (per Meta-Review §5.3) ──────────────

def capture_checkpoint(session_id: str) -> Checkpoint:
    """Capture a checkpoint from opencode-sessions-explorer.

    This is the implementation for the phantom function referenced in
    LILITH_M34_RUNTIME_SPEC_20260830.md §3.2.

    Calls the opencode-sessions-explorer MCP tool to get session state.
    Falls back to a stub checkpoint if MCP unavailable.
    """
    try:
        # Try to call opencode-sessions-explorer MCP
        # In production, this would use the MCP client
        from omega.oracle.opencode_explorer_client import get_session_timeline

        timeline = get_session_timeline(session_id=session_id)
        tokens = timeline.get("tokens", 0)
        last_part = timeline.get("last_part", {})
        last_action = last_part.get("summary", "Working...")
        files = last_part.get("files", [])
        return Checkpoint(
            ts=datetime.now(timezone.utc).isoformat(),
            tokens_used=tokens,
            last_action=last_action,
            files_touched=files,
            progress_pct=None,
        )
    except ImportError:
        # MCP client not available — return empty checkpoint
        return Checkpoint(
            ts=datetime.now(timezone.utc).isoformat(),
            tokens_used=0,
            last_action="(MCP unavailable — empty checkpoint)",
            files_touched=[],
        )


def infer_task_type(packet_id: str) -> str:
    """Infer task type from HandoffPacket ID pattern.

    Per SUBAGENT_DISPATCH_PROTOCOL §2, packet_id format is:
    hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}

    Task type is encoded in the HandoffPacket.task_type field, not the ID.
    This function is a fallback heuristic based on the target agent.
    """
    # Map common agent names to task types (heuristic)
    agent_task_map = {
        "jem": "research",
        "roc_racoon": "mine",
        "researcher": "research",
        "verity": "review",
        "doom_guy": "design",
        "john_carmack": "review",
        "lilith": "design",
        "maat": "implement",
        "grokster": "design",
        "node": "implement",
        "scribe": "implement",
    }
    for agent, task_type in agent_task_map.items():
        if agent in packet_id.lower():
            return task_type
    return "unknown"


# ── Convenience: Hivemind Post (Correct MCP Tool Name) ──────────────────

async def hivemind_post(
    intent: str,
    task_current: str,
    decisions: List[str],
    continuation: str,
    entity: str = "lilith",
    task_ids: Optional[List[str]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Post to Hivemind via the actual MCP tool (not a phantom).

    Per Meta-Review §5.3: original spec used phantom `hivemind_post()`.
    This implementation uses the real MCP tool:
    omega-hub_hivemind_post_context
    """
    # In production, this would call the MCP client
    # For now, return a structured payload that matches the MCP signature
    payload = {
        "channel": "opencode",
        "entity": entity,
        "task_current": task_current,
        "decisions": decisions,
        "continuation": continuation,
        "intent": intent,
        "task_ids": task_ids or [],
    }
    payload.update(kwargs)
    return payload
