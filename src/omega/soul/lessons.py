# 🔱 Soul Lessons Schema — Evidence-Bearing Lesson Models (W1-3)
# AP: AP-SOUL-LESSONS-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ N3 ⬡ soul_lessons ⬡ EVIDENCE-FIELD
#
# Ruling S5 / Ma'at Fork 2 (Team-Study #1): explicit evidence field day one,
# WARN-ONLY start. Gemini 3.1 adjudication trap-catch #2: soul schema lacked
# evidence-field support — schema patch BEFORE promotion.
#
# Backward compatible: lessons WITHOUT evidence remain valid; loaders emit a
# warn-only log. Lessons WITH evidence get structural validation: each
# evidence ref must carry at least one of session_id / artifact / quote.
#
# [M11 Soul Integrity] · [M21 Gate Integrity] · [FP-04 Tier-0 alignment]:
# evidence refs support message-level attribution (session_id + artifact),
# never session-level joins presented as proof.

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)

VALID_LEVELS = {"L1", "L2", "L3"}


class EvidenceRef(BaseModel):
    """One structured evidence reference attached to a lesson.

    At least one of session_id / artifact / quote MUST be present.
    `artifact` should be a repo-relative probe path (O-Q4: probe-path bound
    to each evidence claim). `quote` must be verbatim from the artifact.
    """

    model_config = ConfigDict(extra="forbid")

    session_id: Optional[str] = None
    artifact: Optional[str] = None
    quote: Optional[str] = None

    @model_validator(mode="after")
    def _at_least_one_ref(self) -> "EvidenceRef":
        if not any((self.session_id, self.artifact, self.quote)):
            raise ValueError(
                "evidence ref must carry at least one of "
                "session_id / artifact / quote"
            )
        return self


class Lesson(BaseModel):
    """A staged or approved lesson (proposed_lessons.yaml / approved surface).

    Backward compatible with all historical shapes:
      - bare L1/L2/L3 triplets (no id, no date)
      - combined entries (narrative carrying inline 'L1:' prefix)
      - id-bearing entries (AO-P1..P7 style)
    Extra keys are allowed so legacy entries never fail validation.
    """

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    date: Optional[str] = None
    level: str = Field(default="L3")
    narrative: Optional[str] = None
    insight: Optional[str] = None
    principle: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    evidence: Optional[List[EvidenceRef]] = None

    @model_validator(mode="after")
    def _valid_level(self) -> "Lesson":
        if self.level not in VALID_LEVELS:
            raise ValueError(f"lesson level must be one of {sorted(VALID_LEVELS)}, got '{self.level}'")
        return self


def validate_lessons(data: Any, source: str = "<memory>") -> tuple[List[Lesson], List[str]]:
    """Validate a parsed lessons document.

    Returns (lessons, warnings). WARN-ONLY semantics per ruling S5:
      - missing evidence  -> warning appended, lesson still valid
      - malformed evidence -> pydantic error converted to warning? NO:
        structural errors in PRESENT evidence are hard failures (M21) —
        they raise ValueError via pydantic and propagate.

    Args:
        data: parsed YAML — dict with 'proposals'/'approved' key, or a list.
        source: label for warning messages.

    Returns:
        (lessons, warnings)
    """
    warnings: List[str] = []
    if isinstance(data, dict):
        raw_items = data.get("proposals") or data.get("approved") or []
    elif isinstance(data, list):
        raw_items = data
    else:
        raw_items = []

    lessons: List[Lesson] = []
    for i, item in enumerate(raw_items):
        lesson = Lesson.model_validate(item)
        lessons.append(lesson)
        if not lesson.evidence:
            label = lesson.id or f"item[{i}]"
            warnings.append(
                f"{source}: lesson '{label}' has no evidence field "
                "(warn-only per ruling S5 — attach refs before hard-gate)"
            )
            logger.warning(
                "%s: lesson '%s' has no evidence field (warn-only)",
                source, label,
            )
    return lessons, warnings
