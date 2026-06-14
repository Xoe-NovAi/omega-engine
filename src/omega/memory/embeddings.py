"""Sovereign Embedding Layer — Provider-agnostic vectorization for Omega Memory.
AP: AP-EMBEDDINGS-v1.0.0
"""

import hashlib
import math
import re
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import anyio
import httpx

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
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "shall", "can", "need", "dare",
            "this", "that", "these", "those", "i", "me", "my", "we", "our", "you",
            "your", "he", "him", "his", "she", "her", "it", "its", "they", "them",
            "their", "what", "which", "who", "whom", "when", "where", "why", "how",
            "all", "each", "every", "both", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "because", "as", "until", "while", "about", "between",
            "through", "during", "before", "after", "above", "below", "up", "down",
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
    
    def __init__(self, model: str = "nomic-embed-text:v1.5", base_url: str = "http://127.0.0.1:11434", dimension: int = 768):
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._dimension = dimension
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def get_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dimension
        
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
                return embeddings[0]
            
            logger.warning("Ollama returned empty embeddings for: %.50s", text)
            return [0.0] * self._dimension
        except httpx.HTTPStatusError as e:
            logger.warning("Ollama HTTP error: %s — status=%d", e, e.response.status_code)
            raise
        except httpx.RequestError as e:
            logger.warning("Ollama connection error: %s", e)
            raise
        except Exception as e:
            logger.warning("Ollama embedding error: %s", e)
            raise
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class EmbeddingManager:
    """Manages the embedding provider chain (Local -> Fallback).
    
    Ensures that the engine always has a way to vectorize text,
    preferring high-quality local models over the sovereign fallback.
    """
    
    def __init__(self, providers: Optional[List[IEmbeddingProvider]] = None):
        self._providers = providers or [SovereignFallbackEmbeddingProvider()]
        
    async def get_embedding(self, text: str) -> List[float]:
        for provider in self._providers:
            try:
                return await provider.get_embedding(text)
            except Exception as e:
                logger.warning(f"Embedding provider {provider.__class__.__name__} failed: {e}")
                continue
        
        # This should theoretically never be reached if Fallback is last
        raise RuntimeError("All embedding providers failed.")

    @property
    def current_dimension(self) -> int:
        if not self._providers:
            return 256
        return self._providers[0].dimension
