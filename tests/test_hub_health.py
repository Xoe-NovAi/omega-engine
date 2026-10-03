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
        """The Hub must retain a healthy minimum tool surface."""
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
    """Verify that critical tools are registered and accessible.

    [seam-fix 2026-09-28 carmack] This class previously asserted against
    `/debug/tools` → `sample_tools`, which the endpoint documents as a SAMPLE:
    the live response is

        {"tool_manager_count": 54, ..., "sample_tools": [ ...10 names... ]}

    Ten of fifty-four. Every assertion therefore SKIPPED, permanently —
    `OK (skipped=20)` — so this test could not fail, and in particular could
    not have caught the Hivemind consolidation that removed
    `hivemind_post_context`, `hivemind_get_awareness` and
    `hivemind_heartbeat` from the registered surface.

    It also asserted three names that were never in the surface
    (`library_search`, `memory_search`, and — via the pass — the three retired
    Hivemind names), and `library_search` is not even accepted by the hub's
    own tool-surface curation at boot.

    The fix: assert against the COMPLETE registered surface, obtained from
    the FastMCP registry in-process (`mcp.list_tools()`), which is the same
    list the MCP `tools/list` response serves. A truncated source is treated
    as a hard failure, never as a skip.
    """

    # The Hivemind surface after the NES→EIS consolidation (2026-09-28):
    # 15 tools collapsed to these 4. Naming the *current* set means a future
    # consolidation that drops one of these fails loudly.
    EXPECTED_HIVEMIND_TOOLS = [
        "hivemind_awareness",
        "hivemind_get_metrics",
        "hivemind_handoff",
        "hivemind_lock",
    ]

    # Retired by the consolidation. Kept as an explicit ABSENCE assertion:
    # a name that was folded into another tool must not reappear, and its
    # return to the surface would mean the shim and the real tool diverged.
    RETIRED_HIVEMIND_TOOLS = [
        "hivemind_post_context",
        "hivemind_get_awareness",
        "hivemind_heartbeat",
        "hivemind_workspace_lock_acquire",
        "hivemind_workspace_lock_release",
        "hivemind_workspace_lock_check",
        "hivemind_redis_publish",
        "hivemind_redis_subscribe",
    ]

    # Non-Hivemind tools that must remain available.
    EXPECTED_CORE_TOOLS = [
        "oracle_talk",
        "oracle_summon",
        "oracle_list_entities",
        "omega_memory_search",
        "sovereign_search",
        "library_fts_search",
        "library_web_search",
        "library_get_document",
        "library_inbox",
        "library_discovery",
        "oracle_debug",
        "system_stats",
        "github",
    ]

    @pytest.fixture(scope="class")
    def registered_tools(self) -> list:
        """The COMPLETE registered MCP tool surface, enumerated in a SUBPROCESS.

        Read from the FastMCP registry rather than `/debug/tools`, which
        returns a 10-name sample. Any failure to enumerate is a hard error:
        a test that cannot see the surface must not pass by skipping.

        [maat 2026-09-28] Enumeration moved into a fresh interpreter. This
        used to import `mcp_servers.omega_hub.server` in-process, and that is
        not reproducible inside a pytest session: `tests/test_hivemind.py`
        installs a fake `mcp` package at COLLECTION time, and because
        `server.py` <-> `hub_tools/tools.py` import each other, whichever module
        is imported first wins the binding. Depending on that order the
        deprecated `library_search` either gets curated out (54) or survives
        (55) — and which one you got depended on file order in the run.

        That is the whole story of the long-standing "54 vs 55" discrepancy:
        the live hub was always correct at 54, and the 55 was this test's own
        import-order artifact. A subprocess removes the ordering question
        entirely instead of encoding today's order as an assumption.
        """
        import json as _json
        import subprocess
        import sys as _sys

        code = (
            "import anyio, json\n"
            "from mcp_servers.omega_hub.server import mcp\n"
            "async def _l():\n"
            "    return sorted(t.name for t in await mcp.list_tools())\n"
            # anyio.run() takes the async FUNCTION here, not a pre-made
            # coroutine. Both were tried; passing _l() raises
            # "TypeError: 'coroutine' object is not callable" in this env.
            "print('SURFACE:' + json.dumps(anyio.run(_l)))\n"
        )

        proc = subprocess.run(
            [_sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
            timeout=120,
        )
        line = next(
            (ln for ln in proc.stdout.splitlines() if ln.startswith("SURFACE:")),
            None,
        )
        assert line, (
            "could not enumerate the tool surface in a clean interpreter — "
            f"stdout={proc.stdout[-800:]!r} stderr={proc.stderr[-800:]!r}"
        )
        names = _json.loads(line.split("SURFACE:", 1)[1])

        # M23: refuse to assert against a truncated surface. If the registry
        # ever returns a partial list, every absence assertion below becomes
        # vacuously true, which is exactly the bug being fixed.
        assert len(names) >= 50, (
            f"registered tool surface looks truncated: {len(names)} tools. "
            "Assertions over this list would be vacuous — refusing to assert."
        )
        return names

    def test_registered_surface_is_complete(self, registered_tools):
        """The enumeration must be the real surface, not a sample."""
        assert len(registered_tools) == len(set(registered_tools)), (
            "duplicate tool names in the registry"
        )
        # Cross-check against the running hub's own count. A mismatch means
        # the in-process registry and the served surface have diverged.
        try:
            import httpx2 as _httpx

            with _httpx.Client(base_url=HUB_BASE, timeout=5.0) as c:
                served = c.get("/debug/tools").json()["tool_manager_count"]
        except Exception as e:  # hub not running — in-process check stands alone
            pytest.skip(f"hub not reachable for count cross-check: {e}")

        assert served == len(registered_tools), (
            f"in-process registry has {len(registered_tools)} tools but the "
            f"running hub reports {served} — assertions would be against a "
            "surface that callers cannot reach"
        )

    @pytest.mark.parametrize("tool_name", EXPECTED_HIVEMIND_TOOLS + EXPECTED_CORE_TOOLS)
    def test_critical_tool_registered(self, registered_tools, tool_name):
        """Each critical tool must be in the COMPLETE registered surface.

        No skip path. If the tool is absent the test FAILS — a missing tool
        is a defect, not an environmental condition.
        """
        assert tool_name in registered_tools, (
            f"{tool_name} is not in the registered MCP surface "
            f"({len(registered_tools)} tools). Either it was removed without "
            "updating this list, or the hub failed to register it."
        )

    @pytest.mark.parametrize("tool_name", RETIRED_HIVEMIND_TOOLS)
    def test_retired_tool_absent(self, registered_tools, tool_name):
        """Consolidated-away names must NOT be in the served surface.

        This is the assertion that would have caught the consolidation at
        the moment it happened, when `hivemind_post_context` stopped being
        servable while callers still invoked it.
        """
        assert tool_name not in registered_tools, (
            f"{tool_name} was retired by the Hivemind consolidation but is "
            "back in the registered surface. Either the shim and the real "
            "tool have diverged, or the tool was resurrected without "
            "updating the callers."
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
