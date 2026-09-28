#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
🔱 SearXNG MCP Server — Streamable HTTP Transport (Stateless)
AP: AP-SEARXNG-MCP-STREAMABLE-v1.4.0
⬡ OMEGA ⬡ SEARXNG-MCP ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_searxng_mcp ⬡ STREAMABLE-HTTP

Sovereign metasearch via self-hosted SearXNG.
Uses ASGI + uvicorn pattern for stateless Streamable HTTP (FastMCP 3.x compatible).
Full observability: structured logging, error tracing, lifespan hooks, request tracing.
AnyIO-compliant (no asyncio).
"""

import os
import sys
import signal
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Any

import anyio
import httpx2 as httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

# ──────────────────────────────────────────────────────────────────────────────
# Structured Logging Configuration
# ──────────────────────────────────────────────────────────────────────────────

class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for observability."""
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        import time
        
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info"}:
                log_data[key] = value
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(level: str = "DEBUG") -> logging.Logger:
    """Configure structured logging for the MCP server."""
    logger = logging.getLogger("searxng-mcp")
    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = False
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # Also configure uvicorn loggers
    for uvicorn_logger in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uv_logger = logging.getLogger(uvicorn_logger)
        uv_logger.handlers.clear()
        uv_logger.addHandler(console_handler)
        uv_logger.setLevel(getattr(logging, level.upper()))
        uv_logger.propagate = False
    
    return logger


logger = setup_logging(os.getenv("LOG_LEVEL", "DEBUG"))


# ──────────────────────────────────────────────────────────────────────────────
# Request/Response Tracing Middleware
# ──────────────────────────────────────────────────────────────────────────────

class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware to trace all HTTP requests with timing and context."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        import time
        import uuid
        
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()
        
        # Log request start
        logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client": request.client.host if request.client else "unknown",
            }
        )
        
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log request completion
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )
            
            # Add tracing headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time-MS"] = str(round(duration_ms, 2))
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
            raise


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

MCP_PORT = int(os.getenv("MCP_PORT", "8018"))
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
SEARXNG_URL = os.getenv("SEARXNG_BASE_URL", "http://localhost:8017")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

logger.info("configuration_loaded", extra={
    "mcp_port": MCP_PORT,
    "mcp_host": MCP_HOST,
    "searxng_url": SEARXNG_URL,
    "log_level": LOG_LEVEL,
})


# ──────────────────────────────────────────────────────────────────────────────
# FastMCP Server Initialization
# ──────────────────────────────────────────────────────────────────────────────

# [seam-fix 2026-09-28 maat] stateless_http=True is passed to the CONSTRUCTOR,
# not to streamable_http_app(). Correcting an earlier claim of mine: I previously
# wrote that the `mcp` SDK had "no stateless_http knob". That was WRONG. The knob
# exists — it is a FastMCP *settings* field (default False) that
# streamable_http_app() reads internally:
#
#     StreamableHTTPSessionManager(..., stateless=self.settings.stateless_http, ...)
#
# `streamable_http_app()` itself takes no arguments, which is what misled me.
# So the original `http_app(stateless_http=True, ...)` intent IS reproducible on
# the `mcp` SDK, just at construction time rather than call time. Verified:
#     FastMCP("x").settings.stateless_http              -> False
#     FastMCP("x", stateless_http=True).settings...     -> True
#
# Without this flag the server ran STATEFUL while /health advertised
# "stateless": true — a fabricated claim in a health endpoint, which is exactly
# the unverified-assertion class this workstream exists to eliminate.
mcp = FastMCP("Sovereign SearXNG", stateless_http=True)

# Create ASGI app with Streamable HTTP
# [seam-fix 2026-09-27 maat] Migrated from the standalone `fastmcp` package
# (not installed) to the `mcp` SDK, matching the already-correct pattern at
# mcp_servers/firecrawl/server.py:24.
try:
    app = mcp.streamable_http_app()
    # Report the REAL setting rather than a hardcoded literal, so the health
    # payload can never drift from the server's actual configuration again.
    if not mcp.settings.stateless_http:  # pragma: no cover — defensive
        raise RuntimeError(
            "stateless_http was requested but the SDK reports "
            f"stateless_http={mcp.settings.stateless_http}; /health would lie."
        )
    logger.info("streamable_http_app_created", extra={
        "transport": "streamable-http",
        "stateless": mcp.settings.stateless_http,
    })
except Exception as e:
    logger.critical("fastmcp_app_creation_failed", extra={
        "error_type": type(e).__name__,
        "error_message": str(e),
        "traceback": traceback.format_exc(),
    })
    raise


