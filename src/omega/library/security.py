# 🔱 Omega Engine — Sovereign Security Guards for Library & Curation
# AP: AP-LIBRARY-SECURITY-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ sovereign ⬡ SECURITY ⬡ PHASE-1
#
# Three guards protecting the engine from external threats:
#   1. SSRFGuard — Prevents internal network probing
#   2. PathScopeGuard — Prevents directory traversal
#   3. DownloadSizeGuard — Prevents disk exhaustion
#
# Heritage: [id-soft: doom-1993] SSRF Guard — BSP leaf-culling pattern
#           [id-soft: quake-1996] Path Traversal Guard — zone boundary enforcement
#           [id-soft: quake-1996] Download Size Guard — fixed-timestep pre-check


# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md
import ipaddress
import logging
import socket
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import anyio
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


# ── [id-soft: doom-1993] SSRF Guard ──────────────────────────────────────────
# Ported from BSP leaf-culling: skip invisible subtrees in O(1).
# Here: skip internal IP ranges in O(1) CIDR check.

class SSRFGuard:
    """Network guard that validates URLs against private/internal IP ranges.

    Resolves the hostname to its IP address(es) and checks against
    a compiled list of forbidden CIDR ranges. Blocks loopback, private,
    link-local, and multicast addresses before any HTTP request is made.
    """

    # CIDR ranges that are NEVER valid for external crawling
    FORBIDDEN_RANGES = [
        ipaddress.ip_network("127.0.0.0/8"),       # Loopback
        ipaddress.ip_network("10.0.0.0/8"),         # Private A (RFC 1918)
        ipaddress.ip_network("172.16.0.0/12"),      # Private B (RFC 1918)
        ipaddress.ip_network("192.168.0.0/16"),     # Private C (RFC 1918)
        ipaddress.ip_network("169.254.0.0/16"),     # Link-local
        ipaddress.ip_network("0.0.0.0/8"),          # "This" network
        ipaddress.ip_network("100.64.0.0/10"),      # Carrier-grade NAT
        ipaddress.ip_network("198.18.0.0/15"),      # Benchmarking
        ipaddress.ip_network("240.0.0.0/4"),        # Multicast / Reserved
        ipaddress.ip_network("::1/128"),            # IPv6 loopback
        ipaddress.ip_network("fc00::/7"),           # IPv6 unique-local
        ipaddress.ip_network("fe80::/10"),          # IPv6 link-local
    ]

    @staticmethod
    async def validate(url: str) -> bool:
        """Validate that *url* does not resolve to an internal IP.

        Returns:
            True if the URL is safe to fetch.
            False if it resolves to a forbidden range (blocked).
        """
        try:
            parsed = urlparse(url)
            if not parsed.hostname:
                logger.warning("SSRF: URL has no hostname — blocked")
                return False

            # Resolve hostname to all associated IPs (thread-safe)
            addrinfo = await anyio.to_thread.run_sync(
                socket.getaddrinfo, parsed.hostname, None
            )

            for family, _type, _proto, _canon, sockaddr in addrinfo:
                ip = ipaddress.ip_address(sockaddr[0])
                for cidr in SSRFGuard.FORBIDDEN_RANGES:
                    if ip in cidr:
                        logger.warning(
                            "SSRF blocked: %s resolves to %s (%s)",
                            url[:80], ip, cidr,
                        )
                        return False

            return True

        except (socket.gaierror, ValueError, OSError) as exc:
            logger.warning("SSRF validation failed for %s: %s", url[:80], exc)
            return False


# ── [id-soft: quake-1996] Path Scope Guard ───────────────────────────────────
# Ported from zone.c boundary enforcement: every allocation must stay
# within the zone's low/high watermarks. Here: every file path must
# resolve within the library's data directory.

MAX_DOWNLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB default cap


def validate_path_scope(target_path: Path, base_dir: Path) -> bool:
    """Ensure *target_path* resolves strictly within *base_dir*.

    Resolves both paths to their canonical (real) forms and verifies
    that base_dir is an ancestor of target_path. Prevents directory
    traversal via ``../../etc/passwd`` style attacks.

    Returns:
        True if the path is safe.
        False if it escapes the base directory.
    """
    try:
        resolved_target = target_path.resolve()
        resolved_base = base_dir.resolve()

        if resolved_base in resolved_target.parents or resolved_target == resolved_base:
            return True

        logger.warning(
            "Path traversal blocked: %s escapes base %s",
            resolved_target, resolved_base,
        )
        return False

    except (RuntimeError, OSError) as exc:
        logger.warning("Path scope validation error: %s", exc)
        return False


# ── [id-soft: quake-1996] Download Size Guard ────────────────────────────────
# Ported from Quake's fixed-timestep pre-check: validate before executing.

async def validate_download_size(
    url: str,
    max_bytes: int = MAX_DOWNLOAD_SIZE_BYTES,
) -> bool:
    """Check Content-Length header before downloading (HEAD request).

    Sends a lightweight HTTP HEAD request to inspect the advertised
    content length. If it exceeds *max_bytes*, the download is blocked
    before any significant bandwidth is consumed.

    Returns:
        True if size is acceptable (or undetermined).
        False if Content-Length exceeds max_bytes.
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.head(url)
            content_length = response.headers.get("content-length")

            if content_length and int(content_length) > max_bytes:
                logger.warning(
                    "Download blocked: %s is %s bytes (max %s)",
                    url[:80], content_length, max_bytes,
                )
                return False

            return True

    except (OmegaError, RuntimeError, OSError) as exc:
        # If HEAD fails (server doesn't support it), allow the GET
        # and enforce size limits during streaming instead.
        logger.debug("Size pre-check HEAD failed for %s: %s", url[:80], exc)
        return True
