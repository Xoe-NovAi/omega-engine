# AP: AP-ORACLE-STREAM-HANDLER-v1.0.0
# 🔱 Oracle Stream Handler — Mid-Stream Quota Exhaustion Detection
# Detects quota exhaustion mid-stream via SSE error frames and triggers fallback
# Implements resilient streaming with automatic provider failover on quota events

"""
Stream Handler for Oracle Provider Fabric

Detects quota exhaustion mid-stream during LLM generation by monitoring
Server-Sent Events (SSE) for error events indicating rate limit or quota
exceeded conditions. When detected, triggers automatic fallback to the next
provider in the cascade chain.

Supports detection of:
- OpenRouter 402 (quota exceeded) vs 429 (rate limit) in SSE frames
- Anthropic quota exceeded events in stream
- Google Gemini quota events in stream
- Generic rate limit error patterns in streaming responses

Features:
- Real-time SSE frame parsing
- Quota-exhausted vs rate-limit distinction
- Automatic fallback triggering
- Retry-After header respect
- Observability integration
"""

from __future__ import annotations

import json
import re
import time
from typing import AsyncIterator, Dict, Optional, Tuple

from omega.errors import OmegaError, ProviderRateLimitError
from omega.observability import get_engine, EventType

logger = __import__("logging").getLogger("omega.stream_handler")


class StreamQuotaError(OmegaError):
    """Raised when quota exhaustion is detected mid-stream."""
    pass


class StreamRateLimitError(OmegaError):
    """Raised when rate limit is hit mid-stream."""
    pass


