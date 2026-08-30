# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for HeadroomMiddleware — Sovereign Semantic Compression.

Tests validate integration contract with the headroom library.
Actual compression depends on headroom configuration (API keys, models).
"""

import pytest
from src.omega.oracle.middleware.headroom import HeadroomMiddleware, HeadroomResult


@pytest.mark.anyio
async def test_headroom_passthrough():
    """Middleware returns messages via headroom library (may be unchanged without config)."""
    middleware = HeadroomMiddleware()

    long_text = (
        "The Omega Engine is a sovereign AI runtime. "
        "It uses a local-first approach to inference. "
        "It implements the 22 Sovereign Mandates. "
    ) * 5

    messages = [
        {"role": "user", "content": long_text},
    ]

    compressed, results = await middleware.compress_context("test_entity", messages)

    # Should maintain the count of messages
    assert len(compressed) == len(messages)

    # Should return a result metadata object for each message
    assert len(results) == len(compressed), "Should return result metadata per message"
    for r in results:
        assert isinstance(r, HeadroomResult)
        assert isinstance(r.compressed_text, str)


@pytest.mark.anyio
async def test_headroom_retrieval_error_handling():
    """Middleware handles missing references gracefully."""
    middleware = HeadroomMiddleware()

    result = await middleware.retrieve_original("non_existent_ref_123")

    assert isinstance(result, str)
    assert "ERROR" in result or "could not be retrieved" in result


@pytest.mark.anyio
async def test_headroom_empty_messages():
    """Middleware handles empty message lists."""
    middleware = HeadroomMiddleware()
    compressed, results = await middleware.compress_context("test_entity", [])

    assert compressed == []
    assert results == []
