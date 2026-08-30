# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

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


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import time
import httpx2 as httpx
import json
from typing import Optional, Dict, List

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
        session_id: Optional[str] = None,
        logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0,
        stream: bool = False,
    ) -> str:
        """Send a chat completion request to the OpenAI-compatible API.

        [S3 B3] Streaming support with mid-stream error recovery.
        [S3 B4] Repetition Loop Detector (post-generation guard).
        [S3 B6] In-gateway fallback via OpenRouter `allow_fallbacks` flag.
        """
        api_key = self.resolve_current_api_key()
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
            "stream": stream,
        }
        if logit_bias:
            payload["logit_bias"] = logit_bias

        # [S3 B6] In-gateway fallback — OpenRouter native syntax
        # allow_fallbacks is a BOOLEAN per Final Order D205 correction
        allow_fallbacks = self.config.extra.get("allow_fallbacks", False)
        if allow_fallbacks:
            payload["allow_fallbacks"] = True

        # Support provider-specific payload overrides
        extra_payload = self.config.extra.get("payload", {})
        payload.update(extra_payload)

        url = f"{base_url.rstrip('/')}/v1/chat/completions"

        # [M8 Zero Telemetry] WARP proxy support via socks5h:// (remote DNS)
        # Configurable via provider extra.proxy_url or runtime injection
        proxy_url = self.config.extra.get("proxy_url")
        client_kwargs = {"timeout": self.config.timeout_seconds}
        if proxy_url:
            client_kwargs["proxy"] = proxy_url

        async with httpx.AsyncClient(**client_kwargs) as client:
            if not stream:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                choices = data.get("choices", [])
                if not choices:
                    raise ValueError(f"Provider {self.name} returned empty choices")

                content = choices[0].get("message", {}).get("content", "")
                if not content:
                    raise ValueError(f"Provider {self.name} returned empty content")

                result = content.strip()
            else:
                # [S3 B3] Streaming path with mid-stream error detection
                result = await self._stream_completion(client, url, payload, headers)

            # [S3 B4] Repetition Loop Detector inherited from RemoteProvider.generate()
            # (Called automatically in base class after _send_request returns)

            return result

    async def _stream_completion(
        self, client: "httpx.AsyncClient", url: str, payload: dict, headers: dict
    ) -> str:
        """Stream a chat completion, accumulating content.

        [S3 B3] On mid-stream `finish_reason: 'error'`, raises to trigger
        retry with assistant prefill (handled by base class retry loop).

        [P0-5 Nemotron Fix] Chunk-level timeout tracking:
        - Per-chunk timeout: 30s (configurable via provider config `streaming.chunk_timeout_ms`)
        - Total timeout: 300s (configurable via provider config `streaming.total_timeout_ms`)
        - Heartbeat logging for slow streams
        """
        # Streaming timeout configuration (provider-specific, defaults for Nemotron)
        chunk_timeout_ms = self.config.extra.get("streaming", {}).get("chunk_timeout_ms", 30000)
        total_timeout_ms = self.config.extra.get("streaming", {}).get("total_timeout_ms", 300000)
        chunk_timeout = chunk_timeout_ms / 1000.0
        total_timeout = total_timeout_ms / 1000.0

        chunks: List[str] = []
        chunk_count = 0
        total_start = time.monotonic()
        last_chunk_time = total_start

        async with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                # Check total timeout
                if time.monotonic() - total_start > total_timeout:
                    logger.error(
                        f"Provider {self.name} streaming total timeout ({total_timeout}s) exceeded"
                    )
                    raise RuntimeError(f"Streaming total timeout exceeded ({total_timeout}s)")

                # Check per-chunk timeout
                idle_ms = (time.monotonic() - last_chunk_time) * 1000
                if idle_ms > chunk_timeout_ms:
                    logger.warning(
                        f"Provider {self.name} stream stalled: {idle_ms:.0f}ms since last chunk "
                        f"(threshold: {chunk_timeout_ms}ms). Continuing..."
                    )
                    # Don't raise — Nemotron is slow but works. Just log and continue.

                line = line.strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except (ValueError, OSError):
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                content_piece = delta.get("content", "")
                if content_piece:
                    chunks.append(content_piece)
                    chunk_count += 1
                    last_chunk_time = time.monotonic()

                # [S3 B3] Mid-stream error detection
                finish_reason = choices[0].get("finish_reason")
                if finish_reason == "error":
                    raise RuntimeError(
                        f"Provider {self.name} stream terminated with finish_reason='error'"
                    )

        elapsed = time.monotonic() - total_start
        logger.info(
            f"Provider {self.name} stream completed: {chunk_count} chunks, "
            f"{len(''.join(chunks))} chars, {elapsed:.1f}s total"
        )
        return "".join(chunks).strip()

    @staticmethod
    def _detect_repetition_loop(content: str, model_name: str, threshold: int = 3) -> None:
        """[S3 B4] Repetition Loop Detector.

        Aborts if the last `threshold` chunks (of >=20 chars) are identical,
        indicating a degenerate generation loop. Raises RuntimeError to
        trigger retry via the base class loop.
        """
        if not content or len(content) < 60:
            return

        # Split into ~20-char windows and check last `threshold` are identical
        window = 20
        chunks = [
            content[i : i + window]
            for i in range(max(0, len(content) - window * threshold), len(content), window)
        ]
        if len(chunks) >= threshold and all(c == chunks[0] for c in chunks):
            raise RuntimeError(
                f"Provider {model_name} produced repetitive loop (identical tail detected)"
            )


# OpenAI provider factory removed per D-kal-164 sovereign dependency purge.
# create_openrouter_provider() also removed 2026-08-22: dead code (zero callers)
# carrying the same silent-default bug shape fixed in model_gateway._create_openrouter (M22).
