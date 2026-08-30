# API Reference: Oracle

> Oracle — unified routing, summoning, and entity intelligence.

---

## OracleResponse

**File**: `src/omega/oracle/oracle.py`

Structured response returned by the Oracle's `talk` and `summon` interfaces.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | *Required* | The markdown text response from the entity. |
| `entity` | `str` | `"Oracle"` | Name of the entity that generated the response. |
| `confidence` | `float` | `0.5` | Speculative confidence score (0.0 to 1.0). |
| `trace_id` | `str` | `""` | Trace ID for observability and logging. |
| `slots` | `Optional[List[str]]` | `None` | P1-P10 slots occupied by the entity. |
| `domains` | `Optional[List[str]]` | `None` | Semantic domains handled by this entity. |
| `backend` | `Optional[str]` | `None` | Inference backend provider used (e.g., `"native-gguf"`). |
| `model` | `Optional[str]` | `None` | Model name/ID used for generation. |
| `session_id` | `Optional[str]` | `None` | Active session identifier. |
| `escalated` | `bool` | `False` | True if the query was escalated from Iris to a specialist. |
| `cost_warning` | `Optional[str]` | `None` | Warning message if token budget limits were exceeded. |

---

## Oracle

**File**: `src/omega/oracle/oracle.py`

The main entry point for the Omega Engine's intelligence. It handles intent detection, speculative decoding, domain routing, entity summoning, and soul evolution.

### Constructor

```python
Oracle(registry: Optional[EntityRegistry] = None, model_gateway: Optional[ModelGateway] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `registry` | `Optional[EntityRegistry]` | `None` | Custom entity registry. If `None`, initializes a default one. |
| `model_gateway` | `Optional[ModelGateway]` | `None` | Custom model gateway. If `None`, initializes a default one. |

### Methods

#### `await bootstrap() -> None`

Initializes the Oracle's subsystems, archives stale sessions (M12 compliance), and loads active WAD files. This is automatically called on the first query if not manually invoked.

```python
oracle = Oracle()
await oracle.bootstrap()
```

#### `await talk(query: Union[str, TaintedData], transient: bool = False) -> OracleResponse`

The primary conversational interface. Speculatively decodes queries using Iris. If Iris confidence is low, escalates the query to a domain-matched specialist entity via the semantic router.

```python
response = await oracle.talk("Tell me about my system's health")
print(f"[{response.entity}]: {response.text}")
```

**Parameters**:
- `query`: The user query string or `TaintedData` wrapper for untrusted web inputs.
- `transient`: If `True`, the interaction is not persisted to memory (useful for one-off checks).

**Returns**: `OracleResponse`

#### `await summon(entity_name: str, query: str, session_id: Optional[str] = None, trace_id: Optional[str] = None, transient: bool = False) -> OracleResponse`

Directly summons a specific named entity, bypassing Iris and the semantic router.

```python
response = await oracle.summon("Prometheus", "Harden the container security")
```

**Parameters**:
- `entity_name`: The exact name of the entity to summon.
- `query`: The query string to send to the entity.
- `session_id`: Optional session ID. If omitted, uses or creates the active rolling session.
- `trace_id`: Optional trace ID for tracking.
- `transient`: If `True`, the interaction is not persisted to memory.

**Returns**: `OracleResponse`

#### `assess_confidence(query: str) -> float`

Assess the speculative confidence score of Iris for a given query. If the score is below `IRIS_CONFIDENCE_THRESHOLD` (default `0.6`), the query will be escalated to a specialist.

```python
confidence = oracle.assess_confidence("Hi there!") # High confidence (~1.0)
confidence = oracle.assess_confidence("Write a rust compiler") # Low confidence (~0.1)
```

**Returns**: `float` (0.0 to 1.0)

#### `await verify_claim(claim: str, evidence: List[Dict[str, Any]]) -> VerificationResult`

Uses the local `SkepticalVerifier` to verify an untrusted claim against provided evidence.

**Returns**: `VerificationResult`

#### `await close_session(entity_name: str, session_id: str) -> bool`

Closes an active session, triggering the L1→L2→L3 soul distillation pipeline and writing any newly discovered principles to `proposed_lessons.yaml` (M11 compliance).

```python
success = await oracle.close_session("Prometheus", "ses_20260704_prometheus_1")
```

**Returns**: `bool` — `True` if successfully distilled and saved, `False` otherwise.

#### `await retrieve_headroom_content(ref_id: str) -> str`

Retrieves exact raw content cached by the Headroom middleware using its reference ID, preventing context truncation.

**Returns**: `str`

---

## Sovereign Integration

The `Oracle` class coordinates multiple subsystems to enforce the **Sovereign Mandates**:

1. **PII Shielding (M7/M8)**: Every incoming query in `talk` or `summon` is passed through the `PIIMasker` before being sent to cloud providers.
2. **Local-First Routing (M7)**: The `ModelGateway` is queried using local-first priority.
3. **Resource Guarding (M13)**: Model execution is wrapped in a semaphore to prevent Ryzen 5700U OOM crashes.
4. **Soul Integrity (M11)**: Session closures trigger the `SoulDistillationPipeline` to capture timeless principles.
