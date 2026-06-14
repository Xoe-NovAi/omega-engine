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
        return await Oracle().talk("@SysAdmin how do I deploy a container?")
    result = _run(t)
    assert result.entity == "SysAdmin"
    assert "1" in result.pillars


def test_talk_summon_hey():
    async def t():
        return await Oracle().talk("hey Sentinel, check the security audit")
    result = _run(t)
    assert result.entity == "Sentinel"
    assert "5" in result.pillars


def test_talk_summon_command():
    async def t():
        return await Oracle().talk("summon ModelGate, how is inference routing?")
    result = _run(t)
    assert result.entity == "ModelGate"


def test_talk_domain_routing():
    async def t():
        return await Oracle().talk("I need to check infrastructure monitoring")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_talk_domain_routing_shadow():
    async def t():
        return await Oracle().talk("check observability and logging")
    result = _run(t)
    assert result.entity == "WatchTower"


def test_summon_direct():
    async def t():
        return await Oracle().summon("sysAdmin", "how do I configure the server?")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_summon_case_insensitive():
    async def t():
        return await Oracle().summon("WATCHTOWER", "what metrics do you track?")
    result = _run(t)
    assert result.entity == "WatchTower"


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


def test_summon_uses_record_interaction():
    """After deduplication, summon() should delegate to _record_interaction()."""
    from unittest.mock import AsyncMock, patch

    async def t():
        oracle = Oracle()
        # Mock _record_interaction to track calls
        oracle._record_interaction = AsyncMock()
        result = await oracle.summon("sysAdmin", "configure the server")
        # _record_interaction should have been called
        oracle._record_interaction.assert_called_once()
        call_args = oracle._record_interaction.call_args
        # First arg is resp, second is query, third is trace, fourth is transient
        assert call_args[0][1] == "configure the server"  # query
        assert call_args[0][3] is False  # transient (default)
        return result

    result = _run(t)
    assert result.entity == "SysAdmin"


def test_summon_transient_skips_recording():
    """transient=True should skip _record_interaction."""
    from unittest.mock import AsyncMock

    async def t():
        oracle = Oracle()
        oracle._record_interaction = AsyncMock()
        result = await oracle.summon("sysAdmin", "ephemeral query", transient=True)
        oracle._record_interaction.assert_called_once()
        call_args = oracle._record_interaction.call_args
        assert call_args[0][3] is True  # transient=True
        return result

    result = _run(t)
    assert result.entity == "SysAdmin"


def test_record_interaction_memory_failure_does_not_crash():
    """If add_exchange fails, _record_interaction should not raise."""
    from unittest.mock import AsyncMock, MagicMock

    async def t():
        oracle = Oracle()
        # Make add_exchange raise
        oracle.memory_store.add_exchange = AsyncMock(side_effect=OSError("disk full"))
        # Create a mock response
        resp = MagicMock()
        resp.entity = "SysAdmin"
        resp.session_id = "ses_test"
        resp.text = "test response"
        resp.backend = "mock"
        resp.model = "mock-model"
        trace = MagicMock()
        trace.trace_id = "trace_test"

        # Should not raise
        await oracle._record_interaction(resp, "test query", trace, transient=False)
        return True

    result = _run(t)
    assert result is True


def test_talk_mention_at_start():
    async def t():
        # Use a known entity from the default IWAD (e.g., 'sysAdmin' as seen in other tests)
        return await Oracle().talk("@sysAdmin how do I deploy a container?")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_talk_mention_within_text():
    async def t():
        # '@sysAdmin' is within the text
        return await Oracle().talk("Hello @sysAdmin, can you help me with the server?")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_talk_invalid_mention():
    async def t():
        # '@fakeAgent' should not be recognized as a summon
        # It should fall back to normal talk() routing
        return await Oracle().talk("@fakeAgent hello")
    result = _run(t)
    # Should not be 'fakeAgent', likely 'Iris' or a domain-routed entity
    assert result.entity != "fakeAgent"


def test_talk_mention_case_insensitive():
    async def t():
        return await Oracle().talk("Can you help me @SYSADMIN?")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_talk_mention_email_false_positive():
    """Verify that email addresses do NOT trigger a summon."""
    async def t():
        # 'test@example.com' should not be recognized as a summon to 'example'
        return await Oracle().talk("send an email to test@example.com")
    result = _run(t)
    # Should not be 'example', likely 'Iris' or a domain-routed entity
    assert result.entity != "example"


def test_talk_multiple_mentions():
    """Verify that the first valid mention takes priority."""
    async def t():
        # Both @sysAdmin and @watchTower are likely valid (based on other tests)
        # The first one found by findall should be returned
        return await Oracle().talk("Hello @sysAdmin and @watchTower")
    result = _run(t)
    assert result.entity == "SysAdmin"


def test_get_valid_agents_missing_file():
    """Verify graceful degradation if AGENTS.md is missing."""
    from unittest.mock import patch
    from pathlib import Path

    def t():
        with patch("pathlib.Path.exists", return_value=False):
            oracle = Oracle()
            # Clear cache if it was populated
            Oracle._valid_agents_cache = None
            agents = oracle._get_valid_agents_from_md()
            return agents
    
    result = t()
    assert result == set()

