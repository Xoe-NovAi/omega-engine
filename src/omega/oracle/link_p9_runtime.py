# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Engine — Link P9 Runtime (Agent Handoff & Delegation)
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ LINK-P9
# AP: LINK-P9-v1.0.0
#
# Agent presence tracking, HandoffPacket lifecycle management,
# task queue for inter-agent delegation.
#
# [id-soft: doom3-2004] idEntity event system — agents emit typed events,
#     other agents consume them. Link P9 is the engine's event bus for agents.
# [id-soft: doom-1993] ZONEID Pattern — used for presence integrity.
# [id-soft: quake-1996] Thinker chain — spawn → execute → reap lifecycle.
#
# Protocol docs: docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import json
import logging
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from omega.cvar_table import ZONEID_PRESENCE, ZONEID_HANDOFF  # noqa: F401
from omega.oracle.subagent_dispatcher import (
    HandoffPacket,
    CAPABILITY_REGISTRY,
)

logger = logging.getLogger(__name__)

# ── Agent Presence ────────────────────────────────────────────────────────

PresenceStatus = Literal["active", "idle", "stale", "dead"]

# [id-soft: doom-1993] ZONEID Pattern — presence integrity constant
# Imported from cvar_table (single source of truth per D97)


@dataclass
class AgentPresence:
    """Tracks whether an agent is alive and available.

    [id-soft: doom-1993] ZONEID Pattern — integrity check on presence records.
    """
    agent_name: str
    last_heartbeat: float
    ttl_seconds: float = 300.0  # 5 min default
    status: PresenceStatus = "active"
    current_task: Optional[str] = None
    session_id: Optional[str] = None
    zoneid: int = ZONEID_PRESENCE

    def __post_init__(self) -> None:
        if self.zoneid != ZONEID_PRESENCE:
            raise ValueError(
                f"Invalid ZONEID_PRESENCE: expected {ZONEID_PRESENCE:#x}, "
                f"got {self.zoneid:#x}"
            )

    @property
    def expired(self) -> bool:
        return time.time() > (self.last_heartbeat + self.ttl_seconds)

    def refresh(self, session_id: Optional[str] = None) -> None:
        """Update heartbeat timestamp."""
        self.last_heartbeat = time.time()
        self.status = "active"
        if session_id:
            self.session_id = session_id

    def update_status(self) -> PresenceStatus:
        """Recompute status based on heartbeat age."""
        if self.expired:
            age = time.time() - self.last_heartbeat
            if age > self.ttl_seconds * 2:
                self.status = "dead"
            else:
                self.status = "stale"
        elif self.current_task:
            self.status = "idle"
        else:
            self.status = "active"
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Link P9 Runtime ──────────────────────────────────────────────────────


