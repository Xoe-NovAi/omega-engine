# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SECURITY-TAINT-TEST-v1.0.0
# 🔱 Tests for Tainted Data Protocol — Transitive Propagation
# ⬡ OMEGA ⬡ SECURITY ⬡ tests/security/test_taint.py
"""Tests for the transitive taint propagation engine.

[M7 Local-First] All tests use local-only computation — no cloud API calls.
[M1 AnyIO] Async tests use anyio.
"""
import pytest

from omega.security.taint import (
    TaintLevel,
    TaintSource,
    TaintRecord,
    TaintPropagation,
    TaintAwareIngestion,
    TaintAwareMemory,
    create_taint_propagation,
    get_taint_propagation,
)


class TestTaintLevel:
    def test_ordering(self):
        assert TaintLevel.CLEAN < TaintLevel.LOW
        assert TaintLevel.LOW < TaintLevel.MEDIUM
        assert TaintLevel.MEDIUM < TaintLevel.HIGH
        assert TaintLevel.HIGH < TaintLevel.CONTAMINATED

    def test_max_single(self):
        assert TaintLevel.max(TaintLevel.LOW) == TaintLevel.LOW

    def test_max_multiple(self):
        assert TaintLevel.max(TaintLevel.CLEAN, TaintLevel.HIGH, TaintLevel.MEDIUM) == TaintLevel.HIGH

    def test_max_empty(self):
        assert TaintLevel.max() == TaintLevel.CLEAN

    def test_max_none(self):
        assert TaintLevel.max(TaintLevel.CLEAN, TaintLevel.CLEAN) == TaintLevel.CLEAN


class TestTaintSource:
    def test_basic_source(self):
        source = TaintSource(name="web_search")
        assert source.name == "web_search"
        assert source.url is None
        assert source.provider is None

    def test_full_source(self):
        source = TaintSource(
            name="firecrawl",
            url="https://example.com",
            provider="firecrawl",
        )
        assert source.name == "firecrawl"
        assert source.url == "https://example.com"
        assert source.provider == "firecrawl"


class TestTaintRecord:
    def test_to_dict(self):
        source = TaintSource(name="test", url="https://test.com")
        record = TaintRecord(
            data_id="abc123",
            taint_level=TaintLevel.MEDIUM,
            source=source,
            derived_from=["parent1"],
            metadata={"key": "value"},
        )
        d = record.to_dict()
        assert d["data_id"] == "abc123"
        assert d["taint_level"] == "MEDIUM"
        assert d["source"]["name"] == "test"
        assert d["derived_from"] == ["parent1"]
        assert d["metadata"] == {"key": "value"}

    def test_from_dict(self):
        d = {
            "data_id": "abc123",
            "taint_level": "HIGH",
            "source": {
                "name": "test",
                "url": "https://test.com",
                "provider": "test_provider",
                "timestamp": "2026-01-01T00:00:00+00:00",
            },
            "derived_from": ["parent1", "parent2"],
            "metadata": {"key": "value"},
            "timestamp": "2026-01-01T00:00:00+00:00",
        }
        record = TaintRecord.from_dict(d)
        assert record.data_id == "abc123"
        assert record.taint_level == TaintLevel.HIGH
        assert record.source.name == "test"
        assert record.derived_from == ["parent1", "parent2"]


