# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Phase 3 tests: soul_render, wad_switch, WADEntitySchema, scaffold + lint."""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@pytest.fixture
def wad_env():
    temp_dir = tempfile.mkdtemp()
    wads_dir = Path(temp_dir) / "wads"
    wads_dir.mkdir()
    old_data_dir = os.environ.pop("OMEGA_DATA_DIR", None)
    test_data_dir = Path(temp_dir) / "data"
    test_data_dir.mkdir()
    os.environ["OMEGA_DATA_DIR"] = str(test_data_dir)
    yield wads_dir, temp_dir
    if old_data_dir is not None:
        os.environ["OMEGA_DATA_DIR"] = old_data_dir
    else:
        os.environ.pop("OMEGA_DATA_DIR", None)
    shutil.rmtree(temp_dir, ignore_errors=True)


def make_registry_and_loader(wads_dir):
    fd, config_path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    Path(config_path).write_text("entities: {}\n")
    from omega.oracle.entity_registry import EntityRegistry
    from omega.oracle.wad_loader import WADLoader
    registry = EntityRegistry(config_path=config_path)
    loader = WADLoader(registry, wads_dir=wads_dir)
    return registry, loader, config_path


# ── soul_render tests ──────────────────────────────────────────────────

def test_soul_render_discover():
    """soul_render --all discovers all entities in arcana_novai WAD."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "--all"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "avgn" in result.stdout
    assert "kali" in result.stdout


def test_soul_render_identity_schema():
    """soul_render produces valid output for ANAi identity: schema."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "avgn"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "avgn System Prompt" in result.stdout
    assert "Axioms" in result.stdout
    assert "Directives" in result.stdout


def test_soul_render_entity_schema():
    """soul_render produces valid output for Researcher entity: schema."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "researcher_humboldt"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "Alexander von Humboldt System Prompt" in result.stdout
    assert "Domain Affinities" in result.stdout


def test_soul_render_flat_entity():
    """soul_render handles flat OED entity YAML (no soul.yaml)."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "kali", "--wad", "_omega_default"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "Kali System Prompt" in result.stdout


# ── WADEntitySchema tests ──────────────────────────────────────────────

def test_wade_entity_schema_valid():
    """WADEntitySchema validates a well-formed entity dict."""
    from omega.oracle.wad_loader import validate_wad_entity, WADEntitySchema
    validated, meta = validate_wad_entity(
        {"name": "test", "domains": ["a"], "temperature": 0.5, "context_window": 4096},
        default_name="test",
    )
    assert validated.name == "test"
    assert validated.temperature == 0.5
    assert validated.context_window == 4096


def test_wade_entity_schema_rejects_bad_temperature():
    """WADEntitySchema rejects out-of-range temperature."""
    from omega.oracle.wad_loader import validate_wad_entity
    with pytest.raises(ValueError):
        validate_wad_entity({"name": "bad", "temperature": 5.0}, default_name="bad")


def test_wade_entity_schema_rejects_string_temperature():
    """WADEntitySchema rejects string temperature (strict typing)."""
    from omega.oracle.wad_loader import validate_wad_entity
    with pytest.raises(ValueError):
        validate_wad_entity({"name": "bad", "temperature": "hot"}, default_name="bad")


def test_wade_entity_schema_captures_metadata():
    """Unknown fields become metadata, not errors."""
    from omega.oracle.wad_loader import validate_wad_entity
    validated, meta = validate_wad_entity(
        {"name": "rich", "archetype": "Synthesist", "element": "Air"},
        default_name="rich",
    )
    assert "archetype" in meta
    assert "element" in meta
    assert validated.name == "rich"


# ── wad_switch tests ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_wad_switch_basic(wad_env):
    """wad_switch loads target and unloads conflicting PWADs."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create two WADs
        for name in ("wad_a", "wad_b"):
            stack = wads_dir / name
            stack.mkdir()
            (stack / "manifest.yaml").write_text(
                f"name: {name}\nversion: 1.0.0\ntype: pwad\npriority: 1\nentities: []\n"
            )
            ed = stack / "entities"
            ed.mkdir()
            (ed / f"{name}_ent.yaml").write_text(
                f"entity:\n  name: {name}_ent\n  domains: [test]\n  personality: {name}"
            )

        # Load first
        r1 = await loader.load_wad("wad_a")
        assert r1[0] is True
        assert "wad_a_ent" in [e.name.lower() for e in registry.list()]

        # Switch to second
        result = await loader.wad_switch("wad_b")
        assert result["success"] is True
        assert "wad_b" in result["loaded_wads"]
        assert "wad_a" not in result["loaded_wads"]
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_wad_switch_invalid_target(wad_env):
    """wad_switch returns error for non-existent WAD."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        result = await loader.wad_switch("nonexistent_wad")
        assert result["success"] is False
        assert "missing manifest" in result["error"].lower() or "not found" in result["error"].lower()
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_wad_switch_path_traversal(wad_env):
    """wad_switch rejects path traversal attempts."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        result = await loader.wad_switch("../secrets")
        assert result["success"] is False
        assert "traversal" in result["error"].lower()
    finally:
        Path(cfg).unlink(missing_ok=True)


# ── scaffold + lint tests ───────────────────────────────────────────────

def test_create_wad_scaffold():
    """create_wad.py produces a valid, lint-clean WAD."""
    tmpdir = tempfile.mkdtemp()
    try:
        result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "create_wad.py"), "scaffold_test", "--type", "pwad", "--wads-dir", tmpdir],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert result.returncode == 0
        wad_path = Path(tmpdir) / "scaffold_test"
        assert wad_path.is_dir()
        assert (wad_path / "manifest.yaml").exists()
        assert (wad_path / "entities" / "example" / "soul.yaml").exists()

        # Validate
        v_result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "validate_wad.py"), str(wad_path)],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert v_result.returncode == 0, v_result.stdout + v_result.stderr

        # Lint
        l_result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "lint_wad.py"), str(wad_path)],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert l_result.returncode == 0, l_result.stdout + l_result.stderr
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_lint_wad_duplicate_keys():
    """lint_wad.py detects duplicate YAML keys."""
    tmpdir = tempfile.mkdtemp()
    try:
        wad_path = Path(tmpdir) / "dup_wad"
        wad_path.mkdir()
        (wad_path / "manifest.yaml").write_text("name: dup\nversion: 1.0.0\nentities: []\nname: dup2\n")
        result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "lint_wad.py"), str(wad_path)],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert result.returncode == 1
        assert "duplicate key" in result.stdout.lower()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_lint_wad_axiom_ceiling():
    """lint_wad.py detects axiom ceiling violations."""
    tmpdir = tempfile.mkdtemp()
    try:
        wad_path = Path(tmpdir) / "axiom_wad"
        wad_path.mkdir()
        (wad_path / "manifest.yaml").write_text("name: axiom\nversion: 1.0.0\nentities: []\n")
        ed = wad_path / "entities" / "bigaxioms"
        ed.mkdir(parents=True)
        axioms = "\n".join(f'  - id: "A-{i}"\n    text: "axiom {i}"' for i in range(25))
        (ed / "soul.yaml").write_text(f"identity:\n  keeper: bigaxioms\naxioms:\n{axioms}\n")
        result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "lint_wad.py"), str(wad_path)],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert result.returncode == 1
        assert "axiom count" in result.stdout.lower()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