# ──────────────────────────────────────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id", "X-Request-ID", "X-Response-Time-MS"],
)

# Add request tracing middleware
app.add_middleware(RequestTracingMiddleware)


# ──────────────────────────────────────────────────────────────────────────────
# Exception Handlers
# ──────────────────────────────────────────────────────────────────────────────

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler with full traceback logging."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    logger.error(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "type": type(exc).__name__,
        }
    )


async def http_status_exception_handler(request: Request, exc: httpx.HTTPStatusError) -> JSONResponse:
    """Handle upstream HTTP errors from SearXNG."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    logger.warning(
        "upstream_http_error",
        extra={
            "request_id": request_id,
            "upstream_url": str(exc.request.url),
            "status_code": exc.response.status_code,
            "response_text": exc.response.text[:500] if exc.response.text else None,
        }
    )
    
    return JSONResponse(
        status_code=502,
        content={
            "error": "Upstream service error",
            "request_id": request_id,
            "upstream_status": exc.response.status_code,
        }
    )


async def request_error_handler(request: Request, exc: httpx.RequestError) -> JSONResponse:
    """Handle network/connection errors to upstream."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    logger.error(
        "upstream_connection_failed",
        extra={
            "request_id": request_id,
            "upstream_url": str(exc.request.url) if exc.request else "unknown",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
    
    return JSONResponse(
        status_code=503,
        content={
            "error": "Upstream service unavailable",
            "request_id": request_id,
            "detail": str(exc),
        }
    )

# Register exception handlers on the app
app.exception_handlers[Exception] = global_exception_handler
app.exception_handlers[httpx.HTTPStatusError] = http_status_exception_handler
app.exception_handlers[httpx.RequestError] = request_error_handler


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan Event Logging (wrap the app's lifespan)
# ──────────────────────────────────────────────────────────────────────────────

original_lifespan = app.router.lifespan_context

@asynccontextmanager
async def traced_lifespan(app_instance):
    """Wrap lifespan to add detailed startup/shutdown logging."""
    logger.info("lifespan_startup_begin")
    try:
        async with original_lifespan(app_instance) as state:
            logger.info("lifespan_startup_complete", extra={"state_keys": list(state.keys()) if state else []})
            yield state
    except Exception as e:
        logger.critical("lifespan_startup_failed", extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        })
        raise
    finally:
        logger.info("lifespan_shutdown_begin")
    logger.info("lifespan_shutdown_complete")

app.router.lifespan_context = traced_lifespan


# ──────────────────────────────────────────────────────────────────────────────
# Signal Handlers for Graceful Shutdown (AnyIO-compliant)
# ──────────────────────────────────────────────────────────────────────────────

shutdown_event = anyio.Event()

def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    logger.info("signal_received", extra={"signal": signum, "signal_name": signal.Signals(signum).name})
    shutdown_event.set()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ──────────────────────────────────────────────────────────────────────────────
# MCP Tools
# ──────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def searxng_search(
    query: str,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
    limit: int = 10,
) -> str:
    """Sovereign metasearch via self-hosted SearXNG.

    For YouTube research: categories="videos", engines="youtube,invidious,piped,odysee,peertube"
    For general: categories="general", engines="brave,startpage,marginalia,qwant,bing,wikipedia"
    For code: categories="it", engines="github,gitlab,codeberg,stackoverflow,mdn"
    For science: categories="science", engines="arxiv,semantic_scholar,openalex,crossref,pubmed,google_scholar"
    """
    logger.debug("searxng_search_called", extra={
        "query": query[:100],
        "categories": categories,
        "engines": engines,
        "language": language,
        "pageno": pageno,
        "limit": limit,
    })
    
    form_data = {
        "q": query,
        "format": "json",
        "language": language,
        "categories": categories,
        "pageno": str(pageno),
    }
    if engines:
        form_data["engines"] = engines
    if time_range:
        form_data["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(f"{SEARXNG_URL}/search", data=form_data)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning("searxng_http_error", extra={
                "query": query[:100],
                "status_code": e.response.status_code,
                "response": e.response.text[:200],
            })
            return f"SearXNG HTTP error: {e.response.status_code} - {e}"
        except httpx.RequestError as e:
            logger.error("searxng_request_failed", extra={
                "query": query[:100],
                "error_type": type(e).__name__,
                "error_message": str(e),
            })
            return f"SearXNG request failed: {e}"

    # Collect all result types from SearXNG response
    all_results = []
    
    # Standard web results
    for r in data.get("results", []):
        if isinstance(r, dict):
            item = dict(r)
            item["_result_type"] = "web"
            all_results.append(item)
    
    # Infoboxes (Wikipedia, knowledge panels, etc.)
    for r in data.get("infoboxes", []):
        if isinstance(r, dict):
            item = dict(r)
            item["_result_type"] = "infobox"
            all_results.append(item)
    
    # Direct answers
    for r in data.get("answers", []):
        if isinstance(r, dict):
            item = dict(r)
            item["_result_type"] = "answer"
            all_results.append(item)
        elif isinstance(r, str):
            all_results.append({"_result_type": "answer", "title": "Answer", "content": r, "engine": "searxng"})
    
    # Corrections (did you mean)
    for r in data.get("corrections", []):
        if isinstance(r, dict):
            item = dict(r)
            item["_result_type"] = "correction"
            all_results.append(item)
        elif isinstance(r, str):
            all_results.append({"_result_type": "correction", "title": f"Correction: {r}", "content": r, "engine": "searxng"})
    
    # Suggestions
    for r in data.get("suggestions", []):
        if isinstance(r, dict):
            item = dict(r)
            item["_result_type"] = "suggestion"
            all_results.append(item)
        elif isinstance(r, str):
            all_results.append({"_result_type": "suggestion", "title": f"Suggestion: {r}", "content": r, "engine": "searxng"})

    if not all_results:
        logger.info("searxng_no_results", extra={"query": query[:100]})
        return f"No results for query: {query}"

    lines = [f"Search: {query} | Categories: {categories} | Engines: {engines or 'default'}"]
    for i, r in enumerate(all_results[:limit], 1):
        result_type = r.get("_result_type", "unknown")
        title = r.get("title", r.get("infobox", r.get("answer", r.get("correction", r.get("suggestion", "No title")))))
        url = r.get("url", r.get("urls", [{}])[0].get("url", "No URL") if r.get("urls") else "No URL")
        content = r.get("content", r.get("snippet", r.get("infobox", r.get("answer", "No snippet"))))
        engine = r.get("engine", "unknown")
        lines.append(f"\n[{i}] {title} ({engine}) [{result_type}]")
        lines.append(f"    URL: {url}")
        lines.append(f"    Snippet: {str(content)[:300]}...")

    logger.debug("searxng_search_completed", extra={
        "query": query[:100],
        "result_count": len(all_results),
        "returned": min(len(all_results), limit),
        "types": list(set(r.get("_result_type", "unknown") for r in all_results[:limit])),
    })
    
    return "\n".join(lines)


