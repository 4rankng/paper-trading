#!/usr/bin/env python3
"""Search RAG vector store for relevant documents."""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# Add shared modules to path
shared_dir = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_dir))

from vector_store import get_vector_store
from embeddings import get_embedding_service


def format_result(result: Dict[str, Any]) -> str:
    """Format a single search result for display.

    Args:
        result: Result dict with keys: id, text, metadata, score, collection

    Returns:
        Formatted string
    """
    metadata = result.get("metadata", {})
    score = result.get("score", 0)
    collection = result.get("collection", "unknown")

    # Build header
    lines = [
        f"[{collection}] Score: {score:.3f}",
        f"ID: {result.get('id', 'unknown')}",
    ]

    # Add key metadata
    if "ticker" in metadata:
        lines.append(f"Ticker: {metadata['ticker']}")
    if "date" in metadata:
        lines.append(f"Date: {metadata['date']}")
    if "title" in metadata:
        lines.append(f"Title: {metadata['title']}")
    if "url" in metadata:
        lines.append(f"URL: {metadata['url']}")
    if "doc_type" in metadata:
        lines.append(f"Type: {metadata['doc_type']}")

    # Add text preview (first 200 chars)
    text = result.get("text", "")
    preview = text[:200] + "..." if len(text) > 200 else text
    lines.append(f"\n{preview}")

    return "\n".join(lines)


def search_rag(
    query: str,
    collection: str = "all",
    limit: int = 5,
    ticker: str = None,
    output_format: str = "text",
) -> None:
    """Search RAG vector store.

    Args:
        query: Search query
        collection: Collection name or 'all'
        limit: Number of results to return
        ticker: Optional ticker filter
        output_format: Output format ('text' or 'json')
    """
    vector_store = get_vector_store()
    embedding_service = get_embedding_service()

    # Build metadata filter
    where = {}
    if ticker:
        where["ticker"] = ticker.upper()

    # Search
    print(f"Searching for: {query}")
    print(f"Collection: {collection}")
    if ticker:
        print(f"Ticker filter: {ticker}")
    print(f"Embedding model: {embedding_service.get_embedding_model()}")
    print()

    results = vector_store.search(
        query=query,
        collection=collection,
        n_results=limit,
        where=where if where else None,
    )

    if not results:
        print("No results found")
        return

    # Output results
    if output_format == "json":
        # Output as JSON
        output = {
            "query": query,
            "model": embedding_service.get_embedding_model(),
            "count": len(results),
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        # Output as text
        print(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(format_result(result))
            print()


def main():
    parser = argparse.ArgumentParser(description="Search RAG vector store")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--collection", type=str, default="all",
                        choices=["all", "news", "analytics", "web_searches"],
                        help="Collection to search (default: all)")
    parser.add_argument("--limit", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--ticker", type=str, help="Filter by ticker symbol")
    parser.add_argument("--format", type=str, default="text",
                        choices=["text", "json"],
                        help="Output format (default: text)")

    args = parser.parse_args()

    search_rag(
        query=args.query,
        collection=args.collection,
        limit=args.limit,
        ticker=args.ticker,
        output_format=args.format,
    )


if __name__ == "__main__":
    main()
