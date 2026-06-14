# tests/test_openclaw_runtime.py
import pytest
import anyio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.omega.runtime.openclaw_runtime import OpenClawRuntime
from src.omega.oracle.oracle import OracleResponse

@pytest.fixture
def mock_engine():
    oracle = MagicMock()
    oracle.talk = AsyncMock()
    oracle.summon = AsyncMock()
    
    gateway = MagicMock()
    gateway.select_provider = AsyncMock()
    gateway.get_preferred_backend = AsyncMock()
    gateway._cloud_providers = ["google", "openrouter"]
    
    return oracle, gateway

@pytest.mark.anyio
async def test_runtime_soul_loading(mock_engine, tmp_path):
    """Verify SOUL.md parsing logic."""
    oracle, gateway = mock_engine
    runtime = OpenClawRuntime(oracle, gateway)
    
    soul_file = tmp_path / "SOUL.md"
    soul_file.write_text("routing_rule: high_precision\npreferred_model: gemma-4-31b\nlast_session_id: ses_old")
    
    soul = await runtime._load_soul(soul_file)
    assert soul["routing_rule"] == "high_precision"
    assert soul["preferred_model"] == "gemma-4-31b"
    assert soul["last_session_id"] == "ses_old"

@pytest.mark.anyio
async def test_runtime_session_persistence(mock_engine, tmp_path):
    """Verify session_id is correctly persisted to SOUL.md."""
    oracle, gateway = mock_engine
    runtime = OpenClawRuntime(oracle, gateway)
    
    soul_file = tmp_path / "SOUL.md"
    soul_file.write_text("entity: TEST_ENTITY")
    
    await runtime._persist_session(soul_file, "ses_new_123")
    
    content = soul_file.read_text()
    assert "last_session_id: ses_new_123" in content
    assert "entity: TEST_ENTITY" in content

@pytest.mark.anyio
async def test_runtime_budget_gate_enforcement(mock_engine, tmp_path):
    """Shatter-Glass: Verify cloud budget blocks while local bypasses."""
    oracle, gateway = mock_engine
    runtime = OpenClawRuntime(oracle, gateway)
    
    # Mock health monitor quota usage
    with patch('src.omega.runtime.openclaw_runtime.get_health_monitor') as mock_hm_factory:
        mock_hm = MagicMock()
        mock_hm_factory.return_value = mock_hm
        runtime.health_monitor = mock_hm
        
        soul_file = tmp_path / "SOUL.md"
        soul_file.write_text("")
        
        # Case 1: Cloud provider budget exceeded
        gateway.select_provider.return_value = "google"
        mock_hm.get_quota_usage.return_value = 1.1 # > 100%
        
        res = await runtime.execute("SOPHIA", "Hello", str(soul_file))
        assert "cloud budget exceeded" in res
        
        # Case 2: Local provider bypasses budget
        gateway.select_provider.return_value = "native-gguf"
        # Even if quota is high, local should pass
        mock_hm.get_quota_usage.return_value = 2.0 
        
        # Mock oracle response to avoid crash
        oracle.talk.return_value = OracleResponse(text="Local OK", entity="SOPHIA", trace_id="t1", session_id="s1")
        
        res = await runtime.execute("SOPHIA", "Hello", str(soul_file))
        assert res == "Local OK"

@pytest.mark.anyio
async def test_runtime_routing_model_override(mock_engine, tmp_path):
    """Verify preferred_model in SOUL.md triggers oracle.summon."""
    oracle, gateway = mock_engine
    runtime = OpenClawRuntime(oracle, gateway)
    
    soul_file = tmp_path / "SOUL.md"
    soul_file.write_text("preferred_model: deepseek-r1")
    
    gateway.select_provider.return_value = "native-gguf"
    oracle.summon.return_value = OracleResponse(text="Summoned", entity="X", trace_id="t1", session_id="s1")
    
    await runtime.execute("X", "Query", str(soul_file))
    
    oracle.summon.assert_called_once_with(
        entity_name="X",
        query="Query",
        model_override="deepseek-r1"
    )
    oracle.talk.assert_not_called()

@pytest.mark.anyio
async def test_runtime_full_lifecycle(mock_engine, tmp_path):
    """Verify the complete sequence: Load -> Route -> Budget -> Talk -> Ledger -> Persist."""
    oracle, gateway = mock_engine
    runtime = OpenClawRuntime(oracle, gateway)
    
    soul_file = tmp_path / "SOUL.md"
    soul_file.write_text("routing_rule: default")
    
    gateway.select_provider.return_value = "native-gguf"
    oracle.talk.return_value = OracleResponse(
        text="Lifecycle Complete", 
        entity="KALI", 
        trace_id="trc_full", 
        session_id="ses_full"
    )
    
    with patch.object(runtime.health_monitor, 'record_token_usage') as mock_ledger:
        res = await runtime.execute("KALI", "Lifecycle test", str(soul_file))
        
        assert res == "Lifecycle Complete"
        mock_ledger.assert_called_once()
        # Verify session persistence
        assert "last_session_id: ses_full" in soul_file.read_text()
