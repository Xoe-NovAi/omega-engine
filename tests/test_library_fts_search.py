# ⬡ OMEGA ⬡ P4 ⬡ LIBRARY-FTS ⬡ MCP-TOOL-LAYER ⬡ TESTS
"""Tests for the library_fts_search MCP tool.

AP Token: AP-LIBRARY-FTS-TEST-v1.0.0

Verifies:
- library_fts_search calls Library.search() and returns formatted results
- Empty query returns error
- Query exceeding 500 chars returns error
- Domain parameter is forwarded to Library.search()
- Library exceptions are caught and returned as JSON errors
- Summary truncation at 300 chars
"""

import json
import re
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional

from mcp_servers.omega_hub import state as _state
from mcp_servers.omega_hub.hub_tools import tools as tools_mod


# ── CuratedDocument stub (mirrors omega.library.curator.CuratedDocument) ──

@dataclass
class _StubDocument:
    doc_id: str = "test-doc-001"
    source: str = "https://example.com/test"
    source_type: str = "url"
    title: str = "Test Document"
    body: str = "Test body content"
    summary: str = "Test summary for the document"
    domain: str = "testing"
    quality_score: float = 0.85
    author: Optional[str] = None
    tags: List[str] = field(default_factory=lambda: ["test", "example"])
    word_count: int = 1200
    curated_at: str = "2026-07-04T00:00:00+00:00"
    metadata: dict = field(default_factory=dict)


