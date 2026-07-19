# AP: AP-TEST-STREAMING-v1.0.0
"""
Contract tests for M25 Streaming Resilience.
Tests chunk timeout, heartbeat logging, and graceful fallback.
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from src.omega.oracle.backends.openai_compat import OpenAICompatProvider


class TestStreamingTimeout:
    """Test streaming timeout behavior per M25 mandate."""
    
    @pytest.fixture
    def provider_config(self):
        return {
            "streaming": {
                "chunk_timeout_ms": 30000,
                "total_timeout_ms": 300000,
                "fallback_on_timeout": True,
                "fallback_provider": "native-gguf"
            }
        }
    
    @pytest.fixture
    def provider(self, provider_config):
        with patch("src.omega.oracle.backends.openai_compat.AsyncOpenAI"):
            provider = OpenAICompatProvider(
                name="test-provider",
                config=provider_config
            )
            return provider
    
    @pytest.mark.asyncio
    async def test_chunk_timeout_heartbeat_logging(self, provider):
        """Test that chunk timeout logs heartbeat but continues (not hard-fail)."""
        # Mock a stream with 40s gap between chunks (exceeds 30s chunk_timeout)
        async def mock_stream():
            yield "chunk 1"
            await asyncio.sleep(0.01)  # Simulate 40s gap (compressed for test)
            yield "chunk 2"
            await asyncio.sleep(0.01)
            yield "chunk 3"
        
        # Override timeouts for test speed
        provider.config["streaming"]["chunk_timeout_ms"] = 10  # 10ms for test
        provider.config["streaming"]["total_timeout_ms"] = 1000
        
        with patch.object(provider, "_stream_completion", return_value=mock_stream()):
            with patch("src.omega.oracle.backends.openai_compat.logger") as mock_logger:
                chunks = []
                async for chunk in provider._stream_completion(MagicMock()):
                    chunks.append(chunk)
                
                # Verify heartbeat warning was logged
                warning_calls = [c for c in mock_logger.warning.call_args_list 
                               if "chunk idle timeout" in str(c).lower()]
                assert len(warning_calls) >= 1, "Should log heartbeat warning on chunk timeout"
                
                # Verify stream continued (not hard-failed)
                assert len(chunks) == 3, "Stream should continue after chunk timeout"
    
    @pytest.mark.asyncio
    async def test_total_timeout_graceful_fallback(self, provider):
        """Test total timeout triggers graceful fallback."""
        async def slow_stream():
            for i in range(10):
                await asyncio.sleep(0.1)  # 100ms per chunk
                yield f"chunk {i}"
        
        provider.config["streaming"]["total_timeout_ms"] = 200  # 200ms total
        
        with patch.object(provider, "_stream_completion", return_value=slow_stream()):
            with patch.object(provider, "_fallback_to_next_provider") as mock_fallback:
                mock_fallback.return_value = "fallback result"
                
                result = await provider.generate(MagicMock())
                
                # Should have triggered fallback
                mock_fallback.assert_called_once()
                assert result == "fallback result"
    
    @pytest.mark.asyncio
    async def test_heartbeat_logging_interval(self, provider):
        """Test heartbeat logs every 10s of chunk silence."""
        provider.config["streaming"]["chunk_timeout_ms"] = 10000  # 10s
        
        async def mock_stream():
            yield "chunk 1"
            await asyncio.sleep(0.02)  # 20s simulated
            yield "chunk 2"
        
        with patch.object(provider, "_stream_completion", return_value=mock_stream()):
            with patch("src.omega.oracle.backends.openai_compat.logger") as mock_logger:
                chunks = []
                async for chunk in provider._stream_completion(MagicMock()):
                    chunks.append(chunk)
                
                # Should log heartbeat at ~10s intervals
                heartbeat_calls = [c for c in mock_logger.info.call_args_list 
                                 if "stream alive" in str(c).lower()]
                assert len(heartbeat_calls) >= 1, "Should log heartbeat during long chunk gaps"


class TestProviderFallbackChain:
    """Test provider fallback chain behavior."""
    
    @pytest.mark.asyncio
    async def test_fallback_preserves_provider_name(self):
        """Fallback result should have correct provider_name from actual responder."""
        # This tests M22 Response Provenance
        pass
    
    @pytest.mark.asyncio
    async def test_fallback_chain_exhaustion(self):
        """When all providers fail, raise AllProvidersExhausted."""
        pass


class TestStreamingConfigValidation:
    """Validate streaming config per provider."""
    
    def test_all_cloud_providers_have_streaming_config(self):
        """Every cloud provider in providers.yaml must have streaming section."""
        import yaml
        with open("config/providers.yaml") as f:
            config = yaml.safe_load(f)
        
        cloud_providers = ["opencode-zen", "openrouter", "google", "google-compat", 
                          "anthropic", "xai", "cline", "antigravity"]
        
        for provider_name in cloud_providers:
            provider = config["providers"].get(provider_name, {})
            assert "streaming" in provider, f"{provider_name} missing streaming config"
            streaming = provider["streaming"]
            assert "chunk_timeout_ms" in streaming, f"{provider_name} missing chunk_timeout_ms"
            assert "total_timeout_ms" in streaming, f"{provider_name} missing total_timeout_ms"
            assert "fallback_on_timeout" in streaming, f"{provider_name} missing fallback_on_timeout"
            assert "fallback_provider" in streaming, f"{provider_name} missing fallback_provider"
            assert streaming["fallback_on_timeout"] is True, f"{provider_name} fallback_on_timeout must be true"
            assert streaming["fallback_provider"] == "native-gguf", f"{provider_name} fallback must be native-gguf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])