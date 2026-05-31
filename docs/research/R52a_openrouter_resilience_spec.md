# 🔱 Omega Engine — OpenRouter Resilience Spec
**AP Token**: `AP-OR-RESILIENCE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R-52a

## 1. Overview
This specification defines the resilience layer for the OpenRouter provider within the Omega Engine. The goal is to eliminate transient failures, optimize for latency/throughput via provider pinning, and ensure high availability through health-based API key rotation.

## 2. Error Classification & Handling Matrix

| HTTP Code | Body Pattern | Classification | Action | Strategy |
|---|---|---|---|---|
| **429** | "OpenRouter rate limit" | OR-Limit | **Retry** | Exponential Backoff + Key Rotation |
| **429** | "provider returned error" | Upstream-Limit | **Switch** | Immediate Provider Switch / Fallback Model |
| **502/503/504** | Any | Transient | **Retry** | Exponential Backoff + Jitter |
| **500** | "server_error" | Internal | **Retry** | Limited Retries $\rightarrow$ Fallback |
| **400/401/404** | Any | Fatal | **Fail** | Log Error $\rightarrow$ Raise Exception |

## 3. Retry Strategy (Tenacity + AnyIO)

We use `tenacity` for its declarative retry logic, integrated with `anyio` for non-blocking sleeps.

### Implementation Pattern
```python
import anyio
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential_jitter, 
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger("omega.resilience")

class OpenRouterTransientError(Exception):
    """Exception for errors that should trigger a retry."""
    pass

class OpenRouterFatalError(Exception):
    """Exception for errors that should fail immediately."""
    pass

# Retry configuration: 
# - Start at 1s, max 10s, exponential growth
# - Max 5 attempts
# - Jitter to prevent thundering herd
openrouter_retry_policy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(OpenRouterTransientError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

@openrouter_retry_policy
async def call_openrouter_with_resilience(payload, api_key):
    async with anyio.create_task_group() as tg:
        # Implementation of the actual HTTP call (e.g., using httpx)
        # If response.status == 429 and "provider returned error" in body:
        #     raise OpenRouterFatalError("Upstream limit reached")
        # If response.status in [429, 502, 503, 504]:
        #     raise OpenRouterTransientError(f"Transient error: {response.status}")
        pass
```

## 4. Provider Routing & Pinning

OpenRouter allows steering requests to specific providers via the `provider` object in the request body.

### Request Body Integration
```json
{
  "model": "deepseek/deepseek-chat",
  "messages": [...],
  "provider": {
    "order": ["DeepInfra", "Together", "Novita"],
    "sort": "latency",
    "allow": ["DeepInfra"],
    "avoid": ["SomeUnstableProvider"]
  }
}
```

### `providers.yaml` Schema Extension
We extend the provider configuration to allow per-model routing preferences.

```yaml
providers:
  openrouter:
    api_key_env: GOOGLE_API_KEY # Root .env
    routing_defaults:
      sort: "latency" # Global default
    model_overrides:
      "deepseek/deepseek-chat":
        order: ["DeepInfra", "Together"]
        sort: "throughput"
        fallbacks: ["google/gemma-4-31b-it", "openai/gpt-4o-mini"]
      "meta-llama/llama-3.1-405b":
        order: ["SambaNova"]
        sort: "latency"
```

## 5. Health-Based API Key Rotation

To maximize throughput and avoid 429s, we implement a Redis-backed key rotator.

### Logic
1. **Storage**: Store keys in a Redis Set `omega:keys:openrouter`.
2. **Health Tracking**: Maintain a hash `omega:keys:health` where field = `key_id` and value = `failure_count`.
3. **Selection**:
   - Select key with the lowest `failure_count`.
   - If multiple keys have 0 failures, use round-robin.
4. **Penalty**:
   - On 429 (OR-Limit) $\rightarrow$ Increment `failure_count` by 10.
   - On 5xx $\rightarrow$ Increment `failure_count` by 2.
   - On Success $\rightarrow$ Decrement `failure_count` by 1 (min 0).
5. **TTL**: Failure counts expire after 3600s to allow keys to "recover."

### Key Rotator Class
```python
import redis.asyncio as redis

class OpenRouterKeyRotator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.health_key = "omega:keys:health"
        self.keys_set = "omega:keys:openrouter"

    async def get_best_key(self) -> str:
        keys = await self.redis.smembers(self.keys_set)
        if not keys:
            raise Exception("No API keys configured for OpenRouter")
        
        # Fetch all health scores
        scores = await self.redis.hgetall(self.health_key)
        
        # Sort keys by health score (lowest first)
        sorted_keys = sorted(
            [k.decode() for k in keys], 
            key=lambda k: int(scores.get(k.encode(), 0))
        )
        return sorted_keys[0]

    async def report_failure(self, key: str, penalty: int = 1):
        await self.redis.hincrby(self.health_key, key, penalty)
        # Set TTL for the health score to allow recovery
        await self.redis.expire(self.health_key, 3600)

    async def report_success(self, key: str):
        current = await self.redis.hget(self.health_key, key)
        if current and int(current) > 0:
            await self.redis.hincrby(self.health_key, key, -1)
```

## 6. Implementation Roadmap for MiniMax M2.5

1. **Phase 1**: Implement `OpenRouterKeyRotator` and integrate with `ModelGateway`.
2. **Phase 2**: Implement `openrouter_retry_policy` wrapper around the HTTP client.
3. **Phase 3**: Update `providers.yaml` parser to inject the `provider` object into requests based on `model_overrides`.
4. **Phase 4**: Add integration tests simulating 429s and 502s to verify rotation and backoff.
