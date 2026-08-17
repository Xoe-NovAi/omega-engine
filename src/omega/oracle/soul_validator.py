# AP: AP-PR-READINESS-v1.0.0
# AP: AP-R10-SOUL-VALIDATION-v1.0.0
# 🔱 Soul Validator — R-10 Schema Enforcement
#
# Implements the canonical soul schema defined in docs/research/R10_soul_schema_validation.md.
# Ensures that entity souls are syntactically valid and structurally complete.
#
# [id-soft: vet-015] ZONEID Pattern — validated via soul_power and session counts.
#
# Phase 1E Temple Cleansing (D-398): yaml.safe_load + Pydantic model_validate.
# Pydantic models defined at bottom of file.


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from omega.errors import OmegaError

from pydantic import BaseModel, Field, model_validator, ConfigDict
from pydantic import ValidationError as PydanticValidationError

logger = logging.getLogger(__name__)


class SoulValidationError(Exception):
    """Raised when a soul file violates the R-10 schema."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception


REQUIRED_TOP_KEYS = {"entity"}
# Core required fields in the entity block (backward compatible)
REQUIRED_ENTITY_KEYS = {"name"}
# v6.1 recommended blocks (not required for validation but checked for consistency)
RECOMMENDED_ENTITY_BLOCKS = {"identity", "directives", "team"}
# Fields that were required in v6.0 but forbidden in v6.1 lean schema
FORBIDDEN_ENTITY_BLOCKS = {"soul_axioms", "wisdom_text", "trajectory"}
# Valid soul_version values
SOUL_VERSION = "6.1"


class SoulValidator:
    """Sovereign validator for entity soul files.

    v6.1 Lean Schema: soul.yaml contains only identity, directives, team.
    Session logs -> memory/sessions.yaml.
    Lesson proposals -> memory/proposed_lessons.yaml.
    Approved lessons -> memory/approved_lessons.yaml.

    Provides methods to validate soul.yaml files and generate minimal safe fallbacks
    when corruption is detected.
    """

    def __init__(self, entities_data_dir: Path):
        self.entities_data_dir = entities_data_dir

    def validate(self, entity_name: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate the soul.yaml for a given entity.

        Args:
            entity_name: The human-readable name of the entity.

        Returns:
            A tuple of (is_valid, loaded_data). If is_valid is False,
            loaded_data may be None or a partially loaded dict.
        """
        safe_name = entity_name.lower().replace(" ", "_").replace("'", "")
        soul_file = self.entities_data_dir / safe_name / "soul.yaml"

        if not soul_file.exists():
            logger.warning(f"Soul file not found for {entity_name} at {soul_file}")
            return False, None

        try:
            # Use a safe load with encoding check
            with open(soul_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            self.validate_dict(data)
            return True, data

        except (yaml.YAMLError, SoulValidationError, TypeError, KeyError) as e:
            logger.error(f"Soul validation failure for {entity_name}: {e}")
            return False, None
        except (OmegaError, RuntimeError, OSError) as e:
            logger.critical(
                f"Unexpected error during soul validation for {entity_name}: {e}", exc_info=True
            )
            return False, None

    def validate_dict(self, data: Any) -> None:
        """Verify a dictionary against the v6.1 soul schema using Pydantic.

        v6.0 souls receive a migration warning but are NOT rejected (backward
        compatibility). v6.1 souls are fully validated via ``SoulYaml.model_validate``.

        Raises:
            SoulValidationError: If the dictionary violates the schema.
        """
        if not isinstance(data, dict) or not REQUIRED_TOP_KEYS.issubset(data.keys()):
            raise SoulValidationError("Missing top-level 'entity' key or invalid YAML structure")

        entity = data["entity"]
        if not isinstance(entity, dict):
            raise SoulValidationError("'entity' block must be a dictionary")

        missing = REQUIRED_ENTITY_KEYS - entity.keys()
        if missing:
            raise SoulValidationError(f"Missing required fields in soul: {missing}")

        # Backward Compatibility Check
        version = entity.get("soul_version", "6.0")
        if version != SOUL_VERSION:
            logger.warning(
                f"Entity '{entity.get('name')}' is using soul_version '{version}'. "
                f"Please migrate to '{SOUL_VERSION}' to ensure full compliance."
            )
            # Skip strict v6.1 checks for legacy souls to prevent fleet lobotomy
            return

        # --- Strict v6.1 Pydantic Validation ---
        try:
            SoulYaml.model_validate(data)
        except PydanticValidationError as e:
            errors = []
            for err in e.errors():
                loc = " -> ".join(str(l) for l in err["loc"])
                msg = err["msg"]
                errors.append(f"{loc}: {msg}")
            raise SoulValidationError("; ".join(errors)) from e

        # Memory directory validation -- check that memory/ subdirectory exists
        safe_name = entity["name"].lower().replace(" ", "_").replace("'", "")
        memory_dir = self.entities_data_dir / safe_name / "memory"
        if not memory_dir.exists():
            logger.warning(
                "Entity %s has no memory/ directory. "
                "v6.1 requires memory/sessions.yaml, memory/proposed_lessons.yaml, "
                "and memory/approved_lessons.yaml.",
                entity["name"],
            )

    def get_fallback_soul(self, entity_name: str) -> Dict[str, Any]:
        """Generate a minimal safe soul dictionary for fallback recovery.

        v6.1 lean schema -- only entity block with identity.

        [id-soft: vet-008] Lazy Deletion -- provides a safe baseline to prevent
        engine crash when soul is corrupted.
        """
        return {
            "soul_version": "6.1",
            "entity": {
                "name": entity_name,
                "short": "??",
                "soul_version": "6.1",
            },
            "identity": {
                "voice_summary": f"Fallback identity for {entity_name}.",
                "values": ["recovery"],
                "strengths": ["resilience"],
            },
            "directives": [
                {
                    "id": f"d-fallback-001",
                    "title": "Fallback Recovery",
                    "rule": "Recover from corrupted soul file. Rebuild identity from session history.",
                    "rationale": "Soul file was corrupted or missing. Fallback ensures continud operation.",
                }
            ],
            "team": {
                "allies": [],
                "coordination_protocols": {
                    "workspace_lock": f"I check {entity_name.upper()}_WORKSPACE_LOCK before any file edit.",
                    "live_feed": f"I post to {entity_name.upper()}_HMC_COLLABORATION_HUB after each major task.",
                    "hivemind": "I declare presence via hivemind_post_context at session start.",
                },
            },
        }


# ===================================================================
# Pydantic Models -- v6.1 Lean Schema (Phase 1E Temple Cleansing)
# ===================================================================


class Directive(BaseModel):
    """A single directive entry from soul.yaml ``directives`` list.

    Extra keys are silently ignored (backward compat with v6.0-era directive extras).
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    rule: str
    rationale: Optional[str] = None
    mandate_binding: Optional[List[str]] = None
    priority: Optional[str] = None
    validation: Optional[str] = None


class CorePrinciple(BaseModel):
    """A single core principle entry from soul.yaml ``core_principles`` list.

    Extra keys are silently ignored.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    principle: str
    mandates: Optional[List[str]] = None
    confidence: Optional[float] = None
    tags: Optional[List[str]] = None
    source_session: Optional[str] = None
    evidence: Optional[List[Dict[str, str]]] = None
    directive_provenance: Optional[str] = None


class IdentityBlock(BaseModel):
    """The ``identity`` block of a soul.yaml.

    Extra keys are silently ignored.
    """

    model_config = ConfigDict(extra="ignore")

    voice_summary: Optional[str] = None
    values: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    growth_areas: Optional[List[str]] = None


class EntityBlock(BaseModel):
    """The ``entity`` block -- v6.1 lean schema.

    [id-soft: vet-015] ZONEID Pattern -- validated via soul_power and session counts.

    Extra keys ARE allowed (``extra="allow"``) so that unknown fields do not
    cause rejection. Forbidden v6.0 fields are caught by
    ``check_forbidden_fields``.
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(min_length=1)
    short: str = Field(min_length=2, max_length=6)
    soul_version: str = Field(default="6.1")
    archetype: Optional[str] = None
    hierarchy_level: Optional[int] = Field(default=None, ge=0)
    sovereignty_level: Optional[int] = Field(default=None, ge=1, le=10)
    element: Optional[str] = None
    domain: Optional[str] = None
    lessons_learned: Optional[List[Any]] = None

    @model_validator(mode="before")
    @classmethod
    def check_forbidden_fields(cls, data: Any) -> Any:
        """Reject v6.0-only fields (soul_axioms, wisdom_text, trajectory)."""
        if isinstance(data, dict):
            for forbidden in FORBIDDEN_ENTITY_BLOCKS:
                if forbidden in data:
                    raise ValueError(
                        f"'{forbidden}' is a v6.0 field and must NOT exist in v6.1 souls. "
                        f"Remove it or migrate to memory/ subdirectory."
                    )
        return data


class SoulYaml(BaseModel):
    """Top-level structure of a ``soul.yaml`` file -- v6.1 lean schema.

    Extra keys (e.g. ``nameless_one``, ``allies``, ``version``) are silently
    ignored.
    """

    model_config = ConfigDict(extra="ignore")

    entity: EntityBlock
    identity: Optional[IdentityBlock] = None
    directives: Optional[List[Directive]] = None
    core_principles: Optional[List[CorePrinciple]] = None
    team: Optional[Dict[str, Any]] = None
