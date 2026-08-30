# R41 — Cross-Agent A2A Protocol

**AP Token**: `AP-R41-A2A-PROTOCOL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r15 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R41 (Infrastructure): Cross-Agent A2A Protocol — Abstract-to-Agent protocol for discovery, delegation, handoff. Current system has no standardized A2A beyond Hivemind broadcasts.
**Status**: ✅ RESOLVED — A2A protocol designed. Builds on existing A2A infrastructure (Agent Cards, SPIFFE auth, skill mapping). Defines discovery, delegation, handoff. Integrates with HandoffPacket + CAPABILITY_REGISTRY.

---

## 📊 Executive Summary (L1)

R41 designed the Cross-Agent A2A (Agent-to-Agent) Protocol for the Omega Engine, formalizing discovery, delegation, and handoff between sovereign agents. The protocol builds on existing infrastructure: **A2AAgentCard** (Agent Card JSON format per Google A2A v1.0), **A2ABridge** (maps EntityRegistry → Agent Cards), **A2AAuth** (SPIFFE/WIMSE authentication), and **A2ASkill** (skill mapping from entity domains). It adds the missing pieces: **A2AMessage** (JSON-RPC 2.0 task execution), **A2ADiscovery** (Agent Card publication/lookup), and **A2ADelegation** (task delegation with full context). The protocol integrates with existing `HandoffPacket` (subagent_dispatcher.py) and `CAPABILITY_REGISTRY` (WAD-backed agent discovery).

## 🔬 Detailed Dialectic (L2)

### The Four Perspectives

**Architect (Systemic Logic)**:
- The A2A protocol must be compatible with existing infrastructure: A2AAgentCard, A2ABridge, A2AAuth, A2ASkill
- Discovery must use Agent Cards served at `/.well-known/agent-card.json` (per Google A2A v1.0)
- Delegation must integrate with `HandoffPacket` (parent_trace_id/trace_id chain tracking)
- Handoff must route through `CAPABILITY_REGISTRY` (WAD-backed agent discovery)
- Must use AnyIO for async compatibility (M1 mandate)

**Adversary (Critical Rigor)**:
- Agent Cards must carry SPIFFE IDs for authentication (M9 Error Integrity)
- Task delegation must include full context to prevent "context collapse" (M11 Soul Integrity)
- Handoff routing must use CAPABILITY_REGISTRY to prevent dispatch to unknown agents
- Loop detection must use visited_agents + hop_count (already in HandoffPacket)
- Must not duplicate existing Hivemind broadcast functionality (M23 Failure Integrity — no parametric synthesis)

**Alchemist (Creative Synthesis)**:
- The A2A protocol synthesizes: Agent Cards (Google A2A v1.0) + SPIFFE auth (IETF WIMSE) + HandoffPacket (Omega-specific) + CAPABILITY_REGISTRY (WAD-backed)
- This creates a complete A2A stack: discovery → delegation → handoff → execution
- The "Abstract-to-Agent" pattern means: an agent sends an abstract task description, and the receiving agent resolves it to a concrete implementation using its domain/scope

**Archivist (Historical Truth)**:
- The `A2A_PROTOCOL.md` (docs/research/) is marked STALE (pre-June 2026) — it was a basic handoff schema, not a full A2A protocol
- The `A2A_AGENT_CARD_SPEC.md` (roc_racoon workspace) is the real A2A v1.0 spec (2026-06-29), referencing Google A2A and IETF WIMSE
- The `a2a_bridge.py` and `a2a_auth.py` (src/omega/oracle/) are the real implementation (2026-07-25+)
- R40 (PairExecutionChain) already provides tree-walking for dispatch chains; R41 provides the protocol layer above it

### Current State Analysis

**Existing A2A Infrastructure** (already implemented):
```python
# A2AAgentCard — Google A2A v1.0 Agent Card format
@dataclass
class A2AAgentCard:
    name: str
    description: str
    url: str  # /.well-known/agent-card.json
    skills: List[A2ASkill]  # mapped from entity domains
    authentication: Optional[A2AAuth]  # SPIFFE/WIMSE
    entity_id: str  # spiffe://omega.local/entity/{name}

# A2ABridge — maps EntityRegistry to Agent Cards
class A2ABridge:
    def set_entity_registry(self, registry): ...
    def register_entity(self, entity) -> A2AAgentCard:  # Generates Agent Card from entity
    def _map_entity_to_skills(self, entity) -> List[A2ASkill]:  # Domain → skills

