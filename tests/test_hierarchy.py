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
def hierarchy():
    return SovereignHierarchy()


@pytest.fixture
def hierarchy_with_config():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(SAMPLE_HIERARCHY)
        path = f.name
    yield SovereignHierarchy(hierarchy_config=Path(path))
    Path(path).unlink(missing_ok=True)


def test_default_ranks(hierarchy):
    """RANK_MAP entries should resolve correctly."""
    assert hierarchy.get_rank("sophia") == 0
    assert hierarchy.get_rank("maat") == 1
    assert hierarchy.get_rank("isis") == 2
    assert hierarchy.get_rank("lilith") == 2


def test_unknown_entity_is_keeper(hierarchy):
    """Entities not in RANK_MAP default to rank 3 (Pillar Keeper)."""
    assert hierarchy.get_rank("sekHmet") == 3
    assert hierarchy.get_rank("INANNA") == 3
    assert hierarchy.get_rank("lucifer") == 3
    assert hierarchy.get_rank("hecate") == 3
    assert hierarchy.get_rank("belial") == 3
    assert hierarchy.get_rank("nonexistent") == 3


def test_case_insensitive(hierarchy):
    """Rank lookup is case-insensitive."""
    assert hierarchy.get_rank("Sophia") == 0
    assert hierarchy.get_rank("MAAT") == 1
    assert hierarchy.get_rank("Isis") == 2


def test_recursion_sophia_allowed_at_depth_2(hierarchy):
    """Sophia (Rank 0) max_allowed_depth=3, so depth 2 is allowed."""
    result = hierarchy.check_recursion("sophia", 2)
    assert result["allowed"] is True
    assert result["rank"] == 0
    assert result["max_allowed_depth"] == 3


def test_recursion_sophia_blocked_at_depth_3(hierarchy):
    """Sophia (Rank 0) max_allowed_depth=3, so depth 3 is blocked."""
    result = hierarchy.check_recursion("sophia", 3)
    assert result["allowed"] is False
    assert "recursion limit" in result["reason"]


def test_recursion_maat_allowed_at_depth_1(hierarchy):
    """Ma'at (Rank 1) max_allowed_depth=2, so depth 1 is allowed."""
    result = hierarchy.check_recursion("maat", 1)
    assert result["allowed"] is True
    assert result["max_allowed_depth"] == 2


def test_recursion_maat_blocked_at_depth_2(hierarchy):
    """Ma'at (Rank 1) max_allowed_depth=2, so depth 2 is blocked."""
    result = hierarchy.check_recursion("maat", 2)
    assert result["allowed"] is False


def test_recursion_oversoul_allowed_at_depth_0(hierarchy):
    """Oversoul (Rank 2) max_allowed_depth=1, so depth 0 is allowed."""
    result = hierarchy.check_recursion("isis", 0)
    assert result["allowed"] is True
    assert result["max_allowed_depth"] == 1


def test_recursion_oversoul_blocked_at_depth_1(hierarchy):
    """Oversoul (Rank 2) max_allowed_depth=1, so depth 1 is blocked."""
    result = hierarchy.check_recursion("lilith", 1)
    assert result["allowed"] is False


def test_recursion_keeper_blocked_at_depth_0(hierarchy):
    """Keeper (Rank 3) max_allowed_depth=0, so depth 0 is blocked."""
    result = hierarchy.check_recursion("Sekhmet", 0)
    assert result["allowed"] is False
    assert result["max_allowed_depth"] == 0


def test_recursion_keeper_at_negative_depth(hierarchy):
    """Negative depth should be allowed for any rank."""
    result = hierarchy.check_recursion("Sekhmet", -1)
    assert result["allowed"] is True


def test_load_from_config(hierarchy_with_config):
    """Hierarchy can be loaded from a custom YAML config."""
    assert hierarchy_with_config._hierarchy is not None
    assert "sophia" in hierarchy_with_config._hierarchy
    assert hierarchy_with_config._hierarchy["sophia"]["rank"] == 0


def test_missing_config_file():
    """Missing config file should not raise, just return empty."""
    h = SovereignHierarchy(hierarchy_config=Path("/tmp/nonexistent_hierarchy.yaml"))
    assert h._hierarchy == {}
    # RANK_MAP still works
    assert h.get_rank("sophia") == 0