# 🔱 Cohort Registry Tests
# ⬡ OMEGA ⬡ RESEARCHER ⬡ COHORT-REGISTRY ⬡ TEST
# AP: AP-COHORT-REGISTRY-TEST-v1.0.0
#
# Tests: schema validation, pydantic types, M34 liveness cross-check, atomic writes.
# Gate: all tests must pass for B1 completion.

"""
Test Suite for COHORT-REGISTRY-001 (Task B1)

Validation layers tested:
1. jsonschema structural validation (schema v2020-12)
2. Pydantic type safety (field validators)
3. M34 liveness cross-check (subagent_ids → ACTIVE_SUBAGENTS.json)
4. Atomic write correctness (crash safety)
5. Business logic (create, update, resume, list)
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.oracle.cohort_registry import (
    CohortRegistry,
    CohortStatus,
    CohortType,
    VALID_DISPATCHERS,
    ValidationError,
    LivenessWarning,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_registry(tmp_path: Path) -> CohortRegistry:
    """Create a CohortRegistry with temp files."""
    registry_path = tmp_path / "COHORT_REGISTRY.json"
    schema_path = Path(__file__).parent.parent / "data" / "registry" / "cohort_registry_schema.json"
    return CohortRegistry(
        registry_path=registry_path,
        schema_path=schema_path,
    )


@pytest.fixture
def real_registry() -> CohortRegistry:
    """Use the actual registry on disk (read-only for tests)."""
    return CohortRegistry()


# ── Test 1: Schema file exists and is valid JSON ────────────────────────────

class TestSchemaFile:
    def test_schema_file_exists(self):
        schema_path = Path("data/registry/cohort_registry_schema.json")
        assert schema_path.exists(), f"Schema not found at {schema_path}"

    def test_schema_is_valid_json(self):
        schema_path = Path("data/registry/cohort_registry_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert schema.get("$id") == "https://omega-engine/cohort_registry/v1"

    def test_schema_has_required_definitions(self):
        schema_path = Path("data/registry/cohort_registry_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        assert "$defs" in schema
        assert "cohort" in schema["$defs"]
        cohort_def = schema["$defs"]["cohort"]
        assert "required" in cohort_def
        assert "cohort_id" in cohort_def["required"]


# ── Test 2: Registry instance exists and is valid ───────────────────────────

class TestRegistryInstance:
    def test_instance_file_exists(self):
        reg_path = Path("data/registry/COHORT_REGISTRY.json")
        assert reg_path.exists(), f"Registry not found at {reg_path}"

    def test_instance_is_valid_json(self):
        reg_path = Path("data/registry/COHORT_REGISTRY.json")
        with open(reg_path) as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert "cohorts" in data

    def test_instance_has_alchemical_cohort(self):
        reg_path = Path("data/registry/COHORT_REGISTRY.json")
        with open(reg_path) as f:
            data = json.load(f)
        assert "cohort_alchemical_001" in data["cohorts"]
        c = data["cohorts"]["cohort_alchemical_001"]
        assert c["dispatched_by"] == "grokster"
        assert c["cohort_type"] == "RESEARCH_PAIR"
        assert c["status"] == "COMPLETED"


# ── Test 3: jsonschema validation ───────────────────────────────────────────

class TestJsonSchemaValidation:
    def test_valid_registry_passes(self, tmp_registry: CohortRegistry):
        """A freshly created registry should pass schema validation."""
        errors = tmp_registry.validate_registry()
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_invalid_version_fails(self, tmp_registry: CohortRegistry, tmp_path: Path):
        """Version != '1.0' should fail."""
        data = tmp_registry.read()
        data["version"] = "2.0"
        tmp_registry._atomic_write(data)
        errors = tmp_registry.validate_registry()
        assert any(e.severity == "error" for e in errors)

    def test_missing_cohorts_fails(self, tmp_registry: CohortRegistry, tmp_path: Path):
        """Missing 'cohorts' key should fail."""
        data = tmp_registry.read()
        del data["cohorts"]
        tmp_registry._atomic_write(data)
        errors = tmp_registry.validate_registry()
        assert any(e.severity == "error" for e in errors)

    def test_invalid_cohort_type_fails(self, tmp_registry: CohortRegistry):
        """Invalid cohort_type should fail pydantic validation."""
        # Manually inject invalid data
        data = tmp_registry.read()
        data["cohorts"]["bad_cohort"] = {
            "cohort_id": "cohort_bad00000001",
            "dispatched_by": "kali",
            "subagent_ids": ["ses_test123456"],
            "cohort_type": "INVALID_TYPE",
            "created_at": "2026-08-30T00:00:00Z",
            "status": "ALIVE",
            "resumption_count": 0,
            "resumption_history": [],
            "m34_registry_ref": "ACTIVE_SUBAGENTS.json",
            "tags": [],
        }
        tmp_registry._atomic_write(data)
        errors = tmp_registry.validate_registry()
        # Should have at least one error (pydantic or jsonschema)
        assert len(errors) > 0


# ── Test 4: Pydantic type validation ────────────────────────────────────────

class TestPydanticValidation:
    def test_create_cohort_valid(self, tmp_registry: CohortRegistry):
        """Creating a valid cohort should succeed."""
        cohort_id = tmp_registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_abc12345678"],
            cohort_type=CohortType.EIS_BURST,
            task_brief="Test research burst",
        )
        assert cohort_id.startswith("cohort_")
        c = tmp_registry.get_cohort(cohort_id)
        assert c is not None
        assert c["dispatched_by"] == "kali"
        assert c["status"] == "ALIVE"

    def test_create_cohort_invalid_dispatcher(self, tmp_registry: CohortRegistry):
        """Invalid dispatched_by should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid dispatched_by"):
            tmp_registry.create_cohort(
                dispatched_by="invalid_entity",
                subagent_ids=["ses_abc12345678"],
                cohort_type=CohortType.EIS_BURST,
            )

    def test_create_cohort_empty_subagents(self, tmp_registry: CohortRegistry):
        """Empty subagent_ids should raise ValueError."""
        with pytest.raises(ValueError, match="subagent_ids cannot be empty"):
            tmp_registry.create_cohort(
                dispatched_by="kali",
                subagent_ids=[],
                cohort_type=CohortType.EIS_BURST,
            )

    def test_create_cohort_invalid_session_id(self, tmp_registry: CohortRegistry):
        """Invalid session_id format should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid session_id"):
            tmp_registry.create_cohort(
                dispatched_by="kali",
                subagent_ids=["invalid_session"],
                cohort_type=CohortType.EIS_BURST,
            )

    def test_update_status_valid(self, tmp_registry: CohortRegistry):
        """Updating status should work."""
        cid = tmp_registry.create_cohort(
            dispatched_by="researcher",
            subagent_ids=["ses_test00111111"],
            cohort_type=CohortType.RESEARCH_PAIR,
        )
        tmp_registry.update_status(cid, CohortStatus.INTERRUPTED, reason="Esc x2")
        c = tmp_registry.get_cohort(cid)
        assert c["status"] == "INTERRUPTED"

    def test_resume_cohort_valid(self, tmp_registry: CohortRegistry):
        """Resuming a cohort with valid decisions should work."""
        cid = tmp_registry.create_cohort(
            dispatched_by="grokster",
            subagent_ids=["ses_resume0001", "ses_resume0002"],
            cohort_type=CohortType.RESEARCH_PAIR,
        )
        tmp_registry.update_status(cid, CohortStatus.INTERRUPTED, reason="test")
        tmp_registry.resume_cohort(
            cid,
            resumed_by="lilith",
            decisions={"ses_resume0001": "resume", "ses_resume0002": "abandon"},
            reason="Recovery",
        )
        c = tmp_registry.get_cohort(cid)
        assert c["status"] == "ALIVE"  # Resume sets back to ALIVE
        assert c["resumption_count"] == 1

    def test_resume_invalid_decision(self, tmp_registry: CohortRegistry):
        """Invalid decision in resume should raise ValueError."""
        cid = tmp_registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_baddec001"],
            cohort_type=CohortType.EIS_BURST,
        )
        with pytest.raises(ValueError, match="Invalid decision"):
            tmp_registry.resume_cohort(
                cid,
                resumed_by="kali",
                decisions={"ses_baddec001": "invalid_action"},
            )

    def test_nonexistent_cohort_raises(self, tmp_registry: CohortRegistry):
        """Updating a nonexistent cohort should raise KeyError."""
        with pytest.raises(KeyError, match="Cohort not found"):
            tmp_registry.update_status("cohort_nonexistent00", CohortStatus.FAILED)


# ── Test 5: M34 Liveness Cross-Check ───────────────────────────────────────

class TestM34LivenessCrossCheck:
    def test_liveness_no_m34_registry(self, tmp_path: Path):
        """When M34 registry doesn't exist, liveness check returns empty."""
        reg_path = tmp_path / "COHORT.json"
        m34_path = tmp_path / "NONEXISTENT.json"
        registry = CohortRegistry(
            registry_path=reg_path,
            m34_registry_path=m34_path,
        )
        warnings = registry.check_m34_liveness()
        assert len(warnings) == 0  # No M34 = no cross-check possible

    def test_liveness_subagent_found(self, tmp_path: Path):
        """When subagent exists in M34, no warning."""
        # Create M34 registry with a session
        m34_path = tmp_path / "ACTIVE_SUBAGENTS.json"
        m34_data = {
            "version": "1.1",
            "updated": "2026-08-30T00:00:00Z",
            "sessions": {
                "ses_live12345678": {
                    "session_id": "ses_live12345678",
                    "status": "ALIVE",
                    "agent": "jem",
                }
            },
        }
        with open(m34_path, "w") as f:
            json.dump(m34_data, f)

        # Create cohort with that subagent
        reg_path = tmp_path / "COHORT.json"
        registry = CohortRegistry(
            registry_path=reg_path,
            m34_registry_path=m34_path,
        )
        registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_live12345678"],
            cohort_type=CohortType.EIS_BURST,
        )

        warnings = registry.check_m34_liveness()
        assert len(warnings) == 0

    def test_liveness_subagent_missing(self, tmp_path: Path):
        """When subagent NOT in M34, warning is raised."""
        m34_path = tmp_path / "ACTIVE_SUBAGENTS.json"
        m34_data = {
            "version": "1.1",
            "updated": "2026-08-30T00:00:00Z",
            "sessions": {},
        }
        with open(m34_path, "w") as f:
            json.dump(m34_data, f)

        reg_path = tmp_path / "COHORT.json"
        registry = CohortRegistry(
            registry_path=reg_path,
            m34_registry_path=m34_path,
        )
        registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_deadbeef00001"],
            cohort_type=CohortType.EIS_BURST,
        )

        warnings = registry.check_m34_liveness()
        assert len(warnings) == 1
        assert warnings[0].subagent_id == "ses_deadbeef00001"
        assert warnings[0].cohort_id.startswith("cohort_")


