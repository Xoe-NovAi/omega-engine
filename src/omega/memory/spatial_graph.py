"""Spatial Knowledge Graph for VR Navigation and Knowledge Traversal.
AP: AP-SPATIAL-GRAPH-v1.0.0

Implements spatial proximity graph for VR navigation:
- Build spatial graph from R-tree coordinates
- A* navigation from start to semantic target
- BSP sector streaming for Godot
- Force-directed layout for entities without explicit coordinates

[id-soft: doom-1993] BSP Culling — Spatial partitioning for efficiency
[id-soft: quake-1996] PVS (Potentially Visible Set) — Sector-based visibility
"""

import json
import math
import logging
import random
import struct
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
import heapq

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None

import anyio

from .sqlite_vec_adapter_optimized import SQLiteVecAdapterOptimized

logger = logging.getLogger(__name__)


@dataclass
class SpatialNode:
    """Node in the spatial knowledge graph."""
    rowid: int
    uuid: str
    entity_name: str
    content: str
    x: float
    y: float
    z: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_vector: Optional[List[float]] = None


@dataclass
class SpatialEdge:
    """Edge in the spatial knowledge graph."""
    source: int
    target: int
    spatial_distance: float
    semantic_similarity: float = 0.0
    weight: float = 0.0  # Combined weight for A*


@dataclass
class SectorBounds:
    """BSP sector bounding box for Godot streaming."""
    sector_id: str
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    neighbor_sectors: List[str] = field(default_factory=list)
    center: Tuple[float, float, float] = field(default_factory=lambda: (0.0, 0.0, 0.0))
    radius: float = 0.0


