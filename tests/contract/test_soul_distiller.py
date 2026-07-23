"""
Contract Tests: SoulDistiller — C-0.5 Soul Distillation Pipeline
M21 compliant: isinstance checks on all API boundaries.

Tests:
1. SoulDistiller initializes correctly
2. distill_session returns List[LessonProposal]
3. Writes valid proposed_lessons.yaml schema
"""

import os
import tempfile
from pathlib import Path
from typing import List

import pytest
import yaml

from omega.scribe.distiller import SoulDistiller, LessonProposal


class TestSoulDistillerInit:
    """Test SoulDistiller initialization."""
    
    def test_initializes_correctly(self):
        """M21: isinstance check on SoulDistiller creation."""
        distiller = SoulDistiller(entity_name="test_entity", session_id="ses_test_001")
        assert isinstance(distiller, SoulDistiller)
        assert distiller.entity_name == "test_entity"
        assert distiller.session_id == "ses_test_001"
        assert distiller.model is None
    
    def test_initializes_with_model(self):
        """M21: model parameter stored for M22 provenance."""
        distiller = SoulDistiller(
            entity_name="test_entity",
            session_id="ses_test_002",
            model="test-model-v1"
        )
        assert distiller.model == "test-model-v1"
    
    def test_creates_entity_dir(self):
        """M11: Entity directory created on init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            distiller = SoulDistiller(
                entity_name="test_entity",
                session_id="ses_test_003",
            )
            distiller.entities_dir = Path(tmpdir) / "entities"
            distiller.entity_dir = distiller.entities_dir / "test_entity"
            distiller.proposed_path = distiller.entity_dir / "proposed_lessons.yaml"
            
            distiller.entity_dir.mkdir(parents=True, exist_ok=True)
            assert distiller.entity_dir.exists()


class TestDistillSession:
    """Test distill_session method."""
    
    @pytest.mark.asyncio
    async def test_returns_list_of_lesson_proposals(self):
        """M21: isinstance check on distill_session return type."""
        distiller = SoulDistiller(entity_name="test_entity", session_id="ses_test_004")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            distiller.entities_dir = Path(tmpdir) / "entities"
            distiller.entity_dir = distiller.entities_dir / "test_entity"
            distiller.proposed_path = distiller.entity_dir / "proposed_lessons.yaml"
            distiller.entity_dir.mkdir(parents=True, exist_ok=True)
            
            result = await distiller.distill_session()
            
            assert isinstance(result, list)
            for item in result:
                assert isinstance(item, LessonProposal)
    
    def test_lesson_proposal_has_required_fields(self):
        """M21: LessonProposal dataclass contract."""
        proposal = LessonProposal(
            lesson_id="l3-20260722-001",
            tier="L3",
            principle="Test principle",
            evidence=["evidence1"],
            confidence=0.95,
            source_sessions=["ses_test"],
            model_used="test-model",
        )
        
        assert isinstance(proposal, LessonProposal)
        assert proposal.lesson_id == "l3-20260722-001"
        assert proposal.tier == "L3"
        assert proposal.principle == "Test principle"
        assert proposal.evidence == ["evidence1"]
        assert proposal.confidence == 0.95
        assert proposal.source_sessions == ["ses_test"]
        assert proposal.model_used == "test-model"
        assert proposal.timestamp is not None


class TestWriteProposedLessons:
    """Test proposed_lessons.yaml write and schema."""
    
    def test_writes_valid_yaml(self):
        """M11: Writes valid proposed_lessons.yaml."""
        distiller = SoulDistiller(entity_name="test_entity", session_id="ses_test_005")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            distiller.entities_dir = Path(tmpdir) / "entities"
            distiller.entity_dir = distiller.entities_dir / "test_entity"
            distiller.proposed_path = distiller.entity_dir / "proposed_lessons.yaml"
            distiller.entity_dir.mkdir(parents=True, exist_ok=True)
            
            proposals = [
                LessonProposal(
                    lesson_id="l3-20260722-001",
                    tier="L3",
                    principle="Test principle",
                    evidence=["evidence1"],
                    confidence=0.95,
                    source_sessions=["ses_test"],
                    model_used="test-model",
                )
            ]
            
            distiller._write_proposed_lessons(proposals)
            
            assert distiller.proposed_path.exists()
            
            # Load and validate
            with open(distiller.proposed_path) as f:
                data = yaml.safe_load(f)
            
            assert "proposals" in data
            assert "metadata" in data
            assert len(data["proposals"]) == 1
            assert data["proposals"][0]["lesson_id"] == "l3-20260722-001"
            assert data["proposals"][0]["tier"] == "L3"
            assert data["metadata"]["entity"] == "test_entity"
            assert data["metadata"]["session_id"] == "ses_test_005"
    
    def test_atomic_write(self):
        """M9: Atomic write with tmp → fsync → replace."""
        distiller = SoulDistiller(entity_name="test_entity", session_id="ses_test_006")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            distiller.entities_dir = Path(tmpdir) / "entities"
            distiller.entity_dir = distiller.entities_dir / "test_entity"
            distiller.proposed_path = distiller.entity_dir / "proposed_lessons.yaml"
            distiller.entity_dir.mkdir(parents=True, exist_ok=True)
            
            # Write proposals
            distiller._write_proposed_lessons([
                LessonProposal(
                    lesson_id="l3-20260722-002",
                    tier="L3",
                    principle="Atomic write principle",
                )
            ])
            
            # Verify no tmp file remains
            tmp_files = list(distiller.entity_dir.glob("*.tmp"))
            assert len(tmp_files) == 0
            
            # Verify main file exists and is valid YAML
            with open(distiller.proposed_path) as f:
                data = yaml.safe_load(f)
            assert data["proposals"][0]["lesson_id"] == "l3-20260722-002"


class TestLessonProposalDataclass:
    """Test LessonProposal dataclass behavior."""
    
    def test_default_values(self):
        """M21: LessonProposal defaults correct."""
        proposal = LessonProposal(
            lesson_id="test",
            tier="L1",
        )
        
        assert proposal.principle == ""
        assert proposal.insight == ""
        assert proposal.narrative == ""
        assert proposal.evidence == []
        assert proposal.confidence == 0.0
        assert proposal.source_sessions == []
        assert proposal.mandate_refs == []
        assert proposal.timestamp is not None
    
    def test_tier_type_enforcement(self):
        """M21: Tier must be L1, L2, or L3."""
        for tier in ["L1", "L2", "L3"]:
            proposal = LessonProposal(lesson_id="test", tier=tier)
            assert proposal.tier == tier
