"""Tests for Sovereign Export Bundle (P0-4) — `.omega` entity portability.

Tests cover:
- Export a test entity → verify ZIP structure
- Import it back → verify round-trip integrity
- Verify checksums match
- Error handling for missing entities, invalid bundles
"""

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

from omega.cli.bundle import (
    _export_entity,
    _import_entity,
    _validate_checksums,
    _extract_session_metadata,
    _extract_recent_exchanges,
    _get_entities_dir,
    _get_bundles_dir,
)

# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_entity_dir(tmp_path, monkeypatch):
    """Create a minimal test entity structure in an isolated temp dir."""
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    entities_dir = tmp_path / "entities"
    entity_dir = entities_dir / "test_bundle_entity"
    memory_dir = entity_dir / "memory"
    knowledge_dir = entity_dir / "knowledge"
    workspace_dir = entity_dir / "workspace"

    memory_dir.mkdir(parents=True)
    knowledge_dir.mkdir(parents=True)
    workspace_dir.mkdir(parents=True)

    # soul.yaml
    soul = {
        "soul_version": "6.1",
        "entity": {
            "name": "TestBundleEntity",
            "short": "TB",
            "archetype": "Test Entity",
            "sovereignty_level": 3,
        },
        "identity": {
            "voice_summary": "A test entity for bundle export/import.",
            "values": ["testability", "simplicity"],
            "strengths": ["adaptability"],
            "growth_areas": [],
        },
        "directives": [
            {
                "id": "d-tb-001",
                "title": "Test Directive",
                "rule": "Be testable.",
                "rationale": "Testing ensures sovereignty.",
            }
        ],
    }
    with open(entity_dir / "soul.yaml", "w") as f:
        yaml.dump(soul, f, default_flow_style=False, sort_keys=False)

    # sessions.yaml
    sessions = [
        {
            "session_id": "ses_20260701_test_001",
            "created_at": "2026-07-01T10:00:00Z",
            "summary": "Test session for bundle export",
            "continuation": "Verify round-trip integrity",
        },
        {
            "session_id": "ses_20260701_test_002",
            "created_at": "2026-07-01T12:00:00Z",
            "summary": "Second test session",
            "continuation": "Check multiple sessions export",
        },
    ]
    with open(memory_dir / "sessions.yaml", "w") as f:
        yaml.dump(sessions, f, default_flow_style=False, sort_keys=False)

    # proposed_lessons.yaml
    proposals = {
        "proposals": [
            {
                "id": "tb-test-001",
                "category": "testing",
                "l1_narrative": "Test bundle export works.",
                "l2_insight": "Round-trip testing validates integrity.",
                "l3_universal_principle": "Export without import is half a feature.",
            }
        ]
    }
    with open(memory_dir / "proposed_lessons.yaml", "w") as f:
        yaml.dump(proposals, f, default_flow_style=False, sort_keys=False)

    # knowledge files
    knowledge_1 = "# Entity Knowledge\n\nThis is test knowledge for bundle export."
    with open(knowledge_dir / "test_knowledge.md", "w") as f:
        f.write(knowledge_1)

    knowledge_2 = "---\nid: test-002\ntitle: Another Knowledge File\n---\n\nMore content here."
    with open(knowledge_dir / "more_knowledge.md", "w") as f:
        f.write(knowledge_2)

    knowledge_index = {
        "entity": "TestBundleEntity",
        "updated": "2026-07-01T10:00:00Z",
        "topics": ["testing", "bundles"],
    }
    with open(knowledge_dir / "INDEX.yaml", "w") as f:
        yaml.dump(knowledge_index, f, default_flow_style=False, sort_keys=False)

    # workspace file
    ws_content = "# Workspace Note\n\nA temporary workspace file."
    with open(workspace_dir / "workspace_note.md", "w") as f:
        f.write(ws_content)

    return entity_dir


