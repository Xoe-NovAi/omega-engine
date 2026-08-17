# AP: AP-PR-READINESS-v1.0.0
# AP: AP-WORLD-STATE-v1.0.0
# 🔱 World State Manager — VR Omegaverse State Engine
#
# Implements the 'First Breath' world-state activation.
# Maintains a sovereign representation of the VR Omegaverse.
#
# Heritage: inspired by BSP culling (id Software 1993) — REJECTED per vet-028
#   Instead of scanning the entire world-state, we partition data into
#   sectors (lumps). Queries are first culled by sector-id before
#     performing detailed lookups.


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class WorldLump:
    """A discrete unit of world-state data. [id-soft: doom-1993]"""
    lump_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorldState:
    """Sovereign World State Manager for the VR Omegaverse."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorldState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # Heritage: sector-based partitioning inspired by BSP (id Software 1993) — REJECTED per vet-028
        self._sectors: Dict[str, Dict[str, WorldLump]] = {}
        self._global_state: Dict[str, Any] = {}
        self._initialized = True
        logger.info("WorldState Manager initialized. VR Omegaverse Breath: READY.")

    async def load_lump(self, sector_id: str, lump: WorldLump):
        """Load a data lump into a specific sector. Heritage: Doom 1993 WAD lump system"""
        if sector_id not in self._sectors:
            self._sectors[sector_id] = {}
        self._sectors[sector_id][lump.lump_id] = lump
        logger.debug(f"Loaded lump {lump.lump_id} into sector {sector_id}")

    def set_global(self, key: str, value: Any):
        """Set a global world parameter."""
        self._global_state[key] = value

    def get_global(self, key: str, default: Any = None) -> Any:
        """Get a global world parameter."""
        return self._global_state.get(key, default)

    def lattice_query(self, sector_id: Optional[str], lump_id: Optional[str]) -> Optional[Any]:
        """
        Sector-culling query primitive. Heritage: inspired by Doom 1993 BSP sector culling (REJECTED per vet-028)
        
        Efficiently queries world-state by culling irrelevant sectors.
        If sector_id is provided, we skip all other sectors (O(1) culling).
        """
        # 1. Cull by sector
        if sector_id:
            sector = self._sectors.get(sector_id)
            if not sector:
                return None
            
            # 2. Cull by lump
            if lump_id:
                lump = sector.get(lump_id)
                return lump.data if lump else None
            
            # Return entire sector if no lump_id
            return {k: v.data for k, v in sector.items()}
        
        # Fallback: if no sector_id, we would have to scan all sectors (expensive)
        # In a strict sector-culling system, we might forbid this or return global
        return None

    def get_all_sectors(self) -> List[str]:
        """Return list of active world sectors."""
        return list(self._sectors.keys())

    def reset(self):
        """Reset world state for testing."""
        self._sectors.clear()
        self._global_state.clear()
        logger.debug("WorldState reset for testing")

# Singleton instance for engine-wide access
world_state = WorldState()
