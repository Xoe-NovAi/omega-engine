"""Tainted Data Protocol (TDP) — Sovereign Security Layer.
AP: AP-TDP-v1.0.0
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

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
