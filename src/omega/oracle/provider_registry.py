"""Single source of truth for provider capability metadata (M7/M22).

Reads ``is_cloud`` from ``config/providers.yaml`` — the only authoritative
classifier. All other cloud-classification sites must delegate here.

[M7 Local-First]  Unknown providers default to cloud (pessimistic) — never
inflate the sovereignty claim.
[M22 Provenance]  Classification is derived from config, auditable, and
immutable per-deploy (tied to config SHA).

AP: AP-PROVIDER-REGISTRY-v1.0.0
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """SSOT for provider capability metadata. Loaded once from providers.yaml.

    Replaces five divergent hardcoded classifiers that caused 73.6% of
    historical sovereignty rows to be misclassified (GAP-1).
    """

    # Pessimistic default: unknown providers are classified cloud to never
    # inflate the sovereignty claim (M7).
    _UNKNOWN_IS_CLOUD = True
    # Providers excluded from sovereignty stats entirely (tests, mocks).
    _SYNTHETIC = {"mock", "fallback"}

    def __init__(self, fabric_cfg: list[dict[str, Any]]):
        self._is_cloud: dict[str, bool] = {}
        for p in fabric_cfg:
            name = p.get("provider")
            if name:
                self._is_cloud[name] = bool(p.get("is_cloud", self._UNKNOWN_IS_CLOUD))

    @classmethod
    def from_config_path(cls, path: Optional[Path] = None) -> "ProviderRegistry":
        """Load from config/providers.yaml (or a custom path for tests)."""
        if path is None:
            path = (
                Path(__file__).resolve().parent.parent.parent
                / "config"
                / "providers.yaml"
            )
        if not path.exists():
            logger.warning("Provider config not found at %s. Using empty registry.", path)
            return cls([])
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        fabric_cfg = config.get("inference", {}).get("fallback_chain", [])
        return cls(fabric_cfg)

    @classmethod
    def from_fabric_config(cls, fabric_cfg: list[dict[str, Any]]) -> "ProviderRegistry":
        """Build from an already-loaded fabric config (avoids re-reading YAML)."""
        return cls(fabric_cfg)

    def is_cloud(self, name: str) -> bool:
        """Return True if provider is cloud-based (M7/M22 SSOT)."""
        if name not in self._is_cloud:
            # Warn once per unknown name to avoid log flooding.
            if not getattr(self, "_warned_names", None):
                self._warned_names = set()  # type: ignore[attr-defined]
            if name not in self._warned_names:  # type: ignore[attr-defined]
                logger.warning(
                    "M22: unknown provider %r classified CLOUD (pessimistic)", name
                )
                self._warned_names.add(name)  # type: ignore[attr-defined]
            return self._UNKNOWN_IS_CLOUD
        return self._is_cloud[name]

    def is_synthetic(self, name: str) -> bool:
        """Return True if provider is synthetic (excluded from sovereignty stats)."""
        return name in self._SYNTHETIC

    def classify(self, name: str) -> tuple[bool, bool]:
        """Return (is_cloud, is_synthetic) for a provider name."""
        return self.is_cloud(name), self.is_synthetic(name)

    def all_providers(self) -> dict[str, bool]:
        """Return copy of all provider classifications."""
        return dict(self._is_cloud)
