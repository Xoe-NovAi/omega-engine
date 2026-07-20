# 🔱 Omega Engine — OOMProtector Contract Tests (P0-1 RAM Hardening)
# ⬡ OMEGA ⬡ MA'AT ⬡ P1 ⬡ 2026-07-12
#
# [M21: Gate Integrity] Every new function gets a contract test validating its
# return type via isinstance(). These tests verify OOMProtector.check() returns
# a bool and that ResourceGuard.lock() hard-stops when RAM is critical.

from unittest.mock import AsyncMock

import pytest

from omega.errors import InferenceOOMError
from omega.oracle.resource_guard import OOMProtector, ResourceGuard


def _write_meminfo(tmp_path, mem_available_kb: int) -> str:
    p = tmp_path / "meminfo"
    p.write_text(f"MemTotal: 12000000 kB\nMemAvailable: {mem_available_kb} kB\n")
    return str(p)


@pytest.mark.anyio
async def test_oom_protector_check_returns_bool():
    """M21: check() returns a bool."""
    prot = OOMProtector(min_ram_mb=2048, meminfo_path="/nonexistent/path")
    result = await prot.check()
    assert isinstance(result, bool), f"Expected bool, got {type(result).__name__}"


@pytest.mark.anyio
async def test_oom_protector_safe_when_plenty_of_ram(tmp_path):
    """M21: high MemAvailable → check() returns True (safe)."""
    meminfo = _write_meminfo(tmp_path, 9_000_000)  # ~9000 MB available
    prot = OOMProtector(min_ram_mb=2048, meminfo_path=meminfo)
    assert await prot.check() is True


@pytest.mark.anyio
async def test_oom_protector_hard_stop_when_critical(tmp_path):
    """M21: low MemAvailable → check() returns False (hard-stop)."""
    meminfo = _write_meminfo(tmp_path, 100)  # 100 kB available << 2048 MB
    prot = OOMProtector(min_ram_mb=2048, meminfo_path=meminfo)
    assert await prot.check() is False


@pytest.mark.anyio
async def test_resource_guard_lock_blocks_on_oom():
    """M21: ResourceGuard.lock() raises InferenceOOMError when OOM is critical."""
    guard = ResourceGuard(max_ram_mb=12288)
    guard._oom_protector.check = AsyncMock(return_value=False)
    with pytest.raises(InferenceOOMError):
        async with guard.lock(weight=1):
            pass  # should never be reached


@pytest.mark.anyio
async def test_resource_guard_lock_allows_when_safe():
    """M21: ResourceGuard.lock() proceeds normally when RAM is safe."""
    guard = ResourceGuard(max_ram_mb=12288)
    guard._oom_protector.check = AsyncMock(return_value=True)
    async with guard.lock(weight=1):
        pass  # acquired and released without error
