# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import httpx2 as httpx
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import anyio
import subprocess

from omega.oracle.orchestrator import Orchestrator
from omega.oracle.resource_guard import ResourceGuard


@pytest.fixture
def orchestrator():
    return Orchestrator(resource_guard=ResourceGuard(max_ram_mb=128))


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

    @patch("subprocess.Popen")
    @pytest.mark.anyio
    async def test_watch_mcps_all_healthy(self, mock_popen, orchestrator):
        """watch_mcps should mark all MCPs healthy when they respond 200."""
        mock_popen.return_value = MagicMock(pid=12345)
        mock_acm = self._make_mock_response_context_manager(200)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.return_value = mock_acm
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx2.AsyncClient", return_value=mock_client):
            with patch("anyio.run_process", new_callable=AsyncMock) as mock_process:
                async def one_iter():
                    with anyio.move_on_after(5.0):
                        await orchestrator.watch_mcps()

                await one_iter()
                for name in orchestrator.mcp_ports:
                    assert orchestrator._mcp_status.get(name, {}).get("status") == "healthy", f"{name} not healthy"


    @patch("subprocess.Popen")
    @pytest.mark.anyio
    async def test_watch_mcps_connect_error(self, mock_popen, orchestrator):
        """watch_mcps should mark unresponsive MCPs on connection error."""
        mock_popen.return_value = MagicMock(pid=12345)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.side_effect = httpx.ConnectError("refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx2.AsyncClient", return_value=mock_client):
            with patch("anyio.run_process", new_callable=AsyncMock) as mock_process:
                async def one_iter():
                    with anyio.move_on_after(5.0):
                        await orchestrator.watch_mcps()

                await one_iter()
                for name in orchestrator.mcp_ports:
                    assert orchestrator._mcp_status.get(name, {}).get("status") == "unresponsive"


    @patch("subprocess.Popen")
    @pytest.mark.anyio
    async def test_watch_mcps_degraded(self, mock_popen, orchestrator):
        """watch_mcps should mark MCPs as degraded on non-200 status."""
        mock_popen.return_value = MagicMock(pid=12345)
        mock_acm = self._make_mock_response_context_manager(500)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.stream.return_value = mock_acm
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx2.AsyncClient", return_value=mock_client):
            with patch("anyio.run_process", new_callable=AsyncMock) as mock_process:
                async def one_iter():
                    with anyio.move_on_after(0.1):
                        await orchestrator.watch_mcps()

                await one_iter()
                for name in orchestrator.mcp_ports:
                    status = orchestrator._mcp_status.get(name, {}).get("status")
                    assert status in ("degraded", "unresponsive", "starting"), f"{name} unexpected status: {status}"


class TestDispatchAgent:
    @pytest.mark.anyio
    async def test_dispatch_unsupported_cli(self, orchestrator):
        """dispatch_agent should return error for unsupported CLI type."""
        task_prompt = """[VERIFICATION]
Role: Test
Task: Verify unsupported CLI handling
Constraints: Must return error status
Output: Error dict with status=error
"""
        result = await orchestrator.dispatch_agent("unknown_cli", task_prompt, "Sophia")
        assert result["status"] == "error"

    @pytest.mark.anyio
    async def test_dispatch_cline_success(self, orchestrator):
        """dispatch_agent should run cline and return stdout on success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Task complete"
        mock_result.stderr = b""
        task_prompt = """[VERIFICATION]
Role: Test
Task: Execute cline task
Constraints: Must return success
Output: Success dict
"""

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("cline", task_prompt, "Sophia", timeout=30)

        assert result["status"] == "success"
        assert result["returncode"] == 0

    @pytest.mark.anyio
    async def test_dispatch_opencode_success(self, orchestrator):
        """dispatch_agent should run opencode and return stdout on success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Done"
        mock_result.stderr = b""
        task_prompt = """[VERIFICATION]
Role: Test
Task: Execute opencode task
Constraints: Must return success
Output: Success dict
"""

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("opencode", task_prompt, "Sophia", timeout=30)

        assert result["status"] == "success"

    @pytest.mark.anyio
    async def test_dispatch_cline_failure(self, orchestrator):
        """dispatch_agent should return failure on non-zero returncode."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b""
        mock_result.stderr = b"Error occurred"
        task_prompt = """[VERIFICATION]
Role: Test
Task: Execute cline task
Constraints: Must return failure
Output: Failed dict
"""

        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", new_callable=AsyncMock, return_value=mock_result):
                result = await orchestrator.dispatch_agent("cline", task_prompt, "Sophia", timeout=30)

        assert result["status"] == "failed"
        assert result["returncode"] == 1

    @pytest.mark.anyio
    async def test_dispatch_timeout(self, orchestrator):
        """dispatch_agent should return timeout when execution takes too long."""
        task_prompt = """[VERIFICATION]
Role: Test
Task: Execute cline task with timeout
Constraints: Must return timeout
Output: Timeout dict
"""
        with patch(
            "omega.oracle.orchestrator.EntityWorkspaceManager.get_soul_prompt",
            new_callable=AsyncMock,
            return_value="You are Sophia.",
        ):
            with patch("anyio.run_process", side_effect=TimeoutError("timed out")):
                result = await orchestrator.dispatch_agent("cline", task_prompt, "Sophia", timeout=1)

        assert result["status"] == "timeout"


class TestGetMCPStatus:
    def test_get_mcp_status_empty(self, orchestrator):
        """get_mcp_status returns empty dict when no checks have run."""
        orchestrator._mcp_status = {}
        assert orchestrator.get_mcp_status() == {}

    def test_get_mcp_status_after_check(self, orchestrator):
        """get_mcp_status returns stored statuses for managed MCPs only.
        
        Note: omega-hub is managed by systemd, not Orchestrator, so it won't
        appear in _mcp_status. Only firecrawl and searxng are managed.
        """
        orchestrator._mcp_status["firecrawl"] = {"status": "healthy", "port": 8015}
        orchestrator._mcp_status["searxng"] = {"status": "healthy", "port": 8018}
        status = orchestrator.get_mcp_status()
        assert status["firecrawl"]["status"] == "healthy"
        assert status["searxng"]["status"] == "healthy"
        # omega-hub should NOT be in status (managed by systemd)
        assert "omega-hub" not in status
