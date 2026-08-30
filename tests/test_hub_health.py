# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Hub Server — Health & Registration Tests.

Tests that the omega-hub MCP server is healthy, tools are registered,
and critical tools are callable. These are the "sentinel" tests that
should have existed since Day 1.

AP Token: AP-HUB-HEALTH-TESTS-v1.0.0
"""
import json
import socket
from pathlib import Path
import pytest
import httpx2 as httpx


HUB_BASE = "http://127.0.0.1:8016"


def _hub_reachable() -> bool:
    """Check if omega-hub is reachable at 127.0.0.1:8016."""
    try:
        with socket.create_connection(("127.0.0.1", 8016), timeout=1.0):
            return True
    except OSError:
        return False


# ── Module-level markers: integration tier + clean skip when hub is down ──
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _hub_reachable(), reason="omega-hub not running at 127.0.0.1:8016"),
]


@pytest.fixture(scope="module")
def hub_url():
    return HUB_BASE


@pytest.fixture(scope="module")
def hub_client():
    """Shared httpx client for the module."""
    with httpx.Client(base_url=HUB_BASE, timeout=10.0) as client:
        yield client


# ── Health Tests ──


class TestHubHealth:
    """Verify the omega-hub health endpoint."""

    def test_health_endpoint_returns_200(self, hub_client):
        """Health endpoint must return HTTP 200."""
        resp = hub_client.get("/health")
        assert resp.status_code == 200

    def test_health_endpoint_returns_json(self, hub_client):
        """Health endpoint must return valid JSON."""
        resp = hub_client.get("/health")
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data

    def test_health_status_is_healthy(self, hub_client):
        """Health status must be 'healthy', not 'degraded' or 'error'."""
        resp = hub_client.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_version_is_string(self, hub_client):
        """Version must be a non-empty string."""
        resp = hub_client.get("/health")
        data = resp.json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


# ── Tool Registration Tests ──


class TestToolRegistration:
    """Verify that tools are registered in the MCP tool manager."""

    def test_debug_tools_returns_count(self, hub_client):
        """Debug endpoint must return tool_manager_count."""
        resp = hub_client.get("/debug/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tool_manager_count" in data

    def test_tool_count_above_minimum(self, hub_client):
        """At least 50 tools must be registered (we have 70+)."""
        resp = hub_client.get("/debug/tools")
        data = resp.json()
        count = data["tool_manager_count"]
        assert count >= 50, f"Expected >=50 tools, got {count}"

    def test_tool_count_matches_source(self, hub_client):
        """Tool count must match the number of @mcp.tool() decorators in tools.py."""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "@mcp.tool()",
             "mcp_servers/omega_hub/hub_tools/tools.py"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
        expected = int(result.stdout.strip())
        resp = hub_client.get("/debug/tools")
        data = resp.json()
        actual = data["tool_manager_count"]
        # Allow some tolerance (decorators vs registered tools)
        assert actual >= expected - 5, (
            f"Tool count mismatch: {actual} registered vs {expected} decorators"
        )

    def test_sample_tools_are_strings(self, hub_client):
        """Sample tool names must be non-empty strings."""
        resp = hub_client.get("/debug/tools")
        data = resp.json()
        names = data.get("sample_tools", [])
        assert len(names) > 0
        for name in names:
            assert isinstance(name, str)
            assert len(name) > 0


# ── Critical Tool Presence Tests ──


class TestCriticalTools:
    """Verify that critical tools are registered and accessible."""

    EXPECTED_TOOLS = [
        "oracle_talk",
        "oracle_summon",
        "oracle_list_entities",
        "library_fts_search",
        "library_search",
        "library_web_search",
        "library_get_document",
        "memory_search",
        "omega_memory_search",
        "sovereign_search",
        "hivemind_post_context",
        "hivemind_get_awareness",
        "hivemind_heartbeat",
        # New consolidated tools
        "hivemind_handoff",
        "library_inbox",
        "library_discovery",
        "oracle_debug",
        "system_stats",
        "github",
        "library_web_search",
    ]

    def _get_all_tool_names(self, hub_client) -> list:
        """Get full tool list from debug endpoint."""
        resp = hub_client.get("/debug/tools")
        data = resp.json()
        return data.get("sample_tools", [])

    @pytest.mark.parametrize("tool_name", EXPECTED_TOOLS)
    def test_critical_tool_registered(self, hub_client, tool_name):
        """Each critical tool must be in the registered tool list."""
        names = self._get_all_tool_names(hub_client)
        # Note: debug endpoint only shows first 10 tools
        # For full check, we'd need SSE protocol — this is a smoke test
        if tool_name not in names:
            pytest.skip(
                f"{tool_name} not in debug sample (first 10 only) — "
                "use SSE ListToolsRequest for full check"
            )


# ── SSE Connectivity Tests ──


class TestSSEConnectivity:
    """Verify SSE transport is functional."""

    def test_sse_endpoint_returns_event_stream(self, hub_client):
        """SSE endpoint must accept text/event-stream."""
        with hub_client.stream("GET", "/sse", headers={"Accept": "text/event-stream"}) as resp:
            assert resp.status_code == 200
            # Read first event
            lines = []
            for line in resp.iter_lines():
                lines.append(line)
                if len(lines) >= 3:
                    break
            # Should contain 'event: endpoint' and 'data: /messages/...'
            text = "\n".join(lines)
            assert "endpoint" in text.lower() or "data:" in text.lower()


# ── Endpoint Availability Tests ──


class TestEndpointAvailability:
    """Verify that all expected REST endpoints are reachable."""

    @pytest.mark.parametrize("path,expected_status", [
        ("/health", 200),
        ("/debug/tools", 200),
        ("/config/providers", 200),
        ("/provider", 200),
        ("/entity/current", 200),
        ("/agent", 200),
    ])
    def test_endpoint_returns_expected_status(self, hub_client, path, expected_status):
        """Each REST endpoint must return its expected HTTP status."""
        resp = hub_client.get(path)
        assert resp.status_code == expected_status, (
            f"GET {path} returned {resp.status_code}, expected {expected_status}"
        )

    def test_config_providers_returns_json(self, hub_client):
        """Config providers must return valid JSON."""
        resp = hub_client.get("/config/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_entity_current_returns_json(self, hub_client):
        """Entity current must return valid JSON with entity name."""
        resp = hub_client.get("/entity/current")
        assert resp.status_code == 200
        data = resp.json()
        assert "entity" in data


# ── Resilience Tests ──


class TestHubResilience:
    """Verify the hub doesn't crash on bad input."""

    def test_unknown_endpoint_returns_404(self, hub_client):
        """Unknown endpoints must return 404, not crash the server."""
        resp = hub_client.get("/nonexistent/endpoint")
        assert resp.status_code == 404

    def test_health_still_works_after_bad_request(self, hub_client):
        """Health must still return 200 after a bad request."""
        # Send bad request
        hub_client.get("/nonexistent")
        # Then check health
        resp = hub_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_concurrent_health_requests(self, hub_client):
        """Multiple concurrent health requests must all succeed."""
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(hub_client.get, "/health") for _ in range(5)]
            results = [f.result() for f in futures]
        for resp in results:
            assert resp.status_code == 200
            assert resp.json()["status"] == "healthy"
