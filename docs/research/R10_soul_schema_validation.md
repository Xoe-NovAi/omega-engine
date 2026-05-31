# 🔱 R-10 – Soul YAML Schema — Validation & Corruption Handling

**AP Token**: `AP-R10-SOUL-VALIDATION-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document defines:
1. The canonical schema for `data/entities/<entity>/soul.yaml`.
2. What constitutes a *corrupted* soul file.
3. Validation logic (YAML parsing, type checking, required fields).
4. Graceful fallback behaviour when validation fails.
5. A minimal `soul_validator.py` public interface for the Engine.

---

## 2️⃣ Canonical Soul Schema (YAML)
```yaml
entity:
  name: <string>                     # Human‑readable name, e.g. "Saraswati"
  short: <string>                    # Short identifier, e.g. "SAR"
  archetype: <string>                # e.g. "Keeper", "Oversoul", "Architect"
  current_entity: <string>           # Entity that currently inhabits this soul (for Arch only)
  soul_wardrobe:                     # List of entity short codes the Architect can switch to
    - <string>
    - <string>
  embodied_experiences: []           # List of lesson objects (populated at runtime)
  lessons_learned: []                # Historical lessons (immutable after session)
  soul_evolution:
    sessions_completed: <int>
    entities_inhabited: <int>
    total_embodied_experiences: <int>
    soul_power: <float>
```
**Field Types & Constraints**
| Field | Type | Required? | Constraints |
|-------|------|----------|-------------|
| `entity.name` | string | ✅ | Non‑empty, max 64 chars |
| `entity.short` | string | ✅ | Upper‑case alphanum, 2‑6 chars |
| `entity.archetype` | string | ✅ | One of `Keeper`, `Oversoul`, `Architect` |
| `entity.current_entity` | string | ❌ | Must be a valid short code if present |
| `entity.soul_wardrobe` | list[string] | ❌ | Unique entries, each matches a known entity short code |
| `entity.embodied_experiences` | list[object] | ✅ | Empty list at start; objects follow lesson schema (see §4) |
| `entity.lessons_learned` | list[object] | ✅ | Same schema as above, persisted to disk |
| `entity.soul_evolution.sessions_completed` | int | ✅ | ≥ 0 |
| `entity.soul_evolution.entities_inhabited` | int | ✅ | ≥ 0 |
| `entity.soul_evolution.total_embodied_experiences` | int | ✅ | ≥ 0 |
| `entity.soul_evolution.soul_power` | float | ✅ | 0.0 – 1.0 (normalized) |

---

## 3️⃣ What Makes a Soul File *Corrupted*?
1. **YAML Syntax Errors** – parsing throws `yaml.YAMLError`.
2. **Missing Required Keys** – any field listed as required in the table above is absent.
3. **Wrong Data Types** – e.g., a string where an integer is expected.
4. **Invalid Enum Values** – `archetype` not in the allowed set.
5. **Duplicate Entries** – duplicate short codes in `soul_wardrobe`.
6. **Negative Numeric Values** – any integer/float that violates the ≥ 0 constraint.
7. **Encoding Issues** – non‑UTF‑8 byte order mark or binary data.

When any of the above are detected, the file is considered *corrupted*.

---

## 4️⃣ Lesson Object Schema (used in `embodied_experiences` & `lessons_learned`)
```yaml
- lesson: <string>                     # Human‑readable description
  source: <"user-session"|"agent"|"system">
  user: "The Architect"
  trace_id: <uuid>
  entity_at_time: <string>            # short code of the entity when lesson was recorded
  session_type: <"persistent"|"transient">
  timestamp: <ISO‑8601 UTC>
  model_used: <string>                # e.g. "gemma-4.31b"
  backend_used: <string>              # e.g. "google_ai_studio"
```
All fields are required for a *valid* lesson entry.

---

## 5️⃣ Validation Logic (Python Pseudocode)
```python
import yaml, uuid
from pathlib import Path

