#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
PairExecutionChain — Tree-walking utility for subagent dispatch chains.

Part of R40 (Subagent Pair-Execution Chains). Design per AGENTS.md §8.8.

M1 AnyIO: No asyncio — pure dict operations.
M9 Error Integrity: Chain-of-custody audit includes zoneid validation.
M23 Failure Integrity: Orphan nodes recorded, not crashed.

Usage:
    from r14_pair_execution_chain import PairExecutionChain
    chain = PairExecutionChain(packets)
    ancestors = chain.walk_ancestors(trace_id)
    audit = chain.audit_chain(trace_id)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# [id-soft: vet-015] ZONEID Pattern — magic constant for handoff packet integrity
# Imported from cvar_table (single source of truth per D97)
try:
    from omega.cvar_table import ZONEID_HANDOFF
except ImportError:
    ZONEID_HANDOFF = 0x5A0E1D  # Fallback if cvar_table unavailable


@dataclass
class HandoffPacket:
    """Minimal HandoffPacket for chain-walking (mirrors subagent_dispatcher.HandoffPacket)."""
    source_agent: str
    target_agent: str
    task_type: str
    task_description: str
    packet_id: str = ""
    parent_trace_id: str = ""
    trace_id: str = ""
    zoneid: int = ZONEID_HANDOFF
    status: str = "pending"
    visited_agents: List[str] = field(default_factory=list)
    hop_count: int = 0
    max_hops: int = 10
    created_at: float = 0.0

    def __post_init__(self) -> None:
        if not self.packet_id:
            now = datetime.now()
            short = uuid.uuid4().hex[:8]
            self.packet_id = f"hdp_{now.strftime('%Y%m%d')}_{self.source_agent}_{self.target_agent}_{short}"
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex
        if not self.created_at:
            self.created_at = datetime.now().timestamp()
        if self.zoneid != ZONEID_HANDOFF:
            raise ValueError(f"Invalid ZONEID_HANDOFF: expected {ZONEID_HANDOFF:#x}, got {self.zoneid:#x}")


class PairExecutionChain:
    """
    Builds and walks subagent dispatch chains from HandoffPackets.

    Tree structure: parent_trace_id → trace_id edges.
    Supports ancestor/descendant walking + chain-of-custody auditing.
    """

    def __init__(self, packets: List[HandoffPacket]):
        self.packets: Dict[str, HandoffPacket] = {p.trace_id: p for p in packets}
        self.children: Dict[str, List[str]] = {}
        self.parents: Dict[str, str] = {}

        # Build adjacency
        for p in packets:
            if p.parent_trace_id and p.parent_trace_id in self.packets:
                self.parents[p.trace_id] = p.parent_trace_id
                self.children.setdefault(p.parent_trace_id, []).append(p.trace_id)
            elif p.parent_trace_id:
                # Orphan: parent not in set (cross-session chain)
                self.parents[p.trace_id] = p.parent_trace_id

    def walk_ancestors(self, trace_id: str) -> List[HandoffPacket]:
        """Walk up the chain: trace_id → parent → parent → ... → root."""
        chain: List[HandoffPacket] = []
        current = trace_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            packet = self.packets.get(current)
            if packet:
                chain.append(packet)
                current = self.parents.get(current, "")
            else:
                # Orphan node — record and stop
                chain.append(HandoffPacket(
                    source_agent="UNKNOWN",
                    target_agent="UNKNOWN",
                    task_type="unknown",
                    task_description=f"Orphan: parent {current} not in chain",
                    trace_id=current,
                ))
                break
        return chain

    def walk_descendants(self, trace_id: str) -> List[HandoffPacket]:
        """Walk down the chain: trace_id → children → grandchildren → ..."""
        result: List[HandoffPacket] = []
        stack = [trace_id]
        visited = set()
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            packet = self.packets.get(current)
            if packet:
                result.append(packet)
                stack.extend(self.children.get(current, []))
        return result

    def audit_chain(self, trace_id: str) -> Dict[str, Any]:
        """Chain-of-custody audit: full ancestry + descendants + loop check."""
        ancestors = self.walk_ancestors(trace_id)
        descendants = self.walk_descendants(trace_id)

        # Loop detection
        loop_risk = False
        all_agents: List[str] = []
        for p in ancestors + descendants:
            all_agents.extend(p.visited_agents)
        if len(all_agents) != len(set(all_agents)):
            loop_risk = True

        return {
            "trace_id": trace_id,
            "depth": len(ancestors) - 1,
            "breadth": len(descendants) - 1,
            "ancestors": [p.packet_id for p in ancestors],
            "descendants": [p.packet_id for p in descendants],
            "loop_risk": loop_risk,
            "total_hops": sum(p.hop_count for p in ancestors + descendants),
            "custody": [
                {
                    "packet_id": p.packet_id,
                    "source": p.source_agent,
                    "target": p.target_agent,
                    "task_type": p.task_type,
                    "created_at": p.created_at,
                    "status": p.status,
                    "zoneid_valid": p.zoneid == ZONEID_HANDOFF,
                }
                for p in ancestors + descendants
            ],
        }


def pair_execute(
    executor_type: str,
    verifier_type: str,
    task: str,
    context: str = "",
) -> Tuple[HandoffPacket, HandoffPacket]:
    """
    Dual-agent tandem: executor implements, verifier audits.

    Returns (executor_packet, verifier_packet) with shared trace_id.
    """
    # Executor runs first
    exec_packet = HandoffPacket(
        source_agent="orchestrator",
        target_agent=executor_type,
        task_type="implement",
        task_description=task,
        context=context,
        parent_trace_id="",  # Root of pair
    )

    # Verifier runs after, linked to executor
    verify_packet = HandoffPacket(
        source_agent="orchestrator",
        target_agent=verifier_type,
        task_type="verify",
        task_description=f"Audit: {task}",
        context=context,
        parent_trace_id=exec_packet.trace_id,  # ← Chain link
    )

    return exec_packet, verify_packet


if __name__ == "__main__":
    # Demo: build a chain and audit it
    root = HandoffPacket(source_agent="kali", target_agent="maat", task_type="design", task_description="Phase C")
    child1 = HandoffPacket(source_agent="maat", target_agent="node_P3", task_type="implement", task_description="Fix CI", parent_trace_id=root.trace_id)
    child2 = HandoffPacket(source_agent="maat", target_agent="node_P5", task_type="verify", task_description="Audit CI", parent_trace_id=root.trace_id)
    grandchild = HandoffPacket(source_agent="node_P3", target_agent="verity", task_type="verify", task_description="Final audit", parent_trace_id=child1.trace_id)

    chain = PairExecutionChain([root, child1, child2, grandchild])
    audit = chain.audit_chain(grandchild.trace_id)
    print(f"Depth: {audit['depth']}, Breadth: {audit['breadth']}, Loop risk: {audit['loop_risk']}")
    print(f"Ancestors: {audit['ancestors']}")
    print(f"Descendants: {audit['descendants']}")
