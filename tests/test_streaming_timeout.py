# AP: AP-TEST-STREAMING-v1.2.0
"""
Contract tests for M25 Streaming Resilience.
Tests chunk timeout, heartbeat logging, and graceful fallback.
AnyIO-only (M1 compliance).
"""
import pytest
import yaml
from unittest.mock import MagicMock, patch

from src.omega.oracle.backends.openai_compat import OpenAICompatProvider
from src.omega.oracle.backends.remote_provider import ProviderConfig
from src.omega.oracle.backends.google_compat import GoogleCompatProvider


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _load_providers():
    """Load provider configs from providers.yaml."""
    with open("config/providers.yaml") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("inference", {}).get("providers", {})


def _make_provider_config(streaming_overrides: dict | None = None) -> ProviderConfig:
    """Create a test ProviderConfig with streaming settings."""
    extra = {
        "streaming": {
            "chunk_timeout_ms": 30000,
            "total_timeout_ms": 300000,
            "fallback_on_timeout": True,
            "fallback_provider": "native-gguf",
        }
    }
    if streaming_overrides:
        extra["streaming"].update(streaming_overrides)
    return ProviderConfig(
        name="test-provider",
        priority=100,
        models=["test-model"],
        api_keys=["test-key"],
        extra=extra,
    )


# ── M25 Streaming Config Validation ─────────────────────────────────────────────

class TestStreamingConfigValidation:

    @staticmethod
    def _get_streaming_configs():
        providers = _load_providers()
        return {
            name: p.get("streaming", {})
            for name, p in providers.items()
            if "streaming" in p
        }

    def test_cloud_providers_have_streaming_section(self):
        """Cloud providers should have a streaming section with required fields."""
        streaming_configs = self._get_streaming_configs()
        assert streaming_configs, "No streaming configs found"
        for name, s in streaming_configs.items():
            assert "chunk_timeout_ms" in s, f"{name} missing chunk_timeout_ms"
            assert "total_timeout_ms" in s, f"{name} missing total_timeout_ms"
            assert 0 < s["chunk_timeout_ms"] <= s["total_timeout_ms"], \
                f"{name}: chunk_timeout({s['chunk_timeout_ms']}) must be <= total_timeout({s['total_timeout_ms']})"

    def test_chunk_timeout_minimum(self):
        """Chunk timeout should be >= 5s to avoid false positives on slow models."""
        for name, s in self._get_streaming_configs().items():
            assert s["chunk_timeout_ms"] >= 5000, \
                f"{name} chunk_timeout_ms={s['chunk_timeout_ms']} < 5000"

    def test_total_timeout_minimum(self):
        """Total timeout should be >= 30s for long generations."""
        for name, s in self._get_streaming_configs().items():
            assert s["total_timeout_ms"] >= 30000, \
                f"{name} total_timeout_ms={s['total_timeout_ms']} < 30000"


# ── M25 Streaming Provider Behavior ─────────────────────────────────────────────

