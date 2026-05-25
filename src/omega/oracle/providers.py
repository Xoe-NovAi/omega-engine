import logging
import httpx
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for all inference providers."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (handles Gemini and Gemma models)."""
    async def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY"))

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
        api_key = os.environ.get("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url, 
                json=payload, 
                headers={"x-goog-api-key": api_key}
            )
            response.raise_for_status()
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                return None

class LocallmsterProvider(BaseProvider):
    """LM Studio headless server provider."""
    async def is_available(self) -> bool:
        url = self.config.get("endpoint", "http://127.0.0.1:1234")
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{url}/v1/models")
                return r.status_code == 200
        except Exception:
            return False

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
        url = self.config.get("endpoint", "http://127.0.0.1:1234")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{url}/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "").strip()
            reasoning = message.get("reasoning_content", "").strip()
            return f"{reasoning}\n\n{content}".strip() if reasoning else content

class OllamaProvider(BaseProvider):
    """Ollama local provider."""
    async def is_available(self) -> bool:
        url = self.config.get("endpoint", "http://127.0.0.1:11434")
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
        url = self.config.get("endpoint", "http://127.0.0.1:11434")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{url}/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "").strip()
            reasoning = message.get("reasoning_content", "").strip()
            return f"{reasoning}\n\n{content}".strip() if reasoning else content

class MockProvider(BaseProvider):
    """Offline mock provider — last resort when no inference backend is available."""

    async def is_available(self) -> bool:
        return True

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
        return (
            f"Omega Engine is running in setup mode.\n\n"
            f"No inference backend responded. To enable AI responses:\n"
            f"  1. Set OPENROUTER_API_KEY in your environment (fastest — cloud)\n"
            f"     → `export OPENROUTER_API_KEY='your-key'` or add to .env\n"
            f"  2. Start Ollama with a local model (local — already running):\n"
            f"     → `ollama pull qwen3:1.7b`\n"
            f"  3. Start LM Studio (local — already installed):\n"
            f"     → `lms server start`\n\n"
            f"Quick start: https://github.com/Xoe-NovAi/omega-engine#quickstart"
        )

class NativeGGUFProvider(BaseProvider):
    """Native GGUF provider using llama-cpp-python with Zen 2 optimizations."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.model_path = config.get("model_path")
        # Ensure model path is absolute if it starts with ~/
        if self.model_path and self.model_path.startswith("~"):
            self.model_path = os.path.expanduser(self.model_path)
        self.n_threads = int(os.getenv("OMP_NUM_THREADS", "6"))
        self.llm = None

    async def is_available(self) -> bool:
        """Check if llama-cpp-python is installed and model path exists."""
        if not self.model_path or not os.path.exists(self.model_path):
            return False
        try:
            import llama_cpp  # noqa: F401
            return True
        except ImportError:
            return False

    async def _ensure_loaded(self):
        """Lazy load the model into memory."""
        if self.llm is not None:
            return

        from llama_cpp import Llama
        import anyio
        
        logger.info(f"Loading native GGUF model: {self.model_path} (Threads: {self.n_threads})")
        
        # Zen 2 Optimizations:
        # - n_threads: Pinned to physical cores
        # - type_k/type_v: q8_0 for context efficiency
        # - n_ctx: hardware dependent
        # Using anyio.to_thread to avoid blocking while loading
        def _load():
            return Llama(
                model_path=self.model_path,
                n_threads=self.n_threads,
                n_ctx=self.config.get("n_ctx", 4096),
                type_k=8, # q8_0
                type_v=8, # q8_0
                verbose=False,
                n_gpu_layers=0 # Force CPU on 5700U for stability
            )
        
        self.llm = await anyio.to_thread.run_sync(_load)

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """Perform local inference."""
        import anyio
        await self._ensure_loaded()
        
        # Format prompt (Generic ChatML-style)
        prompt = f"<|system|>{system_prompt}</s><|user|>{user_query}</s><|assistant|>"
        
        try:
            # Run in a thread pool to avoid blocking anyio event loop
            response = await anyio.to_thread.run_sync(
                lambda: self.llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["</s>", "User:", "\n\n"],
                    echo=False
                )
            )
            
            if response and "choices" in response:
                return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Native inference failed: {e}")
        
        return None
