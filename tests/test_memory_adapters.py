# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Memory Adapter Tests
# ⬡ OMEGA ⬡ MEMORY ⬡ TESTS ⬡ v1.0.0 ⬡ 2026-06-15

"""Tests for IMemoryAdapter ABC, MemoryAdapterRegistry, and MemoryRecord."""

import pytest
from omega.memory.adapters import (
    IMemoryAdapter,
    MemoryAdapterRegistry,
    MemoryRecord,
    MemoryType,
    MemoryPriority,
)


# ── Mock Adapter for Testing ──

class MockAdapter(IMemoryAdapter):
    """A minimal concrete IMemoryAdapter for testing."""

    def __init__(self):
        self.history: dict = {}
        self.vault: dict = {}
        self.closed = False

    async def get_history(self, entity_name: str, session_id: str, limit: int) -> list:
        key = f"{entity_name}/{session_id}"
        return self.history.get(key, [])[-limit:]

    async def save_history(self, entity_name: str, session_id: str, exchanges: list) -> None:
        key = f"{entity_name}/{session_id}"
        if key not in self.history:
            self.history[key] = []
        self.history[key].extend(exchanges)

    async def archive(self, entity_name: str, session_id: str) -> bool:
        key = f"{entity_name}/{session_id}"
        if key in self.history:
            del self.history[key]
            return True
        return False

    async def close(self) -> None:
        self.closed = True

    async def get_vault(self, entity_name: str, vault_key: str) -> dict | None:
        return self.vault.get(f"{entity_name}/{vault_key}")

    async def put_vault(self, entity_name: str, vault_key: str, data: dict) -> None:
        self.vault[f"{entity_name}/{vault_key}"] = data


# ── MemoryRecord Tests ──

class TestMemoryRecord:
    """Verify MemoryRecord dataclass construction and serialization."""

    def test_create_defaults(self):
        """Should create a MemoryRecord with sensible defaults."""
        record = MemoryRecord(
            memory_id="test-001",
            entity_name="kali",
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.NORMAL,
            content="Test memory content",
        )
        assert record.memory_id == "test-001"
        assert record.entity_name == "kali"
        assert record.memory_type == MemoryType.EPISODIC
        assert record.priority == MemoryPriority.NORMAL
        assert record.content == "Test memory content"
        assert record.metadata == {}
        assert record.timestamp is None
        assert record.source_trace_id is None

    def test_to_dict_roundtrip(self):
        """Should serialize and deserialize without data loss."""
        record = MemoryRecord(
            memory_id="test-002",
            entity_name="maat",
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.HIGH,
            content="Important insight",
            metadata={"source": "test", "confidence": 0.95},
            timestamp=1234567890.0,
            source_trace_id="trace-abc-123",
        )
        data = record.to_dict()
        restored = MemoryRecord.from_dict(data)
        assert restored.memory_id == record.memory_id
        assert restored.entity_name == record.entity_name
        assert restored.memory_type == record.memory_type
        assert restored.priority == record.priority
        assert restored.content == record.content
        assert restored.metadata == record.metadata
        assert restored.timestamp == record.timestamp
        assert restored.source_trace_id == record.source_trace_id

    def test_all_enum_values(self):
        """All MemoryType and MemoryPriority values should roundtrip cleanly."""
        for mt in MemoryType:
            record = MemoryRecord(
                memory_id=f"type-{mt.value}",
                entity_name="test",
                memory_type=mt,
                priority=MemoryPriority.NORMAL,
                content="Enum test",
            )
            restored = MemoryRecord.from_dict(record.to_dict())
            assert restored.memory_type == mt

        for mp in MemoryPriority:
            record = MemoryRecord(
                memory_id=f"prio-{mp.value}",
                entity_name="test",
                memory_type=MemoryType.EPISODIC,
                priority=mp,
                content="Enum test",
            )
            restored = MemoryRecord.from_dict(record.to_dict())
            assert restored.priority == mp


# ── IMemoryAdapter ABC Tests ──

