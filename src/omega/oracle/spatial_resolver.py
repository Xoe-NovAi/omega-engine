# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Mem Palace — Spatial-Semantic Geometry
# AP: AP-SPATIAL-v1.0.0
#
# Implements a Force-Directed Graph (Fruchterman-Reingold) to map 
# semantic entity relationships into 3D Euclidean space.
#
# This allows the engine to navigate memory not just by cosine 
# similarity, but by spatial proximity and topological structure.
#
# [id-soft: vet-046] BSP Culling — Spatial partitioning for efficiency
#   The spatial resolver provides the coordinates that allow the engine
#   to cull large regions of the semantic space during navigation.
#
# Pattern: Repulsion (k^2/d) + Attraction (d^2/k) + Cooling Schedule


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import math
import random
import logging
from typing import Dict, List, Tuple, Protocol, Optional
from dataclasses import dataclass

logger = logging.getLogger("omega.spatial_resolver")

@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def dist_to(self, other: 'Point3D') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

class ISpatialResolver(Protocol):
    """Protocol for spatial resolution of semantic entities."""
    def resolve_coordinates(self, entities: List[str], relationships: List[Tuple[str, str]]) -> Dict[str, Point3D]:
        ...

class ForceDirectedSpatialResolver:
    """Implements the Fruchterman-Reingold 3D layout algorithm.
    
    Treats entities as particles:
    - Repulsion: All nodes repel each other (like electrons).
    - Attraction: Connected nodes attract each other (like springs).
    - Cooling: Max displacement decreases over time to ensure convergence.
    """
    def __init__(
        self, 
        iterations: int = 100, 
        initial_temp: float = 100.0, 
        decay_factor: float = 0.95,
        volume: float = 1000.0
    ):
        self.iterations = iterations
        self.initial_temp = initial_temp
        self.decay_factor = decay_factor
        self.volume = volume

    def resolve_coordinates(self, entities: List[str], relationships: List[Tuple[str, str]]) -> Dict[str, Point3D]:
        """Compute 3D coordinates for a set of entities based on their relationships."""
        if not entities:
            return {}

        # 1. Initialize random positions
        pos: Dict[str, Point3D] = {
            e: Point3D(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10))
            for e in entities
        }
        
        # 2. Calculate optimal distance k
        # k = sqrt(Volume / N)
        k = math.sqrt(self.volume / len(entities))
        
        temp = self.initial_temp
        
        for i in range(self.iterations):
            # Displacement vectors
            disp: Dict[str, Point3D] = {e: Point3D(0, 0, 0) for e in entities}
            
            # --- Repulsion (All pairs) ---
            for e1 in entities:
                for e2 in entities:
                    if e1 == e2: continue
                    
                    p1, p2 = pos[e1], pos[e2]
                    d = p1.dist_to(p2)
                    if d == 0: d = 0.01 # Avoid div by zero
                    
                    # fr = k^2 / d
                    force = (k**2) / d
                    
                    # Direction vector
                    dx = (p1.x - p2.x) / d
                    dy = (p1.y - p2.y) / d
                    dz = (p1.z - p2.z) / d
                    
                    disp[e1].x += dx * force
                    disp[e1].y += dy * force
                    disp[e1].z += dz * force
            
            # --- Attraction (Connected pairs) ---
            for e1, e2 in relationships:
                if e1 not in pos or e2 not in pos: continue
                
                p1, p2 = pos[e1], pos[e2]
                d = p1.dist_to(p2)
                if d == 0: continue
                
                # fa = d^2 / k
                force = (d**2) / k
                
                # Direction vector
                dx = (p2.x - p1.x) / d
                dy = (p2.y - p1.y) / d
                dz = (p2.z - p1.z) / d
                
                disp[e1].x += dx * force
                disp[e1].y += dy * force
                disp[e1].z += dz * force
                
                disp[e2].x -= dx * force
                disp[e2].y -= dy * force
                disp[e2].z -= dz * force
            
            # --- Apply Displacement with Cooling ---
            for e in entities:
                d_vec = disp[e]
                mag = math.sqrt(d_vec.x**2 + d_vec.y**2 + d_vec.z**2)
                if mag == 0: continue
                
                # Displacement_t = min(Force, Temperature_t)
                limited_mag = min(mag, temp)
                
                pos[e].x += (d_vec.x / mag) * limited_mag
                pos[e].y += (d_vec.y / mag) * limited_mag
                pos[e].z += (d_vec.z / mag) * limited_mag
            
            # Cool down
            temp *= self.decay_factor
            
        return pos

# ── Singleton Access ──────────────────────────────────────────────────────

_spatial_resolver: Optional[ISpatialResolver] = None

def get_spatial_resolver() -> ISpatialResolver:
    global _spatial_resolver
    if _spatial_resolver is None:
        _spatial_resolver = ForceDirectedSpatialResolver()
    return _spatial_resolver