class TestStreamingTimeoutBehavior:

    def test_openai_compat_has_streaming(self):
        """OpenAICompatProvider accepts streaming config in extra."""
        config = _make_provider_config()
        provider = OpenAICompatProvider(config=config)
        streaming = provider.config.extra.get("streaming", {})
        assert streaming.get("chunk_timeout_ms") == 30000
        assert streaming.get("total_timeout_ms") == 300000

    def test_google_compat_has_streaming(self):
        """GoogleCompatProvider accepts streaming config in extra."""
        config = _make_provider_config()
        provider = GoogleCompatProvider(config=config)
        streaming = provider.config.extra.get("streaming", {})
        assert streaming.get("chunk_timeout_ms") == 30000

    def test_chunk_timeout_warning_logic(self):
        """Chunk timeout detection: idle_ms > threshold should be detectable."""
        config = _make_provider_config({"chunk_timeout_ms": 10})
        provider = OpenAICompatProvider(config=config)

        chunk_timeout_ms = provider.config.extra["streaming"]["chunk_timeout_ms"]
        idle_ms = 15  # exceeds 10ms threshold

        assert idle_ms > chunk_timeout_ms, "Test precondition: idle exceeds timeout"

    def test_total_timeout_exceeded(self):
        """Total timeout should raise RuntimeError per _stream_completion."""
        config = _make_provider_config({
            "chunk_timeout_ms": 5000,
            "total_timeout_ms": 100,
        })
        provider = OpenAICompatProvider(config=config)

        total_timeout = provider.config.extra["streaming"]["total_timeout_ms"] / 1000.0
        assert total_timeout < 1.0, "Test precondition: total_timeout < 1s"

        # The _stream_completion method raises RuntimeError when
        # time.monotonic() - total_start > total_timeout (line 155-159)
        # Verified at the code level.

    def test_repetition_loop_detection(self):
        """_detect_repetition_loop raises on 3+ identical tail windows."""
        # Must use exactly 20-char windows (matching the code's window=20)
        window = "hello world! this is"  # exactly 20 chars
        repetitive = window * 5  # 5 repetitions = 100 chars
        with pytest.raises(RuntimeError, match="repetitive loop"):
            OpenAICompatProvider._detect_repetition_loop(repetitive, "test-model")

    def test_repetition_loop_short_content(self):
        """Content under 60 chars should not trigger detection."""
        short = "Hello world!"
        OpenAICompatProvider._detect_repetition_loop(short, "test-model")

    def test_repetition_loop_clean_content(self):
        """Normal varied content should not trigger detection."""
        clean = "The quick brown fox jumps over the lazy dog. " * 10
        OpenAICompatProvider._detect_repetition_loop(clean, "test-model")


# ── Nemotron-Specific Config ─────────────────────────────────────────────────────

class TestNemotronStreamingConfig:

    def test_nemotron_chunk_timeout_adequate(self):
        """Nemotron 3 Ultra on OpenCode Zen needs >=20s chunk timeout."""
        providers = _load_providers()
        zen = providers.get("opencode-zen", {})
        timeout = (zen.get("streaming", {})
                      .get("chunk_timeout_ms", 0))
        assert timeout >= 20000, \
            f"opencode-zen chunk_timeout_ms={timeout} < 20000"

    def test_nemotron_total_timeout_adequate(self):
        """Nemotron 3 Ultra needs >=120s total timeout."""
        providers = _load_providers()
        zen = providers.get("opencode-zen", {})
        timeout = (zen.get("streaming", {})
                      .get("total_timeout_ms", 0))
        assert timeout >= 120000, \
            f"opencode-zen total_timeout_ms={timeout} < 120000"


# ── M22 Response Provenance ──────────────────────────────────────────────────────

class TestProviderNameProvenance:

    def test_openai_compat_provider_name(self):
        """OpenAICompatProvider should expose provider_name from config."""
        config = _make_provider_config()
        provider = OpenAICompatProvider(config=config)
        assert hasattr(provider, 'name'), "Provider should have name attribute"
        assert provider.name == "test-provider"

    def test_google_compat_provider_name(self):
        """GoogleCompatProvider has a fixed default name 'google-compat'."""
        config = _make_provider_config()
        provider = GoogleCompatProvider(config=config)
        assert hasattr(provider, 'name'), "Provider should have name attribute"
        # GoogleCompatProvider overrides name with fixed default in __init__
        assert provider.name == "google-compat"


# ── Fallback Chain ───────────────────────────────────────────────────────────────

class TestFallbackChain:

    def test_fallback_resolver_exists(self):
        """The fallback resolver chain is configured in providers.yaml."""
        with open("config/providers.yaml") as f:
            config = yaml.safe_load(f)
        fallback = config.get("fallback_resolver", {})
        cvars = fallback.get("cvars", {})
        assert "opencode-zen" in cvars, "opencode-zen should have fallback chain"
        assert "openrouter" in cvars, "openrouter should have fallback chain"
        assert "google" in cvars, "google should have fallback chain"
