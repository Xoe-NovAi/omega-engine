"""
Scribe — Soul Distillation Pipeline
M5/M11 compliant: writes proposed_lessons.yaml (blind staging).
"""

from .distiller import SoulDistiller, LessonProposal

__all__ = ["SoulDistiller", "LessonProposal"]
