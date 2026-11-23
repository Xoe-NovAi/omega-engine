# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""End-to-end Headroom integration tests (Phase 4).

Uses the REAL headroom-ai library with the neutral estimator backend:
no network, no PyTorch, HEADROOM_OFFLINE=1.
"""

import json
import os
from types import SimpleNamespace

import pytest

from src.omega.oracle.context_builder import ContextBuilder
from src.omega.oracle.middleware.headroom import (
    HeadroomMiddleware,
    NEUTRAL_TOKENIZER_MODEL,
)


def _repetitive_tool_output() -> str:
    """JSON tool payload with heavy repetition — SmartCrusher territory."""
    return json.dumps(
        [
            {"id": i, "level": "INFO", "msg": "connection established", "host": "node-01"}
            for i in range(120)
        ]
    )


@pytest.mark.anyio
async def test_end_to_end_real_compression_and_ccr():
    """Real compression saves tokens losslessly and keeps originals retrievable."""
    mw = HeadroomMiddleware()
    assert os.environ.get("HEADROOM_OFFLINE") == "1"

    messages = [{"role": "tool", "content": _repetitive_tool_output()}]
    compressed, results = await mw.compress_context(
        "lilith", messages, context_window=1024, session_id="ses_integration"
    )

    assert len(compressed) == 1
    summary = results[0].summary
    assert summary.compressed is True
    assert summary.model == NEUTRAL_TOKENIZER_MODEL
    assert summary.model_limit == 1024
    assert summary.tokens_saved > 0, f"expected real savings, got {summary}"
    assert summary.lossless is True
    assert any("smart_crusher" in t for t in summary.transforms_applied)

    ref = results[0].original_ref
    assert ref is not None
    assert await mw.retrieve_original(ref) == messages[0]["content"]


@pytest.mark.anyio
async def test_context_builder_passes_entity_context_window(monkeypatch):
    """Phase 1.2 wiring: build_context forwards entity.context_window + session_id."""
    captured = {}

    async def _fake_compress(entity_name, messages, context_window=None, session_id=""):
        captured.update(
            entity=entity_name, context_window=context_window, session_id=session_id
        )
        return messages, []

    monkeypatch.setattr(
        "src.omega.oracle.context_builder.get_headroom_middleware",
        lambda: SimpleNamespace(compress_context=_fake_compress),
    )

    registry = SimpleNamespace(
        get=lambda name: SimpleNamespace(model="opencode/big-pickle", context_window=16384)
    )
    builder = ContextBuilder(entity_registry=registry)
    exchanges = [
        {"user": "Where is the observability stack?", "assistant": "On node 0.",
         "timestamp": "2026-11-23T00:00:00Z"}
    ]
    await builder._compact_and_format_exchanges(
        "sophia", exchanges, token_limit=4000, session_id="ses_ctx"
    )

    assert captured["entity"] == "sophia"
    assert captured["context_window"] == 16384
    assert captured["session_id"] == "ses_ctx"
