# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for HeadroomMiddleware — Sovereign Semantic Compression (Phases 1-3).

Validates the Omega-side contract with headroom-ai v0.45.0+: neutral tokenizer
resolution, context_window passthrough, real metrics, budget gate, entity
profiles, offline enforcement and the local CCR store. No network, no PyTorch.
"""

import os
from types import SimpleNamespace

import pytest

import headroom
from src.omega.oracle.middleware.headroom import (
    HeadroomMiddleware,
    HeadroomResult,
    NEUTRAL_TOKENIZER_MODEL,
)


def _fake_registry(model="opencode/big-pickle"):
    return SimpleNamespace(get=lambda name: SimpleNamespace(model=model, context_window=4096))


@pytest.mark.anyio
async def test_headroom_passthrough():
    """Middleware returns one metadata record per message (budget gate may skip)."""
    middleware = HeadroomMiddleware()
    long_text = (
        "The Omega Engine is a sovereign AI runtime. "
        "It uses a local-first approach to inference. "
        "It implements the 22 Sovereign Mandates. "
    ) * 5
    messages = [{"role": "user", "content": long_text}]

    compressed, results = await middleware.compress_context("test_entity", messages)

    assert len(compressed) == len(messages)
    assert len(results) == len(compressed), "Should return result metadata per message"
    for r in results:
        assert isinstance(r, HeadroomResult)
        assert isinstance(r.compressed_text, str)
        assert r.summary is not None
        assert r.summary.model == NEUTRAL_TOKENIZER_MODEL


@pytest.mark.anyio
async def test_headroom_retrieval_error_handling():
    """Missing references are reported, never raise."""
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


def test_resolve_headroom_model_uses_neutral_estimator():
    """opencode/big-pickle is a provider alias -> neutral model, no HF download."""
    mw = HeadroomMiddleware(entity_registry=_fake_registry())
    assert mw.resolve_headroom_model("iris") == NEUTRAL_TOKENIZER_MODEL
    # cached
    assert mw.resolve_headroom_model("iris") == NEUTRAL_TOKENIZER_MODEL


def test_offline_env_enforced():
    """HEADROOM_OFFLINE=1 is set for air-gap operation (M8)."""
    HeadroomMiddleware()
    assert os.environ.get("HEADROOM_OFFLINE") == "1"


def test_entity_profile_mapping():
    """Log-analysis entities get user-message compression in lossless agent mode."""
    mw = HeadroomMiddleware()
    log_profile = mw._profile_for("lilith")
    assert log_profile["compress_user_messages"] is True
    assert log_profile["mode"] == "agent"
    research_profile = mw._profile_for("researcher_humboldt")
    assert research_profile["min_tokens_to_compress"] == 400
    default_profile = mw._profile_for("unknown_entity")
    assert default_profile["compress_user_messages"] is False


@pytest.mark.anyio
async def test_budget_gate_skips_short_context(monkeypatch):
    """Under 70% of model_limit -> no compression call at all."""
    called = []

    def _boom(*args, **kwargs):
        called.append(kwargs)
        raise AssertionError("compress() must not be called under budget")

    monkeypatch.setattr(headroom, "compress", _boom)
    mw = HeadroomMiddleware()
    messages = [{"role": "user", "content": "short"}]
    compressed, results = await mw.compress_context("iris", messages, context_window=8192)

    assert compressed == messages
    assert called == []
    assert results[0].summary.skipped_reason == "under_budget"
    assert mw.get_compression_stats()["totals"]["skipped"] == 1


@pytest.mark.anyio
async def test_model_limit_and_real_metrics(monkeypatch):
    """context_window is passed as model_limit; CompressResult metrics are captured."""
    captured = {}

    def _fake_compress(messages, **kwargs):
        captured.update(kwargs)
        return headroom.CompressResult(
            messages=[{"role": "tool", "content": '{"rows":[1,2,3]}'}],
            tokens_before=900,
            tokens_after=300,
            tokens_saved=600,
            compression_ratio=0.6667,
            transforms_applied=["smart_crusher:json"],
            lossless=True,
            reverted_messages=0,
        )

    monkeypatch.setattr(headroom, "compress", _fake_compress)
    mw = HeadroomMiddleware(entity_registry=_fake_registry())
    # Large enough to exceed the 70% budget gate at model_limit=4096.
    messages = [{"role": "tool", "content": '{"rows":[1,2,3,4,5,6]}' + " " + "x" * 12000}]
    compressed, results = await mw.compress_context(
        "john_carmack", messages, context_window=4096, session_id="ses_test"
    )

    assert captured["model_limit"] == 4096
    assert captured["model"] == NEUTRAL_TOKENIZER_MODEL
    assert captured["config"].mode == "agent"
    assert captured["config"].protect_recent == 6, "code_agent profile applied"

    summary = results[0].summary
    assert summary.tokens_saved == 600, "real CompressResult metric, not hardcoded 0"
    assert summary.tokens_before == 900 and summary.tokens_after == 300
    assert summary.compression_ratio == pytest.approx(0.6667)
    assert summary.transforms_applied == ["smart_crusher:json"]
    assert summary.compressed is True
    assert compressed[0]["content"] == '{"rows":[1,2,3]}'


@pytest.mark.anyio
async def test_ccr_store_roundtrip_and_expiry(monkeypatch):
    """Changed messages get a ref retrievable within TTL, expired after."""
    captured = {}

    def _fake_compress(messages, **kwargs):
        return headroom.CompressResult(
            messages=[{"role": "user", "content": "compressed"}],
            tokens_before=900, tokens_after=300, tokens_saved=600,
            transforms_applied=["test"], lossless=True,
        )

    monkeypatch.setattr(headroom, "compress", _fake_compress)
    mw = HeadroomMiddleware()
    mw._settings.ttl_seconds = 0.01
    original = "original long text " + "y" * 2000
    _, results = await mw.compress_context(
        "lilith", [{"role": "user", "content": original}],
        context_window=512, session_id="ses_ccr"
    )
    ref = results[0].original_ref
    assert ref is not None and ref.startswith("ccr:")
    assert await mw.retrieve_original(ref) == original

    import anyio
    await anyio.sleep(0.02)
    assert "expired" in await mw.retrieve_original(ref)


@pytest.mark.anyio
async def test_stats_accumulate(monkeypatch):
    """Per-call summaries aggregate into per-entity and total stats."""
    def _fake_compress(messages, **kwargs):
        return headroom.CompressResult(
            messages=list(messages), tokens_before=500, tokens_after=400,
            tokens_saved=100, compression_ratio=0.2, lossless=True,
        )

    monkeypatch.setattr(headroom, "compress", _fake_compress)
    mw = HeadroomMiddleware()
    for _ in range(3):
        await mw.compress_context(
            "iris", [{"role": "tool", "content": "x" * 2000}],
            context_window=512, session_id="ses_stats"
        )
    stats = mw.get_compression_stats()
    assert stats["per_entity"]["iris"]["calls"] == 3
    assert stats["totals"]["tokens_saved"] == 300
    assert stats["totals"]["compressed"] == 3


@pytest.mark.anyio
async def test_compression_failure_is_fail_open(monkeypatch):
    """M23: a broken compressor returns originals with an 'error' summary."""
    def _boom(*args, **kwargs):
        raise RuntimeError("headroom exploded")

    monkeypatch.setattr(headroom, "compress", _boom)
    mw = HeadroomMiddleware()
    messages = [{"role": "tool", "content": "x" * 2000}]
    compressed, results = await mw.compress_context(
        "iris", messages, context_window=512
    )
    assert compressed == messages
    assert results == []
    assert mw.get_compression_stats()["totals"]["errors"] == 1
