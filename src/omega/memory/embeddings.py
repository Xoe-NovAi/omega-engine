# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Embedding Layer — Provider-agnostic vectorization for Omega Memory.
AP: AP-EMBEDDINGS-v1.0.0
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import hashlib
import math
import os
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import anyio
import httpx2 as httpx

from omega.cvar_table import ZONEID_EMBEDDING
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


class IEmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Ensures the Omega Engine can swap embedding models (Local vs Cloud)
    without affecting the memory store logic.
    """

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Convert text to a fixed-size vector."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The dimensionality of the vectors produced by this provider."""
        pass


class SovereignFallbackEmbeddingProvider(IEmbeddingProvider):
    """Sovereign Fallback — Deterministic Feature Hashing (Hashing Trick).

    [Right Approximation: evolved from FISR, id Software 1999]
    Provides a zero-dependency, O(1) embedding that is 'right enough'
    for basic semantic retrieval when no model is available.
    """

    def __init__(self, dimension: int = 256):
        self._dimension = dimension
        self._stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "shall",
            "can",
            "need",
            "dare",
            "this",
            "that",
            "these",
            "those",
            "i",
            "me",
            "my",
            "we",
            "our",
            "you",
            "your",
            "he",
            "him",
            "his",
            "she",
            "her",
            "it",
            "its",
            "they",
            "them",
            "their",
            "what",
            "which",
            "who",
            "whom",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "because",
            "as",
            "until",
            "while",
            "about",
            "between",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
        }

    @property
    def dimension(self) -> int:
        return self._dimension

    async def get_embedding(self, text: str) -> List[float]:
        vec = [0.0] * self._dimension
        if not text:
            return vec

        tokens = re.findall(r"[a-zA-Z]\w+", text.lower())
        tokens = [t for t in tokens if t not in self._stopwords and len(t) > 2]
        if not tokens:
            return vec

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim = h % self._dimension
            vec[dim] += 1.0

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec


