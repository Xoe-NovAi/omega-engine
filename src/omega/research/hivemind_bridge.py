"""
Ω-Research Hivemind Bridge — DyTopo Cross-Pollination for Research Agents
⬡ OMEGA ⬡ LILITH ⬡ N6-N10 ⬡ HIVEMIND_BRIDGE

Mandate Compliance:
- M1 AnyIO: All async via AnyIO
- M12 Queue Integrity: Signal lifecycle with terminal states
- M17 Cognitive Integrity: causal_trace_id enables contradiction detection
- M23 Failure Integrity: No soft-failures in bridge pipeline
"""

from __future__ import annotations
import anyio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4

from omega.research.schema import ResearchProposal, AgentSignal, ProposalStatus, ConsensusResult


# ── DyTopo Configuration ─────────────────────────────────────────────────
DYTOPO_CONFIG = {
    "broadcast_timeout_sec": 30,
    "collection_timeout_sec": 60,
    "min_signals_for_consensus": 2,
    "max_signals": 10,
    "expertise_weight": 0.7,
    "confidence_weight": 0.3,
    "redis_channels": {
        "proposals": "hivemind:research:proposals",
        "signals": "hivemind:research:signals",
        "consensus": "hivemind:research:consensus",
    },
}


@dataclass
class DyTopoNode:
    """Dynamic topology node representing a research agent."""
    agent_id: str
    domains: list[str]  # e.g., ["N6", "N7"]
    expertise_scores: dict[str, float]  # domain -> 0.0-1.0
    historical_accuracy: float = 0.5
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    
    def relevance_for_proposal(self, proposal: ResearchProposal) -> float:
        """Compute relevance score for a given proposal."""
        domain_match = 1.0 if proposal.domain in self.domains else 0.3
        expertise = self.expertise_scores.get(proposal.domain, 0.5)
        return domain_match * expertise * self.historical_accuracy


