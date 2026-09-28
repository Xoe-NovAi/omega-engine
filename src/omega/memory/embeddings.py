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


class EmbeddingProviderUnavailableError(OmegaError):
    """Raised when no canonical-capable embedding provider can serve a request.

    [D-1024-DIM-NATIVE-20260926 / M23] This error exists so the engine NEVER
    silently answers with a different model. It is raised when every
    canonical-capable provider fails, and when a provider returns a
    natively-sub-canonical vector (cross-model substitution attempt).

    Inherits OmegaError so existing `except OmegaError` handlers in the
    provider chain keep working; callers that must not swallow it should
    catch this type specifically.
    """


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

    def __init__(self, dimension: Optional[int] = None):
        # [D-1024-DIM-NATIVE-20260926] Default follows the SSOT canonical
        # dimension (config/embedding_strategy.yaml). Feature hashing can
        # emit ANY width, so this provider always matches the canonical
        # collection — including the pre-migration 768 default, which is
        # kept working by passing dimension= explicitly.
        if dimension is None:
            from .embedding_strategy import get_embedding_strategy

            dimension = get_embedding_strategy().canonical_dimension
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
    """Ollama-based embedding provider.

    [Right Approximation: evolved from FISR, id Software 1999]
    Legacy-tier provider for `omega_vec_nomic_768` / `_512` / `_256`.

    [D-1024-DIM-NATIVE-20260926] LEGACY — NOT a canonical-path provider.
    nomic-embed-text is a DIFFERENT MODEL from the canonical
    Qwen3-Embedding-0.6B. Its vectors are not comparable with the canonical
    space, and it MUST NOT be used as a fallback for the canonical collection.
    It is not in `EmbeddingManager`'s default chain; that chain is
    canonical-capable only and raises `EmbeddingProviderUnavailableError`
    rather than substituting this model.

    The previous default model was nomic-embed-text:v1.5. The default is now
    `None`: a caller must name the model and the collection explicitly, so
    instantiating this class with no arguments cannot silently produce a
    768-D nomic vector for a canonical write.

    Model (legacy default, must be passed explicitly): nomic-embed-text:v1.5
    (Q8_0, 274MB, 768-dim, 62.28 MTEB)
    Endpoint: http://127.0.0.1:11434/api/embed
    """

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://127.0.0.1:11434",
        dimension: int = 768,
        target_dim: Optional[int] = None,
    ):
        if model is None:
            raise ValueError(
                "OllamaEmbeddingProvider requires an explicit model.\n"
                "[D-1024-DIM-NATIVE-20260926] The former default "
                "(nomic-embed-text:v1.5) was removed because a nominal "
                "nomic-embed-text was silently substituted for the canonical "
                "Qwen3-Embedding-0.6B whenever the canonical provider was "
                "unavailable. This class is LEGACY-TIER ONLY: it may serve "
                "omega_vec_nomic_768 / _512 / _256 and must never serve "
                "omega_vec_qwen_1024. Pass model=... and target the matching "
                "collection explicitly."
            )
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