@mcp.tool()
async def searxng_health() -> str:
    """Check SearXNG instance health."""
    logger.debug("searxng_health_check_called")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SEARXNG_URL}/healthz")
            logger.info("searxng_health_check_ok", extra={"status_code": resp.status_code})
            return f"SearXNG healthy: {resp.status_code}"
        except Exception as e:
            logger.error("searxng_health_check_failed", extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
            })
            return f"SearXNG unhealthy: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# Health Check Endpoint
# ──────────────────────────────────────────────────────────────────────────────

async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring.

    `stateless` is read from the live FastMCP settings rather than hardcoded.
    A health endpoint that asserts a capability the server does not have is
    worse than one that omits it: it converts a known gap into a false all-clear.
    See the [seam-fix 2026-09-28] note at the FastMCP construction site.
    """
    return JSONResponse({
        "status": "healthy",
        "service": "searxng-mcp",
        "version": "1.4.0",
        "transport": "streamable-http",
        "stateless": mcp.settings.stateless_http,
    })

app.router.routes.append(Route("/health", health_check, methods=["GET"]))


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point (AnyIO-compliant)
# ──────────────────────────────────────────────────────────────────────────────

async def run_server() -> None:
    """Run the server with AnyIO-compliant lifecycle."""
    logger.info("server_starting", extra={
        "host": MCP_HOST,
        "port": MCP_PORT,
        "pid": os.getpid(),
    })
    
    config = uvicorn.Config(
        app,
        host=MCP_HOST,
        port=MCP_PORT,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
        log_config=None,
        lifespan="on",
    )
    server = uvicorn.Server(config)
    
    # Run server with AnyIO task group for proper lifecycle
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(server.serve)
            await shutdown_event.wait()
            logger.info("shutdown_signal_received")
            server.should_exit = True
    except Exception as e:
        logger.critical("server_crashed", extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        })
        raise
    finally:
        logger.info("server_stopped", extra={"pid": os.getpid()})


if __name__ == "__main__":
    anyio.run(run_server)