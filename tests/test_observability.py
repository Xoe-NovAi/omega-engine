"""Tests for Omega Observability."""

from omega.observability import ObservabilityEngine, new_trace_id


def test_new_trace_id():
    tid = new_trace_id()
    assert tid.startswith("trc_")
    assert len(tid) == 16


def test_log_event():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    tid = new_trace_id()
    engine.log_event("test.event", tid, {"key": "value"})
    assert len(engine._event_log) == 1
    assert engine._event_log[0]["event"] == "test.event"
    assert engine._event_log[0]["data"]["key"] == "value"


def test_trace_session():
    engine = ObservabilityEngine(enable_dataset_collection=False)
    trace = engine.trace()
    assert trace.trace_id.startswith("trc_")
    trace.log("test.event", detail="hello")
    assert len(engine._event_log) == 1


def test_trace_session_context_manager():
    engine = ObservabilityEngine(enable_dataset_collection=False)

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
