# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Contextvars-based trace_id propagation for AnyIO
# AP: AP-TRACE-ID-FIX-v1.0.0
#
# Provides a zero-dependency safety net that works alongside
# OpenTelemetry AnyIO instrumentation. Falls back to contextvars
# when OTel is not available.
#
# [M8 Zero Telemetry] No external export — purely local context propagation.
# [M22 Response Provenance] Ensures trace_id is always available for
# observability logging, even when async boundaries drop explicit args.
#
# Usage:
#   from omega.observability.context import get_current_trace_id, set_current_trace_id
#   trace_id = get_current_trace_id()  # Returns existing or generates new
#   set_current_trace_id("trc_abc123")  # Explicitly set for child tasks


# DocRef: docs/explanation/metrics-pipeline.md
import contextvars
import uuid
from typing import Optional

# Context variable for trace_id propagation across async boundaries
_current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_trace_id", default=None
)


def get_current_trace_id() -> str:
    """Get current trace_id or generate a new one.

    This is the central function that all subsystems should call
    to obtain the current trace context. It's the safety net when
    context hasn't been explicitly propagated across async boundaries.

    Returns:
        A trace_id string starting with 'trc_'.
    """
    tid = _current_trace_id.get()
    if tid is None:
        tid = f"trc_{uuid.uuid4().hex[:12]}"
        _current_trace_id.set(tid)
    return tid


def set_current_trace_id(trace_id: str) -> None:
    """Set trace_id in current context.

    Called at the start of an async operation to establish
    the trace context for all child tasks.

    Args:
        trace_id: The trace ID string to set.
    """
    _current_trace_id.set(trace_id)


def reset_current_trace_id() -> None:
    """Reset the current trace_id to None.

    Useful for testing and for cleanly starting new trace contexts.
    """
    _current_trace_id.set(None)
