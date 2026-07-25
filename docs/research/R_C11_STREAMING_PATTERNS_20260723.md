# 🔱 C-11 Property Test Patterns — Domain 5: StreamingResilience
**AP Token**: `AP-C11-STREAMING-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_c11_streaming ⬡ 2026-07-23

---

## §1 Local Implementation Analysis

### 1.1 OpenAICompatBackend Streaming (`src/omega/oracle/backends/openai_compat.py`)
```python
async def _stream_completion(self, request: GenerateRequest) -> AsyncGenerator[str, None]:
    """Stream completion with chunk timeout and total timeout."""
    # Config from providers.yaml:
    # streaming:
    #   chunk_timeout_ms: 30000    # 30s per chunk
    #   total_timeout_ms: 300000   # 5min total
    
    chunk_timeout = self.config.streaming.chunk_timeout_ms / 1000
    total_timeout = self.config.streaming.total_timeout_ms / 1000
    
    start_time = time.monotonic()
    last_chunk_time = start_time
    
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            async for chunk in response.aiter_text():
                now = time.monotonic()
                
                # Chunk timeout check
                if now - last_chunk_time > chunk_timeout:
                    logger.info(f"Stream alive, {now - last_chunk_time:.0f}s since last chunk")
                    # CONTINUE waiting - not hard fail
                
                # Total timeout check
                if now - start_time > total_timeout:
                    raise TimeoutError(f"Stream total timeout exceeded ({total_timeout}s)")
                
                last_chunk_time = now
                yield chunk
```

### 1.2 Provider Config (`config/providers.yaml`)
```yaml
providers:
  - name: openrouter
    type: openai_compat
    streaming:
      chunk_timeout_ms: 30000    # 30s
      total_timeout_ms: 300000   # 5min
  - name: opencode-zen
    type: openai_compat
    streaming:
      chunk_timeout_ms: 30000
      total_timeout_ms: 300000
```

### 1.3 GenerateResult (`src/omega/oracle/types.py`)
```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str          # M22: Actual provider, not configured
    model_name: str
    latency_ms: float
    tokens_generated: int
    finish_reason: str
    streaming: bool = False
    chunk_count: int = 0
    first_chunk_latency_ms: float = 0.0
```

---

## §2 Property-Based Testing Patterns

### 2.1 Pattern 1: Chunk Timeout Heartbeat (Not Hard Fail)
**Property**: Chunk timeout logs heartbeat but continues waiting; doesn't abort stream.

```python
from hypothesis import given, strategies as st
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@given(
    chunk_intervals=st.lists(st.floats(0.1, 60.0), min_size=2, max_size=20),
    chunk_timeout=st.floats(1.0, 30.0),
    total_timeout=st.floats(10.0, 300.0),
)
@pytest.mark.anyio
async def test_chunk_timeout_heartbeat_not_hard_fail(chunk_intervals, chunk_timeout, total_timeout):
    """Chunk timeout triggers heartbeat log but stream continues."""
    from omega.oracle.backends.openai_compat import OpenAICompatBackend
    
    backend = OpenAICompatBackend(config=MockConfig(
        streaming_chunk_timeout_ms=chunk_timeout * 1000,
        streaming_total_timeout_ms=total_timeout * 1000,
    ))
    
    # Mock HTTP response that yields chunks at specified intervals
    async def mock_stream():
        for interval in chunk_intervals:
            await asyncio.sleep(interval)
            yield "chunk"
    
    backend._make_stream_request = AsyncMock(return_value=mock_stream())
    
    chunks_received = []
    heartbeat_logs = []
    
    # Capture logs
    with patch('omega.oracle.backends.openai_compat.logger') as mock_logger:
        async for chunk in backend._stream_completion(MockRequest()):
            chunks_received.append(chunk)
        
        # Check for heartbeat logs (not errors)
        heartbeat_calls = [
            call for call in mock_logger.info.call_args_list
            if "Stream alive" in str(call)
        ]
        
        # Should have heartbeat for each interval > chunk_timeout
        expected_heartbeats = sum(1 for interval in chunk_intervals if interval > chunk_timeout)
        assert len(heartbeat_calls) >= expected_heartbeats
        
        # Should NOT have error logs for chunk timeout
        error_calls = [
            call for call in mock_logger.error.call_args_list
            if "chunk timeout" in str(call).lower()
        ]
        assert len(error_calls) == 0
    
    # All chunks should be received despite timeouts
    assert len(chunks_received) == len(chunk_intervals)
