# Gap R16: pydantic v2 Migration Patterns

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-6.2 (soul_validator.py migration)
**Status:** ✅ RESOLVED

## Summary
pydantic v2 replaces v1's `parse_obj`/`dict()`/`@root_validator`/`orm_mode` with `model_validate`/`model_dump`/`@model_validator`/`model_config = ConfigDict(from_attributes=True)`. Migration is mechanical and well-documented; the engine should pin `pydantic>=2.7` and migrate `soul_validator.py` accordingly.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| pydantic v2 migration guide | https://docs.pydantic.dev/latest/migration/ | 2026 | Canonical v1→v2 mapping |
| pydantic core docs (model_validate) | https://docs.pydantic.dev/latest/ | 2026 | API reference |

## Findings
- **Construction**: v1 `Model.parse_obj(data)` → v2 `Model.model_validate(data)`. `Model(**data)` still works.
- **Serialization**: v1 `obj.dict()` → v2 `obj.model_dump()`. `obj.model_dump_json()` for JSON.
- **Validators**: v1 `@root_validator` → v2 `@model_validator(mode='before')` (or `mode='after'`); v1 `@validator` → v2 `@field_validator`.
- **ORM**: v1 `class Config: orm_mode = True` → v2 `model_config = ConfigDict(from_attributes=True)`.
- **Introspection**: `Model.model_fields` (typed dict) replaces `Model.__fields__`.
- **Config**: `model_config = ConfigDict(...)` replaces the nested `Config` class.

## Recommendation
Migrate `src/omega/oracle/soul_validator.py` (and any other pydantic models) to v2:
1. `parse_obj` → `model_validate`; `dict()` → `model_dump()`.
2. `@root_validator` → `@model_validator(mode='before')`; `@validator` → `@field_validator`.
3. `orm_mode=True` → `model_config = ConfigDict(from_attributes=True)`.
4. Pin `pydantic>=2.7` in `.venv` (M24). Add contract tests asserting `isinstance(model.model_validate(x), Model)` per T21.
5. Grep the repo for `parse_obj|@root_validator|orm_mode|__fields__` to find all v1 call sites before cutting over.

## Confidence
**HIGH** — pydantic v2 is stable (released 2023) with an exhaustive official migration guide.

## Remaining Unknowns
- Exact count of v1 call sites in the repo (requires a grep audit at implementation time).
- Whether any model relies on v1-only `validate_assignment` or `arbitrary_types_allowed` edge cases.
