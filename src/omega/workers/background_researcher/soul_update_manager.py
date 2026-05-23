import anyio
import yaml
from anyio.to_thread import run_sync
from pathlib import Path
from typing import Dict, Any

class SoulUpdateManager:
    def __init__(self, soul_file_path: Path):
        self.soul_file_path = soul_file_path
        self.lock = anyio.Lock()

    async def _read_soul_file(self) -> Dict[str, Any]:
        """Reads the soul YAML file."""
        if not await run_sync(self.soul_file_path.exists):
            return {}
        async with await anyio.open_file(self.soul_file_path, 'r') as f:
            content = await f.read()
            return await run_sync(yaml.safe_load, content) or {}

    async def _write_soul_file(self, data: Dict[str, Any]):
        """Writes the soul YAML file."""
        await run_sync(self.soul_file_path.parent.mkdir, parents=True, exist_ok=True)
        async with await anyio.open_file(self.soul_file_path, 'w') as f:
            await f.write(await run_sync(yaml.safe_dump, data, indent=2))

    async def update_soul(self, update_func) -> Dict[str, Any]:
        """
        Atomically updates the soul file using a provided asynchronous function.
        The update_func will receive the current soul data and should return the modified data.
        """
        async with self.lock:
            current_soul = await self._read_soul_file()
            updated_soul = await update_func(current_soul)
            await self._write_soul_file(updated_soul)
            return updated_soul

    async def get_soul(self) -> Dict[str, Any]:
        """Gets the current soul data."""
        async with self.lock:
            return await self._read_soul_file()