class LinkP9Runtime:
    """The runtime for agent handoff and delegation.

    Manages:
    - Agent presence tracking (TTL + heartbeat)
    - HandoffPacket lifecycle (pending → accepted → completed/failed)
    - Task queue for inter-agent messages
    - Archive management (completed packets → JSON)

    [id-soft: doom3-2004] idEntity event system — agents emit typed events,
    other agents consume them.
    """

    def __init__(self, archive_dir: str = "data/handoff/archive") -> None:
        self._presence: Dict[str, AgentPresence] = {}
        self._outbox: List[HandoffPacket] = []  # packets I'm sending
        self._inbox: List[HandoffPacket] = []   # packets addressed to me
        self._archive_dir = Path(archive_dir)
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        self._dispatch_log: List[Dict[str, Any]] = []

    # ── Presence Management ────────────────────────────────────────────

    def heartbeat(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
        ttl_seconds: float = 300.0,
    ) -> AgentPresence:
        """Register or refresh agent presence.

        Called by agents on startup and periodically during execution.
        If the agent doesn't heartbeat within ttl_seconds, it's marked stale.
        """
        if agent_name in self._presence:
            self._presence[agent_name].refresh(session_id)
            logger.debug("Heartbeat refreshed: %s", agent_name)
        else:
            self._presence[agent_name] = AgentPresence(
                agent_name=agent_name,
                last_heartbeat=time.time(),
                ttl_seconds=ttl_seconds,
                session_id=session_id,
            )
            logger.info("Agent registered: %s (session=%s)", agent_name, session_id)
        return self._presence[agent_name]

    def check_presence(self, agent_name: str) -> Optional[AgentPresence]:
        """Check if an agent is alive. Returns None if unknown."""
        presence = self._presence.get(agent_name)
        if presence:
            presence.update_status()
        return presence

    def list_active(self) -> List[AgentPresence]:
        """List all agents that are active or idle (not stale/dead)."""
        result = []
        for p in self._presence.values():
            p.update_status()
            if p.status in ("active", "idle"):
                result.append(p)
        return result

    def list_all(self) -> List[AgentPresence]:
        """List all known agents regardless of status."""
        for p in self._presence.values():
            p.update_status()
        return list(self._presence.values())

    def prune_dead(self) -> List[str]:
        """Remove agents marked as dead. Returns names of pruned agents."""
        pruned = []
        dead = [
            name for name, p in self._presence.items()
            if p.status == "dead"
        ]
        for name in dead:
            del self._presence[name]
            pruned.append(name)
            logger.info("Pruned dead agent: %s", name)
        return pruned

    # ── Packet Lifecycle ───────────────────────────────────────────────

    def send(self, packet: HandoffPacket) -> None:
        """Queue a handoff packet for dispatch.

        The packet enters the outbox. When the target agent calls receive(),
        it gets the packet from the inbox.
        """
        self._outbox.append(packet)
        self._dispatch_log.append({
            "action": "send",
            "packet_id": packet.packet_id,
            "source": packet.source_agent,
            "target": packet.target_agent,
            "task_type": packet.task_type,
            "timestamp": time.time(),
        })
        logger.info(
            "Packet queued: %s → %s [%s]",
            packet.source_agent,
            packet.target_agent,
            packet.task_type,
        )

    def receive(self, agent_name: str) -> List[HandoffPacket]:
        """Get pending packets addressed to a specific agent.

        Returns packets where target_agent matches and status is 'pending'.
        Sets status to 'accepted' on retrieval.
        """
        pending = [
            p for p in self._outbox
            if p.target_agent == agent_name and p.status == "pending"
        ]
        for p in pending:
            p.status = "accepted"
            self._inbox.append(p)
            self._dispatch_log.append({
                "action": "accept",
                "packet_id": p.packet_id,
                "target": agent_name,
                "timestamp": time.time(),
            })
            logger.info("Packet accepted: %s by %s", p.packet_id, agent_name)
        return pending

    def complete(self, packet_id: str, result: str) -> Optional[HandoffPacket]:
        """Mark a packet as completed and archive it.

        Returns the completed packet, or None if not found.
        """
        packet = self._find_packet(packet_id)
        if packet is None:
            logger.warning("Packet not found for completion: %s", packet_id)
            return None

        packet.status = "completed"
        packet.result = result
        self._archive(packet)
        self._dispatch_log.append({
            "action": "complete",
            "packet_id": packet_id,
            "timestamp": time.time(),
        })
        logger.info("Packet completed: %s", packet_id)
        return packet

    def fail(self, packet_id: str, error: str) -> Optional[HandoffPacket]:
        """Mark a packet as failed and archive it.

        Returns the failed packet, or None if not found.
        """
        packet = self._find_packet(packet_id)
        if packet is None:
            logger.warning("Packet not found for failure: %s", packet_id)
            return None

        packet.status = "failed"
        packet.error = error
        self._archive(packet)
        self._dispatch_log.append({
            "action": "fail",
            "packet_id": packet_id,
            "error": error,
            "timestamp": time.time(),
        })
        logger.warning("Packet failed: %s — %s", packet_id, error)
        return packet

    def timeout(self, packet_id: str) -> Optional[HandoffPacket]:
        """Mark a packet as timed out and archive it.

        Returns the timed-out packet, or None if not found.
        """
        packet = self._find_packet(packet_id)
        if packet is None:
            return None

        packet.status = "timed_out"
        packet.error = f"TTL expired ({packet.ttl_seconds}s)"
        self._archive(packet)
        self._dispatch_log.append({
            "action": "timeout",
            "packet_id": packet_id,
            "timestamp": time.time(),
        })
        logger.warning("Packet timed out: %s", packet_id)
        return packet

    def list_pending(self) -> List[HandoffPacket]:
        """List all packets still in the outbox with pending status."""
        return [p for p in self._outbox if p.status == "pending"]

    def list_in_progress(self) -> List[HandoffPacket]:
        """List all packets that have been accepted but not completed."""
        return [p for p in self._outbox if p.status == "accepted"]

    def check_timeouts(self) -> List[HandoffPacket]:
        """Check for timed-out packets and mark them."""
        timed_out = []
        for p in self._outbox:
            if p.status in ("pending", "accepted") and p.expired:
                result = self.timeout(p.packet_id)
                if result:
                    timed_out.append(result)
        return timed_out

    # ── Archive ────────────────────────────────────────────────────────

    def archive_stats(self) -> Dict[str, int]:
        """Get archive statistics by status."""
        stats: Dict[str, int] = {}
        for p in self._outbox:
            stats[p.status] = stats.get(p.status, 0) + 1
        return stats

    def get_dispatch_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent dispatch log entries."""
        return self._dispatch_log[-limit:]

    # ── Internal ───────────────────────────────────────────────────────

    def _find_packet(self, packet_id: str) -> Optional[HandoffPacket]:
        """Find a packet by ID in outbox or inbox."""
        for p in self._outbox:
            if p.packet_id == packet_id:
                return p
        for p in self._inbox:
            if p.packet_id == packet_id:
                return p
        return None

    def _archive(self, packet: HandoffPacket) -> None:
        """Save completed/failed packet to archive directory."""
        try:
            path = self._archive_dir / f"{packet.packet_id}.json"
            path.write_text(packet.to_json())
            logger.info("Packet archived: %s", path)
        except OmegaError:
            logger.error("Failed to archive packet %s (OmegaError)", packet.packet_id)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Failed to archive packet %s: %s", packet.packet_id, e, exc_info=True)

    def save_state(self, state_dir: str = "data/coordination") -> Path:
        """Save runtime state to disk for crash recovery.

        Stores presence + outbox + inbox + dispatch log.
        """
        state_path = Path(state_dir) / "link_p9_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "presence": {
                name: p.to_dict() for name, p in self._presence.items()
            },
            "outbox": [p.to_dict() for p in self._outbox],
            "inbox": [p.to_dict() for p in self._inbox],
            "dispatch_log": self._dispatch_log[-100:],  # last 100 entries
            "saved_at": datetime.now().isoformat(),
        }
        state_path.write_text(json.dumps(state, indent=2, default=str))
        logger.info("Link P9 state saved: %s", state_path)
        return state_path

    def load_state(self, state_dir: str = "data/coordination") -> bool:
        """Load runtime state from disk. Returns True if state was loaded."""
        state_path = Path(state_dir) / "link_p9_state.json"
        if not state_path.exists():
            return False

        try:
            state = json.loads(state_path.read_text())

            # Restore presence
            for name, p_data in state.get("presence", {}).items():
                self._presence[name] = AgentPresence(**p_data)

            # Restore outbox
            for p_data in state.get("outbox", []):
                self._outbox.append(HandoffPacket(**p_data))

            # Restore inbox
            for p_data in state.get("inbox", []):
                self._inbox.append(HandoffPacket(**p_data))

            # Restore dispatch log
            self._dispatch_log = state.get("dispatch_log", [])

            logger.info("Link P9 state loaded from %s", state_path)
            return True
        except OmegaError:
            return False
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Failed to load Link P9 state: %s", e, exc_info=True)
            return False
