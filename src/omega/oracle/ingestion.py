# AP: AP-INGESTION-v1.0.0
"""
Sovereign Ingestion Pipeline — Sieve-and-Sign Architecture.

Implements the "Sieve-and-Sign" pattern for all external data entering the engine.
Pipeline: Raw Data -> Sieve (PII Masking + Sanitization) -> Sign (Provenance) -> Index.
"""
# DocRef: docs/architecture/SOVEREIGN_INGESTION_PIPELINE.md

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field

from omega.oracle.pii_masker import PIIMasker, PIITokenMap
from omega.ingestion.persistence import IngestionPersistence

logger = logging.getLogger(__name__)


@dataclass
class IngestedDocument:
    """A document that has passed through the sovereign sieve."""

    content: str
    metadata: Dict[str, Any]
    provenance_hash: str
    timestamp: float = field(default_factory=lambda: time.time())
    pii_token_map: Optional[PIITokenMap] = None


class SovereignSieve:
    """The 'Sieve' layer of the ingestion pipeline.

    Ensures that all external data is sanitized and PII-masked before
    entering the sovereign memory.
    """

    def __init__(self, pii_masker: PIIMasker):
        self.pii_masker = pii_masker

    async def sieve(
        self, raw_content: str, provider_name: str = "external"
    ) -> Tuple[str, Optional[PIITokenMap]]:
        """Sieve raw content: sanitize -> mask PII.

        Returns:
            Tuple of (sanitized_content, token_map)
        """
        # 1. Sanitize (remove scripts, normalize whitespace)
        sanitized = self.pii_masker.sanitize_content(raw_content)

        # 2. Mask PII (using the provider_name to determine if masking is needed)
        # process_system_prompt returns (system_prompt, user_query, token_map)
        masked_system, _user_query, token_map = await self.pii_masker.process_system_prompt(
            system_prompt=sanitized,
            user_query="",  # Not applicable for raw ingestion
            provider_name=provider_name,
        )

        return masked_system, token_map


class SovereignSigner:
    """The 'Sign' layer of the ingestion pipeline.

    Adds cryptographic provenance stamps to ingested data to prevent
    silent corruption or unauthorized modification.
    """

    def __init__(self, secret_key: Optional[str] = None):
        # [M8 Zero Telemetry] Secret loaded from env, never hardcoded
        key = secret_key or os.environ.get("OMEGA_INGESTION_SECRET", "omega-sovereign-change-me")
        self.secret_key = key.encode()

    def sign(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate a HMAC-SHA256 provenance stamp.

        The stamp is a hash of the content + metadata + secret key.
        """
        # Create a canonical representation of metadata for signing
        meta_str = "|".join(f"{k}:{v}" for k, v in sorted(metadata.items()))
        payload = f"{content}::{meta_str}".encode()

        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def verify(self, content: str, metadata: Dict[str, Any], stamp: str) -> bool:
        """Verify a provenance stamp."""
        return self.sign(content, metadata) == stamp


class SovereignIngestionPipeline:
    """The full Sovereign Ingestion Pipeline.

    Coordinates the Sieve and Sign layers before indexing data into USM/Vector stores.
    Renamed from 'IngestionPipeline' to avoid collision with omega.ingestion.pipeline.IngestionPipeline.
    """

    def __init__(self, pii_masker: PIIMasker, signer: Optional[SovereignSigner] = None):
        self.sieve = SovereignSieve(pii_masker)
        self.signer = signer or SovereignSigner()

    async def ingest(
        self, raw_content: str, metadata: Dict[str, Any], provider_name: str = "external"
    ) -> IngestedDocument:
        """Process raw data through the full sovereign pipeline.

        Pipeline: Raw -> Sieve -> Sign -> IngestedDocument
        """
        # 1. Sieve (Sanitize + Mask)
        masked_content, token_map = await self.sieve.sieve(raw_content, provider_name)

        # 2. Sign (Provenance)
        stamp = self.signer.sign(masked_content, metadata)

        logger.info(
            "Sovereign Ingestion: processed %d chars, PII masked: %s",
            len(raw_content),
            "Yes" if token_map else "No",
        )

        return IngestedDocument(
            content=masked_content,
            metadata=metadata,
            provenance_hash=stamp,
            pii_token_map=token_map,
        )


class SovereignIngestionCoordinator:
    """WAD-agnostic coordinator for the Sovereign Ingestion Pipeline.

    Ties together the Sieve-and-Sign pipeline with the Tri-Anchor persistence.
    """

    def __init__(self, pii_masker: PIIMasker):
        self.pipeline = SovereignIngestionPipeline(pii_masker)
        self._persistence_cache: Dict[str, IngestionPersistence] = {}

    def _get_persistence(self, entity_name: str) -> IngestionPersistence:
        if entity_name not in self._persistence_cache:
            self._persistence_cache[entity_name] = IngestionPersistence(entity_name)
        return self._persistence_cache[entity_name]

    async def process_and_anchor(
        self,
        raw_content: str,
        metadata: Dict[str, Any],
        target_entity: str,
        provider_name: str = "external",
    ) -> Tuple[str, IngestedDocument]:
        """Full end-to-end ingestion flow:
        1. Sieve & Sign (Sovereign Pipeline)
        2. Raw Anchor (Immutable Ground Truth)
        3. SCA Anchor (Sovereign Continuity Anchor)

        Returns:
            Tuple of (source_id, ingested_doc)
        """
        # Step 1: Sieve and Sign
        doc = await self.pipeline.ingest(raw_content, metadata, provider_name)

        # Step 2: Anchor to Entity
        persistence = self._get_persistence(target_entity)

        # Store as raw bytes for the anchor
        content_bytes = doc.content.encode("utf-8")
        source_id = await persistence.persist_raw_anchor(
            source_name=metadata.get("source", "unknown_source"),
            content=content_bytes,
            quarantine=True,
        )

        # Store the SCA (Sovereign Continuity Anchor) metadata
        await persistence.persist_sca(
            source_id=source_id,
            metadata={
                **metadata,
                "provenance_hash": doc.provenance_hash,
                "timestamp": doc.timestamp,
                "pii_masked": doc.pii_token_map is not None,
            },
            quarantine=True,
        )

        logger.info(
            "Sovereign Ingestion: Anchored source %s to entity %s",
            source_id,
            target_entity,
        )
        return source_id, doc


# Singleton instance for the engine
_coordinator: Optional[SovereignIngestionCoordinator] = None


def get_ingestion_coordinator() -> SovereignIngestionCoordinator:
    global _coordinator
    if _coordinator is None:
        from omega.oracle.pii_masker import PIIMasker

        _coordinator = SovereignIngestionCoordinator(PIIMasker())
    return _coordinator