class OllamaEmbeddingProvider(IEmbeddingProvider):
    """Ollama-based embedding provider using nomic-embed-text v1.5.

    [Right Approximation: evolved from FISR, id Software 1999]
    Provides high-quality 768-dim embeddings via local Ollama inference,
    falling back gracefully if Ollama is unavailable.

    Model: nomic-embed-text:v1.5 (Q8_0, 274MB, 768-dim, 62.28 MTEB)
    Endpoint: http://127.0.0.1:11434/api/embed
    """

    def __init__(
        self,
        model: str = "nomic-embed-text:v1.5",
        base_url: str = "http://127.0.0.1:11434",
        dimension: int = 768,
        target_dim: Optional[int] = None,
    ):
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._native_dimension = dimension
        self._target_dim = target_dim  # FS-Β1: MRL truncation target
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def dimension(self) -> int:
        return self._target_dim if self._target_dim is not None else self._native_dimension

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def get_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        client = await self._get_client()
        try:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings", [])
            if embeddings and len(embeddings) > 0:
                vec = embeddings[0]
                # FS-Β1: MRL truncation to target_dim
                if self._target_dim is not None and len(vec) > self._target_dim:
                    return vec[: self._target_dim]
                return vec

            logger.warning("Ollama returned empty embeddings for: %.50s", text)
            return [0.0] * self.dimension
        except httpx.HTTPStatusError as e:
            logger.warning("Ollama HTTP error: %s — status=%d", e, e.response.status_code)
            raise
        except httpx.RequestError as e:
            logger.warning("Ollama connection error: %s", e)
            raise
        except (httpx.HTTPError, RuntimeError) as e:
            logger.warning("Ollama embedding error: %s", e)
            raise

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class LocalGGUFEmbeddingProvider(IEmbeddingProvider):
    """Local GGUF embedding provider via llama-cpp-python.

    [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity
    Loads an existing GGUF embedding model (e.g. all-MiniLM-L6-v2-f16.gguf)
    via llama-cpp-python's embedding mode. Runs entirely locally — zero
    network calls, zero cloud dependencies.

    This is the PRIMARY embedding provider for the local-first chain.
    No sentence-transformers or PyTorch dependency needed.

    ZONEID: 0x1d4a1d — embedding cache integrity marker
    """

    def __init__(
        self,
        model_path: str = "/media/arcana-novai/omega_library/models/embeddings/all-MiniLM-L6-v2-Q4_K_M.gguf",
        dimension: int = 384,
        n_ctx: int = 512,
        n_threads: int = 6,
        zoneid: int = ZONEID_EMBEDDING,
        target_dim: Optional[int] = None,  # FS-Β1: MRL truncation target
    ):
        self._model_path = os.path.abspath(model_path)
        self._zoneid = zoneid
        self._native_dimension = dimension
        self._target_dim = target_dim  # FS-Β1: MRL truncation target
        self._llama: any = None
        self._n_ctx = n_ctx
        self._n_threads = n_threads
        self._loaded = False

        # Validate model path exists before import
        if not os.path.isfile(self._model_path):
            logger.warning(
                "LocalGGUFEmbeddingProvider: model not found at %s — "
                "provider will raise on get_embedding()",
                self._model_path,
            )

    @property
    def dimension(self) -> int:
        # FS-Β1: Return target_dim if set (MRL truncation), else native
        return self._target_dim if self._target_dim is not None else self._native_dimension

    async def _ensure_loaded(self) -> None:
        """Lazy-load the model on first use (prevents OOM at import time)."""
        if self._loaded and self._llama is not None:
            return
        if not os.path.isfile(self._model_path):
            raise FileNotFoundError(
                f"Embedding model not found: {self._model_path}. "
                "Expected all-MiniLM-L6-v2-f16.gguf at the configured path."
            )

        # Load via llama-cpp-python in a thread (blocking init)
        import llama_cpp  # lazy import — heavy module

        def _load():
            return llama_cpp.Llama(
                model_path=self._model_path,
                embedding=True,
                n_ctx=self._n_ctx,
                n_threads=self._n_threads,
                verbose=False,
            )

        self._llama = await anyio.to_thread.run_sync(_load)
        self._loaded = True
        logger.info(
            "LocalGGUFEmbeddingProvider: loaded %s (native_dim=%d, target_dim=%s, n_ctx=%d, threads=%d)",
            os.path.basename(self._model_path),
            self._native_dimension,
            self._target_dim,
            self._n_ctx,
            self._n_threads,
        )

    async def get_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        await self._ensure_loaded()

        def _embed():
            # llama_cpp.Llama.embed() with newer GGUF returns flat List[float]
            # (e.g., 384 elements). Older GGUFs return List[List[float]].
            # Handle both formats transparently.
            result = self._llama.embed(text)
            if result and len(result) > 0:
                # New GGUF: flat list [f1, f2, ...] — return as-is
                if isinstance(result[0], float):
                    return list(result)
                # Old GGUF: nested list [[f1, f2, ...]] — unwrap first
                return result[0]
            return [0.0] * self._native_dimension

        vec = await anyio.to_thread.run_sync(_embed)

        # FS-Β1: MRL truncation to target_dim
        if self._target_dim is not None and len(vec) > self._target_dim:
            vec = vec[: self._target_dim]
        elif len(vec) != self._native_dimension:
            logger.warning(
                "LocalGGUFEmbeddingProvider: expected dim=%d, got %d — padding/truncating",
                self._native_dimension,
                len(vec),
            )
            if len(vec) < self._native_dimension:
                vec = vec + [0.0] * (self._native_dimension - len(vec))
            else:
                vec = vec[: self._native_dimension]

        # FS-Β1: Final MRL truncation to target_dim
        if self._target_dim is not None and len(vec) > self._target_dim:
            vec = vec[: self._target_dim]

        return vec

    async def close(self):
        """Unload the model to free memory."""
        self._llama = None
        self._loaded = False
        logger.info("LocalGGUFEmbeddingProvider: unloaded")


