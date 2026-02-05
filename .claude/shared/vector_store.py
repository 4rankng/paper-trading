#!/usr/bin/env python3
"""Vector store manager using ChromaDB for semantic search."""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings

from embeddings import get_embedding_service


class VectorStore:
    """Manage ChromaDB vector database for RAG system."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize ChromaDB client.

        Args:
            persist_directory: Directory for persistent storage. Default: filedb/vectordb
        """
        if persist_directory is None:
            persist_directory = os.getenv(
                "VECTOR_DB_PATH", "./filedb/vectordb"
            )

        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        self.embedding_service = get_embedding_service()

        # Collection names
        self.COLLECTIONS = ["news", "web_searches", "analytics"]

    def _get_collection(self, name: str):
        """Get or create collection.

        Args:
            name: Collection name (news, web_searches, analytics)

        Returns:
            ChromaDB collection object
        """
        if name not in self.COLLECTIONS:
            raise ValueError(f"Invalid collection: {name}")

        return self.client.get_or_create_collection(
            name=name,
            metadata={"description": f"{name} documents"},
        )

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
        collection: str = "analytics",
    ) -> None:
        """Add a single document to the vector store.

        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: Document metadata (ticker, date, source, url, etc.)
            collection: Collection name
        """
        col = self._get_collection(collection)

        # Generate embedding
        embedding = self.embedding_service.embed_text(text)

        # Add to collection
        col.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    def add_documents_batch(
        self,
        docs: List[Dict[str, Any]],
        collection: str = "analytics",
    ) -> None:
        """Add multiple documents to the vector store.

        Args:
            docs: List of dicts with keys: id, text, metadata
            collection: Collection name
        """
        if not docs:
            return

        col = self._get_collection(collection)

        # Extract data
        ids = [doc["id"] for doc in docs]
        texts = [doc["text"] for doc in docs]
        metadatas = [doc.get("metadata", {}) for doc in docs]

        # Generate embeddings in batch
        embeddings = self.embedding_service.embed_batch(texts)

        # Add to collection
        col.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        collection: str = "analytics",
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.

        Args:
            query: Search query text
            collection: Collection name or 'all' to search all collections
            n_results: Number of results to return
            where: Metadata filter (e.g., {"ticker": "AAPL"})
            where_document: Document content filter

        Returns:
            List of results with keys: id, text, metadata, score
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)

        if collection == "all":
            # Search all collections and merge results
            results = []
            for col_name in self.COLLECTIONS:
                col = self._get_collection(col_name)
                col_results = col.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where,
                    where_document=where_document,
                )
                # Add collection name to results
                for i, doc_id in enumerate(col_results["ids"][0]):
                    results.append({
                        "id": doc_id,
                        "text": col_results["documents"][0][i],
                        "metadata": col_results["metadatas"][0][i],
                        "score": 1.0 - col_results["distances"][0][i],  # Convert to similarity
                        "collection": col_name,
                    })
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:n_results]
        else:
            # Search specific collection
            col = self._get_collection(collection)
            col_results = col.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
            )

            results = []
            for i, doc_id in enumerate(col_results["ids"][0]):
                results.append({
                    "id": doc_id,
                    "text": col_results["documents"][0][i],
                    "metadata": col_results["metadatas"][0][i],
                    "score": 1.0 - col_results["distances"][0][i],  # Convert to similarity
                    "collection": collection,
                })

            return results

    def delete_document(
        self,
        doc_id: str,
        collection: str = "analytics",
    ) -> None:
        """Delete a document from the vector store.

        Args:
            doc_id: Document ID to delete
            collection: Collection name
        """
        col = self._get_collection(collection)
        col.delete(ids=[doc_id])

    def delete_documents_batch(
        self,
        doc_ids: List[str],
        collection: str = "analytics",
    ) -> None:
        """Delete multiple documents.

        Args:
            doc_ids: List of document IDs to delete
            collection: Collection name
        """
        col = self._get_collection(collection)
        col.delete(ids=doc_ids)

    def get_collection_stats(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about collections.

        Args:
            collection: Specific collection name, or None for all collections

        Returns:
            Dict with collection names and document counts
        """
        if collection:
            col = self._get_collection(collection)
            count = col.count()
            return {collection: count}
        else:
            stats = {}
            for col_name in self.COLLECTIONS:
                col = self._get_collection(col_name)
                stats[col_name] = col.count()
            return stats

    def reset_collection(self, collection: str) -> None:
        """Delete all documents in a collection.

        Args:
            collection: Collection name to reset
        """
        if collection in self.COLLECTIONS:
            self.client.delete_collection(name=collection)
            self._get_collection(collection)  # Recreate

    def reset_all(self) -> None:
        """Delete all collections and recreate them."""
        for col_name in self.COLLECTIONS:
            self.client.delete_collection(name=col_name)
            self._get_collection(col_name)  # Recreate


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get singleton vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