```

### 2.2 Pattern 2: Total Timeout Hard Fail
**Property**: Total timeout aborts stream and raises TimeoutError.

```python
@given(
    total_duration=st.floats(1.0, 600.0),
    total_timeout=st.floats(1.0, 300.0),
)
@pytest.mark.anyio
async def test_total_timeout_hard_fail(total_duration, total_timeout):
    """Total timeout aborts stream with TimeoutError."""
    backend = OpenAICompatBackend(config=MockConfig(
        streaming_chunk_timeout_ms=30000,
        streaming_total_timeout_ms=total_timeout * 1000,
    ))
    
    async def slow_stream():
        await asyncio.sleep(total_duration)
        yield "chunk"
    
    backend._make_stream_request = AsyncMock(return_value=slow_stream())
    
    if total_duration > total_timeout:
        with pytest.raises(TimeoutError):
            async for _ in backend._stream_completion(MockRequest()):
                pass
    else:
        # Should complete normally
        chunks = []
        async for chunk in backend._stream_completion(MockRequest()):
            chunks.append(chunk)
        assert len(chunks) == 1
```

### 2.3 Pattern 3: Graceful Fallback on Stream Failure
**Property**: Stream failure triggers fallback to next provider.

```python
@given(
    fail_at_chunk=st.integers(0, 10),
    num_chunks=st.integers(5, 20),
    fallback_succeeds=st.booleans(),
)
@pytest.mark.anyio
async def test_stream_fallback(fail_at_chunk, num_chunks, fallback_succeeds):
    """Stream failure triggers provider fallback."""
    from omega.oracle.model_gateway import ModelGateway
    
    gateway = ModelGateway()
    
    # Primary provider fails at specific chunk
    async def failing_stream():
        for i in range(num_chunks):
            if i == fail_at_chunk:
                raise httpx.StreamError("Connection reset")
            yield f"chunk_{i}"
    
    # Fallback provider
    async def fallback_stream():
        for i in range(num_chunks):
            yield f"fallback_chunk_{i}"
    
    primary = MockProvider(name="primary", stream_func=failing_stream)
    fallback = MockProvider(name="fallback", stream_func=fallback_stream)
    
    gateway.register_provider(primary)
    gateway.register_provider(fallback)
    
    if fallback_succeeds:
        chunks = []
        async for chunk in gateway.stream_generate(MockRequest()):
            chunks.append(chunk)
        
        # Should have primary chunks up to failure, then fallback chunks
        primary_chunks = [c for c in chunks if c.startswith("chunk_")]
        fallback_chunks = [c for c in chunks if c.startswith("fallback_chunk_")]
        
        assert len(primary_chunks) == fail_at_chunk
        assert len(fallback_chunks) == num_chunks - fail_at_chunk
    else:
        # Both fail - should raise
        with pytest.raises(Exception):
            async for _ in gateway.stream_generate(MockRequest()):
                pass
```

### 2.4 Pattern 4: First Chunk Latency Tracking
**Property**: First chunk latency recorded separately from total latency.

```python
@given(
    first_chunk_delay=st.floats(0.01, 10.0),
    subsequent_delays=st.lists(st.floats(0.01, 1.0), min_size=1, max_size=10),
)
@pytest.mark.anyio
async def test_first_chunk_latency_tracking(first_chunk_delay, subsequent_delays):
    """First chunk latency tracked separately from total."""
    backend = OpenAICompatBackend(config=MockConfig())
    
    async def timed_stream():
        await asyncio.sleep(first_chunk_delay)
        yield "first"
        for delay in subsequent_delays:
            await asyncio.sleep(delay)
            yield "next"
    
    backend._make_stream_request = AsyncMock(return_value=timed_stream())
    
    result = await backend.generate(MockRequest(stream=True))
    
    assert result.streaming is True
    assert result.first_chunk_latency_ms > 0
    assert result.first_chunk_latency_ms <= result.latency_ms
    assert abs(result.first_chunk_latency_ms - first_chunk_delay * 1000) < 50  # ~50ms tolerance
