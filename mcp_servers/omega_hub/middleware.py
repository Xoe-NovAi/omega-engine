# [id-soft: quake3-1999] Hub Middleware — netchan OOB-style rate limiting and error boundary for MCP transport

"""Omega Hub — Security middleware: rate limiting, request size limits, M9 error boundary.

AP: AP-OMEGA-HUB-MIDDLEWARE-v1.0.0

Extracted from server.py (Phase 1b — P1a-5). Provides middleware classes
for HTTP rate-limiting and payload size enforcement, the ``apply_security``
composer, and the ``m9_safe`` decorator for MCP tool error boundaries.

Dependencies:
  - threading (stdlib) — per-IP rate counter locking
  - starlette.middleware.cors (third-party) — CORS headers
  - starlette.responses (third-party) — HTTP 429/413 responses
  - functools (stdlib) — @wraps for decorator preservation
  - omega.observability (internal) — new_trace_id for error tracing
  - mcp.types (third-party) — CallToolResult, TextContent

Public API:
  RateLimitMiddleware         — In-memory per-IP rate limiter
  RequestSizeLimitMiddleware  — Content-length gate against OOM/DOS
  apply_security              — Apply all middleware to a Starlette app
  m9_safe                     — M9-compliant error-boundary decorator

Mandate compliance:
  - M9 (Error Integrity): m9_safe ensures no bare except: — all tools
    caught by this decorator return typed CallToolResult(isError=True)
  - M16 (Modularization): < 200 lines, single responsibility
"""

import json
import logging
import threading
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List

from mcp.types import CallToolResult, TextContent
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from omega.observability import new_trace_id

logger = logging.getLogger("omega.hub")


# ═══════════════════════════════════════════════════════════════════════════
# M9-COMPLIANT TOOL DECORATOR
# ═══════════════════════════════════════════════════════════════════════════

def m9_safe(tool_name: str):
    """Decorator: wrap an async MCP tool with M9-compliant error boundary.

    On exception, returns ``CallToolResult(content=[TextContent(...)], isError=True)``
    so MCP clients see ``isError=True``, not ``isError=False`` with
    an embedded ``"error"`` key.

    [H-A1-aligned: zero id-soft heritage, pure MCP spec pattern.]

    **Dependency footprint:**
      - ``functools.wraps`` (stdlib)
      - ``json`` (stdlib)
      - ``logging`` (stdlib)
      - ``mcp.types.CallToolResult``, ``mcp.types.TextContent``
      - ``omega.observability.new_trace_id``
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                trace_id = new_trace_id()
                logger.error("[%s] %s: %s", tool_name, trace_id, e)
                error_payload = json.dumps({
                    "error": str(e),
                    "trace_id": trace_id,
                    "tool": tool_name,
                }, indent=2)
                return CallToolResult(
                    content=[TextContent(type="text", text=error_payload)],
                    isError=True,
                )
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# RATE-LIMIT MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

class RateLimitMiddleware:
    """Simple in-memory rate limiting to prevent API abuse.

    Tracks requests per IP using a sliding 60-second window. If the
    per-minute limit is exceeded, returns HTTP 429.

    **Dependency footprint:**
      - ``threading.Lock`` (stdlib)
      - ``datetime.datetime`` (stdlib)
      - ``starlette.responses.Response`` (third-party)
    """

    def __init__(self, app, requests_per_minute: int = 100):
        self.app = app
        self.limit = requests_per_minute
        self._counts: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            client_ip = scope.get("client", ("unknown", 0))[0]
            now = datetime.now().timestamp()

            with self._lock:
                history = self._counts.get(client_ip, [])
                # Filter for last 60 seconds
                history = [t for t in history if now - t < 60]
                if len(history) >= self.limit:
                    response = Response("Too Many Requests", status_code=429)
                    await response(scope, receive, send)
                    return
                history.append(now)
                self._counts[client_ip] = history

        await self.app(scope, receive, send)


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST-SIZE MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

class RequestSizeLimitMiddleware:
    """Limits incoming request size to prevent OOM/DOS attacks.

    Checks the ``content-length`` header against a configurable maximum.

    **Dependency footprint:**
      - ``starlette.responses.Response`` (third-party)
    """

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            content_length = 0
            for header, value in scope.get("headers", []):
                if header == b"content-length":
                    content_length = int(value)
                    break
            if content_length > self.max_size:
                response = Response("Request too large", status_code=413)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY COMPOSER
# ═══════════════════════════════════════════════════════════════════════════

def apply_security(app):
    """Apply CORS, rate limiting, and size limits to a Starlette application.

    Call once at server startup on the underlying Starlette app.

    **Dependency footprint:**
      - ``starlette.middleware.cors.CORSMiddleware`` (third-party)
      - ``RateLimitMiddleware`` (this module)
      - ``RequestSizeLimitMiddleware`` (this module)

    **Customization points:**
      - Adjust ``requests_per_minute`` in the ``RateLimitMiddleware``
        initializer for stricter/looser throttling.
      - Uncomment the ``RequestSizeLimitMiddleware`` line to re-enable
        payload size enforcement (currently disabled to debug an ASGI
        protocol error on 25 MB context posts).
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8016",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    # NOTE: Was disabled to debug ASGI protocol error with 25MB context posts.
    # If Starlette raises "ASGI protocol violation" on large posts, check
    # Content-Length vs Transfer-Encoding: chunked compatibility in the client.
    app.add_middleware(RequestSizeLimitMiddleware, max_size=25 * 1024 * 1024)  # 25MB for context posts


__all__ = [
    "m9_safe",
    "RateLimitMiddleware",
    "RequestSizeLimitMiddleware",
    "apply_security",
]
