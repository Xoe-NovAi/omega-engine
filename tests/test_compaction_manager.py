# 🔱 Tests: CompactionManager — Context Window Compaction Trigger
# ⬡ OMEGA ⬡ MEMORY ⬡ tests/test_compaction_manager.py

import pytest
import anyio
from omega.memory.compaction import (
    CompactionManager,
    CompactionResult,
    get_compaction_manager,
    DEFAULT_TRIGGER_THRESHOLD,
    DEFAULT_TARGET_REDUCTION,
)
from omega.memory.block_tools import BlockTools, get_block_store
from omega.memory.recall import RecallStore


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def recall():
    """Provide a fresh RecallStore for tests."""
    import tempfile
    from pathlib import Path
    db_file = tempfile.mktemp(suffix=".db", prefix="recall_compaction_")
    db_path = Path(db_file)
    store = RecallStore(db_path=db_path)
    yield store
    import os
    try:
        os.remove(db_file)
    except OSError:
        pass


@pytest.fixture
def block_tools():
    """Provide BlockTools with isolated DB."""
    import tempfile
    from pathlib import Path
    from omega.memory.block_store import SQLiteBlockStore
    db_file = tempfile.mktemp(suffix=".db", prefix="blocks_compaction_")
    db_path = Path(db_file)
    bstore = SQLiteBlockStore(db_path=db_path)
    bt = BlockTools(bstore)
    yield bt
    import os
    try:
        os.remove(db_file)
    except OSError:
        pass


@pytest.fixture
def manager(block_tools, recall):
    """Provide CompactionManager with injected tools."""
    return CompactionManager(
        block_tools=block_tools,
        recall_store=recall,
        trigger_threshold=0.80,
        target_reduction=0.50,
        context_limit=4000,
    )


# ── Tests: CompactionResult ─────────────────────────────────────────


class TestCompactionResult:
    def test_default_values(self):
        """CompactionResult has sensible defaults."""
        r = CompactionResult()
        assert r.triggered is False
        assert r.tokens_freed == 0
        assert r.tokens_before == 0
        assert r.tokens_after == 0
        assert r.turns_promoted == 0
        assert r.blocks_affected == 0
        assert r.error is None

    def test_triggered_true(self):
        """Can create a triggered result."""
        r = CompactionResult(
            triggered=True,
            tokens_freed=500,
            tokens_before=2000,
            tokens_after=1500,
            turns_promoted=3,
            blocks_affected=1,
        )
        assert r.triggered
        assert r.tokens_freed == 500

    def test_error_result(self):
        """Can create an error result."""
        r = CompactionResult(triggered=False, error="Something broke")
        assert r.error == "Something broke"


# ── Tests: CompactionManager ────────────────────────────────────────


class TestCompactionManagerInit:
    def test_default_config(self):
        """CompactionManager initializes with sensible defaults."""
        cm = CompactionManager()
        assert cm._trigger_threshold == DEFAULT_TRIGGER_THRESHOLD
        assert cm._target_reduction == DEFAULT_TARGET_REDUCTION
        assert cm._context_limit == 4000
        assert cm._lock is not None

    def test_custom_config(self):
        """Can override all config values."""
        cm = CompactionManager(
            trigger_threshold=0.90,
            target_reduction=0.30,
            context_limit=8192,
        )
        assert cm._trigger_threshold == 0.90
        assert cm._target_reduction == 0.30
        assert cm._context_limit == 8192


