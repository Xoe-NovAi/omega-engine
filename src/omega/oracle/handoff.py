# AP: AP-ORACLE-RESTORE-v2.3.0
"""Omega Engine Handoff Protocol.
AP: AP-HANDOFF-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: HANDOFF]

Defines the formal structure for transferring session context, goals, and state 
between agents to eliminate "Agent Amnesia".

[id-soft: vet-008] Grace Period — state preservation during transition
  Similar to Quake's delayed entity removal, the HandoffState ensures that 
  the target agent has a complete snapshot of the previous agent's 
  consciousness before the source agent is decommissioned.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import json

# Aligned with subagent_dispatcher.py PacketStatus
HandoffStatus = Literal["pending", "active", "completed", "stale", "archived"]


@dataclass
class HandoffState:
    """
    A formal context bridge between agent sessions.
    
    L1 (Narrative): What was the source agent doing?
    L2 (Insight): What has been discovered so far?
    L3 (Universal Principle): What is the overarching goal?
    
    Status lifecycle: pending → active → completed / stale
    Aligned with subagent_dispatcher.HandoffPacket (D-270 Decree 2).
    """
    session_id: str
    source_entity: str
    target_entity: str
    current_goal: str
    context_summary: str
    pending_tasks: List[str] = field(default_factory=list)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    trace_id: Optional[str] = None
    status: HandoffStatus = "pending"
    
    # Loop Guard Fields (T2-5)
    visited_agents: List[str] = field(default_factory=list)
    hop_count: int = 0
    max_hops: int = 10

    def is_loop(self, target: str) -> bool:
        """Check if delegating to target would create a loop."""
        return target.lower() in [a.lower() for a in self.visited_agents]

    def increment_hop(self) -> bool:
        """Increment hop count and check against max_hops. Returns True if budget remains."""
        self.hop_count += 1
        return self.hop_count <= self.max_hops

    def to_json(self) -> str:
        """Serialize handoff state for prompt injection."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandoffState':
        """Reconstruct handoff state from a dictionary."""
        return cls(**data)

def format_handoff_prompt(state: HandoffState) -> str:
    """
    Converts a HandoffState into a structured prompt for the target agent.
    """
    return (
        f"--- 🔱 HANDOFF RECEIVED 🔱 ---\n"
        f"FROM: {state.source_entity}\n"
        f"SESSION: {state.session_id}\n"
        f"CURRENT GOAL: {state.current_goal}\n"
        f"CONTEXT SUMMARY: {state.context_summary}\n"
        f"PENDING TASKS:\n" + "\n".join([f"- {t}" for t in state.pending_tasks]) + "\n"
        f"STATE SNAPSHOT: {json.dumps(state.state_snapshot)}\n"
        f"--- END HANDOFF ---\n\n"
        f"You have been summoned to take over this task. Please review the context above "
        f"and continue execution from the pending tasks."
    )