def _extract_json_from_tdp(tdp_output: str) -> dict:
    """Extract JSON from a TDP-wrapped response string.
    
    TDP wraps tool output in:
        ### [EXTERNAL DATA START]
        Source: ...
        Taint Level: ...
        ---
        {json_content}
        ### [EXTERNAL DATA END]
    """
    match = re.search(r"---\n(.*?)\n### \[EXTERNAL DATA END\]", tdp_output, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # If no TDP markers, try parsing directly
    return json.loads(tdp_output)


def _patch_library(mock_library):
    """Set _state.library to a mock so ServiceProxy resolves it correctly."""
    original = _state.library
    _state.library = mock_library
    return original


def _restore_library(original):
    """Restore the original _state.library value."""
    _state.library = original


# ── Tests ──

class TestLibraryFtsSearch:
    """Unit tests for library_fts_search tool function."""

    @pytest.mark.anyio
    async def test_empty_query_returns_error(self):
        """Empty query string should return JSON error, not call Library.search."""

        with patch.object(tools_mod, "_require_service"):
            result = await tools_mod.library_fts_search(query="   ", domain="", limit=10)
            parsed = _extract_json_from_tdp(result)
            assert parsed["error"] == "Search query cannot be empty"
            assert parsed["count"] == 0
            assert parsed["results"] == []

    @pytest.mark.anyio
    async def test_query_exceeding_500_chars_returns_error(self):
        """Query over 500 chars should return JSON error."""

        with patch.object(tools_mod, "_require_service"):
            long_query = "a" * 501
            result = await tools_mod.library_fts_search(query=long_query, domain="", limit=10)
            parsed = _extract_json_from_tdp(result)
            assert parsed["error"] == "Query exceeds 500-char limit"
            assert parsed["count"] == 0
            assert parsed["results"] == []

    @pytest.mark.anyio
    async def test_search_returns_formatted_results(self):
        """Valid query should call Library.search() and format results."""

        stub_docs = [
            _StubDocument(
                doc_id="warp-001",
                title="Warp Proxy Pool Architecture",
                summary="Deep dive into connection pooling for warp proxies",
                domain="networking",
                quality_score=0.92,
                tags=["warp", "proxy", "pooling"],
                word_count=3400,
            ),
        ]

        mock_library = MagicMock()
        mock_library.search = AsyncMock(return_value=stub_docs)
        orig = _patch_library(mock_library)

        try:
            with patch.object(tools_mod, "_require_service"):
                result = await tools_mod.library_fts_search(
                    query="warp proxy pool", domain="networking", limit=10
                )
                parsed = _extract_json_from_tdp(result)

                assert parsed["query"] == "warp proxy pool"
                assert parsed["count"] == 1
                assert parsed["source"] == "library_fts5"
                assert len(parsed["results"]) == 1

                doc_result = parsed["results"][0]
                assert doc_result["doc_id"] == "warp-001"
                assert doc_result["title"] == "Warp Proxy Pool Architecture"
                assert doc_result["domain"] == "networking"
                assert doc_result["quality_score"] == 0.92
                assert "warp" in doc_result["tags"]

                # Verify Library.search was called with correct args
                mock_library.search.assert_awaited_once_with(
                    "warp proxy pool", domain="networking", limit=10
                )
        finally:
            _restore_library(orig)

    @pytest.mark.anyio
    async def test_search_with_empty_domain_passes_none(self):
        """Empty domain string should be converted to None for Library.search()."""

        mock_library = MagicMock()
        mock_library.search = AsyncMock(return_value=[])
        orig = _patch_library(mock_library)

        try:
            with patch.object(tools_mod, "_require_service"):
                result = await tools_mod.library_fts_search(
                    query="test query", domain="", limit=5
                )
                parsed = _extract_json_from_tdp(result)

                assert parsed["count"] == 0
                assert parsed["results"] == []
                mock_library.search.assert_awaited_once_with(
                    "test query", domain=None, limit=5
                )
        finally:
            _restore_library(orig)

    @pytest.mark.anyio
    async def test_library_exception_returns_error_json(self):
        """Library.search() exception should be caught and returned as JSON error."""

        mock_library = MagicMock()
        mock_library.search = AsyncMock(side_effect=RuntimeError("FTS5 index not initialized"))
        orig = _patch_library(mock_library)

        try:
            with patch.object(tools_mod, "_require_service"):
                result = await tools_mod.library_fts_search(
                    query="anything", domain="", limit=10
                )
                parsed = _extract_json_from_tdp(result)

                assert "error" in parsed
                assert "FTS5 index not initialized" in parsed["error"]
                assert parsed["count"] == 0
                assert parsed["results"] == []
        finally:
            _restore_library(orig)

    @pytest.mark.anyio
    async def test_summary_truncated_to_300_chars(self):
        """Document summaries longer than 300 chars should be truncated."""

        long_summary = "x" * 500
        stub_doc = _StubDocument(summary=long_summary)

        mock_library = MagicMock()
        mock_library.search = AsyncMock(return_value=[stub_doc])
        orig = _patch_library(mock_library)

        try:
            with patch.object(tools_mod, "_require_service"):
                result = await tools_mod.library_fts_search(
                    query="test", domain="", limit=10
                )
                parsed = _extract_json_from_tdp(result)

                assert len(parsed["results"][0]["summary"]) == 300
        finally:
            _restore_library(orig)


class TestLibraryFtsSearchIntegration:
    """Verify the tool is properly registered in the MCP tool set."""

    def test_tool_function_exists_and_is_async(self):
        """library_fts_search should be defined and be a coroutine function."""
        fn = getattr(tools_mod, "library_fts_search", None)
        assert fn is not None, "library_fts_search not found in tools module"
        import inspect
        assert inspect.iscoroutinefunction(fn), "library_fts_search must be async"

    def test_tool_has_correct_signature(self):
        """library_fts_search should accept query, domain, limit params."""
        import inspect
        sig = inspect.signature(tools_mod.library_fts_search)
        params = list(sig.parameters.keys())
        assert "query" in params
        assert "domain" in params
        assert "limit" in params

    @pytest.mark.anyio
    async def test_results_include_source_fts5_marker(self):
        """Results JSON should include source=library_fts5 to distinguish from web search."""

        mock_library = MagicMock()
        mock_library.search = AsyncMock(return_value=[])
        orig = _patch_library(mock_library)

        try:
            with patch.object(tools_mod, "_require_service"):
                result = await tools_mod.library_fts_search(
                    query="anything", domain="", limit=10
                )
                parsed = _extract_json_from_tdp(result)
                assert parsed["source"] == "library_fts5"
        finally:
            _restore_library(orig)
