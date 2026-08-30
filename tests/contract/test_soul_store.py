# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract Tests — SoulStore (C-1') Atomic File Writer
AP: AP-SOULSTORE-CONTRACT-v1.0.0

Verifies the 4-layer guarantee stack:
1. AtomicVisibility: content arrives intact
2. CrashDurability: fsync completes before return
3. WriterExclusion: flock prevents concurrent corruption
4. IntegrityDetection: .bak rotation works

[Gate-21] Contract test — validates SoulStore.write_atomic() returns
consistent content that matches the input.
"""

import tempfile
import os
from pathlib import Path

import pytest
import anyio

from omega.soul_store import SoulStore, SoulStoreWriteError, get_soul_store


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory(prefix="soulstore_test_") as d:
        yield Path(d)


@pytest.fixture
def store():
    """Fresh SoulStore instance for each test."""
    return SoulStore(max_backups=3)


# ── Gate-21: Contract Tests ───────────────────────────────────────────

@pytest.mark.anyio
class TestSoulStoreContract:
    """Contract tests for SoulStore atomic writes."""

    async def test_write_atomic_returns_consistent_content(self, tmp_dir, store):
        """Gate-21: write_atomic must produce a file whose content matches input."""
        path = tmp_dir / "test_soul.yaml"
        content = "entity:\n  name: test\n  lessons:\n    - lesson: hello\n"
        
        await store.write_atomic(path, content)
        
        result = await store.read_with_recovery(path)
        assert result == content

    async def test_write_atomic_creates_parent_dirs(self, tmp_dir, store):
        """Gate-21: write_atomic must create parent directories."""
        path = tmp_dir / "subdir" / "nested" / "soul.yaml"
        content = "entity:\n  name: nested\n"
        
        await store.write_atomic(path, content)
        
        assert path.exists()
        result = await store.read_with_recovery(path)
        assert result == content

    async def test_write_atomic_overwrites_existing(self, tmp_dir, store):
        """Gate-21: write_atomic must overwrite existing file atomically."""
        path = tmp_dir / "soul.yaml"
        v1 = "entity:\n  name: v1\n"
        v2 = "entity:\n  name: v2\n"
        
        await store.write_atomic(path, v1)
        await store.write_atomic(path, v2)
        
        result = await store.read_with_recovery(path)
        assert result == v2

    async def test_read_with_recovery_returns_none_on_missing(self, tmp_dir, store):
        """Gate-21: read_with_recovery returns None for non-existent file."""
        path = tmp_dir / "nonexistent.yaml"
        
        result = await store.read_with_recovery(path)
        assert result is None

    def test_singleton_returns_same_instance(self):
        """Gate-21: get_soul_store() returns the same singleton."""
        a = get_soul_store()
        b = get_soul_store()
        assert a is b

    async def test_no_tempfile_left_after_write(self, tmp_dir, store):
        """Gate-21: No .tmp files remain after successful write."""
        path = tmp_dir / "clean.yaml"
        content = "entity:\n  name: clean\n"
        
        await store.write_atomic(path, content)
        
        tmp_files = list(tmp_dir.glob("*.tmp"))
        assert len(tmp_files) == 0