# ── Test 6: Atomic Write Correctness ────────────────────────────────────────

class TestAtomicWrite:
    def test_write_produces_valid_json(self, tmp_registry: CohortRegistry):
        """Each write produces valid, parseable JSON."""
        tmp_registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_write00001"],
            cohort_type=CohortType.EIS_BURST,
        )
        with open(tmp_registry.path) as f:
            data = json.load(f)
        assert "cohorts" in data

    def test_multiple_writes_maintain_integrity(self, tmp_registry: CohortRegistry):
        """10 sequential writes produce valid JSON with all cohorts."""
        for i in range(10):
            tmp_registry.create_cohort(
                dispatched_by="kali",
                subagent_ids=[f"ses_iter{i:010d}"],
                cohort_type=CohortType.EIS_BURST,
                task_brief=f"Iteration {i}",
            )
        data = tmp_registry.read()
        assert len(data["cohorts"]) == 10

    def test_lock_file_cleaned_up(self, tmp_registry: CohortRegistry):
        """Lock file should be removed after write."""
        tmp_registry.create_cohort(
            dispatched_by="kali",
            subagent_ids=["ses_lock00001"],
            cohort_type=CohortType.EIS_BURST,
        )
        lock_path = tmp_registry.path.with_suffix(".lock")
        assert not lock_path.exists(), "Lock file not cleaned up"


