# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.0.0

import anyio
from contextlib import asynccontextmanager

class ResourceGuard:
    """Ensures only one model can be loaded/running at a time.
    
    Prevents OOM on memory-constrained systems (e.g. 14GB Ryzen 7).
    """
    def __init__(self, limit: int = 1):
        self._semaphore = anyio.Semaphore(limit)

    @asynccontextmanager
    async def lock(self):
        """Async context manager to acquire the resource semaphore."""
        async with self._semaphore:
            yield
