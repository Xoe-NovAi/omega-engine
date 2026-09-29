#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
#
# omega_exchange_server.py — read-only artifact origin for the Node 0 -> Node 1
# federation exchange pipe. Replaces `python3 -m http.server` (2026-09-28).
#
# WHY THIS EXISTS — the false-success bug (Carmack, verified by execution):
#   The old origin returned a 48-byte ASCII body to some clients:
#       $ curl -o /tmp/tail.zip http://100.123.51.67:8019/<artifact>
#       /tmp/tail.zip: ASCII text, 48 bytes
#   `curl -o` writes an error body to disk indistinguishably from a successful
#   download. A receiver that skips manifest verification writes a 48-byte "zip",
#   believes the transfer worked, and fails much later at `unzip` — far from the
#   cause. That is a false success on the exact channel the manifest rule exists
#   to protect.
#
# IMPORTANT, AND NOT FIXABLE HERE:
#   That 48-byte body is emitted by TAILSCALED's TLS terminator (Go net/http),
#   not by this service. Proven by the journal line:
#       http: TLS handshake error from 100.123.51.67:PORT:
#             client sent an HTTP request to an HTTPS server
#   The plaintext request never reaches this origin, so NO origin change can
#   suppress that specific response. What this service does is make it
#   UNMISTAKABLE and UNMISTAKABLY-WRONG for a well-behaved client:
#     1. a manifest (path, size, sha256, content-type) served alongside every
#        artifact, so a client can verify BEFORE accepting bytes;
#     2. every error is a JSON envelope tagged `X-Omega-Error: 1`, never a bare
#        body, so an error can never be parsed as a payload;
#     3. a real access log, because "did the pull work?" must be answerable.
#   See docs/operations/EXCHANGE_PIPE_RUNBOOK.md for the exact URL form.
#
# MANDATES
#   M1  — AnyIO only. This module MUST NOT `import asyncio`. Blocking work runs
#         through `anyio.to_thread.run_sync`.
#   M23 — Failure integrity: refuse ambiguous requests loudly rather than
#         degrading quietly.
#   M7  — Local-first, no egress. Binds loopback only; Tailscale Serve fronts it.

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anyio
import uvicorn
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route

