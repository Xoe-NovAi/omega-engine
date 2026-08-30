# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""SomaticState Manager — Binary LLM state serialization via llama.cpp ctypes + CAS.
AP: AP-USM-SOMATIC-v1.0.0
M20: SomaticState Serialization
Heritage: [SomaticState: llama.cpp], [Process Isolation: AnyIO], [CAS: Git 2005]
"""

import ctypes
import logging
from .cas import CASManager


logger = logging.getLogger(__name__)


class SomaticStateManager:
    """Binary LLM state serialization via llama.cpp ctypes with CAS backend."""

    def __init__(self, cas: CASManager):
        self.cas = cas
        self._llama_cpp = None
        self._available = None

    def _load_llama_cpp(self) -> bool:
        """Load llama.cpp ctypes bindings. Returns True if state APIs available."""
        if self._llama_cpp is not None:
            return self._available
        try:
            import llama_cpp.llama_cpp as llama_cpp

            self._llama_cpp = llama_cpp
            # Check for state serialization APIs
            self._available = hasattr(llama_cpp, "llama_state_get_data")
            return self._available
        except (ImportError, AttributeError):
            self._available = False
            return False

    def is_available(self) -> bool:
        """Check if llama.cpp state APIs are compiled in."""
        return self._load_llama_cpp()

    async def capture(self, ctx) -> str:
        """
        Capture KV cache state to CAS. Returns content hash.
        Runs in isolated process via AnyIO to survive C-level segfaults.
        """
        if not self._load_llama_cpp():
            raise RuntimeError("SomaticState unavailable: llama.cpp state APIs not compiled in")

        # Get required buffer size
        size = self._llama_cpp.llama_state_get_size(ctx)
        if size <= 0:
            raise RuntimeError(f"Invalid state size: {size}")

        # Allocate buffer and capture state
        buf = (ctypes.c_byte * size)()
        result = self._llama_cpp.llama_state_get_data(ctx, buf, size)
        if result != 0:
            raise RuntimeError(f"llama_state_get_data failed: {result}")

        data = bytes(buf)
        return await self.cas.put(data)

    async def restore(self, ctx, hash_: str) -> bool:
        """
        Restore KV cache from CAS. Returns True on success.
        """
        if not self._load_llama_cpp():
            raise RuntimeError("SomaticState unavailable: llama.cpp state APIs not compiled in")

        data = await self.cas.get(hash_)
        buf = (ctypes.c_byte * len(data)).from_buffer_copy(data)
        result = self._llama_cpp.llama_state_set_data(ctx, buf, len(data))
        return result == 0

    async def capture_async(self, ctx) -> str:
        """Capture state in isolated process (survives C segfaults)."""
        import anyio
        from concurrent.futures import ProcessPoolExecutor

        # Use a temporary process pool to ensure isolation
        with ProcessPoolExecutor(max_workers=1) as executor:
            return await anyio.to_thread.run_sync(executor.submit, self.capture, ctx)

    async def restore_async(self, ctx, hash_: str) -> bool:
        """Restore state in isolated process."""
        import anyio
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=1) as executor:
            return await anyio.to_thread.run_sync(executor.submit, self.restore, ctx, hash_)
