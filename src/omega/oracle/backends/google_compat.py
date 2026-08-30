# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 GoogleCompatProvider — Gemma 4 Week 1 Step 2
# ⬡ OMEGA ⬡ N6 ⬡ trc_google_compat ⬡ v0.1.0 ⬡ 2026-07-19
#
# Google AI Studio / Vertex AI compatible provider with Gemma 4 thinking support.
# Heritage: [heritage: pi-2026] Gemma 4 Thinking Config (Pi PR #2903) — binary MINIMAL/HIGH + regex /gemma-?4/i
# Heritage: [heritage: litellm-2024] Capability flag pattern for model registry

import logging
import re
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from ..capability_matrix import (
    CapabilityMatrix,
    ModelCapability,
    ProviderConfig,
    get_capability_matrix,
)
from omega.errors import (
    OmegaError,
    ProviderError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderSafetyError,
)

logger = logging.getLogger(__name__)


class GoogleCompatProvider:
    """Google AI Studio / Vertex AI compatible provider with Gemma 4 thinking support.

    Handles:
    - Binary thinking config (MINIMAL/HIGH) per Pi PR #2903
    - Model ID normalization (strip google/ prefix, handle :free suffix)
    - Thinking token extraction and provenance tracking (M22)
    - Rate limit header parsing
    - Both AI Studio (v1beta) and Vertex AI endpoints
    """

    # Gemma 4 detection regex from Pi PR #2903
    GEMMA4_DETECTION_REGEX = re.compile(r"gemma-?4", re.IGNORECASE)

    # Thinking level mapping per capability matrix
    THINKING_LEVEL_MAP = {
        "minimal": "MINIMAL",
        "low": "MINIMAL",
        "standard": "MINIMAL",
        "medium": "HIGH",
        "high": "HIGH",
        "deep": "HIGH",
        "xhigh": "HIGH",
        "none": None,  # Omit thinking_config entirely
    }

    def __init__(
        self,
        name: str = "google-compat",
        config: Optional[Dict[str, Any]] = None,
        capability_matrix: Optional[CapabilityMatrix] = None,
    ):
        self.name = name
        self.config = config or {}
        self.capability_matrix = capability_matrix or get_capability_matrix()
        self.capability_matrix.load()

        # Resolve API key from vault or env
        self.api_key = self._resolve_api_key()

        # Provider config from capability matrix
        self.provider_config: Optional[ProviderConfig] = self.capability_matrix.get_provider_config(
            "google-ai-studio"
        )

        # HTTP client (lazy init for connection pooling)
        self._client: Optional[httpx.AsyncClient] = None

    def _resolve_api_key(self) -> str:
        """Resolve Google API key from vault or environment."""
        try:
            from omega.vault import VaultCore

            vault = VaultCore()
            vault._load_sync()
            cred = vault._credentials.get("google:api_key")
            return cred.encrypted_blob if cred else ""
        except Exception:
            return self.config.get("api_key", "") or ""

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def is_available(self) -> bool:
        """Check if provider is available (has API key)."""
        return bool(self.api_key)

    def _resolve_model_id(self, model_id: str, provider_id: str = "google-ai-studio") -> str:
        """Normalize model ID for the target provider."""
        return self.capability_matrix.normalize_model_id(model_id, provider_id)

    def _get_capability(self, model_id: str) -> Optional[ModelCapability]:
        """Get capability for model (fuzzy match with detection regex)."""
        return self.capability_matrix.get_by_fuzzy_match(model_id)

    def _build_thinking_config(
        self, capability: ModelCapability, thinking_effort: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Build thinking_config per provider schema.

        Per Pi PR #2903, Gemma 4 uses binary MINIMAL/HIGH levels.
        Canonical efforts map as:
          - minimal/low/standard → MINIMAL
          - medium/high/deep/xhigh → HIGH
          - none → omit thinking_config
        """
        if not capability or not capability.thinking_config:
            return None

        thinking_config = capability.thinking_config

        # Determine effective thinking level
        if thinking_effort is None:
            thinking_effort = "standard"  # Default

        # Map canonical effort to provider enum
        provider_level = self.THINKING_LEVEL_MAP.get(thinking_effort.lower())

        # If explicit mapping exists in capability, use that
        if thinking_config.thinking_mapping:
            provider_level = thinking_config.thinking_mapping.get(
                thinking_effort.lower(), provider_level
            )

        if provider_level is None:
            # thinking_effort == "none" → omit thinking_config
            return None

        # Validate against supported levels
        supported = thinking_config.supported_levels
        if supported and provider_level not in supported:
            # Clamp to nearest supported level
            if provider_level == "HIGH" and "HIGH" not in supported:
                provider_level = "MINIMAL"
                logger.warning(
                    f"Clamped HIGH → MINIMAL for {capability.model_id} (supports: {supported})"
                )
            elif provider_level == "MINIMAL" and "MINIMAL" not in supported:
                provider_level = "HIGH"
                logger.warning(
                    f"Clamped MINIMAL → HIGH for {capability.model_id} (supports: {supported})"
                )

        # Build provider-specific thinking config
        if thinking_config.thinking_schema == "thinking_level":
            return {"thinkingConfig": {"thinkingLevel": provider_level}}
        elif thinking_config.thinking_schema == "thinking_budget":
            # Vertex AI Gemini 2.5 uses budget
            budget_map = {"MINIMAL": 0, "HIGH": 8192}
            return {"thinkingConfig": {"thinkingBudget": budget_map.get(provider_level, 0)}}

        return None

    def _extract_thinking_from_response(self, data: Dict[str, Any]) -> Tuple[str, int]:
        """Extract thinking tokens and content from Google API response.

        Returns:
            Tuple of (full_text, thoughts_token_count)
        """
        thoughts_token_count = 0
        full_text = ""

        candidates = data.get("candidates", [])
        if not candidates:
            return "", 0

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        for part in parts:
            if "text" in part:
                full_text += part["text"]
            # Check for thinking metadata
            if "thought" in part and part["thought"]:
                # This is a thinking part
                thoughts_token_count += len(part["text"].split())  # Approximate

        # Also check usageMetadata for thoughtsTokenCount (Google returns this)
        usage = data.get("usageMetadata", {})
        if "thoughtsTokenCount" in usage:
            thoughts_token_count = usage["thoughtsTokenCount"]

        return full_text.strip(), thoughts_token_count

    def _parse_rate_limit_headers(self, headers: httpx.Headers) -> Dict[str, Any]:
        """Parse Google rate limit headers."""
        if not self.provider_config:
            return {}

        rate_headers = self.provider_config.rate_limit_headers
        return {
            "remaining_requests": headers.get(
                rate_headers.get("remaining_requests", "x-ratelimit-remaining-requests")
            ),
            "remaining_tokens": headers.get(
                rate_headers.get("remaining_tokens", "x-ratelimit-remaining-tokens")
            ),
            "retry_after": headers.get(rate_headers.get("retry_after", "retry-after")),
        }

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
        thinking_effort: Optional[str] = None,
        include_thoughts: bool = True,
    ) -> Dict[str, Any]:
        """Generate response from Google AI Studio / Vertex AI.

        Returns dict with:
            - text: Generated text
            - provider_name: Actual provider that served the response
            - is_cloud: True (Google AI Studio is cloud)
            - latency_ms: Request latency
            - model_used: Model ID used
            - thoughts_token_count: Number of thinking tokens (M22 provenance)
        """
        if not self.api_key:
            raise ProviderAuthError(
                provider="google", message="No Google API key available", trace_id=trace_id
            )

        # Resolve model ID and capability
        normalized_model = self._resolve_model_id(model, "google-ai-studio")
        capability = self._get_capability(model)

        # Build thinking config
        thinking_config = self._build_thinking_config(capability, thinking_effort)

        # Build request payload
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "repetitionPenalty": repetition_penalty,
            },
        }

        if logit_bias:
            payload["generationConfig"]["logitBias"] = logit_bias

        if thinking_config:
            payload["generationConfig"]["thinkingConfig"] = thinking_config.get(
                "thinkingConfig", {}
            )

        # Add includeThoughts for thinking extraction
        if include_thoughts and capability and capability.capabilities.get("supports_thinking"):
            payload["generationConfig"]["includeThoughts"] = True

        # Determine endpoint
        base_url = (
            self.provider_config.base_url
            if self.provider_config
            else "https://generativelanguage.googleapis.com/v1beta"
        )
        url = f"{base_url}/models/{normalized_model}:generateContent"

        start_time = time.perf_counter()

        try:
            client = await self._get_client()
            response = await client.post(
                url, json=payload, headers={"x-goog-api-key": self.api_key}
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Parse rate limit headers
            rate_info = self._parse_rate_limit_headers(response.headers)

            # Handle errors
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="google",
                    message="Google API quota exceeded",
                    status_code=429,
                    trace_id=trace_id,
                )
            if response.status_code in (401, 403):
                raise ProviderAuthError(
                    provider="google",
                    message="Google API authentication failed",
                    status_code=response.status_code,
                    trace_id=trace_id,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="google",
                    message="Google API server error",
                    status_code=response.status_code,
                    trace_id=trace_id,
                )

            response.raise_for_status()
            data = response.json()

            # Handle safety blocks
            candidates = data.get("candidates", [])
            if candidates and "finishReason" in candidates[0]:
                finish_reason = candidates[0]["finishReason"]
                if finish_reason == "SAFETY":
                    raise ProviderSafetyError(
                        provider="google",
                        message="Response blocked by Google safety filters",
                        trace_id=trace_id,
                    )

            # Extract text and thinking tokens
            text, thoughts_token_count = self._extract_thinking_from_response(data)

            if not text:
                return {
                    "text": "",
                    "provider_name": "google-ai-studio",
                    "is_cloud": True,
                    "latency_ms": latency_ms,
                    "model_used": normalized_model,
                    "thoughts_token_count": thoughts_token_count,
                    "rate_limit": rate_info,
                }

            return {
                "text": text,
                "provider_name": "google-ai-studio",
                "is_cloud": True,
                "latency_ms": latency_ms,
                "model_used": normalized_model,
                "thoughts_token_count": thoughts_token_count,
                "rate_limit": rate_info,
            }

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(
                provider="google",
                message=f"Google API timeout: {e}",
                trace_id=trace_id,
                raw_error=e,
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                provider="google",
                message=f"Google API HTTP error: {e}",
                status_code=e.response.status_code,
                trace_id=trace_id,
                raw_error=e,
            )
        except OmegaError:
            raise
        except Exception as e:
            logger.error(f"Unexpected Google API failure: {e}", exc_info=True)
            raise ProviderError(
                provider="google",
                message=f"Unexpected Google API failure: {e}",
                trace_id=trace_id,
                raw_error=e,
            ) from e

    async def generate_stream(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
        thinking_effort: Optional[str] = None,
        include_thoughts: bool = True,
    ):
        """Streaming generation (yields chunks).

        Note: Streaming thinking extraction requires chunk accumulation.
        For now, delegates to non-streaming and yields single chunk.
        """
        result = await self.generate(
            model=model,
            system_prompt=system_prompt,
            user_query=user_query,
            temperature=temperature,
            max_tokens=max_tokens,
            trace_id=trace_id,
            session_id=session_id,
            logit_bias=logit_bias,
            repetition_penalty=repetition_penalty,
            thinking_effort=thinking_effort,
            include_thoughts=include_thoughts,
        )
        yield result
