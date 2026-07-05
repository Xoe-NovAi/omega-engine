# 🔱 OpenAI-Compatible Provider — Universal Cloud Backend
# AP: AP-OPENAI-COMPAT-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ opus-4.6 ⬡ antigravity ⬡ trc_core ⬡ OPENAI-COMPAT
#
# Handles any API that speaks the OpenAI /v1/chat/completions protocol.
# This covers: OpenRouter, Azure OpenAI, Google Vertex AI (with Gemma),
# and any other compatible endpoint with explicit base_url configuration.
#
# The Gemma provider, OpenRouter provider, etc. are all instances of this
# class with different base_url and api_key values — no code duplication.
#
# NOTE: Cloud provider defaults (Groq, Together, SambaNova, OpenAI) were removed
# per D-kal-164 sovereign dependency purge. Only OpenRouter remains as
# the cloud fallback. Any other provider must be configured explicitly.

import logging
from typing import Optional, Dict

from .remote_provider import ProviderConfig, RemoteProvider

logger = logging.getLogger(__name__)


class OpenAICompatProvider(RemoteProvider):
    """Remote provider for any OpenAI-compatible chat completions API.

    Works with: OpenRouter, Vertex AI, Azure OpenAI, vLLM,
    and any /v1/chat/completions endpoint with explicit base_url.
    """

    async def _send_request(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float,
        max_tokens: int,
        trace_id: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
    ) -> str:
        """Send a chat completion request to the OpenAI-compatible API."""
        import httpx
        
        api_key = self.resolve_api_key()
        base_url = self.config.base_url
        if not base_url:
            raise ValueError(f"Provider {self.name} has no base_url configured")
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Support provider-specific headers (e.g., OpenRouter requires HTTP-Referer)
        extra_headers = self.config.extra.get("headers", {})
        headers.update(extra_headers)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "repetition_penalty": repetition_penalty,
            "stream": False,
        }
        if logit_bias:
            payload["logit_bias"] = logit_bias
        
        # Support provider-specific payload overrides
        extra_payload = self.config.extra.get("payload", {})
        payload.update(extra_payload)
        
        url = f"{base_url.rstrip('/')}/v1/chat/completions"

        # [M8 Zero Telemetry] WARP proxy support via socks5h:// (remote DNS)
        # Configurable via provider extra.proxy_url or runtime injection
        proxy_url = self.config.extra.get("proxy_url")
        client_kwargs = {"timeout": self.config.timeout_seconds}
        if proxy_url:
            client_kwargs["proxies"] = proxy_url
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            choices = data.get("choices", [])
            if not choices:
                raise ValueError(f"Provider {self.name} returned empty choices")
            
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError(f"Provider {self.name} returned empty content")
            
            return content.strip()


# ── Factory functions for common providers ─────────────────────────────

def create_openrouter_provider(config: ProviderConfig) -> OpenAICompatProvider:
    """Create an OpenRouter provider with correct base URL."""
    config.base_url = config.base_url or "https://openrouter.ai/api"
    config.extra.setdefault("headers", {}).update({
        "HTTP-Referer": "https://github.com/arcana-novai/omega-engine",
        "X-Title": "Omega Engine",
    })
    return OpenAICompatProvider(config)


# OpenAI provider factory removed per D-kal-164 sovereign dependency purge.
