"""Tainted Data Protocol (TDP) — Sovereign Security Layer.
AP: AP-TDP-v1.0.0
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)


@dataclass
class TaintedData:
    """Wrapper for data fetched from external, untrusted sources.

    Ensures that external content is tracked and isolated from
    system instructions to prevent prompt injection.
    """

    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    taint_level: int = 1  # 1: External, 2: High-Risk, 3: Malicious/Blocked

    def __str__(self) -> str:
        return self.content


class TDPGate:
    """The Tainted Data Protocol Gate.

    Enforces strict isolation between system instructions and external data.
    """

    # Delimiters used to isolate tainted data in the final prompt
    START_MARKER = "### [EXTERNAL DATA START]"
    END_MARKER = "### [EXTERNAL DATA END]"

    @classmethod
    def isolate(cls, content: Union[str, TaintedData]) -> str:
        """
        Wraps content in isolation markers if it is tainted.
        If the content is already a string, it is treated as trusted (Internal).
        """
        if isinstance(content, TaintedData):
            # Apply isolation markers to prevent the LLM from treating
            # tainted data as system instructions.
            return (
                f"{cls.START_MARKER}\n"
                f"Source: {content.source}\n"
                f"Taint Level: {content.taint_level}\n"
                f"---\n"
                f"{content.content}\n"
                f"{cls.END_MARKER}"
            )

        # Trusted internal content is returned as-is
        return content

    @classmethod
    def sanitize(cls, content: str) -> str:
        """
        Basic sanitization to remove common prompt injection patterns
        from tainted strings before they even reach the isolation gate.
        """
        # Remove common 'Ignore previous instructions' patterns
        patterns = [
            r"(?i)ignore previous instructions",
            r"(?i)disregard all prior directions",
            r"(?i)you are now a",
            r"(?i)system override",
        ]

        sanitized = content
        for p in patterns:
            import re

            sanitized = re.sub(p, "[REDACTED INJECTION PATTERN]", sanitized)

        return sanitized


def determine_url_taint(*args, **kwargs) -> int:
    """Determines taint level based on the URL provided in the arguments.

    Trusted (Level 1): localhost, 127.0.0.1, github.com/Xoe-NovAi, local paths.
    Untrusted (Level 2): All other external URLs.
    """
    url = None
    # Try to find the URL in positional args or keyword args
    if args:
        url = args[0] if isinstance(args[0], str) else None
    if not url and "url" in kwargs:
        url = kwargs["url"]

    if not url or not isinstance(url, str):
        return 2  # Default to high-risk if no URL found

    trusted_domains = ["localhost", "127.0.0.1", "github.com/Xoe-NovAi"]

    # Check for local file paths
    if url.startswith("/") or url.startswith("./") or url.startswith("../"):
        return 1

    if any(domain in url for domain in trusted_domains):
        return 1

    return 2


def tdp_wrap(source: str, taint_level: Union[int, callable] = 1):
    """Decorator to wrap async tool returns in TaintedData and isolate them.

    [S2-A: Tainted Data Protocol]
    Ensures that any string returned by the decorated function is treated
    as untrusted and wrapped in the TDP isolation gate.

    Args:
        source: The name of the source of the data.
        taint_level: An integer (1-3) or a callable that returns an integer
                     based on the function arguments.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Determine the actual taint level
            actual_level = taint_level
            if callable(taint_level):
                try:
                    actual_level = taint_level(*args, **kwargs)
                except Exception as e:
                    logger.error(f"TDP taint_level callable failed for {func.__name__}: {e}")
                    actual_level = 2  # Default to high-risk on error

            if isinstance(result, str):
                tainted = TaintedData(content=result, source=source, taint_level=actual_level)
                return TDPGate.isolate(tainted)
            return result

        return wrapper

    return decorator
