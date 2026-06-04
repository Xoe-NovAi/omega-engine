import anyio
import pytest
import asyncio
from omega.oracle.resource_guard import ResourceGuard, AtomicLock
from omega.constants import ZONEID_ATOMIC, ZONEID_PROBE

@pytest.mark.anyio
async def test_atomic_lock():
    lock = AtomicLock()
    shared_resource = []
    
    async def increment():
        async with lock:
            val = len(shared_resource)
            await anyio.sleep(0.01)
            shared_resource.append(val)
            
    async with anyio.create_task_group() as tg:
        for _ in range(10):
            tg.start_soon(increment)
            
    assert len(shared_resource) == 10
    assert shared_resource == sorted(shared_resource)

@pytest.mark.anyio
async def test_hardware_lock_capacity():
    # Capacity of 2
    guard = ResourceGuard(total_capacity=2)
    active_locks = 0
    max_active = 0
    
    async def worker():
        nonlocal active_locks, max_active
        async with guard.lock(weight=1):
            active_locks += 1
            max_active = max(max_active, active_locks)
            await anyio.sleep(0.05)
            active_locks -= 1
            
    async with anyio.create_task_group() as tg:
        for _ in range(5):
            tg.start_soon(worker)
            
    assert max_active <= 2

@pytest.mark.anyio
async def test_hardware_lock_weighted():
    # Capacity of 4
    guard = ResourceGuard(total_capacity=4)
    active_locks = 0
    max_active = 0
    
    async def heavy_worker():
        nonlocal active_locks, max_active
        async with guard.lock(weight=4):
            active_locks += 1
            max_active = max(max_active, active_locks)
            await anyio.sleep(0.05)
            active_locks -= 1
            
    async with anyio.create_task_group() as tg:
        for _ in range(3):
            tg.start_soon(heavy_worker)
            
    assert max_active == 1

@pytest.mark.anyio
async def test_hardware_lock_integrity():
    guard = ResourceGuard()
    # Corrupt the magic
    guard._magic = 0xDEADBEEF
    
    with pytest.raises(ValueError, match="ZONEID mismatch"):
        async with guard.lock():
            pass

@pytest.mark.anyio
async def test_atomic_lock_integrity():
    lock = AtomicLock()
    # Corrupt the magic
    lock._magic = 0xDEADBEEF
    
    with pytest.raises(ValueError, match="ZONEID mismatch"):
        async with lock:
            pass

