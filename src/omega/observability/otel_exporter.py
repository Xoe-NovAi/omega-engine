"""OTel GenAI Semantic Convention Exporter to SQLite WAL.
AP: AP-OTEL-EXPORTER-v1.0.0
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ OTEL-EXPORTER

Exports OpenTelemetry GenAI spans to the unified MetricsDB (SQLite WAL).
Implements GenAI semantic conventions: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md
"""

import anyio
import logging
import time
from typing import Any, Dict, Optional

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import Span, SpanContext, TraceFlags, TraceState
from opentelemetry.util.types import AttributeValue

from omega.observability.metrics_db import MetricsDB

logger = logging.getLogger(__name__)

# [M22 SSOT] Lazy ProviderRegistry singleton (imported lazily to avoid a
# circular import — see observability/__init__.py notes).
def _get_provider_registry():
    """Return the cached ProviderRegistry, constructing it on first use.
    Delegates to the process-wide singleton in provider_registry.py."""
    from omega.oracle.provider_registry import get_provider_registry
    return get_provider_registry()

# ── GenAI Semantic Convention Attributes ──────────────────────────────────
# Source: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md

GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_MODEL = "gen_ai.request.model"
GEN_AI_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_MAX_TOKENS = "gen_ai.request.max_tokens"
GEN_AI_TOP_P = "gen_ai.request.top_p"
GEN_AI_TOP_K = "gen_ai.request.top_k"
GEN_AI_STOP_SEQUENCES = "gen_ai.request.stop_sequences"
GEN_AI_PROMPT = "gen_ai.prompt"
GEN_AI_COMPLETION = "gen_ai.completion"
GEN_AI_USAGE_PROMPT_TOKENS = "gen_ai.usage.prompt_tokens"
GEN_AI_USAGE_COMPLETION_TOKENS = "gen_ai.usage.completion_tokens"
GEN_AI_USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens"
GEN_AI_RESPONSE_ID = "gen_ai.response.id"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_AGENT_ID = "gen_ai.agent.id"
GEN_AI_TOOL_CALL = "gen_ai.tool.call"


