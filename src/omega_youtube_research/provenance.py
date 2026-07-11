# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# ProvenanceChain — cryptographic linkage between extracted chunks (Provenance Chain Fix).
#
# Heritage:
#   [heritage: anyio 2024] No async needed — pure hashing, but chain build is CPU-bound
#     and may be wrapped by callers in anyio.to_thread.run_sync if used on large inputs.

"""ProvenanceChain — hash-linked chain of extracted transcript chunks.

This is the **Provenance Chain Fix** (P7 gap): each extracted chunk cryptographically
references its *parent* chunk and its *source*, forming a tamper-evident chain. The
``chain_hash`` of a chunk is a SHA-256 over ``(parent_chain_hash || content_hash ||
source_id)``. The first chunk has no parent, so its ``chain_hash`` binds directly to
the ``source_id``. Any modification to a chunk's content, or reordering/splicing of
chunks, breaks verification of every downstream chunk.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel

from .errors import ProvenanceIntegrityError


class ProvenanceChunk(BaseModel):
    """A single link in the provenance chain."""

    chunk_id: str
    parent_chunk_id: Optional[str] = None
    source_id: str
    sequence: int
    content_hash: str
    chain_hash: str
    source_url: Optional[str] = None
    created_at: str


class ProvenanceChain:
    """Builds and verifies a hash-linked chain of extracted chunks.

    Args:
        source_id: Stable identifier for the source transcript (e.g. ``yt_<vid>_<ts>``).
        source_url: Canonical source URL (embedded in every chunk for attribution).
    """

    def __init__(self, source_id: str, source_url: Optional[str] = None):
        self._source_id = source_id
        self._source_url = source_url
        self._last_chain_hash: Optional[str] = None
        self._last_chunk_id: Optional[str] = None
        self._sequence = 0

    @property
    def source_id(self) -> str:
        """Return the chain's source identifier."""
        return self._source_id

    @staticmethod
    def _sha256(text: str) -> str:
        """Return a ``sha256:``-prefixed hex digest for ``text``."""
        return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

    def add_chunk(self, content: str) -> ProvenanceChunk:
        """Append a chunk to the chain, linking it to the previous chunk + source.

        Args:
            content: The chunk's text content.

        Returns:
            The newly created ``ProvenanceChunk`` with its ``chain_hash``.
        """
        self._sequence += 1
        content_hash = self._sha256(content)
        parent = self._last_chain_hash
        # Chain binding: parent chain hash (or source_id for the root) + content + source.
        if parent is not None:
            binding = parent + content_hash + self._source_id
        else:
            binding = self._source_id + content_hash + self._source_id
        chain_hash = self._sha256(binding)
        chunk = ProvenanceChunk(
            chunk_id=f"chunk_{uuid.uuid4().hex}",
            parent_chunk_id=None if parent is None else self._last_chunk_id,
            source_id=self._source_id,
            sequence=self._sequence,
            content_hash=content_hash,
            chain_hash=chain_hash,
            source_url=self._source_url,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._last_chain_hash = chain_hash
        self._last_chunk_id = chunk.chunk_id
        return chunk

    def verify(self, chunks: List[ProvenanceChunk]) -> bool:
        """Verify the integrity of an ordered list of chunks.

        Recomputes each chunk's expected ``chain_hash`` from its parent and content,
        and confirms the sequence is contiguous starting at 1.

        Args:
            chunks: Chunks in extraction order.

        Returns:
            ``True`` if every link is internally consistent and correctly sequenced;
            ``False`` otherwise (tamper / reorder / splice detected).

        Raises:
            ProvenanceIntegrityError: If a chunk is missing required hash fields.
        """
        expected_seq = 1
        prev_chain_hash: Optional[str] = None
        prev_chunk_id: Optional[str] = None
        for chunk in chunks:
            if not chunk.content_hash or not chunk.chain_hash:
                raise ProvenanceIntegrityError(
                    f"Chunk {chunk.chunk_id} missing hash fields"
                )
            if chunk.sequence != expected_seq:
                return False
            # Recompute binding using the *previous chunk's* chain hash.
            binding = (
                prev_chain_hash if prev_chain_hash is not None else self._source_id
            ) + chunk.content_hash + chunk.source_id
            if self._sha256(binding) != chunk.chain_hash:
                return False
            if chunk.parent_chunk_id != prev_chunk_id:
                return False
            prev_chain_hash = chunk.chain_hash
            prev_chunk_id = chunk.chunk_id
            expected_seq += 1
        return True
