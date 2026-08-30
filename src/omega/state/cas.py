# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Content Addressable Storage (CAS) — The foundation of the Unified State Manager.
AP: AP-USM-CAS-v1.0.0
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

import anyio
from omega.errors import OmegaPersistenceError

logger = logging.getLogger(__name__)


class CASManager:
    """Handles raw blob storage addressed by SHA-256 hashes.

    Implements the core of the Unified State Manager (USM) by ensuring
    that data is immutable and deduplicated.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        # Default to data/state/blobs
        self.base_dir = (
            base_dir
            or Path(
                os.environ.get(
                    "OMEGA_DATA_DIR",
                    str(Path(__file__).resolve().parent.parent.parent.parent / "data"),
                )
            )
            / "state"
            / "blobs"
        )

    async def initialize(self) -> None:
        """Ensure the blob directory exists."""
        await anyio.Path(self.base_dir).mkdir(parents=True, exist_ok=True)

    def _get_blob_path(self, blob_hash: str) -> Path:
        """Compute the path for a blob using the first 4 chars as a prefix.
        Prevents directory bloat by splitting blobs across 256x256 subdirectories.
        """
        # Sharding: blobs/ab/cd/<full-hash>
        return self.base_dir / blob_hash[:2] / blob_hash[2:4] / blob_hash

    async def put(self, data: bytes) -> str:
        """Store data in CAS and return its SHA-256 hash.

        [id-soft: vet-015] ZONEID Pattern — the hash itself acts as the
        ultimate integrity marker.
        """
        if not data:
            raise OmegaPersistenceError("Cannot store empty data")
        blob_hash = hashlib.sha256(data).hexdigest()
        blob_path = self._get_blob_path(blob_hash)

        if await anyio.Path(blob_path).exists():
            return blob_hash

        try:
            await anyio.Path(blob_path.parent).mkdir(parents=True, exist_ok=True)
            # Use atomic write: write to tmp then rename
            tmp_path = blob_path.with_suffix(".tmp")
            async with await anyio.open_file(str(tmp_path), "wb") as f:
                await f.write(data)

            await anyio.Path(tmp_path).rename(blob_path)
            return blob_hash
        except (OSError, RuntimeError) as e:
            logger.error(f"CAS put failed for hash {blob_hash}: {e}", exc_info=True)
            raise OmegaPersistenceError(
                f"Failed to store blob {blob_hash}: {e}", raw_error=e
            ) from e

    async def get(self, blob_hash: str) -> bytes:
        """Retrieve data for a given hash."""
        blob_path = self._get_blob_path(blob_hash)

        if not await anyio.Path(blob_path).exists():
            raise OmegaPersistenceError(f"Blob {blob_hash} not found in CAS")

        try:
            async with await anyio.open_file(str(blob_path), "rb") as f:
                data = await f.read()

            # Verify integrity
            if hashlib.sha256(data).hexdigest() != blob_hash:
                raise OmegaPersistenceError(f"CAS corruption detected for blob {blob_hash}")

            return data
        except (OSError, RuntimeError) as e:
            logger.error(f"CAS get failed for {blob_hash}: {e}", exc_info=True)
            raise OmegaPersistenceError(
                f"Failed to retrieve blob {blob_hash}: {e}", raw_error=e
            ) from e

    async def exists(self, blob_hash: str) -> bool:
        """Check if a blob exists in CAS."""
        return await anyio.Path(self._get_blob_path(blob_hash)).exists()

    async def delete(self, blob_hash: str) -> None:
        """Delete a blob from CAS.
        Note: In a full USM, this would be reference-counted.
        """
        blob_path = self._get_blob_path(blob_hash)
        try:
            if await anyio.Path(blob_path).exists():
                await anyio.Path(blob_path).unlink()
        except (OSError, RuntimeError) as e:
            logger.warning(f"CAS delete failed for {blob_hash}: {e}")

    async def stats(self) -> dict:
        """Return CAS statistics."""
        # Since we don't have a refcount DB in this simple CASManager yet,
        # we just count the files in the blobs directory.
        total_blobs = 0
        total_size = 0
        try:
            # Walk the sharded directory structure
            for shard in self.base_dir.iterdir():
                if shard.is_dir():
                    for subshard in shard.iterdir():
                        if subshard.is_dir():
                            for blob in subshard.iterdir():
                                total_blobs += 1
                                total_size += blob.stat().st_size
        except (OSError, RuntimeError):
            pass
        return {
            "unique_blobs": total_blobs,
            "total_bytes": total_size,
            "total_refs": total_blobs,  # Approximation
        }
