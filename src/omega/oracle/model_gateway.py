# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Model Gateway — Local-First Inference Abstraction
# AP: AP-MODEL-GATEWAY-v2.4.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: MODEL-ABSTRACTION]
#
# LOCAL-FIRST provider fabric with automatic detection and fallback:
#   0. native-gguf       (llama-cpp-python, Zen 2 optimized) [PRIMARY]
#   1. lmster            (LM Studio headless server at :1234)
#   2. Ollama            (OpenAI-compatible API at :11434)
#   3. Google AI Studio  (cloud, Gemma 4 31B)
#   4. OpenCode Zen      (cloud, MiniMax/DeepSeek/MiMo)
#   5. Cline             (cloud via API/headless, 1M context)
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
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
import anyio

@dataclass
class GenerateResult:
    """Standardized result of a model generation call.
    
    [M22: Response Provenance Mandate] Ensures the actual provider
    that served the response is tracked for sovereignty auditing.
    
    [Operation Deep-Siphon] ICS-F v1.0 Sprint 0: logprobs field added.
    Per-token log probabilities from the inference backend. Populated
    when the provider supports logprobs (e.g., NativeGGUF with logprobs=5).
    """
    text: str
    provider_name: str
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
    logprobs: Optional[list] = None

from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import yaml
from omega.cvar_table import cvar_get, cvar_namespace
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential_jitter, 
    retry_if_exception_type,
    before_sleep_log
)

from .backends.mock import OfflineMockBackend
from .backends.openai_compat import OpenAICompatProvider
from .backends.antigravity_provider import AntigravityProvider
from .backends.remote_provider import ProviderConfig
from .resource_guard import ResourceGuard
from .providers import GoogleAIProvider, LocallmsterProvider, OllamaProvider, MockProvider, NativeGGUFProvider
from .health_monitor import CircuitOpenError