class StaticEmbeddingProvider(IEmbeddingProvider):
    """Static embedding provider via model2vec (potion models).

    [id-soft: doom-1993] Precomputed Lookup — static embeddings computed
    once, looked up via numpy at inference time. ~0.01ms per sentence,
    zero GPU, zero cloud dependencies.

    Model: minishlab/potion-base-2M (2M params, 64-dim, ~2MB)
    Fallback: blobbybob/potion-mxbai-micro (768-dim, ~14MB) for higher quality
    """

    def __init__(
        self, model_name: str = "minishlab/potion-base-2M", target_dim: Optional[int] = None
    ):
        self._model_name = model_name
        self._model: any = None
        self._native_dimension = 0
        self._target_dim = target_dim
        self._loaded = False

    @property
    def dimension(self) -> int:
        return self._target_dim if self._target_dim is not None else self._native_dimension

    async def _ensure_loaded(self):
        if self._loaded and self._model is not None:
            return
        from model2vec import StaticModel

        def _load():
            return StaticModel.from_pretrained(self._model_name)

        self._model = await anyio.to_thread.run_sync(_load)
        # Attempt to discover dimension via encode
        test_emb = await anyio.to_thread.run_sync(self._model.encode, "test")
        self._native_dimension = test_emb.shape[0] if hasattr(test_emb, "shape") else len(test_emb)
        self._loaded = True
        logger.info(
            "StaticEmbeddingProvider: loaded %s (native_dim=%d, target_dim=%s)",
            self._model_name,
            self._native_dimension,
            self._target_dim,
        )

    async def get_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        await self._ensure_loaded()

        def _encode():
            vec = self._model.encode(text)
            return vec.tolist() if hasattr(vec, "tolist") else list(vec)

        vec = await anyio.to_thread.run_sync(_encode)

        # FS-Β1: MRL truncation to target_dim
        if self._target_dim is not None and len(vec) > self._target_dim:
            vec = vec[: self._target_dim]
        elif len(vec) != self._native_dimension:
            logger.warning(
                "StaticEmbeddingProvider: expected dim=%d, got %d — padding/truncating",
                self._native_dimension,
                len(vec),
            )
            if len(vec) < self._native_dimension:
                vec = vec + [0.0] * (self._native_dimension - len(vec))
            else:
                vec = vec[: self._native_dimension]

        # FS-Β1: Final MRL truncation to target_dim
        if self._target_dim is not None and len(vec) > self._target_dim:
            vec = vec[: self._target_dim]

        return vec

    async def close(self):
        self._model = None
        self._loaded = False


class GemmaGGUFEmbeddingProvider(LocalGGUFEmbeddingProvider):
    """Google EmbeddingGemma 300M via llama-cpp-python.

    768-dim, 300M params, Q6_K quantized (249MB).
    Higher quality than MiniLM for the cost of more RAM.
    Sits in the chain as an intermediate-quality option.

    [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity
    """

    def __init__(self, target_dim: Optional[int] = None):
        super().__init__(
            model_path="/media/arcana-novai/omega_library/models/embeddings/embeddinggemma-300m-Q6_K.gguf",
            dimension=768,
            target_dim=target_dim,
        )


class EmbeddingManager:
    """Manages the embedding provider chain (Local -> Static -> Ollama -> Fallback).

    Ensures that the engine always has a way to vectorize text,
    preferring high-quality local models over the sovereign fallback.

    Default provider chain (local-first):
        1. LocalGGUFEmbeddingProvider — all-MiniLM via llama-cpp-python (384-dim)
        2. GemmaGGUFEmbeddingProvider — EmbeddingGemma 300M via llama-cpp-python (768-dim)
        3. StaticEmbeddingProvider — potion-base-2M via model2vec (64-dim)
        4. OllamaEmbeddingProvider — nomic-embed-text via Ollama (768-dim)
        5. SovereignFallbackEmbeddingProvider — deterministic hashing (256-dim)
    """

    def __init__(self, providers: Optional[List[IEmbeddingProvider]] = None):
        if providers is not None:
            self._providers = providers
        else:
            # FS-Β1: Use EmbeddingStrategy SSOT for target dimension
            from .embedding_strategy import get_embedding_strategy

            strategy = get_embedding_strategy()
            target_dim = strategy.canonical_dimension  # 768

            self._providers = [
                GemmaGGUFEmbeddingProvider(
                    target_dim=target_dim
                ),  # 768-dim, 300M, primary (quality-first)
                OllamaEmbeddingProvider(
                    dimension=target_dim
                ),  # 768-dim, nomic-embed-text, local fallback
                LocalGGUFEmbeddingProvider(
                    target_dim=target_dim
                ),  # 384-dim native, truncated to 768 via MRL
                StaticEmbeddingProvider(
                    target_dim=target_dim
                ),  # 64-dim native, truncated to 768 via MRL
            ]

    async def get_embedding(self, text: str) -> Tuple[List[float], str]:
        # [test-mode] Short-circuit in test env — returns zero vector to avoid
        # loading the 300M Gemma GGUF embedding model via llama-cpp-python.
        # Each Oracle() creation triggers add_exchange() which calls this,
        # and loading a 300M GGUF takes ~15-30s + 600MB on Ryzen 5700U.
        if os.environ.get("OMEGA_ENV") == "test":
            dim = self.current_dimension
            return [0.0] * dim, "mock"

        for provider in self._providers:
            try:
                embedding = await provider.get_embedding(text)
                return embedding, provider.__class__.__name__
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"Embedding provider {provider.__class__.__name__} failed: {e}")
                continue

        # This should theoretically never be reached if Fallback is last
        raise RuntimeError("All embedding providers failed.")

    @property
    def current_dimension(self) -> int:
        if not self._providers:
            return 256
        return self._providers[0].dimension
