# ⬡ OMEGA ⬡ MA'AT ⬡ BIG-PICKLE ⬡ TDP-INTEGRATION ⬡ PHASE-II
"""Integration tests for the Tainted Data Protocol (TDP) decorator on MCP tools.

AP Token: AP-TDP-TEST-v1.0.0

Tests the @tdp_wrap decorator's behavior across:
- String return wrapping with isolation gates
- Non-string passthrough
- Domain-based taint level determination
- Error handling for callable taint_level
- Integration with security module's determine_url_taint

See: data/handoff/active/ho_d84be1be4392 (S2-A TDP Wiring)
"""

import pytest
from omega.oracle.security import tdp_wrap, TaintedData, TDPGate, determine_url_taint


# ── Basic String Wrapping Tests ──────────────────────────────────────

@pytest.mark.anyio
async def test_tdp_wrap_string_level_1():
    """String output wrapped with Taint Level 1 isolation gate."""
    @tdp_wrap(source="test_tool", taint_level=1)
    async def mock_tool() -> str:
        return "trusted internal data"

    result = await mock_tool()

    assert "### [EXTERNAL DATA START]" in result
    assert "Source: test_tool" in result
    assert "Taint Level: 1" in result
    assert "trusted internal data" in result
    assert "### [EXTERNAL DATA END]" in result


@pytest.mark.anyio
async def test_tdp_wrap_string_level_2():
    """String output wrapped with Taint Level 2 isolation gate."""
    @tdp_wrap(source="external_api", taint_level=2)
    async def mock_tool() -> str:
        return "untrusted external data"

    result = await mock_tool()

    assert "Taint Level: 2" in result
    assert "untrusted external data" in result


@pytest.mark.anyio
async def test_tdp_wrap_string_level_3():
    """String output wrapped with Taint Level 3 (maximum risk) isolation gate."""
    @tdp_wrap(source="unknown_source", taint_level=3)
    async def mock_tool() -> str:
        return "highly untrusted data"

    result = await mock_tool()

    assert "Taint Level: 3" in result
    assert "highly untrusted data" in result


# ── Non-String Passthrough Tests ─────────────────────────────────────

@pytest.mark.anyio
async def test_tdp_wrap_dict_passthrough():
    """Non-string returns pass through unwrapped."""
    @tdp_wrap(source="test_tool")
    async def mock_tool() -> dict:
        return {"status": "ok", "count": 42}

    result = await mock_tool()
    assert result == {"status": "ok", "count": 42}


@pytest.mark.anyio
async def test_tdp_wrap_list_passthrough():
    """List returns pass through unwrapped."""
    @tdp_wrap(source="test_tool")
    async def mock_tool() -> list:
        return ["a", "b", "c"]

    result = await mock_tool()
    assert result == ["a", "b", "c"]


@pytest.mark.anyio
async def test_tdp_wrap_none_passthrough():
    """None returns pass through unwrapped."""
    @tdp_wrap(source="test_tool")
    async def mock_tool() -> None:
        return None

    result = await mock_tool()
    assert result is None


@pytest.mark.anyio
async def test_tdp_wrap_int_passthrough():
    """Integer returns pass through unwrapped."""
    @tdp_wrap(source="test_tool")
    async def mock_tool() -> int:
        return 42

    result = await mock_tool()
    assert result == 42


# ── Callable Taint Level Tests ───────────────────────────────────────

def _dynamic_taint(url: str = "", **kwargs) -> int:
    """Determine taint level based on URL domain."""
    if not url:
        return 1
    trusted = ["localhost", "127.0.0.1", "github.com"]
    if any(d in url for d in trusted):
        return 1
    return 2


@pytest.mark.anyio
async def test_tdp_wrap_callable_taint_trusted():
    """Callable taint_level returns 1 for trusted domains."""
    @tdp_wrap(source="inbox", taint_level=_dynamic_taint)
    async def add_url(url: str = "") -> str:
        return f"Added URL: {url}"

    result = await add_url(url="https://github.com/Xoe-NovAi/omega-engine")
    assert "Taint Level: 1" in result