from .gnosis_proxy import GnosisProxy
from .entity_registry import EntityRegistry
from .entity_affinity import EntityAffinityResolver, AffinityResult
from .budget_gate import BudgetGate
from .provider_selector import ProviderSelector
from omega.observability.token_ledger import TokenLedger
from omega.observability.latency_tracker import tracker
from omega.state.usm import USMManager

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
    DocRef: docs/reference/api/model_gateway.md
    
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
        
        # Load Sovereign Secrets from .env
        self._load_sovereign_secrets()
        
        self.models = self._load_models()
        self._kv_cache_config = self._load_kv_cache_config()
        self._backend_cache: Dict[str, bool] = {}
        
        # Initialize Zen2Optimizer for hardware resonance
        from .cpu_optimizer import Zen2Optimizer
        self._cpu_optimizer = Zen2Optimizer()
        
        self.resource_guard = ResourceGuard()
        self._mock_backend = OfflineMockBackend()
        self.providers = self._load_provider_fabric()
        # [id-soft: vet-055] Fixed-Size Active Set — 32-entry clip range for O(1) culling
        # Sprint 3 Hardening (P6): Split into Local/Cloud tiers to prevent
        # sovereignty drift (Mandate 7) — local providers always tried first.
        self._local_active: List[str] = []
        self._cloud_active: List[str] = []
        # Availability TTL cache (seconds) — avoids repeated health checks
        # for known-healthy or known-dead providers.
        self._availability_cache: Dict[str, Tuple[float, bool]] = {}
        self._availability_ttl: float = 30.0
        # Shared HTTP client (lazy-initialized) for connection pooling.
        self._http_client: Optional[Any] = None
        # Sprint 2 Governance: GnosisProxy for RAG-based tool discovery

        # Sovereign State Manager (USM) for SomaticState (M20)
        from omega.state import get_usm
        self.usm = get_usm()
        
        self._entity_registry = EntityRegistry()
        self._gnosis_proxy = GnosisProxy(self._entity_registry)
        # B5: HealthMonitor for latency and success/failure recording
        self._health_monitor = health_monitor
        # Entity→Model Affinity Resolver (YAML-backed routing DB)
        # Handoff: ho_8135d6122230 — Lilith Phase 1 port from xna-omega-legacy
        # R3: Cross-references provider IDs against config/providers.yaml
        self.affinity_resolver = EntityAffinityResolver(
            yaml_path=Path(__file__).resolve().parent.parent.parent.parent / "config" / "entity_model_affinity.yaml"
        )
        # Seed known providers from loaded fabric for R3 validation
        provider_names = {p.name for p in self.providers}
        self.affinity_resolver.set_known_providers(provider_names)
        
        # A2A Bridge — Sovereign Agent Identity (Google A2A v1.0)
        # Maps EntityRegistry entities to A2A Agent Cards for cross-agent discovery
        from .a2a_bridge import A2ABridge
        self._a2a_bridge = A2ABridge(entity_registry=self._entity_registry)
        
        # Sovereign Guard: Prevent leak amplification by limiting concurrent gateway entries
        self._limiter = anyio.CapacityLimiter(10)
        self.provider_selector = ProviderSelector(self, health_monitor=self._health_monitor)
        from .rate_limiter import RateLimiter
        self.rate_limiter = RateLimiter()
        # [M8 Zero Telemetry] WARP Proxy Pool — optional, injected by Oracle
        # Only used for opencode-zen provider to bypass rate limits.
        # Set via oracle.py: ModelGateway.proxy_pool = EphemeralWarpPool()
        self.proxy_pool: Optional[Any] = None

    def list_providers(self) -> List[Dict[str, Any]]:
        """Return a list of all registered providers and their current health."""
        def _get_prio(p):
            if hasattr(p, 'priority'): return p.priority
            if hasattr(p, 'config'):
                if isinstance(p.config, dict): return p.config.get('priority', 999)
                if hasattr(p.config, 'priority'): return p.config.priority
            return 999

        return [
            {
                "name": p.name,
                "priority": _get_prio(p),
                "type": p.__class__.__name__,
                "healthy": self._backend_cache.get(p.name, False)
            }
            for p in self.providers
        ]

    async def get_available_providers(self, model_name: str) -> List[Any]:
        """Return providers that are available (healthy or untested) for a model.
        
        Filters by health cache — providers with known-false status are excluded.
        Returns all providers if none have been health-checked yet.
        """
        available = []
        for p in self.providers:
            status = self._backend_cache.get(p.name)
            if status is None or status is True:  # untested or healthy
                available.append(p)
        return available

    def list_models(self) -> List[Dict[str, Any]]:
        """Return a list of all configured models and their specs."""
        return [
            {"name": name, **spec}
            for name, spec in self.models.items()
        ]

    def _load_sovereign_secrets(self) -> None:
        """Load API keys from .env file into environment variables.
        
        Implements the Sovereign Gateway pattern: secrets are stored in a 
        single .env file and injected into the process environment.
        """
        env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        if not env_path.exists():
            logger.warning(f"Sovereign secrets file not found at {env_path}. Using system env.")
            return
        
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            logger.info("Sovereign secrets loaded successfully from .env")
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to load sovereign secrets: {e}", exc_info=True)
            raise ConfigError(f"Sovereign secrets load failed: {e}", raw_error=e) from e


    @staticmethod
    def _create_openrouter(name: str, cfg: dict) -> OpenAICompatProvider:
        """Factory for OpenRouter from raw YAML config dict.

        [S3 B5 / D205] Supports both legacy single `api_key` and new
        `api_keys` list (8-account Active-Passive sharding).
        """
        extra = {k: v for k, v in cfg.items() if k not in ("provider", "priority", "api_key", "api_keys", "base_url")}
        # Resolve key list: prefer api_keys list, fall back to wrapping api_key
        api_keys = cfg.get("api_keys", [])
        if not api_keys and cfg.get("api_key"):
            api_keys = [cfg["api_key"]]
        return OpenAICompatProvider(ProviderConfig(
            name=name,
            priority=cfg.get("priority", 0),
            api_keys=api_keys,
            base_url=cfg.get("base_url", "https://openrouter.ai/api").rstrip("/v1"),
            extra=extra,
        ))

    @staticmethod
    def _create_antigravity(name: str, cfg: dict) -> AntigravityProvider:
        """Factory for Antigravity from raw YAML config dict.

        Uses the official google.genai.Client with a custom HttpOptions
        base_url pointing to the Antigravity API.  Sticky account routing
        only (D205) — no round-robin.

        [S3 B5 / D205] Supports both legacy single `api_key` and new
        `api_keys` list (8-account Active-Passive sharding).
        """
        extra = {k: v for k, v in cfg.items() if k not in ("provider", "priority", "api_key", "api_keys", "base_url")}
        # Resolve key list: prefer api_keys list, fall back to wrapping api_key
        api_keys = cfg.get("api_keys", [])
        if not api_keys and cfg.get("api_key"):
            api_keys = [cfg["api_key"]]
        return AntigravityProvider(ProviderConfig(
            name=name,
            priority=cfg.get("priority", 0),
            api_keys=api_keys,
            base_url=cfg.get("base_url", "https://api.antigravity.ai/v1"),
            extra=extra,
        ))

    def _merge_native_gguf_config(self, p_cfg: dict, models: dict) -> dict:
        """Merge models.yaml model spec into native-gguf provider config.

        models.yaml is the single source of truth for model paths, context,
        threads, and KV cache. This method overlays those values onto the
        provider defaults from providers.yaml.

        [HANG-FIX] models.yaml ``path`` ALWAYS overrides providers.yaml
        ``model_path``. If providers.yaml has an unresolved ``env:`` prefix
        in ``model_path``, it is resolved here as fallback only when
        models.yaml has no matching entry.  Previously the merge only copied
        keys that didn't already exist in the provider config — but since
        providers.yaml uses ``model_path`` and models.yaml uses ``path``,
        the mismatch happened to avoid the bug for the default config.
        This fix makes the preference **explicit** and handles the edge case
        where ``path`` is also set in providers.yaml.
        """
        # Resolve env: prefixes in provider config values (e.g. model_path)
        def _resolve_env_prefix(val: str) -> str:
            if isinstance(val, str) and val.startswith("env:"):
                rest = val[4:]
                parts = rest.split("/", 1)
                env_var = parts[0]
                suffix = f"/{parts[1]}" if len(parts) > 1 else ""
                base = os.environ.get(env_var, "")
                if not base:
                    logger.warning("Environment variable %s not set for path %s", env_var, val)
                return base + suffix
            return val

        # Find first on-demand model as default path
        default_spec = models.get(self._system_default_model(), {})
        merged = dict(p_cfg)

        # Resolve env: prefix on any existing model_path first
        if "model_path" in merged:
            resolved = _resolve_env_prefix(merged["model_path"])
            if resolved != merged["model_path"]:
                merged["model_path"] = resolved

        # Keys to pull from models.yaml — ALWAYS prefer models.yaml path
        for key in ("size_gb", "ram_mb", "context_window",
                     "threads", "load_strategy", "entity",
                     "kv_cache_key_type", "kv_cache_value_type"):
            if key in default_spec and key not in merged:
                merged[key] = default_spec[key]
        
        # Path override: models.yaml ``path`` ALWAYS wins over providers.yaml ``model_path``
        if "path" in default_spec:
            models_path = _resolve_env_prefix(default_spec["path"])
            merged["model_path"] = models_path
            logger.debug(
                "native-gguf model_path overridden from models.yaml: %s",
                models_path,
            )
        elif "path" in default_spec and "model_path" not in merged:
            # Fallback: resolve env: prefix on models.yaml path
            merged["model_path"] = _resolve_env_prefix(default_spec["path"])
        
        # Clean up any orphan ``path`` key from provider config
        if "path" in merged:
            del merged["path"]

        # Optimize threads based on model size if not explicitly set
        if "threads" not in merged:
            model_size_b = default_spec.get("size_gb", 1.7) # Default to 1.7B if unknown
            merged["threads"] = self._cpu_optimizer.get_recommended_threads(model_size_b)

        # Map models.yaml names → NativeGGUFProvider config names
        if "context_window" in merged and "n_ctx" not in merged:
            merged["n_ctx"] = merged.pop("context_window")
        if "threads" in merged and "n_threads" not in merged:
            merged["n_threads"] = merged.pop("threads")

        # Map string KV cache types → llama.cpp enum ints
        kv_map = {"f16": 1, "q8_0": 8, "q4_0": 2}
        for yaml_key, prov_key in [("kv_cache_key_type", "type_k"),
                                    ("kv_cache_value_type", "type_v")]:
            if yaml_key in merged:
                merged[prov_key] = kv_map.get(merged.pop(yaml_key), 8)

        return merged

    def _load_provider_fabric(self) -> List[Any]:
        """Load provider chain from providers.yaml.

        [test-mode] When OMEGA_ENV=test, short-circuit to MockProvider only.
        This prevents real GGUF model loading during tests — each fresh
        Oracle() creates a fresh ModelGateway, and loading even a 1.7B model
        takes 15-60s on Ryzen 5700U (no GPU). With 26 oracle tests each
        creating fresh instances, the cumulative time exceeds any reasonable
        timeout. MockProvider returns deterministic responses in <1ms.
        """
        if os.environ.get("OMEGA_ENV") == "test":
            return [MockProvider("mock", {"timeout_seconds": 5.0})]

        providers_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "providers.yaml"
        if not providers_path.exists():
            logger.warning(f"Provider config not found at {providers_path}. Using defaults.")
            return [MockProvider("mock", {})]

        with open(providers_path, "r") as f:
            config = yaml.safe_load(f)

        fabric_config = config.get("inference", {}).get("fallback_chain", [])

        provider_map = {
            "google": GoogleAIProvider,
            "openrouter": ModelGateway._create_openrouter,
            "opencode-zen": ModelGateway._create_openrouter,
            "cline": ModelGateway._create_openrouter,
            "github-copilot": ModelGateway._create_openrouter,
            "antigravity": ModelGateway._create_antigravity,
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
            """Extract priority from provider config — handles both dict and dataclass (ProviderConfig)."""
            cfg = getattr(p, 'config', None)
            if cfg is None:
                return 999
            if isinstance(cfg, dict):
                return cfg.get('priority', 999)
            if hasattr(cfg, 'priority'):
                return cfg.priority
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
        """Get the GGUF path for a model by name. Resolves 'env:' prefixes.

        [M1/P3 Graceful Fallback] Returns None (not empty string) when no path
        is configured, enabling callers to distinguish between 'model not found'
        (None) and 'no file mapping for this model' (also None). Tests can assert
        ``path is not None and path.endswith('.gguf')`` without relying on file
        existence on the test machine.
        """
        spec = self.models.get(model_name)
        if not spec:
            return None
        
        def resolve_path(p: str) -> str:
            if p.startswith("env:"):
                env_var = p[4:].split("/")[0]
                relative_path = "/".join(p[4:].split("/")[1:])
                base = os.environ.get(env_var, "")
                return os.path.join(base, relative_path)
            return p

        path = resolve_path(spec.get("path", ""))
        if path and Path(path).exists():
            return path
        for alt in spec.get("alt_paths", []):
            resolved_alt = resolve_path(alt)
            if Path(resolved_alt).exists():
                return resolved_alt
        # [M1/P3] Return None instead of empty string when no path configured
        return path if path else None

    def get_model_spec(self, model_name: str) -> Optional[dict]:
        """Get full model spec."""
        return self.models.get(model_name)

    def get_model_weight(self, model_name: str) -> int:
        """Return resource weight for a model based on RAM requirements (in MB).
        
        Sovereign-Sized: returns actual RAM requirement from models.yaml.
        """
        spec = self.models.get(model_name)
        if not spec:
            return 1024 # Default to 1GiB if unknown
        
        return spec.get("ram_mb", 1024)

    # ── Backend availability detection ─────────────────────────────────
    async def _check_lmster(self) -> bool:
        """Check if lmster (LM Studio headless) is running (127.0.0.1:1234/v1/models)."""
        try:
            import httpx2 as httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.LMSTER_URL}/v1/models")
                return r.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def _check_ollama(self) -> bool:
        """Check if Ollama is running (127.0.0.1:11434/api/tags)."""
        try:
            import httpx2 as httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.OLLAMA_URL}/api/tags")
                return r.status_code == 200
        except (httpx.HTTPError, OSError):
            return False

    async def _check_llama_cpp(self) -> bool:
        """Check if llama.cpp server is running (127.0.0.1:8080/health)."""
        try:
            import httpx2 as httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{self.LLAMA_CPP_URL}/health")
                return r.status_code == 200
        except (httpx.HTTPError, OSError):
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

    # ── Speculative decoding config (from cpu_optimizer) ─────────────
    # Port 3.5: expose the CPU-level speculative decode config for Oracle/Iris.
    @property
    def spec_decode_config(self) -> 'SpeculativeDecodeConfig':
        """Expose the Zen 2-optimized speculative decode configuration.

        Returns:
            SpeculativeDecodeConfig with draft_model, min/max_draft_tokens,
            and target_acceptance_rate tailored for the Ryzen 7 5700U.
        """
        return self._cpu_optimizer.spec_decode

    @property
    def health_monitor(self):
        """Expose the health monitor for provider availability checks."""
        return self._health_monitor

    # ── Entity-aware model affinity ───────────────────────────────────
    # Per-entity model overrides for domain-specific routing.
    # Fallback chain: entity override → entity registry field → domain default → system default
    # [legacy: xna-omega-legacy] Port 3.1: Entity Model Affinity

    _entity_model_map: Dict[str, str] = {}  # entity_name.lower() -> model_name

    def set_entity_model(self, entity_name: str, model_name: str) -> None:
        """Set a per-entity model override.
        
        DEPRECATED: Use config/entity_model_affinity.yaml for persistent routing.
        This method still works for temporary runtime overrides.
        """
        logger.warning(
            "set_entity_model() is deprecated. Use config/entity_model_affinity.yaml "
            "for sovereign routing. Runtime override applied: %s -> %s",
            entity_name, model_name
        )
        self._entity_model_map[entity_name.lower().strip()] = model_name
        logger.debug("Entity model affinity set: %s -> %s", entity_name.lower(), model_name)


    def remove_entity_model(self, entity_name: str) -> None:
        """Remove a per-entity model override, reverting to default resolution.
        
        DEPRECATED: Use config/entity_model_affinity.yaml for persistent routing.
        """
        logger.warning(
            "remove_entity_model() is deprecated. Use config/entity_model_affinity.yaml "
            "for sovereign routing."
        )
        self._entity_model_map.pop(entity_name.lower().strip(), None)

    def get_model_for_entity(
        self,
        entity_name: Optional[str] = None,
        affinity_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Resolve the best model for an entity using fallback chain.

        Resolution priority:
        0. YAML Affinity Resolver — Entity→Model Affinity DB (entity_model_affinity.yaml)
           NEW: Ported from xna-omega-legacy by Lilith (ho_8135d6122230).
           Provides 3-tier model preferences, routing rules, inference presets.
        1. Entity override (set_entity_model) — runtime overrides for entity-specific routing
        2. Entity registry field — the entity's configured ``model`` in its YAML definition
        3. Domain-based mapping — entity's first domain linked to model config
        4. System default — "qwen3-1.7b" (Iris tier)

        Args:
            entity_name: Entity name to resolve. If None, returns system default.
            affinity_context: Optional context dict for YAML affinity resolver
                (domain, complexity, online, requires, prompt_length).

        Returns:
            Model identifier string.
        """
        if not entity_name:
            return self._system_default_model()

        key = entity_name.lower().strip()

        # Tier 0: YAML Affinity Resolver — Entity→Model Affinity DB
        # [id-soft: vet-016] cvar pattern — YAML-backed config, hot-reloadable
        if self.affinity_resolver.is_loaded() or affinity_context is not None:
            try:
                result = self.affinity_resolver.resolve(
                    entity_name=key,
                    context=affinity_context or {},
                )
                if result and result.best_match:
                    logger.debug(
                        "Affinity resolver matched '%s' → model=%s tier=%s provider=%s",
                        key, result.best_match, result.tier, result.provider,
                    )
                    return result.best_match
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("Affinity resolver failed (non-fatal): %s", str(e), exc_info=True)

        # Tier 1: Runtime override via set_entity_model()
        override = self._entity_model_map.get(key)
        if override:
            return override

        # Tier 2: Entity registry field
        entity = self._entity_registry.get(key)
        if entity and entity.model:
            return entity.model

        # Tier 3: Domain-based — use entity's first domain to find model match
        if entity and entity.domains:
            domain = entity.domains[0].lower()
            # Check if models.yaml has domain->model mappings
            domain_key = f"domain.{domain}"
            if domain_key in getattr(self, 'models', {}):
                domain_model = self.models[domain_key].get("model")
                if domain_model:
                    return domain_model

        # Tier 4: System default
        return self._system_default_model()

    async def resolve_entity_affinity(
        self,
        entity_name: str,
        query: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AffinityResult]:
        """Resolve full entity→model affinity including inference presets.
        
        Returns the full AffinityResult dataclass with model, provider, tier,
        and inference_presets (temperature, system_prompt, preferred_context).
        
        This is the primary integration point for Oracle._summon() to apply
        entity-specific inference tuning from the YAML affinity database.
        
        Args:
            entity_name: Entity to resolve affinity for.
            query: The user query (used for prompt_length_lt matching).
            context: Optional context dict (domain, complexity, online, requires).
        """
        # Ensure resolver is loaded (lazy init)
        if not self.affinity_resolver.is_loaded():
            try:
                await self.affinity_resolver.load()
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("Affinity resolver load failed (non-fatal): %s", str(e), exc_info=True)
                return None
        
        try:
            return await self.affinity_resolver.resolve(
                entity_name=entity_name,
                query=query,
                context=context,
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning("Entity affinity resolution failed (non-fatal): %s", str(e), exc_info=True)
            return None

    @staticmethod
    def _system_default_model() -> str:
        """Return the system default model for unaffiliated queries."""
        return "qwen3-1.7b"

    # ── Model name resolution ──────────────────────────────────────────
    async def _resolve_ollama_model(self, model_name: str) -> str:
        """Resolve config model name to an Ollama tag.

        Checks available Ollama models and finds the best match.
        Falls back to the original model name if resolution fails.
        """
        try:
            import httpx2 as httpx
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.OLLAMA_URL}/api/tags")
                if r.status_code == 200:
                    data = r.json()
                    available = [m["name"] for m in data.get("models", [])]
                    if model_name in available:
                        return model_name
                    name_lower = model_name.lower().split("-")[0].split("_")[0]
                    for tag in available:
                        if tag.lower().startswith(name_lower):
                            return tag
                    if available:
                        return available[0]
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.debug(f"Ollama model resolution failed for {model_name}: {e}", exc_info=True)
            # Resolve to original as fallback
        return model_name

    # ── Circuit Breaker Integration ──────────────────────────────────

    def _get_provider_timeout(self, provider) -> float:
        """Per-provider timeout with MagicMock-safe type check."""
        try:
            timeout = provider.config.timeout_seconds
        except AttributeError:
            timeout = provider.config.get("timeout_seconds", 130.0)
        if isinstance(timeout, (int, float)):
            return float(timeout)
        return 130.0

    @property
    def _cloud_providers(self) -> set:
        """Set of cloud provider names for sovereignty tracking."""
        return {"google", "openrouter", "opencode-zen", "cline"}

    def _is_cloud_provider(self, provider) -> bool:
        """Check if a provider is a cloud provider."""
        return provider.name in self._cloud_providers

    # [id-soft: vet-046] BSP Culling — O(1) pre-check skips broken providers
    async def _precheck_provider(self, provider, model_name: str) -> bool:
        """BSP-style pre-check: is this provider worth trying?
        
        [id-soft: vet-046] BSP Culling — single O(1) circuit breaker check
        skips entire provider subtree, adapted from Doom's static BSP tree
        to dynamic provider health state.

        Checks (cheapest first):
        1. Circuit breaker state — if OPEN, skip instantly (O(1) dict lookup)
        2. Provider availability — does the server respond?

        FIX T2.2: Check breaker by provider.name directly, not via model_name
        indirection through _model_provider_map. The old code called
        is_available(model_name) which used _model_provider_map.get(model_name)
        to find the provider — if the mapping was missing it always returned True.
        """
        # Circuit breaker is the cheapest check — single dict lookup by provider name
        if self._health_monitor:
            breaker = self._health_monitor._breakers.get(provider.name)
            if breaker and not breaker.is_available:
                return False

        # Provider self-health check (sync or async)
        if hasattr(provider, 'is_available'):
            try:
                if inspect.iscoroutinefunction(provider.is_available):
                    if not await provider.is_available():
                        return False
                else:
                    if not provider.is_available():
                        return False
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("Provider %s availability check failed: %s", getattr(provider, 'name', '?'), e)
                return False

        return True

    def _record_provider_failure(self, provider, model_name: str, trace_id: Optional[str] = None):
        """Record provider failure with HealthMonitor and observability."""
        if self._health_monitor:
            self._health_monitor.record_failure(model_name)
        
        # Record failure in latency tracker (latency is 0 or estimated)
        tracker.record(
            provider=provider.name,
            model=model_name,
            latency_ms=0.0,
            status="failure",
            trace_id=trace_id
        )
        
        if trace_id:
            try:
                from omega.observability import get_engine, EventType
                get_engine().log_event(
                    EventType.BACKEND_FALLBACK, trace_id,
                    {"provider": provider.name, "model": model_name,
                     "event": "provider_failed"}
                )
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("Failed to log BACKEND_FALLBACK event for provider %s: %s",
                                getattr(provider, 'name', '?'), e)

    def _update_active_set(self, provider_name: str) -> None:
        """Maintain tiered fixed-size active sets of successful providers (LRU).

        [id-soft: vet-055] Fixed-Size Active Set — 32-entry clip range.
        [hardening-p6] Sovereignty-Tiered — local and cloud providers are
        tracked in separate sets to prevent sovereignty drift (Mandate 7).
        A known-good local provider is always preferred over a known-good
        cloud provider, regardless of recency.
        """
        is_cloud = self._is_cloud_provider_name(provider_name)
        target = self._cloud_active if is_cloud else self._local_active

        if provider_name in target:
            target.remove(provider_name)
        target.insert(0, provider_name)
        if len(target) > 32:
            target.pop()

    def _is_cloud_provider_name(self, name: str) -> bool:
        """Check if a provider name is a cloud provider."""
        return name in self._cloud_providers

    def _fallback_response(self, model_name: str, system_prompt: str, user_query: str) -> str:
        """Generate a fallback response when all providers fail.
        
        Returns a helpful message indicating that no inference backend is available
        and instructions for enabling local or cloud inference.
        """
        return (
            f"⚠️ no inference backend is running for model '{model_name}'.\n\n"
            "To use the Omega Engine, please:\n"
            "1. Start a local inference backend (llama-cpp-python, LM Studio, or Ollama), OR\n"
            "2. Configure cloud credentials (Google AI Studio, OpenRouter, GitHub Copilot), OR\n"
            "3. Check logs for provider errors: omega-hub is attempting to fallback through the provider fabric.\n\n"
            "System prompt: {}\nUser query: {}".format(
                system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt,
                user_query[:100] + "..." if len(user_query) > 100 else user_query,
            )
        )

    async def generate(
        self, model_name: str, system_prompt: str, user_query: str,
        temperature: float = 0.7, max_tokens: int = 1024, trace_id: Optional[str] = None,
        session_id: Optional[str] = None, entity_name: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
    ) -> 'GenerateResult':
        """Iterate provider fabric with circuit breaker protection.
        
        [id-soft: vet-055] Fixed-Size Active Set — first try the 32 most recently
        successful providers before falling back to the full fabric.
        """
        # ── Sovereign Sampling Layer ──────────────────────────────────────────
        # [Sovereign Sampling] Intervention for Gemma 4 31B to eliminate repetition loops.
        # Target: gemma-4-31b-it (or any model identified as Gemma 4 31B)
        if "gemma-4-31b" in model_name.lower():
            # Increase temperature and repetition penalty to escape local probability peaks.
            temperature = max(temperature, 0.85)
            repetition_penalty = max(repetition_penalty, 1.2)
            
            # Verified token IDs for ' la' and 'la-' from COGNITIVE_STABILITY_PLAN.md
            # These are used to mathematically forbid the model from selecting them.
            GEMMA_LA_TOKENS = {
                759: -10.0,    # ' la'
                2149: -10.0,   # 'la-'
                236772: -10.0, # 'la-' (variant)
            }
            if logit_bias is None:
                logit_bias = GEMMA_LA_TOKENS
            else:
                logit_bias.update(GEMMA_LA_TOKENS)
        
        last_exception = None
        errors = []
        success_provider = None
        _latency_ms = 0.0  # [M22] Initialize before loop for fallback path
        # ── Provider Selection Layer ──────────────────────────────────────────
        # Use the ProviderSelector to reorder the fabric based on query content (PII)
        # and provider health. This ensures we try the most suitable providers first.
        ordered_providers = await self.provider_selector.get_ordered_providers(model_name, user_query)
        if not ordered_providers:
            raise ProviderUnavailableError(message=f"No providers available for model {model_name}")

        # [M8 Zero Telemetry] WARP Proxy Pool injection for opencode-zen
        # If proxy_pool is configured, inject socks5h:// proxy URL into the
        # opencode-zen provider's extra config before the provider loop.
        # This ensures DNS is resolved through the WARP exit node (socks5h://),
        # preventing local DNS leaks per the Sovereign Security Protocol.
        proxy_pool = getattr(self, 'proxy_pool', None)
        if proxy_pool is not None:
            for provider in ordered_providers:
                if provider.name == "opencode-zen" and hasattr(provider, 'config'):
                    try:
                        proxy_url = await proxy_pool.get_proxy_url()
                        provider.config.extra["proxy_url"] = proxy_url
                        logger.debug("WARP proxy injected for opencode-zen: %s", proxy_url)
                    except Exception as exc:
                        logger.warning("WARP proxy injection failed for opencode-zen: %s", exc)

        for provider in ordered_providers:
            logger.debug(f"Trying provider: {provider.name}")
            # Step 1: BSP-style pre-check — fast fail if circuit is OPEN
            if not await self._precheck_provider(provider, model_name):
                errors.append(f"{provider.name}: culled by precheck")
                continue
            
            # Step 1.5: Sovereign Budget Gate (Shatter-Glass Phase 3)
            # Only check budget for cloud providers
            if self._is_cloud_provider(provider) and entity_name:
                if not await BudgetGate.check_budget(entity_name, trace_id or "unknown"):
                    errors.append(f"{provider.name}: cloud budget exhausted for {entity_name}")
                    continue
            
            # Rate Limiting: Check if provider has available tokens
            if not await self.rate_limiter.check_limit(provider.name):
                errors.append(f"{provider.name}: rate limit exceeded")
                continue
            
            # Step 2: Execute with Hardware Lock and breaker protection
            timeout = self._get_provider_timeout(provider)
            breaker = None  # Initialize for else-clause scope
            
            # Use Hardware Lock to prevent resource contention
            weight = self.get_model_weight(model_name)
            spec = self.get_model_spec(model_name)
            
            try:
                async with self.resource_guard.lock(weight=weight, model_spec=spec):
                    with anyio.move_on_after(timeout) as cancel_scope:
                        # [M22 Response Provenance] Start latency measurement
                        _start_time = time.monotonic()
                        
                        # Use HealthMonitor's breaker if available, otherwise direct call.
                        if self._health_monitor:
                            breaker = self._health_monitor._breakers.get(provider.name)
                            if breaker:
                                async def _call_with_none_as_failure():
                                    r = await provider.generate(
                                        model_name, system_prompt, user_query,
                                        temperature, max_tokens, trace_id=trace_id,
                                        session_id=session_id,
                                        logit_bias=logit_bias,
                                        repetition_penalty=repetition_penalty,
                                    )
                                    if not r:
                                        raise TimeoutError(f"Provider {provider.name} returned empty response")
                                    return r
                                result = await breaker.call(_call_with_none_as_failure, trace_id=trace_id)
                            else:
                                result = await provider.generate(
                                    model_name, system_prompt, user_query,
                                    temperature, max_tokens, trace_id=trace_id,
                                    session_id=session_id,
                                    logit_bias=logit_bias,
                                    repetition_penalty=repetition_penalty,
                                )
                        else:
                            result = await provider.generate(
                                model_name, system_prompt, user_query,
                                temperature, max_tokens, trace_id=trace_id,
                                session_id=session_id,
                                logit_bias=logit_bias,
                                repetition_penalty=repetition_penalty,
                            )
                        
                        if result:
                            # [M22 Response Provenance] Record latency immediately after provider returns
                            _latency_ms = (time.monotonic() - _start_time) * 1000
                            if self._health_monitor:
                                self._health_monitor.record_success(model_name)
                            self._update_active_set(provider.name)
                            
                            # Record latency to time-series tracker
                            # [M22 Response Provenance] is_cloud passed for
                            # Sovereignty Gate tracking (P0-2). This ensures
                            # the MetricsDB receives accurate local/cloud ratio.
                            tracker.record(
                                provider=provider.name,
                                model=model_name,
                                latency_ms=_latency_ms,
                                status="success",
                                trace_id=trace_id,
                                is_cloud=self._is_cloud_provider(provider),
                            )
                            
                            success_provider = provider
                            
                            
                            # Sovereign Token Ledger Integration
                            # Capture actual usage from provider or estimate
                            # Note: In a full implementation, providers would return a structured response
                            # containing usage metadata. For now, we use the bridge's estimation.
                            tokens_in = len(system_prompt) // 4
                            tokens_out = len(result) // 4
                            
                            await TokenLedger().record_transaction(
                                trace_id=trace_id or "unknown",
                                entity=entity_name or "system",
                                tokens_in=tokens_in,
                                tokens_out=tokens_out,
                                provider_name=provider.name
                            )
                            
                            break
                        
                        if cancel_scope.cancelled_caught:
                            errors.append(f"{provider.name}: timed out ({timeout}s)")
                            self._record_provider_failure(provider, model_name, trace_id)
                            continue
            except CircuitOpenError:
                errors.append(f"{provider.name}: circuit OPEN")
                continue
            except TimeoutError as e:
                errors.append(f"{provider.name}: {e}")
                self._record_provider_failure(provider, model_name, trace_id)
                continue
            except Exception as e:
                last_exception = e
                logger.error(
                    "ModelGateway.generate: unexpected error from provider=%s trace=%s err=%s",
                    provider.name, trace_id, str(e), exc_info=True
                )
                errors.append(f"{provider.name}: {e}")
                self._record_provider_failure(provider, model_name, trace_id)
                continue

        
        if success_provider:
            # [Operation Deep-Siphon] ICS-F v1.0 Sprint 0: capture logprobs from provider.
            # Duck-typing: NativeGGUFProvider sets _last_logprobs after each generate().
            # Other providers don't have this attribute — getattr defaults to None.
            logprobs = getattr(success_provider, '_last_logprobs', None)
            return GenerateResult(
                text=result,
                provider_name=success_provider.name,
                is_cloud=self._is_cloud_provider(success_provider),
                logprobs=logprobs,
                latency_ms=_latency_ms,      # [M22] Actual latency from measurement
                model_used=model_name,        # [M22] Actual model that served
            )
        
# If all providers failed, propagate the last critical error if it exists
        if last_exception and isinstance(last_exception, (InferenceError, OmegaError)):
            logger.critical(f"All providers failed. Propagating last critical error: {last_exception}")
            raise last_exception

        logger.warning("All providers failed. Trace: %s | Errors: %s", trace_id, '; '.join(errors))
        return GenerateResult(
            text=self._fallback_response(model_name, system_prompt, user_query),
            provider_name="fallback",
            is_cloud=self._is_cloud_provider_name("fallback"),  # Derived from provider_name per M22
            latency_ms=_latency_ms,   # [M22] Report measured latency (0.0 if never reached a provider)
            model_used=model_name,    # [M22] Report the model that was requested
        )

    # ── Somatic State API (M20) ──────────────────────────────────────────
    
    def _get_native_gguf_provider(self) -> Optional['NativeGGUFProvider']:
        """Find the NativeGGUFProvider in the provider fabric."""
        for provider in self.providers:
            if isinstance(provider, NativeGGUFProvider):
                return provider
        return None

    async def save_state(self, state_id: str) -> bool:
        """Save the current model's somatic state (KV cache) to the USM.
        
        Delegates to the NativeGGUFProvider to capture bytes, then
        persists them via the Unified State Manager.
        
        Args:
            state_id: Unique identifier for the state snapshot.
            
        Returns:
            True if state was captured and saved successfully, False otherwise.
        """
        provider = self._get_native_gguf_provider()
        if provider is None:
            logger.warning("No NativeGGUFProvider available for save_state")
            return False
        
        try:
            # Capture raw bytes from the provider
            state_bytes = await provider.save_state()
            
            # Persist bytes in the USM
            # We use a specific namespace for somatic states
            usm_key = f"somatic:{state_id}"
            await self.usm.put(usm_key, state_bytes)
            
            logger.info(f"Somatic state saved to USM for {state_id}")
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to save somatic state {state_id} to USM: {e}")
            return False
    
    async def load_state(self, state_id: str) -> bool:
        """Load a somatic state (KV cache) from the USM into the current model.
        
        Delegates to the USM to retrieve bytes, then pushes them to the provider.
        
        Args:
            state_id: Unique identifier for the state snapshot.
            
        Returns:
            True if state was loaded successfully, False otherwise.
        """
        provider = self._get_native_gguf_provider()
        if provider is None:
            logger.warning("No NativeGGUFProvider available for load_state")
            return False
        
        try:
            # Retrieve bytes from the USM
            usm_key = f"somatic:{state_id}"
            state_bytes = await self.usm.get(usm_key)
            
            if state_bytes is None:
                logger.warning(f"No somatic state found in USM for {state_id}")
                return False
            
            # Push bytes to the provider
            return await provider.load_state(state_bytes)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to load somatic state {state_id} from USM: {e}")
            return False



    async def _call_provider_with_resilience(self, provider, model_name, system_prompt, user_query, temperature, max_tokens, trace_id=None):
        """Wrapper to apply the OpenRouter retry policy."""
        @openrouter_retry_policy
        async def _do_call():
            try:
                return await provider.generate(model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id)
            except (OmegaError, RuntimeError, OSError) as e:
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
        import httpx2 as httpx

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
        import httpx2 as httpx

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
        import httpx2 as httpx

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
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"ONNX inference failed: {e}", exc_info=True)
            return None

    def is_onnx_available(self) -> bool:
        """Check if ONNX Runtime is installed and usable."""
        try:
            import onnxruntime as ort
            return "CPUExecutionProvider" in ort.get_available_providers()
        except ImportError:
            return False

    def get_provider_for_entity(self, entity_name: str):
        """Get the provider instance that was last used for an entity.
        
        This is used for somatic state capture (M20).
        """
        # The active provider is tracked in the active set
        # For now, return the first NativeGGUFProvider if available
        for provider in self.providers:
            if provider.__class__.__name__ == "NativeGGUFProvider":
                return provider
        return None

    # ── Fallback ──────────────────────────────────────────────────────
    async def embed(self, text: str) -> List[float]:
        """Generate a vector embedding for the given text.
        
        Currently uses a mock implementation. In a full implementation, this 
        would route to a local embedding model (e.g., SentenceTransformers) 
        or a cloud provider.
        """
        # Mock embedding: 384-dim vector (standard for MiniLM)
        # In production, this would call a real embedding model.
        import numpy as np
        return np.random.rand(384).tolist()

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
