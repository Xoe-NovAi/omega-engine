# 🔱 omega-vetala — Trace Propagation
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ TRACING
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake3-1999] netchan — trace_id as a message-channel identifier
#
"""Distributed trace context propagation for the moderation system.

Uses ``contextvars`` (fully compatible with ``anyio``) to carry the
current trace through async boundaries without explicit parameter
passing.  A ``@traced`` decorator allows any callable to be wrapped
with timing and span tracking.

Trace structure::

    RootSpan (trace_id=A, span_id=1)
    ├── Span "check_moderation" (trace_id=A, span_id=2, parent=1)
    │   ├── Span "perspective.analyze" (trace_id=A, span_id=3, parent=2)
    │   └── Span "log_decision" (trace_id=A, span_id=4, parent=2)
    └── Span "record_metrics" (trace_id=A, span_id=5, parent=1)
"""

from __future__ import annotations

import functools
import time
import uuid
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Context variable — carries the active trace through async boundaries
# ---------------------------------------------------------------------------

_current_trace: ContextVar[TraceContext | None] = ContextVar(
    "moderation_current_trace", default=None
)


# ---------------------------------------------------------------------------
# Span and trace data structures
# ---------------------------------------------------------------------------

@dataclass
class Span:
    """A single span within a trace.

    Attributes:
        operation: Name of the traced operation.
        span_id: Unique 16-hex-char identifier for this span.
        parent_span_id: Span ID of the parent span (empty for root).
        start_time: ``time.monotonic()`` when the span started.
        duration_ms: Duration in milliseconds (set on exit).
        success: Whether the operation completed without exception.
        error: Error message if the operation failed.
    """

    operation: str = ""
    span_id: str = ""
    parent_span_id: str = ""
    start_time: float = 0.0
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""


@dataclass
class TraceContext:
    """Holds the current trace state and accumulated spans.

    Attributes:
        trace_id: Unique identifier for the entire trace.
        current_span_id: The most recently entered span.
        spans: List of all spans in this trace.
    """

    trace_id: str = ""
    current_span_id: str = ""
    spans: list[Span] = field(default_factory=list)

    def new_span(self, operation: str) -> str:
        """Create a new span under the current span.

        Args:
            operation: Name for the new span.

        Returns:
            The new span's ID.
        """
        span_id = uuid.uuid4().hex[:16]
        parent = self.current_span_id
        self.spans.append(Span(
            operation=operation,
            span_id=span_id,
            parent_span_id=parent,
            start_time=time.monotonic(),
        ))
        self.current_span_id = span_id
        return span_id

    def end_span(self, span_id: str, *, success: bool = True, error: str = "") -> None:
        """Complete a span by recording its duration.

        Args:
            span_id: The span to close.
            success: Whether the operation succeeded.
            error: Error message if it failed.
        """
        now = time.monotonic()
        for span in self.spans:
            if span.span_id == span_id:
                span.duration_ms = (now - span.start_time) * 1000
                span.success = success
                span.error = error
                # Restore parent as current
                self.current_span_id = span.parent_span_id
                break

    def export(self) -> dict[str, Any]:
        """Export the trace as a JSON-serialisable dict.

        Returns:
            Dict with ``trace_id`` and a ``spans`` list.
        """
        return {
            "trace_id": self.trace_id,
            "spans": [
                {
                    "operation": s.operation,
                    "span_id": s.span_id,
                    "parent_span_id": s.parent_span_id,
                    "duration_ms": round(s.duration_ms, 2),
                    "success": s.success,
                    "error": s.error,
                }
                for s in self.spans
            ],
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_trace() -> TraceContext:
    """Initialise a new root trace and set it as the current context.

    Returns:
        A new :class:`TraceContext` with a fresh trace_id.
    """
    ctx = TraceContext(
        trace_id=uuid.uuid4().hex[:16],
        current_span_id=uuid.uuid4().hex[:16],
    )
    # Root span
    ctx.spans.append(Span(
        operation="root",
        span_id=ctx.current_span_id,
        start_time=time.monotonic(),
    ))
    _current_trace.set(ctx)
    return ctx


def get_current_trace() -> TraceContext | None:
    """Retrieve the active trace context (or ``None``)."""
    return _current_trace.get()


def clear_trace() -> None:
    """Clear the current trace context."""
    _current_trace.set(None)


def within_trace(trace: TraceContext) -> None:
    """Set *trace* as the current context.

    This is useful when resuming a trace across async boundaries
    (e.g., in a worker task spawned from a parent).

    Args:
        trace: The :class:`TraceContext` to activate.
    """
    _current_trace.set(trace)


# ---------------------------------------------------------------------------
# traced decorator
# ---------------------------------------------------------------------------

def traced(operation: str) -> Callable[[F], F]:
    """Decorator that wraps a callable with span tracing.

    The decorator reads the current :class:`TraceContext` from contextvars,
    creates a child span for *operation*, calls the wrapped function, and
    records duration and success/failure.

    Usage::

        @traced("perspective.analyze")
        async def analyze(self, text: str) -> ModerationResult:
            ...

    If no trace is active, the decorator is a no-op (the function is
    called directly without tracing overhead).

    Args:
        operation: Name for the span.

    Returns:
        A decorator.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            trace = get_current_trace()
            if trace is None:
                return await func(*args, **kwargs)

            span_id = trace.new_span(operation)
            try:
                result = await func(*args, **kwargs)
            except Exception as exc:
                trace.end_span(span_id, success=False, error=str(exc))
                raise
            else:
                trace.end_span(span_id, success=True)
                return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            trace = get_current_trace()
            if trace is None:
                return func(*args, **kwargs)

            span_id = trace.new_span(operation)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                trace.end_span(span_id, success=False, error=str(exc))
                raise
            else:
                trace.end_span(span_id, success=True)
                return result

        # Return the appropriate wrapper based on whether the function
        # is a coroutine function
        if _is_async(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


def _is_async(func: Callable[..., Any]) -> bool:
    """Check if *func* is an async callable.

    Args:
        func: The callable to inspect.

    Returns:
        ``True`` if the callable is a coroutine function.
    """
    import asyncio
    import inspect

    if asyncio.iscoroutinefunction(func):
        return True
    if hasattr(func, "__call__"):
        return asyncio.iscoroutinefunction(getattr(func, "__call__"))
    return inspect.iscoroutinefunction(func)


# ---------------------------------------------------------------------------
# Context manager for manual tracing
# ---------------------------------------------------------------------------

class trace_span:
    """Context manager that wraps a block of code in a trace span.

    Usage::

        with trace_span("db_query"):
            result = db.query(...)
    """

    def __init__(self, operation: str):
        self._operation = operation
        self._span_id: str = ""

    def __enter__(self) -> trace_span:
        trace = get_current_trace()
        if trace is not None:
            self._span_id = trace.new_span(self._operation)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._span_id:
            trace = get_current_trace()
            if trace is not None:
                trace.end_span(
                    self._span_id,
                    success=exc_type is None,
                    error=str(exc_val) if exc_val else "",
                )
