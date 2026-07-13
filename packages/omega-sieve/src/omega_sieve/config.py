"""Configuration loader for omega-sieve.

Reads from ~/.config/omega-sieve/config.yaml with sensible defaults.
All providers are optional — the sieve degrades gracefully.
"""

# AP: AP-OMEGA-SIEVE-CONFIG-v1.0.0

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import yaml


DEFAULT_CONFIG_PATH = Path("~/.config/omega-sieve/config.yaml").expanduser()


@dataclass
class ProviderConfig:
    """API provider configuration."""
    api_key: str = ""
    base_url: str = ""
    enabled: bool = True


@dataclass
class BudgetConfig:
    """Budget limits per provider per day."""
    exa_max_calls: int = 100
    firecrawl_max_calls: int = 100
    openrouter_max_calls: int = 500
    warn_at: float = 0.8  # Warn when 80% of budget consumed


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    enabled: bool = False
    datacenter: list[str] = field(default_factory=list)
    residential: list[str] = field(default_factory=list)


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    backend: str = "sqlite"  # "sqlite" | "memory" | "none"
    path: str = str(Path("~/.cache/omega-sieve/").expanduser())
    ttl_days: int = 7


@dataclass
class DomainConfig:
    """Domain-specific extraction rules."""
    allowlist: dict[str, str] = field(default_factory=lambda: {
        "gutenberg": r"^https?://[^.]*\.gutenberg\.org/.*$",
        "arxiv": r"^https?://arxiv\.org/.*$",
        "pubmed": r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/.*$",
        "wikipedia": r"^https?://[^.]*\.wikipedia\.org/.*$",
        "github": r"^https?://github\.com/.*$",
    })


@dataclass
class SieveConfig:
    """Top-level configuration for omega-sieve.

    All fields have defaults — you can use the sieve with zero config.
    """
    providers: dict[str, ProviderConfig] = field(default_factory=lambda: {
        "exa": ProviderConfig(api_key=os.getenv("EXA_API_KEY", "")),
        "firecrawl": ProviderConfig(api_key=os.getenv("FIRECRAWL_API_KEY", "")),
        "openrouter": ProviderConfig(api_key=os.getenv("OPENROUTER_API_KEY", "")),
    })
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    domains: DomainConfig = field(default_factory=DomainConfig)
    searxng_url: str = os.getenv("SEARXNG_URL", "http://localhost:4004")

    @classmethod
    def from_dict(cls, d: dict) -> "SieveConfig":
        """Create config from dictionary (YAML load result)."""
        providers = {}
        for name, cfg in d.get("providers", {}).items():
            providers[name] = ProviderConfig(**cfg) if isinstance(cfg, dict) else ProviderConfig(api_key=str(cfg))

        return cls(
            providers=providers,
            budget=BudgetConfig(**(d.get("budget", {}))),
            proxy=ProxyConfig(**(d.get("proxy", {}))),
            cache=CacheConfig(**(d.get("cache", {}))),
            domains=DomainConfig(**(d.get("domains", {}))),
            searxng_url=d.get("searxng_url", cls.searxng_url),
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary (for YAML dump)."""
        return {
            "providers": {k: {"api_key": v.api_key[:8] + "..." if v.api_key else "", "base_url": v.base_url, "enabled": v.enabled} for k, v in self.providers.items()},
            "budget": {"exa_max_calls": self.budget.exa_max_calls, "firecrawl_max_calls": self.budget.firecrawl_max_calls, "openrouter_max_calls": self.budget.openrouter_max_calls, "warn_at": self.budget.warn_at},
            "proxy": {"enabled": self.proxy.enabled},
            "cache": {"enabled": self.cache.enabled, "backend": self.cache.backend, "path": self.cache.path, "ttl_days": self.cache.ttl_days},
            "domains": {"allowlist": dict(self.domains.allowlist)},
            "searxng_url": self.searxng_url,
        }


def load_config(path: Optional[str] = None) -> SieveConfig:
    """Load configuration from YAML file.

    Args:
        path: Path to config file. Defaults to ~/.config/omega-sieve/config.yaml.

    Returns:
        SieveConfig with merged defaults and file values.
    """
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return SieveConfig()

    with open(config_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return SieveConfig()

    return SieveConfig.from_dict(data)


def init_config(path: Optional[str] = None) -> SieveConfig:
    """Initialize default config file if it doesn't exist.

    Args:
        path: Path to config file. Defaults to ~/.config/omega-sieve/config.yaml.

    Returns:
        Loaded SieveConfig.
    """
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = SieveConfig()
        with open(config_path, "w") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)
        return config

    return load_config(path)