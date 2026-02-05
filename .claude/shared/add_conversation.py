#!/usr/bin/env python3
"""Add conversation messages to the vector store for semantic search.

Usage:
    python add_conversation.py --session-id <id> --role <user|assistant> \
        --content "<message>" --timestamp <iso-timestamp> --message-id <uuid>

This script is called by the webapp's RAG store API to vectorize conversations.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conversation_store import get_conversation_store


def add_conversation(
    session_id: str,
    role: str,
    content: str,
    timestamp: str,
    message_id: str,
) -> dict:
    """Add a single conversation message to the vector store.

    Args:
        session_id: Session identifier
        role: 'user' or 'assistant'
        content: Message content
        timestamp: ISO timestamp string
        message_id: Unique message identifier

    Returns:
        Dict with success status and message_id
    """
    try:
        store = get_conversation_store()

        store.add_conversation(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=timestamp,
            message_id=message_id,
        )

        return {
            "success": True,
            "message_id": message_id,
        }

    except Exception as e:
        print(f"Error adding conversation: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Add conversation message to vector store"
    )
    parser.add_argument(
        "--session-id",
        required=True,
        help="Session identifier"
    )
    parser.add_argument(
        "--role",
        required=True,
        choices=["user", "assistant"],
        help="Message role"
    )
    parser.add_argument(
        "--content",
        required=True,
        help="Message content"
    )
    parser.add_argument(
        "--timestamp",
        help="ISO timestamp (default: current time)"
    )
    parser.add_argument(
        "--message-id",
        help="Unique message ID (default: auto-generated UUID)"
    )

    args = parser.parse_args()

    # Generate timestamp if not provided
    timestamp = args.timestamp or datetime.now().isoformat()

    # Generate message ID if not provided
    message_id = args.message_id
    if not message_id:
        import uuid
        message_id = str(uuid.uuid4())

    result = add_conversation(
        session_id=args.session_id,
        role=args.role,
        content=args.content,
        timestamp=timestamp,
        message_id=message_id,
    )

    # Output as JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