# ── Test 7: Real Registry Validation ────────────────────────────────────────

class TestRealRegistry:
    def test_real_registry_validates(self, real_registry: CohortRegistry):
        """The actual COHORT_REGISTRY.json should pass all validation."""
        errors = real_registry.validate_registry()
        errors_only = [e for e in errors if e.severity == "error"]
        assert len(errors_only) == 0, f"Validation errors: {[e.message for e in errors_only]}"

    def test_real_registry_schema_matches(self):
        """The real schema file should be loadable by jsonschema."""
        import jsonschema
        schema_path = Path("data/registry/cohort_registry_schema.json")
        reg_path = Path("data/registry/COHORT_REGISTRY.json")
        with open(schema_path) as f:
            schema = json.load(f)
        with open(reg_path) as f:
            data = json.load(f)
        # Should not raise
        jsonschema.validate(data, schema)


# ── Test 8: Enum Constraints ────────────────────────────────────────────────

class TestEnumConstraints:
    def test_all_cohort_types_in_schema(self):
        """All CohortType values should be in the schema."""
        schema_path = Path("data/registry/cohort_registry_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        schema_types = set(schema["$defs"]["cohort"]["properties"]["cohort_type"]["enum"])
        code_types = {ct.value for ct in CohortType}
        assert schema_types == code_types, f"Mismatch: schema={schema_types}, code={code_types}"

    def test_all_cohort_statuses_in_schema(self):
        """All CohortStatus values should be in the schema."""
        schema_path = Path("data/registry/cohort_registry_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        schema_statuses = set(schema["$defs"]["cohort"]["properties"]["status"]["enum"])
        code_statuses = {cs.value for cs in CohortStatus}
        assert schema_statuses == code_statuses, f"Mismatch: schema={schema_statuses}, code={code_statuses}"

    def test_all_dispatchers_in_schema(self):
        """All VALID_DISPATCHERS should be in the schema."""
        schema_path = Path("data/registry/cohort_registry_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        schema_dispatchers = set(schema["$defs"]["cohort"]["properties"]["dispatched_by"]["enum"])
        assert schema_dispatchers == VALID_DISPATCHERS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
