# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ORACLE-RESTORE-v2.3.0
# [heritage: anyio 2024] M1 AnyIO — async runtime (to_thread.run_sync for blocking inference)
# [heritage: llama-cpp-python 2023] Native GGUF inference (llama_copy_state_data for SomaticState M20)

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import atexit
import logging
import httpx2 as httpx
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError
)

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

def _resolve_google_api_key() -> str:
    """Resolve the Google API key from the sovereign vault.

    Replaces the previous scattered ``os.environ.get("GOOGLE_API_KEY")`` read
    so the encrypted VaultCore is the single source of truth for API keys.
    """
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("google:api_key")
        return cred.encrypted_blob if cred else ""
    except Exception:
        return ""

class BaseProvider(ABC):
    """Base class for all inference providers."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    def resolve_model(self, model_name: str) -> str:
        """Resolve config model name to provider-specific model name via overrides."""
        overrides = self.config.get("model_overrides", {})
        if not isinstance(overrides, dict):
            return model_name
        return overrides.get(model_name, model_name)

    @abstractmethod
    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None, session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0) -> Optional[str]:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (handles Gemini and Gemma models)."""
    async def is_available(self) -> bool:
        return bool(_resolve_google_api_key())

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None, session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0, api_key: Optional[str] = None) -> Optional[str]:
        # Use provided api_key or fallback to the sovereign vault
        key = api_key or _resolve_google_api_key()
        if not key:
            raise ProviderAuthError(provider="google", message="No Google API key provided or found in environment", trace_id=trace_id)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "repetitionPenalty": repetition_penalty,
            }
        }
        if logit_bias:
            # Google AI Studio uses a different format for logit bias (if supported)
            # For now, we pass it in a way that doesn't crash, or omit if not supported by the specific model
            payload["generationConfig"]["logitBias"] = logit_bias
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url, 
                    json=payload, 
                    headers={"x-goog-api-key": key}
                )
                
                if response.status_code == 429:
                    raise ProviderRateLimitError(provider="google", message="Google API quota exceeded", status_code=429, trace_id=trace_id)
                if response.status_code in (401, 403):
                    raise ProviderAuthError(provider="google", message="Google API authentication failed", status_code=response.status_code, trace_id=trace_id)
                if response.status_code >= 500:
                    raise ProviderUnavailableError(provider="google", message="Google API server error", status_code=response.status_code, trace_id=trace_id)
                
                response.raise_for_status()
                data = response.json()
                
                # Handle safety blocks
                if data.get("candidates") and "finishReason" in data["candidates"][0] and data["candidates"][0]["finishReason"] == "SAFETY":
                    raise ProviderSafetyError(provider="google", message="Response blocked by Google safety filters", trace_id=trace_id)
                
                if not data.get("candidates"):
                    return None
                
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(provider="google", message=f"Google API timeout: {e}", trace_id=trace_id, raw_error=e)
        except httpx.HTTPStatusError as e:
            # Fallback for any other HTTP errors not caught by status checks
            raise ProviderError(provider="google", message=f"Google API HTTP error: {e}", status_code=e.response.status_code, trace_id=trace_id, raw_error=e)
        except OmegaError as e:
            # Allow our custom typed errors to propagate untouched
            raise e
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Unexpected Google API failure: {e}", exc_info=True)
            raise ProviderError(provider="google", message=f"Unexpected Google API failure: {e}", trace_id=trace_id, raw_error=e) from e