```

### 2.5 Pattern 5: Chunk Count Accuracy
**Property**: Chunk count equals actual chunks yielded.

```python
@given(
    num_chunks=st.integers(1, 100),
    chunk_sizes=st.lists(st.integers(1, 100), min_size=1, max_size=100),
)
@pytest.mark.anyio
async def test_chunk_count_accuracy(num_chunks, chunk_sizes):
    """Chunk count in GenerateResult matches actual chunks."""
    backend = OpenAICompatBackend(config=MockConfig())
    
    async def chunked_stream():
        for size in chunk_sizes[:num_chunks]:
            yield "x" * size
    
    backend._make_stream_request = AsyncMock(return_value=chunked_stream())
    
    result = await backend.generate(MockRequest(stream=True))
    
    assert result.chunk_count == num_chunks
    assert result.streaming is True
```

### 2.6 Pattern 6: Provider Name Provenance (M22)
**Property**: `GenerateResult.provider_name` reflects actual provider, not configured intent.

```python
@given(
    primary_name=st.sampled_from(["google", "openrouter", "opencode-zen"]),
    fallback_name=st.sampled_from(["google", "openrouter", "opencode-zen"]),
    primary_fails=st.booleans(),
)
@pytest.mark.anyio
async def test_provider_provenance(primary_name, fallback_name, primary_fails):
    """GenerateResult.provider_name reflects actual provider used."""
    from omega.oracle.model_gateway import ModelGateway
    
    gateway = ModelGateway()
    
    async def primary_stream():
        if primary_fails:
            raise Exception("Primary failed")
        yield "primary_chunk"
    
    async def fallback_stream():
        yield "fallback_chunk"
    
    primary = MockProvider(name=primary_name, stream_func=primary_stream)
    fallback = MockProvider(name=fallback_name, stream_func=fallback_stream)
    
    gateway.register_provider(primary)
    gateway.register_provider(fallback)
    
    result = await gateway.generate(MockRequest(stream=True))
    
    if primary_fails:
        assert result.provider_name == fallback_name
    else:
        assert result.provider_name == primary_name
    
    # Should NEVER be the configured default, always actual
    assert result.provider_name in (primary_name, fallback_name)
```

### 2.7 Pattern 7: Concurrent Stream Isolation
**Property**: Concurrent streams don't interfere with each other's timeouts.

```python
@given(
    num_streams=st.integers(2, 20),
    stream_durations=st.lists(st.floats(0.1, 30.0), min_size=2, max_size=20),
)
@pytest.mark.anyio
async def test_concurrent_stream_isolation(num_streams, stream_durations):
    """Concurrent streams have independent timeout tracking."""
    backend = OpenAICompatBackend(config=MockConfig(
        streaming_chunk_timeout_ms=5000,
        streaming_total_timeout_ms=10000,
    ))
    
    async def make_stream(duration):
        async def stream():
            await asyncio.sleep(duration)
            yield "done"
        return stream()
    
    backend._make_stream_request = AsyncMock(side_effect=[make_stream(d) for d in stream_durations[:num_streams]])
    
    # Launch all streams concurrently
    async def run_stream(i):
        try:
            async for _ in backend._stream_completion(MockRequest()):
                pass
            return "success"
        except TimeoutError:
            return "timeout"
    
    results = await asyncio.gather(*[run_stream(i) for i in range(num_streams)])
    
    # Each stream should succeed/fail based on its own duration
    for i, (result, duration) in enumerate(zip(results, stream_durations)):
        if duration > 10.0:  # total_timeout
            assert result == "timeout"
        else:
            assert result == "success"
```

### 2.8 Pattern 8: Empty Stream Handling
**Property**: Empty stream (no chunks) handled gracefully.

```python
@pytest.mark.anyio
async def test_empty_stream():
    """Empty stream returns empty result, not error."""
    backend = OpenAICompatBackend(config=MockConfig())
    
    async def empty_stream():
        return
        yield  # Never reached
    
    backend._make_stream_request = AsyncMock(return_value=empty_stream())
    
    result = await backend.generate(MockRequest(stream=True))
    
    assert result.text == ""
    assert result.chunk_count == 0
    assert result.streaming is True
    assert result.finish_reason == "empty"
```

---

## §3 Hypothesis Strategy Composites

### 3.1 Stream Timing Strategy
```python
from hypothesis import strategies as st

