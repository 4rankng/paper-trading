#!/usr/bin/env python3
"""Ingest news articles from filedb/news into ChromaDB vector store."""

import os
import sys
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import yaml


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Convert non-serializable metadata values to strings.

    ChromaDB only accepts str, int, float, bool in metadata.
    """
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    return sanitized

# Add shared modules to path
shared_dir = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_dir))

from vector_store import get_vector_store
from embeddings import get_embedding_service


# Chunking parameters
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens
MIN_CHUNK_SIZE = 200  # tokens


def count_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 chars)."""
    return len(text) // 4


def chunk_text(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Split text into chunks with overlap.

    Args:
        text: Input text to chunk
        metadata: Document metadata to attach to each chunk

    Returns:
        List of dicts with keys: id, text, metadata
    """
    chunks = []
    estimated_tokens = count_tokens(text)

    # If text is small enough, return as single chunk
    if estimated_tokens <= MIN_CHUNK_SIZE:
        return [{
            "id": metadata.get("id", "unknown"),
            "text": text,
            "metadata": metadata,
        }]

    # Simple character-based chunking (for token accuracy, use tiktoken)
    # Target: ~1000 tokens = ~4000 chars
    target_chars = CHUNK_SIZE * 4
    overlap_chars = CHUNK_OVERLAP * 4
    min_chars = MIN_CHUNK_SIZE * 4

    start = 0
    chunk_idx = 0

    while start < len(text):
        end = start + target_chars

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings near the target
            window = text[end-100:end]
            for i, char in enumerate(reversed(window)):
                if char in '.!?':
                    end = end - 100 + i + 1
                    break

        chunk_text = text[start:end].strip()

        # Skip if too small (except for last chunk)
        if len(chunk_text) >= min_chars or end >= len(text):
            chunk_id = f"{metadata.get('id', 'unknown')}_chunk{chunk_idx}"
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx

            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_metadata,
            })
            chunk_idx += 1

        start = end - overlap_chars

    return chunks


def parse_news_file(filepath: Path) -> Dict[str, Any]:
    """Parse news article file with YAML frontmatter.

    Args:
        filepath: Path to .md file

    Returns:
        Dict with keys: metadata (dict), content (str)
    """
    content = filepath.read_text()

    # Check for YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                article_content = parts[2].strip()
                return {"metadata": metadata or {}, "content": article_content}
            except yaml.YAMLError:
                pass

    # No valid frontmatter
    return {"metadata": {}, "content": content}


def scan_news_articles(base_dir: Path, ticker: str = None) -> List[Dict[str, Any]]:
    """Scan filedb/news for articles.

    Args:
        base_dir: Base filedb directory
        ticker: Optional ticker filter (e.g., "NVDA")

    Returns:
        List of article dicts with keys: id, text, metadata
    """
    news_dir = base_dir / "news"
    articles = []

    if not news_dir.exists():
        print(f"News directory not found: {news_dir}")
        return articles

    # Determine search pattern
    if ticker:
        search_dirs = [news_dir / ticker]
    else:
        search_dirs = [d for d in news_dir.iterdir() if d.is_dir()]

    for ticker_dir in search_dirs:
        if not ticker_dir.is_dir():
            continue

        ticker = ticker_dir.name

        # Scan year/month directories
        for year_dir in ticker_dir.iterdir():
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                # Find all .md files
                for md_file in month_dir.glob("*.md"):
                    parsed = parse_news_file(md_file)

                    # Build metadata
                    metadata = parsed["metadata"]
                    metadata.update({
                        "ticker": ticker,
                        "year": year_dir.name,
                        "month": month_dir.name,
                        "filename": md_file.name,
                        "filepath": str(md_file.relative_to(base_dir)),
                        "content_type": "news",
                    })

                    # Sanitize metadata (convert datetime to string, etc.)
                    metadata = sanitize_metadata(metadata)

                    # Generate unique ID
                    file_hash = hashlib.md5(str(md_file).encode()).hexdigest()[:8]
                    doc_id = f"news_{ticker}_{file_hash}"

                    articles.append({
                        "id": doc_id,
                        "text": parsed["content"],
                        "metadata": metadata,
                    })

    print(f"Found {len(articles)} news articles")
    return articles


def ingest_news(
    base_dir: str = "./filedb",
    ticker: str = None,
    force: bool = False,
) -> None:
    """Ingest news articles into vector store.

    Args:
        base_dir: Base filedb directory
        ticker: Optional ticker filter
        force: Re-index all files (ignore existing)
    """
    base_path = Path(base_dir)
    vector_store = get_vector_store()

    # Scan for articles
    articles = scan_news_articles(base_path, ticker)

    if not articles:
        print("No articles found to ingest")
        return

    # Chunk articles
    all_chunks = []
    for article in articles:
        # Add doc_id to metadata for chunking
        metadata_with_id = article["metadata"].copy()
        metadata_with_id["id"] = article["id"]
        chunks = chunk_text(article["text"], metadata_with_id)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks from {len(articles)} articles")

    # Add to vector store
    print("Adding chunks to vector store...")
    vector_store.add_documents_batch(all_chunks, collection="news")

    # Show stats
    stats = vector_store.get_collection_stats("news")
    print(f"News collection now has {stats.get('news', 0)} documents")


def main():
    parser = argparse.ArgumentParser(description="Ingest news articles into RAG vector store")
    parser.add_argument("--ticker", type=str, help="Ticker symbol to filter (e.g., NVDA)")
    parser.add_argument("--base-dir", type=str, default="./filedb", help="Base filedb directory")
    parser.add_argument("--force", action="store_true", help="Re-index all files")

    args = parser.parse_args()

    ingest_news(
        base_dir=args.base_dir,
        ticker=args.ticker,
        force=args.force,
    )


if __name__ == "__main__":
    main()
