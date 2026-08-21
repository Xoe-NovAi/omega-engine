# Error Handling & Metrics — Fallback Logic + OTel Metrics

**Section**: 09 of 10  
**Priority**: P1 — Failure integrity (M23) + Temple-Grade observability (M13 T9)  

---

## Error Handling Philosophy (M23 Failure Integrity)

> **Mandate**: No "soft-failures" or simulated rigor. If Headroom fails, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]` — OR gracefully fallback to uncompressed with full observability.

**Our Approach**: Graceful fallback with **full observability** — log every fallback, export metrics, never silently swallow errors.

---

## Fallback Strategy Matrix

| Failure Point | Detection | Fallback Action | Logging | Metrics |
|---------------|-----------|-----------------|---------|---------|
| Headroom not installed | ImportError at init | Disable middleware, log warning | WARNING | `headroom.disabled=1` |
| ContentRouter.compress() fails | Exception | Try SmartCrusher fallback → return original | WARNING + error details | `headroom.fallback_total++` |
| CCR store unavailable | Exception | Continue without CCR (compression still works) | WARNING | `headroom.ccr.unavailable=1` |
| Operation timeout (5s) | anyio timeout | Return original, increment fallback counter | WARNING + latency | `headroom.timeout_total++` |
| Any other exception | Exception | Return original, increment error counter | ERROR + traceback | `headroom.error_total++` |

---

## Timeout Implementation (M23)

```python
# In HeadroomMiddleware.compress_messages()
async def compress_messages(self, messages: List[Message]) -> List[Message]:
    start_time = time.perf_counter()
    
    try:
        # ... compression logic ...
        
        # Check timeout
        elapsed = time.perf_counter() - start_time
        if elapsed > self.config.operation_timeout_seconds:
            raise TimeoutError(f"Headroom compression exceeded {self.config.operation_timeout_seconds}s")
        
        return compressed + protected
        
    except TimeoutError:
        # Explicit timeout handling
        self._metrics["fallback_count"] += 1
        self._metrics["timeout_count"] = self._metrics.get("timeout_count", 0) + 1
        
        logger.warning(
            "Headroom compression timeout, falling back to uncompressed",
            extra={
                "timeout_seconds": self.config.operation_timeout_seconds,
                "elapsed_seconds": elapsed,
                "message_count": len(messages),
            }
        )
        return messages
        
    except Exception as e:
        # General exception handling
        self._metrics["fallback_count"] += 1
        self._metrics["error_count"] += 1
        
        logger.warning(
            "Headroom compression failed, falling back to uncompressed",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "latency_ms": (time.perf_counter() - start_time) * 1000,
                "message_count": len(messages),
            }
        )
        return messages
```

---

## Comprehensive Error Handling in All Components

### HeadroomMiddleware

```python
async def compress_messages(self, messages: List[Message]) -> List[Message]:
    """Main entry point with full error isolation."""
    if not self._initialized:
        try:
            await self.initialize()
        except Exception as e:
            logger.error(f"Headroom initialization failed: {e}")
            self._disabled = True
            return messages
    
    if getattr(self, '_disabled', False):
        return messages
    
    # ... compression with timeout and fallback ...
```

### RetrievalCompressor

```python
async def search_and_compress(self, query: str, entity_name: str, top_k: int = 10, filters: Optional[Dict] = None):
    try:
        # ... compression pipeline ...
    except Exception as e:
        self._metrics["fallback_count"] += 1
        logger.warning(f"Retrieval compression failed: {e}")
        # Fallback: uncompressed search
        raw = await self.memory_store.search(query, entity_name, top_k, filters)
        return self._to_compressed_chunks(raw, raw)
```

### MCPToolCompressor

```python
async def compress_tool_schemas(self, tools: List[Dict]) -> List[Dict]:
    try:
        return await anyio.to_thread.run_sync(self._crusher.compress, tools)
    except Exception as e:
        self._metrics["fallback_count"] += 1
        logger.warning(f"MCP tool schema compression failed: {e}")
        return tools