class TestTaintPropagation:
    def test_tag_data(self):
        tp = TaintPropagation()
        data_id = tp.tag_data(
            content="external content",
            source=TaintSource(name="web_search"),
            taint_level=TaintLevel.MEDIUM,
        )
        assert data_id is not None
        assert len(data_id) == 32  # SHA256[:32]

    def test_get_taint_level_known(self):
        tp = TaintPropagation()
        data_id = tp.tag_data(
            content="external content",
            source=TaintSource(name="web_search"),
            taint_level=TaintLevel.HIGH,
        )
        assert tp.get_taint_level(data_id) == TaintLevel.HIGH

    def test_get_taint_level_unknown(self):
        tp = TaintPropagation()
        # Unknown data_id should return CLEAN
        assert tp.get_taint_level("nonexistent") == TaintLevel.CLEAN

    def test_derive_data_inherits_max_taint(self):
        tp = TaintPropagation()
        id1 = tp.tag_data("content1", TaintSource(name="s1"), TaintLevel.LOW)
        id2 = tp.tag_data("content2", TaintSource(name="s2"), TaintLevel.HIGH)

        derived_id = tp.derive_data("derived content", [id1, id2])
        # Should inherit the max taint level (HIGH)
        assert tp.get_taint_level(derived_id) == TaintLevel.HIGH

    def test_derive_data_no_parents(self):
        tp = TaintPropagation()
        derived_id = tp.derive_data("derived content", [])
        assert tp.get_taint_level(derived_id) == TaintLevel.CLEAN

    def test_derive_data_unknown_parent(self):
        tp = TaintPropagation()
        derived_id = tp.derive_data("derived content", ["unknown_parent"])
        # Unknown parent → CLEAN
        assert tp.get_taint_level(derived_id) == TaintLevel.CLEAN

    def test_elevate_taint(self):
        tp = TaintPropagation()
        data_id = tp.tag_data("content", TaintSource(name="s"), TaintLevel.LOW)
        assert tp.get_taint_level(data_id) == TaintLevel.LOW

        # Elevate to HIGH
        assert tp.elevate_taint(data_id, TaintLevel.HIGH, "Found malicious content") is True
        assert tp.get_taint_level(data_id) == TaintLevel.HIGH

    def test_elevate_taint_not_higher(self):
        tp = TaintPropagation()
        data_id = tp.tag_data("content", TaintSource(name="s"), TaintLevel.HIGH)
        # Cannot lower taint
        assert tp.elevate_taint(data_id, TaintLevel.LOW, "test") is False
        assert tp.get_taint_level(data_id) == TaintLevel.HIGH

    def test_elevate_taint_unknown(self):
        tp = TaintPropagation()
        assert tp.elevate_taint("nonexistent", TaintLevel.HIGH, "test") is False

    def test_elevate_propagates_to_derived(self):
        tp = TaintPropagation()
        parent_id = tp.tag_data("parent", TaintSource(name="s"), TaintLevel.LOW)
        child_id = tp.derive_data("child", [parent_id])
        assert tp.get_taint_level(child_id) == TaintLevel.LOW

        # Elevate parent → child should also be elevated
        tp.elevate_taint(parent_id, TaintLevel.HIGH, "parent contaminated")
        assert tp.get_taint_level(child_id) == TaintLevel.HIGH

    def test_filter_by_taint(self):
        tp = TaintPropagation()
        id_clean = tp.tag_data("clean", TaintSource(name="s"), TaintLevel.CLEAN)
        id_low = tp.tag_data("low", TaintSource(name="s"), TaintLevel.LOW)
        id_high = tp.tag_data("high", TaintSource(name="s"), TaintLevel.HIGH)

        filtered = tp.filter_by_taint([id_clean, id_low, id_high], max_level=TaintLevel.LOW)
        assert id_clean in filtered
        assert id_low in filtered
        assert id_high not in filtered

    def test_get_contaminated_sources(self):
        tp = TaintPropagation()
        tp.tag_data("clean", TaintSource(name="s"), TaintLevel.CLEAN)
        tp.tag_data("high", TaintSource(name="s"), TaintLevel.HIGH)
        tp.tag_data("contaminated", TaintSource(name="s"), TaintLevel.CONTAMINATED)

        contaminated = tp.get_contaminated_sources()
        assert len(contaminated) == 2

    def test_get_stats(self):
        tp = TaintPropagation()
        tp.tag_data("c1", TaintSource(name="s"), TaintLevel.CLEAN)
        tp.tag_data("c2", TaintSource(name="s"), TaintLevel.LOW)
        tp.tag_data("c3", TaintSource(name="s"), TaintLevel.HIGH)

        stats = tp.get_stats()
        assert stats["total_records"] == 3
        assert stats["by_level"]["CLEAN"] == 1
        assert stats["by_level"]["LOW"] == 1
        assert stats["by_level"]["HIGH"] == 1
        assert stats["contaminated_sources"] == 1

    def test_clear(self):
        tp = TaintPropagation()
        tp.tag_data("content", TaintSource(name="s"), TaintLevel.HIGH)
        assert tp.get_stats()["total_records"] == 1
        tp.clear()
        assert tp.get_stats()["total_records"] == 0

    def test_stable_hash(self):
        """Same content should produce the same data_id."""
        tp = TaintPropagation()
        id1 = tp.tag_data("same content", TaintSource(name="s"), TaintLevel.LOW)
        id2 = tp.tag_data("same content", TaintSource(name="s"), TaintLevel.LOW)
        assert id1 == id2