@pytest.mark.anyio
async def test_tdp_wrap_callable_taint_untrusted():
    """Callable taint_level returns 2 for untrusted domains."""
    @tdp_wrap(source="inbox", taint_level=_dynamic_taint)
    async def add_url(url: str = "") -> str:
        return f"Added URL: {url}"

    result = await add_url(url="https://evil.com/malware")
    assert "Taint Level: 2" in result


@pytest.mark.anyio
async def test_tdp_wrap_callable_taint_empty():
    """Callable taint_level returns 1 for empty URL (based on custom logic)."""
    @tdp_wrap(source="inbox", taint_level=_dynamic_taint)
    async def add_url(url: str = "") -> str:
        return f"Added URL: {url}"

    result = await add_url(url="")
    # _dynamic_taint returns 1 for empty URLs (our test logic says empty=internal)
    assert "Taint Level: 1" in result


# ── determine_url_taint Integration Tests ────────────────────────────

@pytest.mark.anyio
async def test_determine_url_taint_localhost():
    """determine_url_taint returns 1 for localhost URLs."""
    @tdp_wrap(source="inbox", taint_level=determine_url_taint)
    async def add_url(url: str) -> str:
        return f"Added URL: {url}"

    result = await add_url(url="http://localhost:8016/config")
    assert "Taint Level: 1" in result


@pytest.mark.anyio
async def test_determine_url_taint_github_trusted():
    """determine_url_taint returns 1 for Xoe-NovAi GitHub URLs."""
    @tdp_wrap(source="inbox", taint_level=determine_url_taint)
    async def add_url(url: str) -> str:
        return f"Added URL: {url}"

    result = await add_url(url="https://github.com/Xoe-NovAi/omega-engine/blob/main/README.md")
    assert "Taint Level: 1" in result


@pytest.mark.anyio
async def test_determine_url_taint_external():
    """determine_url_taint returns 2 for external URLs."""
    @tdp_wrap(source="inbox", taint_level=determine_url_taint)
    async def add_url(url: str) -> str:
        return f"Added URL: {url}"

    result = await add_url(url="https://example.com/page")
    assert "Taint Level: 2" in result


@pytest.mark.anyio
async def test_determine_url_taint_empty():
    """determine_url_taint returns 2 for empty URL (no URL = untrusted)."""
    @tdp_wrap(source="inbox", taint_level=determine_url_taint)
    async def add_url(url: str) -> str:
        return f"Added URL: {url}"

    result = await add_url(url="")
    assert "Taint Level: 2" in result


# ── Multiple Decorator Stacking Tests ────────────────────────────────

@pytest.mark.anyio
async def test_tdp_wrap_multiple_calls():
    """Multiple calls to same decorated function produce independent wraps."""
    call_count = 0

    @tdp_wrap(source="counter", taint_level=1)
    async def increment() -> str:
        nonlocal call_count
        call_count += 1
        return f"Count: {call_count}"

    r1 = await increment()
    r2 = await increment()

    assert "Count: 1" in r1
    assert "Count: 2" in r2
    assert "### [EXTERNAL DATA START]" in r1
    assert "### [EXTERNAL DATA START]" in r2


# ── Error Recovery Tests ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_tdp_wrap_callable_taint_raises():
    """When taint_level callable raises, falls back to level 2."""
    def broken_taint(**kwargs):
        raise ValueError("Intentional failure for testing")

    @tdp_wrap(source="broken_source", taint_level=broken_taint)
    async def mock_tool() -> str:
        return "data from broken source"

    result = await mock_tool()
    # Should still produce an isolation gate with fallback level 2
    assert "### [EXTERNAL DATA START]" in result
    assert "Taint Level: 2" in result
    assert "data from broken source" in result