```

### EntityContextCompressor

```python
async def compress_entity_context(self, context: Dict) -> Dict:
    try:
        # ... compression ...
    except Exception as e:
        self._metrics["fallback_count"] += 1
        logger.warning(f"Entity context compression failed: {e}")
        return context
```

### CCRStore

```python
async def store(self, original: str, compressed: str, **kwargs) -> str:
    try:
        # ... store logic ...
    except Exception as e:
        logger.error(f"CCR store failed: {e}")
        # Don't raise — CCR is optional enhancement
        return ""  # Empty ref means "no CCR available"

async def retrieve(self, key: str) -> Optional[str]:
    try:
        # ... retrieve logic ...
    except Exception as e:
        logger.error(f"CCR retrieve failed for {key}: {e}")
        return None  # Graceful degradation
```

---

## OpenTelemetry Metrics Export

### Metric Definitions

```python
# src/omega/observability/headroom_metrics.py
from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation


class HeadroomMetrics:
    """OpenTelemetry metrics for Headroom compression."""
    
    def __init__(self, meter_name: str = "omega.headroom"):
        self.meter = metrics.get_meter(meter_name)
        self._register_metrics()
    
    def _register_metrics(self):
        # Compression ratio gauge (updated via callback)
        self.compression_ratio = self.meter.create_gauge(
            name="headroom.compression_ratio",
            description="Average compression ratio (compressed/original tokens)",
            unit="ratio",
        )
        
        # Latency histogram
        self.latency_histogram = self.meter.create_histogram(
            name="headroom.latency_ms",
            description="Headroom compression latency in milliseconds",
            unit="ms",
        )
        
        # Fallback counter
        self.fallback_counter = self.meter.create_counter(
            name="headroom.fallback_total",
            description="Total number of Headroom fallbacks to uncompressed",
            unit="count",
        )
        
        # Error counter
        self.error_counter = self.meter.create_counter(
            name="headroom.error_total",
            description="Total number of Headroom errors",
            unit="count",
        )
        
        # Timeout counter
        self.timeout_counter = self.meter.create_counter(
            name="headroom.timeout_total",
            description="Total number of Headroom operation timeouts",
            unit="count",
        )
        
        # Disabled gauge (1 if Headroom unavailable)
        self.disabled_gauge = self.meter.create_gauge(
            name="headroom.disabled",
            description="Whether Headroom middleware is disabled (1) or enabled (0)",
            unit="count",
        )
        
        # CCR availability
        self.ccr_available = self.meter.create_gauge(
            name="headroom.ccr.available",
            description="Whether CCR store is available (1) or unavailable (0)",
            unit="count",
        )
        
        # Per-compressor metrics
        self.compressor_ratio = self.meter.create_gauge(
            name="headroom.compressor.ratio",
            description="Compression ratio by compressor type",
            unit="ratio",
        )
        
        self.compressor_latency = self.meter.create_histogram(
            name="headroom.compressor.latency_ms",
            description="Latency by compressor type",
            unit="ms",
        )
        
        self.compressor_count = self.meter.create_counter(
            name="headroom.compressor.count",
            description="Number of compressions by compressor type",
            unit="count",
        )
    
    def record_compression(
        self,
        compressor: str,
        original_tokens: int,
        compressed_tokens: int,
        latency_ms: float,
        fallback: bool = False,
        timeout: bool = False,
        error: bool = False,
    ):
        """Record a compression operation."""
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        
        # Overall metrics
        self.latency_histogram.record(latency_ms)
        
        if fallback:
            self.fallback_counter.add(1, {"compressor": compressor})
        if timeout:
            self.timeout_counter.add(1, {"compressor": compressor})
        if error:
            self.error_counter.add(1, {"compressor": compressor, "error_type": "compression"})
        
        # Per-compressor metrics
        self.compressor_ratio.set(ratio, {"compressor": compressor})
        self.compressor_latency.record(latency_ms, {"compressor": compressor})
        self.compressor_count.add(1, {"compressor": compressor})
    
    def record_ccr_operation(
        self,
        operation: str,  # "store" | "retrieve"
        success: bool,
        latency_ms: float,
    ):
        """Record CCR store operation."""
        self.meter.create_histogram(
            name=f"headroom.ccr.{operation}.latency_ms",
            description=f"CCR {operation} latency",
            unit="ms",
        ).record(latency_ms)
        
        self.meter.create_counter(
            name=f"headroom.ccr.{operation}.total",
            description=f"CCR {operation} operations",
            unit="count",
        ).add(1, {"success": str(success).lower()})
    
    def set_disabled(self, disabled: bool):
        """Set disabled status."""
        self.disabled_gauge.set(1 if disabled else 0)
    
    def set_ccr_available(self, available: bool):
        """Set CCR availability."""
        self.ccr_available.set(1 if available else 0)
