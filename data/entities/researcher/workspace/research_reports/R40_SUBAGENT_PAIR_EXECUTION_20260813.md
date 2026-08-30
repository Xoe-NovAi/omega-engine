<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# R40 — Subagent Pair-Execution Chains

**AP Token**: `AP-R40-PAIR-EXEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r14 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R40 (Infrastructure): Subagent Pair-Execution Chains — ancestor/descendant tree walking for pair-execution chains (executor-opus + executor-gpt, etc.). Design chain-of-custody auditing.
**Status**: ✅ RESOLVED — PairExecutionChain utility designed. Tree-walking + chain-of-custody auditing specified. Integrates with existing HandoffPacket (parent_trace_id/trace_id).

---

## 📊 Executive Summary (L1)

R40 required designing pair-execution chain infrastructure for subagent dispatch. The Omega Engine already has `HandoffPacket` (subagent_dispatcher.py) with `parent_trace_id`/`trace_id` for chaining, `visited_agents`/`hop_count` for loop protection, and `CAPABILITY_REGISTRY` for agent discovery. R40 extends this with **PairExecutionChain** — a tree-walking utility that builds ancestor/descendant chains from HandoffPackets and provides chain-of-custody auditing. The pair-execution pattern (executor-opus + executor-gpt) is formalized as a dual-agent tandem where one agent executes and the other verifies, with full trace propagation.

## 🔬 Detailed Dialectic (L2)

### The Four Perspectives

**Architect (Systemic Logic)**:
- PairExecutionChain must build a tree from HandoffPackets using `parent_trace_id` → `trace_id` edges
- Tree-walking must support both directions: ancestors (up) and descendants (down)
- Must integrate with existing `CAPABILITY_REGISTRY` for agent resolution
- Must use AnyIO for async compatibility (M1 mandate)

**Adversary (Critical Rigor)**:
- Chain-of-custody must be tamper-evident: each hop records source, target, timestamp, context hash
- Loop detection must use `visited_agents` + `hop_count` (already in HandoffPacket)
- Pair-execution must not create infinite recursion: max_hops=10 (already enforced)
- Must handle missing parent_trace_id gracefully (root nodes)

**Alchemist (Creative Synthesis)**:
- Pair-execution enables "executor + verifier" tandem: one agent implements, the other audits
- This maps to the Cognitive Sovereign's "Navigator + Auditor" pattern (Pillar 1)
- Chain-of-custody auditing provides forensic traceability for compliance (M9 Error Integrity)

**Archivist (Historical Truth)**:
- The HandoffPacket design (AP-ORACLE-RESTORE-v2.3.0) already includes ZONEID pattern (vet-015) for integrity
- The opencode-sessions-explorer session-genealogy tool already walks parent/child trees (reference implementation)
- R40 formalizes this for agent dispatch chains (not just session trees)

### Current State Analysis

**Existing Infrastructure** (subagent_dispatcher.py):
```python
@dataclass
class HandoffPacket:
    source_agent: str
    target_agent: str
    task_type: TaskType
    task_description: str
    packet_id: str = ""
    parent_trace_id: str = ""      # ← Chain parent link
    trace_id: str = ""             # ← Unique chain ID
    zoneid: int = ZONEID_HANDOFF   # ← Integrity magic (vet-015)
    status: PacketStatus = "pending"
    visited_agents: List[str] = field(default_factory=list)  # ← Loop guard
    hop_count: int = 0             # ← Loop guard
    max_hops: int = 10             # ← Loop guard