class TestCompactionManagerCheckAndCompact:
    async def test_no_blocks_no_compaction(self, manager, block_tools):
        """No compaction when there are no blocks."""
        result = await manager.check_and_compact("nonexistent")
        assert result.triggered is False

    async def test_below_threshold_no_compaction(self, manager, block_tools):
        """No compaction when usage is below threshold."""
        # Create a small block (far below threshold)
        await block_tools.create_essential_block("persona", "test_entity", "test")
        result = await manager.check_and_compact("test_entity")
        assert result.triggered is False

    async def test_get_usage_ratio_empty(self, manager):
        """Usage ratio is 0 for empty entity."""
        ratio = await manager.get_usage_ratio("nonexistent")
        assert ratio == 0.0

    async def test_get_usage_ratio_small(self, manager, block_tools):
        """Usage ratio is small for minimal blocks."""
        await block_tools.create_essential_block("persona", "test_entity", "test", value="I am a test entity.")
        ratio = await manager.get_usage_ratio("test_entity")
        assert ratio < 0.80  # Well below threshold
        assert ratio > 0.0

    async def test_get_status_structure(self, manager, block_tools):
        """get_status returns expected structure."""
        await block_tools.create_essential_block("persona", "test_entity", "test")
        status = await manager.get_status("test_entity")
        assert "usage_ratio" in status
        assert "trigger_threshold" in status
        assert "total_tokens" in status
        assert "max_tokens" in status
        assert "is_over_threshold" in status
        assert "num_blocks" in status
        assert "block_labels" in status

    async def test_get_status_over_threshold(self, manager, block_tools):
        """get_status correctly reports over threshold."""
        # Create a very large block
        large_content = "test " * 5000  # ~20000 chars = ~5000 tokens
        await block_tools.create_essential_block(
            "persona", "big_entity", "test", value=large_content,
        )
        status = await manager.get_status("big_entity")
        # 20000 chars / 4 = 5000 tokens > 3200 (80% of 4000)
        assert status["is_over_threshold"] is True

    async def test_concurrent_safety(self, manager, block_tools):
        """Multiple concurrent check_and_compact calls are safe."""
        await block_tools.create_essential_block(
            "persona", "concurrent_entity", "test",
        )

        results = []
        async def check():
            r = await manager.check_and_compact("concurrent_entity")
            results.append(r)

        async with anyio.create_task_group() as tg:
            tg.start_soon(check)
            tg.start_soon(check)
            tg.start_soon(check)

        assert all(r.triggered is False for r in results)


class TestCompactionManagerPromoteExcess:
    async def test_promote_excess_without_recall(self, block_tools):
        """No promotion when recall_store is None."""
        cm = CompactionManager(block_tools=block_tools, recall_store=None)
        await block_tools.create_essential_block(
            "decisions", "test_entity", "test",
        )
        result = await cm.check_and_compact("test_entity")
        assert result.triggered is False

    async def test_promote_excess_with_recall(self, manager, block_tools, recall):
        """Compaction with recall store wired works."""
        # Create a large block to trigger compaction
        large_content = "Important decision: " + "We decided to use " * 1000
        await block_tools.create_essential_block(
            "decisions", "promote_entity", "test",
            value=large_content,
        )

        # Add some turns to recall so we can promote
        await recall.append_exchange(
            entity_name="promote_entity",
            session_id="ses_001",
            turn_index=0,
            user_message="Important decision point",
            assistant_message="We decided to use power-law decay",
        )

        result = await manager.check_and_compact("promote_entity")
        # Should not crash — may or may not trigger depending on block size
        assert isinstance(result, CompactionResult)
        assert result.error is None


class TestCompactionManagerSingleton:
    def test_singleton_same(self):
        """get_compaction_manager returns the same instance."""
        cm1 = get_compaction_manager()
        cm2 = get_compaction_manager()
        assert cm1 is cm2

    def test_singleton_reset(self):
        """Different instances possible with explicit constructor."""
        cm1 = CompactionManager()
        cm2 = CompactionManager()
        assert cm1 is not cm2


# ── Constants Test ──────────────────────────────────────────────────


def test_constants():
    """Constants are reasonable."""
    assert 0.0 < DEFAULT_TRIGGER_THRESHOLD < 1.0
    assert 0.0 < DEFAULT_TARGET_REDUCTION < 1.0
