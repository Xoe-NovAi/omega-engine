# 🔱 Omega Engine — MnemosyneAdapter Tests
# ⬡ OMEGA ⬡ TESTS ⬡ MNEMOSYNE ⬡ v1.0.0 ⬡ 2026-06-15

"""Tests for the Arcana-NovAi MnemosyneAdapter (WAD-layer IMemoryAdapter)."""

import json
import os
import tempfile
import time

import pytest

from omega.memory.adapters import (
    IMemoryAdapter,
    MemoryAdapterRegistry,
    MemoryRecord,
    MemoryType,
    MemoryPriority,
)


# ── Fixtures ──

@pytest.fixture
async def adapter():
    """Create a fresh MnemosyneAdapter with a temp vault dir."""
    import tempfile
    from pathlib import Path
    from config.wads.arcana_novai.adapters.mnemosyne_adapter import MnemosyneAdapter
    # Override vault dir to temp
    import config.wads.arcana_novai.adapters.mnemosyne_adapter as mod
    orig_getter = mod._get_vault_dir
    test_vault_dir = Path(tempfile.mkdtemp(prefix="mnemosyne_test_"))
    mod._get_vault_dir = lambda: test_vault_dir
    
    inst = MnemosyneAdapter()
    await inst.initialize()
    yield inst
    
    # Cleanup temp dir
    import shutil
    vault_dir = inst._vault_dir
    await inst.close()
    if vault_dir and vault_dir.exists():
        shutil.rmtree(vault_dir, ignore_errors=True)
    
    # Restore
    mod._get_vault_dir = orig_getter


# ── Basic Contract Tests ──

class TestMnemosyneAdapterContract:
    """Verify MnemosyneAdapter satisfies the IMemoryAdapter contract."""

    async def test_is_imemoryadapter(self, adapter):
        """Should implement IMemoryAdapter."""
        assert isinstance(adapter, IMemoryAdapter)

    async def test_spheres_loaded(self, adapter):
        """Should load 13 spheres from spheres.yaml."""
        assert len(adapter._spheres) == 13
        assert "keter" in adapter._spheres
        assert "mnemosyne" in adapter._spheres

    async def test_qliphoth_loaded(self, adapter):
        """Should load 12 Qliphothic shells from qliphoth.yaml."""
        assert len(adapter._qliphoth) == 12
        assert "thaumiel" in adapter._qliphoth
        assert "gemaliel" in adapter._qliphoth

    async def test_entity_spheres_mapped(self, adapter):
        """Should map entities to spheres."""
        assert adapter._entity_spheres.get("kali") == "malkuth"
        assert adapter._entity_spheres.get("prometheus") == "keter"
        assert adapter._entity_spheres.get("iris") == "mnemosyne"


# ── Vault CRUD Tests ──

class TestMnemosyneAdapterVault:
    """Verify vault read/write operations."""

    async def test_get_vault_nonexistent(self, adapter):
        """Should return None for nonexistent vault key."""
        result = await adapter.get_vault("kali", "nonexistent")
        assert result is None

    async def test_put_and_get_vault(self, adapter):
        """Should write and read a vault entry."""
        data = {"key": "value", "number": 42}
        await adapter.put_vault("kali", "test_entry", data)
        result = await adapter.get_vault("kali", "test_entry")
        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    async def test_update_vault(self, adapter):
        """Should overwrite existing vault entry."""
        await adapter.put_vault("kali", "shadow", {"count": 1})
        await adapter.put_vault("kali", "shadow", {"count": 2, "extra": True})
        result = await adapter.get_vault("kali", "shadow")
        assert result["count"] == 2
        assert result["extra"] is True

    async def test_multiple_entities_isolated(self, adapter):
        """Vault entries for different entities should be isolated."""
        await adapter.put_vault("kali", "test", {"entity": "kali"})
        await adapter.put_vault("maat", "test", {"entity": "maat"})

        kali_vault = await adapter.get_vault("kali", "test")
        maat_vault = await adapter.get_vault("maat", "test")

        assert kali_vault["entity"] == "kali"
        assert maat_vault["entity"] == "maat"


# ── History Tests ──

class TestMnemosyneAdapterHistory:
    """Verify exchange history persistence."""

    async def test_save_and_get_history(self, adapter):
        """Should save and retrieve exchange history."""
        exchanges = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        await adapter.save_history("kali", "session_test_001", exchanges)

        result = await adapter.get_history("kali", "session_test_001", limit=10)
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"

    async def test_history_limit(self, adapter):
        """Should respect limit parameter."""
        exchanges = [{"role": "user", "content": f"msg_{i}"} for i in range(20)]
        await adapter.save_history("kali", "session_limit", exchanges)

        result = await adapter.get_history("kali", "session_limit", limit=5)
        assert len(result) == 5

    async def test_history_nonexistent_session(self, adapter):
        """Should return empty list for nonexistent session."""
        result = await adapter.get_history("kali", "nonexistent_session", limit=10)
        assert result == []


