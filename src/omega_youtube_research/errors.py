# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# Sovereign, local-first YouTube transcript ingestion + provenance tracking.
#
# Heritage:
#   [heritage: anyio 2024] All async I/O wrapped in anyio.to_thread.run_sync
#   [heritage: cryptography 2023] HMAC-SHA256 signing via cryptography.hazmat
#   [heritage: pydantic 2017] Typed data contracts for every public API
#   [heritage: aiosqlite 2021] WAL-mode SQLite persistence
#   [heritage: sqlite-fts5 2015] (future) full-text indexing of transcripts
#   No id Software heritage tags — original Omega architecture (Sieve-and-Sign protocol).

"""Typed error taxonomy for the YouTube Research Module.

Mandate 9 (Error Integrity): every failure is typed, traceable, and testable.
No bare ``except:`` and no silent swallowing anywhere in this module.
"""

from typing import Any, Dict, Optional

from omega.errors import OmegaError


class YouTubeResearchError(OmegaError):
    """Base class for all YouTube Research Module failures."""


class YouTubeAuthError(YouTubeResearchError):
    """Raised when a YouTube Data API key is missing or rejected."""

    def __init__(self, message: str, provider: str = "youtube_data_api", **kwargs):
        self.provider = provider
        super().__init__(message, **kwargs)


class YouTubeAPIError(YouTubeResearchError):
    """Raised when the YouTube Data API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        body: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.status_code = status_code
        self.body = body or {}
        super().__init__(message, **kwargs)


class SigningError(YouTubeResearchError):
    """Raised when attestation signing or verification fails."""


class ProvenanceIntegrityError(YouTubeResearchError):
    """Raised when a provenance hash chain fails verification (tamper detected)."""


class PersistenceError(YouTubeResearchError):
    """Raised when atomic persistence (SQLite WAL or JSON rename) fails."""


class SieveError(YouTubeResearchError):
    """Raised when transcript sieving produces an invalid result."""
