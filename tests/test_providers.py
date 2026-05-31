import os
from unittest.mock import AsyncMock, patch

import pytest
import httpx

from omega.oracle.providers import (
    BaseProvider,
    MockProvider,
    GoogleAIProvider,
    LocallmsterProvider,
    OllamaProvider,
    NativeGGUFProvider,
)


class TestBaseProvider:
    """BaseProvider cannot be instantiated directly (ABC)."""

    def test_cannot_instantiate(self):
        """BaseProvider should raise TypeError due to abstract methods."""
        with pytest.raises(TypeError):
            BaseProvider("test", {})


class TestMockProvider:
    @pytest.fixture
    def provider(self):
        return MockProvider("mock", {})

    @pytest.mark.anyio
    async def test_is_available(self, provider):
        """Mock provider is always available."""
        assert await provider.is_available() is True

    @pytest.mark.anyio
    async def test_generate_returns_string(self, provider):
        """Mock generate returns a helpful setup message."""
        result = await provider.generate("qwen3-test", "system", "hello", 0.7, 128)
        assert result is not None
        assert "Omega Engine is running in setup mode" in result
        assert "OPENROUTER_API_KEY" in result
        assert "inference backend" in result


class TestGoogleAIProvider:
    @pytest.fixture
    def provider(self):
        return GoogleAIProvider("google", {})

    @pytest.mark.anyio
    async def test_is_available_with_key(self, provider):
        """is_available returns True when GOOGLE_API_KEY is set."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            assert await provider.is_available() is True

    @pytest.mark.anyio
    async def test_is_available_no_key(self, provider):
        """is_available returns False when GOOGLE_API_KEY is not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert await provider.is_available() is False

    @pytest.mark.anyio
    async def test_generate_success(self, provider):
        """Successful API call returns parsed text."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "  Hello, world!  "}]
                }
            }]
        }

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                result = await provider.generate(
                    "gemma-4-31b", "be helpful", "hi", 0.7, 256
                )
                assert result == "Hello, world!"

    @pytest.mark.anyio
    async def test_generate_missing_candidates(self, provider):
        """API response without candidates returns None."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"candidates": []}

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                result = await provider.generate(
                    "gemma-4-31b", "be helpful", "hi", 0.7, 256
                )
                assert result is None

    @pytest.mark.anyio
    async def test_generate_malformed_response(self, provider):
        """Malformed API response returns None without raising."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                result = await provider.generate(
                    "gemma-4-31b", "be helpful", "hi", 0.7, 256
                )
                assert result is None

    @pytest.mark.anyio
    async def test_generate_http_error(self, provider):
        """HTTP errors propagate as httpx.HTTPStatusError."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=AsyncMock(), response=mock_response
        )

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                with pytest.raises(httpx.HTTPStatusError):
                    await provider.generate(
                        "gemma-4-31b", "be helpful", "hi", 0.7, 256
                    )


class TestLocallmsterProvider:
    @pytest.fixture
    def provider(self):
        return LocallmsterProvider("lmster", {"endpoint": "http://127.0.0.1:1234"})

    @pytest.mark.anyio
    async def test_is_available_success(self, provider):
        """is_available returns True when server responds."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            available = await provider.is_available()
            assert available is True

    @pytest.mark.anyio
    async def test_is_available_timeout(self, provider):
        """is_available returns False on connection error."""
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
            available = await provider.is_available()
            assert available is False

    @pytest.mark.anyio
    async def test_generate_with_reasoning(self, provider):
        """generate returns content with reasoning_preamble."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "  Final answer  ",
                    "reasoning_content": "  I think, therefore...  ",
                }
            }]
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await provider.generate(
                "qwen3-1.7b", "system", "query", 0.7, 1024
            )
            assert result is not None
            assert "I think, therefore..." in result
            assert "Final answer" in result

    @pytest.mark.anyio
    async def test_generate_no_reasoning(self, provider):
        """generate returns just content when no reasoning_content."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Just the answer",
                    "reasoning_content": "",
                }
            }]
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await provider.generate(
                "qwen3-1.7b", "system", "query", 0.7, 1024
            )
            assert result == "Just the answer"

    @pytest.mark.anyio
    async def test_generate_empty_content(self, provider):
        """generate returns empty string when content is empty."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "  ",
                    "reasoning_content": "",
                }
            }]
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await provider.generate(
                "qwen3-1.7b", "system", "query", 0.7, 1024
            )
            assert result == ""


class TestOllamaProvider:
    @pytest.fixture
    def provider(self):
        return OllamaProvider("ollama", {"endpoint": "http://127.0.0.1:11434"})

    @pytest.mark.anyio
    async def test_is_available_success(self, provider):
        """is_available returns True when /api/tags responds."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            available = await provider.is_available()
            assert available is True

    @pytest.mark.anyio
    async def test_is_available_failure(self, provider):
        """is_available returns False on connection error."""
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
            available = await provider.is_available()
            assert available is False

    @pytest.mark.anyio
    async def test_generate(self, provider):
        """generate returns parsed content."""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Ollama response",
                }
            }]
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await provider.generate(
                "llama3.2", "system", "query", 0.5, 512
            )
            assert result == "Ollama response"


class TestNativeGGUFProvider:
    @pytest.fixture
    def provider(self):
        return NativeGGUFProvider(
            "native",
            {"model_path": "/tmp/nonexistent_model.gguf", "n_ctx": 2048},
        )

    @pytest.mark.anyio
    async def test_is_available_no_model_path(self):
        """is_available returns False when model_path doesn't exist."""
        p = NativeGGUFProvider("native", {"model_path": "/nonexistent.gguf"})
        result = await p.is_available()
        assert result is False

    @pytest.mark.anyio
    async def test_is_available_no_model_path_key(self):
        """is_available returns False when model_path not in config."""
        p = NativeGGUFProvider("native", {})
        result = await p.is_available()
        assert result is False

    def test_init_expands_tilde_path(self):
        """__init__ expands ~/ in model_path."""
        p = NativeGGUFProvider("native", {"model_path": "~/test.gguf"})
        assert p.model_path is not None
        assert "~" not in p.model_path
        assert p.model_path.startswith("/")

    def test_init_threads_from_config(self):
        """__init__ reads n_threads from config dict."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf", "n_threads": 4})
        assert p._n_threads == 4

    def test_init_default_threads(self):
        """__init__ defaults to 6 threads when not in config."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf"})
        assert p._n_threads == 6

    def test_n_threads_is_int(self, provider):
        """n_threads is always an int."""
        assert isinstance(provider._n_threads, int)

    def test_init_cores_from_config(self):
        """__init__ reads cores from config dict."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf", "cores": [0, 2, 4]})
        assert p._cores == [0, 2, 4]

    def test_init_default_cores(self):
        """__init__ defaults to Zen 2 physical cores."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf"})
        assert p._cores == [0, 2, 4, 6]

    def test_init_kv_cache_types(self):
        """__init__ reads type_k and type_v from config."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf", "type_k": 0, "type_v": 0})
        assert p._type_k == 0
        assert p._type_v == 0

    def test_init_default_kv_cache(self):
        """__init__ defaults to q8_0 (enum 8) for KV cache."""
        p = NativeGGUFProvider("native", {"model_path": "/tmp/test.gguf"})
        assert p._type_k == 8
        assert p._type_v == 8

    def test_get_status(self, provider):
        """get_status returns provider state dict."""
        status = provider.get_status()
        assert status["provider"] == "native"
        assert status["loaded"] is False
        assert status["cores"] == [0, 2, 4, 6]
        assert status["threads"] == 6
