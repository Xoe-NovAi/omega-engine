# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for Sovereign Hierarchy (pure logic, no network)."""

import tempfile
from pathlib import Path

import pytest
import yaml

from omega.oracle.hierarchy import SovereignHierarchy


SAMPLE_HIERARCHY = """
sophia:
  rank: 0
  domains:
    - gnosis
    - wisdom
  color: gold

maat:
  rank: 1
  domains:
    - audit
    - balance
  color: silver
"""


@pytest.fixture
async def hierarchy():
    h = SovereignHierarchy()
    await h.load()
    return h


@pytest.fixture
async def hierarchy_with_config():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(SAMPLE_HIERARCHY)
        path = f.name
    h = SovereignHierarchy(hierarchy_config=Path(path))
    await h.load()
    yield h
    Path(path).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_default_ranks(hierarchy):
    """Hierarchy entries should resolve correctly based on YAML.

    Current default hierarchy.yaml: kali (Founder)=rank 0,
    maat/lilith (Executive)=rank 1, all others default to rank 3.
    """
    assert hierarchy.get_rank("kali") == 0
    assert hierarchy.get_rank("maat") == 1
    assert hierarchy.get_rank("lilith") == 1
    # sophia was removed in the Phase-1 nomenclature sweep — defaults to rank 3
    assert hierarchy.get_rank("sophia") == 3
    # Isis is per-IWAD (Arcana-NovAi), not in core hierarchy — defaults to rank 3
    assert hierarchy.get_rank("isis") == 3


@pytest.mark.anyio
async def test_unknown_entity_is_keeper(hierarchy):
    """Entities not in RANK_MAP default to rank 3 (Pillar Keeper), unless they are special."""
    assert hierarchy.get_rank("sekHmet") == 3
    assert hierarchy.get_rank("INANNA") == 3
    assert hierarchy.get_rank("lucifer") == 3
    assert hierarchy.get_rank("hecate") == 3
    # roc_racoon is per-IWAD, not in core hierarchy — defaults to rank 3
    assert hierarchy.get_rank("roc_racoon") == 3
    assert hierarchy.get_rank("nonexistent") == 3


@pytest.mark.anyio
async def test_case_insensitive(hierarchy):
    """Rank lookup is case-insensitive."""
    assert hierarchy.get_rank("KALI") == 0
    assert hierarchy.get_rank("MAAT") == 1
    assert hierarchy.get_rank("Isis") == 3  # per-IWAD entity, defaults to rank 3


@pytest.mark.anyio
async def test_recursion_kali_allowed_at_depth_2(hierarchy):
    """Kali (Rank 0) max_allowed_depth=3, so depth 2 is allowed."""
    result = hierarchy.check_recursion("kali", 2)
    assert result["allowed"] is True
    assert result["rank"] == 0
    assert result["max_allowed_depth"] == 3


@pytest.mark.anyio
async def test_recursion_kali_blocked_at_depth_3(hierarchy):
    """Kali (Rank 0) max_allowed_depth=3, so depth 3 is blocked."""
    result = hierarchy.check_recursion("kali", 3)
    assert result["allowed"] is False
    assert "recursion limit" in result["reason"]


@pytest.mark.anyio
async def test_recursion_oversoul_allowed_at_depth_1(hierarchy):
    """Oversoul (Rank 1) max_allowed_depth=2, so depth 1 is allowed."""
    result = hierarchy.check_recursion("maat", 1)
    assert result["allowed"] is True
    assert result["max_allowed_depth"] == 2


@pytest.mark.anyio
async def test_recursion_oversoul_blocked_at_depth_2(hierarchy):
    """Oversoul (Rank 1) max_allowed_depth=2, so depth 2 is blocked."""
    result = hierarchy.check_recursion("lilith", 2)
    assert result["allowed"] is False


@pytest.mark.anyio
async def test_recursion_oversoul_allowed_at_depth_0(hierarchy):
    """Oversoul (Rank 1) max_allowed_depth=2, so depth 0 is allowed."""
    result = hierarchy.check_recursion("maat", 0)
    assert result["allowed"] is True
    assert result["max_allowed_depth"] == 2


@pytest.mark.anyio
async def test_recursion_oversoul_blocked_at_depth_1(hierarchy):
    """Oversoul (Rank 1) max_allowed_depth=2, so depth 1 is allowed (not blocked)."""
    result = hierarchy.check_recursion("lilith", 1)
    assert result["allowed"] is True


@pytest.mark.anyio
async def test_recursion_keeper_blocked_at_depth_0(hierarchy):
    """Keeper (Rank 3) max_allowed_depth=0, so depth 0 is blocked."""
    result = hierarchy.check_recursion("Sekhmet", 0)
    assert result["allowed"] is False
    assert result["max_allowed_depth"] == 0


@pytest.mark.anyio
async def test_recursion_keeper_at_negative_depth(hierarchy):
    """Negative depth should be allowed for any rank."""
    result = hierarchy.check_recursion("Sekhmet", -1)
    assert result["allowed"] is True


@pytest.mark.anyio
async def test_load_from_config(hierarchy_with_config):
    """Hierarchy can be loaded from a custom YAML config."""
    assert hierarchy_with_config._hierarchy is not None
    assert "sophia" in hierarchy_with_config._hierarchy
    assert hierarchy_with_config._hierarchy["sophia"]["rank"] == 0


def test_missing_config_file():
    """Missing config file should not raise, just return empty.
    Without config, all entities default to Rank 3.
    """
    h = SovereignHierarchy(hierarchy_config=Path("/tmp/nonexistent_hierarchy.yaml"))
    assert h._hierarchy == {}
    assert h.get_rank("sophia") == 3