class SpatialKnowledgeGraph:
    """Spatial knowledge graph for VR navigation and knowledge traversal.

    Builds a proximity graph from R-tree coordinates where:
    - Nodes = memories with spatial coordinates
    - Edges = spatial proximity + semantic similarity
    - Supports A* navigation, sector streaming, neighbor queries
    """

    def __init__(
        self,
        adapter: SQLiteVecAdapterOptimized,
        k_neighbors: int = 6,
        spatial_weight: float = 0.5,
        semantic_weight: float = 0.5,
        sector_size: float = 100.0,
    ):
        self.adapter = adapter
        self.k_neighbors = k_neighbors
        self.spatial_weight = spatial_weight
        self.semantic_weight = semantic_weight
        self.sector_size = sector_size

        self._graph: Optional["nx.Graph"] = None
        self._nodes: Dict[int, SpatialNode] = {}
        self._sectors: Dict[str, SectorBounds] = {}
        self._entity_sectors: Dict[str, Set[str]] = defaultdict(set)
        self._built = False

    async def build_spatial_graph(
        self,
        entity_name: str,
        k_neighbors: Optional[int] = None,
        force_rebuild: bool = False,
    ) -> "nx.Graph":
        """Build spatial proximity graph for an entity's memories.

        1. Get all memories with spatial coords from R-tree
        2. Connect each node to k nearest spatial neighbors
        3. Edge weight = spatial distance + semantic similarity
        """
        if self._built and not force_rebuild and self._graph is not None:
            return self._graph

        if not HAS_NETWORKX:
            raise RuntimeError("networkx required for spatial graph. Install: pip install networkx")

        k = k_neighbors or self.k_neighbors

        # 1. Get all memories with spatial coordinates for this entity
        nodes = await self._fetch_spatial_nodes(entity_name)
        if not nodes:
            logger.warning("No spatial nodes found for entity: %s", entity_name)
            self._graph = nx.Graph()
            self._built = True
            return self._graph

        # Store nodes
        self._nodes = {node.rowid: node for node in nodes}

        # 2. Build graph with k-nearest neighbors
        graph = nx.Graph()

        # Add nodes
        for node in nodes:
            graph.add_node(
                node.rowid,
                uuid=node.uuid,
                entity_name=node.entity_name,
                content=node.content[:200],  # Truncate for memory
                pos=(node.x, node.y, node.z),
                metadata=node.metadata,
            )

        # 3. Connect each node to k nearest spatial neighbors
        # Use spatial index for efficient neighbor search
        for node in nodes:
            neighbors = await self._get_spatial_neighbors(node.rowid, k)
            for neighbor_rowid, spatial_dist in neighbors:
                if neighbor_rowid not in self._nodes:
                    continue

                neighbor = self._nodes[neighbor_rowid]

                # Compute semantic similarity if both have vectors
                semantic_sim = 0.0
                if node.semantic_vector and neighbor.semantic_vector:
                    semantic_sim = self._cosine_similarity(node.semantic_vector, neighbor.semantic_vector)

                # Combined weight: lower = better for A*
                # spatial_weight * normalized_distance + semantic_weight * (1 - similarity)
                max_spatial_dist = self.sector_size * 2  # Normalization factor
                norm_spatial = min(spatial_dist / max_spatial_dist, 1.0)
                weight = (
                    self.spatial_weight * norm_spatial +
                    self.semantic_weight * (1.0 - semantic_sim)
                )

                edge = SpatialEdge(
                    source=node.rowid,
                    target=neighbor_rowid,
                    spatial_distance=spatial_dist,
                    semantic_similarity=semantic_sim,
                    weight=weight,
                )

                graph.add_edge(
                    node.rowid,
                    neighbor_rowid,
                    weight=weight,
                    spatial_distance=spatial_dist,
                    semantic_similarity=semantic_sim,
                )

        # 4. Build BSP sectors
        await self._build_sectors(nodes)

        self._graph = graph
        self._built = True

        logger.info(
            "Built spatial graph for %s: %d nodes, %d edges, %d sectors",
            entity_name, graph.number_of_nodes(), graph.number_of_edges(), len(self._sectors)
        )

        return graph

    async def _fetch_spatial_nodes(self, entity_name: str) -> List[SpatialNode]:
        """Fetch all memories with spatial coordinates for an entity."""
        def _sync_fetch():
            conn = self.adapter._get_read_conn()
            cursor = conn.execute("""
                SELECT s.id, d.uuid, d.entity_name, d.content, d.metadata_json,
                       s.minX, s.minY, s.minZ
                FROM omega_memory_spatial s
                JOIN omega_memory_data d ON s.id = d.id
                WHERE d.entity_name = ?
            """, (entity_name,))

            nodes = []
            for row in cursor.fetchall():
                rowid, uuid, ent_name, content, metadata_json, x, y, z = row
                metadata = {}
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        pass

                # Try to get semantic vector from primary collection
                semantic_vector = None
                try:
                    vec_cursor = conn.execute(
                        "SELECT embedding FROM omega_vec_gemma_768 WHERE rowid = ?",
                        (rowid,)
                    )
                    vec_row = vec_cursor.fetchone()
                    if vec_row and vec_row[0]:
                        import struct
                        semantic_vector = list(struct.unpack(f"{768}f", vec_row[0]))
                except Exception:
                    pass

                nodes.append(SpatialNode(
                    rowid=rowid,
                    uuid=uuid,
                    entity_name=ent_name,
                    content=content or "",
                    x=x, y=y, z=z,
                    metadata=metadata,
                    semantic_vector=semantic_vector,
                ))
            return nodes

        import json
        return await anyio.to_thread.run_sync(_sync_fetch)

    async def _get_spatial_neighbors(self, rowid: int, k: int) -> List[Tuple[int, float]]:
        """Get k nearest spatial neighbors using R-tree."""
        def _sync_neighbors():
            conn = self.adapter._get_read_conn()
            # Get the node's coordinates
            cursor = conn.execute(
                "SELECT minX, minY, minZ FROM omega_memory_spatial WHERE id = ?",
                (rowid,)
            )
            row = cursor.fetchone()
            if not row:
                return []
            x, y, z = row[0], row[1], row[2]

            # R-tree KNN query using bounding box expansion
            # Start with small radius, expand until we have k neighbors
            radius = 10.0
            max_radius = self.sector_size * 4
            neighbors = []

            while radius <= max_radius and len(neighbors) < k:
                min_x, max_x = x - radius, x + radius
                min_y, max_y = y - radius, y + radius
                min_z, max_z = z - radius, z + radius

                cursor = conn.execute("""
                    SELECT s.id, s.minX, s.minY, s.minZ
                    FROM omega_memory_spatial s
                    WHERE s.id != ?
                      AND s.minX <= ? AND s.maxX >= ?
                      AND s.minY <= ? AND s.maxY >= ?
                      AND s.minZ <= ? AND s.maxZ >= ?
                    LIMIT ?
                """, (rowid, max_x, min_x, max_y, min_y, max_z, min_z, k * 2))

                candidates = []
                for r in cursor.fetchall():
                    nid, nx, ny, nz = r
                    dist = math.sqrt((nx - x)**2 + (ny - y)**2 + (nz - z)**2)
                    candidates.append((nid, dist))

                # Sort by distance and take new ones
                candidates.sort(key=lambda x: x[1])
                for nid, dist in candidates:
                    if nid not in [n[0] for n in neighbors]:
                        neighbors.append((nid, dist))
                        if len(neighbors) >= k:
                            break

                radius *= 2.0

            return neighbors[:k]

        return await anyio.to_thread.run_sync(_sync_neighbors)

    async def _build_sectors(self, nodes: List[SpatialNode]) -> None:
        """Build BSP sectors for Godot streaming."""
        if not nodes:
            return

        # Compute world bounds
        min_x = min(n.x for n in nodes)
        max_x = max(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        max_y = max(n.y for n in nodes)
        min_z = min(n.z for n in nodes)
        max_z = max(n.z for n in nodes)

        # Add padding
        padding = self.sector_size * 0.5
        min_x -= padding; max_x += padding
        min_y -= padding; max_y += padding
        min_z -= padding; max_z += padding

        # Create grid of sectors
        nx_cells = max(1, int(math.ceil((max_x - min_x) / self.sector_size)))
        ny_cells = max(1, int(math.ceil((max_y - min_y) / self.sector_size)))
        nz_cells = max(1, int(math.ceil((max_z - min_z) / self.sector_size)))

        # Assign nodes to sectors
        sector_nodes: Dict[str, List[SpatialNode]] = defaultdict(list)

        for node in nodes:
            sx = int(math.floor((node.x - min_x) / self.sector_size))
            sy = int(math.floor((node.y - min_y) / self.sector_size))
            sz = int(math.floor((node.z - min_z) / self.sector_size))
            sx = max(0, min(sx, nx_cells - 1))
            sy = max(0, min(sy, ny_cells - 1))
            sz = max(0, min(sz, nz_cells - 1))

            sector_id = f"sector_{sx}_{sy}_{sz}"
            sector_nodes[sector_id].append(node)
            self._entity_sectors[node.entity_name].add(sector_id)

        # Create sector bounds
        for sector_id, sector_node_list in sector_nodes.items():
            parts = sector_id.split("_")
            sx, sy, sz = int(parts[1]), int(parts[2]), int(parts[3])

            sec_min_x = min_x + sx * self.sector_size
            sec_max_x = min_x + (sx + 1) * self.sector_size
            sec_min_y = min_y + sy * self.sector_size
            sec_max_y = min_y + (sy + 1) * self.sector_size
            sec_min_z = min_z + sz * self.sector_size
            sec_max_z = min_z + (sz + 1) * self.sector_size

            center_x = (sec_min_x + sec_max_x) / 2
            center_y = (sec_min_y + sec_max_y) / 2
            center_z = (sec_min_z + sec_max_z) / 2
            radius = math.sqrt(
                (sec_max_x - sec_min_x)**2 +
                (sec_max_y - sec_min_y)**2 +
                (sec_max_z - sec_min_z)**2
            ) / 2

            # Find neighbor sectors (26-connected in 3D)
            neighbors = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx == 0 and dy == 0 and dz == 0:
                            continue
                        nx_s, ny_s, nz_s = sx + dx, sy + dy, sz + dz
                        if 0 <= nx_s < nx_cells and 0 <= ny_s < ny_cells and 0 <= nz_s < nz_cells:
                            neighbor_id = f"sector_{nx_s}_{ny_s}_{nz_s}"
                            if neighbor_id in sector_nodes:
                                neighbors.append(neighbor_id)

            self._sectors[sector_id] = SectorBounds(
                sector_id=sector_id,
                min_x=sec_min_x, max_x=sec_max_x,
                min_y=sec_min_y, max_y=sec_max_y,
                min_z=sec_min_z, max_z=sec_max_z,
                neighbor_sectors=neighbors,
                center=(center_x, center_y, center_z),
                radius=radius,
            )

    async def navigate_to(
        self,
        start_rowid: int,
        target_query: str,
        entity_name: str,
        max_steps: int = 20,
    ) -> List[Dict[str, Any]]:
        """A* navigation from start to target using spatial + semantic edges.

        Returns path as list of node dicts with rowid, coords, content.
        """
        if not self._built or self._graph is None:
            await self.build_spatial_graph(entity_name)

        if start_rowid not in self._graph:
            raise ValueError(f"Start node {start_rowid} not in graph")

        # For now, use semantic search to find target candidates
        # In full implementation, this would use hybrid spatial+semantic query
        target_nodes = await self._find_target_nodes(entity_name, target_query)
        if not target_nodes:
            return []

        # A* to closest target
        target_rowid = target_nodes[0]["rowid"]
        path = await self._astar_path(start_rowid, target_rowid, max_steps)

        # Convert path to result format
        result = []
        for rowid in path:
            if rowid in self._nodes:
                node = self._nodes[rowid]
                result.append({
                    "rowid": rowid,
                    "uuid": node.uuid,
                    "content": node.content,
                    "coordinates": (node.x, node.y, node.z),
                    "metadata": node.metadata,
                })
        return result

    async def _find_target_nodes(self, entity_name: str, query: str) -> List[Dict[str, Any]]:
        """Find target nodes matching query using hybrid search."""
        # Use adapter's hybrid search
        try:
            # This would need an embedding - for now return empty
            # Full implementation: embed query, hybrid search, return top candidates
            return []
        except Exception:
            return []

    async def _astar_path(self, start: int, goal: int, max_steps: int) -> List[int]:
        """A* pathfinding on spatial graph."""
        if not self._graph or start not in self._graph or goal not in self._graph:
            return []

        # Heuristic: Euclidean distance in 3D
        def heuristic(a: int, b: int) -> float:
            if a not in self._nodes or b not in self._nodes:
                return float('inf')
            na, nb = self._nodes[a], self._nodes[b]
            return math.sqrt((na.x - nb.x)**2 + (na.y - nb.y)**2 + (na.z - nb.z)**2)

        open_set = [(heuristic(start, goal), 0.0, start, [start])]
        closed_set = set()
        g_scores = {start: 0.0}

        while open_set and len(closed_set) < max_steps:
            f_score, g_score, current, path = heapq.heappop(open_set)

            if current == goal:
                return path

            if current in closed_set:
                continue
            closed_set.add(current)

            for neighbor in self._graph.neighbors(current):
                if neighbor in closed_set:
                    continue

                edge_data = self._graph.get_edge_data(current, neighbor)
                weight = edge_data.get("weight", 1.0) if edge_data else 1.0
                tentative_g = g_score + weight

                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, tentative_g, neighbor, path + [neighbor]))

        # No path found, return direct path if close
        if heuristic(start, goal) < self.sector_size:
            return [start, goal]
        return [start]

    async def sector_stream(
        self,
        sector_bounds: Tuple[float, float, float, float, float, float],
        entity_name: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Stream memories in a BSP sector for Godot streaming.

        sector_bounds: (min_x, max_x, min_y, max_y, min_z, max_z)
        """
        min_x, max_x, min_y, max_y, min_z, max_z = sector_bounds

        def _sync_sector_query():
            conn = self.adapter._get_read_conn()
            cursor = conn.execute("""
                SELECT s.id, d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json,
                       s.minX, s.minY, s.minZ
                FROM omega_memory_spatial s
                JOIN omega_memory_data d ON s.id = d.id
                WHERE s.minX <= ? AND s.maxX >= ?
                  AND s.minY <= ? AND s.maxY >= ?
                  AND s.minZ <= ? AND s.maxZ >= ?
                  AND d.entity_name = ?
                LIMIT ?
            """, (max_x, min_x, max_y, min_y, max_z, min_z, entity_name, limit))

            results = []
            for row in cursor.fetchall():
                rowid, uuid, ent_name, session_id, role, content, timestamp, metadata_json, x, y, z = row
                metadata = {}
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        pass
                results.append({
                    "rowid": rowid,
                    "uuid": uuid,
                    "entity_name": ent_name,
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp,
                    "coordinates": (x, y, z),
                    "metadata": metadata,
                })
            return results

        import json
        return await anyio.to_thread.run_sync(_sync_sector_query)

    async def get_sector_memories(
        self,
        sector_id: str,
        entity_name: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all memories in a BSP sector for Godot streaming."""
        if sector_id not in self._sectors:
            return []

        sector = self._sectors[sector_id]
        bounds = (sector.min_x, sector.max_x, sector.min_y, sector.max_y, sector.min_z, sector.max_z)
        return await self.sector_stream(bounds, entity_name, limit)

    async def get_spatial_neighbors(
        self,
        rowid: int,
        k: int = 6,
    ) -> List[Tuple[int, float]]:
        """Get k nearest spatial neighbors for graph construction."""
        return await self._get_spatial_neighbors(rowid, k)

    def get_sector_info(self, sector_id: str) -> Optional[SectorBounds]:
        """Get sector bounds and metadata."""
        return self._sectors.get(sector_id)

    def get_entity_sectors(self, entity_name: str) -> List[str]:
        """Get all sector IDs for an entity."""
        return list(self._entity_sectors.get(entity_name, set()))

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        if not self._graph:
            return {"built": False}
        return {
            "built": True,
            "nodes": self._graph.number_of_nodes(),
            "edges": self._graph.number_of_edges(),
            "sectors": len(self._sectors),
            "entities": len(self._entity_sectors),
            "sector_size": self.sector_size,
        }


# ── Force-Directed Layout for Entities Without Coordinates ──────────────────

class ForceDirectedLayout:
    """Force-directed layout for assigning 3D coordinates to entities without explicit coordinates.

    Uses semantic similarity as spring force, spatial proximity as repulsion.
    Iterates to stable positions. Stores in metadata: spatial_x, spatial_y, spatial_z.
    """

    def __init__(
        self,
        adapter: SQLiteVecAdapterOptimized,
        iterations: int = 100,
        initial_temp: float = 100.0,
        decay_factor: float = 0.95,
        volume: float = 1000.0,
        repulsion_strength: float = 1.0,
        attraction_strength: float = 1.0,
    ):
        self.adapter = adapter
        self.iterations = iterations
        self.initial_temp = initial_temp
        self.decay_factor = decay_factor
        self.volume = volume
        self.repulsion_strength = repulsion_strength
        self.attraction_strength = attraction_strength

    async def compute_layout(
        self,
        entity_name: str,
        relationship_edges: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, Tuple[float, float, float]]:
        """Compute 3D coordinates for all memories of an entity.

        Args:
            entity_name: Entity to compute layout for.
            relationship_edges: Optional semantic relationships (uuid_a, uuid_b).

        Returns:
            Dict mapping uuid -> (x, y, z) coordinates.
        """
        # Fetch all memories for entity
        nodes = await self._fetch_all_nodes(entity_name)
        if not nodes:
            return {}

        uuids = [n["uuid"] for n in nodes]
        uuid_to_idx = {u: i for i, u in enumerate(uuids)}

        # Initialize random positions
        import random
        pos = {
            u: [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)]
            for u in uuids
        }

        # Build adjacency from relationships
        adj = defaultdict(set)
        if relationship_edges:
            for a, b in relationship_edges:
                if a in uuid_to_idx and b in uuid_to_idx:
                    adj[a].add(b)
                    adj[b].add(a)

        # Also add semantic similarity edges (top-k per node)
        # This would require vector similarity - simplified for now

        k = math.sqrt(self.volume / len(uuids))
        temp = self.initial_temp

        for iteration in range(self.iterations):
            disp = {u: [0.0, 0.0, 0.0] for u in uuids}

            # Repulsion: all pairs
            for i, u1 in enumerate(uuids):
                for u2 in uuids[i+1:]:
                    p1, p2 = pos[u1], pos[u2]
                    dx, dy, dz = p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]
                    d = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if d < 0.01:
                        d = 0.01
                        dx, dy, dz = random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01)

                    force = (k * k) / d * self.repulsion_strength
                    fx, fy, fz = (dx / d) * force, (dy / d) * force, (dz / d) * force

                    disp[u1][0] += fx; disp[u1][1] += fy; disp[u1][2] += fz
                    disp[u2][0] -= fx; disp[u2][1] -= fy; disp[u2][2] -= fz

            # Attraction: connected pairs
            for u1 in uuids:
                for u2 in adj[u1]:
                    p1, p2 = pos[u1], pos[u2]
                    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
                    d = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if d < 0.01:
                        continue

                    force = (d * d) / k * self.attraction_strength
                    fx, fy, fz = (dx / d) * force, (dy / d) * force, (dz / d) * force

                    disp[u1][0] += fx; disp[u1][1] += fy; disp[u1][2] += fz
                    disp[u2][0] -= fx; disp[u2][1] -= fy; disp[u2][2] -= fz

            # Apply displacement with cooling
            for u in uuids:
                dx, dy, dz = disp[u]
                mag = math.sqrt(dx*dx + dy*dy + dz*dz)
                if mag == 0:
                    continue
                limited = min(mag, temp)
                pos[u][0] += (dx / mag) * limited
                pos[u][1] += (dy / mag) * limited
                pos[u][2] += (dz / mag) * limited

            temp *= self.decay_factor

        # Convert to result dict
        result = {u: (pos[u][0], pos[u][1], pos[u][2]) for u in uuids}

        # Update database with new coordinates
        await self._update_coordinates(entity_name, result)

        return result

    async def _fetch_all_nodes(self, entity_name: str) -> List[Dict[str, Any]]:
        """Fetch all nodes for an entity (with or without coordinates)."""
        def _sync_fetch():
            conn = self.adapter._get_read_conn()
            cursor = conn.execute("""
                SELECT d.id, d.uuid, d.content, d.metadata_json,
                       s.minX, s.minY, s.minZ
                FROM omega_memory_data d
                LEFT JOIN omega_memory_spatial s ON d.id = s.id
                WHERE d.entity_name = ?
            """, (entity_name,))

            nodes = []
            for row in cursor.fetchall():
                rowid, uuid, content, metadata_json, x, y, z = row
                metadata = {}
                if metadata_json:
                    try:
                        import json
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        pass
                nodes.append({
                    "rowid": rowid,
                    "uuid": uuid,
                    "content": content or "",
                    "metadata": metadata,
                    "has_coords": x is not None,
                    "x": x or 0.0, "y": y or 0.0, "z": z or 0.0,
                })
            return nodes

        return await anyio.to_thread.run_sync(_sync_fetch)

    async def _update_coordinates(
        self,
        entity_name: str,
        coords_map: Dict[str, Tuple[float, float, float]],
    ) -> None:
        """Update spatial coordinates in R-tree and metadata."""
        def _sync_update():
            conn = self.adapter._get_write_conn()
            conn.execute("BEGIN IMMEDIATE")

            for uuid_str, (x, y, z) in coords_map.items():
                # Get rowid
                cursor = conn.execute(
                    "SELECT id FROM omega_memory_data WHERE uuid = ? AND entity_name = ?",
                    (uuid_str, entity_name)
                )
                row = cursor.fetchone()
                if not row:
                    continue
                rowid = row[0]

                # Update R-tree
                conn.execute("""
                    INSERT OR REPLACE INTO omega_memory_spatial
                    (id, minX, maxX, minY, maxY, minZ, maxZ)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (rowid, x, x, y, y, z, z))

                # Update metadata_json with spatial coords
                cursor = conn.execute(
                    "SELECT metadata_json FROM omega_memory_data WHERE id = ?",
                    (rowid,)
                )
                row = cursor.fetchone()
                metadata = {}
                if row and row[0]:
                    try:
                        import json
                        metadata = json.loads(row[0])
                    except json.JSONDecodeError:
                        pass

                metadata["spatial_x"] = x
                metadata["spatial_y"] = y
                metadata["spatial_z"] = z

                conn.execute(
                    "UPDATE omega_memory_data SET metadata_json = ? WHERE id = ?",
                    (json.dumps(metadata), rowid)
                )

            conn.commit()

        import json
        await anyio.to_thread.run_sync(_sync_update)
        logger.info("Updated spatial coordinates for %d nodes in entity %s", len(coords_map), entity_name)


# ── Singleton Access ────────────────────────────────────────────────────────

_spatial_graph: Optional[SpatialKnowledgeGraph] = None
_force_layout: Optional[ForceDirectedLayout] = None


def get_spatial_graph(adapter: SQLiteVecAdapterOptimized) -> SpatialKnowledgeGraph:
    """Get or create the singleton SpatialKnowledgeGraph."""
    global _spatial_graph
    if _spatial_graph is None:
        _spatial_graph = SpatialKnowledgeGraph(adapter)
    return _spatial_graph


def get_force_directed_layout(adapter: SQLiteVecAdapterOptimized) -> ForceDirectedLayout:
    """Get or create the singleton ForceDirectedLayout."""
    global _force_layout
    if _force_layout is None:
        _force_layout = ForceDirectedLayout(adapter)
    return _force_layout