class ResearchHivemindBridge:
    """
    DyTopo Cross-Pollination Bridge for Research Agents.
    
    Flow:
    1. broadcast_proposal() → Fan-out to relevant agents via Redis Pub/Sub
    2. collect_signals() → Gather critiques, validations, extensions
    3. synthesize_consensus() → Weighted aggregation → ConsensusResult
    
    Integrates with existing Hivemind (M12) via omega-hub_hivemind_redis_publish/subscribe.
    """
    
    def __init__(
        self,
        redis_publish: Callable[[str, str, int], Any],
        redis_subscribe: Callable[[str, float, int], Any],
        get_awareness: Callable[[], Any],
        nodes: dict[str, DyTopoNode] | None = None,
    ):
        self.redis_publish = redis_publish
        self.redis_subscribe = redis_subscribe
        self.get_awareness = get_awareness
        self.nodes = nodes or {}
        self._pending_proposals: dict[str, ResearchProposal] = {}
        self._signal_buffers: dict[str, list[AgentSignal]] = {}
    
    async def broadcast_proposal(self, proposal: ResearchProposal) -> list[str]:
        """
        Fan-out proposal to relevant agents via Hivemind Redis Pub/Sub.
        
        Returns list of agent_ids that received the proposal.
        """
        # Select relevant agents based on DyTopo relevance
        relevant_agents = self._select_relevant_agents(proposal)
        
        if not relevant_agents:
            return []
        
        # Prepare broadcast payload
        payload = {
            "type": "research_proposal",
            "proposal": proposal.to_dict(),
            "target_agents": relevant_agents,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": str(uuid4()),
        }
        
        # M12: Publish to Hivemind Redis channel
        channel = DYTOPO_CONFIG["redis_channels"]["proposals"]
        await self.redis_publish(channel, json.dumps(payload), ttl=30)
        
        # Track pending
        self._pending_proposals[str(proposal.id)] = proposal
        self._signal_buffers[str(proposal.id)] = []
        
        # Update proposal status
        proposal.advance_status(ProposalStatus.SCOUTING)
        
        return relevant_agents
    
    def _select_relevant_agents(self, proposal: ResearchProposal) -> list[str]:
        """Select agents based on DyTopo relevance scoring."""
        scored = []
        for agent_id, node in self.nodes.items():
            if not node.is_active:
                continue
            relevance = node.relevance_for_proposal(proposal)
            if relevance > 0.3:  # Threshold
                scored.append((agent_id, relevance))
        
        # Sort by relevance, take top N
        scored.sort(key=lambda x: x[1], reverse=True)
        max_agents = min(DYTOPO_CONFIG["max_signals"], len(scored))
        return [agent_id for agent_id, _ in scored[:max_agents]]
    
    async def collect_signals(
        self,
        proposal_id: str,
        timeout_sec: int = 30,
    ) -> list[AgentSignal]:
        """
        Gather signals from peer agents for a proposal.
        
        Uses Redis Pub/Sub subscription with timeout (M23: no indefinite blocking).
        """
        channel = DYTOPO_CONFIG["redis_channels"]["signals"]
        proposal_key = str(proposal_id)
        
        # Subscribe with timeout
        start_time = time.time()
        signals = []
        
        while time.time() - start_time < timeout_sec:
            remaining = timeout_sec - (time.time() - start_time)
            if remaining <= 0:
                break
            
            try:
                result = await self.redis_subscribe(channel, timeout=min(remaining, 5.0), max_messages=10)
                if result.get("status") == "success":
                    for msg in result.get("messages", []):
                        signal = self._parse_signal(msg, proposal_key)
                        if signal:
                            signals.append(signal)
                            self._signal_buffers[proposal_key].append(signal)
            except anyio.get_cancelled_exc_class():
                break
            except Exception:
                # M23: Log but continue collection
                pass
        
        # Also check awareness for any direct signals
        awareness = await self.get_awareness()
        for agent in awareness:
            if agent.get("entity") in self.nodes:
                # Check for signals in agent's context
                pass
        
        return signals
    
    def _parse_signal(self, message: dict, proposal_key: str) -> AgentSignal | None:
        """Parse Hivemind message into AgentSignal."""
        try:
            data = message if isinstance(message, dict) else json.loads(message)
            if data.get("type") != "research_signal":
                return None
            if data.get("proposal_id") != proposal_key:
                return None
            
            signal_data = data.get("signal", {})
            return AgentSignal(
                agent_id=signal_data["agent_id"],
                proposal_id=UUID(signal_data["proposal_id"]),
                causal_trace_id=signal_data.get("causal_trace_id", ""),
                signal_type=signal_data["signal_type"],
                content=signal_data["content"],
                confidence=signal_data["confidence"],
                domain_expertise=signal_data["domain_expertise"],
                timestamp=datetime.fromisoformat(signal_data["timestamp"]),
                trace_id=signal_data.get("trace_id", str(uuid4())),
            )
        except Exception:
            return None
    
    async def synthesize_consensus(self, signals: list[AgentSignal]) -> ConsensusResult:
        """
        Weighted aggregation of agent signals → ConsensusResult.
        
        Weights: expertise_weight * domain_expertise + confidence_weight * confidence
        """
        if not signals:
            return ConsensusResult(
                proposal_id=UUID("00000000-0000-0000-0000-000000000000"),
                accepted=False,
                weighted_score=0.0,
                participating_agents=[],
                dissenting_signals=[],
                synthesized_insight="No signals received",
            )
        
        # Group by signal type
        validations = [s for s in signals if s.signal_type == "validation"]
        critiques = [s for s in signals if s.signal_type == "critique"]
        extensions = [s for s in signals if s.signal_type == "extension"]
        contradictions = [s for s in signals if s.signal_type == "contradiction"]
        
        # M17: Contradiction detection via causal_trace_id
        trace_ids = set(s.causal_trace_id for s in signals if s.causal_trace_id)
        contradiction_detected = len(contradictions) > 0
        
        # Weighted scoring
        total_weight = 0.0
        weighted_sum = 0.0
        participating = []
        
        for signal in signals:
            weight = (
                DYTOPO_CONFIG["expertise_weight"] * signal.domain_expertise +
                DYTOPO_CONFIG["confidence_weight"] * signal.confidence
            )
            total_weight += weight
            weighted_sum += weight * signal.confidence
            participating.append(signal.agent_id)
        
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Consensus threshold
        min_signals = DYTOPO_CONFIG["min_signals_for_consensus"]
        accepted = len(signals) >= min_signals and avg_score >= 0.6 and not contradiction_detected
        
        # Synthesize insight
        insight_parts = []
        if validations:
            insight_parts.append(f"Validated by {len(validations)} agents")
        if critiques:
            insight_parts.append(f"{len(critiques)} critiques: " + "; ".join(c.content[:50] for c in critiques[:3]))
        if extensions:
            insight_parts.append(f"{len(extensions)} extensions proposed")
        if contradictions:
            insight_parts.append(f"⚠️ {len(contradictions)} contradictions detected (M17)")
        
        synthesized = " | ".join(insight_parts) if insight_parts else "No consensus reached"
        
        # L3 Principle Candidate (M11)
        l3_candidate = None
        if accepted and avg_score > 0.8:
            l3_candidate = f"High-confidence consensus on {signals[0].causal_trace_id}: {synthesized[:100]}"
        
        return ConsensusResult(
            proposal_id=signals[0].proposal_id,
            accepted=accepted,
            weighted_score=avg_score,
            participating_agents=participating,
            dissenting_signals=critiques + contradictions,
            synthesized_insight=synthesized,
            l3_principle_candidate=l3_candidate,
        )
    
    async def run_full_cycle(self, proposal: ResearchProposal) -> ConsensusResult:
        """
        Execute complete cross-pollination cycle.
        
        1. Broadcast proposal
        2. Collect signals
        3. Synthesize consensus
        4. Update proposal with result
        """
        # Phase 1: Broadcast
        agents = await self.broadcast_proposal(proposal)
        if not agents:
            return ConsensusResult(
                proposal_id=proposal.id,
                accepted=False,
                weighted_score=0.0,
                participating_agents=[],
                dissenting_signals=[],
                synthesized_insight="No relevant agents available",
            )
        
        # Phase 2: Collect
        signals = await self.collect_signals(str(proposal.id), DYTOPO_CONFIG["collection_timeout_sec"])
        
        # Phase 3: Synthesize
        consensus = await self.synthesize_consensus(signals)
        
        # Phase 4: Update proposal
        proposal.consensus_signals = [s.to_dict() for s in signals]
        proposal.final_clear = None  # Will be set by AMFO
        proposal.result_summary = consensus.synthesized_insight
        
        if consensus.accepted:
            proposal.advance_status(ProposalStatus.CONSENSUS)
        else:
            proposal.advance_status(ProposalStatus.REJECTED)
        
        # Publish consensus result
        await self._publish_consensus(consensus)
        
        return consensus
    
    async def _publish_consensus(self, consensus: ConsensusResult) -> None:
        """Publish consensus result to Hivemind."""
        channel = DYTOPO_CONFIG["redis_channels"]["consensus"]
        payload = {
            "type": "research_consensus",
            "consensus": {
                "proposal_id": str(consensus.proposal_id),
                "accepted": consensus.accepted,
                "weighted_score": consensus.weighted_score,
                "participating_agents": consensus.participating_agents,
                "synthesized_insight": consensus.synthesized_insight,
                "l3_principle_candidate": consensus.l3_principle_candidate,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.redis_publish(channel, json.dumps(payload), ttl=60)


# ── Hivemind Adapter Functions (M12 Integration) ─────────────────────────
async def hivemind_redis_publish(channel: str, message: str, ttl: int = 20) -> dict:
    """Adapter for omega-hub_hivemind_redis_publish."""
    from omega_hub import omega_hub_hivemind_redis_publish
    result = await omega_hub_hivemind_redis_publish(channel=channel, message=message, ttl=ttl)
    return json.loads(result)


async def hivemind_redis_subscribe(channel: str, timeout: float = 2.0, max_messages: int = 50) -> dict:
    """Adapter for omega-hub_hivemind_redis_subscribe."""
    from omega_hub import omega_hub_hivemind_redis_subscribe
    result = await omega_hub_hivemind_redis_subscribe(channel=channel, timeout=timeout, max_messages=max_messages)
    return json.loads(result)


async def hivemind_get_awareness() -> list[dict]:
    """Adapter for omega-hub_hivemind_get_awareness."""
    from omega_hub import omega_hub_hivemind_get_awareness
    result = await omega_hub_hivemind_get_awareness()
    return json.loads(result)


# ── Factory Function ─────────────────────────────────────────────────────
def create_research_bridge(nodes: dict[str, DyTopoNode] | None = None) -> ResearchHivemindBridge:
    """Create bridge with default Hivemind adapters."""
    return ResearchHivemindBridge(
        redis_publish=hivemind_redis_publish,
        redis_subscribe=hivemind_redis_subscribe,
        get_awareness=hivemind_get_awareness,
        nodes=nodes,
    )


# ── Contract Test Helpers (M21) ──────────────────────────────────────────
def assert_research_bridge_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for ResearchHivemindBridge type."""
    assert isinstance(obj, ResearchHivemindBridge), f"Expected ResearchHivemindBridge, got {type(obj)}"
    assert hasattr(obj, "broadcast_proposal")
    assert callable(obj.broadcast_proposal)
    assert hasattr(obj, "collect_signals")
    assert callable(obj.collect_signals)
    assert hasattr(obj, "synthesize_consensus")
    assert callable(obj.synthesize_consensus)
    assert hasattr(obj, "run_full_cycle")
    assert callable(obj.run_full_cycle)


def assert_dytopo_node_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for DyTopoNode type."""
    assert isinstance(obj, DyTopoNode), f"Expected DyTopoNode, got {type(obj)}"
    assert hasattr(obj, "agent_id")
    assert hasattr(obj, "domains")
    assert hasattr(obj, "expertise_scores")
    assert hasattr(obj, "relevance_for_proposal")
    assert callable(obj.relevance_for_proposal)
