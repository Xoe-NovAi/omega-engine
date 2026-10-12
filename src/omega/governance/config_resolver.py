# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ GOVERNANCE ⬡ CONFIG_RESOLVER
# Single source of truth for project paths (D-281 Phase II).
#
# Robust multi-context resolution:
#   1. OMEGA_CONFIG_DIR environment variable
#   2. Source / editable install tree (via __file__.parents[3] / config)
#   3. Current working directory (Path.cwd() / config)
#   4. User configuration directory (~/.config/omega)
#   5. Package data (wheel install) — via importlib.resources.files("omega.config_data")
#
# Circular-import safe: pure Path objects, lazy readers perform I/O only when called.

import os
import sysconfig
from pathlib import Path
from typing import Any, Optional, Union

import yaml

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources  # py3.8 fallback


# ─── Multi-Context Path Resolution ──────────────────────────────────────────

class _ConfigDir:
    """Config directory resolver with fallback chain: env → dev → cwd → user → package."""

    def __init__(self):
        self._resolved: Optional[Path] = None
        self._pkg_config_traversable = None

    def resolve(self) -> Path:
        """Resolve config directory with fallback chain."""
        if self._resolved is not None:
            return self._resolved

        # 1. Environment variable override (highest precedence)
        env_dir = os.environ.get("OMEGA_CONFIG_DIR")
        if env_dir:
            p = Path(env_dir).expanduser().resolve()
            if p.is_dir():
                self._resolved = p
                return self._resolved

        # 2. Source / editable checkout (4 parents from this file: governance -> omega -> src -> root)
        dev_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_config = dev_root / "config"
        if dev_config.is_dir() and (dev_config / "omega.yaml").is_file():
            self._resolved = dev_config
            return self._resolved

        # 3. Current working directory (common for CLI invoked from cloned repository)
        cwd_config = Path.cwd() / "config"
        if cwd_config.is_dir() and (cwd_config / "omega.yaml").is_file():
            self._resolved = cwd_config
            return self._resolved

        # 4. User configuration directory (~/.config/omega)
        user_config = Path.home() / ".config" / "omega"
        if user_config.is_dir() and (user_config / "omega.yaml").is_file():
            self._resolved = user_config
            return self._resolved

        # 5. Package data (wheel install) — via importlib.resources.files("omega.config_data")
        try:
            pkg_config = pkg_resources.files("omega.config_data")
            # Verify package config exists by checking for a known file
            if (pkg_config / "embedding_strategy.yaml").is_file():
                # Use as_file() context manager to get a real Path
                self._pkg_config_cm = pkg_resources.as_file(pkg_config)
                self._resolved = self._pkg_config_cm.__enter__()
                return self._resolved
        except (ModuleNotFoundError, AttributeError, FileNotFoundError):
            pass

        # 6. Fallback: if cwd has embedding_strategy.yaml
        cwd_config = Path.cwd() / "config"
        if cwd_config.is_dir() and (cwd_config / "embedding_strategy.yaml").is_file():
            self._resolved = cwd_config
            return self._resolved

        # Default to dev_config (will fail with clear message if accessed when absent)
        dev_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_config = dev_root / "config"
        self._resolved = dev_config
        return self._resolved

    def cleanup(self):
        """Clean up package data context manager if used."""
        if hasattr(self, '_pkg_config_cm') and self._pkg_config_cm:
            try:
                self._pkg_config_cm.__exit__(None, None, None)
            except Exception:
                pass


# Global config directory instance
_config_dir = _ConfigDir()


def _get_config_dir() -> Path:
    """Get resolved config directory (lazy, cached)."""
    return _config_dir.resolve()


# Public constants — resolved at call time via _get_config_dir()
CONFIG_DIR = _get_config_dir()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WADS_DIR = CONFIG_DIR / "wads"
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"


def _open_config_file(filename: str):
    """Open a config file from the resolved config directory."""
    return open(_get_config_dir() / filename, encoding="utf-8")


def get_active_iwad() -> str:
    """Read active_iwad from config/omega.yaml at call time (lazy).

    Nested key: omega.entity.active_iwad (default: ``_omega_default``).
    """
    try:
        with _open_config_file("omega.yaml") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return "_omega_default"
    return data.get("omega", {}).get("entity", {}).get("active_iwad", "_omega_default")


def get_wad_path(wad_name: str) -> Path:
    """Resolve a WAD directory under WADS_DIR."""
    return _get_config_dir() / "wads" / wad_name


def get_entity_dir(entity_name: str) -> Path:
    """Resolve entity data directory under DATA_DIR/entities."""
    return Path(__file__).resolve().parent.parent.parent.parent / "data" / "entities" / entity_name
