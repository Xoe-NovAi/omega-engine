"""Tests for Omega Observability."""

from omega.observability import ObservabilityEngine, new_trace_id


def test_new_trace_id():
    tid = new_trace_id()
    assert tid.startswith("trc_")
    assert len(tid) == 16


def test_log_event():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()
    tid = new_trace_id()
    engine.log_event("test.event", tid, {"key": "value"})
    assert len(engine._event_log) == 1
    assert engine._event_log[0]["event"] == "test.event"
    assert engine._event_log[0]["data"]["key"] == "value"


def test_trace_session():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()
    trace = engine.trace()
    assert trace.trace_id.startswith("trc_")
    trace.log("test.event", detail="hello")
    assert len(engine._event_log) == 1


def test_trace_session_context_manager():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()
    
    async def run():
        async with engine.trace() as trace:
            trace.log("query.received", query="hello")
        assert len(engine._event_log) == 1
        assert engine._event_log[0]["event"] == "query.received"

    import anyio
    anyio.run(run)


def test_record_training_example():
    engine = ObservabilityEngine(enable_dataset_collection=True)
    tid = new_trace_id()
    engine.record_training_example(
        trace_id=tid,
        query="what is justice?",
        system_prompt="You are Ma'at.",
        response="Justice is balance.",
        entity="Ma'at",
        model="qwen3-1.7b-q6_k",
        backend="ollama",
        confidence=0.9,
        latency_ms=1500,
    )
    assert len(engine._dataset) == 1
    example = engine._dataset[0]
    assert example["trace_id"] == tid
    assert example["messages"][-1]["content"] == "Justice is balance."
    assert example["metadata"]["entity"] == "Ma'at"


def test_stats():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()
    tid = new_trace_id()
    engine.log_event("query.received", tid, {})
    engine.log_event("response.delivered", tid, {})
    
    stats = engine.stats()
    assert stats["total_events"] == 2
    assert stats["event_counts"]["query.received"] == 1
    assert stats["event_counts"]["response.delivered"] == 1
    assert stats["dataset_size"] == 0


def test_flush_dataset(tmp_path):
    import anyio

    engine = ObservabilityEngine(enable_dataset_collection=True)
    tid = new_trace_id()
    engine.record_training_example(tid, "q?", "sys", "resp", "E", "m", "b", 0.5, 100)

    async def run():
        path = await engine.flush_dataset()
        assert path is not None
        assert path.exists()
        content = path.read_text()
        assert tid in content

    anyio.run(run)


def test_dataset_collection_disabled():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    tid = new_trace_id()
    engine.record_training_example(tid, "q?", "sys", "resp", "E", "m", "b", 0.5, 100)
    assert engine._dataset == []


def test_eventtype_enum_completeness():
    from omega.observability import EventType
    # Ensure no duplicate values in EventType
    values = [getattr(EventType, attr) for attr in dir(EventType) if not attr.startswith("__")]
    assert len(values) == len(set(values)), f"Duplicate EventType values found: {values}"


# ── Contextvars Safety Net Tests ─────────────────────────────────────


def test_contextvars_generates_new_trace_id():
    """get_current_trace_id() generates a new trace_id when none is set."""
    from omega.observability.context import get_current_trace_id, reset_current_trace_id

    reset_current_trace_id()  # Ensure clean state
    tid = get_current_trace_id()
    assert tid.startswith("trc_"), f"Expected trc_ prefix, got {tid}"
    assert len(tid) == 16, f"Expected 16 chars, got {len(tid)}: {tid}"


def test_contextvars_returns_same_id_when_set():
    """get_current_trace_id() returns the same ID after set_current_trace_id()."""
    from omega.observability.context import get_current_trace_id, set_current_trace_id, reset_current_trace_id

    reset_current_trace_id()  # Ensure clean state
    set_current_trace_id("explicit-trace-123")
    assert get_current_trace_id() == "explicit-trace-123"


def test_contextvars_persists_across_calls():
    """get_current_trace_id() returns the same ID when called multiple times."""
    from omega.observability.context import get_current_trace_id, reset_current_trace_id

    reset_current_trace_id()
    first = get_current_trace_id()
    second = get_current_trace_id()
    assert first == second, "Multiple calls should return the same trace_id"


def test_reset_trace_id_generates_new():
    """After reset_current_trace_id(), get_current_trace_id() generates a new ID."""
    from omega.observability.context import get_current_trace_id, set_current_trace_id, reset_current_trace_id

    set_current_trace_id("first-trace")
    assert get_current_trace_id() == "first-trace"

    reset_current_trace_id()
    new_tid = get_current_trace_id()
    assert new_tid != "first-trace", "After reset, should get a new trace ID"
    assert new_tid.startswith("trc_")


# ── record_error trace_id Tests ────────────────────────────────────────


def test_record_error_with_trace_id():
    """record_error() uses the provided trace_id."""
    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()

    error = ValueError("test error")
    engine.record_error(error, trace_id="explicit-trace-456")

    recent = engine._forensics.recent_errors
    assert len(recent) >= 1
    # The most recent error should have our trace_id
    last_err = recent[-1]
    assert last_err["trace_id"] == "explicit-trace-456"

    # Check event log too
    found = any(
        e["event"] == "error" and e["trace_id"] == "explicit-trace-456"
        for e in engine._event_log
    )
    assert found, "Error event must carry the explicit trace_id"


def test_record_error_without_trace_id():
    """record_error() uses contextvars safety net when trace_id is None."""
    from omega.observability.context import set_current_trace_id, reset_current_trace_id

    reset_current_trace_id()
    set_current_trace_id("context-trace-789")

    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()

    error = RuntimeError("error without trace_id")
    engine.record_error(error, trace_id=None)

    # Error should NOT have "unknown" as trace_id
    recent = engine._forensics.recent_errors
    last_err = recent[-1]
    assert last_err["trace_id"] != "unknown", "trace_id must never be 'unknown'"
    # Should have picked up the contextvar
    assert last_err["trace_id"] == "context-trace-789"

    # Check event log too
    found = any(
        e["event"] == "error" and e["trace_id"] == "context-trace-789"
        for e in engine._event_log
    )
    assert found, "Error event must carry contextvar trace_id"


def test_record_error_generates_new_trace_id_when_no_context():
    """record_error() generates a new trace_id when no contextvar is set."""
    from omega.observability.context import reset_current_trace_id

    reset_current_trace_id()  # Ensure no context trace

    engine = ObservabilityEngine(enable_dataset_collection=False)
    engine.clear_log()

    error = RuntimeError("error with no context")
    engine.record_error(error, trace_id=None)

    recent = engine._forensics.recent_errors
    last_err = recent[-1]
    assert last_err["trace_id"] != "unknown", "trace_id must never be 'unknown'"
    assert last_err["trace_id"].startswith("trc_"), "Should generate new trace_id"

