import logging
import httpx
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Lazy import for cpu_optimizer (avoids circular imports at module load time)
_cpu_optimizer = None

def _get_cpu_optimizer():
    """Lazy-load Zen2Optimizer to avoid circular imports."""
    global _cpu_optimizer
    if _cpu_optimizer is None:
        from .cpu_optimizer import Zen2Optimizer
        _cpu_optimizer = Zen2Optimizer()
    return _cpu_optimizer

class BaseProvider(ABC):
    """Base class for all inference providers."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (handles Gemini and Gemma models)."""
    async def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY"))

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
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

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
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

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
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

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
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
    """Native GGUF provider using llama-cpp-python with full Zen 2 optimizations.

    This is the Omega Engine's local-first inference backend. It runs GGUF models
    directly via llama-cpp-python with CPU pinning, KV cache quantization, and
    memory-aware context sizing.

    Zen 2 optimizations applied:
      - CPU affinity pinned to physical cores [0,2,4,6]
      - OMP_NUM_THREADS=6, OMP_PROC_BIND=close, OMP_PLACES=cores
      - KV cache q8_0 (50% memory vs f16, negligible quality loss)
      - Thread count scaled to model size (4 for <1B, 6 otherwise)
      - Batch sizes tuned to L2 cache (512KB/core)
      - Memory pressure monitoring before model load
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.model_path = config.get("model_path")
        if self.model_path and self.model_path.startswith("~"):
            self.model_path = os.path.expanduser(self.model_path)

        # Zen 2 core configuration
        self._cores = config.get("cores", [0, 2, 4, 6])
        self._n_threads = config.get("n_threads", 6)
        self._n_threads_batch = config.get("n_threads_batch", 6)

        # Context configuration
        self._n_ctx = config.get("n_ctx", 4096)
        self._n_ctx_max = config.get("n_ctx_max", 32768)
        self._ctx_overflow = config.get("ctx_overflow", "rolling_window")

        # KV cache configuration
        self._type_k = config.get("type_k", 8)  # 8 = q8_0
        self._type_v = config.get("type_v", 8)  # 8 = q8_0

        # Batch configuration (tuned for Zen 2 L2 cache: 512KB/core)
        self._n_batch = config.get("n_batch", 512)
        self._n_ubatch = config.get("n_ubatch", 32)

        # Memory management
        self._use_mmap = config.get("use_mmap", True)
        self._use_mlock = config.get("use_mlock", False)
        self._n_gpu_layers = config.get("n_gpu_layers", 0)

        # State
        self.llm = None
        self._loaded_ctx = 0
        self._loaded_model = None
        self._affinity_applied = False

    async def is_available(self) -> bool:
        """Check if llama-cpp-python is installed and model path exists."""
        if not self.model_path or not os.path.exists(self.model_path):
            return False
        try:
            import llama_cpp  # noqa: F401
            return True
        except ImportError:
            return False

    def _apply_cpu_affinity(self) -> Dict[str, Any]:
        """Pin this process to physical cores for optimal inference.

        Returns affinity result dict.
        """
        if self._affinity_applied:
            return {"success": True, "already_pinned": True}

        try:
            optimizer = _get_cpu_optimizer()
            result = optimizer.enforce_affinity(self._cores)
            self._affinity_applied = result.get("success", False)
            return result
        except Exception as e:
            logger.warning(f"CPU affinity enforcement failed (non-fatal): {e}")
            return {"success": False, "error": str(e)}

    def _estimate_context_memory(self, n_ctx: int) -> Dict[str, float]:
        """Estimate RAM needed for model + KV cache at given context length.

        Returns dict with model_mb, kv_cache_mb, total_mb, fits_in_ram.
        """
        try:
            from .cpu_optimizer import RAM_AVAILABLE_AI_MB, RAM_NOVA_RESIDENT_MB

            # Estimate model size from file
            model_size_mb = 0
            if self.model_path and os.path.exists(self.model_path):
                model_size_mb = os.path.getsize(self.model_path) / (1024 * 1024)

            # KV cache estimation for q8_0
            # Per-token: ~2 bytes key + ~2 bytes value per layer (simplified)
            # Conservative: ~2MB per 1K tokens for a 4B model at q8_0
            kv_per_1k_tokens_mb = 2.0
            kv_cache_mb = (n_ctx / 1000) * kv_per_1k_tokens_mb

            total_mb = model_size_mb + kv_cache_mb + RAM_NOVA_RESIDENT_MB
            fits = total_mb < RAM_AVAILABLE_AI_MB

            return {
                "model_mb": round(model_size_mb, 0),
                "kv_cache_mb": round(kv_cache_mb, 0),
                "total_mb": round(total_mb, 0),
                "available_mb": RAM_AVAILABLE_AI_MB,
                "fits_in_ram": fits,
                "headroom_mb": round(RAM_AVAILABLE_AI_MB - total_mb, 0),
            }
        except Exception:
            return {"model_mb": 0, "kv_cache_mb": 0, "total_mb": 0, "fits_in_ram": True}

    def _select_optimal_context(self, requested_ctx: Optional[int] = None) -> int:
        """Select optimal context length based on memory pressure.

        If requested_ctx is provided, use it (if it fits). Otherwise, pick
        the largest context that leaves adequate headroom.
        """
        if requested_ctx:
            est = self._estimate_context_memory(requested_ctx)
            if est.get("fits_in_ram", False):
                return min(requested_ctx, self._n_ctx_max)
            logger.warning(
                f"Requested context {requested_ctx} may not fit "
                f"(est {est.get('total_mb', 0)}MB, available {est.get('available_mb', 0)}MB)"
            )

        # Auto-select: try 32K, then 16K, then 8K, then 4K
        for ctx in [32768, 16384, 8192, 4096]:
            est = self._estimate_context_memory(ctx)
            if est.get("fits_in_ram", False):
                logger.info(f"Auto-selected context: {ctx} tokens (est {est.get('total_mb', 0)}MB)")
                return ctx

        return 4096  # Minimum safe context

    async def _ensure_loaded(self, n_ctx: Optional[int] = None):
        """Load or reload the model with optimal Zen 2 settings.

        Applies CPU pinning, selects context size, and configures KV cache.
        """
        target_ctx = self._select_optimal_context(n_ctx)

        # Skip reload if same model and context already loaded
        if self.llm is not None and self._loaded_model == self.model_path and self._loaded_ctx >= target_ctx:
            return

        # Apply CPU affinity before loading
        affinity_result = self._apply_cpu_affinity()
        if affinity_result.get("success"):
            logger.info(f"CPU affinity applied: cores {self._cores}")

        from llama_cpp import Llama
        import anyio

        # Determine thread count based on model (tiny models need fewer threads)
        threads = 4 if "0.6b" in (self.model_path or "").lower() else self._n_threads

        logger.info(
            f"Loading GGUF model: {self.model_path}\n"
            f"  Context: {target_ctx} tokens\n"
            f"  Threads: {threads} (physical cores: {self._cores})\n"
            f"  KV cache: k={self._type_k} v={self._type_v}\n"
            f"  Batch: {self._n_batch}/{self._n_ubatch}\n"
            f"  mmap: {self._use_mmap}, mlock: {self._use_mlock}"
        )

        def _load():
            return Llama(
                model_path=self.model_path,
                n_threads=threads,
                n_threads_batch=self._n_threads_batch,
                n_ctx=target_ctx,
                n_batch=self._n_batch,
                n_ubatch=self._n_ubatch,
                type_k=self._type_k,
                type_v=self._type_v,
                use_mmap=self._use_mmap,
                use_mlock=self._use_mlock,
                n_gpu_layers=self._n_gpu_layers,
                verbose=False,
            )

        self.llm = await anyio.to_thread.run_sync(_load)
        self._loaded_ctx = target_ctx
        self._loaded_model = self.model_path
        logger.info(f"Model loaded: {target_ctx} context, {threads} threads")

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        trace_id: Optional[str] = None,
        n_ctx: Optional[int] = None,
    ) -> Optional[str]:
        """Perform local inference with Zen 2 optimizations.

        Args:
            model: Model identifier (used for logging).
            system_prompt: System prompt text.
            user_query: User query text.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            trace_id: Observability trace ID.
            n_ctx: Optional context length override. If None, auto-selects.

        Returns:
            Generated text or None on failure.
        """
        import anyio
        await self._ensure_loaded(n_ctx)

        # Format prompt (ChatML-style for most GGUF models)
        prompt = f"<|system|>{system_prompt}</s><|user|>{user_query}</s><|assistant|>"

        try:
            response = await anyio.to_thread.run_sync(
                lambda: self.llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["</s>", "User:", "\n\n"],
                    echo=False,
                )
            )

            if response and "choices" in response:
                return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Native GGUF inference failed: {e}")
            # Reset model state on error to force reload
            self.llm = None
            self._loaded_ctx = 0

        return None

    async def reload_with_context(self, n_ctx: int) -> bool:
        """Explicitly reload the model with a new context length.

        Useful for dynamic context management — call this when a conversation
        needs more context than currently allocated.

        Returns:
            True if reload succeeded.
        """
        old_ctx = self._loaded_ctx
        try:
            self.llm = None  # Force unload
            await self._ensure_loaded(n_ctx)
            logger.info(f"Context reloaded: {old_ctx} -> {self._loaded_ctx}")
            return True
        except Exception as e:
            logger.error(f"Context reload failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current provider status for observability."""
        return {
            "provider": self.name,
            "model_path": self.model_path,
            "loaded": self.llm is not None,
            "loaded_context": self._loaded_ctx,
            "cores": self._cores,
            "threads": self._n_threads,
            "kv_cache": f"k={self._type_k},v={self._type_v}",
            "affinity_applied": self._affinity_applied,
        }
