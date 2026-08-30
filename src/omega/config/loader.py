# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Config Loader — Public/Private Config Split with Deep Merge
AP: AP-CONFIG-LOADER-v1.0.0
⬡ OMEGA ⬡ P3 ⬡ config_loader ⬡ GITIGNORED-CONFIG

Implements R19 Soul Privacy Model Part 3:
Gitignored Config Split — public/ + private/ with runtime merge
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Merges public + private config with private taking precedence.

    Directory structure:
    config/
    ├── public/                    # Git-tracked
    │   ├── omega.yaml
    │   ├── models.yaml
    │   ├── providers.public.yaml  # Endpoints, model mappings, rate limits
    │   ├── wads/
    │   └── glossary.md
    │
    ├── private/                   # Gitignored, encrypted at rest
    │   ├── providers.private.yaml # API keys, secrets, OAuth tokens
    │   ├── vault.yaml             # Encrypted credential store
    │   └── local_overrides.yaml   # Machine-specific paths, hardware config
    │
    ├── .gitignore                 # Excludes private/
    └── config.yaml                # Loader config (optional)
    """

    def __init__(
        self,
        config_root: Union[str, Path] = "config",
        auto_decrypt: bool = True,
    ):
        """
        Initialize config loader.

        Args:
            config_root: Root config directory
            auto_decrypt: Whether to auto-decrypt encrypted values
        """
        self.config_root = Path(config_root)
        self.public_root = self.config_root / "public"
        self.private_root = self.config_root / "private"
        self.auto_decrypt = auto_decrypt

        # Cache for loaded configs
        self._cache: Dict[str, Any] = {}

    def _load_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file safely."""
        if not path.exists():
            return None
        try:
            content = path.read_text(encoding="utf-8")
            return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return None

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Private config overrides public config recursively.
        Lists are replaced (not merged) — last writer wins.
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override (including lists, scalars, None)
                result[key] = value

        return result

    def _decrypt_secrets(
        self, config: Dict[str, Any], encrypted_section: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decrypt secrets in config using encrypted section metadata.

        Expected encrypted section format:
        {
            "encrypted": {
                "providers.openrouter.api_key": {"cipher": "age", "key_id": "key1"},
                "providers.google.api_key": {"cipher": "age", "key_id": "key1"}
            }
        }
        """
        if not self.auto_decrypt or not encrypted_section:
            return config

        # In production, this would call age/GPG/sops decryption
        # For now, return config as-is (secrets should be in plaintext in private config
        # which is gitignored and encrypted at rest via restic)
        logger.debug("Auto-decrypt enabled but no decryptor implemented — returning plaintext")
        return config

    def load_providers(self) -> Dict[str, Any]:
        """Load providers config: public + private merge."""
        cache_key = "providers"
        if cache_key in self._cache:
            return self._cache[cache_key]

        public = self._load_yaml(self.public_root / "providers.public.yaml")
        private = self._load_yaml(self.private_root / "providers.private.yaml")

        merged = self._deep_merge(public or {}, private or {})

        # Handle encrypted section
        if private and "encrypted" in private:
            merged = self._decrypt_secrets(merged, private["encrypted"])

        self._cache[cache_key] = merged
        return merged

    def load_omega(self) -> Dict[str, Any]:
        """Load omega.yaml (public only)."""
        cache_key = "omega"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = self._load_yaml(self.public_root / "omega.yaml") or {}
        self._cache[cache_key] = config
        return config

    def load_models(self) -> Dict[str, Any]:
        """Load models.yaml (public only)."""
        cache_key = "models"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = self._load_yaml(self.public_root / "models.yaml") or {}
        self._cache[cache_key] = config
        return config

    def load_wads(self) -> Dict[str, Any]:
        """Load WAD definitions (public only)."""
        cache_key = "wads"
        if cache_key in self._cache:
            return self._cache[cache_key]

        wads_dir = self.public_root / "wads"
        wads = {}

        if wads_dir.exists():
            for wad_file in wads_dir.glob("*.yaml"):
                wad_name = wad_file.stem
                wads[wad_name] = self._load_yaml(wad_file) or {}

        self._cache[cache_key] = wads
        return wads

    def load_vault(self) -> Dict[str, Any]:
        """Load encrypted vault (private only)."""
        cache_key = "vault"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = self._load_yaml(self.private_root / "vault.yaml") or {}
        self._cache[cache_key] = config
        return config

    def load_local_overrides(self) -> Dict[str, Any]:
        """Load machine-specific overrides (private only)."""
        cache_key = "local_overrides"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = self._load_yaml(self.private_root / "local_overrides.yaml") or {}
        self._cache[cache_key] = config
        return config

    def load_all(self) -> Dict[str, Any]:
        """Load all configs as a unified dict."""
        return {
            "omega": self.load_omega(),
            "models": self.load_models(),
            "providers": self.load_providers(),
            "wads": self.load_wads(),
            "vault": self.load_vault(),
            "local_overrides": self.load_local_overrides(),
        }

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get merged config for a specific provider."""
        providers = self.load_providers()
        return providers.get(provider_name, {})

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get model config by name."""
        models = self.load_models()
        return models.get(model_name, {})

    def reload(self) -> None:
        """Clear cache and reload all configs."""
        self._cache.clear()

    def ensure_private_dirs(self) -> None:
        """Ensure private directories exist with proper permissions."""
        self.private_root.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions (owner read/write only)
        self.private_root.chmod(0o700)

        # Create .gitignore if not exists
        gitignore = self.config_root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("""# Private config — NEVER COMMIT
private/
providers.private.yaml
vault.yaml
local_overrides.yaml
*.enc
*.age
*.key
""")

    def create_private_templates(self) -> None:
        """Create template private config files if they don't exist."""
        self.ensure_private_dirs()

        templates = {
            "providers.private.yaml": """# Private provider configuration — GITIGNORED
# API keys, secrets, OAuth tokens
# This file is NEVER committed to git

# Example:
# openrouter:
#   api_key: "sk-or-v1-..."
#   default_model: "anthropic/claude-3-opus"
#
# google:
#   api_key: "AIza..."
#   project_id: "my-project"
#
# antigravity:
#   oauth_tokens: {}
#   account_ids: []
""",
            "vault.yaml": """# Encrypted credential vault — GITIGNORED
# Use age/GPG/sops for encryption at rest

# Example:
# credentials:
#   github_token:
#     value: "ghp_..."
#     encrypted: true
#     cipher: "age"
#     key_id: "age1..."
""",
            "local_overrides.yaml": """# Machine-specific overrides — GITIGNORED
# Paths, hardware config, local model locations

# Example:
# paths:
#   models_dir: "/mnt/models"
#   data_dir: "/home/user/omega-data"
#
# hardware:
#   gpu: "nvidia"
#   cuda_version: "12.4"
#   threads: 8
""",
        }

        for filename, content in templates.items():
            path = self.private_root / filename
            if not path.exists():
                path.write_text(content)
                path.chmod(0o600)
                logger.info(f"Created private config template: {path}")


# =============================================================================
# PROVIDER CONFIG MODEL
# =============================================================================


class ProvidersConfig:
    """Typed access to providers configuration."""

    def __init__(self, loader: ConfigLoader):
        self.loader = loader
        self._config = loader.load_providers()

    def get(self, provider: str, key: str, default: Any = None) -> Any:
        """Get nested config value using dot notation."""
        provider_config = self._config.get(provider, {})
        keys = key.split(".")
        value = provider_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        return self.get(provider, "api_key")

    def get_oauth_tokens(self, provider: str) -> Dict[str, Any]:
        """Get OAuth tokens for provider."""
        return self.get(provider, "oauth_tokens", {})

    def get_all_providers(self) -> Dict[str, Any]:
        """Get all provider configs."""
        return self._config.copy()

    def reload(self) -> None:
        """Reload from disk."""
        self.loader.reload()
        self._config = self.loader.load_providers()


# =============================================================================
# FACTORY
# =============================================================================


def create_config_loader(
    config_root: Union[str, Path] = "config",
    auto_decrypt: bool = True,
) -> ConfigLoader:
    """Factory: create ConfigLoader with default or custom config."""
    loader = ConfigLoader(config_root=config_root, auto_decrypt=auto_decrypt)
    loader.ensure_private_dirs()
    loader.create_private_templates()
    return loader


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ConfigLoader",
    "ProvidersConfig",
    "create_config_loader",
]
