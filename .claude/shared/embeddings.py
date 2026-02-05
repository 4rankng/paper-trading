#!/usr/bin/env python3
"""Embedding service using Ollama or GLM/Z.AI APIs."""

import os
import hashlib
import asyncio
from typing import List, Dict, Optional
from functools import lru_cache
import httpx

# Cache for embeddings to avoid re-computation
_embedding_cache: Dict[str, List[float]] = {}


class EmbeddingService:
    """Generate embeddings using Ollama (primary) or GLM/Z.AI (fallback)."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.provider = os.getenv("EMBEDDING_MODEL", "ollama").lower()
        self.timeout = 30.0

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        # Check cache
        cache_key = self._get_cache_key(text)
        if cache_key in _embedding_cache:
            return _embedding_cache[cache_key]

        # Generate embedding
        if self.provider == "ollama":
            embedding = self._embed_ollama(text)
        else:
            embedding = self._embed_glm(text)

        # Cache result
        _embedding_cache[cache_key] = embedding
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        # Filter out cached texts
        uncached_texts = []
        uncached_indices = []
        results = [None] * len(texts)

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in _embedding_cache:
                results[i] = _embedding_cache[cache_key]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Embed uncached texts
        if uncached_texts:
            if self.provider == "ollama":
                new_embeddings = self._embed_batch_ollama(uncached_texts)
            else:
                new_embeddings = [self._embed_glm(t) for t in uncached_texts]

            # Cache and place in results
            for idx, text, emb in zip(uncached_indices, uncached_texts, new_embeddings):
                cache_key = self._get_cache_key(text)
                _embedding_cache[cache_key] = emb
                results[idx] = emb

        return results

    def _embed_ollama(self, text: str) -> List[float]:
        """Generate embedding using Ollama API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])
        except Exception as e:
            print(f"Ollama embedding error: {e}")
            # Fallback to GLM if Ollama fails
            return self._embed_glm(text)

    def _embed_batch_ollama(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch using Ollama (sequential for now)."""
        # Ollama doesn't support batch embedding natively, so we do sequential
        embeddings = []
        for text in texts:
            emb = self._embed_ollama(text)
            embeddings.append(emb)
        return embeddings

    def _embed_glm(self, text: str) -> List[float]:
        """Generate embedding using GLM/Z.AI API as fallback.

        This is a placeholder - implement based on actual GLM/Z.AI API.
        For now, returns a dummy embedding.
        """
        # TODO: Implement actual GLM/Z.AI embedding API call
        # For now, return a small fixed embedding for testing
        import warnings
        warnings.warn("GLM embedding not implemented, using dummy embedding")
        return [0.0] * 384  # 384-dim dummy

    async def aembed_text(self, text: str) -> List[float]:
        """Async version of embed_text."""
        cache_key = self._get_cache_key(text)
        if cache_key in _embedding_cache:
            return _embedding_cache[cache_key]

        if self.provider == "ollama":
            embedding = await self._aembed_ollama(text)
        else:
            embedding = self._embed_glm(text)  # GLM doesn't have async

        _embedding_cache[cache_key] = embedding
        return embedding

    async def aembed_batch(self, texts: List[str]) -> List[List[float]]:
        """Async batch embedding."""
        uncached_texts = []
        uncached_indices = []
        results = [None] * len(texts)

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in _embedding_cache:
                results[i] = _embedding_cache[cache_key]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        if uncached_texts:
            if self.provider == "ollama":
                new_embeddings = await self._aembed_batch_ollama(uncached_texts)
            else:
                new_embeddings = [self._embed_glm(t) for t in uncached_texts]

            for idx, text, emb in zip(uncached_indices, uncached_texts, new_embeddings):
                cache_key = self._get_cache_key(text)
                _embedding_cache[cache_key] = emb
                results[idx] = emb

        return results

    async def _aembed_ollama(self, text: str) -> List[float]:
        """Async Ollama embedding."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])
        except Exception as e:
            print(f"Async Ollama embedding error: {e}")
            return self._embed_glm(text)

    async def _aembed_batch_ollama(self, texts: List[str]) -> List[List[float]]:
        """Async batch embedding for Ollama."""
        tasks = [self._aembed_ollama(text) for text in texts]
        return await asyncio.gather(*tasks)

    def get_embedding_model(self) -> str:
        """Return active model name."""
        if self.provider == "ollama":
            return f"ollama:{self.model}"
        return "glm:unknown"


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance."""
    return EmbeddingService()


# Convenience functions
def embed_text(text: str) -> List[float]:
    """Generate embedding for text using default service."""
    return get_embedding_service().embed_text(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    return get_embedding_service().embed_batch(texts)


def get_embedding_model() -> str:
    """Get active embedding model name."""
    return get_embedding_service().get_embedding_model()
