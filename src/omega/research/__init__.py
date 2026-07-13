"""
Ω-Research Module — CLEAR-Pareto Sovereignty Scorecard + AMFO Evaluator + Hivemind Bridge
⬡ OMEGA ⬡ LILITH ⬡ P6-P10 ⬡ RESEARCH

Public API:
- CLEARScore: 5-dimension sovereignty scorecard
- ResearchProposal: Full lifecycle research unit
- ProposalStatus: DRAFT → SCOUTING → VALIDATING → SYNTHESIZING → CONSENSUS → ARCHIVED
- AMFOEvaluator: Tiered fidelity evaluation (scout → validate → synthesize)
- CalibratedJudge: Isotonic regression calibrated LLM judge
- ResearchHivemindBridge: DyTopo cross-pollination bridge
- DyTopoNode: Dynamic topology node for agent routing
"""

from .schema import (
    CLEARScore,
    ResearchProposal,
    ProposalStatus,
    AgentSignal,
    ConsensusResult,
    AMFO_TIERS,
    CalibratedJudge,
    AMFOEvaluator,
    AMFOResult,
    AMFOEvaluation,
    oracle_summon,
    assert_clear_score_type,
    assert_amfo_evaluator_type,
    assert_research_proposal_type,
    assert_agent_signal_type,
)

from .hivemind_bridge import (
    ResearchHivemindBridge,
    DyTopoNode,
    DYTOPO_CONFIG,
    create_research_bridge,
    assert_research_bridge_type,
    assert_dytopo_node_type,
)

__all__ = [
    # Schema
    "CLEARScore",
    "ResearchProposal",
    "ProposalStatus",
    "AgentSignal",
    "ConsensusResult",
    "AMFO_TIERS",
    # Scorecard
    "CalibratedJudge",
    "AMFOEvaluator",
    "AMFOResult",
    "AMFOEvaluation",
    "oracle_summon",
    "assert_clear_score_type",
    "assert_amfo_evaluator_type",
    "assert_research_proposal_type",
    "assert_agent_signal_type",
    # Hivemind Bridge
    "ResearchHivemindBridge",
    "DyTopoNode",
    "DYTOPO_CONFIG",
    "create_research_bridge",
    "assert_research_bridge_type",
    "assert_dytopo_node_type",
]

__version__ = "1.0.0"