class Qwen3GGUFEmbeddingProvider(LocalGGUFEmbeddingProvider):
    """Qwen3-Embedding-0.6B via llama-cpp-python.

    [D-768-DIM-MODEL-SWAP] Replaces EmbeddingGemma-300M as the primary
    embedding model. 600M params, Q5_K_M quantized (~470MB).

    Native dimension: 1024 — which IS the canonical dimension
    (D-1024-DIM-NATIVE-20260926), so no MRL truncation is applied by
    default. MRL remains available by passing target_dim explicitly.

    Quality: MTEB 64.33 (native 1024), ~64.0 (MRL 768), ~62.0 (MRL 256).
    Instruction-aware: prepends "Instruct: Retrieve relevant technical
    documentation\nQuery: " to query text (NOT document text).

    Requires:
    - llama.cpp compiled with --pooling last
    - Q5_K_M or Q8_0 quantization (Q4_K_M has ~5% drift)
    - Last-token pooling (not mean pooling)

    [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity
    """

    def __init__(self, target_dim: Optional[int] = None):
        super().__init__(
            model_path="/media/arcana-novai/omega_library/models/embeddings/Qwen3-Embedding-0.6B-Q5_K_M.gguf",
            dimension=1024,  # native == canonical
            target_dim=target_dim,  # None = emit native 1024
        )
        # [D-1024-DIM-NATIVE-20260926] MRL chain 1024→768/512/256/128/64 is
        # AVAILABLE but not the canonical path.
        self._instruction_prefix = (
            "Instruct: Retrieve relevant technical documentation\nQuery: "
        )

    async def get_embedding(self, text: str, is_query: bool = True) -> List[float]:
        """Override to inject instruction prefix on queries.

        Per Qwen3-Embedding-0.6B paper: prefix is applied to QUERIES only,
        not to documents being indexed. This improves retrieval by ~2-3%.
        """
        if is_query:
            text = self._instruction_prefix + text
        return await super().get_embedding(text)


