import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from omega.workers.background_researcher.distiller import Distiller
from omega.workers.background_researcher.models import GnosisPacket
from omega.workers.background_researcher.credit_budget import APICreditBudget

@pytest.mark.anyio
async def test_jem_pipeline_verification():
    # 1. Setup Mocks
    mock_budget = MagicMock(spec=APICreditBudget)
    mock_budget.check_daily_limit.return_value = True
    
    distiller = Distiller(budget=mock_budget)
    
    # Mock Backends
    distiller.lmster.call = AsyncMock(return_value='{"claims": [{"claim": "T1 Fact", "sources": ["url1"], "confidence": 0.9}]}')
    distiller.minimax.call = AsyncMock(return_value='{"claims": [{"claim": "T2 Fact", "sources": ["url1"], "agreement_level": 0.8}], "distillations": [{"claim": "T2 Fact", "l1": "N1", "l2": "I2", "l3": "P3"}], "convergence_signal": "verified", "recommendation": "write_to_soul"}')
    distiller.gemini.call = AsyncMock(return_value='{"reviewed": true, "corrections": [{"claim": "T2 Fact", "correction": "Corrected Fact"}], "confidence_scores": {"l3_principle": 0.9}, "recommended_directions": [{"direction": "Follow-up", "reason": "Interesting", "priority": 0.9}]}')
    distiller.gemini._extract_json = MagicMock(side_effect=lambda x: json.loads(x))

    # Mock SoulUpdateManager to avoid writing to real files during test
    distiller.soul_manager.update_subfacet_soul = AsyncMock()

    # 2. Run Distillation
    topic = "Test Topic"
    content = "Some research content"
    sources = ["http://example.com"]
    
    gnosis = await distiller.distill(topic, content, sources)

    # 3. Verifications
    
    # A. Budget Checks
    # Should check gemma_calls for T2 and T3
    assert mock_budget.check_daily_limit.call_count >= 2
    mock_budget.check_daily_limit.assert_any_call("gemma_calls")
    assert mock_budget.increment_daily.call_count >= 2
    mock_budget.increment_daily.assert_any_call("gemma_calls")

    # B. T3 Application
    # Check if correction was applied to L3
    assert "[CORRECTION: Corrected Fact]" in gnosis.distillations[0]["l3"]
    # Check if recommended directions were captured
    assert len(gnosis.recommended_directions) == 1
    assert gnosis.recommended_directions[0]["direction"] == "Follow-up"

    # C. Soul Update Loop
    # Should call update_subfacet_soul for initiate, analyst, and editor
    assert distiller.soul_manager.update_subfacet_soul.call_count == 3
    calls = [call.args[0] for call in distiller.soul_manager.update_subfacet_soul.call_args_list]
    assert "initiate" in calls
    assert "analyst" in calls
    assert "editor" in calls

    print("\n✅ Jem Pipeline Verification Passed!")

if __name__ == "__main__":
    import anyio
    anyio.run(test_jem_pipeline_verification)
