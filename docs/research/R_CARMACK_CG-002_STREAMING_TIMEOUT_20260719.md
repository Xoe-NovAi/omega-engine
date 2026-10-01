<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CG-002: Streaming Timeout Test Suite
**AP Token**: `AP-CARMACK-CG002-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
Contract test for chunk timeout + heartbeat + graceful fallback (Mandate 25)

---

## 📋 Primary Source Findings

### AnyIO Timeout Patterns (Official Docs)

**`anyio.move_on_after(delay)`** — Exits context block on timeout, no exception:
```python
from anyio import move_on_after, sleep

async def main():
    with move_on_after(1) as scope:
        print('Starting sleep')
        await sleep(2)
        print('This should never be printed')
    print(f'Exited cancel scope, cancelled = {scope.cancelled_caught}')
```

**`anyio.fail_after(delay)`** — Raises `TimeoutError` on timeout:
```python
from anyio import fail_after, sleep

async def main():
    try:
        with fail_after(1):
            await sleep(2)
    except TimeoutError:
        print('Operation timed out')
```

**Key Difference**: `move_on_after` = soft timeout (continue), `fail_after` = hard timeout (raise).

### Streaming Heartbeat Pattern (from odysian/vector-doc-qa #248)
```python
# SSE streaming with heartbeat
async def stream_with_heartbeat(generator, heartbeat_interval=15):
    queue = asyncio.Queue()
    
    async def producer():
        async for chunk in generator:
            await queue.put(("data", chunk))
        await queue.put(("done", None))
    
    async def heartbeat():
        while True:
            await asyncio.sleep(heartbeat_interval)
            await queue.put(("heartbeat", ": keep-alive\n\n"))
    
    producer_task = asyncio.create_task(producer())
    heartbeat_task = asyncio.create_task(heartbeat())
    
    try:
        while True:
            event_type, data = await queue.get()
            if event_type == "done":
                break
            yield f"event: {event_type}\ndata: {data}\n\n"
    finally:
        producer_task.cancel()
        heartbeat_task.cancel()
```

### Nemotron 3 Ultra Streaming Bug (Observed)
- **Symptom**: 30+ second gaps between chunks on OpenCode Zen
- **OpenCode Behavior**: Treats stall as timeout → empty response → all tokens lost
- **Required Fix**: Per-chunk idle timeout (30s) with heartbeat logging, NOT hard-fail

---

## ✅ M25 Mandate Requirements (from SOVEREIGN_MANDATES.md)

| Parameter | Value | Config Location |
|-----------|-------|-----------------|
| Per-chunk idle timeout | 30s | `config/providers.yaml` → `streaming.chunk_timeout_ms` |
| Total stream timeout | 5min | `config/providers.yaml` → `streaming.total_timeout_ms` |
| On chunk timeout | LOG heartbeat, CONTINUE waiting | `openai_compat.py:_stream_completion()` |
| On total timeout | GRACEFUL fallback to next provider | Provider fabric chain |

---

## 🧪 Test Implementation: `tests/test_streaming_timeout.py`

```python
"""
Contract tests for M25 Streaming Resilience.
Validates: chunk timeout + heartbeat + graceful fallback.
"""
import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock, patch
from src.omega.oracle.backends.openai_compat import OpenAICompatProvider
from src.omega.oracle.providers import GenerateResult


