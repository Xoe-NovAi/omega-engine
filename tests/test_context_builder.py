import pytest
from omega.oracle.context_builder import ContextBuilder, MAX_EXCHANGE_DISPLAY_LENGTH

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
    # build_context now uses token_limit for sliding window truncation
    # It always fetches MAX_EXCHANGE_DISPLAY_LENGTH and truncates locally
    result = await cb.build_context("Sophia", "ses_123", token_limit=1)
    # With token_limit=1, the sliding window should produce a very short context
    mock_memory_store.get_history.assert_called_with(
        entity_name="Sophia", session_id="ses_123", limit=MAX_EXCHANGE_DISPLAY_LENGTH
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
        entity_name="user", session_id="ses_123", limit=MAX_EXCHANGE_DISPLAY_LENGTH
    )

@pytest.mark.anyio
async def test_build_context_for_user_exception(mock_memory_store):
    mock_memory_store.get_history.side_effect = Exception("DB Error")
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context_for_user("user_1", "ses_123")
    assert context == ""

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
async def test_build_context_with_custom_limit(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    # build_context now uses token_limit for sliding window; always fetches MAX_EXCHANGE_DISPLAY_LENGTH
    await cb.build_context("Sophia", "ses_123", token_limit=10)
    mock_memory_store.get_history.assert_called_with(
        entity_name="Sophia", session_id="ses_123", limit=MAX_EXCHANGE_DISPLAY_LENGTH
    )

@pytest.mark.anyio
async def test_build_context_for_user_with_data(mock_memory_store, sample_exchanges):
    mock_memory_store.get_history.return_value = sample_exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)
    context = await cb.build_context_for_user("u1", "s1")
    assert "User: What is strength?" in context

@pytest.mark.anyio
async def test_sliding_window_keeps_newest_exchanges(mock_memory_store):
    """The sliding window must keep the most recent exchanges, not the oldest."""
    exchanges = [
        {"timestamp": "2026-05-16T10:00:00Z", "user": "msg-oldest-1", "assistant": "resp-oldest-1"},
        {"timestamp": "2026-05-16T10:01:00Z", "user": "msg-2", "assistant": "resp-2"},
        {"timestamp": "2026-05-16T10:02:00Z", "user": "msg-3", "assistant": "resp-3"},
        {"timestamp": "2026-05-16T10:03:00Z", "user": "msg-4", "assistant": "resp-4"},
        {"timestamp": "2026-05-16T10:04:00Z", "user": "msg-newest-5", "assistant": "resp-newest-5"},
    ]
    mock_memory_store.get_history.return_value = exchanges
    cb = ContextBuilder(memory_store=mock_memory_store)

    # Use a token budget that fits 3 exchanges + header but not all 5
    # Each exchange block is ~80 chars = ~20 tokens, header ~35 chars = ~9 tokens
    # 3 exchanges + header = ~69 tokens. Use 80.
    context = await cb.build_context("Sophia", "ses_123", token_limit=80)

    # Newest must be present (the last 3 survive)
    assert "msg-newest-5" in context
    assert "resp-newest-5" in context
    assert "msg-4" in context
    assert "msg-3" in context

    # Oldest must be absent (dropped by sliding window)
    assert "msg-oldest-1" not in context
    assert "resp-oldest-1" not in context

    # Output should be in chronological order
    pos_3 = context.find("msg-3")
    pos_4 = context.find("msg-4")
    pos_newest = context.find("msg-newest-5")
    assert pos_3 < pos_4 < pos_newest  # chronological order preserved