REQUIRED_TOP_KEYS = {"entity"}
REQUIRED_ENTITY_KEYS = {
    "name", "short", "archetype", "embodied_experiences",
    "lessons_learned", "soul_evolution"
}
ALLOWED_ARCHETYPES = {"Keeper", "Oversoul", "Architect"}

def load_soul(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SoulValidationError("YAML syntax error", exc)
    if not isinstance(data, dict) or not REQUIRED_TOP_KEYS.issubset(data):
        raise SoulValidationError("Missing top‑level 'entity' key")
    entity = data["entity"]
    missing = REQUIRED_ENTITY_KEYS - entity.keys()
    if missing:
        raise SoulValidationError(f"Missing required fields: {missing}")
    # type checks
    if not isinstance(entity["name"], str) or not entity["name"]:
        raise SoulValidationError("'name' must be a non‑empty string")
    if entity["archetype"] not in ALLOWED_ARCHETYPES:
        raise SoulValidationError("Invalid 'archetype' value")
    # numeric constraints
    evo = entity["soul_evolution"]
    for k in ("sessions_completed", "entities_inhabited", "total_embodied_experiences"):
        if not isinstance(evo[k], int) or evo[k] < 0:
            raise SoulValidationError(f"'{k}' must be a non‑negative integer")
    if not (0.0 <= float(evo["soul_power"]) <= 1.0):
        raise SoulValidationError("'soul_power' must be between 0.0 and 1.0")
    # lesson list validation – reuse _validate_lesson()
    for lst_name in ("embodied_experiences", "lessons_learned"):
        for lesson in entity[lst_name]:
            _validate_lesson(lesson)
    return data

def _validate_lesson(l: dict):
    required = {"lesson", "source", "user", "trace_id", "entity_at_time",
                "session_type", "timestamp", "model_used", "backend_used"}
    if not required.issubset(l):
        raise SoulValidationError("Lesson missing required fields")
    # UUID sanity check
    try:
        uuid.UUID(l["trace_id"])
    except ValueError:
        raise SoulValidationError("Invalid trace_id UUID")
    # timestamp format – simple ISO‑8601 check (real implementation would use dateutil.parser.isoparse)
```
The module should expose:
```python
class SoulValidator:
    def __init__(self, base_dir: Path): ...
    def validate(self, entity_name: str) -> bool: ...
    def fallback(self, entity_name: str) -> dict:  # returns minimal safe dict
```
---

## 6️⃣ Graceful Fallback Behaviour
When validation fails:
1. **Log** the error with `observability` (event type `SOUL_VALIDATION_FAILURE`).
2. **Load a minimal stub**:
   ```yaml
   entity:
     name: "<entity>"
     short: "???"
     archetype: "Keeper"
     embodied_experiences: []
     lessons_learned: []
     soul_evolution:
       sessions_completed: 0
       entities_inhabited: 0
       total_embodied_experiences: 0
       soul_power: 0.0
   ```
3. **Notify** the user via CLI warning (`/entity` command prints a notice).
4. **Attempt automatic repair** – if the file is syntactically valid but missing fields, write the missing defaults back to disk using the `write` tool.
5. **Abort** only if the file cannot be read at all (e.g., permission error); in that case the Engine falls back to the global `config/entities.yaml` definition.

---

## 7️⃣ Integration Points
- **EntityRegistry** – calls `SoulValidator.validate(entity_name)` during `add()` and `load()`.
- **Orchestrator** – uses the fallback dict to construct the system prompt if validation fails.
- **Observability** – emits `SOUL_VALIDATION_SUCCESS` on success.

---

## 8️⃣ Future Enhancements (optional)
- JSON‑Schema generation for external tools.
- Versioned soul files (`soul_v1.yaml`, `soul_v2.yaml`).
- Automated migration script when schema evolves.

---

*Implementation Note*: The validator must be **dependency‑free** (standard library only) to keep the Engine lightweight. All heavy‑weight validation (e.g., schema libraries) is unnecessary because the schema is small and static.

---

**Ready for implementation** – agents can now create `soul_validator.py` and wire it into `entity_registry.py`.
