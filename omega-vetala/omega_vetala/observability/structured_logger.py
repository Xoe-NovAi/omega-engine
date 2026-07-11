# 🔱 omega-vetala — Structured Moderation Logger
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ STRUCTURED-LOGGER
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake-1996] cvar — structured log fields as observable state
#
"""Structured JSON logging for every moderation decision.

Privacy guarantee: **No raw content is ever written to logs.**
Content is replaced with a SHA-256[:16] content fingerprint so that
repeat offenders can be correlated without storing the actual text.

Log levels:
    DEBUG: Every individual provider decision (high volume).
    INFO:  Final aggregated decision / flag event.
    WARNING: Provider failure or timeout.
    ERROR: Systemic failure (all providers down, config error).
"""

from __future__ import annotations

import hashlib
import json
import logging
import logging.handlers
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, TextIO


# ---------------------------------------------------------------------------
# Content hashing — the core privacy primitive
# ---------------------------------------------------------------------------

_CONTENT_HASH_CACHE: dict[str, str] = {}


def _content_hash(text: str) -> str:
    """Return a **reversible-only-by-brute-force** fingerprint of *text*.

    Uses SHA-256 and truncates to 16 hex characters (64 bits).  This is
    enough to correlate repeated violations by the same user without
    storing the actual text.  64 bits of preimage resistance means an
    attacker would need ~2^64 guesses to reverse a single hash — infeasible
    for any realistic scenario.

    Results are cached because the same text is often logged multiple
    times (DEBUG per-provider + INFO final decision).

    Args:
        text: The raw content to fingerprint.

    Returns:
        A 16-character hex digest.
    """
    if text not in _CONTENT_HASH_CACHE:
        _CONTENT_HASH_CACHE[text] = hashlib.sha256(text.encode()).hexdigest()[:16]
    return _CONTENT_HASH_CACHE[text]


# ---------------------------------------------------------------------------
# Category hashing — category names are logged, scores are numeric
# ---------------------------------------------------------------------------

def _hash_categories(categories: dict[str, float]) -> dict[str, float]:
    """Return category scores keyed by the SHA-256[:16] of each category name.

    This prevents category names from leaking provider-specific taxonomies
    into the logs.  The scores themselves are kept as-is because they are
    numeric aggregates with no semantic content.

    Args:
        categories: Raw category-name → score mapping.

    Returns:
        Mapping of hashed-category → score.
    """
    return {_content_hash(k): round(v, 4) for k, v in categories.items()}


# ---------------------------------------------------------------------------
# Action type — what decision was taken
# ---------------------------------------------------------------------------

class ActionTaken:
    """Canonical action types returned by the moderation system."""

    ALLOW: str = "allow"
    WARN: str = "warn"
    BLOCK: str = "block"
    REVIEW: str = "review"
    ERROR: str = "error"


# ---------------------------------------------------------------------------
# Structured log entry
# ---------------------------------------------------------------------------

@dataclass
class LogEntry:
    """A single structured log entry for a moderation decision.

    All fields are serialisable to JSON.  No raw content is stored.
    """

    timestamp: str = ""
    trace_id: str = ""
    provider_name: str = ""
    content_hash: str = ""
    is_flagged: bool = False
    confidence: float = 0.0
    latency_ms: float = 0.0
    category_scores: dict[str, float] = field(default_factory=dict)
    action_taken: str = ""
    level: str = "DEBUG"
    message: str = ""


# ---------------------------------------------------------------------------
# JSON log formatter
# ---------------------------------------------------------------------------

