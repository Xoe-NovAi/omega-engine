# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# External YAML configuration for the YouTube Research Module.
# Mandate 16 (Portability): no hardcoded paths — every path is resolved from
# configuration or an environment override (OMEGA_CONFIG_DIR).

"""Configuration contracts for the YouTube Research Module.

All configuration is loaded from an external YAML file (``config/youtube_research.yaml``
by default). Paths are never hardcoded in source — they are resolved at load time and
may be overridden via the ``OMEGA_CONFIG_DIR`` environment variable.
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from .errors import YouTubeResearchError


class SieveConfig(BaseModel):
    """Configuration for the SovereignSieve cleaning engine."""

    preserve_hesitations: bool = True
    remove_timestamps: bool = True
    remove_speaker_labels: bool = True
    url_replacement: str = "[URL]"
    # Relevance gate: a search hit is kept only if at least one query token
    # (length >= min_token_len) appears in its title or description.
    min_token_len: int = 3


class SignerConfig(BaseModel):
    """Configuration for the SovereignSigner attestation engine."""

    key_path: str = "config/keys/youtube_research.key"
    key_id: str = "omega-youtube-research-key-2026"
    algorithm: str = "HMAC-SHA256"
    signer: str = "omega-youtube-research/v1.0"


class PersistenceConfig(BaseModel):
    """Configuration for AtomicPersistence (WAL SQLite + atomic JSON renames)."""

    atomic_writes: bool = True
    tmp_suffix: str = ".tmp"
    db_path: str = "data/youtube_research/provenance.db"
    # Chunk size (characters) used when splitting a transcript into provenance chunks.
    chunk_size: int = 2000


class EmbeddingConfig(BaseModel):
    """Configuration for embedding backends (used by N1/N2, declared here for P0)."""

    qwen_model: str = "Qwen3-Embedding-0.6B"
    mrl_dimension: int = 768
    greek_bert_model: str = "ancient-greek-BERT"
    greek_bert_dim: int = 768


class YouTubeResearchConfig(BaseModel):
    """Top-level configuration for the YouTube Research Module."""

    sieve: SieveConfig = Field(default_factory=SieveConfig)
    signer: SignerConfig = Field(default_factory=SignerConfig)
    persistence: PersistenceConfig = Field(default_factory=PersistenceConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "YouTubeResearchConfig":
        """Load configuration from an external YAML file.

        Args:
            path: Explicit path to the YAML config. If ``None``, resolves
                ``$OMEGA_CONFIG_DIR/youtube_research.yaml`` (defaulting to
                ``config/youtube_research.yaml`` relative to the current working
                directory). Never raises on a missing file — returns defaults so
                the module remains usable in minimal/test environments.

        Returns:
            A validated ``YouTubeResearchConfig`` instance.

        Raises:
            YouTubeResearchError: If the file exists but cannot be parsed as YAML.
        """
        if path is None:
            base = Path(os.environ.get("OMEGA_CONFIG_DIR", "config"))
            path = base / "youtube_research.yaml"
        if not path.exists():
            return cls()
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - defensive
            raise YouTubeResearchError(
                f"Failed to parse YouTube Research config at {path}: {exc}"
            ) from exc
        return cls(**data)
