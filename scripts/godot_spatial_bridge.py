#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Godot Spatial Bridge — HTTP/WebSocket Server for VR Navigation.
AP: AP-GODOT-SPATIAL-BRIDGE-v1.0.0

Provides REST and WebSocket endpoints for Godot 4 to query spatial memories:
- GET /spatial/range?x=10&y=5&z=2&radius=5&entity=kali
- GET /spatial/sector?sector=sector_12&entity=grokster
- GET /spatial/navigate?start=123&target=hello&entity=kali
- GET /spatial/hybrid?x=10&y=5&z=2&query=hello&entity=kali
- WS  /spatial/stream — Real-time sector streaming for Godot

[id-soft: doom-1993] BSP Culling — Spatial partitioning for efficiency
[id-soft: quake-1996] PVS (Potentially Visible Set) — Sector-based visibility
"""

import anyio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from omega.memory.sqlite_vec_adapter_optimized import SQLiteVecAdapterOptimized
from omega.memory.spatial_graph import get_spatial_graph, get_force_directed_layout

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_DB_PATH = os.environ.get(
    "OMEGA_DB_PATH",
    os.path.join(os.path.expanduser("~"), "omega", "data", "omega_memory.db")
)
DEFAULT_HOST = os.environ.get("GODOT_BRIDGE_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.environ.get("GODOT_BRIDGE_PORT", "8765"))

# ── Pydantic Models ──────────────────────────────────────────────────────────

class SpatialRangeRequest(BaseModel):
    x: float = Field(..., description="Center X coordinate")
    y: float = Field(..., description="Center Y coordinate")
    z: float = Field(..., description="Center Z coordinate")
    radius: float = Field(10.0, ge=0.1, le=1000.0, description="Search radius")
    entity: str = Field(..., description="Entity name")
    limit: int = Field(50, ge=1, le=500, description="Max results")


class SectorRequest(BaseModel):
    sector: str = Field(..., description="Sector ID (e.g., sector_0_1_2)")
    entity: str = Field(..., description="Entity name")
    limit: int = Field(50, ge=1, le=500, description="Max results")


class NavigateRequest(BaseModel):
    start_rowid: Optional[int] = Field(None, description="Start node rowid")
    start_x: Optional[float] = Field(None, description="Start X coordinate")
    start_y: Optional[float] = Field(None, description="Start Y coordinate")
    start_z: Optional[float] = Field(None, description="Start Z coordinate")
    target_query: str = Field(..., description="Semantic target query")
    entity: str = Field(..., description="Entity name")
    max_steps: int = Field(20, ge=1, le=100, description="Max path steps")


class HybridRequest(BaseModel):
    x: float = Field(..., description="Query position X")
    y: float = Field(..., description="Query position Y")
    z: float = Field(..., description="Query position Z")
    query: str = Field(..., description="Semantic query text")
    entity: str = Field(..., description="Entity name")
    semantic_weight: float = Field(0.7, ge=0.0, le=1.0)
    spatial_weight: float = Field(0.3, ge=0.0, le=1.0)
    radius: float = Field(50.0, ge=0.1, le=1000.0)
    limit: int = Field(20, ge=1, le=100)
    collection: str = Field("omega_vec_qwen_768", description="Vector collection")


class NeighborsRequest(BaseModel):
    rowid: int = Field(..., description="Node rowid")
    k: int = Field(6, ge=1, le=50, description="Number of neighbors")
    entity: str = Field(..., description="Entity name")


class LayoutRequest(BaseModel):
    entity: str = Field(..., description="Entity name")
    iterations: int = Field(100, ge=10, le=1000)


class SpatialResponse(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    count: int = 0


# ── Global State ─────────────────────────────────────────────────────────────

adapter: Optional[SQLiteVecAdapterOptimized] = None
active_websockets: List[WebSocket] = []


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global adapter
    logger.info("Starting Godot Spatial Bridge...")
    logger.info("DB Path: %s", DEFAULT_DB_PATH)

    adapter = SQLiteVecAdapterOptimized(db_path=DEFAULT_DB_PATH)
    await adapter._ensure_initialized()

    logger.info("Adapter initialized. Bridge ready on %s:%d", DEFAULT_HOST, DEFAULT_PORT)
    yield

    logger.info("Shutting down Godot Spatial Bridge...")
    if adapter:
        await adapter.close()
    for ws in active_websockets:
        await ws.close()


# ── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Omega Engine — Godot Spatial Bridge",
    description="Spatial memory queries for VR navigation in Godot 4",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper Functions ─────────────────────────────────────────────────────────

def _require_adapter() -> SQLiteVecAdapterOptimized:
    if adapter is None:
        raise HTTPException(status_code=503, detail="Adapter not initialized")
    return adapter


async def _broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients."""
    dead = []
    for ws in active_websockets:
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_websockets.remove(ws)


