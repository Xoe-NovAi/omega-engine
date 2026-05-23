import httpx
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import anyio

from omega.oracle.orchestrator import Orchestrator
from omega.oracle.resource_guard import ResourceGuard


@pytest.fixture
def orchestrator():
    return Orchestrator(resource_guard=ResourceGuard(limit=1))


class TestMCPWatchdog:
    def _make_mock_response_context_manager(self, status_code: int):
        """Build a mock that behaves like an async context manager for httpx.Response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = status_code

        class AsyncContextManagerMock:
            async def __aenter__(self_acm):
                return mock_response

            async def __aexit__(self_acm, exc_type, exc_val, exc_tb):
                pass
        return AsyncContextManagerMock()

    @pytest.mark.asyncio
    async def test_watch_mcps_all_healthy(self, orchestrator):
        """watch_mcps should mark all MCPs healthy when they respond 200."""
        mock_acm = self._make_mock_response_context_manager(200)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.return_value = mock_acm
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            async def one_iter():
                with anyio.move_on_after(1.0):
                    await orchestrator.watch_mcps()

            await one_iter()
            for name in orchestrator.mcp_ports:
                assert orchestrator._mcp_status.get(name, {}).get("status") == "healthy", f"{name} not healthy"

    @pytest.mark.asyncio
    async def test_watch_mcps_connect_error(self, orchestrator):
        """watch_mcps should mark unresponsive MCPs on connection error."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.side_effect = httpx.ConnectError("refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            async def one_iter():
                with anyio.move_on_after(1.0):
                    await orchestrator.watch_mcps()

            await one_iter()
            for name in orchestrator.mcp_ports:
                assert orchestrator._mcp_status.get(name, {}).get("status") == "unresponsive"

    @pytest.mark.asyncio
    async def test_watch_mcps_degraded(self, orchestrator):
        """watch_mcps should mark MCPs as degraded on non-200 status."""
        mock_acm = self._make_mock_response_context_manager(500)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.return_value = mock_acm
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("anyio.run_process", new_callable=AsyncMock) as mock_process:
                async def one_iter():
                    with anyio.move_on_after(0.1):
                        await orchestrator.watch_mcps()

                await one_iter()
                for name in orchestrator.mcp_ports:
                    status = orchestrator._mcp_status.get(name, {}).get("status")
                    assert status in ("degraded", "unresponsive"), f"{name} unexpected status: {status}"


class TestDispatchAgent:
    @pytest.mark.asyncio
    async def test_dispatch_unsupported_cli(self, orchestrator):
        """dispatch_agent should return error for unsupported CLI type."""
        result = await orchestrator.dispatch_agent("unknown_cli", "task", "Sophia")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_dispatch_cline_success(self, orchestrator):
        """dispatch_agent should run cline and return stdout on success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Task complete"
        mock_result.stderr = b""

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("cline", "do something", "Sophia", timeout=30)

        assert result["status"] == "success"
        assert result["returncode"] == 0

    @pytest.mark.asyncio
    async def test_dispatch_opencode_success(self, orchestrator):
        """dispatch_agent should run opencode and return stdout on success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Done"
        mock_result.stderr = b""

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("opencode", "do it", "Sophia", timeout=30)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_dispatch_cline_failure(self, orchestrator):
        """dispatch_agent should return failure on non-zero returncode."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b""
        mock_result.stderr = b"Error occurred"

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("cline", "do something", "Sophia", timeout=30)

        assert result["status"] == "failed"
        assert result["returncode"] == 1

    @pytest.mark.asyncio
    async def test_dispatch_timeout(self, orchestrator):
        """dispatch_agent should return timeout when execution takes too long."""
        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", side_effect=TimeoutError("timed out")):
                result = await orchestrator.dispatch_agent("cline", "task", "Sophia", timeout=1)

        assert result["status"] == "timeout"


class TestGetMCPStatus:
    def test_get_mcp_status_empty(self, orchestrator):
        """get_mcp_status returns empty dict when no checks have run."""
        assert orchestrator.get_mcp_status() == {}

    def test_get_mcp_status_after_check(self, orchestrator):
        """get_mcp_status returns stored statuses."""
        orchestrator._mcp_status["omega-hub"] = {"status": "healthy", "port": 8016}
        status = orchestrator.get_mcp_status()
        assert status["omega-hub"]["status"] == "healthy"
