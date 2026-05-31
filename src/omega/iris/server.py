# 🔱 Iris — The Voice Assistant
# AP: AP-NOVA-SERVER-v1.0.0
# ICS: [NODE: HERMES | ARCHETYPE: HERMES | CONTEXT: NOVA-MESSENGER]
#
# Iris is the always-on Podman container. She:
#   - Listens for user input (HTTP, voice, CLI)
#   - Routes to the correct Pillar Keeper via the Oracle
#   - Answers simple queries directly with qwen3-1.7b-270m
#   - Bridges between user and the 10 Pillar Keepers
#
# Lightweight: python:3.13-slim + qwen3-1.7b-270m (~500MB image, ~300MB RAM)

import logging
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add src to path so we can import omega modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from omega.oracle import Oracle, OracleResponse

logger = logging.getLogger("iris")
logging.basicConfig(level=logging.INFO)

# ── FastAPI App ──────────────────────────────────────────────────────────
app = FastAPI(title="Iris — Omega Voice Assistant", version="1.0.0")


# ── Request/Response Models ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    entity: Optional[str] = None  # Direct summon if provided


class ChatResponse(BaseModel):
    response: str
    entity: str
    pillars: list[str] = []
    sigil: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str


# ── Iris Engine ──────────────────────────────────────────────────────────
class IrisEngine:
    """Iris routing and response logic."""

    def __init__(self):
        self.oracle = Oracle()

    async def handle(self, query: str, entity: Optional[str] = None) -> OracleResponse:
        """Route query to the correct entity."""
        if entity:
            result = await self.oracle.summon(entity, query)
        else:
            result = await self.oracle.talk(query)
        return result


engine = IrisEngine()


# ── Endpoints ────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint. Routes to correct entity."""
    try:
        result = await engine.handle(request.query, request.entity)
        return ChatResponse(
            response=result.text,
            entity=result.entity,
            pillars=result.pillars,
            sigil=result.sigil,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for Podman."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/voice")
async def voice(request: ChatRequest):
    """Voice endpoint. Accepts text from Whisper STT, returns TTS-ready text."""
    try:
        result = await engine.handle(request.query, request.entity)
        return ChatResponse(
            response=result.text,
            entity=result.entity,
            pillars=result.pillars,
            sigil=result.sigil,
        )
    except Exception as e:
        logger.error(f"Voice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entities")
async def list_entities():
    """List all available entities."""
    entities = engine.oracle.registry.list()
    return {
        "entities": [
            {
                "name": e.name,
                "pillar": e.pillars,
                "pantheon": e.pantheon,
                "sigil": e.sigil,
                "domains": e.domains,
            }
            for e in entities
        ]
    }


# ── Direct entry point ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