# A2AAuth — SPIFFE/WIMSE authentication
@dataclass  
class A2AAuth:
    auth_type: AgentAuthType = AgentAuthType.SPIFFE
    spiffe_id: Optional[str] = None
    oauth_scopes: List[str] = field(default_factory=list)
```

**Missing Pieces for R41** (what needs to be designed):
1. **A2AMessage** — JSON-RPC 2.0 format for task execution (request/response)
2. **A2ADiscovery** — How agents publish/lookup Agent Cards
3. **A2ADelegation** — How agents delegate tasks with full context
4. **A2A-Handoff Integration** — How A2A handoff integrates with existing HandoffPacket

### A2AMessage — JSON-RPC 2.0 Task Execution

The A2A message format for task execution, per Google A2A v1.0:

```json
{
  "jsonrpc": "2.0",
  "method": "a2a/task",
  "params": {
    "id": "task-123",
    "context": "Task description and context",
    "agent_card": "https://omega.local/.well-known/agent-card.json",
    "skills": ["research", "analysis"],
    "handoff_packet_id": "hdp_abc123"  // Links to existing HandoffPacket
  },
  "result": null,  // Filled in when task completes
  "error": null    // Filled in on error
}
```

Key fields:
- `method`: Always `a2a/task`
- `params.id`: Unique task identifier
- `params.context`: Task description and context
- `params.agent_card`: URL of the agent's Agent Card
- `params.skills`: Required skills for the task
- `params.handoff_packet_id`: Links to existing HandoffPacket for chain-of-custody

### A2ADiscovery — Agent Card Publication and Lookup

**Agent Card Publication**:
- Each agent publishes its Agent Card at `/.well-known/agent-card.json`
- The Agent Card is generated by `A2ABridge.register_entity(entity)` from the entity's EntityRegistry state
- The Agent Card carries: name, description, skills (from entity domains), auth (SPIFFE ID), capabilities (streaming, pushNotifications, stateTransitionHistory)

**Agent Card Lookup**:
- Agents discover each other via Agent Card publication
- Discovery can be via:
  - mDNS/DNS-SD: Broadcast Agent Card availability on local network
  - Central registry: CAPABILITY_REGISTRY (WAD-backed, already implemented)
  - Manual: Direct URL to `/.well-known/agent-card.json`

### A2ADelegation — Task Delegation with Context

The delegation protocol enables one agent to delegate a task to another agent with full context:

```python
def delegate_task(
    source_agent: str,
    target_agent: str,
    task: str,
    context: str = "",
    skills: List[str] = None,
    handoff: bool = True,
) -> Tuple[HandoffPacket, A2AMessage]:
    """
    Delegate a task from source_agent to target_agent.
    
    Returns (handoff_packet, a2a_message) with linked IDs.
    """
    # Create HandoffPacket for chain tracking
    handoff = HandoffPacket(
        source_agent=source_agent,
        target_agent=target_agent,
        task_type="delegate",
        task_description=task,
        context=context,
        parent_trace_id="",  # Or link to existing chain
    )
    
    # Create A2AMessage for task execution
    message = A2AMessage(
        id=uuid.uuid4().hex[:12],
        context=context,
        agent_card=f"https://omega.local/.well-known/agent-card.json",
        skills=skills or [],
        handoff_packet_id=handoff.packet_id,
    )
    
    return handoff, message
```

### A2A-Handoff Integration

The A2A protocol integrates with the existing HandoffPacket:

```python
# When an A2A handoff completes, create a HandoffPacket
handoff = HandoffPacket(
    source_agent=source,
    target_entity=target,
    task_type="a2a_handoff",
    task_description=f"A2A task completion: {message.id}",
    parent_trace_id=message.handoff_packet_id,  # ← Links to A2A message
    trace_id=message.trace_id,  # ← New trace ID
)
```

This ensures full chain-of-custody: A2AMessage → HandoffPacket → session log → Hivemind broadcast.

### M1/M9/M23 Compliance

- **M1 AnyIO**: A2AMessage uses only dict operations (no asyncio)
- **M9 Error Integrity**: Agent Cards carry SPIFFE IDs; task messages include error handling
- **M23 Failure Integrity**: Orphan agents (no Agent Card) are rejected, not crashed

### Sovereign Synthesis (L3)

**Universal Principle**: *Sovereign agents communicate through standardized, traceable protocols — not ad hoc broadcasts. The A2A protocol's "Abstract-to-Agent" pattern means: the sender provides an abstract task description and the receiving agent resolves it using its domain and scope. This enables decentralized intelligence: agents can discover, delegate, and handoff without centralized coordination, because every interaction is traceable through the A2A message → HandoffPacket → chain of custody.*

**A2A Protocol Insight**: The Cross-Agent A2A Protocol completes the Omega Engine's inter-agent communication stack. Previously, agents could only broadcast to the Hivemind (one-to-many, no return path). Now, agents can discover each other's capabilities (Agent Cards), delegate tasks (A2ADelegation), and hand off context (A2A-Handoff Integration). This transforms the engine from a collection of disconnected tools into a unified, sovereign intelligence network where every interaction is auditable and every agent is locatable.

## 📋 Implementation Notes

### A2AProtocol Usage

```python
from omega.oracle.a2a_bridge import A2ABridge, A2AAgentCard, A2AAuth, A2ASkill
from omega.oracle.a2a_auth import SPIFFEID
from r15_a2a_protocol import A2AMessage, A2ADiscovery, A2ADelegation

