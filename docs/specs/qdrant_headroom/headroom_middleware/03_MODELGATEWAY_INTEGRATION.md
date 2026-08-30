# ModelGateway Integration — _prepare_messages()

**File**: `src/omega/oracle/model_gateway.py`  
**Section**: 03 of 10  
**Priority**: P1 — Core integration point for tool output compression  

---

## Current _prepare_messages() (Before)

```python
# src/omega/oracle/model_gateway.py (current)
async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
    """Prepare messages for provider — token counting, truncation, formatting."""
    # 1. Convert to provider format
    formatted = self._format_messages(messages)
    
    # 2. Count tokens
    token_count = await self._count_tokens(formatted)
    
    # 3. Truncate if exceeds model context
    if token_count > self.max_context_tokens:
        formatted = await self._truncate_messages(formatted, token_count)
    
    return formatted
```

---

## Modified _prepare_messages() (After)

```python
# src/omega/oracle/model_gateway.py (modified)
from omega.oracle.middleware.headroom import HeadroomMiddleware, HeadroomMiddlewareConfig
from omega.config import get_config


class ModelGateway:
    def __init__(
        self,
        providers: List[BaseProvider],
        provider_registry: ProviderRegistry,
        config: Optional[ModelGatewayConfig] = None,
    ):
        # ... existing init ...
        
        # Headroom Middleware (lazy initialization)
        self._headroom_middleware: Optional[HeadroomMiddleware] = None
        self._headroom_config = self._load_headroom_config()
    
    def _load_headroom_config(self) -> HeadroomMiddlewareConfig:
        """Load Headroom config from config/headroom.yaml with env overrides."""
        from omega.config.headroom import HeadroomYamlConfig
        yaml_config = HeadroomYamlConfig.load()
        return yaml_config.to_middleware_config()
    
    async def _ensure_headroom_initialized(self) -> None:
        """Lazy initialization of Headroom middleware."""
        if self._headroom_middleware is None:
            self._headroom_middleware = HeadroomMiddleware(self._headroom_config)
            await self._headroom_middleware.initialize()
    
    async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
        """
        Prepare messages for provider — with Headroom compression.
        
        Pipeline:
        1. Headroom compression (tool outputs, logs, search results, code)
        2. Token counting on COMPRESSED messages
        3. Truncation if needed
        4. Provider-specific formatting
        """
        # 1. Headroom compression BEFORE token counting (critical for savings)
        if self._headroom_middleware is not None:
            try:
                messages = await self._headroom_middleware.compress_messages(messages)
            except Exception as e:
                # M23 Failure Integrity: log and continue with uncompressed
                import logging
                logger = logging.getLogger("omega.model_gateway")
                logger.warning(f"Headroom compression failed in _prepare_messages: {e}")
                # Fall through to uncompressed path
        
        # 2. Convert to provider format
        formatted = self._format_messages(messages)
        
        # 3. Count tokens on COMPRESSED messages
        token_count = await self._count_tokens(formatted)
        
        # 4. Truncate if exceeds model context (protects recent turns already done by Headroom)
        if token_count > self.max_context_tokens:
            formatted = await self._truncate_messages(formatted, token_count)
        
        return formatted
    
    async def shutdown(self) -> None:
        """Cleanup Headroom middleware on gateway shutdown."""
        if self._headroom_middleware:
            await self._headroom_middleware.shutdown()
            self._headroom_middleware = None
        # ... existing shutdown ...
```

---

## Integration Points Detail

### 1. Initialization Timing

```python
# Option A: Eager initialization (in __init__)
async def __init__(self, ...):
    # ...
    self._headroom_middleware = HeadroomMiddleware(self._headroom_config)
    await self._headroom_middleware.initialize()

# Option B: Lazy initialization (RECOMMENDED - avoids startup delay)
async def _ensure_headroom_initialized(self):
    if self._headroom_middleware is None:
        self._headroom_middleware = HeadroomMiddleware(self._headroom_config)
        await self._headroom_middleware.initialize()

# Called at start of _prepare_messages()
```

