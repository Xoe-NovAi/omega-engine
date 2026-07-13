# 🔱 Omega Engine — Qdrant Payload Index Contract Tests (GAP 6 / A1·2)
# ⬡ OMEGA ⬡ MA'AT ⬡ P2 ⬡ 2026-07-12
#
# [M21: Gate Integrity] Every new function gets a contract test that validates
# its return type via isinstance(). These tests verify ensure_payload_indexes()
# creates KEYWORD payload indexes for entity_name and session_id, and is
# idempotent across restarts.

import inspect
from unittest.mock import MagicMock

import anyio
import pytest
from qdrant_client.models import PayloadSchemaType

from omega.memory.vector_adapters import QdrantAdapter


def _run(coro_fn):
    """Run an async test coroutine (same pattern as test_contract_m21.py)."""
    return anyio.run(coro_fn)


def test_ensure_payload_indexes_is_callable():
    """M21: QdrantAdapter.ensure_payload_indexes exists and is a coroutine fn."""
    assert hasattr(QdrantAdapter, "ensure_payload_indexes"), (
        "QdrantAdapter must expose ensure_payload_indexes()"
    )
    assert inspect.iscoroutinefunction(QdrantAdapter.ensure_payload_indexes), (
        "ensure_payload_indexes must be async (AnyIO)"
    )


def test_ensure_payload_indexes_creates_keyword_indexes():
    """M21: calling it creates entity_name + session_id KEYWORD payload indexes."""
    async def t():
        adapter = QdrantAdapter(collection_name="test_payload_idx")
        # Replace the real client with a mock so no network call occurs
        adapter.client = MagicMock()
        adapter.client.create_payload_index = MagicMock()

        result = await adapter.ensure_payload_indexes()

        # M21: return type is None
        assert result is None, f"Expected None, got {type(result).__name__}"

        # Both indexes requested exactly once
        assert adapter.client.create_payload_index.call_count == 2, (
            f"Expected 2 create_payload_index calls, got {adapter.client.create_payload_index.call_count}"
        )
        calls = {
            c.kwargs["field_name"]: c.kwargs["field_schema"]
            for c in adapter.client.create_payload_index.call_args_list
        }
        assert "entity_name" in calls, f"entity_name index missing: {calls}"
        assert "session_id" in calls, f"session_id index missing: {calls}"
        # KEYWORD schema (qdrant-2021 payload index type)
        assert calls["entity_name"] == PayloadSchemaType.KEYWORD, (
            f"entity_name schema must be KEYWORD, got {calls['entity_name']}"
        )
        assert calls["session_id"] == PayloadSchemaType.KEYWORD, (
            f"session_id schema must be KEYWORD, got {calls['session_id']}"
        )
        return True

    assert _run(t) is True


def test_ensure_payload_indexes_idempotent_on_already_exists():
    """M21: 'already exists' errors are swallowed (idempotent across restarts)."""
    async def t():
        adapter = QdrantAdapter(collection_name="test_payload_idx")
        adapter.client = MagicMock()

        def _raise_already_exists(*args, **kwargs):
            raise RuntimeError("Payload index already exists")

        adapter.client.create_payload_index = MagicMock(side_effect=_raise_already_exists)

        # Must NOT raise — idempotent-safe on restart
        result = await adapter.ensure_payload_indexes()
        assert result is None, f"Expected None on idempotent path, got {result!r}"
        return True

    assert _run(t) is True
