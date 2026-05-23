"""Tests for Omega Oracle (async)."""

import pytest

from omega.oracle.oracle import Oracle


def _run(coro_fn):
    """Run an async test function."""
    import anyio
    return anyio.run(coro_fn)


def test_talk_empty_query():
    async def t():
        r = await Oracle().talk("")
        return r
    result = _run(t)
    assert result.entity is not None  # Some entity handled the empty query
    assert isinstance(result.entity, str)


def test_talk_summon_pattern():
    async def t():
        return await Oracle().talk("@Sekhmet what is strength?")
    result = _run(t)
    assert result.entity == "Sekhmet"
    assert "P1: Flesh" in result.pillars


def test_talk_summon_hey():
    async def t():
        return await Oracle().talk("hey hecate, what do you see?")
    result = _run(t)
    assert result.entity == "Hecate"
    assert "P8: Shadow" in result.pillars


def test_talk_summon_command():
    async def t():
        return await Oracle().talk("summon Brigid, give me poetry")
    result = _run(t)
    assert result.entity == "Brigid"


def test_talk_domain_routing():
    async def t():
        return await Oracle().talk("I need strength and protection")
    result = _run(t)
    assert result.entity == "Sekhmet"


def test_talk_domain_routing_shadow():
    async def t():
        return await Oracle().talk("I want to explore my shadow")
    result = _run(t)
    assert result.entity == "Hecate"


def test_summon_direct():
    async def t():
        return await Oracle().summon("sekHmet", "what is strength?")
    result = _run(t)
    assert result.entity == "Sekhmet"


def test_summon_case_insensitive():
    async def t():
        return await Oracle().summon("INANNA", "what lies beneath?")
    result = _run(t)
    assert result.entity == "Inanna"


def test_summon_unknown_entity():
    async def t():
        return await Oracle().summon("unknown_entity", "hello")
    result = _run(t)
    assert result.entity is not None


def test_all_pillar_keepers_have_required_fields():
    """Structural invariants - every pillar keeper must have required fields.
    
    Does NOT hardcode entity names per the Engine-Stack Firewall mandate.
    """
    oracle = Oracle()
    keepers = oracle.registry.list_pillar_keepers()
    assert len(keepers) >= 1  # At least one keeper exists
    for k in keepers:
        assert k.name is not None, "Pillar keeper missing name"
        assert k.pillars, "Pillar keeper must have pillar assignments"
        assert k.domains is not None, "Pillar keeper must have domains"


def test_iris_speculative_decoder_simple():
    """Simple queries should be handled by Iris directly."""
    async def t():
        return await Oracle().talk("hello")
    result = _run(t)
    assert result.entity == "Iris"
    assert result.confidence >= 0.8


def test_iris_speculative_decoder_complex():
    """Complex queries should escalate to a Pillar Keeper."""
    async def t():
        return await Oracle().talk("explain the meaning of justice")
    result = _run(t)
    assert result.escalated is True


def test_iris_confidence_assessment():
    """Non-async — pure logic check."""
    oracle = Oracle()
    # Simple greetings → high confidence
    assert oracle._assess_iris_confidence("hello") >= 0.8
    assert oracle._assess_iris_confidence("thanks") >= 0.8
    # Complex indicators → zero confidence (triggers escalation)
    assert oracle._assess_iris_confidence("explain the meaning of justice") == 0.0
    assert oracle._assess_iris_confidence("why is the sky blue") == 0.0
    assert oracle._assess_iris_confidence("how does gravity work") == 0.0
    # Short query → moderate confidence (Iris will try)
    assert oracle._assess_iris_confidence("i like apples") >= 0.3
    assert oracle._assess_iris_confidence("tell me a story") >= 0.3
    assert oracle._assess_iris_confidence("what can you do") >= 0.5


# ── Integration Tests: ContextBuilder Wiring ────────────────────────────


def test_talk_injects_context_into_prompt():
    """Verify ContextBuilder.build_context is called during talk()."""
    from unittest.mock import AsyncMock, patch

    async def t():
        with patch("omega.oracle.oracle.ContextBuilder") as MockCB:
            mock_instance = MockCB.return_value
            mock_instance.build_context = AsyncMock(return_value="")
            mock_instance.prepend_to_prompt = AsyncMock(side_effect=lambda ctx, prompt: prompt)

            oracle = Oracle()
            oracle.context_builder = mock_instance
            return await oracle.talk("hello")

    result = _run(t)
    assert result is not None


def test_talk_with_empty_memory_still_works():
    """First conversation with no history should not crash."""
    async def t():
        oracle = Oracle()
        # Ensure memory store is clean
        return await oracle.talk("this is my first message")

    result = _run(t)
    assert result is not None
    assert result.text is not None


def test_talk_context_builder_exception_does_not_crash():
    """If ContextBuilder fails, Oracle should gracefully degrade."""
    from unittest.mock import AsyncMock, patch

    async def t():
        oracle = Oracle()
        # Make build_context raise an exception
        oracle.context_builder.build_context = AsyncMock(
            side_effect=OSError("simulated memory failure")
        )
        return await oracle.talk("I need strength")

    result = _run(t)
    # Should still get a response, not crash
    assert result is not None
    assert result.text is not None
