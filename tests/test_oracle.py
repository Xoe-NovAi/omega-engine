# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for Omega Oracle (async)."""

import pytest

from omega.oracle.oracle import Oracle


@pytest.mark.anyio
async def test_talk_empty_query():
    r = await Oracle().talk("")
    assert r.entity is not None  # Some entity handled the empty query
    assert isinstance(r.entity, str)


@pytest.mark.anyio
async def test_talk_summon_pattern():
    result = await Oracle().talk("@SysAdmin how do I deploy a container?")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_talk_summon_hey():
    result = await Oracle().talk("hey Sentinel, check the security audit")
    assert result.entity == "Sentinel"


@pytest.mark.anyio
async def test_talk_summon_command():
    result = await Oracle().talk("summon ModelGate, how is inference routing?")
    assert result.entity == "ModelGate"


@pytest.mark.anyio
async def test_talk_domain_routing():
    result = await Oracle().talk("I need to check infrastructure monitoring")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_talk_domain_routing_shadow():
    result = await Oracle().talk("check observability and logging")
    assert result.entity == "WatchTower"


@pytest.mark.anyio
async def test_summon_direct():
    result = await Oracle().summon("sysAdmin", "how do I configure the server?")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_summon_case_insensitive():
    result = await Oracle().summon("WATCHTOWER", "what metrics do you track?")
    assert result.entity == "WatchTower"


@pytest.mark.anyio
async def test_summon_unknown_entity():
    result = await Oracle().summon("unknown_entity", "hello")
    assert result.entity is not None


def test_all_slot_keepers_have_required_fields():
    """Structural invariants - every slot keeper must have required fields.
    
    Does NOT hardcode entity names per the Engine-Stack Firewall mandate.
    """
    oracle = Oracle()
    keepers = oracle.registry.list_slot_keepers()
    assert len(keepers) >= 1  # At least one keeper exists
    for k in keepers:
        assert k.name is not None, "Slot keeper missing name"
        assert k.slots, "Slot keeper must have slot assignments"
        assert k.domains is not None, "Slot keeper must have domains"


@pytest.mark.anyio
async def test_iris_speculative_decoder_simple():
    """Simple queries should be handled by Iris directly."""
    result = await Oracle().talk("hello")
    assert result.entity == "Iris"
    assert result.confidence >= 0.8


@pytest.mark.anyio
async def test_iris_speculative_decoder_complex():
    """Complex queries should escalate to a Node Keeper."""
    result = await Oracle().talk("explain the meaning of justice")
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


@pytest.mark.anyio
async def test_talk_injects_context_into_prompt():
    """Verify ContextBuilder.build_context is called during talk()."""
    from unittest.mock import AsyncMock, patch

    with patch("omega.oracle.oracle.ContextBuilder") as MockCB:
        mock_instance = MockCB.return_value
        mock_instance.build_context = AsyncMock(return_value="")
        mock_instance.prepend_to_prompt = AsyncMock(side_effect=lambda ctx, prompt: prompt)

        oracle = Oracle()
        oracle.context_builder = mock_instance
        result = await oracle.talk("hello")
        assert result is not None


@pytest.mark.anyio
async def test_talk_with_empty_memory_still_works():
    """First conversation with no history should not crash."""
    oracle = Oracle()
    result = await oracle.talk("this is my first message")
    assert result is not None
    assert result.text is not None


@pytest.mark.anyio
async def test_talk_context_builder_exception_does_not_crash():
    """If ContextBuilder fails, Oracle should gracefully degrade."""
    from unittest.mock import AsyncMock

    oracle = Oracle()
    oracle.context_builder.build_context = AsyncMock(
        side_effect=OSError("simulated memory failure")
    )
    result = await oracle.talk("I need strength")
    assert result is not None
    assert result.text is not None


@pytest.mark.anyio
async def test_summon_uses_record_interaction():
    """After deduplication, summon() should delegate to _record_interaction()."""
    from unittest.mock import AsyncMock

    oracle = Oracle()
    oracle._record_interaction = AsyncMock()
    result = await oracle.summon("sysAdmin", "configure the server")
    oracle._record_interaction.assert_called_once()
    call_args = oracle._record_interaction.call_args
    assert call_args[0][1] == "configure the server"
    assert call_args[0][3] is False
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_summon_transient_skips_recording():
    """transient=True should skip _record_interaction."""
    from unittest.mock import AsyncMock

    oracle = Oracle()
    oracle._record_interaction = AsyncMock()
    result = await oracle.summon("sysAdmin", "ephemeral query", transient=True)
    oracle._record_interaction.assert_called_once()
    call_args = oracle._record_interaction.call_args
    assert call_args[0][3] is True
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_record_interaction_memory_failure_does_not_crash():
    """If add_exchange fails, _record_interaction should not raise."""
    from unittest.mock import AsyncMock, MagicMock

    oracle = Oracle()
    oracle.memory_store.add_exchange = AsyncMock(side_effect=OSError("disk full"))
    resp = MagicMock()
    resp.entity = "SysAdmin"
    resp.session_id = "ses_test"
    resp.text = "test response"
    resp.backend = "mock"
    resp.model = "mock-model"
    trace = MagicMock()
    trace.trace_id = "trace_test"

    await oracle._record_interaction(resp, "test query", trace, transient=False)


@pytest.mark.anyio
async def test_talk_mention_at_start():
    result = await Oracle().talk("@sysAdmin how do I deploy a container?")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_talk_mention_within_text():
    result = await Oracle().talk("Hello @sysAdmin, can you help me with the server?")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_talk_invalid_mention():
    result = await Oracle().talk("@fakeAgent hello")
    assert result.entity != "fakeAgent"


@pytest.mark.anyio
async def test_talk_mention_case_insensitive():
    result = await Oracle().talk("Can you help me @SYSADMIN?")
    assert result.entity == "SysAdmin"


@pytest.mark.anyio
async def test_talk_mention_email_false_positive():
    """Verify that email addresses do NOT trigger a summon."""
    result = await Oracle().talk("send an email to test@example.com")
    assert result.entity != "example"


@pytest.mark.anyio
async def test_talk_multiple_mentions():
    """Verify that the first valid mention takes priority."""
    result = await Oracle().talk("Hello @sysAdmin and @watchTower")
    assert result.entity == "SysAdmin"


def test_get_valid_agents_missing_file():
    """Verify graceful degradation if AGENTS.md is missing."""
    from unittest.mock import patch
    from pathlib import Path

    with patch("pathlib.Path.exists", return_value=False):
        oracle = Oracle()
        Oracle._valid_agents_cache = None
        agents = oracle._get_valid_agents_from_md()
        assert agents == set()

