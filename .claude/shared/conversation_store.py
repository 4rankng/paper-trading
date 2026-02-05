#!/usr/bin/env python3
"""Conversation-specific vector store with semantic search and time decay."""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

try:
    from .vector_store import VectorStore, get_vector_store
except ImportError:
    from vector_store import VectorStore, get_vector_store


class ConversationStore(VectorStore):
    """Manage conversation history with semantic search and time-based relevance."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize conversation store.

        Args:
            persist_directory: Directory for persistent storage
        """
        super().__init__(persist_directory)

        # Add conversations to supported collections
        if "conversations" not in self.COLLECTIONS:
            self.COLLECTIONS.append("conversations")

        # Time decay parameters
        self.TIME_DECAY_HALFLIFE_HOURS = 24  # 50% weight after 24 hours
        self.MAX_SESSION_AGE_DAYS = 30  # Don't search sessions older than this

    def add_conversation(
        self,
        session_id: str,
        role: str,
        content: str,
        timestamp: str,
        message_id: str,
    ) -> None:
        """Add a conversation message to the vector store.

        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
            timestamp: ISO timestamp string
            message_id: Unique message identifier
        """
        metadata = {
            "session_id": session_id,
            "role": role,
            "timestamp": timestamp,
            "message_type": "conversation",
        }

        self.add_document(
            doc_id=message_id,
            text=content,
            metadata=metadata,
            collection="conversations",
        )

    def add_conversations_batch(
        self,
        messages: List[Dict[str, Any]],
    ) -> None:
        """Add multiple conversation messages efficiently.

        Args:
            messages: List of dicts with keys: session_id, role, content, timestamp, id
        """
        if not messages:
            return

        docs = [
            {
                "id": msg["id"],
                "text": msg["content"],
                "metadata": {
                    "session_id": msg["session_id"],
                    "role": msg["role"],
                    "timestamp": msg["timestamp"],
                    "message_type": "conversation",
                },
            }
            for msg in messages
        ]

        self.add_documents_batch(docs, collection="conversations")

    def search_conversations(
        self,
        query: str,
        session_id: str,
        n_results: int = 5,
        time_decay: bool = True,
        recency_boost: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Search conversations with semantic similarity and optional time decay.

        Args:
            query: Search query
            session_id: Session to search within
            n_results: Number of results to return
            time_decay: Apply time-based relevance decay
            recency_boost: Boost factor for recent messages (0.0-1.0)

        Returns:
            List of results with keys: id, text, metadata, score, time_decayed_score
        """
        # Search with session filter
        results = self.search(
            query=query,
            collection="conversations",
            n_results=n_results * 2,  # Get more for reranking
            where={"session_id": session_id},
        )

        # Filter out messages older than MAX_SESSION_AGE_DAYS
        cutoff_time = datetime.now() - timedelta(days=self.MAX_SESSION_AGE_DAYS)
        filtered_results = []

        for result in results:
            try:
                msg_time = datetime.fromisoformat(result["metadata"]["timestamp"])
                if msg_time > cutoff_time:
                    filtered_results.append(result)
            except (KeyError, ValueError):
                # Include if timestamp parsing fails
                filtered_results.append(result)

        # Apply time decay if requested
        if time_decay and filtered_results:
            filtered_results = self._apply_time_decay(
                filtered_results, recency_boost=recency_boost
            )

        # Sort by time-decayed score and return top N
        filtered_results.sort(key=lambda x: x.get("time_decayed_score", x["score"]), reverse=True)
        return filtered_results[:n_results]

    def get_recent_messages(
        self,
        session_id: str,
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get most recent messages from a session (no semantic search).

        Args:
            session_id: Session identifier
            n_results: Number of recent messages to return

        Returns:
            List of messages ordered by timestamp (newest first)
        """
        col = self._get_collection("conversations")

        # Get all messages for session
        try:
            results = col.get(
                where={"session_id": session_id},
                include=["documents", "metadatas"],
            )

            messages = []
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                try:
                    msg_time = datetime.fromisoformat(metadata["timestamp"])
                    messages.append({
                        "id": doc_id,
                        "text": results["documents"][i],
                        "metadata": metadata,
                        "timestamp": msg_time,
                    })
                except (KeyError, ValueError):
                    # Skip if timestamp parsing fails
                    continue

            # Sort by timestamp descending
            messages.sort(key=lambda x: x["timestamp"], reverse=True)
            return messages[:n_results]

        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []

    def get_session_summary(self, session_id: str) -> Optional[str]:
        """Get session summary if it exists.

        Args:
            session_id: Session identifier

        Returns:
            Summary text or None
        """
        col = self._get_collection("conversations")

        try:
            results = col.get(
                ids=[f"{session_id}_summary"],
                include=["documents"],
            )

            if results["ids"]:
                return results["documents"][0]
        except Exception:
            pass

        return None

    def save_session_summary(self, session_id: str, summary: str) -> None:
        """Save a session summary to the vector store.

        Args:
            session_id: Session identifier
            summary: Summary text
        """
        metadata = {
            "session_id": session_id,
            "type": "session_summary",
            "timestamp": datetime.now().isoformat(),
            "message_type": "summary",
        }

        self.add_document(
            doc_id=f"{session_id}_summary",
            text=summary,
            metadata=metadata,
            collection="conversations",
        )

    def delete_session(self, session_id: str) -> None:
        """Delete all messages for a session.

        Args:
            session_id: Session identifier
        """
        col = self._get_collection("conversations")

        try:
            # Get all message IDs for session
            results = col.get(
                where={"session_id": session_id},
                include=["documents"],
            )

            if results["ids"]:
                self.delete_documents_batch(results["ids"], collection="conversations")
        except Exception as e:
            print(f"Error deleting session: {e}")

    def _apply_time_decay(
        self,
        results: List[Dict[str, Any]],
        recency_boost: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Apply time-based decay to relevance scores.

        Recent messages get boosted, older messages get penalized.
        Uses exponential decay: decay_factor = exp(-hours_ago / half_life)

        Args:
            results: List of search results with scores
            recency_boost: Additional boost for very recent messages (< 1 hour)

        Returns:
            Results with added 'time_decayed_score' field
        """
        now = datetime.now()

        for result in results:
            try:
                msg_time = datetime.fromisoformat(result["metadata"]["timestamp"])
                hours_ago = (now - msg_time).total_seconds() / 3600

                # Exponential decay
                decay_factor = pow(
                    0.5, hours_ago / self.TIME_DECAY_HALFLIFE_HOURS
                )

                # Additional boost for very recent messages
                if hours_ago < 1:
                    decay_factor *= (1 + recency_boost)

                # Combine semantic similarity with time decay
                # Formula: time_decayed_score = score * decay_factor + (1 - decay_factor) * 0.3
                # This ensures old messages still have minimum 30% of original relevance
                semantic_score = result["score"]
                time_decayed_score = (
                    semantic_score * decay_factor + (1 - decay_factor) * 0.3
                )

                result["time_decayed_score"] = min(time_decayed_score, 1.0)
                result["hours_ago"] = hours_ago
                result["decay_factor"] = decay_factor

            except (KeyError, ValueError):
                # If timestamp parsing fails, use original score
                result["time_decayed_score"] = result["score"]
                result["hours_ago"] = 0
                result["decay_factor"] = 1.0

        return results


# Singleton instance
_conversation_store: Optional[ConversationStore] = None


def get_conversation_store() -> ConversationStore:
    """Get singleton conversation store instance."""
    global _conversation_store
    if _conversation_store is None:
        _conversation_store = ConversationStore()
    return _conversation_store
