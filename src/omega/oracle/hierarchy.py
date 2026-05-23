"""Omega Sovereign Hierarchy — Rank and Recursion Management.

AP: AP-HIERARCHY-LOGIC-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: HIERARCHY]
"""

import yaml
from pathlib import Path
from typing import Dict, Optional

class SovereignHierarchy:
    """Manages entity ranks and recursion limits based on the Oversoul Hierarchy."""

    RANK_MAP = {
        "sophia": 0,
        "maat": 1,
        "isis": 2,
        "lilith": 2,
        # Pillar Keepers are Rank 3
    }

    def __init__(self, hierarchy_config: Optional[Path] = None):
        self.config_path = hierarchy_config or Path(__file__).resolve().parent.parent.parent.parent / "config" / "hierarchy.yaml"
        self._hierarchy = {}
        self._load()

    def _load(self):
        if not self.config_path.exists():
            return
        with open(self.config_path, "r") as f:
            self._hierarchy = yaml.safe_load(f)

    def get_rank(self, entity_name: str) -> int:
        """Get the numeric rank of an entity (0=Root, 3=Keeper)."""
        name = entity_name.lower()
        if name in self.RANK_MAP:
            return self.RANK_MAP[name]
        
        # Check if it's a pillar keeper
        # We could also check entities.yaml, but the hierarchy.yaml has governance.
        # Actually, any entity not in the RANK_MAP is likely a Keeper or below.
        return 3

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
