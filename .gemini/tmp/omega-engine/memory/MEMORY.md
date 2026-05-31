# 🔱 Omega Engine Memory Index

## Project Overview
- **Name:** Omega Engine (Reclaimed Vision)
- **Role:** Senior Software Engineer / Collaborative Peer Programmer
- **Theme:** Syncretic mythological RAG engine (10 Pillar Keepers)
- **Tech Stack:** Python 3.12+, AnyIO, Qdrant, Redis, Postgres, FastAPI, MCP.

## Key Paths & Ports
- `omega-hub`: **Port 8016** (Consolidated MCP, Decision 50)
- `omega-iris`: **Port 8080** (Voice assistant)
- `lmster`: **Port 1234** (Primary local inference)
- `src/omega/oracle/oracle.py`: Core routing logic.
- `src/omega/oracle/model_gateway.py`: Local model management.
- `config/entities.yaml`: Entity definitions (the 10 Keepers).
- `RECLAIMED_VISION.md`: The canonical architectural vision.

## Active Intelligence
- **Jem 2.0 Oversoul**: 3 sub-facets for tiered research:
    1. **Initiate (L1)**: Qwen3-1.7B (lmster), raw fact gathering.
    2. **Analyst (L2)**: Gemma 4 31B, synthesis and uncertainty manifest.
    3. **Editor (L3)**: Big Pickle (frontier), final QA and resolution.
- **Sovereign Plugin**: OpenCode plugin calling Hub for identity and boundary guarding.

## Common Workflows
- `make setup`: Install dependencies.
- `make test`: Run test suite.
- `omega talk "<query>"`: Interact with the Oracle.
- `omega summon <Entity> "<query>"`: Direct entity interaction.

## Notes
- "Iris" seems to be the current name for the voice assistant container (formerly "Nova").
- High performance is a priority (see `cpu_optimizer.py`).
- Infrastructure runs in Podman (`deploy/infra/docker-compose.yml`).