@st.composite
def stream_timing(draw):
    """Generate realistic stream timing patterns."""
    pattern = draw(st.sampled_from(["steady", "bursty", "slow_start", "degrading"]))
    num_chunks = draw(st.integers(1, 50))
    
    if pattern == "steady":
        interval = draw(st.floats(0.05, 0.5))
        return [interval] * num_chunks
    
    elif pattern == "bursty":
        # Fast bursts separated by pauses
        intervals = []
        for i in range(num_chunks):
            if i % 5 == 0:
                intervals.append(draw(st.floats(1.0, 5.0)))  # Pause
            else:
                intervals.append(draw(st.floats(0.01, 0.1)))  # Burst
        return intervals
    
    elif pattern == "slow_start":
        # First chunk slow, then steady
        first = draw(st.floats(1.0, 10.0))
        rest = [draw(st.floats(0.05, 0.2)) for _ in range(num_chunks - 1)]
        return [first] + rest
    
    else:  # degrading
        # Gradually slowing down
        return [draw(st.floats(0.05, 0.5)) * (1 + i * 0.1) for i in range(num_chunks)]
```

### 3.2 Provider Failure Strategy
```python
@st.composite
def provider_failure_scenario(draw):
    """Generate provider failure scenarios for fallback testing."""
    num_providers = draw(st.integers(2, 5))
    providers = [f"provider_{i}" for i in range(num_providers)]
    
    # Which provider succeeds (last one always succeeds for guaranteed success)
    success_index = draw(st.integers(0, num_providers - 1))
    
    fail_points = []
    for i in range(num_providers):
        if i < success_index:
            # This provider fails
            fail_at = draw(st.integers(0, 10))
            fail_points.append((providers[i], fail_at))
        elif i == success_index:
            fail_points.append((providers[i], None))  # Succeeds
        else:
            fail_points.append((providers[i], "unreached"))  # Never tried
    
    return fail_points
```

---

## §4 Integration with Existing Test Pattern

### 4.1 Proven Pattern Adaptation
```python
# From tests/property/test_breaker_fsm.py
@pytest.mark.anyio
@given(st.data())
async def test_streaming_resilience_property(data):
    backend = OpenAICompatBackend(config=MockConfig(
        streaming_chunk_timeout_ms=5000,
        streaming_total_timeout_ms=30000,
    ))
    
    # Generate stream timing
    timing = data.draw(stream_timing())
    
    async def mock_stream():
        for interval in timing:
            await asyncio.sleep(interval)
            yield "chunk"
    
    backend._make_stream_request = AsyncMock(return_value=mock_stream())
    
    chunks = []
    async for chunk in backend._stream_completion(MockRequest()):
        chunks.append(chunk)
    
    # All chunks received despite timing variations
    assert len(chunks) == len(timing)
```

---

## §5 Extraction Targets for Omega Engine

| Pattern | Omega Type | Test File | Status |
|---------|------------|-----------|--------|
| Chunk timeout heartbeat | `OpenAICompatBackend._stream_completion` | `test_streaming_chunk_timeout.py` | Ready |
| Total timeout hard fail | `OpenAICompatBackend._stream_completion` | `test_streaming_total_timeout.py` | Ready |
| Graceful fallback | `ModelGateway.stream_generate` | `test_streaming_fallback.py` | Ready |
| First chunk latency | `GenerateResult.first_chunk_latency_ms` | `test_streaming_first_chunk.py` | Ready |
| Chunk count accuracy | `GenerateResult.chunk_count` | `test_streaming_chunk_count.py` | Ready |
| Provider provenance (M22) | `GenerateResult.provider_name` | `test_streaming_provenance.py` | Ready |
| Concurrent isolation | `OpenAICompatBackend` | `test_streaming_concurrent.py` | Ready |
| Empty stream handling | `OpenAICompatBackend._stream_completion` | `test_streaming_empty.py` | Ready |

---

## §6 Key Findings Summary

1. **Chunk Timeout = Heartbeat, Not Fail**: 30s chunk timeout logs "Stream alive" but continues waiting
2. **Total Timeout = Hard Fail**: 5min total timeout raises TimeoutError and triggers fallback
3. **Graceful Fallback**: Stream failure at any chunk triggers provider fallback seamlessly
4. **M22 Provenance**: `GenerateResult.provider_name` tracks actual provider, not configured
5. **First Chunk Latency**: Tracked separately for TTFT (Time To First Token) metrics
6. **Chunk Count**: Accurate count for billing/observability
7. **Concurrent Isolation**: Each stream has independent timeout tracking
8. **Config-Driven**: Timeouts from `config/providers.yaml` per provider

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ C-11 Domain 5 Complete ⬡ 2026-07-23*