# ── REST Endpoints ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "godot-spatial-bridge"}


@app.get("/spatial/range", response_model=SpatialResponse)
async def spatial_range(
    x: float = Query(..., description="Center X"),
    y: float = Query(..., description="Center Y"),
    z: float = Query(..., description="Center Z"),
    radius: float = Query(10.0, ge=0.1, le=1000.0),
    entity: str = Query(..., description="Entity name"),
    limit: int = Query(50, ge=1, le=500),
):
    """Find all memories within radius of (x,y,z) — VR navigation query."""
    try:
        ad = _require_adapter()
        results = await ad.spatial_range_query(entity, x, y, z, radius, limit)
        return SpatialResponse(success=True, data=results, count=len(results))
    except Exception as e:
        logger.error("Spatial range query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/sector", response_model=SpatialResponse)
async def spatial_sector(
    sector: str = Query(..., description="Sector ID"),
    entity: str = Query(..., description="Entity name"),
    limit: int = Query(50, ge=1, le=500),
):
    """Get all memories in a BSP sector for Godot streaming."""
    try:
        ad = _require_adapter()
        results = await ad.get_sector_memories(sector, entity, limit)
        return SpatialResponse(success=True, data=results, count=len(results))
    except Exception as e:
        logger.error("Sector query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/navigate", response_model=SpatialResponse)
async def spatial_navigate(
    start_rowid: Optional[int] = Query(None),
    start_x: Optional[float] = Query(None),
    start_y: Optional[float] = Query(None),
    start_z: Optional[float] = Query(None),
    target_query: str = Query(..., description="Semantic target query"),
    entity: str = Query(..., description="Entity name"),
    max_steps: int = Query(20, ge=1, le=100),
):
    """VR navigation: spatial A* from start to semantic target."""
    try:
        ad = _require_adapter()

        # Determine start position
        if start_rowid is not None:
            # Get coordinates from rowid
            def _get_coords():
                conn = ad._get_read_conn()
                cursor = conn.execute(
                    "SELECT minX, minY, minZ FROM omega_memory_spatial WHERE id = ?",
                    (start_rowid,)
                )
                row = cursor.fetchone()
                return row

            row = await anyio.to_thread.run_sync(_get_coords)
            if not row:
                raise HTTPException(status_code=404, detail=f"Node {start_rowid} not found")
            start_pos = (row[0], row[1], row[2])
        elif all(v is not None for v in (start_x, start_y, start_z)):
            start_pos = (start_x, start_y, start_z)
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either start_rowid or start_x/start_y/start_z"
            )

        results = await ad.vr_navigate_to(entity, start_pos, target_query, max_steps)
        return SpatialResponse(success=True, data=results, count=len(results))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Navigation query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/hybrid", response_model=SpatialResponse)
