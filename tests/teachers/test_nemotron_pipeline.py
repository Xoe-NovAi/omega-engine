# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — M21 Contract Tests for Nemotron Teacher Pipeline
# AP: AP-M21-NEMOTON-TEACHER-v1.0.0
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_m21 ⬡ ACTIVE
#
# Contract tests verifying Nemotron Teacher Pipeline for DPO pair generation.

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from dataclasses import asdict

from omega.teachers.nemotron_pipeline import (
    NemotronTeacherPipeline,
    DPOPair,
    CritiqueResult,
)


@pytest.fixture
def mock_openrouter_key():
    """Fixture providing a mock OpenRouter API key."""
    return "sk-or-v1-test-key-1234567890"


@pytest.fixture
def temp_dpo_dir():
    """Fixture providing a temporary directory for DPO pairs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def pipeline(mock_openrouter_key, temp_dpo_dir):
    """Fixture providing a NemotronTeacherPipeline instance."""
    return NemotronTeacherPipeline(
        openrouter_key=mock_openrouter_key,
        dpo_storage_dir=str(temp_dpo_dir),
        max_iterations=2,
    )


class TestNemotronTeacherPipeline:
    """M21 Contract Tests: Nemotron Teacher Pipeline."""
    
    def test_pipeline_initialization(self, pipeline, mock_openrouter_key, temp_dpo_dir):
        """Verify pipeline initializes correctly."""
        assert pipeline.openrouter_key == mock_openrouter_key
        assert pipeline.dpo_storage_dir == temp_dpo_dir
        assert pipeline.max_iterations == 2
        assert pipeline.stats["pairs_generated"] == 0
    
    def test_dpo_pair_dataclass(self):
        """Verify DPOPair dataclass structure."""
        pair = DPOPair(
            prompt="Test prompt",
            chosen="Chosen response",
            rejected="Rejected response",
            metadata={"model": "test"},
        )
        
        assert pair.prompt == "Test prompt"
        assert pair.chosen == "Chosen response"
        assert pair.rejected == "Rejected response"
        assert pair.metadata == {"model": "test"}
        assert pair.timestamp is not None
    
    def test_critique_result_dataclass(self):
        """Verify CritiqueResult dataclass structure."""
        result = CritiqueResult(
            accepted=True,
            issues=["issue1"],
            suggestions=["suggestion1"],
            raw_response="raw",
        )
        
        assert result.accepted is True
        assert result.issues == ["issue1"]
        assert result.suggestions == ["suggestion1"]
        assert result.raw_response == "raw"
    
    def test_parse_critique_accepted(self, pipeline):
        """Verify critique parsing for accepted response."""
        raw = """- ACCEPTED: yes
- ISSUES: none
- SUGGESTIONS: none"""
        
        result = pipeline._parse_critique(raw)
        assert result.accepted is True
        assert result.issues == ["none"]
        assert result.suggestions == ["none"]
    
    def test_parse_critique_rejected(self, pipeline):
        """Verify critique parsing for rejected response."""
        raw = """- ACCEPTED: no
- ISSUES: factual error, missing context
- SUGGESTIONS: add examples, clarify terminology"""
        
        result = pipeline._parse_critique(raw)
        assert result.accepted is False
        assert "factual error" in result.issues
        assert "add examples" in result.suggestions
    
    def test_parse_verdict_accepted(self, pipeline):
        """Verify verdict parsing for accepted response."""
        raw = """- ACCEPTED: yes
- REASON: Addressed all issues"""
        
        result = pipeline._parse_verdict(raw)
        assert result.accepted is True
    
    def test_parse_verdict_rejected(self, pipeline):
        """Verify verdict parsing for rejected response."""
        raw = """- ACCEPTED: no
- REASON: Still has factual errors"""
        
        result = pipeline._parse_verdict(raw)
        assert result.accepted is False
        assert "Still has factual errors" in result.issues
    
    @pytest.mark.anyio
    async def test_generate_dpo_pair_with_mock(self, pipeline):
        """Verify DPO pair generation with mock responses."""
        # Mock the Nemotron API calls
        mock_critique = """- ACCEPTED: no
- ISSUES: needs more detail
- SUGGESTIONS: expand explanation"""
        
        mock_verdict = """- ACCEPTED: yes
- REASON: Good improvement"""
        
        with patch.object(pipeline, '_call_nemotron') as mock_call:
            mock_call.side_effect = [mock_critique, mock_verdict]
            
            # Mock local generation
            async def mock_generate(prompt, model):
                return f"Mock response for: {prompt[:50]}..."
            
            pair = await pipeline.generate_dpo_pair(
                prompt="Explain Zone Memory",
                local_generate_fn=mock_generate,
            )
            
            assert pair is not None
            assert pair.prompt == "Explain Zone Memory"
            assert pair.chosen != pair.rejected  # Different responses
            assert pipeline.stats["pairs_generated"] == 1
    
    @pytest.mark.anyio
    async def test_generate_dpo_pair_saves_to_file(self, pipeline, temp_dpo_dir):
        """Verify DPO pairs are saved to JSONL files."""
        # Mock responses
        mock_critique = """- ACCEPTED: yes
- ISSUES: none
- SUGGESTIONS: none"""
        
        with patch.object(pipeline, '_call_nemotron') as mock_call:
            mock_call.return_value = mock_critique
            
            async def mock_generate(prompt, model):
                return "Mock response"
            
            await pipeline.generate_dpo_pair(
                prompt="Test prompt",
                local_generate_fn=mock_generate,
            )
            
            # Check that file was created
            jsonl_files = list(temp_dpo_dir.glob("dpo_pairs_*.jsonl"))
            assert len(jsonl_files) == 1
            
            # Check file content
            with open(jsonl_files[0]) as f:
                content = f.read()
                data = json.loads(content)
                assert data["prompt"] == "Test prompt"
                assert data["chosen"] == "Mock response"
    
    @pytest.mark.anyio
    async def test_generate_dpo_pair_failure_handling(self, pipeline):
        """Verify pipeline handles generation failures gracefully."""
        # Mock failed local generation
        async def failing_generate(prompt, model):
            raise Exception("Generation failed")
        
        pair = await pipeline.generate_dpo_pair(
            prompt="Test prompt",
            local_generate_fn=failing_generate,
        )
        
        assert pair is None
        assert pipeline.stats["pairs_generated"] == 0
    
    def test_stats_tracking(self, pipeline):
        """Verify stats are correctly tracked."""
        initial_stats = pipeline.get_stats()
        assert initial_stats["pairs_generated"] == 0
        assert initial_stats["pairs_accepted"] == 0
        assert initial_stats["pairs_rejected"] == 0
        assert initial_stats["total_iterations"] == 0
    
    def test_nemotron_model_constant(self, pipeline):
        """Verify Nemotron model constant is correct."""
        assert pipeline.NEMOTRON_MODEL == "nvidia/nemotron-3-ultra-550b-a55b"
