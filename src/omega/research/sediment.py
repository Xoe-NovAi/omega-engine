# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-MAAT-SEDA-v1.0.0
# 🔱 SEDA — Sovereign Engine Data Access Ring-Bus
#
# A lightweight event bus built on AnyIO memory object streams.
# Provides topic-based pub/sub with back-pressure policies, subscriber
# lifecycle management, and dead-letter handling for the Omega Engine.
#
# Design principles:
#   - M1 AnyIO: Uses only anyio.create_memory_object_stream — no asyncio.
#   - M8 Zero Telemetry: All data stays local; no external reporting.
#   - M9 Error Integrity: Typed errors with trace_id propagation.
#   - M23 Failure Integrity: Buffer overflow raises SEDAOverflowError, not silent drop.
#
# [id-soft: vet-045] SEDA Ring-Bus — inspired by LMAX Disruptor ring buffer pattern.
#   The Disruptor uses a pre-allocated ring buffer with sequence-based coordination
#   for ultra-low-latency event passing. Omega's SEDA bus uses AnyIO memory object
#   streams with configurable buffer sizes and back-pressure policies, trading
#   Disruptor's zero-allocation for AnyIO portability and M1 compliance.
#   The core insight (single-writer, multi-subscriber event fan-out) is preserved.

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import anyio

from omega.errors import OmegaError

logger = logging.getLogger(__name__)


# ─── Errors ─────────────────────────────────────────────────────────────────────


class SEDAError(OmegaError):
    """Base error for SEDA bus failures."""

    pass


class SEDAOverflowError(SEDAError):
    """Raised when a subscriber's buffer overflows and the policy is 'reject'."""

    pass


class SEDASubscriptionError(SEDAError):
    """Raised when subscription operations fail."""

    pass


# ─── Enums & Constants ──────────────────────────────────────────────────────────


class SEDATopic(str, Enum):
    """Named topics for SEDA event routing.

    Topics correspond to observability data categories that the TUI
    and other consumers need to subscribe to.
    """

    TRACES = "traces"
    METRICS = "metrics"
    FLEET_HEALTH = "fleet_health"
    COGNITIVE_VELOCITY = "cognitive_velocity"
    TOKEN_BURN = "token_burn"
    SOVEREIGNTY_RATIO = "sovereignty_ratio"
    SOMATIC_PRESSURE = "somatic_pressure"
    ENTITY_SELECTED = "entity_selected"
    SYSTEM_EVENT = "system_event"
    # [O1 Phase 2] DAG & Step Trace topics for TUI execution tracer
    DAG_UPDATE = "dag_update"
    STEP_TRACE = "step_trace"
    MEMORY_SCORE = "memory_score"
    EXECUTION_PLAN = "execution_plan"


class BackPressurePolicy(str, Enum):
    """Back-pressure policies for buffer overflow.

    - BUFFER: Drop oldest events to make room (ring-buffer semantics).
    - REJECT: Raise SEDAOverflowError (fail-fast, M23).
    - BLOCK: Wait for buffer space (may stall publisher).
    """

    BUFFER = "buffer"
    REJECT = "reject"
    BLOCK = "block"


# Default buffer sizes per topic
DEFAULT_BUFFER_SIZES: Dict[str, int] = {
    SEDATopic.TRACES.value: 100,
    SEDATopic.METRICS.value: 200,
    SEDATopic.FLEET_HEALTH.value: 50,
    SEDATopic.COGNITIVE_VELOCITY.value: 50,
    SEDATopic.TOKEN_BURN.value: 50,
    SEDATopic.SOVEREIGNTY_RATIO.value: 50,
    SEDATopic.SOMATIC_PRESSURE.value: 50,
    SEDATopic.ENTITY_SELECTED.value: 10,
    SEDATopic.SYSTEM_EVENT.value: 20,
    # [O1 Phase 2] DAG & Step Trace buffer sizes
    SEDATopic.DAG_UPDATE.value: 30,
    SEDATopic.STEP_TRACE.value: 100,
    SEDATopic.MEMORY_SCORE.value: 50,
    SEDATopic.EXECUTION_PLAN.value: 10,
}


# ─── Data Models ────────────────────────────────────────────────────────────────


@dataclass
class SEDAEvent:
    """A single event flowing through the SEDA bus.

    Attributes:
        topic: The SEDATopic this event belongs to.
        payload: The event data (any serializable structure).
        entity: The entity this event relates to (or "system").
        trace_id: Correlation ID for tracing (M9).
        timestamp: ISO 8601 UTC timestamp.
        priority: Event priority (0=normal, 1=high, 2=critical).
    """

    topic: SEDATopic
    payload: Any
    entity: str = "system"
    trace_id: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic.value,
            "payload": self.payload,
            "entity": self.entity,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "priority": self.priority,
        }