async def spatial_hybrid(
    x: float = Query(..., description="Query position X"),
    y: float = Query(..., description="Query position Y"),
    z: float = Query(..., description="Query position Z"),
    query: str = Query(..., description="Semantic query text"),
    entity: str = Query(..., description="Entity name"),
    semantic_weight: float = Query(0.7, ge=0.0, le=1.0),
    spatial_weight: float = Query(0.3, ge=0.0, le=1.0),
    radius: float = Query(50.0, ge=0.1, le=1000.0),
    limit: int = Query(20, ge=1, le=100),
    collection: str = Query("omega_vec_qwen_768"),
):
    """Hybrid semantic + spatial query for VR-aware retrieval."""
    try:
        ad = _require_adapter()

        # Note: This requires an embedding vector for the query.
        # For now, we'll need the client to provide the vector or we embed here.
        # This is a placeholder - full implementation needs embedding provider.
        raise HTTPException(
            status_code=501,
            detail="Hybrid query requires embedding vector. Use POST /spatial/hybrid with vector."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Hybrid query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.post("/spatial/hybrid", response_model=SpatialResponse)
async def spatial_hybrid_post(request: HybridRequest):
    """Hybrid semantic + spatial query with embedding vector."""
    try:
        ad = _require_adapter()

        # TODO: Embed the query text to get vector
        # For now, return error indicating embedding needed
        raise HTTPException(
            status_code=501,
            detail="Query embedding not implemented. Provide pre-computed vector in future version."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Hybrid POST query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/neighbors", response_model=SpatialResponse)
async def spatial_neighbors(
    rowid: int = Query(..., description="Node rowid"),
    k: int = Query(6, ge=1, le=50),
    entity: str = Query(..., description="Entity name"),
):
    """Get k nearest spatial neighbors for graph construction."""
    try:
        ad = _require_adapter()
        neighbors = await ad.get_spatial_neighbors(rowid, k)
        data = [{"rowid": n[0], "distance": n[1]} for n in neighbors]
        return SpatialResponse(success=True, data=data, count=len(data))
    except Exception as e:
        logger.error("Neighbors query failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.post("/spatial/layout", response_model=SpatialResponse)
async def compute_layout(request: LayoutRequest):
    """Compute force-directed layout for entity memories without coordinates."""
    try:
        ad = _require_adapter()
        layout = get_force_directed_layout(ad)
        coords = await layout.compute_layout(request.entity, iterations=request.iterations)
        data = {uuid: {"x": x, "y": y, "z": z} for uuid, (x, y, z) in coords.items()}
        return SpatialResponse(success=True, data=data, count=len(data))
    except Exception as e:
        logger.error("Layout computation failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/graph/stats", response_model=SpatialResponse)
async def graph_stats(entity: str = Query(..., description="Entity name")):
    """Get spatial graph statistics."""
    try:
        ad = _require_adapter()
        graph = get_spatial_graph(ad)
        await graph.build_spatial_graph(entity)
        stats = graph.get_graph_stats()
        return SpatialResponse(success=True, data=stats, count=1)
    except Exception as e:
        logger.error("Graph stats failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


@app.get("/spatial/sectors", response_model=SpatialResponse)
async def list_sectors(entity: str = Query(..., description="Entity name")):
    """List all BSP sectors for an entity."""
    try:
        ad = _require_adapter()
        graph = get_spatial_graph(ad)
        await graph.build_spatial_graph(entity)
        sectors = graph.get_entity_sectors(entity)
        sector_infos = []
        for sid in sectors:
            sector = graph.get_sector_info(sid)
            if sector:
                sector_infos.append({
                    "sector_id": sector.sector_id,
                    "center": sector.center,
                    "radius": sector.radius,
                    "bounds": {
                        "min_x": sector.min_x, "max_x": sector.max_x,
                        "min_y": sector.min_y, "max_y": sector.max_y,
                        "min_z": sector.min_z, "max_z": sector.max_z,
                    },
                    "neighbors": sector.neighbor_sectors,
                })
        return SpatialResponse(success=True, data=sector_infos, count=len(sector_infos))
    except Exception as e:
        logger.error("List sectors failed: %s", e, exc_info=True)
        return SpatialResponse(success=False, error=str(e))


# ── WebSocket Endpoint ───────────────────────────────────────────────────────

@app.websocket("/spatial/stream")
async def spatial_stream(websocket: WebSocket):
    """WebSocket for real-time sector streaming to Godot.

    Client sends: {"type": "subscribe", "entity": "kali", "sectors": ["sector_0_0_0", ...]}
    Server sends: {"type": "sector_update", "sector": "...", "memories": [...]}
    """
    await websocket.accept()
    active_websockets.append(websocket)
    logger.info("WebSocket connected. Total: %d", len(active_websockets))

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "subscribe":
                entity = data.get("entity")
                sectors = data.get("sectors", [])
                if not entity:
                    await websocket.send_json({"type": "error", "message": "entity required"})
                    continue

                ad = _require_adapter()
                graph = get_spatial_graph(ad)
                await graph.build_spatial_graph(entity)

                # Send initial sector data
                for sector_id in sectors:
                    memories = await graph.get_sector_memories(sector_id, entity, limit=100)
                    await websocket.send_json({
                        "type": "sector_update",
                        "sector": sector_id,
                        "memories": memories,
                        "count": len(memories),
                    })

                # Acknowledge subscription
                await websocket.send_json({
                    "type": "subscribed",
                    "entity": entity,
                    "sectors": sectors,
                })

            elif msg_type == "range_query":
                # Real-time range query
                x = data.get("x", 0)
                y = data.get("y", 0)
                z = data.get("z", 0)
                radius = data.get("radius", 10)
                entity = data.get("entity")
                limit = data.get("limit", 50)

                if not entity:
                    await websocket.send_json({"type": "error", "message": "entity required"})
                    continue

                ad = _require_adapter()
                results = await ad.spatial_range_query(entity, x, y, z, radius, limit)
                await websocket.send_json({
                    "type": "range_result",
                    "query_id": data.get("query_id"),
                    "memories": results,
                    "count": len(results),
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({"type": "error", "message": f"Unknown type: {msg_type}"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error: %s", e, exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.info("WebSocket cleaned up. Total: %d", len(active_websockets))


# ── Main Entry Point ─────────────────────────────────────────────────────────

def main():
    """Run the Godot Spatial Bridge server."""
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 60)
    logger.info("  Omega Engine — Godot Spatial Bridge")
    logger.info("  AP: AP-GODOT-SPATIAL-BRIDGE-v1.0.0")
    logger.info("  [id-soft: doom-1993] BSP Culling")
    logger.info("=" * 60)

    uvicorn.run(
        "godot_spatial_bridge:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()