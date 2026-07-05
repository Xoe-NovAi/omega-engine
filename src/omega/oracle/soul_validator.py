# AP: AP-PR-READINESS-v1.0.0
# AP: AP-R10-SOUL-VALIDATION-v1.0.0
# 🔱 Soul Validator — R-10 Schema Enforcement
# ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: SOUL-INTEGRITY]
#
# Implements the canonical soul schema defined in docs/research/R10_soul_schema_validation.md.
# Ensures that entity souls are syntactically valid and structurally complete.
#
# [id-soft: doom-1993] ZONEID Pattern — validated via soul_power and session counts.

import yaml
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from omega.errors import SoulCorruptionError, OmegaPersistenceError

logger = logging.getLogger(__name__)

class SoulValidationError(Exception):
    """Raised when a soul file violates the R-10 schema."""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception

REQUIRED_TOP_KEYS = {"entity"}
# Core required fields in the entity block (backward compatible)
REQUIRED_ENTITY_KEYS = {
    "name"
}
# v6.1 recommended blocks (not required for validation but checked for consistency)
RECOMMENDED_ENTITY_BLOCKS = {"identity", "directives", "team"}
# Fields that were required in v6.0 but forbidden in v6.1 lean schema
FORBIDDEN_ENTITY_BLOCKS = {"soul_axioms", "wisdom_text", "trajectory"}
# Valid soul_version values
SOUL_VERSION = "6.1"


class SoulValidator:
    """Sovereign validator for entity soul files.
    
    v6.1 Lean Schema: soul.yaml contains only identity, directives, team.
    Session logs → memory/sessions.yaml.
    Lesson proposals → memory/proposed_lessons.yaml.
    Approved lessons → memory/approved_lessons.yaml.
    
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
            logger.critical(f"Unexpected error during soul validation for {entity_name}: {e}", exc_info=True)
            return False, None

    def validate_dict(self, data: Any) -> None:
        """Verify a dictionary against the v6.1 soul schema.
        
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

        # --- Strict v6.1 Checks Below ---

        if "short" not in entity:
            raise SoulValidationError("Missing required field in v6.1 soul: {'short'}")

        # Forbidden-field checks — fields that existed in v6.0 but don't belong in v6.1
        for forbidden in FORBIDDEN_ENTITY_BLOCKS:
            if forbidden in entity:
                raise SoulValidationError(
                    f"'{forbidden}' is a v6.0 field and must NOT exist in v6.1 souls. "
                    f"Remove it or migrate to memory/ subdirectory."
                )

        # Type and Value Constraints
        if not isinstance(entity["name"], str) or not entity["name"]:
            raise SoulValidationError("'name' must be a non-empty string")
        
        if not isinstance(entity["short"], str) or not (2 <= len(entity["short"]) <= 6):
            raise SoulValidationError("'short' must be a string between 2 and 6 characters")

        # v6.1: archetype is a description string, not constrained to fixed set
        # Optional fields: hierarchy_level, sovereignty_level, element, domain
        if "hierarchy_level" in entity:
            if not isinstance(entity["hierarchy_level"], int) or entity["hierarchy_level"] < 0:
                raise SoulValidationError("'hierarchy_level' must be a non-negative integer")
        if "sovereignty_level" in entity:
            if not isinstance(entity["sovereignty_level"], int) or not (1 <= entity["sovereignty_level"] <= 10):
                raise SoulValidationError("'sovereignty_level' must be an integer between 1 and 10")

        # v6.1: optional blocks with type validation
        if "identity" in data:
            identity = data["identity"]
            if not isinstance(identity, dict):
                raise SoulValidationError("'identity' block must be a dictionary")

        if "directives" in data:
            directives = data["directives"]
            if not isinstance(directives, list):
                raise SoulValidationError("'directives' must be a list")
            for d in directives:
                if not isinstance(d, dict) or "id" not in d or "rule" not in d:
                    raise SoulValidationError(
                        "Each directive must have 'id' and 'rule' fields"
                    )

        if "team" in data:
            team = data["team"]
            if not isinstance(team, dict):
                raise SoulValidationError("'team' block must be a dictionary")

        # Memory directory validation — check that memory/ subdirectory exists
        safe_name = entity["name"].lower().replace(" ", "_").replace("'", "")
        memory_dir = self.entities_data_dir / safe_name / "memory"
        if not memory_dir.exists():
            logger.warning(
                "Entity %s has no memory/ directory. "
                "v6.1 requires memory/sessions.yaml, memory/proposed_lessons.yaml, "
                "and memory/approved_lessons.yaml.",
                entity["name"],
            )

        # v6.1: lessons_learned is OPTIONAL and not validated for content structure
        if "lessons_learned" in entity:
            if not isinstance(entity["lessons_learned"], list):
                raise SoulValidationError("'lessons_learned' must be a list if present")

    def get_fallback_soul(self, entity_name: str) -> Dict[str, Any]:
        """Generate a minimal safe soul dictionary for fallback recovery.
        
        v6.1 lean schema — only entity block with identity.
        
        [id-soft: doom-1993] Lazy Deletion — provides a safe baseline to prevent
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
                    "live_feed": f"I post to {entity_name.upper()}_LIVE_FEED after each major task.",
                    "hivemind": "I declare presence via hivemind_post_context at session start.",
                },
            },
        }
