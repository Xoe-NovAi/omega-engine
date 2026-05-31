# 🔱 Model Gateway — Local-First Inference Abstraction
# AP: AP-MODEL-GATEWAY-v2.4.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: MODEL-ABSTRACTION]
#
# LOCAL-FIRST provider fabric with automatic detection and fallback:
#   0. native-gguf       (llama-cpp-python, Zen 2 optimized) [PRIMARY]
#   1. lmster            (LM Studio headless server at :1234)
#   2. Ollama            (OpenAI-compatible API at :11434)
#   3. Google AI Studio  (cloud, Gemma 4 31B)
#   4. OpenRouter        (cloud, 300+ models)
#   5. OpenCode          (OpenCode built-in provider)
#   6. GitHub Copilot    (cloud, Claude/GPT models)
#   99. Graceful fallback (setup instructions)
#
# Zen 2 optimizations:
#   - CPU affinity pinned to physical cores [0,2,4,6]
#   - KV cache quantization (q8_0 key, q8_0 value by default)
#   - Adaptive thread pool (6 threads, pinned to cores 0,2,4,6)
#   - Cache-friendly batch sizes (512/32 for small models, 64/16 for 8B+)
#   - OMP_PROC_BIND=close for NUMA-aware scheduling on single-CCX

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import anyio
import yaml
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential_jitter, 
    retry_if_exception_type,
    before_sleep_log
)

from .backends.mock import OfflineMockBackend
from .backends.openai_compat import OpenAICompatProvider
from .backends.remote_provider import ProviderConfig
from .resource_guard import ResourceGuard
from .providers import GoogleAIProvider, LocallmsterProvider, OllamaProvider, MockProvider, NativeGGUFProvider
from .gnosis_proxy import GnosisProxy
from .entity_registry import EntityRegistry

logger = logging.getLogger(__name__)

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

