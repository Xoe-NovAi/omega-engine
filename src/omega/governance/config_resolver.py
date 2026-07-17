# ⬡ OMEGA ⬡ GOVERNANCE ⬡ CONFIG_RESOLVER
# Single source of truth for project paths (D-281 Phase II).
#
# Constants are pure Path objects — NO I/O at module level (circular-import safe).
# Lazy readers (get_active_iwad) perform I/O only when called.
# Do NOT re-export from governance/__init__.py — import explicitly at call sites.

from pathlib import Path
from typing import Any

import yaml

# ─── Pure Path Constants (NO I/O at module level) ────────────────────────────
# Path: governance → omega → src → REPO ROOT (4 parents).
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
WADS_DIR = CONFIG_DIR / "wads"
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"


def get_active_iwad() -> str:
    """Read active_iwad from config/omega.yaml at call time (lazy).

    Nested key: omega.entity.active_iwad (default: ``_omega_default``).
    """
    omega_yaml = CONFIG_DIR / "omega.yaml"
    if not omega_yaml.exists():
        return "_omega_default"
    with open(omega_yaml, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}
    return (
        data.get("omega", {})
        .get("entity", {})
        .get("active_iwad", "_omega_default")
    )


def get_wad_path(wad_name: str) -> Path:
    """Resolve a WAD directory under WADS_DIR."""
    return WADS_DIR / wad_name


def get_entity_dir(entity_name: str) -> Path:
    """Resolve entity data directory under DATA_DIR/entities."""
    return DATA_DIR / "entities" / entity_name