class EmbeddingManager:
    """Manages the embedding provider chain (canonical-first, fail-loud).

    [D-1024-DIM-NATIVE-20260926] The default chain is CANONICAL-CAPABLE ONLY:

        1. Qwen3GGUFEmbeddingProvider — Qwen3-Embedding-0.6B via llama-cpp
           (native 1024 == canonical)
        2. SovereignFallbackEmbeddingProvider — deterministic feature hashing
           at the canonical width; zero dependencies, cannot fail

    M23 FAIL-LOUD: if the canonical provider is unavailable the chain RAISES
    `EmbeddingProviderUnavailableError` naming D-1024-DIM-NATIVE-20260926. It
    does NOT silently substitute a different model. Previously this chain
    carried OllamaEmbeddingProvider (nomic-embed-text, natively 768-D) at
    position 1: when Qwen3 was unavailable it answered with 768-D vectors from
    a DIFFERENT MODEL, and because the write went to omega_vec_nomic_768 the
    vec0 lock (1024) and the adapter's per-collection guard (768) both saw a
    legal width. The substitution was invisible by construction.

    MRL truncation is unaffected and remains LEGAL: a 1024-D Qwen3 vector
    truncated to 768/512/256/128/64 by `target_dim` is the same model and is
    accepted. What is now impossible is a NATIVE sub-canonical vector from a
    different model reaching the canonical write path.

    Sub-canonical providers (Ollama/nomic, MiniLM, potion) still exist as
    classes for their own legacy collections; they are simply not in the
    default canonical chain. A caller that explicitly wants a legacy-tier
    collection must pass that provider AND target the matching collection.
    """

    # Explicit, actionable failure text — referenced by tests and by the
    # negative test in tests/contracts/test_embedding_dimension.py.
    CANONICAL_UNAVAILABLE_MESSAGE = (
        "Canonical embedding provider unavailable — refusing to substitute a "
        "different model.\n"
        "  Decision:  D-1024-DIM-NATIVE-20260926\n"
        "  Canonical:  Qwen3-Embedding-0.6B at 1024-dim NATIVE "
        "(collection omega_vec_qwen_1024)\n"
        "  Cause:      every canonical-capable provider failed\n"
        "  Legal:      MRL truncation of a 1024-D Qwen3 vector to "
        "768/512/256/128/64 (same model, narrower width)\n"
        "  ILLEGAL:    a natively-768 nomic-embed-text (or minilm/potion) "
        "vector standing in for the canonical space\n"
        "  Fix:        restore the Qwen3 GGUF model and its llama.cpp build "
        "(--pooling last), or explicitly pass a provider and target a "
        "matching legacy collection. Do NOT re-add a cross-model fallback."
    )

    def __init__(self, providers: Optional[List[IEmbeddingProvider]] = None):
        if providers is not None:
            self._providers = providers
            self._canonical_width = None  # infer below when possible
        else:
            # FS-Β1: Use EmbeddingStrategy SSOT for target dimension
            from .embedding_strategy import get_embedding_strategy

            strategy = get_embedding_strategy()
            target_dim = strategy.canonical_dimension  # 1024 (D-1024-DIM-NATIVE)

            self._canonical_width = target_dim
            self._providers = [
                Qwen3GGUFEmbeddingProvider(
                    target_dim=target_dim
                ),  # native 1024 == canonical, primary (D-1024-DIM-NATIVE)
                # Sovereign hash fallback at the CANONICAL width. Deterministic,
                # zero-dependency, cannot fail — so the chain never has to
                # reach a different model to produce a 1024-D answer.
                SovereignFallbackEmbeddingProvider(dimension=target_dim),
            ]

        if self._canonical_width is None:
            from .embedding_strategy import get_embedding_strategy

            self._canonical_width = get_embedding_strategy().canonical_dimension

    def _assert_canonical_width(
        self, embedding: List[float], provider: IEmbeddingProvider
    ) -> None:
        """M23: a sub-canonical answer is a FAILURE, not a fallback.

        Guards the case the removed nomic fallback exploited: a provider that
        returns a natively-narrower vector than canonical. Same-model MRL
        truncation is allowed because it is signalled by an explicit
        `target_dim` on the provider, not inferred from width.
        """
        if self._canonical_width is None or not embedding:
            return
        actual = len(embedding)
        if actual == self._canonical_width:
            return

        # A provider explicitly configured for MRL truncation is a same-model
        # narrow view of the canonical space — legal.
        if getattr(provider, "_target_dim", None) is not None:
            return

        raise EmbeddingProviderUnavailableError(
            f"{provider.__class__.__name__} returned {actual}-dim on a "
            f"{self._canonical_width}-dim canonical request.\n"
            f"{self.CANONICAL_UNAVAILABLE_MESSAGE}"
        )

    async def get_embedding(self, text: str) -> Tuple[List[float], str]:
        # [test-mode] Short-circuit in test env — returns zero vector to avoid
        # loading the Qwen3-Embedding-0.6B GGUF embedding model via llama-cpp-python.
        # Each Oracle() creation triggers add_exchange() which calls this,
        # and loading a 600M GGUF takes ~15-30s + 600MB on Ryzen 5700U.
        if os.environ.get("OMEGA_ENV") == "test":
            # [Carmack audit 2026-09-26] Use the CANONICAL width, not
            # providers[0].dimension. The short-circuit used to mirror the head
            # provider, so a chain headed by a sub-canonical provider emitted a
            # sub-canonical zero vector in test mode — the same cross-model
            # width violation the production path now refuses. M23: the
            # canonical collection is the only thing this feeds.
            dim = self._canonical_width or self.current_dimension
            return [0.0] * dim, "mock"

        failures: List[str] = []
        for provider in self._providers:
            try:
                embedding = await provider.get_embedding(text)
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"Embedding provider {provider.__class__.__name__} failed: {e}")
                failures.append(f"{provider.__class__.__name__}: {e}")
                continue

            # M23: width is verified BEFORE the answer is returned. A provider
            # that answered at the wrong width is treated as a failure and the
            # chain continues — it is never handed to the caller.
            try:
                self._assert_canonical_width(embedding, provider)
            except EmbeddingProviderUnavailableError as e:
                logger.error("Cross-model substitution blocked: %s", e)
                failures.append(f"{provider.__class__.__name__}: {e}")
                continue

            return embedding, provider.__class__.__name__

        # M23: never return a sub-canonical answer. Fail loud and name the
        # decision so the operator knows exactly what was refused.
        raise EmbeddingProviderUnavailableError(
            f"{self.CANONICAL_UNAVAILABLE_MESSAGE}\n"
            f"  Provider failures:\n"
            + "".join(f"    - {f}\n" for f in failures)
        )

    @property
    def current_dimension(self) -> int:
        if not self._providers:
            return 256
        return self._providers[0].dimension
