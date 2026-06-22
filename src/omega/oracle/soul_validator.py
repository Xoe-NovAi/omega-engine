# AP: AP-PR-READINESS-v1.0.0
# AP Token: AP-R10-SOUL-VALIDATION-v1.0.0
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
REQUIRED_ENTITY_KEYS = {
    "name", "short", "archetype", "embodied_experiences",
    "lessons_learned", "soul_evolution"
}
ALLOWED_ARCHETYPES = {"Keeper", "Oversoul", "Architect"}

class SoulValidator:
    """Sovereign validator for entity soul files.
    
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
        except Exception as e:
            logger.critical(f"Unexpected error during soul validation for {entity_name}: {e}", exc_info=True)
            return False, None

    def validate_dict(self, data: Any) -> None:
        """Verify a dictionary against the R-10 soul schema.
        
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

        # Type and Value Constraints
        if not isinstance(entity["name"], str) or not entity["name"]:
            raise SoulValidationError("'name' must be a non-empty string")
        
        if not isinstance(entity["short"], str) or not (2 <= len(entity["short"]) <= 6):
            raise SoulValidationError("'short' must be a string between 2 and 6 characters")

        if entity["archetype"] not in ALLOWED_ARCHETYPES:
            raise SoulValidationError(f"Invalid 'archetype' {entity['archetype']}. Must be one of {ALLOWED_ARCHETYPES}")

        # Numeric constraints in soul_evolution
        evo = entity["soul_evolution"]
        if not isinstance(evo, dict):
            raise SoulValidationError("'soul_evolution' must be a dictionary")

        for k in ("sessions_completed", "entities_inhabited", "total_embodied_experiences"):
            if k not in evo or not isinstance(evo[k], int) or evo[k] < 0:
                raise SoulValidationError(f"'{k}' must be a non-negative integer")

        if "soul_power" not in evo or not isinstance(evo["soul_power"], (int, float)) or not (0.0 <= float(evo["soul_power"]) <= 1.0):
            raise SoulValidationError("'soul_power' must be a float between 0.0 and 1.0")

        # Lesson validation
        for lst_name in ("embodied_experiences", "lessons_learned"):
            lessons = entity.get(lst_name, [])
            if not isinstance(lessons, list):
                raise SoulValidationError(f"'{lst_name}' must be a list")
            for lesson in lessons:
                self._validate_lesson(lesson)

    def _validate_lesson(self, lesson: Any) -> None:
        """Verify a single lesson object against the R-10 schema."""
        if not isinstance(lesson, dict):
            raise SoulValidationError("Lesson entry must be a dictionary")

        required = {"lesson", "source", "user", "trace_id", "entity_at_time",
                    "session_type", "timestamp", "model_used", "backend_used"}
        if not required.issubset(lesson.keys()):
            raise SoulValidationError(f"Lesson missing required fields: {required - lesson.keys()}")

        try:
            uuid.UUID(str(lesson["trace_id"]))
        except ValueError:
            raise SoulValidationError(f"Invalid trace_id UUID: {lesson['trace_id']}")

    def get_fallback_soul(self, entity_name: str) -> Dict[str, Any]:
        """Generate a minimal safe soul dictionary for fallback recovery.
        
        [id-soft: doom-1993] Lazy Deletion — provides a safe baseline to prevent
        engine crash when soul is corrupted.
        """
        return {
            "entity": {
                "name": entity_name,
                "short": "???",
                "archetype": "Keeper",
                "embodied_experiences": [],
                "lessons_learned": [],
                "soul_evolution": {
                    "sessions_completed": 0,
                    "entities_inhabited": 0,
                    "total_embodied_experiences": 0,
                    "soul_power": 0.0
                }
            }
        }
