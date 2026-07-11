# 🔱 AxiomRegistry Contract Tests — M21 Gate Integrity
# ⬡ OMEGA ⬡ MAAT ⬡ P1-P5 ⬡ opencode ⬡ trc_axiom_registry_test ⬡ ACTIVE
# AP Token: AP-AXIOM-REGISTRY-TEST-v1.0.0
"""
Contract tests for AxiomRegistry per M21 Gate Integrity.

Every public API returns a typed result validated via isinstance(result, T).
Tests are deterministic and network-free.
"""

from pathlib import Path

import pytest

from omega.errors import WADError
from omega.oracle.axiom_registry import AxiomRegistry

WAD_DIR = Path("config/wads/arcana_novai")
MISSING_DIR = Path("config/wads/__nonexistent_axiom_wad__")

EXPECTED_IDS = [
    "ff1_truth",
    "ff2_sovereignty",
    "ff3_gnosis",
    "ff4_continuity",
    "ff5_liberation",
]

EXPECTED_NAMES = ["Truth", "Sovereignty", "Gnosis", "Continuity", "Liberation"]


class TestAxiomRegistryContracts:
    """M21 Contract Tests — type validation for all public APIs."""

    def test_load_returns_dict_with_five_axioms(self) -> None:
        """load() returns a dict containing exactly 5 five_fold axioms."""
        registry = AxiomRegistry(WAD_DIR)
        result = registry.load()

        # Contract: returns dict
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        # Contract: five_fold present and length 5
        assert "five_fold" in result, "axioms.yaml must contain 'five_fold'"
        assert isinstance(result["five_fold"], list), "five_fold must be a list"
        assert len(result["five_fold"]) == 5, f"Expected 5 axioms, got {len(result['five_fold'])}"

    def test_list_axioms_returns_expected_ids(self) -> None:
        """list_axioms() returns the expected id list."""
        registry = AxiomRegistry(WAD_DIR)
        ids = registry.list_axioms()

        # Contract: returns list
        assert isinstance(ids, list), f"Expected list, got {type(ids)}"
        # Contract: all items are str
        assert all(isinstance(i, str) for i in ids), "All ids must be str"
        # Contract: exact expected ids
        assert ids == EXPECTED_IDS, f"Expected {EXPECTED_IDS}, got {ids}"

    def test_get_preamble_nonempty_contains_names(self) -> None:
        """get_preamble() returns a non-empty str containing all axiom names."""
        registry = AxiomRegistry(WAD_DIR)
        preamble = registry.get_preamble()

        # Contract: returns str
        assert isinstance(preamble, str), f"Expected str, got {type(preamble)}"
        # Contract: non-empty
        assert len(preamble) > 0, "Preamble must be non-empty"
        # Contract: contains every axiom name
        for name in EXPECTED_NAMES:
            assert name in preamble, f"Preamble must contain axiom name '{name}'"

    def test_get_preamble_entity_tailored(self) -> None:
        """get_preamble(entity_name=...) includes the entity name in the header."""
        registry = AxiomRegistry(WAD_DIR)
        preamble = registry.get_preamble(entity_name="Sophia")

        # Contract: returns str
        assert isinstance(preamble, str)
        # Contract: tailored header contains entity name
        assert "Sophia" in preamble, "Tailored preamble must mention the entity"

    def test_missing_axioms_file_returns_empty_no_crash(self) -> None:
        """Missing axioms.yaml yields empty dict, empty list, placeholder preamble."""
        registry = AxiomRegistry(MISSING_DIR)
        result = registry.load()

        # Contract: returns dict (not exception)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert result == {}, "Missing file must yield empty dict"
        # Contract: list_axioms empty
        assert registry.list_axioms() == []
        # Contract: preamble is a non-empty placeholder str
        preamble = registry.get_preamble()
        assert isinstance(preamble, str)
        assert len(preamble) > 0
        assert "No axioms" in preamble

    def test_malformed_yaml_raises_wad_error(self, tmp_path: Path) -> None:
        """Malformed axioms.yaml raises typed WADError (M9 — no silent swallow)."""
        bad_file = tmp_path / "axioms.yaml"
        bad_file.write_text("five_fold: [unclosed\n")

        registry = AxiomRegistry(tmp_path)
        # Contract: typed error, not bare Exception
        with pytest.raises(WADError) as exc_info:
            registry.load()
        assert isinstance(exc_info.value, WADError)
        assert isinstance(exc_info.value, Exception)