```

**Gap**: No utility to:
1. Build a tree from multiple HandoffPackets
2. Walk ancestors/descendants of a given trace_id
3. Audit chain-of-custody (who dispatched whom, when, with what context)

### PairExecutionChain Design

```python
class PairExecutionChain:
    """
    Builds and walks subagent dispatch chains from HandoffPackets.
    
    Tree structure: parent_trace_id → trace_id edges.
    Supports ancestor/descendant walking + chain-of-custody auditing.
    """
    
    def __init__(self, packets: List[HandoffPacket]):
        self.packets = {p.trace_id: p for p in packets}
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
        chain = []
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
        result = []
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
        all_agents = []
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
```

### Pair-Execution Pattern

The pair-execution pattern (executor-opus + executor-gpt) is formalized as:

```python
def pair_execute(
    executor_type: str,      # e.g., "executor-opus"
    verifier_type: str,      # e.g., "executor-gpt"
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
    exec_packet.save()
    
    # Verifier runs after, linked to executor
    verify_packet = HandoffPacket(
        source_agent="orchestrator",
        target_agent=verifier_type,
        task_type="verify",
        task_description=f"Audit: {task}",
        context=context,
        parent_trace_id=exec_packet.trace_id,  # ← Chain link
    )
    verify_packet.save()
    
    return exec_packet, verify_packet
```

### Integration with opencode-sessions-explorer

The `session-genealogy` tool already walks parent/child session trees:
```
opencode-sessions-explorer-session-genealogy(
    session_id="ses_xxx",
    direction="both",  # ancestors | descendants | both
    max_depth=5,
)
```

R40's PairExecutionChain mirrors this for agent dispatch chains (not session trees). Both use the same tree-walking algorithm; R40 applies it to HandoffPacket graphs instead of session parent_id graphs.

### M1/M9/M23 Compliance

- **M1 AnyIO**: PairExecutionChain uses only dict operations (no asyncio)
- **M9 Error Integrity**: Chain-of-custody audit includes zoneid validation (vet-015) per hop
- **M23 Failure Integrity**: Orphan nodes (missing parent) are recorded, not crashed

### Sovereign Synthesis (L3)

**Universal Principle**: *Sovereign intelligence is not a single monolith but a network of specialized agents, each with a clear lineage. The health of the fleet depends not on individual agent capability but on the integrity of the dispatch chains that connect them — every handoff must be traceable, every loop guarded, every custody auditable.*

**Pair-Execution Insight**: The executor+verifier tandem pattern (executor-opus + executor-gpt) embodies the Cognitive Sovereign's "Navigator + Auditor" duality (Pillar 1). By formalizing pair-execution as a traceable chain, the Omega Engine gains forensic accountability: every implementation can be traced to its verifier, every verifier to its implementation. This is not overhead — it is the structural foundation of sovereign trust.

## 📋 Implementation Notes

### PairExecutionChain Usage

```python
from omega.oracle.subagent_dispatcher import HandoffPacket
from r14_pair_execution import PairExecutionChain

# Load packets from data/handoff/archive/
packets = [HandoffPacket.load_async(p) for p in packet_paths]
chain = PairExecutionChain(packets)

# Walk ancestors of a trace_id
ancestors = chain.walk_ancestors("hdp_20260813_kali_roc_abc123")

# Audit chain-of-custody
audit = chain.audit_chain("hdp_20260813_kali_roc_abc123")
print(f"Depth: {audit['depth']}, Breadth: {audit['breadth']}, Loop risk: {audit['loop_risk']}")
```

### Pair-Execution Launch

```python
from omega.oracle.subagent_dispatcher import pair_execute

exec_packet, verify_packet = pair_execute(
    executor_type="executor-opus",
    verifier_type="executor-gpt",
    task="Implement circuit breaker in model_gateway.py",
    context="R30 benchmark recommends interlock 2.6.0",
)
# Then launch both via Task tool with subagent_type from CAPABILITY_REGISTRY
```

## 📊 Research Artifacts

- **Design**: `data/entities/researcher/workspace/research_reports/r40_pair_execution_chain.py` (PairExecutionChain design)
- **Integration**: `src/omega/oracle/subagent_dispatcher.py` (existing HandoffPacket)
- **Reference**: `opencode-sessions-explorer-session-genealogy` (session tree-walking)
- **Environment**: Python 3.13.7, venv

## 🔗 Related Documents

- `src/omega/oracle/subagent_dispatcher.py` — HandoffPacket, CAPABILITY_REGISTRY, dispatch()
- `src/omega/governance/dispatch_registry.py` — WAD-backed dispatch config
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — Dispatch protocol spec
- `SOVEREIGN_MANDATES.md` — M1 (AnyIO), M9 (Error Integrity), M23 (Failure Integrity)
- `CREDITS.md` — vet-015 ZONEID Pattern heritage

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r14 ⬡ 20260813*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3.5-lightning | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
