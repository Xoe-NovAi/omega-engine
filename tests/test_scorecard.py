# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Contract Tests for Ω-Research Scorecard (M21 Gate Integrity)
⬡ OMEGA ⬡ VERITY ⬡ TEST
"""

import pytest
from uuid import uuid4
from datetime import datetime

from src.omega.research.schema import (
    CLEARScore,
    ResearchProposal,
    ProposalStatus,
)
from src.omega.research.hivemind_bridge import AgentSignal
from src.omega.research import (
    AMFOEvaluation,
    AMFOEvaluator,
    CalibratedJudge,
    AMFO_TIERS,
    assert_clear_score_type,
    assert_amfo_evaluator_type,
    assert_research_proposal_type,
)


class TestCLEARScore:
    """Contract tests for CLEARScore dataclass."""
    
    def test_clear_score_creation(self):
        score = CLEARScore(
            cost_efficiency=0.5,
            local_first_ratio=0.8,
            epistemic_rigor=0.7,
            adversarial_robustness=0.6,
            reproducibility=0.75,
        )
        assert_clear_score_type(score)
        assert score.cost_efficiency == 0.5
        assert score.local_first_ratio == 0.8
        assert score.epistemic_rigor == 0.7
        assert score.adversarial_robustness == 0.6
        assert score.reproducibility == 0.75
    
    def test_clear_score_to_vector(self):
        score = CLEARScore(0.5, 0.8, 0.7, 0.6, 0.75)
        vec = score.to_vector()
        assert len(vec) == 5
        assert vec[0] == -0.5  # cost inverted
        assert vec[1] == 0.8
        assert vec[2] == 0.7
        assert vec[3] == 0.6
        assert vec[4] == 0.75
    
    def test_clear_score_dominates(self):
        # A dominates B: A >= B on all, A > B on at least one
        a = CLEARScore(0.3, 0.9, 0.8, 0.7, 0.8)  # lower cost, higher others
        b = CLEARScore(0.5, 0.7, 0.6, 0.5, 0.6)
        assert a.dominates(b) is True
        assert b.dominates(a) is False
    
    def test_clear_score_no_dominance_when_equal(self):
        a = CLEARScore(0.5, 0.8, 0.7, 0.6, 0.75)
        b = CLEARScore(0.5, 0.8, 0.7, 0.6, 0.75)
        assert a.dominates(b) is False
        assert b.dominates(a) is False
    
    def test_clear_score_no_dominance_when_mixed(self):
        a = CLEARScore(0.3, 0.9, 0.8, 0.7, 0.8)
        b = CLEARScore(0.5, 0.7, 0.9, 0.5, 0.6)  # b better on epistemic
        assert a.dominates(b) is False
        assert b.dominates(a) is False


class TestResearchProposal:
    """Contract tests for ResearchProposal lifecycle."""
    
    def test_proposal_creation(self):
        proposal = ResearchProposal(
            causal_trace_id="trace_123",
            domain="P6",
            hypothesis="Local inference can match cloud quality",
            experiment_spec={"model": "qwen3-4b", "budget": 100},
            budget_usd=50.0,
            assigned_agents=["roc_racoon", "jem"],
        )
        assert_research_proposal_type(proposal)
        assert proposal.causal_trace_id == "trace_123"
        assert proposal.domain == "P6"
        assert proposal.status == ProposalStatus.DRAFT
        assert proposal.is_terminal() is False
    
    def test_proposal_status_transitions(self):
        proposal = ResearchProposal(
            causal_trace_id="trace_123",
            domain="P6",
            hypothesis="Test",
            experiment_spec={},
        )
        
        # Valid transitions
        proposal.advance_status(ProposalStatus.SCOUTING)
        assert proposal.status == ProposalStatus.SCOUTING
        
        proposal.advance_status(ProposalStatus.VALIDATING)
        assert proposal.status == ProposalStatus.VALIDATING
        
        proposal.advance_status(ProposalStatus.SYNTHESIZING)
        assert proposal.status == ProposalStatus.SYNTHESIZING
        
        proposal.advance_status(ProposalStatus.CONSENSUS)
        assert proposal.status == ProposalStatus.CONSENSUS
        
        proposal.advance_status(ProposalStatus.ARCHIVED)
        assert proposal.status == ProposalStatus.ARCHIVED
        assert proposal.is_terminal() is True
    
    def test_proposal_invalid_transition_raises(self):
        proposal = ResearchProposal(
            causal_trace_id="trace_123",
            domain="P6",
            hypothesis="Test",
            experiment_spec={},
        )
        proposal.advance_status(ProposalStatus.SCOUTING)
        
        # Cannot go from SCOUTING to ARCHIVED directly
        with pytest.raises(ValueError):
            proposal.advance_status(ProposalStatus.ARCHIVED)
    
    def test_proposal_rejection_terminal(self):
        proposal = ResearchProposal(
            causal_trace_id="trace_123",
            domain="P6",
            hypothesis="Test",
            experiment_spec={},
        )
        proposal.advance_status(ProposalStatus.REJECTED)
        assert proposal.is_terminal() is True
        assert proposal.completed_at is not None
    
    def test_proposal_to_dict_roundtrip(self):
        proposal = ResearchProposal(
            causal_trace_id="trace_123",
            domain="P7",
            hypothesis="Memory distillation works",
            experiment_spec={"method": "L1->L2->L3"},
            budget_usd=25.0,
            assigned_agents=["lucifer"],
        )
        proposal.advance_status(ProposalStatus.SCOUTING)
        
        data = proposal.to_dict()
        assert data["causal_trace_id"] == "trace_123"
        assert data["domain"] == "P7"
        assert data["status"] == "SCOUTING"
        assert data["budget_usd"] == 25.0
        
        # Round-trip
        restored = ResearchProposal.from_dict(data)
        assert restored.causal_trace_id == "trace_123"
        assert restored.domain == "P7"
        assert restored.status == ProposalStatus.SCOUTING


class TestAMFOTiers:
    """Contract tests for AMFO tier configuration."""
    
    def test_amfo_tiers_structure(self):
        assert len(AMFO_TIERS) == 3
        assert AMFO_TIERS[0]["name"] == "scout"
        assert AMFO_TIERS[1]["name"] == "validate"
        assert AMFO_TIERS[2]["name"] == "synthesize"
        
        for tier in AMFO_TIERS:
            assert "budget_sec" in tier
            assert "fidelity" in tier
            assert "model" in tier
            assert tier["budget_sec"] > 0
    
    def test_amfo_tiers_increasing_budget(self):
        budgets = [t["budget_sec"] for t in AMFO_TIERS]
        assert budgets == sorted(budgets)  # Strictly increasing


class TestCalibratedJudge:
    """Contract tests for CalibratedJudge."""
    
    def test_judge_creation(self):
        judge = CalibratedJudge()
        assert judge.model == "qwen3-4b-thinking-q4_k_m"
        assert judge._calibrated is False
    
    def test_judge_uncalibrated_passthrough(self):
        judge = CalibratedJudge()
        assert judge.judge(0.7) == 0.7
        assert judge.judge(0.3) == 0.3
    
    def test_judge_calibration(self):
        judge = CalibratedJudge()
        # Mock calibration data: (raw_score, oracle_score)
        oracle_labels = [(0.1, 0.2), (0.3, 0.4), (0.5, 0.6), (0.7, 0.8), (0.9, 0.95)]
        judge.calibrate(oracle_labels)
        # After calibration, should apply isotonic regression
        # (exact values depend on sklearn, but should be monotonic)


class TestAMFOEvaluator:
    """Contract tests for AMFOEvaluator."""
    
    @pytest.fixture
    def mock_oracle(self):
        """Mock oracle that returns structured responses."""
        class MockResponse:
            def __init__(self, text, provider="mock", tokens=100):
                self.text = text
                self.provider_name = provider
                self.tokens_used = tokens
        
        async def summon(model: str, prompt: str):
            if "SCOUT" in prompt:
                return MockResponse('{"feasible":true,"estimated_cost_usd":0.3,"local_first_estimate":0.8}')
            elif "VALIDATE" in prompt:
                return MockResponse('{"epistemic_rigor":0.7}')
            else:
                return MockResponse('{"cost_efficiency":0.7,"local_first_ratio":0.8,"epistemic_rigor":0.7,"adversarial_robustness":0.6,"reproducibility":0.7}')
        
        return summon
    
    @pytest.mark.anyio
    async def test_amfo_evaluator_creation(self, mock_oracle):
        evaluator = AMFOEvaluator(oracle_summon=mock_oracle)
        assert_amfo_evaluator_type(evaluator)
        assert len(evaluator.tiers) == 3
    
    @pytest.mark.anyio
    async def test_amfo_evaluation_runs(self, mock_oracle):
        evaluator = AMFOEvaluator(oracle_summon=mock_oracle)
        proposal = ResearchProposal(
            causal_trace_id="trace_test",
            domain="P6",
            hypothesis="Test hypothesis",
            experiment_spec={"test": True},
        )
        
        result = await evaluator.evaluate(proposal)
        
        assert isinstance(result, AMFOEvaluation)
        assert len(result.tier_results) >= 1
        assert result.proposal_id == str(proposal.id)
        assert result.total_time_sec >= 0


class TestAgentSignal:
    """Contract tests for AgentSignal (cross-pollination)."""
    
    def test_signal_creation(self):
        signal = AgentSignal(
            agent_id="roc_racoon",
            proposal_id=uuid4(),
            causal_trace_id="trace_123",
            signal_type="validation",
            content="Source verified",
            confidence=0.9,
            domain_expertise=0.8,
        )
        assert signal.agent_id == "roc_racoon"
        assert signal.signal_type == "validation"
        assert signal.confidence == 0.9
        assert signal.domain_expertise == 0.8
    
    def test_signal_to_dict_roundtrip(self):
        proposal_id = uuid4()
        signal = AgentSignal(
            agent_id="jem",
            proposal_id=proposal_id,
            causal_trace_id="trace_456",
            signal_type="critique",
            content="Methodology gap",
            confidence=0.7,
            domain_expertise=0.9,
        )
        data = signal.to_dict()
        restored = AgentSignal.from_dict(data)
        assert restored.agent_id == "jem"
        assert restored.proposal_id == proposal_id
        assert restored.causal_trace_id == "trace_456"