class _JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Format *record* as a JSON line."""
        entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields from the LogEntry
        extra = getattr(record, "extra_fields", {})
        entry.update(extra)

        # Ensure content_hash is never the raw text
        if "content_hash" in entry and len(entry.get("content_hash", "")) > 16:
            entry["content_hash"] = _content_hash(entry["content_hash"])

        return json.dumps(entry, default=str)


# ---------------------------------------------------------------------------
# Main logger class
# ---------------------------------------------------------------------------

class ModerationLogger:
    """Structured logger for moderation decisions.

    Usage::

        logger = ModerationLogger(log_path="/var/log/moderation.jsonl")
        logger.log_decision(
            trace_id="abc123",
            provider_name="perspective",
            is_flagged=True,
            confidence=0.92,
            latency_ms=142.0,
            categories={"TOXICITY": 0.92},
            action_taken="block",
            text=raw_text,   #  ← only the hash is logged
        )

    Args:
        log_path: Path to the JSON lines log file.  If empty, logs to stdout.
        max_bytes: Maximum size in bytes before log rotation (default 100 MB).
        backup_count: Number of rotated log files to keep (default 5).
        level: Minimum logging level (default logging.DEBUG).
    """

    def __init__(
        self,
        log_path: str = "",
        *,
        max_bytes: int = 100 * 1024 * 1024,
        backup_count: int = 5,
        level: int = logging.DEBUG,
    ) -> None:
        self._logger = logging.getLogger("omega_vetala.observability")
        self._logger.setLevel(level)
        self._logger.handlers.clear()

        formatter = _JSONFormatter()

        if log_path:
            handler: logging.Handler = logging.handlers.RotatingFileHandler(
                filename=log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_decision(
        self,
        trace_id: str,
        provider_name: str,
        is_flagged: bool,
        confidence: float,
        latency_ms: float,
        categories: dict[str, float],
        action_taken: str,
        text: str = "",
        *,
        level: int = logging.DEBUG,
    ) -> None:
        """Log a single moderation decision.

        Args:
            trace_id: Unique identifier traceable across the call chain.
            provider_name: Which provider produced this result.
            is_flagged: Whether the content was flagged.
            confidence: Overall confidence score (0.0–1.0).
            latency_ms: Wall-clock time in milliseconds.
            categories: Per-category scores (the **keys** are hashed).
            action_taken: One of ActionTaken values.
            text: Raw content — **only the hash is logged**.
            level: Python logging level for this entry.
        """
        entry: dict[str, Any] = {
            "trace_id": trace_id,
            "provider_name": provider_name,
            "is_flagged": is_flagged,
            "confidence": round(confidence, 4),
            "latency_ms": round(latency_ms, 2),
            "category_scores": _hash_categories(categories),
            "action_taken": action_taken,
        }

        if text:
            entry["content_hash"] = _content_hash(text)

        record = self._logger.makeRecord(
            name=self._logger.name,
            level=level,
            fn="",
            lno=0,
            msg="moderation_decision",
            args=(),
            exc_info=None,
        )
        record.extra_fields = entry  # type: ignore[attr-defined]
        self._logger.handle(record)

    def log_provider_failure(
        self,
        trace_id: str,
        provider_name: str,
        error_message: str,
        latency_ms: float,
        text: str = "",
    ) -> None:
        """Log a provider failure at WARNING level.

        Args:
            trace_id: Trace identifier.
            provider_name: The provider that failed.
            error_message: Description of the failure.
            latency_ms: Time spent before failure.
            text: Raw content — **only hash is logged**.
        """
        entry: dict[str, Any] = {
            "trace_id": trace_id,
            "provider_name": provider_name,
            "error": error_message,
            "latency_ms": round(latency_ms, 2),
        }
        if text:
            entry["content_hash"] = _content_hash(text)

        record = self._logger.makeRecord(
            name=self._logger.name,
            level=logging.WARNING,
            fn="",
            lno=0,
            msg="provider_failure",
            args=(),
            exc_info=None,
        )
        record.extra_fields = entry  # type: ignore[attr-defined]
        self._logger.handle(record)

    def log_systemic_failure(
        self,
        trace_id: str,
        error_message: str,
    ) -> None:
        """Log a systemic failure at ERROR level.

        Args:
            trace_id: Trace identifier.
            error_message: Description of the failure.
        """
        entry: dict[str, Any] = {
            "trace_id": trace_id,
            "error": error_message,
        }
        record = self._logger.makeRecord(
            name=self._logger.name,
            level=logging.ERROR,
            fn="",
            lno=0,
            msg="systemic_failure",
            args=(),
            exc_info=None,
        )
        record.extra_fields = entry  # type: ignore[attr-defined]
        self._logger.handle(record)

    def log_flag_event(
        self,
        trace_id: str,
        provider_name: str,
        is_flagged: bool,
        confidence: float,
        latency_ms: float,
        categories: dict[str, float],
        action_taken: str,
        text: str = "",
    ) -> None:
        """Log a final flag decision at INFO level.

        This is a convenience wrapper around :meth:`log_decision` with
        ``level=logging.INFO`` intended for the *final* aggregated result.
        """
        self.log_decision(
            trace_id=trace_id,
            provider_name=provider_name,
            is_flagged=is_flagged,
            confidence=confidence,
            latency_ms=latency_ms,
            categories=categories,
            action_taken=action_taken,
            text=text,
            level=logging.INFO,
        )
