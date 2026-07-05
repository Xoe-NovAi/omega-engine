# API Reference: Model Gateway

> ModelGateway — abstracts local model inference, auto-detects backends, and enforces local-first priority.

---

## GenerateResult

**File**: `src/omega/oracle/model_gateway.py`

Standardized result returned by a successful model generation call. Enforces the **Response Provenance Mandate (M22)**.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | *Required* | The generated text output. |
| `provider_name` | `str` | *Required* | The actual provider that served the response (e.g., `"native-gguf"`). |
| `is_cloud` | `bool` | *Required* | `True` if the provider is a cloud service, `False` if local. |
| `latency_ms` | `float` | `0.0` | Total latency of the generation call in milliseconds. |
| `model_used` | `Optional[str]` | `None` | The exact model name/ID used for generation. |
| `logprobs` | `Optional[list]` | `None` | Per-token log probabilities (populated if supported by the backend). |

---

## ModelGateway

**File**: `src/omega/oracle/model_gateway.py`

The provider fabric manager. It manages local backends (native-gguf, LM Studio, Ollama) and cloud fallbacks (Google AI Studio, OpenRouter). Enforces Zen 2 optimizations, hardware resource guarding, and provider circuit breakers.

### Constructor

```python
ModelGateway(config_path: Optional[str] = None, health_monitor: Optional[Any] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `Optional[str]` | `None` | Path to `models.yaml`. If `None`, resolves from environment variable `OMEGA_MODELS_CONFIG` or defaults to `config/models.yaml`. |
| `health_monitor` | `Optional[Any]` | `None` | Shared health monitor instance for tracking circuit breaker states. |

---

### Methods

#### `await generate(model_name: str, system_prompt: str, user_query: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None, trace_id: Optional[str] = None) -> GenerateResult`

Executes text generation across the provider fabric. Automatically routes to the highest-priority, healthy provider supporting the requested model.

```python
gateway = ModelGateway()
result = await gateway.generate(
    model_name="qwen3-1.7b",
    system_prompt="You are a helpful assistant.",
    user_query="Hello!",
    temperature=0.7,
    trace_id="trace_12345"
)
print(f"Result: {result.text} (via {result.provider_name})")
```

**Parameters**:
- `model_name`: Name of the model to execute.
- `system_prompt`: System prompt defining the persona.
- `user_query`: User query string.
- `temperature`: Optional temperature override.
- `max_tokens`: Optional max tokens limit.
- `trace_id`: Optional trace ID for observability.

**Returns**: `GenerateResult`

**Raises**:
- `CircuitOpenError`: If all providers for the model are currently tripped.
- `ModelNotFoundError`: If the requested model is not configured.
- `InferenceError` (or subclass): On generation failure.

#### `list_providers() -> List[Dict[str, Any]]`

Lists all configured providers in priority order.

**Returns**: `List[Dict[str, Any]]`

#### `list_models() -> List[Dict[str, Any]]`

Lists all configured models and their specifications.

**Returns**: `List[Dict[str, Any]]`

#### `async def detect_backends() -> Dict[str, bool]`

Probes local network ports to detect which backends are active (e.g., LM Studio on `:1234`, Ollama on `:11434`, llama.cpp on `:8080`).

```python
backends = await gateway.detect_backends()
# backends = {"lmster": True, "ollama": False, "native-gguf": True}
```

**Returns**: `Dict[str, bool]`

#### `async def get_preferred_backend() -> str`

Returns the highest-priority active local backend.

**Returns**: `str`

#### `async def embed(text: str) -> List[float]`

Generates semantic vector embeddings for the given text using the preferred local embedding provider.

```python
vector = await gateway.embed("Hello, world!")
# vector = [0.123, -0.456, ...]
```

**Returns**: `List[float]` (vector array)

#### `async def check_health() -> Dict[str, Any]`

Performs health checks across all providers and returns a status dictionary.

**Returns**: `Dict[str, Any]`

---

## Zen 2 and Hardware Optimizations

The `ModelGateway` leverages the `Zen2Optimizer` and `ResourceGuard` to optimize inference on the Ryzen 7 5700U:

1. **Resource Guarding (OOM Protection)**: Every direct-inference call (e.g., NativeGGUF) is wrapped in `self.resource_guard.acquire()` to ensure only one heavy model executes at a time, preventing memory thrashing on 12Gi RAM.
2. **KV Cache Quantization**: Automatically retrieves optimized KV cache flags (`-ctk q8_0 -ctv q8_0`) per model to reduce memory bottlenecks.
3. **Adaptive Threading**: Allocates `LLAMA_CPP_N_THREADS=4` for small models (1.7B) and `8` for large models (8B) to prevent CPU core thrashing.

---

## id Software Heritage Patterns

### Fixed-Size Active Set `[id-soft: doom-1993]`
Configured providers are split into `_local_active` and `_cloud_active` sets, capped at 32 entries total (`MAXVISPLANES = 32`). This allows $O(1)$ visibility culling before execution — dead or degraded providers are culled instantly, preventing slow timeouts.
