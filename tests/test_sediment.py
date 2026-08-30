# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import AsyncMock, MagicMock
from omega.research.sediment import (
    SEDABus,
    SEDAReader,
    SEDAEvent,
    SEDATopic,
    BackPressurePolicy,
    SEDAError,
    SEDAOverflowError,
    SEDASubscriptionError,
    DEFAULT_BUFFER_SIZES,
)
from omega.observability.observability_reader import FleetHealth, CognitiveVelocity, TokenBurn


# ─── SEDABus Tests ──────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_bus_create_and_close():
    """SEDABus can be created and closed."""
    bus = SEDABus()
    assert bus.subscriber_count == 0
    assert bus.is_closed is False
    await bus.close()
    assert bus.is_closed is True


@pytest.mark.anyio
async def test_bus_subscribe_and_publish():
    """Subscribing to a topic and publishing delivers events."""
    bus = SEDABus()
    send_stream, recv_stream = await bus.subscribe(
        topic=SEDATopic.TRACES,
        subscriber_id="test_subscriber",
        buffer_size=10,
    )

    assert bus.subscriber_count == 1
    assert "test_subscriber" in bus.get_subscribers_for_topic(SEDATopic.TRACES)

    event = SEDAEvent(
        topic=SEDATopic.TRACES,
        payload={"message": "test event"},
        entity="test_entity",
    )
    delivered = await bus.publish(event)
    assert delivered == 1

    received = await recv_stream.receive()
    assert received.topic == SEDATopic.TRACES
    assert received.payload["message"] == "test event"
    assert received.entity == "test_entity"

    await bus.close()


@pytest.mark.anyio
async def test_bus_multiple_subscribers_same_topic():
    """Multiple subscribers to the same topic each get their own copy."""
    bus = SEDABus()
    _, recv1 = await bus.subscribe(SEDATopic.METRICS, "sub1", buffer_size=10)
    _, recv2 = await bus.subscribe(SEDATopic.METRICS, "sub2", buffer_size=10)

    event = SEDAEvent(topic=SEDATopic.METRICS, payload={"value": 42})
    delivered = await bus.publish(event)
    assert delivered == 2

    e1 = await recv1.receive()
    e2 = await recv2.receive()
    assert e1.payload["value"] == 42
    assert e2.payload["value"] == 42

    await bus.close()


@pytest.mark.anyio
async def test_bus_backpressure_buffer_policy():
    """BUFFER policy drops oldest events when buffer is full."""
    bus = SEDABus()
    _, recv_stream = await bus.subscribe(
        topic=SEDATopic.TRACES,
        subscriber_id="small_buffer",
        buffer_size=2,
        policy=BackPressurePolicy.BUFFER,
    )

    # Fill buffer with 2 events
    for i in range(2):
        await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": i}))

    # Third event should trigger buffer drop (oldest dropped)
    await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": 2}))

    # First received should be the second event (index 1), not the first (index 0)
    e1 = await recv_stream.receive()
    e2 = await recv_stream.receive()
    assert e1.payload["i"] == 1  # First was dropped
    assert e2.payload["i"] == 2

    await bus.close()


@pytest.mark.anyio
async def test_bus_backpressure_reject_policy():
    """REJECT policy raises SEDAOverflowError when buffer is full."""
    bus = SEDABus()
    _, recv_stream = await bus.subscribe(
        topic=SEDATopic.TRACES,
        subscriber_id="reject_sub",
        buffer_size=1,
        policy=BackPressurePolicy.REJECT,
    )

    # Fill buffer
    await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": 0}))

    # Next publish should raise
    with pytest.raises(SEDAOverflowError, match="buffer full"):
        await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": 1}))

    await bus.close()


@pytest.mark.anyio
async def test_bus_backpressure_block_policy():
    """BLOCK policy waits for buffer space."""
    bus = SEDABus()
    _, recv_stream = await bus.subscribe(
        topic=SEDATopic.TRACES,
        subscriber_id="block_sub",
        buffer_size=1,
        policy=BackPressurePolicy.BLOCK,
    )

    # Fill buffer
    await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": 0}))

    # Consume one to make room, then publish should succeed
    await recv_stream.receive()
    await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"i": 1}))

    e = await recv_stream.receive()
    assert e.payload["i"] == 1

    await bus.close()


