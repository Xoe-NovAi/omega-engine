# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.0.0

import anyio
from contextlib import asynccontextmanager

class ResourceGuard:
    """Ensures model resource usage doesn't exceed system capacity.
    
    Uses a weighted semaphore pattern to allow multiple light models 
    to run concurrently while restricting heavy models.
    """
    def __init__(self, total_capacity: int = 8):
        self._capacity = total_capacity
        self._current_usage = 0
        self._condition = anyio.Condition()

    @asynccontextmanager
    async def lock(self, weight: int = 1):
        """Async context manager to acquire weighted resource locks."""
        async with self._condition:
            while self._current_usage + weight > self._capacity:
                await self._condition.wait()
            self._current_usage += weight
        
        try:
            yield
        finally:
            async with self._condition:
                self._current_usage -= weight
                self._condition.notify_all()
