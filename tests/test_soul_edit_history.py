# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-TEST-SOUL-EDIT-HISTORY-v1.0.0
# 🔱 Tests for SoulEditHistory — Immutable Audit Trail
# ⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ TEST-SOUL-EDIT-HISTORY
#
# Tests the append-only audit trail for soul.yaml mutations.
#
# M21: Gate Integrity — contract tests verify return types with isinstance
# M9: Error Integrity — tests for error paths

import os
import time
from pathlib import Path
from typing import Any, Dict, List

import anyio
import pytest

from omega.oracle.soul_edit_history import SoulEditHistory, SoulEditEntry


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def temp_entities_dir(tmp_path: Path) -> Path:
    """Create a temporary entities directory for test isolation."""
    entities_dir = tmp_path / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)
    return entities_dir


@pytest.fixture
def history(temp_entities_dir: Path) -> SoulEditHistory:
    """Create a SoulEditHistory instance backed by the temp directory."""
    return SoulEditHistory(entities_dir=temp_entities_dir)


@pytest.fixture
def sample_entry() -> SoulEditEntry:
    """A sample edit entry for testing."""
    return SoulEditEntry(
        entity_name="test_entity",
        field_path="entity.lessons_learned[0]",
        old_value=None,
        new_value="L3: The Principle of Testing",
        source="soul_distiller",
        trace_id="trace-001",
        agent_name="jem",
        summary="Added first L3 principle",
    )


# ── SoulEditEntry Tests ──────────────────────────────────────────────

class TestSoulEditEntry:
    """Contract tests for SoulEditEntry dataclass."""

    def test_entry_is_dataclass(self, sample_entry: SoulEditEntry) -> None:
        """M21: Contract test — SoulEditEntry is a dataclass with correct types."""
        assert isinstance(sample_entry, SoulEditEntry)
        assert isinstance(sample_entry.entity_name, str)
        assert isinstance(sample_entry.field_path, str)
        assert isinstance(sample_entry.source, str)
        assert isinstance(sample_entry.trace_id, str)

    def test_auto_timestamp(self) -> None:
        """Entry without explicit timestamp gets one auto-assigned."""
        entry = SoulEditEntry(entity_name="test", field_path="entity.name")
        assert entry.timestamp > 0
        assert abs(time.time() - entry.timestamp) < 2.0

    def test_provided_timestamp(self) -> None:
        """Entry with explicit timestamp preserves it."""
        ts = 1234567890.0
        entry = SoulEditEntry(
            entity_name="test", field_path="entity.name",
            timestamp=ts,
        )
        assert entry.timestamp == ts


# ── SoulEditHistory Tests ────────────────────────────────────────────

