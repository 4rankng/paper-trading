#!/usr/bin/env python3
"""Search conversations using semantic similarity via RAG.

Usage:
    python search_conversations.py --session-id <id> --query "<query>" [--limit 5] [--no-time-decay]

This script is called by the webapp's RAG API to perform semantic search
on conversation history, replacing the old keyword-based approach.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conversation_store import get_conversation_store


def search_conversations(
    session_id: str,
    query: str,
    limit: int = 5,
    time_decay: bool = True,
) -> dict:
    """Search conversations using semantic similarity.

    Args:
        session_id: Session identifier
        query: Search query
        limit: Number of results to return
        time_decay: Apply time-based relevance decay

    Returns:
        Dict with keys: context (string), sources (list of source info)
    """
    try:
        store = get_conversation_store()

        # Perform semantic search
        results = store.search_conversations(
            query=query,
            session_id=session_id,
            n_results=limit,
            time_decay=time_decay,
        )

        if not results:
            return {
                "context": "",
                "sources": [],
            }

        # Build context string
        context_parts = []
        sources = []

        for result in results:
            role = result["metadata"].get("role", "unknown")
            content = result["text"]

            # Format: "User: ..." or "Assistant: ..."
            role_label = "User" if role == "user" else "Assistant"
            context_parts.append(f"{role_label}: {content}")

            sources.append({
                "message_id": result["id"],
                "timestamp": result["metadata"].get("timestamp", ""),
                "relevance": result.get("time_decayed_score", result["score"]),
                "hours_ago": result.get("hours_ago", 0),
                "decay_factor": result.get("decay_factor", 1.0),
            })

        context = "\n\n".join(context_parts)

        return {
            "context": context,
            "sources": sources,
        }

    except Exception as e:
        print(f"Error searching conversations: {e}", file=sys.stderr)
        return {
            "context": "",
            "sources": [],
            "error": str(e),
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search conversations using semantic similarity"
    )
    parser.add_argument(
        "--session-id",
        required=True,
        help="Session identifier"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Search query"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of results (default: 5)"
    )
    parser.add_argument(
        "--no-time-decay",
        action="store_true",
        help="Disable time-based relevance decay"
    )

    args = parser.parse_args()

    result = search_conversations(
        session_id=args.session_id,
        query=args.query,
        limit=args.limit,
        time_decay=not args.no_time_decay,
    )

    # Output as JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
