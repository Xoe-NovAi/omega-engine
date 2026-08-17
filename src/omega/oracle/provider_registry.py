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
        # model name -> provider name (populated from providers.yaml
        # `providers:` map supported_models, Decision 4).
        self._model_to_provider: dict[str, str] = {}

    @classmethod
    def from_config_path(cls, path: Optional[Path] = None) -> "ProviderRegistry":
        """Load from config/providers.yaml (or a custom path for tests)."""
        if path is None:
            path = (
                Path(__file__).resolve().parent.parent.parent.parent / "config" / "providers.yaml"
            )
        if not path.exists():
            logger.warning("Provider config not found at %s. Using empty registry.", path)
            return cls([])
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        fabric_cfg = config.get("inference", {}).get("fallback_chain", [])
        registry = cls(fabric_cfg)
        registry._load_model_map(config.get("inference", {}).get("providers", {}))  # noqa: SLF001
        return registry

    @classmethod
    def from_fabric_config(cls, fabric_cfg: list[dict[str, Any]]) -> "ProviderRegistry":
        """Build from an already-loaded fabric config (avoids re-reading YAML)."""
        return cls(fabric_cfg)

    @staticmethod
    def _normalize_model(model_name: str) -> str:
        """Normalize a model name for matching across providers.

        Collapses suffix/prefix inconsistencies between config and runtime:
        ``google/gemma-4-31b-it:free`` -> ``gemma-4-31b-it`` and
        ``qwen3-1.7b-local`` -> ``qwen3-1.7b``.
        """
        name = model_name.strip().lower()
        if "/" in name:
            name = name.rsplit("/", 1)[1]
        if ":" in name:
            name = name.split(":", 1)[0]
        for suffix in ("-local", "-free", "-thinking"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break
        return name

    def _load_model_map(self, providers_cfg: dict[str, dict[str, Any]]) -> None:
        """Build model -> provider map from the runtime `providers:` map.

        When a model is served by multiple providers the lowest priority
        number wins (matches the fallback-chain ordering semantics).
        """
        self._model_to_provider = {}
        entries: list[tuple[int, str, str]] = []
        for pname, pcfg in providers_cfg.items():
            if not isinstance(pcfg, dict):
                continue
            priority = int(pcfg.get("priority", 999))
            for model in pcfg.get("supported_models", []) or []:
                entries.append((priority, pname, self._normalize_model(model)))
        for _priority, pname, norm in sorted(entries, key=lambda e: (e[0], e[1])):
            self._model_to_provider.setdefault(norm, pname)

    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Resolve which provider serves this model (Decision 4).

        Checks, in order:
        1. Exact provider name (backwards compatible with call sites that
           pass a provider key directly).
        2. Normalized match against ``providers:` map ``supported_models``.

        Returns ``None`` when the model cannot be mapped — callers must then
        apply the pessimistic cloud default (M7).
        """
        if model_name in self._is_cloud:
            return model_name
        return self._model_to_provider.get(self._normalize_model(model_name))

    def is_cloud(self, name: str) -> bool:
        """Return True if provider is cloud-based (M7/M22 SSOT).

        [M7 Local-First] Unknown providers default to CLOUD (pessimistic) so
        the sovereignty claim can never be inflated by unrecorded/modified
        provider names. M7 text: "Cloud is a safety net, not a crutch" — an
        unknown backend is treated as unapproved/external until proven local.
        """
        if name not in self._is_cloud:
            # Warn once per unknown name to avoid log flooding.
            if not getattr(self, "_warned_names", None):
                self._warned_names = set()  # type: ignore[attr-defined]
            if name not in self._warned_names:  # type: ignore[attr-defined]
                logger.warning("M22: unknown provider %r classified CLOUD (pessimistic)", name)
                self._warned_names.add(name)  # type: ignore[attr-defined]
            return self._UNKNOWN_IS_CLOUD
        return self._is_cloud[name]

    def is_synthetic(self, name: str) -> bool:
        """Return True if provider is synthetic (excluded from sovereignty stats)."""
        return name in self._SYNTHETIC

    def synthetic_providers(self) -> set[str]:
        """Return the set of synthetic provider names (test/probe backends)."""
        return set(self._SYNTHETIC)

    def classify(self, name: str) -> tuple[bool, bool]:
        """Return (is_cloud, is_synthetic) for a provider name."""
        return self.is_cloud(name), self.is_synthetic(name)

    def all_providers(self) -> dict[str, bool]:
        """Return copy of all provider classifications."""
        return dict(self._is_cloud)


# ── Process-wide Singleton ──────────────────────────────────────────
# [GAP-1] Single source for cloud/local classification — replaces 6
# independent from_config_path() call sites across model_gateway.py,
# observability/__init__.py, otel_exporter.py, remote_provider.py,
# ingestion/pipeline.py, and metrics_db.py.
_registry: Optional["ProviderRegistry"] = None


def get_provider_registry() -> "ProviderRegistry":
    """Process-wide singleton. [GAP-1] Single source for cloud/local
    classification — replaces 6 independent from_config_path() call sites.
    """
    global _registry
    if _registry is None:
        _registry = ProviderRegistry.from_config_path()
    return _registry


def reset_provider_registry() -> None:
    """Reset for tests. Mirrors reset_observability()/reset_memory_store()."""
    global _registry
    _registry = None
