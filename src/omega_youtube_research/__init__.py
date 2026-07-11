# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# Public API surface for the YouTube Research Module.
#
# Heritage:
#   No id Software heritage tags — original Omega architecture (Sieve-and-Sign protocol).

"""YouTube Research Module (P0) — public API.

Sovereign, local-first YouTube transcript ingestion and provenance tracking.
Components:
  * SovereignSieve      — search filtering + transcript cleaning
  * SovereignSigner     — HMAC-SHA256 sca.json attestation + JWT envelope
  * AtomicPersistence   — WAL SQLite + atomic JSON renames
  * ProvenanceChain     — cryptographic linkage between extracted chunks
  * YouTubeResearchModule — P0 orchestrator (Sieve -> Sign -> Chain -> Persist)
"""

from .config import (
    EmbeddingConfig,
    PersistenceConfig,
    SieveConfig,
    SignerConfig,
    YouTubeResearchConfig,
)
from .errors import (
    PersistenceError,
    ProvenanceIntegrityError,
    SigningError,
    SieveError,
    YouTubeAPIError,
    YouTubeAuthError,
    YouTubeResearchError,
)
from .module import IngestResult, YouTubeResearchModule
from .persistence import AtomicPersistence, ProvenanceChunkRecord
from .provenance import ProvenanceChain, ProvenanceChunk
from .signer import SourceChainAttestation, SovereignSigner
from .sieve import SieveMetadata, SieveResult, SovereignSieve, YouTubeVideo

__all__ = [
    "YouTubeResearchConfig",
    "SieveConfig",
    "SignerConfig",
    "PersistenceConfig",
    "EmbeddingConfig",
    "YouTubeResearchError",
    "YouTubeAuthError",
    "YouTubeAPIError",
    "SigningError",
    "ProvenanceIntegrityError",
    "PersistenceError",
    "SieveError",
    "SovereignSieve",
    "YouTubeVideo",
    "SieveMetadata",
    "SieveResult",
    "SovereignSigner",
    "SourceChainAttestation",
    "AtomicPersistence",
    "ProvenanceChunkRecord",
    "ProvenanceChain",
    "ProvenanceChunk",
    "YouTubeResearchModule",
    "IngestResult",
]