class StreamHandler:
    """
    Handles streaming LLM responses with mid-stream quota/rate limit detection.
    
    Wraps provider streams to detect quota exhaustion or rate limiting
    mid-stream and convert them to exceptions that trigger fallback.
    
    Detects:
    - SSE error frames with quota exceeded indicators
    - HTTP 402/429 status codes in streaming responses
    - Error messages in streaming chunks
    - Retry-After headers for cooldown calculation
    
    When quota exhaustion is detected:
    - Raises StreamQuotaError with quota recovery time
    - When rate limit detected:
    - Raises StreamRateLimitError with retry delay
    """

    def __init__(self):
        self._logger = logger
        
        # Patterns for detecting quota exhaustion in streaming content
        self._quota_patterns = [
            re.compile(r"monthly\.quota|daily\.limit|out\.of\.credits|quota\.exceeded", re.I),
            re.compile(r"insufficient\.credit|billing|payment|plan\.limit", re.I),
            re.compile(r"'quota'|'credits'", re.I),
        ]
        
        # Patterns for rate limit detection
        self._rate_limit_patterns = [
            re.compile(r"rate\s*limit|too\s*many\s*requests|throttl", re.I),
            re.compile(r"429|rate\s*limited", re.I),
        ]

    async def handle_stream(
        self,
        provider_name: str,
        stream: AsyncIterator[Dict[str, Any]],
        model_name: str,
        trace_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Process a streaming response, detecting quota/rate limit events mid-stream.
        
        Args:
            provider_name: Name of the provider generating the stream
            stream: Async iterator yielding response chunks/dicts
            model_name: Model being used for generation
            trace_id: Optional trace ID for observability
            
        Yields:
            Text chunks from the stream
            
        Raises:
            StreamQuotaError: When quota exhaustion is detected mid-stream
            StreamRateLimitError: When rate limit is hit mid-stream
            OmegaError: For other streaming errors
        """
        self._logger.debug(f"Starting stream handler for {provider_name}")
        
        try:
            async for chunk in stream:
                # Handle different stream formats
                text_chunk = self._extract_text_chunk(chunk)
                if text_chunk:
                    yield text_chunk
                
                # Check for quota/rate limit events in the chunk
                await self._check_for_quota_events(
                    provider_name, 
                    chunk, 
                    model_name, 
                    trace_id
                )
                
        except StreamQuotaError:
            # Re-raise quota errors to trigger fallback
            raise
        except StreamRateLimitError:
            # Re-raise rate limit errors to trigger fallback
            raise
        except Exception as e:
            self._logger.error(f"Stream handler error for {provider_name}: {e}")
            # Convert to appropriate stream error if it looks like quota/rate limit
            error_str = str(e).lower()
            if any(p.search(error_str) for p in self._quota_patterns):
                raise StreamQuotaError(f"Quota exceeded in stream: {e}") from e
            elif any(p.search(error_str) for p in self._rate_limit_patterns):
                raise StreamRateLimitError(f"Rate limit in stream: {e}") from e
            else:
                raise  # Re-raise original error

    def _extract_text_chunk(self, chunk: Any) -> Optional[str]:
        """
        Extract text content from a stream chunk.
        
        Handles various streaming formats:
        - Plain text strings
        - Dict with 'text' or 'content' keys
        - OpenAI-style streaming chunks
        - Anthropic-style streaming events
        """
        if isinstance(chunk, str):
            return chunk
        
        if isinstance(chunk, dict):
            # OpenAI-style: {"choices": [{"delta": {"content": "..."}}]}
            if "choices" in chunk and isinstance(chunk["choices"], list):
                for choice in chunk["choices"]:
                    if isinstance(choice, dict) and "delta" in choice:
                        delta = choice["delta"]
                        if isinstance(delta, dict) and "content" in delta:
                            return delta["content"]
            
            # Anthropic-style: {"type": "content_block_delta", "delta": {"text": "..."}}
            if chunk.get("type") == "content_block_delta":
                delta = chunk.get("delta", {})
                if isinstance(delta, dict) and "text" in delta:
                    return delta["text"]
            
            # Generic text fields
            for key in ["text", "content", "message", "response"]:
                if key in chunk and isinstance(chunk[key], str):
                    return chunk[key]
            
            # SSE format: check for data field
            if "data" in chunk:
                data = chunk["data"]
                if isinstance(data, str):
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(data)
                        return self._extract_text_chunk(parsed)
                    except json.JSONDecodeError:
                        # Return raw data if not JSON
                        return data
                elif isinstance(data, dict):
                    return self._extract_text_chunk(data)
        
        return None

    async def _check_for_quota_events(
        self,
        provider_name: str,
        chunk: Any,
        model_name: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """
        Check a stream chunk for quota or rate limit events.
        
        Raises appropriate exceptions when detected.
        """
        # Convert chunk to string for pattern matching
        chunk_str = json.dumps(chunk) if not isinstance(chunk, str) else chunk
        chunk_str_lower = chunk_str.lower()
        
        # Check for SSE error events (OpenRouter, Anthropic style)
        if isinstance(chunk, dict):
            # OpenRouter SSE error: {"type": "error", "error": {"type": "rate_limit_error", ...}}
            if chunk.get("type") == "error":
                error_info = chunk.get("error", {})
                error_type = error_info.get("type", "").lower()
                error_code = error_info.get("code")
                
                # OpenRouter specific: rate_limit_error vs quota_exceeded
                if error_type == "rate_limit_error":
                    # Check if it's actually quota (402) vs rate limit (429)
                    if error_code == 402:
                        await self._handle_quota_event(
                            provider_name, 
                            "OpenRouter quota exceeded (402)", 
                            chunk,
                            model_name,
                            trace_id
                        )
                    elif error_code == 429:
                        await self._handle_rate_limit_event(
                            provider_name,
                            "OpenRouter rate limit (429)",
                            chunk,
                            model_name,
                            trace_id
                        )
            
            # Anthropic style: look for error in delta or event type
            if chunk.get("type") == "error" or chunk.get("error"):
                error_info = chunk.get("error", chunk)
                error_msg = str(error_info.get("message", ""))
                if self._matches_quota_pattern(error_msg):
                    await self._handle_quota_event(
                        provider_name,
                        f"Anthropic quota exceeded: {error_msg}",
                        chunk,
                        model_name,
                        trace_id
                    )
                elif self._matches_rate_limit_pattern(error_msg):
                    await self._handle_rate_limit_event(
                        provider_name,
                        f"Anthropic rate limit: {error_msg}",
                        chunk,
                        model_name,
                        trace_id
                    )
        
        # Check for quota/rate limit patterns in raw chunk string
        if self._matches_quota_pattern(chunk_str):
            await self._handle_quota_event(
                provider_name,
                "Quota exceeded detected in stream",
                chunk,
                model_name,
                trace_id
            )
        elif self._matches_rate_limit_pattern(chunk_str):
            await self._handle_rate_limit_event(
                provider_name,
                "Rate limit detected in stream",
                chunk,
                model_name,
                trace_id
            )

    def _matches_quota_pattern(self, text: str) -> bool:
        """Check if text matches quota exhaustion patterns."""
        return any(pattern.search(text) for pattern in self._quota_patterns)

    def _matches_rate_limit_pattern(self, text: str) -> bool:
        """Check if text matches rate limit patterns."""
        return any(pattern.search(text) for pattern in self._rate_limit_patterns)

    async def _handle_quota_event(
        self,
        provider_name: str,
        reason: str,
        chunk: Any,
        model_name: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """
        Handle a quota exceeded event mid-stream.
        
        Extracts recovery time and raises StreamQuotaError.
        """
        self._logger.warning(f"Quota exceeded mid-stream for {provider_name}: {reason}")
        
        # Try to extract recovery time from chunk
        retry_after = self._extract_retry_after(chunk)
        
        # Record observability event
        try:
            engine = get_engine()
            engine.log_event(
                EventType.BACKEND_FALLBACK,
                trace_id or "unknown",
                {
                    "provider": provider_name,
                    "event": "quota_exceeded_midstream",
                    "reason": reason,
                    "retry_after_seconds": retry_after,
                    "model": model_name,
                }
            )
        except Exception:
            pass  # Observability is best-effort
        
        # Raise quota error
        raise StreamQuotaError(
            f"Quota exceeded mid-stream for {provider_name}: {reason}"
        )

    async def _handle_rate_limit_event(
        self,
        provider_name: str,
        reason: str,
        chunk: Any,
        model_name: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """
        Handle a rate limit event mid-stream.
        
        Extracts retry delay and raises StreamRateLimitError.
        """
        self._logger.warning(f"Rate limit hit mid-stream for {provider_name}: {reason}")
        
        # Try to extract retry delay from chunk
        retry_after = self._extract_retry_after(chunk)
        
        # Record observability event
        try:
            engine = get_engine()
            engine.log_event(
                EventType.BACKEND_FALLBACK,
                trace_id or "unknown",
                {
                    "provider": provider_name,
                    "event": "rate_limit_midstream",
                    "reason": reason,
                    "retry_after_seconds": retry_after,
                    "model": model_name,
                }
            )
        except Exception:
            pass  # Observability is best-effort
        
        # Raise rate limit error
        raise StreamRateLimitError(
            f"Rate limit hit mid-stream for {provider_name}: {reason}"
        )

    def _extract_retry_after(self, chunk: Any) -> Optional[float]:
        """
        Extract retry-after value from a stream chunk.
        
        Looks for:
        - Retry-After header in chunk
        - retry_after field in JSON
        - Estimated delay from error messages
        
        Returns seconds as float, or None if not found.
        """
        # Check for direct retry_after field
        if isinstance(chunk, dict):
            if "retry_after" in chunk:
                try:
                    return float(chunk["retry_after"])
                except (ValueError, TypeError):
                    pass
            
            # Check in headers
            if "headers" in chunk and isinstance(chunk["headers"], dict):
                headers = chunk["headers"]
                if "retry-after" in headers:
                    try:
                        return float(headers["retry-after"])
                    except (ValueError, TypeError):
                        pass
                if "Retry-After" in headers:
                    try:
                        return float(headers["Retry-After"])
                    except (ValueError, TypeError):
                        pass
            
            # Check in error info
            if "error" in chunk and isinstance(chunk["error"], dict):
                error = chunk["error"]
                if "retry_after" in error:
                    try:
                        return float(error["retry_after"])
                    except (ValueError, TypeError):
                        pass
        
        # Check for estimates in error messages
        if isinstance(chunk, str) or (isinstance(chunk, dict) and "message" in chunk):
            msg = chunk if isinstance(chunk, str) else chunk.get("message", "")
            msg_lower = msg.lower()
            
            # Look for patterns like "try again in 5 seconds" or "wait 60s"
            import re
            match = re.search(r"(?:try again|wait|retry).*?(\d+)\s*seconds?", msg_lower)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
            
            match = re.search(r"(?:try again|wait|retry).*?(\d+)\s*minutes?", msg_lower)
            if match:
                try:
                    return float(match.group(1)) * 60
                except ValueError:
                    pass
        
        return None

    def is_quota_error(self, error: Exception) -> bool:
        """Check if an error is a quota exhaustion error."""
        return isinstance(error, StreamQuotaError)

    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error."""
        return isinstance(error, StreamRateLimitError)

    def get_retry_delay(self, error: Exception) -> Optional[float]:
        """
        Extract retry delay from a stream error.
        
        Returns seconds to wait before retrying, or None if not applicable.
        """
        # This would require: error has retry_after attribute (we don't currently store it)
        # For now, return None - caller should use default backoff
        return None


# Global stream handler instance
_stream_handler: Optional[StreamHandler] = None


def get_stream_handler() -> StreamHandler:
    """Get or create the global stream handler instance."""
    global _stream_handler
    if _stream_handler is None:
        _stream_handler = StreamHandler()
    return _stream_handler