# 🔱 Bridge — OpenCode WebSocket Bridge
**AP Token**: `AP-BRIDGE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Bridge package — FastAPI WebSocket bridge between OpenCode clients and the Omega Oracle.
**Tags**: bridge, websocket, opencode, fastapi, oracle, budget-gate, token-ledger
**Cross-references**: src/omega/bridge/opencode_bridge.py, src/omega/oracle/oracle.py, src/omega/observability/token_ledger.py, docs/architecture/MESH_NETWORK_SPEC.md

---

## Overview

The `bridge` package provides a **FastAPI WebSocket bridge** that connects OpenCode clients to the Omega Oracle. It implements the transfer of user messages to the Oracle and streams responses back while enforcing budget gates and token ledgering.

This is the **Carmack Mode P0-2** implementation — minimal, working scaffold for immediate dev leverage. Full ACP multiplexer deferred (D-435).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Bridge Package                            │
├─────────────────────────────────────────────────────────────┤
│  opencode_bridge.py  │  OpenCodeBridge — FastAPI + WS      │
│                      │  BudgetGate — cloud budget enforcement│
│                      │  TokenLedger — usage tracking         │
└─────────────────────────────────────────────────────────────┘
```

**Flow**:
```
OpenCode Client → WebSocket (/ws/chat) → OpenCodeBridge
                                                    ↓
                                            BudgetGate.check_budget()
                                                    ↓
                                            Oracle.talk() / Oracle.summon()
                                                    ↓
                                            TokenLedger.record_transaction()
                                                    ↓
                                            Stream response chunks → Client
```

---

## Components

### BudgetGate

Conceptual equivalent to `src/omega/oracle/budget_gate.py`. Enforces hard-stop cloud budget gates for sovereign inference.

```python
class BudgetGate:
    @staticmethod
    async def check_budget(entity_name: str, trace_id: str) -> bool:
        """
        Verify if entity has remaining budget for cloud inference.
        
        Args:
            entity_name: Entity requesting inference
            trace_id: Request trace ID
            
        Returns:
            True if budget available, False otherwise
        """
        # Default: True (real impl queries budget store)
        return True
```

**Integration**: Called before every Oracle inference. If `False`, returns `"❌ Budget gate exceeded. Cloud inference blocked."` to client.

---

### OpenCodeBridge

FastAPI WebSocket bridge between OpenCode clients and the Omega Oracle.

#### Constructor

```python
OpenCodeBridge()
```

Initializes:
- `Oracle()` instance
- FastAPI app with title "Omega OpenCode Bridge"
- Routes: `/health`, `/ws/chat`, `/voice`

#### Methods

##### `_load_soul_context(entity_name: str) -> str`
Minimal SOUL.md loader for entity-specific bridge context.

```python
soul_context = bridge._load_soul_context("prometheus")
# Returns content of data/entities/prometheus/SOUL.md or ""
```

##### `async _handle_inference(websocket: WebSocket, query: str)`
Coordinate inference flow: Budget Gate → Oracle → Ledger.

```python
await bridge._handle_inference(websocket, "Harden the container security")
```

**Flow**:
1. Generate `trace_id`
2. `BudgetGate.check_budget(entity_name, trace_id)` — block if exceeded
3. `Oracle.talk(query)` — forward to Oracle
4. `TokenLedger.record_transaction()` — log usage (M22 provenance)
5. Stream response in 50-char chunks with 10ms delay

**Error Handling**:
- `OmegaError` → `"⚠️ Engine Error: {error}"`
- Other exceptions → `"❌ A critical system error occurred."`

#### `_setup_routes()`
Configures FastAPI endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Sovereign health probe |
| `/ws/chat` | WebSocket | Main chat bridge |
| `/voice` | POST | Voice endpoint (STT→Oracle→TTS) |
| `/entities` | GET | List available entities |

---

## FastAPI Endpoints

### `GET /health`
```json
{
  "status": "online",
  "engine": "omega-core",
  "bridge": "opencode-v1"
}
```

### `WebSocket /ws/chat`
Main bridge for OpenCode communication.

**Client → Server**: Plain text query
**Server → Client**: Streamed text chunks (50 chars, 10ms interval)

```python
# Client example
import websockets

async with websockets.connect("ws://localhost:8000/ws/chat") as ws:
    await ws.send("What is the Engine-Stack Firewall?")
    async for chunk in ws:
        print(chunk, end="", flush=True)
```

### `POST /voice`
Voice endpoint — accepts text from Whisper STT, returns TTS-ready text.

```json
// Request
{"query": "Hello Iris", "entity": null}

// Response
{"response": "Greetings...", "entity": "Iris", "slots": []}
```

### `GET /entities`
List all available entities from Oracle registry.

```json
{
  "entities": [
    {"name": "Prometheus", "slots": ["P1", "P2"], "domains": ["security", "infrastructure"]},
    {"name": "Kali", "slots": ["P3"], "domains": ["audit", "compliance"]}
  ]
}
```

---

## Server Initialization

```python
# At module level — for FastAPI server (uvicorn)
from omega.bridge.opencode_bridge import bridge
app = bridge.app

# Run with: uvicorn omega.bridge.opencode_bridge:app --host 0.0.0.0 --port 8000
```

---

## Usage Example

```python
from omega.bridge.opencode_bridge import OpenCodeBridge
import uvicorn

# Create bridge
bridge = OpenCodeBridge()

# Run server
uvicorn.run(bridge.app, host="0.0.0.0", port=8000)

# Or import app directly
from omega.bridge.opencode_bridge import app
# uvicorn omega.bridge.opencode_bridge:app
```

---

## Configuration

The bridge uses the Oracle's configuration (providers, models, resource guards). No separate bridge config exists currently.

**Future**: BudgetGate will integrate with a persistent budget store (Redis/SQLite) for per-entity cloud spend limits.

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | FastAPI/uvicorn native async; `anyio.sleep` for streaming delay |
| **M7 Local-First** | Oracle routes local-first; bridge is transport only |
| **M8 Zero Telemetry** | No external analytics; local TokenLedger only |
| **M13 Temple-Grade** | BudgetGate hard-stop; structured error responses |
| **M22 Response Provenance** | TokenLedger records `provider_name` from Oracle response |
| **M23 Failure Integrity** | WebSocket errors caught and reported; no silent failures |

---

## Current Limitations (Deferred)

| Feature | Status | Deferred To |
|---------|--------|-------------|
| ACP stdio multiplexer | ❌ Not implemented | D-435 |
| Mid-stream 402 recovery | ❌ Not implemented | ACP multiplexer |
| Per-entity budget store | ❌ Stub returns `True` | BudgetGate impl |
| Entity summon via WS | ❌ Only `talk` supported | Phase 2 |
| Authentication | ❌ Self-asserted identity | M18 |

---

## Testing

```bash
# Start bridge server
uvicorn omega.bridge.opencode_bridge:app --host 0.0.0.0 --port 8000

# Test with websocat
echo "What is a WAD?" | websocat ws://localhost:8000/ws/chat

# Test health endpoint
curl http://localhost:8000/health
```

```bash
pytest tests/test_opencode_bridge.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ BRIDGE-v1.0.0 ⬡ 2026-10-02 ⬡*