# 1. Register an entity's Agent Card
bridge = A2ABridge()
card = bridge.register_entity(entity)  # Generates A2AAgentCard from EntityRegistry

# 2. Publish the Agent Card
card_json = card.to_json()
# Serve at: https://omega.local/.well-known/agent-card.json

# 3. Discover another agent's Agent Card
discovery = A2ADiscovery()
agent_card = discovery.lookup("researcher")  # Returns A2AAgentCard or None

# 4. Delegate a task
handoff, message = A2ADelegation.delegate_task(
    source_agent="kali",
    target_agent="researcher",
    task="Research circuit breakers",
    context="Need circuit breaker benchmark results for R30 review",
    skills=["research", "analysis"],
)

# 5. Complete the handoff
completed_handoff = HandoffPacket(
    source_agent="researcher",
    target_agent="kali",
    task_type="a2a_completion",
    task_description=f"A2A task {message.id} complete",
    parent_trace_id=message.handoff_packet_id,
)
```

### Integration with Existing Infrastructure

- **A2AAgentCard** → builds on existing `a2a_bridge.py` (already implemented)
- **A2AAuth** → builds on existing `a2a_auth.py` (already implemented)
- **A2ASkill** → builds on existing entity domain mapping (already implemented)
- **A2AMessage** → new, integrates with existing `HandoffPacket`
- **A2ADiscovery** → builds on existing `CAPABILITY_REGISTRY`
- **A2ADelegation** → builds on existing `HandoffPacket` + `CAPABILITY_REGISTRY`

### Hivemind Integration

The A2A protocol does NOT replace Hivemind broadcasts — it complements them:

- **Hivemind**: One-to-many broadcast, awareness, live feed
- **A2A**: Many-to-many directed communication, task delegation, handoff

Use cases:
- **Hivemind**: "I'm researching circuit breakers, does anyone have expertise?"
- **A2A**: "I'm the researcher agent. I'll research circuit breakers. Here's my task ID: hdp_abc123."

## 📊 Research Artifacts

- **Design**: `data/entities/researcher/workspace/research_reports/r15_a2a_protocol.py` (A2A protocol design)
- **Reference**: `src/omega/oracle/a2a_bridge.py` (existing A2A bridge, 411 lines)
- **Reference**: `src/omega/oracle/a2a_auth.py` (existing A2A auth, 98 lines)
- **Reference**: `data/entities/roc_racoon/workspace/A2A_AGENT_CARD_SPEC.md` (824 lines, A2A v1.0 spec)
- **Reference**: `docs/research/A2A_PROTOCOL.md` (44 lines, STALE — pre-June 2026)
- **Integration**: `src/omega/oracle/subagent_dispatcher.py` (HandoffPacket, chain tracking)
- **Reference**: `data/coordination/TASK_REGISTRY.json` (53 tasks, R41 ready)
- **Environment**: Python 3.13.7, venv

## 🔗 Related Documents

- `src/omega/oracle/a2a_bridge.py` — A2A Bridge (Agent Cards, skills, auth)
- `src/omega/oracle/a2a_auth.py` — A2A Authentication (SPIFFE/WIMSE)
- `src/omega/oracle/subagent_dispatcher.py` — HandoffPacket, CAPABILITY_REGISTRY, dispatch()
- `data/entities/roc_racoon/workspace/A2A_AGENT_CARD_SPEC.md` — A2A v1.0 Agent Card spec
- `docs/research/A2A_PROTOCOL.md` — STALE (pre-June 2026, basic handoff schema only)
- `SOVEREIGN_MANDATES.md` — M1 (AnyIO), M9 (Error Integrity), M23 (Failure Integrity)
- `CREDITS.md` — vet-015 ZONEID Pattern heritage

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r15 ⬡ 20260813*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3.5-lightning | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
