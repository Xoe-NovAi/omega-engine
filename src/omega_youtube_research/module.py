# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# YouTubeResearchModule — orchestrates Sieve -> Signer -> ProvenanceChain -> Persistence.
#
# Heritage:
#   [heritage: anyio 2024] All I/O wrapped in anyio.to_thread.run_sync where blocking
#   [heritage: pydantic 2017] Typed IngestResult contract for every public API

"""YouTubeResearchModule — the P0 structural orchestrator.

Wires the four P0 components into a single ingest pipeline and emits a metadata
dictionary compatible with ``MemoryStore.add_exchange(metadata=...)`` so the
provenance chain propagates end-to-end (sca.json -> MemoryStore -> downstream
Gnosis Graph). This is the Provenance Chain Fix at the integration boundary.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .config import YouTubeResearchConfig
from .errors import YouTubeResearchError
from .persistence import AtomicPersistence, ProvenanceChunkRecord
from .provenance import ProvenanceChain, ProvenanceChunk
from .signer import SovereignSigner, SourceChainAttestation
from .sieve import SieveResult, SovereignSieve


class IngestResult(BaseModel):
    """Result of a full ingest pass (Sieve -> Sign -> Chain -> Persist)."""

    source_id: str
    source_url: str
    provenance_hash: str
    chunk_count: int
    attestation: SourceChainAttestation
    chunks: List[ProvenanceChunk]


class YouTubeResearchModule:
    """Sovereign YouTube transcript ingestion + provenance module (P0).

    Args:
        config: Module configuration (loaded from YAML by default).
        signer: Pre-built ``SovereignSigner``. If omitted, built from config keys.
        persistence: Pre-built ``AtomicPersistence``. If omitted, built from config.
    """

    def __init__(
        self,
        config: Optional[YouTubeResearchConfig] = None,
        signer: Optional[SovereignSigner] = None,
        persistence: Optional[AtomicPersistence] = None,
    ):
        self._config = config or YouTubeResearchConfig.load()
        self._sieve = SovereignSieve(self._config.sieve)
        self._signer = signer or SovereignSigner.from_config(self._config.signer)
        if persistence is None:
            persistence = AtomicPersistence(
                db_path=Path(self._config.persistence.db_path),
                tmp_suffix=self._config.persistence.tmp_suffix,
            )
        self._persistence = persistence

    async def init(self) -> None:
        """Initialise backing persistence (WAL SQLite)."""
        await self._persistence.init()

    async def close(self) -> None:
        """Close backing persistence."""
        await self._persistence.close()

    async def ingest_transcript(
        self,
        *,
        video_id: str,
        raw_transcript: str,
        source_url: Optional[str] = None,
        chunk_size: Optional[int] = None,
    ) -> IngestResult:
        """Run the full Sieve-and-Sign pipeline over a raw transcript.

        Args:
            video_id: YouTube video id (used to build the stable ``source_id``).
            raw_transcript: The raw transcript text to sieve + sign.
            source_url: Canonical URL. Defaults to the watch URL for ``video_id``.
            chunk_size: Optional override for transcript chunk size (characters).

        Returns:
            An ``IngestResult`` carrying the source id, provenance hash, and the
            full provenance chunk chain.
        """
        if not video_id:
            raise YouTubeResearchError("ingest_transcript requires a non-empty video_id")
        url = source_url or f"https://www.youtube.com/watch?v={video_id}"
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        source_id = f"yt_{video_id}_{ts}"

        # 1. Sieve
        sieve_result: SieveResult = self._sieve.clean_transcript(raw_transcript)

        # 2. Sign (Sieve-and-Sign)
        attestation = self._signer.sign(
            cleaned_text=sieve_result.cleaned_text,
            sieve_metadata=sieve_result.metadata.model_dump(),
            source_id=source_id,
            source_type="youtube_transcript",
            source_url=url,
        )

        # 3. Provenance chain (split cleaned text into linked chunks)
        chunks = self._build_chain(
            source_id=source_id,
            source_url=url,
            cleaned_text=sieve_result.cleaned_text,
            chunk_size=chunk_size or self._config.persistence.chunk_size,
        )

        # 4. Persist (WAL SQLite + atomic JSON sidecar)
        await self._persistence.store_attestation(attestation)
        for ch in chunks:
            await self._persistence.store_chunk(
                ProvenanceChunkRecord(
                    chunk_id=ch.chunk_id,
                    source_id=ch.source_id,
                    parent_chunk_id=ch.parent_chunk_id,
                    sequence=ch.sequence,
                    content_hash=ch.content_hash,
                    chain_hash=ch.chain_hash,
                    source_url=ch.source_url,
                    created_at=ch.created_at,
                )
            )
        sidecar = (
            Path(self._config.persistence.db_path).parent
            / f"{source_id}.sca.json"
        )
        await self._persistence.atomic_write_json(
            sidecar, attestation.model_dump()
        )

        return IngestResult(
            source_id=source_id,
            source_url=url,
            provenance_hash=attestation.provenance_hash,
            chunk_count=len(chunks),
            attestation=attestation,
            chunks=chunks,
        )

    @staticmethod
    def _build_chain(
        *, source_id: str, source_url: str, cleaned_text: str, chunk_size: int
    ) -> List[ProvenanceChunk]:
        """Split cleaned text into ordered, hash-linked provenance chunks."""
        chain = ProvenanceChain(source_id=source_id, source_url=source_url)
        size = max(64, chunk_size)
        pieces = [cleaned_text[i : i + size] for i in range(0, len(cleaned_text), size)]
        if not pieces:  # always emit at least one (empty) chunk for provenance
            pieces = [""]
        return [chain.add_chunk(piece) for piece in pieces]

    def to_memory_metadata(self, result: IngestResult) -> Dict[str, Any]:
        """Build a ``MemoryStore.add_exchange``-compatible metadata dict.

        This is the Provenance Chain Fix at the integration boundary: the sca.json
        provenance hash + source id flow into sovereign memory so downstream systems
        (Gnosis Graph, Crisis Matrix) can verify attribution.

        Args:
            result: The ``IngestResult`` from :meth:`ingest_transcript`.

        Returns:
            A metadata dict carrying provenance fields plus chunk linkage.
        """
        return {
            "source_id": result.source_id,
            "source_type": result.attestation.source_type,
            "source_url": result.source_url,
            "provenance_hash": result.provenance_hash,
            "chunk_count": result.chunk_count,
            "sieve_metadata": result.attestation.sieve_metadata,
            "is_youtube_ingest": True,
        }
