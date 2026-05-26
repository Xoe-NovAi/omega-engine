import pytest
from omega.oracle.context_builder import ContextBuilder

@pytest.mark.anyio
async def test_context_builder_init_default_store(mock_memory_store):
    # Test that it uses the default store if none provided
    # Since we can't easily check the singleton without resetting, 
    # we just check it doesn't crash.
    cb = ContextBuilder()
    assert cb.memory_store is not None

@pytest.mark.anyio
async def test_context_builder_init_custom_store(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    assert cb.memory_store == mock_memory_store

@pytest.mark.anyio
async def test_build_context_empty_history(mock_memory_store):
    mock_memory_store.get_history.return_value = []
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context("Sophia", "ses_123")
    assert context == ""

@pytest.mark.anyio
async def test_build_context_happy_path(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context("Sophia", "ses_123")
    assert "## Recent Memory Context" in context
    assert "What is strength?" in context
    assert "Courage is strength" in context
    assert "---" in context

@pytest.mark.anyio
async def test_build_context_respects_limit(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    # limit is passed to memory_store.get_history
    await cb.build_context("Sophia", "ses_123", limit=1)
    mock_memory_store.get_history.assert_called_with(
        entity_name="Sophia", session_id="ses_123", limit=1
    )

@pytest.mark.anyio
async def test_build_context_exception_returns_empty(mock_memory_store):
    mock_memory_store.get_history.side_effect = Exception("DB Error")
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context("Sophia", "ses_123")
    assert context == ""

@pytest.mark.anyio
async def test_build_context_none_exchanges(mock_memory_store):
    mock_memory_store.get_history.return_value = None
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context("Sophia", "ses_123")
    assert context == ""

@pytest.mark.anyio
async def test_build_context_for_user_happy_path(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context_for_user("user_1", "ses_123")
    assert "## Recent Memory Context" in context
    mock_memory_store.get_history.assert_called_with(
        entity_name="user", session_id="ses_123", limit=6
    )

@pytest.mark.anyio
async def test_build_context_for_user_exception(mock_memory_store):
    mock_memory_store.get_history.side_effect = Exception("DB Error")
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context_for_user("user_1", "ses_123")
    assert context == ""

@pytest.mark.anyio
async def test_format_exchanges_structure(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    exchanges = [
        {"timestamp": "2026-05-16T10:00:00Z", "user": "U1", "assistant": "A1"},
    ]
    formatted = cb._format_exchanges(exchanges)
    assert "User: U1" in formatted
    assert "Assistant: A1" in formatted
    assert "---" in formatted

@pytest.mark.anyio
async def test_format_timestamp_valid(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    ts = "2026-05-16T10:00:00+00:00"
    formatted = cb._format_timestamp(ts)
    assert "2026-05-16 10:00:00" in formatted

@pytest.mark.anyio
async def test_format_timestamp_invalid(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    assert cb._format_timestamp(None) == "unknown"
    assert cb._format_timestamp("not-a-date") == "not-a-date"

@pytest.mark.anyio
async def test_truncate_short_text(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    text = "Short text"
    assert cb._truncate(text) == text

@pytest.mark.anyio
async def test_truncate_long_text(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    text = "a" * 600
    truncated = cb._truncate(text)
    assert len(truncated) == 503 # 500 + "..."
    assert truncated.endswith("...")

@pytest.mark.anyio
async def test_prepend_to_prompt_empty_context(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    prompt = "You are a helpful assistant."
    assert cb.prepend_to_prompt("", prompt) == prompt
    assert cb.prepend_to_prompt(None, prompt) == prompt

@pytest.mark.anyio
async def test_prepend_to_prompt_with_context(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = "Memory: User said hello."
    prompt = "You are a helpful assistant."
    result = cb.prepend_to_prompt(context, prompt)
    assert result.startswith(context)
    assert result.endswith(prompt)
    assert "\n" in result

@pytest.mark.anyio
async def test_build_context_formatting_timestamp_call(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context("Sophia", "ses_123")
    # Check if timestamp is formatted (e.g., [2026-05-16 10:00:00])
    import re
    assert re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", context)

@pytest.mark.anyio
async def test_build_context_for_user_empty(mock_memory_store):
    mock_memory_store.get_history.return_value = []
    cb = ContextBuilder(memory_store=mock_memory_store)
    assert await cb.build_context_for_user("u1", "s1") == ""

@pytest.mark.anyio
async def test_prepend_to_prompt_whitespace_only(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    prompt = "Hello"
    assert cb.prepend_to_prompt("   ", prompt) == prompt

@pytest.mark.anyio
async def test_format_exchanges_empty_list(mock_memory_store):
    cb = ContextBuilder(memory_store=mock_memory_store)
    # _format_exchanges doesn't handle empty list explicitly, it just returns header + separator
    # but build_context handles it. Let's check the raw method.
    formatted = cb._format_exchanges([])
    assert "## Recent Memory Context" in formatted
    assert "---" in formatted

@pytest.mark.anyio
async def test_build_context_with_custom_limit(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    await cb.build_context("Sophia", "ses_123", limit=1)
    mock_memory_store.get_history.assert_called_with(
        entity_name="Sophia", session_id="ses_123", limit=1
    )

@pytest.mark.anyio
async def test_build_context_for_user_with_data(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context_for_user("u1", "s1")
    assert "User: What is strength?" in context
