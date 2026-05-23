"""Omega Sovereign Hierarchy — Rank and Recursion Management.

AP: AP-HIERARCHY-LOGIC-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: HIERARCHY]
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Optional
import anyio

logger = logging.getLogger(__name__)

class SovereignHierarchy:
    """Manages entity ranks and recursion limits based on the Oversoul Hierarchy."""

    def __init__(self, hierarchy_config: Optional[Path] = None):
        self.config_path = hierarchy_config or Path(__file__).resolve().parent.parent.parent.parent / "config" / "hierarchy.yaml"
        self._hierarchy = {}


    async def load(self):
        """Asynchronously load the hierarchy configuration."""
        if not self.config_path.exists():
            logger.warning(f"Hierarchy config not found at {self.config_path}")
            return
        async with await anyio.open_file(self.config_path, "r") as f:
            content = await f.read()
            self._hierarchy = yaml.safe_load(content)
            logger.info(f"Loaded hierarchy from {self.config_path}")


    def get_rank(self, entity_name: str) -> int:
        """Get the numeric rank of an entity (0=Root, 3=Keeper) by traversing the hierarchy.yaml.
        
        Ranks:
            0: Sophia (The Field)
            1: Kali (Unification)
            2: Oversouls / Special Keepers (Synthesis, Sovereignty, Abyss)
            3: Pillar Keepers
        """
        name = entity_name.lower()
        
        # 1. Root check
        if name == "sophia":
            return 0
            
        hierarchy_data = self._hierarchy.get("hierarchy", {})
        if not hierarchy_data:
            return 3 # Default to Keeper if config is missing
            
        # 2. Resolve entity name to hierarchy key (e.g., "maat" -> "maat_oversoul")
        lookup_name = name
        if lookup_name not in hierarchy_data:
            # Try common oversoul suffix
            if f"{name}_oversoul" in hierarchy_data:
                lookup_name = f"{name}_oversoul"
            # Try unification mapping
            elif name == "kali" and "kali_unification" in hierarchy_data:
                lookup_name = "kali_unification"
            else:
                # Not found in hierarchy, check if it's a keeper
                keepers = hierarchy_data.get("keepers", {})
                if name in keepers or any(k.get("keeper") == name for k in keepers.values() if isinstance(k, dict)):
                    return 3
                return 3 # Default fallback
        
        print(f"DEBUG: Resolved {name} to {lookup_name}")
                
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
                print(f"DEBUG: Hit top of chain at {current} with depth {depth}")
                return depth + 1 if current == "kali_unification" else depth + 1
            
            current = parent
            depth += 1
            
        print(f"DEBUG: Loop ended for {name}, depth {depth}, current {current}")
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
