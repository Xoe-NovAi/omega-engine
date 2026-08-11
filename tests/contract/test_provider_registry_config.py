# AP: AP-TEST-PROVIDER-REGISTRY-CONFIG-20260809
# 🔱 ProviderRegistry Config Loading Test
# Verifies ProviderRegistry correctly loads providers from config/providers.yaml

import tempfile
import yaml
from pathlib import Path
from src.omega.oracle.provider_registry import ProviderRegistry


class TestProviderRegistryConfigLoading:
    """Test ProviderRegistry config loading path."""

    def test_loads_providers_from_yaml(self):
        """ProviderRegistry loads providers from config.yaml with correct is_cloud values."""
        # Arrange: Create mock config.yaml matching actual structure
        mock_config = {
            "inference": {
                "fallback_chain": [
                    {"provider": "test-local", "priority": 0, "enabled": True, "is_cloud": False},
                    {"provider": "test-cloud-1", "priority": 1, "enabled": True, "is_cloud": True},
                    {"provider": "test-cloud-2", "priority": 2, "enabled": True, "is_cloud": True},
                ],
                "providers": {
                    "test-local": {"priority": 0, "enabled": True, "supported_models": ["test-model-local"]},
                    "test-cloud-1": {"priority": 1, "enabled": True, "supported_models": ["test-model-cloud-1"]},
                    "test-cloud-2": {"priority": 2, "enabled": True, "supported_models": ["test-model-cloud-2"]},
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            # Act: Load registry from mock config
            registry = ProviderRegistry.from_config_path(config_path)

            # Assert: All 3 providers loaded
            all_providers = registry.all_providers()
            assert len(all_providers) == 3, f"Expected 3 providers, got {len(all_providers)}"

            # Assert: Provider names match
            provider_names = set(all_providers.keys())
            assert provider_names == {"test-local", "test-cloud-1", "test-cloud-2"}

            # Assert: is_cloud values match mock
            for name, is_cloud in all_providers.items():
                if name == "test-local":
                    assert is_cloud is False, f"{name} should be local"
                else:
                    assert is_cloud is True, f"{name} should be cloud"

    def test_unknown_provider_defaults_to_cloud(self):
        """Unknown provider (not in config) defaults to cloud (pessimistic per M7)."""
        mock_config = {
            "inference": {
                "fallback_chain": [
                    {"provider": "known-local", "priority": 0, "enabled": True, "is_cloud": False},
                ],
                "providers": {
                    "known-local": {"priority": 0, "enabled": True, "supported_models": ["known-model"]},
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            registry = ProviderRegistry.from_config_path(config_path)

            # Unknown provider should default to cloud (pessimistic)
            assert registry.is_cloud("unknown-provider") is True
            # Known provider should match config
            assert registry.is_cloud("known-local") is False

    def test_synthetic_provider_exclusion(self):
        """Synthetic providers (mock, fallback) are excluded from sovereignty stats."""
        mock_config = {
            "inference": {
                "fallback_chain": [
                    {"provider": "real-local", "priority": 0, "enabled": True, "is_cloud": False},
                    {"provider": "mock", "priority": 99, "enabled": True, "is_cloud": False},
                    {"provider": "fallback", "priority": 100, "enabled": True, "is_cloud": False},
                ],
                "providers": {
                    "real-local": {"priority": 0, "enabled": True, "supported_models": ["real-model"]},
                    "mock": {"priority": 99, "enabled": True, "supported_models": ["mock-model"]},
                    "fallback": {"priority": 100, "enabled": True, "supported_models": ["fallback-model"]},
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(yaml.dump(mock_config))

            registry = ProviderRegistry.from_config_path(config_path)

            # Synthetic providers should be marked as such
            assert registry.is_synthetic("mock") is True
            assert registry.is_synthetic("fallback") is True
            assert registry.is_synthetic("real-local") is False