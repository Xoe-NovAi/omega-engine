"""
Contract tests for SoulDistiller — M21 Gate Integrity compliance.
Tests verify isinstance(result, ExpectedType) for all public API boundaries.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from omega.scribe import SoulDistiller, LessonProposal


class TestSoulDistillerContract:
    """Contract tests for SoulDistiller public API."""
    
    @pytest.fixture
    def temp_entities_dir(self):
        """Create a temporary entities directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        entities_dir = temp_dir / "data" / "entities"
        entities_dir.mkdir(parents=True)
        yield entities_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def distiller(self, temp_entities_dir):
        """Create a SoulDistiller instance with temp directory."""
        # Patch the entities_dir to use temp directory
        with patch.object(SoulDistiller, '__init__', lambda self, entity_name, session_id, model=None: 
                         setattr(self, 'entity_name', entity_name) or
                         setattr(self, 'session_id', session_id) or
                         setattr(self, 'model', model) or
                         setattr(self, 'entities_dir', temp_entities_dir.parent.parent) or
                         setattr(self, 'entity_dir', temp_entities_dir / entity_name) or
                         setattr(self, 'proposed_path', temp_entities_dir / entity_name / "proposed_lessons.yaml") or
                         self.entity_dir.mkdir(parents=True, exist_ok=True)):
            distiller = SoulDistiller("test_entity", "ses_20260722_test_001", "test-model")
            yield distiller
    
    @pytest.mark.asyncio
    async def test_distill_session_returns_list_of_lesson_proposals(self, distiller):
        """T1: distill_session() returns List[LessonProposal]."""
        # Mock _load_session_exchanges to return empty list
        with patch.object(distiller, '_load_session_exchanges', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = []
            
            result = await distiller.distill_session()
            
            # Contract: must return List[LessonProposal]
            assert isinstance(result, list), "distill_session must return a list"
            for item in result:
                assert isinstance(item, LessonProposal), f"Each item must be LessonProposal, got {type(item)}"
    
    @pytest.mark.asyncio
    async def test_distill_session_with_exchanges_returns_l1_proposals(self, distiller):
        """T2: distill_session with exchanges produces L1 proposals."""
        # Mock _load_session_exchanges to return sample exchanges
        with patch.object(distiller, '_load_session_exchanges', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = [
                {"role": "user", "content": "Test question"},
                {"role": "assistant", "content": "Test answer"},
            ]
            
            result = await distiller.distill_session()
            
            # Contract: must return list with L1 proposals
            assert isinstance(result, list)
            l1_proposals = [p for p in result if p.tier == "L1"]
            assert len(l1_proposals) > 0, "Should produce at least one L1 proposal"
            
            for proposal in l1_proposals:
                assert isinstance(proposal, LessonProposal)
                assert proposal.tier == "L1"
                assert proposal.narrative != ""
                assert proposal.lesson_id.startswith("l1-")
                assert proposal.confidence > 0
                assert proposal.model_used == "test-model"  # M22 provenance
    
    @pytest.mark.asyncio
    async def test_write_proposed_lessons_creates_valid_yaml(self, distiller):
        """T3: _write_proposed_lessons creates valid YAML with correct schema."""
        proposals = [
            LessonProposal(
                lesson_id="l1-20260722-001",
                tier="L1",
                narrative="Test narrative",
                evidence=["exchange_0"],
                confidence=0.8,
                source_sessions=["ses_test"],
                model_used="test-model",
            ),
            LessonProposal(
                lesson_id="l2-20260722-001",
                tier="L2",
                insight="Test insight",
                evidence=["exchange_0"],
                confidence=0.7,
                source_sessions=["ses_test"],
                model_used="test-model",
            ),
            LessonProposal(
                lesson_id="l3-20260722-001",
                tier="L3",
                principle="Test principle",
                evidence=["exchange_0"],
                confidence=0.6,
                source_sessions=["ses_test"],
                mandate_refs=["M5", "M11"],
                model_used="test-model",
            ),
        ]
        
        distiller._write_proposed_lessons(proposals)
        
        # Verify file exists
        assert distiller.proposed_path.exists(), "proposed_lessons.yaml must be created"
        
        # Verify YAML structure
        import yaml
        with open(distiller.proposed_path) as f:
            data = yaml.safe_load(f)
        
        # Contract: must have proposals list and metadata
        assert "proposals" in data, "Must have 'proposals' key"
        assert "metadata" in data, "Must have 'metadata' key"
        assert len(data["proposals"]) == 3, "Must have 3 proposals"
        
        # Verify each proposal has required fields
        for proposal in data["proposals"]:
            assert "lesson_id" in proposal
            assert "tier" in proposal
            assert "evidence" in proposal
            assert "confidence" in proposal
            assert "source_sessions" in proposal
            assert "mandate_refs" in proposal
            assert "model_used" in proposal  # M22 provenance
            assert "timestamp" in proposal
            
            # Tier-specific fields
            if proposal["tier"] == "L1":
                assert "narrative" in proposal
            elif proposal["tier"] == "L2":
                assert "insight" in proposal
            elif proposal["tier"] == "L3":
                assert "principle" in proposal
        
        # Verify metadata
        metadata = data["metadata"]
        assert metadata["entity"] == "test_entity"
        assert metadata["session_id"] == "ses_20260722_test_001"
        assert metadata["model_used"] == "test-model"
        assert "tier_counts" in metadata
        assert metadata["tier_counts"]["L1"] == 1
        assert metadata["tier_counts"]["L2"] == 1
        assert metadata["tier_counts"]["L3"] == 1
    
    @pytest.mark.asyncio
    async def test_distill_session_writes_proposed_lessons_yaml(self, distiller):
        """Integration test: full pipeline writes proposed_lessons.yaml."""
        with patch.object(distiller, '_load_session_exchanges', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = [
                {"role": "user", "content": "How do I optimize this?"},
                {"role": "assistant", "content": "Profile first, then optimize."},
            ]
            
            result = await distiller.distill_session()
            
            # Verify file was written
            assert distiller.proposed_path.exists(), "proposed_lessons.yaml must be created"
            
            # Verify content
            import yaml
            with open(distiller.proposed_path) as f:
                data = yaml.safe_load(f)
            
            assert "proposals" in data
            assert len(data["proposals"]) > 0
            assert data["metadata"]["entity"] == "test_entity"
            assert data["metadata"]["model_used"] == "test-model"  # M22 provenance


class TestLessonProposalContract:
    """Contract tests for LessonProposal dataclass."""
    
    def test_lesson_proposal_creation_with_required_fields(self):
        """LessonProposal can be created with required fields."""
        proposal = LessonProposal(
            lesson_id="l1-test-001",
            tier="L1",
            narrative="Test narrative",
        )
        
        assert isinstance(proposal, LessonProposal)
        assert proposal.lesson_id == "l1-test-001"
        assert proposal.tier == "L1"
        assert proposal.narrative == "Test narrative"
        assert proposal.timestamp is not None  # Auto-generated
    
    def test_lesson_proposal_tier_validation(self):
        """LessonProposal tier must be L1, L2, or L3."""
        # Valid tiers
        for tier in ["L1", "L2", "L3"]:
            proposal = LessonProposal(lesson_id="test", tier=tier)
            assert proposal.tier == tier
    
    def test_lesson_proposal_defaults(self):
        """LessonProposal has correct default values."""
        proposal = LessonProposal(lesson_id="test", tier="L1")
        
        assert proposal.principle == ""
        assert proposal.insight == ""
        assert proposal.narrative == ""
        assert proposal.evidence == []
        assert proposal.confidence == 0.0
        assert proposal.source_sessions == []
        assert proposal.mandate_refs == []
        assert proposal.model_used is None
        assert proposal.timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])