class TestIMemoryAdapter:
    """Verify the ABC contract — abstract methods must raise TypeError."""

    def test_cannot_instantiate_abc(self):
        """Should not allow direct instantiation of IMemoryAdapter."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IMemoryAdapter()

    def test_can_instantiate_concrete(self):
        """Should allow instantiation of a class with all abstract methods."""
        adapter = MockAdapter()
        assert isinstance(adapter, IMemoryAdapter)

    def test_missing_method_raises(self):
        """Should fail if a concrete class doesn't implement all methods."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            type("BadAdapter", (IMemoryAdapter,), {})()

    async def test_lifecycle_hooks_default(self):
        """Lifecycle hooks should have default implementations that return empty."""
        adapter = MockAdapter()
        result = await adapter.on_session_end("test", "transcript")
        assert result == []
        precompact = await adapter.on_pre_compact("test", "session-1")
        assert precompact == {}

    async def test_sphere_operations_default(self):
        """Sphere/qliphoth operations should default to empty dict."""
        adapter = MockAdapter()
        sphere = await adapter.get_sphere("test")
        assert sphere == {}
        qliphoth = await adapter.get_qliphoth()
        assert qliphoth == {}


# ── MemoryAdapterRegistry Tests ──

class TestMemoryAdapterRegistry:
    """Verify registry registration, lookup, and error handling."""

    def setup_method(self):
        self.registry = MemoryAdapterRegistry()
        self.default_adapter = MockAdapter()
        self.arcana_adapter = MockAdapter()

    def test_register_and_get_wad(self):
        """Should register and retrieve an adapter by WAD name."""
        self.registry.register("_omega_default", self.default_adapter)
        retrieved = self.registry.get_for_wad("_omega_default")
        assert retrieved is self.default_adapter

    def test_register_invalid_type_raises(self):
        """Should reject registration of objects not implementing IMemoryAdapter."""
        with pytest.raises(TypeError, match="must implement IMemoryAdapter"):
            self.registry.register("bad", "not_an_adapter")

    def test_entity_mapping_lookup(self):
        """Should resolve adapter by entity name through WAD mapping."""
        self.registry.register("arcana_novai", self.arcana_adapter)
        self.registry.register_entity_to_wad("kali", "arcana_novai")
        self.registry.register_entity_to_wad("maat", "arcana_novai")

        assert self.registry.get_for_entity("kali") is self.arcana_adapter
        assert self.registry.get_for_entity("maat") is self.arcana_adapter

    def test_unmapped_entity_returns_none(self):
        """Should return None for entities without WAD mapping."""
        assert self.registry.get_for_entity("unknown_entity") is None

    def test_mapping_to_unregistered_wad_logs_warning(self, caplog):
        """Should log a warning when entity maps to unregistered WAD."""
        self.registry.register_entity_to_wad("orphan", "nonexistent_wad")
        assert "no adapter registered" in caplog.text

    def test_multiple_wads(self):
        """Should support multiple WADs with different entity mappings."""
        default = MockAdapter()
        arcana = MockAdapter()

        self.registry.register("_omega_default", default)
        self.registry.register("arcana_novai", arcana)

        self.registry.register_entity_to_wad("prometheus", "_omega_default")
        self.registry.register_entity_to_wad("kali", "arcana_novai")
        self.registry.register_entity_to_wad("lucifer", "arcana_novai")

        assert self.registry.get_for_entity("prometheus") is default
        assert self.registry.get_for_entity("kali") is arcana
        assert self.registry.get_for_entity("lucifer") is arcana

    def test_list_adapters(self):
        """Should list all registered adapters with their class names."""
        self.registry.register("_omega_default", MockAdapter())
        self.registry.register("arcana_novai", MockAdapter())

        listing = self.registry.list_adapters()
        assert "_omega_default" in listing
        assert "arcana_novai" in listing
        assert listing["_omega_default"] == "MockAdapter"

    def test_get_stats(self):
        """Should return registry statistics for observability."""
        self.registry.register("test_wad", MockAdapter())
        self.registry.register_entity_to_wad("entity_a", "test_wad")

        stats = self.registry.get_stats()
        assert stats["adapters"] == 1
        assert stats["wads"] == ["test_wad"]
        assert stats["entity_mappings"] == 1

    def test_double_entity_mapping_overwrites(self):
        """Re-mapping an entity to a different WAD should overwrite."""
        self.registry.register("wad_a", MockAdapter())
        self.registry.register("wad_b", MockAdapter())

        self.registry.register_entity_to_wad("test_entity", "wad_a")
        assert self.registry.get_for_entity("test_entity") is self.registry.get_for_wad("wad_a")

        self.registry.register_entity_to_wad("test_entity", "wad_b")
        assert self.registry.get_for_entity("test_entity") is self.registry.get_for_wad("wad_b")
