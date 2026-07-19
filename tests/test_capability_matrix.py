# 🔱 Capability Matrix Tests — Gemma 4 Week 1 Step 2
# ⬡ OMEGA ⬡ P10 ⬡ trc_test_capability_matrix ⬡ v0.1.0 ⬡ 2026-07-19

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.oracle.capability_matrix import (
    CapabilityMatrix,
    ModelCapability,
    ProviderConfig,
    ThinkingConfig,
    QuotaTier,
    get_capability_matrix,
    reset_capability_matrix
)


class TestCapabilityMatrix:
    """Test suite for CapabilityMatrix loader and validator."""
    
    @pytest.fixture(autouse=True)
    def reset_matrix(self):
        """Reset global matrix before each test."""
        reset_capability_matrix()
        yield
        reset_capability_matrix()
    
    def test_load_matrix(self):
        """Test that capability matrix loads without error."""
        matrix = get_capability_matrix()
        models = matrix.load()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        assert "gemma-4-31b-it" in models
    
    def test_gemma4_capability_exists(self):
        """Test Gemma 4 31B capability is loaded correctly."""
        matrix = get_capability_matrix()
        matrix.load()
        
        capability = matrix.get("gemma-4-31b-it")
        assert capability is not None
        assert capability.model_id == "gemma-4-31b-it"
        assert capability.display_name == "Gemma 4 31B Instruct"
        assert capability.max_context == 32768
        assert capability.max_output == 8192
    
    def test_gemma4_thinking_config(self):
        """Test Gemma 4 thinking configuration (binary MINIMAL/HIGH)."""
        matrix = get_capability_matrix()
        matrix.load()
        
        capability = matrix.get("gemma-4-31b-it")
        assert capability.thinking_config is not None
        assert capability.thinking_config.supported_levels == ["MINIMAL", "HIGH"]
        assert capability.thinking_config.detection_regex == "/gemma-?4/i"
        assert capability.thinking_config.default == "MINIMAL"
        
        # Check thinking mapping
        mapping = capability.thinking_config.thinking_mapping
        assert mapping["minimal"] == "MINIMAL"
        assert mapping["standard"] == "MINIMAL"
        assert mapping["deep"] == "HIGH"
    
    def test_gemma4_provider_ids(self):
        """Test Gemma 4 provider ID mappings."""
        matrix = get_capability_matrix()
        matrix.load()
        
        capability = matrix.get("gemma-4-31b-it")
        provider_ids = capability.provider_ids
        
        assert "google-ai-studio" in provider_ids
        assert "google-vertex-ai" in provider_ids
        assert "openrouter" in provider_ids
        assert "native-gguf" in provider_ids
        assert provider_ids["google-ai-studio"] == "gemma-4-31b-it"
        assert provider_ids["openrouter"] == "google/gemma-4-31b-it"
    
    def test_gemma4_quota_tiers(self):
        """Test Gemma 4 quota configuration."""
        matrix = get_capability_matrix()
        matrix.load()
        
        capability = matrix.get("gemma-4-31b-it")
        quota = capability.quota
        
        assert "free_tier" in quota
        assert quota["free_tier"].rpm == 15
        assert quota["free_tier"].tpm == 16000
        assert quota["free_tier"].rpd == 1500
        assert quota["free_tier"].rolling_window_ms == 60000
        
        assert "tier_1" in quota
        assert quota["tier_1"].rpm == 60
    
    def test_fuzzy_match_detection_regex(self):
        """Test fuzzy matching with Gemma 4 detection regex."""
        matrix = get_capability_matrix()
        matrix.load()
        
        # Test various Gemma 4 model ID formats
        capability = matrix.get_by_fuzzy_match("gemma-4-31b-it")
        assert capability is not None
        assert capability.model_id == "gemma-4-31b-it"
        
        capability = matrix.get_by_fuzzy_match("gemma4-31b-it")
        assert capability is not None
        
        capability = matrix.get_by_fuzzy_match("google/gemma-4-31b-it")
        assert capability is not None
    
    def test_supports_thinking(self):
        """Test thinking support detection."""
        matrix = get_capability_matrix()
        matrix.load()
        
        assert matrix.supports_thinking("gemma-4-31b-it") is True
        assert matrix.supports_thinking("gemma-4-26b-it") is True
        assert matrix.supports_thinking("gemma-4-12b-unified") is True
        
        # Non-thinking models should return False
        # (We don't have non-thinking models in test config, but the method should work)
    
    def test_get_thinking_levels(self):
        """Test getting supported thinking levels."""
        matrix = get_capability_matrix()
        matrix.load()
        
        levels = matrix.get_thinking_levels("gemma-4-31b-it")
        assert levels == ["MINIMAL", "HIGH"]
        
        levels = matrix.get_thinking_levels("gemma-4-12b-unified")
        assert levels == ["MINIMAL", "HIGH"]
    
    def test_get_thinking_mapping(self):
        """Test canonical effort to provider enum mapping."""
        matrix = get_capability_matrix()
        matrix.load()
        
        mapping = matrix.get_thinking_mapping("gemma-4-31b-it")
        assert mapping["minimal"] == "MINIMAL"
        assert mapping["standard"] == "MINIMAL"
        assert mapping["deep"] == "HIGH"
        assert mapping["high"] == "HIGH"
    
    def test_provider_configs(self):
        """Test provider configurations are loaded."""
        matrix = get_capability_matrix()
        matrix.load()
        
        providers = matrix.get_all_providers()
        assert "google-ai-studio" in providers
        assert "google-vertex-ai" in providers
        assert "openrouter" in providers
        assert "native-gguf" in providers
        
        google_config = providers["google-ai-studio"]
        assert google_config.auth_type == "api_key"
        assert google_config.thinking_schema == "thinking_level"
        assert google_config.model_id_format == "bare"
        assert google_config.id_prefix_to_strip == "google/"
    
    def test_normalize_model_id(self):
        """Test model ID normalization for different providers."""
        matrix = get_capability_matrix()
        matrix.load()
        
        # OpenRouter keeps :free suffix
        normalized = matrix.normalize_model_id("google/gemma-4-31b-it:free", "openrouter")
        assert normalized == "google/gemma-4-31b-it:free"
        
        # Google AI Studio strips google/ prefix and :free suffix
        normalized = matrix.normalize_model_id("google/gemma-4-31b-it:free", "google-ai-studio")
        assert normalized == "gemma-4-31b-it"
        
        # Vertex AI same as AI Studio
        normalized = matrix.normalize_model_id("google/gemma-4-31b-it", "google-vertex-ai")
        assert normalized == "gemma-4-31b-it"
    
    def test_routing_rules(self):
        """Test routing rules are loaded."""
        matrix = get_capability_matrix()
        matrix.load()
        
        default_rules = matrix.get_routing_rules("default")
        assert "strategy" in default_rules
        assert default_rules["strategy"] == "capability_first"
        
        thinking_rules = matrix.get_routing_rules("thinking_deep")
        assert thinking_rules["strategy"] == "capability_first"
        assert "native-gguf" in thinking_rules["preference"]
    
    def test_gemma4_12b_mtp_drafter(self):
        """Test Gemma 4 12B has MTP drafter config."""
        matrix = get_capability_matrix()
        matrix.load()
        
        capability = matrix.get("gemma-4-12b-unified")
        assert capability.mtp_drafter is not None
        assert capability.mtp_drafter["layers"] == 6
        assert capability.mtp_drafter["speedup"] == "2-3x"
        assert capability.max_context == 262144  # 256K context
    
    def test_thinking_token_tracking_config(self):
        """Test thinking token tracking configuration."""
        matrix = get_capability_matrix()
        matrix.load()
        
        tracking = matrix._thinking_token_tracking
        assert tracking["budget_multiplier"] == 3.0
        assert tracking["track_per_response"] is True
        assert "thoughts_token_count" in tracking["fields"]
        assert tracking["estimate_before_request"] is True
    
    def test_health_monitoring_config(self):
        """Test health monitoring configuration."""
        matrix = get_capability_matrix()
        matrix.load()
        
        health = matrix._health_monitoring
        assert health["quota_check_interval_ms"] == 60000
        assert health["circuit_breaker"]["quota_errors_trip_circuit"] is False
        assert health["streaming"]["per_chunk_timeout_ms"] == 30000
        assert health["streaming"]["total_timeout_ms"] == 300000
        assert health["streaming"]["graceful_fallback"] is True


class TestCapabilityMatrixValidation:
    """Test validation and error handling."""
    
    @pytest.fixture(autouse=True)
    def reset_matrix(self):
        reset_capability_matrix()
        yield
        reset_capability_matrix()
    
    def test_missing_config_raises(self):
        """Test that missing config file raises FileNotFoundError."""
        matrix = CapabilityMatrix(Path("/nonexistent/path.yaml"))
        with pytest.raises(FileNotFoundError):
            matrix.load()
    
    def test_invalid_yaml_raises(self, tmp_path):
        """Test that invalid YAML raises error."""
        bad_config = tmp_path / "bad.yaml"
        bad_config.write_text("invalid: yaml: [")
        
        matrix = CapabilityMatrix(bad_config)
        with pytest.raises(yaml.YAMLError):
            matrix.load()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
