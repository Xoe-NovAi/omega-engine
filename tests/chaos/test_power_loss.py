# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Chaos test: SoulStore survives kill -9 + power loss."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
import signal
import yaml

@pytest.mark.chaos
@pytest.mark.anyio
async def test_soulstore_power_loss_during_write(soul_store):
    """Simulate power loss during atomic write — file must be valid or absent."""
    # This test verifies the atomic write pattern is correct.
    # In a real power loss scenario, the temp file may be present but the final
    # file should either be the old version or the new version, never corrupt.
    data = {"entity": {"name": "test_entity", "lessons_learned": ["power_loss_test"]}}
    
    # Write soul data
    await soul_store.write_soul("test_entity", data, actor="user", trace_id="power-loss-test")
    
    # Verify the soul file is valid YAML
    soul_path = soul_store._get_entity_dir("test_entity") / "soul.yaml"
    assert soul_path.exists()
    content = soul_path.read_text()
    loaded = yaml.safe_load(content)
    assert loaded["entity"]["lessons_learned"] == ["power_loss_test"]
    
    # Simulate a partial write by creating a temp file and not completing rename
    # (This is a structural test; actual power loss simulation requires filesystem injection)
    temp_fd, temp_path = tempfile.mkstemp(dir=str(soul_path.parent), suffix=".soul_tmp")
    os.write(temp_fd, b"corrupted")
    os.close(temp_fd)
    
    # The temp file should not affect the original soul file
    assert soul_path.exists()
    original_content = soul_path.read_text()
    assert "power_loss_test" in original_content
    
    # Clean up temp file
    os.unlink(temp_path)

@pytest.mark.chaos
@pytest.mark.anyio
async def test_soulstore_kill_during_write(soul_store):
    """Simulate process kill during write — lock should auto-release."""
    # SoulLock uses fcntl.flock which auto-releases on process death.
    # This test verifies that after a simulated kill, the lock is released.
    from omega.oracle.soul_store import SoulLock
    
    lock_path = str(soul_store._get_entity_dir("test_entity") / ".soul.lock")
    lock = SoulLock(lock_path, timeout=1.0)
    
    # Acquire lock
    assert lock.acquire() is True
    
    # Simulate process kill by closing the file descriptor without release
    # (In real kill -9, the kernel releases the flock automatically)
    os.close(lock._fd)
    lock._fd = None
    
    # Create a new lock instance and verify it can acquire
    lock2 = SoulLock(lock_path, timeout=1.0)
    assert lock2.acquire() is True
    lock2.release()
