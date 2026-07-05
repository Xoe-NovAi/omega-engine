"""M21 Gate Integrity: Contract Tests for Soul Distiller.

[M21: Gate Integrity Mandate] The soul distiller must write to
proposed_lessons.yaml (NOT soul.yaml) to preserve soul integrity
during the Staging Gate review workflow. These tests verify the
fix for the "soul distiller poison loop" (D-kal-173).

Test Plan:
  1. distill_and_save() writes to proposed_lessons.yaml, NOT soul.yaml
  2. distill_and_save() creates proposed_lessons.yaml if missing
  3. L1/L2/L3 entries appear under the 'proposals:' section
  4. soul.yaml is NOT modified by any soul distiller operation
  5. Default section is 'proposals' (not 'embodied_experiences')
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from omega.oracle.soul_distiller import SoulDistiller, DistillationEntry


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def temp_entities_dir():
    """Create a temporary entities directory with a test entity."""
    tmp_dir = tempfile.mkdtemp()
    entity_dir = Path(tmp_dir) / "test_entity"
    entity_dir.mkdir(parents=True)
    # Create a minimal soul.yaml (must exist for the entity to be valid)
    soul_path = entity_dir / "soul.yaml"
    soul_path.write_text(
        "soul_version: '6.1'\n"
        "entity: test_entity\n"
        "directives:\n"
        "  core_identity: Test entity\n"
    )
    yield tmp_dir, entity_dir, soul_path
    shutil.rmtree(tmp_dir)


@pytest.mark.anyio
async def test_distill_saves_to_proposed_lessons_not_soul(temp_entities_dir):
    """M21: Contract test — distill_and_save() writes to proposed_lessons.yaml, NOT soul.yaml.
    
    The soul distiller poison loop fix (D-kal-173) redirects writes from
    soul.yaml to proposed_lessons.yaml. This test verifies that:
    1. proposed_lessons.yaml is created/updated
    2. soul.yaml is NOT modified (content unchanged)
    3. The 'proposals' section in proposed_lessons.yaml contains the entries
    """
    tmp_dir, entity_dir, soul_path = temp_entities_dir
    distiller = SoulDistiller(str(tmp_dir))
    
    # Record soul.yaml content before
    soul_before = soul_path.read_text()
    
    # Run distill_and_save
    result = await distiller.distill_and_save(
        session_transcript="Session: Made architectural decision to fix soul distiller poison loop. Decided to redirect writes to proposed_lessons.yaml.",
        entity_name="test_entity",
    )
    
    assert result is True, "distill_and_save() should return True on success"
    
    # Verify soul.yaml is UNCHANGED
    soul_after = soul_path.read_text()
    assert soul_after == soul_before, (
        "soul.yaml was modified by soul distiller! "
        "The poison loop fix is not working — writes are still going to soul.yaml."
    )
    
    # Verify proposed_lessons.yaml EXISTS
    lessons_path = entity_dir / "proposed_lessons.yaml"
    assert lessons_path.exists(), (
        "proposed_lessons.yaml was not created. "
        "The soul distiller should write to proposed_lessons.yaml."
    )
    
    # Verify the 'proposals' section exists and contains L1/L2/L3 entries
    content = lessons_path.read_text()
    assert "proposals:" in content, (
        "proposed_lessons.yaml should contain a 'proposals:' section, "
        f"got:\n{content}"
    )
    assert "L1_" in content or "L1_narrative" in content, (
        "proposed_lessons.yaml should contain L1 narrative entries, "
        f"got:\n{content}"
    )
    assert "L2_" in content or "L2_insight" in content, (
        "proposed_lessons.yaml should contain L2 insight entries, "
        f"got:\n{content}"
    )
    assert "L3_" in content or "L3_principle" in content, (
        "proposed_lessons.yaml should contain L3 principle entries, "
        f"got:\n{content}"
    )


def test_distill_creates_proposed_lessons_if_missing(temp_entities_dir):
    """M21: Contract test — distill_and_save() creates proposed_lessons.yaml if missing.
    
    If an entity has no proposed_lessons.yaml yet, the soul distiller
    should create one with a minimal 'proposals:' section rather than
    failing silently.
    """
    tmp_dir, entity_dir, soul_path = temp_entities_dir
    
    # Verify proposed_lessons.yaml does NOT exist before
    lessons_path = entity_dir / "proposed_lessons.yaml"
    assert not lessons_path.exists(), "Precondition failed: proposed_lessons.yaml should not exist yet"
    
    distiller = SoulDistiller(str(tmp_dir))
    result = distiller.distill_and_save(
        session_transcript="Session: First session for this entity.",
        entity_name="test_entity",
    )
    
    assert result is True, "distill_and_save() should create proposed_lessons.yaml on first call"
    assert lessons_path.exists(), "proposed_lessons.yaml should be created by distill_and_save()"


def test_distill_default_section_is_proposals(temp_entities_dir):
    """M21: Contract test — default section is 'proposals', not 'embodied_experiences'.
    
    The v6.1 soul architecture protocol changes the default section from
    'embodied_experiences' (v6.0, soul.yaml) to 'proposals' (v6.1,
    proposed_lessons.yaml). This test verifies the default.
    """
    tmp_dir, entity_dir, soul_path = temp_entities_dir
    
    # Check the class default directly
    assert SoulDistiller.distill_and_save.__defaults__ is not None, (
        "distill_and_save should have default arguments"
    )
    # The default section is the last positional arg with a default
    # distill_and_save(self, session_transcript, entity_name, source_trace_id=None, section="proposals")
    import inspect
    sig = inspect.signature(SoulDistiller.distill_and_save)
    params = list(sig.parameters.values())
    section_param = [p for p in params if p.name == "section"]
    assert len(section_param) > 0, "distill_and_save must have a 'section' parameter"
    
    default_val = section_param[0].default
    assert default_val == "proposals", (
        f"Default section should be 'proposals', got '{default_val}'. "
        "The poison loop fix changed the wrong default."
    )


def test_soul_yaml_remains_readable_after_distill(temp_entities_dir):
    """M21: Contract test — soul.yaml remains valid YAML after soul distiller runs.
    
    The primary risk of the poison loop was that concurrent or sequential
    distiller calls might corrupt soul.yaml. Since the fix now writes to
    proposed_lessons.yaml, soul.yaml should remain pristine and parseable.
    """
    tmp_dir, entity_dir, soul_path = temp_entities_dir
    distiller = SoulDistiller(str(tmp_dir))
    
    # Run multiple distill calls to stress-test
    for i in range(3):
        result = distiller.distill_and_save(
            session_transcript=f"Session {i}: Test session number {i}.",
            entity_name="test_entity",
        )
        assert result is True, f"distill_and_save() failed on iteration {i}"
    
    # soul.yaml should still be valid YAML
    import yaml
    try:
        parsed = yaml.safe_load(soul_path.read_text())
        assert parsed is not None, "soul.yaml is empty or invalid"
        assert isinstance(parsed, dict), "soul.yaml should parse to a dict"
        assert parsed.get("entity") == "test_entity", "soul.yaml entity field should be preserved"
        assert parsed.get("soul_version") == "6.1", "soul.yaml version should be preserved"
    except yaml.YAMLError as e:
        pytest.fail(f"soul.yaml is no longer valid YAML after soul distiller runs:\n{e}")


def test_proposed_lessons_is_valid_yaml(temp_entities_dir):
    """M21: Contract test — proposed_lessons.yaml is valid YAML.
    
    The soul distiller must produce valid YAML that the Staging Gate TUI
    can parse. Broken YAML in proposed_lessons.yaml would crash the TUI.
    """
    tmp_dir, entity_dir, soul_path = temp_entities_dir
    distiller = SoulDistiller(str(tmp_dir))
    
    # Run distill
    distiller.distill_and_save(
        session_transcript="Session: Testing YAML output validity.",
        entity_name="test_entity",
    )
    
    lessons_path = entity_dir / "proposed_lessons.yaml"
    content = lessons_path.read_text()
    
    # Parse as YAML — should not raise
    import yaml
    try:
        parsed = yaml.safe_load(content)
        assert parsed is not None, "proposed_lessons.yaml parsed to None"
        assert isinstance(parsed, dict), (
            f"proposed_lessons.yaml should be a dict, got {type(parsed)}"
        )
        assert "proposals" in parsed, "proposed_lessons.yaml should have 'proposals' key"
    except yaml.YAMLError as e:
        pytest.fail(f"proposed_lessons.yaml is not valid YAML:\n{content}\nError: {e}")