class TestSoulEditHistory:
    """Contract tests for SoulEditHistory append-only log."""

    @pytest.mark.anyio
    async def test_append_new_entity(self, history: SoulEditHistory, sample_entry: SoulEditEntry) -> None:
        """Appending to a new entity creates the history file."""
        result = await history.append(sample_entry)
        assert result is None  # append returns None on success

        entries = await history.get_history("test_entity")
        assert len(entries) == 1
        assert entries[0]["entity_name"] == "test_entity"
        assert entries[0]["field_path"] == "entity.lessons_learned[0]"

    @pytest.mark.anyio
    async def test_append_multiple_entries(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """Multiple appends are all preserved in the log."""
        for i in range(5):
            entry = SoulEditEntry(
                entity_name="test_entity",
                field_path=f"entity.field_{i}",
                new_value=f"value_{i}",
                source=sample_entry.source,
                trace_id=f"trace-{i:03d}",
            )
            await history.append(entry)

        entries = await history.get_history("test_entity", limit=10)
        assert len(entries) == 5

        # Most recent first
        assert entries[0]["field_path"] == "entity.field_4"
        assert entries[-1]["field_path"] == "entity.field_0"

    @pytest.mark.anyio
    async def test_append_is_immutable(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """Once appended, entries cannot be modified (append-only)."""
        await history.append(sample_entry)

        # Attempt to overwrite — append always adds, never replaces
        overwrite = SoulEditEntry(
            entity_name="test_entity",
            field_path="entity.lessons_learned[0]",
            old_value="L3: The Principle of Testing",
            new_value="OVERWRITTEN",
            source="malicious",
            trace_id="trace-999",
        )
        await history.append(overwrite)

        entries = await history.get_history("test_entity")
        assert len(entries) == 2
        # Both entries are preserved (first has None old_value, second has the original)
        assert entries[1]["new_value"] == "L3: The Principle of Testing"
        assert entries[0]["new_value"] == "OVERWRITTEN"

    @pytest.mark.anyio
    async def test_get_history_empty(self, history: SoulEditHistory) -> None:
        """Getting history for an entity with no edits returns empty list."""
        entries = await history.get_history("nonexistent")
        assert isinstance(entries, list)
        assert len(entries) == 0

    @pytest.mark.anyio
    async def test_get_history_limit(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """The limit parameter correctly restricts returned entries."""
        for i in range(20):
            entry = SoulEditEntry(
                entity_name="test_entity",
                field_path=f"entity.field_{i}",
                new_value=f"value_{i}",
                source=sample_entry.source,
                trace_id=f"trace-{i:03d}",
            )
            await history.append(entry)

        entries = await history.get_history("test_entity", limit=5)
        assert len(entries) == 5

    @pytest.mark.anyio
    async def test_get_history_source_filter(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """The source parameter correctly filters entries."""
        await history.append(sample_entry)

        other = SoulEditEntry(
            entity_name="test_entity",
            field_path="entity.name",
            new_value="new_name",
            source="manual",
            trace_id="trace-002",
        )
        await history.append(other)

        distiller_entries = await history.get_history("test_entity", source="soul_distiller")
        assert len(distiller_entries) == 1
        assert distiller_entries[0]["source"] == "soul_distiller"

        manual_entries = await history.get_history("test_entity", source="manual")
        assert len(manual_entries) == 1
        assert manual_entries[0]["source"] == "manual"

    @pytest.mark.anyio
    async def test_get_history_after_timestamp(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """The after_timestamp parameter correctly filters entries."""
        ts_before = time.time()
        await history.append(sample_entry)

        await anyio.sleep(0.01)
        ts_mid = time.time()
        await anyio.sleep(0.01)

        later = SoulEditEntry(
            entity_name="test_entity",
            field_path="entity.name",
            new_value="after_mid",
            source="manual",
            trace_id="trace-003",
        )
        await history.append(later)

        # Only entries after ts_mid
        entries = await history.get_history("test_entity", after_timestamp=ts_mid)
        assert len(entries) == 1
        assert entries[0]["new_value"] == "after_mid"

        # All entries
        all_entries = await history.get_history("test_entity")
        assert len(all_entries) == 2

    @pytest.mark.anyio
    async def test_count_entries(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """Count returns correct entry totals."""
        assert await history.count_entries("test_entity") == 0

        for i in range(3):
            entry = SoulEditEntry(
                entity_name="test_entity",
                field_path=f"entity.field_{i}",
                new_value=f"value_{i}",
                source=sample_entry.source,
                trace_id=f"trace-{i:03d}",
            )
            await history.append(entry)

        assert await history.count_entries("test_entity") == 3

    @pytest.mark.anyio
    async def test_get_unique_sources(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """Unique sources are correctly enumerated."""
        assert await history.get_unique_sources("test_entity") == []

        await history.append(sample_entry)

        other = SoulEditEntry(
            entity_name="test_entity",
            field_path="entity.name",
            new_value="new_name",
            source="manual",
            trace_id="trace-004",
        )
        await history.append(other)

        # Same source again
        await history.append(sample_entry)

        sources = await history.get_unique_sources("test_entity")
        assert sorted(sources) == ["manual", "soul_distiller"]

    @pytest.mark.anyio
    async def test_corrupt_history_file(self, history: SoulEditHistory, temp_entities_dir: Path) -> None:
        """A corrupt history file is handled gracefully."""
        # Write invalid YAML to the history file
        history_path = temp_entities_dir / "corrupt_entity" / "soul_edit_history.yaml"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        await anyio.to_thread.run_sync(history_path.write_text, "not: valid: yaml: [[[")

        entries = await history.get_history("corrupt_entity")
        assert isinstance(entries, list)
        assert len(entries) == 0

    @pytest.mark.anyio
    async def test_not_a_list_history_file(self, history: SoulEditHistory, temp_entities_dir: Path) -> None:
        """A history file that is valid YAML but not a list is handled gracefully."""
        history_path = temp_entities_dir / "dict_entity" / "soul_edit_history.yaml"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        await anyio.to_thread.run_sync(history_path.write_text, "key: value\nnested:\n  - item\n")

        entries = await history.get_history("dict_entity")
        assert isinstance(entries, list)
        assert len(entries) == 0

    @pytest.mark.anyio
    async def test_get_history_returns_list(self, history: SoulEditHistory) -> None:
        """M21: Contract test — get_history always returns a list."""
        entries = await history.get_history("nonexistent")
        assert isinstance(entries, list)

        sample = SoulEditEntry(
            entity_name="contract_test",
            field_path="entity.name",
            new_value="test",
            source="manual",
            trace_id="trace-005",
        )
        await history.append(sample)

        entries = await history.get_history("contract_test")
        assert isinstance(entries, list)
        assert len(entries) > 0

    @pytest.mark.anyio
    async def test_get_history_most_recent_first(
        self, history: SoulEditHistory, sample_entry: SoulEditEntry
    ) -> None:
        """Entries are returned most-recent-first."""
        import time as time_module
        base_ts = time_module.time()

        for i in range(5):
            entry = SoulEditEntry(
                entity_name="test_entity",
                field_path=f"entity.field_{i}",
                new_value=f"value_{i}",
                source="manual",
                trace_id=f"trace-{i:03d}",
                timestamp=base_ts + i,
            )
            await history.append(entry)

        entries = await history.get_history("test_entity", limit=10)
        timestamps = [e["timestamp"] for e in entries]
        # Each successive timestamp should be >= the previous (most recent first = descending)
        assert all(timestamps[i] >= timestamps[i + 1] for i in range(len(timestamps) - 1))

    @pytest.mark.anyio
    async def test_concurrent_appends(self, history: SoulEditHistory) -> None:
        """Concurrent appends to the same entity do not corrupt the log."""
        async def append_n(n: int) -> None:
            for i in range(5):
                entry = SoulEditEntry(
                    entity_name="concurrent_entity",
                    field_path=f"entity.field_{n}_{i}",
                    new_value=f"value_{n}_{i}",
                    source=f"worker_{n}",
                    trace_id=f"trace-{n:03d}-{i:03d}",
                )
                await history.append(entry)

        # Launch 3 concurrent workers
        async with anyio.create_task_group() as tg:
            tg.start_soon(append_n, 1)
            tg.start_soon(append_n, 2)
            tg.start_soon(append_n, 3)

        entries = await history.get_history("concurrent_entity", limit=100)
        assert len(entries) == 15  # 3 workers × 5 entries each