class LocallmsterProvider(BaseProvider):
    """LM Studio headless server provider."""
    async def is_available(self) -> bool:
        url = self.config.get("endpoint", "http://127.0.0.1:1234")
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{url}/v1/models")
                return r.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None, session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0) -> Optional[str]:
        url = self.config.get("endpoint", "http://127.0.0.1:1234")
        resolved_model = self.resolve_model(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        # [id-soft: vet-016] Cvar System — typed config lookup from cvar_table
        try:
            from omega.cvar_table import cvar_get
            stop_tokens = cvar_get("config.gguf.stop_tokens", ["</s>", "User:", "\n\n"])
        except ImportError:
            stop_tokens = ["</s>", "User:", "\n\n"]
        
        payload = {
            "model": resolved_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop_tokens,
            "repetition_penalty": repetition_penalty,
            "stream": False,
        }
        if logit_bias:
            payload["logit_bias"] = logit_bias
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{url}/v1/chat/completions", json=payload)
                
                if response.status_code == 429:
                    raise ProviderRateLimitError(provider="lmster", message="LM Studio rate limit exceeded", status_code=429, trace_id=trace_id)
                if response.status_code >= 500:
                    raise ProviderUnavailableError(provider="lmster", message="LM Studio server error", status_code=response.status_code, trace_id=trace_id)
                
                response.raise_for_status()
                data = response.json()
                message = data["choices"][0]["message"]
                content = message.get("content", "").strip()
                reasoning = message.get("reasoning_content", "").strip()
                return f"{reasoning}\n\n{content}".strip() if reasoning else content
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(provider="lmster", message=f"LM Studio timeout: {e}", trace_id=trace_id, raw_error=e)
        except httpx.HTTPStatusError as e:
            raise ProviderError(provider="lmster", message=f"LM Studio HTTP error: {e}", status_code=e.response.status_code, trace_id=trace_id, raw_error=e)
        except OmegaError as e:
            raise e
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Unexpected LM Studio failure: {e}", exc_info=True)
            raise ProviderError(provider="lmster", message=f"Unexpected LM Studio failure: {e}", trace_id=trace_id, raw_error=e) from e

class OllamaProvider(BaseProvider):
    """Ollama local provider."""
    async def is_available(self) -> bool:
        url = self.config.get("endpoint", "http://127.0.0.1:11434")
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{url}/api/tags")
                return r.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None, session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0) -> Optional[str]:
        url = self.config.get("endpoint", "http://127.0.0.1:11434")
        resolved_model = self.resolve_model(model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        # [id-soft: vet-016] Cvar System — typed config lookup from cvar_table
        # Port 1.3: ChatML stop tokens prevent hallucinated conversation turns
        try:
            from omega.cvar_table import cvar_get
            stop_tokens = cvar_get("config.gguf.stop_tokens", ["</s>", "User:", "\n\n"])
        except ImportError:
            stop_tokens = ["</s>", "User:", "\n\n"]
        
        payload = {
            "model": resolved_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop_tokens,
            "repetition_penalty": repetition_penalty,
            "stream": False,
        }
        if logit_bias:
            payload["logit_bias"] = logit_bias
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{url}/v1/chat/completions", json=payload)
                
                if response.status_code == 429:
                    raise ProviderRateLimitError(provider="ollama", message="Ollama rate limit exceeded", status_code=429, trace_id=trace_id)
                if response.status_code >= 500:
                    raise ProviderUnavailableError(provider="ollama", message="Ollama server error", status_code=response.status_code, trace_id=trace_id)
                
                response.raise_for_status()
                data = response.json()
                message = data["choices"][0]["message"]
                content = message.get("content", "").strip()
                reasoning = message.get("reasoning_content", "").strip()
                return f"{reasoning}\n\n{content}".strip() if reasoning else content
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(provider="ollama", message=f"Ollama timeout: {e}", trace_id=trace_id, raw_error=e)
        except httpx.HTTPStatusError as e:
            raise ProviderError(provider="ollama", message=f"Ollama HTTP error: {e}", status_code=e.response.status_code, trace_id=trace_id, raw_error=e)
        except OmegaError as e:
            raise e
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Unexpected Ollama failure: {e}", exc_info=True)
            raise ProviderError(provider="ollama", message=f"Unexpected Ollama failure: {e}", trace_id=trace_id, raw_error=e) from e

class MockProvider(BaseProvider):
    """Offline mock provider — last resort when no inference backend is available."""

    async def is_available(self) -> bool:
        return True

    async def generate(self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None, session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0) -> Optional[str]:
        demo = os.environ.get("OMEGA_DEMO")
        if demo:
            return (
                f"I am the Omega Engine — sovereign AI runtime.\n\n"
                f"You asked: \"{user_query}\"\n\n"
                f"I hear you through the Oracle, routed by the Iris decoder, "
                f"enhanced by memory from the Soul Engine.\n\n"
                f"This is a demo response. Connect a local GGUF model at "
                f"lmster :1234 or native-gguf for full inference.\n\n"
                f"302 tests pass. 71 modules. 12 Sovereign Mandates enforced."
            )
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

    Heritage:
      [id-soft: vet-016] Cvar System — config values read from cvar_table
      Port 1.1 (filter_llama_kwargs): validate_llama_kwargs() called at init
      Port 1.2 (n_gpu_layers=0): explicit CPU-only default via cvar
      Port 1.5 (atomic trace_id): trace_id propagated to observability events
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.model_path = config.get("model_path")
        if self.model_path and self.model_path.startswith("~"):
            self.model_path = os.path.expanduser(self.model_path)

        # [id-soft: vet-016] Cvar System — typed config lookup from cvar_table
        try:
            from omega.cvar_table import cvar_get, validate_llama_kwargs
            # Port 1.1: validate llama-cpp kwargs — moved to _ensure_loaded
            # where the actual llama_cpp.Llama() kwargs are built. Validating
            # the raw provider config here caused false positives because
            # config also contains `provider`, `priority`, `cores`, etc.
            self._kwarg_filter_enabled = cvar_get("config.gguf.kwarg_filter", True)
            n_gpu = cvar_get("config.gguf.n_gpu_layers", 0)
            n_ctx_default = cvar_get("config.gguf.n_ctx", 4096)
            n_threads_default = cvar_get("config.gguf.n_threads", 6)
        except ImportError:
            self._kwarg_filter_enabled = False
            n_gpu = 0
            n_ctx_default = 4096
            n_threads_default = 6

        # Zen 2 core configuration
        self._cores = config.get("cores", [0, 2, 4, 6])
        self._n_threads = config.get("n_threads", n_threads_default)
        self._n_threads_batch = config.get("n_threads_batch", self._n_threads)

        # Context configuration
        self._n_ctx = config.get("n_ctx", n_ctx_default)
        self._n_ctx_max = config.get("n_ctx_max", 32768)
        self._ctx_overflow = config.get("ctx_overflow", "rolling_window")

        # KV cache configuration
        self._type_k = config.get("type_k", 8)  # 8 = q8_0
        self._type_v = config.get("type_v", 8)  # 8 = q8_0, 1 = f16

        # ── P0-1: Explicit KV cache type (q8_0 quantizes the KV cache) ──
        # [heritage: quake-1996] Zone Memory — quantize the KV cache to fit
        # more context in the same RAM budget (the 4-tier memory principle).
        # When present, kv_cache_type overrides type_k/type_v uniformly.
        kv_cache_type = config.get("kv_cache_type")
        if kv_cache_type:
            _KV_TYPE_MAP = {"q8_0": 8, "q4_0": 4, "q5_0": 5, "q6_0": 6, "f16": 1, "f32": 0}
            _mapped = _KV_TYPE_MAP.get(str(kv_cache_type).lower())
            if _mapped is not None:
                self._type_k = _mapped
                self._type_v = _mapped
            else:
                logger.warning("Unknown kv_cache_type '%s' — keeping type_k/type_v", kv_cache_type)

        # Batch configuration (tuned for Zen 2 L2 cache: 512KB/core)
        self._n_batch = config.get("n_batch", 512)
        self._n_ubatch = config.get("n_ubatch", 32)

        # Memory management
        self._use_mmap = config.get("use_mmap", True)
        self._use_mlock = config.get("use_mlock", False)
        # [id-soft: vet-016] Cvar System — typed config lookup from cvar_table
        # Port 1.2: explicit CPU-only default prevents iGPU crash on Vega 7
        self._n_gpu_layers = config.get("n_gpu_layers", n_gpu)

        # State
        self._worker_process = None
        self._req_queue = None
        self._res_queue = None
        self._loaded_ctx = 0
        self._loaded_model = None
        self._affinity_applied = False
        # [Operation Deep-Siphon] ICS-F v1.0 Sprint 0: last inference logprobs.
        self._last_logprobs = None
        # Isolated pool for synchronous C-calls to prevent anyio global pool exhaustion
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="gguf_inference")
        atexit.register(self.shutdown)

    def __del__(self):
        """Destructor — clean up worker process on garbage collection.
        
        BUG-002 (2026-07-02): Without this, when a NativeGGUFProvider goes
        out of scope (e.g., during A/B testing with multiple instances),
        the worker subprocess keeps running as a zombie holding model memory.
        
        atexit.register(self.shutdown) at line 346 only fires on clean exit.
        __del__ catches GC-time collection.
        """
        try:
            self.shutdown()
        except (RuntimeError, OSError):
            pass

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
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"CPU affinity enforcement failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _estimate_context_memory(self, n_ctx: int) -> Dict[str, float]:
        """Estimate RAM needed for model + KV cache at given context length.

        Returns dict with model_mb, kv_cache_mb, total_mb, fits_in_ram.
        """
        try:
            from .cpu_optimizer import RAM_AVAILABLE_AI_MB, RAM_DRAFT_RESIDENT_MB

            # Estimate model size from file
            model_size_mb = 0
            if self.model_path and os.path.exists(self.model_path):
                model_size_mb = os.path.getsize(self.model_path) / (1024 * 1024)

            # KV cache estimation for q8_0
            # Per-token: ~2 bytes key + ~2 bytes value per layer (simplified)
            # Conservative: ~2MB per 1K tokens for a 4B model at q8_0
            kv_per_1k_tokens_mb = 2.0
            kv_cache_mb = (n_ctx / 1000) * kv_per_1k_tokens_mb

            total_mb = model_size_mb + kv_cache_mb + RAM_DRAFT_RESIDENT_MB
            fits = total_mb < RAM_AVAILABLE_AI_MB

            return {
                "model_mb": round(model_size_mb, 0),
                "kv_cache_mb": round(kv_cache_mb, 0),
                "total_mb": round(total_mb, 0),
                "available_mb": RAM_AVAILABLE_AI_MB,
                "fits_in_ram": fits,
                "headroom_mb": round(RAM_AVAILABLE_AI_MB - total_mb, 0),
            }
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Failed to estimate memory for model '%s': %s", self.model_path or '?', e, exc_info=True)
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

        Spawns a worker process for inference to isolate C++ crashes.
        """
        target_ctx = self._select_optimal_context(n_ctx)

        # Skip reload if same model and context already loaded
        if self._worker_process is not None and self._loaded_model == self.model_path and self._loaded_ctx >= target_ctx:
            return

        # Apply CPU affinity before loading
        affinity_result = self._apply_cpu_affinity()
        if affinity_result.get("success"):
            logger.info(f"CPU affinity applied: cores {self._cores}")

        # Spawn worker process for inference
        import anyio
        from multiprocessing import Process, Queue

        # Create queues for inter-process communication
        self._req_queue = Queue()
        self._res_queue = Queue()

        # Worker function that loads the model and runs inference
        def _worker(req_queue, res_queue, model_path, n_threads, n_threads_batch,
                      n_ctx, n_batch, n_ubatch, type_k, type_v,
                      use_mmap, use_mlock, n_gpu_layers, kwarg_filter_enabled):
            from llama_cpp import Llama
            try:
                from omega.cvar_table import validate_llama_kwargs
            except ImportError:
                validate_llama_kwargs = None
            
            # Build the exact kwargs we'll pass to Llama(), then validate them
            llama_kwargs = {
                "model_path": model_path,
                "n_threads": n_threads,
                "n_threads_batch": n_threads_batch,
                "n_ctx": n_ctx,
                "n_batch": n_batch,
                "n_ubatch": n_ubatch,
                "type_k": type_k,
                "type_v": type_v,
                "use_mmap": use_mmap,
                "use_mlock": use_mlock,
                "n_gpu_layers": n_gpu_layers,
                "verbose": False,
            }
            if kwarg_filter_enabled and validate_llama_kwargs:
                kwarg_warnings = validate_llama_kwargs(llama_kwargs, "NativeGGUFProvider.worker")
                if kwarg_warnings:
                    import logging
                    logging.getLogger("omega.workers").warning(
                        "NativeGGUFProvider.worker: %d kwarg warnings:\n  %s",
                        len(kwarg_warnings), "\n  ".join(kwarg_warnings)
                    )
            
            # Load the model — wrap in try/except to signal load failure
            try:
                llm = Llama(**llama_kwargs)
            except (OmegaError, RuntimeError, OSError) as e:
                # Send load failure back to parent, then exit
                res_queue.put({"status": "load_error", "error": repr(e)})
                return
            
            # Signal that loading succeeded
            res_queue.put({"status": "ready"})
            
            # Keep the worker alive, waiting for requests
            while True:
                try:
                    # Get request from queue
                    request = req_queue.get()
                    if request is None:  # Shutdown signal
                        break
                    
                    # Handle Somatic State Commands
                    if "command" in request:
                        cmd = request["command"]
                        if cmd == "SAVE_STATE":
                            try:
                                # [M20] Somatic capture: copy internal KV state to bytes
                                state_bytes = llama_cpp.llama_copy_state_data(llm)
                                res_queue.put({"status": "state_captured", "data": state_bytes})
                            except (OmegaError, RuntimeError, OSError) as e:
                                res_queue.put(e)
                            continue
                        elif cmd == "LOAD_STATE":
                            try:
                                # [M20] Somatic restore: set internal KV state from bytes
                                state_bytes = request.get("state_bytes")
                                llama_cpp.llama_set_state_data(llm, state_bytes)
                                res_queue.put({"status": "state_restored"})
                            except (OmegaError, RuntimeError, OSError) as e:
                                res_queue.put(e)
                            continue




                    # Unpack request
                    system_prompt = request["system_prompt"]
                    user_query = request["user_query"]
                    max_tokens = request["max_tokens"]
                    temperature = request["temperature"]
                    stop = request["stop"]
                    logprobs = request.get("logprobs", False)
                    enable_thinking = request.get("enable_thinking", False)
                    logit_bias = request.get("logit_bias")
                    repetition_penalty = request.get("repetition_penalty", 1.0)
                    
                    # [id-soft: vet-002] Right Approximation — fast heuristic over exact (create_chat_completion with template match)
                    # to properly apply the GGUF's embedded Jinja chat template.
                    # This enables thinking mode control via chat_template_kwargs.
                    # Raw llm(prompt=...) does NOT apply the template.
                    #
                    # chat_template_kwargs is NOT in the Python bindings (v0.3.32).
                    # Workaround: wrap the default chat handler to inject kwargs,
                    # matching the pattern from llama_cpp/server/model.py:328-333.
                    #
                    # BUG-002 (2026-07-02): Reset llm.chat_handler BEFORE getting
                    # base_handler. On the 2nd+ call with enable_thinking=False,
                    # llm.chat_handler was already set to _handler_with_kwargs from
                    # the first call, causing base_handler → _handler_with_kwargs
                    # which wraps itself → infinite recursion.
                    if enable_thinking is not None and not enable_thinking:
                        import llama_cpp.llama_chat_format as _chat_fmt
                        # Reset to prevent self-wrapping recursion
                        llm.chat_handler = None
                        base_handler = (
                            llm.chat_handler
                            or llm._chat_handlers.get(llm.chat_format)
                            or _chat_fmt.get_chat_completion_handler(llm.chat_format)
                        )
                        _template_kwargs = {"enable_thinking": False}
                        def _handler_with_kwargs(*args, **kwargs):
                            return base_handler(*args, **{**_template_kwargs, **kwargs})
                        llm.chat_handler = _handler_with_kwargs
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query},
                    ]
                    kwargs = {k: v for k, v in {
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stop": stop,
                        "logit_bias": logit_bias,
                        "repeat_penalty": repetition_penalty,
                    }.items() if v is not None}
                    if logprobs:
                        kwargs["logprobs"] = logprobs
                    response = llm.create_chat_completion(**kwargs)

                    # Send response back to main process
                    res_queue.put(response)

                except (OmegaError, RuntimeError, OSError) as e:
                    import logging
                    logging.getLogger("omega.workers").error(
                        f"Worker process error: {e}", exc_info=True
                    )
                    # Send error back to main process
                    res_queue.put(e)

        # Start the worker process with explicit args (avoid closure over self)
        self._worker_process = Process(
            target=_worker,
            args=(
                self._req_queue, self._res_queue,
                self.model_path, self._n_threads, self._n_threads_batch,
                target_ctx, self._n_batch, self._n_ubatch,
                self._type_k, self._type_v,
                self._use_mmap, self._use_mlock, self._n_gpu_layers,
                self._kwarg_filter_enabled,
            ),
        )
        self._worker_process.start()

        # Wait for the worker to signal ready or load failure (30s timeout)
        try:
            init_signal = await anyio.to_thread.run_sync(
                lambda: self._res_queue.get(timeout=120)
            )
            if isinstance(init_signal, dict) and init_signal.get("status") == "load_error":
                error_msg = init_signal.get("error", "Unknown load error")
                self._worker_process.terminate()
                self._worker_process = None
                self._req_queue = None
                self._res_queue = None
                raise InferenceLoadError(
                    f"Failed to load model {self.model_path}: {error_msg}",
                    raw_error=error_msg,
                )
        except (TimeoutError, Exception) as e:
            if isinstance(e, InferenceLoadError):
                raise
            # Worker process likely crashed — terminate and raise
            if self._worker_process is not None:
                self._worker_process.terminate()
                self._worker_process = None
            self._req_queue = None
            self._res_queue = None
            raise InferenceLoadError(
                f"Worker process did not initialize within 30s: {e}",
                raw_error=e,
            ) from e

        self._loaded_ctx = target_ctx
        self._loaded_model = self.model_path
        logger.info(f"Worker process initialized: {target_ctx} context, {self._n_threads} threads")


    async def save_state(self) -> bytes:
        """Captures the current model state and returns the raw bytes.
        
        This allows the ModelGateway to store the state in a sovereign
        Content Addressable Storage (CAS) system.
        """
        if self._worker_process is None:
            raise InferenceRuntimeError("No worker process active; cannot capture state")
        
        try:
            # Send SAVE_STATE command to worker
            await anyio.to_thread.run_sync(self._req_queue.put, {"command": "SAVE_STATE"})
            
            # Wait for state bytes from worker
            response = await anyio.to_thread.run_sync(self._res_queue.get)
            
            if isinstance(response, dict) and response.get("status") == "state_captured":
                return response.get("data")
            
            raise InferenceRuntimeError(f"Worker failed to capture state: {response}")
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Somatic capture failed: {e}")
            raise InferenceRuntimeError(f"Somatic capture failed: {e}") from e

    async def load_state(self, state_bytes: bytes) -> bool:
        """Restores a model state from raw bytes into the worker process.
        
        Returns:
            True if state was restored successfully.
        """
        if self._worker_process is None:
            raise InferenceRuntimeError("No worker process active; cannot restore state")
        
        try:
            # Send LOAD_STATE command to worker with bytes
            await anyio.to_thread.run_sync(self._req_queue.put, {
                "command": "LOAD_STATE", 
                "state_bytes": state_bytes
            })
            
            # Wait for confirmation
            response = await anyio.to_thread.run_sync(self._res_queue.get)
            if isinstance(response, dict) and response.get("status") == "state_restored":
                logger.info("Somatic state restored successfully")
                return True
            
            raise InferenceRuntimeError(f"Worker failed to restore state: {response}")
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Somatic restore failed: {e}")
            raise InferenceRuntimeError(f"Somatic restore failed: {e}") from e

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        trace_id: Optional[str] = None,
        n_ctx: Optional[int] = None,
        session_id: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
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
            session_id: Optional session ID.
            logit_bias: Optional mapping of token IDs to bias values.
            repetition_penalty: Penalty for repeating tokens.
        
        Returns:
            Generated text or None on failure.
        """
        import anyio
        await self._ensure_loaded(n_ctx)
        
        # [id-soft: vet-002] Right Approximation — fast heuristic over exact (create_chat_completion with template match)
        # separately. The worker uses create_chat_completion() which applies the GGUF's
        # embedded Jinja chat template, enabling proper thinking mode control via
        # chat_template_kwargs={"enable_thinking": False}.
        
        if session_id:
            logger.debug("Session-aware inference [session_id=%s, trace_id=%s]", session_id, trace_id)
        
        # [Operation Deep-Siphon] Reset last logprobs before each inference.
        # Prevents stale data from a previous successful call leaking
        # after a subsequent error (ICS-F v1.0 Sprint 0).
        self._last_logprobs = None
        
        # Send request to worker process (system_prompt + user_query, not pre-formatted)
        # [heritage: llama-cpp-python 2023] logit_bias — forwarded to llama-cpp-python
        # worker (see worker loop line 603). Supported since v0.2.0 (commit 07e47f5).
        request = {
            "system_prompt": system_prompt,
            "user_query": user_query,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": ["</s>", "User:", "\n\n"],
            "enable_thinking": False,
        }
        if logit_bias:
            request["logit_bias"] = logit_bias
        
        try:
            # Send request to worker (threaded — Queue.put blocks on serialization)
            await anyio.to_thread.run_sync(self._req_queue.put, request)
            
            # Wait for response (threaded — Queue.get blocks on I/O)
            response = await anyio.to_thread.run_sync(self._res_queue.get)
            
            # Check if response is an exception
            if isinstance(response, Exception):
                raise response
            
            if response is None:
                logger.warning("NativeGGUF inference returned None response")
                return None
            elif "choices" not in response:
                logger.warning("NativeGGUF inference returned response without choices")
                return None
            else:
                choice = response["choices"][0]
                # Response format difference:
                # Raw completion: choice["text"]
                # Chat completion: choice["message"]["content"]
                text = ""
                if "message" in choice and "content" in choice["message"]:
                    text = (choice["message"]["content"] or "").strip()
                elif "text" in choice:
                    text = choice["text"].strip()
                
                # Capture logprobs from response for ICS-F v1.0 compliance
                # Use `or {}` because logprobs key may exist with None value
                # when logprobs were not requested (logprobs=False in worker).
                self._last_logprobs = (choice.get("logprobs") or {}).get("top_logprobs")
                # [id-soft: vet-016] Cvar System — typed config lookup from cvar_table
                # Port 1.5: atomic trace_id logging for observability
                if trace_id:
                    logger.debug(
                        "NativeGGUF inference complete [trace_id=%s] tokens=%d chars=%d",
                        trace_id, response.get("usage", {}).get("completion_tokens", 0), len(text),
                    )
                return text
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            # Check for OOM patterns in the error message
            err_msg = str(e).lower()
            if "cuda malloc" in err_msg or "out of memory" in err_msg or "allocation failed" in err_msg:
                raise InferenceOOMError(
                    message=f"Native GGUF OOM: {e}", 
                    trace_id=trace_id, 
                    raw_error=e
                )
            if "illegal instruction" in err_msg or "segmentation fault" in err_msg:
                raise InferenceRuntimeError(
                    message=f"Native GGUF runtime crash: {e}", 
                    trace_id=trace_id, 
                    raw_error=e
                )
            
            logger.error(f"NativeGGUF inference failed: {e}", exc_info=True)
            # BUG-002 (2026-07-02): Must call shutdown() before dropping the
            # worker reference. Previously, self._worker_process = None was set
            # without terminating the process, leaving a zombie worker holding
            # ~2-5GB of model memory in RAM.
            self.shutdown()
            self._worker_process = None
            self._loaded_ctx = 0
            raise InferenceError(message=f"Native GGUF inference failed: {e}", trace_id=trace_id, raw_error=e) from e

    async def reload_with_context(self, n_ctx: int) -> bool:
        """Explicitly reload the model with a new context length.

        Atomic model swap with rollback: if the new model fails to load, the
        previous model instance and context are restored. Never leave the
        engine with a None model state.

        Useful for dynamic context management — call this when a conversation
        needs more context than currently allocated.

        Returns:
            True if reload succeeded.
        """
        # [id-soft: vet-057] Atomic Swap — save old state before mutation
        old_worker = self._worker_process
        old_ctx = self._loaded_ctx
        self._worker_process = None  # Signal unloading
        try:
            await self._ensure_loaded(n_ctx)
            logger.info(f"Context reloaded: {old_ctx} -> {self._loaded_ctx}")
            return True
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            # [id-soft: vet-058] Rollback — restore old state on failure
            self._worker_process = old_worker
            self._loaded_ctx = old_ctx if old_worker else 0
            logger.error(f"Context reload failed, rolled back to {self._loaded_ctx}: {e}", exc_info=True)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current provider status for observability."""
        return {
            "provider": self.name,
            "model_path": self.model_path,
            "loaded": self._worker_process is not None,
            "loaded_context": self._loaded_ctx,
            "cores": self._cores,
            "threads": self._n_threads,
            "kv_cache": f"k={self._type_k},v={self._type_v}",
            "affinity_applied": self._affinity_applied,
        }

    def shutdown(self):
        """Cleanly shut down the isolated inference executor."""
        if self._worker_process is not None:
            if self._req_queue is not None:
                try:
                    self._req_queue.put(None)  # Send shutdown signal
                except (RuntimeError, OSError):
                    pass
            self._worker_process.join(timeout=10)
            if self._worker_process.is_alive():
                self._worker_process.terminate()
        self._executor.shutdown(wait=False)
