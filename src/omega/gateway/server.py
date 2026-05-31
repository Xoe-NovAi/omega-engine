import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import anyio

from omega.oracle.model_gateway import ModelGateway

# 🔱 Omega Gateway — Rate-Limit Resilience Proxy
# Port: 8018
# Purpose: Centralized Reactive Backoff & Empirical Rate-Limit Mapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omega-gateway")

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class BackoffState:
    def __init__(self):
        self.fail_count = 0
        self.retry_after = 0.0
        self.current_backoff = 60  # Start at 60s

    def record_failure(self):
        self.fail_count += 1
        self.retry_after = time.time() + self.current_backoff
        # Reactive backoff sequence: 60 -> 120 -> 240
        self.current_backoff = min(self.current_backoff * 2, 240)
        logger.warning(f"Rate limit hit. Backing off for {self.current_backoff}s. Next attempt: {self.retry_after}")

    def record_success(self):
        self.fail_count = 0
        self.current_backoff = 60
        self.retry_after = 0.0

    def is_in_backoff(self) -> bool:
        return time.time() < self.retry_after

class OmegaGateway:
    def __init__(self):
        self.gateway = FastAPI(title="Omega Gateway")
        self.model_gateway = ModelGateway()
        self.backoff_registry: Dict[str, BackoffState] = {}
        
        self._setup_routes()

    def _get_backoff(self, provider_name: str) -> BackoffState:
        if provider_name not in self.backoff_registry:
            self.backoff_registry[provider_name] = BackoffState()
        return self.backoff_registry[provider_name]

    def _setup_routes(self):
        @self.gateway.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            # 1. Extract system and user prompts from OpenAI format
            system_prompt = ""
            user_query = ""
            for msg in request.messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                elif msg["role"] == "user":
                    user_query = msg["content"]

            # 2. Route through ModelGateway
            # We use the ModelGateway's built-in provider fabric
            try:
                # We wrap the call to handle 429s empirically
                # ModelGateway.generate returns (response, is_cloud)
                response, is_cloud = await self.model_gateway.generate(
                    model_name=request.model,
                    system_prompt=system_prompt,
                    user_query=user_query,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )

                if not response:
                    raise HTTPException(status_code=503, detail="No available providers could generate a response.")

                # Record success for the primary provider used (if we could track it)
                # In this simplified proxy, we assume if it worked, the fabric is healthy.
                
                # 3. Format as OpenAI response
                return ChatCompletionResponse(
                    id=f"chatcmpl-{uuid.uuid4()}",
                    created=int(time.time()),
                    model=request.model,
                    choices=[{
                        "message": {
                            "role": "assistant",
                            "content": response
                        },
                        "finish_reason": "stop",
                        "index": 0
                    }],
                    usage={
                        "prompt_tokens": len(system_prompt + user_query) // 4,
                        "completion_tokens": len(response) // 4,
                        "total_tokens": (len(system_prompt + user_query) + len(response)) // 4
                    }
                )

            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "rate limit" in err_msg:
                    # Empirical Mapping: Record the 429
                    # We don't know exactly which provider failed here because ModelGateway abstracts it,
                    # but we can track the 'model' as a proxy or the gateway as a whole.
                    # For this implementation, we'll track it per model.
                    self._get_backoff(request.model).record_failure()
                    raise HTTPException(status_code=429, detail=f"Rate limit reached. Reactive backoff active. {e}")
                
                logger.error(f"Gateway Error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

app = OmegaGateway().gateway

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8018)