# ── Configuration ────────────────────────────────────────────────────────────
ROOT = Path(os.environ.get("OMEGA_EXCHANGE_ROOT", "/home/arcana-novai/exchange"))
HOST = os.environ.get("OMEGA_EXCHANGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("OMEGA_EXCHANGE_PORT", "8019"))

# Never bind a wildcard address. The tailnet boundary is Tailscale Serve, which
# applies the packet filter. Binding 0.0.0.0 here would put this on the LAN —
# exactly the class of defect `make check-lan-exposure` exists to catch.
if HOST not in ("127.0.0.1", "::1", "localhost"):
    print(
        f"FATAL: refusing to bind non-loopback host {HOST!r}. "
        "The exchange origin is loopback-only by mandate; Tailscale Serve "
        "provides the tailnet boundary.",
        file=sys.stderr,
    )
    raise SystemExit(2)

ERROR_HEADER = "X-Omega-Error"
SERVICE_NAME = "omega-exchange/2.0"

# ── Structured access log ─────────────────────────────────────────────────────
# One line per request, JSON, to stdout -> systemd journal.
# Fields: ts (UTC, explicit +00:00), method, path, status, bytes, client_ip,
#         user_agent, duration_ms, note.
#
# The previous `python3 -m http.server` origin wrote NO access log at all, which
# is why we could assert "the log has never shown a hit from N1" about a log that
# did not exist. A successful pull and a failed pull were indistinguishable. This
# is the falsifiability requirement: without it, "did it work?" is unanswerable
# and the same conversation repeats.
def access_log(**fields: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "service": SERVICE_NAME,
    }
    payload.update(fields)
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def error_envelope(status: int, reason: str, detail: str, **extra: Any) -> JSONResponse:
    """A machine-readable error. Never a bare body.

    The `X-Omega-Error: 1` header is the cheap client-side check: a client that
    downloaded this file can tell, without parsing, that it is not a payload.
    """
    body = {
        "error": reason,
        "detail": detail,
        "status": status,
        "service": SERVICE_NAME,
        "verification_required": True,
        "hint": (
            "This is an error envelope, not an artifact. Do not treat these bytes "
            "as a payload. Fetch /manifest.json and verify size + sha256 before "
            "accepting any download."
        ),
    }
    body.update(extra)
    return JSONResponse(
        body,
        status_code=status,
        headers={ERROR_HEADER: "1", "Cache-Control": "no-store"},
    )


# ── Manifest ─────────────────────────────────────────────────────────────────
_manifest_cache: dict[str, Any] = {"mtime": None, "entries": []}
# Bounded so a pathological directory cannot grow this without limit.
_MANIFEST_MAX_ENTRIES = 5000


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_manifest() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    root_mtime = ROOT.stat().st_mtime if ROOT.exists() else 0.0
    if _manifest_cache["mtime"] == root_mtime:
        return _manifest_cache["entries"]

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in sorted(filenames):
            if name.startswith("."):
                continue
            p = Path(dirpath) / name
            try:
                st = p.lstat()
            except OSError:
                continue
            if not os.path.isfile(p) or os.path.islink(p):
                # Never follow symlinks out of the root.
                continue
            entries.append(
                {
                    "path": str(p.relative_to(ROOT)),
                    "size": st.st_size,
                    "sha256": _sha256(p),
                    "content_type": _guess_type(name),
                    "modified_utc": datetime.fromtimestamp(
                        st.st_mtime, timezone.utc
                    ).isoformat(timespec="seconds"),
                }
            )
            if len(entries) >= _MANIFEST_MAX_ENTRIES:
                entries.sort(key=lambda e: e["path"])
                _manifest_cache.update(mtime=root_mtime, entries=entries)
                return entries

    entries.sort(key=lambda e: e["path"])
    _manifest_cache.update(mtime=root_mtime, entries=entries)
    return entries


def _guess_type(name: str) -> str:
    ext = os.path.splitext(name)[1].lower()
    return {
        ".zip": "application/zip",
        ".json": "application/json",
        ".sha256": "text/plain; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
        ".txt": "text/plain; charset=utf-8",
        ".tgz": "application/gzip",
        ".tar": "application/x-tar",
    }.get(ext, "application/octet-stream")


def _safe_resolve(rel_path: str) -> Path | None:
    """Resolve a request path inside ROOT, or None if it escapes.

    Rejects traversal (`..`), absolute paths, and symlinks that leave the root.
    """
    if not rel_path or rel_path in (".", "/"):
        return None
    if rel_path.startswith("/"):
        rel_path = rel_path.lstrip("/")
    candidate = (ROOT / rel_path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate


# ── Handlers ─────────────────────────────────────────────────────────────────
async def manifest(request: Any) -> Response:
    entries = await anyio.to_thread.run_sync(_build_manifest)
    body = {
        "service": SERVICE_NAME,
        "root": str(ROOT),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(entries),
        "how_to_verify": (
            "For each entry: download the file, then assert its byte length equals "
            "'size' and sha256sum equals 'sha256'. If either differs, the transfer "
            "failed — do not use the file."
        ),
        "url_form": "https://n0.tail51f14a.ts.net:8019/<path>  (HTTPS ONLY)",
        "broken_url_form": (
            "http://100.123.51.67:8019/<path> is BROKEN: the tailnet IP speaks "
            "HTTPS. A plain-HTTP request is rejected by Tailscale with a 48-byte "
            "ASCII body that curl -o writes to disk like a successful download."
        ),
        "entries": entries,
    }
    raw = json.dumps(body, indent=2).encode("utf-8")
    access_log(
        method="GET",
        path="/manifest.json",
        status=200,
        bytes=len(raw),
        client_ip=request.client.host if request.client else "-",
        user_agent=request.headers.get("user-agent", "-"),
        note="manifest",
    )
    return Response(
        raw,
        media_type="application/json",
        headers={"Cache-Control": "no-store", "Content-Length": str(len(raw))},
    )


async def index(request: Any) -> Response:
    entries = await anyio.to_thread.run_sync(_build_manifest)
    body = {
        "service": SERVICE_NAME,
        "root": str(ROOT),
        "count": len(entries),
        "manifest": "/manifest.json",
        "url_form": "https://n0.tail51f14a.ts.net:8019/<path>  (HTTPS ONLY)",
        "paths": [e["path"] for e in entries],
    }
    raw = json.dumps(body, indent=2).encode("utf-8")
    access_log(
        method=request.method,
        path="/",
        status=200,
        bytes=len(raw),
        client_ip=request.client.host if request.client else "-",
        user_agent=request.headers.get("user-agent", "-"),
    )
    return Response(
        raw,
        media_type="application/json",
        headers={"Cache-Control": "no-store", "Content-Length": str(len(raw))},
    )


def _log(request: Any, method: str, path: str, status: int, nbytes: int, note: str = "") -> None:
    access_log(
        method=method,
        path=path,
        status=status,
        bytes=nbytes,
        client_ip=request.client.host if request.client else "-",
        user_agent=request.headers.get("user-agent", "-"),
        note=note or None,
    )


async def serve_file(request: Any) -> Response:
    started = time.monotonic()
    raw_path = request.url.path
    rel = raw_path.lstrip("/")
    target = _safe_resolve(rel)

    def _stat() -> tuple[int, str] | None:
        if target is None or not target.exists() or not target.is_file():
            return None
        st = target.stat()
        return st.st_size, _sha256(target)

    info = await anyio.to_thread.run_sync(_stat)
    if info is None:
        _log(request, request.method, raw_path, 404, 0, "not_found")
        return error_envelope(
            404,
            "not_found",
            f"No artifact at {rel!r}. Fetch /manifest.json for the real paths.",
            path=rel,
        )

    size, digest = info
    _log(
        request,
        request.method,
        raw_path,
        200,
        size,
        f"sha256={digest[:16]} dur_ms={(time.monotonic()-started)*1000:.1f}",
    )
    return FileResponse(
        target,
        media_type=_guess_type(target.name),
        headers={
            # The client can verify from headers alone, before hashing the body.
            "X-Omega-Size": str(size),
            "X-Omega-SHA256": digest,
            "X-Omega-Error": "0",
        },
    )


async def _unsupported(request: Any, exc: Exception) -> Response:
    # Starlette raises 405 when a path matches but the method does not. Without
    # this handler the default response is a bare `Allow` header with an empty
    # body — which is exactly the "short body a client could mistake for a
    # payload" shape this service exists to eliminate.
    _log(request, request.method, request.url.path, 405, 0, "method_rejected")
    return error_envelope(
        405,
        "method_not_allowed",
        f"{request.method} is not supported. This origin is READ-ONLY.",
        allowed=["GET", "HEAD"],
    )


async def _not_found(request: Any, exc: Exception) -> Response:
    _log(request, request.method, request.url.path, 404, 0, "route_rejected")
    return error_envelope(
        404, "not_found", f"No route {request.url.path!r}. See / or /manifest.json."
    )


app = Starlette(
    routes=[
        Route("/", index, methods=["GET", "HEAD"]),
        Route("/manifest.json", manifest, methods=["GET", "HEAD"]),
        Route("/healthz", index, methods=["GET", "HEAD"]),
        # GET/HEAD only. Every other verb on this path is refused with 405 by
        # the exception handler below.
        Route("/{path:path}", serve_file, methods=["GET", "HEAD"]),
    ],
    exception_handlers={405: _unsupported, 404: _not_found},
)


def main() -> None:
    if not ROOT.exists():
        print(f"FATAL: exchange root {ROOT} does not exist", file=sys.stderr)
        raise SystemExit(2)
    access_log(
        method="-", path="-", status=0, bytes=0,
        client_ip="-", user_agent="-",
        note=f"startup root={ROOT} bind={HOST}:{PORT}",
    )
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_config=None,      # we do our own structured access log
        access_log=False,     # disable uvicorn's own, avoid double logging
    )


if __name__ == "__main__":
    main()
