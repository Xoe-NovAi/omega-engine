# 🔱 GoogleCompatProvider Tests — Gemma 4 Week 1 Step 2
# ⬡ OMEGA ⬡ P10 ⬡ trc_test_google_compat ⬡ v0.1.0 ⬡ 2026-07-19

import pytest
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.oracle.backends.google_compat import GoogleCompatProvider
from omega.oracle.capability_matrix import CapabilityMatrix, reset_capability_matrix
from omega.errors import ProviderAuthError, ProviderRateLimitError, ProviderUnavailableError


class TestGoogleCompatProvider:
    """Test suite for GoogleCompatProvider."""
    
    @pytest.fixture(autouse=True)
    def reset_matrix(self):
        reset_capability_matrix()
        yield
        reset_capability_matrix()
    
    @pytest.fixture
    def capability_matrix(self):
        """Create a capability matrix for testing."""
        matrix = CapabilityMatrix()
        matrix.load()
        return matrix
    
    @pytest.fixture
    def provider(self, capability_matrix):
        """Create a GoogleCompatProvider instance."""
        with patch.object(GoogleCompatProvider, '_resolve_api_key', return_value="test-api-key"):
            provider = GoogleCompatProvider(
                name="google-compat",
                config={"api_key": "test-api-key"},
                capability_matrix=capability_matrix
            )
        return provider
    
    def test_provider_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.name == "google-compat"
        assert provider.api_key == "test-api-key"
        assert provider.capability_matrix is not None
        assert provider.provider_config is not None
        assert provider.provider_config.display_name == "Google AI Studio (gemini.googleapis.com)"
    
    @pytest.mark.anyio
    async def test_is_available_with_key(self, provider):
        """Test is_available returns True with API key."""
        assert await provider.is_available() is True
    
    @pytest.mark.anyio
    async def test_is_available_without_key(self, capability_matrix):
        """Test is_available returns False without API key."""
        with patch.object(GoogleCompatProvider, '_resolve_api_key', return_value=""):
            provider = GoogleCompatProvider(
                name="google-compat",
                config={},
                capability_matrix=capability_matrix
            )
        assert await provider.is_available() is False
    
    def test_resolve_model_id(self, provider):
        """Test model ID normalization."""
        # Test google/ prefix stripping
        normalized = provider._resolve_model_id("google/gemma-4-31b-it", "google-ai-studio")
        assert normalized == "gemma-4-31b-it"
        
        # Test :free suffix stripping for Google API
        normalized = provider._resolve_model_id("google/gemma-4-31b-it:free", "google-ai-studio")
        assert normalized == "gemma-4-31b-it"
        
        # Test bare model ID passes through
        normalized = provider._resolve_model_id("gemma-4-31b-it", "google-ai-studio")
        assert normalized == "gemma-4-31b-it"
    
    def test_get_capability_fuzzy_match(self, provider):
        """Test capability lookup with fuzzy matching."""
        # Exact match
        cap = provider._get_capability("gemma-4-31b-it")
        assert cap is not None
        assert cap.model_id == "gemma-4-31b-it"
        
        # With google/ prefix
        cap = provider._get_capability("google/gemma-4-31b-it")
        assert cap is not None
        assert cap.model_id == "gemma-4-31b-it"
        
        # With :free suffix
        cap = provider._get_capability("gemma-4-31b-it:free")
        assert cap is not None
        assert cap.model_id == "gemma-4-31b-it"
    
    def test_build_thinking_config_minimal(self, provider):
        """Test building MINIMAL thinking config."""
        cap = provider._get_capability("gemma-4-31b-it")
        
        config = provider._build_thinking_config(cap, "minimal")
        assert config is not None
        assert config["thinkingConfig"]["thinkingLevel"] == "MINIMAL"
        
        config = provider._build_thinking_config(cap, "low")
        assert config["thinkingConfig"]["thinkingLevel"] == "MINIMAL"
        
        config = provider._build_thinking_config(cap, "standard")
        assert config["thinkingConfig"]["thinkingLevel"] == "MINIMAL"
    
    def test_build_thinking_config_high(self, provider):
        """Test building HIGH thinking config."""
        cap = provider._get_capability("gemma-4-31b-it")
        
        config = provider._build_thinking_config(cap, "medium")
        assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"
        
        config = provider._build_thinking_config(cap, "high")
        assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"
        
        config = provider._build_thinking_config(cap, "deep")
        assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"
        
        config = provider._build_thinking_config(cap, "xhigh")
        assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"
    
    def test_build_thinking_config_none(self, provider):
        """Test omitting thinking config for 'none' effort."""
        cap = provider._get_capability("gemma-4-31b-it")
        
        config = provider._build_thinking_config(cap, "none")
        assert config is None
    
    def test_build_thinking_config_clamping(self, provider):
        """Test thinking level clamping for unsupported levels."""
        # Create a capability with only MINIMAL support
        from omega.oracle.capability_matrix import ModelCapability, ThinkingConfig
        
        cap = ModelCapability(
            model_id="test-model",
            display_name="Test Model",
            thinking_config=ThinkingConfig(
                supported_levels=["MINIMAL"],
                detection_regex="",
                default="MINIMAL",
                thinking_mapping={"minimal": "MINIMAL", "deep": "MINIMAL"}
            )
        )
        
        # Request HIGH but only MINIMAL supported -> clamp to MINIMAL
        config = provider._build_thinking_config(cap, "deep")
        assert config["thinkingConfig"]["thinkingLevel"] == "MINIMAL"
    
    def test_extract_thinking_from_response(self, provider):
        """Test extracting thinking tokens from response."""
        # Response with thoughtsTokenCount in usageMetadata
        data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Hello world"}]
                }
            }],
            "usageMetadata": {
                "thoughtsTokenCount": 42
            }
        }
        
        text, thoughts = provider._extract_thinking_from_response(data)
        assert text == "Hello world"
        assert thoughts == 42
    
    def test_extract_thinking_from_response_with_thought_parts(self, provider):
        """Test extracting thinking from thought parts."""
        data = {
            "candidates": [{
                "content": {
                    "parts": [
                        {"text": "Let me think...", "thought": True},
                        {"text": "Hello world"}
                    ]
                }
            }]
        }
        
        text, thoughts = provider._extract_thinking_from_response(data)
        assert "Hello world" in text
        assert thoughts > 0  # Approximate count from thought parts
    
    def test_parse_rate_limit_headers(self, provider):
        """Test parsing Google rate limit headers."""
        headers = {
            "x-ratelimit-remaining-requests": "10",
            "x-ratelimit-remaining-tokens": "5000",
            "retry-after": "30"
        }
        
        rate_info = provider._parse_rate_limit_headers(headers)
        assert rate_info["remaining_requests"] == "10"
        assert rate_info["remaining_tokens"] == "5000"
        assert rate_info["retry_after"] == "30"
    
    @pytest.mark.anyio
    async def test_generate_auth_error(self, capability_matrix):
        """Test generate raises auth error without API key."""
        with patch.object(GoogleCompatProvider, '_resolve_api_key', return_value=""):
            provider = GoogleCompatProvider(
                name="google-compat",
                config={},
                capability_matrix=capability_matrix
            )
        
        with pytest.raises(ProviderAuthError):
            await provider.generate(
                model="gemma-4-31b-it",
                system_prompt="Test",
                user_query="Hello"
            )
    
    @pytest.mark.anyio
    async def test_generate_rate_limit_error(self, provider):
        """Test generate handles 429 rate limit."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(ProviderRateLimitError):
                await provider.generate(
                    model="gemma-4-31b-it",
                    system_prompt="Test",
                    user_query="Hello"
                )
    
    @pytest.mark.anyio
    async def test_generate_server_error(self, provider):
        """Test generate handles 5xx server errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(ProviderUnavailableError):
                await provider.generate(
                    model="gemma-4-31b-it",
                    system_prompt="Test",
                    user_query="Hello"
                )
    
    @pytest.mark.anyio
    async def test_generate_success(self, provider):
        """Test successful generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Hello! How can I help you?"}]
                },
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "thoughtsTokenCount": 10
            }
        }
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            result = await provider.generate(
                model="gemma-4-31b-it",
                system_prompt="You are helpful",
                user_query="Hello",
                thinking_effort="standard"
            )
            
            assert result["text"] == "Hello! How can I help you?"
            assert result["provider_name"] == "google-ai-studio"
            assert result["is_cloud"] is True
            assert result["model_used"] == "gemma-4-31b-it"
            assert result["thoughts_token_count"] == 10
            assert result["latency_ms"] > 0
    
    @pytest.mark.anyio
    async def test_generate_with_thinking_high(self, provider):
        """Test generation with HIGH thinking effort."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [
                        {"text": "Let me think...", "thought": True},
                        {"text": "The answer is 42."}
                    ]
                },
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "thoughtsTokenCount": 100
            }
        }
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            result = await provider.generate(
                model="gemma-4-31b-it",
                system_prompt="You are helpful",
                user_query="What is the meaning of life?",
                thinking_effort="deep"
            )
            
            assert result["text"] == "Let me think...The answer is 42."
            assert result["thoughts_token_count"] == 100
    
    @pytest.mark.anyio
    async def test_generate_safety_block(self, provider):
        """Test generation handles safety blocks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {
            "candidates": [{
                "finishReason": "SAFETY"
            }]
        }
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            from omega.errors import ProviderSafetyError
            with pytest.raises(ProviderSafetyError):
                await provider.generate(
                    model="gemma-4-31b-it",
                    system_prompt="Test",
                    user_query="Bad query"
                )
    
    @pytest.mark.anyio
    async def test_generate_timeout(self, provider):
        """Test generation handles timeout."""
        import httpx
        
        with patch.object(provider, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.TimeoutException("Timeout")
            mock_get_client.return_value = mock_client
            
            with pytest.raises(Exception) as exc_info:
                await provider.generate(
                    model="gemma-4-31b-it",
                    system_prompt="Test",
                    user_query="Hello"
                )
            
            # Should be ProviderTimeoutError
            assert "timeout" in str(exc_info.value).lower()


class TestGoogleCompatProviderIntegration:
    """Integration-style tests for GoogleCompatProvider."""
    
    @pytest.fixture(autouse=True)
    def reset_matrix(self):
        reset_capability_matrix()
        yield
        reset_capability_matrix()
    
    def test_gemma4_detection_regex(self):
        """Test Gemma 4 detection regex matches correctly."""
        import re
        pattern = re.compile(r"gemma-?4", re.IGNORECASE)
        
        assert pattern.search("gemma-4-31b-it") is not None
        assert pattern.search("gemma4-31b-it") is not None
        assert pattern.search("GEMMA-4-31B-IT") is not None
        assert pattern.search("google/gemma-4-31b-it") is not None
        assert pattern.search("gemma-3-27b-it") is None
    
    def test_binary_thinking_levels(self):
        """Test that Gemma 4 only supports MINIMAL and HIGH."""
        matrix = CapabilityMatrix()
        matrix.load()
        
        cap = matrix.get("gemma-4-31b-it")
        levels = cap.thinking_config.supported_levels
        
        assert levels == ["MINIMAL", "HIGH"]
        assert "LOW" not in levels
        assert "MEDIUM" not in levels
        assert "STANDARD" not in levels
    
    def test_thinking_mapping_canonical_to_provider(self):
        """Test canonical effort levels map to provider enums."""
        matrix = CapabilityMatrix()
        matrix.load()
        
        mapping = matrix.get_thinking_mapping("gemma-4-31b-it")
        
        # Canonical efforts map to binary provider levels
        assert mapping["minimal"] == "MINIMAL"
        assert mapping["low"] == "MINIMAL"
        assert mapping["standard"] == "MINIMAL"
        assert mapping["medium"] == "HIGH"
        assert mapping["high"] == "HIGH"
        assert mapping["deep"] == "HIGH"
        assert mapping["xhigh"] == "HIGH"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
