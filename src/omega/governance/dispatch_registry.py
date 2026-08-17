# ⬡ OMEGA ⬡ GOVERNANCE ⬡ DISPATCH_REGISTRY
# Single source for dispatch.yaml with mtime-aware cache.
# Covers: oracle.py, subagent_dispatcher.py, ics.py, fleet_status_tui.py, mandate_auditor.py
# M2 Firewall: No WAD entity names in engine core.

import threading
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from omega.governance.config_resolver import WADS_DIR


_cache = {"mtime": 0.0, "data": None}
_lock = threading.Lock()


def load_dispatch_yaml(iwad: Optional[str] = None, root: Optional[Path] = None) -> Dict[str, Any]:
    """Load full dispatch.yaml dict with mtime-aware cache.

    Args:
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.
        root: Optional root path override for testing. If None, uses global WADS_DIR.

    Returns:
        Full parsed YAML dict (contains 'entities' key).

    Raises:
        FileNotFoundError: If dispatch.yaml not found.
        ValueError: If YAML is malformed.
    """
    if iwad is None:
        from omega.governance.config_resolver import get_active_iwad

        iwad = get_active_iwad()

    base = root or WADS_DIR
    path = base / iwad / "entities" / "dispatch.yaml"

    if not path.exists():
        raise FileNotFoundError(f"No dispatch config found at {path}")

    mtime = path.stat().st_mtime

    with _lock:
        if _cache["mtime"] != mtime:
            with open(path, encoding="utf-8") as f:
                _cache["data"] = yaml.safe_load(f) or {}
            _cache["mtime"] = mtime

    return _cache["data"]


def get_dispatch_entities(
    iwad: Optional[str] = None, root: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Get entities list from dispatch.yaml (top-level 'entities' key).

    Args:
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.
        root: Optional root path override for testing. If None, uses global WADS_DIR.

    Returns:
        List of entity definition dicts.
    """
    data = load_dispatch_yaml(iwad, root)
    return data.get("entities", [])


def get_entity_by_role(
    role: str, iwad: Optional[str] = None, root: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Find entity by role (e.g., 'kali', 'maat', 'node_P3').

    Args:
        role: Role constant to search for.
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.
        root: Optional root path override for testing. If None, uses global WADS_DIR.

    Returns:
        Entity dict if found, None otherwise.
    """
    entities = get_dispatch_entities(iwad, root)
    for e in entities:
        if e.get("role") == role:
            return e
    return None


def invalidate_cache() -> None:
    """Force cache invalidation (for tests)."""
    with _lock:
        _cache["mtime"] = 0.0
        _cache["data"] = None


__all__ = [
    "load_dispatch_yaml",
    "get_dispatch_entities",
    "get_entity_by_role",
    "invalidate_cache",
]