# ═══════════════════════════════════════════════════════════════════════
# Tests — Export
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.anyio
async def test_export_creates_bundle(test_entity_dir, tmp_path):
    """Exporting an entity creates a valid .omega.zip bundle."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))
    assert bundle_path.endswith(".omega.zip")
    assert Path(bundle_path).exists()
    assert Path(bundle_path).stat().st_size > 0


@pytest.mark.anyio
async def test_export_bundle_contents(test_entity_dir, tmp_path):
    """Exported bundle contains all expected files."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    with zipfile.ZipFile(bundle_path, "r") as zf:
        names = zf.namelist()

    # Required files
    assert "manifest.json" in names, "Missing manifest.json"
    assert "checksums.sha256" in names, "Missing checksums.sha256"
    assert "soul.yaml" in names, "Missing soul.yaml"

    # Sessions
    assert "sessions/session_metadata.json" in names, "Missing session metadata"

    # Knowledge
    assert "knowledge/index.json" in names, "Missing knowledge index"
    assert "knowledge/test_knowledge.md" in names, "Missing test_knowledge.md"
    assert "knowledge/more_knowledge.md" in names, "Missing more_knowledge.md"
    assert "knowledge/INDEX.yaml" in names, "Missing INDEX.yaml"

    # Proposed lessons
    assert "proposed_lessons.yaml" in names, "Missing proposed_lessons.yaml"

    # Workspace
    assert "workspace/workspace_note.md" in names, "Missing workspace_note.md"


@pytest.mark.anyio
async def test_export_manifest_structure(test_entity_dir, tmp_path):
    """Manifest.json has correct schema structure."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    with zipfile.ZipFile(bundle_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))

    assert manifest["schema_version"] == "1.0.0"
    assert manifest["bundle_version"] == "1.0.0"
    assert manifest["entity_name"] == "test_bundle_entity"
    assert "created_at" in manifest
    assert manifest["file_count"] > 0
    assert manifest["total_size_bytes"] > 0


@pytest.mark.anyio
async def test_export_checksums_validate(test_entity_dir, tmp_path):
    """Checksums in the bundle are valid SHA256."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    # Read bundle contents directly for validation
    with zipfile.ZipFile(bundle_path, "r") as zf:
        contents = {name: zf.read(name) for name in zf.namelist()}

    errors = _validate_checksums(contents)
    assert errors == [], f"Checksum validation failed: {errors}"


