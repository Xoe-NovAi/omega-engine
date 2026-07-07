# AP: AP-ORACLE-RESTORE-v2.3.0
"""Omega Sovereign Hierarchy — Rank and Recursion Management.

AP: AP-HIERARCHY-LOGIC-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: HIERARCHY]

[id-soft: quake3-1999] Hard-Boundary Struct — hierarchy tier separation
  Q3A separates entityState_t (engine) from entityShared_t (game) with
  a "DO NOT MODIFY" boundary. HierarchyManager enforces rank-based
  boundaries: lower-rank entities cannot modify higher-rank state.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
import os
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import yaml
from pathlib import Path
from typing import Dict, Optional
import anyio

logger = logging.getLogger(__name__)

class SovereignHierarchy:
    """Manages entity ranks and recursion limits based on the Oversoul Hierarchy."""

    def __init__(self, hierarchy_config: Optional[Path] = None):
        if hierarchy_config is None:
            try:
                omega_config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
                with open(omega_config_path, "r") as f:
                    omega_cfg = yaml.safe_load(f)
                active_iwad = omega_cfg.get("omega", {}).get("entity", {}).get("active_iwad", "_omega_default")  # [remediated: M2-LEAK] — bypasses WadLoader; should use wad_loader.wads_dir
                
                # Use OMEGA_WADS_DIR env var if present, otherwise default to config/wads
                wads_base = Path(os.environ.get("OMEGA_WADS_DIR", str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads")))  # [remediated: M2-LEAK] — Path traversal bypasses WadLoader; inject WadLoader
                self.config_path = wads_base / active_iwad / "hierarchy.yaml"  # [remediated: M2-LEAK] — direct path construction, not wad_loader.resolve_wad_path()
            except OmegaError:
                logger.warning("OmegaError resolving active IWAD for hierarchy. Falling back to default.")
                wads_base = Path(os.environ.get("OMEGA_WADS_DIR", str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads")))  # [remediated: M2-LEAK] — fallback path also bypasses WadLoader
                self.config_path = wads_base / cvar_get("config.entity.active_iwad", "_omega_default") / "hierarchy.yaml"  # [remediated: M2-LEAK] — duplicate path construction bypass

        else:
            self.config_path = hierarchy_config
        self._hierarchy = {}

    async def load(self, config_path: Optional[Path] = None):
        """Asynchronously load the hierarchy configuration.
        
        Args:
            config_path: Optional path to a specific hierarchy file (e.g., from a WAD).
                          If None, uses the default config_path.
        """
        path = config_path or self.config_path
        if not path.exists():
            logger.warning(f"Hierarchy config not found at {path}")
            return
        async with await anyio.open_file(str(path), "r") as f:
            content = await f.read()
            self._hierarchy = yaml.safe_load(content)
            logger.info(f"Loaded hierarchy from {path}")


    def get_rank(self, entity_name: str) -> int:
        """Get the numeric rank of an entity (0=Root, 3=Keeper) by traversing the hierarchy.yaml.
        
        Ranks:
            0: The Field (e.g., Sophia)
            1: Unification (e.g., Root Entity)
            2: Oversouls / Special Keepers
            3: Pillar Keepers
        """
        name = entity_name.lower()
        hierarchy_data = self._hierarchy.get("hierarchy", {})
        if not hierarchy_data:
            return 3 # Default to Keeper if config is missing

        # 1. Identify the "Field" (Root of all)
        # We look for the entity that 'contains' the others or is explicitly the root
        field_entity = next((k for k, v in hierarchy_data.items() if isinstance(v, dict) and "contains" in v), None)
        if name == field_entity:
            return 0

        # 2. Resolve entity name to hierarchy key (data-driven, no hardcoded names)
        #    Try common suffixes: _founder, _cto, _ciso, _oversoul, _unification
        lookup_name = name
        if lookup_name not in hierarchy_data:
            for suffix in ("_founder", "_cto", "_ciso", "_oversoul", "_unification"):
                if f"{name}{suffix}" in hierarchy_data:
                    lookup_name = f"{name}{suffix}"
                    break
            else:
                # Check if it's a keeper
                keepers = hierarchy_data.get("keepers", {})
                if name in keepers or any(k.get("keeper") == name for k in keepers.values() if isinstance(k, dict)):
                    return 3
                return 3 # Default fallback

        # 3. Traverse reports_to chain to determine rank
        current = lookup_name
        depth = 0
        visited = set()
        
        while current in hierarchy_data:
            if current in visited:
                break # Cycle detected
            visited.add(current)
            
            node = hierarchy_data[current]
            if not isinstance(node, dict):
                break
                
            parent = node.get("reports_to")
            if not parent:
                # We hit the top of the reports_to chain (e.g., Root Entity)
                # If the field_entity exists, the top of the chain is Rank 1
                return depth + (1 if field_entity else 0)
            
            current = parent
            depth += 1
            
        return 2 if lookup_name in hierarchy_data else 3

    def check_recursion(self, entity_name: str, current_depth: int) -> Dict[str, any]:
        """Check if an entity is allowed to spawn a subagent at the given depth.
        
        Rules:
            - Max Depth is 3.
            - Sophia (Rank 0) has full depth.
            - Ma'at (Rank 1) has depth 2.
            - Oversouls (Rank 2) have depth 1.
            - Keepers (Rank 3) have depth 0 (no subagents).
        """
        rank = self.get_rank(entity_name)
        max_allowed_depth = 3 - rank
        
        allowed = current_depth < max_allowed_depth
        
        return {
            "entity": entity_name,
            "rank": rank,
            "current_depth": current_depth,
            "max_allowed_depth": max_allowed_depth,
            "allowed": allowed,
            "reason": "OK" if allowed else f"Entity '{entity_name}' (Rank {rank}) reached recursion limit (Max Depth: {max_allowed_depth})"
        }
