# 🔱 Iris — The Voice Assistant
**AP Token**: `AP-IRIS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Iris package — always-on voice assistant container with intent detection and entity routing.
**Tags**: iris, voice, assistant, fastapi, intent-matching, oracle
**Cross-references**: src/omega/iris/server.py, src/omega/iris/matcher.py, src/omega/oracle/oracle.py, docs/architecture/ORACLE_DEEP_DIVE.md

---

## Overview

The `iris` package implements **Iris** — the always-on voice assistant for the Omega Engine. She runs as a lightweight Podman container and serves as the primary user interface.

**Iris Responsibilities**:
- Listens for user input (HTTP, voice, CLI)
- Routes to correct entity via Oracle
- Answers simple queries directly with qwen3-1.7b-270m
- Bridges between user and the 10 specialist nodes

**Specs**: Python 3.13-slim + qwen3-1.7b-270m (~500MB image, ~300MB RAM)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Iris Package                            │
├─────────────────────────────────────────────────────────────┤
│  server.py           │  FastAPI server + endpoints          │
│  matcher.py          │  IntentMatcher — intent detection    │
│  __init__.py         │  (empty — exports via modules)       │
└─────────────────────────────────────────────────────────────┘
```

**Flow**:
```
User Input → IrisEngine.handle() → IntentMatcher.classify()
                                    ↓
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              "summon"         "domain"         "direct"
                    ▼               ▼               ▼
            Oracle.summon()   Oracle.talk()   Iris direct response
```

---

## IrisEngine (server.py)

### Constructor

```python
IrisEngine()
```
Initializes `Oracle()` instance.

### Methods

#### `async handle(query: str, entity: Optional[str] = None) -> OracleResponse`
Route query to correct entity.

```python
engine = IrisEngine()

# Direct summon
result = await engine.handle("Harden the container", entity="Prometheus")

# Auto-route via Iris
result = await engine.handle("What is the Engine-Stack Firewall?")
```

**Parameters**:
- `query`: User input text
- `entity`: Optional explicit entity name (bypasses intent matching)

**Returns**: `OracleResponse` with `text`, `entity`, `slots`, etc.

---

## FastAPI Endpoints

### `POST /chat`
Main chat endpoint — routes to correct entity.

**Request**:
```json
{
  "query": "What is a WAD?",
  "entity": null
}
```

**Response**:
```json
{
  "response": "A WAD (Where's All Data) is...",
  "entity": "Iris",
  "slots": []
}
```

### `GET /health`
Health check for Podman.

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### `POST /voice`
Voice endpoint — accepts text from Whisper STT, returns TTS-ready text.

**Request/Response**: Same as `/chat`

### `GET /entities`
List all available entities from Oracle registry.

**Response**:
```json
{
  "entities": [
    {"name": "Prometheus", "slots": ["P1", "P2"], "domains": ["security", "infrastructure"]},
    {"name": "Kali", "slots": ["P3"], "domains": ["audit", "compliance"]}
  ]
}
```

---

## IntentMatcher (matcher.py)

Lightweight intent detection for the always-on Iris container.

### Classification Types

| Type | Description | Handler |
|------|-------------|---------|
| `summon` | Explicit entity request | `Oracle.summon()` |
| `domain` | Needs domain routing | `Oracle.talk()` |
| `direct` | Iris can answer directly | Iris response |
| `voice_cmd` | Voice control (volume, repeat) | Special handling |

### Patterns

| Pattern | Regex | Example |
|---------|-------|---------|
| `@summon` | `^@(\w+)[,:\s]+(.+)$` | `@Prometheus harden the container` |
| `Hey/Summon` | `^(?:hey\s+|summon\s+)(.+?)[,:]\s*(.*)$` | `Hey Prometheus, harden the container` |
| Greeting | `^\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b` | `Hello Iris` |
| Farewell | `^\b(bye|goodbye|exit|quit|thanks?|thank you)\b` | `Goodbye` |
| Help | `^\b(help|what can you do|commands|how do i)\b[?.]*$` | `What can you do?` |
| Repeat | `(repeat|say that again|what did you say)` | `Repeat that` |
| Volume | `(volume|louder|softer|quieter)` | `Volume up` |
| Speed | `(speed|faster|slower)` | `Speak slower` |

### Methods

#### `classify(text: str) -> Tuple[str, Optional[str]]`
Classify intent and return `(intent_type, entity_name)`.

```python
matcher = IntentMatcher()

matcher.classify("@Prometheus harden the container")
# ("summon", "Prometheus")

matcher.classify("Hey Iris, what is a WAD?")
# ("summon", "Iris")

matcher.classify("What is the Engine-Stack Firewall?")
# ("domain", None)

matcher.classify("Hello there!")
# ("direct", None)

matcher.classify("Say that again")
# ("voice_cmd", "repeat")
```

#### `is_iris_capable(text: str) -> bool`
Can Iris answer directly without routing?

```python
matcher.is_iris_capable("Hello!")  # True
matcher.is_iris_capable("What is M2?")  # False
```

#### `iris_response(text: str) -> Optional[str]`
Generate direct Iris response for simple queries.

```python
matcher.iris_response("Hello!")
# "Greetings, seeker. I am Iris, your voice interface..."

matcher.iris_response("Help")
# "I can help you connect with any entity...\n  'summon [entity]'..."
```

---

## Deployment

### Podman Container

```dockerfile
# Containerfile
FROM python:3.13-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["python", "-m", "omega.iris.server"]
```

```bash
# Build
podman build -t omega-iris .

# Run
podman run -d \
  --name omega-iris \
  -p 8080:8080 \
  --health-cmd="curl -f http://localhost:8080/health || exit 1" \
  --health-interval=30s \
  omega-iris
```

### Direct Run

```bash
# Development
python -m omega.iris.server
# Runs on 127.0.0.1:8080

# With uvicorn directly
uvicorn omega.iris.server:app --host 0.0.0.0 --port 8080
```

---

## Usage Example

```python
from omega.iris import IrisEngine, IntentMatcher

engine = IrisEngine()
matcher = IntentMatcher()

# Check intent before routing
intent, entity = matcher.classify(user_input)

if intent == "direct":
    response = matcher.iris_response(user_input)
elif intent == "summon":
    result = await engine.handle(user_input, entity=entity)
else:  # domain
    result = await engine.handle(user_input)

print(result.text)
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | FastAPI/uvicorn native async |
| **M2 Firewall** | Iris is interface; Oracle handles engine logic |
| **M7 Local-First** | Oracle routes local-first; Iris direct uses local qwen3-1.7b-270m |
| **M8 Zero Telemetry** | No external analytics |
| **M13 Temple-Grade** | Structured error responses; health endpoint |
| **M22 Response Provenance** | OracleResponse includes `provider_name` |
| **M23 Failure Integrity** | HTTP 500 with error detail; no silent failures |

---

## Testing

```bash
pytest tests/test_iris_server.py tests/test_iris_matcher.py -v
```

Key test scenarios:
- Intent classification accuracy
- Direct response generation
- FastAPI endpoint responses
- Health check endpoint
- Entity listing
- Error handling

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ IRIS-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