@pytest.mark.anyio
async def test_export_soul_yaml(test_entity_dir, tmp_path):
    """soul.yaml in the bundle matches the original."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    with zipfile.ZipFile(bundle_path, "r") as zf:
        soul_data = yaml.safe_load(zf.read("soul.yaml"))

    assert soul_data["entity"]["name"] == "TestBundleEntity"
    assert soul_data["entity"]["archetype"] == "Test Entity"
    assert soul_data["identity"]["values"] == ["testability", "simplicity"]


# ═══════════════════════════════════════════════════════════════════════
# Tests — Import
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.anyio
async def test_import_round_trip(test_entity_dir, tmp_path):
    """Importing an exported bundle reconstructs entity state accurately."""
    # Export
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    entity_dir = _get_entities_dir() / "test_bundle_entity"
    assert entity_dir.exists()

    # Check original proposed lessons exist
    original_proposals = entity_dir / "memory" / "proposed_lessons.yaml"
    assert original_proposals.exists()

    # Remove entity dir to verify clean import
    shutil.rmtree(str(entity_dir))
    assert not entity_dir.exists()

    # Import
    imported_name = await _import_entity(bundle_path, overwrite=True)
    assert imported_name == "test_bundle_entity"

    # Verify entity directory was recreated
    assert entity_dir.exists()
    assert (entity_dir / "soul.yaml").exists()

    # Verify soul content
    with open(entity_dir / "soul.yaml") as f:
        soul_data = yaml.safe_load(f)
    assert soul_data["entity"]["name"] == "TestBundleEntity"

    # Verify knowledge was imported
    knowledge_dir = entity_dir / "knowledge"
    assert knowledge_dir.exists()
    assert (knowledge_dir / "test_knowledge.md").exists()
    assert (knowledge_dir / "more_knowledge.md").exists()
    assert (knowledge_dir / "INDEX.yaml").exists()

    # Verify proposed lessons were imported
    assert (entity_dir / "memory" / "proposed_lessons.yaml").exists()

    # Verify sessions were reconstructed
    assert (entity_dir / "memory" / "sessions.yaml").exists()

    # Verify workspace was imported
    assert (entity_dir / "workspace" / "workspace_note.md").exists()


@pytest.mark.anyio
async def test_import_without_overwrite_fails_for_existing(test_entity_dir, tmp_path):
    """Importing without --overwrite fails if entity already exists."""
    bundle_path = await _export_entity("test_bundle_entity", str(tmp_path))

    # Entity dir already exists — should fail without overwrite
    with pytest.raises(ValueError, match="already exists"):
        await _import_entity(bundle_path, overwrite=False)


@pytest.mark.anyio
async def test_import_invalid_bundle(tmp_path):
    """Importing an invalid bundle raises appropriate errors."""
    # Non-existent file
    with pytest.raises(FileNotFoundError, match="not found"):
        await _import_entity("/nonexistent/path.omega.zip", overwrite=True)

    # Create invalid zip (not a bundle)
    bad_zip = tmp_path / "bad.omega.zip"
    with zipfile.ZipFile(bad_zip, "w") as zf:
        zf.writestr("some_file.txt", b"not a bundle")

    with pytest.raises(ValueError, match="missing manifest.json"):
        await _import_entity(str(bad_zip), overwrite=True)


# ═══════════════════════════════════════════════════════════════════════
# Tests — Utility functions
# ═══════════════════════════════════════════════════════════════════════


def test_extract_session_metadata():
    """_extract_session_metadata parses session data correctly."""
    session_data = {
        "sessions.yaml": yaml.dump([
            {"session_id": "ses_001", "created_at": "2026-07-01T10:00:00Z", "summary": "First"},
            {"session_id": "ses_002", "created_at": "2026-07-02T10:00:00Z", "summary": "Second"},
        ]).encode("utf-8"),
    }
    meta = _extract_session_metadata(session_data)
    assert meta["total_sessions"] == 2
    assert len(meta["sessions"]) == 2
    assert meta["sessions"][0]["session_id"] == "ses_001"


def test_extract_session_metadata_empty():
    """_extract_session_metadata handles empty input."""
    assert _extract_session_metadata({}) == {"total_sessions": 0, "sessions": []}
    assert _extract_session_metadata({"sessions.yaml": b""}) == {"total_sessions": 0, "sessions": []}
    assert _extract_session_metadata({"sessions.yaml": b"invalid: [yaml:"}) == {"total_sessions": 0, "sessions": []}


def test_extract_recent_exchanges():
    """_extract_recent_exchanges returns recent session summaries."""
    session_data = {
        "sessions.yaml": yaml.dump([
            {"session_id": "ses_001", "summary": "First session", "created_at": "2026-07-01T10:00:00Z"},
            {"session_id": "ses_002", "summary": "Second session", "created_at": "2026-07-02T10:00:00Z"},
        ]).encode("utf-8"),
    }
    exchanges = _extract_recent_exchanges(session_data)
    assert len(exchanges) == 2
    assert exchanges[0]["summary"] == "First session"


def test_validate_checksums_valid():
    """_validate_checksums returns empty list for valid bundle."""
    file_a_hash = hashlib.sha256(b"hello").hexdigest()
    file_b_hash = hashlib.sha256(b"world").hexdigest()
    contents = {
        "file_a.txt": b"hello",
        "file_b.txt": b"world",
        "checksums.sha256": (
            f"{file_a_hash}  file_a.txt\n"
            f"{file_b_hash}  file_b.txt\n"
        ).encode("utf-8"),
    }
    errors = _validate_checksums(contents)
    assert errors == []


def test_validate_checksums_mismatch():
    """_validate_checksums catches mismatch."""
    wrong_hash = hashlib.sha256(b"wrong").hexdigest()
    contents = {
        "file_a.txt": b"hello",
        "checksums.sha256": (
            f"{wrong_hash}  file_a.txt\n"
        ).encode("utf-8"),
    }
    errors = _validate_checksums(contents)
    assert len(errors) == 1
    assert "Checksum mismatch" in errors[0]


@pytest.mark.anyio
async def test_export_nonexistent_entity(tmp_path, monkeypatch):
    """Exporting a non-existent entity fails with appropriate error."""
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="not found"):
        await _export_entity("nonexistent_entity", str(tmp_path))


@pytest.mark.anyio
async def test_bundle_creates_in_default_dir(test_entity_dir):
    """Export without output path creates bundle in data/bundles/."""
    bundle_path = await _export_entity("test_bundle_entity")
    assert bundle_path.endswith(".omega.zip")
    assert Path(bundle_path).exists()

    # Should be in bundles/ directory
    bundles_dir = _get_bundles_dir()
    assert str(bundles_dir) in str(bundle_path)