# ─── O1 Phase 2: DAG & Step Trace Event Dataclasses ─────────────────────────────


@dataclass
class DAGUpdateEvent:
    """Published when a DAG is created, updated, or completed.

    [O1 Phase 2] Enables the TUI to render a visual DAG with color-coded
    task status (completed/pending/failed) and dependency edges.

    Attributes:
        dag_id: Unique DAG identifier (matches trace_id prefix).
        goal: The original user goal that spawned this DAG.
        tasks: List of task dicts (id, description, action_type, dependencies, status).
        completed_tasks: IDs of completed tasks.
        pending_tasks: IDs of pending tasks.
        failed_tasks: IDs of failed tasks (with error info).
        trace_id: Correlation ID for tracing.
        timestamp: ISO 8601 UTC timestamp.
    """

    dag_id: str
    goal: str
    tasks: List[Dict[str, Any]]
    completed_tasks: List[str]
    pending_tasks: List[str]
    failed_tasks: List[str]
    trace_id: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dag_id": self.dag_id,
            "goal": self.goal,
            "tasks": self.tasks,
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "failed_tasks": self.failed_tasks,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }


@dataclass
class StepTraceEvent:
    """Published for each execution step in a DAG.

    [O1 Phase 2] Enables the TUI to render a real-time step trace table
    with provider attribution, token usage, and latency.

    Attributes:
        step_id: Unique step identifier.
        dag_id: Parent DAG identifier.
        task_id: The sub-task this step belongs to.
        action_type: Type of action (extract, code, summarize, classify, etc.).
        provider: Provider name (native-gguf, antigravity, etc.).
        is_local: Whether the provider is local (M7 sovereignty).
        tokens_used: Total tokens consumed (prompt + completion).
        latency_ms: Execution latency in milliseconds.
        status: Step status (started, completed, failed, escalated).
        error: Error message if failed.
        trace_id: Correlation ID.
        timestamp: ISO 8601 UTC timestamp.
    """

    step_id: str
    dag_id: str
    task_id: str
    action_type: str
    provider: str
    is_local: bool
    tokens_used: int
    latency_ms: float
    status: str  # "started", "completed", "failed", "escalated"
    error: Optional[str] = None
    trace_id: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "dag_id": self.dag_id,
            "task_id": self.task_id,
            "action_type": self.action_type,
            "provider": self.provider,
            "is_local": self.is_local,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "error": self.error,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }


@dataclass
class MemoryScoreEvent:
    """Published for dual-branch memory scoring updates.

    [O1 Phase 2] Enables the TUI to visualize declarative vs episodic
    retrieval scores with lambda decay, consolidation penalty, and
    importance weighting.

    Attributes:
        entity: Entity name for this memory score.
        declarative_score: Score from declarative (consolidated) branch.
        episodic_score: Score from episodic (recent) branch.
        lambda_decay: Decay rate applied (default 0.005).
        consolidation_penalty: Penalty for unconsolidated memories (default 0.4).
        importance_weight: Weight for importance signal (default 0.5).
        trace_id: Correlation ID.
        timestamp: ISO 8601 UTC timestamp.
    """

    entity: str
    declarative_score: float
    episodic_score: float
    lambda_decay: float = 0.005
    consolidation_penalty: float = 0.4
    importance_weight: float = 0.5
    trace_id: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity": self.entity,
            "declarative_score": self.declarative_score,
            "episodic_score": self.episodic_score,
            "lambda_decay": self.lambda_decay,
            "consolidation_penalty": self.consolidation_penalty,
            "importance_weight": self.importance_weight,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }


@dataclass
class SEDASubscriber:
    """A subscriber to one or more SEDA topics.

    Attributes:
        id: Unique subscriber identifier.
        topics: Set of topics this subscriber is interested in.
        send_stream: The AnyIO send stream for delivering events.
        recv_stream: The AnyIO receive stream for the subscriber to consume.
        buffer_size: Configured buffer size for this subscriber.
        policy: Back-pressure policy.
        active: Whether this subscriber is currently active.
    """

    id: str
    topics: Set[str]
    send_stream: anyio.streams.memory.ObjectSendStream
    recv_stream: anyio.streams.memory.ObjectReceiveStream
    buffer_size: int
    policy: BackPressurePolicy
    active: bool = True
    created_at: float = field(default_factory=time.time)