class TestStreamingTimeouts:
    """M25: Streaming Resilience contract tests."""
    
    @pytest.fixture
    def provider_config(self):
        return {
            "name": "test-provider",
            "base_url": "http://localhost:8080",
            "api_key": "test-key",
            "streaming": {
                "chunk_timeout_ms": 30000,   # 30s per chunk
                "total_timeout_ms": 300000,  # 5min total
            }
        }
    
    @pytest.fixture
    def provider(self, provider_config):
        return OpenAICompatProvider(provider_config)
    
    @pytest.mark.anyio
    async def test_chunk_timeout_logs_heartbeat_not_hard_fail(self, provider):
        """
        M25 REQUIREMENT: On chunk timeout, LOG heartbeat and CONTINUE waiting.
        NOT: raise TimeoutError and lose all tokens.
        """
        # Mock a stream that stalls for 35s between chunks (exceeds 30s chunk timeout)
        async def slow_stream():
            yield "chunk 1"
            await anyio.sleep(35)  # Exceeds chunk_timeout_ms
            yield "chunk 2"
        
        provider._stream_raw = AsyncMock(return_value=slow_stream())
        
        # Capture log output
        with patch('src.omega.oracle.backends.openai_compat.logger') as mock_logger:
            chunks = []
            async for chunk in provider._stream_completion("test prompt"):
                chunks.append(chunk)
            
            # Verify: got both chunks despite stall
            assert len(chunks) == 2
            assert chunks[0] == "chunk 1"
            assert chunks[1] == "chunk 2"
            
            # Verify: heartbeat logged at INFO level
            mock_logger.info.assert_any_call(
                "Stream alive, 35s since last chunk"
            )
            
            # Verify: NO TimeoutError raised
            mock_logger.error.assert_not_called()
    
    @pytest.mark.anyio
    async def test_total_timeout_triggers_graceful_fallback(self, provider):
        """
        M25 REQUIREMENT: On total timeout, graceful fallback to next provider.
        """
        async def very_slow_stream():
            yield "chunk 1"
            await anyio.sleep(310)  # Exceeds total_timeout_ms (300s)
            yield "chunk 2"
        
        provider._stream_raw = AsyncMock(return_value=very_slow_stream())
        
        with patch('src.omega.oracle.backends.openai_compat.logger') as mock_logger:
            chunks = []
            async for chunk in provider._stream_completion("test prompt"):
                chunks.append(chunk)
            
            # Should get first chunk only
            assert len(chunks) == 1
            assert chunks[0] == "chunk 1"
            
            # Should log total timeout
            mock_logger.warning.assert_any_call(
                "Stream total timeout reached (300s), falling back to next provider"
            )
    
    @pytest.mark.anyio
    async def test_chunk_timeout_configurable_per_provider(self, provider):
        """Verify chunk_timeout_ms and total_timeout_ms read from config."""
        assert provider.chunk_timeout == 30.0  # seconds
        assert provider.total_timeout == 300.0  # seconds
    
    @pytest.mark.anyio
    async def test_nemotron_30s_gap_scenario(self, provider):
        """
        REGRESSION TEST: Nemotron 3 Ultra on OpenCode Zen has 30s+ chunk gaps.
        This test MUST pass to unblock MaKaLi councils.
        """
        async def nemotron_stream():
            yield "First token"
            await anyio.sleep(32)  # Nemotron observed gap
            yield "Second token after gap"
            await anyio.sleep(32)
            yield "Third token"
        
        provider._stream_raw = AsyncMock(return_value=nemotron_stream())
        
        with patch('src.omega.oracle.backends.openai_compat.logger') as mock_logger:
            chunks = []
            async for chunk in provider._stream_completion("test"):
                chunks.append(chunk)
            
            # All 3 chunks received despite 32s gaps
            assert len(chunks) == 3
            assert chunks == ["First token", "Second token after gap", "Third token"]
            
            # Two heartbeats logged
            assert mock_logger.info.call_count >= 2
            mock_logger.info.assert_any_call("Stream alive, 32s since last chunk")


class TestStreamingConfigValidation:
    """Validate providers.yaml streaming section exists for all cloud providers."""
    
    def test_opencode_zen_has_streaming_config(self):
        import yaml
        with open("config/providers.yaml") as f:
            config = yaml.safe_load(f)
        
        opencode_zen = next(p for p in config["providers"] if p["name"] == "opencode-zen")
        assert "streaming" in opencode_zen
        assert opencode_zen["streaming"]["chunk_timeout_ms"] == 30000
        assert opencode_zen["streaming"]["total_timeout_ms"] == 300000
    
    def test_openrouter_has_streaming_config(self):
        import yaml
        with open("config/providers.yaml") as f:
            config = yaml.safe_load(f)
        
        openrouter = next(p for p in config["providers"] if p["name"] == "openrouter")
        assert "streaming" in openrouter
        assert openrouter["streaming"]["chunk_timeout_ms"] == 30000
        assert openrouter["streaming"]["total_timeout_ms"] == 300000
```

---

## 🔬 id Software Qualification Gate

> **"Cannot be justified WITHOUT citing the original hardware constraint."**

| Aspect | id Software Analog | M25 Streaming Fix |
|--------|-------------------|-------------------|
| **Constraint** | 15W TDP thermal ceiling (Ryzen 5700U) | Nemotron 30s+ chunk gaps on OpenCode Zen |
| **Technique** | Dynamic frequency scaling, frame pacing | Chunk-level timeout + heartbeat logging + continue |
| **Justification** | Throttling loses frames; pacing keeps 60fps | Hard timeout loses ALL tokens; heartbeat keeps stream alive |
| **Scope** | Renderer only | Provider streaming only |

**Verdict**: **PASSES** — The 30s chunk gap is a real provider infrastructure constraint (OpenCode Zen's Nemotron deployment), not a cargo-cult pattern.

---

## 📝 Implementation Checklist

- [ ] Add `streaming` section to `config/providers.yaml` for `opencode-zen` and `openrouter`
- [ ] Implement `_stream_completion()` with `anyio.move_on_after(chunk_timeout)` per chunk
- [ ] Add heartbeat logging at INFO level on chunk timeout
- [ ] Add total timeout with graceful fallback warning
- [ ] Add `tests/test_streaming_timeout.py` with 3 contract tests
- [ ] Add `make test-streaming` target to Makefile
- [ ] Verify Nemotron 3 Ultra on OpenCode Zen completes councils without token loss

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
