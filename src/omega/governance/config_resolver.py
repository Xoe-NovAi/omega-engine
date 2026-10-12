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
#
# Circular-import safe: pure Path objects, lazy readers perform I/O only when called.

import os
from pathlib import Path
from typing import Any, Optional

import yaml

# ─── Multi-Context Path Resolution ──────────────────────────────────────────

def _resolve_config_dir() -> Path:
    """Resolve config directory across editable, dev, wheel, and standalone contexts."""
    # 1. Environment variable override (highest precedence)
    env_dir = os.environ.get("OMEGA_CONFIG_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
        if p.is_dir():
            return p

    # 2. Source / editable checkout (4 parents from this file: governance -> omega -> src -> root)
    dev_root = Path(__file__).resolve().parent.parent.parent.parent
    dev_config = dev_root / "config"
    if dev_config.is_dir() and (dev_config / "omega.yaml").is_file():
        return dev_config

    # 3. Current working directory (common for CLI invoked from cloned repository)
    cwd_config = Path.cwd() / "config"
    if cwd_config.is_dir() and (cwd_config / "omega.yaml").is_file():
        return cwd_config

    # 4. User configuration directory (~/.config/omega)
    user_config = Path.home() / ".config" / "omega"
    if user_config.is_dir() and (user_config / "omega.yaml").is_file():
        return user_config

    # 5. Fallback: if cwd has embedding_strategy.yaml
    if cwd_config.is_dir() and (cwd_config / "embedding_strategy.yaml").is_file():
        return cwd_config

    # Default to dev_config (will fail with clear message if accessed when absent)
    return dev_config


def _resolve_project_root(config_dir: Path) -> Path:
    """Resolve root directory from resolved config directory."""
    if config_dir.name == "config" and config_dir.parent.is_dir():
        return config_dir.parent
    return Path.cwd()


# Canonical paths resolved once at module load
CONFIG_DIR: Path = _resolve_config_dir()
PROJECT_ROOT: Path = _resolve_project_root(CONFIG_DIR)
WADS_DIR: Path = CONFIG_DIR / "wads"
DATA_DIR: Path = (
    PROJECT_ROOT / "data"
    if (PROJECT_ROOT / "data").is_dir()
    else (Path.cwd() / "data" if (Path.cwd() / "data").is_dir() else PROJECT_ROOT / "data")
)
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"
AGENTS_MD: Path = PROJECT_ROOT / "AGENTS.md"


def get_active_iwad() -> str:
    """Read active_iwad from config/omega.yaml at call time (lazy).

    Nested key: omega.entity.active_iwad (default: ``_omega_default``).
    """
    omega_yaml = CONFIG_DIR / "omega.yaml"
    if not omega_yaml.exists():
        return "_omega_default"
    with open(omega_yaml, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}
    return data.get("omega", {}).get("entity", {}).get("active_iwad", "_omega_default")


def get_wad_path(wad_name: str) -> Path:
    """Resolve a WAD directory under WADS_DIR."""
    return WADS_DIR / wad_name


def get_entity_dir(entity_name: str) -> Path:
    """Resolve entity data directory under DATA_DIR/entities."""
    return DATA_DIR / "entities" / entity_name
