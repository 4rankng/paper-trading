#!/usr/bin/env python3
"""Store web search results in ChromaDB if finance-relevant."""

import os
import sys
import argparse
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add shared modules to path
shared_dir = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_dir))

from vector_store import get_vector_store
from relevance import is_finance_relevant, extract_tickers, get_relevance_score


def load_web_search_history(base_dir: str) -> List[Dict[str, Any]]:
    """Load web search history from filedb/webapp.

    This is a placeholder - adjust based on your actual web search storage.

    Args:
        base_dir: Base filedb directory

    Returns:
        List of web search result dicts
    """
    # TODO: Implement based on your actual web search storage format
    # For now, return empty list
    print("Warning: Web search history loading not implemented")
    return []


def store_web_search_result(
    query: str,
    results: List[Dict[str, Any]],
    vector_store,
) -> int:
    """Store web search results if finance-relevant.

    Args:
        query: Search query string
        results: List of search results (title, url, snippet)
        vector_store: VectorStore instance

    Returns:
        Number of results stored
    """
    stored_count = 0

    for idx, result in enumerate(results):
        # Combine title and snippet for relevance check
        text = f"{result.get('title', '')} {result.get('snippet', '')}"

        # Check if finance-relevant
        if not is_finance_relevant(text):
            continue

        # Extract metadata
        tickers = extract_tickers(text)
        relevance = get_relevance_score(text)

        # Skip low-relevance results
        if relevance < 0.3:
            continue

        # Create document
        doc_id = f"websearch_{hashlib.md5(query.encode() + result.get('url', '').encode()).hexdigest()[:8]}"
        metadata = {
            "query": query,
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "tickers": ",".join(tickers),
            "relevance_score": relevance,
            "stored_at": datetime.now().isoformat(),
            "content_type": "web_search",
        }

        vector_store.add_document(
            doc_id=doc_id,
            text=text,
            metadata=metadata,
            collection="web_searches",
        )
        stored_count += 1

    return stored_count


def ingest_web_searches(
    base_dir: str = "./filedb",
    force: bool = False,
) -> None:
    """Ingest web search results into vector store.

    Args:
        base_dir: Base filedb directory
        force: Re-index all searches (ignore existing)
    """
    base_path = Path(base_dir)
    vector_store = get_vector_store()

    # Load web search history
    searches = load_web_search_history(str(base_path))

    if not searches:
        print("No web searches found to ingest")
        return

    print(f"Processing {len(searches)} web searches...")

    total_stored = 0
    for search in searches:
        query = search.get("query", "")
        results = search.get("results", [])

        stored = store_web_search_result(query, results, vector_store)
        total_stored += stored
        print(f"  Query '{query}': stored {stored}/{len(results)} results")

    print(f"Total: stored {total_stored} finance-relevant results")

    # Show stats
    stats = vector_store.get_collection_stats("web_searches")
    print(f"Web searches collection now has {stats.get('web_searches', 0)} documents")


def main():
    parser = argparse.ArgumentParser(description="Ingest web search results into RAG vector store")
    parser.add_argument("--base-dir", type=str, default="./filedb", help="Base filedb directory")
    parser.add_argument("--force", action="store_true", help="Re-index all searches")

    args = parser.parse_args()

    ingest_web_searches(
        base_dir=args.base_dir,
        force=args.force,
    )


if __name__ == "__main__":
    main()