class OTelSQLiteExporter(SpanExporter):
    """Exports OTel spans to MetricsDB using GenAI semantic conventions."""
    
    def __init__(self, metrics_db: MetricsDB):
        self._metrics_db = metrics_db
        self._shutdown = False
    
    def export(self, spans) -> SpanExportResult:
        """Export spans to MetricsDB. Called by OTel SDK from background thread."""
        if self._shutdown:
            return SpanExportResult.SUCCESS
        
        try:
            for span in spans:
                # [M1 AnyIO] Bridge sync OTel SDK thread to async MetricsDB
                anyio.from_thread.run(self._export_span, span)
        except Exception as e:
            logger.error(f"OTel export failed: {e}")
            return SpanExportResult.FAILURE
        
        return SpanExportResult.SUCCESS
    
    async def _export_span(self, span: Span) -> None:
        """Export a single span to MetricsDB. [M1 AnyIO] Now async."""
        # Extract GenAI attributes
        attrs = dict(span.attributes) if span.attributes else {}
        
        # Determine if this is a GenAI span
        gen_ai_system = attrs.get(GEN_AI_SYSTEM)
        if not gen_ai_system:
            # Not a GenAI span, skip
            return
        
        trace_id = format(span.context.trace_id, '032x')
        span_id = format(span.context.span_id, '016x')
        
        # Extract key metrics
        provider = attrs.get(GEN_AI_SYSTEM, "unknown")
        model = attrs.get(GEN_AI_MODEL, "unknown")
        prompt_tokens = attrs.get(GEN_AI_USAGE_PROMPT_TOKENS, 0)
        completion_tokens = attrs.get(GEN_AI_USAGE_COMPLETION_TOKENS, 0)
        total_tokens = attrs.get(GEN_AI_USAGE_TOTAL_TOKENS, prompt_tokens + completion_tokens)
        
        # Calculate latency from span timing
        latency_ms = 0.0
        if span.end_time and span.start_time:
            latency_ms = (span.end_time - span.start_time) / 1_000_000  # ns to ms
        
        # Determine if cloud provider
        is_cloud = self._is_cloud_provider(provider)
        
        # Record to MetricsDB performance table
        await self._metrics_db.record_performance(
            latency_ms=latency_ms,
            provider=provider,
            model_used=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            is_cloud=is_cloud,
            trace_id=f"trc_{trace_id[:12]}",
        )
        
        # Also record as event for full traceability
        await self._metrics_db.record_event(
            event_type="gen_ai.span",
            trace_id=f"trc_{trace_id[:12]}",
            provider=provider,
            payload={
                "span_name": span.name,
                "span_id": span_id,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
                "is_cloud": is_cloud,
                "status": str(span.status.status_code),
                "attributes": {k: v for k, v in attrs.items() if not k.startswith("gen_ai.")},
            },
        )
    
    def _is_cloud_provider(self, provider: str) -> bool:
        """Determine if provider is cloud-based (delegates to ProviderRegistry SSOT)."""
        return _get_provider_registry().is_cloud(provider)
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        self._shutdown = True
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush - no-op for synchronous exporter."""
        return True


def setup_otel_exporter(metrics_db: MetricsDB) -> OTelSQLiteExporter:
    """Set up OTel TracerProvider with SQLite exporter.
    
    Returns the exporter instance for potential further configuration.
    """
    exporter = OTelSQLiteExporter(metrics_db)
    
    # Create tracer provider with batch processor
    provider = TracerProvider()
    processor = BatchSpanProcessor(
        exporter,
        max_queue_size=2048,
        max_export_batch_size=512,
        schedule_delay_millis=5000,
    )
    provider.add_span_processor(processor)
    
    # Set as global tracer provider
    from opentelemetry.trace import set_tracer_provider
    set_tracer_provider(provider)
    
    return exporter


def get_tracer(name: str = "omega"):
    """Get a tracer for the given name."""
    from opentelemetry.trace import get_tracer_provider
    return get_tracer_provider().get_tracer(name)


# ── Convenience Functions for GenAI Span Creation ──────────────────────────

def create_gen_ai_span(
    tracer,
    operation_name: str,
    provider: str,
    model: str,
    trace_id: Optional[str] = None,
    **kwargs
) -> Span:
    """Create a GenAI span with standard attributes.
    
    Args:
        tracer: OTel tracer instance
        operation_name: Operation name (e.g., "chat", "completion", "embedding")
        provider: Provider name (e.g., "native-gguf", "google", "openrouter")
        model: Model name
        trace_id: Optional trace ID to continue
        **kwargs: Additional GenAI attributes (temperature, max_tokens, etc.)
    
    Returns:
        Started span with GenAI attributes set
    """
    span_name = f"gen_ai.{operation_name}"
    
    # Build attributes
    attributes = {
        GEN_AI_SYSTEM: provider,
        GEN_AI_MODEL: model,
        GEN_AI_OPERATION_NAME: operation_name,
    }
    
    # Add optional GenAI request parameters
    if "temperature" in kwargs:
        attributes[GEN_AI_TEMPERATURE] = kwargs["temperature"]
    if "max_tokens" in kwargs:
        attributes[GEN_AI_MAX_TOKENS] = kwargs["max_tokens"]
    if "top_p" in kwargs:
        attributes[GEN_AI_TOP_P] = kwargs["top_p"]
    if "top_k" in kwargs:
        attributes[GEN_AI_TOP_K] = kwargs["top_k"]
    if "stop_sequences" in kwargs:
        attributes[GEN_AI_STOP_SEQUENCES] = kwargs["stop_sequences"]
    
    # Add agent/entity context if available
    if "entity" in kwargs:
        attributes[GEN_AI_AGENT_ID] = kwargs["entity"]
    
    # Create span context if trace_id provided
    context = None
    if trace_id:
        # Parse trace_id (format: trc_xxxxxxxxxxxx)
        tid = trace_id.replace("trc_", "")
        if len(tid) == 12:
            tid = tid + "00000000000000000000"  # pad to 32 hex chars
        trace_id_int = int(tid, 16)
        span_context = SpanContext(
            trace_id=trace_id_int,
            span_id=0,  # will be generated
            is_remote=False,
            trace_flags=TraceFlags(TraceFlags.SAMPLED),
            trace_state=TraceState(),
        )
        from opentelemetry.trace import set_span_in_context
        context = set_span_in_context(
            Span(span_context=span_context)  # dummy span for context
        )
    
    span = tracer.start_span(span_name, attributes=attributes, context=context)
    return span


def end_gen_ai_span(
    span: Span,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    response_id: Optional[str] = None,
    prompt: Optional[str] = None,
    completion: Optional[str] = None,
    error: Optional[Exception] = None,
) -> None:
    """End a GenAI span with usage and response attributes.
    
    Args:
        span: The span to end
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        response_id: Provider response ID
        prompt: The prompt text (optional, for debugging)
        completion: The completion text (optional, for debugging)
        error: Error if the operation failed
    """
    if not span or not span.is_recording():
        return
    
    total_tokens = prompt_tokens + completion_tokens
    
    # Set usage attributes
    span.set_attribute(GEN_AI_USAGE_PROMPT_TOKENS, prompt_tokens)
    span.set_attribute(GEN_AI_USAGE_COMPLETION_TOKENS, completion_tokens)
    span.set_attribute(GEN_AI_USAGE_TOTAL_TOKENS, total_tokens)
    
    if response_id:
        span.set_attribute(GEN_AI_RESPONSE_ID, response_id)
    
    # Optionally record prompt/completion (can be large, use with caution)
    if prompt:
        span.set_attribute(GEN_AI_PROMPT, prompt[:1000])  # truncate
    if completion:
        span.set_attribute(GEN_AI_COMPLETION, completion[:1000])  # truncate
    
    # Set status
    if error:
        span.record_exception(error)
        span.set_status(Status(StatusCode.ERROR, str(error)))
    else:
        span.set_status(Status(StatusCode.OK))
    
    span.end()


# Import Status for end_gen_ai_span
from opentelemetry.trace import Status, StatusCode, set_span_in_context