# tests/test_openclaw_bridge.py
import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from omega.bridge.opencode_bridge import bridge, BudgetGate, TokenLedger
from omega.oracle.oracle import OracleResponse
from omega.errors import OmegaError

client = TestClient(bridge.app)

@pytest.mark.anyio
async def test_bridge_health_check():
    """Verify the sovereign health probe endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["bridge"] == "opencode-v1"

@pytest.mark.anyio
async def test_bridge_websocket_flow():
    """Test full WebSocket message loop: Send -> Oracle -> Stream."""
    # Setup mocks
    mock_response = OracleResponse(
        text="Sovereign response from the void.",
        entity="KALI",
        trace_id="trc_123",
        cost_warning=None,
        session_id="ses_abc"
    )
    
    with patch.object(bridge.oracle, 'talk', new_callable=AsyncMock) as mock_talk:
        mock_talk.return_value = mock_response
        
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.send_text("Hello Omega")
            
            # The bridge chunks response into 50-char segments
            # "Sovereign response from the void." is < 50 chars, so 1 chunk
            data = websocket.receive_text()
            assert data == "Sovereign response from the void."
            
            mock_talk.assert_called_once_with("Hello Omega")

@pytest.mark.anyio
async def test_bridge_budget_gate_block():
    """Shatter-Glass: Verify Cloud Budget Gate blocks requests."""
    with patch.object(BudgetGate, 'check_budget', new_callable=AsyncMock) as mock_gate:
        mock_gate.return_value = False  # Budget exceeded
        
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.send_text("Request cloud inference")
            data = websocket.receive_text()
            assert "Budget gate exceeded" in data

@pytest.mark.anyio
async def test_bridge_token_ledger_integration():
    """Shatter-Glass: Verify Token Ledger is called on success."""
    mock_response = OracleResponse(
        text="Tokenized response.",
        entity="SOPHIA",
        trace_id="trc_token",
        cost_warning=None,
        session_id="ses_token"
    )
    
    with patch.object(bridge.oracle, 'talk', new_callable=AsyncMock) as mock_talk, \
         patch.object(TokenLedger, 'record_transaction', new_callable=AsyncMock) as mock_ledger:
        
        mock_talk.return_value = mock_response
        
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.send_text("Test ledger")
            websocket.receive_text() # consume response
            
            mock_ledger.assert_called_once()
            args = mock_ledger.call_args[1]
            assert args['trace_id'] == "trc_token"
            assert args['entity'] == "SOPHIA"
            assert isinstance(args['tokens_in'], int)
            assert isinstance(args['tokens_out'], int)

@pytest.mark.anyio
async def test_bridge_oracle_error_handling():
    """Verify bridge catches OmegaErrors and reports them to client."""
    with patch.object(bridge.oracle, 'talk', new_callable=AsyncMock) as mock_talk:
        mock_talk.side_effect = OmegaError("Core engine deadlock")
        
        with client.websocket_connect("/ws/chat") as websocket:
                websocket.send_text("Trigger error")
                data = websocket.receive_text()
                assert "Engine Error" in data
                assert "Core engine deadlock" in data

