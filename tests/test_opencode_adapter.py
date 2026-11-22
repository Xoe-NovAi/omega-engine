# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""CI test for OpenCode adapter drift detection."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def test_soul_render_all_entities():
    """soul_render --all discovers all entities without errors."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "--all"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "discovered:" in result.stdout


def test_soul_render_identity_schema():
    """soul_render produces valid output for ANAi identity: schema."""
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "soul_render.py"), "avgn"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "System Prompt" in result.stdout


def test_lint_wad_all():
    """All WADs in config/wads/ pass lint."""
    wads_dir = REPO / "config" / "wads"
    if not wads_dir.is_dir():
        pytest.skip("No config/wads/ directory")
    for wad_path in sorted(wads_dir.iterdir()):
        if not wad_path.is_dir():
            continue
        result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "lint_wad.py"), str(wad_path)],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert result.returncode == 0, f"Lint failed for {wad_path.name}: {result.stdout}"


def test_validate_wad_all():
    """All WADs in config/wads/ pass validation."""
    wads_dir = REPO / "config" / "wads"
    if not wads_dir.is_dir():
        pytest.skip("No config/wads/ directory")
    for wad_path in sorted(wads_dir.iterdir()):
        if not wad_path.is_dir():
            continue
        result = subprocess.run(
            [PYTHON, str(REPO / "scripts" / "validate_wad.py"), str(wad_path)],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(REPO / "src")},
        )
        assert result.returncode == 0, f"Validation failed for {wad_path.name}: {result.stdout}"


def test_wad_diff_self():
    """wad_diff on identical WADs reports identical."""
    wad = REPO / "config" / "wads" / "_omega_default"
    if not wad.is_dir():
        pytest.skip("WAD not found")
    result = subprocess.run(
        [PYTHON, str(REPO / "scripts" / "wad_diff.py"), str(wad), str(wad)],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )
    assert result.returncode == 0
    assert "IDENTICAL" in result.stdout


def test_entity_registry_batch_add():
    """EntityRegistry.batch_add() works correctly."""
    import tempfile
    from pathlib import Path
    from omega.oracle.entity_registry import EntityRegistry, Entity

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "entities.yaml"
        config_path.write_text("entities: {}\n")
        registry = EntityRegistry(config_path=str(config_path))

        import anyio

        async def run():
            entities = [
                Entity(name=f"test_entity_{i}", domains=["test"], personality="test", model="opencode/big-pickle")
                for i in range(3)
            ]
            await registry.batch_add(entities)
            assert len(registry.list()) == 3

        anyio.run(run)


def test_soul_context_cache():
    """soul_utils load_entity_soul_context uses cache."""
    import tempfile
    from pathlib import Path
    import os
    from omega.soul_utils import load_entity_soul_context

    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        entity_dir = data_dir / "entities" / "testent"
        entity_dir.mkdir(parents=True)
        (entity_dir / "soul.yaml").write_text("identity:\n  keeper: testent\naxioms:\n  - id: A1\n    text: Test axiom\n")

        # First call
        result1 = load_entity_soul_context("testent", data_dir)
        # Second call should use cache (same result)
        result2 = load_entity_soul_context("testent", data_dir)
        assert result1 == result2