# ── Archive Tests ──

class TestMnemosyneAdapterArchive:
    """Verify session archiving."""

    async def test_archive_session(self, adapter):
        """Should archive a session without error."""
        exchanges = [{"role": "user", "content": "test"}]
        await adapter.save_history("kali", "session_arch", exchanges)

        success = await adapter.archive("kali", "session_arch")
        assert success is True

        # After archive, live session should be gone
        result = await adapter.get_history("kali", "session_arch", limit=10)
        assert result == []

    async def test_archive_nonexistent(self, adapter):
        """Should return False for nonexistent session."""
        success = await adapter.archive("kali", "nonexistent")
        assert success is False


# ── Sphere Tests ──

class TestMnemosyneAdapterSphere:
    """Verify sphere/qliphoth queries."""

    async def test_get_sphere_by_entity(self, adapter):
        """Should return sphere metadata for an entity."""
        sphere = await adapter.get_sphere("kali")
        assert sphere.get("name") == "Malkuth"
        assert sphere.get("domain") == "manifestation"
        assert sphere.get("archetype") == "manifestor"

    async def test_get_sphere_by_name(self, adapter):
        """Should return sphere metadata by sphere name."""
        sphere = await adapter.get_sphere("nonexistent", sphere_name="keter")
        assert sphere.get("domain") == "strategic_direction"
        assert sphere.get("translation") == "Crown"

    async def test_get_sphere_unknown_entity(self, adapter):
        """Should return empty dict for unknown entity."""
        sphere = await adapter.get_sphere("unknown_entity")
        assert sphere == {}

    async def test_get_sphere_unknown_name(self, adapter):
        """Should return empty dict for unknown sphere name."""
        sphere = await adapter.get_sphere("kali", sphere_name="nonexistent")
        assert sphere == {}

    async def test_get_qliphoth(self, adapter):
        """Should return qliphothic taxonomy."""
        qliphoth = await adapter.get_qliphoth()
        assert "shells" in qliphoth
        assert "thaumiel" in qliphoth["shells"]
        assert "history" not in qliphoth or qliphoth.get("history", {}).get("failures", []) == []

    async def test_get_qliphoth_with_entity(self, adapter):
        """Should return qliphoth with entity's failure history."""
        qliphoth = await adapter.get_qliphoth("kali")
        assert "shells" in qliphoth
        # No history yet
        assert qliphoth.get("history", {}).get("failures", []) == []


# ── Lifecycle Hooks Tests ──

class TestMnemosyneAdapterLifecycle:
    """Verify session lifecycle hooks."""

    async def test_on_session_end_updates_shadow(self, adapter):
        """Session end should update shadow state."""
        # First session
        records = await adapter.on_session_end("kali", "test transcript")
        assert len(records) == 1
        assert records[0].entity_name == "kali"
        assert records[0].memory_type == MemoryType.EPISODIC

        shadow = await adapter.get_vault("kali", "shadow")
        assert shadow is not None
        assert shadow["session_count"] == 1
        assert shadow["evolution_stage"] == "AWAKENING"  # 1 session < 3

        # Second session
        await adapter.on_session_end("kali", "another transcript")
        shadow = await adapter.get_vault("kali", "shadow")
        assert shadow["session_count"] == 2

    async def test_on_pre_compact(self, adapter):
        """Pre-compact should return vault snapshot."""
        await adapter.on_session_end("kali", "test")
        checkpoint = await adapter.on_pre_compact("kali", "session_001")
        assert "vault_snapshot" in checkpoint
        assert checkpoint["sphere"] == "malkuth"
        assert checkpoint["adapter"] == "mnemosyne"


# ── Registry Integration Tests ──

class TestMnemosyneAdapterRegistry:
    """Verify MnemosyneAdapter works with MemoryAdapterRegistry."""

    async def test_registry_integration(self, adapter):
        """Should register and be found via registry."""
        registry = MemoryAdapterRegistry()
        registry.register("arcana_novai", adapter)
        registry.register_entity_to_wad("kali", "arcana_novai")

        found = registry.get_for_entity("kali")
        assert found is adapter

        sphere = await found.get_sphere("kali")
        assert sphere.get("name") == "Malkuth"