class ModelGateway:

    """Abstracts local model inference. Auto-detects available backends.

    Supports Zen 2 optimizations:
      - KV cache quantization per-model
      - Adaptive thread count
      - ONNX Runtime fallback for compatible models
    """

    # Default backend URLs
    LMSTER_URL = "http://127.0.0.1:1234"
    OLLAMA_URL = "http://127.0.0.1:11434"
    LLAMA_CPP_URL = "http://127.0.0.1:8080"

    def __init__(self, config_path: Optional[str] = None, health_monitor: Optional[Any] = None):
        if config_path is None:
            config_path = os.environ.get(
                "OMEGA_MODELS_CONFIG",
                str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "models.yaml"),
            )
        self.config_path = Path(config_path)
        self.models = self._load_models()
        self._kv_cache_config = self._load_kv_cache_config()
        self._backend_cache: Dict[str, bool] = {}
        
        # Initialize Zen2Optimizer for hardware resonance
        from .cpu_optimizer import Zen2Optimizer
        self._cpu_optimizer = Zen2Optimizer()
        
        self.resource_guard = ResourceGuard()
        self._mock_backend = OfflineMockBackend()
        self.providers = self._load_provider_fabric()
        # Sprint 2 Governance: GnosisProxy for RAG-based tool discovery
        self._entity_registry = EntityRegistry()
        self._gnosis_proxy = GnosisProxy(self._entity_registry)
        # B5: HealthMonitor for latency and success/failure recording
        self._health_monitor = health_monitor
        # Sovereign Guard: Prevent leak amplification by limiting concurrent gateway entries
        self._limiter = anyio.CapacityLimiter(10)

    @staticmethod
    def _create_openrouter(name: str, cfg: dict) -> OpenAICompatProvider:
        """Factory for OpenRouter from raw YAML config dict."""
        extra = {k: v for k, v in cfg.items() if k not in ("provider", "priority", "api_key", "base_url")}
        return OpenAICompatProvider(ProviderConfig(
            name=name,
            priority=cfg.get("priority", 0),
            api_key=cfg.get("api_key"),
            base_url=cfg.get("base_url", "https://openrouter.ai/api").rstrip("/v1"),
            extra=extra,
        ))

    @staticmethod
    def _merge_native_gguf_config(p_cfg: dict, models: dict) -> dict:
        """Merge models.yaml model spec into native-gguf provider config.

        models.yaml is the single source of truth for model paths, context,
        threads, and KV cache. This method overlays those values onto the
        provider defaults from providers.yaml.
        """
        # Find first on-demand model as default path
        default_spec = models.get("phi-4-mini", {})
        merged = dict(p_cfg)

        # Keys to pull from models.yaml
        for key in ("path", "size_gb", "ram_mb", "context_window",
                     "threads", "load_strategy", "entity",
                     "kv_cache_key_type", "kv_cache_value_type"):
            if key in default_spec and key not in merged:
                merged[key] = default_spec[key]

        # Map models.yaml names → NativeGGUFProvider config names
        if "path" in merged and "model_path" not in merged:
            merged["model_path"] = merged.pop("path")
        if "context_window" in merged and "n_ctx" not in merged:
            merged["n_ctx"] = merged.pop("context_window")
        if "threads" in merged and "n_threads" not in merged:
            merged["n_threads"] = merged.pop("threads")

        # Map string KV cache types → llama.cpp enum ints
        kv_map = {"f16": 0, "q8_0": 8, "q4_0": 9, "fp8": 7}
        for yaml_key, prov_key in [("kv_cache_key_type", "type_k"),
                                    ("kv_cache_value_type", "type_v")]:
            if yaml_key in merged:
                merged[prov_key] = kv_map.get(merged.pop(yaml_key), 8)

        return merged

    def _load_provider_fabric(self) -> List[Any]:
        """Load provider chain from providers.yaml."""
        providers_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "providers.yaml"
        if not providers_path.exists():
            logger.warning(f"Provider config not found at {providers_path}. Using defaults.")
            return [MockProvider("mock", {})]

        with open(providers_path, "r") as f:
            config = yaml.safe_load(f)

        fabric_config = config.get("inference", {}).get("fallback_chain", [])

        provider_map = {
            "google": GoogleAIProvider,
            "opencode": ModelGateway._create_openrouter,
            "openrouter": ModelGateway._create_openrouter,
            "github-copilot": ModelGateway._create_openrouter,
            "lmster": LocallmsterProvider,
            "ollama": OllamaProvider,
            "native-gguf": NativeGGUFProvider,
            "mock": MockProvider,
        }

        instances = []
        for p_cfg in fabric_config:
            name = p_cfg.get("provider")
            if name not in provider_map:
                logger.warning(f"Unrecognized provider '{name}' in config. Skipping.")
                continue
            if name == "native-gguf":
                merged = self._merge_native_gguf_config(p_cfg, self.models)
                instances.append(provider_map[name](name, merged))
            else:
                instances.append(provider_map[name](name, p_cfg))

        def _get_priority(p):
            if hasattr(p, 'config') and isinstance(p.config, dict):
                return p.config.get('priority', 999)
            return 999
        instances.sort(key=_get_priority)

        return instances if instances else [MockProvider("mock", {})]

    def _load_models(self) -> dict:
        """Load model specs from config."""
        if not self.config_path.exists():
            logger.warning(f"Models config not found at {self.config_path}")
            return {}
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("models", {}) if data else {}

    def _load_kv_cache_config(self) -> dict:
        """Load KV cache quantization config."""
        if not self.config_path.exists():
            return {}
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("kv_cache", {}) if data else {}

    def get_kv_cache_flags(self, model_name: str) -> List[str]:
        """Get llama-server KV cache quantization flags for a model.

        Uses per-model config if available, otherwise default.
        """
        default_key = self._kv_cache_config.get("default_key_type", "q8_0")
        default_value = self._kv_cache_config.get("default_value_type", "q8_0")
        per_model = self._kv_cache_config.get("models", {}).get(model_name, {})

        key_type = per_model.get("key_type", default_key)
        value_type = per_model.get("value_type", default_value)

        return ["-ctk", key_type, "-ctv", value_type, "-mli", "1"]

    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get the GGUF path for a model by name."""
        spec = self.models.get(model_name)
        if not spec:
            return None
        path = spec.get("path")
        if path and Path(path).exists():
            return path
        for alt in spec.get("alt_paths", []):
            if Path(alt).exists():
                return alt
        return path

    def get_model_spec(self, model_name: str) -> Optional[dict]:
        """Get full model spec."""
        return self.models.get(model_name)

    def get_model_weight(self, model_name: str) -> int:
        """Return resource weight for a model based on RAM requirements.
        
        Light: 1, Medium: 2, Heavy: 4.
        """
        spec = self.models.get(model_name)
        if not spec:
            return 1
        
        ram_mb = spec.get("ram_mb", 0)
        if ram_mb >= 4000:
            return 4
        if ram_mb >= 2000:
            return 2
        return 1

    # ── Backend availability detection ─────────────────────────────────
    async def _check_lmster(self) -> bool:
        """Check if lmster (LM Studio headless) is running (127.0.0.1:1234/v1/models)."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.LMSTER_URL}/v1/models")
                return r.status_code == 200
        except Exception:
            return False

    async def _check_ollama(self) -> bool:
        """Check if Ollama is running (127.0.0.1:11434/api/tags)."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.OLLAMA_URL}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def _check_llama_cpp(self) -> bool:
        """Check if llama.cpp server is running (127.0.0.1:8080/health)."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.LLAMA_CPP_URL}/health")
                return r.status_code == 200
        except Exception:
            return False

    async def _check_llama_cli(self) -> bool:
        """Check if llama-cli binary is available (async, non-blocking)."""
        try:
            result = await anyio.run_process(["llama-cli", "--version"], check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _check_llmster(self) -> bool:
        """Check if llmster binary is available (async, non-blocking)."""
        try:
            result = await anyio.run_process(["llmster", "--version"], check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def detect_backends(self) -> Dict[str, bool]:
        """Detect all available inference backends. Returns dict of name -> available."""
        backends = {
            "lmster": await self._check_lmster(),
            "ollama": await self._check_ollama(),
            "llama_cpp": await self._check_llama_cpp(),
            "llama_cli": await self._check_llama_cli(),
            "llmster": await self._check_llmster(),
        }
        self._backend_cache = backends
        return backends

    async def get_preferred_backend(self) -> str:
        """Return the name of the best available backend.
        
        Cloud-first priority: Google → OpenRouter → OpenCode → Copilot → lmster → Ollama.
        Local inference backends detect available servers.
        """
        # Cloud providers are always considered "available" (upstream health is their concern)
        # For local backends, check actual availability
        backends = await self.detect_backends()
        for name in ["lmster", "ollama", "llama_cpp", "llama_cli", "llmster"]:
            if backends.get(name):
                return name
        # If no local backend found, cloud providers will be used via fabric
        return "cloud"

    # ── Model name resolution ──────────────────────────────────────────
    async def _resolve_ollama_model(self, model_name: str) -> str:
        """Resolve config model name to an Ollama tag.

        Checks available Ollama models and finds the best match.
        Falls back to the first available model if no match found.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.OLLAMA_URL}/api/tags")
                if r.status_code == 200:
                    data = r.json()
                    available = [m["name"] for m in data.get("models", [])]
                    # Try exact match first
                    if model_name in available:
                        return model_name
                    # Try prefix match (e.g. 'krikri' matches 'krikri:latest')
                    name_lower = model_name.lower().split("-")[0].split("_")[0]
                    for tag in available:
                        if tag.lower().startswith(name_lower):
                            return tag
                    # Return first available as fallback
                    if available:
                        return available[0]
        except Exception:
            pass
        return model_name

    async def _enrich_with_tools(self, model_name: str, system_prompt: str, user_query: str) -> str:
        """Pre-inference hook: enrich system prompt with GnosisProxy discovered tools."""
        try:
            # Derive entity name from model_name
            spec = self.models.get(model_name, {})
            entity_name = spec.get("entity", model_name).split(",")[0].strip()
            if not entity_name or entity_name == model_name:
                # Fallback: try to derive from model mapping
                entity_name = model_name.split("-")[0].title() if "-" in model_name else "Oracle"
 
            discovered = self._gnosis_proxy.discover_tools(user_query, entity_name)
            if discovered:
                tool_lines = "\n".join(
                    f"  - {t['name']}: {t['description'][:80]}"
                    for t in discovered
                )
                tools_block = f"\n\n### Available Tools (GnosisProxy)\n{tool_lines}\n"
                return system_prompt + tools_block
        except Exception as e:
            logger.debug(f"GnosisProxy enrichment skipped: {e}")
        return system_prompt

    # ── Generation (auto-detect + fallback chain) ──────────────────────
    async def _execute_with_retry(self, provider: Any, model_name: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int, trace_id: Optional[str] = None) -> Optional[str]:
        """Execute request with retry logic and background metrics tracking.
        
        Consolidates retry logic: RemoteProviders handle their own internal retries.
        """
        from .backends.remote_provider import RemoteProvider
        
        # If it's a RemoteProvider, it owns its retry loop. Call once.
        if isinstance(provider, RemoteProvider):
            start_time = time.monotonic()
            try:
                response = await provider.generate(model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                if self._health_monitor:
                    latency_ms = (time.monotonic() - start_time) * 1000
                    self._health_monitor.record_latency(model_name, latency_ms)
                    self._health_monitor.record_success(model_name)
                return response
            except Exception as e:
                if self._health_monitor:
                    self._health_monitor.record_failure(model_name)
                logger.error(f"Remote provider {provider.name} failed: {e}")
                return None

        # Local providers use the gateway's retry loop
        response = None
        max_retries = 3
        for attempt in range(max_retries):
            start_time = time.monotonic()
            try:
                response = await provider.generate(model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                if self._health_monitor:
                    latency_ms = (time.monotonic() - start_time) * 1000
                    self._health_monitor.record_latency(model_name, latency_ms)
                    self._health_monitor.record_success(model_name)
                if response:
                    return response
            except Exception as e:
                if self._health_monitor:
                    self._health_monitor.record_failure(model_name)
                err_msg = str(e).lower()
                is_transient = any(code in err_msg for code in ["429", "502", "503", "504", "timeout"])
                if not is_transient or attempt == max_retries - 1:
                    logger.error(f"Fatal or final error with {provider.name}: {e}")
                    raise e
                logger.warning(f"Transient error with {provider.name} (attempt {attempt+1}): {e}. Retrying...")
                await anyio.sleep(2 ** attempt)
        return None

    def _resolve_model_name(self, provider: Any, model_name: str) -> str:
        """Resolve model name through provider-specific overrides.
        
        Entities use local GGUF filenames (e.g., 'qwen3-1.7b-q6_k') as model names.
        Cloud providers need these translated to their model IDs (e.g., 'qwen/qwen3-1.7b').
        The provider's 'model_overrides' config section maps local names → provider names.
        """
        # Extract overrides from provider config (works for both BaseProvider and RemoteProvider)
        overrides: Dict[str, str] = {}
        if hasattr(provider, 'config'):
            if isinstance(provider.config, dict):
                overrides = provider.config.get('model_overrides', {})
            elif hasattr(provider.config, 'extra'):
                overrides = provider.config.extra.get('model_overrides', {})
        
        return overrides.get(model_name, model_name)

    async def generate(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        pinned_provider: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Tuple[str, bool]:
        """Send a prompt to the model using the configured provider fabric.
        
        Returns:
            Tuple of (response_text, is_cloud)
        """
        async with self._limiter:
            if temperature is None:
                temperature = 0.7
                
            if os.environ.get("OMEGA_ENV") == "test":
                res = await self._mock_backend.generate(
                    model_name, system_prompt, user_query, temperature, max_tokens
                )
                return res, False
            
            # Calculate resource weight for this model
            weight = self.get_model_weight(model_name)
            
            # Pre-inference GnosisProxy enrichment
            enriched_prompt = await self._enrich_with_tools(model_name, system_prompt, user_query)
            
            # Provider Selection
            if pinned_provider:
                # Bypass fallback chain and use specific provider
                target_provider = next((p for p in self.providers if p.name == pinned_provider), None)
                if target_provider:
                    # Resolve model name for pinned provider
                    resolved_model = self._resolve_model_name(target_provider, model_name)
                    # ResourceGuard protection for pinned local providers
                    if isinstance(target_provider, (LocallmsterProvider, OllamaProvider, NativeGGUFProvider)):
                        async with self.resource_guard.lock(weight=weight):
                            res = await self._call_provider_with_resilience(target_provider, resolved_model, enriched_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                            is_cloud = target_provider.name in ("google", "openrouter", "opencode", "github-copilot")
                            return res, is_cloud
                    res = await self._call_provider_with_resilience(target_provider, resolved_model, enriched_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                    is_cloud = target_provider.name in ("google", "openrouter", "opencode", "github-copilot")
                    return res, is_cloud
                logger.warning(f"Pinned provider {pinned_provider} not found. Falling back to chain.")
            
            for provider in self.providers:
                if not await provider.is_available():
                    continue
                
                # Resolve model name through provider's overrides
                resolved_model = self._resolve_model_name(provider, model_name)
                
                try:
                    # Wrap local providers in a timeout to prevent systemic hangs
                    if isinstance(provider, (LocallmsterProvider, OllamaProvider, NativeGGUFProvider)):
                        async with self.resource_guard.lock(weight=weight):
                            with anyio.move_on_after(130):
                                response = await self._execute_with_retry(provider, resolved_model, enriched_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                    else:
                        response = await self._execute_with_retry(provider, resolved_model, enriched_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
                    
                    if response:
                        is_cloud = provider.name in ("google", "openrouter", "opencode", "github-copilot")
                        return response, is_cloud
                except Exception as e:
                    logger.warning(f"Provider {provider.name} failed after retries: {e}")
                    # Log backend fallback event for observability
                    if trace_id:
                        try:
                            from omega.observability import get_engine, EventType
                            get_engine().log_event(
                                EventType.BACKEND_FALLBACK,
                                trace_id,
                                {"failed_provider": provider.name, "error": str(e)[:200], "model": model_name}
                            )
                        except Exception:
                            pass
            
            fallback = self._fallback_response(model_name, enriched_prompt, user_query)
            return fallback, False

    async def _call_provider_with_resilience(self, provider, model_name, system_prompt, user_query, temperature, max_tokens, trace_id=None):
        """Wrapper to apply the OpenRouter retry policy."""
        @openrouter_retry_policy
        async def _do_call():
            try:
                return await provider.generate(model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
            except Exception as e:
                # Map specific HTTP errors to Transient vs Fatal
                err_msg = str(e).lower()
                if "429" in err_msg and "provider returned error" in err_msg:
                    raise OpenRouterFatalError(f"Upstream limit reached: {e}")
                if any(code in err_msg for code in ["429", "502", "503", "504"]):
                    raise OpenRouterTransientError(f"Transient error: {e}")
                raise e
        
        return await _do_call()

    # ── Backend: Ollama (OpenAI-compatible API) ──────────────────────
    async def _try_ollama(
        self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Inference via Ollama's OpenAI-compatible API at 127.0.0.1:11434."""
        import httpx

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
            response = await client.post(f"{self.OLLAMA_URL}/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
        return None

    # ── Backend: lmster (LM Studio Headless Server) ───────────────────
    async def _try_lmster(
        self, model: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Inference via lmster (LM Studio headless server) at 127.0.0.1:1234 OpenAI-compatible API."""
        import httpx

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
            response = await client.post(f"{self.LMSTER_URL}/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
        return None

    # ── Backend: llama.cpp HTTP server ────────────────────────────────
    async def _try_llama_server(
        self, system_prompt: str, user_query: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Inference via llama.cpp HTTP server at 127.0.0.1:8080."""
        import httpx

        prompt = f"{system_prompt}\n\nUser: {user_query}\n\nEntity:"
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": ["User:", "\n\n"],
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.LLAMA_CPP_URL}/completion", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("content", "").strip()

    # ── Backend: Direct GGUF CLI (llama-cli or llmster) ───────────────
    async def _try_direct_gguf(
        self, cli_name: str, model_path: str, system_prompt: str, user_query: str,
        temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Inference via direct CLI subprocess (llama-cli or llmster)."""
        prompt = f"<|system|>{system_prompt}</s><|user|>{user_query}</s><|assistant|>"

        result = await anyio.run_process(
            [
                cli_name,
                "--model", model_path,
                "--prompt", prompt,
                "--temp", str(temperature),
                "--n-predict", str(max_tokens),
                "--no-display-prompt",
            ],
            capture_output=True,
            check=False,
        )

        if result.returncode == 0:
            output = result.stdout.decode().strip()
            return output if output else None
        return None

    # ── Backend: ONNX Runtime ─────────────────────────────────────────
    async def _try_onnx(
        self, model_path: str, system_prompt: str, user_query: str,
        temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Inference via ONNX Runtime (optimized for Zen 2 CPU)."""
        try:
            import onnxruntime as ort
        except ImportError:
            logger.debug("ONNX Runtime not installed; skipping ONNX backend")
            return None

        try:
            sess = ort.InferenceSession(
                model_path,
                providers=["CPUExecutionProvider"],
                sess_options=ort.SessionOptions(),
            )
            input_name = sess.get_inputs()[0].name
            # Simple text completion via ONNX (for compatible models)
            input_text = f"{system_prompt}\n\nUser: {user_query}\n\nAssistant:"
            inputs = {input_name: [input_text]}
            outputs = sess.run(None, inputs)
            if outputs and len(outputs[0]) > 0:
                return str(outputs[0][0])[:max_tokens]
        except Exception as e:
            logger.debug(f"ONNX inference failed: {e}")
        return None

    def is_onnx_available(self) -> bool:
        """Check if ONNX Runtime is installed and usable."""
        try:
            import onnxruntime as ort
            return "CPUExecutionProvider" in ort.get_available_providers()
        except ImportError:
            return False

    # ── Fallback ──────────────────────────────────────────────────────
    def _fallback_response(self, model_name: str, system_prompt: str, user_query: str) -> str:
        """Return a graceful fallback with setup instructions."""
        entity_name = "Oracle"
        for name, spec in self.models.items():
            if name == model_name:
                entity_name = spec.get("entity", "Oracle").split(",")[0].strip()
                break

        return (
            f"{entity_name} is here, but no inference backend is running.\n\n"
            f"Quick options:\n"
            f"  1. Start lmster (LM Studio headless server) — `lmster --model path/to/model.gguf` on :1234\n"
            f"  2. `ollama run qwen3:1.7b` — lightweight fallback, auto-detected at :11434\n"
            f"  3. Run llama-server: `llama-server --model path/to/model.gguf` on :8080\n\n"
            f"Then try: `omega summon {entity_name.title()} \"{user_query}\"`"
        )

    # ── Diagnostics ───────────────────────────────────────────────────
    async def check_health(self) -> Dict[str, Any]:
        """Return health status of all inference backends.

        Cloud-first priority: Google → OpenRouter → OpenCode → Copilot → lmster → Ollama
        Local backends checked via HTTP; cloud providers are always considered available.
        """
        backends = await self.detect_backends()
        # Show provider fabric status
        fabric_status = {}
        for p in self.providers:
            name = p.name
            is_avail = await p.is_available()
            fabric_status[name] = {
                "available": is_avail,
                "priority": getattr(p.config, 'priority', 999) if hasattr(p, 'config') else 999,
            }
        return {
            "fabric": fabric_status,
            "local_backends": {
                "lmster": {
                    "available": backends.get("lmster", False),
                    "url": self.LMSTER_URL,
                    "note": "LM Studio headless. Start: `lms server start`"
                },
                "ollama": {
                    "available": backends.get("ollama", False),
                    "url": self.OLLAMA_URL,
                    "note": "Ollama fallback. Run: `ollama run qwen3:1.7b`"
                },
                "llama_cpp": {
                    "available": backends.get("llama_cpp", False),
                    "url": self.LLAMA_CPP_URL,
                    "note": "llama.cpp HTTP server"
                },
            },
        }

    async def is_server_alive(self) -> bool:
        """Check if any inference backend is available."""
        backends = await self.detect_backends()
        return any(backends.values())