**Recommendation**: Lazy initialization (Option B) — Headroom only initializes on first inference request.

### 2. Message Flow

```
User Prompt
    │
    ▼
Oracle.talk() / Oracle.summon()
    │
    ▼
ModelGateway._prepare_messages(messages)
    │
    ├─► HeadroomMiddleware.compress_messages(messages)
    │       │
    │       ├─ Protect recent 2 turns (Carmack Q6.1)
    │       ├─ ContentRouter.compress(to_compress)
    │       │       ├─ SmartCrusher (JSON tool outputs)
    │       │       ├─ LogCompressor (Hivemind/logs)
    │       │       ├─ SearchCompressor (RAG results)
    │       │       ├─ CodeAwareCompressor (GitHub diffs)
    │       │       └─ CacheAligner (KV cache prefix)
    │       ├─ Store originals in CCR (if enabled)
    │       └─ Return compressed + protected
    │
    ▼
Token counting on COMPRESSED messages
    │
    ▼
Truncation if needed (max_context_tokens)
    │
    ▼
Provider-specific formatting
    │
    ▼
Provider.generate()
```

### 3. Token Counting Impact

**Before Headroom**: Token count includes full tool outputs (often 10K-50K tokens)
**After Headroom**: Token count on compressed messages (60-95% reduction)

```python
# Example: Tool output compression impact
# Raw tool output: 50,000 tokens
# After SmartCrusher: ~6,200 tokens (87.6% reduction)
# Token counting sees 6,200 instead of 50,000
# → No truncation needed, full context preserved
```

---

## Configuration for ModelGateway

```yaml
# config/headroom.yaml — ModelGateway section
headroom:
  omega:
    model_gateway:
      protect_recent_turns: 2           # Never compress last 2 turns
      compress_tool_outputs: true       # SmartCrusher on tool results
      compress_logs: true               # LogCompressor on Hivemind/logs
      compress_search_results: true     # SearchCompressor on RAG
      compress_code: true               # CodeAware on GitHub diffs
```

---

## Provider-Specific Considerations

### Local Providers (native-gguf, LM Studio, Ollama)
- **Maximum benefit**: Token generation ~50ms/1K tokens on Ryzen 5700U
- 50K tokens saved = ~2.5s generation time saved
- Headroom overhead: 5-15ms → **Net win: ~2.48s per request**

### Cloud Providers (Google, OpenRouter, OpenCode Zen)
- **Benefit**: Reduced input token costs, faster processing
- Headroom overhead still minimal vs network latency

### Streaming Providers
- Compression happens BEFORE streaming starts
- No impact on chunk-level streaming

---

## Error Handling in ModelGateway

```python
async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
    # Headroom compression with full error isolation
    if self._headroom_middleware is not None:
        try:
            await self._ensure_headroom_initialized()
            messages = await self._headroom_middleware.compress_messages(messages)
        except Exception as e:
            # M23: Never let Headroom failure break inference
            import logging
            logger = logging.getLogger("omega.model_gateway.headroom")
            logger.warning(
                "Headroom compression failed, using uncompressed messages",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "message_count": len(messages),
                }
            )
            # Continue with original messages
    
    # ... rest of pipeline ...
```

---

## Testing the Integration

