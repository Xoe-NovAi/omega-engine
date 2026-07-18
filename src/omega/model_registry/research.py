"""
Research Profile Data Classes
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-18
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResearchProfile:
    profile: str
    context_window: int
    reasoning_depth: str
    tool_fidelity: str
    guardrails: list[str] = field(default_factory=list)
    failure_signature: str = ""
    shadow_focus: str = ""