@pytest.mark.anyio
async def test_bus_unsubscribe():
    """Unsubscribing removes the subscriber from the bus."""
    bus = SEDABus()
    _, recv_stream = await bus.subscribe(SEDATopic.TRACES, "temp_sub", buffer_size=10)

    assert bus.subscriber_count == 1
    result = await bus.unsubscribe("temp_sub")
    assert result is True
    assert bus.subscriber_count == 0

    # Publishing should deliver 0 events
    delivered = await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={}))
    assert delivered == 0

    await bus.close()


@pytest.mark.anyio
async def test_bus_unsubscribe_nonexistent():
    """Unsubscribing a non-existent subscriber returns False."""
    bus = SEDABus()
    result = await bus.unsubscribe("nonexistent")
    assert result is False
    await bus.close()


@pytest.mark.anyio
async def test_bus_publish_closed_raises():
    """Publishing to a closed bus raises SEDAError."""
    bus = SEDABus()
    await bus.close()
    with pytest.raises(SEDAError, match="closed bus"):
        await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={}))


@pytest.mark.anyio
async def test_bus_subscribe_closed_raises():
    """Subscribing to a closed bus raises SEDASubscriptionError."""
    bus = SEDABus()
    await bus.close()
    with pytest.raises(SEDASubscriptionError, match="closed bus"):
        await bus.subscribe(SEDATopic.TRACES, "late_sub", buffer_size=10)


@pytest.mark.anyio
async def test_bus_default_buffer_sizes():
    """Default buffer sizes are set per topic."""
    assert DEFAULT_BUFFER_SIZES[SEDATopic.TRACES.value] == 100
    assert DEFAULT_BUFFER_SIZES[SEDATopic.METRICS.value] == 200
    assert DEFAULT_BUFFER_SIZES[SEDATopic.SYSTEM_EVENT.value] == 20


@pytest.mark.anyio
async def test_bus_multi_topic_subscription():
    """A subscriber can subscribe to multiple topics."""
    bus = SEDABus()
    send1, recv1 = await bus.subscribe(SEDATopic.TRACES, "multi_sub", buffer_size=10)
    send2, recv2 = await bus.subscribe(SEDATopic.METRICS, "multi_sub", buffer_size=10)

    # Same subscriber, different topics
    assert send1 is send2
    assert recv1 is recv2

    # Publish to traces
    await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={"t": 1}))
    e = await recv1.receive()
    assert e.payload["t"] == 1

    # Publish to metrics
    await bus.publish(SEDAEvent(topic=SEDATopic.METRICS, payload={"m": 2}))
    e = await recv2.receive()
    assert e.payload["m"] == 2

    await bus.close()


# ─── SEDAReader Tests ───────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_seda_reader_creates_bus_and_reader():
    """SEDAReader wraps a SovereignReader and SEDABus."""
    mock_reader = MagicMock()
    bus = SEDABus()
    reader = SEDAReader(mock_reader, bus, poll_interval=0.1)

    assert reader._reader is mock_reader
    assert reader._bus is bus
    assert reader._poll_interval == 0.1
    assert reader._current_entity == "system"

    await bus.close()


@pytest.mark.anyio
async def test_seda_reader_set_entity():
    """SEDAReader.set_entity updates the current entity filter."""
    mock_reader = MagicMock()
    bus = SEDABus()
    reader = SEDAReader(mock_reader, bus, poll_interval=0.1)

    reader.set_entity("kali")
    assert reader._current_entity == "kali"

    await bus.close()