# ─── SEDA Bus ───────────────────────────────────────────────────────────────────


class SEDABus:
    """Sovereign Engine Data Access ring-bus.

    A topic-based pub/sub event bus built on AnyIO memory object streams.
    Provides back-pressure policies, subscriber lifecycle management,
    and dead-letter handling.

    Usage:
        bus = SEDABus()
        send, recv = await bus.subscribe("traces", "my_consumer")
        await bus.publish(SEDAEvent(topic=SEDATopic.TRACES, payload={...}))
        async for event in recv:
            ...
    """

    def __init__(self, default_buffer_size: int = 100):
        self._default_buffer_size = default_buffer_size
        self._subscribers: Dict[str, SEDASubscriber] = {}
        self._topic_subscribers: Dict[str, List[str]] = {}  # topic -> [subscriber_ids]
        self._closed: bool = False

    @property
    def subscriber_count(self) -> int:
        """Total number of active subscribers."""
        return sum(1 for s in self._subscribers.values() if s.active)

    @property
    def is_closed(self) -> bool:
        """Whether the bus has been closed."""
        return self._closed

    def _buffer_size_for_topic(self, topic: str) -> int:
        """Get the default buffer size for a topic."""
        return DEFAULT_BUFFER_SIZES.get(topic, self._default_buffer_size)

    async def subscribe(
        self,
        topic: str | SEDATopic,
        subscriber_id: str,
        buffer_size: Optional[int] = None,
        policy: BackPressurePolicy = BackPressurePolicy.BUFFER,
    ) -> tuple[anyio.streams.memory.ObjectSendStream, anyio.streams.memory.ObjectReceiveStream]:
        """Subscribe to a topic.

        Creates a dedicated memory object stream pair for this subscriber.
        Multiple subscribers to the same topic each get their own stream.

        Args:
            topic: The topic to subscribe to (SEDATopic or string).
            subscriber_id: Unique identifier for this subscriber.
            buffer_size: Buffer size (defaults to topic-specific default).
            policy: Back-pressure policy for buffer overflow.

        Returns:
            Tuple of (send_stream, recv_stream). The subscriber consumes from
            recv_stream. The bus uses send_stream to deliver events.

        Raises:
            SEDASubscriptionError: If the bus is closed or subscriber_id exists.
        """
        if self._closed:
            raise SEDASubscriptionError("Cannot subscribe to a closed bus")

        topic_str = topic.value if isinstance(topic, SEDATopic) else topic

        if subscriber_id in self._subscribers:
            existing = self._subscribers[subscriber_id]
            if topic_str not in existing.topics:
                existing.topics.add(topic_str)
                self._topic_subscribers.setdefault(topic_str, []).append(subscriber_id)
                logger.debug(f"Subscriber '{subscriber_id}' added to topic '{topic_str}'")
                return existing.send_stream, existing.recv_stream
            raise SEDASubscriptionError(
                f"Subscriber '{subscriber_id}' already subscribed to topic '{topic_str}'"
            )

        buf_size = buffer_size or self._buffer_size_for_topic(topic_str)
        send_stream, recv_stream = anyio.create_memory_object_stream(max_buffer_size=buf_size)

        subscriber = SEDASubscriber(
            id=subscriber_id,
            topics={topic_str},
            send_stream=send_stream,
            recv_stream=recv_stream,
            buffer_size=buf_size,
            policy=policy,
        )
        self._subscribers[subscriber_id] = subscriber
        self._topic_subscribers.setdefault(topic_str, []).append(subscriber_id)

        logger.debug(
            f"Subscriber '{subscriber_id}' subscribed to topic '{topic_str}' (buffer={buf_size})"
        )
        return send_stream, recv_stream

    async def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe a subscriber from all topics.

        Closes the subscriber's streams and removes it from the bus.

        Args:
            subscriber_id: The subscriber to remove.

        Returns:
            True if the subscriber was found and removed, False otherwise.
        """
        if subscriber_id not in self._subscribers:
            return False

        subscriber = self._subscribers[subscriber_id]
        subscriber.active = False

        # Close streams
        try:
            await subscriber.send_stream.aclose()
            await subscriber.recv_stream.aclose()
        except Exception as e:
            logger.warning(f"Error closing streams for subscriber '{subscriber_id}': {e}")

        # Remove from topic mappings
        for topic in subscriber.topics:
            if topic in self._topic_subscribers:
                self._topic_subscribers[topic] = [
                    sid for sid in self._topic_subscribers[topic] if sid != subscriber_id
                ]
                if not self._topic_subscribers[topic]:
                    del self._topic_subscribers[topic]

        del self._subscribers[subscriber_id]
        logger.debug(f"Subscriber '{subscriber_id}' unsubscribed")
        return True

    async def publish(
        self,
        event: SEDAEvent,
        topic: Optional[str | SEDATopic] = None,
    ) -> int:
        """Publish an event to all subscribers of the event's topic.

        Args:
            event: The SEDAEvent to publish.
            topic: Optional topic override (uses event.topic if not specified).

        Returns:
            Number of subscribers that received the event.

        Raises:
            SEDAOverflowError: If a subscriber's buffer overflows and policy is REJECT.
        """
        if self._closed:
            raise SEDAError("Cannot publish to a closed bus")

        topic_str = topic.value if isinstance(topic, SEDATopic) else (topic or event.topic.value)
        delivered = 0

        subscriber_ids = self._topic_subscribers.get(topic_str, [])

        for sid in subscriber_ids:
            subscriber = self._subscribers.get(sid)
            if not subscriber or not subscriber.active:
                continue

            try:
                if subscriber.policy == BackPressurePolicy.REJECT:
                    subscriber.send_stream.send_nowait(event)
                elif subscriber.policy == BackPressurePolicy.BLOCK:
                    await subscriber.send_stream.send(event)
                else:  # BUFFER policy
                    try:
                        subscriber.send_stream.send_nowait(event)
                    except anyio.WouldBlock:
                        # Drop oldest event to make room
                        try:
                            _ = await subscriber.recv_stream.receive()
                        except anyio.EndOfStream:
                            pass
                        subscriber.send_stream.send_nowait(event)

                delivered += 1
            except anyio.WouldBlock:
                if subscriber.policy == BackPressurePolicy.REJECT:
                    raise SEDAOverflowError(
                        f"Subscriber '{sid}' buffer full (size={subscriber.buffer_size}) "
                        f"for topic '{topic_str}'. Policy=REJECT."
                    )
                else:
                    logger.warning(
                        f"Subscriber '{sid}' buffer full for topic '{topic_str}'. "
                        f"Event dropped (policy={subscriber.policy.value})."
                    )
            except Exception as e:
                logger.error(f"Failed to deliver event to subscriber '{sid}': {e}")

        return delivered

    async def publish_to_entity(
        self,
        event: SEDAEvent,
        entity: str,
    ) -> int:
        """Publish an event filtered by entity.

        Delivers the event only to subscribers that have subscribed
        to the event's topic AND have the matching entity filter.

        Args:
            event: The SEDAEvent to publish.
            entity: The entity to filter by.

        Returns:
            Number of subscribers that received the event.
        """
        event.entity = entity
        return await self.publish(event)

    async def close(self) -> None:
        """Close the bus and all subscriber streams."""
        if self._closed:
            return

        self._closed = True

        for subscriber in self._subscribers.values():
            subscriber.active = False
            try:
                await subscriber.send_stream.aclose()
                await subscriber.recv_stream.aclose()
            except Exception as e:
                logger.warning(f"Error closing subscriber '{subscriber.id}': {e}")

        self._subscribers.clear()
        self._topic_subscribers.clear()
        logger.info("SEDABus closed")

    def get_subscribers_for_topic(self, topic: str | SEDATopic) -> List[str]:
        """Get list of subscriber IDs for a topic."""
        topic_str = topic.value if isinstance(topic, SEDATopic) else topic
        return self._topic_subscribers.get(topic_str, [])


# ─── SEDA Reader Adapter ────────────────────────────────────────────────────────


class SEDAReader:
    """Adapter that bridges SovereignReader to the SEDA bus.

    Periodically polls the SovereignReader and publishes results as
    SEDA events on the appropriate topics. This allows the TUI to
    subscribe to real-time observability data via the SEDA bus
    instead of polling directly.

    Usage:
        reader = SovereignReader(db_path, trace_dir, crash_dir)
        bus = SEDABus()
        seda_reader = SEDAReader(reader, bus)
        await seda_reader.start()
        # ... later ...
        await seda_reader.stop()
    """

    def __init__(
        self,
        reader: Any,
        bus: SEDABus,
        poll_interval: float = 2.0,
    ):
        self._reader = reader
        self._bus = bus
        self._poll_interval = poll_interval
        self._cancel_scope: Optional[anyio.CancelScope] = None
        self._running: bool = False
        self._current_entity: str = "system"
        self._trace_id: str = "unknown"

    async def start(self) -> None:
        """Start the SEDA reader background task."""
        if self._running:
            return

        self._running = True
        self._trace_id = f"seda-reader-{int(time.time())}"

        async with anyio.create_task_group() as tg:
            self._cancel_scope = tg.cancel_scope
            tg.start_soon(self._poll_loop)

    async def stop(self) -> None:
        """Stop the SEDA reader background task."""
        self._running = False
        if self._cancel_scope:
            self._cancel_scope.cancel()

    def set_entity(self, entity: str) -> None:
        """Set the current entity for filtering."""
        self._current_entity = entity

    async def _poll_loop(self) -> None:
        """Main polling loop — fetches data and publishes SEDA events."""
        while self._running:
            try:
                await self._fetch_and_publish()
            except Exception as e:
                logger.error(f"SEDA reader poll error: {e}")
                # Publish error event
                await self._bus.publish(
                    SEDAEvent(
                        topic=SEDATopic.SYSTEM_EVENT,
                        payload={"error": str(e), "source": "seda_reader"},
                        entity="system",
                        trace_id=self._trace_id,
                    )
                )

            try:
                await anyio.sleep(self._poll_interval)
            except anyio.get_cancelled_exc_class():
                break

    async def _fetch_and_publish(self) -> None:
        """Fetch all observability data and publish as SEDA events.

        Each data source is fetched independently. If one fails, the
        error is logged and an error event is published, but other
        sources are still attempted (M9: error integrity).
        """
        entity = self._current_entity

        # Fleet health
        try:
            health = await self._reader.get_fleet_health()
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.FLEET_HEALTH,
                    payload={
                        "breaker_states": health.breaker_states,
                        "global_error_rate": health.global_error_rate,
                    },
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: fleet health fetch failed: {e}")
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.SYSTEM_EVENT,
                    payload={"error": str(e), "source": "fleet_health"},
                    entity="system",
                    trace_id=self._trace_id,
                )
            )

        # Traces
        try:
            traces = await self._reader.tail_live_traces(max_lines=30)
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.TRACES,
                    payload=[t.to_dict() if hasattr(t, "to_dict") else t.__dict__ for t in traces],
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: traces fetch failed: {e}")

        # Cognitive velocity
        try:
            velocity = await self._reader.get_cognitive_velocity(entity)
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.COGNITIVE_VELOCITY,
                    payload={
                        "tokens_per_second": velocity.tokens_per_second,
                        "acceleration": velocity.acceleration,
                    },
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: velocity fetch failed: {e}")

        # Token burn
        try:
            cost = await self._reader.get_entity_cost(entity)
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.TOKEN_BURN,
                    payload={
                        "prompt_tokens": cost.prompt_tokens,
                        "completion_tokens": cost.completion_tokens,
                        "cost_usd": cost.cost_usd,
                        "provider_name": cost.provider_name,
                    },
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: cost fetch failed: {e}")

        # Sovereignty ratio
        try:
            sovereignty = await self._reader.get_sovereignty_ratio(entity)
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.SOVEREIGNTY_RATIO,
                    payload={"ratio": sovereignty},
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: sovereignty fetch failed: {e}")

        # Somatic pressure
        try:
            somatic = await self._reader.get_somatic_pressure(entity)
            await self._bus.publish(
                SEDAEvent(
                    topic=SEDATopic.SOMATIC_PRESSURE,
                    payload=somatic,
                    entity=entity,
                    trace_id=self._trace_id,
                )
            )
        except Exception as e:
            logger.error(f"SEDA reader: somatic fetch failed: {e}")

        # System event (heartbeat)
        await self._bus.publish(
            SEDAEvent(
                topic=SEDATopic.SYSTEM_EVENT,
                payload={"status": "poll_complete", "entity": entity},
                entity="system",
                trace_id=self._trace_id,
            )
        )


# ─── Module exports ─────────────────────────────────────────────────────────────

__all__ = [
    "SEDABus",
    "SEDAReader",
    "SEDAEvent",
    "SEDASubscriber",
    "SEDATopic",
    "BackPressurePolicy",
    "SEDAError",
    "SEDAOverflowError",
    "SEDASubscriptionError",
    "DEFAULT_BUFFER_SIZES",
    # [O1 Phase 2] DAG & Step Trace event types
    "DAGUpdateEvent",
    "StepTraceEvent",
    "MemoryScoreEvent",
]