```

---

## Integration with Components

### HeadroomMiddleware Metrics Export

```python
# In HeadroomMiddleware.__init__()
from omega.observability.headroom_metrics import HeadroomMetrics

class HeadroomMiddleware:
    def __init__(self, config: Optional[HeadroomMiddlewareConfig] = None):
        # ... existing init ...
        self._otel_metrics = HeadroomMetrics()
    
    def _update_metrics(self, original, compressed, latency_ms, compressor, fallback):
        # ... existing internal metrics ...
        
        # Export to OTel
        orig_tokens = sum(len(str(m.get("content", ""))) // 4 for m in original)
        comp_tokens = sum(len(str(m.get("content", ""))) // 4 for m in compressed)
        
        self._otel_metrics.record_compression(
            compressor=compressor,
            original_tokens=orig_tokens,
            compressed_tokens=comp_tokens,
            latency_ms=latency_ms,
            fallback=fallback,
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        # ... existing metrics ...
        return {
            # ... existing ...
            "otel_exported": True,
        }
```

### ModelGateway Integration

```python
# In ModelGateway._prepare_messages()
async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
    if self._headroom_middleware:
        try:
            await self._ensure_headroom_initialized()
            messages = await self._headroom_middleware.compress_messages(messages)
        except Exception as e:
            logger.warning(f"Headroom compression failed: {e}")
            # Metrics already recorded in middleware
    
    # Export Headroom metrics after each request
    if self._headroom_middleware and self._headroom_config.enable_metrics:
        metrics = self._headroom_middleware.get_metrics()
        # Metrics are auto-exported via OTel callbacks
    
    return formatted
```

---

## Prometheus/Grafana Dashboard Queries

```promql
# Headroom compression ratio (avg over 5m)
avg_over_time(headroom_compression_ratio[5m])

# Headroom latency p99
histogram_quantile(0.99, rate(headroom_latency_ms_bucket[5m]))

# Fallback rate (fallbacks per minute)
rate(headroom_fallback_total[1m])

# Error rate
rate(headroom_error_total[1m])

# Timeout rate
rate(headroom_timeout_total[1m])

# Per-compressor ratio
headroom_compressor_ratio

# Per-compressor latency p99
histogram_quantile(0.99, rate(headroom_compressor_latency_ms_bucket[5m]))

# CCR store operations
rate(headroom_ccr_store_total[1m])
rate(headroom_ccr_retrieve_total[1m])

# Headroom disabled status
headroom_disabled

# CCR availability
headroom_ccr_available
```

---

## Alerting Rules

```yaml
# prometheus/alerts/headroom.yml
groups:
- name: headroom
  rules:
  - alert: HeadroomHighFallbackRate
    expr: rate(headroom_fallback_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Headroom fallback rate > 10% for 5 minutes"
      description: "Headroom is frequently falling back to uncompressed. Check logs for errors."
  
  - alert: HeadroomHighErrorRate
    expr: rate(headroom_error_total[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Headroom error rate > 5%"
      description: "Headroom compression is failing frequently. May indicate library issue."
  
  - alert: HeadroomHighLatency
    expr: histogram_quantile(0.99, rate(headroom_latency_ms_bucket[5m])) > 100
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Headroom p99 latency > 100ms"
      description: "Headroom compression is adding significant latency. Consider disabling aggressive compressors."
  
  - alert: HeadroomDisabled
    expr: headroom_disabled == 1
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Headroom middleware is disabled"
      description: "Headroom failed to initialize. Compression unavailable."
  
  - alert: CCRStoreUnavailable
    expr: headroom_ccr_available == 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CCR store unavailable"
      description: "Cross-agent reversible memory store is down. Original content retrieval disabled."
  
  - alert: CCRStoreDiskUsageHigh
    expr: headroom_ccr_disk_usage_gb / headroom_ccr_max_size_gb > 0.8
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "CCR store disk usage > 80%"
      description: "CCR store approaching size limit. Cleanup may not be keeping up."
```

---

## Health Check Endpoint

```python
# src/omega/api/health.py (addition)

async def headroom_health_check() -> Dict[str, Any]:
    """Health check for Headroom middleware."""
    from omega.oracle.model_gateway import get_model_gateway
    
    gateway = get_model_gateway()
    headroom = gateway._headroom_middleware
    
    if not headroom:
        return {
            "status": "disabled",
            "reason": "Headroom middleware not initialized",
        }
    
    if getattr(headroom, '_disabled', False):
        return {
            "status": "degraded",
            "reason": "Headroom initialization failed",
        }
    
    # Test compression
    try:
        test_msg = [{"role": "user", "content": "test"}]
        start = time.perf_counter()
        await headroom.compress_messages(test_msg)
        latency_ms = (time.perf_counter() - start) * 1000
        
        metrics = headroom.get_metrics()
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "total_compressions": metrics["total_compressions"],
            "avg_compression_ratio": metrics["average_compression_ratio"],
            "fallback_rate": (
                metrics["fallback_count"] / metrics["total_compressions"]
                if metrics["total_compressions"] > 0 else 0
            ),
            "ccr_available": headroom._ccr is not None,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "reason": f"Health check compression failed: {e}",
        }
```

---

## Logging Standards

```python
# Structured logging for Headroom operations
import logging
import json

logger = logging.getLogger("omega.headroom")

# Compression success
logger.info(
    "Headroom compression completed",
    extra={
        "compressor": "ContentRouter",
        "original_tokens": 50000,
        "compressed_tokens": 6200,
        "ratio": 0.124,
        "latency_ms": 15.2,
        "protected_turns": 2,
    }
)

# Fallback
logger.warning(
    "Headroom compression fallback",
    extra={
        "reason": "timeout",
        "timeout_seconds": 5.0,
        "elapsed_seconds": 5.1,
        "fallback_count": 3,
    }
)

# Error
logger.error(
    "Headroom compression error",
    extra={
        "error": "Connection refused",
        "error_type": "ConnectionError",
        "compressor": "SmartCrusher",
        "traceback": traceback.format_exc(),
    }
)
```

---

## Testing Error Scenarios

```python
# tests/test_headroom_error_handling.py

@pytest.mark.asyncio
async def test_headroom_timeout_fallback():
    """Headroom falls back on timeout."""
    config = HeadroomMiddlewareConfig(operation_timeout_seconds=0.001)  # 1ms timeout
    middleware = HeadroomMiddleware(config)
    await middleware.initialize()
    
    # Large content that will take >1ms
    messages = [{"role": "user", "content": "x" * 100000}]
    
    result = await middleware.compress_messages(messages)
    
    # Should return original (fallback)
    assert result == messages
    assert middleware._metrics["fallback_count"] == 1
    assert middleware._metrics.get("timeout_count", 0) == 1


@pytest.mark.asyncio
async def test_headroom_import_error_disables():
    """Headroom disables gracefully if not installed."""
    # Mock import failure
    with patch("omega.oracle.middleware.headroom.ContentRouter", side_effect=ImportError):
        middleware = HeadroomMiddleware()
        await middleware.initialize()
        
        messages = [{"role": "user", "content": "test"}]
        result = await middleware.compress_messages(messages)
        
        assert result == messages
        assert middleware._disabled is True


@pytest.mark.asyncio
async def test_ccr_failure_doesnt_break_compression():
    """CCR failure doesn't break compression."""
    middleware = HeadroomMiddleware()
    middleware._ccr = AsyncMock(side_effect=Exception("CCR down"))
    
    messages = [{"role": "user", "content": "test"}]
    result = await middleware.compress_messages(messages)
    
    # Compression should still work
    assert result is not None
    assert len(result) == 1
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 09/10*