@pytest.mark.anyio
async def test_seda_reader_publishes_events():
    """SEDAReader fetches data and publishes SEDA events."""
    # Create a mock reader with async methods
    mock_reader = MagicMock()
    mock_reader.get_fleet_health = AsyncMock(
        return_value=FleetHealth(breaker_states={"test": "closed"}, global_error_rate=0.0)
    )
    mock_reader.tail_live_traces = AsyncMock(return_value=[])
    mock_reader.get_cognitive_velocity = AsyncMock(
        return_value=CognitiveVelocity(tokens_per_second=10.0, acceleration=0.5)
    )
    mock_reader.get_entity_cost = AsyncMock(
        return_value=TokenBurn(100, 50, 0.001, "native-gguf")
    )
    mock_reader.get_sovereignty_ratio = AsyncMock(return_value=1.0)
    mock_reader.get_somatic_pressure = AsyncMock(
        return_value={"avg_latency_ms": 10.0, "max_latency_ms": 50.0, "request_count": 5}
    )

    bus = SEDABus()
    reader = SEDAReader(mock_reader, bus, poll_interval=0.1)

    # Subscribe to topics
    _, recv_health = await bus.subscribe(SEDATopic.FLEET_HEALTH, "test_health", buffer_size=10)
    _, recv_traces = await bus.subscribe(SEDATopic.TRACES, "test_traces", buffer_size=10)
    _, recv_velocity = await bus.subscribe(SEDATopic.COGNITIVE_VELOCITY, "test_vel", buffer_size=10)
    _, recv_cost = await bus.subscribe(SEDATopic.TOKEN_BURN, "test_cost", buffer_size=10)
    _, recv_sov = await bus.subscribe(SEDATopic.SOVEREIGNTY_RATIO, "test_sov", buffer_size=10)
    _, recv_somatic = await bus.subscribe(SEDATopic.SOMATIC_PRESSURE, "test_somatic", buffer_size=10)
    _, recv_sys = await bus.subscribe(SEDATopic.SYSTEM_EVENT, "test_sys", buffer_size=10)

    # Run one poll cycle
    await reader._fetch_and_publish()

    # Verify events were published
    health_event = await recv_health.receive()
    assert health_event.payload["breaker_states"] == {"test": "closed"}
    assert health_event.payload["global_error_rate"] == 0.0

    velocity_event = await recv_velocity.receive()
    assert velocity_event.payload["tokens_per_second"] == 10.0

    cost_event = await recv_cost.receive()
    assert cost_event.payload["prompt_tokens"] == 100
    assert cost_event.payload["provider_name"] == "native-gguf"

    sov_event = await recv_sov.receive()
    assert sov_event.payload["ratio"] == 1.0

    somatic_event = await recv_somatic.receive()
    assert somatic_event.payload["avg_latency_ms"] == 10.0

    sys_event = await recv_sys.receive()
    assert sys_event.payload["status"] == "poll_complete"

    await bus.close()


@pytest.mark.anyio
async def test_seda_reader_error_handling():
    """SEDAReader publishes error events on reader failure."""
    mock_reader = MagicMock()
    mock_reader.get_fleet_health = AsyncMock(side_effect=Exception("DB connection failed"))

    bus = SEDABus()
    reader = SEDAReader(mock_reader, bus, poll_interval=0.1)

    _, recv_sys = await bus.subscribe(SEDATopic.SYSTEM_EVENT, "err_test", buffer_size=10)

    await reader._fetch_and_publish()

    # An error event should have been published
    event = await recv_sys.receive()
    assert event.payload["error"] == "DB connection failed"
    assert event.payload["source"] == "fleet_health"

    await bus.close()


# ─── SEDAEvent Tests ────────────────────────────────────────────────────────────

def test_seda_event_to_dict():
    """SEDAEvent.to_dict produces correct serialization."""
    event = SEDAEvent(
        topic=SEDATopic.TRACES,
        payload={"key": "value"},
        entity="test_entity",
        trace_id="trace-123",
        priority=1,
    )
    d = event.to_dict()
    assert d["topic"] == "traces"
    assert d["payload"] == {"key": "value"}
    assert d["entity"] == "test_entity"
    assert d["trace_id"] == "trace-123"
    assert d["priority"] == 1
    assert "timestamp" in d


def test_seda_event_defaults():
    """SEDAEvent has correct default values."""
    event = SEDAEvent(topic=SEDATopic.METRICS, payload={})
    assert event.entity == "system"
    assert event.trace_id == "unknown"
    assert event.priority == 0
    assert event.timestamp is not None