```python
# tests/test_headroom_model_gateway.py
import pytest
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.middleware.headroom import HeadroomMiddleware


@pytest.mark.asyncio
async def test_model_gateway_headroom_compression():
    """ModelGateway._prepare_messages compresses tool outputs."""
    gateway = ModelGateway(providers=[], provider_registry=...)
    
    # Mock messages with large tool output
    messages = [
        {"role": "user", "content": "Analyze this data"},
        {"role": "assistant", "content": "", "tool_calls": [
            {"function": {"name": "search", "arguments": "..."}, "id": "call_1"}
        ]},
        {"role": "tool", "content": "x" * 50000, "tool_call_id": "call_1"},  # 50K chars
    ]
    
    # Initialize Headroom
    await gateway._ensure_headroom_initialized()
    
    # Prepare messages (triggers compression)
    compressed = await gateway._prepare_messages(messages)
    
    # Verify compression occurred
    tool_msg = next(m for m in compressed if m.get("role") == "tool")
    assert len(tool_msg["content"]) < 50000  # Compressed
    assert len(tool_msg["content"]) > 1000   # Not over-compressed


@pytest.mark.asyncio
async def test_model_gateway_headroom_fallback():
    """ModelGateway falls back gracefully if Headroom fails."""
    gateway = ModelGateway(providers=[], provider_registry=...)
    
    # Break Headroom by not initializing
    gateway._headroom_middleware = None
    
    messages = [{"role": "user", "content": "hello"}]
    result = await gateway._prepare_messages(messages)
    
    # Should return original messages unchanged
    assert result == messages


@pytest.mark.asyncio
async def test_model_gateway_protects_recent_turns():
    """Recent N turns are protected from compression."""
    gateway = ModelGateway(providers=[], provider_registry=...)
    await gateway._ensure_headroom_initialized()
    
    messages = [
        {"role": "user", "content": "old message " + "x" * 10000},
        {"role": "assistant", "content": "old response " + "y" * 10000},
        {"role": "user", "content": "recent message"},      # Turn -2
        {"role": "assistant", "content": "recent response"}, # Turn -1 (protected)
    ]
    
    compressed = await gateway._prepare_messages(messages)
    
    # Last 2 turns should be unchanged
    assert compressed[-2]["content"] == "recent message"
    assert compressed[-1]["content"] == "recent response"
    
    # First 2 turns should be compressed
    assert len(compressed[0]["content"]) < len(messages[0]["content"])
    assert len(compressed[1]["content"]) < len(messages[1]["content"])
```

---

## Metrics Export (OTel)

```python
# In ModelGateway after _prepare_messages
async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
    # ... compression ...
    
    # Export Headroom metrics to OTel
    if self._headroom_middleware and self._headroom_config.enable_metrics:
        metrics = self._headroom_middleware.get_metrics()
        self._export_headroom_metrics(metrics)
    
    return formatted


def _export_headroom_metrics(self, metrics: dict):
    """Export Headroom metrics to OpenTelemetry."""
    from opentelemetry import metrics
    
    meter = metrics.get_meter("omega.headroom")
    
    # Compression ratio gauge
    ratio_gauge = meter.create_gauge(
        "headroom.compression_ratio",
        description="Average compression ratio (compressed/original)",
    )
    ratio_gauge.set(metrics["average_compression_ratio"])
    
    # Latency histogram
    latency_hist = meter.create_histogram(
        "headroom.latency_ms",
        description="Headroom compression latency in milliseconds",
    )
    latency_hist.record(metrics["average_latency_ms"])
    
    # Fallback counter
    fallback_counter = meter.create_counter(
        "headroom.fallback_total",
        description="Total number of Headroom fallbacks to uncompressed",
    )
    fallback_counter.add(metrics["fallback_count"])
    
    # Error counter
    error_counter = meter.create_counter(
        "headroom.error_total",
        description="Total number of Headroom errors",
    )
    error_counter.add(metrics["error_count"])
```

---

## Shutdown Sequence

```python
# In ModelGateway.shutdown()
async def shutdown(self) -> None:
    # 1. Shutdown Headroom middleware (flushes CCR, closes connections)
    if self._headroom_middleware:
        await self._headroom_middleware.shutdown()
        self._headroom_middleware = None
    
    # 2. Shutdown providers
    for provider in self.providers:
        await provider.shutdown()
    
    # 3. Close provider registry
    await self.provider_registry.close()
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 03/10*