class TestTaintAwareIngestion:
    def test_determine_taint_local(self):
        assert TaintAwareIngestion.determine_taint_level(
            "local", source_url="http://localhost:8016/config"
        ) == TaintLevel.CLEAN

    def test_determine_taint_github_trusted(self):
        assert TaintAwareIngestion.determine_taint_level(
            "firecrawl", source_url="https://github.com/Xoe-NovAi/omega-engine"
        ) == TaintLevel.LOW

    def test_determine_taint_search(self):
        assert TaintAwareIngestion.determine_taint_level(
            "searxng", source_url="https://searx.example.com"
        ) == TaintLevel.MEDIUM

    def test_determine_taint_external(self):
        assert TaintAwareIngestion.determine_taint_level(
            "firecrawl", source_url="https://example.com/page"
        ) == TaintLevel.HIGH

    def test_determine_taint_unknown_provider(self):
        assert TaintAwareIngestion.determine_taint_level(
            "unknown_provider", source_url=None
        ) == TaintLevel.HIGH

    def test_determine_taint_no_url(self):
        assert TaintAwareIngestion.determine_taint_level(
            "firecrawl", source_url=None
        ) == TaintLevel.MEDIUM  # firecrawl maps to MEDIUM

    def test_determine_taint_localhost_provider(self):
        assert TaintAwareIngestion.determine_taint_level(
            "localhost", source_url=None
        ) == TaintLevel.CLEAN


class TestTaintAwareMemory:
    @pytest.mark.anyio
    async def test_tag_block_content(self):
        tam = TaintAwareMemory()
        data_id = await tam.tag_block_content(
            content="some content",
            block_label="decisions",
            entity_name="test_entity",
            taint_level=TaintLevel.MEDIUM,
        )
        assert data_id is not None
        assert tam._tp.get_taint_level(data_id) == TaintLevel.MEDIUM

    @pytest.mark.anyio
    async def test_check_block_taint_default_clean(self):
        tam = TaintAwareMemory()
        # Untracked block → CLEAN
        level = tam.check_block_taint("nonexistent_block", "test_entity")
        assert level == TaintLevel.CLEAN

    @pytest.mark.anyio
    async def test_should_promote_to_core_clean(self):
        tam = TaintAwareMemory()
        data_id = tam._tp.tag_data(
            "content", TaintSource(name="s"), TaintLevel.CLEAN
        )
        assert tam.should_promote_to_core(data_id, max_level=TaintLevel.LOW) is True

    @pytest.mark.anyio
    async def test_should_promote_to_core_high(self):
        tam = TaintAwareMemory()
        data_id = tam._tp.tag_data(
            "content", TaintSource(name="s"), TaintLevel.HIGH
        )
        assert tam.should_promote_to_core(data_id, max_level=TaintLevel.LOW) is False


class TestSingleton:
    def test_create_taint_propagation_returns_instance(self):
        tp = create_taint_propagation()
        assert isinstance(tp, TaintPropagation)

    def test_get_taint_propagation_returns_instance(self):
        tp = get_taint_propagation()
        assert isinstance(tp, TaintPropagation)

    def test_singleton_returns_same_instance(self):
        tp1 = get_taint_propagation()
        tp2 = get_taint_propagation()
        assert tp1 is tp2
